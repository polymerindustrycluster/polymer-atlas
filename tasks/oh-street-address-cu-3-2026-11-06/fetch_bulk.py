"""Read T2's pinned house lookup helper; export only public facility identity/address fields."""
import json,re,sqlite3,subprocess,sys,types
from pathlib import Path
from fetch import TASK,ROOT,frs,read,write
HELPER_COMMIT='5bd0c22f3aedbcc8269de8ae4d2c3783487ca7cd'
CACHE=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/cache/bulk')
sys.path.insert(0,str(ROOT/'scripts'))
helper=types.ModuleType('pinned_bulk_source');helper.__file__=str(ROOT/'scripts/bulk_sources.py')
exec(compile(subprocess.check_output(['git','show',HELPER_COMMIT+':scripts/bulk_sources.py'],text=True),helper.__file__,'exec'),helper.__dict__)
FIELDS=('REGISTRY_ID','FAC_NAME','FAC_STREET','FAC_CITY','FAC_STATE','FAC_ZIP','FAC_COUNTY')
def manifest():
 with sqlite3.connect((CACHE/'frs.sqlite').as_uri()+'?mode=ro',uri=True) as db:return json.loads(db.execute('SELECT json FROM manifest').fetchone()[0])
def facility(rows,rid):
 assert len(rows)==1 and rows[0]['REGISTRY_ID']==rid,'missing/ambiguous bulk identifier'
 r=rows[0]
 return dict(RegistryId=rid,FacilityName=r['FAC_NAME'],LocationAddress=r['FAC_STREET'],CityName=r['FAC_CITY'],StateAbbr=r['FAC_STATE'],ZipCode=r['FAC_ZIP'],CountyName=r['FAC_COUNTY'],SupplementalLocation='')
def namekey(value):
 tokens=re.findall('[A-Z0-9]+',value.upper().replace('&',' AND '))
 if tokens[:1]==['THE']:tokens=tokens[1:]
 while tokens and tokens[-1] in {'INC','INCORPORATED','LLC','CORP','CORPORATION','CO','COMPANY','LTD','LIMITED'}:tokens.pop()
 return ' '.join(tokens)
def known():
 out=[]
 for rid,street,city,zip_,name in [('110000745766','160 Parker Ct','Chardon','44024','Rhein Chemie Corp'),('110000391415','350 N Buckeye St','Bellevue','44811','A. Schulman, Inc.'),('110000383941','555 W Linfoot St','Wauseon','43567','Lear Corporation')]:
  rows=helper.frs_by_registry_id(rid);f=facility(rows,rid)
  assert frs.streetkey(f['LocationAddress'])==frs.streetkey(street) and frs.norm(f['CityName'])==frs.norm(city) and f['ZipCode'][:5]==zip_ and namekey(f['FacilityName'])==namekey(name)
  assert any(r['REGISTRY_ID']==rid for r in helper.frs_by_name_city(f['FacilityName'],city))
  site=dict(city=city,zip=zip_,county=f['CountyName'])
  for k,v in [('city','WRONG CITY'),('zip','00000'),('county','WRONG COUNTY')]:assert frs.conflict(dict(site,**{k:v}),f)
  for bad in ([],rows+rows,[dict(rows[0],REGISTRY_ID='110000000000')]):
   try:facility(bad,rid)
   except AssertionError:pass
   else:raise AssertionError('missing/duplicate/wrong bulk registry ID accepted')
  assert frs.conflict(dict(city=city,zip=zip_,county=f['CountyName'],**{k:v}) if k not in ('city','zip','county') else dict({'city':city,'zip':zip_,'county':f['CountyName']},**{k:v}),f)
  assert frs.conflict(dict(city=city,zip=zip_,county=f['CountyName']),dict(f,LocationAddress='PO BOX 99'))
  out.append(dict(registry_id=rid,expected_operator=name,expected_street=street,city=city,zip=zip_,result='PASS'))
 assert namekey('The Example Co Inc')==namekey('Example Corporation')
 assert namekey('ABC Polymers')!=namekey('ABC Plastics')
 assert namekey('Tarkett USA Inc')!=namekey('Tarkett North America')
 assert namekey('The Company Store')!=namekey('Store Company')
 write(TASK/'bulk_known.csv',out)
def main():
 known();before=manifest();assert before['url']=='https://echo.epa.gov/files/echodownloads/echo_exporter.zip'
 selected=[s for s in read(TASK/'frame.csv') if s['selected']=='yes']
 leads=read(TASK/'registry_links_input.csv')+read(TASK/'frs_notes_leads.csv')+read(TASK/'frs_packet_leads.csv')
 bindings=[];queries=[];raw={};seen=set()
 def collect(s,kind,query,rows):
  queries.append(dict(site_id=s['site_id'],query_type=kind,query=query,rows_returned=len(rows),blank_ids=sum(not r.get('REGISTRY_ID') for r in rows)))
  for r in rows:
   rid=r.get('REGISTRY_ID') or ''
   if not rid:continue
   if (s['site_id'],rid) in seen:continue
   seen.add((s['site_id'],rid))
   full=helper.frs_by_registry_id(rid)
   projected=[{k:r.get(k) or '' for k in FIELDS} for r in full];raw[rid]=projected
   bindings.append(dict(site_id=s['site_id'],org_id=s['org_id'],registry_id=rid,binding=kind,query=query))
 for s in selected:
  for r in leads:
   if r['site_id']==s['site_id']:collect(s,'existing_id_lead',r['registry_id'],helper.frs_by_registry_id(r['registry_id']))
  names=[s['held_legal_name']]+s['held_trade_names'].split(';');names=[n.strip() for n in names if n.strip()]
  variants=set(names)
  for n in names:
   stem=namekey(n)
   for suffix in ('',' INC',' INCORPORATED',' LLC',' CORP',' CORPORATION',' CO',' COMPANY',' LTD',' LIMITED'):variants.add(stem+suffix)
  for name in sorted(variants):collect(s,'exact_name_city_discovery',name,helper.frs_by_name_city(name,s['city']))
 assert before==manifest(),'bulk snapshot changed during lookup'
 folder=TASK/'bulk_raw';folder.mkdir(exist_ok=True)
 for rid,rows in raw.items():(folder/(rid+'.json')).write_text(json.dumps(rows,indent=2)+'\n')
 write(TASK/'bulk_bindings.csv',bindings,['site_id','org_id','registry_id','binding','query']);write(TASK/'bulk_queries.csv',queries)
 (TASK/'bulk_manifest.json').write_text(json.dumps(dict(source=before,helper_commit=HELPER_COMMIT,source_caveats=['retrieval date not address-effective date','same archive SHA as held Nov1 spine','permit activity not establishment operating status','18887 source rows have blank registry IDs','ECHO covers regulated facilities, not all FRS']),indent=2)+'\n')
 print('PASS bulkknown3;selected',len(selected),'lookupcalls',len(queries),'returnedrows',sum(r['rows_returned'] for r in queries),'uniqueIDbindings',len(bindings),'uniqueIDs',len(raw))
if __name__=='__main__':main()
