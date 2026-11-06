#!/usr/bin/env python3
"""L14 wave2: reuse wave1 raw matching and sorted append; preflight before any write."""
import argparse
import csv
import importlib.util
import subprocess
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('equipment_wave1', ROOT / 'tasks/equipment-wave-1-2026-11-06/build.py')
house = importlib.util.module_from_spec(spec)
spec.loader.exec_module(house)
read, has, Text, append_sorted = house.read, house.has, house.Text, house.append_sorted

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw-check', action='store_true')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data')
    parser.add_argument('--inputs', type=Path, default=HERE / 'inputs.csv')
    args = parser.parse_args()
    rows = read(args.inputs)
    fields = next(csv.reader((args.data_dir / 'equipment.csv').open()))
    assert rows and len({r['equipment_id'] for r in rows}) == len(rows)
    assert len({(r['host_org_id'], r['name'].strip().lower()) for r in rows}) == len(rows)
    assert all(100 <= int(r['equipment_id'][4:]) <= 999 for r in rows)
    hosts = {r['org_id'] for p in [args.data_dir / 'ecosystem.csv', *sorted(args.data_dir.glob('organizations_*.csv'))] for r in read(p)}
    assert all(r['host_org_id'] in hosts for r in rows), 'unheld host'
    programs = {r['program_id']: r for r in read(args.data_dir / 'programs.csv')}
    assert all(not r['program_id'] or programs[r['program_id']]['institution_org_id'] == r['host_org_id'] for r in rows), 'program host differs'
    known = [('TA Instruments Q50 Thermogravimetric Analyzer (TGA)', 'tga', 'ORG-001316'),
             ('Asylum MFP-3D-BIO Atomic Force Microscope', 'afm', 'ORG-000158'),
             ('Zeiss Crossbeam 550 Ga FIB-SEM', 'sem', 'ORG-002778')]
    for name, cls, host in known:
        assert any((r['name'], r['equipment_class'], r['host_org_id']) == (name, cls, host) for r in rows), name
    assert not has('Asylum MFP-3D-BIO Atomic Force Microscope', 'Fabricated instrument XYZ')
    equipment = [{k: r[k] for k in fields} for r in rows]
    existing = {r['equipment_id']: r for r in read(args.data_dir / 'equipment.csv')}
    for row in equipment:
        if row['equipment_id'] in existing:
            assert existing[row['equipment_id']] == row, 'existing ID differs'
    new = [r for r in equipment if r['equipment_id'] not in existing]
    pairs = {(r['host_org_id'], r['name'].strip().lower()) for r in existing.values()}
    assert not any((r['host_org_id'], r['name'].strip().lower()) in pairs for r in new), 'existing instrument duplicate'
    if args.raw_check:
        for url in sorted({r['source_ref'] for r in rows}):
            result = subprocess.run(['curl', '-fL', '--max-time', '45', '-A', 'Mozilla/5.0', '-sS', url], capture_output=True, check=True)
            page = Text(); page.feed(result.stdout.decode('utf8', 'replace'))
            text = ' '.join(page.parts)
            source_rows = [r for r in rows if r['source_ref'] == url]
            for row in source_rows:
                for claim in ['name', 'quote'] + (['access_quote'] if row['access_quote'] else []):
                    assert has(text, row[claim]), (row['equipment_id'], claim, 'absent')
            print('RAW PASS', len(source_rows), 'equipment rows', url, flush=True)
        print('RAW yield', len(rows), '/', len(rows), 'equipment rows; no skipped sources', flush=True)
    if args.apply and new:
        append_sorted(args.data_dir / 'equipment.csv', new, 'equipment_id')
    print('Known-answer 3/3; fabricated-name negative PASS;', len(rows), 'equipment rows;', len(new), 'new')
    print('By institution:', dict(Counter(r['institution'] for r in rows)))
    print('By equipment_class:', dict(Counter(r['equipment_class'] for r in rows)))

if __name__ == '__main__':
    main()
