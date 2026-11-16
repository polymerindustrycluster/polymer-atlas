"""Regression from Codex clerk PR #357 refutation; all remote commands stubbed."""
import pathlib,tempfile,os,subprocess
repo=pathlib.Path.cwd()
with tempfile.TemporaryDirectory() as td:
 p=pathlib.Path(td)
 (p/'git').write_text('''#!/bin/bash
case "$1" in
rev-parse) if [ "$2" = --show-toplevel ]; then printf '%s\\n' "$TEST_REPO"; else echo lane-head; fi ;;
merge-base) exit 1 ;;
merge-tree) echo merged-tree ;;
commit-tree) echo synced-head ;;
worktree) if [ "$2" = add ]; then mkdir -p "${@: -2:1}"; fi ;;
push) printf 'ATTEMPTED git'; printf ' %s' "$@"; printf '\\n'; ;;
esac
exit 0
''')
 (p/'gh').write_text('#!/bin/bash\necho main\n')
 (p/'python3').write_text('#!/bin/bash\nexit 0\n')
 for f in p.iterdir():f.chmod(0o755)
 env=dict(os.environ,PATH=str(p)+':'+os.environ['PATH'],TEST_REPO=str(repo))
 r=subprocess.run(['bash','scripts/integrate/sync_pr.sh','999','approved-head'],env=env,text=True,capture_output=True)
 print('All Git/GitHub/Python calls stubbed. No remote operation executed.');print(r.stdout);print(r.stderr);print('exit',r.returncode)
 assert r.returncode != 0
 assert 'ATTEMPTED git push' not in r.stdout
