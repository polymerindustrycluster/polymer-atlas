"""Incremental immutable per-record hashes; final freeze gates original-evidence release."""
import argparse,csv,datetime,hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent

def digest(r):return hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def collected():
 rows=[]
 for k in 'abc':
  p=H/f'verdicts_{k}.json'
  if p.exists():rows.extend(json.loads(p.read_text()))
 assert len(rows)==len({r['site_id'] for r in rows}),'duplicate blind result'
 return rows

def main(final=False):
 sample=list(csv.DictReader((H/'sample.csv').open()));ids={r['site_id'] for r in sample}
 rows=collected();now={r['site_id']:digest(r) for r in rows}
 assert set(now)<=ids,'unselected result'
 p=H/'blind_locks.json';old=json.loads(p.read_text()) if p.exists() else {}
 for k,v in old.items():
  if now.get(k)==v:continue
  correction=json.loads((H/'blind_metadata_correction.json').read_text())
  assert k==correction['site_id'] and v==correction['first_lock_hash'] and now[k]==correction['final_hash'],'unreported locked result mutation'
  prior=json.loads((H/'initial_SITE014014_reconstructed.json').read_text())
  assert digest(prior)==v
  revised=json.loads(json.dumps(prior));revised['sources'][0]['source_class']='certification_registry';revised['sources'][1]['source_class']='certification_registry'
  assert revised==next(r for r in rows if r['site_id']==k),'mutation exceeded admitted two metadata fields'

 for r in rows:
  assert r['grade'] in {'agreement','field_error','creation_error','unresolved'}
  assert r['locked_at_utc'] and r['fields_tested'] and r['limitations']
  if r['grade']=='unresolved':assert r['settling_fact']
  if r['grade']=='field_error':assert r['field_errors'] and all(e['field'] and e['proposed_value'] and e['source_url'] and e['quote'] for e in r['field_errors'])
  if r['grade']=='creation_error':assert r['creation_error_reason']
  if r['grade']!='unresolved':assert r['sources'] and all(s['raw_checked'] for s in r['sources'])
 p.write_text(json.dumps(dict(now,**old),indent=2,sort_keys=True)+'\n')
 if final:
  assert set(now)==ids and len(rows)==50,'incomplete blind verdict census'
  assert not (H/'original_evidence_comparison.json').exists(),'evidence already released'
  receipt={'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sample_sha256':hashlib.sha256((H/'sample.csv').read_bytes()).hexdigest(),'files':{f'verdicts_{k}.json':hashlib.sha256((H/f'verdicts_{k}.json').read_bytes()).hexdigest() for k in 'abc'},'records':now,'first_lock_metadata_exception':'blind_metadata_correction.json','adjudicated_sha256':hashlib.sha256((H/'adjudicated_verdicts.json').read_bytes()).hexdigest(),'blindness':'Researchers report no original evidence/source notes read. Assertions and lane/tier metadata exposed. Parent read only locked new-source research until final freeze.'}
  (H/'freeze.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 print('PASS immutable blind locks',len(now),'/50', 'FINAL' if final else 'partial')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');main(p.parse_args().final)
