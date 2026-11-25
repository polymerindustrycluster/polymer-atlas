#!/usr/bin/env python3
"""Shared own-site corpus. No canonical data writes; cache must stay outside the repo.

Promotes L1 run.py's curl transport, Text extraction, hash receipts and challenge
checks, and evidence-audit analyze.py's calibrated contiguous-word matcher.
Owner ruling 2026-11-24: robots.txt no longer blocks a fetch (it is read for Crawl-delay and receipted as
robots_disallowed yes/no/unreadable), a bot-check page is retried once in a fresh local Chrome, and LinkedIn
company pages are fetchable logged out. Kept: the per-host rate limit, no solver services, no personal profiles.
Usage: python3 scripts/site_corpus.py crawl [--cache-dir PATH]
       python3 scripts/site_corpus.py rawcheck URL QUOTE [--cache-dir PATH]
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import csv
from datetime import datetime, timezone
import fcntl
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
import unicodedata
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

from regions import PIC18

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/cache/site_corpus')
UA = 'Mozilla/5.0 (compatible; AtlasSiteCorpus/1.0)'
ROBOT_AGENT = 'AtlasSiteCorpus'
KINDS = {
    'about': r'about|company|who-we-are',
    'locations': r'contact|location|facilit',
    'news': r'news|press',
    'quality': r'quality|certificat',
    'markets': r'industr|market',
    'products': r'product|capabilit|process|service',
}
BOT_CODES = (200, 403, 503, 999)  # 999 is LinkedIn's refusal; other codes never reach the browser
# shortcut: markers copied from scripts/liveness_sweep.py (importing it pulls in the whole sweep); merge if either list grows.
BOT_TITLES = ('just a moment', 'attention required', 'access denied', 'are you a robot', 'pardon our interruption',
              'verify you are human', 'security check', 'captcha', 'ddos protection', 'request blocked')
BOT_BODY = ('g-recaptcha', 'h-captcha', 'hcaptcha.com', 'px-captcha', 'cf-challenge', 'challenge-platform',
            'cdn-cgi/challenge', 'enable javascript and cookies to continue', 'incapsula incident',
            'sucuri website firewall', 'akamai reference')
VERIFY = re.compile(r"verify you are human|i am human|i.m not a robot|i am not a robot", re.I)
SIGNIN_PATH = re.compile(r'/(?:authwall|login|uas/|checkpoint)', re.I)
STAFF_PATH = re.compile(r'/(?:staff-directory|employee-directory|our-team|team|staff)/?$', re.I)
CHALLENGE_HOSTS = ('challenges.cloudflare.com',)  # the only other origin a bot-check frame may load from
STALE = ('ROBOTS_BLOCKED', 'DOMAIN_BLOCKED')  # receipts written under the pre-2026-11-24 rules; refetched, never replayed
WALLS = ('just a moment...', 'verify you are human', 'attention required! | cloudflare',
         'checking your browser', 'access to this page has been denied',
         'enable javascript and cookies to continue', 'request blocked')


def words(value):
    return re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', value or '').encode('ascii', 'ignore').decode().lower())


def on_page(quote, text):
    """Calibrated audit matcher: contiguous normalized words, never a bag of words."""
    q, p = words(quote), words(text)
    return any(p[i:i + len(q)] == q for i in range(len(p) - len(q) + 1)) if q else None


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []; self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'): self.skip += 1
        if tag == 'a':
            self.links.extend(v for k, v in attrs if k == 'href' and v)

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'): self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip: self.parts.append(data)


def url(value):
    if re.search(r"[\x00-\x20\x7f\\]", value):
        raise ValueError('Ambiguous URL characters')
    p = urlsplit(value)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
        raise ValueError('Expected an HTTP(S) URL without credentials')
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or '/', p.query, ''))


def linkedin_url(target):
    parsed = urlsplit(target)
    host = unquote(parsed.hostname or '').encode('idna').decode().lower().rstrip('.')
    if host == 'r.jina.ai':
        # The first path component can contain the URL the relay will request.
        wrapped = urlsplit(unquote(parsed.path.removeprefix('/')))
        host = unquote(wrapped.hostname or '').encode('idna').decode().lower().rstrip('.')
    return any(host == domain or host.endswith('.' + domain) for domain in ('linkedin.com', 'lnkd.in'))


def linkedin_company_page(target):
    """Company pages only (logged out): /company/<slug> or /showcase/<slug>, optionally /about. Never /in/, /pub/, /people."""
    p = urlsplit(target)
    host = unquote(p.hostname or '').encode('idna').decode().lower().rstrip('.')
    path = unquote(p.path)
    return (host == 'linkedin.com' or host.endswith('.linkedin.com')) and \
        bool(re.fullmatch(r'/(?:company|showcase)/(?!\.+/?$)[^/]+(?:/about)?/?', path))


def linkedin_blocked(target):
    """A LinkedIn URL the fetcher refuses: anything but a company page (robots.txt aside, read for the receipt field)."""
    return linkedin_url(target) and not (linkedin_company_page(target) or urlsplit(target).path == '/robots.txt')


def challenged(code, body):
    """Bot-check page: title or wall text always; widget markers only on a refusal code or a nearly empty page."""
    lower = body.lower()
    title = re.search(r'<title[^>]*>(.*?)</title>', lower, re.S)
    parser = Text(); parser.feed(body); text = ' '.join(parser.parts)
    if any(w in text.lower() for w in WALLS) or (title and any(m in title[1] for m in BOT_TITLES)): return True
    return any(m in lower for m in BOT_BODY) and (code in (403, 503, 999) or len(words(text)) < 40)


def host_of(value):
    return (urlsplit(value).hostname or '').lower().removeprefix('www.')


def private_page(final, body):
    """Staff-directory paths and form-only pages carry personal data (AGENTS.md §6): never stored. Same tests as the 2026-11-16 crawl."""
    if STAFF_PATH.search(urlsplit(final).path): return True
    if '<form' not in body.lower(): return False
    parser = Text(); parser.feed(re.sub(r'<form\b.*?</form>', '', body, flags=re.I | re.S))
    return len(words(' '.join(parser.parts))) < 80


def refused(target, current):
    """Status for a hop the fetcher will not request, else ''. An own-site fetch never lands on LinkedIn."""
    if not linkedin_url(current): return ''
    if not linkedin_url(target): return 'DOMAIN_BLOCKED'
    if SIGNIN_PATH.match(unquote(urlsplit(current).path)): return 'SIGNIN_WALL'
    return 'DOMAIN_BLOCKED' if linkedin_blocked(current) else ''


def verdict(flags):
    """robots_disallowed across redirect hops: yes if any hop's URL was disallowed, else unreadable if any hop's robots.txt was."""
    flags = flags - {''}
    return 'yes' if 'yes' in flags else 'unreadable' if 'unreadable' in flags else 'no' if flags else ''


def verify_click(page):
    """Click ONE positively identified plain verify-human control and nothing else: a button, checkbox or label whose own
    name says verify/human (not inside a form that asks for a password, email or text), or Cloudflare's Turnstile widget
    frame. Returns 1 if clicked."""
    def plain(loc):
        return loc.count() == 1 and loc.first.is_visible() and loc.first.evaluate(
            "e => { const f = e.closest('form'); return !(f && f.querySelector('input[type=password],input[type=email],input[type=text]')) }")
    try:
        for frame in page.frames:
            for loc in (frame.get_by_role('button', name=VERIFY), frame.get_by_role('checkbox', name=VERIFY), frame.get_by_label(VERIFY)):
                if plain(loc):
                    loc.first.click(timeout=3000); return 1
        for handle in page.query_selector_all('iframe'):
            src, box = urlsplit(handle.get_attribute('src') or ''), handle.bounding_box()
            if src.hostname in CHALLENGE_HOSTS and '/turnstile/' in src.path and box and 200 <= box['width'] <= 400 and 40 <= box['height'] <= 100:
                page.mouse.click(box['x'] + 28, box['y'] + box['height'] / 2); return 1  # its checkbox sits in a closed shadow root
    except Exception:
        pass
    return 0


def same_page(a, b):
    def identity(value):
        p = urlsplit(value)
        return (p.hostname.lower().removeprefix('www.'), p.port, p.path.rstrip('/'), p.query)
    return identity(a) == identity(b)


def key(value):
    return hashlib.sha256(value.encode()).hexdigest()


class Corpus:
    def __init__(self, cache_dir=DEFAULT_CACHE):
        self.cache = Path(cache_dir).resolve()
        if self.cache == ROOT or ROOT in self.cache.parents:
            raise ValueError('Cache must be outside the repository')
        self.cache.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def lock(self, name):
        with (self.cache / (name + '.lock')).open('a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            yield f

    @contextmanager
    def slot(self):
        # File locks coordinate all readers/crawlers sharing this cache, not just threads.
        while True:
            for i in range(8):
                f = (self.cache / f'slot-{i}.lock').open('a+')
                try:
                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    f.close(); continue
                try:
                    yield
                finally:
                    f.close()
                return
            time.sleep(.1)

    def request(self, target, delay=1):
        """L1 curl transport, with redirects handled by fetch so robots gates each hop."""
        if linkedin_blocked(target):
            raise ValueError('Only LinkedIn company pages may be requested')
        with self.lock('host-' + key(urlsplit(target).hostname)) as clock:
            clock.seek(0)
            last = float(clock.read() or 0)
            time.sleep(max(0, last - time.time()))
            with self.slot(), tempfile.TemporaryDirectory(dir=self.cache) as tmp:
                clock.seek(0); clock.truncate(); clock.write(str(time.time() + delay)); clock.flush()
                raw, headers = Path(tmp) / 'raw', Path(tmp) / 'headers'
                p = subprocess.run(['curl', '-q', '-sS', '-A', UA, '--max-time', '25',
                                    '--max-filesize', '12000000', '-D', str(headers), '-o', str(raw),
                                    '-w', '%{http_code}', target], capture_output=True, text=True)
                h = headers.read_text(errors='replace') if headers.exists() else ''
                retry = re.findall(r'(?im)^retry-after:\s*(\d+)', h)
                if retry:
                    clock.seek(0); clock.truncate(); clock.write(str(time.time() + max(delay, int(retry[-1])))); clock.flush()
                locations = re.findall(r'(?im)^location:\s*(.*?)\s*$', h)
                types = re.findall(r'(?im)^content-type:\s*(.*?)\s*$', h)
                return dict(code=int(p.stdout or 0), raw=raw.read_bytes() if raw.exists() else b'',
                            location=locations[-1] if locations else '',
                            content_type=types[-1] if types else '', error=p.stderr[:300], exit=p.returncode)

    def cached(self, target):
        meta = self.cache / (key(target) + '.json')
        if not meta.exists(): return None
        r = json.loads(meta.read_text())
        if r.get('extraction_version') != 3 or r.get('status') in STALE: return None
        r.setdefault('robots_disallowed', 'not_recorded')
        if r['url'] != target: raise ValueError('Cache URL mismatch')
        if hashlib.sha256((self.cache / r['raw_file']).read_bytes()).hexdigest() != r['sha256']:
            raise ValueError('Cache hash mismatch: ' + target)
        if hashlib.sha256((self.cache / r['text_file']).read_bytes()).hexdigest() != r['text_sha256']:
            raise ValueError('Cache text hash mismatch: ' + target)
        return r

    def blob(self, name, content):
        if (self.cache / name).exists(): return
        with tempfile.NamedTemporaryFile(dir=self.cache, delete=False) as f:
            f.write(content)
        Path(f.name).replace(self.cache / name)

    def fallback(self, target, delay):
        # A proxy read also consumes the original host's request budget.
        if linkedin_url(target):
            raise ValueError('LinkedIn pages are never read through a proxy')
        with self.lock('host-' + key(urlsplit(target).hostname)) as clock:
            clock.seek(0)
            time.sleep(max(0, float(clock.read() or 0) - time.time()))
            clock.seek(0); clock.truncate(); clock.write(str(time.time() + delay)); clock.flush()
            return self.request('https://r.jina.ai/' + target)

    def save(self, target, response, status, final, route, robots_disallowed=''):
        stem = key(target)
        raw = response.get('raw', b'')
        body = raw.decode('utf-8', 'replace')
        if status == 'ok' and urlsplit(target).path != '/robots.txt' and (private_page(final, body) or private_page(target, '')):
            response, raw, body, status = {}, b'', '', 'CONTACT_FORM_OR_STAFF_DIRECTORY'  # discarded before storage
        if route == 'jina':
            text = body.split('Markdown Content:', 1)[-1] if 'Markdown Content:' in body else ''
            source = re.search(r'(?m)^URL Source:\s*(https?://\S+)', body)
            final = source[1] if source else final
        elif 'html' in response.get('content_type', '') or '<html' in body.lower():
            parser = Text(); parser.feed(body); text = ' '.join(parser.parts)
        else:
            text = body
        if status == 'ok' and (not text.strip() or '\ufffd' in text or any(w in text.lower() for w in WALLS)):
            status = 'FETCH_FAILED'
        raw_name = hashlib.sha256(raw).hexdigest() + '.raw'
        text_name = hashlib.sha256(text.encode()).hexdigest() + '.txt'
        self.blob(raw_name, raw)
        self.blob(text_name, text.encode())
        r = dict(url=target, status=status, http_status=response.get('code', 0),
                 final_url=final, route=route, fetched_at=datetime.now(timezone.utc).isoformat(),
                 sha256=hashlib.sha256(raw).hexdigest(), raw_file=raw_name, text_file=text_name,
                 text_sha256=hashlib.sha256(text.encode()).hexdigest(), extraction_version=3,
                 error=response.get('error', ''), robots_disallowed=robots_disallowed)
        meta = self.cache / (stem + '.json.tmp')
        meta.write_text(json.dumps(r)); meta.replace(self.cache / (stem + '.json'))
        with self.lock('index'):
            dest = self.cache / 'index.csv'
            if dest.exists() and dest.read_text().split('\n', 1)[0] != ','.join(r): dest = self.cache / 'index-robots.csv'
            exists = dest.exists()
            with dest.open('a', newline='') as f:
                w = csv.DictWriter(f, list(r))
                if not exists: w.writeheader()
                w.writerow(r)
        return r

    def robots(self, target):
        """('yes'|'no'|'unreadable', crawl delay seconds). Informational: a Disallow never blocks a fetch (owner ruling 2026-11-24)."""
        p = urlsplit(target)
        robots = urlunsplit((p.scheme, p.netloc, '/robots.txt', '', ''))
        r = self.fetch(robots, robots=True)
        parser = RobotFileParser()
        if r['status'] == 'ok':
            parser.parse((self.cache / r['text_file']).read_text().splitlines())
            state = 'no' if parser.can_fetch(ROBOT_AGENT, target) else 'yes'
        else:
            parser.parse([])
            state = 'no' if r['http_status'] in (404, 410) else 'unreadable'  # unreadable: default 1 s delay, no block
        delay = max(1, parser.crawl_delay(ROBOT_AGENT) or 0)
        rate = parser.request_rate(ROBOT_AGENT)
        if rate: delay = max(delay, rate.seconds / rate.requests)
        return state, delay

    def policy(self, target):
        """What the pre-2026-11-24 rule would have decided: (allowed only when robots.txt was readable and allowed, delay)."""
        state, delay = self.robots(target)
        return state == 'no', delay

    def manual(self, target, final, code):
        with self.lock('manual'):
            dest = self.cache / 'manual-bot-check.csv'
            exists = dest.exists()
            with dest.open('a', newline='') as f:
                w = csv.writer(f)
                if not exists: w.writerow(['url', 'final_url', 'http_status', 'listed_at'])
                w.writerow([target, final, code, datetime.now(timezone.utc).isoformat()])

    BROWSER_WAIT = 30  # seconds the page gets to finish its own check

    def browser(self, target, delay=1, no_cookies=False):
        """Fresh local Chrome (no profile, cookies or login): waits out the page's own check and clicks one plain
        verify-human control. Never a puzzle, a solver service or a proxy. Same host clock and slots as request().
        Every navigation is checked before it loads: refused or staff-directory destinations and other hosts are aborted
        (the 'blocked' key says why), later same-host navigations are spaced by the delay. no_cookies (LinkedIn): documents
        only, cookies cleared after every response, and a Cookie header on any request fails the visit."""
        gone = dict(code=0, raw=b'', location='', content_type='', exit=127, unavailable=True, final_url=target)
        try: from playwright.sync_api import sync_playwright
        except ImportError: return dict(gone, error='PLAYWRIGHT_UNAVAILABLE')
        start = host_of(target)
        with self.lock('host-' + key(urlsplit(target).hostname)) as clock:
            clock.seek(0)
            time.sleep(max(0, float(clock.read() or 0) - time.time()))
            with self.slot(), sync_playwright() as pw:
                clock.seek(0); clock.truncate(); clock.write(str(time.time() + delay)); clock.flush()
                try: chrome = pw.chromium.launch(channel='chrome', headless=True)
                except Exception as e: return dict(gone, error=('CHROME_UNAVAILABLE: ' + str(e))[:300])
                try:
                    ctx = chrome.new_context(accept_downloads=False, service_workers='block')
                    page = ctx.new_page()
                    code, last, blocked, leaked = [0], [None], [], []
                    def guard(route):
                        req = route.request
                        if no_cookies and req.resource_type != 'document' or req.resource_type in ('image', 'font', 'media'):
                            return route.abort()
                        if req.is_navigation_request() and req.url.startswith(('http://', 'https://')):
                            main = req.frame.parent_frame is None
                            why = refused(target, req.url) or ('CONTACT_FORM_OR_STAFF_DIRECTORY' if STAFF_PATH.search(urlsplit(req.url).path) else '')
                            if not why and host_of(req.url) != start and (main or host_of(req.url) not in CHALLENGE_HOSTS):
                                why = 'CROSS_HOST_REDIRECT'
                            if why:
                                if main: blocked.append((why, req.url))
                                return route.abort()
                            if main:
                                if last[0] is not None: time.sleep(max(0, last[0] + delay - time.time()))
                                last[0] = time.time()
                        route.continue_()
                    ctx.route('**/*', guard)
                    def seen(resp):
                        if resp.frame == page.main_frame and resp.request.is_navigation_request(): code[0] = resp.status
                        if no_cookies: ctx.clear_cookies()
                    page.on('response', seen)
                    if no_cookies: page.on('request', lambda r: leaked.append(r.url) if 'cookie' in r.all_headers() else None)
                    error = ''
                    try: page.goto(target, wait_until='domcontentloaded', timeout=25000)
                    except Exception as e: error = str(e)[:300]
                    def html():  # None while the page is navigating
                        try: return page.content()
                        except Exception: return None
                    begin, clicks = time.time(), 0
                    while time.time() - begin < self.BROWSER_WAIT and not blocked:
                        now = html()
                        if now is not None and code[0] and not challenged(code[0], now): break
                        if time.time() - begin > 4 and not clicks: clicks += verify_click(page)
                        page.wait_for_timeout(1000)
                    try: page.wait_for_load_state('networkidle', timeout=5000)
                    except Exception: pass
                    final = html()
                    for _ in range(5):
                        if final is not None: break
                        page.wait_for_timeout(1000); final = html()
                    out = dict(code=code[0], raw=(final or '').encode(), location='', content_type='text/html', exit=0, error=error, final_url=page.url)
                    if blocked: return dict(out, raw=b'', blocked=blocked[0][0], final_url=blocked[0][1])
                    if leaked: return dict(out, raw=b'', error='COOKIE_SENT: ' + leaked[0], code=0)
                    return out
                finally:
                    chrome.close()

    def fetch(self, target, robots=False):
        target = url(target)
        robots = robots or urlsplit(target).path == '/robots.txt'
        with self.lock('url-' + key(target)):
            if why := refused(target, target):
                return self.save(target, {}, why, target, 'direct')
            cached = self.cached(target)
            if cached:
                if why := refused(target, cached['final_url']):
                    return self.save(target, {}, why, cached['final_url'], 'direct')
                return cached
            current, response, flags = target, {}, set()
            for _ in range(6):
                state, delay = ('', 1) if robots else self.robots(current)
                flags.add(state)
                response = self.request(current, delay)
                if response['code'] in (301, 302, 303, 307, 308) and response['location']:
                    current = url(urljoin(current, response['location']))
                    if why := refused(target, current):
                        return self.save(target, {}, why, current, 'direct', verdict(flags))
                    # Only robots paths are exempt from a destination robots check.
                    if robots and urlsplit(current).path != '/robots.txt': break
                    continue
                break
            seen = verdict(flags)
            if response.get('code') in (301, 302, 303, 307, 308):
                return self.save(target, response, 'FETCH_FAILED', current, 'direct', seen)
            if not robots and response.get('code') in BOT_CODES and challenged(response['code'], response['raw'].decode('utf-8', 'replace')):
                b = self.browser(current, delay, no_cookies=linkedin_url(target))
                if b.get('unavailable'):  # an unresolved bot check is for a person, never an ok receipt
                    self.manual(target, current, response['code'])
                    return self.save(target, dict(response, error=b['error']), 'BOT_CHECK_MANUAL', current, 'direct', seen)
                if b.get('blocked'): return self.save(target, {}, b['blocked'], b['final_url'], 'browser', seen)
                if why := refused(target, b['final_url']): return self.save(target, {}, why, b['final_url'], 'browser', seen)
                if b['error'].startswith('COOKIE_SENT'): return self.save(target, {}, 'FETCH_FAILED', b['final_url'], 'browser', seen)
                seen = verdict(flags | {self.robots(b['final_url'])[0]})  # the page may have moved within its host
                if challenged(b['code'], b['raw'].decode('utf-8', 'replace')):
                    self.manual(target, b['final_url'], b['code'])
                    return self.save(target, b, 'BOT_CHECK_MANUAL', b['final_url'], 'browser', seen)
                return self.save(target, b, 'ok' if b['code'] == 200 else 'FETCH_FAILED', b['final_url'], 'browser', seen)
            if response.get('exit') == 0 and response.get('code') == 200:
                r = self.save(target, response, 'ok', current, 'direct', seen)
                if r['status'] in ('ok', 'CONTACT_FORM_OR_STAFF_DIRECTORY') or robots: return r  # an excluded page is not retried through a proxy
            if not robots and response.get('code') != 429 and urlsplit(current).hostname != 'r.jina.ai' and not linkedin_url(current):
                fallback = self.fallback(current, delay)
                if fallback['code'] == 200 and fallback['exit'] == 0:
                    source = re.search(r'(?m)^URL Source:\s*(https?://\S+)', fallback['raw'].decode('utf-8', 'replace'))
                    if not source or not same_page(current, source[1]):
                        return self.save(target, fallback, 'WRONG_PAGE', current, 'jina', seen)
                    return self.save(target, fallback, 'ok', current, 'jina', verdict(flags | {self.robots(source[1])[0]}))
            return self.save(target, response, 'FETCH_FAILED', current, 'direct', seen)

    def rawcheck(self, target, quote):
        """Return yes/no/unfetchable; a fetch failure says nothing about the claim."""
        if not words(quote): return 'no_quote'
        r = self.fetch(target)
        if r['status'] == 'WRONG_PAGE': return 'wrong_page'
        if r['status'] != 'ok': return 'unfetchable'
        if not same_page(target, r['final_url']): return 'wrong_page'
        return 'yes' if on_page(quote, (self.cache / r['text_file']).read_text()) else 'no'

    def crawl(self, website):
        origin = urlsplit(website)
        website = urlunsplit((origin.scheme, origin.netloc, '/', '', ''))
        home = self.fetch(website)
        base = home['final_url'] if home['status'] == 'ok' else website
        p = urlsplit(base)
        sitemap = self.fetch(urlunsplit((p.scheme, p.netloc, '/sitemap.xml', '', '')))
        links = []
        if home['status'] == 'ok':
            parser = Text(); parser.feed((self.cache / home['raw_file']).read_text(errors='replace'))
            links.extend(urljoin(base, link) for link in parser.links)
        maps = [sitemap]
        for receipt in maps:
            if receipt['status'] != 'ok': continue
            try: tree = ET.fromstring((self.cache / receipt['raw_file']).read_bytes())
            except ET.ParseError: continue
            locs = [e.text.strip() for e in tree.iter() if e.tag.split('}')[-1] == 'loc' and e.text]
            if tree.tag.split('}')[-1] == 'sitemapindex':
                # shortcut: at most two sitemap children; expand only if coverage warrants it.
                if len(maps) == 1:
                    maps.extend(self.fetch(loc) for loc in locs[:2] if urlsplit(loc).netloc == p.netloc)
            else: links.extend(locs)
        candidates = sorted({url(link) for link in links if urlsplit(link).scheme in ('http', 'https')
                             and urlsplit(link).netloc == p.netloc and not urlsplit(link).query}, key=lambda x: (len(x), x))
        selected = set()
        pages = {'home': home['status']}
        for kind, pattern in KINDS.items():
            match = next((x for x in candidates if x not in selected and re.search(pattern, urlsplit(x).path, re.I)), None)
            if match:
                selected.add(match); pages[kind] = self.fetch(match)['status']
            else: pages[kind] = 'NOT_DISCOVERED'
        return pages


def rawcheck(target, quote, cache_dir=DEFAULT_CACHE):
    return Corpus(cache_dir).rawcheck(target, quote)


def read(path):
    with path.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))


def frame(root=ROOT):
    pic = {r['org_id'] for p in (root / 'data').glob('sites_*.csv') for r in read(p)
           if r['state'] == 'OH' and r['county'].removesuffix(' County') in PIC18}
    orgs = [r for p in (root / 'data').glob('organizations_*.csv') for r in read(p)]
    assert len(orgs) == len({r['org_id'] for r in orgs}), 'Duplicate org IDs'
    rows = []
    for r in orgs:
        if not r['website'].startswith(('http://', 'https://')): continue
        if r['org_id'] not in pic and not r['tier1_qualifier'] and r['status'] != 'active': continue
        group = 'PIC18' if r['org_id'] in pic else 'Tier1' if r['tier1_qualifier'] else 'active'
        rows.append(dict(org_id=r['org_id'], website=url(r['website']), group=group))
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['crawl', 'rawcheck'])
    p.add_argument('args', nargs='*')
    p.add_argument('--cache-dir', type=Path, default=DEFAULT_CACHE)
    a = p.parse_args(); corpus = Corpus(a.cache_dir)
    if a.command == 'rawcheck':
        if len(a.args) != 2: p.error('rawcheck needs URL and QUOTE')
        print(corpus.rawcheck(*a.args)); return
    rows = frame()
    coverage = corpus.cache / 'coverage.csv'
    with corpus.lock('crawl'), coverage.open('w', newline='') as f:
        w = csv.DictWriter(f, ['org_id', 'website', 'group', 'home', *KINDS, 'error'])
        w.writeheader(); f.flush()
        for group in ('PIC18', 'Tier1', 'active'):
            batch = [r for r in rows if r['group'] == group]
            def work(r):
                try: return dict(r, **corpus.crawl(r['website']), error='')
                except Exception as e: return dict(r, error=f'{type(e).__name__}: {e}')
            with ThreadPoolExecutor(max_workers=8) as pool:
                for result in pool.map(work, batch):
                    w.writerow(result); f.flush()
                    print(json.dumps(result), flush=True)
            print(group, len(batch), 'selected organizations with website processed', flush=True)


if __name__ == '__main__': main()
