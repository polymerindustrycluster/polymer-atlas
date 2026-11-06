#!/usr/bin/env python3
"""Apply the reviewed L4 packet, refusing drift and ID collisions. Re-run after fresh-main checkout."""
import argparse
import csv
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted
from health import read
spec = importlib.util.spec_from_file_location('record_fixes', ROOT/'tasks/record-fixes-2026-11-03/build_fixes.py')
matcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(matcher)


def write(path, rows, fields=None):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]), lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data-dir', type=Path, default=ROOT/'data')
    p.add_argument('--raw-check', action='store_true', help='check packet against freshly fetched raw_path files')
    a = p.parse_args()
    packet, edits = read(HERE/'evidence_packet.csv'), read(HERE/'edits.csv')
    if a.raw_check:
        assert matcher.has('nylon part','nylon') and not matcher.has('nylon machinery','nylon part')
        checked = []
        for e in packet:
            assert matcher.has(Path(e['raw_path']).read_text(), e['quote']), e['evidence_id']
            checked.append(dict(evidence_id=e['evidence_id'], raw='yes'))
        write(HERE/'rawcheck.csv', checked)
    assert {r['evidence_id'] for r in read(HERE/'rawcheck.csv') if r['raw']=='yes'} == {e['evidence_id'] for e in packet}
    assert len({e['evidence_id'] for e in packet}) == len(packet)
    assert all(170109 <= int(e['evidence_id'][4:]) <= 179999 for e in packet)
    ev_by = {e['evidence_id']:e for e in packet}
    shards = {p:read(p) for p in sorted(a.data_dir.glob('organizations_*.csv')) if not p.name.endswith('_all.csv')}
    org = {r['org_id']:(path,r) for path, rows in shards.items() for r in rows}
    all_ev = []
    ev_locations = {}
    for path in a.data_dir.glob('evidence_*.csv'):
        for row in read(path):
            assert row['evidence_id'] not in ev_locations, 'duplicate global evidence ID'
            ev_locations[row['evidence_id']] = path
            all_ev.append(row)
    for row in packet:
        expected = a.data_dir / ('evidence_' + org[row['record_id']][0].name)
        if row['evidence_id'] in ev_locations:
            assert ev_locations[row['evidence_id']] == expected, 'existing evidence ID in wrong shard'
    for e in packet:
        for held in all_ev:
            if held['evidence_id'] == e['evidence_id']:
                assert all(held[k] == e[k] for k in held), 'global evidence ID collision'
    touched = set()
    for e in edits:
        assert e['field'] in {'website','verification_tier'}
        assert e['evidence_ids'] and all(ev_by[i]['record_id']==e['org_id'] for i in e['evidence_ids'].split(';')), e
        path, r = org[e['org_id']]
        assert r[e['field']] in {e['old'], e['new']}, ('drift',e)
        if r[e['field']] != e['new']:
            r[e['field']] = e['new']; touched.add(path)
    for oid in {e['org_id'] for e in edits if e['field'] == 'verification_tier'}:
        witnessed = [e for e in all_ev + packet if e['record_id'] == oid and e['record_table'] == 'organizations']
        assert {'existence','address','scope'} <= {e['claim_type'] for e in packet if e['record_id']==oid and e['source_class']=='own_site' and e['tier_effect']=='supports_A'}, ('missing fresh own must-have',oid)
        must = {'existence','address','scope','activity','liveness','code'}
        strength = {'supports_C':1, 'supports_B':2, 'supports_A':3}
        ranks = []
        for claim in must:
            rows = [e for e in witnessed if e['claim_type'] == claim]
            supporting = [e for e in rows if e['tier_effect'] != 'contradicts']
            if not rows: continue
            assert supporting, ('unsupported claim',oid,claim)
            assert all(e['observed_date'] < max(x['observed_date'] for x in supporting) for e in rows if e['tier_effect']=='contradicts'), ('contradiction',oid,claim)
            ranks.append(max(strength[e['tier_effect']] for e in supporting))
        assert {'existence','address','scope'} <= {e['claim_type'] for e in witnessed}
        assert org[oid][1]['verification_tier'] == {1:'C',2:'B',3:'A'}[min(ranks)], ('tier restatement',oid)
    # Validate all prospective evidence before mutating any file.
    pending = defaultdict(list)
    for e in packet:
        path = a.data_dir/('evidence_'+org[e['record_id']][0].name)
        fields = list(read(path)[0])
        row = {k:e[k] for k in fields}
        existing = {r['evidence_id']:r for r in read(path)}
        if row['evidence_id'] in existing:
            assert existing[row['evidence_id']] == row, 'evidence ID collision'
        else:
            pending[path].append(row)
    for path in touched: write(path,shards[path])
    for path,rows in pending.items(): append_sorted(path,rows,'evidence_id')
    print(f'Applied {len(edits)} evidenced cells across {len({e["org_id"] for e in edits})} organizations; {len(packet)} evidence rows')


if __name__ == '__main__':
    main()
