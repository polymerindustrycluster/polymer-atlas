# PIC-18 market canary, 2026-11-18: 10 organizations MKT3 left `not_adjudicated`

Claim: atlas-w18-mktcanary (controller thr_9i2c6byhcz). First user: the Atlas owner, for prospecting by market; non-use is a finding if no prospecting list uses `markets_served` by 2026-12-16. No issue closed. Family review is pending.

## Question and answer

Can `markets_served` still be filled from stored own-site pages for PIC-18 organizations MKT3 (PR #360, `tasks/pic18-markets-3-2026-11-16/`) left `not_adjudicated`? **4 of the 10 organizations filled; 3 from stored pages alone and 1 (Alterra) only after a live fetch of an own-site page linked from the stored home page.** Six are held, one of them (GrafTech) gated on an owner ruling. n = 10, so the 95% Wilson interval for 4/10 is 17% to 69% (3/10 stored-only: 11% to 60%). The scale-up bar (3 or more apply and the refute is clean) is met on the count with or without the live fetch; the refute of this revision has not run. (Revision 2 after Gemini's refute of 76459c47: Schibley moved from held to applied. Revision 3 after Codex's refute of 61a89d91: Alterra's `plastics_rubber_processors` value withdrawn; the organization stays applied on `chemical_mining_metals_processing`, so the count is still 4 organizations, now 4 values.)

## Frame, unit and filter

Frame: the 10 organizations drawn by the controller (seed 20261118): ORG-000043, 000087, 000157, 000469, 000508, 001380, 001422, 001504, 001892, 002136. `check.py` recomputes, independently of the verdict table, that each is blank at base `15f2b154`, is `not_adjudicated` in MKT3's `holds.csv`, and has at least one stored text page of 1 KB or more in the pinned MKT3 manifest snapshot. Tiers: A 3 (000087, 000508, 001892), B 6, C 1 (000157).

MKT3 reached vs not, derived by `build.mkt3_reach` and rechecked by `check.py` from MKT3's own ordering (tier A all screened in full; tier B the first 103 of 175 by Ohio employee band then organization ID, using MKT3's base `d410968`; tiers C and U not reached). Blank bands may sort before or after banded rows, so each blank-band organization gets a rank range: ORG-000043 ranks 4-42 and ORG-000469 ranks 43-81 (both **screened in full**, nothing surfaced); ORG-002136 ranks 126-164 (**stricter filter only**, so its market sentence was never in front of a reader); ORG-001380, 001422, 001504 are inconclusive (**cannot tell**). Tier A (000087, 000508, 001892): **screened in full**; tier C (000157): **not reached**. Reach counts: screened in full 5, stricter filter only 1, not reached 1, cannot tell 3. Of the 4 applies, Alterra (screened) and Schibley (tier A, screened) were reached and not applied by MKT3 (Alterra's sentence is on a page that was not in the stored set; Schibley's sentence is on a stored page and was missed or left unadjudicated), Kongsberg was only filter-screened, and Theken is inconclusive. Screened is the screen MKT3 ran, not a claim that a reader read every page.

## Verdicts and terms (one value = one evidence row, all supports_A narrative sentences)

| Org | Verdict | `markets_served` | Evidence | Source |
|---|---|---|---|---|
| ORG-000043 Alterra Energy | VERIFIED | chemical_mining_metals_processing (plastics_rubber_processors withheld) | EVD-396200 | live: alterra360.com/faqs (linked from the stored home page): "This Circular Oil is used by our partners—global leaders in plastics and chemicals—to replace virgin, fossil-derived oil." |
| ORG-001504 Theken Companies | VERIFIED | medical_device | EVD-396201 | stored: nextsteparthropedix.com/about: "NextStep Arthropedix is a division of the Akron-based Theken Companies. Our team is focused on the design and development of orthopedic joint implants." |
| ORG-002136 Kongsberg Automotive | VERIFIED | automotive_oem | EVD-396202 | stored: kongsbergautomotive.com/products-services/: "...products for the passenger car, commercial vehicle, and off-highway markets. Our innovations offer car makers easy integration..." |
| ORG-001892 Schibley Solvents and Chemicals (tier A) | VERIFIED | plastics_rubber_processors | EVD-396203 | stored: schibley.com/ (home page): "We are an independent distributor of raw material chemicals that has been servicing the Fiberglass Reinforced Plastics, Coatings, Lubricants, Adhesives and the Household, Industrial & Institutional market segment for almost 100 years." Only the plastics segment maps to a §3.3 term. |

Term table. `automotive_oem` only because the quote runs through "car makers" (a quote ending at "markets." supports only `automotive_unspecified`); off-highway, Aftermarket and Industrial Hoses are not tagged. `medical_device` for implants is by meaning ("orthopedic joint implants"); `check.py` adds `implant` to MKT3's `medical_device` wording pattern for this reason, and no other §3.3 term fits a maker of joint implants. `chemical_mining_metals_processing` is the literal word "chemicals" for partners that use Alterra's circular oil. Alterra's `plastics_rubber_processors` value was withdrawn after Codex's refute: the FAQ describes petrochemical feedstock use, a chemical-processing customer, and no stored or linked page names a customer that processes plastic or rubber into parts or products; the settling fact is in `verdicts.csv`. Schibley's `plastics_rubber_processors` rests on its literal "Fiberglass Reinforced Plastics" segment.

Holds (6 organizations, `STILL_UNCERTAIN`; settling facts in `verdicts.csv`; none is a finding of absence):

| Reason | Orgs |
|---|---|
| no_market_claim | ORG-000087 Rainbow Rubber Extrusions |
| scope_owner_ruling | ORG-000157 GrafTech (watchlist-for-exclusion, owner ruling pending; the stored home page does name steelmaking customers in corporate sentences, so scope, not evidence, is what holds it) |
| no_vocab_market | ORG-000469 Northeastern Plastics International (printed PVC cards) |
| off_vocabulary_or_ambiguous_market | ORG-000508 Polymer 5 ("every market segment") |
| menu_or_nav_only | ORG-001380 Bauer Corporation ("CATV & Utility Ladders" menu and catalog titles) |
| group_or_redirect_attribution | ORG-001422 Elster Perfection (record website is Honeywell Process Solutions; its pages never name Elster Perfection) |

## Writes (rule 13) and outcome check

- Only `markets_served` changed, on 4 organization rows, each blank at base: `data/organizations_OH.csv` 3 cells (Alterra, Theken, Schibley), `data/organizations_INTL.csv` 1 cell (Kongsberg). 4 evidence rows appended: `evidence_organizations_OH.csv` 3, `evidence_organizations_INTL.csv` 1, IDs EVD-396200 to 396203 of the block 396200-396299, via `scripts/shard_io.py` `append_sorted`. `check.py` compares every data file with base: nothing else changed.
- Outcome: `python3 S/harness/pic18_unknown.py "$PWD" <ref>`. Unit: PIC-18 organization rows (794). At merge-base `15f2b154`: `mkt_unknown=383 (48.2%)`. At HEAD: `mkt_unknown=379 (47.7%)`. **It fell by exactly 4, the number of organizations applied.** `proc_unknown` (331) and `band_unknown` (445) unchanged.

## Live fetches (rule 14)

13 fetches, all of URLs linked from a stored page of the same organization (`fetches.csv` records the linking page), through the shared `scripts/site_corpus.py` (robots-aware), cached under `S/persist/pic18-market-canary-2026-11-18/` with sha256. No organization exceeded 6. Result: 1 apply (Alterra FAQ); the Bauer, Polymer 5, Rainbow, Northeastern and Alterra's other pages added no claim. The two Polymer 5 pages print a personal sales address, so their blobs, per-URL records and index rows were deleted (rule 9) and `fetches.csv` keeps status only (`retained=purged_personal_contact`); the cache was then scanned for non-generic addresses and none remain.

## Self-refute (rule 15)

- self-refute: grain — 4 rows checked, 0 changed. Kongsberg's page is group-wide, and the record is the group (HQ Kongsberg, Norway), so organization grain; Theken's page is a division of the record's own legal entity and no NextStep, Arthropedix or other organization record exists (checked every shard); no site row is written.
- self-refute: founding — 0 rows checked (no founding or age value written), 0 changed. Theken's History page was not used: it lists sold companies and VisionAir (a separate record).
- self-refute: strength — 4 rows checked, 1 changed. All four are narrative sentences (supports_A) and `witness_class.nav_only` is false for each raw page; the one change is Bauer's "CATV & Utility Ladders" entries, which I first read as a telecom lead and held as menu/catalog titles (supports_C).
- self-refute: truncated quote — 4 rows checked, 1 changed. Kongsberg's quote was extended through "car makers", the words that carry OEM; the others end at sentence ends that include the claim words.
- self-refute: attribution — 10 organizations checked, 4 changed (the fourth: Alterra's customer type, below). Elster Perfection held because its record website is the Honeywell group portal (a parent page); GrafTech held on scope only (an earlier note wrongly said its stored pages named steel only in an employee line and a news release; corrected); Schibley's quote was first attributed to the wrong stored page (strong-link, not home) and is now the home-page sentence, quoted exactly. Alterra's FAQ names a chemical-processing customer, not a plastic or rubber processor, so that value was withdrawn (Codex 24 finding 1).

## Named checks

- `python3 tasks/pic18-market-canary-2026-11-18/check.py`: PASS. Injected defects each refused for their own reason (18): term not in the vocabulary, quote not found in its stored page, tag broader than the words, raw hash tampering, text digest of the wrong bytes, duplicate proposal, frame ID with no verdict, frame ID with two verdicts, hold with a blank settling fact, tampered verdict value, value on a hold, wrong MKT3 reach basis, write to a non-blank cell, write to another column, interrupted shard write (shards intact, retry and replay succeed, no temp sibling left), occupied evidence ID (no market cell written), truncated input shard (an organization shard or an evidence shard with one row removed: nothing replaced), and scrub (no per-URL record or index row left). Text digests are of the stored file bytes (revision 3 fix; the earlier digests hashed `read_text()` output).
- `build.py`: idempotent (replay leaves the data diff byte-identical). `python3 scripts/validate.py`: 0 errors. The builder stages each changed shard as a temp sibling and `os.replace`s it only after refusing any occupied evidence ID and asserting each staged shard's row count equals its count at the merge-base (`git show 15f2b154:data/<shard>`) plus the rows the packet adds to it (organization shards +0, evidence shards + the packet's rows for that shard). It does not otherwise validate the input shards, and the base is a fixed constant, so replaying after main changes these shards needs the constant updated. `python3 scripts/check_row_loss.py --base origin/main`: OK. `python3 scripts/export_vocab.py --check`: current. `python3 -m unittest discover -s scripts -p 'test_*.py'`: 335 tests OK (1 skipped); no script was touched.
- Reuse: `witness_class.py` is imported from MKT3's folder, not copied; MKT3 committed no extractor, so the market sentences were found by reading the stored pages (a keyword sentence filter plus a full read of each page's content area).

## Not checked

Family review. Source presence does not prove semantic fit; `verdicts.csv` is the reviewable judgment. GrafTech's pages are reader-route text with no DOM check (it is held anyway). No site-level markets. The frame is 10 organizations: the yield has a wide interval and tier A is only 3 of the 10, so the tier mix of the remaining 191 is not the tier mix here.

## Proposed follow-ups (not in this PR)

- Owner ruling under B-MARKETS-VOCAB: a term for printed cards (Northeastern).
- Owner ruling on carbon/graphite scope (GrafTech) before any markets value is written to it.
- Elster Perfection: a record-specific own page; the record website points at the parent portal.
