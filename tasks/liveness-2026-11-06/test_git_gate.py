"""Known-answer Git masking regressions; never edits Atlas data."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from git_gate import assert_data_unchanged

class GitGateTests(unittest.TestCase):
    def test_git_states(self):
        for case in ['clean','committed_masked','staged_masked','working','untracked']:
            with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
                def git(*args):
                    return subprocess.run(['git',*args],cwd=d,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                git('init');git('config','user.name','Gate Test');git('config','user.email','gate@example.invalid')
                data=Path(d)/'data';data.mkdir();f=data/'example.csv';f.write_text('status\nactive\n')
                git('add','.');git('commit','-m','base');git('update-ref','refs/remotes/origin/main','HEAD')
                if case=='untracked':(data/'new.csv').write_text('status\nclosed\n')
                elif case!='clean':
                    f.write_text('status\nclosed\n')
                    if case in ('committed_masked','staged_masked'):
                        git('add','data/example.csv')
                        if case=='committed_masked':git('commit','-m','mutation')
                        f.write_text('status\nactive\n')
                if case=='clean':assert_data_unchanged(d)
                else:
                    with self.assertRaises((subprocess.CalledProcessError,AssertionError)):assert_data_unchanged(d)

if __name__=='__main__':unittest.main()
