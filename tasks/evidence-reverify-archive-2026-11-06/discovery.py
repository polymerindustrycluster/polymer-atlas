#!/usr/bin/env python3
"""Resumable CDX/SPN worker. Outputs stay in build/ until a reviewed top-up."""
import hashlib
import json
import re
import subprocess
import time
import urllib.parse
from run import CACHE, HERE, ROOT, read, write, fetch, on_page
from archive import FIELDS, same_page

END = time.monotonic() + 11 * 3600
LAST = {}


def request(url, bucket, interval):
    delay = 60
    while time.monotonic() < END:
        time.sleep(max(0, LAST.get(bucket, 0) + interval - time.monotonic()))
        header = CACHE/'discovery-headers.txt'
        p = subprocess.run(['curl','-sS','-L','-A','Mozilla/5.0 (Atlas evidence archive audit)','--max-time','45','-D',str(header),'-w','\n%{http_code}',url],capture_output=True,text=True)
        LAST[bucket] = time.monotonic()
        body, _, code = p.stdout.rpartition('\n')
        if code != '429': return body,code,header.read_text() if header.exists() else ''
        h = header.read_text() if header.exists() else ''
        retry = re.findall(r'(?im)^retry-after:\s*(\d+)',h)
        wait = max(delay,int(retry[-1]) if retry else 0)
        print('429',bucket,'backoff',wait,flush=True)
        time.sleep(min(wait,max(0,END-time.monotonic()))); delay = min(delay*2,1800)
    raise TimeoutError('11-hour worker window exhausted; resume from cache')


def cdx(url):
    query=urllib.parse.urlencode(dict(url=url,output='json',limit='-5',filter='statuscode:200'))
    body,code,_=request('https://web.archive.org/cdx/search/cdx?'+query,'cdx',5)
    if code != '200': return [],'CDX_FETCH_FAILED_'+code
    try:
        rows=json.loads(body)
        if not rows:return [],'NO_CAPTURE'
        header,*data=rows
        rows=[dict(zip(header,r)) for r in data]
        refs=['https://web.archive.org/web/'+r['timestamp']+'/'+r['original'] for r in rows if re.fullmatch(r'\d{14}',r.get('timestamp','')) and same_page(r.get('original',''),url)]
        return list(reversed(refs)),'FOUND' if refs else 'NO_EXACT_CAPTURE'
    except (ValueError,TypeError,KeyError):return [],'CDX_INVALID_RESPONSE'


def main():
    grouped={}
    for e in read(HERE/'verdicts.csv'):
        if e['judgment']=='SUPPORTED':grouped.setdefault(e['url'],[]).append(e)
    supported_ids = {e['evidence_id'] for rows in grouped.values() for e in rows}
    results=ROOT/'build/l1-discovery';results.mkdir(exist_ok=True)
    all_links=[r for p in results.glob('*.json') for r in json.loads(p.read_text())['links'] if r['evidence_id'] in supported_ids]
    write(ROOT/'build/l1-cdx-links.csv',sorted(all_links,key=lambda x:x['evidence_id']),FIELDS)
    for i,(url,rows) in enumerate(sorted(grouped.items()),1):
        if time.monotonic() >= END: break
        path=results/(hashlib.sha256(url.encode()).hexdigest()+'.json')
        if path.exists():continue
        refs,status=cdx(url)
        if status in ('NO_CAPTURE','NO_EXACT_CAPTURE') and urllib.parse.urlsplit(url).query:
            # shortcut: query-string SPN targets held until an encoded submit route is verified.
            status = 'SPN_QUERY_HOLD'
        elif status in ('NO_CAPTURE','NO_EXACT_CAPTURE'):
            _,code,_=request('https://web.archive.org/save/'+url,'spn',20)
            if code in ('200','201','202','302'):
                time.sleep(20); refs,status=cdx(url)
            else:status='SPN_FETCH_FAILED_'+code
        links=[]
        for ref in refs:
            if len(links)==len(rows):break
            # Back off on replay 429 independently of CDX/SPN; retry only after the wait.
            replay_delay = 60
            f = None
            while time.monotonic()<END:
                time.sleep(2)
                f=fetch(ref,refresh=True,fallback=False)
                if f['attempts'][-1]['status']!='429':break
                print('429 replay backoff',replay_delay,flush=True);time.sleep(max(replay_delay,f['attempts'][-1].get('retry_after',0)));replay_delay=min(replay_delay*2,1800)
            if f is None: raise TimeoutError('Worker window exhausted during replay; resume this URL')
            if f['status']!='ok' or f['attempts'][-1]['effective_url'].rstrip('/')!=ref.rstrip('/'):continue
            for e in rows:
                if any(x['evidence_id']==e['evidence_id'] for x in links):continue
                if on_page(e['quote'],ROOT/f['page']):
                    stamp=re.search(r'/web/(\d{14})/',ref)[1]
                    links.append(dict(evidence_id=e['evidence_id'],archive_ref=ref,captured_at=stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:8],created_by='atlas-L1-reverify-archive'))
        path.write_text(json.dumps(dict(url=url,status=status,links=links)))
        all_links=[r for p in results.glob('*.json') for r in json.loads(p.read_text())['links'] if r['evidence_id'] in supported_ids]
        write(ROOT/'build/l1-cdx-links.csv',sorted(all_links,key=lambda x:x['evidence_id']),FIELDS)
        print(i,'/',len(grouped),'CDX',status,'links',len(all_links),flush=True)


if __name__=='__main__':main()
