#!/usr/bin/env python3
"""Freshly fetch every packet capture and fail on missing/unreadable/mismatched content."""
import re
import sys
import hashlib
import time
from archive import same_page
from run import HERE, ROOT, read, fetch, on_page, bound_verdicts, write


def main():
    frozen = (HERE/'archive_links.csv').read_bytes()
    packet = read(HERE/'archive_links.csv')
    verdicts = bound_verdicts()
    receipts = []
    fields = ['evidence_id','archive_ref','quote_sha256','packet_sha256','checked_at']
    write(HERE/'archive_checks.csv',[],fields)
    canonical = {r['evidence_id']:r for r in read(ROOT/'data/archive_links.csv')}
    assert len({r['evidence_id'] for r in packet}) == len(packet)
    pages = {}; failures = []
    for r in packet:
        eid,ref = r['evidence_id'],r['archive_ref']
        v = verdicts[eid]
        if '--packet-only' not in sys.argv:
            assert canonical.get(eid) == r, ('packet not applied',eid)
        assert v['judgment'] == 'SUPPORTED' and v['quote'], eid
        match = re.fullmatch(r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)',ref)
        assert match and same_page(match[2],v['source_ref']),eid
        if ref not in pages:
            time.sleep(2)
            for attempt in range(3):
                pages[ref] = fetch(ref,refresh=True,fallback=False)
                if pages[ref]['status'] == 'ok': break
                code = pages[ref]['attempts'][-1]['status']
                if attempt < 2: time.sleep(max(60 * 2**attempt, pages[ref]['attempts'][-1].get('retry_after',0)) if code == '429' else 10)
        f = pages[ref]
        if f['status'] != 'ok' or f['attempts'][-1]['effective_url'].rstrip('/') != ref.rstrip('/') or not on_page(v['quote'],ROOT/f['page']):
            failures.append(eid)
        else:
            receipts.append(dict(evidence_id=eid,archive_ref=ref,quote_sha256=hashlib.sha256(v['quote'].encode()).hexdigest(),packet_sha256=hashlib.sha256(frozen).hexdigest(),checked_at=f['fetched_at']))
    print('archive fresh re-fetch:',len(packet),'rows;',len(pages),'captures;',len(failures),'failures',flush=True)
    assert (HERE/'archive_links.csv').read_bytes() == frozen, 'packet changed during check'
    if '--packet-only' not in sys.argv:
        assert set(canonical) == {r['evidence_id'] for r in packet}, 'canonical rows outside checked packet'
    assert not failures, failures
    assert packet, 'No archive rows verified: archive gate incomplete (not a vacuous pass)'
    write(HERE/'archive_checks.csv',receipts,fields)


if __name__ == '__main__': main()
