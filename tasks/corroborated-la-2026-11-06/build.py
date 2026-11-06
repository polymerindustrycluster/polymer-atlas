#!/usr/bin/env python3
"""L3 federal-only C continuation, adapted from L11's CORROBORATED builder.
Preflight all outputs before writes; replay compares complete canonical rows.
"""
import argparse,csv,json,re,sys
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from atlas import street_key,name_key,squash,dedupe,Table
DATE='2026-11-06';BY='atlas-L3-corroborated-la'
SOURCE='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv'
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def write(p,rows,fields):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--state',required=True,choices=['LA']);ap.add_argument('--apply',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 cs=read(H/'input.csv');vs=read(H/'verdicts.csv');byc={r['cluster_id']:r for r in cs}
 assert len(cs)==len(vs)==42 and Counter(r['cluster_id'] for r in cs)==Counter(r['cluster_id'] for r in vs)
 assert [r['cluster_id'] for r in cs]==[r['cluster_id'] for r in vs], 'frozen ID order changed'
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 orgs={r['org_id']:(p,r) for p in data.glob('organizations_*.csv') for r in read(p)}
 oldsites=[r for p in data.glob('sites_*.csv') for r in read(p)]
 oldev=[r for p in data.glob('evidence_*.csv') for r in read(p)]
 tables={name:Table(name) for name in ['organizations','sites','ecosystem']}
 for oid,(p,r) in orgs.items():tables['organizations'].rows.append({**r,'__file__':p.name,'__line__':0})
 tables['sites'].rows=[{**r,'__file__':'sites_'+r['state']+'.csv','__line__':0} for r in oldsites]
 tables['ecosystem'].rows=[{**r,'__file__':'ecosystem.csv','__line__':0} for r in read(data/'ecosystem.csv')]
 out=defaultdict(list);updates=defaultdict(dict);alloc=[];create_dedupe={}
 for idx,v in enumerate(vs):
  if v['state']!=a.state or v['verdict']!='VERIFIED':continue
  c=byc[v['cluster_id']];oid=v['held_org_id'];op,org=orgs[oid]
  assert org['status']=='active' and not org['successor_org_id']
  fed=[ita[i[4:]] for i in c['sources_with_ids'].split(';') if i.startswith('ITA:')];assert fed
  f=fed[0];assert f['establishment_id']==v['establishment_id']
  create_dedupe[v['cluster_id']]=dedupe(tables,domain=org['website'] or None,name=f['company_name'],street=f['street'],city=f['city'],state=a.state,zip_=f['zip5'])
  matches={key for key,(_,r) in orgs.items() if r['status']=='active' and not r['successor_org_id'] and name_key(f['company_name']) in {name_key(n) for n in [r['legal_name']]+r['trade_names'].split(';')}}
  assert matches=={oid}, 'ambiguous filed operator'
  aliases=[org['legal_name']]+org['trade_names'].split(';');assert name_key(f['company_name']) in {name_key(x) for x in aliases}
  assert all(r['reliability']=='ok' and r['state']==a.state and r['naics_code']==f['naics_code'] and street_key(r['street'])==street_key(f['street']) for r in fed)
  assert street_key(f['street']) and f['city'] and f['zip5'] and f['schema_2_2_signal']=='P'
  assert f['naics_code'].startswith('326') or f['naics_code'] in {'325211','325212','325510','325520','325910'}, 'not a producer code'
  assert re.search(r'plastic|polymer|rubber|resin|paint|coating|\binks?\b',f['industry_description'],re.I) and not re.search(r'remover|stripper|cleaner',f['industry_description'],re.I), 'activity does not settle polymer manufacturing'
  assert v['cluster_id'] not in {r['cluster_id'] for r in read(H/'holds-reviewed.csv')}, 'manual identity/function hold'
  sid=f'SITE-{12500+idx:06d}';eid=306000+idx*20;assert 12500+idx<=12999
  for s in oldsites:
   if s['site_id']==sid:continue
   assert not (s['state']==a.state and street_key(s['street_address'])==street_key(f['street'])),('street conflict',c['cluster_id'],s['site_id'])
   assert not (s['org_id']==oid and s['state']==a.state and squash(s['city'])==squash(f['city']) and not s['street_address']),('blank street conflict',c['cluster_id'],s['site_id'])
  ring='1' if f['naics_code'].startswith('326') or f['naics_code'] in {'325211','325212'} else '2'
  ref=SOURCE+'#establishment_ID='+f['establishment_id']
  notes=f"{c['cluster_id']}; CY2025 ITA establishment_ID {f['establishment_id']}; date_submitted {f['date_submitted']}; inherited packet observed 2026-11-01, reviewed {DATE}. Provisional federal-only C; current operation not checked. Filed establishment_name: {f['establishment_name']}."
  out[f'sites_{a.state}.csv'].append(dict(site_id=sid,org_id=oid,site_name=org['legal_name']+' - '+f['city'],site_type='manufacturing_plant',street_address=f['street'],city=f['city'],state=a.state,zip=f['zip5'],country='US',ring_primary=ring,naics_primary=f['naics_code'],naics_primary_source_type='government_filing',naics_confidence='medium',operating_status='unknown',sources=ref,verification_tier='C',last_verified=DATE,created_by=BY,notes=notes))
  claims={'existence':f"ITA establishment {f['establishment_id']}: {f['establishment_name']}",'address':f"{f['street']}, {f['city']}, {a.state} {f['zip5']}, US; county unset",'scope':f"Provisional ring_primary {ring}; filed activity: {f['industry_description']}; federal-only C",'code':f"naics_primary {f['naics_code']}; government_filing, medium confidence",'parent':f"org_id {oid} ({org['legal_name']}); filed company_name {f['company_name']}",'activity':f"CY2025 establishment filing: {f['industry_description']}; current operating status unknown",'liveness':f"CY2025 filing submitted {f['date_submitted']}; not a live 2026 operating observation"}
  for claim,detail in claims.items():
   out[f'evidence_sites_{a.state}.csv'].append(dict(evidence_id=f'EVD-{eid:06d}',record_table='sites',record_id=sid,claim_type=claim,claim_detail=detail,source_class='government_filing',source_ref=ref,observed_date='2026-11-01',tier_effect='supports_C',created_by=BY,notes=notes));eid+=1
  # Primary government filings attest registrant identity (A); plant scope/liveness remain provisional C.
  # City/unit labels are not registrant entity names; retain them in site notes, not parent aliases.
  registrant=f['company_name'].strip()
  if registrant!=org['legal_name']:
   previous=updates[op].get(oid,org['trade_names']);parts=[x.strip() for x in previous.split(';') if x.strip()]
   if registrant not in parts:parts.append(registrant)
   updates[op][oid]='; '.join(parts)
   out[f"evidence_organizations_{op.stem.split('_')[-1]}.csv"].append(dict(evidence_id=f'EVD-{eid:06d}',record_table='organizations',record_id=oid,claim_type='existence',claim_detail='Federal registrant trade_names: '+registrant,source_class='government_filing',source_ref=ref,observed_date='2026-11-01',tier_effect='supports_A',created_by=BY,notes=notes))
  alloc.append(dict(cluster_id=c['cluster_id'],site_id=sid,org_id=oid,establishment_id=f['establishment_id'],state=a.state))
 # Global cross-shard ID collision preflight, including records in unexpected shards.
 assert len(oldsites)==len({r['site_id'] for r in oldsites}), 'conflicting ID: duplicate SITE across shards'
 assert len(oldev)==len({r['evidence_id'] for r in oldev}), 'conflicting ID: duplicate EVD across shards'
 allids={'site_id':{r['site_id']:r for r in oldsites},'evidence_id':{r['evidence_id']:r for r in oldev}}
 pending={}
 for name,rows in out.items():
  p=data/name;old=read(p);key='site_id' if name.startswith('sites_') else 'evidence_id';header=list(old[0]);local={r[key] for r in old}
  for r in rows:
   assert key!='evidence_id' or 300000<=int(r[key][4:])<=309999
   if r[key] in allids[key]:assert r[key] in local and allids[key][r[key]]=={k:r.get(k,'') for k in header},('conflicting ID',r[key])
  pending[name]=[r for r in rows if r[key] not in allids[key]]
 if a.apply:
  for name,rows in pending.items():
   if rows:append_sorted(data/name,rows,'site_id' if name.startswith('sites_') else 'evidence_id')
  for p,changes in updates.items():
   rows=read(p)
   for r in rows:
    if r['org_id'] in changes:r['trade_names']=changes[r['org_id']]
   write(p,rows,list(rows[0]))
 (H/f'create-dedupe_{a.state}.json').write_text(json.dumps(create_dedupe,indent=2)+'\n')
 write(H/f'allocations_{a.state}.csv',alloc,['cluster_id','site_id','org_id','establishment_id','state'])
 print(json.dumps({'state':a.state,'verdicts':dict(Counter(v['verdict'] for v in vs if v['state']==a.state)),'sites_C':len(alloc),'organizations_created':0,'evidence_rows':sum(len(rs) for name,rs in out.items() if name.startswith('evidence_')),'pending_rows':{k:len(v) for k,v in pending.items()}}))
if __name__=='__main__':main()
