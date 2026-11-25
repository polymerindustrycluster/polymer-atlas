#!/usr/bin/env python3
"""Planted cases for the headed-Chrome retry and the HTTP/1.1 transport fallback in scripts/site_corpus.py, on top of every
earlier case of tasks/robots-off-fetch-2026-11-25/check.py (robots off, LinkedIn company pages, privacy exclusion, robots.txt
never on disk).

Usage: python3 check.py SCRIPTS_DIR [--real-browser]
  SCRIPTS_DIR     the scripts/ directory whose site_corpus.py is judged (the head, a copy of origin/main, or of 5dd966d9).
  --real-browser  also drives real headed Chrome against a local fixture server (HEADED CHROME OPENS WINDOWS ON THIS MAC).
                  Needs `uv run --with playwright` and the sandbox off; with no Chrome the cases FAIL, never skip.
Each case prints PASS or FAIL and the check exits 1 if any case fails. Every case asserts behaviour.
"""
import sys, tempfile
from pathlib import Path
from unittest.mock import patch

scripts = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(scripts))
import site_corpus as sc  # noqa: E402

RESULTS = []
REAL_BROWSER = getattr(sc.Corpus, 'browser', None)
sc.Corpus.browser = lambda self, target, delay=1, *a, **k: dict(unavailable=True, error='PLAYWRIGHT_UNAVAILABLE', code=0, raw=b'', exit=127, final_url=target, flags=set(), blocked='')  # mocked cases never launch Chrome
PAGE = '<html><body><p>' + 'Real polymer molding. ' * 20 + '</p></body></html>'
WALL = '<html><title>Just a moment...</title><body>Checking your browser</body></html>'
PUZZLE = '<html><title>Security check</title><body><div class="g-recaptcha"></div></body></html>'
SENTINEL = 'SENTINEL-PERSONAL-DATA-7731'
SENT_PAGE = '<html><body><p>' + ('Real polymer molding ' + SENTINEL + '. ') * 20 + '</p></body></html>'
FORM = '<html><form action="/c"><input name=n></form><p>' + SENTINEL + '</p></html>'  # form-only page: personal data by the crawl's rule


def resp(body='', code=200, location=''):
    return dict(raw=body.encode(), code=code, location=location, content_type='text/html', exit=0, error='')


def case(fn):
    try:
        with tempfile.TemporaryDirectory() as d:
            fn(sc.Corpus(d), Path(d))
        RESULTS.append((True, fn.__name__))
        print('PASS ' + fn.__name__, flush=True)
    except Exception as e:  # AssertionError or anything else is a FAIL with its reason
        RESULTS.append((False, fn.__name__))
        print(f'FAIL {fn.__name__} - {type(e).__name__}: {e}'[:230], flush=True)
    return fn


def serve(robots, page):
    return lambda u, delay=1: robots if u.endswith('/robots.txt') else page


def cache_text(tmp):
    return b''.join(f.read_bytes() for f in tmp.iterdir() if f.is_file())


def no_sentinel(tmp):
    assert SENTINEL.encode() not in cache_text(tmp), 'the excluded body reached the cache'


@case
def robots_disallowed_url_is_fetched_and_receipted_yes(c, tmp):
    with patch.object(c, 'request', side_effect=serve(resp('User-agent: *\nDisallow: /'), resp(PAGE))):
        r = c.fetch('https://example.org/private')
    assert r['status'] == 'ok', f"status {r['status']}"
    assert r.get('robots_disallowed') == 'yes', f"robots_disallowed {r.get('robots_disallowed')!r}"


@case
def unreadable_robots_is_not_disallow_all(c, tmp):
    with patch.object(c, 'request', side_effect=serve(resp(code=500), resp(PAGE))):
        r = c.fetch('https://example.org/')
    assert r['status'] == 'ok', f"status {r['status']}"
    assert r.get('robots_disallowed') == 'unreadable', f"robots_disallowed {r.get('robots_disallowed')!r}"


@case
def crawl_delay_is_still_honored(c, tmp):
    delays = []
    def request(u, delay=1):
        if not u.endswith('/robots.txt'): delays.append(delay)
        return resp('User-agent: *\nCrawl-delay: 7\nDisallow: /') if u.endswith('/robots.txt') else resp(PAGE)
    with patch.object(c, 'request', side_effect=request):
        r = c.fetch('https://example.org/')
    assert r['status'] == 'ok' and delays == [7], f"status {r['status']} delays {delays}"


@case
def intermediate_redirect_hop_robots_is_receipted(c, tmp):
    def request(u, delay=1):
        if u == 'https://b.example.net/robots.txt': return resp('User-agent: *\nDisallow: /mid')
        if u.endswith('/robots.txt'): return resp(code=404)
        if u == 'https://a.example.org/': return resp(code=302, location='https://b.example.net/mid')
        if u == 'https://b.example.net/mid': return resp(code=302, location='https://c.example.com/end')
        return resp(PAGE)
    with patch.object(c, 'request', side_effect=request):
        r = c.fetch('https://a.example.org/')
    assert r['status'] == 'ok' and r.get('robots_disallowed') == 'yes', f"status {r['status']} robots_disallowed {r.get('robots_disallowed')!r} (the disallowed hop sat between two allowed URLs)"


@case
def stale_blocked_receipt_is_refetched(c, tmp):
    target = 'https://example.org/old'
    c.save(target, {}, 'ROBOTS_BLOCKED', target, 'direct')
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(PAGE))):
        r = c.fetch(target)
    assert r['status'] == 'ok', f"status {r['status']} (an old ROBOTS_BLOCKED receipt kept answering)"


@case
def linkedin_company_page_is_fetched_logged_out_without_cookies(c, tmp):
    argv = []
    def run(cmd, **kw):
        argv.append(cmd)
        return type('P', (), dict(stdout='200', stderr='', returncode=0))()
    target = 'https://www.linkedin.com/company/acme'
    with patch.object(sc.subprocess, 'run', side_effect=run):
        c.request(target)
    assert argv, 'no request was made for a LinkedIn company page'
    flat = ' '.join(argv[0]).lower().split()
    assert '-q' in flat and not any(f in flat for f in ('-b', '--cookie', '--cookie-jar', '-c', '-h', '--header', '-u', '--user')), flat  # -q: no curlrc
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp('<html><section data-test-id="about-us"><p data-test-id="about-us__description">' + 'About us polymer molding. ' * 10 + '</p></section></html>'))):
        r = c.fetch(target)
    assert r['status'] == 'ok', f"status {r['status']}"


@case
def linkedin_personal_profiles_and_staff_lists_refuse_at_every_hop(c, tmp):
    for target in ('https://www.linkedin.com/in/someone', 'https://www.linkedin.com/pub/someone/1/2/3', 'https://www.linkedin.com/%69n/someone',
                   'https://www.linkedin.com/company/acme/people', 'https://lnkd.in/x'):
        with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(PAGE))) as request:
            r = c.fetch(target)
        assert r['status'] != 'ok' and not request.call_count, f'{target}: status {r["status"]}, requests {request.call_count}'
    for start in ('https://www.linkedin.com/company/acme', 'https://example.org/'):  # a hop to a profile, from LinkedIn or from an own site
        def request(u, delay=1, start=start):
            if u.endswith('/robots.txt'): return resp(code=404)
            return resp(code=302, location='https://www.linkedin.com/in/someone') if u == start else resp(SENTINEL)
        with patch.object(c, 'request', side_effect=request) as req:
            r = c.fetch(start)
        assert r['status'] == 'DOMAIN_BLOCKED' and 'https://www.linkedin.com/in/someone' not in [x.args[0] for x in req.call_args_list], f'{start}: status {r["status"]}'
    no_sentinel(tmp)


@case
def challenge_page_is_manual_never_ok(c, tmp):
    for n, (code, html) in enumerate([(403, WALL), (200, PUZZLE), (503, WALL), (999, WALL)]):
        with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(html, code=code))):
            r = c.fetch(f'https://example.org/{n}')
        assert r['status'] == 'BOT_CHECK_MANUAL', f'HTTP {code}: status {r["status"]}'
        assert f'https://example.org/{n}' in (tmp / 'manual-bot-check.csv').read_text(), f'HTTP {code}: not on the manual list'


for status in ('ok', 'FETCH_FAILED', 'BOT_CHECK_MANUAL', 'WRONG_PAGE', 'DOMAIN_BLOCKED'):
    def privacy(c, tmp, status=status):
        c.save('https://example.org/contact', dict(resp(FORM), raw=FORM.encode()), status, 'https://example.org/contact', 'direct')
        c.save('https://example.org/x', resp(PAGE.replace('Real', SENTINEL)), status, 'https://example.org/our-team/', 'direct')  # staff-directory path
        no_sentinel(tmp)
    privacy.__name__ = f'privacy_exclusion_before_storing_status_{status}'
    case(privacy)


@case
def privacy_exclusion_holds_through_fetch_for_ok_and_failed(c, tmp):
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(FORM))):
        assert c.fetch('https://example.org/contact')['status'] != 'ok'
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(FORM, code=500))):
        assert c.fetch('https://example.org/contact2')['status'] != 'ok'
    no_sentinel(tmp)


def jina(body):
    return lambda u, delay=1: resp(code=404) if u.endswith('/robots.txt') else (resp(body) if u.startswith('https://r.jina.ai/') else resp(code=500))


@case
def form_page_is_never_forwarded_to_the_reader(c, tmp):
    reader = 'Title: Contact\nURL Source: https://example.org/contact\nMarkdown Content:\n' + SENTINEL + ' ' + 'reader text ' * 40
    def request(u, delay=1):
        if u.endswith('/robots.txt'): return resp(code=404)
        return resp(reader) if u.startswith('https://r.jina.ai/') else resp(FORM, code=500)
    with patch.object(c, 'request', side_effect=request) as req:
        r = c.fetch('https://example.org/contact')
    assert r['status'] != 'ok' and not any('r.jina.ai' in x.args[0] for x in req.call_args_list), f"status {r['status']}, reader called"
    no_sentinel(tmp)


@case
def robots_txt_body_is_never_written_to_disk(c, tmp):
    import hashlib, json
    bodies = {'html form': FORM.encode(), 'bom': b'\xef\xbb\xbf' + FORM.encode(), 'space then bom': b'  \n\xef\xbb\xbf' + FORM.encode(),
              'plain rules with a comment': ('User-agent: *\nDisallow: /private\n# ' + SENTINEL).encode(), 'binary': b'\x00\x01' + SENTINEL.encode()}
    for n, (name, body) in enumerate(bodies.items()):
        host = f'https://h{n}.example.org/'
        with patch.object(c, 'request', side_effect=serve(dict(resp(), raw=body), resp(PAGE))):
            r = c.fetch(host)
            assert r['status'] == 'ok', f'{name}: status {r["status"]}'
        no_sentinel(tmp)
        receipts = [json.loads(f.read_text()) for f in tmp.glob('robots-*.json')]
        assert any(x['url'] == host + 'robots.txt' and x['sha256'] == hashlib.sha256(body).hexdigest() and x['http_status'] == 200 and x['status'] == 'ok' for x in receipts), f'{name}: no robots receipt with the body hash'
        assert not any(f.read_bytes() == body for f in tmp.iterdir() if f.is_file()), f'{name}: the body is on disk'
    with patch.object(c, 'request', side_effect=serve(dict(resp(), raw=bodies['plain rules with a comment']), resp(PAGE))):
        assert c.fetch('https://h3.example.org/private')['robots_disallowed'] == 'yes'  # still parsed, in memory


@case
def robots_curl_command_writes_no_file(c, tmp):
    argv = []
    def run(cmd, **kw):
        argv.append(cmd)
        return type('P', (), dict(stdout=b'HTTP/1.1 200 OK\r\n\r\nUser-agent: *\n\n200', stderr=b'', returncode=0))()
    with patch.object(sc.subprocess, 'run', side_effect=run):
        r = c.request('https://example.org/robots.txt')
    cmd = argv[0]
    assert cmd[cmd.index('-o') + 1] == '-' and '-D' not in cmd and r['code'] == 200 and r['raw'] == b'User-agent: *\n', f'robots curl command {cmd}'


@case
def real_curl_never_writes_a_robots_body_to_any_file(c, tmp):
    import http.server, threading, time, os
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.send_header('Content-Type', 'text/html'); self.end_headers()
            if self.path == '/robots.txt':
                self.wfile.write(FORM.encode()); self.wfile.flush(); time.sleep(1.5)  # curl holds the body for 1.5 s: a temp file would show
            else:
                self.wfile.write(PAGE.encode())
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    sys_tmp = Path(tempfile.mkdtemp()); seen, stop = [], threading.Event()
    def watch():
        while not stop.is_set():
            for root in (tmp, sys_tmp):
                for f in root.rglob('*'):
                    try:
                        if f.is_file() and SENTINEL.encode() in f.read_bytes(): seen.append(str(f))
                    except OSError: pass
            time.sleep(0.01)
    t = threading.Thread(target=watch); t.start()
    old = os.environ.get('TMPDIR'); os.environ['TMPDIR'] = str(sys_tmp)  # curl and Python temp files would land here
    try:
        r = c.fetch(f'http://127.0.0.1:{srv.server_port}/')
    finally:
        stop.set(); t.join(); srv.shutdown()
        if old is None: os.environ.pop('TMPDIR')
        else: os.environ['TMPDIR'] = old
    assert r['status'] == 'ok' and r['robots_disallowed'] in ('no', 'yes'), f"status {r['status']}"
    assert not seen, f'the robots body was on disk at: {seen[:2]}'
    assert not [f for f in sys_tmp.rglob('*') if f.is_file()], 'files left in the temp dir'
    no_sentinel(tmp)


@case
def reader_bot_check_is_manual_never_ok(c, tmp):
    for n, body in enumerate(['Title: Security check\nURL Source: https://example.org/{n}\nMarkdown Content:\nComplete this CAPTCHA to proceed.',
                              'Title: Just a moment...\nURL Source: https://example.org/{n}\nMarkdown Content:\n' + 'Checking your browser before accessing the site. ' * 3]):
        with patch.object(c, 'request', side_effect=jina(body.replace('{n}', str(n)))):
            r = c.fetch(f'https://example.org/{n}')
        assert r['status'] == 'BOT_CHECK_MANUAL' and f'https://example.org/{n}' in (tmp / 'manual-bot-check.csv').read_text(), f'reader body {n}: status {r["status"]}'


LI_PAGE = ('<html><head><script type="application/ld+json">{"@graph":[{"@type":"Organization","name":"Acme Polymers","description":"Polymer molder",'
           '"foundingDate":"1986","address":{"streetAddress":"1 Main St","addressLocality":"Akron","addressRegion":"Ohio","postalCode":"44301","member":{"name":"%(s)s"}},'
           '"department":{"employee":{"name":"%(s)s"}},"employee":[{"name":"%(s)s"}]},{"@type":"Article","author":{"name":"%(s)s"}}]}</script>'
           '<script>var people="%(s)s"</script></head><body>'
           '<section data-test-id="about-us"><h2>About us</h2><p data-test-id="about-us__description">Acme molds polymer parts for medical devices.</p><dl>'
           '<div data-test-id="about-us__website"><dt>Website</dt><dd><a href="https://www.linkedin.com/redir/x">http://www.acme.example</a><p class="hidden">External link %(s)s</p></dd></div>'
           '<div data-test-id="about-us__industry"><dt>Industry</dt><dd>Plastics Manufacturing</dd></div>'
           '<div data-test-id="about-us__size"><dt>Company size</dt><dd>51-200 employees</dd></div>'
           '<div data-test-id="about-us__headquarters"><dt>Headquarters</dt><dd>Akron, Ohio</dd></div>'
           '<div data-test-id="about-us__foundedOn"><dt>Founded</dt><dd>1986</dd></div>'
           '<div data-test-id="about-us__specialties"><dt>Specialties</dt><dd>Injection molding, thermoforming</dd></div>'
           '<div data-test-id="about-us__organizationType"><dt>Type</dt><dd>%(s)s Privately Held</dd></div></dl></section>'
           '<section data-test-id="employees-at"><ul><li>%(s)s</li></ul></section><div class="anything-new">%(s)s</div></body></html>') % dict(s=SENTINEL)


@case
def linkedin_company_page_stores_only_the_allowlisted_extract(c, tmp):
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(LI_PAGE))):
        r = c.fetch('https://www.linkedin.com/company/acme')
    assert r['status'] == 'ok', f"status {r['status']}"
    stored = (tmp / r['raw_file']).read_bytes()
    import hashlib, json
    got = json.loads(stored)
    assert got['name'] == 'Acme Polymers' and got['specialties'] == 'Injection molding, thermoforming' and got['industry'] == 'Plastics Manufacturing', got
    assert got['company_size'] == '51-200 employees' and got['headquarters'] == 'Akron, Ohio' and got['founded'] == '1986' and got['website'] == 'http://www.acme.example', got
    assert got['address'] == {'streetAddress': '1 Main St', 'addressLocality': 'Akron', 'addressRegion': 'Ohio', 'postalCode': '44301'}, got['address']
    assert set(got) <= {'source_url', 'name', 'description', 'website', 'industry', 'company_size', 'headquarters', 'address', 'founded', 'specialties'}, set(got)
    assert b'<' not in stored and r['sha256'] == hashlib.sha256(stored).hexdigest() and r['url'] and r['fetched_at'] and r['final_url'], 'not a plain extract with its receipt'
    no_sentinel(tmp)


def plant_legacy_linkedin(tmp, target='https://www.linkedin.com/company/acme'):
    """A receipt written before the extract-only rule: the raw company page and its text, with a valid hash receipt."""
    import hashlib, json
    raw = LI_PAGE.encode(); text = LI_PAGE.replace('<', ' <').encode()
    rf, tf = hashlib.sha256(raw).hexdigest() + '.raw', hashlib.sha256(text).hexdigest() + '.txt'
    (tmp / rf).write_bytes(raw); (tmp / tf).write_bytes(text)
    r = dict(url=target, status='ok', http_status=200, final_url=target, route='direct', fetched_at='2026-11-20T00:00:00+00:00', sha256=hashlib.sha256(raw).hexdigest(),
             raw_file=rf, text_file=tf, text_sha256=hashlib.sha256(text).hexdigest(), extraction_version=3, error='')
    (tmp / (sc.key(target) + '.json')).write_text(json.dumps(r))


@case
def legacy_linkedin_page_is_never_replayed_and_is_purged(c, tmp):
    plant_legacy_linkedin(tmp)
    assert SENTINEL.encode() in cache_text(tmp), 'the plant failed'
    assert c.cached('https://www.linkedin.com/company/acme') is None, 'an old raw company page replayed from the cache'
    no_sentinel(tmp)  # purged on the lookup
    plant_legacy_linkedin(tmp)
    sc.PURGED.discard(tmp.resolve()) if hasattr(sc, 'PURGED') else None
    sc.Corpus(tmp)  # a new run sweeps the cache
    no_sentinel(tmp)


@case
def linkedin_extract_receipt_still_replays_and_legacy_is_replaced_by_one(c, tmp):
    plant_legacy_linkedin(tmp)
    target = 'https://www.linkedin.com/company/acme'
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(LI_PAGE))) as req:
        first = c.fetch(target); n = req.call_count; second = c.fetch(target)
    assert first['status'] == 'ok' and second['sha256'] == first['sha256'] and req.call_count == n, f"status {first['status']}, replay re-requested ({n} -> {req.call_count})"
    no_sentinel(tmp)


@case
def linkedin_page_without_an_extractable_field_is_withheld(c, tmp):
    page = '<html><body><p>' + 'Sign in to see more. ' * 30 + SENTINEL + '</p></body></html>'
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(page))):
        r = c.fetch('https://www.linkedin.com/company/acme')
    assert r['status'] != 'ok', f"status {r['status']}"
    no_sentinel(tmp)


@case
def linkedin_pages_at_other_statuses_store_no_body(c, tmp):
    for n, (code, html) in enumerate([(403, WALL.replace('Checking', SENTINEL)), (500, LI_PAGE), (200, PUZZLE.replace('Security', SENTINEL))]):
        with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(html, code=code))):
            c.fetch(f'https://www.linkedin.com/company/acme{n}')
    no_sentinel(tmp)


def rendered(html, final='https://example.org/', code=200, flags=None, blocked=''):
    return lambda self, target, delay=1, *a, **k: dict(code=code, raw=html.encode(), location='', content_type='text/html', exit=0, error='', final_url=final, flags=flags or set(), blocked=blocked)


def with_browser(c, browser, target='https://example.org/', page=None):
    with patch.object(c, 'request', side_effect=serve(resp(code=404), page or resp(WALL, code=403))), patch.object(sc.Corpus, 'browser', browser):
        return c.fetch(target)


@case
def challenge_is_retried_once_in_the_browser_and_an_ok_page_is_receipted(c, tmp):
    import hashlib
    calls = []
    def browser(self, target, delay=1, *a, **k): calls.append(target); return rendered(PAGE, target)(self, target)
    r = with_browser(c, browser)
    assert calls == ['https://example.org/'], f'browser calls {calls}'
    assert r['status'] == 'ok' and r['route'] == 'browser', f"status {r['status']} route {r.get('route')}"
    assert r['sha256'] == hashlib.sha256((tmp / r['raw_file']).read_bytes()).hexdigest() == hashlib.sha256(PAGE.encode()).hexdigest()


@case
def challenge_error_and_excluded_browser_results_are_never_stored(c, tmp):
    for n, (html, code, blocked, final, want) in enumerate([(PUZZLE.replace('Security', SENTINEL), 200, '', None, 'BOT_CHECK_MANUAL'),
                                                           ('<html><p>Temporarily unavailable ' + SENTINEL + '</p></html>', 503, '', None, 'FETCH_FAILED'),
                                                           (SENT_PAGE, 200, '', 'https://example.org/our-team/', 'CONTACT_FORM_OR_STAFF_DIRECTORY'),
                                                           ('', 0, 'DOMAIN_BLOCKED', 'https://www.linkedin.com/in/someone', 'DOMAIN_BLOCKED')]):
        t = f'https://example.org/{n}'
        r = with_browser(c, rendered(html, final or t, code, blocked=blocked), t)
        assert r['status'] == want, f'case {n}: status {r["status"]} (want {want})'
    no_sentinel(tmp)



@case
def browser_result_for_a_linkedin_page_is_reduced_to_the_extract(c, tmp):
    r = with_browser(c, rendered(LI_PAGE, 'https://www.linkedin.com/company/acme'), 'https://www.linkedin.com/company/acme')
    assert r['status'] == 'ok' and (tmp / r['raw_file']).read_bytes().lstrip()[:1] == b'{', f"status {r['status']}"
    no_sentinel(tmp)


@case
def robots_states_of_every_browser_hop_reach_the_receipt(c, tmp):
    r = with_browser(c, rendered(PAGE, 'https://example.org/', flags={'yes'}))
    assert r['status'] == 'ok' and r['robots_disallowed'] == 'yes', f"status {r['status']} robots_disallowed {r.get('robots_disallowed')!r}"


@case
def curl_http2_error_is_retried_once_over_http11_with_verification_on(c, tmp):
    calls = []
    def request(u, delay=1, http1=False):
        if u.endswith('/robots.txt'): return resp(code=404)
        calls.append(http1)
        return dict(code=0, raw=b'', location='', content_type='', exit=92, error='curl: (92) HTTP/2 stream') if not http1 else resp(PAGE)
    with patch.object(c, 'request', side_effect=request):
        r = c.fetch('https://example.org/')
    assert r['status'] == 'ok' and calls == [False, True], f"status {r['status']} http1 per call {calls}"
    argv = []
    with patch.object(sc.subprocess, 'run', side_effect=lambda cmd, **kw: argv.append(cmd) or type('P', (), dict(stdout='200', stderr='', returncode=0))()):
        c.request('https://example.org/x', 1, http1=True)
    assert '--http1.1' in argv[0] and not {'-k', '--insecure', '--proxy-insecure'} & set(argv[0]), argv[0]


@case
def tls_chain_failure_goes_to_the_browser_after_the_http11_retry(c, tmp):
    calls = []
    def request(u, delay=1, http1=False):
        if u.endswith('/robots.txt'): return resp(code=404)
        calls.append(http1)
        return dict(code=0, raw=b'', location='', content_type='', exit=60, error='curl: (60) SSL certificate problem')
    seen = []
    def browser(self, target, delay=1, *a, **k): seen.append(target); return rendered(PAGE, target)(self, target)
    with patch.object(c, 'request', side_effect=request), patch.object(sc.Corpus, 'browser', browser):
        r = c.fetch('https://example.org/')
    assert r['status'] == 'ok' and calls == [False, True] and seen == ['https://example.org/'], f"status {r['status']} calls {calls} browser {seen}"
    with patch.object(c, 'request', side_effect=request), patch.object(sc.Corpus, 'browser', lambda self, t, d=1, *a, **k: dict(unavailable=True, error='CHROME_UNAVAILABLE', code=0, raw=b'', exit=127, final_url=t, flags=set(), blocked='')):
        r = c.fetch('https://example.org/two')
    assert r['status'] == 'FETCH_FAILED', f"status {r['status']} (a TLS failure with no browser is not a bot check)"


@case
def failed_browser_navigation_is_fetch_failed_without_a_robots_lookup_on_the_error_page(c, tmp):
    asked = []
    def request(u, delay=1, **kw):
        asked.append(u)
        return resp(code=404) if u.endswith('/robots.txt') else resp(WALL, code=403)
    gone = lambda self, target, delay=1, *a, **k: dict(code=0, raw=b'', location='', content_type='', exit=0, error='net::ERR_CERT_COMMON_NAME_INVALID', final_url='chrome-error://chromewebdata/', flags=set(), blocked='')
    with patch.object(c, 'request', side_effect=request), patch.object(sc.Corpus, 'browser', gone):
        r = c.fetch('https://example.org/')
    assert r['status'] == 'FETCH_FAILED' and not any(u.startswith('chrome-error') for u in asked), f"status {r['status']}, asked {asked}"


def mutation():
    """The kept-line case must fail when its guard is removed; meaningful only where the guard exists."""
    if not hasattr(sc, 'linkedin_blocked'):
        print('SKIP mutation (no linkedin_blocked in this copy)'); return
    with patch.object(sc, 'linkedin_blocked', return_value=False), tempfile.TemporaryDirectory() as d:
        try: linkedin_personal_profiles_and_staff_lists_refuse_at_every_hop(sc.Corpus(d), Path(d)); caught = False
        except AssertionError: caught = True
    RESULTS.append((caught, 'mutation'))
    print(('PASS ' if caught else 'FAIL ') + 'mutation_linkedin_guard_removed - with the guard removed the profile case ' + ('fails' if caught else 'still passes (it checks nothing)'))


mutation()


def real_browser():
    import http.server, threading, time
    sc.Corpus.browser = REAL_BROWSER
    sc.Corpus.BROWSER_WAIT = 8
    LOG = []
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            curl = 'AtlasSiteCorpus' in self.headers.get('User-Agent', '')
            LOG.append((time.time(), self.headers.get('Host'), self.path, self.headers.get('Cookie'), curl))
            path, code, extra, body = self.path.split('?')[0], 200, {}, PAGE
            port = self.server.server_port
            if path == '/robots.txt': body = 'User-agent: *\nCrawl-delay: 3\nDisallow: /y' if (self.headers.get('Host') or '').startswith('localhost') else 'User-agent: *\nAllow: /'
            elif curl: code, body = 403, WALL  # curl sees a bot check on every page; Chrome sees the real route
            elif path in ('/h1', '/h2', '/x', '/y', '/c1'):
                code = 302; extra = {'Location': {'/h1': '/h2', '/h2': '/our-team', '/x': f'http://localhost:{port}/y', '/y': '/y2', '/c1': '/c2'}[path]}
                if path == '/c1': extra['Set-Cookie'] = 'a=1'
            elif path == '/our-team': body = SENT_PAGE
            elif path == '/c2': extra = {'Set-Cookie': 'b=2'}; body = '<html><script>document.cookie="js=1"</script><iframe src="/c3"></iframe>' + PAGE + '</html>'
            elif path == '/err': code, body = 503, '<html><p>Temporarily unavailable ' + SENTINEL + '</p></html>'
            elif path == '/wall': body = '<html><title>Just a moment...</title><!-- ' + SENTINEL + ' --></html>'
            elif path == '/assets': body = '<html><script src="/s.js"></script><img src="/img.png">' + PAGE + '</html>'
            elif path == '/nav': body = '<html><title>Security check</title><button onclick="location=\'/clicked\'">Verify you are human</button><label><input type=checkbox onchange="location=\'/clicked\'"> Verify you are human</label></html>'
            self.send_response(code); self.send_header('Content-Type', 'text/html')
            for k, v in extra.items(): self.send_header(k, v)
            self.end_headers(); self.wfile.write(body.encode())
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{srv.server_port}'
    chrome = lambda frag: [e for e in LOG if frag in e[2] and not e[4]]

    @case
    def b1_real_chrome_loads_only_documents_and_receipts_an_ok_page(c, tmp):
        import hashlib
        r = c.fetch(base + '/assets')
        assert r['status'] == 'ok' and r['route'] == 'browser', f"status {r['status']} route {r.get('route')} error {r.get('error')!r}"
        assert not chrome('/s.js') and not chrome('/img.png'), 'a script or image was requested'
        assert r['sha256'] == hashlib.sha256((tmp / r['raw_file']).read_bytes()).hexdigest()

    @case
    def b2_redirect_hop_to_a_staff_directory_is_aborted_before_it_is_sent(c, tmp):
        r = c.fetch(base + '/h1')
        assert r['status'] == 'CONTACT_FORM_OR_STAFF_DIRECTORY' and not chrome('/our-team'), f"status {r['status']}; chrome requests {[e[2] for e in LOG if not e[4]]}"
        no_sentinel(tmp)

    @case
    def b3_every_hop_host_is_robots_checked_and_paced(c, tmp):
        r = c.fetch(base + '/x')
        ts = [e[0] for e in chrome('/y')]
        assert r['status'] == 'ok' and r['robots_disallowed'] == 'yes', f"status {r['status']} robots_disallowed {r.get('robots_disallowed')!r}"
        assert any(e[1].startswith('localhost') and e[2] == '/robots.txt' for e in LOG), 'the hop host robots.txt was never read'
        hits = sorted(e[0] for e in LOG if e[1].startswith('localhost') and e[2] in ('/y', '/y2') and not e[4])
        assert len(hits) == 2 and hits[1] - hits[0] >= 2.9, f'gap between the two localhost documents {[round(b - a, 1) for a, b in zip(hits, hits[1:])]} (Crawl-delay 3)'

    @case
    def b4_no_cookie_is_ever_sent(c, tmp):
        r = c.fetch(base + '/c1')
        sent = [(e[2], e[3]) for e in LOG if not e[4] and e[3]]
        assert r['status'] == 'ok' and not sent, f"status {r['status']}; Chrome sent cookies {sent}"
        from playwright.sync_api import sync_playwright  # control: the fixture does leak a cookie to an unprotected Chrome
        before = len(LOG)
        with sync_playwright() as pw:
            b = pw.chromium.launch(channel='chrome', headless=False); pg = b.new_context().new_page(); pg.goto(base + '/c1'); pg.wait_for_timeout(1500); b.close()
        assert any(e[3] for e in LOG[before:]), 'control: an unprotected Chrome should have sent the cookie back'

    @case
    def b5_error_and_bot_check_pages_are_never_stored(c, tmp):
        assert c.fetch(base + '/err')['status'] == 'FETCH_FAILED'
        assert c.fetch(base + '/wall')['status'] == 'BOT_CHECK_MANUAL'
        assert base + '/wall' in (tmp / 'manual-bot-check.csv').read_text()
        no_sentinel(tmp)

    @case
    def b6_the_browser_never_clicks_or_types(c, tmp):
        r = c.fetch(base + '/nav')
        assert r['status'] == 'BOT_CHECK_MANUAL' and not chrome('/clicked'), f"status {r['status']}; clicked {bool(chrome('/clicked'))}"
    srv.shutdown()


if '--real-browser' in sys.argv: real_browser()
bad = [n for ok, n in RESULTS if not ok]
print(f'{len(RESULTS) - len(bad)} PASS, {len(bad)} FAIL')
sys.exit(1 if bad else 0)
