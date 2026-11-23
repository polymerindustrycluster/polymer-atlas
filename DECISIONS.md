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
- **City and locality (controller rulings 2026-11-22, within the owner's standard; not owner rulings):** first, a quoted city other than the record's is a FAIL (`city_differs`). Then, after the source-map lane reported site cities written with a second locality in parentheses ("Cleveland (Solon)"), the locality test moved to `scripts/matching.py`: same state, and the quoted city is a spelling of the record's city or of either part of a parenthetical city, or the two ZIP5 values are equal; otherwise `city_differs`. A missing city on either side is not contrary evidence, and a quoted other state stays `state_differs`. The ZIP5 leg loosens the first controller ruling. It stands only if Codex's read of 40 of the 140 rows it newly passes finds no different place; one different place and the ZIP5 leg comes out. Of the 324 batch rows that carried `city_differs`, 278 lose it on an equal ZIP5 (140 become PASS) and 46 keep it; the parenthetical leg changed none, because the gate already read both parts. The last-activity derivation is unchanged; what it would change is measured in `tasks/evidence-binding-gate-2026-11-22/locality_followup.py` as an owner/schema question (tier-B rows are excluded by SCHEMA §4.5).
- **Effect on the quarantined batches 5/6 (34,094 rows):** 20,705 PASS (round two: 20,749). The 44 round-two PASS rows that now fail: 24 name only a recorded parent, 12 quote another city with another or no readable ZIP, 4 state another suite, 4 name only a generic label. No row quotes another state. Measured against the 1,098 rows the stricter site-name reading failed, the same comparison now counts 1,104 (6 rows that both readings failed on the city pass the round-two reading after the ZIP5 leg): 1,086 pass and the same 18 still fail.
- **Decided by:** the repo owner, in session, 2026-11-22, as multiple choice (the split, site-name parts, parent names); the city and locality bullet records the controller's rulings of the same day.
