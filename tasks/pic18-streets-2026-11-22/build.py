#!/usr/bin/env python3
"""Builds packet.csv, holds.csv, dedupe_leads.csv, fetches.csv from verdicts.csv (hand readings), the stored captures and archive.csv. Writes nothing under data/.
Each VERIFIED row: the quote must be a contiguous substring of capture_text of the capture (archive original bytes when archived, else the live bytes); the offset is computed
here, never typed; ZIP only if inside the quote; the proposed street must appear in the quote; AGENTS 3 step 3 dedupe runs over every site shard (and site notes)."""
import csv, glob, hashlib, json, sys
from pathlib import Path
D = Path(__file__).resolve().parent; R = D.parents[1]; sys.path.insert(0, str(R / 'scripts')); sys.path.insert(0, str(D))
from atlas import street_key, NOTES_STREET_RE
from captext import capture_text
STORE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/streets-2026-11-22')
rd = lambda p: list(csv.DictReader(open(p, newline='', encoding='utf-8')))
sha = lambda b: hashlib.sha256(b).hexdigest()
def write(name, rows, cols):
    with open(D / name, 'w', newline='') as f:
        w = csv.DictWriter(f, cols, lineterminator='\n'); w.writeheader(); w.writerows(rows)
frame = {r['site_id']: r for r in rd(D / 'frame.csv')}
T = D.parent
prior = {}  # site_id -> {street_key: where}: streets the earlier street lanes saw (PPP/SAM leads; street-notes candidates)
for r in rd(T / 'pic18-street-leads-2026-11-16/leads.csv'): prior.setdefault(r['site_id'], {})[street_key(r['street'])] = 'street-leads 2026-11-16 ' + r['lead_class'] + ' lead'
for r in rd(T / 'pic18-street-notes-2026-11-17/verdicts.csv'):
    for m in NOTES_STREET_RE.finditer(r['candidates'] or ''): prior.setdefault(r['site_id'], {})[street_key(m.group(0))] = 'street-notes 2026-11-17 candidate'
ver = rd(D / 'verdicts.csv'); arch = {r['page_url']: r for r in rd(D / 'archive.csv')} if (D / 'archive.csv').exists() else {}
fx = [json.loads(l) for l in open(STORE / 'fetches.jsonl')]
live = {j['final_url']: j for j in fx if j.get('status') == 'ok' and j['kind'] != 'robots'}
sites = [s for f in sorted(glob.glob(str(R / 'data/sites_*.csv'))) for s in rd(f)]
by_key = {}
for s in sites:
    k = street_key(s['street_address'])
    if k: by_key.setdefault(k, []).append(s)
assert {v['site_id'] for v in ver} <= set(frame)
packet, holds, leads = [], [], []
for v in ver:
    f = frame[v['site_id']]
    if v['verdict'] != 'VERIFIED':
        js = [j for j in fx if j['org_id'] == f['org_id'] and j['kind'] != 'robots']
        holds.append(dict(site_id=v['site_id'], org_id=f['org_id'], verdict=v['verdict'], reason=v['reason'], detail=v['detail'], website=f['website'], pages_fetched=sum(j.get('status') == 'ok' for j in js), fetch_statuses=';'.join(sorted({j.get('status', '') for j in js}))))
        continue
    q = v['quote']; assert '\n' not in q and q == ' '.join(q.split()), 'quote must be whitespace-collapsed'
    a = arch.get(v['page_url']); has_arch = bool(a and a['status'] == 'ok')
    if has_arch: raw, shx, basis = (STORE / 'archive' / (a['archive_sha256'] + '.raw')).read_bytes(), a['archive_sha256'], 'archive_original'
    else: lj = live[v['page_url']]; raw, shx, basis = (STORE / 'raw' / (lj['sha256'] + '.raw')).read_bytes(), lj['sha256'], 'live'
    t = capture_text(raw); assert sha(raw) == shx
    assert t.count(q) >= 1, f"{v['site_id']}: quote not in capture text"
    off = t.index(q)
    assert v['street'].split(',')[0].lower() in q.lower() and f['city'].lower() in q.lower(), f"{v['site_id']}: street or city not in quote"
    assert not v['zip'] or v['zip'] in q
    same = lambda s: s['city'].strip().lower() == f['city'].strip().lower() and s['state'] == 'OH'  # one address = one site: the street in the same city and state
    dup = [s for s in by_key.get(street_key(v['street']), []) if s['site_id'] != v['site_id']]
    notes_hit = [s for s in sites if s['site_id'] != v['site_id'] and f" {street_key(v['street'])} " in f" {street_key(s['notes'])} "]
    for s in dup: leads.append(dict(site_id=v['site_id'], street=v['street'], other_site_id=s['site_id'], other_org_id=s['org_id'], other_city=s['city'], where='street_address', other_street=s['street_address'], blocking=int(same(s))))
    for s in notes_hit: leads.append(dict(site_id=v['site_id'], street=v['street'], other_site_id=s['site_id'], other_org_id=s['org_id'], other_city=s['city'], where='notes', other_street='', blocking=int(same(s))))
    block = sorted({s['site_id'] for s in dup + notes_hit if same(s)})
    if block:
        holds.append(dict(site_id=v['site_id'], org_id=f['org_id'], verdict='STILL_UNCERTAIN', reason='DEDUPE_LEAD', detail=f"street {v['street']} already belongs to {block} in the same city; not proposed (AGENTS 3 step 3)", website=f['website'], pages_fetched='', fetch_statuses='')); continue
    mine = street_key(v['street']); org_sites = [s for s in sites if s['org_id'] == f['org_id']]
    me_row = next(s for s in sites if s['site_id'] == v['site_id'])
    sib = [s for s in org_sites if s['site_id'] != v['site_id'] and s['city'].strip().lower() == f['city'].strip().lower() and s['state'] == 'OH']
    other = {street_key(m.group(0)): 'the site notes' for m in NOTES_STREET_RE.finditer(me_row['notes'])}
    other.update(prior.get(v['site_id'], {})); other = {k: w for k, w in other.items() if k and k != mine and not (mine.startswith(k + ' ') or k.startswith(mine + ' '))}  # a truncated regex match ('2474 state rte' for '... 4') is the same street
    for s in sib: leads.append(dict(site_id=v['site_id'], street=v['street'], other_site_id=s['site_id'], other_org_id=s['org_id'], other_city=s['city'], where=f"same operator, same city ({s['operating_status']}, tier {s['verification_tier']}, street {s['street_address'] or 'blank'})", other_street=s['street_address'], blocking=1))
    if sib:
        holds.append(dict(site_id=v['site_id'], org_id=f['org_id'], verdict='STILL_UNCERTAIN', reason='SIBLING_SAME_CITY', detail=f"{sorted(s['site_id'] for s in sib)} is the same operator's record in {f['city']}; which record owns {v['street']} is a dedupe/owner call (street-notes lane rule). Page reading: VERIFIED for the street at the operator.", website=f['website'], pages_fetched='', fetch_statuses='')); continue
    if other:
        holds.append(dict(site_id=v['site_id'], org_id=f['org_id'], verdict='STILL_UNCERTAIN', reason='TWO_CANDIDATES', detail=f"page gives {v['street']}; another candidate on record: {other} (key: where seen). Which one is the site is a question for the owner.", website=f['website'], pages_fetched='', fetch_statuses='')); continue
    packet.append(dict(site_id=v['site_id'], org_id=f['org_id'], proposed_street=v['street'], city=f['city'], zip=v['zip'], county=f['county'],
                       county_basis="the record's county, unchanged (earlier street lanes' rule); not derived from the page",
                       quote=q, source_url=v['page_url'], archive_url=a['archive_ref'] if has_arch else '', archive_captured_at=a['captured_at'] if has_arch else '',
                       capture_basis=basis, capture_sha256=shx, archive_served_sha256=a['archive_served_sha256'] if has_arch else '', org_sites_all_shards=len(org_sites), org_sites_same_city=len(sib) + 1, offset=off, length=len(q), live_sha256=live[v['page_url']]['sha256'], tie=v['tie'], archive_status='' if has_arch else 'NOT_ARCHIVED'))
write('packet.csv', packet, ['site_id', 'org_id', 'proposed_street', 'city', 'zip', 'county', 'county_basis', 'quote', 'source_url', 'archive_url', 'archive_captured_at', 'capture_basis', 'capture_sha256', 'archive_served_sha256', 'offset', 'length', 'live_sha256', 'org_sites_all_shards', 'org_sites_same_city', 'tie', 'archive_status'])
write('holds.csv', holds, ['site_id', 'org_id', 'verdict', 'reason', 'detail', 'website', 'pages_fetched', 'fetch_statuses'])
write('dedupe_leads.csv', leads, ['site_id', 'street', 'other_site_id', 'other_org_id', 'other_city', 'where', 'other_street', 'blocking'])
ids = {}
for r in frame.values():
    if r['site_id'] in {v['site_id'] for v in ver}: ids.setdefault(r['org_id'], []).append(r['site_id'])
frows = [dict(org_id=j['org_id'], site_ids=';'.join(ids[j['org_id']]), kind=j['kind'], url=j['url'], final_url=j.get('final_url', ''), http=j['http'], status=j.get('status', 'ok' if j['kind'] == 'robots' and j['http'] == 200 else 'robots_' + str(j['http'])), sha256=j.get('sha256', ''), fetched_at=j['fetched_at'], note=j.get('note', '')) for j in fx if j['org_id'] in ids]
write('fetches.csv', frows, ['org_id', 'site_ids', 'kind', 'url', 'final_url', 'http', 'status', 'sha256', 'fetched_at', 'note'])
print(f'verified {len(packet)}  holds {len(holds)}  dedupe lead rows {len(leads)}  fetch rows {len(frows)} (pages {sum(r["kind"] != "robots" for r in frows)})')
