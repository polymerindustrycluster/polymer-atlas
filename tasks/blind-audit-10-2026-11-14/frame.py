"""Blind audit 10 frame: every record created or changed (non-derived columns) by a first-parent commit in BASE..HEAD.

Two independent derivations must agree (AGENTS §2 rule 10): (1) the sum of per-commit first-parent diffs, which gives
PR attribution; (2) one BASE-vs-HEAD diff of the whole table, which gives the net change. Unit: record = one row at HEAD
keyed by its table ID (people_identifiers: person_id+identifier_type+identifier_id).
Usage: python3 frame.py            verify frame.csv + frame_provenance.json reproduce from git
       python3 frame.py --write    (re)write them
"""
import csv, io, json, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[1]  # git pathspecs (data/) are cwd-relative: always run git from the repo root
BASE = '1fefbd29ea2fa654a59bf4d1e0b9acc8470a010f'   # last commit before the window (PR #257)
HEAD = '4ecc7cf87847fbee27111af4c56c9acf92e0c095'   # PR #329 merge
TABLES = {  # table -> (file regex, key columns)
    'people': (r'data/people\.csv', ('person_id',)),
    'programs': (r'data/programs\.csv', ('program_id',)),
    'ecosystem': (r'data/ecosystem\.csv', ('org_id',)),
    'organizations': (r'data/organizations_[A-Z0-9]+\.csv', ('org_id',)),
    'sites': (r'data/sites_[A-Z0-9]+\.csv', ('site_id',)),
    'relationships': (r'data/relationships\.csv', ('relationship_id',)),
    'people_identifiers': (r'data/people_identifiers\.csv', ('person_id', 'identifier_type', 'identifier_id')),
    'event_participation': (r'data/event_participation\.csv', ('participation_id',)),
}
DERIVED = lambda c: c.startswith('tier1_qualifier')  # AGENTS §1: derived fields are hands-off; owner brief names tier1_qualifier*
ROLLUP = {'polymer_program', 'polymer_program_name', 'polymer_program_url'}  # SCHEMA §4.11 generated rollup of an institution's program rows
FRAME_FIELDS = ['table', 'record_id', 'change_kind', 'prs', 'pr_columns', 'changed_columns', 'derived_rollup_only', 'shard']


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


def pr_of(sha):
    m = re.search(r'\(#(\d+)\)\s*$', git('log', '-1', '--format=%s', sha)) or re.search(r'pull request #(\d+)', git('log', '-1', '--format=%s', sha))
    return int(m.group(1)) if m else None


def derive():
    commits = git('rev-list', '--first-parent', '--reverse', f'{BASE}..{HEAD}').split()
    assert len(commits) == 59, f'expected 59 first-parent commits in range, got {len(commits)}'
    assert git('rev-parse', commits[0] + '^1').strip() == BASE, 'first first-parent commit does not sit on BASE'
    touched = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))  # table -> key -> pr -> cols
    created_by = defaultdict(dict)                   # table -> key -> pr that created it
    per_pr = Counter()
    pr_of_commit, other_data_files = {}, Counter()
    derived_only = Counter()
    for sha in commits:
        pr = pr_of(sha)
        assert pr, f'no PR number in subject of {sha}'
        pr_of_commit[sha] = pr
        changed_files = git('diff-tree', '--no-commit-id', '--name-only', '-r', sha + '^1', sha, '--', 'data/').splitlines()
        for t, (rx, _) in TABLES.items():
            fs = [p for p in changed_files if re.fullmatch(rx, p)]
            if not fs:
                continue
            # a deleted/renamed shard is absent at one side: load only the files that exist there
            have = lambda ref: [p for p in fs if subprocess.run(['git', 'cat-file', '-e', f'{ref}:{p}'], cwd=ROOT).returncode == 0]
            c, ch, d_only, dele, _ = diff(load(sha + '^1', have(sha + '^1'), t), load(sha, have(sha), t))
            for k in c:
                touched[t][k][pr] |= {'*created*'}
                created_by[t].setdefault(k, pr)
                per_pr[(pr, t, 'created')] += 1
            for k, cols in ch.items():
                touched[t][k][pr] |= set(cols)
                per_pr[(pr, t, 'changed')] += 1
            for k in dele:
                touched[t][k][pr] |= {'*deleted*'}
                per_pr[(pr, t, 'deleted')] += 1
            for k in d_only:
                derived_only[(pr, t)] += 1
        for p in changed_files:
            if not any(re.fullmatch(rx, p) for rx, _ in TABLES.values()) and not p.startswith('data/evidence_'):
                other_data_files[p] += 1
    # (2) independent net derivation: whole tables at BASE vs HEAD
    fb, fh = table_files(BASE), table_files(HEAD)
    frame, prov_tables = [], {}
    for t in TABLES:
        old, new = load(BASE, fb[t], t), load(HEAD, fh[t], t)
        c, ch, d_only, dele, moves = diff(old, new)
        net = {k: ['*created*'] for k in c}
        net.update(ch)
        commit_keys = {k for k, v in touched[t].items() if any(cols - {'*deleted*'} for cols in v.values()) and k in new}
        # keys the commits touched with a non-derived change and that still exist at HEAD, minus net-unchanged (reverted) ones
        reverted = sorted(k for k in commit_keys if k not in net)
        net_not_in_commits = sorted(k for k in net if k not in commit_keys)
        assert not net_not_in_commits, f'{t}: net change not seen by any first-parent commit: {net_not_in_commits[:5]}'
        transient = sorted(k for k in touched[t] if k not in old and k not in new)
        for k in sorted(net):
            r, shard = new[k]
            prs = sorted(p for p, cols in touched[t][k].items() if cols - {'*deleted*'})
            cols = sorted(net[k], key=lambda c: (list(r).index(c) if c in r else 999)) if net[k] != ['*created*'] else [c for c in r if r[c] != '' and not DERIVED(c)]
            frame.append(dict(table=t, record_id=k, change_kind='created' if k in c else 'changed', prs=';'.join(map(str, prs)),
                              pr_columns=json.dumps({str(p): sorted(touched[t][k][p] - {'*deleted*'}) for p in prs}, sort_keys=True),
                              changed_columns=';'.join(cols), shard=shard,
                              # kept in the frame (brief names only tier1_qualifier*); flagged so the owner can rule it out
                              derived_rollup_only=str(t == 'ecosystem' and k not in c and not set(cols) - {'last_verified'} - ROLLUP).lower()))
        ids = [key_of(t, r) for r, _ in new.values()]
        assert len(ids) == len(set(ids)), f'{t}: record ids not unique at HEAD'
        prov_tables[t] = dict(base_rows=len(old), head_rows=len(new), created=len(c), changed_nonderived=len(ch), frame=len(net),
                              derived_only_excluded=len(d_only), deleted_not_in_frame=len(dele), shard_move_only_excluded=len(moves),
                              touched_then_reverted=len(reverted), created_then_deleted=len(transient),
                              deleted_ids=sorted(dele), reverted_ids=reverted, transient_ids=transient,
                              prs_touching_record_sum=sum(len(touched[t][k]) for k in net))
    # out-of-scope tables that changed in the window (reported, not framed)
    ev_old, ev_new = ({r['event_id']: r for r in rows_at(ref, 'data/events.csv')} for ref in (BASE, HEAD))
    il_old, il_new = (rows_at(ref, 'data/inclusion_log.csv') for ref in (BASE, HEAD))
    out_of_scope = dict(events=dict(base_rows=len(ev_old), head_rows=len(ev_new), rows_with_pic_events_slug_set_in_window=sum(1 for k in ev_new if ev_new[k].get('pic_events_slug', '') != ev_old.get(k, {}).get('pic_events_slug', '')),
                                  rows_with_other_value_change=sum(1 for k in ev_new if k in ev_old and any(ev_old[k].get(c, '') != v for c, v in ev_new[k].items() if c != 'pic_events_slug'))),
                        inclusion_log=dict(base_rows=len(il_old), head_rows=len(il_new), appended_rows=len([r for r in il_new if r not in il_old]), removed_rows=len([r for r in il_old if r not in il_new])))
    # ID-namespace collision check between organizations and ecosystem (both ORG- ids)
    eco = {r['org_id'] for r, _ in load(HEAD, table_files(HEAD)['ecosystem'], 'ecosystem').values()}
    org = {r['org_id'] for r, _ in load(HEAD, table_files(HEAD)['organizations'], 'organizations').values()}
    assert not eco & org, 'org_id appears in both ecosystem and organizations'
    assert all(prov_tables[t]['frame'] > 0 for t in prov_tables if t != 'relationships'), 'a table that git shows as changed came out empty'
    keyed = [(r['table'], r['record_id']) for r in frame]
    assert len(keyed) == len(set(keyed)), 'duplicate (table, record_id) in frame'
    pr_rows = [dict(pr=pr, table=t, kind=kind, records=n) for (pr, t, kind), n in sorted(per_pr.items())]
    prov = dict(base=BASE, head=HEAD, first_parent_commits=len(commits), prs=sorted(set(pr_of_commit.values())),
                commit_to_pr={s[:7]: p for s, p in pr_of_commit.items()}, tables=prov_tables, frame_total=len(frame),
                out_of_scope_tables=out_of_scope, per_pr_per_table=pr_rows, data_files_changed_outside_frame_tables=dict(other_data_files),
                derived_only_by_pr_table=[dict(pr=p, table=t, records=n) for (p, t), n in sorted(derived_only.items())],
                unit='record: one row at HEAD, keyed by table ID (people_identifiers: person_id+identifier_type+identifier_id), created or changed in a non-derived column by a first-parent commit in BASE..HEAD',
                excluded='tier1_qualifier* columns (derived, AGENTS section 1); evidence_*.csv appends (not a frame table); deleted rows (no current value to audit)')
    return sorted(frame, key=lambda r: (list(TABLES).index(r['table']), r['record_id'])), prov


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
    print('PASS frame reproduces from git;', len(frame), 'records;', {t: v['frame'] for t, v in prov['tables'].items()})
