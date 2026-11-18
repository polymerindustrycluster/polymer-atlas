"""check.py: recomputes the A11-113 removal against the pinned base; fails on injected defects. python3 tasks/a11-113-2026-11-18/check.py"""
import copy, csv, importlib.util, io, itertools, json, re, subprocess, tempfile
from unittest.mock import patch
from pathlib import Path
T = Path(__file__).resolve().parent
ROOT = T.parents[1]
spec = importlib.util.spec_from_file_location('build', T / 'build.py'); build = importlib.util.module_from_spec(spec); spec.loader.exec_module(build)
BASE = (T / 'base.txt').read_text().strip()
def rd(text): return list(csv.DictReader(io.StringIO(text, newline='')))
def verify(base_rows, rows, removals, adj):
    bk = [build.link_key(r) for r in base_rows]; nk = [build.link_key(r) for r in rows]
    want = [x['record_id'] for x in adj if x['grade'] == 'CREATION_ERROR' and x['change_class'] == 'uei_links']  # independent count from the adjudication
    assert len(want) == 1, f'adjudication has {len(want)} CREATION_ERROR uei_links items, expected 1'
    gone = sorted(set(bk) - set(nk))
    assert gone == want, f'removed link keys {gone} != the A11-113 key'
    assert len(nk) == len(bk) - 1, f'row count {len(nk)} != base {len(bk)} minus 1'
    assert [k for k in bk if k in set(nk)] == nk, 'rows added or reordered'
    assert all(r == next(b for b in base_rows if build.link_key(b) == build.link_key(r)) for r in rows), 'a kept row changed'
    assert [(r['table'], r['key']) for r in removals] == [('registry_links', k) for k in gone], 'REMOVALS.csv does not list exactly the removed link'
    assert all(r['reason'].strip() for r in removals)
    return dict(links_before=len(bk), links_after=len(nk), removed=len(gone), uei_links_kept=sum(r['registry'] == 'UEI' for r in rows))
def main():
    adj = json.loads(build.ADJ.read_text())['decisions']; assert next(x for x in adj if x['id'] == 'A11-113')['record_id'] in {build.link_key(r) for r in rd(subprocess.check_output(['git', 'show', f'{BASE}:data/registry_links.csv'], cwd=ROOT, text=True))}
    base_rows = rd(subprocess.check_output(['git', 'show', f'{BASE}:data/registry_links.csv'], cwd=ROOT, text=True))
    rows = list(csv.DictReader(build.LINKS.open(newline=''))); removals = list(csv.DictReader((T / 'REMOVALS.csv').open(newline='')))
    got = verify(base_rows, rows, removals, adj); print('PASS', got)
    assert got == dict(links_before=6025, links_after=6024, removed=1, uei_links_kept=sum(r['registry'] == 'UEI' for r in base_rows) - 1), got
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASE, '--', 'data'], cwd=ROOT, text=True).split()
    assert changed == ['data/registry_links.csv'], f'data files changed: {changed}'
    out = subprocess.run(['python3', 'scripts/check_row_loss.py', '--base', BASE], cwd=ROOT, capture_output=True, text=True); assert out.returncode == 0, out.stdout + out.stderr
    assert not re.search(r'requests|urllib|http\.client|api_key', (T / 'build.py').read_text()), 'build.py may call an API'
    before = build.LINKS.read_bytes(), (T / 'REMOVALS.csv').read_bytes(); build.main()
    assert before == (build.LINKS.read_bytes(), (T / 'REMOVALS.csv').read_bytes()), 'rebuild changed files'
    def inject(name, mut):
        r, m = copy.deepcopy(rows), copy.deepcopy(removals); mut(r, m)
        try: verify(base_rows, r, m, adj)
        except AssertionError as x: print('  caught', name, '->', str(x)[:80]); return
        raise SystemExit(f'FAIL: injected defect not caught: {name}')
    inject('removal without a REMOVALS row', lambda r, m: m.clear())
    inject('second link removed', lambda r, m: r.pop(next(i for i, x in enumerate(r) if x['registry'] == 'UEI')))
    inject('second link removed (non-UEI)', lambda r, m: r.pop(0))
    inject('removed link left in place', lambda r, m: r.append(next(b for b in base_rows if build.link_key(b) == adj_key(adj))))
    inject('kept row altered', lambda r, m: r[0].update(match_basis='edited'))
    inject('truncated file (100 rows)', lambda r, m: r.__delitem__(slice(100, None)))
    # Codex's cut-short-write reproduction (PR #382 review), on a temp copy of the base: a write that dies after 100 rows must leave the target intact, and a retry must give base minus 1
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp); f = d / 'registry_links.csv'; f.write_bytes(subprocess.check_output(['git', 'show', f'{BASE}:data/registry_links.csv'], cwd=ROOT))
        with patch.object(build, 'T', d), patch.object(build, 'LINKS', f):
            real = build.write_atomic
            def cut(path, header, rows, _real=real):
                def dying(): yield from itertools.islice(rows, 100); raise OSError('injected interrupted write')
                return _real(path, header, dying())
            try:
                with patch.object(build, 'write_atomic', cut): build.main()
                raise SystemExit('FAIL: cut-short write did not raise')
            except OSError: pass
            assert len(list(csv.DictReader(f.open(newline='')))) == 6025 and not list(d.glob('*.tmp')), 'cut-short write damaged the target or left a temp file'
            build.main(); n = len(list(csv.DictReader(f.open(newline=''))))
            assert n == 6024, f'retry left {n} links, expected 6024'
        with tempfile.TemporaryDirectory() as tmp:  # a target already truncated by some other writer: the builder must refuse, not report success
            d = Path(tmp); f = d / 'registry_links.csv'; lines = subprocess.check_output(['git', 'show', f'{BASE}:data/registry_links.csv'], cwd=ROOT, text=True).splitlines(True)
            f.write_text(''.join(lines[:101]))
            with patch.object(build, 'T', d), patch.object(build, 'LINKS', f):
                try: build.main(); raise SystemExit('FAIL: builder accepted a truncated target')
                except AssertionError as x: print('  caught truncated target on retry ->', str(x)[:70])
        print('  caught cut-short write (target intact, no temp file, retry gives 6024)')
    print('check.py: PASS (6 injected defects caught, plus the cut-short-write reproduction and a truncated-target retry)')
def adj_key(adj): return next(x for x in adj if x['id'] == 'A11-113')['record_id']
if __name__ == '__main__': main()
