#!/usr/bin/env python3
"""Apply the verified archive packet; existing links are immutable. Re-run after rebasing."""
import re
import sys
from archive import FIELDS, same_page
from run import HERE, ROOT, read
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted


def main():
    evidence = {r['evidence_id']:r for p in sorted((ROOT/'data').glob('evidence_*.csv')) for r in read(p)}
    packet = read(HERE/'archive_links.csv')
    assert len({r['evidence_id'] for r in packet}) == len(packet)
    target = ROOT/'data/archive_links.csv'
    old = {r['evidence_id']:r for r in read(target)}
    additions = []
    for r in packet:
        eid = r['evidence_id']
        match = re.fullmatch(r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)',r['archive_ref'])
        assert match and eid in evidence and same_page(match[2],evidence[eid]['source_ref']),r
        stamp = match[1]
        assert r['captured_at'] == stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:8],r
        if eid in old: assert old[eid] == r, ('immutable link conflict',eid)
        else: additions.append(r)
    if additions: append_sorted(target,additions,'evidence_id')
    print('archive_links added',len(additions),'packet rows',len(packet))


if __name__ == '__main__': main()
