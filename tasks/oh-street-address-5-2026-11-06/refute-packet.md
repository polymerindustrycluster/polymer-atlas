Adversarial completion refute L2 Ohio round5. NEWbranch agent/codex/oh-street-address-5, exact original448frame positions161–260/IDs152160–152259, offcurrentmain thenmerged171. EndVERDICT:APPROVE/REFUTE with demonstrated findings; readonly,nomerge.
Frame448=160prior+100worked+188future.100activeblankstoredPIC18A/Bownwebsite rows refreshedBEFOREfetch.203attempts=168fetched35unavailable;100siteIDsreconciled,39rawaddresssites.25VERIFIED/75STILL_UNCERTAIN.25street/source-only edits+25append-only own_site/address/supports_AEVD152161–152256,recordtiersA10/B15unchanged. Noentities/geography/ZIP/tier/status/ring/registry/derivedchanges, no inclusion-logcalls. Coverage324/1883→349/1883(17.21→18.53%),excludespending15619+19224. Sourcepriorityonlyrawheld-operatorpages,hostredirectbinding,physicalstreetcityZIP,actualby-mail/mail/postal/emailnegative gate. Noquotescomposedfromnotes.
Predeclared site-grain guard catches5WRONGHQaddresses: ShinEtsu963/1030Evansrecords onlyfind1150Damar;Steere487Commerce/350Tacoma/303Tacomarecords onlyfind285Commerce. Sameoperatorcity/ZIP peers+noboundstreetlead→HOLD,notrootcontactguess. These5 assertedinthecheck. Actualsource nofalseinferenceofclosure.
Noteparserinitiallyfalse-vetoed city/state/ZIP/sourceannotationsasstreetstrings (3positives); fixedstructuralboundaries BEFOREcanonicalapply, same100rows/sources. notes_regression.csv reproducesoldfalseveto3cases;7fixtures isolateStreetfromCity/provenancewhilePRESERVINGunitSuite100≠300. TrueBauer1505Bowmanvs2540Progress,S4suite/direction,ChalfantZIPconflictsSTILLHOLD (asserted). Nochangedcountunit,source/tierpolicyorpositivecherry-picking. Lexicalnormalizationonlyordinarysuffix/directionaliases.
Groundtruth: known3LIVEaddresses beforefetch+wrongcity/PObox/phoneprefixPASS; check.py25fills,boundary/idempotence,actualby-mail&notes&5grain+3realconflictfixtures,street/foreignEVD-beforewritemutationsPASS; full25/25acceptedfreshquotecensus0errors(population<30); validate.py0errors,diffcheckPASS; mainkeycomparisonallkeys/legacyevidencepreserved25edits25appends. No scripts/changes. Currentstructuredactiveaddresskeyscan0otherhits; noentitymerge.
Potentialfailures: parserstripsrealunit/overridestrueconflict; genericHQstilltreatedasplant; sourcephysicalvsbymail; sourceoperator/sitecontextwrong; quote/hash/cityZIPbinding; IDcollision/legacyrowloss/rebase; partialsourceyield; treatingunavailableasabsence. Challengeexactdata.
Reference-only Polynew3557StateRte93BalticCensusaddress-exactcountyTuscarawas agreesstoredcounty;3literalcountyknownanswersfirstPASS. RawJSON/CSVin taskfolder; no coords/county/tierusedasnewcanonicaldata. ThisgeographiccheckisNOTaddresswitness/tierpromotion.
Onlyextra171READMEapprovalreceipt: controller merged reviewed7af4219 atd9527fe beforeworker couldrecordboth independentAPPROVEs. No171data/code ridesR5. BothCodex2/Grok2independentlyrawchecked38canonical sources+namedchecks, receiptnotesaddedtomergeREADME. Source/taskdata hereonlyR5. Older156/192remainunderreviewandtakepriority.
Commands: python3 tasks/oh-street-address-5-2026-11-06/check.py; python3 scripts/validate.py; python3 tasks/oh-street-address-5-2026-11-06/audit.py; fetch.py --known (network). Full448frame,rawchecks,203pagechecks,100verdicts,75holds,journalandnotesregressionskept. Belowallcode+100compactinputs+25witnesses+100verdicts+25audit. Inspectfullnotesinframewhenbindingunclear.

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
 aliases={'STREET':'ST','ROAD':'RD','AVENUE':'AVE','DRIVE':'DR','COURT':'CT','PARKWAY':'PKWY','BOULEVARD':'BLVD','PLACE':'PL','WEST':'W','EAST':'E','NORTH':'N','SOUTH':'S'}
 return ' '.join(aliases.get(t,t) for t in re.findall('[A-Z0-9]+',v.upper()))
def note_streets(s):
 out=[x[0] for x in extract(s['notes'],s['city'])]
 m=re.search(r'(?i)\bstreet(?:\s*\([^)]*\))?:\s*(.+)',s['notes'])
 if m:
  value=re.split(r'\.\s+(?=PASS|BAND|CERT|Ring|INTEGRATION|Parcel|Re-pointed|NAICS|Source|Address confirmed|Co-located|Converted|(?i:county UNVERIFIED)|\[)',m[1])[0]
  value=re.split(r',\s*'+re.escape(s['city'])+r'\b',value,maxsplit=1,flags=re.I)[0]
  value=re.split(r'\s+\((?=(?i:address per|company contact|GS1 manufacturer))',value,maxsplit=1)[0]
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
       source_class='own_site',source_ref=r['url'],observed_date=DATE,tier_effect='supports_A',created_by='atlas-L2-oh-address-5',
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
 summary=dict(eligible_sites=448,prior_batch_sites=160,worked=100,unworked=188,fills=len(ev),holds=100-len(ev),active_ohio_sites=len(active),before_streets=before,after_streets=before+len(ev))
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
  ('Test City','Street: 191 American Blvd, Suite 100, Test City (company contact page)','191 American Blvd, Suite 100')]
 for city,notes,expected in cases:
  leads=build.note_streets(dict(city=city,notes=notes));assert leads and build.key(leads[-1])==build.key(expected),(leads,expected)
 assert build.key(cases[-1][2])!=build.key('191 American Blvd Suite 300'),'unit distinction erased'
 for sid in ('SITE-001316','SITE-001317','SITE-001416','SITE-001417','SITE-001418'):
  row=next(v for v in verdicts if v['site_id']==sid);assert row['verdict']=='STILL_UNCERTAIN' and 'site-specific binding' in row['reason'],sid
 for sid in ('SITE-001419','SITE-001524','SITE-001579'):
  assert next(v for v in verdicts if v['site_id']==sid)['verdict']=='STILL_UNCERTAIN',sid

 assert len(ev)==25,'frozen source-adjudication yield changed; inspect before revising'
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
  build.write(p,[r for r in build.read(p) if r['created_by']!='atlas-L2-oh-address-5'])
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  after=build.read(build.ROOT/'data/sites_OH.csv');changed=0
  assert len(before)==len(after)
  for a,b in zip(before,after):
   fields={k for k in a if a[k]!=b[k]}
   assert fields <= {'street_address','sources'},(a['site_id'],fields)
   if fields:
    changed+=1;assert not a['street_address'] and b['street_address'] and a['operating_status']=='active'
  assert changed==25
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

INPUT siteID|orgID|siteName|city|ZIP|county|tier|website|parsedStreetLeads
SITE-000648|ORG-000608|Tomlinson 1880 — Parma|Parma|44130|Cuyahoga|A|https://www.tomlinson1880.com/|['11699 Brookpark Road, Unit 500']
SITE-000667|ORG-000626|Vinylume Products, Inc. — Youngstown|Youngstown|44515|Mahoning|B|https://www.vinylume.com/|['3745 Hendricks Road', '3745 Hendricks Rd', '3745 Hendricks Road']
SITE-000676|ORG-000635|THE WOOSTER BRUSH COMPANY — Wooster|Wooster|44691|Wayne|B|https://www.woosterbrush.com/|['604 Madison Avenue', '604 Madison Avenue', '604 Madison Avenue']
SITE-000677|ORG-000636|Wrap Tite - Site 1|Solon|44139|Cuyahoga|A|https://www.wraptite.com/|['6200 Cochran Rd.', '6200 Cochran Rd']
SITE-000678|ORG-000636|Wrap Tite - Site 3|Solon|44139|Cuyahoga|A|https://www.wraptite.com/|['6075 Cochran Road', '6250 Camp Industrial Road', '6250 Camp Industrial Rd']
SITE-000680|ORG-000638|Yokohama Industries Americas Ohio|Painesville|44077|Lake|A|https://www.yokohamaiaohio.com/|['474 Newell St', '474 Newell St']
SITE-000683|ORG-000640|Zehrco-Giancola Composites — Ashtabula|Ashtabula|44004|Ashtabula|A|https://zehrco-giancola.com/|['1501 West 47th Street', '1501 West 47th Street']
SITE-000717|ORG-000666|American Colors Inc. — Sandusky|Sandusky|44870|Erie|A|https://www.americancolors.com/|['1110 Edgewater Ave']
SITE-000755|ORG-000697|BALL BOUNCE AND SPORT, INC. — Ashland|Ashland|44805|Ashland|B|https://hedstrom.com/|['2040 Cellar Drive']
SITE-000788|ORG-000728|Charter Next Generation - Ontario|Ontario|44906|Richland|A|https://cnginc.com/|['2355 W 4th Street. Verification wave 2 (2026-10-28): verified; tier U → packet tier']
SITE-000789|ORG-000728|Charter Next Generation — Lexington Campus|Lexington|44904|Richland|A|https://cnginc.com/|["230 Industrial Dr. Verification wave 2 (2026-10-28): verified; tier C → packet tier. Wave-2: site renamed from pre-2020 predecessor 'Next Generation Films, Inc.' (Charter NEX merged with Next Generation Films in 2020 to form Charter Next Generation); predecessor name retained in org trade_names"]
SITE-000864|ORG-000799|Dover High Performance Plastics — Dover|Dover|44622|Tuscarawas|A|https://dhpp.net/|['140 Williams Drive. Verification wave 2 (2026-10-28): verified; tier C → packet tier']
SITE-000879|ORG-000813|Edge Plastics — Mansfield|Mansfield|44902|Richland|B|https://edgeplasticsinc.com/|['449 Newman Street. Verification wave 2 (2026-10-28): verified; tier C → packet tier']
SITE-001125|ORG-001042|Polynew — Baltic|Baltic|43804|Tuscarawas|A|https://polynew.com/|['3557 State Route 93']
SITE-001311|ORG-001330|Finite Fiber — Akron|Akron|44306|Summit|B|https://finitefiber.com/|['1374 Markle Street. County assigned per county-assignments packet (grok-list-2026-10-28/county_assignments.md): Summit (confidence high)']
SITE-001316|ORG-000569|Shin-Etsu Silicones of America, Inc. — 963 Evans Ave|Akron|44305|Summit|A|https://www.shinetsusilicones.com/|[]
SITE-001317|ORG-000569|Shin-Etsu Silicones of America, Inc. — 1030 Evans Ave|Akron|44305|Summit|A|https://www.shinetsusilicones.com/|[]
SITE-001390|ORG-001379|Elyria Plastic Products — Elyria|Elyria|44035|Lorain|A|https://elyriapp.com/|['710 Taylor Street', '710 Taylor Street']
SITE-001394|ORG-000033|LyondellBasell — Fairport Harbor (Equistar)|Fairport Harbor|44077|Lake|B|https://lyondellbasell.com|['110 Third Street. Repo fix 2026-10-28: added from grok-pic12 staged record per verification wave 2 variant sweep (parent already in repo; staged org was ALREADY_IN_REPO — site is the genuinely new establishment)']
SITE-001396|ORG-000176|Kent Elastomer Products — Mogadore|Mogadore|44260|Summit|B|https://kentelastomer.com|['3890 Mogadore Industrial Parkway. Repo fix 2026-10-28: added from grok-pic12 staged record per verification wave 2 variant sweep (parent already in repo; staged org was ALREADY_IN_REPO — site is the genuinely new establishment)', '3890 Mogadore Industrial Pkwy']
SITE-001400|ORG-000188|Universal Polymer & Rubber — Tallmadge|Tallmadge|44278|Summit|A|https://universalpolymer.com|['165 Northeast Avenue']
SITE-001416|ORG-000588|Steere Enterprises — Tallmadge (487 Commerce St)|Tallmadge|44278|Summit|A|https://www.steere.com/|[]
SITE-001417|ORG-000588|Steere Enterprises — Tallmadge (350 Tacoma Ave)|Tallmadge|44278|Summit|A|https://www.steere.com/|[]
SITE-001418|ORG-000588|Steere Enterprises — Tallmadge (303 Tacoma Ave)|Tallmadge|44278|Summit|A|https://www.steere.com/|[]
SITE-001419|ORG-001380|Bauer Corporation — Wooster|Wooster|44691|Wayne|B|https://bauerladder.com/|['1505 E BOWMAN ST', '2540 Progress Drive', '1505 E BOWMAN ST']
SITE-001420|ORG-001381|Hyload Inc. — Wadsworth|Wadsworth|44281|Medina|B|https://www.hyload.com/|['9976 RITTMAN RD', '9976 RITTMAN RD']
SITE-001421|ORG-001382|SR Products — Struthers|Struthers|44471|Mahoning|B|https://www.simon-products.com/|['276 State Street']
SITE-001423|ORG-001384|Sterilite Corporation — Massillon|Massillon||Stark|B|https://www.sterilite.com/|['4495 Sterilite St SE']
SITE-001424|ORG-001385|Aexcel Corp. — Mentor|Mentor|44060|Lake|A|https://www.aexcelcorp.com/|['7373 Production Drive']
SITE-001425|ORG-001386|Ergomat Inc. — Lorain|Lorain|44053|Lorain|B|https://www.ergomat.com/|['7395 Industrial Parkway Dr']
SITE-001426|ORG-001387|Etched Metal — Solon|Solon|44139|Cuyahoga|A|https://etched-metal.com/|['30200 Solon Industrial Parkway']
SITE-001427|ORG-001388|Hy-Ko Products Company — Northfield|Northfield|44067|Summit|B|https://www.hy-ko.com/|['60 Meadow Lane']
SITE-001428|ORG-001389|IML Containers Ohio — Alliance|Alliance||Stark|B|https://imlcontainer.com/|['2455 West Main St']
SITE-001429|ORG-001390|Interpak, Inc. — Mentor|Mentor|44060|Lake|B|https://www.rotomold.com/|['7278 Justin Way']
SITE-001431|ORG-001392|Kalcor Coatings Company — Willoughby|Willoughby|44094|Lake|B|https://www.kalcor.com/|['37721 Stevens Blvd']
SITE-001432|ORG-000002|Lubrizol Advanced Materials — Brecksville|Brecksville|44141|Cuyahoga|B|https://www.lubrizol.com|['9911 Brecksville Road']
SITE-001433|ORG-000684|ASK Chemicals — Cleveland West|Cleveland||Cuyahoga|B|https://www.ask-chemicals.com/|['2191 West 110th Street']
SITE-001434|ORG-000684|ASK Chemicals — Cuyahoga Heights|Cuyahoga Heights||Cuyahoga|B|https://www.ask-chemicals.com/|['4600 East 71st Street']
SITE-001435|ORG-000665|Amcor — Aurora (PVC Stretch Film)|Aurora||Portage|B|https://www.amcor.com/|['1450 S Chillicothe Rd']
SITE-001436|ORG-001393|Kaufman Container — Cleveland|Cleveland|44135|Cuyahoga|B|https://www.kaufmancontainer.com/|['1000 Keystone Parkway']
SITE-001437|ORG-001394|Kent Displays — Kent|Kent|44240|Portage|B|https://kentdisplays.com/|['343 Portage Blvd']
SITE-001438|ORG-001395|CREO Greenhouse — Mogadore|Mogadore|44260|Summit|B|https://creogroup.com/|['3175 Gilchrist Road']
SITE-001439|ORG-001396|Sure-foot Industries — Cleveland|Cleveland|44130|Cuyahoga|A|https://surefootcorp.com/|['20260 First Avenue']
SITE-001440|ORG-001397|PolyKinetix — Massillon|Massillon|44746|Stark|B|https://polykinetix.com|['240 6TH ST NW']
SITE-001441|ORG-001398|Smithers Medical Products — North Canton|North Canton||Stark|B|https://smithersmedicalproducts.com/|[]
SITE-001449|ORG-001404|Deflecto — Dover|Dover|44622|Tuscarawas|B|https://www.deflecto.com/|['303 Oxford Street']
SITE-001455|ORG-001409|American Bath Group — Salem|Salem|44460|Columbiana|B|https://americanbathgroup.com/|['605 S. ELLSWORTH AVE.', '605 S. ELLSWORTH AVE.']
SITE-001468|ORG-001422|Elster Perfection — Geneva|Geneva||Ashtabula|B|https://process.honeywell.com|['436 N Eagle St']
SITE-001480|ORG-001432|Cell-O-Core — Wadsworth|Wadsworth|44274|Medina|B|https://cellocore.com|['6935 RIDGE RD.', '6935 Ridge Rd', '6935 RIDGE RD.']
SITE-001481|ORG-001433|Extruded Silicone Products — Mogadore|Mogadore||Summit|B|https://esprubber.com|['3300 Gilchrist Road']
SITE-001483|ORG-001435|Meese (MODRoto) — Ashtabula|Ashtabula||Ashtabula|B|https://modroto.com|[]
SITE-001484|ORG-001436|Modern Builders Supply / Polaris — Austintown|Austintown||Mahoning|B|https://www.modernbuilderssupply.com|[]
SITE-001485|ORG-001436|Modern Builders Supply / Polaris — Boardman|Boardman||Mahoning|B|https://www.modernbuilderssupply.com|['45 Karago Ave']
SITE-001487|ORG-001438|Thogus Products — Avon Lake|Avon Lake|44012|Lorain|A|https://www.thogus.com/|['33490 Pin Oak Pkwy']
SITE-001505|ORG-001454|IMCD US — Westlake|Westlake|44145|Cuyahoga|B|https://www.imcdus.com|['2 Equity Way Ste 210']
SITE-001506|ORG-001455|Lamports Filter Media — Cleveland|Cleveland||Cuyahoga|B|https://lamports.com/|['837 E 79th St']
SITE-001511|ORG-001460|Spectrum Dispersions — Ravenna|Ravenna|44266|Portage|B|https://spectrumcustom.com/|['225 West Lake St']
SITE-001512|ORG-001461|Sare Plastics — Alliance|Alliance|44601|Stark|B|https://sareplastics.com|['12240 Rockhill Ave NE']
SITE-001522|ORG-001007|Owens Corning — Tallmadge Technology Center / XPS Plant|Tallmadge||Summit|B|https://www.owenscorning.com/|[]
SITE-001524|ORG-001465|Chalfant Sewing Fabricators — Cleveland|Cleveland|44109|Cuyahoga|B|https://chalfantusa.com/|['11525 Madison Avenue']
SITE-001525|ORG-001466|Henkel — Warrensville Heights (LOCTITE Cleveland plant)|Warrensville Heights|44128|Cuyahoga|A|https://www.henkel-northamerica.com/|['Cranwood Pkwy']
SITE-001529|ORG-000006|Tremco CPG — Cleveland (Miles Ave)|Cleveland|44128|Cuyahoga|B|https://www.rpminc.com|['17610 Miles Ave']
SITE-001534|ORG-001472|ChemMasters — Madison|Madison|44057|Lake|B|https://chemmasters.net/|['300 Edwards St']
SITE-001538|ORG-000132|Sherwin-Williams — Massillon|Massillon|44646|Stark|B|https://www.sherwin-williams.com|['600 Nova Dr SE']
SITE-001539|ORG-001475|ChromaScape — Twinsburg (HQ)|Twinsburg|44087|Summit|B|https://chromascape.com/|['2055 Enterprise Pkwy']
SITE-001543|ORG-001477|Aurora Material Solutions - Streetsboro (HQ & Main Plant)|Streetsboro|44241|Portage|A|https://www.auroramaterialsolutions.com/|['9280 Jefferson Street']
SITE-001546|ORG-001480|ACE Laboratories - Ravenna|Ravenna|44266|Portage|B|https://ace-laboratories.com/|['6800 N Chestnut St Suite C']
SITE-001560|ORG-001494|Allied Machine & Engineering — Dover|Dover||Tuscarawas|A|https://alliedmachine.com/|['120 Deeds Dr']
SITE-001563|ORG-001497|Budzar Industries — Willoughby|Willoughby||Lake|B|https://budzar.com/|['38241 Willoughby Pkwy']
SITE-001567|ORG-001501|Polymer Valley Chemicals — Akron|Akron||Summit|B|https://polymervalleychemicals.com/|[]
SITE-001568|ORG-001504|THEKEN COMPANIES, LLC — Akron|Akron|44306|Summit|B|https://nextsteparthropedix.com/|['1800 Triplett Blvd']
SITE-001570|ORG-001506|ValenSil Technologies, LLC — Avon|Avon|44011|Lorain|A|https://valensil.com/|['34910 Commerce Way']
SITE-001571|ORG-001507|HOYA VISION CARE - CLEVELAND — Berea|Berea|44017|Cuyahoga|A|https://hoyavision.com/|['94 Pelret Industrial Pkwy', '94 PELRET INDUSTRIAL PKWY']
SITE-001573|ORG-001509|Health-Mor, Inc — Brooklyn|Brooklyn|44144|Cuyahoga|B|https://filterqueen.com/|['1 American Way']
SITE-001577|ORG-001513|Coltene/Whaledent Inc. — Cuyahoga Falls|Cuyahoga Falls|44223|Summit|B|https://coltene.com/|['235 Ascot Pkwy']
SITE-001578|ORG-001514|Julius Zorn, Inc. (Juzo USA) — Cuyahoga Falls|Cuyahoga Falls|44223|Summit|B|https://juzousa.com/|['3690 Zorn Drive']
SITE-001579|ORG-001515|S4 Medical Corp — Chagrin Falls|Chagrin Falls|44022|Geauga|A|https://s4medical.com/|['549 E Washington Street', '549 Washington St Ste 8']
SITE-001588|ORG-001523|Centerline Biomedical, Inc. — Warrensville Heights|Warrensville Heights|44128|Cuyahoga|B|https://centerlinebiomedical.com/|['4535 Renaissance Pkwy']
SITE-001589|ORG-001524|Kapp Surgical, Inc. — Cleveland|Cleveland|44128|Cuyahoga|B|https://kappsurgical.com/|['4919 Warrensville Center Rd']
SITE-001590|ORG-001525|SPR Therapeutics, Inc — Cleveland|Cleveland|44122|Cuyahoga|A|https://sprtherapeutics.com/|['22901 Millcreek Blvd.', '22901 Millcreek Blvd Ste 500']
SITE-001591|ORG-001526|Viscus Biologics, LLC — Cleveland|Cleveland|44128|Cuyahoga|A|https://viscusbiologics.com/|['26309 Miles Road']
SITE-001593|ORG-001528|Mabel Dental Lab — Cuyahoga Falls|Cuyahoga Falls|44221|Summit|B|https://mabeldental.com/|['891 Graham Rd Ste C']
SITE-001599|ORG-001534|Zimmer Surgical, Inc. — Dover|Dover|44622|Tuscarawas|B|https://zimmerbiomet.com/|['200 WEST OHIO AVE']
SITE-001603|ORG-001538|Perma Laboratories LLC — Hinckley|Hinckley|44233|Medina|B|https://perma-laboratories.com/|['120 Wakefield Run Blvd']
SITE-001604|ORG-001539|GuidedSMILE LLC — Independence|Independence|44131|Cuyahoga|B|https://guidedsmile.com/|['7100 E. Pleasant Valley Rd']
SITE-001605|ORG-001540|Emergency Products & Research, Inc. — Kent|Kent|44240|Portage|B|https://epandr.com/|['890 West Main Street']
SITE-001606|ORG-001541|AlphaMicron Inc. — Kent|Kent|44240|Portage|A|https://alphamicron.com/|['1950 State Route 59']
SITE-001611|ORG-001546|Earthwalk Orthotics Acquisition Company LLC (Earthwalk Orthotics) — Massillon|Massillon|44646|Stark|A|https://earthwalkorthotics.com/|['500 Vista Ave SE']
SITE-001613|ORG-001548|Frantz Medical Development Ltd. (Frantz Medical Group) — Mentor|Mentor|44060|Lake|B|https://frantzgroup.com/|['7740 Metric Dr']
SITE-001614|ORG-001549|STERIS Corporation — Mentor|Mentor|44060|Lake|B|https://steris.com/|['9325 Pinecone Drive']
SITE-001615|ORG-001549|STERIS Corporation — Mentor|Mentor|44060|Lake|B|https://steris.com/|['6515 Hopkins Rd']
SITE-001616|ORG-001550|United States Endoscopy Group, Inc. (STERIS Endoscopy) — Mentor|Mentor|44060|Lake|B|https://steris.com/|['5976 Heisley Rd']
SITE-001617|ORG-001551|Volk Optical Inc. — Mentor|Mentor|44060|Lake|A|https://volk.com/|['7893 Enterprise Dr']
SITE-001621|ORG-001555|Synapse Biomedical Inc. — Oberlin|Oberlin|44074|Lorain|B|https://synapsebiomedical.com/|['300 Artino Street']
SITE-001622|ORG-001556|FARETEC, Inc. — Painesville|Painesville|44077|Lake|A|https://faretec.com/|['1610 W. Jackson St., No. 6']
SITE-001623|ORG-001557|MatPLUS, LTD — Painesville|Painesville|44077|Lake|B|https://matplusinc.com/|['76 Burton St']
SITE-001629|ORG-001562|Bay Corporation — Westlake|Westlake|44145|Cuyahoga|B|https://baycorporation.com/|['867 Canterbury Rd']
SITE-001630|ORG-001563|SurgTech, Inc. — Westlake|Westlake|44145|Cuyahoga|B|https://surgtech-med.com/|['24600 Center Ridge Road, Suite 195']
SITE-001632|ORG-001565|Automation Plastics Corporation — Aurora|Aurora|44202|Portage|A|http://www.automationplastics.com/|["150 Lena Drive (per the operator's own site / wave-2 verdict W2-002 evidence)"]
SITE-001637|ORG-001570|GHSP — Lexington|Lexington|44904|Richland|B|https://www.ghsp.com/|["345 South Mill Street (per the operator's own site / wave-2 verdict W2-011 evidence)"]
WITNESS evidenceID|siteID|claimDetail|sourceURL|exactQuote+SHA innotes (allclassown_site,effectsupports_A,date2026-11-06)
EVD-152161|SITE-000667|street_address 3745 Hendricks Rd, Youngstown, OH; own-page ZIP 44515|https://www.vinylume.com/|Raw checked 2026-11-06; SHA-256 fff0e1a46da5b2b08a3cfc8c507f2e81f244a97ee91d19566eea856b8f675ddb; quote: 3745 Hendricks Rd Youngstown,OH 44515. County, county_source, ZIP and record tier unchanged.
EVD-152165|SITE-000680|street_address 474 Newell St, Painesville, OH; own-page ZIP 44077|https://www.yokohamaiaohio.com/contact-us|Raw checked 2026-11-06; SHA-256 5b0065d4b9bcea4a8802542615e08c8440f97e270e5b672b999460954c3b14ef; quote: 474 Newell St Painesville, OH 44077. County, county_source, ZIP and record tier unchanged.
EVD-152166|SITE-000683|street_address 1501 West 47th Street, Ashtabula, OH; own-page ZIP 44004|https://zehrco-giancola.com/|Raw checked 2026-11-06; SHA-256 c43fcf56ec135a80dbb1273f49acfb3e58fc0500494dd2e007ad0969389abb62; quote: 1501 West 47th Street, Ashtabula, OH 44004. County, county_source, ZIP and record tier unchanged.
EVD-152168|SITE-000755|street_address 2040 Cellar Drive, Ashland, OH; own-page ZIP 44805|https://hedstrom.com/|Raw checked 2026-11-06; SHA-256 fe15ee8eaf2fc594adab0fd77b01bff96268874dd366a9d1d99cbf83515ea01f; quote: 2040 Cellar Drive Ashland, OH 44805. County, county_source, ZIP and record tier unchanged.
EVD-152173|SITE-001125|street_address 3557 State Route 93, Baltic, OH; own-page ZIP 43804|https://polynew.com/contact.htm|Raw checked 2026-11-06; SHA-256 64f1779a6d833aa1cf4413d3a56801a82c2b61ea07dd1702fddcef1aaf8a4c49; quote: 3557 State Route 93 Baltic, OH 43804. County, county_source, ZIP and record tier unchanged.
EVD-152177|SITE-001390|street_address 710 Taylor Street, Elyria, OH; own-page ZIP 44035|https://elyriapp.com/|Raw checked 2026-11-06; SHA-256 fc8e6b8aff7df48bc8f28ab74d86cc5b32f1dc62577f5dcdc98b4268049ec81a; quote: 710 Taylor Street | Elyria, Ohio 44035. County, county_source, ZIP and record tier unchanged.
EVD-152186|SITE-001421|street_address 276 State St., Struthers, OH; own-page ZIP 44471|https://www.simon-products.com/|Raw checked 2026-11-06; SHA-256 fac2a9dc38daeca3bfacd6505605414bac68cfc180f3852bf3cc2b9d671cf7a5; quote: 276 State St. • Struthers, Ohio 44471. County, county_source, ZIP and record tier unchanged.
EVD-152190|SITE-001426|street_address 30200 Solon Industrial Parkway, Solon, OH; own-page ZIP 44139|https://etched-metal.com/|Raw checked 2026-11-06; SHA-256 4eea8dc0aa61f7771883d9e4ee0bbb5d1b4d9b962a5e70d634ce0312da998018; quote: 30200 Solon Industrial Parkway Solon, OH 44139. County, county_source, ZIP and record tier unchanged.
EVD-152191|SITE-001427|street_address 60 Meadow Lane, Northfield, OH; own-page ZIP 44067-1415|https://www.hy-ko.com/|Raw checked 2026-11-06; SHA-256 5bd7833ffab9b06710c6f2c8510ffd0e8392764df9a2fdce59744e77b9ed9a5b; quote: 60 Meadow Lane Northfield, OH 44067-1415. County, county_source, ZIP and record tier unchanged.
EVD-152193|SITE-001429|street_address 7278 Justin Way, Mentor, OH; own-page ZIP 44060|https://www.rotomold.com/contact.html|Raw checked 2026-11-06; SHA-256 6a75f2be968f5f071ce0d66d7e4b1ef5acaaf28c36a344843ea19d7909f326ca; quote: 7278 Justin Way Mentor, OH 44060. County, county_source, ZIP and record tier unchanged.
EVD-152202|SITE-001439|street_address 20260 First Avenue, Cleveland, OH; own-page ZIP 44130|https://surefootcorp.com/|Raw checked 2026-11-06; SHA-256 c0881b2733c392b6c33b2767816d3cf11669e095434a78dd68efe18bea2dc576; quote: 20260 First Avenue Cleveland, OH 44130. County, county_source, ZIP and record tier unchanged.
EVD-152213|SITE-001487|street_address 33490 Pin Oak Parkway, Avon Lake, OH; own-page ZIP 44012|https://www.thogus.com/|Raw checked 2026-11-06; SHA-256 0640ccce20d7700be078131447bfd5b70f53b8362679b4bbe8a644ef36ccf1b9; quote: 33490 Pin Oak Parkway , Avon Lake Ohio , 44012. County, county_source, ZIP and record tier unchanged.
EVD-152216|SITE-001511|street_address 225 West Lake St, Ravenna, OH; own-page ZIP 44266|https://spectrumcustom.com/|Raw checked 2026-11-06; SHA-256 9ec63bd1c07b6e450d09c44c1959c7d5ed209917f45dc689cdc52f55bbf08f6b; quote: 225 West Lake St Ravenna, OH 44266. County, county_source, ZIP and record tier unchanged.
EVD-152222|SITE-001534|street_address 300 Edwards Street, Madison, OH; own-page ZIP 44057|https://chemmasters.net/|Raw checked 2026-11-06; SHA-256 bde6e5c9f6cf7911dcbf0128fe5f0dfe8bf7d80454ce5a05649221d942b09972; quote: 300 Edwards Street, Madison, Ohio 44057. County, county_source, ZIP and record tier unchanged.
EVD-152225|SITE-001543|street_address 9280 Jefferson St., Streetsboro, OH; own-page ZIP 44241|https://www.auroramaterialsolutions.com/|Raw checked 2026-11-06; SHA-256 fd8c8d0960c0d6d43803ee9955bec5890f4f540a663c5f6a30c08479c8fac6b6; quote: 9280 Jefferson St. Streetsboro, Ohio 44241. County, county_source, ZIP and record tier unchanged.
EVD-152228|SITE-001563|street_address 38241 Willoughby Parkway, Willoughby, OH; own-page ZIP 44094|https://budzar.com/|Raw checked 2026-11-06; SHA-256 ad391b453ddb60bba171482b3e0bbd48a4b49eb8bb64404da6e4667c99ec8310; quote: 38241 Willoughby Parkway Willoughby, OH 44094. County, county_source, ZIP and record tier unchanged.
EVD-152230|SITE-001568|street_address 1800 Triplett Boulevard, Akron, OH; own-page ZIP 44306|https://nextsteparthropedix.com/|Raw checked 2026-11-06; SHA-256 e243e38d0a5f6cb3965ee02b9ec9d4e2b8b9a8235c76be2819a927dd8b43745e; quote: 1800 Triplett Boulevard, Akron, OH, 44306. County, county_source, ZIP and record tier unchanged.
EVD-152231|SITE-001570|street_address 34910 Commerce Way, Avon, OH; own-page ZIP 44011|https://valensil.com/|Raw checked 2026-11-06; SHA-256 f1f4d183b086ce64e07fc8dbc2df77e53a7ea2c270d2533f0455631cd0c9f824; quote: 34910 Commerce Way • Avon, Ohio 44011. County, county_source, ZIP and record tier unchanged.
EVD-152235|SITE-001578|street_address 3690 Zorn Drive, Cuyahoga Falls, OH; own-page ZIP 44223|https://juzousa.com/|Raw checked 2026-11-06; SHA-256 560aca04c5d9ea305277447a9f93493b8a4add8ef2bb248982c5e051d399b790; quote: 3690 Zorn Drive • Cuyahoga Falls, OH 44223. County, county_source, ZIP and record tier unchanged.
EVD-152238|SITE-001589|street_address 4919 Warrensville Center Rd, Cleveland, OH; own-page ZIP 44128|https://kappsurgical.com/contact-us/|Raw checked 2026-11-06; SHA-256 d35cbfecf0f3dd234dd53abb000ccc1b9a71686c68afe6586b4cb8c5542db264; quote: 4919 Warrensville Center Rd Cleveland, Ohio 44128. County, county_source, ZIP and record tier unchanged.
EVD-152248|SITE-001613|street_address 7740 Metric Dr., Mentor, OH; own-page ZIP 44060|https://frantzgroup.com/|Raw checked 2026-11-06; SHA-256 7fa8acd73f8c77ef2f44e12e6c0821a60ceed9d614d53541037050be950c5493; quote: 7740 Metric Dr., Mentor, Ohio 44060. County, county_source, ZIP and record tier unchanged.
EVD-152252|SITE-001617|street_address 7893 Enterprise Dr, Mentor, OH; own-page ZIP 44060|https://volk.com/|Raw checked 2026-11-06; SHA-256 c3b0afff81b1c5204950fd46f55c251664f7f1454092ffa4c73df7cb78bfd180; quote: 7893 Enterprise Dr, Mentor, OH 44060. County, county_source, ZIP and record tier unchanged.
EVD-152253|SITE-001621|street_address 300 Artino St., Oberlin, OH; own-page ZIP 44074|https://synapsebiomedical.com/|Raw checked 2026-11-06; SHA-256 3be597a640ab000d4ff2e35c19eb65d43b22fb655e46d108d573a236cad26392; quote: 300 Artino St., Oberlin, OH 44074. County, county_source, ZIP and record tier unchanged.
EVD-152255|SITE-001623|street_address 76 Burton Street, Painesville, OH; own-page ZIP 44077|https://matplusinc.com/|Raw checked 2026-11-06; SHA-256 6a4d455d9bf8ade6d2bc74139dfb45abe0bdea4d86179c3643813fb64e7a68cb; quote: 76 Burton Street Painesville, OH 44077. County, county_source, ZIP and record tier unchanged.
EVD-152256|SITE-001629|street_address 867 CANTERBURY ROAD, Westlake, OH; own-page ZIP 44145|https://baycorporation.com/contact/where-we-are|Raw checked 2026-11-06; SHA-256 572cd513302b34b75ca1b87ff0389ab5445eec13b07bb02076baf5a0c616e9e1; quote: 867 CANTERBURY ROAD WESTLAKE, OH 44145. County, county_source, ZIP and record tier unchanged.
FILE verdicts.csv
site_id,verdict,street_address,evidence_id,reason
SITE-000648,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000667,VERIFIED,3745 Hendricks Rd,EVD-152161,
SITE-000676,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000677,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000678,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000680,VERIFIED,474 Newell St,EVD-152165,
SITE-000683,VERIFIED,1501 West 47th Street,EVD-152166,
SITE-000717,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000755,VERIFIED,2040 Cellar Drive,EVD-152168,
SITE-000788,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000789,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000864,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-000879,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001125,VERIFIED,3557 State Route 93,EVD-152173,
SITE-001311,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001316,STILL_UNCERTAIN,1150 Damar Drive,,generic corporate address lacks site-specific binding among same-operator city/ZIP records
SITE-001317,STILL_UNCERTAIN,1150 Damar Drive,,generic corporate address lacks site-specific binding among same-operator city/ZIP records
SITE-001390,VERIFIED,710 Taylor Street,EVD-152177,
SITE-001394,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001396,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001400,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001416,STILL_UNCERTAIN,285 Commerce St.,,generic corporate address lacks site-specific binding among same-operator city/ZIP records
SITE-001417,STILL_UNCERTAIN,285 Commerce St.,,generic corporate address lacks site-specific binding among same-operator city/ZIP records
SITE-001418,STILL_UNCERTAIN,285 Commerce St.,,generic corporate address lacks site-specific binding among same-operator city/ZIP records
SITE-001419,STILL_UNCERTAIN,2540 Progress Drive,,notes address conflicts; dated adjudication needed
SITE-001420,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001421,VERIFIED,276 State St.,EVD-152186,
SITE-001423,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001424,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001425,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001426,VERIFIED,30200 Solon Industrial Parkway,EVD-152190,
SITE-001427,VERIFIED,60 Meadow Lane,EVD-152191,
SITE-001428,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001429,VERIFIED,7278 Justin Way,EVD-152193,
SITE-001431,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001432,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001433,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001434,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001435,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001436,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001437,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001438,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001439,VERIFIED,20260 First Avenue,EVD-152202,
SITE-001440,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001441,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001449,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001455,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001468,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001480,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001481,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001483,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001484,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001485,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001487,VERIFIED,33490 Pin Oak Parkway,EVD-152213,
SITE-001505,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001506,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001511,VERIFIED,225 West Lake St,EVD-152216,
SITE-001512,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001522,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001524,STILL_UNCERTAIN,11525 Madison Avenue,,own-page ZIP conflicts with current site ZIP; existing notes name an unresolved ZIP discrepancy; reconcile primary locality first
SITE-001525,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001529,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001534,VERIFIED,300 Edwards Street,EVD-152222,
SITE-001538,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001539,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001543,VERIFIED,9280 Jefferson St.,EVD-152225,
SITE-001546,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001560,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001563,VERIFIED,38241 Willoughby Parkway,EVD-152228,
SITE-001567,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001568,VERIFIED,1800 Triplett Boulevard,EVD-152230,
SITE-001570,VERIFIED,34910 Commerce Way,EVD-152231,
SITE-001571,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001573,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001577,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001578,VERIFIED,3690 Zorn Drive,EVD-152235,
SITE-001579,STILL_UNCERTAIN,549 E Washington Street,,notes address conflicts; dated adjudication needed
SITE-001588,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001589,VERIFIED,4919 Warrensville Center Rd,EVD-152238,
SITE-001590,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001591,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001593,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001599,STILL_UNCERTAIN,200 West Ohio Ave,,mailing-only or ambiguous address context
SITE-001603,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001604,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001605,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001606,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001611,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001613,VERIFIED,7740 Metric Dr.,EVD-152248,
SITE-001614,STILL_UNCERTAIN,5960 Heisley Road,,own-page street blocks disagree; notes address conflicts; dated adjudication needed
SITE-001615,STILL_UNCERTAIN,5960 Heisley Road,,own-page street blocks disagree; notes address conflicts; dated adjudication needed
SITE-001616,STILL_UNCERTAIN,5960 Heisley Road,,own-page street blocks disagree; notes address conflicts; dated adjudication needed
SITE-001617,VERIFIED,7893 Enterprise Dr,EVD-152252,
SITE-001621,VERIFIED,300 Artino St.,EVD-152253,
SITE-001622,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001623,VERIFIED,76 Burton Street,EVD-152255,
SITE-001629,VERIFIED,867 CANTERBURY ROAD,EVD-152256,
SITE-001630,STILL_UNCERTAIN,,,need own-page physical street block at recorded city; no admissible block fetched
SITE-001632,STILL_UNCERTAIN,150 Lena Drive,,notes address conflicts; dated adjudication needed
SITE-001637,STILL_UNCERTAIN,345 S. Mill St,,notes address conflicts; dated adjudication needed

FILE audit.csv
site_id,source_ref,sha256,result,error
SITE-001613,https://frantzgroup.com/,dab9ab1d42f94814fdf390a34445367d03c37070e3c80671b0cfec74fe5e94a9,PASS,
SITE-000680,https://www.yokohamaiaohio.com/contact-us,eabdf5c7aeee46febe052fabf9e6d3fb0e572ad39693d6db567380676649d1aa,PASS,
SITE-000683,https://zehrco-giancola.com/,c43fcf56ec135a80dbb1273f49acfb3e58fc0500494dd2e007ad0969389abb62,PASS,
SITE-001125,https://polynew.com/contact.htm,64f1779a6d833aa1cf4413d3a56801a82c2b61ea07dd1702fddcef1aaf8a4c49,PASS,
SITE-001426,https://etched-metal.com/,4eea8dc0aa61f7771883d9e4ee0bbb5d1b4d9b962a5e70d634ce0312da998018,PASS,
SITE-000667,https://www.vinylume.com/,fff0e1a46da5b2b08a3cfc8c507f2e81f244a97ee91d19566eea856b8f675ddb,PASS,
SITE-001439,https://surefootcorp.com/,c0881b2733c392b6c33b2767816d3cf11669e095434a78dd68efe18bea2dc576,PASS,
SITE-001511,https://spectrumcustom.com/,9ec63bd1c07b6e450d09c44c1959c7d5ed209917f45dc689cdc52f55bbf08f6b,PASS,
SITE-001427,https://www.hy-ko.com/,5bd7833ffab9b06710c6f2c8510ffd0e8392764df9a2fdce59744e77b9ed9a5b,PASS,
SITE-001589,https://kappsurgical.com/contact-us/,017b8a1015bee7a5c8f8a580397ddb0d586a419d65566bd58429e8e1a5e58556,PASS,
SITE-001578,https://juzousa.com/,0e537dec238c78d510a1c8bdfea21dca90ce3569bb7c5f906543c86ce7273053,PASS,
SITE-001563,https://budzar.com/,8ad05c9c72618ace9c91a1083dca4130158920c9b132f42c6894fbf1afa66b52,PASS,
SITE-001623,https://matplusinc.com/,681dc2b86c425fc3fcd0865f0a273ca40a736334dfa8e2b7b00ee5e54ddd2564,PASS,
SITE-000755,https://hedstrom.com/,06a3ac118eed80db3d3b824667654d5453809745d12cccc6b85625fd33078ad4,PASS,
SITE-001617,https://volk.com/,970971259d79cc5f36e043aeff676ed66c954fcb8c3aa7574cb7a4e88a71f88d,PASS,
SITE-001621,https://synapsebiomedical.com/,3be597a640ab000d4ff2e35c19eb65d43b22fb655e46d108d573a236cad26392,PASS,
SITE-001429,https://www.rotomold.com/contact.html,6a75f2be968f5f071ce0d66d7e4b1ef5acaaf28c36a344843ea19d7909f326ca,PASS,
SITE-001543,https://www.auroramaterialsolutions.com/,fd8c8d0960c0d6d43803ee9955bec5890f4f540a663c5f6a30c08479c8fac6b6,PASS,
SITE-001629,https://baycorporation.com/contact/where-we-are,c6445fc54db2417ca4f5be33d828419754a1dc8fdf1c0bf95f4512cceb8b30ee,PASS,
SITE-001570,https://valensil.com/,f1f4d183b086ce64e07fc8dbc2df77e53a7ea2c270d2533f0455631cd0c9f824,PASS,
SITE-001568,https://nextsteparthropedix.com/,e243e38d0a5f6cb3965ee02b9ec9d4e2b8b9a8235c76be2819a927dd8b43745e,PASS,
SITE-001534,https://chemmasters.net/,bde6e5c9f6cf7911dcbf0128fe5f0dfe8bf7d80454ce5a05649221d942b09972,PASS,
SITE-001487,https://www.thogus.com/,0640ccce20d7700be078131447bfd5b70f53b8362679b4bbe8a644ef36ccf1b9,PASS,
SITE-001421,https://www.simon-products.com/,fac2a9dc38daeca3bfacd6505605414bac68cfc180f3852bf3cc2b9d671cf7a5,PASS,
SITE-001390,https://elyriapp.com/,fc8e6b8aff7df48bc8f28ab74d86cc5b32f1dc62577f5dcdc98b4268049ec81a,PASS,

FILE summary.json
{
  "eligible_sites": 448,
  "prior_batch_sites": 160,
  "worked": 100,
  "unworked": 188,
  "fills": 25,
  "holds": 75,
  "active_ohio_sites": 1883,
  "before_streets": 324,
  "after_streets": 349
}

FILE notes_regression.csv
city,notes,expected_street,old_leads,corrected_leads,old_false_veto,corrected_match
Elyria,"Street: 710 Taylor Street, Elyria, OH 44035",710 Taylor Street,"['710 Taylor Street', '710 Taylor Street, Elyria, OH 44035']","['710 Taylor Street', '710 Taylor Street']",yes,yes
Avon,Street: 34910 Commerce Way (address per FDA establishment registration; verified). FDA FEI 123,34910 Commerce Way,['34910 Commerce Way (address per FDA establishment registration; verified). FDA FEI 123'],['34910 Commerce Way'],yes,yes
Youngstown,Street (per Grok): 3745 Hendricks Rd. county UNVERIFIED — Grok county_check=TRUE,3745 Hendricks Rd,['3745 Hendricks Rd. county UNVERIFIED — Grok county_check=TRUE'],['3745 Hendricks Rd'],yes,yes
