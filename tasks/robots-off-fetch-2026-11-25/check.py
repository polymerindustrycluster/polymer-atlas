#!/usr/bin/env python3
"""Planted cases for the 2026-11-24/25 owner rulings on scripts/site_corpus.py: robots.txt off, bot checks to a manual list,
LinkedIn company pages logged out, privacy exclusion before any body is stored.

Usage: python3 check.py SCRIPTS_DIR
  SCRIPTS_DIR  the scripts/ directory whose site_corpus.py is judged (yours, or a copy of origin/main's or of an earlier head).
Each case prints PASS or FAIL and the check exits 1 if any case fails. Every case asserts behaviour, on a mocked transport.
"""
import sys, tempfile
from pathlib import Path
from unittest.mock import patch

scripts = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(scripts))
import site_corpus as sc  # noqa: E402

RESULTS = []
PAGE = '<html><body><p>' + 'Real polymer molding. ' * 20 + '</p></body></html>'
WALL = '<html><title>Just a moment...</title><body>Checking your browser</body></html>'
PUZZLE = '<html><title>Security check</title><body><div class="g-recaptcha"></div></body></html>'
SENTINEL = 'SENTINEL-PERSONAL-DATA-7731'
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
    with patch.object(c, 'request', side_effect=serve(resp(code=404), resp('<html>Acme | LinkedIn ' + 'About us polymer molding. ' * 10 + '</html>'))):
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


@case
def no_chrome_is_launched(c, tmp):
    assert not hasattr(sc.Corpus, 'browser'), 'the Chrome retry waits for its own PR'


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
bad = [n for ok, n in RESULTS if not ok]
print(f'{len(RESULTS) - len(bad)} PASS, {len(bad)} FAIL')
sys.exit(1 if bad else 0)
