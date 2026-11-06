#!/usr/bin/env python3
"""Independent merged-frame/27-site census, no-write replay, real packet faults."""
import argparse,copy,csv,hashlib,io,json,subprocess
from pathlib import Path
from build import H,ROOT,packet,read,receipt
ap=argparse.ArgumentParser();ap.add_argument('--negative-controls',action='store_true');a=ap.parse_args()
base=json.loads((H/'baseline.json').read_text());freeze=base['frame_commit']
def frozen_sites():
 for p in subprocess.check_output(['git','ls-tree','-r','--name-only',freeze,'data/'],text=True,cwd=ROOT).splitlines():
  if p.startswith('data/sites_') and p.endswith('.csv'):
   yield from csv.DictReader(io.StringIO(subprocess.check_output(['git','show',freeze+':'+p],text=True,cwd=ROOT)))
all_sites=list(frozen_sites());frame=read(H/'input.csv');holds=packet();assert holds==read(H/'verdicts.csv')
expected=[r for r in all_sites if r['created_by']=='atlas-L3-corroborated-mo-sc' and r['verification_tier']=='C']
assert {r['site_id']:r for r in frame}=={r['site_id']:r for r in expected},'merged-only nine-site frame mismatch'
prior=read(H/'prior-frames.csv');assert len(prior)==18 and len({r['site_id'] for r in prior})==18
assert sum(r['packet_pr']=='216' for r in prior)==3 and sum(r['packet_pr']=='232' for r in prior)==15
for pr,task in [('216','l3-merged-site-quality'),('232','l3-merged-site-quality-2')]:
 group=[r for r in prior if r['packet_pr']==pr];commits={r['source_commit'] for r in group};assert len(commits)==1
 original=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',next(iter(commits))+':tasks/'+task+'-2026-11-06/input.csv'],text=True,cwd=ROOT))))
 assert {r['site_id'] for r in group}=={r['site_id'] for r in original}
birth={r['site_id'] for r in all_sites if r['created_by'] in {'atlas-L3-corroborated-mo-sc','atlas-L3-corroborated-la','atlas-L3-corroborated-mn','atlas-L3-corroborated-nj'}}|{'SITE-012001'}
union=[r['site_id'] for r in prior+frame];assert len(union)==len(set(union))==27 and set(union)==birth,'aggregate birth census mismatch'
def hashes():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data').glob('*.csv')}
before=hashes();v=(H/'verdicts.csv').read_bytes();subprocess.run(['python3',str(H/'build.py'),'--apply'],check=True,cwd=ROOT,capture_output=True);assert hashes()==before and v==(H/'verdicts.csv').read_bytes(),'non-idempotent replay'
assert not subprocess.check_output(['git','diff',base['commit'],'--','data/'],cwd=ROOT),'canonical delta'
import importlib.util
spec=importlib.util.spec_from_file_location('qcew',ROOT/'scripts/build_qcew_denominators.py');qcew=importlib.util.module_from_spec(spec);spec.loader.exec_module(qcew)
num=qcew.atlas_numerators(str(ROOT));den=read(ROOT/'docs/denominators/qcew_state_polymer_2023_2024.csv')
for r in read(H/'t3.csv'):
 title={'MO':'Missouri','SC':'South Carolina'}[r['state']]
 d=next(x for x in den if x['year']=='2023' and x['industry_code']=='326' and x['own_code']=='5' and x['area_title'].startswith(title))
 assert int(r['strict_before'])==int(r['strict_after'])==num[(r['state'],'326')][1]
 assert int(r['qcew_private_establishments'])==int(d['annual_avg_estabs'])
 assert float(r['share_before_pct'])==float(r['share_after_pct'])==round(100*int(r['strict_after'])/int(d['annual_avg_estabs']),4)
if a.negative_controls:
 for field,value,needle in [('verdict','VERIFIED','unapproved promotion'),('site_id','SITE-999999','under-returned census')]:
  p=H/'holds.csv';old=p.read_bytes();rows=read(p);rows[0][field]=value
  try:
   with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
   run=subprocess.run(['python3',str(H/'build.py'),'--apply'],capture_output=True,text=True,cwd=ROOT)
   assert run.returncode and needle in run.stderr and hashes()==before and (H/'verdicts.csv').read_bytes()==v,'fault accepted or wrote'
  finally:p.write_bytes(old)
 bad=copy.deepcopy(json.loads((H/'holds-sources.json').read_text())[0]);bad['quote']+=' fabricatedholdproof7731'
 try:receipt(bad)
 except AssertionError:pass
 else:raise AssertionError('fabricated hold quote accepted')
print('PASS: 9/9 merged holds; aggregate 27=3+15+9 unique birth sites; 9 raw + 3 known positive/negative receipts; canonical bytes and replay unchanged; 3 faults (if requested)')
