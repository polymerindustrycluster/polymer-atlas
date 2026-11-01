# OSHA ITA Form 300A (CY2025) polymer value-chain establishments - 2026-11-01

**Status: lead and proposal product, not Atlas data.** Nothing here edits `data/`, allocates an ID, sets a tier, changes a status, decides a ring or mints a registry link. Built by `scripts/build_osha_ita.py` (stdlib; re-runnable; self-contained - it does not import `build_echo_spine.py`). Packet lane output: the integrator of record decides what, if anything, is applied. Keys are the ITA `establishment_ID` values as filed (not Atlas IDs).

## 1. Provenance, input, raw counts

- **Source:** OSHA Injury Tracking Application (ITA), Form 300A establishment-specific summary data, calendar year 2025 (`year_filing_for` = 2025 on every row). Public dataset: <https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data>.
- **What was supplied:** an owner-supplied, **filtered** extract downloaded by the repo owner (`filtered_full_value_chain_ITA_300A.tsv`, SHA-256 `69c0d987d453471293b092640b392eaef44b21cb55446a1c9b69ad8b54bf703a`, tab separated). **The filter the owner applied is not known in detail** (the file name says 'filtered full value chain'; the content shows NAICS-driven selection, see section 2). This packet therefore says nothing about ITA filers outside the extract, and the absence of an establishment from the extract is not evidence of anything. The raw file is **not** in the repo and was only read in isolated mode (`python3 -I`).
- **Rows (unit: ITA establishment records, one `establishment_ID` each):** **11,194**. **Count reconciliation (AGENTS 2 rule 10c):** the brief said 11,193; this packet counts 11,194. The file has 11,194 newline characters and does **not** end with a newline, so `wc -l` (11,194) already equals the record count when the last record is unterminated, and 'wc -l minus the header' undercounts by one. Checked three ways: CSV parse with and without quote handling, and a raw tab count (every physical line has 31 tabs = 32 columns). `establishment_ID` and the ITA row `ID` are both unique (asserted, rule 10b); no record was dropped or merged. Every `date_submitted` is in 2026 (CY2025 filings submitted in the 2026 window).
- **Columns kept in the packet:** identity (IDs, names, address, EIN), NAICS (code, vintage, description), size (`size` code, `annual_average_employees`) and the filing date. **Never written:** all injury/illness columns (`no_injuries_illnesses`, deaths, DAFW/DJTR cases and days, injuries, skin/respiratory/poisoning/hearing/other illness totals). `total_hours_worked` is used in memory for one plausibility screen on the employee count and appears in outputs only as the flag `hours_per_employee_screen`.
- **Cleaning applied (unit: records):** zip restored to 5 digits where ITA dropped leading zeros: 754 records (`zip_as_filed` keeps the original); EIN restored to 9 digits for 484 records whose IRS prefix is 01-06 (`ein_quality = zero_padded`), 2,185 records carry an EIN that is blank or unusable and are never grouped (blank 2,125; invalid length or placeholder 60); a numeric prefix such as `4006 - ` in an establishment name is stripped for matching only.
- States/territories present: 53 (TX 987, OH 918, CA 617, PA 602, IL 592, MI 516, GA 495, IN 471, WI 419, NC 417, ...).

## 2. NAICS classification against SCHEMA 2.2 (label only, no ruling)

Each row's `naics_code` (employer-entered on the ITA form; `naics_year` mixes vintages: 2012 4,844, 2017 53, 2022 6,297) is looked up in SCHEMA section 2.2. `scope_class` is a label, **not a ring decision**: Ring is decided by the section 1 tests (SCHEMA 2.1: NAICS never decides a ring; AGENTS 2.9: scope is an owner ruling). Core = a code under the four families the inspection and ECHO lanes use (3252, 3255, 3259, 326); signal P/S/X is SCHEMA 2.2's own key.

| scope_class | Meaning | ITA establishments |
|---|---|---:|
| `core_P` | core family, SCHEMA 2.2 Ring 1/2 Primary code (every 326xxx listed code, 325211/325212/325991/325510/325520) | 6,019 |
| `core_S` | core family, listed Secondary (325220, 325998) | 417 |
| `core_X` | core family, listed exclude-by-default (325920 explosives) | 42 |
| `core_unlisted` | core family prefix but not a SCHEMA 2.2 code (325910 printing ink, 325992 toner/photo, 326100 family-level code) | 137 |
| `ring3_P` | Ring 3 Primary (333511, 424610, 562920) | 203 |
| `ring3_S` | Ring 3 Secondary (333249, 333514, 424690, 423830, 423930, 332710, 541330 ...) | 1,005 |
| `ring3_X` | Ring 3 exclude-by-default (333242 semiconductor machinery) | 0 |
| `other_listed_S` | listed Secondary outside the core families (313320; 325130 and 325199 basic-chemical codes; composites-adjacent) | 505 |
| `ring4_S` | Ring 4 Secondary (Ring 4 test always required) | 64 |
| `ring4_X` | Ring 4 exclude-by-default (238xxx installers, 311xxx food, 325412 pharma) | 27 |
| `unlisted` | not in SCHEMA 2.2 (3251 basic/industrial gases/carbon black, 441330 auto-parts retail, 423840, 333241, ...) | 2,775 |
| **Total** | | **11,194** |

By 4-digit NAICS prefix (unit: establishments), top 14: 3261 4,001; 3251 1,491; 4246 969; 4413 809; 3259 805; 3255 654; 3262 600; 3252 555; 3332 348; 4238 279; 4241 73; 3335 69; 3371 42; 1114 34.

**What the extract is.** Core-family rows = 6,615 (59.1% of 11,194); the remaining 4,579 are the 'value chain' the file name promises: 3251 basic chemicals/industrial gases/carbon black (1,491), 4246 chemical distributors (969), 4413 automotive parts/tire retail (809), 3332 machinery (348), 4238 industrial/plastics machinery and supply wholesalers (279) and a long tail. Most of these are **unlisted in SCHEMA 2.2** or Ring 3 Secondary: labelled, not ruled. They are matched to Atlas sites too (a Ring 3 or Ring 4 Atlas site can match), but they are **not** in the leads tables except the separate Ring 3 Primary count.

**NAICS observations for the integrator (not rulings).** (a) The extract mixes NAICS 2012, 2017 and 2022 vintages; SCHEMA 2.2 is written in 2022-era codes (e.g. plastics machinery at 333249) while ITA rows carry both 333248 and 333249 with the same plastics-machinery description, so 333248 is shown `unlisted` here although it looks adjacent to the listed 333249. (b) `326100` is a family-level pseudo-code, not a 6-digit NAICS (1 row, `core_unlisted`). (c) ITA NAICS is **entered by the employer in a mandatory federal filing**; whether that is `government_filing` (the inspection-lane precedent, and this packet's default) or `company_disclosed` under SCHEMA 2.1 is not settled here - an open classification question, flagged. It never overwrites a site NAICS (SCHEMA 2.1; AGENTS 4); `site_matches.csv` shows `naics_relation` (same_6digit / same_4digit / differs) for matched sites.

## 3. Match to Atlas sites

Atlas side: 5,773 site rows (all shards, any status/tier); a usable street key exists for 5,223 (90.5%) - from the `street_address` column where filled, otherwise a heuristic read of `Street...:` phrases in `notes`. Ladder = the ECHO/inspection ladder (AGENTS 3, operator rule): street exact + state + (zip5 or city) + name agreement = MATCH_SITE; street exact with a different name = POSSIBLE (co-tenant or successor operator); street unknown on either side + same zip5 + strong name = MATCH_SITE (moderate); same city + strong name, or weaker name = POSSIBLE; ties at the top rank = POSSIBLE; both streets present but different is never a match. Coordinates are not used. **One departure, improving on the inspection lane:** name agreement is tested against both `establishment_name` (often a generic plant label such as 'HERINGTON FACILITY') and `company_name` (the filing company, the operator) and the better of the two is used; `name_used` in `site_matches.csv` says which.

| Verdict | ITA establishments | of which core family |
|---|---:|---:|
| MATCH_SITE | 1,703 | 1,456 |
| POSSIBLE | 346 | 238 |
| NO_MATCH | 9,145 | 4,921 |
| **Total** | **11,194** | **6,615** |

**Match rate (unit: ITA establishments matched to an Atlas site row):** MATCH_SITE = 1,703 of 11,194 (**15.2%**) over all rows; **1,456 of 6,615 (22.0%)** over core-family rows (the comparable figure to the inspection lane's 15.0%); MATCH_SITE + POSSIBLE = 18.3% overall, 25.6% core. This is an establishment-to-site match rate, **not Atlas coverage**: the extract is a filtered slice of ITA filers, and ITA submission is required only of employers above OSHA's size/industry thresholds (a rule, not something this file proves), so many Atlas sites are legitimately absent.

MATCH_SITE by basis: `street_exact+loc+name` 1,662; `name_zip_street_unknown` 41. POSSIBLE by best basis: `name_city_street_unknown` 121; `street_exact+loc_name_differs` 113; `name_zip_weak` 65; `street_exact_locality_differs` 21; `street_exact+loc+name` 19; `name_zip_street_unknown` 7.
Name field that carried the MATCH_SITE agreement (unit: establishments): establishment_name 1,191; company_name 512.
Distinct Atlas sites reached by at least one MATCH_SITE establishment: 1,636 (unit: site rows); 43 of them are reached by more than one ITA establishment_ID (several filings at one address).
Inside the ITA file itself, 372 street+zip addresses carry more than one `establishment_ID` (803 establishments); left visible (`ita_estabs_at_address`), never merged (one address = one site, operator-owned; AGENTS 3).
ITA NAICS vs the matched site's `naics_primary` (unit: MATCH_SITE establishments): same_6digit 1,071; differs 250; site_naics_blank 230; same_4digit 152 - informational only; no NAICS overwrite is proposed.

**Liveness (activity signal only).** A CY2025 filing with employees and hours is dated evidence the establishment operated in 2025. It is never a status change (AGENTS 3). **7 ITA establishments point at an Atlas site recorded closed/idled** (2 MATCH_SITE, 5 POSSIBLE) - re-verification leads only (`liveness_note`); a filing at a possibly different operator of the same address does not show the recorded operator is active.
  - 1258696 LyondellBasell Advanced Polymers Inc (OH) -> SITE-000033 LyondellBasell — Akron [POSSIBLE]: closed; site_closed_in_atlas;site_notes_cite_WARN_closure
  - 996782 LyondellBasell Advanced Polymers Inc (OH) -> SITE-000033 LyondellBasell — Akron [POSSIBLE]: closed; site_closed_in_atlas;site_notes_cite_WARN_closure
  - 192082 IFI (OH) -> SITE-000180 IER Fujikura — Macedonia [MATCH_SITE]: closed; site_closed_in_atlas;site_tombstoned_duplicate_of:SITE-000398
  - 1326562 Yokohama Industries Americas Ohio (OH) -> SITE-000599 SAS Rubber Co. — Painesville [POSSIBLE]: closed; site_closed_in_atlas
  - 935710 Mondo Polymer Technologies, Inc. (OH) -> SITE-001042 Mondo Polymer Technologies — Reno [POSSIBLE]: closed; site_closed_in_atlas;site_tombstoned_duplicate_of:SITE-001043
  - 1273140 Cornerstone Building Brands - Walbridge Ohio (OH) -> SITE-000820 Cornerstone Building Brands — Walbridge [MATCH_SITE]: closed; site_closed_in_atlas;site_notes_cite_WARN_closure
  - 1431759 Robin Industries Holmco (OH) -> SITE-001174 Robin Industries, Inc. — Winesburg [POSSIBLE]: closed; site_closed_in_atlas;site_tombstoned_duplicate_of:SITE-001176

`site_caution` (in `site_matches.csv` and `band_proposals.csv`) is read from the Atlas site row: closed/idled status, a pass-11 'tombstoned as duplicate of SITE-x' note, or a WARN citation. MATCH_SITE rows that land on a tombstoned-duplicate site: 1 (the live twin is the likelier home of any band; e.g. the IFI row lands on the retired SITE-000180 while the live IER Industries row SITE-000398 carries street 'Bavaria Road' vs the ITA 'Bavaria Dr E', so the street key differs). A CY2025 filing at a plant the Atlas holds as closed on a WARN notice is not a contradiction when the WARN closure window is later than 2025 (SITE-000820's window is 2026-12-01 to 2026-12-31 per its notes).

## 4. EIN to organization link candidates

EINs are public in ITA. They are **candidates only**: the registry enum (SCHEMA 4.8) has no employer-EIN value (owner item already raised), so nothing here is a `registry_links` row, and an EIN found only in this file is a phantom for registry purposes (AGENTS 4). Usable EINs (unit: distinct 9-digit EINs): 4,487 over 9,009 establishments (80.5% of rows); 976 EINs appear on more than one establishment (5,498 establishments). Link method: the EIN of a MATCH_SITE establishment is associated with that site's org; the same EIN on other rows then points at that org.

- **EIN-org candidate pairs: 964** (distinct EIN x Atlas org via at least one MATCH_SITE row); 939 EINs reach a held org; 852 Atlas orgs get at least one EIN candidate.
- `ein_status` (unit: establishments): EIN_NO_HELD_ORG 5,624; no_usable_ein 2,185; EIN_CANDIDATE_ORG_OTHER_LOCATION 1,168; EIN_SPANS_MULTIPLE_HELD_ORGS 991; EIN_ON_MATCHED_SITE_AND_OTHER_ROWS 631; EIN_ON_MATCHED_SITE_ONLY 595.
- `EIN_CANDIDATE_ORG_OTHER_LOCATION` (1,168 establishments; 892 are core_P with verdict not MATCH_SITE): an establishment whose EIN equals the EIN of a held org's matched site - a likely **other site of a held org** (a stronger signal than a name match; still a lead, not a dedupe verdict). Those rows' `lead_class` stays name-based, so this is an extra column, not a reclassification.
- `EIN_SPANS_MULTIPLE_HELD_ORGS`: 22 EINs map to more than one Atlas org through MATCH_SITE rows - possible duplicate or parent/subsidiary org records in the Atlas, or a bad site match; dedupe-review candidates, not merges (AGENTS 3: when in doubt do not merge).
  - EIN 061653740: ORG-000761 Covestro LLC | ORG-003985 Elementis Specialties, Inc.
  - EIN 205404918: ORG-002723 Amrize Building Envelope LLC | ORG-004214 SES Foam LLC
  - EIN 221682767: ORG-000237 Sealed Air - Automated Packaging Systems | ORG-000566 Sealed Air Corporation
  - EIN 260081950: ORG-000547 LANXESS Rhein Chemie | ORG-003919 LANXESS Corporation
  - EIN 264323543: ORG-001752 Performance Plastics Ltd. | ORG-002534 Pexco LLC
  - EIN 340253240: ORG-000003 The Goodyear Tire & Rubber Company | ORG-000439 Mickey Thompson Performance Tires & Wheels
  - EIN 340310980: ORG-000385 Iten Defense | ORG-000386 Iten Industries, Inc. | ORG-002079 TDM LLC
  - EIN 340660330: ORG-000005 Day-Glo Color Corp | ORG-000006 RPM International Inc.
  - EIN 361258310: ORG-000889 ITW Tomco | ORG-003917 ITW Performance Polymers & Fluids
  - EIN 364126680: ORG-000665 Amcor Flexibles North America, Inc. | ORG-002907 Amcor plc
  - EIN 371699313: ORG-004318 Wilsonart LLC | ORG-004319 American Surfacing Materials LLC
  - EIN 381745524: ORG-002441 Dart Container Corporation | ORG-002474 Dart Container Corp. Of Pennsylvania
  - EIN 383475026: ORG-001091 Royal Building Products (Westlake Royal Building Products) | ORG-002298 Metamora Products Corporation
  - EIN 455472404: ORG-003635 Chem-Tainer Industries Inc. | ORG-003687 Tank Holding Corp.
  - EIN 461321243: ORG-002470 Allegheny Performance Plastics, LLC | ORG-002510 Holbrook Tool & Molding Inc.

## 5. Employee-band proposals (`band_proposals.csv`)

`annual_average_employees` is the employer-reported annual average number of employees at the establishment for CY2025 on the Form 300A (source class `government_filing`). It supports an `employee_band_site` **proposal** for **MATCH_SITE rows only**, at **site grain only** - never pushed to the organization or other sites (SCHEMA 4.5), and band only, never a headcount (SCHEMA 4.4). `employee_count_source_date` = the filing's `date_submitted` (ISO). Basis text per row: `OSHA ITA 300A CY2025, establishment_ID X: annual average employees N → band`. Zero is treated as missing, not a count.

- Establishments with a usable count (unit: establishments): 11,178 of 11,194; 16 have zero. By band: 1-9 1,285; 10-49 4,272; 50-99 2,562; 100-249 2,185; 250-499 624; 500-999 180; 1000-4999 62; 5000+ 8.
- **Data-quality screens (unit: establishments with a count).** `size_code_vs_avg_employees`: consistent 10,322; inconsistent 856. The ITA `size` code is expected to follow the employee count (observed: 1 = under 20, 21 = 20-99, 22 = 100-249, 3 = 250+, and a code 2 that spans 20-249); 856 of 11,178 counts fall outside their own row's size class - the two fields disagree and this packet does not decide which is right. `hours_per_employee_screen`: ok 10,992; implausible_hours_per_employee 186 (a count is 'implausible' when hours worked per employee is under 300 or over 4,500 - the file median is about 2,000; these look like keying errors, e.g. an hours figure typed into the employee box). `reliability` = ok (both screens pass) / review (size code disagrees) / suspect (hours screen fails).
- Reliability of all usable counts: ok 10,170; review 822; suspect 186.

**Band proposals: 1,635** (unit: Atlas site rows; one per matched site; where several ITA filings sit at one site the strongest match, then the most reliable, then the latest filing is shown and the others are listed in `other_ita_estabs_at_site` - never summed). MATCH_SITE sites reached: 1,636; sites with no usable count: 1; sites with more than one ITA establishment: 43.

| Relation to the site's current `employee_band_site` | All proposals | reliability = ok only |
|---|---:|---:|
| fills_blank | 1,599 | 1,464 |
| fills_unknown | 6 | 6 |
| matches_existing | 13 | 13 |
| conflicts_existing | 11 | 9 |
| existing_nonstandard_value | 6 | 4 |
| **Total** | **1,635** | **1,496** |

**Fill blanks:** 1,605 proposals fill a blank or `unknown` band (1,470 of them reliability ok). Existing values outside the SCHEMA 4.4 vocabulary are flagged `existing_nonstandard_value` and never overwritten by this packet. `conflicts_existing` rows are for integrator review; existing bands that came from the CRM landing (242 banded-only values per the QUEUE) are not distinguished in the site CSV, so provenance of the existing value must be read from the site notes.

Proposed bands (unit: site rows): 1-9 12; 10-49 391; 50-99 472; 100-249 495; 250-499 181; 500-999 68; 1000-4999 15; 5000+ 1.

### 5.1 Comparison with the inspection lane's proposals

The inspection lane (`tasks/osha-spine-2026-11-01/band_proposals.csv`, 889 proposals, band from `nr_in_estab` at the latest inspection with a count, source dates 2019-2026) vs this packet, by site (unit: site rows). ITA is the stronger and more recent source (an annual employer-attested figure for CY2025 vs an inspection-time figure of uncertain definition) - **disagreements are flagged, not resolved**.

| Result | Site rows |
|---|---:|
| agree (same band) | 375 |
| differ | 155 |
| ITA-only (site has an ITA proposal, no inspection proposal) | 1,105 |
| inspection-only (site has an inspection proposal, no ITA proposal) | 359 |

Sites with both proposals: 530; **agreement 70.8%** (375 same band).
Among the 155 differing sites, band distance (ITA minus inspection, in band steps): -5: 3; -4: 3; -3: 4; -2: 8; -1: 60; +1: 69; +2: 6; +3: 1; +5: 1. Adjacent-band differences (+/-1) are 83.2% of the differing sites; ITA higher in 77, ITA lower in 78. ITA is the newer figure for 445 of the 530 sites with both.
Restricted to ITA reliability = ok: agreement 354 of 485 (73.0%).
Where the site already carries a standard band and both lanes propose one (8 sites): existing matches neither 5; existing=ITA 3.

`inspection-only` sites are those the ITA extract does not reach with a usable count (not in the filtered extract, filed under a different name/address, or zero count); that is not a disagreement. Reproduce the list as inspection `band_proposals.csv` minus this file's `site_id` set.

### 5.2 Establishment cross-reference with the inspection lane

Each ITA establishment was looked up in the inspection lane's `establishments.csv` (6,473 establishments, all core-family NAICS, inspected 2019 or later): same street + state + (zip5 or city) + name agreement = `BOTH_SOURCES`; street unknown on one side + same zip5 + strong name = `BOTH_SOURCES` (name+zip); same street + locality but name differs = `BOTH_ADDRESS_NAME_DIFFERS` (co-tenant, rebrand or successor); else `ITA_ONLY`. Over all ITA rows (unit: ITA establishments): BOTH_SOURCES 1,791; BOTH_ADDRESS_NAME_DIFFERS 257; ITA_ONLY 9,146. Over core-family rows: BOTH_SOURCES 1,640 of 6,615.
Verdict consistency between the two lanes on BOTH_SOURCES core rows (a check on the shared ladder): ITA NO_MATCH; inspection lane NO_MATCH: 1,071; ITA MATCH_SITE; inspection lane MATCH_SITE at the same site: 508; ITA POSSIBLE; inspection lane POSSIBLE: 50; ITA POSSIBLE; inspection lane MATCH_SITE: 4; ITA POSSIBLE; inspection lane NO_MATCH: 4; ITA POSSIBLE; inspection lane NO_MATCH/POSSIBLE: 1; ITA MATCH_SITE; inspection lane POSSIBLE/NO_MATCH: 1; ITA POSSIBLE; inspection lane MATCH_SITE/POSSIBLE: 1.

## 6. NO_MATCH leads in core polymer NAICS, by state, sorted by QCEW gap

NO_MATCH = no Atlas site candidate cleared the ladder: a **lead, not a finding of absence** (name or street form may differ; the Atlas may hold the plant under another operator). Lead pool = core-family rows (`core_P`, `core_S`, `core_X`, `core_unlisted`); the headline pool is **`core_P`** (SCHEMA 2.2 Ring 1/2 Primary codes). Core-family NO_MATCH establishments: **4,921** (core_P 4,376; core_S 374; core_X 42; core_unlisted 129). Of the **4,376 core_P** NO_MATCH: 2,475 NET_NEW_LEAD (no Atlas org with this normalized name on either name field), 1,134 NAME_EQUALS_HELD_ORG_OTHER_LOCATION (likely another site of a held org), 441 HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS, 326 NAME_IN_HELD_ORG_TRADE_NAMES_OR_NOTES. `lead_class` and `lead_ref` per row are in `site_matches.csv` (rows with `verdict = NO_MATCH`). Every row still needs ring/scope adjudication - owner-ruling-adjacent, not settled here (AGENTS 2.9).

Sort key = QCEW gap per `docs/denominators/README.md`: QCEW 2023 private establishments, NAICS 326, minus Atlas strict 326 sites (`operating_status` active/unknown, tier A-C, `naics_primary` starts 326), recomputed from `data/sites_*.csv` at run time. The gap is a count difference, not a coverage figure, and the NO_MATCH pool per state is **not** an estimate of it (the ITA extract is a filtered slice of 20+-employee filers over several NAICS families; QCEW counts 326 reporting units of every size). Top 20 states by gap:

| Gap rank | State | QCEW gap (326) | ITA establishments (all) | core family | core MATCH_SITE | core NO_MATCH | core_P NO_MATCH | of which NET_NEW | core_P NO_MATCH also in inspection lane | of which NET_NEW |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | CA | 1,267 | 617 | 326 | 38 | 286 | 254 | 156 | 49 | 32 |
| 2 | TX | 869 | 987 | 520 | 99 | 397 | 339 | 179 | 72 | 41 |
| 3 | FL | 775 | 395 | 193 | 26 | 166 | 154 | 108 | 22 | 9 |
| 4 | MI | 772 | 516 | 369 | 42 | 321 | 306 | 196 | 85 | 58 |
| 5 | IL | 755 | 592 | 356 | 42 | 310 | 280 | 165 | 55 | 33 |
| 6 | GA | 446 | 495 | 306 | 38 | 260 | 223 | 137 | 41 | 25 |
| 7 | IN | 430 | 471 | 311 | 52 | 248 | 240 | 130 | 56 | 31 |
| 8 | WI | 408 | 419 | 297 | 56 | 239 | 226 | 142 | 54 | 32 |
| 9 | NY | 387 | 293 | 161 | 24 | 137 | 118 | 83 | 26 | 18 |
| 10 | NC | 382 | 417 | 276 | 67 | 200 | 182 | 84 | 42 | 23 |
| 11 | SC | 357 | 265 | 158 | 34 | 117 | 98 | 47 | 12 | 6 |
| 12 | NJ | 355 | 256 | 163 | 23 | 137 | 121 | 73 | 31 | 21 |
| 13 | TN | 350 | 317 | 189 | 45 | 144 | 129 | 80 | 33 | 21 |
| 14 | MN | 349 | 266 | 175 | 14 | 159 | 141 | 99 | 65 | 44 |
| 15 | MO | 331 | 220 | 130 | 27 | 99 | 89 | 46 | 15 | 7 |
| 16 | KY | 260 | 246 | 154 | 28 | 123 | 114 | 55 | 39 | 16 |
| 17 | PA | 246 | 602 | 396 | 183 | 173 | 139 | 46 | 37 | 10 |
| 18 | MA | 221 | 220 | 134 | 29 | 104 | 96 | 61 | 31 | 20 |
| 19 | AL | 219 | 224 | 128 | 21 | 105 | 97 | 56 | 16 | 7 |
| 20 | VA | 213 | 189 | 105 | 25 | 77 | 58 | 28 | 21 | 11 |

**Leads seen in both OSHA sources (stronger leads).** core_P NO_MATCH establishments that the inspection lane also lists (same address and name, or name + zip): **1,003 of 4,376** (22.9%); 572 of those are NET_NEW_LEAD. A further 138 core_P NO_MATCH share an address with an inspection-lane establishment under a different name (`BOTH_ADDRESS_NAME_DIFFERS`; co-tenant, rebrand or successor - weaker). Two separate OSHA records (an employer-filed 300A for CY2025 and a compliance-officer inspection record since 2019) naming the same establishment raises confidence that it exists and operated, not that it is in scope (both carry an OSHA-channel NAICS, so they are not independent evidence of the code). Full per-state counts: `leads_by_state.csv` (`coreP_no_match_both_osha_sources`, `..._net_new`).

Examples: the strongest rows in the five largest-gap states (core_P, NO_MATCH, seen in both OSHA sources, NET_NEW_LEAD, reliability ok), largest reported employee count first, up to 5 per state; names are public business names as filed. Full lists = filter `site_matches.csv` on `scope_class=core_P`, `verdict=NO_MATCH`, `cross_source=BOTH_SOURCES`, `lead_class=NET_NEW_LEAD`.

| State | ITA establishment_ID | Company / establishment | City | NAICS | Employees band (ITA) | Latest OSHA inspection |
|---|---|---|---|---|---|---|
| CA | 1379418 | - / Milgard Windows and Doors | Temecula | 326199 | 500-999 | 2023-06-09 |
| CA | 1020642 | SIG Packaging, LLC / SIG Packaging, LLC - Merced | Merced | 326111 | 250-499 | 2026-07-23 |
| CA | 978189 | Poly-Tainer, Inc. / Poly-Tainer, Inc. - California | Simi Valley | 326160 | 250-499 | 2026-04-22 |
| CA | 865878 | - / VPET USA LLC | FONTANA | 326199 | 100-249 | 2026-04-22 |
| CA | 1075786 | Labcon, North America / Labcon, North America | Petaluma | 326199 | 100-249 | 2026-07-10 |
| TX | 1333035 | Poly-America / Poly-America | Grand Prairie | 326111 | 1000-4999 | 2024-01-11 |
| TX | 1181375 | dBA Virginia Rose, H&S Consulting / SPR Pkg, LLC | Rockwall | 326111 | 250-499 | 2023-09-07 |
| TX | 1518061 | D6 Inc / D6 Sulphur Springs | Sulphur Springs | 326112 | 100-249 | 2023-02-28 |
| TX | 1448308 | Global Enterprises / Polymerica dba Global Enterprises | El Paso | 326199 | 100-249 | 2023-10-19 |
| TX | 54886 | ARLANXEO Performance Elastomers LLC / ARLANXEO, Orange Site, Texas | Orange | 325212 | 100-249 | 2024-05-16 |
| FL | 139849 | KING PLASTIC CORPORATION / KING PLASTIC CORPORATION | North Port | 326113 | 100-249 | 2025-06-03 |
| FL | 521927 | Captiva Containers / Captiva Containers | Miami | 326199 | 100-249 | 2022-04-11 |
| FL | 919266 | Fluid Routing Solutions, LLC / Fluid Routing Solutions Ocala | Ocala | 326220 | 50-99 | 2025-12-18 |
| FL | 1566933 | Spartan Composites / Spartan Composites | Rockledge | 325211 | 10-49 | 2024-04-09 |
| FL | 1411331 | Rounded by Concealment Express / Rounded | Jacksonville | 326199 | 10-49 | 2024-10-31 |
| MI | 61877 | Western Diversified Plastics / Western Diversified Plastics | Mattawan | 326199 | 500-999 | 2025-03-31 |
| MI | 91829 | US Farathane / Port Huron | Port Huron | 326199 | 500-999 | 2025-11-25 |
| MI | 811622 | Airboss Flexible Products / Airboss Flexible Products | Auburn Hills | 326291 | 250-499 | 2024-02-20 |
| MI | 1123907 | Summit Polymers Inc / Summit Polymers Inc. Plant 8 | Vicksburg | 326199 | 250-499 | 2026-06-17 |
| MI | 990734 | Shuert Technologies / Shuert Technology LLC | Sterling Heights | 326199 | 250-499 | 2025-04-04 |
| IL | 1284693 | BCI Acrylic / BCI Acrylic, Inc | Libertyville | 326191 | 250-499 | 2024-04-18 |
| IL | 1312194 | Hoffer Plastics / Hoffer Plastics | South Elgin | 326199 | 250-499 | 2019-02-01 |
| IL | 1308384 | Parker Hannifin - O-ring, Woodridge, IL / Engineered Materials Woodridge | Woodridge | 326291 | 100-249 | 2023-05-02 |
| IL | 1522621 | BWAY / BWAY Arthur | Elk Grove Village | 326199 | 100-249 | 2026-02-19 |
| IL | 1531978 | Seymour of Sycamore / Seymour of Sycamore | Sycamore | 325510 | 100-249 | 2025-03-13 |

Other lead-strength columns in `site_matches.csv` / `leads_by_state.csv`: `ein_status = EIN_CANDIDATE_ORG_OTHER_LOCATION` (the EIN ties the row to a held org's matched site; 839 core_P NO_MATCH rows) and `ita_estabs_at_address` (several filings at one address; distinct street+zip addresses among core_P NO_MATCH, summed over states: 4,272).
Ring 3 Primary rows (333511 / 424610 / 562920) are outside the core-family pool but counted separately (unit: ITA establishments): 203 total, 19 MATCH_SITE, 6 POSSIBLE, 178 NO_MATCH. They are Ring 3 distribution/tooling/recovery candidates for an owner scope decision, not Ring 1/2 leads.

## 7. Caveats (binding on any reader)

- **Filtered extract, unknown filter.** The owner's filter is not known in detail; the file is not a census of ITA filers, and nothing here (including 'ITA_ONLY') says anything about establishments outside it.
- **ITA coverage is by rule, not by plant.** Only establishments whose employers are subject to OSHA's electronic-submission thresholds (and that actually filed) appear; the extract nonetheless contains establishments with under 20 employees (company-level thresholds), so the threshold is not a clean line. Absence is nothing.
- **NAICS is employer-entered** and can be stale, coarse or wrong (the extract mixes NAICS 2012/2017/2022 vintages and includes mis-coded rows, e.g. plastic-surgeon codes 621111, retail 441330, and odd descriptions). It is a filing value for the establishment, never a company fact, never a ring decision, never overwrites a site NAICS (SCHEMA 2.1, AGENTS 4). `scope_class` labels; it does not rule.
- **`annual_average_employees` is a self-reported figure** with visible quality problems (size-code disagreement; hours-per-employee implausibility; counts of 50,000+ at plants). It is a band input with a date, not a headcount; `reliability` is a screen, not a verdict. Zero is missing. Never allocated to the org or other sites (SCHEMA 4.5).
- **`date_submitted` is the filing date for CY2025**, not the date the average was measured; the figure describes calendar 2025. `employee_count_source_date` follows the owner's instruction (date_submitted).
- **Addresses are establishment addresses** as typed by the filer; leading zeros in zip and EIN were lost by the download and restored by rule; a few filers give an HQ or mailing address for a plant (cannot be detected from the file alone). Matching is by address + name, not coordinates.
- **Activity is not status.** A CY2025 filing never changes an Atlas status; the closed/idled overlaps are re-verification leads only (AGENTS 3). A failed or empty match is never evidence of closure.
- **EIN is a candidate link only** (no registry enum value; owner item raised). One EIN can span several establishments, orgs or affiliates; EIN-spans-multiple-orgs rows are dedupe-review candidates, never merges.
- **Leads only.** No row is a verdict in the AGENTS 2.8 grammar (not VERIFIED, REJECT, STILL_UNCERTAIN or DUPLICATE_OF). NO_MATCH is a lead; MATCH_SITE is a match candidate for the integrator.
- **Counts name their unit and filter:** rows/establishments = ITA establishment records (one `establishment_ID` each); sites = Atlas site rows; proposals = one per matched Atlas site; core family = NAICS under 3252/3255/3259/326; core_P = the Primary-signal subset.
- **Privacy.** No individual names, emails or phones in any output; injury/illness data is excluded entirely; EIN is a business identifier published by OSHA in this dataset.

## 8. Reproduce

```
python3 -I scripts/build_osha_ita.py <path>/filtered_full_value_chain_ITA_300A.tsv --as-of 2026-11-01
# input SHA-256: 69c0d987d453471293b092640b392eaef44b21cb55446a1c9b69ad8b54bf703a
# cross-reference inputs: tasks/osha-spine-2026-11-01/{establishments,site_matches,band_proposals}.csv
```
