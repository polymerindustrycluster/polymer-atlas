"""Original evidence is released only AFTER all independent/adjudicated verdict hashes freeze."""
import csv,datetime,hashlib,io,json,subprocess
from collections import Counter
from pathlib import Path
from lock import digest
H=Path(__file__).resolve().parent

def main():
 freeze=json.loads((H/'freeze.json').read_text())
 for name,sha in freeze['files'].items():assert hashlib.sha256((H/name).read_bytes()).hexdigest()==sha,'frozen blind file changed'
 assert hashlib.sha256((H/'adjudicated_verdicts.json').read_bytes()).hexdigest()==freeze['adjudicated_sha256'],'adjudication changed after freeze'
 rows=json.loads((H/'adjudicated_verdicts.json').read_text());ids={r['site_id'] for r in rows};assert len(ids)==50
 start=H/'comparison_start.json'
 if not start.exists():start.write_text(json.dumps({'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_before_read':freeze['frozen_at_utc']},indent=2)+'\n')
 assert json.loads(start.read_text())['started_at_utc']>freeze['frozen_at_utc']
 pin=json.loads((H/'frame_provenance.json').read_text())['pinned_main']
 paths=subprocess.check_output(['git','ls-tree','--name-only',pin,'data/']).decode().splitlines();original={i:[] for i in ids}
 for path in paths:
  if not path.startswith('data/evidence_sites_'):continue
  raw=subprocess.check_output(['git','show',pin+':'+path]).decode()
  for r in csv.DictReader(io.StringIO(raw)):
   if r['record_id'] in ids:
    original[r['record_id']].append({k:r[k] for k in ('evidence_id','claim_type','source_class','source_ref','observed_date','tier_effect')})
 out={'pinned_main':pin,'comparison_started_at_utc':json.loads(start.read_text())['started_at_utc'],'records':[dict(site_id=r['site_id'],blind_grade=r['blind_grade'],final_grade=r['grade'],original_evidence=original[r['site_id']]) for r in rows],'typed_claim_coverage':{k:sum(any(e['claim_type']==k for e in es) for es in original.values()) for k in sorted({e['claim_type'] for es in original.values() for e in es})},'source_class_rows':dict(Counter(e['source_class'] for es in original.values() for e in es)),'original_evidence_rows':sum(map(len,original.values())),'interpretation':'Original evidence compared after freeze only; never rewrites a blind result. Missing/weak typed rows are provenance observations, not factual errors.'}
 (H/'original_evidence_comparison.json').write_text(json.dumps(out,indent=2)+'\n')
 print('PASS post-freeze comparison:',out['original_evidence_rows'],'original EVD rows;',out['typed_claim_coverage'],out['source_class_rows'])
if __name__=='__main__':main()
