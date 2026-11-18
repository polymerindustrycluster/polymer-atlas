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
| replaced with an identifier-free page + new evidence | **25** | 28 evidence rows, EVD-396100..396127 (24 existence at `supports_A`; at `supports_B`: 925 existence, 925 scope, 1199 scope, and 850's news-page title row) |
| URL blanked (old evidence stays the source) | **4** | PERSON-000054, -000075, -000359, -001304 |
| held (STILL_UNCERTAIN) | **0** | no row was left without a usable `sources` |

Only `public_profile_url`, `lab_url`, `sources` and `last_verified` changed, on those 29 rows. `last_verified` = 2026-11-18 on 23 of the 25
replaced rows (a page fetched today confirmed name, title, institution and the recorded role); it is unchanged on PERSON-000051 and -001037 (their pages do not establish the recorded role, see below) and on the 4 blanked rows (nothing was re-checked on them). Where a replaced row's `sources` lacked the new page it was appended, because the new evidence rows cite it.

## Per row (A = `/polymer/about-us/our-people` listing page 1, A2 = its `?currentPage=2`; all pages stored with sha256 in `witness.csv` / `manifest.csv`)
| Person | Action | Page (host / path) | How the page became fetchable (rule 14) | Evidence |
|---|---|---|---|---|
| 000043, 045, 046, 048, 049, 050, 057, 058, 078 | replaced | uakron.edu A | already a source on these rows | 396100-396105, 396109, 396110, 396114 |
| 000051, 052, 055, 061 | replaced | uakron.edu A2 | pagination link on the A page | 396106-396108, 396111 (052 answers EVD-333160; 051's claim narrowed: see below) |
| 000076 | replaced | uakron.edu `/engineering/me/our-people` | nav link on `/engineering/me/research/` (a source on PERSON-000077) | 396112 |
| 000077 | replaced | same, `?currentPage=2` | pagination link on the previous page | 396113 |
| 000079 | replaced | uakron.edu `/engineering/cbe/our-people/faculty` | search I ran: Zhou + department + Akron (uakron.edu) | 396115 |
| 000097 | replaced | artsci.uc.edu chemistry faculty directory | search: Simms + chemistry + Cincinnati (uc.edu) | 396116 |
| 000104 | replaced | ceas.uc.edu MSE faculty list | search: Shi + MSE + Cincinnati (uc.edu) | 396117 |
| 000779 | replaced (sources only) | colorado.edu `/mechanical/` faculty page | search: Long + mechanical engineering + CU Boulder | 396118 |
| 000850 | replaced | chem.fsu.edu department person page, plus news.fsu.edu 2025-07-11 item (states the recorded Distinguished Research Professor title) | search: Schlenoff + Lawton + FSU (both) | 396119, 396120 |
| 000882 | replaced (sources only) | chem.uci.edu people page | search: Guan + chemistry + UC Irvine | 396121 |
| 000925 | replaced | artsandsciences.fsu.edu faculty spotlight | search: Shanbhag + Scientific Computing + FSU | 396122-396123 (answers EVD-280034, -280035, -280105) |
| 001037 | replaced | latech.edu directory | search: Peters + chemical engineering + Louisiana Tech | 396124 (claim narrowed: see below) |
| 001132 | replaced (sources only) | buffalo.edu chemistry faculty page | already a source on the row | 396125 |
| 001199 | replaced (sources only) | engr.colostate.edu faculty page | already a source on the row | 396126-396127 (answers EVD-283153) |
Blanked: 000054, 000075, 000359, 001304 (reasons under Holds and blanks).

## Holds and blanks, each with its settling fact and the row's actual remaining provenance
Evidence counts are `evidence_people` rows at base; `check.py` prints them.
- **PERSON-000054 (blanked):** the listing states name and rank, but not the specialty that the old evidence row (EVD-280053) took from the identifier URL. Provenance: 4 base evidence rows, 3 of them (EVD-280052/053/113) cite the removed URL and stay; the fourth (EVD-333162) cites the listing. `sources` keeps 2 pages. Settles it: an identifier-free page stating that specialty.
- **PERSON-000075 (blanked):** the university's emeritus page styles him Distinguished Professor Emeritus; the row says professor. Provenance: 1 base evidence row (EVD-333171), on another source (the polymer-physics research page); none cites the removed URL. `sources` keeps 3 pages. Settles it: an owner call on emeritus rows.
- **PERSON-000359 (blanked):** the only identifier-free department page found lists him under In Memoriam; a search result I did not fetch reports his death in January 2026. Provenance: no `evidence_people` rows at all; `sources` keeps 1 page (that directory). A status change needs dated evidence (AGENTS §3) and is not this task.
- **PERSON-001304 (blanked):** the only identifier-free page found with her full name is a seminar-series line (a list item). Provenance: no `evidence_people` rows at all; `sources` keeps 1 page, the department BME profile that states her rank (its address carries an account-style `unid`, see follow-up 1).
No row was left with empty `sources`: PERSON-000097, -000925 and -001037 had only identifier URLs and each found a page.

## Rows whose page does not establish the recorded role (round-1 review, finding 1)
Evidence is narrowed to what the page states, the people `role` column is untouched, and `last_verified` is not bumped.
- **PERSON-000051 (EVD-396106):** the row says interim director; the listing gives an endowed professorship and names PERSON-000052 as director. Claim now: name, institution and endowed-professor title; director role not verified.
- **PERSON-001037 (EVD-396124):** the directory's title field says Associate Professor, its overview sentence says assistant. Claim now: name and institution; the recorded assistant rank is not established. Settles it: a dated page stating one rank.
- **PERSON-000850 (EVD-396119, -396120):** the department page lists professorships but not the research rank; a second FSU page (news item, 2025-07-11) states the recorded title, so the row stays replaced and its date is bumped (class `own_site`, `supports_B`: V-22 needs own_site for an existence claim).

## V-62 (scripts/validate.py, next to V-51)
Error on any people row whose `public_profile_url`, `lab_url` or `sources` matches the pre-push pattern, widened by an optional explicit port and with `#` ending the path (review finding 2: an account path behind `:443` was missed, and fragment text such as `#faq?u=x` was read as a query); ignores `evidence_people`; adds nothing to
`validate_debt_baseline.json`. Six tests in `scripts/test_validate.py`: `?u=` profile, `/~` lab, scheme-less `/~` in sources, `/~` behind an explicit port must fail; a
widen-style `?u=` on an organizations row, the placeholder `u=<id>`, and fragment text must pass. Planted defect: with the error line neutralized, the failing-case tests fail (run once). On the base `people.csv` the rule fires on all 50 cells.

## Rule 15 self-refute
- self-refute: grain — 25 replaced rows checked, 0 changed. Each page is the person's own department or college page, naming the person on that page; none is a company-wide page. PERSON-001199's page styles the person "David Wang" and is flagged in its evidence note (the older row EVD-283152 already accepted it).
- self-refute: founding — 0 rows checked (no founding claims in this packet), 0 changed.
- self-refute: strength — 28 evidence rows checked, 4 at `supports_B` (the college news article for PERSON-000925, the two scope rows, and the FSU news title row for PERSON-000850). The 24 existence rows are `supports_A` because each is an own-site directory or profile entry that names the person and gives the rank, within the §4.13 ceiling for `own_site` and matching the existing EVD-3331xx rows on the same listing. (The first build used B everywhere and V-25 refused it for 24 tier-A rows; the reason for A is the page type, not the validator.) The UC chemistry and MSE entries (PERSON-000097, -000104) are list lines in a faculty directory and are the weakest A rows.
- self-refute: truncated quote — 28 quotes checked, 0 changed. Each quote runs to the end of the title and department (or the full sentence) and is checked in order in the stored page and again in the evidence note; contact details between segments are omitted and marked.
- self-refute: attribution — 29 rows checked, 7 changed after review: 4 blanked (000054, 000075, 000359, 001304), 2 evidence claims narrowed with `last_verified` left unbumped (000051, 001037), 1 second page added so the recorded title is stated (000850). The page-level attribution of each quote is to the person's own institution.

## Role-mismatch rule applied
A row is replaced and re-dated only when the page (or a second page) states the same person at the same institution and the recorded title. Where the page states the person and institution but not the recorded role, the row is replaced, the evidence claim is narrowed to what the page states, the role column is left alone and the row is a follow-up (-000051, -001037). It is blanked when the page puts the person in a different status (emeritus: -000075; In Memoriam: -000359) or does not state a fact the old evidence took from the identifier URL (-000054, -001304). PERSON-001199's page styles the person "David Wang"; its image alt text links both name forms, and EVD-283152 already accepted it.

## check.py
`python3 tasks/people-identifier-urls-2026-11-18/check.py` (reads stored pages under the S/persist path). Recounts the frame at base and now, proves 0 identifier URLs remain on people rows, every replacement has evidence rows whose quote is found in order in its sha256-checked stored page, no base evidence row changed, new ids only in EVD-396100..396199, people changes confined to 29 rows and 4 columns; then injects 8 defects and requires each to be caught. It takes the intended outcome per row from `build.py` (not from which evidence survived), and binds each witness digest to its URL in the fetch manifest. `build.py` writes witness files, then evidence, then people last, so a failed write is recovered by re-running (tested with an injected append failure); a second run says "nothing to do".

## Proposed follow-ups (not done here; owner or controller)
1. Pattern gap: other account-style identifiers pass the V-62 pattern: a `?unid=` Utah BME profile (PERSON-001304 sources), `researchdirectory.uc.edu/p/<shortname>` (PERSON-000104 sources and EVD-333190), `experts.colorado.edu/...fisid_<id>` (PERSON-000779). Rule for owner: widen the pattern or accept.
2. Role or status mismatches, rows unchanged: PERSON-000051 (interim director not on the page; the page names PERSON-000052 as director), PERSON-001037 (title field Associate Professor vs overview assistant), PERSON-000075 (emeritus vs role `professor`), PERSON-000359 (deceased January 2026 per an unfetched search result vs a live row), PERSON-001199 (page name "David Wang" vs "Qiang Wang").
3. `dev.uakron.edu` hosts were cited on two rows' sources (PERSON-000051, -000077); both are replaced.

## Not checked
No page was re-read beyond the quoted facts; specialties on rows other than 925 and 1199 were not re-verified (the old URLs carried no specialty evidence). The persist cache is outside the repo, so `check.py` needs it. Raw pages are not committed (only hashes and quotes).
