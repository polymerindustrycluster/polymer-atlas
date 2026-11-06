import sys
sys.dont_write_bytecode=True
import csv,pathlib,subprocess,hashlib,json,re,concurrent.futures
from html.parser import HTMLParser
BASE=pathlib.Path(__file__).parent
CACHE=pathlib.Path('/tmp/residual-hq3-a');CACHE.mkdir(exist_ok=True)
class Text(HTMLParser):
 def __init__(self):super().__init__();self.out=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip:self.out.append(d)
def visible(raw):
 p=Text();p.feed(raw);return ' '.join(' '.join(p.out).split())
def fetch(job):
 oid,url=job;key=oid+'_'+hashlib.sha256(url.encode()).hexdigest()[:10];p=CACHE/(key+'.raw')
 assert not p.exists(),('duplicate fetch',oid,url)
 existing=[x for x in CACHE.glob(oid+'_*.json')]
 assert len(existing)<5,('cap',oid)
 result=subprocess.run(['curl','-L','--max-time','20','--compressed','-A','Mozilla/5.0','-sS',url],capture_output=True)
 p.write_bytes(result.stdout)
 if result.stdout.startswith(b'%PDF'):
  txt=subprocess.check_output(['pdftotext','-raw',str(p),'-']).decode()
 else:txt=visible(result.stdout.decode('utf-8','replace'))
 p.with_suffix('.txt').write_text(txt)
 rc=dict(org_id=oid,url=url,raw_sha256=hashlib.sha256(result.stdout).hexdigest(),path=str(p),error=result.stderr.decode()[:100])
 p.with_suffix('.json').write_text(json.dumps(rc));return rc,txt
def batch(jobs):
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
  for rc,txt in ex.map(fetch,jobs):
   print(rc['org_id'],rc['url'],len(txt),[txt[max(0,m.start()-100):m.end()+250] for m in re.finditer(r'(?i)headquarter|corporate office',txt)][:8],flush=True)
if __name__=='__main__':
 rows=list(csv.DictReader((BASE/'input.csv').open()));batch([(r['org_id'],r['website']) for r in rows if r['website'] and r['status']=='active'])
