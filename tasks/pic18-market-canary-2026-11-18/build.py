"""Replay the market canary packet (idempotent): 10 frozen frame orgs, ordered-word quote check, fill only a blank markets_served cell."""
import csv
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MKT3 = ROOT / 'tasks/pic18-markets-3-2026-11-16'
STORE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist')
CORPUS, LIVE = STORE / 'pic18-corpus-2026-11-16', STORE / 'pic18-market-canary-2026-11-18'
SNAPSHOT = STORE / 'pic18-markets-3/manifest.snapshot.csv'
BASE = '200859b5'  # merge-base this packet was built on
FIRST_ID, LAST_ID = 396200, 396299
FRAME = 'ORG-000043 ORG-000087 ORG-000157 ORG-000469 ORG-000508 ORG-001380 ORG-001422 ORG-001504 ORG-001892 ORG-002136'.split()  # seed 20261118, drawn by the controller
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(MKT3))  # witness_class is reused from MKT3, not copied
from shard_io import append_sorted
import witness_class

_spec = importlib.util.spec_from_file_location('mkt3_build', MKT3 / 'build.py')
_mkt3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mkt3)
read, found = _mkt3.read, _mkt3.found  # MKT3's csv reader and ordered-word quote matcher
shards = lambda: sorted(p for p in (ROOT / 'data').glob('organizations_*.csv') if p.stem != 'organizations_all')


def write(name, rows):
    with (HERE / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def locate(oid, kind, url):
    """The stored or live page for a quote: (raw path, text path, recorded raw sha256). Hash is checked by the caller."""
    if kind == 'stored':
        r = next(r for r in read(SNAPSHOT) if r['org_id'] == oid and r['url'] == url and r['status'] == 'ok' and r['text_file'])
        return CORPUS / (r['raw_file'] or r['text_file']), CORPUS / r['text_file'], r['sha256']
    assert kind == 'live', kind
    r = next(r for r in read(HERE / 'fetches.csv') if r['org_id'] == oid and r['url'] == url and r['status'] == 'ok' and r['retained'] == 'yes')
    return LIVE / r['raw_file'], LIVE / r['text_file'], r['sha256']


def proposals(orgs):
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']['MARKETS']['values']
    out = []
    for line in (HERE / 'selection.tsv').read_text().splitlines():
        oid, tags, kind, url, quote = line.split('\t')
        assert oid in FRAME, ('outside frame', oid)
        raw, text, recorded = locate(oid, kind, url)
        assert sha(raw) == recorded, ('raw hash mismatch', oid)
        page = text.read_text()
        assert found(page, quote), ('quote absent', oid)
        for value in tags.split(';'):
            assert value in vocab, ('off vocabulary', value)
            out.append(dict(org_id=oid, field='markets_served', value=value, verdict='VERIFIED', source_kind=kind, source_url=url, quote=quote,
                            raw_sha256=recorded, text_sha256=hashlib.sha256(page.encode()).hexdigest(), raw_file=str(raw.relative_to(STORE)),
                            text_file=str(text.relative_to(STORE)), tier_effect='supports_A'))  # narrative sentence on the company's own page
    assert len({(r['org_id'], r['value']) for r in out}) == len(out), 'duplicate proposal'
    for i, r in enumerate(out):
        r['evidence_id'] = f'EVD-{FIRST_ID + i:06d}'
    assert out and out[-1]['evidence_id'] <= f'EVD-{LAST_ID}', 'outside assigned EVD block'
    return out


def apply(inputs, evidence):
    rows = {p: read(p) for p in shards()}
    orgs = {r['org_id']: (p, r) for p, rs in rows.items() for r in rs}
    have = {r['evidence_id'] for p in (ROOT / 'data').glob('evidence_*.csv') for r in read(p)}
    values = {}
    for r in inputs:
        values.setdefault(r['org_id'], []).append(r['value'])
    touched = set()
    for oid, tags in values.items():
        path, row = orgs[oid]
        expected = ';'.join(sorted(tags))
        assert row['markets_served'] in ('', expected), ('target cell is not blank', oid)  # the only write is into a blank cell
        if row['markets_served'] != expected:
            row['markets_served'] = expected
            touched.add(path)
    add = {}
    for ev in evidence:
        if ev['evidence_id'] not in have:
            home = orgs[ev['record_id']][0]
            add.setdefault(home.with_name(home.name.replace('organizations_', 'evidence_organizations_')), []).append(ev)
    backup = LIVE / 'pre-application'
    backup.mkdir(parents=True, exist_ok=True)
    for path in touched | set(add):
        if not (backup / path.name).exists():
            shutil.copyfile(path, backup / path.name)
    for path in sorted(touched):
        with path.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[path][0]), lineterminator='\n')
            w.writeheader()
            w.writerows(rows[path])
    for path, evs in add.items():
        append_sorted(path, evs, 'evidence_id')


def verdict_rows(inputs):
    applied = {}
    for r in inputs:
        applied.setdefault(r['org_id'], []).append(r['value'])
    return [dict(v, values=';'.join(sorted(applied.get(v['org_id'], [])))) for v in read(HERE / 'verdicts.csv')]


def counts_for(orgs, inputs, verdicts):
    ap = {r['org_id'] for r in inputs}
    return dict(frame_organizations=len(FRAME), applied_organizations=len(ap), applied_values=len(inputs),
                applied_by_source=dict(Counter(next(r['source_kind'] for r in inputs if r['org_id'] == o) for o in ap)),
                held_organizations=sum(v['verdict'] == 'STILL_UNCERTAIN' for v in verdicts),
                held_by_class=dict(Counter(v['hold_class'] for v in verdicts if v['verdict'] == 'STILL_UNCERTAIN')),
                applied_tiers=dict(Counter(orgs[o][1]['verification_tier'] for o in ap)),
                mkt3_reach=dict(Counter(v['mkt3_reach'] for v in verdicts)),
                live_fetches=len(read(HERE / 'fetches.csv')))


def main():
    orgs = {r['org_id']: (p, r) for p in shards() for r in read(p)}
    inputs = proposals(orgs)
    evidence = [dict(evidence_id=r['evidence_id'], record_table='organizations', record_id=r['org_id'], claim_type='activity',
                     claim_detail=f'markets_served {r["value"]}: "{r["quote"]}"', source_class='own_site', source_ref=r['source_url'],
                     observed_date='2026-11-18', tier_effect=r['tier_effect'], created_by='claude atlas-w18-mktcanary',
                     notes='Own-company source; field witness retained, SHA256 ' + r['raw_sha256']) for r in inputs]
    apply(inputs, evidence)
    verdicts = verdict_rows(inputs)
    write('inputs.csv', inputs)
    write('evidence_packet.csv', evidence)
    write('verdicts.csv', verdicts)
    counts = counts_for(orgs, inputs, verdicts)
    (HERE / 'counts.json').write_text(json.dumps(counts, indent=2, sort_keys=True) + '\n')
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
