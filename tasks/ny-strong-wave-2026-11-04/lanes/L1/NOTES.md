# Lane L1 notes (NY STRONG wave, 2026-11-04)

Input: 17 clusters. Output: `verdicts.csv` (17 rows, one per cluster, brief column order).

## Counts (unit: input clusters)
| Verdict | n | Clusters |
|-|-|-|
| VERIFIED_NEW_ORG | 12 | 00331 Alliance, 00528 Mechanical Rubber, 00380 Poly Craft, 00334 Tessy, 00491 XTO, 00315 Shelter, 00324 Schluter, 00497 Currier/Alentra, 00495 Staroba, 00519 RubberForm, 00287 CRM, 00486 LeRoy |
| VERIFIED_NEW_SITE | 1 | 00120 Corning Oneonta under ORG-004846 (tier B) |
| REJECT | 3 | 00136 Poly-Pak (closure), 00171 Aldon (chemical blender), 00043 Ames Goldsmith (silver powders) |
| STILL_UNCERTAIN | 1 | 00205 Saint-Gobain Poestenkill (own-site page bot-blocked) |
| DUPLICATE_OF | 0 | no cluster has a held site at its street (step 3 empty for all 17) |

Tiers: new orgs C, Corning site B, per the brief.

## Flags for the integrator
1. **LF-NY-00528 Mechanical Rubber.** Domain mechanicalrubber.com is held on ORG-000119 (Mechanical Rubber Ohio LLC, Strongsville), which the company's own 2020 release says it acquired (Durox). The Warwick plant is the group headquarters and is run by the parent entity. I wrote NEW_ORG for the parent and recommend linking ORG-000119 under it; the fallback is NEW_SITE under ORG-000119.
2. **LF-NY-00136 Poly-Pak** is a REJECT on a dated closure (WARN Jan 2025, May 1 2025 layoffs, property sale closed Aug 2025, demolition). The quote is LIBN trade press; the company domain now redirects to NAP Industries (Newark NJ). Form 5500 check (rule 8) done on both EINs at this address: 112286527 plan year 2020 (received 2026-04-03) and 112286547 plan year 2023 (5500-SF, received 2025-10-13). Both are address-matched; I read the gate as a currency test (both plan years precede the May 2025 closure), which you must confirm. If read literally, the verdict becomes STILL_UNCERTAIN. The fusion latest_activity 2026-04-03 is the 5500 receipt date; the latest OSHA inspection is 2023-03-08. Poly-Pak itself may still operate elsewhere.
3. **LF-NY-00120 Corning Oneonta.** The release says tissue-culture flasks and roller bottles; Corning's own Oneonta job posting (2026-10-25) states plastic parts, regrind buckets and cap hoppers, which settles plastic. No resin or process is named, so materials and processes are blank. fusion_refs ORG-001007 is Owens Corning, wrong; the right held org is ORG-004846.
4. **LF-NY-00205 Saint-Gobain Poestenkill** is probably a NEW_SITE under ORG-000035 but the plant page is behind a bot wall (tinyfish, WebFetch and Jina all failed). Open it in a normal browser and copy a span.
5. **Scope questions (owner rulings, not self-ruled).** XTO (die-cut gaskets from purchased sheet), Schluter (foam panels and shower trays inside a mostly metal and mortar tile-systems maker), CRM (scrap-tire crumb rubber: Ring 3 vs Ring 1), Poly Craft (flexible packaging converter). Verdicts are VERIFIED with the question named in `note`.
6. **Identity.** Currier Plastics is now Alentra (currierplastics.com redirects to alentracdmo.com); legal name left as the federal one. Staroba shares its address with EcoStar LLC.
7. **HQ.** For single-site companies with no 'headquarters' wording (Poly Craft, XTO, LeRoy, Schluter) the HQ is the single address printed on the site. Shelter's header carries both 12407 (typo) and 12047. CRM's HQ is Newport Beach CA; its Albany plant prints Colonie, NY 12205 (city changed from ALBANY per brief).
8. **County.** Supplied by the lane where the federal row was blank (Warwick, Liverpool, Holland, Lockport, Auburn, LeRoy); CRM HQ county (Orange, CA) too. Verify.
9. **Quotes.** All copied from pages fetched this session via tinyfish fetch_content (one curly-apostrophe sentence avoided). The Currier quote spans an address block and a description that the page renders as separate lines; whitespace joined with single spaces.

## Method
Dedupe: `atlas.py dedupe-check` by name (all variants), street+city+ZIP, and domain for every cluster; text grep of the org and site shards for brands (Alentra, EcoStar, NAP, PolyPak, Aldon, Ames, Schluter and others). Hits: ORG-000119 (domain), ORG-004846 (name and domain), ORG-000035 (name and domain). Unrelated hits ignored: "PolyPak Packaging" (Mercury Plastics group, not Poly-Pak Industries), ORG-002560, ORG-002913, ORG-001929.
No `data/` edits, no git. Helper script: scratchpad `l1_write.py` (appends one row per verdict, asserts quote length of 25 words or fewer; vocabulary terms checked against SCHEMA 3.1 and 3.2, 0 unknown).
