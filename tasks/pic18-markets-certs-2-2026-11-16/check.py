"""Reconcile the complete frame, retained-page hashes, proposals and per-field holds."""
import copy
import hashlib
import json
from collections import Counter
from build import HERE, ROOT, CORPUS, FIELDS, read, source, proposals, found, at_base, BASE, witness_pages, certificate_check


def verify(inputs, frames, holds):
    _, _, pages, frame = source()
    assert len(frames) == len(frame) and {r['org_id'] for r in frames} == set(frame), 'frame yield'
    assert len({r['org_id'] for r in frames}) == len(frames), 'duplicate frame'
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']
    accepted = set()
    for r in inputs:
        key = (r['org_id'], r['field'], r['value'])
        assert key not in accepted, 'duplicate proposal'
        accepted.add(key)
        assert r['org_id'] in frame and r['field'] in FIELDS
        assert r['value'] in vocab['MARKETS' if r['field'] == 'markets_served' else 'CERTS']['values'], 'off vocabulary'
        assert not frame[r['org_id']][1][r['field']], 'nonblank target'
        p = next(p for p in witness_pages(pages) if p['org_id'] == r['org_id'] and p['url'] == r['source_url'])
        assert r['raw_file'] == p['raw_file'] and r['text_file'] == p['text_file']
        assert r['raw_sha256'] == p['sha256'] == hashlib.sha256((CORPUS / (p['raw_file'] or p['text_file'])).read_bytes()).hexdigest(), 'raw hash mismatch'
        text = (CORPUS / p['text_file']).read_text()
        assert hashlib.sha256(text.encode()).hexdigest() == r['text_sha256'], 'text hash mismatch'
        assert found(text, r['quote']), 'quote absent'
        if r['field'] == 'certifications':
            certificate_check(next(c for c in witness_pages([]) if c['org_id'] == r['org_id']), text)
        assert r['tier_effect'] == ('supports_U' if frame[r['org_id']][1]['verification_tier'] == 'U' else 'supports_A')
    blank = {(oid, f) for oid, (_, org) in frame.items() for f in FIELDS if not org[f]}
    applied = {(r['org_id'], r['field']) for r in inputs}
    held = {(r['org_id'], r['field']) for r in holds}
    assert len(holds) == len(held) and not applied & held and applied | held == blank, 'field coverage yield'
    assert all(r['settling_fact'] and r['verdict'] == 'STILL_UNCERTAIN' for r in holds)
    assert inputs == proposals(frame, pages), 'selection mismatch'


def boundary(inputs, evidence):
    homes = source()[0]
    values = {}
    for r in inputs:
        values.setdefault((r['org_id'],r['field']), set()).add(r['value'])
    evs = {r['evidence_id']: r for r in evidence}
    cells, new_evs = 0, 0
    shards = {}
    for p in sorted((ROOT / 'data').glob('*.csv')):
        if p.name.endswith('_all.csv'):
            continue
        before, after = at_base(p), read(p)
        if p.name.startswith('organizations_'):
            expected = copy.deepcopy(before)
            for r in expected:
                for field in FIELDS:
                    if (r['org_id'],field) in values:
                        assert not r[field]
                        r[field] = ';'.join(sorted(values[(r['org_id'],field)]))
                        shards[r['org_id']] = p.name
                        cells += 1
            assert after == expected, ('unrelated organization change', p)
        elif p.name.startswith('evidence_organizations_'):
            append = [r for r in evidence if homes[r['record_id']][0] == p.name.replace('evidence_organizations_', 'organizations_')]
            assert not set(evs) & {r['evidence_id'] for r in before}, 'reused evidence ID'
            assert after == sorted(before + append, key=lambda r: r['evidence_id']), ('evidence delta mismatch', p)
            new_evs += len(append)
        else:
            assert before == after, ('out of scope data change', p)
    assert cells == len(values) and new_evs == len(evidence), 'application yield'
    assert len(read(HERE / 'holds.csv')) == len({(r['org_id'],r['field']) for r in read(HERE / 'holds.csv')}), 'duplicate holds'
    app = json.loads((HERE / 'application.json').read_text())
    counts = {}
    for (oid, field), tags in values.items():
        c = counts.setdefault(shards[oid], dict(field_cells=0, value_rows=0, evidence_rows=0))
        c['field_cells'] += 1
        c['value_rows'] += len(tags)
        c['evidence_rows'] += len(tags)
    assert app == dict(base=BASE, cells=cells, evidence_rows=new_evs, by_shard=counts)
    print('BOUNDARY PASS:', cells, 'field cells;', new_evs, 'new evidence rows; other data unchanged')


def main():
    inputs, frames, holds = [read(HERE / f) for f in ('inputs.csv', 'frame.csv', 'holds.csv')]
    verify(inputs, frames, holds)
    for name, mutate in [
        ('fabricated quote', lambda i, f, h: i[0].update(quote='fabricated violet elephant market')),
        ('off vocabulary', lambda i, f, h: i[0].update(value='consumer_goods')),
        ('missing field disposition', lambda i, f, h: h.pop()),
        ('raw hash tampering', lambda i, f, h: i[0].update(raw_sha256='0'*64)),
        ('duplicate proposal', lambda i, f, h: i.append(i[0].copy())),
    ]:
        args = copy.deepcopy((inputs, frames, holds))
        mutate(*args)
        try:
            verify(*args)
        except AssertionError:
            print('REFUSED:', name)
        else:
            raise AssertionError('silent pass: '+name)
    _, manifest, pages, frame = source()
    selected_pages = [p for p in pages if p['org_id'] in frame]
    for p in selected_pages:
        assert hashlib.sha256((CORPUS / (p['raw_file'] or p['text_file'])).read_bytes()).hexdigest() == p['sha256']
    expected = dict(manifest_organizations=len({r['org_id'] for r in manifest}),
                    retained_organizations=len({r['org_id'] for r in pages}), frame_organizations=len(frame),
                  frame_markets_blank=sum(not org['markets_served'] for _, org in frame.values()),
                  frame_certifications_blank=sum(not org['certifications'] for _, org in frame.values()),
                  frame_reader_pages=sum(r['org_id'] in frame and r['via']=='reader' for r in pages),
                  frame_direct_pages=sum(r['org_id'] in frame and r['via']=='direct' for r in pages),
                    frame_pages=len(selected_pages), blank_field_cells=len(holds)+len({(r['org_id'],r['field']) for r in inputs}),
                    proposed_market_values=sum(r['field']=='markets_served' for r in inputs), proposed_certification_values=sum(r['field']=='certifications' for r in inputs),
                    proposed_organizations=len({r['org_id'] for r in inputs}), held_field_cells=len(holds),
                    proposed_organization_tiers=dict(Counter(frame[oid][1]['verification_tier'] for oid in {r['org_id'] for r in inputs})),
                    data_cells_applied=len({(r['org_id'],r['field']) for r in inputs}), extra_fetches=len(json.loads((CORPUS.parent / 'pic18-markets-certs-2/certificates/fetches.json').read_text())))
    assert json.loads((HERE / 'counts.json').read_text()) == expected
    evidence = read(HERE / 'evidence_packet.csv')
    assert len(evidence) == len(inputs) and len({r['evidence_id'] for r in evidence}) == len(inputs)
    for i, (ev, r) in enumerate(zip(evidence, inputs)):
        assert ev['evidence_id'] == r['evidence_id'] == f'EVD-{370070+i:06d}'
        assert ev['record_id'] == r['org_id'] and ev['source_ref'] == r['source_url']
        assert ev['claim_detail'] == f'{r["field"]} {r["value"]}: "{r["quote"]}"'
        assert ev['tier_effect'] == r['tier_effect']
    fetches = json.loads((CORPUS.parent / 'pic18-markets-certs-2/certificates/fetches.json').read_text())
    assert max(Counter(r['org_id'] for r in fetches).values()) <= 3, 'fetch budget exceeded'
    boundary(inputs, evidence)
    print('PASS:', json.dumps(expected))


if __name__ == '__main__':
    main()
