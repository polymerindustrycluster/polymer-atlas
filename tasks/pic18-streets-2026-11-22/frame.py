#!/usr/bin/env python3
"""Frame: active tier A-C PIC-18 Ohio sites, organization has no size band (site bands and org employee_band_ohio all unknown), street_address blank.
Same definition as controller harness pic18_unknown.py (band pick). Writes frame.csv; canary = first 25 of a seeded shuffle (seed 20261122, sorted by site_id)."""
import csv, glob, random, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(R / 'scripts'))
from regions import PIC18
rd = lambda p: list(csv.DictReader(open(p, newline='', encoding='utf-8')))
O = {r['org_id']: r for f in glob.glob(str(R / 'data/organizations_*.csv')) for r in rd(f)}
E = {r['org_id']: r for r in rd(R / 'data/ecosystem.csv')}
GT = {}
for s in rd(R / 'data/sites_OH.csv'):
    if s['county'] in PIC18 and s['operating_status'] == 'active' and s['verification_tier'] and s['verification_tier'] in 'ABC':
        GT.setdefault(s['org_id'], []).append(s)
toks = lambda v: {t.strip() for t in (v or '').split(';') if t.strip() and t.strip() != 'unknown'}
rows, orgs_nb, sites_nb = [], 0, 0
for oid, ss in GT.items():
    rec = O.get(oid) or E.get(oid) or {}
    if set().union(*(toks(s['employee_band_site']) for s in ss)) or toks(rec.get('employee_band_ohio')): continue
    orgs_nb += 1; sites_nb += len(ss)
    for s in ss:
        if not s['street_address'].strip():
            rows.append(dict(site_id=s['site_id'], org_id=oid, org_name=rec.get('legal_name', ''), site_name=s['site_name'], site_type=s['site_type'], city=s['city'], zip=s['zip'], county=s['county'],
                             tier=s['verification_tier'], website=(rec.get('website') or '').strip(), org_sites_in_frame=0))
n = {}
for r in rows: n[r['org_id']] = n.get(r['org_id'], 0) + 1
for r in rows: r['org_sites_in_frame'] = n[r['org_id']]
rows.sort(key=lambda r: r['site_id']); order = [r['site_id'] for r in rows]; random.Random(20261122).shuffle(order)
rank = {s: i + 1 for i, s in enumerate(order)}
for r in rows: r['shuffle_rank'] = rank[r['site_id']]; r['canary'] = int(rank[r['site_id']] <= 25)
with open(Path(__file__).parent / 'frame.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)
print(f'orgs with no band {orgs_nb}; their active A-C PIC-18 sites {sites_nb}; frame (blank street) {len(rows)} sites of {len(n)} orgs; with website {sum(1 for r in rows if r["website"] not in ("", "none_found"))}; canary {sum(r["canary"] for r in rows)}')
