#!/usr/bin/env python3
"""Apply the reviewed field packet; repeat runs preserve existing evidence IDs."""
import csv
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORPUS = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-corpus-2026-11-16')
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted


def read(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))


def words(s):
    # Same contiguous normalized word-sequence test as ownership round 2 rawcheck_tool.py.
    return re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower())


def validate_packet(packet):
    assert len({(p['org_id'], p['field']) for p in packet}) == len(packet)
    for p in packet:
        assert p['field'] in ('ownership_type', 'year_founded')
        assert p['value'] in ('family_owned', 'private_company', 'employee_owned') if p['field'] == 'ownership_type' else re.fullmatch(r'(18|19|20)\d{2}', p['value'])
        for kind in ('text', 'raw'):
            data = (CORPUS / p[kind + '_file']).read_bytes()
            assert hashlib.sha256(data).hexdigest() == p[kind + '_sha256']
        a, b = words((CORPUS / p['text_file']).read_text()), words(p['quote'])
        assert b and any(a[i:i+len(b)] == b for i in range(len(a)-len(b)+1)), p


def main():
    packet = json.loads((HERE / 'proposals.json').read_text())
    validate_packet(packet)
    groups = {f: read(f) for f in sorted((ROOT / 'data').glob('organizations_*.csv'))}
    orgs = {r['org_id']: (f, r) for f, rows in groups.items() for r in rows}
    evgroups = {}
    touched = set()
    for n, p in enumerate(packet, 373000):
        f, o = orgs[p['org_id']]
        assert o[p['field']] in ('', p['value']), (p, o[p['field']])
        o[p['field']] = p['value']
        touched.add(f)
        ef = ROOT / 'data' / ('evidence_' + f.name)
        ev = dict(evidence_id=f'EVD-{n:06d}', record_table='organizations', record_id=p['org_id'],
                  claim_type='parent' if p['field'] == 'ownership_type' else 'existence',
                  claim_detail=f'{p["field"]}={p["value"]}: "{p["quote"]}"', source_class='own_site',
                  source_ref=p['url'], observed_date='2026-11-16',
                  tier_effect='supports_U' if o['verification_tier'] == 'U' else 'supports_A',
                  created_by='atlas-w16-ownership', notes='Shared retained own-site corpus; quote checked as ordered words. No parent linkage asserted.')
        existing = {r['evidence_id']: r for r in read(ef)}
        if ev['evidence_id'] in existing:
            assert existing[ev['evidence_id']] == ev
        else:
            evgroups.setdefault(ef, []).append(ev)
    for f in sorted(touched):
        with f.open('w', newline='') as out:
            w = csv.DictWriter(out, fieldnames=list(groups[f][0]), lineterminator='\n')
            w.writeheader(); w.writerows(groups[f])
    for f, rows in evgroups.items():
        append_sorted(f, rows, 'evidence_id')
    print(f'{len(packet)} field fills; {len({p["org_id"] for p in packet})} organizations; {sum(map(len, evgroups.values()))} evidence rows appended')


if __name__ == '__main__':
    main()
