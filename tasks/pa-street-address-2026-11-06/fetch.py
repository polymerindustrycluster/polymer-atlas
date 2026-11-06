"""Raw-check PA operator pages; only complete physical street/city/state/ZIP blocks become candidates."""
import concurrent.futures,csv,hashlib,json,re,subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlparse
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[1]
def read(p):return list(csv.DictReader(open(p)))
def write(p,rows):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
class Page(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.links=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
  if t=='a':self.links.extend(v for k,v in a if k=='href' and re.search('contact|location',v,re.I))
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,s):
  if not self.skip and s.strip():self.parts.append(s.strip())
def fetch(u):
 r=subprocess.run(['curl','--fail','-L','--max-time','25','-A','Mozilla/5.0',u],capture_output=True)
 if r.returncode:raise ValueError('transport '+str(r.returncode))
 p=Page();p.feed(r.stdout.decode(errors='replace'));return ' '.join(p.parts),p.links,hashlib.sha256(r.stdout).hexdigest()
def extract(text,city):
 suffix=r'(?:Street|St\.?|Road|Rd\.?|Drive|Dr\.?|Avenue|Ave\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Parkway|Pkwy\.?|Place|Pl\.?|Way|Court|Ct\.?|Route\s+\d+)'
 pattern=r'\b(\d{1,6}\s+(?:(?!\d+\b)[A-Za-z0-9.#/-]+\s+){0,8}?'+suffix+r')[, •|]*\s*'+re.escape(city)+r'\s*[, •|]*\s*(?:PA|Pennsylvania)\s*[, •|]*\s*(\d{5}(?:-\d{4})?)\b'
 text=' '.join(text.split())
 return [(m[1].strip(),m[2],m[0]) for m in re.finditer(pattern,text,re.I)]
def known():
 cases=[('2935 W 17th St, Erie, PA 16505','Erie','2935 W 17th St','16505'),('7 Headley Pl, Fallsington PA 19054','Fallsington','7 Headley Pl','19054'),('21 Lebanon Parkway, Lebanon, PA 17042','Lebanon','21 Lebanon Parkway','17042')]
 for text,city,street,zip_ in cases:
  assert extract(text,city)==[(street,zip_,text)]
  assert not extract(text,'WRONG CITY') and not extract('PO Box 123, '+city+', PA '+zip_,city)
 assert extract('Phone 2166 1 Lark Ave., Leola, PA 17540','Leola')==[('1 Lark Ave.','17540','1 Lark Ave., Leola, PA 17540')]
 assert extract('2970 Molding Division Main Office 1040 Maple Avenue Lake City, PA 16423','Lake City')==[('1040 Maple Avenue','16423','1040 Maple Avenue Lake City, PA 16423')]
 print('PASS: 3 known address blocks; injected wrong-city and PO-box cases rejected')
def main():
 known();sites=read(TASK/'baseline_blank.csv');orgs={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
 def work(s):
  base=orgs[s['org_id']]['website']
  if not base and s['site_id'] in ('SITE-002834','SITE-002838'):base=re.search(r'https?://[^; ]+',s['sources'])[0]
  base=base if '://' in base or not base else 'https://'+base
  # Sources already on the site can supply an own-domain URL when corporate website is blank.
  todo=[base] if base else [];seen=[];out=[]
  for _ in range(4):
   if not todo:break
   u=todo.pop(0)
   if u in seen:continue
   seen.append(u)
   try:
    text,links,sha=fetch(u)
    for street,zip_,quote in extract(text,s['city']):
     out.append(dict(site_id=s['site_id'],street_address=street,source_zip=zip_,quote=quote,url=u,sha256=sha,checked_urls=';'.join(seen)))
    todo.extend(v for v in (urljoin(u,x) for x in links) if urlparse(v).hostname==urlparse(base).hostname and v not in seen and v not in todo)
   except Exception:pass
  return out or [dict(site_id=s['site_id'],street_address='',source_zip='',quote='',url=base,sha256='',checked_urls=';'.join(seen))]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:out=[r for group in pool.map(work,sites) for r in group]
 write(TASK/'rawchecks.csv',out);print('rawcheck rows',len(out),'sites with address',len({r['site_id'] for r in out if r['street_address']}))
if __name__=='__main__':main()
