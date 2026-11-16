# Census geocode — atlas-w16-geo

Task claim: controller w1116 GEO brief; queue unchanged per contract. Integrator of record: atlas-w16-geo, exclusively coordinates in US site shards. First user: Atlas map maintainer, at PR review; non-use finding date 2026-11-23.

Acceptance criteria: every US street-address site in the pinned baseline receives exactly one Census geographies batch response; only Match/Exact fills blank coordinate fields; all other cells and all rows survive; three existing coordinate pairs return within 200 m; county differences and unsuccessful matches are held in packets. ZIP requires an owner ruling and remains held.

Source: https://geocoding.geo.census.gov/geocoder/geographies/addressbatch with Public_AR_Current / Current_Current. Discovery metadata in benchmarks.json and vintages.json. County FIPS labels: https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt (retained counties.txt). Coordinates are reference data under SCHEMA §4.5, never verification evidence. No tiers, last_verified dates, or sources are changed.

Reproduce: `python3 tasks/census-geocode-2026-11-16/fetch.py` resumes missing batches; `python3 tasks/census-geocode-2026-11-16/build.py` applies blanks idempotently; `python3 tasks/census-geocode-2026-11-16/check.py` checks the full pinned input and data diff, packets, every summary count, three known answers and three injected defects. Baseline commit: be2e6084d430f1e6f9de0f66289b1d3c2570e255. Known answers are the first three baseline rows with existing address_interpolated pairs, selected without examining their distances; a Non_Exact result can check coordinates but cannot authorize fills.

`proposals.csv` records each applied field; `holds.csv` records unsuccessful match holds; `county_mismatches.csv` records every Exact county difference, including blank recorded counties, with PIC-18 flags using scripts/regions.py. The flag considers either recorded or returned Ohio county. No county is edited. `OWNER_BATTERY.md` holds all ZIP fills pending a dated ruling. Raw input and response batches are retained; baseline.csv is a public frozen witness.

Proposed follow-ups: adjudicate county packet using site-specific parcel/physical-address sources; settle ZIP exemption. Existing coordinates can disagree with new Census interpolation and are preserved. The Census 2020 county-name reference may need adjudication where county boundaries/names have since changed.

## Results and checks

Frame: 5,631 US site rows with nonblank street_address (the brief counted 5,639; current pinned US-only frame excludes INTL). Of these, 2,504 lack a complete coordinate pair and 473 lack ZIP.

Applied: 1,208 site rows, each receiving latitude, longitude and address_interpolated precision. Changed-site verification tiers: {'C': 804, 'B': 366, 'A': 29, 'U': 9}; tiers unchanged. Exact: 3,999 site rows; held results: 831 Non_Exact, 774 No_Match, 27 Tie. County packet: 418 site rows (including blank recorded counties), zero PIC-18 flags. All ZIP fills held.

Checks passed: `python3 tasks/census-geocode-2026-11-16/check.py` (complete input/response yield, full data diff, every receipt count, three coordinate known answers within 200 m, missing response/duplicate frame/malformed coordinates rejected); `python3 scripts/validate.py` (0 errors); `python3 scripts/check_row_loss.py --base origin/main` (no row loss); `python3 scripts/export_vocab.py --check` (current). No shared scripts changed.
