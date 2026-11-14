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

## Addendum 2026-11-14 (controller instruction): materials withdrawn too

| Site | Cell | Withdrawn value | Merge-base value | Reason | What would settle it |
|---|---|---|---|---|---|
| SITE-020003 | `materials` | `composites_frp;epoxy` | (row is new; empty) | Rests on the same Iuka sister-site inference the reviewer refuted for `processes`; no Wichita witness names a material. | A Wichita-specific material witness (own page or filed document). |

- No evidence row supported only `materials`: EVD-350109 to EVD-350112 and EVD-350114 to EVD-350116 are identity, address, NAICS, parent, activity and liveness rows. Nothing else retired.
- `notes` on SITE-020003: the row is new, so there is no merge-base value. I deleted only the sentence that asserted the alignment ("Process/materials aligned to the held Iuka Fiber Glass Systems site; no own-page process read for Wichita, so tier C."). The rest of the creation notes is untouched. Nothing was added.

## Addendum 2026-11-14 (Codex re-check @ 9044f06): scope row for SITE-020003 restored with a limited witness

The re-check found that withdrawing EVD-350113 left the new site with no scope row (SCHEMA §4.13). Search for a Wichita-specific own-site witness, four fetches, none with Wichita text: a web search (only job postings and aggregators, which this repo does not count as capability witnesses); `https://www.nov.com/fgs` raw and via Jina; `https://nov.com/products-and-services/brands/lf-manufacturing` raw and via Jina; NOV's large-diameter FRP tanks flyer PDF (no "Wichita" or "Kansas"). A search that returns nothing is not evidence the plant makes nothing.

What was found instead is a primary filing for this exact establishment: OSHA ITA CY2025 establishment 1459584 (company NOV, establishment "Wichita Fiber Glass Systems", 2501 S West St, Wichita, KS 67217), NAICS 326122, industry description "Fittings and unions, rigid plastics pipe, manufacturing" (held spine `tasks/osha-ita-2026-11-01/establishments.csv`). SCHEMA §2.2 lists 326122 as Ring 1, signal P, matching `ring_primary` 1.

**One new evidence row, EVD-350117** (`scope`, `government_filing`, `supports_C`; allocated in this lane's block EVD-350100 to 350199; no other branch uses it). It states only what the filing says: the plant's filed industry, with no process or material inferred. It replaces retired EVD-350113 and is a new row, so it needs review. Nothing else changed: `processes`, `materials` and the notes sentence stay withdrawn, and the settling fact for them is unchanged.
