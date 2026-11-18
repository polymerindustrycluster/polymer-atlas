#!/usr/bin/env python3
"""Owner ruling 2026-11-18b item 2: apply SITE-000562 `rubber_molding_transfer` (held in PR #381) now that SCHEMA 3.1 (v1.16) has the term.

Unions the term into the existing non-blank `processes` cell of data/sites_OH.csv (nothing removed, no other column touched) and appends one
evidence row to data/evidence_sites_OH.csv with scripts/shard_io.py append_sorted. The evidence id is allocated at apply time above the maximum across
every data/evidence_*.csv shard and above EVD_FLOOR (never reused, never filling a gap; AGENTS.md 3). The site is tier C, so a services-menu line
(supports_C) may union into `processes`; on tier A/B it would be a site_capabilities row only (owner ruling 2026-11-14) and the builder refuses.
Refuses before any write unless: the quote carries the words of the term ("transfer"); the cited URL and the locality URL are the manifest entries (url, sha256,
files, organization) of the stored pages whose bytes were checked; and both shards have exactly the row counts of the pinned base (base.txt), with unique ids.
A replay (row and cell already present and equal to the plan) writes nothing.
"""
import csv, importlib.util, io, os, subprocess, sys
from collections import Counter
from pathlib import Path
T = Path(__file__).resolve().parent
ROOT = T.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted
spec = importlib.util.spec_from_file_location('cap2a_build', ROOT / 'tasks/pic18-capabilities-corpus-2a-2026-11-16/build.py')
cap2a = importlib.util.module_from_spec(spec); spec.loader.exec_module(cap2a)
WHO, SITE, TERM = 'claude-code atlas-w18-rulings', 'SITE-000562', 'rubber_molding_transfer'
TERM_WORD = {TERM: 'transfer'}  # the quote must carry the words of the term it supports ("Compression Molding" must not pass)
EVD_FLOOR = 397199  # controller 2026-11-18: above main's maximum and open PR #395's block; the id minted is the next above max(this, tree maximum)
CORPUS_MANIFEST = cap2a.CORPUS / 'manifest.csv'
def read(p): return list(csv.DictReader(Path(p).open(newline='')))
def rd(text): return list(csv.DictReader(io.StringIO(text, newline='')))
def git_show(ref, path): return subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
def base_ref(): return (T / 'base.txt').read_text().strip()
def write_atomic(path, header, rows):
    tmp = path.with_name(path.name + '.tmp')
    try:
        with tmp.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=header, lineterminator='\n'); w.writeheader(); w.writerows(rows); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
def max_evidence_id(data):
    return max(int(r['evidence_id'][4:]) for p in sorted(Path(data).glob('evidence_*.csv')) for r in read(p))
def evidence_row(d, eid):
    return dict(evidence_id=eid, record_table='sites', record_id=d['site_id'], claim_type='scope', claim_detail=f"{d['field']}={d['term']}; quote: {d['quote']}",
                source_class='own_site', source_ref=d['url'], observed_date='2026-11-16', tier_effect='supports_C', created_by=WHO,
                notes=(f"{d['basis']}; raw SHA256 {d['sha256']}; locality witness on {d['grain_url']}: \"{d['grain_quote']}\"; term appended to a non-blank cell as a union ({d['authority']}); "
                       "services-menu item, supports_C on a tier C site; page fetched 2026-11-16, stored page re-read 2026-11-18."))
def manifest_by_file():
    rows = read(CORPUS_MANIFEST)
    return {r['raw_file']: r for r in rows} | {r['text_file']: r for r in rows}
def check_decision(d, org_id):
    """Quote, term words, vocabulary, stored-page bytes (CAP2A helper) and the manifest binding of both cited URLs; raises AssertionError."""
    assert (d['site_id'], d['field'], d['term'], d['basis']) == (SITE, 'processes', TERM, 'menu'), 'decision is not the planned one'
    cap2a.validate_decision(d)
    assert TERM_WORD[d['term']] in d['quote'].lower(), f"the quote lacks the word {TERM_WORD[d['term']]!r} of {d['term']}"
    m = manifest_by_file()
    r = m.get(d['raw_file'])
    assert r and r['url'] == d['url'] and r['sha256'] == d['sha256'] and r['text_file'] == d['text_file'] and r['org_id'] == org_id, 'cited url is not the manifest entry (url, sha256, files, organization) of the checked page'
    g = m.get(d['grain_text_file'])
    assert g and g['url'] == d['grain_url'] and g['org_id'] == org_id, 'locality url is not the manifest entry of the checked locality page'
def main(data=ROOT / 'data', decisions=T / 'decisions.csv'):
    data = Path(data); SITES, EVID = data / 'sites_OH.csv', data / 'evidence_sites_OH.csv'
    (d,) = read(decisions)
    sites = read(SITES); ev = read(EVID)
    site = next(s for s in sites if s['site_id'] == SITE)
    assert site['state'] == 'OH' and site['operating_status'] == 'active'
    assert site['verification_tier'] == 'C', f"{SITE} is tier {site['verification_tier']}: a menu term on tier A/B is a site_capabilities row only (owner ruling 2026-11-14)"
    check_decision(d, site['org_id'])
    cur = [v for v in site['processes'].split(';') if v]
    assert cur, 'union applies to a non-blank cell'
    mine = [r for r in ev if r['record_id'] == SITE and r['claim_detail'].startswith(f'processes={TERM}')]
    base_sites, base_ev = len(rd(git_show(base_ref(), 'data/sites_OH.csv'))), len(rd(git_show(base_ref(), 'data/evidence_sites_OH.csv')))
    # exact counts against the pinned base before any write: a truncated or padded shard is refused (the evidence row may already be present)
    assert len(sites) == base_sites, f'sites_OH has {len(sites)} rows, the base has {base_sites}'
    assert len(ev) == base_ev + len(mine) and len(mine) <= 1, f'evidence_sites_OH has {len(ev)} rows, expected {base_ev} plus the one row of this PR'
    assert all(c == 1 for c in Counter(r['evidence_id'] for r in ev).values()) and all(c == 1 for c in Counter(r['site_id'] for r in sites).values()), 'duplicate ids'
    if mine:
        assert mine[0] == evidence_row(d, mine[0]['evidence_id']) and mine[0]['created_by'] == WHO, 'the minted evidence row differs from the plan'
    else:
        row = evidence_row(d, 'EVD-%06d' % (max(EVD_FLOOR, max_evidence_id(data)) + 1))
        append_sorted(EVID, [row], 'evidence_id')  # shared writer: atomic, rejects an occupied id; evidence first, so a retry after an interruption completes the site
    if TERM not in cur:
        site['processes'] = ';'.join(cur + [TERM])
        write_atomic(SITES, list(sites[0]), sites)
    print(f'{SITE} processes = {site["processes"]}; evidence {(mine or [row])[0]["evidence_id"]} (supports_C)')
if __name__ == '__main__': main()
