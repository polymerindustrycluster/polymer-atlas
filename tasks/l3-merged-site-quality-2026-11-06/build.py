#!/usr/bin/env python3
"""Joint primary-source quality adjudication of the three frozen merged L3 C sites."""
import argparse,csv,hashlib,importlib.util,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from atlas import name_key,street_key
spec=importlib.util.spec_from_file_location('raw',ROOT/'tasks/strong-waves-mo-sc-la-2026-11-06/prepare.py');raw=importlib.util.module_from_spec(spec);spec.loader.exec_module(raw)
BY='atlas-L3-merged-site-quality';DATE='2026-11-06'
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def witness(r):
 p=Path(r['raw_path']);bridge=Path(r['bridge_raw_path'])
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['raw_sha256'],'job raw hash changed'
 assert hashlib.sha256(bridge.read_bytes()).hexdigest()==r['bridge_sha256'],'issuer bridge changed'
 assert 'https://plastipak.wd1.myworkdayjobs.com/Plastipak' in bridge.read_text(),'issuer tenant link absent'
 d=json.loads(p.read_text());j=d['jobPostingInfo'];t=raw.Text();t.feed(j['jobDescription']);text=' '.join(t.parts)
 assert r['raw'] and j['jobReqId']=='REQ24583' and j['location']==r['city_quote']=='Plastipak - Pineville, LA'
 assert j['startDate']==r['source_date']=='2026-09-23' and d['hiringOrganization']['name']==r['issuer_quote']=='1000 Plastipak Packaging Inc. (US)'
 assert raw.contains(text,r['quote']),'scope quote absent'
 assert r['source_url']=='https://plastipak.wd1.myworkdayjobs.com/wday/cxs/plastipak/Plastipak/job/Process-Technician--Day-Shift_REQ24583'
 return text

def require_five(rows):
 assert {r['claim_type'] for r in rows if r['tier_effect']=='supports_B'}=={'existence','address','code','parent','scope'},'missing B must-have claim'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 frame=read(H/'input.csv');selected=json.loads((H/'selected.json').read_text());holds=read(H/'holds.csv')
 assert len(frame)==3 and {r['site_id'] for r in frame}=={'SITE-012001','SITE-012503','SITE-012511'}
 assert len(selected)==1 and selected[0]['site_id']=='SITE-012511'
 assert {r['site_id'] for r in holds}=={'SITE-012001','SITE-012503'} and all(r['verdict']=='STILL_UNCERTAIN' and r['reason'] for r in holds)
 sites=[(p,r) for p in data.glob('sites_*.csv') for r in read(p)];assert len(sites)==len({r['site_id'] for _,r in sites}),'duplicate site ID'
 by={r['site_id']:(p,r) for p,r in sites};ev=[(p,r) for p in data.glob('evidence_*.csv') for r in read(p)];assert len(ev)==len({r['evidence_id'] for _,r in ev}),'duplicate evidence ID'
 have={r['evidence_id']:(p,r) for p,r in ev};orgs={r['org_id']:r for p in data.glob('organizations_*.csv') for r in read(p)}
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')};updates={};planned=[];verdicts=[]
 for slot,i in enumerate(frame):
  p,now=by[i['site_id']]
  if i['site_id']!='SITE-012511':assert now==i,('held record changed',i['site_id']);verdicts.append(next(r for r in holds if r['site_id']==i['site_id']));continue
  r=selected[0];witness(r);assert i['verification_tier']=='C' and i['operating_status']=='unknown'
  f=ita[r['establishment_id']];org=orgs[i['org_id']];assert i['org_id']=='ORG-001033' and org['status']=='active' and not org['successor_org_id']
  assert name_key(f['company_name']) in {name_key(x) for x in [org['legal_name']]+org['trade_names'].split(';')}
  assert street_key(f['street']) and street_key(f['street'])==street_key(i['street_address']) and (f['city'],f['state'],f['zip5'],f['naics_code'])==(i['city'],i['state'],i['zip'],i['naics_primary'])
  assert f['reliability']=='ok' and f['naics_code']=='326160' and f['establishment_id']=='192504'
  new=dict(i);new.update(verification_tier='B',last_verified=DATE,sources=i['sources']+'; '+r['source_url'],notes=i['notes']+' | '+DATE+' quality: joint federal and company-issued Pineville plastic-container manufacturing witness; five must-have claims B. Operating_status unknown retained; job dated2026-09-23. Workday tenant linked by own careers page.')
  assert now in [i,new],('conflicting site edit',i['site_id']);updates[p]={i['site_id']:new}
  claims={'existence':f"ITA192504: {f['establishment_name']}; filed company_name {f['company_name']}",'address':f"{f['street']}, {f['city']}, {f['state']} {f['zip5']}, US; county unchanged/unset",'code':f"naics_primary {f['naics_code']}; government_filing, medium confidence",'parent':f"org_id {i['org_id']} ({org['legal_name']}); filed company_name {f['company_name']}"}
  for n,(claim,detail) in enumerate(list(claims.items())+[('scope',r['quote'])]):
   own=claim=='scope';e=dict(evidence_id=f'EVD-{304000+slot*6+n:06d}',record_table='sites',record_id=i['site_id'],claim_type=claim,claim_detail=detail,source_class='own_site' if own else 'government_filing',source_ref=r['source_url'] if own else i['sources'],observed_date=r['source_date'] if own else '2026-11-01',tier_effect='supports_B',created_by=BY,notes=(r['note'] if own else f"CY2025 banked ITA192504 submitted {f['date_submitted']}, joint company-issued Pineville scope corroboration; government facts stay government claims.")+f' Retrieved/reviewed{DATE}; current operating status unknown.')
   path=data/'evidence_sites_LA.csv'
   if e['evidence_id'] in have:assert have[e['evidence_id']]==(path,e),('conflicting evidence ID',e['evidence_id'])
   planned.append((path,e))
  verdicts.append(dict(site_id=i['site_id'],verdict='VERIFIED',reason='Five must-have claims atB after federal and company-issued Pineville plastic-container manufacturing corroboration; statusunknown retained.'))
 require_five([r for _,r in planned])
 if a.apply:
  for p,changes in updates.items():write(p,[changes.get(r['site_id'],r) for r in read(p)])
  for p in {p for p,_ in planned}:
   pending=[r for q,r in planned if p==q and r['evidence_id'] not in have]
   if pending:append_sorted(p,pending,'evidence_id')
 write(H/'verdicts.csv',verdicts)
 print(json.dumps({'merged_C_frame':3,'promoted':1,'holds':2,'new_evidence':5,'pending_evidence':sum(r['evidence_id'] not in have for _,r in planned)}))
if __name__=='__main__':main()
