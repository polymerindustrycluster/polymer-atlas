# Re-read basis labels for PIC-18 process and market values, 2026-11-26

Read on: 2026-11-24
Read by: Codex (OpenAI GPT-6.2 Sol), controller packets requote-pilot-2026-11-24 (40 owners) and requote-all-2026-11-24 (345 more owners)
Checked by: Gemini (Google Gemini 4 Hydrogen): 220 of the 935 STATED values in the 2026-11-24 rounds, and on 2026-11-26 a census of the 461 further STATED values this PR would label (see Second-family check)
Built by: Claude Sonnet 5.5 (Claude Code), thread thr_zpyjrwcn58

Owner ruling 2026-11-24 10:29, item 2 (DECISIONS.md): every process or market value cited from a page keeps its public place with a generated
per-value basis label, and all 385 PIC-18 owners with such values are re-read against their stored pages. The re-read ran on 2026-11-24.
This PR applies **labels only**: the STATED and IMPLIED lines. No NOT_STATED line is here, so no value becomes `not_found_pending_refetch`
(withheld). Hiding is a separate PR with its own counts (ruling 3).

## Result (unit: value keys of `data/value_basis.csv`, one per record, field and value)

| Change to `data/value_basis.csv` | processes | markets_served | all |
|---|---:|---:|---:|
| `not_yet_checked` to `stated` | 185 | 305 | **490** |
| `not_yet_checked` to `implied` | 38 | 30 | **68** |
| any other change of basis | 0 | 0 | 0 |
| `not_found_pending_refetch` (withheld) | 0 | 0 | **0** |

558 keys change (`CLAIMS_CHECKED.csv` has 558 rows). By table: organizations 263 stated and 35 implied; sites 227 stated and 33 implied. All 558 are on records of
active tier A-C PIC-18 sites or their owners; 220 of the 792 PIC-18 owners (organizations and ecosystem entities) gain at least one label (processes 117, markets 153).
The table keeps its 9,566 keys: stated 57 to 547, implied 0 to 68, filing 18, not_yet_checked 9,491 to 8,933. On 6 of the 558 keys the deciding evidence row moves to the
row that cites the read page.

## What is not labelled here, and why

| Not labelled | Lines | Where listed |
|---|---:|---|
| The reader read another page of the cited site than the page the bound row cites (SCHEMA §4.24: no label, the key stays `not_yet_checked`) | **392**: processes 207 (178 STATED, 29 IMPLIED), markets_served 185 (157 STATED, 28 IMPLIED) | the lines stay in `VALUE_VERDICTS.csv` and are listed in `UNBOUND.csv` with the read page and the page the row cites. **Follow-up, a later PR:** own-site evidence rows for the read pages through the binding gate; the lines then label with no change to this folder. |
| The 2026-11-26 second-family census held the line (below) | **57**: processes 40, markets_served 17 | `HOLDS.csv`, reason as the census gave it; the key stays `not_yet_checked` |
| A STATED site value with only an organization-level bound row (the generator stops on it) | 3 | `HOLDS.csv`: SITE-000082 `foam_fabrication`, SITE-000107 `plastics_machining_cnc`, SITE-001375 `construction_building_products` |
| Second-family adjudication to NOT_STATED (the hiding PR's scope) | 2 | `HOLDS.csv`: ORG-000534 `automotive_unspecified`, SITE-001867 `plastics_fabrication_welding` |
| Pack NOT_STATED adjudicated up (a label needs a quote and offset, or a witness page that is not the cited page) | 2 | `HOLDS.csv`: ORG-001666 `rv_powersports_trailers` (to STATED), SITE-001729 `appliances` (to IMPLIED) |
| Every NOT_STATED line (249 after the adjudications) and every NO_PAGE line (189) | 249 and 189 | not in this PR. NOT_STATED maps to withholding (ruling 3): a separate PR with its own counts. |

## Second-family check (read this before trusting a label)

**2026-11-24 rounds.** The second family read 152 values in round 1 (all 77 IMPLIED, a seeded 50 STATED, a seeded 25 NOT_STATED; 145 agree) and 170 STATED values in round 2
(114 with no value word in the quote, 6 quoting a pre-2000 year, a seeded 50 of the rest; 156 agree): 220 of the 935 STATED values. It disputed 17 STATED values (all to IMPLIED);
the controller adopted the stricter class for all 17 (21 adjudications in all: 17 applied, 4 held). Round 2's pre-registered line (0 to 2 disagreements in the seeded random 50) held: 0 of 50.

**2026-11-26 census.** A blind sample of 40 of the 461 labelled-STATED keys no second family had read gave 3 IMPLIED, which met the stop line fixed in advance (3 or more refutes).
Gemini 4 Hydrogen (High), run with `council-ask --effort deep`, then read **all 461** such keys in 5 blind batches. Each batch carried 5 planted wrong values: **25 of 25 caught**,
so no batch is void. The adoption rule was fixed at 16:20 on 2026-11-26, before the census ran: where Gemini reads IMPLIED, the label becomes `implied` (33 keys: processes 23, markets 10);
where it reads NOT_STATED, or COMPANY_WIDE on a site key, the line is dropped from `VALUE_VERDICTS.csv`, the key stays `not_yet_checked`, and it is listed in `HOLDS.csv` (57 keys:
41 STATED COMPANY_WIDE, 4 IMPLIED COMPANY_WIDE, 1 NOT_STATED COMPANY_WIDE, 11 NOT_STATED). The other 371 stay `stated`. Of the 57 held keys, 46 are a company-wide reading on a site key and 11 are NOT_STATED. All 46 company-wide site keys belong to owners with one held site (43 owners, each with exactly one site row in the Atlas, active); that does not change
the rule, because SCHEMA §4.24 says a corporate statement does not settle a plant claim. `ADJUDICATION-census.csv` (the 90 changes) and `census_scored.csv` (Gemini's class for all 461 keys)
are in `second-family/`, as the controller delivered them except that the repo's CSV rule (LF line endings, `.gitattributes`) converted CRLF to LF; nothing else differs (the delivered files have sha256 `011633f88fec1f5b65a220c46f7b633374f436de6e66fb5ca59b4ce5c2ce8d34` and `326aeeed54b969aa922067fbda4a862df8c7a61114be13427b97fef452e0e377`; `INPUTS.sha256` holds the LF forms). On the 33 IMPLIED lines the class changes and the quote and offset are cleared, because the
generator's IMPLIED format carries neither (SCHEMA §4.24); nothing else on the line changes.

With the census, every key labelled here has a second-family reading: 119 `stated` and 35 `implied` from the 2026-11-24 rounds, the rest from the census. The 392 unbound lines are labelled by nothing here.

## Files

`VALUE_VERDICTS.csv`: the pack's `values.csv` lines (STATED 825, IMPLIED 125), class replaced where an adjudication or the census says so; an IMPLIED line carries no quote or offset (SCHEMA §4.24).
`VALUE_PAGES.csv`: page sha256 to the URL the page was captured from, from the lane's corpus manifest (builder: `value-pages-builder/build_value_pages.py`). `HOLDS.csv`, `UNBOUND.csv`: above.
`CLAIMS_CHECKED.csv`: one `verified` row for each of the 558 labelled keys (the harness's format has no value column, so `check.py` compares the rows with the keys whose basis changed as a
multiset; `python3 -I check.py --write-claims` writes it). `second-family/`: the census files. `INPUTS.sha256`: the pack files, the census files and this folder's files. `build.py` rebuilds the three
csv files from the pack and the census (`python3 -I build.py PERSIST_DIR`). `check.py` is the named check. `data/value_basis.csv` is regenerated with
`python3 scripts/value_basis.py --pages PERSIST_DIR`; nobody edits it.

## Pilot (AGENTS §2a rule 8b)

Before the full set, a seeded draw (seed `20261126-labels`; 25 STATED and 5 IMPLIED lines by SHA-256 rank of the seed and the value key) was run through the generator:
19 of 30 lines labelled (17 stated, 2 implied), 0 problems, all 30 quotes replayed and all 30 page URLs matched the corpus manifest; 11 lines read another page of the cited site (9 STATED,
2 IMPLIED). That passed the generator but missed the pre-registered "no more than 3 of 30 fail for one reason", so the work stopped and the controller ruled "go": label what the schema allows and
list the rest as a follow-up. The full set's 392 of 1,007 lines (before the census) matches the pilot's 11 of 30 within sampling error.
