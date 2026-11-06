"""Seeded 30-fill fresh raw-page audit, with a full census when fewer than30 accepted."""
import concurrent.futures,json,random
from build import TASK,read
from fetch import fetch,write,extract
evidence=read(TASK/'evidence.csv');sample=random.Random(20261106).sample(sorted(evidence,key=lambda e:e['record_id']),min(30,len(evidence)));sites={r['site_id']:r for r in read(TASK/'frame.csv')}
def check(e):
 error='';sha=''
 try:
  text,links,sha=fetch(e['source_ref'])
  quote=e['notes'].split('; quote: ')[1].removesuffix('. County, county_source, ZIP and record tier unchanged.')
  assert ' '.join(quote.split()) in ' '.join(text.split()),'raw quote absent on fresh fetch'
  assert extract(quote,sites[e['record_id']]['city']),'quote not a city-specific physical address block'
 except Exception as ex:error=str(ex)
 return dict(site_id=e['record_id'],source_ref=e['source_ref'],sha256=sha,result='PASS' if not error else 'FAIL',error=error)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(check,sample))
write(TASK/'audit.csv',out)
summary=dict(accepted_fills=len(evidence),audited=len(out),errors=sum(bool(r['error']) for r in out))
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert len(out)==min(30,len(evidence)) and summary['errors']==0,out
