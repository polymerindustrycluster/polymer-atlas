# Audit record: one-row repair of the PIC-18 street-fill batch (PR #493)

Label: codex pic18-street-fill-repair-2026-11-23
Result: PASS
Sample: census, 1 of 1 evidence row (EVD-483020). No sampling.
Reviewers: Antigravity (Gemini 4 Hydrogen); Claude Sonnet 5.5. Neither built the row (builder: Codex GPT-6.2 Sol).

## What was audited

Each reviewer, with its own code, checked the input file against `tasks/pic18-street-fill-repair-2026-11-23/INPUTS.sha256`,
opened OSHA ITA 300A 2025 (partial) row 352594 in the shared store, and confirmed that EVD-483020 reproduces from it: the
quoted operator is the held legal name American Bath Group, the quoted street equals SITE-001455's street, and the quote,
source_ref, observed_date and tier_effect follow the street-fill batch's ITA address convention. The evidence ID is above
the tree-wide maximum and unique. Both approved PR #493 at `f48af0e9` and graded this one-row label PASS.

After the merge the controller compared `main` with the reviewed head: `git diff f48af0e9 origin/main --
data/evidence_sites_OH.csv` is empty, so the row on `main` is the row that was audited.

## What this audit is not

It does not settle who operates the Salem plant today: an OSHA inspection opened 2026-10-20 names American Standard Inc.
at the same street, recorded as a lead in the task README.
