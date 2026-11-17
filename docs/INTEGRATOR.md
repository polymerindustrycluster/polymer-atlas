# Integrator tools

Run these from anywhere inside the checkout; Python 3, Git (with merge-tree
--write-tree), Bash and authenticated `gh` are required. No home paths or ledger
are assumed. These commands are for the designated integrator, not research lanes.

```sh
python3 scripts/integrate/delta_compare.py APPROVED CANDIDATE
python3 scripts/integrate/cell_replay.py APPROVED /path/to/main-worktree
scripts/integrate/sync_pr.sh PR APPROVED
scripts/integrate/ci_merge.sh PR APPROVED
scripts/integrate/merge_queue.sh /path/to/queue.txt
```

The queue contains `PR APPROVED_SHA` per line. Successful entries are recorded in
`queue.txt.done`; failure stops the queue. Re-running a queue requires removing
completed entries. Optional `INTEGRATOR_LEDGER` names an external merge log;
`INTEGRATOR_TIMEOUT` sets the CI wait in seconds (default 3600).

As specified in tasks/CAMPAIGN.md, approval carries forward only over an unchanged
approved payload, or a strict subset with only refuted claims withdrawn. Code,
packets, reports and source meaning require targeted review even with an empty
data delta. `delta_compare.py --allow-subset` diagnoses a subset; it does not
establish that withdrawals were refuted. Automated sync/merge accepts identical
deltas only. Review changed non-data payload separately; receipts are not evidence
that changed code is approved.

Delta comparison uses each head's merge-base with origin/main, logical shard
families and keyed cells. Replay preflights all files, rejects deletions, duplicate
keys, header drift, new-key collisions and cells changed on main. Registry links
and people identifiers use the composite keys in check_row_loss.py; inclusion logs use
whole-row keys with occurrence counts. New/deleted
CSV files require manual integration. Replay writes only data; use a disposable
worktree. Filesystem write failures can leave partial writes, so retain backups.

Sync tries merge-tree first, otherwise applies the non-data patch to main and
replays approved cells. It checks identical data delta, non-data head changes,
validation and row loss before a non-force push. The shared push guard resolves
origin's default branch from the remote and refuses main, that default branch
(including destinations ending in either name), fork PRs, unknown metadata,
force/deletion refspecs and destinations other than the PR's own head branch.
It checks before sync mutations and again immediately before pushing. Non-data changes caused solely
by main may conservatively require manual review. CI waits for `validate` on the
pushed branch SHA; premerge validates the merged tree, and merge uses an expected
head guard. Success requires GitHub's state to be MERGED. Never invoke mergepr.sh
directly: ci_merge.sh supplies the SHA whose required check passed.

Checks: `python3 -m unittest discover -s scripts`. Fixtures cover identical and
subset deltas, differing values, concurrent-cell refusal and composite appends.
No live PR is merged by these tests.
