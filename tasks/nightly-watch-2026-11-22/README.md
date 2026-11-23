# Nightly watch on `main` (2026-11-22)

Owner, 2026-11-22: "I'm upset we didn't catch this all sooner." On 2026-11-21 and 22 one harness merged 28 pull requests,
34,094 evidence rows and 6,837 registry links, most before the required check finished, and it was noticed only because
the owner asked for a look. Every safeguard the project had ran inside an agent session, so when no controller session was
awake nothing watched. This is the watch that needs nobody awake: a scheduled GitHub Actions job on `main` that fails
loudly, so GitHub emails the owner, and files one issue as a backstop.

Built by: Claude Code, Anthropic (Claude Sonnet 5.5). Tooling only: nothing under `data/` changes.

## What it checks

`scripts/nightly_watch.py` looks at the last 24 hours on `main` (`--since <hours|date|ref>` and `--until` for a backfill)
and exits 1 on any finding, or 2 when it could not inspect something (an API error, an unreadable file, a shallow
clone, a PR it cannot place on `main`'s history). It always prints what it inspected: window, commits, pull requests,
rows. Constants are at the top of the script.

| | Finding | Threshold or rule |
|---|---|---|
| a | bulk add | more than 1,000 evidence rows under one `created_by` label or by one PR; more than 1,000 registry links by one PR (`registry_links.csv` has no `created_by` column, so links can only be counted per PR) |
| b | no review record | a merged PR that changed `data/` has fewer than 2 comments starting `**Review record**` posted before the merge |
| c | merged before `validate` | the last `validate` check run on the PR head that started before the merge is missing, unfinished at the merge, or not `success`. A PR merged into a merge-train branch is exempt; the train PR that reaches `main` is judged |
| d | red `main` | the latest completed `validate` run on `main` is not `success` |
| e | flat outcome | 3 or more `data/` PRs merged and none of the three PIC-18 unknown counts (process, market, size; the `pic18_unknown.py` definition, copied in) fell between the window's base and head |
| f | no provenance | an evidence row added in the window whose `created_by` label is new and names no folder under `tasks/` (a folder name of 6 or more characters appears inside the label) |
| g | undeclared loss | keyed rows removed from `data/`, or tracked files removed elsewhere, with no new `REMOVALS.csv` entry (it calls `scripts/check_row_loss.py`'s functions, once per first-parent commit) |

Rows are counted per first-parent commit, never as a net window diff, so a batch that is merged and reverted the same day
(#457 and #458, reverted by #465) still counts. Tests: `python3 scripts/test_nightly_watch.py` has one planted case per
finding that must fire, a clean day that must pass, API and shallow-history failures that must fail, a real throwaway git
repo for the row counting and merge-train handling, and the known-answer nights below.

## Backfill (known answer)

Method: the workflow runs at 11:17 UTC (06:17 US Eastern standard time). Each row below is one such run, a 24-hour window
ending at 11:17 UTC on that date, collected live from git and GitHub with the real script on 2026-11-22
(`python3 scripts/nightly_watch.py --since 2026-11-21T11:17Z --until 2026-11-22T11:17Z --save-facts ...`). The facts of
each night are committed in `backfill/` (counts, SHAs and timestamps only); `backfill-output.txt` is the full printed
report of every night, reproducible offline with `python3 scripts/nightly_watch.py --facts backfill/night-<date>.json`.
The last row is the rest of 2026-11-22, up to 23:00 UTC.

| Night ending 11:17 UTC | PRs | of which `data/` | Evidence rows added | Links added | a | b | c | d | e | f | g |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-17 | 20 | 16 | 469 | 577 | · | 16 | · | · | · | · | · |
| 2026-11-18 | 19 | 12 | 513 | 0 | · | 12 | · | · | · | · | · |
| 2026-11-19 | 26 | 16 | 188 | 0 | · | 16 | · | · | · | · | · |
| 2026-11-20 | 20 | 14 | 534 | 0 | · | 14 | 2 | · | · | · | · |
| 2026-11-21 | 18 | 11 | 1,393 | 0 | · | 11 | 4 | · | 1 | 1 | · |
| **2026-11-22** | 16 | 15 | 2,744 | 1,765 | **3** | 15 | **16** | · | **1** | 9 | · |
| 2026-11-22, to 23:00 UTC | 7 | 5 | 34,094 | 6,837 | 5 | 3 | 1 | · | 1 | 4 | · |

(Cells are the number of findings; `·` is none. No run had an inspection error. `main`'s latest `validate` was green in
every window, so d never fired.)

**Incident (2026-11-19 to 11-22).** The watch fires on a, b, c and e on the night ending 2026-11-22 11:17 UTC, the first
night that contains the burn-down batches, and again on the partial day that contains #457 and #458:

- a: `spaghetti-burndown-batch2-2026-11-21` added 1,728 evidence rows, PR #443 alone 1,276, and PR #453 1,765 registry
  links. In the last row, PR #458 adds 23,564 evidence rows and 6,837 links and PR #457 10,530 rows.
- b: every `data/` PR before #460 lacks the two review records (11 of 11, 15 of 15, 3 of 3 in the three incident windows).
  #460, #462, #463 and #465, which carry the convention, come out clean.
- c: all 16 PRs merged in the night ending 11-22 were merged without a finished `validate` on their head: 14 were merged
  2 to 5 minutes before it finished, and #441 and #443 never had a `validate` run on their head. Not every incident PR trips it: #457 and #458, the two
  largest, had a green `validate` that finished before their merge, so c alone would not have caught the 34,094 rows.
- e: 11 data PRs in the night ending 11-21 and 15 in the next, and process/market/size unknowns stayed 322/316/443.

**On which night the owner would first have been emailed.** For the incident itself, the morning of **Sunday 2026-11-22,
06:17 EST** (the run ending 11:17 UTC), about 16.5 hours after #443 merged (2026-11-21 18:51 UTC) and before #457 and #458
existed. That run would have said a, b, c, e and f together, with the numbers. Earlier signals were weaker: **Saturday
2026-11-21 06:17 EST** already carried e (11 `data/` PRs, no PIC-18 unknown count moving), one f and 4 c findings, all from
the evidence-backfill lanes that ran before the burn-down batches, and **Friday 2026-11-20** carried the first c (2).
The next run after the 34,094 rows (Monday 2026-11-23 06:17 EST) would have flagged them even though #465 reverted them
the same day, because rows are counted per commit.

**Quiet window (2026-11-16 to 11-18).** After tuning, the nights ending 11-17, 11-18 and 11-19 (UTC) raise b only; there
is no a, c, d, e, f or g, and no error. b is not a false alarm in the sense of a mistake: the review-record convention
began with the owner rulings of 2026-11-22 (#460), so all 44 `data/` PRs in that window lack it. I did not date-gate b,
because the same rule is what fires on the incident. It will be quiet once every data PR carries two records.

### What I chose, and why

| Finding | Choice | Why (quiet window, 11-16 to 11-18) |
|---|---|---|
| a | 1,000 evidence rows and 1,000 links, unchanged from the brief | the largest legitimate unit in the window was 577 links in one PR and 248 evidence rows under one label; the incident units were 1,276 to 23,564 |
| b | 2 records, no date gate | see above |
| c | **merge-train members exempt** | before this, the window had 5 findings, all PRs merged into the 2026-11-16 and 11-17 merge trains (#347, #350, #351, #353, #354), whose heads never had their own `validate` run because the train PR was validated as a whole. They are false alarms and are no longer judged; the train PR is |
| e | 3 PRs, any non-decrease | silent in the window: the three counts fell every night (342/439/538 to 340/432/445, then 331/383/445, then 324/319/443). It is a "busy but flat" detector, so it also fires on nights of evidence backfill, which does not move those three counts by design |
| f | **new labels only**, via a frozen baseline | 260 of the 356 `created_by` labels on `main` (36,187 of 47,416 evidence rows) never named a `tasks/` folder (`atlas-w16-*`, `lane_A02`, `spaghetti-*`), so the rule as written fired on every night: 7, 9 and 7 labels on the three quiet nights. `label_baseline.txt` freezes the 250 labels present at `248e9409` (2026-11-20 evening, before the burn-down) that name no folder; from then on a new label must name a folder. Regenerate with `python3 scripts/nightly_watch.py --print-label-baseline <ref>`. The freeze point is a judgement: a later one would silence the burn-down labels |
| g | reuse `check_row_loss` as is | no loss in any window. #465 removed rows with quarantine entries and passes |

## What the owner must do so the email reaches them

I cannot see the owner's GitHub settings, so each item below is unverified.

1. **The workflow only runs once it is on `main`.** `schedule` and `workflow_dispatch` triggers do not exist before the
   merge, so the YAML is untested as a workflow in this PR (its script and tests are tested). After the merge, run it once
   by hand: Actions, nightly-watch, Run workflow. It will fail and open the issue if the last 24 hours have findings,
   which proves the whole path.
2. **Who gets the failure email.** GitHub's documentation (Notifications for workflow runs, read 2026-11-22) says
   notifications for scheduled workflows go to the user who initially created the workflow; if a different user later
   edits the cron line, to that user; if the workflow is disabled and re-enabled, to whoever re-enabled it. With one
   shared GitHub account for the agents and the owner, that is the shared account, and so the mailbox on that account.
   Check that mailbox is the one the owner reads, or have the owner's own account make the last edit to the `cron` line.
3. **Notification settings of that account** (github.com, Settings, Notifications, "Actions"): enable Email (or Web and
   Mobile) and choose "Send notifications for failed workflows only". Check the account's notification email address and
   that it is verified.
4. **The issue backstop.** A failed run opens one issue titled "Nightly watch: findings" and later failures comment on it
   (a comment emails everyone subscribed). Watch the repository for Issues (Watch, Custom, Issues) so that email arrives
   even if item 2 goes wrong. The workflow does not close the issue; the owner closes it when the findings are handled.
5. GitHub may delay a scheduled run under load and disables schedules after 60 days without repository activity. The
   watch has no dead-man's switch: if GitHub does not run it, nothing says so. Glance at the Actions tab once a week.

## What the watch cannot see

- Work that never reaches `main`: a branch, a local tree, a PR that is open or closed unmerged, or the content of a
  review. It sees merges, not what an agent did before them.
- A review record is a self-reported comment. The check counts comments that start with `**Review record**` before the
  merge; it cannot tell a real second-family review from a pasted heading.
- One shared GitHub account: author, merger and commenter are the same login, so the watch cannot tell who did what;
  `created_by` is free text, and f only checks that a new label names a folder.
- Row edits in place: it counts added evidence rows and links and removed keyed rows, not changed values.
- A green `validate` only means the validator passed; c checks timing and conclusion, not correctness.
- The PIC-18 unknown counts are three numbers at one grain; e does not know whether a PR was meant to move them.
- Admin bypass of the `main` ruleset is visible only through c, d and b after the fact.
- Its own absence (item 5 above).
