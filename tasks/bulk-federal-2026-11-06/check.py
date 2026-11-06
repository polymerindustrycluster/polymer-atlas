#!/usr/bin/env python3
"""Live cache gate: all five snapshots required; no missing-source skips."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts import bulk_sources as b


def check(cache):
    cache = b.cache_dir(cache)
    counts = {}
    for source in ('frs', 'sec', 'tickers', 'lei', 'rr'):
        with sqlite3.connect((cache / (source + '.sqlite')).as_uri() + '?mode=ro', uri=True) as db:
            meta = json.loads(db.execute('SELECT json FROM manifest').fetchone()[0])
            indexed = db.execute('SELECT count(*) FROM records').fetchone()[0]
        raw = cache / meta['file']
        assert raw.stat().st_size == meta['size'], source + ' size mismatch'
        assert b.sha256(raw) == meta['sha256'], source + ' SHA mismatch'
        assert indexed == meta['indexed_rows'], source + ' index yield mismatch'
        assert indexed + meta['historical_members'] == meta['row_count'] == meta['independent_count']
        if meta['published_count'] is not None:
            assert meta['row_count'] == meta['published_count']
        counts[source] = meta['row_count']
    for registry_id, name in [('110007881596', 'STAR PLASTICS'), ('110000344253', 'ARMACELL'),
                              ('110072288286', 'DELRIN')]:
        assert any(name in row['FAC_NAME'] for row in b.frs_by_registry_id(registry_id, cache))
    for cik, ticker in [(320193, 'AAPL'), (789019, 'MSFT'), (1318605, 'TSLA')]:
        assert int(b.sec_by_cik(cik, cache)['cik']) == cik
        assert any(int(row['cik']) == cik for row in b.sec_by_ticker(ticker, cache))
    for lei, legal_name in [('HWUPKR0MPOU8FGXBT394', 'APPLE INC.'),
                            ('7ZW8QJWVPR4P1J1KQY45', 'GOOGLE LLC'),
                            ('5493006MHB84DD0ZWV18', 'ALPHABET INC.')]:
        matches = b.lei_by_lei(lei, cache)
        assert len(matches) == 1 and matches[0]['Entity.LegalName'].upper() == legal_name
        assert any(row['LEI'] == lei for row in b.lei_by_name(legal_name, cache))
    assert any(row['Relationship.EndNode.NodeID'] == '5493006MHB84DD0ZWV18'
               and row['Relationship.RelationshipType'] == 'IS_DIRECTLY_CONSOLIDATED_BY'
               for row in b.lei_relationships('7ZW8QJWVPR4P1J1KQY45', cache))
    print(json.dumps({'PASS': counts, 'unit': 'CSV rows / SEC JSON members / ticker associations'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', type=Path, default=b.DEFAULT_CACHE)
    check(parser.parse_args().cache_dir)
