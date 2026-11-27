# Withhold PIC-18 process and market values read NOT_STATED by two families, 2026-11-26

Read on: 2026-11-24
Read by: Codex (OpenAI GPT-6.2 Sol), controller packets requote-pilot-2026-11-24 (40 owners) and requote-all-2026-11-24 (345 more owners)
Checked by: Gemini (Google Gemini 4 Hydrogen): 3 of the 37 values in the 2026-11-24 rounds, the other 34 in a blind read on 2026-11-26 (see Second-family check)
Built by: Claude Sonnet 5.5 (Claude Code), thread thr_dj85nmwhby

Owner ruling 2026-11-24 10:29, item 3 (DECISIONS.md): a value whose re-read says NOT_STATED gets basis `not_found_pending_refetch`, which withholds it from public display; the record tables keep it (SCHEMA §4.24).
PR #575 labelled the STATED and IMPLIED lines and left every NOT_STATED line out; this PR is that excluded scope. **The rule (a controller default, reported to the owner; not a ruling, so no DECISIONS.md entry):
a value is withheld only where both model families read it NOT_STATED; any other outcome holds it, and a held value stays public with basis `not_yet_checked`.**
This is a data PR that rests on a read, so AGENTS §2a rule 4 asks for review records from two model families.

## Result (unit: value keys of `data/value_basis.csv`, one per record, field and value)

| Change to `data/value_basis.csv` | organizations | sites | processes | markets_served | all |
|---|---:|---:|---:|---:|---:|
| `not_yet_checked` to `not_found_pending_refetch` (withheld) | 15 | 22 | 13 | 24 | **37** |
| any other change (every other key, its basis, bound row and date) | 0 | 0 | 0 | 0 | 0 |

By table and field: organizations markets_served 13, organizations processes 2, sites processes 11, sites markets_served 11. All 37 are on records of active tier A-C PIC-18 sites or their owners; 17 owners hold at least one (17 organization pages and the directory, county and prospect outputs change; below).
The table keeps its 9,566 keys: stated 547, implied 67, filing 18, not_found_pending_refetch 37, not_yet_checked 8,897. The deciding bound row (`evidence_id`) of each of the 37 is the row it already had; `basis_date` is 2026-11-24, the re-read's date.
`CLAIMS_CHECKED.csv`: 37 `withdrawn` rows and 42 `held` rows (79, one for each adjudicated key).

## The frame: 263 candidates to 79 to 37 (unit: value keys)

| Step | Keys | Where |
|---|---:|---|
| Candidates: the pack's 249 NOT_STATED lines, the 2 lines the 2026-11-24 adjudication takes to NOT_STATED (both IMPLIED in the pack), the 12 `reread-labels-2026-11-26/HOLDS.csv` lines whose reason begins "Gemini 4 Hydrogen census NOT_STATED" | **263** | no duplicate key (asserted). The brief expected 265: the 2026-11-24 `adjudicated.csv` takes only 2 lines to NOT_STATED, and its other 2 NOT_STATED lines go up and are already among the 249 |
| Rejected by the generator (`scripts/value_basis.py`, run on a scratch copy) | **184** | `REJECTED.csv`: 183 UNBOUND (the read page is another page of the cited site: SCHEMA §4.24, "a different page never withholds a value, NOT_STATED included"; the cited page is in `cited_source_refs`), 1 no bound row on its own record (SITE-000292 `distribution`), 0 outranked by a verified quote or filing |
| Frame: the generator accepts them as NOT_STATED | **79** | `second-family/ADJUDICATION-hide.csv`, one line each: processes 37, markets_served 42; organizations 27, sites 52; 48 owners |
| Withheld | **37** | action `withhold` |
| Held | **42** | action `hold`, `HOLDS.csv` |

The 183 UNBOUND lines stay in the pack; they withhold nothing until own-site evidence rows for the read pages go through the binding gate (the follow-up #575 already named). `frame.py` is the stage-1 script (run against `12e79893`; it asserts main withholds nothing, so it is a point-in-time script);
its output is `REJECTED.csv` and the frame counts above. The frame's pilot (AGENTS §2a rule 8b, seed `20261126-hide`, 30 frame lines by SHA-256 rank of the seed and the key): 30 of 30 became `not_found_pending_refetch`, 0 problems, 0 unbound,
3 owners (rings 1/2/4) and 1 market owner known to unknown; the pilot draws from lines the full run had already accepted, so it tested the run, not the acceptance rate (79 of 263).

## The 42 holds (unit: value keys; each line of `HOLDS.csv` carries its reason)

| Hold | Keys |
|---|---:|
| Gemini's blind read of 2026-11-26 is STATED (the re-read said NOT_STATED); all 15 quotes replay verbatim | 15 |
| Gemini's blind read of 2026-11-26 is IMPLIED | 7 |
| The re-read said STATED, Gemini's 2026-11-26 census says NOT_STATED (the 12 census lines, including SITE-001891 `extrusion_pipe_tube`, which Gemini also reads COMPANY_WIDE) | 11 + 1 |
| The re-read said NOT_STATED, the second family read it STATED (ORG-001666 `rv_powersports_trailers`, adjudicated up on 2026-11-24) | 1 |
| A site value whose only bound row is on the organization (SCHEMA §4.24 grain: a corporate statement does not settle a plant claim; the same rule #575 applied to IMPLIED): SITE-000051, 000077, 000114, 000171, 000216, 001428, 002932, all processes | 7 |

## Second-family check (read this before trusting the withholding)

**Reader of record:** Codex (OpenAI GPT-6.2 Sol), 2026-11-24, from the stored pages. **Second family:** Gemini 4 Hydrogen (High), `council-ask --effort deep`.
- **34 of the 37** are from a blind read on 2026-11-26 of the 56 frame keys the second family had not read (the 63 never-second-read frame keys less the 7 held for grain), in 2 batches. The batches carried 12 plants in all, truly stated keys from #575 on the same pages: Gemini read 11 STATED and 1 IMPLIED and none NOT_STATED, so neither batch is void
  (reported by the controller; the plant rows are not in the delivered file). Result on the 56: **34 NOT_STATED, 15 STATED (15 of 15 quotes replay verbatim), 7 IMPLIED.** The rule was fixed before the read.
- **3 of the 37** were read NOT_STATED by Gemini in the 2026-11-24 rounds (the controller's persist `second-family/verdicts.csv`) and agree with the re-read.
- No withheld key has a second-family class other than NOT_STATED; `check.py` recomputes the class from `second-family/read_scored.csv` and the 2026-11-24 verdict files, not from the adjudication's own column.
- A false hide is the costly error (a value leaves the public directory), so the rule errs toward holding. Both families read the stored page text only (the blind-read prompt says "Read only the page text given"); nobody fetched a live page. `not_found_pending_refetch` means a fresh fetch may find the value; it is withheld, not deleted.

## Owners (unit: owners; the controller harness's definition, `harness/pic18_unknown.py`: known = the union of the owner's PIC-18 site tokens, else its own row's)

PIC-18 owners of active tier A-C sites (organizations and ecosystem entities), 792; rings 1/2/4 are the 601 of them whose organization row has ring_primary 1, 2 or 4.

| | Unknown before to after | Known to unknown |
|---|---|---:|
| process, rings 1/2/4 | 204 to 208 of 601 (33.9% to 34.6%) | **4** (ORG-000119, ORG-001937 ring 1; ORG-001700, ORG-001916 ring 2) |
| process, all rings | 327 to 331 of 792 (41.3% to 41.8%) | 4 (the same four) |
| market | 300 to 301 of 792 (37.9% to 38.0%) | **1** (ORG-001396) |

The stage-1 frame projection for all 79 was 6 and 4; the 37 withheld give 4 and 1. A real build of the site on this tree and on `12e79893` (`scripts/build_site.py`, which strips withheld keys at line 493, A/B, footer note normalised) differs in 17 organization pages (exactly the 17 owners with a withheld key), the directory (`directory.html`, `.csv`, `.json` and 6 county directory pages),
5 county pages and `prospects.csv`; no other file. In `directory.json`, 36 tokens leave an owner's row for the 37 keys and nothing else changes; the 37th token (SITE-000185 `rubber_extrusion`) stays because that owner's only other site value is also withheld, so the row falls back to the organization row, which still holds it and is labelled "org record".
The directory's own unknown counts move 205 to 209 (rings 1/2/4), 328 to 332 and 300 to 301; they sit 1 above the harness at the base (the directory's display rule differs from the harness by one owner).
Public outputs that drop a withheld value: the site pages and directory (`build_site.py`), the graph tags (`build_graph.py`, line 93), the release export (`export_release.py`: the cell is blanked, an evidence row naming the value reads "[withheld from this release]", and the `value_basis` rows of the basis are left out). The record tables and `data/*.csv` keep the values.

## Checks

`python3 -I tasks/hide-not-stated-2026-11-26/check.py --store <controller persist dir>` regenerates `data/value_basis.csv` from the repo's data, every other `tasks/` folder and this folder's lines, and compares the whole table with `12e79893`:
exactly the 37 keys change, each `not_yet_checked` to `not_found_pending_refetch`, each on its own record; every withheld key is a `withhold` line whose second-family class is recomputed as NOT_STATED; the adjudication's 79 actions follow the rule; the 7 grain holds are exactly the keys a NOT_STATED line would withhold on an organization row (tried by a generator run, not assumed);
`REJECTED.csv` plus the adjudicated keys equal the 263 candidates recomputed from the pack; `HOLDS.csv`, `CLAIMS_CHECKED.csv` and `INPUTS.sha256` match; the owner counts above hold. Without the store the page-URL manifest, the pack comparison, the grain trial and the 2026-11-24 second-family reads are reported NOT_INSPECTED and the exit code is 3, never 0.
Planted defects, each shown rejected by the rule it names: a hold line put back as NOT_STATED (`held_line`); one of the 7 organization-row site lines put back (`grain`); a withhold line dropped (`line_dropped`); an edited `value_basis` row (`edited_row`); a dropped `value_basis` key (`dropped_key`);
a withhold key whose second-family class is not NOT_STATED (`second_family`); a STATED verdict line (`class`); an adjudicated key also listed as rejected and a dropped rejected line (`frame`); a dropped, a re-pointed and a held-as-withdrawn CLAIMS_CHECKED row (`claims`).

`check.py` of `tasks/reread-labels-2026-11-26/` (PR #575) is a point-in-time check: it regenerates the table from its own folder alone and asserts "nothing is withheld", so it fails on any tree that holds this PR (37 `edited_row` findings); CI does not run folder checks. It is left as it is (follow-up: have it include other folders or retire it).

## One test changed

`scripts/test_build_site.py` `RealDataHeadlineTest.test_filter_counts_match_the_csvs` recomputes the directory's process-filter counts from the CSVs with the csv module alone and did not drop withheld values, so it failed on this tree
(the page gives 88 companies with `injection_molding`, the oracle 89: SITE-001891's `injection_molding`, ORG-001859, is withheld). #575 withheld nothing, so the oracle's gap never showed. The oracle now reads `data/value_basis.csv` and drops `not_found_pending_refetch` keys (6 lines).
Planted defect: with `value_basis.strip_withheld` replaced by a no-op (the page shows withheld values) the test fails, 89 != 88.

## Files

`VALUE_VERDICTS.csv`: the pack's `values.csv` lines for the 37 withhold keys, class NOT_STATED, no quote or offset, as the pack gives them (SCHEMA §4.24). `VALUE_PAGES.csv`: page sha256 to the URL the page was captured from, from the lane's corpus manifest (builder: `value-pages-builder/build_value_pages.py`).
`HOLDS.csv`: the 42 holds with the adjudication's reason. `REJECTED.csv`: the 184 candidates the generator rejects, with its reason and the page the bound row cites. `second-family/ADJUDICATION-hide.csv` and `read_scored.csv`: the controller's files; `ADJUDICATION-hide.csv` is byte for byte
(sha256 `6d4558c5ead6702d5e84355205e718faae8f5e49122bc117358ddfe39e68449d`); `read_scored.csv` was delivered with CRLF line endings (sha256 `b7a5be51a1dd0fea0a0f802486ac62b9b75874e597a33ec577ca0e8f449abd85`) and the repo's CSV rule (LF, `.gitattributes`) converted it; nothing else differs (`INPUTS.sha256` holds the LF form).
`CLAIMS_CHECKED.csv` (`python3 -I check.py --store ... --write-claims` writes it). `INPUTS.sha256`: the pack files and this folder's files. `build.py` rebuilds `VALUE_VERDICTS.csv`, `VALUE_PAGES.csv` and `HOLDS.csv` (`python3 -I build.py PERSIST_DIR`); `data/value_basis.csv` is regenerated with
`python3 scripts/value_basis.py --pages PERSIST_DIR`; nobody edits it. `frame.py`: stage 1.
