#!/usr/bin/env python3
"""Planted cases for the HTTP/1.1 transport fallback in scripts/site_corpus.py (curl exits 35, 60 and 92 get one retry over --http1.1).

Usage: python3 check.py SCRIPTS_DIR     (the scripts/ directory judged: the head, or a copy of origin/main's)
Each case prints PASS or FAIL; the check exits 1 if any fails. Every case asserts behaviour on a mocked curl transport.
"""
import sys, tempfile
from pathlib import Path
from unittest.mock import patch

scripts = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(scripts))
import site_corpus as sc  # noqa: E402

RESULTS = []
PAGE = '<html><body><p>' + 'Real polymer molding. ' * 20 + '</p></body></html>'


def resp(body='', code=200, location='', exit=0):
    return dict(raw=body.encode(), code=code, location=location, content_type='text/html', exit=exit, error='')


def case(fn):
    try:
        with tempfile.TemporaryDirectory() as d:
            fn(sc.Corpus(d), Path(d))
        RESULTS.append((True, fn.__name__)); print('PASS ' + fn.__name__, flush=True)
    except Exception as e:  # AssertionError or anything else is a FAIL with its reason
        RESULTS.append((False, fn.__name__)); print(f'FAIL {fn.__name__} - {type(e).__name__}: {e}'[:230], flush=True)
    return fn


def transport(calls, first):
    """curl mock: robots.txt is 404; the page fails with `first` over HTTP/2 and succeeds over HTTP/1.1; every call is logged."""
    def request(u, delay=1, http1=False):
        calls.append((u, http1))
        if u.endswith('/robots.txt'): return resp(code=404)
        return first if not http1 else resp(PAGE)
    return request


@case
def exit_92_with_no_status_is_retried_once_over_http11(c, tmp):
    calls = []
    with patch.object(c, 'request', side_effect=transport(calls, dict(code=0, raw=b'', location='', content_type='', exit=92, error='curl: (92) HTTP/2 stream'))):
        r = c.fetch('https://example.org/')
    pages = [x for x in calls if x[0].startswith('https://example.org/') and not x[0].endswith('/robots.txt')]
    assert r['status'] == 'ok' and pages == [('https://example.org/', False), ('https://example.org/', True)], f"status {r['status']} page calls {pages}"


@case
def exit_92_after_http_200_headers_is_retried_and_its_redirect_followed(c, tmp):
    calls = []
    def request(u, delay=1, http1=False):
        calls.append((u, http1))
        if u.endswith('/robots.txt'): return resp(code=404)
        if u == 'https://example.org/a': return resp(PAGE, exit=92) if not http1 else resp(code=301, location='https://example.org/b')
        return resp(PAGE)
    with patch.object(c, 'request', side_effect=request):
        r = c.fetch('https://example.org/a')
    pages = [x for x in calls if x[0].startswith('https://example.org/') and not x[0].endswith('/robots.txt')]
    assert r['status'] == 'ok' and pages == [('https://example.org/a', False), ('https://example.org/a', True), ('https://example.org/b', False)], f"status {r['status']} page calls {pages}"


@case
def handshake_and_chain_failures_are_retried_once_and_only_once(c, tmp):
    for exit_code in (35, 60):
        calls = []
        failing = lambda u, delay=1, http1=False, e=exit_code: (calls.append((u, http1)) or (resp(code=404) if u.endswith('/robots.txt') else dict(code=0, raw=b'', location='', content_type='', exit=e, error=f'curl: ({e})')))
        with patch.object(c, 'request', side_effect=failing):
            r = c.fetch(f'https://example.org/{exit_code}')
        pages = [x for x in calls if x[0].startswith('https://example.org/') and not x[0].endswith('/robots.txt')]
        assert r['status'] == 'FETCH_FAILED' and pages == [(f'https://example.org/{exit_code}', False), (f'https://example.org/{exit_code}', True)], f'exit {exit_code}: status {r["status"]} page calls {pages}'


@case
def a_timeout_is_not_retried_but_an_http2_error_beside_it_is(c, tmp):
    for code, retried in ((28, False), (92, True)):
        calls = []
        with patch.object(c, 'request', side_effect=transport(calls, dict(code=0, raw=b'', location='', content_type='', exit=code, error=f'curl: ({code})'))):
            c.fetch(f'https://example.org/e{code}')
        got = any(h for u, h in calls if u.startswith('https://example.org/e'))
        assert got == retried, f'exit {code}: http1 retry {got} (want {retried})'


@case
def the_robots_txt_transport_gets_the_same_retry(c, tmp):
    calls = []
    def request(u, delay=1, http1=False):
        calls.append((u, http1))
        if u.endswith('/robots.txt'): return resp('User-agent: *\nDisallow: /private') if http1 else dict(code=0, raw=b'', location='', content_type='', exit=92, error='curl: (92)')
        return resp(PAGE)
    with patch.object(c, 'request', side_effect=request):
        r = c.fetch('https://example.org/private')
    assert r['status'] == 'ok' and r['robots_disallowed'] == 'yes' and ('https://example.org/robots.txt', True) in calls, f"status {r['status']} robots_disallowed {r.get('robots_disallowed')!r}"


@case
def the_http11_command_keeps_certificate_verification_on(c, tmp):
    argv = []
    class P: stdout = '200'; stderr = ''; returncode = 0
    with patch.object(sc.subprocess, 'run', side_effect=lambda cmd, **kw: argv.append(cmd) or P()):
        c.request('https://example.org/x', 1, http1=True)
        c.request('https://example.org/y', 1)
    assert '--http1.1' in argv[0] and '--http1.1' not in argv[1], argv
    assert not {'-k', '--insecure', '--proxy-insecure'} & set(argv[0]), argv[0]


bad = [n for ok, n in RESULTS if not ok]
print(f'{len(RESULTS) - len(bad)} PASS, {len(bad)} FAIL')
sys.exit(1 if bad else 0)
