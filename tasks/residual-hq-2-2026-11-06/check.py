#!/usr/bin/env python3
"""Full-union preservation oracle, byte-idempotency and no-write fault checks."""
import csv
import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(path):
    return list(csv.DictReader(path.open()))


def union(directory, pattern, key):
    result = {}
    for p in directory.glob(pattern):
        for row in read(p):
            assert row[key] not in result, row[key]
            result[row[key]] = row
    return result


def hashes(data):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}


def run(data, expect=0):
    result = subprocess.run(['python3', str(HERE / 'build.py'), '--data-dir', str(data), '--apply'], capture_output=True)
    assert (result.returncode == 0) == (expect == 0), result.stderr.decode()


if __name__ == '__main__':
    data = ROOT / 'data'
    base = (HERE / 'base.txt').read_text().strip()
    oldorg, oldev = {}, {}
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', base, 'data'], cwd=ROOT, text=True).splitlines()
    for name in names:
        key = 'org_id' if Path(name).name.startswith('organizations_') else 'evidence_id' if Path(name).name.startswith('evidence_') else None
        if key:
            rows = list(csv.DictReader(io.StringIO(subprocess.check_output(['git', 'show', f'{base}:{name}'], cwd=ROOT, text=True))))
            dest = oldorg if key == 'org_id' else oldev
            for row in rows:
                assert row[key] not in dest
                dest[row[key]] = row
    updates = json.loads((HERE / 'updates.json').read_text())
    assert not {'ORG-004391', 'ORG-004522'} & set(updates)
    noworg = union(data, 'organizations_*.csv', 'org_id')
    nowev = union(data, 'evidence_*.csv', 'evidence_id')
    assert noworg.keys() == oldorg.keys(), 'organization union changed'
    for oid, old in oldorg.items():
        assert noworg[oid] == old | updates.get(oid, {}).get('fields', {}), oid
    assert all(nowev[eid] == old for eid, old in oldev.items()), 'old evidence content changed'
    assert not {'EVD-315005', 'EVD-315006', 'EVD-315008'} & set(nowev)
    assert noworg['ORG-004391'] == oldorg['ORG-004391'], 'held IDEX row changed'
    assert noworg['ORG-004522'] == oldorg['ORG-004522'], 'held HQ or ownership changed'
    assert set(nowev) - set(oldev) == {s['evidence']['evidence_id'] for s in updates.values()}
    for spec in updates.values():
        assert nowev[spec['evidence']['evidence_id']] == spec['evidence']
    verdicts = read(HERE / 'verdicts.csv')
    assert len(verdicts) == len({r['org_id'] for r in verdicts}) == 100
    assert {r['org_id'] for r in verdicts} == {r['org_id'] for r in read(HERE / 'cohort.csv')}
    assert {r['org_id'] for r in verdicts if r['outcome'] == 'HQ_FOUND'} == set(updates)
    assert all(r['settling_fact'] for r in verdicts if r['outcome'] == 'STILL_UNKNOWN')
    spec = importlib.util.spec_from_file_location('prepare', HERE / 'prepare.py')
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    receipts = {r['org_id']: r for r in json.loads((HERE / 'rawcheck.json').read_text())}
    for oid, update in updates.items():
        rc = receipts[oid]
        assert rc['matched'] and hashlib.sha256(Path(rc['path']).read_bytes()).hexdigest() == rc['raw_sha256']
        assert rc['quote'] in update['evidence']['claim_detail']
        assert rc['url'] == update['evidence']['source_ref']
    assert prep.matches('Headquarters: Troy, Michigan USA', 'Headquarters Troy Michigan USA')
    assert not prep.matches('Mailing address Troy Michigan', 'Headquarters Troy Michigan')
    assert not prep.matches('Headquarters Troy Michigan', 'Headquarters Houston Texas')
    before = hashes(data)
    run(data)
    assert hashes(data) == before, 'replay changed bytes'
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / 'data'
        shutil.copytree(data, scratch)
        packet = Path(tmp) / 'packet'
        packet.mkdir()
        for name in ('cohort.csv', 'verdicts.csv', 'updates.json', 'preimages.csv'):
            shutil.copy2(HERE / name, packet / name)
        spec = importlib.util.spec_from_file_location('poisoned_builder', HERE / 'build.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        builder.HERE = packet
        for held_id, error_text in [('ORG-004522', 'B-PARENT(a)'), ('ORG-004391', 'privacy-contact')]:
            poisoned = dict(updates)
            poisoned[held_id] = json.loads((HERE / 'withdrawn-proposals.json').read_text())[held_id]
            (packet / 'updates.json').write_text(json.dumps(poisoned))
            verdict_rows = read(HERE / 'verdicts.csv')
            for row in verdict_rows:
                if row['org_id'] == held_id:
                    row['outcome'] = 'HQ_FOUND'
            with (packet / 'verdicts.csv').open('w', newline='') as out:
                writer = csv.DictWriter(out, fieldnames=list(verdict_rows[0]), lineterminator='\n')
                writer.writeheader()
                writer.writerows(verdict_rows)
            before = hashes(scratch)
            try:
                builder.main(scratch, apply=True)
                raise RuntimeError(f'{held_id} held proposal was admitted')
            except AssertionError as exc:
                assert error_text in str(exc), exc
            assert hashes(scratch) == before, f'{held_id} mutation caused writes'
        oid = next(iter(updates))
        target = next(p for p in scratch.glob('organizations_*.csv') if any(r['org_id'] == oid for r in read(p)))
        original = target.read_bytes()
        text = target.read_text()
        target.write_text(text.replace(oid, oid + 'X', 1))
        before = hashes(scratch)
        run(scratch, expect=1)
        assert hashes(scratch) == before, 'missing ID caused writes'
        target.write_bytes(original)
        target.write_text(target.read_text().replace('legal_name', 'wrong_header', 1))
        before = hashes(scratch)
        run(scratch, expect=1)
        assert hashes(scratch) == before, 'header conflict caused writes'
        target.write_bytes(original)
        evpath = next(p for p in scratch.glob('evidence_*.csv') if updates[oid]['evidence']['evidence_id'] in p.read_text())
        mutated = read(evpath)
        for row in mutated:
            if row['evidence_id'] == updates[oid]['evidence']['evidence_id']:
                row['source_ref'] = 'https://example.invalid/conflict'
        with evpath.open('w', newline='') as out:
            writer = csv.DictWriter(out, fieldnames=list(mutated[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows(mutated)
        before = hashes(scratch)
        run(scratch, expect=1)
        assert hashes(scratch) == before, 'evidence conflict caused writes'
    print(f'PASS: exact 100 verdicts; {len(updates)} HQ moves; full organization/evidence unions; raw receipts; byte-idempotency; 5 no-write faults including HB&G and IDEX admission; 2 quote substitutions')
