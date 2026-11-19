#!/bin/bash
# premerge.sh <pr> [expected-head]
set -euo pipefail
R=$(git rev-parse --show-toplevel); PR=$1
cd "$R"
git fetch -q origin main "+refs/pull/$PR/head:refs/remotes/pr/$PR"
H=$(git rev-parse "refs/remotes/pr/$PR^{commit}")
[ -z "${2:-}" ] || [ "$H" = "$2" ]
W=$(mktemp -d); rmdir "$W"
trap 'git -C "$R" worktree remove --force "$W" 2>/dev/null || true' EXIT
git worktree add -q --detach "$W" origin/main
cd "$W"
git -c user.email=ci@local -c user.name=premerge merge -q --no-edit "$H"
python3 scripts/validate.py
python3 scripts/check_row_loss.py --base origin/main
