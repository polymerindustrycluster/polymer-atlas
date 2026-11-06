# IFS Coatings, Gainesville TX site — 2026-11-06

Controller task D (thr_9i2c6byhcz). This creates the Gainesville plant of IFS Coatings, Inc. (ORG-013500, merged in #243) as a site. First user: the campaign integrator, 2026-11-06. If nothing uses this record by 2026-11-13, record that as a non-use finding.

## Change (applied by `build.py`, idempotent)

**SITE-019100 "IFS Coatings - Gainesville"** goes in `sites_TX.csv` under ORG-013500:
- type `hq_and_plant`: the certificate names it the "design & manufacture, sales & central function" site;
- 3601 North I-35, Gainesville, TX 76240, county Cooke (`county_source physical_address`);
- ring 2 `coating_formulation`, NAICS 325510 from ITA, status active, **tier B**;
- coordinates and employee band left blank.

**9 evidence rows, EVD-332011 to EVD-332019,** in `evidence_sites_TX.csv`. Every active-site must-have claim (existence, address, scope, code, parent, activity, liveness) has at least one `supports_B` row.

| Claim | Rows | Witness |
|---|---|---|
| existence | 332011 own_site B; 332012 government_filing B | certificate line "3601 North I-35, Gainsville, TX 76240 – Design & manufacture, sales & central function." (the certificate's own spelling); ITA 73137 "IFS Coatings, Inc.(Texas)", 3601 N Interstate 35, 76240 |
| address | 332013 own_site B; 332014 registry C | certificate "With Central Functions At: 3601 North I-35 Gainesville, TX 76240"; county row below |
| scope | 332015 own_site B | "Design & Manufacture of thermosetting powder coatings & thermoplastic coatings." |
| code | 332016 government_filing B | ITA 73137 NAICS 325510, "Powder coatings manufacturing" |
| parent | 332017 own_site B | certificate "IFS Coatings, Inc. With Central Functions At: 3601 North I-35" |
| activity | 332018 own_site B | same site line as existence (one observation, two claims, two rows) |
| liveness | 332019 own_site B | "Certificate Issued: April 14, 2026" |

**Tier B** follows the CAMPAIGN convention: a federal record plus an own-site witness re-fetched raw and found verbatim. I re-fetched the certificate on 2026-11-06. It is byte-identical to the #243 copy (sha256 `5c32583138f5…cd12a1`), and its text is committed here with the phone number removed.

**County.** The Census address matcher returns no match for this I-35 frontage address in six spellings. Instead, I fetched the live FRS record for 110059616973 on 2026-11-06. It gives county COOKE, FIPS 48097, at point 33.66818, -97.15134. A Census coordinates lookup at that point returns Cooke County, GEOID 48097. Both receipts are committed (`frs_110059616973_2026-11-06.json`, `census_county_2026-11-06.json`). FRS gives ZIP 76241, while the own site, ITA and OSHA all give 76240; I used 76240.

**Dedupe** (`python3 scripts/atlas.py dedupe-check`, including the step-5 site_name search):
- Step 1 hits only the parent ORG-013500 itself (ifscoatings.com), which is expected.
- Street search finds 0 hits for "3601 North I-35" and "3601 N Interstate 35".
- The only site_name hit is SITE-006097 Ardmore, on a different street.
- None of the 8 other Gainesville TX sites is at 3601. The nearest is PPG and MFG Texas at 3333 N I-35.

## LF-TX-00505 (held in #170, tasks/corroborated-tx-2-2026-11-06)

This note records the lead's resolution here; the merged packet is not edited. The hold named the parent of record as its settling fact. That fact was met when #243 created ORG-013500 and showed the Ardmore site belongs to it. The lead is now **VERIFIED and applied as SITE-019100**, with the evidence above. OSHA inspection 346783756 and FRS 110059616973 (325510 and 326299) are cited in the site's sources. The 326299 code that put the cluster into #170's cohort does not change the site's primary code. The site sits in Ring 2, so it does not enter #170's strict-326 QCEW numerator.

## Fetches

- Certificate PDF: 1 re-fetch.
- Census geocoder: one service, six address forms plus one coordinate lookup.
- FRS REST: 1.
- Everything else reuses the #170 and #243 extracts.

## Checks

- `python3 tasks/ifs-coatings-gainesville-2026-11-06/check.py`: PASS.
  - Against the merge-base, only `sites_TX.csv` and `evidence_sites_TX.csv` change, by exactly the new rows.
  - All 9 witnesses re-check, and all 7 must-have claims are at `supports_B`.
  - Four injected defects fail: a fabricated quote, the wrong county FIPS, the Ardmore ITA record, and a missing parent row.
  - A rebuild leaves the bytes unchanged.
- `python3 scripts/validate.py`: OK, 0 errors (V-25 accepts tier B).
- `python3 scripts/check_row_loss.py --base origin/main`: OK.
- No council review was run (controller override). The controller routes review.
