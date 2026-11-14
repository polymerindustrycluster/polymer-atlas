# PR #311 (AR/OK: HMS Little Rock + Kingspan Stillwater) — holds and retired IDs

Withdrawals applied 2026-11-14 after Codex's REFUTE of PR #311 @ c00cc14 (reviews/311-atlas-clerk-codex-10.md; Gemini's refute on the same head raised the same two findings, reviews/311-atlas-clerk-gemini-1.md).
Units: cells and evidence rows on `ORG-013801` / `SITE-020005` (Kingspan Roofing + Waterproofing, Stillwater). Both rows are new in this PR, so every merge-base value is empty. HMS (`ORG-013800`, `SITE-020004`) is untouched.

## Hold 1: federal NAICS 326199 (cells: naics_primary, naics_primary_source_type, naics_primary_source_name [org only], naics_confidence, on both rows)

The cited witness, OSHA ITA establishment 1424574, is filed as company `Kingspan Roofing + Waterproofing`, establishment `Kingspan Roofing + Waterproofing- Stillwater`, NAICS **326299**, not 326199 and not `SHEET VINYL FLOORING MFG FACILITY` (that is the legacy FRS 110000454838 name). Read `tasks/osha-ita-2026-11-01/establishments.csv`, `establishment_id == '1424574'`.

| Withdrawn | Merge-base | What would settle it |
|---|---|---|
| naics_primary `326199` (org and site), with its source type, source name and confidence | empty (rows are new) | A fresh lane re-reads ITA 1424574, quotes it as it is (326299, rubber roofing membrane), and the owner/lane rules whether 326299 keeps `ring_primary` 1. Writing 326299 in now would be a new value needing its own review. |

Also removed, as misstating the witness (text deletions only, nothing added): from `sources` on both rows the fragment "; OSHA ITA Form 300A CY2025 establishment 1424574 (SHEET VINYL FLOORING MFG FACILITY)"; from the org `notes` the sentence "FRS 110000454838 and ITA 1424574 still carry the legacy name ... not treated as the current legal operator."; from the site `notes` the sentence "Site tier C: the federal NAICS still rides the legacy sheet-vinyl facility name ...". The FRS legacy-name statements and the ITA liveness mentions (EVD-350220, EVD-350228, the site note on latest_activity) are kept: ITA 1424574 does sit at this street, and the reviewers did not dispute that.

## Hold 2: processes and materials (cells: processes `extrusion_sheet`, materials `thermoplastics`, on both rows)

The contact page gives the legal name and street; the Greater OKC Chamber article says "membrane and insulation for low-slope roofing". Neither names a process or a polymer material.

| Withdrawn | Merge-base | What would settle it |
|---|---|---|
| processes `extrusion_sheet`, materials `thermoplastics` (org and site) | empty | A Kingspan own-page or filed document naming the process and material made at 4115 N Perkins Road. |

No evidence row supported only these cells: EVD-350217 and EVD-350225 claim `ring_primary` 1 and "roofing membrane and insulation" as the chamber article says them, so they stay.

## Retired evidence IDs (never reuse)

| ID | Was |
|---|---|
| EVD-350218 | ORG-013801 `code`, naics_primary 326199 from ITA 1424574 "(SHEET VINYL FLOORING MFG FACILITY)" |
| EVD-350224 | SITE-020005 `code`, naics_primary 326199 from ITA 1424574 "(ITA/FRS still titled SHEET VINYL FLOORING MFG FACILITY)" |

The code claim type had no row on either record after this withdrawal; see the addendum below, which restores it from the correct witness.

## Addendum 2026-11-14 (Codex re-check @ 12514c5): NAICS restored from the filing itself

The re-check found that clearing NAICS left `ORG-013801` and `SITE-020005` without the must-have NAICS primary, its provenance, and code evidence (SCHEMA §4.4, §4.5, §4.13). The cited witness does carry a NAICS: the held ITA spine (`tasks/osha-ita-2026-11-01/establishments.csv`, `establishment_id == '1424574'`) files company `Kingspan Roofing + Waterproofing`, establishment `Kingspan Roofing + Waterproofing- Stillwater`, `4115 N Perkins Road`, Stillwater, OK 74075, NAICS **326299**, "Roofing (i.e., single ply rubber membrane) manufacturing". The name and street match the held org (legal name "Kingspan Roofing + Waterproofing, Inc.", trade name "Kingspan Roofing + Waterproofing") and site, so the filing is the right witness.

Ring check: SCHEMA §2.2 lists 326299 (All Other Rubber Product Mfg) under Ring 1 with signal P, which matches the existing `ring_primary` 1 on both records, so no ring change and no judgment call was needed. (§2.2 also says NAICS is never the ring decision alone; the ring was already set by the lane, unchanged here.)

New or changed values, all needing review:
- `ORG-013801`: `naics_primary` 326299, `naics_primary_source_type` government_filing, `naics_primary_source_name` "OSHA ITA CY2025 establishment 1424574", `naics_confidence` low (the value first reviewed; not upgraded), and the `sources` cell regains the ITA citation, now with the filing's real names.
- `SITE-020005`: `naics_primary` 326299, `naics_primary_source_type` government_filing, `naics_confidence` low, and the same `sources` citation.
- Two new code evidence rows, `EVD-350240` (organization) and `EVD-350241` (site): `government_filing`, `supports_C`, quoting the ITA record exactly, observed 2026-11-14. IDs checked free on every remote branch. They replace retired EVD-350218 and EVD-350224, whose IDs stay retired.

Still blank and unchanged: `processes` and `materials` on both records (Hold 2). SCHEMA §4.x lists "at least one of processes/materials" for a complete v1 record; the re-check did not raise it, but it is a gap a later review may.
