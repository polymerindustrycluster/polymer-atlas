# Audit record: PIC-18 size bands from OSHA records (PR #468)

Label: claude-code pic18-size-bands-2026-11-22
Result: PASS
Sample: census, 50 of 50 evidence rows and their 50 site bands (47 OSHA ITA establishment records, 3 OSHA inspections; 47 organizations). No sampling: every row was replayed.
Reviewers: Codex (GPT-6.2 Astra); Antigravity (Gemini 4 Hydrogen). Neither built the batch (builder: Claude Code, Claude Sonnet 5.5).

## What was audited

Each reviewer, with its own code and not the packet's, read the raw OSHA files in the shared store by path and sha256 and
compared every one of the 50 rows with its source record: the operator name is a name the Atlas site record holds
(corporate-form words aside), the street is the site's own street, the filing is dated within five years (cutoff
2021-11-22), and the band follows from the reported headcount. Result: 50 of 50 reproduce; 0 rest on a parent-only name,
on a locality alone, or on a Form 5500 filing. Verdicts: `APPROVE` from both at
`cc65f3a4d4dbea42626cc0be332cfc8dfc2c9632` (round 3), recorded in the Review record comment on PR #468.

After the merge the controller compared `main` with the audited head: `git diff cc65f3a4 origin/main --
data/sites_OH.csv data/evidence_sites_OH.csv` is empty at `main` fb95d4c0, so the rows on `main` are the rows that were
audited. PIC-18 organization rows with unknown size (active tier A to C sites, organization fallback): 443 before, 396
after, of 794.

## What this audit is not

- It is the pre-merge two-family replay, recorded as the batch's audit because it covered every row. No second,
  post-merge sample was drawn.
- Headcounts were checked against the public filings, not against the employers.
- The 28 Form 5500 fills first proposed in PR #468 were withdrawn before merge and are not part of this batch; they are
  parked on `agent/claude-code/pic18-size-form5500-2026-11-22` pending an owner ruling.
