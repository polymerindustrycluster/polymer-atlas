# Blind audit 10 — phase 1: frame, sample, blind inputs

Owner request 2026-11-14: a blind sample audit of the data PRs merged 2026-11-09 to 2026-11-12, which merged on
"owner-approved" packet checks without a recorded two-family refute and mostly without a task-folder builder or check.
Controller thr_9i2c6byhcz; lead thr_4tngyjjf65 (Claude). Phase 1 builds the frame, the sample and the blind inputs and
stops. Branch `agent/claude-code/blind-audit-10`, no PR yet. Phase 2 (two blind reviewers) and phase 3 (lead
adjudication) are separate instructions. No `data/` edits, no new IDs.

First user: the repo owner / controller, deciding whether the merged PRs need a two-family refute. Non-use is a finding
on 2026-12-14 if no one has read the phase 3 report by then.

## Check

`python3 tasks/blind-audit-10-2026-11-14/check.py` — PASS recorded in the controller report. It needs full git history
(the CI validate job checks out with `fetch-depth: 0`). It re-derives the frame from git, reconciles it, re-draws the
sample from the seed, and checks that `blind_a.csv` equals `blind_b.csv`, the freeze hashes, and the leak scan. It also
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

| table (unit: record) | rows at BASE | created | changed (non-derived cols) | **frame** | deleted (not in frame) | rows at HEAD |
|---|---|---|---|---|---|---|
| people | 1,454 | 63 | 432 | **495** | 4 | 1,513 |
| programs | 171 | 45 | 100 | **145** | 0 | 216 |
| ecosystem | 402 | 6 | 32 | **38** | 0 | 408 |
| organizations | 5,024 | 0 | 2 | **2** | 0 | 5,024 |
| sites | 7,189 | 1 | 2 | **3** | 0 | 7,190 |
| relationships | 360 | 0 | 0 | **0** | 0 | 360 |
| people_identifiers | 0 | 816 | 0 | **816** | 0 | 816 |
| event_participation | 1,142 | 154 | 0 | **154** | 0 | 1,296 |
| **all** | | 1,085 | 568 | **1,653** | 4 | |

Excluded, with counts (unit: record): `tier1_qualifier*`-only changes **0** (the window opens after the tier-1 re-derive
PR #257, so none exist); records changed only by evidence appends are outside the frame by construction (PRs #258 and
#266 changed only `evidence_organizations_*` shards, so they contribute no frame record); 4 people rows deleted by merge
(`PERSON-000812`, `-001260`, `-001331`, `-001402`; PRs #260, #264, #265, #283) have no current value to audit; touched-
then-reverted 0; created-then-deleted 0; shard-move-only 0. Out-of-scope tables that also changed: `events.csv` (71 rows;
64 rows gained a value in the new `pic_events_slug` column, 0 rows changed in any other column), `inclusion_log.csv`
(22 rows appended). 12 frame records were touched by two PRs; the frame lists both PRs and the columns each changed.

**Reconciliation (AGENTS §2 rule 10c).** Derived creations per PR equal the counts the PR titles state outright, for all
34 (PR, table) pairs a title gives (e.g. #259: 804 identifier rows; #263: 11; #293: 6 center rows; #297: 11 people and 2
institutions; #299: 11 program rows and 3 institutions; #300: 8 program rows) and the 4 stated deletions, and the sum of
per-PR creations equals the net creations in every table (`check.py`). #263's title says 815 identifier links in total
and HEAD holds 816: the 816th was created by #271 (SCHEMA v1.13), whose title states no count. Derived-column
exclusions and tables are in `frame_provenance.json`; per-PR counts per table are in its `per_pr_per_table`.

**Open scope flag.** 32 of the 38 ecosystem records changed only in the §4.11 generated rollup columns
(`polymer_program`, `polymer_program_name`, `polymer_program_url`) plus `last_verified`. The brief names only
`tier1_qualifier*` as derived, so they stay in the frame, marked `derived_rollup_only=true` in `frame.csv`. Whether
rollup-only recomputes are an audit target is an owner/controller call; a change after phase 2 starts costs a re-draw.

## Sample

50 records, table strata, simple random within stratum. Seed `BLIND-AUDIT-10-2026-11-14-v1`; each stratum draws with
`random.Random(int(SHA256(seed|table)))` over record IDs sorted ascending (`sample.py`, receipt `draw.json`).

Allocation rule (the lead's assumption; the brief asks for proportional with at least 3 per stratum of 5 or more
records): strata under 5 records are taken whole, every other stratum gets at least 3, and the rest of the 50 is split in
proportion by largest remainder. Without the census, organizations (2) and sites (3) would round to zero and leave the
Gregstrom (#267) and OMG Thermoforming (#268) corrections unaudited.

| stratum (unit: record) | N in frame | n sampled | inclusion probability | design weight |
|---|---|---|---|---|
| people_identifiers | 816 | 21 | 0.0257 | 38.9 |
| people | 495 | 13 | 0.0263 | 38.1 |
| programs | 145 | 4 | 0.0276 | 36.3 |
| event_participation | 154 | 4 | 0.0260 | 38.5 |
| ecosystem | 38 | 3 | 0.0789 | 12.7 |
| sites | 3 | 3 (census) | 1 | 1 |
| organizations | 2 | 2 (census) | 1 | 1 |
| relationships | 0 | 0 | — | — |

31 sampled records are creations and 19 are changes (people: 3 created, 10 changed; programs: 1 created, 3 changed;
ecosystem: 1 created, 2 changed; sites 1 and 2; organizations 0 and 2). The sample spans 21 PRs (20 of the 21 identifier
rows come from #259, in proportion to its 804 of 816). Rates must be stated per table stratum, with the unit; the pooled
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
- `cited_sources`: the record's own `sources` text with source-read dates removed; in 4 records the text cited
  working-packet or staging paths, so only its public URLs are kept (`sample.csv` column `sources_scrubbed_to_urls`).
- `evidence_json`: claim type and URL for each current evidence row (people, programs, ecosystem, organizations, sites).

Withheld: the PR, lane, `created_by`, `notes`, `last_verified`, `as_of`, `observed_date`, `evidence_date`,
`last_activity_evidence_date` (all date the pass), evidence `evidence_id`, `tier_effect`, `claim_detail`, `source_class`,
and any packet, verdict or reviewer text. Phase 3 audits those fields unblinded.

**Blindness is by protocol, not access control.** `frame.csv` and `sample.csv` sit beside the blind files and carry PR
attribution, so hand each reviewer only their blind file. `freeze.json` holds the sha256 of both blind files, the frame,
the sample, the draw receipt, the provenance, and `frame.py` and `sample.py`; `check.py` fails if any changed after the
freeze.

## What phase 2 and 3 do

Phase 2: two reviewers, each given only one blind file and no `council-ask` or OpenAI route (CONTRACT-CLAUDE), research
every record fresh from primary or public sources (about 6 routes per record, quotes re-checked raw), lock a verdict per
record before reading any evidence, and use the AGENTS §2 rule 8 grammar (VERIFIED, REJECT with the deciding fact,
STILL_UNCERTAIN with the settling fact, DUPLICATE_OF) per audited column. Phase 3 (lead): unblind, compare the two
reviewers with the held evidence, adjudicate disagreements, and report per-table rates (unit and filter stated) with 95%
Wilson intervals (z = 1.959964), census strata marked, using the audit-9 statistics code adapted for this frame.
