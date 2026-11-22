# Working rules of 2026-11-22: the checks

The owner adopted seven working rules on 2026-11-22 (AGENTS.md section 2a; DECISIONS.md entries of the same date).
The trigger: one harness built, verified and merged about 34,000 evidence rows in a day, 28% of them did not bind to
their record, and every check was green. A rule without a check gets one or is not called a rule.

`scripts/check_pr_rules.py` is the check for rules 1, 4, 5 and 6, run by `.github/workflows/pr-rules.yml` as the check
named `pr-rules`. Its tests are `scripts/test_check_pr_rules.py` (run by `scripts/run_tests.py` in `validate`). Each
test below names the planted violation that must fail and the compliant case that must pass.

| Rule | What the check catches | Planted case (test class.method) |
|---|---|---|
| 1. Builder never merges | PR body without `Built by: <harness>, <model family>`; no counted reviewer from a family other than the builder's | `TestRules1And4.test_missing_built_by_line_fails`, `.test_builder_is_only_reviewer_family_fails` |
| 2. Packet and replay check | not here: `scripts/check_evidence_binding.py`, lands with branch `agent/claude-code/evidence-binding-gate-2026-11-22` | built by atlas-w22-binding-gate |
| 3. Binding gate | not here: same lane and branch | built by atlas-w22-binding-gate |
| 4. Two families review a data PR | fewer than two families approving at the current head; a stale-SHA record; a REFUTE; two records from one family; an unrecognised family; a PR that touches `scripts/` or `data/` with one record | `TestRules1And4.test_one_family_on_data_pr_fails`, `.test_two_records_same_family_count_once`, `.test_stale_head_does_not_count`, `.test_refute_does_not_count`, `.test_unknown_family_does_not_count`, `.test_scripts_only_pr_needs_two` |
| 5. Size cap | more than 1,000 evidence rows or 1,000 registry links without a "size waiver" line naming the PR's branch in DECISIONS.md | `TestRule5.test_over_cap_without_waiver_fails`, `.test_registry_links_over_cap_fails`, `.test_waiver_must_name_this_branch` |
| 5. Audit before the next batch | a data PR while a `created_by` label on `main` is not in the baseline and not named in any `tasks/<folder>/AUDIT.md` on `main` | `TestRule5.test_unaudited_label_blocks_a_data_pr`, `.test_label_substring_in_audit_is_not_an_audit` |
| 6. Raw inputs by checksum | evidence rows or registry links added with no `tasks/<folder>/INPUTS.sha256`; a malformed, empty, absolute or `..` line | `TestRule6.*` |
| all | a fact the check could not read (collection failure, missing field) fails the run | `TestUninspectable.*`, `TestRule5.test_missing_audit_facts_fail_instead_of_pass` |

Compliant cases that must pass: `TestCompliant.test_compliant_data_pr_passes_and_prints_what_it_inspected`,
`.test_non_data_pr_needs_one_record`, `TestRule5.test_at_cap_passes`. `TestCollectors` runs the row counter and the
label reader against a real git repository (quoted multiline fields included), because the facts-level tests cannot
show that the collector reads the right things. The check was also run live on PR #462 and PR #461 on 2026-11-22;
it counted 12 evidence rows on #461 (the size lane's own figure) and parsed #462's Codex record.

## Review-record format the parser accepts

The format already in use on PRs #460 and #462: a comment whose first line is `**Review record**`, then
`- **Verifier:** <family>, <model>, ...` (the family is read from the text before the first comma) and
``- **Verdict:** APPROVE|REFUTE at `<40-hex head SHA>` ``. The family is mapped from keywords (OpenAI/Codex/GPT; Anthropic/
Claude/Opus/Sonnet/Haiku; Google/Gemini/Antigravity; xAI/Grok). An unrecognised or ambiguous family does not count.

## What it cannot catch

- **Who merged (rule 1).** Every harness acts through one shared GitHub account, so a merge by the builder looks the
  same as a merge by anyone. The check can only require that a different family approved. Closing this needs separate
  accounts or a human merge, which is an owner decision.
- **A false review record.** The record is a comment any harness can post. The check reads the family and SHA the
  comment claims; it cannot tell whether that family actually reviewed. The reviewer's work is in its report, which the
  record points to.
- **The hashes in `INPUTS.sha256` (rule 6).** Format only. A reviewer checks them against the shared store.
- **A PR that edits the check.** `pull_request` workflows run the script from the PR's own tree, so a PR could weaken
  `check_pr_rules.py` or `pr-rules.yml` and pass. Both are under `scripts/` or `.github/`, so a PR that touches them
  needs the two-family review for `scripts/`, and a human reads the diff. A ruleset restriction on `.github/` and
  `scripts/check_*` paths would close it; that is a settings change the controller or owner makes.
- **Rule 5 audit content.** The check finds a file `AUDIT.md` naming the label; it does not judge the audit. Audit
  files are read from `main`, so a PR cannot audit itself, but a thin audit file passes.
- **Rule 5 counts rows the PR adds, not rows it changes.** A PR that rewrites 5,000 existing evidence rows adds none.
  Row loss is `check_row_loss.py`'s job; row rewrites are not counted by anything.
- **Rules 2 and 3**: not built here (see the table). **Rule 7** has no check (see AGENTS.md "Start here").

## Open questions for the owner or controller

1. **Baseline scope.** The instruction was to grandfather every `created_by` label on `main` today, so the baseline holds
   440 labels, including the batch-5 and batch-6 labels. Those are the labels the revert removes and the re-admission
   PRs re-add, so grandfathering them means a re-admission batch is never blocked for lack of an audit. Deleting the
   two lines `spaghetti-batch5-2026-11-22` and `spaghetti-batch6-2026-11-22` from the baseline (a one-line change)
   would require an `AUDIT.md` for them first.
2. **Scripts-only PRs.** The instruction names two cases (touches `data/`; touches neither `data/` nor `scripts/`). A PR
   that touches `scripts/` and not `data/` is treated as the first case: two families. Say if it should be one.
3. **The 2026-11-20 "Codex-only for now" waiver** (QUEUE.md, evidence lanes) conflicts with rule 4 as worded. The check
   does not honour it: two families are required. Say if the waiver still stands for any lane.
4. **Labels in tables other than evidence.** The label reader takes `created_by` from every `data/*.csv` that has the
   column, not only the evidence shards (all 440 labels on main today). Narrower would be evidence shards only.
5. **Merge-time versus comment-time.** A review record posted after the last push counts when the head SHA matches; a
   later push makes it stale and the PR needs fresh records. That is intended; stated here so it is not a surprise.
