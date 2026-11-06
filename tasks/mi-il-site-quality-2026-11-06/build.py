"""Upgrade only the frozen merged-site frame; preflight all shards before writing."""
import argparse,csv,hashlib,json,re,sys
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlsplit
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from atlas import name_key,street_key
from fetch import read,on_page,write
DATE='2026-11-06';BY='codex atlas-L11-mi-il-quality'
def host(u):return (urlsplit(u).hostname or '').lower().removeprefix('www.')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 inputs=read(H/'input.csv');sel=read(H/'selected.csv');raw={r['site_id']:r for r in read(H/'rawcheck.csv')};holds=read(H/'holds.csv')
 assert len(inputs)==len({r['site_id'] for r in inputs})==35
 chosen={r['site_id']:r for r in sel};assert len(chosen)==len(sel)==len(raw)
 assert len(holds)==len({r['site_id'] for r in holds}) and not(set(chosen)&{r['site_id'] for r in holds})
 assert set(chosen)|{r['site_id'] for r in holds}=={r['site_id'] for r in inputs}
 orgs={r['org_id']:r for p in data.glob('organizations_*.csv') for r in read(p)}
 sites=[(p.name,r) for p in data.glob('sites_*.csv') for r in read(p)];current={r['site_id']:(n,r) for n,r in sites};assert len(current)==len(sites)
 evs=[(p.name,r) for p in data.glob('evidence_*.csv') for r in read(p)];ev={r['evidence_id']:(n,r) for n,r in evs};assert len(ev)==len(evs),'global evidence collision'
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 out=defaultdict(list);edits=defaultdict(dict);alloc=[];vs=[]
 for slot,i in enumerate(inputs):
  sid=i['site_id'];name,now=current[sid];base={k:i[k] for k in now};r=chosen.get(sid)
  if not r:
   assert now==base,('held site changed',sid)
   vs.append(next(v for v in holds if v['site_id']==sid));continue
  assert raw[sid]==r and r['raw']=='yes' and r['quote'] and r['city_quote'] and r['binding_quote']
  page=ROOT/r['page'];assert hashlib.sha256(page.read_bytes()).hexdigest()==r['page_sha256'],'source hash changed'
  assert all(on_page(r[k],page) for k in ['quote','city_quote','binding_quote']),('raw words absent',sid)
  org=orgs[i['org_id']];domain=host(org['website']);source=host(r['source_url'])
  assert source==r['own_domain']
  direct=domain and (source==domain or source.endswith('.'+domain))
  # The only cross-domain witnesses are already recorded ultimate parents, B-PARENT.
  if not direct:
   assert (sid,org['ultimate_parent_name'],source) in [('SITE-018012','Techniplas','techniplas.com'),('SITE-019007','Avery Dennison Corporation','label.averydennison.com')],('own domain/parent missing',sid)
  fid=re.search(r'establishment_ID=(\d+)',i['sources'])[1];f=ita[fid]
  assert f['state']==i['state'] and f['zip5']==i['zip'] and street_key(f['street'])==street_key(i['street_address']) and f['naics_code']==i['naics_primary']
  assert name_key(f['company_name']) in {name_key(org['legal_name']),*(name_key(t) for t in org['trade_names'].split(';') if t)}
  assert i['operating_status']=='unknown' and i['verification_tier']=='C'
  updated=base.copy();updated.update(verification_tier='B',last_verified=DATE,sources=i['sources']+';'+r['source_url'],notes=i['notes']+' | '+DATE+' own-site quality pass: B for existence/address/scope/code/operator after joint primary-source review; operating_status unknown retained. '+r['note'])
  assert now in [base,updated],('conflicting site edit',sid);edits[name][sid]=updated
  claims={'existence':f"ITA {fid}: {f['establishment_name']}; company {f['company_name']}",'address':f"{f['street']}, {f['city']}, {f['state']} {f['zip5']}, US; county unchanged/unset",'code':f"naics_primary {f['naics_code']}; government_filing; medium confidence",'parent':f"Operator org_id {i['org_id']} ({org['legal_name']}); filed company_name {f['company_name']}"}
  observations=[dict(claim_type=c,claim_detail=d,source_class='government_filing',source_ref=i['sources'],observed_date='2026-11-01',notes=f"CY2025 banked ITA, submitted {f['date_submitted']}, reviewed {DATE}; second independent own plant witness {r['source_url']}. Government facts remain government claims; B reflects joint identity/location/process corroboration, not current operation.") for c,d in claims.items()]
  observations.append(dict(claim_type='scope',claim_detail='"'+r['quote']+'"',source_class='own_site',source_ref=r['source_url'],observed_date=r['source_date'] or DATE,notes=f"Raw fetched {r['fetched_at']}; source date distinct from retrieval. {r['note']}"))
  for n,e in enumerate(observations):
   eid=f'EVD-{277500+slot*6+n:06d}';e.update(evidence_id=eid,record_table='sites',record_id=sid,tier_effect='supports_B',created_by=BY);out['evidence_sites_'+i['state']+'.csv'].append(e)
   alloc.append(dict(evidence_id=eid,site_id=sid,claim_type=e['claim_type']))
  vs.append(dict(site_id=sid,verdict='VERIFIED',reason=r['note']))
 pending={}
 for name,rows in out.items():
  header=list(read(data/name)[0]);pending[name]=[]
  for r in rows:
   if r['evidence_id'] in ev:assert ev[r['evidence_id']]==(name,{k:r.get(k,'') for k in header}),('global ID collision',r['evidence_id'])
   else:pending[name].append(r)
 if a.apply:
  for name,changes in edits.items():
   old=read(data/name);new=[changes.get(r['site_id'],r) for r in old]
   if new!=old:write(data/name,new,list(old[0]))
  for name,rows in pending.items():
   if rows:append_sorted(data/name,rows,'evidence_id')
 write(H/'verdicts.csv',vs,['site_id','verdict','reason']);write(H/'allocations.csv',alloc,['evidence_id','site_id','claim_type'])
 print(json.dumps(dict(frame=35,verdicts=dict(Counter(r['verdict'] for r in vs)),tier_changes=len(chosen),new_evidence=len(alloc),pending_evidence=sum(map(len,pending.values())))))
if __name__=='__main__':main()
