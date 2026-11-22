#!/usr/bin/env python3
"""Mechanical check for the 2026-11-22 web canary. Re-verifies every candidate quote against its stored capture by hash and offset, then proves it
fails on planted defects. Usage: python3 check.py [STORE]   (STORE = persist/web-canary-2026-11-22, outside the repo; default below)
Exit 0 = all real rows pass AND every planted defect was caught."""
import csv, hashlib, json, re, sys
from pathlib import Path
D = Path(__file__).resolve().parent
STORE = Path(sys.argv[1] if len(sys.argv) > 1 else '/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/web-canary-2026-11-22')
SCHEMA = (D.parents[1] / 'docs' / 'SCHEMA.md').read_text()
sha = lambda b: hashlib.sha256(b).hexdigest()
rd = lambda p: list(csv.DictReader(open(D / p, newline='', encoding='utf-8')))
terms = lambda a, b: set(re.findall(r'`([a-z0-9_]+)`', SCHEMA[SCHEMA.index(a):SCHEMA.index(b)]))
VOCAB = {'processes': terms('### 3.1 Processes', '### 3.2 Materials'), 'markets_served': terms('### 3.3 Markets Served', '### 3.4 Certifications')}
VERDICTS = {'VERIFIED', 'REJECT', 'STILL_UNCERTAIN', 'DUPLICATE_OF'}
words = lambda v: re.findall(r'[a-z0-9]+', v.lower())


def quote_problems(r, fetched):
    """Return the list of reasons this candidate row fails (empty = pass)."""
    p, q = [], r['quote']
    if r['field'] not in VOCAB: return ['field not processes|markets_served']
    if r['term'] not in VOCAB[r['field']]: p.append('term not in controlled vocabulary')
    if r['verdict'] not in VERDICTS: p.append('verdict not in grammar')
    if len(q) < 40: p.append('quote under 40 characters')
    if '\n' in q: p.append('quote spans lines')
    f = STORE / 'text' / (r['capture_sha256'] + '.txt')
    if not f.exists(): return p + ['capture missing']
    b = f.read_bytes()
    if sha(b) != r['capture_sha256']: p.append('capture hash mismatch')
    t = b.decode()
    try: off = int(r['offset'])
    except ValueError: return p + ['offset not an integer']
    if t[off:off + len(q)] != q: p.append('quote is not at the stated offset (not verbatim)')
    meta = json.loads((STORE / 'text' / (r['capture_sha256'] + '.lines.json')).read_text())
    line = next((m for m in meta if m[0] <= off < m[1]), None)
    if not line or off + len(q) > line[1]: p.append('quote not inside one main-text line')
    if r['capture_sha256'] not in fetched: p.append('capture not listed in fetches.csv')
    return p


def main():
    frame, fetches, cands = rd('frame.csv'), rd('fetches.csv'), rd('candidates.csv')
    bad = []
    if len(frame) != 25: bad.append(f'frame has {len(frame)} rows, not 25')
    ids = {r['org_id'] for r in frame}
    for r in fetches:  # every stored raw capture re-hashes to the listed sha256
        if r['sha256'] and r['kind'] != 'robots' and r['status'] in ('ok', 'THIN_OR_EMPTY', 'NOT_HTML'):  # robots.txt bodies were hashed, not stored
            f = STORE / 'raw' / (r['sha256'] + '.raw')
            if not f.exists() or sha(f.read_bytes()) != r['sha256']: bad.append('raw capture missing or hash mismatch: ' + r['url'])
    fetched = {r['text_sha256'] for r in fetches if r.get('text_sha256')}
    for r in cands:
        if r['org_id'] not in ids: bad.append('candidate outside frame: ' + r['org_id'])
        bad += [f"{r['org_id']} {r['term']}: {x}" for x in quote_problems(r, fetched)]
    holds = rd('holds.csv')  # every (org, field) is exactly one of: VERIFIED fill, or a hold
    cover = [(r['org_id'], r['field']) for r in holds] + sorted({(r['org_id'], r['field']) for r in cands if r['verdict'] == 'VERIFIED'})
    want = sorted((o, f) for o in ids for f in VOCAB)
    if sorted(cover) != want: bad.append(f'holds + VERIFIED fills do not cover each (org, field) exactly once: {len(cover)} vs {len(want)}')
    if any(not r['settling_fact'].strip() or not r['reason'].strip() for r in holds): bad.append('hold without reason or settling fact')
    for r in cands:  # a VERIFIED row needs a reason-free narrative line: reject list-item lines (supports_C strength)
        meta = json.loads((STORE / 'text' / (r['capture_sha256'] + '.lines.json')).read_text()) if (STORE / 'text' / (r['capture_sha256'] + '.lines.json')).exists() else []
        if r['verdict'] == 'VERIFIED' and any(m[0] <= int(r['offset']) < m[1] and m[2] in ('li', 'td') for m in meta): bad.append(f"{r['org_id']} {r['term']}: VERIFIED quote sits in a list/table line")
    # planted defects: each must be caught, or the check is a silent pass
    ok = [r for r in cands if not quote_problems(r, fetched)]
    miss = []
    if ok:
        r = ok[0]
        plants = {
            'paraphrase': dict(r, quote=r['quote'].replace(r['quote'].split()[2], 'foo', 1)),
            'short quote': dict(r, quote=r['quote'][:30]),
            'wrong offset': dict(r, offset=str(int(r['offset']) + 1)),
            'bad capture hash': dict(r, capture_sha256='0' * 64),
            'term outside vocabulary': dict(r, term='made_up_term'),
            'bad verdict': dict(r, verdict='MAYBE'),
        }
        for name, row in plants.items():
            if not quote_problems(row, fetched): miss.append(name)
    if bad or miss:
        print('FAIL', *bad, *[f'planted defect not caught: {m}' for m in miss], sep='\n  '); sys.exit(1)
    v = [r for r in cands if r['verdict'] == 'VERIFIED']
    print(f'OK frame={len(frame)} fetch rows={len(fetches)} candidates={len(cands)} VERIFIED={len(v)}; {len(ok)} rows re-verified; planted defects caught: {6 if ok else 0}')


if __name__ == '__main__': main()
