# Lane L1 notes (NJ STRONG wave, 2026-11-04)

16 clusters in, 16 verdicts out (`verdicts.csv`, 22 columns, parses clean, cluster IDs match input).

| Verdict | Tier | Count | Clusters |
|-|-|-|-|
| VERIFIED_NEW_ORG | C | 11 | 00401 Ames Rubber, 00255 Master Bond, 00245 Monmouth Rubber, 00267 Exothermic, 00360 Flexabar, 00342 Microseal, 00516 All American Poly, 00595 Holocraft/Flexcraft, 00440 Triumph Plastics, 00412 Productive Plastics, 00534 Engineering Laboratories |
| VERIFIED_NEW_SITE | C | 2 | 00436 Sabert 879 Main St (ORG-003489), 00419 Mauser/BWAY Dayton (ORG-000717) |
| REJECT | - | 2 | 00679 Hudson Technologies (refrigerant reclaimer), 00398 Troy Chemical Newark (biocide/additive chemistry) |
| STILL_UNCERTAIN | - | 1 | 00387 A&C Catalysts / ACCI, Linden |

No DUPLICATE_OF: dedupe step 3 (street) returned no hit for any row. No closures found.

## Method
Read-only `atlas.py dedupe-check` (name, every name variant, street) plus a domain check for every company domain and an `rg` pass for brand names across `data/organizations_*.csv` and `data/sites_*.csv`. Own-site pages fetched with TinyFish and Jina; searches used for discovery only. Every `own_quote` was copied from a page I fetched, then re-checked programmatically against the live page (raw HTML, else Jina): 16 of 16 present, all 25 words or fewer. About 4-6 fetches per candidate.

## Flags for the integrator
1. **Sabert split address (00436).** Sabert's own contact page: corporate HQ / R&D Center is 2288 Main Street Extension, "our New Jersey plant is located down the street ... at 879 Main Street". Held SITE-003913 is "Headquarters and Sayreville Plant" at 2288. Not a street duplicate, so I issued VERIFIED_NEW_SITE; consider narrowing SITE-003913 to HQ/R&D. Tier C because the page does not say what is made at 879 specifically. ZIP 08861 is the federal row's; Sabert's own pages use 08872.
2. **Two held Mauser/BWAY organizations (00419).** ORG-006250 "Bway Corporation" (Cedar City UT, created 2026-11-04, no website, no parent link) and ORG-000717 "Mauser Packaging Solutions" (domain mauserpackaging.com, trade name BWAY). I attached Dayton to ORG-000717. The two should be reconciled. Own site lists Dayton only as "Small Packaging", so no processes tagged.
3. **A&C Catalysts (00387), scope question.** Epoxy curing agents and thermoset additives (Technicure, Technirez). Site names Linden as HQ and Harrisonville MO as the plant; resin production is stated company-wide, not for Linden. Settling fact: a source stating resin/polymer production at 1600 W Blancke St. If found, owner should rule whether curing agents/imidazoles are Ring 2 or precursor/additive chemistry (B6/B28).
4. **Troy Chemical (00398) is a scope reject from product profile, not a statement about Newark.** Own site never says what Newark makes. Reject rests on the B28 blending line; reopen if a permit (NJDEP PCP240003 packet, would not fetch) or Arxada page states polymer production there. Integrator may prefer STILL_UNCERTAIN.
5. **All American Poly (00516): address not seen in fetched page text.** The home-page location carousel is script-rendered (only North Little Rock AR renders in TinyFish and Jina; direct fetch is 403). The Piscataway address appears only in search snippets of the company's own pages, so the quote is activity_only and the plant link rests on federal rows. Please re-fetch /contact/ footer in a browser.
6. **HQ policy.** Where a company's own contact page prints a single company address (Exothermic, Microseal, Flexabar, Triumph, Productive, Engineering Labs, All American Poly) I used it as HQ and said so in `note`. Flexcraft prints several facilities and no HQ, so `org_hq_*` is blank. Master Bond, Ames and Monmouth state "headquarters" explicitly.
7. **Dead federal-name domains.** engineeringlabs.com is a parked GoDaddy page; the live site is plasticballs.com. Ames' domain amescorp.com (amesrubber.com redirects). Flexabar corrected street spelling: federal "RUGERS" vs own site "Rutgers University Boulevard".
8. **County left blank** where the federal row was blank (All American Poly, Flexcraft, Engineering Labs); not required outside Ohio. HQ counties for Flexcraft-type blanks were not inferred.
9. **naics_primary** set only when a single listed 6-digit code fits the own-site activity; blank for Microseal, All American Poly (mixed film/bag codes), BWAY and A&C/Troy/Hudson rows with no clear primary.
10. **Thin or dated pages:** Flexabar and Triumph pages are old and short (45-year-product language; (c) 2016). Triumph names no extrusion process, so only printing is tagged; Engineering Labs names no process or resin (its /materials and /products pages returned bot_blocked), so processes and materials are blank.
11. Process mapping judgments: Ames fluoroelastomer/fluorosilicone to `specialty_elastomers`; Monmouth gets only `foam_production_unspecified` (equipment listed, process not named).
