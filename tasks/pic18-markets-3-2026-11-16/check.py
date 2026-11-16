"""Recompute every published count, reconcile yield against an independent count, prove the check fails on injected defects."""
import copy
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from build import (HERE, ROOT, CORPUS, SNAPSHOT, BASE, FIRST_ID, read, source, proposals, found, at_base, counts_for)

# Wording each controlled tag needs in its own quote (refuted before: broader/different tag than the words).
WORDS = {
    'aerospace_defense': r'aerospace|aviation|defen[cs]e|military|aircraft|air frame|jet engine', 'automotive_unspecified': r'automotive|heavy trucking',
    'automotive_aftermarket': r'after ?market', 'appliances': r'appliance', 'electronics_electrical': r'electronic|electrical',
    'medical_healthcare_general': r'medical|healthcare', 'medical_device': r'medical device|medical equipment|fda-cleared device',
    'pharmaceutical_biotech': r'pharmaceutical|biologics', 'construction_building_products': r'construction|building|window|concrete',
    'infrastructure_civil': r'infrastructure', 'energy_oil_gas': r'oil|gas|petroleum', 'energy_renewables_battery': r'battery',
    'marine': r'marine|boat', 'chemical_mining_metals_processing': r'chemical|mining', 'rail_transportation': r'rail',
    'agriculture': r'agricult|farm', 'general_industrial': r'industrial|general industry', 'water_wastewater': r'water',
    'food_processing_foodservice': r'food processing', 'packaging_food_beverage': r'food and protective packaging',
    'packaging_industrial': r'bags for industrial use', 'plastics_rubber_processors': r'plastic|rubber', 'tire_rubber_goods': r'tire',
    'telecom_datacom': r'telecom', 'rv_powersports_trailers': r'\brv\b', 'consumer_goods_housewares': r'housewares|household',
    'toys_sporting_goods': r'toys|sporting|sports', 'footwear_apparel': r'apparel', 'industrial_machinery': r'industrial machinery',
    'lawn_garden_recreation': r'lawn',
}


def independent_frame():
    """Frame count by a separate route: ok pages in the pinned manifest x blank markets cells at BASE, minus prior lanes."""
    ok = {r['org_id'] for r in csv.DictReader(open(SNAPSHOT)) if r['status'] == 'ok' and r['text_file']}
    prior = {r['org_id'] for r in csv.DictReader(open(HERE / 'prior_lanes.csv'))}
    n = 0
    for f in subprocess.check_output(['git', 'ls-tree', '--name-only', BASE, 'data/'], cwd=ROOT, text=True).split():
        if re.fullmatch(r'data/organizations_[A-Z]+\.csv', f):
            for r in csv.DictReader(subprocess.check_output(['git', 'show', f'{BASE}:{f}'], cwd=ROOT, text=True).splitlines()):
                n += r['org_id'] in ok and not r['markets_served'] and r['org_id'] not in prior
    return n


def verify(inputs, frames, holds):
    _, _, pages, frame, _ = source()
    assert len(frames) == len(frame) == independent_frame() and {r['org_id'] for r in frames} == set(frame), 'frame yield vs independent count'
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']['MARKETS']['values']
    seen = set()
    for r in inputs:
        key = (r['org_id'], r['value'])
        assert key not in seen, 'duplicate proposal'
        seen.add(key)
        assert r['org_id'] in frame and r['field'] == 'markets_served' and not frame[r['org_id']][1]['markets_served'], 'nonblank or outside frame'
        assert r['value'] in vocab, 'off vocabulary'
        assert re.search(WORDS[r['value']], r['quote'], re.I), ('tag wording absent from quote', r['value'])
        p = next(p for p in pages if p['org_id'] == r['org_id'] and p['url'] == r['source_url'])
        assert r['raw_sha256'] == p['sha256'] == hashlib.sha256((CORPUS / (p['raw_file'] or p['text_file'])).read_bytes()).hexdigest(), 'raw hash mismatch'
        text = (CORPUS / p['text_file']).read_text()
        assert hashlib.sha256(text.encode()).hexdigest() == r['text_sha256'], 'text hash mismatch'
        assert found(text, r['quote']), 'quote absent'
        assert r['tier_effect'] == ('supports_U' if frame[r['org_id']][1]['verification_tier'] == 'U' else 'supports_A')
    applied = {r['org_id'] for r in inputs}
    held = [r['org_id'] for r in holds]
    assert len(held) == len(set(held)) and not applied & set(held) and applied | set(held) == set(frame), 'disposition coverage'
    assert all(r['settling_fact'] and r['verdict'] == 'STILL_UNCERTAIN' for r in holds)
    assert inputs == proposals(frame, pages), 'selection mismatch'


def boundary(inputs, evidence):
    homes = source()[0]
    values = {}
    for r in inputs:
        values.setdefault(r['org_id'], set()).add(r['value'])
    cells = new_evs = 0
    for p in sorted((ROOT / 'data').glob('*.csv')):
        if p.name.endswith('_all.csv'):
            continue
        before, after = at_base(p), read(p)
        if p.name.startswith('organizations_'):
            expected = copy.deepcopy(before)
            for r in expected:
                if r['org_id'] in values:
                    assert not r['markets_served']
                    r['markets_served'] = ';'.join(sorted(values[r['org_id']]))
                    cells += 1
            assert after == expected, ('unrelated organization change', p.name)
        elif p.name.startswith('evidence_organizations_'):
            append = [r for r in evidence if homes[r['record_id']][0] == p.name.replace('evidence_organizations_', 'organizations_')]
            assert not {r['evidence_id'] for r in evidence} & {r['evidence_id'] for r in before}, 'reused evidence ID'
            assert after == sorted(before + append, key=lambda r: r['evidence_id']), ('evidence delta mismatch', p.name)
            new_evs += len(append)
        else:
            assert before == after, ('out of scope data change', p.name)
    assert cells == len(values) and new_evs == len(evidence), 'application yield'
    print('BOUNDARY PASS:', cells, 'market cells;', new_evs, 'new evidence rows; all other data unchanged')


def main():
    inputs, frames, holds = [read(HERE / f) for f in ('inputs.csv', 'frame.csv', 'holds.csv')]
    verify(inputs, frames, holds)
    for name, mutate in [
        ('fabricated quote', lambda i, f, h: i[0].update(quote='fabricated violet elephant market')),
        ('off vocabulary', lambda i, f, h: i[0].update(value='consumer_goods')),
        ('broader tag than the words', lambda i, f, h: i[0].update(value='consumer_goods_housewares')),
        ('missing disposition', lambda i, f, h: h.pop()),
        ('raw hash tampering', lambda i, f, h: i[0].update(raw_sha256='0' * 64)),
        ('duplicate proposal', lambda i, f, h: i.append(i[0].copy())),
        ('dropped frame row', lambda i, f, h: f.pop()),
    ]:
        args = copy.deepcopy((inputs, frames, holds))
        mutate(*args)
        try:
            verify(*args)
        except AssertionError:
            print('REFUSED:', name)
        else:
            raise AssertionError('silent pass: ' + name)
    _, manifest, pages, frame, prior = source()
    expected = counts_for(manifest, pages, frame, inputs, holds, prior)
    assert json.loads((HERE / 'counts.json').read_text()) == expected, 'counts.json stale'
    evidence = read(HERE / 'evidence_packet.csv')
    assert len(evidence) == len(inputs) == expected['proposed_values']
    for i, (ev, r) in enumerate(zip(evidence, inputs)):
        assert ev['evidence_id'] == r['evidence_id'] == f'EVD-{FIRST_ID + i:06d}' and FIRST_ID + i <= 390999
        assert ev['record_id'] == r['org_id'] and ev['source_ref'] == r['source_url'] and ev['tier_effect'] == r['tier_effect']
        assert ev['claim_detail'] == f'markets_served {r["value"]}: "{r["quote"]}"'
    boundary(inputs, evidence)
    print('PASS:', json.dumps(expected))


if __name__ == '__main__':
    main()
