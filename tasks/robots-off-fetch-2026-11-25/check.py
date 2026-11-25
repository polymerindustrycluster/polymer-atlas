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
