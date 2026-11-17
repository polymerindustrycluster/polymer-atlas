"""Named check for blind audit 11, phase 1: frame reproduces from git and reconciles with every PR's published counts, one
hand-verified known answer per stratum (value at BASE, at HEAD, and at the step that made it), the classifier and leak scan
catch planted defects, the sample re-draws from the seed, and the blind inputs are identical, frozen and leak-free.
Adapted from tasks/blind-audit-10-2026-11-14/check.py.
Run from anywhere: python3 tasks/blind-audit-11-2026-11-17/check.py   (needs full git history: CI validate uses fetch-depth 0)
"""
import csv, hashlib, json, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import frame as F
import sample as S

H = F.H
sha = lambda p: hashlib.sha256((H / p).read_bytes()).hexdigest()
read = lambda p: list(csv.DictReader((H / p).open(newline='')))

# Published counts (AGENTS section 2 rule 10c), from each merged PR's body, or its task README where a replay superseded the body.
# (pr, table, class, kind) -> records
PUBLISHED = {
    (339, 'ecosystem', 'rulings', 'changed'): 1, (346, 'programs', 'rulings', 'changed'): 1,
    (341, 'registry_links', 'registry_federal_links', 'created'): 105, (341, 'sites', 'bands', 'changed'): 12,
    (340, 'members', 'members', 'changed'): 60, (340, 'members', 'members', 'created'): 1, (340, 'organizations', 'members', 'changed'): 1,
    (342, 'sites', 'zips', 'changed'): 348, (355, 'registry_links', 'uei_links', 'created'): 472, (353, 'sites', 'streets', 'changed'): 23,
    (350, 'organizations', 'navigation_links', 'changed'): 176, (349, 'organizations', 'markets', 'changed'): 16,
    (348, 'organizations', 'bands', 'changed'): 117,
    (348, 'sites', 'bands', 'changed'): 131,  # body says 137; tasks/ppp-size-bands-2026-11-16/README.md "Replay after PR #341": six #341 bands preserved, final 131
    (352, 'organizations', 'parents', 'changed'): 11, (351, 'sites', 'capabilities', 'changed'): 3, (351, 'site_capabilities', 'capabilities', 'created'): 8,
    (354, 'sites', 'tier_changes', 'changed'): 3, (344, 'organizations', 'markets', 'changed'): 31, (360, 'organizations', 'markets', 'changed'): 77,
    (361, 'sites', 'capabilities', 'changed'): 9, (361, 'site_capabilities', 'capabilities', 'created'): 4,
    (365, 'sites', 'capabilities', 'changed'): 14, (365, 'site_capabilities', 'capabilities', 'created'): 35,  # title says 45; body: 10 capability IDs retired, 35 rows
    (364, 'archive_links', 'archive_links', 'created'): 2188,
}
PUBLISHED_CELLS = {343: 58, 347: 63, 350: 234}  # "fill 58 / 63 ownership and founding fields"; "234 navigation cells"
PUBLISHED_337 = 3        # "All three material-filled records" (one organization, two sites)
PUBLISHED_336 = 1208     # "1,208 site coordinate pairs": all derived (coordinates), none in the frame

# Hand-verified from `git show` at BASE, HEAD and the merge step (class, table, record_id, step sha, pr, {col: (base, head)}); base None = created
KNOWN = [
    ('ownership_founding', 'organizations', 'ORG-000105', '20e87b3', 343, {'year_founded': ('', '1931'), 'ownership_type': ('', '')}),
    ('markets', 'organizations', 'ORG-000227', '45e184c', 360, {'markets_served': ('', 'aerospace_defense;appliances;automotive_unspecified;electronics_electrical;medical_healthcare_general')}),
    ('capabilities', 'site_capabilities', 'CAP-001106', 'b72f9df', 351, {'site_id': (None, 'SITE-001757'), 'capability_type': (None, 'material'), 'term': (None, 'polyurethane_pu'), 'provenance': (None, 'company_disclosed')}),
    ('streets', 'sites', 'SITE-000185', 'c7d606f', 353, {'street_address': ('', '300 Martinel Dr.')}),
    ('parents', 'organizations', 'ORG-000433', '915176b', 352, {'ultimate_parent_name': ('', 'HEXPOL Group'), 'parent_org_id': ('', '')}),
    ('registry_federal_links', 'registry_links', 'ORG-000038|FRS|110006267887|SITE-000038', '9bd1a8b', 341, {'match_basis': (None, 'echo_exporter_street_city_zip_name:SITE-000038')}),
    ('uei_links', 'registry_links', 'ORG-000889|UEI|SJZCEMGNC9D1|', 'd410968', 355, {'match_basis': (None, 'sam_exact_uei')}),
    ('bands', 'organizations', 'ORG-000478', '5b78ee7', 348, {'employee_band_ohio': ('', '1-9')}),
    ('members', 'members', 'MBR-000009', 'd18224a', 340, {'snapshot_date': ('2026-10-29', '2026-11-16'), 'display_name': ('Rubber Division', 'Rubber Division')}),
    ('zips', 'sites', 'SITE-000169', 'a66e2ae', 342, {'zip': ('', '44124')}),
    ('tier_changes', 'sites', 'SITE-000240', 'c958a8f', 354, {'verification_tier': ('C', 'B')}),
    ('archive_links', 'archive_links', 'EVD-013312|https://web.archive.org/web/20261104022108/https://www.avient.com/', '527ad21', 364, {'captured_at': (None, '2026-11-04')}),
    ('rulings', 'ecosystem', 'ORG-013503', '25e6f76', 339, {'polymer_program': ('true', '')}),
    ('rulings', 'programs', 'PROG-000329', 'ef32b5b', 346, {'status': ('active', 'tombstoned')}),
    ('navigation_links', 'organizations', 'ORG-000554', '23feb5c', 350, {'newsroom_url': ('', 'https://www.rpplusm.com/blog'), 'linkedin_url': ('', ''), 'newsroom_feed_url': ('', '')}),
]
A10_IS_ROLLUP_ONLY = lambda table, cols: table == 'ecosystem' and bool(set(cols) & {'polymer_program', 'polymer_program_name', 'polymer_program_url'}) and not set(cols) - {'last_verified', 'polymer_program', 'polymer_program_name', 'polymer_program_url'}  # A10 frame.py, verbatim logic


def check_frame():
    frame, prov = F.derive()
    assert read('frame.csv') == frame, 'frame.csv != git derivation'
    assert json.loads((H / 'frame_provenance.json').read_text()) == json.loads(json.dumps(prov)), 'provenance != git derivation'
    per = {(r['pr'], r['table'], r['change_class'], r['kind']): r['records'] for r in prov['per_pr']}
    for k, n in PUBLISHED.items():
        assert per.get(k) == n, f'PR #{k[0]} {k[1:]}: published {n}, git says {per.get(k)}'
    cells = Counter()
    for r in prov['cells_per_pr']:
        cells[r['pr']] += r['cells']
    for pr, n in PUBLISHED_CELLS.items():
        assert cells[pr] == n, f'PR #{pr}: published {n} cells, git says {cells[pr]}'
    assert sum(n for (pr, *_), n in per.items() if pr == 337) == PUBLISHED_337
    assert prov['derived_only_by_pr'] == [dict(pr=336, table='sites', records=PUBLISHED_336)]
    assert prov['generated_by_pr'] == [dict(pr=352, table='relationships', records=1)]  # "1 generated parent_of edge"
    assert set(per) == set(PUBLISHED) | {k for k in per if k[0] in (337, 343, 347)}, f'per-PR rows with no published count: {set(per) - set(PUBLISHED)}'
    for t, v in prov['tables'].items():  # per table: head = base + created; no deletions; nothing touched then reverted
        assert v['head_rows'] == v['base_rows'] + v['created'] and v['touched_then_reverted'] == 0, t
    assert prov['frame_total'] == len(frame) == sum(v['frame'] for v in prov['tables'].values()) == 3959
    assert dict(Counter(r['change_class'] for r in frame)) == prov['frame_by_class']
    assert sum(per.values()) == len(frame), 'every frame row is one per-PR record change (no record changed twice in one class)'
    assert len({(r['table'], r['record_id'], r['change_class']) for r in frame}) == len(frame), 'duplicate frame key'
    assert prov['trains'] == {'359': [353, 350, 349, 348, 356, 352, 351, 354], '363': [343, 347]}
    return frame, prov


def known_answers(frame):
    by = {(r['table'], r['record_id'], r['change_class']): r for r in frame}
    files = F.table_files(F.HEAD)
    for cl, t, k, step, pr, cols in KNOWN:
        row = by[(t, k, cl)]
        assert row['prs'] == str(pr), (k, row['prs'])
        step = F.git('rev-parse', step).strip()
        shard = row['shard']
        assert shard in files[t]
        get = lambda ref: next((r for r in F.rows_at(ref, shard) if F.key_of(t, r) == k), None)
        b, h, sb, sa = get(F.BASE), get(F.HEAD), get(step + '^1'), get(step)
        for c, (old, new) in cols.items():
            assert h[c] == new and sa[c] == new, (k, c, 'head/step value')
            assert (b is None and sb is None) if old is None else (b[c] == old and sb[c] == old), (k, c, 'base/pre-step value')
        assert set(cols) - {'capability_type', 'provenance', 'site_id', 'term', 'match_basis', 'captured_at', 'display_name', 'linkedin_url', 'newsroom_feed_url', 'ownership_type', 'parent_org_id'} \
            <= set(row['changed_columns'].split(';')), (k, row['changed_columns'])
    assert {cl for cl, *_ in KNOWN} == set(F.CLASSES), 'a stratum has no known answer'
    # #339 is in the frame although A10's rollup rule would have dropped it: the controller named the rulings stratum
    assert A10_IS_ROLLUP_ONLY('ecosystem', ['polymer_program']) and ('ecosystem', 'ORG-013503', 'rulings') in by
    # coordinates are derived: a coordinate-only change is excluded, a content change is kept, a shard move alone is not a change
    row = lambda **kw: ({'site_id': 'S', 'zip': '', 'latitude': '', 'longitude': '', 'geocode_precision': '', **kw})
    old = {'S': (row(), 'a.csv')}
    assert F.diff(old, {'S': (row(latitude='41.1', longitude='-81.5', geocode_precision='address_interpolated'), 'a.csv')})[2] == ['S']
    assert F.diff(old, {'S': (row(zip='44305', latitude='41.1'), 'a.csv')})[1] == {'S': ['zip']}
    assert F.diff(old, {'S': (row(), 'b.csv')})[4] == ['S']
    # classifier: every column maps or the build fails; ride-along alone fails; class split for registry links; authored edges fail
    assert F.classes_of_change('sites', 'S', ['zip', 'sources']) == {'zips': {'zip', 'sources'}}
    for bad in (['website'], ['last_verified', 'notes'], ['status']):
        try:
            F.classes_of_change('organizations', 'X', bad)
        except AssertionError:
            continue
        raise AssertionError(f'classifier accepted {bad}')
    assert F.created_class('registry_links', {'registry': 'UEI'}) == 'uei_links' and F.created_class('registry_links', {'registry': 'TRI_TRIFID'}) == 'registry_federal_links'
    try:
        F.created_class('relationships', {'relationship_id': 'R', 'relationship_type': 'member_of', 'basis': 'directory'})
    except AssertionError:
        pass
    else:
        raise AssertionError('an authored member_of edge was not refused')


def check_sample(frame):
    sample, alloc = S.draw(frame)
    assert sum(alloc.values()) == S.N == 120
    sizes = Counter(r['change_class'] for r in frame)
    assert all(alloc[c] >= S.FLOOR for c in sizes if sizes[c] >= S.CENSUS_BELOW) and all(alloc[c] == sizes[c] for c in sizes if sizes[c] < S.CENSUS_BELOW)
    norm = lambda rows: [{k: str(r[k]) for k in sample[0]} for r in rows]  # csv reads strings; draw() holds ints
    assert norm(read('sample.csv')) == norm(sample), 'sample.csv != seeded re-draw'
    assert {(r['table'], r['record_id'], r['change_class']) for r in sample} <= {(r['table'], r['record_id'], r['change_class']) for r in frame}
    return sample


def check_header(fields):
    assert fields == S.BLIND_FIELDS, f'blind header must be exactly the whitelist, got {fields}'


def check_blind(sample):
    assert (H / 'blind_a.csv').read_bytes() == (H / 'blind_b.csv').read_bytes(), 'blind_a != blind_b'
    check_header(list(csv.DictReader((H / 'blind_a.csv').open(newline='')).fieldnames))
    rows = read('blind_a.csv')
    key = lambda r: (r['table'], r['record_id'], S.BLIND_LABEL.get(r['change_class'], r['change_class']))
    assert len(rows) == 120 and {key(r) for r in rows} == {key(r) for r in sample}
    assert {r['blind_id']: key(r) for r in rows} == {r['blind_id']: key(r) for r in read('sample.csv')}, 'sample.csv blind_id map != blind file'
    assert 'rulings' not in {r['change_class'] for r in rows} and 'program_status' in {r['change_class'] for r in rows}
    assert not S.leak_scan(rows), S.leak_scan(rows)
    assert [r['record_id'] for r in rows] != sorted(r['record_id'] for r in rows), 'blind order follows ID order'
    assert not re.search(r'#\d+', (H / 'REVIEWER_INSTRUCTIONS.md').read_text()), 'reviewer instructions name a PR'
    freeze = json.loads((H / 'freeze.json').read_text())['sha256']
    assert set(freeze) >= {'blind_a.csv', 'blind_b.csv', 'REVIEWER_INSTRUCTIONS.md', 'frame.csv', 'sample.csv'}
    for p, h in freeze.items():
        assert sha(p) == h, f'{p} changed after freeze'
    return rows


def check_leak_scan_catches(rows):
    """Plant defects in a copy; every one must be caught (a gate that cannot fail is not a gate)."""
    plain = next(r for r in rows if r['table'] != 'archive_links')
    arch = next(r for r in rows if r['table'] == 'archive_links')
    for r, field, plant in [(plain, 'cited_sources', 'see PR #271'), (plain, 'evidence_json', 'EVD-333050'), (plain, 'values_json', 'minted in wave 3'),
                            (plain, 'cited_sources', 'verdict packet (staging working/x)'), (plain, 'context_json', '2026-11-16'),
                            (plain, 'cited_sources', 'Lane CAP2A'), (plain, 'values_json', 'per the 2026 ruling'), (plain, 'record_id', 'EVD-013312'), (arch, 'record_id', ' banked'),
                            (arch, 'values_json', 'EVD-013312')]:
        bad = [dict(x) for x in rows]
        i = rows.index(r)
        bad[i][field] = bad[i][field] + (' ' if field != 'record_id' or r is arch else '|') + plant
        assert S.leak_scan(bad), f'leak scan missed planted {plant!r} in {field}'
    assert not S.leak_scan([dict(plain, context_json='{"city": "Green Lane", "state": "PA"}')]), 'place name Green Lane must pass'
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
    print(f"PASS blind-audit-11 phase 1: {len(frame)} frame record changes {prov['frame_by_class']}; published counts reconcile for {len(PUBLISHED)} "
          f"(PR, table, class) pairs + cells for #343/#347/#350; {len(KNOWN)} known answers ({len(F.CLASSES)} strata); sample {len(sample)} re-draws; "
          f"blind files identical, frozen, leak-free; planted defects caught")
