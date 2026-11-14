# PR #309 (OR/KS: Carestream White City + NOV Fiber Glass Systems Wichita) — holds and retired IDs

Withdrawals applied 2026-11-14 after Codex's REFUTE of PR #309 @ e042775 (reviews/309-atlas-clerk-codex-10.md).
Units: cells and evidence rows in `data/sites_KS.csv` / `data/evidence_sites_KS.csv`.

## Holds (1 cell, 1 site)

| Site | Cell | Withdrawn value | Merge-base value | Reviewer's reason | What would settle it |
|---|---|---|---|---|---|
| SITE-020003 (NOV Fiber Glass Systems - Wichita) | `processes` | `composites_filament_winding` | (row is new; empty) | No Wichita process witness: EVD-350113 says the process was inferred from the held Iuka sister site, and NAICS 326122 names a product industry, not filament winding; FRS returns identity/address only. | A Wichita-specific process witness (the plant's own page or a filed document naming the process at 2501 S West St). |

## Retired evidence IDs (never reuse)

| ID | Was | Why withdrawn |
|---|---|---|
| EVD-350113 | SITE-020003 `scope`, "ring_primary 1; fiber-glass / FRP pipe products (federal NAICS 326122); process inferred from the held NOV Fiber Glass Systems Iuka sister site" | Its text records an inference, not a witness, for the process. `ring_primary` 1 stays supported by EVD-350112 (naics_primary 326122, OSHA ITA, government_filing). |

## Surfaced, not changed

`materials` on SITE-020003 (`composites_frp;epoxy`) and the row `notes` cell say they were aligned to the Iuka sister site by the same inference. The reviewer did not flag them, so they are untouched here; the next reviewer should decide whether to hold them too.
