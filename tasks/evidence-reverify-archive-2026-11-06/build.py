#!/usr/bin/env python3
"""Apply the verified archive packet; existing links are immutable. Re-run after rebasing."""
import re
import hashlib
import sys
from archive import FIELDS, same_page
from run import HERE, ROOT, read, bound_verdicts
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted


def main():
    evidence = {r['evidence_id']:r for p in sorted((ROOT/'data').glob('evidence_*.csv')) for r in read(p)}
    packet = read(HERE/'archive_links.csv')
    verdicts = bound_verdicts()
    receipts = {r['evidence_id']:r for r in read(HERE/'archive_checks.csv')}
    assert set(receipts) == {r['evidence_id'] for r in packet}, 'Run fresh packet check before application'
    digest = hashlib.sha256((HERE/'archive_links.csv').read_bytes()).hexdigest()
    assert len({r['evidence_id'] for r in packet}) == len(packet)
    target = ROOT/'data/archive_links.csv'
    old = {r['evidence_id']:r for r in read(target)}
    additions = []
    for r in packet:
        eid = r['evidence_id']
        v, receipt = verdicts[eid], receipts[eid]
        assert v['judgment'] == 'SUPPORTED' and v['quote'], eid
        assert receipt['archive_ref'] == r['archive_ref'] and receipt['packet_sha256'] == digest, eid
        assert receipt['quote_sha256'] == hashlib.sha256(v['quote'].encode()).hexdigest(), eid
        match = re.fullmatch(r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)',r['archive_ref'])
        assert match and eid in evidence and same_page(match[2],evidence[eid]['source_ref']),r
        stamp = match[1]
        assert r['captured_at'] == stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:8],r
        if eid in old: assert old[eid] == r, ('immutable link conflict',eid)
        else: additions.append(r)
    if additions: append_sorted(target,additions,'evidence_id')
    print('archive_links added',len(additions),'packet rows',len(packet))


if __name__ == '__main__': main()
