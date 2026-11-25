"""Named check: python3 -m unittest discover -s scripts -p 'test_site_corpus.py'."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
import subprocess
import time
from unittest.mock import patch

import tempfile
import unittest
from site_corpus import Corpus, ROOT, Text, challenged, frame, linkedin_company_page, on_page, url


def response(body='', code=200, location='', content_type='text/plain'):
    return dict(raw=body.encode(), code=code, location=location, content_type=content_type, exit=0, error='')


class SiteCorpusTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp_path = Path(directory.name)
        # No unit test launches Chrome; the browser path is exercised by tasks/browser-fetch-2026-11-25/check.py.
        patcher = patch.object(Corpus, 'browser', return_value=dict(code=403, raw=b'<html><title>Just a moment...</title></html>', content_type='text/html', exit=0, error='', final_url='https://example.org/', flags=set(), blocked=''))  # Chrome ran and the check stayed
        patcher.start(); self.addCleanup(patcher.stop)

    def test_calibrated_known_answer_and_mutations(self):
        for quote, expected in [
            ('precision polymer molding', True),
            ('Précision-polymer MOLDING!', True),
            ('Précision—polymer MOLDING!', False),  # Legacy ASCII normalization joins this dash.
            ('polymer precision molding', False),
            ('precision invented polymer molding', False),
            ('precision molding', False),
            ('', None), ('!!!', None),
        ]:
            with self.subTest(quote=quote):
                self.assertIs(on_page(quote, 'Our precision polymer molding serves industry.'), expected)


    def test_html_extraction(self):
        p = Text(); p.feed('<html><script>fabricated quote</script><style>hidden</style><p>Real &amp; public</p></html>')
        assert ' '.join(p.parts) == 'Real & public'


    def test_cache_receipt_and_single_fetch(self):
        tmp_path = self.tmp_path
        c = Corpus(tmp_path)
        calls = []
        def request(u, delay=1):
            calls.append(u)
            return response('User-agent: *\nDisallow: /private' if u.endswith('/robots.txt') else '<html>Precision polymer molding</html>', content_type='text/html' if not u.endswith('txt') else 'text/plain')
        with patch.object(c, 'request', side_effect=request):
            with ThreadPoolExecutor(max_workers=4) as pool:
                assert list(pool.map(lambda _: c.rawcheck('https://example.org/', 'precision polymer molding'), range(4))) == ['yes'] * 4
            assert c.rawcheck('https://example.org/', 'fabricated quote') == 'no'
            private = c.fetch('https://example.org/private')
            assert private['status'] == 'ok' and private['robots_disallowed'] == 'yes'  # a Disallow is receipted, not obeyed
        assert calls == ['https://example.org/robots.txt', 'https://example.org/', 'https://example.org/private']
        r = c.cached('https://example.org/')
        assert r['sha256'] == hashlib.sha256((tmp_path / r['raw_file']).read_bytes()).hexdigest()
        assert r['final_url'] == 'https://example.org/' and r['fetched_at']
        (tmp_path / r['raw_file']).write_text('tamper')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'): c.cached('https://example.org/')


    def test_unreadable_robots_no_longer_blocks(self):
        for code in (403, 429, 500, 0):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as directory:
                c = Corpus(directory)
                with patch.object(c, 'request', side_effect=lambda u, delay=1: response(code=code) if u.endswith('/robots.txt') else response('Real polymer molding')) as request:
                    assert c.rawcheck('https://example.org/', 'real polymer molding') == 'yes'
                    assert request.call_count == 2
                    assert c.cached('https://example.org/')['robots_disallowed'] == 'unreadable'

    def test_crawl_delay_still_honored(self):
        c = Corpus(self.tmp_path); delays = []
        def request(u, delay=1):
            if not u.endswith('/robots.txt'): delays.append(delay)
            return response('User-agent: *\nCrawl-delay: 7\nDisallow: /' if u.endswith('/robots.txt') else 'Real polymer molding')
        with patch.object(c, 'request', side_effect=request):
            assert c.fetch('https://example.org/')['robots_disallowed'] == 'yes'
        assert delays == [7]

    def test_stale_blocked_receipts_are_refetched(self):
        c = Corpus(self.tmp_path)
        for status in ('ROBOTS_BLOCKED', 'DOMAIN_BLOCKED'):
            with self.subTest(status=status):
                target = f'https://example.org/{status}'
                c.save(target, {}, status, target, 'direct')
                assert c.cached(target) is None

    def test_linkedin_company_pages_only(self):
        c = Corpus(self.tmp_path)
        for target in ('https://www.linkedin.com/in/someone', 'https://linkedin.com/pub/someone/1/2/3', 'https://jobs.linkedin.com/',
                       'https://lnkd.in/123', 'https://linkedin%2ecom/', 'https://www.linkedin.com/company/acme/people',
                       'https://www.linkedin.com/%69n/someone', 'https://www.linkedin.com/company/../in/someone',
                       'https://r.jina.ai/https://linkedin.com/company/acme'):
            with self.subTest(target=target), patch.object(c, 'request', return_value=response(code=404)) as request:
                receipt = c.fetch(target)
                request.assert_not_called()
                self.assertEqual(receipt['status'], 'DOMAIN_BLOCKED')
        for target in ('https://linkedin.com/company/acme', 'https://WWW.LinkedIn.com./company/acme/about/', 'https://www.linkedin.com/showcase/acme-x'):
            with self.subTest(target=target):
                assert linkedin_company_page(target)
                with patch.object(c, 'request', side_effect=lambda u, delay=1: response(code=404) if u.endswith('/robots.txt') else response('<html><section data-test-id="about-us"><p data-test-id="about-us__description">Acme molds polymer parts</p></section></html>', content_type='text/html')):
                    assert c.fetch(target)['status'] == 'ok'

    def test_linkedin_signin_wall_is_its_own_status(self):
        c = Corpus(self.tmp_path)
        def request(u, delay=1):
            if u.endswith('/robots.txt'): return response(code=404)
            return response(code=302, location='https://www.linkedin.com/authwall?trk=x')
        with patch.object(c, 'request', side_effect=request):
            assert c.fetch('https://www.linkedin.com/company/acme')['status'] == 'SIGNIN_WALL'

    def test_challenge_detector(self):
        assert challenged(200, '<html><title>Just a moment...</title></html>')
        assert challenged(403, '<html><title>x</title><div class="cf-challenge"></div></html>')
        assert challenged(200, '<html><div class="g-recaptcha"></div><p>short</p></html>')
        assert not challenged(200, '<html><div class="g-recaptcha"></div><p>' + 'word ' * 80 + '</p></html>')  # a contact form is not a wall
        assert not challenged(404, '<html><title>Not found</title></html>')

    def test_unavailable_browser_is_its_own_cached_outcome(self):
        c = Corpus(self.tmp_path)
        gone = dict(unavailable=True, error='PLAYWRIGHT_UNAVAILABLE', code=0, raw=b'', exit=127, final_url='', flags=set(), blocked='')
        with patch.object(Corpus, 'browser', return_value=gone) as browser, patch.object(c, 'request', side_effect=lambda u, delay=1: response(code=404) if u.endswith('/robots.txt') else response('<html><title>Just a moment...</title></html>', code=403, content_type='text/html')) as request:
            first = c.fetch('https://example.org/x'); n = request.call_count
            second = c.fetch('https://example.org/x')
        assert first['status'] == second['status'] == 'BROWSER_UNAVAILABLE' and browser.call_count == 1 and request.call_count == n
        assert len((self.tmp_path / 'manual-bot-check.csv').read_text().strip().split('\n')) == 2  # header and one row

    def test_challenge_page_is_manual_never_ok(self):
        c = Corpus(self.tmp_path)
        for n, (code, html) in enumerate([(403, '<html><title>Just a moment...</title></html>'), (200, '<html><title>Security check</title><div class="g-recaptcha"></div></html>')]):
            with self.subTest(code=code), patch.object(c, 'request', side_effect=lambda u, delay=1: response(code=404) if u.endswith('/robots.txt') else response(html, code=code, content_type='text/html')):
                r = c.fetch(f'https://example.org/{n}')
                assert r['status'] == 'BOT_CHECK_MANUAL'
                assert f'https://example.org/{n}' in (self.tmp_path / 'manual-bot-check.csv').read_text()

    def test_linkedin_link_remains_navigation(self):
        link = 'https://www.linkedin.com/company/acme/'
        parser = Text()
        parser.feed(f'<a href="{link}">LinkedIn</a>')
        self.assertEqual(parser.links, [link])

    def test_redirect_to_linkedin_stops_before_destination_request(self):
        c = Corpus(self.tmp_path)
        def request_page(target, delay=1):
            if target.endswith('/robots.txt'):
                return response(code=404)
            if target == 'https://example.org/':
                return response(code=302, location='//www.linkedin.com/company/acme')
            return response('LinkedIn content')
        with patch.object(c, 'request', side_effect=request_page) as request:
            receipt = c.fetch('https://example.org/')
        self.assertEqual(request.call_count, 2)
        self.assertEqual(receipt['status'], 'DOMAIN_BLOCKED')

    def test_redirect_destination_robots_is_receipted_not_obeyed(self):
        tmp_path = self.tmp_path
        c = Corpus(tmp_path); seen = []
        def request(u, delay=1):
            seen.append(u)
            if u == 'https://other.org/robots.txt': return response('User-agent: *\nDisallow: /')
            if u.endswith('/robots.txt'): return response(code=404)
            return response('page') if u == 'https://other.org/private' else response(code=302, location='https://other.org/private')
        with patch.object(c, 'request', side_effect=request):
            receipt = c.fetch('https://example.org/')
        assert receipt['robots_disallowed'] == 'yes'  # the destination hop would have been disallowed
        assert seen == ['https://example.org/robots.txt', 'https://example.org/', 'https://other.org/robots.txt', 'https://other.org/private']


    def test_jina_strips_wrapper_and_walls(self):
        tmp_path = self.tmp_path
        c = Corpus(tmp_path)
        def request(u, delay=1):
            if u.endswith('/robots.txt'): return response(code=404)
            if u.startswith('https://r.jina.ai/'):
                return response('Title: NOT EVIDENCE\nURL Source: https://example.org/\nMarkdown Content:\nReal polymer molding')
            return response(code=500)  # a bot-check page never goes to the Jina proxy (see test_challenge_without_browser_is_manual)
        with patch.object(c, 'request', side_effect=request):
            assert c.rawcheck('https://example.org/', 'real polymer molding') == 'yes'
            assert c.rawcheck('https://example.org/', 'NOT EVIDENCE') == 'no'
            assert c.cached('https://example.org/')['route'] == 'jina'


    def test_discovery_six_types_and_sitemap(self):
        tmp_path = self.tmp_path
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


    def test_limits_and_repo_boundary(self):
        tmp_path = self.tmp_path
        with self.assertRaisesRegex(ValueError, 'outside'): Corpus(ROOT / 'build/cache')
        with self.assertRaises(ValueError): url('file:///tmp/secret')
        with self.assertRaises(ValueError): url('https://user:pass@example.org')
        c = Corpus(tmp_path); starts = []
        def run(args, **kwargs):
            starts.append(time.monotonic())
            Path(args[args.index('-o') + 1]).write_text('known page')
            return subprocess.CompletedProcess(args, 0, '200', '')
        with patch('site_corpus.subprocess.run', side_effect=run):
            with ThreadPoolExecutor(max_workers=2) as pool:
                list(pool.map(c.request, ['https://example.org/a', 'https://example.org/b']))
        assert starts[1] - starts[0] >= .99


    def test_frame_priority(self):
        tmp_path = self.tmp_path
        d = tmp_path / 'data'; d.mkdir()
        (d / 'sites_OH.csv').write_text('org_id,state,county\nORG-1,OH,Summit\n')
        (d / 'organizations_OH.csv').write_text('org_id,status,website,tier1_qualifier\nORG-1,active,https://a.org,x\nORG-2,active,https://b.org,x\nORG-3,active,https://c.org,\nORG-4,closed,https://d.org,\n')
        assert [r['group'] for r in frame(tmp_path)] == ['PIC18', 'Tier1', 'active']


    def test_robots_www_redirect_and_page_identity(self):
        tmp_path = self.tmp_path
        c = Corpus(tmp_path)
        def request(u, delay=1):
            if u == 'https://example.org/robots.txt': return response(code=301, location='https://www.example.org/robots.txt')
            if u.endswith('/robots.txt'): return response('User-agent: *\nAllow: /')
            if u == 'https://example.org/old': return response(code=301, location='https://example.org/new')
            return response('Known polymer page')
        with patch.object(c, 'request', side_effect=request):
            assert c.rawcheck('https://example.org/old', 'known polymer page') == 'wrong_page'
            assert c.rawcheck('https://example.org/new', 'known polymer page') == 'yes'


    def test_global_eight_slots_across_instances(self):
        tmp_path = self.tmp_path
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


    def test_specific_bot_rules_not_browser_prefix(self):
        tmp_path = self.tmp_path
        c = Corpus(tmp_path)
        robots = 'User-agent: AtlasSiteCorpus\nDisallow: /\n\nUser-agent: *\nAllow: /'
        with patch.object(c, 'request', side_effect=lambda u, delay=1: response(robots) if u.endswith('/robots.txt') else response('page')):
            assert c.fetch('https://example.org/')['robots_disallowed'] == 'yes'
        with patch.object(c, 'request', side_effect=lambda u, delay=1: response('User-agent: *\nAllow: /') if u.endswith('/robots.txt') else response('page')):
            assert c.fetch('https://example.net/')['robots_disallowed'] == 'no'


    def test_redirect_limit_cannot_fallback_past_policy(self):
        tmp_path = self.tmp_path
        c = Corpus(tmp_path); seen = []
        def request(u, delay=1):
            seen.append(u)
            if u.endswith('/robots.txt'): return response(code=404)
            n = int(u.rsplit('/', 1)[-1])
            return response(code=302, location='https://deny.org/private' if n == 5 else f'https://example.org/{n+1}')
        with patch.object(c, 'request', side_effect=request):
            assert c.fetch('https://example.org/0')['status'] == 'FETCH_FAILED'
        assert all('r.jina.ai' not in x and 'deny.org' not in x for x in seen)


    def test_proxy_cannot_mint_another_pages_quote(self):
        tmp_path = self.tmp_path
        c = Corpus(tmp_path)
        def request(u, delay=1):
            if u.endswith('/robots.txt'): return response(code=404)
            if u.startswith('https://r.jina.ai/'):
                return response('URL Source: https://deny.org/private\nMarkdown Content:\nForbidden quote')
            return response(code=403)
        with patch.object(c, 'request', side_effect=request):
            assert c.rawcheck('https://example.org/', 'Forbidden quote') == 'wrong_page'
            assert c.cached('https://example.org/')['status'] == 'WRONG_PAGE'


if __name__ == "__main__":
    unittest.main()
