# residual-hq2-a — 2026-11-06

Packet-only research for the 30 organization IDs in read-only `input.csv`.
`verdicts.csv` contains 6 proposed HQ_FOUND and 24 STILL_UNKNOWN verdicts;
`outcome` mirrors `verdict` for parent compatibility. All county fields are
empty: no county was inferred. Holds carry an explicit settling fact.

Proposed headquarters: ORG-004311 Jacuzzi Brands LLC (Chino Hills, CA);
ORG-004346 American Renolit Corporation (LaPorte, IN); ORG-004348 Amerityre
(Boulder City, NV); ORG-004350 Polymer Laboratories & Solutions / Poly Labs
(Lewiston, ME); ORG-004354 Armorock LLC (Henderson, NV); ORG-004383 Delivery
Concepts (Elkhart, IN). Two findings are exact-entity LEI registry headquarters;
the other four use own-site pages or an own-hosted certificate. The certificate
HQ label and address are two excerpts from the same PDF table row (separator
` || `), totaling under 25 words. All positive quotes were checked against
fresh curl response bytes, with HTML visible-text or pdftotext extraction.

Parent must independently re-fetch positives before integration. In particular,
Jacuzzi's registry has a 2026-04-13 update and gives Chino Hills; newer group and
privacy-office leads have other cities and were not substituted for the exact
entity's registry HQ. Armorock's registry gives Henderson, whereas third-party
plant/HQ leads mention Boulder City. These are reported registry observations,
not a claim that all conflicting location references have been resolved.
Poly Labs release is dated April 2022. The Renolit certificate was issued
2024-06-28 and expires 2027-08-06. Country US follows the explicit domestic
state/country context; headquarters cities and states are quoted, not inferred
from plant/contact locations. Merged Zodiac ORG-004322 is held without fetch:
tombstones remain in their original shard.

`receipts.json` records 52 curl attempts, URLs, raw SHA-256 and temporary cache
paths. `fetch_count` counts these actual page-fetch attempts (including failures),
not search-index discovery queries or HTTP redirect hops; maximum per entity is
3, below the cap of 6. Search snippets alone were never accepted as evidence.
Raw bytes and extracted text remain only in `/tmp/residual-hq2-a/`; no raw page,
email or personal contact details were copied into this packet. Failed or blocked
fetches were treated only as route availability failures. Known domains were
checked first, followed by cheap own about/contact/location pages and targeted
public-primary discovery. The local estate search was incomplete because the
Mac lacks the Windows Documents catalogues; that miss was not treated as absence.

Named runnable check:

```
PYTHONDONTWRITEBYTECODE=1 python3 tasks/residual-hq-2-2026-11-06/lanes/a/check.py
```

Result: PASS — 30 input/output organization IDs, exact coverage and uniqueness;
6 HQ_FOUND / 24 STILL_UNKNOWN; 52 raw SHA-256 receipts; max 3 fetches per entity;
all positive quote matches and 25-word limits; 3 known parser/source cases
(visible HQ markup, script-text exclusion, split HQ/address excerpts); missing
row, duplicate ID and fabricated-quote mutations rejected. Input SHA-256 is
recorded in receipts. This verifies packet integrity, not independent factual
approval; parent owns re-fetch, integration and completion reviews.

No data, queue, tracker, ID allocation, branch, commit or settings changes.
No private CRM used. No liveness, tier or status determination attempted.
