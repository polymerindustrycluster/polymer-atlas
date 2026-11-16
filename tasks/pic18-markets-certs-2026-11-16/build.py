"""Build a packet only; the controller is the sole canonical-data integrator."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORPUS = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-corpus-2026-11-16')
FIELDS = ('markets_served', 'certifications')


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


def source():
    orgs = {r['org_id']: (p.name, r) for p in sorted((ROOT / 'data').glob('organizations_*.csv'))
            if p.stem != 'organizations_all' for r in read(p)}
    manifest = read(CORPUS / 'manifest.csv')
    pages = [r for r in manifest if r['status'] == 'ok' and r['text_file'] and r['raw_file']]
    frame = {oid: orgs[oid] for oid in sorted({r['org_id'] for r in pages})
             if any(not orgs[oid][1][f] for f in FIELDS)}
    return orgs, manifest, pages, frame


def proposals(frame, pages):
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']['MARKETS']['values']
    result = []
    for line in (HERE / 'selection.tsv').read_text().splitlines():
        oid, tags, url, quote = line.split('\t')
        assert oid in frame and not frame[oid][1]['markets_served'], 'outside blank-field frame'
        page = next(r for r in pages if r['org_id'] == oid and r['url'] == url)
        raw = CORPUS / page['raw_file']
        assert hashlib.sha256(raw.read_bytes()).hexdigest() == page['sha256'], 'raw hash mismatch'
        text = (CORPUS / page['text_file']).read_text()
        assert found(text, quote), ('quote absent', oid, quote)
        for value in tags.split(';'):
            assert value in vocab, 'off vocabulary'
            result.append(dict(org_id=oid, field='markets_served', value=value, verdict='VERIFIED',
                               applied='held_for_integration', source_url=url, quote=quote,
                               raw_sha256=page['sha256'], text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                               raw_file=page['raw_file'], text_file=page['text_file'],
                               tier_effect='supports_U' if frame[oid][1]['verification_tier'] == 'U' else 'supports_A'))
    assert len({(r['org_id'], r['field'], r['value']) for r in result}) == len(result), 'duplicate proposal'
    assert len(result) <= 3000
    for i, r in enumerate(result):
        r['evidence_id'] = f'EVD-{370000+i:06d}'
    return result


def main():
    orgs, manifest, pages, frame = source()
    inputs = proposals(frame, pages)
    frame_rows, holds = [], []
    for oid, (shard, org) in frame.items():
        own_pages = [p for p in pages if p['org_id'] == oid]
        texts = [(p, ' '.join((CORPUS / p['text_file']).read_text().split())) for p in own_pages]
        frame_rows.append(dict(org_id=oid, legal_name=org['legal_name'], shard=shard,
                               tier=org['verification_tier'], markets_blank=int(not org['markets_served']),
                               certifications_blank=int(not org['certifications']), retained_pages=len(own_pages)))
        for field in FIELDS:
            if org[field]:
                continue
            if any(r['org_id'] == oid and r['field'] == field for r in inputs):
                continue
            pattern = r'ISO\s*\d+|IATF|AS9100|certifi' if field == 'certifications' else r'market|industr|application'
            signal = next(((p, m.group()) for p, t in texts if (m := re.search(pattern, t, re.I))), None)
            settling = ('Current certificate naming standard/edition, issuer or number, exact entity/site scope and unexpired validity.'
                        if field == 'certifications' else
                        'Exact-entity own-product narrative naming a MARKETS vocabulary market; category/menu labels alone do not establish A-strength scope.')
            holds.append(dict(org_id=oid, field=field, verdict='STILL_UNCERTAIN', applied='held',
                              hold_class='certificate_identity_currency_scope' if field == 'certifications' else 'scope_attribution_or_vocabulary',
                              settling_fact=settling, signal='mention_present' if signal else 'no_screening_term',
                              source_url=signal[0]['url'] if signal else own_pages[0]['url']))
    write('frame.csv', frame_rows)
    write('inputs.csv', inputs)
    write('holds.csv', holds)
    evidence = [dict(evidence_id=r['evidence_id'], record_table='organizations', record_id=r['org_id'],
                     claim_type='activity', claim_detail=f'markets_served {r["value"]}: "{r["quote"]}"',
                     source_class='own_site', source_ref=r['source_url'], observed_date='2026-11-16',
                     tier_effect=r['tier_effect'], created_by='codex atlas-w16-markets-certs',
                     notes='Corporate own-product market claim; retained source SHA256 '+r['raw_sha256']) for r in inputs]
    write('evidence_packet.csv', evidence)
    counts = dict(manifest_organizations=len({r['org_id'] for r in manifest}), retained_organizations=len({r['org_id'] for r in pages}),
                  frame_organizations=len(frame), frame_pages=sum(int(r['retained_pages']) for r in frame_rows),
                  blank_field_cells=sum(int(r['markets_blank'])+int(r['certifications_blank']) for r in frame_rows),
                  proposed_market_values=len(inputs), proposed_certification_values=0,
                  proposed_organizations=len({r['org_id'] for r in inputs}), held_field_cells=len(holds),
                  proposed_organization_tiers=dict(Counter(frame[oid][1]['verification_tier'] for oid in {r['org_id'] for r in inputs})),
                  data_cells_applied=0, extra_fetches=0)
    (HERE / 'counts.json').write_text(json.dumps(counts, indent=2, sort_keys=True)+'\n')
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
