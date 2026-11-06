# T2 bulk federal cache — atlas-T2-bulk-federal

Acceptance criteria (written before implementation): official national ECHO CSV,
SEC submissions archive and ticker JSON, GLEIF LEI and relationship Golden Copy
CSV archives download outside the repository; atomic verified indexes expose local
lookups; manifests include URL, retrieval date, bytes, SHA-256 and reconciled row
counts. Failures must preserve an existing index and never become empty successes.
Census helper enforces 1–10,000 uniquely keyed business addresses and reconciles
response IDs. Known-answer and injected-defect checks cover every source.
No canonical Atlas rows change (0 organizations, 0 sites, 0 evidence rows at any tier).
First users: campaign research lanes, 2026-11-06; non-use finding date: 2026-11-07.

## Source terms checked 2026-11-06

- [EPA disclaimers](https://www.epa.gov/web-policies-and-procedures/epa-disclaimers):
  “Individual documents on the EPA website may have different copyright conditions”.
  [ECHO download page](https://echo.epa.gov/tools/data-downloads) explicitly offers
  the national Exporter download; it is the task's permitted alternative to separate
  FRS facility/NAICS/program tables. It covers regulated facilities, not all FRS.
- [SEC fair access](https://www.sec.gov/about/developer-resources):
  “no more than 10 requests per second”. [SEC FAQ](https://www.sec.gov/about/webmaster-frequently-asked-questions)
  requires a declared User-Agent with contact. The CLI requires an explicit contact
  email; sequential bulk requests avoid per-entity crawling. [Official API docs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
  link the bulk archive on **www.sec.gov**, not data.sec.gov. company_tickers.json
  likewise lives on www.sec.gov/files/. These official locations govern the URLs.
- [GLEIF terms](https://www.gleif.org/en/meta/lei-data-terms-of-use):
  “The data available through the Access Service are provided under the CC0 licence”.
  Use the complete Golden Copy CSVs (LEI-CDF and RR-CDF), not deltas. The live
  metadata endpoint supplies each release URL, compressed size and record count.
- [Census batch API](https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html):
  “There is currently an upper limit of 10,000 records per batch file.”
  Coordinates are interpolated reference data, never verification evidence.

## Reuse and boundaries

Reuses `scripts/build_echo_spine.py`'s `squash` normalizer and its established
ECHO_EXPORTER.csv mapping. Inspected tasks/echo-frs-spine-2026-11-01 (report and
CSV packets), tasks/form5500-spine-2026-11-01, and tasks/registry-links-2026-11-02.
Those are filtered research/matching products, not reusable national cache writers;
Form 5500 remains separate. Exact normalized name/city lookup returns all candidates;
it never resolves parent/operator identity or assigns status, scope or tiers.

## Use

```sh
python3 tasks/bulk-federal-2026-11-06/build.py --contact 'YOUR_REAL_CONTACT_EMAIL'
# Select a subset with --sources frs, or --sources lei rr; --cache-dir overrides default.
uv run --with pytest python3 -m pytest -q scripts/test_bulk_sources.py
```

Default cache: `/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/cache/bulk`.
The same CLI rebuilds a snapshot without appending duplicate records. Downloads
are content-addressed; previous snapshots remain available to previous indexes.
Allow tens of GB of disk for archives and indexes; no archives are extracted.
SQLite is built in a temporary file and atomically replaces each source index.
There is one writer per cache; lanes use read-only lookup connections.

```python
from scripts.bulk_sources import (
    frs_by_registry_id, frs_by_name_city, sec_by_ticker, sec_by_cik,
    lei_by_name, lei_by_lei, lei_relationships, census_batch,
)
frs_by_registry_id('110007881596')  # list of complete ECHO CSV rows
sec_by_cik('0000320193')           # full submissions object or None
sec_by_ticker('AAPL')              # list of full submissions objects
lei_by_lei('HWUPKR0MPOU8FGXBT394') # list of complete LEI-CDF rows
census_batch([['1', '4600 Silver Hill Rd', 'Washington', 'DC', '20233']])
```

All lookup functions accept `cache=`; Census uses its public batch service. Name lookups normalize punctuation,
case and whitespace using the existing spine normalizer, not fuzzy identity rules.
Missing indexes raise; absent keys in an installed snapshot return empty results.
SEC historical submission JSON members are validated and counted but not indexed
as extra issuers; full current filing arrays remain in the archive. Relationship
lookups return outgoing child→parent rows without interpreting their validity.
Blank FRS IDs are retained/countable; they are never minted as registry links.
Manifests are embedded in each SQLite database (authoritative), with a combined
`manifest.json` convenience export. SHA-256 is a locally observed digest, not an
upstream authenticity signature. ZIP CRC plus HTTPS and byte counts check transfer
integrity. Each CSV is independently reread and reconciled against SQLite yield;
GLEIF additionally reconciles against its published per-release record_count.
SEC reconciles issuer + historical counts against archive member count. ECHO and
SEC do not publish an exact row total in the files: no invented upstream total.

## Known-answer checks

Offline fixtures test three ECHO facility ID/name/city pairs from the independent
held spine (Star Plastics Ravenswood, Armacell Spencer, Delrin Washington), three
SEC issuer CIK/ticker pairs (Apple, Microsoft, Tesla), Apple LEI/name and the Google→Alphabet direct-parent
RR pair independently checked against GLEIF. The Census fixture checks the business address
of Census headquarters and the multipart request/response contract. These establish
parser behavior, not a live response; live verification results are recorded below.

## Live verification

2026-11-06: Census headquarters address returned Match / Exact, longitude
-76.92836638093, latitude 38.84505589808 (business address; no personal data).
The helper sent one input row and received the same one ID.

Census's [general API terms](https://www.census.gov/data/developers/about/terms-of-service.html)
also state: “You may use the Census Bureau API to develop a service”. The batch
service's own documentation supplies its distinct request parameters and limits.

Named live gate: `python3 tasks/bulk-federal-2026-11-06/check.py`. It requires all five installed snapshots, rehashes raw files and checks known answers; missing sources fail.

The independent live [GLEIF Apple record](https://api.gleif.org/api/v1/lei-records/HWUPKR0MPOU8FGXBT394)
confirmed `HWUPKR0MPOU8FGXBT394` → `Apple Inc.` on 2026-11-06.

The live gate checks three LEIs (Apple, Google LLC, Alphabet Inc.) and the
[Google→Alphabet direct-parent relationship](https://api.gleif.org/api/v1/lei-records/7ZW8QJWVPR4P1J1KQY45/direct-parent-relationship),
independently fetched 2026-11-06: child `7ZW8QJWVPR4P1J1KQY45`, parent
`5493006MHB84DD0ZWV18`, type `IS_DIRECTLY_CONSOLIDATED_BY`.

Full-file exercise found that GLEIF's 338-column rows expand to roughly 77 GiB of
repeated JSON keys before SQLite overhead. The first temporary LEI build was
stopped before publication. Payloads now use stdlib zlib compression per row;
lookups return the identical dictionaries. Existing plain-JSON cache indexes remain
readable. Raw archives are retained. This is a storage correction, not a filter:
all rows and fields remain, and the same count/known-answer gates apply.

The official SEC ZIP contains one non-data member, `placeholder.txt`, whose exact
bytes are `Placeholder file`. The importer explicitly validates and reports it in
`auxiliary_members`; it is not a JSON issuer/history row. Every other member must
match the CIK JSON grammar. `archive_members = row_count + len(auxiliary_members)`
records the complete archive accounting; unknown files still fail the build.

## Review dispositions

Codex clerk-6 REFUTE on `aede40e`: (1) a history-only SEC ZIP could replace a
populated issuer index with zero indexed issuers; (2) duplicate ticker JSON keys
could collapse before both counts. Fixed: require positive indexed yield before
publication; reject duplicate keys in external JSON objects before indexing.
Regression `test_history_only_and_duplicate_json_preserve_cache` proves both
failures preserve existing Apple results. Targeted suite: 10 passed.
