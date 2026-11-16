"""Reconcile the complete frame, retained-page hashes, proposals and per-field holds."""
import copy
import hashlib
import json
from collections import Counter
from build import HERE, ROOT, CORPUS, FIELDS, read, source, proposals, found


def verify(inputs, frames, holds):
    _, _, pages, frame = source()
    assert len(frames) == len(frame) and {r['org_id'] for r in frames} == set(frame), 'frame yield'
    assert len({r['org_id'] for r in frames}) == len(frames), 'duplicate frame'
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']['MARKETS']['values']
    accepted = set()
    for r in inputs:
        key = (r['org_id'], r['field'], r['value'])
        assert key not in accepted, 'duplicate proposal'
        accepted.add(key)
        assert r['org_id'] in frame and r['field'] == 'markets_served'
        assert r['value'] in vocab, 'off vocabulary'
        assert not frame[r['org_id']][1][r['field']], 'nonblank target'
        p = next(p for p in pages if p['org_id'] == r['org_id'] and p['url'] == r['source_url'])
        assert r['raw_file'] == p['raw_file'] and r['text_file'] == p['text_file']
        assert r['raw_sha256'] == p['sha256'] == hashlib.sha256((CORPUS / p['raw_file']).read_bytes()).hexdigest(), 'raw hash mismatch'
        text = (CORPUS / p['text_file']).read_text()
        assert hashlib.sha256(text.encode()).hexdigest() == r['text_sha256'], 'text hash mismatch'
        assert found(text, r['quote']), 'quote absent'
        assert r['tier_effect'] == ('supports_U' if frame[r['org_id']][1]['verification_tier'] == 'U' else 'supports_A')
    blank = {(oid, f) for oid, (_, org) in frame.items() for f in FIELDS if not org[f]}
    applied = {(r['org_id'], r['field']) for r in inputs}
    held = {(r['org_id'], r['field']) for r in holds}
    assert len(holds) == len(held) and not applied & held and applied | held == blank, 'field coverage yield'
    assert all(r['settling_fact'] and r['verdict'] == 'STILL_UNCERTAIN' for r in holds)
    assert inputs == proposals(frame, pages), 'selection mismatch'


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
        assert hashlib.sha256((CORPUS / p['raw_file']).read_bytes()).hexdigest() == p['sha256']
    expected = dict(manifest_organizations=len({r['org_id'] for r in manifest}),
                    retained_organizations=len({r['org_id'] for r in pages}), frame_organizations=len(frame),
                    frame_pages=len(selected_pages), blank_field_cells=len(holds)+len({(r['org_id'],r['field']) for r in inputs}),
                    proposed_market_values=len(inputs), proposed_certification_values=0,
                    proposed_organizations=len({r['org_id'] for r in inputs}), held_field_cells=len(holds),
                    proposed_organization_tiers=dict(Counter(frame[oid][1]['verification_tier'] for oid in {r['org_id'] for r in inputs})),
                    data_cells_applied=0, extra_fetches=0)
    assert json.loads((HERE / 'counts.json').read_text()) == expected
    evidence = read(HERE / 'evidence_packet.csv')
    assert len(evidence) == len(inputs) and len({r['evidence_id'] for r in evidence}) == len(inputs)
    for i, (ev, r) in enumerate(zip(evidence, inputs)):
        assert ev['evidence_id'] == r['evidence_id'] == f'EVD-{370000+i:06d}'
        assert ev['record_id'] == r['org_id'] and ev['source_ref'] == r['source_url']
        assert ev['claim_detail'] == f'markets_served {r["value"]}: "{r["quote"]}"'
        assert ev['tier_effect'] == r['tier_effect']
    print('PASS:', json.dumps(expected))


if __name__ == '__main__':
    main()
