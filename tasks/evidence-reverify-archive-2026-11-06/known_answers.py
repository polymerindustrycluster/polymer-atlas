"""Four inspected live-page examples plus adversarial matcher mutations."""
from run import HERE, ROOT, read, fetch, on_page
rows = {r['evidence_id']: r for r in read(HERE / 'inputs.csv')}
for eid in ('EVD-013356', 'EVD-013357', 'EVD-013360', 'EVD-013379'):
    e = rows[eid]; f = fetch(e['url'])
    assert f['status'] == 'ok', (eid, f)
    assert on_page(e['quote'], ROOT / f['page']) is True, eid
    assert on_page(e['quote'] + ' zzzcalibrationneedlezzz', ROOT / f['page']) is False, eid
    assert on_page(' '.join(reversed(e['quote'].split())), ROOT / f['page']) is False, eid
    assert on_page('', ROOT / f['page']) is None
    print(eid, 'positive + inserted-defect + reversed-order PASS')

from archive import same_page
assert same_page('http://www.example.com/path/', 'https://EXAMPLE.com/path')
assert not same_page('https://example.com/path', 'https://example.com/other')
assert not same_page('https://example.com/path?x=1', 'https://example.com/path?x=2')
assert not same_page('https://example.com/Path', 'https://example.com/path')
print('V-59 URL binding mutations PASS')

import json
from unittest.mock import patch
import discovery
valid = json.dumps([['timestamp','original'],['20260102030405','https://example.com/claim']])
wrong = json.dumps([['timestamp','original'],['20260102030405','https://example.com/other']])
for payload, code, expected in ((valid,'200','FOUND'), (wrong,'200','NO_EXACT_CAPTURE'),
                                 ('[]','200','NO_CAPTURE'), ('{}','500','CDX_FETCH_FAILED_500'),
                                 ('not json','200','CDX_INVALID_RESPONSE')):
    with patch.object(discovery, 'request', return_value=(payload, code, '')):
        refs, status = discovery.cdx('https://example.com/claim')
        assert status == expected, (status, expected)
        if refs: assert refs == ['https://web.archive.org/web/20260102030405/https://example.com/claim']
print('CDX known-answer exact-page/other-page/empty/error/invalid-response PASS')
