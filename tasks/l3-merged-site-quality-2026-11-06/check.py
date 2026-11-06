#!/usr/bin/env python3
"""Merged-frame/weakest-claim/source boundary and fail-before-write quality checks."""
import argparse,copy,csv,hashlib,io,json,shutil,subprocess,sys,tempfile
from pathlib import Path
from build import H,ROOT,read,witness,raw,BY,require_five
ap=argparse.ArgumentParser();ap.add_argument('--negative-controls',action='store_true');a=ap.parse_args()
baseline=json.loads((H/'baseline.json').read_text());base=baseline['commit'];freeze=baseline.get('frame_commit',base);frame=read(H/'input.csv');vs=read(H/'verdicts.csv');sel=json.loads((H/'selected.json').read_text());assert len(frame)==len(vs)==3 and {r['site_id'] for r in frame}=={r['site_id'] for r in vs}
frozen=[]
for path in subprocess.check_output(['git','ls-tree','-r','--name-only',freeze,'data/'],cwd=ROOT,text=True).splitlines():
 if path.startswith('data/sites_') and path.endswith('.csv'):
  frozen.extend(r for r in csv.DictReader(io.StringIO(subprocess.check_output(['git','show',freeze+':'+path],cwd=ROOT,text=True))) if r['verification_tier']=='C' and r['created_by'] in {'atlas-L3-strong-mo-sc-la','atlas-L3-corroborated-mo-sc','atlas-L3-corroborated-la','atlas-L3-corroborated-mn','atlas-L3-corroborated-nj'})
assert {r['site_id']:r for r in frozen}=={r['site_id']:r for r in frame},'under-returned merged frame'
assert sum(r['verdict']=='VERIFIED' for r in vs)==1 and sum(r['verdict']=='STILL_UNCERTAIN' for r in vs)==2
text=witness(sel[0]);bad=copy.deepcopy(sel[0]);bad['quote']+=' fabricatedplantproof7731'
try:witness(bad)
except AssertionError:pass
else:raise AssertionError('fabricated scope accepted')
sites={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)}
for r in frame:
 now=sites[r['site_id']];diff={k for k in r if r[k]!=now[k]}
 if r['site_id']=='SITE-012511':assert diff=={'verification_tier','sources','notes'} and now['verification_tier']=='B' and now['operating_status']=='unknown'
 else:assert not diff,('held site changed',r['site_id'])
paths=subprocess.check_output(['git','diff','--name-only',base,'--','data/'],cwd=ROOT,text=True).splitlines();assert set(paths)=={'data/sites_LA.csv','data/evidence_sites_LA.csv'},paths
new=[]
for path in paths:
 old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',base+':'+path],cwd=ROOT,text=True))));now=read(ROOT/path);key=list(old[0])[0];by={r[key]:r for r in now};assert len(by)==len(now)
 for r in old:
  assert r[key] in by
  if r[key]!='SITE-012511':assert by[r[key]]==r,('old row edited',path,r[key])
 if key=='site_id':assert len(old)==len(now)
 else:have={r[key] for r in old};new=[r for r in now if r[key] not in have]
assert len(new)==5 and {r['evidence_id'] for r in new}=={f'EVD-{n:06d}' for n in range(304012,304017)}
assert {r['claim_type'] for r in new}=={'existence','address','code','parent','scope'} and all(r['tier_effect']=='supports_B' and r['record_id']=='SITE-012511' and r['created_by']==BY for r in new)
for r in new:
 if r['source_class']=='own_site':assert r['claim_type']=='scope' and r['claim_detail']==sel[0]['quote'] and r['observed_date']=='2026-09-23' and r['source_ref']==sel[0]['source_url']
 else:assert r['source_class']=='government_filing' and r['observed_date']=='2026-11-01' and r['source_ref'].endswith('#establishment_ID=192504')
# Complete weakest-claim regression: dropping any of the five observations cannot support B.
for claim in ['existence','address','code','parent','scope']:
 bad=[r for r in new if r['claim_type']!=claim]
 try:require_five(bad)
 except AssertionError:pass
 else:raise AssertionError(('missing B claim accepted',claim))
for r in json.loads((H/'rawcheck.json').read_text()):
 if 'raw_text_path' in r:p=Path(r['raw_text_path']);t=p.read_text()
 else:
  name='home' if r['source_url'].endswith('.com/') else 'about';p=Path('/tmp/l3-quality-watson-'+name+'.html');parser=raw.Text();parser.feed(p.read_text());t=' '.join(parser.parts)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['raw_sha256'] and raw.contains(t,r['quote']) and not raw.contains(t,r['quote']+' fabricatedplantproof7731')
if a.negative_controls:
 with tempfile.TemporaryDirectory() as d:
  root=Path(d);data=root/'data';shutil.copytree(ROOT/'data',data);packet=root/'tasks'/H.name;packet.parent.mkdir();shutil.copytree(H,packet)
  (root/'scripts').symlink_to(ROOT/'scripts',target_is_directory=True)
  for name in ['osha-ita-2026-11-01','strong-waves-mo-sc-la-2026-11-06','evidence-repair-2-2026-11-04']:(packet.parent/name).symlink_to(ROOT/'tasks'/name,target_is_directory=True)
  def fail(needle):
   hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')};run=subprocess.run([sys.executable,str(packet/'build.py'),'--data-dir',str(data),'--apply'],capture_output=True,text=True)
   assert run.returncode and needle in run.stderr,run.stderr;assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
  wrong=data/'evidence_sites_AL.csv';orig=wrong.read_bytes();rows=read(wrong)
  with wrong.open('a',newline='') as f:csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n').writerow({**rows[0],'evidence_id':'EVD-304012'})
  fail('duplicate evidence ID');wrong.write_bytes(orig)
  p=packet/'selected.json';bad=copy.deepcopy(sel);bad[0]['quote']+=' fabricatedplantproof7731';p.write_text(json.dumps(bad));fail('scope quote absent')
  bad=copy.deepcopy(sel);bad[0]['city_quote']='Plastipak - Wrong City';p.write_text(json.dumps(bad));fail('AssertionError')
  bad=copy.deepcopy(sel);bad[0]['raw_sha256']='0'*64;p.write_text(json.dumps(bad));fail('job raw hash changed')
print('PASS3mergedCsites/1C→B2holds/5Bclaims/oldrows/evidenceappendonly/rawissuer-city-scope/5missingclaims/4no-writefaults(ifrequested); strict326 unchanged')
