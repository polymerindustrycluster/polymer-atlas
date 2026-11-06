#!/usr/bin/env python3
"""Replay reviewed HQ placements; preflight the entire pass before writing."""
import argparse
import csv
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
from atlas import shard_of
from shard_io import append_sorted


def read(path):
    return list(csv.DictReader(path.open(newline='', encoding='utf-8')))


def write(path, rows, header):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator='\n')
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: r[header[0]]))
    path.write_text(buf.getvalue(), encoding='utf-8', newline='')


def main(data, apply=False):
    cohort = read(HERE / 'cohort.csv')
    verdicts = read(HERE / 'verdicts.csv')
    assert len(cohort) == len(verdicts) == 49
    assert len({r['org_id'] for r in verdicts}) == 49
    assert {r['org_id'] for r in verdicts} == {r['org_id'] for r in cohort}
    assert all(r['outcome'] in ('HQ_FOUND', 'STILL_UNKNOWN') for r in verdicts)
    assert all(r['settling_fact'] for r in verdicts if r['outcome'] == 'STILL_UNKNOWN')
    updates = json.loads((HERE / 'updates.json').read_text())
    assert not {'ORG-009017', 'ORG-009026'} & set(updates)
    assert set(updates) == {r['org_id'] for r in verdicts if r['outcome'] == 'HQ_FOUND'}
    tables = {p.name: read(p) for p in data.glob('organizations_*.csv')}
    evidence = {p.name: read(p) for p in data.glob('evidence_*.csv')}
    headers = {name: next(csv.reader((data / name).open())) for name in tables | evidence}
    org_header = headers['organizations_US.csv']
    ev_header = headers['evidence_organizations_US.csv']
    assert all(headers[n] == org_header for n in tables)
    assert all(headers[n] == ev_header for n in evidence)
    orgs = {r['org_id']: (n, r) for n, rows in tables.items() for r in rows}
    assert len(orgs) == sum(map(len, tables.values()))
    evs = {r['evidence_id']: (n, r) for n, rows in evidence.items() for r in rows}
    assert len(evs) == sum(map(len, evidence.values()))
    changed = set()
    additions = {}
    applied = 0
    for old in cohort:
        oid = old['org_id']
        if oid not in updates:
            continue
        spec = updates[oid]
        fields, newev = spec['fields'], spec['evidence']
        assert set(fields) <= {'hq_city', 'hq_state', 'hq_country', 'hq_county', 'hq_in_scope', 'sources', 'notes'}
        assert old['status'] in ('active', 'unknown')
        assert fields['hq_city'] and fields['hq_country']
        target, status, _ = shard_of('org', fields['hq_state'], fields['hq_country'])
        assert status == 'ok' and target != 'US'
        oname, ename = f'organizations_{target}.csv', f'evidence_organizations_{target}.csv'
        expected = old | fields
        actual_name, actual = orgs[oid]
        assert (actual_name, actual) in [('organizations_US.csv', old), (oname, expected)], f'preimage conflict {oid}'
        eid = newev['evidence_id']
        assert 317000 <= int(eid[4:]) <= 317999
        assert newev['record_id'] == oid and newev['claim_type'] == 'address'
        assert newev['record_table'] == 'organizations'
        assert newev['source_class'] in ('own_site', 'government_filing', 'registry')
        assert newev['tier_effect'] == ('supports_C' if newev['source_class'] == 'registry' else 'supports_A')
        if eid in evs:
            assert evs[eid] == (ename, newev), f'evidence collision {eid}'
            assert actual == expected and actual_name == oname
            continue
        assert actual == old and actual_name == 'organizations_US.csv', f'partial replay {oid}'
        tables['organizations_US.csv'].remove(actual)
        tables.setdefault(oname, []).append(expected)
        changed.update(('organizations_US.csv', oname))
        # Evidence content is immutable; only its home shard changes with its record.
        for name, rows in list(evidence.items()):
            moving = [e for e in rows if e['record_table'] == 'organizations' and e['record_id'] == oid]
            if moving and name != ename:
                evidence[name] = [e for e in rows if e not in moving]
                evidence.setdefault(ename, []).extend(moving)
                changed.update((name, ename))
        additions.setdefault(ename, []).append(newev)
        applied += 1
    assert len({r['evidence_id'] for rows in additions.values() for r in rows}) == sum(map(len, additions.values()))
    assert not set(evs) & {r['evidence_id'] for rows in additions.values() for r in rows}
    for name in changed:
        assert (tables[name] if name in tables else evidence[name]), f'empty shard requires explicit review: {name}'
    if apply:
        for name in sorted(changed):
            rows = tables[name] if name in tables else evidence[name]
            assert rows, f'empty shard requires explicit review: {name}'
            write(data / name, rows, org_header if name in tables else ev_header)
        for name, rows in additions.items():
            path = data / name
            if not path.exists():
                write(path, [], ev_header)
            append_sorted(path, rows, 'evidence_id')
    print(f'{applied} organization moves; {sum(map(len, additions.values()))} new address observations; apply={apply}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', type=Path, default=HERE.parents[1] / 'data')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    main(args.data_dir, args.apply)
