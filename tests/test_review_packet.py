import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('review', Path(__file__).resolve().parents[1] / 'scripts/check_review_packet.py')
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)

class ReviewPacketTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'data').mkdir()
        self.row = {'org_id': 'ORG-000001', 'legal_name': 'A, Inc.', 'status': 'active'}
        self.write(self.row)
        self.packet = {'cases': [{'case_id': 'P1', 'canonical_action': 'none', 'records': [
            {'table': 'organizations', 'id': 'ORG-000001', 'sha256': review.fingerprint(self.row)}]}]}
    def tearDown(self):
        self.tmp.cleanup()
    def write(self, row, tag='OH'):
        with (self.root / 'data' / f'organizations_{tag}.csv').open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=row.keys()); w.writeheader(); w.writerow(row)
    def test_unchanged(self):
        self.assertEqual(review.check_packet(self.root, self.packet), [])
    def test_changed_field_blocks(self):
        self.write(dict(self.row, status='merged'))
        self.assertTrue(review.check_packet(self.root, self.packet))
    def test_removed_id_blocks(self):
        self.write(dict(self.row, org_id='ORG-000002'))
        self.assertTrue(review.check_packet(self.root, self.packet))
    def test_duplicate_current_id_blocks(self):
        self.write(self.row, 'PA')
        self.assertTrue(review.check_packet(self.root, self.packet))
    def test_shard_move_preserves_identity(self):
        (self.root / 'data/organizations_OH.csv').unlink()
        self.write(self.row, 'PA')
        self.assertEqual(review.check_packet(self.root, self.packet), [])
    def test_auto_action_rejected(self):
        self.packet['cases'][0]['canonical_action'] = 'merge'
        self.assertTrue(review.check_packet(self.root, self.packet))

if __name__ == '__main__':
    unittest.main()
