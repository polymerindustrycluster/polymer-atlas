"""Resumable live-fetch of own-site pages LINKED from a stored corpus page (rule 14). Cap 6 per organization; cache is cached by URL."""
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
from site_corpus import Corpus

STORE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-market-canary-2026-11-18')
# (org, url, stored page that links to it)
TARGETS = [
    ('ORG-001380', 'https://bauerladder.com/why-bauer/', 'ORG-001380/1b41446b (home) href'),
    ('ORG-001380', 'https://bauerladder.com/oem-ladders/', 'ORG-001380/1b41446b (home) href'),
    ('ORG-001380', 'https://bauerladder.com/catv-utility-combo-ladders/', 'ORG-001380/1b41446b (home) href'),
    ('ORG-000508', 'https://www.polymer5.com/page4', 'ORG-000508/pass2-efb50b0d (home) href'),
    ('ORG-000508', 'https://www.polymer5.com/facilities', 'ORG-000508/pass2-efb50b0d (home) href'),
    ('ORG-000087', 'https://rainbowrubber.com/our-story', 'ORG-000087/6662aab3 (home) href'),
    ('ORG-000087', 'https://rainbowrubber.com/rubber-extrusion-services', 'ORG-000087/6662aab3 (home) href'),
    ('ORG-000087', 'https://rainbowrubber.com/resources', 'ORG-000087/6662aab3 (home) href'),
    ('ORG-000469', 'https://northeasternplastics.com/AboutUs/?referrerPage=Home&refPgId=530993786&PCUrl=1', 'ORG-000469/5b5f1d57 (home) href'),
    ('ORG-000087', 'https://rainbowrubber.com/rubber-extrusion-services/peristaltic-pump-applications', 'ORG-000087/6662aab3 (home) href'),
    ('ORG-000043', 'https://www.alterra360.com/our-partners', 'ORG-000043/a32342d1 (home) href'),
    ('ORG-000043', 'https://www.alterra360.com/our-purpose', 'ORG-000043/a32342d1 (home) href'),
    ('ORG-000043', 'https://www.alterra360.com/faqs', 'ORG-000043/a32342d1 (home) href'),
]


GENERIC = {'info', 'sales', 'contact', 'support', 'office', 'hello', 'customerservice', 'marketing', 'privacy', 'webmaster', 'enquiries', 'inquiries', 'service', 'hr', 'careers', 'orders'}


def scrub(cache, r):
    """Rule 9: a page that prints a personal address is not retained (blobs, per-URL meta and index row deleted); the fetch row stays as status only."""
    text = (cache.cache / r['text_file']).read_text(errors='replace') + (cache.cache / r['raw_file']).read_text(errors='replace')
    if not any(e.split('@')[0].lower() not in GENERIC and not e.lower().endswith(('.png', '.jpg', '.svg', '.webp', '.wixpress.com'))
               for e in re.findall(r'[\w.+-]{1,80}@[\w.-]{1,160}\.[a-zA-Z]{2,20}', text)):
        return False
    for k in ('text_file', 'raw_file'):
        (cache.cache / r[k]).unlink(missing_ok=True)
        r[k] = ''
    return True


def main():
    assert max(sum(o == t[0] for t in TARGETS) for o, *_ in TARGETS) <= 6
    c = Corpus(STORE)
    rows = []
    for org, url, linked_from in TARGETS:
        r = c.fetch(url)
        purged = scrub(c, r)
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
