# Lane L1 notes (CA STRONG wave, 2026-11-04)

20 clusters in, 20 verdicts out (`verdicts.csv`, 22 columns, parses clean).

| Verdict | Tier | Count | Clusters |
|-|-|-|-|
| VERIFIED_NEW_ORG | C | 13 | 00097 Vista Paint, 00376 Westland, 00282 Laird, 01370 Westcoat, 01432 Merrill's, 00383 Wrex, 00982 Perf. Polymer Tech, 00765 Intl Coatings, 00894 Coastcraft, 02755 Labcon, 02866 N. American Fire Hose, 01114 Nuconic, 01594 Mercury Plastics (LA) |
| VERIFIED_NEW_SITE | B | 3 | 01781 Indorama Fontana (ORG-004245), 01455 Saint-Gobain Garden Grove (ORG-000035), 00821 Performance Composites Compton (ORG-004845) |
| VERIFIED_NEW_SITE | C | 1 | 02119 Altium Fresno (ORG-001408) |
| REJECT | - | 1 | 01570 rPlanet Earth Vernon (closed 2025-09) |
| STILL_UNCERTAIN | - | 2 | 01635 Rainin Oakland, 02875 Ronford/Hoffman Paramount |

No DUPLICATE_OF verdicts: no street hit anywhere (dedupe step 3 was 0 for every row).

## Tools and method
- Read-only `scripts/atlas.py dedupe-check` and `show` for every org/street, plus the input hits. Fetches via TinyFish fetch (raw page text, used for quotes), Wayback for two dead sites, search snippets for discovery. No `data/` edits, no git.
- Roughly 4-6 fetches per candidate. Every `own_quote` was copied from fetched page text (<=25 words, one continuous span) EXCEPT the Saint-Gobain Garden Grove quote, which comes from a search-result snippet because omniseal-solutions.com returned 403 / bot_blocked. Re-verify that one.

## Integrator flags
1. **rPlanet (01570) - Form 5500 check not run.** AGENTS rule 8 requires the EFAST2 address check before a closure REJECT; this lane could not run it. F5500 sponsor EIN 383978902 is a plan fact and blocks only if its address is 5300 Boyle Ave. Closure itself is dated and multi-sourced (Plastics News 2025-09-12, Recycling Today 2025-09-19, Recycling International 2026-05-21). Niagara Bottling bought the idle plant (May 2026) and plans to restart it; treat as a future lead, not an operating site.
2. **Name collision (01594).** Mercury Plastics (LA, PolyPak Packaging, mercplastics.com, LDPE film) is NOT held ORG-000431 (Mercury Plastics, Middlefield OH, Masco, mercury-plastics.com). Give the new org a distinguishing name. Federal street has a typo ("WASHINGTONG") kept as given.
3. **Westland (00376)** now sits on a Globe Composite Solutions subdomain; Globe is held (ORG-004046, Stoughton MA). Both are ESCO subsidiaries. I chose NEW_ORG (separate legal entity); integrator may prefer a sibling/parent link. ESCO is not held.
4. **Nuconic (01114)** is a sibling of held ORG-002637 Tray-Pak inside the Easypak group (Graham Partners). NEW_ORG, no merge; parent link is the integrator's call.
5. **Performance Polymer Tech (00982):** live pptech.com now serves an unrelated gambling page (domain re-registered). Witness is a Jan 2025 Wayback capture; this is not closure evidence (OSHA activity 2026-05-19) but operating status should be confirmed before create. Website field left blank.
6. **Altium Fresno (02119):** `current_atlas_hits` was blank but dedupe step 2 finds ORG-001408 by name. The only Fresno page is an Altium-branded SEO landing page naming the address with no activity statement, so tier C (plant_only). altiumpkg.com location pages are bot-blocked.
7. **Merrill's (01432):** own pages do not print Burlingame in fetched text (address blocks render empty). Confirm in a browser. Thermoforming term comes from the page title/meta.
8. **Rainin (01635):** own pages call Oakland the headquarters and place tip molding "in California" without a city; a new tip facility opened in Vacaville in 2022 (Wikipedia). Oakland may be instrument assembly only. Settling fact is in the row.
9. **Ronford (02875):** federal sponsor is a PEO. Same address hosts Hoffman Plastic Compounds (PVC compounds, since 1970). Entity and own-site tie unsettled; scope is clearly in.
10. **Owner-ruling candidates (not self-ruled):** North American Fire Hose (02866) is rubber-lined jacketed hose (NAICS 326220); Indorama Fontana (01781) is PET flake recycling (ring 3 vs 1); Rainin is a pipette/instrument maker.

## Field conventions used
- New organizations are always tier C per the brief, even with an own-site witness; sites under held orgs are B only when the own page names the plant.
- County filled by researcher (not federal row) for Labcon (Sonoma) and North American Fire Hose (Santa Barbara) where the federal county was blank; noted in each row.
- `processes`/`materials` only where the cited page (or a named sibling page on the same site) states them; blank otherwise. `coating_formulation` is taken from "coatings manufacturer / formulated products / proprietary formulas".
- `naics_primary` filled only where one code is clearly primary for the product (Vista, Laird, Westcoat 325510; Coastcraft, Westland, PPT 326291; NAFH 326220; Altium 326160); blank for mixed sets.
