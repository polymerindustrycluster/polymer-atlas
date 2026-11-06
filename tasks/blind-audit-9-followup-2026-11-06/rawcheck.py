"""Verify fresh blind citations against hashed raw bodies; never treat unread text as a pass."""
import argparse,csv,hashlib,json,runpy,subprocess,sys,tempfile
from pathlib import Path
H=Path(__file__).resolve().parent
ROOT=H.parents[1]
sys.path.insert(0,str(ROOT/'tasks/pic18-record-health-2026-11-06'))
Text=runpy.run_path(str(ROOT/'tasks/pic18-record-health-2026-11-06/refetch.py'))['Text']
W=runpy.run_path(str(ROOT/'tasks/evidence-repair-2-2026-11-04/prep.py'))['W']
def found(text,quote):
 p,q=W(text),W(quote)
 return bool(q) and any(p[i:i+len(q)]==q for i in range(len(p)-len(q)+1))
def extracted(raw,path):
 if raw.startswith(b'%PDF'):
  return [subprocess.check_output(['pdftotext',*option,str(path),'-']).decode('utf-8','replace') for option in [[],['-layout']]]
 text=raw.decode('utf-8','replace')
 if text.lstrip().startswith(('{','[')):
  try:text=json.dumps(json.loads(text),ensure_ascii=False)
  except json.JSONDecodeError:pass
 parser=Text();parser.feed(text)
 return [' '.join(parser.parts)]
def main():
 assert found('Polymer & foam manufacturing','Polymer foam')
 assert found('Storopack, Inc. 320 Craig Place','320 Craig Place')
 assert found('CAFÉ molding 123','cafe molding 123')
 assert not found('polymer foam manufacturing','fabricated lunar qualification')
 rows=[];attempts=[];ocr=[]
 for k in 'ab':
  calibration=json.loads((H/f'calibration_{k}.json').read_text())
  mapping=calibration.get('ocr_map',[])
  ocr.extend([mapping] if isinstance(mapping,dict) else mapping)
  rows+=json.loads((H/f'verdicts_{k}.json').read_text());attempts+=json.loads((H/f'receipts_{k}.json').read_text())
 assert len(rows)==len({r['site_id'] for r in rows})==16,'incomplete16-site quote census'
 paths={};results=[];holdouts=[];unarchived=[];verified_bodies=0
 for rec in attempts:
  if not rec['raw_path']:
   assert rec['error'] and int(rec['bytes'])==0 and rec['sha256']==hashlib.sha256(b'').hexdigest(),'unreported missing rawbody'
   assert str(rec.get('status',rec.get('http_status')))!='200','successful response body unavailable'
   unarchived.append({'site_id':rec['site_id'],'url':rec['url'],'status':rec.get('status',rec.get('http_status')),'reason':rec['error']});continue
  p=Path(rec['raw_path']);b=p.read_bytes();assert len(b)==int(rec['bytes']) and hashlib.sha256(b).hexdigest()==rec['sha256'],'raw receipt mismatch'
  verified_bodies+=1
  if str(rec.get('status',rec.get('http_status')))=='200':paths[rec['site_id'],rec['url']]=rec
 for r in rows:
  for source in r['sources']:
   if not source['raw_checked']:
    assert r['grade']=='unresolved','unread settled finding';holdouts.append({'site_id':r['site_id'],'url':source['url'],'reason':'explicit unread/discovery citation'});continue
   rec=paths[r['site_id'],source['url']];assert str(rec.get('status',rec.get('http_status')))=='200','non200 source claimed read'
   p=Path(rec['raw_path']);candidates=extracted(p.read_bytes(),p)
   if not any(found(t,source['quote']) for t in candidates):
    maps=[m for m in ocr if m['site_id']==r['site_id'] and m['pdf_sha256']==rec['sha256']]
    for mapping in maps:
     assert mapping['visual_check'] and hashlib.sha256(p.read_bytes()).hexdigest()==mapping['pdf_sha256']
     page=int(mapping['page_number']);assert page>0
     with tempfile.TemporaryDirectory() as temp:
      prefix=Path(temp).resolve()/'page'
      subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','5000','-png','-singlefile',str(p),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
      candidates.append(subprocess.check_output(['tesseract',str(prefix)+'.png','stdout'],stderr=subprocess.DEVNULL).decode('utf-8','replace'))
   assert any(found(t,source['quote']) for t in candidates),('raw quote missing; OCR requires explicit page review, not silent skip',r['site_id'],source['url'],source['quote'])
   assert not any(found(t,source['quote']+' fabricated lunar qualification') for t in candidates),'fabricated addition accepted'
   results.append({'site_id':r['site_id'],'url':source['url'],'quote':source['quote'],'raw':'yes','sha256':rec['sha256']})
 (H/'rawcheck_results.json').write_text(json.dumps({'checked_quote_observations':len(results),'held_out_citations':holdouts,'attempted_routes':len(attempts),'raw_bodies_verified':verified_bodies,'unarchived_discovery_or_failed_routes':unarchived,'quotes':results},indent=2)+'\n')
 print('PASS',len(rows),'sites;',len(results),'rawquote observations;',len(holdouts),'explicit unreadholdouts;',verified_bodies,'rawbodyhash/byte receipts;',len(unarchived),'unarchived discovery/failed attempts explicitly excluded from sources;fabrications rejected')
if __name__=='__main__':main()
