#!/usr/bin/env python3
"""Route 1 (owner ruling 2026-11-22): where the live site cannot be read, record whether the Wayback Machine holds a capture of the record's website (availability API) and its date;
if the capture is dated on or after 2024-11-22, read it as the company's own page: the capture of the record URL, then up to 5 same-domain links found on that capture (each requested as
web.archive.org/web/<ts>id_/<url>, which Wayback serves from its nearest capture). The live page governs whenever it is readable, so only organizations whose live fetch failed are tried;
robots-disallowed sites are recorded but not read. Writes wayback_availability.csv and appends capture rows to the store's archived_fetches.jsonl; raw bytes (gunzipped) go to the store."""
import csv, gzip, hashlib, json, re, sys, time
from pathlib import Path
from urllib.parse import urljoin, urlsplit
D = Path(__file__).resolve().parent; sys.path.insert(0, str(D))
import fetch
STORE = fetch.STORE; (STORE / 'wb').mkdir(exist_ok=True)
CUTOFF = '20241122'
sha = lambda b: hashlib.sha256(b).hexdigest()
F = fetch.Fetcher()
frame = list(csv.DictReader(open(D / 'frame.csv')))
holds = {r['site_id']: r for r in csv.DictReader(open(D / 'holds.csv'))}
TRY = {'NO_DNS', 'TLS_ERROR', 'TIMEOUT', 'CONNECTION_REFUSED', 'ROBOTS_HTTP_403', 'HOME_404', 'THIN_PAGE', 'TRANSPORT_ERROR', 'HOME_HTTP_202'}
ALL = TRY | {'ROBOTS_DISALLOWS'}
orgs = {}
for r in frame:
    h = holds.get(r['site_id'])
    if h and h['reason'] in ALL: orgs.setdefault(r['org_id'], dict(site_ids=[], website=fetch.website(r['website']), reason=h['reason']))['site_ids'].append(r['site_id'])
def wb(url):
    """GET a web.archive.org id_ URL, following Wayback's redirects to the nearest capture; returns (response, final capture timestamp)."""
    cur = url
    for _ in range(6):
        r = F.curl1(cur)
        if r['code'] in (301, 302, 303, 307, 308) and r['location']: cur = urljoin(cur, r['location']); continue
        break
    m = re.search(r'/web/(\d{14})id_/', cur); return r, (m.group(1) if m else '')
def body(r): return gzip.decompress(r['raw']) if r['raw'][:2] == b'\x1f\x8b' else r['raw']
out, log = [], open(STORE / 'archived_fetches.jsonl', 'a')
def rec(row): row['fetched_at'] = time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime()); log.write(json.dumps(row) + '\n'); log.flush()
for oid, o in sorted(orgs.items()):
    host = o['website']; row = dict(org_id=oid, site_ids=';'.join(o['site_ids']), website=host, live_reason=o['reason'], available='', snapshot_url='', snapshot_date='', read='')
    r = F.curl1('https://archive.org/wayback/available?url=' + host.split('//')[-1].rstrip('/'))
    try: snap = json.loads(r['raw'])['archived_snapshots'].get('closest', {})
    except Exception: snap = None
    if snap is None: row['available'] = 'API_ERROR'
    elif not snap: row['available'] = 'no'
    else: row.update(available='yes', snapshot_url=snap['url'], snapshot_date=snap['timestamp'][:8])
    if row['available'] == 'yes' and o['reason'] != 'ROBOTS_DISALLOWS' and snap['timestamp'][:8] >= CUTOFF:
        ts = snap['timestamp']; u = re.sub(r'^https?://web\.archive\.org/web/\d+/', '', snap['url']); n = 0
        r, fts = wb(f'https://web.archive.org/web/{ts}id_/{u}'); b = body(r)
        rec(dict(org_id=oid, kind='archived_home', url=u, archive_ts=fts, http=r['code'], sha256=sha(b), bytes=len(b)))
        if r['code'] == 200 and b:
            (STORE / 'wb' / (sha(b) + '.raw')).write_bytes(b); row['read'] = 'home'
            pg = fetch.Page(); pg.feed(b.decode('utf-8', 'replace')); _, links = pg.result()
            for lu, txt in fetch.pick_links(u, links, {urlsplit(u).netloc.lower().removeprefix('www.') + urlsplit(u).path.rstrip('/')}):
                if n >= 5: break
                r2, f2 = wb(f'https://web.archive.org/web/{ts}id_/{lu}'); b2 = body(r2); n += 1
                rec(dict(org_id=oid, kind='archived_link', url=lu, archive_ts=f2, http=r2['code'], sha256=sha(b2), bytes=len(b2)))
                if r2['code'] == 200 and b2: (STORE / 'wb' / (sha(b2) + '.raw')).write_bytes(b2)
            row['read'] = f'home+{n}'
    out.append(row); print(oid, row['available'], row['snapshot_date'], row['read'])
with open(D / 'wayback_availability.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, list(out[0]), lineterminator='\n'); w.writeheader(); w.writerows(out)
