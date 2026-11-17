# PPP loan scout — 2026-11-16

Claim: atlas-w16-ppp-scout, controller thr_9i2c6byhcz; packet only. First user: Atlas integrator; assess usefulness at the next address-enrichment pass, by 2026-12-15. No canonical data edited, IDs allocated, tiers raised or records created. Every proposal is **held**, none applied.

## Terms and privacy before ingestion

Official [SBA FOIA release](https://data.sba.gov/dataset/ppp-foia), identifier SBA-OCA-2022-07-001, modified 2024-10-21, lists license **U.S. Government Works**. [SBA reproduction policy](https://www.sba.gov/about-sba/open-government/about-the-sba-gov-website/) permits distribution/copying of public-domain government information and requests acknowledgement; third-party protected material remains separate. This packet acknowledges SBA. Public release does not establish suitability for publishing home addresses.

The stream retains only named corporations, S corporations, LLCs, partnerships and LLPs. Sole proprietors, self-employed individuals, independent contractors, unknown business types and unnamed/redacted borrowers are excluded before indexing. No demographics, personal contacts or lender fields retained. An LLC can still use a home: unverified borrower addresses are **not committed**. Cache is restricted to the permitted business rows; even those addresses require an independently public business-location witness before publication. Loan numbers identify source loans, not people.

`manifest.json` records exact filenames, SHA256, dates, streamed bytes and parsed row counts. Raw files were never saved. The 2024 release has numbered files rather than Ohio files: file 9 contains Ohio among other states. Only national >150k and numbered file 9 were streamed in full; range probes of other files were discarded. These two files contain 968,524 and 900,000 loan rows respectively; 32,645 and 319,339 Ohio loan rows. Privacy gate excluded 2,674 and 168,497 Ohio rows; scope/name filtering retained 951 and 1,002 rows. Cache is under 1 MB, below 500 MB. cp1252 decodes release bytes without dropping records. Local SBA DNS failed mid-run; DNS-over-HTTPS lookup restored access with normal hostname TLS verification.

## Measured screening yield (units and filters)

Pinned Atlas inputs are hashed in `atlas_inputs.json`. The checkout has **1,046 active Ohio site rows in PIC-18**, using `scripts/regions.py`, all rings. Of those, **490** have empty street_address and **827** have empty employee_band_site. These differ from the brief's 419 and 22%; no attempt was made to silently reconcile different snapshots/filters. Nonempty `unknown` bands are excluded from the blank denominator.

| Use | Candidate sites / eligible sites | Rate | Wilson 95% | Applied / held |
|---|---:|---:|---|---|
| Street candidate | 152 / 490 | 31.0% | 27.1–35.3% | 0 / 152 |
| JobsReported present | 346 / 827 | 41.8% | 38.5–45.2% | 0 / 346 |

Intervals are descriptive screening intervals, not uncertainty on an exhaustively counted frame. Matching is deliberately provisional: normalized legal/trade/parenthetical names and locality-stripped site names across all shards, plus exact normalized street+city where available, then same borrower/site city. Domain is unavailable in PPP. Notes/rebrand chains and exact operator identity remain adjudication holds; these are **not** dedupe-approved joins. Filtering uses 325/326 OR held organization names; borrowed legal-name variants outside that filter may be missed. Street matches can hit co-tenants. No absence or closure is inferred.

Samples: sort unique site IDs; `random.Random(20261116).sample`, 20 without replacement independently for blank-street, blank-band and existing-band frames. Multiple loans per sampled site remain visible in cache, never summed. Public reviews contain site IDs and no unconfirmed addresses.

Twenty address candidates were inspected against own-company routes (URLs/status/hashes cached). Five have contact-address corroboration: Chemical Solvents, 31 Inc., JP Industrial, Adcal, Scott Molders. This is **5/20, 25%, Wilson 11.2–46.9%** for contact-address corroboration, not plant precision. JP explicitly labels its address headquarters. Contact-only pages, blocked/missing routes, old operators and changed addresses remain unresolved; **0/20 received a plant-confirmed verdict**. That is a verification yield, not evidence that all 20 candidates are wrong. Plant-address precision is unestimated; unresolved cases make the potential true proportion range 0–100%. Remaining primary/federal checks are a stated limitation of this packet.

Twenty blank-band site matches were hand-inspected at loan-row grain (`jobs_review.csv`): figures exist, but **0/20 have independently established site allocation**. Treating borrower headcount as plant headcount is unsupported. Twenty other sampled sites with nonempty Atlas bands were compared to their latest matched loan (not a sum): **15 within band, 4 outside, 1 unknown/uncomparable**. Among 19 comparable sites, 78.9% agree (Wilson 56.7–91.5%). This is arithmetic compatibility, not employee-count validation; bands may have different observation dates and grain. `band_review.csv` exposes every comparison.

The discovery screen yields **342 loan rows / 296 normalized borrower names**, Ohio ProjectCountyName in PIC-18, NAICS beginning 325/326, with no hit in the provisional name/site-name/street matcher. These are potential leads, not 296 proved missing establishments. County is source-reported project county, not independently geocoded borrower county. No domain/notes/successor adjudication or 20-lead precision sample was completed, so net-new precision is unestimated. The user's “nearly every small manufacturer borrowed” premise was not established and is not used as a denominator.

## Source semantics and owner battery B-PPP

Proposed classification: `government_filing` for the dated borrower application fact released by SBA. §4.13 permits that class up to supports_A for claims it actually states; it does not make a borrower address a plant address or self-reported NAICS a scope determination. Use at most corroborative supports_C for unresolved establishment identity; tier-U records use supports_U. No standalone current scope, activity or liveness upgrade.

`size_band` permits government_filing/own_site only and caps at **supports_B**, per B-BAND and `tasks/size-band-evidence-2026-11-03`. Its cited precedents are OSHA and Form 5500, not an explicit PPP admission. JobsReported is a borrower application employment measure, not audited site employment or jobs saved. Owner approval and site-allocation evidence are required before mapping it to a site band; never sum draws, loans or parent sites. Date each claim to **DateApproved (2020–2021)** (the SBA dictionary labels it Loan Funded Date) as the available loan observation date, explicitly noting the underlying employment reference period is unspecified. Record 2024-09-30 as release vintage and 2026-11-16 as retrieval date; neither makes employment current. `last_verified` records the actual check date and must not disguise historic evidence as current.

| Proposed use / battery choice | Recommendation | Applied / held | Settling fact |
|---|---|---|---|
| Address research queue | GO as discovery only | held | Explicit operator plant address from own site or federal establishment record, privacy cleared |
| Automatic street fill | NO-GO | held | Plant precision test resolving the 20 sample cases and exact operator matches |
| Current site employee band | NO-GO | held | Owner admission, dated establishment allocation, comparable employment definition |
| Historic borrower size witness | Conditional GO, separate dated research packet | held | Owner decides whether PPP is admitted under B-BAND and how historic borrower grain is represented |
| Polymer-NAICS discovery | GO for targeted primary verification | held | Full AGENTS §3 keys and 20-loan lead precision sample; NAICS alone never settles scope |

Owner question B-PPP: admit privacy-filtered SBA PPP as historical government-filing discovery/corroboration, prohibit automatic plant streets/current bands, and require independent plant/operator evidence plus explicit owner admission for any size-band integration? Recommend yes. No schema vocabulary is changed here.

## Reproduction and validation

`python3 tasks/ppp-loan-scout-2026-11-16/fetch.py` resumes completed-file receipts and streams remaining files. `build.py` recomputes frames/cache packets; `finish.py` renders fixed hand-review decisions. `check.py` checks input hashes, independent CSV retained counts, yields, intervals, privacy filtering, idempotence and rejection of three injected defects (wrong yield, missing receipt, bad hash). Raw input row counts are parser counters recorded during streaming; no second full download was made to independently recount the discarded raw files.

Proposed follow-ups: complete federal plant adjudication of the address sample; full dedupe and lead sample; independent employment/site allocation; verify file boundaries against a complete release index. No new tracked commitments created. No data changes at any tier; no inclusion_log entries.

## B-PPP bulk organization-grain addendum (2026-11-16)

No hand checks or new downloads. The original provisional match found **415 organizations / 424 active PIC-18 sites**. All 606 loan–site pairs have positive integral JobsReported and map to the existing eight Atlas bands (`1-9` through `5000+`) using the held Form 5500 band helper. Each organization/site contributes once: choose the latest loan date, break ties by loan number, never sum draws. Rows and full-precision intervals are in `org_bulk_comparisons.csv` and `org_bulk.json`.

Single-site Ohio-only means **exactly one active site across all held site shards, and every held site (including inactive) is in Ohio/US**. There are 392 such organizations among the matches. This is the requested operational proxy for borrower = organization = plant; unrecorded sites and mismatched borrowers remain a limitation of the held data. No subsidiary headcount is rolled up to a parent.

Comparison categories are disjoint: exact band, exactly one band away, two or more bands away. “Within one” additionally includes exact matches. Denominator is records with an in-vocabulary held band; blank/unknown/off-vocabulary values are uncomparable and excluded, not silently normalized (e.g. 100–199 is not the adopted 100–249). CIs are descriptive Wilson 95% intervals, not causal accuracy or a census sampling error.

| Unit / cohort | Matched | Comparable | Uncomparable | Exact n (%; 95% CI) | Adjacent only n (%; 95% CI) | Off ≥2 n (%; 95% CI) | Within one n (%; 95% CI) |
|---|---:|---:|---:|---|---|---|---|
| organizations / all_matches | 415 | 114 | 301 | 82 (71.9%; 63.1–79.4%) | 30 (26.3%; 19.1–35.1%) | 2 (1.8%; 0.5–6.2%) | 112 (98.2%; 93.8–99.5%) |
| organizations / single_site_ohio | 392 | 106 | 286 | 75 (70.8%; 61.5–78.6%) | 29 (27.4%; 19.8–36.5%) | 2 (1.9%; 0.5–6.6%) | 104 (98.1%; 93.4–99.5%) |
| sites / all_matches | 424 | 76 | 348 | 56 (73.7%; 62.8–82.3%) | 17 (22.4%; 14.5–32.9%) | 3 (3.9%; 1.4–11.0%) | 73 (96.1%; 89.0–98.6%) |
| sites / single_site_ohio | 392 | 72 | 320 | 54 (75.0%; 63.9–83.6%) | 16 (22.2%; 14.2–33.1%) | 2 (2.8%; 0.8–9.6%) | 70 (97.2%; 90.4–99.2%) |

### Potential blank-band fills (every proposal held, zero applied)

For the requested rules, **name+address** is the strict case: borrower name matches an organization legal/trade/parenthetical name or one of its site names, and the borrower street+city matches a held street+city of that organization. Rule (b) additionally requires the single-site Ohio-only proxy; rule (c) additionally requires that same qualifying loan’s NAICS to start 325 or 326. If several loans qualify, choose the latest qualifying loan. This differs from the original scout’s weaker name-or-street plus city screen. We report the weaker name+city with a supplied borrower street separately, so it cannot be mistaken for exact street matching. Blank means empty, not `unknown` or off-vocabulary.

| Match evidence | Rule | Eligible organizations | Blank organization Ohio bands | Blank site bands on single-site Ohio-only orgs | Applied / held |
|---|---|---:|---:|---:|---|
| name_city_address_present | a | 384 | 275 | 294 | 0 / all |
| name_city_address_present | b | 362 | 260 | 294 | 0 / all |
| name_city_address_present | c | 193 | 114 | 138 | 0 / all |
| name_street_city_exact | a | 185 | 124 | 137 | 0 / all |
| name_street_city_exact | b | 174 | 117 | 137 | 0 / all |
| name_street_city_exact | c | 92 | 47 | 62 | 0 / all |

Rules (a) and (b) have equal single-site site counts because that column already restricts to single-site organizations. Fill counts are candidate record counts, not mutually exclusive additions: (c) is nested in (b), nested in (a). `org_bulk_fills.csv` carries deduplicated rule/grain/record keys, dated source loan IDs and mapped bands, with no borrower streets.

### Updated owner recommendation and dating

**B-PPP: recommend conditional GO for historical organization Ohio-band candidates under strict rule (b): 117 blank organization bands, plus 137 blank site-band candidates at the same operational grain.** If the owner wants a polymer-NAICS restriction, strict rule (c) narrows these to **47 organizations / 62 sites**; NAICS is an extra filter, never scope proof. The broader rule (a) yields 124 blank organization bands but includes multi-site borrowers, so Ohio allocation is unresolved and it is not recommended for automatic filling. Weak locality-only candidates (260 organizations / 294 sites under b) remain discovery-only. All remain HELD pending owner admission, exact borrower/operator adjudication and source precedence; canonical values are not changed.

The bulk comparison supports a historical band witness more than the small hand sample alone: for the single-site proxy, 104/106 comparable organization bands and 70/72 comparable site bands are within one band. This does not establish that the missing-band population has the same agreement, that adjacent bands are exact, or that the matching is correct. Existing disagreements go to review per R13; PPP must not overwrite OSHA/other preferred sources.

**Vintage: loan approval date (the release column `DateApproved`, called “Loan Funded Date” in the SBA dictionary), 2020 or 2021.** Across selected comparison observations there are 447 dated 2020 and 392 dated 2021; these count organization and site observations separately, so the same loan can occur at both grains. Label any admitted band “historical borrower-reported employment band, SBA PPP, loan date YYYY-MM-DD (2020/2021); underlying employment reference period unspecified; retrieved 2026-11-16.” Use that exact source date in the existing BAND-SOURCE notes convention (and employee_count_source_date if adopted/exported), not the 2024 release or 2026 retrieval as employment vintage. Evidence observed_date carries the source period/date where force depends on it, with retrieval in notes. Never label it a current 2026 band or infer 2026 liveness. Owner must decide whether historic values may populate the undated band columns with explicit notes, or stay research-only; recommend historical-labelled fills only under the strict single-site rule and after the gate above.
