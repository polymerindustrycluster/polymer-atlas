# Lane I1 notes (2026-11-04)

18 clusters in; 18 verdict rows out (`verdicts.csv`, 22 columns, parsed clean).

| Verdict | Tier | Count |
|-|-|-|
| VERIFIED_NEW_ORG | C | 10 (Hoehn, Dorel, Titus Precision, Earthwise, OTECH, Exo-s, EFP, B&F, Toray Resin, Mossberg) |
| VERIFIED_NEW_SITE | B | 2 (D&W Fine Pack, Genpak Scottsburg) |
| VERIFIED_NEW_SITE | C | 1 (Latham Fort Wayne) |
| DUPLICATE_OF | - | 1 (Ashley Industrial Molding -> SITE-003559) |
| REJECT | - | 1 (Tri-Pac, scope) |
| STILL_UNCERTAIN | - | 3 (NYX New Albany, ACS Technical Products, Fiberglas & Plastic Fabricating) |

## Searches run
`atlas.py dedupe-check` by name plus street for the five clusters with hits (Precision Plastics, D&W, Genpak, Ashley, Latham), and by name for the other 13. `atlas.py show` on ORG-003120, ORG-002885, ORG-000416 and the Fort Wayne step-2/4 hits. No domain search (step 1) was run for any cluster. Web: 6 or fewer fetches/searches per cluster, company site first.

## Calls that need the integrator's eye
- **Ashley (LF-IN-00402):** the dedupe tool's step 3 missed the held site because of street spelling; held SITE-003559 is 310 South Wabash Street, Ashley. Treat as a duplicate.
- **Quote kinds:** where a page does not put plant and activity in one span, I used `plant_only` or `activity_only` and put the other half in `deciding_fact`. Several own-site pages are company-hosted PDFs (certificates) because the HTML pages never name the plant: Hoehn (June 2022, expired 2025), Exo-s (2021-2024), B&F (2025-2028). The integrator re-fetch of PDFs will see line breaks inside the quoted spans.
- **Tiering:** new organizations are C per the brief even where the own-site witness is strong (Hoehn, Titus, OTECH, B&F, Mossberg, EFP, Toray). Genpak is B on a plant_only witness plus trade press; its own page does not say what Scottsburg makes. Latham is C because the only witness is the SEC 10-K, not an own-site page.
- **Hoehn:** the cluster's F5500 EIN 475340441 and the OSHA/ITA name variants belong to Personnel Management Services Inc dba Express Managed Services, a staffing firm. The F5500 leg does not corroborate Hoehn itself.
- **Titus Precision:** the federal name PRECISION PLASTICS INC is the pre-Jan-2022 name; do not confuse with precisionplasticsinc.com (California). Dedupe step-4 hits (six other "Precision Plastics" orgs in OH/PA) are unrelated.
- **Exo-s:** HQ is Sherbrooke, Quebec; whether to record the Canadian parent or the US entity (Exo-s USA LLC) and which shard it belongs in is the integrator's call (AGENTS 3, Appendix C). Only `blow_molding` is tagged for Howe, from the certificate.
- **Earthwise:** street 100 Earthwise Way is not confirmed by the own site; two directories give 3661 S 800 W instead.
- **Toray Resin:** held Toray orgs (ORG-003164, ORG-004324, ORG-002963) are separate entities; no merge made.
- **Counties filled where the federal row was blank:** Wayne (B&F), LaGrange (Exo-s), DeKalb (Mossberg), from public geography, not from the federal row.
- **ACS Technical Products:** held as STILL_UNCERTAIN because the open question is a scope ruling (epoxidized-oil plasticizers and bio-based epoxy chemistry), which is an owner call under AGENTS 2.9. Propose it as a battery item if the pilot wants it decided.
- **NYX:** may be mold-making (Ring 3) rather than molding; the site was Beach Mold and Tool before the 2019 purchase.

## Not done
No Form 5500 check was needed (no reject for closure or non-establishment). The one REJECT is scope, resting on third-party descriptions of Tri-Pac (no own-site witness found; tri-pac.com returned a placeholder), so it is reopenable. No closure notices were found for any cluster; NYX and Exo-s had temporary layoffs in 2023 only.
