"""Small real Git repositories exercise approved deltas and replay refusals."""
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
