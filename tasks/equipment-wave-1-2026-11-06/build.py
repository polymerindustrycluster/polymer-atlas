#!/usr/bin/env python3
"""Idempotent L14 application. --raw-check re-fetches every admitted source before writing."""
import csv
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted

# Word-sequence normalization reused from ownership-status-2-2026-11-05/rawcheck_tool.py.
W = lambda s: re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower())

def has(text, quote):
    return bool(W(quote)) and (' ' + ' '.join(W(quote)) + ' ') in (' ' + ' '.join(W(text)) + ' ')

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip -= 1
    def handle_data(self, text):
        if not self.skip: self.parts.append(text)


def read(path):
    with path.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))


def main():
    rows = read(HERE / 'inputs.csv')
    fields = next(csv.reader((ROOT / 'data/equipment.csv').open()))
    assert len({r['equipment_id'] for r in rows}) == len(rows)
    assert len({(r['host_org_id'], r['name'].lower()) for r in rows}) == len(rows)
    assert all(1 <= int(r['equipment_id'][4:]) <= 999 for r in rows)
    hosts = {r['org_id'] for p in [ROOT / 'data/ecosystem.csv', *sorted((ROOT / 'data').glob('organizations_*.csv'))] for r in read(p)}
    assert all(r['host_org_id'] in hosts for r in rows)
    # Three hand-confirmed answers, plus a fabricated name to prove the matcher fails closed.
    for name, cls in [('Differential Scanning Calorimetry (DSC)', 'dsc'), ('Atomic Force Microscope (AFM)', 'afm'), ('Lulzbot Taz 6 (Fused deposition modeling)', 'additive_manufacturing_polymer')]:
        assert any(r['name'] == name and r['equipment_class'] == cls for r in rows), name
    assert has('TA Differential Scanning Calorimeter (DSC)', 'Differential Scanning Calorimeter')
    assert not has('TA Differential Scanning Calorimeter (DSC)', 'Fabricated instrument XYZ')
    if '--raw-check' in sys.argv:
        for url in sorted({r['source_ref'] for r in rows}):
            result = subprocess.run(['curl', '-fL', '--max-time', '45', '-A', 'Mozilla/5.0', '-sS', url], capture_output=True, check=True)
            parser = Text(); parser.feed(result.stdout.decode('utf-8', 'replace'))
            text = ' '.join(parser.parts)
            for row in [r for r in rows if r['source_ref'] == url]:
                assert has(text, row['quote']), (row['equipment_id'], 'quote absent')
                assert has(text, row['name']), (row['equipment_id'], 'name absent')
                if row['access_quote']: assert has(text, row['access_quote']), (row['equipment_id'], 'access quote absent')
            print('RAW PASS', url)
        print('Raw-check yield:', len(rows), '/', len(rows), 'equipment rows; no skipped sources')
    equipment = [{k: r[k] for k in fields} for r in rows]
    existing = {r['equipment_id']: r for r in read(ROOT / 'data/equipment.csv')}
    for row in equipment:
        if row['equipment_id'] in existing: assert existing[row['equipment_id']] == row, 'existing ID differs'
    new = [r for r in equipment if r['equipment_id'] not in existing]
    pairs = {(r['host_org_id'], r['name'].strip().lower()) for r in existing.values()}
    assert not any((r['host_org_id'], r['name'].strip().lower()) in pairs for r in new), 'existing instrument duplicate'
    if '--apply' in sys.argv and new: append_sorted(ROOT / 'data/equipment.csv', new, 'equipment_id')
    print('Known-answer 3/3; negative matcher check passed;', len(equipment), 'equipment rows;', len(new), 'new')
    print('By host:', dict(Counter(r['host_org_id'] for r in rows)))
    print('By class:', dict(Counter(r['equipment_class'] for r in rows)))

if __name__ == '__main__': main()
