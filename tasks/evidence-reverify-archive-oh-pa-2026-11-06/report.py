"""Reconcile both continuation censuses against canonical membership and exact disposition sets."""
import io
import sys
from collections import Counter
from shared import HERE,ROOT,BASE,house,bound_verdicts

all_rows=bound_verdicts()
prior=set(house.bound_verdicts(BASE))
sites=[r for p in (ROOT/'data').glob('sites_*.csv') for r in house.read(p)]
evidence={r['evidence_id']:r for p in (ROOT/'data').glob('evidence_*.csv') for r in house.read(p) if r['source_class']=='own_site'}
continuation={}
lines=[]
for state,n in (('OH',1947),('PA',1639)):
    rows=house.bound_verdicts(HERE/state)
    si={r['site_id'] for r in sites if r['state']==state}
    oi={r['org_id'] for r in sites if r['site_id'] in si}
    expected={eid for eid,r in evidence.items() if eid not in prior and ((r['record_table']=='sites' and r['record_id'] in si) or (r['record_table']=='organizations' and r['record_id'] in oi))}
    assert set(rows)==expected and len(rows)==n
    assert not set(rows)&set(continuation)
    prior.update(rows);continuation.update(rows)
    lines.append(f"{state}: {len(rows)} evidence rows / {len({r['url'] for r in rows.values()})} cited references; {dict(Counter(r['judgment'] for r in rows.values()))}")
    for claim in sorted({r['claim_type'] for r in rows.values()}):
        g=[r for r in rows.values() if r['claim_type']==claim];k=sum(r['judgment']=='SUPPORTED' for r in g);lo,hi=house.wilson(k,len(g))
        lines.append(f"- {state} {claim}: {k}/{len(g)} quote-supported ({100*k/len(g):.1f}%; Wilson 95% {lo}–{hi}%)")
leads=house.read(HERE/'repair_leads.csv')
assert len(leads)==len({r['evidence_id'] for r in leads})
assert {r['evidence_id'] for r in leads}=={eid for eid,r in continuation.items() if r['judgment']!='SUPPORTED'}
new=house.read(HERE/'new_archive_links.csv');out=house.read(HERE/'archive_outcomes.csv')
assert len(new)+len(out)==len({r['evidence_id'] for r in new+out})
assert {r['evidence_id'] for r in new+out}=={eid for eid,r in continuation.items() if r['judgment']=='SUPPORTED'}
packet=house.read(HERE/'archive_links.csv')
inherited=house.read(BASE/'archive_links.csv')
assert {r['evidence_id'] for r in packet}=={r['evidence_id'] for r in inherited+new}
assert len(packet)==len(inherited)+len(new)
lines.append(f"Continuation total: {len(continuation)} rows / {len({r['url'] for r in continuation.values()})} distinct references; {len(leads)} repair/availability leads; {len(new)} new archive links; {len(out)} archive holds. Inherited links: {len(inherited)}.")
text='\n'.join(lines)+'\n';print(text,end='')
if '--emit' not in sys.argv:
    document=(HERE/'README.md').read_text()
    assert document.split('<!-- RESULTS BEGIN -->\n',1)[1].split('<!-- RESULTS END -->',1)[0]==text
