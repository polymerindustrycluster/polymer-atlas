# PIC-18 markets_served re-pass 3 (MKT3), 2026-11-16 — applied

Claim: atlas-w16-mkt3, controller thr_9i2c6byhcz; designated integrator for this scope (AGENTS 2.7). First user: the Atlas owner, for prospecting by market; non-use is a finding if no prospecting list uses `markets_served` by 2026-12-16. No issue closed. Family review is pending.

## Frame, unit and filter

- Frame: **387 organizations** with at least one retained 2026-11-16 corpus page (pinned manifest snapshot, 745 attempted / 628 with retained pages), `markets_served` blank at base `d410968`, and not already filled by the two earlier lanes (PR #344, 32 organizations; PR #349, 15 organizations; listed in `prior_lanes.csv`, 47 total). Tiers: **A 175, B 175, C 35, U 2**.
- Order worked: tier A, then tier B, by Ohio employee band then org_id. A screening extractor surfaced market sentences from each organization's markets, industries, products, capabilities, home and about pages, and I read and decided each one that surfaced text. All 175 tier A and the first 103 of 175 tier B organizations (278 in all) were screened with the full extractor; tier B rank 104 to 175 got only a stricter "industries / we serve" sentence filter, so organizations without such a sentence were not read. Tiers C and U were not reached.
- Stopped at the 35-minute limit.

## Result (all counts recomputed by check.py)

| Unit and filter | Count |
|---|---:|
| Organizations with a markets_served cell applied (blank before) | **77** (tier A 56, tier B 21) |
| markets_served values applied (one controlled tag each) | **213** |
| Evidence rows appended, all supports_A, from the block EVD-389000 to EVD-389237 (25 IDs retired, see below) | **213** |
| Organizations held in the frame (applied or held covers all 387 once) | **310** |

Applied by shard: organizations_OH.csv 76 cells / 208 values; organizations_US.csv 1 / 5. Yield: 77 of 387 frame organizations (20%).

Holds (organizations, by class; settling fact in `holds.csv` and `reviewed_holds.csv`): **not_adjudicated 260** (not reached, or no market sentence surfaced; not evidence of absence); read and held with a reason: group_or_redirect_attribution 9, menu_or_nav_only 11, off_vocabulary_or_ambiguous_market 14, scope_attribution 5, no_market_text 2, no_vocab_market 1. Every frame organization appears exactly once as applied or held. A held cell is unresolved work, never a negative finding.

## Rules followed

- MARKETS vocabulary only; each tag needs its own wording in its quote (`WORDS` map in check.py, so "consumer goods" cannot become housewares, "Food & Beverage" cannot become food processing, a motorsport example cannot become sporting goods).
- Quote must appear, words in order, in the stored page text; raw SHA256 matches the manifest.
- Effect: a narrative sentence, or a content-page "industries/markets served" list (round-5 precedent), is supports_A. Navigation-only menus, product lists, group or redirect pages are held. No C-strength terms were written on tier A/B rows.
- Held on purpose: Alternative Energy (MUM, ORG-000455) and retail-security verticals (Checkpoint, ORG-002153) are not mapped to energy_renewables_battery or retail tags (B-MARKETS-VOCAB). Window, door and grille makers (ORG-000293) are tagged only where the page names the window/door product line.
- Only `markets_served` changed on organization rows; no sources, notes, last_verified or tier edits. Provenance is in the evidence rows.

## Review repairs on #360 (Codex-20 and Gemini-h13 refutations of 4fbfe1e)

Withdrawn and held: **25 values / 8 organizations**; their evidence IDs are retired (never reused or renumbered; `withdrawn.csv` carries the original quote, hashes and a settling fact). Listed in `withdrawn.csv`:

| Organization | IDs | Class | Why |
|---|---|---|---|
| Dalin Mold / Rubber Mold Design ORG-001763 | 389231-389234 | article_not_own_markets | Educational article on what rubber injection molding can make |
| PolyMet Recovery ORG-001868 | 389158-389164 | menu_or_nav_only | Navigation dropdown; no narrative witness in stored content pages |
| Sealed Air - Automated Packaging Systems ORG-000237 | 389082-389083 | group_or_redirect_attribution | sealedair.com parent pages (Cryovac, parent medical films) |
| H & B Machine & Tool ORG-000361 | 389090-389093 | menu_or_nav_only | Footer brand tagline |
| Altor Solutions ORG-002146 | 389174-389175 | menu_or_nav_only | Mega-menu entry |
| Inter-Ion ORG-001681 | 389225-389228 | menu_or_nav_only | "Industries We Serve" tab-label list (narrative sentences exist on stored markets pages; replace in a follow-up) |
| Jet Di ORG-001744 | 389152 | tagline_or_header | Page-title tagline repeated in the header menu |
| Enterprise Rubber ORG-000026 | 389101 | generic_product_explainer | What rubber bump stops are used for in general |

Integra ORG-000455, EVD-389004: quote extended through "customers in the wastewater treatment industry." (the stored sentence), re-verified in order against the stored page and hash. This is the only changed claim; every other row is unchanged or removed.

Sweep of all 238 rows (99 distinct witnesses): `witness_class.py` checks every HTML witness for navigation, header, footer and menu ancestry and every URL for blog, news, article or guide paths; source domain is compared with the parent organization's domain; generic "X are used in" product explainers were read by hand. Flags that were class-name false positives (page-has-no-sidebar, wsite-not-footer, all-but-footer, quick-text-style-menu, avada-footer-scripts) were checked in the stored HTML and kept. Reader-route witnesses (no HTML: Integra, Steelastic, Professional Plastics) cannot be DOM-checked; their text reads as content paragraphs.

## Named checks

- `python3 tasks/pic18-markets-3-2026-11-16/check.py`: PASS. Reconciles the frame against an independent count (ok pages x blank cells at base minus prior lanes), every quote, hash, vocabulary tag and per-tag wording, coverage, evidence IDs in block, and the full-tree boundary against base (77 cell fills, 213 evidence appends, nothing else). Injected defects refused, each for its own reason: fabricated quote, off-vocabulary tag, broader tag than the words, missing disposition, tampered hash, duplicate proposal, dropped frame row, a navigation-menu witness, a blog/article witness, a parent/group-domain witness (10/10).
- `python3 tasks/pic18-markets-3-2026-11-16/build.py`: idempotent; replay leaves the data diff byte-identical.
- `python3 scripts/validate.py`: PASS, 0 errors (41,929 evidence rows). `python3 scripts/check_row_loss.py --base origin/main`: OK. `python3 scripts/export_vocab.py --check`: current.
- Not run: `unittest discover -s scripts` (no script touched).

## Not checked

Reader-route witnesses have no DOM check. Source presence does not prove semantic fit; selection.tsv is the reviewable judgment and is not family-reviewed yet. Organizations whose pages surfaced no market sentence were not read in full. Reader-route pages (104 in the corpus) were screened with the same text. No fetches were made beyond the shared corpus. The frame is frozen at base `d410968`. After main moved to `89d9e46` the packet was replayed onto it by cell-replay merge (data files taken from main, `build.py` re-applied; lane delta unchanged: 85 cell fills, 238 evidence appends), and the boundary check compares to `89d9e46`.

## Proposed follow-ups

- Read the 260 not_adjudicated organizations (tier B rank 104 onward in full, then tiers C and U).
- Owner rulings under B-MARKETS-VOCAB for Alternative Energy, retail-security verticals, water-heater, recreation-surface and window-covering cases listed in `reviewed_holds.csv`.
- Exact-entity checks for Rochling, Trelleborg, Huntsman, Survitec, LG Chem and ASC group pages before any market is copied to these rows.
