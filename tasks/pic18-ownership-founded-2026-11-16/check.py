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
retained = {p['org_id'] for p in build.read(build.CORPUS / 'manifest.csv') if p['status'] == 'ok'}
expected = {(oid, field) for oid in retained for field in ('ownership_type', 'year_founded') if not baseline[oid][field]}
assert {(p['org_id'], p['field']) for p in frame} == expected
assert len(frame) == len(expected) == 830
assert len({p['org_id'] for p in frame}) == 419
build.validate_packet(packet)
assert {(p['org_id'], p['field']) for p in packet} <= expected
current = {r['org_id']: r for f in (build.ROOT/'data').glob('organizations_*.csv') for r in build.read(f)}
delta = {(oid, k): r[k] for oid, r in current.items() for k in r if r[k] != baseline[oid][k]}
assert delta == {(p['org_id'], p['field']): p['value'] for p in packet}
evs = {r['evidence_id']:r for f in (build.ROOT/'data').glob('evidence_organizations_*.csv') for r in build.read(f)}
for n, p in enumerate(packet, 373000):
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
print('PASS: frame',len(expected),'blank organization fields across 419 organizations; applied',len(packet),'fields across',len({p['org_id'] for p in packet}),'organizations;',dict(Counter(p['field'] for p in packet)),'; 3/3 injected defects rejected')
assert len(packet) == 58 and len({p['org_id'] for p in packet}) == 54
assert Counter(p['field'] for p in packet) == {'ownership_type': 30, 'year_founded': 28}
assert len(frame) - len(packet) == 772
report = (H/'README.md').read_text()
assert report.count('| applied |') == 58 and report.count('| held |') == 772
assert Counter(current[oid]['verification_tier'] for oid in {p['org_id'] for p in packet}) == {'A': 27, 'B': 22, 'C': 5}
