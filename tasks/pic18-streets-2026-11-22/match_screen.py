#!/usr/bin/env python3
"""Upper bound on what the size sprint could then match: for each packet street, count street-equal (derive_last_activity.same_street) filings in the size sprint's cached
OSHA ITA / OSHA inspection / Form 5500 extracts (persist/size-sprint-2026-11-22/cache) in the same city (or ZIP) dated on/after 2021-11-22 (ruling A, 5 years).
Name is NOT tested, so a hit is a candidate filing for the size lane's own matcher, not a band. Writes match_screen.csv: site_id, kind, filing_name, year/date, count."""
import csv, re, sys
from pathlib import Path
D = Path(__file__).resolve().parent; sys.path.insert(0, str(D.parents[1] / 'scripts'))
from atlas import squash
from derive_last_activity import same_street
C = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/size-sprint-2026-11-22/cache'); csv.field_size_limit(10**9)
P = list(csv.DictReader(open(D / 'packet.csv')))
fr = {r['site_id']: r for r in csv.DictReader(open(D / 'frame.csv'))}
z5 = lambda z: re.sub(r'\D', '', z or '')[:5]
out = []
for p in P:
    street, city, zp = p['proposed_street'], p['city'], p['zip']
    for f, kind, st, ci, zi, nm, when, n in (('ita_oh.csv', 'ITA', 'street_address', 'city', 'zip_code', 'establishment_name', 'year_filing_for', 'annual_average_employees'),
                                              ('insp_oh.csv', 'inspection', 'site_address', 'site_city', 'site_zip', 'estab_name', 'open_date', 'nr_in_estab'),
                                              ('f5500_oh.csv', 'form5500', 'loc1', 'loccity', 'loczip', 'sponsor', 'tax_prd', 'active')):
        for r in csv.DictReader(open(C / f, newline='', encoding='utf-8')):
            addr = r.get(st) or ''
            if not addr or not same_street(street, addr): continue
            if squash(r.get(ci, '')) != squash(city) and not (zp and z5(r.get(zi, '')) == z5(zp)): continue
            w = r[when]; yr = int(w[:4]) if w[:4].isdigit() else 0
            if yr >= 2022 or (yr == 2021 and w[:10] >= '2021-11-22') or (kind == 'ITA' and yr >= 2021): out.append(dict(site_id=p['site_id'], kind=kind, filing_name=r[nm], date_or_year=w[:10], count=r.get(n, ''), street=addr))
with open(D / 'match_screen.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, ['site_id', 'kind', 'filing_name', 'date_or_year', 'count', 'street'], lineterminator='\n'); w.writeheader(); w.writerows(out)
print(len(P), 'packet sites;', len({o['site_id'] for o in out}), 'with >=1 street-equal filing in the 5-year window;', len(out), 'filing rows')
