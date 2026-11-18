"""Recompute every published count, reconcile the frame against independent inputs, prove the check fails on injected defects."""
import copy
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import (HERE, ROOT, MKT3, CORPUS, LIVE, SNAPSHOT, BASE, FIRST_ID, LAST_ID, FRAME, read, found, sha, locate, proposals, shards,
                   verdict_rows, counts_for, witness_class)

# Wording each applied tag needs in its own quote, after the legal name is stripped. medical_device adds "implant": the owner-vocabulary
# term covers implantable devices by meaning, and no other registered term fits a maker of joint implants (README "Term table").
WORDS = {'medical_device': r'medical device|medical equipment|fda-cleared device|implant', 'automotive_oem': r'car makers|vehicle makers|\boem',
         'plastics_rubber_processors': r'plastic|rubber', 'chemical_mining_metals_processing': r'chemical|mining'}
HOLD_CLASSES = {'no_market_claim', 'scope_owner_ruling', 'no_vocab_market', 'off_vocabulary_or_ambiguous_market', 'menu_or_nav_only', 'group_or_redirect_attribution'}


def git_rows(path):
    return list(__import__('csv').DictReader(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True).splitlines()))


def base_orgs():
    names = subprocess.check_output(['git', 'ls-tree', '--name-only', BASE, 'data/'], cwd=ROOT, text=True).split()
    return {r['org_id']: r for f in names if re.fullmatch(r'data/organizations_[A-Za-z]+\.csv', f) for r in git_rows(f)}


def verify(inputs, verdicts):
    base = base_orgs()
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']['MARKETS']['values']
    # input side, independently of the verdict table: frame orgs are blank at BASE, were not_adjudicated in MKT3, and hold a stored text page >= 1 KB
    mkt3_holds = {r['org_id']: r for r in read(MKT3 / 'holds.csv')}
    pages = [r for r in read(SNAPSHOT) if r['status'] == 'ok' and r['text_file']]
    for oid in FRAME:
        assert not base[oid]['markets_served'], ('frame org not blank at base', oid)
        assert mkt3_holds[oid]['hold_class'] == 'not_adjudicated', ('frame org was adjudicated by MKT3', oid)
        assert any(len((CORPUS / p['text_file']).read_text()) >= 1000 for p in pages if p['org_id'] == oid), ('no stored text page of 1 KB', oid)
    ids = [v['org_id'] for v in verdicts]
    assert sorted(ids) == sorted(FRAME) and len(set(ids)) == len(ids) == 10, 'frame ID with no verdict, or two'
    seen = set()
    for r in inputs:
        key = (r['org_id'], r['value'])
        assert key not in seen, 'duplicate proposal'
        seen.add(key)
        org = base[r['org_id']]
        assert r['org_id'] in FRAME and r['field'] == 'markets_served' and not org['markets_served'], 'nonblank or outside frame'
        assert r['value'] in vocab, 'off vocabulary'
        assert r['value'] in WORDS and re.search(WORDS[r['value']], re.sub(re.escape(org['legal_name']), '', r['quote'], flags=re.I), re.I), ('tag wording absent from quote', r['value'])
        raw, text, recorded = locate(r['org_id'], r['source_kind'], r['source_url'])
        assert r['raw_sha256'] == recorded == sha(raw), 'raw hash mismatch'
        page = text.read_text()
        assert __import__('hashlib').sha256(page.encode()).hexdigest() == r['text_sha256'], 'text hash mismatch'
        assert found(page, r['quote']), 'quote absent'
        assert not witness_class.nav_only(raw.read_text(errors='replace'), r['quote']), 'nav menu witness'
        assert not witness_class.article_url(r['source_url']), 'article source witness'
        assert r['tier_effect'] == 'supports_A', 'strength'
    applied = {r['org_id'] for r in inputs}
    for v in verdicts:
        if v['org_id'] in applied:
            assert v['verdict'] == 'VERIFIED', 'applied org not VERIFIED'
        else:
            assert v['verdict'] == 'STILL_UNCERTAIN' and v['hold_class'] in HOLD_CLASSES, 'hold without verdict class'
            assert v['settling_fact'].strip(), 'hold without settling fact'
            assert len(v['settling_fact'].split()) >= 8, 'settling fact does not name the missing claim'
    assert applied <= set(FRAME) and {v['org_id'] for v in verdicts if v['verdict'] == 'VERIFIED'} == applied, 'verdict/applied mismatch'
    assert inputs == proposals(None), 'selection mismatch'


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
            assert not {r['evidence_id'] for r in evidence} & {r['evidence_id'] for r in before}, 'reused evidence ID'
            assert after == sorted(before + add, key=lambda r: r['evidence_id']), ('evidence delta mismatch', p.name)
            new_evs += len(add)
        else:
            assert before == after, ('out of scope data change', p.name)
    assert new_evs == len(evidence), 'evidence yield'
    print('BOUNDARY PASS:', cells, 'market cells;', new_evs, 'new evidence rows; all other data unchanged')


def main():
    inputs, verdicts = read(HERE / 'inputs.csv'), read(HERE / 'verdicts.csv')
    verify(inputs, verdicts)
    cases = [
        ('term not in the vocabulary', 'off vocabulary', lambda i, v: i[0].update(value='consumer_goods')),
        ('quote not found in its stored page', 'quote absent', lambda i, v: i[0].update(quote=i[0]['quote'] + ' fabricated violet elephant')),
        ('frame ID with no verdict', 'frame ID with no verdict', lambda i, v: v.pop()),
        ('frame ID with two verdicts', 'frame ID with no verdict, or two', lambda i, v: v.append(copy.deepcopy(v[0]))),
        ('hold with a blank settling fact', 'hold without settling fact', lambda i, v: next(x for x in v if x['verdict'] == 'STILL_UNCERTAIN').update(settling_fact=' ')),
        ('tag broader than the words', 'tag wording', lambda i, v: i[0].update(value='plastics_rubber_processors') if i[0]['value'] != 'plastics_rubber_processors' else i[0].update(value='medical_device')),
        ('raw hash tampering', 'raw hash mismatch', lambda i, v: i[0].update(raw_sha256='0' * 64)),
        ('duplicate proposal', 'duplicate proposal', lambda i, v: i.append(i[0].copy())),
    ]
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
    base = base_orgs()
    expected = counts_for({o: (None, base[o]) for o in base}, inputs, verdict_rows(inputs))
    assert json.loads((HERE / 'counts.json').read_text()) == expected, 'counts.json stale'
    evidence = read(HERE / 'evidence_packet.csv')
    assert [e['evidence_id'] for e in evidence] == [r['evidence_id'] for r in inputs] and len(evidence) == expected['applied_values']
    assert all(f'EVD-{FIRST_ID:06d}' <= e['evidence_id'] <= f'EVD-{LAST_ID}' for e in evidence), 'evidence ID outside block'
    for ev, r in zip(evidence, inputs):
        assert ev['record_id'] == r['org_id'] and ev['source_ref'] == r['source_url'] and ev['tier_effect'] == r['tier_effect']
        assert ev['claim_detail'] == f'markets_served {r["value"]}: "{r["quote"]}"'
    boundary(inputs, evidence)
    print('PASS:', json.dumps(expected))


if __name__ == '__main__':
    main()
