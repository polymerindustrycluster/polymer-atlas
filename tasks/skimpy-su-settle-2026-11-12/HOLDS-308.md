# PR #308 (CT: LATICRETE Bethany + Silgan Thomaston) — holds and retired IDs

Withdrawals applied 2026-11-14 after Codex's REFUTE of PR #308 @ 0016be6 (reviews/308-atlas-clerk-codex-10.md).
Units: cells and evidence rows in `data/sites_CT.csv` / `data/evidence_sites_CT.csv`.

## Holds (1 cell, 1 site)

| Site | Cell | Withdrawn value | Merge-base value | Reviewer's reason | What would settle it |
|---|---|---|---|---|---|
| SITE-020001 (Silgan Dispensing Systems Thomaston) | `materials` | `thermoplastics` | (row is new; empty) | The own locations page identifies the plant and address, not its material; FRS returns identity/address only; NAICS 326199 does not distinguish thermoplastics from other plastics. | A site-specific material witness (an own-site or filed document naming the resin/material class made at 60 Electric Avenue). |

## Retired evidence IDs (never reuse)

| ID | Was | Why withdrawn |
|---|---|---|
| EVD-350013 | SITE-020001 `scope`, "ring_primary 1; plastics manufacturing plant (federal NAICS 326199)", cited to the silgandispensing.com locations page | The claim text rests on federal NAICS, not on the cited page. `ring_primary` 1 stays supported by EVD-350012 (naics_primary 326199, OSHA ITA, government_filing); no other value depended on this row. |
