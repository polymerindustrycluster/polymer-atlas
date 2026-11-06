#!/usr/bin/env python3
"""Run every tasks/<slug>/check.py against the tree it was written for, not against today's main.

A task check pins numbers and commits (QCEW numerators, a `git diff <pinned-main> -- data/` base, row
counts) that later merges legitimately move, so on current main it reports baseline drift, not a defect.
Each check is therefore run in a throwaway clone at the state its author validated: for the PR merge that
first added check.py, the branch tip (second parent) with `origin/main` set to the merge-base; for a direct
commit, that commit with `origin/main` set to its parent. The task's own folder is then overlaid from
current origin/main, so a baseline file corrected since the merge is the one exercised. A failure there is a
real defect, a baseline that was already stale when the PR merged, or a file the check needs that was never
committed. `--at head` runs the same checks on current origin/main instead (the census: a check that fails
only there is baseline drift).

    python3 scripts/run_task_checks.py                       # every task, at its own pass
    python3 scripts/run_task_checks.py corroborated-ca-3     # name filter (substring)
    python3 scripts/run_task_checks.py --at head --jobs 8    # census on current origin/main

Exit status is 1 when any check fails or times out. Checks that fetch live URLs can fail on the network alone.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(repo, *args):
    return subprocess.run(['git', *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()


def tasks_with_checks(repo, ref):
    """Slugs whose tasks/<slug>/check.py exists at `ref`."""
    names = git(repo, 'ls-tree', '--name-only', ref, 'tasks/').splitlines()
    return sorted(Path(n).name for n in names
                  if subprocess.run(['git', 'cat-file', '-e', f'{ref}:{n}/check.py'], cwd=repo,
                                    capture_output=True).returncode == 0)


def pass_state(repo, ref, slug):
    """(tree commit, origin/main commit) the check's author validated against."""
    intro = git(repo, 'log', '--first-parent', '--diff-filter=A', '--format=%H', ref, '--', f'tasks/{slug}/check.py').splitlines()[-1]
    parents = git(repo, 'rev-list', '--parents', '-1', intro).split()[1:]
    if len(parents) == 2:
        return parents[1], git(repo, 'merge-base', *parents)
    return intro, parents[0] if parents else intro


def run_one(repo, ref, slug, at, timeout):
    """Return (status, commit, seconds, output tail) for one task's check."""
    tree, base = (ref, ref) if at == 'head' else pass_state(repo, ref, slug)
    tmp = Path(tempfile.mkdtemp(prefix=f'task-check-{slug[:30]}-'))
    start = time.time()
    try:
        git(repo, 'clone', '--shared', '--no-checkout', '--quiet', str(repo), str(tmp / 'repo'))
        clone = tmp / 'repo'
        git(clone, 'update-ref', 'refs/remotes/origin/main', base)
        git(clone, 'checkout', '--quiet', '--detach', tree)
        shutil.rmtree(clone / 'tasks' / slug, ignore_errors=True)
        git(clone, 'checkout', '--quiet', ref, '--', f'tasks/{slug}')
        try:
            p = subprocess.run([sys.executable, f'tasks/{slug}/check.py'], cwd=clone, capture_output=True,
                               text=True, timeout=timeout)
            status, out = ('PASS' if p.returncode == 0 else 'FAIL'), p.stdout + p.stderr
        except subprocess.TimeoutExpired:
            status, out = 'TIMEOUT', f'no result after {timeout}s'
        return status, tree[:9], time.time() - start, '\n'.join(out.strip().splitlines()[-6:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('names', nargs='*', help='only tasks whose slug contains one of these')
    ap.add_argument('--at', choices=['pass', 'head'], default='pass')
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--timeout', type=int, default=900, help='seconds per check')
    ap.add_argument('--repo', type=Path, default=ROOT)
    ap.add_argument('--ref', default='origin/main', help='tree whose task folders are overlaid (use HEAD to test a PR before merge)')
    args = ap.parse_args(argv)
    ref = git(args.repo, 'rev-parse', args.ref)
    slugs = [s for s in tasks_with_checks(args.repo, ref) if not args.names or any(n in s for n in args.names)]
    if not slugs:
        sys.exit('no task check.py matched')
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        results = list(ex.map(lambda s: run_one(args.repo, ref, s, args.at, args.timeout), slugs))
    for slug, (status, commit, secs, tail) in zip(slugs, results):
        print(f'{status:8} {slug} @{commit} {secs:.0f}s')
        if status != 'PASS':
            print('\n'.join('    ' + line for line in tail.splitlines()))
    bad = [s for s, r in zip(slugs, results) if r[0] != 'PASS']
    print(f'{len(slugs) - len(bad)}/{len(slugs)} task checks passed (at {args.at}, ref={ref[:9]})')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
