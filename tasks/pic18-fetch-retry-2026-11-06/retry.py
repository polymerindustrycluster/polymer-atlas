"""Packet-only retry; reuse the calibrated L1 quote/parser/identity code unchanged."""
import argparse,csv,hashlib,importlib.util,json,os,re,subprocess,sys,threading,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
spec=importlib.util.spec_from_file_location('l1audit',ROOT/'tasks/evidence-reverify-archive-2026-11-06/run.py');l1=importlib.util.module_from_spec(spec);spec.loader.exec_module(l1)
sys.modules.setdefault('run',l1)
spec=importlib.util.spec_from_file_location('l1archive',ROOT/'tasks/evidence-reverify-archive-2026-11-06/archive.py');archive=importlib.util.module_from_spec(spec);spec.loader.exec_module(archive)
CACHE=ROOT/'build/pic18-fetch-retry-cache';CACHE.mkdir(parents=True,exist_ok=True)
# Keep all original audit files and its cache read-only.
l1.CACHE=CACHE
read=l1.read;on_page=l1.on_page;quote=l1.quote;same_page=archive.same_page
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
locks={};rate_limited=set()
def write(path,rows):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
def target(ref):
    # Only extract an explicit URL already present in the citation, never discover a replacement.
    m=re.search(r'https?://[^\s;]+',ref)
    return m[0] if m else ''
def key(url,route):return hashlib.sha256((route+'|'+url).encode()).hexdigest()
def assess(url,route,raw_path,receipt,source_url=None):
    result={**receipt,'url':url,'route':route,'raw_path':str(raw_path.relative_to(ROOT)),'raw_sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest(),'text_path':'','text_sha256':'','format':'','posture':'FETCH_FAILED','reason':'Route did not return a readable successful source.'}
    if receipt['http_status']!=200 or receipt.get('exit_code',0)!=0:return result
    raw=raw_path.read_bytes();text_path=raw_path.with_suffix('.txt')
    try:
        if raw.lstrip().startswith(b'%PDF'):
            p=subprocess.run(['pdftotext','-layout',str(raw_path),str(text_path)],capture_output=True)
            if p.returncode!=0:result['reason']='PDF extraction failed';return result
            text=text_path.read_text(encoding='utf-8');result['format']='pdf'
        else:
            charset=receipt.get('charset') or 'utf-8';body=raw.decode(charset,errors='strict')
            if route=='jina':
                error=re.search(r'(?im)^Warning: Target URL returned error (\d+)',body)
                if error:
                    result['reason']='Jina reports upstream HTTP '+error[1];result['upstream_status']=int(error[1]);return result
                m=re.search(r'(?m)^URL Source:\s*(https?://\S+)',body);source_url=m[1] if m else ''
                text=body.split('Markdown Content:',1)[1] if 'Markdown Content:' in body else ''
                result['format']='jina_raw_text'
            elif route=='firecrawl_pdf_text':text=body;result['format']='nas_pdf_text'
            else:
                parser=l1.Text();parser.feed(body);text=' '.join(parser.parts);result['format']='html_text_nodes'
            text_path.write_text(text,encoding='utf-8')
    except (UnicodeError,LookupError,ValueError) as e:
        result['reason']='Decode/parser hold: '+type(e).__name__;return result
    result['effective_source_url']=source_url or receipt.get('effective_url','')
    result['text_path']=str(text_path.relative_to(ROOT));result['text_sha256']=hashlib.sha256(text_path.read_bytes()).hexdigest()
    low=text.lower()
    wall=any(s in low for s in ('just a moment...', 'verify you are human', 'attention required! | cloudflare','this site can’t be reached','checking your browser','complete the captcha','captcha challenge','access denied','accessdenied','you have been blocked'))
    if len(l1.ns['words'](text))<15 or wall:
        result['reason']='Empty/short document or recognized challenge wall';return result
    # Reuse L1's decoding/challenge and strict host/path/query posture, presenting the unwrapped source identity.
    f=dict(status='ok',page=result['text_path'],attempts=[dict(route=url,effective_url=result['effective_source_url'])])
    result['posture']=l1.live_posture(f,url)
    result['reason']='Readable exact cited source' if result['posture']=='ok' else 'Source identity/decoding/challenge hold'
    return result
def fetch(url,route,refresh=False):
    stem=CACHE/key(url,route);meta=stem.with_suffix('.json');raw=stem.with_suffix('.raw');headers=stem.with_suffix('.headers')
    if meta.exists() and not refresh:return json.loads(meta.read_text())
    endpoint=('https://'+url[7:] if route=='curl_https' else url) if route in {'curl','curl_https'} else 'https://r.jina.ai/'+url
    host=urlsplit(endpoint).hostname or '';lock=locks.setdefault(host,threading.Lock())
    with lock:
        if host in rate_limited:
            result=dict(url=url,route=route,http_status=429,posture='FETCH_FAILED',reason='Host stopped after429; no additional request',request_performed=False,fetched_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),text_path='',text_sha256='')
            meta.write_text(json.dumps(result,indent=2)+'\n');return result
        p=subprocess.run(['curl','-L','-sS','--compressed','-A',UA,'--max-time','25','--max-filesize','16000000','-D',str(headers),'-o',str(raw),'-w','%{http_code}\n%{url_effective}',endpoint],capture_output=True,text=True)
        code,_,effective=p.stdout.partition('\n');status=int(code) if code.isdigit() else 0
        if status==429:rate_limited.add(host)
    if not raw.exists():raw.write_bytes(b'')
    hs=headers.read_text(errors='replace') if headers.exists() else '';cs=re.findall(r'(?im)^content-type:[^\n]*charset=["\x27]?([^;\s"\x27]+)',hs)
    receipt=dict(request_performed=True,http_status=status,effective_url=effective,exit_code=p.returncode,charset=cs[-1] if cs else '',fetched_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),error=p.stderr.strip()[:300])
    result=assess(url,route,raw,receipt);meta.write_text(json.dumps(result,indent=2)+'\n');return result
def needs_more(url,rows):
    results=[json.loads(p.read_text()) for p in CACHE.glob('*.json') if p.name in {key(url,r)+'.json' for r in ['curl','curl_https','jina','firecrawl','firecrawl_pdf_text']}]
    readable=[r for r in results if r['posture']=='ok']
    return not readable or any(e['quote'] and not any(on_page(e['quote'],ROOT/r['text_path']) is True for r in readable) for e in rows)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--route',choices=['curl','curl_https','jina'],required=True);ap.add_argument('--refresh',action='store_true');a=ap.parse_args()
    rows=read(P/'input.csv');groups={target(r['url']):[] for r in rows if target(r['url'])}
    for r in rows:
        if target(r['url']):groups[target(r['url'])].append(r)
    urls=sorted(u for u,rs in groups.items() if a.route=='curl' or ((a.route!='curl_https' or u.startswith('http://')) and needs_more(u,rs)))
    print('Retry',a.route,len(urls),'explicit URLs',flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,r in enumerate(pool.map(lambda u:fetch(u,a.route,a.refresh),urls),1):print(i,'/',len(urls),r['posture'],r['url'],flush=True)
if __name__=='__main__':main()
