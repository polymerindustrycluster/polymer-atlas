"""Named packet check: counts, hashes, privacy gate, and three injected defects."""
import copy,hashlib,json,subprocess,sys
from build import D,P,ROOT,read,common
from fetch import safe

def validate(m,manifest):
 assert m['active_pic18_sites']==1046
 assert len(manifest)==2
 for r in manifest:
  p=P/(r['file']+'.filtered.csv')
  assert hashlib.sha256(p.read_bytes()).hexdigest()==r['filtered_sha256']
  rows=read(p)
  assert len(rows)==r['counts']['retained']
  assert all(safe(x) and x['BorrowerState']=='OH' for x in rows)
 assert m['indexed_loans']==sum(r['counts']['retained'] for r in manifest)
 assert m['address']['candidate_sites']==len({r['site_id'] for r in read(P/'matches.csv') if not r['atlas_street'] and r['BorrowerAddress']})
 for label in ['address','jobs']:
  assert m[label]['wilson95']==common.wilson(m[label]['candidate_sites'],m[label]['denominator'])
  assert len(read(D/(label+'_review.csv')))==20
 for p,h in json.loads((D/'atlas_inputs.json').read_text()).items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 assert sum(p.stat().st_size for p in P.glob('*'))<500_000_000

def check_bulk(m):
 from org_bulk import classify,loan_band,ORDER
 rows=read(D/'org_bulk_comparisons.csv');fills=read(D/'org_bulk_fills.csv')
 assert len({(r['grain'],r['record_id']) for r in rows})==len(rows)
 assert len({(r['match_rule'],r['rule'],r['grain'],r['record_id']) for r in fills})==len(fills)
 for r in rows:assert r['comparison']==classify(r['loan_band'],r['atlas_band'])
 for r in m['comparisons']:
  rr=[x for x in rows if x['grain']==r['grain'] and (r['cohort']=='all_matches' or x['single_site_ohio']=='True')]
  assert len(rr)==r['matched_records']
  good=[x for x in rr if x['comparison']!='uncomparable'];assert len(good)==r['comparable']
  for k in ['exact','adjacent','off_two_plus','within_one']:
   n=sum(x['comparison'] in (['exact','adjacent'] if k=='within_one' else [k]) for x in good)
   assert n==r[k]['n'] and common.wilson(n,len(good))==r[k]['wilson95']
 for r in m['fills']:
  rr=[x for x in fills if x['match_rule']==r['match_rule'] and x['rule']==r['rule']]
  assert sum(x['grain']=='organizations' for x in rr)==r['blank_org_bands']
  assert sum(x['grain']=='sites' for x in rr)==r['blank_single_site_bands']
 assert [loan_band(str(n)) for n in [0,1,9,10,49,50,99,100,249,250,499,500,999,1000,4999,5000]]==['','1-9','1-9','10-49','10-49','50-99','50-99','100-249','100-249','250-499','250-499','500-999','500-999','1000-4999','1000-4999','5000+']
 assert all(not loan_band(v) for v in ['','NaN','Infinity','-1','1.5'])
 assert classify('5000+','1000-4999')=='adjacent'
 assert classify('100-249','10-49')=='off_two_plus'
 assert classify('100-249','100-199')=='uncomparable'

def main():
 m=json.loads((D/'metrics.json').read_text());manifest=json.loads((D/'manifest.json').read_text());validate(m,manifest)
 # Independent parser row count is a second pass over each retained input.
 for r in manifest:
  import csv
  with (P/(r['file']+'.filtered.csv')).open() as f:assert sum(1 for _ in csv.reader(f))-1==r['counts']['retained']
 for defect in ['yield','missing_file','hash']:
  mm=copy.deepcopy(m);rr=copy.deepcopy(manifest)
  if defect=='yield':mm['indexed_loans']+=1
  elif defect=='missing_file':rr.pop()
  else:rr[0]['filtered_sha256']='0'*64
  try:validate(mm,rr)
  except AssertionError:print('injected defect rejected:',defect)
  else:raise AssertionError('silent pass: '+defect)
 for typ in ['Sole Proprietorship','Self-Employed Individuals','Independent Contractors','']:
  assert not safe({'BusinessType':typ,'BorrowerName':'EXAMPLE BUSINESS'})
 bulk=json.loads((D/'org_bulk.json').read_text());check_bulk(bulk)
 for defect in ['agreement','fill','interval']:
  bad=copy.deepcopy(bulk)
  if defect=='agreement':bad['comparisons'][0]['exact']['n']+=1
  elif defect=='fill':bad['fills'][0]['blank_org_bands']+=1
  else:bad['comparisons'][0]['exact']['wilson95']=[0,1]
  try:check_bulk(bad)
  except AssertionError:print('bulk injected defect rejected:',defect)
  else:raise AssertionError('bulk silent pass: '+defect)
 before={p.name:p.read_bytes() for p in [D/'metrics.json',D/'address_review.csv',D/'jobs_review.csv',D/'band_review.csv',D/'org_bulk.json',D/'org_bulk_comparisons.csv',D/'org_bulk_fills.csv',D/'README.md']}
 subprocess.run([sys.executable,str(D/'build.py')],check=True);subprocess.run([sys.executable,str(D/'finish.py')],check=True)
 assert all((D/name).read_bytes()==b for name,b in before.items()),'non-idempotent packet'
 print('PASS: packet check; three injected defects rejected; privacy gate; idempotent build')
if __name__=='__main__':main()
