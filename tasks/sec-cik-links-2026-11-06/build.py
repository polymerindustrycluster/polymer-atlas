"""Build and append only source-verified own SEC identities; safe to replay."""
import argparse
import csv
import hashlib
import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COLS = ['org_id', 'registry', 'registry_id', 'match_basis', 'as_of', 'site_id']
FIELDS = ['org_id', 'legal_name', 'stock_ticker', 'resolved_ticker', 'candidate_cik',
          'sec_name', 'verdict', 'finding', 'settling_fact', 'source_url']


def read(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def name_key(name):
    name = re.sub(r'/[A-Z]{2,3}/?', '', name.upper()).replace('&', ' AND ')
    words = re.findall(r'[A-Z0-9]+', name)
    words = words[1:] if words[:1] == ['THE'] else words
    equivalents = {'CORPORATION': 'CORP', 'INCORPORATED': 'INC', 'COMPANY': 'CO', 'LIMITED': 'LTD'}
    return [equivalents.get(w, w) for w in words]


def own_name(held, sec):
    # These two held names omit a legal form; neither conflicts with a different held form.
    if (held, sec) in {('Pentair', 'PENTAIR plc'), ('GrafTech International', 'GRAFTECH INTERNATIONAL LTD')}:
        return True
    return name_key(held) == name_key(sec)


def packet(data):
    frame = json.loads((HERE / 'frame.json').read_text())
    assert len(frame) == 103 and len({r['org_id'] for r in frame}) == 103, 'frozen frame coverage'
    candidates = json.loads((HERE / 'sources/ticker-candidates.json').read_text())
    raw_file = (HERE / 'sources/company_tickers.json').read_bytes()
    manifest = json.loads((HERE / 'sources/ticker-manifest.json').read_text())
    assert manifest['url'] == 'https://www.sec.gov/files/company_tickers.json'
    assert hashlib.sha256(raw_file).hexdigest() == manifest['sha256'], 'full ticker snapshot hash mismatch'
    full = json.loads(raw_file)
    assert len(raw_file) == manifest['size_bytes'] and len(full) == manifest['association_count'] == 10409
    full_index = {(r['ticker'], r['cik_str']): r for r in full.values()}
    assert len(full_index) == 10409 and len({r['cik_str'] for r in full.values()}) == manifest['distinct_ciks'] == 8004
    receipts = json.loads((HERE / 'sources/ticker-receipts.json').read_text())
    assert receipts['url'] == 'https://www.sec.gov/files/company_tickers.json'
    source = {(r['ticker'], r['cik_str']): r for r in receipts['records']}
    by_ticker = {}
    for row in candidates:
        assert row['ticker'] not in by_ticker, 'ambiguous ticker candidate'
        assert full_index[(row['ticker'], row['cik_str'])] == row, 'candidate not in full SEC snapshot'
        by_ticker[row['ticker']] = row
    orgs = {r['org_id']: r for p in data.glob('organizations_*.csv') for r in read(p)}
    links, verdicts = [], []
    for held in frame:
        org = orgs[held['org_id']]
        assert all(org[k] == held[k] for k in held), f"frame identity/input drift {held['org_id']}"
        ticker = 'CSW' if held['org_id'] == 'ORG-002886' else held['stock_ticker']
        row = by_ticker.get(ticker)
        v = {k: '' for k in FIELDS}
        v.update({k: held[k] for k in ('org_id', 'legal_name', 'stock_ticker')})
        v['verdict'] = 'STILL_UNCERTAIN'
        if not row:
            v['finding'] = 'Own ticker-file identity unresolved in the full ticker-association subset; this is not an all-EDGAR search or an absence/listing-status claim.'
            if not held['stock_ticker'] or 'parent' in held['stock_ticker'].lower() or ':' in held['stock_ticker']:
                v['finding'] += ' Held basis may identify a parent or foreign listing, not the held own filer.'
            v['settling_fact'] = 'An own-entity entry in SEC company_tickers.json, confirmed by the SEC company record at the held legal-entity grain.'
        else:
            cik = str(row['cik_str']).zfill(10)
            v.update(resolved_ticker=ticker, candidate_cik=cik, sec_name=row['title'])
            witness = source[(ticker, row['cik_str'])]
            assert all(witness[k] == row[k] for k in ('cik_str', 'ticker', 'title')), 'ticker witness mismatch'
            raw = witness['raw_entry'].split(':', 1)[1]
            assert json.loads(raw) == row, 'raw ticker entry mismatch'
            assert witness['raw_entry'].encode('utf-8') in raw_file, 'literal ticker token absent from full raw source'
            api = json.loads((HERE / 'sources' / f'CIK{cik}.json').read_text())
            url = f'https://data.sec.gov/submissions/CIK{cik}.json'
            v['source_url'] = url
            assert api['url'] == url and api['as_of'] == receipts['as_of'], 'source URL/date mismatch'
            assert not api.get('error') and api['http_status'] == 200, 'SEC company fetch unresolved'
            assert str(api['cik']).zfill(10) == cik and ticker in api['tickers'], 'CIK/ticker mismatch'
            assert api['raw_name_token'] == json.dumps(api['name'], ensure_ascii=False), 'raw name token mismatch'
            assert name_key(api['name']) == name_key(row['title']), 'ticker-file/company-record name disagreement'
            if not own_name(held['legal_name'], api['name']):
                v['finding'] = f"Ticker resolves to {api['name']}; this does not establish the held entity's own filer identity."
                v['settling_fact'] = 'Source-system own-filer identity matching the held entity; a parent, brand, or recycled ticker cannot mint an own SEC_CIK.'
            else:
                v['verdict'] = 'VERIFIED'
                v['finding'] = f"Own issuer name agrees in SEC ticker entry and company record: {api['name']}."
                if ticker != held['stock_ticker']:
                    v['finding'] += ' SEC currently carries CSW; held CSWI is unchanged.'
                links.append(dict(zip(COLS, [held['org_id'], 'SEC_CIK', cik,
                    f"sec_ticker_name_match:{ticker}; sec_submissions_name:{api['name']}; source:{url}", api['as_of'], ''])))
        verdicts.append(v)
    assert len({r['registry_id'] for r in links}) == len(links), 'same own filer attributed twice'
    return links, verdicts


def write_csv(path, rows, fields):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def apply(data, links):
    existing = read(data / 'registry_links.csv')
    key = lambda r: tuple(r[k] for k in ('org_id', 'registry', 'registry_id', 'site_id'))
    old = {key(r): r for r in existing}
    assert len(old) == len(existing), 'duplicate existing registry key'
    pending = []
    for row in links:
        if key(row) in old:
            assert old[key(row)] == row, 'existing key has different values'
        else:
            assert not any(r['org_id'] == row['org_id'] and r['registry'] == 'SEC_CIK' for r in existing), 'another own CIK already linked'
            pending.append(row)
    # Registry rows have composite keys; reuse the established registry writer, not the single-ID shard writer.
    spec = importlib.util.spec_from_file_location('registry_writer', ROOT / 'tasks/registry-links-2026-11-02/build_links.py')
    writer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(writer)
    before = (data / 'registry_links.csv').read_bytes()
    if pending:
        writer.apply(data, pending)
        assert (data / 'registry_links.csv').read_bytes().startswith(before), 'old registry bytes changed'
    return len(pending)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', type=Path, default=ROOT / 'data')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    links, verdicts = packet(args.data_dir)
    if args.apply:
        print('Appended', apply(args.data_dir, links), 'SEC_CIK links')
    else:
        write_csv(HERE / 'new_links.csv', links, COLS)
        write_csv(HERE / 'verdicts.csv', verdicts, FIELDS)
        print('Packet:', len(links), 'VERIFIED;', len(verdicts) - len(links), 'STILL_UNCERTAIN')
