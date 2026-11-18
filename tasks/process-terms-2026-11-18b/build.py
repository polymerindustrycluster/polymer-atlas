#!/usr/bin/env python3
"""Owner ruling 2026-11-18b item 2: apply SITE-000562 `rubber_molding_transfer` (held in PR #381) now that SCHEMA 3.1 (v1.16) has the term.

Unions the term into the existing non-blank `processes` cell of data/sites_OH.csv (nothing removed, no other column touched) and mints
one evidence row (EVD-396950) in data/evidence_sites_OH.csv. The site is tier C, so a services-menu line (supports_C) may union into `processes`;
on a tier A/B site this would be a site_capabilities row only (owner ruling 2026-11-14) and the builder refuses. Quote and locality witness are
validated against the stored page by the CAP2A helper (sha256, words in order, term in the vocabulary). Idempotent.
"""
import csv, importlib.util, io, os, sys
from pathlib import Path
T = Path(__file__).resolve().parent
ROOT = T.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('cap2a_build', ROOT / 'tasks/pic18-capabilities-corpus-2a-2026-11-16/build.py')
cap2a = importlib.util.module_from_spec(spec); spec.loader.exec_module(cap2a)
WHO, SITE, TERM = 'claude-code atlas-w18-rulings', 'SITE-000562', 'rubber_molding_transfer'
EVD_FLOOR = 397199  # controller 2026-11-18: above main's maximum (397103) and open PR #395's block (397110-397115); the first id minted is the next above max(this, tree maximum)
SITES, EVID = ROOT / 'data/sites_OH.csv', ROOT / 'data/evidence_sites_OH.csv'
def read(p): return list(csv.DictReader(Path(p).open(newline='')))
def write_atomic(path, header, rows):
    tmp = path.with_name(path.name + '.tmp')
    try:
        with tmp.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=header, lineterminator='\n'); w.writeheader(); w.writerows(rows); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
def max_evidence_id():
    return max(int(r['evidence_id'][4:]) for p in sorted((ROOT / 'data').glob('evidence_*.csv')) for r in read(p))
def evidence_row(d, eid):
    return dict(evidence_id=eid, record_table='sites', record_id=d['site_id'], claim_type='scope', claim_detail=f"{d['field']}={d['term']}; quote: {d['quote']}",
                source_class='own_site', source_ref=d['url'], observed_date='2026-11-16', tier_effect='supports_C', created_by=WHO,
                notes=(f"{d['basis']}; raw SHA256 {d['sha256']}; locality witness on {d['grain_url']}: \"{d['grain_quote']}\"; term appended to a non-blank cell as a union ({d['authority']}); "
                       "services-menu item, supports_C on a tier C site; page fetched 2026-11-16, stored page re-read 2026-11-18."))
def main():
    (d,) = read(T / 'decisions.csv')
    assert (d['site_id'], d['field'], d['term'], d['basis']) == (SITE, 'processes', TERM, 'menu')
    cap2a.validate_decision(d)
    sites = read(SITES); site = next(s for s in sites if s['site_id'] == SITE)
    assert site['state'] == 'OH' and site['operating_status'] == 'active'
    assert site['verification_tier'] == 'C', f"{SITE} is tier {site['verification_tier']}: a menu term on tier A/B is a site_capabilities row only (owner ruling 2026-11-14)"
    cur = [v for v in site['processes'].split(';') if v]
    assert cur, 'union applies to a non-blank cell'
    if TERM not in cur: site['processes'] = ';'.join(cur + [TERM])
    ev = read(EVID)
    mine = [r for r in ev if r['record_id'] == SITE and r['claim_detail'].startswith(f'processes={TERM}') and r['created_by'] == WHO]
    if mine:  # re-run: the row minted earlier must be exactly the planned row
        assert len(mine) == 1 and mine[0] == evidence_row(d, mine[0]['evidence_id']), 'the minted evidence row differs from the plan'
        row = mine[0]
    else:
        assert not any(r['record_id'] == SITE and r['claim_detail'].startswith(f'processes={TERM}') for r in ev), 'term already has an evidence row'
        row = evidence_row(d, 'EVD-%06d' % (max(EVD_FLOOR, max_evidence_id()) + 1)); ev.append(row)
    write_atomic(EVID, list(ev[0]), sorted(ev, key=lambda r: r['evidence_id']))
    write_atomic(SITES, list(sites[0]), sites)
    print(f'{SITE} processes = {site["processes"]}; evidence {row["evidence_id"]} (supports_C)')
if __name__ == '__main__': main()
