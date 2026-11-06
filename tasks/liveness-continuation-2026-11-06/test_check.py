"""Yield and trust-boundary known answers for the continuation packet gate."""
import copy
import unittest
from check import validate

class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.queue=[dict(org_id=f'ORG-{n:06}',rank=str(n)) for n in range(11,155)]
        self.rows=[dict(r,verdict='STILL_UNCERTAIN',finding='Primary route unavailable; status unresolved',fetch_count='1',settling_fact='Current named operating witness required') for r in self.queue]
    def test_complete(self):validate(self.queue,self.rows)
    def test_missing_row(self):
        with self.assertRaises(AssertionError):validate(self.queue,self.rows[:-1])
    def test_duplicate_row(self):
        with self.assertRaises(AssertionError):validate(self.queue,self.rows[:-1]+[self.rows[0]])
    def test_empty_hold(self):
        rows=copy.deepcopy(self.rows);rows[0]['settling_fact']=''
        with self.assertRaises(AssertionError):validate(self.queue,rows)
    def test_unwitnessed_verified(self):
        rows=copy.deepcopy(self.rows);rows[0].update(verdict='VERIFIED',source_url='https://example.invalid/',quote='',raw_check='unfetchable')
        with self.assertRaises(AssertionError):validate(self.queue,rows)
    def test_undated_status(self):
        rows=copy.deepcopy(self.rows);rows[0].update(proposed_status='closed',source_date='')
        with self.assertRaises(AssertionError):validate(self.queue,rows)

if __name__=='__main__':unittest.main()
