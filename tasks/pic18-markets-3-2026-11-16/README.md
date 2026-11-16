# PIC-18 markets_served re-pass 3 (MKT3), 2026-11-16 — applied

Claim: atlas-w16-mkt3, controller thr_9i2c6byhcz; designated integrator for this scope (AGENTS 2.7). First user: the Atlas owner, for prospecting by market; non-use is a finding if no prospecting list uses `markets_served` by 2026-12-16. No issue closed. Family review is pending.

## Frame, unit and filter

- Frame: **387 organizations** with at least one retained 2026-11-16 corpus page (pinned manifest snapshot, 745 attempted / 628 with retained pages), `markets_served` blank at base `d410968`, and not already filled by the two earlier lanes (PR #344, 32 organizations; PR #349, 15 organizations; listed in `prior_lanes.csv`, 47 total). Tiers: **A 175, B 175, C 35, U 2**.
- Order worked: tier A, then tier B, by Ohio employee band then org_id. A screening extractor surfaced market sentences from each organization's markets, industries, products, capabilities, home and about pages, and I read and decided each one that surfaced text. All 175 tier A and the first 78 of 175 tier B organizations were screened this way; tiers C and U and the rest of B were not reached.
- Stopped at the 35-minute limit.

## Result (all counts recomputed by check.py)

| Unit and filter | Count |
|---|---:|
| Organizations with a markets_served cell applied (blank before) | **79** (tier A 62, tier B 17) |
| markets_served values applied (one controlled tag each) | **225** |
| Evidence rows appended, EVD-389000 to EVD-389224 (all supports_A) | **225** |
| Organizations held in the frame (applied or held covers all 387 once) | **308** |

Applied by shard: organizations_OH.csv 77 cells / 218 values; organizations_MO.csv 1 / 2; organizations_US.csv 1 / 5. Yield: 79 of 387 frame organizations (20%); 79 of the 253 organizations actually screened (31%).

Holds (organizations, by class; settling fact in `holds.csv` and `reviewed_holds.csv`): **not_adjudicated 266** (not reached, or no market sentence surfaced; not evidence of absence); read and held with a reason: group_or_redirect_attribution 9, menu_or_nav_only 11, off_vocabulary_or_ambiguous_market 14, scope_attribution 5, no_market_text 2, no_vocab_market 1. Every frame organization appears exactly once as applied or held. A held cell is unresolved work, never a negative finding.

## Rules followed

- MARKETS vocabulary only; each tag needs its own wording in its quote (`WORDS` map in check.py, so "consumer goods" cannot become housewares, "Food & Beverage" cannot become food processing, a motorsport example cannot become sporting goods).
- Quote must appear, words in order, in the stored page text; raw SHA256 matches the manifest.
- Effect: a narrative sentence, or a content-page "industries/markets served" list (round-5 precedent), is supports_A. Navigation-only menus, product lists, group or redirect pages are held. No C-strength terms were written on tier A/B rows.
- Held on purpose: Alternative Energy (MUM, ORG-000455) and retail-security verticals (Checkpoint, ORG-002153) are not mapped to energy_renewables_battery or retail tags (B-MARKETS-VOCAB). Window, door and grille makers (ORG-000293) are tagged only where the page names the window/door product line.
- Only `markets_served` changed on organization rows; no sources, notes, last_verified or tier edits. Provenance is in the evidence rows.

## Named checks

- `python3 tasks/pic18-markets-3-2026-11-16/check.py`: PASS. Reconciles the frame against an independent count (ok pages x blank cells at base minus prior lanes), every quote, hash, vocabulary tag and per-tag wording, coverage, evidence IDs in block, and the full-tree boundary against base (79 cell fills, 225 evidence appends, nothing else). Injected defects refused: fabricated quote, off-vocabulary tag, broader tag than the words, missing disposition, tampered hash, duplicate proposal, dropped frame row (7/7).
- `python3 tasks/pic18-markets-3-2026-11-16/build.py`: idempotent; replay leaves the data diff byte-identical.
- `python3 scripts/validate.py`: PASS, 0 errors (41,916 evidence rows). `python3 scripts/check_row_loss.py --base origin/main`: OK. `python3 scripts/export_vocab.py --check`: current.
- Not run: `unittest discover -s scripts` (no script touched).

## Not checked

Source presence does not prove semantic fit; selection.tsv is the reviewable judgment and is not family-reviewed yet. Organizations whose pages surfaced no market sentence were not read in full. Reader-route pages (104 in the corpus) were screened with the same text. No fetches were made beyond the shared corpus. Boundary check compares to base `d410968`; a later main will differ by other lanes' rows.

## Proposed follow-ups

- Continue the frame from tier B rank 78 onward, then tiers C and U (266 not_adjudicated organizations).
- Owner rulings under B-MARKETS-VOCAB for Alternative Energy, retail-security verticals, water-heater, recreation-surface and window-covering cases listed in `reviewed_holds.csv`.
- Exact-entity checks for Rochling, Trelleborg, Huntsman, Survitec, LG Chem and ASC group pages before any market is copied to these rows.
