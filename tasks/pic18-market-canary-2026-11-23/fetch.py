#!/usr/bin/env python3
"""Market trial adapter of the 2026-11-22 robots-aware fetcher.

Bodies remain in memory. The reader can preserve inspected, privacy-safe
sentences with their source offsets. Every response gets a digest and log row.
"""
import csv, gzip, hashlib, io, json, re, subprocess, sys, time, zlib
from threading import Thread
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

D = Path(__file__).resolve().parent
STORE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/market-canary-2026-11-23')
UA, AGENT = 'Mozilla/5.0 (compatible; AtlasSiteCorpus/1.0)', 'AtlasSiteCorpus'
MAX_PAGES = 6
SKIP_TAGS = {'script', 'style', 'noscript', 'nav', 'header', 'footer', 'aside', 'svg', 'form', 'select', 'button', 'iframe', 'template', 'head'}
SKIP_CLASS = re.compile(r'(^|[\s_-])(nav|navbar|menu|footer|cookie|breadcrumbs?|skip-link|sidebar|mega|dropdown)([\s_-]|$)', re.I)
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
BLOCK = {'p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th', 'tr', 'section', 'article', 'main', 'ul', 'ol', 'table', 'br', 'blockquote', 'dd', 'dt', 'figcaption', 'span_break'}
# link text/path scoring: capabilities, processes, services, products, industries, markets (lower rank = better)
PRIORITY = [r'industr|market|applications|who we serve', r'capabilit|what we do', r'about|company|who we are', r'product|solution', r'service|manufactur']
CLASS = {6: 'NO_DNS', 7: 'CONN_REFUSED', 28: 'TIMEOUT', 35: 'TLS_ERROR', 60: 'TLS_ERROR'}  # what remains after the HTTP/1.1 retry
AVOID = re.compile(r'career|job|login|log in|cart|privacy|terms|cookie|contact|news|blog|press|event|sitemap|\.(pdf|jpe?g|png|gif|zip|docx?|xlsx?)(\?|$)|mailto:|tel:|javascript:', re.I)


class Page(HTMLParser):
    """Main-text extractor (drops nav/header/footer/aside/forms and menu-ish classes) + anchor list."""
    def __init__(self, classskip=True):
        super().__init__(convert_charrefs=True); self.classskip = classskip
        self.stack, self.lines, self.cur, self.kind, self.links, self.a = [], [], [], 'p', [], None
    def skipping(self): return any(s for _, s in self.stack)
    def flush(self):
        t = re.sub(r'\s+', ' ', ''.join(self.cur)).strip()
        if t: self.lines.append((t, self.kind))
        self.cur = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'a' and d.get('href'): self.a = [d['href'], []]
        if tag in VOID:
            if tag == 'br' and not self.skipping(): self.flush()
            return
        skip = tag in SKIP_TAGS or (self.classskip and tag not in ('html', 'body', 'main', 'article') and bool(SKIP_CLASS.search((d.get('class') or '') + ' ' + (d.get('id') or '')))) or d.get('aria-hidden') == 'true'
        self.stack.append((tag, skip))
        if tag in BLOCK and not self.skipping():
            self.flush(); self.kind = {'li': 'li', 'td': 'td', 'th': 'td'}.get(tag, 'h' if tag[0] == 'h' and tag[1:].isdigit() else 'p')
    def handle_endtag(self, tag):
        if tag == 'a' and self.a: self.links.append((self.a[0], re.sub(r'\s+', ' ', ''.join(self.a[1])).strip())); self.a = None
        if tag in VOID: return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                was_block = tag in BLOCK
                del self.stack[i:]
                if was_block and not self.skipping(): self.flush()
                break
    def handle_data(self, data):
        if self.a is not None: self.a[1].append(data)
        if not self.skipping(): self.cur.append(data)
    def result(self):
        self.flush(); return self.lines, self.links


def sha(b): return hashlib.sha256(b).hexdigest()
def reg_domain(host):
    h = host.lower().removeprefix('www.').split('.'); return '.'.join(h[-3:] if len(h) >= 3 and h[-2] in ('co', 'com', 'org', 'ac') else h[-2:])


def decode_body(body, encoding):
    if body and ('gzip' in encoding.lower() or body.startswith(b'\x1f\x8b')):
        with gzip.GzipFile(fileobj=io.BytesIO(body)) as stream:
            decoded = stream.read(20_000_001)
        if len(decoded) > 20_000_000:
            raise ValueError('decoded body exceeds 20 MB')
        return decoded
    return body


class Fetcher:
    charge_robots = False

    def __init__(self, store=STORE, start=0):
        store.mkdir(parents=True, exist_ok=True); (store / 'captures').mkdir(exist_ok=True)
        self.pages = {}
        self.last, self.robots, self.n = {}, {}, start
        self.log = (store / 'fetches.jsonl').open('a' if start else 'x')
    def curl(self, target, kind='robots'):
        charge = kind != 'robots' or self.charge_robots
        if charge and not self.remaining:
            return None
        r = self.curl1(target, kind)
        if r['exit'] in {5, 6, 7, 16, 18, 28, 35, 52, 55, 56, 60, 92, 95, 96, 97} and (not charge or self.remaining):
            return self.curl1(target, kind, True)
        return r

    def curl1(self, target, kind, h1=False):
        host = urlsplit(target).hostname
        time.sleep(max(0, self.last.get(host, 0) + 1.2 - time.time()))
        if kind != 'robots' or self.charge_robots:
            self.remaining -= 1
        p = subprocess.run(
            ['curl', '-q', '-sS', '--noproxy', '*', '--proto', '=http,https',
             *(['--http1.1'] if h1 else []), '-A', UA, '--max-time', '25',
             '--max-filesize', '8000000', '-D', '/dev/stderr',
             '-w', '%{stderr}\nATLAS_HTTP:%{http_code}', target],
            capture_output=True)
        self.last[host] = time.time()
        self.n += 1
        headers, _, code = p.stderr.decode(errors='replace').rpartition('ATLAS_HTTP:')
        loc = re.findall(r'(?im)^location:[ \t]*(.*?)\r?$', headers)
        ct = re.findall(r'(?im)^content-type:[ \t]*(.*?)\r?$', headers)
        enc = re.findall(r'(?im)^content-encoding:[ \t]*(.*?)\r?$', headers)
        memento = re.findall(r'(?im)^memento-datetime:[ \t]*(.*?)\r?$', headers)
        try:
            body, decode_error = decode_body(p.stdout, enc[-1] if enc else ''), False
        except (OSError, EOFError, ValueError, zlib.error):
            body, decode_error = b'', True
        r = dict(code=int(code.strip() or 0), raw=body, location=loc[-1] if loc else '',
                 decode_error=decode_error, memento=memento[-1] if memento else '',
                 ctype=ct[-1] if ct else '', exit=p.returncode, request=self.n)
        self.record(dict(kind='request', request_kind=kind, request=self.n,
                         url=public_url(target), http=r['code'], exit=r['exit'],
                         protocol='http/1.1 retry' if h1 else 'default',
                         sha256='' if decode_error else sha(body), bytes=len(body), decode_error=decode_error))
        return r

    def allowed(self, target):
        p = urlsplit(target); base = f'{p.scheme}://{p.netloc}'
        if base not in self.robots:
            ru = base + '/robots.txt'
            for _ in range(5):  # RFC 9309: follow up to five redirects when fetching robots.txt
                r = self.curl(ru)
                if r is None:
                    self.record(dict(kind='robots', url=public_url(ru), note='request budget exhausted'))
                    return None
                if r['code'] in (301, 302, 303, 307, 308) and r['location']: ru = urljoin(ru, r['location']); continue
                break
            rp = RobotFileParser()
            if r['code'] in (404, 410) and not r['exit'] and not r['decode_error']: rp.parse([])
            elif r['code'] == 200 and r['exit'] == 0 and not r['decode_error']: rp.parse(r['raw'].decode('utf-8', 'replace').splitlines())
            else: rp.parse(['User-agent: *', 'Disallow: /'])  # robots unreadable: treated as closed (not fetched), recorded as ROBOTS_UNREADABLE
            self.robots[base] = (rp, r['code'] if not r['decode_error'] else 0, r['exit'])
            self.record(dict(kind='robots', url=public_url(ru), http=r['code'], sha256=sha(r['raw']), note='robots.txt read' if r['code'] == 200 else f'robots http {r["code"]} exit {r["exit"]}'))
        rp, code, _ = self.robots[base]
        return rp.can_fetch(AGENT, target) if code in (200, 404, 410) and not self.robots[base][2] else None
    def record(self, row):
        row['fetched_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds'); row.setdefault('org_id', getattr(self, 'org', ''))
        self.log.write(json.dumps(row) + '\n'); self.log.flush()
    def get(self, target, kind):
        """Get a page, charging each redirect and retry to the same budget."""
        cur = target
        for _ in range(5):
            if not self.remaining:
                status = 'BUDGET'
                break
            if (urlsplit(cur).scheme not in ('http', 'https')
                    or reg_domain(urlsplit(cur).hostname or '') != self.domain):
                status = 'OFF_DOMAIN'
                break
            ok = self.allowed(cur)
            if not ok:
                rx = self.robots[urlsplit(cur).scheme + '://' + urlsplit(cur).netloc][2]
                status = ('ROBOTS_BLOCKED' if ok is False else CLASS.get(rx, f'CURL_{rx}')
                          if rx else 'ROBOTS_UNREADABLE')
                break
            r = self.curl(cur, kind)
            if not r['exit'] and r['code'] in (301, 302, 303, 307, 308) and r['location']:
                cur = urljoin(cur, r['location'])
                continue
            status = ('DECODE_ERROR' if r['decode_error'] else 'ok' if r['exit'] == 0 and r['code'] == 200 else f'HTTP_{r["code"]}'
                      if r['exit'] == 0 else CLASS.get(r['exit'], f'CURL_{r["exit"]}'))
            return self.capture(target, cur, kind, status, r)
        else:
            status = 'REDIRECT_LIMIT'
        self.record(dict(kind=kind, url=public_url(target), final_url=public_url(cur), status=status))
        return status, cur, [], []

    def capture(self, target, cur, kind, status, r):
        row = dict(kind=kind, url=public_url(target), final_url=public_url(cur),
                   status=status, request=r['request'], sha256='' if r['decode_error'] else sha(r['raw']))
        lines, links = [], []
        self.last_body = r['raw']
        if status == 'ok' and ('html' in r['ctype'].lower() or b'<html' in r['raw'][:2000].lower()
                               or b'<!doctype' in r['raw'][:200].lower()):
            body = r['raw'].decode('utf-8', 'replace')
            pg = Page(); pg.feed(body); lines, links = pg.result()
            if sum(len(t) for t, _ in lines) < 200:
                pg = Page(classskip=False); pg.feed(body); lines, links = pg.result()
                row['class_fallback'] = True
            text = ''.join(t + '\n' for t, _ in lines)
            row['text_sha256'] = sha(text.encode())
            row['chars'] = len(text)
            if len(text) < 200:
                row['status'] = status = 'THIN_OR_EMPTY'
            row['org_id'] = self.org
            self.pages[r['request']] = (row, lines)
        elif status == 'ok':
            row['status'] = status = 'NOT_HTML'
        self.record(row)
        return status, cur, lines, links


def public_url(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.hostname or '', p.path, '', ''))


def pick_links(base, links, seen):
    dom, out = reg_domain(urlsplit(base).hostname), []
    for href, txt in links:
        u = urljoin(base, href.strip()); p = urlsplit(u)
        if p.scheme not in ('http', 'https') or reg_domain(p.hostname or '') != dom or AVOID.search(txt + ' ' + u): continue
        u = urlunsplit((p.scheme, p.netloc, p.path or '/', p.query if len(p.query) < 40 else '', ''))
        key = u.rstrip('/').lower().removeprefix('https://').removeprefix('http://').removeprefix('www.')
        if key in seen or p.path in ('', '/'): continue
        hay = (txt + ' ' + p.path).lower()
        rank = next((i for i, pat in enumerate(PRIORITY) if re.search(pat, hay)), None)
        if rank is not None: out.append((rank, len(p.path), u, key, txt))
    out.sort(); res, ks = [], set()
    for rank, _, u, key, txt in out:
        if key not in ks: ks.add(key); res.append((u, txt))
    return res


def fetch_frame(fetcher):
    with (D / 'frame.csv').open() as f:
        frame = list(csv.DictReader(f))
    for row in frame:
        site = row['website']
        fetcher.org = row['org_id']
        fetcher.domain = reg_domain(urlsplit(site).hostname)
        fetcher.remaining = MAX_PAGES
        st, final, _, links = fetcher.get(site, 'home')
        seen = {urlsplit(final).netloc.lower().removeprefix('www.') + urlsplit(final).path.rstrip('/')}
        if st == 'THIN_OR_EMPTY' and fetcher.remaining:
            m = re.search(rb'(?i)http-equiv="refresh"[^>]*content="\d+;\s*URL=([^"]+)"', fetcher.last_body)
            if m:
                st, final, _, links = fetcher.get(urljoin(final, m.group(1).decode()), 'meta')
        if st == 'ok':
            for u, _ in pick_links(final, links, seen):
                if not fetcher.remaining:
                    break
                fetcher.get(u, 'link')
        print(fetched_summary(fetcher, row['org_id'], st), flush=True)
    print(f'FETCH COMPLETE, {fetcher.n} HTTP attempts', flush=True)


def fetched_summary(fetcher, oid, status):
    return f'{oid} home={status} page attempts={MAX_PAGES - fetcher.remaining} total attempts={fetcher.n}'


if __name__ == '__main__':
    from screen import show, preserve
    f = Fetcher()
    worker = Thread(target=fetch_frame, args=(f,))
    worker.start()
    for command in sys.stdin:
        args = command.strip().split(maxsplit=2)
        if not args:
            continue
        if args[0] == 'show':
            show(f.pages.copy(), args[1:])
        if args[0] == 'preserve':
            preserve(f.pages.copy(), D / 'selection.tsv')
        if args[0] == 'quit':
            break
    worker.join()
