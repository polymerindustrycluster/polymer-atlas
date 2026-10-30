#!/usr/bin/env python3
"""Read-only preflight for adjudication packets. Never applies a proposed motion."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def fingerprint(row):
    return hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def check_packet(root, packet):
    errors = []
    tables = {}
    for table in ('organizations', 'sites'):
        key = 'org_id' if table == 'organizations' else 'site_id'
        rows = {}
        for path in sorted((root / 'data').glob(table + '_*.csv')):
            with path.open(newline='', encoding='utf-8') as stream:
                for row in csv.DictReader(stream):
                    identifier = row[key]
                    if identifier in rows:
                        errors.append(f'duplicate current ID: {table}/{identifier}')
                    rows[identifier] = row
        tables[table] = rows
    seen = set()
    for case in packet['cases']:
        label = case['case_id']
        if label in seen:
            errors.append(f'duplicate case ID: {label}')
        seen.add(label)
        if case.get('canonical_action') != 'none':
            errors.append(f'{label}: review packet must not authorize an automatic action')
        for ref in case['records']:
            row = tables.get(ref['table'], {}).get(ref['id'])
            if row is None:
                errors.append(f"{label}: missing {ref['table']}/{ref['id']}")
            elif fingerprint(row) != ref['sha256']:
                errors.append(f"{label}: changed {ref['table']}/{ref['id']} — re-adjudicate")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check_packet(args.root, json.loads(args.packet.read_text(encoding='utf-8')))
    for error in errors:
        print('ERROR', error)
    if not errors:
        print('OK — all referenced rows match; this does not approve any proposed motion.')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
