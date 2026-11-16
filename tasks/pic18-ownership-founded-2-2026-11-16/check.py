#!/usr/bin/env python3
"""Check packet yield, corpus hashes, applied cells, evidence and mutation rejection."""
import copy
import json
import subprocess
from collections import Counter
import build

H = build.HERE
packet = json.loads((H / 'proposals.json').read_text())
frame = json.loads((H / 'frame.json').read_text())
base = subprocess.check_output(['git', 'merge-base', 'HEAD', 'origin/main'], text=True).strip()
files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', base, 'data'], text=True).splitlines()
import csv, io
baseline = {}
for f in files:
    if f.startswith('data/organizations_') and f.endswith('.csv'):
        baseline.update({r['org_id']: r for r in csv.DictReader(io.StringIO(subprocess.check_output(['git', 'show', base+':'+f], text=True)))})
groups = {}
for p in build.read(build.CORPUS / 'manifest.csv'):
    if p['status'] == 'ok':
        groups.setdefault(p['org_id'], []).append(p)
retained = {oid for oid, pages in groups.items() if all(p['pass'] == '2' for p in pages)}
assert sum(len(groups[oid]) for oid in retained) == 954
expected = {(oid, field) for oid in retained for field in ('ownership_type', 'year_founded') if not baseline[oid][field]}
assert {(p['org_id'], p['field']) for p in frame} == expected
assert len(frame) == len(expected) == 411
assert len({p['org_id'] for p in frame}) == 209
build.validate_packet(packet)
assert {(p['org_id'], p['field']) for p in packet} <= expected
current = {r['org_id']: r for f in (build.ROOT/'data').glob('organizations_*.csv') for r in build.read(f)}
delta = {(oid, k): r[k] for oid, r in current.items() for k in r if r[k] != baseline[oid][k]}
assert delta == {(p['org_id'], p['field']): p['value'] for p in packet}
evs = {r['evidence_id']:r for f in (build.ROOT/'data').glob('evidence_organizations_*.csv') for r in build.read(f)}
for n, p in enumerate(packet, 373058):
    e = evs[f'EVD-{n:06d}']
    assert e['record_id'] == p['org_id'] and e['source_ref'] == p['url']
    assert e['claim_detail'] == f'{p["field"]}={p["value"]}: "{p["quote"]}"'
for key, value in [('quote', 'fabricated sentence absent from the retained source 987654321'), ('text_sha256', '0'*64), ('field', 'sources')]:
    bad = copy.deepcopy(packet); bad[0][key] = value
    try:
        build.validate_packet(bad)
    except AssertionError:
        pass
    else:
        raise AssertionError('mutation survived: '+key)
print('PASS: frame',len(expected),'blank organization fields across 209 organizations; applied',len(packet),'fields across',len({p['org_id'] for p in packet}),'organizations;',dict(Counter(p['field'] for p in packet)),'; 3/3 injected defects rejected')

assert len(packet) == 76 and len({p['org_id'] for p in packet}) == 64
assert Counter(p['field'] for p in packet) == {'ownership_type': 27, 'year_founded': 49}
assert Counter(p['via'] for p in packet) == {'direct': 71, 'reader': 5}
assert len(frame) - len(packet) == 335
assert Counter(current[oid]['verification_tier'] for oid in {p['org_id'] for p in packet}) == {'A': 31, 'B': 32, 'C': 1}
report = (H/'README.md').read_text()
assert report.count('| applied |') == 76 and report.count('| held |') == 335
