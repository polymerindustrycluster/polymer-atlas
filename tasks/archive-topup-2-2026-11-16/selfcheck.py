"""Malformed references/bytes and one failed item cannot silently break the loop."""
import tempfile
from unittest.mock import patch
from common import *
import fetch
assert not valid_url('Owens Corning certification statement (held record)')
assert not valid_url('https:///missing-host')
assert valid_url('https://example.com/page')
assert byte_run([sys.executable,'-c','import sys;sys.stdout.buffer.write(bytes([255]))'],capture_output=True,text=True).stdout=='\ufffd'
with tempfile.TemporaryDirectory() as d:
    p=Path(d);cache=p/'cache';cache.mkdir()
    rows=[dict(evidence_id='EVD-test-'+str(i),url='https://example.com/'+str(i),quote='fixture quote',url_order=str(i)) for i in (1,2)]
    def request(*args):
        if not getattr(request,'failed',False):request.failed=True;raise OSError('injected item failure')
        return '{}','503',''
    with patch.object(fetch,'PROOFS',p),patch.object(house,'CACHE',cache),patch.object(house,'read',return_value=rows),patch.object(discovery,'request',side_effect=request),patch.object(fetch.time,'sleep'):
        fetch.main()
        fetch.main()
    journal=[json.loads(line) for line in (p/'journal.jsonl').read_text().splitlines()]
    assert len(journal)==2 and journal[0]['status']=='ITEM_ERROR_OSError' and journal[1]['status']=='SPN_FETCH_FAILED_503'
print('URL parser, malformed bytes, item failure, continuation and resume skipping PASS')
