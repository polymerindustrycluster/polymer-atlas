#!/bin/bash
# sync_pr.sh <pr> <approved-sha>
set -euo pipefail
PR=$1; AH=$2
R=$(git rev-parse --show-toplevel); S=$(cd "$(dirname "$0")" && pwd)
cd "$R"
source "$S/push_guard.sh"
BR=$(gh pr view "$PR" --json headRefName --jq .headRefName)
guard_pr_push "$PR" "$AH:refs/heads/$BR"
git fetch -q origin main "+refs/pull/$PR/head:refs/remotes/pr/$PR"
H=$(git rev-parse "refs/remotes/pr/$PR^{commit}")
W=$(mktemp -d); rmdir "$W"
trap 'git -C "$R" worktree remove --force "$W" 2>/dev/null || true' EXIT
if git merge-base --is-ancestor origin/main "$H"; then NEW=$H
else
  if T=$(git merge-tree --write-tree origin/main "$H" 2>/dev/null); then :
  else
    MB=$(git merge-base origin/main "$H")
    git worktree add -q --detach "$W" origin/main
    git diff --binary "$MB" "$H" -- . ':(exclude)data' > "$W/lane.patch"
    if [ -s "$W/lane.patch" ]; then git -C "$W" apply --3way --index "$W/lane.patch"; fi
    rm "$W/lane.patch"
    python3 "$S/cell_replay.py" "$H" "$W"
    git -C "$W" add data
    T=$(git -C "$W" write-tree)
    git worktree remove --force "$W"
  fi
  NEW=$(git commit-tree "$T" -p "$H" -p origin/main -m "Merge origin/main into $BR (approved cell delta preserved)")
fi
python3 "$S/delta_compare.py" "$AH" "$NEW"
# Data identity alone cannot carry approval over changed code or packets.
git diff --exit-code "$AH" "$H" -- . ':(exclude)data' ':(exclude)tasks/*/receipts*'
git worktree add -q --detach "$W" "$NEW"
(cd "$W"; python3 scripts/validate.py; python3 scripts/check_row_loss.py --base origin/main)
if [ "$NEW" != "$H" ]; then push_pr_head "$PR" "$NEW:refs/heads/$BR"; fi
printf 'Synced #%s at %s\n' "$PR" "$NEW"
