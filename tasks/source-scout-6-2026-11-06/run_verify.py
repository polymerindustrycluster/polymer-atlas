"""Verify the non-duplicate rows of <route>/sample_pre.csv by own-site fetch (<=6 fetches/row) and write <route>/sample.csv with final verdicts.
Usage: python3 -I run_verify.py fda|fied|usaspending|dol   (live network; check.py is offline and reads the committed sample.csv)"""
import csv,sys,time,datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import common,verify
KEY={'fda':'registration_number','fied':'registry_id','usaspending':'uei','dol':'unit_key','ftz':'company'}
SRC={'fda':'FDA Establishment Registration & Device Listing weekly bulk files (accessdata.fda.gov/premarket/ftparea)','fied':'NREL Foundational Industry Energy Dataset 2017 (data.openei.org/submissions/6158)',
 'usaspending':'USAspending.gov API FY2025 contract recipients','dol':'DOL OFLC LCA Disclosure Data FY2025 Q4 (Wayback capture 20260114000337)','ftz':'ITA OFIS FTZ Production Database (ofis.trade.gov/ManufacturingDB)'}
def seeds(route,key):
 for r in csv.DictReader(open(HERE/'seeds.csv')):
  if r['route']==route and r['key_contains'] in key:return ([r['url']] if r['url'] else []),r['note']
 return [],''
def main(route,only=None):
 rows=list(csv.DictReader(open(HERE/route/'sample_pre.csv')));out=[];today=datetime.date.today().isoformat()
 kept={r[KEY[route]]:r for r in csv.DictReader(open(HERE/route/'sample.csv'))} if only else {}  # --only SUBSTRING re-verifies matching rows and keeps the rest
 for r in rows:
  if only and only not in r[KEY[route]]:out.append(kept[r[KEY[route]]]);continue
  ch='';note='';v=dict(fetches=0,url='',status='',sha256='',address_found=0,name_found=0,polymer_words='',process_hit=0,process_witness='',quote='',note='')
  if r['duplicate_of']:verdict,reason='DUPLICATE_OF',f"held {r['duplicate_of']} by registry link or singleton exact street+locality; not re-verified"
  else:
   ch=verify.corpus_hit(r['street']) if r.get('street') else ''
   su,note=seeds(route,r[KEY[route]].lower() if route=='dol' else r[KEY[route]])
   v=verify.verify(r.get('sam_name') or r.get('frs_name') or r.get('name') or r['employer_name'],r['street'],r['city'],r['state'],seed_urls=su,max_fetch=5 if su else 6) if (su or not note) else verify.verify('','','','');time.sleep(1)
   if su:v['fetches']+=1  # the SearXNG search that produced the seed URL
   if note and not su:v['fetches']=1
   v['note']=(v['note']+' '+note).strip() if note else v['note']
   if v['address_found'] and v['name_found'] and v['process_hit'] and v['polymer_words'] and v['process_witness']:verdict,reason='VERIFIED',f"own site states the entity name and street address, and on that same page a polymer word within 80 chars of a process word; fetched {today}; existence/address/liveness plus a scope lead, ring/scope is an owner ruling"
   elif v['address_found'] and v['name_found']:verdict,reason='STILL_UNCERTAIN',f"own site states the address (live {today}) but no polymer process wording on that page ({v['fetches']} fetches){('; '+v['note'].strip()) if v['note'].strip() else ''}; settling fact: own-site statement of a polymer process at this site"
   else:verdict,reason='STILL_UNCERTAIN',f"no own-site page stating this street address within {v['fetches']} fetches ({v['note'].strip() or 'no address on visited pages'}); settling fact: own-site or primary record of the establishment at this address; a failed or unmatched fetch is not evidence of closure"
  out.append(dict(r,verdict=verdict,verified_new=int(verdict=='VERIFIED'),verify_fetches=v['fetches'],verify_url=v['url'],verify_http=v['status'],verify_sha256=v['sha256'],verify_address_found=v['address_found'],
   verify_name_found=v['name_found'],verify_polymer_words=v['polymer_words'],verify_process_hit=v['process_hit'],verify_process_witness=v['process_witness'] if verdict=='VERIFIED' else '',verify_quote=v['quote'] if verdict=='VERIFIED' else '',seed_note=note if not r['duplicate_of'] else '',verify_date=today if not r['duplicate_of'] else '',corpus_street_hit=(ch if not r['duplicate_of'] else ''),reason=reason,source=SRC[route]))
  print(route,r[KEY[route]],verdict,v['fetches'],flush=True)
 for d in out:d.setdefault('verify_process_witness','')  # rows kept by --only predate the column
 common.write_csv(HERE/route/'sample.csv',[{**{'verify_process_witness':''},**d} for d in out],list(max(out,key=len)))
if __name__=='__main__':main(sys.argv[1],sys.argv[3] if len(sys.argv)>3 and sys.argv[2]=='--only' else None)
