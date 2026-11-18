"""Blind audit 11 frame: every record change (one record x one change class) made by the data PRs merged 2026-11-16..17.

Adapted from tasks/blind-audit-10-2026-11-14/frame.py. Steps are the first-parent commits BASE..HEAD, with each merge train
expanded into its own first-parent "Merge PR #N ... into merge train" commits, so every change is attributed to the PR
that made it. Two derivations must agree (AGENTS §2 rule 10): (1) the per-step diffs, which give PR and class
attribution; (2) one BASE-vs-HEAD diff of each whole table, which gives the net change.
Unit: record change = one row at HEAD (keyed by its table ID) x one change class, graded on that class's columns.
Usage: python3 frame.py            verify frame.csv + frame_provenance.json reproduce from git
       python3 frame.py --write    (re)write them
"""
import csv, io, json, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[1]  # git pathspecs (data/) are cwd-relative: always run git from the repo root
BASE = 'be2e6084d430f1e6f9de0f66289b1d3c2570e255'   # first parent of 6b07f18 (the #336 merge): PR #334
HEAD = '4182519137dd8d8483d244ae9a2247ed7c03f2f4'   # PR #365 merge, main at the brief
TABLES = {  # table -> (file regex, key columns)
    'organizations': (r'data/organizations_[A-Z0-9]+\.csv', ('org_id',)),
    'sites': (r'data/sites_[A-Z0-9]+\.csv', ('site_id',)),
    'ecosystem': (r'data/ecosystem\.csv', ('org_id',)),
    'programs': (r'data/programs\.csv', ('program_id',)),
    'members': (r'data/members\.csv', ('member_row_id',)),
    'registry_links': (r'data/registry_links\.csv', ('org_id', 'registry', 'registry_id', 'site_id')),
    'site_capabilities': (r'data/site_capabilities\.csv', ('capability_id',)),
    'archive_links': (r'data/archive_links\.csv', ('evidence_id', 'archive_ref')),
    'relationships': (r'data/relationships\.csv', ('relationship_id',)),
}
# AGENTS §1: tier1_qualifier* are derived, and coordinates are reference data, never evidence (controller brief: out of frame)
DERIVED = lambda c: c.startswith('tier1_qualifier') or c in ('latitude', 'longitude', 'geocode_precision')
RIDE = {'last_verified', 'sources', 'notes'}  # ride along with the class change they document; never a class alone
CLASS = {  # column -> change class (controller brief 2026-11-17; navigation_links is the one class the brief did not name)
    'year_founded': 'ownership_founding', 'ownership_type': 'ownership_founding',
    'markets_served': 'markets', 'certifications': 'markets',
    'processes': 'capabilities', 'materials': 'capabilities', 'materials_other_note': 'capabilities',
    'street_address': 'streets', 'zip': 'zips',
    'parent_org_id': 'parents', 'ultimate_parent_name': 'parents',
    'employee_band_ohio': 'bands', 'employee_band_site': 'bands',
    'pic_member': 'members', 'membership_source_url': 'members', 'snapshot_date': 'members', 'display_name': 'members',
    'verification_tier': 'tier_changes',
    'newsroom_url': 'navigation_links', 'newsroom_feed_url': 'navigation_links', 'linkedin_url': 'navigation_links',
}
TABLE_CLASS = {('ecosystem', 'polymer_program'): 'rulings', ('programs', 'status'): 'rulings'}  # the AFFOA owner rulings (#339, #346)
CLASSES = ['ownership_founding', 'markets', 'capabilities', 'streets', 'parents', 'registry_federal_links', 'uei_links', 'bands',
           'members', 'zips', 'tier_changes', 'archive_links', 'rulings', 'navigation_links']
GENERATED_EDGE = {'parent_of', 'successor_of', 'merged_into'}  # AGENTS §4: generated from organization columns, never authored
DATA_PRS = {336, 339, 346, 341, 340, 337, 342, 355, 353, 350, 349, 348, 352, 351, 354, 343, 347, 344, 360, 361, 365, 364}
NO_DATA_PRS = {335, 338, 345, 356, 357, 358, 366}  # packet, tooling, site and queue PRs: no frame-table row may change
FRAME_FIELDS = ['change_class', 'table', 'record_id', 'change_kind', 'prs', 'pr_columns', 'changed_columns', 'shard']


def class_of(table, col):
    return TABLE_CLASS.get((table, col)) or CLASS.get(col)


def created_class(table, r):
    """Change class of a created row; None = generated (out of frame)."""
    if table == 'registry_links':
        return 'uei_links' if r['registry'] == 'UEI' else 'registry_federal_links'
    if table == 'relationships':
        assert r['relationship_type'] in GENERATED_EDGE and r['basis'].startswith('Generated from'), f'authored relationship created: {r["relationship_id"]}'
        return None
    return {'archive_links': 'archive_links', 'site_capabilities': 'capabilities', 'members': 'members'}[table]


def git(*a):
    return subprocess.check_output(['git', *a], cwd=ROOT).decode()


def rows_at(ref, path):
    text = subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=ROOT).decode('utf-8')
    return list(csv.DictReader(io.StringIO(text, newline='')))


def key_of(table, r):
    return '|'.join(r[k] for k in TABLES[table][1])


def table_files(ref):
    """All shard paths per table at ref."""
    paths = git('ls-tree', '-r', '--name-only', ref, 'data/').splitlines()
    return {t: [p for p in paths if re.fullmatch(rx, p)] for t, (rx, _) in TABLES.items()}


def load(ref, files, table):
    """key -> (row, shard path), merged across the given files."""
    out = {}
    for p in files:
        for r in rows_at(ref, p):
            k = key_of(table, r)
            assert k not in out, f'{table}: duplicate key {k} at {ref[:7]}'
            out[k] = (r, p)
    return out


def diff(old, new):
    """(created, changed{key: nonderived cols}, derived_only, deleted, shard_moves) between two key->(row, path) maps."""
    created = [k for k in new if k not in old]
    deleted = [k for k in old if k not in new]
    changed, derived_only, moves = {}, [], []
    for k in new.keys() & old.keys():
        (o, op), (n, np_) = old[k], new[k]
        cols = [c for c in n if o.get(c, '') != n[c]]
        cols += [c for c in o if c not in n and o[c] != '']
        nd = [c for c in cols if not DERIVED(c)]
        if nd:
            changed[k] = nd
        elif cols:
            derived_only.append(k)
        elif op != np_:
            moves.append(k)
    return created, changed, derived_only, deleted, moves


def classes_of_change(table, k, cols):
    """{class: cols} for one changed record; ride-along columns go to every class the same step changed. Fails on an unmapped column."""
    unmapped = [c for c in cols if c not in RIDE and not class_of(table, c)]
    assert not unmapped, f'{table} {k}: changed column(s) with no change class: {unmapped}'
    by = defaultdict(set)
    for c in cols:
        if c not in RIDE:
            by[class_of(table, c)].add(c)
    assert by, f'{table} {k}: only ride-along columns changed: {cols}'
    ride = {c for c in cols if c in RIDE}
    return {cl: cs | ride for cl, cs in by.items()}


def pr_num(sha):
    s = git('log', '-1', '--format=%s', sha)
    m = re.search(r'Merge PR #(\d+) .*into merge train', s) or re.search(r'pull request #(\d+)', s)
    assert m, f'no PR number in subject of {sha}: {s}'
    return int(m.group(1))


def steps():
    """[(sha, pr, train_pr)]: first-parent commits, merge trains expanded into their own first-parent PR merges."""
    out, trains = [], {}
    main = git('rev-list', '--first-parent', '--reverse', f'{BASE}..{HEAD}').split()
    assert len(main) == 21 and git('rev-parse', main[0] + '^1').strip() == BASE, 'window is not the 21 first-parent commits on BASE'
    for c in main:
        ps = git('log', '-1', '--format=%P', c).split()
        sub = git('rev-list', '--first-parent', '--reverse', f'{ps[0]}..{ps[1]}').split() if len(ps) > 1 else []
        tr = [s for s in sub if re.search(r'Merge PR #\d+ .*into merge train', git('log', '-1', '--format=%s', s))]
        if not tr:
            out.append((c, pr_num(c), None))
            continue
        # a train must branch from the main parent and its merge must add nothing to data/ beyond the train tip
        assert git('rev-parse', sub[0] + '^1').strip() == ps[0], f'train {c[:7]} does not branch from its main parent'
        assert git('diff', '--name-only', ps[1], c, '--', 'data/').strip() == '', f'train merge {c[:7]} changes data/ beyond the train tip'
        assert tr == sub, f'train {c[:7]} has first-parent commits that are not PR merges'
        trains[pr_num(c)] = [pr_num(s) for s in tr]
        out += [(s, pr_num(s), pr_num(c)) for s in tr]
    return out, trains


def derive():
    st, trains = steps()
    touched = defaultdict(lambda: defaultdict(set))  # (table, key, class) -> pr -> cols
    per_pr = Counter()      # (pr, table, class, kind) -> records
    cells = Counter()       # (pr, table, class) -> non-ride cells changed
    derived_only, generated, other_files, deleted = Counter(), Counter(), Counter(), Counter()
    prs_with_rows = set()
    for sha, pr, _ in st:
        files = git('diff-tree', '--no-commit-id', '--name-only', '-r', sha + '^1', sha, '--', 'data/').splitlines()
        for t, (rx, _) in TABLES.items():
            fs = [p for p in files if re.fullmatch(rx, p)]
            if not fs:
                continue
            have = lambda ref: [p for p in fs if subprocess.run(['git', 'cat-file', '-e', f'{ref}:{p}'], cwd=ROOT).returncode == 0]
            new = load(sha, have(sha), t)
            c, ch, d_only, dele, _ = diff(load(sha + '^1', have(sha + '^1'), t), new)
            for k in c:
                cl = created_class(t, new[k][0])
                if cl is None:
                    generated[(pr, t)] += 1
                    continue
                touched[(t, k, cl)][pr] |= {'*created*'}
                per_pr[(pr, t, cl, 'created')] += 1
                prs_with_rows.add(pr)
            for k, cols in ch.items():
                for cl, cs in classes_of_change(t, k, cols).items():
                    touched[(t, k, cl)][pr] |= cs
                    per_pr[(pr, t, cl, 'changed')] += 1
                    cells[(pr, t, cl)] += len(cs - RIDE)
                    prs_with_rows.add(pr)
            for k in dele:
                deleted[(pr, t)] += 1
            for k in d_only:
                derived_only[(pr, t)] += 1
        for p in files:
            if not any(re.fullmatch(rx, p) for rx, _ in TABLES.values()) and not re.fullmatch(r'data/evidence_[a-z_]+_[A-Z0-9]+\.csv', p):
                other_files[p] += 1
    all_prs = {pr for _, pr, _ in st} | set(trains)
    assert prs_with_rows == DATA_PRS - {336}, f'PRs with frame rows {sorted(prs_with_rows)} != brief data PRs minus coordinate-only #336'
    assert all_prs == DATA_PRS | NO_DATA_PRS | set(trains), f'unexpected PR set {sorted(all_prs - DATA_PRS - NO_DATA_PRS - set(trains))}'
    assert not other_files and not deleted, (dict(other_files), dict(deleted))
    # (2) independent net derivation: whole tables at BASE vs HEAD
    fb, fh = table_files(BASE), table_files(HEAD)
    frame, prov_tables = [], {}
    for t in TABLES:
        old, new = load(BASE, fb[t], t), load(HEAD, fh[t], t)
        c, ch, d_only, dele, moves = diff(old, new)
        net = {}
        for k in c:
            cl = created_class(t, new[k][0])
            if cl:
                net[(k, cl)] = ['*created*']
        for k, cols in ch.items():
            kept = set()
            for cl, cs in classes_of_change(t, k, cols).items():
                # a ride-along column belongs to a class only if a step changed it together with that class
                cs = {c for c in cs if c not in RIDE or any(c in v for v in touched[(t, k, cl)].values())}
                net[(k, cl)] = sorted(cs)
                kept |= cs
            assert set(cols) <= kept, f'{t} {k}: net ride-along change no class step made: {set(cols) - kept}'
        seen = {(k, cl) for (tt, k, cl), v in touched.items() if tt == t and k in new and any(v.values())}
        missing = sorted(x for x in net if x not in seen)
        assert not missing, f'{t}: net change not seen by any step: {missing[:5]}'
        reverted = sorted(x for x in seen if x not in net)
        for (k, cl) in sorted(net):
            r, shard = new[k]
            prs = sorted(touched[(t, k, cl)])
            cols = [c for c in r if c in net[(k, cl)]] if net[(k, cl)] != ['*created*'] else [c for c in r if r[c] != '' and not DERIVED(c)]
            frame.append(dict(change_class=cl, table=t, record_id=k, change_kind='created' if net[(k, cl)] == ['*created*'] else 'changed', prs=';'.join(map(str, prs)),
                              pr_columns=json.dumps({str(p): sorted(touched[(t, k, cl)][p]) for p in prs}, sort_keys=True), changed_columns=';'.join(cols), shard=shard))
        assert not dele, f'{t}: rows deleted in the window {dele[:5]}'
        prov_tables[t] = dict(base_rows=len(old), head_rows=len(new), created=len(c), changed_nonderived=len(ch), derived_only_excluded=len(d_only),
                              generated_excluded=sum(1 for k in c if created_class(t, new[k][0]) is None), frame=len(net), shard_move_only_excluded=len(moves),
                              touched_then_reverted=len(reverted), reverted=[f'{k}|{cl}' for k, cl in reverted])
    keyed = [(r['table'], r['record_id'], r['change_class']) for r in frame]
    assert len(keyed) == len(set(keyed)), 'duplicate (table, record_id, class) in frame'
    for t in TABLES:  # AGENTS §2 rule 10b: record IDs unique at HEAD
        ids = [key_of(t, r) for r, _ in load(HEAD, fh[t], t).values()]
        assert len(ids) == len(set(ids)), f'{t}: ids not unique at HEAD'
    eco, org = ({r['org_id'] for r, _ in load(HEAD, fh[t], t).values()} for t in ('ecosystem', 'organizations'))
    assert not eco & org, 'org_id appears in both ecosystem and organizations'
    by_class = Counter(r['change_class'] for r in frame)
    assert set(by_class) == set(CLASSES), f'classes with no frame rows or unknown: {set(CLASSES) ^ set(by_class)}'
    prov = dict(base=BASE, head=HEAD, first_parent_commits=21, steps=[dict(sha=s[:7], pr=p, train=tr) for s, p, tr in st], trains={str(k): v for k, v in trains.items()},
                tables=prov_tables, frame_total=len(frame), frame_by_class={cl: by_class[cl] for cl in CLASSES},
                per_pr=[dict(pr=pr, table=t, change_class=cl, kind=kind, records=n) for (pr, t, cl, kind), n in sorted(per_pr.items())],
                cells_per_pr=[dict(pr=pr, table=t, change_class=cl, cells=n) for (pr, t, cl), n in sorted(cells.items())],
                derived_only_by_pr=[dict(pr=p, table=t, records=n) for (p, t), n in sorted(derived_only.items())],
                generated_by_pr=[dict(pr=p, table=t, records=n) for (p, t), n in sorted(generated.items())],
                unit='record change: one row at HEAD keyed by its table ID (registry_links: org_id+registry+registry_id+site_id; archive_links: evidence_id+archive_ref) x one change class, created or changed in a non-derived column by a step in BASE..HEAD',
                excluded='latitude, longitude, geocode_precision (reference data, AGENTS section 1; all of #336) and tier1_qualifier* (derived); generated parent_of/successor_of/merged_into edges in relationships.csv (AGENTS section 4); evidence_*.csv appends (not a frame table); last_verified/sources/notes changes ride with the class change they document')
    return sorted(frame, key=lambda r: (CLASSES.index(r['change_class']), list(TABLES).index(r['table']), r['record_id'])), prov


def write_csv(path, rows, fields):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


if __name__ == '__main__':
    frame, prov = derive()
    if '--write' in sys.argv:
        write_csv(H / 'frame.csv', frame, FRAME_FIELDS)
        (H / 'frame_provenance.json').write_text(json.dumps(prov, indent=1, sort_keys=True) + '\n')
    with (H / 'frame.csv').open(newline='') as f:
        assert list(csv.DictReader(f)) == frame, 'frame.csv differs from the pinned git derivation'
    assert json.loads((H / 'frame_provenance.json').read_text()) == json.loads(json.dumps(prov)), 'frame_provenance.json differs'
    print('PASS frame reproduces from git;', len(frame), 'record changes;', prov['frame_by_class'])
