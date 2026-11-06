"""Named check: exact delta vs the merge-base, raw witnesses, V-25 tier support, idempotent rebuild, injected defects fail."""
import csv, hashlib, io, re, subprocess, sys
from build import HERE, ROOT, SITE, ORG, read, witnessed, site_row

git = lambda *a: subprocess.check_output(['git', *a], cwd=ROOT, text=True)
base = git('merge-base', 'HEAD', 'origin/main').strip()
def before(name): return list(csv.DictReader(io.StringIO(git('show', f'{base}:data/{name}'))))

ws = read(HERE/'witnesses.csv'); ita = {r['establishment_id']: r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
assert len(ws) == 9 and all(witnessed(w, ita) for w in ws)
FILES = {'data/sites_TX.csv', 'data/evidence_sites_TX.csv'}
changed = set(git('diff', '--name-only', base, '--', 'data/').split()) | set(git('diff', '--name-only', '--', 'data/').split())
assert changed == FILES, ('unexpected data files changed', changed ^ FILES)
for name, key, new_ids in [('sites_TX.csv', 'site_id', {SITE}), ('evidence_sites_TX.csv', 'evidence_id', {w['evidence_id'] for w in ws})]:
    old = {r[key]: r for r in before(name)}; now = {r[key]: r for r in read(ROOT/'data'/name)}
    assert set(now) - set(old) == new_ids and all(now[k] == old[k] for k in old), (name, 'delta is not exactly the new rows')
site = next(r for r in read(ROOT/'data/sites_TX.csv') if r['site_id'] == SITE)
assert site == site_row(list(site)) and site['org_id'] == ORG and site['county'] == 'Cooke' and site['verification_tier'] == 'B'
# V-25 restated: every active-site must-have claim carries at least one supports_B row.
must = {'existence', 'address', 'scope', 'code', 'parent', 'activity', 'liveness'}
assert must <= {w['claim_type'] for w in ws if w['tier_effect'] in ('supports_A', 'supports_B')}

# Injected defects must fail.
wc = next(w for w in ws if w['witness'].endswith('.txt'))
assert not witnessed(dict(wc, quote='3601 North I-35, Gainesville – Warehousing only.'), ita), 'fabricated quote accepted'
assert not witnessed(dict(next(w for w in ws if w['witness'] == 'FRS'), quote='48181'), ita), 'wrong county FIPS accepted'
assert not witnessed(dict(next(w for w in ws if w['claim_type'] == 'code'), witness='ITA:73266'), ita), 'Ardmore ITA record accepted for Gainesville'
weak = [w for w in ws if not (w['claim_type'] == 'parent' and w['tier_effect'] == 'supports_B')]
assert 'parent' not in {w['claim_type'] for w in weak if w['tier_effect'] in ('supports_A', 'supports_B')}, 'V-25 restatement cannot see a missing claim'

# Idempotent rebuild.
h = lambda: [hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sorted(FILES)]
pre = h(); subprocess.run([sys.executable, str(HERE/'build.py')], check=True, capture_output=True); assert pre == h(), 'rebuild changed bytes'
for f in HERE.iterdir():
    if f.suffix in {'.csv', '.md', '.txt', '.json'}:
        assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\(\d{3}\) ?\d{3}-\d{4}', f.read_text()), ('contact data', f.name)
print(f'PASS: base {base[:7]}; {SITE} created under {ORG} (tier B, Cooke), 9 evidence rows, 9 raw witnesses, 7/7 must-have claims at supports_B; 4 injected defects rejected; idempotent')
