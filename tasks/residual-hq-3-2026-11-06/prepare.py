#!/usr/bin/env python3
"""Combine frozen HQ packets; independently raw-fetch each positive once."""
import concurrent.futures
import csv
import hashlib
import importlib.util
import json
import subprocess
from urllib.parse import urlsplit
from pathlib import Path

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


fetcher = module('packet_fetch', HERE / 'fetch.py')
words = module('house_rawcheck', HERE.parent / 'evidence-repair-2-2026-11-04/prep.py').W


def matches(text, quote):
    hay = ' ' + ' '.join(words(text)) + ' '
    for part in quote.split('||'):
        needle = ' ' + ' '.join(words(part)) + ' '
        if not words(part) or needle not in hay:
            return False
        hay = hay[hay.index(needle) + len(needle) - 1:]
    return True


def observe(row):
    receipt, text = fetcher.fetch((row['org_id'], row['source_url']))
    raw = Path(receipt['path'])
    if raw.read_bytes().startswith(b'%PDF'):
        result = subprocess.run(['pdftotext', '-layout', str(raw), '-'], capture_output=True)
        assert result.returncode == 0, result.stderr
        text = result.stdout.decode('utf-8', 'replace')
    return dict(receipt, matched=matches(text, row['quote']), quote=row['quote'],
                text_sha256=hashlib.sha256(text.encode()).hexdigest())


if __name__ == '__main__':
    rows = []
    for lane in ('a', 'b'):
        with (HERE / f'lanes/{lane}/verdicts.csv').open() as f:
            packet = list(csv.DictReader(f))
        assert len(packet) == 50, lane
        rows.extend(packet)
    old = {r['org_id']: r for r in csv.DictReader((HERE / 'cohort.csv').open())}
    assert len(rows) == len({r['org_id'] for r in rows}) == len(old) == 100
    assert {r['org_id'] for r in rows} == set(old)
    for r in rows:
        assert r['outcome'] in ('HQ_FOUND', 'STILL_UNKNOWN')
        if r['outcome'] == 'HQ_FOUND':
            assert old[r['org_id']]['status'] == 'active'
            assert r['source_class'] in ('own_site', 'government_filing', 'registry')
            assert r['quote'] and len(r['quote'].split()) <= 25
            registry_host = urlsplit(r['source_url']).hostname or ''
            state_registry = registry_host.endswith('.gov') or '.state.' in registry_host
            if r['source_class'] == 'registry' and (old[r['org_id']]['verification_tier'] in ('A', 'B') or not state_registry):
                r.update(outcome='STILL_UNKNOWN', settling_fact='Explicit own-site or dated primary HQ witness; address-only registry caps at C and LEI-only discovery is held.', note='Registry proposal held pending stronger exact-entity HQ corroboration.')
            if r['hq_state'] == 'OH':
                r.update(outcome='STILL_UNKNOWN', settling_fact='Explicit HQ county needed to assign Ohio scope without city-based inference.', note='Ohio HQ proposed but county/scope not independently settled in this pass.')
    saved = json.loads((HERE / 'rawcheck.json').read_text()) if (HERE / 'rawcheck.json').exists() else []
    byid = {r['org_id']: r for r in saved}
    for r in rows:
        if r['org_id'] in byid:
            rc = byid[r['org_id']]
            assert r['source_url'] == rc['url'] and r['quote'] == rc['quote'], 'changed source requires explicit new observation'
            assert hashlib.sha256(Path(rc['path']).read_bytes()).hexdigest() == rc['raw_sha256']
    jobs = [r for r in rows if r['outcome'] == 'HQ_FOUND' and r['org_id'] not in byid]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        receipts = saved + list(pool.map(observe, jobs))
    (HERE / 'rawcheck.json').write_text(json.dumps(receipts, indent=2) + '\n')
    byid = {r['org_id']: r for r in receipts}
    updates = {}
    for index, r in enumerate(sorted(rows, key=lambda r: r['org_id'])):
        if r['outcome'] != 'HQ_FOUND':
            assert r['settling_fact'], r['org_id']
            continue
        if not byid[r['org_id']]['matched']:
            r.update(outcome='STILL_UNKNOWN', settling_fact='Fresh retrievable exact-entity HQ witness; integrator could not reproduce proposed quote.', note='Failed raw reproduction is availability/matching uncertainty, never absence.')
            continue
        before = old[r['org_id']]
        fields = {key: r[key] for key in ('hq_city', 'hq_state', 'hq_country')}
        fields.update(hq_county='', hq_in_scope='international' if r['hq_country'] != 'US' else 'national_us',
                      sources=before['sources'] + '; ' + r['source_url'],
                      notes=before['notes'] + ' | HQ placement 2026-11-06: explicit entity HQ; unsupported prior county cleared. Move is not a tier/status re-verification.')
        updates[r['org_id']] = dict(fields=fields, evidence=dict(
            evidence_id=f'EVD-{316000 + index:06d}', record_table='organizations', record_id=r['org_id'], claim_type='address',
            claim_detail=f"HQ {r['hq_city']}, {r['hq_state']}, {r['hq_country']}: \"{r['quote']}\"",
            source_class=r['source_class'], source_ref=r['source_url'], observed_date='2026-11-06', tier_effect='supports_C' if r['source_class'] == 'registry' else 'supports_A',
            created_by='codex atlas-L5b-residual-hq3',
            notes='HQ witness independently re-fetched raw; fetched 2026-11-06; county unsupported and blank; record tier unchanged.'))
    fields = ['org_id', 'legal_name', 'outcome', 'hq_city', 'hq_state', 'hq_country', 'hq_county', 'source_url', 'source_class', 'quote', 'settling_fact', 'note']
    with (HERE / 'verdicts.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: r['org_id']))
    (HERE / 'updates.json').write_text(json.dumps(updates, indent=2) + '\n')
    print(f'100 verdicts; {len(updates)} HQ_FOUND; {100-len(updates)} STILL_UNKNOWN; {len(jobs)} new integrator fetches')
