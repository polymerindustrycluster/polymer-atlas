#!/usr/bin/env python3
"""Idempotent builder. This pass adjudicated 72 held leads and applied ZERO data rows:
no lead reached VERIFIED, so there is no organization, site or evidence row to append.
build.py proves that: it checks the packet and the reserved ID blocks, and writes counts.json."""
import csv, json, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BLOCKS = {'org_id': (14300, 14499), 'site_id': (20400, 20599), 'evidence_id': (391000, 392999)}

def read(p):
    with open(p, newline='', encoding='utf-8') as f: return list(csv.DictReader(f))

def used_ids(data=ROOT / 'data'):
    """Every ID in this lane's blocks that already exists in data/ (must stay empty)."""
    out = []
    for p in sorted(data.glob('*.csv')):
        for r in read(p):
            for col, (lo, hi) in BLOCKS.items():
                v = r.get(col, '')
                if v and v.split('-')[-1].isdigit() and lo <= int(v.split('-')[-1]) <= hi: out.append((p.name, v))
    return out

def counts(verdicts):
    return dict(leads_adjudicated=len(verdicts), by_verdict=dict(Counter(v['verdict'] for v in verdicts)),
                applied=sum(v['disposition'] == 'applied' for v in verdicts),
                held=sum(v['disposition'] == 'held' for v in verdicts), data_rows_added=0)

if __name__ == '__main__':
    v = read(HERE / 'verdicts.csv')
    assert all(r['verdict'] in {'VERIFIED', 'DUPLICATE_OF', 'REJECT', 'STILL_UNCERTAIN'} for r in v)
    assert not any(r['verdict'] == 'VERIFIED' for r in v), 'a VERIFIED row needs a create path this builder does not have'
    assert not used_ids(), used_ids()
    c = counts(v)
    (HERE / 'counts.json').write_text(json.dumps(c, indent=1, sort_keys=True) + '\n')
    print(c)
