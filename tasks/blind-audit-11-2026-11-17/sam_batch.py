"""One batched SAM Entity Management API v3 request for the 13 sampled UEIs (controller ruling 2026-11-17).
The key is read from ~/.config/polymer-atlas/sam.env and sent only as the X-Api-Key header: never printed, logged, put in a
URL or committed. The raw response is stored outside the repo (private/audit11/), with its sha256; nothing from it is
printed except counts (R-SAM: no SAM name or address enters the repo or the report).
ueiSAM takes values joined by ~ (no brackets: the gateway rejects them). The API returns 10 records per page (open.gsa.gov/api/entity-api), so page 1 is requested only if totalRecords > 10.
Run once: python3 sam_batch.py"""
import csv, hashlib, json, os, re, subprocess, tempfile
from pathlib import Path

H = Path(__file__).resolve().parent
OUT = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/private/audit11')
UEIS = [r['record_id'].split('|')[2] for r in csv.DictReader((H / 'sample.csv').open(newline='')) if r['change_class'] == 'uei_links']
URL = 'https://api.sam.gov/entity-information/v3/entities?ueiSAM={}&includeSections=entityRegistration,coreData&page={}'


def key():
    m = re.search(r'^\s*(?:export\s+)?SAM_API_KEY\s*=\s*(.+)$', (Path.home() / '.config/polymer-atlas/sam.env').read_text(), re.M)
    k = re.sub(r'["\'\s]', '', m.group(1))  # same normalisation as the controller's sed: strip quotes, spaces, CR/LF
    assert len(k) >= 20, 'SAM key did not load'
    return k


def get(page):
    """curl with the header read from a 0600 temp file: the key never reaches argv, a URL or a log (urllib's header handling got 401)."""
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        os.chmod(f.name, 0o600)
        f.write(f'X-Api-Key: {key()}\nAccept: application/json\n')
    try:
        r = subprocess.run(['curl', '-s', '-g', '-m', '90', '-H', '@' + f.name, '-w', '\n%{http_code}', URL.format('~'.join(UEIS), page)], capture_output=True)
    finally:
        os.unlink(f.name)
    body, _, code = r.stdout.rpartition(b'\n')
    return int(code or 0), body


def main():
    assert len(UEIS) == len(set(UEIS)) == 13
    files = {}
    status, body = get(0)
    print('page 0: HTTP', status, len(body), 'bytes')
    assert status == 200, f'HTTP {status}: nothing stored'
    (OUT / 'sam_uei_raw.json').write_bytes(body)
    files['sam_uei_raw.json'] = hashlib.sha256(body).hexdigest()
    total = json.loads(body).get('totalRecords')
    if total and total > 10:
        status, body = get(1)
        print('page 1: HTTP', status, len(body), 'bytes')
        assert status == 200, f'page 1 HTTP {status}'
        (OUT / 'sam_uei_raw_page1.json').write_bytes(body)
        files['sam_uei_raw_page1.json'] = hashlib.sha256(body).hexdigest()
    (OUT / 'sam_uei_raw.sha256').write_text(''.join(f'{h}  {n}\n' for n, h in files.items()))
    got = {e['entityRegistration']['ueiSAM'] for n in files for e in json.loads((OUT / n).read_bytes()).get('entityData', [])}
    print('totalRecords', total, '| sampled UEIs returned', len(got & set(UEIS)), 'of 13 | not returned', len(set(UEIS) - got))


if __name__ == '__main__':
    main()
