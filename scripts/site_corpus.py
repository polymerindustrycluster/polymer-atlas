#!/usr/bin/env python3
"""Shared own-site corpus. No canonical data writes; cache must stay outside the repo.

Promotes L1 run.py's curl transport, Text extraction, hash receipts and challenge
checks, and evidence-audit analyze.py's calibrated contiguous-word matcher.
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
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

from regions import PIC18

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/cache/site_corpus')
UA = 'Mozilla/5.0 (compatible; AtlasSiteCorpus/1.0)'
KINDS = {
    'about': r'about|company|who-we-are',
    'locations': r'contact|location|facilit',
    'news': r'news|press',
    'quality': r'quality|certificat',
    'markets': r'industr|market',
    'products': r'product|capabilit|process|service',
}
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
    p = urlsplit(value)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
        raise ValueError('Expected an HTTP(S) URL without credentials')
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or '/', p.query, ''))


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
        with self.lock('host-' + key(urlsplit(target).hostname)) as clock:
            clock.seek(0)
            last = float(clock.read() or 0)
            time.sleep(max(0, last - time.time()))
            with self.slot(), tempfile.TemporaryDirectory(dir=self.cache) as tmp:
                clock.seek(0); clock.truncate(); clock.write(str(time.time() + delay)); clock.flush()
                raw, headers = Path(tmp) / 'raw', Path(tmp) / 'headers'
                p = subprocess.run(['curl', '-sS', '-A', UA, '--max-time', '25',
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
        if r.get('extraction_version') != 2: return None
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
        with self.lock('host-' + key(urlsplit(target).hostname)) as clock:
            clock.seek(0)
            time.sleep(max(0, float(clock.read() or 0) - time.time()))
            clock.seek(0); clock.truncate(); clock.write(str(time.time() + delay)); clock.flush()
            return self.request('https://r.jina.ai/' + target)

    def save(self, target, response, status, final, route):
        stem = key(target)
        raw = response.get('raw', b'')
        body = raw.decode('utf-8', 'replace')
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
                 text_sha256=hashlib.sha256(text.encode()).hexdigest(), extraction_version=2,
                 error=response.get('error', ''))
        meta = self.cache / (stem + '.json.tmp')
        meta.write_text(json.dumps(r)); meta.replace(self.cache / (stem + '.json'))
        with self.lock('index'):
            dest = self.cache / 'index.csv'
            exists = dest.exists()
            with dest.open('a', newline='') as f:
                w = csv.DictWriter(f, list(r))
                if not exists: w.writeheader()
                w.writerow(r)
        return r

    def policy(self, target):
        p = urlsplit(target)
        robots = urlunsplit((p.scheme, p.netloc, '/robots.txt', '', ''))
        r = self.fetch(robots, robots=True)
        parser = RobotFileParser()
        if r['status'] == 'ok':
            parser.parse((self.cache / r['text_file']).read_text().splitlines())
        elif r['http_status'] in (404, 410): parser.parse([])
        else: parser.parse(['User-agent: *', 'Disallow: /'])
        delay = max(1, parser.crawl_delay(UA) or 0)
        rate = parser.request_rate(UA)
        if rate: delay = max(delay, rate.seconds / rate.requests)
        return parser.can_fetch(UA, target), delay

    def fetch(self, target, robots=False):
        target = url(target)
        robots = robots or urlsplit(target).path == '/robots.txt'
        with self.lock('url-' + key(target)):
            cached = self.cached(target)
            if cached: return cached
            current, response = target, {}
            for _ in range(6):
                allowed, delay = (True, 1) if robots else self.policy(current)
                if not allowed: return self.save(target, {}, 'ROBOTS_BLOCKED', current, 'direct')
                response = self.request(current, delay)
                if response['code'] in (301, 302, 303, 307, 308) and response['location']:
                    current = url(urljoin(current, response['location']))
                    # Only robots paths are exempt from a destination robots check.
                    if robots and urlsplit(current).path != '/robots.txt': break
                    continue
                break
            if response.get('exit') == 0 and response.get('code') == 200:
                r = self.save(target, response, 'ok', current, 'direct')
                if r['status'] == 'ok' or robots: return r
            if not robots and response.get('code') != 429:
                fallback = self.fallback(current, delay)
                if fallback['code'] == 200 and fallback['exit'] == 0:
                    return self.save(target, fallback, 'ok', current, 'jina')
            return self.save(target, response, 'FETCH_FAILED', current, 'direct')

    def rawcheck(self, target, quote):
        """Return yes/no/unfetchable; a fetch failure says nothing about the claim."""
        if not words(quote): return 'no_quote'
        r = self.fetch(target)
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
            print(group, len(batch), 'active organizations with website processed', flush=True)


if __name__ == '__main__': main()
