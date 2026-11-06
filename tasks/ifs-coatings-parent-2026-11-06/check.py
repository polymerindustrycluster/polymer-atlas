"""Named check: exact delta vs the merge-base, raw witnesses, idempotent rebuild, injected defects fail."""
import csv, hashlib, io, re, subprocess, sys

import build
from build import HERE, ROOT, ORG, SITE, OLD, PERSIST, read, witnessed

assert PERSIST.is_dir(), f'persisted witnesses missing: {PERSIST}'
git = lambda *a: subprocess.check_output(['git', *a], cwd=ROOT, text=True)
base = git('merge-base', 'HEAD', 'origin/main').strip()
def before(name): return list(csv.DictReader(io.StringIO(git('show', f'{base}:data/{name}'))))

ws = read(HERE/'witnesses.csv'); ita = {r['establishment_id']: r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
assert len(ws) == 11 and all(witnessed(w, ita) for w in ws)
changed = set(git('diff', '--name-only', base, '--', 'data/').split()) | set(git('diff', '--name-only', '--', 'data/').split())
FILES = {'data/organizations_TX.csv', 'data/sites_OK.csv', 'data/evidence_organizations_TX.csv', 'data/evidence_sites_OK.csv'}
assert changed == FILES, ('unexpected data files changed', changed ^ FILES)

def site_ok(row): return row['org_id'] == ORG and build.CERT in row['sources'] and OLD in row['notes']
for name, key, new_ids, cols in [('organizations_TX.csv', 'org_id', {ORG}, set()), ('sites_OK.csv', 'site_id', set(), {'org_id', 'sources', 'notes', 'last_verified'}),
                                  ('evidence_organizations_TX.csv', 'evidence_id', {w['evidence_id'] for w in ws if w['record_table'] == 'organizations'}, set()),
                                  ('evidence_sites_OK.csv', 'evidence_id', {w['evidence_id'] for w in ws if w['record_table'] == 'sites'}, set())]:
    old = {r[key]: r for r in before(name)}; now = {r[key]: r for r in read(ROOT/'data'/name)}
    assert old.keys() <= now.keys(), (name, 'row removed')
    assert set(now) - set(old) == new_ids, (name, 'new rows', set(now) - set(old))
    edits = {(k, c) for k in old for c in old[k] if old[k][c] != now[k][c]}
    assert edits == {(SITE, c) for c in cols if (SITE, c) in edits} and {c for _, c in edits} == cols, (name, edits)
assert site_ok(next(r for r in read(ROOT/'data/sites_OK.csv') if r['site_id'] == SITE))

# Injected defects must fail.
w0 = next(w for w in ws if w['source_class'] == 'own_site')
assert not witnessed(dict(w0, quote='IFS Industries operates 3430 Cypert Way'), ita), 'fabricated quote accepted'
weins = next(w for w in ws if w['witness'] == 'ITA:73266')
assert not witnessed(dict(weins, quote='231628033'), ita), 'IFS Industries EIN accepted as the operator EIN'
s = next(r for r in before('sites_OK.csv') if r['site_id'] == SITE)
assert not site_ok(s), 'site left at the old parent accepted'

# Idempotent rebuild.
h = lambda: [hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sorted(FILES)]
pre = h(); subprocess.run([sys.executable, str(HERE/'build.py')], check=True, capture_output=True); assert pre == h(), 'rebuild changed bytes'
for f in HERE.iterdir():
    if f.suffix in {'.csv', '.md', '.txt'}:
        assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\(\d{3}\) ?\d{3}-\d{4}', f.read_text()), ('contact data', f.name)
print(f'PASS: base {base[:7]}; 1 org created, {SITE} re-pointed {OLD}->{ORG} (4 cells), 11 evidence rows, 11 raw witnesses; 3 injected defects rejected; idempotent')
