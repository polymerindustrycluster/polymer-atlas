# PIC-18 markets and certifications — batch 2, 2026-11-16

Claim: atlas-w16-markets-certs / batch 2, controller thr_9i2c6byhcz. Separate branch and PR from batch 1 (#344). Controller explicitly delegated integration of this batch under AGENTS §2.7. First user: Atlas owner for member prospecting; integration/review due in this wave, no adoption claimed and no issue closed.

## Frozen scope

Base: `25e6f7666c355e2cd1700635eaf4e4ff40e32941` (origin/main at batch creation). Frame: organizations whose **every retained corpus page has pass 2**, with blank markets_served or certifications at that base. The corpus manifest snapshot is retained at `persist/pic18-markets-certs-2/manifest.snapshot.csv` in controller storage. Its SHA256 is pinned in corpus.json and checked before frame construction. Later corpus growth cannot change this frame. Raw/text pages remain in the supplied `persist/pic18-corpus-2026-11-16/` directory.

The snapshot has 745 attempted organizations and 628 organizations with retained pages across both passes. The batch frame is **200 organizations / 893 retained pages**, including **790 direct HTML pages and 103 reader pages**. Initially blank cells: **153 market cells + 200 certification cells = 353 organization-field cells**. This excludes pass-1 organizations and pass-2 organizations with both target cells already populated.

## Applied result

**41 market values applied to 15 organizations / 15 market cells; one certification value applied to one organization / one certificate cell.** Total **16 distinct organizations / 16 cells / 42 append-only evidence rows**, unchanged tiers **A 5 / B 8 / C 3**. IDs **EVD-370070–370111**, within the reserved block. Organization yield: **16/200 = 8%**; no new batch inferred under CAMPAIGN's low-yield rule.

| Organization shard | Market cells | Certification cells | Total value rows | Matching evidence shard | New evidence rows |
|---|---:|---:|---:|---|---:|
| organizations_OH.csv | 15 | 1 | 42 | evidence_organizations_OH.csv | 42 |

**337 blank field cells remain held**, with named settling facts in holds.csv. These are unresolved field cells, not negative findings or 337 organizations. inputs.csv labels accepted values `applied`; holds.csv labels every unresolved cell `held`. Every initially blank cell is covered exactly once. No creates, dedupe-create or inclusion-log edits; no sources, notes, last_verified, tier, ownership or qualifier edits on organization rows. All other canonical data is unchanged.

## Source decisions

Reuses batch 1 / round 5's one-value/one-evidence method, literal market vocabulary, ordered normalized-word quote check, identity/scope/currency certificate gate, field-level holds, pre-write collision checks, and full-tree application boundary. Reader pages have no retained raw HTML: their manifest SHA256 authenticates the retained reader text bytes. `raw_sha256` in inputs means the manifest's retained-source SHA256 (reader text for that route), with raw_file empty; text_sha256 is also recorded. No reader output is represented as independently fetched HTML. All 893 manifest hashes and all accepted quotes are checked.

Markets require company statements about their own products/services. Broad medical stays medical_healthcare_general; automotive remains unspecified absent explicit OEM/aftermarket evidence. Food processing uses those words, not Food & Beverage. J&O explicitly names household products and agricultural injection molding. Thermo Packaging explicitly supplies its own packaging to house wares, sports, cosmetics and named industries. Zing-Pac explicitly names food packaging, medical, cosmetics, pharmaceutical and lawn/garden applications for its own equipment. Swagelok's industrial fluid systems stay general_industrial. Off-vocabulary energy/consumer/communications labels are not forced into narrower tags. Menus and taglines were withheld as A-strength evidence. Redirected Cardinal/CPI/Stuchell pages are held for exact-entity attribution; a shared destination is not authority to copy another company's markets.

## Certificate follow-ups

Four extra fetches, one per organization (under three per organization):

- **Kapp Surgical ORG-001524 — applied iso_13485.** Own-domain linked certificate MD19.4432, National Standards Authority of Ireland; names **KAPP Surgical Instrument, Inc.**, **4919 Warrensville Center Rd., Warrensville Heights, OH 44128**. ISO 13485:2016; effective **2024-06-10**, expires **2027-06-09**. Scope: design/manufacture/service/distribution of reusable surgical instruments and accessories, orthopaedic implants and securement devices. Exact identity/site/number/expiry quotes in certificates.json; PDF SHA256 `61ca42a95e5bce159124fe38d6ef1e0c70b8122e5fc3cdad89b82e31591330b6` checked. Single named certificate scope, not all-site certification inferred.
- **Paramont ORG-001027:** readable linked AS9100D certificate 264532, Amtivo, expires 2027-01-16. AS9100 is already populated; no fill, evidence mint or additional field inferred. ISO 9001 portion not added.
- **ITPS ORG-001597:** fetched linked PDF is image-only under pdftotext; identity/dates remain unread. Hold for readable certificate with edition/site/issuer and current validity; no OCR performed.
- **Wrap-Tite ORG-000636:** linked PDF fetch failed; availability only, no absence inference. Hold for a retrievable certificate with the same required details.

PDFs, extracted texts and fetch receipts stay under `persist/pic18-markets-certs-2/certificates/`; only short business-fact witnesses travel. No private/CRM/licensed source or personal contact data is committed. Remaining certification holds require exact certificate identity, current edition and expiry, and site scope. No ISO transition ruling is self-issued.

## Named checks and application journal

- `python3 tasks/pic18-markets-certs-2-2026-11-16/build.py`: PASS; exact field union and evidence append through scripts/shard_io.py append_sorted. Pre-pass backups retained at `persist/pic18-markets-certs-2/pre-application/`. application.json records pinned base and counts by shard. Full canonical-data/task-file replay byte-identical.
- `python3 tasks/pic18-markets-certs-2-2026-11-16/check.py`: PASS; source hashes, all 42 quotes, certificate identity/scope/dates, uniqueness, complete 353-cell yield, every counts.json count and full canonical-data comparison against pinned main. Exactly 16 field fills / 42 new evidence rows, no unrelated field changes, old evidence edits or row loss. Five injected packet defects rejected: fabricated quote, invalid tag, missing disposition, tampered source hash, duplicate value.
- `python3 tasks/pic18-markets-certs-2-2026-11-16/guardcheck.py`: PASS; expired certificate and fabricated identity rejected; duplicate evidence ID, identical evidence in foreign shard, changed evidence payload and conflicting cell rejected before any canonical write.
- `python3 scripts/validate.py`: PASS, 0 errors; 41,617 evidence rows checked on this branch (batch 1's unmerged data excluded).
- `python3 scripts/check_row_loss.py --base origin/main`: PASS.
- `python3 scripts/export_vocab.py --check`: PASS.

Required two-family review and hosted CI remain pending. No shared scripts changed; their unittest suite was not run. Source presence is not independent semantic approval. This is conservative screening, not exhaustive semantic discovery or an issuer suspension-registry audit.

## Proposed follow-ups

- Resolve remaining exact-entity and off-vocabulary market holds through owner rulings or explicit company-product narratives.
- Obtain readable/current documents for unresolved certifications, including ITPS image OCR and Wrap-Tite retrievability.
