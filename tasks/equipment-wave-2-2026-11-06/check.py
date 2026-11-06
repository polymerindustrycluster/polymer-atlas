#!/usr/bin/env python3
"""Census, exact main preservation, replay and fail-before-write checks."""
import csv
import hashlib
import importlib.util
import io
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
s = importlib.util.spec_from_file_location('lane', HERE / 'build.py')
lane = importlib.util.module_from_spec(s); s.loader.exec_module(lane)
rows = lane.read(HERE / 'inputs.csv')
current = lane.read(ROOT / 'data/equipment.csv')
main = list(csv.DictReader(io.StringIO(subprocess.check_output(['git', 'show', 'origin/main:data/equipment.csv'], cwd=ROOT, text=True))))
by_id = {r['equipment_id']: r for r in current}
assert len(by_id) == len(current)
assert all(by_id[r['equipment_id']] == r for r in main), 'main equipment altered or lost'
fields = list(current[0])
assert all(by_id[r['equipment_id']] == {k: r[k] for k in fields} for r in rows)
assert {r['equipment_id'] for r in current} == {r['equipment_id'] for r in main + rows}
verdicts = lane.read(HERE / 'verdicts.csv')
assert len(verdicts) == len(rows) == 54
assert {r['equipment_id'] for r in verdicts if r['verdict'] == 'VERIFIED'} == {r['equipment_id'] for r in rows}
with tempfile.TemporaryDirectory() as d:
    data = Path(d)
    for path in [ROOT / 'data/ecosystem.csv', ROOT / 'data/programs.csv', *sorted((ROOT / 'data').glob('organizations_*.csv'))]:
        (data / path.name).write_bytes(path.read_bytes())
    path = data / 'equipment.csv'
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(main)
    cmd = [sys.executable, str(HERE / 'build.py'), '--data-dir', str(data), '--apply']
    subprocess.run(cmd, check=True, capture_output=True)
    assert lane.read(path) == current
    digest = lambda: {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
    before = digest()
    subprocess.run(cmd, check=True, capture_output=True)
    assert digest() == before, 'replay changed CSV bytes'
    for mutation in ['existing_id', 'duplicate_name', 'unheld_host', 'uc_access', 'combined_calorimeters']:
        bad = [dict(r) for r in rows]
        if mutation == 'existing_id': bad[0]['notes'] += ' Fabricated mutation.'
        if mutation == 'duplicate_name': bad[0]['equipment_id'] = 'EQP-000999'
        if mutation == 'unheld_host': bad[0]['host_org_id'] = 'ORG-999999'
        if mutation == 'uc_access': bad[16]['access_mode'] = 'not_stated'
        if mutation == 'combined_calorimeters': bad[44]['name'] += ' + Fast Scanning Calorimeter (Mettler Toledo)'
        badpath = Path(d).parent / (data.name + '-bad.csv')
        try:
            with badpath.open('w', newline='') as f:
                w = csv.DictWriter(f, fieldnames=list(bad[0])); w.writeheader(); w.writerows(bad)
            result = subprocess.run(cmd + ['--inputs', str(badpath)], capture_output=True, text=True)
            expected = {'existing_id': 'existing ID differs', 'duplicate_name': 'existing instrument duplicate', 'unheld_host': 'unheld host', 'uc_access': 'UC external-rate witness lost', 'combined_calorimeters': 'DSC/FSC grain differs'}[mutation]
            assert result.returncode and expected in result.stderr, (mutation, result.stderr)
            assert digest() == before, mutation + ' wrote data'
        finally:
            badpath.unlink()
        print(mutation, 'refused before any write')
print('PASS: 54/54 VERIFIED equipment rows; main rows preserved; exact projection; byte-idempotent replay; 5 negative controls')

if '--pages' in sys.argv:
    import html
    import re
    count = 0
    for host in sorted({r['host_org_id'] for r in rows}):
        expected = [r for r in current if r['host_org_id'] == host]
        page = (ROOT / 'build/pages/orgs' / (host + '.html')).read_text()
        section = re.search(r'<h2>Equipment and testing \((\d+) equipment rows\)</h2>.*?<tbody>(.*?)</tbody>', page, re.S)
        assert section and int(section[1]) == len(expected), host
        actual = []
        for tr in re.findall(r'<tr>(.*?)</tr>', section[2], re.S):
            cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', tr, re.S)
            assert len(cells) == 4
            actual.append((html.unescape(cells[0]), html.unescape(cells[1]), html.unescape(cells[2]),
                           html.unescape(re.search(r'href="([^"]+)"', cells[3])[1])))
        wanted = [(r['name'], r['equipment_class'].replace('_', ' '), r['access_mode'].replace('_', ' '), r['source_ref']) for r in expected]
        assert sorted(actual) == sorted(wanted), host
        count += len(expected)
    assert count == len(rows)
    print('PAGES PASS:', count, 'equipment names/classes/access/source links across 8 actual host HTML sections')
