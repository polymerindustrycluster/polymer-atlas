"""Named reconciliation, witness, known-answer and byte-idempotence checks."""
import csv,hashlib,io,json,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from atlas import load_tables,dedupe
from build import read
cs=read(H/'input.csv');vs=read(H/'verdicts.csv');alloc=read(H/'allocations.csv')
def frame_check(cs,vs):
 assert len(cs)==len(vs)==len({v['cluster_id'] for v in vs})==150
 assert {c['cluster_id'] for c in cs}=={v['cluster_id'] for v in vs}
frame_check(cs,vs)
try:frame_check(cs,vs[:-1]+[vs[0]])
except AssertionError:pass
else:raise AssertionError('duplicate injected verdict escaped')
assert len(alloc)==18==len({r['site_id'] for r in alloc})
for name,key in [('sites_IL.csv','site_id'),('evidence_sites_IL.csv','evidence_id')]:
 old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show','9489b607c19b450c195c2353944c61719105e1f9:data/'+name],cwd=ROOT,text=True))))
 now={r[key]:r for r in read(ROOT/'data'/name)}
 assert all(now[r[key]]==r for r in old),'changed existing row'
assert len(read(H/'blind-input.csv'))==18
T=load_tables(ROOT/'data');known={} 
for name,domain,oid in [('Plastipak Packaging, Inc.','plastipak.com','ORG-001033'),('Advanced Drainage Systems, Inc.','adspipe.com','ORG-000651'),('Lacks Enterprises, Inc.','lacksenterprises.com','ORG-003325')]:
 d=dedupe(T,name=name,domain=domain);assert oid in {h['id'] for s in d['steps'] for h in s['hits']};known[name]=d
(H/'known_answers.json').write_text(json.dumps(known,indent=2))
paths=[ROOT/'data'/s for s in ['sites_IL.csv','evidence_sites_IL.csv']];before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True)
assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
rows=read(ROOT/'data/sites_IL.csv');ids={r['site_id'] for r in alloc};strict=lambda r:r['operating_status'] in ['active','unknown'] and r['verification_tier'] in ['A','B','C'] and r['naics_primary'].startswith('326')
after=sum(strict(r) for r in rows);baseline=sum(strict(r) for r in rows if r['site_id'] not in ids)
assert baseline==68 and after==85
result=dict(state='IL',qcew_2023_private_establishments_326=797,before_strict_sites=baseline,after_strict_sites=after,before_percent=100*baseline/797,after_percent=100*after/797,known_answers=3,worked_clusters=150,unique_verdicts=150,creates_C=18,evidence_rows=126)
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',result)
