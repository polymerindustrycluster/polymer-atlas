# Blind audit 10 — frame, sample, blind inputs (phase 1) and adjudicated results (phase 3)

Owner request 2026-11-14: a blind sample audit of the data PRs merged 2026-11-09 to 2026-11-12, which merged on
"owner-approved" packet checks without a recorded two-family refute and mostly without a task-folder builder or check.
Controller thr_9i2c6byhcz; lead thr_4tngyjjf65 (Claude). Phase 1 built the frame, the sample and the blind inputs; phase 2 ran
two blind reviewers (A Claude, B Codex) outside this branch; phase 3 is the lead's adjudication and statistics (below). Branch
`agent/claude-code/blind-audit-10`, draft PR. No `data/` edits, no new IDs. The report is
`docs/reviews/BLIND_AUDIT_10_2026-11-14.md`.

**Revision v2, 2026-11-14 (controller rulings; v1 superseded).** Phase 1 first shipped at head `4fd98d7` with a 1,653-record
frame and seed `...-v1`. The controller then ruled (1) the 32 ecosystem records whose only changes are the generated
rollup columns are derived and leave the frame, (2) organizations and sites stay a full census with the floor of 3 for the
other strata, (3) identifier rows stay in proportion, and phase 3 reports error rates per stratum as well as overall.
Phase 2 had not started, so the draw was redone with seed `BLIND-AUDIT-10-2026-11-14-v2`. v1's receipts are kept in
`superseded_v1/` (`draw_v1.json`, `freeze_v1.json`); v1's frame, sample and blind files are in git history at `4fd98d7`.
The v1 blind files were never given to a reviewer.

First user: the repo owner / controller, deciding whether the merged PRs need a two-family refute. Non-use is a finding
on 2026-12-14 if no one has read the phase 3 report by then.

## Check

`python3 tasks/blind-audit-10-2026-11-14/check.py` — PASS recorded in the controller report. It needs full git history
(the CI validate job checks out with `fetch-depth: 0`). It re-derives the frame from git, reconciles it, re-draws the
sample from the seed, and checks that `blind_a.csv` equals `blind_b.csv`, the freeze hashes, and the leak scan. It runs seven
known-answer tests on the derivation (Gregstrom HQ moves across shards as one changed record in #267 with its HQ columns
flagged; `SITE-019101` created and `SITE-004416` changed; `PERSON-001402` deleted and absent from the frame; identifier
rows attributed 804 to #259, 11 to #263, 1 to #271; `PROG-000305` created by #284; `ORG-004660` (UChicago), changed only in rollup columns, absent from the frame and listed as
excluded; `ORG-013501` (Wake Forest), a created ecosystem row, kept), plus synthetic tests that a `tier1_qualifier`-only
change is excluded, a content change kept, a shard move alone is not a change, and the rollup predicate excludes an
ecosystem rollup-only change but nothing else. It also
plants five defects (a PR number, an `EVD-` id, a "minted in wave 3" phrase, a packet/staging reference, a pass date) and
a `pr` column in copies of the blind file, and each must be caught.

## Frame

**Unit: changed record** = one row at HEAD, keyed by its table ID (`people_identifiers`: person_id + identifier_type +
identifier_id), that was created, or changed in at least one non-derived column, by a first-parent commit in
`1fefbd2..4ecc7cf` on `main` (BASE `1fefbd29`, PR #257; HEAD `4ecc7cf8`, PR #329 merge; 59 first-parent commits, 59 PRs,
53 of them touch at least one frame record). Eight tables: people, programs, ecosystem, organizations, sites,
relationships, people_identifiers, event_participation. Shard files are read as one table, so a cross-shard move (the
Gregstrom HQ, MA to NH) is one changed record, not a delete plus a create.

Two independent derivations must agree, and `frame.py` asserts it: (1) the sum of the 59 per-commit first-parent diffs
(`sha^1..sha`), which gives PR attribution and per-PR changed columns; (2) one whole-table BASE-vs-HEAD diff, which gives
the net changed columns. Every net change must be seen by some commit (none was missed); record IDs are unique within
every table at HEAD, and `org_id` never appears in both `organizations` and `ecosystem`.

| table (unit: record) | rows at BASE | created | changed (non-derived cols) | rollup-only, excluded | **frame** | deleted (not in frame) | rows at HEAD |
|---|---|---|---|---|---|---|---|
| people | 1,454 | 63 | 432 | 0 | **495** | 4 | 1,513 |
| programs | 171 | 45 | 100 | 0 | **145** | 0 | 216 |
| ecosystem | 402 | 6 | 32 | 32 | **6** | 0 | 408 |
| organizations | 5,024 | 0 | 2 | 0 | **2** | 0 | 5,024 |
| sites | 7,189 | 1 | 2 | 0 | **3** | 0 | 7,190 |
| relationships | 360 | 0 | 0 | 0 | **0** | 0 | 360 |
| people_identifiers | 0 | 816 | 0 | 0 | **816** | 0 | 816 |
| event_participation | 1,142 | 154 | 0 | 0 | **154** | 0 | 1,296 |
| **all** | | 1,085 | 568 | 32 | **1,621** | 4 | |

The "changed" column counts before the rollup exclusion, so frame = created + changed - rollup-only excluded; the 1,621
frame is 536 changed + 1,085 created.

Excluded, with counts (unit: record): ecosystem records changed only in the §4.11 generated rollup columns
(`polymer_program`, `polymer_program_name`, `polymer_program_url`, with `last_verified` riding along) **32** (controller
ruling 2026-11-14; IDs in `frame_provenance.json` under `tables.ecosystem.rollup_excluded_ids`); `tier1_qualifier*`-only
changes **0** (the window opens after the tier-1 re-derive PR #257, so none exist); records changed only by evidence appends are outside the frame by construction (PRs #258 and
#266 changed only `evidence_organizations_*` shards, so they contribute no frame record); 4 people rows deleted by merge
(`PERSON-000812`, `-001260`, `-001331`, `-001402`; PRs #260, #264, #265, #283) have no current value to audit; touched-
then-reverted 0; created-then-deleted 0; shard-move-only 0. Out-of-scope tables that also changed: `events.csv` (71 rows;
64 rows gained a value in the new `pic_events_slug` column, 0 rows changed in any other column), `inclusion_log.csv`
(22 rows appended). 8 frame records were touched by two PRs; the frame lists both PRs and the columns each changed.
`git diff --numstat` shows +1,514/-1,455 lines in `people.csv` against 495 frame records, because SCHEMA v1.13 inserted
the `lab_url` column and so rewrote every row (1,454 rows plus the header); frame membership compares parsed column
values, not lines, so those rewrites do not count. Anyone rebasing people changes will hit that line-level conflict.

**Reconciliation (AGENTS §2 rule 10c).** Derived creations per PR equal the counts the PR titles state outright, for all
34 (PR, table) pairs a title gives (e.g. #259: 804 identifier rows; #263: 11; #293: 6 center rows; #297: 11 people and 2
institutions; #299: 11 program rows and 3 institutions; #300: 8 program rows) and the 4 stated deletions, and the sum of
per-PR creations equals the net creations in every table (`check.py`). #263's title says 815 identifier links in total
and HEAD holds 816: the 816th was created by #271 (SCHEMA v1.13), whose title states no count. Derived-column
exclusions and tables are in `frame_provenance.json`; per-PR counts per table are in its `per_pr_per_table`.

**Rollup exclusion.** The brief names `tier1_qualifier*` as its example of a derived column; the controller ruled the
generated rollup columns derived too (they are the output of the program rows, which are themselves in the frame). So the
ecosystem stratum is its 6 created rows. The program rows behind those rollups stay audited in the programs stratum.

## Sample

50 records, table strata, simple random within stratum. Seed `BLIND-AUDIT-10-2026-11-14-v2`; each stratum draws with
`random.Random(int(SHA256(seed|table)))` over record IDs sorted ascending (`sample.py`, receipt `draw.json`).

Allocation rule (the lead's assumption, confirmed by the controller 2026-11-14; the brief asks for proportional with at
least 3 per stratum of 5 or more records): strata under 5 records are taken whole, every other stratum gets at least 3, and the rest of the 50 is split in
proportion by largest remainder. Without the census, organizations (2) and sites (3) would round to zero and leave the
Gregstrom (#267) and OMG Thermoforming (#268) corrections unaudited.

| stratum (unit: record) | N in frame | n sampled | inclusion probability | design weight |
|---|---|---|---|---|
| people_identifiers | 816 | 21 | 0.0257 | 38.9 |
| people | 495 | 13 | 0.0263 | 38.1 |
| programs | 145 | 4 | 0.0276 | 36.3 |
| event_participation | 154 | 4 | 0.0260 | 38.5 |
| ecosystem | 6 | 3 | 0.5 | 2 |
| sites | 3 | 3 (census) | 1 | 1 |
| organizations | 2 | 2 (census) | 1 | 1 |
| relationships | 0 | 0 | — | — |

34 sampled records are creations and 16 are changes (people: 3 created, 10 changed; programs: 2 created, 2 changed;
ecosystem: 3 created; sites: 1 created, 2 changed; organizations: 2 changed; identifiers and event rows: all created). The
sample spans 20 PRs (all 21 identifier rows come from #259, which holds 804 of the 816 identifier rows). Rates must be stated per table stratum, with the unit; the pooled
frame rate needs the design weights above. No claim covers records outside the frame, and `frame.csv` is not a census of
everything the PRs touched (evidence-only changes are out).

**Records with no public URL.** 21 of 50, all `people_identifiers`: that table has no `sources` column and no evidence
shard, and its claim is the identifier itself, which the ORCID public registry settles. Every other sampled record carries
at least one public URL in its sources, evidence or values. In the frame, 0 of 154 `event_participation` rows lack an
http evidence URL. A reviewer who cannot reach a source reports STILL_UNCERTAIN under AGENTS §2 rule 8, never a REJECT.

## Blind inputs

`blind_a.csv` and `blind_b.csv` are byte-identical (each reviewer gets the full 50). Row order is a seeded shuffle, so it
does not follow ID order, which tracks PR order. Fields are a whitelist (`sample.py` `BLIND_FIELDS`), built from git at the
pinned HEAD, never from the working tree:

`blind_id, table, record_id, record_label, change_kind, columns_under_audit, values_json, context_json, cited_sources,
evidence_json`

- `values_json`: current values of the changed columns (for a created record, every non-empty column), including
  `verification_tier` and, for identifiers, `match_basis`, which are schema fields and not packet verdicts.
- `context_json`: foreign keys resolved to names (institution, program, parent org, event, person; for an identifier
  row, the person's institution and public profile URL).
- `cited_sources`: the record's own `sources` text with source-read dates removed; in 2 records the text cited
  working-packet or staging paths, so only its public URLs are kept (`sample.csv` column `sources_scrubbed_to_urls`).
- `evidence_json`: claim type and URL for each current evidence row (people, programs, ecosystem, organizations, sites).

Withheld: the PR, lane, `created_by`, `notes`, `last_verified`, `as_of`, `observed_date`, `evidence_date`,
`last_activity_evidence_date` (all date the pass), evidence `evidence_id`, `tier_effect`, `claim_detail`, `source_class`,
and any packet, verdict or reviewer text. Phase 3 audits those fields unblinded.

**Blindness is by protocol, not access control.** `frame.csv` and `sample.csv` sit beside the blind files and carry PR
attribution, so hand each reviewer only their blind file. `freeze.json` holds the sha256 of both blind files, the frame,
the sample, the draw receipt, the provenance, and `frame.py` and `sample.py` (the leak-scan pattern is also recorded
there; its bare `integrat` token was narrowed to `integration pass|integrator` after it false-positived on "integrated
devices" in a legitimate description); `check.py` fails if any changed after the
freeze.

## Phase 2 and 3 — what was done

Phase 2: two reviewers, each given one copy of the blind file and no OpenAI route for A (CONTRACT-CLAUDE), researched every record
fresh, locked a verdict per record, and used the AGENTS section 2 rule 8 grammar. Locked outputs are copied here unchanged:
`verdicts_a.csv` (sha256 `dfd8f490…cf4e`: 45 AGREE / 4 FIELD_ERROR / 0 CREATION / 1 UNRESOLVED) and `verdicts_b.csv`
(`60efe428…d7bc`: 37 / 0 / 0 / 13), (sha256 of the reviewers' CRLF originals; the committed copies are the exact LF normalization the repo's `*.csv eol=lf` rule applies, and `check.py` restores CRLF before comparing), with each reviewer's receipts (`receipts_a.json`, `receipts_b.json`; A did not save page bodies).
Cross-tab: both AGREE 36; A AGREE / B UNRESOLVED 9; A FIELD_ERROR / B UNRESOLVED 4; A UNRESOLVED / B AGREE 1.

Phase 3 (lead): the 14 disagreements were re-researched from fresh raw fetches (`adjudicate_fetch.py` stores each body hash-named under
`/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/blind-audit-10/raw/` and appends a receipt to
`adjudication_receipts.jsonl`; `adjudicate_build.py` holds the 14 decisions, re-verifies every quote as an ordered word sequence on the
stored page, every absence on a page that returned HTTP 200, and writes `adjudication.json` with a word excerpt per quote so the quotes
can be re-checked without the raw bodies). A failed fetch is never evidence of absence. Final grade per record is the shared grade where
the reviewers agreed and the lead's grade otherwise (`final_grades.csv`); `stats.py` writes `statistics.json` (per-stratum counts, rates
and Wilson 95% intervals with z = 1.959964, design-weighted frame estimate, sensitivity, corrections list); `write_report.py` writes the
report from those files.

**Result (unit: sampled record; frame 1,621):** 45 AGREE, 2 FIELD_ERROR (EVP-001297 `edition_dates`; PROG-000314 `url`,
`public_door_url`, partner list), 0 CREATION_ERROR, 3 UNRESOLVED (ORG-013503 AFFOA polymer scope, held for an owner ruling;
ORG-003807 OMG Thermoforming, whose description calls OMG srl "the parent" with no source for ownership; PERSON-002180 program link).
Design-weighted confirmed-error rate 4.6%. The corrections are listed in the report and are **not applied**.

**Reviewer A's stale-checkout disclosure:** A's early notes used a checkout behind the audited state; A corrected A10-002 and A10-041 in
its lock. No grade is affected: A10-002 is AGREE from both reviewers and `scripts/validate.py` passes at the pinned head, A10-041's
final grade is the lead's own, and `stale_checkout_check.py` re-ran the duplicate checks for all 50 records at the pinned head (none found).

**Check.** `check.py` now also recomputes phase 3: reviewer lock hashes, the cross-tab, that the 14 adjudications are exactly the
disagreements, every receipt (committed excerpt always; full stored body, hash, absence terms and raw patterns when the persist directory
is present, with an explicit warning and a failure on absence receipts if it is not), final grades, statistics, the report text, and
duplicates at the pinned head, plus the repo facts the report states (recomputed, not taken from reviewer A) and the two corrected records' values on
the later main. It plants an incomplete census, a duplicated verdict, an unreadable quote and an empty persist directory, and each must be rejected;
the duplicated-verdict plant exposed a real silent-accept path in `stats.summarize`, now fixed.

## What this audit does not cover

Records outside the frame; evidence-only PRs (#258, #266); fields not under audit for a sampled record; the unsampled rows that may share
the TPO end-date error (listed as a lead in the report, not rated). No second-family review of the report has run.
