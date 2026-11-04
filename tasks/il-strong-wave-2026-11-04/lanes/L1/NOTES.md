# Lane L1 notes (IL STRONG wave, 2026-11-04)

Input: 21 clusters. Output: `verdicts.csv` (21 rows, 22 columns). No `data/` edits, no git.

## Tally
- VERIFIED_NEW_ORG, tier C: 11 (Hoffer, Demgy Chicago, Com-Pac, R.M. Lucas, Rogan, Williams Hayward, Fabrik, Magenta, Central Ink, P&P Industries, Elgin Molded Plastics)
- VERIFIED_NEW_SITE, tier B: 2 (WinCup West Chicago under ORG-000984; Logoplaste Plainfield under ORG-000935)
- STILL_UNCERTAIN: 6 (Eichrom, Pactiv Bridgeview, Pactiv Frankfort, Parker Woodridge, Nalco Clearing, Technipaq)
- REJECT: 2 (CCI Lemont, Koppers Stickney)
- DUPLICATE_OF: 0. Street-level dedupe found no held site at any of the 21 addresses.

## Method
- Dedupe: `scripts/atlas.py dedupe-check` (name, street, domain where known) plus `show` on every org named in `current_atlas_hits`.
- Own-site text was read with WebFetch and, for verbatim checking, tinyfish `fetch_content` (full page text). Quotes marked verified were checked against the tinyfish text: Hoffer, Com-Pac, R.M. Lucas, Elgin Molded, Magenta, Fabrik, Williams Hayward, WinCup, Logoplaste, Central Ink, P&P (partial), Demgy.
- Quotes NOT checked verbatim against full page text (integrator should re-fetch): Rogan (JS-rendered; quote is the rendered heading with a U+2011 hyphen), CCI (relayed by search summary), Koppers (8-K phrase relayed by the fetch tool), Technipaq (meta description).

## Judgement calls the integrator should look at
1. "Federal sources only = tier C" was applied only where a company page shows in-scope work. Where no reachable company page showed in-scope work for the plant (Pactiv x2, Parker, Nalco, Technipaq, Eichrom), the verdict is STILL_UNCERTAIN, not a federal-only VERIFIED. Pactiv and Parker have a high prior of becoming VERIFIED_NEW_SITE once a page is readable.
2. Blocked routes (availability signals only, not evidence): parker.com (403 / bot_blocked), icims and dejobs job boards (410, bot_blocked, redirect), illinoisjoblink (401), investors.koppers.com (403), logoplaste.com via WebFetch (ECONNREFUSED; readable via tinyfish).
3. Central Ink (ink maker): Ring 2 inks need a polymer/resin binder; the pages never say so. Scope flag in the row.
4. Logoplaste: ORG-000935 is a plant-named org ("Logoplaste Lima"); the same domain covers all US plants. Integrator decides whether to rename or parent before attaching Plainfield. Plants page also lists a separate LOGOPLASTE CHICAGO.
5. WinCup: ORG-000984 shows HQ Mount Sterling OH; WinCup's contact page prints HQ Atlanta GA and lists Mount Sterling and West Chicago as plants.
6. R.M. Lucas: the cluster carries two ECHO IDs; the About page lists a second plant at 3211 S. Wood St, Chicago.
7. Magenta: search results (not own site) report a 2024 acquisition by NewCo Plastics; own site still says family-owned.
8. Counties left blank where the federal row has none (Fabrik, Magenta, Central Ink, P&P, Elgin); not inferred.
9. Nalco: Ecolab prints 6233 W. 65th St; federal row 6216 W 66th Pl. Treated as unconfirmed same campus.
10. Koppers REJECT is scope (coal-tar distillation), not closure; the 2026-05-08 wind-down is conditional on union bargaining and is not a dated outcome. Form 5500 check not run because no REJECT here rests on closure or no-establishment.

## Searches run per record
Name, street (and domain where an own site was known) via `atlas.py dedupe-check`; for the nine records with org hits in the input, `atlas.py show` on the hit org ids.
