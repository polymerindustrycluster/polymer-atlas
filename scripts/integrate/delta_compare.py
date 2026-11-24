"""Compare lane cell deltas against each head's merge-base with origin/main."""
import argparse
import csv
import io
from pathlib import Path
import subprocess
import tarfile

COMPOSITE = {'registry_links.csv': ('org_id', 'registry', 'registry_id', 'site_id'),
             'people_identifiers.csv': ('person_id', 'identifier_type', 'identifier_id'),
             'ipeds_completions.csv': ('program_key', 'year'),
             'value_basis.csv': ('record_table', 'record_id', 'field', 'value')}


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True)


def table(text, name):
    reader = csv.DictReader(io.StringIO(text))
    header = reader.fieldnames
    if not header:
        raise ValueError(f'{name}: missing header')
    keys = COMPOSITE.get(Path(name).name, (header[0],))
    rows = {}
    occurrences = {}
    for row in reader:
        if None in row or None in row.values():
            raise ValueError(f'{name}: malformed row')
        key = tuple(row[c] for c in keys)
        if Path(name).name == 'inclusion_log.csv':
            whole = tuple(row[c] for c in header)
            occurrences[whole] = occurrences.get(whole, 0) + 1
            key = whole + (str(occurrences[whole]),)
        if key in rows:
            raise ValueError(f'{name}: duplicate key {key}')
        rows[key] = row
    return header, rows


def rows(root, ref):
    result = {}
    archive = subprocess.check_output(['git', '-C', str(root), 'archive', ref, 'data/'])
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        contents = [(member.name, tar.extractfile(member).read().decode('utf-8'))
                    for member in tar if member.isfile() and member.name.endswith('.csv')]
    for path, text in contents:
        name = Path(path).name
        family = ('organizations' if name.startswith(('organizations_', 'ecosystem.')) else
                  'evidence' if name.startswith('evidence') else
                  'sites' if name.startswith('sites_') else name)
        _, records = table(text, name)
        for key, row in records.items():
            k = (family, key)
            if k in result:
                raise ValueError(f'duplicate across shards: {k}')
            result[k] = row
    return result


def delta(root, ref):
    base = git(root, 'merge-base', 'origin/main', ref).strip()
    a, b = rows(root, base), rows(root, ref)
    out = {}
    for key, row in b.items():
        if key not in a:
            out[(key, '*new*')] = tuple(sorted(row.items()))
        else:
            for col in a[key].keys() | row.keys():
                if a[key].get(col) != row.get(col):
                    out[(key, col)] = row.get(col)
    for key in a.keys() - b.keys():
        out[(key, '*removed*')] = True
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('approved'); p.add_argument('candidate')
    p.add_argument('--allow-subset', action='store_true', help='diagnostic only; withdrawals require human review')
    a = p.parse_args()
    root = git('.', 'rev-parse', '--show-toplevel').strip()
    old, new = delta(root, a.approved), delta(root, a.candidate)
    if old == new:
        print('IDENTICAL'); return 0
    if new.items() < old.items():
        print('SUBSET (withdrawals require review)'); return 0 if a.allow_subset else 1
    print(f'DIFFERENT: approved={len(old)} candidate={len(new)} cells/rows')
    for key in sorted(old.keys() | new.keys()):
        if old.get(key) != new.get(key):
            print(key)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
