# Audit record: PIC-18 evidence queue from OSHA and Form 5500 files (PR #475)

Label: claude-code pic18-evidence-queue-2026-11-22
Result: PASS
Sample: census, 123 of 123 evidence rows (EVD-482000..482122: 113 organization rows, 10 site rows; 78 PIC-18 records). No sampling: every row was replayed.
Reviewers: Codex (GPT-6.2); Antigravity (Gemini 4 Hydrogen). Neither built the batch (builder: Claude Code).

## What was audited

Each reviewer, with its own code and not the packet's matcher (`binding.py`), read the cited OSHA and Form 5500 records
in the shared store by path and sha256 and compared every one of the 123 rows with its source record. Results:

- 123 of 123 rows reproduce from the raw files; 0 failing evidence IDs.
- Every organization row binds on the organization's own legal name (corporate-form words aside); 0 bind on a parent
  name or a trade name alone. Every site row binds on the operator's name and the site's own street.
- The 96 mailing-address rows stay inside the owner's ruling of 2026-11-22: a Form 5500 mailing address proves existence
  and headquarters city only. 39 of them are organization address rows claiming city and state, with no street; no site
  row rests on a mailing address.
- None of the 39 source rows held because the filer is a different entity under a recorded trade name entered the batch.
- The validator debt baseline shrinks by the 78 cured records (V-65 by 67, V-68 by 11) and gains nothing.

Codex: round 1 at `e3765ea0` (rows all reproduce; one finding on hosted CI silently omitting the replay, fixed by
#479), round 2 `APPROVE` at `e1966ba6`. Gemini: `APPROVE` at `e1966ba6`. Both recorded in the Review record comment on
PR #475.

After the merge the controller compared `main` with the audited head: `git diff e1966ba6 origin/main --
data/evidence_organizations_OH.csv data/evidence_sites_OH.csv` is empty at `main` 14e0ce9a, so the rows on `main` are
the rows that were audited.

## What this audit is not

- It is the pre-merge two-family replay, recorded as the batch's audit because it covered every row. No second,
  post-merge sample was drawn.
- Hosted CI cannot replay the packet (the raw files are in the shared store); the replays ran on the reviewers'
  machines.
- These rows witness existence, address and activity claims. They fill no process, market or size value: PIC-18
  organization rows with unknown process, market and size are 322, 316 and 396 of 794 before and after.
