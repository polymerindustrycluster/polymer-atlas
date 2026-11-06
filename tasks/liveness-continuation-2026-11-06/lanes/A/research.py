"""Bounded curl collection and house normalized-word check; verdicts manually authored."""
import csv,html,re,subprocess,sys,unicodedata
from pathlib import Path
from html.parser import HTMLParser
HERE=Path(__file__).resolve().parent
CACHE=Path('/tmp/atlas-L8-cont-A'); CACHE.mkdir(exist_ok=True)
W=lambda s: re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKD',html.unescape(s or '')).encode('ascii','ignore').decode().lower())
def found(text,quote):
    p,q=W(text),W(quote)
    return bool(q) and any(p[i:i+len(q)]==q for i in range(len(p)-len(q)+1))
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.hide=0
    def handle_starttag(self,t,a):
        if t in ('script','style'): self.hide+=1
    def handle_endtag(self,t):
        if t in ('script','style'): self.hide=max(0,self.hide-1)
    def handle_data(self,d):
        if not self.hide and d.strip(): self.parts.append(d.strip())
def fetch(org,url,route='curl-browser-UA'):
    if not url.startswith('http'): url='https://'+url
    logs=list(csv.DictReader(open(HERE/'fetch_log.csv'))) if (HERE/'fetch_log.csv').exists() else []
    n=sum(r['org_id']==org for r in logs)+1
    assert n<=6,org+' fetch cap'
    path=CACHE/f'{org}-{n}.html'
    target='https://r.jina.ai/'+url if route=='jina' else url
    p=subprocess.run(['curl','--compressed','-L','--max-time','22','--connect-timeout','8','-A','Mozilla/5.0','-sS','-o',str(path),'-w','%{http_code}\t%{url_effective}',target],capture_output=True,text=True)
    code,_,final=p.stdout.partition('\t')
    body=path.read_text(errors='replace') if path.exists() else ''
    t=Text(); t.feed(body); clean='\n'.join(t.parts) if '<html' in body.lower() or '<!doctype' in body.lower() else body
    path.with_suffix('.txt').write_text(clean)
    row=dict(org_id=org,url=url,http=code,route=route,error=p.stderr.strip(),observed_date='2026-11-06',final_url=final,raw_cache_path=str(path))
    with open(HERE/'fetch_log.csv','a',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=row);
        if not logs: wr.writeheader()
        wr.writerow(row)
    print(org,n,code,final,str(path),'\n'+clean[:12500]+'\n')
if __name__=='__main__':
    if sys.argv[1]=='fetch': fetch(*sys.argv[2:])
    elif sys.argv[1]=='ranks':
        for r in csv.DictReader(open(HERE/'input.csv')):
            if int(sys.argv[2])<=int(r['rank'])<=int(sys.argv[3]): fetch(r['org_id'],r['current_website'] or r['final_url'] or r['domain'])
