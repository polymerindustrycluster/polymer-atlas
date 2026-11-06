# Refute brief — S6 data.gov federal source scout (packet only)

Branch `agent/claude-code/source-scout-6`. Folder `tasks/source-scout-6-2026-11-06/`. No `data/`, `scripts/`, `docs/` or `tasks/QUEUE.md` change. Try to REFUTE; list what holds up.

## What was done
Five federal routes measured, each with a 20-unit seeded sample (seed 20261106, `random.Random.sample` over the frame sorted by its unique key):
FDA registration/listing (US facility, active, Manufacturer/Contract Manufacturer, polymer-named product codes), NREL FIED 2017 (primary NAICS 3252/3255/326), ITA FTZ production authority (HTSUS ch.39/40 finished products), DOL OFLC LCA FY2025 (employer NAICS 3252/326, Certified, US worksite), USAspending FY2025 contract recipients (award NAICS 3252/3261/3262).

## Re-run
`python3 -I tasks/source-scout-6-2026-11-06/check.py` (offline, recomputes every count/yield from the committed CSVs, re-draws each sample from its frame, runs known answers and injected defects).
Builders need the persist cache (`/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/source-scout-6/`); `fetch_routes.py` re-probes routes and re-checks the terms quotes raw.

## Where it could be wrong (attack these)
1. **Silent row loss.** DuckDB `read_xlsx` returned 118,580 of the DOL sheet's 563,689 `<row>` elements with no error. Independent XML count: 118,581 rows carry a value (header + 118,580), the rest are blank styled rows; openpyxl agrees. Check this reasoning.
2. **FDA address type.** `ADDRESS_TYPE_ID` F = facility, U = US agent of a foreign firm (person names). Frame uses F + country US + REG_STATUS_ID 1 only. Confirm no agent rows in `fda/frame.csv`.
3. **Product-code filter** is a keyword filter on device *names* (regex in `fda/build.py`), IVD panels excluded. Not a material class. Confirm the regex/known answers; say whether it should be wider/narrower.
4. **USAspending NAICS is the award's procurement code**, not the recipient's industry; frame is recipients with >=1 FY2025 contract award under 3252/3261/3262, US-located. The API rejects 3-digit NAICS (needs 2/4/6 digits), so 326 was expanded to 3261+3262.
5. **FTZ** database has company names only (no address). Frame = companies with >=1 approval listing a *Product* part in ch.39/40 across the 43 four-digit headings 3901-3926, 4001-4017. DUPLICATE_OF there is organization grain on exact normalized name.
6. **Own-site verification** (`verify.py`): VERIFIED needs, on ONE page of the entity's site, the entity name (leading <=3 tokens contiguous), the street address (Atlas street_key tokens contiguous) and a polymer word within 80 chars of a process word. Candidate URLs came from SearXNG/Bing searches (`seeds.csv` records the manually chosen ones). A bot-walled or search-missed site is an availability hold, never evidence of closure or absence. Check that no VERIFIED row is a false positive (open `verify_url`, check `verify_quote`).
7. **Dedupe**: registry link (FRS / UEI / FDA_FEI) first, then `atlas.dedupe` name/street/trade-name; DUPLICATE_OF only for a registry link or a singleton exact street+locality site. Check `site_hits`/`org_hits` columns for any miss you can find by hand.
8. **Personal data**: no worker, attorney, preparer, POC, phone or e-mail columns; `verify_quote` is a redacted address window. Check the CSVs.
9. Wilson intervals are for n=20 per route at *different grains* (facility, company, employer-worksite, UEI); they must not be pooled.

## Verdict requested
APPROVE or REFUTE (with the deciding fact), and any count you could not reproduce.
