#!/usr/bin/env python3
"""Planted cases for the 2026-11-24 robots/bot-check/LinkedIn rule change in scripts/site_corpus.py.

Usage: python3 check.py SCRIPTS_DIR [--real-browser]
  SCRIPTS_DIR  the scripts/ directory whose site_corpus.py is judged (yours, or a copy of origin/main's).
  --real-browser  also drives real local Chrome against a local fixture server (auto-clearing check, a plain
                  checkbox in the page, a checkbox in a frame, an interactive puzzle that never clears).
                  Needs `uv run --with playwright` and the sandbox off; with no Chrome the cases FAIL, never skip.
Each case prints PASS or FAIL and the check exits 1 if any case fails. Every case asserts behaviour.
"""
import hashlib, http.server, sys, tempfile, threading
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
    def browser(target, delay=1): calls.append(target); return rendered(PAGE, target)
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(WALL, code=403))), patch.object(sc.Corpus, 'browser', create=True, side_effect=browser):
        r = c.fetch('https://example.org/')
    assert calls == ['https://example.org/'], f'browser calls {calls}'
    assert r['status'] == 'ok' and r.get('route') == 'browser', f"status {r['status']} route {r.get('route')}"
    assert r['sha256'] == hashlib.sha256((tmp / r['raw_file']).read_bytes()).hexdigest() and r['sha256'] == hashlib.sha256(PAGE.encode()).hexdigest()


@case
def puzzle_page_lands_on_the_manual_list(c, tmp):
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp(WALL, code=403))), patch.object(sc.Corpus, 'browser', create=True, side_effect=lambda t, delay=1: rendered(PUZZLE, t)):
        r = c.fetch('https://example.org/puzzle')
    assert r['status'] == 'BOT_CHECK_MANUAL', f"status {r['status']}"
    assert 'https://example.org/puzzle' in (tmp / 'manual-bot-check.csv').read_text()


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
    }
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            body = pages.get(self.path.split('?')[0])
            self.send_response(200 if body else 404); self.send_header('Content-Type', 'text/html'); self.end_headers()
            self.wfile.write((body or 'nf').encode())
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{srv.server_port}'
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
    srv.shutdown()


if '--real-browser' in sys.argv: real_browser()
bad = [n for ok, n, _ in RESULTS if not ok]
print(f'{len(RESULTS) - len(bad)} PASS, {len(bad)} FAIL')
sys.exit(1 if bad else 0)
