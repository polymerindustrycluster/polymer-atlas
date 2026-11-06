import sys
sys.dont_write_bytecode=True
import json,hashlib,pathlib,subprocess,re
from research import BASE,visible

def norm(s):return ' '.join(s.split()).casefold()
def matched(q,text):
 parts=q.split(' || ')
 if not q or sum(len(p.split()) for p in parts)>25:return False
 start=0;text=norm(text)
 for p in parts:
  index=text.find(norm(p),start)
  if index<0:return False
  start=index+len(norm(p))
 return True
def coverage(inputs,outputs):
 assert len(inputs)==len(outputs)==5
 assert len({r['pair_id'] for r in outputs})==5
 expected={r['pair_id']:(r['a_id'],r['b_id'],r['record_table']) for r in inputs}
 assert {r['pair_id']:(r['a_id'],r['b_id'],r['record_table']) for r in outputs}==expected

def merge_allowed(proof):
 return bool(proof.get('source_date') and proof.get('primary') and proof.get('same_legal_entity') and (not proof.get('is_site') or proof.get('same_establishment')))

def main():
 inputs=json.loads((BASE/'input.json').read_text());outputs=json.loads((BASE/'verdicts.json').read_text());manifest=json.loads((BASE/'receipts.json').read_text());receipts=manifest['fetches']
 coverage(inputs,outputs)
 assert hashlib.sha256((BASE/'input.json').read_bytes()).hexdigest()==manifest['input_sha256']
 assert manifest['baseline']=='542629e'
 texts={}
 for rc in receipts:
  raw=pathlib.Path(rc['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==rc['raw_sha256']
  text=subprocess.check_output(['pdftotext','-raw',rc['path'],'-']).decode() if raw.startswith(b'%PDF') else visible(raw.decode('utf-8','replace'))
  texts[rc['raw_sha256']]=text
 for r in outputs:
  assert r['verdict'] in ('VERIFIED','STILL_UNCERTAIN','REJECT') or r['verdict'].startswith('DUPLICATE_OF')
  assert r['decision'] in ('SAME_ENTITY','DISTINCT','LINK_FLAG')
  assert r['recommendation'] and r['reason']
  if r['verdict']=='STILL_UNCERTAIN':assert r['settling_fact'] and r['decision']=='LINK_FLAG'
  assert not r['duplicate_of'] and r['decision']!='SAME_ENTITY'
  for org,count in r['primary_fetch_count_by_org'].items():
   assert count==sum(org in x['org_ids'] for x in receipts)<=5
  for ev in r['evidence']:
   assert ev['observed_date']=='2026-11-06' and ev['date_basis']
   assert ev['source_class'] in ('own_site','government_filing')
   assert not ev['source_date'] or re.fullmatch(r'\d{4}-\d{2}-\d{2}',ev['source_date'])
   assert set(ev['endpoint_ids'])<={r['a_id'],r['b_id']}
   assert any(x['url']==ev['source_url'] and x['raw_sha256']==ev['raw_sha256'] for x in receipts)
   assert matched(ev['quote'],texts[ev['raw_sha256']]),(r['pair_id'],'quote mismatch',ev['quote'])
 byid={r['pair_id']:r for r in outputs}
 # Three actual-source known answers, not invented expected legal equivalences.
 assert byid['D03']['decision']=='DISTINCT' and 'parent company' in byid['D03']['evidence'][0]['quote']
 assert byid['D04']['decision']=='DISTINCT' and 'A subsidiary of Bridgestone Americas' in byid['D04']['evidence'][1]['quote']
 assert byid['D05']['decision']=='LINK_FLAG' and all(x in byid['D05']['evidence'][0]['quote'] for x in ('NORTH PLANT','SOUTH PLANT','1550','1441'))
 # Mutation controls exercise the actual merge predicate, not parallel prose checks.
 full=dict(source_date='2025-01-01',primary=True,same_legal_entity=True,is_site=True,same_establishment=True)
 assert merge_allowed(full)
 assert not merge_allowed(dict(full,same_legal_entity=False,shared_address=True))
 assert not merge_allowed(dict(full,same_legal_entity=False,parent_only=True))
 assert not merge_allowed(dict(full,source_date=''))
 assert not merge_allowed(dict(full,same_establishment=False))
 assert not matched('A fabricated alias proves identity','No identity claim was stated')
 assert not matched('B || A','A B')
 for bad in (outputs[:-1],outputs[:-1]+[outputs[0]]):
  try:coverage(inputs,bad)
  except AssertionError:pass
  else:raise AssertionError('coverage silently accepted defect')
 print('PASS: exact 5 pairs/endpoints; 2 VERIFIED DISTINCT + 3 STILL_UNCERTAIN LINK_FLAG; 20 raw hashes; every quote <=25 source words and ordered; dates/periods explicit; max 5 helper fetches/org; 3 source known answers; address-only, parent-only, undated, different-site, fabricated-quote, reversed-order, missing/duplicate-pair faults rejected.')
if __name__=='__main__':main()
