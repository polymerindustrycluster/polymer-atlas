"""Small real Git repositories exercise approved deltas and replay refusals."""
import os
import csv
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).parent / 'integrate'
sys.path.insert(0, str(TOOLS))
from delta_compare import delta, git
from cell_replay import replay


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.r = Path(self.tmp.name)
        git(self.r, 'init', '-q')
        git(self.r, 'config', 'user.email', 'test@example.invalid')
        git(self.r, 'config', 'user.name', 'Test')
        (self.r / 'data').mkdir()
        self.write('sites_OH.csv', 'site_id,name,notes\nS1,old,base\n')
        self.commit('base')
        git(self.r, 'update-ref', 'refs/remotes/origin/main', 'HEAD')

    def write(self, name, text):
        (self.r / 'data' / name).write_text(text)

    def commit(self, message):
        git(self.r, 'add', '.')
        git(self.r, 'commit', '-qm', message)
        return git(self.r, 'rev-parse', 'HEAD').strip()

    def lane(self):
        self.write('sites_OH.csv', 'site_id,name,notes\nS1,new,base\n')
        return self.commit('lane')

    def test_identical_subset_and_value_diff(self):
        a = self.lane()
        self.assertEqual(delta(self.r, a), delta(self.r, 'HEAD'))
        self.write('sites_OH.csv', 'site_id,name,notes\nS1,new,extra\n')
        b = self.commit('more')
        self.assertLess(delta(self.r, a).items(), delta(self.r, b).items())
        self.write('sites_OH.csv', 'site_id,name,notes\nS1,other,base\n')
        c = self.commit('different')
        self.assertNotEqual(delta(self.r, a), delta(self.r, c))
        proc = subprocess.run([sys.executable, str(TOOLS.resolve() / 'delta_compare.py'), a, c], cwd=self.r, capture_output=True)
        self.assertEqual(proc.returncode, 1)

    def test_value_basis_delta_uses_composite_key_and_rejects_duplicates(self):
        name = 'value_basis.csv'
        header = 'record_table,record_id,field,value,basis,evidence_id,basis_date\n'
        first = 'organizations,ORG-000001,processes,injection_molding,not_yet_checked,,\n'
        second = 'organizations,ORG-000001,processes,extrusion,not_yet_checked,,\n'
        self.write(name, header + first + second)
        self.commit('value basis base')
        git(self.r, 'update-ref', 'refs/remotes/origin/main', 'HEAD')

        edited = second.replace('not_yet_checked', 'implied')
        self.write(name, header + edited + first)
        head = self.commit('one basis changed')
        key = (name, ('organizations', 'ORG-000001', 'processes', 'extrusion'))
        self.assertEqual(delta(self.r, head), {(key, 'basis'): 'implied'})

        self.write(name, header + first + second + edited)
        duplicate = self.commit('duplicate basis key')
        with self.assertRaisesRegex(ValueError, r"value_basis\.csv: duplicate key .*extrusion"):
            delta(self.r, duplicate)

    def test_replay_preserves_other_cells_and_refuses_concurrent_cell(self):
        a = self.lane()
        self.write('sites_OH.csv', 'site_id,name,notes\nS1,old,main-note\n')
        replay(a, self.r)
        self.assertIn('S1,new,main-note', (self.r / 'data/sites_OH.csv').read_text())
        self.write('sites_OH.csv', 'site_id,name,notes\nS1,main,main-note\n')
        before = (self.r / 'data/sites_OH.csv').read_bytes()
        with self.assertRaisesRegex(ValueError, 'main changed'):
            replay(a, self.r)
        self.assertEqual(before, (self.r / 'data/sites_OH.csv').read_bytes())

    def test_composite_key_append(self):
        for name, header, first, second in (
            ('registry_links.csv', 'org_id,registry,registry_id,site_id', 'O1,R,1,S1', 'O1,R,1,S2'),
            ('people_identifiers.csv', 'person_id,identifier_type,identifier_id', 'P1,R,1', 'P1,R,2')):
            self.write(name, f'{header}\n{first}\n')
            self.commit('composite base')
            git(self.r, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
            self.write(name, f'{header}\n{first}\n{second}\n')
            a = self.commit('append')
            self.assertEqual(len(delta(self.r, a)), 1)
            self.write(name, f'{header}\n{first}\n')
            replay(a, self.r)
            self.assertEqual((self.r / 'data' / name).read_text(), f'{header}\n{first}\n{second}\n')

    def test_header_row_removal_and_collision_refusals(self):
        a = self.lane()
        self.write('sites_OH.csv', 'site_id,renamed,notes\nS1,old,base\n')
        with self.assertRaisesRegex(ValueError, 'header drift'):
            replay(a, self.r)
        self.write('sites_OH.csv', 'site_id,name,notes\n')
        deleted = self.commit('delete')
        with self.assertRaisesRegex(ValueError, 'rows removed'):
            replay(deleted, self.r)
        self.write('sites_OH.csv', 'site_id,name,notes\nS1,old,base\nS2,new,base\n')
        appended = self.commit('append')
        with self.assertRaisesRegex(ValueError, 'already on main'):
            replay(appended, self.r)

    def test_inclusion_log_uses_whole_row_and_occurrence(self):
        self.write('inclusion_log.csv', 'date,entity,notes\n2026-11-16,A,x\n2026-11-16,A,x\n')
        self.commit('log base')
        git(self.r, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
        self.write('inclusion_log.csv', 'date,entity,notes\n2026-11-16,A,x\n2026-11-16,A,x\n2026-11-16,B,y\n')
        a = self.commit('log append')
        self.assertEqual(len(delta(self.r, a)), 1)
        self.write('inclusion_log.csv', 'date,entity,notes\n2026-11-16,A,x\n2026-11-16,A,x\n')
        replay(a, self.r)
        self.assertIn('2026-11-16,B,y', (self.r / 'data/inclusion_log.csv').read_text())


class MergeModeTests(unittest.TestCase):
    def test_unknown_merge_mode_is_refused_before_any_git_or_gh_call(self):
        with tempfile.TemporaryDirectory() as temp:
            root, log = Path(temp), Path(temp) / 'calls.log'
            for tool in ('git', 'gh'):
                (root / tool).write_text(f'#!/bin/bash\necho {tool} "$*" >> "{log}"\n')
                (root / tool).chmod(0o755)
            for mode in ('rebase', ''):  # an explicitly empty mode must not fall back to merge
                env = {**os.environ, 'PATH': f"{root}:{os.environ['PATH']}", 'MERGE_MODE': mode}
                r = subprocess.run(['bash', str(TOOLS.resolve() / 'mergepr.sh'), '1', 'a' * 40, 'b' * 40],
                                   env=env, capture_output=True, text=True)
                self.assertEqual(r.returncode, 2, f'{mode!r}: {r.stderr}')
                self.assertIn('MERGE_MODE must be merge or squash', r.stderr)
                self.assertFalse(log.exists(), 'no git or gh call may happen before the mode is checked')

    def test_both_modes_keep_the_approved_head_check(self):
        text = (TOOLS / 'mergepr.sh').read_text()
        self.assertIn('gh pr merge "$PR" --"$MODE" --match-head-commit "$WANT"', text)


class PushGuardTests(unittest.TestCase):
    def test_reviewer_repro_refuses_main_without_pushing(self):
        result = subprocess.run([sys.executable, str(TOOLS.resolve() / 'repro_main_push.py')],
                                cwd=TOOLS.resolve().parents[1], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('ATTEMPTED git push', result.stdout)

    def test_push_destinations_and_force_refusals(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'git').write_text("""#!/bin/bash
case "$1" in
ls-remote) [ "$TEST_DEFAULT" = unknown ] || printf 'ref: refs/heads/%s\tHEAD\n' "$TEST_DEFAULT" ;;
push) printf '%s\n' "$*" >> "$TEST_PUSH_LOG" ;;
esac
""")
            (root / 'gh').write_text("""#!/bin/bash
case "$*" in
*isCrossRepository*) echo "$TEST_FORK" ;;
*headRefName*) echo "$TEST_BRANCH" ;;
esac
""")
            for name in ('git', 'gh'):
                (root / name).chmod(0o755)
            log = root / 'push.log'
            env = dict(os.environ, PATH=str(root) + ':' + os.environ['PATH'],
                       TEST_PUSH_LOG=str(log), TEST_DEFAULT='trunk',
                       TEST_FORK='false', TEST_BRANCH='lane')
            command = 'source "$1"; shift; push_pr_head "$@"'
            cases = [
                ('main', 'main', 'head:refs/heads/main'),
                ('trunk', 'trunk', 'head:refs/heads/trunk'),
                ('trunk', 'topic/main', 'head:refs/heads/topic/main'),
                ('trunk', 'topic/trunk', 'head:refs/heads/topic/trunk'),
                ('trunk', 'lane', 'head:refs/heads/other'),
                ('trunk', 'lane', '+head:refs/heads/lane'),
                ('trunk', 'lane', '--force'),
                ('trunk', 'lane', ':refs/heads/lane'),
                ('unknown', 'lane', 'head:refs/heads/lane'),
            ]
            for default, branch, spec in cases:
                with self.subTest(default=default, branch=branch, spec=spec):
                    r = subprocess.run(['bash', '-c', command, 'test', str(TOOLS.resolve() / 'push_guard.sh'), '1', spec],
                                       env=dict(env, TEST_DEFAULT=default, TEST_BRANCH=branch), capture_output=True)
                    self.assertNotEqual(r.returncode, 0)
                    self.assertFalse(log.exists())
            for fork in ('true', ''):
                r = subprocess.run(['bash', '-c', command, 'test', str(TOOLS.resolve() / 'push_guard.sh'),
                                    '1', 'head:refs/heads/lane'], env=dict(env, TEST_FORK=fork), capture_output=True)
                self.assertNotEqual(r.returncode, 0)
                self.assertFalse(log.exists())
            r = subprocess.run(['bash', '-c', command, 'test', str(TOOLS.resolve() / 'push_guard.sh'),
                                '1', 'head:refs/heads/lane', '--force'], env=env, capture_output=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse(log.exists())
            r = subprocess.run(['bash', '-c', command, 'test', str(TOOLS.resolve() / 'push_guard.sh'),
                                '1', 'head:refs/heads/lane'], env=env, capture_output=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(log.read_text().strip(), 'push --no-follow-tags origin head:refs/heads/lane')
