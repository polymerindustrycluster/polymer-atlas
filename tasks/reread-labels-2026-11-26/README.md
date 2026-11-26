# Re-read basis labels for PIC-18 process and market values, 2026-11-26

Read on: 2026-11-24
Read by: Codex (OpenAI GPT-6.2 Sol), controller packet requote-pilot-2026-11-24 (40 owners) and requote-all-2026-11-24 (345 more owners)
Checked by: Gemini (Google Gemini 4 Hydrogen), partial: 220 of the 935 STATED values read, plus all 77 IMPLIED and 25 of the 249 NOT_STATED (see Coverage)
Built by: Claude Sonnet 5.5 (Claude Code), thread thr_zpyjrwcn58

Owner ruling 2026-11-24 10:29, item 2 (DECISIONS.md): every process or market value cited from a page keeps its public place with a generated
per-value basis label, and all 385 PIC-18 owners with such values are re-read against their stored pages. The re-read ran on 2026-11-24.
This PR applies **labels only**: the STATED and IMPLIED lines. No NOT_STATED line is here, so no value becomes `not_found_pending_refetch`
(withheld). Hiding is a separate PR with its own counts (ruling 3).

## Result (unit: value keys of `data/value_basis.csv`, one per record, field and value)

| Change to `data/value_basis.csv` | processes | markets_served | all |
|---|---:|---:|---:|
| `not_yet_checked` to `stated` | 248 | 332 | **580** |
| `not_yet_checked` to `implied` | 15 | 20 | **35** |
| any other change of basis | 0 | 0 | 0 |
| `not_found_pending_refetch` (withheld) | 0 | 0 | **0** |

By table: organizations 281 stated and 20 implied; sites 299 stated and 15 implied. All 615 keys are on records of active tier A-C PIC-18 sites or their
owners; 235 of the 792 PIC-18 owners (organizations and ecosystem entities) gain at least one label (processes 135, markets 160). The table keeps its
9,566 keys: stated 57 to 637, implied 0 to 35, filing 18, not_yet_checked 9,491 to 8,876. On 7 of the 615 keys the deciding evidence row moves to the row that cites the read page.

## What is not labelled here, and why

| Not labelled | Lines | Where listed |
|---|---:|---|
| The reader read another page of the cited site than the page the bound row cites (SCHEMA §4.24: no label, the key stays `not_yet_checked`) | **392**: processes 207 (178 STATED, 29 IMPLIED), markets_served 185 (157 STATED, 28 IMPLIED) | the lines stay in `VALUE_VERDICTS.csv` and are listed in `UNBOUND.csv` with the read page and the page the row cites. **Follow-up, a later PR:** own-site evidence rows for the read pages through the binding gate; the lines then label with no change to this folder. |
| A STATED site value with only an organization-level bound row (the generator stops on it) | 3 | `HOLDS.csv`: SITE-000082 `foam_fabrication`, SITE-000107 `plastics_machining_cnc`, SITE-001375 `construction_building_products` |
| Second-family adjudication to NOT_STATED (the hiding PR's scope) | 2 | `HOLDS.csv`: ORG-000534 `automotive_unspecified`, SITE-001867 `plastics_fabrication_welding` |
| Pack NOT_STATED adjudicated up (a label needs a quote and offset, or a witness page that is not the cited page) | 2 | `HOLDS.csv`: ORG-001666 `rv_powersports_trailers` (to STATED), SITE-001729 `appliances` (to IMPLIED) |
| Every NOT_STATED line (249 after the adjudications) and every NO_PAGE line (189) | 249 and 189 | not in this PR. NOT_STATED maps to withholding (ruling 3): a separate PR with its own counts. |

## Files

`VALUE_VERDICTS.csv`: the pack's `values.csv` lines (STATED 915, IMPLIED 92), class replaced where a second-family adjudication says so; an IMPLIED line carries
no quote or offset (SCHEMA §4.24). Of the 21 adjudications, 17 are STATED to IMPLIED (applied) and 4 are held (above). `VALUE_PAGES.csv`: page sha256 to the URL the page was
captured from, from the lane's corpus manifest (builder: `value-pages-builder/build_value_pages.py`). `HOLDS.csv`, `UNBOUND.csv`: above. `INPUTS.sha256`: the pack files and this folder's
files. `build.py` rebuilds the three csv files from the pack (`python3 -I build.py PERSIST_DIR`). `check.py` is the named check. `data/value_basis.csv` is regenerated with
`python3 scripts/value_basis.py --pages PERSIST_DIR`; nobody edits it.

## Pilot (AGENTS §2a rule 8b)

Before the full set, a seeded draw (seed `20261126-labels`; 25 STATED and 5 IMPLIED lines by SHA-256 rank of the seed and the value key) was run through the generator:
19 of 30 lines labelled (17 stated, 2 implied), 0 problems, all 30 quotes replayed and all 30 page URLs matched the corpus manifest; 11 lines read another page of the cited site (9 STATED,
2 IMPLIED). That passed the generator but missed the pre-registered "no more than 3 of 30 fail for one reason", so the work stopped and the controller ruled "go": label what the schema allows and
list the rest as a follow-up. The full set's 392 of 1,007 matches the pilot's 11 of 30 within sampling error.

## Coverage of the second-family check (read this before trusting a label)

The second family read 152 values in round 1 (all 77 IMPLIED, a seeded 50 STATED, a seeded 25 NOT_STATED; 145 agree) and 170 STATED values in
round 2 (114 with no value word in the quote, 6 quoting a pre-2000 year, a seeded 50 of the rest; 156 agree). That is 220 of the 935 STATED
values read; **715 STATED values have no second-family reading**. The second family disputed 17 STATED values (all to IMPLIED); the controller
adopted the stricter class for all 17. Round 2's pre-registered line (0 to 2 disagreements in the seeded random 50) held: 0 of 50. The 715
unread STATED values rest on the reader's own verdict, a replayed quote, and that agreement rate; a reviewer family should sample them.
