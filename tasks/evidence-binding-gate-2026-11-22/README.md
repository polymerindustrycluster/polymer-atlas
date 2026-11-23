# Evidence binding gate (2026-11-22)

Built by: Claude Code, Anthropic

On 2026-11-22, batches 5 and 6 (PRs #457 and #458) added about 34,000 evidence rows that were joined by machine. Every check passed. The controller's first-cut test found that 28% of those rows do not bind to the record they are filed on:

- the quote names another operator;
- the quote prints another street;
- or a headquarters is claimed from a plant permit.

`validate.py` checks a row's form, never whether its quote is about that record. The owner ruled both batches reverted (PR #465 did that), and ruled that a row returns only if it passes a hardened binding gate. This folder holds that gate's record.

This is the third round. Codex refuted the first round with 8 blocking and 3 follow-up findings (`S/reviews/467-r1-review-codex.md`), and the controller's rulings A to G followed. Codex refuted the second round with 6 blocking findings (`S/reviews/467-r2-review-codex.md`). The two-round cap sent it to the owner, who ruled on 2026-11-22, as multiple choice, to **split** the PR:

- **This PR is the gate for structured rows only.** It fixes Codex r2 findings 2, 3 and 4 (location conflicts, bare site labels, parent names).
- **No web admission here.** A web row is FAIL or READ_REQUIRED, and a READ_REQUIRED or UNINSPECTABLE row fails the PR. Per-row proofs, readings, `--verify-proofs`, archive fetching and running a folder's `check.py` moved to branch `agent/claude-code/evidence-binding-web-proofs-2026-11-22` (no PR yet), with Codex r2 findings 1, 5 and 6 as its to-do list.
- **Provenance is presence only.** Nothing from the gated tree is executed.

The table at the end maps each finding to the test that now holds it.

Every number below comes from `python3 tasks/evidence-binding-gate-2026-11-22/check.py`, except the replay table, which comes from `replay.py` beside it (written to [replay.csv](replay.csv)). `check.py` reads pinned commits and fails if any of its 120 numbers drifts. Rows are cited by `evidence_id` only.

## What the gate decides

`scripts/check_evidence_binding.py` gives every evidence row exactly one verdict.

| Verdict | Meaning | Reasons |
| --- | --- | --- |
| PASS | **Structured sources only.** The quoted operator is a name the record itself holds, by exact `name_key` of the whole field; a site-name part counts unless every token in it is a generic label. On a site row whose street passes, a held name followed only by corporate-form words also binds (owner ruling 2026-11-22). A recorded parent's name never binds. For a site row, `scripts/matching.py` `same_street()` holds, and a quoted city or state equals the site's. For an organization `address` row, the source states the entity's own address (USAspending recipient, SBIR firm) and the quoted city and state are the record's headquarters. | — |
| FAIL | The quote is about something else. No waiver exists. | `name_not_held`, `parent_name_lead` (the filing names only a recorded parent: a lead to be read), `street_differs`, `unit_differs`, `state_differs`, `city_differs`, `record_no_street`, `quote_no_street`, `hq_from_facility_or_permit`, `hq_from_s5_identity_source`, `hq_city_state_differs`; web: `not_own_site`, `street_absent_from_quote`, `unit_differs` (several may join with `+`) |
| READ_REQUIRED | A web quote that the mechanical tests did not fail. A web quote is never PASS. | `mechanics_clear`, `no_record_website`, `name_absent_from_quote`, `web_record_no_street`, `record_street_no_civic_number`, `web_class_untested` |
| UNINSPECTABLE | The gate cannot read the row. It is never a pass. | `no_quote`, `other_table`, `record_not_found`, `unknown_source_family`, `parse_failed`, `operator_not_a_name`, `no_civic_number` |

A PR is admitted only when every row it adds or changes is PASS. A FAIL, READ_REQUIRED or UNINSPECTABLE row fails it; the message says to take the row out and hold it as a lead, and that web admission lands in the follow-up.

### Structured rows: one street test for the whole repo (ruling B)

- **Street.** The site street test is `scripts/matching.py` `same_street()`. It moved there from `derive_last_activity.py` (#463), and both scripts import it; its tests are in `scripts/test_matching.py`. The gate's structured street PASS is exactly `same_street(site street, quoted street)`:
  - the two `street_key` values are equal;
  - the key has a civic number and at least one more token;
  - no designator conflicts: when both sides state a suite or unit, they agree, and when both state a building, they agree (`matching.designators_conflict()`, new this round). A designator on one side only is not a conflict.

  The gate's street part keeps every designator-only comma part beside the street, in dotted and abbreviated forms ("Ste. 300", "Bldg. A", "Building B", "#12"), so the designator test sees it; the first two rounds dropped "Ste. 300" before the test (Codex r2 finding 2). The gate only adds a reason on the failing side: `street_differs`, `unit_differs`, `quote_no_street`, `record_no_street`, or `no_civic_number` (UNINSPECTABLE) for equal keys that name no place. The #463 example EVD-431716 / SITE-002988 (a building number with no street) is UNINSPECTABLE, not PASS.

  The derivation uses the same `same_street()`, so the building rule reaches it too. Re-derived on the #463 extracts against the 393c3895 site shards, all 7,196 site pairs are unchanged (2,632 populated, 4,564 empty), and `tasks/last-activity-street-leg-2026-11-22/check.py` passes.
- **City and state** (Codex r2 finding 2). The city and state printed after the street are read with or without a ZIP ("…, DOVER, OH 44101", "…, DOVER, TX", "…, DOVER OHIO", "…, DAYTON"). A quoted state other than the site's is FAIL `state_differs`, as a two-letter code or a full state name. A quoted city other than the site's is FAIL `city_differs`, unless the quoted ZIP5 equals the site's `zip`. Both halves are controller rulings of 2026-11-22 within the owner's standard, not owner rulings. City names are compared as spellings of one name, never as nearby places: Mt/St/Ft/Pk spelled out, "City of X" and a trailing Township/City/Town/Village/Borough dropped, spaces ignored ("MC COOK" is McCook), ECHO's "SPRINGFIELD, TOWNSHIP OF" read as Springfield, and either part of a record city written with a second locality in parentheses ("Cleveland (Solon)", "Killingly (Dayville)"). A quoted county is not a city and is not compared. A ZIP is read as 5 digits, ZIP+4 or 9 digits; a 4-digit ZIP, "317E6", "00000" or a foreign postcode never matches. The test lives in `scripts/matching.py` (`city_keys`, `zip5`, `city_differs`, and `same_locality` for the derivation follow-up below), so the gate and the derivation can share it. Two readings of the ruling are mine: a quote with no city, or a site with no city, is not contrary evidence (as before), and a quoted other state stays its own reason, `state_differs`, which an equal ZIP never overrides.
- **Operator.** A permittee, operator or establishment field is one name. It is never split on commas, so "Other Operator, Acme Polymer" does not match Acme Polymer. On a permit, the operator is the permittee, not the facility label.
- **Site-name parts** (Codex r2 finding 3; owner ruling 2026-11-22, "drop generic labels only"). A site name yields keys: the whole name, the name less its trailing locality, and each " - " part that is not the city. A key is ignored as a held name only when every token in it is a generic label from the one fixed list in `scripts/matching.py` (`GENERIC_LABELS`, `generic_label()`):
  - facility words: plant, facility, warehouse, works, site, office, HQ, headquarters, building, unit;
  - a number or ordinal (2, #2, 2nd, two, second, and "No." / "Number" before it);
  - a compass word (north, NE, …);
  - a US state, by name or code (the 50 states and DC);
  - the site's own city or county.

  Any other part (a brand, a division, a trading name) counts as a held name. So a permit naming only "Plant 2", "North Works", the site's city or its county fails `name_not_held`, while "Tamarack" on a site of Tamarack Rubber Company binds. "Main" was added to the list later the same day (owner, relayed by the controller), so "Main Plant" is a label too; no site key on the tree is a label only because of "main", so no row changes.
- **Corporate-form words** (owner ruling 2026-11-22, `DECISIONS.md`). On a site row whose street already passes `same_street()`, a quoted name also binds when a held name is a leading run of it and every extra token is one of: Inc, Incorporated, LLC, L.L.C., Corp, Corporation, Co, Company, Ltd, Limited, LP, LLP, Holdings, Holding, Group, US, USA, U.S., North America, Americas. The rule is `matching.corporate_form_extension()`. It does not apply to web rows, to organization rows (they have no street test), or to predecessor or notes-only names. "Acme Polymer Services" fails, and so does the fleet-services affiliate on EVD-455899.
- **Parent names** (Codex r2 finding 4; owner ruling 2026-11-22, "fail everywhere"). A filing that names only a recorded parent or ultimate parent (or that name plus corporate-form words), and none of the operator organization's own names, never binds a subsidiary's record by machine, on any path, including when the parent's name is part of the site name. It is FAIL `parent_name_lead`: a lead to be read. "Acme Polymer Holdings" on a site of Acme Polymer whose ultimate parent is Acme Polymer Holdings fails this way, whether or not the site is named "Acme Polymer Holdings - Elm Works". - **Other parsing.** Quote parsing uses an explicit table of source families (ECHO, OSHA, FMCSA, state entity files, USAspending, SBIR and nine state permit layers); any other source is `unknown_source_family`. A permittee field with no letters (`operator_not_a_name`) is the NC DEQ layer's shifted columns.

### Web quotes: FAIL or READ_REQUIRED, never PASS (ruling A)

A web quote (`source_ref` starting with `http`) is free text. Code can show that it is not about the record. It cannot show that it is: a quote with the right street and name can still describe a sibling plant, a former operator or a satellite office. So the mechanical tests can only fail a row, and in this PR a row they do not fail is held (READ_REQUIRED), which fails the PR.

1. **Own site.** For an `own_site` row, the URL must be on the record's own website. That is the site's organization's `website`, or the organization's own.
   - Registrable domains are compared: the last two host labels, or three under a country second level such as `co.uk`. `www.` is ignored, and a sibling subdomain matches.
   - **Platform hosts.** On a shared platform host (atlas `PLATFORM_HOSTS` plus pages.dev, netlify.app, vercel.app, github.io, wixsite, sites.google and others), both the host and the path must match the record's website. A bare platform root never matches. So `other-molder.pages.dev` is not `acme.pages.dev`.
   - Off the record's website is FAIL `not_own_site`.
2. **Street** (site `address` or `existence` rows, any web class). The record's civic number must be immediately followed by its first street word. A direction or a single letter may sit between. Tokens are normalised as `street_key` normalises a street line.
   - The suffix is not compared: "321 Oak Avenue" for "321 Oak Street" is READ_REQUIRED, not FAIL. A suffix test was tried in round two and dropped, because on `main` it failed real matches whose quote carried a direction word ("1920 Tampa E Blvd" style).
   - A number that is a phone area code or a ZIP is not followed by the street word, so it does not count.
   - Absent is FAIL `street_absent_from_quote`.
   - If the record states a suite or unit, and every occurrence of the street in the quote states only other suites, the row is FAIL `unit_differs`.
3. **Name** (`directory` and `press` rows). If no held name appears in the quote, the row is READ_REQUIRED (`name_absent_from_quote`).

When nothing fails, the row is READ_REQUIRED. Its reason says what the reader must settle (`mechanics_clear` when every test ran).

### Modes

- `--all [--head REF | --tree DIR] [--out FILE]` reports every evidence row on a tree, by verdict and reason, by `created_by` and by source family. It asserts that the verdict counts sum to the rows read. It also checks the CSV row count against an independent count of lines that open with an evidence ID, and that the evidence IDs are unique.
- `--new-since REF` is the pull-request gate.
  - **What it checks:** every row that is new since the merge-base with REF, and every row that differs from its base row in **any** column (ruling D). A column absent on one side counts as empty, so a migration that adds an empty column edits no row.
  - **Exit 1:** any FAIL, READ_REQUIRED or UNINSPECTABLE row.
  - **Exit 2:** an unreadable base, zero rows or a duplicate ID. The gate fails closed.
- `--provenance-since REF` applies the provenance rules (below).
- `--sample N --seed S [--since REF]` is an audit of the gate and admits nothing. It lists N PASS rows per `created_by` label, chosen by `sha256(seed:evidence_id)`, for a reviewer to read.
- `--tree DIR` reads `data/` and `tasks/` from DIR instead of this checkout (see "Trust boundary").

Rows already on `main` are not failed. `--all` reports them.

## Provenance (ruling E, presence only)

A `created_by` label names exactly one folder:

- a one-word label names the folder of that exact name;
- a two-word label names the folder of its exact second word, because the first word is the harness (`claude-code lane-a` names `lane-a`);
- any other label names no folder.

There is no prefix match, no extra token and no date variant. `--provenance-since` fails a PR when any label of an added or changed row:

- names no folder;
- names a folder with no `check.py`, or an empty one;
- is new to the base while its folder already exists there (a new label adds its own folder in this PR).

**The gate checks presence only. It executes nothing from the PR tree.** The replay a folder's `check.py` performs is run by the lane that built the rows, and again by the reviewing family, and their results go in the PR. A present, non-empty `check.py` says nothing about whether it reproduces the rows.

## Trust boundary (ruling F)

The `validate` job checks out the PR and runs the PR's own copy of this checker. A PR that edits the checker or the workflow changes the result. So the two binding steps in `validate.yml` (`--new-since`, `--provenance-since`) are early feedback, labelled "not authoritative" in `docs/ci/README.md`.

The authoritative run belongs to the rules lane (atlas-w22-rules, PR #466). It is a `pull_request_target` workflow that runs `main`'s checker against the PR's files with `--tree <PR checkout>`. With `--tree`:

- `data/` and `tasks/` are read from that directory;
- symlinks are refused, as are paths that resolve outside it; a symlinked evidence shard stops the run (exit 2);
- nothing from it is executed;
- the base is the REF itself, because a plain directory has no history (the workflow checks out the PR merge ref).

## Verdict tables

Counts below are evidence rows.

**`main` today (393c3895, after #463):** 47,416 rows. 0 PASS, 207 FAIL, 2,776 READ_REQUIRED and 44,433 UNINSPECTABLE. Under ruling A no web row passes, and every PASS on `main` was a web row. 41,461 of the UNINSPECTABLE rows carry no quote. A PR that added all of `main` would fail on all 47,416: 207 FAIL and 47,209 held. 6,744 of the held rows have an archive capture the follow-up's per-row proof could cite.

**`main` at 8f30ce0f** (the branch cut, still holding batches 5 and 6): 81,510 rows. 20,705 PASS, 13,108 FAIL, 3,120 READ_REQUIRED and 44,577 UNINSPECTABLE.

**Quarantined batches** (rows PRs #457 and #458 added, 4ee02127 → 17834918):

| `created_by` | Rows | PASS | FAIL | READ_REQUIRED | UNINSPECTABLE |
| --- | ---: | ---: | ---: | ---: | ---: |
| spaghetti-batch5-2026-11-22 | 10,352 | 6,800 (65.7%) | 3,366 (32.5%) | 176 | 10 |
| spaghetti-batch6-2026-11-22 | 23,564 | 13,905 (59.0%) | 9,525 (40.4%) | 0 | 134 |
| spaghetti-burndown-batch1-2026-11-21 (re-added in #457) | 122 | 0 | 6 | 116 | 0 |
| spaghetti-burndown-batch2-2026-11-21 (re-added in #457) | 56 | 0 | 4 | 52 | 0 |
| **Both PRs** | **34,094** | **20,705 (60.7%)** | **12,901 (37.8%)** | **344** | **144** |

488 rows are held (READ_REQUIRED or UNINSPECTABLE) and fail the gate. 344 of them have an archive capture at 17834918.

FAIL, READ_REQUIRED and UNINSPECTABLE reasons in the batches, by row:

| Reason | Rows |
| --- | ---: |
| `name_not_held` | 4,508 |
| `street_differs` | 3,554 |
| `record_no_street` | 2,720 |
| `hq_from_s5_identity_source` | 627 |
| `name_not_held+street_differs` | 492 |
| `quote_no_street` | 434 |
| web READ_REQUIRED: `mechanics_clear` 166, `web_record_no_street` 139, `web_class_untested` 17, `no_record_website` 13, `name_absent_from_quote` 9 | 344 |
| `name_not_held+record_no_street` | 252 |
| `operator_not_a_name` (UNINSPECTABLE) | 98 |
| `hq_from_facility_or_permit` | 74 |
| `name_not_held+quote_no_street` | 72 |
| `parent_name_lead` (new this round) | 68 |
| `city_differs` (new this round): alone 12, with `street_differs` 14, with `name_not_held` 12, three-way 8 | 46 |
| `no_civic_number` (UNINSPECTABLE) | 42 |
| web FAIL: `not_own_site` 15, `street_absent_from_quote` 5 | 20 |
| `parent_name_lead` with another reason (`record_no_street` 12, `street_differs` 2, `quote_no_street` 2) | 16 |
| `unit_differs` | 14 |
| other (`parse_failed` 4, two `name_not_held+unit_differs`, two mixed HQ rows) | 8 |

Round two failed 12,857 of these rows; round three fails 12,901. By a one-off run of the round-two gate (c6b6f83b) on the same rows, which `check.py` cannot reproduce because that code is gone, the 44 more are all round-two PASS rows: 24 name only a recorded parent (`parent_name_lead`; 10 of them bound through a site-name part), 12 quote another city with another or no readable ZIP, 4 state another suite, and 4 name only a generic label. 46 rows carry `city_differs` in all. No batch row quotes another state.

**The ZIP5 rule, measured.** Before it (head 1b4f49e1), 324 batch rows carried `city_differs`, 152 of them round-two PASS rows. With it, 278 of the 324 lose the reason: 140 become PASS and 138 still fail for another reason. 46 keep it. All 278 changes come from the ZIP5 leg. The parenthetical leg changed none: the gate already read both parts of a parenthetical city, and only 13 sites on the tree (9 in Ohio) have one.

By source family (PASS / FAIL / READ_REQUIRED / UNINSPECTABLE):

| Source family | PASS | FAIL | READ_REQUIRED | UNINSPECTABLE |
| --- | ---: | ---: | ---: | ---: |
| EPA ECHO | 9,354 | 7,142 | 0 | 30 |
| OSHA | 6,800 | 3,356 | 0 | 10 |
| FMCSA Company Census | 1,787 | 480 | 0 | 2 |
| state-entity-files-bulk | 580 | 344 | 0 | 0 |
| USAspending bulk | 667 | 4 | 0 | 0 |
| TCEQ Central Registry | 209 | 431 | 0 | 0 |
| PA DEP | 316 | 244 | 0 | 2 |
| Ohio EPA | 60 | 478 | 0 | 0 |
| NC DEQ ArcGIS | 183 | 165 | 0 | 98 |
| URL (web quote) | 0 | 20 | 344 | 0 |
| CA DTSC | 310 | 52 | 0 | 0 |
| CA SWRCB | 204 | 38 | 0 | 0 |
| SBIR/STTR bulk | 93 | 79 | 0 | 2 |
| IN IGMAP | 96 | 40 | 0 | 0 |
| NJDEP | 46 | 16 | 0 | 0 |
| GA EPD | 0 | 12 | 0 | 0 |

## Web quotes on `main` today

| Filter (web-quote rows on `main` at 393c3895, excluding `no_quote` and `other_table`) | Rows | FAIL | READ_REQUIRED |
| --- | ---: | ---: | ---: |
| Burn-down batches 1 to 4 (`created_by` spaghetti-burndown-batch1 to 4, spaghetti-drift-rewitness, spaghetti-nourl-cleared, all 2026-11-21) | 2,668 | 203 | 2,465 |
| All other web-quote rows | 315 | 4 | 311 |

The 2,668 burn-down rows by reason:

- READ_REQUIRED: `mechanics_clear` 1,550, `web_record_no_street` 638, `no_record_website` 181, `web_class_untested` 80, `name_absent_from_quote` 8, `record_street_no_civic_number` 8;
- FAIL: `not_own_site` 101, `street_absent_from_quote` 95, `street_absent_from_quote+not_own_site` 5, `unit_differs+not_own_site` 2.

**The 734 people rows** (`spaghetti evidence-backfill-w1-2026-11-19`, all `own_site` existence) carry no quote. They are UNINSPECTABLE (`other_table`). Measured against the website of the person's institution, 676 sit on the institution's domain, 23 off it, and 35 belong to an institution with no website. The gate does not apply that test. A PR adding these rows would fail on all 734; the follow-up's proof line also needs a quote.

## Calibration against the hand-labelled spotcheck

These are the rows that `S/reviews/w1122-spotcheck.md` labelled by hand. Labels are carried in `check.py` by evidence_id only.

| Draw | Spotcheck label | Gate verdict |
| --- | --- | --- |
| Appendix A (OSHA address flags, 60) | DIFFERENT_ADDRESS (54) | FAIL 54 |
| | CANNOT_TELL (5) | FAIL 5 (none pass) |
| | SAME_PLACE (1, EVD-428624) | PASS 1 |
| Appendix B (exact-street name checks, 40) | DEFECT (5: EVD-449620, EVD-450128, EVD-457493, EVD-455899, EVD-457589) | FAIL 5 |
| | MATCH (35) | PASS 26, FAIL 9 |

The calibration is unchanged from round two. The 9 true matches that fail do so under the strict reading:

- held name plus a plant word: EVD-448086, EVD-446818;
- name variant: EVD-444906;
- division name: EVD-443796;
- operator named only in notes: EVD-445324;
- permittee is another legal string and only the facility label matches: EVD-457497, EVD-456891;
- `street_key` limit (one route written two ways): EVD-438364;
- the held name is one comma part of an OSHA establishment field: EVD-431182 (since round two a name field is no longer split).

Each is an owner question below.

## Measured disagreements with the first cut

The first cut is `S/audits/2026-11-22-binding-test/binding.py`, whose `verdicts.csv` sits outside the repo. Run `check.py --first-cut <path>` to reproduce this table. The first cut judged 38,226 rows (EVD-399606 and above) at 17834918.

| First cut → this gate | Rows |
| --- | ---: |
| PASS → PASS | 20,423 |
| FAIL → FAIL | 9,321 |
| PASS → FAIL | 3,696 |
| FREETEXT → READ_REQUIRED | 2,832 |
| OTHER_TABLE / NO_QUOTE → UNINSPECTABLE | 1,441 (804 / 637) |
| FREETEXT → FAIL (web tests) | 227 |
| FAIL → PASS | 126 |
| PASS → UNINSPECTABLE | 122 |
| FAIL → UNINSPECTABLE | 22 |
| FREETEXT → PASS (ECHO quotes the first cut did not parse) | 16 |

The first cut's FAIL share on the batch rows reproduces at 9,469 / 34,094 = **27.8%**, the 28% the brief cites. On the same rows this gate fails 38.3%.

- **Stricter (PASS → FAIL, 3,696).**
  - The first cut accepted any token subset, which passed a held name inside another name and a parent's name two levels up. This gate requires exact `name_key` equality of the whole field with a name the record holds, a site-name part only when it is not a generic label, and never a recorded parent's name.
  - The first cut passed facility-label matches.
  - The first cut never checked the city or the source of a headquarters claim against SCHEMA §4.8 S-5.
- **Looser (FAIL → PASS, 126).** The first cut's OSHA parser misread a suite in its own comma part, a city printed twice and a 4-digit ZIP. Its ECHO test rejected number-word streets ("One … Drive").
- **PASS → UNINSPECTABLE (122).** 98 are the NC DEQ shifted-column rows. The rest are equal street keys that name no place, such as a building number, and ECHO quotes the gate does not parse.

## The false-PASS side

The batch PASS rows, by which held name the whole quoted name matched:

| Name basis | Rows |
| --- | ---: |
| A name of the operator organization | 18,247 |
| The site name's leading part (not a generic label) | 1,288 |
| The full site name or another part of it (not a generic label) | 998 |
| A held name plus corporate-form words, street passing (owner ruling) | 172 |

**PASS means that the quote binds to the record, not that the row is admissible.** Tier ceilings and address roles remain the validator's and the integrator's job.

## Questions for the owner

The gate implements the strict reading. Each alternative is measured on the batch rows; none of them passes in the gate. "Would pass" means the row's only defect is the one named.

1. **Site-name parts. Ruled 2026-11-22, "drop generic labels only"** (see "Structured rows"). The stricter reading first implemented this round (a part must hold the organization's name tokens) failed 1,098 round-two PASS rows. Under the ruling 1,080 of them pass and 18 still fail. With the later ZIP5 rule the same comparison counts 1,104, because 6 rows that both readings failed on `city_differs` now pass the round-two reading (EVD-437963, EVD-437964, EVD-443573, EVD-443574, EVD-451785, EVD-451786): 1,086 pass and the same 18 still fail. 4 name only a generic label: a city plus a number (EVD-430449, EVD-430450) and a state plus "Plant" (EVD-435129, EVD-435130). The other 14 name only a recorded parent and fail `parent_name_lead` (EVD-449039, EVD-449040, EVD-439981, EVD-439982, EVD-449191, EVD-449192, EVD-457602, EVD-457603, EVD-441695, EVD-441696, EVD-445455, EVD-445456, EVD-434357, EVD-434358). The list is [finding3_still_fail.csv](finding3_still_fail.csv). "Main" was then added to the label list; it changes none of these counts.
2. **A held name plus more words** (`leading_run`). **Ruled 2026-11-22 for corporate-form words only** (see "Structured rows"). After the ruling and this round's rules, 1,789 rows still fail with a held name plus other words as their only defect, for example "ARMACOR LLC-CONOVER PLANT" against Armacor (modelled on EVD-445712). Plant words and other extensions stay open. The fleet-services affiliate on EVD-455899 still fails.
3. **Permit facility label when the permittee differs:** 154 rows would pass. Examples: EVD-457497 and EVD-456891.
4. **A parent's name. Ruled 2026-11-22, "fail everywhere".** A filing naming only a recorded parent or ultimate parent never binds a subsidiary's record by machine; it fails `parent_name_lead`, a lead to be read. 84 batch rows fail this way (68 with no other defect). All 10 rows that bound through a site-name part holding the parent's name in this round's earlier build now fail `parent_name_lead`: EVD-440581, EVD-440582, EVD-439543, EVD-439544, EVD-456592, EVD-456593, EVD-451209, EVD-451210, EVD-451881, EVD-451882.
5. **A predecessor or other name found only in the record's notes:** 842 `name_not_held` rows match, and 736 of them have no other defect. The list is [notes_name_rows.csv](notes_name_rows.csv) (evidence_id, path:line at 17834918, record_id; no notes text). Codex's read found EVD-437869 an apparent match of this kind.
6. **Dotted initials** ("A.B.C." against "ABC"): 130 rows would pass. This is a `name_key` limit.
7. **One comma part of a name field** (`comma_part`): 120 rows would pass if a held name as one comma part counted, as in OSHA's "ESTABLISHMENT, COMPANY". The same reading would pass "Other Operator, Acme Polymer", which is why it does not.
8. **A mailing city. Controller ruling 2026-11-22, within the owner's standard: an equal ZIP5 is the same locality.** It relaxes the controller's own earlier ruling that a city conflict is a FAIL. Codex reads 40 of the 140 rows it newly passes; one different place among them and the ZIP5 leg comes out. 324 batch rows quoted a city other than the record's after spelling normalisation, many of them a postal city for the physical one. 278 have an equal ZIP5 and no longer fail on the city (EVD-441995 now passes). 46 keep `city_differs` because the ZIP5 values differ or one is unreadable; the 12 with no other defect are EVD-440045, EVD-440046, EVD-444159, EVD-444160, EVD-445283, EVD-445284, EVD-448175, EVD-448176, EVD-451433, EVD-451434, EVD-451625 and EVD-451626.
9. **Street-key limits** (reported, not widened), counted over the 4,064 rows whose reason includes `street_differs`:

   | Class | Rows | Example IDs |
   | --- | ---: | --- |
   | `same_number_token_subset` (one side adds words such as "US", "LA" or a suffix) | 1,528 | EVD-425437, EVD-425485 |
   | `same_number_other` (another street name or suffix) | 1,270 | EVD-425511, EVD-430113 |
   | `different_number` | 924 | EVD-425445 |
   | `same_street_other_number` (a campus address?) | 236 | EVD-425487, EVD-430077 |
   | `number_word` ("First Street" against "1st Street") | 92 | EVD-425473 |
   | `number_in_recorded_range` ("1201-1205 Main" against "1203 Main") | 14 | EVD-430273, EVD-439483 |

   Codex's read adds two classes the strict reading fails: a filing that lists several suites, one of them the record's (EVD-443124 / SITE-019015), and a record street split into words ("Ind US Trial", EVD-437185 and EVD-432164).
10. **Not open: headquarters from identity-only sources.** SCHEMA §4.8 S-5 already rules on this. These 627 rows (343 state-entity, 284 FMCSA) fail under an existing owner ruling. The count is kept for the record.
11. **USAspending and SBIR as headquarters sources** (332 rows pass). A UEI can be registered for a single plant, and an SBIR address dates from the award year. Whether USAspending counts as SAM under R-SAM (2026-11-16, lifted for the public SAM extract on 2026-11-22) is your ruling.
12. **Shifted columns** (NC DEQ, 98 rows): 90 would pass if the facility label were read as the operator.
13. **Web quotes.** No web row passes; these are measured on `main` today.
    - 60 `not_own_site` rows sit on a host that carries a held name (a sister or regional domain).
    - 14 `street_absent_from_quote` rows show the street once spacing is ignored ("Bragg Ridge" against "Braggridge").
    - `registry` and `government_filing` web rows have no test of their own (111 rows on `main`, `web_class_untested`).
14. **Codex's 30-row read of the round-one FAIL rows** (follow-up 1). Codex drew 30 FAIL rows, one per reason stratum plus 15 allocated by stratum size, with `Random(20261122)`. It read them against the historical records:
    - 18 were justified rejections;
    - 9 were apparent same-record matches;
    - 3 were indeterminate.

    Weighted back to the stratum sizes, the shares are 41.7%, 41.1% and 17.2%. Codex notes that this is a sample, not a population rate, and that several strata have one observation. Its apparent matches fall under questions 5, 6, 9 and the range class in 9. The question for you: does a FAIL rate with roughly two-fifths apparent matches change which readings you rule on first?
15. **Codex round-one follow-up 3** is fixed: the two fixture templates whose boilerplate occurred in withdrawn quotes are replaced. Follow-up 2 (proof-file width) moved with the proof code to the follow-up branch.

## Replay: the last 40 commits under these rules

The replay runs `replay.py` over the last 40 first-parent commits on `main` up to 8f30ce0f, judging each one against its parent. 24 of the 40 added or changed evidence rows. "Held" counts every READ_REQUIRED or UNINSPECTABLE row, each of which fails the gate. "With an archive link" counts held rows that had a `data/archive_links.csv` capture at that commit: the rows the follow-up's per-row proof could cite. Provenance is presence only, as in the gate.

| Commit | Subject | Rows | PASS | FAIL | READ_REQUIRED | UNINSPECTABLE | Held | … with an archive link | Binding gate | Provenance |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 178349185 | Merge pull request #458 from polymerindustrycluster/agent/sp | 23,564 | 13,905 | 9,525 | 0 | 134 | 134 | 0 | fail | fail |
| 6a76e923f | Merge pull request #457 from polymerindustrycluster/agent/sp | 10,530 | 6,800 | 3,376 | 344 | 10 | 354 | 344 | fail | fail |
| 4924083cd | R2 re-capture recovery mint: 39 evidence rows + 39 archive l | 39 | 0 | 8 | 31 | 0 | 31 | 31 | fail | fail |
| 4ea038848 | Phase C unit 3: 22 accuracy corrections (EVD-425415..425436  | 22 | 0 | 0 | 0 | 22 | 22 | 22 | fail | fail |
| b99fd9e1e | Burn-down batch 4: R1 re-witness mint — 240 evidence rows +  | 240 | 0 | 24 | 216 | 0 | 216 | 216 | fail | fail |
| a514c67d8 | Burn-down batch 3 build F: wave-3 requeue mint — 124 evidenc | 124 | 0 | 7 | 117 | 0 | 117 | 117 | fail | fail |
| 9b2276f2e | Burn-down batch 3 build E2: quote-defect mint — 233 evidence | 233 | 0 | 13 | 220 | 0 | 220 | 220 | fail | fail |
| c67ad8314 | Burn-down batch 3 build E1: drift-recovered2 mint — 27 evide | 27 | 0 | 1 | 26 | 0 | 26 | 26 | fail | fail |
| f06631bc6 | Batch-2 drift-recovered mint: 178 evidence rows for 104 reco | 178 | 0 | 22 | 156 | 0 | 156 | 156 | fail | fail |
| c29df58e8 | No-URL cleared set: 16 two-family-reviewed evidence rows for | 16 | 0 | 2 | 14 | 0 | 14 | 14 | fail | fail |
| 120ec9204 | Drift re-witness mint: 53 evidence rows for 28 records recov | 53 | 0 | 4 | 49 | 0 | 49 | 49 | fail | fail |
| c2b1d1803 | Evidence burn-down batch 2: wave-3 backfill (1,276 rows, 699 | 1,276 | 0 | 106 | 1,170 | 0 | 1,170 | 1,170 | fail | fail |
| 5219c5d79 | Evidence burn-down batch 1: wave-2 backfill (482 rows, 255 r | 482 | 0 | 16 | 466 | 0 | 466 | 466 | fail | fail |
| 117e38707 | Phase C unit 2: 22 PIC-18 street fills from the judgment-que | 22 | 0 | 0 | 0 | 22 | 22 | 21 | fail | fail |
| dd38735d8 | Phase C unit 1: 32 department-row programs created from the  | 32 | 0 | 0 | 0 | 32 | 32 | 32 | fail | fail |
| 01ef298ec | Merge pull request #436 from polymerindustrycluster/agent/cl | 152 | 0 | 0 | 0 | 152 | 152 | 0 | fail | fail |
| 3f448ea18 | Merge pull request #435 from polymerindustrycluster/agent/cl | 204 | 0 | 0 | 0 | 204 | 204 | 0 | fail | fail |
| 248e94099 | Merge pull request #434 from polymerindustrycluster/agent/cl | 251 | 0 | 0 | 0 | 251 | 251 | 0 | fail | fail |
| 18cb709c5 | Merge pull request #432 from polymerindustrycluster/agent/cl | 80 | 0 | 0 | 0 | 80 | 80 | 0 | fail | fail |
| 5fa5ba937 | Merge pull request #427 from polymerindustrycluster/agent/cl | 23 | 0 | 0 | 23 | 0 | 23 | 23 | fail | fail |
| edd9591c9 | Merge pull request #424 from polymerindustrycluster/agent/cl | 2 | 0 | 0 | 0 | 2 | 2 | 0 | fail | fail |
| 6c29fa6c4 | IPEDS CIP fills: 26 degree programs (EVD-400340..EVD-400365) | 26 | 0 | 0 | 0 | 26 | 26 | 0 | fail | fail |
| 209be678e | Evidence backfill wave 1: 734 tier-A people existence witnes | 734 | 0 | 0 | 0 | 734 | 734 | 0 | fail | fail |
| d48ce7e6a | Hygiene sweep (audit F11): Farathane duplicate merged, APT s | 5 | 0 | 0 | 0 | 5 | 5 | 0 | fail | fail |
| **24 commits** | | **38,315** | **20,705** | **13,104** | **2,832** | **1,674** | **4,506** | **2,907** | 0 pass | 0 pass |

- **Binding gate.** None of the 24 commits would have passed. 4,506 rows were held, and 2,907 of them had an archive capture.
- **Provenance.** No commit's labels meet the folder rules, so all 24 fail. This is the baseline the rule starts from, not a defect in the rule.
- **Migration commit.** SCHEMA v1.19 (4ee02127) added the empty `address_role` column to every evidence shard. Because an absent column counts as empty, it edits no row, and it does not appear in the table.

## Codex findings and the tests that hold them

Tests are in `scripts/test_check_evidence_binding.py` unless noted. Each class was also loosened in a copy of the gate, and the mutation check in `check.py` confirms that the tests fail.

**Round two** (`S/reviews/467-r2-review-codex.md`, six blocking; owner split 2026-11-22):

| Codex r2 finding | Where | Fix | Tests | Mutants caught |
| --- | --- | --- | --- | --- |
| 1. A reading for one organization admits another's row | follow-up branch | Moved: bind the reading to evidence_id, record_id and a quote hash | — | — |
| 2. "Ste. 300" vs Suite 100, Building A vs B, Dayton vs Dover, Dover TX with no ZIP all passed | this PR | Designator-only comma parts stay with the street; `matching.designators_conflict()` (suite/unit and building); city and state read with or without a ZIP; a city conflict is FAIL `city_differs` | `Verdicts.test_designators_and_place_conflicts`, `test_other_state_fails`, `test_shared_building_other_suite`; `test_matching.SameStreet.test_designators` | no_unit_test, no_building_test (in matching.py), designator_part_dropped, no_state_test, state_needs_zip, no_city_test |
| 3. "Plant 2" passed as the operator of "Acme Polymer - Plant 2" | this PR | A site-name part made only of generic labels (owner's fixed list in `matching.GENERIC_LABELS`, or the site's city or county) is not a held name | `Verdicts.test_bare_site_label_is_not_the_operator` ("Plant 2", the city, the county, "North Works", a state); `test_matching.GenericLabels` (one test per word class) | bare_site_labels, no_label_words (in matching.py) |
| 4. "Acme Polymer Holdings", the recorded ultimate parent, passed through the corporate-form rule | this PR | A filing naming only a recorded parent (or parent + corporate-form words) fails `parent_name_lead` on every path, including through the site name | `Verdicts.test_parent_name_is_a_lead_on_every_path`, `test_corporate_form_extension`, `test_parent_name_is_strict_fail` | parent_binds, parent_form_binds |
| 5. A folder's `check.py` ran unconfined | follow-up branch | Removed here: provenance is presence only, nothing is executed | `GateMechanics.test_provenance_rules` (presence only) | provenance_borrowed_folder |
| 6. The trusted path does not verify archive bytes | follow-up branch | Moved: the trusted workflow runs archive verification and fails closed, never a neutral skip | — | — |
| Follow-up: gzip captures | follow-up branch | Moved: decode gzip on Wayback `id_` responses | — | — |

READ_REQUIRED and UNINSPECTABLE rows now fail the PR, with a message naming the follow-up (`GateMechanics.test_held_rows_fail_the_gate`; `KnownAnswer.test_batch6_is_blocked`).

The follow-up branch `agent/claude-code/evidence-binding-web-proofs-2026-11-22` carries the proof code as it stood at c6b6f83b and a to-do list: reading bound to evidence_id, record_id and a quote hash; a batch script never runs in the trusted job unless confined; the trusted workflow verifies archive bytes and fails closed; gzip decoding; "main text" excluding navigation and footers; duplicate `archive_links` IDs and invalid UTF-8 in proof files.

**Round one** (`S/reviews/467-r1-review-codex.md`), as it stands in this PR:

| Codex r1 finding | Fix | Tests | Mutants caught |
| --- | --- | --- | --- |
| 1. Unverified archive proof | Moved to the follow-up with the proof code; here no row is admitted by proof | — | — |
| 2. In-place edit of `source_class` reported zero rows | Any column edit re-gates the row (ruling D) | `GateMechanics.test_any_column_edit_regates` (source_class, created_by, notes; empty-column migration) | edit_some_columns |
| 3. EVD-431716 / SITE-002988 passed; building A suite 100 vs 300; spelled-out PO box; OH vs TX | The gate's structured PASS is `matching.same_street()`; a quoted other state fails | `Verdicts.test_building_number_is_not_a_street`, `test_shared_building_other_suite`, `test_spelled_out_po_box_both_sides`, `test_other_state_fails`; `KnownAnswer.test_building_number_row_does_not_pass` (the real row); `test_matching.py` | number_only_streets, no_unit_test, no_state_test |
| 4. Sibling sites 321 Oak Street Suite 100 / Oak Avenue Suite 300; area code 321; ZIP 43000 | Web rows never PASS. The civic number must be followed by the street word. A suite conflict fails. | `Verdicts.test_web_sibling_sites_one_quote`, `test_web_area_code_and_zip_are_not_civic_numbers`, `test_no_url_row_is_ever_pass` | web_pass, web_civic_only, web_no_unit_test |
| 5. "Acme Polymer Services"; former operator; "Other Operator, Acme Polymer"; other-molder.pages.dev | Web rows never PASS. A name field is one name. Platform hosts need host and path. | `Verdicts.test_web_other_operator_or_tenant_never_passes`, `test_osha_name_is_one_name`, `test_permittee_is_one_name`, `test_web_platform_host_and_path` | comma_split_names, web_platform_as_domain, web_any_domain |
| 6. Satellite plant passed as headquarters | Web rows never PASS; an organization address quote is READ_REQUIRED, which fails the PR | `Verdicts.test_web_satellite_plant_as_hq`, `test_no_url_row_is_ever_pass` | web_pass |
| 7. Provenance by filename; extra token; empty check.py | Exact label → folder rule; non-empty check.py present; a new label adds its folder | `GateMechanics.test_label_names_its_folder_exactly`, `test_provenance_rules` (extra token, prefix, other date, borrowed folder) | provenance_borrowed_folder |
| 8. The required job runs the PR's own gate | `--tree` for a trusted run. validate.yml steps labelled not authoritative. The `pull_request_target` workflow is the rules lane's (PR #466). | `GateMechanics.test_tree_reads_refuse_symlinks_and_escapes`, `test_tree_fails_closed` | — |
| F-1. Genuine matches rejected | Not widened; measured as owner questions | — | — |
| F-2. Extra proof cell ignored | Moved to the follow-up with the proof code | — | — |
| F-3. Fixture boilerplate in withdrawn quotes | Both templates replaced with synthetic labels | leak guard in `check.py` | — |

Also tested: the owner's corporate-form rule (`Verdicts.test_corporate_form_extension`, `test_matching.CorporateForm`, `KnownAnswer.test_fleet_services_row_still_fails`; mutant corporate_form_any_word).

## Follow-up for the last_activity derivation (not in this PR)

This PR changes no data. `scripts/derive_last_activity.py` is unchanged: it applies a tier-A OSHA extract row (the extract harness built tier A from name + city + state) when `same_street()` holds, and it never applies a tier-B row (SCHEMA §4.5 and v1.19 exclude tier B by design). `matching.same_locality()` is ready for it. [locality_followup.py](locality_followup.py) re-derives against the 7,196 site pairs at 393c3895 and lists every site that would change in [locality_followup.csv](locality_followup.csv) (site_id, state, county, PIC-18, old and new date and source, the tier and locality leg of the new row; no printed street or name). It asserts first that today's rule reproduces all 7,196 pairs. Three readings:

| Rule | Site pairs changed | Newly dated | Date or source changed | Of them PIC-18 |
| --- | ---: | ---: | ---: | ---: |
| Add the locality test to tier-A rows only | 0 | 0 | 0 | 0 |
| Also admit tier-B rows that pass street, locality and the gate's name test | 117 | 91 | 26 | 11 (8 newly dated) |
| Also admit every tier-B row that passes street and locality | 580 | 414 | 166 | 38 (27 newly dated) |

No tier-A row that passes the street test fails the locality test, so the locality test alone changes nothing; every change needs tier-B rows. The extract does not say what tier B means beyond "not A", and 919 tier-B rows print the site's exact city, so tier B may also be a weaker name match. Of the 608 ITA tier-B rows that pass street and locality, 509 fail the gate's name test. All 41 inspection tier-B rows that pass street and locality pass it. By locality leg, the 580 split into city 536, ZIP5 42, parenthetical city 2.

**Owner/schema question (recommendation: the middle row).** Admitting tier B needs a dated SCHEMA §4.5 revision. I recommend admitting a tier-B row only when it also passes the evidence gate's name test, so a derived date never rests on a name the gate would not bind: 117 site pairs. The third row would rest 463 more on names the gate rejects.

**The source-map lane's 122.** The controller relayed that lane's finding that 122 PIC-18 sites with an OSHA street and name match miss `last_activity_date` because of parenthetical city text. The lane's own `SOURCE_MAP.md` (§5, line 101 in the controller's storage) withdraws the city explanation: city text is equal for 114 and only the ZIP agrees for 8. It finds 29 sites absent from the #463 extracts, tier-B rows for most of the rest, and tier-A rows whose single latest street string fails although another record passes. The two counts are not the same measure: the lane matched the full OSHA files in its lake, and this measure reads only the #463 extracts. Joined by site_id (the lane's 122 ids, from running its `sql/undated_122_split.sql` read-only), 25 of the 122 get a date under the widest reading above and 8 under the recommended one; all 25 are tier-B rows. The other 97 cannot be dated from the #463 extracts under any of these rules. Of the 27 PIC-18 sites the widest reading newly dates, 25 are in the lane's 122. Only 13 sites on the tree carry a parenthetical city, and the parenthetical leg dates 2. The larger gain is an extract rebuilt from the full OSHA files, the lane's item 5, not the city test.

## What this gate cannot see

- **Truth.** The gate checks that a quote is about the record. It does not check that the quote is faithful to its source or that the source is current. An extract older than an operator change can still pass.
- **Web rows.** No web row can be admitted by this gate. Per-row proof is the follow-up.
- **A mailing city with another ZIP.** A filing printed with a postal city and a ZIP other than the site's fails `city_differs` (owner question 8). An equal ZIP is trusted: one ZIP covers several places, so a neighbouring town printed with the site's ZIP passes when the street and name also pass. County is not checked.
- **A state name read as the city.** Some quotes print the state name in the city's place ("…, NEVADA, NV 89081"), and `quoted_place` then reads "Nevada" as the city. Those rows failed `city_differs` before; an equal ZIP now hides the misread. The parser is not fixed this round.
- **Places that differ only by their kind.** Dropping a trailing Township/City/Village/Borough makes "Union City", "Union Township" and "Union" compare equal, although they can be different places.
- **Identity behind an equal name.** An unrelated namesake at the same street would pass. Organization existence rows from structured sources are judged on the name alone.
- **The claim's own value.** The gate compares the quote with the record's current fields, not with the value `claim_detail` asserts.
- **Tier ceilings.** The §4.13 `tier_effect` ceilings and `address_role` are not checked.
- **Provenance scripts.** The gate checks that a folder's `check.py` is present and not empty. It executes nothing, so it cannot tell whether that script reproduces the rows: the lane runs it, and the reviewing family runs it again.
- **Its own trust.** Inside the `validate` job the gate is the PR's own copy. Only `main`'s copy run with `--tree` is authoritative.
- **Quote text in this PR.** The leak guard compares every street-, ID- or name-like segment of the test strings (at least 10 characters, field boilerplate excluded) with every `claim_detail` at 17834918, including the withdrawn rows. It does not scan for shorter phrases, registry boilerplate or this README. Rows are cited by ID and path:line only.

## Checks

| Check | Command | Result |
| --- | --- | --- |
| Gate unit tests | `cd scripts && python3 -m unittest test_check_evidence_binding` | 75 tests OK. They use synthetic strings shaped like real rows. They include the Codex counterexamples and a known-answer replay of batch 6: `--new-since` and `--provenance-since` both exit 1, and the real EVD-431716 row is not PASS. |
| Street, label, locality and corporate-form tests | `cd scripts && python3 -m unittest test_matching test_derive_last_activity` | 17 tests OK |
| Last-activity derivation | `python3 tasks/last-activity-street-leg-2026-11-22/check.py` | PASS; all 7,196 site pairs unchanged by the building rule (2,632 populated) |
| This folder's check | `python3 tasks/evidence-binding-gate-2026-11-22/check.py` | 181 numbers OK, 58 of them from the derivation follow-up |
| Leak guard (inside `check.py`) | — | 0 of 233 segments occur in any `claim_detail` at 17834918. A planted real fragment is caught. |
| Mutation check (inside `check.py`) | — | 27 loosenings, each caught by at least one failing test. Failing tests per loosening: token subset names 9, comma split names 2, corporate form any word 6, number only streets 2, no unit test 3, no building test 1, designator part dropped 1, state as floor 1, no state test 3, no city test 2, state needs zip 1, no paren city 1, zip ignored 1, empty zips match 1, bare site labels 1, no label words 1, parent binds 3, parent form binds 1, hq from any source 2, web pass 7, web any domain 3, web platform as domain 2, web civic only 3, web no unit test 1, web name unchecked 1, edit some columns 1, provenance borrowed folder 1 |
| Replay | `python3 tasks/evidence-binding-gate-2026-11-22/replay.py` | Writes `replay.csv`, the table above |

The remaining repository checks are recorded in the PR.
