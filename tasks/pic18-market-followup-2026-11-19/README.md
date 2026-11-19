# PIC-18 market follow-up (owner rulings 2026-11-19 M1 and M2): 4 of 14 organizations' `markets_served` filled (6 values), 10 held

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

**4 of 14 filled (29%); 95% Wilson interval 12% to 55%.** Counted separately: **4 organizations, 4 distinct witness URLs, 4 distinct quoted passages, 6 values**. Tiers: B 3, C 1. 2 from stored pages, 2 only after a live fetch of a page linked from a stored page (rule 14). M1 applies: 3 of 13; M2: Myrava. Evidence IDs EVD-397377 to EVD-397382 (allocated from one above the maximum across `data/evidence_*.csv` at the base, EVD-397376, owner ruling E1).

## Applied (every quote a narrative sentence or a content-page markets list, supports_A; no group-wide claim is attributed)

| Organization (tier) | `markets_served` | Evidence (EVD- numbers) | Source and quote | Basis |
|---|---|---|---|---|
| ORG-000119 Mechanical Rubber Ohio LLC (B) | rail_transportation; general_industrial | 397377-397378 | live: www.mechanicalrubber.com/mechanical-rubber-ohio/: "Durox Extrusions Request For Quote OEM & Custom Profiles Locomotive, Transit, Vehicle, Off-Road & Industrial Markets" | M1: The fetched page is titled and addressed "Mechanical Rubber Ohio" (URL /mechanical-rubber-ohio/) and its heading names the facility's product brand Durox Extrusions; the record's trade name is Mechanical Rubber and its site is mechanicalrubber.com. |
| ORG-001558 Myrava, LLC (C) | medical_device | 397379 | stored: myrava.com/: "Empowering clinicians with FDA-cleared, patient-specific medical devices and point-of-care manufacturing solutions ​that can help improve care , enhance efficiency , and support better outcomes" | M2: own site; the note caps the tier only, which stays C |
| ORG-001949 Akron Steel Fabricators Co. (B) | tire_rubber_goods; plastics_rubber_processors | 397380-397381 | live: polinggroup.com/company_info_asf: "ASF has been recognized as an innovator throughout the tire and rubber industries." | M1: The fetched page is the ASF Division page of the Poling Group site ("The History of ASF-Akron Steel Fabricators"); ASF is the record's name and division. |
| ORG-004022 VMI Holland B.V. (B) | pharmaceutical_biotech | 397382 | stored: www.vmi-group.com/: "VMI Care creates automatic systems for the pharmaceutical industry." | M1: The site is published by the record itself ("© Copyright VMI Holland B.V"); the record's trade names are VMI Group and VMI, and the card names VMI Care, a VMI business line. |

Term notes. `rail_transportation` for "Locomotive, Transit" and `general_industrial` for "Industrial Markets" (Durox Extrusions' line on the Mechanical Rubber Ohio page; "Vehicle" and "Off-Road" name no section 3.3 term). `tire_rubber_goods` and `plastics_rubber_processors` for "the tire and rubber industries" (ASF builds rubber-processing machinery for them). `pharmaceutical_biotech` for "the pharmaceutical industry". `medical_device` for Myrava's "FDA-cleared, patient-specific medical devices".

## Holds (10 organizations, `STILL_UNCERTAIN`; settling facts in `verdicts.csv`; none is a finding of absence)

| Organization | Hold class | Why |
|---|---|---|
| ORG-000438 Mexichem Specialty Resins Inc. | no_market_claim | M1 re-screen: the fetched Vestolit region page names the Avon Lake plant and Mexichem Specialty Resins, Inc. (a pilot plant for dispersion, blending, powder coating and specialty suspension vinyl resins, and "market needs for new product development") but names no customer industry or product market; the stored pages are the Vestolit group's. |
| ORG-000606 Third Dimension Division | off_vocabulary_or_ambiguous_market | M1 re-screen: the fetched GBP Third Dimension Division page names the division as the subject ("we operate six facilities in Ohio ... custom displays, promotional and protective packaging solutions, and warehousing services"), so attribution is met; no section 3.3 term fits unqualified packaging (consumer, industrial and food and beverage packaging are separate terms). |
| ORG-000752 Polynt Composites USA, Inc. | group_or_redirect_attribution | M1 re-screen: no stored or fetched Polynt page names Polynt Composites USA, Sandusky or Cook Composites; the market statements ("transportation and construction to electronics and energy"; the composites product page) are group-wide. |
| ORG-001447 Axalta Coating Systems USA LLC | group_or_redirect_attribution | M1 re-screen: no stored page names Axalta Coating Systems USA or Orrville as the subject of a claim; the RV, powersports, aviation, marine and rail and light-vehicle statements are the global group's. |
| ORG-001462 Clevite Elastomers Technical Center (Tenneco) | group_or_redirect_attribution | M1 re-screen: no stored Tenneco page names Clevite or Milan; the markets statements (emissions, bearings, performance solutions) are Tenneco's. |
| ORG-001513 Coltene/Whaledent Inc. | group_or_redirect_attribution | M1 re-screen: the stored pages are the COLTENE Group's ("© COLTENE Group") and never name Whaledent, Coltene/Whaledent or Cuyahoga Falls; COLTENE is the group's brand, so the dental statements are group-wide. |
| ORG-001534 Zimmer Surgical, Inc. | group_or_redirect_attribution | M1 re-screen: the stored Zimmer Biomet pages name Zimmer Surgical only in a contact address (Dover, Ohio); the fetched Surgical specialty page names no subsidiary; the healthcare statements are Zimmer Biomet's. |
| ORG-002047 Wayne-Dalton Plastics (Wayne Dalton Corp) | off_vocabulary_or_ambiguous_market | M1 re-screen: the record's legal name embeds Wayne Dalton Corp and the stored pages speak as Wayne Dalton ("At Wayne Dalton, we strive to accommodate all customers ... garage door styles"), so attribution is met; the stated products (residential garage doors, dock equipment) carry no wording that matches a section 3.3 term (no "building" or "construction"). |
| ORG-003196 Eckart America Corporation | group_or_redirect_attribution | M1 re-screen: the stored ECKART pages name ECKART America only in a certificate list (ISO and policy PDFs); every market statement (coatings, plastics, cosmetics pigments) is the global group's. |
| ORG-003771 ST BlowMoulding USA LLC | group_or_redirect_attribution | M1 re-screen: the stored pages name ST BlowMoulding USA LLC only in address footers; the industrial packaging and automotive statements are the Italian group's. |

## Writes (rule 13) and outcome check

- Only `markets_served` changes, on 4 organization rows, each blank at base: `data/organizations_OH.csv` and `data/organizations_INTL.csv`. 6 evidence rows appended to the matching `evidence_organizations_*.csv`. `check.py` compares every data file with the base and requires each applied row's tier unchanged (Myrava stays tier C).
- Publish order: evidence shards, then organization shards, each staged, verified against the base row counts and replaced atomically; backups are written from `git show ec7e19be:<file>` into `pre-application-batchfollowup-ec7e19be` with sha256 recorded and verified (batch 2's hardened `build.py`).
- Outcome: `python3 S/harness/pic18_unknown.py "$PWD" <ref>` (unit: PIC-18 organization rows, 794). At merge-base `ec7e19be`: `mkt_unknown=319`. At HEAD: `mkt_unknown=315`. **It fell by exactly 4, the number of organizations applied.**

## Live fetches (rule 14)

7 fetches, each of a URL linked from a stored page of the same organization (`fetches.csv` records the linking page), through `scripts/site_corpus.py` (robots-aware), cached under `S/persist/pic18-market-followup-2026-11-19/` with sha256: Mechanical Rubber Ohio, Third Dimension Division, Vestolit US region sites, Poling ASF Division, Zimmer Biomet Surgical, Polynt Composites, Zatkoff (fetched before the controller took ORG-000169 out of M1 scope; unused). 2 applied (Mechanical Rubber Ohio, ASF). No organization exceeded 1.

## Self-refute (rule 15)

- self-refute: grain — 4 organizations checked, 0 changed. Every claim sits on a page that names the subject: the Mechanical Rubber Ohio facility page (and its Durox Extrusions brand), the ASF Division page, VMI's own site (published by VMI Holland B.V.), Myrava's own site. The writes are organization-grain; Mechanical Rubber's group address (Warwick, NY) is not used.
- self-refute: founding — 4 rows checked, 1 changed. The ASF quote first began "Established in 1946, ..."; it now begins at "ASF has been recognized ..." and no founding year is written.
- self-refute: strength — 6 values checked, 0 changed. Held: none for strength. The two judgment calls: the Durox line "OEM & Custom Profiles Locomotive, Transit, Vehicle, Off-Road & Industrial Markets" is a content-page markets line (the controller's ruling treats a content-page markets list as supports_A), `witness_class.nav_only` finds it outside chrome; VMI Care's card sentence is a complete sentence.
- self-refute: truncated quote — 6 values checked, 0 changed. Each quote ends at its claim words.
- self-refute: attribution — 14 organizations checked, 10 held. The M1 subject test is a check (`subjects.csv`: the quote must contain a name of the subsidiary, brand or plant, with the basis), not a reading: Polynt, Axalta, Clevite, COLTENE, Zimmer Surgical, ECKART and ST BlowMoulding stay held because no page names the subsidiary as the subject of a market claim; Vestolit's Avon Lake and Wayne Dalton name the subject but state no market in section 3.3 words; Third Dimension names the division but no single packaging term fits.

## Named checks

- `python3 tasks/pic18-market-followup-2026-11-19/check.py`: PASS with the boundary check; reuses batch 2's injections (frame count and identity, term, quote, hashes, duplicate, hold without a settling fact, tier effect, read basis, tag wording, OEM wording, new ID above the base maximum, retired ID reuse, falsified evidence provenance in the shard and the packet, backups: stale base, 128-byte truncated, replay, third apply, retry after the first canonical evidence write, unsafe write order, renumber replay) and adds: **a group-wide claim attributed to a subsidiary** (a record whose quote does not name its subject is refused), **an out-of-scope organization swapped into the frame**, **the Myrava tier changed** (in the verify step and in the data write), and a `group domain witness` for a record with no named subject. The do-not-promote assertion is lifted only for the M2 record.
- `build.py` is idempotent. `scripts/validate.py` 0 errors; `check_row_loss.py --base origin/main`, `export_vocab.py --check` and `python3 -m unittest discover -s scripts -p 'test_*.py'`: see the PR description.

## Not checked

Family review. Holds were screened by name search over stored pages and the 7 linked fetches; other group-site pages that might name a subsidiary were not crawled. No site-level markets.

## Proposed follow-ups (not in this PR)

- Polynt, Axalta, Clevite/Tenneco, COLTENE, Zimmer Biomet, ECKART and ST BlowMoulding: a subsidiary-specific page (a US plant or product-line page naming the Ohio entity) would settle each.
- Wayne Dalton ORG-002047: a sentence naming the building or construction trade in words that match a section 3.3 term.
