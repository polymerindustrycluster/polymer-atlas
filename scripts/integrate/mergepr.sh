#!/bin/bash
# mergepr.sh <pr> <approved-head> <validated-pushed-head>
# MERGE_MODE=squash keeps a branch's private history off main (DECISIONS 2026-11-17); default merge.
set -euo pipefail
PR=$1; AH=$2; WANT=$3
MODE=${MERGE_MODE-merge}  # only an unset variable defaults; an empty one is refused
case "$MODE" in merge|squash) ;; *) echo "MERGE_MODE must be merge or squash, not '$MODE'" >&2; exit 2 ;; esac
R=$(git rev-parse --show-toplevel); S=$(cd "$(dirname "$0")" && pwd)
cd "$R"
git fetch -q origin main "+refs/pull/$PR/head:refs/remotes/pr/$PR"
GOT=$(git rev-parse "pr/$PR")
# GitHub can serve a stale refs/pull/N/head (2026-11-19, #401); fail loudly, never silently under set -e
[ "$GOT" = "$WANT" ] || { echo "mergepr: pr/$PR is $GOT, not the validated head $WANT. If the branch head is $WANT, GitHub's pull ref is stale: push an empty commit and re-run." >&2; exit 1; }
python3 "$S/delta_compare.py" "$AH" "$WANT"
git diff --exit-code "$AH" "$WANT" -- . ':(exclude)data' ':(exclude)tasks/*/receipts*'
"$S/premerge.sh" "$PR" "$WANT"
if [ "$(gh pr view "$PR" --json isDraft --jq .isDraft)" = true ]; then gh pr ready "$PR"; fi
gh pr merge "$PR" --"$MODE" --match-head-commit "$WANT"
[ "$(gh pr view "$PR" --json state --jq .state)" = MERGED ] || { echo 'GitHub has not reported MERGED'; exit 4; }
if [ -n "${INTEGRATOR_LEDGER:-}" ]; then printf '%s MERGED #%s approved=%s head=%s\n' "$(date)" "$PR" "$AH" "$WANT" >> "$INTEGRATOR_LEDGER"; fi
echo "merged #$PR at $WANT"
