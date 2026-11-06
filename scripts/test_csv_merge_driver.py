import subprocess
import sys
from pathlib import Path

DRIVER = Path(__file__).with_name('csv_merge_driver.py')


def run(tmp_path, base, ours, theirs, name='data/sites_OH.csv'):
    paths = [tmp_path / n for n in ('base', 'ours', 'theirs')]
    for p, content in zip(paths, (base, ours, theirs)):
        p.write_text(content)
    p = subprocess.run([sys.executable, str(DRIVER), *map(str, paths), name], capture_output=True)
    return p.returncode, paths[1].read_text()


def test_merges_and_conflicts(tmp_path):
    b = 'id,value\n1,a\n2,b\n'
    assert run(tmp_path, b, b+'3,c\n', b+'4,d\n') == (0, b+'3,c\n4,d\n')
    assert run(tmp_path, b, 'id,value\n1,x\n2,b\n', 'id,value\n1,a\n2,y\n') == (0, 'id,value\n1,x\n2,y\n')
    for a, t in [('id,value\n1,x\n2,b\n', 'id,value\n1,y\n2,b\n'), ('id,value\n1,a\n', b), ('id,changed\n1,a\n2,b\n', b)]:
        status, output = run(tmp_path, b, a, t)
        assert status == 1 and '<<<<<<<' in output


def test_real_merge(tmp_path):
    path = 'data/evidence_organizations_OH.csv'
    def show(ref):
        return subprocess.check_output(['git', 'show', f'{ref}:{path}'], text=True)
    merge = '09df9e9'
    base = subprocess.check_output(['git', 'merge-base', f'{merge}^1', f'{merge}^2'], text=True).strip()
    status, output = run(tmp_path, show(base), show(f'{merge}^1'), show(f'{merge}^2'), path)
    assert status == 0
    assert output == show(merge)


def test_pipes_and_occurrences(tmp_path):
    header = 'researcher,notes\n'
    base = header + 'alice|team,hello\nalice|team,hello\n'
    replacement = header + 'alice,team|hello\nalice|team,hello\n'
    assert run(tmp_path, base, replacement, base, 'data/inclusion_log.csv')[0] == 1
    header = 'org_id,registry,registry_id,site_id,value\n'
    base = header + 'a|b,c,d,e,old\n'
    replacement = header + 'a,b|c,d,e,old\n'
    assert run(tmp_path, base, replacement, base, 'data/registry_links.csv')[0] == 1


def test_setup_survives_linked_worktree_removal(tmp_path):
    import shutil
    repo = tmp_path / 'repo'
    repo.mkdir()
    def git(*args):
        return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()
    git('init', '-b', 'primary')
    git('config', 'user.name', 'Test')
    git('config', 'user.email', 'test@example.com')
    (repo / 'scripts').mkdir()
    (repo / 'data').mkdir()
    for name in ('csv_merge_driver.py', 'check_row_loss.py', 'setup_merge_driver.sh'):
        shutil.copy(Path(__file__).with_name(name), repo / 'scripts' / name)
    csv_path = repo / 'data' / 'sites_OH.csv'
    csv_path.write_text('id,value\n1,a\n')
    git('add', '.')
    git('commit', '-m', 'base')
    git('branch', 'other')
    csv_path.write_text('id,value\n1,a\n2,b\n')
    git('commit', '-am', 'primary')
    linked = tmp_path / 'linked'
    git('worktree', 'add', '-b', 'setup', str(linked), 'HEAD')
    subprocess.run(['sh', str(linked / 'scripts' / 'setup_merge_driver.sh')], cwd=linked, check=True)
    git('worktree', 'remove', str(linked))
    git('checkout', 'other')
    csv_path.write_text('id,value\n1,a\n3,c\n')
    git('commit', '-am', 'other')
    git('merge', 'primary')
    assert csv_path.read_text() == 'id,value\n1,a\n2,b\n3,c\n'
