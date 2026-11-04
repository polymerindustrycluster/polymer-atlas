# Lane L2 notes (TX STRONG wave, 2026-11-04)

Input: 21 clusters. Output: `verdicts.csv` (21 rows, all clusters covered; coverage and 25-word quote cap checked by script).

## Counts (verdict, tier)
- VERIFIED_NEW_ORG: 8, all tier C (Altamira, Jamak, Plastech, Proske, Doskocil/Petmate, Minigrip, CKS, Waco Boom)
- VERIFIED_NEW_SITE: 6 (tier B: Silgan Houston under ORG-001115, Aurora Pasadena under ORG-001477; tier C: Genpak Carthage ORG-003472, Berry Victoria ORG-002544, Sealed Air Pflugerville ORG-000566, DAP Dallas ORG-001474)
- STILL_UNCERTAIN: 6 (Marian Fort Worth, CE Shepherd, WNA Lancaster, CATEC, Rohart, Ponderosa)
- REJECT: 1 (ENF Kyle)
- DUPLICATE_OF: 0. `atlas.py dedupe-check` found no street (step 3) hit for any of the 21.

## Method
- Dedupe: `atlas.py dedupe-check --name/--street/--city/--zip` for all rows, plus `--domain` for new-org websites. Only domain hit: inteplast.com = ORG-003476 (affiliate of Minigrip, see below).
- Own-site fetches used WebFetch, which summarizes with a small model. Every `own_quote` was reported verbatim by the fetcher, not seen as raw HTML. **The integrator's re-fetch is the real check.** Weakest quotes: Plastech (page title), Silgan (assembled from separate lines of a locations list), Marian (short phrase).
- Effort cap respected (about 6 fetches or fewer per organization). When the cap ran out without a primary signal the verdict is STILL_UNCERTAIN.

## Flags for the integrator
1. **Altamira**: the federal address 10633 W. Little York is the Corporate Headquarters on Evantic's locations page. Manufacturing is at 6455 Clara Rd Ste 300, Houston 77041, which is what the row uses. Decide HQ-office site versus plant site. The PTFE/PEEK quote is Evantic-wide, not Houston-specific.
2. **Berry Victoria** is the weakest VERIFIED row: no own-site page, scope from Resource Recycling 2020-02-05 and job posts. Berry merged into Amcor (2025-04-30, secondary source); check the parent of record. Downgrade to STILL_UNCERTAIN if an own-site witness is mandatory.
3. **Sealed Air Pflugerville** and **Genpak Carthage** and **DAP Dallas** are federal-only tier C. Their quotes are company-level activity statements; processes and materials were left blank on purpose (no parent-capability inheritance, SCHEMA B14).
4. **Minigrip**: witness is the Inteplast Group page (affiliate). Atlas holds Inteplast Group as ORG-003476; I did not attach Minigrip as its site because the page only says "affiliate".
5. **CKS Packaging**: input county was blank; Dallas County used. Own site never names Dallas. ZoomInfo snippet says an office move from 2818 Merrell Rd was planned for June 2026; not dated closure evidence.
6. **CE Shepherd**: the own site calls 2221 Canada Dry the "Main Office" and says it has two Houston plants (wire welding/PVC coating; plastics division), without saying which is at that address.
7. **ENF Kyle** REJECT is a scope reject (fine chemicals and thinners for semiconductors), not a closure. Per the B28 blending line. Form 5500 check not applicable: the plant exists and is not being rejected as closed.
8. **Rohart**: MapQuest "Closed" flag is not dated closure evidence, and Form 5500 F5500:741610645 is on file, so no reject.
9. Failed or unreadable fetches (not evidence): dap.com/about-us 404, sealedair.com/locations 404, Silgan and Ponderosa PDFs unreadable, novolex.com/locations Lancaster row not visible, genpak.com pages name no Carthage.

## Nothing skipped silently
No personal data, emails or phones recorded. No git, no edits under data/.
