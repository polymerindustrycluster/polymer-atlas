# Ohio EPA air permits — CORROBORATION_ONLY, requested PTI/PTIO discovery held

Requested population: polymer-NAICS PTI/PTIO facilities in the18 counties from scripts/regions.PIC18. **Requested population count,20-row sample and dedupe yield are NOT MEASURED.** sample.csv is header-only; it must never be combined with the separate PBR fallback below.

## Route and terms

[Official issued-permit guidance](https://epa.ohio.gov/divisions-and-offices/air-pollution-control/permitting/issued-air-permits) raw-fetched HTTP200 states:
> The Ohio EPA eDocument System must now be used to search for air permits online.

The same page describes the old search as retired, and says:
> courtesy to the public and regulated community

These excerpts concern access, not a blanket license. The page bars altering/falsifying/misusing permit information. The linked privacy-policy route returned404; no automation-specific permission or restriction was successfully established there. No permit was altered or legal clearance claimed.

[Current eDocument portal](https://edocpub.epa.ohio.gov/publicportal/edochome.aspx) returned HTTP200 Request Rejected (244bytes), or a TSPD JavaScript/CAPTCHA challenge. NAS Firecrawl raw output contained the same challenge, not search results; HTTP variant also challenged. **HTTP200 is not a passed route.** No CAPTCHA attempted or bypassed. Available CUA browser inventory was empty; native Chrome failed cgWindowNotFound; no usable interactive browser. The legacy wwwapp permit path timed out; ebiz Air facility path returned a login-redirect shell (155bytes), not a public facility list. [Air Services guidance](https://epa.ohio.gov/divisions-and-offices/air-pollution-control/about-dapc/air-services) describes access delegation for regulated users; no account/login or delegated access requested.

No PTI/PTIO site or NAICS absence/closure is inferred from these route failures. A permit authorizes construction/operation under stated conditions; even a final issued permit does not establish current production. Draft-issued records cannot authorize installation/operation, per official guidance.

## Separate fallback: Permit-by-Rule (PBR), not PTI/PTIO

The official page links [Active Permit-by-Rule workbook](https://dam.assets.ohio.gov/raw/upload/v1719438323/epa.ohio.gov/Public/DAPC/PermitbyRule.xlsx), HTTP200, report generated2026-11-05 20:00:10 (source does not label timezone). SHA256 in pbr_counts.json. Workbook has **Whole workbook:19,443 emissions-unit rows /12,196 facility IDs**, plus1blank data row. **PIC-18 county-only filter:7,824unit rows /4,758facility IDs.** State OH filter:19,440unit rows/12,194IDs; PIC18 county plus state OH:7,822unit rows/4,757IDs. These are source-field filters, not a verified physical-geography census. Workbook has no NAICS or website columns. Fallback inclusion is an explicit case-insensitive polymer/plastic/thermoplastic/rubber/resin/urethane/composites/extrusion/thermoforming/injection-mold keyword in facility name OR emission-unit description, restricted to PIC18county and grouped by native facility ID. **33matching unit rows /21facility IDs.** These are21keyword leads, not21polymer plants. Aluminum extrusion, university backup generators and resin-handling support operations illustrate expected noise. No new scope/ring rule is adopted.

20 IDs sampled uniformly without replacement, seed20261106, sorted facility IDs: see pbr_sample.csv. Source-evidence verdicts **4DUPLICATE_OF held Ohio sites,16STILL_UNCERTAIN,0VERIFIED-new**. Measured fallback current-sufficiency yield **0/20=0%,95%WilsonCI0–16.11%**. This describes the government-workbook-only adjudication, not a six-fetch current own-site campaign, not the requested PTI/PTIO NAICS yield, and not a claim no new facilities exist. Full21-ID frame has4singleton street duplicates /17uncertain: exact held-street match rate4/21=19.05% (frame census). Sample exact-match rate4/20=20%,Wilson95%8.07–41.60%; this is overlap, not verified-new discovery yield. Normalized exact street matches only are conservative; abbreviations/unit differences can hide additional held sites, so unmatched is not new.

Dedupe uses all-shard atlas.dedupe: organization legal/trade name and aliases/notes plus site street with city/state/ZIP. Domain unavailable. Org-only hits never establish site duplication. `site_hits` singleton matches terminate at SITE-003470 (LyondellBasell Ashtabula) and SITE-000704 (Akzo Nobel Huron). Operator identity not changed. No closure REJECTs, no Form5500 closure conclusions. Every uncertainty names the current operator/process/site evidence needed.

Reproduce with installed openpyxl (no dependency added):
```
uv run --with openpyxl python tasks/source-scout-5-2026-11-06/ohio-air/build_pbr.py /tmp/l5c-pbr.xlsx
python3 tasks/source-scout-5-2026-11-06/check.py
```
Source input is fetched only via the official workbook URL above. Known positives and negative keywords are checked before building. Independent DuckDB census of workbook-exported CSV and native XLSX XML row counts reconcile; neither zeroes missing records. County geography is sourced from the workbook, never mailing-city inference. No coordinate fields exported.

| Hold | Settling fact | Recommendation |
|---|---|---|
| Requested PTI/PTIO polymer-NAICS discovery | Working permitted public eDocument search/export, covering PIC18 and source-stated NAICS (or a documented public bulk equivalent) | Hold requested count/sample/yield; do not substitute PBR or federal ECHO |
|17fallback uncertain siteIDs | Primary current polymer-process/operator and physical-address evidence; resolve abbreviated-address aliases | Packet only; no create/status change |

Geographic quality hold: `geography_anomalies.csv` preserves all3 non-OH-coded source unit rows across2facility IDs. `04-48-01-2010` has state IN, street “Out of State” and county `Out_of_state_county`. Both `13-18-00-8701` Circle K rows have state NC and a Raleigh NC street, but city Cleveland, ZIP44111 and county Cuyahoga. No conflicting field is preferred or corrected. Settling fact: an authoritative physical establishment address for each native facility ID. The two IDs are outside the keyword frame; all21keyword IDs are state OH, so the frame,20-ID sample and yields are unchanged. County-only counts must never be described as verified physical PIC18 establishments.

Current-main overlap refresh (main be76f04, after Grok9320c93 review): main's Ohio street-fill pass populated the previously empty street fields for held SITE-000462 (Mercury Plastics,15760 MADISON RD,Middlefield) and SITE-000570 (Quality Synthetic Rubber,1700 HIGHLAND RD.,Twinsburg). The shared matcher code did not change. The named oracle caught both new singleton street matches; builder replay changes only site_hits/verdict/duplicate_of/reason for those two native IDs (02-28-00-0043 and16-77-13-0080), in both frame and sample. Source identities, seed, geography, source counts and verified-new yield remain unchanged. Current frame:4duplicates/17uncertain among21IDs; sample:4duplicates/16uncertain among20IDs; overlap4/21=19.05%frame,4/20=20%sample (Wilson95%8.07–41.60%). Earlier two-duplicate counts and unchanged-output approval statements above describe the earlier held-Atlas snapshot and are superseded for current overlap. Both families must review this refresh; draft remains. No canonical rows changed by this lane.
