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
 before={p.name:p.read_bytes() for p in [D/'metrics.json',D/'address_review.csv',D/'jobs_review.csv',D/'band_review.csv']}
 subprocess.run([sys.executable,str(D/'build.py')],check=True);subprocess.run([sys.executable,str(D/'finish.py')],check=True)
 assert all((D/name).read_bytes()==b for name,b in before.items()),'non-idempotent packet'
 print('PASS: packet check; three injected defects rejected; privacy gate; idempotent build')
if __name__=='__main__':main()
