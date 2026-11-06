"""Named packet checks: uniqueness, source yield, idempotence, QCEW numerator delta."""
import csv, hashlib, json, subprocess, sys
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_qcew_denominators import atlas_numerators
from build import read
vs=read(P/'verdicts.csv');cs=read(P/'input.csv');alloc=read(P/'allocations.csv');blind=read(P/'blind-input.csv')
assert len(vs)==len(cs)==len({r['cluster_id'] for r in vs})==40
assert {r['cluster_id'] for r in vs}=={r['cluster_id'] for r in cs}
assert len(alloc)==len({r['site_id'] for r in alloc})==19
assert len(blind)==len({r['cluster_id'] for r in blind})==19
assert {r['cluster_id'] for r in blind}<={r['cluster_id'] for r in alloc}
paths=[ROOT/'data'/n for n in ['organizations_US.csv','sites_TX.csv','evidence_organizations_US.csv','evidence_sites_TX.csv']]
before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
subprocess.run([sys.executable,str(P/'build.py'),'--apply'],check=True)
assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths],'Rebuild changed canonical bytes'
n=atlas_numerators(str(ROOT));b=json.loads((P/'qcew_before.json').read_text());after=n['TX','326'][1]
new={r['site_id'] for r in alloc};rows=read(ROOT/'data/sites_TX.csv');delta=sum(r['site_id'] in new and r['naics_primary'].startswith('326') for r in rows)
assert after-b['atlas_strict']==delta
result={**b,'atlas_strict_after':after,'delta_strict':delta,'before_pct':100*b['atlas_strict']/b['qcew_2023_private_establishments'],'after_pct':100*after/b['qcew_2023_private_establishments']}
(P/'qcew_result.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 40/40 unique verdicts; 19/19 blind census witnesses; idempotent canonical bytes;',result)
# Cross-shard collision injected into a pre-pass fixture must leave every shard unchanged.
import io, os, shutil, tempfile, build
with tempfile.TemporaryDirectory(prefix='l6-tx3-collision-') as tmp:
    fixture=Path(tmp);shutil.copytree(ROOT/'data',fixture/'data')
    for n in ['tasks','docs','scripts']:(fixture/n).symlink_to(ROOT/n,target_is_directory=True)
    for n in ['organizations_US.csv','evidence_organizations_US.csv','sites_TX.csv','evidence_sites_TX.csv']:
        (fixture/'data'/n).write_bytes(subprocess.check_output(['git','show','origin/main:data/'+n],cwd=ROOT))
    target=fixture/'data/evidence_sites_OH.csv';ev=read(target);ev[0]['evidence_id']='EVD-194004'
    with open(target,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=ev[0],lineterminator='\n');w.writeheader();w.writerows(ev)
    def hashes():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (fixture/'data').glob('*.csv')}
    before=hashes();build.ROOT=fixture;sys.argv=['build.py','--apply']
    try:build.main()
    except AssertionError as e:assert 'cross-shard ID collision' in str(e),str(e)
    else:raise AssertionError('Cross-shard ID collision accepted')
    assert before==hashes(),'Collision caused partial writes'
    print('PASS: cross-shard EVD collision rejected with zero writes across all shards.')
