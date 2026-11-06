"""Gate-level regression for Codex3's redirected replay-query finding."""
import csv
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
import check_archives as checker
from archive import same_capture

SOURCE = 'https://example.test/page?key=a/'
REF = 'https://web.archive.org/web/20260102030405/' + SOURCE
QUOTE = 'This known preserved quote names the actual manufacturing activity stated in the evidence record'


def gate_case(effective, expected):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);(root/'data').mkdir()
        row=dict(evidence_id='EVD-TEST',archive_ref=REF,captured_at='2026-01-02',created_by='test')
        for target in (root/'archive_links.csv',root/'data/archive_links.csv'):
            with target.open('w') as f:
                w=csv.DictWriter(f,fieldnames=list(row));w.writeheader();w.writerow(row)
        (root/'page.txt').write_text(QUOTE)
        verdict=dict(judgment='SUPPORTED',quote=QUOTE,source_ref=SOURCE)
        response=dict(status='ok',page='page.txt',attempts=[dict(effective_url=effective,status='200')],fetched_at='2026-11-06T11:00:00Z')
        with patch.object(checker,'HERE',root),patch.object(checker,'ROOT',root),patch.object(checker,'bound_verdicts',return_value={'EVD-TEST':verdict}),patch.object(checker,'fetch',return_value=response),patch.object(checker.time,'sleep',return_value=None),patch.object(sys,'argv',['check_archives.py']):
            try:
                checker.main()
            except AssertionError as e:
                assert not expected and e.args == (['EVD-TEST'],), e
            else:
                assert expected, 'redirected capture incorrectly passed fresh gate'
        receipts=list(csv.DictReader((root/'archive_checks.csv').open()))
        assert len(receipts) == int(expected)


assert same_capture(REF,REF)
assert not same_capture(REF,REF[:-1])
assert not same_capture(REF,REF.replace('key=a/','key=A/'))
assert not same_capture(REF,REF.replace('20260102030405','20260102030406'))
assert same_capture('https://web.archive.org/web/20260102030405/https://www.example.test/page/', 'https://web.archive.org/web/20260102030405/http://example.test/page')
gate_case(REF,True)
gate_case(REF[:-1],False)
gate_case(REF.replace('20260102030405','20260102030406'),False)
print('Replay binding PASS: exact positive, redirected query and different timestamp rejected; no failed receipts')
