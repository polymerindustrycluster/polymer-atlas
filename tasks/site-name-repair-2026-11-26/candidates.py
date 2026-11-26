#!/usr/bin/env python3
"""Candidate finder for the site-name repair (owner ruling 2026-11-25, "Fix site names, then close").

Reads only held data: data/sites_*.csv, data/organizations_*.csv and the retained own-site corpus (manifest.csv + page text).
No fetch, no model, no write to data/.

Frame: PIC-18 sites (scripts/regions.py: state OH, county in PIC-18) that are active, tier A-C, with a held street.
A page is the organization's own when its requested or final host is the held website's host, or the host the held website
redirects to (the corpus crawled the held website and its same-domain links). The site's street is searched on each own page
with the site's city within 150 characters. Held names for the site: the parts of `site_name` outside the locality, the
organization's `legal_name` and each `trade_names` entry, legal-form words dropped.

Candidate classes (they overlap; each says a page names the street differently from the held site_name):
  A  the run printed directly before the street differs from every held name, and no held name is in the 350-character window
  B  no held name on any retained own page of the site
  C  a held name (legal or trade name) is beside the street but never the site_name's own part
  D  the run before the street is a held name plus a following word: "Third Dimension Division" for held "Third Dimension"
  E  as A, but a held name is also in the window (an excuse that hid a different heading directly above the street)

Usage: candidates.py [--corpus DIR]... [--out DIR] [--raw FILE]
       candidates.py --selftest [--against CANDIDATES.csv]   known answers + planted cases; exit 1 on any miss
"""
import argparse
import csv
import glob
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from atlas import SUFFIX, name_key, squash, street_key  # noqa: E402
from regions import PIC18  # noqa: E402

PERSIST = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist')
CORPORA = [PERSIST / 'pic18-corpus-2026-11-16', PERSIST / 'pic18-robots-off-main-2026-11-25']
BEFORE, AFTER, CITY_WINDOW = 200, 150, 150
# Known answers (controller, 2026-11-25 audit 13 smoke: site_name CONTRADICTED, confirmed by hand). Why the first finder missed each:
# 000646 printed "<held name> Division" and 'division' was dropped as a generic word; 001778's held website redirects to another host.
KNOWN = ('SITE-000646', 'SITE-001778')
GENERIC = {'plant', 'hq', 'headquarters', 'facility', 'office', 'division', 'site', 'works', 'operations', 'manufacturing',
           'north', 'south', 'east', 'west', 'campus', 'center', 'branch', 'location', 'warehouse', 'and'}
UI = {'privacy', 'policy', 'terms', 'conditions', 'subscribe', 'closed', 'map', 'maps', 'home', 'careers', 'sitemap', 'tech', 'advice', 'support',
      'follow', 'linked', 'linkedin', 'rights', 'reserved', 'copyright', 'success', 'stories', 'government', 'requirements', 'tradeshows',
      'events', 'glossary', 'faqs', 'faq', 'shipping', 'returns', 'return', 'sign', 'up', 'touch', 'knowledge', 'talk', 'lets', 'let',
      "let's", 'gallery', 'applications', 'saturday', 'sunday', 'monday', 'friday', 'delivery', 'services', 'service', 'life', 'design',
      'capabilities', 'recent', 'projects', 'thank', 'you', 'first', 'last', 'name', 'menu', 'top', 'history', 'molding', 'specialist',
      'javascript', 'sales', 'region', 'literature', 'portal', 'partners', 'other', 'solutions', 'products', 'inspection', 'welding',
      'laser', 'micro', 'details', 'detail', 'today', 'about', 'more', 'learn', 'read', 'view', 'click', 'here', 'now', 'online', 'website', 'web', 'connectors', 'precision', 'injection', 'window', 'production', 'distribution', 'machinery'}
LABELS = {'address', 'addresses', 'location', 'locations', 'contact', 'contacts', 'us', 'phone', 'tel', 'fax', 'email', 'hours', 'headquarters',
          'corporate', 'office', 'offices', 'main', 'mailing', 'shipping', 'physical', 'visit', 'find', 'our', 'ohio', 'oh', 'usa',
          'plant', 'facility', 'manufacturing', 'located', 'at', 'the', 'in', 'business', 'call', 'directions', 'map', 'get', 'info',
          'information', 'quote', 'request', 'a', 'north', 'america', 'united', 'states'} | GENERIC
DIVISION = {'division', 'group', 'unit', 'subsidiary', 'dba'}  # words that name an organizational unit; never dropped from a printed run
CONNECT = {'and', '&', 'of', 'the'}
RANK_KIND = {'D': 0, 'A': 1, 'E': 2, '': 3}
STOP = (LABELS | UI) - DIVISION - CONNECT  # a run printed before the street ends at one of these


def read(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def host_root(value):
    host = (urlsplit(value if '//' in value else '//' + value).hostname or '').lower().removeprefix('www.')
    return '.'.join(host.split('.')[-2:])


def street_regex(street):
    """Regex for the street line: number, words and street-suffix forms, any punctuation between."""
    back = {}
    for long, short in SUFFIX.items():
        back.setdefault(short, [short]).append(long)
    parts = []
    for t in street_key(street).split():
        alts = back.get(t, [t])
        if t.isdigit() and len(t) <= 3: alts = [t + r'(?:st|nd|rd|th)?']; parts.append('(?:' + '|'.join(alts) + ')'); continue
        parts.append('(?:' + '|'.join(re.escape(a) + (r'\.?' if a in back else '') for a in alts) + ')')
    return re.compile(r'(?<![A-Za-z0-9])' + r'[^A-Za-z0-9]+'.join(parts) + r'(?![A-Za-z0-9])', re.I) if parts else None


def held_names(site, org, site_only=False):
    """Normalized (name_key) names a page could print for this site: not the city, not generic words at an edge."""
    skip = GENERIC | set(squash(site['city']).split())
    raw = re.split(r'\s[—–-]\s', site['site_name'])
    if not site_only: raw += [org['legal_name']] + [x for x in org['trade_names'].split(';') if x.strip()]
    out = set()
    for r in raw:
        toks = name_key(re.sub(r'\((?:OSHA|EPA) filing name\)', '', r)).split()
        while toks and toks[0] in skip: toks.pop(0)
        while toks and toks[-1] in skip: toks.pop()
        if toks: out.add(' '.join(toks))
    return out


def printed_name(before):
    """The capitalized run right before the street: trailing contact labels skipped, then name words until a nav or label word.
    Returns (text as printed, name_key). A division word (Division, Group, Unit) is part of the run."""
    toks = re.findall(r"[A-Za-z0-9&'’.\-]+|[^\sA-Za-z0-9]", before[-160:])
    word = lambda t: t.lower().strip('.:')  # noqa: E731
    i = len(toks)
    while i and (re.fullmatch(r'[^\sA-Za-z0-9&]+', toks[i - 1]) or (word(toks[i - 1]) in LABELS and word(toks[i - 1]) not in DIVISION)): i -= 1
    run = []
    while i and len(run) < 8:
        t = toks[i - 1]
        if t == ',': i -= 1; continue
        if word(t) in STOP or re.fullmatch(r'\d{5}', t) or not re.fullmatch(r"[A-Z][A-Za-z0-9&'’.\-]*|&|and|of|the|[A-Z0-9]{2,}", t): break
        run.insert(0, t); i -= 1
    while run and run[0].lower() in CONNECT: run.pop(0)
    key = [t for t in name_key(' '.join(run)).split() if not t.isdigit()]
    return (' '.join(run), ' '.join(key)) if key else ('', '')


def same(a, b):
    """Names equal or one inside the other, ignoring spaces (H.B. = HB)."""
    a, b = a.replace(' ', ''), b.replace(' ', '')
    return a in b or b in a


def contains(words_text, key):
    return f' {key} ' in f' {words_text} '


def on_page(quote, text):
    """Contiguous normalized words, as scripts/site_corpus.on_page."""
    q, t = squash(quote).split(), squash(text).split()
    return bool(q) and any(t[i:i + len(q)] == q for i in range(len(t) - len(q) + 1))


def judge(before, after, names, own_names, city):
    """One street hit. kind: D (a held name plus a following word), A (differs, no held name in window), E (differs, held name in window), '' otherwise."""
    window = squash(before + ' ' + after)
    held = [n for n in names if contains(window, n)]
    shown, key = printed_name(before)
    kind = ''
    if key and key != city:
        for n in sorted(names, key=len, reverse=True):
            at = key.rfind(n)
            tail = [t for t in key[at + len(n):].split() if t not in city.split()] if at >= 0 else []
            if tail: kind = 'D'; break
        if not kind and not any(same(key, n) for n in names): kind = 'A' if not held else 'E'
    return dict(held_beside=bool(held), site_part_beside=any(contains(window, n) for n in own_names), printed=shown, kind=kind)


def load_pages(corpora):
    pages = {}  # org_id -> page rows
    for c in corpora:
        for row in read(c / 'manifest.csv'):
            if row['status'] != 'ok' or not row['text_file'] or not (c / row['text_file']).exists(): continue
            pages.setdefault(row['org_id'], []).append(dict(url=row['final_url'] or row['url'], asked=row['url'], corpus=c.name,
                                                            text_file=str(c / row['text_file']), via=row['via'], sha256=row['sha256'], raw_file=row['raw_file']))
    return pages


def own_pages(org, pages):
    """Pages of the organization's own domain: the held website's host, or where the held website redirects."""
    site = host_root(org['website'])
    domains = {site} | {host_root(p['url']) for p in pages if host_root(p['asked']) == site}
    return [p for p in pages if host_root(p['url']) in domains or host_root(p['asked']) in domains]


def find(corpora=None, root=ROOT):
    sites = [r for p in sorted(glob.glob(str(root / 'data/sites_*.csv'))) for r in read(p)]
    orgs = {r['org_id']: r for p in sorted(glob.glob(str(root / 'data/organizations_*.csv'))) for r in read(p)}
    frame = [s for s in sites if s['state'] == 'OH' and s['county'].removesuffix(' County') in PIC18
             and s['operating_status'] == 'active' and s['verification_tier'] in 'ABC' and s['street_address'].strip()]
    pages = load_pages(corpora or CORPORA)
    cache, cands = {}, []
    counts = dict(frame=len(frame), frame_sites_with_own_domain_page=0, sites_street_and_city_on_own_page=0, held_name_beside_street=0)
    for s in frame:
        org = orgs.get(s['org_id'])
        if not org: continue
        own = own_pages(org, pages.get(s['org_id'], []))
        if not own: continue
        counts['frame_sites_with_own_domain_page'] += 1
        rx, names, city = street_regex(s['street_address']), held_names(s, org), squash(s['city'])
        own_names = held_names(s, org, site_only=True)
        hits, site_words = [], ''
        for p in own:
            text = cache.get(p['text_file']) or cache.setdefault(p['text_file'], Path(p['text_file']).read_text(encoding='utf-8', errors='replace'))
            site_words += ' ' + squash(text)
            for m in rx.finditer(text) if rx else ():
                if city not in squash(text[max(0, m.start() - CITY_WINDOW):m.end() + CITY_WINDOW]): continue
                before, after = text[max(0, m.start() - BEFORE):m.start()], text[m.end():m.end() + AFTER]
                hits.append(dict(judge(before, after, names, own_names, city), site_id=s['site_id'], org_id=s['org_id'], site_name=s['site_name'],
                                 street=s['street_address'], city=s['city'], url=p['url'], corpus=p['corpus'], via=p['via'], sha256=p['sha256'],
                                 before=' '.join(before.split()), match=m.group(0), after=' '.join(after.split())))
        if not hits: continue
        counts['sites_street_and_city_on_own_page'] += 1
        stood = any(h['held_beside'] for h in hits)
        counts['held_name_beside_street'] += stood
        absent = not any(contains(site_words, n) or n.replace(' ', '') in site_words.replace(' ', '') for n in names)  # spaces ignored: H.B. = HB
        kinds = {h['kind'] for h in hits}
        cls = ('A' if 'A' in kinds and not stood else '') + ('B' if absent else '') + ('C' if stood and not any(h['site_part_beside'] for h in hits) else '') \
            + ('D' if 'D' in kinds else '') + ('E' if 'E' in kinds else '')
        if cls:
            show = next((h for h in hits if h['kind'] == 'D'), None) or next((h for h in hits if h['kind'] in ('A', 'E')), None) or hits[0]
            cands.append(dict(show, cls=cls))
    tally = dict(counts, **{f'candidates_{k}': sum(k in c['cls'] for c in cands) for k in 'ABCDE'}, candidates_union=len(cands))
    return cands, tally


def selftest(against=None):
    """Known answers on the held corpus, and planted cases on the page judge. Any miss exits 1."""
    bad = []
    # planted cases: (text before the street, held names, expected kind)
    cases = [('Contact Third Dimension Division', {'third dimension'}, 'D'),
             ('Our labs. Acme Widgets Tensile Testing', {'j t adams'}, 'A'),
             ('J T Adams Company Tensile Testing', {'j t adams'}, 'D'),
             ('Stroup Belting', {'stroup and son'}, 'A'),
             ('Hours Mon-Fri 8-5. Plant Phone 330 Acme Group', {'acme'}, 'D'),
             ('B.F. Plastics, Inc.', {'bf plastics'}, ''),       # punctuation and legal form: the same entity
             ('Contact Details', {'convertapax'}, ''),            # a label, no name
             ('Privacy Policy Terms & Conditions', {'acme'}, ''),  # navigation
             ('Progressive Foam Headquarters', {'progressive foam technologies'}, ''),  # a short form of the held name
             ('Third Dimension', {'third dimension'}, '')]
    for before, names, want in cases:
        got = judge(before, '', names, names, 'geneva')['kind']
        if got != want: bad.append(f'planted {before!r}: want {want!r}, got {got!r}')
    if against:
        ids = {r['site_id'] for r in read(against)}
    else:
        if not CORPORA[0].exists(): bad.append(f'known answers need the held corpus at {CORPORA[0]}')
        ids = {c['site_id'] for c in find()[0]} if not bad else set()
    bad += [f'known answer {k} is not a candidate' for k in KNOWN if k not in ids]
    print('FAIL' if bad else 'PASS', f'selftest: {len(cases)} planted cases, {len(KNOWN)} known answers')
    for b in bad: print('  ', b)
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--corpus', type=Path, action='append')
    ap.add_argument('--out', type=Path, default=Path(__file__).parent)
    ap.add_argument('--raw', type=Path, help='also write the page excerpts (they can hold personal names; keep outside the repo)')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--against', type=Path, help='with --selftest: check this CANDIDATES.csv instead of running the finder')
    a = ap.parse_args()
    if a.selftest: sys.exit(selftest(a.against))
    cands, tally = find(a.corpus)
    a.out.mkdir(parents=True, exist_ok=True)
    keep = ['site_id', 'cls', 'org_id', 'site_name', 'url', 'corpus', 'sha256']  # no page excerpts: they can hold a person's name
    for path, cols in ((a.out / 'CANDIDATES.csv', keep), (a.raw, keep[:4] + ['street', 'city', 'url', 'sha256', 'printed', 'before', 'match', 'after'])):
        if path:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, cols, extrasaction='ignore'); w.writeheader(); w.writerows(cands)
    (a.out / 'candidates_tally.json').write_text(json.dumps(tally, indent=1) + '\n')
    print(json.dumps(tally, indent=1))


if __name__ == '__main__':
    main()
