Deep adversarial completion refute: L2 finalOhioA/B round7, agent/codex/oh-street-address-7. Readonly; VERDICT APPROVE/REFUTE with demonstrated facts, no merge/status action.
Predeclared original448frame positions361–448,88active storedPIC18 A/Bblankstreets;360prior+88worked+0future=448. Fixed152360–152447slots, main419678b. Originalframe identity/order/slots checked against immutable reviewed171@7af4219 because main is mid-controller-declared NON-DATA DELETION incident; no missingtask=absence inference. Do not merge main until restorationPR209lands.
24VERIFIED64STILL_UNCERTAIN;24streetfillsA20/B4unchanged+6OWNER-AUTHORIZEDnotesflags across26existingrecords,26append-only own_site/address/supports_AEVD(24fillIDs152361–152430+2notes-onlyIDs152448/449 expressly allocatedbycontroller). ActiveOH324/1883→348/1883(17.21→18.48%),excludespending156/192/207/208.166researchattempts134fetched32unavailable,88IDsyield,28raw-addresssites. Fourconflictsheld:Cosarmail/GuildSuite350/Hedstrom100Hedstromvs2040Cellar/SmetzerdedicatedtruckretreadvsotherWoosterstreets. Holds60noraw+1mail+2notes+1multiple+notes=64.
Owner ruling explicitly supersedes original street/sources-only boundary for SIX EXACTNOTES SUFFIXES: apply four true own-page streetfills and flag bothsidesof3same-addresspairs. AmericanSign001858/Thermoprene001904@5718TransportationGarfieldHeights;HorsemenPride001882/Tusco001721(R6)@10008StateRoute43Streetsboro;ITPlastics001924/Overmold001717(R6)@7675JentherMentor. AGENTS3 linkandflag/SCHEMA4.5multioperator: possibleduplicate/co-locationLEADS ONLY;nomerge/site_group/status inference. Bothrecords'ownpagesandoldnotesagreeaddresses. New2notes-onlysources freshlyfetched. note_flags.csv freezesoldnotes+exactappend;unrelatednotesrejectBEFOREwrites. FourfillEVDclaimdetailsalsoflagotherSITE;2notes-onlyEVDcoverR6rows. MERGE208BEFORER7 because its strictfrozen-notesguardotherwisecorrectlyrejects laternotes; thisbuilderpreservesR6streetswhenpresent.
Onlynewmatcherchange Rte→Route ordinaryabbreviation;2184StateRte43=2184StateRoute43≠Route44. Prior10notesfixtures+PARK/Pk/suite/unit/house-number+actualbymail/mail/postal/email-negativeretained. Heldoperatorhostredirects/rawquote/city/knownZIP/physicalcontextbinding. GenericHQneedsstreetbindingwhenpeers.
ChecksPASS:3LIVEknownbeforefetch; check.py24fills/6notes/26EVD boundary+byte-idempotent+street/notes drift+fill and late-notes-only foreignEVD collisions failbeforeanywrite,4trueconflictsHOLD; auditALL24streetwitnesses+ALL2notes-onlywitnessesfresh26/26errors0(population<30),inclmailcontext; validator0;baselineallsitekeys/legacyEVDpreserved24street+6notes+26appends;diffcheck.
RowlossPASS on66cc2d7 vs419678b using unchangedhouseguard fromR6branch with __file__=THIScwd/scripts/check_row_loss.py(ROOTcurrentworktree), scriptabsentdueincident. Nativeguard/replayrequiredafter209. Do not mistake /tmpROOT or unrelatedworktreePASS. No scripts edited.
Framecompletion.csv448unique/exactIDs:15660=19V41U;171100=38V62U;207100=25V75U;208100=36V64U;final88=24V64U =>142V306U0unworked. Namedcheckassertseachpartitionandtotals. Only38fillsmergedinbaseline,104proposed;CU19240rowsoutsideframe.
Challenge: accidentalunit/sourcequalifiererasure; wrongsite/HQ; bymail; notesauthority/evidencecoverage/latecollision; dedupeflagmisreadasadjudication; rebasefield/rowloss; sourcequote/cityZIP/host; conflating26EVDwith24fills; fullframecompletionvsmergedcoverage. No geography/status/tier/ring/registry/derivedfields changed,noentitycreates/deletes/merges.
Run task/check.py; task/audit.py; fetch.py --known; scripts/validate.py; native scripts/check_row_loss.py after209restore(orhousefallbackexplicitROOT). Taskpath tasks/oh-street-address-7-2026-11-06. Full448frame/fullnotes/note_flags/pagechecks/journal/framecompletion in repo. Belowallcode/88compactinputs/26witnesses/88verdicts/26audit, exactflagsuffixes+controllerIDs.

FILE fetch.py
"""Raw-check held PIC-18 Ohio operator pages; only complete physical street/city/state/ZIP blocks become candidates."""
import concurrent.futures,csv,hashlib,json,re,subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlparse
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[1]
def read(p):return list(csv.DictReader(open(p)))
def write(p,rows):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
class Page(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.links=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
  if t=='a':self.links.extend(v for k,v in a if k=='href' and re.search('contact|location',v,re.I))
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,s):
  if not self.skip and s.strip():self.parts.append(s.strip())
def fetch(u):
 r=subprocess.run(['curl','--fail','-L','--max-time','25','-A','Mozilla/5.0','-w','\\n__ATLAS_URL__%{url_effective}',u],capture_output=True)
 if r.returncode:raise ValueError('HTTP/transport failure '+str(r.returncode))
 raw,final=r.stdout.rsplit(b'\n__ATLAS_URL__',1)
 host=lambda v:(urlparse(v).hostname or '').lower().removeprefix('www.')
 if host(final.decode())!=host(u):raise ValueError('redirect leaves held operator host')
 p=Page();p.feed(raw.decode(errors='replace'));return ' '.join(p.parts),p.links,hashlib.sha256(raw).hexdigest()
def extract(text,city):
 # shortcut: plain address blocks only; held JS/image/unit layouts need a site-specific raw witness.
 suffix=r'(?:Street|St\.?|Road|Rd\.?|Drive|Dr\.?|Avenue|Ave\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Parkway|Pkwy\.?|Place|Pl\.?|Way|Court|Ct\.?|Route\s+\d+)'
 pattern=r'\b(\d{1,6}\s+(?:(?!\d+\b)[A-Za-z0-9.#/-]+\s+){0,8}?'+suffix+r')[, •|]*\s*'+re.escape(city)+r'\s*[, •|]*\s*(?:OH|Ohio)\s*[, •|]*\s*(\d{5}(?:-\d{4})?)\b'
 text=' '.join(text.split())
 return [(m[1].strip(),m[2],m[0]) for m in re.finditer(pattern,text,re.I)]
def mailing_posture(text,quote):
 text=' '.join(text.split());pos=text.find(quote)
 if pos<0:return 'quote absent on fresh fetch'
 context=text[max(0,pos-80):pos+len(quote)]
 return 'mailing-only context' if re.search(r'(?i)mailing\s+address|postal\s+address|\bby\s+mail\b',context) else ''
def known():
 cases=[('373 Washington St. Chardon OH 44024','Chardon','373 Washington St.','44024'),
        ('1101 Moore Road, Avon, Ohio 44011','Avon','1101 Moore Road','44011'),
        ('1150 Damar Drive Akron, Ohio 44305-1201','Akron','1150 Damar Drive','44305-1201')]
 for text,city,street,zip_ in cases:
  assert extract(text,city)==[(street,zip_,text)]
  assert not extract(text,'WRONG CITY') and not extract('PO Box 123, '+city+', OH '+zip_,city)
 assert extract('Phone 2166 1 Lark Ave., Leola, OH 17540','Leola')==[('1 Lark Ave.','17540','1 Lark Ave., Leola, OH 17540')]
 assert extract('2970 Molding Division Main Office 1040 Maple Avenue Lake City, OH 16423','Lake City')==[('1040 Maple Avenue','16423','1040 Maple Avenue Lake City, OH 16423')]
 urls=['https://chardoncp.com/','https://www.freemansupply.com/','https://www.shinetsusilicones.com/']
 out=[]
 for (quote,city,street,zip_),url in zip(cases,urls):
  text,links,sha=fetch(url)
  assert any(r[0]==street and r[1]==zip_ for r in extract(text,city)),(url,extract(text,city))
  out.append(dict(url=url,city=city,expected_street=street,expected_zip=zip_,sha256=sha,result='PASS'))
 write(TASK/'known_answers.csv',out)
 print('PASS: three live literal address answers; wrong-city/PO-box/phone-prefix mutations')
def main():
 sites=[r for r in read(TASK/'frame.csv') if r['selected']=='yes']
 groups={}
 for r in sites:groups.setdefault(r['org_id'],[]).append(r)
 def work(item):
  oid,rows=item;base=rows[0]['website'];base=base if '://' in base else 'https://'+base
  todo=[base];seen=[];out=[];pages=[]
  # Existing own-host URLs are source leads, never evidence until fetched.
  for r in rows:
   for u in re.findall(r'https?://[^; <>]+',r['sources']):
    if (urlparse(u).hostname or '').removeprefix('www.')==(urlparse(base).hostname or '').removeprefix('www.') and u not in todo:todo.append(u)
  while todo and len(seen)<5:
   u=todo.pop(0).split('#')[0]
   if u in seen:continue
   seen.append(u)
   try:
    text,links,sha=fetch(u);found=0
    for r in rows:
     for street,zip_,quote in extract(text,r['city']):
      posture=mailing_posture(text,quote)
      out.append(dict(site_id=r['site_id'],street_address=street,source_zip=zip_,quote=quote,url=u,sha256=sha,posture=posture));found+=1
    pages.append(dict(org_id=oid,url=u,outcome='fetched',address_blocks=found,error=''))
    links=sorted(links,key=lambda x:('location' not in x.lower(),len(x)))
    for link in links:
     v=urljoin(u,link).split('#')[0]
     if (urlparse(v).hostname or '').removeprefix('www.')==(urlparse(base).hostname or '').removeprefix('www.') and v not in seen and v not in todo:todo.append(v)
   except Exception as ex:pages.append(dict(org_id=oid,url=u,outcome='unavailable',address_blocks=0,error=str(ex)))
  for r in rows:
   if not any(o['site_id']==r['site_id'] for o in out):out.append(dict(site_id=r['site_id'],street_address='',source_zip='',quote='',url=base,sha256='',posture='need physical street at recorded city; no raw address block found'))
  return out,pages
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(work,groups.items()))
 out=[r for rows,pages in results for r in rows];pages=[r for rows,log in results for r in log]
 assert {r['site_id'] for r in out}=={r['site_id'] for r in sites}
 write(TASK/'rawchecks.csv',out);write(TASK/'page_checks.csv',pages)
 print('selected sites',len(sites),'rawcheck sites',len({r['site_id'] for r in out}),'sites with address',len({r['site_id'] for r in out if r['street_address']}),'pages',len(pages),flush=True)
if __name__=='__main__':
 if '--known' in __import__('sys').argv:known()
 else:main()

FILE build.py
"""Integrate selected own-site address blocks; validate every planned write before touching canonical data."""
import csv,hashlib,json,re,sys
from pathlib import Path
from urllib.parse import urlparse
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from fetch import read,write,extract,fetch
DATE='2026-11-06'
def key(v):
 aliases={'STREET':'ST','ROAD':'RD','AVENUE':'AVE','DRIVE':'DR','COURT':'CT','PARKWAY':'PKWY','BOULEVARD':'BLVD','PLACE':'PL','PARK':'PK','RTE':'ROUTE','WEST':'W','EAST':'E','NORTH':'N','SOUTH':'S'}
 return ' '.join(aliases.get(t,t) for t in re.findall('[A-Z0-9]+',v.upper()))
def note_streets(s):
 out=[x[0] for x in extract(s['notes'],s['city'])]
 m=re.search(r'(?i)\bstreet(?:\s*\([^)]*\))?:\s*(.+)',s['notes'])
 if m:
  value=re.split(r'\.\s+(?=PASS|BAND|CERT|Ring|INTEGRATION|Parcel|Re-pointed|NAICS|Source|Address confirmed|Co-located|Converted|Filing basis|(?i:county UNVERIFIED)|\[)',m[1])[0]
  value=re.split(r',\s*'+re.escape(s['city'])+r'\b',value,maxsplit=1,flags=re.I)[0]
  value=re.split(r'\s+\((?=(?i:address per|company contact|GS1 manufacturer|per (?:the operator|wave-\d+ verdict)))',value,maxsplit=1)[0]
  out.append(value.rstrip('. '))
 out+=re.findall(r'(?i)(?:Address[^:]{0,120}:|at)\s*(\d+\s+[^,;()]+),\s*'+re.escape(s['city']),s['notes'])
 return out
def plan():
 frame=read(TASK/'frame.csv');selected=[r for r in frame if r['selected']=='yes'];checks=read(TASK/'rawchecks.csv')
 assert len(frame)==448 and len({s['site_id'] for s in frame})==448
 assert len(selected)==88 and len({s['reserved_evidence_id'] for s in frame})==448
 assert {r['site_id'] for r in checks}=={s['site_id'] for s in selected},'source yield mismatch'
 canonical=read(ROOT/'data/sites_OH.csv')
 verdicts=[];ev=[]
 for s in selected:
  rows=[r for r in checks if r['site_id']==s['site_id'] and r['street_address']];why=[]
  if not s['city'].strip():why.append('recorded city missing; establish locality before filling street')
  if not rows:why.append('need own-page physical street block at recorded city; no admissible block fetched')
  peers=[t for t in canonical if t['site_id']!=s['site_id'] and t['org_id']==s['org_id'] and t['operating_status']=='active' and key(t['city'])==key(s['city']) and (not s['zip'] or not t['zip'] or s['zip'][:5]==t['zip'][:5])]
  if rows and peers and not note_streets(s):why.append('generic corporate address lacks site-specific binding among same-operator city/ZIP records')
  if any(r['posture'] for r in rows):why.append('mailing-only or ambiguous address context')
  host=lambda u:(urlparse(u if '://' in u else 'https://'+u).hostname or '').removeprefix('www.')
  for r in rows:
   assert host(r['url'])==host(s['website']),'witness leaves held operator host'
   assert re.fullmatch('[0-9a-f]{64}',r['sha256']),'missing page digest'
   assert any(key(a)==key(r['street_address']) and z==r['source_zip'] for a,z,q in extract(r['quote'],s['city'])),'quote/field binding failure'
  if len({key(r['street_address']) for r in rows})>1:why.append('own-page street blocks disagree')
  if len({r['source_zip'][:5] for r in rows})>1:why.append('own-page ZIPs disagree')
  if any(s['zip'] and s['zip'][:5]!=r['source_zip'][:5] for r in rows):why.append('own-page ZIP conflicts with current site ZIP')
  if rows and re.search(r'(?i)\bZIP discrepancy:',s['notes']):why.append('existing notes name an unresolved ZIP discrepancy; reconcile primary locality first')
  if rows and any(key(n)!=key(rows[0]['street_address']) for n in note_streets(s)):why.append('notes address conflicts; dated adjudication needed')
  if any(key(r['street_address']).startswith(('PO BOX','P O BOX')) or not re.match(r'^\d+\s+[A-Za-z]',r['street_address']) for r in rows):why.append('non-physical or ambiguous street')
  v=dict(site_id=s['site_id'],verdict='STILL_UNCERTAIN' if why else 'VERIFIED',street_address=rows[0]['street_address'] if rows else '',evidence_id='' if why else s['reserved_evidence_id'],reason='; '.join(why))
  verdicts.append(v)
  if not why:
   r=rows[0];ev.append(dict(evidence_id=s['reserved_evidence_id'],record_table='sites',record_id=s['site_id'],claim_type='address',
       claim_detail=f"street_address {r['street_address']}, {s['city']}, OH; own-page ZIP {r['source_zip']}",
       source_class='own_site',source_ref=r['url'],observed_date=DATE,tier_effect='supports_A',created_by='atlas-L2-oh-address-7',
       notes=f"Raw checked {DATE}; SHA-256 {r['sha256']}; quote: {r['quote']}. County, county_source, ZIP and record tier unchanged."))
 assert len(verdicts)==len({v['site_id'] for v in verdicts})==88
 return selected,verdicts,ev
def note_plan():
 flags=read(TASK/'note_flags.csv');assert len(flags)==len({r['site_id'] for r in flags})==6
 frame={r['site_id']:r for r in read(TASK/'frame.csv')};ev=[]
 for r in flags:
  assert r['other_site_id'] in frame and r['site_id']!=r['other_site_id']
  if not r['evidence_id']:continue
  s=frame[r['site_id']]
  quote=r['source_notes'].split('; quote: ')[1].removesuffix('. County, county_source, ZIP and record tier unchanged.')
  assert any(key(a)==key(r['street_address']) and z==r['source_zip'] for a,z,q in extract(quote,s['city']))
  assert (urlparse(r['source_ref']).hostname or '').removeprefix('www.')==(urlparse(s['website']).hostname or '').removeprefix('www.')
  ev.append(dict(evidence_id=r['evidence_id'],record_table='sites',record_id=r['site_id'],claim_type='address',claim_detail=f"Address overlap lead with {r['other_site_id']}: both publish {r['street_address']}, {s['city']}; no merge or co-location adjudication",source_class='own_site',source_ref=r['source_ref'],observed_date=DATE,tier_effect='supports_A',created_by='atlas-L2-oh-address-7',notes=r['source_notes']))
 assert {e['evidence_id'] for e in ev}=={'EVD-152448','EVD-152449'}
 return flags,ev
def run(apply=False):
 selected,verdicts,ev=plan();sites=read(ROOT/'data/sites_OH.csv');byid={s['site_id']:s for s in sites};frozen={s['site_id']:s for s in selected};eb={e['record_id']:e for e in ev}
 flags,note_ev=note_plan();flag_byid={r['site_id']:r for r in flags};all_ev=ev+note_ev
 frame={r['site_id']:r for r in read(TASK/'frame.csv')}
 for r in flags:
  s=byid[r['site_id']];old=frame[r['site_id']]
  for field in ('org_id','city','state','county','county_source','zip','verification_tier','operating_status'):assert s[field]==old[field],(s['site_id'],field,'flag target changed')
  assert s['notes'] in (r['notes_before'],r['notes_before']+r['note_append']),'pre-existing notes conflict'
  assert s['street_address'] in ('',r['street_address']),'flag address changed'
  if r['site_id'] in eb:eb[r['site_id']]['claim_detail']+=f"; possible duplicate/co-location lead with {r['other_site_id']}; no adjudication"
 # Whole-namespace preflight, including foreign shards. No canonical write happens before every invariant passes.
 existing={}
 for p in (ROOT/'data').glob('evidence_*.csv'):
  for r in read(p):
   if r['evidence_id'] in {e['evidence_id'] for e in all_ev}:existing.setdefault(r['evidence_id'],[]).append((p.name,r))
 new=[]
 for v in verdicts:
  if v['verdict']!='VERIFIED':continue
  s=byid[v['site_id']];old=frozen[s['site_id']];e=eb[s['site_id']]
  for field in ('org_id','city','state','county','county_source','zip','verification_tier','operating_status'):assert s[field]==old[field],(s['site_id'],field,'main changed')
  assert s['notes'] in (old['notes'],old['notes']+flag_byid.get(s['site_id'],{}).get('note_append','')),'main notes changed'
  assert s['operating_status']=='active' and not old['street_address']
  assert s['street_address'] in ('',v['street_address']),'pre-existing street conflict'
  have=existing.get(e['evidence_id'],[])
  assert not have or have==[('evidence_sites_OH.csv',e)],'global evidence ID collision'
  if not have:new.append(e)
 for e in note_ev:
  have=existing.get(e['evidence_id'],[])
  assert not have or have==[('evidence_sites_OH.csv',e)],'global notes evidence ID collision'
  if not have:new.append(e)
 if apply:
  (TASK/'backups').mkdir(exist_ok=True)
  for name in ('sites_OH.csv','evidence_sites_OH.csv'):
   p=ROOT/'data'/name;b=TASK/'backups'/name
   if not b.exists():b.write_bytes(p.read_bytes())
  for v in verdicts:
   if v['verdict']!='VERIFIED':continue
   s=byid[v['site_id']];e=eb[s['site_id']];s['street_address']=v['street_address']
   if e['source_ref'] not in s['sources']:s['sources']+='; '+e['source_ref']
  for r in flags:byid[r['site_id']]['notes']=r['notes_before']+r['note_append']
  if new:append_sorted(ROOT/'data/evidence_sites_OH.csv',new,'evidence_id')
  write(ROOT/'data/sites_OH.csv',sites)
 write(TASK/'verdicts.csv',verdicts);write(TASK/'holds.csv',[r for r in verdicts if r['verdict']!='VERIFIED'])
 if all_ev:write(TASK/'evidence.csv',all_ev)
 active=[r for r in sites if r['operating_status']=='active']
 actual=sum(bool(s['street_address']) for s in active)
 before=actual-len(ev) if all(byid[e['record_id']]['street_address'] for e in ev) else actual
 summary=dict(eligible_sites=448,prior_batch_sites=360,worked=88,unworked=0,fills=len(ev),holds=88-len(ev),note_flags=len(flags),evidence_rows=len(all_ev),active_ohio_sites=len(active),before_streets=before,after_streets=before+len(ev))
 (TASK/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
if __name__=='__main__':run('--apply' in sys.argv)

FILE check.py
"""Check real fill boundary/replay and fail-before-write on street and cross-shard ID collisions."""
import contextlib,hashlib,io,shutil,tempfile
from pathlib import Path
import build
from fetch import mailing_posture
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 root=build.ROOT;selected,verdicts,ev=build.plan()
 flags,note_ev=build.note_plan();flag_byid={r['site_id']:r for r in flags}
 completion=build.read(build.TASK/'frame_completion.csv')
 assert len(completion)==len({r['site_id'] for r in completion})==448
 assert {r['site_id'] for r in completion}=={r['site_id'] for r in build.read(build.TASK/'frame.csv')}
 assert {r['site_id'] for r in completion if r['batch_pr']=='round7'}=={r['site_id'] for r in selected}
 for batch,n,fills in (('156',60,19),('171',100,38),('207',100,25),('208',100,36),('round7',88,24)):
  rows=[r for r in completion if r['batch_pr']==batch]
  assert len(rows)==n and sum(r['verdict']=='VERIFIED' for r in rows)==fills and sum(r['verdict']=='STILL_UNCERTAIN' for r in rows)==n-fills

 quote='1293 South Main Street Akron, Ohio 44301'
 for prefix in ('You can reach us by mail at this address: ','Mailing address: ','Postal address: '):assert mailing_posture(prefix+quote,quote)=='mailing-only context'
 assert not mailing_posture('Email us. Physical address: '+quote,quote)
 cases=[
  ('Elyria','Street: 710 Taylor Street, Elyria, OH 44035','710 Taylor Street'),
  ('Struthers','Street: 276 State Street, Struthers (company contact page). Converted from a verdict','276 State Street'),
  ('Avon','Street: 34910 Commerce Way (address per FDA establishment registration; verified). FDA FEI 123','34910 Commerce Way'),
  ('Youngstown','Street (per Grok): 3745 Hendricks Rd. county UNVERIFIED — Grok county_check=TRUE','3745 Hendricks Rd'),
  ('Ashland','Street (per Grok): 2040 Cellar Drive. Address confirmed 2026-10-29: source','2040 Cellar Drive'),
  ('Avon Lake','Street: 33490 Pin Oak Pkwy, Avon Lake. Co-located with distinct company','33490 Pin Oak Pkwy'),
  ('Test City','Street: 191 American Blvd, Suite 100, Test City (company contact page)','191 American Blvd, Suite 100'),
  ('Wooster',"Street: 1022 Heyl Rd (per the operator's own site / wave-2 verdict W2-026 evidence).",'1022 Heyl Rd'),
  ('Berea',"Street: 125 Pelret Industrial Pkwy (per wave-3 verdict W3-0166 evidence; own-site spelling 'Pelret'). Ecosystem org ORG-001594",'125 Pelret Industrial Pkwy'),
  ('Cleveland','Street: 4529 Industrial Pkwy. Filing basis: Check RUN and POSITIVE','4529 Industrial Pkwy')]
 for city,notes,expected in cases:
  leads=build.note_streets(dict(city=city,notes=notes));assert leads and build.key(leads[-1])==build.key(expected),(leads,expected)
 assert build.key(cases[6][2])!=build.key('191 American Blvd Suite 300'),'unit distinction erased'

 assert build.key('2184 State Rte 43')==build.key('2184 State Route 43')
 assert build.key('2184 State Rte 43')!=build.key('2184 State Route 44')
 assert build.key('2915 INDUSTRIAL PARK DR')==build.key('2915 Industrial Pk Dr')
 assert build.key('7675 JENTHER DR')!=build.key('7676 JENTHER DR')
 assert build.key(build.note_streets(dict(city='Middlefield',notes='Street: 16090 Industrial Parkway, Unit 1 (per wave-3 verdict W3-0600 evidence).'))[-1])!=build.key('16090 Industrial Parkway')

 for sid in ('SITE-001865','SITE-001909','SITE-001916','SITE-001931'):
  assert next(v for v in verdicts if v['site_id']==sid)['verdict']=='STILL_UNCERTAIN',sid
 assert len(ev)==24,'frozen source-adjudication yield changed; inspect before revising'
 with tempfile.TemporaryDirectory() as tmp:
  build.ROOT=Path(tmp);(build.ROOT/'data').mkdir()
  for p in (root/'data').glob('evidence_*.csv'):shutil.copyfile(p,build.ROOT/'data'/p.name)
  shutil.copyfile(root/'data/sites_OH.csv',build.ROOT/'data/sites_OH.csv')
  frozen={r['site_id']:r for r in selected};before=build.read(build.ROOT/'data/sites_OH.csv')
  for r in before:
   if r['site_id'] in frozen:
    old=frozen[r['site_id']]
    for k in r:r[k]=old[k]
   if r['site_id'] in flag_byid:r['notes']=flag_byid[r['site_id']]['notes_before']
  build.write(build.ROOT/'data/sites_OH.csv',before)
  p=build.ROOT/'data/evidence_sites_OH.csv'
  build.write(p,[r for r in build.read(p) if r['created_by']!='atlas-L2-oh-address-7'])
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  after=build.read(build.ROOT/'data/sites_OH.csv');changed=0;streets=0;notes=0
  assert len(before)==len(after)
  for a,b in zip(before,after):
   fields={k for k in a if a[k]!=b[k]}
   assert fields <= {'street_address','sources','notes'},(a['site_id'],fields)
   if fields:
    changed+=1;assert a['operating_status']=='active'
   if 'street_address' in fields:streets+=1;assert not a['street_address'] and b['street_address']
   if 'notes' in fields:
    notes+=1;r=flag_byid[a['site_id']];assert a['notes']==r['notes_before'] and b['notes']==r['notes_before']+r['note_append']
  assert changed==26 and streets==len(ev)==24 and notes==6
  paths=list((build.ROOT/'data').glob('*.csv'));hashes={p.name:digest(p) for p in paths}
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  assert hashes=={p.name:digest(p) for p in paths},'not byte-idempotent'
  target=next(r for a,r in zip(before,after) if not a['street_address'] and r['street_address'])
  original=target['street_address'];target['street_address']='999 WRONG ROAD';build.write(build.ROOT/'data/sites_OH.csv',after)
  hashes={p.name:digest(p) for p in paths}
  try:
   with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  except AssertionError:pass
  else:raise AssertionError('street conflict overwritten')
  assert hashes=={p.name:digest(p) for p in paths},'wrote before conflict refusal'
  target['street_address']=original;build.write(build.ROOT/'data/sites_OH.csv',after)
  flag_target=next(r for r in after if r['site_id'] in flag_byid);original_note=flag_target['notes'];flag_target['notes']+=' UNRELATED EDIT'
  build.write(build.ROOT/'data/sites_OH.csv',after);hashes={p.name:digest(p) for p in paths}
  try:
   with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  except AssertionError:pass
  else:raise AssertionError('unrelated note change overwritten')
  assert hashes=={p.name:digest(p) for p in paths},'wrote before notes conflict refusal'
  flag_target['notes']=original_note;build.write(build.ROOT/'data/sites_OH.csv',after)
  foreign=build.ROOT/'data/evidence_sites_ZZ.csv'
  for foreign_row in (ev[0],note_ev[-1]):
   build.write(foreign,[foreign_row])
   paths=list((build.ROOT/'data').glob('*.csv'));hashes={p.name:digest(p) for p in paths}
   try:
    with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
   except AssertionError:pass
   else:raise AssertionError('foreign-shard evidence collision accepted')
   assert hashes=={p.name:digest(p) for p in paths},'wrote before global collision refusal'

 build.ROOT=root
 print(f'PASS {len(ev)} fills +6 authorized notes/26 evidence; field boundary; byte-idempotent; street, notes and late notes-only foreign-ID mutations rejected before canonical writes')
if __name__=='__main__':main()

FILE audit.py
"""Seeded 30-fill fresh raw-page audit, with a full census when fewer than30 accepted."""
import concurrent.futures,json,random
from build import TASK,read
from fetch import fetch,write,extract,mailing_posture
evidence=read(TASK/'evidence.csv');sample=random.Random(20261106).sample(sorted(evidence,key=lambda e:e['record_id']),min(30,len(evidence)));sites={r['site_id']:r for r in read(TASK/'frame.csv')}
def check(e):
 error='';sha=''
 try:
  text,links,sha=fetch(e['source_ref'])
  quote=e['notes'].split('; quote: ')[1].removesuffix('. County, county_source, ZIP and record tier unchanged.')
  assert ' '.join(quote.split()) in ' '.join(text.split()),'raw quote absent on fresh fetch'
  assert extract(quote,sites[e['record_id']]['city']),'quote not a city-specific physical address block'
  assert not mailing_posture(text,quote),'mailing-only context on fresh audit'
 except Exception as ex:error=str(ex)
 return dict(site_id=e['record_id'],kind='street_fill' if e['claim_detail'].startswith('street_address ') else 'note_flag',source_ref=e['source_ref'],sha256=sha,result='PASS' if not error else 'FAIL',error=error)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(check,sample))
write(TASK/'audit.csv',out)
summary=dict(accepted_street_fills=sum(e['claim_detail'].startswith('street_address ') for e in evidence),address_evidence_rows=len(evidence),audited=len(out),audited_street_fills=sum(r['kind']=='street_fill' for r in out),audited_note_flags=sum(r['kind']=='note_flag' for r in out),errors=sum(bool(r['error']) for r in out))
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert len(out)==min(30,len(evidence)) and summary['errors']==0,out

SELECTED INPUTS;fullnames/notes in frame.csv
site_id,org_id,city,zip,county,verification_tier,website,reserved_evidence_id
SITE-001851,ORG-001768,Kent,44240,Portage,A,https://actionsuper.com,EVD-152360
SITE-001852,ORG-001769,Cleveland,44114,Cuyahoga,A,https://adherexpackaging.com,EVD-152361
SITE-001854,ORG-001774,Akron,44311,Summit,A,https://alcontool.com,EVD-152362
SITE-001855,ORG-001776,Alliance,44601,Stark,B,https://slesnick.com,EVD-152363
SITE-001856,ORG-001777,Solon,44139,Cuyahoga,A,https://anchor-online.com,EVD-152364
SITE-001858,ORG-001779,Garfield Heights,44125,Cuyahoga,A,https://americansignproducts.com,EVD-152365
SITE-001859,ORG-001780,Akron,44310,Summit,A,https://americantestingtechnologies.com,EVD-152366
SITE-001860,ORG-001781,Eastlake,44095,Lake,B,https://astromfg.com,EVD-152367
SITE-001861,ORG-001783,Lakewood,44107,Cuyahoga,A,https://beacongasket.com,EVD-152368
SITE-001862,ORG-001784,North Lawrence,44666,Stark,A,https://bfplasticsinc.com,EVD-152369
SITE-001864,ORG-001788,Kent,44240,Portage,A,https://colonialpatt.com,EVD-152370
SITE-001865,ORG-001791,Kent,44240,Portage,A,https://cosarmold.com,EVD-152371
SITE-001867,ORG-001793,Boardman,44512,Mahoning,A,https://customtarpaulin.com,EVD-152372
SITE-001873,ORG-001806,Eastlake,44095,Lake,B,https://enpress.com,EVD-152373
SITE-001874,ORG-001808,Richfield,44286,Summit,A,https://eurotechdirect.com,EVD-152374
SITE-001875,ORG-001810,Macedonia,44056,Summit,A,https://expertgasket.com,EVD-152375
SITE-001876,ORG-001817,Cleveland,44112,Cuyahoga,A,https://g2materials.com,EVD-152376
SITE-001880,ORG-001826,Kent,44240,Portage,A,https://hapcoinc.com,EVD-152377
SITE-001882,ORG-001829,Streetsboro,44241,Portage,B,https://horsemenspride.com,EVD-152378
SITE-001883,ORG-001830,Twinsburg,44087,Summit,A,https://impactsleeves.com,EVD-152379
SITE-001888,ORG-001855,Cleveland,44102,Cuyahoga,A,https://newkor.com,EVD-152380
SITE-001889,ORG-001856,Barberton,44203,Summit,A,https://novationsi.com,EVD-152381
SITE-001891,ORG-001859,Aurora,44202,Portage,A,https://oem-miller.com,EVD-152382
SITE-001893,ORG-001868,Akron,44310,Summit,A,https://polymetrecovery.com,EVD-152383
SITE-001894,ORG-001869,Solon,44139,Cuyahoga,A,https://prolineautomation.com,EVD-152384
SITE-001895,ORG-001878,Chagrin Falls,44023,Geauga,A,https://qubeinc.com,EVD-152385
SITE-001896,ORG-001879,Akron,,Summit,A,https://rainbowmastermixing.com,EVD-152386
SITE-001897,ORG-001880,Akron,44310,Summit,A,https://razoredgeprecisiongrinding.com,EVD-152387
SITE-001898,ORG-001883,Hudson,44236,Summit,A,https://rezkemchemicals.com,EVD-152388
SITE-001899,ORG-001891,Brunswick,44212,Medina,A,https://inflatableimages.com,EVD-152389
SITE-001900,ORG-001892,Elyria,44035,Lorain,A,https://schibley.com,EVD-152390
SITE-001904,ORG-001905,Garfield Heights,44125,Cuyahoga,A,https://thermoprene.com,EVD-152391
SITE-001905,ORG-001911,Akron,44305,Summit,A,https://unitedfeedscrews.com,EVD-152392
SITE-001908,ORG-001916,Willoughby,44094,Lake,A,https://zerodproducts.com,EVD-152393
SITE-001909,ORG-001917,Medina,44256,Medina,A,guildcpo.com,EVD-152394
SITE-001916,ORG-000697,Ashland,44805,Ashland,B,https://hedstrom.com/,EVD-152395
SITE-001917,ORG-001923,Akron,44305,Summit,B,https://artemispolymerprocessing.com,EVD-152396
SITE-001922,ORG-001928,Burton,44021,Geauga,A,https://green-processing.com,EVD-152397
SITE-001923,ORG-001929,Middleburg Heights,44130,Cuyahoga,A,https://hycompinc.com,EVD-152398
SITE-001924,ORG-001930,Mentor,44060,Lake,A,http://www.itplastics.com/,EVD-152399
SITE-001927,ORG-001933,New Philadelphia,44663,Tuscarawas,B,https://performance-additives.com,EVD-152400
SITE-001928,ORG-001934,Canal Fulton,44614,Stark,B,https://rackpowdercoating.com,EVD-152401
SITE-001930,ORG-001936,Akron,44312,Summit,A,https://rotocastmold.com,EVD-152402
SITE-001931,ORG-001937,Wooster,44691,Wayne,A,https://smetzertire.com,EVD-152403
SITE-001933,ORG-001939,Creston,44217,Wayne,B,https://ecoflexrtpv.com,EVD-152404
SITE-001935,ORG-001941,Chagrin Falls,44023,Geauga,B,https://thermopackaging.com,EVD-152405
SITE-001937,ORG-001943,Tallmadge,44278,Summit,B,https://trans-foam.com,EVD-152406
SITE-001939,ORG-001945,North Jackson,44451,Mahoning,B,https://vinylprofilesinc.com,EVD-152407
SITE-001940,ORG-001946,Ashland,44805,Ashland,B,https://waugs.com,EVD-152408
SITE-001941,ORG-001947,Ashtabula,44004,Ashtabula,B,https://aammold.com/index.html,EVD-152409
SITE-001943,ORG-001949,Akron,44319,Summit,B,polinggroup.com,EVD-152410
SITE-001945,ORG-001951,Elyria,44035,Lorain,B,castekusa.com,EVD-152411
SITE-001951,ORG-001957,Akron,44313,Summit,A,http://friessequipment.com/,EVD-152412
SITE-001952,ORG-001958,Brunswick,44212,Medina,B,http://www.icslabs.com/,EVD-152413
SITE-001953,ORG-001959,Akron,44312,Summit,B,https://tiremolds.com,EVD-152414
SITE-001957,ORG-001963,Munroe Falls,44262,Summit,A,msbmachine.com,EVD-152415
SITE-001959,ORG-001965,Akron,44311,Summit,B,http://www.mcneilnrm.com/,EVD-152416
SITE-001972,ORG-001978,Canton,44709,Stark,A,sprayworksequipment.com,EVD-152417
SITE-001980,ORG-001986,Kent,44240,Portage,B,https://optimaxplastic.com/index.php/rotomolding/,EVD-152418
SITE-001986,ORG-001992,Perry,44081,Lake,B,https://precisionpolymercasting.com/,EVD-152419
SITE-001991,ORG-001997,Akron,44310,Summit,B,quikey.com,EVD-152420
SITE-001992,ORG-001998,North Lima,44452,Mahoning,B,ram-plastics.com,EVD-152421
SITE-001993,ORG-001999,Wadsworth,44281,Medina,B,raydarrubber.com,EVD-152422
SITE-002001,ORG-002007,Akron,44306,Summit,A,http://www.s-aindustries.com/,EVD-152423
SITE-002004,ORG-002010,Louisville,44641,Stark,B,sherwoodcorp.com,EVD-152424
SITE-002005,ORG-002011,Medina,44256,Medina,A,solutionsinpc.com,EVD-152425
SITE-002008,ORG-002014,Mogadore,44260,Portage,B,http://www.stroupbelting.com/,EVD-152426
SITE-002012,ORG-002018,Columbia Station,44028,Lorain,A,telarcorp.com,EVD-152427
SITE-002016,ORG-002022,Streetsboro,44241,Portage,A,simplay3.com,EVD-152428
SITE-002025,ORG-002031,North Jackson,44451,Mahoning,B,vinyltechint.com,EVD-152429
SITE-002028,ORG-002034,Chagrin Falls,44023,Geauga,A,https://gizmowhipguide.com,EVD-152430
SITE-002031,ORG-002037,Twinsburg,44087,Summit,B,zingpac.com,EVD-152431
SITE-002032,ORG-002038,Akron,44320,Summit,B,pinnaclerecyclingllc.com,EVD-152432
SITE-002033,ORG-002039,Cleveland,44111,Cuyahoga,A,https://www.paramelt.com,EVD-152433
SITE-002037,ORG-002043,Bellevue,44811,Huron,A,https://mcpp-global.com,EVD-152434
SITE-002038,ORG-000103,Akron,44306,Summit,A,https://hexpolcompounding.com,EVD-152435
SITE-002041,ORG-002047,Conneaut,44030,Ashtabula,B,https://wayne-dalton.com,EVD-152436
SITE-002043,ORG-002049,Bedford,44146,Cuyahoga,A,https://sietins.com,EVD-152437
SITE-002052,ORG-001787,Tallmadge,,Summit,B,https://circlemold.com,EVD-152438
SITE-002067,ORG-002067,Oakwood,44146,Cuyahoga,B,https://www.aropha.com,EVD-152439
SITE-002068,ORG-002068,Akron,44308,Summit,B,https://www.chemstress.com,EVD-152440
SITE-002069,ORG-002069,Minerva,44657,Stark,B,https://www.summitglove.com,EVD-152441
SITE-002073,ORG-002073,Wooster,44691,Wayne,B,https://energyene.com,EVD-152442
SITE-002079,ORG-000698,Elyria,44035,Lorain,A,https://www.basf.com/us/en.html,EVD-152443
SITE-002082,ORG-000005,Twinsburg,44087,Summit,A,https://www.dayglo.com,EVD-152444
SITE-002084,ORG-000002,Painesville,44077,Lake,B,https://www.lubrizol.com,EVD-152445
SITE-002110,ORG-002153,Canton,,Stark,A,alphaworld.com,EVD-152446
SITE-002904,ORG-000009,Wadsworth,,Medina,B,https://www.myersindustries.com,EVD-152447

AUTHORIZED NOTE FLAGS;exact oldnotes in note_flags.csv
site_id,other_site_id,note_append,evidence_id
SITE-001858,SITE-001904," ADDRESS-OVERLAP LEAD (2026-11-06): possible co-location/duplicate with SITE-001904; both publish 5718 Transportation Blvd., Garfield Heights. No merge, site_group or status adjudication. Sources: https://americansignproducts.com; https://thermoprene.com.",
SITE-001904,SITE-001858," ADDRESS-OVERLAP LEAD (2026-11-06): possible co-location/duplicate with SITE-001858; both publish 5718 Transportation Blvd, Garfield Heights. No merge, site_group or status adjudication. Sources: https://thermoprene.com; https://americansignproducts.com.",
SITE-001882,SITE-001721," ADDRESS-OVERLAP LEAD (2026-11-06): possible co-location/duplicate with SITE-001721; both publish 10008 State Route 43, Streetsboro. No merge, site_group or status adjudication. Sources: https://horsemenspride.com; http://www.tuscoproducts.com/.",
SITE-001721,SITE-001882," ADDRESS-OVERLAP LEAD (2026-11-06): possible co-location/duplicate with SITE-001882; both publish 10008 State Route 43, Streetsboro. No merge, site_group or status adjudication. Sources: http://www.tuscoproducts.com/; https://horsemenspride.com.",EVD-152448
SITE-001924,SITE-001717," ADDRESS-OVERLAP LEAD (2026-11-06): possible co-location/duplicate with SITE-001717; both publish 7675 Jenther Dr, Mentor. No merge, site_group or status adjudication. Sources: http://www.itplastics.com/; https://www.overmoldexpress.com/.",
SITE-001717,SITE-001924," ADDRESS-OVERLAP LEAD (2026-11-06): possible co-location/duplicate with SITE-001924; both publish 7675 Jenther Dr, Mentor. No merge, site_group or status adjudication. Sources: https://www.overmoldexpress.com/; http://www.itplastics.com/.",EVD-152449

FILE evidence.csv
evidence_id,record_table,record_id,claim_type,claim_detail,source_class,source_ref,observed_date,tier_effect,created_by,notes
EVD-152361,sites,SITE-001852,address,"street_address 3100 Hamilton Avenue, Cleveland, OH; own-page ZIP 44114",own_site,https://adherexpackaging.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 aa8e1a6dc16c8288c053f1743bd0df8b26df571c73bd95c18ecc7f5d62fb5d8d; quote: 3100 Hamilton Avenue, Cleveland, Ohio 44114. County, county_source, ZIP and record tier unchanged."
EVD-152362,sites,SITE-001854,address,"street_address 565 Lafollette St., Akron, OH; own-page ZIP 44311",own_site,https://alcontool.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 f5d13aea945736f18fa9d24b54fd1657f47e1624feb8453d90e221bd44b9d946; quote: 565 Lafollette St. Akron, OH 44311. County, county_source, ZIP and record tier unchanged."
EVD-152365,sites,SITE-001858,address,"street_address 5718 Transportation Blvd., Garfield Heights, OH; own-page ZIP 44125; possible duplicate/co-location lead with SITE-001904; no adjudication",own_site,https://americansignproducts.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 01abe995c01d36c8e01583883e970217763841091c9cfddcab964263d240ab08; quote: 5718 Transportation Blvd. Garfield Heights, OH 44125. County, county_source, ZIP and record tier unchanged."
EVD-152367,sites,SITE-001860,address,"street_address 34459 Curtis Boulevard, Eastlake, OH; own-page ZIP 44095",own_site,https://astromfg.com/contact-us,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 835af5489a346cc345da4073eac6e74d8b402b7590c9e167695d039ade6cd655; quote: 34459 Curtis Boulevard Eastlake, Ohio 44095. County, county_source, ZIP and record tier unchanged."
EVD-152368,sites,SITE-001861,address,"street_address 1610 Coutant Avenue, Lakewood, OH; own-page ZIP 44107",own_site,https://beacongasket.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 744b7d747816982f1169354360bdb25b21342582e66b84672992e31e9eb60f35; quote: 1610 Coutant Avenue Lakewood, Ohio 44107. County, county_source, ZIP and record tier unchanged."
EVD-152370,sites,SITE-001864,address,"street_address 920 OVERHOLT RD, Kent, OH; own-page ZIP 44240",own_site,https://colonialpatt.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 b1c17cf569e4700bbec049f30bba727fc9fa35a1c035e0b0122dfa2698c76cd2; quote: 920 OVERHOLT RD KENT, OHIO 44240. County, county_source, ZIP and record tier unchanged."
EVD-152372,sites,SITE-001867,address,"street_address 8095 Southern Blvd., Boardman, OH; own-page ZIP 44512",own_site,https://customtarpaulin.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 48f9db577cbb44d30dae1896fd4fb7319b65aedcf3335ba4fc23a2b6532ff7f3; quote: 8095 Southern Blvd. Boardman, OH 44512. County, county_source, ZIP and record tier unchanged."
EVD-152376,sites,SITE-001876,address,"street_address 1700 London Road, Cleveland, OH; own-page ZIP 44112",own_site,https://g2materials.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 2b328627f3a370f1efe03ca43abccc213f20a7dd9a141f35c965dd9fd257122a; quote: 1700 London Road Cleveland, OH 44112. County, county_source, ZIP and record tier unchanged."
EVD-152377,sites,SITE-001880,address,"street_address 390 Portage Blvd., Kent, OH; own-page ZIP 44240",own_site,https://hapcoinc.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 bb0a80846f9c869c4bfa72fa5e38112362680fe83fbbf67d7f6ab2c01b4a7ff5; quote: 390 Portage Blvd. Kent, OH 44240. County, county_source, ZIP and record tier unchanged."
EVD-152378,sites,SITE-001882,address,"street_address 10008 State Route 43, Streetsboro, OH; own-page ZIP 44241; possible duplicate/co-location lead with SITE-001721; no adjudication",own_site,https://horsemenspride.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 2b5c20e3624e089a1e70e3d9f8db7087e5a6d892fbd4b90654f3bc8e714ac9b8; quote: 10008 State Route 43 Streetsboro, Ohio 44241. County, county_source, ZIP and record tier unchanged."
EVD-152380,sites,SITE-001888,address,"street_address 10410 Berea Road, Cleveland, OH; own-page ZIP 44102",own_site,https://newkor.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 394a70e97bf46b28dee6a9748341b3a5af82b3ef6154cb84d6074060cbaa5858; quote: 10410 Berea Road Cleveland, OH 44102. County, county_source, ZIP and record tier unchanged."
EVD-152383,sites,SITE-001893,address,"street_address 1280 Devalera St., Akron, OH; own-page ZIP 44310",own_site,https://polymetrecovery.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 5422e671b532dcd9972b8fe1c2a3551a3597a7d1419c0616220f9cd6471e37c9; quote: 1280 Devalera St. Akron, OH 44310. County, county_source, ZIP and record tier unchanged."
EVD-152385,sites,SITE-001895,address,"street_address 16744 West Park Circle Drive, Chagrin Falls, OH; own-page ZIP 44023",own_site,https://qubeinc.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 25d5e05700def58ab07e677502559f450b89afa62f3750638b04a549482598db; quote: 16744 West Park Circle Drive | Chagrin Falls, OH 44023. County, county_source, ZIP and record tier unchanged."
EVD-152386,sites,SITE-001896,address,"street_address 467 Dan St., Akron, OH; own-page ZIP 44310",own_site,https://rainbowmastermixing.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 73bdac57c76679be068b07bedd5056e0cfea3202304a833d32606f9654630a69; quote: 467 Dan St., Akron, OH 44310. County, county_source, ZIP and record tier unchanged."
EVD-152389,sites,SITE-001899,address,"street_address 2880 Interstate Parkway, Brunswick, OH; own-page ZIP 44212",own_site,https://inflatableimages.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 7f2457ba690a17b575bbc1546e1b71fc258385ef39b56f31f4583b8fbbe1b454; quote: 2880 Interstate Parkway Brunswick, OH 44212. County, county_source, ZIP and record tier unchanged."
EVD-152391,sites,SITE-001904,address,"street_address 5718 Transportation Blvd, Garfield Heights, OH; own-page ZIP 44125; possible duplicate/co-location lead with SITE-001858; no adjudication",own_site,https://thermoprene.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 af78d0c66dbbca0f7e7d68c70e837fa0274bb2c9edd59def0a998c0512c86f9b; quote: 5718 Transportation Blvd, Garfield Heights, OH 44125. County, county_source, ZIP and record tier unchanged."
EVD-152392,sites,SITE-001905,address,"street_address 487 Wellington Avenue, Akron, OH; own-page ZIP 44305",own_site,https://unitedfeedscrews.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 bfc4c848b70e23d89c626142ad80d10c6f3485d6f54c3beff5bfd1a17d0c2b9b; quote: 487 Wellington Avenue, Akron, Ohio 44305. County, county_source, ZIP and record tier unchanged."
EVD-152399,sites,SITE-001924,address,"street_address 7675 Jenther Dr, Mentor, OH; own-page ZIP 44060; possible duplicate/co-location lead with SITE-001717; no adjudication",own_site,http://www.itplastics.com/,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 1eebc6846e0a0c0f3f981aa732d659a3c124fee7cdbba701339749f99f61b84e; quote: 7675 Jenther Dr Mentor, Ohio 44060. County, county_source, ZIP and record tier unchanged."
EVD-152402,sites,SITE-001930,address,"street_address 1900 Englewood Ave, Akron, OH; own-page ZIP 44312",own_site,https://rotocastmold.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 5d16dc71036448e32fc7422000d6a276efd5ebc986910d80b875c09320ebfd03; quote: 1900 Englewood Ave Akron, OH 44312. County, county_source, ZIP and record tier unchanged."
EVD-152411,sites,SITE-001945,address,"street_address 527 Ternes Ln, Elyria, OH; own-page ZIP 44035",own_site,https://castekusa.com/contact/,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 90668c8280f2146d2748abf0e04854023b47d699ad8670c4def0b73bb9ec7ad7; quote: 527 Ternes Ln, Elyria, OH 44035. County, county_source, ZIP and record tier unchanged."
EVD-152415,sites,SITE-001957,address,"street_address 36 Castle Dr, Munroe Falls, OH; own-page ZIP 44262",own_site,https://msbmachine.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 62a1062a244eb4e9870547e0cd7fa8ae1cf98f72fcfef028fa442a7c05b0343d; quote: 36 Castle Dr, Munroe Falls, OH 44262. County, county_source, ZIP and record tier unchanged."
EVD-152426,sites,SITE-002008,address,"street_address 2184 State Route 43, Mogadore, OH; own-page ZIP 44260",own_site,http://www.stroupbelting.com/,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 7b56c4edaaa2c7364cc8f989743dacd33c4a48dcc94350eaa392aad6b814c16a; quote: 2184 State Route 43 Mogadore, Oh 44260. County, county_source, ZIP and record tier unchanged."
EVD-152428,sites,SITE-002016,address,"street_address 9450 Rosemont Drive, Streetsboro, OH; own-page ZIP 44241",own_site,https://simplay3.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 051cb00b15a1ede4bc6a19f5658f90ea1c6f0524f7efec9ea5a8bde3a2b751ba; quote: 9450 Rosemont Drive Streetsboro, OH 44241. County, county_source, ZIP and record tier unchanged."
EVD-152430,sites,SITE-002028,address,"street_address 16829 Park Circle Drive, Chagrin Falls, OH; own-page ZIP 44023-4515",own_site,https://gizmowhipguide.com,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 e1d00248a9cb4ae4827b0da5e420257ee110fd17156f8ae68932faaa87c64fde; quote: 16829 Park Circle Drive • Chagrin Falls, Ohio 44023-4515. County, county_source, ZIP and record tier unchanged."
EVD-152448,sites,SITE-001721,address,"Address overlap lead with SITE-001882: both publish 10008 State Route 43, Streetsboro; no merge or co-location adjudication",own_site,http://www.tuscoproducts.com/,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 5a490fbce1d7763f22db3035213ec5de618a95642c102882da4ebd5abb7e412e; quote: 10008 State Route 43 Streetsboro, Ohio 44241. County, county_source, ZIP and record tier unchanged."
EVD-152449,sites,SITE-001717,address,"Address overlap lead with SITE-001924: both publish 7675 Jenther Dr, Mentor; no merge or co-location adjudication",own_site,https://www.overmoldexpress.com/,2026-11-06,supports_A,atlas-L2-oh-address-7,"Raw checked 2026-11-06; SHA-256 7133716e8923fa8a399deacb6f1ac62661bc4ec442fa650fe729f09485c7b8b8; quote: 7675 Jenther Dr, Mentor, OH 44060. County, county_source, ZIP and record tier unchanged."

FILE verdicts.csv
site_id,verdict,street_address,evidence_id,reason
SITE-001851,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001852,VERIFIED,3100 Hamilton Avenue,EVD-152361,
SITE-001854,VERIFIED,565 Lafollette St.,EVD-152362,
SITE-001855,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001856,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001858,VERIFIED,5718 Transportation Blvd.,EVD-152365,
SITE-001859,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001860,VERIFIED,34459 Curtis Boulevard,EVD-152367,
SITE-001861,VERIFIED,1610 Coutant Avenue,EVD-152368,
SITE-001862,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001864,VERIFIED,920 OVERHOLT RD,EVD-152370,
SITE-001865,STILL_UNCERTAIN,395 Portage Blvd,,mailing-only or ambiguous address context
SITE-001867,VERIFIED,8095 Southern Blvd.,EVD-152372,
SITE-001873,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001874,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001875,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001876,VERIFIED,1700 London Road,EVD-152376,
SITE-001880,VERIFIED,390 Portage Blvd.,EVD-152377,
SITE-001882,VERIFIED,10008 State Route 43,EVD-152378,
SITE-001883,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001888,VERIFIED,10410 Berea Road,EVD-152380,
SITE-001889,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001891,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001893,VERIFIED,1280 Devalera St.,EVD-152383,
SITE-001894,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001895,VERIFIED,16744 West Park Circle Drive,EVD-152385,
SITE-001896,VERIFIED,467 Dan St.,EVD-152386,
SITE-001897,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001898,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001899,VERIFIED,2880 Interstate Parkway,EVD-152389,
SITE-001900,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001904,VERIFIED,5718 Transportation Blvd,EVD-152391,
SITE-001905,VERIFIED,487 Wellington Avenue,EVD-152392,
SITE-001908,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001909,STILL_UNCERTAIN,3637 Medina Rd,,notes address conflicts; dated adjudication needed
SITE-001916,STILL_UNCERTAIN,2040 Cellar Drive,,notes address conflicts; dated adjudication needed
SITE-001917,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001922,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001923,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001924,VERIFIED,7675 Jenther Dr,EVD-152399,
SITE-001927,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001928,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001930,VERIFIED,1900 Englewood Ave,EVD-152402,
SITE-001931,STILL_UNCERTAIN,352 W. Liberty St.,,own-page street blocks disagree; notes address conflicts; dated adjudication needed
SITE-001933,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001935,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001937,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001939,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001940,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001941,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001943,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001945,VERIFIED,527 Ternes Ln,EVD-152411,
SITE-001951,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001952,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001953,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001957,VERIFIED,36 Castle Dr,EVD-152415,
SITE-001959,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001972,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001980,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001986,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001991,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001992,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001993,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002001,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002004,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002005,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002008,VERIFIED,2184 State Route 43,EVD-152426,
SITE-002012,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002016,VERIFIED,9450 Rosemont Drive,EVD-152428,
SITE-002025,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002028,VERIFIED,16829 Park Circle Drive,EVD-152430,
SITE-002031,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002032,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002033,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002037,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002038,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002041,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002043,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002052,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002067,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002068,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002069,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002073,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002079,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002082,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002084,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002110,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-002904,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched

FILE audit.csv
site_id,kind,source_ref,sha256,result,error
SITE-001930,street_fill,https://rotocastmold.com,5d16dc71036448e32fc7422000d6a276efd5ebc986910d80b875c09320ebfd03,PASS,
SITE-001721,note_flag,http://www.tuscoproducts.com/,9b29ebd9a4246f216dc451585a91f393a131ecb2e8211bcff1bee4705226c2db,PASS,
SITE-001852,street_fill,https://adherexpackaging.com,6079da5191e2c39d8cc25d5a4d46f32335e42a2b23fdd160821ca33d11f1ff4f,PASS,
SITE-001858,street_fill,https://americansignproducts.com,01abe995c01d36c8e01583883e970217763841091c9cfddcab964263d240ab08,PASS,
SITE-001864,street_fill,https://colonialpatt.com,cd44af3ce207078cf35edefb875335233231790b703f0371b0b83b26dcc34695,PASS,
SITE-001717,note_flag,https://www.overmoldexpress.com/,7133716e8923fa8a399deacb6f1ac62661bc4ec442fa650fe729f09485c7b8b8,PASS,
SITE-001924,street_fill,http://www.itplastics.com/,1eebc6846e0a0c0f3f981aa732d659a3c124fee7cdbba701339749f99f61b84e,PASS,
SITE-001880,street_fill,https://hapcoinc.com,e7252d8eb568adcca2d8b4a5340e74527f77b1f3807d87efa888e77592db586d,PASS,
SITE-001888,street_fill,https://newkor.com,394a70e97bf46b28dee6a9748341b3a5af82b3ef6154cb84d6074060cbaa5858,PASS,
SITE-001867,street_fill,https://customtarpaulin.com,48f9db577cbb44d30dae1896fd4fb7319b65aedcf3335ba4fc23a2b6532ff7f3,PASS,
SITE-002028,street_fill,https://gizmowhipguide.com,e1d00248a9cb4ae4827b0da5e420257ee110fd17156f8ae68932faaa87c64fde,PASS,
SITE-001905,street_fill,https://unitedfeedscrews.com,bfc4c848b70e23d89c626142ad80d10c6f3485d6f54c3beff5bfd1a17d0c2b9b,PASS,
SITE-001896,street_fill,https://rainbowmastermixing.com,73bdac57c76679be068b07bedd5056e0cfea3202304a833d32606f9654630a69,PASS,
SITE-002016,street_fill,https://simplay3.com,06b9031c53b9c0006eda61fc23ea76ae5f416b0acda4b9cb6e7b9417ff3a1962,PASS,
SITE-001854,street_fill,https://alcontool.com,f5d13aea945736f18fa9d24b54fd1657f47e1624feb8453d90e221bd44b9d946,PASS,
SITE-001957,street_fill,https://msbmachine.com,62a1062a244eb4e9870547e0cd7fa8ae1cf98f72fcfef028fa442a7c05b0343d,PASS,
SITE-002008,street_fill,http://www.stroupbelting.com/,7b56c4edaaa2c7364cc8f989743dacd33c4a48dcc94350eaa392aad6b814c16a,PASS,
SITE-001876,street_fill,https://g2materials.com,2b328627f3a370f1efe03ca43abccc213f20a7dd9a141f35c965dd9fd257122a,PASS,
SITE-001895,street_fill,https://qubeinc.com,25d5e05700def58ab07e677502559f450b89afa62f3750638b04a549482598db,PASS,
SITE-001945,street_fill,https://castekusa.com/contact/,90668c8280f2146d2748abf0e04854023b47d699ad8670c4def0b73bb9ec7ad7,PASS,
SITE-001904,street_fill,https://thermoprene.com,58990a6eb8bdb24d1fc93abd6c01518486126ff5fc1522eafa2cf7ea84eb513c,PASS,
SITE-001899,street_fill,https://inflatableimages.com,ed481d1f9ef8402ffe4aa71a73dd977c9d25ccc98a543a34e9d3874037a4255c,PASS,
SITE-001893,street_fill,https://polymetrecovery.com,5422e671b532dcd9972b8fe1c2a3551a3597a7d1419c0616220f9cd6471e37c9,PASS,
SITE-001882,street_fill,https://horsemenspride.com,45d5f60527ef70dd6e69f4f64cc4fc582cc43601594b8ab7ceaef16b54b7eea8,PASS,
SITE-001861,street_fill,https://beacongasket.com,744b7d747816982f1169354360bdb25b21342582e66b84672992e31e9eb60f35,PASS,
SITE-001860,street_fill,https://astromfg.com/contact-us,835af5489a346cc345da4073eac6e74d8b402b7590c9e167695d039ade6cd655,PASS,

AUDIT SUMMARY
{
  "accepted_street_fills": 24,
  "address_evidence_rows": 26,
  "audited": 26,
  "audited_street_fills": 24,
  "audited_note_flags": 2,
  "errors": 0
}
