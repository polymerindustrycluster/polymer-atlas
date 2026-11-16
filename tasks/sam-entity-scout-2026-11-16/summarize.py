"""Recompute manual-review summaries; SAM attributes stay in private index."""
import csv,json,math,sqlite3
from collections import Counter
from build import HERE,CACHE,ROOT

def wilson(k,n):
 z=1.959963984540054;p=k/n;d=1+z*z/n
 c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return [max(0,c-h),min(1,c+h)]

def summarize():
 m=json.loads((HERE/'metrics.json').read_text());rs=list(csv.DictReader((HERE/'sample.csv').open()));out={}
 for cls in m['match_pairs_by_class']:
  sample=[r for r in rs if r['match_class']==cls];c=Counter(r['verdict'] for r in sample);n=len(sample);k=c['VERIFIED']
  out[cls]=dict(n=n,confirmed=k,rejected=c['REJECT'],uncertain=c['STILL_UNCERTAIN'],confirmed_fraction=k/n,wilson95=wilson(k,n))
 db=sqlite3.connect(CACHE/'sam.sqlite')
 m['manual_pair_consistency_by_class']=out
 existing={(r['site_id'] or r['org_id'],r['registry_id']) for r in csv.DictReader((ROOT/'data/registry_links.csv').open()) if r['registry']=='UEI'}
 proposed=[r for r in rs if r['verdict']=='VERIFIED' and (r['record_id'],r['uei']) not in existing]
 m['reviewed_new_uei_pair_candidates']=len(proposed)
 m['mintable_uei_links']=None
 m['independent_identity_precision_by_class']=None
 m['distinct_indexed_ueis']=db.execute('select count(distinct uei) from sam').fetchone()[0]
 # City/ZIP is discovery screening only; never a county assertion.
 cities={}
 for r in csv.DictReader((ROOT/'data/sites_OH.csv').open()):
  if r['county'] in __import__('regions').PIC18:cities[r['city'].casefold()]=1
 leads=[]
 for uei,city,naics,listed in db.execute("select distinct uei,city,naics,listed_naics from sam where state='OH' and not exists(select 1 from matches where matches.uei=sam.uei)"):
  if city.casefold() in cities and any(c.startswith(('3252','3255','326')) for c in [naics]+listed.split('~')):leads.append(uei)
 m['unheld_polymer_uei_pic18_city_screen_leads']=len(set(leads))
 m['county_verified_unheld_pic18_polymer_entities']=None
 with (HERE/'lead_ueis.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['uei','applied_or_held','settling_fact']);w.writerows((u,'held','Independent physical-address county and current polymer activity verification') for u in sorted(set(leads)))
 (HERE/'metrics.json').write_text(json.dumps(m,indent=2)+'\n')
 return m
if __name__=='__main__':summarize()
