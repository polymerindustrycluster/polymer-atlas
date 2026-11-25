#!/usr/bin/env python3
"""Planted cases for the 2026-11-24 robots/bot-check/LinkedIn rule change in scripts/site_corpus.py.

Usage: python3 check.py SCRIPTS_DIR [--real-browser]
  SCRIPTS_DIR  the scripts/ directory whose site_corpus.py is judged (yours, or a copy of origin/main's).
  --real-browser  also drives real local Chrome against a local fixture server (auto-clearing check, a plain
                  checkbox in the page, a checkbox in a frame, an interactive puzzle that never clears).
                  Needs `uv run --with playwright` and the sandbox off; with no Chrome the cases FAIL, never skip.
Each case prints PASS or FAIL and the check exits 1 if any case fails. Every case asserts behaviour.
"""
import hashlib, http.server, sys, tempfile, threading, time
from pathlib import Path
from unittest.mock import patch

scripts = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(scripts))
import site_corpus as sc  # noqa: E402

RESULTS = []
PAGE = '<html><body><p>' + 'Real polymer molding. ' * 20 + '</p></body></html>'
WALL = '<html><title>Just a moment...</title><body>Checking your browser</body></html>'
PUZZLE = '<html><title>Security check</title><body><div class="g-recaptcha"></div></body></html>'


def resp(body='', code=200, location=''):
    return dict(raw=body.encode(), code=code, location=location, content_type='text/html', exit=0, error='')


def rendered(html, final='https://example.org/'):
    return dict(code=200, raw=html.encode(), location='', content_type='text/html', exit=0, error='', final_url=final)


def case(fn):
    try:
        with tempfile.TemporaryDirectory() as d:
            detail = fn(sc.Corpus(d), Path(d)) or ''
        RESULTS.append((True, fn.__name__, detail))
    except Exception as e:  # AssertionError or anything else is a FAIL with its reason
        RESULTS.append((False, fn.__name__, f'{type(e).__name__}: {e}'[:200]))
    print(('PASS ' if RESULTS[-1][0] else 'FAIL ') + fn.__name__ + (' - ' + RESULTS[-1][2] if RESULTS[-1][2] else ''), flush=True)
    fn.__wrapped__ = fn
    return fn


def serve(robots, page):
    return lambda u, delay=1: robots if u.endswith('/robots.txt') else page


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
def stale_blocked_receipt_is_refetched(c, tmp):
    target = 'https://example.org/old'
    c.save(target, {}, 'ROBOTS_BLOCKED', target, 'direct')
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(PAGE))):
        r = c.fetch(target)
    assert r['status'] == 'ok', f"status {r['status']} (an old ROBOTS_BLOCKED receipt kept answering)"


@case
def linkedin_company_page_is_fetched_logged_out(c, tmp):
    argv = []
    def run(cmd, **kw):
        argv.append(cmd)
        return type('P', (), dict(stdout='200', stderr='', returncode=0))()
    target = 'https://www.linkedin.com/company/acme'
    with patch.object(sc.subprocess, 'run', side_effect=run):
        c.request(target)
    assert argv, 'no request was made for a LinkedIn company page'
    flat = ' '.join(argv[0]).lower()
    assert not any(f in flat.split() for f in ('-b', '--cookie', '--cookie-jar', '-c', '-h', '--header', '-u', '--user')), flat
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp('<html>Acme | LinkedIn ' + 'About us polymer molding. ' * 10 + '</html>'))):
        r = c.fetch(target)
    assert r['status'] == 'ok', f"status {r['status']}"


@case
def linkedin_personal_profiles_and_staff_lists_still_refuse(c, tmp):
    for target in ('https://www.linkedin.com/in/someone', 'https://www.linkedin.com/pub/someone/1/2/3',
                   'https://www.linkedin.com/%69n/someone', 'https://www.linkedin.com/company/acme/people', 'https://lnkd.in/x'):
        with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(PAGE))) as request:
            r = c.fetch(target)
        assert r['status'] != 'ok' and not request.call_count, f'{target}: status {r["status"]}, requests {request.call_count}'


@case
def challenge_page_routes_to_browser_with_hash_receipt(c, tmp):
    calls = []
    def browser(target, delay=1, **kw): calls.append(target); return rendered(PAGE, target)
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(WALL, code=403))), patch.object(sc.Corpus, 'browser', create=True, side_effect=browser):
        r = c.fetch('https://example.org/')
    assert calls == ['https://example.org/'], f'browser calls {calls}'
    assert r['status'] == 'ok' and r.get('route') == 'browser', f"status {r['status']} route {r.get('route')}"
    assert r['sha256'] == hashlib.sha256((tmp / r['raw_file']).read_bytes()).hexdigest() and r['sha256'] == hashlib.sha256(PAGE.encode()).hexdigest()


@case
def puzzle_page_lands_on_the_manual_list(c, tmp):
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(WALL, code=403))), patch.object(sc.Corpus, 'browser', create=True, side_effect=lambda t, delay=1, **kw: rendered(PUZZLE, t)):
        r = c.fetch('https://example.org/puzzle')
    assert r['status'] == 'BOT_CHECK_MANUAL', f"status {r['status']}"
    assert 'https://example.org/puzzle' in (tmp / 'manual-bot-check.csv').read_text()


SENTINEL = 'SENTINEL-PERSONAL-DATA-7731'
SENT_PAGE = '<html><body><p>' + ('Real polymer molding ' + SENTINEL + '. ') * 20 + '</p></body></html>'


def cache_text(tmp):
    return b''.join(f.read_bytes() for f in tmp.iterdir() if f.is_file())


def browser_returning(html, final, code=200, seen=None):
    def browser(target, delay=1, **kw):
        if seen is not None: seen.append(kw)
        return rendered(html, final) | dict(code=code)
    return browser


def walled(c, browser, target='https://example.org/', page=resp(WALL, code=403)):
    with patch.object(c, 'request', side_effect=serve(resp(code=404), page)), patch.object(sc.Corpus, 'browser', create=True, side_effect=browser):
        return c.fetch(target)


@case
def r1_browser_profile_destination_is_never_stored(c, tmp):
    r = walled(c, browser_returning(SENT_PAGE, 'https://www.linkedin.com/in/someone'))
    assert r['status'] != 'ok' and SENTINEL.encode() not in cache_text(tmp), f"status {r['status']}, sentinel stored: {SENTINEL.encode() in cache_text(tmp)}"


@case
def r1_browser_staff_directory_is_never_stored(c, tmp):
    r = walled(c, browser_returning(SENT_PAGE, 'https://example.org/our-team/'))
    assert r['status'] != 'ok' and SENTINEL.encode() not in cache_text(tmp), f"status {r['status']}, sentinel stored: {SENTINEL.encode() in cache_text(tmp)}"


@case
def r1_contact_form_only_page_is_never_stored(c, tmp):
    form = '<html><form action="/c"><input name=n></form><p>' + SENTINEL + '</p></html>'
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(form))):
        r = c.fetch('https://example.org/contact')
    assert r['status'] != 'ok' and SENTINEL.encode() not in cache_text(tmp), f"status {r['status']}, sentinel stored: {SENTINEL.encode() in cache_text(tmp)}"


@case
def r2_browser_receipt_robots_follows_the_final_url(c, tmp):
    robots = resp('User-agent: *\nDisallow: /secret')
    with patch.object(c, 'request', side_effect=serve(robots, resp(WALL, code=403))), \
            patch.object(sc.Corpus, 'browser', create=True, side_effect=browser_returning(PAGE, 'https://example.org/secret')):
        r = c.fetch('https://example.org/start')
    assert r['status'] == 'ok' and r.get('robots_disallowed') == 'yes', f"status {r['status']} robots_disallowed {r.get('robots_disallowed')!r}"


@case
def r3_only_linkedin_visits_run_cookieless(c, tmp):
    seen = []
    walled(c, browser_returning(PAGE, 'https://www.linkedin.com/company/acme', seen=seen), 'https://www.linkedin.com/company/acme')
    walled(c, browser_returning(PAGE, 'https://example.org/', seen=seen))
    assert [k.get('no_cookies') for k in seen] == [True, False], f'no_cookies per browser call: {[k.get("no_cookies") for k in seen]}'


@case
def r4_challenge_without_a_browser_is_manual_not_ok(c, tmp):
    gone = lambda target, delay=1, **kw: dict(code=0, raw=b'', exit=127, error='PLAYWRIGHT_UNAVAILABLE', unavailable=True, final_url=target)
    r = walled(c, gone, 'https://example.org/p', resp(PUZZLE))
    assert r['status'] == 'BOT_CHECK_MANUAL' and 'https://example.org/p' in (tmp / 'manual-bot-check.csv').read_text(), f"status {r['status']}"


@case
def r4_error_page_after_the_browser_is_not_ok(c, tmp):
    r = walled(c, browser_returning('<html><p>Temporarily unavailable</p></html>', 'https://example.org/', code=503))
    assert r['status'] != 'ok', f"status {r['status']}"


def mutation():
    """The kept-line case must fail when its guard is removed; meaningful only where the guard exists."""
    if not hasattr(sc, 'linkedin_blocked'):
        print('SKIP mutation (no linkedin_blocked in this copy)'); return
    with patch.object(sc, 'linkedin_blocked', return_value=False), tempfile.TemporaryDirectory() as d:
        try: linkedin_personal_profiles_and_staff_lists_still_refuse.__wrapped__(sc.Corpus(d), Path(d)); caught = False
        except AssertionError: caught = True
    RESULTS.append((caught, 'mutation_linkedin_guard_removed', ''))
    print(('PASS ' if caught else 'FAIL ') + 'mutation_linkedin_guard_removed - with the guard removed the profile case ' + ('fails' if caught else 'still passes (it checks nothing)'))


mutation()


def real_browser():
    pages = {
        '/auto': '<html><title>Just a moment...</title><body>Checking your browser</body><script>setTimeout(()=>{document.title="Home";document.body.innerHTML=%r},2500)</script></html>' % PAGE,
        '/click': '<html><title>Security check</title><body><button id=b onclick="document.title=\'Home\';document.body.innerHTML=%r">Verify you are human</button></body></html>' % PAGE,
        '/frame': '<html><title>Security check</title><body><iframe src="/inner" width=300 height=70></iframe></body></html>',
        '/inner': '<html><body><label><input type=checkbox onchange="parent.document.title=\'Home\';parent.document.body.innerHTML=%r"> Verify you are human</label></body></html>' % PAGE,
        '/puzzle': PUZZLE,
        '/toteam': '<html><title>Just a moment...</title><meta http-equiv=refresh content="0;url=/our-team"></html>',
        '/our-team': SENT_PAGE,
        '/hop1': '<html><title>Just a moment...</title><meta http-equiv=refresh content="0;url=/hop2"></html>',
        '/hop2': PAGE,
        '/c1': '<html><title>Just a moment...</title><meta http-equiv=refresh content="0;url=/c2"></html>',
        '/c2': PAGE,
        '/boxes': '<html><title>Security check</title><body><label><input type=checkbox onchange="fetch(\'/clicked?main\')"> I agree to the terms</label><iframe src="/inner2"></iframe></body></html>',
        '/inner2': '<html><body><input type=checkbox onchange="fetch(\'/clicked?frame\')"></body></html>',
        '/twostage': '<html><title>Security check</title><body><script>function mk(){document.body.innerHTML=\'<button onclick="fetch(\\\'/clicked?stage\\\');mk()">Verify you are human</button>\'};mk()</script></body></html>',
    }
    LOG = []
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            LOG.append((time.time(), self.headers.get('Host'), self.path, self.headers.get('Cookie')))
            body = pages.get(self.path.split('?')[0])
            if self.path == '/robots.txt': body = 'User-agent: *\nCrawl-delay: 3'
            if self.path.startswith('/clicked'): body = 'x'
            extra = {'Set-Cookie': 's=1'} if self.path == '/c1' else {}
            self.send_response(200 if body else 404); self.send_header('Content-Type', 'text/html')
            for k, v in extra.items(): self.send_header(k, v)
            self.end_headers()
            self.wfile.write((body or 'nf').encode())
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{srv.server_port}'
    sc.Corpus.BROWSER_WAIT = 8
    hits = lambda frag: [e for e in LOG if frag in e[2]]
    pages['/tootherhost'] = '<html><title>Just a moment...</title><meta http-equiv=refresh content="0;url=http://localhost:%d/other"></html>' % srv.server_port
    pages['/other'] = SENT_PAGE
    for path, want in (('/auto', 'ok'), ('/click', 'ok'), ('/frame', 'ok'), ('/puzzle', 'BOT_CHECK_MANUAL')):
        def run(c, tmp, path=path, want=want):
            r = c.fetch(base + path)
            assert r['status'] == want and r.get('route') == 'browser', f"status {r['status']} route {r.get('route')} error {r.get('error')!r}"
            if want == 'ok':
                assert 'Real polymer molding' in (tmp / r['text_file']).read_text() and r['sha256'] == hashlib.sha256((tmp / r['raw_file']).read_bytes()).hexdigest()
            else:
                assert base + path in (tmp / 'manual-bot-check.csv').read_text()
        run.__name__ = 'real_chrome' + path.replace('/', '_')
        case(run)

    def never_loads(path, want):
        def run(c, tmp):
            r = c.fetch(base + path)
            assert r['status'] == want and not hits(want_path[path]) and SENTINEL.encode() not in cache_text(tmp), \
                f"status {r['status']} (want {want}); server saw {[e[2] for e in LOG if e[2] != '/robots.txt']}"
        run.__name__ = 'r1_real_chrome' + path.replace('/', '_') + '_never_loaded'
        case(run)
    want_path = {'/toteam': '/our-team', '/tootherhost': '/other'}
    never_loads('/toteam', 'CONTACT_FORM_OR_STAFF_DIRECTORY')
    never_loads('/tootherhost', 'CROSS_HOST_REDIRECT')

    @case
    def r2_real_chrome_navigations_are_paced_by_crawl_delay(c, tmp):
        r = c.fetch(base + '/hop1')
        times = [e[0] for e in LOG if e[2] in ('/hop1', '/hop2')]
        assert r['status'] == 'ok' and len(times) == 3, f"status {r['status']} requests {[e[2] for e in LOG]}"
        gaps = [round(b - a, 1) for a, b in zip(times, times[1:])]
        assert min(gaps) >= 2.9, f'gaps between the curl hop, the browser hop and the next navigation: {gaps} (Crawl-delay 3)'

    @case
    def r3_real_chrome_sends_no_cookie_when_asked_and_does(c, tmp):
        quiet = c.browser(base + '/c1', 1, no_cookies=True)
        sent_quiet = [e[3] for e in hits('/c2')]
        c.browser(base + '/c1', 1, no_cookies=False)
        sent_loud = [e[3] for e in hits('/c2')][len(sent_quiet):]
        assert b'Real polymer molding' in quiet['raw'] and sent_quiet == [None], f'no_cookies=True: Cookie headers at /c2 {sent_quiet}'
        assert sent_loud and sent_loud[0], f'control: a cookie set by the page should come back without no_cookies, got {sent_loud}'

    @case
    def r5_real_chrome_unrelated_checkboxes_are_never_clicked(c, tmp):
        r = c.fetch(base + '/boxes')
        assert not hits('/clicked'), f"clicked {[e[2] for e in hits('/clicked')]} (status {r['status']})"

    @case
    def r5_real_chrome_clicks_one_control_once(c, tmp):
        sc.Corpus.BROWSER_WAIT = 14
        r = c.fetch(base + '/twostage')
        sc.Corpus.BROWSER_WAIT = 8
        assert len(hits('/clicked')) == 1, f"clicks {len(hits('/clicked'))} (status {r['status']})"
    srv.shutdown()


if '--real-browser' in sys.argv: real_browser()
bad = [n for ok, n, _ in RESULTS if not ok]
print(f'{len(RESULTS) - len(bad)} PASS, {len(bad)} FAIL')
sys.exit(1 if bad else 0)
