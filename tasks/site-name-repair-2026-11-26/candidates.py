#!/usr/bin/env python3
"""Candidate finder for the site-name repair (owner ruling 2026-11-25, "Fix site names, then close").

Reads only held data: data/sites_*.csv, data/organizations_*.csv and the retained own-site corpus
(manifest.csv + page text; pages of one organization on its own domain). No fetch, no model, no write to data/.

Frame: PIC-18 sites (scripts/regions.py: state OH, county in PIC-18) that are active, tier A-C, with a held street.
For each site, every retained own-domain page of its organization is searched for the site's street (atlas.street_key
suffix forms) with the site's city within 150 characters. The name test: does a held name for the site (a part of
`site_name` outside the locality, the organization's `legal_name`, a `trade_names` entry; legal-form words dropped)
appear within 200 characters before or 150 after the street? Yes -> the held name stands on that page. No -> candidate:
the page prints a name beside the street that no held name covers; a reader decides (AGENTS.md section 2 rule 8).

Usage: candidates.py [--corpus DIR]... [--out DIR] [--raw FILE]   (default corpora: the 2026-11-16 corpus and the 2026-11-25 main-fetch run)
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
GENERIC = {'plant', 'hq', 'headquarters', 'facility', 'office', 'division', 'site', 'works', 'operations', 'manufacturing',
           'north', 'south', 'east', 'west', 'campus', 'center', 'branch', 'location', 'warehouse', 'and'}


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


def held_names(site, org):
    """Normalized (name_key) names a page could print for this site: not the city, not generic words."""
    skip = GENERIC | set(squash(site['city']).split())
    raw = re.split(r'\s[—–-]\s', site['site_name']) + [org['legal_name']] + [x for x in org['trade_names'].split(';') if x.strip()]
    out = set()
    for r in raw:
        toks = name_key(re.sub(r'\((?:OSHA|EPA) filing name\)', '', r)).split()
        while toks and toks[0] in skip: toks.pop(0)
        while toks and toks[-1] in skip: toks.pop()
        if toks: out.add(' '.join(toks))
    return out


LABELS = {'address', 'addresses', 'location', 'locations', 'contact', 'contacts', 'us', 'phone', 'tel', 'fax', 'email', 'hours', 'headquarters',
          'corporate', 'office', 'offices', 'main', 'mailing', 'shipping', 'physical', 'visit', 'find', 'our', 'ohio', 'oh', 'usa',
          'plant', 'facility', 'manufacturing', 'located', 'at', 'the', 'in', 'business', 'call', 'directions', 'map', 'get', 'info',
          'information', 'quote', 'request', 'a', 'us:', 'north', 'america', 'united', 'states'} | GENERIC
UI = {'privacy', 'policy', 'terms', 'conditions', 'subscribe', 'closed', 'map', 'maps', 'home', 'careers', 'sitemap', 'tech', 'advice', 'support',
      'follow', 'linked', 'linkedin', 'rights', 'reserved', 'copyright', 'success', 'stories', 'government', 'requirements', 'tradeshows',
      'events', 'glossary', 'faqs', 'faq', 'shipping', 'returns', 'return', 'sign', 'up', 'touch', 'knowledge', 'talk', 'lets', 'let',
      "let's", 'gallery', 'applications', 'saturday', 'sunday', 'monday', 'friday', 'delivery', 'services', 'service', 'life', 'design',
      'capabilities', 'recent', 'projects', 'thank', 'you', 'first', 'last', 'name', 'menu', 'top', 'history', 'molding', 'specialist',
      'javascript', 'sales', 'region', 'literature', 'portal', 'partners', 'other', 'solutions', 'products', 'inspection', 'welding',
      'laser', 'micro', 'connectors', 'precision', 'injection', 'closed', 'window', 'production', 'distribution', 'machinery'}
LEGAL = {'inc', 'llc', 'corp', 'corporation', 'company', 'co', 'ltd', 'lp', 'llp', 'incorporated'}


def printed_name(before):
    """The capitalized run right before the street, after trailing contact labels: what the page prints as the name there."""
    toks = re.findall(r"[A-Za-z0-9&'’.\-]+|[^\sA-Za-z0-9]", before[-160:])
    i = len(toks)
    while i and (re.fullmatch(r'[^\sA-Za-z0-9&]+', toks[i - 1]) or toks[i - 1].lower().strip('.:') in LABELS): i -= 1
    run = []
    while i and len(run) < 8:
        t = toks[i - 1]
        if re.fullmatch(r"[A-Z][A-Za-z0-9&'’.\-]*|&|and|of|the|[A-Z0-9]{2,}", t) and not re.fullmatch(r'\d{5}', t): run.insert(0, t); i -= 1
        else: break
    while run and run[0].lower() in ('and', 'of', 'the', '&'): run.pop(0)
    key = name_key(' '.join(run)).split()
    key = [t for t in key if (t not in LABELS and t not in UI) or t in LEGAL]
    key = [t for t in key if not t.isdigit() and len(t) > 1]
    return (' '.join(run), ' '.join(key)) if key else ('', '')


def same(a, b):
    """Names equal or one inside the other, ignoring spaces (H.B. = HB)."""
    a, b = a.replace(' ', ''), b.replace(' ', '')
    return a in b or b in a


def on_page(quote, text):
    """Contiguous normalized words, as scripts/site_corpus.on_page."""
    q, t = squash(quote).split(), squash(text).split()
    return bool(q) and any(t[i:i + len(q)] == q for i in range(len(t) - len(q) + 1))


def contains(words_text, key):
    return f' {key} ' in f' {words_text} '


def load_pages(corpora):
    pages = {}  # org_id -> [(url, text)]
    for c in corpora:
        for row in read(c / 'manifest.csv'):
            if row['status'] != 'ok' or not row['text_file']: continue
            f = c / row['text_file']
            if f.exists():
                pages.setdefault(row['org_id'], []).append(dict(url=row['final_url'] or row['url'], corpus=c.name, text_file=str(f), via=row['via'], sha256=row['sha256'], raw_file=row['raw_file']))
    return pages


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--corpus', type=Path, action='append')
    ap.add_argument('--out', type=Path, default=Path(__file__).parent)
    ap.add_argument('--raw', type=Path, help='also write the page excerpts (they can hold personal names; keep outside the repo)')
    a = ap.parse_args()
    corpora = a.corpus or CORPORA
    sites = [r for p in sorted(glob.glob(str(ROOT / 'data/sites_*.csv'))) for r in read(p)]
    orgs = {r['org_id']: r for p in sorted(glob.glob(str(ROOT / 'data/organizations_*.csv'))) for r in read(p)}
    frame = [s for s in sites if s['state'] == 'OH' and s['county'].removesuffix(' County') in PIC18
             and s['operating_status'] == 'active' and s['verification_tier'] in 'ABC' and s['street_address'].strip()]
    pages = load_pages(corpora)
    cache, tally, cands = {}, dict(frame=len(frame)), []
    counts = dict(frame_sites_with_own_domain_page=0, sites_street_and_city_on_own_page=0, held_name_beside_street=0, no_name_beside_street=0)
    for s in frame:
        org = orgs.get(s['org_id'])
        if not org: continue
        dom = host_root(org['website'])
        own = [p for p in pages.get(s['org_id'], []) if host_root(p['url']) == dom]
        if not own: continue
        counts['frame_sites_with_own_domain_page'] += 1
        rx, names, city = street_regex(s['street_address']), held_names(s, org), squash(s['city'])
        hits, site_words = [], ''
        for p in own:
            text = cache.get(p['text_file']) or cache.setdefault(p['text_file'], Path(p['text_file']).read_text(encoding='utf-8', errors='replace'))
            site_words += ' ' + squash(text)
            for m in rx.finditer(text) if rx else ():
                if city not in squash(text[max(0, m.start() - CITY_WINDOW):m.end() + CITY_WINDOW]): continue
                before, after = text[max(0, m.start() - BEFORE):m.start()], text[m.end():m.end() + AFTER]
                held = [n for n in names if contains(squash(before + ' ' + after), n)]
                shown, pkey = printed_name(before)
                # a printed name different from every held name: not covered by one, and not a part of one
                differs = bool(pkey) and not any(same(pkey, n) for n in names) and pkey != city
                hits.append(dict(site_id=s['site_id'], org_id=s['org_id'], site_name=s['site_name'], street=s['street_address'], city=s['city'],
                                 url=p['url'], corpus=p['corpus'], via=p['via'], sha256=p['sha256'], held_name_beside=bool(held), printed=shown, differs=differs,
                                 before=' '.join(before.split()), match=m.group(0), after=' '.join(after.split())))
        if not hits: continue
        counts['sites_street_and_city_on_own_page'] += 1
        stood = any(h['held_name_beside'] for h in hits)
        diff = [h for h in hits if h['differs']]
        # B: no held name on any retained page of the organization's own domain (spaces ignored: H.B. = HB)
        absent = not any(contains(site_words, n) or n.replace(' ', '') in site_words.replace(' ', '') for n in names)
        counts['held_name_beside_street'] += stood
        counts['no_name_beside_street'] += not stood and not diff
        cls = 'A' * (not stood and bool(diff)) + 'B' * absent
        if cls: cands.append(dict((diff or hits)[0], cls=cls, held_names_on_site=not absent))
    tally.update(counts, candidates_A_other_name_beside_street=sum('A' in c['cls'] for c in cands),
                 candidates_B_held_name_nowhere_on_site=sum('B' in c['cls'] for c in cands), candidates_union=len(cands))
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
