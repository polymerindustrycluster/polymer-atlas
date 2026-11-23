"""Print every sentence in the material held for the canary sites that names a process-like word (reading aid; adjudication is by hand)."""
import re, sys
import common as c
from lex import sents, hits
d = c.load(); smp = c.sample(d['frame'])
EV = {}
for e in c.rd('data/evidence_*.csv'): EV.setdefault((e['record_table'], e['record_id']), []).append(e)
for s in smp:
    o = d['orgs'].get(s['org_id']) or d['eco'].get(s['org_id'])
    pg = c.pages(s['org_id'])
    print(f"\n===== {s['site_id']} {s['org_id']} {s['site_name'][:40]} | {s['site_type']} tier {s['verification_tier']} | active sites (all shards) of org: {d['active_by_org'][s['org_id']]} | corpus pages {len(pg)}")
    for r in pg:
        t = (c.CORPUS / r['text_file']).read_text(errors='replace'); seen = set()
        for z in sents(t):
            h = [x for x in hits(z) if x not in ('assembly_secondary_ops', 'printing_decorating_plastics', 'die_cutting_converting')]
            z2 = c.norm(z)
            if h and 25 < len(z2) < 420 and z2 not in seen:
                seen.add(z2); print(f"  [{r['page_kind']} {r['url'][:60]}] {h} :: {z2[:300]}")
                if len(seen) > 9: break
