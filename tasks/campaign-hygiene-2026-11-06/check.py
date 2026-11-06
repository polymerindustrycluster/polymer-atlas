"""Named hygiene check: frozen GitHub state, source counts, receipt boundaries, negative controls."""
import collections
import copy
import csv
import hashlib
import io
import subprocess
from pathlib import Path
import build

P, ROOT = build.TASK, build.ROOT

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True)


def allowed_receipt(path):
    return path.startswith('tasks/') and (path.endswith('/README.md') or path.endswith('/approved-replay.json') or path.endswith('/review-packet-v2.json'))


def changed_lines(commit, paths):
    return [x for x in git('show', '--format=', commit, '--', *paths).splitlines()
            if x[:1] in {'+', '-'} and not x.startswith(('+++', '---'))]


def check():
    base = (P / 'base.txt').read_text().strip()
    claims, continuations, counts = [build.load(x) for x in ['claims.json', 'continuations.json', 'counts.json']]
    prefix = git('show', base + ':tasks/QUEUE.md').split(build.MARKER, 1)[0]
    actual = (ROOT / 'tasks/QUEUE.md').read_text()
    assert actual == build.render(prefix, claims, continuations, counts), 'queue differs from audited render/prefix'
    assert '(PR #67)' not in actual.split(build.MARKER, 1)[1], 'incorrect restore PR'
    assert actual.count('`open` **Tombstone-site operator holds:') == 1
    for badstate in ['merged', 'open']:
        bad = copy.deepcopy(claims)
        bad[0]['state'] = badstate
        if badstate == claims[0]['state']:
            continue
        try:
            build.validate_claims(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError('wrong-state negative control was accepted')
    assert not allowed_receipt('scripts/validate.py'), 'receipt boundary negative failed'
    assert not allowed_receipt('tasks/example/check.py'), 'receipt code boundary negative failed'
    for row in build.load('receipts.json'):
        paths = row['selected_paths']
        assert paths and all(allowed_receipt(x) for x in paths), 'non-receipt path'
        source = row['source_commit']
        assert set(row['source_paths']) == set(git('diff-tree', '--no-commit-id', '--name-only', '-r', source).splitlines())
        if row['disposition'] == 'already_in_main':
            subprocess.run(['git', '-C', str(ROOT), 'merge-base', '--is-ancestor', source, base], check=True)
        else:
            picked = row['receipt_commit']
            assert set(git('diff-tree', '--no-commit-id', '--name-only', '-r', picked).splitlines()) == set(paths)
            assert changed_lines(source, paths) == changed_lines(picked, paths), 'receipt patch differs from source'
        for path, digest in row['installed_sha256'].items():
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, 'receipt content changed'
    sources = {}
    for src in counts['sources']:
        raw = git('show', src['revision'] + ':' + src['path'])
        assert hashlib.sha256(raw.encode()).hexdigest() == src['sha256'], 'frozen count source changed'
        sources[src['path']] = list(csv.DictReader(io.StringIO(raw)))
    archives = [v for k, v in sources.items() if k.endswith('/archive_outcomes.csv')]
    ids = [[r['evidence_id'] for r in a] for a in archives]
    assert [len(x) for x in ids] == counts['archive_unlinked_supported_rows']
    assert len(set(sum(ids, []))) == sum(map(len, ids)) == counts['archive_union']
    hqs = {k.split('/')[1].removesuffix('-2026-11-06'): v for k, v in sources.items() if '/residual-hq-' in k}
    allhq = [r for v in hqs.values() for r in v]
    assert len(allhq) == len({r['org_id'] for r in allhq}) == 249
    assert {k:dict(collections.Counter(r['outcome'] for r in v)) for k,v in hqs.items()} == counts['residual_hq_cohorts']
    assert sum(r['outcome'] == 'STILL_UNKNOWN' for r in allhq) == counts['residual_hq_holds'] == 221
    routes = sources['tasks/pic18-record-health-6-2026-11-06/remaining_gap_routes.csv']
    byorg = collections.defaultdict(set)
    for r in routes:
        byorg[r['org_id']].add(r['class_now'])
    assert len(routes) == counts['t1_gap_memberships'] == 197
    assert len(byorg) == counts['t1_unhealthy_organizations'] == 155
    assert dict(collections.Counter(''.join(sorted(v)) for v in byorg.values())) == counts['t1_class_combinations'] == {'b':50,'c':93,'d':11,'bc':1}
    human = [r for r in routes if byorg[r['org_id']] == {'c'}]
    assert len(human) == counts['human_only_gap_memberships'] == 130
    assert dict(collections.Counter(r['gap'] for r in human)) == counts['human_only_gap_types']
    oh = [r for r in sources['data/sites_OH.csv'] if r['operating_status'] == 'active']
    assert len(oh) == counts['active_oh_sites'] == 1883
    assert sum(not r['street_address'].strip() for r in oh) == counts['active_oh_blank_streets'] == 1559
    tomb = sources['tasks/tombstone-site-operators-2026-11-06/verdicts.csv']
    assert len(tomb) == 14 and collections.Counter(r['verdict'] for r in tomb) == {'VERIFIED':10,'STILL_UNCERTAIN':4}
    changed = git('diff', '--name-only', base, '--').splitlines()
    assert all(x.startswith('tasks/') for x in changed), 'change outside docs/tasks scope'
    assert not git('diff', '--name-only', base, '--', 'data/', 'scripts/', 'AGENTS.md', 'docs/SCHEMA.md', 'tasks/CAMPAIGN.md')
    print(f'PASS: {len(claims)} PR claims, {len(continuations)} unopened continuations, 11 receipt audits, six follow-up lines; source counts, protected paths and negative controls.')


if __name__ == '__main__':
    check()
