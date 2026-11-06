"""Reconciliation, existing-row preservation, idempotence and injected collision checks."""
import csv,hashlib,io,json,shutil,subprocess,sys,tempfile
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from atlas import load_tables,dedupe
from build import read
STATE='MI';N=48;CREATES=2;BASE='f437e0b89149e19e9c21e3ce360f983927b3d6bc'
cs=read(H/'input.csv');vs=read(H/'verdicts.csv');alloc=read(H/'allocations.csv');prior=read(H/'prior-input.csv')
def frame_check(vs):
 assert len(cs)==len(vs)==len({v['cluster_id'] for v in vs})==N
 assert {c['cluster_id'] for c in cs}=={v['cluster_id'] for v in vs}
frame_check(vs)
try:frame_check(vs[:-1]+[vs[0]])
except AssertionError:pass
else:raise AssertionError('injected duplicate verdict escaped')
assert not ({r['cluster_id'] for r in prior}&{r['cluster_id'] for r in cs})
universe={r['cluster_id'] for r in read(ROOT/'tasks/lead-fusion-2026-11-01/clusters.csv') if r['state']==STATE and r['class']=='CORROBORATED'}
assert universe=={r['cluster_id'] for r in prior+cs}
assert len(alloc)==CREATES==len({r['site_id'] for r in alloc})
assert len(read(H/'blind-input.csv'))==CREATES
paths=[ROOT/'data'/('sites_'+STATE+'.csv'),ROOT/'data'/('evidence_sites_'+STATE+'.csv')]
for p,key in zip(paths,['site_id','evidence_id']):
 old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':data/'+p.name],cwd=ROOT,text=True))))
 now={r[key]:r for r in read(p)};assert all(now[r[key]]==r for r in old),'changed existing row'
before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True)
assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
# Inject the motivating defect in another evidence shard; the builder must fail before ANY write.
with tempfile.TemporaryDirectory() as d:
 data=Path(d)/'data';shutil.copytree(ROOT/'data',data)
 rows=read(paths[1]);new=next(r for r in rows if r['record_id']==alloc[0]['site_id'])
 target=data/'evidence_people.csv'
 with target.open('a',newline='') as f:csv.DictWriter(f,fieldnames=list(new),lineterminator='\n').writerow(new)
 hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
 result=subprocess.run([sys.executable,str(H/'build.py'),'--apply','--data-dir',str(data)],capture_output=True,text=True)
 assert result.returncode!=0 and 'cross-shard ID collision' in result.stderr,result.stderr
 assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
T=load_tables(ROOT/'data')
for name,oid in [('Plastipak Packaging, Inc.','ORG-001033'),('Advanced Drainage Systems, Inc.','ORG-000651'),('Lacks Enterprises, Inc.','ORG-003325')]:
 assert oid in {h['id'] for s in dedupe(T,name=name)['steps'] for h in s['hits']}
rows=read(paths[0]);ids={r['site_id'] for r in alloc};strict=lambda r:r['operating_status'] in ['active','unknown'] and r['verification_tier'] in ['A','B','C'] and r['naics_primary'].startswith('326')
after=sum(strict(r) for r in rows);before=sum(strict(r) for r in rows if r['site_id'] not in ids)
assert before==138 and after==before
result=dict(state=STATE,worked_clusters=N,creates_C=CREATES,evidence_rows=7*CREATES,known_answers=3,blind_census_size=CREATES,before_strict326=before,after_strict326=after,qcew2023_private_establishments326=819,strict_share_percent=100*after/819,delta=0)
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',result)
