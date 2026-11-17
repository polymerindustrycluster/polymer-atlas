"""Lane CAP2B builder: replays decisions.csv into processes/materials, CAP rows, EVD rows, verdicts.csv.
Idempotent: reserved IDs are recomputed from decision order and must match any row already present."""
import csv, hashlib, html, io, json, re, subprocess, sys
from pathlib import Path
T = Path(__file__).resolve().parent
ROOT = T.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted
CORPUS = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-corpus-2026-11-16')
BASE = (T / 'base.txt').read_text().strip()
WHO, DATE, CAP0, EVD0 = 'atlas-w16-cap2b', '2026-11-16', 1500, 388000
# IDs withdrawn after review of 1516036 (VisionAir SITE-001569): retired, never reused or renumbered
RETIRED_EVD, RETIRED_CAP = {388013}, {1503}
HOLD_SITES_TAGGED_MENU = 'capability row only; tag held (owner ruling 2026-11-14)'

def read(p):
    return list(csv.DictReader(Path(p).open(newline='')))
def base(p):
    return list(csv.DictReader(io.StringIO(subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=ROOT, text=True))))
def write(p, rows):
    with Path(p).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)
def norm(t):
    return ' '.join(t.split())
def vocab():
    return json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']

def validate_decision(d):
    """Raises AssertionError unless the quote, term and locality witness all hold against the stored pages."""
    for raw, sha in ((d['raw_file'], d['sha256']), (d['grain_raw_file'], d['grain_sha256'])):
        assert hashlib.sha256((CORPUS / raw).read_bytes()).hexdigest() == sha, f'raw hash mismatch {raw}'
    plain = html.unescape(re.sub('<[^>]+>', ' ', (CORPUS / d['raw_file']).read_text(errors='replace')))
    words = iter(re.findall(r'\w+', plain.lower()))
    assert all(any(w == q for w in words) for q in re.findall(r'\w+', d['quote'].lower())), 'quote words absent or out of order in raw page'
    assert norm(d['quote']) in norm((CORPUS / d['text_file']).read_text(errors='replace')), 'quote not in stored text'
    gtext = norm((CORPUS / d['grain_raw_file'].replace('.html', '.txt')).read_text(errors='replace'))
    assert norm(d['grain_quote']) in gtext, 'locality witness not in stored text'
    assert len(d['quote'].split()) <= 25, 'quote over 25 words'
    assert d['term'] in vocab()[d['field'].upper()]['values'], 'term not in vocabulary'
    assert d['basis'] in ('narrative', 'menu')

ROLLUP = ('thermoforming_', 'rubber_molding_', 'extrusion_', 'blow_molding_')  # b02 method: subtype -> SCHEMA 3.6 umbrella

def cap_term(term, typ):
    values = vocab()['CAP_' + typ.upper()]['values']
    if term in values: return term
    return next((p[:-1] for p in ROLLUP if term.startswith(p) and p[:-1] in values), None)

def id_stream(start, retired):
    i = start
    while True:
        if i not in retired: yield i
        i += 1

def outputs(decisions, sl):
    """Pure function of base tree + decisions: (site rows, caps, evidence, verdicts)."""
    ids = {r['site_id'] for r in sl}
    sites = {r['site_id']: dict(r) for p in sorted((ROOT / 'data').glob('sites_*.csv')) if p.name != 'sites_all.csv'
             for r in base(str(p.relative_to(ROOT))) if r['site_id'] in ids}
    live = {(c['site_id'], c['capability_type'], c['term']) for c in base('data/site_capabilities.csv') if not c['withdrawn_date']}
    caps, ev, verdicts = [], [], []
    evid, capid = id_stream(EVD0, RETIRED_EVD), id_stream(CAP0, RETIRED_CAP)
    for d in decisions:
        validate_decision(d)
        s = sites[d['site_id']]; typ = 'process' if d['field'] == 'processes' else 'material'
        tag = not (d['basis'] == 'menu' and s['verification_tier'] in ('A', 'B'))
        if tag:
            s[d['field']] = ';'.join(sorted(set(filter(None, s[d['field']].split(';'))) | {d['term']}))
            ev.append(dict(evidence_id=f'EVD-{next(evid):06d}', record_table='sites', record_id=s['site_id'], claim_type='scope',
                           claim_detail=f"{d['field']}={d['term']}; quote: {d['quote']}", source_class='own_site', source_ref=d['url'],
                           observed_date=DATE, tier_effect='supports_A' if d['basis'] == 'narrative' else 'supports_C', created_by=WHO,
                           notes=f"{d['basis']}; raw SHA256 {d['sha256']}; locality witness: {d['grain_quote']} ({d['grain_url']}); single active Atlas site."))
        ct = cap_term(d['term'], typ)
        if ct and (s['site_id'], typ, ct) not in live:
            live.add((s['site_id'], typ, ct))
            caps.append(dict(capability_id=f'CAP-{next(capid):06d}', site_id=s['site_id'], org_id=s['org_id'], capability_type=typ, term=ct,
                             provenance='company_disclosed', source_ref=d['url'], observed_date=DATE, withdrawn_date='', created_by=WHO,
                             notes=f"Quote: {d['quote']} Basis: {d['basis']}. Raw SHA256 {d['sha256']}." + ('' if tag else ' Section-3 tag held per owner ruling 2026-11-14; needs narrative plant evidence.')))
        verdicts.append(dict(site_id=d['site_id'], term=d['term'], verdict='VERIFIED', disposition='applied' if tag else HOLD_SITES_TAGGED_MENU, reason=f"{d['basis']} quote on own page", settling_fact='' if tag else 'Plant narrative sentence stating this term'))
    return sites, caps, ev, verdicts

def verdict_rows(decisions, sl, applied):
    holds = read(T / 'holds.csv'); screen = {r['site_id']: r['terms_with_any_hit'] for r in read(T / 'screen.csv')}
    out = list(applied); held = {h['site_id'] for h in holds}; decided = {d['site_id'] for d in decisions}
    for h in holds:
        for term in (h['terms'].split(';') if h['terms'] else ['']):
            out.append(dict(site_id=h['site_id'], term=term, verdict='STILL_UNCERTAIN', disposition='held', reason=h['reason'], settling_fact=h['settling_fact']))
    for r in sl:
        if r['site_id'] in held or r['site_id'] in decided: continue
        hits = screen[r['site_id']]
        reason = (f'term-screen hits ({hits}) read as navigation, product, customer, parent or unbound wording, not a statement of what this establishment does'
                  if hits else 'no hit on the lane term screen (a regex family per vocabulary term, run on the stored pages)')
        out.append(dict(site_id=r['site_id'], term='', verdict='STILL_UNCERTAIN', disposition='nothing found', reason=reason,
                        settling_fact='An own-page narrative or capability sentence tying a governed process or material to this establishment'))
    return sorted(out, key=lambda v: (v['site_id'], v['term']))

def main():
    sl = read(T / 'slice.csv'); decisions = read(T / 'decisions.csv')
    sites, caps, ev, applied = outputs(decisions, sl)
    path = ROOT / 'data/sites_OH.csv'; current = read(path)
    for s in current:
        if s['site_id'] in sites:
            for col in ('processes', 'materials'):
                add = set(filter(None, sites[s['site_id']][col].split(';'))) - set(filter(None, next(r for r in base('data/sites_OH.csv') if r['site_id'] == s['site_id'])[col].split(';')))
                if add: s[col] = ';'.join(sorted(set(filter(None, s[col].split(';'))) | add))
    write(path, current)
    for fn, rows, key in (('site_capabilities.csv', caps, 'capability_id'), ('evidence_sites_OH.csv', ev, 'evidence_id')):
        p = ROOT / 'data' / fn; have = {r[key]: r for r in read(p)}
        for r in rows:
            if r[key] in have: assert r == have[r[key]], f'{r[key]} present with different content'
        append_sorted(p, [r for r in rows if r[key] not in have], key)
    verdicts = verdict_rows(decisions, sl, applied); write(T / 'verdicts.csv', verdicts)
    dsites = {d['site_id'] for d in decisions}
    summary = dict(slice_sites=len(sl), term_decisions=len(decisions), applied_sites=len(dsites), tagged_sites=len({e['record_id'] for e in ev}),
                   tag_terms=len(ev), capability_rows=len(caps), evidence_rows=len(ev),
                   held_only_sites=len({v['site_id'] for v in verdicts if v['disposition'] == 'held'} - dsites),
                   nothing_found_sites=len({v['site_id'] for v in verdicts if v['disposition'] == 'nothing found'}),
                   verdict_rows=len(verdicts))
    (T / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n'); print(summary)

if __name__ == '__main__':
    main()
