#!/usr/bin/env python3
"""Exact frozen merged census, source and five-claim strength, preservation and no-write faults."""
import argparse,copy,csv,hashlib,io,json,shutil,subprocess,sys,tempfile
from pathlib import Path
from build import H,ROOT,read,witness,require_five,raw,BY,CLAIMS
ap=argparse.ArgumentParser();ap.add_argument('--negative-controls',action='store_true');a=ap.parse_args()
base=json.loads((H/'baseline.json').read_text());integration=base['commit'];freeze=base['frame_commit'];frame=read(H/'input.csv');vs=read(H/'verdicts.csv');sel=json.loads((H/'selected.json').read_text());chosen={r['site_id']:r for r in sel}
assert len(frame)==len(vs)==len({r['site_id'] for r in vs})==15 and {r['site_id'] for r in frame}=={r['site_id'] for r in vs}
assert sum(r['verdict']=='VERIFIED' for r in vs)==6 and sum(r['verdict']=='STILL_UNCERTAIN' for r in vs)==9
frozen=[]
for path in subprocess.check_output(['git','ls-tree','-r','--name-only',freeze,'data/'],cwd=ROOT,text=True).splitlines():
 if path.startswith('data/sites_') and path.endswith('.csv'):
  frozen.extend(r for r in csv.DictReader(io.StringIO(subprocess.check_output(['git','show',freeze+':'+path],cwd=ROOT,text=True))) if r['verification_tier']=='C' and r['created_by'] in {'atlas-L3-corroborated-mn','atlas-L3-corroborated-nj'})
assert {r['site_id']:r for r in frozen}=={r['site_id']:r for r in frame},'under-returned merged C frame'
sites={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)};orgs={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)};slots={r['site_id']:n for n,r in enumerate(frame)}
for i in frame:
 now=sites[i['site_id']];diff={k for k in i if i[k]!=now[k]}
 if i['site_id'] in chosen:
  assert diff=={'verification_tier','sources','notes'} and now['verification_tier']=='B' and now['operating_status']=='unknown'
  r=chosen[i['site_id']];text=witness(r,orgs[i['org_id']]);assert not raw.contains(text,r['quote']+' fabricatedplantproof7731')
 else:assert not diff,('held site changed',i['site_id'])
paths=subprocess.check_output(['git','diff','--name-only',integration,'--','data/'],cwd=ROOT,text=True).splitlines();assert set(paths)=={f'data/{p}_{st}.csv' for p in ['sites','evidence_sites'] for st in ['MN','NJ']},paths
new=[]
for path in paths:
 prior=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',integration+':'+path],cwd=ROOT,text=True))));now=read(ROOT/path);key=list(prior[0])[0];by={r[key]:r for r in now};assert len(by)==len(now)
 for r in prior:
  assert r[key] in by,('old row lost',path,r[key])
  if r[key] not in chosen:assert by[r[key]]==r,('old row edited',path,r[key])
 if key=='site_id':assert len(prior)==len(now)
 else:have={r[key] for r in prior};new.extend(r for r in now if r[key] not in have)
assert len(new)==30 and {r['evidence_id'] for r in new}=={f'EVD-{304100+slots[sid]*6+n:06d}' for sid in chosen for n in range(5)}
for sid,r in chosen.items():
 rows=[e for e in new if e['record_id']==sid];assert len(rows)==5;require_five(rows)
 assert all(e['tier_effect']=='supports_B' and e['created_by']==BY and e['record_table']=='sites' for e in rows)
 for e in rows:
  if e['claim_type']=='scope':assert e['source_class']=='own_site' and e['claim_detail']==r['quote'] and e['source_ref']==r['source_url'] and e['observed_date']==(r['source_date'] or '2026-11-06')
  else:assert e['source_class']=='government_filing' and e['observed_date']=='2026-11-01' and '#establishment_ID=' in e['source_ref']
 for claim in CLAIMS:
  try:require_five([e for e in rows if e['claim_type']!=claim])
  except AssertionError:pass
  else:raise AssertionError(('missing mandatory claim accepted',sid,claim))
receipts=json.loads((H/'holds-sources.json').read_text());assert {r['site_id'] for r in receipts}=={r['site_id'] for r in vs if r['verdict']=='STILL_UNCERTAIN'}
def hold_receipt(r):
 p=Path(r['raw_text_path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'] and raw.contains(p.read_text(),r['quote']),'hold quote/source mismatch'
for r in receipts:hold_receipt(r);assert not raw.contains(Path(r['raw_text_path']).read_text(),r['quote']+' fabricatedholdproof7731')
bad=copy.deepcopy(receipts[0]);bad['quote']+=' fabricatedholdproof7731'
try:hold_receipt(bad)
except AssertionError:pass
else:raise AssertionError('fabricated hold quote accepted')
if a.negative_controls:
 with tempfile.TemporaryDirectory() as d:
  root=Path(d);data=root/'data';shutil.copytree(ROOT/'data',data);packet=root/'tasks'/H.name;packet.parent.mkdir();shutil.copytree(H,packet);(root/'scripts').symlink_to(ROOT/'scripts',target_is_directory=True)
  for name in ['osha-ita-2026-11-01','strong-waves-mo-sc-la-2026-11-06','evidence-repair-2-2026-11-04']:(packet.parent/name).symlink_to(ROOT/'tasks'/name,target_is_directory=True)
  def fail(needle):
   hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')};run=subprocess.run([sys.executable,str(packet/'build.py'),'--data-dir',str(data),'--apply'],capture_output=True,text=True)
   assert run.returncode and needle in run.stderr,run.stderr;assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
  p=data/'evidence_sites_AL.csv';orig=p.read_bytes();rows=read(p)
  with p.open('a',newline='') as f:csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n').writerow({**rows[0],'evidence_id':new[0]['evidence_id']})
  fail('duplicate EVD ID');p.write_bytes(orig)
  p=packet/'selected.json'
  for field,value,needle in [('quote',sel[0]['quote']+' fabricatedplantproof7731','scope/city/binding quote absent'),('city_quote','Wrong City 7731','scope/city/binding quote absent'),('issuer_quote','Unrelated Company 7731','visible issuer absent'),('page_sha256','0'*64,'source text hash changed')]:
   bad=copy.deepcopy(sel);bad[0][field]=value;p.write_text(json.dumps(bad));fail(needle)
  bad=copy.deepcopy(sel);bad[0]['source_url']='https://unrelated.invalid/plant';p.write_text(json.dumps(bad));fail('source URL receipt mismatch')
  bad=copy.deepcopy(sel);next(r for r in bad if r['site_id']=='SITE-012700')['city_quote']='Clearwater';p.write_text(json.dumps(bad));fail('city does not name frozen plant')
print('PASS15 merged-only sites/6C→B9holds/30B evidence/30missing-claim mutations/6raw+negative/sourceissuer/oldrowpreservation/exact4files18cells;7beforewritefaults(ifrequested)')
