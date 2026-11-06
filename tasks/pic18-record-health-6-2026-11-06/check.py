#!/usr/bin/env python3
"""Verify exact continuation delta and one raw-checked evidence row per added value."""
import csv,io,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from health import read
BASE='97ee6bc2a4475a47d8449ca79db688fb9114ab0f'
def old(p):return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',f'{BASE}:{p.relative_to(ROOT)}'],text=True))))
expected={(r['org_id'],r['field']):(r['old'],r['new']) for r in read(HERE/'edits.csv')};actual={}
for p in ROOT.joinpath('data').glob('*.csv'):
 before=old(p);after=read(p)
 if p.name.startswith('organizations_'):
  a={r['org_id']:r for r in before};b={r['org_id']:r for r in after};assert a.keys()==b.keys()
  for oid,row in b.items():
   for k,v in row.items():
    if v!=a[oid][k]:actual[oid,k]=(a[oid][k],v)
 elif not p.name.startswith('evidence_'):assert before==after,p
assert actual==expected,(actual,expected)
packet={r['evidence_id']:r for r in read(HERE/'evidence_packet.csv')};new={}
for p in ROOT.joinpath('data').glob('evidence_*.csv'):
 a={r['evidence_id']:r for r in old(p)};b={r['evidence_id']:r for r in read(p)}
 assert all(b.get(k)==v for k,v in a.items()),p
 new.update({k:v for k,v in b.items() if k not in a})
assert new.keys()==packet.keys()
assert all(all(packet[k][f]==v for f,v in r.items()) for k,r in new.items())
for (oid,field),(_,value) in expected.items():
 if field!='notes':
  for term in value.split(';'):assert sum(r['record_id']==oid and r['field']==field and r['value']==term for r in packet.values())==1
assert {r['evidence_id'] for r in read(HERE/'rawcheck.csv') if r.get('raw_sha256')}==packet.keys()
import subprocess as sp
assert sp.run(['python3',str(HERE/'check_routes.py'),'--require-work']).returncode==0
print(f'PASS {len(actual)} cells, {len(new)} append-only evidence rows, classification separately checked; all other data unchanged')
