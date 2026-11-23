#!/usr/bin/env python3
"""Replay the controller's PIC-18 frame at the pinned base; control answers are opt-in."""
import argparse
import csv
import io
import random
import re
import subprocess
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
BASE = '454dc9f57ff6f676b9c0c1742203f089ca898805'
SEED = 20261123
sys.path.insert(0, str(ROOT / 'scripts'))
from regions import PIC18


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True)


def tokens(value):
    return {part.strip() for part in (value or '').split(';')} - {'', 'unknown'}


def frame():
    files = git('ls-tree', '--name-only', BASE, 'data/').splitlines()

    def rows(prefix):
        for path in files:
            if Path(path).name.startswith(prefix):
                yield from csv.DictReader(io.StringIO(git('show', f'{BASE}:{path}')))

    records = {r['org_id']: r for r in rows('ecosystem.csv')}
    records.update({r['org_id']: r for r in rows('organizations_')})
    sites = {}
    for row in rows('sites_'):
        if (row['state'] == 'OH' and row['county'] in PIC18 and row['operating_status'] == 'active'
                and row['verification_tier'] in ('A', 'B', 'C')):
            sites.setdefault(row['org_id'], set()).update(tokens(row['markets_served']))
    with (D / 'prior_ids.csv').open() as f:
        excluded = {r['org_id'] for r in csv.DictReader(f)}
    assert len(excluded) == 25
    pools = {'unknown': [], 'control': []}
    counts = {'unknown': 0, 'unknown_populated': 0, 'unknown_web': 0, 'control_web': 0}
    known = {}
    for oid, site_terms in sorted(sites.items()):
        record = records.get(oid, {})
        held = site_terms or tokens(record.get('markets_served'))
        cohort = 'control' if held else 'unknown'
        counts['unknown'] += not held
        web = record.get('website', '').strip()
        counts['unknown_populated'] += bool(web) and not held
        if not web or web.lower() in ('none_found', 'none', 'n/a', 'unknown') or ' ' in web or '.' not in web:
            continue
        counts[cohort + '_web'] += 1
        if oid not in excluded:
            url = web if re.match(r'https?://', web, re.I) else 'https://' + web
            pools[cohort].append((oid, url))
            known[oid] = held
    assert (len(sites), counts['unknown'], counts['unknown_populated'], counts['unknown_web']) == (794, 316, 274, 266), counts
    drawn = []
    for cohort, size in [('unknown', 25), ('control', 10)]:
        random.Random(SEED).shuffle(pools[cohort])
        drawn.extend((cohort, i, oid, url) for i, (oid, url) in enumerate(pools[cohort][:size], 1))
    return drawn, known, counts, {c: len(p) for c, p in pools.items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--score', action='store_true', help='reveal recorded control terms after reading')
    args = parser.parse_args()
    drawn, known, counts, pool_sizes = frame()
    if args.score:
        for cohort, _, oid, _ in drawn:
            if cohort == 'control':
                print(oid, ';'.join(sorted(known[oid])))
    else:
        with (D / 'frame.csv').open('w', newline='') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(('cohort', 'rank', 'org_id', 'website'))
            writer.writerows(drawn)
        print(counts, pool_sizes)
