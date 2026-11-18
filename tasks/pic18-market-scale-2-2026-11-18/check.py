"""Recompute every published count, reconcile the frame against independent inputs, prove the check fails on injected defects."""
import copy
import csv
import json
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlparse
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B
import fetch
from build import (HERE, ROOT, MKT3, CORPUS, LIVE, SNAPSHOT, BASE, FIRST_ID, LAST_ID, FRAME, FRAME_ALL, BATCH, BATCH_SIZE, RESCREEN, F, read, found, sha, locate, proposals,
                   shards, verdict_rows, counts_for, witness_class)

# Wording each applied tag needs in its own quote, after the legal name is stripped (MKT3's map, plus the words this batch needs).
# medical_device covers implants, stents and thrombectomy systems by meaning (the canary's Theken precedent); plastics_rubber_processors covers
# the rotomolding and molders' industries (rotational molding and injection molding are plastics processes).
WORDS = {
    'aerospace_defense': r'aerospace|aviation|defen[cs]e|military|aircraft|armed forces', 'automotive_unspecified': r'automotive', 'automotive_oem': r'\boem\b|tier ?[1i]\b|original equipment', 'automotive_aftermarket': r'after ?market',
    'electronics_electrical': r'electronic|electrical', 'medical_healthcare_general': r'medical|health ?care|doctors', 'medical_device': r'medical device|implant|stent|thrombectomy|fda[- ]approved|physicians during procedures',
    'pharmaceutical_biotech': r'pharmaceutical', 'construction_building_products': r'construction|building', 'energy_oil_gas': r'oil and gas|petroleum',
    'marine': r'marine|boat', 'chemical_mining_metals_processing': r'chemical|mining|metal ?forming|metal forging', 'water_wastewater': r'wastewater', 'industrial_machinery': r'manufacturing machinery|machine manufacturers|production equipment', 'rail_transportation': r'\brail\b', 'agriculture': r'agricult|farm',
    'general_industrial': r'industrial', 'food_processing_foodservice': r'food processing|food ?service|catering', 'plastics_rubber_processors': r'plastic|rubber|rotomold|molders',
    'telecom_datacom': r'telecom', 'dental': r'dentist|dental|denture', 'toys_sporting_goods': r'toys|sporting|sports', 'lawn_garden_recreation': r'\blawn\b', 'tire_rubber_goods': r'\btire', 'appliances': r'appliance', 'consumer_goods_housewares': r'housewares|household', 'energy_renewables_battery': r'batter(y|ies)', 'rv_powersports_trailers': r'\brv\b'
}
HOLD_CLASSES = {'no_market_claim', 'scope_owner_ruling', 'no_vocab_market', 'off_vocabulary_or_ambiguous_market', 'menu_or_nav_only', 'group_or_redirect_attribution', 'list_item_only'}
READ_BASES = {'page_read', 'text_screened'}


def git_rows(path):
    return list(__import__('csv').DictReader(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True).splitlines()))


def base_orgs():
    names = subprocess.check_output(['git', 'ls-tree', '--name-only', BASE, 'data/'], cwd=ROOT, text=True).split()
    return {r['org_id']: r for f in names if re.fullmatch(r'data/organizations_[A-Za-z]+\.csv', f) for r in git_rows(f)}


def domain(u):
    return urlparse(u if '//' in u else '//' + u).netloc.lower().removeprefix('www.')


def registrable(u):
    return '.'.join(domain(u).split('.')[-2:])  # shortcut: last two labels, so co.uk-style hosts compare loosely; upgrade if a record needs it


def verify_frame(frame_all, frame):
    """The frame is recomputed from git (canary pool definition) and must equal the packet's: count, identity, batch slice, no canary overlap."""
    assert len(frame_all) == F.EXPECTED, ('frame count changed', len(frame_all))
    assert frame_all == F.frame(), 'frame differs from the pool recomputed at the frame ref'
    # independent route: the pool one commit earlier (before the canary applied 4 cells) minus the canary's 10 equals the frame
    assert [o for o in F.market_pool('15f2b154') if o not in F.CANARY] == frame_all, 'frame differs from the pre-canary pool minus the canary 10'
    assert frame == (frame_all[:BATCH_SIZE] if BATCH == 1 else frame_all[BATCH_SIZE:] + RESCREEN) and not set(frame) & set(F.CANARY), 'batch slice'
    assert len(frame) == (BATCH_SIZE if BATCH == 1 else F.EXPECTED - BATCH_SIZE + len(RESCREEN)), 'batch size'
    assert set(RESCREEN) <= set(frame_all[:BATCH_SIZE]) and len(RESCREEN) == len(set(RESCREEN)) == 5, 'rescreen organizations must be batch 1 frame organizations'
    prior = {r['org_id']: r for r in read(ROOT / 'tasks/pic18-market-scale-1-2026-11-18/verdicts.csv')}
    assert set(RESCREEN) == {o for o, r in prior.items() if r['verdict'] == 'STILL_UNCERTAIN' and r['hold_class'] == 'list_item_only'}, 'rescreen set differs from batch 1 list_item_only holds'


def verify(inputs, verdicts, frame_all=None, frame=None):
    frame_all, frame = frame_all or FRAME_ALL, frame or FRAME
    verify_frame(frame_all, frame)
    base = base_orgs()
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']['MARKETS']['values']
    # input side, independently of the verdict table: frame orgs are blank at BASE, were not_adjudicated in MKT3, and hold a stored text page >= 1 KB
    mkt3_holds = {r['org_id']: r for r in read(MKT3 / 'holds.csv')}
    pages = [r for r in read(SNAPSHOT) if r['status'] == 'ok' and r['text_file']]
    for oid in frame:
        assert not base[oid]['markets_served'], ('frame org not blank at base', oid)
        assert mkt3_holds[oid]['hold_class'] == 'not_adjudicated', ('frame org was adjudicated by MKT3', oid)
        assert any(len((CORPUS / p['text_file']).read_text()) >= 1000 for p in pages if p['org_id'] == oid), ('no stored text page of 1 KB', oid)
    ids = [v['org_id'] for v in verdicts]
    assert sorted(ids) == sorted(frame) and len(set(ids)) == len(ids) == len(frame), 'frame ID with no verdict, or two'
    retired = {r['evidence_id'] for r in read(HERE / 'withdrawn.csv')}
    assert not retired & {r['evidence_id'] for r in inputs}, 'retired evidence ID reused'
    assert all(f'EVD-{FIRST_ID:06d}' <= i <= f'EVD-{LAST_ID}' for i in retired), 'retired ID outside the block'
    base_max = max(r['evidence_id'] for n in subprocess.check_output(['git', 'ls-tree', '--name-only', BASE, 'data/'], cwd=ROOT, text=True).split()
                   if re.fullmatch(r'data/evidence_[A-Za-z_]+\.csv', n) for r in git_rows(n))
    assert min((r['evidence_id'] for r in inputs), default='EVD-999999') > base_max, ('new evidence ID not above the merge-base maximum', base_max)
    seen = set()
    for r in inputs:
        assert not (r['value'] == 'automotive_unspecified' and re.search(WORDS['automotive_oem'], r['quote'], re.I)), 'automotive_unspecified on OEM or Tier 1 wording'
        key = (r['org_id'], r['value'])
        assert key not in seen, 'duplicate proposal'
        seen.add(key)
        org = base[r['org_id']]
        assert r['org_id'] in frame and r['field'] == 'markets_served' and not org['markets_served'], 'nonblank or outside frame'
        assert not re.search(r'do not promote|carbon|graphite', ' '.join([org['legal_name'], org['notes']]), re.I), ('carbon/graphite or do-not-promote record applied', r['org_id'])
        assert r['value'] in vocab, 'off vocabulary'
        assert r['value'] in WORDS and re.search(WORDS[r['value']], re.sub(re.escape(org['legal_name']), '', r['quote'], flags=re.I), re.I), ('tag wording absent from quote', r['value'])
        raw, text, recorded = locate(r['org_id'], r['source_kind'], r['source_url'])
        assert r['raw_sha256'] == recorded == sha(raw), 'raw hash mismatch'
        page = text.read_text()
        assert sha(text) == r['text_sha256'], 'text hash mismatch'  # bytes of the stored file, not read_text() output
        assert found(page, r['quote']), 'quote absent'
        assert not witness_class.nav_only(raw.read_text(errors='replace'), r['quote']), 'nav menu witness'
        assert not witness_class.article_url(r['source_url']), 'article source witness'
        parent = base.get(org['parent_org_id'])
        assert not (parent and domain(parent['website']) == domain(r['source_url'])), 'group domain witness'
        assert registrable(r['source_url']) == registrable(org['website']), ('source domain differs from the record website', r['org_id'])
        assert r['tier_effect'] == ('supports_U' if org['verification_tier'] == 'U' else 'supports_A'), 'strength'
    applied = {r['org_id'] for r in inputs}
    for v in verdicts:
        assert v['read_basis'] in READ_BASES, 'read basis missing'
        if v['org_id'] in applied:
            assert v['verdict'] == 'VERIFIED', 'applied org not VERIFIED'
        else:
            assert v['verdict'] == 'STILL_UNCERTAIN' and v['hold_class'] in HOLD_CLASSES, 'hold without verdict class'
            assert v['settling_fact'].strip(), 'hold without settling fact'
            assert len(v['settling_fact'].split()) >= 8, 'settling fact does not name the missing claim'
    expected = {o: ';'.join(sorted(r['value'] for r in inputs if r['org_id'] == o)) for o in frame}
    for v in verdicts:
        assert v['values'] == expected[v['org_id']], ('verdict values differ from the inputs', v['org_id'])  # holds must be empty
    assert applied <= set(frame) and {v['org_id'] for v in verdicts if v['verdict'] == 'VERIFIED'} == applied, 'verdict/applied mismatch'
    assert inputs == proposals({o: base[o]['verification_tier'] for o in frame}), 'selection mismatch'


def cell_writes(before, after, values):
    """Every changed organization row differs only in a blank markets_served cell, and only for a proposed org."""
    changed = 0
    for oid, a in after.items():
        b = before[oid]
        if a == b:
            continue
        diff = {k for k in a if a[k] != b[k]}
        assert diff == {'markets_served'}, ('write outside markets_served', oid, diff)
        assert not b['markets_served'], ('write to a non-blank cell', oid)
        assert oid in values and a['markets_served'] == ';'.join(sorted(values[oid])), ('unproposed write', oid)
        changed += 1
    assert changed == len(values), 'application yield'
    return changed


def derived_evidence(inputs, tiers):
    """Every applied evidence row, rebuilt from inputs.csv and the stored page bytes (sha256 recomputed here), never from the editable evidence packet."""
    out = []
    for r in inputs:
        raw, _, _ = locate(r['org_id'], r['source_kind'], r['source_url'])
        out.append(dict(evidence_id=r['evidence_id'], record_table='organizations', record_id=r['org_id'], claim_type='activity',
                        claim_detail=f'markets_served {r["value"]}: "{r["quote"]}"', source_class='own_site', source_ref=r['source_url'],
                        observed_date='2026-11-18', tier_effect='supports_U' if tiers[r['org_id']] == 'U' else 'supports_A',
                        created_by='claude atlas-w18-mktscale', notes='Own-company source; field witness retained, SHA256 ' + sha(raw)))
    return out


def packet_matches(packet, derived):
    assert packet == derived, 'evidence packet differs from the rows derived from inputs.csv and the stored pages'


def evidence_delta(before, after, add):
    """The canonical shard is the base rows plus exactly the derived rows, every field equal (source_class, date, digest note, strength)."""
    assert not {r['evidence_id'] for r in add} & {r['evidence_id'] for r in before}, 'reused evidence ID'
    assert after == sorted(before + add, key=lambda r: r['evidence_id']), 'evidence delta mismatch (a field differs from the value derived from inputs.csv and the stored page)'


def boundary(inputs, evidence):
    values = {}
    for r in inputs:
        values.setdefault(r['org_id'], []).append(r['value'])
    before_o = base_orgs()
    after_o = {r['org_id']: r for p in shards() for r in read(p)}
    assert set(before_o) == set(after_o), 'organization rows added or removed'
    cells = cell_writes(before_o, after_o, values)
    new_evs, home = 0, {r['org_id']: p.name for p in shards() for r in read(p)}
    for p in sorted((ROOT / 'data').glob('*.csv')):
        if p.name.endswith('_all.csv') or p.name.startswith('organizations_'):
            continue
        before, after = git_rows(f'data/{p.name}'), read(p)
        if p.name.startswith('evidence_organizations_'):
            add = [r for r in evidence if home[r['record_id']].replace('organizations_', 'evidence_organizations_') == p.name]
            evidence_delta(before, after, add)
            new_evs += len(add)
        else:
            assert before == after, ('out of scope data change', p.name)
    assert new_evs == len(evidence), 'evidence yield'
    print('BOUNDARY PASS:', cells, 'market cells;', new_evs, 'new evidence rows; all other data unchanged')


def builder_tests(inputs, evidence):
    """Interrupted write, occupied evidence ID, and scrub replay, on temporary copies only."""
    home = {r['org_id']: p.name for p in shards() for r in read(p)}
    org_shards = sorted({home[r['org_id']] for r in inputs})
    names = tuple(org_shards + [n.replace('organizations_', 'evidence_organizations_') for n in org_shards])
    assert 'organizations_OH.csv' in names, 'the truncation test below needs the OH shard in the packet'
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / 'data').mkdir()

        def reset(preoccupy=None):
            for n in names:
                (root / 'data' / n).write_bytes(subprocess.check_output(['git', 'show', f'{BASE}:data/{n}'], cwd=ROOT))
            if preoccupy:
                p = root / 'data/evidence_organizations_OH.csv'
                rows = read(p)
                rows.append(dict(rows[0], evidence_id=preoccupy, record_id='ORG-999999'))
                with p.open('w', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
                    w.writeheader()
                    w.writerows(sorted(rows, key=lambda r: r['evidence_id']))

        def snapshot():
            return {n: (root / 'data' / n).read_bytes() for n in names}
        with patch.object(B, 'ROOT', root), patch.object(B, 'LIVE', root / 'backup'):
            reset()
            before, original = snapshot(), csv.DictWriter.writerows

            def cut(writer, rows):
                original(writer, list(rows)[:100])
                raise OSError('interrupted')
            try:
                with patch.object(csv.DictWriter, 'writerows', cut):
                    B.apply(inputs, evidence)
            except OSError:
                pass
            else:
                raise AssertionError('silent pass: interrupted write')
            assert snapshot() == before, 'interrupted write damaged a shard'
            B.apply(inputs, evidence)  # retry succeeds from the intact state
            B.apply(inputs, evidence)  # replay is a no-op
            assert all(not (root / 'data' / n).with_name(n + '.tmp').exists() for n in names), 'temp sibling left behind'
            print('REFUSED: interrupted write leaves shards intact; retry and replay succeed')
            reset()
            B.apply(inputs, evidence)
            final = snapshot()
            by_org = {}
            for e in evidence:
                by_org.setdefault(e['record_id'], set()).add(e['evidence_id'])
            real_replace = B.os.replace
            for k in range(1, len(names) + 1):  # interrupt at every canonical replacement: no cell may be published without its evidence rows
                reset()
                calls = []

                def cut_replace(src, dst, _k=k):
                    calls.append(dst)
                    if len(calls) == _k:
                        raise OSError('interrupted between replacements')
                    return real_replace(src, dst)
                try:
                    with patch.object(B.os, 'replace', cut_replace):
                        B.apply(inputs, evidence)
                except OSError:
                    pass
                else:
                    raise AssertionError('silent pass: interruption at replacement %d' % k)
                have = {r['evidence_id'] for n in names if n.startswith('evidence_') for r in read(root / 'data' / n)}
                for n in names:
                    if n.startswith('organizations_'):
                        for r in read(root / 'data' / n):
                            if r['org_id'] in by_org and r['markets_served']:
                                assert by_org[r['org_id']] <= have, ('a market cell was published without its evidence rows', r['org_id'], k)
                B.apply(inputs, evidence)  # retry
                assert snapshot() == final, 'retry after an interruption did not reproduce the canonical shards'
            print('REFUSED: interruption between canonical replacements (every position): no cell without its evidence rows; retry reproduces the shards')
            reset(preoccupy=evidence[0]['evidence_id'])
            before = snapshot()
            try:
                B.apply(inputs, evidence)
            except AssertionError as e:
                assert 'occupied' in str(e), str(e)
            else:
                raise AssertionError('silent pass: occupied evidence ID')
            assert snapshot() == before, 'a market cell was written despite an occupied ID'
            print('REFUSED: occupied evidence ID (no market cell written)')
            for n in ('organizations_OH.csv', 'evidence_organizations_OH.csv'):  # truncated input shard: one row removed
                reset()
                p = root / 'data' / n
                lines = p.read_bytes().split(b'\n')
                p.write_bytes(b'\n'.join(lines[:5] + lines[6:]))  # drop one data row (the 4th)
                before = snapshot()
                try:
                    B.apply(inputs, evidence)
                except AssertionError as e:
                    assert 'differs from base' in str(e), str(e)
                else:
                    raise AssertionError('silent pass: truncated ' + n)
                assert snapshot() == before, 'a shard changed despite a truncated input'
            print('REFUSED: truncated input shard (organization and evidence), nothing replaced')
    with tempfile.TemporaryDirectory() as td:  # scrub: purge then a lookup must refetch, not raise
        c = fetch.Corpus(td)
        url = 'https://example.test/page'
        r = c.save(url, dict(raw=b'<html><body>Sales: jane.doe@example.test a long enough page body about nothing in particular</body></html>',
                             code=200, content_type='text/html', exit=0), 'ok', url, 'direct')
        assert fetch.scrub(c, r, url), 'scrub missed a personal address'
        assert c.cached(url) is None and not any(row['url'] == url for row in csv.DictReader((Path(td) / 'index.csv').open())), 'scrub left a record behind'
        print('REFUSED: scrub leaves no per-URL record or index row')


def main():
    packet_only = '--packet-only' in sys.argv  # data/ not yet written: skip the boundary and application-state checks, loudly
    inputs, verdicts = read(HERE / 'inputs.csv'), read(HERE / 'verdicts.csv')
    verify(inputs, verdicts)
    first = inputs[0]['org_id']
    held = lambda v: next(x for x in v if x['verdict'] == 'STILL_UNCERTAIN')
    cases = [
        ('term not in the vocabulary', 'off vocabulary', lambda i, v: i[0].update(value='consumer_goods')),
        ('quote not found in its stored page', 'quote absent', lambda i, v: i[0].update(quote=i[0]['quote'] + ' fabricated violet elephant')),
        ('frame ID with no verdict', 'frame ID with no verdict', lambda i, v: v.pop()),
        ('frame ID with two verdicts', 'frame ID with no verdict, or two', lambda i, v: v.append(copy.deepcopy(v[0]))),
        ('hold with a blank settling fact', 'hold without settling fact', lambda i, v: held(v).update(settling_fact=' ')),
        ('tag broader than the words', 'tag wording', lambda i, v: i[0].update(value='aerospace_defense' if i[0]['value'] != 'aerospace_defense' else 'marine')),
        ('raw hash tampering', 'raw hash mismatch', lambda i, v: i[0].update(raw_sha256='0' * 64)),
        ('duplicate proposal', 'duplicate proposal', lambda i, v: i.append(i[0].copy())),
        ('text digest of the wrong bytes', 'text hash mismatch', lambda i, v: i[0].update(text_sha256='f' * 64)),
        ('tampered verdict value', 'verdict values differ', lambda i, v: next(x for x in v if x['org_id'] == first).update(values='aerospace_defense;marine')),
        ('value on a hold', 'verdict values differ', lambda i, v: held(v).update(values='aerospace_defense')),
        ('automotive_unspecified on OEM wording', 'automotive_unspecified on OEM', lambda i, v: next(x for x in i if re.search(WORDS['automotive_oem'], x['quote'], re.I)).update(value='automotive_unspecified')),
        ('new evidence ID not above the merge-base maximum', 'not above the merge-base maximum', lambda i, v: i[0].update(evidence_id='EVD-000001')),
        ('read basis missing', 'read basis missing', lambda i, v: v[0].update(read_basis='')),
        ('wrong tier effect for the record tier', 'strength', lambda i, v: i[0].update(tier_effect='supports_C' if i[0]['tier_effect'] == 'supports_A' else 'supports_A')),
    ]
    if read(HERE / 'withdrawn.csv'):
        cases.append(('retired evidence ID reused', 'retired evidence ID reused', lambda i, v: i[0].update(evidence_id=read(HERE / 'withdrawn.csv')[0]['evidence_id'])))
    for name, expect, mutate in cases:
        args = copy.deepcopy((inputs, verdicts))
        mutate(*args)
        try:
            verify(*args)
        except AssertionError as e:
            assert expect in str(e), ('refused for the wrong reason', name, str(e))
            print('REFUSED:', name)
        else:
            raise AssertionError('silent pass: ' + name)
    frame_cases = [  # frame-level injections: the recomputed pool and the packet frame must agree
        ('frame count change (one organization added)', 'frame count changed', lambda a: a + ['ORG-999999']),
        ('frame count change (one organization dropped)', 'frame count changed', lambda a: a[:-1]),
        ('frame order or identity change', 'frame differs from the pool', lambda a: a[:5] + [a[6], a[5]] + a[7:]),
    ]
    for name, expect, mutate in frame_cases:
        try:
            verify(inputs, verdicts, frame_all=mutate(list(FRAME_ALL)), frame=FRAME)
        except AssertionError as e:
            assert expect in str(e), ('refused for the wrong reason', name, str(e))
            print('REFUSED:', name)
        else:
            raise AssertionError('silent pass: ' + name)
    sub = ['ORG-000036' if x == 'ORG-000229' else x for x in RESCREEN]
    verdicts_sub = copy.deepcopy(verdicts)
    next(r for r in verdicts_sub if r['org_id'] == 'ORG-000229')['org_id'] = 'ORG-000036'
    with patch(__name__ + '.RESCREEN', sub):
        try:
            verify(inputs, verdicts_sub, frame=FRAME_ALL[96:] + sub)
        except AssertionError as e:
            assert 'rescreen set differs' in str(e), str(e)
            print('REFUSED: re-screen substitution (a batch-1 hold of another class in place of a list_item_only hold)')
        else:
            raise AssertionError('silent pass: re-screen substitution')
    base = base_orgs()
    attribution = [  # records patched in memory: a parent on the source domain; a different record website; a carbon or do-not-promote note
        ('group domain witness', 'group domain witness', lambda b, o: b[o].update(parent_org_id='ORG-PARENT') or b.update({'ORG-PARENT': dict(b[o], website=b[o]['website'])})),
        ('source domain differs from the record website', 'source domain differs', lambda b, o: b[o].update(website='https://unrelated-example.test/')),
        ('do-not-promote note on an applied record', 'do-not-promote', lambda b, o: b[o].update(notes=b[o]['notes'] + ' Do not promote.')),
        ('carbon or graphite record applied', 'do-not-promote', lambda b, o: b[o].update(legal_name='Example Graphite Corp')),
    ]
    for name, expect, mutate in attribution:
        patched = copy.deepcopy(base)
        mutate(patched, first)
        with patch(__name__ + '.base_orgs', lambda: patched):
            try:
                verify(inputs, verdicts)
            except AssertionError as e:
                assert expect in str(e), ('refused for the wrong reason', name, str(e))
                print('REFUSED:', name)
            else:
                raise AssertionError('silent pass: ' + name)
    builder_tests(inputs, read(HERE / 'evidence_packet.csv'))
    if packet_only:
        cells = {r['org_id']: r['markets_served'] for p in shards() for r in read(p)}
        assert not any(cells[o] for o in {r['org_id'] for r in inputs}), 'packet-only mode but a frame cell is already written: run check.py without --packet-only'
        print('PACKET ONLY: data/ is not written; boundary and counts-after-application checks were skipped')
    # a write to a non-blank cell, and a write to any other column, on the real organization rows
    values = {}
    for r in inputs:
        values.setdefault(r['org_id'], []).append(r['value'])
    before, after = base_orgs(), {r['org_id']: r for p in shards() for r in read(p)}
    for name, expect, mutate in [('write to a non-blank cell', 'non-blank cell', lambda b, a: b[next(iter(values))].update(markets_served='aerospace_defense')),
                                 ('write to another column', 'outside markets_served', lambda b, a: a[next(iter(values))].update(notes='edited'))]:
        b, a = copy.deepcopy(before), copy.deepcopy(after)
        mutate(b, a)
        try:
            cell_writes(b, a, values)
        except AssertionError as e:
            assert expect in str(e), ('refused for the wrong reason', name, str(e))
            print('REFUSED:', name)
        else:
            raise AssertionError('silent pass: ' + name)
    tiers = {o: base[o]['verification_tier'] for o in base}
    expected = counts_for(tiers, inputs, verdict_rows(inputs))
    assert json.loads((HERE / 'counts.json').read_text()) == expected, 'counts.json stale'
    evidence = derived_evidence(inputs, tiers)
    packet_matches(read(HERE / 'evidence_packet.csv'), evidence)
    assert len(evidence) == expected['applied_values']
    assert all(f'EVD-{FIRST_ID:06d}' <= e['evidence_id'] <= f'EVD-{LAST_ID}' for e in evidence), 'evidence ID outside block'
    # falsified provenance, in the packet and in the canonical shard, must both be refused
    home_shard = {r['org_id']: p.name for p in shards() for r in read(p)}
    first_shard = home_shard[inputs[0]['org_id']].replace('organizations_', 'evidence_organizations_')
    base_ev = git_rows(f'data/{first_shard}')
    mine = [e for e in evidence if home_shard[e['record_id']].replace('organizations_', 'evidence_organizations_') == first_shard]
    good = sorted(base_ev + mine, key=lambda r: r['evidence_id'])
    evidence_delta(base_ev, good, mine)
    for field, bad in [('source_class', 'government_filing'), ('observed_date', '2020-01-01'), ('notes', 'unsupported digest'), ('tier_effect', 'supports_C')]:
        forged = copy.deepcopy(good)
        next(r for r in forged if r['evidence_id'] == mine[0]['evidence_id'])[field] = bad
        try:
            evidence_delta(base_ev, forged, mine)
        except AssertionError as e:
            assert 'evidence delta mismatch' in str(e), str(e)
            print('REFUSED: falsified', field, 'in the canonical evidence shard')
        else:
            raise AssertionError('silent pass: falsified ' + field)
    forged_packet = copy.deepcopy(evidence)
    forged_packet[0]['source_class'] = 'government_filing'
    try:
        packet_matches(forged_packet, evidence)
    except AssertionError as e:
        assert 'evidence packet differs' in str(e), str(e)
        print('REFUSED: falsified source_class in the evidence packet (packet must equal the derived rows)')
    else:
        raise AssertionError('silent pass: falsified packet')
    if not packet_only:
        boundary(inputs, evidence)
    print('PASS:', json.dumps(expected))


if __name__ == '__main__':
    main()
