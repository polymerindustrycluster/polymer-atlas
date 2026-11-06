#!/usr/bin/env python3
"""Availability is discovery only; a paced readable replay must contain the quote."""
import concurrent.futures
import hashlib
import json
import re
import subprocess
import time
import threading
import sys
from run import HERE, ROOT, CACHE, read, write, fetch, on_page

FIELDS = ['evidence_id', 'archive_ref', 'captured_at', 'created_by']
AVAILABILITY_STOP = threading.Event()


def same_page(a, b):
    from urllib.parse import urlsplit
    def norm(url):
        p = urlsplit(url.strip())
        return (p.netloc.lower().removeprefix('www.'), p.path.rstrip('/'), p.query, p.fragment)
    return norm(a) == norm(b)


def same_capture(a, b):
    pattern = r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)'
    left, right = re.fullmatch(pattern, a), re.fullmatch(pattern, b)
    return bool(left and right and left[1] == right[1] and same_page(left[2], right[2]))


def available(url):
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + '.available.json')
    if path.exists(): return json.loads(path.read_text())
    if AVAILABILITY_STOP.is_set(): return dict(url=url, archive_ref='', availability_status='RATE_LIMIT_HOLD')
    time.sleep(1)
    p = subprocess.run(['curl','-sS','--max-time','25','-G','https://archive.org/wayback/available','--data-urlencode','url='+url,'-w','\n%{http_code}'], capture_output=True, text=True)
    body, _, code = p.stdout.rpartition('\n')
    if code == '429': AVAILABILITY_STOP.set()
    try:
        d = json.loads(body) if code == '200' and p.returncode == 0 else {}
        c = d.get('archived_snapshots', {}).get('closest', {})
        ref = c.get('url', '').replace('http://web.archive.org/', 'https://web.archive.org/')
        m = re.fullmatch(r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)', ref)
        if not (c.get('available') and c.get('status') == '200' and m and same_page(m[2], url)): ref = ''
        result = dict(url=url, archive_ref=ref, availability_status=code)
    except (ValueError, TypeError): result = dict(url=url, archive_ref='', availability_status='invalid_json')
    path.write_text(json.dumps(result)); return result


def main():
    verdicts = read(HERE / 'verdicts.csv')
    grouped = {}
    for r in verdicts:
        if r['judgment'] == 'SUPPORTED': grouped.setdefault(r['url'], []).append(r)
    if any(json.loads(p.read_text()).get('availability_status') == '429' for p in CACHE.glob('*.available.json')):
        AVAILABILITY_STOP.set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        availability = list(pool.map(available, sorted(grouped)))
    print('availability queried', len(availability), flush=True)
    links, outcomes = [], []
    consecutive_429 = 0
    for i, a in enumerate(availability, 1):
        ref = a['archive_ref']
        status = ('NO_CAPTURE' if a['availability_status'] == '200' else 'RATE_LIMIT_HOLD' if a['availability_status'] in ('429','RATE_LIMIT_HOLD') else 'AVAILABILITY_FAILED')
        if ref and '--cached-only' in sys.argv and not (CACHE / (hashlib.sha256(ref.encode()).hexdigest()+'.json')).exists():
            status = 'CAPTURE_PENDING'
        elif ref and consecutive_429 < 3:
            if '--cached-only' not in sys.argv: time.sleep(2)
            f = fetch(ref, fallback=False)
            code = f['attempts'][-1]['status']
            consecutive_429 = consecutive_429 + 1 if code == '429' else 0
            if code == '429': time.sleep(30)
            effective = f['attempts'][-1]['effective_url']
            # Redirecting to another capture/page cannot bind the discovered timestamp.
            if f['status'] == 'ok' and same_capture(effective, ref):
                status = 'READABLE'
                for e in grouped[a['url']]:
                    if on_page(e['quote'], ROOT / f['page']):
                        stamp = re.search(r'/web/(\d{14})/', ref)[1]
                        links.append(dict(evidence_id=e['evidence_id'], archive_ref=ref, captured_at=stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:8], created_by='atlas-L1-reverify-archive'))
                    else: outcomes.append(dict(evidence_id=e['evidence_id'],url=a['url'],archive_ref=ref,status='QUOTE_ABSENT'))
            else: status = 'CAPTURE_FETCH_FAILED' if f['status'] != 'ok' else 'CAPTURE_REDIRECT_HOLD'
        elif ref: status = 'RATE_LIMIT_HOLD'
        if status != 'READABLE':
            outcomes.extend(dict(evidence_id=e['evidence_id'], url=a['url'],archive_ref=ref,status=status) for e in grouped[a['url']])
        write(HERE / 'archive_links.csv', sorted(links,key=lambda x:x['evidence_id']), FIELDS)
        write(HERE / 'archive_outcomes.csv', outcomes, ['evidence_id','url','archive_ref','status'])
        if i % 25 == 0: print('captures', i, '/',len(availability),'links',len(links), flush=True)
    assert len(links) + len(outcomes) == sum(len(v) for v in grouped.values())
    assert len({r['evidence_id'] for r in links+outcomes}) == len(links)+len(outcomes)
    print('archive links',len(links),'outcomes',len(outcomes),flush=True)


if __name__ == '__main__': main()
