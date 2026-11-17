#!/bin/bash
# merge_queue.sh <queue-file>: serial queue of "PR approved-head" lines. Stop on failure.
set -euo pipefail
Q=$1; S=$(cd "$(dirname "$0")" && pwd)
while read -r PR AH; do
  [ -n "$PR" ] || continue
  if [ "$(gh pr view "$PR" --json state --jq .state)" != MERGED ]; then
    "$S/sync_pr.sh" "$PR" "$AH"
    "$S/ci_merge.sh" "$PR" "$AH"
  fi
  printf '%s %s\n' "$PR" "$AH" >> "$Q.done"
done < "$Q"
