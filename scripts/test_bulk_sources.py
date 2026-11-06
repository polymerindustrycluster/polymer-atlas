"""Known-answer snapshots plus corrupt-input checks; no network by default."""
import csv
import io
import json
import sqlite3
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

try:
    from . import bulk_sources as b
except ImportError:
    import bulk_sources as b


class BulkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cache = Path(self.temp.name)

    def archive(self, name, members):
        path = self.cache / name
        with zipfile.ZipFile(path, 'w') as z:
            for member, data in members.items():
                z.writestr(member, data)
        return path

    def csvzip(self, name, rows):
        data = io.StringIO(newline='')
        writer = csv.DictWriter(data, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        return self.archive(name + '.zip', {name + '.csv': data.getvalue()})

    def test_frs_known_answers_and_blanks(self):
        # IDs/names from the independently held 2026-11-01 ECHO spine.
        rows = [dict(REGISTRY_ID='110007881596', FAC_NAME='STAR PLASTICS, LLC, RAVENSWOOD', FAC_CITY='RAVENSWOOD'),
                dict(REGISTRY_ID='110000344253', FAC_NAME='ARMACELL LLC', FAC_CITY='SPENCER'),
                dict(REGISTRY_ID='110072288286', FAC_NAME='DELRIN USA LLC - BLDG 200', FAC_CITY='WASHINGTON'),
                dict(REGISTRY_ID='', FAC_NAME='UNLINKED', FAC_CITY='SPENCER')]
        path = self.csvzip('frs', rows)
        meta = b.index_file('frs', path, self.cache, expected_count=4)
        self.assertEqual(meta['indexed_rows'], 4)
        for row in rows[:3]:
            self.assertEqual(b.frs_by_registry_id(row['REGISTRY_ID'], self.cache), [row])
            self.assertEqual(b.frs_by_name_city(row['FAC_NAME'].lower(), row['FAC_CITY'], self.cache), [row])
        with sqlite3.connect(self.cache / 'frs.sqlite') as db:
            self.assertEqual(db.execute('SELECT typeof(payload) FROM records LIMIT 1').fetchone()[0], 'blob')
            # Previously installed plain-JSON indexes remain readable.
            db.execute('UPDATE records SET payload=? WHERE id=?', (json.dumps(rows[0]), rows[0]['REGISTRY_ID']))
        self.assertEqual(b.frs_by_registry_id(rows[0]['REGISTRY_ID'], self.cache), [rows[0]])
        self.assertEqual(b.frs_by_registry_id('absent', self.cache), [])
        with self.assertRaises(ValueError):
            b.frs_by_registry_id('', self.cache)

    def sec_fixture(self):
        rows = [(320193, 'Apple Inc.', 'AAPL'), (789019, 'MICROSOFT CORP', 'MSFT'), (1318605, 'Tesla, Inc.', 'TSLA')]
        members = {'CIK' + str(cik).zfill(10) + '.json': json.dumps(dict(cik=cik, name=name, tickers=[ticker], filings={}))
                   for cik, name, ticker in rows}
        members['CIK0000320193-submissions-001.json'] = json.dumps({'accessionNumber': ['1']})
        members['placeholder.txt'] = 'Placeholder file'
        path = self.archive('sec.zip', members)
        meta = b.index_file('sec', path, self.cache, expected_count=4)
        self.assertEqual(meta['archive_members'], 5)
        self.assertEqual(meta['auxiliary_members'], ['placeholder.txt'])
        ticks = self.cache / 'tickers.json'
        ticks.write_text(json.dumps({str(i): dict(cik_str=cik, title=name, ticker=ticker)
                                    for i, (cik, name, ticker) in enumerate(rows)}))
        b.index_file('tickers', ticks, self.cache, expected_count=3)
        return rows

    def test_sec_known_answers(self):
        for cik, name, ticker in self.sec_fixture():
            issuer = b.sec_by_cik('CIK' + str(cik).zfill(10), self.cache)
            self.assertEqual(issuer['name'], name)
            self.assertEqual(issuer['tickers'], [ticker])
            self.assertIn('filings', issuer)
            self.assertEqual(b.sec_by_ticker(ticker.lower(), self.cache)[0]['cik'], cik)
        self.assertIsNone(b.sec_by_cik('9999999', self.cache))
        with self.assertRaises(ValueError):
            b.sec_by_cik('bad', self.cache)

    def test_history_only_and_duplicate_json_preserve_cache(self):
        self.sec_fixture()
        old = b.sec_by_cik(320193, self.cache)
        path = self.archive('history.zip', {
            'CIK0000320193-submissions-001.json': json.dumps({'accessionNumber': ['1']})})
        with self.assertRaisesRegex(ValueError, 'reconciliation'):
            b.index_file('sec', path, self.cache)
        self.assertEqual(b.sec_by_cik(320193, self.cache), old)
        path = self.cache / 'duplicate.json'
        row = json.dumps(dict(cik_str=320193, ticker='AAPL', title='Apple'))
        path.write_text('{"0":' + row + ',"0":' + row + '}')
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            b.index_file('tickers', path, self.cache)
        self.assertEqual(b.sec_by_ticker('AAPL', self.cache)[0], old)

    def test_ticker_punctuation_and_missing_submission(self):
        self.sec_fixture()
        path = self.cache / 'ticks.json'
        path.write_text(json.dumps({'0': dict(cik_str=320193, title='Apple', ticker='X-Y'),
                                    '1': dict(cik_str=789019, title='Microsoft', ticker='X.Y'),
                                    '2': dict(cik_str=99999, title='Missing', ticker='MISSING')}))
        b.index_file('tickers', path, self.cache)
        self.assertEqual(b.sec_by_ticker('X-Y', self.cache)[0]['cik'], 320193)
        self.assertEqual(b.sec_by_ticker('X.Y', self.cache)[0]['cik'], 789019)
        with self.assertRaisesRegex(ValueError, 'absent from submissions'):
            b.sec_by_ticker('MISSING', self.cache)

    def test_gleif_known_answer_and_relationship(self):
        row = {'LEI': 'HWUPKR0MPOU8FGXBT394', 'Entity.LegalName': 'APPLE INC.', 'Entity.LegalAddress.City': 'CUPERTINO'}
        path = self.csvzip('lei', [row])
        b.index_file('lei', path, self.cache, expected_count=1)
        self.assertEqual(b.lei_by_lei(row['LEI'].lower(), self.cache), [row])
        self.assertEqual(b.lei_by_name('Apple Inc.', self.cache), [row])
        # Independently checked against GLEIF's Google direct-parent relationship.
        rr = {'Relationship.StartNode.NodeID': '7ZW8QJWVPR4P1J1KQY45',
              'Relationship.EndNode.NodeID': '5493006MHB84DD0ZWV18',
              'Relationship.RelationshipType': 'IS_DIRECTLY_CONSOLIDATED_BY'}
        b.index_file('rr', self.csvzip('rr', [rr]), self.cache, expected_count=1)
        self.assertEqual(b.lei_relationships('7ZW8QJWVPR4P1J1KQY45', self.cache), [rr])

    def test_count_mismatch_preserves_index(self):
        row = dict(REGISTRY_ID='123', FAC_NAME='Old', FAC_CITY='City')
        path = self.csvzip('frs', [row])
        b.index_file('frs', path, self.cache)
        with self.assertRaisesRegex(ValueError, 'published record count'):
            b.index_file('frs', path, self.cache, expected_count=2)
        self.assertEqual(b.frs_by_registry_id('123', self.cache), [row])

    def test_reject_ragged_empty_duplicate_and_schema_drift(self):
        for text in ['REGISTRY_ID,FAC_NAME,FAC_CITY\n1,a\n', 'wrong\n1\n', 'REGISTRY_ID,FAC_NAME,FAC_CITY\n']:
            with self.assertRaises((ValueError, KeyError)):
                b.index_file('frs', self.archive('bad.zip', {'x.csv': text}), self.cache)
        row = {'LEI': 'same', 'Entity.LegalName': 'a', 'Entity.LegalAddress.City': 'b'}
        with self.assertRaises(sqlite3.IntegrityError):
            b.index_file('lei', self.csvzip('duplicate', [row, row]), self.cache)
        with self.assertRaises(ValueError):
            b.cache_dir(b.REPO / 'build' / 'bulk')
        checkout = self.cache / 'checkout'
        checkout.mkdir()
        (checkout / '.git').write_text('gitdir: elsewhere')
        with self.assertRaises(ValueError):
            b.cache_dir(checkout / 'nested-cache')
        with self.assertRaises(ValueError):
            b.user_agent('no contact')
        with self.assertRaises(Exception):
            b.frs_by_registry_id('123', self.cache)

    def test_census_known_answer_and_limits(self):
        address = ['1', '4600 Silver Hill Rd', 'Washington', 'DC', '20233']
        response = b'"1","4600 Silver Hill Rd, Washington, DC, 20233","Match","Exact","4600 SILVER HILL RD, WASHINGTON, DC, 20233","-76.927,38.846","1","L"\n'
        with patch.object(b, 'urlopen', return_value=io.BytesIO(response)) as fetch:
            result = b.census_batch([address])
            self.assertEqual(result[0][2], 'Match')
            self.assertIn(b'name="addressFile"', fetch.call_args.args[0].data)
            self.assertIn(b'4600 Silver Hill Rd', fetch.call_args.args[0].data)
        with patch.object(b, 'urlopen', return_value=io.BytesIO(b'"1","address","Match"\n')):
            with self.assertRaisesRegex(ValueError, 'match fields'):
                b.census_batch([address])
        for rows in [[], [address] * 10001, [address, address], [['1', '']]]:
            with self.assertRaises(ValueError):
                b.census_batch(rows)
        with patch.object(b, 'urlopen', return_value=io.BytesIO(b'"wrong","address","No_Match"\n')):
            with self.assertRaisesRegex(ValueError, 'ID/count'):
                b.census_batch([address])

    def test_build_uses_full_golden_copy_and_manifest(self):
        row = {'LEI': 'HWUPKR0MPOU8FGXBT394', 'Entity.LegalName': 'Apple Inc.',
               'Entity.LegalAddress.City': 'Cupertino'}
        path = self.csvzip('golden', [row])
        full = {'url': 'https://goldencopy.gleif.org/full.csv.zip',
                'size': path.stat().st_size, 'record_count': 1}
        response = {'data': {'publish_date': '2026-11-06 08:00:00', 'full_file': {'csv': full}}}
        meta = dict(url=full['url'], date='2026-11-06', size=full['size'],
                    sha256=b.sha256(path), file=path.name)
        with patch.object(b, 'urlopen', return_value=io.BytesIO(json.dumps(response).encode())), \
             patch.object(b, 'download', return_value=(path, meta)) as fetch:
            result = b.build(['lei'], self.cache, 'test@example.org')
        self.assertEqual(fetch.call_args.args[0], full['url'])
        self.assertEqual(fetch.call_args.args[3], full['size'])
        self.assertEqual(result['lei']['published_count'], 1)
        self.assertEqual(json.loads((self.cache / 'manifest.json').read_text()), result)

    def test_download_truncation_and_content_addressing(self):
        class Response(io.BytesIO):
            headers = {'Content-Length': '100'}
        with patch.object(b, 'urlopen', return_value=Response(b'bad')):
            with self.assertRaisesRegex(ValueError, 'truncated'):
                b.download('https://example.test', self.cache / 'x.zip', 'test')
        class Good(io.BytesIO):
            headers = {'Content-Length': '2'}
        with patch.object(b, 'urlopen', return_value=Good(b'{}')):
            path, meta = b.download('https://example.test', self.cache / 'x.json', 'test')
        self.assertEqual(meta['size'], 2)
        self.assertEqual(meta['sha256'], b.sha256(path))


if __name__ == '__main__':
    unittest.main()
