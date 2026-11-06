"""Exact 16-site follow-up census and immutable incremental locks, no original evidence read."""
import argparse,csv,datetime,hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent

def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def digest(r):return hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def collected():
 rows=[]
 for k in 'ab':
  p=H/f'verdicts_{k}.json'
  if p.exists():rows+=json.loads(p.read_text())
 assert len(rows)==len({r['site_id'] for r in rows}),'duplicate verifier output'
 return rows

def main(final=False):
 inputs=read(H/'input.csv');expected={r['site_id'] for r in inputs};baseline=json.loads((H/'baseline.json').read_text())
 assert len(inputs)==len(expected)==16 and expected==set(baseline['followup_ids'])
 rows=collected();current={r['site_id']:digest(r) for r in rows};assert set(current)<=expected
 p=H/'locks.json';prior=json.loads(p.read_text()) if p.exists() else {}
 assert all(current.get(k)==v for k,v in prior.items()),'post-lock mutation or lost record'
 for r in rows:
  assert r['grade'] in {'agreement','field_error','creation_error','unresolved'} and r['locked_at_utc'] and r['limitations']
  if r['grade']=='unresolved':assert r['settling_fact']
  if r['grade']=='field_error':assert r['field_errors']
  if r['grade']=='creation_error':assert r['creation_error_reason']
  if r['grade']!='unresolved':assert r['sources'] and all(s['raw_checked'] for s in r['sources'])
 p.write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
 if final:
  assert len(rows)==16 and set(current)==expected
  out=H/'freeze.json';assert not out.exists(),'final freeze already exists'
  out.write_text(json.dumps({'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':current,'files':{f'verdicts_{k}.json':hashlib.sha256((H/f'verdicts_{k}.json').read_bytes()).hexdigest() for k in 'ab'},'input_sha256':hashlib.sha256((H/'input.csv').read_bytes()).hexdigest(),'blindness':'Fresh verifiers report no original evidence/old audit verdict/report/canonical source notes read; frozen assertions/selection-as-previously-unresolved known. Parent is unblinded integrator.'},indent=2,sort_keys=True)+'\n')
 print('PASS immutable follow-up locks',len(rows),'/16', 'FINAL' if final else 'partial')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');main(p.parse_args().final)
