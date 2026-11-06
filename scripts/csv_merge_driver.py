#!/usr/bin/env python3
"""Conservative three-way merge for keyed Atlas CSV files."""
import csv
import io
import subprocess
import sys
from collections import Counter
from pathlib import Path

from check_row_loss import COMPOSITE, table_of, WHOLE_ROW


def parse(path, table):
    with open(path, encoding='utf-8', newline='') as f:
        rows = list(csv.reader(f, strict=True))
    if not rows:
        raise ValueError('empty CSV')
    header, data = rows[0], rows[1:]
    seen = Counter()
    result = {}
    for row in data:
        if len(row) != len(header):
            raise ValueError('invalid row width')
        if table in WHOLE_ROW:
            key = tuple(row)
        elif table in COMPOSITE:
            fields = dict(zip(header, row))
            key = tuple(fields.get(column, "") for column in COMPOSITE[table])
        else:
            key = row[0]
        if table in WHOLE_ROW:
            seen[key] += 1
            key = (key, seen[key])
        if key in result:
            raise ValueError('duplicate key')
        result[key] = row
    return header, result


def merge(base, ours, theirs, path):
    table = table_of(path)
    bh, b = parse(base, table)
    ah, a = parse(ours, table)
    th, t = parse(theirs, table)
    if bh != ah or bh != th or b.keys() - a.keys() or b.keys() - t.keys():
        raise ValueError('header changed or row deleted')
    result = {}
    for key in b.keys() | a.keys() | t.keys():
        old, left, right = b.get(key), a.get(key), t.get(key)
        if left == right:
            result[key] = left
        elif left == old:
            result[key] = right
        elif right == old:
            result[key] = left
        else:
            raise ValueError(f'conflicting key: {key}')
    # Preserve existing order; insert additions in key order among the existing IDs.
    if table in WHOLE_ROW or table in ('registry_links', 'people_identifiers'):
        keys = list(b) + sorted(result.keys() - b.keys())
    else:
        keys = list(b)
        for key in sorted(result.keys() - b.keys()):
            index = next((i for i, existing in enumerate(keys) if existing > key), len(keys))
            keys.insert(index, key)
    out = io.StringIO(newline='')
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(bh)
    writer.writerows(result[k] for k in keys)
    Path(ours).write_text(out.getvalue(), encoding='utf-8', newline='')


def main():
    base, ours, theirs, path = sys.argv[1:]
    try:
        merge(base, ours, theirs, path)
    except (ValueError, csv.Error, UnicodeError) as e:
        # git merge-file supplies familiar conflict markers; force markers if it
        # would otherwise silently resolve a semantic conflict such as deletion.
        original = Path(ours).read_bytes()
        proc = subprocess.run(['git', 'merge-file', '-p', ours, base, theirs], capture_output=True)
        if proc.returncode == 1:
            Path(ours).write_bytes(proc.stdout)
        else:
            other = Path(theirs).read_bytes()
            Path(ours).write_bytes(b'<<<<<<< ours\n' + original + b'\n=======\n' + other + b'\n>>>>>>> theirs\n')
        print(f'CSV merge conflict in {path}: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
