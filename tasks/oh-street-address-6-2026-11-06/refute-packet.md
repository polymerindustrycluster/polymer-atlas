Adversarial deep completion refute: L2 Ohio round6, agent/codex/oh-street-address-6. Readonly; end VERDICT APPROVE/REFUTE with demonstrated facts, no merge/status actions.
Scope fixed BEFOREfetch: original448frame positions261–360,100active storedPIC18A/B blank streets.260prior+100worked+88future=448. IDs152260–152359 fixed by original frame position; main ca9480fa. All448IDs/order/reservations match original round3 frame on main.100refreshed selected records, including one ecosystem-held operator, no scope/ring/status rulings.
Result36VERIFIED64STILL_UNCERTAIN;36existingstreet/source-only edits+36append-only own_site/address/supports_A evidence;tiersA24/B12unchanged. ActiveOH324/1883→360/1883(17.21→19.12%), excludes pending15619/19224/20725. Sources operator pages rawchecked with curl browserUA, held-host redirects only, physical street+city+knownZIPbinding.199attempts=176fetched23unavailable;100IDs reconciled;42rawaddresssites.
Hold64=58noadmissiblerawblock+1ownstreetconflict+4notesconflict+1knownZIPconflict. Real six conflicts asserted HOLD: ChemicalSolvents twoClevelandstreets;Ruscoe219EMiller vs485Kenmore;SOPREMA310&275 vs310Quadral;MaineRubberUnit1 vsunitless;Zehrco5500Washingtonvs1501W47thHQ;FlexLinkZIP18222vs44119. No unavailable route implies absence/closure.
Preliminary11positive planner falsely retained '(per wave-3 verdict...)'/'(per the operator...)' and '. Filing basis:' inside street text. Three old/new reproductions in notes_regression.csv and10literalfixtures establish exact qualifier stripping; ordinary PARK/Pk normalization adds no location inference. Same100frame/42rawsites/sources beforeafter. Suite100≠300, Unit1≠unitless, house numbers distinct; all six actualconflicts remainheld. Scrutinize parser for hidden real conflict erasure and sameoperatorHQ conflation. GenericHQ guard from207 unchanged.
ChecksPASS:3LIVEknown beforefetch+wrongcity/PObox/phoneprefix; check.py36fillfieldboundary+byte-idempotence+street/foreignEVD-beforewrite+10notes/PARK/unit/by-mailfixtures; seeded20261106 random30/36freshaudit0errors(quote/city/heldhost/freshmailcontext); validator0; mainkey/legacyEVDpreservation exactly36+36; allshardstreet/city/state scan0otherhits; rowloss/diffcheck. No scripts edits. County/county_source/ZIP/coordinates/tier/status/ring/registry/derived fields untouched; no entities created/deleted/merged.
ReferenceonlyCensusRittmanquery returned0addressmatches: NOTcountyconfirmation or evidenceofabsence; rawJSON retained, no geographywrite. Widerlocalcatalogue partial onMac, no private/licensed material imported.
Potential failures: physical-vs-mail context; operator/sitebinding; strippedunit/oldstreet; unknownZIP masquerading localitymatch; rawquote words/order; globalIDcollision/legacyrowloss/replaydrift; sourceyield under-return; counting unworked as reviewed.
Run: python3 tasks/oh-street-address-6-2026-11-06/check.py; python3 tasks/oh-street-address-6-2026-11-06/audit.py; python3 tasks/oh-street-address-6-2026-11-06/fetch.py --known; python3 scripts/validate.py; python3 scripts/check_row_loss.py --base origin/main --head HEAD.
All100outcomes/36witnesses and audit below; full448frame/notes/rawchecks/pagechecks/README/journal available in task folder. No previous-pass data/code/docs rides this branch. Refute before readiness.

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
 aliases={'STREET':'ST','ROAD':'RD','AVENUE':'AVE','DRIVE':'DR','COURT':'CT','PARKWAY':'PKWY','BOULEVARD':'BLVD','PLACE':'PL','PARK':'PK','WEST':'W','EAST':'E','NORTH':'N','SOUTH':'S'}
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
 assert len(selected)==100 and len({s['reserved_evidence_id'] for s in frame})==448
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
       source_class='own_site',source_ref=r['url'],observed_date=DATE,tier_effect='supports_A',created_by='atlas-L2-oh-address-6',
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
 summary=dict(eligible_sites=448,prior_batch_sites=260,worked=100,unworked=88,fills=len(ev),holds=100-len(ev),active_ohio_sites=len(active),before_streets=before,after_streets=before+len(ev))
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

 assert build.key('2915 INDUSTRIAL PARK DR')==build.key('2915 Industrial Pk Dr')
 assert build.key('7675 JENTHER DR')!=build.key('7676 JENTHER DR')
 assert build.key(build.note_streets(dict(city='Middlefield',notes='Street: 16090 Industrial Parkway, Unit 1 (per wave-3 verdict W3-0600 evidence).'))[-1])!=build.key('16090 Industrial Parkway')
 for sid in ('SITE-001651','SITE-001661','SITE-001690','SITE-001715','SITE-001725','SITE-001793'):
  assert next(v for v in verdicts if v['site_id']==sid)['verdict']=='STILL_UNCERTAIN',sid
 assert len(ev)==36,'frozen source-adjudication yield changed; inspect before revising'
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
  build.write(p,[r for r in build.read(p) if r['created_by']!='atlas-L2-oh-address-6'])
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  after=build.read(build.ROOT/'data/sites_OH.csv');changed=0
  assert len(before)==len(after)
  for a,b in zip(before,after):
   fields={k for k in a if a[k]!=b[k]}
   assert fields <= {'street_address','sources'},(a['site_id'],fields)
   if fields:
    changed+=1;assert not a['street_address'] and b['street_address'] and a['operating_status']=='active'
  assert changed==len(ev)
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
 print(f'PASS {len(ev)} fills; street/sources only; byte-idempotent; street and foreign-ID mutations rejected before canonical writes')
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
 return dict(site_id=e['record_id'],source_ref=e['source_ref'],sha256=sha,result='PASS' if not error else 'FAIL',error=error)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(check,sample))
write(TASK/'audit.csv',out)
summary=dict(accepted_fills=len(evidence),audited=len(out),errors=sum(bool(r['error']) for r in out))
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert len(out)==min(30,len(evidence)) and summary['errors']==0,out

SELECTED INPUTS;full names and notes in frame.csv
site_id,org_id,city,zip,county,verification_tier,website,reserved_evidence_id
SITE-001640,ORG-001573,Wooster,,Wayne,B,https://www.prc-saltillo.com/,EVD-152260
SITE-001647,ORG-001576,Garfield Heights,44125,Cuyahoga,A,https://aabacoplastics.com/,EVD-152261
SITE-001648,ORG-001577,Beachwood,44122,Cuyahoga,B,https://master-builders-solutions.com/,EVD-152262
SITE-001649,ORG-001578,Akron,44301,Summit,A,https://brightideashops.com/,EVD-152263
SITE-001650,ORG-001579,Solon,44139,Cuyahoga,A,https://cartierwilson.com/,EVD-152264
SITE-001651,ORG-001580,Cleveland,44109,Cuyahoga,B,https://chemicalsolvents.com/,EVD-152265
SITE-001652,ORG-001581,Solon,,Cuyahoga,B,https://epacflexibles.com/,EVD-152266
SITE-001654,ORG-000135,Walton Hills,44146,Cuyahoga,B,https://www.valtris.com,EVD-152267
SITE-001655,ORG-001583,Ashtabula,44004,Ashtabula,A,https://grandriverrubber.com/,EVD-152268
SITE-001656,ORG-001584,Solon,44139,Cuyahoga,B,https://green-innovate.com/,EVD-152269
SITE-001657,ORG-001585,Chardon,44024,Geauga,A,https://hitechextrusions.com/,EVD-152270
SITE-001658,ORG-001586,Kent,44240,Portage,A,https://jos-tech.com/,EVD-152271
SITE-001659,ORG-001587,Solon,44139,Cuyahoga,B,https://minijector.com/,EVD-152272
SITE-001660,ORG-001588,Kent,44240,Portage,A,https://kentmold.com/,EVD-152273
SITE-001661,ORG-001589,Akron,44301,Summit,B,https://ruscoe.com/,EVD-152274
SITE-001662,ORG-001590,Warren,,Trumbull,B,https://tolwire.com/,EVD-152275
SITE-001663,ORG-001591,Medina,44256,Medina,B,https://winsellinc.com/,EVD-152276
SITE-001664,ORG-001592,Highland Heights,,Cuyahoga,B,https://alphatoolandmold.com/,EVD-152277
SITE-001665,ORG-001593,Cleveland,,Cuyahoga,B,https://clamshellusa.com/,EVD-152278
SITE-001666,ORG-001594,Berea,44017,Cuyahoga,A,https://crgiconnect.com/,EVD-152279
SITE-001667,ORG-001595,Westlake,,Cuyahoga,B,https://1110gear.com/,EVD-152280
SITE-001668,ORG-001596,Cleveland,,Cuyahoga,A,https://gatewayrecycle.com/,EVD-152281
SITE-001669,ORG-001597,Niles,,Trumbull,B,https://itps-inc.com/,EVD-152282
SITE-001670,ORG-001598,Cleveland,,Cuyahoga,B,https://homesteadfinishingproducts.com/,EVD-152283
SITE-001671,ORG-001599,Solon,,Cuyahoga,B,https://multiplastsystems.com/,EVD-152284
SITE-001672,ORG-001600,Brooklyn Heights,,Cuyahoga,B,https://northshorestrapping.com/,EVD-152285
SITE-001674,ORG-001602,Cleveland,,Cuyahoga,B,https://royalpowder.com/,EVD-152286
SITE-001675,ORG-001603,Brooklyn Heights,,Cuyahoga,B,https://speedlinepvc.com/,EVD-152287
SITE-001680,ORG-001607,Newbury,,Geauga,B,https://kinetico.com/,EVD-152288
SITE-001682,ORG-001609,Stow,,Summit,A,https://mactac.com/,EVD-152289
SITE-001688,ORG-000004,Ravenna,,Portage,A,https://www.parker.com,EVD-152290
SITE-001690,ORG-001619,Wadsworth,,Medina,A,https://www.soprema.us/,EVD-152291
SITE-001693,ORG-001622,Salem,,Columbiana,A,http://www.absolutepolymers.com/,EVD-152292
SITE-001694,ORG-001623,Brunswick,,Medina,B,https://adcalinc.com/,EVD-152293
SITE-001695,ORG-001624,Akron,,Summit,A,http://www.acecryo.com/,EVD-152294
SITE-001702,ORG-001630,Akron,,Summit,A,https://www.akronbelting.com/,EVD-152295
SITE-001703,ORG-001631,Copley,,Summit,B,http://www.akrondispersions.com/,EVD-152296
SITE-001707,ORG-001634,Ravenna,,Portage,A,https://www.astraproductsltd.com/,EVD-152297
SITE-001708,ORG-001635,Green,,Summit,A,http://www.eagleplasticsgroup.com/,EVD-152298
SITE-001709,ORG-001636,Akron,,Summit,B,https://pressuresensitivefilms.com/,EVD-152299
SITE-001710,ORG-001637,Willoughby,,Lake,B,https://www.ftmeng.com/,EVD-152300
SITE-001712,ORG-001639,Elyria,,Lorain,A,http://plastic-enterprises.com,EVD-152301
SITE-001714,ORG-001640,Brunswick,,Medina,A,https://m-line.com/,EVD-152302
SITE-001715,ORG-001641,Middlefield,,Geauga,A,https://mainerubberpreforms.com/,EVD-152303
SITE-001716,ORG-001642,Massillon,,Stark,B,http://www.motivodisplay.com/,EVD-152304
SITE-001717,ORG-001643,Mentor,,Lake,A,https://www.overmoldexpress.com/,EVD-152305
SITE-001718,ORG-001644,Elyria,,Lorain,B,https://www.rpmindinc.com/,EVD-152306
SITE-001719,ORG-001645,Austinburg,,Ashtabula,B,http://rtscompaniesinc.com/,EVD-152307
SITE-001721,ORG-001646,Streetsboro,,Portage,B,http://www.tuscoproducts.com/,EVD-152308
SITE-001722,ORG-001647,Lorain,,Lorain,A,http://www.vaprocessinc.com/contact,EVD-152309
SITE-001723,ORG-001648,East Canton,,Stark,B,http://tuffboom.com/,EVD-152310
SITE-001725,ORG-000640,Ashtabula,,Ashtabula,B,https://zehrco-giancola.com/,EVD-152311
SITE-001729,ORG-001653,Willoughby,,Lake,A,https://brunsbrush.com/,EVD-152312
SITE-001731,ORG-001655,Chagrin Falls,,Geauga,B,https://c4poly.com/,EVD-152313
SITE-001732,ORG-001656,Akron,,Summit,A,https://clearsonic.com/,EVD-152314
SITE-001733,ORG-001657,Seville,,Medina,B,https://comdess.com/,EVD-152315
SITE-001741,ORG-001665,North Canton,,Stark,A,https://dischem.com/,EVD-152316
SITE-001742,ORG-001666,Stow,,Summit,A,https://drossbach.com/,EVD-152317
SITE-001743,ORG-001667,Streetsboro,,Portage,A,https://dudick.com/,EVD-152318
SITE-001744,ORG-001668,Norwalk,,Huron,A,https://durablecorp.com/,EVD-152319
SITE-001746,ORG-001670,Eastlake,,Lake,A,https://enpac.com/,EVD-152320
SITE-001747,ORG-001671,Rittman,,Wayne,A,https://fastforming.com/,EVD-152321
SITE-001748,ORG-001672,Mantua,,Portage,B,https://flashitllc.com/,EVD-152322
SITE-001754,ORG-001678,Canton,,Stark,A,https://harrisonpaint.com/,EVD-152323
SITE-001755,ORG-001679,Northfield,,Summit,A,https://holloplastics.com/,EVD-152324
SITE-001756,ORG-001680,Ravenna,,Portage,B,https://hytechproducts.com/,EVD-152325
SITE-001757,ORG-001681,Cuyahoga Falls,,Summit,B,https://inter-ion.com/,EVD-152326
SITE-001758,ORG-001682,Tallmadge,,Summit,A,https://vinylleatherrepair.com/,EVD-152327
SITE-001770,ORG-001694,Ashland,,Ashland,A,https://novatex.us/,EVD-152328
SITE-001774,ORG-001698,Canton,,Stark,B,https://www.prime-plastics.com/,EVD-152329
SITE-001775,ORG-001699,Westlake,,Cuyahoga,B,aerocaseinc.com,EVD-152330
SITE-001776,ORG-001700,Bedford,,Cuyahoga,B,http://www.haradhesive.com/,EVD-152331
SITE-001777,ORG-001701,Cleveland,,Cuyahoga,B,https://www.continentalpaints.com/,EVD-152332
SITE-001779,ORG-001703,Valley View,,Cuyahoga,B,premieraerosol.com,EVD-152333
SITE-001780,ORG-001704,Cleveland,,Cuyahoga,A,vpdcorp.net,EVD-152334
SITE-001783,ORG-001707,Painesville,,Lake,B,dynaflexinc.com,EVD-152335
SITE-001785,ORG-001709,Norwalk,,Huron,A,tuftexballoons.com,EVD-152336
SITE-001786,ORG-001710,Akron,,Summit,B,none found,EVD-152337
SITE-001790,ORG-001714,Warren,,Trumbull,B,amlube.com,EVD-152338
SITE-001791,ORG-001715,Cleveland,,Cuyahoga,B,axionlabs.co,EVD-152339
SITE-001793,ORG-001717,Cleveland,18222,Cuyahoga,B,flexlinkllc.com,EVD-152340
SITE-001796,ORG-001720,Cleveland,,Cuyahoga,A,sunartdecals.com,EVD-152341
SITE-001798,ORG-001722,Bedford Heights,26201,Cuyahoga,B,grovebags.com,EVD-152342
SITE-001799,ORG-001723,Sandusky,,Erie,B,https://pntproducts.com/,EVD-152343
SITE-001800,ORG-001724,Medina,,Medina,B,https://www.rpmrepublic.com/,EVD-152344
SITE-001801,ORG-001725,Sandusky,,Erie,B,https://www.sealmaster.net/,EVD-152345
SITE-001804,ORG-001728,Warren,44484,Trumbull,B,https://www.anatotemp.com/#/,EVD-152346
SITE-001806,ORG-001730,Shaker Heights,16781,Cuyahoga,B,https://3d-dent.com/,EVD-152347
SITE-001807,ORG-001731,Norwalk,44857,Huron,B,https://nissha.medical ; https://nissha.com,EVD-152348
SITE-001815,ORG-001739,Concord Twp,44077,Lake,A,http://www.api2.net/,EVD-152349
SITE-001820,ORG-001744,Brunswick,44212,Medina,A,https://jet-di.com/,EVD-152350
SITE-001831,ORG-001755,Medina,44256,Medina,A,http://www.medinarecycling.com/,EVD-152351
SITE-001833,ORG-001757,Mentor,44060,Lake,B,https://acousa.com/,EVD-152352
SITE-001834,ORG-001758,Niles,44446,Trumbull,B,http://www.nilesbldg.com/,EVD-152353
SITE-001836,ORG-000549,Independence,44131,Cuyahoga,A,https://www.robin-industries.com/,EVD-152354
SITE-001837,ORG-000057,Kent,44240,Portage,B,https://smithersoasis.com,EVD-152355
SITE-001840,ORG-000115,Mentor,44060,Lake,B,http://www.cuyahogaplastics.com/,EVD-152356
SITE-001842,ORG-000007,Orrville,,Wayne,B,https://www.vibrantz.com,EVD-152357
SITE-001843,ORG-001760,Cleveland,44135,Cuyahoga,B,https://pioneerathletics.com,EVD-152358
SITE-001846,ORG-001763,Austinburg,44010,Ashtabula,B,https://dalinmold.com,EVD-152359

FILE evidence.csv
evidence_id,record_table,record_id,claim_type,claim_detail,source_class,source_ref,observed_date,tier_effect,created_by,notes
EVD-152260,sites,SITE-001640,address,"street_address 1022 Heyl Rd, Wooster, OH; own-page ZIP 44691",own_site,https://prc-saltillo.com/contact,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 c76241cdc2eba04748b249ed0709c1b5f5bfe25c6b3d54d2df716b3babc74d4f; quote: 1022 Heyl Rd Wooster, OH 44691. County, county_source, ZIP and record tier unchanged."
EVD-152261,sites,SITE-001647,address,"street_address 9520 Midwest Avenue, Garfield Heights, OH; own-page ZIP 44125",own_site,https://aabacoplastics.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 ae4542f7952a51e712d39c0557e05d5ef1c3cd4c2f16452e456e94ece66daa88; quote: 9520 Midwest Avenue Garfield Heights , OH 44125. County, county_source, ZIP and record tier unchanged."
EVD-152268,sites,SITE-001655,address,"street_address 2029 Aetna Rd, Ashtabula, OH; own-page ZIP 44004",own_site,https://grandriverrubber.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 98702d9d919bd0f7f4497a6d8f369580076cf69b366d84b7fcbd255275eefc01; quote: 2029 Aetna Rd, Ashtabula, OH, 44004. County, county_source, ZIP and record tier unchanged."
EVD-152270,sites,SITE-001657,address,"street_address 12621 Chardon Windsor Road, Chardon, OH; own-page ZIP 44024",own_site,https://hitechextrusions.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 c93c9d97ac083f217b96e6c6bcd9df08b320bdb5def1859a43feb5515091c344; quote: 12621 Chardon Windsor Road Chardon, Ohio 44024. County, county_source, ZIP and record tier unchanged."
EVD-152271,sites,SITE-001658,address,"street_address 852 West Main St., Kent, OH; own-page ZIP 44240",own_site,https://jos-tech.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 5bd00f990a05a80c7b876f3e33874e91636c99418df15cfd4423571f5f4ea30c; quote: 852 West Main St., Kent, OH 44240. County, county_source, ZIP and record tier unchanged."
EVD-152279,sites,SITE-001666,address,"street_address 125 Pelret Industrial Parkway, Berea, OH; own-page ZIP 44017",own_site,https://crgiconnect.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 463fbb3562945e5a7b4268161fcdf626291206bc051e8a6e258146a2f6ce6df7; quote: 125 Pelret Industrial Parkway Berea, OH 44017. County, county_source, ZIP and record tier unchanged."
EVD-152281,sites,SITE-001668,address,"street_address 4223 East 49th Street, Cleveland, OH; own-page ZIP 44125",own_site,https://gatewayrecycle.com/locations/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 5bd3342d1a60b14a1adf1ec24e301d1a60fecc055d34a28b121d51cd7c20945b; quote: 4223 East 49th Street Cleveland, Ohio 44125. County, county_source, ZIP and record tier unchanged."
EVD-152285,sites,SITE-001672,address,"street_address 1400 Valley Belt Road, Brooklyn Heights, OH; own-page ZIP 44131",own_site,https://northshorestrapping.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 8e599104420253dae43f42968cf19c53f3eb0ff73d9f41c79daef546a6c5327c; quote: 1400 Valley Belt Road, Brooklyn Heights, Ohio, 44131. County, county_source, ZIP and record tier unchanged."
EVD-152287,sites,SITE-001675,address,"street_address 1215 Valley Belt Road, Brooklyn Heights, OH; own-page ZIP 44131",own_site,https://speedlinepvc.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 ca7597a67800b9406cd10d8773243c1ac74098e7d2972d7f4cb3de1886a1ac8e; quote: 1215 Valley Belt Road Brooklyn Heights, OH 44131. County, county_source, ZIP and record tier unchanged."
EVD-152289,sites,SITE-001682,address,"street_address 4560 Darrow Road, Stow, OH; own-page ZIP 44224",own_site,https://mactac.com/ContactUs,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 0e819108652a39cbb828a0b9c226d22da3d21183681866cb00d642f098cafe93; quote: 4560 Darrow Road Stow, Ohio 44224. County, county_source, ZIP and record tier unchanged."
EVD-152295,sites,SITE-001702,address,"street_address 1244 Home Ave, Akron, OH; own-page ZIP 44310",own_site,https://www.akronbelting.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 74a46b3abb14f89efd158140539d26cba0f5313886eb34ab189ff0660df493ac; quote: 1244 Home Ave, Akron, OH 44310. County, county_source, ZIP and record tier unchanged."
EVD-152297,sites,SITE-001707,address,"street_address 7154 State Route 88, Ravenna, OH; own-page ZIP 44266",own_site,https://www.astraproductsltd.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 86e306285e48fce27231703ce397768cf5d892b72d3fae28a0b46675329aa5c6; quote: 7154 State Route 88, Ravenna, Ohio 44266. County, county_source, ZIP and record tier unchanged."
EVD-152301,sites,SITE-001712,address,"street_address 41520 Schaden Road, Elyria, OH; own-page ZIP 44035",own_site,http://plastic-enterprises.com,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 d5f0d57578c8c6ed18d4052a83a931f2f516fa216bb30dc8b5aa5a89e881d79e; quote: 41520 Schaden Road Elyria, Ohio 44035. County, county_source, ZIP and record tier unchanged."
EVD-152302,sites,SITE-001714,address,"street_address 2906 Nationwide Pkwy, Brunswick, OH; own-page ZIP 44212",own_site,https://m-line.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 eada56e407a4b226382a1c0ad73ae4ecf8f3a14a0a2e653aec379e93e81e21fc; quote: 2906 Nationwide Pkwy Brunswick, OH 44212. County, county_source, ZIP and record tier unchanged."
EVD-152305,sites,SITE-001717,address,"street_address 7675 Jenther Dr, Mentor, OH; own-page ZIP 44060",own_site,https://www.overmoldexpress.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 7133716e8923fa8a399deacb6f1ac62661bc4ec442fa650fe729f09485c7b8b8; quote: 7675 Jenther Dr, Mentor, OH 44060. County, county_source, ZIP and record tier unchanged."
EVD-152307,sites,SITE-001719,address,"street_address 2900 Industrial Park Drive, Austinburg, OH; own-page ZIP 44010",own_site,http://rtscompaniesinc.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 3e9c71c0c49a8ec27c3fa628959896af41359e364fcd95d40efdaad5d7fd72e7; quote: 2900 Industrial Park Drive, Austinburg, OH 44010. County, county_source, ZIP and record tier unchanged."
EVD-152308,sites,SITE-001721,address,"street_address 10008 State Route 43, Streetsboro, OH; own-page ZIP 44241",own_site,http://www.tuscoproducts.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 fee6c8ef8d3bb7746ac5eb6b16d43b7be9dc6c15e84ef7a370329a6cc142c76a; quote: 10008 State Route 43 Streetsboro, Ohio 44241. County, county_source, ZIP and record tier unchanged."
EVD-152309,sites,SITE-001722,address,"street_address 2345 E. 28th St., Lorain, OH; own-page ZIP 44055",own_site,http://www.vaprocessinc.com/contact,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 1d2bbf3a9534094e1d03255bfbc5eb52de1400a28963e3fd10aacf0f9b6ef014; quote: 2345 E. 28th St. Lorain, OH 44055. County, county_source, ZIP and record tier unchanged."
EVD-152312,sites,SITE-001729,address,"street_address 36650 Reading Ave., Willoughby, OH; own-page ZIP 44094",own_site,https://brunsbrush.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 e88aabb060a24381b3eaf1243b05b07e1caf0b4d46a71627049d66e164b51933; quote: 36650 Reading Ave. Willoughby, OH 44094. County, county_source, ZIP and record tier unchanged."
EVD-152314,sites,SITE-001732,address,"street_address 1025 Evans Ave, Akron, OH; own-page ZIP 44305",own_site,https://clearsonic.com/pages/contact,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 7a042e5117a862f15e30c7105d01e3c4c891dd37cb744f131c56a313e914b5f4; quote: 1025 Evans Ave Akron OH 44305. County, county_source, ZIP and record tier unchanged."
EVD-152317,sites,SITE-001742,address,"street_address 1500 Commerce Drive, Stow, OH; own-page ZIP 44224",own_site,https://drossbach.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 574fae521f2e433803fc42868e42c313013c1068ddaf420fdbe97cff677d92ab; quote: 1500 Commerce Drive Stow, Ohio 44224. County, county_source, ZIP and record tier unchanged."
EVD-152319,sites,SITE-001744,address,"street_address 75 N. Pleasant St, Norwalk, OH; own-page ZIP 44857",own_site,https://durablecorp.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 6b49b08f6fbdd698f88f99783440df4065a23b2efd1a2db9d9b21b24eba86140; quote: 75 N. Pleasant St Norwalk, Ohio 44857. County, county_source, ZIP and record tier unchanged."
EVD-152320,sites,SITE-001746,address,"street_address 34355 Melinz Parkway, Eastlake, OH; own-page ZIP 44095",own_site,https://enpac.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 69329f80551204ba1571b8fae83dd03c779f11db6cb680fdde4bd8d0026d7d81; quote: 34355 Melinz Parkway Eastlake, OH 44095. County, county_source, ZIP and record tier unchanged."
EVD-152321,sites,SITE-001747,address,"street_address 300 Morning Star Drive, Rittman, OH; own-page ZIP 44270",own_site,https://fastforming.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 4c6d389eadaa7f2e0d25aeb2323b7c453e9014ee119fd244c2ebdc3e5e448420; quote: 300 Morning Star Drive Rittman, OH 44270. County, county_source, ZIP and record tier unchanged."
EVD-152322,sites,SITE-001748,address,"street_address 4494 Orchard Street, Mantua, OH; own-page ZIP 44231",own_site,https://flashitllc.com/contact/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 32cdb91a75656119de306373d4fb8fbb7f18710ef3b16488f41aff3bf2cf7f94; quote: 4494 Orchard Street Mantua, Ohio 44231. County, county_source, ZIP and record tier unchanged."
EVD-152327,sites,SITE-001758,address,"street_address 218 S. Thomas Rd., Tallmadge, OH; own-page ZIP 44278",own_site,https://vinylleatherrepair.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 79a1d8c4e9432dd492dd6755f47e9eb9c78fd2794563fbab4b11f1bffc144e24; quote: 218 S. Thomas Rd. Tallmadge OH 44278. County, county_source, ZIP and record tier unchanged."
EVD-152328,sites,SITE-001770,address,"street_address 1070 Faultless Dr, Ashland, OH; own-page ZIP 44805",own_site,https://novatex.us/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 d9df67569fe802c6614072c46de82c4cd362ef389ca5fa5d3566327a6016072a; quote: 1070 Faultless Dr, Ashland, OH 44805. County, county_source, ZIP and record tier unchanged."
EVD-152330,sites,SITE-001775,address,"street_address 1061 Bradley Road, Westlake, OH; own-page ZIP 44145",own_site,https://aerocaseinc.com/contact.html,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 c697bada7cc41f584269e96efe19cc724bb3cdf6522e41231bd63ffea0efb5cf; quote: 1061 Bradley Road, Westlake Ohio 44145. County, county_source, ZIP and record tier unchanged."
EVD-152331,sites,SITE-001776,address,"street_address 60 South Park Street, Bedford, OH; own-page ZIP 44146",own_site,http://www.haradhesive.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 efd33a0f9acecdc944f1c0c7ed5855cd523c048bb355d7a5ed025bbbef46a2c6; quote: 60 South Park Street, Bedford, OH 44146. County, county_source, ZIP and record tier unchanged."
EVD-152334,sites,SITE-001780,address,"street_address 3600 Ridge Road, Cleveland, OH; own-page ZIP 44102",own_site,https://vpdcorp.net,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 1e38d2c887a21e9d27b71ff6e8e1998e6b47cce72bc0f1a36a094a4c07c2550e; quote: 3600 Ridge Road Cleveland, Ohio 44102. County, county_source, ZIP and record tier unchanged."
EVD-152335,sites,SITE-001783,address,"street_address 1000 Bacon Road, Painesville, OH; own-page ZIP 44077",own_site,https://dynaflexinc.com,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 997d092f0eeefe89d6eb988ce6f0ba8ed632998e18fe2d26de35213833527e04; quote: 1000 Bacon Road, Painesville, OH 44077. County, county_source, ZIP and record tier unchanged."
EVD-152341,sites,SITE-001796,address,"street_address 3001 Superior Ave., Cleveland, OH; own-page ZIP 44114",own_site,https://sunartdecals.com,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 549d2dc90aa02fbb9cf97a65bcac2d06936a96b631f092d6a1e89bb98b0cb76e; quote: 3001 Superior Ave., Cleveland, Ohio 44114. County, county_source, ZIP and record tier unchanged."
EVD-152343,sites,SITE-001799,address,"street_address 472 Industrial Parkway, Sandusky, OH; own-page ZIP 44870",own_site,https://pntproducts.com/contact/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 57aa882ab6136a655346e83c475559522a5a2cd142a68ccbfc622fa18ec2c6b2; quote: 472 Industrial Parkway Sandusky, OH 44870. County, county_source, ZIP and record tier unchanged."
EVD-152351,sites,SITE-001831,address,"street_address 370 Lake Road, Medina, OH; own-page ZIP 44256",own_site,http://www.medinarecycling.com/,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 99532154e351a9c5d57389e5385a8e09046a42c378e69057a6672b26236e4c0f; quote: 370 Lake Road Medina, Ohio 44256. County, county_source, ZIP and record tier unchanged."
EVD-152358,sites,SITE-001843,address,"street_address 4529 Industrial Parkway, Cleveland, OH; own-page ZIP 44135",own_site,https://pioneerathletics.com,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 691e1b081509828a8d577b43eb9994bacf6dc0c375a36ac01ae75f64247b7bd9; quote: 4529 Industrial Parkway Cleveland, OH 44135. County, county_source, ZIP and record tier unchanged."
EVD-152359,sites,SITE-001846,address,"street_address 2915 Industrial Pk Dr, Austinburg, OH; own-page ZIP 44010",own_site,https://dalinmold.com,2026-11-06,supports_A,atlas-L2-oh-address-6,"Raw checked 2026-11-06; SHA-256 450384a879fd8be9cc9ae6454737762927270e3aefa304026e73583cba1d97f3; quote: 2915 Industrial Pk Dr Austinburg, OH 44010. County, county_source, ZIP and record tier unchanged."

FILE verdicts.csv
site_id,verdict,street_address,evidence_id,reason
SITE-001640,VERIFIED,1022 Heyl Rd,EVD-152260,
SITE-001647,VERIFIED,9520 Midwest Avenue,EVD-152261,
SITE-001648,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001649,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001650,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001651,STILL_UNCERTAIN,3751 Jennings Road,,own-page street blocks disagree
SITE-001652,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001654,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001655,VERIFIED,2029 Aetna Rd,EVD-152268,
SITE-001656,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001657,VERIFIED,12621 Chardon Windsor Road,EVD-152270,
SITE-001658,VERIFIED,852 West Main St.,EVD-152271,
SITE-001659,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001660,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001661,STILL_UNCERTAIN,485 Kenmore Boulevard,,notes address conflicts; dated adjudication needed
SITE-001662,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001663,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001664,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001665,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001666,VERIFIED,125 Pelret Industrial Parkway,EVD-152279,
SITE-001667,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001668,VERIFIED,4223 East 49th Street,EVD-152281,
SITE-001669,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001670,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001671,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001672,VERIFIED,1400 Valley Belt Road,EVD-152285,
SITE-001674,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001675,VERIFIED,1215 Valley Belt Road,EVD-152287,
SITE-001680,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001682,VERIFIED,4560 Darrow Road,EVD-152289,
SITE-001688,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001690,STILL_UNCERTAIN,310 Quadral Drive,,notes address conflicts; dated adjudication needed
SITE-001693,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001694,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001695,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001702,VERIFIED,1244 Home Ave,EVD-152295,
SITE-001703,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001707,VERIFIED,7154 State Route 88,EVD-152297,
SITE-001708,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001709,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001710,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001712,VERIFIED,41520 Schaden Road,EVD-152301,
SITE-001714,VERIFIED,2906 Nationwide Pkwy,EVD-152302,
SITE-001715,STILL_UNCERTAIN,16090 Industrial Parkway,,notes address conflicts; dated adjudication needed
SITE-001716,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001717,VERIFIED,7675 Jenther Dr,EVD-152305,
SITE-001718,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001719,VERIFIED,2900 Industrial Park Drive,EVD-152307,
SITE-001721,VERIFIED,10008 State Route 43,EVD-152308,
SITE-001722,VERIFIED,2345 E. 28th St.,EVD-152309,
SITE-001723,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001725,STILL_UNCERTAIN,1501 West 47th Street,,notes address conflicts; dated adjudication needed
SITE-001729,VERIFIED,36650 Reading Ave.,EVD-152312,
SITE-001731,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001732,VERIFIED,1025 Evans Ave,EVD-152314,
SITE-001733,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001741,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001742,VERIFIED,1500 Commerce Drive,EVD-152317,
SITE-001743,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001744,VERIFIED,75 N. Pleasant St,EVD-152319,
SITE-001746,VERIFIED,34355 Melinz Parkway,EVD-152320,
SITE-001747,VERIFIED,300 Morning Star Drive,EVD-152321,
SITE-001748,VERIFIED,4494 Orchard Street,EVD-152322,
SITE-001754,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001755,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001756,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001757,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001758,VERIFIED,218 S. Thomas Rd.,EVD-152327,
SITE-001770,VERIFIED,1070 Faultless Dr,EVD-152328,
SITE-001774,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001775,VERIFIED,1061 Bradley Road,EVD-152330,
SITE-001776,VERIFIED,60 South Park Street,EVD-152331,
SITE-001777,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001779,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001780,VERIFIED,3600 Ridge Road,EVD-152334,
SITE-001783,VERIFIED,1000 Bacon Road,EVD-152335,
SITE-001785,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001786,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001790,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001791,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001793,STILL_UNCERTAIN,18222 LANKEN AVE.,,own-page ZIP conflicts with current site ZIP
SITE-001796,VERIFIED,3001 Superior Ave.,EVD-152341,
SITE-001798,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001799,VERIFIED,472 Industrial Parkway,EVD-152343,
SITE-001800,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001801,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001804,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001806,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001807,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001815,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001820,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001831,VERIFIED,370 Lake Road,EVD-152351,
SITE-001833,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001834,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001836,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001837,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001840,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001842,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001843,VERIFIED,4529 Industrial Parkway,EVD-152358,
SITE-001846,VERIFIED,2915 Industrial Pk Dr,EVD-152359,

FILE audit.csv
site_id,source_ref,sha256,result,error
SITE-001657,https://hitechextrusions.com/,f4de98a83ed02ef058c4d400148dce6521826ee4029e6a893572a421d1be8d05,PASS,
SITE-001666,https://crgiconnect.com/,447916b0735c8c86a4a855b75a560259b9b2943a40ce6a5a21bb04af12ba7138,PASS,
SITE-001675,https://speedlinepvc.com/,2ac7d8447b11607573b44fcd69d1ee049080af1264ef1be436e099651edeed49,PASS,
SITE-001719,http://rtscompaniesinc.com/,3e9c71c0c49a8ec27c3fa628959896af41359e364fcd95d40efdaad5d7fd72e7,PASS,
SITE-001640,https://prc-saltillo.com/contact,12f022e096a70fc7addf8277d9ae0325bb62f6b163f617e2365d8c6f8e62b3e7,PASS,
SITE-001732,https://clearsonic.com/pages/contact,2a8612e677fff7e563065cca0c2663ab07f97df9a46d07606b9cd5ea9b2bfe42,PASS,
SITE-001775,https://aerocaseinc.com/contact.html,c697bada7cc41f584269e96efe19cc724bb3cdf6522e41231bd63ffea0efb5cf,PASS,
SITE-001702,https://www.akronbelting.com/,74a46b3abb14f89efd158140539d26cba0f5313886eb34ab189ff0660df493ac,PASS,
SITE-001712,http://plastic-enterprises.com,d5f0d57578c8c6ed18d4052a83a931f2f516fa216bb30dc8b5aa5a89e881d79e,PASS,
SITE-001831,http://www.medinarecycling.com/,99532154e351a9c5d57389e5385a8e09046a42c378e69057a6672b26236e4c0f,PASS,
SITE-001744,https://durablecorp.com/,5800475bf530d24c744a5f49fac122498d68e2af64ae6828d7323dd314f51148,PASS,
SITE-001796,https://sunartdecals.com,cd588c0607f31840966c39db1242241600f54cb66472a356b46ef5fc2d4c299d,PASS,
SITE-001742,https://drossbach.com/,574fae521f2e433803fc42868e42c313013c1068ddaf420fdbe97cff677d92ab,PASS,
SITE-001748,https://flashitllc.com/contact/,472d4fb7890eefbe26aea6b58d8595a1eda09ff4385ec54a3f14a074924e392f,PASS,
SITE-001846,https://dalinmold.com,450384a879fd8be9cc9ae6454737762927270e3aefa304026e73583cba1d97f3,PASS,
SITE-001668,https://gatewayrecycle.com/locations/,73934bab0a94652803f33c33f7d14dbca1fb4530c30622f04ded1b4475c63de1,PASS,
SITE-001770,https://novatex.us/,d9df67569fe802c6614072c46de82c4cd362ef389ca5fa5d3566327a6016072a,PASS,
SITE-001658,https://jos-tech.com/,5bd00f990a05a80c7b876f3e33874e91636c99418df15cfd4423571f5f4ea30c,PASS,
SITE-001843,https://pioneerathletics.com,666a35e561dcce9c741488b49c0de63aa89fbe2bffe8cd1d6bca2468d85c3191,PASS,
SITE-001682,https://mactac.com/ContactUs,d599b8ebd6262077276da80beedc01edf0c9840c9f2d2a33406aaacf1c0e5b92,PASS,
SITE-001729,https://brunsbrush.com/,e88aabb060a24381b3eaf1243b05b07e1caf0b4d46a71627049d66e164b51933,PASS,
SITE-001722,http://www.vaprocessinc.com/contact,1d2bbf3a9534094e1d03255bfbc5eb52de1400a28963e3fd10aacf0f9b6ef014,PASS,
SITE-001776,http://www.haradhesive.com/,efd33a0f9acecdc944f1c0c7ed5855cd523c048bb355d7a5ed025bbbef46a2c6,PASS,
SITE-001746,https://enpac.com/,0ee8ee27535582474d0c665dbec7841b767f4bb85f58049decb48b4fc2fbe0f6,PASS,
SITE-001758,https://vinylleatherrepair.com/,42092069b4e852ed164790b1abbacef456f9bb076a1b89acb2cc43af4547f570,PASS,
SITE-001783,https://dynaflexinc.com,997d092f0eeefe89d6eb988ce6f0ba8ed632998e18fe2d26de35213833527e04,PASS,
SITE-001780,https://vpdcorp.net,1e38d2c887a21e9d27b71ff6e8e1998e6b47cce72bc0f1a36a094a4c07c2550e,PASS,
SITE-001647,https://aabacoplastics.com/,2928771c1990ea31cc6737b82ba12c6c3c03378eb95c6e26358a4515adca7779,PASS,
SITE-001672,https://northshorestrapping.com/,976c8989fdb2432a620719ea5a452c639cc0626878101ad1559cd6e880864f2b,PASS,
SITE-001747,https://fastforming.com/,4c6d389eadaa7f2e0d25aeb2323b7c453e9014ee119fd244c2ebdc3e5e448420,PASS,

FILE notes_regression.csv
site_id,own_street,old_note_values,new_note_values,result
SITE-001640,1022 Heyl Rd,1022 Heyl Rd (per the operator's own site / wave-2 verdict W2-026 evidence),1022 Heyl Rd,false provenance-tail veto reproduced and fixed
SITE-001666,125 Pelret Industrial Parkway,125 Pelret Industrial Pkwy (per wave-3 verdict W3-0166 evidence; own-site spelling 'Pelret'). Ecosystem org ORG-001594 — FK resolves in ecosystem.csv,125 Pelret Industrial Pkwy,false provenance-tail veto reproduced and fixed
SITE-001843,4529 Industrial Parkway,"4529 Industrial Pkwy. Filing basis: Check RUN and POSITIVE: main-form filings PY2022-PY2024 at the exact address under the candidate's own legal name (the matcher's ADDR_ONLY class is an artifact of the leading 'THE' in the staged name), business code 325500 (paint and coating manufacturing) cor…",4529 Industrial Pkwy,false provenance-tail veto reproduced and fixed

AUDIT SUMMARY
{
  "accepted_fills": 36,
  "audited": 30,
  "errors": 0
}
