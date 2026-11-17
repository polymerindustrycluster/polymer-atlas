"""Refuse replay collisions before any canonical file is written."""
import hashlib
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch
import build


def save(p, rows):
    import csv
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def main():
    inputs = build.read(build.HERE / 'inputs.csv')
    evidence = build.read(build.HERE / 'evidence_packet.csv')
    with tempfile.TemporaryDirectory(prefix='mkt-guards-') as tmp:
        root = Path(tmp)
        shutil.copytree(build.ROOT / 'data', root / 'data')
        snapshot = {p: p.read_bytes() for p in (root / 'data').glob('*.csv')}
        ev = evidence[0]
        source = next(p for p in snapshot if p.name.startswith('evidence_') and any(r['evidence_id'] == ev['evidence_id'] for r in build.read(p)))
        for case in ('duplicate evidence ID', 'foreign evidence shard', 'changed evidence payload', 'conflicting market cell'):
            for p, content in snapshot.items():
                p.write_bytes(content)
            rows = build.read(source)
            if case == 'duplicate evidence ID':
                save(source, rows + [ev])
            elif case == 'foreign evidence shard':
                save(source, [r for r in rows if r['evidence_id'] != ev['evidence_id']])
                target = root / 'data/evidence_organizations_DE.csv'
                assert target != source
                save(target, build.read(target) + [ev])
            elif case == 'changed evidence payload':
                next(r for r in rows if r['evidence_id'] == ev['evidence_id'])['claim_detail'] = 'tampered'
                save(source, rows)
            else:
                p = next(p for p in snapshot if p.name.startswith('organizations_') and not p.name.endswith('_all.csv') and any(r['org_id'] == ev['record_id'] for r in build.read(p)))
                rows = build.read(p)
                next(r for r in rows if r['org_id'] == ev['record_id'])['markets_served'] = 'dental'
                save(p, rows)
            before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in snapshot}
            with patch.object(build, 'ROOT', root):
                try:
                    build.apply(inputs, evidence)
                except AssertionError:
                    pass
                else:
                    raise AssertionError('silent pass: '+case)
            assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in snapshot}, 'failed guard wrote data'
            print('REFUSED BEFORE WRITE:', case)


if __name__ == '__main__':
    main()
