"""Named check for blind audit 10 (phases 1 and 3): frame reproduces from git and reconciles, sample re-draws, blind inputs are
identical, frozen, and leak-free, the leak scan / derivation catch planted defects, and phase 3 recomputes every count: reviewer
lock hashes, cross-tab, the 14 adjudications (each quote re-verified), final grades, per-stratum and weighted statistics, the report.
Run from anywhere: python3 tasks/blind-audit-10-2026-11-14/check.py   (needs full git history: CI validate uses fetch-depth 0)
"""
import copy, csv, hashlib, json, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adjudicate_fetch as AF
import frame as F
import sample as S
import stale_checkout_check as SC
import stats as ST
import write_report as WR

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
        assert v['frame'] == v['created'] + v['changed_nonderived'] - v['derived_rollup_only_excluded'], t
        assert v['head_rows'] == v['base_rows'] + v['created'] - v['deleted_not_in_frame'], t
    assert prov['frame_total'] == len(frame) == sum(v['frame'] for v in prov['tables'].values()) == 1621
    assert Counter(r['table'] for r in frame) == {t: v['frame'] for t, v in prov['tables'].items() if v['frame']}
    assert len({(r['table'], r['record_id']) for r in frame}) == len(frame), 'duplicate frame id'
    assert sum(v['derived_only_excluded'] for v in prov['tables'].values()) == 0  # tier1_qualifier* exclusion removed nothing in this window
    assert prov['tables']['ecosystem']['derived_rollup_only_excluded'] == 32 == len(prov['tables']['ecosystem']['rollup_excluded_ids'])
    assert not {r['record_id'] for r in frame if r['table'] == 'ecosystem'} & set(prov['tables']['ecosystem']['rollup_excluded_ids'])
    return frame, prov


def known_answers(frame):
    by = {(r['table'], r['record_id']): r for r in frame}
    g = by[('organizations', 'ORG-003645')]  # Gregstrom HQ moved MA -> NH (PR 267): changed across shards, HQ columns flagged
    assert g['prs'] == '267' and {'hq_city', 'hq_state', 'hq_county'} <= set(g['changed_columns'].split(';')) and g['shard'].endswith('organizations_NH.csv'), g
    assert by[('sites', 'SITE-019101')]['change_kind'] == 'created' and by[('sites', 'SITE-004416')]['changed_columns'].startswith('operating_status')
    assert ('people', 'PERSON-001402') not in by and 'PERSON-001402' in json.loads((H / 'frame_provenance.json').read_text())['tables']['people']['deleted_ids']
    assert Counter(r['prs'] for r in frame if r['table'] == 'people_identifiers') == {'259': 804, '263': 11, '271': 1}
    assert by[('programs', 'PROG-000305')]['change_kind'] == 'created' and by[('programs', 'PROG-000305')]['prs'] == '284'  # MRSEC row named in the PR title
    assert ('ecosystem', 'ORG-004660') not in by and 'ORG-004660' in json.loads((H / 'frame_provenance.json').read_text())['tables']['ecosystem']['rollup_excluded_ids']  # UChicago: rollup-only
    assert by[('ecosystem', 'ORG-013501')]['change_kind'] == 'created'  # Wake Forest: a created ecosystem row stays in
    assert F.is_rollup_only('ecosystem', ['polymer_program_name', 'last_verified']) and not F.is_rollup_only('ecosystem', ['polymer_program_name', 'website'])
    assert not F.is_rollup_only('people', ['polymer_program_name']) and not F.is_rollup_only('ecosystem', ['last_verified'])
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


LOCKED = {'verdicts_a.csv': 'dfd8f49021143b9e36df8584ad08141eee871e367fd057aec91bf2ff3969cf4e', 'verdicts_b.csv': '60efe428329df94808d517e08adab740ebdc6008b43d618b13e97bd53757d7bc'}


def check_phase3():
    for p, h in LOCKED.items():  # the reviewers' locked files, as BOARD recorded them
        assert sha(p) == h, f'{p} changed after the reviewer lock'
    a, b = ({r['blind_id']: r['verdict'] for r in read(f'verdicts_{k}.csv')} for k in 'ab')
    assert len(a) == len(b) == 50 and a.keys() == b.keys()
    assert Counter(a.values()) == {'AGREE': 45, 'FIELD_ERROR': 4, 'UNRESOLVED': 1} and Counter(b.values()) == {'AGREE': 37, 'UNRESOLVED': 13}
    assert Counter((a[i], b[i]) for i in a) == {('AGREE', 'AGREE'): 36, ('AGREE', 'UNRESOLVED'): 9, ('FIELD_ERROR', 'UNRESOLVED'): 4, ('UNRESOLVED', 'AGREE'): 1}
    adj = json.loads((H / 'adjudication.json').read_text())
    assert {e['id'] for e in adj} == {i for i in a if a[i] != b[i]} and len(adj) == 14, 'adjudication does not cover exactly the disagreements'
    full = missing = 0
    for e in adj:
        assert e['grade'] in ST.GRADES and (e['grade'] != 'UNRESOLVED' or e['settling_fact']) and (e['grade'] != 'FIELD_ERROR' or (e['current_value'] and e['correct_value']))
        for r in e['receipts']:
            assert r['http_status'] == 200 or r['via'] in ('dig', 'curl+xhr-referer'), f"receipt on a page that did not load: {r['url']}"
            if r.get('quote'):  # committed excerpt (CI-safe): the quote's words appear in order in the page's word stream
                assert AF.quote_in_order(r['excerpt_words'], r['quote']), f"excerpt lacks quote: {r['url']}"
            raw = AF.RAW / f"{r['sha256']}.bin"
            if raw.exists():  # full stored body (persist dir): hash, quote, absence and raw pattern re-verified
                body = raw.read_bytes()
                assert hashlib.sha256(body).hexdigest() == r['sha256'] and len(body) == r['bytes'], f"stored body hash mismatch: {r['url']}"
                text = AF.visible(body, r['url'])
                assert not r.get('quote') or AF.quote_in_order(text, r['quote']), f"quote not on stored page: {r['url']}"
                assert all(not AF.re.search(AF.re.escape(t), text, AF.re.I) for t in r.get('absent', [])), f"absent term present: {r['url']}"
                assert not r.get('raw_re') or AF.re.search(r['raw_re'].encode(), body), f"raw pattern missing: {r['url']}"
                full += 1
            else:
                missing += 1
                assert not r.get('absent') and not r.get('raw_re'), f"absence/raw receipt cannot be verified without the stored body: {r['url']}"
    final = ST.final_grades()
    assert read('final_grades.csv') == [{k: str(v) for k, v in r.items()} for r in final], 'final_grades.csv != recomputation'
    sample = read('sample.csv')
    res = ST.summarize(sample, final)
    stored = json.loads((H / 'statistics.json').read_text())
    for k, v in res.items():
        assert json.loads(json.dumps(v)) == stored[k], f'statistics.json {k} != recomputation'
    assert stored['final_counts'] == {'AGREE': 46, 'FIELD_ERROR': 2, 'CREATION_ERROR': 0, 'UNRESOLVED': 2}
    assert ST.wilson(0, 20) == [0, 0.161125] and ST.wilson(20, 20) == [0.838875, 1] and ST.wilson(10, 20) == [0.299298, 0.700702]
    assert stored['corrections'] == ST.corrections(adj) and len(stored['corrections']) == 2
    dups, n = SC.duplicates()
    assert n == 50 and not dups, f'duplicates at pinned HEAD: {dups}'
    assert WR.render() == WR.OUT.read_text(), 'docs/reviews report differs from the regenerated text'
    # planted defects: each must be rejected, never accepted as a smaller or kinder census
    sf = ST.final_grades()
    for bad_final in (sf[:-1], sf + [sf[0]], [dict(r, final_grade='AGREE') if r['final_grade'] == 'UNRESOLVED' else r for r in sf][:-1]):
        try:
            ST.summarize(sample, bad_final)
        except AssertionError:
            continue
        raise AssertionError('summarize accepted an incomplete or duplicated verdict census')
    short = copy.deepcopy(adj)
    short[0]['receipts'][0]['excerpt_words'] = 'nothing relevant'
    assert not AF.quote_in_order(short[0]['receipts'][0]['excerpt_words'], short[0]['receipts'][0]['quote']), 'raw-check accepted a quote that is not on the page'
    return full, missing, stored




if __name__ == '__main__':
    frame, prov = check_frame()
    known_answers(frame)
    sample = check_sample(frame)
    rows = check_blind(sample)
    check_leak_scan_catches(rows)
    print(f"PASS blind-audit-10 phase 1: {len(frame)} frame records ({dict(Counter(r['table'] for r in frame))}), 59 first-parent commits, "
          f"{len(sample)} sampled (seed {S.SEED}), blind_a == blind_b, freeze hashes match, leak scan clean and catches 5 planted defects")
    full, missing, st = check_phase3()
    print(f"PASS blind-audit-10 phase 3: reviewer locks match, cross-tab 36/9/4/1, 14 adjudications ({full + missing} receipts: {full} re-verified against stored full bodies, "
          f"{missing} on committed excerpts only), final grades {st['final_counts']}, per-stratum and weighted statistics recomputed, report regenerates identically, "
          f"no duplicates at pinned HEAD, incomplete/duplicate census and unreadable-quote defects rejected")
    if missing:
        print(f"WARNING: {missing} receipts were verified only on the committed excerpt; the stored raw bodies ({AF.RAW}) are not present here, so full-body hashes and absence terms were not re-checked for them")
