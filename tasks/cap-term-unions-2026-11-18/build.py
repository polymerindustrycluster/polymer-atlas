"""Idempotent builder: appends the 8 ruled capability terms to existing processes/materials cells of data/sites_OH.csv as a union (nothing removed)
and mints an evidence row (EVD-396500..) for each term that has none. Quote/locality validation is reused from the CAP2A builder."""
import csv, importlib.util, io, json, os, subprocess
from pathlib import Path
T = Path(__file__).resolve().parent
ROOT = T.parents[1]
import sys; sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('cap2a_build', ROOT / 'tasks/pic18-capabilities-corpus-2a-2026-11-16/build.py')
cap2a = importlib.util.module_from_spec(spec); spec.loader.exec_module(cap2a)
WHO, EV0 = 'atlas-w18-backlog', 396500
BASE = (T / 'base.txt').read_text().strip()
SITES, EVID = ROOT / 'data/sites_OH.csv', ROOT / 'data/evidence_sites_OH.csv'
def read(p): return list(csv.DictReader(Path(p).open(newline='')))
def base_count(p): return len(list(csv.DictReader(io.StringIO(subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=ROOT, text=True), newline=''))))
def write_atomic(path, header, rows):
    """Temp file in the same directory, flush + fsync, then os.replace: an interrupted write never leaves a truncated target."""
    tmp = path.with_name(path.name + '.tmp')
    try:
        with tmp.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=header, lineterminator='\n'); w.writeheader(); w.writerows(rows); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
def evidence_row(i, d):
    return dict(evidence_id=f'EVD-{EV0 + i}', record_table='sites', record_id=d['site_id'], claim_type='scope', claim_detail=f"{d['field']}={d['term']}; quote: {d['quote']}",
                source_class='own_site', source_ref=d['url'], observed_date='2026-11-16', tier_effect='supports_C' if d['basis'] == 'menu' else 'supports_A', created_by=WHO,
                notes=f"{d['basis']}; raw SHA256 {d['sha256']}; locality witness on {d['grain_url']}: \"{d['grain_quote']}\"; term appended to a non-blank cell as a union ({d['authority']}); page fetched 2026-11-16.")
def main():
    decisions = read(T / 'decisions.csv')
    for d in decisions: cap2a.validate_decision(d)
    sites = read(SITES); by = {s['site_id']: s for s in sites}
    ev = read(EVID); have = {r['evidence_id']: r for r in ev}
    assert len(sites) == base_count('data/sites_OH.csv') and len(ev) in (base_count('data/evidence_sites_OH.csv'), base_count('data/evidence_sites_OH.csv') + len(decisions)), 'a target file is not the base (or the base plus this PR): refusing to write'
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
    all_ev = sorted(ev + new_ev, key=lambda r: r['evidence_id'])
    assert len(sites) == base_count('data/sites_OH.csv'), 'sites row count differs from the base'
    assert len(all_ev) == base_count('data/evidence_sites_OH.csv') + len(decisions) and len({r['evidence_id'] for r in all_ev}) == len(all_ev), 'evidence row count is not base + one per term'
    write_atomic(SITES, list(sites[0]), sites)
    write_atomic(EVID, list(ev[0]), all_ev)
    print(json.dumps(dict(decisions=len(decisions), evidence_rows_added=len(new_ev), sites=len({d['site_id'] for d in decisions}))))
if __name__ == '__main__': main()
