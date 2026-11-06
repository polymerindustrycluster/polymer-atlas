"""Retain short raw text witnesses and hold context, not downloaded full pages."""
from research import D,has
import csv,json,re,hashlib
from collections import defaultdict
by=defaultdict(list)
for r in csv.DictReader((D/'packet.csv').open()):by[r['raw_path']].append(r['quote'])
cal=json.loads((D/'calibration.json').read_text());by[cal['raw_path']].append(cal['quote'])
for row in csv.DictReader((D/'frame.csv').open()):
 folder=D/'raw'/row['org_id'];rp=folder/'routes.json';rr=json.loads(rp.read_text())
 for r in rr:
  p=D/r['raw_path'];t=' '.join(p.read_text().split());original_hash=hashlib.sha256(t.encode()).hexdigest();ranges=[]
  for q in by.get(r['raw_path'],[]):
   i=t.lower().find(' '.join(q.split()).lower());assert i>=0,(r['raw_path'],q);ranges.append((max(0,i-130),min(len(t),i+len(q)+150)))
  if not ranges:
   # Preserve concise availability and decision context for holds.
   ranges=[(0,min(300,len(t)))]
   needles=[row['hq_city'],'Headquartered in','new headquarters','Radici Plastics USA LLC','Endura Plastics','Stewart Acquisitions']
   for needle in needles:
    if len(needle)<3:continue
    m=re.search(r'\b'+re.escape(needle)+r'\b',t,re.I)
    if m:ranges.append((max(0,m.start()-80),min(len(t),m.end()+240)))
  merged=[]
  for a,b in sorted(ranges):
   if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
   else:merged.append((a,b))
  excerpt='\n[... excerpt boundary ...]\n'.join(t[a:b] for a,b in merged)
  excerpt=re.sub(r'(?:\+?1[\s.-]*)?\(?[2-9]\d{2}\)?[\s.-]*\d{3}[\s.-]*\d{4}','[phone redacted]',excerpt)
  for q in by.get(r['raw_path'],[]):assert has(excerpt,q),(p,q)
  p.write_text(excerpt+'\n');r['notes']+=' Retained short extracted-text excerpt; normalized pre-excerpt SHA256='+original_hash+'.'
 rp.write_text(json.dumps(rr,indent=2))
for p in (D/'raw').glob('*/firecrawl-response.json'):
 x=json.loads(p.read_text());h=hashlib.sha256(p.read_bytes()).hexdigest();p.write_text(json.dumps({'response_sha256':h,'note':'Raw HTML fetched in this pass, parsed with lead Text; full response discarded after retaining contact-redacted short text excerpts.','text_path':'firecrawl.txt'},indent=2))
for p in D.glob('gov-search-*.json'):
 x=json.loads(p.read_text());x={'org_ids':x['org_ids'],'queries':x['queries'],'result_sha256':hashlib.sha256(str(x['result']).encode()).hexdigest(),'notes':'Government discovery search only. Broad or unmatched results not evidence; specific primary routes are in routes.csv. Full search dumps discarded to exclude unrelated personal contacts.'};p.write_text(json.dumps(x,indent=2))
p=D/'ita_candidates.json';rows=json.loads(p.read_text());keys=['org_id','establishment_id','ita_row_id','company_name','establishment_name','street','city','state','zip5','naics_code','naics_year','industry_description','date_submitted','year_filing_for'];p.write_text(json.dumps([{k:r[k] for k in keys} for r in rows],indent=2))
print('PASS: excerpts preserve every packet quote; full page/HTML dumps and unnecessary filing fields discarded')
