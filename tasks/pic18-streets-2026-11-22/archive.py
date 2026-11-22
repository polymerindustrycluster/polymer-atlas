#!/usr/bin/env python3
"""Save each page cited by a VERIFIED row to the Wayback Machine (SCHEMA 4.22, archive at capture) and store the archived original bytes (the id_ form the
binding gate fetches). Idempotent: URLs already in archive.csv are skipped. Writes archive.csv: page_url, archive_ref, captured_at, archive_served_sha256, archive_sha256 (of the bytes after undoing a gzip Content-Encoding, which Wayback id_ serves as stored: the capture the quote offsets index), live_sha256, same_bytes, status.
Only a URL that a stored capture of this lane fetched is ever submitted (never a guessed URL)."""
import csv, gzip, hashlib, json, re, subprocess, sys, time
from pathlib import Path
D = Path(__file__).resolve().parent
STORE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/streets-2026-11-22'); (STORE / 'archive').mkdir(exist_ok=True)
sha = lambda b: hashlib.sha256(b).hexdigest()
live = {}
for l in open(STORE / 'fetches.jsonl'):
    j = json.loads(l)
    if j.get('status') == 'ok' and j['kind'] != 'robots': live[j['final_url']] = j['sha256']
done = {r['page_url']: r for r in csv.DictReader(open(D / 'archive.csv'))} if (D / 'archive.csv').exists() else {}
urls = sorted({r['page_url'] for r in csv.DictReader(open(D / 'verdicts.csv')) if r['verdict'] == 'VERIFIED'})
def curl(args): return subprocess.run(['curl', '-sS', '-m', '180', '-A', 'Mozilla/5.0 (compatible; AtlasSiteCorpus/1.0)'] + args, capture_output=True)
for u in urls:
    if u in done and done[u]['status'] == 'ok': continue
    assert u in live, f'{u} was not fetched by this lane'
    ref, status = '', 'SAVE_FAILED'
    for attempt in range(3):
        r = curl(['-o', '/dev/null', '-D', '-', 'https://web.archive.org/save/' + u]).stdout.decode('latin-1')
        m = re.search(r'(?im)^location:\s*(https://web\.archive\.org/web/(\d{14})/\S+)', r)
        if m: ref = m.group(1); break
        time.sleep(20 * (attempt + 1))
    row = dict(page_url=u, archive_ref=ref, captured_at='', archive_served_sha256='', archive_sha256='', live_sha256=live[u], same_bytes='', status=status)
    if ref:
        ts = re.search(r'/web/(\d{14})/', ref).group(1); row['captured_at'] = f'{ts[:4]}-{ts[4:6]}-{ts[6:8]}'
        b = b''
        for attempt in range(3):
            time.sleep(5); p = curl(['-L', re.sub(r'(/web/\d{14})/', r'\1id_/', ref)]); b = p.stdout
            if p.returncode == 0 and b: break
        if b:
            row['archive_served_sha256'] = sha(b); b = gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b
            row['archive_sha256'] = sha(b); (STORE / 'archive' / (row['archive_sha256'] + '.raw')).write_bytes(b)
            row['same_bytes'] = int(row['archive_sha256'] == live[u]); row['status'] = 'ok'
        else: row['status'] = 'ARCHIVE_UNREADABLE'
    done[u] = row; print(u, row['status'], ref)
rows = [done[u] for u in sorted(done)]
with open(D / 'archive.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)
