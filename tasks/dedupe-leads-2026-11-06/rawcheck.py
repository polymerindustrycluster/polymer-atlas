#!/usr/bin/env python3
"""Independently re-fetch packet witnesses once; report failures rather than silently skip."""
import concurrent.futures
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = Path('/tmp/dedupe-leads-integrator')
CACHE.mkdir(exist_ok=True)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


visible = module('house_reader', HERE / 'lanes/a/research.py').visible
words = module('house_words', HERE.parent / 'evidence-repair-2-2026-11-04/prep.py').W


def matches(text, quote):
    hay = ' ' + ' '.join(words(text)) + ' '
    for part in quote.split('||'):
        needle = ' ' + ' '.join(words(part)) + ' '
        if not words(part) or needle not in hay:
            return False
        hay = hay[hay.index(needle) + len(needle) - 1:]
    return True


def text_of(path):
    raw = path.read_bytes()
    if raw.startswith(b'%PDF'):
        return subprocess.check_output(['pdftotext', '-raw', str(path), '-']).decode('utf-8', 'replace')
    return visible(raw.decode('utf-8', 'replace'))


def fetch(url):
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest()[:16] + '.raw')
    result = subprocess.run(['curl', '-L', '--max-time', '40', '--compressed', '-A', 'Mozilla/5.0', '-sS', url], capture_output=True)
    path.write_bytes(result.stdout)
    return dict(source_url=url, raw_path=str(path), raw_sha256=hashlib.sha256(result.stdout).hexdigest(),
                curl_exit=result.returncode, error=result.stderr.decode('utf-8', 'replace')[:200])


if __name__ == '__main__':
    rows = sum((json.loads((HERE / f'lanes/{lane}/verdicts.json').read_text()) for lane in ('a', 'b')), [])
    evidence = [e for v in rows for e in v['evidence']]
    urls = sorted({e['source_url'] for e in evidence})
    out = HERE / 'rawcheck.json'
    receipts = json.loads(out.read_text()) if out.exists() else []
    saved = {r['source_url']: r for r in receipts}
    for r in json.loads((HERE / 'calibration.json').read_text()):
        if r['source_url'] not in saved:
            saved[r['source_url']] = dict(source_url=r['source_url'], raw_path=r['raw_path'], raw_sha256=r['raw_sha256'], curl_exit=0, error='')
    for r in saved.values():
        assert hashlib.sha256(Path(r['raw_path']).read_bytes()).hexdigest() == r['raw_sha256']
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        fresh = list(pool.map(fetch, [u for u in urls if u not in saved]))
    saved.update({r['source_url']: r for r in fresh})
    for url in urls:
        r = saved[url]
        try:
            text = text_of(Path(r['raw_path']))
            r['quotes'] = [dict(quote=e['quote'], matched=matches(text, e['quote'])) for e in evidence if e['source_url'] == url]
            r['status'] = 'PASS' if text.strip() and all(q['matched'] for q in r['quotes']) else 'UNCONFIRMED'
        except (subprocess.CalledProcessError, OSError) as exc:
            r.update(status='UNINSPECTABLE', extraction_error=str(exc), quotes=[])
    out.write_text(json.dumps([saved[u] for u in urls], indent=2) + '\n')
    print(f'{len(evidence)} quoted observations / {len(urls)} distinct sources; ' + ', '.join(f"{s}={sum(saved[u]['status']==s for u in urls)}" for s in ('PASS', 'UNCONFIRMED', 'UNINSPECTABLE')))
