"""Named check: python3 -m pytest -q scripts/test_site_corpus.py."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import time
from unittest.mock import patch

import pytest
from site_corpus import Corpus, ROOT, Text, frame, on_page, url


def response(body='', code=200, location='', content_type='text/plain'):
    return dict(raw=body.encode(), code=code, location=location, content_type=content_type, exit=0, error='')


@pytest.mark.parametrize('quote,expected', [
    ('precision polymer molding', True),
    ('Précision-polymer MOLDING!', True),
    ('Précision—polymer MOLDING!', False),  # Legacy ASCII normalization joins this dash.
    ('polymer precision molding', False),
    ('precision invented polymer molding', False),
    ('precision molding', False),
    ('', None), ('!!!', None),
])
def test_calibrated_known_answer_and_mutations(quote, expected):
    assert on_page(quote, 'Our precision polymer molding serves industry.') is expected


def test_html_extraction():
    p = Text(); p.feed('<html><script>fabricated quote</script><style>hidden</style><p>Real &amp; public</p></html>')
    assert ' '.join(p.parts) == 'Real & public'


def test_cache_receipt_and_single_fetch(tmp_path):
    c = Corpus(tmp_path)
    calls = []
    def request(u, delay=1):
        calls.append(u)
        return response('User-agent: *\nDisallow: /private' if u.endswith('/robots.txt') else '<html>Precision polymer molding</html>', content_type='text/html' if not u.endswith('txt') else 'text/plain')
    with patch.object(c, 'request', side_effect=request):
        with ThreadPoolExecutor(max_workers=4) as pool:
            assert list(pool.map(lambda _: c.rawcheck('https://example.org/', 'precision polymer molding'), range(4))) == ['yes'] * 4
        assert c.rawcheck('https://example.org/', 'fabricated quote') == 'no'
        assert c.fetch('https://example.org/private')['status'] == 'ROBOTS_BLOCKED'
    assert calls == ['https://example.org/robots.txt', 'https://example.org/']
    r = c.cached('https://example.org/')
    assert r['sha256'] == hashlib.sha256((tmp_path / r['raw_file']).read_bytes()).hexdigest()
    assert r['final_url'] == 'https://example.org/' and r['fetched_at']
    (tmp_path / r['raw_file']).write_text('tamper')
    with pytest.raises(ValueError, match='hash mismatch'): c.cached('https://example.org/')


@pytest.mark.parametrize('code', [403, 429, 500, 0])
def test_unavailable_robots_fails_closed(tmp_path, code):
    c = Corpus(tmp_path)
    with patch.object(c, 'request', return_value=response(code=code)) as request:
        assert c.rawcheck('https://example.org/', 'some quote') == 'unfetchable'
        assert request.call_count == 1


def test_redirect_checks_destination_robots(tmp_path):
    c = Corpus(tmp_path); seen = []
    def request(u, delay=1):
        seen.append(u)
        if u == 'https://other.org/robots.txt': return response('User-agent: *\nDisallow: /')
        if u.endswith('/robots.txt'): return response(code=404)
        return response(code=302, location='https://other.org/private')
    with patch.object(c, 'request', side_effect=request):
        assert c.fetch('https://example.org/')['status'] == 'ROBOTS_BLOCKED'
    assert seen == ['https://example.org/robots.txt', 'https://example.org/', 'https://other.org/robots.txt']


def test_jina_strips_wrapper_and_walls(tmp_path):
    c = Corpus(tmp_path)
    def request(u, delay=1):
        if u.endswith('/robots.txt'): return response(code=404)
        if u.startswith('https://r.jina.ai/'):
            return response('Title: NOT EVIDENCE\nURL Source: https://example.org/\nMarkdown Content:\nReal polymer molding')
        return response('verify you are human')
    with patch.object(c, 'request', side_effect=request):
        assert c.rawcheck('https://example.org/', 'real polymer molding') == 'yes'
        assert c.rawcheck('https://example.org/', 'NOT EVIDENCE') == 'no'
        assert c.cached('https://example.org/')['route'] == 'jina'


def test_discovery_six_types_and_sitemap(tmp_path):
    c = Corpus(tmp_path); seen = []
    links = '<html>' + ''.join(f'<a href="/{v}">{v}</a>' for v in ['about', 'locations', 'news', 'quality', 'markets', 'products', 'about-long']) + '</html>'
    def request(u, delay=1):
        seen.append(u)
        if u.endswith('/robots.txt'): return response(code=404)
        if u.endswith('/sitemap.xml'): return response('<urlset><url><loc>https://evil.org/about</loc></url></urlset>')
        return response(links, content_type='text/html')
    with patch.object(c, 'request', side_effect=request):
        assert set(c.crawl('https://example.org/').values()) == {'ok'}
    assert len(seen) == 9
    assert all('evil.org' not in u for u in seen)


def test_limits_and_repo_boundary(tmp_path):
    with pytest.raises(ValueError, match='outside'): Corpus(ROOT / 'build/cache')
    with pytest.raises(ValueError): url('file:///tmp/secret')
    with pytest.raises(ValueError): url('https://user:pass@example.org')
    c = Corpus(tmp_path); starts = []
    def run(args, **kwargs):
        starts.append(time.monotonic())
        Path(args[args.index('-o') + 1]).write_text('known page')
        return subprocess.CompletedProcess(args, 0, '200', '')
    with patch('site_corpus.subprocess.run', side_effect=run):
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(c.request, ['https://example.org/a', 'https://example.org/b']))
    assert starts[1] - starts[0] >= .99


def test_frame_priority(tmp_path):
    d = tmp_path / 'data'; d.mkdir()
    (d / 'sites_OH.csv').write_text('org_id,state,county\nORG-1,OH,Summit\n')
    (d / 'organizations_OH.csv').write_text('org_id,status,website,tier1_qualifier\nORG-1,active,https://a.org,x\nORG-2,active,https://b.org,x\nORG-3,active,https://c.org,\nORG-4,closed,https://d.org,\n')
    assert [r['group'] for r in frame(tmp_path)] == ['PIC18', 'Tier1', 'active']


def test_robots_www_redirect_and_page_identity(tmp_path):
    c = Corpus(tmp_path)
    def request(u, delay=1):
        if u == 'https://example.org/robots.txt': return response(code=301, location='https://www.example.org/robots.txt')
        if u.endswith('/robots.txt'): return response('User-agent: *\nAllow: /')
        if u == 'https://example.org/old': return response(code=301, location='https://example.org/new')
        return response('Known polymer page')
    with patch.object(c, 'request', side_effect=request):
        assert c.rawcheck('https://example.org/old', 'known polymer page') == 'wrong_page'
        assert c.rawcheck('https://example.org/new', 'known polymer page') == 'yes'


def test_global_eight_slots_across_instances(tmp_path):
    import threading
    mutex = threading.Lock()
    active, maximum = 0, 0
    def use(_):
        nonlocal active, maximum
        with Corpus(tmp_path).slot():
            with mutex:
                active += 1; maximum = max(maximum, active)
            time.sleep(.05)
            with mutex: active -= 1
    with ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(use, range(12)))
    assert maximum == 8
