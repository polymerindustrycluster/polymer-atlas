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
assert {r['cluster_id'] for r in blind}=={r['cluster_id'] for r in alloc}
paths=[ROOT/'data'/n for n in ['organizations_US.csv','sites_CA.csv','evidence_organizations_US.csv','evidence_sites_CA.csv']]
before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
subprocess.run([sys.executable,str(P/'build.py'),'--apply'],check=True)
assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths],'Rebuild changed canonical bytes'
n=atlas_numerators(str(ROOT));b=json.loads((P/'qcew_before.json').read_text());after=n['CA','326'][1]
new={r['site_id'] for r in alloc};rows=read(ROOT/'data/sites_CA.csv');delta=sum(r['site_id'] in new and r['naics_primary'].startswith('326') for r in rows)
assert after-b['atlas_strict']==delta
result={**b,'atlas_strict_after':after,'delta_strict':delta,'before_pct':100*b['atlas_strict']/b['qcew_2023_private_establishments'],'after_pct':100*after/b['qcew_2023_private_establishments']}
(P/'qcew_result.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 40/40 unique verdicts; 19/19 create witnesses; idempotent canonical bytes;',result)
# Removing the own-site scope witnesses must expose unsupported B promotions.
import os, shutil, tempfile
with tempfile.TemporaryDirectory(prefix='l6-ca-scope-mutation-') as tmp:
    d=Path(tmp)/'data';shutil.copytree(ROOT/'data',d)
    bsites={r['site_id'] for r in alloc if r['tier']=='B'}
    p=d/'evidence_sites_CA.csv';ev=read(p);kept=[r for r in ev if not(r['record_id'] in bsites and r['claim_type']=='scope' and r['source_class']=='own_site')]
    assert len(ev)-len(kept)==len(bsites)==3
    with open(p,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=ev[0],lineterminator='\n');w.writeheader();w.writerows(kept)
    r=subprocess.run([sys.executable,str(ROOT/'scripts/validate.py')],env={**os.environ,'ATLAS_DATA_DIR':str(d)},capture_output=True,text=True)
    assert r.returncode!=0 and all(s in r.stdout for s in bsites),r.stdout[-3000:]
    print('PASS: removing all3 own scope witnesses makes validator reject B claims.')
