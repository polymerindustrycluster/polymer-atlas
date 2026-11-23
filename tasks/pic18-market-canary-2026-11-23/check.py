#!/usr/bin/env python3
"""Replay the market packet and exercise five separately failing check rules."""
import csv
import gzip
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from math import sqrt
from pathlib import Path
from urllib.parse import urlsplit

from archive import replay_parts
from fetch import D, MAX_PAGES, STORE, decode_body, reg_domain
from frame import frame
from screen import CONTACT

SCHEMA = (D.parents[1] / 'docs' / 'SCHEMA.md').read_text()
VOCAB = set(re.findall(r'`([a-z0-9_]+)`', SCHEMA.split('### 3.3 Markets Served')[1].split('### 3.4 Certifications')[0]))
# Literal wording checks adapted from the November 18 market batches. A reader
# still has to establish that the statement is the sampled operator's.
WORDS = {
    'aerospace_defense': r'aerospace|aviation|defen[cs]e|military|aircraft',
    'automotive_unspecified': r'automotive|auto care',
    'automotive_oem': r'automotive.*(?:oem|original equipment)|car makers',
    'automotive_aftermarket': r'aftermarket',
    'medical_device': r'medical device|medical equipment',
    'medical_healthcare_general': r'healthcare|health care|hospitals|clinics',
    'pharmaceutical_biotech': r'pharmaceutical|biotech',
    'construction_building_products': r'construction|building products|home build|commercial roofing|contractors|building industr',
    'infrastructure_civil': r'infrastructure|civil engineering',
    'packaging_food_beverage': r'packag.*(?:food|beverage|coffee)|(?:food|beverage).*packag',
    'packaging_industrial': r'industrial packag|packag.*industrial',
    'packaging_consumer': r'consumer (?:goods|products).*packag|packag.*consumer (?:goods|products)',
    'food_processing_foodservice': r'food processing|food ?service',
    'cosmetics_personal_care': r'cosmetic|personal care|beauty industr',
    'consumer_goods_housewares': r'housewares|household goods|consumer goods|consumer products',
    'appliances': r'appliance',
    'electronics_electrical': r'electronic|electrical industry',
    'agriculture': r'agricultur|farming',
    'marine': r'marine|boatbuild',
    'energy_oil_gas': r'oil (?:and|&) gas|oilfield|petroleum industry',
    'energy_renewables_battery': r'renewab|batter(?:y|ies)|solar power|wind energy',
    'water_wastewater': r'wastewater|water treatment',
    'plastics_rubber_processors': r'plastic(?:s)? (?:processors|industry|industries|molders)|rubber (?:processors|industry|industries)|polymer process|injection molders|rotomolders|rubber compounds for .*custom molding',
    'tire_rubber_goods': r'\btires?\b|rubber goods',
    'industrial_machinery': r'industrial (?:machinery|equipment)|machine manufacturers',
    'general_industrial': r'industrial (?:market|industr|customers|sectors|clients)|general industr',
    'chemical_mining_metals_processing': r'chemical (?:process|industr)|mining|metal (?:process|forming|forging)',
    'lawn_garden_recreation': r'lawn|garden',
    'toys_sporting_goods': r'toys|sporting goods',
    'footwear_apparel': r'footwear|apparel',
    'telecom_datacom': r'telecom|datacom',
    'furniture_office': r'furniture',
    'rail_transportation': r'railroad|railway|\brail\b',
    'rv_powersports_trailers': r'\brvs?\b|recreational vehicle|trailers|powersports',
    'dental': r'dentistry|dentists|dental',
}
SERVICE = r'\b(?:serv(?:e|es|ed|ing)|support(?:s|ing)?|supply|supplies|provid\w+|offer\w*|develop\w*|specializ\w+|mak(?:e|es|ing)|produc\w+|manufactur\w+|deliver\w*|partner\w*|work\w*|design\w*|us(?:e|ed)|markets)\b'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(name, delimiter=','):
    with (D / name).open() as f:
        return list(csv.DictReader(f, delimiter=delimiter))


def domain(url):
    return reg_domain(urlsplit(url).hostname or '')


def quote_problems(row, page, website, excerpts, skip=''):
    quote, term = row['quote'], row['term']
    witnesses = [x for x in excerpts if x['quote'] == quote]
    pattern = WORDS.get(term)
    rules = {
        'verbatim': bool(witnesses),
        'end-market sentence': (quote.endswith(('.', '!', '?')) and bool(re.search(SERVICE, quote, re.I))
                                and (pattern is None or bool(re.search(pattern, quote, re.I)))),
        'own operator': row['scope'] == 'own' and domain(website) == domain(page['final_url']),
        'organization binding': page['org_id'] == row['org_id'],
        'controlled term': term in VOCAB and pattern is not None,
        'narrative': page['status'] == 'ok' and not page.get('class_fallback')
                     and all(x['kind'] == 'p' for x in witnesses),
        'privacy': not CONTACT.search(quote) and '\n' not in quote,
    }
    return [rule for rule, passes in rules.items() if not passes and rule != skip]


def selftest():
    quote = 'We supply custom housings to manufacturers in the aerospace industry.'
    product = 'We manufacture custom housings, brackets, and covers.'
    row = dict(org_id='ORG-test', term='aerospace_defense', scope='own', quote=quote)
    page = dict(final_url='https://example.com/markets', org_id='ORG-test', status='ok')
    excerpts = [dict(quote=q, kind='p') for q in (quote, product)]
    website = 'https://example.com/'
    assert not quote_problems(row, page, website, excerpts)
    plants = [
        ('paraphrase', 'verbatim', dict(row, quote=quote.replace('custom', 'bespoke')), page),
        ('product list without industry', 'end-market sentence', dict(row, quote=product), page),
        ('parent-group page', 'own operator', dict(row, scope='parent_group'), page),
        ("another organization's page", 'organization binding', row, dict(page, org_id='ORG-other')),
        ('invented term', 'controlled term', dict(row, term='invention_market'), page),
    ]
    for label, rule, bad_row, bad_page in plants:
        assert not quote_problems(bad_row, bad_page, website, excerpts, skip=rule), label
        assert quote_problems(bad_row, bad_page, website, excerpts) == [rule], label
        print(f'{label} passed with rule disabled, failed with rule enabled ({rule})')


def wilson(success, total):
    p, z = success / total, 1.959963984540054
    d = 1 + z*z/total
    center = (p + z*z/(2*total))/d
    half = z*sqrt(p*(1-p)/total + z*z/(4*total*total))/d
    return max(0, center-half), min(1, center+half)


def request_log(store):
    log = store / 'fetches.jsonl'
    entries = [json.loads(line) for line in log.read_text().splitlines()]
    requests = {r['request']: r for r in entries if r['kind'] == 'request'}
    assert [r['request'] for r in entries if r['kind'] == 'request'] == list(range(1, 1 + len(requests)))
    for i, request in requests.items():
        assert (request['sha256'] == '' if request.get('decode_error')
                else re.fullmatch(r'[0-9a-f]{64}', request['sha256']))
        if request['protocol'] == 'http/1.1 retry':
            prev = requests[i-1]
            assert prev['protocol'] == 'default' and prev['exit'] and prev['url'] == request['url']
            assert prev['org_id'] == request['org_id'] and prev['request_kind'] == request['request_kind']
    return entries, requests


def capture_receipts(store, entries, requests, manifest_name):
    pages = {r['request']: r for r in entries if 'text_sha256' in r}
    assert {p.name for p in (store / 'captures').glob('*.json')} == {f'{i}.json' for i in pages}
    manifest = ['{}  fetches.jsonl'.format(sha((store / 'fetches.jsonl').read_bytes()))]
    captures = {}
    for i, page in sorted(pages.items()):
        path = store / 'captures' / f'{i}.json'
        contents = path.read_bytes()
        manifest.append(f'{sha(contents)}  captures/{i}.json')
        capture = json.loads(contents)
        assert capture['request'] == i and capture['raw_sha256'] == page['sha256'] == requests[i]['sha256']
        assert capture['text_sha256'] == page['text_sha256'] and page['org_id'] == requests[i]['org_id']
        captures[i] = capture['excerpts']
    actual = '\n'.join(manifest) + '\n'
    if '--seal' in sys.argv:
        (D / manifest_name).write_text(actual)
    assert (D / manifest_name).read_text() == actual, 'capture manifest changed'
    return pages, captures


def check_archive(store, websites, live_readable, live_fills):
    archive_store = store / 'wayback'
    entries, requests = request_log(archive_store)
    assert {r['org_id'] for r in entries} == websites.keys()
    attempts = Counter(r['org_id'] for r in requests.values())
    assert attempts.keys() == websites.keys() and max(attempts.values()) <= MAX_PAGES
    assert all(r['request_kind'] in ('cdx', 'robots', 'wayback_capture') for r in requests.values())
    lookups = [(r['org_id'], r.get('scope', 'exact')) for r in entries if r['kind'] == 'lookup']
    assert len(lookups) == len(set(lookups))
    assert {o for o, scope in lookups if scope == 'exact'} == websites.keys()
    assert all(scope in ('exact', 'domain') for _, scope in lookups)
    pages, excerpts = capture_receipts(archive_store, entries, requests, 'WAYBACK.sha256')
    sources = {r['request']: r for r in entries if r['kind'] == 'archive_source'}
    assert pages.keys() <= sources.keys()
    for request in requests.values():
        if request['request_kind'] == 'wayback_capture':
            assert replay_parts(request['url'], websites[request['org_id']])
    for i, page in pages.items():
        source = sources[i]
        assert replay_parts(page['final_url'], websites[page['org_id']]) == (source['captured_at'], source['source'])
        assert (source['org_id'], source['status']) == (page['org_id'], page['status'])
        assert requests[i]['request_kind'] == 'wayback_capture'
        assert requests[i]['http'] == 200 and not requests[i]['exit'] and not requests[i]['decode_error']
    selected = set()
    pairs = set()
    outcomes = read('archive_results.tsv', '\t')
    assert len(outcomes) == len(websites) and {r['org_id'] for r in outcomes} == websites.keys()
    for row in read('archive_selection.tsv', '\t'):
        i, oid, term = int(row['request']), row['org_id'], row['term']
        page = dict(pages[i], final_url=sources[i]['source'])
        problems = quote_problems(row, page, websites[oid], excerpts[i])
        assert not problems, (oid, term, problems)
        assert (oid, term) not in pairs
        pairs.add((oid, term))
        selected.add((i, row['quote']))
    assert selected == {(i, x['quote']) for i, values in excerpts.items() for x in values}
    filled = {o for o, _ in pairs}
    readable = {p['org_id'] for p in pages.values() if p['status'] == 'ok'}
    assert filled <= readable
    for row in outcomes:
        oid = row['org_id']
        expected = 'VERIFIED' if oid in filled else 'STILL_UNCERTAIN'
        basis = 'archive_read' if oid in readable else 'no_readable_archive'
        assert (row['verdict'], row['basis']) == (expected, basis)
        assert row['note']
    total_fills = live_fills + len(filled)
    total_readable = live_readable + len(readable)
    lo, hi = wilson(total_fills, 25)
    print(f'archive: {len(readable)}/{len(websites)} rescued, {len(filled)} new fills ({len(pairs)} terms), '
          f'{len(requests)} requests, {len(pages)} HTML captures')
    print(f'combined: 25 = {total_fills} with fills + {total_readable-total_fills} held '
          f'+ {25-total_readable} no readable page; Wilson 95% {lo:.1%}–{hi:.1%}')
    encoded = gzip.compress(b'archive bytes')
    assert decode_body(encoded, 'gzip') == decode_body(encoded, '') == b'archive bytes'
    try:
        decode_body(b'invalid compressed body', 'gzip')
    except OSError:
        pass
    else:
        raise AssertionError('invalid gzip accepted')
    site = 'https://example.com'
    prefix = 'https://web.archive.org/web/'
    assert replay_parts(prefix + '20241123000000id_/https://www.example.com/', site)
    assert not replay_parts(prefix + '20241122235959id_/https://example.com/', site)
    assert not replay_parts(prefix + '20251123000000id_/https://example.org/', site)
    assert not replay_parts(prefix + '20251123000000/https://example.com/', site)
    print('archive selftest: gzip header and magic, broken gzip, date boundary, cross-domain and non-id_ passed')


def main(store):
    drawn, known, counts, pools = frame()
    sampled = read('frame.csv')
    assert [(r['cohort'], int(r['rank']), r['org_id'], r['website']) for r in sampled] == drawn
    websites = {r['org_id']: r['website'] for r in sampled}
    assert len(websites) == 35
    entries, requests = request_log(store)
    assert {r['org_id'] for r in entries} == websites.keys()
    attempts = Counter(r['org_id'] for r in requests.values() if r['request_kind'] != 'robots')
    assert attempts and max(attempts.values()) <= MAX_PAGES
    pages, captures = capture_receipts(store, entries, requests, 'CAPTURES.sha256')
    hits = defaultdict(set)
    selected = set()
    for row in read('selection.tsv', '\t'):
        i, oid, term = int(row['request']), row['org_id'], row['term']
        problems = quote_problems(row, pages[i], websites[oid], captures[i])
        assert not problems, (oid, term, problems)
        assert term not in hits[oid], (oid, term)
        hits[oid].add(term)
        selected.add((i, row['quote']))
    assert selected == {(i, x['quote']) for i, excerpts in captures.items() for x in excerpts}
    home = {r['org_id']: r['status'] for r in entries if r['kind'] == 'home'}
    assert sum(r['kind'] == 'home' for r in entries) == len(home) == len(websites)
    readable = {r['org_id'] for r in pages.values() if r['status'] == 'ok'}
    holds = read('holds.tsv', '\t')
    assert {r['org_id'] for r in holds} == readable - hits.keys()
    assert len(holds) == len(readable - hits.keys())
    assert all(r['reason'] and r['settling_fact'] for r in holds)
    assert hits.keys() <= readable
    for cohort in ('unknown', 'control'):
        ids = {r['org_id'] for r in sampled if r['cohort'] == cohort}
        fills, held, missing = ids & hits.keys(), ids & (readable - hits.keys()), ids - readable
        assert len(fills) + len(held) + len(missing) == len(ids)
        causes = Counter(home[oid] for oid in missing)
        print(f'{cohort}: {len(ids)} = {len(fills)} with terms + {len(held)} held + {len(missing)} no readable page; {dict(sorted(causes.items()))}')
        if cohort == 'unknown':
            assert not any(known[o] for o in ids)
            lo, hi = wilson(len(fills), len(ids))
            print(f'Wilson 95% {lo:.1%}–{hi:.1%}; ×274 {274*lo:.1f}–{274*hi:.1f}; ×{pools[cohort]} {pools[cohort]*lo:.1f}–{pools[cohort]*hi:.1f}')
        else:
            reproduced = {o for o in ids if hits[o] & known[o]}
            agrees = sum(len(hits[o] & known[o]) for o in ids)
            n = sum(len(hits[o]) for o in ids)
            print(f'controls reproduced {len(reproduced)}/{len(ids)} organizations; {agrees}/{n} read term pairs recorded')
            for o in sorted(ids):
                print(f'{o} held={";".join(sorted(known[o]))} matched={";".join(sorted(hits[o] & known[o]))} leads={";".join(sorted(hits[o] - known[o]))}')
    print(f'requests {sum(attempts.values())} page + {len(requests)-sum(attempts.values())} robots = {len(requests)}; HTML captures {len(pages)}')
    print(f'frame {counts}, excluding prior sample {pools}')
    selftest()
    if (D / 'archive_results.tsv').exists():
        missed = {r['org_id']: r['website'] for r in sampled
                  if r['cohort'] == 'unknown' and r['org_id'] not in readable}
        assert len(missed) == 12
        unknown = {r['org_id'] for r in sampled if r['cohort'] == 'unknown'}
        check_archive(store, missed, len(unknown & readable), len(unknown & hits.keys()))


if __name__ == '__main__':
    options = [x for x in sys.argv[1:] if x != '--seal']
    main(Path(options[0]) if options else STORE)
