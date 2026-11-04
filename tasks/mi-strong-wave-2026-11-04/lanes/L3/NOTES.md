# L3 notes (MI STRONG wave, 2026-11-04)

Input: 21 clusters. Output: `verdicts.csv` (21 rows). Nothing under `data/` was touched; no git run.

## Counts (unit: input clusters, this lane)

| Verdict | Rows | Tier column |
|-|-|-|
| VERIFIED_NEW_ORG | 15 | C (site-level B proposed in the note where an own-site witness exists) |
| VERIFIED_NEW_SITE | 2 | G&T Byron Center = B; Sherwin-Williams Holland = C (no own-site page) |
| REJECT | 3 | blank: Gage (scope), McGean-Rohco (scope), West Michigan Molding (closed 2023) |
| STILL_UNCERTAIN | 1 | blank: Dart Mason (Howell Rd) |
| DUPLICATE_OF | 0 | no street-level hit anywhere |

Tier convention matches the IN national pilot (NEW_ORG = C, NEW_SITE = B with own-site witness else C, REJECT and
STILL_UNCERTAIN blank).

## Dedupe
`atlas.py dedupe-check` run for every cluster (name + street + zip) and for every candidate domain. Street hits: none.
Org-only hits: Sherwin-Williams (ORG-000132 is the parent; ORG-000088 in fusion_refs is PPG, a notes mention only;
ORG-002886 CSW Industrials is also a notes substring), G&T (domain hit ORG-002475 at step 1, name hit ORG-002631 at
step 2; ORG-002475 used), Dart (ORG-002441, supplied by fusion). No domain hits for the other new orgs.

## Evidence quality flags for the integrator
- All 16 `own_quote` strings were re-fetched this session and matched exactly (page text, or pdftotext for the two CIE
  certificate quotes). All are 25 words or fewer. Gage has no `own_quote`; its 31-word sentence sits in deciding_fact.
- **West Michigan Molding (REJECT)**: EGLE report N2146 (2023-11-15): "ceased normal operations in July", equipment
  removed, status "Permanently Closed"; WARN closure notice 2023-07-20 (134 workers). Form 5500 check DONE from
  `tasks/form5500-spine-2026-11-01/sponsors.csv`: EIN 853347814 mails to 1425 Aerial View Dr (the establishment), but
  the latest filing (received 2025-06-12) is a FINAL short-plan-year return with 1 participant, so it is a plan
  wind-down fact and does not block. The cluster `latest_activity` 2025-06-12 is that filing's receipt date, not an
  OSHA inspection. Plastics News and Crain's returned 403; cited by headline only.
- **Sherwin-Williams Holland**: evidence is state regulatory (EGLE B7711, 2021), not own-site. Tier C.
- **Systex**: company website not found (domain guesses parked or unresolved; denso.com page 403). Only the LinkedIn
  self-description plus EGLE N7282 (about 90 injection machines, 13.6M lb resin per year). Tier C.
- **Packaging Personified**: weakest witness. Sparta appears only as a footer address; extrusion is company-wide.
- **US Farathane**: plant-named page (locations) and activity page (processes) differ; activity is company-wide.
- **Century Plastics (2 rows, same org)**: only a TUV ISO 14001 certificate hosted on cieautomotive.com names the
  plants; the company's own domain is parked. LF-MI-00348 is a second VERIFIED_NEW_ORG row for the same org as
  LF-MI-00962: create the org once and attach both sites.
- **Look-alike domains avoided**: grandtraverseplastics.com (spam content; real site gtpplastics.com), camcar.com
  (Textron fasteners), apacproducts.com (pipeline accessories). Directory "Closed" flags on Ironwood and Dart were not
  treated as evidence.
- **McGean-Rohco**: own home, story, capabilities and equipment pages checked; Livonia is a custom chemical toll plant
  (reactors, blending) with no polymer, resin, adhesive or sealant product stated.
- **Dart**: dartcontainer.com pages render empty without JavaScript, so no own-site page could be read; that is an
  availability signal only. Search-result descriptions point to an R&D and tooling campus, a scope question for the
  owner, not a lane decision.

## Items for owner / integrator
1. G&T Industries: two PA orgs (ORG-002475, ORG-002631) for one company; HQ on both is wrong per own site (Byron Center MI).
2. Century Plastics has more Michigan plants (Utica Dr x2, Quadrate Dr Plant 5, warehouses) per the certificate annex;
   not in this wave.
3. Federal county was blank for Shelby Twp, Williamsburg and Muskegon rows; filled from city.
4. Street corrections from own sites: McPherson (1347 East M-89), East Jordan (6400 M-32 Highway), A-Pac (2719 Courier
   Dr NW), Sherwin (trimmed trailing ", Holland").
