#!/usr/bin/env python3
"""Apply the fixed L14 residue packet, preflight all namespaces before any write."""
import argparse
import csv
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted

def read(p):
    with p.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))

def plan(data):
    inputs, verdicts = read(HERE / 'inputs.csv'), read(HERE / 'verdicts.csv')
    assert len(inputs) == len(verdicts) == 26
    assert len({r['lead_id'] for r in verdicts}) == 26
    assert {r['cluster_id'] for r in inputs} == {r['lead_id'] for r in verdicts}
    assert all(r['verdict'] in {'VERIFIED', 'DUPLICATE_OF', 'REJECT', 'STILL_UNCERTAIN'} for r in verdicts)
    evidence = read(HERE / 'evidence_rows.csv')
    for site in read(HERE / 'creates_sites.csv'):
        assert any(r['record_table'] == 'sites' and r['record_id'] == site['site_id']
                   and r['claim_type'] == 'parent' and site['org_id'] in r['claim_detail']
                   for r in evidence), 'missing site parent evidence'
    specs = [('creates_orgs.csv', 'organizations_US.csv', 'org_id', 'organizations_*.csv', 9600, 9699),
             ('creates_sites.csv', 'sites_OH.csv', 'site_id', 'sites_*.csv', 13100, 13199),
             ('evidence_rows.csv', None, 'evidence_id', 'evidence_*.csv', 295000, 299999)]
    pending = {}
    org_dest = {r["org_id"]: p.name for p in data.glob("organizations_*.csv") for r in read(p)}
    org_dest["ORG-009600"] = "organizations_US.csv"
    for src, target, key, glob, lo, hi in specs:
        old = {}
        for p in sorted(data.glob(glob)) + ([data / 'ecosystem.csv'] if key == 'org_id' else []):
            for r in read(p):
                assert r[key] not in old, ('duplicate existing ID', r[key])
                old[r[key]] = (p, r)
        rows = read(HERE / src)
        assert len({r[key] for r in rows}) == len(rows)
        for r in rows:
            assert lo <= int(r[key].split('-')[1]) <= hi
            dest = target or ('evidence_' + org_dest[r['record_id']] if r['record_table'] == 'organizations' else 'evidence_sites_OH.csv')
            p = data / dest
            assert set(r) == set(next(csv.reader(p.open())))
            if r[key] in old:
                assert old[r[key]] == (p, r), ('ID collision or changed packet', r[key])
            else: pending.setdefault((p, key), []).append(r)
    sites = [r for p in data.glob('sites_*.csv') for r in read(p)]
    orgs = [r for p in data.glob('organizations_*.csv') for r in read(p)]
    neworg = read(HERE / 'creates_orgs.csv')[0]
    assert not any(r['org_id'] != neworg['org_id'] and 'peakperformancepolymers.com' in r['website'].lower() for r in orgs), 'domain duplicate'
    assert not any(r['site_id'] != 'SITE-013100' and re.sub(r'[^a-z0-9]', '', r['street_address'].lower()) in {'9109stateroute250nw','9109us250nw'} for r in sites), 'address duplicate'
    assert any(r['site_id'] == 'SITE-001473' and r['org_id'] == 'ORG-001426' for r in sites), 'duplicate target missing'
    path = data / 'registry_links.csv'
    key = lambda r: (r['org_id'], r['registry'], r['registry_id'])
    old_links = {key(r): r for r in read(path)}
    assert len(old_links) == len(read(path)), 'duplicate existing registry triple'
    additions = read(HERE / 'registry_additions.csv')
    assert len(additions) == len({key(r) for r in additions}) == 4
    pinned = read(ROOT / 'tasks/discovery-pic18-2026-11-03/L1/registry_link_candidates.csv')
    fullkey = lambda r: key(r) + (r['site_id'],)
    assert {fullkey(r) for r in additions} == {fullkey(r) for r in pinned}, 'registry scope changed'
    assert {(r['registry'], r['registry_id']) for r in additions} == {(r['registry'], r['registry_id']) for r in read(HERE / 'registry_sources.csv')}, 'registry witnesses differ from proposed links'
    site_org = {r['site_id']: r['org_id'] for r in sites}
    for row in additions:
        assert row['org_id'] in org_dest
        if row['site_id']: assert site_org[row['site_id']] == row['org_id']
        if key(row) in old_links: assert old_links[key(row)] == row, 'registry triple changed'
    new_links = [r for r in additions if key(r) not in old_links]
    if new_links: pending[(path, None)] = new_links
    return pending

def raw_check():
    # Reuse the house word normalizer without importing its unavailable Windows fetch client.
    import importlib.util
    spec = importlib.util.spec_from_file_location('house_prep', ROOT / 'tasks/evidence-repair-2-2026-11-04/prep.py')
    house = importlib.util.module_from_spec(spec); spec.loader.exec_module(house)
    from html.parser import HTMLParser
    class Text(HTMLParser):
        def handle_data(self, data): self.parts.append(data)
    def words(text): return ' ' + ' '.join(house.W(text)) + ' '
    def has(text, quote): return bool(house.W(quote)) and words(quote) in words(text)
    quote_rows = [r for r in read(HERE / 'evidence_rows.csv')
                  if int(r['evidence_id'][4:]) < 295008 or r['evidence_id'] == 'EVD-295013']
    urls = {r['source_ref'] for r in quote_rows} | {'https://www.nexxta.com/locations'}
    with tempfile.TemporaryDirectory() as tmp:
        for n, url in enumerate(sorted(urls)):
            p = Path(tmp) / f'{n}.raw'
            subprocess.run(['curl', '-fL', '--max-time', '45', '-A', 'Mozilla/5.0', '-sS', url, '-o', str(p)], check=True)
            if p.read_bytes().startswith(b'%PDF'):
                subprocess.run(['pdftotext', '-layout', str(p), str(p.with_suffix('.txt'))], check=True)
                text = p.with_suffix('.txt').read_text()
            else:
                t = Text(); t.parts=[]; t.feed(p.read_text()); text=' '.join(t.parts)
            for r in quote_rows:
                if r['source_ref'] == url:
                    quote = r['claim_detail'].split('"')[1]
                    assert has(text, quote), (r['evidence_id'], 'raw quote absent')
            if url.endswith('NOE.pdf'):
                assert has(text, '9109 State Route 250')
                # shortcut: fixed columns for this permit witness; re-check layout if the source changes.
                subprocess.run(['pdftotext', '-layout', '-f', '277', '-l', '277', str(p), str(p.with_suffix('.parent.txt'))], check=True)
                lines = p.with_suffix('.parent.txt').read_text().splitlines()
                hits = [i for i, line in enumerate(lines) if '0GRN00360*BG' in line]
                assert len(hits) == 1, 'parent permit row missing or repeated'
                block = lines[hits[0]:hits[0]+3]
                for start, end, expected in [(26, 51, 'Peak Performance Polymers'),
                                             (75, 90, 'Peak Performance Polymers'),
                                             (91, 113, '9109 State Route 250 NW'),
                                             (113, 129, 'Strasburg')]:
                    assert has(' '.join(line[start:end].strip() for line in block), expected), 'parent permit column changed'
            elif 'nexxta.com' in url: assert has(text, '150 E Longview Ave') and has(text, '26 injection molding presses')
            else: assert has(text, 'CUSTOM POLYURETHANE MANUFACTURING')
            assert not has(text, 'Fabricated polymer plant at 9999 Nowhere'), 'negative control'
            print('RAW PASS', url)
    print('Raw evidence yield9/9; source yield3/3; hand-known manufacturer/address/held-duplicate3/3 plus fabricated negative PASS')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-dir',type=Path,default=ROOT/'data');ap.add_argument('--apply',action='store_true');ap.add_argument('--raw-check',action='store_true');a=ap.parse_args()
    pending=plan(a.data_dir.resolve())
    if a.raw_check:
        raw_check()
        subprocess.run([sys.executable, str(HERE / "verify_registry.py")], check=True)
    if a.apply:
        for (p,key),rows in pending.items():
            if key is not None: append_sorted(p,rows,key)
            else:
                # Registry rows have a composite key; append_sorted requires a unique single-ID column.
                old = read(p)
                with p.open('w', newline='', encoding='utf-8') as handle:
                    writer = csv.DictWriter(handle, fieldnames=list(old[0]), lineterminator='\n')
                    writer.writeheader(); writer.writerows(old + rows)
    print('PASS census26/26; proposed1organization+1site+14evidence+4registrylinks; pending',sum(map(len,pending.values())), 'rows')

if __name__=='__main__':main()
