#!/usr/bin/env python3
"""One polite pass: record website + <=5 same-domain pages reached by links on fetched pages. Direct curl only (no proxy), robots.txt gated
per hop, 1 s between requests to a host, one retry only after a curl transport failure. Never builds a URL: every fetched URL is the record's
website or an href found on a page fetched here. Captures (raw + extracted main text + line kinds) go to STORE, outside the repo.
Usage: python3 fetch.py [org_id ...]   (default: all 25 in frame.csv)"""
import csv, hashlib, json, re, subprocess, sys, tempfile, time, os
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

D = Path(__file__).resolve().parent
STORE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/web-canary-2026-11-22')
UA, AGENT = 'Mozilla/5.0 (compatible; AtlasSiteCorpus/1.0)', 'AtlasSiteCorpus'
MAX_EXTRA = 5
SKIP_TAGS = {'script', 'style', 'noscript', 'nav', 'header', 'footer', 'aside', 'svg', 'form', 'select', 'button', 'iframe', 'template', 'head'}
SKIP_CLASS = re.compile(r'(^|[\s_-])(nav|navbar|menu|footer|cookie|breadcrumbs?|skip-link|sidebar|mega|dropdown)([\s_-]|$)', re.I)
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
BLOCK = {'p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th', 'tr', 'section', 'article', 'main', 'ul', 'ol', 'table', 'br', 'blockquote', 'dd', 'dt', 'figcaption', 'span_break'}
# link text/path scoring: capabilities, processes, services, products, industries, markets (lower rank = better)
PRIORITY = [r'capabilit', r'process', r'what we do|manufactur', r'service', r'industr|market|applications', r'product|solution', r'about|company|who we are']
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


class Fetcher:
    def __init__(self):
        STORE.mkdir(parents=True, exist_ok=True); (STORE / 'raw').mkdir(exist_ok=True); (STORE / 'text').mkdir(exist_ok=True)
        self.last, self.robots, self.n, self.log = {}, {}, 0, open(STORE / 'fetches.jsonl', 'a')
    def curl(self, target):
        r = self.curl1(target)
        return self.curl1(target, True) if r['exit'] != 0 else r  # the one retry, transport failure only, over HTTP/1.1 (curl 52/56/92 are HTTP/2 stream errors), same declared user-agent
    def curl1(self, target, h1=False):
        host = urlsplit(target).hostname
        time.sleep(max(0, self.last.get(host, 0) + 1.2 - time.time()))
        with tempfile.TemporaryDirectory() as tmp:
            raw, hd = Path(tmp, 'raw'), Path(tmp, 'h')
            p = subprocess.run(['curl', '-sS', *(['--http1.1'] if h1 else []), '-A', UA, '--max-time', '25', '--max-filesize', '8000000', '-D', str(hd), '-o', str(raw), '-w', '%{http_code}', target], capture_output=True, text=True)
            self.last[host] = time.time(); self.n += 1
            h = hd.read_text(errors='replace') if hd.exists() else ''
            loc = re.findall(r'(?im)^location:\s*(.*?)\s*$', h); ct = re.findall(r'(?im)^content-type:\s*(.*?)\s*$', h)
            return dict(code=int(p.stdout or 0), raw=raw.read_bytes() if raw.exists() else b'', location=loc[-1] if loc else '', ctype=ct[-1] if ct else '', exit=p.returncode, err=p.stderr[:200])
    def allowed(self, target):
        p = urlsplit(target); base = f'{p.scheme}://{p.netloc}'
        if base not in self.robots:
            ru = base + '/robots.txt'
            for _ in range(5):  # RFC 9309: follow up to five redirects when fetching robots.txt
                r = self.curl(ru)
                if r['code'] in (301, 302, 303, 307, 308) and r['location']: ru = urljoin(ru, r['location']); continue
                break
            rp = RobotFileParser()
            if r['code'] in (404, 410): rp.parse([])
            elif r['code'] == 200 and r['exit'] == 0: rp.parse(r['raw'].decode('utf-8', 'replace').splitlines())
            else: rp.parse(['User-agent: *', 'Disallow: /'])  # robots unreadable: treated as closed (not fetched), recorded as ROBOTS_UNREADABLE
            self.robots[base] = (rp, r['code'], r['exit'])
            self.record(dict(kind='robots', url=ru, http=r['code'], sha256=sha(r['raw']), note='robots.txt read' if r['code'] == 200 else f'robots http {r["code"]} exit {r["exit"]}'))
        rp, code, _ = self.robots[base]
        return rp.can_fetch(AGENT, target) if code in (200, 404, 410) else None
    def record(self, row):
        row['fetched_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds'); row.setdefault('org_id', getattr(self, 'org', ''))
        self.log.write(json.dumps(row) + '\n'); self.log.flush()
    def get(self, target, kind):
        """Fetch one page; returns (status, final_url, lines, links)."""
        cur = target
        for _ in range(5):
            ok = self.allowed(cur)
            if not ok:
                rx = self.robots[urlsplit(cur).scheme + '://' + urlsplit(cur).netloc][2]
                st = 'ROBOTS_BLOCKED' if ok is False else CLASS.get(rx, f'CURL_{rx}') if rx else 'ROBOTS_UNREADABLE'  # transport reason beats a generic label
                self.record(dict(kind=kind, url=target, final_url=cur, http=0, status=st, sha256='', note='robots.txt disallows' if ok is False else 'robots.txt could not be read (availability fact); page not fetched')); return st, cur, [], []
            r = self.curl(cur)
            if r['code'] in (301, 302, 303, 307, 308) and r['location']: cur = urljoin(cur, r['location']); continue
            break
        status = 'ok' if r['exit'] == 0 and r['code'] == 200 else f'HTTP_{r["code"]}' if r['exit'] == 0 else CLASS.get(r['exit'], f'CURL_{r["exit"]}')
        row = dict(kind=kind, url=target, final_url=cur, http=r['code'], status=status, sha256=sha(r['raw']), bytes=len(r['raw']), ctype=r['ctype'], note=r['err'])
        lines, links = [], []
        if status == 'ok' and ('html' in r['ctype'].lower() or b'<html' in r['raw'][:2000].lower() or b'<!doctype' in r['raw'][:200].lower()):
            body = r['raw'].decode('utf-8', 'replace'); pg = Page(); pg.feed(body); lines, links = pg.result()
            if sum(len(t) for t, _ in lines) < 200:  # class heuristic may have swallowed a content wrapper: tag-only pass
                pg = Page(classskip=False); pg.feed(body); lines, links = pg.result(); row['note'] = 'class-skip off (content wrapper matched a menu class)'
            (STORE / 'raw' / (row['sha256'] + '.raw')).write_bytes(r['raw'])
            text, meta, pos = '', [], 0
            for t, k in lines: meta.append([pos, pos + len(t), k]); text += t + '\n'; pos += len(t) + 1
            tb = text.encode(); row['text_sha256'] = sha(tb); row['chars'] = len(text)
            (STORE / 'text' / (row['text_sha256'] + '.txt')).write_bytes(tb); (STORE / 'text' / (row['text_sha256'] + '.lines.json')).write_text(json.dumps(meta))
            if len(text) < 200: row['status'] = status = 'THIN_OR_EMPTY'; row['note'] = 'under 200 characters of main text (JS-rendered, wall or empty)'
        elif status == 'ok':
            row['status'] = status = 'NOT_HTML'; row['note'] = 'not stored as text; ' + r['ctype']
            (STORE / 'raw' / (row['sha256'] + '.raw')).write_bytes(r['raw'])
        self.last_sha = row['sha256']; self.record(row); return status, cur, lines, links


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


def main(ids):
    F = Fetcher(); frame = {r['org_id']: r for r in csv.DictReader(open(D / 'frame.csv'))}
    for oid in ids or frame:
        F.org = oid; site = frame[oid]['website']; seen = set()
        st, final, lines, links = F.get(site, 'home'); seen.add(urlsplit(final).netloc.lower().removeprefix('www.') + urlsplit(final).path.rstrip('/'))
        if st == 'THIN_OR_EMPTY':  # a meta-refresh target on the record's own page is a link found on a fetched page
            m = re.search(rb'(?i)http-equiv="refresh"[^>]*content="\d+;\s*URL=([^"]+)"', (STORE / 'raw' / (F.last_sha + '.raw')).read_bytes())
            if m:
                site2 = urljoin(final, m.group(1).decode()); st, final, lines, links = F.get(site2, 'link:meta-refresh'); seen.add(urlsplit(final).netloc.lower().removeprefix('www.') + urlsplit(final).path.rstrip('/'))
        if st not in ('ok',): print(oid, 'home', st); continue
        got = 0
        for u, txt in pick_links(final, links, seen):
            if got >= MAX_EXTRA: break
            st2, f2, l2, _ = F.get(u, f'link:{txt[:40]}'); got += 1
        print(oid, 'home ok;', got, 'extra; total requests so far', F.n)


if __name__ == '__main__': main(sys.argv[1:])
