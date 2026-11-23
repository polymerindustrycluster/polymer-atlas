# Working rules of 2026-11-22: the checks

The owner adopted seven working rules on 2026-11-22 (AGENTS.md section 2a; DECISIONS.md entries of the same date).
The trigger: one harness built, verified and merged about 34,000 evidence rows in a day, 28% of them did not bind to
their record, and every check was green. A rule without a check gets one or is not called a rule.

**Cut down by owner ruling (2026-11-22, after two Codex review rounds).** An earlier version of this PR also read PR
comments and review records. It was dropped because it could not be made sound: a record is a self-reported comment on
one shared GitHub account. Review (rules 1 and 4) is now practice, stated as such in AGENTS.md, and nothing in this PR
reads a comment. What remains is below.

| Rule | Status |
|---|---|
| 1. Builder never merges | Practice. Not checked. One GitHub account is shared by every harness, so who merged cannot be verified. |
| 2. Packet and replay | Partly checked by PR #467's gate (below). Not replay, not sampling. |
| 3. Binding gate | Checked for structured evidence rows by PR #467's gate, by name and street. |
| 4. Tiered review | Practice. Not checked. Enforcement would need separate accounts and GitHub-required reviews (owner's choice, not now). |
| 5. Size cap | Checked: `check_pr_rules.py`. |
| 5. Audit before the next batch | Checked: `check_pr_rules.py`, with a deployment condition (below). |
| 5. Freeze on national backfill | Owner policy. Not checked. |
| 6. Raw inputs by checksum | Checked, format only: `check_pr_rules.py`. |
| 7. Where things live | Practice. Not checked. |

## What is checked, and the planted case for each

`scripts/check_pr_rules.py`, run by `.github/workflows/pr-rules.yml` as the check run `pr-rules`; tests in
`scripts/test_check_pr_rules.py` (run by `scripts/run_tests.py` in `validate`).

| Check | What it catches | Planted case (test) |
|---|---|---|
| Size cap | more than 1,000 evidence rows or 1,000 new registry identities without a waiver | `TestRule5.test_over_cap_without_waiver_fails`, `.test_registry_links_over_cap_fails`; compliant: `.test_at_cap_passes` |
| Waiver | the waiver line must be added by the PR, contain "size waiver", and carry `branch=<name>` whose token EQUALS the PR's branch; every suffix tried (`+alternate`, `-extra`, `/more`, `.y`, `,`, `;`, `@x`, `#1`, `=y`, `.lock` and more), another branch, no `branch=` field, no waiver words, `xbranch=` all fail | `TestRule5.test_waiver_compares_the_complete_branch_field_for_equality` |
| Audit record | a data PR while a `created_by` label on `main` is not in the baseline and not named by a valid `AUDIT.md` (`Label:`, `Result: PASS`, `Sample:`, `Reviewers:`); a pending audit, a missing field or a FAIL audit | `TestRule5.test_unaudited_label_blocks_a_data_pr`, `.test_pending_audit_does_not_count`, `.test_fail_audit_blocks`, `.test_audit_missing_sample_or_reviewers_does_not_count` |
| INPUTS.sha256 | evidence rows or registry links with no `tasks/<folder>/INPUTS.sha256`; a malformed or empty line; an absolute path of either style, `.`, `..`, a directory; **the bare word `raw` or `provenance` (it names the store, not a file: at least one component below it is needed)**; a repo path that is not an existing file | `TestRule6.*`, in particular `.test_the_store_itself_is_not_a_file`, `.test_absolute_dot_dotdot_and_directory_paths_fail` |
| Fail on what it could not inspect | a failed read of a tracked git object, a short CSV row, a missing column, a collection failure, an empty changed-file list | `TestUninspectable.*`, `TestCollectors.test_failed_read_of_a_tracked_path_raises`, `.test_collect_reports_a_failed_read_and_the_run_fails` |
| Registry identity | a metadata edit to a held link is not a new link | `TestCollectors.test_registry_metadata_edit_is_not_a_new_link` |
| Nothing reads a comment | the checker and workflow carry no comment, review-record or PR-body logic | `TestCompliant.test_no_review_record_is_read_anywhere`, `TestWorkflow.test_no_comment_trigger_and_no_comment_reading` |

Compliant cases that must pass: `TestCompliant.*`, `TestRule5.test_valid_pass_audit_clears_label_and_several_labels_per_file`.
`TestCollectors` runs the row counter, the label reader and `collect()` itself against a real git repository.

## The binding-gate job

The workflow's second check run, `binding-gate`, runs main's `scripts/check_evidence_binding.py` (PR #467, the gate for
structured rows) twice with `--tree pr`: `--new-since origin/main` and `--provenance-since origin/main`. The PR merge
result is checked out as data into `./pr`; the trusted checkout (the base branch, `fetch-depth: 0`) supplies the code and
the rules. **Nothing from the PR tree is executed.** The job has `permissions: {}` (the repository is public) and both
checkouts use `persist-credentials: false`. A separate job, which runs no PR code, holds `checks: write` and publishes
the result. The job fails if the merge commit's second parent is not the current PR head (a stale merge ref). States:
`passed` (success); `failed` and `cannot_inspect` (failure; the latter when main's script lacks a mode or exits 2);
`not_yet`. **`not_yet` is the one pass that checked nothing:** until `scripts/check_evidence_binding.py` is on `main` the
check run says "gate not yet on main: nothing was checked" and posts success, because the gate cannot judge the PR that
adds it. Nothing is neutral and nothing is skipped. `TestBindingGateJob` pins these properties in the workflow text.
Not verified: the gate steps have not run on a runner (the script is not on `main` until #467 merges).

## What it cannot catch

- **Who merged, and whether a review happened (rules 1 and 4).** Practice only; see the table.
- **A PR that edits the check** is judged by the version on `main`, so it cannot weaken its own gate. The version on
  `main` is only as good as its last review, and the ruleset (a setting, not a file) is what makes `pr-rules` required.
- **Audit freshness (deployment condition).** Two data PRs tested against the same clean `main` can both pass, and the
  first then lands a new label. The check is evaluated on PR events, not when `main` moves. It holds only once the
  controller has made `pr-rules` a required check **and** turned on the ruleset's strict (up-to-date) policy. Neither is
  done by this PR; `docs/ci/README.md` says so.
- **The hashes in `INPUTS.sha256`.** Format only. A reviewer checks them against the shared store. Paths under `raw/`
  and `provenance/` are in the shared store, not the repository, so a directory there cannot be told from a file beyond
  the rules above.
- **Audit content.** The check finds an `AUDIT.md` with the four lines; it does not judge the audit. Audit files are read
  from `main`, so a PR cannot audit itself, but a thin audit file passes.
- **Rows a PR changes.** Only added rows are counted: a PR that rewrites 5,000 existing evidence rows adds none.
  Row loss is `check_row_loss.py`'s job.
- **Failed evaluation on an unchanged head.** If a re-run on the same head fails to collect, no new check run is posted
  and an earlier result stands. A new push always starts from no result.

## Still open for the owner or controller

1. **Baseline scope.** The baseline holds all 440 `created_by` labels on `main` on 2026-11-22, including the batch-5 and
   batch-6 labels. Those are the labels the revert removed and the re-admission PRs re-add, so grandfathering them means a
   re-admission batch is not blocked for lack of an audit. Deleting `spaghetti-batch5-2026-11-22` and
   `spaghetti-batch6-2026-11-22` from the baseline would require an `AUDIT.md` first.
2. **Labels in tables other than evidence.** The label reader takes `created_by` from every `data/*.csv` that has the
   column, not only the evidence shards.
3. **A FAIL audit is permanent until its file changes.** A later PASS file does not override it.
4. **Ruleset (controller):** require `pr-rules` and `binding-gate`, and turn on the strict policy (see above).
