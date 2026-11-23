# Audit record: PIC-18 process from Ohio EPA air permits (PR #481)

Label: claude-code atlas-w22-process-permits
Result: PASS
Sample: census, 2 of 2 evidence rows (EVD-483000 SITE-000140 foam_extrusion, permit P0140000; EVD-483001 SITE-001078 calendering, permit P0135097) and the 2 site process fills they support. No sampling: every row was read against its permit.
Reviewers: Codex (GPT-6.2); Antigravity (Gemini 4 Hydrogen). Neither built the batch (builder: Claude Code).

## What was audited

Each reviewer opened the permit PDFs (the original bytes, extracted with `pdftotext`) and compared, for each fill, the
facility ID, holder, street and municipality printed on the permit with the Atlas site and organization records, and the
quoted sentence with the permit text. Both permits bind to their plants, and each quote states the process it fills.
Round 1 (both families, at `11903c21`) refused on release defects, not on the fills: the evidence IDs reused retired
gaps, and one permit PDF was not yet in the shared store. Round 2 (both families) `APPROVE` at `4c36e322`: IDs above the
tree maximum, both PDFs in `INPUTS.sha256` and in the store's `raw/MANIFEST.sha256`. Recorded in the Review record
comment on PR #481.

The controller merged `main` into the branch before merge (an append-only conflict in `data/evidence_sites_OH.csv`
with #475's rows; both kept). Line-for-line, the data change against `main` was identical to the approved PR's.

## What this audit is not

- It is the pre-merge two-family reading, recorded as the batch's audit because it covered both rows. No post-merge
  sample was drawn.
- A permit states what the plant is permitted to run, at the permit's date; it was not checked against the plant
  today.
- The held owner questions on permits (the capability-only rule, holder-name form, blank street, municipality
  mismatch) are not part of this batch.
