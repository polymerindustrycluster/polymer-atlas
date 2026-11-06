"""C→B on the capped merged frame only; preflight every witness/preimage/global ID before writing."""
import argparse,csv,hashlib,json,sys
from collections import defaultdict,Counter
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from atlas import name_key,street_key
from site_corpus import on_page
from prep import read,write,host
DATE='2026-11-06';BY='codex atlas-L11-strong-quality'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 inputs=read(H/'input.csv');eligible=read(H/'eligible_frame.csv');selected=read(H/'selected.csv');verdicts=read(H/'verdicts.csv');slots=read(H/'id_slots.csv')
 assert len(inputs)==len(verdicts)==40 and inputs==eligible[:40] and len({r['site_id'] for r in inputs})==40
 bysel={r['site_id']:r for r in selected};vs={r['site_id']:r for r in verdicts};slot={r['site_id']:int(r['slot']) for r in slots}
 assert len(vs)==40 and set(vs)=={r['site_id'] for r in inputs} and len(bysel)==len(selected)
 assert set(bysel)=={k for k,v in vs.items() if v['verdict']=='VERIFIED'} and set(bysel)<=set(slot)
 assert all(v['verdict'] in ['VERIFIED','STILL_UNCERTAIN'] for v in verdicts)
 fs={r['site_id']:r for r in read(H/'federal_review.csv')}
 county={r['site_id']:r for r in json.loads((H/'county_receipts.json').read_text())}
 site_list=[(p.name,r) for p in data.glob('sites_*.csv') for r in read(p)];sites={r['site_id']:(n,r) for n,r in site_list};assert len(sites)==len(site_list)
 orgs={r['org_id']:r for p in data.glob('organizations_*.csv') for r in read(p)}
 ev_list=[(p.name,r) for p in data.glob('evidence_*.csv') for r in read(p)];ev={r['evidence_id']:(n,r) for n,r in ev_list};assert len(ev)==len(ev_list),'global evidence collision'
 retired={r['evidence_id'] for r in read(H/'retired_ids.csv')}
 out=defaultdict(list);edits=defaultdict(dict);alloc=[]
 for i in inputs:
  sid=i['site_id'];name,now=sites[sid];old={k:i[k] for k in now};r=bysel.get(sid)
  if not r:assert now==old,('held preimage changed',sid);continue
  assert i['verification_tier']=='C' and i['operating_status']=='active'
  p=ROOT/r['page'];assert p.exists(),'Missing public witness: run python3 tasks/strong-wave-site-quality-2026-11-06/acquire.py'
  text=p.read_text();assert hashlib.sha256(p.read_bytes()).hexdigest()==r['page_sha256'],'raw hash mismatch'
  for k in ['quote','activity_quote','city_quote','binding_quote','context_quote']:
   if r[k]:assert on_page(r[k],text),('quote/binding absent',sid,k)
  assert r['city_quote'].lower()==i['city'].lower()
  org=orgs[i['org_id']];assert all(org[k]==i['org_'+k] for k in ['legal_name','website','trade_names'])
  assert org['parent_org_id']==i['parent_org_id'] and org['ultimate_parent_name']==i['ultimate_parent_name']
  assert host(r['source_url'])==host(org['website']),('unrecorded own domain/parent',sid)
  assert fs[sid]['admissible']=='yes';f=json.loads(fs[sid]['chosen'])
  aliases={name_key(org['legal_name']),*(name_key(t) for t in org['trade_names'].split(';') if t)}
  assert name_key(f['name']) in aliases and street_key(f['physical_street'])==street_key(i['street_address'])
  assert f['state']==i['state'] and f['zip']==i['zip'] and f['code']==i['naics_primary']
  if f['street']!=f['physical_street']:assert sid=='SITE-011009' and on_page('Physical Address: 6 Spruce Street Northwest Remer, Minnesota 56672',text)
  # Refuse a changed packet even if someone edits federal_review.csv alongside it.
  if f['kind']=='ITA':
   original=next(x for x in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv') if x['establishment_id']==f['key'])
   assert f['url']=='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv#establishment_ID='+f['key']
   assert [original[k] for k in ['company_name','street','city','state','zip5','naics_code']]==[f[k] for k in ['name','street','city','state','zip','code']]
  else:
   original=next(x for x in read(ROOT/'tasks/osha-spine-2026-11-01/establishments.csv') if x['est_key']==f['key'])
   assert f['url']=='https://www.osha.gov/ords/imis/establishment.inspection_detail?id='+original['latest_activity_nr']
   assert [original[k] for k in ['name','street','city','state','zip','naics_latest']]==[f[k] for k in ['name','street','city','state','zip','code']]
  new=old.copy();new.update(verification_tier='B',last_verified=DATE,sources=old['sources']+';'+r['source_url'],notes=old['notes']+' | '+DATE+' C→B quality: all seven site claims jointly corroborated by filed operator/address/code and raw own-site plant/activity witness. Active status retained; no status transition. '+r['note'])
  assert now in [old,new],('stale selected preimage',sid);edits[name][sid]=new
  c=county[sid];assert c['source_url'].startswith('https://geocoding.geo.census.gov/geocoder/geographies/address?')
  cq=parse_qs(urlsplit(c['source_url']).query);assert all(cq[k]==[i[v]] for k,v in [('street','street_address'),('city','city'),('state','state'),('zip','zip')])
  assert c['matched_address'].endswith(', '+i['state']+', '+i['zip'])
  assert c['status']=='PASS' and c['county'].removesuffix(' County').lower()==i['county'].lower()
  cp=ROOT/c['raw_file'];assert cp.exists(),'Missing county witness: run county_check.py'
  assert hashlib.sha256(cp.read_bytes()).hexdigest()==c['raw_sha256'],'county source hash mismatch'
  cb=json.loads(cp.read_text())['result']['addressMatches'];assert any(x['matchedAddress']==c['matched_address'] and any(g['NAME']==c['county'] and g['GEOID']==c['geoid'] for g in x.get('geographies',{}).get('Counties',[])) for x in cb)
  assert street_key(c['matched_address'].split(',',1)[0])==street_key(i['street_address'])
  claims={'existence':f"{f['kind']} {f['key']}: {f['name']} establishment at {f['street']}, {f['city']}, {f['state']} {f['zip']}",'address':f"Filed address {f['street']}, {f['city']}, {f['state']} {f['zip']}; physical street {i['street_address']}; county {i['county'] or 'unset'} retained",'code':f"naics_primary {f['code']}; government_filing; confidence {i['naics_confidence']}",'parent':f"Filed operator {f['name']}; held org_id {i['org_id']} ({org['legal_name']})"}
  obs=[dict(claim_type=k,claim_detail=v,source_class='government_filing',source_ref=f['url'],observed_date='2026-11-01',notes=f"Banked {f['kind']} source row, own as-of/submission/inspection date {f['date']}; reviewed {DATE}. Joint own-site plant witness corroborates filed identity/location/code/operator at B, without promoting the organization. County retained from original physical-address determination; no county edit.") for k,v in claims.items()]
  address=next(x for x in obs if x['claim_type']=='address');address.update(claim_detail=f"Census matched physical address {c['matched_address']}; county {c['county']}; county GEOID {c['geoid']}",source_ref=c['source_url'],observed_date=DATE,notes='Official Census address-exact county geography, jointly bound to the operator by filing and raw own-site witness. Coordinates are not used as evidence or tier inputs; no county/coordinate cell changes.')
  scope='"'+r['quote']+'"'+(' | "'+r['context_quote']+'"' if r['context_quote'] else '')
  for claim,detail in [('scope',scope),('activity','"'+r['activity_quote']+'"'),('liveness','"'+r['activity_quote']+'"')]:
   obs.append(dict(claim_type=claim,claim_detail=detail,source_class='own_site',source_ref=r['source_url'],observed_date=DATE,notes=f"Raw observed {r['fetched_at']}; undated live present-tense manufacturing witness, not a dated production event or status transition. "+r['note']))
  for n,e in enumerate(obs):
   eid=f'EVD-{279000+slot[sid]*7+n:06d}';assert int(eid[4:])<=279999 and eid not in retired,'retired ID reuse'
   e.update(evidence_id=eid,record_table='sites',record_id=sid,tier_effect='supports_B',created_by=BY);shard='evidence_sites_'+i['state']+'.csv';out[shard].append(e);alloc.append(dict(evidence_id=eid,site_id=sid,claim_type=e['claim_type'],shard=shard))
 pending={}
 for name,rows in out.items():
  header=list(read(data/name)[0]);pending[name]=[]
  for r in rows:
   if r['evidence_id'] in ev:assert ev[r['evidence_id']]==(name,{k:r.get(k,'') for k in header}),('global ID collision',r['evidence_id'])
   else:pending[name].append(r)
 if a.apply:
  for name,byid in edits.items():
   old=read(data/name);new=[byid.get(r['site_id'],r) for r in old]
   if old!=new:write(data/name,new,list(old[0]))
  for name,rows in pending.items():
   if rows:append_sorted(data/name,rows,'evidence_id')
 write(H/'allocations.csv',alloc,['evidence_id','site_id','claim_type','shard'])
 print(json.dumps(dict(frame=40,promotions=len(selected),holds=40-len(selected),evidence=len(alloc),pending=sum(map(len,pending.values())))))
if __name__=='__main__':main()
