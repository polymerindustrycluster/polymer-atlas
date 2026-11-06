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
assert len(alloc)==len({r['site_id'] for r in alloc})==20
assert len(blind)==len({r['cluster_id'] for r in blind})==20
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
print('PASS: 40/40 unique verdicts; 20/20 blind sample witnesses; idempotent canonical bytes;',result)
