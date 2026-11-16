#!/bin/bash
# mergepr.sh <pr> <approved-head> <validated-pushed-head>
set -euo pipefail
PR=$1; AH=$2; WANT=$3
R=$(git rev-parse --show-toplevel); S=$(cd "$(dirname "$0")" && pwd)
cd "$R"
git fetch -q origin main "+refs/pull/$PR/head:refs/remotes/pr/$PR"
[ "$(git rev-parse "pr/$PR")" = "$WANT" ]
python3 "$S/delta_compare.py" "$AH" "$WANT"
git diff --exit-code "$AH" "$WANT" -- . ':(exclude)data' ':(exclude)tasks/*/receipts*'
"$S/premerge.sh" "$PR" "$WANT"
if [ "$(gh pr view "$PR" --json isDraft --jq .isDraft)" = true ]; then gh pr ready "$PR"; fi
gh pr merge "$PR" --merge --match-head-commit "$WANT"
[ "$(gh pr view "$PR" --json state --jq .state)" = MERGED ] || { echo 'GitHub has not reported MERGED'; exit 4; }
if [ -n "${INTEGRATOR_LEDGER:-}" ]; then printf '%s MERGED #%s approved=%s head=%s\n' "$(date)" "$PR" "$AH" "$WANT" >> "$INTEGRATOR_LEDGER"; fi
echo "merged #$PR at $WANT"
