# OSHA inspections polymer-establishment spine - 2026-11-01

**Status: lead and proposal product, not Atlas data.** Nothing here edits `data/`, allocates an ID, sets a tier or changes a status. Built by `scripts/build_osha_inspections.py` (stdlib; re-runnable; shares the Atlas loader and match ladder of `scripts/build_echo_spine.py`). Packet lane output: the integrator of record decides what, if anything, is applied. `est_key` values are local row keys (hash of the aggregation key), not Atlas IDs.

## 1. Route, filters, raw counts

- **Route:** DOL Open Data Portal v4, dataset OSHA / Inspection (catalog id 10334; found in the 45-dataset catalog noted in `ROUTE_REPORT.md`). Endpoint: `https://apiprod.dol.gov/v4/get/OSHA/inspection/json?<params>&X-API-KEY=<KEY>`. The key (free DOL portal key, `DOL_API_KEY`) works only as a query parameter (header form returns 401); it is read from the environment, never written to any repo file, log or cache filename. Cache = one file per page named by the SHA-256 of the key-stripped URL, kept outside the repo (`/tmp/claude-0/osha_dol/cache`), so the run can be replayed without a key.
- **Metadata:** `.../json/metadata?X-API-KEY=<KEY>` lists 36 fields. Used: `activity_nr`, `estab_name`, `site_address`, `site_city`, `site_state`, `site_zip`, `owner_type`, `sic_code`, `naics_code`, `insp_type`, `nr_in_estab` (dictionary: "Number of employees in establishment", varchar, 0 <= N), `open_date`, `close_case_date`. `naics_code` and `open_date` are filterable server-side.
- **Filter (server side, per NAICS family, sequential):** `filter_object` = `naics_code like '<family>%'` AND `open_date gte 2019-01-01`, for families 3252, 3255, 3259, 326; paging `limit=1000`, `offset`, `sort_by=activity_nr&sort=asc` (stable order), 0.4s pause between requests; 10 pages in total (the first live run fetched all of them with no rate limiting or error responses; a 429 would stop the run, and re-runs replay from the key-free cache).
- **Date re-check (local):** 0 rows fell outside the window and were dropped; 0 duplicate `activity_nr` rows dropped.
- **Raw result:** **9,166 inspections** (unit: OSHA inspection records, one `activity_nr` each; opened 2019-01-01 or later; NAICS under 3252/3255/3259/326). By family: 3252: 865; 3255: 666; 3259: 907; 326: 6,728.
- By 4-digit NAICS prefix (inspection counts): 3252: 865; 3255: 666; 3259: 907; 3261: 5,696; 3262: 1,032.
- By `owner_type` (A private, B local govt, C state govt, D federal): A: 9,152; D: 12; B: 2. Not filtered; government-owned establishments are included as inspected.

## 2. Establishments

Aggregation key = normalized name (numeric `160609 - ` style prefixes stripped; Inc/LLC/Corp/The removed) + normalized street (suffix and direction canonicalized; unit/suite removed; falls back to city when no street) + state + zip5. **6,473 establishments** (unit: distinct aggregation keys, state + name + address) across **9,166 inspections** (reconciles to section 1: 9,166 raw minus 0 out of window). Establishments in 51 states/territories (0 with a blank state). One physical address can appear as more than one establishment when OSHA recorded different names there (rebrand, co-tenant, name typo); that is left visible, not merged.

Establishments by state (unit: establishments; inspections in parentheses), top 15 by establishment count: OH 492 (757); TX 474 (623); PA 432 (618); MI 395 (636); CA 369 (455); IL 288 (410); GA 278 (370); MN 277 (397); NC 251 (346); IN 220 (264); WI 217 (318); MA 204 (267); TN 193 (310); FL 179 (225); NY 160 (223). All states: `leads_by_state.csv`.

Latest-inspection year (unit: establishments): 2019 810; 2020 480; 2021 650; 2022 749; 2023 931; 2024 980; 2025 1,012; 2026 861.

## 3. Match to Atlas sites

Atlas side: 5,773 site rows (all shards, any status/tier); a usable street key exists for 5,223 (90.5%) - from the `street_address` column where filled, otherwise a heuristic read of `Street...:` phrases in `notes` (the Atlas often keeps the street in notes). Sites with no street key can match only on **name + zip/city**; those matches are labelled `name_zip_street_unknown` / `name_city_street_unknown` / `name_zip_weak` in `basis`. Ladder (identical to the ECHO spine; operator rule AGENTS 3): street exact + state + (zip5 or city) + name agreement = MATCH_SITE; street exact with a different name = POSSIBLE (co-tenant or successor operator); street unknown on either side + same zip5 + strong name = MATCH_SITE (moderate); same city + strong name, or weaker name, = POSSIBLE; ties at the top rank = POSSIBLE; both streets present but different is never a match. Coordinates are not used.

| Verdict | Establishments |
|---|---:|
| MATCH_SITE | 971 |
| POSSIBLE | 246 |
| NO_MATCH | 5,256 |
| **Total** | **6,473** |

**Match rate (unit: OSHA establishments matched to an Atlas site row):** MATCH_SITE = 971 of 6,473 (**15.0%**); MATCH_SITE + POSSIBLE = 18.8%. This is an establishment-to-site match rate, **not Atlas coverage**: OSHA lists inspected establishments only (programmed and unprogrammed), and the Atlas holds sites for which no inspection occurred since 2019-01-01.

MATCH_SITE by basis: `street_exact+loc+name` 937; `name_zip_street_unknown` 34. POSSIBLE by best basis: `street_exact+loc_name_differs` 144; `name_city_street_unknown` 50; `name_zip_weak` 23; `street_exact_locality_differs` 23; `street_exact+loc+name` 6.

Distinct Atlas sites reached by at least one MATCH_SITE establishment: 895 (unit: site rows); 70 of them are reached by more than one OSHA establishment key (name variants at one address).

## 4. Employee-band proposals (`band_proposals.csv`)

`nr_in_estab` is OSHA's recorded number of employees in the establishment at inspection (an OSHA-recorded figure, source class `government_filing`). It supports an `employee_band_site` **proposal** for **MATCH_SITE rows only**, at **site grain only** - never pushed to the organization or to other sites of the org (SCHEMA 4.5: never allocate parent headcount pro-rata; SCHEMA 4.4: band only, never a precise headcount stored as fact). Basis text per row: `OSHA inspection <activity_nr> opened <date>: nr_in_estab N → band`; `employee_count_source_date` = that inspection's open date. The value used is the most recent inspection of the establishment that carries a non-zero `nr_in_estab` (`latest_inspection_has_nr` says whether that is also the latest inspection). Zero or blank `nr_in_estab` is treated as missing, not as a count.

- Establishments with a usable `nr_in_estab` (unit: establishments): 6,246 of 6,473; by band: 1-9 658; 10-49 2,085; 50-99 1,277; 100-249 1,431; 250-499 479; 500-999 184; 1000-4999 114; 5000+ 18.
- **Band proposals: 889** (unit: Atlas site rows; one per matched site, using the latest valid value among its matched establishment keys). MATCH_SITE sites without any usable `nr_in_estab`: 6.
- Relation to the site's current `employee_band_site`: fills_blank 873; conflicts_existing 8; matches_existing 4; existing_nonstandard_value 2; fills_unknown 2.
- Proposed bands: 1-9 15; 10-49 216; 50-99 188; 100-249 276; 250-499 123; 500-999 46; 1000-4999 19; 5000+ 6.
- Band stability across all of a site's inspections that carry a value: same band every time 785; varies 104. The value is from the latest inspection with a count; it is 2.8 years old at the median (range 0.0 to 7.8). The latest inspection itself carries the count for 888 of the proposals.
- Rows with `relation_to_current = conflicts_existing` or `band_stable = N` deserve integrator review before any apply; `fills_unknown` / `fills_blank` rows are the straightforward ones. Existing site values outside the SCHEMA 4.4 vocabulary (e.g. `100-199`) are flagged `existing_nonstandard_value` and never overwritten by this packet.

## 5. Liveness (activity signal only)

`latest_inspection` is the open date of the establishment's most recent OSHA inspection in the window. It is an **activity signal only**: it shows OSHA inspected that establishment on that date, i.e. it existed and operated enough to be inspected. It is never a status change (AGENTS 3: status changes need dated primary evidence), and the **absence** of an inspection is nothing - most plants are never inspected in a given year, and a failed or empty fetch is never evidence of closure. Of 6,473 establishments, 2,978 have a latest inspection within 3 years of 2026-11-01; of 971 MATCH_SITE establishments, 495 do. **0 MATCH_SITE establishments** map to an Atlas site recorded as closed/idled, and 2 POSSIBLE establishments point at a closed/idled site (`liveness_note` in `site_matches.csv`): re-verification leads for the integrator, not a status change either way (an inspection at a possibly different operator of the same address does not show the recorded operator is active).

## 6. NO_MATCH leads by state, sorted by QCEW gap

NO_MATCH = no Atlas site candidate cleared the ladder. It is a **lead, not a finding of absence** (name or street form may differ). `lead_class`: `NET_NEW_LEAD` (no Atlas org with this normalized name), `NAME_EQUALS_HELD_ORG_OTHER_LOCATION` (likely another site of a held org; AGENTS 3 steps 2/4), `HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS` (strongly similar name at another street in the same city/zip). **5,256 NO_MATCH establishments** (unit: OSHA establishments): 3,987 NET_NEW_LEAD, 660 NAME_EQUALS_HELD_ORG_OTHER_LOCATION, 385 HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS; 2,381 have a latest inspection within 3 years.

Sort key = QCEW gap per `docs/denominators/README.md`: QCEW 2023 private establishments, NAICS 326, minus Atlas strict 326 sites (`operating_status` active/unknown, tier A-C, `naics_primary` starts 326), recomputed from `data/sites_*.csv` at run time. The gap is a count difference, not a matched-facility coverage figure, and the NO_MATCH pool per state is **not** an estimate of it (OSHA lists inspected establishments over four NAICS families, QCEW counts 326 reporting units). Top 20 by gap:

| Gap rank | State | QCEW gap (326) | OSHA establishments | MATCH_SITE | NO_MATCH | NO_MATCH, inspected within 3y | of which NET_NEW_LEAD |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | CA | 1,267 | 369 | 25 | 341 | 131 | 288 |
| 2 | TX | 869 | 474 | 39 | 416 | 153 | 310 |
| 3 | FL | 775 | 179 | 15 | 163 | 83 | 137 |
| 4 | MI | 772 | 395 | 40 | 352 | 169 | 285 |
| 5 | IL | 755 | 288 | 22 | 265 | 110 | 208 |
| 6 | GA | 446 | 278 | 18 | 257 | 112 | 191 |
| 7 | IN | 430 | 220 | 27 | 187 | 94 | 137 |
| 8 | WI | 408 | 217 | 30 | 181 | 82 | 133 |
| 9 | NY | 387 | 160 | 14 | 144 | 77 | 117 |
| 10 | NC | 382 | 251 | 46 | 191 | 77 | 140 |
| 11 | SC | 357 | 99 | 16 | 77 | 40 | 62 |
| 12 | NJ | 355 | 155 | 11 | 144 | 71 | 112 |
| 13 | TN | 350 | 193 | 24 | 167 | 80 | 135 |
| 14 | MN | 349 | 277 | 10 | 261 | 158 | 216 |
| 15 | MO | 331 | 120 | 19 | 97 | 26 | 77 |
| 16 | KY | 260 | 139 | 21 | 117 | 55 | 78 |
| 17 | PA | 246 | 432 | 185 | 200 | 104 | 111 |
| 18 | MA | 221 | 204 | 17 | 183 | 100 | 154 |
| 19 | AL | 219 | 104 | 12 | 86 | 29 | 56 |
| 20 | VA | 213 | 138 | 21 | 113 | 42 | 82 |

Full table (every state with OSHA establishments, gap-sorted): `leads_by_state.csv`; the individual NO_MATCH establishments with `lead_class` are the `verdict = NO_MATCH` rows of `site_matches.csv`.

## 7. Caveats (binding on any reader)

- **OSHA NAICS is inspector-recorded**, assigned by the compliance officer at the inspection (the dataset also carries a legacy `sic_code`); it can be wrong, stale or coarse. It is a `government_filing` value for the inspected establishment at best, never a company fact, never a ring decision, and never overwrites a site NAICS with its own source (SCHEMA 2.1, AGENTS 4). `naics_all` shows every code seen at one establishment.
- **Addresses are site addresses** (the inspected worksite), not a mailing or HQ address; some are free-text descriptions ("APPROX. 1/2 mile ...") that yield no street key, and construction-style or multi-site entries exist. Mailing fields were not used.
- **Inspected does not mean in scope.** The NAICS filter catches plastics, rubber, resin and chemical-product establishments, but also coded-in neighbours (e.g. 325920 explosives, which SCHEMA 2.2 marks exclude-by-default, and other 3259 codes that 2.2 lists as secondary or not at all) and mis-coded establishments. Every NO_MATCH row is a lead needing ring/scope adjudication - an owner-ruling-adjacent question this lane does not settle (AGENTS 2.9).
- **Leads only.** No row is a verdict in the AGENTS 2.8 grammar (not VERIFIED, REJECT, STILL_UNCERTAIN or DUPLICATE_OF); they are match candidates and band proposals for the integrator.
- **`nr_in_estab`** is an inspection-time figure of uncertain definition (establishment or inspected portion; often rounded, sometimes carried over between inspections). It is a band input with a date, not a headcount; see `nr_age_years` and `band_stable`.
- **Window and coverage.** Only inspections opened 2019-01-01 or later; OSHA inspection records include state-plan states' data as loaded by DOL; completeness of the DOL extract by state was not verified. An establishment inspected before 2019 only is outside this file, and that is not evidence of anything.
- **Counts name their unit:** inspections = records; establishments = aggregation keys (not facilities, not companies, not Atlas sites).

## 8. Reproduce

```
set -a; . /root/.config/polymer-atlas/api_keys.env; set +a   # DOL_API_KEY from the environment only
python3 scripts/build_osha_inspections.py --as-of 2026-11-01
# first-page probe (key shown as <KEY>):
#   https://apiprod.dol.gov/v4/get/OSHA/inspection/json?limit=1&X-API-KEY=<KEY>
```
