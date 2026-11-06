#!/usr/bin/env python3
"""Apply the curated Georgia federal-only C packet; reruns compare then skip exact rows."""
import argparse,csv,json,sys,re
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent; ROOT=H.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from atlas import street_key
DATE='2026-11-06'; BY='codex atlas-L7-corr-fl-ga'
SOURCE='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv'
def read(p):
 with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def clean_street(f):
 return re.sub(r',\s*'+re.escape(f['city'])+r',\s*GA\s+\d{5}(?:-\d{4})?$', '', f['street'], flags=re.I)
def ring_for_naics(code):
 if code.startswith('326'):return '1'
 if code in {'325212','325510','325520','325991'}:return '2'
 raise ValueError('HOLD: explicit site-scope/ring witness required; no blanket 325 fallback (SCHEMA1)')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 cs={r['cluster_id']:r for r in read(H/'input.csv')};vs=read(H/'verdicts.csv')
 assert len(vs)==len(cs)==147 and len({v['cluster_id'] for v in vs})==147
 assert set(cs)=={v['cluster_id'] for v in vs}
 assert set(v['verdict'] for v in vs)<={'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'}
 reviewed={r['establishment_id']:r for r in read(H/'reviewed_establishments.csv')}
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 orgs={r['org_id']:r for p in data.glob('organizations_*.csv') for r in read(p)}
 oldsites=[r for p in data.glob('sites_*.csv') for r in read(p)]
 out=defaultdict(list);eid=201000;alloc=[]
 reservations={r['cluster_id']:r for r in read(H/'id_reservations.csv')}
 for idx,v in enumerate(v for v in vs if v['verdict']=='VERIFIED'):
  c=cs[v['cluster_id']];oid=v['held_org_id'];org=orgs[oid];assert org['status']=='active' and not org['successor_org_id']
  fed=[ita[s[4:]] for s in c['sources_with_ids'].split(';') if s.startswith('ITA:')]
  assert fed and all(r['state']=='GA' for r in fed)
  f=fed[0];assert (f['company_name'],f['establishment_name'])==(reviewed[f['establishment_id']]['company_name'],reviewed[f['establishment_id']]['establishment_name'])
  assert f['schema_2_2_signal']=='P' and f['naics_code'][:3] in ('326','325')
  assert all(r['naics_code']==f['naics_code'] and street_key(r['street'])==street_key(clean_street(f)) for r in fed)
  assert f['street'] and f['city'] and f['zip5']
  sid=reservations[c['cluster_id']]['site_id'];serial=int(sid[5:])-16100;eid=201000+7*serial;assert 16100<=int(sid[5:])<=17999
  assert f['reliability']=='ok' and f['size_code_vs_avg_employees']=='consistent'
  street=clean_street(f)
  # A blank held street at the same parent/locality is an unresolved duplicate, not a free address.
  for s in oldsites:
   if s['site_id']==sid:continue
   assert not (s['state']=='GA' and street_key(s['street_address'])==street_key(clean_street(f))),(c['cluster_id'],s['site_id'])
   assert not (s['org_id']==oid and s['state']=='GA' and s['city'].casefold()==f['city'].casefold() and not s['street_address']),(c['cluster_id'],s['site_id'])
  ring=ring_for_naics(f['naics_code'])
  ref=SOURCE+'#establishment_ID='+f['establishment_id']
  notes=f"CY2025 ITA establishment_ID {f['establishment_id']}; date_submitted {f['date_submitted']}; packet observed 2026-11-01, reviewed {DATE}. {v['reason']}"
  out['sites_GA.csv'].append(dict(site_id=sid,org_id=oid,site_name=org['legal_name']+' - '+f['city'],site_type='manufacturing_plant',street_address=street,city=f['city'],state='GA',zip=f['zip5'],country='US',ring_primary=ring,naics_primary=f['naics_code'],naics_primary_source_type='government_filing',naics_confidence='medium',operating_status='active',sources=ref,verification_tier='C',last_verified=DATE,created_by=BY,notes=f"{c['cluster_id']}; Federal-only provisional C, operating evidence is CY2025 filing, not a 2026 observation. {notes}"))
  claims={
   'existence':f"ITA establishment {f['establishment_id']}: {f['establishment_name']}",
   'address':f"{street}, {f['city']}, GA {f['zip5']}, US; county left unset",
   'scope':f"Provisional ring_primary {ring}, manufacturing_plant; employer-reported NAICS {f['naics_code']} (SCHEMA 2.2 Primary); federal-only C per CAMPAIGN convention",
   'code':f"naics_primary {f['naics_code']}; government_filing, medium confidence",
   'parent':f"org_id {oid} ({org['legal_name']}); filed company_name {f['company_name']}; establishment_name {f['establishment_name']}",
   'activity':f"Manufacturing filing for CY{f['year_filing_for']}; active provisional at that vintage",
   'liveness':f"CY{f['year_filing_for']} filing submitted {f['date_submitted']}; does not assert live operating check in 2026"}
  for claim,detail in claims.items():
   assert eid<=219999
   out['evidence_sites_GA.csv'].append(dict(evidence_id=f'EVD-{eid:06d}',record_table='sites',record_id=sid,claim_type=claim,claim_detail=detail,source_class='government_filing',source_ref=ref,observed_date='2026-11-01',tier_effect='supports_C',created_by=BY,notes=notes));eid+=1
  alloc.append(dict(cluster_id=c['cluster_id'],site_id=sid,org_id=oid,establishment_id=f['establishment_id']))
 # Check namespaces across all shards before any mutation, including the alias update.
 pending={}
 for name,rows in out.items():
  key='site_id' if name.startswith('sites_') else 'evidence_id'
  seen=defaultdict(list)
  for p in data.glob('sites_*.csv' if key=='site_id' else 'evidence_*.csv'):
   for r in read(p):seen[r[key]].append((p.name,r))
  with (data/name).open() as f:header=next(csv.reader(f))
  assert len({r[key] for r in rows})==len(rows)
  for r in rows:
   if r[key] in seen:
    assert seen[r[key]]==[(name,{k:r.get(k,'') for k in header})],('conflicting ID',r[key])
  pending[name]=[r for r in rows if r[key] not in seen]
 if a.apply:
  for name,rows in pending.items():
   if rows:append_sorted(data/name,rows,'site_id' if name.startswith('sites_') else 'evidence_id')
 with open(H/'allocations.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=list(alloc[0]),lineterminator='\n');w.writeheader();w.writerows(alloc)
 print(json.dumps({'worked_GA_clusters':len(vs),'verdicts':dict(Counter(v['verdict'] for v in vs)),'sites_C':len(alloc),'organizations_created':0,'evidence_rows':sum(len(r) for k,r in out.items() if k.startswith('evidence_')),'pending_rows':{k:len(v) for k,v in pending.items()}}))
if __name__=='__main__':main()
