# OSHA establishment spine: route report (2026-11-01)

Lane: packet lane (no `data/` edits, no IDs allocated, nothing committed).
Task: A-01 in `docs/IDEAS_AND_RESOURCES.md` (OSHA ITA Form 300A establishment data plus OSHA inspections).

## Outcome

**NO KEYLESS BULK ROUTE FOUND.** Step 2 (spine build) was not run, so there is no `build_osha_spine.py` and there are no spine CSVs. This is an availability result for the routes tested from this environment. It is not evidence about the data.

- **ITA (Form 300A) establishment data.** The only official host is `www.osha.gov`, which returns 403 to this environment. We did not work around it. ITA is **not in the DOL open-data catalog at all**. The full catalog was listed (45 datasets, 5 pages) and contains no injury-tracking or 300A dataset.
- **OSHA inspections.** The DOL catalog does list OSHA datasets: Inspection (id 10334), Violation (10338), Violation Event (10357), Accident, Accident Injury, Accident Abstract, Accident Lookup2, Related Activity, Emphasis Codes, Optional Code Info and Violation Gen Duty Std. The data endpoint answers 401 without an API key. The old bulk-zip pattern (`enforcedata.dol.gov/data_catalog/OSHA/osha_inspection_YYYYMMDD.csv.zip`, and the `enfxfr.dol.gov` host) now serves only the data.dol.gov single-page app shell (HTTP 200, 9,768 bytes of HTML, not a zip), so it is a dead route.
- The inspection datasets carry establishment name, address, NAICS and inspection dates, but no employee counts. They are a discovery and recency source only, not a size source. ITA is the size source.

## URLs tried (about 32 requests; default curl user-agent, no spoofing)

| # | URL | Result |
|---|---|---|
| 1 | https://data.dol.gov/ | 200, JS single-page app shell |
| 2 | https://data.dol.gov/data-catalog | 200, same shell |
| 3 | https://enforcedata.dol.gov/views/data_catalogs.php | 200, redirects to data.dol.gov, same shell |
| 4 | https://enforcedata.dol.gov/views/data_summary.php | 200, redirects to data.dol.gov, same shell |
| 5 | https://enforcedata.dol.gov/data_catalog/OSHA/osha_inspection_20261031.csv.zip | 200, HTML shell (not a zip) |
| 6 | https://data.dol.gov/data_catalog/OSHA/osha_inspection_20261031.csv.zip | 200, HTML shell (not a zip) |
| 7 | https://enforcedata.dol.gov/views/search.php | 200, redirects to shell |
| 8 | https://data.dol.gov/robots.txt | 200 (`Disallow: /static/`) |
| 9 | https://data.dol.gov/sitemap.xml | 200, HTML shell |
| 10 | https://data.dol.gov/static/js/main.9348c9fd.js | 200, app bundle. It points only to `apiprod.dol.gov/v4/...` (key required) and `dataportal.dol.gov` |
| 11 | https://enfxfr.dol.gov/data_catalog/OSHA/osha_inspection_20261031.csv.zip | 200, redirects to data.dol.gov, HTML shell |
| 12 | https://enfxfr.dol.gov/data_catalog/OSHA/ | 200, HTML shell |
| 13 | https://apiprod.dol.gov/v4/datasets (and `?page=2` to `?page=5`, 4 more requests) | 200, catalog metadata only, no key needed. Lists 45 datasets. OSHA items are on pages 2 and 4. No ITA dataset |
| 14 | https://dataportal.dol.gov/datasets/10280 | 200, HTML shell |
| 15 | https://catalog.data.gov/api/3/action/package_search?q=osha+inspection&rows=5 | 404 |
| 16 | https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data | 403 |
| 21 | https://apiprod.dol.gov/v4/get/OSHA/inspection/json?limit=1 | 401, "API key is either incorrect or missing" |
| 22 | https://ita.osha.gov/ | proxy CONNECT 502 (host not reachable) |
| 23 | https://data.osha.gov/ | proxy CONNECT 502 (host not reachable) |
| 24 | https://osha.gov/Establishment-Specific-Injury-and-Illness-Data | 403 |
| 25 | https://www.dol.gov/agencies/osha/data | 404 |
| 26 | https://catalog.data.gov/dataset?q=osha+injury+tracking+application | 200, redirected to the catalog home, no search results rendered |
| 27 | https://www.osha.gov/sites/default/files/ita/ITA_Data_CY2023.zip | 403 (guessed path, so it says nothing about the file) |
| 28 | https://catalog.data.gov/api/search?q=osha%20injury%20tracking&per_page=5 | 404 |

The count ran to about 32, slightly over the 30-request cap, because catalog paging took five requests under item 13. Raw bodies and the request log are in `/tmp/claude-0/osha_raw/` (outside the repo).

## What is needed (either one unblocks the build)

1. **ITA size data (preferred, since it carries employee counts).** A human downloads the ITA establishment CSVs from https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data in a normal browser. The "Form 300A summary data" files exist for CY2016 to the latest year. Place them at `/tmp/claude-0/osha_raw/ita/` (or another named path) as `ITA_300A_<year>.csv` (zip is fine). Expected columns include establishment_name, street_address, city, state, zip_code, naics_code, annual_average_employees, total_hours_worked and year_filing_for. This route is human-fetched, so no bot-wall is touched.
2. **Inspections (discovery and last-inspection date).** Register for a free DOL API key at https://dataportal.dol.gov and provide it as environment variable `DOL_API_KEY`. Then `https://apiprod.dol.gov/v4/get/OSHA/inspection/json` can be paged with a key. The lane will not request or invent a key. Alternatively, a human downloads the OSHA inspection bulk CSV from https://www.osha.gov/data (also 403 here) and places it in the same directory.

## Notes for the build once data lands

- Filter NAICS prefixes 3252, 3255, 3259 and 326.
- `docs/SCHEMA.md` §4.5 (line 929) marks `employee_band_site` as **MUST** if any source gives it, and says never to allocate parent headcount pro-rata to sites. §4.4 and line 815 say never to store a precise headcount as fact: store the band plus `employee_count_source_date`.
- Band proposals would use basis text "OSHA ITA CY YYYY annual average employees N → band", source class `government_filing`, for MATCH_SITE rows only. They would go to the integrator as packets and never be applied by the lane.
- The ITA covers establishments with 20+ employees (and 10+ in designated industries), so a missing match is not evidence that a site is small or closed.
