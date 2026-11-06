#!/usr/bin/env python3
"""Document parent-group links/usage for merged PR141 witnesses; canonical evidence append-only."""
import argparse,csv,json,sys
from collections import defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
BY='atlas-L3-parent-provenance-fix';DATE='2026-11-06'
WEBFLAG=' Group domain used as website (B-PARENT/B-PARENT-WEB); parent relationship documented.'
SOURCEFLAG=' Group domain used as own_site source (B-PARENT); parent relationship documented.'
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');a=ap.parse_args()
 audit=read(H/'audit.csv');parents=read(H/'parent-witnesses.csv');flags=read(H/'flag-witnesses.csv')
 assert len(audit)==19 and len({r['site_id'] for r in audit})==19
 targets={r['org_id']:r['ultimate_parent_name'] for r in parents};assert set(targets)=={'ORG-009017','ORG-009022','ORG-009026'}
 assert {r['org_id'] for r in flags}=={'ORG-003555','ORG-001336'}
 assert all(r['raw']=='yes' for r in parents+flags)
 assert all(r['ultimate_parent_name']==targets[r['org_id']] for r in parents), 'inconsistent planned parent'
 paths={};tables={}
 for p in (ROOT/'data').glob('organizations_*.csv'):
  tables[p]=read(p)
  for r in tables[p]:paths[r['org_id']]=(p,r)
 touched=set()
 for oid in set(targets)|{r['org_id'] for r in flags}:
  p,r=paths[oid];touched.add(p)
  if oid in targets:
   assert r['ultimate_parent_name'] in ('',targets[oid]),('unexpected parent',oid)
   r['ultimate_parent_name']=targets[oid]
  else:assert r['parent_org_id'] or r['ultimate_parent_name'],('missing previously recorded parent',oid)
  flag=WEBFLAG if r['website'] else SOURCEFLAG
  if flag not in r['notes']:r['notes']+=flag
 planned=defaultdict(list)
 for i,w in enumerate(parents+flags):
  p,_=paths[w['org_id']];evpath=ROOT/'data'/('evidence_'+p.name)
  planned[evpath].append(dict(evidence_id=f'EVD-{307000+i:06d}',record_table='organizations',record_id=w['org_id'],claim_type='parent' if i<len(parents) else 'existence',claim_detail=w['link_detail']+' Raw quote: '+w['quote'],source_class='own_site',source_ref=w['source_url'],observed_date=w['observed_date'],tier_effect='supports_C',created_by=BY,notes=w['notes']+' Retrieved/checked '+DATE+'. No prior evidence row edited.'))
 # Preflight every planned ID globally before writing either table.
 old=[(p,r) for p in (ROOT/'data').glob('evidence_*.csv') for r in read(p)]
 assert len(old)==len({r['evidence_id'] for _,r in old}), 'duplicate existing evidence ID'
 have={r['evidence_id']:(p,r) for p,r in old};pending={}
 for p,rows in planned.items():
  for e in rows:
   assert 300000<=int(e['evidence_id'][4:])<=309999
   if e['evidence_id'] in have:
    q,r=have[e['evidence_id']];assert q==p and r==e,('conflicting evidence ID',e['evidence_id'])
  pending[p]=[r for r in rows if r['evidence_id'] not in have]
 if a.apply:
  for p in touched:
   rows=tables[p]
   with p.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
  for p,rows in pending.items():
   if rows:append_sorted(p,rows,'evidence_id')
 print(json.dumps({'site_issuer_audit':len(audit),'new_parent_fields':len(targets),'group_flags':len(targets)+len(flags),'parent_evidence':len(parents),'issuer_evidence':len(flags),'new_evidence':sum(map(len,pending.values()))}))
if __name__=='__main__':main()
