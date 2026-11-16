"""Replay the MKT3 markets packet (idempotent): frozen frame, ordered-word quote check, one value / one evidence row."""
import csv
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from functools import cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STORE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist')
CORPUS = STORE / 'pic18-corpus-2026-11-16'
SNAPSHOT = STORE / 'pic18-markets-3/manifest.snapshot.csv'
BASE = 'd410968ab2967b9fedc4d7350204289375a3abc4'
FIRST_ID = 389000
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted


def read(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows):
    assert rows
    with (HERE / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def norm(s):
    return ' '.join(re.findall(r'\w+', s.lower()))


def found(text, quote):
    return bool(norm(quote)) and norm(quote) in norm(text)


@cache
def at_base(p):
    text = subprocess.check_output(['git', 'show', f'{BASE}:{p.relative_to(ROOT)}'], cwd=ROOT, text=True)
    return list(csv.DictReader(io.StringIO(text)))


def source():
    assert hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest() == json.loads((HERE / 'corpus.json').read_text())['manifest_sha256'], 'manifest changed'
    orgs = {r['org_id']: (p.name, r) for p in sorted((ROOT / 'data').glob('organizations_*.csv'))
            if p.stem != 'organizations_all' for r in at_base(p)}
    manifest = read(SNAPSHOT)
    pages = [r for r in manifest if r['status'] == 'ok' and r['text_file']]
    prior = {r['org_id'] for r in read(HERE / 'prior_lanes.csv')}
    frame = {oid: orgs[oid] for oid in sorted({r['org_id'] for r in pages})
             if not orgs[oid][1]['markets_served'] and oid not in prior}
    return orgs, manifest, pages, frame, prior


def proposals(frame, pages):
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']['MARKETS']['values']
    result = []
    for line in (HERE / 'selection.tsv').read_text().splitlines():
        oid, tags, url, quote = line.split('\t')
        assert oid in frame, ('outside blank-markets frame', oid)
        page = next(r for r in pages if r['org_id'] == oid and r['url'] == url)
        raw = CORPUS / (page['raw_file'] or page['text_file'])
        assert hashlib.sha256(raw.read_bytes()).hexdigest() == page['sha256'], 'raw hash mismatch'
        text = (CORPUS / page['text_file']).read_text()
        assert found(text, quote), ('quote absent', oid, quote)
        for value in tags.split(';'):
            assert value in vocab, ('off vocabulary', value)
            result.append(dict(org_id=oid, field='markets_served', value=value, verdict='VERIFIED', applied='applied',
                               source_url=url, quote=quote, raw_sha256=page['sha256'],
                               text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                               raw_file=page['raw_file'], text_file=page['text_file'],
                               tier_effect='supports_U' if frame[oid][1]['verification_tier'] == 'U' else 'supports_A'))
    assert len({(r['org_id'], r['value']) for r in result}) == len(result), 'duplicate proposal'
    assert len(result) <= 2000, 'outside assigned EVD block'
    for i, r in enumerate(result):
        r['evidence_id'] = f'EVD-{FIRST_ID + i:06d}'
    return result


def apply(inputs, evidence):
    shards = {p: read(p) for p in sorted((ROOT / 'data').glob('organizations_*.csv')) if p.stem != 'organizations_all'}
    orgs = {r['org_id']: (p, r) for p, rows in shards.items() for r in rows}
    assert len(orgs) == sum(map(len, shards.values())), 'duplicate organization IDs'
    evs = [(p, r) for p in (ROOT / 'data').glob('evidence_*.csv') for r in read(p)]
    have = {r['evidence_id']: (p, r) for p, r in evs}
    assert len(have) == len(evs), 'duplicate evidence IDs'
    values = defaultdict(set)
    for r in inputs:
        values[r['org_id']].add(r['value'])
    touched, additions = set(), defaultdict(list)
    for oid, tags in values.items():
        path, row = orgs[oid]
        expected = ';'.join(sorted(tags))
        assert row['markets_served'] in ('', expected), ('conflicting target cell', oid)
        if row['markets_served'] != expected:
            row['markets_served'] = expected
            touched.add(path)
    for ev in evidence:
        target = orgs[ev['record_id']][0].with_name(orgs[ev['record_id']][0].name.replace('organizations_', 'evidence_organizations_'))
        assert target.exists(), 'missing evidence shard'
        if ev['evidence_id'] in have:
            path, old = have[ev['evidence_id']]
            assert path == target and old == ev, 'evidence replay mismatch'
        else:
            additions[target].append(ev)
    backup = STORE / 'pic18-markets-3/pre-application'
    backup.mkdir(parents=True, exist_ok=True)
    for path in touched | set(additions):
        if not (backup / path.name).exists():
            shutil.copyfile(path, backup / path.name)
    for path in sorted(touched):
        with path.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(shards[path][0]), lineterminator='\n')
            w.writeheader()
            w.writerows(shards[path])
    for path, rows in additions.items():
        append_sorted(path, rows, 'evidence_id')
    by_shard = {}
    for oid, tags in values.items():
        c = by_shard.setdefault(orgs[oid][0].name, dict(evidence_rows=0, market_cells=0, market_values=0))
        c['market_cells'] += 1
        c['market_values'] += len(tags)
        c['evidence_rows'] += len(tags)
    (HERE / 'application.json').write_text(json.dumps(dict(base=BASE, cells=len(values), evidence_rows=len(evidence), by_shard=by_shard), indent=2, sort_keys=True) + '\n')


def holds_for(frame, inputs, own_pages):
    reviewed = {r['org_id']: r for r in read(HERE / 'reviewed_holds.csv')}
    done = {r['org_id'] for r in inputs}
    holds = []
    for oid in frame:
        if oid in done:
            continue
        r = reviewed.get(oid)
        holds.append(dict(org_id=oid, tier=frame[oid][1]['verification_tier'], field='markets_served', verdict='STILL_UNCERTAIN', applied='held',
                          hold_class=r['hold_class'] if r else 'not_adjudicated',
                          note=r['note'] if r else 'Not reached in the 35-minute budget (or no market sentence surfaced by the screening pass)',
                          settling_fact='Exact-entity own-product or own-customer narrative naming a MARKETS vocabulary market; navigation, group or off-vocabulary labels do not settle it.',
                          retained_pages=len(own_pages[oid])))
    return holds


def main():
    orgs, manifest, pages, frame, prior = source()
    inputs = proposals(frame, pages)
    own = defaultdict(list)
    for p in pages:
        own[p['org_id']].append(p)
    holds = holds_for(frame, inputs, own)
    frame_rows = [dict(org_id=oid, legal_name=org['legal_name'], shard=shard, tier=org['verification_tier'], retained_pages=len(own[oid]))
                  for oid, (shard, org) in frame.items()]
    write('frame.csv', frame_rows)
    write('inputs.csv', inputs)
    write('holds.csv', holds)
    evidence = [dict(evidence_id=r['evidence_id'], record_table='organizations', record_id=r['org_id'], claim_type='activity',
                     claim_detail=f'markets_served {r["value"]}: "{r["quote"]}"', source_class='own_site', source_ref=r['source_url'],
                     observed_date='2026-11-16', tier_effect=r['tier_effect'], created_by='claude atlas-w16-mkt3',
                     notes='Own-company source; field witness retained, SHA256 ' + r['raw_sha256']) for r in inputs]
    apply(inputs, evidence)
    write('evidence_packet.csv', evidence)
    counts = counts_for(manifest, pages, frame, inputs, holds, prior)
    (HERE / 'counts.json').write_text(json.dumps(counts, indent=2, sort_keys=True) + '\n')
    print(json.dumps(counts))


def counts_for(manifest, pages, frame, inputs, holds, prior):
    ap = {r['org_id'] for r in inputs}
    return dict(manifest_organizations=len({r['org_id'] for r in manifest}),
                retained_organizations=len({r['org_id'] for r in pages}),
                prior_lane_organizations_excluded=len(prior),
                frame_organizations=len(frame),
                frame_tiers=dict(Counter(org['verification_tier'] for _, org in frame.values())),
                proposed_organizations=len(ap), proposed_values=len(inputs),
                proposed_organization_tiers=dict(Counter(frame[o][1]['verification_tier'] for o in ap)),
                held_organizations=len(holds),
                held_by_class=dict(Counter(h['hold_class'] for h in holds)))


if __name__ == '__main__':
    main()
