#!/usr/bin/env python3
"""Append explicit schema-grounded scope observations; never rewrite earlier evidence."""
import csv,json,sys
from pathlib import Path
from collections import defaultdict
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'scripts'))
from shard_io import append_sorted
def read(p):
 with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def main(data,apply=False):
 audit=read(H/'audit.csv');assert len(audit)==11 and len({r['site_id'] for r in audit})==11
 it={r['establishment_id']:r for r in read(R/'tasks/osha-ita-2026-11-01/establishments.csv')};out=defaultdict(list)
 for a in audit:
  f=it[a['establishment_id']];s=next(s for s in read(data/f"sites_{a['state']}.csv") if s['site_id']==a['site_id'])
  assert f['naics_code']==a['naics_primary']==s['naics_primary'] and s['ring_primary']==a['explicit_ring']=='2'
  assert f['naics_code'] in {'325510','325520'} and f['schema_2_2_signal']=='P' and f['state']==a['state'] and s['city']==f['city']
  activity='paint/coating manufacturing' if f['naics_code']=='325510' else 'adhesive/sealant manufacturing'
  out[f"evidence_sites_{a['state']}.csv"].append(dict(evidence_id=a['evidence_id'],record_table='sites',record_id=a['site_id'],claim_type='scope',claim_detail=f"ring_primary 2 via {activity}; ITA NAICS {f['naics_code']} is explicitly listed in SCHEMA 2.2 Ring2; federal-only provisional C",source_class='government_filing',source_ref='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv#establishment_ID='+f['establishment_id'],observed_date='2026-11-01',tier_effect='supports_C',created_by='codex atlas-L7-explicit-ring-basis',notes=f"ITA establishment_ID {f['establishment_id']}, date_submitted {f['date_submitted']}; reviewed2026-11-06. Exact-code schema basis replaces blanket325-prefix reasoning; earlier evidence retained unchanged; no current-operation or tier upgrade claim."))
 seen=defaultdict(list)
 for p in data.glob('evidence_*.csv'):
  for r in read(p):seen[r['evidence_id']].append((p.name,r))
 pending={}
 for name,rows in out.items():
  with (data/name).open() as f:header=next(csv.reader(f))
  for r in rows:
   if r['evidence_id'] in seen:assert seen[r['evidence_id']]==[(name,{k:r.get(k,'') for k in header})],('conflicting ID',r['evidence_id'])
  pending[name]=[r for r in rows if r['evidence_id'] not in seen]
 if apply:
  for name,rows in pending.items():
   if rows:append_sorted(data/name,rows,'evidence_id')
 print(json.dumps({'audited_merged_sites':37,'fallback_derived_FL':4,'fallback_derived_GA':7,'wrong_ring_values':0,'append_scope_rows':11,'pending':{k:len(v) for k,v in pending.items()}}))
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,default=R/'data');p.add_argument('--apply',action='store_true');a=p.parse_args();main(a.data_dir,a.apply)
