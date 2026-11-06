"""Bounded rendered-route recovery is availability-only; frozen16 grades never change."""
import hashlib,json
from collections import Counter
from pathlib import Path
from rawcheck import H,Text,found

def main():
 supplemental=json.loads((H/'supplement_b.json').read_text());receipts=json.loads((H/'supplement_receipts_b.json').read_text());original=json.loads((H/'verdicts_b.json').read_text());freeze=json.loads((H/'freeze.json').read_text())
 assert hashlib.sha256((H/'verdicts_b.json').read_bytes()).hexdigest()==freeze['files']['verdicts_b.json']
 assert len(supplemental)==len({r['site_id'] for r in supplemental})==4
 assert len(receipts)==9
 roles=Counter(r['role'] for r in receipts);assert roles.get('target')==6 and sum(v for k,v in roles.items() if k!='target')==3
 for rec in receipts:
  for pathkey,hashkey,byteskey in [('raw_path','sha256','bytes'),('tool_response_path','tool_response_sha256','tool_response_bytes')]:
   raw=Path(rec[pathkey]).read_bytes();assert hashlib.sha256(raw).hexdigest()==rec[hashkey] and len(raw)==rec[byteskey]
  assert rec['request']['maxAge']==0 and not any(x in rec['request'] for x in ['jsonOptions','extract','actions'])
 prior={r['site_id']:r for r in original}
 for r in supplemental:
  assert r['grade']==prior[r['site_id']]['grade']=='unresolved' and r['locked_at_utc']
  assert r['supersedes_original_followup_hash']==freeze['files']['verdicts_b.json'],'this field points to the prior FILE hash, not object hash'
  for source in r['sources']:
   assert source['source_class']=='route_availability_only','supplement cannot silently promote a site claim'
   body=Path(source['raw_path']).read_bytes();assert hashlib.sha256(body).hexdigest()==source['sha256']
   parser=Text();parser.feed(body.decode('utf-8','replace'));text=' '.join(parser.parts)
   assert found(text,source['quote']) and not found(text,source['quote']+' fabricated lunar qualification')
 cal=supplemental[0]['calibration'];assert cal['passed'] and len(cal['positive_records'])==3
 for r in cal['positive_records']:
  body=Path(r['raw_path']).read_bytes();assert hashlib.sha256(body).hexdigest()==r['raw_sha256']
  parser=Text();parser.feed(body.decode('utf-8','replace'));text=' '.join(parser.parts)
  assert found(text,r['positive_quote']) and not found(text,r['fabricated_negative'])
 base=[]
 for k in 'ab':base+=json.loads((H/f'receipts_{k}.json').read_text())
 counts=Counter(r['site_id'] for r in base+receipts if not r['url'].startswith('web-search://'))
 parent=json.loads((H/'parent_request_accounting.json').read_text())
 charged=counts+Counter(parent['site_budget_charges'])
 assert max(counts.values())<=10 and max(charged.values())<=10
 result={'supplement_sha256':hashlib.sha256((H/'supplement_b.json').read_bytes()).hexdigest(),'receipt_sha256':hashlib.sha256((H/'supplement_receipts_b.json').read_bytes()).hexdigest(),'target_requests':6,'known_answer_requests':3,'positive_site_findings':0,'grades_unchanged':True,'combined_logged_attempts':len(base)+9,'verifier_source_requests':sum(counts.values()),'parent_http_requests':parent['known_answer_and_diagnostic_http_requests'],'all_recorded_source_http_requests':sum(counts.values())+parent['known_answer_and_diagnostic_http_requests'],'source_budget_charges_with_shared_parent_fetches':dict(charged),'combined_max_source_requests_per_site':max(counts.values()),'site_source_counts':dict(counts),'timing_limit':cal['timing'],'fetch_limit':'maxAge0 requested; metadata does not independently attest origin cache age. No positive site fact inferred from this supplement.'}
 (H/'supplement_check_results.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS4unchangedholds/6target+3KAT/rawHTML+toolresponsehashes+quotes/3positive+fakeKAT/sourcebudget<=10/original16immutable/0newfacts')
if __name__=='__main__':main()
