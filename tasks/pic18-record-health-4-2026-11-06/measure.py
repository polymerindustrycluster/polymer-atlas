#!/usr/bin/env python3
"""Preserve original T1; report dated-distinct-pair exclusion as a separate scenario."""
from pathlib import Path
from health import read,health
from build import write
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
org=[r for p in sorted((ROOT/'data').glob('organizations_*.csv')) for r in read(p)]
sites=[r for p in sorted((ROOT/'data').glob('sites_*.csv')) for r in read(p)]
rows=health(org,sites,{r['org_id'] for r in read(ROOT/'data/ecosystem.csv')});write(HERE/'health.csv',rows)
ver=read(HERE/'duplicate_verdicts.csv');distinct={tuple(sorted((r['left'],r['right']))) for r in ver if r['adjudication']=='distinct'}
assert all(r['verdict']=='VERIFIED' and r['as_of']=='2026-11-06' for r in ver if r['adjudication']=='distinct')
assert len(distinct)==7
witness={tuple(sorted((r['left'],r['right']))) for r in read(HERE/'distinct_witnesses.csv')}
assert distinct==witness
adjusted=[]
for r in rows:
 peers=[p for p in r['duplicate_org_ids'].split(';') if p and tuple(sorted((r['org_id'],p))) not in distinct]
 n=dict(r);n['duplicate_org_ids']=';'.join(peers);n['gap_duplicate']=int(bool(peers));n['gap_count']=sum(int(n[k]) for k in ['gap_tier','gap_duplicate','gap_website','gap_capabilities']);n['healthy']=int(n['gap_count']==0);adjusted.append(n)
assert len(rows)==len(adjusted) and all(int(b['healthy'])>=int(a['healthy']) for a,b in zip(rows,adjusted))
write(HERE/'health_distinct_scenario.csv',adjusted)
for label,rs in [('Original T1 unchanged definition',rows),('Scenario only: dated distinct pairs excluded',adjusted)]:
 n=sum(int(r['healthy']) for r in rs);print(f'{label}: {n}/{len(rs)} PIC18 Ring1–2 organizations = {100*n/len(rs):.2f}%')
