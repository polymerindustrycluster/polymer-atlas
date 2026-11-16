# NEI SCC capability scout — packet only

Claim: atlas-w16-nei-scout, controller-assigned lane NEI, 2026-11-16. No canonical data changes and no queue edits (contract §9).

Acceptance criteria fixed before analysis: identify latest public point/process release; index Ohio first within 1 GB total downloads; join at site grain only through explicit site registry links or unique street/locality matches; report Ohio and PIC-18 unique-site coverage and blank-field opportunity; classify SCC/tag proposals exact, broader or judgment-call; seed 20 matched sites and check operator-owned pages; report Wilson interval with unknowns explicit; hold all adoption for an owner ruling. First user: Atlas integrator; use decision at this wave's review, 2026-11-16.

Packet complete for review; all adoption remains held.

## Decision: NO-GO for bulk capability fills; GO as a bounded discovery lead

The SCC route yields a small matched frame, and the hand check confirms too few **site-specific capabilities** to authorize automated enrichment. All proposals in `crosswalk.csv`, `join_audit.csv`, and `frame.csv` are **held**. No evidence IDs, registry links, capabilities, statuses, or canonical rows are added. The Atlas integrator is the intended first user; the decision is due at wave review on 2026-11-16.

## Source and release

Latest available full release: **2023 NEI, final September 2026**. The 2026 inventory is planned, with products coming in 2029, not an available replacement. EPA's [release page](https://www.epa.gov/air-emissions-inventories/2023-national-emissions-inventory-nei), [supporting data page](https://www.epa.gov/air-emissions-inventories/2023-nei-supporting-data-and-summaries), and [technical documentation](https://gaftp.epa.gov/Air/nei/2023/doc/TSD/where-can-i-obtain-the-2023-nei-data.html) distinguish facility summaries from process summaries.

Exact [point/process ZIP](https://gaftp.epa.gov/air/nei/2023/data_summaries/2023nei_facility_process_byregion_21jul2026.zip): file dated 2026-07-21, 188,866,267 bytes by HEAD, despite the landing page's 421 MB label. Outer member `eis_report_38215_process_R5.zip`, bytes 28665921–57904414, contains `emis_sum_proc_38215.csv`. The embedded criteria identify 2023NEI, Region 5, annual routine emissions, not-tagged data. These are **2023 observations**, not proof of current operation. EPA's [SCC API](https://sor-scc-api.epa.gov/sccwebservices/v1/SCC?format=CSV) supplies official hierarchy descriptions.

Downloaded the 29,238,494-byte Region 5 range after stopping a 3.5 MB national partial. Stream-read Region 5, retain Ohio before projecting/indexing, deduplicate pollutant repetitions; no expanded national CSV is stored. National partial, Region 5 ZIP and compressed range were deleted after indexing. Total downloads including the SCC dictionary and sampled websites remained far below 1 GB; retained indexes/corpus below 2 GB. `source_receipt.json` pins the range and Ohio index hashes. Larger indexes and fetched own-site receipts live under controller storage `persist/nei-scc-scout/` (see scripts). Local estate search was incomplete: Windows Documents catalogue paths were absent on this Mac; no claim that local holdings are absent.

## Measured coverage (pinned Atlas baseline be2e6084d430f1e6f9de0f66289b1d3c2570e255)

Denominators include all Ohio Atlas site rows and all rings/statuses; PIC-18 is the county set in `scripts/regions.py`. These are distinct site candidates, not verified establishments or percentage gains in capability fill.

| Unit/filter | Ohio | PIC-18 |
|---|---:|---:|
| Atlas site rows | 2,010 | 1,136 |
| Sites with a unique join and at least one selected polymer-context SCC | 45 | 30 |
| Of those, blank `processes` | 23 | 13 |
| Of those, blank `materials` | 20 | 11 |
| Of those, either field blank (union) | 25 | 14 |
| Of those, at least one exact/broader candidate tag in crosswalk | 35 | 26 |

Ohio process index: **11,576 distinct projected rows / 1,842 EIS facilities**; independent DuckDB census reconciles both. Selection gives **225 distinct observed SCCs**, **240 candidate mapping rows**, and **2,644 projected source rows** (not distinct processes, because descriptions/calculation materials can vary). `metrics.json` is authoritative for machine-readable counts.

Selection uses whole-word plastic(s), rubber, resin(s), polymer(s), adhesive, ink in official SCC hierarchy, plus named coating application/operation codes. This is a generous **polymer-context** screen: heaters, solvent handling, storage, leaks and unclassified codes within polymer industries may enter the context frame. A hit does not imply an adoptable capability. General surface-coating application enters as a lead even where binder chemistry is unstated. Nonpolymer cereal coatings and metal conversion baths do not enter by the coating keyword alone. Not exhaustive: fibers and narrower chemical names without these words can be missed. Blank-field counts are opportunity ceilings, not fills.

Join: explicit site-level EIS/TRI registry links where available, otherwise normalized exact street plus five-digit ZIP, using the existing `atlas.street_key`. All candidates in this baseline use street+ZIP; no EIS/FRS IDs are invented, no parent-only registry link is promoted to a facility link. Source has EIS and TRI, not FRS; no FRS→EIS crosswalk was obtained. Multiple Atlas matches stay held. Unmatched rows stay in `join_audit.csv`; names/fuzzy matches do not create joins. A unique street candidate still needs operator confirmation and campus-grain resolution. Missing Atlas streets make this a conservative join census rather than a measure of NEI's full usefulness.

## Candidate SCC/tag crosswalk

`crosswalk.csv` covers observed selected codes and labels every proposed row **exact**, **broader**, or **judgment-call**. “Broader” means the proposed Atlas tag is coarser than the SCC; “exact” means same capability at Atlas vocabulary grain, not verified establishment attribution. Empty tag/field means no defensible controlled tag proposed. All held; settling facts are in each row.

Examples: 30801007 Molding Machine → `molding_unspecified` (exact); 30801002 Extruder → `extrusion_unspecified` (exact); 30800772 Pultrusion → `composites_pultrusion` (exact); tire manufacturing operations → `tire_manufacturing` / `elastomers_rubber` (broader); fiberglass resin products → `composites_frp` (broader). Acrylic Resins → `acrylic_pmma` is judgment-call, because acrylic resins need not be PMMA. Storage/cleanup codes do not mint process tags merely from their industry context. Material tags inferred from the broader family remain proposals for owner adjudication, never an assertion of feedstock at a specific unit. The dictionary is current at retrieval, not a reconstructed 2023 dictionary; historical SCC changes require checking before application.

## Twenty seeded hand checks

Uniform sample without replacement, `random.Random(20261116)`, frame sorted by site ID. Frozen in `sample_frame.csv`; row-by-row own-site assessments in `sample_checks.csv`. Fetched and inspected operator homepages and selected capability/location pages, with hashed receipts retained outside the repo; no substitution of failed sites. Two records had no Atlas own-domain URL; one homepage fetch failed. There were 17 readable homepages, two no-URL cases, and one failed homepage. No fetch failure is a disagreement or absence finding.

**2 VERIFIED, 18 STILL_UNCERTAIN, 0 REJECT.** Confirmation requires at least one site-named capability compatible with its selected SCC, not every SCC at the facility. Okamoto's own Sandusky about page states calendering; Duracote's own capability page states coating equipment under one roof in Ravenna. Premix-Hadlock's Geneva row has a Conneaut contact on its own page: hold exact establishment attribution. General parent claims, addresses next to general capability claims, and product menus are not accepted as site process confirmation.

Confirmed fraction of all sampled candidates: **2/20 = 10.0%, 95% Wilson interval 2.79%–30.10%**. Agreement among resolved checks is **2/2 = 100%, Wilson 34.24%–100%**, but the **18/20 unresolved** make this unsuitable as an accuracy estimate. There is no supported 90% disagreement claim. The sample tests at-least-one-capability/site agreement, not per-SCC precision, site-match accuracy, or present-day operating status. No capability is applied.

## Owner battery proposal B-NEI-SCC (held)

**Question:** May a dated government point-source SCC be a capability witness, and under what exact-code and site-link conditions?

**Recommendation:** Admit exact process-code observations as historical discovery/corroboration at facility grain; permit a narrowly reviewed pilot only after a named SCC crosswalk is approved, unique EIS/FRS linkage or validated operator/address match is established, and source year/operator currency is carried explicitly. Do not auto-fill parent capabilities, current status, specific resin from a family, or process from auxiliary emissions equipment. Hold broader/judgment mappings pending per-code adjudication. This scout does not establish a sufficient yield for a fill campaign.

**Existing source class / ceiling:** A dated NEI government record of fact fits `government_filing` under SCHEMA §4.13, whose existing class ceiling is `supports_A`. That ceiling is not an awarded tier, an SCC capability ruling, or permission to promote a record. A bare FRS/EIS registry identity record is `registry`, ceiling `supports_B`; registry address alone caps at `supports_C`. A tier-U record uses `supports_U`. A weak/context-only SCC cannot support a scope restatement at A/B. Any permitted future use must obey the owner's 2026-11-14 capability-row rule and preserve per-claim strength. Owner must decide whether SCC assignments merit capability support at all and cap that support; no schema is changed here.

## Reproduction and checks

`python3 tasks/nei-scc-scout-2026-11-16/build.py` rebuilds the packet idempotently from controller cache. `index_source.py` reconstructs the pinned Ohio projection from the exact checked Region 5 byte range if its index receipt is absent; SCC CSV is fetched from the API URL above into the same cache. It verifies the compressed range hash before decoding. `fetch_sample.py` fetches the seeded homepages through existing corpus transport; `extra_fetch.json` pins the manually selected follow-up pages. Sample judgments remain hand-authored and are never regenerated by the builder.

Named check: `python3 tasks/nei-scc-scout-2026-11-16/check.py` — PASS: packet replay, independent DuckDB index census, seed/uniqueness, exact supported quotes, and **4/4 injected defects rejected** (duplicate site, changed count, fabricated quote, corrupted stored witness). Required pre-push checks are recorded in the PR. No shared scripts or data changed.

## Proposed follow-ups

- Owner ruling B-NEI-SCC; settle broader/judgment-call mappings individually.
- Obtain public source-verified FRS↔EIS facility crosswalk, then rerun address-missing opportunity before considering another own-site batch.
- Resolve operator and campus identities before counting any candidate as an establishment; check exact process currency independently.

Not checked: comprehensive FRS crosswalk, per-SCC precision, full Ohio NEI recall, current operation, and every capability at each sampled plant. Risk: 2023 source year, broad classification context, and street/campus matches can overstate current site capability.

## Positive-witness reproducibility repair (2026-11-16)

Both positives were freshly re-obtained with **HTTP 200, direct route**, using `scripts/site_corpus.py` → `Corpus.fetch` → curl with `Mozilla/5.0 (compatible; AtlasSiteCorpus/1.0)`. No search snippet or proxy text was used for either positive. The reviewer's urllib 403 is a route availability difference; four held-source fetch failures leave those holds unchanged. Neither positive is downgraded, and the 2/20 fraction and Wilson intervals above remain unchanged.

The fetched full page text for each positive is now stored at a named path under controller storage `persist/nei-scc-scout/positive_witnesses/`. `positive_witnesses.json` in this task pins the text hash, URL, original raw hash/time, fresh raw hash/time, and transport. Both fresh extracted text hashes equal the original extracted text hashes.

| Site / witness | Fresh retrieval (UTC) | Stored file relative to `persist/nei-scc-scout/` | Text SHA-256 |
|---|---|---|---|
| SITE-000337 — https://www.duracote.com/capabilities/ | 2026-11-16T19:36:03.622070+00:00 | `positive_witnesses/SITE-000337.txt` | `92e5e7f06bfcf6b761af39f3c7abac1f9d0ecfbbe0fcf11a529f0cb4be944fe9` |
| SITE-001078 — https://okamotosandusky.com/about/ | 2026-11-16T19:36:04.377998+00:00 | `positive_witnesses/SITE-001078.txt` | `5879a81321241ea4debdd76f3a34cd195d26373a86d71b84b139548efe627b2b` |

`check.py` verifies each positive quote against that named stored text, checks its pinned hash, verifies fresh raw-page hashes and successful route receipts, and retains the original witness checks. Its fourth injected defect corrupts a stored copy, requires rejection, then restores the exact original bytes in a `finally` block. The full cached text stays in controller storage; only provenance metadata travels in this packet. Canonical data, sample selection, assessments, and coverage counts are unchanged.
