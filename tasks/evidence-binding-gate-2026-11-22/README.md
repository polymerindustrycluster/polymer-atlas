# Evidence binding gate (2026-11-22)

On 2026-11-22, batches 5 and 6 (PRs #457 and #458) added about 34,000 evidence rows that were joined by machine. Every check passed. The controller's first-cut test found that 28% of those rows do not bind to the record they are filed on:

- the quote names another operator;
- the quote prints another street;
- or a headquarters is claimed from a plant permit.

`validate.py` checks a row's form, never whether its quote is about that record. The owner ruled both batches reverted (another lane is doing that), and ruled that a row returns only if it passes a hardened binding gate. This folder holds that gate's record.

Every number below comes from `python3 tasks/evidence-binding-gate-2026-11-22/check.py`. It reads pinned commits and fails if any of its 53 numbers drifts. Rows are cited by `evidence_id` only. No source quote text is copied here or in the tests (controller instruction, 2026-11-22).

## What the gate decides

`scripts/check_evidence_binding.py` gives every evidence row exactly one verdict.

| Verdict | Meaning | Reasons |
| --- | --- | --- |
| PASS | The quoted operator is a name the record itself holds (exact `name_key`). For a site row, the quoted street equals the site's `street_address` under `street_key`, the key has a civic number, and no stated suite or unit conflicts. For an organization `address` row, the source states the entity's own address (USAspending recipient, SBIR firm) and the quoted city and state are the record's headquarters. | — |
| FAIL | The quote is about something else. | `name_not_held`, `street_differs`, `unit_differs`, `record_no_street`, `quote_no_street`, `hq_from_facility_or_permit`, `hq_from_s5_identity_source`, `hq_city_state_differs` (several may join with `+`) |
| UNINSPECTABLE | The gate cannot read the row. This is never a pass. Rows in this class are counted and reported. | `no_quote`, `free_text_web_quote`, `other_table`, `record_not_found`, `unknown_source_family`, `parse_failed`, `operator_not_a_name`, `no_civic_number` |

How the quote is read:

- **Source families.** Quote parsing uses an explicit table of source families (ECHO, OSHA, FMCSA, state entity files, USAspending, SBIR and nine state permit layers). Any other source is `unknown_source_family`.
- **Operator.** On a permit, the operator is the permittee, not the facility label.
- **Shifted columns.** A permittee field with no letters (`operator_not_a_name`) is the NC DEQ layer's shifted columns, as in "permittee: 3".
- **Civic number.** Equal street keys with no civic number, such as a bare park or road name, are UNINSPECTABLE. A civic number is a token holding a digit (`198A`, `N44 W33341`) or a leading number word (`One Innovation Dr`), so those forms pass (controller addition 2026-11-22).
- **Suite or unit.** `street_key` drops suites, so a separate test fails a row only when both sides state a suite or unit and the two differ. This covers the SITE-000514 and SITE-019015 class from the 463 review.

### Modes

- `--all [--head REF] [--out FILE]` reports every evidence row on a tree:
  - by verdict and reason;
  - by `created_by`;
  - by source family.

  It asserts that the rows judged equal the rows read, and that the evidence IDs are unique.
- `--new-since REF` is the pull-request gate.
  - **What it checks:** rows that are new since the merge-base with REF, or whose binding fields (`record_table`, `record_id`, `claim_type`, `claim_detail`, `source_ref`) changed. A re-pointed row is a new claim.
  - **Exit 1:** any FAIL or UNINSPECTABLE row without a waiver.
  - **Exit 2:** an unreadable base, zero rows, a duplicate ID, or a malformed waiver file. The check fails closed.
- `--provenance-since REF` exits 1 when a `created_by` label of an added row does not name a `tasks/<folder>/` holding a `check.py`. The whole label counts, and so does any one of its words.

Rows already on `main` are not failed. `--all` reports them.

### Waiver file

The waiver file is any `tasks/**/BINDING_WAIVERS.csv`. Its header is `evidence_id,reason,reviewer`, with one line per row. A reason and a reviewer are both required.

Waivers are keyed by `evidence_id`. IDs are never reused (AGENTS §3), so an old waiver cannot authorise a later row.

### CI

`.github/workflows/validate.yml` runs both PR modes against `origin/<base>`, after the row-loss guard, on pull requests only.

## Verdict tables

Counts below are evidence rows.

**Current `main` at 8f30ce0f** (the branch cut; batches 5 and 6 are still on it):

| Filter | Rows | PASS | FAIL | UNINSPECTABLE |
| --- | ---: | ---: | ---: | ---: |
| All evidence rows | 81,510 | 20,733 | 12,871 | 47,906 |
| Without the rows PRs #457 and #458 added | 47,416 | 0 | 0 | 47,416 |

No row outside the two join batches is inspectable. Of the 47,416, 41,461 carry no quote, and the rest are free-text web quotes, other tables or unknown families. The gate inspects the bulk-join formats and nothing else.

**Quarantined batches** (rows PRs #457 and #458 added, 4ee02127 → 17834918):

| `created_by` | Rows | PASS | FAIL | UNINSPECTABLE |
| --- | ---: | ---: | ---: | ---: |
| spaghetti-batch5-2026-11-22 | 10,352 | 6,808 (65.8%) | 3,354 (32.4%) | 190 |
| spaghetti-batch6-2026-11-22 | 23,564 | 13,925 (59.1%) | 9,517 (40.4%) | 122 |
| spaghetti-burndown-batch1-2026-11-21 (re-added in #457) | 122 | 0 | 0 | 122 |
| spaghetti-burndown-batch2-2026-11-21 (re-added in #457) | 56 | 0 | 0 | 56 |
| **Both PRs** | **34,094** | **20,733 (60.8%)** | **12,871 (37.8%)** | **490** |

FAIL and UNINSPECTABLE reasons in the batches, by row:

| Reason | Rows |
| --- | ---: |
| `name_not_held` | 4,590 |
| `street_differs` | 3,628 |
| `record_no_street` | 2,732 |
| `hq_from_s5_identity_source` | 627 |
| `name_not_held+street_differs` | 474 |
| `quote_no_street` | 406 |
| `free_text_web_quote` | 364 |
| `name_not_held+record_no_street` | 252 |
| `operator_not_a_name` | 98 |
| `hq_from_facility_or_permit` | 74 |
| `name_not_held+quote_no_street` | 70 |
| `no_civic_number` | 24 |
| `unit_differs` | 14 |
| other (`parse_failed` 4, three mixed HQ rows) | 7 |

By source family (PASS / FAIL / UNINSPECTABLE):

| Source family | PASS | FAIL | UNINSPECTABLE |
| --- | ---: | ---: | ---: |
| EPA ECHO | 9,380 | 7,124 | 22 |
| OSHA | 6,808 | 3,354 | 4 |
| FMCSA Company Census | 1,789 | 480 | 0 |
| state-entity-files-bulk | 580 | 344 | 0 |
| USAspending bulk | 669 | 2 | 0 |
| TCEQ Central Registry | 209 | 431 | 0 |
| PA DEP | 312 | 248 | 2 |
| Ohio EPA | 60 | 478 | 0 |
| NC DEQ ArcGIS | 185 | 163 | 98 |
| CA DTSC | 306 | 56 | 0 |
| CA SWRCB | 202 | 40 | 0 |
| SBIR/STTR bulk | 95 | 79 | 0 |
| IN IGMAP | 92 | 44 | 0 |
| NJDEP | 46 | 16 | 0 |
| GA EPD | 0 | 12 | 0 |
| URL (free text) | 0 | 0 | 364 |

## Calibration against the hand-labelled spotcheck

These are the rows that `S/reviews/w1122-spotcheck.md` labelled by hand. Labels are carried in `check.py` by evidence_id only.

| Draw | Spotcheck label | Gate verdict |
| --- | --- | --- |
| Appendix A (OSHA address flags, 60) | DIFFERENT_ADDRESS (54) | FAIL 54 |
| | CANNOT_TELL (5) | FAIL 5 (none pass) |
| | SAME_PLACE (1, EVD-428624) | PASS 1 |
| Appendix B (exact-street name checks, 40) | DEFECT (5: EVD-449620, EVD-450128, EVD-457493, EVD-455899, EVD-457589) | FAIL 5 |
| | MATCH (35) | PASS 27, FAIL 8 |

The 8 true matches that fail do so under the strict reading:

- held name plus a plant word: EVD-448086, EVD-446818;
- name variant: EVD-444906;
- division name: EVD-443796;
- operator named only in notes: EVD-445324;
- permittee is another legal string and only the facility label matches: EVD-457497, EVD-456891;
- `street_key` limit (one route written two ways): EVD-438364.

Each is an owner question below.

## Measured disagreements with the first cut

The first cut is `S/audits/2026-11-22-binding-test/binding.py`, whose `verdicts.csv` sits outside the repo. Run `check.py --first-cut <path>` to reproduce this table. The first cut judged 38,226 rows (EVD-399606 and above) at 17834918.

| First cut → this gate | Rows |
| --- | ---: |
| PASS → PASS | 20,589 |
| FAIL → FAIL | 9,321 |
| PASS → FAIL | 3,546 |
| FREETEXT / OTHER_TABLE / NO_QUOTE → UNINSPECTABLE | 4,496 |
| FAIL → PASS | 128 |
| PASS → UNINSPECTABLE | 106 |
| FAIL → UNINSPECTABLE | 20 |
| FREETEXT → PASS / FAIL | 16 / 4 |

The first cut's FAIL share on the batch rows reproduces at 9,469 / 34,094 = **27.8%**, which is the 28% the brief cites. On the same rows this gate fails 37.8%.

**Where the gate is stricter (PASS → FAIL, 3,546):**

- The first cut accepted any token subset. That passed a held name inside another name, and a parent's name two levels up. This gate requires exact `name_key` equality with a name the record holds.
- The first cut passed facility-label matches.
- The first cut never checked the source of a headquarters claim against SCHEMA §4.8 S-5. 627 FMCSA and state-filing HQ rows now fail.

**Where the gate is looser (FAIL → PASS, 128):**

- The first cut's OSHA parser misread the following as different streets: a suite in its own comma part, a city printed twice, and a 4-digit ZIP.
- The first cut's ECHO test demanded a digit, so it rejected number-word streets ("One … Drive").
- Its name test missed names written with "&" or ":".
- Of the 128, 98 are OSHA rows and 30 are ECHO rows.

**PASS → UNINSPECTABLE (106):**

- 98 are the NC DEQ shifted-column rows, where the first cut read the facility label as the operator.
- 6 are equal street keys with no civic number, and 2 are ECHO quotes the gate does not parse.

## The false-PASS side

These are the batch PASS rows, by which quoted form matched which held name.

| Name basis | Rows |
| --- | ---: |
| Whole quoted name = a name of the operator organization | 18,343 |
| Whole quoted name = the site name's leading part | 1,314 |
| Whole quoted name = the full site name or another part of it | 934 |
| One comma part ("company, facility label") = an organization name | 118 |
| One comma part = the site name's leading part | 24 |

Samples of the last three classes read as true matches: a name plus the site's locality, and a company plus its plant label.

Only 2 PASS rows (EVD-438285, EVD-438286) match nothing but a non-leading part of the site name, and that part is a real division name.

The 30 ECHO rows that moved FAIL → PASS against the first cut are number-word streets and names with parentheses.

**PASS means the quote binds to the record, not that the row is admissible.** For example, an FMCSA site `address` row passes on street equality while SCHEMA §4.8 S-5 says the FMCSA census address is the carrier's filed address. Tier ceilings and address roles remain the validator's and the integrator's job.

## Questions for the owner

The gate implements the strict reading. Each alternative reading below is measured on the batch rows; none of them passes in the gate. In each count, "would pass" means the row's only defect is the one named.

1. **A held name plus more words** (`leading_run`): 1,829 rows would pass.
   - Example of a true match: "ARMACOR LLC-CONOVER PLANT" against Armacor, modelled on EVD-445712.
   - The same rule also passes the fleet-services affiliate named as permittee on EVD-455899, which is a different operator.
   - A facility-word list would separate the two, but that is the kind of normaliser widening the brief reserves to you.
2. **Permit facility label when the permittee differs:** 154 rows would pass. Examples: EVD-457497 and EVD-456891.
   - Batches 5 and 6 also contain permits filed by contractors and neighbouring operators at a held plant. Those rows fail under both readings.
3. **A parent's name** (parent chain or `ultimate_parent_name`): 46 rows would pass.
4. **A predecessor or other name found only in the record's notes:** 982 `name_not_held` rows match. 868 of them have no other defect.
   - The full list for you is [notes_name_rows.csv](notes_name_rows.csv): evidence_id, path:line at 17834918, and record_id. It contains no notes text.
   - Example: EVD-450005 (Covestro / former Vencorex).
5. **Dotted initials** ("A.B.C." against "ABC"): 142 rows would pass.
   - This is a `name_key` limit, so it is reported here and not widened.
6. **Street-key limits** (reported, not widened, per the brief), counted over the 3,628 `street_differs` rows:

   | Class | Rows | Example IDs |
   | --- | ---: | --- |
   | `same_number_token_subset` (one side adds words such as "US", "LA" or a suffix) | 1,552 | EVD-425437, EVD-425485 |
   | `same_number_other` (another street name or suffix, e.g. Avenue against Way) | 1,274 | EVD-425511, EVD-430113 |
   | `different_number` | 934 | EVD-425445 |
   | `same_street_other_number` (another number on the same street; a campus address?) | 236 | EVD-425487, EVD-430077 |
   | `number_word` (cardinal or ordinal: "First Street" against "1st Street") | 92 | EVD-425473 |
   | `number_in_recorded_range` ("1201-1205 Main" against "1203 Main") | 14 | EVD-430273, EVD-439483 |

   - The brief's third named class, "&" against "and", does not exist: `squash` already folds "&" into "and", and EVD-428624 passes.
   - Whether a campus address (another number on one street, or another entrance) counts as a match is your ruling.
7. **Headquarters from identity-only sources.** SCHEMA §4.8 S-5 (owner ruling 2026-11-22, battery S-5) governs this: a state filing's address may be an agent's, and the FMCSA address is the carrier's filed address. Under that ruling these rows fail:
   - 343 state-entity `principal_address` rows;
   - 284 FMCSA rows.

   Each would otherwise pass on name, city and state. The question is whether a state filing's labelled *principal* office is an entity-address source.
8. **USAspending and SBIR as headquarters sources** (333 rows pass): I treated both as stating the entity's own address. But a UEI can be registered for a single plant, and an SBIR address dates from the award year.
   - USAspending recipient addresses come from SAM registrations. R-SAM (2026-11-16) bars copying a SAM name or address into the Atlas.
   - The 2026-11-22 ruling (DECISIONS.md) lifts that bar for the public SAM extract only.
   - Whether USAspending counts as SAM under R-SAM is your ruling.
9. **Shifted columns** (NC DEQ, 98 rows): 94 would pass if the facility label were read as the operator.
10. **Gate scope.** Under the brief as written, every new row with no quote or a free-text web quote is UNINSPECTABLE and needs its own waiver line.
    - **Replay.** I replayed the last 40 first-parent commits on `main`, each against its parent. 22 of the 24 commits that added evidence rows had nothing inspectable. Burn-down batch 2 (c2b1d1803) alone would need 1,276 waiver lines.
    - **Provenance.** The provenance check would have failed all 24.
    - **Status.** The gate ships as written, with the provenance folder allowed to exist already at the head. This was put to the controller on 2026-11-22 with two narrower options: gate only the structured families, or accept one waiver line per `created_by`.

## What this gate cannot see

- **Truth.** The gate checks that a quote is about the record, not that the quote is faithful to its source or that the source is current.
  - It fetches nothing.
  - An extract older than an operator change can still pass. For example, a permit held by the new operator under the old street would pass.
  - Spotcheck §6 checked 15 quotes against the EPA bulk tables by hand.
- **The city.** For a site row the gate binds the street, not the city.
  - 242 of the 18,592 site PASS rows in the batches quote a city other than the record's, e.g. EVD-438149 and EVD-448255.
  - Some are mailing names for the same place (a big city's name for a suburb). Others may be a same-named street in another town.
  - The quoted state agrees with the record on every site PASS row in the batches: 0 differ, and the state was read on 18,582 of 18,592.
  - County is not checked at all.
- **Identity behind an equal name.** An unrelated namesake at the same street would pass. Organization existence rows are judged on the name alone.
  - The 57 Motiva permits for distinct stores pass existence 57 times from one registry. The gate does not measure that correlation.
  - The 57 matching headquarters rows fail.
- **The claim's own value.** The gate compares the quote with the record's current fields, not with the value `claim_detail` asserts. If a record field changes later, the row's verdict can change.
- **Tier ceilings.** The §4.13 `tier_effect` class ceilings are not checked. Neither is `address_role`.
- **Field edits.** An edit to a row's tier effect, date or notes is not re-gated. Only a change to its binding fields is.
- **Free text.** Free-text web quotes (3,347 rows on `main`) and rows without quotes (41,461) are UNINSPECTABLE. So is every row outside the bulk-join formats.
- **Waivers.** The waiver's reviewer is free text, and the gate cannot verify who it names.
- **Provenance.** The provenance check proves that a `check.py` exists. It does not prove that the script runs or that it reproduces the rows.

## Checks

| Check | Command | Result |
| --- | --- | --- |
| Gate unit tests | `cd scripts && python3 -m unittest test_check_evidence_binding` (CI runs them through `scripts/run_tests.py`) | 49 tests OK. They cover planted defects, true matches and uninspectable rows, all synthetic strings shaped like real rows, plus a known-answer replay: `--new-since 6a76e923 --head 17834918` and `--provenance-since` on the same range both exit 1. |
| This folder's check | `python3 tasks/evidence-binding-gate-2026-11-22/check.py` | 53 numbers OK. See the two rows below. |
| Leak guard (inside `check.py`) | — | 0 of the 164 street-, ID- or name-like segments in the test strings occur in any `claim_detail` at 17834918. A planted real fragment is caught. |
| Mutation check (inside `check.py`) | — | Copies of the gate each loosen one rule, and each loosening is caught by the planted-defect tests: token-subset names fail 6, number-only streets 2, no unit test 1, HQ from any source 2. |

The remaining repository checks are recorded in the PR.
