#!/usr/bin/env python3
"""Exact packet/no-canonical-change oracle with real admission fault controls."""
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import tempfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def hashes(root):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.csv')}


def replay(builder):
    with contextlib.redirect_stdout(io.StringIO()):
        builder.main()


if __name__ == '__main__':
    base = (HERE / 'base.txt').read_text().strip()
    base_paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', base, 'data'], cwd=ROOT, text=True).splitlines()
    expected = {Path(n).name: hashlib.sha256(subprocess.check_output(['git', 'show', f'{base}:{n}'], cwd=ROOT)).hexdigest() for n in base_paths if n.endswith('.csv')}
    assert hashes(ROOT / 'data') == expected, 'canonical CSV bytes changed'
    pairs = json.loads((HERE / 'pairs.json').read_text())
    final = json.loads((HERE / 'verdicts.json').read_text())
    assert len(pairs) == len(final) == len({v['pair_id'] for v in final}) == 12
    assert {v['pair_id']: (v['a_id'], v['b_id']) for v in final} == {v['pair_id']: (v['a_id'], v['b_id']) for v in pairs}
    flags = list(csv.DictReader((HERE / 'flags.csv').open()))
    assert len(flags) == len({(f['pair_id'], f['record_id']) for f in flags}) == 24
    wanted = {(v['pair_id'], a, b) for v in final for a, b in [(v['a_id'], v['b_id']), (v['b_id'], v['a_id'])]}
    assert {(f['pair_id'], f['record_id'], f['linked_record_id']) for f in flags} == wanted
    assert all(f['settling_fact'] and f['canonical_effect'] == 'none' for f in flags)
    raw = module('rawcheck', HERE / 'rawcheck.py')
    receipts = json.loads((HERE / 'rawcheck.json').read_text())
    assert len(receipts) == len({r['source_url'] for r in receipts}) == 19
    for r in receipts:
        assert hashlib.sha256(Path(r['raw_path']).read_bytes()).hexdigest() == r['raw_sha256']
        text = raw.text_of(Path(r['raw_path']))
        for q in r['quotes']:
            assert raw.matches(text, q['quote']) == q['matched']
    assert sum(r['status'] == 'PASS' for r in receipts) == 15
    assert sum(r['status'] == 'UNCONFIRMED' for r in receipts) == 4
    for v in final:
        assert v['decision'] in ('DISTINCT', 'LINK_FLAG')
        assert v['canonical_effect'].startswith('NONE')
        if v['verdict'] == 'STILL_UNCERTAIN':
            assert v['settling_fact']
        for e in v['evidence']:
            if e['source_date']:
                date.fromisoformat(e['source_date'])
        if v['verdict'] == 'VERIFIED':
            assert v['decision'] == 'DISTINCT'
            assert any(e['source_date'] and e['integrator_raw_status'] == 'PASS' for e in v['evidence'])
    assert {v['pair_id'] for v in final if v['verdict'] == 'VERIFIED'} == {'D03', 'D04'}
    control = json.loads((HERE / 'distinct-location-control.json').read_text())
    assert {r['city'] for r in control['records']} == {'Middlefield', 'Chagrin Falls'}
    # Three distinct real-source known answers and a fabricated quote.
    for fragment in ('Roppe-Press-Release', '20260227571355', 'INDUS.pdf'):
        rc = next(r for r in receipts if fragment in r['source_url'])
        assert all(raw.matches(raw.text_of(Path(rc['raw_path'])), q['quote']) for q in rc['quotes'])
    assert not raw.matches('Roppe Holding parent of Roppe Corporation', 'Roppe Holding is the same legal entity as Roppe Corporation')
    builder = module('builder', HERE / 'build.py')
    output_hashes = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in ('verdicts.json', 'flags.csv')}
    replay(builder)
    assert {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in output_hashes} == output_hashes
    assert hashes(ROOT / 'data') == expected
    with tempfile.TemporaryDirectory() as tmp:
        packet = Path(tmp)
        shutil.copytree(HERE / 'lanes', packet / 'lanes', ignore=shutil.ignore_patterns('__pycache__'))
        for name in ('pairs.json', 'rawcheck.json', 'verdicts.json', 'flags.csv'):
            shutil.copy2(HERE / name, packet / name)
        builder.HERE = packet
        lane = packet / 'lanes/a/verdicts.json'
        original = lane.read_bytes()
        for defect in ('missing', 'duplicate', 'endpoint', 'merge'):
            rows = json.loads(original)
            if defect == 'missing': rows.pop()
            if defect == 'duplicate': rows[-1] = rows[0]
            if defect == 'endpoint': rows[0]['a_id'] = 'SITE-999999'
            if defect == 'merge': rows[0]['decision'] = 'MERGE'
            lane.write_text(json.dumps(rows))
            before = {(packet / n).name: (packet / n).read_bytes() for n in output_hashes}
            try:
                replay(builder)
                raise RuntimeError(f'{defect} was admitted')
            except AssertionError:
                pass
            assert all((packet / n).read_bytes() == before[n] for n in output_hashes), 'failed preflight wrote outputs'
        for defect in ('undated', 'fake_quote'):
            rows = json.loads(original)
            v = next(v for v in rows if v['pair_id'] == 'D03')
            for e in v['evidence']:
                if defect == 'undated': e['source_date'] = ''
                else: e['quote'] = 'Fabricated same legal entity merger of Roppe companies'
            lane.write_text(json.dumps(rows))
            replay(builder)
            amended = next(v for v in json.loads((packet / 'verdicts.json').read_text()) if v['pair_id'] == 'D03')
            assert amended['verdict'] == 'STILL_UNCERTAIN', defect
    assert hashes(ROOT / 'data') == expected
    print('PASS:12 exact adjudications/24 reciprocal flags;2 dated distinct/10 holds;19 sources=15 raw-confirmed+4 unconfirmed;0 canonical changes;idempotent;3 real known answers+6 admission faults;APT raw gap remains explicitly UNINSPECTABLE')
