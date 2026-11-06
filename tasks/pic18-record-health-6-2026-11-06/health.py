#!/usr/bin/env python3
"""T1 organization-grain health; exact active Ring 1–2 Ohio sites in PIC-18."""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from atlas import domain_key, domain_match, name_key, street_key
from regions import PIC18


def read(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def health(orgs, sites, ecosystem_ids=()):
    assert len({o['org_id'] for o in orgs}) == len(orgs), 'duplicate org IDs'
    assert len({s['site_id'] for s in sites}) == len(sites), 'duplicate site IDs'
    by_id = {o['org_id']: o for o in orgs}
    assert all(s['org_id'] in by_id or s['org_id'] in ecosystem_ids for s in sites), 'unknown site owner'
    sites = [s for s in sites if s['org_id'] in by_id]  # ecosystem sites do not enter organization T1
    live = {o['org_id']: o for o in orgs if o['status'] not in {'closed', 'merged', 'acquired'}}
    footprint = {s['org_id'] for s in sites if s['operating_status'] == 'active'
                 and s['state'] == 'OH' and s['county'] in PIC18 and s['ring_primary'] in {'1', '2'}}
    names, streets, osites = defaultdict(set), defaultdict(set), defaultdict(list)
    for o in live.values():
        if name_key(o['legal_name']):
            names[name_key(o['legal_name'])].add(o['org_id'])
    for s in sites:
        osites[s['org_id']].append(s)
        if s['org_id'] in live and s['operating_status'] == 'active' and street_key(s['street_address']):
            streets[(street_key(s['street_address']), s['city'].strip().lower(), s['state'])].add(s['org_id'])
    domains = {oid: domain_key(o['website']) if o['website'].strip().lower() != 'none_found' else '' for oid, o in by_id.items()}
    out = []
    for oid in sorted(footprint):
        o = by_id[oid]
        peers = names[name_key(o['legal_name'])] - {oid}
        for pid, p in live.items():
            if pid != oid and domain_match(domains[oid], domains[pid]):
                peers.add(pid)
        for s in osites[oid]:
            if s['operating_status'] == 'active' and street_key(s['street_address']):
                peers |= streets[(street_key(s['street_address']), s['city'].strip().lower(), s['state'])] - {oid}
        flags = dict(gap_tier=int(o['verification_tier'] in {'C', 'U'}),
                     gap_duplicate=int(bool(peers)), gap_website=int(not o['website'].strip() or o['website'].strip().lower() == 'none_found'),
                     gap_capabilities=int(not any(r.get('processes', '').strip() or r.get('materials', '').strip()
                                                 for r in [o] + osites[oid])))
        out.append(dict(org_id=oid, legal_name=o['legal_name'], **flags,
                        duplicate_org_ids=';'.join(sorted(peers)), gap_count=sum(flags.values()), healthy=int(not any(flags.values()))))
    return out


def self_check():
    def org(i, **kw):
        return dict(org_id=i, legal_name=i, status='active', website='', verification_tier='B', processes='', materials='', **kw)
    def site(i, o, **kw):
        r = dict(site_id=i, org_id=o, operating_status='active', state='OH', county='Summit', ring_primary='1', street_address='', city='Akron', processes='', materials='')
        r.update(kw); return r
    a, b, c, d, e = [org(i) for i in 'abcde']
    a.update(website='https://example.com', legal_name='Acme, Inc.', materials='pvc')
    b.update(website='https://www.example.com/x', legal_name='Acme LLC')
    c.update(website='https://unique.com', verification_tier='C')
    d.update(website='none_found')
    e.update(website='https://other.com', materials='pvc')
    rows = health([a,b,c,d,e], [site('1','a'),site('2','c',materials='pvc'),site('3','d',county='Erie'),site('4','e',state='PA')])
    assert len(rows) == 3 and rows[0]['duplicate_org_ids'] == 'b'
    assert rows[1]['gap_tier'] == 1 and rows[1]['gap_capabilities'] == 0
    assert rows[2]['gap_website'] == 1 and rows[2]['gap_capabilities'] == 1
    a['website'] = 'none_found'; b['website'] = 'none_found'; b['legal_name'] = 'Beta'
    assert health([a,b,c,d,e], [site('1','a')])[0]['gap_duplicate'] == 0
    a['website'] = 'https://example.com'; b['website'] = 'https://example.com'
    b.update(status='merged')
    assert health([a,b,c,d,e], [site('1','a')])[0]['healthy'] == 1
    a['website'] = ''
    assert health([a,b,c,d,e], [site('1','a')])[0]['healthy'] == 0
    a['website']='https://example.com'; a['legal_name']='Alpha'
    b.update(status='active',website='https://beta.com',legal_name='Beta')
    r=health([a,b], [site('1','a',street_address='123 Main Street'),site('2','b',street_address='123 Main St')])
    assert r[0]['gap_duplicate'] == 1
    print('health self-check passed (domain/name/street, dead peers, geography, site capability, injected missing website)')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--data-dir', type=Path, default=ROOT/'data')
    p.add_argument('--output', type=Path, default=Path(__file__).with_name('health.csv'))
    p.add_argument('--self-check', action='store_true')
    a = p.parse_args()
    if a.self_check:
        self_check()
    rows = health([r for f in sorted(a.data_dir.glob('organizations_*.csv')) if not f.name.endswith('_all.csv') for r in read(f)],
                  [r for f in sorted(a.data_dir.glob('sites_*.csv')) if not f.name.endswith('_all.csv') for r in read(f)], {r['org_id'] for r in read(a.data_dir/'ecosystem.csv')})
    assert rows, 'empty denominator'
    with a.output.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)
    n = sum(r['healthy'] for r in rows)
    print(f'T1: {n}/{len(rows)} PIC-18 Ring 1–2 organizations = {100*n/len(rows):.2f}% free of blocking gaps')
