# Working rules of 2026-11-22: the checks

The owner adopted seven working rules on 2026-11-22 (AGENTS.md section 2a; DECISIONS.md entries of the same date).
The trigger: one harness built, verified and merged about 34,000 evidence rows in a day, 28% of them did not bind to
their record, and every check was green. A rule without a check gets one or is not called a rule.

`scripts/check_pr_rules.py` is the check for rules 1, 4, 5 and 6, run by `.github/workflows/pr-rules.yml`, which
publishes the check run named `pr-rules` on the PR head. Its tests are `scripts/test_check_pr_rules.py` (run by
`scripts/run_tests.py` in `validate`). Each test below names the planted violation that must fail and the compliant
case that must pass.

**Independent control (owner ruling, controller 2026-11-22).** The workflow runs on `pull_request_target` and
`issue_comment`, checks out the base branch only, and runs the checker on `main` against facts fetched for the PR
number. It never checks out or executes PR code. **Consequence, stated plainly:** a PR that changes
`scripts/check_pr_rules.py` or `.github/workflows/pr-rules.yml` is judged by the version already on `main`, so such a PR
cannot weaken its own gate; it needs one review record from a family other than the builder's, like any non-data PR (owner ruling "tier by risk", 2026-11-22, which superseded the earlier instruction that tooling PRs need two families). The new version first judges the PR after
the one that merges it. This PR itself cannot be judged by the new workflow before it merges (the workflow does not
exist on `main`); it is run through the checker locally and needs one independent review record.

| Rule | What the check catches | Planted case (test class.method) |
|---|---|---|
| 1. Builder never merges | PR body without `Built by: <harness>, <model family>`; no counted reviewer from a family other than the builder's | `TestRules1And4.test_missing_built_by_line_fails`, `.test_builder_is_only_reviewer_family_fails` |
| 2. Packet and replay | not here: `scripts/check_evidence_binding.py`, lands with branch `agent/claude-code/evidence-binding-gate-2026-11-22` | built by atlas-w22-binding-gate |
| 3. Binding gate | not here: same lane and branch | built by atlas-w22-binding-gate |
| 4. Tiered review: two families for a PR touching `data/`, one independent record for every other PR | fewer than two families approving at the current head; a stale-SHA record; a REFUTE; a later REFUTE withdrawing an approval; an abbreviated SHA; two models of one family; the same model under two family labels; a record with no model, an unknown model, or no "What it checked" | `TestRules1And4.*`, in particular `.test_scripts_ci_and_process_prs_need_one_independent_record`, `.test_any_data_file_makes_it_a_two_family_pr` |
| 5. Size cap | more than 1,000 evidence rows or 1,000 new registry identities without a "size waiver" line, added to DECISIONS.md by the PR, naming exactly the PR's branch | `TestRule5.test_over_cap_without_waiver_fails`, `.test_registry_links_over_cap_fails`, `.test_waiver_must_name_exactly_this_branch` |
| 5. Audit before the next batch | a data PR while a `created_by` label on `main` is not in the baseline and not named by a valid `AUDIT.md` (`Label:`, `Result: PASS`, `Sample:`, `Reviewers:`); a FAIL audit; a pending audit | `TestRule5.test_unaudited_label_blocks_a_data_pr`, `.test_pending_audit_does_not_count`, `.test_fail_audit_blocks`, `.test_audit_missing_sample_or_reviewers_does_not_count` |
| 6. Raw inputs by checksum | evidence rows or registry links added with no `tasks/<folder>/INPUTS.sha256`; a malformed or empty line; an absolute path of either style, `.`, `..`, a directory, a repo path that is not an existing file | `TestRule6.*` |
| all | a fact the check could not read (collection failure, a failed read of a tracked object, an empty changed-file list) fails the run | `TestUninspectable.*`, `TestCollectors.test_failed_read_of_a_tracked_path_raises`, `.test_collect_reports_a_failed_read_and_the_run_fails` |

Compliant cases that must pass: `TestCompliant.*`, `TestRule5.test_at_cap_passes`,
`.test_valid_pass_audit_clears_label_and_several_labels_per_file`, `TestRules1And4.test_later_approval_after_refute_restores`.
`TestCollectors` runs the row counter, the label reader and `collect()` itself against a real git repository (quoted
multiline fields, a metadata-only registry edit, a path absent at base, a failed blob read). `TestWorkflow` pins the
workflow to `pull_request_target`, a base-only checkout, and comment created, edited and deleted. The check was also
run live on PR #461 and PR #462 on 2026-11-22.

## Counterexamples from Codex's round 1 on PR #466 (each is now a test)

| # | Finding | Fix |
|---|---|---|
| 1 | the PR's own checker judged the PR | `pull_request_target`, base checkout, `TestWorkflow` |
| 2 | a later REFUTE or a stale abbreviated SHA still counted | latest record per verifier governs; the SHA is read only from the verdict line, 40 characters |
| 3 | family labels and family-only records counted | family derived from the model by a fixed map; model, verdict with SHA and "What it checked" required |
| 4 | a longer or prefixed branch name lifted the cap | exact branch, on a line the PR adds to DECISIONS.md |
| 5 | audit gate stale after main moves | documented: the ruleset's strict policy (below) |
| 6 | a failed blob read looked like zero rows | `InspectionError`; only a path absent from one side of the diff is absent |
| 7 | a registry metadata edit counted as a new link | identity (org_id, registry, registry_id, site_id) |
| 8 | Windows absolute path, `.` and directories accepted | relative POSIX file path; repo paths must exist as a file at head |
| 9 | an edited or deleted comment did not re-evaluate; run chosen by SHA | `issue_comment` created, edited, deleted; evaluated by PR number through the API |

## Review-record format the parser accepts

A comment whose first line is `**Review record**`, then
`- **Verifier:** <harness>, <model>, ...` (the model is the second comma-separated field),
``- **Verdict:** APPROVE|REFUTE at `<40-hex head SHA>` `` and `- **What it checked:** <what, at least ten characters>`.
The family comes from the model by a fixed map of whole words: GPT or Codex is OpenAI; Claude, Opus, Sonnet, Haiku or
Fable is Anthropic; Gemini is Google; Grok is xAI; Muse is Meta. An unknown model does not count; two models of one
family are one family. Formats on #460 and #462 (`OpenAI Codex, GPT-6.2 Astra, ...`) parse. A model name must be written
so that its family appears in it (for example `Gemini 4 Hydrogen`, not `4 Hydrogen`).

## What it cannot catch

- **Who merged (rule 1).** Every harness acts through one shared GitHub account, so a merge by the builder looks the
  same as a merge by anyone. The check can only require that a record from a different family exists. Closing this
  needs separate accounts or a human merge, which is an owner decision.
- **A false review record.** The record is a self-reported comment any harness can post on the shared account. The
  check reads the model, verdict, SHA and checked-line the comment claims; it cannot tell whether that model actually
  reviewed. The reviewer's work is in its report, which the record points to.
- **The hashes in `INPUTS.sha256` (rule 6).** Format only. A reviewer checks them against the shared store.
- **A PR that edits the check** is judged by the version on `main` (see above), so it cannot weaken its own gate. What
  remains: the version on `main` is only as good as its last two-family review, and the ruleset (a setting, not a file)
  is what makes `pr-rules` required.
- **A stale audit gate (finding 5).** Two data PRs tested against the same clean `main` can both pass, then the first
  lands a new label. The check is re-evaluated on PR events and comments, not when `main` moves. The controller sets
  the ruleset's strict policy (branch up to date with `main` before merge) when making `pr-rules` required, so a PR is
  re-judged after `main` moves. Without that setting this gap is open.
- **The round cap, the re-review scope and the BLOCKING or FOLLOW-UP marking (rule 4).** Practice for the controller, not
  checked. The checker only notes a REFUTE record that names no BLOCKING finding; it still withdraws that approval.
- **The freeze on national evidence backfill (rule 5).** Owner policy, no check.
- **A raw-store path that is a directory.** Paths under `raw/` and `provenance/` are in the shared store, not the
  repository, so the check cannot tell a file from a directory there; it rejects a trailing slash and `.`/`..`.
- **Rule 5 audit content.** The check finds a file `AUDIT.md` naming the label; it does not judge the audit. Audit
  files are read from `main`, so a PR cannot audit itself, but a thin audit file passes.
- **Rule 5 counts rows the PR adds, not rows it changes.** A PR that rewrites 5,000 existing evidence rows adds none.
  Row loss is `check_row_loss.py`'s job; row rewrites are not counted by anything.
- **Rules 2 and 3**: not built here (see the table). **Rule 7** has no check (see AGENTS.md "Start here").

## Rulings applied (controller, 2026-11-22) and what is still open

Applied from the controller's message on Codex's round 1: independent control; the latest record per verifier; family
from the model; exact-branch waiver; strict policy documented; read failures fail; registry identity; path grammar;
comment events by PR number; AUDIT.md structure (`Label:`, `Result: PASS|FAIL`, `Sample:`, `Reviewers:`; pending does
not count; FAIL blocks, including a grandfathered label); rule 3 scope as the binding gate enforces it.

Still open for the owner or controller:

1. **Baseline scope.** The baseline holds all 440 `created_by` labels on `main` on 2026-11-22, including the batch-5 and
   batch-6 labels. Those are the labels the revert removes and the re-admission PRs re-add, so grandfathering them
   means a re-admission batch is not blocked for lack of an audit. Deleting the two lines
   `spaghetti-batch5-2026-11-22` and `spaghetti-batch6-2026-11-22` from the baseline would require an `AUDIT.md` first.
2. **The 2026-11-20 "Codex-only for now" waiver** (QUEUE.md, evidence lanes) conflicts with rule 4. The check does not
   honour it: a data PR needs two families.
3. **Labels in tables other than evidence.** The label reader takes `created_by` from every `data/*.csv` that has the
   column, not only the evidence shards.
4. **A FAIL audit is permanent until its file changes.** Any `AUDIT.md` with `Result: FAIL` blocks data PRs for that
   label; a later PASS file does not override it. Clearing it means editing the FAIL record in a reviewed PR.
5. **Merge-time versus comment-time.** A record posted after the last push counts when its SHA matches; a later push
   makes it stale. Intended; stated so it is not a surprise.
