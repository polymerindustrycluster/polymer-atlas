"""Reject data changes in each Git state, including masked staged/committed edits."""
import subprocess


def assert_data_unchanged(root):
    base=subprocess.check_output(['git','merge-base','HEAD','origin/main'],cwd=root,text=True).strip()
    for args in ([base,'HEAD'],['--cached','HEAD'],[]):
        subprocess.run(['git','diff','--exit-code',*args,'--','data/'],cwd=root,check=True,stdout=subprocess.PIPE)
    assert not subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','data/'],cwd=root,text=True).strip(), 'untracked data files'
