#!/usr/bin/env python3
"""Verify exact continuation delta and one raw-checked evidence row per added value."""
import csv,io,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from health import read
BASE='419678b2e3e415194dad804af8daca649b163f3e'
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
cap=read(HERE/'capability/frame.csv');cv=read(HERE/'capability/verdicts.csv');dv=read(HERE/'duplicate_verdicts.csv');df=read(HERE/'duplicate_frame.csv')
assert len(cap)==68 and len({r['org_id'] for r in cap})==68
assert len(cv)==68 and {r['org_id'] for r in cv}=={r['org_id'] for r in cap}
assert len(df)==33 and len({(r['left'],r['right']) for r in df})==33
assert len(dv)==33 and {(r['left'],r['right']) for r in dv}=={(r['left'],r['right']) for r in df}
assert sum(r['adjudication']=='distinct' for r in dv)==7
assert {r['evidence_id'] for r in read(HERE/'rawcheck.csv') if r['raw']=='yes'}==packet.keys()
print(f'PASS {len(actual)} cells, {len(new)} append-only evidence rows, 33/33 duplicate pairs and68/68 capability verdict census; all other data unchanged')
