#!/bin/bash
# ci_merge.sh <pr> <approved-head>: bounded wait for validate on the pushed branch tip.
set -euo pipefail
PR=$1; AH=$2; S=$(cd "$(dirname "$0")" && pwd)
cd "$(git rev-parse --show-toplevel)"
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
BR=$(gh pr view "$PR" --json headRefName --jq .headRefName)
WANT=$(git ls-remote origin "refs/heads/$BR" | cut -f1)
[ -n "$WANT" ]
END=$(( $(date +%s) + ${INTEGRATOR_TIMEOUT:-3600} ))
while [ "$(date +%s)" -lt "$END" ]; do
  HEAD=$(gh pr view "$PR" --json headRefOid --jq .headRefOid)
  [ "$HEAD" = "$WANT" ] || { sleep 10; continue; }
  STATE=$(gh api "repos/$REPO/commits/$WANT/check-runs?check_name=validate" --jq '[.check_runs[] | select(.name=="validate")] | sort_by(.id) | last | if .status=="completed" then .conclusion else "pending" end')
  case "$STATE" in
    success) "$S/mergepr.sh" "$PR" "$AH" "$WANT"; exit $? ;;
    pending|null) sleep 20 ;;
    *) echo "validate=$STATE for $WANT"; exit 6 ;;
  esac
done
echo "Timed out waiting for validate on $WANT"; exit 7
