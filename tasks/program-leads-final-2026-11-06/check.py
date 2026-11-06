"""Packet assertions, deliberate false-duplicate/verdict injections, no data mutation."""
from pathlib import Path
import copy,hashlib
from build import HERE,read,check


def hashes():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE.parents[1]/'data').glob('*.csv')}


before=hashes();check();check();assert before==hashes()
rows=read(HERE/'verdicts.csv')
for kind in ('duplicate','missing','new_create'):
    bad=copy.deepcopy(rows)
    if kind=='duplicate':
        row=next(r for r in bad if r['verdict']=='DUPLICATE_OF');row['record_id']='PROG-000001'
    elif kind=='missing':bad.pop()
    else:bad[0]['verdict']='VERIFIED'
    try:check(bad)
    except AssertionError:pass
    else:raise AssertionError('injected defect silently passed: '+kind)
    assert before==hashes()
print('PASSno-write replay;injected false duplicate/missing lead/unauthorized create rejected')
