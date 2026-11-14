"""Raw fetch + receipt for phase 3 adjudication. Bodies go to the persist dir (hash-named); receipts append to adjudication_receipts.jsonl.
Usage: python3 adjudicate_fetch.py URL [term ...]   prints status/size and context around each term (case-insensitive).
A failed fetch (403, 202, timeout, bot wall) is an availability signal about the route, never evidence of absence."""
import hashlib, html, json, re, subprocess, sys, unicodedata
from datetime import datetime, timezone
from pathlib import Path

H = Path(__file__).resolve().parent
RAW = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/blind-audit-10/raw')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
# dashes become word breaks first: ascii-folding would otherwise glue 'technologies—from' into one token
WORDS = lambda s: re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', re.sub(r'[\u2010-\u2015\u2212]', ' ', s or '')).encode('ascii', 'ignore').decode().lower())


def visible(body: bytes, url: str) -> str:
    if body[:5] == b'%PDF-':
        r = subprocess.run(['pdftotext', '-layout', '-', '-'], input=body, capture_output=True)
        return r.stdout.decode('utf-8', 'replace')
    t = body.decode('utf-8', 'replace')
    t = re.sub(r'(?is)<(script|style|noscript)\b.*?</\1>', ' ', t)
    t = re.sub(r'(?s)<[^>]+>', ' ', t)
    return html.unescape(t)


def quote_in_order(text: str, quote: str) -> bool:
    q, w = WORDS(quote), WORDS(text)
    return bool(q) and any(w[i:i + len(q)] == q for i in range(len(w) - len(q) + 1))


def fetch(url: str, via: str = 'curl') -> dict:
    target = url if via == 'curl' else 'https://r.jina.ai/' + url
    r = subprocess.run(['curl', '-sSL', '--max-time', '45', '-A', UA, '-H', 'Accept: text/html,application/xhtml+xml,application/pdf,*/*', '-w', '\n%{http_code}', target], capture_output=True)
    body, _, code = r.stdout.rpartition(b'\n')
    try:
        status = int(code or 0)
    except ValueError:
        status = 0
    sha = hashlib.sha256(body).hexdigest()
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / f'{sha}.bin').write_bytes(body)
    rec = dict(url=url, via=via, http_status=status, bytes=len(body), sha256=sha, fetched_at=datetime.now(timezone.utc).isoformat(timespec='seconds'))
    with (H / 'adjudication_receipts.jsonl').open('a') as f:
        f.write(json.dumps(rec) + '\n')
    return rec


if __name__ == '__main__':
    url, terms = sys.argv[1], sys.argv[2:]
    rec = fetch(url)
    if rec['http_status'] != 200 or rec['bytes'] < 800:
        print('curl route:', rec['http_status'], rec['bytes'], '-> trying jina')
        rec = fetch(url, 'jina')
    print({k: rec[k] for k in ('via', 'http_status', 'bytes', 'sha256')})
    text = re.sub(r'\s+', ' ', visible((RAW / f"{rec['sha256']}.bin").read_bytes(), url))
    for t in terms:
        hits = [m.start() for m in re.finditer(re.escape(t), text, re.I)]
        print(f'--- {t!r}: {len(hits)} hit(s)')
        for i in hits[:2]:
            print('   ...' + text[max(0, i - 110):i + 170] + '...')
