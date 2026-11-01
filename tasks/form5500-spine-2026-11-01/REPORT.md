# Form 5500 polymer-sponsor spine - REPORT

Generated 2026-11-01 by `scripts/build_form5500_spine.py`; packet-lane output, **no file under `data/` was edited, no ID allocated, no status changed**. Every row here is a lead or a proposal for the integrator of record; nothing is a verdict. Task claim: no QUEUE.md line was edited by this lane (lanes do not write shared files); the integrator should add/claim the line.

## 1. What this is

DOL EFAST2 Form 5500 and Form 5500-SF bulk "Latest" datasets, filtered to polymer business codes and collapsed to one row per sponsor EIN, then matched to the Atlas. Three uses: (1) an employee-size input (SCHEMA owner ruling R7f, 2026-11-01: a plan-participant count is an admissible employee-band input - `government_filing`, with plan year, always banded, never a precise headcount); (2) a national discovery spine of **employers** (sponsor EIN, not establishment); (3) a liveness signal (latest plan year filed).

### Source files (retrieved 2026-11-01; raw zips kept outside the repo)

| Plan-year file | Form | Zip | Bytes | SHA-256 |
|---|---:|---:|---:|---:|
| 2025 | 5500 | F_5500_2025_Latest.zip | 12,945,186 | `9f6245cdcbb86ae167af4595bb3dba4fbf7845df98f4ccd6748aa98fa2a4e582` |
| 2025 | 5500-SF | F_5500_SF_2025_Latest.zip | 105,100,962 | `2db4677bd93455ccc082d378fdd56594ac90ca0fc6f2da1639a15aea8ed3e94d` |
| 2024 | 5500 | F_5500_2024_Latest.zip | 28,642,573 | `8884391d48a9e362fd7d2b91d6e37430bd2e54355c9dbc3479985c9d876872f8` |
| 2024 | 5500-SF | F_5500_SF_2024_Latest.zip | 136,400,721 | `11370908e2bbc78d1d418b2f2a2177875e0524c12b69a181432d6fd65a5966c3` |
| 2023 | 5500 | F_5500_2023_Latest.zip | 29,357,833 | `303d4c80af9b8727a7ed7e58cd3c4324dbbfa16828807ace9fd71e2138ea3331` |
| 2023 | 5500-SF | F_5500_SF_2023_Latest.zip | 131,128,075 | `f463f915b5fc4f951727900061966a957cd2a3d3f4fb1e7af585d4e22769e90e` |

URL pattern: `https://askebsa.dol.gov/FOIA%20Files/<YEAR>/Latest/<zip>`; index page <https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/public-disclosure/foia/form-5500-datasets>. Column names were confirmed against the published `*_layout.txt` and the 2024 form PDFs (data-dictionary zip). 2023, 2024 and 2025 file sets were all used: 2024 is complete enough on its own, but 2023 supplies sponsors that have not (yet) filed 2024 and 2025 supplies the freshest liveness signal. **The 2025 file set is incomplete** (measured 2026-11-01: plan-year-2025 filings in the 2025 Latest files are ~100k Form 5500 / ~621k SF against ~219k / ~773k plan-year-2024 filings in the 2024 files; large-plan filings on extension were still arriving at the 2026-09-25 dataset date), so absence from PY2025 is not a signal. The 2025 files also carry plan-year-**2026** rows: short plan years (tax period ends in early 2026) - plan wind-downs, not typos.

### Field definitions used

- **Active participants** = Form 5500 `TOT_ACTIVE_PARTCP_CNT` (line 6a(2), active participants at the **end** of the plan year) / Form 5500-SF `SF_TOT_ACT_PARTCP_EOY_CNT` (line 5d(2)). `total_participants_boy` = `TOT_PARTCP_BOY_CNT` / `SF_TOT_PARTCP_BOY_CNT` (all participants incl. retirees, beginning of year) is carried for context only and never banded.
- **Business code** = `BUSINESS_CODE` / `SF_BUSINESS_CODE`, the filer-selected code from the IRS list printed in the form instructions. Source type for any NAICS taken from it: `government_filing`; confidence no higher than `medium` (filer-selected, mostly padded group codes).
- **Polymer set** = every code starting 3252, 3255, 3259, 326 plus Ring 3 Primary 333511 / 424610 / 562920 (SCHEMA 2.2). Form 5500 filers mostly use padded group codes, so the effective set is: `326100` (3209), `325900` (1080), `326200` (682), `325500` (620), `325200` (294), `326199` (3), `326000` (2), `333511` (2), `424610` (1), `326111` (1), `326220` (1), `325212` (1). Sponsors per code are in section 3.
- **One row per sponsor EIN.** Latest plan year Y = latest plan-year-begin year among polymer-coded filings. Representative filing = most active participants among **all** the EIN's filings for Y (any code), because one sponsor's plans overlap (the same employees are in the 401(k) and the health plan): MAX, never the sum. `n_plans_latest_py` / `max_active_latest_py` expose multi-plan sponsors.
- **Final and short-year filings never set a band.** A filing with the final-filing flag or the short-plan-year flag reports a wind-down (active participants are typically 0 with participants still listed at the beginning of the year). Y above is therefore the latest plan year among *operating* (non-final, non-short) polymer-coded filings; only a sponsor with no operating filing falls back to its final/short filing and is left unbanded (`rep_basis = final_or_short_only`). The liveness columns (`latest_filed_plan_year_any`, `final_filing_flag_latest`, `short_plan_year_flag_latest`, `latest_py_all_final_or_short`) still look at **all** filings.

## 2. Headline counts

Unit: **unique sponsor EINs** (employers, not establishments) with at least one Form 5500 / 5500-SF filing in the 2023-2025 file sets coded to the polymer set.

| Measure | Value |
|---|---:|
| Polymer-coded filings read (rows, all years, both forms) | 18,629 |
| Unique sponsor EINs (rows in sponsors.csv) | 5,897 |
| ... with a US state on the address | 5,895 |
| ... foreign / no US state | 2 |
| ... with active participants >= 1 (bandable) | 5,547 |
| ... with active participants blank or 0 (not bandable) | 350 |
| ... of which only final / short-plan-year filings exist (`rep_basis` = final_or_short_only) | 181 |
| ... multi-plan sponsors in latest plan year (n_plans_latest_py > 1) | 1,021 |
| ... street line withheld for privacy (no entity designator and < 10 participants) | 102 |
| Sponsors by latest plan year filed (any code) | PY2026: 50; PY2025: 3,925; PY2024: 1,665; PY2023: 241; PY2022: 1; PY2021: 8; PY2020: 3; PY2019: 2; PY2015: 1; PY2005: 1 |

Rows read per file (polymer-coded only):

| Plan-year file | Form | Polymer-coded filings |
|---|---:|---:|
| 2023 | 5500 | 3,423 |
| 2023 | 5500-SF | 3,916 |
| 2024 | 5500 | 3,177 |
| 2024 | 5500-SF | 3,869 |
| 2025 | 5500 | 1,461 |
| 2025 | 5500-SF | 2,783 |

## 3. Sponsors by state (all sponsors, polymer set)

Unit: unique sponsor EINs by the state on the representative filing's address (location address if present, else mailing). `326-coded` = sponsors whose polymer code starts 326 (plastics/rubber products, the QCEW 326 comparison set).

| State | Sponsor EINs | 326-coded | Bandable | Matched (ORG+SITE) | POSSIBLE | NO_MATCH |
|---|---:|---:|---:|---:|---:|---:|
| CA | 611 | 397 | 572 | 15 | 26 | 570 |
| OH | 529 | 387 | 488 | 310 | 29 | 190 |
| IL | 380 | 261 | 368 | 23 | 23 | 334 |
| TX | 361 | 193 | 338 | 44 | 27 | 290 |
| MI | 355 | 279 | 335 | 29 | 23 | 303 |
| PA | 310 | 218 | 290 | 145 | 35 | 130 |
| NJ | 270 | 161 | 256 | 29 | 15 | 226 |
| NY | 235 | 158 | 220 | 11 | 20 | 204 |
| WI | 227 | 170 | 216 | 28 | 19 | 180 |
| IN | 222 | 161 | 205 | 26 | 17 | 179 |
| GA | 205 | 114 | 189 | 20 | 15 | 170 |
| MA | 200 | 124 | 186 | 12 | 18 | 170 |
| NC | 188 | 106 | 179 | 29 | 20 | 139 |
| MN | 180 | 133 | 171 | 11 | 14 | 155 |
| FL | 143 | 85 | 143 | 6 | 10 | 127 |
| MO | 134 | 88 | 124 | 12 | 15 | 107 |
| TN | 107 | 73 | 101 | 17 | 8 | 82 |
| SC | 106 | 60 | 100 | 17 | 9 | 80 |
| CT | 101 | 61 | 95 | 12 | 9 | 80 |
| WA | 77 | 55 | 70 | 4 | 3 | 70 |
| KY | 76 | 46 | 67 | 9 | 5 | 62 |
| VA | 72 | 49 | 67 | 8 | 4 | 60 |
| IA | 70 | 54 | 67 | 8 | 6 | 56 |
| CO | 60 | 39 | 59 | 6 | 1 | 53 |
| AZ | 57 | 36 | 55 | 1 | 4 | 52 |
| OR | 57 | 41 | 56 | 6 | 1 | 50 |
| AL | 52 | 31 | 49 | 4 | 3 | 45 |
| KS | 49 | 36 | 46 | 7 | 5 | 37 |
| NH | 48 | 34 | 46 | 4 | 3 | 41 |
| MD | 42 | 24 | 37 | 2 | 5 | 35 |
| LA | 41 | 11 | 40 | 5 | 4 | 32 |
| OK | 39 | 22 | 39 | 1 | 5 | 33 |
| UT | 36 | 23 | 29 | 3 | 3 | 30 |
| DE | 35 | 17 | 30 | 4 | 3 | 28 |
| RI | 30 | 24 | 30 | 6 | 1 | 23 |
| AR | 28 | 23 | 27 | 5 | 2 | 21 |
| NE | 22 | 14 | 22 | 1 | 2 | 19 |
| NV | 22 | 11 | 19 | 0 | 0 | 22 |
| MS | 15 | 10 | 14 | 4 | 2 | 9 |
| SD | 15 | 14 | 14 | 3 | 1 | 11 |
| ME | 14 | 11 | 14 | 0 | 2 | 12 |
| PR | 13 | 8 | 13 | 0 | 0 | 13 |
| WV | 13 | 6 | 13 | 6 | 0 | 7 |
| VT | 12 | 6 | 12 | 2 | 0 | 10 |
| ID | 8 | 7 | 8 | 2 | 0 | 6 |
| ND | 7 | 5 | 7 | 1 | 0 | 6 |
| HI | 6 | 4 | 6 | 0 | 0 | 6 |
| MT | 6 | 3 | 6 | 0 | 1 | 5 |
| NM | 4 | 2 | 3 | 0 | 0 | 4 |
| WY | 3 | 1 | 3 | 0 | 0 | 3 |
| GU | 2 | 0 | 2 | 0 | 0 | 2 |
| FOREIGN | 2 | 2 | 1 | 0 | 0 | 2 |

### Sponsors by polymer business code

| Business code | SCHEMA 2.2 signal | Granularity | Sponsor EINs |
|---|---:|---:|---:|
| 326100 | R1:P (326111-326199 group) | padded_group | 3209 |
| 325900 | R2:mixed (325991 P; 325998 S; 325920 X; 325910,325992 not in 2.2) | padded_group | 1080 |
| 326200 | R1:P (326211-326299 group) | padded_group | 682 |
| 325500 | R2:P*/P (325510,325520) | padded_group | 620 |
| 325200 | R2:P/S mixed (325211,325212 P; 325220 S) | padded_group | 294 |
| 326199 | R1:P | exact6 | 3 |
| 326000 | R1:P (326 group) | padded_group | 2 |
| 333511 | R3:P | exact6 | 2 |
| 424610 | R3:P | exact6 | 1 |
| 326111 | R1:P | exact6 | 1 |
| 326220 | R1:P | exact6 | 1 |
| 325212 | R2:P | exact6 | 1 |
| 325520 | R2:P | exact6 | 1 |

Padded group codes (`...00`) cover several 6-digit NAICS codes, so **the Form 5500 code never settles a 6-digit NAICS, a ring or a scope claim**; it is a discovery lead and a coarse industry signal (SCHEMA 2.1, 'NAICS is a signal for discovery... never the Ring decision alone'). 325900 and 325200 mix Primary, Secondary and Exclude codes (e.g. 325920 explosives) and are the noisiest.

## 4. Match to the Atlas

Method: same normalizers and step order as `scripts/atlas.py dedupe-check` (AGENTS.md section 3). Step 1 (domain) cannot run - Form 5500 has no website. Cross-check: this run re-ran 400 random sponsors through `atlas.dedupe()` itself (`--selftest`) and the step 2 and step 3 hit sets were identical (0 mismatches; a mismatch aborts the build). Classes:

- **MATCH_ORG**: step 2 normalized name equals an Atlas legal_name / trade_name **and** the sponsor state is the org's HQ state or one of its site states (`+3` in `match_step` = a step-3 street+locality hit on a site of that same org as well).
- **MATCH_SITE**: step 3 street + locality (same state and ZIP5 or city) equal an Atlas site, and the sponsor name shares its first non-generic token with the operator / site / trade names.
- **POSSIBLE**: anything weaker - name equal but state conflicts, street equal but name differs (multi-tenant / parent address), fuzzy name (suffix/plural/holding words stripped), or a step-4 hit in trade_names/notes. Needs a human; never merged.
- **NO_MATCH**: no hit at any step run. Not evidence the establishment is absent from the Atlas under another name or that it is in scope.

| Match class | Sponsor EINs | Share of sponsors |
|---|---:|---:|
| MATCH_ORG | 829 | 14.1% |
| MATCH_SITE | 69 | 1.2% |
| POSSIBLE | 418 | 7.1% |
| NO_MATCH | 4,581 | 77.7% |
| **Total** | 5,897 | 100% |

**Match rate (MATCH_ORG + MATCH_SITE) = 898 of 5,897 sponsor EINs = 15.2%**; matched sponsors resolve to 869 distinct Atlas organizations/ecosystem rows. With POSSIBLE included the upper bound is 22.3%.

Match step distribution (non-NO_MATCH rows):

| match_step | Sponsor EINs |
|---|---:|
| 2 | 509 |
| 2+3 | 320 |
| 2_name_exact_state_conflict | 140 |
| 2b_fuzzy_name | 23 |
| 2b_fuzzy_name_state_conflict | 53 |
| 3 | 69 |
| 3_street_only_name_differs | 66 |
| 4_legal_name_contains | 16 |
| 4_notes_contains | 104 |
| 4_trade_names_contains | 16 |

Match rate by employee-size band of the sponsor (band from active participants):

| Band | Sponsors | MATCH_ORG | MATCH_SITE | POSSIBLE | NO_MATCH | Match rate |
|---|---:|---:|---:|---:|---:|---:|
| 1-9 | 999 | 55 | 5 | 29 | 910 | 6.0% |
| 10-49 | 2033 | 220 | 16 | 108 | 1689 | 11.6% |
| 50-99 | 853 | 145 | 9 | 52 | 647 | 18.1% |
| 100-249 | 842 | 172 | 19 | 69 | 582 | 22.7% |
| 250-499 | 369 | 82 | 7 | 47 | 233 | 24.1% |
| 500-999 | 217 | 48 | 4 | 46 | 119 | 24.0% |
| 1000-4999 | 201 | 67 | 3 | 35 | 96 | 34.8% |
| 5000+ | 33 | 14 | 1 | 3 | 15 | 45.5% |
| (no active count) | 350 | 26 | 5 | 29 | 290 | 8.9% |

Read the size table first: a high match rate in the large bands and a low one in the small bands is the expected shape (Atlas discovery was biased to larger employers and to Ohio). Sponsor-to-establishment is not 1:1, so a NO_MATCH sponsor with 500 participants is a lead for one or more establishments, not a count of missing plants.

## 5. Employee-band proposals (MATCH rows only)

`band_proposals.csv` has 1,178 rows covering 898 matched sponsor EINs (one org-level row per matched sponsor, plus a site-level row only where the org has exactly one Atlas site, that site is the address match, and so the sponsor and the establishment coincide). Basis text on every row: `Form 5500 plan year YYYY, active participants N -> band`; `basis_public_text` is the band-only wording to put in any evidence row, because R7f says **never a precise headcount** - the exact N appears only in the lane-internal `basis` column.

| Target table | Target field | Proposal class | Rows |
|---|---:|---:|---:|
| - | - | NO_COUNT | 31 |
| organizations | - | NOTE_ONLY | 612 |
| organizations | employee_band_ohio | CONFLICT | 27 |
| organizations | employee_band_ohio | CONSISTENT | 19 |
| organizations | employee_band_ohio | FILL | 209 |
| sites | employee_band_site | CONFLICT | 9 |
| sites | employee_band_site | CONSISTENT | 4 |
| sites | employee_band_site | FILL | 267 |

Proposal classes: **FILL** = existing value blank/unknown; **CONSISTENT** = existing band equals the proposal; **CONFLICT** = existing band differs (never overwrite without review - the existing band may be an Ohio-site band from a better source); **NOTE_ONLY** = no field push: sponsor address is not Ohio (`employee_band_ohio` is an Ohio band), or the org has non-Ohio Atlas sites / is a diversified conglomerate (the plan then covers more than Ohio, so the band is only an upper bound for Ohio), or the matched row is an ecosystem row; **NO_COUNT** = representative filing carries no active participants.

- Ohio org-level `employee_band_ohio`: **209 FILL**, 19 CONSISTENT, 27 CONFLICT.
- Site-level `employee_band_site` rows: 280 (single-establishment orgs with address match only).
- Derived-field effect to expect: 16 of the Ohio FILL proposals are in a 250+ band; `employee_band_ohio` is an input to the derived `tier1_qualifier` leg `employees_250plus` (SCHEMA 4.4), so applying them will change derived output at the next derivation pass. `tier1_qualifier` itself is never hand-edited (AGENTS.md section 1).
- Caveats carried in every row: Plan participants are not employees exactly (they include eligible/covered workers and are counted at the plan, not the establishment); a plan sponsor can cover several establishments and states; the representative plan is the sponsor's largest by active participants, never a sum.
- Integration route: these are packets. An integrator applies them one writer per file, with `employee_count_source_date` and a `government_filing` evidence row per band (SCHEMA 4.13); FILL rows still need the integrator's own look at multi-plan and MATCH_SITE flags.

## 6. Discovery leads (NO_MATCH) by state

Unit: unique sponsor EINs with no Atlas hit at any step. **These are employers with an ERISA plan, not verified establishments**; each still needs the full create path (AGENTS.md sections 3-4: dedupe on the establishment's own domain/address, primary-source existence + scope evidence, tier U/C at birth; a platform/roster category such as a business code is a discovery lead and never supports a scope claim). The Form 5500 business code is filer-chosen and coarse, so expect noise (325900/325200 especially) and out-of-scope filers (e.g. plastics distributors, paint/coating blenders under 325500).

Largest QCEW NAICS 326 gap states (`docs/denominators/README.md`: QCEW 2023 private 326 establishments minus Atlas strict sites). Columns: QCEW 326 establishments 2023 | Atlas site rows in state (all rows) | sponsors | 326-coded sponsors | NO_MATCH sponsors | NO_MATCH 326-coded | NO_MATCH with >= 50 active participants | POSSIBLE (review first).

| State | QCEW 2023 326 estabs | Atlas site rows | Sponsor EINs | 326-coded | NO_MATCH leads | NO_MATCH 326-coded | NO_MATCH >= 50 active | POSSIBLE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CA | 1306 | 138 | 611 | 397 | 570 | 368 | 142 | 26 |
| TX | 953 | 369 | 361 | 193 | 290 | 155 | 111 | 27 |
| FL | 798 | 82 | 143 | 85 | 127 | 73 | 44 | 10 |
| MI | 819 | 173 | 355 | 279 | 303 | 237 | 144 | 23 |
| IL | 797 | 160 | 380 | 261 | 334 | 227 | 139 | 23 |
| GA | 491 | 139 | 205 | 114 | 170 | 93 | 64 | 15 |
| IN | 512 | 171 | 222 | 161 | 179 | 123 | 92 | 17 |
| WI | 456 | 128 | 227 | 170 | 180 | 131 | 77 | 19 |
| NY | 410 | 79 | 235 | 158 | 204 | 133 | 57 | 20 |
| NC | 453 | 181 | 188 | 106 | 139 | 75 | 61 | 20 |
| **Top-10 gap states** |  |  | 2,927 | 1,924 | 2,496 | 1,615 | 931 | 200 |

Sponsor counts are employers (a multi-plant employer is one EIN) and QCEW counts establishments, so the two columns are different units and must never be divided to get 'coverage'. They show where the unmatched employer leads sit relative to the Atlas gap.

All-state NO_MATCH counts are in the section 3 table (column NO_MATCH) and in `matches.csv` (filter `match_class=NO_MATCH`, join to `sponsors.csv` on `ein` for name/address/size).

## 7. Liveness use (signal only - never a status change)

A sponsor's latest filed plan year and its `final_filing_flag_latest` are **plan facts**. Per AGENTS.md section 3: a final Form 5500 filing is a plan fact, never a status change; an operating-status change needs dated primary evidence; a failed or absent fetch is never evidence of closure. Used this way:

- **Positive signal (operating-evidence lead):** a matched, Atlas-`active` org whose EIN filed a plan year 2024 or 2025 with active participants > 0 is a dated government-filing activity witness (SCHEMA 4.4 `last_activity_evidence_date` floor / `liveness_signal=operating_evidence` are the integrator's call, and only where the filing's address **is** the establishment in question - AGENTS.md section 2 rule 8).
- **Owes-a-look signal:** a final-filing flag, or no filing in the latest complete plan year, on a matched `active` org is the 'closure signature' ingredient SCHEMA 4.4 describes - it queues a direct liveness check and nothing more.

| Measure (unit: matched sponsor EINs whose Atlas row is status=active) | Count |
|---|---:|
| Matched sponsors (ORG+SITE) whose Atlas row is `active` | 894 |
| ... latest filed plan year 2025 (partial year) | 597 |
| ... latest filed plan year 2024 | 265 |
| ... latest filed plan year 2023 or earlier (no 2024/2025 filing found in these files) | 26 |
| ... every filing of the latest plan year is a final or short-plan-year filing (plan wind-down; a plan fact, not a status) | 68 |
| Matched sponsors whose Atlas row is NOT active (tombstoned/other) yet filed PY2024+ | 4 |

Orgs to queue for a direct liveness look (lead only; IDs from `matches.csv`):

`ORG-000069, ORG-000071, ORG-000077, ORG-000103, ORG-000175, ORG-000191, ORG-000375, ORG-000419, ORG-000454, ORG-000477, ORG-000522, ORG-000544, ORG-000603, ORG-000697, ORG-000772, ORG-000793, ORG-000842, ORG-000870, ORG-000903, ORG-001019, ORG-001114, ORG-001141, ORG-001156, ORG-001160, ORG-001173, ORG-001395, ORG-001437, ORG-001452, ORG-001602, ORG-001651, ORG-001787, ORG-001860, ORG-001878, ORG-001933, ORG-001949, ORG-002000, ORG-002031, ORG-002133, ORG-002135, ORG-002148, ORG-002211, ORG-002268, ORG-002290, ORG-002304, ORG-002315, ORG-002326, ORG-002348, ORG-002391, ORG-002465, ORG-002562, ORG-002648, ORG-002685, ORG-002692, ORG-002712, ORG-002734, ORG-002888, ORG-002941, ORG-002962, ORG-003017, ORG-003257` ... (+19 more)

Cross-check against the Atlas's existing `liveness_signal=closure_signature` seed(s): ORG-002148 (THE ARTHUR CORPORATION): matched sponsor EIN 341352998, latest filed plan year 2023, all latest-year filings final/short = 1.

Caveats: PY2025 is partial; a sponsor can be acquired and its EIN retired while the establishment keeps operating (look for a successor EIN: `LAST_RPT_SPONS_EIN` is in the raw files, not carried here); a filing's address is usually the HQ/administrative address, not the plant; a sponsor filing blocks a REJECT for closure only when its address is the establishment (AGENTS.md section 2 rule 8). Nothing in this report changes any `status`.

## 8. OWNER item - registry value for employer EINs

**Question.** `registry_links.registry` (SCHEMA 4.8) has `EIN_NONPROFIT` only (ProPublica, nonprofits). Form 5500 publishes the sponsor EIN for every employer-sponsored plan, i.e. an EIN for ordinary for-profit employers is now obtainable from a government bulk source - the section 4.8 sentence 'no bulk EIN source is adopted' no longer holds. Should an employer-EIN registry value be added?

**Recommendation: yes - add a single `EIN` registry value (dated schema revision; this is a vocabulary change, so an owner ruling per AGENTS.md section 2 rule 9 - not settled here).** Reasons: (a) the EIN is the exact join key for Form 5500, IRS EO/BMF, PPP, SBA and many state filings, turning later name-matching into key-matching (the UEI doctrine applied to employers); (b) the table is already multi-value by design, which fits a parent org holding several legal-entity EINs; (c) a second value just for for-profits (`EIN_EMPLOYER`) would split one identifier across two enum values with no semantic difference - the cleaner path is one `EIN` value, with `EIN_NONPROFIT` grandfathered as-is (or aliased to `EIN` in the same revision). Proposed mint rule, mirroring UEI/FRS: mint only where the EIN's own filing is the witness **and** the link is not by name resemblance alone - require MATCH_ORG with a step-3 street+locality hit on a site of that org (name AND address agree), `registry_id` = 9 digits verbatim, `match_basis` e.g. `form5500_sponsor_ein_name_address:PY2024`, `as_of` = retrieval date. An EIN seen only in this project's own files is a phantom and mints nothing (AGENTS.md section 4).

Yield under that rule today: **320** sponsor EINs are mint-ready (MATCH_ORG with step `2+3`); a further 509 MATCH_ORG sponsors agree on name and state but have no address hit (most Atlas Ohio sites lack `street_address`: Ohio site street_address fill was 7.2% per the field-fill profile), so they would wait for an address or a second witness. Cautions for the owner: an EIN identifies a legal entity, not an establishment or a brand, and sole-proprietor/individual EINs exist - the Atlas records employers that are businesses, and the mint rule above never touches an entity that is a natural person; the rule above applies a vocabulary only - no row is minted by this lane.

## 9. Blockers, limits and honest caveats

- **Employer, not establishment.** One EIN may operate many plants; sponsor address is usually HQ/administration. Discovery rows yield employers to research, not sites.
- **Coverage bias.** Only employers sponsoring a retirement or (for 100+ participants / funded) welfare plan that files a 5500 or 5500-SF appear; one-participant plans file 5500-EZ (not in these datasets); small shops without a plan are invisible. Under-representation of the smallest establishments is structural.
- **Participants are not employees.** They include covered workers and leased/related-employer coverage under controlled-group and multiple-employer plans (a PEO or MEP sponsor can show participants at other employers). Treat the band as a plan-size input (R7f), not a headcount.
- **Code granularity.** See section 3: padded group codes only; 6-digit polymer codes are rare, and the Ring 3 Primary codes 424610/562920 do not exist in the Form 5500 code list (only 333511 appears, a handful of times) - Ring 3 distribution/recycling is not discoverable by this source.
- **Privacy.** Only business sponsor fields are published; no phone, email, officer or preparer names. 102 street lines are withheld where the sponsor name has no entity designator and the plan has fewer than 10 participants (possible home address, AGENTS.md section 6). Matching used the full address in memory before withholding.
- **Queue.** This lane did not touch `tasks/QUEUE.md` or `data/`; a QUEUE line and an integrator pass are needed before any band or EIN is applied.
- **Re-run:** `python3 scripts/build_form5500_spine.py --raw-dir /tmp/claude-0/f5500_raw --selftest 300` (downloads missing zips; deterministic apart from newly published DOL files).
