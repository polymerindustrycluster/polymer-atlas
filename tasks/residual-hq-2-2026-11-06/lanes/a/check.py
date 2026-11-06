"""Run packet coverage, receipts, quote and parser checks; raw cache stays in /tmp."""
import csv,hashlib,json,pathlib,re,subprocess
from research import BASE,visible

def norm(s):return ' '.join(s.split()).casefold()
def quoted(quote,text):
 parts=quote.split(' || ')
 return sum(len(x.split()) for x in parts)<=25 and all(norm(x) in norm(text) for x in parts)
def coverage(inputs,outputs):
 ids=[r['org_id'] for r in outputs]
 assert len(ids)==len(inputs)==30
 assert len(ids)==len(set(ids))
 assert set(ids)=={r['org_id'] for r in inputs}
def main():
 inp=list(csv.DictReader((BASE/'input.csv').open()));out=list(csv.DictReader((BASE/'verdicts.csv').open()))
 coverage(inp,out)
 manifest=json.loads((BASE/'receipts.json').read_text())
 assert hashlib.sha256((BASE/'input.csv').read_bytes()).hexdigest()==manifest['input_sha256']
 receipts=manifest['fetches']
 # Three known cases: visible markup, forbidden script text, split HQ/address quotes.
 assert visible('<h1>Corporate HQ</h1><p>Elkhart, IN</p>')=='Corporate HQ Elkhart, IN'
 assert not quoted('Headquarters Boston, MA',visible('<script>Headquarters Boston, MA</script><p>Contact Boston, MA</p>'))
 assert quoted('American Renolit Corporation - HQ || LaPorte, IN','American Renolit Corporation - HQ 1207 E. Lincolnway LaPorte, IN 46350 USA')
 # Mutation checks: missing record, duplicate ID, fabricated quote must fail.
 for bad in (out[:-1],out[:-1]+[out[0]]):
  try:coverage(inp,bad)
  except AssertionError:pass
  else:raise AssertionError('coverage accepted defect')
 assert not quoted('Headquarters Atlantis, ZZ','Corporate HQ: Elkhart, IN')
 positive=0
 for r in out:
  rr=[x for x in receipts if x['org_id']==r['org_id']]
  assert int(r['fetch_count'])==len(rr)<=6
  assert r['outcome']==r['verdict'] in ('HQ_FOUND','STILL_UNKNOWN')
  for rc in rr:
   raw=pathlib.Path(rc['path']).read_bytes()
   assert hashlib.sha256(raw).hexdigest()==rc['raw_sha256']
  if r['verdict']=='HQ_FOUND':
   positive+=1
   rc=next(x for x in rr if x['url']==r['source_url'] and x['raw_sha256']==r['raw_sha256'])
   raw=pathlib.Path(rc['path']).read_bytes()
   if raw.startswith(b'%PDF'):
    text=subprocess.check_output(['pdftotext','-raw',rc['path'],'-']).decode()
   else:text=visible(raw.decode('utf-8','replace'))
   assert quoted(r['quote'],text),(r['org_id'],'quote mismatch')
   assert re.search(r'(?i)headquarter|\bHQ\b',r['quote'])
   assert r['hq_city'] and r['hq_state'] and r['hq_country']=='US'
  else:
   assert r['settling_fact']
   assert not any(r[x] for x in ('hq_city','hq_state','hq_country','hq_county','quote'))
 assert positive==6
 print(f'PASS: 30 unique allocated organization verdicts; {positive} HQ_FOUND; {30-positive} STILL_UNKNOWN; {len(receipts)} raw/hash receipts; max fetches {max(int(r["fetch_count"]) for r in out)}; 3 parser/source cases and 3 defect mutations.')
if __name__=='__main__':main()
