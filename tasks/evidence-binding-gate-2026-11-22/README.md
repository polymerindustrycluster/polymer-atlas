# Evidence binding gate (2026-11-22)

On 2026-11-22, batches 5 and 6 (PRs #457 and #458) added about 34,000 evidence rows that were joined by machine. Every check passed. The controller's first-cut test found that 28% of those rows do not bind to the record they are filed on:

- the quote names another operator;
- the quote prints another street;
- or a headquarters is claimed from a plant permit.

`validate.py` checks a row's form, never whether its quote is about that record. The owner ruled both batches reverted (another lane is doing that), and ruled that a row returns only if it passes a hardened binding gate. This folder holds that gate's record.

Every number below comes from `python3 tasks/evidence-binding-gate-2026-11-22/check.py`, except the replay table, which comes from `replay.py` beside it (written to [replay.csv](replay.csv)). `check.py` reads pinned commits and fails if any of its 101 numbers drifts. Rows are cited by `evidence_id` only. No source quote text is copied here or in the tests (controller instruction, 2026-11-22).

## What the gate decides

`scripts/check_evidence_binding.py` gives every evidence row exactly one verdict.

| Verdict | Meaning | Reasons |
| --- | --- | --- |
| PASS | **Structured sources:** the quoted operator is a name the record itself holds (exact `name_key`). For a site row, the quoted street equals the site's `street_address` under `street_key`, the key has a civic number, and no stated suite or unit conflicts. For an organization `address` row, the source states the entity's own address (USAspending recipient, SBIR firm) and the quoted city and state are the record's headquarters. **Web quotes:** see "Web quotes" below. | — |
| FAIL | The quote is about something else. | `name_not_held`, `street_differs`, `unit_differs`, `record_no_street`, `quote_no_street`, `hq_from_facility_or_permit`, `hq_from_s5_identity_source`, `hq_city_state_differs`; web: `not_own_site`, `street_absent_from_quote` (several may join with `+`) |
| UNINSPECTABLE | The gate cannot read the row. This is never a pass. Rows in this class are counted and reported. A pull request owes a proof line for each one. | `no_quote`, `other_table`, `record_not_found`, `unknown_source_family`, `parse_failed`, `operator_not_a_name`, `no_civic_number`; web: `no_record_website`, `name_absent_from_quote`, `web_record_no_street`, `record_street_no_civic_number`, `web_class_untested`, `web_site_row_no_street_claim`, `hq_absent_from_quote` |

How the quote is read:

- **Source families.** Quote parsing uses an explicit table of source families (ECHO, OSHA, FMCSA, state entity files, USAspending, SBIR and nine state permit layers). Any other source is `unknown_source_family`.
- **Operator.** On a permit, the operator is the permittee, not the facility label.
- **Shifted columns.** A permittee field with no letters (`operator_not_a_name`) is the NC DEQ layer's shifted columns, as in "permittee: 3".
- **Civic number.** Equal street keys with no civic number, such as a bare park or road name, are UNINSPECTABLE. A civic number is a token holding a digit (`198A`, `N44 W33341`) or a leading number word (`One Innovation Dr`), so those forms pass (controller addition 2026-11-22).
- **Suite or unit.** `street_key` drops suites, so a separate test fails a row only when both sides state a suite or unit and the two differ. This covers the SITE-000514 and SITE-019015 class from the 463 review.

### Web quotes (controller ruling 2026-11-22)

A web quote (`source_ref` starting with `http`) is free text. The gate runs three mechanical tests before it calls such a row UNINSPECTABLE.

1. **Own site.** For an `own_site` row, the URL's host must be the record's own website domain. That is the site's organization's `website`, or the organization's own.    - **How domains are compared.** Each URL is normalised by `domain_key` from `scripts/atlas.py`, which strips the scheme, `www.`, the port and the path. The registrable domains are then compared: the last two host labels, or three under a country second level such as `co.uk`. So a sibling subdomain matches.
   - **Shared platforms.** On a shared platform host (atlas `PLATFORM_HOSTS`: wixsite, LinkedIn and others), the URL must be on the same host and under the record's path. A LinkedIn page never matches a company's own domain.
   - **Why not `normalize_website`.** `normalize_website` in `scripts/liveness_sweep.py` returns the full host, not the registrable domain, and does not handle platform hosts, so it was not reused.
   - **Notes in the field.** Text in the website field that is not a host is ignored.
   - Another domain is FAIL: `not_own_site`.
   - No website on the record is UNINSPECTABLE: `no_record_website`.
2. **Street.** On a site `address` or `existence` row, any web class, the street's civic number and its first street word must both appear in the quote. Tokens are normalised as `street_key` normalises a street line: suffixes, ordinals and number words. Direction words are skipped when the first street word is chosen, and so is a single letter that belongs to the civic number ("2210 C Larkspur Rd").
   - Absent is FAIL: `street_absent_from_quote`.
   - A record with no street is UNINSPECTABLE: `web_record_no_street`. So is a street with no civic number: `record_street_no_civic_number`.
3. **Name.** On a `directory` or `press` row, a name the record holds (`name_key`) must appear in the quote. Otherwise the row is UNINSPECTABLE (`name_absent_from_quote`), not FAIL, because the page may name it outside the quoted span.

A web row passes only when it is bound and nothing failed:

- by the own-site domain, or for directory and press by a held name;
- for a site row, by the street as well. A site row with another claim type (`scope`, `parent`) stays UNINSPECTABLE (`web_site_row_no_street_claim`), because a domain or a name binds the company, not the plant.
- An organization `address` row also needs its headquarters city and state in the quote; otherwise it is `hq_absent_from_quote`.
- The ruling gives no test for `registry` or `government_filing` web rows. They are UNINSPECTABLE (`web_class_untested`) unless the street test fails them.

### Modes

- `--all [--head REF] [--out FILE]` reports every evidence row on a tree:
  - by verdict and reason;
  - by `created_by`;
  - by source family.

  It asserts that the rows judged equal the rows read, and that the evidence IDs are unique.
- `--new-since REF` is the pull-request gate.
  - **What it checks:** rows that are new since the merge-base with REF, or whose binding fields (`record_table`, `record_id`, `claim_type`, `claim_detail`, `source_ref`) changed. A re-pointed row is a new claim.
  - **Exit 1:** any FAIL row, or any UNINSPECTABLE row without a valid proof line (below).
  - **Exit 2:** an unreadable base, zero rows or a duplicate ID. The check fails closed.
- `--sample N --seed S [--since REF]` is an audit of the gate and admits nothing. It lists N PASS rows per `created_by` label, chosen by `sha256(seed:evidence_id)`, for a reviewer to read. The share of those rows found unbound measures the gate's escape rate. Sampling never admits a row (controller ruling 2026-11-22). A clean sample of 30 still misses a 1% defect rate about 74% of the time, and it says nothing about the source of any row it did not draw.
- `--provenance-since REF` exits 1 when a `created_by` label of an added row does not name a `tasks/<folder>/` holding a `check.py`. The whole label counts, and so does any one of its words.

Rows already on `main` are not failed. `--all` reports them.

### No waivers; UNINSPECTABLE rows are admitted only by a per-row proof

There is no waiver file and no sample admission (controller rulings 2026-11-22; the per-row proof supersedes an earlier 30-row sample).

- **FAIL rows.** A FAIL row is never waived. Fix the row, or take it out and hold it as a lead.
- **UNINSPECTABLE rows.** Each one needs its own line in `tasks/<folder>/BINDING_PROOF.csv`. The folder is named by the `created_by` label or one of its words, as for `check.py`. The header is `evidence_id,capture,capture_sha256,quote_offset,quote_length`:
  - `capture`: where the quote was read. That is either the row's Wayback archive ref or a repo path under `tasks/` to a stored capture.
  - `capture_sha256`: 64 lowercase hex digits.
  - `quote_offset`, `quote_length`: the quote's character position in the capture. The length must be above zero.
- **What the gate verifies.**
  - Every UNINSPECTABLE row has a proof line, and an evidence ID has at most one.
  - The hash and the offsets are well-formed.
  - An archive capture equals the row's `data/archive_links.csv` `archive_ref` where one exists, and in any case has the Wayback form.
  - For a capture stored in the repo, the gate verifies it: the file's sha256 must match, and the row's quote must sit at exactly that offset.
  - A row with no proof line fails the PR. It stays a lead until someone proves it.
- **What CI does not do.** CI does not fetch the web, so an archive capture's hash and offset are not checked in CI. The lane's own `check.py` replays the quote against the capture, and the reviewing family re-runs it.

### CI

`.github/workflows/validate.yml` runs both PR modes against `origin/<base>`, after the row-loss guard, on pull requests only.

## Verdict tables

Counts below are evidence rows.

**`main` at 8f30ce0f** (the branch cut, where batches 5 and 6 were still on it; PR #465, 3ce1cc73, has since reverted them):

| Filter | Rows | PASS | FAIL | UNINSPECTABLE |
| --- | ---: | ---: | ---: | ---: |
| All evidence rows | 81,510 | 22,605 | 13,095 | 45,810 |
| Without the rows PRs #457 and #458 added | 47,416 | 1,706 | 204 | 45,506 |

Outside the two join batches, only web quotes are inspectable (next section). Of the 45,506 UNINSPECTABLE rows there, 41,461 carry no quote.

A pull request that added all of `main` today would owe 45,810 proof lines. 5,363 of those rows already have a `data/archive_links.csv` capture.

**Quarantined batches** (rows PRs #457 and #458 added, 4ee02127 → 17834918):

| `created_by` | Rows | PASS | FAIL | UNINSPECTABLE |
| --- | ---: | ---: | ---: | ---: |
| spaghetti-batch5-2026-11-22 | 10,352 | 6,870 (66.4%) | 3,364 (32.5%) | 118 |
| spaghetti-batch6-2026-11-22 | 23,564 | 13,925 (59.1%) | 9,517 (40.4%) | 122 |
| spaghetti-burndown-batch1-2026-11-21 (re-added in #457) | 122 | 90 | 6 | 26 |
| spaghetti-burndown-batch2-2026-11-21 (re-added in #457) | 56 | 14 | 4 | 38 |
| **Both PRs** | **34,094** | **20,899 (61.3%)** | **12,891 (37.8%)** | **304** |

These rows would owe 304 proof lines. 178 of those rows have an archive capture at 17834918.

FAIL and UNINSPECTABLE reasons in the batches, by row:

| Reason | Rows |
| --- | ---: |
| `name_not_held` | 4,590 |
| `street_differs` | 3,628 |
| `record_no_street` | 2,732 |
| `hq_from_s5_identity_source` | 627 |
| `name_not_held+street_differs` | 474 |
| `quote_no_street` | 406 |
| `name_not_held+record_no_street` | 252 |
| web quotes: `web_record_no_street` 139, `web_class_untested` 17, `not_own_site` 15, `no_record_website` 13, `name_absent_from_quote` 9, `street_absent_from_quote` 5 | 198 |
| `operator_not_a_name` | 98 |
| `hq_from_facility_or_permit` | 74 |
| `name_not_held+quote_no_street` | 70 |
| `no_civic_number` | 24 |
| `unit_differs` | 14 |
| other (`parse_failed` 4, two `name_not_held+unit_differs`, two mixed HQ rows) | 8 |

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
| URL (web quote) | 166 | 20 | 178 |

## Web quotes on `main` under the 2026-11-22 ruling

Before the ruling, all 3,347 web-quote rows on `main` were UNINSPECTABLE. Under the three tests:

| Filter (web-quote rows on `main` at 8f30ce0f) | Rows | PASS | FAIL | UNINSPECTABLE |
| --- | ---: | ---: | ---: | ---: |
| Burn-down batches 1 to 4 (`created_by` spaghetti-burndown-batch1 to 4, spaghetti-drift-rewitness, spaghetti-nourl-cleared, all 2026-11-21) | 2,846 | 1,642 | 210 | 994 |
| All other web-quote rows | 501 | 230 | 14 | 257 |

The 2,846 burn-down rows by reason:

| Verdict and reason | Rows |
| --- | ---: |
| PASS | 1,642 |
| UNINSPECTABLE `web_record_no_street` (site row, record has no street) | 677 |
| UNINSPECTABLE `no_record_website` | 192 |
| FAIL `not_own_site` | 113 |
| UNINSPECTABLE `web_class_untested` (registry, government_filing) | 96 |
| FAIL `street_absent_from_quote` | 93 |
| UNINSPECTABLE `hq_absent_from_quote` | 12 |
| UNINSPECTABLE `name_absent_from_quote` | 9 |
| UNINSPECTABLE `record_street_no_civic_number` | 8 |
| FAIL `street_absent_from_quote+not_own_site` | 4 |

By record and claim, the PASS rows are 595 organization existence, 417 organization address, 317 site existence, 311 site address and 2 ecosystem existence.

What bound the 1,872 web PASS rows on `main` (measured on the false-PASS side):

- 1,824 rows are bound by the own-site domain.
- 48 are bound by a held name in a directory or press quote. For 15 of them the shortest matching name is one word, which a quote could contain by chance.
- On every web site PASS row, the civic number and the first street word stand within two tokens of each other.

**The 734 people rows** (`spaghetti evidence-backfill-w1-2026-11-19`, all `own_site` existence) carry no quote, and the ruling's tests are written for sites and organizations. They stay UNINSPECTABLE (`other_table`), and the street and name tests cannot run on them. The one test that could run is the domain test. Measured against the website of the person's institution, it gives:

- 676 rows on the institution's domain;
- 23 rows off it;
- 35 rows whose institution has no website.

The gate does not apply it. A PR adding these rows would owe 734 proof lines, one per row.

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
| FREETEXT → PASS (web-quote tests) | 1,743 |
| FREETEXT / OTHER_TABLE / NO_QUOTE → UNINSPECTABLE | 2,549 (1,108 / 804 / 637) |
| FREETEXT → FAIL (web-quote tests) | 224 |
| FAIL → PASS | 128 |
| PASS → UNINSPECTABLE | 106 |
| FAIL → UNINSPECTABLE | 20 |

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
| Web quote, bound by own-site domain or held name (and street, for sites) | 166 |

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
7. **Not open: headquarters from identity-only sources.** SCHEMA §4.8 S-5 already rules on this. State-entity and FMCSA addresses are identity-only: a state filing's address may be an agent's, and the FMCSA address is the carrier's filed address. These 627 rows therefore fail under an existing owner ruling:
   - 343 state-entity `principal_address` rows;
   - 284 FMCSA rows.

   Each would otherwise pass on name, city and state. The count is kept for the record, not as a question.
8. **USAspending and SBIR as headquarters sources** (333 rows pass): I treated both as stating the entity's own address. But a UEI can be registered for a single plant, and an SBIR address dates from the award year.
   - USAspending recipient addresses come from SAM registrations. R-SAM (2026-11-16) bars copying a SAM name or address into the Atlas.
   - The 2026-11-22 ruling (DECISIONS.md) lifts that bar for the public SAM extract only.
   - Whether USAspending counts as SAM under R-SAM is your ruling.
9. **Shifted columns** (NC DEQ, 98 rows): 94 would pass if the facility label were read as the operator.
10. **Web quotes.** These are measured on `main`; nothing in this list passes.
    - **Sister domains.** 67 `not_own_site` rows sit on a host that carries a held name (a regional or sister domain, such as a `-usa` variant). Should another domain owned by the company count as its own site? Only a registry of company domains could tell.
    - **Spacing.** 12 `street_absent_from_quote` rows show the street once spacing is ignored ("Bragg Ridge" against "Braggridge").
    - **Classes with no test.** `registry` and `government_filing` web rows have no test of their own, so 131 rows on `main` are `web_class_untested`. Which test should they get?
    - **People rows.** The domain test is not applied to them (734 rows; 23 off the institution's domain).

The strict reading ships. Questions 1 to 6 and 8 to 10 stay open, with their measured counts, until re-admission starts.

## Replay: the last 40 commits under these rules

The replay runs `replay.py` over the last 40 first-parent commits on `main` up to 8f30ce0f, judging each one against its parent. 24 of the 40 added or re-pointed evidence rows. "Needs a proof line" counts every UNINSPECTABLE row: each one would have needed its own line in a `BINDING_PROOF.csv`. "With an archive link" counts those rows that had a `data/archive_links.csv` capture at that commit. No commit carried a proof file.

| Commit | Subject | Rows | PASS | FAIL | UNINSPECTABLE | Needs a proof line | … with an archive link | Binding gate | Provenance |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 178349185 | Merge pull request #458 from polymerindustrycluster/agent/sp | 23,564 | 13,925 | 9,517 | 122 | 122 | 0 | fail | fail |
| 6a76e923f | Merge pull request #457 from polymerindustrycluster/agent/sp | 10,530 | 6,974 | 3,374 | 182 | 182 | 178 | fail | fail |
| 4924083cd | R2 re-capture recovery mint: 39 evidence rows + 39 archive l | 39 | 19 | 8 | 12 | 12 | 12 | fail | fail |
| 4ea038848 | Phase C unit 3: 22 accuracy corrections (EVD-425415..425436 | 22 | 0 | 0 | 22 | 22 | 22 | fail | fail |
| b99fd9e1e | Burn-down batch 4: R1 re-witness mint — 240 evidence rows + | 240 | 134 | 24 | 82 | 82 | 82 | fail | fail |
| a514c67d8 | Burn-down batch 3 build F: wave-3 requeue mint — 124 evidenc | 124 | 80 | 7 | 37 | 37 | 37 | fail | fail |
| 9b2276f2e | Burn-down batch 3 build E2: quote-defect mint — 233 evidence | 233 | 121 | 13 | 99 | 99 | 99 | fail | fail |
| c67ad8314 | Burn-down batch 3 build E1: drift-recovered2 mint — 27 evide | 27 | 13 | 1 | 13 | 13 | 13 | fail | fail |
| f06631bc6 | Batch-2 drift-recovered mint: 178 evidence rows for 104 reco | 178 | 78 | 20 | 80 | 80 | 80 | fail | fail |
| c29df58e8 | No-URL cleared set: 16 two-family-reviewed evidence rows for | 16 | 7 | 2 | 7 | 7 | 7 | fail | fail |
| 120ec9204 | Drift re-witness mint: 53 evidence rows for 28 records recov | 53 | 37 | 4 | 12 | 12 | 12 | fail | fail |
| c2b1d1803 | Evidence burn-down batch 2: wave-3 backfill (1,276 rows, 699 | 1,276 | 694 | 105 | 477 | 477 | 477 | fail | fail |
| 5219c5d79 | Evidence burn-down batch 1: wave-2 backfill (482 rows, 255 r | 482 | 353 | 16 | 113 | 113 | 113 | fail | fail |
| 117e38707 | Phase C unit 2: 22 PIC-18 street fills from the judgment-que | 22 | 0 | 0 | 22 | 22 | 21 | fail | fail |
| dd38735d8 | Phase C unit 1: 32 department-row programs created from the | 32 | 0 | 0 | 32 | 32 | 32 | fail | fail |
| 01ef298ec | Merge pull request #436 from polymerindustrycluster/agent/cl | 152 | 0 | 0 | 152 | 152 | 0 | fail | fail |
| 3f448ea18 | Merge pull request #435 from polymerindustrycluster/agent/cl | 120 | 0 | 0 | 120 | 120 | 0 | fail | fail |
| 248e94099 | Merge pull request #434 from polymerindustrycluster/agent/cl | 251 | 0 | 0 | 251 | 251 | 0 | fail | fail |
| 18cb709c5 | Merge pull request #432 from polymerindustrycluster/agent/cl | 80 | 0 | 0 | 80 | 80 | 0 | fail | fail |
| 5fa5ba937 | Merge pull request #427 from polymerindustrycluster/agent/cl | 23 | 23 | 0 | 0 | 0 | 0 | pass | fail |
| edd9591c9 | Merge pull request #424 from polymerindustrycluster/agent/cl | 2 | 0 | 0 | 2 | 2 | 0 | fail | fail |
| 6c29fa6c4 | IPEDS CIP fills: 26 degree programs (EVD-400340..EVD-400365) | 26 | 0 | 0 | 26 | 26 | 0 | fail | fail |
| 209be678e | Evidence backfill wave 1: 734 tier-A people existence witnes | 734 | 0 | 0 | 734 | 734 | 0 | fail | fail |
| d48ce7e6a | Hygiene sweep (audit F11): Farathane duplicate merged, APT s | 5 | 0 | 0 | 5 | 5 | 0 | fail | fail |
| **24 commits** | | **38,231** | **22,458** | **13,091** | **2,682** | **2,682** | **1,185** | 1 pass | 0 pass |

- **Proof lines.** Across the 24 commits, 2,682 rows would have needed a proof line. 1,185 of them had an archive capture to cite.
- **Binding gate.** One of the 24 commits would have passed: PR #427 (5fa5ba937), with 23 rows that all PASS. Every other commit had a FAIL row, or UNINSPECTABLE rows with no proof lines.
- **Provenance.** The provenance check fails all 24 commits; no commit's `created_by` named a `tasks/<folder>/check.py`. This 24-of-24 failure is the baseline the rule starts from, not a defect in the rule.

## What this gate cannot see

- **Truth.** The gate checks that a quote is about the record, not that the quote is faithful to its source or that the source is current.
  - It fetches nothing.
  - An extract older than an operator change can still pass. For example, a permit held by the new operator under the old street would pass.
  - Spotcheck §6 checked 15 quotes against the EPA bulk tables by hand.
- **The city.** For a site row the gate binds the street, not the city.
  - 242 of the 18,592 structured-source site PASS rows in the batches quote a city other than the record's, e.g. EVD-438149 and EVD-448255. (The other 39 site PASS rows are web quotes, which the city is not read from.)
  - Some are mailing names for the same place (a big city's name for a suburb). Others may be a same-named street in another town.
  - The quoted state agrees with the record on every site PASS row in the batches: 0 differ, and the state was read on 18,582 of 18,592.
  - County is not checked at all.
- **Identity behind an equal name or domain.** An unrelated namesake at the same street would pass. Organization existence rows are judged on the name alone, or for a web quote on the domain alone. A web row passes on its own site even when the record's `website` was itself filled from that page.
  - The 57 Motiva permits for distinct stores pass existence 57 times from one registry. The gate does not measure that correlation.
  - The 57 matching headquarters rows fail.
- **The claim's own value.** The gate compares the quote with the record's current fields, not with the value `claim_detail` asserts. If a record field changes later, the row's verdict can change.
- **Tier ceilings.** The §4.13 `tier_effect` class ceilings are not checked. Neither is `address_role`.
- **Field edits.** An edit to a row's tier effect, date or notes is not re-gated. Only a change to its binding fields is.
- **Free text.** A web quote is bound only by the three mechanical tests. A quote that prints the right street and sits on the right domain can still be about something else on that page. Rows without quotes (41,461 on `main`) are UNINSPECTABLE, as is every row outside the bulk-join formats and the web tests.
- **Proofs.** For an archive capture, CI checks the form of the proof line, not its truth. A stored capture proves that the quote is in that file, not that the file is the page the source served. Neither shows that the quote binds to the record: a proof line admits an UNINSPECTABLE row on the strength of its capture alone.
- **Provenance.** The provenance check proves that a `check.py` exists. It does not prove that the script runs or that it reproduces the rows.

## Checks

| Check | Command | Result |
| --- | --- | --- |
| Gate unit tests | `cd scripts && python3 -m unittest test_check_evidence_binding` (CI runs them through `scripts/run_tests.py`) | 57 tests OK. They cover planted defects, true matches, uninspectable rows, the web tests, proof lines and the audit sample, all synthetic strings shaped like real rows. They also include a known-answer replay: `--new-since 6a76e923 --head 17834918` and `--provenance-since` on the same range both exit 1, and the batch 6 replay prints the missing proof file. |
| This folder's check | `python3 tasks/evidence-binding-gate-2026-11-22/check.py` | 101 numbers OK. See the two rows below. |
| Leak guard (inside `check.py`) | — | 0 of the 184 street-, ID- or name-like segments in the test strings occur in any `claim_detail` at 17834918. A planted real fragment is caught. |
| Mutation check (inside `check.py`) | — | Copies of the gate each loosen one rule, and the tests catch every loosening. Failing tests per loosening: token-subset names 6; number-only streets 2; no unit test 1; HQ from any source 2; any web domain 4; web street by civic number only 2; web name unchecked 1; proof quote not checked at its offset 1; proof archive ref not matched 1. |
| Replay | `python3 tasks/evidence-binding-gate-2026-11-22/replay.py` | Writes `replay.csv`; the table above. |

The remaining repository checks are recorded in the PR.
