#!/usr/bin/env python3
"""Archive at capture (SCHEMA §4.22, V-66): Save Page Now for each evidence row's cited page, verified in the CDX index, then one
data/archive_links.csv row per evidence id. Usage: archive.py [--apply]"""
import csv, json, sys, time, urllib.request, urllib.parse
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; D = Path(__file__).parent; LABEL = 'site-name-repair-2026-11-26'
UA = {'User-Agent': 'Mozilla/5.0 (compatible; AtlasArchive/1.0)'}


def get(url, t=150):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=t) as r: return r.geturl(), r.read(300000)


def main():
    ev = [r for r in csv.DictReader(open(ROOT / 'data/evidence_sites_OH.csv', newline='', encoding='utf-8')) if r['created_by'] == LABEL]
    have = {r['evidence_id'] for r in csv.DictReader(open(ROOT / 'data/archive_links.csv', newline='', encoding='utf-8'))}
    out = []
    for e in ev:
        if e['evidence_id'] in have: continue
        url, ref = e['source_ref'], None
        for attempt in range(3):
            try:
                final, _ = get('https://web.archive.org/save/' + url)
                m = __import__('re').search(r'/web/(\d{14})/', final)
                if m:
                    q = urllib.parse.quote(url, safe='')
                    cdx = json.loads(get(f'https://web.archive.org/cdx/search/cdx?url={q}&output=json&from={m[1][:8]}&limit=20')[1] or b'[]')
                    if any(row[1] == m[1] for row in cdx[1:]): ref = f'https://web.archive.org/web/{m[1]}/{url}'; break
                    print(e['evidence_id'], 'snapshot', m[1], 'not yet in CDX; retry'); time.sleep(20)
            except Exception as x: print(e['evidence_id'], 'attempt', attempt, str(x)[:100]); time.sleep(15)
        print(e['evidence_id'], ref or 'NO SNAPSHOT', flush=True)
        if ref: out.append([e['evidence_id'], ref, ref.split('/web/')[1][:8][:4] + '-' + ref.split('/web/')[1][4:6] + '-' + ref.split('/web/')[1][6:8], f'claude-code {LABEL}'])
        time.sleep(6)
    if '--apply' in sys.argv and out:
        with open(ROOT / 'data/archive_links.csv', 'a', newline='', encoding='utf-8') as f: csv.writer(f, lineterminator='\n').writerows(out)
    print(len(out), 'archive rows', 'appended' if '--apply' in sys.argv else '(dry run)')


if __name__ == '__main__': main()
