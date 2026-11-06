# Polyurethane Manufacturers Association — CORROBORATION_ONLY, 2026-11-06

Selected from A-06 because the live public list is static HTML with company links. PPI's [terms](https://www.plasticpipe.org/PPI-Home/ContentAreas/Terms-and-Conditions.aspx) bar bots/data mining; AMBA's direct route returned a challenge. PMA provides the useful crawlable route among these tested alternatives; the other four suggested directories were not exhaustively compared.

Route: HTTP 200 headless GET of [Meet our Members](https://www.pmahome.org/meet-our-members). No login, API or bulk file needed. Polymer-discovery slice: **95 distinct named entries in the Processor Members section**, counted against 95 HTML list elements; this is a directory section, not 95 verified polymer operators. Excludes supplier/service/academic/individual categories. Personal members were neither sampled nor exported. The live page changes; the observed sample is the pinned snapshot, not the entire roster.

Terms check: the footer's `/privacy-policy` resolves to login, so **no usable public terms clause granting republication was available to quote**. [robots.txt](https://www.pmahome.org/robots.txt) says `Crawl-delay: 10` and does not disallow the public member-list path; this is a route policy, **not permission or a substitute for terms**. Rights remain a hold. The list was fetched once; company verification requests went to separate domains. Do not publish a bulk roster or mint member_of edges until rights are resolved.

Sample: seeded uniform draw without replacement, seed 20261106, 20 of 95 processor entries in page order. Verdicts: **3 VERIFIED new organization leads, 7 DUPLICATE_OF, 10 STILL_UNCERTAIN**. Measured verified-new yield **3/20 = 15.0%, 95% Wilson CI 5.24–36.04%**. Three new leads: Chemi-Flex (Lombard IL), ABCO Subsea (Houston TX), Meridian Laboratory (Middleton WI). Each has primary polymer-product language and a public US business address, raw re-fetched (`raw_checks.csv`: six word-order checks using the house evidence-repair normalizer); all-shard domain/name/street/trade-name checks returned no hit. Organization leads only: no plant status or site scope inferred. `sample.csv` retains minimal quotes, URLs and verdicts; no data records or edges are applied.

Domain/name and aliases use the existing `scripts/atlas.py` dedupe function across all organization shards plus ecosystem. Street checks apply when a primary address was obtained; blank streets mean uninspected, never no match. Seven singleton domain/name matches terminate at held IDs. Substring-only matches, multiple IDs and the Universal Seal→HM Royal domain/operator ambiguity are STILL_UNCERTAIN. Failed fetches remain uncertain and were not treated as absence. At most four requests per entry; no closure REJECTs.

Known-answer check: Goodyear ORG-000003, Avient ORG-000001, Lubrizol ORG-000002 resolve with the shared matcher (`../build.py`). The parser boundary was corrected before sampling: `<h3><span>Supplier Members</span></h3>` must end the processor frame; the earlier 146-entry mixed frame was discarded, not used for yields.

| Hold | Settling fact | Recommendation |
|---|---|---|
| PMA publication rights | Accessible terms or written permission for directory-derived public membership edges | CORROBORATION_ONLY until resolved |
| 10 uncertain sample entries | Primary polymer operation/identity and address, or operator linkage for ambiguous duplicates | No create/merge from a roster category alone |
