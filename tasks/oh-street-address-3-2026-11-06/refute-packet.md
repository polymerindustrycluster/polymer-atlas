Adversarial completion refute, L2 Ohio street round3, branch agent/codex/oh-street-address-3. Return VERDICT: APPROVE/REFUTE with actual demonstrated defects, no mutations or merge.
Frozen ORIGINAL448frame positions61–160 (IDs152060–152159) exactly next100 after prior156'sfirst60.100worked=38VERIFIED/62STILL_UNCERTAIN;288futureframe rows unworked. All100 were blank,activePIC18A/B with operatorwebsite on main8e8c71a beforefetch.38street/source-only edits,38append-only own_site/address/supports_A evidence; tiersA27/B11unchanged. No county/county_source/ZIP/status/tier/ring/registry/derived edits, no org/site creates/deletes/inclusionlog. Coverage286/1883→324/1883 (15.19→17.21%), excludes disjoint20pending156. Check currentmain if156merges; replayonmain recipe, not scope growth.
209rawpage attempts=186fetched+23unavailable; all100siteIDs accounted,54rawaddresssites38admitted. Missingcityblocks/multiple street/ZIPs/knownZIP/notes conflicts/mail-only/cross-host redirects held. Quote-to-field/city/ZIP/digest/held-host binding asserted. Street normalization only suffix/direction abbreviations. Ownpage address blocks only,no personal contacts/fullHTML retained. Five research pages/operator reserves sixth audit; inherited federal exception not used.
Named ground truth: live three known literal operator addresses before scaling (Chardon373Washington,Freeman1101MooreAvon,ShinEtsu1150DamarAkron),3/3; wrongcity/PObox/phoneprefix injections pass. check.py38fills,boundary,idempotence,preexistingstreet and foreign-shardEVD collisions rejectBEFOREcanonicalwrites. audit.py sortedsiteIDs Random20261106.sample(38,30),fresh30/30,0missingquotes/errors. validate.py0errors; no scripts/ changes; diffcheckPASS. Beforeapply immutable scope/rawchecks/backup/journal fixed. Latermain integration must preserve allkeys/evidence; The38outputs remain fixed except verified review findings. PriorPR156head9ef stillDRAFT,notbundled.
Potential failures: wrongoperatororlocationfooter, mailingvsphysical, sourcecountycontradiction, unparsednotesstreet, normalization falselyequates, URLredirectidentity, numericprefix pollution, globalID/rebase rowloss, applybeforefailure, underreturnedextractor, samplingcoverage.
Reproduce read-only temp checks:
python3 tasks/oh-street-address-3-2026-11-06/check.py
python3 scripts/validate.py
python3 tasks/oh-street-address-3-2026-11-06/audit.py
python3 tasks/oh-street-address-3-2026-11-06/fetch.py --known
Full448inputframe and rawchecks/page_checks/journal in taskfolder. Below allcode+100compactinputs+100verdicts+38witnesses+30audit. Evidence rows share source_class own_site, claim_type address,tier_effect supports_A,date2026-11-06,created_byatlas-L2-oh-address-3; compactwitnesses retain IDs/ref/detail/exactquote/digest. Read full original notes in frame.csv if source-adjudication unclear. Controller05:55/06:25 clerk route supersedes council-only order; two families required before readiness.

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
 assert len(selected)==100 and len({s['reserved_evidence_id'] for s in frame})==448
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
       source_class='own_site',source_ref=r['url'],observed_date=DATE,tier_effect='supports_A',created_by='atlas-L2-oh-address-3',
       notes=f"Raw checked {DATE}; SHA-256 {r['sha256']}; quote: {r['quote']}. County, county_source, ZIP and record tier unchanged."))
 assert len(verdicts)==len({v['site_id'] for v in verdicts})==100
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
 summary=dict(eligible_sites=448,prior_batch_sites=60,worked=100,unworked=288,fills=len(ev),holds=100-len(ev),active_ohio_sites=len(active),before_streets=before,after_streets=before+len(ev))
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
 assert len(ev)==38,'frozen acceptance count changed; inspect before revising'
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
  build.write(p,[r for r in build.read(p) if r['created_by']!='atlas-L2-oh-address-3'])
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  after=build.read(build.ROOT/'data/sites_OH.csv');changed=0
  assert len(before)==len(after)
  for a,b in zip(before,after):
   fields={k for k in a if a[k]!=b[k]}
   assert fields <= {'street_address','sources'},(a['site_id'],fields)
   if fields:
    changed+=1;assert not a['street_address'] and b['street_address'] and a['operating_status']=='active'
  assert changed==38
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
 print('PASS 38 fills; street/sources only; byte-idempotent; street and foreign-ID mutations rejected before canonical writes')
if __name__=='__main__':main()

FILE audit.py
"""Seeded 30-fill fresh raw-page audit, with a full census when fewer than30 accepted."""
import concurrent.futures,json,random
from build import TASK,read
from fetch import fetch,write,extract
evidence=read(TASK/'evidence.csv');sample=random.Random(20261106).sample(sorted(evidence,key=lambda e:e['record_id']),min(30,len(evidence)));sites={r['site_id']:r for r in read(TASK/'frame.csv')}
def check(e):
 error='';sha=''
 try:
  text,links,sha=fetch(e['source_ref'])
  quote=e['notes'].split('; quote: ')[1].removesuffix('. County, county_source, ZIP and record tier unchanged.')
  assert ' '.join(quote.split()) in ' '.join(text.split()),'raw quote absent on fresh fetch'
  assert extract(quote,sites[e['record_id']]['city']),'quote not a city-specific physical address block'
 except Exception as ex:error=str(ex)
 return dict(site_id=e['record_id'],source_ref=e['source_ref'],sha256=sha,result='PASS' if not error else 'FAIL',error=error)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(check,sample))
write(TASK/'audit.csv',out)
summary=dict(accepted_fills=len(evidence),audited=len(out),errors=sum(bool(r['error']) for r in out))
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert len(out)==min(30,len(evidence)) and summary['errors']==0,out

INPUT siteID|siteName|city|currentZIP|county|tier|heldWebsite|parsedNotesStreetLeads
SITE-000158|Cleveland State University — Cleveland|Cleveland|44114|Cuyahoga|A|https://www.csuohio.edu|['2151 EUCLID AVE', '2121 Euclid Avenue', '2151 EUCLID AVE']
SITE-000179|Graphic Arts Rubber — Cuyahoga Falls|Cuyahoga Falls|44223|Summit|A|https://www.graphicartsrubber.com/|['101 Ascot Parkway', '101 ASCOT PKY.']
SITE-000183|Kent Elastomer Products — Kent|Kent|44240|Portage|A|https://kentelastomer.com|['1500 ST. CLAIR AVE.', '1500 St. Clair Ave', '1500 ST. CLAIR AVE.', '1500 St. Clair Ave', '1500 St Clair Ave']
SITE-000186|Jet Rubber Company — Rootstown|Rootstown|44272|Portage|B|http://www.jetrubber.com/|['4457 TALLMADGE RD', '4457 Tallmadge Rd', '4457 TALLMADGE RD', '4457 Tallmadge Rd']
SITE-000189|Orazen Extruded Polymers — Aurora|Aurora||Portage|A|http://www.orazen.com/|[]
SITE-000192|Anyseals — Brecksville|Brecksville|44141|Cuyahoga|B|https://www.anyseals.com/|['10391 BRECKSVILLE RD', '10391 BRECKSVILLE RD']
SITE-000196|GBSA — Chardon|Chardon||Geauga|A|http://www.gbsa.com/|['112 Parker Court']
SITE-000198|Ohio Elastomers — Perry|Perry||Lake|B|https://ohioelastomers.com|[]
SITE-000199|Triangle Chemical — Mentor|Mentor||Lake|B|http://trianglechem.com/|['7027 Spinach Drive', '7027 Spinach Dr']
SITE-000201|Salem-Republic Rubber — Sebring|Sebring|44672|Mahoning|A|https://salem-republic.com|['475 W CALIFORNIA AVE', '475 West California Avenue', '475 W CALIFORNIA AVE']
SITE-000202|Qualiform — Wadsworth|Wadsworth|44281|Medina|A|https://qualiformrubbermolding.com|['350 STATE ST', '689 Weber Drive', '350 STATE ST']
SITE-000203|Goldsmith & Eggleton — Wadsworth|Wadsworth|44281|Medina|B|https://www.goldsmith-eggleton.com/|['300 1ST ST', '300 1ST ST', '300 1ST ST', '300 1ST ST', '300 1st St']
SITE-000204|Kenda American Technology Center — Green|Green|44720|Summit|B|https://www.kendatire.com/|[]
SITE-000206|Seaman Corporation — Wooster|Wooster||Wayne|A|https://www.seamancorp.com|['1000 Venture Boulevard']
SITE-000212|HEXPOL Compounding — Burton (Burton Rubber Processing)|Burton||Geauga|A|https://hexpolcompounding.com|['14330 Kinsman Rd']
SITE-000213|HEXPOL Compounding — Middlefield (Gold Key Processing)|Middlefield||Geauga|B|https://hexpolcompounding.com|['14910 MADISON RD']
SITE-000216|Bridgestone Americas - Akron (Advanced Tire Production Center)|Akron||Summit|B|https://bridgestoneamericas.com|[]
SITE-000217|Synthomer, Inc. - Akron (Akron Technology Center)|Akron|44305|Summit|A|https://synthomer.com|['2990 Gilchrist Rd']
SITE-000218|Synthomer, Inc. - Akron (Tech Way Drive)|Akron|44306|Summit|A|https://synthomer.com|['1380 Tech Way Dr']
SITE-000220|A.r.e. Accessories — Massillon|Massillon|44646|Stark|A|https://realtruck.com/|['400 NAVE ROAD SE']
SITE-000221|A-Roo Co. — Strongsville|Strongsville|44149|Cuyahoga|A|https://www.a-roo.com/|['22360 Royalton Road']
SITE-000222|ABC Plastics — Lodi|Lodi|44254|Medina|A|http://www.abcplasticslodi.com/|['140 West Drive', '140 West Drive']
SITE-000224|Additive Engineering Solutions — Akron|Akron|44305|Summit|A|https://additiveeng.com/|['990 Evans Ave']
SITE-000227|Advanced Poly-Packaging, Inc. — Akron|Akron|44306|Summit|A|https://www.advancedpoly.com/|['1331 Emmitt Road']
SITE-000241|American Foam Products — Painesville|Painesville|44077|Lake|A|https://www.americanfoamproducts.com/|['753 Liberty St']
SITE-000245|Apollo Plastics, Inc. — Mentor|Mentor|44060|Lake|A|https://apolloplastics.net/|['7555 Tyler Blvd Unit 11']
SITE-000247|Arc Rubber, Inc. — Geneva|Geneva|44041|Ashtabula|A|http://www.arcrubber.com/|['100 Water St']
SITE-000250|Associated Materials — Cuyahoga Falls|Cuyahoga Falls|44223|Summit|A|https://www.associatedmaterials.com/|['3773 STATE ROAD']
SITE-000263|Blade-tech Industries — Streetsboro|Streetsboro|44241|Portage|A|https://blade-tech.com/|['10125 Wellman Road']
SITE-000264|Blair Rubber — Seville|Seville|44273|Medina|A|https://blairrubber.com/|['5020 Enterprise Parkway']
SITE-000271|Buckeye Packaging Co., Inc. — Alliance|Alliance|44601|Stark|A|https://www.buckeyepackaging.com/|['12223 Marlboro Ave NE']
SITE-000272|Buckeye Rubber & Packing Co. — Beachwood|Beachwood|44122|Cuyahoga|B|https://buckeyerubber.com/|['23940 Mercantile Rd.. county UNVERIFIED — Grok county_check=TRUE']
SITE-000276|CANTEX — Aurora|Aurora|44202|Portage|A|https://www.cantexinc.com/|['11444 Chamberlain Road #1. county UNVERIFIED — Grok county_check=TRUE']
SITE-000281|Cast Nylons 4366|Willoughby|44094|Lake|B|https://castnylon.com/|['4366 Hamann Parkway']
SITE-000285|CG Thermal LLC — Twinsburg|Twinsburg|44087|Summit|A|https://cgthermal.com/|['1470 Enterprise Pkwy']
SITE-000286|Chapin Custom Molding — Elyria|Elyria|44035|Lorain|B|https://chapincustommolding.com/|['635 Oberlin Elyria Road']
SITE-000310|CPC Bags — Elyria|Elyria|44035|Lorain|A|https://creativepackagingconcepts.com/|['214 Brace Avenue']
SITE-000312|Creative Millwork of Ohio, Inc. — Ashtabula|Ashtabula|44004|Ashtabula|A|https://www.creativemillwork.com/|['1801 W. 47th St.. RETIRED 2026-10-28 pass 4: Creative Millwork Ashtabula — out-of-scope org (packet 05). Do not promote. REJECT_FAILS annotation 2026-10-29 pass 5 (org record carries the detail): DOL Form 5500-SF evidence (PY2024 ACK 20250527090227NAL0010867424001, both filing cycles on file) removed the liveness basis of the packet-05 reject; scope re-verification queued — record NOT reinstated. REINSTATEMENT 2026-10-29 pass 6 §2.4: superseded by the wave-2 VERIFIED verdict (W2-049, Tier A) — see the org record. Promoted to the repo in pass 6 with IDs riding']
SITE-000318|Dca Construction Products — Garrettsville|Garrettsville|44231|Portage|A|https://durajoint.com/|['10421 Industrial Drive']
SITE-000325|Dinesol Plastics Inc — Niles|Niles|44446|Trumbull|A|https://dinesol.com/|['195 East Park Ave']
SITE-000327|Dott Foam Products — Avon|Avon|44011|Lorain|A|https://dottproducts.com/|['1273 Lear Industrial Pkwy']
SITE-000336|Dura-Line (Accessories)|Elyria|44035|Lorain|B|https://www.duraline.com/|['669 Sugar Lane']
SITE-000337|DURACOTE IC DISC CORPORATION — Ravenna|Ravenna|44266|Portage|A|https://www.duracote.com/|['350 N Diamond Street', '350 N Diamond Street']
SITE-000342|Eagle Elastomer — Peninsula|Peninsula|44264|Summit|A|https://eagleelastomer.com/|['70 Cuyahoga Falls Ind. Pkwy', '70 Cuyahoga Falls Industrial Parkway. county UNVERIFIED — Grok county_check=TRUE']
SITE-000343|ECP Corp DBA Polycase — Avon|Avon|44011|Lorain|A|https://www.polycase.com/|["1305 Chester Industrial Parkway. Wave-2 verification 2026-10-29 (W2-009): VERIFIED Tier A — an own-domain UL certificate settles the operator as ECP Corporation dba Polycase at 1305 Chester Industrial Pkwy, Avon. Org tier B -> A; site tier C -> A on the same evidence. Legal name not churned: verdict form 'ECP Corporation' is a stylistic variant of the recorded 'ECP Corp dba Polycase' (same operator asserted)", '1305 Chester Industrial Pkwy']
SITE-000348|Enterprise Plastics — Kent|Kent|44240|Portage|A|https://enterpriseplastics.net/|['838 Overholt Rd.', '838 Overholt Rd']
SITE-000362|Flambeau Sharon Center Plant|Wadsworth|44281|Medina|B|https://www.flambeau.com/|['1468 Wolf Creek Trail. county UNVERIFIED — Grok county_check=TRUE']
SITE-000368|Forest City Technologies — Wellington|Wellington|44090|Lorain|B|https://www.forestcitytech.com/|['299 Cloud Street']
SITE-000383|GRAFIX — Maple Heights|Maple Heights|44137|Cuyahoga|B|https://www.grafixplastics.com/|['5800 Pennsylvania Avenue']
SITE-000386|H & B Machine & Tool Co., Inc. — Cleveland|Cleveland|44103|Cuyahoga|B|https://www.hb-machine.com/|['1390 E. 40th St']
SITE-000390|HARRISON MACHINE & PLASTIC CORP.|Garrettsville|44231|Portage|A|https://www.harrisonplastic.com/|['11614 State Route 88', '11614 STATE ROUTE 88']
SITE-000396|Hub Plastics — Geneva|Geneva|44041|Ashtabula|A|https://hubplastics.com/|['700 Pro-Gram Parkway', '700 Pro-Gram Parkway']
SITE-000398|IER INDUSTRIES INC — Macedonia|Macedonia|44056|Summit|B|https://www.ierfujikura.com/|['8271 Bavaria Road']
SITE-000403|Infinity Composites Inc. — Ashtabula|Ashtabula|44004|Ashtabula|A|https://www.infinityfrp.com/|['2905 North Bend Rd', '2905 North Bend Road', '2905 North Bend RD']
SITE-000418|J & O Plastics Inc. — Rittman|Rittman|44270|Wayne|A|https://jandoplastics.com/|['12475 Sheets Rd']
SITE-000421|Jaco Products Co. — Middlefield|Middlefield|44062|Geauga|A|https://jacoproducts.com/|['15060 Madison Road']
SITE-000423|Jerico Plastic Industries, Inc. — Wadsworth|Wadsworth|44281|Medina|A|https://jericoplastic.com/|['7970 Boneta Rd']
SITE-000426|Johnson Brothers Rubber Co. — West Salem|West Salem|44287|Wayne|B|https://www.johnsonbrosrubbercompany.com/|['42 W. Buckeye Street. Wave-3 verification 2026-10-29 (W3-0745): VERIFIED Tier B at the own-site address 42 W Buckeye St, West Salem — site tier C -> B. The lead address 41 Center St, Greenwich (Huron) is NOT created: an unconfirmed establishment lead, held (pass-7 held item H-7.5)']
SITE-000429|JRM Chemical — Cleveland|Cleveland||Cuyahoga|A|https://soilmoist.com/|['4881 Neo Pkwy']
SITE-000441|Kobelco Stewart Bolling — Hudson|Hudson|44236|Summit|A|https://www.ksbi.com/|['1600 Terex Rd']
SITE-000445|Latham Pool Products (Youngstown - GLI)|Youngstown||Mahoning|A|https://www.glipoolproducts.com/|['215 Sinter Court', '215 Sinter Court']
SITE-000455|M&M Industries, Inc Lordstown — Lordstown|Lordstown|44481|Trumbull|B|https://www.mmcontainer.com/|['1702 Henn Pkwy']
SITE-000456|Mac Divitt Rubber Co., LLC — North Perry|North Perry|44081|Lake|A|https://www.macdivittrubber.com/|['3291 Center Road. county UNVERIFIED — Grok county_check=TRUE']
SITE-000458|Malish Corp., Plastic Div. — Mentor|Mentor|44060|Lake|B|https://malishplastics.com/|['7333 Corporate Boulevard']
SITE-000460|Mar-Bal Inc. — Chagrin Falls|Chagrin Falls|44023|Geauga|A|https://www.mar-bal.com/|['10095 Queens Way']
SITE-000461|Mar-Bal Inc. — Painesville|Painesville|44077|Lake|A|https://www.mar-bal.com/|['787 RENAISSANCE PKWY']
SITE-000466|MEDCO LABS — Bedford Heights|Bedford Heights|44146|Cuyahoga|A|https://medcocoatedproducts.com/|['5156 Richmond Road. county UNVERIFIED — Grok county_check=TRUE']
SITE-000473|Middlefield Plastics, Inc. — Middlefield|Middlefield|44062|Geauga|A|https://www.middlefieldplastics.com/|['15235 Burton Windsor Road']
SITE-000480|Molded Devices of Ohio, Inc|Kent||Portage|B|https://aptyx.com/|['4485 Crystal Pkwy', '4485 Crystal Parkway Ste 100', '4485 Crystal Pkwy Ste 100', '4485 Crystal Pkwy']
SITE-000481|Molded Extruded Specialties, Div. of Frank Novak & Sons, Inc. — Cleveland|Cleveland|44128|Cuyahoga|B|https://www.mespecialties.com/|['23940 Miles Road']
SITE-000483|Molded Fiber Glass Research Company|Ashtabula|44005|Ashtabula|B|https://moldedfiberglass.com/|['1315 W. 47th Street']
SITE-000486|Montville Plastics & Rubber — Parkman|Parkman|44080|Geauga|B|https://www.montvilleplastics.com/|['15567 Main Market Rd']
SITE-000487|MUM Industries, Inc. — Mentor|Mentor|44060|Lake|A|https://integraenclosures.com/|['8989 Tyler Blvd']
SITE-000488|NATIONAL FEEDSCREW & MACHINERY — Massillon|Massillon|44647|Stark|B|https://www.nfm.net/|['1339 DUNCAN ST SW', '577 Oberlin Road S.W.']
SITE-000496|Nippon Paint Automotive Americas — Cleveland|Cleveland|44102|Cuyahoga|B|https://www.nipponpaintamericas.com/|['11110 Berea Road']
SITE-000500|North American Seal & Supply, Inc. — Cleveland|Cleveland|44125|Cuyahoga|B|https://northamericanseal.com/|['7621 Hub Parkway']
SITE-000522|PFC-OH — Massillon|Massillon|44646|Stark|A|https://pfccases.com/|['201 Vista Ave SE']
SITE-000525|Philpott Solutions Group — Brunswick|Brunswick|44212|Medina|B|https://philpottsolutions.com/|['1010 Industrial Pkwy. N']
SITE-000528|The Plas-mac — Solon|Solon|44139|Cuyahoga|B|https://mercurymachine.com/plas-mac-corporation/|['30250 Carter St. county UNVERIFIED — Grok county_check=TRUE']
SITE-000533|PlastiWin Capital Equipment — Twinsburg|Twinsburg|44087|Summit|A|https://plastiwin.com/|['9347 Ravenna Rd Unit G']
SITE-000535|PLASTPRO INC — Ashtabula|Ashtabula|44004|Ashtabula|B|https://www.plastproinc.com/|['4737 KISTER CT']
SITE-000538|Greenbridge — Mentor (HQ & manufacturing)|Mentor|44060|Lake|A|https://www.greenbridge.com/|['6277 Heisley Road']
SITE-000539|Polychem Dispersions, Inc. — Middlefield|Middlefield|44062|Geauga|B|https://dispersions.com/|['16066 Industrial Parkway']
SITE-000540|Greenbridge Cleveland — Executive Offices & Manufacturing Facility|Cleveland|44102|Cuyahoga|A|https://www.greenbridge.com/|['7000 Denison Avenue']
SITE-000545|Polymer Packaging, Inc. — North Canton|North Canton|44720|Stark|A|https://www.polymerpkg.com/|['9239 Akcan Circle N.W']
SITE-000546|PolyStamp, LLC. — Youngstown|Youngstown|44515|Mahoning|A|https://poly-stamp.com/|['427 Thacher Ln']
SITE-000557|Premix, Inc. — Conneaut (North Kingsville)|Conneaut (North Kingsville)|44030|Ashtabula|B|https://premix-hadlock.com/|['3365 E Center St. county UNVERIFIED — Grok county_check=TRUE. Active confirmed 2026-10-30 in integration pass 17 (motion A-07): verification wave 1 design TRIA-S22 VERIFIED the North Kingsville plant (TRI RY2024 filer; Rt 20 & Harmon Rd as filed) — the design row folds into this held row (R-05); no duplicate site created']
SITE-000564|Promerus — Akron|Akron|44307|Summit|A|https://www.promerus.com/|['225 W Bartges St', '225 W BARTGES ST']
SITE-000574|Rapid Molds — North Canton|North Canton|44720|Stark|A|https://rapidmolding.com/|['9107 Pleasantwood Ave Nw', '9107 Pleasantwood Ave NW']
SITE-000586|Robin Industries, Inc. — Fredericksburg|Fredericksburg|44627|Wayne|A|https://www.robin-industries.com/|['300 West Clay Street']
SITE-000587|Robin Industries, Inc. — North Canton (HQ)|North Canton|44720|Stark|A|https://www.robin-industries.com/|['8562 Port Jackson Ave. NW']
SITE-000588|Röchling Automotive USA LLP — Akron|Akron|44312|Summit|A|https://www.roechling.com/|['2275 Picton Parkway']
SITE-000591|Royal Plastics, Inc. — Mentor|Mentor|44060|Lake|B|https://royalplastics.com/|['9410 Pineneedle Dr']
SITE-000601|Schneller LLC — Kent|Kent|44240|Portage|A|https://www.schneller.com/|['6019 Powdermill Road']
SITE-000603|Scott Molders, Inc. — Kent|Kent|44240|Portage|B|https://scottmolders.com/|['7180 State Rte. 43']
SITE-000605|Sealed Air (APS- STC)|Streetsboro|44241|Portage|B|https://www.sealedair.com/|['10175 Philipp Parkway', '10175 Philipp Pkwy']
SITE-000623|Sprosty Bag Co., Inc. — Smithville|Smithville|44677|Wayne|B|https://sprostybag.com/|['5857 N. Apple Creek Road. county UNVERIFIED — Grok county_check=TRUE']
SITE-000631|Sun State Plastics, Inc. — North Canton|North Canton|44720|Stark|B|https://www.sunstateplastics.com/|['4045 Kevin St. NW']
SITE-000646|THIRD DIMENSION, INC. — Geneva|Geneva|44041|Ashtabula|A|https://gbp.com/|['633 Pleasant Avenue', '633 PLEASANT AVE']
SITE-000647|Timco Rubber Products, Inc. — Berea|Berea|44017|Cuyahoga|A|https://www.timcorubber.com/|['125 Blaze Industrial Parkway. county UNVERIFIED — Grok county_check=TRUE']
WITNESSES evidenceID|siteID|claimDetail|sourceURL|notesExactQuoteAndSHA
EVD-152063|SITE-000186|street_address 4457 Tallmadge Road, Rootstown, OH; own-page ZIP 44272|http://www.jetrubber.com/|Raw checked 2026-11-06; SHA-256 550e8156d0b09f5bbf02d559116b67beca2ea0f859662348671bbe33f9be372b; quote: 4457 Tallmadge Road Rootstown, OH 44272. County, county_source, ZIP and record tier unchanged.
EVD-152064|SITE-000189|street_address 999 South Chillicothe Rd., Aurora, OH; own-page ZIP 44202|http://www.orazen.com/|Raw checked 2026-11-06; SHA-256 05141c209f2309e98f7b587668c5d85f7b0690795e3488c6dc2ef4041e4477bc; quote: 999 South Chillicothe Rd., Aurora, Ohio, 44202. County, county_source, ZIP and record tier unchanged.
EVD-152065|SITE-000192|street_address 10391 Brecksville Road, Brecksville, OH; own-page ZIP 44141|https://www.anyseals.com/|Raw checked 2026-11-06; SHA-256 f2abf0cc49d1b35fbb0dc29069c94d339969a2b0072fe57efff7588d0be20e89; quote: 10391 Brecksville Road Brecksville, Ohio 44141. County, county_source, ZIP and record tier unchanged.
EVD-152066|SITE-000196|street_address 112 Parker Court, Chardon, OH; own-page ZIP 44024|http://www.gbsa.com/|Raw checked 2026-11-06; SHA-256 aab3de08c181c4a2348a65fa7b591a8226ea8929cdbcdb10fd50ca5bd22b6cea; quote: 112 Parker Court, Chardon, OH 44024. County, county_source, ZIP and record tier unchanged.
EVD-152067|SITE-000198|street_address 3470 Blackmore Road, Perry, OH; own-page ZIP 44081|https://ohioelastomers.com|Raw checked 2026-11-06; SHA-256 1fe04dab7c7ffd7d46f5e70368d11ff1dbeb9610d569b77c4b59b8cb6a126c35; quote: 3470 Blackmore Road Perry, OH 44081. County, county_source, ZIP and record tier unchanged.
EVD-152069|SITE-000201|street_address 475 W. California Avenue, Sebring, OH; own-page ZIP 44672|https://salem-republic.com|Raw checked 2026-11-06; SHA-256 ea4731f1eeb1c03990e7e3a3f177ab5d72a442349a61af2cbf050af94c863b7f; quote: 475 W. California Avenue Sebring, OH 44672. County, county_source, ZIP and record tier unchanged.
EVD-152073|SITE-000206|street_address 1000 Venture Boulevard, Wooster, OH; own-page ZIP 44691|https://www.seamancorp.com|Raw checked 2026-11-06; SHA-256 c59ea122a73a9a0e0be0cc8cf29b8dbe4c451692980175bffb8da82abd87b8da; quote: 1000 Venture Boulevard Wooster, Ohio 44691. County, county_source, ZIP and record tier unchanged.
EVD-152082|SITE-000224|street_address 990 Evans Ave, Akron, OH; own-page ZIP 44305|https://additiveeng.com/|Raw checked 2026-11-06; SHA-256 ebd4ca87f2d90b4b26ecc51c6372e4af7581a6baa7a07c538be9a5a4435307c8; quote: 990 Evans Ave Akron, OH 44305. County, county_source, ZIP and record tier unchanged.
EVD-152086|SITE-000247|street_address 100 Water Street, Geneva, OH; own-page ZIP 44041|http://www.arcrubber.com/contact.php|Raw checked 2026-11-06; SHA-256 86b641d3f6f5660cac36e7dda3aea77dbe25d3656c241f7f6433d1a7c89321f0; quote: 100 Water Street, Geneva, OH 44041. County, county_source, ZIP and record tier unchanged.
EVD-152088|SITE-000263|street_address 10125 Wellman Road, Streetsboro, OH; own-page ZIP 44241|https://blade-tech.com/|Raw checked 2026-11-06; SHA-256 c12a6398f77bdaa5f61b58ea52f110e6d48f2c80714e2acfd84dbc51386ccf65; quote: 10125 Wellman Road Streetsboro, OH 44241. County, county_source, ZIP and record tier unchanged.
EVD-152089|SITE-000264|street_address 5020 Enterprise Parkway, Seville, OH; own-page ZIP 44273|https://blairrubber.com/|Raw checked 2026-11-06; SHA-256 f86aefea09af45a4fe90a9bc3eb97d96ae7633f9bc762e30d8f42e079e3dd9fd; quote: 5020 Enterprise Parkway Seville, OH 44273. County, county_source, ZIP and record tier unchanged.
EVD-152096|SITE-000310|street_address 214 Brace Avenue, Elyria, OH; own-page ZIP 44035|https://creativepackagingconcepts.com/|Raw checked 2026-11-06; SHA-256 6c7d67bce193264cfcd305613b448123ef852efbe80c956765d9b24487d08ac5; quote: 214 Brace Avenue, Elyria, OH 44035. County, county_source, ZIP and record tier unchanged.
EVD-152098|SITE-000318|street_address 10421 Industrial Drive, Garrettsville, OH; own-page ZIP 44231|https://durajoint.com/|Raw checked 2026-11-06; SHA-256 5205d2917bf340f1895a2419afc962a3ae6cfe844093ef57fc8e08b67e61fd89; quote: 10421 Industrial Drive Garrettsville, OH 44231. County, county_source, ZIP and record tier unchanged.
EVD-152099|SITE-000325|street_address 195 East Park Ave., Niles, OH; own-page ZIP 44446|https://dinesol.com/|Raw checked 2026-11-06; SHA-256 d83297462f2619ad07287a037871bd3e544092f8c300d2bebdd854d1f965dbd5; quote: 195 East Park Ave. Niles, OH 44446. County, county_source, ZIP and record tier unchanged.
EVD-152100|SITE-000327|street_address 1273 Lear Industrial Pkwy., Avon, OH; own-page ZIP 44011|https://dottproducts.com/|Raw checked 2026-11-06; SHA-256 9d3bad82114ffa3f414cf39fd47434b3b3add804e6b234ce1befa6c8a50e9497; quote: 1273 Lear Industrial Pkwy. Avon, OH 44011. County, county_source, ZIP and record tier unchanged.
EVD-152102|SITE-000337|street_address 350 N Diamond Street, Ravenna, OH; own-page ZIP 44266|https://www.duracote.com/|Raw checked 2026-11-06; SHA-256 a35490b375676b8eccd097892fd491156ed70b7feec2c43883ed745b6138337f; quote: 350 N Diamond Street Ravenna , OH 44266. County, county_source, ZIP and record tier unchanged.
EVD-152105|SITE-000348|street_address 838 Overholt Rd., Kent, OH; own-page ZIP 44240|https://enterpriseplastics.net/|Raw checked 2026-11-06; SHA-256 09f06dd1a86784e021b6bf5716d5a26af419985b91ce6c0afcced7f856da44da; quote: 838 Overholt Rd. Kent, OH 44240. County, county_source, ZIP and record tier unchanged.
EVD-152107|SITE-000368|street_address 299 Cloud Street, Wellington, OH; own-page ZIP 44090|https://www.forestcitytech.com/|Raw checked 2026-11-06; SHA-256 7eb016cb957a1d12b6a4a7a0d482b89b1f8b4fe28aa3443830f7aa8b327106f9; quote: 299 Cloud Street Wellington, OH 44090. County, county_source, ZIP and record tier unchanged.
EVD-152109|SITE-000386|street_address 1390 East 40th Street, Cleveland, OH; own-page ZIP 44103|https://www.hb-machine.com/|Raw checked 2026-11-06; SHA-256 d829070abae7c871adbce0d55fe3abb3846fd4ae8577ded4042b6141802f8445; quote: 1390 East 40th Street Cleveland, OH 44103. County, county_source, ZIP and record tier unchanged.
EVD-152110|SITE-000390|street_address 11614 State Route 88, Garrettsville, OH; own-page ZIP 44231|https://www.harrisonplastic.com/|Raw checked 2026-11-06; SHA-256 1e645163b530be29316d6371aee7bf146400ac4c1d52cd88430e14f93f853372; quote: 11614 State Route 88 Garrettsville, OH 44231. County, county_source, ZIP and record tier unchanged.
EVD-152111|SITE-000396|street_address 700 Pro-Gram Parkway, Geneva, OH; own-page ZIP 44041|https://hubplastics.com/|Raw checked 2026-11-06; SHA-256 e6cb1b8b73c497053cc68f2fb0f6a64c5b1bd3da3e50513e2b2adfc0d960c59c; quote: 700 Pro-Gram Parkway Geneva, OH 44041. County, county_source, ZIP and record tier unchanged.
EVD-152112|SITE-000398|street_address 8271 Bavaria Road, Macedonia, OH; own-page ZIP 44056|https://www.ierfujikura.com/contact-us|Raw checked 2026-11-06; SHA-256 327ef709f604f4edfed7a6c9162c6ec4bf1b93deea6d7acf046421139bb83c64; quote: 8271 Bavaria Road Macedonia, OH 44056. County, county_source, ZIP and record tier unchanged.
EVD-152113|SITE-000403|street_address 2905 N Bend Rd, Ashtabula, OH; own-page ZIP 44004|https://www.infinityfrp.com/|Raw checked 2026-11-06; SHA-256 923c37cc0fd08c28e64dcbc87b81961d603ab21fdc7c25f4d3a57d3aee6db55e; quote: 2905 N Bend Rd Ashtabula OH 44004. County, county_source, ZIP and record tier unchanged.
EVD-152116|SITE-000423|street_address 7970 Boneta Rd., Wadsworth, OH; own-page ZIP 44281|https://jericoplastic.com/|Raw checked 2026-11-06; SHA-256 65efaab8a2e159b01009a6866fef28ab81a62bb6c69fa2a7f8d48bb6ea9fa265; quote: 7970 Boneta Rd. Wadsworth, Ohio 44281. County, county_source, ZIP and record tier unchanged.
EVD-152118|SITE-000429|street_address 4881 NEO Parkway, Cleveland, OH; own-page ZIP 44128|https://soilmoist.com/|Raw checked 2026-11-06; SHA-256 2889bea9aaf281b9473e082f26e7c57719ae56fbf99081b040c9c003e2eeddfa; quote: 4881 NEO Parkway Cleveland, Ohio 44128. County, county_source, ZIP and record tier unchanged.
EVD-152119|SITE-000441|street_address 1600 Terex Rd., Hudson, OH; own-page ZIP 44236|https://www.ksbi.com/|Raw checked 2026-11-06; SHA-256 54cab3e764f00bc43fa8f54e144e615abfbddb40e32f6a749edc8e30caff43ad; quote: 1600 Terex Rd. Hudson, Oh 44236. County, county_source, ZIP and record tier unchanged.
EVD-152123|SITE-000458|street_address 7333 Corporate Boulevard, Mentor, OH; own-page ZIP 44060|https://malishplastics.com/|Raw checked 2026-11-06; SHA-256 3aa5a0998e121a7b2a97d3dbdea23dcc92294f4ed1d3be7afcb6326a28cb464f; quote: 7333 Corporate Boulevard Mentor, Ohio 44060. County, county_source, ZIP and record tier unchanged.
EVD-152124|SITE-000460|street_address 10095 Queens Way, Chagrin Falls, OH; own-page ZIP 44023|https://www.mar-bal.com/contact-us/|Raw checked 2026-11-06; SHA-256 1198eab31d109cbe913c9904510a317236606d8feebe91d8eb8242712eacee9a; quote: 10095 Queens Way Chagrin Falls, Ohio 44023. County, county_source, ZIP and record tier unchanged.
EVD-152125|SITE-000461|street_address 787 Renaissance Pkwy, Painesville, OH; own-page ZIP 44077|https://www.mar-bal.com/contact-us/|Raw checked 2026-11-06; SHA-256 1198eab31d109cbe913c9904510a317236606d8feebe91d8eb8242712eacee9a; quote: 787 Renaissance Pkwy Painesville, OH 44077. County, county_source, ZIP and record tier unchanged.
EVD-152131|SITE-000486|street_address 15567 Main Market Rd., Parkman, OH; own-page ZIP 44080|https://www.montvilleplastics.com/|Raw checked 2026-11-06; SHA-256 234ceecd3a28a6f1220449321ffc16639edd33e8abf2a2742089189df5163f68; quote: 15567 Main Market Rd. Parkman, OH 44080. County, county_source, ZIP and record tier unchanged.
EVD-152134|SITE-000496|street_address 11110 Berea Road, Cleveland, OH; own-page ZIP 44102|https://www.nipponpaintamericas.com/locations/|Raw checked 2026-11-06; SHA-256 36d38792c995bee7cca09b382752031565a0d58f8c64cbfe50e10c7ef19ca859; quote: 11110 Berea Road Cleveland, OH 44102. County, county_source, ZIP and record tier unchanged.
EVD-152135|SITE-000500|street_address 7621 HUB PARKWAY, Cleveland, OH; own-page ZIP 44125|https://northamericanseal.com/|Raw checked 2026-11-06; SHA-256 942f377aec093a83469b6d368af200e343022561cc3b438d4133881afbbf6deb; quote: 7621 HUB PARKWAY CLEVELAND, OH 44125. County, county_source, ZIP and record tier unchanged.
EVD-152141|SITE-000538|street_address 6277 Heisley Road, Mentor, OH; own-page ZIP 44060|https://greenbridge.com/contact/|Raw checked 2026-11-06; SHA-256 8a6ede6e68e869679bc2b9ac6a09b65b3ae0668dc42fc541169f0340a83dfab4; quote: 6277 Heisley Road Mentor, Ohio 44060. County, county_source, ZIP and record tier unchanged.
EVD-152142|SITE-000539|street_address 16066 Industrial Parkway, Middlefield, OH; own-page ZIP 44062|https://dispersions.com/|Raw checked 2026-11-06; SHA-256 7e6b46ef639a2248c63ea0d86f57b5f347a8dc8eece52f6be626ee04c03233f1; quote: 16066 Industrial Parkway Middlefield , OH 44062. County, county_source, ZIP and record tier unchanged.
EVD-152143|SITE-000540|street_address 7000 Denison Avenue, Cleveland, OH; own-page ZIP 44102|https://greenbridge.com/contact/|Raw checked 2026-11-06; SHA-256 8a6ede6e68e869679bc2b9ac6a09b65b3ae0668dc42fc541169f0340a83dfab4; quote: 7000 Denison Avenue Cleveland, Ohio 44102. County, county_source, ZIP and record tier unchanged.
EVD-152145|SITE-000546|street_address 427 Thacher Ln, Youngstown, OH; own-page ZIP 44515|https://poly-stamp.com/|Raw checked 2026-11-06; SHA-256 792c5e0e74902da7bbf114bd3b60a1558c7bf12955cb4d216c325d82dd9395f1; quote: 427 Thacher Ln Youngstown, OH 44515. County, county_source, ZIP and record tier unchanged.
EVD-152147|SITE-000564|street_address 225 W Bartges St, Akron, OH; own-page ZIP 44307|https://www.promerus.com/|Raw checked 2026-11-06; SHA-256 09d4305a785ae6be03ac49c271b5c913c93f7da6ea2e03e2708bca57caf8ff9e; quote: 225 W Bartges St Akron, Ohio 44307. County, county_source, ZIP and record tier unchanged.
EVD-152149|SITE-000586|street_address 300 West Clay Street, Fredericksburg, OH; own-page ZIP 44627|https://www.robin-industries.com/locations|Raw checked 2026-11-06; SHA-256 7541df8e6f8c58134a61b21f47bfca6c0eedb9326afed45684bd73d58e65aa07; quote: 300 West Clay Street Fredericksburg, OH 44627. County, county_source, ZIP and record tier unchanged.
FILE verdicts.csv
site_id,verdict,street_address,evidence_id,reason
SITE-000158,STILL_UNCERTAIN,2121 Euclid Avenue,,own-page ZIP conflicts with current site ZIP; notes address conflicts; dated adjudication needed
SITE-000179,STILL_UNCERTAIN,101 Ascot Parkway,,notes address conflicts; dated adjudication needed
SITE-000183,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000186,VERIFIED,4457 Tallmadge Road,EVD-152063,
SITE-000189,VERIFIED,999 South Chillicothe Rd.,EVD-152064,
SITE-000192,VERIFIED,10391 Brecksville Road,EVD-152065,
SITE-000196,VERIFIED,112 Parker Court,EVD-152066,
SITE-000198,VERIFIED,3470 Blackmore Road,EVD-152067,
SITE-000199,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000201,VERIFIED,475 W. California Avenue,EVD-152069,
SITE-000202,STILL_UNCERTAIN,689 Weber Drive,,notes address conflicts; dated adjudication needed
SITE-000203,STILL_UNCERTAIN,300 First Street,,notes address conflicts; dated adjudication needed
SITE-000204,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000206,VERIFIED,1000 Venture Boulevard,EVD-152073,
SITE-000212,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000213,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000216,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000217,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000218,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000220,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000221,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000222,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000224,VERIFIED,990 Evans Ave,EVD-152082,
SITE-000227,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000241,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000245,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000247,VERIFIED,100 Water Street,EVD-152086,
SITE-000250,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000263,VERIFIED,10125 Wellman Road,EVD-152088,
SITE-000264,VERIFIED,5020 Enterprise Parkway,EVD-152089,
SITE-000271,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000272,STILL_UNCERTAIN,23940 Mercantile Rd.,,notes address conflicts; dated adjudication needed
SITE-000276,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000281,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000285,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000286,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000310,VERIFIED,214 Brace Avenue,EVD-152096,
SITE-000312,STILL_UNCERTAIN,1801 W. 47th St,,notes address conflicts; dated adjudication needed
SITE-000318,VERIFIED,10421 Industrial Drive,EVD-152098,
SITE-000325,VERIFIED,195 East Park Ave.,EVD-152099,
SITE-000327,VERIFIED,1273 Lear Industrial Pkwy.,EVD-152100,
SITE-000336,STILL_UNCERTAIN,860 Garden St.,,own-page street blocks disagree; notes address conflicts; dated adjudication needed
SITE-000337,VERIFIED,350 N Diamond Street,EVD-152102,
SITE-000342,STILL_UNCERTAIN,70 Cuyahoga Falls Ind. Pkwy,,notes address conflicts; dated adjudication needed
SITE-000343,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000348,VERIFIED,838 Overholt Rd.,EVD-152105,
SITE-000362,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000368,VERIFIED,299 Cloud Street,EVD-152107,
SITE-000383,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000386,VERIFIED,1390 East 40th Street,EVD-152109,
SITE-000390,VERIFIED,11614 State Route 88,EVD-152110,
SITE-000396,VERIFIED,700 Pro-Gram Parkway,EVD-152111,
SITE-000398,VERIFIED,8271 Bavaria Road,EVD-152112,
SITE-000403,VERIFIED,2905 N Bend Rd,EVD-152113,
SITE-000418,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000421,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000423,VERIFIED,7970 Boneta Rd.,EVD-152116,
SITE-000426,STILL_UNCERTAIN,42 W. Buckeye Street,,notes address conflicts; dated adjudication needed
SITE-000429,VERIFIED,4881 NEO Parkway,EVD-152118,
SITE-000441,VERIFIED,1600 Terex Rd.,EVD-152119,
SITE-000445,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000455,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000456,STILL_UNCERTAIN,3291 Center Road,,notes address conflicts; dated adjudication needed
SITE-000458,VERIFIED,7333 Corporate Boulevard,EVD-152123,
SITE-000460,VERIFIED,10095 Queens Way,EVD-152124,
SITE-000461,VERIFIED,787 Renaissance Pkwy,EVD-152125,
SITE-000466,STILL_UNCERTAIN,5156 Richmond Road,,notes address conflicts; dated adjudication needed
SITE-000473,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000480,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000481,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000483,STILL_UNCERTAIN,2925 MFG Place,,own-page ZIP conflicts with current site ZIP; notes address conflicts; dated adjudication needed
SITE-000486,VERIFIED,15567 Main Market Rd.,EVD-152131,
SITE-000487,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000488,STILL_UNCERTAIN,577 Oberlin Road,,notes address conflicts; dated adjudication needed
SITE-000496,VERIFIED,11110 Berea Road,EVD-152134,
SITE-000500,VERIFIED,7621 HUB PARKWAY,EVD-152135,
SITE-000522,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000525,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000528,STILL_UNCERTAIN,30250 Carter St,,notes address conflicts; dated adjudication needed
SITE-000533,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000535,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000538,VERIFIED,6277 Heisley Road,EVD-152141,
SITE-000539,VERIFIED,16066 Industrial Parkway,EVD-152142,
SITE-000540,VERIFIED,7000 Denison Avenue,EVD-152143,
SITE-000545,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000546,VERIFIED,427 Thacher Ln,EVD-152145,
SITE-000557,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000564,VERIFIED,225 W Bartges St,EVD-152147,
SITE-000574,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000586,VERIFIED,300 West Clay Street,EVD-152149,
SITE-000587,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000588,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000591,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000601,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000603,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000605,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000623,STILL_UNCERTAIN,5857 N. Apple Creek Road,,notes address conflicts; dated adjudication needed
SITE-000631,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000646,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000647,STILL_UNCERTAIN,125 Blaze Industrial Parkway,,notes address conflicts; dated adjudication needed

FILE audit.csv
site_id,source_ref,sha256,result,error
SITE-000196,http://www.gbsa.com/,aab3de08c181c4a2348a65fa7b591a8226ea8929cdbcdb10fd50ca5bd22b6cea,PASS,
SITE-000201,https://salem-republic.com,ea4731f1eeb1c03990e7e3a3f177ab5d72a442349a61af2cbf050af94c863b7f,PASS,
SITE-000247,http://www.arcrubber.com/contact.php,86b641d3f6f5660cac36e7dda3aea77dbe25d3656c241f7f6433d1a7c89321f0,PASS,
SITE-000337,https://www.duracote.com/,a35490b375676b8eccd097892fd491156ed70b7feec2c43883ed745b6138337f,PASS,
SITE-000186,http://www.jetrubber.com/,550e8156d0b09f5bbf02d559116b67beca2ea0f859662348671bbe33f9be372b,PASS,
SITE-000396,https://hubplastics.com/,b4117db101b12ad1979605d756e14b138c1f74ace848024122f3cee7818d7fde,PASS,
SITE-000441,https://www.ksbi.com/,54cab3e764f00bc43fa8f54e144e615abfbddb40e32f6a749edc8e30caff43ad,PASS,
SITE-000546,https://poly-stamp.com/,792c5e0e74902da7bbf114bd3b60a1558c7bf12955cb4d216c325d82dd9395f1,PASS,
SITE-000461,https://www.mar-bal.com/contact-us/,0781c002b619aa4fe26d7342dd22ee5e1c1abc34770ae073bcd6c1693f64cd39,PASS,
SITE-000398,https://www.ierfujikura.com/contact-us,403091617f137bb6a0649359a55708b699dd7eca98bbcaf5f12bad36b0d9de00,PASS,
SITE-000539,https://dispersions.com/,7e6b46ef639a2248c63ea0d86f57b5f347a8dc8eece52f6be626ee04c03233f1,PASS,
SITE-000538,https://greenbridge.com/contact/,2caaedb2250d98ba8f0e6a6c924b6b3dead1c965679229fbb81856cbc9ea834e,PASS,
SITE-000460,https://www.mar-bal.com/contact-us/,0781c002b619aa4fe26d7342dd22ee5e1c1abc34770ae073bcd6c1693f64cd39,PASS,
SITE-000586,https://www.robin-industries.com/locations,7541df8e6f8c58134a61b21f47bfca6c0eedb9326afed45684bd73d58e65aa07,PASS,
SITE-000206,https://www.seamancorp.com,c59ea122a73a9a0e0be0cc8cf29b8dbe4c451692980175bffb8da82abd87b8da,PASS,
SITE-000496,https://www.nipponpaintamericas.com/locations/,36d38792c995bee7cca09b382752031565a0d58f8c64cbfe50e10c7ef19ca859,PASS,
SITE-000198,https://ohioelastomers.com,1fe04dab7c7ffd7d46f5e70368d11ff1dbeb9610d569b77c4b59b8cb6a126c35,PASS,
SITE-000564,https://www.promerus.com/,97ffa8324138d8d55d549c83ce593c985f67fcf32920cf673166e57178b9d335,PASS,
SITE-000263,https://blade-tech.com/,4a8e0f791c7ce83081ce401b34a84739b64d21393b74b6f32c6c17c2fa693afb,PASS,
SITE-000386,https://www.hb-machine.com/,d829070abae7c871adbce0d55fe3abb3846fd4ae8577ded4042b6141802f8445,PASS,
SITE-000486,https://www.montvilleplastics.com/,234ceecd3a28a6f1220449321ffc16639edd33e8abf2a2742089189df5163f68,PASS,
SITE-000264,https://blairrubber.com/,482a7998cce468dff4c8d3509a51f7aaadae2af8a9676eca28394136432213ca,PASS,
SITE-000500,https://northamericanseal.com/,6de06fd70bc764c0554e13925432553142bd7ede0aa1a62d044b555331329043,PASS,
SITE-000429,https://soilmoist.com/,2889bea9aaf281b9473e082f26e7c57719ae56fbf99081b040c9c003e2eeddfa,PASS,
SITE-000310,https://creativepackagingconcepts.com/,6c7d67bce193264cfcd305613b448123ef852efbe80c956765d9b24487d08ac5,PASS,
SITE-000318,https://durajoint.com/,4810ea14a98503aeeb0acdc007e431b7e07cf1c88b7db9236a1c2ee705355ee4,PASS,
SITE-000325,https://dinesol.com/,d83297462f2619ad07287a037871bd3e544092f8c300d2bebdd854d1f965dbd5,PASS,
SITE-000403,https://www.infinityfrp.com/,63df5941fef1ae37fa76785def1e05aecf86181404557025cb53135a1d3c498f,PASS,
SITE-000540,https://greenbridge.com/contact/,a2637606e276ed33b69878d6efe18d140f1e9c09c458496ab5d069fe17e0eb86,PASS,
SITE-000189,http://www.orazen.com/,3c3691da2b2448d205236fa0bc405f6ed4d64a8518c07c9c019c79d9cd9d5ab5,PASS,

FILE summary.json
{
  "eligible_sites": 448,
  "prior_batch_sites": 60,
  "worked": 100,
  "unworked": 288,
  "fills": 38,
  "holds": 62,
  "active_ohio_sites": 1883,
  "before_streets": 286,
  "after_streets": 324
}
