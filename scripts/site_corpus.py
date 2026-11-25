#!/usr/bin/env python3
"""Shared own-site corpus. No canonical data writes; cache must stay outside the repo.

Promotes L1 run.py's curl transport, Text extraction, hash receipts and challenge
checks, and evidence-audit analyze.py's calibrated contiguous-word matcher.
Owner ruling 2026-11-24: robots.txt no longer blocks a fetch (it is read for Crawl-delay and receipted as
robots_disallowed yes/no/unreadable across every redirect hop), a bot-check page is receipted BOT_CHECK_MANUAL and listed
for a person (a browser retry waits for its own PR), and LinkedIn company pages are fetchable logged out, with no cookies. Kept: the per-host rate limit, no solver services, no personal profiles.
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
HTTP1_RETRY = (35, 60, 92)  # curl exits worth one HTTP/1.1 retry: SSL connect, certificate chain, HTTP/2 stream error
BOT_CODES = (200, 403, 503, 999)  # 999 is LinkedIn's refusal; a bot check shows on these codes only
# shortcut: markers copied from scripts/liveness_sweep.py (importing it pulls in the whole sweep); merge if either list grows.
BOT_TITLES = ('just a moment', 'attention required', 'access denied', 'are you a robot', 'pardon our interruption',
              'verify you are human', 'security check', 'captcha', 'ddos protection', 'request blocked')
BOT_BODY = ('g-recaptcha', 'h-captcha', 'hcaptcha.com', 'px-captcha', 'cf-challenge', 'challenge-platform',
            'cdn-cgi/challenge', 'enable javascript and cookies to continue', 'incapsula incident',
            'sucuri website firewall', 'akamai reference')
SIGNIN_PATH = re.compile(r'/(?:authwall|login|uas/|checkpoint)', re.I)
STAFF_PATH = re.compile(r'/(?:staff-directory|employee-directory|our-team|team|staff)/?$', re.I)
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


# A LinkedIn company page is never stored. Only these fields of it are: the page's own labelled fields and a flat JSON-LD
# Organization. Everything else (employees, posts, nested objects, scripts, markup) is dropped.
LI_FIELDS = {'about-us__description': 'description', 'about-us__website': 'website', 'about-us__industry': 'industry',
             'about-us__size': 'company_size', 'about-us__headquarters': 'headquarters', 'about-us__foundedOn': 'founded',
             'about-us__specialties': 'specialties'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
LI_ADDRESS = ('streetAddress', 'addressLocality', 'addressRegion', 'postalCode', 'addressCountry')
GENERIC = {'info', 'sales', 'contact', 'support', 'office', 'hello', 'customerservice', 'marketing', 'privacy', 'webmaster',
           'enquiries', 'inquiries', 'service', 'hr', 'careers', 'orders'}


def li_extract_only(raw):
    """True if these bytes are an allowlisted LinkedIn extract (flat JSON of the allowed keys) or empty; anything else is a legacy page."""
    if not raw: return True
    try: d = json.loads(raw)
    except ValueError: return False
    keys = {'source_url', 'name', 'description', 'website', 'industry', 'company_size', 'headquarters', 'address', 'founded', 'specialties'}
    return isinstance(d, dict) and set(d) <= keys and all(
        isinstance(v, str) or (k == 'address' and isinstance(v, dict) and set(v) <= set(LI_ADDRESS) and all(isinstance(x, str) for x in v.values()))
        for k, v in d.items())


def li_clean(value, cap=300):
    text = re.sub(r'\s+', ' ', value).strip()[:cap]
    return re.sub(r'[\w.+-]{1,80}@[\w.-]{1,160}\.[a-zA-Z]{2,20}', lambda m: m[0] if m[0].split('@')[0].lower() in GENERIC else '[redacted]', text)


class LinkedinExtract(HTMLParser):
    """Collects the text of the allowlisted `about-us__*` fields and the JSON-LD Organization's flat fields; nothing else."""
    def __init__(self):
        super().__init__(convert_charrefs=True); self.fields = {}; self.field = None; self.depth = 0; self.skip = 0; self.ld = None; self.script = False; self.org = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'script':
            self.script = True
            self.ld = [] if 'ld+json' in a.get('type', '') else None; return
        if self.field:
            if tag not in VOID:
                self.depth += 1
                if tag in ('dt', 'icon', 'script', 'style') or (tag == 'p' and self.field != 'description'): self.skip += 1
            return
        if a.get('data-test-id') in LI_FIELDS and tag not in VOID:
            self.field, self.depth, self.skip = LI_FIELDS[a['data-test-id']], 1, 0

    def handle_endtag(self, tag):
        if tag == 'script': self.script = False
        if tag == 'script' and self.ld is not None:
            try:
                d = json.loads(''.join(self.ld)); graph = d.get('@graph', [d]) if isinstance(d, dict) else d
                org = next(g for g in graph if isinstance(g, dict) and g.get('@type') in ('Organization', 'Corporation', 'LocalBusiness'))
                self.org = {k: org[k] for k in ('name', 'description', 'foundingDate') if isinstance(org.get(k), str)}
                if isinstance(org.get('address'), dict):
                    self.org['address'] = {k: org['address'][k] for k in LI_ADDRESS if isinstance(org['address'].get(k), str)}
            except (ValueError, AttributeError, StopIteration): pass
            self.ld = None
        elif self.field:
            if tag in ('dt', 'icon', 'script', 'style') or (tag == 'p' and self.field != 'description'): self.skip = max(0, self.skip - 1)
            self.depth -= 1
            if self.depth == 0: self.field = None

    def handle_data(self, data):
        if self.ld is not None: self.ld.append(data)
        elif self.field and not self.skip and not self.script: self.fields[self.field] = self.fields.get(self.field, '') + ' ' + data

    def result(self, source):
        """The allowlisted extract, or None when the page gave no name and no field (a wall, an error, a changed page)."""
        out = {'source_url': source}
        for k in ('name', 'description', 'foundingDate'):
            if self.org.get(k): out[{'foundingDate': 'founded'}.get(k, k)] = li_clean(self.org[k], 3000 if k == 'description' else 300)
        if self.org.get('address'): out['address'] = {k: li_clean(v) for k, v in self.org['address'].items()}
        for k, v in self.fields.items():
            if li_clean(v): out[k] = li_clean(v, 3000 if k == 'description' else 300)  # the page's own labelled text wins over JSON-LD
        return out if len(out) > 1 else None


def reader_challenged(body):
    """Jina's markdown form of a bot check: its Title line and text go through the same detector as a direct page."""
    title = re.search(r'(?m)^Title:\s*(.*)$', body)
    text = body.split('Markdown Content:', 1)[-1]
    return challenged(200, f'<title>{title[1] if title else ""}</title><p>{text}</p>') or (
        len(words(text)) < 80 and bool(re.search(r'captcha|verify you are human|are you a robot|security check', text, re.I)))


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


def same_page(a, b):
    def identity(value):
        p = urlsplit(value)
        return (p.hostname.lower().removeprefix('www.'), p.port, p.path.rstrip('/'), p.query)
    return identity(a) == identity(b)


def key(value):
    return hashlib.sha256(value.encode()).hexdigest()


PURGED = set()  # caches already swept for legacy LinkedIn pages in this process


class Corpus:
    def __init__(self, cache_dir=DEFAULT_CACHE):
        self.cache = Path(cache_dir).resolve()
        if self.cache == ROOT or ROOT in self.cache.parents:
            raise ValueError('Cache must be outside the repository')
        self.cache.mkdir(parents=True, exist_ok=True)
        self.memo = {}  # robots.txt bodies: in memory only
        if self.cache not in PURGED:
            PURGED.add(self.cache); self.purge_linkedin()

    @contextmanager
    def lock(self, name):
        with (self.cache / (name + '.lock')).open('a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            yield f

    @contextmanager
    def slot(self, pool='slot', n=8):
        # File locks coordinate all readers/crawlers sharing this cache, not just threads.
        while True:
            for i in range(n):
                f = (self.cache / f'{pool}-{i}.lock').open('a+')
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

    def request(self, target, delay=1, http1=False):
        """L1 curl transport, with redirects handled by fetch so robots gates each hop."""
        if linkedin_blocked(target):
            raise ValueError('Only LinkedIn company pages may be requested')
        with self.lock('host-' + key(urlsplit(target).hostname)) as clock:
            clock.seek(0)
            last = float(clock.read() or 0)
            time.sleep(max(0, last - time.time()))
            with self.slot():
                clock.seek(0); clock.truncate(); clock.write(str(time.time() + delay)); clock.flush()
                cmd = ['curl', '-q', '-sS', '-A', UA, '--max-time', '25', '--max-filesize', '12000000'] + (['--http1.1'] if http1 else [])
                if urlsplit(target).path == '/robots.txt':
                    # robots.txt never touches disk: headers and body come back on stdout, no -o file, no -D file, no temp dir.
                    p = subprocess.run(cmd + ['-i', '-o', '-', '-w', '\n%{http_code}', target], capture_output=True)
                    out, _, status = p.stdout.rpartition(b'\n')
                    h, _, body = out.partition(b'\r\n\r\n')
                    h = h.decode('utf-8', 'replace'); error = p.stderr.decode('utf-8', 'replace')[:300]; code = int(status or 0)
                else:
                    with tempfile.TemporaryDirectory(dir=self.cache) as tmp:
                        raw, headers = Path(tmp) / 'raw', Path(tmp) / 'headers'
                        p = subprocess.run(cmd + ['-D', str(headers), '-o', str(raw), '-w', '%{http_code}', target], capture_output=True, text=True)
                        h = headers.read_text(errors='replace') if headers.exists() else ''
                        body = raw.read_bytes() if raw.exists() else b''
                    error = p.stderr[:300]; code = int(p.stdout or 0)
                retry = re.findall(r'(?im)^retry-after:\s*(\d+)', h)
                if retry:
                    clock.seek(0); clock.truncate(); clock.write(str(time.time() + max(delay, int(retry[-1])))); clock.flush()
                locations = re.findall(r'(?im)^location:\s*(.*?)\s*$', h)
                types = re.findall(r'(?im)^content-type:\s*(.*?)\s*$', h)
                return dict(code=code, raw=body, location=locations[-1] if locations else '',
                            content_type=types[-1] if types else '', error=error, exit=p.returncode)

    def legacy_linkedin(self, r):
        """A LinkedIn receipt whose stored file is not an allowlisted extract: written before the extract-only rule."""
        if not (linkedin_url(r.get('url', '')) or linkedin_url(r.get('final_url', ''))) or not r.get('raw_file'): return False
        f = self.cache / Path(r['raw_file']).name
        return f.exists() and not li_extract_only(f.read_bytes())

    def purge(self, r, meta):
        for name in (r.get('raw_file'), r.get('text_file')):
            if name: (self.cache / Path(name).name).unlink(missing_ok=True)
        meta.unlink(missing_ok=True)

    def purge_linkedin(self):
        """Once per cache per process: delete every legacy LinkedIn page (raw, text and receipt), so none can replay."""
        for meta in self.cache.glob('*.json'):
            try: r = json.loads(meta.read_text())
            except ValueError: continue
            if isinstance(r, dict) and self.legacy_linkedin(r): self.purge(r, meta)

    def cached(self, target):
        meta = self.cache / (key(target) + '.json')
        if not meta.exists(): return None
        r = json.loads(meta.read_text())
        if r.get('extraction_version') != 3 or r.get('status') in STALE: return None
        if r.get('status') == 'BOT_CHECK_MANUAL' and not r.get('browser_tried'): return None  # written before the browser retry: try it once
        if self.legacy_linkedin(r): self.purge(r, meta); return None  # never replayed
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

    def save(self, target, response, status, final, route, robots_disallowed='', browser_tried=''):
        stem = key(target)
        raw = response.get('raw', b'')
        body = raw.decode('utf-8', 'replace')
        code = dict(code=response.get('code', 0))
        if private_page(final, body) or private_page(target, ''):
            # Discarded before storage, whatever the status: a failed or manual receipt must not keep the body either.
            response, raw, body = code, b'', ''
            if status == 'ok': status = 'CONTACT_FORM_OR_STAFF_DIRECTORY'
        elif linkedin_url(final) or linkedin_url(target):
            # Never the raw page: only the allowlisted extract of a company page that was ok, at no other status.
            extract = None
            if status == 'ok' and linkedin_company_page(final):
                page = LinkedinExtract(); page.feed(body); extract = page.result(final)
            response, raw, body = code, b'', ''
            if extract:
                raw = json.dumps(extract, indent=1, ensure_ascii=False).encode(); body = raw.decode()
                response = dict(code=code['code'], raw=raw, content_type='application/json')
            elif status == 'ok': status = 'FETCH_FAILED'
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
        if status != 'ok' or '/robots.txt' in (urlsplit(target).path, urlsplit(final).path):
            # Storage is decided after the final classification: no body for any non-ok status, and robots.txt is receipt-only.
            if status == 'ok': status = 'FETCH_FAILED'
            raw, text = b'', ''
        raw_name = hashlib.sha256(raw).hexdigest() + '.raw'
        text_name = hashlib.sha256(text.encode()).hexdigest() + '.txt'
        self.blob(raw_name, raw)
        self.blob(text_name, text.encode())
        r = dict(url=target, status=status, http_status=response.get('code', 0),
                 final_url=final, route=route, fetched_at=datetime.now(timezone.utc).isoformat(),
                 sha256=hashlib.sha256(raw).hexdigest(), raw_file=raw_name, text_file=text_name,
                 text_sha256=hashlib.sha256(text.encode()).hexdigest(), extraction_version=3,
                 error=response.get('error', ''), robots_disallowed=robots_disallowed, browser_tried=browser_tried)
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

    def wait_host(self, hostname, delay, retry_after=0):
        """Per-host pacing for a request that is not curl's own: wait out the host clock, then book the next slot, or
        the server's Retry-After if that is longer (as curl's transport does)."""
        with self.lock('host-' + key(hostname)) as clock:
            clock.seek(0)
            time.sleep(max(0, float(clock.read() or 0) - time.time()))
            clock.seek(0); clock.truncate(); clock.write(str(time.time() + max(delay, retry_after))); clock.flush()

    def hop(self, current, delay):
        """One transport step: curl, and if it fails on the TLS handshake, the certificate chain or HTTP/2 (whatever the
        HTTP status curl had read), once more over HTTP/1.1. The retry's response is processed like any other.
        Certificate verification stays on."""
        response = self.request(current, delay)
        if response.get('exit') in HTTP1_RETRY: response = self.request(current, delay, http1=True)
        return response

    BROWSER_WAIT = 30  # seconds the page gets to finish its own check

    def guard(self, ev, st):
        """Decides one request that Chrome paused at the CDP Fetch stage. Returns ('fail', None), ('continue', headers) or,
        for a response, ('response', headers). `st`: target, start host, main frame id, delay, flags, blocked, code.
        Only the main frame's documents are admitted; a child frame, popup, script, image, XHR or font is failed, so no
        target exists that this guard does not see."""
        u, rid = ev['request']['url'], ev['requestId']
        if 'responseStatusCode' in ev or 'responseErrorReason' in ev:  # response stage
            status = ev.get('responseStatusCode', 0)
            if ev['resourceType'] == 'Document' and ev['frameId'] == st['main'] and not 300 <= status < 400: st['code'] = status
            wait = [h['value'] for h in ev.get('responseHeaders', []) if h['name'].lower() == 'retry-after']
            if wait and wait[0].strip().isdigit(): self.wait_host(urlsplit(u).hostname, 0, min(int(wait[0]), 3600))  # Retry-After counts for browser hops too
            return 'response', [h for h in ev.get('responseHeaders', []) if h['name'].lower() != 'set-cookie']
        why = ''
        if ev['resourceType'] != 'Document' or not u.startswith(('http://', 'https://')) or ev['frameId'] != st['main']: why = 'SKIP'
        elif refused(st['target'], u): why = refused(st['target'], u)
        elif STAFF_PATH.search(urlsplit(u).path): why = 'CONTACT_FORM_OR_STAFF_DIRECTORY'
        elif urlsplit(u).path == '/robots.txt': why = 'ROBOTS_TXT_IS_RECEIPT_ONLY'
        elif host_of(u) != st['start'] and 'redirectedRequestId' not in ev: why = 'CROSS_HOST_NAVIGATION'
        if why:
            if why != 'SKIP': st['blocked'].append((why, u))
            return 'fail', None
        state, hop_delay = self.robots(u)  # robots state and the host's own Crawl-delay, for this hop
        st['flags'].add(state)
        self.wait_host(urlsplit(u).hostname, max(st['delay'], hop_delay))
        return 'continue', [{'name': k, 'value': v} for k, v in ev['request'].get('headers', {}).items() if k.lower() != 'cookie']

    def browser(self, target, delay=1):
        """One headed local Chrome visit (it opens a window on this machine): fresh context, no profile, no clicks, no typing.
        Every request is paused at the CDP Fetch stage and decided by `guard` before it is sent, HTTP redirect hops included.
        Chrome is started with site isolation off and popups blocked, and any extra page fails the visit, so the one guarded
        session sees every request. Cookies: Set-Cookie is stripped from every response, the jar is emptied before every
        request, a Cookie header is stripped from every request, and document.cookie is a no-op. Returns the rendered main document with
        the robots states seen (`flags`) and, if a hop was refused, why (`blocked`)."""
        gone = dict(code=0, raw=b'', location='', content_type='', exit=127, unavailable=True, final_url=target, flags=set(), blocked='')
        try: from playwright.sync_api import sync_playwright
        except ImportError: return dict(gone, error='PLAYWRIGHT_UNAVAILABLE')
        # Its own two-slot pool: a visit never holds a curl slot, so the robots lookups it triggers cannot deadlock on one.
        with self.slot('browser-slot', 2), sync_playwright() as pw:
            try:
                chrome = pw.chromium.launch(channel='chrome', headless=False, args=[
                    '--disable-site-isolation-trials', '--disable-features=IsolateOrigins,site-per-process', '--block-new-web-contents'])
            except Exception as e: return dict(gone, error=('CHROME_UNAVAILABLE: ' + str(e))[:300])
            try:
                ctx = chrome.new_context(accept_downloads=False, service_workers='block')
                ctx.add_init_script("Object.defineProperty(document, 'cookie', {get() { return '' }, set(v) {}}); window.open = () => null")
                extra = []
                ctx.on('page', lambda pg: extra.append(pg.url))
                page = ctx.new_page(); cdp = ctx.new_cdp_session(page)
                cdp.send('Network.enable')
                st = dict(target=target, start=host_of(target), main=cdp.send('Page.getFrameTree')['frameTree']['frame']['id'],
                          delay=delay, flags=set(), blocked=[], code=0)
                extra.clear()  # the guarded page itself

                def paused(ev):
                    try:
                        act, headers = self.guard(ev, st)
                        if act == 'response':
                            cdp.send('Fetch.continueResponse', {'requestId': ev['requestId'], 'responseCode': ev.get('responseStatusCode', 200), 'responseHeaders': headers})
                        elif act == 'continue':
                            cdp.send('Network.clearBrowserCookies')
                            cdp.send('Fetch.continueRequest', {'requestId': ev['requestId'], 'headers': headers})
                        else: cdp.send('Fetch.failRequest', {'requestId': ev['requestId'], 'errorReason': 'BlockedByClient'})
                    except Exception:
                        try: cdp.send('Fetch.failRequest', {'requestId': ev['requestId'], 'errorReason': 'Failed'})
                        except Exception: pass

                cdp.on('Fetch.requestPaused', paused)
                cdp.send('Fetch.enable', {'patterns': [{'urlPattern': '*', 'requestStage': 'Request'}, {'urlPattern': '*', 'requestStage': 'Response'}]})
                error = ''
                try: page.goto(target, wait_until='domcontentloaded', timeout=25000)
                except Exception as e: error = str(e)[:300]
                if error and not st['code'] and not st['blocked']:  # the navigation itself failed (certificate, DNS, reset): nothing to wait for
                    return dict(gone, unavailable=False, exit=0, error=error, flags=st['flags'])

                def html():  # None while the page is navigating
                    try: return page.content()
                    except Exception: return None
                begin = time.time()
                while time.time() - begin < self.BROWSER_WAIT and not st['blocked'] and not extra:
                    now = html()
                    if now is not None and st['code'] and not challenged(st['code'], now): break
                    page.wait_for_timeout(1000)
                final = html()
                for _ in range(5):
                    if final is not None: break
                    page.wait_for_timeout(1000); final = html()
                if extra:  # a second page opened: its requests were never guarded, so nothing from this visit is kept
                    return dict(gone, unavailable=False, exit=0, error='EXTRA_PAGE_OPENED', flags=st['flags'])
                if st['blocked']:
                    return dict(gone, unavailable=False, exit=0, error=error, flags=st['flags'], blocked=st['blocked'][0][0], final_url=st['blocked'][0][1])
                return dict(code=st['code'], raw=(final or '').encode(), location='', content_type='text/html', exit=0, error=error,
                            final_url=page.url, flags=st['flags'], blocked='')
            finally:
                chrome.close()

    def visit(self, target, current, delay, flags, response, kind):
        """The one browser retry of a page curl could not read (kind 'challenge': a bot check; 'tls': a certificate chain or
        handshake curl rejects). Only an ok document is stored; refused hops, bot checks and error pages never are, and every
        receipt written after a real browser run is marked browser_tried."""
        b = self.browser(current, delay)
        seen = verdict(flags | b.get('flags', set()))
        note = dict(code=response.get('code', 0), error=b.get('error', ''))
        if b.get('unavailable'):
            if kind == 'challenge': self.manual(target, current, response.get('code', 0))
            return self.save(target, note, 'BOT_CHECK_MANUAL' if kind == 'challenge' else 'FETCH_FAILED', current, 'direct', seen)
        tried = 'yes'
        if b['blocked']: return self.save(target, note, b['blocked'], b['final_url'], 'browser', seen, tried)
        if b['error'].startswith('EXTRA_PAGE_OPENED'): return self.save(target, note, 'FETCH_FAILED', current, 'browser', seen, tried)
        if why := refused(target, b['final_url']): return self.save(target, note, why, b['final_url'], 'browser', seen, tried)
        if not b['code'] or not b['final_url'].startswith(('http://', 'https://')):  # no document came back
            return self.save(target, dict(note, error=b.get('error', '') or note['error']), 'FETCH_FAILED', current, 'browser', seen, tried)
        seen = verdict(flags | b['flags'] | {self.robots(b['final_url'])[0]})
        if challenged(b['code'], b['raw'].decode('utf-8', 'replace')):
            self.manual(target, b['final_url'], b['code'])
            return self.save(target, dict(note, code=b['code']), 'BOT_CHECK_MANUAL', b['final_url'], 'browser', seen, tried)
        if b['code'] != 200: return self.save(target, dict(note, code=b['code']), 'FETCH_FAILED', b['final_url'], 'browser', seen, tried)
        return self.save(target, b, 'ok', b['final_url'], 'browser', seen, tried)

    def robots_rules(self, target):
        """(receipt, text) for the host's robots.txt. The body is parsed in memory and NEVER written to disk, whatever it
        holds; only a receipt (url, final_url, status, http_status, bytes, sha256, fetched_at) goes to robots-<key>.json."""
        p = urlsplit(target)
        robots = urlunsplit((p.scheme, p.netloc, '/robots.txt', '', ''))
        with self.lock('url-' + key(robots)):
            if robots in self.memo: return self.memo[robots]
            current, response = robots, {}
            for _ in range(6):
                if refused(robots, current): response = {}; break
                response = self.hop(current, 1)
                if response['code'] in (301, 302, 303, 307, 308) and response['location']:
                    current = url(urljoin(current, response['location']))
                    if urlsplit(current).path != '/robots.txt': break  # only robots paths are followed
                    continue
                break
            raw, code = response.get('raw', b''), response.get('code', 0)
            ok = response.get('exit') == 0 and code == 200
            receipt = dict(url=robots, final_url=current, status='ok' if ok else 'FETCH_FAILED', http_status=code, bytes=len(raw),
                           sha256=hashlib.sha256(raw).hexdigest(), fetched_at=datetime.now(timezone.utc).isoformat(), route='direct',
                           raw_file='', text_file='', robots_disallowed='', error=response.get('error', ''))
            meta = self.cache / ('robots-' + key(robots) + '.json.tmp')
            meta.write_text(json.dumps(receipt)); meta.replace(self.cache / ('robots-' + key(robots) + '.json'))
            self.memo[robots] = receipt, (raw.decode('utf-8', 'replace') if ok else '')
            return self.memo[robots]

    def robots(self, target):
        """('yes'|'no'|'unreadable', crawl delay seconds). Informational: a Disallow never blocks a fetch (owner ruling 2026-11-24)."""
        receipt, text = self.robots_rules(target)
        parser = RobotFileParser()
        if receipt['status'] == 'ok':
            parser.parse(text.splitlines())
            state = 'no' if parser.can_fetch(ROBOT_AGENT, target) else 'yes'
        else:
            parser.parse([])
            state = 'no' if receipt['http_status'] in (404, 410) else 'unreadable'  # unreadable: default 1 s delay, no block
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

    def fetch(self, target):
        target = url(target)
        if urlsplit(target).path == '/robots.txt': return self.robots_rules(target)[0]  # receipt only, no body on disk
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
                state, delay = self.robots(current)
                flags.add(state)
                response = self.hop(current, delay)
                if response['code'] in (301, 302, 303, 307, 308) and response['location']:
                    current = url(urljoin(current, response['location']))
                    if why := refused(target, current):
                        return self.save(target, {}, why, current, 'direct', verdict(flags))
                    continue
                break
            seen = verdict(flags)
            if response.get('code') in (301, 302, 303, 307, 308):
                return self.save(target, response, 'FETCH_FAILED', current, 'direct', seen)
            if response.get('code') in BOT_CODES and challenged(response['code'], response['raw'].decode('utf-8', 'replace')):
                return self.visit(target, current, delay, flags, response, 'challenge')
            if response.get('code') == 0 and response.get('exit') in (35, 60):  # handshake or chain still rejected over HTTP/1.1: Chrome may do better
                return self.visit(target, current, delay, flags, response, 'tls')
            if response.get('exit') == 0 and response.get('code') == 200:
                r = self.save(target, response, 'ok', current, 'direct', seen)
                if r['status'] in ('ok', 'CONTACT_FORM_OR_STAFF_DIRECTORY'): return r  # an excluded page is not retried through a proxy
            if private_page(current, response.get('raw', b'').decode('utf-8', 'replace')):
                return self.save(target, response, 'FETCH_FAILED', current, 'direct', seen)  # never forwarded to a reader
            if response.get('code') != 429 and urlsplit(current).hostname != 'r.jina.ai' and not linkedin_url(current):
                fallback = self.fallback(current, delay)
                if fallback['code'] == 200 and fallback['exit'] == 0:
                    source = re.search(r'(?m)^URL Source:\s*(https?://\S+)', fallback['raw'].decode('utf-8', 'replace'))
                    if not source or not same_page(current, source[1]):
                        return self.save(target, fallback, 'WRONG_PAGE', current, 'jina', seen)
                    if reader_challenged(fallback['raw'].decode('utf-8', 'replace')):  # the reader met a bot check: Chrome tries the original URL; its body is never stored
                        return self.visit(target, current, delay, flags, dict(code=200), 'challenge')
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
