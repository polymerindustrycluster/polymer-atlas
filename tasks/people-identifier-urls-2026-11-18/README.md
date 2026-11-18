# People identifier URLs: owner rulings 2026-11-18 items 1 and 1b, and validator V-62 (SCHEMA v1.13.4)

Branch `agent/claude-code/people-identifier-urls`. Task: remove personal-account identifier URLs (`?u=<network id>`, `/~<account>`)
from `data/people.csv`, then make V-62 refuse new ones. No URL below is written out; rows are named by person ID.

## Frame (unit: `people.csv` rows with an identifier URL in `public_profile_url`, `lab_url` or `sources`)
Base `099497fa` (and unchanged at the rebased base `5553d26a`): **29 rows** = 18 `?u=` + 11 `/~` (one `/~` written without a scheme,
PERSON-001037); 50 cells (`public_profile_url` and/or `sources`; no `lab_url`). `check.py` recounts this by csv and by an
independent raw-line count (both 29). `evidence_people.csv`: 8 rows cite such URLs (4 `?u=`, 4 `/~`); none was edited.

## Applied counts (unit: people rows)
| Outcome | Rows | Detail |
|---|---|---|
| replaced with an identifier-free page + new evidence | **25** | 27 evidence rows, EVD-396100..396126 (24 existence at `supports_A`; 925 existence, 925 scope, 1199 scope at `supports_B`) |
| URL blanked (old evidence stays the source) | **4** | PERSON-000054, -000075, -000359, -001304 |
| held (STILL_UNCERTAIN) | **0** | no row was left without a usable `sources` |

Only `public_profile_url`, `lab_url`, `sources` and `last_verified` changed, on those 29 rows. `last_verified` = 2026-11-18 on the 25
replaced rows (a page fetched today confirmed name, title and institution); it is unchanged on the 4 blanked rows (nothing was re-checked
on them). Where a replaced row's `sources` lacked the new page it was appended, because the new evidence rows cite it.

## Per row (A = `/polymer/about-us/our-people` listing page 1, A2 = its `?currentPage=2`; all pages stored with sha256 in `witness.csv` / `manifest.csv`)
| Person | Action | Page (host / path) | How the page became fetchable (rule 14) | Evidence |
|---|---|---|---|---|
| 000043, 045, 046, 048, 049, 050, 057, 058, 078 | replaced | uakron.edu A | already a source on these rows | 396100-396105, 396109, 396110, 396114 |
| 000051, 052, 055, 061 | replaced | uakron.edu A2 | pagination link on the A page | 396106-396108, 396111 (052 answers EVD-333160) |
| 000076 | replaced | uakron.edu `/engineering/me/our-people` | nav link on `/engineering/me/research/` (a source on PERSON-000077) | 396112 |
| 000077 | replaced | same, `?currentPage=2` | pagination link on the previous page | 396113 |
| 000079 | replaced | uakron.edu `/engineering/cbe/our-people/faculty` | search I ran: Zhou + department + Akron (uakron.edu) | 396115 |
| 000097 | replaced | artsci.uc.edu chemistry faculty directory | search: Simms + chemistry + Cincinnati (uc.edu) | 396116 |
| 000104 | replaced | ceas.uc.edu MSE faculty list | search: Shi + MSE + Cincinnati (uc.edu) | 396117 |
| 000779 | replaced (sources only) | colorado.edu `/mechanical/` faculty page | search: Long + mechanical engineering + CU Boulder | 396118 |
| 000850 | replaced | chem.fsu.edu department person page | search: Schlenoff + Lawton + FSU | 396119 |
| 000882 | replaced (sources only) | chem.uci.edu people page | search: Guan + chemistry + UC Irvine | 396120 |
| 000925 | replaced | artsandsciences.fsu.edu faculty spotlight | search: Shanbhag + Scientific Computing + FSU | 396121-396122 (answers EVD-280034, -280035, -280105) |
| 001037 | replaced | latech.edu directory | search: Peters + chemical engineering + Louisiana Tech | 396123 |
| 001132 | replaced (sources only) | buffalo.edu chemistry faculty page | already a source on the row | 396124 |
| 001199 | replaced (sources only) | engr.colostate.edu faculty page | already a source on the row | 396125-396126 (answers EVD-283153) |
Blanked: 000054, 000075, 000359, 001304 (reasons under Holds and blanks).

## Holds and blanks, each with its settling fact
- **PERSON-000054 (blanked):** the listing states name and rank, but not the specialty that the old evidence row (EVD-280053) took from the identifier URL. The old rows EVD-280052/053/113 stay as the source. Settles it: an identifier-free page stating that specialty.
- **PERSON-000075 (blanked):** the university's emeritus page styles him Distinguished Professor Emeritus; the row says professor. Not the same role, so no replacement. Settles it: an owner call on emeritus rows (see follow-ups).
- **PERSON-000359 (blanked):** the only identifier-free department page found lists him under In Memoriam, and a search result I did not fetch reports his death in January 2026. A status change needs dated evidence (AGENTS §3) and is not this task.
- **PERSON-001304 (blanked):** the only identifier-free page found with her full name is a seminar-series line (a list item). The department BME profile that states her rank is already in `sources`.
No row had to be held for want of `sources`: PERSON-000097, -000925 and -001037 had only identifier URLs and each found a page.

## V-62 (scripts/validate.py, next to V-51)
Error on any people row whose `public_profile_url`, `lab_url` or `sources` matches the pre-push pattern; ignores `evidence_people`; adds nothing to
`validate_debt_baseline.json`. Four tests in `scripts/test_validate.py`: `?u=` profile, `/~` lab, scheme-less `/~` in sources must fail; a
widen-style `?u=` on an organizations row and the placeholder `u=<id>` must pass. Planted defect: with the error line neutralized, the three
failing-case tests fail (run once). On the base `people.csv` the rule fires on all 50 cells.

## Rule 15 self-refute
- self-refute: grain — 25 replaced rows checked, 0 changed. Each page is the person's own department or college page, naming the person on that page; none is a company-wide page. PERSON-001199's page styles the person "David Wang" and is flagged in its evidence note (the older row EVD-283152 already accepted it).
- self-refute: founding — 0 rows checked (no founding claims in this packet), 0 changed.
- self-refute: strength — 27 evidence rows checked, 3 kept at `supports_B` (the college news article for PERSON-000925, and the two scope rows). The 24 existence rows are `supports_A` because each is an own-site directory or profile entry that names the person and gives the rank, within the §4.13 ceiling for `own_site` and matching the existing EVD-3331xx rows on the same listing. (The first build used B everywhere and V-25 refused it for 24 tier-A rows; the reason for A is the page type, not the validator.) The UC chemistry and MSE entries (PERSON-000097, -000104) are list lines in a faculty directory and are the weakest A rows.
- self-refute: truncated quote — 27 quotes checked, 0 changed. Each quote runs to the end of the title and department (or the full sentence) and is checked in order in the stored page and again in the evidence note; contact details between segments are omitted and marked.
- self-refute: attribution — 29 rows checked, 4 changed to blank (000054, 000075, 000359, 001304). PERSON-001037: the same page's header reads Associate Professor while the overview sentence the row records says assistant; the note says so. PERSON-000850: the department page title is "Professor"; the row's role is research_professor (follow-up).

## Role-mismatch rule applied
A row is replaced when the page states the same person at the same institution and a title in the same rank family as the row, with any difference flagged in the evidence note and in the follow-ups (PERSON-000850, -001037, -001199). It is blanked when the page puts the person in a different status (emeritus: -000075; In Memoriam: -000359) or does not state a fact the old evidence took from the identifier URL (-000054, -001304).

## check.py
`python3 tasks/people-identifier-urls-2026-11-18/check.py` (reads stored pages under the S/persist path). Recounts the frame at base and now, proves 0 identifier URLs remain on people rows, every replacement has evidence rows whose quote is found in order in its sha256-checked stored page, no base evidence row changed, new ids only in EVD-396100..396199, people changes confined to 29 rows and 4 columns; then injects 6 defects and requires each to be caught. `build.py` is idempotent (second run: "nothing to do").

## Proposed follow-ups (not done here; owner or controller)
1. Pattern gap: other account-style identifiers pass the V-62 pattern: a `?unid=` Utah BME profile (PERSON-001304 sources), `researchdirectory.uc.edu/p/<shortname>` (PERSON-000104 sources and EVD-333190), `experts.colorado.edu/...fisid_<id>` (PERSON-000779). Rule for owner: widen the pattern or accept.
2. PERSON-000075: emeritus status vs role `professor`. PERSON-000359: deceased January 2026 vs a live row. PERSON-000850: role `research_professor` vs department page "Professor". PERSON-001037: LaTech header says Associate Professor, row says assistant. PERSON-001199: name form "David Wang" on the page vs "Qiang Wang".
3. `dev.uakron.edu` hosts were cited on two rows' sources (PERSON-000051, -000077); both are replaced.

## Not checked
No page was re-read beyond the quoted facts; specialties on rows other than 925 and 1199 were not re-verified (the old URLs carried no specialty evidence). The persist cache is outside the repo, so `check.py` needs it. Raw pages are not committed (only hashes and quotes).
