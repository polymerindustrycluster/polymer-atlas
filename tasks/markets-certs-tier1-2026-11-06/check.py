"""Fetch known answers, check every packet quote, then independently re-fetch a seeded 30-value sample."""
import csv, random, hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fetch import fetch, found
HERE = Path(__file__).resolve().parent

def main():
    frame = list(csv.DictReader((HERE / 'frame.csv').open()))
    verdicts = list(csv.DictReader((HERE / 'verdicts.csv').open()))
    assert len(frame) == len(verdicts) == 30, 'frame/verdict yield mismatch'
    assert len({r['org_id'] for r in frame}) == len({r['org_id'] for r in verdicts}) == 30
    assert {r['org_id'] for r in frame} == {r['org_id'] for r in verdicts}
    assert all(r['verdict'] in ('VERIFIED', 'STILL_UNCERTAIN') for r in verdicts)
    cases = [
        ('https://cimaplastics.com/markets.shtml', 'Markets Served Outdoor Power Equipment Medical', True),
        ('https://esterle.com/', 'ISO 9001:2015 certification', True),
        ('https://www.hudsonextrusions.com/', 'iso 9001:2015 Without Design', True),
        ('https://cimaplastics.com/quality.shtml', 'ISO 9001:2015 certified', False),
    ]
    for url, quote, expected in cases:
        text, _, _ = fetch(url)
        assert found(text, quote) == expected, (url, quote)
        assert not found(text, 'L10 deliberately fabricated defect phrase'), url
    print('known answers: 4/4; injected fabricated quotes refused: 4/4')
    rows = list(csv.DictReader((HERE / 'inputs.csv').open()))
    routes = {}
    def retrieve(url):
        text, _, route = fetch(url); routes[url] = route
        return url, text
    pages = dict(ThreadPoolExecutor(6).map(retrieve, sorted({r['source_url'] for r in rows})))
    for r in rows:
        assert found(pages[r['source_url']], r['quote']), r
        if r['verdict'] == 'VERIFIED' and r['field'] == 'certifications':
            assert found(pages[r['source_url']], r['cert_identity_quote']), r
            assert found(pages[r['source_url']], r['cert_expiry_quote']), r
    print('packet quotes:', len(rows), 'passed; zero unavailable pages')
    sample = random.Random(20361106).sample([r for r in rows if r['verdict'] == 'VERIFIED'], 30)
    pages = dict(ThreadPoolExecutor(6).map(retrieve, sorted({r['source_url'] for r in sample})))
    out = [{**r, 'raw': 'yes' if found(pages[r['source_url']], r['quote']) else 'no',
            'route': routes[r['source_url']], 'text_sha256': hashlib.sha256(pages[r['source_url']].encode()).hexdigest()} for r in sample]
    with (HERE / 'audit30.csv').open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator='\n'); w.writeheader(); w.writerows(out)
    assert all(r['raw'] == 'yes' for r in out)
    print('random fresh raw re-check: 30 value rows; 0 errors; seed 20361106')

if __name__ == '__main__': main()
