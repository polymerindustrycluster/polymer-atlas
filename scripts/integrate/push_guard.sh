#!/bin/bash
# Source this file; every automated push goes through push_pr_head.
guard_pr_push() {
  [ "$#" -eq 2 ] || return 1
  local pr=$1 spec=$2 target default branch
  case "$spec" in :*|*:*:*|+*|-*|*[[:space:]]*) echo "Refusing force/options/multiple refspecs" >&2; return 1 ;; esac
  case "$spec" in *:*) target=${spec#*:} ;; *) echo "Explicit destination required" >&2; return 1 ;; esac
  default=$(git ls-remote --symref origin HEAD | awk '$1=="ref:" && $3=="HEAD" {sub("^refs/heads/", "", $2); print $2}')
  [ -n "$default" ] || { echo "Cannot resolve origin default branch" >&2; return 1; }
  case "$target" in main|*/main|"$default"|*/"$default")
    echo "Refusing protected branch: $target" >&2; return 1 ;;
  esac
  [ "$(gh pr view "$pr" --json isCrossRepository --jq .isCrossRepository)" = false ] || {
    echo "Refusing fork or unknown head repository" >&2; return 1;
  }
  branch=$(gh pr view "$pr" --json headRefName --jq .headRefName)
  [ -n "$branch" ] && [ "$target" = "refs/heads/$branch" ] || {
    echo "Destination must be the PR's own head branch" >&2; return 1;
  }
  git check-ref-format "$target"
}

push_pr_head() {
  guard_pr_push "$@" || return 1
  # No caller-supplied flags: this is always one ordinary, non-force push.
  git push --no-follow-tags origin "$2"
}
