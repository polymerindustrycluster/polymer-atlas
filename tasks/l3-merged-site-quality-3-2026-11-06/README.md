# L3 final merged-site quality census

Current/final batch under the controller's merged-only quality assignment. The 2026-11-06 conservation instruction supersedes continuation: finish this nine-site frame and existing review fixes; start no new batch. No canonical data changes, promotions, creates, registry links, evidence rows, or status assertions.

Acceptance was recorded in LANE_BRIEF.md and this README before research/application. The frozen frame is the nine C establishments created by merged PR164 (four MO, five SC), on main 98cd9aeaefa13a1b6990f0f46db7831ab4ec5bb0. Every site receives exactly one verdict. All nine are STILL_UNCERTAIN with a named settling fact in holds.csv. This is a quality hold, not a withdrawal of a merged site. No owner scope/ring/vocabulary ruling or absence/closure inference is made.

| Frozen quality packet | Establishments reviewed | C→B proposals | Holds |
|---|---:|---:|---:|
| PR216 (Watson + merged LA) | 3 | 1 | 2 |
| PR232 (merged MN/NJ) | 15 | 6 | 9 |
| This packet (merged MO/SC) | 9 | 0 | 9 |
| Distinct L3 establishments born at C | 27 | 7 | 20 |

The independent check derives all 27 birth sites from exact creation classes plus Watson SITE-012001, and proves the three frozen frames are disjoint and exhaustive. Prior-frames.csv cites immutable source commits for the 18 earlier site IDs. Earlier seven upgrades remain proposals subject to their own review; this packet changes none of them.

## Settling facts

| Site | Outstanding primary fact |
|---|---|
| Buckhorn Springfield SITE-012107 | Own-issued local manufacturing witness at the held street; catalog capabilities remain company-wide. |
| Sealed Air Saint Joseph SITE-012118 | Local polymer-film activity; the admitted local job describes flexographic printing of packaging. |
| Graham Joplin SITE-012127 | Own-issued local bottle process tied to the held street. |
| Spartech Cape Girardeau SITE-012148 | Same-street ZIP reconciliation: own 63702-0758 versus filed 63701. |
| Michelin Piedmont SITE-012181 | Same-establishment bridge from own Tweel plant page to filed Michelin PMG, 1610 Old Grove Road. No claim they are different is made. |
| American Roller Rock Hill SITE-012198 | Local rubber-roll-cover activity, rather than global product offerings plus the footer address. |
| Amrize Wellford SITE-012199 | Local thermoplastic-manufacturing description versus filed rubber-membrane activity, plus issuer/operator treatment. |
| Sterilite Clinton SITE-012219 | Own local polymer-process witness; corporate product statement and script-only career search do not settle it. |
| Berry Greenville SITE-012226 | Local bottle process and street binding; Amcor Greenville EHS job supplies neither. |

All nine admitted hold observations were raw fetched during this quality pass. Holds-sources.json records exact quote, URL, extraction path, SHA256 and retrieval date. Eight use this batch's source text; Graham uses the same-day quality2 raw fetch of the identical company page and Sterilite uses this batch's live raw homepage. Firecrawl fallbacks request live rawHtml (maxAge=0), never AI summaries. Buckhorn PDF uses curl/browser UA and pdftotext. Discovery-raw.json records initial probe attempts, not absence findings. Failed routes/404s/script shells are availability only; no quote from them is admitted as substantive evidence.

Primary route budget approximately six per organization, counting fallback routes: Buckhorn ≤5; Sealed Air 3; Graham 2 plus the already held same-day source; Spartech 2; Michelin 3 including a redirected search result; American Roller 5; Amrize 3; Sterilite 6; Berry 6. No exploratory re-crawl after conservation. Three known published positives (MO-00088, MO-00023, SC-00082) and three fabricated suffix negatives calibrate the reused house matcher; no new matcher/fetcher was introduced. Full nine-hold census rechecked, not sampled. Native personal/entity catalogue coverage is incomplete on this Mac; no catalogue miss is treated as absence. Only public company material and existing public federal records were used, with no personal, PIC CRM, vault, or licensed content copied into the packet.

## Checks

`python3 tasks/l3-merged-site-quality-3-2026-11-06/check.py --negative-controls` PASS: exact nine merged-only verdicts, 27-site aggregate, nine raw positive/fake-suffix receipts, three known answers, byte-identical all-canonical replay. Injected VERIFIED and substituted site-ID faults invoke the actual builder and fail before any verdict/data write; fabricated hold quote also fails. Every canonical CSV remains identical to pinned main. The idempotent builder reproduces verdicts.csv and has no canonical write path. No scripts/ edits, so the full scripts pytest suite is not rerun.

`python3 scripts/validate.py`: 0 errors. T3 uses scripts/build_qcew_denominators.py atlas_numerators and the held QCEW2023 private denominators: MO 47/368 and SC 56/406 before=after, as recorded in t3.csv. Ratios compare establishment counts, not matched coverage. No canonical cell changes, so no numerator/share changes. Historical PR164 reported SC57; pinned main is SC56 because merged correction 5294bb7/408713b set Yokohama SITE-012023 closed from dated issuer/WARN evidence. That separate merged status correction is preserved; it is outside this C-site quality frame.

Reserved EVD304300–304353 slots remain entirely unused and permanently unavailable for reuse; no ORG/SITE IDs allocated. Earlier EVD304012–016 and quality2 slots304100–304189 remain untouched. IDs stay within the controller's EVD300000–309999 block.

Two-family first refutes pending; no Ready/Done/merge claim. Controller alone merges and changes tracker status. First user: controller/research integrator, review date 2026-11-06. This packet resolves the coverage census, not the 20 primary-source holds across all quality packets. Current operation and unresolved holds were not certified.
