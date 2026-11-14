"""Named check for blind audit 10 phase 1: frame reproduces from git and reconciles, sample re-draws, blind inputs are
identical, frozen, and leak-free, and the leak scan / derivation catch planted defects.
Run from anywhere: python3 tasks/blind-audit-10-2026-11-14/check.py   (needs full git history: CI validate uses fetch-depth 0)
"""
import csv, hashlib, json, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import frame as F
import sample as S

H = F.H
sha = lambda p: hashlib.sha256((H / p).read_bytes()).hexdigest()
read = lambda p: list(csv.DictReader((H / p).open(newline='')))

# Published counts from the merged PR titles (AGENTS section 2 rule 10c). Only counts a title states outright.
PUBLISHED_CREATED = {(259, 'people_identifiers'): 804, (263, 'people_identifiers'): 11, (284, 'programs'): 1, (284, 'people'): 1, (288, 'programs'): 3,
                     (289, 'people'): 5, (290, 'people'): 4, (291, 'people'): 1, (293, 'programs'): 6, (295, 'programs'): 1, (297, 'people'): 11,
                     (297, 'ecosystem'): 2, (298, 'programs'): 5, (299, 'programs'): 11, (299, 'ecosystem'): 3, (300, 'programs'): 8,
                     (301, 'programs'): 3, (301, 'ecosystem'): 1, (302, 'people'): 5, (303, 'people'): 9, (303, 'programs'): 1, (304, 'people'): 2,
                     (304, 'programs'): 1, (306, 'people'): 8, (306, 'programs'): 2, (310, 'people'): 5, (310, 'programs'): 1, (316, 'people'): 1,
                     (323, 'people'): 4, (323, 'programs'): 1, (325, 'people'): 1, (327, 'people'): 4, (328, 'people'): 2, (328, 'programs'): 1}
PUBLISHED_DELETED = {(260, 'people'): 1, (264, 'people'): 1, (265, 'people'): 1, (283, 'people'): 1}


def check_frame():
    frame, prov = F.derive()
    assert read('frame.csv') == frame, 'frame.csv != git derivation'
    assert json.loads((H / 'frame_provenance.json').read_text()) == json.loads(json.dumps(prov)), 'provenance != git derivation'
    per = {(r['pr'], r['table'], r['kind']): r['records'] for r in prov['per_pr_per_table']}
    for (pr, t), n in PUBLISHED_CREATED.items():
        assert per.get((pr, t, 'created')) == n, f'PR #{pr} {t}: title says {n} created, git says {per.get((pr, t, "created"))}'
    for (pr, t), n in PUBLISHED_DELETED.items():
        assert per.get((pr, t, 'deleted')) == n, f'PR #{pr} {t}: title says {n} deleted'
    for t, v in prov['tables'].items():  # per-table: sum of per-PR creations == net creations; frame == created + changed; head = base + created - deleted
        assert sum(n for (pr, tt, k), n in per.items() if tt == t and k == 'created') == v['created'], t
        assert v['frame'] == v['created'] + v['changed_nonderived'], t
        assert v['head_rows'] == v['base_rows'] + v['created'] - v['deleted_not_in_frame'], t
    assert prov['frame_total'] == len(frame) == sum(v['frame'] for v in prov['tables'].values()) == 1653
    assert Counter(r['table'] for r in frame) == {t: v['frame'] for t, v in prov['tables'].items() if v['frame']}
    assert len({(r['table'], r['record_id']) for r in frame}) == len(frame), 'duplicate frame id'
    assert sum(v['derived_only_excluded'] for v in prov['tables'].values()) == 0  # tier1_qualifier* exclusion removed nothing in this window
    return frame, prov


def known_answers(frame):
    by = {(r['table'], r['record_id']): r for r in frame}
    g = by[('organizations', 'ORG-003645')]  # Gregstrom HQ moved MA -> NH (PR 267): changed across shards, HQ columns flagged
    assert g['prs'] == '267' and {'hq_city', 'hq_state', 'hq_county'} <= set(g['changed_columns'].split(';')) and g['shard'].endswith('organizations_NH.csv'), g
    assert by[('sites', 'SITE-019101')]['change_kind'] == 'created' and by[('sites', 'SITE-004416')]['changed_columns'].startswith('operating_status')
    assert ('people', 'PERSON-001402') not in by and 'PERSON-001402' in json.loads((H / 'frame_provenance.json').read_text())['tables']['people']['deleted_ids']
    assert Counter(r['prs'] for r in frame if r['table'] == 'people_identifiers') == {'259': 804, '263': 11, '271': 1}
    assert by[('programs', 'PROG-000305')]['change_kind'] == 'created' and by[('programs', 'PROG-000305')]['prs'] == '284'  # MRSEC row named in the PR title
    # derivation unit tests on synthetic rows: derived-only change excluded, content change kept, shard move alone not a change
    row = lambda **kw: ({'org_id': 'O', 'x': '1', 'tier1_qualifier': '', 'tier1_qualifier_basis': '', **kw})
    old = {'O': (row(), 'a.csv')}
    assert F.diff(old, {'O': (row(tier1_qualifier='public_parent', tier1_qualifier_basis='b'), 'a.csv')})[2] == ['O']
    assert F.diff(old, {'O': (row(x='2'), 'a.csv')})[1] == {'O': ['x']}
    assert F.diff(old, {'O': (row(), 'b.csv')})[4] == ['O']


def check_sample(frame):
    sample, alloc = S.draw(frame)
    assert sum(alloc.values()) == S.N == 50
    sizes = Counter(r['table'] for r in frame)
    assert all(alloc[t] >= S.FLOOR for t in sizes if sizes[t] >= S.CENSUS_BELOW) and all(alloc[t] == sizes[t] for t in sizes if sizes[t] < S.CENSUS_BELOW)
    cur = read('sample.csv')
    norm = lambda rows: [{k: str(r[k]) for k in sample[0]} for r in rows]  # csv reads strings; draw() holds ints
    assert norm(cur) == norm(sample), 'sample.csv != seeded re-draw'
    assert {(r['table'], r['record_id']) for r in sample} <= {(r['table'], r['record_id']) for r in frame}
    return sample


def check_header(fields):
    assert fields == S.BLIND_FIELDS, f'blind header must be exactly the whitelist, got {fields}'


def check_blind(sample):
    a, b = (H / 'blind_a.csv').read_bytes(), (H / 'blind_b.csv').read_bytes()
    assert a == b, 'blind_a != blind_b'
    check_header(list(csv.DictReader((H / 'blind_a.csv').open(newline='')).fieldnames))
    rows = read('blind_a.csv')
    assert len(rows) == 50 and {(r['table'], r['record_id']) for r in rows} == {(r['table'], r['record_id']) for r in sample}
    assert not S.leak_scan(rows), S.leak_scan(rows)
    # blind row order must not follow ID order (ids track PR order)
    assert [r['record_id'] for r in rows] != sorted(r['record_id'] for r in rows)
    freeze = json.loads((H / 'freeze.json').read_text())['sha256']
    for p, h in freeze.items():
        assert sha(p) == h, f'{p} changed after freeze'
    assert freeze['blind_a.csv'] == freeze['blind_b.csv']
    return rows


def check_leak_scan_catches(rows):
    """Plant defects in a copy; every one must be caught (a gate that cannot fail is not a gate)."""
    for field, plant in [('cited_sources', 'see PR #271'), ('evidence_json', 'EVD-333050'), ('values_json', 'minted in wave 3'),
                         ('cited_sources', 'verdict packet (staging working/x)'), ('context_json', '2026-11-11')]:
        bad = [dict(r) for r in rows]
        bad[0][field] += ' ' + plant
        assert S.leak_scan(bad), f'leak scan missed planted {plant!r} in {field}'
    try:
        check_header(S.BLIND_FIELDS + ['pr'])
    except AssertionError:
        return
    raise AssertionError('header check missed a planted pr column')


if __name__ == '__main__':
    frame, prov = check_frame()
    known_answers(frame)
    sample = check_sample(frame)
    rows = check_blind(sample)
    check_leak_scan_catches(rows)
    print(f"PASS blind-audit-10 phase 1: {len(frame)} frame records ({dict(Counter(r['table'] for r in frame))}), 59 first-parent commits, "
          f"{len(sample)} sampled (seed {S.SEED}), blind_a == blind_b, freeze hashes match, leak scan clean and catches 5 planted defects")
