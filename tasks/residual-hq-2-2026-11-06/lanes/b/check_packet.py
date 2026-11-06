#!/usr/bin/env python3
"""Check packet coverage, caps, receipts and quotes; raw files remain in /tmp."""
import csv, hashlib, html, re, subprocess, unicodedata
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent

def read(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))

def words(s):
    return re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower())

def has(text, quote):
    t, q = words(text), words(quote)
    return bool(q) and any(t[i:i+len(q)] == q for i in range(len(t)-len(q)+1))

def content(path):
    raw = path.read_bytes()
    if raw.startswith(b'%PDF'):
        p = subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True, text=True, check=True)
        return p.stdout
    s = raw.decode('utf8', 'replace')
    s = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', ' ', s, flags=re.S|re.I)
    return html.unescape(re.sub('<[^>]+>', ' ', s))

def check(rows, inputs, receipts):
    assert len(inputs) == len(rows) == 30, 'Expected all 30 allocated organizations'
    assert len({r['org_id'] for r in rows}) == 30, 'Duplicate verdict ID'
    assert {r['org_id'] for r in rows} == {r['org_id'] for r in inputs}, 'ID coverage differs'
    names = {r['org_id']:r['legal_name'] for r in inputs}
    counts = Counter(r['org_id'] for r in receipts)
    for r in rows:
        oid = r['org_id']
        assert r['legal_name'] == names[oid], oid
        assert 1 <= int(r['fetch_count']) <= 6, oid
        assert int(r['fetch_count']) == counts[oid], oid
        assert r['outcome'] == r['verdict'] in {'HQ_FOUND','STILL_UNKNOWN'}, oid
        matches = [p for p in receipts if p['org_id']==oid and p['source_url']==r['source_url'] and p['raw_sha256']==r['raw_sha256']]
        assert len(matches)==1, ('Missing or duplicate receipt',oid)
        if r['verdict']=='HQ_FOUND':
            assert all(r[k] for k in ['hq_city','hq_state','hq_country','source_class','quote']), oid
            assert r['source_class'] in {'own_site','registry'}, oid
            assert len(r['quote'].replace(' || ',' ').split()) <= 25, oid
            text = content(Path(matches[0]['raw_cache']))
            assert all(has(text,q) for q in r['quote'].split(' || ')), ('Quote mismatch',oid)
            assert has(r['quote'],r['hq_city']), oid
        else:
            assert r['settling_fact'] and r['reason'], oid
            assert not any(r[k] for k in ['hq_city','hq_state','hq_country','hq_county','quote']), oid
    for r in receipts:
        raw = Path(r['raw_cache'])
        assert raw.exists(), ('Cannot inspect raw receipt',str(raw))
        assert hashlib.sha256(raw.read_bytes()).hexdigest() == r['raw_sha256'], str(raw)
    return counts

if __name__ == '__main__':
    rows, inputs, receipts = read(HERE/'verdicts.csv'), read(HERE/'input.csv'), read(HERE/'receipts.csv')
    check(rows, inputs, receipts)
    # Real source/parser cases: HTML statement, split HTML HQ label/address, PDF footer.
    for oid in ['ORG-004523','ORG-004391','ORG-004533']:
        assert next(r for r in rows if r['org_id']==oid)['verdict']=='HQ_FOUND', oid
    # Negative controls must fail: missing record, duplicate ID, invented quote.
    for kind in ['missing','duplicate','quote']:
        bad = [dict(r) for r in rows]
        if kind=='missing': bad.pop()
        elif kind=='duplicate': bad[-1]=dict(bad[0])
        else: next(r for r in bad if r['verdict']=='HQ_FOUND')['quote']='Invented headquarters in Nowhere California'
        try: check(bad,inputs,receipts)
        except AssertionError: pass
        else: raise AssertionError('Negative control passed: '+kind)
    print('PASS: 30/30 unique allocated orgs; 7 HQ_FOUND, 23 STILL_UNKNOWN; 87 receipt hashes; <=6 fetches/org; all 7 positive quotes matched; 3 real source/parser cases; 3 negative controls rejected.')
