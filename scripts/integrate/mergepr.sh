#!/bin/bash
# mergepr.sh <pr> <approved-head> <validated-pushed-head>
# MERGE_MODE=squash keeps a branch's private history off main (DECISIONS 2026-11-17); default merge.
set -euo pipefail
PR=$1; AH=$2; WANT=$3
MODE=${MERGE_MODE:-merge}
case "$MODE" in merge|squash) ;; *) echo "MERGE_MODE must be merge or squash, not '$MODE'" >&2; exit 2 ;; esac
R=$(git rev-parse --show-toplevel); S=$(cd "$(dirname "$0")" && pwd)
cd "$R"
git fetch -q origin main "+refs/pull/$PR/head:refs/remotes/pr/$PR"
[ "$(git rev-parse "pr/$PR")" = "$WANT" ]
python3 "$S/delta_compare.py" "$AH" "$WANT"
git diff --exit-code "$AH" "$WANT" -- . ':(exclude)data' ':(exclude)tasks/*/receipts*'
"$S/premerge.sh" "$PR" "$WANT"
if [ "$(gh pr view "$PR" --json isDraft --jq .isDraft)" = true ]; then gh pr ready "$PR"; fi
gh pr merge "$PR" --"$MODE" --match-head-commit "$WANT"
[ "$(gh pr view "$PR" --json state --jq .state)" = MERGED ] || { echo 'GitHub has not reported MERGED'; exit 4; }
if [ -n "${INTEGRATOR_LEDGER:-}" ]; then printf '%s MERGED #%s (%s) approved=%s head=%s\n' "$(date)" "$PR" "$MODE" "$AH" "$WANT" >> "$INTEGRATOR_LEDGER"; fi
echo "merged #$PR at $WANT"
