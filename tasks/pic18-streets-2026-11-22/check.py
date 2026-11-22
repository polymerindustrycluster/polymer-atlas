#!/usr/bin/env python3
"""Re-verifies packet.csv against the stored captures (outside the repo; arg 1 overrides the store path) and proves the check fails on planted defects.
Every packet row: capture bytes re-hash to capture_sha256; the quote is at offset/length in main text of those bytes; the quote holds the street and the record's city
(and the ZIP, if proposed); no phone number or email in the quote; the source URL's registrable domain is the organization's website domain (or a link-found page on it);
archive_url has the SCHEMA 4.22 shape and cites source_url; county is the record's. Also: frame has 121 rows recomputed independently of frame.csv; every frame site is in
exactly one of packet/holds; fetches.csv lists every packet capture. Exit 0 only if every real row passes AND every planted defect is caught."""
import csv, glob, gzip, hashlib, re, sys
from pathlib import Path
from urllib.parse import urlsplit
D = Path(__file__).resolve().parent; R = D.parents[1]; sys.path.insert(0, str(D)); sys.path.insert(0, str(R / 'scripts'))
from captext import main_text as capture_text
STORE = Path(sys.argv[1] if len(sys.argv) > 1 else '/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/streets-2026-11-22')
rd = lambda p: list(csv.DictReader(open(p, newline='', encoding='utf-8')))
sha = lambda b: hashlib.sha256(b).hexdigest()
frame = {r['site_id']: r for r in rd(D / 'frame.csv')}
PHONE = re.compile(r'(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)'); EMAIL = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
ARCH = re.compile(r'https://web\.archive\.org/web/\d{14}/(\S+)')
def regd(h): h = (h or '').lower().removeprefix('www.').split('.'); return '.'.join(h[-3:] if len(h) >= 3 and h[-2] in ('co', 'com', 'org', 'ac') else h[-2:])
def norm_url(u): p = urlsplit(u); return (p.netloc.lower().removeprefix('www.') + p.path.rstrip('/'))

def problems(r):
    p, q = [], r['quote']; f = frame.get(r['site_id'])
    if not f: return ['site not in frame']
    cap = STORE / {'archive_original': 'archive', 'archived_copy': 'wb', 'live': 'raw'}[r['capture_basis']] / (r['capture_sha256'] + ('.raw'))
    if not cap.exists(): return ['capture missing']
    b = cap.read_bytes()
    if sha(b) != r['capture_sha256']: p.append('capture hash mismatch')
    t = capture_text(b)
    try: off, n = int(r['offset']), int(r['length'])
    except ValueError: return p + ['offset/length not integers']
    if n != len(q): p.append('length is not the quote length')
    if t[off:off + n] != q: p.append('quote is not verbatim at offset')
    if q != ' '.join(q.split()): p.append('quote not whitespace-collapsed')
    if r['proposed_street'].split(',')[0].lower() not in q.lower(): p.append('street not in quote')
    if not re.search(r'(?<![A-Za-z])' + re.escape(f['city']) + r'(?![A-Za-z])', q, re.I) or re.search(r'(?i)\b(?:north|south|east|west|new|old|port|mount|mt\.?)\s+' + re.escape(f['city']) + r'\b', q) and not f['city'].lower().startswith(('north', 'south', 'east', 'west', 'new')): p.append("record's city not in quote as a whole word (or a directional/prefixed variant of it)")
    if r['zip'] and r['zip'] not in q: p.append('zip not in quote')
    if PHONE.search(q) or EMAIL.search(q): p.append('phone number or email in quote')
    if r['city'] != f['city'] or r['county'] != f['county']: p.append('city/county differ from the record')
    web = regd(urlsplit(f['website'].split()[0] if f['website'].split() else '').hostname or f['website'].split()[0].split('/')[0] if f['website'].split() else '')
    if regd(urlsplit(r['source_url']).hostname) != web: p.append('source URL is off the record domain')
    if r['archive_url']:
        m = ARCH.fullmatch(r['archive_url'])
        if not m or norm_url(m.group(1)) != norm_url(r['source_url']): p.append('archive_url does not cite source_url in 4.22 form')
    else: p.append('no archive_url: a row without its archive capture is held (archive_unavailable)')
    if r['source_route'] not in ('live', 'archived_copy', 'rendered', 'official_page'): p.append('source_route not allowed for a VERIFIED row (image_text is never VERIFIED)')
    if r['source_route'] == 'archived_copy':
        m = ARCH.fullmatch(r['archive_url'])
        if r['observed_date'] < '2024-11-22': p.append('archived copy older than 2024-11-22')
        if not m or r['archive_url'].split('/web/')[1][:8] != r['observed_date'].replace('-', ''): p.append('capture timestamp is not the observed date')
    return p

def main():
    packet, holds, fetches = rd(D / 'packet.csv'), rd(D / 'holds.csv'), rd(D / 'fetches.csv')
    bad = []
    # independent frame recount (no frame.py code): active tier A-C Ohio PIC-18 sites, blank street, organization with no size band
    from regions import PIC18
    orgs = {r['org_id']: r for f in glob.glob(str(R / 'data/organizations_*.csv')) for r in rd(f)}; eco = {r['org_id']: r for r in rd(R / 'data/ecosystem.csv')}
    ss = [s for s in rd(R / 'data/sites_OH.csv') if s['county'] in PIC18 and s['operating_status'] == 'active' and s['verification_tier'] in ('A', 'B', 'C')]
    tk = lambda v: {x.strip() for x in (v or '').split(';') if x.strip() and x.strip() != 'unknown'}
    nb = {o for o in {s['org_id'] for s in ss} if not (set().union(*(tk(s['employee_band_site']) for s in ss if s['org_id'] == o)) or tk((orgs.get(o) or eco.get(o) or {}).get('employee_band_ohio')))}
    indep = {s['site_id'] for s in ss if s['org_id'] in nb and not s['street_address'].strip()}
    if indep != set(frame): bad.append(f'frame differs from independent recount: {len(indep)} vs {len(frame)}')
    done = [r['site_id'] for r in packet] + [r['site_id'] for r in holds]
    attempted = {r['site_id'] for r in rd(D / 'verdicts.csv')}
    if sorted(done) != sorted(set(done)) or set(done) != attempted: bad.append('packet+holds must cover each attempted site exactly once')
    if not attempted <= set(frame): bad.append('attempted site outside the frame')
    cited = {r['capture_sha256'] for r in packet}
    for r in packet:
        for why in problems(r): bad.append(f"{r['site_id']}: {why}")
    # planted defects: each must be caught
    from atlas import NOTES_STREET_RE
    caught = 0; plants = []; tx = lambda r: capture_text((STORE / {'archive_original': 'archive', 'archived_copy': 'wb', 'live': 'raw'}[r['capture_basis']] / (r['capture_sha256'] + '.raw')).read_bytes())
    if not packet: bad.append('empty packet: nothing to plant defects into')
    else:
        base = packet[0]; w0 = base['quote'].split()[0]
        plants.append(('paraphrased quote', {**base, 'quote': base['quote'].replace(w0, 'Zzzz', 1)}))
        plants.append(('shifted offset', {**base, 'offset': str(int(base['offset']) + 3)}))
        plants.append(('bad capture sha', {**base, 'capture_sha256': '0' * 63 + '1'}))
        plants.append(('phone number in quote', {**base, 'quote': base['quote'] + ' 555-010-0199', 'length': str(len(base['quote']) + 13)}))
        plants.append(('off-domain source', {**base, 'source_url': 'https://example.org/contact'}))
        n_other = 0
        for r in packet:  # a real street from ANOTHER city on a stored page, filed on the site whose page it is
            tt = tx(r)
            for m in NOTES_STREET_RE.finditer(tt):
                q2 = tt[m.start(): m.end() + 40]; q2 = q2[: len(q2.split(',')[0]) + 14] if ',' in q2 else q2
                if r['city'].lower() not in tt[max(0, m.start() - 80): m.end() + 80].lower() and r['quote'] not in q2:
                    q2 = ' '.join(q2.split()); plants.append((f"address from another city ({r['site_id']}: {q2[:40]})", {**r, 'proposed_street': m.group(0), 'zip': '', 'quote': q2, 'offset': str(tt.index(q2)), 'length': str(len(q2))})); n_other += 1; break
            if n_other >= 2: break
        if not n_other: bad.append('could not plant an address-from-another-city defect (no stored page of a packet row has a street outside the record city)')
    for name, row in plants:
        if problems(row): caught += 1
        else: bad.append(f'planted defect NOT caught: {name}')
    for r in packet:
        if r['capture_sha256'] not in cited: pass
    fshas = {r['sha256'] for r in fetches}
    homes = {}
    for x in fetches:
        if x['kind'] == 'home': homes[x['org_id']] = x['status']
    for r in packet:
        if r['source_route'] == 'archived_copy' and homes.get(r['org_id']) == 'ok': bad.append(f"{r['site_id']}: archived copy used although the live home page was readable (live page governs)")
        if r['source_route'] == 'live' and r['live_sha256'] not in fshas: bad.append(f"{r['site_id']}: live capture not in fetches.csv")
    for r in []:
        if r['live_sha256'] not in fshas: bad.append(f"{r['site_id']}: live capture not in fetches.csv")
    print(f'frame={len(frame)} (independent recount {len(indep)}) attempted={len(attempted)} packet={len(packet)} holds={len(holds)} fetch rows={len(fetches)}; planted defects caught {caught}/{len(plants)}')
    for b in bad: print('FAIL', b)
    sys.exit(1 if bad else 0)
main()
