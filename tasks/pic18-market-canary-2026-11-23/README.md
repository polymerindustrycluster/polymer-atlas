# PIC-18 live-site market canary, 2026-11-23

**3 of 25 market-unknown PIC-18 organizations (12%) had at least one VERIFIED organization-level market statement.** The 95% Wilson interval is **4.2%–30.0%**. Applying the unrounded interval to the requested 274 populated website cells gives **11.4–82.1 organizations**. That projection assumes the sampled rate also applies to the cells excluded from the draw. Scaled to the 255 eligible organizations, the interval is **10.6–76.4 organizations**.

The 25 organizations reconcile to **3 with a fill, 10 held after reading, and 12 with no readable page**. The 3 fills are ABC Packaging Direct, Kaufman Container and Hapco, with eight organization–term pairs in [selection.tsv](selection.tsv). Each source sentence attributes the supply to the sampled company and names an end market. The packet represents organization-level claims.

The evidence binding gate on main assigns a web quote that clears the mechanical checks **READ_REQUIRED** ([checker](../../scripts/check_evidence_binding.py), lines 23 and 33). The owner approved admission by per-row proof on 2026-11-23. The current gate holds the fills until that path is deployed.

## Frame and control scoring

Claim `atlas-w23-market-canary`, controller `thr_9i2c6byhcz`, owner-approved live trial 2026-11-23. Packet base `454dc9f57ff6f676b9c0c1742203f089ca898805`. The controller's `pic18_unknown.py` and the packet replay independently counted **316 market-unknown of 794 PIC-18 organization rows**. Both use active tier A–C Ohio sites in `scripts/regions.py` PIC18, union site terms first, then fall back to the organization or ecosystem row. A market is unknown if both grains have no terms after discounting the `unknown` sentinel.

Of the 316, **274** had a populated website cell. Five cells were missing-site sentinels, and three contained multiple or annotated URLs. The previous canary's single-link parser yields **266**. The 25 IDs from the November 22 canary at `eacd6fd1` excluded 11 of those 266, leaving **255** eligible. For the controls, the same website parser yields 478 market-known organizations before those exclusions and **464** after. The resulting pools were sorted by organization ID, shuffled independently with seed 20261123, and drawn without replacement. [frame.csv](frame.csv) carries the draw.

The control selection and holds were frozen before opening the recorded market terms. **4 of 10 controls reproduced at least one recorded term** (4 of 7 controls with a readable page). **4 of 6 read organization–term pairs agreed with the recorded terms (66.7% recorded-term precision).** The records have incomplete coverage, so the other two reads are leads.

| Control organization | Recorded term reproduced | Additional term read |
|---|---|---|
| FlexLink | `packaging_industrial` | `general_industrial` |
| RP+M | `aerospace_defense` | |
| Novatex North America | `medical_healthcare_general` | |
| Graphic Arts Rubber | `pharmaceutical_biotech` | `plastics_rubber_processors` |

## Availability and reading

| Cause of no readable page | Market-unknown organizations | Control organizations |
|---|---:|---:|
| TLS error reading robots.txt | 4 | 0 |
| DNS failure reading robots.txt | 2 | 0 |
| Connection refused reading robots.txt | 1 | 0 |
| Empty reply reading robots.txt | 1 | 1 |
| Page returned HTTP 403 | 1 | 1 |
| robots.txt returned HTTP 403 | 1 | 0 |
| HTML contained less than 200 main-text characters | 2 | 1 |
| **Total** | **12** | **3** |

**156 HTTP attempts** across both cohorts, including **99 page requests** and **57 robots.txt requests**. The fetch ran **3 minutes 51 seconds** from first to last HTTP attempt (06:37:26–06:41:17 EST). The frame reconciliation through frozen reading took about **7 minutes**, followed by replay, documentation and branch publication.

The November 22 fetcher retained its declared `Mozilla/5.0 (compatible; AtlasSiteCorpus/1.0)` user-agent, robots checks per hop, 1.2-second host delay and one conditional HTTP/1.1 transport retry. Redirect hops, retries and any meta refresh consume the six-attempt page budget. Market and industry links took priority over capabilities, about, product and service links. The adapted screen selected relevant lines for reading. A reader adjudicated the source operator, surrounding wording and controlled term. A failed fetch records availability for this run. The live pass used HTTP text extraction. The Wayback follow-up is below.

The `persist/market-canary-2026-11-23/` controller store has the attempt and response manifest, SHA-256 hashes of bodies and extracted text, and 79 extracted-capture receipts with privacy-reviewed exact excerpts where selected. Before writing excerpts, the fetch session matched each sentence against its in-memory extraction and recorded its original offset and line kind. Full page and robots bodies stayed in memory because they can contain names or direct contact data. Replay re-hashes the preserved receipts and checks the saved excerpts, while full-page hashes are receipt metadata. The branch includes the checksum manifest and the reviewed sentences.

## Owner questions

1. Does a generic “medical industry” statement map to `medical_device` or `medical_healthcare_general`, or require a named audience? Novatex's control quote explicitly names hospitals, pediatricians and clinics.
2. Does a group portfolio claim qualify when the Atlas org is itself the group? The American Bath Group brands page names new construction, but the trial held the umbrella claim. The U.S. Storopack site's group language is also held, along with the Huntsman, Zimmer Biomet and Kenda group claims.
3. Does `lawn_garden_recreation` cover pools and waterparks? The Family Fun Pools control was held on the words read.
4. Do generic “industrial and commercial applications” qualify for `general_industrial`? Speedline was held. The FlexLink control explicitly names industrial markets.
5. Are the jewelry trade, unnamed packaging submarkets, or application descriptions sufficient for a controlled tag? Zero-D names jewelers, while the Enterprise Rubber and Lamports pages describe product uses without a sentence linking the operator to the market.

## Replay

`python3 tasks/pic18-market-canary-2026-11-23/check.py` replays the frame, attempt accounting, capture hashes, quote checks and control scoring. Five separate mutations pass with their relevant rule disabled and fail with it enabled. The mutations cover a paraphrase, a product-only sentence, a parent-group page, another organization's page and an invented term.

Pages outside the six-attempt budget and independent second-reader adjudication were outside this trial. The owner-approved admission path has yet to reach the binding gate on main.


## Wayback follow-up, 2026-11-23

The owner ruled that an own-site capture up to two years old can witness a market. The follow-up tried the 12 market-unknown organizations with no readable live page. **6 of 12 yielded readable archived pages, with zero new VERIFIED organizations or terms.** The combined result remains **3 of 25** with a VERIFIED fill (12%, 95% Wilson **4.2%–30.0%**). The other 22 comprise **16 held after reading** and **6 with no readable page**.

The six readable recoveries were SurgTech, Spectrum Plastics, Rack Coating Services, Grafix, Premier Aerosol Packaging and Inflatable Images. The strict sentence rule held the claims in truncated product previews, market headings, standalone categories, and descriptions of product uses or services with no named customer market. The other six and their availability outcomes are in [archive_results.tsv](archive_results.tsv).

The trial requested exact-URL CDX matches first. A second pass tried a filtered domain lookup where at least two requests remained. It prioritized market, industry, capability and company pages from the index, then replayed promising dated HTML candidates until a page was readable or the request limit was reached. The Lincoln Electric domain lookup returned subdomain captures, and all three tried were thin. The window was 2024-11-23 through 2026-11-23 inclusive. Replays required Wayback `id_`, a same-registrable-domain original and an in-window capture date. The original robots-aware user-agent was used throughout.

**54 logged Wayback requests** (including two shared robots requests), plus one shared robots preflight. The two fetch passes spanned **5m 28s** from first to last logged request. Each organization stayed within six attempts across the passes. The fetcher recognized gzip via the Content-Encoding header or magic bytes and decompressed before hashing. [WAYBACK.sha256](WAYBACK.sha256) binds the attempt log and 22 extracted-capture receipts in `persist/market-canary-2026-11-23/wayback/`. Full bodies remained in memory for privacy. There were no selected archive excerpts.

The named replay also checks the archive request cap, dates, original domain and receipts, and recomputes the combined Wilson interval. It exercises gzip detection and failure, the date boundary, and rejection of cross-domain or non-`id_` replays. The archive pass used one reader and the CDX results and pages reached under the request budget.
