# Decisions ledger

Append-only record of why the Atlas is the way it is (portfolio rule 5). Newest last. Each entry names its date, the
decision, who made it, and where the detail lives. Scope, ring and vocabulary rulings stay in the owner-battery files
and dated SCHEMA revisions; this ledger records release and operating decisions and points to those rulings.

## 2026-11-14: first public release, first user, and non-use review

- **Decision:** cut the first dated release of the Atlas (`v2026.11.14`) from main at the main commit that merges this ledger (data identical to `accc03b`), built with
  `scripts/export_release.py` (see the release notes on GitHub).
- **First user (portfolio rule 8):** John Swanson, using the Atlas for PIC work.
- **Non-use review date:** 2026-12-14 (30 days after the release). On that date, check whether the release has been
  used for PIC work, and record the result here; non-use is a finding, and "parked" is a legitimate outcome.
- **Decided by:** the repo owner, in session, 2026-11-14.
- **Quality basis:** blind audit 10 (`docs/reviews/BLIND_AUDIT_10_2026-11-14.md`): 45 of 50 sampled changed records
  agreed, 2 field errors (both corrected in #332), 0 creation errors, 3 unresolved; design-weighted confirmed-error
  rate 4.6% (Wilson 95% about 1.3% to 15.5%).

## 2026-11-14: `validate` is a required check on main

- **Decision:** a repository ruleset ("main: require validate") requires the `validate` workflow to pass before any
  merge into main; repository admins may bypass in an emergency.
- **Why:** after #271 (SCHEMA v1.13) left `docs/schema/vocab.json` stale, 37 consecutive pushes merged on a red check,
  and the unit-test, SQLite-build and artifact steps never ran (fixed in #329).
- **Decided by:** the repo owner, in session, 2026-11-14.

## 2026-11-16: Gemini is the second review family; Claude Opus stands in on Codex-written PRs

- **Decision:** every data change is still refuted by two AI families before merge: Codex always, plus Gemini.
  When Gemini is unavailable, a Claude Opus reviewer may stand in for pull requests written by Codex (never for
  work Claude wrote). Packet-only and docs-only pull requests keep needing one family plus CI.
- **Why:** Grok's usage balance ran out on 2026-11-14, and review capacity is the limit on how fast work lands.
- **Decided by:** the repo owner, in session, 2026-11-16 (`tasks/owner-rulings-2026-11-16/README.md`).

## 2026-11-16: the public site becomes a working tool (PIC-18 prospects, CSV, evidence on organization pages)

- **Decision:** the site gains a PIC-18 prospects page (one row per organization row with at least one site row in a
  PIC-18 county, operating status active, tier A-C), a "Download these rows (CSV)" button on table pages, a
  `prospects.csv` built with the site, a latest-release link on every page, an "active, tier A-C" column on the county
  index that sums to the PIC-18 headline, county tables by process and employee band, and the evidence rows on
  organization pages in place of source strings. Graph, map + network and street map open on PIC-18.
- **Why:** the site audit of 2026-11-16 (first user: John Swanson, non-use review 2026-12-14) answered 2 of 12 real
  tasks, mostly because nothing could be filtered or taken away. Detail and the 12-task tally are in the PR.
- **Rules fixed here:** (1) an unknown value (blank or the literal "unknown") is shown as unknown and counted per
  filter, never read as zero or small; (2) employee band is the PIC-18 site band, else the organization's Ohio band,
  and each row says which; process, material and market follow the same rule; (3) public membership is shown only as
  "on the public member list" or "not on the public member list" (AGENTS.md section 5.1), and the page says the second is
  not "not a member"; (4) organization pages show evidence only as structured fields (claim type, source class, strength,
  observed date) and the source links found in the citation; the claim text, notes, lane ids and the prose of source
  strings are never published, because free text cannot be made safe by a pattern filter (a Codex review found claim text
  naming individuals, e.g. EVD-128276); (5) every page number is
  recomputed from `data/` in `scripts/test_build_site.py`.
- **Not decided here:** whether to publish a non-member list or keep a private membership overlay (audit finding 3) stays an
  owner ruling.
- **Decided by:** built to the controller's task from the audit; no owner ruling is claimed or needed for the wording
  above, which restates AGENTS.md section 5.1.

## 2026-11-17: QUEUE.md stays the single tracker; private branch history stays off main

- **Decision:** `tasks/QUEUE.md` remains the Atlas's only tracker (resynced in #368). When a pull request branch's
  history has carried private or SAM-derived text, it lands by squash merge or a fresh replacement pull request, so
  those commits never reach main (#362 replaced by #367; #372 squash-merged).
- **Limit:** GitHub keeps each pull request's own refs (`refs/pull/N`), which only GitHub support can purge.
- **Decided by:** the repo owner, in session, 2026-11-17 (tracker; strip names from #362); the squash practice is the
  controller's, recorded here.

## 2026-11-18: owner battery of 2026-11-17 ruled "all as recommended"

- **Decision:** the eight held items plus item 1b (identifier URLs in people rows) are ruled as recommended. Detail is
  in `tasks/owner-rulings-2026-11-18/README.md`. The PPP "Strict matches" ruling of 2026-11-16 is recorded as SCHEMA
  v1.13.3 (§1 R13).
- **Decided by:** the repo owner, in session, 2026-11-18, as multiple choice.

## 2026-11-19: an old commit with person names stays in main's history

- **Decision:** main's history is not rewritten to remove commit 3b30b2f. PR #252 landed as a merge commit, so its
  first commit, which stored about ten speakers' names in a drop list before a later commit replaced them with
  hashes, is reachable from main. The names were on public speaker pages, and no current file holds them.
- **Why:** a rewrite of main breaks every clone and open branch while several sessions merge daily, for names that
  were already public. Since 2026-11-17 such branches land by squash (entry above), which keeps the case from recurring.
- **Decided by:** the repo owner, in session, 2026-11-18, as multiple choice ("Leave it"). Detail:
  `tasks/owner-rulings-2026-11-18c/README.md` item 3.

## 2026-11-20: owner rulings 2026-11-19e on the Muse follow-ups

- **Decision:** four rulings on the questions Muse's answers left open (detail and evidence:
  `tasks/owner-rulings-2026-11-19e/README.md`).
  1. **Gate B for people stays strict.** Polymer research must be stated on the person's own profile or lab page, on the
     university's domain. A department, center or program page, a lab page describing members' projects, and an
     off-domain lab site do not count. Aguado, Szleifer, Healy and Correa stay held; Gabrielson stays held on currency.
  2. **Emeritus conflicts are held.** Zimmerman (Illinois) and Allcock (Penn State) stay leads until one current
     university page settles the conflict.
  3. **Sterilite's LEI stays.** ORG-001384 is the parent company, Sterilite Corporation, so the link is the record's own.
     Its HQ field (Massillon, OH) is wrong and moves in a later pass. The owner first chose "remove" when the question
     framed the record as an Ohio plant. That framing was wrong, and the ruling was reversed on the corrected facts in
     the same session.
  4. **year_founded may use a second source in place of the address gate.** Where GLEIF's address does not name the
     organization's HQ, a second source's SAME verdict plus a re-read quote from the company's own page may stand in.
     Plastipak is excluded because its only quote is third-party. Applied only where the company's own sources do not
     state a conflicting year and both review families judged the row SOUND.
- **Decided by:** the repo owner, in session, 2026-11-19/20, as multiple choice.

## 2026-11-22: owner rulings on the merge gate, contact data in evidence quotes, and the review record

- **Decision:** three rulings after a review of the 42 PRs merged since 2026-11-20 (UTC).
  1. **No account merges ahead of `validate`.** The repository-admin bypass on the ruleset "main: require validate" was
     removed on 2026-11-22. GitHub now refuses a merge until `validate` is green on the PR head; open the PR and wait, or
     use auto-merge. Evidence: 23 of the 42 PRs, all from `agent/spaghetti/*` branches, were merged before `validate`
     finished on their head. #422 and #423 then failed it (a V-64 unit test, not the data validator), and the broken
     commits sat on `main` from the #422 merge (11:45Z) to the #426 merge (15:03Z) on 2026-11-20; the `main` check itself
     read failed from 11:48Z to 15:06Z.
  2. **Contact data in evidence quotes.** A company's public switchboard phone or fax number and a role address may stay
     in a verbatim quote. An individual's email, a direct line, an extension or a mobile number may not: cut the quote
     before it. AGENTS.md section 6 carries the sentence. Rows already in `data/evidence_*.csv` are not edited (evidence
     is append-only); the rows that may hold an individual's detail are being triaged, and their remedy returns to the
     owner.
  3. **Review record.** Each PR carries one comment per verifier naming its model family and model, its verdict and what
     it checked. 39 of the 42 PRs had no review or comment on GitHub.
- **Decided by:** the repo owner, in session, 2026-11-22, as multiple choice.

## 2026-11-22: owner rulings on SAM extract evidence, the Muse pause and batch 7

- **Decision:** three rulings after the review of burn-down batches 5 to 7.
  1. **The public SAM.gov entity extract may be quoted as evidence.** This lifts, for the public extract only, the
     2026-11-16 R-SAM bar on copying a SAM name or address into the Atlas (`tasks/owner-rulings-2026-11-16/README.md`).
     The R-SAM filter stays: a record marked D&B-sourced, or last updated before 2022-04-04, is not quoted (D&B is a
     licensed source under AGENTS.md section 5). SAM API responses were not addressed and stay under R-SAM. A batch
     that quotes the extract shows that its rows pass the filter.
  2. **Muse pauses minting and integration.** Until the owner lifts this, Muse opens no data PR and mints nothing. It
     continues downloads and the archive copy, and may do read-only work: publishing its join code and match rules, and
     triaging its own flagged rows without editing them. Reason: batch 5's OSHA site matches required name, city and
     state but no street, and batches 6 and 7 were built before the address audit of 2026-11-22 identified the batch-5
     mismatches.
  3. **Batch 7 (PR #459) stays in draft** until its joins are checked the way batch 5's were.
- **Decided by:** the repo owner, in session, 2026-11-22, as multiple choice.

## 2026-11-22: owner ruling, batches 5 and 6 reverted
- **Decision:** burn-down batches 5 (PR #457) and 6 (PR #458) are taken off `main` whole: 34,094 evidence rows (33,916 labelled batch 5 or 6, and 178 QC-1 cured backfill rows labelled burn-down batch 1 or 2 that arrived in PR #457; the 39 recapture rows that arrived in PR #455 are not removed), 6,837 registry links and 364 archive links. A binding test over the 33,916 batch-5/6-labelled evidence rows (is the quoted operator a name the record holds, and is the quoted street the record's street) gave 24,241 PASS; 9,469 with an explicit FAIL verdict, on 2,590 records; and 206 with no binding verdict (free-text rows the test could not parse). Batch 5's OSHA site match required name, city and state but no street. This is an exception to the append-only rule of SCHEMA 4.13, taken so that nothing unproven stays in the canonical data while rows are re-checked.
- **Return and IDs:** a removed row that later passes the binding gate and a replay against the raw source file returns under its original evidence ID in a new, reviewed PR. That is restoration of the same row, not reuse of an ID, so it does not conflict with AGENTS.md section 3 or the "never reused" rule of SCHEMA Appendix C 6.1. A removed ID is reserved for its own row and is never given to a different row; `scripts/atlas.py next-id` counts every id in a `tasks/**/REMOVALS.csv` toward its floor, so the allocator skips the gap (`EVD-425437` to `EVD-459524`), and exits non-zero rather than guess when it cannot find the tasks folder.
- **What is kept:** `tasks/revert-batches-5-6-2026-11-22/quarantine/` holds, for every one of the 34,094 removed evidence rows, its ID, record keys, source key and first-cut binding verdict, passing and failing alike, with no row text; and the 6,837 removed registry links and 364 archive links, verbatim. The row text is recoverable from commit 17834918 by evidence ID. This supersedes the same day's narrower ruling to remove 844 rows.
- **Decided by:** the repo owner, in session, 2026-11-22, as multiple choice.

## 2026-11-22: owner ruling, the evidence binding gate is a strict floor, then merge (PR #467)
- **Decision:** Codex's third review of PR #467 (head 9205837e) refuted it with 7 blocking findings, all from constructed counterexamples; on the real reverted rows it showed no wrong plant. The owner ruled, as multiple choice relayed by the controller: **strict floor, then merge.** A structured row is PASS only when every leg matches positively and nothing in the quote is left unexplained:
  - **name:** a held name exactly, or a held name plus corporate-form words only. No parenthetical or trailing text is dropped to get there ("Acme Polymer (operated by Quill Resins)" does not pass). A name whose key equals a recorded parent's or ultimate parent's does not pass, even when the key also equals the record's own, unless its text is the record's own name and not the parent's. A site-name part made only of generic labels, including either part of a parenthetical city, is not a name;
  - **street:** `matching.same_street()`;
  - **unit:** a suite, unit, apartment, room, floor, department or building designator stated on either side is stated and equal on both; one the parser cannot read is not a match;
  - **locality:** `matching.same_locality()` is called and holds: the state on both sides and equal, and the city equal (either part of a parenthetical city) or the ZIP5 equal, the ZIP read from ZIP, ZIP+4 with a hyphen or a space, or a trailing dash. A missing state or an unread locality is not a match;
  - **two records:** a quote that would pass on two site records passes on neither.
- **Verdicts:** a row that is not PASS and shows no demonstrated conflict is **HELD** (`held_for_reading:<legs>`); a demonstrated conflict stays FAIL with its reason. Both fail the PR; the difference is which reader's queue the row joins. A self-referencing ultimate parent (the record's own name in that field) is not a parent.
- **What the gate is:** a floor, not proof. PASS means every mechanical leg matched. Admitting a data PR still needs two model families reading rows. A counterexample found after merge becomes a test and a fix as a follow-up, not a reason to hold the gate.
- **Deployment (condition, not claim; Codex r3 finding 7):** the gate decides nothing until the trusted workflow from PR #466 (`pr-rules.yml`, check run `binding-gate`; merged at a7053b2b while this PR was open) is made a required check under the ruleset's strict (branch up to date) policy. Until then the `validate.yml` binding steps are early feedback.
- **Effect on the quarantined batches 5/6 (34,094 rows):** PASS 20,705 to 20,160 (549 rows move PASS to HELD, 4 FAIL to PASS); FAIL 12,897; HELD 549; READ_REQUIRED 344; UNINSPECTABLE 144. The last-activity derivation is unchanged on all 7,196 site pairs. Codex's fourth review found two more constructed passes (a record street with a one-sided level or basement suffix; a locality holding a second state or ZIP); the controller ruled to fix exactly those two and their families (HELD `street_suffix_unexplained`, and a city holding a digit or a state is `locality_not_read`), which moved 18 more batch rows PASS to HELD and none toward PASS, and to merge on a confirmation of those two cases only. A fifth review found the ECHO "TOWNSHIP OF" path bypassing the city test; fixed the same way (the test now runs on the final city on every path), with no historical row changed. Counterexamples found after that are follow-up PRs.
- **Decided by:** the repo owner, in session, 2026-11-22, as multiple choice (relayed by the controller). It supersedes the controller's earlier approach of passing a row unless a conflict is found.

## 2026-11-22: owner ruling, name match on structured rows when the street matches (corporate-form words only)
- **Decision:** in the evidence binding gate, a structured-source site row whose street already passes the shared street test (`scripts/matching.py` `same_street()`) also binds on its name when the quoted filing or permit name equals a name the record holds, or when a held name is a leading run of it and every extra token is a corporate-form word from this fixed list: Inc, Incorporated, LLC, L.L.C., Corp, Corporation, Co, Company, Ltd, Limited, LP, LLP, Holdings, Holding, Group, US, USA, U.S., North America, Americas. Any other extra word stays FAIL `name_not_held` ("Acme Polymer Services" fails; the fleet-services affiliate on EVD-455899 fails). The rule lives in `scripts/matching.py` (`corporate_form_extension`).
- **Scope:** it does not apply to web rows, to organization rows without a street test, or to predecessor, parent or notes-only names; those questions stay open.
- **Effect:** of the 1,829 batch 5/6 rows whose only defect under the first round of the gate was a held name followed by more words, 150 now pass; 172 rows of the quarantined batches pass on this basis in all, none of them on a parent's name.
- **Decided by:** the repo owner, in session, 2026-11-22, as multiple choice.

## 2026-11-22: owner ruling, evidence binding gate split (PR #467 structured rows only)
- **Decision:** after Codex's second refutation of PR #467 hit the two-round cap, the owner split the PR. #467 is the binding gate for structured rows only. A web row is FAIL or READ_REQUIRED, and a READ_REQUIRED or UNINSPECTABLE row fails the PR; admission of web rows by per-row proof (proof files, readings, archive fetching) moves to branch `agent/claude-code/evidence-binding-web-proofs-2026-11-22`. Provenance is presence only: a `created_by` label's folder holds a non-empty `check.py`, and the gate executes nothing from the tree it gates; the lane and the reviewing family run the replay. This supersedes the controller's earlier rulings C, the execution part of E, and the proof/reading design for #467.
- **Rules added to #467:** for a structured site row the quoted state must equal the record's, read with or without a ZIP; a suite, unit or building stated on both sides must agree, in dotted and abbreviated forms, in the shared `scripts/matching.py` test (the last-activity derivation is unchanged on all 7,196 sites). The city half (a quoted other city is a FAIL) is a controller ruling within the owner's standard, not part of the owner's ruling; see the locality bullet.
- **Site-name parts ("drop generic labels only"):** a site-name part is ignored as a held name only when every token in it is a generic label: plant, facility, warehouse, works, site, office, HQ, headquarters, building, unit, main ("main" added by the owner the same day, relayed by the controller; it changes no row: no site key on the tree is generic only because of it); a number or ordinal; a compass word; a US state; or the site's own city or county. Any other part (a brand, a division, a trading name) counts as a held name. The list is one fixed list in `scripts/matching.py` (`GENERIC_LABELS`). A permit naming only "Plant 2" or only the city fails. This replaces the stricter reading first implemented (a part must hold the organization's name tokens), which failed 1,098 previously passing batch rows; under this ruling 1,080 of them pass, 4 fail as generic labels and 14 fail under the parent rule below.
- **Parent names ("fail everywhere"):** a filing that names only a recorded parent or ultimate parent (or that name plus corporate-form words) never binds a subsidiary's record by machine, on any path, including when the parent's name is part of the site name. It fails with reason `parent_name_lead`, a lead to be read. All 10 batch rows that bound this way through a site-name part now fail `parent_name_lead`.
- **City and locality (controller rulings 2026-11-22, within the owner's standard; not owner rulings):** first, a quoted city other than the record's is a FAIL (`city_differs`). Then, after the source-map lane reported site cities written with a second locality in parentheses ("Cleveland (Solon)"), the locality test moved to `scripts/matching.py`: same state, and the quoted city is a spelling of the record's city or of either part of a parenthetical city, or the two ZIP5 values are equal; otherwise `city_differs`. A missing city on either side is not a conflict, so it is never a FAIL; since the floor ruling below it is not a match either, so the row is HELD. A quoted other state stays `state_differs`. The ZIP5 leg loosens the first controller ruling, on the condition that Codex's read of 40 of the 140 rows it newly passes find no different place. Codex's round-three read: 32 the same place, 0 a different place, 8 cannot tell. The ZIP5 leg stays. Of the 324 batch rows that carried `city_differs`, 278 lose it on an equal ZIP5 (140 become PASS) and 46 keep it; the parenthetical leg changed none, because the gate already read both parts. The last-activity derivation is unchanged; what it would change is measured in `tasks/evidence-binding-gate-2026-11-22/locality_followup.py` as an owner/schema question (tier-B rows are excluded by SCHEMA §4.5).
- **Effect on the quarantined batches 5/6 (34,094 rows):** 20,705 PASS (round two: 20,749). The 44 round-two PASS rows that now fail: 24 name only a recorded parent, 12 quote another city with another or no readable ZIP, 4 state another suite, 4 name only a generic label. No row quotes another state. Measured against the 1,098 rows the stricter site-name reading failed, the same comparison now counts 1,104 (6 rows that both readings failed on the city pass the round-two reading after the ZIP5 leg): 1,086 pass and the same 18 still fail.
- **Decided by:** the repo owner, in session, 2026-11-22, as multiple choice (the split, site-name parts, parent names); the city and locality bullet records the controller's rulings of the same day.

## 2026-11-22: owner rulings after the process retrospective

- **Decision:** five rulings, after three advisers (Claude Fable 5.2, GPT-6.2 Astra, Gemini 4 Neon) reviewed the project's process from one fact sheet.
  1. **Outcome first.** The next data work is a PIC-18 size sprint from files already pulled (OSHA headcounts and Form 5500 for single-site organizations) and a 25-organization live-site trial for process and markets, each as a packet through the binding gate.
  2. **National evidence backfill is frozen** outside PIC-18 until the PIC-18 unknown shares move. Repairs, re-admission of reverted rows that answer a PIC-18 question, and the whole-Atlas audit are exempt.
  3. **Review is tiered by risk.** Data PRs keep two families. Other PRs take one family and at most two rounds. Findings are marked blocking or follow-up, and follow-ups do not hold a merge.
  4. **The comment-reading review check was dropped** after two review rounds found it could not be made sound; the rest of the checker stays (PR #466): size cap, audit record, INPUTS.sha256, and the binding-gate job. Review stays practice, and separate GitHub accounts for builders and reviewers are not created now.
  5. **Lighter running.** Mandatory startup reading is cut to one short page; a preflight command and generated counts precede review; the controller hands off to a fresh thread each wave; Opus is used only when the owner asks.
- **Why:** 38 PRs merged from 2026-11-19 to 2026-11-22 moved the PIC-18 unknowns by zero; 251 review verdicts were spent on 80 PRs, and every PR that reached three or four rounds was a non-data PR.
- **Decided by:** the repo owner, in session, 2026-11-22, as multiple choice.

## 2026-11-22: the day's rulings in one register

- **Decision:** Record the day's rulings and their governing sources in `tasks/owner-rulings-2026-11-22/README.md`.
- **Basis:** Working rule 7 in AGENTS.md §2a (PR #466) records decisions in this ledger.
- **Decided by:** the repo owner, in session, 2026-11-22.

## 2026-11-22: `hq_in_scope` `ne_ohio` means the HQ county is in PIC-18 (owner ruling, in session)
- **Decision:** the owner ruled, in session on 2026-11-22, "PIC-18 exactly" (multiple choice): the stored `hq_in_scope` value `ne_ohio` means the HQ county is in PIC-18; Carroll and Holmes are not `ne_ohio`. SCHEMA 4.4 defined `ne_ohio` by a 20-county list marked "confirm once, then freeze in code"; it now points at `scripts/regions.py` (v1.19.2). The owner ruling of 2026-11-03 (AGENTS.md section 8) fixed PIC-18 as the cluster *reporting* region and superseded the earlier county lists for reporting; it did not by itself change the stored field, which is why this ruling was asked for.
- **Applied:** 312 organizations whose HQ county is in PIC-18 and whose label was `pic12` (224), `ohio_other` (78) or `ohio_statewide` (10) are relabelled `ne_ohio` (`tasks/region-labels-2026-11-22/`). At that head zero organization rows carry `pic12`; 84 carry `ohio_statewide` (79 with a named Ohio county outside PIC-18, 5 with no county), which are not decided here.
- **Why:** a company-owner review found PIC-18 companies labelled with the retired 12-county region or as other Ohio (8 of 20 sampled).
- **Not decided here:** the 20 record errors (an out-of-state HQ with an Ohio county and similar) are leads, not relabels.

## 2026-11-22: owner rulings for the PIC-18 size sprint (headcount age, corporate-word name matches)
- **Decision:** two rulings, taken as multiple choice, that settle `tasks/pic18-size-sprint-2026-11-22/`.
  1. **Headcount age: 5 years.** A filing sets a band only if its source date (ITA: the filing year's period end,
     31 December; inspection: open date; Form 5500: plan year end) is on or after 2021-11-22. Older filings are held as
     leads with the reason `stale_over_5_years`. Recorded in SCHEMA 1 R13 at v1.19.3.
  2. **Name match when the street already matches: corporate words only.** The held name may be a leading run of the
     filing name when every extra token is a corporate-form word from this fixed list: Inc, Incorporated, LLC, L.L.C.,
     Corp, Corporation, Co, Company, Ltd, Limited, LP, LLP, Holdings, Holding, Group, US, USA, U.S., North America,
     Americas. Anything else (Services, Logistics, a place name, another business word) stays held. Containment of one
     name in the other is not accepted.
- **Why:** the size sprint's first candidate set used inspection counts from 1974 to 2015 as 2026 bands, and found
  filings whose company name differs from the record's only by a corporate word (GrafTech International Holdings,
  RTS Companies US) beside filings of other businesses on the same street. The packet applies both rulings; the
  alternatives are kept in controller storage, not in the repo.
- **Decided by:** the repo owner, in session, 2026-11-22, as multiple choice.

## 2026-11-22: `corporation` entity type, and `ohio_statewide` rows with a named county
- **Decision:** two owner rulings of round 13, taken as multiple choice. (1) "Add 'corporation'": SCHEMA 4.4 `entity_type` gains a plain `corporation` value (v1.19.4), filled only where the legal name ends in Inc, Incorporated, Corp or Corporation; public or private is never guessed; Co, Company, Ltd and Limited stay `unknown`. (2) The 79 organization rows still carrying the undefined `ohio_statewide` with a named Ohio HQ county outside PIC-18 get `ohio_other`; the 5 with no county stay held.
- **Applied:** `tasks/entity-type-from-name-2026-11-22/` (LLC and LP/LLP fills as in the earlier packet, plus the corporation fill) and `tasks/ohio-statewide-labels-2026-11-22/`. No evidence rows.
- **Decided by:** the repo owner, in session, 2026-11-22, as multiple choice.

## 2026-11-22: retirement-plan participant counts are leads only

- **Decision (“Leads only”):** A retirement plan's active-participant count is not a plant headcount and fills no size band. It stays a lead.
- **Supersedes:** The allowance for Form 5500 active-participant counts in SCHEMA §1 R13 and §4.13. See `tasks/owner-rulings-2026-11-22/README.md`, I2, for the owner’s wording and the parked packet.
- **Decided by:** the repo owner, in session, 2026-11-22, round 14.

## 2026-11-22: PIC-18 evidence queue from the NAS files; mailing address proves existence and city only; trade-name filers held

- **Decision:** 123 evidence rows (EVD-482000..482122; 10 site rows, 113 organization rows) are applied for 78 of the 419 PIC-18 records in the V-65 / V-68 queue, built from the public OSHA and Form 5500 files held on the NAS (`tasks/pic18-evidence-queue-2026-11-22/`: frame, packet, leads, INPUTS.sha256, build, replay check). The debt baseline shrinks by exactly the 78 entries `validate.py` reports as now passing (V-65 by 67, V-68 by 11). Rules for the rows: one witness per missing claim per record; sites bind on the site's own street, state, city or ZIP5 and a held operator name; `tier_effect` is the strength SCHEMA 4.13 gives the source class (`government_filing`: `supports_A`).
- **Owner ruling (mailing address):** "a Form 5500 mailing address proves EXISTENCE AND CITY ONLY. A filing under the company's legal name with a mailing address in its headquarters city shows the company exists there; it never proves a street or a plant location, and the street line is not published." So existence rows from mailing-role filings stand; an organization `address` row from a mailing-role filing claims `hq_city` and `hq_state` only and its quote carries no street line; the 19 street-level mailing candidates are not applied; nothing from a mailing address is ever attached to a site.
- **Decided by (mailing address):** the repo owner, in session, 2026-11-22, as multiple choice.
- **Controller ruling (trade-name hold):** a filing by an operating subsidiary does not witness the holding company, even when the subsidiary's name is recorded as a trade name of the holding record. An organization binds only through its legal name (or a marked alias of it). Six organizations are held with reason `different_entity_trade_name`: ORG-000383, ORG-000391, ORG-000460, ORG-000482, ORG-001433, ORG-001461 (`held_filer_not_the_record.csv`). Each is a record-quality lead: a subsidiary's or affiliate's name sitting in a parent's `trade_names`.
- **Decided by (trade-name hold):** the controller thread of this orchestration, 2026-11-22. This is a controller ruling, not an owner ruling.
- **Reproducibility, not correctness:** `check.py` replays each row from the raw files by path and sha256 with the builder's own matcher (`binding.py`); it shows the rows can be rebuilt, not that the matcher is right. The outcome line (PIC-18 process, market and size unknown shares) does not move: these rows add existence and address evidence only.

## 2026-11-23: round 15 rulings

- **Audit gate (“Let it ride in the next PR”):** The next data PR may add the prior batch's `tasks/<folder>/AUDIT.md`. The audit still requires `Label:`, `Result: PASS`, `Sample:` and `Reviewers:`. A valid `Result: FAIL` blocks from either source.
- **Usage-limit recovery (“Add the wake, use a cheap worker”):** A BB automation runs every 30 minutes and hands child threads stopped on usage limits to a GPT-6 Luna steward. This is an operating decision.
- **Live-site markets trial:** Run a 25-organization, packet-only trial on the PIC-18 market-unknown frame. The company-page process route remains dropped after one hit in 25 organizations in the prior trial.
- **Decided by:** the repo owner, in the controller's session, 2026-11-23. See `tasks/owner-rulings-2026-11-22/README.md`, round 15.

- **2026-11-23, round 16 (“Build it, archived pages count”):** Admit own-site web evidence by a per-row, cross-family proof and capture replay in the trusted gate. A company’s own archived page within two years counts for market, extending the 2026-11-22 street ruling. Decided by: owner. See SCHEMA §4.13 and the round-16 owner register.

## 2026-11-23: round 17 rulings, accuracy target and enrichment order

- **Accuracy target (“PIC-18 ≤5%, rest ≤10%”):** The unit is the record: a sampled record is wrong if any published field it carries is wrong. The whole-Atlas blind audit is stratified by region. PIC-18 is good enough to publish when the 95% Wilson upper bound of its record error rate is at most 5%; the rest of Ohio and the rest of the country, at most 10%. At a true error rate of 2% the PIC-18 bound needs about 205 effective records read, and at 3% about 460; at 10%, about 55 to 71 per region (continuous Wilson bound at the assumed rate). The earlier blind audits (10: 4.6%; 11: 2.9% content rate at an effective n of 36) measured recently changed records in other frames and are not whole-Atlas rates.
- **Patents, trademarks and FDA lists (“Pilot first, rule later”):** Before any of them may witness a process or market claim, a read-only pilot on 30 to 50 PIC-18 organizations, stratified and with its minimum worthwhile yield and effort cap written down before it runs, reports what each shows; admission as evidence is then an owner ruling. A patent shows an invention, not that a plant runs the process.
- **Residual unknowns (“Publish 'unknown' for now”):** Process and market cells that no admissible source fills are published as unknown. Company outreach is revisited after the pilots report.
- **Pilot order (by staff need):** market verticals first, then process lists, then size and call lists, then the event and membership product fixes.
- **Decided by:** the repo owner, in the controller's session, 2026-11-23, as multiple choice.

## 2026-11-23: pr-rules no longer runs when a PR is marked ready

- **Decision (“do the fix”):** `.github/workflows/pr-rules.yml` drops the `ready_for_review` trigger. On PR #492 a push and a ready toggle seconds apart started two runs on the same head; the queued one was cancelled, the `pr-rules` and `binding-gate` check runs the other posted through the API were filed under the cancelled run's check suite, and the ruleset blocked the merge with every required check green. Marking a PR ready does not change its head, so the checks have already judged it. Reopening a PR, re-running a run by hand, or moving the branch back to a commit already tested can still repeat work on one head; when a merge is blocked with every required check green, push a new commit. PR #493 was also blocked with its checks green, but both of its runs succeeded, so this does not explain it; its cause was not established.
- **Decided by:** the repo owner, in the controller's session, 2026-11-23.

## 2026-11-23: round 18 rulings, audit strata for people, programs and events, and four stale PRs

- **Decision (audit strata):** researchers (people records), programs, and events with their participation rows are each a
  stratum of blind audit 12, held to the same unit as the round 17 target (a sampled record is wrong if any published field
  on it is wrong) at a 95% Wilson upper bound of 10% or less.
- **Decision (stale PRs, "close 2, park 2"):** PR #459 (batch 7, national evidence backfill) is closed under the standing
  freeze, its branch kept. PR #482 (one size band outside PIC-18) is closed; the route re-runs in the rest-of-Ohio phase.
  PRs #464 (Form 5500 organization lane) and #488 (notes history) stay open as drafts until blind audit 12 reports whether
  they matter for accuracy. Nothing in them is rejected.
- **Counting note (AGENTS §7):** the PIC-18 outcome frame of 794 is the owners of active tier A to C PIC-18 sites: 787
  organization records plus 7 ecosystem records. Earlier controller notes called it "794 organization rows".
- **Decided by:** the repo owner, in the controller's session, 2026-11-23, as multiple choice.

## 2026-11-23: round 19 rulings, trademarks and OpenCorporates as leads, a web arm for the process pilot, first-user task 5

- **Trademark goods statements ("Leads only"):** a USPTO trademark goods statement never fills a market cell. One that names
  a use sector ("gloves for medical use") queues the organization for its own-site page, and that page is the witness under
  the round 16 ruling. Basis: the read-only market pilot (40 of the 316 PIC-18 market-unknown owners) met its pre-registered
  floor exactly, 4 of 40 organizations with a reader-agreed term (rows: 8 agree, 2 disagree, 1 unresolved), but 6 of the 8
  agreed rows rest on abandoned applications (3) or cancelled registrations (3), which show a past product line, not current
  sales; the other 2 are live registrations (USPTO status 702). The owner was asked with "all 8", a controller error found in
  review; the corrected count does not change the reason for the ruling, and the owner is told of the correction. The FDA food-contact
  and drug master file lists and the NHTSA lists matched 0 of the 40 and are not used for market.
- **OpenCorporates ("Leads only"):** an OpenCorporates result may point to a charter or a status; a fact enters `data/` only
  after it is read at the state registry or another held source and cited there. OpenCorporates values never enter `data/`,
  `tasks/` or a pull request. Basis: its terms require ODbL share-alike for data combined with ours, and `data/` is CC BY 4.0.
- **Own-site pages in the process pilot ("Yes, pilot it"):** the process pilot adds an own-site web arm with the same
  pre-registered design (40 owners, a 10% minimum yield, about 6 fetches per organization). This reopens, for a pilot only, the
  company-page process route recorded as dropped in round 15; if the arm misses its floor, the route stays dropped.
- **First-user task 5 ("Answered within ruling"):** "PIC-18 companies that are not PIC members" is graded Answered: under the
  2026-11-01 ruling the site lists organizations not on the public member list, with its caveat, which is the most that public
  data allows.
- **Decided by:** the repo owner, in the controller's session, 2026-11-23, as multiple choice.

## 2026-11-23: round 20 rulings, own-site process evidence, blind audit 12 scope and size, program specialty tags

- **Own-site pages for process ("Admit, company or plant"):** a company's own page may witness a process claim. It fills the
  organization record; it fills a plant (site) only when the page names that plant's city or the company has one site. The
  per-row proof and capture replay of SCHEMA §4.13 (PR #490) and a reading by a second model family apply to every row.
  Basis: the read-only pilot met its pre-registered floor exactly: a reader agreed with a proposed term for 4 of 40 sampled
  PIC-18 owners whose process is unknown (5 of 5 terms agreed); 2 of the 4 tie the process to the PIC-18 plant.
- **Patents stay leads.** The patent pilot missed its pre-registered floor: a reader agreed for 3 of the 50 PIC-18
  process-unknown owners with a patent lead, against a floor of 5.
- **Blind audit 12 ("Accept all defaults", "Raise to 110"):** the scope questions B1 to B9 of
  `tasks/blind-audit-12-protocol-2026-11-23/PROTOCOL.md` section 9 take their recommended defaults, and each 10% stratum reads
  up to 110 records at stage 2 instead of 71 (a stratum whose true record error is 3% then passes about 77% of the time, and
  one truly at 10% passes about 1.4% of the time). PIC-18 stays at 205 and 460.
- **Program specialty tags ("Wrong: REJECT"):** a specialty tag on a program record that its cited page does not state makes
  the record wrong; the tag is removed or replaced with what the page states.
- **Decided by:** the repo owner, in the controller's session, 2026-11-23, as multiple choice.

## 2026-11-23: rounds 21 and 22, archive copies for own-site rows, binding-gate fixes, blind audit 12 placements

- **Archive copies for own-site rows ("archive.org API keys"):** SCHEMA §4.22 archive-at-capture and validator V-66 stand
  unchanged. Unauthenticated Save Page Now returned a bot check, so own-site pages are saved through the authenticated
  archive.org Save Page Now API with keys the owner supplied; the keys are held outside the repository and never appear in it.
  A by-hash copy in the private raw store does not stand in for the public archive reference.
- **Binding-gate fixes ("Fix both"):** the binding gate judges evidence rows on program and ecosystem records, binding each to the names and places its record holds; for program and ecosystem office
  rows it adds an own-page test, so a sibling page on the same institution's domain does not bind. It keeps the page's
  article text when a Divi-style page has an empty main element. An empty extraction is never a PASS. Merged as PR #501; no
  existing row changed to or from PASS.
- **Blind audit 12 records without a stratum ("Place by city, exclude 1"):** of the 31 records that fit no stratum at
  `0b191fe6`, 28 are placed from sources. Two Ohio-headquartered organizations with no sourceable county (ORG-001835,
  ORG-001503) go in the rest-of-Ohio stratum because every county their city spans lies outside PIC-18; no county is written to
  the data. ORG-003769 is left out of the frame as a named, counted exclusion until a state registry read settles its
  headquarters.
- **Decided by:** the repo owner, in the controller's session, 2026-11-23, as multiple choice.
- **Controller rulings under these decisions** (not owner answers): where Save Page Now deduplicates a save to an earlier,
  unchanged capture, that capture is cited with its true date once the row's quote is reproduced from it (first applied to
  ORG-000038's two pages in PR #502). The audit 12 draw will read the placements above from a checked-in list in
  `tasks/blind-audit-12-protocol-2026-11-23/`, added with the B6 data pull request, rather than from a new placement rule.

## 2026-11-23 12:48: R13 size filings, “10 years, dated”

> Accept filings up to 10 years old. Each band shows its source year, and a newer contradicting source
> always wins. The audit 12 readers check a sample.

The repo owner superseded the v1.19.3 five-year limit for R13 sources 1 and 2. SCHEMA v1.19.7 records
the band-write cutoff, the hold for a stale or superseded filing, and the existing evidence and site
notes fields that show the source year.

## 2026-11-23 13:16: R13 filing-date and audit checks (round 24, item 2)

> Say what is checked

At write time the integrator replays each filing date against the raw snapshot. The PIC-18 ten-year
packet supplies `tasks/pic18-size-10yr-2026-11-23/check.py`. Blind audit 12 readers check sampled bands
against their cited filings with the filing year shown.

## 2026-11-23: round 24, item 1 · blind audit 12 judged values

- **Owner ruling (“Withhold now, repair too”):** Keep a flagged judged field in the Audit 12 packet and show its value as
  `[withheld for blindness]`. Audit the underlying claim from evidence and give the withheld literal no correct credit.
  Report withheld cells separately per stratum. Header and metadata leaks remain hard failures.
- The controller approves only exact non-NAICS-source false positives from the private inventory. A separate lane
  repairs the public labels. The [protocol addendum](tasks/blind-audit-12-tooling-2026-11-23/PROTOCOL_ADDENDUM_2026-11-23.md)
  records packet handling without reopening the sealed draw.

## 2026-11-23: blind audit 12 reading gates, “Settle PIC-18 first”

> Settle PIC-18 first

- **Owner ruling.** The audit 12 draw waits until two things are done. First, all 234 unread PIC-18 evidence rows from
  screen 5 are read. Second, the PIC-18 evidence rows already known not to tie to their record (43 rows) are re-cited
  or withdrawn. This supersedes the controller's earlier closing of that gate on a 50-row sample. The reason is the audit
  12 protocol. A row whose page names a different operator or street makes its record wrong, and an unsettled claim
  makes its record unresolved. PIC-18's pass rule counts both, however the reading gates graded them.
- **Sample rule outside PIC-18.** Reading gates for rest of Ohio and rest of country close on a seeded random sample of
  50 rows. The seed is written down before the draw, and reading stops at 2 or fewer REJECT. The unread rows are listed
  as accepted open. They are not graded. Fifty rows bound the REJECT rate at about 7% (95% upper bound), which cannot
  show 5%. That is why PIC-18 is read in full.
- **What REJECT means.** A REJECT is a contradiction: the readable page names a different street or place than the
  record. A page that is readable but does not tie the claim to the record's place is STILL_UNCERTAIN, not wrong. The
  reading was fixed before the samples were read, and it is not changed for one region after its result is known. In
  PIC-18, rows that stay STILL_UNCERTAIN are re-cited or withdrawn under the ruling above.
- **Screen 5 routes rows, it never decides them.** Screen 5 replays each row's literal quote against its cached archive
  capture. A FAIL or NOT_INSPECTED row goes to a reader. A PASS is not counted as a read, and the screen's false-fail
  rate is reported, not gated.
- **G6 and G7 narrowed.** G6 covers the ATLAS-9 reads outside PIC-18. G7 covers the second read of ATLAS-8's 86 open
  claims. Both close when their reads are in. What stays STILL_UNCERTAIN after the second read is listed and accepted
  open; it does not hold the draw. Inside PIC-18, the owner ruling above supersedes this.
  For Claude-built rows, a read by another model family decides.

## 2026-11-23 16:18 · PIC-18 settlement evidence floors (owner ruling)

“Keep row, mark unverified (2026-11-23)”. Retain the evidence rows whose
withdrawal would breach the presence floor. Apply the owner-listed tier U
marks with a dated note and preserve their record values. For non-floor
identity, existence and address withdrawals, tier U applies when the
remaining rows fail to tie the affected claim. Records in the owner's
keep list stand at their held tier.

The owner also ruled “Yes, one gate PR”. Press notices, mailing city and
municipality at the same ZIP, 43-character federal names, registry name
variants, blank-street registry rows, EDGAR and Kent's header wrapper
will be considered in a separate gate PR. Hold the re-admission rows
until that gate work lands. This data PR applies the current gate.

At 16:32 the controller confirmed the published owner census and the
Enpac and Intertex tier marks. Each record listed below moves to U.

| Record | Prior tier | Audit frame at `1600f540` |
|---|---|---|
| `ORG-000068` | C | PIC18_RECORDS |
| `ORG-000206` | B | PIC18_RECORDS |
| `ORG-000212` | B | PIC18_RECORDS |
| `ORG-000265` | B | PIC18_RECORDS |
| `ORG-000404` | B | PIC18_RECORDS |
| `ORG-001397` | B | PIC18_RECORDS |
| `ORG-001762` | B | outside |
| `ORG-001832` | B | PIC18_RECORDS |
| `ORG-001857` | B | PIC18_RECORDS |
| `ORG-001886` | B | PIC18_RECORDS |
| `ORG-002011` | A | PIC18_RECORDS |
| `SITE-001296` | C | PIC18_RECORDS |
| `SITE-001575` | C | PIC18_RECORDS |

The PIC-18 owner census moves from 794 to 792 owners of active tier A–C
sites. Beacon ORG-001511 leaves after SITE-001575 moves to U. ORG-001197
leaves after SITE-001296 moves to U because its other sites fall outside
PIC-18. The controller confirmed both departures. At the resulting
792-owner denominator, 305 have unknown process, 303 have unknown
market, and 372 have unknown size. The count changes reflect the frame
departures. The separate audit strata are listed for the tier marks.

## 2026-11-23 — One evidence binding gate PR for ATLAS-38 G8

The owner approved “Yes, one gate PR (2026-11-23)” so the gate can read
the seven source and capture cases holding up PIC-18 settlement. The
gate change precedes the data re-cites. A trade notice's dateline can
bind organization existence. An HQ claim requires an explicit
statement of headquarters. §4.13 records the remaining admission rules
and the limits on street, locality, names, filing identity and replay.

## 2026-11-23 17:34 · Dead website domains

“Dead domains: blank the website field and record the old domain in
notes.” Apply the owner ruling to the two reviewed entries. ORG-001971
holds the parked domain odm.com. ORG-002064 holds a 404 at
polytechmolding.com that does not identify the firm. Clear both website
cells, retain the date and observed condition in notes, and keep each
organization status.

## 2026-11-23 17:34 · SPE sections belong in ecosystem

“Ecosystem, not sites.” Retire the Akron and Cleveland SPE site
representations, SITE-000091 and SITE-000163, while retaining both site
IDs. Their active trade-association records are already in ecosystem
as ORG-000091 and ORG-000163. Apply after the audit 12 draw and the
all-notes repair. The existing `closed` site tombstone convention marks
the retirement of the site records. The sections remain active.

## 2026-11-23 19:21 · Gemini stays the second review family, with a watchdog

“Keep Gemini + watchdog.” Gemini remains the second review family and
the audit 12 adjudicator. Gemini threads that hang mid-turn are stopped
by the controller's watchdog, and messages lost mid-turn are delivered
again once. After three hangs in two hours, that thread's work moves to
another family.

## 2026-11-23 20:00 · Audit 12 records with one independent family

“Gemini + flagged read + lead.” An audit 12 record that only one family
other than its builder can read is read by Gemini, gets a second read
from a family flagged as the builder's, and gets a lead re-check from a
fresh source fetch. The report shows each stratum with and without these
records. The 21:27 stop below overtook this ruling: no lead re-checks ran,
and the report gives no per-stratum rates with or without these records.

## 2026-11-23 21:27 · Audit 12 stopped early; the next audit is lean

“Stop now, verify sample.” Reader flags already placed each stratum past
or near its fail line, so all readers and lead lanes were stopped. Some
strata reached the line only with unresolved records counted as errors,
which is the audit's conservative treatment. One verifier confirms flagged
errors in rank order until each stratum fails on verified errors alone.
It then sorts all flagged errors, most of them unverified, into repair
classes. There is no stage 2, no third read and no lead sweep. The audit
12 report gives the result and the error classes, not exact rates.

“Lean design.” The audit after the repairs uses a smoke sample before any
draw, fetches sources once by script and replays quotes, gives each
record one reader with plants and a second family only for flagged
records plus a random check share, and stops a stratum once it crosses
its fail line. The controller drafts this as a protocol revision for an
owner ruling, with sizes and false-pass risk recomputed.

## 2026-11-23 21:43 · Fan-outs are priced and piloted (AGENTS.md §2a rule 8)

“Make this a durable rule change.” Audit 12 spent about 450M input
tokens across 20 threads to confirm a FAIL its pilot had already shown.
The Claude and Codex shares come from their provider usage logs. The
Gemini share comes from bb's usage events, because no Gemini usage log
was read, so it is unverified. The owner adopted AGENTS.md §2a rule 8 as
written: a fan-out is priced and piloted before it scales, an audit is
lean, and spend is measured while work runs. Review corrected only its
sentence on enforcement, to state exactly what the harness checks.

- “8 live children.” The controller's harness refuses a spawn while 8 or
  more of its children are unarchived, unless the command carries the
  owner's fan-out tag. Without that tag it also refuses spawns run from
  a script file or a loop. It refuses a spawn command it inspects
  directly when the brief has no `Budget:` line, tag or not. It does not
  read the briefs inside an owner-tagged script; the controller checks
  those by hand.
- “200M per 2 hours.” When the controller's children have spent more
  than 200M input tokens over a rolling two hours, the controller's
  outcome line turns RED. Spawns are then blocked unless marked critical
  path or owner-approved. The meter counts only the controller's direct
  children and reads Gemini spend from bb's events. The first week's
  spend rate goes to the owner.
- “Yes, skill + lesson.” The cross-project bb-orchestration skill gains a
  fan-out budget section, and the lesson is proposed for the portfolio
  lessons file.

Rule 8 is practice in this repo. CI does not check it. The controller's
harness checks only the parts listed above, and it cannot see spawns by
other harnesses, by children or in other projects.

## 2026-11-23 22:01 · Drop notes from the release

“Drop notes from release.” The release's organization and site CSVs omit
the `notes` column, and so do the matching tables of the bundled SQLite
copy. The repository keeps its notes, and the site pages keep withholding
them. Implemented in `scripts/export_release.py`. Reason: notes are the
build narrative ("Created ... in integration pass 17 ...") and about 4,600
organization and 6,800 site notes cells carry process wording.

## 2026-11-23 22:32 · Process and material vocabulary repair

“Move to other-note.” Keep off-vocabulary process and material wording
verbatim in semicolon-joined, deduplicated `processes_other_note` and
`materials_other_note` on organizations and sites. A fully exact spelling
conversion may use the controlled tokens. The conversion splits on commas
and “and”, lowercases, strips “ (secondary)”, and turns spaces, hyphens
and slashes into underscores. Each part must match an allowed token.

“Allow on Ring 3.” The nine Ring 3 subtype terms are allowed as process
tokens only when the record's primary ring is 3. Preserve the wording
in the other-note when the term is outside the record's process vocabulary.
Schema v1.19.8 and the V-55 pass are in
`tasks/p1-vocab-repair-2026-11-23/`.

## 2026-11-23 · Audit 13 scope and decision rule (ATLAS-7)

**“Smoke only”.** After the remaining repairs land, read up to 40 random
PIC-18 records. Stop on the third record with a confirmed error or
unresolved claim. Return the number read, errors, unresolved rate and
measured input tokens per record by provider to the owner before any draw.

**“Decide after the smoke”.** The full draw and its decision rule await a
separate owner ruling. With perfect reads and a true PIC-18 error rate of
2%, the proposed stress-safe rule passes PIC-18 in only 9.9% of draws.
The proposed plant-calibrated rule raises that probability to 80.4% and
depends on the plants representing reader misses on real records.

| Stage or design | OpenAI | Google | Anthropic | Total projected input tokens (millions) |
|---|---:|---:|---:|---:|
| Authorized smoke | 1.69 | 1.92 | 0.54 | 4.15 |
| Smoke and stress-safe draw (option) | 37.43 | 39.85 | 6.54 | 83.83 |
| Smoke, calibration and calibrated draw (option) | 60.31 | 78.39 | 7.70 | 146.40 |

Estimates use short per-record calls. The smoke measures actual cost.
The calibrated option includes 45.75M input tokens for additional plants.
The previous audit consumed about 450M input tokens. [Sizing assumptions and calculations](tasks/blind-audit-13-protocol-2026-11-24/SIZES.md)

## 2026-11-24 · Step-back rulings: publish only what is stated, PIC-18 only, one family for mechanical PRs

The owner asked why accurate data has been so hard to get. The controller measured three causes:
- The registries the Atlas links (7,992 links: FRS, TRI, EIN, SEC and others) hold identity, address, industry codes and some headcounts, but not what a plant makes or whom it sells to.
- Company sites mostly do not state the fact. Of 27 headquarters reads left unsettled on 2026-11-24, 17 pages loaded but did not say where the headquarters is, 6 stated something the evidence rules cannot admit, and 4 failed to load.
- Every change paid a fixed review cost. PR #539 needed four rounds for 15 cells, and every refusal on #539 concerned a checking script, not the data.

Under the audit 13 rule (stop on the third record with an error or an unresolved claim, of 40), the controller forecast that the smoke was likely to stop early whatever the repairs. Audit 12 found 74 of 189 PIC-18 records with no demonstrated error but a claim nobody could confirm, and repairs do not make an unstated fact confirmable.

**"Publish only what's stated."** A published value that no public source states goes back to unknown and is kept internally as a lead. The audit counts only published values, and an unknown value is not an error. Unknown counts will rise before they fall. The withdrawal pass is specified, with its counts measured, before any data change.

**"PIC-18 only."** Repairs, reads and the audit's pass or fail cover the PIC-18 owners (organizations and ecosystem entities with an active tier A–C site in the 18 counties) and their sites. National records stay as they are, labelled unaudited. A script may still fix them at no extra cost.

**"One family for mechanical."** A data PR that applies a written rule by script, with no reading or judgment, adds no evidence row, and passes a deterministic check that rejects planted defects needs one review record, from Codex (OpenAI). Reads, judgments and new evidence keep two families. AGENTS.md §2a rule 4 is amended to match.

Decided by the repo owner in session, 2026-11-24 07:35, by multiple choice; all three were the recommended options.

## 2026-11-24 · Look-back rulings: what an audit counts as wrong, and how "publish only what's stated" is applied

The owner asked for a look-back over the whole project since 2026-11-06: his decisions, the plan, the schema and the ways
of working. Seven models answered independently (Claude Opus 5.5, Claude Sonnet 5.5, GPT-6.2 Astra, GPT-6.2 Sol, Gemini 4
Hydrogen, Gemini 4 Carbon, Gemini 4 Neon). The controller re-measured every number that drives a ruling.

**The census behind this morning's withdrawal figures was wrong.** It read only one OSHA citation format for size bands,
and it was too strict for process and market: it required the 2026-11-23 proof file and exact vocabulary words. Among
the 792 PIC-18 owners at e9bcabf:
- 420 owners have a size band. 359 have at least one non–Form 5500 size-evidence row behind it (357 a government
  filing, 2 only company website statements), 32 rest only on Form 5500 and 29 have no size row.
- 460 owners have a process value and 489 a market value. A script screened each published value against the evidence
  rows of its record and owner. Of 961 process values, 118 have a row that names the value and carries a quote marker,
  679 have a row that names it without one (mostly 2026-11-01 rows such as "organizations.processes includes X (org
  scope, own-site disclosure)"), and 164 have no row that names it. For 1,358 market values the split is 561, 771 and
  26. 81 process owners and 234 market owners have at least one value of the first kind.
- These are screening results. The screen does not establish that a quote supports the value, that the row binds to
  the record, or what a reader verified.

The figures given to the owner at 12:52 (unknown 789 / 791 / 769 of 792 after withdrawal) are void. For the values
whose row names them without a quote, the stored own-site corpus manifest lists a page with the cited page's host and
path for 383 of 679 process values and 511 of 771 market values (502 if the query string must also match). Whether the
stored page is the cited page is not checked.

**How "publish only what's stated" is applied.** Nothing is withdrawn in bulk. A cited value is re-read against its stored
page first; a value no source states goes back to unknown only after that check. A pilot of the re-read runs before any
withdrawal (owner answer 2026-11-24, "pilot"). The schema proposal for a per-value basis (stated, from a filing, cited,
none), derived from evidence rows and shown on the site, waits for the pilot's result.

**What an audit counts as wrong.** A published value is wrong only when a source contradicts it. A value that cannot be
confirmed is reported as unconfirmed, by field, next to the error rate; it is not counted as an error. The PIC-18 bar
(at most 5% wrong) gates on the core fields: organization or site name, operating status, street, county and polymer
relevance. Process, market and size report their error rate and unconfirmed share by field and do not gate. Audit 13
keeps its smoke-first design under this unit. Under the previous unit, audit 12 recorded 74 of 189 sampled PIC-18
records whose only finding was an unresolved claim, with no demonstrated error; it also recorded 12 confirmed PIC-18
error cases.

**Also answered.** Company outreach (PIC staff asking companies to confirm their listings): a pilot is approved in
principle for later, not now. The first-user note to the City of Akron waits until the PIC-18 sites with no street are
filled. The way the controller asks the owner for decisions is unchanged.

Decided by the repo owner in session, 2026-11-24, by multiple choice. The audit unit was the recommended option; the
other three answers ("pilot, but in the future", "wait", "keep as now") were not.

## 2026-11-24 · Owner rulings 10:29: map-listing streets, per-value basis labels, implied and unstated values, filing name variants

The owner answered four questions by multiple choice. All four answers were the recommended option. Each ruling is
recorded below with its measured effect. The implementation (generator, gate routes, fills) comes in later PRs that
cite this one; this entry and its PR change no data file and no script.

**1. Map-listing streets.** A street from a map listing (Overture Maps places first; Google listings for what remains; the
owner accepts the terms-of-service exposure of Google-derived addresses) may fill a blank site `street_address` only where
it agrees with a second source the Atlas holds: a government filing (OSHA, EPA, SBA PPP or SAM.gov), the company's own
site, or an existing held lead. Same-street equality is decided by script. The cell carries the label "from a map
listing". The route never overwrites a street. A filled street is audited against the PIC-18 5% street error bar like any
other street. County still settles from the physical address (Census geocode), never from the listing.
- Measured (PIC-18 sites with a blank street_address, 155): Overture matched 68 by held name and city; 44 of those agree
  with a held lead. About 6 of 57 listings point elsewhere (the headquarters or another plant). That is why name and city
  alone were not chosen.
- Does not change: county settlement, the street error bar, the never-overwrite rule, the PMIR bar (a platform row is
  never sole support for a scope claim). Emails and phones are never pulled.
- Written as: SCHEMA v1.20.0 §4.13 (source class `platform_category`, no vocabulary addition; ceiling `supports_C`),
  AGENTS.md §2a rule 3, and the `overture-maps-places` row in `docs/sources_registry.csv` and `docs/SOURCES.md`.

**2. Unquoted process and market values.** A bound evidence row can name a value and a page and save none of the page's
words. Those values stay public with a generated per-value basis label: stated, from a filing, implied or not yet
checked. All 385 PIC-18 owners with such values are re-read against their stored pages.
- Measured (re-quote pilot: 40 PIC-18 owners, 168 values, one Codex reader): 0 values contradicted by their page; of the
  values with a readable page, 68% of process values and 74% of market values were stated.
- Does not change: the binding gate and the quote rules for new rows; this ruling concerns values already public.
- Written as: SCHEMA v1.20.0 §4.24 (the generated `value_basis` table) and the §4.4 and §4.5 pointers.

**3. Implied and unstated values.** A value the page supports only by inference ("we make bottles" for blow molding) stays,
labelled "implied". A value the page does not state (NOT_STATED) is hidden from public display, never deleted, until a
fresh fetch of the company's pages finds it or confirms it is absent. The ruling names no step after a confirmed absence. The controller reads the
earlier ruling (a value no source states goes back to unknown) as applying; that is an inference, not part of this ruling.
- Does not change: the record tables keep a hidden value throughout. The ruling states nothing about how an audit counts a
  hidden value; the look-back ruling's audit unit stands as written.
- Written as: SCHEMA v1.20.0 §4.24 (basis `implied`; basis `not_found_pending_refetch`, withheld from display).

**4. Filing name variants.** Where an OSHA or EPA filing at the same street and city names the operator in a longer or
older form ("Swagelok Manufacturing Company" for "Swagelok"; "C 4 Polymers" for "C4 Polymers"), the filing's name is added
to the organization as an alternate name citing that filing, when its distinctive words match a held name and its street
and city match. A second model family checks each addition. The street then fills through the normal binding gate.
- Measured: 17 PIC-18 sites.
- Does not change: no records merge, no `org_id` changes, no tier rises; the binding gate's operator test is unchanged,
  it simply sees a name the record now holds.
- Written as: SCHEMA v1.20.0 §4.13 (the rule) and §4.4 (`trade_names[]`, marker `(OSHA filing name)` or
  `(EPA filing name)`, following the `(TRI filing name)` entries), and AGENTS.md §2a rule 3.

**Follow-on PRs (each cites this one).** The `value_basis` generator, its validator rule and the first fill from the
385-owner re-read; the gate routes for the map-listing street and the filing name variant; the Overture street fill
(moving the raw pull to the shared store); the name-variant additions with their second-family checks.

Decided by the repo owner in session, 2026-11-24 10:29, by multiple choice. All four were the recommended option.

## 2026-11-24 · Per-value basis generator (SCHEMA v1.20.1): where verdicts live, precedence, grain

Implements the 10:29 per-value basis ruling (SCHEMA §4.24). Not an owner ruling: §4.24 left these four points to the
generator's PR, and this entry records what that PR fixed. Each is open to an owner change.

- **Verdict storage.** A reader's verdict is `tasks/<folder>/VALUE_VERDICTS.csv`, in the re-read lane's `values.csv` format
  as written. It lives under `tasks/` because lanes never write `data/` (AGENTS.md §2 rule 7); the generated
  `data/value_basis.csv` changes in the same PR, so a verdict reaches a label only through a data PR and its review. A
  packet counts only when its README names the reader's family and a different family that checked it (the controller's
  instruction that labels from the 2026-11-24 re-read publish only after the Gemini check). The generator adds no
  evidence: the line's `evidence_id` is the bound row that names the value.
- **Precedence.** Verified quote (`BINDING_PROOF.csv` `VERIFIED`, claim hash unchanged, or a replayed STATED verdict) beats
  a filing statement beats the latest reader verdict (IMPLIED, NOT_STATED) beats a bare naming row. A proven quote
  outranks NOT_STATED. Two verdict classes on one latest date stop the generator.
- **Grain.** `stated` and `filing` come only from a row on the value's own record. A row on the organization gives a
  site's value at most `not_yet_checked`; the re-read pilot's rule is that a corporate statement does not settle a plant claim.
- **What V-69 cannot see.** CI has no page store, so a STATED verdict's quote is replayed only where `--pages` is given;
  V-69 warns with the count not replayed. For the proof route it checks the proof line and the claim hash and does not
  fetch the capture again (the gate replayed it when the row merged).
- **Values no bound row names.** Controller ruling 2026-11-24 after the first run: every published process or market value
  gets a row. A value no bound row names is `not_yet_checked` with an empty `evidence_id`, and V-69 fails on a published
  value with no row. 165 process and 26 market values on PIC-18 owners' display rows are in this state (unit: one value on
  the record that supplies it).
- **Evidence text in the release.** The release bundle also blanks evidence `claim_detail` and `notes` that name a withheld
  value and drops the site's capability row for it (consistent with "hidden until a refetch"); the repository CSVs keep them.
- **Round 1 review (Codex, 2026-11-24).** A verdict labels only its own record (owner, grain, page folder, own-record
  evidence for STATED); a verdict that cannot be applied stops the generator; a verdict labels a key only for the page a bound
  row cites (VALUE_PAGES.csv), another page of the same site gives no label and never withholds; a filing or proof row must assert this value
  in its head; graph links carry the label; the release refuses a stale database basis table.

Measured at the first table (9,551 rows, one per held process and market value on organization and site rows, all
states): 42 `stated`, 18 `filing`, 9,491 `not_yet_checked`, of which 2,944 are named by no bound row. The screen's 118 and 561
quoted values (process, market) on PIC-18 display rows reconcile to these rows: 18 `filing` and 10 `stated` of the
process values, 18 `stated` of the market values, and the rest `not_yet_checked` because the quote sits on an organization
row for a site value (9 process, 216 market) or has no verified proof or names several values (81, 327).

## 2026-11-24 · Owner rulings 12:12

- **Write it + check it.** Record an organization website only after fetching a page on that site that shows both a
  name the organization record holds and an Ohio locality. The binding gate checks changed website fills for
  replayable own-site evidence that shows both. The site corpus fetcher refuses LinkedIn requests outright.
- **Merge on the fix.** Merge PR #550 on its post-cap fix, with no further review round.
- **Pilots.** Approved “Links + website leads,” “Refetch with PDFs and JS rendering,” and “New street witness (FMCSA).”
  The Brave Search pilot was not approved.

## 2026-11-24 · Audit 13 smoke choices

The amended audit 13 protocol (PR #554) left four choices open. The owner answered each; the protocol now carries the ruled option. Options and measured consequences are kept in `tasks/blind-audit-13-protocol-2026-11-24/OWNER_CHOICES.md`.

1. **Smoke stop.** The smoke stops at the third record with a contradicted core field (name, operating status, street, county, polymer relevance) of the 40 it reads.
2. **Descriptive fields.** A contradicted process, market, size or other non-core value is reported by field with its error rate and never stops the smoke.
3. **Unconfirmed claims.** No ceiling on the unconfirmed share now. They are reported per field, and the owner sets any ceiling for a draw after the smoke.
4. **Polymer relevance.** A reader judges only whether the record, at its grain, is in or out of scope under the SCHEMA ring tests and exclusions. A different ring number is not an error.

Decided by the repo owner in session, 2026-11-24 13:13, by multiple choice. All four were the recommended option.

## 2026-11-24 · Owner rulings 15:15

Decided by the repo owner in session, 2026-11-24 15:15, by multiple choice. All three were the recommended option.

1. **HQ county stays a core field.** An organization's `hq_county` is judged and gates the audit 13 smoke like `county`.
2. **Report filed values with no replayer as not inspected.** A filed value whose class has no replayer (PPP and other size bands, filing NAICS, every registry class, and a NAICS value whose source name is blank or withheld) no longer blocks preflight or packet issuance. It is reported by field as NOT_INSPECTED, with counts: never as checked and never as unconfirmed. The reader packet says it was not inspected. Classes with a replayer (OSHA ITA, OSHA inspection, Form 5500 lead-only) keep their receipts. Unknown builder family, an unapproved leak flag and a missing core-field dependency still block. `tasks/blind-audit-13-protocol-2026-11-24/PROTOCOL.md` carries the amended replay paragraph.
3. **The web re-read scales by a cheap run.** Scripted fetch and passage search, one short reader call per owner, 50 owners first (about 8M input tokens), then about 47M if the batch holds at 20% or better.

## 2026-11-24 · Owner ruling on #556

Decided by the repo owner in session, 2026-11-24, by multiple choice ("Run now, hand-check", the recommended option). Codex refuted PR #556 in both review rounds with 9 open BLOCKING findings (listed in the PR body under "Follow-ups (owner ruling)").

- Merge #556 with the 9 findings as follow-ups.
- The audit 13 smoke runs one call at a time (`smoke.py run --window 1`).
- The controller hand-checks every record counted in k, every plant verdict and every packet's record ID against its sealed row.
- The smoke report marks the size-band and child-field tallies unreliable.
- The findings are fixed before any full draw.

## 2026-11-24 · Owner rulings 19:08 and 20:51

Decided by the repo owner in session on 2026-11-24, by multiple choice. The 20:51 rulings were all the recommended option.

At 19:08:

1. Fill ceiling 'Measure ceiling, then floor': after the smoke, a script-only census of how many of the 327 process-blank PIC-18 owners have any own website or filing that could state a process; then any fill route stops when a batch yields under 20% of owners.
2. Fitness 'Re-grade and ask': after the smoke, re-grade the 12 first-user tasks on current main and the owner asks the first user whether they use the Atlas and what is missing; that decides fill vs accuracy work.

At 20:51:

1. Smoke attempt 1 counts as stopped at a missed control (the overturned plant); its reads stay on record as partial. Next: one combined fix PR (runner persists every reader answer; a plant passes only when the swap is named; the nine #556 follow-ups), then a new sealed smoke attempt on a new snapshot.
2. P1 exit: a clean smoke (every plant verified) unlocks the full PIC-18 draw; the draw's result is the P1 exit.

## 2026-11-25 · Owner ruling 07:57 on the audit 13 plant check

Decided by the repo owner in session on 2026-11-25, by multiple choice, the recommended option ("Hand-check decides"). It followed the Codex review of the script witness rule on PR #561 (comment 7162985847).

- The witness rule for plants (eligibility and detection) is a flag only and never the decider.
- For every plant read in a run, `score` requires a hand-check record written by the controller in the run folder (`handcheck.csv`: plant id, quote, verdict CAUGHT, MISSED or INELIGIBLE, reviewer, time; mode 0600, create-exclusive) and refuses while any plant lacks one or the file was altered after the lock line.
- The published plant result comes only from those records, with the script flag shown beside it.
- Draw-time eligibility stays a filter. The draw receipt lists every plant's eligibility quote, so the hand-check can reject an ineligible plant; it is counted as INELIGIBLE and reported.

## 2026-11-24 · Owner rulings 21:21 and 21:26 (robots.txt, bot checks, LinkedIn)

Decided by the repo owner in session, 2026-11-24 and 2026-11-25.

1. **Robots (21:21).** "Rule change: ignore robots.txt. Click thru bot checks." A robots.txt Disallow no longer blocks a fetch in `scripts/site_corpus.py`. The ruling also said to click through bot checks (see item 4: that part waits).
2. **LinkedIn (21:26).** "LinkedIn should not be barred." Logged out first, no account, no cookies. This reverses owner battery B-LINKEDIN (2026-11-04, navigation link only) for the fetcher. How a LinkedIn page may count as evidence is a separate change (SCHEMA and the binding gate), not made here.
3. **Kept lines.** The per-host rate limit and Crawl-delay stay. No paid CAPTCHA-solving service, no proxy rotation and no cookies. A bot-check page goes to a manual list (`BOT_CHECK_MANUAL`, `manual-bot-check.csv`). LinkedIn company pages (`/company/`, `/showcase/`) only: personal profiles (`/in/`, `/pub/`), staff lists and employee names stay out by the privacy rule (AGENTS.md §6).
4. **Split (2026-11-25 06:08, multiple choice, as recommended: "Split it").** The robots, LinkedIn-company-page and privacy changes ship now. The click-through half of the 21:21 ruling does not: a bot-check page is receipted `BOT_CHECK_MANUAL` and listed in `manual-bot-check.csv`, never `ok`. The Chrome retry and its click logic were taken out of PR #560 after two review rounds (REFUTE on redirect hops inside the browser, cookies, coordinate clicks) and wait for a separate browser PR. Privacy exclusion (staff-directory paths, form-only pages) applies before any body is stored, at every status.
5. **LinkedIn stores an extract only (2026-11-25 06:32, multiple choice, as recommended: "Allowlist, last pass").** After Codex refuted the people-block stripper, a LinkedIn company page is never stored: only an allowlisted extract is (name, description/About, website, industry, company size range, headquarters or flat address, founding date and Specialties). If the last review rejects it, LinkedIn comes out of #560 and the rest merges.
6. **Structural fixes (2026-11-25 06:43, multiple choice, as recommended: "Structural fix, repro-only check").** A robots.txt body is never written to disk: it is parsed in memory and only a receipt (status, hash) is stored. Any cached LinkedIn receipt whose stored file is not an allowlisted JSON extract is a miss, is never replayed, and its files are purged.
7. **Visible per page.** Each receipt records `robots_disallowed` (yes, no, unreadable), so the change shows per page. An unreadable robots.txt is no longer read as Disallow all.

Replaces the robots-per-hop rule in `docs/ACQUISITION.md` and the exhibitor-roster exception to it. Follow-up for the owner: AGENTS.md §4 still says "The site corpus fetcher refuses LinkedIn requests"; the sentence is now stale and is not edited here. The check is `tasks/robots-off-fetch-2026-11-25/check.py`.

## 2026-11-25 · Audit 13 reader rule: an own page counts

Owner ruling 2026-11-25 11:27, "Reader rule: own page counts". The reader rule now reads: "An operator's own page (on its own domain) that names the operator and gives exactly one street at the record's locality speaks for the site at that locality: that street can contradict the site's street. A page that lists several locations at that locality, or labels the address as headquarters or office only, does not; a parent's headquarters street still does not contradict a plant's street."

Reason: smoke attempt 2 was void. A reader marked a planted wrong street UNCONFIRMED under the rule that a company-level page cannot contradict a site value, while the operator's own home-page footer gave the true street at the record's locality, which the Atlas binds from that same page. 6 of the 9 plants had this shape, so wrong streets sourced this way were undetectable.

Follow-up ruling, 2026-11-25, "Simplify: hand-check plants": two automated eligibility checks for this rule, and a `--reject-plants` re-draw option, were refuted in review, so the code is dropped. The controller decides plant eligibility by hand after fetch and before any reading (one address block on the cited source, shown in the reader's excerpt, with a name the record holds or its operator, the true value and the record's locality; the source the operator's own domain or site-specific; no headquarters-only or office-only label). There is no re-draw: a plant the hand-check rejects counts INELIGIBLE and is reported apart from caught and missed (seal rule 5, owner ruling 07:57). Changed files: `tasks/blind-audit-13-smoke-2026-11-24/READER_INSTRUCTIONS.md` and the README only.

## 2026-11-25 · Browser path for bot checks (headed Chrome, no clicks)

Follows the owner rulings of 2026-11-24 21:21 ("Rule change: ignore robots.txt. Click thru bot checks."), 2026-11-24 21:26 ("LinkedIn should not be barred.") and 2026-11-25 06:08 ("Split it": the browser path comes as its own reviewed PR). Evidence: on the merged fetcher (curl only) 0 of 127 PIC-18 LinkedIn company pages and 12 of 117 own-site organizations were readable; a quarantined headed-Chrome run read 122 of 127 LinkedIn pages without a click, and headless Chrome was held by Cloudflare on 3 of 3.

1. A page the curl path calls a bot check is retried once in headed local Chrome (a window opens on the machine). No clicks, no typing: headed Chrome cleared every LinkedIn check without them, and the click findings of the earlier review stay closed by not clicking.
2. Every request the browser makes is checked before it is sent (privacy exclusions, LinkedIn profile refusal, other hosts, robots state, per-host pacing), HTTP redirect hops included. No cookie is ever sent. Only documents load.
3. Bodies of excluded destinations, bot-check pages and error pages are never stored. LinkedIn pages are reduced to the allowlisted extract, as on main.
4. curl failures on the TLS handshake, the certificate chain or HTTP/2 get one retry over HTTP/1.1, with verification on; a chain curl still rejects goes to Chrome. No certificate verification is ever disabled.

The check is `tasks/browser-fetch-2026-11-25/check.py`.

## 2026-11-25 · HTTP/1.1 transport fallback; the two bare-curl runs recorded

The owner's 2026-11-24 ruling ("Rule change: ignore robots.txt. Click thru bot checks.") shipped in #560 without a browser (owner ruling 2026-11-25 06:08, "Split it"). Two runs on the merged fetcher, curl only, are recorded in `docs/ACQUISITION.md` section 3: the 117 PIC-18 organizations with no readable page, of which 12 became readable (7 of 8 real robots disallows, 4 of 98 unreadable robots.txt), and the 127 LinkedIn company pages, of which 0 did (all 127 answered a Cloudflare 403). Most of the 105 still unreadable fail inside curl: certificate chain 27, HTTP/2 or empty reply 28, DNS 11, timeout 7, handshake 5.

1. A curl failure on the TLS handshake, the certificate chain or HTTP/2 (exit 35, 60 or 92), whatever HTTP status curl had read, gets one retry over HTTP/1.1 inside the same transport step (page, redirect hop and robots.txt). Its response, redirects included, is processed like any other. Certificate verification stays on; nothing is ever disabled. Whether the retry recovers any of the 105 is not measured.
2. LinkedIn now runs through Muse with raw evidence on the NAS (the owner, 2026-11-25). The fetcher's LinkedIn company-page path from #560 is unchanged and is not the route for it. A LinkedIn page stays a navigation link only until the evidence route lands.
3. The browser retry for bot checks is a separate change and is not part of this entry.

The check is `tasks/fetch-fallback-2026-11-25/check.py`.

## 2026-11-25 · LinkedIn evidence route (SCHEMA v1.21.0)

Owner ruling 2026-11-24 21:26 (in chat and by multiple choice): "LinkedIn should not be barred." (1) Use: "Full evidence: anything on a LinkedIn company page (About, Specialties, industry, size range, location) counts as evidence" (option 3 of 3; the controller had recommended company-own-words only). (2) Access: "logged out first; measure yield; logging in stays open." It "Reverses owner battery B-LINKEDIN (2026-11-04, navigation link only)" and the AGENTS.md §4 line that the site corpus fetcher refuses LinkedIn requests, kept by the privacy rule (AGENTS.md §6): company pages only, never personal profiles or employee names. Until a binding-gate route landed, LinkedIn values were leads. On 2026-11-25 the owner gave the LinkedIn pull to Muse, whose reviewed package carries raw guest captures on the NAS (the controller replayed 150 of 150 sampled values against them).

This entry is the route. SCHEMA v1.21.0 adds `source_class=linkedin_company`: a logged-out company page, organization grain only, never a site, street, county or child unit; one labelled field per row (industry, specialties, founding year, HQ city, company size) from the subject's own About section; free-text descriptions are held for a reader and never passed by machine. A LinkedIn company size is organization-wide: it can set only the worldwide band `employee_band_global`, never `employee_band_ohio` or a site band, and a bracket sets a band only where it nests in one Atlas band (`5,001-10,000` and `10,001+` are `5000+`; every other bracket sets none). A parent roll-up page, including one whose title normalizes to the child's name, supports nothing for the child. The tier ceiling is proposed as `supports_A`, the same as an own-site page for self-declared facts: **an owner ruling to confirm**, together with admitting `size_band` from this class. The binding gate passes a row only if the row names its capture by sha256 (`notes: capture_sha256: <hex>; acquisition: guest`) and the task's `INPUTS.sha256` names it, the capture is the cited page and not signed in, its title carries a name the record holds and not its parent's, the claimed field of the About section has the claimed value, and the quote holds the field's label and value; no email, phone or person beside a role. Validator V-22 enforces the class, ceiling, grammar and grain. Two further owner rulings of 2026-11-25 narrowed the route: "Exact-field round 3" (the quote is exactly one labelled field as the capture shows it; any sign-in marker refuses the capture; the claimed size bracket equals the capture's and an inverted bracket sets nothing) and "Closed fields, round 4" (the machine reads only the label-line/value-line layout of the About section, never the flattened line; an Industry passes only if it is in LinkedIn's published Industry Codes V2 list, kept in `docs/schema/linkedin_industry_codes_v2.csv`; a size only if it is one of LinkedIn's fixed brackets; Founded only a four-digit year; an HQ city only if it equals the record's own held HQ city; Specialties never by machine, held for reading). Codex alone reviews each of these rounds. Owner ruling 2026-11-25 18:11, "Drop HQ city, merge": every `linkedin_company` `hq_city` row is held for reading (`linkedin_hq_city_needs_reading`), whatever the record holds, because a record's own city can be set in the same PR; the change only removes a pass path, so #567 merged without a further review round. Follow-up for the owner: AGENTS.md §4 still says "The site corpus fetcher refuses LinkedIn requests"; the fetcher has allowed company pages since #560, so the sentence is stale and is not edited here. Checks: `scripts/test_check_evidence_binding.py` (`LinkedInCompanyRoute`) and `scripts/test_validate.py` (`test_v22_linkedin_company_*`).


## 2026-11-25 · Freeze gate scope and review rounds (AGENTS.md §2a rule 4)

Decided by the repo owner in session on 2026-11-25 18:25, by multiple choice: the owner chose all four options. The question put to the owner, as the controller recorded it on its board (a paraphrase, not the owner's words): adopt four lessons from the genealogy controller. (1) Freeze gate scope: a gate or tool PR plants its defect, the gate catches it, then scope freezes; later edge cases are follow-ups unless they corrupt data, publish personal data or let the gate pass what it cannot inspect; this amends AGENTS.md §2a rule 4 and is recorded in DECISIONS.md. (2) Yield per source on the outcome line: rows that moved process, market or size per source and per 1M tokens, and route lanes to the best source. (3) A bounded-negative ledger per owner and field, keeping searched-and-not-found apart from never-looked, checked before any search. (4) An idle stop guard in the controller's Stop hook: refuse an idle stop while a lane waits, unless an expiring idle-ok reason is recorded.

This entry carries item (1) only; items (2) to (4) are controller-side tooling outside the repo. Rule 4 now says: a PR that adds or changes a gate or tool plants the defect it exists to catch and shows the check catching it; once it does, scope freezes, and later edge cases are FOLLOW-UP unless they corrupt data, publish personal data or let the gate pass what it cannot inspect, which stay BLOCKING as the rule already defines. Origin: the Family-History controller's report that gate PRs lose rounds to edge cases after the gate already catches its planted defect; in this repo PR #539 needed four rounds for 15 cells and every refusal concerned a checking script (entry 2026-11-24, "Owner rulings"). Like the rest of rule 4 this is practice: nothing mechanical checks it. No data file is changed.

Second ruling, same day, 19:21, by multiple choice: the owner chose the recommended option, which read "Adopt, same PR". The question put to the owner, as the controller recorded it (a paraphrase, not the owner's words; it came from the genealogy controller's second note): in AGENTS.md §2a rule 4, reviewers' criteria are set before round 1; the builder fixes every BLOCKING finding of a round in one push, each with a planted test; later rounds are a regression check on those tests and the diff; the two-round cap counts rounds on the same evidence; a new kind of finding raised in round 2 or later is FOLLOW-UP unless it corrupts data, publishes personal data or lets a check pass what it could not inspect.

Rule 4 now says the same in its own words (the sentence after the gate-scope freeze), and the revision note of 2026-11-25 carries both rulings with their times. Like the freeze, this is practice: nothing mechanical checks the rounds. No data file is changed.

## 2026-11-25 · Owner rulings 18:16 and 20:12: fix the site names, then close P1

Decided by the repo owner in session on 2026-11-25. Audit 13 smoke attempt 3 stopped at 20 of 40 real records with 2 core-field contradictions, both `site_name`: the site is named for a legal entity or its parent while the operator's own page prints the operating division at that street.

1. **18:16, "Fix site names, then close".** P1 closes on the audit 13 smokes plus a site-name repair pass. **This supersedes the 2026-11-24 20:51 ruling (2), that a clean smoke unlocks the full PIC-18 draw:** there is no full draw; the P1 exit is the smokes plus this repair.
2. **20:12, "Name on the door" (multiple choice, the recommended option).** `site_name` becomes the name the operator's own page prints at that street wherever the held name differs by more than a legal-form word (legal entity, parent, predecessor, brand or division). The old name moves to the site's `notes` (SCHEMA §4.5 has no site `trade_names`; §5.4 keeps former names in `notes` or the organization's `trade_names[]`). A difference of a legal-form word (Inc, LLC, Corp, Co, Company, The) or punctuation only stays. This is how the audit 13 smoke readers scored SITE-001778.

Applied in `tasks/site-name-repair-2026-11-26/`: 6 renames, each with an own-site evidence row that passes the binding gate; the rest of the candidates are held, with the reason for each in that folder's README. The check is `tasks/site-name-repair-2026-11-26/check.py`. No schema or script file changes.

## 2026-11-26 · Gate route for SBA PPP size bands (SCHEMA v1.21.1)

Owner ruling 2026-11-26 07:36, "Gate PR for PPP first" (the controller's option A, recommended). Two earlier rulings the same morning (07:20) stand behind it: re-run the 2026-11-16 PPP size-band pass on current main, and apply the v1.19.7 ten-year age limit to PPP. The re-run was stopped when `scripts/check_evidence_binding.py` returned no PASS for any PPP row: the 248 rows of 2026-11-16 are `no_quote`, a PPP-shaped row with a quote is `unknown_source_family`, and an http source is `READ_REQUIRED web_class_untested` (a proof cannot rescue it).

This entry is the gate route. A labelled `SBA PPP ` family is added to the binding gate for `size_band` claims only (every other use of PPP data stays a lead). The quote carries three fields, `borrower_name`, `business_type` and `address`; the gate FAILS a business type outside the five on the scout's privacy whitelist and holds a quote that does not state one, so a sole proprietor, self-employed or individual borrower never passes; the borrower name must be the operator's own legal, trade or former name (never a site label), the street must equal the record's, the quote must state a city that equals the record's (no city is HELD), and a ZIP5 the record holds must agree. An organization row is judged on its one active site and only where every held site is in Ohio. The `business_type` field is an addition to the quote shape the controller proposed: without it the gate could not inspect the privacy line, and a gate must fail on what it cannot inspect (AGENTS.md section 7). The gate does not read the loan date or the job count; the re-run's own check does. SCHEMA v1.21.1 states the row format and extends the ten-year limit to source 4 in the same revision. The 2026-11-16 row format stays unadmitted, because it has no quote.

## 2026-11-26 · Owner rulings 04:04 and 04:26

Carried here from the SITE-001778 fix, which stopped, so the rulings are on the record in the repo. Three answers at 04:04; the third was replaced at 04:26.

1. The question on the SITE-001778 site-name fix: "Fix in P2, one small PR." The fix was tried on 2026-11-26 and stopped: tensile.com, where the held website redirects, does not print the held name. It waits on the filing name-variant gate route.
2. The question on the eight site names that rest only on a page footer: "Keep them held." There is no footer gate route; those names stay held.
3. The question on the next pilot: "Air-permit pilot first", replaced at 04:26 by "Size-ceiling census". The premise of the question was wrong: the 85 held Ohio air-permit PDFs had already been read by the 2026-11-23 permit lane. The census ran and is recorded in `docs/ACQUISITION.md`. The audit of the #571 market fills, `tasks/linkedin-market-ownsite-2026-11-26/AUDIT.md`, is carried in the same PR.

## 2026-11-26 · Owner rulings: PPP re-run and PPP age

Two answers at 07:20 to multiple-choice questions after the census found 38 size-unknown PIC-18 owners that the 2026-11-16 PPP rule binds today. (1) On what to do first: "PPP now, street route next", that is, re-run the 2026-11-16 PPP pass on current main now and take the street-fill route after. (2) On whether an age limit applies to PPP loans: "Same ten-year rule", that is, the v1.19.7 ten-year limit applies to source 4 as it does to sources 1 and 2. The 07:36 ruling "Gate PR for PPP first" and SCHEMA v1.21.1 are in the entry above; the gate route merged as #572.

Applied in `tasks/ppp-size-bands-rerun-2026-11-26/`: blank bands only, the strict name, street and city rule, the latest qualifying loan per organization and a loan dated on or after 2016-11-26. Every candidate evidence row went through the binding gate; the five it did not pass are dropped and listed with their reasons (ORG-001525 and its site, held by the controller's ruling for a different suite; ORG-001590, SITE-001662 and SITE-001694, a suite on one side only). No suite rule was added to the copied matching logic.

## 2026-11-26 · Owner rulings 08:11, 10:53 and 12:10

Owner rulings of 2026-11-26 at 08:11, 10:53 and 12:10, recorded by the controller from its board. The questions below are the controller's paraphrases; only the words in quotation marks are the owner's answers. The question and option text is on the controller board.

1. **08:11.** On a multi-model review of how the Atlas would be built from scratch (Claude, GPT-6.2 Astra and Gemini 4 Neon), the owner answered "Evidence-bound round", "Me now, alongside PPP" and "Price them, you rule after".
2. **10:53, "One regression-only check".** PR #572 was past its two-round cap (AGENTS.md §2a rule 4), and the owner authorized Codex to recheck only the empty-city fix and its regression tests.
3. **12:10, the outcome of that review.**
   - "Keep the street hold": the Akron first-user note still waits for street fills.
   - "Keep deferred": company confirmation outreach.
   - "Weekly repair batch" and "Strict gate defaults": small repairs go in one weekly PR, with current reviews. After the PPP data PR, filing families get strict defaults, replayed over past verdicts first.
   - "Default list with caps": the controller takes the listed operational choices itself, each capped at 3M tokens and reported daily for the owner's veto. It is a one-week trial, 2026-11-26 to 2026-12-03, and it stops if the owner overrides 3 or more listed defaults. Scope, vocabulary, publication and rule changes stay with the owner.

**Correction to the 07:20 ruling.** The ruling's "street route next" (as the controller recorded it) rested on a stale premise, that the street route was unbuilt. AGENTS.md §2a rule 3 and `docs/ACQUISITION.md` said so, and both were wrong. The gate routes for the map-listing street and the filing name variant were implemented in PR #549 (2026-11-24, `map_listing_result` and `filing_name_variant_bound` in `scripts/check_evidence_binding.py`), and the street route ran in PR #552: 1 of 153 blank PIC-18 streets filled, and 36 note-street agreements held pending a decision on lead forms (`tasks/pic18-map-streets-2026-11-24/README.md`). The 2026-11-24 10:29 entry above says the gate routes come "in later PRs"; that was true when written and stands as history. The PR that adds this entry corrects AGENTS.md §2a rule 3 and `docs/ACQUISITION.md` (the lines naming either route as unbuilt or planned). It amends no rule and changes no data file.
