#!/usr/bin/env python3
"""Build the controller-authorized packet-only adjudications and bidirectional flags."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    pairs = json.loads((HERE / 'pairs.json').read_text())
    proposals = sum((json.loads((HERE / f'lanes/{lane}/verdicts.json').read_text()) for lane in ('a', 'b')), [])
    assert len(pairs) == len(proposals) == len({v['pair_id'] for v in proposals}) == 12
    expected = {v['pair_id']: (v['a_id'], v['b_id'], v['record_table']) for v in pairs}
    assert {v['pair_id']: (v['a_id'], v['b_id'], v['record_table']) for v in proposals} == expected
    receipts = {r['source_url']: r for r in json.loads((HERE / 'rawcheck.json').read_text())}
    final, flags = [], []
    for v in sorted(proposals, key=lambda r: r['pair_id']):
        assert v['decision'] in ('DISTINCT', 'LINK_FLAG'), 'no admissible merge in this packet'
        assert v['verdict'] in ('VERIFIED', 'STILL_UNCERTAIN')
        if v['verdict'] == 'STILL_UNCERTAIN':
            assert v['settling_fact']
        for e in v['evidence']:
            r = receipts[e['source_url']]
            quote_match = any(q['quote'] == e['quote'] and q['matched'] for q in r['quotes'])
            e['integrator_raw_status'] = 'PASS' if r['status'] == 'PASS' and quote_match else 'UNCONFIRMED'
            e['integrator_raw_sha256'] = r['raw_sha256']
            # A group page is contextual press when its parent is not recorded.
            if 'innoplast.com/' in e['source_url'] or 'esschem.com/' in e['source_url']:
                e['source_class'] = 'press'
                e['attribution_note'] = 'Unrecorded group/affiliate issuer; contextual witness only, no own_site/tier_A implication (B-PARENT).'
        if v['verdict'] == 'VERIFIED':
            dated = [e for e in v['evidence'] if e['source_date'] and e['integrator_raw_status'] == 'PASS']
            if not dated:
                v.update(verdict='STILL_UNCERTAIN', decision='LINK_FLAG', settling_fact='Independently retrievable dated primary legal-identity witness for this distinction.')
        v['canonical_effect'] = 'NONE: packet-only links/flags; no notes, merge, status, evidence or registry mutation'
        final.append(v)
        settling = v['settling_fact'] or 'Legal entities are distinct on dated witness; shared registry attribution still requires source-system verification.'
        for endpoint, counterpart in [(v['a_id'], v['b_id']), (v['b_id'], v['a_id'])]:
            flags.append(dict(pair_id=v['pair_id'], record_table=v['record_table'], record_id=endpoint,
                              linked_record_id=counterpart, verdict=v['verdict'], decision=v['decision'],
                              settling_fact=settling, canonical_effect='none'))
    (HERE / 'verdicts.json').write_text(json.dumps(final, indent=2) + '\n')
    with (HERE / 'flags.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(flags[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(flags)
    print(f'12 adjudications; {sum(v["verdict"]=="VERIFIED" for v in final)} distinct / {sum(v["verdict"]=="STILL_UNCERTAIN" for v in final)} holds; 24 bidirectional flags; zero canonical writes')


if __name__ == '__main__':
    main()
