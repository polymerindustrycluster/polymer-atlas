"""Render reproducible review tables; address probes are hand-adjudicated, not auto-accepted."""
import csv,json,re
from build import D,P,read,write,common

def main():
 probes=json.loads((P/'address_probes.json').read_text()); addr=read(P/'address_sample.csv');jobs=read(P/'jobs_sample.csv');bands=read(P/'band_comparison.csv')
 corroborated={'SITE-001651','SITE-000687','SITE-000983','SITE-001694','SITE-000603'}
 rows=[]
 for sid in sorted({r['site_id'] for r in addr}):
  p=next(x for x in probes if x['site_id']==sid)
  rows.append(dict(site_id=sid,verdict='STILL_UNCERTAIN',own_address_corrob=str(sid in corroborated),plant_verified='False',settling_fact='Own-site or federal plant-grain address witness; contact/HQ address alone does not establish a plant',urls=';'.join(c['url'] for c in p['checks'] if c['url'].startswith('http'))))
 def public(name,rs):
  with (D/name).open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
 public('address_review.csv',rows)
 js=[]
 for sid in sorted({r['site_id'] for r in jobs}):
  rr=[r for r in jobs if r['site_id']==sid]
  js.append(dict(site_id=sid,loan_ids=';'.join(r['LoanNumber'] for r in rr),jobs_reported=';'.join(r['JobsReported'] for r in rr),verdict='STILL_UNCERTAIN',settling_fact='Establishment allocation and dated site employee evidence; borrower employment is not site employment'))
 public('jobs_review.csv',js)
 bs=[]
 for sid in sorted({r['site_id'] for r in bands}):
  rr=[r for r in bands if r['site_id']==sid];r=rr[0]
  r=max(rr,key=lambda r:(int(r['DateApproved'].split('/')[2]),int(r['DateApproved'].split('/')[0]),int(r['DateApproved'].split('/')[1])))
  nums=re.findall(r'\d+',r['atlas_band']);n=float(r['JobsReported']);result='uncomparable'
  if len(nums)==2:result='within' if int(nums[0])<=n<=int(nums[1]) else 'outside'
  bs.append(dict(site_id=sid,loan_id=r['LoanNumber'],date_approved=r['DateApproved'],jobs_reported=r['JobsReported'],atlas_band=r['atlas_band'],comparison=result,verdict='STILL_UNCERTAIN'))
 public('band_review.csv',bs)
 m=json.loads((D/'metrics.json').read_text());m['review']={'address_contact_corroborated':5,'address_reviewed':20,'plant_confirmed':0,'jobs_reviewed':20,'site_jobs_confirmed':0,'band_within':sum(r['comparison']=='within' for r in bs),'band_outside':sum(r['comparison']=='outside' for r in bs),'band_uncomparable':sum(r['comparison']=='uncomparable' for r in bs),'address_contact_wilson95':common.wilson(5,20)}
 (D/'metrics.json').write_text(json.dumps(m,indent=2)+'\n')
if __name__=='__main__':main()
