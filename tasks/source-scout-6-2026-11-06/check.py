"""Offline named check for the S6 federal-dataset scout: recomputes every sample yield / frame count from the committed CSVs, re-draws each seeded
sample from its committed frame, runs the known-answer and injected-defect controls, scans for personal data, and (when the persist cache exists)
re-counts the large frames independently with DuckDB. No network. `--write` refreshes metrics.json; the default fails on drift.
Usage: python3 -I tasks/source-scout-6-2026-11-06/check.py [--write]"""
import csv,importlib.util,json,math,re,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import common
ROUTES={'fda':'registration_number','fied':'registry_id','ftz':'company','dol':'unit_key','usaspending':'uei'}
FRAME_N={'fda':689,'fied':20834,'ftz':68,'dol':114,'usaspending':1564}
def read(p):return list(csv.DictReader(open(p,newline='')))
def module(p):
 spec=importlib.util.spec_from_file_location(p.parent.name+'_build',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def yields(rows,key):
 assert len(rows)==20 and len({r[key] for r in rows})==20,'20 unique sample units required'
 for r in rows:
  assert r['verdict'] in common.VERDICTS and r['verified_new'] in {'0','1'} and (r['verified_new']=='1')==(r['verdict']=='VERIFIED')
  assert (r['verdict']=='DUPLICATE_OF')==bool(r['duplicate_of']),f"{r[key]}: duplicate_of/verdict mismatch"
  assert int(r.get('verify_fetches') or 0)<=6,f"{r[key]}: fetch budget exceeded"
 k=sum(int(r['verified_new']) for r in rows);m=sum(bool(r['atlas_ids']) for r in rows)
 return dict(sampled=20,verdicts={v:sum(r['verdict']==v for r in rows) for v in sorted({r['verdict'] for r in rows})},
  duplicate_of=sum(r['verdict']=='DUPLICATE_OF' for r in rows),any_atlas_match=m,any_atlas_match_wilson95=common.wilson(m,20),
  site_or_registry_match=sum(bool(r['site_hits'] or r['registry_hits']) for r in rows),
  verified_new=k,verified_new_yield=k/20,verified_new_wilson95=common.wilson(k,20),
  live_address_confirmed_scope_unknown=sum(r['verdict']=='STILL_UNCERTAIN' and r.get('verify_address_found')=='1' for r in rows),
  fetches_spent=sum(int(r.get('verify_fetches') or 0) for r in rows))
def witness_ok(r,ver):
 """A VERIFIED row needs a polymer-word witness: polymer words found on the address page AND a committed span in which a polymer MATERIAL word sits within 80 chars of a process word."""
 w=r.get('verify_process_witness','')
 assert r['verify_polymer_words'].strip(),f"{r.get('registration_number') or r.get('unit_key') or r.get('uei')}: verified_new row with an empty polymer-word witness"
 assert ver.PROCESS.search(w) and ver.POLY.search(w) and not ver.SURG.search(w),f"verified_new row whose process witness fails the rule: {w!r}"
def duckdb(sql):
 return subprocess.run(['duckdb','-csv','-noheader','-c',sql],capture_output=True,text=True,check=True).stdout.strip()
def main():
 assert common.wilson(0,20)==[0,0.161125] and common.wilson(20,20)==[0.838875,1] and common.wilson(1,20)==[0.008881,0.236131] and common.wilson(4,20)==[0.080658,0.416017]
 # injected defects must trip the gates
 for bad in ([dict(a='x',verdict='VERIFIED',verified_new='1',duplicate_of='',atlas_ids='',site_hits='',registry_hits='')]*20,):
  try:yields(bad,'a')
  except AssertionError:pass
  else:raise AssertionError('duplicate-unit sample escaped the gate')
 try:yields([dict(a=str(i),verdict='VERIFIED',verified_new='0',duplicate_of='',atlas_ids='',site_hits='',registry_hits='') for i in range(20)],'a')
 except AssertionError:pass
 else:raise AssertionError('verdict/verified_new mismatch escaped')
 ver=module(HERE/'verify.py')
 for bad in (dict(verify_polymer_words='',verify_process_witness='Extruded Dense Extruded'),dict(verify_polymer_words='plastic',verify_process_witness='Plastic and Cosmetic Surgery Products'),dict(verify_polymer_words='plastic',verify_process_witness='')):
  try:witness_ok(bad,ver)
  except AssertionError:pass
  else:raise AssertionError(f'witness gate let through {bad}')
 witness_ok(dict(verify_polymer_words='plastics',verify_process_witness='Plastics Contract Manufacturing'),ver)
 tables=common.atlas.load_tables(common.ROOT/'data');orgids={r['org_id'] for t in ('organizations','ecosystem') for r in tables[t].rows};siteids={r['site_id'] for r in tables['sites'].rows}
 A=common.Atlas()
 for name,reg,want in [('The Goodyear Tire & Rubber Company',('UEI','WPMTYSB6BFN1'),'ORG-000003'),('zzz none',('FRS','110000462936'),'SITE-004945'),('Avient Corporation',None,'ORG-000001')]:
  m=A.match(name,registry=reg);assert want in m['atlas_ids'].split(';') or want in m['registry_hits'].split(';'),(name,m)
 metrics={}
 for route,key in ROUTES.items():
  frame=read(HERE/route/'frame.csv');sample=read(HERE/route/'sample.csv');counts=json.loads((HERE/route/'counts.json').read_text())
  assert len(frame)==len({r[key] for r in frame})==FRAME_N[route],(route,len(frame))
  fk=[r for r in common.draw(frame,key)];assert [r[key] for r in fk]==[r[key] for r in sample],f'{route}: sample is not the seeded draw from frame.csv'
  byk={r[key]:r for r in frame}
  for r in sample:
   for f,v in byk[r[key]].items():assert r[f]==v,(route,r[key],f)
   for ref in filter(None,(r['duplicate_of'],*r['site_hits'].split(';'))):assert ref in orgids|siteids,(route,ref)
   if r['verdict']=='VERIFIED':
    witness_ok(r,ver)
    assert r['verify_url'] and r['verify_address_found']=='1' and r['verify_name_found']=='1' and r['verify_process_hit']=='1' and r['verify_sha256'],(route,r[key])
    assert (r['street'].split() or [''])[0] in r['verify_quote'],f'{route}: verified quote lacks the street number'
  metrics[route]=yields(sample,key);metrics[route]['frame_units']=len(frame)
  if 'state' in frame[0]:metrics[route]['frame_units_in_ohio']=sum(r['state']=='OH' for r in frame)
  # personal-data guard: header allowlist words and value patterns across every committed CSV of the route
  for f in ('frame.csv','sample.csv'):
   text=(HERE/route/f).read_text()
   assert not re.search(r'(poc|attorney|email|phone|fein|contact|preparer|worker)',text.splitlines()[0],re.I),(route,f,'personal-data column')
   assert not re.search(r'[\w.+-]+@[\w-]+\.[a-z]{2,}',text.replace('"@"','')),(route,f,'email address in values')
   assert not re.search(r'(?<![\d.])\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b',text),(route,f,'phone number in values')
 # per-route counts that must reconcile
 c=json.loads((HERE/'fda/counts.json').read_text());assert c['frame']==689 and c['us_facility_active']==13100 and c['polymer_product_codes']==153
 fdaf=read(HERE/'fda/frame.csv');assert all(r['street'] and r['state'] in common.atlas.USPS for r in fdaf)  # US-agent (address type U) rows would carry person names and no facility state
 c=json.loads((HERE/'fied/counts.json').read_text());assert (c['unit_rows'],c['facilities_all'],c['slice_facilities'],c['slice_unit_rows'])==(644881,502165,20834,35566) and sum(c['slice_naics_prefix_counts'].values())==20834
 c=json.loads((HERE/'ftz/counts.json').read_text());assert (c['headings_queried'],c['approval_records_returned'],c['frame_companies'])==(43,406,68)
 c=json.loads((HERE/'dol/counts.json').read_text());assert (c['data_rows'],c['naics_slice_cases'],c['certified_us_worksite_slice_cases'],c['frame_employer_worksite_units'])==(118580,148,130,114)
 c=json.loads((HERE/'usaspending/counts.json').read_text());assert c['recipients']==1564 and c['awards_count_independent']==32651
 # known answers / negative controls for each route's filter
 fda=module(HERE/'fda/build.py');assert fda.poly_code('Bracket, Plastic, Orthodontic','DE') and not fda.poly_code('Resin, Ion-Exchange, Thioglycolic Acid','CH') and not fda.poly_code('Scalpel, Stainless','GS')
 assert fda.street_of({'ADDRESS_LINE_1':'ENDOSCOPY','ADDRESS_LINE_2':'76 S. MERIDIAN AVE.'})=='76 S. MERIDIAN AVE.'
 fied=module(HERE/'fied/build.py');assert fied.in_slice(fied.naics('326199.0')) and fied.in_slice('32551') and not fied.in_slice(fied.naics('332618.0')) and fied.zip5('2134.0')=='02134'
 ftz=module(HERE/'ftz/build.py');assert ftz.poly_product({'PartType':'Product','HTSUS':'3920.10'}) and not ftz.poly_product({'PartType':'Component','HTSUS':'3920.10'}) and not ftz.poly_product({'PartType':'Product','HTSUS':'8414.59'})
 dol=module(HERE/'dol/build.py');assert dol.in_slice('326199') and dol.in_slice('3261') and not dol.in_slice('541511') and dol.zip5('44316-0001')=='44316'
 assert ver.addr_found('Visit us at 33587 Walker Rd., Avon Lake','33587 Walker Road') and not ver.addr_found('33587 Walter Rd','33587 Walker Road') and not ver.addr_found('Suite 5587 Walker','33587 Walker Road')
 assert ver.PROCESS.search('We manufacture custom rubber and plastic parts') and not ver.PROCESS.search('Contact us about our supply of office products')
 # independent census (DuckDB over the persist cache) when present; explicit SKIPPED otherwise, never a silent pass
 P=common.PERSIST;ind=[]
 if (P/'fied/foundational_industry_data_2017.csv').exists():
  n=duckdb(f"select count(distinct registryID) from read_csv('{P}/fied/foundational_industry_data_2017.csv',all_varchar=true,ignore_errors=false,max_line_size=10000000) where regexp_matches(cast(cast(try_cast(naicsCode as double) as bigint) as varchar),'^(3252|3255|326)')")
  assert int(n)==20834,f'FIED independent count {n}';ind.append(('fied_slice_facilities',n))
 else:ind.append(('fied_slice_facilities','SKIPPED: persist cache absent'))
 if (P/'dol/lca_fy2025_q4_kept.csv').exists():
  n=duckdb(f"select count(*) from read_csv('{P}/dol/lca_fy2025_q4_kept.csv',all_varchar=true) where regexp_matches(NAICS_CODE,'^(3252|326)') and CASE_STATUS='Certified' and trim(WORKSITE_ADDRESS1)<>''");assert int(n)==130,n;ind.append(('dol_certified_slice_cases',n))
 else:ind.append(('dol_certified_slice_cases','SKIPPED: persist cache absent'))
 metrics['independent_recount']=dict(ind)
 dest=HERE/'metrics.json'
 if '--write' in sys.argv:dest.write_text(json.dumps(metrics,indent=1,sort_keys=True)+'\n')
 else:
  old=json.loads(dest.read_text());old.pop('independent_recount',None);new=dict(metrics);new.pop('independent_recount')
  assert old==json.loads(json.dumps(new)),'stale metrics.json (run with --write after review)'
 routes=read(HERE/'routes.csv');rs={(r['source'],r['role']):r['http_status'] for r in routes}
 assert rs[('dol','host-direct')]=='403' and rs[('dol','wayback-landing')]=='200' and rs[('ftz','legacy-T/IM')]=='0' and rs[('nei','landing-2023')]=='404' and rs[('fda','bulk')]=='200' and rs[('usaspending','api')]=='200'
 terms=read(HERE/'terms_checks.csv');assert len(terms)==6 and {r['source'] for r in terms}=={'fda','fied','nei','ftz','dol','usaspending'} and all(r['raw_words_in_order']=='PASS' for r in terms)
 print(json.dumps(metrics,indent=1,sort_keys=True));print('PASS: 5 routes x 20 sampled units; frames reconcile; seeded draws reproduce; negative controls; personal-data guard;',metrics['independent_recount'])
if __name__=='__main__':main()
