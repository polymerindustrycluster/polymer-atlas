"""Idempotent builder, lane CAP2A: applies hand-adjudicated process/material terms (decisions.csv) to sites_OH.csv (processes,
materials only), appends site_capabilities rows (CAP-001200..) and evidence_sites_OH rows (EVD-387000..), writes verdicts.csv."""
import csv, hashlib, html, io, json, re, subprocess, sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
T = Path(__file__).resolve().parent
ROOT = T.parents[1]
sys.path.insert(0, str(ROOT / 'scripts')); sys.path.insert(0, str(T))
from shard_io import append_sorted
from regions import PIC18
from holds import HOLDS
CORPUS = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-corpus-2026-11-16')
BASE = (T / 'base.txt').read_text().strip()
WHO = 'atlas-w16-cap2a'
EVD0, CAP0 = 387000, 1200
VOCAB = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']
CAP_UMBRELLA = [('extrusion_', 'extrusion'), ('thermoforming_', 'thermoforming'), ('blow_molding_', 'blow_molding'), ('rubber_molding_', 'rubber_molding')]
def read(p): return list(csv.DictReader(Path(p).open(newline='')))
def base(p): return list(csv.DictReader(io.StringIO(subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=ROOT, text=True), newline='')))
def write(p, rows):
    with Path(p).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)
def norm(t): return ' '.join(t.split())
def cap_term(typ, term):
    """Section 3.6 family for a section 3 term (b02 mapping); None when 3.6 has no term."""
    cv = VOCAB['CAP_' + typ.upper()]['values']
    if term in cv: return term
    if typ == 'process':
        if term in ('custom_compounding', 'compounding_unspecified', 'compounding_extrusion'): return 'compounding'
        for pre, fam in CAP_UMBRELLA:
            if term.startswith(pre): return fam
    return None
@lru_cache(maxsize=1)
def frame_now():
    """Independent recomputation of the PR #351 frame criteria at the pinned base."""
    sites = [r for p in sorted((ROOT / 'data').glob('sites_*.csv')) if p.name != 'sites_all.csv' for r in base(str(p.relative_to(ROOT)))]
    n = Counter(s['org_id'] for s in sites if s['operating_status'] == 'active')
    excluded = {r['site_id'] for b in ('01', '02') for f in ('frame.csv', 'verdicts.csv') for r in read(ROOT / f'tasks/oh-capabilities-2026-11-12-b{b}/{f}')}
    orgs = {r['org_id'] for r in read(CORPUS / 'manifest.csv') if r['text_file']}
    return [s for s in sites if s['state'] == 'OH' and s['county'] in PIC18 and s['operating_status'] == 'active' and s['verification_tier'] in ('A', 'B', 'C')
            and (not s['processes'] or not s['materials']) and n[s['org_id']] == 1 and s['site_id'] not in excluded and s['org_id'] in orgs]
def slice_ids(): return [r['site_id'] for r in read(T / 'slice.csv')]
def validate_decision(d):
    assert hashlib.sha256((CORPUS / d['raw_file']).read_bytes()).hexdigest() == d['sha256'], 'raw hash'
    raw = (CORPUS / d['raw_file']).read_text(errors='replace')
    words = iter(re.findall(r'\w+', html.unescape(re.sub('<[^>]+>', ' ', raw)).lower()))
    assert all(any(w == q for w in words) for q in re.findall(r'\w+', d['quote'].lower())), 'quote words absent from raw page in order'
    assert norm(d['quote']) in norm((CORPUS / d['text_file']).read_text()), 'quote not in page text'
    assert norm(d['grain_quote']) in norm((CORPUS / d['grain_text_file']).read_text()), 'locality witness absent'
    assert len(d['quote'].split()) <= 25
    assert d['term'] in VOCAB[d['field'].upper()]['values'], 'term outside vocabulary'
    assert d['basis'] in ('narrative', 'menu')
def outputs(decisions):
    sites = {r['site_id']: dict(r) for r in base('data/sites_OH.csv') if r['site_id'] in set(slice_ids())}
    assert set(sites) == set(slice_ids()), 'slice site missing from base sites_OH'
    live = {(c['site_id'], c['capability_type'], c['term']) for c in base('data/site_capabilities.csv') if not c['withdrawn_date']}
    caps, ev, verdicts = [], [], []
    for d in decisions:
        validate_decision(d)
        s = sites[d['site_id']]; typ = 'process' if d['field'] == 'processes' else 'material'
        assert s['state'] == 'OH' and s['operating_status'] == 'active' and s['verification_tier'] in ('A', 'B', 'C')
        tier_ok = not (d['basis'] == 'menu' and s['verification_tier'] in ('A', 'B'))  # owner ruling 2026-11-14
        blank = not next(x for x in base('data/sites_OH.csv') if x['site_id'] == s['site_id'])[d['field']].strip()  # b02 fill-blank-only rule
        tag = tier_ok and blank
        if tag:
            have = [v for v in s[d['field']].split(';') if v]
            if d['term'] not in have: s[d['field']] = ';'.join(have + [d['term']])
            ev.append(dict(evidence_id=f'EVD-{EVD0 + len(ev):06d}', record_table='sites', record_id=s['site_id'], claim_type='scope',
                           claim_detail=f"{d['field']}={d['term']}; quote: {d['quote']}", source_class='own_site', source_ref=d['url'], observed_date='2026-11-16',
                           tier_effect='supports_C' if d['basis'] == 'menu' else 'supports_A', created_by=WHO,
                           notes=f"{d['basis']}; raw SHA256 {d['sha256']}; locality witness on {d['grain_url']}: \"{d['grain_quote']}\"; the organization has one active Atlas site; corpus fetched 2026-11-16."))
        ct = cap_term(typ, d['term'])
        cap_note = ''
        if ct and (s['site_id'], typ, ct) not in live:
            live.add((s['site_id'], typ, ct))
            caps.append(dict(capability_id=f'CAP-{CAP0 + len(caps):06d}', site_id=s['site_id'], org_id=s['org_id'], capability_type=typ, term=ct, provenance='company_disclosed',
                             source_ref=d['url'], observed_date='2026-11-16', withdrawn_date='', created_by=WHO,
                             notes=f"Quote: {d['quote']} Basis: {d['basis']}. Raw SHA256 {d['sha256']}. Locality witness: \"{d['grain_quote']}\"."
                                   + ('' if tag else ' Section-3 tag held per owner ruling 2026-11-14 (C-strength on a tier A/B site).' if not tier_ok else ' Section-3 tag held: the cell was not blank at base (fill-blank rule); recommend appending.')))
            cap_note = f'; capability {ct}'
        elif not tag and not ct: cap_note = '; no section 3.6 term, so no row'
        elif not tag: cap_note = f'; capability {ct} already live'
        disp = 'applied' if tag else 'capability row only' if not tier_ok else 'tag held (cell not blank at base)'
        verdicts.append(dict(site_id=s['site_id'], term=d['term'], verdict='VERIFIED', disposition=disp + cap_note,
                             settling_fact='' if tag else 'A narrative sentence (supports_A) for this term, or a section 3.6 term (owner ruling 2026-11-14)' if not tier_ok
                             else 'Controller call: append to a cell that holds non-section-3.1 values (recommended: append)' ))
    decided = {d['site_id'] for d in decisions}
    for sid in slice_ids():
        n = int(sid[5:])
        if n in HOLDS and (sid not in decided or n == 591):
            cls, fact = HOLDS[n]
            verdicts.append(dict(site_id=sid, term='', verdict='STILL_UNCERTAIN', disposition=f'held: {cls}', settling_fact=fact))
        else:
            assert sid in decided, ('no verdict for', sid)
    return sites, caps, ev, verdicts
def summary(decisions, sites, caps, ev, verdicts):
    orig = {r['site_id']: r for r in base('data/sites_OH.csv')}
    return dict(slice_sites=len(slice_ids()), term_decisions=len(decisions), sites_with_applied_terms=len({d['site_id'] for d in decisions}),
                sites_tagged=len({r['record_id'] for r in ev}), capability_rows=len(caps), evidence_rows=len(ev),
                changed_site_rows=sum(sites[k] != orig[k] for k in sites), held_sites=len({v['site_id'] for v in verdicts if v['verdict'] == 'STILL_UNCERTAIN'}),
                verdict_rows=len(verdicts), slice_sites_not_in_frame_now=sorted(set(slice_ids()) - {s['site_id'] for s in frame_now()}))
def main():
    decisions = read(T / 'decisions.csv')
    sites, caps, ev, verdicts = outputs(decisions)
    path = ROOT / 'data/sites_OH.csv'; current = read(path)
    orig = {r['site_id']: r for r in base('data/sites_OH.csv')}
    for s in current:
        if s['site_id'] in sites:
            for col in ('processes', 'materials'):
                have = [v for v in s[col].split(';') if v]
                s[col] = ';'.join(have + [v for v in sites[s['site_id']][col].split(';') if v and v not in have])
    write(path, current)
    for filename, rows, key in [('site_capabilities.csv', caps, 'capability_id'), ('evidence_sites_OH.csv', ev, 'evidence_id')]:
        p = ROOT / 'data' / filename; have = {r[key]: r for r in read(p)}
        for r in rows:
            if r[key] in have: assert r == have[r[key]], r[key]
        append_sorted(p, [r for r in rows if r[key] not in have], key)
    write(T / 'verdicts.csv', verdicts)
    sm = summary(decisions, sites, caps, ev, verdicts)
    (T / 'summary.json').write_text(json.dumps(sm, indent=2) + '\n'); print(sm)
if __name__ == '__main__': main()
