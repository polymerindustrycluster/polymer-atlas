# Owner rulings of 2026-11-22

The quotations below identify the recorded decision and where to check it. Main refers to `393c3895`. **Ledger only** refers to the controller’s `BOARD.md`; line numbers identify the excerpts. PR and branch references are pinned to the versions inspected for this register.

## Disagreements and differences for the owner

- **Headcount age.** The round 7 ledger says “headcount age limit 5 years.” PR #468’s `DECISIONS.md` and the size-sprint branch give 2021-11-22 as the cutoff. PR #468’s proposed SCHEMA §1 R13 says the cutoff “is not a rolling window: a later ruling moves it by a dated revision.” The record leaves open whether the five-year limit should roll forward. See C3.
- **Review record.** Main’s `DECISIONS.md` explicitly requires comments naming the model family and model. PR #466’s `AGENTS.md` specifies family counts and records at the current head, but the sentence listing comment fields omits “model family.” Its `DECISIONS.md` item 3 also gives a shorter account of tiering. See A2–A3 for both texts.
- **Contact quotes.** Main’s `DECISIONS.md` says the contact detail “may stay in a verbatim quote.” Main’s `AGENTS.md` §6 explicitly requires it to be incidental to a quote that witnesses another claim and lists the narrower bars. See C1 for both texts.
- **Parent names.** The first name-match entry in PR #467 leaves parent names open. The later split entry records the owner’s “fail everywhere” decision, quoted in C6.
- **City matching.** PR #467’s `DECISIONS.md` gives a city-equality requirement and then records the controller’s later locality instruction allowing an equal ZIP5 and treating a missing city as neutral. See A7–A7a for those texts and A7b for the owner’s subsequent strict-floor ruling.
- **Industry codes (settled 2026-11-22, round 12).** The round 11 ledger says “industry codes as a low-tier lead” (D8). The In-Hand lane brief says “owner ruling: fill at a low tier, marked as inferred from a code” and asks for a fill proposal (C10). See G2 for the later ruling.
- **Ohio backfill.** PR #466 freezes national backfill outside PIC-18 “until the PIC-18 unknown shares move” (D2). The later ledger direction says each Ohio route re-runs “when its PIC-18 PR merges (lifts the freeze for Ohio, route by route)” (D3). PR #466’s text does not mention the route-by-route release.
- **Rendered-page tooling.** The round 8 ledger says “switch on the NAS browser for script pages.” The streets branch specifies Firecrawl for rendered pages, tesseract for images and SearXNG for official-page searches. See C8.
- **Street canary yield.** The ledger records 7 of 25 verified on line 2161 and 5 of 25 verified on line 2165. The streets branch’s README reports 3 of 25 under the main-text rule. The full 121-site packet is a separate result cited in F2.

## Review and revert context

Main `DECISIONS.md` records “23 of the 42 PRs, all from `agent/spaghetti/*` branches, were merged before `validate` finished on their head.” The review window covers PRs merged since 2026-11-20 UTC, as reviewed on 2026-11-22. Separately, the revert removed 34,094 evidence rows, 6,837 registry links and 364 archive links from batches 5 and 6. The first binding test returned an explicit FAIL on 9,469 of the 33,916 evidence rows labelled batch 5 or 6, with 206 rows receiving no verdict. Both counts are in main’s `DECISIONS.md` under the corresponding headings cited in A1 and B1.

## A. Merging and review

### A1. Required validation

**Owner ruling** · main, `DECISIONS.md` (“owner rulings on the merge gate, contact data in evidence quotes, and the review record”), item 1 and GitHub ruleset 27269436.

> **No account merges ahead of `validate`.** The repository-admin bypass on the ruleset "main: require validate" was removed on 2026-11-22. GitHub now refuses a merge until `validate` is green on the PR head; open the PR and wait, or use auto-merge.

### A2. Review comments

**Owner ruling** · main, `DECISIONS.md` (“owner rulings on the merge gate, contact data in evidence quotes, and the review record”), item 3.

> Each PR carries one comment per verifier naming its model family and model, its verdict and what it checked.

### A2a. Muse posts verifier verdicts

**Owner ruling** · **ledger only**, `BOARD.md` line 2078. See A3 for the later review tiers and B3 for the later Muse pause.

> Muse posts verifier verdicts on PRs

### A3. Review tier, head, independence and round cap

**Owner ruling** · PR #466 at `bf4d01bb`, `AGENTS.md` §2a rule 4. See also PR #466 at `bf4d01bb`, `DECISIONS.md` (“owner rulings after the process retrospective”), item 3.

> **Review is tiered by risk, recorded on the PR.** *Practice.* (Owner ruling 2026-11-22, "tier by risk".) A PR that changes any file under `data/` gets review records from two model families at the current head; every other PR gets one, from a family other than the builder's. The controller arranges the reviews and posts a `**Review record**` comment per verifier on the PR, naming the model, the verdict at the head SHA and what was checked. A non-data PR is capped at two review rounds; after that the open findings go to the owner. On a later round only the family that refused re-reviews, unless the fix adds a file or changes more than 30 lines. Every finding is marked BLOCKING (a defect that reaches data or users, publishes personal data, lets a check pass on what it could not inspect, or lets CI be defeated) or FOLLOW-UP; follow-ups do not hold a merge and are listed in the PR and on the board; a verdict is REFUTE only when at least one finding is BLOCKING. **Nothing mechanical checks any of this, and the records are self-reported comments on a shared account.**

> **Review is tiered by risk.** Data PRs keep two families. Other PRs take one family and at most two rounds. Findings are marked blocking or follow-up, and follow-ups do not hold a merge.

### A4. Seven working rules

**Owner ruling** · PR #466 at `bf4d01bb`, `AGENTS.md` §2a rules 1–7. Review details in A3, checksum details in E3a.

> **The agent that builds a batch never merges it.**

> **No evidence row or registry link merges without its packet and a replay check in the repo.**

> **A binding gate in CI: the quoted operator is a name the record holds and the quoted street equals the record's street, or the row is a lead.**

> **Review is tiered by risk, recorded on the PR.**

> **A batch is audited before the next one builds on it, with a size cap per PR.**

> **Raw inputs live in the shared store by checksum.**

> **Decisions in `DECISIONS.md`, commitments on the board, chat for messages only.**

> **Rules 1, 4 and 7 are practice: nothing mechanical checks them.**

> People and program rows are held.

> The street test does not apply to people or program rows; those are held, not tested.

> A PR may add at most 1,000 evidence rows and 1,000 registry links unless it adds a line to `DECISIONS.md` that contains the words "size waiver" and `branch=<its complete branch name>` (compared for equality with the PR's branch). A PR that touches `data/` fails while any `created_by` label on `main` lacks an audit record: a file `tasks/<folder>/AUDIT.md` on `main` with the lines `Label:`, `Result: PASS`, `Sample:` and `Reviewers:` (a `Result: FAIL` blocks). The labels on `main` on 2026-11-22 are grandfathered in `tasks/working-rules-2026-11-22/audit_baseline.txt`. **Deployment condition:** the audit stays current for a PR only once the controller has made `pr-rules` a required check and turned on the ruleset's strict (branch up to date with `main`) policy; until then two data PRs can both pass against the same `main`.

### A5. Comment checker and GitHub accounts

**Owner ruling** · PR #466 at `bf4d01bb`, `DECISIONS.md` (“owner rulings after the process retrospective”), item 4. This supersedes the round 6 direction to keep the comment-reading checker (`BOARD.md` line 2143).

> keep the #466 checker (no GitHub machine accounts now);

> **The comment-reading review check was dropped** after two review rounds found it could not be made sound; the rest of the checker stays (PR #466): size cap, audit record, INPUTS.sha256, and the binding-gate job. Review stays practice, and separate GitHub accounts for builders and reviewers are not created now.

### A6. Structured gate and separate web proofs

**Owner ruling** · PR #467 at `8bfea6b0`, `DECISIONS.md` (“owner ruling, evidence binding gate split”). Web follow-up design in Branch `agent/claude-code/evidence-binding-web-proofs-2026-11-22` at `9f06632f`, `tasks/evidence-binding-web-proofs-2026-11-22/README.md`.

> #467 is the binding gate for structured rows only. A web row is FAIL or READ_REQUIRED, and a READ_REQUIRED or UNINSPECTABLE row fails the PR; admission of web rows by per-row proof (proof files, readings, archive fetching) moves to branch `agent/claude-code/evidence-binding-web-proofs-2026-11-22`. Provenance is presence only: a `created_by` label's folder holds a non-empty `check.py`, and the gate executes nothing from the tree it gates; the lane and the reviewing family run the replay. This supersedes the controller's earlier rulings C, the execution part of E, and the proof/reading design for #467.

> `tasks/<folder>/BINDING_PROOF.csv` proof lines, each with a cross-family reading;

### A6a. Per-row proof replaces sample admission

**Controller ruling** · **ledger only**, `BOARD.md` line 2139

> GATE RULING REVISED after Astra's retrospective point: uninspectable rows are admitted only by a per-row proof record (capture ref, sha256, quote offset), never by a sample; sampling becomes an audit mode only.

### A7. Units and locality in the structured gate

**Owner ruling** · PR #467 at `8bfea6b0`, `DECISIONS.md` (“owner ruling, evidence binding gate split”, rules added to #467).

> for a structured site row the quoted city and state must equal the record's (state read with or without a ZIP; a city conflict is a FAIL); a suite, unit or building stated on both sides must agree, in dotted and abbreviated forms, in the shared `scripts/matching.py` test (the last-activity derivation is unchanged on all 7,196 sites).

### A7a. Parenthetical locality and ZIP5

**Controller ruling** · PR #467 at `8bfea6b0`, `DECISIONS.md` (locality bullet in the split entry).

> same state, and the quoted city is a spelling of the record's city or of either part of a parenthetical city, or the two ZIP5 values are equal; otherwise `city_differs`. A missing city on either side is not contrary evidence, and a quoted other state stays `state_differs`. This loosens the city half of the rule above (Codex r2 finding 2) by the ZIP5 leg.

### A7b. Strict floor and merge condition

**Owner ruling** · **ledger only**, `BOARD.md` line 2226. Later ruling on PR #467.

> strict floor, then merge: PASS only when every leg matches positively and nothing in the quote is unexplained; else held for reading; Codex confirms its counterexamples fail and stops; gate documented as a floor, not proof.

### A7c. Canonical street matcher

**Controller ruling** · **ledger only**, `BOARD.md` line 2233.

> the repo's street matcher is the canonical one: scripts/atlas.py street_key today, scripts/matching.py once PR #467 merges. The gate, the last-activity derivation and the labelled test set use it. Muse's pull-code street function is not used for anything that reaches the repo; its 402 disagreements with the repo's function (of 5,083 batch-5 pairs, Muse's count) are to be read and added to the labelled test set.

## B. Reverted batches and Muse

### B1. Whole-batch revert and restoration

**Owner ruling** · main, `DECISIONS.md` (“owner ruling, batches 5 and 6 reverted”). Failed rows as leads and the superseded narrower order are also recorded in the ledger (rounds 2–3).

> burn-down batches 5 (PR #457) and 6 (PR #458) are taken off `main` whole: 34,094 evidence rows (33,916 labelled batch 5 or 6, and 178 QC-1 cured backfill rows labelled burn-down batch 1 or 2 that arrived in PR #457; the 39 recapture rows that arrived in PR #455 are not removed), 6,837 registry links and 364 archive links.

> a removed row that later passes the binding gate and a replay against the raw source file returns under its original evidence ID in a new, reviewed PR.

> remove the different-street OSHA rows in one PR, built by Claude Code;

> failed rows kept as leads. Supersedes the 844-row removal.

### B2. Last activity at the site’s own street

**Owner ruling** · main, `tasks/last-activity-street-leg-2026-11-22/README.md` (#463), opening and “Counts”; `docs/SCHEMA.md` §4.5, `last_activity_source`.

> **Owner ruling 2026-11-22 (multiple choice): "Fix script, re-derive."**

> Only tier-A (name + street) matches feed the derivation — a derived record field never rests on a name/city-only match.

### B3. Muse pauses minting and integration

**Owner ruling** · main, `DECISIONS.md` (“owner rulings on SAM extract evidence, the Muse pause and batch 7”), item 2.

> **Muse pauses minting and integration.** Until the owner lifts this, Muse opens no data PR and mints nothing. It continues downloads and the archive copy, and may do read-only work: publishing its join code and match rules, and triaging its own flagged rows without editing them.

### B4. Batch 7 stays in draft

**Owner ruling** · main, `DECISIONS.md` (“owner rulings on SAM extract evidence, the Muse pause and batch 7”), item 3.

> **Batch 7 (PR #459) stays in draft** until its joins are checked the way batch 5's were.

### B5. Muse login, inbox and NAS setup handoff

**Owner ruling** · **ledger only**, `BOARD.md` line 2117

> Muse gets no Kaneo login; atlas-store with Muse inbox + controller ingest; controller prepares, owner applies

### B6. Git history, November 19 carryover

**Owner ruling** · **ledger only**, `BOARD.md` line 2075

> merge #416 and #417 despite Codex REFUTE at cap; leave git history (scrub forward only); archive clerks.

## C. What may count as evidence

### C1. Contact details incidental to evidence quotes

**Owner ruling** · main, `AGENTS.md` §6 and main, `DECISIONS.md` (“owner rulings on the merge gate, contact data in evidence quotes, and the review record”), item 2.

> Evidence quotes are the one exception, and it is narrow (owner ruling 2026-11-22): where a verbatim quote that witnesses another claim incidentally shows a company's public switchboard phone or fax number or a role address (info@, sales@), the quote may keep it. A quote is never a place to record contact data, and every narrower bar stands: exhibitor contact blocks are never transcribed (SCHEMA §4.12), an ecosystem office carries its generic contact page and never an office phone number (§4.6), and equipment records carry no contact data (§4.19). A quote never carries an individual's email, a direct line, an extension, a mobile number, or a home address — cut the quote before it.

> A company's public switchboard phone or fax number and a role address may stay in a verbatim quote. An individual's email, a direct line, an extension or a mobile number may not: cut the quote before it. AGENTS.md section 6 carries the sentence. Rows already in `data/evidence_*.csv` are not edited (evidence is append-only); the rows that may hold an individual's detail are being triaged, and their remedy returns to the owner.

### C2. Public SAM extract and filter

**Owner ruling** · main, `DECISIONS.md` (“owner rulings on SAM extract evidence, the Muse pause and batch 7”), item 1.

> **The public SAM.gov entity extract may be quoted as evidence.** This lifts, for the public extract only, the 2026-11-16 R-SAM bar on copying a SAM name or address into the Atlas (`tasks/owner-rulings-2026-11-16/README.md`). The R-SAM filter stays: a record marked D&B-sourced, or last updated before 2022-04-04, is not quoted (D&B is a licensed source under AGENTS.md section 5). SAM API responses were not addressed and stay under R-SAM. A batch that quotes the extract shows that its rows pass the filter.

### C3. Headcount source age

**Owner ruling** · PR #468 at `a55f7d93`, `DECISIONS.md` (“owner rulings for the PIC-18 size sprint”), item 1, and PR #468, `docs/SCHEMA.md` §1 R13. Also branch `agent/claude-code/pic18-size-sprint-2026-11-22` at `db44edb6`, `DECISIONS.md`, item 1. See the disagreement above.

> headcount age limit 5 years

> **Headcount age: 5 years.** A filing sets a band only if its source date (ITA: the filing year's period end, 31 December; inspection: open date; Form 5500: plan year end) is on or after 2021-11-22. Older filings are held as leads with the reason `stale_over_5_years`.

> A filing sets a band under sources 1 to 3 only if its source date is on or after 2021-11-22: for ITA 300A, the end of the filing year (31 December); for an OSHA inspection, its open date; for Form 5500, the plan-year end. An older filing is a lead only and never sets a band; the integrator records it as held with the reason `stale_over_5_years`. The cutoff is five years before the ruling and is not a rolling window: a later ruling moves it by a dated revision. It applies to the evidence behind a band, not to bands already in the data.

### C4. Corporate-form name extensions after a street match

**Owner ruling** · PR #467 at `8bfea6b0`, `DECISIONS.md` (“name match on structured rows when the street matches”) and PR #468 at `a55f7d93`, `DECISIONS.md` (“owner rulings for the PIC-18 size sprint”), item 2. The same size-sprint text is on branch `agent/claude-code/pic18-size-sprint-2026-11-22` at `db44edb6`, `DECISIONS.md`.

> in the evidence binding gate, a structured-source site row whose street already passes the shared street test (`scripts/matching.py` `same_street()`) also binds on its name when the quoted filing or permit name equals a name the record holds, or when a held name is a leading run of it and every extra token is a corporate-form word from this fixed list: Inc, Incorporated, LLC, L.L.C., Corp, Corporation, Co, Company, Ltd, Limited, LP, LLP, Holdings, Holding, Group, US, USA, U.S., North America, Americas. Any other extra word stays FAIL `name_not_held` ("Acme Polymer Services" fails; the fleet-services affiliate on EVD-455899 fails). The rule lives in `scripts/matching.py` (`corporate_form_extension`).

> **Scope:** it does not apply to web rows, to organization rows without a street test, or to predecessor, parent or notes-only names; those questions stay open.

> **Name match when the street already matches: corporate words only.** The held name may be a leading run of the filing name when every extra token is a corporate-form word from this fixed list: Inc, Incorporated, LLC, L.L.C., Corp, Corporation, Co, Company, Ltd, Limited, LP, LLP, Holdings, Holding, Group, US, USA, U.S., North America, Americas. Anything else (Services, Logistics, a place name, another business word) stays held. Containment of one name in the other is not accepted.

### C5. Generic site-name parts

**Owner ruling** · PR #467 at `8bfea6b0`, `DECISIONS.md` (site-name parts bullet in the split entry).

> a site-name part is ignored as a held name only when every token in it is a generic label: plant, facility, warehouse, works, site, office, HQ, headquarters, building, unit, main ("main" added by the owner the same day, relayed by the controller; it changes no row: no site key on the tree is generic only because of it); a number or ordinal; a compass word; a US state; or the site's own city or county. Any other part (a brand, a division, a trading name) counts as a held name. The list is one fixed list in `scripts/matching.py` (`GENERIC_LABELS`). A permit naming only "Plant 2" or only the city fails.

### C6. Parent name on any machine path

**Owner ruling** · PR #467 at `8bfea6b0`, `DECISIONS.md` (parent names bullet in the split entry).

> a filing that names only a recorded parent or ultimate parent (or that name plus corporate-form words) never binds a subsidiary's record by machine, on any path, including when the parent's name is part of the site name. It fails with reason `parent_name_lead`, a lead to be read.

### C7. Archived company page for a street

**Owner ruling** · Branch `agent/claude-code/pic18-streets-2026-11-22` at `e4424601`, `DECISIONS.md` (“owner rulings, sources for a street address”), item 1.

> "A Wayback Machine capture of the company's own page counts as the company's own page for a street address when the capture is dated on or after 2024-11-22 (within two years). Cite the archive URL, record the capture date as the observed date, and mark the row source_route=archived_copy. An older capture is a lead only (hold reason archived_copy_over_2_years). Use it only when the live site cannot be read; if the live site is readable, the live page governs."

### C8. Rendered pages, address images and official page search

**Owner ruling** · Branch `agent/claude-code/pic18-streets-2026-11-22` at `e4424601`, `DECISIONS.md` (“owner rulings, sources for a street address”), items 2–4. Round 8 wording also in `BOARD.md` line 2167.

> switch on the NAS browser for script pages, reading address images (flagged, second-model reading), a search for an official page

> For a page that is thin because scripts build it, load it through the Firecrawl tools (markdown, onlyMainContent). It obeys robots.txt and is never used to get past a block, a login or a CAPTCHA. Mark source_route=rendered.

> Where the address is an image on the company's own page, download it from the same domain, read it with tesseract and record the text. Such a row is never VERIFIED by the lane that read it: source_route=image_text, verdict STILL_UNCERTAIN, settling fact "second-model reading of the image", the image's sha256 kept; no person's name, email or phone transcribed from an image.

> For a site still without a street, at most three SearXNG searches may find another public page that states the plant's address (a state or federal agency page, a county or city economic-development or permit page, the company's own page on another of its domains); that page is fetched and quoted; never cite the search result, a map service, a people-search site or a paid directory. Mark source_route=official_page and name the publisher.

### C8a. Main text, failed captures and fetcher identity

**Controller ruling** · Branch `agent/claude-code/pic18-streets-2026-11-22` at `e4424601`, `DECISIONS.md` (“owner rulings, sources for a street address”), controller rulings bullet.

> quotes come from main text only (navigation, header, footer excluded); a page whose Wayback save fails twice is held (`archive_unavailable`); no second user-agent (the fetcher forces HTTP/1.1 on a transport failure).

### C9. Two agreeing government sources for the street trial

**Owner ruling** · **ledger only**, `BOARD.md` line 2167

> a 25-site trial of government files as a street source (two agreeing source families required).

### C10. Industry-code route and packet conditions

**Controller implementation of the owner ruling in D8** · **ledger only**, `BOARD.md` line 2209; lane instructions in the controller’s `briefs/w1122/process-inhand.md`, Part B.

**2026-11-22, round 12.** The owner superseded the code-derived fill proposal below. See G2.

> pursue process via Ohio air permits, industry codes as a low-tier lead, and reading material already held (not the company form);

> Part B: industry codes as a lead (owner ruling: fill at a low tier, marked as inferred from a code)

> Write the code-to-process table explicitly (code, title, process term, why it is one-to-one) and list the codes you reject as too broad (for example a general "all other plastics product" code maps to no single process). Keep it short and conservative; the table itself is what the owner approved in principle and will want to see.

> Only a code filed BY the establishment in a government filing matched on street and held name counts (NAICS provenance per AGENTS section 4: `government_filing`); a directory code never does.

> The fill is marked as inferred from a code: propose exactly how (which field or evidence claim carries "inferred from NAICS <code> on <filing>", which tier_effect), reading SCHEMA 3.1, 4.13 and the processes field rules, and whether the schema needs a dated sentence to allow it. If it does, write the proposed sentence and tell the controller before applying anything: schema wording is the owner's.

## D. Work commissioned and release conditions

### D1. PIC-18 unknowns pilot, spot-check and cleanup

**Owner ruling** · **ledger only**, `BOARD.md` line 2078

> start PIC-18 unknowns pilot + Codex spot-check + cleanup PR.

### D1a. Size sprint and 25-organization live-site process and market trial

**Owner ruling** · PR #466 at `bf4d01bb`, `DECISIONS.md` (“owner rulings after the process retrospective”), item 1 (round 6).

> **Outcome first.** The next data work is a PIC-18 size sprint from files already pulled (OSHA headcounts and Form 5500 for single-site organizations) and a 25-organization live-site trial for process and markets, each as a packet through the binding gate.

### D1b. Street lane for the 121 size-frame sites without streets

**Owner ruling** · Branch `agent/claude-code/pic18-streets-2026-11-22` at `e4424601`, `tasks/pic18-streets-2026-11-22/README.md`, opening and “Frame”. Commission also in `BOARD.md` line 2153.

> Owner pick 2026-11-22 ("Yes, those 121").

> start a street lane for the 121.

### D2. PIC-18-first backfill freeze and exemptions

**Owner ruling** · PR #466 at `bf4d01bb`, `DECISIONS.md` (“owner rulings after the process retrospective”), item 2; PR #466 at `bf4d01bb`, `AGENTS.md` §2a rule 5 (“Standing freeze”).

> **National evidence backfill is frozen** outside PIC-18 until the PIC-18 unknown shares move. Repairs, re-admission of reverted rows that answer a PIC-18 question, and the whole-Atlas audit are exempt.

### D3. Rest of Ohio, route by route

**Owner ruling** · **ledger only**, `BOARD.md` line 2202

> roll into the rest of Ohio when PIC-18 is done. Each route re-runs on Ohio outside PIC-18 when its PIC-18 PR merges (lifts the freeze for Ohio, route by route).

### D4. Open the size packet PR before the gate

**Owner ruling** · **ledger only**, `BOARD.md` line 2198 (instruction); implementing packet in PR #468 at `a55f7d93`, `tasks/pic18-size-sprint-2026-11-22/README.md`.

> "Open the size pr". Size lane told to apply the 98 bands (95 orgs) on a clean branch and open the PR now (EVD-481000..481199 reserved); two-family review to follow. Supersedes gate-first sequencing for this packet only.

### D5. Form 5500 organization packet cut

**Owner ruling** · PR #464 at `da65a06c`, `tasks/evidence-form5500-orgs-2026-11-20/README.md`, opening.

> keep the rows for organizations that still have no evidence row, plus the lane's liveness rows; drop the rest.

### D6. Audit the whole Atlas

**Owner ruling** · **ledger only**, `BOARD.md` line 2102

> audit the WHOLE Atlas;

### D7. Activity-date and EPA identifier release conditions

**Owner ruling** · **ledger only**, `BOARD.md` line 2201.

> "Yes queue them": two board cards added behind the evidence lane: activity dates for the 122 PIC-18 sites with parenthetical city text (after #467 merges), and EPA identifiers for PIC-18 sites by exact facility match (after the evidence canary).

### D7a. Activity-date diagnosis corrected

**Controller correction** · **ledger only**, `BOARD.md` line 2219.

> CORRECTION: the '122 PIC-18 sites miss last_activity_date because of parenthetical city text' claim (source-map lane, repeated by the controller to the owner) is withdrawn: city text is equal for 114 of 122; 97 need the OSHA extract rebuilt from the full files in the lake. Card ATLAS-23 rescoped.

### D7b. NAS evidence enrichment and canary

**Owner question and controller implementation** · **ledger only**, `BOARD.md` line 2199.

> OWNER asked when the NAS files can enrich Ohio and the evidence queue.

> Lane spawned: pic18-evidence (Sonnet): PIC-18 queue from the lake, one witness per missing claim, canary of 25 first, EVD-482000..482999 reserved. Ohio outside PIC-18 held by the freeze until the unknowns move.

### D8. Process work routes

**Owner ruling** · **ledger only**, `BOARD.md` line 2209

> pursue process via Ohio air permits, industry codes as a low-tier lead, and reading material already held (not the company form);

**2026-11-22, round 12.** Owner ruling, **ledger only**, `BOARD.md` line 2241, item 2. See G2.

> This settles the earlier pick "industry codes as a low-tier lead" as leads only, no fills.

### D9. Pipeline history in public notes

**Owner ruling** · **ledger only**, `BOARD.md` line 2209

> move pipeline history out of public notes;

### D10. Three consistency fixes

**Owner ruling** · **ledger only**, `BOARD.md` line 2209

> do all three consistency fixes (company type from name, company-plant agreement, region labels);

### D11. Regional totals and verification split

**Owner ruling** · **ledger only**, `BOARD.md` line 2209

> totals count unverified sites and show the split.

### D11a. Existing prospect filter

**Existing publication rule** · main, `docs/SITE_HOWTO.md`, “What it produces”, prospects row.

> PIC-18 prospects: one row per organization row with an active tier A-C site row in a PIC-18 county.

### D12. Schema v1.19 battery

**Owner ruling** · main, `docs/SCHEMA.md`, revision history, v1.19 (#456).

> owner ruling 2026-11-22, “I mean let’s add them all to the schema, why not” — battery candidates S-1…S-6, all six).** (1) **§4.8 identifier extension (S-1/S-3/S-4/S-5).** The registry enum gains `RCRA_EPA_ID`, `NPDES_PERMIT_ID`, `STATE_ENTITY_ID`, and `USDOT`, and the minting doctrine for `FRS` (ECHO/FRS program files, exact facility match or program-ID crosswalk, facility grain), `LEI` (GLEIF exact), and `SEC_CIK` (EDGAR exact) is codified; `STATE_ENTITY_ID` and `USDOT` are identity-only and may never support an address claim. **No identifier rows are minted by this revision** — minting rides the wave-1 join batches. Validator V-6: enum extended, facility grain extended to the two EPA permit-grain types, ID shapes for USDOT / RCRA_EPA_ID / NPDES_PERMIT_ID. (2) **Address roles (S-2).** §4.13 evidence gains a trailing `address_role` column (`physical` / `mailing` / `agent` / `registered_office`; empty = unspecified — the value on all 47,377 pre-existing rows) and the same-role ADDRESS_DIFF rule: a contradiction fires only between witnesses of the same role; cross-role differences are recorded, not contradictions. Validator V-22: field set extended; a present role must be in the vocabulary, and a role on a non-address claim warns. (3) **Derived site activity (S-6).** §4.5 sites gain `last_activity_date` / `last_activity_source`, a derived pair written only by `scripts/derive_last_activity.py` (never hand-edited), initially populated from the 2026-11-21 OSHA bulk extracts — tier-A matches only: 3,746 of 7,196 sites (1,357 `osha_inspection`, 2,389 `osha_ita`); tier-B matches (2,264 extract rows) are excluded by design. Year-precision witnesses contribute the filing year's period end (Dec 31) under the convention stated in §4.5; absence asserts nothing. Validator V-5: the pair is set together or not at all, the date is ISO, the source is in the vocabulary. `docs/schema/vocab.json` regenerated. No record, claim, or tier changes.

## E. Coordination, source access and tools

### E1. Tracker and claim ledger

**Owner ruling** · PR #466 at `bf4d01bb`, `AGENTS.md`, “Start here” (“Where things live”) and §2a rule 7.

> `tasks/QUEUE.md` is the claim ledger, the line you mark `claimed:` before you build. The board is the tracker: commitments live in Kaneo, PIC workspace, project ATLAS (the repo's declared tracker from 2026-11-22). Decisions live in `DECISIONS.md`. Chat (the crosswalk `polymeratlas`) is for messages only: a decision or a commitment that exists only in chat does not exist.

### E2. Participants in the private crosswalk

**Owner ruling** · **ledger only**, `BOARD.md` line 2104

> dedicated crosswalk (created: polymeratlas, kept to Claude Code, Muse, Gemini, ChatGPT; charter pinned);

### E3. Shared read-only raw store

**Owner ruling** · **ledger only**, `BOARD.md` line 2104.

> shared read-only raw store on the NAS

> owner creates the share

### E3a. Raw-input checksums and manifest format

**Owner ruling** · PR #466 at `bf4d01bb`, `AGENTS.md` §2a rule 6.

> **Raw inputs live in the shared store by checksum.** *Checked, format only,* by `scripts/check_pr_rules.py`: a PR adding evidence rows or registry links adds `tasks/<folder>/INPUTS.sha256` (lines of `<sha256> <path>`; the path is a file below `raw/` or `provenance/`, or an existing repo file). The hashes themselves are checked by a reviewer against the store; the check says so in its output.

### E3b. DuckDB and the Parquet layer

**Controller implementation of an owner direction** · **ledger only**, `BOARD.md` line 2171

> OWNER asked for DuckDB done correctly: source-map lane told to build a Parquet lake in atlas-store/lake/2026-11-22 (one row per source record, keys from the repo's matcher, manifest reconciling counts, views.sql).

### E3c. All Muse databases and the private staging boundary

**Owner ruling** · **ledger only**, `BOARD.md` line 2168. Publication of membership is governed by main, `AGENTS.md` §5.1.

> factor in all the databases Muse pulled.

> contains crm-crossref, crm-export and pic-member-list folders: PRIVATE, never to enter atlas-store or any lane.

> a record may carry the public membership flag only for a member **findable on the public PIC website member list**, and the record's `sources` cite that public list. The PIC CRM is a private, internal system: it may be used to reconcile the website list against the Atlas internally, but it is never the cited source for a membership fact — nor for any other fact in any public row, and no public row names CRM content (owner ruling 2026-11-01; validator V-50) — and no membership information that exists only in the CRM is published. Where the website list and the CRM disagree, the website governs what publishes and the discrepancy is an internal reconciliation item, not a publishable fact.

### E4. Lighter startup, handoff and Opus routing

**Owner ruling** · PR #466 at `bf4d01bb`, `DECISIONS.md` (“owner rulings after the process retrospective”), item 5.

> **Lighter running.** Mandatory startup reading is cut to one short page; a preflight command and generated counts precede review; the controller hands off to a fresh thread each wave; Opus is used only when the owner asks.

### E4a. Use GPT-6.2 Sol where appropriate

**Owner ruling** · **ledger only**, `BOARD.md` line 2217

> use GPT-6.2 Sol agents where appropriate to save Anthropic usage.

### E4b. Gemini 4 Neon for the retrospective

**Owner direction for the retrospective** · **ledger only**, `BOARD.md` line 2136.

> Gemini 4 Neon, owner asked for it by name; guard accepts Neon only with OWNER-APPROVED-NEON

### E5. Labelled set first and five tooling trials

**Owner ruling** · **ledger only**, `BOARD.md` line 2177

> trial both decision models (OpenAI Decisions API on GPT-6 Luna; TypeSafe Jev) on labelled rows; build a labelled test set first; trial usaddress, Splink and trafilatura/extruct.

### E5a. Decision-model pilot key location

**Owner ruling** · **ledger only**, `BOARD.md` line 2192

> keys for the decision-model pilots should be in the env on the NAS.

### E6. Make the decisions durable

**Owner ruling** · **ledger only**, `BOARD.md` line 2212

> "make sure these decisions and changes are all durable; upset we didn't catch this sooner"

## F. Trial results and measurements

### F1. Government-file street trial

**Trial result** · Branch `agent/claude-code/pic18-size-sprint-2026-11-22` at `db44edb6`, `tasks/pic18-street-from-filings-2026-11-22/README.md`, “Numbers”; disposition **ledger only**, `BOARD.md` line 2176.

> Yield: 1 proposal of 25 (4%).

> Yield 4%: route parked.

### F2. Full site-street packet

**Trial result** · Branch `agent/claude-code/pic18-streets-2026-11-22` at `e4424601`, `tasks/pic18-streets-2026-11-22/README.md`, “Result”.

> **Streets VERIFIED: 8 of 121 (6.6%; 95% Wilson 3.4%-12.6%).** Canary: 3 of 25 under the main-text rule.

### F3. Matcher trials and decision models

**Trial result** · **ledger only**, `BOARD.md` line 2197

> usaddress, Splink: drop (Splink name triage only). Jev jev-1.14.0 at 0.7: street 0/423 FA, recall 13/16 vs baseline 7/16; name 3/46 FA and order-sensitive (6/16 flips); $0.02 per 1,000 requests. OpenAI not run (no key). Trafilatura's main text carries other-place names on 7/8 wrong-place sites.

### F4. PIC-18 outcome baseline

**Measurement** · **ledger only**, `BOARD.md` lines 2077 and 2196. The denominator is 794 PIC-18 organization rows. Unknowns in process, market and size order.

> outcome number unchanged (794; 40.6/39.8/55.8%).

> Outcome number unchanged (322/316/443).

## Round 1 review findings

| Finding | What changed |
| --- | --- |
| 1 | A2–A3 quote current-head data reviews, independent family for other PRs, the later-round exception and finding severity. |
| 2 | C1–C2 quote incidental contact detail, narrower privacy bars and proof that the SAM batch passed the filter. |
| 3 | C4–C6 quote the full lists, the structured-site street test and the parent exclusion on every path. |
| 4 | C7–C8a quote live-page priority and archive citation requirements, and attribute the user-agent instruction to the controller. |
| 5 | D1–D1b record the pilot and cleanup, the size and web trials and the 121-site street lane. F4 locates the denominator in the ledger. |
| 6 | D7 records the 122-site activity-date frame and the PIC-18 EPA identifier scope with their distinct release conditions. |
| 7 | D11–D11a cite the new totals ruling and the existing prospect filter separately. |
| 8 | B5 and E2–E3b record who can participate, who prepares and applies setup, what triggers checksums and where the Parquet direction lives. |
| 9 | E3c records the all-databases direction, the private staging boundary and the membership publication rule. |
| 10 | E4–E4a quote the Opus restriction and the later Sol direction by name. |
| 11 | E5 and F3 separate the full trial commission from its results, including Splink’s retained use for name triage and which decision model ran. |
| 12 | The new `DECISIONS.md` entry cites §2a rule 7 in PR #466. |
| Follow-up | The introduction gives the review window and the PR denominator independently of reverted row and link totals. |

## Round 2 review findings

| Finding | What changed |
| --- | --- |
| Blocking 1 | A2a quotes the owner’s Muse verifier-posting direction and points to the later review and pause rulings. |
| Blocking 2 | C10 quotes the complete instructions on documenting a code-derived fill proposal and escalating schema wording before application. |
| Follow-up 1 | The city-matching note points to both A7 and A7a. |
| Follow-up 2 | The disagreements list compares D8 with C10 on industry-code use and D2 with D3 on release of Ohio backfill. |
| Follow-up 3 | E4b records the retrospective model request, D7b records the NAS enrichment question and canary, and B6 quotes all three November 19 actions. |
| Follow-up 4 | A4 quotes the rules 2–3 exclusion for people and program rows. |
| Follow-up 5 | C8 quotes the ledger’s NAS-browser wording alongside the streets branch’s tooling instructions. |

## G. Round 12 and consistency follow-through

### G1. Process named in permit equipment descriptions

**Owner ruling** · **ledger only**, `BOARD.md` line 2241, item 1.

> a permit's equipment description may fill the process field when it names a process in the vocabulary, for that site only; general equipment (mixer, blender, paint booth) fills nothing.

### G2. Industry codes stay leads

**Owner ruling** · **ledger only**, `BOARD.md` line 2241, item 2. The rule cited there is in main, `docs/SCHEMA.md` §2.4.

> SCHEMA 2.4 stands: no process is filled from an industry code; codes stay leads. This settles the earlier pick "industry codes as a low-tier lead" as leads only, no fills.

### G3. Form 5500 mailing-address evidence

**Owner ruling** · **ledger only**, `BOARD.md` line 2241, item 3.

> A Form 5500 mailing address proves existence and city only: a filing under the company's legal name with a mailing address in its headquarters city shows the company exists there; it never proves a street or a plant location and the street line is not published; a size band still needs the mailing street to equal the single site's recorded street.

### G4. Company confirmation form

**Owner ruling** · **ledger only**, `BOARD.md` line 2241, item 4.

> The company "confirm your record" form: not now.

### G5. Region labels go first

**Controller ruling** · **ledger only**, `BOARD.md` line 2232. Implementation in PR #470 at `d8854e88`, `tasks/region-labels-2026-11-22/README.md`.

> region labels 312 PIC-18 relabels to ne_ohio (GO, PR to open first);

### G6. Company-type fill waits for PR #470

**Controller ruling** · **ledger only**, `BOARD.md` lines 2232 and 2240.

> Entity-type HELD until #470 merges;

### G7. Company-and-plant agreement held

**Controller ruling** · **ledger only**, `BOARD.md` line 2232. Governing text in main, `docs/SCHEMA.md` §4.4, `processes[]` / `materials[]` / `markets_served[]` row.

> company-plant agreement 435 orgs / 796 cells HELD: SCHEMA 4.4 says do not backfill site to parent, which contradicts the owner's pick: needs a dated revision and a tier ruling.

> Parent = union of sites, but do not backfill a site's process to Parent unless Parent claims it corporately — note in field source
