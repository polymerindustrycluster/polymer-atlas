"""Idempotent builder: appends the 11 ruled capability terms to existing processes/materials cells of data/sites_OH.csv as a union (nothing removed)
and mints an evidence row (EVD-396500..) for each term that has none. Quote/locality validation is reused from the CAP2A builder."""
import csv, importlib.util, json
from pathlib import Path
T = Path(__file__).resolve().parent
ROOT = T.parents[1]
import sys; sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted
spec = importlib.util.spec_from_file_location('cap2a_build', ROOT / 'tasks/pic18-capabilities-corpus-2a-2026-11-16/build.py')
cap2a = importlib.util.module_from_spec(spec); spec.loader.exec_module(cap2a)
WHO, EV0 = 'atlas-w18-backlog', 396500
SITES, EVID = ROOT / 'data/sites_OH.csv', ROOT / 'data/evidence_sites_OH.csv'
def read(p): return list(csv.DictReader(Path(p).open(newline='')))
def evidence_row(i, d):
    return dict(evidence_id=f'EVD-{EV0 + i}', record_table='sites', record_id=d['site_id'], claim_type='scope', claim_detail=f"{d['field']}={d['term']}; quote: {d['quote']}",
                source_class='own_site', source_ref=d['url'], observed_date='2026-11-16', tier_effect='supports_C' if d['basis'] == 'menu' else 'supports_A', created_by=WHO,
                notes=(f"Same-page sentence carrying the material scope: \"{d['context_quote']}\". " if d['context_quote'] else '') + f"{d['basis']}; raw SHA256 {d['sha256']}; locality witness on {d['grain_url']}: \"{d['grain_quote']}\"; term appended to a non-blank cell as a union ({d['authority']}); page fetched 2026-11-16.")
def main():
    decisions = read(T / 'decisions.csv')
    for d in decisions: cap2a.validate_decision(d); assert not d['context_quote'] or cap2a.norm(d['context_quote']) in cap2a.norm((cap2a.CORPUS / d['text_file']).read_text()), 'context quote not on the page'
    sites = read(SITES); by = {s['site_id']: s for s in sites}
    ev = read(EVID); have = {r['evidence_id']: r for r in ev}
    new_ev = []
    for i, d in enumerate(decisions):
        s = by[d['site_id']]; assert s['state'] == 'OH' and s['operating_status'] == 'active' and s['verification_tier'] in ('A', 'B', 'C')
        assert not (d['basis'] == 'menu' and s['verification_tier'] in ('A', 'B')), 'C-strength term on tier A/B: capability row only'
        cur = [v for v in s[d['field']].split(';') if v]
        assert cur, 'union rule applies to non-blank cells; fill-blank is not this PR'
        if d['term'] not in cur: s[d['field']] = ';'.join(cur + [d['term']])
        row = evidence_row(i, d)
        if row['evidence_id'] in have: assert have[row['evidence_id']] == row, row['evidence_id']
        else:
            assert not any(r['record_id'] == d['site_id'] and r['claim_detail'].startswith(f"{d['field']}={d['term']}") for r in ev), 'term already has an evidence row'
            new_ev.append(row)
    with SITES.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(sites[0]), lineterminator='\n'); w.writeheader(); w.writerows(sites)
    append_sorted(EVID, new_ev, 'evidence_id')
    print(json.dumps(dict(decisions=len(decisions), evidence_rows_added=len(new_ev), sites=len({d['site_id'] for d in decisions}))))
if __name__ == '__main__': main()
