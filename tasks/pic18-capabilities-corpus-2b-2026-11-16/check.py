"""Recomputes every published count of lane CAP2B and proves the checks fail on injected defects.
Run after build.py. Needs the shared corpus under persist/pic18-corpus-2026-11-16 (see build.CORPUS)."""
import copy, csv, json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B
from build import T, ROOT, read, base, norm
sys.path.insert(0, str(ROOT / 'scripts'))
from regions import PIC18
PRIOR_DECIDED = {'SITE-000060', 'SITE-000245', 'SITE-001757', 'SITE-001865'}  # the 4 sites PR #351 adjudicated
def fail(m): raise AssertionError(m)

def frame():
    """Eligible sites recomputed from the base tree, independent of slice.csv (PR #351 criteria)."""
    sites = [r for p in sorted((ROOT / 'data').glob('sites_*.csv')) if p.name != 'sites_all.csv' for r in base(str(p.relative_to(ROOT)))]
    n = Counter(s['org_id'] for s in sites if s['operating_status'] == 'active')
    excl = {r['site_id'] for b in ('01', '02') for f in ('frame.csv', 'verdicts.csv') for r in read(ROOT / f'tasks/oh-capabilities-2026-11-12-b{b}/{f}')}
    orgs = {r['org_id'] for r in read(B.CORPUS / 'manifest.csv') if r['text_file']}
    return [s for s in sites if s['state'] == 'OH' and s['county'] in PIC18 and s['operating_status'] == 'active' and s['verification_tier'] in 'ABC'
            and (not s['processes'] or not s['materials']) and n[s['org_id']] == 1 and s['site_id'] not in excl and s['org_id'] in orgs]

def check_slice(sl, fr):
    rest = sorted((s['site_id'] for s in fr if s['site_id'] not in PRIOR_DECIDED))
    if [r['site_id'] for r in sl] != rest[len(rest) // 2:]: fail('slice is not the second half of the unadjudicated frame')
    pages = Counter(r['org_id'] for r in read(B.CORPUS / 'manifest.csv') if r['text_file'])
    for r in sl:
        if int(r['n_pages']) != pages[r['org_id']] or pages[r['org_id']] < 1: fail(f"page count mismatch {r['site_id']}")
    return len(fr), len(rest)

def check_coverage(verdicts, sl, decisions):
    seen = {v['site_id'] for v in verdicts}
    if missing := [r['site_id'] for r in sl if r['site_id'] not in seen]: fail(f'sites without verdict: {missing[:3]}')
    for d in decisions:
        if not any(v['site_id'] == d['site_id'] and v['term'] == d['term'] and v['verdict'] == 'VERIFIED' for v in verdicts): fail(f"no verdict for {d['site_id']} {d['term']}")
    for v in verdicts:
        if v['verdict'] == 'STILL_UNCERTAIN' and not v['settling_fact']: fail(f"hold without settling fact {v['site_id']}")

def check_rules(sites, ev, caps):
    for e in ev:
        if e['record_table'] == 'sites' and e['tier_effect'] == 'supports_C' and sites[e['record_id']]['verification_tier'] in ('A', 'B'): fail(f"C-strength scope tag on tier A/B {e['record_id']} (V-25)")
    if any(not (388000 <= int(e['evidence_id'][4:]) <= 388999) for e in ev) or any(not (1500 <= int(c['capability_id'][4:]) <= 1799) for c in caps): fail('id outside reserved block')

def must_fail(label, fn):
    try: fn()
    except AssertionError: print(f'  injected defect caught: {label}'); return
    fail(f'injected defect NOT caught: {label}')

def main():
    sl, decisions = read(T / 'slice.csv'), read(T / 'decisions.csv')
    fr = frame(); nfr, nrest = check_slice(sl, fr); print(f'frame {nfr} eligible sites; unadjudicated {nrest}; slice {len(sl)} (second half)')
    sites, caps, ev, applied = B.outputs(decisions, sl)  # validates every decision against the stored pages
    check_rules(sites, ev, caps)
    # data files: exactly base + expected rows, other cells untouched
    for fn, rows, key in (('site_capabilities.csv', caps, 'capability_id'), ('evidence_sites_OH.csv', ev, 'evidence_id')):
        now, was = {r[key]: r for r in read(ROOT / 'data' / fn)}, {r[key] for r in base('data/' + fn)}
        if set(now) - was != {r[key] for r in rows} or was - set(now): fail(f'{fn}: id set differs from base + expected')
        for r in rows:
            if now[r[key]] != r: fail(f'{fn}: {r[key]} differs from expected')
    bs = {r['site_id']: r for r in base('data/sites_OH.csv')}; cur = read(ROOT / 'data/sites_OH.csv')
    if [r['site_id'] for r in cur] != list(bs): fail('sites_OH row set/order changed')
    changed = 0
    for r in cur:
        o = bs[r['site_id']]; diff = {k for k in r if r[k] != o[k]}
        if not diff: continue
        changed += 1
        if r['site_id'] not in sites or not diff <= {'processes', 'materials'}: fail(f"unexpected change {r['site_id']} {diff}")
        for col in diff:
            if o[col]: fail(f"{r['site_id']} {col} was not blank on base (fill-blank-only)")
            if not set(o[col].split(';')) - {''} <= set(r[col].split(';')) or set(r[col].split(';')) != set(filter(None, sites[r['site_id']][col].split(';'))): fail(f"{r['site_id']} {col} differs from expected")
    verdicts = read(T / 'verdicts.csv')
    if verdicts != B.verdict_rows(decisions, sl, applied): fail('verdicts.csv differs from recomputation')
    check_coverage(verdicts, sl, decisions)
    dsites = {d['site_id'] for d in decisions}
    expect = dict(slice_sites=len(sl), term_decisions=len(decisions), applied_sites=len(dsites), tagged_sites=len({e['record_id'] for e in ev}), tag_terms=len(ev),
                  capability_rows=len(caps), evidence_rows=len(ev), held_only_sites=len({v['site_id'] for v in verdicts if v['disposition'] == 'held'} - dsites),
                  nothing_found_sites=len({v['site_id'] for v in verdicts if v['disposition'] == 'nothing found'}), verdict_rows=len(verdicts))
    if json.loads((T / 'summary.json').read_text()) != expect: fail('summary.json differs from recomputation')
    if changed != expect['tagged_sites']: fail('changed site rows != tagged sites')
    if expect['applied_sites'] + expect['held_only_sites'] + expect['nothing_found_sites'] != len(sl): fail('site dispositions do not partition the slice')
    print('counts OK:', expect)
    # injected defects: each check must fail on a planted fault
    d0 = decisions[0]
    must_fail('false quote', lambda: B.validate_decision({**d0, 'quote': d0['quote'] + ' and we also run extrusion lines'}))
    must_fail('invalid vocabulary term', lambda: B.validate_decision({**d0, 'term': 'injection_moulding'}))
    must_fail('false locality witness', lambda: B.validate_decision({**d0, 'grain_quote': '1 Nowhere Road, Mentor, Ohio'}))
    must_fail('site without verdict', lambda: check_coverage([v for v in verdicts if v['site_id'] != sl[0]['site_id']], sl, decisions))
    must_fail('C-strength tag on tier B', lambda: check_rules(sites, [{**ev[0], 'tier_effect': 'supports_C', 'record_id': 'SITE-001613'}], caps))
    must_fail('id outside block', lambda: check_rules(sites, ev, [{**caps[0], 'capability_id': 'CAP-009999'}]))
    must_fail('slice is not second half', lambda: check_slice(sl[1:], fr))
    print('ALL CHECKS PASSED')

if __name__ == '__main__':
    main()
