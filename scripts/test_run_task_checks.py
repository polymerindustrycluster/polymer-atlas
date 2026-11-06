"""run_task_checks.py: a check passes at its own merge, fails on drifted head, and a broken check still fails."""
import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path

import run_task_checks

GOOD = '''import subprocess
from pathlib import Path
root = Path(__file__).resolve().parents[2]
assert (root / "count.txt").read_text() == "1"
git = lambda *a: subprocess.check_output(["git", *a], cwd=root, text=True).strip()
assert git("rev-parse", "origin/main") == git("rev-parse", "HEAD^1")  # base the PR was written against
'''
BROKEN = 'assert False, "defect"\n'


def git(repo, *args):
    subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=repo, check=True,
                   capture_output=True)


class RunTaskChecks(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        git(self.repo, 'init', '-q', '-b', 'main')
        (self.repo / 'count.txt').write_text('1')
        git(self.repo, 'add', '.')
        git(self.repo, 'commit', '-qm', 'init')
        git(self.repo, 'checkout', '-qb', 'feat')
        for slug, body in [('good', GOOD), ('broken', BROKEN)]:
            (self.repo / 'tasks' / slug).mkdir(parents=True)
            (self.repo / 'tasks' / slug / 'check.py').write_text(body)
        git(self.repo, 'add', '.')
        git(self.repo, 'commit', '-qm', 'tasks')
        git(self.repo, 'checkout', '-q', 'main')
        git(self.repo, 'merge', '-q', '--no-ff', 'feat', '-m', 'Merge pull request #1')
        (self.repo / 'count.txt').write_text('2')  # a later merge moves the number the check pinned
        git(self.repo, 'commit', '-qam', 'later merge')
        git(self.repo, 'update-ref', 'refs/remotes/origin/main', 'main')

    def run_at(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = run_task_checks.main(['--repo', str(self.repo), *argv])
        return code, out.getvalue()

    def test_passes_at_its_pass_state_not_on_drifted_head(self):
        code, out = self.run_at('good', '--at', 'pass')
        self.assertEqual(code, 0, out)
        self.assertIn('PASS     good', out)
        code, out = self.run_at('good', '--at', 'head')
        self.assertEqual(code, 1, out)
        self.assertIn('FAIL     good', out)

    def test_broken_check_fails_at_its_pass_state(self):
        code, out = self.run_at('broken', '--at', 'pass')
        self.assertEqual(code, 1, out)
        self.assertIn('defect', out)


if __name__ == '__main__':
    unittest.main()
