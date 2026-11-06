#!/usr/bin/env python3
"""Bounded own-domain route collection; candidates require human semantic review."""
import csv, json, re, sys, subprocess, hashlib, unicodedata
from pathlib import Path
from urllib.parse import urljoin,urlparse
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from raw import Text
D=Path(__file__).resolve().parent
W=lambda s: re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower())
def has(text,phrase):
 t,p=W(text),W(phrase)
 return bool(p) and any(t[i:i+len(p)]==p for i in range(len(t)-len(p)+1))
def fetch(oid,url,kind):
 folder=D/'raw'/oid; folder.mkdir(parents=True,exist_ok=True)
 key=hashlib.sha256(url.encode()).hexdigest()[:12]; body=folder/(key+'.body'); txt=folder/(key+'.txt')
 p=subprocess.run(['curl','-L','--max-time','22','--connect-timeout','8','-A','Mozilla/5.0','-sS','-w','%{http_code}\t%{url_effective}',url,'-o',str(body)],capture_output=True,text=True)
 meta=p.stdout.split('\t',1); code=meta[0]; final=meta[-1]; b=body.read_bytes() if body.exists() else b''
 err=p.stderr.strip()
 if b.startswith(b'%PDF'):
  q=subprocess.run(['pdftotext','-layout',str(body),str(txt)],capture_output=True,text=True); text=txt.read_text(errors='replace') if txt.exists() else ''; err+=' '+q.stderr.strip()
 else:
  raw=b.decode('utf-8',errors='replace'); x=Text(); x.feed(raw); text=' '.join(' '.join(x.parts).split()); txt.write_text(text)
 raw=b.decode('utf-8',errors='replace') if not b.startswith(b'%PDF') else ''
 # Keep text witnesses without scraped contact details; source URLs allow independent re-fetch.
 text=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[contact redacted]', text)
 text=re.sub(r'(?<![\w])(?:\+?1[ .-]?)?\(?[2-9]\d{2}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)', '[phone redacted]', text)
 txt.write_text(text)
 if body.exists(): body.unlink()
 route=dict(org_id=oid,kind=kind,source_ref=url,final_url=final,http_status=code,availability=('available' if code.startswith('2') and len(text)>100 else 'failed_or_empty'),raw_path=str(txt.relative_to(D)),error=err)
 return route,text,raw

def collect(row):
 oid=row['org_id']; base=row['website']; base=base if '://' in base else 'https://'+base
 root=urljoin(base,'/'); out=[]; seen=set(); links=[]
 def get(url,kind):
  seen.add(url); r,t,h=fetch(oid,url,kind); out.append(r)
  # URL discovery only; ownership constrained to the corporate host.
  for link in re.findall(r'(?:href=["\']([^"\']+)|<loc>\s*([^<]+))',h,re.I):
   u=urljoin(r['final_url'] if r['final_url'].startswith('http') else root,link[0] or link[1]).split('#')[0].replace('&amp;','&')
   host=urlparse(u).hostname or ''; orig=urlparse(root).hostname or ''
   if host.removeprefix('www.')==orig.removeprefix('www.') and u not in links: links.append(u)
  return r,t,h
 get(urljoin(root,'sitemap.xml'),'sitemap')
 r,t,h=get(base,'home')
 if r['availability']!='available' or any(z in t.lower() for z in ['just a moment','checking your browser','access denied']): get('https://r.jina.ai/'+base,'jina_home')
 def score(u):
  s=u.lower(); return 10*bool(re.search(r'\.pdf(?:\?|$)',s))+8*bool(re.search('material|capabilit|manufactur|process|product|rubber|resin|polymer|urethane|composite|about',s))-15*bool(re.search('privacy|contact|cart|login|news|blog|author|tag/',s))
 while len(out)<6:
  choices=[u for u in links if u not in seen and score(u)>0]
  if choices:
   u=sorted(choices,key=lambda u:(-score(u),len(u)))[0]; get(u,'pdf' if '.pdf' in u.lower() else 'product_or_capability'); continue
  maps=[u for u in links if u not in seen and ('sitemap' in u or u.endswith('.xml'))]
  if maps: get(maps[0],'sitemap_child'); continue
  # Conventional product and alternative sitemap routes are attempts, never evidence if absent.
  defaults=[urljoin(root,p) for p in ['products/','wp-sitemap.xml','capabilities/','about-us/']]
  u=next((u for u in defaults if u not in seen),None)
  if u: get(u,'product_probe' if 'sitemap' not in u else 'sitemap_probe')
  else: break
 with (D/'raw'/oid/'routes.json').open('w') as f: json.dump(out,f,indent=2)
 print(oid,len(out),flush=True)
 return out
if __name__=='__main__':
 if sys.argv[1]=='calibrate':
  for oid,url in [('CAL-novex','https://novexinc.com/'),('CAL-mipco','https://mipco.org/'),('CAL-tuftex','https://tuftexballoons.com/')]:
   r,t,h=fetch(oid,url,'calibration'); (D/'raw'/oid/'routes.json').write_text(json.dumps([r],indent=2)); print(oid,r['http_status'],t[:200])
 else:
  rows=list(csv.DictReader((D/'frame.csv').open())); assert len(rows)==len({r['org_id'] for r in rows})==68
  start,end=map(int,sys.argv[1:3])
  with ThreadPoolExecutor(max_workers=8) as ex: list(ex.map(collect,rows[start:end]))
