"""Resumable live-fetch of own-site pages LINKED from a stored corpus page (rule 14). Cap 6 per organization; cache is cached by URL."""
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
from site_corpus import Corpus, key

STORE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-market-scale-2026-11-18')
# (org, url, stored page that links to it)
TARGETS = [
    ('ORG-001958', 'http://www.icslabs.com/industriesserved/sporting-goods/', 'ORG-001958 stored home page href (Sporting Goods)'),
    ('ORG-001958', 'http://www.icslabs.com/industriesserved/construction-industrial-manufacturing/', 'ORG-001958 stored home page href (Construction, Manufacturing and General Industry)'),
    ('ORG-001958', 'http://www.icslabs.com/industriesserved/defense-tactical/', 'ORG-001958 stored home page href (Defense & Tactical)'),
    ('ORG-001958', 'http://www.icslabs.com/industriesserved/emergency-response/', 'ORG-001958 stored home page href (Emergency Response)'),
    ('ORG-001958', 'http://www.icslabs.com/industriesserved/recreation-leisure/', 'ORG-001958 stored home page href (Recreation & Leisure)'),
    ('ORG-001657', 'https://comdess.com/index.php/content/application-areas', 'ORG-001657 stored locations page href (Application Areas)'),
]


GENERIC = {'info', 'sales', 'contact', 'support', 'office', 'hello', 'customerservice', 'marketing', 'privacy', 'webmaster', 'enquiries', 'inquiries', 'service', 'hr', 'careers', 'orders'}


def forget(cache, url):
    """Drop a URL's cache record (per-URL JSON and index row) so a later lookup refetches instead of reading deleted blobs."""
    (cache.cache / (key(url) + '.json')).unlink(missing_ok=True)
    index = cache.cache / 'index.csv'
    if index.exists():
        rows = list(csv.DictReader(index.open()))
        keep = [r for r in rows if r['url'] != url]
        if len(keep) != len(rows):
            with index.open('w', newline='') as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(keep)


def scrub(cache, r, url):
    """Rule 9: a page that prints a personal address is not retained: blobs, per-URL JSON and index row are deleted; the fetch row stays as status only."""
    text = (cache.cache / r['text_file']).read_text(errors='replace') + (cache.cache / r['raw_file']).read_text(errors='replace')
    if not any(e.split('@')[0].lower() not in GENERIC and not e.lower().endswith(('.png', '.jpg', '.svg', '.webp', '.wixpress.com'))
               for e in re.findall(r'[\w.+-]{1,80}@[\w.-]{1,160}\.[a-zA-Z]{2,20}', text)):
        return False
    for k in ('text_file', 'raw_file'):
        (cache.cache / r[k]).unlink(missing_ok=True)
        r[k] = ''
    forget(cache, url)
    return True


def repair(cache):
    """A record whose blobs are gone (an earlier scrub) is forgotten, so the fetch below refetches it."""
    for _, url, _ in TARGETS:
        meta = cache.cache / (key(url) + '.json')
        if meta.exists():
            rec = json.loads(meta.read_text())
            if not (cache.cache / rec['raw_file']).exists() or not (cache.cache / rec['text_file']).exists():
                forget(cache, url)


def main():
    assert max(sum(o == t[0] for t in TARGETS) for o, *_ in TARGETS) <= 6
    c = Corpus(STORE)
    repair(c)
    rows = []
    for org, url, linked_from in TARGETS:
        r = c.fetch(url)
        purged = scrub(c, r, r['url'])
        rows.append(dict(org_id=org, url=url, linked_from=linked_from, status=r['status'], http_status=r['http_status'], final_url=r['final_url'],
                         route=r['route'], sha256=r['sha256'], text_file=r['text_file'], raw_file=r['raw_file'], text_sha256=r['text_sha256'], fetched_at=r['fetched_at'],
                         retained='purged_personal_contact' if purged else 'yes'))
        print(org, url, r['status'], flush=True)
    with (HERE / 'fetches.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


if __name__ == '__main__':
    main()
