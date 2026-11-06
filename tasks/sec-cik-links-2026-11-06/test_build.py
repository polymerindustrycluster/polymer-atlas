"""Reject the entity and data-loss defects this lane could introduce."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import build


class GateTests(unittest.TestCase):
    def test_parent_brand_and_legal_form_collisions(self):
        for held, filer in [('Synventive Molding Solutions, Inc.', 'BARRICK MINING CORP'),
                            ('Legend Brands Inc.', 'RPM INTERNATIONAL INC/DE/'),
                            ('STERIS Corporation', 'STERIS plc'),
                            ('Exxon Mobil Corporation', 'ExxonMobil Holdings Corp')]:
            self.assertFalse(build.own_name(held, filer))
        self.assertTrue(build.own_name('Avient Corporation', 'AVIENT CORP'))

    def test_conflicting_final_link_writes_nothing(self):
        links, _ = build.packet(build.ROOT / 'data')
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            path = data / 'registry_links.csv'
            conflict = dict(links[-1], registry_id='9999999999')
            build.write_csv(path, [conflict], build.COLS)
            before = path.read_bytes()
            with self.assertRaisesRegex(AssertionError, 'another own CIK'):
                build.apply(data, links)
            self.assertEqual(before, path.read_bytes())

    def test_bad_source_and_duplicate_frame_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            here = Path(tmp) / 'packet'
            shutil.copytree(build.HERE, here)
            with patch.object(build, 'HERE', here):
                path = here / 'sources/CIK0001122976.json'
                original = path.read_text()
                for field, value in [('cik', '9999999999'), ('name', 'WRONG ENTITY'), ('tickers', ['WRONG'])]:
                    receipt = json.loads(original)
                    receipt[field] = value
                    path.write_text(json.dumps(receipt))
                    with self.assertRaises(AssertionError):
                        build.packet(build.ROOT / 'data')
                path.write_text(original)
                frame_path = here / 'frame.json'
                frame = json.loads(frame_path.read_text())
                for bad in [frame[:-1], frame[:-1] + [frame[0]]]:
                    frame_path.write_text(json.dumps(bad))
                    with self.assertRaisesRegex(AssertionError, 'frozen frame coverage'):
                        build.packet(build.ROOT / 'data')

    def test_changed_full_snapshot_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            here = Path(tmp) / 'packet'
            shutil.copytree(build.HERE, here)
            path = here / 'sources/company_tickers.json'
            path.write_bytes(path.read_bytes() + b' ')
            with patch.object(build, 'HERE', here):
                with self.assertRaisesRegex(AssertionError, 'snapshot hash mismatch'):
                    build.packet(build.ROOT / 'data')

    def test_additive_alias_only_preserves_identity_gate(self):
        expected = build.packet(build.ROOT / 'data')
        original = build.read
        def changed(field, value):
            def read(path):
                rows = original(path)
                if path.name.startswith('organizations_'):
                    for row in rows:
                        if row['org_id'] == 'ORG-000651':
                            row[field] = value if field != 'trade_names' else value(row[field])
                return rows
            return read
        with patch.object(build, 'read', changed('trade_names', lambda v: v + '; harmless test alias')):
            self.assertEqual(build.packet(build.ROOT / 'data'), expected)
        for field, value in [('legal_name', 'WRONG ENTITY'), ('stock_ticker', 'WRONG'), ('trade_names', lambda v: '')]:
            with patch.object(build, 'read', changed(field, value)):
                with self.assertRaises(AssertionError):
                    build.packet(build.ROOT / 'data')


if __name__ == '__main__':
    unittest.main()
