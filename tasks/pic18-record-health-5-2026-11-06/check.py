#!/usr/bin/env python3
"""Assert every changed data cell against the evidence packet; legacy evidence stays append-only."""
import csv
import io
import subprocess
from pathlib import Path
from health import read, self_check, health

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = '547d51b882ad4f10f9c1284e03236c015b754061'

def old(path):
    return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',f'{BASE}:{path.relative_to(ROOT)}'],text=True,cwd=ROOT))))

self_check()
edits=read(HERE/'edits.csv')
expected={(e['org_id'],e['field']):(e['old'],e['new']) for e in edits}
actual={}
for path in ROOT.joinpath('data').glob('organizations_*.csv'):
    before={r['org_id']:r for r in old(path)}
    after={r['org_id']:r for r in read(path)}
    assert before.keys()==after.keys(), 'unexpected create/delete'
    for oid,row in after.items():
        for field,value in row.items():
            if value!=before[oid][field]: actual[oid,field]=(before[oid][field],value)
assert actual==expected, (actual,expected)
packet={r['evidence_id']:r for r in read(HERE/'evidence_packet.csv')}
for e in edits:
    assert e['evidence_ids'] and all(packet[i]['record_id']==e['org_id'] for i in e['evidence_ids'].split(';'))
new={}
for path in ROOT.joinpath('data').glob('evidence_*.csv'):
    before={r['evidence_id']:r for r in old(path)}
    after={r['evidence_id']:r for r in read(path)}
    assert all(after.get(k)==v for k,v in before.items()), 'legacy evidence changed'
    new.update({k:v for k,v in after.items() if k not in before})
assert new.keys()==packet.keys()
assert all(all(packet[k][field]==value for field,value in row.items()) for k,row in new.items())
print(f'PASS: {len(actual)} changed organization cells all evidenced; {len(new)} evidence rows append-only; no organization creates/deletes')
path=ROOT/'data/relationships.csv'
before={r['relationship_id']:r for r in old(path)}
after={r['relationship_id']:r for r in read(path)}
assert all(after.get(k)==v for k,v in before.items())
assert after==before, 'unexpected relationship edit'
for path in ROOT.joinpath('data').glob('sites_*.csv'):
    assert old(path)==read(path), 'unexpected site edit'
print('PASS: no relationship or site edits')
frame=read(HERE/'frame.csv');ver=read(HERE/'verdicts.csv')
assert len(frame)==62 and len({r['org_id'] for r in frame})==62
assert len(ver)==62 and {r['org_id'] for r in ver}=={r['org_id'] for r in frame}
assert {e['org_id'] for e in edits}<={r['org_id'] for r in frame}
for e in edits:
 assert e['field']=='verification_tier'
 proof=[packet[i] for i in e['evidence_ids'].split(';')]
 assert {'existence','address','scope'}<={r['claim_type'] for r in proof if r['source_class']=='own_site' and r['tier_effect']=='supports_A'}
for path in ROOT.joinpath('data').glob('*.csv'):
 if not path.name.startswith(('organizations_','evidence_')):assert old(path)==read(path),path
print('PASS:62/62 unique verdict census;ownmust-have tierproof;allother data unchanged')
