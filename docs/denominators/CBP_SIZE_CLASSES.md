# CBP establishment size classes, polymer NAICS (reference data)

**Status: reference data, not canonical Atlas data.** Nothing here is merged into
`data/`, and nothing here changes a record, tier, status or count in the Atlas.
Companion to the QCEW denominators in [`README.md`](README.md) (same folder):
that file gives *how many* establishments QCEW counts; this one shows *what size*
CBP says they are, so the owner can see which sources can reach the coverage gap.

Built by `scripts/build_cbp_size_classes.py` (stdlib only; re-runnable:
`python3 scripts/build_cbp_size_classes.py --raw-dir /tmp/claude-0/cbp_raw`;
add `--tables-md` to regenerate the tables below). Output:
[`cbp_size_classes_polymer.csv`](cbp_size_classes_polymer.csv) (5,190 rows:
50 US rows, 2,380 state rows, 2,760 Ohio/Pennsylvania county rows).

**Do not blend CBP and QCEW.** CBP and QCEW use different frames, reference
periods and suppression rules (see "CBP versus QCEW" below). No ratio in this
file or its CSV divides a CBP number by a QCEW number or fills one source's
suppressed cell from the other.

PIC-18 refresh (2026-11-06): the rebuilt 5,190-row CSV is byte-identical: all six added counties were already present. The report tables now use `regions.PIC18`; the six added counties reconcile to the Census API in `tasks/source-scout-3-2026-11-06/cbp/`.

## Retrieval

- **Retrieved:** 2026-11-01 (UTC). **Reference year:** 2023 (mid-March employment-size class; 2017 NAICS). No API and no key: the Census Data API's data endpoint answered every query from this environment with a redirect to a "missing key" page, so the public bulk files were used instead. Metadata (`variables.json`) was reachable, but no data was pulled from the API.
- **Bulk files** (HTTP 200, downloaded whole, cached outside the repo in `/tmp/claude-0/cbp_raw/`):
  - <https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23us.zip> (nation)
  - <https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23st.zip> (states)
  - <https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip> (counties; stream-filtered to NAICS 326/3261/3262/3252/3259 rows for FIPS state 39 and 42, never loaded whole)
- **County names only** (no data): <https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt>; the script aborts if any PIC-18 FIPS does not match its expected county name.
- **Record layouts** used to verify field names (linked from <https://www.census.gov/programs-surveys/cbp/technical-documentation/record-layouts.html>): `us-layout-2018.txt` (U.S., 2018-2023), `state-layout-2020.txt`, `county-layout-2020.txt` (County, 2020-2023), all under <https://www2.census.gov/programs-surveys/cbp/technical-documentation/records-layouts/>.
- **Methodology page:** <https://www.census.gov/programs-surveys/cbp/technical-documentation/methodology.html>. The page itself carries a notice (read 2026-11-01) that it "is no longer current" because the Census Bureau is evaluating alternatives to noise infusion; the statements used below are the ones on that page.

SHA-256 of the downloaded files (re-download and compare to detect a later revision):

| File | SHA-256 |
|---|---|
| `cbp23us.zip` | `3f9018f807f1ffd7bcbb00690f9792573bc2bc6bb4cfab9df14ca7ab3eac0862` |
| `cbp23st.zip` | `9fc306ecc4f9633092e2432c2db2acdf53798da0480e6f6beeb953d583b41ede` |
| `cbp23co.zip` | `e9539e96ceb91608ad44ab1cfc651d7c1ff9b88bddfe7a8ff64134ccde6e9603` |
| `national_county2020.txt` | `9f6e5f6eb6ac2f5e9a36d5fd01dec77991bddc75118f748a069441a4782970d6` |

## Method and fields

- **Fields (verified in the layouts, not assumed):** `naics`, `lfo` (nation and state files only; `-` = all legal forms; the county file has no `lfo` column and is all forms), `est` (total establishments) and the establishment-count size-class columns `n<5, n5_9, n10_19, n20_49, n50_99, n100_249, n250_499, n500_999, n1000`. The county file also carries `n1000_1`..`n1000_4` sub-classes of 1,000+; they are not used.
- **Filters:** NAICS 326, 3261, 3262, 3252, 3259 (CBP stores them padded, e.g. `326///`); legal form `-` (all) for nation and states; United States, 50 state-level rows, and every Ohio and Pennsylvania county that has a row (the PIC-18 counties are Ohio counties). Puerto Rico is not in these files.
- **Unit:** employer establishments (locations with paid employees at any time in the year; government establishments are excluded except a short list of government-sponsored industries). Size class is by **mid-March 2023 paid employment**. The `<5` class (formerly "1 to 4") includes establishments that reported no mid-March paid employees but paid wages at some time during the year (methodology page). So `<5` is not strictly "1-4 employees".
- **Noise and flags.** CBP noise-infuses employment and payroll (flags G/H/J on those fields). The layouts give **no noise flag** on `est` or on the size-class establishment counts, and this file uses only those counts, not employment or payroll. The only flag on a size-class count is **`N`: "Not available or not comparable"** (layout). The methodology page states that since reference year 2017 a cell is published only if it holds three or more establishments, and otherwise it is dropped. The CSV preserves `N` as an empty `estab` with `estab_flag = N`. **An `N` cell is never read as zero.**
- **What `N` hides, arithmetically.** `EST` is always published. In every row with no `N` cell the nine size classes sum to `EST` exactly (the script aborts otherwise; none failed). So in a row with `N` cells, `EST` minus the published cells is the number of establishments sitting in the `N` cells together. This residual is arithmetic, not an official value (Census: values derived by subtraction "are not official"), and it does not say how the residual divides among the `N` cells.
- **Shares and bounds.** Bands are sums of CBP classes: **<20** = `<5` + `5-9` + `10-19`; **20-99** = `20-49` + `50-99`; **100+** = `100-249` + `250-499` + `500-999` + `1000+`. Share = band establishments / `EST`. Where a band contains no `N` cell the share is exact. Where it does, the table shows `low-high%`: low = published cells only; high = low plus the whole residual (valid because the residual cannot be larger than all establishments in `N` cells). That is a bound, not an estimate; the actual share is somewhere inside it. A band that is entirely `N` can run from 0% to the residual share.
- **CSV columns:** `year, geo_level (US|state|county), geo_fips, geo_usps, geo_name, naics, naics_title, size_code, size_label, estab, estab_flag, estab_total_row, legal_form, source_file`. `size_code` is `all` (the `EST` total, never flagged), `lt5, 5_9, 10_19, 20_49, 50_99, 100_249, 250_499, 500_999, 1000plus`. A geography with no CBP row for a NAICS has no CSV rows for it (absent, not zero).

## CBP versus QCEW (why they are never blended)

| | CBP 2023 (this file) | QCEW 2023 ([README](README.md)) |
|---|---|---|
| Reference period | Mid-March employment; counts locations with paid employees any time in the year | Annual average of monthly establishment counts |
| Frame | Census Business Register (administrative records plus surveys); excludes businesses without an EIN or without employees and most government establishments; the methodology notes undercoverage, mainly multi-unit companies and very small employers, and says Census has no estimate of establishment undercoverage | State UI-covered employment, private-sector rows (own_code 5) |
| Disclosure | Cells under 3 establishments not published (`N`); noise on employment and payroll | Disclosure code N withholds employment/wages; establishment count still published |
| Size detail | Establishment counts by 9 size classes | None in the files used |

For scale only, with no ratio drawn: CBP 2023 NAICS 326 (all forms, US) = 11,392 establishments; QCEW 2023 NAICS 326 (private, US000) = 14,200 establishments (README). The 50 CBP state rows for 326 sum to 11,391, one less than the national row (reason not established here). The two frames count different things, so use CBP here for the **shape** of the size distribution, not as a replacement denominator.

## Size distributions

#### Table 1. United States, NAICS 326, CBP 2023: establishments by employment-size class

Unit and filter: **employer establishments** (CBP `EST` and `N*` fields), NAICS 326 (2017 NAICS), all legal forms, United States (50 states + DC), mid-March 2023 employment-size class, all published (no `N` flag in any national cell).

| Size class (CBP column) | Establishments | Share of 326 EST |
|---|---:|---:|
| <5 employees (CBP '<5', formerly 1-4) (`n<5`) | 2,184 | 19.2% |
| 5-9 employees (`n5_9`) | 1,292 | 11.3% |
| 10-19 employees (`n10_19`) | 1,669 | 14.7% |
| 20-49 employees (`n20_49`) | 2,313 | 20.3% |
| 50-99 employees (`n50_99`) | 1,730 | 15.2% |
| 100-249 employees (`n100_249`) | 1,532 | 13.4% |
| 250-499 employees (`n250_499`) | 482 | 4.2% |
| 500-999 employees (`n500_999`) | 125 | 1.1% |
| 1,000+ employees (`n1000`) | 65 | 0.6% |
| **All (EST)** | **11,392** | 100.0% |

#### Table 2. United States, CBP 2023: share of establishments by band, five NAICS

Unit and filter: **share of employer establishments** in the NAICS, all legal forms, United States. Bands are sums of CBP size classes: <20 = `<5` + `5-9` + `10-19` (below OSHA ITA's 20-employee reach); 20-99 = `20-49` + `50-99`; 100+ = `100-249` + `250-499` + `500-999` + `1000+`. No national cell is `N`, so bands are exact.

| Geography | Establishments (EST) | <20 employees | 20-99 | 100+ | Any N-flagged cell? |
|---|---:|---:|---:|---:|---|
| US, NAICS 326 | 11,392 | 45.2% | 35.5% | 19.3% | no |
| US, NAICS 3261 | 9,636 | 43.8% | 36.4% | 19.9% | no |
| US, NAICS 3262 | 1,756 | 52.7% | 30.8% | 16.6% | no |
| US, NAICS 3252 | 1,567 | 42.1% | 39.8% | 18.1% | no |
| US, NAICS 3259 | 2,251 | 61.5% | 29.0% | 9.5% | no |

#### Table 3. Top-15 gap states, NAICS 326, CBP 2023: share of establishments by band

Unit and filter: **share of employer establishments**, NAICS 326, all legal forms, state-level CBP rows, in the NAICS 326 gap-rank order of `docs/denominators/README.md` (QCEW minus strict Atlas; that ranking uses QCEW and is not recomputed here). Where a band contains an `N` cell the cell shows `low-high%`: low = published cells only; high = low plus every establishment sitting in `N` cells (`EST` minus published cells), a bound and not an estimate.

| Geography | Establishments (EST) | <20 employees | 20-99 | 100+ | Any N-flagged cell? |
|---|---:|---:|---:|---:|---|
| CA | 1,126 | 58.3% | 29.6% | 12.0-12.1% | yes (1 estab in N cells) |
| TX | 780 | 48.7% | 35.0% | 16.3% | no |
| FL | 469 | 66.5% | 23.7% | 9.4-9.8% | yes (2 estab in N cells) |
| MI | 598 | 38.8% | 34.6% | 26.6% | no |
| IL | 620 | 45.3% | 36.0% | 18.4-18.7% | yes (2 estab in N cells) |
| GA | 373 | 35.9% | 36.7% | 27.3% | no |
| IN | 468 | 31.4% | 43.6% | 25.0% | no |
| WI | 419 | 36.0% | 39.1% | 24.6-24.8% | yes (1 estab in N cells) |
| NY | 371 | 49.1% | 35.3% | 15.4-15.6% | yes (1 estab in N cells) |
| NC | 380 | 32.4% | 41.6% | 26.1% | no |
| SC | 207 | 35.3% | 36.7% | 28.0% | no |
| NJ | 304 | 45.7% | 41.1% | 12.2-13.2% | yes (3 estab in N cells) |
| TN | 317 | 37.2% | 35.0% | 27.8% | no |
| MN | 276 | 48.2% | 33.7% | 17.4-18.1% | yes (2 estab in N cells) |
| MO | 241 | 42.7% | 38.6% | 18.7% | no |

#### Table 3b. Top-15 gap states, NAICS 326, CBP 2023: establishments by size class

Unit and filter: **employer establishments**, NAICS 326, all legal forms. `N` = CBP's flag for a not-available cell; it is not zero. Last column = establishments in `N` cells (`EST` minus published cells; arithmetic residual, not an official value).

| State | EST | <5 | 5-9 | 10-19 | 20-49 | 50-99 | 100-249 | 250-499 | 500-999 | 1000+ | In N cells |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CA | 1,126 | 292 | 154 | 211 | 213 | 120 | 104 | 26 | 5 | N | 1 |
| TX | 780 | 170 | 87 | 123 | 159 | 114 | 86 | 23 | 14 | 4 | 0 |
| FL | 469 | 175 | 58 | 79 | 72 | 39 | 35 | 9 | N | N | 2 |
| MI | 598 | 103 | 55 | 74 | 110 | 97 | 108 | 43 | 4 | 4 | 0 |
| IL | 620 | 125 | 61 | 95 | 135 | 88 | 90 | 19 | N | 5 | 2 |
| GA | 373 | 51 | 27 | 56 | 75 | 62 | 79 | 15 | 4 | 4 | 0 |
| IN | 468 | 50 | 41 | 56 | 103 | 101 | 83 | 24 | 7 | 3 | 0 |
| WI | 419 | 53 | 49 | 49 | 87 | 77 | 77 | 21 | 5 | N | 1 |
| NY | 371 | 84 | 39 | 59 | 80 | 51 | 41 | 13 | N | 3 | 1 |
| NC | 380 | 49 | 38 | 36 | 79 | 79 | 67 | 19 | 8 | 5 | 0 |
| SC | 207 | 32 | 18 | 23 | 40 | 36 | 31 | 17 | 4 | 6 | 0 |
| NJ | 304 | 50 | 39 | 50 | 73 | 52 | 31 | 6 | N | N | 3 |
| TN | 317 | 49 | 28 | 41 | 63 | 48 | 53 | 27 | 4 | 4 | 0 |
| MN | 276 | 53 | 38 | 42 | 60 | 33 | 41 | 7 | N | N | 2 |
| MO | 241 | 41 | 33 | 29 | 58 | 35 | 37 | 8 | N | N | 0 |

#### Table 4. PIC-18 counties, NAICS 326, CBP 2023: share of establishments by band

Unit and filter: **share of employer establishments**, NAICS 326, all legal forms, county-level CBP rows (the county file has no legal-form column). The `PIC-18 sum` row adds the 18 counties' published cells; its `N`-cell residual is summed over counties, so its bounds are for the sum of published county rows. Bounds as in Table 3.

| Geography | Establishments (EST) | <20 employees | 20-99 | 100+ | Any N-flagged cell? |
|---|---:|---:|---:|---:|---|
| Ashland (39005) | 4 | 0.0-100.0% | 0.0-100.0% | 0.0-100.0% | yes (4 estab in N cells) |
| Ashtabula (39007) | 25 | 28.0-36.0% | 44.0% | 20.0-28.0% | yes (2 estab in N cells) |
| Columbiana (39029) | 3 | 0.0-100.0% | 0.0-100.0% | 0.0-100.0% | yes (3 estab in N cells) |
| Cuyahoga (39035) | 55 | 56.4% | 30.9% | 10.9-12.7% | yes (1 estab in N cells) |
| Erie (39043) | 5 | 0.0-100.0% | 0.0-100.0% | 0.0-100.0% | yes (5 estab in N cells) |
| Geauga (39055) | 25 | 40.0-56.0% | 32.0% | 12.0-28.0% | yes (4 estab in N cells) |
| Huron (39077) | 8 | 0.0-100.0% | 0.0-100.0% | 0.0-100.0% | yes (8 estab in N cells) |
| Lake (39085) | 21 | 33.3-38.1% | 42.9% | 19.0-23.8% | yes (1 estab in N cells) |
| Lorain (39093) | 27 | 40.7% | 40.7% | 18.5% | no |
| Mahoning (39099) | 14 | 0.0-57.1% | 42.9% | 0.0-57.1% | yes (8 estab in N cells) |
| Medina (39103) | 17 | 35.3-82.4% | 17.6-64.7% | 0.0-47.1% | yes (8 estab in N cells) |
| Portage (39133) | 42 | 26.2% | 50.0% | 23.8% | no |
| Richland (39139) | 5 | 0.0-100.0% | 0.0-100.0% | 0.0-100.0% | yes (5 estab in N cells) |
| Stark (39151) | 29 | 55.2% | 31.0% | 0.0-13.8% | yes (4 estab in N cells) |
| Summit (39153) | 75 | 48.0% | 37.3% | 9.3-14.7% | yes (4 estab in N cells) |
| Trumbull (39155) | 8 | 0.0-100.0% | 0.0-100.0% | 0.0-100.0% | yes (8 estab in N cells) |
| Tuscarawas (39157) | 25 | 24.0-44.0% | 32.0% | 24.0-44.0% | yes (5 estab in N cells) |
| Wayne (39169) | 13 | 0.0-46.2% | 30.8-76.9% | 23.1-69.2% | yes (6 estab in N cells) |
| **PIC-18 sum** (18 of 18 counties with a row) | 401 | 35.2-54.1% | 33.7-52.6% | 12.2-31.2% | yes (76 estab in N cells) |

#### Table 4b. PIC-18 counties, NAICS 326, CBP 2023: establishments by size class

Unit and filter: **employer establishments**, NAICS 326, all legal forms. `N` is not zero.

| County (FIPS) | EST | <5 | 5-9 | 10-19 | 20-49 | 50-99 | 100-249 | 250-499 | 500-999 | 1000+ | In N cells |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Ashland (39005) | 4 | N | N | N | N | N | N | N | N | N | 4 |
| Ashtabula (39007) | 25 | 4 | N | 3 | 5 | 6 | 5 | N | N | N | 2 |
| Columbiana (39029) | 3 | N | N | N | N | N | N | N | N | N | 3 |
| Cuyahoga (39035) | 55 | 19 | 7 | 5 | 10 | 7 | 6 | N | N | N | 1 |
| Erie (39043) | 5 | N | N | N | N | N | N | N | N | N | 5 |
| Geauga (39055) | 25 | 4 | N | 6 | 5 | 3 | 3 | N | N | N | 4 |
| Huron (39077) | 8 | N | N | N | N | N | N | N | N | N | 8 |
| Lake (39085) | 21 | 4 | N | 3 | 5 | 4 | 4 | N | N | N | 1 |
| Lorain (39093) | 27 | 3 | 4 | 4 | 5 | 6 | 5 | N | N | N | 0 |
| Mahoning (39099) | 14 | N | N | N | 3 | 3 | N | N | N | N | 8 |
| Medina (39103) | 17 | 3 | 3 | N | 3 | N | N | N | N | N | 8 |
| Portage (39133) | 42 | 3 | 4 | 4 | 9 | 12 | 7 | 3 | N | N | 0 |
| Richland (39139) | 5 | N | N | N | N | N | N | N | N | N | 5 |
| Stark (39151) | 29 | 8 | 4 | 4 | 5 | 4 | N | N | N | N | 4 |
| Summit (39153) | 75 | 17 | 8 | 11 | 15 | 13 | 7 | N | N | N | 4 |
| Trumbull (39155) | 8 | N | N | N | N | N | N | N | N | N | 8 |
| Tuscarawas (39157) | 25 | N | N | 6 | 5 | 3 | 6 | N | N | N | 5 |
| Wayne (39169) | 13 | N | N | N | 4 | N | 3 | N | N | N | 6 |
| **PIC-18 sum of published cells** | **401** | 65+N | 30+N | 46+N | 74+N | 61+N | 46+N | 3+N | 0+N | 0+N | 76 |

`+N` in the sum row marks a class where at least one county cell is `N`, so the figure is a published-cells-only lower bound.



### Reading the tables

- **National (measured):** of 11,392 NAICS 326 employer establishments, **45.2% (5,145) have fewer than 20 employees**, 35.5% (4,043) have 20-99, and 19.3% (2,204) have 100 or more. Every national cell is published, so these are exact for CBP. The 3261 (plastics products) mix is close to 326; 3262 (rubber products) and especially 3259 (other chemical products, 61.5% under 20) skew smaller.
- **Top-15 gap states (measured):** the under-20 share runs from 31.4% (IN) to 66.5% (FL); CA is 58.3%, TX 48.7%, MI 38.8%. `N` cells in a state are few (1 to 3 establishments in `N` cells in the seven states that have any among these 15), so their bounds are narrow. These bands describe CBP's establishment frame in each state, not Atlas coverage.
- **PIC-18:** see Tables 4 and 4b for the 18-county totals and suppression bounds. Suppressed cells remain unknown; these are establishment counts, never organization counts.
- A share of *establishments* is not a share of employment, output or emissions. Employment is noise-infused in CBP and was not used here.
- CBP's under-20 count is probably not an upper estimate of the population of small shops: the methodology says undercoverage is concentrated in multi-unit companies and very small employers, and Census has no estimate of it. Direction and size of any bias in the shares are not measured here.

## What this implies for sourcing (reasoning, not measurement)

Everything in this section is inference from the program rules named, applied to the CBP shape above. **No source coverage, hit rate or overlap was measured**: this repo has no per-source establishment-size data, and CBP carries no facility identity, so none of this can be matched to a plant. Check each program rule against its current published text before relying on it.

| Source | Plausible size reach | Reasoning |
|---|---|---|
| **TRI** (EPA Toxics Release Inventory) | Mostly the 100+ band, some of 20-99; little or none of <20 | TRI covers manufacturing facilities with 10 or more full-time-equivalent employees that manufacture or process above the statutory chemical thresholds (commonly 25,000 lb per chemical) or otherwise use above 10,000 lb. Plastics molders and converters buying resin often fall below a chemical threshold even when large. Resin and chemical makers (3252, 3259) are more likely to file than molders (3261). Band 100+ is 19.3% of national 326 establishments, so even full TRI reach leaves most of the 326 frame untouched. |
| **OSHA ITA** (Injury Tracking Application, Form 300A) | Up to the 20+ bands (about 54.8% of national 326 establishments: 35.5% + 19.3%) as a ceiling; nothing in <20 | Electronic submission applies to establishments with 250+ employees in industries that must keep OSHA records and to establishments with 20-249 employees in designated higher-hazard industries (an NAICS list in the rule's appendix). Whether each of 3261, 3262, 3252 and 3259 is on that list was not checked here, and non-filing reduces real reach below the ceiling. OSHA's "employees" are annual-average style counts, CBP's size is mid-March paid employment, so band edges do not align exactly. |
| **State manufacturer directories** | Plausibly spans all bands, including <20 | State and regional industrial directories usually aim at all manufacturers and list a size or employee range, which is the one source type here that could plausibly reach the 45.2% under 20. Completeness and freshness vary by state and were not tested. Licensed commercial directories remain discovery-only under AGENTS.md section 5; only the underlying primary or public source may be cited. |
| **Association rosters** (PIC, state plastics associations, trade groups) | Skewed to mid-size and large members; thin on <20 | Membership rosters reflect who joins and pays dues, which tends toward larger firms with multiple plants. A roster is a discovery lead and, per AGENTS.md section 4, a roster category never supports a scope claim by itself; PIC membership publishes only as section 5.1 allows. |
| **Other routes for <20** | Needed to reach the largest single band | Candidates to evaluate, none tested here: state business-registry and tax-registration filings, municipal or county economic-development company lists, SAM.gov registrations, supplier and customer lists on company sites, and trade-show exhibitor lists. Each needs primary-source verification and the evidence contract (AGENTS.md section 4) before a record is created, and small shops will mostly be Tier U or C. |

Takeaways for the owner, as reasoning only:

1. TRI plus ITA, even if each worked perfectly, can only address establishments with roughly 10 or 20 and more employees. CBP says that is about 55% of national NAICS 326 establishments. The remaining roughly 45% are the part only directories, registries and local lists can find.
2. The gap states differ by about a factor of two in small-shop share (IN 31.4% to FL 66.5%), so the right source mix is state-specific: the large-plant programs go further in IN, NC, GA, SC and TN than in FL, CA and NY.
3. If PIC-18 reporting needs a small-shop count, CBP county cells for the smaller counties are mostly `N`; a county-level small-shop denominator would need a different source or an owner ruling on how to treat that gap. Per AGENTS.md section 9 this is an owner scope question and is not decided here.
