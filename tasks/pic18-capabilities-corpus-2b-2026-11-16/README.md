# PIC-18 corpus capabilities, second half (lane CAP2B) — 2026-11-16

Integrator of record: atlas-w16-cap2b. Draft PR, no merge. First user: PIC cluster reporting analyst; non-use is a finding if the process counts are not used in reporting by 2026-12-16.

## Scope and frame
Slice = the sites PR #351's frame left unadjudicated (224 eligible in its frame, 4 decided there), sorted by site_id, second half: **110 active tier A–C PIC-18 Ohio sites** (A 42, B 55, C 13), SITE-001479 to SITE-004208. Each has a blank process or material cell, an organization with exactly one active Atlas site, and at least one stored corpus page. `check.py` recomputes the frame from the pinned base tree (`base.txt` = main at 89d9e46, after #351 merged) and asserts the slice is exactly that second half and that each site's stored-page count matches the manifest.

## Results (unit: Atlas sites in the slice, unless stated)
| | count |
|---|---|
| slice sites | 110 |
| sites with data applied | **10** (9.1%): tier B 6, tier A 4 |
| of those, site rows gaining section-3 tags | 9 (processes/materials cells only; all were blank before) |
| term decisions applied | 15 (13 section-3 tags with evidence rows; 2 capability-row-only on tier B menu terms) |
| evidence rows | 13 (EVD-388000 to 388012), all supports_A; EVD-388013 retired |
| site_capabilities rows | 4 (CAP-001500, 001501, 001502, 001504), all company_disclosed; CAP-001503 retired |
| sites held with named terms and a settling fact | 36 |
| sites with nothing found on the term screen | 64 |
| verdict rows | 133 (one or more per slice site; `verdicts.csv`) |

Applied: SITE-001613 injection_molding; SITE-001623 foam_fabrication, compression_molding, foams_polymeric; SITE-001664 mold_tool_making, tooling_repair_maintenance (+ injection_molding as capability row only); SITE-001669 polymer_additives; SITE-001690 acrylic_pmma; SITE-001785 natural_rubber_nr; SITE-001831 recycling_unspecified; SITE-001864 mold_tool_making, tooling_repair_maintenance; SITE-001941 mold_tool_making; SITE-001935 thermoforming_unspecified (capability row `thermoforming`, tier B menu, no tag).

## Revision after review of 1516036 (Codex-21)
SITE-001569 VisionAir withdrawn: the silicone-stent page cites 526 S. Main St., Suite 509, Akron 44311, but the site record is 1800 Triplett Blvd, 44306, so the claim is company-grain. Silicones tag, EVD-388013 and CAP-001503 are retired (never reused; CAP-001504 keeps its number) and the term is a hold whose settling fact is a stored page tying the material to the Triplett establishment. Sweep of the other applied sites for a witness address that differs from the site record: house numbers match for Frantz (7740 Metric Dr), MatPLUS (76 Burton St), Alpha Tool (83 Alpha Park), Maple City (55 Newton St), Colonial Patterns (920 Overholt Rd), Medina Recycling (370 Lake Rd) and Thermo Packaging (16815 Park Circle Dr). ITPS, SOPREMA and AAM carry city-grained witnesses in their rows (kept unchanged so the delta stays a subset). Stored pages add: ITPS home page prints "852 Anne Street Niles. Oh 44446" (record "852 Ann Ave", same number and city); SOPREMA locations page prints "Wadsworth, Ohio 310 Quadral Drive" (record "310 & 275 QUADRAL DR"); AAM stored pages print no street (record 4636 Valleyview Blvd), so AAM's tie to the record rests on the city and single-site status. `check.py` now compares a street-grained witness's house number with the record's and fails on the VisionAir case.

## Rules applied
Narrative sentence = supports_A; list/menu item = supports_C. Tier A/B with a C-strength term: capability row only, no section-3 tag, no evidence row (ruling 2026-11-14). Tier C: tag plus supports_C evidence (no applied tier C site remains after the withdrawal). Every applied term has a ≤25-word quote that appears word-for-word in order in the stored raw page (SHA-256 pinned) and a locality witness (the plant address or "located in <city>") on a stored page of the same organization. Thermoforming subtype rolls up to `thermoforming` for the capability row (b02 method). Only `processes` and `materials` cells changed; no organization, tier, source, note or date cell touched.

## How far this got — read honestly
About 40 sites had their stored pages read in the relevant windows (every applied site, every named hold, and the sites the term screen flagged with plant-looking wording). The other ~70 were judged from first-hit-per-term snippets of the lane's term screen (one regex family per vocabulary term) plus a supplementary screen (liquid crystal, pulverizing, pultrusion, filament winding, fiber, dye, tape, molded/molding, extruded, resin, plastic, polymer, cast, tubing, blister). "Nothing found" means no hit on that screen, not full-page adjudication and not a claim the capability is absent. A failed or empty fetch is availability, never absence.

## Holds (all in `verdicts.csv` and `holds.csv`, each with its settling fact)
Main reasons: distributor/equipment-dealer/consultant wording rather than plant process; stored page is a parent or group page; plant not allocated on a multi-location page (GHSP, RPM, RTS, Green Processing, Jax); no stored page names the plant locality (RAM Plastics, AlphaMicron, Kapp); tier A/B menu terms with no capability-vocabulary term (Rotocast mold making; MatPLUS die cutting/lamination); term broader than the words (Frantz assembly, Niles Building "vinyl"). Two owner-ruling holds: SITE-001986 Castinite casting of epoxy/quartz polymer concrete (does it map to potting_encapsulation_casting — recommend no) and its composites_unspecified, held because materials already held `epoxy` and the b02 rule is fill-blank-only. SITE-001731 C4 Polymers keeps the earlier lane's hold.

## Replay and checks
`python3 tasks/pic18-capabilities-corpus-2b-2026-11-16/build.py` then `check.py` (needs the shared corpus path in `build.CORPUS`). Build is idempotent (rerun leaves zero diff). `check.py` recomputes the frame, every decision against the raw pages, the data-file deltas (id sets, full-row preservation, fill-blank-only), verdict coverage, summary counts, and fails on 9 injected defects (false quote, invalid term, false locality, missing verdict, C-strength tag on tier B, witness street differs from record, retired id reused, id outside block, wrong slice). Output in `CHECKS.txt`. `scripts/` untouched, so the unit-test run was skipped.

## Proposed follow-ups
- Settle the two Castinite owner questions (polymer-concrete casting mapping; additive writes to non-blank cells).
- Read the ~70 snippet-judged sites in full, and the first half of the frame (the other CAP2 lane).
- Fetch contact pages for sites with no locality witness (RAM Plastics, AlphaMicron, Kapp Surgical).
- Two-family refute review before merge (not requested by this worker per contract).
