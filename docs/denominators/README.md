# QCEW polymer-industry denominators (reference data)

**Status: reference data, not canonical Atlas data.** Nothing here is merged into
`data/`, and nothing here changes a record, tier, status or count in the Atlas.
These files exist to unblock the Pennsylvania and PIC-12 denominators that
`docs/reviews/F5_PUBLIC_COUNTS_2026-10-30.md` ("Official denominator verification
and limits") recorded as BLOCKED because the source extracts were never committed.

Built by `scripts/build_qcew_denominators.py` (stdlib only; re-runnable:
`python3 scripts/build_qcew_denominators.py --raw-dir <dir> [--coverage-md]`).

| File | Content |
|---|---|
| `qcew_state_polymer_2023_2024.csv` | Private-sector annual averages: 50 states + DC + Puerto Rico + Virgin Islands (as BLS publishes them), plus the national row `US000`, x 8 industry codes x 2023 and 2024 (782 rows) |
| `qcew_county_polymer_ohio_pa_2023_2024.csv` | Same measures for every Ohio (39xxx) and Pennsylvania (42xxx) county that BLS publishes a row for, x 8 industry codes x 2 years (1,185 rows) |

A row exists only where BLS published one. A missing county x industry row means
BLS published no row for that cell; it is not recorded as zero here and is not
proven zero (see "Absent cells" below).

## Retrieval

- **Retrieved:** 2026-11-01 (UTC), with `curl` through the session proxy; every request returned HTTP 200.
- **Annual slices (one file per year x industry; `own_code` 5 rows filtered locally):**
  `https://data.bls.gov/cew/data/api/{YEAR}/a/industry/{INDUSTRY}.csv`
  for YEAR in 2023, 2024 and INDUSTRY in 326, 3261, 3262, 3252, 325211, 325212, 3259, 325991.
  Example: <https://data.bls.gov/cew/data/api/2023/a/industry/326.csv>.
- **Area titles:** <https://data.bls.gov/cew/doc/titles/area/area_titles.csv>
- **Documentation:** <https://www.bls.gov/cew/additional-resources/open-data/csv-data-slices.htm>
- **2024 annual is published** (all 8 slices returned data with `year` 2024, `qtr` A). Nothing is blocked.
- **Vintage caveat:** QCEW annual data is revised; these are the values served on the retrieval date. The Ohio DJFS benchmark cited by F5 reflects employer reports through 2024-06-01, so small differences from a later BLS pull would not be surprising (none were found; see the Ohio check).

SHA-256 of the raw slices as retrieved (raw files are kept outside the repo; re-download and compare to detect later revisions):

| Raw file | SHA-256 |
|---|---|
| `2023_3252.csv` | `7398ae97e5169fdac90156f200147bd9d03c96b2f5ed99eb9403ecab854e83a2` |
| `2023_325211.csv` | `d2938ef89852b8513993abf4a025364245ff1a1e00497366ca426e45250b490a` |
| `2023_325212.csv` | `cf79d9c48b4e04a2ddcdf2e15232f19ca87212dcbf9d556789ba7ab18df03ffb` |
| `2023_3259.csv` | `c697f1e848b1adbf0fb6635ecdcbcfbb3bff1824d1fa47f67ad246ccff946b62` |
| `2023_325991.csv` | `732d89f18ee9602fb60ba141d7aa6ed6748083f71de2edf526440f0bb82b3d00` |
| `2023_326.csv` | `5dc58c60c67b065cb3a79ce047ba381ae49838dea5743b6cf603b474b581b0c7` |
| `2023_3261.csv` | `57c387ecf4112bb78dd951d0afde3470f7e7b9df125baec5f5698ee758195b17` |
| `2023_3262.csv` | `f2ecefe1fa1f215b4ebefd102b62df042711e7ce3dc39f0ca3d5e4901d1c63e2` |
| `2024_3252.csv` | `2eeb7691b621baf07b101d86be09ac47727a7b2a80e607ffe5beebc4f4c49eef` |
| `2024_325211.csv` | `ad3e9066dfa1cc4b50615bededcf5c5cec157050e2ec3f085b9786dddc5d1cac` |
| `2024_325212.csv` | `b0bad2a5d426c5ac22acba024943b6ae762cb8f389b3d8a7dcb1b1d907a09211` |
| `2024_3259.csv` | `8be7b008ae706066737bb711e08154adfeabe98c003e540deac7234dbbf04303` |
| `2024_325991.csv` | `6ca8f8416ced2e002d13dc2c03485f8f01e6d6e97827b18456c40d1d0bbd1c95` |
| `2024_326.csv` | `3fe57abd3e94279729c25a1872b149359696487b1d0e891ad7f9ce08c97cfa05` |
| `2024_3261.csv` | `b4fd92626c2812ade3bf3500c47ea91649783791a49e76b331c6d0154b90b105` |
| `2024_3262.csv` | `deecc6e1876c154fae4076d6f205a7d6a1de7da1188b17fe57350ebb10f1143e` |
| `area_titles.csv` | `92ec00f591bd986cd46e027a05e35b33b0d2d724f3b76c96969f0e73145698d6` |

## Filters and fields

- `own_code` = 5 (private ownership); `qtr` = A (annual averages); `size_code` is 0 in every source row.
- State rows: `agglvl_code` 55-58 (state x NAICS 3/4/5/6-digit), area FIPS `SS000`. National row: `agglvl_code` 15-18, area `US000` (included in the state file, labelled `U.S. TOTAL`). County rows: `agglvl_code` 75-78, FIPS beginning 39 or 42. The county files include the BLS pseudo-areas `39999` / `42999` ("Unknown Or Undefined") if published; they are not real counties.
- Output fields: `year, area_fips, area_title, industry_code, own_code, agglvl_code, annual_avg_estabs, annual_avg_emplvl, total_annual_wages, avg_annual_pay, disclosure_code`. `area_title` comes from the BLS area titles file, not from this project.
- Industry codes: 326 (plastics and rubber products), 3261 (plastics products), 3262 (rubber products), 3252 (resin, synthetic rubber, artificial fibers), 325211 (plastics material and resin), 325212 (synthetic rubber), 3259 (other chemical products), 325991 (custom compounding of purchased resins). The `agglvl_code` carries the digit level (55/75 = 3-digit, 56/76 = 4-digit, 57/77 = 5-digit, 58/78 = 6-digit).

## Disclosure handling

BLS marks cells it cannot disclose with `disclosure_code` N and publishes
`annual_avg_emplvl`, `total_annual_wages` and `avg_annual_pay` on those rows as
**zeros**. Those zeros are not data. In the output CSVs those three fields are
written **empty** on every N row and `disclosure_code` stays `N`. Consumers must
never read an empty cell as zero.

`annual_avg_estabs` is different: on N rows BLS still publishes a non-zero
establishment count (employment and wages are withheld, the count is not).
The script keeps that count as published. Evidence that the N-row counts are
real values and not placeholders: summing published county counts reproduces the
published state count to within rounding of the annual averaging (differences
of at most 5), for example Ohio 2023 NAICS 326 counties sum 892 vs state 890,
3261 710 vs 706, 3262 185 vs 184, 3252 116 vs 115, 3259 156 vs 153. Because the
employment/wage fields are empty on N rows, those rows are still flagged in the
sums below with `*`.

The CSVs carry no zero in place of a suppressed value. If a future BLS release
blanks an establishment count the script writes it empty and the coverage
tables show "no row" or "suppressed", never zero.

## Known checks

### 1. Ohio 2023 private establishments vs the Ohio DJFS figures cited in F5

F5 cites the Ohio DJFS annual 2023 QCEW table (private sector heading):
326 = 890, 3261 = 706, 3262 = 184, 3252 = 115, 3259 = 153.

| NAICS | DJFS (cited in F5) | BLS 2023 area 39000, own 5 | Result | BLS 2024 (for reference) |
|---|---:|---:|---|---:|
| 326 | 890 | 890 | MATCH | 917 |
| 3261 | 706 | 706 | MATCH | 729 |
| 3262 | 184 | 184 | MATCH | 188 |
| 3252 | 115 | 115 | MATCH | 118 |
| 3259 | 153 | 153 | MATCH | 163 |

All five match exactly. This confirms the filter set (year 2023, quarter A,
area 39000, own_code 5, annual_avg_estabs) described in F5. It also means the
BLS API slice and the DJFS publication are the same data vintage for these cells.
Ohio sub-cells 325211 = 78, 325212 = 28 are published for 2023; 325991 for Ohio
carries disclosure_code N (estab count 36 published, employment and wages
withheld).

### 2. PIC-12 county FIPS verified against `area_titles.csv`

Each FIPS below was looked up in the BLS area titles file on the retrieval date
and the build script aborts if any title differs:

| FIPS | BLS area title |
|---|---|
| 39007 | Ashtabula County, Ohio |
| 39035 | Cuyahoga County, Ohio |
| 39055 | Geauga County, Ohio |
| 39085 | Lake County, Ohio |
| 39093 | Lorain County, Ohio |
| 39099 | Mahoning County, Ohio |
| 39103 | Medina County, Ohio |
| 39133 | Portage County, Ohio |
| 39151 | Stark County, Ohio |
| 39153 | Summit County, Ohio |
| 39155 | Trumbull County, Ohio |
| 39169 | Wayne County, Ohio |

Ashtabula is 39007; 39005 is Ashland County and is not in PIC-12.

### 3. PIC-12 county sums

Unit and filter: **sum of QCEW private-sector (own_code 5) annual-average
establishments over the 12 PIC-12 counties**, one row per county x industry as
published, annual averages for the stated year. Counties flagged `*` are included
at their published establishment count.


#### PIC-12 counties, 2023, private establishments (`annual_avg_estabs`)

`*` = row carries `disclosure_code` N (employment and wages withheld; establishment count still published). `--` = BLS published no row for that county x industry cell.

| County (FIPS) | 326 | 3261 | 3262 | 3252 | 325211 | 325212 | 3259 | 325991 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Ashtabula (39007) | 21 | 17\* | 4\* | 1\* | 1\* | -- | -- | -- |
| Cuyahoga (39035) | 65 | 58 | 7 | 8\* | 5 | 3\* | 15 | 1\* |
| Geauga (39055) | 28 | 21 | 7 | 7 | 3\* | 4\* | 3\* | 1\* |
| Lake (39085) | 23 | 17 | 6 | 3\* | 3\* | -- | 6\* | -- |
| Lorain (39093) | 18 | 15 | 3 | 2\* | 2\* | -- | 9 | 3\* |
| Mahoning (39099) | 19 | 17\* | 2\* | -- | -- | -- | -- | -- |
| Medina (39103) | 21 | 12 | 9 | 5 | 4\* | 1\* | 6 | -- |
| Portage (39133) | 35 | 27 | 8 | 5 | 3\* | 2\* | 5 | 3\* |
| Stark (39151) | 30 | 27 | 3 | 1\* | -- | 1\* | 7\* | 2\* |
| Summit (39153) | 76 | 48 | 28 | 18 | 6\* | 10 | 9 | 5 |
| Trumbull (39155) | 13 | 11\* | 2\* | -- | -- | -- | 1\* | -- |
| Wayne (39169) | 18 | 13 | 5 | 2\* | 1\* | 1\* | 1\* | 1\* |
| **Sum of published cells** | **367** | **283** | **84** | **52** | **28** | **22** | **62** | **16** |


#### PIC-12 counties, 2024, private establishments (`annual_avg_estabs`)

`*` = row carries `disclosure_code` N (employment and wages withheld; establishment count still published). `--` = BLS published no row for that county x industry cell.

| County (FIPS) | 326 | 3261 | 3262 | 3252 | 325211 | 325212 | 3259 | 325991 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Ashtabula (39007) | 19 | 15\* | 4\* | 2\* | 2\* | -- | -- | -- |
| Cuyahoga (39035) | 69 | 61 | 8 | 8\* | 5 | 3\* | 17 | 2\* |
| Geauga (39055) | 28 | 21 | 7 | 7 | 3\* | 4\* | 3\* | 1\* |
| Lake (39085) | 23 | 17 | 6 | 3\* | 3\* | -- | 5\* | -- |
| Lorain (39093) | 19 | 16\* | 3\* | 3\* | 3\* | -- | 10 | 3\* |
| Mahoning (39099) | 19 | 17\* | 2\* | -- | -- | -- | 1\* | -- |
| Medina (39103) | 23 | 14 | 8 | 5 | 4\* | 1\* | 6 | -- |
| Portage (39133) | 40 | 29 | 11 | 4 | 3\* | 1\* | 5 | 3\* |
| Stark (39151) | 29 | 26 | 3 | 1\* | -- | 1\* | 8 | 2\* |
| Summit (39153) | 77 | 47 | 30 | 19 | 7\* | 10 | 8 | 5\* |
| Trumbull (39155) | 13 | 11\* | 2\* | -- | -- | -- | 1\* | -- |
| Wayne (39169) | 16 | 12\* | 4\* | 2\* | 1\* | 1\* | 2\* | 1\* |
| **Sum of published cells** | **375** | **286** | **88** | **54** | **31** | **21** | **66** | **17** |

**PIC-12 sums versus the historically reported figures (2023):**

| NAICS | 2023 sum of published cells | N-flagged counties included | Counties with no row | Historical (F5 "historically reported") | Result |
|---|---:|---|---|---:|---|
| 326 | 367 | none | none | 367 | MATCH, complete (12 of 12 counties, no N flag) |
| 3261 | 283 | Ashtabula, Mahoning, Trumbull | none | 283 | MATCH; 3 counties are N-flagged (counts published) |
| 3262 | 84 | Ashtabula, Mahoning, Trumbull | none | 84 | MATCH; 3 counties are N-flagged |
| 3252 | 52 | Ashtabula, Cuyahoga, Lake, Lorain, Stark, Wayne | Mahoning, Trumbull | 52 | MATCH; 6 N-flagged, 2 no row |
| 3259 | 62 | Geauga, Lake, Stark, Trumbull, Wayne | Ashtabula, Mahoning | 62-63 | 62 reproduced; 63 not reproduced; 5 N-flagged, 2 no row |

Reading the table honestly:

- The sums reproduce the earlier numbers **only** when the establishment counts
  on N-flagged rows are included. If N-flagged cells were dropped the 2023 sums
  would be 238 (3261), 76 (3262), 35 (3252) and 44 (3259), which would be
  incomplete lower bounds and would not match the historical figures. The
  inclusion rests on the check in "Disclosure handling" (N-row estab counts are
  real and county counts reconcile to state totals within rounding).
- **Labeling:** 326 is a complete 12-of-12 sum with no N flag. The sums for
  3261, 3262, 3252 and 3259 each include N-flagged county cells (employment and
  wages are missing for those counties; establishment counts are published) and
  3252 and 3259 additionally have counties with no published row. They are
  "sum of published cells", not independently confirmed complete counts: a
  county with no row is treated as having no published establishments, which is
  not proven zero.
- That the sums agree with the old numbers shows the old numbers came from the
  same BLS 2023 annual private series. It does not verify the old, uncommitted
  extracts (`staging/working/denominators_pic12.csv`), which remain unavailable.
- The 3259 historical "62-63": the BLS pull gives 62. Nothing in the public
  files explains where 63 came from; do not state it as verified.
- 2023 sub-industry sums for context (many cells are N-flagged or absent, so
  treat as incomplete): 325211 = 28 (9 rows), 325212 = 22 (7 rows), 325991 = 16
  (7 rows). Per-county values are in the county CSV and the table above.
- A 325991 denominator is now available at state and county grain, but with
  heavy N-flagging and "no row" cells, so it is a published-cell figure, not a
  complete frame. F5 recorded 325991 as lacking a verified denominator; this
  provides one for Ohio (36) and Pennsylvania (23) at state level, 2023.

**Pennsylvania state denominators (2023, own 5):** 326 = 642, 3261 = 551,
3262 = 91, 3252 = 62, 3259 = 135, 325211 = 54 (N-flagged), 325212 = 4,
325991 = 23 (2024: 644, 556, 88, 67, 130, 59, 4, 21). This replaces the F5
"PA denominator BLOCKED" statement for these cells. F5's 396 PA NAICS-326 site
rows are a numerator: strict count 396 vs 642 = 61.7%, a count ratio and not
matched-facility coverage.


#### PIC-12 county 326 numerators vs QCEW 2023 (Ohio only)

| County | QCEW 2023 326 estabs | Atlas all rows | Atlas strict | Strict / QCEW | Gap |
|---|---:|---:|---:|---:|---:|
| Ashtabula | 21 | 25 | 25 | 119.0% | -4 |
| Cuyahoga | 65 | 95 | 81 | 124.6% | -16 |
| Geauga | 28 | 37 | 33 | 117.9% | -5 |
| Lake | 23 | 39 | 34 | 147.8% | -11 |
| Lorain | 18 | 23 | 23 | 127.8% | -5 |
| Mahoning | 19 | 22 | 21 | 110.5% | -2 |
| Medina | 21 | 18 | 18 | 85.7% | 3 |
| Portage | 35 | 52 | 48 | 137.1% | -13 |
| Stark | 30 | 31 | 30 | 100.0% | 0 |
| Summit | 76 | 104 | 91 | 119.7% | -15 |
| Trumbull | 13 | 5 | 5 | 38.5% | 8 |
| Wayne | 18 | 14 | 14 | 77.8% | 4 |
| **PIC-12** | **367** | **465** | **423** | **115.3%** | **-56** |

### 4. Atlas vs QCEW coverage by state (NAICS prefix tables)

**Caveat, as in F5:** a count ratio is **not matched-facility coverage**, and a
ratio over 100% is **not proof of completeness** or evidence of "excess"
discovery. The Atlas numerator includes non-manufacturing and inferred-NAICS
sites and is a 2026 inventory; the denominator is a 2023 annual average of
private-sector establishments (an establishment is a QCEW reporting unit, not
necessarily a plant). No matched ratio is claimed.

**Numerator units and filters (both stated, both from `data/sites_*.csv`, read
at build time; Atlas states are the physical `state` column of the site row):**

- **Atlas all rows:** Atlas site rows, any tier, any operating status,
  NAICS-coded with `naics_primary` starting with the code. Includes closed rows
  and tier U.
- **Atlas strict:** Atlas site rows with `operating_status` in (`active`,
  `unknown`) AND `verification_tier` in (A, B, C), NAICS-coded with
  `naics_primary` starting with the code. No parent inheritance, no secondary
  NAICS. The strict cut equals the F5 "primary" cut and reproduces F5's
  published numerators exactly (OH 326/3261/3262/3252/3259 = 815/648/167/82/79;
  PA 326 = 396).
- **Denominator:** QCEW 2023 private establishments (`annual_avg_estabs`,
  own_code 5), same-state row. **Gap** = QCEW minus Atlas strict (negative means
  more strict Atlas sites than QCEW establishments).
- Rows with blank NAICS are not in any numerator. The note that F5's
  "recorded" cut (any tier, active/unknown only) differs from the "all rows"
  column here (which also includes closed and other statuses) applies: OH 326
  all rows = 1,025 here vs F5 recorded = 988.

**National totals, NAICS 326, 2023:** QCEW private establishments = **14,200**
(US000 national row; the 50 states + DC sum to 14,205 and with Puerto Rico
14,244; state sums differ from the national row by a few establishments,
reason not established here, likely annual-average rounding). Atlas strict = **2,201**, Atlas all rows = **2,412** (all US site
rows; no Atlas site is outside the 50 states + DC + PR list). Strict / national
= 15.5%. Also national QCEW 2023 3261 = 12,048, 3262 = 2,152, 3252 = 1,965,
3259 = 3,414, 325211 = 1,511, 325212 = 219, 325991 = 463 (2024: 326 = 14,375).

The tables below are generated by
`python3 scripts/build_qcew_denominators.py --raw-dir <dir> --coverage-md`
and are a snapshot of the Atlas as of the retrieval date. They go stale as
`data/sites_*.csv` changes; re-run rather than edit.


#### NAICS 326, all states, sorted by QCEW 326 establishments (descending)

| State | QCEW 2023 private estabs | Atlas all rows | Atlas strict | All / QCEW | Strict / QCEW | Gap (QCEW - strict) |
|---|---:|---:|---:|---:|---:|---:|
| CA | 1306 | 39 | 39 | 3.0% | 3.0% | 1267 |
| TX | 953 | 84 | 84 | 8.8% | 8.8% | 869 |
| OH | 890 | 1025 | 815 | 115.2% | 91.6% | 75 |
| MI | 819 | 47 | 47 | 5.7% | 5.7% | 772 |
| FL | 798 | 23 | 23 | 2.9% | 2.9% | 775 |
| IL | 797 | 42 | 42 | 5.3% | 5.3% | 755 |
| PA | 642 | 397 | 396 | 61.8% | 61.7% | 246 |
| IN | 512 | 82 | 82 | 16.0% | 16.0% | 430 |
| GA | 491 | 45 | 45 | 9.2% | 9.2% | 446 |
| WI | 456 | 48 | 48 | 10.5% | 10.5% | 408 |
| NC | 453 | 71 | 71 | 15.7% | 15.7% | 382 |
| NY | 410 | 23 | 23 | 5.6% | 5.6% | 387 |
| SC | 406 | 49 | 49 | 12.1% | 12.1% | 357 |
| TN | 401 | 51 | 51 | 12.7% | 12.7% | 350 |
| MN | 368 | 19 | 19 | 5.2% | 5.2% | 349 |
| MO | 368 | 37 | 37 | 10.1% | 10.1% | 331 |
| NJ | 368 | 13 | 13 | 3.5% | 3.5% | 355 |
| KY | 282 | 22 | 22 | 7.8% | 7.8% | 260 |
| VA | 241 | 28 | 28 | 11.6% | 11.6% | 213 |
| AL | 239 | 20 | 20 | 8.4% | 8.4% | 219 |
| MA | 236 | 15 | 15 | 6.4% | 6.4% | 221 |
| UT | 205 | 10 | 10 | 4.9% | 4.9% | 195 |
| WA | 194 | 16 | 16 | 8.2% | 8.2% | 178 |
| IA | 191 | 17 | 17 | 8.9% | 8.9% | 174 |
| OR | 174 | 10 | 10 | 5.7% | 5.7% | 164 |
| CO | 168 | 5 | 5 | 3.0% | 3.0% | 163 |
| CT | 164 | 7 | 7 | 4.3% | 4.3% | 157 |
| AZ | 163 | 14 | 14 | 8.6% | 8.6% | 149 |
| KS | 133 | 21 | 21 | 15.8% | 15.8% | 112 |
| MD | 127 | 9 | 9 | 7.1% | 7.1% | 118 |
| AR | 125 | 19 | 19 | 15.2% | 15.2% | 106 |
| OK | 121 | 13 | 13 | 10.7% | 10.7% | 108 |
| LA | 117 | 6 | 6 | 5.1% | 5.1% | 111 |
| MS | 115 | 23 | 23 | 20.0% | 20.0% | 92 |
| ID | 103 | 4 | 4 | 3.9% | 3.9% | 99 |
| NV | 100 | 10 | 10 | 10.0% | 10.0% | 90 |
| NH | 82 | 5 | 5 | 6.1% | 6.1% | 77 |
| NE | 77 | 11 | 11 | 14.3% | 14.3% | 66 |
| RI | 53 | 4 | 4 | 7.5% | 7.5% | 49 |
| WV | 53 | 8 | 8 | 15.1% | 15.1% | 45 |
| DE | 48 | 3 | 3 | 6.2% | 6.2% | 45 |
| ME | 47 | 6 | 6 | 12.8% | 12.8% | 41 |
| SD | 46 | 4 | 4 | 8.7% | 8.7% | 42 |
| NM | 39 | 2 | 2 | 5.1% | 5.1% | 37 |
| PR | 39 | 0 | 0 | 0.0% | 0.0% | 39 |
| MT | 32 | 1 | 1 | 3.1% | 3.1% | 31 |
| ND | 31 | 1 | 1 | 3.2% | 3.2% | 30 |
| VT | 22 | 1 | 1 | 4.5% | 4.5% | 21 |
| HI | 20 | 0 | 0 | 0.0% | 0.0% | 20 |
| WY | 13 | 2 | 2 | 15.4% | 15.4% | 11 |
| AK | 5 | 0 | 0 | 0.0% | 0.0% | 5 |
| DC | 1 | 0 | 0 | 0.0% | 0.0% | 1 |
| **Sum of listed areas (50 states + DC + PR)** | **14244** | **2412** | **2201** | 16.9% | 15.5% | 12043 |

Top 15 areas by gap (QCEW minus strict Atlas), NAICS 326:

| Rank | State | Gap | QCEW | Atlas strict |
|---:|---|---:|---:|---:|
| 1 | CA | 1267 | 1306 | 39 |
| 2 | TX | 869 | 953 | 84 |
| 3 | FL | 775 | 798 | 23 |
| 4 | MI | 772 | 819 | 47 |
| 5 | IL | 755 | 797 | 42 |
| 6 | GA | 446 | 491 | 45 |
| 7 | IN | 430 | 512 | 82 |
| 8 | WI | 408 | 456 | 48 |
| 9 | NY | 387 | 410 | 23 |
| 10 | NC | 382 | 453 | 71 |
| 11 | SC | 357 | 406 | 49 |
| 12 | NJ | 355 | 368 | 13 |
| 13 | TN | 350 | 401 | 51 |
| 14 | MN | 349 | 368 | 19 |
| 15 | MO | 331 | 368 | 37 |

#### NAICS 3261, 3262, 3252, 3259 in the same state order (QCEW 326 descending)

Cell format: `QCEW / Atlas strict / gap`. `no row` = BLS published no state row for that cell (no value is invented; the gap is not computed).

| State | 3261 | 3262 | 3252 | 3259 |
|---|---|---|---|---|
| CA | 1118 / 32 / 1086 | 188 / 7 / 181 | 167 / 15 / 152 | 287 / 3 / 284 |
| TX | 817 / 79 / 738 | 136 / 5 / 131 | 208 / 48 / 160 | 331 / 16 / 315 |
| OH | 706 / 648 / 58 | 184 / 167 / 17 | 115 / 82 / 33 | 153 / 79 / 74 |
| MI | 690 / 38 / 652 | 129 / 9 / 120 | 109 / 13 / 96 | 193 / 7 / 186 |
| FL | 684 / 21 / 663 | 115 / 2 / 113 | 105 / 8 / 97 | 222 / 3 / 219 |
| IL | 691 / 29 / 662 | 106 / 13 / 93 | 111 / 17 / 94 | 199 / 10 / 189 |
| PA | 551 / 347 / 204 | 91 / 49 / 42 | 62 / 86 / -24 | 135 / 24 / 111 |
| IN | 443 / 61 / 382 | 69 / 21 / 48 | 47 / 6 / 41 | 90 / 10 / 80 |
| GA | 401 / 32 / 369 | 89 / 13 / 76 | 93 / 12 / 81 | 138 / 11 / 127 |
| WI | 413 / 39 / 374 | 44 / 9 / 35 | 22 / 6 / 16 | 53 / 4 / 49 |
| NC | 375 / 57 / 318 | 78 / 14 / 64 | 94 / 17 / 77 | 92 / 11 / 81 |
| NY | 366 / 20 / 346 | 44 / 3 / 41 | 25 / 6 / 19 | 101 / 3 / 98 |
| SC | 338 / 29 / 309 | 68 / 20 / 48 | 86 / 18 / 68 | 101 / 3 / 98 |
| TN | 319 / 32 / 287 | 82 / 19 / 63 | 93 / 13 / 80 | 87 / 11 / 76 |
| MN | 316 / 19 / 297 | 52 / 0 / 52 | 13 / 2 / 11 | 63 / 3 / 60 |
| MO | 309 / 27 / 282 | 59 / 10 / 49 | 36 / 8 / 28 | 72 / 5 / 67 |
| NJ | 315 / 11 / 304 | 54 / 2 / 52 | 62 / 8 / 54 | 120 / 9 / 111 |
| KY | 224 / 16 / 208 | 58 / 6 / 52 | 74 / 13 / 61 | 95 / 5 / 90 |
| VA | 205 / 23 / 182 | 36 / 5 / 31 | 58 / 7 / 51 | 82 / 1 / 81 |
| AL | 192 / 16 / 176 | 48 / 4 / 44 | 47 / 6 / 41 | 55 / 2 / 53 |
| MA | 213 / 13 / 200 | 24 / 2 / 22 | 33 / 10 / 23 | 48 / 5 / 43 |
| UT | 177 / 9 / 168 | 29 / 1 / 28 | 19 / 1 / 18 | 38 / 0 / 38 |
| WA | 181 / 16 / 165 | 13 / 0 / 13 | 14 / 1 / 13 | 37 / 0 / 37 |
| IA | 161 / 10 / 151 | 30 / 7 / 23 | 10 / 3 / 7 | 24 / 0 / 24 |
| OR | 146 / 8 / 138 | 28 / 2 / 26 | 18 / 8 / 10 | 56 / 0 / 56 |
| CO | 157 / 5 / 152 | 11 / 0 / 11 | 15 / 1 / 14 | 43 / 3 / 40 |
| CT | 143 / 5 / 138 | 21 / 2 / 19 | 21 / 4 / 17 | 36 / 4 / 32 |
| AZ | 143 / 13 / 130 | 20 / 1 / 19 | 12 / 1 / 11 | 36 / 2 / 34 |
| KS | 112 / 14 / 98 | 22 / 7 / 15 | 6 / 2 / 4 | 33 / 3 / 30 |
| MD | 105 / 8 / 97 | 21 / 1 / 20 | 19 / 2 / 17 | 38 / 0 / 38 |
| AR | 95 / 10 / 85 | 30 / 9 / 21 | 10 / 5 / 5 | 19 / 2 / 17 |
| OK | 102 / 10 / 92 | 19 / 3 / 16 | 14 / 2 / 12 | 55 / 1 / 54 |
| LA | 92 / 6 / 86 | 25 / 0 / 25 | 41 / 15 / 26 | 59 / 1 / 58 |
| MS | 100 / 18 / 82 | 15 / 5 / 10 | 19 / 6 / 13 | 24 / 4 / 20 |
| ID | 82 / 4 / 78 | 21 / 0 / 21 | 4 / 0 / 4 | 25 / 0 / 25 |
| NV | 91 / 9 / 82 | 8 / 1 / 7 | 3 / 0 / 3 | 26 / 0 / 26 |
| NH | 69 / 4 / 65 | 13 / 1 / 12 | 10 / 1 / 9 | 9 / 0 / 9 |
| NE | 61 / 7 / 54 | 16 / 4 / 12 | 4 / 0 / 4 | 10 / 0 / 10 |
| RI | 49 / 4 / 45 | 4 / 0 / 4 | 13 / 1 / 12 | 10 / 1 / 9 |
| WV | 46 / 4 / 42 | 7 / 4 / 3 | 20 / 7 / 13 | 19 / 1 / 18 |
| DE | 41 / 3 / 38 | 7 / 0 / 7 | 18 / 0 / 18 | 16 / 1 / 15 |
| ME | 41 / 6 / 35 | 6 / 0 / 6 | 3 / 0 / 3 | 9 / 0 / 9 |
| SD | 36 / 4 / 32 | 10 / 0 / 10 | 1 / 0 / 1 | 5 / 0 / 5 |
| NM | 31 / 2 / 29 | 8 / 0 / 8 | 6 / 0 / 6 | 34 / 0 / 34 |
| PR | 35 / 0 / 35 | 4 / 0 / 4 | 8 / 0 / 8 | 15 / 1 / 14 |
| MT | 27 / 1 / 26 | 5 / 0 / 5 | no row | 7 / 0 / 7 |
| ND | 28 / 1 / 27 | 3 / 0 / 3 | 2 / 0 / 2 | 3 / 0 / 3 |
| VT | 19 / 1 / 18 | 3 / 0 / 3 | 6 / 1 / 5 | 8 / 0 / 8 |
| HI | 18 / 0 / 18 | 2 / 0 / 2 | no row | 3 / 0 / 3 |
| WY | 10 / 2 / 8 | 3 / 0 / 3 | 1 / 0 / 1 | 11 / 0 / 11 |
| AK | 4 / 0 / 4 | 1 / 0 / 1 | 1 / 0 / 1 | 8 / 0 / 8 |
| DC | 1 / 0 / 1 | no row | no row | no row |
| **Sum** | **12089 / 1773 / 10316** | **2159 / 428 / 1731** | **1978 / 463 / 1515** | **3433 / 249 / 3184** |

Sub-industries 325211, 325212 and 325991 are not tabulated by state: most state
cells are N-flagged or absent, so a state-by-state ratio would be dominated by
incomplete denominators. Their state values are in the state CSV.

## Reading cautions

- Counts ratios compare unlike things: Atlas site rows (2026, includes
  non-manufacturing and inferred NAICS, one site can carry a different prefix
  than the QCEW unit) vs QCEW establishments (2023 annual average). Do not
  publish these as "coverage %" without the matched-facility analysis F5 calls
  for.
- The large gaps outside Ohio mostly reflect where the Atlas has done discovery
  work (Ohio and Pennsylvania lead); they are a "where to look next" ordering,
  not a measure of how many plants are missing.
- Do not blend CBP and QCEW (F5): CBP uses a different frame and its own
  suppression, and the two must not fill each other's suppressed cells.
- QCEW covers employer establishments in UI-covered employment; own_code 5 is
  private only (government-owned plants are excluded).
