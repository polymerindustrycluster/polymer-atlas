# PIC-18 market follow-up (owner rulings 2026-11-19 M1 and M2): 4 of 14 organizations' `markets_served` filled (7 values), 10 held

Claim: atlas-w18-mktscale (controller thr_9i2c6byhcz). First user: the Atlas owner, for prospecting by market; non-use is a finding if no prospecting list uses `markets_served` by 2026-12-16. No issue closed. Family review is pending. Rulings: `tasks/owner-rulings-2026-11-19/README.md` (PR #401).

## Frame, unit and filter

Unit: PIC-18 organization records. **M1** re-screens the 17 organizations held as `group_or_redirect_attribution` in the market-scale batches (10 in #390, 7 in #396): a market claim on a group's website is attributable to a subsidiary or division record only where the page names that subsidiary, its brand or its plant as the subject of the claim; a group-wide claim alone stays held. The controller removed 4 of the 17 as not group-site cases (below), leaving **13**. **M2** adds Myrava (ORG-001558): its note "do not promote above C without own-site check" caps the tier only, so `markets_served` may be filled at tier C from an own-site claim. Frame = 14 organizations, recomputed from the merged batches' `verdicts.csv` (hold class) and compared by `check.py` with the ruling's own ID list.

Out of M1 scope, left held with their existing settling facts (controller, from the Codex review of #401), reported here only:

| Organization | Existing hold class | Existing settling fact |
|---|---|---|
| ORG-000036 Win Plastic Extrusions LLC | group_or_redirect_attribution | An own-page sentence by Win Plastic Extrusions itself naming its customer industries; a directory listing of other manufacturers settles nothing. |
| ORG-000169 Zatkoff Seals & Packings | group_or_redirect_attribution | An own-page sentence by Zatkoff naming customers or industries it supplies; manufacturer catalog copy settles nothing. |
| ORG-001461 Stuchell Products, LLC | group_or_redirect_attribution | An own-page sentence from the Stuchell Products site naming markets; the CPI Precision Plastics page names another entity. |
| ORG-002038 Pinnacle Recycling, LLC | group_or_redirect_attribution | Owner ruling on subsidiary or division records whose only website is the group site (controller is taking it to the owner); or an own-page sentence from the record's own entity. |

Reading basis: each frame organization's stored pages were searched for the record's name, brand and plant words; each page that names the subject was read; every organization's stored `<a>` links were searched for pages that could name the subject (7 fetches, below). `page_read` = the page naming the subject was opened and read.

## Result

**4 of 14 filled (29%); 95% Wilson interval 12% to 55%.** Counted separately: **4 organizations, 4 distinct witness URLs, 4 distinct quoted passages, 7 values**. Tiers: B 2, C 1. 1 from stored pages, 3 only after a live fetch of a page linked from a stored page (rule 14). M1 applies: 3 of 13; M2: Myrava. Evidence IDs EVD-397377 to EVD-397386 (allocated from one above the maximum across `data/evidence_*.csv` at the base, EVD-397376, owner ruling E1).

## Applied (every quote a narrative sentence or a content-page markets list, supports_A; no group-wide claim is attributed)

| Organization (tier) | `markets_served` | Evidence (EVD- numbers) | Source and quote | Basis |
|---|---|---|---|---|
| ORG-000119 Mechanical Rubber Ohio LLC (B) | rail_transportation; general_industrial | 397377-397378 | live: www.mechanicalrubber.com/mechanical-rubber-ohio/: "Durox Extrusions Request For Quote OEM & Custom Profiles Locomotive, Transit, Vehicle, Off-Road & Industrial Markets" | M1 (quote subject): The fetched page is titled and addressed "Mechanical Rubber Ohio" (URL /mechanical-rubber-ohio/) and its heading names the facility's product brand Durox Extrusions; the record's trade name is Mechanical Rubber and its site is mechanicalrubber.com. |
| ORG-000606 Third Dimension Division (A) | packaging_consumer | 397386 | live: gbp.com/locations/third-dimension/: "E Flute: Perfect for retail packaging and displays, offering a fantastic print surface." | M1 (page subject): The witness is the Third Dimension Division's own page on the GBP site (URL /locations/third-dimension/, title "Third Dimension Division | Green Bay Packaging", H1 "Third Dimension Division Corrugated Box Manufacturer Geneva, OH"); the E Flute paragraph sits in the body of that page. Mode page: the quote itself does not repeat the name. |
| ORG-001558 Myrava, LLC (C) | medical_device | 397379 | stored: myrava.com/: "Empowering clinicians with FDA-cleared, patient-specific medical devices and point-of-care manufacturing solutions ​that can help improve care , enhance efficiency , and support better outcomes" | M2: own site; the note caps the tier only, which stays C |
| ORG-001949 Akron Steel Fabricators Co. (B) | tire_rubber_goods; plastics_rubber_processors; chemical_mining_metals_processing | 397383-397385 | live: polinggroup.com/company_info_asf: "Serving the tire, rubber, plastic, and steel industries, the ASF Division offers a complete line of proven standard machinery products, including new calenders and ancillary equipment, mill blender..." | M1 (quote subject): The fetched page is the ASF Division page of the Poling Group site ("The History of ASF-Akron Steel Fabricators"); ASF is the record's name and division, and the quote names the ASF Division. |

Term notes. `rail_transportation` for "Locomotive, Transit" and `general_industrial` for "Industrial Markets" (Durox Extrusions' line on the Mechanical Rubber Ohio page; "Vehicle" and "Off-Road" name no section 3.3 term). `packaging_consumer` for "retail packaging and displays" (Third Dimension's E Flute paragraph; a paragraph in the page body, not a list or menu item, so supports_A on this tier A record). `tire_rubber_goods`, `plastics_rubber_processors` and `chemical_mining_metals_processing` for "the tire, rubber, plastic, and steel industries" (ASF Division): tire and rubber and plastic map to the first two; section 3.3 has no steel term, and `chemical_mining_metals_processing` is the registered chemical, mining and metals-processing term, whose meaning covers the steel industry (the batch-2 precedent is AML's "metal forging ... metalforming"), so steel is mapped there and is not broader than the words. `medical_device` for Myrava's "FDA-cleared, patient-specific medical devices". Observation dates come from the journals: the corpus manifest's `fetched_at` for a stored page (Myrava 2026-11-16) and the fetch journal's `fetched_at` for a live page (2026-11-19).

## Holds (10 organizations, `STILL_UNCERTAIN`; settling facts in `verdicts.csv`; none is a finding of absence)

| Organization | Hold class | Why |
|---|---|---|
| ORG-000438 Mexichem Specialty Resins Inc. | no_market_claim | M1 re-screen: the fetched Vestolit region page names the Avon Lake plant and Mexichem Specialty Resins, Inc. (a pilot plant for dispersion, blending, powder coating and specialty suspension vinyl resins, and "market needs for new product development") but names no customer industry or product market; the stored pages are the Vestolit group's. |
| ORG-000752 Polynt Composites USA, Inc. | group_or_redirect_attribution | M1 re-screen: the stored Polynt texts name POLYNT COMPOSITES USA INC. only in a location block (an address at Carpentersville, Illinois); no stored or fetched page names Polynt Composites USA, Sandusky or Cook Composites as the subject of a market claim, and the market statements ("transportation and construction to electronics and energy"; the composites product page) are the Polynt group's. |
| ORG-001447 Axalta Coating Systems USA LLC | group_or_redirect_attribution | M1 re-screen: no stored page names Axalta Coating Systems USA or Orrville as the subject of a claim; the RV, powersports, aviation, marine and rail and light-vehicle statements are the global group's. |
| ORG-001462 Clevite Elastomers Technical Center (Tenneco) | group_or_redirect_attribution | M1 re-screen: no stored Tenneco page names Clevite or Milan; the markets statements (emissions, bearings, performance solutions) are Tenneco's. |
| ORG-001513 Coltene/Whaledent Inc. | group_or_redirect_attribution | M1 re-screen: the stored pages are the COLTENE Group's ("© COLTENE Group") and never name Whaledent, Coltene/Whaledent or Cuyahoga Falls; COLTENE is the group's brand, so the dental statements are group-wide. |
| ORG-001534 Zimmer Surgical, Inc. | group_or_redirect_attribution | M1 re-screen: the stored Zimmer Biomet pages name Zimmer Surgical only in a contact address (Dover, Ohio); the fetched Surgical specialty page names no subsidiary; the healthcare statements are Zimmer Biomet's. |
| ORG-002047 Wayne-Dalton Plastics (Wayne Dalton Corp) | off_vocabulary_or_ambiguous_market | M1 re-screen: the record's legal name embeds Wayne Dalton Corp and the stored pages speak as Wayne Dalton ("At Wayne Dalton, we strive to accommodate all customers ... garage door styles"), so attribution is met; the stated products (residential garage doors, dock equipment) carry no wording that matches a section 3.3 term (no "building" or "construction"). |
| ORG-003196 Eckart America Corporation | group_or_redirect_attribution | M1 re-screen: the stored ECKART pages name ECKART America only in a certificate list (ISO and policy PDFs); every market statement (coatings, plastics, cosmetics pigments) is the global group's. |
| ORG-003771 ST BlowMoulding USA LLC | group_or_redirect_attribution | M1 re-screen: the stored pages name ST BlowMoulding USA LLC only in address footers; the industrial packaging and automotive statements are the Italian group's. |
| ORG-004022 VMI Holland B.V. | group_or_redirect_attribution | M1 re-screen (Codex round 1): the VMI Care card ("VMI Care creates automatic systems for the pharmaceutical industry") names a VMI Group business line on a site credited to VMI Holland B.V.; no stored or linked page ties VMI Care to VMI Holland B.V. as the entity that runs it, and the site calls itself VMI Group. The pharmaceutical term fits the words, so only the entity link is missing. |

## Writes (rule 13) and outcome check

- Only `markets_served` changes, on 4 organization rows, each blank at base: `data/organizations_OH.csv` and `data/organizations_INTL.csv`. 7 evidence rows appended to the matching `evidence_organizations_*.csv`. `check.py` compares every data file with the base and requires each applied row's tier unchanged (Myrava stays tier C).
- Publish order: evidence shards, then organization shards, each staged, verified against the base row counts and replaced atomically; backups are written from `git show 55ab601a:<file>` into `pre-application-batchfollowup-55ab601a` with sha256 recorded and verified (batch 2's hardened `build.py`).
- Outcome: `python3 S/harness/pic18_unknown.py "$PWD" <ref>` (unit: PIC-18 organization rows, 794). At merge-base `55ab601a`: `mkt_unknown=319`. At HEAD: `mkt_unknown=315`. **It fell by exactly 4, the number of organizations applied.**

## Live fetches (rule 14)

7 fetches, each of a URL linked from a stored page of the same organization (`fetches.csv` records the linking page), through `scripts/site_corpus.py` (robots-aware), cached under `S/persist/pic18-market-followup-2026-11-19/` with sha256: Mechanical Rubber Ohio, Third Dimension Division, Vestolit US region sites, Poling ASF Division, Zimmer Biomet Surgical, Polynt Composites, Zatkoff (fetched before the controller took ORG-000169 out of M1 scope; unused). 3 applied (Mechanical Rubber Ohio, Third Dimension, ASF). No organization exceeded 1.

## Self-refute (rule 15)

- self-refute: grain — 4 organizations checked, 0 changed. Every M1 claim sits on a page that names the subject: the Mechanical Rubber Ohio facility page (and its Durox Extrusions brand), the Third Dimension Division's own page, the ASF Division page; Myrava's is its own site. The writes are organization-grain; Mechanical Rubber's group address (Warwick, NY) is not used. VMI (the Dutch group entity) was held because the VMI Care card does not tie the line to the recorded entity.
- self-refute: founding — 4 rows checked, 1 changed. The ASF quote first began "Established in 1946, ..."; the witness is now the "Serving the tire, rubber, plastic, and steel industries" passage and no founding year is written.
- self-refute: strength — 7 values checked, 0 changed. The judgment calls: the Durox line "OEM & Custom Profiles Locomotive, Transit, Vehicle, Off-Road & Industrial Markets" is a content-page markets line (supports_A under the controller's ruling; `witness_class.nav_only` finds it outside chrome); the E Flute sentence is a `<p class="wp-block-paragraph">` in the page body, not a `<li>` or menu, with a bold label; the ASF sentence is a full sentence.
- self-refute: truncated quote — 7 values checked, 0 changed. Each quote ends at its claim words (the ASF quote runs through its sentence end).
- self-refute: attribution — 14 organizations checked, 10 held. The M1 subject test is a check, not a reading: every applied M1 record needs a `subjects.csv` entry (with its basis) and either its quote names the subsidiary, its brand or its plant (mode quote) or the witness is the subsidiary's dedicated page (mode page: the title names it and the URL carries the slug). Polynt, Axalta, Clevite, COLTENE, Zimmer Surgical, ECKART and ST BlowMoulding stay held because no page names the subsidiary as the subject of a market claim (Polynt's stored texts name POLYNT COMPOSITES USA INC. only in a location block, an Illinois address); VMI is held for the missing entity link; Vestolit's Avon Lake and Wayne Dalton name the subject but state no market in section 3.3 words.

## Review rounds on #403 (Codex 6 findings, Gemini approve; each fixed or rebutted)

| # | Finding | Call |
|---|---|---|
| 1 | Live witness dates predate the fetch | Fixed: `observed_date` comes from the journals (manifest for a stored page, fetch journal for a live page); `check.py` derives it from the journals separately and compares (the date injection still runs) |
| 2 | VMI lacks the M1 link to the recorded entity | Fixed: held; EVD-397382 retired; settling fact: a page that ties VMI Care to VMI Holland B.V. |
| 3 | ASF names a third market | Fixed: the witness is the "Serving the tire, rubber, plastic, and steel industries" passage; steel mapped to `chemical_mining_metals_processing` (reasoning in the term notes); EVD-397380 and 397381 retired, new rows 397383 to 397385 |
| 4 | Polynt hold misstates the corpus | Fixed: the verdict and README now say the stored texts name POLYNT COMPOSITES USA INC. only in a location block (Carpentersville, Illinois); the hold stands because no market claim names it as the subject |
| 5 | Third Dimension packaging_consumer | Applied: "E Flute: Perfect for retail packaging and displays, offering a fantastic print surface." is a body paragraph (not a list or menu), so it is supports_A on tier A; `retail packaging` is added to the wording map; EVD-397386; the subject is established by mode page (the division's dedicated page) |
| 6 | Parent-only probe | Fixed: every applied M1 record must have a subject entry; the probe (Codex's Poling sentence, no subject entry) is accepted when the subject rule is disabled and refused when enabled (no subject entry, and a name-less quote with an entry); a page-mode slug injection is added |

## Named checks

- `python3 tasks/pic18-market-followup-2026-11-19/check.py`: PASS with the boundary check; reuses batch 2's injections (frame count and identity, term, quote, hashes, duplicate, hold without a settling fact, tier effect, read basis, tag wording, OEM wording, new ID above the base maximum, retired ID reuse, falsified evidence provenance in the shard and the packet, backups: stale base, 128-byte truncated, replay, third apply, retry after the first canonical evidence write, unsafe write order, renumber replay) and adds: **a parent-only claim with no subject entry**, **a group-wide claim attributed to a subsidiary** (a record whose quote does not name its subject is refused), **an out-of-scope organization swapped into the frame**, **the Myrava tier changed** (in the verify step and in the data write), and a `group domain witness` for a record with no named subject. The do-not-promote assertion is lifted only for the M2 record.
- `build.py` is idempotent. `scripts/validate.py` 0 errors; `check_row_loss.py --base origin/main`, `export_vocab.py --check` and `python3 -m unittest discover -s scripts -p 'test_*.py'`: see the PR description.

## Not checked

Family review. Holds were screened by name search over stored pages and the 7 linked fetches; other group-site pages that might name a subsidiary were not crawled. No site-level markets.

## Proposed follow-ups (not in this PR)

- Polynt, Axalta, Clevite/Tenneco, COLTENE, Zimmer Biomet, ECKART and ST BlowMoulding: a subsidiary-specific page (a US plant or product-line page naming the Ohio entity) would settle each.
- Wayne Dalton ORG-002047: a sentence naming the building or construction trade in words that match a section 3.3 term.
