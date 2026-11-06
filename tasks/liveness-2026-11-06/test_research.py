"""Known curl result checks: never mistake a failed/empty route for evidence."""
import unittest
from unittest.mock import patch
from subprocess import CompletedProcess
from research import fetch

class RawCheckTests(unittest.TestCase):
    def result(self,stdout,code=0):
        return CompletedProcess([],code,stdout=stdout,stderr='')

    @patch('research.subprocess.run')
    def test_known_good_words(self,run):
        run.return_value=self.result('<p>Kittyhawk Molding</p>\n200')
        self.assertEqual(fetch(('ORG-X','https://example.com','Kittyhawk Molding'))['raw'],'yes')

    @patch('research.subprocess.run')
    def test_missing_quote(self,run):
        run.return_value=self.result('<p>Other business</p>\n200')
        self.assertEqual(fetch(('ORG-X','https://example.com','Kittyhawk Molding'))['raw'],'no')

    @patch('research.subprocess.run')
    def test_failed_curl_with_body(self,run):
        run.return_value=self.result('Kittyhawk Molding\n200',28)
        self.assertEqual(fetch(('ORG-X','https://example.com','Kittyhawk Molding'))['raw'],'unfetchable')

    @patch('research.subprocess.run')
    def test_http_failure(self,run):
        run.return_value=self.result('Kittyhawk Molding\n403')
        self.assertEqual(fetch(('ORG-X','https://example.com','Kittyhawk Molding'))['raw'],'unfetchable')

    @patch('research.subprocess.run')
    def test_empty_quote_never_passes(self,run):
        run.return_value=self.result('<p>hello</p>\n200')
        self.assertEqual(fetch(('ORG-X','https://example.com',''))['raw'],'no')

if __name__=='__main__': unittest.main()
