#!/usr/bin/env python3
"""Promote only the frozen six jointly corroborated MN/NJ establishments."""
import argparse,csv,hashlib,importlib.util,json,sys
from pathlib import Path
from urllib.parse import urlsplit
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from atlas import name_key,street_key
spec=importlib.util.spec_from_file_location('raw',ROOT/'tasks/strong-waves-mo-sc-la-2026-11-06/prepare.py');raw=importlib.util.module_from_spec(spec);spec.loader.exec_module(raw)
BY='atlas-L3-merged-site-quality-2';DATE='2026-11-06';CLAIMS={'existence','address','code','parent','scope'}
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def host(u):return (urlsplit(u if '://' in u else 'https://'+u).hostname or '').lower().removeprefix('www.')
def require_five(rows):
 assert {r['claim_type'] for r in rows if r['tier_effect']=='supports_B'}==CLAIMS,'missing B must-have claim'
def witness(r,org):
 p=Path(r['page']);capture=Path(r['capture']);text=p.read_text()
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['page_sha256'],'source text hash changed'
 assert hashlib.sha256(capture.read_bytes()).hexdigest()==r['capture_sha256'],'capture hash changed'
 assert r['raw'] and all(raw.contains(text,r[k]) for k in ['quote','city_quote','binding_quote']),'scope/city/binding quote absent'
 receipt=next(x for x in json.loads((H/'rawcheck.json').read_text()) if x['site_id']==r['site_id'])
 assert receipt['source_url']==r['source_url'],'source URL receipt mismatch'
 if r['source_date']:assert r['site_id']=='SITE-012669' and r['source_date']=='2021-07-15' and raw.contains(text,'July 15th, 2021'),'unsupported source date'
 if r['issuer_mode']=='og_site_name':
  assert 'property="og:site_name" content="'+r['issuer_quote']+'"' in capture.read_text(),'metadata issuer absent'
 else:assert r['issuer_mode']=='visible_text' and raw.contains(text,r['issuer_quote']),'visible issuer absent'
 direct=org['website'] and (host(r['source_url'])==host(org['website']) or host(r['source_url']).endswith('.'+host(org['website'])))
 assert direct or name_key(r['issuer_quote']) in {name_key(x) for x in [org['legal_name']]+org['trade_names'].split(';')},'operator issuer not established'
 return text

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 frame=read(H/'input.csv');sel=json.loads((H/'selected.json').read_text());chosen={r['site_id']:r for r in sel};holds=read(H/'holds.csv')
 assert len(frame)==len({r['site_id'] for r in frame})==15 and len(chosen)==len(sel)==6
 assert len(holds)==len({r['site_id'] for r in holds})==9 and not(set(chosen)&{r['site_id'] for r in holds})
 assert set(chosen)|{r['site_id'] for r in holds}=={r['site_id'] for r in frame}
 sites=[(p,r) for p in data.glob('sites_*.csv') for r in read(p)];assert len(sites)==len({r['site_id'] for _,r in sites}),'duplicate SITE ID'
 current={r['site_id']:(p,r) for p,r in sites};orgs={r['org_id']:r for p in data.glob('organizations_*.csv') for r in read(p)}
 evidence=[(p,r) for p in data.glob('evidence_*.csv') for r in read(p)];assert len(evidence)==len({r['evidence_id'] for _,r in evidence}),'duplicate EVD ID';have={r['evidence_id']:(p,r) for p,r in evidence}
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')};edits={};out=[];vs=[]
 for slot,i in enumerate(frame):
  sid=i['site_id'];path,now=current[sid]
  if sid not in chosen:assert now==i,('held site changed',sid);vs.append(next(r for r in holds if r['site_id']==sid));continue
  r=chosen[sid];org=orgs[i['org_id']];witness(r,org)
  assert raw.contains(r['city_quote'],i['city']),'city does not name frozen plant'
  assert i['verification_tier']=='C' and i['operating_status']=='unknown' and org['status']=='active' and not org['successor_org_id']
  fid=i['sources'].split('#establishment_ID=')[-1];f=ita[fid]
  assert street_key(f['street']) and street_key(f['street'])==street_key(i['street_address'])
  assert (f['city'],f['state'],f['zip5'],f['naics_code'])==(i['city'],i['state'],i['zip'],i['naics_primary']) and f['reliability']=='ok'
  assert name_key(f['company_name']) in {name_key(x) for x in [org['legal_name']]+org['trade_names'].split(';')}
  new=dict(i);new.update(verification_tier='B',last_verified=DATE,sources=i['sources']+'; '+r['source_url'],notes=i['notes']+' | '+DATE+' quality: raw own-issued plant-city/polymer-activity witness jointly corroborates five mandatory claims at B; operating_status unknown retained. '+r['note'])
  assert now in [i,new],('conflicting site edit',sid);edits.setdefault(path,{})[sid]=new
  claims={'existence':f"ITA{fid}: {f['establishment_name']}; filed company_name {f['company_name']}",'address':f"{f['street']}, {f['city']}, {f['state']} {f['zip5']}, US; county unchanged/unset",'code':f"naics_primary {f['naics_code']}; government_filing, medium confidence",'parent':f"org_id {i['org_id']} ({org['legal_name']}); filed company_name {f['company_name']}"}
  observations=[]
  for n,(claim,detail) in enumerate(list(claims.items())+[('scope',r['quote'])]):
   own=claim=='scope';e=dict(evidence_id=f'EVD-{304100+slot*6+n:06d}',record_table='sites',record_id=sid,claim_type=claim,claim_detail=detail,source_class='own_site' if own else 'government_filing',source_ref=r['source_url'] if own else i['sources'],observed_date=(r['source_date'] or DATE) if own else '2026-11-01',tier_effect='supports_B',created_by=BY,notes=(r['note'] if own else f"CY2025 banked ITA{fid}, submitted {f['date_submitted']}; joint raw own plant witness {r['source_url']}. Federal facts remain federal claims; no current operating assertion.")+f' Retrieved/reviewed{DATE}.')
   assert 304100<=int(e['evidence_id'][4:])<=304189
   p=data/('evidence_sites_'+i['state']+'.csv')
   if e['evidence_id'] in have:assert have[e['evidence_id']]==(p,e),('conflicting EVD ID',e['evidence_id'])
   out.append((p,e));observations.append(e)
  require_five(observations);vs.append(dict(site_id=sid,verdict='VERIFIED',reason='Five mandatory B claims jointly corroborated by banked federal record and raw own-issued plant-city/polymer-activity witness; unknown status retained.'))
 if a.apply:
  for p,changes in edits.items():write(p,[changes.get(r['site_id'],r) for r in read(p)])
  for p in {p for p,_ in out}:
   pending=[r for q,r in out if q==p and r['evidence_id'] not in have]
   if pending:append_sorted(p,pending,'evidence_id')
 write(H/'verdicts.csv',vs)
 print(json.dumps({'frozen_merged_C_sites':15,'promoted':6,'holds':9,'new_B_evidence':30,'pending_evidence':sum(r['evidence_id'] not in have for _,r in out)}))
if __name__=='__main__':main()
