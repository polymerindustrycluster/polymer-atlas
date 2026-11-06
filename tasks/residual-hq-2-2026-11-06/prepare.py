#!/usr/bin/env python3
"""Combine packet verdicts, independently fetch every candidate, then freeze updates."""
import concurrent.futures
import csv
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


fetcher = module('packet_fetch', HERE / 'lanes/a/research.py')
words = module('house_rawcheck', HERE.parent / 'evidence-repair-2-2026-11-04/prep.py').W
fetcher.CACHE = Path('/tmp/residual-hq2-integrator')
fetcher.CACHE.mkdir(exist_ok=True)


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
    matched = matches(text, row['quote'])
    return dict(receipt, matched=matched, quote=row['quote'], text_sha256=hashlib.sha256(text.encode()).hexdigest())


if __name__ == '__main__':
    rows = []
    for lane in ('lead', 'a', 'b'):
        with (HERE / f'lanes/{lane}/verdicts.csv').open() as f:
            packet = list(csv.DictReader(f))
        assert len(packet) == (40 if lane == 'lead' else 30), lane
        rows.extend(packet)
    assert len({r['org_id'] for r in rows}) == 100
    # Bloomberg LEI discovery records are not the state-registry/own-site
    # source requested by this pass. Do not promote their addresses silently.
    for r in rows:
        if r['outcome'] == 'HQ_FOUND' and r['source_class'] == 'registry' and 'apps.sos.wv.gov/' not in r['source_url']:
            r.update(outcome='STILL_UNKNOWN', settling_fact='Own-site, state registry or dated primary public record explicitly designating HQ for this exact held entity.', note='Registry discovery lead held under the pass source restriction: ' + r.get('note', ''))
    for r in rows:
        if r['org_id'] == 'ORG-004530':
            r.update(outcome='STILL_UNKNOWN', settling_fact='Own-site or government HQ witness sufficient for the held B-tier address claim.', note='WV SOS principal office is explicit but registry address caps at C (SCHEMA 4.13); V-25 prevents applying it to held B tier without an unauthorized downgrade. EVD-315008 retired after local preflight, never published.')
    for r in rows:
        if r['org_id'] == 'ORG-004522':
            r.update(outcome='STILL_UNKNOWN', source_class='press', settling_fact='HB&G-issued HQ witness, state registry or dated primary public record for the held entity.', note='B-PARENT(a): MBP is not an already-recorded parent; portfolio source is press ceiling B and undated, not admitted by this pass. EVD-315006 retired; no ownership edit.')
    previous = json.loads((HERE / 'updates.json').read_text()) if (HERE / 'updates.json').exists() else {}
    candidates = [r for r in rows if r['outcome'] == 'HQ_FOUND']
    receipts = json.loads((HERE / 'rawcheck.json').read_text()) if (HERE / 'rawcheck.json').exists() else []
    saved = {r['org_id']: r for r in receipts}
    jobs = []
    for r in candidates:
        if r['org_id'] in saved:
            rc = saved[r['org_id']]
            assert rc['url'] == r['source_url'] and rc['quote'] == r['quote']
            assert hashlib.sha256(Path(rc['path']).read_bytes()).hexdigest() == rc['raw_sha256']
        else:
            jobs.append(r)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        receipts += list(pool.map(observe, jobs))
    byid = {r['org_id']: r for r in receipts}
    old = {r['org_id']: r for r in csv.DictReader((HERE / 'cohort.csv').open())}
    updates = {}
    for r in sorted(rows, key=lambda r: r['org_id']):
        if r['outcome'] != 'HQ_FOUND':
            assert r['settling_fact'], r['org_id']
            continue
        receipt = byid[r['org_id']]
        if not receipt['matched']:
            r.update(outcome='STILL_UNKNOWN', settling_fact='Fresh retrievable own-site HQ designation for the exact held entity; proposed quote could not be reproduced by integrator.', note='Independent raw fetch failed to reproduce proposed quote; availability is not absence.')
            continue
        assert len(r['quote'].split()) <= 25, r['org_id']
        before = old[r['org_id']]
        scope = 'international' if r['hq_country'] != 'US' else 'national_us'
        assert r['hq_state'] != 'OH', 'Ohio scope requires county-specific review'
        fields = {key: r[key] for key in ('hq_city', 'hq_state', 'hq_country')}
        fields.update(hq_county=r.get('hq_county', ''), hq_in_scope=scope,
                      sources=before['sources'] + '; ' + r['source_url'],
                      notes=before['notes'] + ' | HQ placement 2026-11-06: explicit entity HQ; prior county cleared where unsupported. Move is not a tier/status re-verification.')
        eid = previous[r['org_id']]['evidence']['evidence_id'] if r['org_id'] in previous else f'EVD-{315000 + len(updates):06d}'
        updates[r['org_id']] = dict(fields=fields, evidence=dict(
            evidence_id=eid, record_table='organizations', record_id=r['org_id'], claim_type='address',
            claim_detail=f"HQ {r['hq_city']}, {r['hq_state']}, {r['hq_country']}: \"{r['quote']}\"",
            source_class=r['source_class'], source_ref=r['source_url'], observed_date='2026-11-06',
            tier_effect='supports_C' if r['source_class'] == 'registry' else 'supports_A', created_by='codex atlas-L5b-residual-hq',
            notes='Own-site HQ designation independently re-fetched raw 2026-11-06; county left blank unless evidenced; record tier unchanged.'))
    fields = ['org_id', 'legal_name', 'outcome', 'hq_city', 'hq_state', 'hq_country', 'hq_county', 'source_url', 'source_class', 'quote', 'settling_fact', 'note']
    with (HERE / 'verdicts.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: r['org_id']))
    (HERE / 'rawcheck.json').write_text(json.dumps(receipts, indent=2) + '\n')
    (HERE / 'updates.json').write_text(json.dumps(updates, indent=2) + '\n')
    print(f'100 verdicts; {len(updates)} independently checked HQ_FOUND; {100-len(updates)} STILL_UNKNOWN')
