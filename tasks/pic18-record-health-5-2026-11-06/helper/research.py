#!/usr/bin/env python3
"""Bounded own-primary collection. Quotes are reviewed before packet admission."""
import csv,json,re,subprocess,sys,hashlib,unicodedata
from pathlib import Path
from urllib.parse import urljoin,urlparse,quote
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from raw import Text
D=Path(__file__).resolve().parent
W=lambda s:re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower())
def has(t,p):
 t,p=W(t),W(p);return bool(p) and any(t[i:i+len(p)]==p for i in range(len(t)-len(p)+1))
def fetch(oid,url,kind):
 folder=D/'raw'/oid;folder.mkdir(parents=True,exist_ok=True);key=hashlib.sha256(url.encode()).hexdigest()[:12];body=folder/(key+'.body');txt=folder/(key+'.txt')
 p=subprocess.run(['curl','-L','--max-time','20','--connect-timeout','8','-A','Mozilla/5.0','-sS','-w','%{http_code}\t%{url_effective}',url,'-o',str(body)],capture_output=True,text=True)
 parts=p.stdout.split('\t',1);status=parts[0];final=parts[-1];b=body.read_bytes() if body.exists() else b'';err=p.stderr.strip();raw=''
 if b.startswith(b'%PDF'):
  x=subprocess.run(['pdftotext','-layout',str(body),str(txt)],capture_output=True,text=True);t=txt.read_text(errors='replace') if txt.exists() else '';err+=' '+x.stderr.strip()
 else:
  raw=b.decode(errors='replace');x=Text();x.feed(raw);t=' '.join(' '.join(x.parts).split())
 t=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','[contact redacted]',t)
 t=re.sub(r'(?<![\w])(?:\+?1[ .-]?)?\(?[2-9]\d{2}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)','[phone redacted]',t)
 txt.write_text(t)
 if body.exists():body.unlink()
 rr=dict(org_id=oid,kind=kind,source_ref=url,final_url=final,http_status=status,availability=('available' if status.startswith('2') and len(t)>100 and not any(z in t.lower() for z in ['just a moment','verify you are human','access denied']) else 'failed_or_sparse'),raw_path=str(txt.relative_to(D)),notes=err)
 return rr,t,raw
OVERRIDE={'ORG-001452':'https://dlhbowles.com/','ORG-001726':'https://www.enduraplastics.com/','ORG-003885':'https://www.radicigroup.com/en/contacts/contacts-hpp/worldwide-hpp/','ORG-001721':'https://www.truco-inc.com/','ORG-001921':'https://www.pottersbeads.com/'}
def collect(row):
 oid=row['org_id'];base=OVERRIDE.get(oid,row['website']); rr=[];links=[];seen=set()
 if not base or base=='none_found' or 'not this' in base:
  (D/'raw'/oid).mkdir(parents=True,exist_ok=True);(D/'raw'/oid/'routes.json').write_text('[]');return
 base=base.split(' (')[0];base=base if '://' in base else 'https://'+base;root=urljoin(base,'/')
 def get(u,k):
  seen.add(u);r,t,h=fetch(oid,u,k);rr.append(r)
  for a in re.findall(r'href=["\']([^"\']+)',h,re.I):
   u=urljoin(r['final_url'] if r['final_url'].startswith('http') else base,a).split('#')[0]
   if (urlparse(u).hostname or '').removeprefix('www.')==(urlparse(r['final_url']).hostname or '').removeprefix('www.') and u not in links and not re.search(r'wp-json|oembed|\.css|\.js|facebook|linkedin|mailto:|tel:',u):links.append(u)
  return r
 r=get(base,'own_home')
 if r['availability']!='available':get('https://r.jina.ai/'+base,'jina_home')
 for regex,default,kind in [(r'contact|location', 'contact-us/','own_address'),(r'about|company','about-us/','own_identity'),(r'capabilit|manufactur|process|product|rubber|polymer|\.pdf','products/','own_scope')]:
  choices=[u for u in links if u not in seen and re.search(regex,u,re.I) and not re.search('privacy|terms|career|news|blog',u,re.I)]
  u=min(choices,key=len) if choices else urljoin(root,default);get(u,kind)
 (D/'raw'/oid/'routes.json').write_text(json.dumps(rr,indent=2));print(oid,len(rr),flush=True)
if __name__=='__main__':
 rows=list(csv.DictReader((D/'frame.csv').open()));start,end=map(int,sys.argv[1:3])
 with ThreadPoolExecutor(max_workers=8) as ex:list(ex.map(collect,rows[start:end]))
