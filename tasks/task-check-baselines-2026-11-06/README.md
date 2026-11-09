# Task-check baselines (2026-11-06)

Lane: `atlas-task-check-baselines` (Claude, bb child of thr_9i2c6byhcz). Branch `agent/claude-code/task-check-baselines`.
No `data/` file, task result, verdict or builder is changed. Units below: **task checks** = `tasks/*/check.py` files.

## What changed

1. **`scripts/run_task_checks.py`** (new; test `scripts/test_run_task_checks.py`). A check pins numbers and commits that
   later merges legitimately move, so it cannot be judged on today's main. The runner finds, per task, the first-parent
   merge that added `check.py`, then runs it in a throwaway `git clone --shared` at the state its author validated:
   the PR branch tip (second parent) with `origin/main` set to the merge-base (a direct commit: itself, with `origin/main`
   at its parent). The task's own folder is overlaid from `--ref` (default `origin/main`; `--ref HEAD` tests a PR before
   merge), so a corrected baseline file is the one exercised. `--at head` runs on current `origin/main` for the census.
   No existing runner was found (grep of `scripts/`, `.github/`, task READMEs for `check.py` runners).
   Why the branch tip and not the merge commit: the merge commit failed 30 of 95 because many checks assert
   `git diff <pinned-main> -- data/` is exactly the PR's own files; at the merge commit that diff also contains PRs that
   merged in between. 19 of those 30 pass at the branch tip untouched.
2. **Three baseline files corrected**, each recomputed at the PR's merge parent (journal below).

## Census (units: task checks; `tasks/*/check.py`)

| Run | Passed | Failed |
|---|---|---|
| Current `origin/main` (2b39aa65f), `--at head` | 30 of 96 | 66 |
| Each check at its own pass state, before repairs (tree of 14f134dd9) | 83 of 95 | 12 |
| Same, after the 3 repairs (`--ref HEAD`) | 86 of 95 | 9 |
| Same, on the merged tree f49540cd8 (96 checks) | 84 of 96 | 12 (the 9, plus 3 live-fetch `newsroom-urls*`, see below) |

An earlier head census at 14f134dd9 gave 34 of 95. Of the 66 head failures at 2b39aa65f, 55 pass at their own pass state
(the data is fine, the pins moved) and 11 fail at both. **No real data defect was found.**

## Baseline journal (before / after)

| File | Field | Before | After | How the after value was recomputed |
|---|---|---|---|---|
| `corroborated-ca-3-2026-11-06/qcew_before.json` | `atlas_strict` | 93 | 118 | task's own `atlas_numerators` ('CA','326')[1] at PR #175 merge parent 778c74ccc: 118; at branch tip 93f2d8874: 130 (= 118 + the 12 new 326 sites in `allocations.csv`) |
| `corroborated-ca-4-2026-11-06/qcew_before.json` | `atlas_strict` | 93 | 110 | same function at PR #178 merge parent 47354e126: 110; at tip 864fe9807: 118 (= 110 + 8). #178 merged before #175, hence 110 then 118 |
| `people-titles-3-2026-11-06/base_commit.txt` | commit | 49ddb5ddd (#229 merge) | f57638a07d49 | PR #235 merge parent; the old pin predated people created by PRs that merged before #235, so "title pass created people" fired |

`qcew_result.json` in both CA folders is a recorded result and is left as written (it still shows the 93 base; the check
rewrites it when run in place).

## The 12 that still fail at their own pass state on the merged tree (none is a data defect)

| Task check | Class | Evidence |
|---|---|---|
| corroborated-il-2 | untracked witness | `build.py` asserts the Morris witness exists; README says run `acquire_morris.py` first. Acquired in a sandbox, then `check.py` PASS |
| creation-error-corrections-2 | untracked cache | needs `build/l11-correction2-cache/frozen` (gitignored). `acquire.py` in a sandbox, then `check.py` PASS |
| creation-error-corrections, evidence-repair-3, mi-il-site-quality, pic18-fetch-retry | untracked cache | need gitignored `build/...-cache` pages that exist on no clean clone; no acquire script for them. Not run past the missing file, so any stale pin behind it is unknown |
| strong-wave-site-quality | cache, then stale pin | cache acquired with `acquire.py`, then `git diff BASE -- data` fails: `baseline.json` `base` is both the frame base `build.py` consumes and the check's diff base. Moving it to the merge parent (2fc6c508e) breaks `build.py --apply`, so a baseline-file edit cannot fix it; the check needs a separate diff-base pin |
| evidence-repair-4 | local branch ref | runs `git show agent/codex/evidence-repair-3:...`; passes only in a checkout holding that branch name (it exists in the shared repo here, not in a clone). Replace with the merge SHA |
| markets-certs-tier1-round3, newsroom-urls, newsroom-urls-other, newsroom-urls-pic18 | live network | these re-fetch live pages. round3: nipponpaintamericas.com "unfetchable" on 5 of 6 runs (it passed once, in the head census). The three newsroom checks passed on all three earlier full runs, then returned HTTP 403 on every run after repeated census runs from this machine (likely a bot block caused by the census itself). Availability, not a baseline or data finding; rerun later from a quiet host |

To run the persistent ones, put their caches under the controller's `persist/<task-slug>/` (CONTRACT-CLAUDE) and point the
check there, or commit the small public ones; that is outside this lane.

## Named checks

- `python3 scripts/run_task_checks.py --at pass --ref HEAD` -> 86/95 before merging main (the 9 non-network rows above); 84/96 after (those 9 plus 3 live-fetch 403s).
- `python3 scripts/run_task_checks.py corroborated-ca-3 corroborated-ca-4 people-titles-3 --ref HEAD` -> 3/3 PASS; before the edits the same three FAIL at the same state.
- `python3 -m unittest scripts/test_run_task_checks.py`: a check passes at its pass state and fails on a drifted head; a deliberately broken check fails with its message.
- `python3 scripts/validate.py` 0 errors; `python3 scripts/check_row_loss.py --base origin/main` OK.
