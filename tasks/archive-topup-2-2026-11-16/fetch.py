"""Resumable slice worker; one durable result per URL, bounded by a persisted deadline."""
import time, shutil, fcntl
from common import *

def main():
    state=PROOFS/'state.json'
    if not state.exists():state.write_text(json.dumps(dict(started=time.time(),deadline=time.time()+3*3600)))
    deadline=json.loads(state.read_text())['deadline']
    discovery.END=time.monotonic()+max(0,deadline-time.time())
    # New captures are paced per worker; discovery retries back off on HTTP 429.
    def request(url,bucket,interval):return original_request(url,'all',5 if bucket=='spn' else 0)
    original_request=discovery.request
    discovery.request=request
    discovery.LAST['all']=time.monotonic()
    grouped={}
    for r in house.read(Path(__import__('os').environ.get('ARCHIVE_TOPUP_INPUTS',str(HERE/'inputs.csv')))):grouped.setdefault(r['url'],[]).append(r)
    worker=int(os.environ.get('ARCHIVE_WORKER','0'))
    workers=int(os.environ.get('ARCHIVE_WORKERS','1'))
    for position,(url,rows) in enumerate(grouped.items()):
        if position%workers!=worker:continue
        result=PROOFS/(sha(url.encode())+'.json')
        if result.exists():continue
        if time.time()>=deadline:break
        assert valid_url(url),url
        try:
            body,code,_=discovery.request('https://archive.org/wayback/available?'+__import__('urllib.parse',fromlist=['urlencode']).urlencode({'url':url}),'availability',6)
            try:
                capture=json.loads(body).get('archived_snapshots',{}).get('closest',{}) if code=='200' else {}
                ref=capture.get('url','').replace('http://web.archive.org/','https://web.archive.org/')
                match=re.fullmatch(r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)',ref)
                refs=[ref] if capture.get('available') and capture.get('status')=='200' and match and same_page(match[2],url) else []
                status='FOUND' if refs else 'NO_CAPTURE' if code=='200' else 'AVAILABILITY_FAILED_'+code
            except (ValueError,TypeError):refs=[];status='AVAILABILITY_INVALID_RESPONSE'
            attempts=[];links=[];checks=[]
            def replay(ref):
                if time.time()>=deadline:raise TimeoutError('authorized window exhausted')
                time.sleep(max(0,discovery.LAST.get('all',0)-time.monotonic()))
                f=house.fetch(ref,refresh=True,fallback=False)
                discovery.LAST['all']=time.monotonic()
                a=f['attempts'][-1]
                if a['status']=='429':
                    time.sleep(min(max(60,a.get('retry_after',0)),max(0,deadline-time.time())))
                proof=PROOFS/(sha(ref.encode())+'.txt')
                if f['status']=='ok':shutil.copyfile(ROOT/f['page'],proof)
                checks.append(dict(archive_ref=ref,status=f['status'],http=a['status'],effective_url=a['effective_url'],checked_at=f['fetched_at'],page_sha256=sha(proof.read_bytes()) if f['status']=='ok' else ''))
                if f['status']!='ok':attempts.append('FETCH_FAILED_'+a['status']);return
                if not same_capture(a['effective_url'],ref):attempts.append('REPLAY_REDIRECT_HOLD');return
                for e in rows:
                    if e['quote'] and house.on_page(e['quote'],proof) and not any(x['evidence_id']==e['evidence_id'] for x in links):
                        stamp=re.search(r'/web/(\d{14})/',ref)[1]
                        links.append(dict(evidence_id=e['evidence_id'],archive_ref=ref,captured_at=f'{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}',created_by='atlas-w16-archive'))
                attempts.append('READABLE')
            for ref in refs:
                replay(ref)
                if links:break
            if not links:
                # Existing discovery method holds query-string SPN routes until encoding is verified.
                if __import__('urllib.parse',fromlist=['urlsplit']).urlsplit(url).query:status='SPN_QUERY_HOLD'
                else:
                    _,code,_=discovery.request('https://web.archive.org/save/'+url,'spn',20)
                    status='SPN_FETCH_FAILED_'+code
                    if code in ('200','201','202','302'):
                        time.sleep(min(20,max(0,deadline-time.time())))
                        fresh,status=discovery.cdx(url)
                        for ref in fresh:
                            replay(ref)
                            if links:break
            outcomes=[dict(evidence_id=e['evidence_id'],status='VERIFIED' if any(x['evidence_id']==e['evidence_id'] for x in links) else 'NO_PRESERVED_QUOTE' if not e['quote'] else 'QUOTE_ABSENT' if 'READABLE' in attempts else status if not attempts else attempts[-1]) for e in rows]
            payload=dict(url=url,links=links,checks=checks,outcomes=outcomes,status=status,finished=time.time())
        except TimeoutError:raise
        except Exception as exc:
            payload=dict(url=url,links=[],checks=[],outcomes=[dict(evidence_id=e['evidence_id'],status='ITEM_ERROR_'+type(exc).__name__) for e in rows],status='ITEM_ERROR_'+type(exc).__name__,error=str(exc)[:300],finished=time.time())
        links=payload['links'];status=payload['status']
        tmp=result.with_suffix('.tmp');tmp.write_text(json.dumps(payload));tmp.replace(result)
        with open(PROOFS/'journal.jsonl','a') as f:
            fcntl.flock(f,fcntl.LOCK_EX)
            f.write(json.dumps(dict(url_order=rows[0]['url_order'],url=url,links=len(links),status=status,finished=time.time()))+'\n');f.flush()
        for raw in house.CACHE.glob('*.raw'):raw.unlink()
        assert sum(p.stat().st_size for p in PROOFS.glob('*') if p.is_file())<2_000_000_000,'proof cache cap'
        print(rows[0]['url_order'],len(grouped),len(links),status,flush=True)
    (PROOFS/('worker-'+os.environ.get('ARCHIVE_WORKER','0')+'-terminal.json')).write_text(json.dumps(dict(finished=time.time(),deadline=deadline)))
if __name__=='__main__':
    try:main()
    except TimeoutError as e:
        (PROOFS/('worker-'+os.environ.get('ARCHIVE_WORKER','0')+'-terminal.json')).write_text(json.dumps(dict(finished=time.time(),reason=str(e))))
