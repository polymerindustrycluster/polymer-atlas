"""Known-answer and injected replay/quote/transport faults against the new batch gate."""
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch
import check_archives as gate
from archive import FIELDS

quote='Known polymer manufacturing quote for the controlled archive gate'
source='https://example.test/page?key=a/'
ref='https://web.archive.org/web/20260102030405/'+source
cases=[('VERIFIED','ok',ref,quote),('REPLAY_REDIRECT_HOLD','ok',ref[:-1],quote),('REPLAY_REDIRECT_HOLD','ok',ref.replace('20260102030405','20260102030406'),quote),('QUOTE_ABSENT','ok',ref,'Different page body'),('FETCH_FAILED','FETCH_FAILED',ref,'')]
for expected,status,effective,text in cases:
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);proofs=root/'proofs';proofs.mkdir()
        row=dict(evidence_id='EVD-TEST',archive_ref=ref,captured_at='2026-01-02',created_by='test')
        gate.house.write(root/'candidates.csv',[row],FIELDS)
        (root/'page.txt').write_text(text)
        f=dict(status=status,page='page.txt',attempts=[dict(effective_url=effective,status='200' if status=='ok' else '000',retry_after=0)],fetched_at='2026-11-06T14:00:00Z')
        verdict=dict(judgment='SUPPORTED',quote=quote,source_ref=source)
        with patch.object(gate,'HERE',root),patch.object(gate,'ROOT',root),patch.object(gate,'PROOFS',proofs),patch.object(gate.house,'bound_verdicts',return_value={'EVD-TEST':verdict}),patch.object(gate.house,'fetch',return_value=f),patch.object(gate.time,'sleep'):
            try:gate.main()
            except AssertionError as e:assert expected!='VERIFIED' and 'No newly verified archive' in str(e),e
            else:assert expected=='VERIFIED'
        assert gate.house.read(root/'outcomes.csv')[0]['status']==expected
        assert len(gate.house.read(root/'archive_checks.csv'))==int(expected=='VERIFIED')
print('Known-answer positive + query/timestamp redirect/absent quote/failed transport mutations PASS')
