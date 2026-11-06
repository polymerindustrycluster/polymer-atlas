"""Packet check, including raw PDF excerpts and deliberate defects."""
import sys
sys.dont_write_bytecode=True
import csv,json,hashlib,pathlib,re,subprocess
from research import BASE,visible
FIELDS='org_id legal_name verdict outcome hq_city hq_state hq_country hq_county source_url source_class quote fetch_count reason settling_fact note raw_sha256'.split()
def norm(s):return ' '.join(s.split()).casefold()
def quote_matches(q,text):
 parts=q.split(' || ')
 if not q or sum(len(x.split()) for x in parts)>25:return False
 text=norm(text);start=0
 for part in parts:
  at=text.find(norm(part),start)
  if at<0:return False
  start=at+len(norm(part))
 return True
def coverage(inputs,outputs):
 ids=[r['org_id'] for r in outputs]
 assert len(inputs)==len(outputs)==25
 assert len(ids)==len(set(ids))
 assert set(ids)=={r['org_id'] for r in inputs}
def header(fields):assert list(fields)==FIELDS
def extract(rc):
 raw=pathlib.Path(rc['path']).read_bytes()
 return subprocess.check_output(['pdftotext','-raw',rc['path'],'-']).decode() if raw.startswith(b'%PDF') else visible(raw.decode('utf-8','replace'))
def main():
 inputs=list(csv.DictReader((BASE/'input.csv').open()))
 with (BASE/'verdicts.csv').open() as f:
  reader=csv.DictReader(f);header(reader.fieldnames);outputs=list(reader)
 coverage(inputs,outputs)
 manifest=json.loads((BASE/'receipts.json').read_text());receipts=manifest['fetches']
 assert hashlib.sha256((BASE/'input.csv').read_bytes()).hexdigest()==manifest['input_sha256']
 byid={r['org_id']:r for r in outputs}
 # Three actual source known answers, including calibrated PDF columns and rebrand.
 expected={'ORG-007432':('Monroe','LA'),'ORG-007712':('Hopkins','MN'),'ORG-007729':('Clearwater','MN')}
 for oid,pair in expected.items():
  r=byid[oid];assert r['outcome']=='HQ_FOUND' and (r['hq_city'],r['hq_state'])==pair
  rc=next(x for x in receipts if x['org_id']==oid and x['url']==r['source_url'])
  assert quote_matches(r['quote'],extract(rc))
 # Known other-entity HQ is a hold, never Omega -> Sigma's Florida headquarters.
 assert byid['ORG-007428']['outcome']=='STILL_UNKNOWN'
 # Six defect controls: missing row, duplicate ID, missing header, false quote,
 # hidden-script HQ and reversed excerpt order.
 for bad in (outputs[:-1],outputs[:-1]+[outputs[0]]):
  try:coverage(inputs,bad)
  except AssertionError:pass
  else:raise AssertionError('coverage accepted defect')
 try:header(FIELDS[:-1])
 except AssertionError:pass
 else:raise AssertionError('header accepted defect')
 assert not quote_matches('Headquarters Atlantis, ZZ','Contact Minneapolis, MN')
 assert not quote_matches('Headquarters Atlantis, ZZ',visible('<script>Headquarters Atlantis, ZZ</script><p>Contact</p>'))
 assert not quote_matches('Clearwater, MN || HEADQUARTERS','HEADQUARTERS Clearwater, MN')
 for rc in receipts:
  assert rc['org_id'] in byid
  assert hashlib.sha256(pathlib.Path(rc['path']).read_bytes()).hexdigest()==rc['raw_sha256']
 for r in outputs:
  rr=[x for x in receipts if x['org_id']==r['org_id']]
  assert len(rr)==int(r['fetch_count'])<=5
  assert r['outcome']==r['verdict'] in ('HQ_FOUND','STILL_UNKNOWN')
  assert r['legal_name']==next(x['legal_name'] for x in inputs if x['org_id']==r['org_id'])
  assert not r['hq_county']
  if r['outcome']=='HQ_FOUND':
   assert r['hq_city'] and re.fullmatch('[A-Z]{2}',r['hq_state']) and r['hq_country']=='US'
   assert r['source_class']=='own_site' and re.search('(?i)headquarter',r['quote'])
   rc=next(x for x in rr if x['url']==r['source_url'] and x['raw_sha256']==r['raw_sha256'])
   assert quote_matches(r['quote'],extract(rc)),r['org_id']
  else:
   assert r['reason'] and r['settling_fact']
   assert not any(r[x] for x in ('hq_city','hq_state','hq_country','quote'))
 count=sum(r['outcome']=='HQ_FOUND' for r in outputs);assert count==3
 print(f'PASS: 25 unique exact allocated organization IDs; {count} HQ_FOUND / {25-count} STILL_UNKNOWN; {len(receipts)} raw/hash receipts; max {max(int(r["fetch_count"]) for r in outputs)} primary fetches/org; 3 real-source known answers + parent-HQ negative; 6 fault controls rejected; all positive excerpts <=25 total words and ordered in raw source text.')
if __name__=='__main__':main()
