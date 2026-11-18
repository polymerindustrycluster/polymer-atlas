# Blind audit 11: the data PRs merged 2026-11-16 and 2026-11-17

The owner approved this audit on 2026-11-17. It asks whether the data PRs merged on 2026-11-16 and 2026-11-17 hold up.
Unlike the PRs blind audit 10 sampled, every one of these passed a two-family refute gate before merge.

**Result (phase 3):** 118 of 120 sampled record changes agree; 1 field error, 1 creation error, 0 unresolved. Design-weighted,
the confirmed-error rate is 1.8% overall [0.5%, 6.4%] and 2.9% on the content strata [0.5%, 14.3%], the figure comparable
with blind audit 10's 4.6%. A10's rate lies inside that interval, so the audit cannot rank the two. The report is
[`docs/reviews/BLIND_AUDIT_11_2026-11-17.md`](../../docs/reviews/BLIND_AUDIT_11_2026-11-17.md); the two corrections are listed there and not applied.

The machinery is blind audit 10's (`tasks/blind-audit-10-2026-11-14/`), copied and adapted rather than rebuilt.

**Phases:**
1. Frame, sample and blind inputs (commit `70ee86f`).
2. Two blind reviewers, dispatched by the controller outside this branch: A = Claude Opus, B = Codex on GPT-6.2 Astra.
3. The lead's adjudication, statistics and report. The PR changes 0 data rows.

## Frame

**Window:**
- Base: `be2e608`, the first parent of `6b07f18` (the #336 merge).
- Head: `4182519`, the #365 merge, which was main at the brief.
- The window holds 21 first-parent commits. The two merge trains are expanded into their own PR merges, so every change is
  attributed to the PR that made it:
  - #359: #353, #350, #349, #348, #356, #352, #351, #354.
  - #363: #343, #347.
- `frame.py` asserts two things about each train: it branches from its main parent, and its merge adds nothing to `data/`
  beyond the train tip.

**Unit: record change.** A record change is one row at HEAD, keyed by its table ID, under one change class. It is graded
only on that class's columns.
- `registry_links` is keyed by org_id+registry+registry_id+site_id; `archive_links` by evidence_id+archive_ref.
- One site can carry a ZIP fill, a band and a capability tag from three PRs. Those are three record changes in three
  strata, so a per-record unit could not be stratified by change class.
- `last_verified`, `sources` and `notes` ride with the class change made in the same step, and are never a class alone.
- The column-to-class map is exhaustive. The build fails on any changed column with no class, on a ride-along-only change,
  and on any changed data file outside the frame tables and evidence shards.

**Excluded:**
- `latitude`, `longitude` and `geocode_precision`. They are reference data and never evidence (AGENTS §1). This removes all
  1,208 #336 rows; 150 of those sites are in the frame for other classes.
- `tier1_qualifier*` columns, which are derived.
- Generated `parent_of`, `successor_of` and `merged_into` edges, which AGENTS §4 says are generated from organization
  columns. #352 generated one. An authored `member_of` edge would fail the build.
- `evidence_*.csv` appends, which are not a frame table.
- Packet, tooling, site and queue PRs (#335, #338, #345, #356, #357, #358, #366). The build asserts they change no frame row.

**Frame: 3,959 record changes.** Column meanings: N is the stratum's frame size, n the sample drawn, p the inclusion
probability, and w the design weight N/n.

| Stratum (change class) | PRs | Tables | N | n | p | w |
|---|---|---|---|---|---|---|
| `ownership_founding` | #343, #347 | organizations 109 | 109 | 3 | 0.0275 | 36.3 |
| `markets` | #344, #349, #360 | organizations 124 | 124 | 3 | 0.0242 | 41.3 |
| `capabilities` | #337, #351, #361, #365 | organizations 1, sites 28, site_capabilities 47 | 76 | 3 | 0.0395 | 25.3 |
| `streets` | #353 | sites 23 | 23 | 3 | 0.1304 | 7.7 |
| `parents` | #352 | organizations 11 | 11 | 3 | 0.2727 | 3.7 |
| `registry_federal_links` | #341 | registry_links 105 (FRS 73, TRI 32) | 105 | 3 | 0.0286 | 35.0 |
| `uei_links` | #355 | registry_links 472 | 472 | 13 | 0.0275 | 36.3 |
| `bands` | #341, #348 | organizations 117, sites 143 | 260 | 7 | 0.0269 | 37.1 |
| `members` | #340 | organizations 1, members 61 | 62 | 3 | 0.0484 | 20.7 |
| `zips` | #342 | sites 348 | 348 | 9 | 0.0259 | 38.7 |
| `tier_changes` | #354 | sites 3 | 3 | 3 (census) | 1 | 1 |
| `archive_links` | #364 | archive_links 2188 | 2188 | 60 | 0.0274 | 36.5 |
| `rulings` | #339, #346 | ecosystem 1, programs 1 | 2 | 2 (census) | 1 | 1 |
| `navigation_links` | #350 | organizations 176 | 176 | 5 | 0.0284 | 35.2 |

**Classification calls, flagged for the controller:**
- **`navigation_links` (#350: LinkedIn, newsroom and feed URLs) is a stratum the brief did not name.** It is own-site
  evidence, unlike registry or archive links, so it stands alone.
- **`rulings` includes #339.** #339 cleared AFFOA's ecosystem `polymer_program`. A10's rollup-only rule would have dropped
  it as derived, but the brief names the AFFOA rulings as a stratum. `check.py` asserts both that A10's rule would drop it
  and that this frame keeps it.
  - The blind files label this stratum `program_status`, because the frame's name would tell a reviewer the value had
    already been decided.
  - Both rows are AFFOA records, which both A10 reviewers already graded as A10-003, so they are not blind to those
    reviewers.
- **59 `members` rows changed only `snapshot_date`.** That change re-asserts the public listing, so it is kept as a
  claim. One more row changed its display name as well, and one row was created.
- **`certifications` (one #349 cell) is in `markets`**, and #337's three material fills are in `capabilities`.
- **`bands` pools two source types:** PPP-reported bands (#348) and federal-filing bands (#341).

**Reconciliation (AGENTS §2 rule 10c).** `check.py` asserts each PR's published count against git, for 25
(PR, table, class) pairs, plus cell counts for #343 (58), #347 (63) and #350 (234), #337's three records, #336's 1,208
coordinate-only rows and #352's one generated edge.

Four published figures needed reading past the title. In each case git agrees with the later statement:
- **#348:** the body says 137 site bands. The task README's "Replay after PR #341" preserved six bands #341 had already
  filled, leaving a final 131.
- **#365:** the title says 45 capability rows. The body retired 10 capability IDs, leaving 35.
- **#360:** the title says 79 organizations. The body says 77 after withdrawals.
- **#349:** "41 markets" counts values; the change filled 16 cells on 16 organizations.

## Sample

**The draw:**
- n = 120, seed `BLIND-AUDIT-11-2026-11-17-v1`, A10's allocation rule.
- Strata under 5 record changes are taken whole. Every other stratum gets at least 3, and the rest is split in proportion
  by largest remainder.
- `random.Random` is seeded by SHA-256 of seed|class and samples from (table, record_id) sorted ascending. Blind row order is
  a separate seeded shuffle.
- 79 of the sampled record changes are creations and 41 are changes.

**Why 120.** Under this allocation the Kish effective sample size is 110.0. At A10's rate of 4.6%, that gives a Wilson
95% half-width of about ±4.1 points (n = 100 would give ±4.7). At 2% it gives ±3.0.

On time: A10's reviewer A finished 50 rows in about 32 minutes by its file timestamps. Half of this sample is archive
links, and a check of one archive link, ZIP, FRS link or member row took a few seconds. A band row took one streamed SBA
file read, 11 seconds. So about 80 to 120 minutes per reviewer is expected, with UEI rows the exception below.

**Per-stratum intervals will be wide.** Eleven of the 14 strata draw 3 to 9 records. Census strata need no interval.

## Blind inputs

`blind_a.csv` and `blind_b.csv` are byte-identical: 120 rows, sha256 `a8c01159…c950`. Fields are a whitelist built from
git at the pinned HEAD:

`blind_id, change_class, table, record_id, record_label, change_kind, columns_under_audit, values_json, context_json,
cited_sources, evidence_json`

**Field contents:**
- `context_json` holds the record's locator fields that are not under audit, with foreign keys resolved to
  name/website/HQ (organizations) or name and address (sites).
- For an archive link, `context_json` holds the URL the capture should be of and the record that evidence supports.
- `cited_sources` holds the record's `sources`, or a capability row's `source_ref`, with source-read dates removed. In 30
  rows the text named a working path or pass, so only its public URLs are kept.

**Withheld, as in A10:** the PR, lane, `created_by`, `notes`, `last_verified`, `as_of`, `observed_date`, evidence IDs and
evidence prose, `tier_effect`, and `source_class`.

**Leak scan.** The pattern is A10's, with three changes:
- `lane` now matches only the lowercase word or "Lane <ID>". The old token hit the place name "Green Lane, PA" in a real
  organization's HQ.
- `ruling`/`rulings` is added.
- An `archive_links` `record_id` may carry `EVD-` only when the cell is exactly an evidence-id|Wayback key. `EVD-`
  anywhere else still trips the scan; `check.py` plants it to prove that.

**Blindness is by protocol, not access control.** `frame.csv` and `sample.csv` carry PR attribution, so reviewers get only
their blind file and `REVIEWER_INSTRUCTIONS.md`, copied outside the repo. `freeze.json` pins the frame, the sample, the
draw, both blind files, the instructions, `frame.py` and `sample.py`.

**Reviewer instructions.** `REVIEWER_INSTRUCTIONS.md` is A10's reviewer brief adapted for record changes. It keeps A10's
verdict grammar (AGREE / FIELD_ERROR / CREATION_ERROR / UNRESOLVED) and lock procedure, and adds:
- neutral per-class pointers to public sources;
- the claim each row makes, taken from SCHEMA (§4.22 for archive links, including that a capture must replay the cited
  page; §4.8 for registry links);
- a pin on commit `4182519` for any `data/` read, so that A10's stale-checkout problem cannot recur.

**Reachability.** Checked one row per class from the blind row alone:
- Archive, ZIP (Census geocoder), FRS (ECHO), member list and company pages answered at once.
- PPP bands are in public SBA files of about 0.4 GB each. A streamed grep takes seconds.
- **UEI rows (13 of 120) failed every unauthenticated route I tried, on one sampled UEI:**
  - the SAM.gov entity API (HTTP 400, needs a key);
  - SAM.gov's public search API, which returned only exclusion records, by UEI and by name;
  - USAspending recipient autocomplete (0 hits; it holds award recipients only);
  - HigherGov (404). #355's source is the SAM PUBLIC monthly extract,
  `SAM_PUBLIC_MONTHLY_V2_20261101.ZIP`, whose sha256 is in `tasks/sam-uei-links-2026-11-16/README.md`. Unless reviewers
  get a SAM API key or that file, expect UEI rows to come back UNRESOLVED.
  - *Phase 3:* the controller had the lead make one batched API request after the daily quota reset; both reviewers were
    told to use the stored response. Reviewer B had locked before it existed.

## Check

`python3 tasks/blind-audit-11-2026-11-17/check.py` verifies:
- the frame reproduces from git, and every published count reconciles;
- one known answer per stratum (15 records, both rulings included). I checked each record's BASE and HEAD values by hand
  from `git show`; `check.py` then recomputes them and also checks the value just before and after the merge step that
  made it, and the PR attribution;
- planted defects are refused: a coordinate-only diff, an unmapped column, a ride-along-only change, an organization
  `status` change, and an authored `member_of` edge;
- the leak scan catches nine planted leaks and passes the "Green Lane" place name;
- the sample re-draws from the seed;
- the blind files are identical, keyed to the sample, leak-free and unchanged since the freeze.

It was also run against injected failures: a wrong published count, a wrong known value, a wrong merge step, and a
one-byte edit to `blind_b.csv`. All four were caught.

## Phase 3: adjudication, statistics, report

**Reviewer outputs.** `copy_verdicts.py` copied both locked files after checking them against their BOARD lock hashes
(`locks.json`). The committed `verdicts_a.csv` and `verdicts_b.csv` are LF copies with every free-text cell (field,
correct_value, source_url, quote, note) blanked on the 13 UEI rows, because reviewer A quoted SAM names and addresses
there (R-SAM). `receipts_a.json` and `receipts_b.json` are byte copies.

**Adjudication** (`adjudicate_build.py` → `adjudication.json`). The 22 rows the reviewers did not both grade AGREE, plus
the 7 band rows both graded AGREE, which the controller asked the lead to check against the owner's PPP ruling:
- Web receipts are fresh raw fetches (`adjudicate_fetch.py`, index in `adjudication_receipts.jsonl`, bodies in the
  controller's persist dir). Each quote is re-checked as an ordered word sequence; `raw_re` and `raw_not_re` patterns
  are checked on the raw bytes.
- The SBA PPP and OSHA ITA files were read whole and hashed (`stream_extract.py`); only the matching rows were kept. Both
  PPP files match #348's manifest hashes.
- Each band row's five "Strict matches" conditions are recomputed from git (the value at #348's step parent, the HEAD
  evidence row, the organization's held sites and PIC-18 county) and from the PPP row.
- UEI rows are decided against one batched SAM Entity API v3 response (`sam_batch.py`; key sent only as a header, response
  stored privately with its sha256). The match test: an active registration with the same AGENTS §3 normalized name and the
  same HQ city and state. Per-row facts go to a private note whose sha256 is pinned in `adjudication.json`; the repo carries
  only each row's grade.

**Statistics** (`stats.py` → `final_grades.csv`, `statistics.json`): per-stratum Wilson intervals, the overall
design-weighted rate and the content rate (without archive links, ZIPs and navigation links) at the Kish effective n.
**Report** (`write_report.py`): rendered deterministically; `check.py` fails if the committed text differs.

**Check, phase 3.** `check.py` also verifies the locks and the redaction rule, the cross-tab (98/18/1/3), adjudication
coverage, every receipt, the band conditions, the UEI results, final grades, statistics, the report, and an R-SAM scan of
every committed output for SAM-only names or street lines. Planted defects (an edited report, an unredacted UEI cell, a
flipped grade, a wrong JobsReported, a truncated census) were all caught. Without the private files (raw bodies, the SAM
response, the reviewer originals) the affected checks print `NOT CHECKED`; `--require-private` makes that a failure.

## Caveats

- **Not like-for-like with A10.** A10's frame was people, programs, identifiers and events. This frame is 55% archive
  links, 12% UEI links and 9% ZIPs, so its overall rate measures a different mix. The content rate (controller ruling
  2026-11-17: without archive links, ZIPs and navigation links) is the comparable figure. Per-stratum rates are imprecise
  at n = 3.
- **No claim covers records outside the frame.** `frame.csv` does not list everything the PRs touched: evidence-only
  changes and coordinates are out.
