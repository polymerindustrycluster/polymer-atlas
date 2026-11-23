# Blind audit 12: protocol (ATLAS-7, the P1 exit test)

Status: **DRAFT until the owner answers the battery in section 9.** The sample is not drawn now. It is drawn once, at P1 exit,
by `draw.py` against a recorded `origin/main` SHA, so no fix can aim at it. Nobody who writes this protocol or fixes data sees the
seed; the controller holds it. Sealing = the controller records, in the ledger and before the draw, the sha256 of this file, of
`draw.py`, of `sizes.json`, and the `--at` SHA. The seed file's sha256 is **`5144840e29ac8aad7204812bf272282ffe0e39a2ce6bb6ba795d4d35f68d3df3`**;
`draw.py` holds it as a constant, has no flag that changes it, and refuses a seed file that hashes differently.

## 1. What the owner ruled (DECISIONS.md, 2026-11-23; quoted)

- Round 17: "The unit is the record: a sampled record is wrong if any published field it carries is wrong. The whole-Atlas blind
  audit is stratified by region. PIC-18 is good enough to publish when the 95% Wilson upper bound of its record error rate is at most 5%;
  the rest of Ohio and the rest of the country, at most 10%. At a true error rate of 2% the PIC-18 bound needs about 205 effective records
  read, and at 3% about 460; at 10%, about 55 to 71 per region (continuous Wilson bound at the assumed rate)."
- Round 18: "researchers (people records), programs, and events with their participation rows are each a stratum of blind audit 12, held to
  the same unit as the round 17 target (a sampled record is wrong if any published field on it is wrong) at a 95% Wilson upper bound of 10% or less."
- Round 17: "Process and market cells that no admissible source fills are published as unknown." An empty cell is not a published claim,
  so an omission is never an error (section 4); it is counted and reported separately.

Six strata, so six decisions. `PIC18_RECORDS` at 5%; `REST_OHIO_RECORDS`, `REST_US_RECORDS`, `RESEARCHERS`, `PROGRAMS`, `EVENTS` at 10%.
P1 exits when all six PASS under section 8. One failed stratum is a failed audit; the fix is a new audit with a **new** seed and a new
sealed hash (this seed is spent by its draw).

## 2. Frames (what is drawn from)

The frame is built from the CSVs at the `--at` SHA, read by `git show <SHA>:`, never the working tree. `--at` must be a full SHA that
is an ancestor of `origin/main`. `python3 draw.py frame --at <SHA>` prints the frame without a seed and fails on any broken invariant.

| stratum | records pooled in it (unit: record) | filter (all rows of the table that match) |
|---|---|---|
| `PIC18_RECORDS` | `organizations`, `ecosystem` and `sites` rows placed in PIC-18 by section 2.1 | sites: `operating_status=active`, tier A-C. Organizations and ecosystem rows: `status=active`, tier A-C, **or** owner of a frame site (B2) |
| `REST_OHIO_RECORDS` | the same three tables, placed in Ohio outside PIC-18 | same |
| `REST_US_RECORDS` | the same three tables, placed anywhere else, non-US rows included | same |
| `RESEARCHERS` | `people` rows | `status` blank or `active`, tier A-C |
| `PROGRAMS` | `programs` rows | `status=active`, tier A-C |
| `EVENTS` | `events` rows and `event_participation` rows pooled | events: `status=active`, tier A-C. Participation rows: tier A-C and their event in the frame |

These are the published headline cuts: the site's index cards use "operating status active; verification tiers A-C" for sites and
organizations, "status active" for programs, and `scripts/regions.py` (PIC-18) for the region. Tombstoned, closed, `unknown`-status and
tier-U records have public pages too and are **not** in the frame (B1). Every exclusion is counted by reason in `draw_receipt.json`, and
the report states that the bounds say nothing about excluded records.

**2.1 Region (a record is in exactly one stratum).** Sites: `country` not US -> rest of country; else by `state` and `county` (OH and a county in
PIC-18 -> PIC-18; other OH -> rest of Ohio; other states -> rest of country). Organizations and ecosystem rows, by footprint, first match wins:
PIC-18 if the record owns a frame site in PIC-18 or its HQ (`hq_state`/`hq_county`; ecosystem `state`/`county`) is in PIC-18; rest of Ohio if it owns
a frame site in Ohio or its HQ state is OH; else rest of country (B3). `draw.py` **refuses to draw** while any frame record fits no stratum:
an Ohio HQ with a blank county and no positive PIC-18 footprint (whatever else it owns, since its HQ could be in PIC-18), or a record with no state and no site. An organization whose HQ state is blank but which owns frame sites is placed by its sites alone (B3). Nothing is defaulted to a bucket (B6).

**2.2 Reconciliation (AGENTS section 2 rule 10).** `draw.py` asserts, and the selftest plants a failure for each: every table's header is
fully classified (section 3), record IDs are unique in every table and `org_id` never sits in both `organizations` and `ecosystem`, every
site resolves to an owner, every participation row resolves to an event and organization, and for every table rows in the frame minus
owner-added plus excluded equals the table's rows (the release `COUNTS.md` unit: rows). It then runs the site builder's own `active_ab` and
`pic18_active_sites` (`scripts/build_site.py` as of the SHA) on the same site rows and requires equal counts. The README's static counts are dated
to a commit and are not a check. Indicative frame at `1b924786` (not binding; the draw re-derives it): PIC-18 1,928 records (1,010
organizations, 37 ecosystem, 881 sites), rest of Ohio 1,396 (765, 24, 607), rest of country 8,386 (3,102, 291, 4,993), researchers 1,603, programs
251, events 1,722 (98 events, 1,624 participation rows). 31 records fit no stratum there (B6). The site builder's counts at that SHA, 6,481 active
A-C sites, 1,488 in Ohio, 881 in PIC-18, equal the frame's.

## 3. Published fields

"Published" is read from the code, not guessed. Two surfaces: the **site** (`scripts/build_site.py`: organization and ecosystem pages with their
site rows, evidence tables, programs, researchers and equipment; `experts.json`; the map, prospects and county pages; `build_graph.py` and
`build_events_3d.py` for events) and the **release export** (`scripts/export_release.py` copies every `data/*.csv` column verbatim, plus the
generated `*_incl_sites` columns). The release carries every column, including `notes` and `created_by`. Judging builder prose is not a reading
task, so the judged set is the world-fact columns of both surfaces (B8). Each column of each table has exactly one class; `draw.py` fails if a
column at the SHA is missing or unclassified, so a new column cannot slip past the audit.

- **J** judged by a reader. **K** shown as context (IDs, foreign keys resolved to names, the record's own `sources` text with source-read dates
  removed), not judged. **B** judged by binding replay, withheld from readers (2.2 below). **W** withheld, not judged: builder metadata and fields that
  date the pass (`created_by`, `notes`, `last_verified`, `observed_date`, `evidence_date`, `as_of`). **D** derived or generated, recomputed by the integrator and
  not read. **R** reference data. **M** machine-checked by the validator or gate, not read.
- **Derived (D).** `tier1_qualifier*` (AGENTS section 1: refreshed by the derivation, never hand-edited), the ecosystem `polymer_program*` rollups, `last_activity_*`.
  The integrator recomputes them at the SHA with the derivation procedure; a mismatch is a record error (the derivation or its input is wrong). They are not read
  because a reader has nothing to compare them with. `hq_in_scope` is a J field: it is a published claim about the HQ county.
- **Ownership and parent links are judged.** `sites.org_id`, `programs.institution_org_id`, `people.institution_org_id`, `event_participation.org_id`, `equipment.host_org_id`, `registry_links.org_id`, `site_capabilities.org_id` and `code_assignments.org_id` are published assertions ("this site belongs to that operator"): class J, not K. `withdrawn_date` on equipment, capability and engagement rows decides whether the public claim is live: J. Evidence `observed_date` can be a filing's own period date: class B, judged by replay.
- **Release-only and out-of-unit.** The three organization columns `processes_incl_sites`, `materials_incl_sites`, `markets_served_incl_sites` exist only in the release export (`export_release.py`); they are class D, recomputed by the integrator with `build_site.org_field_sources` at the SHA. `code_assignments` is a child table (classified). `ref_codes`, `ref_code_map`, `inclusion_log` and the three `ipeds_*` tables are reference or log tables that no stratum record carries; `draw.py` fails if `data/` holds a table that is neither classified nor named out of the unit (last row of the table below).
- **Reference (R).** `latitude`, `longitude`, `geocode_precision` are "reference data: never evidence" (AGENTS section 1). The map shows them, so strictly they are
  published. Readers do not judge them and they do not decide a record; the report states that coordinates were not audited (B8).
- **2.4 Child rows are judged with the record they hang from.** Evidence rows, `registry_links`, `site_capabilities`, `equipment`, `people_identifiers`,
  `people_engagement`, `archive_links`, `members` and generated `relationships`: a sampled record is wrong if one of its child rows' judged fields is wrong (B9).
  **Evidence rows** (class B) are judged only by replaying the binding gate (`scripts/check_evidence_binding.py`, as of the SHA, against stored captures): a row
  whose quote is not on the cited page, or whose page names a different operator or street, makes the record wrong. The gate compares structured values to the Atlas; its PASS does not show that the raw filing contains the quote, so **a PASS is necessary, not sufficient**: each evidence row's quote is also replayed against the stored page (ordered words), or read independently. **An in-scope child that cannot be settled** (not replayable, page unreachable, quote not replayed) **marks its parent UNRESOLVED, once however many children are unsettled**, so it enters u and the decision in section 8. It is never silently an AGREE and never an error by itself.

<!-- FIELDS:BEGIN -->
| table | `J` judged by readers | `K` context, not judged | `B` judged by binding replay (integrator) | `W` withheld, not judged | `D` derived/generated, recomputed | `R` reference, not read | `M` machine-checked |
|---|---|---|---|---|---|---|---|
| `organizations` | `legal_name` `trade_names` `parent_org_id` `ultimate_parent_name` `entity_type` `ring_primary` `ring_secondary` `diversified_conglomerate` `hq_city` `hq_state` `hq_county` `hq_country` `hq_in_scope` `naics_primary` `naics_primary_source_type` `naics_primary_source_name` `naics_confidence` `naics_secondary` `processes` `materials` `markets_served` `employee_band_ohio` `website` `description_1line` `status` `status_date` `successor_org_id` `verification_tier` `year_founded` `stock_ticker` `ownership_type` `certifications` `pic_member` `member_since` `membership_source_url` `newsroom_url` `newsroom_feed_url` `linkedin_url` | `org_id` `sources` | — | `pic_relevance` `last_verified` `created_by` `notes` `last_activity_evidence_date` `liveness_signal` `monitor_watch` | `tier1_qualifier` `tier1_qualifier_basis` | — | — |
| `sites` | `org_id` `site_name` `site_type` `city` `state` `zip` `county` `ring_primary` `naics_primary` `naics_primary_source_type` `naics_confidence` `processes` `processes_other_note` `materials` `materials_other_note` `markets_served` `employee_band_site` `operating_status` `verification_tier` `street_address` `country` `site_group_id` | `site_id` `sources` | — | `last_verified` `created_by` `notes` `county_source` | `last_activity_date` `last_activity_source` | `latitude` `longitude` `geocode_precision` | — |
| `ecosystem` | `legal_name` `ecosystem_subtype` `generalist` `services_offered` `geography_served` `city` `state` `county` `website` `description_1line` `status` `verification_tier` `record_grain` `parent_institution_org_id` `public_door_url` `office_name` `tto_url` `industry_partnership_modes` `technology_areas` `pic_member` `member_since` `membership_source_url` `ipeds_unitid` `ror_id` | `org_id` `sources` | — | `pic_relevance` `last_verified` `created_by` `notes` | `polymer_program` `polymer_program_name` `polymer_program_url` | — | — |
| `people` | `full_name` `institution_org_id` `program_org_id` `role` `role_as_published` `research_specialties` `public_profile_url` `lab_url` `verification_tier` `status` `status_date` | `person_id` `sources` | — | `last_verified` | — | — | — |
| `programs` | `institution_org_id` `program_name` `program_type` `credential_types` `level` `cip_code` `cip_source_type` `unit_department` `description_1line` `url` `public_door_url` `first_year_awarded` `last_year_awarded` `latest_completions` `completions_year` `specialty_processes` `specialty_materials` `research_areas` `engagement_modes` `apprenticeship_registered` `employer_custom_training` `admissions_status` `facilities_note` `scale_band` `geography_served` `city` `state` `county` `status` `verification_tier` | `program_id` `sources` | — | `last_verified` `pic_relevance` `created_by` `notes` | — | — | — |
| `events` | `name` `trade_names` `organizer_name` `organizer_org_id` `event_format` `cadence` `cadence_note` `typical_timing` `home_city` `home_state` `home_region` `geography_note` `subject_scope` `subject_note` `event_url` `status` `status_date` `verification_tier` `pic_events_slug` | `event_id` `sources` `status_source` | — | `last_verified` `pic_relevance` `created_by` `notes` | — | — | — |
| `event_participation` | `event_id` `org_id` `edition_year` `edition_name` `role` `role_detail` `edition_dates` `edition_city` `edition_state` `evidence_source_name` `evidence_source_url` `verification_tier` | `participation_id` `sources` | — | `evidence_date` `last_verified` `created_by` `notes` | — | — | — |
| `evidence` | — | `evidence_id` `record_table` `record_id` `claim_type` `source_ref` | `claim_detail` `source_class` `address_role` `observed_date` | `created_by` `notes` | — | — | `tier_effect` |
| `registry_links` | `org_id` `site_id` `registry` `registry_id` | `match_basis` | — | `as_of` | — | — | — |
| `site_capabilities` | `site_id` `org_id` `capability_type` `term` `provenance` `withdrawn_date` | `capability_id` `source_ref` | — | `observed_date` `created_by` `notes` | — | — | — |
| `equipment` | `host_org_id` `site_id` `program_id` `name` `equipment_class` `access_mode` `withdrawn_date` | `equipment_id` `source_ref` | — | `observed_date` `created_by` `notes` | — | — | — |
| `people_identifiers` | `identifier_id` | `person_id` `identifier_type` `match_basis` | — | `as_of` | — | — | — |
| `people_engagement` | `mode` `withdrawn_date` | `engagement_id` `person_id` `source_ref` | — | `observed_date` `created_by` `notes` | — | — | — |
| `code_assignments` | `org_id` `code_system` `code_value` `role` `source_type` `stated_title` | `assignment_id` `source_name` `source_ref` | — | `observed_date` `created_by` `notes` | — | — | — |
| `archive_links` | `archive_ref` `captured_at` | `evidence_id` | — | `created_by` | — | — | — |
| `members` | `org_id` `display_name` `member_tier` `record_class` `member_since` `membership_source_url` `snapshot_date` | `member_row_id` | — | `notes` | — | — | — |
| `relationships` | — | `relationship_id` `from_org_id` `to_org_id` | — | `created_by` `notes` | — | — | `relationship_type` `effective_from` `effective_to` `basis` `source_ref` |
| `organizations` (release export only) | — | — | — | — | `processes_incl_sites` `materials_incl_sites` `markets_served_incl_sites` | — | — |
| out of the unit | `ref_codes` (reference vocabulary (NAICS titles shown on pages are reference data)); `ref_code_map` (code concordance, reference); `inclusion_log` (decision log, builder prose); `ipeds_institutions` (IPEDS reference layer (SCHEMA 4.23)); `ipeds_programs` (IPEDS reference layer (SCHEMA 4.23)); `ipeds_completions` (IPEDS reference layer (SCHEMA 4.23)) | | | | | | |
<!-- FIELDS:END -->

## 4. What is wrong, unknown, or not checkable

A reader judges each **J** field of the record against public sources (AGENTS section 5; licensed sources and the PIC CRM are never evidence). The cited sources
and evidence URLs are a starting point, not the answer: re-fetch raw; a quote counts only if its words appear in order on the page.

| situation | grade |
|---|---|
| Every J value present is supported by a primary or public source, at the grain the record claims (organization or site) and in SCHEMA vocabulary | AGREE |
| At least one J value is false, or no source supports it and a source contradicts it, or it is stated at the wrong grain (a company-wide fact on a site row) | FIELD_ERROR, naming the field, the correct value and a quoted URL |
| The row should not exist: wrong entity, out of scope under SCHEMA, an identifier or link that belongs to someone else | CREATION_ERROR |
| The row duplicates another held record | CREATION_ERROR graded DUPLICATE_OF, naming the target record ID and the chain, which must end at a held record (AGENTS section 2 rule 8); counted in k |
| A value cannot be settled inside the fetch budget, or a source is unreachable | UNRESOLVED (the grammar's STILL_UNCERTAIN), naming the fact that would settle it |
| A cell is empty | never an error: not a claim. Counted as an omission when a primary source plainly states the value |
| A value was true at the SHA's commit date and a dated source shows a change after it | AGREE, noted `drift`. A change that cannot be dated to after the SHA is UNRESOLVED |

Rules that bind every reader (AGENTS section 2 rule 8): at most about 6 primary-source fetches per record (a cap, not a target; a record with many J
values spends them on the values the cited sources do not settle); a failed fetch (403, timeout, bot wall, empty result) is never evidence of absence, closure or
error; before any REJECT for closure run the Form 5500 check; licensed sources are leads only. **Field rules:** `verification_tier` is judged against the record's
evidence under SCHEMA 4.1 and 4.13 (the reader sees each evidence row's claim type and URL, not its `tier_effect`); NAICS is judged for the code *and* the
`naics_primary_source_type` label (a directory repeating a code is `directory_assigned`); employee bands are judged against the cited source and SCHEMA's
band definitions, never a guessed headcount; `processes`, `materials`, `markets_served` are judged per token, and a token with no source at that grain is an error;
`pic_member` against the public PIC member list only; `year_founded`, `ownership_type`, `parent_org_id` against the organization's own disclosure or a public filing;
people: `role_as_published`, `research_specialties` and `public_profile_url` against the institution's own public page; events and participation: `edition_year`,
`role`, `edition_dates`, `edition_city` against the event's own or the exhibitor list's public page (never an exhibitor contact block).
Privacy: no individual's email, direct phone or home address appears in any output; reports give `path:line`, not the value (AGENTS section 6).

## 5. Blindness and the two reading families

Packet = one row per sampled record: `blind_id, stratum, table, record_id, record_label, columns_under_audit, values_json, context_json, cited_sources, evidence_json`,
built **from a whitelist** (J and K columns, class table above) at the SHA, by adapting audit 11's `sample.py` (`Head`, `blind_row`, `leak_scan`; not rebuilt here).
It carries the record and its published fields. It does not carry: evidence rows' `tier_effect`, `claim_detail` or `source_class`; `created_by` (the batch label);
`notes`; any date that dates the pass; PR, lane, packet or ruling words (audit 11's leak scan, which also scrubs source-read dates from `sources`); the stratum's draw rank;
or any history. Row order is a seeded shuffle, not ID order. `blind_a.csv` and `blind_b.csv` are byte-identical.

- **Reader A: Claude Sonnet 5.5. Reader B: OpenAI Codex GPT-6.2 Astra, `--service-tier default`.** Independent: neither sees the other's verdicts, the frame, `sample.csv`,
  the receipts or git history. The ATLAS-7 card names Opus for the reading; **the controller's routing replaces it** (Opus conserved, owner preference 2026-10-26). Hand
  each reader only its blind file and `REVIEWER_INSTRUCTIONS.md` (audit 11's file, with section 4's grades).
- **Locks.** Each reader writes `verdicts.csv` and `receipts.json` outside the repo, locks a sha256 in the ledger, and never edits after.
- **Adjudication (every non-AGREE row).** Both AGREE -> AGREE. Any other row goes to a third, independent read by a family that is neither A nor B (Gemini 4 Hydrogen), blind
  to A and B, on those records only. Two of three agree -> that grade. Three different grades, or a non-AGREE majority without a quoted URL -> the lead re-researches from fresh raw
  fetches (stored hash-named; every quote re-checked as an ordered word sequence; every absence on an HTTP 200 page), as audit 10 and 11 did. **Every FIELD_ERROR and CREATION_ERROR in the
  final grades is lead-verified this way**, whatever the readers said: errors are what fail a stratum.

## 6. Defect plants (a gate against a silent pass)

`draw.py` also writes `plants.csv`: exactly three per stratum, taken from records ranked just past n2 (never sampled ones) or, where the stratum is a census or has no spare records, from published rows of the same tables **outside** the frame (tier U, tombstoned); the draw refuses if a stratum cannot supply three. Each with one J field swapped, in the reading packet only, for the same field of
another record of the same table whose value differs. The packet builder applies them. A reader must flag each plant (FIELD_ERROR or UNRESOLVED on that field). **A reader that misses
more than 2 of the 18 plants has its AGREE verdicts voided** and its records are re-read by another family. Plants never enter a rate. Plants prove a reader looks; they do not prove
it is accurate, and the report says so.

## 7. Draw procedure

```
python3 tasks/blind-audit-12-protocol-2026-11-23/draw.py --selftest        # before anything: must print PASS
python3 .../draw.py frame --at <SHA>                                      # no seed; must show 0 unassignable records
python3 .../draw.py draw --seed-file <controller's path> --at <SHA> --out <new folder>
```

- One binding draw. The controller records the `--at` SHA and the sha256 of this file, of `draw.py` and of `sizes.json` in the ledger **before** running, and passes them as `--expect-protocol-sha256`, `--expect-draw-sha256` and `--expect-sizes-sha256`; `draw.py` refuses if any differs from the file it is running with. The plan (n1, n2, target) is read from the committed `sizes.json`, which must equal what `sizes.py` computes, so no executable-only plan can run. **A fresh `--out` folder is not a global one-draw lock: the lock is the ledger.** The controller records the draw once, keeps `draw_receipt.json`, and treats a second draw against the same seed as a protocol violation. Output files are written owner-only (mode 0600, folder 0700) because they hold both stages; the controller keeps them private and hands readers only stage-1 blind packets.
- Per stratum: one seeded permutation of the frame's `table|id` keys (sorted ascending, then `random.Random(int(SHA256(seed|SHA|stratum))).shuffle`). **Stage 1 = ranks 1..n1; stage 2 =
  ranks 1..n2: a prefix**, so extending never re-draws. The controller releases stage-1 rows; stage-2 rows stay with the controller until section 8 says to read them.
- Outputs: `frame.csv`, `sample.csv` (stratum, rank, stage, table, record_id, region basis, stratum N, census flag), `plants.csv`, `draw_receipt.json` (SHA, seed **sha256** only, `draw.py`/
  `sizes.json`/protocol sha256, plan, reconciliation, file hashes). The seed text is in no output.
- Selection is simple random within the stratum over its pooled records, so inclusion probability is equal and **the effective n is n** (Kish factor 1). **Census branch.** A stratum with N at most n2 is a census: all N records are released and read in one stage (stage 1 = everyone), the ordinary early, futility and final cutoffs of section 8 do **not** apply to it, and nothing is decided until every record is read. The decision is then exact: **PASS iff (k+u)/N is at most the stratum's target**, no interval (an interval would add sampling error a census does not have). No finite-population correction is applied; the bound is conservative for the small strata.
- Grades are against the values **at the SHA**. Data merged after it is not corrected during the audit; corrections are listed and applied afterwards by PR.

## 8. Stopping and the decision (pre-registered; numbers in `sizes.json`, made by `sizes.py`)

k = records graded wrong (FIELD_ERROR + CREATION_ERROR after adjudication); u = records still UNRESOLVED after adjudication; n = records read in the stratum. The decision uses
the **conservative** count k+u (an unresolved record is treated as wrong): **At the final look, PASS iff the Wilson upper bound of (k+u)/n is at most the stratum's target.** The report also gives the bound at k alone. (This is a final-look rule: at stage 1 the three rules below govern, so for example 1 unresolved of 55 meets the ordinary bound but still reads stage 2 because it is above `early_k`.)
Bound = two-sided 95% Wilson, z = 1.959964. For a non-census stratum, stage 1 reads n1, then:

1. k+u at or below `early_k`: PASS now (judged at z = 2.326, so the early look cannot raise the false-pass chance);
2. k+u at or above `futile_k`: FAIL now (the chance stage 2 could pass, at a true 2% rate, is under 5%);
3. otherwise read to n2, and PASS iff k+u is at most `final_k` (the ordinary 95% bound at n2). **No third look, no extension, no re-draw, no dropping records.**

| stratum | target | n1 | n2 | early_k | futile_k | final_k | P(pass), true 2% | P(pass), true 3% | false pass at true = target |
|---|---|---|---|---|---|---|---|---|---|
| PIC18_RECORDS | 5% | 205 | 460 | 2 | 12 | 13 | 92% | 49% | 1.7% |
| each 10% stratum (x5) | 10% | 55 | 110 | 0 | 5 | 4 | 93% | 77% | 1.4% |

**Sizes recomputed with code (`sizes.py`, continuous Wilson bound at k = rate x n), against DECISIONS.md:** 5% target at true 2%: **203** (ruling 205); at 3%: **457** (ruling 460); 10% target at
2%: 55 (55); at 3%: 71 (71). The lane brief also listed "35 at 1%" for the 10% strata; DECISIONS.md states no figure at 1%. The recomputed 1% size is **43**; 35 is the zero-error size (0 errors in 35 gives a bound of 10%). Differences are reported, not
silently used: the plan keeps the ruling's 205/460 and 55/71, which are within 3 records of the recomputation. These sizes put the bound **at** the target when the observed rate equals the assumed one, so
they are not 95%-pass sizes: at a true 3%, PIC-18 passes about half the time and each 10% stratum about two times in three (B10).

- The probabilities above are binomial-model values; the draw samples without replacement, so the exact (hypergeometric) chance of a false PASS is lower (for example 0.84% at 26 wrong of 251 programs). The limits stay conservative on the checked frames.
- No optional stopping: the stage sizes, `early_k`, `futile_k`, `final_k` and the decision statistic are fixed here; nobody picks a bound after seeing data. The reported bound at the stopping look is the
  nominal 95% Wilson bound; the table above gives the exact chance of a false PASS for the whole rule (below the 2.5% one-sided level of a 95% bound in every stratum).
- Report, per stratum: N, n read, k, u, the bound at k and at k+u, effective n, the stage that decided, plants caught per reader, omissions, evidence rows replayed / not replayable, exclusions by reason.
  Per-table rates inside a pooled stratum are descriptive and decide nothing. Counts name their unit and filter (AGENTS section 7).

## 9. Owner battery (not settled here; AGENTS section 2 rule 9). The protocol is sealed only after these are answered; `draw.py` implements the recommended defaults

**Answered 2026-11-23 (owner round 20, multiple choice, DECISIONS.md):** B1-B9 "Accept all defaults" as recommended below;
B10 "Raise to 110": each 10% stratum reads n2 = 110 (the table in section 8 shows the plan in force; the ruling's 71 is kept
in `sizes.py` RULING for the record). The protocol is sealed with these answers.

| id | question | recommendation | changes the draw? |
|---|---|---|---|
| B1 | Which records are in the frame: the published headline cut (active, tiers A-C) or every published page, tombstoned, `unknown` and tier-U included? | Headline cut. Excluded at `1b924786`: 170 organizations, 33 ecosystem, 715 sites (389 of them active tier U), 11 people, 2 programs. Bounds then say nothing about those | yes |
| B2 | Owners of a frame site whose own record is not active A-C (29 records at `1b924786` meet it, 28 of them assigned to a stratum and one held under B6; 15 of the assigned are in the PIC-18 stratum, including 12 of the 794 PIC-18 outcome-frame owners) | Include: the site's owner is read in the outcome frame and its fields publish | yes |
| B3 | Region of an organization: by footprint (this draft) or by HQ only; and an organization with no HQ state that owns frame sites (placed by its sites alone here) | Footprint, first match wins as in 2.1, so a Texas parent with one PIC-18 plant is a PIC-18 record; an Ohio HQ with no county is held (B6) | yes |
| B4 | Organizations, ecosystem and site rows pooled in one stratum per region by simple random sampling (this draft), or sampled per table with weights | Pooled: equal weights, Kish factor 1, matches "organizations and sites by region" | yes |
| B5 | Ecosystem rows (408) are not named by the rulings | Include with organizations: they publish pages, are Ring 5 and are in the 794 outcome frame | yes |
| B6 | 31 records fit no stratum at `1b924786`: 20 ecosystem rows with no state, 4 ecosystem and 5 organization rows with an Ohio HQ and no county, 2 organizations with no state | Fill the 9 Ohio counties by a data PR before the draw. Place the 22 location-less rows in rest of country only if an integrator confirms from `geography_served`; the draw refuses until none remain | yes |
| B7 | Events stratum unit: events and participation rows pooled (this draft: about 4 events and 67 rows in 71) or a census of the 98 events plus a sample of rows | Pooled; events rarely get read, so add a census of the 98 event rows' own J fields if the owner wants the event record itself held to 10% | yes |
| B8 | Which columns count as "published": site fields plus release columns that state a world fact (the J set), not builder metadata; coordinates not judged | As the table in section 3. The strict reading (every column, `notes` and `created_by` included) cannot be graded; a geocode check can be added as a deterministic test if the owner wants coordinates in the unit | no (packet) |
| B9 | Child rows (evidence, registry links, capabilities, equipment, code assignments, identifiers, engagement, archive links, members) judged with their parent, evidence by binding-gate plus raw-quote replay, an unsettled child marking the parent UNRESOLVED | Yes; it is the failure that cost the Atlas 28% of a day's rows. Awaiting the owner, so not settled here | no (packet) |
| B10 | Stage-2 size: the ruling's 460 and 71 (a true 3% passes 49% and 64% of the time), or larger | Keep 460 for PIC-18. Raise each 10% stratum to n2 = 110 (true 3% passes 77%; true 2%, 93%; false pass 1.4%). Reading cost is 5 x 39 more records | yes (`sizes.PLAN`) |

Settled here as method, not scope (disclosed for the owner to veto): unresolved counted as wrong in the decision; omissions not errors; drift not an error; third-family adjudication
and lead verification of every error; plants.

**B6 answered 2026-11-23 (owner round 22, [DECISIONS.md](../../DECISIONS.md)).**
The frame reads [placements.csv](placements.csv) from its pinned commit. The file lists
the source-confirmed national or international ecosystem placements, approved Ohio city
placements where every county lies outside PIC-18, and the named exclusion of ORG-003769
pending the Sunbiz read. It accepts an entry only for a record that is otherwise
unassignable in that frame. The reconciliation shows the named exclusion and its count.
Dublin, Westerville and Columbus supply the approved Ohio city bases. The Columbus basis applies
to the two Ohio Innovation Exchange records under the controller's implementation of round 22.

## 10. Reuse, checks, and what was not built

Reused, not rebuilt: audit 10 and 11's whitelist-and-leak-scan packet builder (`tasks/blind-audit-11-2026-11-17/sample.py`), `REVIEWER_INSTRUCTIONS.md`, lock and receipt practice, adjudication fetch/build scripts,
`stats.py`'s Wilson (this folder's `sizes.py` uses the same z and passes its known answers), and the binding gate. **Not built here:** the packet builder for audit 12 (a follow-up lane adapts `sample.py` using the
J/K classes), the evidence-replay harness over the gate, the reader instructions for the new fields, and any data fix for B6. **Checks:** `python3 tasks/blind-audit-12-protocol-2026-11-23/sizes.py --selftest` and
`draw.py --selftest` (synthetic fixtures, then the real frame at `origin/main` with the site builder's own counts; it **fails** when `origin/main` is missing, and `--selftest --synthetic-only` runs the synthetic half alone and says so).
