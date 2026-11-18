# PIC-18 organization-level process canary, 2026-11-18

**Result: 0 of 10 organizations applied. No data row changed.** Every organization is STILL_UNCERTAIN. The canary answers its question: for this frame, stored own-site pages did not support filling organization-level `processes` from corporate claims. `process_unknown` stays at 331 (unit: PIC-18 organization rows with no process at site or organization grain).

## Frame (fixed by the controller, not changed here)
Seed 20261118; 10 organizations drawn from 258 PIC-18 organizations with an unknown process at site and organization grain, exactly one active Atlas site across all shards, and stored corpus pages. Stratum H = held by a 2026-11-16 capability lane at site grain (5). Stratum N = never adjudicated (5). All 10 rows are in `data/organizations_OH.csv`; all 10 have one active OH site with a blank `processes` cell.

## Per-organization verdict and term table
| Org | Name | Tier | Stratum | Readable pages | Verdict | Terms | Hold reason |
|---|---|---|---|---|---|---|---|
| ORG-000488 | Pharmacy-Lite Packaging | B | H | 6 (5 stored, 1 live) | STILL_UNCERTAIN | none | no_process_named |
| ORG-001513 | Coltene/Whaledent Inc. | B | H | 4 stored (live /company/about/ and /science/: HTTP 403) | STILL_UNCERTAIN | none | no_process_named |
| ORG-001774 | Alcon Tool Co | A | H | 6 stored | STILL_UNCERTAIN | none | vocab_and_strength |
| ORG-001986 | Optimax Plastic LLC | B | H | 4 stored | STILL_UNCERTAIN | none | equipment_maker_not_process |
| ORG-002047 | Wayne-Dalton Plastics | B | H | 1 real page + 2 bot-check walls | STILL_UNCERTAIN | none | fetch_blocked |
| ORG-000066 | Custom Plastic Extrusions, Ltd. | C | N | 0 (website `none_found`) | STILL_UNCERTAIN | none | no_website |
| ORG-000107 | T&M Plastics Co. | U | N | 0 (robots-blocked) | STILL_UNCERTAIN | none | fetch_blocked |
| ORG-000192 | Triangle Chemical Co. | C | N | 0 (empty body) | STILL_UNCERTAIN | none | fetch_blocked |
| ORG-001497 | Budzar Industries LLC | B | N | 0 (robots-blocked) | STILL_UNCERTAIN | none | fetch_blocked |
| ORG-001855 | NewKor Inc. | A | N | 1 stored (1,638 bytes) | STILL_UNCERTAIN | none | vocab_and_strength |

`holds.csv` has what was read and the fact that would settle each case. `verdicts.csv` is the machine form. `pages.csv` lists every stored and live fetch row with its recomputed sha256 check.

## Yield
- Stratum H: 0 of 5 organizations applied. Stratum N: 0 of 5 applied. Total 0 of 10.
- Only 6 of the 10 organizations have any readable page; 4 of 5 in stratum N have none, so the stored-pages premise held for 6 of 10, not 10 of 10 (the frame counted organizations with manifest rows, and the manifest rows for those 4 are failed fetches).

## Holds by reason (unit: organizations)
- no_process_named: 2 (the pages say the company manufactures a product and never say how).
- vocab_and_strength: 2 (ORG-001774 tooling for steel knives: no §3.1 term matches and the items are tab/list entries; ORG-001855 tubing: no §3.1 term matches "spiral wound"; both tier A, where a list item is supports_C and fails V-25).
- equipment_maker_not_process: 1 (Optimax sells equipment and consulting to rotomolders; no page says it rotomolds).
- fetch_blocked: 4 (ORG-002047 bot wall; ORG-000107, -000192, -001497 no readable page).
- no_website: 1 (ORG-000066; rule 14 bars guessing a domain).

## Fetches (rule 14)
Six live fetches, stored under `S/persist/pic18-org-process-canary-2026-11-18/` (cache and `live-fetches.json`, with sha256): the record website for ORG-000107, -000192, -001497 (all unreadable again), `https://pharmacylite.com/biodegradable` (an href on the stored home page; no process), and two links on the stored Coltene company page (HTTP 403). `fetch.py` is the script; it goes through `scripts/site_corpus.py`, so robots.txt gates every request. No URL was constructed.

## Outcome check
`python3 S/harness/pic18_unknown.py "$PWD" <ref>`, with S the controller thread-storage atlas folder:
- merge-base 099497f: PIC-18 org rows=794 proc_unknown=331 (41.7%)
- HEAD: proc_unknown=331 (41.7%). Fall = 0 = organizations applied.

## What the code does
- `build.py` writes `pages.csv` and `verdicts.csv`, and would fill blank `processes` cells and append EVD-396000..396099 rows from `claims.csv` (header only, no claims). The writer ran only in `check.py`'s temp copy, where a fixture claim was applied, re-applied (byte-identical) and diffed.
- `check.py` recomputes frame size, page counts against files on disk, sha256 of every stored page, applied organizations against the base commit, and then proves it fails on nine injected defects: term not in §3.1; quote not on the stored page; supports_C on tier B; page hash mismatch; organization outside the frame; write to a non-`processes` column; write to a non-blank cell; write to a site row; evidence id outside the block.
- The fixture claim used for the positive control (Optimax, `rotational_molding`) is **not** a finding. I hold Optimax on the merits above.

## Not checked
- Pages beyond the stored 5 or 6 per organization (about 6 fetches each were allowed; failed fetches used them). No search was run for other own-site URLs, so an organization could have a process page I did not reach.
- Wayne-Dalton's plastics operation (Conneaut) was not read: both deeper pages are a bot wall.
- Parent or sister-company pages were excluded by rule, not read.
- Whether the other 248 of the 258 eligible organizations would yield: a 0 of 10 draw gives an upper 95% bound of 27.8% (Wilson), so this canary does not show the rate is zero.

## Proposed follow-ups
- Draw the next canary only from organizations with a readable own-site page; 4 of 10 here had none, which capped the yield before any claim was read.
- Optimax-type equipment makers and tool makers need an owner ruling on whether a customer-serving statement ever counts as a process claim (this canary says no).
- A schema question for the owner: no §3.1 term fits spiral-wound tubing or vulcanized-fiber and phenolic tube making (ORG-001855).
