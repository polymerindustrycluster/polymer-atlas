#!/usr/bin/env python3
"""PIC18 quote-presence audit; raw cache lives outside the shipped tree in build/."""
import ast
import concurrent.futures
import csv
import hashlib
import html.parser
import json
import os
import threading
import re
import subprocess
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from regions import PIC18

# Load the calibrated functions unchanged, without running analyze.py's CLI.
source = ast.parse((ROOT / 'tasks/evidence-audit-2026-11-03/analyze.py').read_text())
ns = dict(re=re, unicodedata=unicodedata, Path=Path, math=__import__('math'))
for node in source.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'words' for t in node.targets) or isinstance(node, ast.FunctionDef) and node.name in ('on_page', 'wilson'):
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<calibrated-audit>', 'exec'), ns)
on_page, wilson = ns['on_page'], ns['wilson']
CACHE = ROOT / 'build/l11-repair3-cache'
CACHE.mkdir(parents=True, exist_ok=True)


def read(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write(p, rows, fields):
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fields, extrasaction='ignore', lineterminator='\n')
        w.writeheader(); w.writerows(rows)


class Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'): self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)


def fetch(url, refresh=False, fallback=True):
    key = hashlib.sha256(url.encode()).hexdigest()
    meta, page = [CACHE / (key + ext) for ext in ('.json', '.txt')]
    raw = CACHE / (key + f'.{os.getpid()}.{threading.get_ident()}.raw')
    if meta.exists() and not refresh:
        result = json.loads(meta.read_text())
        assert result['url'] == url
        return result
    attempts = []
    for route in [url] + (['https://r.jina.ai/' + url] if fallback else []):
        p = subprocess.run(['curl', '-L', '-sS', '-A', 'Mozilla/5.0 (Atlas evidence re-verification)', '--max-time', '25', '--max-filesize', '12000000', '-D', str(raw.with_suffix('.headers')), '-o', str(raw), '-w', '%{http_code}\n%{url_effective}', route], capture_output=True, text=True)
        code, _, effective = p.stdout.partition('\n')
        headers = raw.with_suffix('.headers').read_text(errors='replace') if raw.with_suffix('.headers').exists() else ''
        retry = re.findall(r'(?im)^retry-after:\s*(\d+)', headers)
        attempts.append(dict(route=route, status=code, exit=p.returncode, effective_url=effective, error=p.stderr.strip()[:300], retry_after=int(retry[-1]) if retry else 0))
        body = raw.read_bytes().decode('utf-8', errors='replace') if raw.exists() else ''
        if p.returncode == 0 and code == '200' and len(body) > 200 and not body.startswith('%PDF'):
            if route == url:
                parser = Text(); parser.feed(body); text = ' '.join(parser.parts)
            else:
                # Jina metadata is not page evidence.
                text = body.split('Markdown Content:', 1)[-1] if 'Markdown Content:' in body else ''
            lower = text.lower()
            wall = any(x in lower for x in ('just a moment...', 'verify you are human', 'attention required! | cloudflare', 'this site can’t be reached', 'checking your browser'))
            if len(ns['words'](text)) >= 15 and not wall:
                tmp_page = page.with_suffix(f'.{os.getpid()}.{threading.get_ident()}.txt.tmp')
                tmp_page.write_text(text); tmp_page.replace(page)
                result = dict(url=url, status='ok', page=str(page.relative_to(ROOT)), sha256=hashlib.sha256(raw.read_bytes()).hexdigest(), attempts=attempts, fetched_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
                tmp_meta = meta.with_suffix(f'.{os.getpid()}.{threading.get_ident()}.json.tmp')
                tmp_meta.write_text(json.dumps(result)); tmp_meta.replace(meta); return result
        if code == '429': break
    result = dict(url=url, status='FETCH_FAILED', page='', attempts=attempts, fetched_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    tmp_meta = meta.with_suffix(f'.{os.getpid()}.{threading.get_ident()}.json.tmp')
    tmp_meta.write_text(json.dumps(result)); tmp_meta.replace(meta); return result


def quote(e):
    m = re.search(r'Quote:\s*["“](.*?)["”](?:\s*\||\s*$)', e['notes'], re.S)
    if m: q = m.group(1).strip()
    else:
        spans = re.findall(r'["“]([^"“”]+)["”]', e['claim_detail'], re.S)
        q = spans[0].strip() if len(spans) == 1 else ''
    return q if ns['words'](q) else ''


def live_posture(f, url):
    if f['status'] != 'ok': return 'FETCH_FAILED'
    text = (ROOT / f['page']).read_text()
    lower = text.lower()
    if '\ufffd' in text or any(x in lower for x in ("this site can't be reached", 'enable javascript and cookies to continue', 'checking if the site connection is secure', 'access to this page has been denied', 'please complete the security check', 'request blocked')):
        return 'FETCH_FAILED'
    attempt = f['attempts'][-1]
    effective = attempt['effective_url']
    if attempt['route'] != url:
        # Jina's URL Source header, not its wrapper URL, identifies the returned page.
        key = hashlib.sha256(url.encode()).hexdigest()
        effective = ''
        for raw in CACHE.glob(key + '*.raw'):
            if hashlib.sha256(raw.read_bytes()).hexdigest() == f.get('sha256'):
                m = re.search(r'(?m)^URL Source:\s*(https?://\S+)', raw.read_text(errors='replace'))
                effective = m[1] if m else ''
                break
    if not effective: return 'FETCH_FAILED'
    from urllib.parse import urlsplit
    a,b = urlsplit(url),urlsplit(effective)
    norm = lambda x: (x.hostname.lower().removeprefix('www.') if x.hostname else '', x.path.rstrip('/'), x.query)
    return 'ok' if norm(a) == norm(b) else 'WRONG_PAGE'
