"""Retain concise witnesses/hold context rather than full page/HTML bodies."""
from research import D,has
import csv,json,re,hashlib
from collections import defaultdict
qq=defaultdict(list)
for r in csv.DictReader((D/'packet.csv').open()):qq[r['raw_path']].append(r['quote'])
for r in json.loads((D/'calibration_controls.json').read_text()):qq[r['raw_path']].append(r['quote'])
cal=json.loads((D/'calibration.json').read_text());qq[cal['new_route']['raw_path']].append(cal['positive_quote'])
for folder in (D/'raw').iterdir():
 rp=folder/'routes.json'
 if not rp.exists():continue
 rr=json.loads(rp.read_text())
 for r in rr:
  p=D/r['raw_path'];t=' '.join(p.read_text().split());ranges=[(0,min(280,len(t)))];r['notes']+=' Pre-excerpt normalized-text SHA256='+hashlib.sha256(t.encode()).hexdigest()+'. Short contact-redacted text excerpt retained.'
  for q in qq.get(r['raw_path'],[]):
   i=t.lower().find(' '.join(q.split()).lower());assert i>=0,(p,q);ranges.append((max(0,i-180),min(len(t),i+len(q)+180)))
  if not qq.get(r['raw_path']):
   for term in ['PVC','North America','nylon rings','Nylon Filament','Injection Molded','reinforced vinyl','High-density polyethylene','RFD Beaufort','graphite','polymer']:
    m=re.search(re.escape(term),t,re.I)
    if m:ranges.append((max(0,m.start()-80),min(len(t),m.end()+150)));break
  merged=[]
  for a,b in sorted(ranges):
   if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(merged[-1][1],b))
   else:merged.append((a,b))
  out='\n[... excerpt boundary ...]\n'.join(t[a:b] for a,b in merged)
  for q in qq.get(r['raw_path'],[]):assert has(out,q),(p,q)
  p.write_text(out+'\n')
 rp.write_text(json.dumps(rr,indent=2))
for p in (D/'raw').glob('*/firecrawl-response.json'):
 x=json.loads(p.read_text());p.write_text(json.dumps({'requested_url':x['requested_url'],'response_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'notes':'Fresh NAS formats=html maxAge0; raw HTML parsed without summaries; full response discarded after contact-redacted excerpts.'},indent=2))
for p in D.glob('search-*.json'):
 x=json.loads(p.read_text());x['result_sha256']=hashlib.sha256(x.pop('result').encode()).hexdigest();x['notes']='Discovery only; no model summary or search excerpt admitted as evidence. URLs and queries retained; full search dumps discarded.';p.write_text(json.dumps(x,indent=2))
print('PASS quote-preserving excerpts and metadata only; all full body/HTML/search dumps removed')
