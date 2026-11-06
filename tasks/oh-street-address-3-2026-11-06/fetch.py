"""Raw-check held PIC-18 Ohio operator pages; only complete physical street/city/state/ZIP blocks become candidates."""
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
 r=subprocess.run(['curl','--fail','-L','--max-time','25','-A','Mozilla/5.0','-w','\\n__ATLAS_URL__%{url_effective}',u],capture_output=True)
 if r.returncode:raise ValueError('HTTP/transport failure '+str(r.returncode))
 raw,final=r.stdout.rsplit(b'\n__ATLAS_URL__',1)
 host=lambda v:(urlparse(v).hostname or '').lower().removeprefix('www.')
 if host(final.decode())!=host(u):raise ValueError('redirect leaves held operator host')
 p=Page();p.feed(raw.decode(errors='replace'));return ' '.join(p.parts),p.links,hashlib.sha256(raw).hexdigest()
def extract(text,city):
 suffix=r'(?:Street|St\.?|Road|Rd\.?|Drive|Dr\.?|Avenue|Ave\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Parkway|Pkwy\.?|Place|Pl\.?|Way|Court|Ct\.?|Route\s+\d+)'
 pattern=r'\b(\d{1,6}\s+(?:(?!\d+\b)[A-Za-z0-9.#/-]+\s+){0,8}?'+suffix+r')[, •|]*\s*'+re.escape(city)+r'\s*[, •|]*\s*(?:OH|Ohio)\s*[, •|]*\s*(\d{5}(?:-\d{4})?)\b'
 text=' '.join(text.split())
 return [(m[1].strip(),m[2],m[0]) for m in re.finditer(pattern,text,re.I)]
def known():
 cases=[('373 Washington St. Chardon OH 44024','Chardon','373 Washington St.','44024'),
        ('1101 Moore Road, Avon, Ohio 44011','Avon','1101 Moore Road','44011'),
        ('1150 Damar Drive Akron, Ohio 44305-1201','Akron','1150 Damar Drive','44305-1201')]
 for text,city,street,zip_ in cases:
  assert extract(text,city)==[(street,zip_,text)]
  assert not extract(text,'WRONG CITY') and not extract('PO Box 123, '+city+', OH '+zip_,city)
 assert extract('Phone 2166 1 Lark Ave., Leola, OH 17540','Leola')==[('1 Lark Ave.','17540','1 Lark Ave., Leola, OH 17540')]
 assert extract('2970 Molding Division Main Office 1040 Maple Avenue Lake City, OH 16423','Lake City')==[('1040 Maple Avenue','16423','1040 Maple Avenue Lake City, OH 16423')]
 urls=['https://chardoncp.com/','https://www.freemansupply.com/','https://www.shinetsusilicones.com/']
 out=[]
 for (quote,city,street,zip_),url in zip(cases,urls):
  text,links,sha=fetch(url)
  assert any(r[0]==street and r[1]==zip_ for r in extract(text,city)),(url,extract(text,city))
  out.append(dict(url=url,city=city,expected_street=street,expected_zip=zip_,sha256=sha,result='PASS'))
 write(TASK/'known_answers.csv',out)
 print('PASS: three live literal address answers; wrong-city/PO-box/phone-prefix mutations')
def main():
 sites=[r for r in read(TASK/'frame.csv') if r['selected']=='yes']
 groups={}
 for r in sites:groups.setdefault(r['org_id'],[]).append(r)
 def work(item):
  oid,rows=item;base=rows[0]['website'];base=base if '://' in base else 'https://'+base
  todo=[base];seen=[];out=[];pages=[]
  # Existing own-host URLs are source leads, never evidence until fetched.
  for r in rows:
   for u in re.findall(r'https?://[^; <>]+',r['sources']):
    if (urlparse(u).hostname or '').removeprefix('www.')==(urlparse(base).hostname or '').removeprefix('www.') and u not in todo:todo.append(u)
  while todo and len(seen)<5:
   u=todo.pop(0).split('#')[0]
   if u in seen:continue
   seen.append(u)
   try:
    text,links,sha=fetch(u);found=0
    for r in rows:
     for street,zip_,quote in extract(text,r['city']):
      pos=' '.join(text.split()).find(quote);context=' '.join(text.split())[max(0,pos-80):pos+len(quote)]
      posture='mailing-only context' if re.search(r'(?i)mailing\s+address|postal\s+address',context) else ''
      out.append(dict(site_id=r['site_id'],street_address=street,source_zip=zip_,quote=quote,url=u,sha256=sha,posture=posture));found+=1
    pages.append(dict(org_id=oid,url=u,outcome='fetched',address_blocks=found,error=''))
    links=sorted(links,key=lambda x:('location' not in x.lower(),len(x)))
    for link in links:
     v=urljoin(u,link).split('#')[0]
     if (urlparse(v).hostname or '').removeprefix('www.')==(urlparse(base).hostname or '').removeprefix('www.') and v not in seen and v not in todo:todo.append(v)
   except Exception as ex:pages.append(dict(org_id=oid,url=u,outcome='unavailable',address_blocks=0,error=str(ex)))
  for r in rows:
   if not any(o['site_id']==r['site_id'] for o in out):out.append(dict(site_id=r['site_id'],street_address='',source_zip='',quote='',url=base,sha256='',posture='need physical street at recorded city; no raw address block found'))
  return out,pages
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(work,groups.items()))
 out=[r for rows,pages in results for r in rows];pages=[r for rows,log in results for r in log]
 assert {r['site_id'] for r in out}=={r['site_id'] for r in sites}
 write(TASK/'rawchecks.csv',out);write(TASK/'page_checks.csv',pages)
 print('selected sites',len(sites),'rawcheck sites',len({r['site_id'] for r in out}),'sites with address',len({r['site_id'] for r in out if r['street_address']}),'pages',len(pages),flush=True)
if __name__=='__main__':
 if '--known' in __import__('sys').argv:known()
 else:main()
