Adversarial completion review. Lane L2 Ohio streets round2, branch agent/codex/oh-street-address-2. End VERDICT: APPROVE/REFUTE with demonstrated defects; no mutations or merge. Scope:20 existing active PIC18 A/B site street fills,20 own_site/address/supports_A evidence, unchanged record tiersA12/B8. Only street_address/sources columns change; no entities/IDs created except address evidence, no county/county_source/ZIP/status/tier/registry/ring/qualifier changes.

Frozen frame448 eligible prior-PR134-held active PIC18 A/B sites with operator website. Worked first60 immutable IDs, source yields60 site IDs exactly;20VERIFIED/40STILL_UNCERTAIN;388frame rows explicitly unworked. PriorOH134 fills excluded by held-ID membership; PA separate/merged. Main-only Ohio street count143/1883→163/1883 (7.59→8.66%); prospective combined with143pendingOH134 disjoint fills306/1883, never claimed already merged. EVD152000–152447 sparse frame-position allocation; accepted152002–152053. Controller06:30 continuation and original L2 application delegation.

Sources:128attempts=104fetched+24unavailable;26sites rawaddressblocks,20admitted. Own host-bound raw HTML via curl browserUA; redirects outside held operator host rejected, personal contacts/fullHTML not retained. Address-only quote exact word order; quote-to-street/city/ZIP/held-host/digest binding asserted. Five research fetches/operator +sixth freshaudit. Other pages fail/unknown→HOLD, no absence inference. Samecity multipleaddresses/ZIPs, recordedZIP or notedstreetconflicts, mailing-only contexts→HOLD. No paid/private/CRM sources.

Ground truth: check.py PASS20fills onlystreet/sources, same secondbuild bytes; pre-existing street and foreign evidence-shard collision reject BEFORE canonical writes. Three literal LIVE calibration addresses pass before scaling:Chardon373Washington;Freeman1101MooreAvon;ShinEtsu1150DamarAkron, plus wrongcity/PObox/phoneprefix mutation fixtures. Full accepted-fill census20/20 freshly refetched,0errors (population<30). validate.py0errors; no scripts/ changes. mainbdb8b98 merged viaf9a96a9, checksrePASS; no foreign data changes in diff. PA README-only note permitted explicitly by controller because PA147 merged before862f67a approval documentation landed; noPA data/code rides this PR.

Potential failures: wrongoperator/locationfooter, mailing-vsphysical, unparsed note street, false normalizedstreetagreement, weak geography, hidden record loss fromrebase, incomplete IDpreflight, applybeforefailure, extractor's numericprefix, underreturnedsource counts. Challenge actual evidence, not hypotheticalquota ofbugs.

Commands (from a clean review checkout of branch; mutating apply only in temp):
python3 tasks/oh-street-address-2-2026-11-06/check.py
python3 scripts/validate.py
python3 tasks/oh-street-address-2-2026-11-06/audit.py
python3 tasks/oh-street-address-2-2026-11-06/fetch.py --known
Full448 input frame.csv and sourceattempts page_checks.csv in taskfolder. Below all code, selected60 compactinputs,20evidence,60verdicts,20audit. Inspect fullnotes inframe ifneeded; compactinput preserves named street leads.

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
 suffix=r'(?:Street|St\.?|Road|Rd\.?|Drive|Dr\.?|Avenue|Ave\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Parkway|Pkwy\.?|Place|Pl\.?|Way|Court|Ct\.?|Route\s+\d+)'
 pattern=r'\b(\d{1,6}\s+(?:(?!\d+\b)[A-Za-z0-9.#/-]+\s+){0,8}?'+suffix+r')[, •|]*\s*'+re.escape(city)+r'\s*[, •|]*\s*(?:OH|Ohio)\s*[, •|]*\s*(\d{5}(?:-\d{4})?)\b'
 text=' '.join(text.split())
 return [(m[1].strip(),m[2],m[0]) for m in re.finditer(pattern,text,re.I)]
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
      pos=' '.join(text.split()).find(quote);context=' '.join(text.split())[max(0,pos-80):pos+len(quote)]
      posture='mailing-only context' if re.search(r'(?i)mailing\s+address|postal\s+address',context) else ''
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
 aliases={'STREET':'ST','ROAD':'RD','AVENUE':'AVE','DRIVE':'DR','COURT':'CT','PARKWAY':'PKWY','BOULEVARD':'BLVD','PLACE':'PL','WEST':'W','EAST':'E','NORTH':'N','SOUTH':'S'}
 return ' '.join(aliases.get(t,t) for t in re.findall('[A-Z0-9]+',v.upper()))
def note_streets(s):
 out=[x[0] for x in extract(s['notes'],s['city'])]
 m=re.search(r'(?i)\bstreet(?:\s*\([^)]*\))?:\s*(.+)',s['notes'])
 if m:
  out.append(re.split(r'\.\s+(?=PASS|BAND|CERT|Ring|INTEGRATION|Parcel|Re-pointed|NAICS|Source|\[)',m[1])[0].rstrip('. '))
 out+=re.findall(r'(?i)(?:Address[^:]{0,120}:|at)\s*(\d+\s+[^,;()]+),\s*'+re.escape(s['city']),s['notes'])
 return out
def plan():
 frame=read(TASK/'frame.csv');selected=[r for r in frame if r['selected']=='yes'];checks=read(TASK/'rawchecks.csv')
 assert len(frame)==448 and len({s['site_id'] for s in frame})==448
 assert len(selected)==60 and len({s['reserved_evidence_id'] for s in frame})==448
 assert {r['site_id'] for r in checks}=={s['site_id'] for s in selected},'source yield mismatch'
 verdicts=[];ev=[]
 for s in selected:
  rows=[r for r in checks if r['site_id']==s['site_id'] and r['street_address']];why=[]
  if not rows:why.append('need own-page physical street block at recorded city; no admissible block fetched')
  if any(r['posture'] for r in rows):why.append('mailing-only or ambiguous address context')
  host=lambda u:(urlparse(u if '://' in u else 'https://'+u).hostname or '').removeprefix('www.')
  for r in rows:
   assert host(r['url'])==host(s['website']),'witness leaves held operator host'
   assert re.fullmatch('[0-9a-f]{64}',r['sha256']),'missing page digest'
   assert any(key(a)==key(r['street_address']) and z==r['source_zip'] for a,z,q in extract(r['quote'],s['city'])),'quote/field binding failure'
  if len({key(r['street_address']) for r in rows})>1:why.append('own-page street blocks disagree')
  if len({r['source_zip'][:5] for r in rows})>1:why.append('own-page ZIPs disagree')
  if any(s['zip'] and s['zip'][:5]!=r['source_zip'][:5] for r in rows):why.append('own-page ZIP conflicts with current site ZIP')
  if rows and any(key(n)!=key(rows[0]['street_address']) for n in note_streets(s)):why.append('notes address conflicts; dated adjudication needed')
  if any(key(r['street_address']).startswith(('PO BOX','P O BOX')) or not re.match(r'^\d+\s+[A-Za-z]',r['street_address']) for r in rows):why.append('non-physical or ambiguous street')
  v=dict(site_id=s['site_id'],verdict='STILL_UNCERTAIN' if why else 'VERIFIED',street_address=rows[0]['street_address'] if rows else '',evidence_id='' if why else s['reserved_evidence_id'],reason='; '.join(why))
  verdicts.append(v)
  if not why:
   r=rows[0];ev.append(dict(evidence_id=s['reserved_evidence_id'],record_table='sites',record_id=s['site_id'],claim_type='address',
       claim_detail=f"street_address {r['street_address']}, {s['city']}, OH; own-page ZIP {r['source_zip']}",
       source_class='own_site',source_ref=r['url'],observed_date=DATE,tier_effect='supports_A',created_by='atlas-L2-oh-address-2',
       notes=f"Raw checked {DATE}; SHA-256 {r['sha256']}; quote: {r['quote']}. County, county_source, ZIP and record tier unchanged."))
 assert len(verdicts)==len({v['site_id'] for v in verdicts})==60
 return selected,verdicts,ev
def run(apply=False):
 selected,verdicts,ev=plan();sites=read(ROOT/'data/sites_OH.csv');byid={s['site_id']:s for s in sites};frozen={s['site_id']:s for s in selected};eb={e['record_id']:e for e in ev}
 # Whole-namespace preflight, including foreign shards. No canonical write happens before every invariant passes.
 existing={}
 for p in (ROOT/'data').glob('evidence_*.csv'):
  for r in read(p):
   if r['evidence_id'] in {e['evidence_id'] for e in ev}:existing.setdefault(r['evidence_id'],[]).append((p.name,r))
 new=[]
 for v in verdicts:
  if v['verdict']!='VERIFIED':continue
  s=byid[v['site_id']];old=frozen[s['site_id']];e=eb[s['site_id']]
  for field in ('org_id','city','state','county','county_source','zip','verification_tier','operating_status','notes'):assert s[field]==old[field],(s['site_id'],field,'main changed')
  assert s['operating_status']=='active' and not old['street_address']
  assert s['street_address'] in ('',v['street_address']),'pre-existing street conflict'
  have=existing.get(e['evidence_id'],[])
  assert not have or have==[('evidence_sites_OH.csv',e)],'global evidence ID collision'
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
  if new:append_sorted(ROOT/'data/evidence_sites_OH.csv',new,'evidence_id')
  write(ROOT/'data/sites_OH.csv',sites)
 write(TASK/'verdicts.csv',verdicts);write(TASK/'holds.csv',[r for r in verdicts if r['verdict']!='VERIFIED'])
 if ev:write(TASK/'evidence.csv',ev)
 active=[r for r in sites if r['operating_status']=='active']
 actual=sum(bool(s['street_address']) for s in active)
 before=actual-len(ev) if all(byid[e['record_id']]['street_address'] for e in ev) else actual
 summary=dict(eligible_sites=448,worked=60,unworked=388,fills=len(ev),holds=60-len(ev),active_ohio_sites=len(active),before_streets=before,after_streets=before+len(ev))
 (TASK/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
if __name__=='__main__':run('--apply' in sys.argv)

FILE check.py
"""Check real fill boundary/replay and fail-before-write on street and cross-shard ID collisions."""
import contextlib,hashlib,io,shutil,tempfile
from pathlib import Path
import build
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 root=build.ROOT;selected,verdicts,ev=build.plan()
 assert len(ev)==20,'frozen acceptance count changed; inspect before revising'
 with tempfile.TemporaryDirectory() as tmp:
  build.ROOT=Path(tmp);(build.ROOT/'data').mkdir()
  for p in (root/'data').glob('evidence_*.csv'):shutil.copyfile(p,build.ROOT/'data'/p.name)
  shutil.copyfile(root/'data/sites_OH.csv',build.ROOT/'data/sites_OH.csv')
  frozen={r['site_id']:r for r in selected};before=build.read(build.ROOT/'data/sites_OH.csv')
  for r in before:
   if r['site_id'] in frozen:
    old=frozen[r['site_id']]
    for k in r:r[k]=old[k]
  build.write(build.ROOT/'data/sites_OH.csv',before)
  p=build.ROOT/'data/evidence_sites_OH.csv'
  build.write(p,[r for r in build.read(p) if r['created_by']!='atlas-L2-oh-address-2'])
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  after=build.read(build.ROOT/'data/sites_OH.csv');changed=0
  assert len(before)==len(after)
  for a,b in zip(before,after):
   fields={k for k in a if a[k]!=b[k]}
   assert fields <= {'street_address','sources'},(a['site_id'],fields)
   if fields:
    changed+=1;assert not a['street_address'] and b['street_address'] and a['operating_status']=='active'
  assert changed==20
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
  foreign=build.ROOT/'data/evidence_sites_ZZ.csv';build.write(foreign,[ev[0]])
  paths=list((build.ROOT/'data').glob('*.csv'));hashes={p.name:digest(p) for p in paths}
  try:
   with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  except AssertionError:pass
  else:raise AssertionError('foreign-shard evidence collision accepted')
  assert hashes=={p.name:digest(p) for p in paths},'wrote before global collision refusal'
 build.ROOT=root
 print('PASS 20 fills; street/sources only; byte-idempotent; street and foreign-ID mutations rejected before canonical writes')
if __name__=='__main__':main()

FILE audit.py
"""Fresh raw-page census of all accepted fills (20 < the requested 30-row sample)."""
import concurrent.futures,json
from build import TASK,read
from fetch import fetch,write,extract
evidence=read(TASK/'evidence.csv');sites={r['site_id']:r for r in read(TASK/'frame.csv')}
def check(e):
 error='';sha=''
 try:
  text,links,sha=fetch(e['source_ref'])
  quote=e['notes'].split('; quote: ')[1].removesuffix('. County, county_source, ZIP and record tier unchanged.')
  assert ' '.join(quote.split()) in ' '.join(text.split()),'raw quote absent on fresh fetch'
  assert extract(quote,sites[e['record_id']]['city']),'quote not a city-specific physical address block'
 except Exception as ex:error=str(ex)
 return dict(site_id=e['record_id'],source_ref=e['source_ref'],sha256=sha,result='PASS' if not error else 'FAIL',error=error)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(check,evidence))
write(TASK/'audit.csv',out)
summary=dict(accepted_fills=len(evidence),audited=len(out),errors=sum(bool(r['error']) for r in out))
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert len(out)==20 and summary['errors']==0,out

COMPACT INPUTS site_id|operator site|city|existingZIP|county|tier|website|parsedstreetleads
SITE-000002 | Lubrizol — Wickliffe HQ | Wickliffe | 44077 | Lake | B | https://www.lubrizol.com | ['155 FREEDOM ROAD', '155 FREEDOM ROAD']
SITE-000004 | Parker-Hannifin — Cleveland HQ | Cleveland | 44124 | Cuyahoga | B | https://www.parker.com | []
SITE-000005 | Day-Glo — Cleveland HQ | Cleveland |  | Cuyahoga | B | https://www.dayglo.com | []
SITE-000006 | Vibrantz (Chromaflo legacy) — Ashtabula | Ashtabula |  | Ashtabula | B | https://www.vibrantz.com | []
SITE-000007 | Struktol — Stow HQ | Stow | 44223 | Summit | B | https://www.struktol.com | ['201 E. STEELS CORNERS ROAD', '201 E. STEELS CORNERS ROAD']
SITE-000008 | Myers Industries — Akron HQ | Akron | 44301 | Summit | B | https://www.myersindustries.com | ['1293 S MAIN ST', '1293 S MAIN ST']
SITE-000009 | GEON - Westlake HQ | Westlake | 44131 | Cuyahoga | B | https://www.geon.com | ['6100 OAK TREE BLVD', '6100 OAK TREE BLVD']
SITE-000010 | Bridgestone Americas Technology Center - Akron | Akron | 44317 | Summit | B | https://bridgestoneamericas.com | ['1200 FIRESTONE PARKWAY', '1200 FIRESTONE PARKWAY']
SITE-000014 | Diamond America — Akron | Akron |  | Summit | A | https://daextrusion.com | []
SITE-000017 | Ace Rubber Products — Akron | Akron |  | Summit | A | https://theacerubber.com | ['1200 Devalera St', '1200 Devalera St']
SITE-000035 | Saint-Gobain Performance Plastics — Akron | Akron | 44305 | Summit | A | https://saint-gobain.com | ['2664 GILCHRIST RD', '2664 GILCHRIST RD']
SITE-000037 | HKB Enterprises, Inc. — Akron | Akron |  | Summit | A | https://hkbenterprises.com | []
SITE-000038 | Pioneer Plastics Corp. — Akron | Akron | 44312 | Summit | A | https://pioneerplasticscorp.com | ['3330 MASSILLON ROAD', '3330 Massillon Rd', '3330 MASSILLON ROAD']
SITE-000039 | Landmark Plastic Corp. — Akron | Akron | 44306 | Summit | A | https://landmarkplastic.com | ['1331 KELLY AVE', '1331 KELLY AVE']
SITE-000043 | Alterra Energy — Akron | Akron | 44306 | Summit | B | https://alterra360.com/ | ['1200 EAST WATERLOO ROAD', '1200 EAST WATERLOO ROAD', '1200 E Waterloo Rd']
SITE-000044 | APV Engineered Coatings — Akron | Akron |  | Summit | A | https://apvcoatings.com | ['1390 Firestone Parkway']
SITE-000047 | Smithers — Akron | Akron |  | Summit | B | https://smithers.com | ['425 West Market Street', '425 West Market Street']
SITE-000048 | Akrochem Corp. — Akron | Akron | 44333 | Summit | B | https://akrochem.com | ['3770 EMBASSY PARKWAY', '3770 Embassy Parkway', '3770 EMBASSY PARKWAY']
SITE-000050 | Synthomer, Inc. — Mogadore | Mogadore | 44260 | Portage | A | https://synthomer.com | ['165 S. Cleveland Ave']
SITE-000051 | Continental ContiTech USA — Fairlawn | Fairlawn |  | Summit | B | https://continental-industry.com | []
SITE-000052 | Harwick Standard Distribution Corp. — Akron | Akron | 44305 | Summit | A | https://harwickstandard.com | ['60 S. SEIBERLING ST.', '60 S. Seiberling Street', '60 S. SEIBERLING ST.']
SITE-000056 | CF Extrusion Technologies — Cuyahoga Falls | Cuyahoga Falls |  | Summit | A | https://cfextrusion.com | []
SITE-000058 | Steelastic — Cuyahoga Falls | Cuyahoga Falls |  | Summit | A | https://steelastic.com | []
SITE-000060 | Esterle Mold & Machine Co., Inc. — Stow | Stow |  | Summit | B | https://esterle.com | ['1539 Commerce Drive', '1539 Commerce Drive']
SITE-000061 | Ferriot, Inc. — Akron | Akron | 44312 | Summit | A | https://ferriot.com | ['2685 MOGADORE ROAD', '2685 MOGADORE ROAD']
SITE-000070 | Plastic Materials, Inc. — Macedonia | Macedonia | 44056 | Summit | B | https://plasticmaterialsinc.com | ['775 E HIGHLAND RD', '775 E HIGHLAND RD']
SITE-000071 | Miles Rubber & Packing — Twinsburg | Twinsburg |  | Summit | A | https://milesrubber.com | ['9020 Dutton Dr']
SITE-000072 | Cima Plastics Group — Twinsburg | Twinsburg |  | Summit | B | https://cimaplastics.com | []
SITE-000074 | MRP Solutions — Twinsburg | Twinsburg | 44087 | Summit | A | https://mrpsolutions.com/ | ['2222 HIGHLAND RD', '2222 Highland Road', '2222 HIGHLAND RD']
SITE-000075 | Industrial Mold & Machine — Twinsburg | Twinsburg | 44087 | Summit | B | https://industrialmold.com | ['2057 EAST AURORA RD', '2057 EAST AURORA RD']
SITE-000076 | Crown Composites Tooling — Twinsburg | Twinsburg |  | Summit | A | https://crownmold.net | []
SITE-000077 | Mantaline Corp. — Twinsburg | Twinsburg |  | Summit | B | https://mantaline.com | []
SITE-000078 | Giesecke+Devrient America — Twinsburg | Twinsburg |  | Summit | B | https://gi-de.com | []
SITE-000079 | General Plastex, Inc. — Barberton | Barberton | 44203 | Summit | A | https://generalplastex.com | ['35 STUVER PL.', '235 Stuver Place', '35 STUVER PL.']
SITE-000081 | Novex, Inc. — Barberton | Barberton | 44203 | Summit | B | https://novexinc.com | ['74 ROBINSON AVE', '74 ROBINSON AVE']
SITE-000082 | Merryweather Foam, Inc. — Barberton | Barberton | 44203 | Summit | A | https://merryweather.com | ['11 BROWN ST', '11 Brown St.', '11 BROWN ST', '11 Brown St']
SITE-000083 | Michael Day Enterprises, LLC — Norton | Norton |  | Summit | A | https://mdayinc.com | ['3960 Summit Rd']
SITE-000085 | Ohio Precision Molding — Barberton | Barberton | 44203 | Summit | B | https://ohioprecisionmolding.com | ['122 E. Tuscarawas Ave']
SITE-000086 | Rubber Associates, Inc. — Barberton | Barberton | 44203 | Summit | A | https://rubberassociates.com | ['1522 W TURKEYFOOT LAKE RD', '1522 W. Turkeyfoot Lake Road', '1522 W TURKEYFOOT LAKE RD']
SITE-000087 | Rainbow Rubber Extrusions — Barberton | Barberton |  | Summit | A | https://rainbowrubber.com | ['1580 West Turkeyfoot Lake Rd.']
SITE-000092 | Ohio Rubber Group — Hudson | Hudson | 44236 | Summit | B | https://ohiorubbergroup.org | []
SITE-000101 | Polymerics, Inc. — Cuyahoga Falls | Cuyahoga Falls | 44221 | Summit | A | http://www.polymericsinc.com | ['2828 2ND ST', '2828 Second Street', '2828 2ND ST']
SITE-000105 | PharoPLAST — Cleveland | Cleveland |  | Cuyahoga | A | https://www.pharoplast.com/ | ['1643 Eddy Rd']
SITE-000106 | T&M Plastics Co. — Cleveland | Cleveland |  | Cuyahoga | B | http://www.tmplasticsusa.com | ['1249 W 78TH ST', '1249 W 78TH ST']
SITE-000107 | HP Manufacturing — Cleveland | Cleveland | 44115 | Cuyahoga | A | https://hpmanufacturing.com | ['3705 CARNEGIE AVE.', '3705 Carnegie Avenue', '3705 CARNEGIE AVE.']
SITE-000109 | Team Plastic — Cleveland | Cleveland | 44111 | Cuyahoga | A | https://teamplasticsinc.com/ | ['3901 W 150th St', '3901 W 150th St']
SITE-000111 | Trico Machine Products — Cleveland | Bedford Heights |  | Cuyahoga | B | https://tricomachine.com | []
SITE-000112 | Custom Rubber Corp. — Cleveland | Cleveland | 44114 | Cuyahoga | A | https://customrubbercorp.com | ['3710 PAYNE AVE', '3710 PAYNE AVE']
SITE-000114 | Cuyahoga Plastics — Euclid | Euclid | 44132 | Cuyahoga | A | http://www.cuyahogaplastics.com/ | ['1265 BABBITT RD.', '1265 BABBITT RD.']
SITE-000115 | AMD Plastics — Euclid | Euclid |  | Cuyahoga | A | https://www.amdplastics.com/ | []
SITE-000116 | North American Plastics-Chem — Euclid | Euclid |  | Cuyahoga | B | https://noramcobag.com | ['1400 E. 222nd St.']
SITE-000117 | GSH Industries — Strongsville | Strongsville | 44149 | Cuyahoga | A | https://gshindustries.com | ['15242 FOLTZ INDUSTRIAL PKWY', '15242 Foltz Industrial Pkwy', '15242 FOLTZ INDUSTRIAL PKWY', '15242 Foltz Industrial Pkwy']
SITE-000123 | Prime Conduit — Beachwood | Beachwood |  | Cuyahoga | B | https://primeconduit.com | []
SITE-000125 | Cardinal Products — North Royalton | North Royalton |  | Cuyahoga | A | https://cpipp.com/ | []
SITE-000129 | Peak Nano — Valley View | Valley View |  | Cuyahoga | B | https://www.peaknano.com | []
SITE-000133 | Oatey — Cleveland | Cleveland | 44135 | Cuyahoga | A | https://oatey.com | ['4700 W. 160TH ST.', '4700 West 160th St.', '4700 W. 160TH ST.', '4700 West 160th St.']
SITE-000134 | Novagard Solutions — Cleveland | Cleveland | 44114 | Cuyahoga | A | https://novagard.com | ['2720 E 79TH ST', '5109 Hamilton Ave', '2720 E 79TH ST']
SITE-000136 | Roto Polymers — Warrensville Heights | Warrensville Heights |  | Cuyahoga | A | https://rotopolymers.com | ['26210 Emery Road']
SITE-000145 | Plastics Machinery Group — Bedford Heights | Bedford Heights |  | Cuyahoga | A | https://plasticsmg.com | ['5455 Perkins Road']
SITE-000150 | NSL Analytical Services — Warrensville Heights | Warrensville Heights | 44128 | Cuyahoga | B | http://nslanalytical.com/ | ['7650 HUB PKWY', '7650 HUB PKWY']
FILE evidence.csv
evidence_id,record_table,record_id,claim_type,claim_detail,source_class,source_ref,observed_date,tier_effect,created_by,notes
EVD-152002,sites,SITE-000005,address,"street_address 4515 St. Clair Avenue, Cleveland, OH; own-page ZIP 44103",own_site,https://www.dayglo.com/contact-us/,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 16617eb93bcc5bac01c4d5352a16d52640d788a47edd8906291c0473dd018394; quote: 4515 St. Clair Avenue Cleveland, OH 44103. County, county_source, ZIP and record tier unchanged."
EVD-152005,sites,SITE-000008,address,"street_address 1293 South Main Street, Akron, OH; own-page ZIP 44301",own_site,https://www.myersindustries.com/contact-us/,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 735c1b8c5eb63d756e9f806ccbfbc99bbaf22881031dfd1a4d024d12a7f03582; quote: 1293 South Main Street Akron, Ohio 44301. County, county_source, ZIP and record tier unchanged."
EVD-152009,sites,SITE-000017,address,"street_address 1200 Devalera St, Akron, OH; own-page ZIP 44310",own_site,https://theacerubber.com,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 adb5d12c62a0caf491866e51dae6eca8a713b6f0e9cf8d3eb4d81e699dc31a6b; quote: 1200 Devalera St, Akron, Ohio 44310. County, county_source, ZIP and record tier unchanged."
EVD-152012,sites,SITE-000038,address,"street_address 3330 Massillon Road, Akron, OH; own-page ZIP 44312",own_site,https://pioneerplasticscorp.com/contact,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 7c9e6a46cea01cf0c0eddd892573a6b90f66cbcba368b87f939b27894949456f; quote: 3330 Massillon Road Akron, OH 44312. County, county_source, ZIP and record tier unchanged."
EVD-152013,sites,SITE-000039,address,"street_address 1331 Kelly Ave., Akron, OH; own-page ZIP 44306",own_site,https://landmarkplastic.com,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 e356557a50a2314de9bc1f21c7eabbf97afe142392d77eb74491091d8928beb4; quote: 1331 Kelly Ave. Akron, Ohio 44306. County, county_source, ZIP and record tier unchanged."
EVD-152023,sites,SITE-000060,address,"street_address 1539 Commerce Drive, Stow, OH; own-page ZIP 44224",own_site,https://esterle.com,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 ae6376d22c18958a0b7bcec5d105970cf75ec825c6dc213e21d33bb5a064b4fe; quote: 1539 Commerce Drive, Stow, OH 44224. County, county_source, ZIP and record tier unchanged."
EVD-152026,sites,SITE-000071,address,"street_address 9020 Dutton Drive, Twinsburg, OH; own-page ZIP 44087",own_site,https://milesrubber.com/contact-us,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 b2b4c6be2e931f738c7292ec6afd7ac79c2682081ead12931ada488043bda7c4; quote: 9020 Dutton Drive, Twinsburg, Ohio 44087. County, county_source, ZIP and record tier unchanged."
EVD-152027,sites,SITE-000072,address,"street_address 2146 Enterprise Parkway, Twinsburg, OH; own-page ZIP 44087",own_site,https://cimaplastics.com,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 7db45d057caa82c8f77822bbb7049a5d378f712e4b06e979f25024ac69d089b8; quote: 2146 Enterprise Parkway Twinsburg, OH 44087. County, county_source, ZIP and record tier unchanged."
EVD-152028,sites,SITE-000074,address,"street_address 2222 Highland Road, Twinsburg, OH; own-page ZIP 44087",own_site,https://mrpsolutions.com/contact-us,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 e3841b01af8b0270df49b4506dfca511810440aaf930cf61a1bf62f46bb7322e; quote: 2222 Highland Road Twinsburg, OH 44087. County, county_source, ZIP and record tier unchanged."
EVD-152029,sites,SITE-000075,address,"street_address 2057 E. Aurora Rd., Twinsburg, OH; own-page ZIP 44087",own_site,https://industrialmold.com,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 1afcaef402c1d2016308fe0384d1b8cfd9166c8916b8e690ff58e0005a136517; quote: 2057 E. Aurora Rd. Twinsburg, OH 44087. County, county_source, ZIP and record tier unchanged."
EVD-152034,sites,SITE-000081,address,"street_address 74 Robinson Ave, Barberton, OH; own-page ZIP 44203",own_site,https://novexinc.com,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 7bc4297a0c5c609375b58d3ea346488792645551ba187c02ca1078abde6fe1d5; quote: 74 Robinson Ave Barberton, OH 44203. County, county_source, ZIP and record tier unchanged."
EVD-152035,sites,SITE-000082,address,"street_address 11 Brown St., Barberton, OH; own-page ZIP 44203",own_site,https://merryweather.com,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 fcedc4591a36db0d6d120c84ba2ff0cfa047fa95c9fb1a376bccaba1afd25499; quote: 11 Brown St. Barberton , OH 44203. County, county_source, ZIP and record tier unchanged."
EVD-152038,sites,SITE-000086,address,"street_address 1522 W. Turkeyfoot Lake Road, Barberton, OH; own-page ZIP 44203",own_site,https://rubberassociates.com,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 24bad599f084e6903c3601bee6feef918772db4ea09468b3e9e4226cf07bb526; quote: 1522 W. Turkeyfoot Lake Road Barberton, OH 44203. County, county_source, ZIP and record tier unchanged."
EVD-152039,sites,SITE-000087,address,"street_address 1580 West Turkeyfoot Lake Rd., Barberton, OH; own-page ZIP 44203",own_site,https://rainbowrubber.com,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 d805c9453dc6379228b7dfbe51c5a67974ae7b65f3de6cfbfa3e3043e9f67a15; quote: 1580 West Turkeyfoot Lake Rd. Barberton, OH 44203. County, county_source, ZIP and record tier unchanged."
EVD-152044,sites,SITE-000107,address,"street_address 3705 Carnegie Avenue, Cleveland, OH; own-page ZIP 44115",own_site,https://hpmanufacturing.com,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 6c0d55d62c1d9660f650e6cc8faab3cc0169875ebfdbcca3dd2b8678978f276f; quote: 3705 Carnegie Avenue Cleveland, Ohio 44115. County, county_source, ZIP and record tier unchanged."
EVD-152045,sites,SITE-000109,address,"street_address 3901 W 150th St, Cleveland, OH; own-page ZIP 44111",own_site,https://teamplasticsinc.com/,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 27d1bf5ac80a7cb1c16375a7c4d7e5ac2ad3e67c0f1186e1d75ead642c93ff93; quote: 3901 W 150th St, Cleveland, OH 44111. County, county_source, ZIP and record tier unchanged."
EVD-152046,sites,SITE-000111,address,"street_address 5081 Corbin Drive, Bedford Heights, OH; own-page ZIP 44128",own_site,https://tricomachine.com,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 26905a209d3a6ae77ad4dc57bc0f7d2ee64b065e34cb147094fbc4f9ba1fcdc4; quote: 5081 Corbin Drive Bedford Heights, OH 44128. County, county_source, ZIP and record tier unchanged."
EVD-152050,sites,SITE-000116,address,"street_address 1400 E. 222nd. St., Euclid, OH; own-page ZIP 44117",own_site,https://noramcobag.com/contact-us/,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 b7e7a425b250c09f18751953393a6c9204cf4d0b8ee6ee1230ba370c1d83f932; quote: 1400 E. 222nd. St. Euclid, OH 44117. County, county_source, ZIP and record tier unchanged."
EVD-152051,sites,SITE-000117,address,"street_address 15242 Foltz Industrial Pkwy, Strongsville, OH; own-page ZIP 44149",own_site,https://gshindustries.com,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 37bceacbf151016f1df887691ac92805d35b96a2efac459b936378907c332877; quote: 15242 Foltz Industrial Pkwy, Strongsville, Ohio 44149. County, county_source, ZIP and record tier unchanged."
EVD-152053,sites,SITE-000125,address,"street_address 11929 Abbey Rd, North Royalton, OH; own-page ZIP 44133",own_site,https://cpipp.com/,2026-11-06,supports_A,atlas-L2-oh-address-2,"Raw checked 2026-11-06; SHA-256 7c7cfa47ab57aa4639dbbb1533ae29da8f7a859f967a25ab28a817882e4ea87f; quote: 11929 Abbey Rd, North Royalton, OH, 44133. County, county_source, ZIP and record tier unchanged."

FILE verdicts.csv
site_id,verdict,street_address,evidence_id,reason
SITE-000002,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000004,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000005,VERIFIED,4515 St. Clair Avenue,EVD-152002,
SITE-000006,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000007,STILL_UNCERTAIN,201 East Steels Corners Road,,own-page street blocks disagree; own-page ZIP conflicts with current site ZIP
SITE-000008,VERIFIED,1293 South Main Street,EVD-152005,
SITE-000009,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000010,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000014,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000017,VERIFIED,1200 Devalera St,EVD-152009,
SITE-000035,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000037,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000038,VERIFIED,3330 Massillon Road,EVD-152012,
SITE-000039,VERIFIED,1331 Kelly Ave.,EVD-152013,
SITE-000043,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000044,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000047,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000048,STILL_UNCERTAIN,3770 Embassy Parkway,,own-page street blocks disagree; own-page ZIPs disagree; own-page ZIP conflicts with current site ZIP
SITE-000050,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000051,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000052,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000056,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000058,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000060,VERIFIED,1539 Commerce Drive,EVD-152023,
SITE-000061,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000070,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000071,VERIFIED,9020 Dutton Drive,EVD-152026,
SITE-000072,VERIFIED,2146 Enterprise Parkway,EVD-152027,
SITE-000074,VERIFIED,2222 Highland Road,EVD-152028,
SITE-000075,VERIFIED,2057 E. Aurora Rd.,EVD-152029,
SITE-000076,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000077,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000078,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000079,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000081,VERIFIED,74 Robinson Ave,EVD-152034,
SITE-000082,VERIFIED,11 Brown St.,EVD-152035,
SITE-000083,STILL_UNCERTAIN,3960 Summit Rd,,own-page ZIPs disagree
SITE-000085,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000086,VERIFIED,1522 W. Turkeyfoot Lake Road,EVD-152038,
SITE-000087,VERIFIED,1580 West Turkeyfoot Lake Rd.,EVD-152039,
SITE-000092,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000101,STILL_UNCERTAIN,2828 Second Street,,notes address conflicts; dated adjudication needed
SITE-000105,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000106,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000107,VERIFIED,3705 Carnegie Avenue,EVD-152044,
SITE-000109,VERIFIED,3901 W 150th St,EVD-152045,
SITE-000111,VERIFIED,5081 Corbin Drive,EVD-152046,
SITE-000112,STILL_UNCERTAIN,1274 East 55th Street,,own-page ZIP conflicts with current site ZIP; notes address conflicts; dated adjudication needed
SITE-000114,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000115,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000116,VERIFIED,1400 E. 222nd. St.,EVD-152050,
SITE-000117,VERIFIED,15242 Foltz Industrial Pkwy,EVD-152051,
SITE-000123,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000125,VERIFIED,11929 Abbey Rd,EVD-152053,
SITE-000129,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000133,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000134,STILL_UNCERTAIN,5109 Hamilton Ave,,notes address conflicts; dated adjudication needed
SITE-000136,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000145,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000150,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched

FILE audit.csv
site_id,source_ref,sha256,result,error
SITE-000005,https://www.dayglo.com/contact-us/,bc854408663dd11ff143b33d890c1976cd7b572d12c423076902d3f77646a7fa,PASS,
SITE-000008,https://www.myersindustries.com/contact-us/,735c1b8c5eb63d756e9f806ccbfbc99bbaf22881031dfd1a4d024d12a7f03582,PASS,
SITE-000017,https://theacerubber.com,adb5d12c62a0caf491866e51dae6eca8a713b6f0e9cf8d3eb4d81e699dc31a6b,PASS,
SITE-000038,https://pioneerplasticscorp.com/contact,7c9e6a46cea01cf0c0eddd892573a6b90f66cbcba368b87f939b27894949456f,PASS,
SITE-000039,https://landmarkplastic.com,e356557a50a2314de9bc1f21c7eabbf97afe142392d77eb74491091d8928beb4,PASS,
SITE-000060,https://esterle.com,6ff737214ab5d0b117fca04db9ab6d88990ec9dc2dbc834f49edcef5c1f834cc,PASS,
SITE-000071,https://milesrubber.com/contact-us,b2b4c6be2e931f738c7292ec6afd7ac79c2682081ead12931ada488043bda7c4,PASS,
SITE-000072,https://cimaplastics.com,7db45d057caa82c8f77822bbb7049a5d378f712e4b06e979f25024ac69d089b8,PASS,
SITE-000074,https://mrpsolutions.com/contact-us,e3841b01af8b0270df49b4506dfca511810440aaf930cf61a1bf62f46bb7322e,PASS,
SITE-000075,https://industrialmold.com,1afcaef402c1d2016308fe0384d1b8cfd9166c8916b8e690ff58e0005a136517,PASS,
SITE-000081,https://novexinc.com,7bc4297a0c5c609375b58d3ea346488792645551ba187c02ca1078abde6fe1d5,PASS,
SITE-000082,https://merryweather.com,fcedc4591a36db0d6d120c84ba2ff0cfa047fa95c9fb1a376bccaba1afd25499,PASS,
SITE-000086,https://rubberassociates.com,24bad599f084e6903c3601bee6feef918772db4ea09468b3e9e4226cf07bb526,PASS,
SITE-000087,https://rainbowrubber.com,202a95deea9562095715fb8e883623190cc66cd94a68e2688b3b7f6fe383aac5,PASS,
SITE-000107,https://hpmanufacturing.com,6c0d55d62c1d9660f650e6cc8faab3cc0169875ebfdbcca3dd2b8678978f276f,PASS,
SITE-000109,https://teamplasticsinc.com/,953ee1934649501db3b2b5e351998c35113158bb8a761eaa588c368cf8167bf5,PASS,
SITE-000111,https://tricomachine.com,26905a209d3a6ae77ad4dc57bc0f7d2ee64b065e34cb147094fbc4f9ba1fcdc4,PASS,
SITE-000116,https://noramcobag.com/contact-us/,b7e7a425b250c09f18751953393a6c9204cf4d0b8ee6ee1230ba370c1d83f932,PASS,
SITE-000117,https://gshindustries.com,37bceacbf151016f1df887691ac92805d35b96a2efac459b936378907c332877,PASS,
SITE-000125,https://cpipp.com/,7c7cfa47ab57aa4639dbbb1533ae29da8f7a859f967a25ab28a817882e4ea87f,PASS,

FILE summary.json
{
  "eligible_sites": 448,
  "worked": 60,
  "unworked": 388,
  "fills": 20,
  "holds": 40,
  "active_ohio_sites": 1883,
  "before_streets": 143,
  "after_streets": 163
}
