# PIC-18 organization-level process canary, 2026-11-18

**Result: 0 of 10 organizations applied. No data row changed.** Every organization is STILL_UNCERTAIN. The canary answers its question: for this frame, stored own-site pages did not support filling organization-level `processes` from corporate claims. `process_unknown` stays at 331 (unit: PIC-18 organization rows with no process at site or organization grain).

## Frame (fixed by the controller, not changed here)
Seed 20261118; 10 organizations drawn from 258 PIC-18 organizations with an unknown process at site and organization grain, exactly one active Atlas site across all shards, and stored corpus pages. Stratum H = held by a 2026-11-16 capability lane at site grain (5). Stratum N = never adjudicated (5). All 10 rows are in `data/organizations_OH.csv`; all 10 have one active OH site with a blank `processes` cell.

## Per-organization verdict and term table
| Org | Name | Tier | Stratum | Readable pages | Verdict | Terms | Hold reason |
|---|---|---|---|---|---|---|---|
| ORG-000488 | Pharmacy-Lite Packaging | B | H | 9 (5 stored, 4 live) | STILL_UNCERTAIN | none | no_process_named |
| ORG-001513 | Coltene/Whaledent Inc. | B | H | 4 stored (live /company/about/ and /science/: HTTP 403) | STILL_UNCERTAIN | none | no_process_named |
| ORG-001774 | Alcon Tool Co | A | H | 6 stored | STILL_UNCERTAIN | none | owner_vocab_ruling |
| ORG-001986 | Optimax Plastic LLC | B | H | 5 (4 stored, 1 live) | STILL_UNCERTAIN | none | equipment_maker_not_process |
| ORG-002047 | Wayne-Dalton Plastics | B | H | 1 real page + 2 bot-check walls (live retry: HTTP 403) | STILL_UNCERTAIN | none | fetch_blocked |
| ORG-000066 | Custom Plastic Extrusions, Ltd. | C | N | 0 (website `none_found`) | STILL_UNCERTAIN | none | no_website |
| ORG-000107 | T&M Plastics Co. | U | N | 0 (robots-blocked) | STILL_UNCERTAIN | none | fetch_blocked |
| ORG-000192 | Triangle Chemical Co. | C | N | 0 (empty body) | STILL_UNCERTAIN | none | fetch_blocked |
| ORG-001497 | Budzar Industries LLC | B | N | 0 (robots-blocked) | STILL_UNCERTAIN | none | fetch_blocked |
| ORG-001855 | NewKor Inc. | A | N | 1 stored (1,638 bytes) | STILL_UNCERTAIN | none | vocab_and_strength |

`holds.csv` has what was read and the fact that would settle each case. `verdicts.csv` is the machine form. `pages.csv` lists every stored and live fetch row with its recomputed sha256 check.

## Yield
- Stratum H: 0 of 5 organizations applied. Stratum N: 0 of 5 applied. Total 0 of 10.
- Only 6 of the 10 organizations have any readable page; 4 of 5 in stratum N have none, so the stored-pages premise held for 6 of 10, not 10 of 10 (the frame counted organizations with manifest rows, and the manifest rows for those 4 are failed fetches). "Readable" includes ORG-002047's two bot-check walls only as status-ok; its one real page is counted.

## Holds by reason (unit: organizations)
- no_process_named: 2 (the pages say the company manufactures a product and never say how). ORG-000488: two linked PDFs unread.
- owner_vocab_ruling: 1 (ORG-001774 Alcon Tool). The about page has one narrative sentence, "Delivering custom design, full production, and expert refurbishment of industrial cutting tools for manufacturing applications worldwide since 1946." The only term whose words could fit is `tooling_repair_maintenance`, which §3.1 names but does not define. Whether it covers refurbishing metal industrial knives is a vocabulary question, so it is held with a recommendation (no; define it as polymer-processing tooling) in `holds.csv`. `plastics_machining_cnc`, `coating_applying` and `mold_tool_making` were considered and rejected: steel knives, plating, and cutting tools rather than molds.
- vocab_and_strength: 1 (ORG-001855 NewKor: no §3.1 term names spiral winding of tubing, `composites_filament_winding` is a different process, and a list item on a tier A record is supports_C, which fails V-25).
- equipment_maker_not_process: 1 (Optimax sells equipment and consulting to rotomolders. Its record website URL, `/index.php/rotomolding/`, is a general explainer of the process, which is not a company claim; no page says Optimax rotomolds parts).
- fetch_blocked: 4 (ORG-002047 bot wall; ORG-000107, -000192, -001497 no readable page).
- no_website: 1 (ORG-000066; rule 14 bars guessing a domain).

## Fetches (rule 14)
Twelve live fetches on 2026-11-18, stored under `S/persist/pic18-org-process-canary-2026-11-18/` (cache and `live-fetches.json`, with sha256); none used more than 5 per organization. Each URL is either the website on the record or a link on a stored page, as `fetch.py` states per row: the record website for ORG-000107, -000192, -001497 (unreadable again) and ORG-001986 (`/index.php/rotomolding/`, read); four hrefs on the stored Pharmacy-Lite home page (`/biodegradable` and three `/products/...` pages read, the bio-sheet PDF unreadable); two links on the stored Coltene company page (HTTP 403); one link on the stored Wayne-Dalton home page (HTTP 403). The fetcher is `scripts/site_corpus.py`, so robots.txt gates every request. No URL was constructed.

## Outcome check
`python3 S/harness/pic18_unknown.py "$PWD" <ref>`, with S the controller thread-storage atlas folder:
- merge-base 099497f: PIC-18 org rows=794 proc_unknown=331 (41.7%)
- HEAD: proc_unknown=331 (41.7%). Fall = 0 = organizations applied. `check.py` asserts both numbers and the equality (run it after committing; the harness reads git refs).

## What the code does
- `build.py` writes `pages.csv` and `verdicts.csv`, and would fill blank `processes` cells and append EVD-396000..396099 rows from `claims.csv` (header only, no claims). The writer ran only in `check.py`'s temp copy, where a fixture claim was applied, re-applied (byte-identical) and diffed.
- `check.py` recomputes frame size, page counts against files on disk (28 status-ok pages with text, including 2 bot-check walls and 1 Coltene image), sha256 of every stored page, applied organizations against the base commit, also asserts that `git diff` against the merge-base touches only `organizations_OH.csv` and `evidence_organizations_OH.csv`, and then proves it fails on nine injected defects: term not in §3.1; quote not on the stored page; supports_C on tier B; page hash mismatch; organization outside the frame; write to a non-`processes` column; write to a non-blank cell; write to a site row; evidence id outside the block.
- The fixture claim used for the positive control (Optimax, `rotational_molding`) is **not** a finding. I hold Optimax on the merits above.

## Not checked
- Pages I did not reach: the two Pharmacy-Lite PDFs, Coltene's blocked pages, and anything not linked from a stored page. No search was run for other own-site URLs, so an organization could have a process page I did not reach.
- Wayne-Dalton's plastics operation (Conneaut) was not read: both deeper pages are a bot wall.
- Parent or sister-company pages were excluded by rule, not read.
- Whether the other 248 of the 258 eligible organizations would yield: a 0 of 10 draw gives an upper 95% bound of 27.8% (Wilson), so this canary does not show the rate is zero.

## Proposed follow-ups
- Draw the next canary only from organizations with a readable own-site page; 4 of 10 here had none, which capped the yield before any claim was read.
- Optimax-type equipment makers and tool makers need an owner ruling on whether a customer-serving statement ever counts as a process claim (this canary says no).
- A schema question for the owner: no §3.1 term fits spiral-wound tubing or vulcanized-fiber and phenolic tube making (ORG-001855).
