"""Fetch known answers, check every packet quote, then independently re-fetch a seeded 30-value sample."""
import csv, random, hashlib
from unittest.mock import patch
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fetch import fetch, found
HERE = Path(__file__).resolve().parent

def main():
    frame = list(csv.DictReader((HERE / 'frame.csv').open()))
    verdicts = list(csv.DictReader((HERE / 'verdicts.csv').open()))
    assert len(frame) == len(verdicts) == 100, 'frame/verdict yield mismatch'
    assert len({r['org_id'] for r in frame}) == len({r['org_id'] for r in verdicts}) == 100
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
    for body in [b'You are being redirected... Javascript is required. Please enable javascript before you are allowed to see this page.',
                 b"prospira.us doesn't work properly without JavaScript enabled. Please enable it to continue. " * 2,
                 b'Request Rejected Network security system Dear user, the requested URL has been rejected for security reasons. ' * 2]:
        with patch('fetch.subprocess.run', return_value=SimpleNamespace(returncode=0, stdout=body)):
            try: fetch('https://example.invalid/challenge'); raise AssertionError('challenge accepted')
            except RuntimeError: pass
    print('3 redirect/JS-only/network-rejection controls refused on all routes')
    with patch('fetch.subprocess.run', side_effect=[SimpleNamespace(returncode=22, stdout=b''), SimpleNamespace(returncode=0, stdout=b'<html><body>' + b'Known plain route witness for the fallback control. ' * 4 + b'</body></html>')]):
        plain, _, route = fetch('https://example.invalid/plain')
        assert found(plain, 'Known plain route witness') and route.endswith(' [uncompressed]')
    print('compressed failure/plain success control passed')
    print('known answers: 4/4; injected fabricated quotes refused: 4/4')
    rows = list(csv.DictReader((HERE / 'inputs.csv').open()))
    assert all(r['verdict'] in ('VERIFIED', 'STILL_UNCERTAIN') for r in rows)
    candidates = len(rows)
    rows = [r for r in rows if r['verdict'] == 'VERIFIED']
    print('candidate values:', candidates, '; raw/application required:', len(rows), '; explicit unapplied holds:', candidates - len(rows))
    routes = {}
    def retrieve(url):
        text, _, route = fetch(url); routes[url] = route
        return url, text
    pages = dict(ThreadPoolExecutor(6).map(retrieve, sorted({r['source_url'] for r in rows})))
    for r in rows:
        assert found(pages[r['source_url']], r['quote']), r
        if r['verdict'] == 'VERIFIED' and r['field'] == 'certifications':
            assert found(pages[r['source_url']], r['cert_identity_quote']), r
            if r['cert_basis'] == 'dated_certificate':
                assert found(pages[r['source_url']], r['cert_expiry_quote']), r
            else:
                assert r['cert_basis'] == 'current_edition_page'
                assert r['value'] == 'iso_45001' and '2018' in r['quote']
                assert not r['cert_expiry']
    print('packet quotes:', len(rows), 'passed; zero unavailable pages')
    sample = random.Random(20361109).sample([r for r in rows if r['verdict'] == 'VERIFIED'], 30)
    pages = dict(ThreadPoolExecutor(6).map(retrieve, sorted({r['source_url'] for r in sample})))
    out = [{**r, 'raw': 'yes' if found(pages[r['source_url']], r['quote']) else 'no',
            'route': routes[r['source_url']], 'text_sha256': hashlib.sha256(pages[r['source_url']].encode()).hexdigest()} for r in sample]
    with (HERE / 'audit30.csv').open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator='\n'); w.writeheader(); w.writerows(out)
    assert all(r['raw'] == 'yes' for r in out)
    print('random fresh raw re-check: 30 value rows; 0 errors; seed 20361109')

if __name__ == '__main__': main()
