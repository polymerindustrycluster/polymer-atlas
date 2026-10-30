# F4 — pass-20–25 coordinates reference packet

Pinned main: `eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05` (2026-10-30).
Draft PR #11. No canonical data edits, ID allocation, tier changes, county changes,
evidence rows or inclusion-log decisions. **Coordinates are reference data only.**

## Results and population boundary

Exactly **1,517 site rows created in passes 20–25** receive one disposition:

| Disposition | Site rows |
|---|---:|
| Reference match, strict address comparison passed | 935 |
| No match | 228 |
| Non-exact provider match, held | 246 |
| Exact provider match but stricter address comparison failed, held | 57 |
| Multiple candidates / tie, held | 10 |
| Existing coordinates, not overwritten | 1 |
| No recorded street address | 15 |
| Partial/unnumbered/intersection address | 25 |
| **Total** | **1,517** |

The **935** proposed pairs are `address_interpolated`, never rooftop or parcel.
**582** held rows contain no proposed coordinates. Provider availability is not
an establishment verdict. No failed HTTP request or missing response occurred.

The queue's `SITE-003399+` shorthand overselects **2,563** rows. Actual population
is `SITE-004446`–`SITE-005962`, proved independently by (a) `created_by` pass 20–25
and (b) the ID-set difference from the parent of the first pass-20 commit.
Pass counts: 20=177, 21=282, 22=273, 23=280, 24=251, 25=254.

**Cohort wording is an integrator review item:** 1,342 rows explicitly say
`TRI national wave` in current notes (831 accepted reference pairs); 175 other
pass-20–25 creations (104 accepted pairs) include SC/Q01–Q02 records and rewritten
notes. Absence of that note string is not proof a site was outside TRI. This
packet does not assert that all 1,517 are TRI-verified. Both strata are explicit.
No records outside the 1,517-row population are included.

## Public provider, access and privacy

The [official Census API documentation](https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html)
(accessed 2026-10-30, page last updated 02/2026) expressly describes public use,
CSV file batch submission and a 10,000-record limit. The
[Census documentation page](https://www.census.gov/programs-surveys/geography/technical-documentation/complete-technical-documentation/census-geocoder.html)
describes interpolation along TIGER address ranges. One batch of **1,476**
recorded business addresses was submitted; no key, login, payment, persistent
access, parallel scraping or access-control bypass. Only existing Atlas business
site addresses were used, with no personal-contact fields. No external address
enrichment or private records were consulted. The eligibility gate holds explicit
residential/home-address indications; this is not an independent occupancy audit.

Request: `geographies/addressbatch`, benchmark `4` (`Public_AR_Current`), vintage
`4` (`Current_Current`). Request and response retrieved **2026-10-30**;
server response date **21:35:59 UTC**, HTTP 200, 251,295 raw CSV bytes.
`benchmarks.json` and `vintages.json` bank available choices. Current benchmarks
are mutable: replay may differ later; the raw response is the reproducible record.
Response headers are retained with the transient cookie omitted.

## Safeguards

- Recorded street/city/state/ZIP submitted unchanged; no invented structure number.
- Missing street, unnumbered road, intersection, kilometer and PO-box formats held.
  Wisconsin grid numbers and spelled `ONE` are eligible structure numbers.
- Full ID parity: 1,476 unique request IDs = 1,476 unique response IDs.
- Only provider `Match` + `Exact` can qualify. `Non_Exact`, `Tie`, `No_Match` held.
- Additionally compare street, city, state and supplied ZIP, allowing only case,
  punctuation, common street suffix/direction abbreviations and ONE/1. Different
  house number, road, city, state or ZIP is held. The 57 comparison holds are
  54 street and 3 city differences; conservative false holds are intentional.
- Coordinates are parsed as **longitude,latitude** from Census then emitted as
  `lat,lng`; numeric bounds/signs checked. Source and precision accompany every
  accepted pair. Held pairs are blank; raw candidates remain in response.csv.
- This confirms an address-range match, not the business operator, current activity,
  site boundary, entrance, parcel or rooftop. No evidence/tier inference is made.
- `accepted-review-sample.csv` exposes 20 accepted rows: 12 deterministic random
  rows (seed 20261030) plus 8 address-edge examples, including a Wisconsin grid
  number and highway addresses. Street/locality comparisons were inspected.

## County conflict candidates — report, never correct

The geocoder's FIPS values are compared to recorded county names using the
[official 2020 county-code reference](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt)
(retrieved 2026-10-30). This is a **screen**, not county adjudication: the code list
and geocoder geography vintage may differ. Cosmetic punctuation, diacritics,
county suffixes and `(independent city)` spelling normalize; city and county remain
distinct. 1,232 match results agree by name, 1 has a blank recorded county,
279 rows are not assessed, and these 5 require review:

| Site | Recorded county | Geocoder reference county | Coordinate disposition |
|---|---|---|---|
| SITE-004476 | Florence | Williamsburg County | held non-exact |
| SITE-004770 | DODGE | Washington County | reference match |
| SITE-005532 | Palo Pinto | Parker County | reference match |
| SITE-005536 | Baltimore | Baltimore city | reference match |
| SITE-005731 | Herkimer | Fulton County | held non-exact |

These are not established field errors. **Do not use this packet as a county source
or correction.** Even accepted coordinate pairs do not resolve county conflicts.
Seek authoritative address-specific parcel/jurisdiction evidence separately.

## Files and reproduction

`population.csv`: all site IDs, input addresses, cohort, creation pass, input hold,
existing coordinates and canonical-row SHA-256 (computed before packet metadata assembly).
`request.csv`: exact headerless public request. `response.csv`: full raw response.
`coordinates-packet.csv`: one disposition per site, proposed lat/lng/precision,
source, comparison detail, county conflict screen and settling facts for holds.
`manifest.json`: pin, cohort proof, input digests, SHA-256 of every canonical file.
`summary.json`: output reconciliation and raw-response digest.

Large CSV/source artifacts are stored as bounded base64 transport parts (not new
state claims or changed analytical strata). `transport-manifest.json` fixes each
part order, byte count and SHA-256. Run `reconstruct.py` first; it recreates files in `build/f4-reviewed/` (or a supplied scratch directory),
retaining the exact independently reviewed bytes and refuses to overwrite differing bytes.
This packaging avoids the connector's stalled large-blob request. All 1,517 rows,
1,476 raw responses and canonical fingerprints are retained.

From repository root, offline reproducibility:

```sh
python3 docs/reviews/f4-coordinates-2026-10-30/reconstruct.py
python3 build/f4-reviewed/prepare.py
python3 build/f4-reviewed/process.py
python3 -m unittest discover -s build/f4-reviewed -p 'test_*.py'
python3 scripts/validate.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

To intentionally retrieve a fresh response (do not replace this banked evidence):

```sh
curl --fail-with-body --max-time 600 \
 --form addressFile=@build/f4-reviewed/request.csv \
 --form benchmark=4 --form vintage=4 \
 https://geocoding.geo.census.gov/geocoder/geographies/addressbatch \
 --output /tmp/f4-new-response.csv
```

## Verification and handoff

Canonical validator passes on the exact packet tree: 4,179 organization rows,
5,770 site rows checked. **6 packet-specific tests pass** (coverage, response parity,
held-coordinate exclusions, coordinate bounds/signs/source/precision, strict address
negative cases, county semantics and every canonical file fingerprint);
**37 existing regression tests pass**. `git diff <pin> -- data/` is empty.
Main rechecked at 21:37 UTC: still the pinned SHA; no drift absorbed.

Integrator must recheck current site identity/address and all data fingerprints
before applying anything; pair coordinates with `address_interpolated`, mapping
packet `lat/lng` to schema `latitude/longitude`. Never apply held rows, raw candidate
coordinates, county values, tiers or evidence changes. This draft requires independent
review and integrator action; it is not a canonical application or merge request.
