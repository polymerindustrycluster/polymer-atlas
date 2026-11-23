# Owner rulings of 2026-11-22: the register

Every ruling the repo owner made in session on 2026-11-22, in one place. A ruling takes effect when it is made, not when the pull request that implements it merges. Each was put as a multiple-choice question unless marked "said". The "Where it lives" column says whether the ruling is already carried by a file on `main`, or only by an open pull request or a branch at the time of writing; this file is what makes the second kind durable. `DECISIONS.md` holds the reasons for the first three groups and points here for the rest.

Why there are so many: on 2026-11-21 and 22 two integration batches put 34,094 machine-joined evidence rows and 6,837 registry links on `main` in one day, most merged before the required check finished. A binding test found that about a third did not belong to the record they were attached to. Nothing running at the time checked whether a quote was about its record.

## A. Merging and review

| # | Ruling | Where it lives |
|---|---|---|
| A1 | No account merges before `validate` is green. The admin bypass on the ruleset "main: require validate" was removed. | GitHub ruleset; `DECISIONS.md` (PR #460) |
| A2 | Every PR carries a comment per verifier: model family and model, verdict, what was checked. | `DECISIONS.md` (PR #460) |
| A3 | Review is tiered. A PR that changes `data/` gets two model families. Any other PR gets one family and at most two rounds; then open findings go to the owner. On a later round only the family that refused re-reviews. Findings are BLOCKING or FOLLOW-UP, and follow-ups do not hold a merge. | Open PR #466 |
| A4 | Seven working rules adopted: the builder never merges; no evidence row or link merges without its packet and a replay check; a binding gate in CI; two families on data PRs, recorded; a batch is audited before the next builds on it, with a size cap; raw inputs live in the shared store by checksum; decisions in `DECISIONS.md`, commitments on the board, chat for messages only. | Open PR #466 |
| A5 | The comment-reading review check was dropped after two review rounds found it could not be made sound; the rest of the rules checker stays. Separate GitHub accounts for builders and reviewers are not created now. | Open PR #466 |
| A6 | The gate PR is split: PR #467 gates rows from structured government files only; web-sourced rows have no admission path until a follow-up adds per-row proof and a recorded reading by another model family. A row the gate cannot decide is never admitted by a sample. | Open PR #467; branch `agent/claude-code/evidence-binding-web-proofs-2026-11-22` |

## B. The reverted batches and Muse

| # | Ruling | Where it lives |
|---|---|---|
| B1 | Batches 5 (PR #457) and 6 (PR #458) are reverted whole. A removed row returns under its original evidence ID, in a new reviewed PR, only after it passes the binding gate and a replay against the raw file. Rows that fail are kept as leads. This superseded a narrower ruling of the same day to remove 844 rows. | `main` (PR #465); `DECISIONS.md` |
| B2 | `last_activity_date` is derived only from a filing at the site's own street; re-derived (3,746 to 2,632 sites). | `main` (PR #463) |
| B3 | Muse mints nothing and opens no data PR until the owner lifts this. Downloads, the archive copy and read-only work continue. | `DECISIONS.md` (PR #462) |
| B4 | Batch 7 (PR #459) stays in draft until its joins are checked. | `DECISIONS.md` (PR #462) |
| B5 | Muse gets no tracker login; it reports with a path and a sha256 and the controller keeps the board. Muse hands files over through an inbox; the controller verifies and moves them into the store. | This file |
| B6 | Git history is not rewritten (ruled 2026-11-19; restated here because removed rows remain in history). | This file |

## C. What may count as evidence

| # | Ruling | Where it lives |
|---|---|---|
| C1 | A company's switchboard phone or fax number and a role address may stay in a verbatim quote. An individual's email, direct line, extension or mobile number may not. | `AGENTS.md` section 6 (PR #460) |
| C2 | The public SAM.gov entity extract may be quoted as evidence. The 2026-11-16 filter stays: no record marked D&B-sourced or last updated before 2022-04-04. SAM API responses stay leads only. | `DECISIONS.md` (PR #462) |
| C3 | Headcount age: a filing sets a size band only if dated within five years (on or after 2021-11-22). Older filings are leads. | Open PR #468 (SCHEMA v1.19.1) |
| C4 | Name match when the street already matches: the filing's name must equal a held name, or be a held name plus corporate-form words only (Inc, Incorporated, LLC, Corp, Corporation, Co, Company, Ltd, Limited, LP, LLP, Holdings, Holding, Group, US, USA, North America, Americas). | Open PRs #467 and #468 |
| C5 | A part of a site name is ignored as a held name only when every word in it is a generic label (plant, facility, warehouse, main, a number, a compass word, a state, the site's city or county). Brand and division names on the site record count. | Open PR #467 |
| C6 | A filing that names only a recorded parent never binds a subsidiary's site by machine. It is a lead to be read. | Open PR #467 |
| C7 | An archived copy of the company's own page counts as the company's own page for a street address when captured within two years. Older captures are leads. | Branch `agent/claude-code/pic18-streets-2026-11-22` |
| C8 | Sites the fetcher cannot read: the NAS browser may be used for script-built pages (never to pass a block or login); an address shown as an image may be read by text recognition but is flagged until a second model reads it; a search may be used to find an official page, which is then fetched and quoted, never the search result, a map service or a paid directory. No second user-agent. | Branch `agent/claude-code/pic18-streets-2026-11-22` |
| C9 | A street may be taken from government files only as a trial, and only where two independent file families agree. The 25-site trial yielded 1; the route is parked. | Branch `agent/claude-code/pic18-size-sprint-2026-11-22` |
| C10 | Process may be filled at a low tier from an industry code the establishment itself filed, marked as inferred from the code, using a conservative code table shown to the owner first. | Not yet in the repo (lane in progress) |

## D. What to work on

| # | Ruling | Where it lives |
|---|---|---|
| D1 | Outcome first: the measure is the PIC-18 unknown shares (process, market, size on 794 organization rows). | Open PR #466 |
| D2 | Evidence backfill outside PIC-18 is frozen until the PIC-18 unknowns move. Repairs, re-admission of reverted rows that answer a PIC-18 question, and the whole-Atlas audit are exempt. | Open PR #466 |
| D3 | When PIC-18 is done, roll into the rest of Ohio: each route runs on Ohio outside PIC-18 once its PIC-18 PR merges (said). The freeze still holds outside Ohio. | This file |
| D4 | The size PR does not wait for the gate (said: "open the size PR"). | Open PR #468 |
| D5 | The Form 5500 organization lane is cut to organizations that still have no evidence, plus its liveness rows. | Open PR #464 |
| D6 | The whole Atlas gets a blind two-reviewer sample audit, not only the recent window. | Not yet in the repo (queued) |
| D7 | Activity dates for PIC-18 sites the date script misses, and EPA identifiers re-made by exact facility match, are queued behind the evidence lane (said). | Not yet in the repo (queued) |
| D8 | Process routes to pursue: Ohio EPA air permits; reading material already held; industry codes as a low-tier lead. The company confirmation form was not chosen. | Not yet in the repo (lanes in progress) |
| D9 | Pipeline history moves out of the public `notes` field. Facts a reader needs stay as plain sentences; history goes to a file kept for audit. Nothing is deleted. | Not yet in the repo (lane in progress) |
| D10 | Three consistency fixes, each a small reviewed data PR: company type from an unambiguous legal-name suffix; carry processes, materials and markets between a company and its only plant; recompute region labels from the county. | Not yet in the repo (lane in progress) |
| D11 | Regional totals count unverified (tier U) sites and always show the split; prospect lists default to tier A to C. | Not yet in the repo (queued) |

## E. Coordination and tools

| # | Ruling | Where it lives |
|---|---|---|
| E1 | The tracker for this repo is a Kaneo project (PIC workspace, project ATLAS). `tasks/QUEUE.md` stays the claim ledger. | Open PR #466 |
| E2 | Agents working on the Atlas talk in a dedicated private crosswalk; nothing said there authorizes a change to `main`. | This file |
| E3 | One shared raw-data store on the NAS, read-only to every agent, with a checksum manifest; a Parquet layer built from it for queries. A PR that adds rows names its inputs by sha256. | Open PR #466 (rule 6) |
| E4 | Run lighter: one short page of mandatory startup reading; a preflight command and counts generated from the data; a fresh controller thread each wave; the most expensive models only when the owner asks. | Open PR #466 (item 5 of its entry) |
| E5 | Tools are adopted or dropped on a score against a labelled test set, not by argument. Trials on 2026-11-22: an address parser and a record-linkage library were dropped; two decision models are on trial; none may admit a row by itself. | This file |
