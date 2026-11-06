#!/usr/bin/env python3
"""Fail on missing/duplicate gap classifications or an unworked initial desk route."""
import argparse,csv,json
from pathlib import Path
from collections import Counter,defaultdict
HERE=Path(__file__).resolve().parent
def read(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
def check(rows,require_work=False):
 frame=read(HERE/'frame.csv');health=read(HERE/'health_projected_before.csv')
 assert len(health)==632 and len({r['org_id'] for r in health})==632
 assert sum(r['healthy']=='0' for r in health)==160
 assert len(frame)==160 and len({r['org_id'] for r in frame})==160
 expected={(r['org_id'],g) for r in health if r['healthy']=='0' for g in ['tier','duplicate','website','capabilities'] if r['gap_'+g]=='1'}
 keys=[(r['org_id'],r['gap']) for r in rows]
 assert len(keys)==204 and len(set(keys))==204,'missing or duplicate gap rows'
 assert set(keys)==expected,'gap inventory differs from independent projected health flags'
 initial={(r['org_id'],r['gap']):r for r in read(HERE/'gap_routes_initial.csv')}
 assert set(initial)==set(keys)
 for r in rows:
  assert r['initial_class'] in {'a','b','c','d'}
  assert r['initial_class']==initial[r['org_id'],r['gap']]['initial_class'],'initial class rewritten'
  assert r['reason'] and r['settling_fact'] and r['prior_evidence'],'unexplained classification'
  if r['initial_class']=='a':
   assert r['source_route'] and r['route_not_tried_basis'],'unnamed desk route'
   if require_work:assert r['work_outcome'] in {'VERIFIED','STILL_UNCERTAIN'} and r['attempted_url'],'unworked desk route'
 counts=Counter(r['initial_class'] for r in rows);by=Counter(r['gap'] for r in rows)
 assert dict(counts)=={'b':52,'c':67,'a':75,'d':10},counts
 assert by=={'tier':52,'duplicate':31,'website':28,'capabilities':93},by
 org=defaultdict(set)
 for r in rows:org[r['org_id']].add(r['initial_class'])
 all_a=sum(s=={'a'} for s in org.values());assert all_a==57
 assert 569-472-all_a==40
 if require_work:
  after=read(HERE/'health_projected_after.csv');remaining=read(HERE/'remaining_gap_routes.csv')
  result=json.loads((HERE/'work_results.json').read_text())
  assert len(after)==len({r['org_id'] for r in after})==632
  assert sum(r['healthy']=='1' for r in after)==result['healthy_after']==477
  expected_after={(r['org_id'],g) for r in after for g in ['tier','duplicate','website','capabilities'] if r['gap_'+g]=='1'}
  assert {(r['org_id'],r['gap']) for r in remaining}==expected_after
  assert len(remaining)==len(expected_after)==result['remaining_gaps']==197
  assert len({r['org_id'] for r in remaining})==result['remaining_organizations']==155
  assert Counter(r['class_now'] for r in remaining)==result['remaining_classes']=={'b':55,'c':131,'d':11}
  assert result['needed_for90']==569-477==92
  assert expected_after-expected=={('ORG-001462','duplicate')}
  assert len(expected-expected_after)==result['resolved_initial_gaps']==8
 return counts
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--require-work',action='store_true');a=p.parse_args()
 rows=read(HERE/'gap_routes.csv');counts=check(rows,a.require_work)
 try:check(rows[:-1])
 except AssertionError:pass
 else:raise AssertionError('missing-row mutation silently passed')
 print(f'PASS 160-org/204-gap census; classes {dict(counts)}; 57 desk-only orgs; missing-row mutation rejected'+('; all75desk routes worked' if a.require_work else ''))
