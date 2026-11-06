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
CACHE = ROOT / 'build/l1-cache'
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
    if m: return m.group(1).strip()
    m = re.search(r'["“](.+)["”]', e['claim_detail'], re.S)
    return m.group(1).strip() if m else ''


def frame():
    sites = [r for p in sorted((ROOT / 'data').glob('sites_*.csv')) for r in read(p)]
    si = {r['site_id'] for r in sites if r['state'] == 'OH' and re.sub(r' County$', '', r['county']) in PIC18}
    oi = {r['org_id'] for r in sites if r['site_id'] in si}
    rows = [r for p in sorted((ROOT / 'data').glob('evidence_*.csv')) for r in read(p) if r['source_class'] == 'own_site' and ((r['record_table'] == 'organizations' and r['record_id'] in oi) or (r['record_table'] == 'sites' and r['record_id'] in si))]
    assert len({r['evidence_id'] for r in rows}) == len(rows)
    for r in rows: r.update(url=r['source_ref'], quote=quote(r))
    write(HERE / 'inputs.csv', rows, list(rows[0]))
    return rows


def audit():
    rows = frame()
    urls = sorted({r['url'] for r in rows})
    print('frame', len(rows), 'URLs', len(urls), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for i, result in enumerate(pool.map(fetch, urls), 1):
            if i % 50 == 0: print('fetched', i, '/', len(urls), flush=True)
    results = []
    for e in rows:
        f = fetch(e['url'])
        if f['status'] != 'ok': judgment, reason = 'FETCH_FAILED', 'No readable live page via direct or Jina route; availability only.'
        elif not e['quote']: judgment, reason = 'PARTIAL', 'No preserved verbatim quote: manual claim judgment needed; not an adverse claim verdict.'
        elif on_page(e['quote'], ROOT / f['page']): judgment, reason = 'SUPPORTED', 'Preserved quote occurs as contiguous normalized words; claim semantics not independently rejudged.'
        else: judgment, reason = 'NOT_SUPPORTED', 'Preserved quote not found as contiguous normalized words; claim itself may still be true.'
        results.append(dict(**e, judgment=judgment, reason=reason, page=f['page'], checked_at=f['fetched_at']))
    write(HERE / 'verdicts.csv', results, list(results[0]))
    leads = [dict(evidence_id=r['evidence_id'], record=r['record_id'], claim_type=r['claim_type'], url=r['url'], judgment=r['judgment'], settling_page='A readable own-site page stating: ' + r['claim_detail'], reason=r['reason']) for r in results if r['judgment'] != 'SUPPORTED']
    write(HERE / 'repair_leads.csv', leads, ['evidence_id','record','claim_type','url','judgment','settling_page','reason'])
    assert len(leads) + sum(r['judgment'] == 'SUPPORTED' for r in results) == len(rows)
    print(Counter(r['judgment'] for r in results), flush=True)


if __name__ == '__main__':
    audit()
