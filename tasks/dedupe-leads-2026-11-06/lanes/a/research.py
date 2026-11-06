import sys
sys.dont_write_bytecode=True
import pathlib,subprocess,json,hashlib,re,concurrent.futures
from html.parser import HTMLParser
BASE=pathlib.Path(__file__).parent; CACHE=pathlib.Path('/tmp/dedupe-leads-a');CACHE.mkdir(exist_ok=True)
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
 pair,url,orgs=job; key=pair+'_'+hashlib.sha256(url.encode()).hexdigest()[:10];p=CACHE/(key+'.raw')
 assert not p.exists()
 receipts=[json.loads(x.read_text()) for x in CACHE.glob('*.json')]
 for org in orgs:assert sum(org in x['org_ids'] for x in receipts)<5,org
 result=subprocess.run(['curl','-L','--max-time','25','--compressed','-A','Mozilla/5.0','-sS',url],capture_output=True);p.write_bytes(result.stdout)
 txt=subprocess.check_output(['pdftotext','-raw',str(p),'-']).decode() if result.stdout.startswith(b'%PDF') else visible(result.stdout.decode('utf-8','replace'))
 p.with_suffix('.txt').write_text(txt)
 rc=dict(pair_id=pair,org_ids=orgs,url=url,raw_sha256=hashlib.sha256(result.stdout).hexdigest(),path=str(p),error=result.stderr.decode()[:100]);p.with_suffix('.json').write_text(json.dumps(rc));return rc,txt
def batch(jobs):
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
  for rc,txt in ex.map(fetch,jobs):print(rc['pair_id'],rc['url'],len(txt),[txt[max(0,m.start()-80):m.end()+200] for m in re.finditer('(?i)subsidiar|wholly owned|acquir|iten|TDM|Lauren|Westlake Royal|Roppe Holding',txt)][:9],flush=True)
