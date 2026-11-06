"""Bind a live NAS rawHtml/PDF-parser response to the exact requested primary source."""
import argparse,hashlib,json
from retry import CACHE,ROOT,assess,key
ap=argparse.ArgumentParser();ap.add_argument('--url',required=True);ap.add_argument('--response',required=True);ap.add_argument('--pdf',action='store_true');a=ap.parse_args()
response=ROOT/a.response;d=json.loads(response.read_text());m=d.get('metadata') or {}
if d.get('data') and isinstance(d['data'],dict):d=d['data'];m=d.get('metadata') or {}
html=d.get('rawHtml') or '';markdown=d.get('markdown') or ''
route='firecrawl_pdf_text' if a.pdf and not html and markdown else 'firecrawl'
raw=CACHE/(key(a.url,route)+'.raw');raw.write_text(html or (markdown if a.pdf else ''),encoding='utf-8')
r=dict(http_status=m.get('statusCode',0),effective_url=m.get('url',''),exit_code=0,fetched_at=d.get('_retrieved_at',''),request_performed=True,request_maxAge=0,provider_response_path=str(response.relative_to(ROOT)),provider_response_sha256=hashlib.sha256(response.read_bytes()).hexdigest(),scrape_id=m.get('scrapeId',''),parser_page_count=m.get('numPages',m.get('pdfNumPages','')))
f=assess(a.url,route,raw,r,source_url=m.get('url',''))
if not m.get('url'):f['posture']='FETCH_FAILED';f['reason']='NAS final source URL absent; requested URL alone is not source binding'
# Provider input-URL echoes cannot erase an independently observed source redirect.
for method in ['curl','curl_https']:
 p=CACHE/(key(a.url,method)+'.json')
 if p.exists() and json.loads(p.read_text()).get('posture')=='WRONG_PAGE':
  f['posture']='WRONG_PAGE';f['reason']='Native redirect conflicts with NAS input/final-URL identity; explicit binding hold';f['binding_conflict']=True
(CACHE/(key(a.url,route)+'.json')).write_text(json.dumps(f,indent=2)+'\n')
print(json.dumps({k:f.get(k) for k in ['url','route','posture','format','text_path','reason']}))
