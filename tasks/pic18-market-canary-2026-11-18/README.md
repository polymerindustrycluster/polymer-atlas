# PIC-18 market canary, 2026-11-18: 10 organizations MKT3 left `not_adjudicated`

Claim: atlas-w18-mktcanary (controller thr_9i2c6byhcz). First user: the Atlas owner, for prospecting by market; non-use is a finding if no prospecting list uses `markets_served` by 2026-12-16. No issue closed. Family review is pending.

## Question and answer

Can `markets_served` still be filled from stored own-site pages for PIC-18 organizations MKT3 (PR #360, `tasks/pic18-markets-3-2026-11-16/`) left `not_adjudicated`? **3 of the 10 organizations filled; 2 from stored pages alone and 1 (Alterra) only after a live fetch of an own-site page linked from the stored home page.** Seven are held, one of them (GrafTech) gated on an owner ruling. n = 10, so the 95% Wilson interval for 3/10 is 11% to 60% (2/10: 6% to 51%). The scale-up bar (3 or more apply and the refute is clean) is met on the count only if the live fetch is counted; the refute has not run. The scale-up decision stays with the controller.

## Frame, unit and filter

Frame: the 10 organizations drawn by the controller (seed 20261118): ORG-000043, 000087, 000157, 000469, 000508, 001380, 001422, 001504, 001892, 002136. `check.py` recomputes, independently of the verdict table, that each is blank at base `200859b5`, is `not_adjudicated` in MKT3's `holds.csv`, and has at least one stored text page of 1 KB or more in the pinned MKT3 manifest snapshot. Tiers: A 3 (000087, 000508, 001892), B 6, C 1 (000157).

MKT3 reached vs not (from its README; the packet has no per-organization screen log): tier A was screened in full (ORG-000087, 000508, 001892: **reached, no sentence surfaced**); tier C was never reached (ORG-000157: **not reached**); tier B was screened in full only to rank 103 by employee band then ID, and all six B organizations here have a blank band, so **cannot tell** (000043, 000469, 001380, 001422, 001504, 002136). All 3 applies are in the "cannot tell" tier B group. The three tier A organizations MKT3 did read all stayed held, so the canary gives no sign that MKT3 missed readable sentences in tier A.

## Verdicts and terms (all tier B; one value = one evidence row, all supports_A narrative sentences)

| Org | Verdict | `markets_served` | Evidence | Source |
|---|---|---|---|---|
| ORG-000043 Alterra Energy | VERIFIED | plastics_rubber_processors; chemical_mining_metals_processing | EVD-396200, 396201 | live: alterra360.com/faqs (linked from the stored home page): "This Circular Oil is used by our partners—global leaders in plastics and chemicals—to replace virgin, fossil-derived oil." |
| ORG-001504 Theken Companies | VERIFIED | medical_device | EVD-396202 | stored: nextsteparthropedix.com/about: "NextStep Arthropedix is a division of the Akron-based Theken Companies. Our team is focused on the design and development of orthopedic joint implants." |
| ORG-002136 Kongsberg Automotive | VERIFIED | automotive_oem | EVD-396203 | stored: kongsbergautomotive.com/products-services/: "...products for the passenger car, commercial vehicle, and off-highway markets. Our innovations offer car makers easy integration..." |

Term table. `automotive_oem` only because the quote runs through "car makers" (a quote ending at "markets." supports only `automotive_unspecified`); off-highway, Aftermarket and Industrial Hoses are not tagged. `medical_device` for implants is by meaning ("orthopedic joint implants"); `check.py` adds `implant` to MKT3's `medical_device` wording pattern for this reason, and no other §3.3 term fits a maker of joint implants. `plastics_rubber_processors` and `chemical_mining_metals_processing` are the literal words "plastics" and "chemicals" for partners who use the product; Alterra's mapping of "plastics" to the processors term is the least certain of the four (a plastics producer is not strictly a processor), so a reviewer who disagrees can drop that one row without touching the rest.

Holds (7 organizations, `STILL_UNCERTAIN`; settling facts in `verdicts.csv`; none is a finding of absence):

| Reason | Orgs |
|---|---|
| no_market_claim | ORG-000087 Rainbow Rubber Extrusions |
| scope_owner_ruling | ORG-000157 GrafTech (watchlist-for-exclusion, owner ruling pending; stored pages name steel only in an employee-profile line and a /news/ release) |
| no_vocab_market | ORG-000469 Northeastern Plastics International (printed PVC cards) |
| off_vocabulary_or_ambiguous_market | ORG-000508 Polymer 5 ("every market segment"); ORG-001892 Schibley ("Coatings, Polymer and Composite markets") |
| menu_or_nav_only | ORG-001380 Bauer Corporation ("CATV & Utility Ladders" menu and catalog titles) |
| group_or_redirect_attribution | ORG-001422 Elster Perfection (record website is Honeywell Process Solutions; its pages never name Elster Perfection) |

## Writes (rule 13) and outcome check

- Only `markets_served` changed, on 3 organization rows, each blank at base: `data/organizations_OH.csv` 2 cells (Alterra 2 values, Theken 1), `data/organizations_INTL.csv` 1 cell (Kongsberg). 4 evidence rows appended: `evidence_organizations_OH.csv` 3, `evidence_organizations_INTL.csv` 1, IDs EVD-396200 to 396203 of the block 396200-396299, via `scripts/shard_io.py` `append_sorted`. `check.py` compares every data file with base: nothing else changed.
- Outcome: `python3 S/harness/pic18_unknown.py "$PWD" <ref>`. Unit: PIC-18 organization rows (794). At merge-base `200859b5`: `mkt_unknown=383 (48.2%)`. At HEAD: `mkt_unknown=380 (47.9%)`. **It fell by exactly 3, the number of organizations applied.** `proc_unknown` (331) and `band_unknown` (445) unchanged.

## Live fetches (rule 14)

13 fetches, all of URLs linked from a stored page of the same organization (`fetches.csv` records the linking page), through the shared `scripts/site_corpus.py` (robots-aware), cached under `S/persist/pic18-market-canary-2026-11-18/` with sha256. No organization exceeded 6. Result: 1 apply (Alterra FAQ); the Bauer, Polymer 5, Rainbow, Northeastern and Alterra's other pages added no claim. The two Polymer 5 pages print a personal sales address, so their blobs, per-URL records and index rows were deleted (rule 9) and `fetches.csv` keeps status only (`retained=purged_personal_contact`); the cache was then scanned for non-generic addresses and none remain.

## Self-refute (rule 15)

- self-refute: grain — 4 rows checked, 0 changed. Kongsberg's page is group-wide, and the record is the group (HQ Kongsberg, Norway), so organization grain; Theken's page is a division of the record's own legal entity and no NextStep, Arthropedix or other organization record exists (checked every shard); no site row is written.
- self-refute: founding — 0 rows checked (no founding or age value written), 0 changed. Theken's History page was not used: it lists sold companies and VisionAir (a separate record).
- self-refute: strength — 4 rows checked, 1 changed. All four are narrative sentences (supports_A) and `witness_class.nav_only` is false for each raw page; the one change is Bauer's "CATV & Utility Ladders" entries, which I first read as a telecom lead and held as menu/catalog titles (supports_C).
- self-refute: truncated quote — 4 rows checked, 1 changed. Kongsberg's quote was extended through "car makers", the words that carry OEM; the others end at sentence ends that include the claim words.
- self-refute: attribution — 10 organizations checked, 2 changed. Elster Perfection held because its record website is the Honeywell group portal (a parent page); GrafTech held on scope and on an employee-profile line, not a corporate sentence.

## Named checks

- `python3 tasks/pic18-market-canary-2026-11-18/check.py`: PASS. Injected defects each refused for their own reason: term not in the vocabulary, quote not found in its stored page, tag broader than the words, raw hash tampering, duplicate proposal, frame ID with no verdict, frame ID with two verdicts, hold with a blank settling fact, write to a non-blank cell, write to another column (10/10).
- `build.py`: idempotent (replay leaves the data diff byte-identical). `python3 scripts/validate.py`: 0 errors. `python3 scripts/check_row_loss.py --base origin/main`: OK. `python3 scripts/export_vocab.py --check`: current. `python3 -m unittest discover -s scripts -p 'test_*.py'`: see PR body (no script touched).
- Reuse: `witness_class.py` is imported from MKT3's folder, not copied; MKT3 committed no extractor, so the market sentences were found by reading the stored pages (a keyword sentence filter plus a full read of each page's content area).

## Not checked

Family review. Source presence does not prove semantic fit; `verdicts.csv` is the reviewable judgment. GrafTech's pages are reader-route text with no DOM check (it is held anyway). No site-level markets. The frame is 10 organizations: the yield has a wide interval and the three tier A organizations were all held, so the tier mix of the remaining 191 is not the tier mix here.

## Proposed follow-ups (not in this PR)

- Owner ruling under B-MARKETS-VOCAB: whether polymer/composite fabricators map to `plastics_rubber_processors` (Schibley), and a term for printed cards (Northeastern).
- Owner ruling on carbon/graphite scope (GrafTech) before any markets value is written to it.
- Elster Perfection: a record-specific own page; the record website points at the parent portal.
