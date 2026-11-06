"""Retrieve SEC company identities; raw responses stay outside the repository."""
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = Path('/tmp/atlas-sec-cik-raw')


def fetch(cik):
    cik = str(cik).zfill(10)
    url = f'https://data.sec.gov/submissions/CIK{cik}.json'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 PolymerAtlas registry verification'})
    receipt = {'url': url, 'as_of': datetime.now(timezone.utc).date().isoformat()}
    try:
        with urllib.request.urlopen(req, timeout=40) as response:
            raw = response.read()
            receipt['http_status'] = response.status
        CACHE.mkdir(exist_ok=True)
        (CACHE / f'{cik}.json').write_bytes(raw)
        data = json.loads(raw)
        assert str(data['cik']).zfill(10) == cik, 'response CIK mismatch'
        assert data['name'] and isinstance(data['tickers'], list), 'incomplete SEC company record'
        receipt.update({k: data[k] for k in ('cik', 'name', 'tickers', 'exchanges')})
        receipt['raw_sha256'] = hashlib.sha256(raw).hexdigest()
        receipt['raw_name_token'] = json.dumps(data['name'], ensure_ascii=False)
        assert receipt['raw_name_token'] in raw.decode('utf-8'), 'name token absent from raw response'
    except Exception as exc:
        receipt['error'] = str(exc)
    (HERE / 'sources' / f'CIK{cik}.json').write_text(json.dumps(receipt, indent=2) + '\n')
    time.sleep(0.3)
    return receipt


if __name__ == '__main__':
    import sys
    if '--known' in sys.argv:
        known = [(320193, 'Apple Inc.', 'AAPL'), (51143, 'INTERNATIONAL BUSINESS MACHINES CORP', 'IBM'),
                 (89800, 'SHERWIN WILLIAMS CO', 'SHW'), (1122976, 'AVIENT CORP', 'AVNT')]
        for cik, name, ticker in known:
            r = fetch(cik)
            assert not r.get('error') and r['name'] == name and ticker in r['tickers'], r
        print('PASS four independently known CIK/name/ticker records')
    else:
        candidates = json.loads((HERE / 'sources/ticker-candidates.json').read_text())
        for row in candidates:
            r = fetch(row['cik_str'])
            print(row['ticker'], r.get('name', r.get('error')), flush=True)
