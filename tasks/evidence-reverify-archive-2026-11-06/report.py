"""Deterministic yield and per-claim rates; no skipped rows can pass reconciliation."""
from collections import Counter
import io, sys
real_print = print
buffer = io.StringIO()
def print(*args, **kwargs):
 kwargs["file"] = buffer
 real_print(*args, **kwargs)
from run import HERE, ROOT, read, wilson, bound_verdicts
r = list(bound_verdicts().values()); inputs = read(HERE/'inputs.csv'); leads = read(HERE/'repair_leads.csv')
assert {x['evidence_id'] for x in inputs} == {x['evidence_id'] for x in r}
assert len(r) == len(inputs) == len({x['evidence_id'] for x in r}) == 3683
assert len({x['source_ref'] for x in inputs}) == 1120
assert len(leads) == len({x['evidence_id'] for x in leads})
assert {x['evidence_id'] for x in leads} == {x['evidence_id'] for x in r if x['judgment'] != 'SUPPORTED'}
print('PIC18 evidence rows:', len(r), 'distinct cited refs:',len({x['source_ref'] for x in r}))
print('Judgments:',dict(Counter(x['judgment'] for x in r)))
print('Repair/availability leads:',len(leads),'/',len(r))
print('| Claim | Quote supported / all rows | Rate (Wilson 95% CI) | Supported / readable | Rate (Wilson 95% CI) | 2026-11-03 semantic audit |')
print('|-|-:|-|-:|-|-|')
old={'scope':'122/151 (81%; 74–86%)','existence':'12/24 (50%; 31–69%)','address':'7/13 (54%; 29–77%)','parent':'0/2 (0%; 0–66%)'}
for kind in sorted({x['claim_type'] for x in r}):
 g=[x for x in r if x['claim_type']==kind];n=len(g);k=sum(x['judgment']=='SUPPORTED' for x in g);m=sum(x['judgment']!='FETCH_FAILED' for x in g)
 lo,hi=wilson(k,n);a,b=wilson(k,m)
 print(f'| {kind} | {k}/{n} | {100*k/n:.1f}% ({lo}–{hi}%) | {k}/{m} | {100*k/m:.1f}% ({a}–{b}%) | {old.get(kind,"not sampled")} |')
if (HERE/'archive_links.csv').exists():
 links=read(HERE/'archive_links.csv');out=read(HERE/'archive_outcomes.csv')
 assert len(links)+len(out)==sum(x['judgment']=='SUPPORTED' for x in r)
 assert len({x['evidence_id'] for x in links+out})==len(links)+len(out)
 assert {x['evidence_id'] for x in links+out} == {x['evidence_id'] for x in r if x['judgment']=='SUPPORTED'}
 print('Archive packet:',len(links),'rows /',len({x['archive_ref'] for x in links}),'captures')
 print('Archive holds:',dict(Counter(x['status'] for x in out)))

text = buffer.getvalue()
real_print(text,end='')
if '--emit' not in sys.argv:
 document = (HERE/'README.md').read_text()
 rendered = document.split('<!-- RESULTS BEGIN -->\n',1)[1].split('<!-- RESULTS END -->',1)[0]
 assert rendered == text, 'README result block differs from recomputed results'
