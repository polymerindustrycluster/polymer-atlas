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
| replaced with an identifier-free page + new evidence | **23** | 26 evidence rows, EVD-396100..396125 (22 existence at `supports_A`; at `supports_B`: 925 existence, 925 scope, 1199 scope, and 850's news-page title row) |
| URL blanked (no new evidence; old evidence, where any, stays) | **6** | PERSON-000051, -000054, -000075, -000359, -001037, -001304 |
| held (STILL_UNCERTAIN) | **0** | see PERSON-001037 under Holds and blanks: its `sources` would have been empty, so the one identifier-free page found is kept as a plain source (needs the controller's call) |

Only `public_profile_url`, `lab_url`, `sources` and `last_verified` changed, on those 29 rows. `last_verified` = 2026-11-18 on the 23
replaced rows (a page fetched today confirmed name, title, institution and the recorded role); it is unchanged on the 6 blanked rows (nothing was re-checked
on them). Where a replaced row's `sources` lacked the new page it was appended, because the new evidence rows cite it.

## Per row (A = `/polymer/about-us/our-people` listing page 1, A2 = its `?currentPage=2`; all pages stored with sha256 in `witness.csv` / `manifest.csv`)
| Person | Action | Page (host / path) | How the page became fetchable (rule 14) | Evidence |
|---|---|---|---|---|
| 000043, 045, 046, 048, 049, 050, 057, 058, 078 | replaced | uakron.edu A | already a source on these rows | 396100-396105, 396108, 396109, 396113 |
| 000052, 055, 061 | replaced | uakron.edu A2 | pagination link on the A page | 396106, 396107, 396110 (052 answers EVD-333160) |
| 000076 | replaced | uakron.edu `/engineering/me/our-people` | nav link on `/engineering/me/research/` (a source on PERSON-000077) | 396111 |
| 000077 | replaced | same, `?currentPage=2` | pagination link on the previous page | 396112 |
| 000079 | replaced | uakron.edu `/engineering/cbe/our-people/faculty` | search I ran: Zhou + department + Akron (uakron.edu) | 396114 |
| 000097 | replaced | artsci.uc.edu chemistry faculty directory | search: Simms + chemistry + Cincinnati (uc.edu) | 396115 |
| 000104 | replaced | ceas.uc.edu MSE faculty list | search: Shi + MSE + Cincinnati (uc.edu) | 396116 |
| 000779 | replaced (sources only) | colorado.edu `/mechanical/` faculty page | search: Long + mechanical engineering + CU Boulder | 396117 |
| 000850 | replaced | chem.fsu.edu department person page, plus news.fsu.edu 2025-07-11 item (states the recorded Distinguished Research Professor title) | search: Schlenoff + Lawton + FSU (both) | 396118, 396119 |
| 000882 | replaced (sources only) | chem.uci.edu people page | search: Guan + chemistry + UC Irvine | 396120 |
| 000925 | replaced | artsandsciences.fsu.edu faculty spotlight | search: Shanbhag + Scientific Computing + FSU | 396121, 396122 (answers EVD-280034, -280035, -280105) |
| 001132 | replaced (sources only) | buffalo.edu chemistry faculty page | already a source on the row | 396123 |
| 001199 | replaced (sources only) | engr.colostate.edu faculty page | already a source on the row | 396124, 396125 (answers EVD-283153) |
Blanked: 000051, 000054, 000075, 000359, 001037, 001304 (reasons under Holds and blanks).

## Holds and blanks, each with its settling fact and the row's actual remaining provenance
Evidence counts are `evidence_people` rows at base; `check.py` prints them.
- **PERSON-000051 (blanked, round 2):** the listing gives an endowed professorship and names PERSON-000052 as director; no page states the interim director role the row records. Provenance: 1 base evidence row (EVD-333159, citing the listing); none cites the removed URLs. `sources` keeps 1 page, that listing. Settles it: a dated page stating the interim directorship.
- **PERSON-000054 (blanked):** the listing states name and rank, but not the specialty that the old evidence row (EVD-280053) took from the identifier URL. Provenance: 4 base evidence rows, 3 of them (EVD-280052/053/113) cite the removed URL and stay; the fourth (EVD-333162) cites the listing. `sources` keeps 2 pages. Settles it: an identifier-free page stating that specialty.
- **PERSON-000075 (blanked):** the university's emeritus page styles him Distinguished Professor Emeritus; the row says professor. Provenance: 1 base evidence row (EVD-333171), on another source (the polymer-physics research page); none cites the removed URL. `sources` keeps 3 pages. Settles it: an owner call on emeritus rows.
- **PERSON-000359 (blanked):** the only identifier-free department page found lists him under In Memoriam; a search result I did not fetch reports his death in January 2026. Provenance: no `evidence_people` rows at all; `sources` keeps 1 page (that directory). A status change needs dated evidence (AGENTS §3) and is not this task.
- **PERSON-001037 (blanked, round 2; NEEDS THE CONTROLLER'S CALL):** the only identifier-free page found (the university directory) has a title field (Associate Professor) that conflicts with its overview sentence (assistant professor), so it cannot settle the recorded rank. The row had no evidence rows and its only source was the identifier URL, so blanking would empty `sources`; the ruling's hold branch would instead keep the identifier URL, which fails V-62. I kept the directory page as a plain source (no evidence row, no role claim, `last_verified` unchanged) so `sources` is non-empty and V-62 passes. Settles it: a dated page stating one rank, or the owner choosing the hold branch.
- **PERSON-001304 (blanked):** the only identifier-free page found with her full name is a seminar-series line (a list item). Provenance: no `evidence_people` rows at all; `sources` keeps 1 page, the department BME profile that states her rank (its address carries an account-style `unid`, see follow-up 1).
PERSON-000097 and -000925 had only identifier URLs and each found a page; PERSON-000850 states its recorded title on a second page (class `own_site`, `supports_B`: V-22 needs `own_site` for an existence claim).

## V-62 (scripts/validate.py, next to V-51)
Error on any people row whose `public_profile_url`, `lab_url` or `sources` carries an account URL, decided by `scripts/people_url.py` (also used by `check.py`): each URL token is parsed with `urlsplit` (prefix `//` when there is no scheme); it fails on a query parameter `u` whose value starts with a letter or digit at any position, or a path segment starting `~` plus a letter or digit; the fragment is ignored. This replaced the round-1 regex, which missed an account in a second query parameter with no slash after the host and read a filename inside a fragment as a query. Ignores `evidence_people`; adds nothing to `validate_debt_baseline.json`. Eight tests in `scripts/test_validate.py`: `?u=` profile, `/~` lab, scheme-less `/~` in sources, `/~` behind an explicit port, an account in the second query parameter with no path must fail; a widen-style `?u=` on an organizations row, the placeholder `u=<id>`, and fragment text (two forms) must pass. Planted defect: with the error line neutralized, the failing-case tests fail (run once). On the base `people.csv` the rule fires on 29 rows and 50 cells, as the pre-push pattern does.

## Rule 15 self-refute
- self-refute: grain — 23 replaced rows checked, 0 changed. Each page is the person's own department or college page, naming the person on that page; none is a company-wide page. PERSON-001199's page styles the person "David Wang" and is flagged in its evidence note (the older row EVD-283152 already accepted it).
- self-refute: founding — 0 rows checked (no founding claims in this packet), 0 changed.
- self-refute: strength — 26 evidence rows checked, 4 at `supports_B` (the college news article for PERSON-000925, the two scope rows, and the FSU news title row for PERSON-000850). The 22 existence rows are `supports_A` because each is an own-site directory or profile entry that names the person and gives the rank, within the §4.13 ceiling for `own_site` and matching the existing EVD-3331xx rows on the same listing. (The first build used B everywhere and V-25 refused it for 24 tier-A rows in the first build; the reason for A is the page type, not the validator.) The UC chemistry and MSE entries (PERSON-000097, -000104) are list lines in a faculty directory and are the weakest A rows.
- self-refute: truncated quote — 26 quotes checked, 0 changed. Each quote runs to the end of the title and department (or the full sentence) and is checked in order in the stored page and again in the evidence note; contact details between segments are omitted and marked.
- self-refute: attribution — 29 rows checked, 8 changed after review: 6 blanked (000051, 000054, 000075, 000359, 001037, 001304) and 1 second page added so the recorded title is stated (000850); round 2 also made `check.py` compare each witness quote with the planned person's own quote. The page-level attribution of each quote is to the person's own institution.

## Role-mismatch rule applied
A row is replaced and re-dated only when the page (or a second page) states the same person at the same institution and the recorded title. Where no identifier-free page states the recorded role, the ruling's other branch applies and the URL is blanked, with the role column left alone (-000051, -001037, and -000054 where the specialty is missing). It is also blanked when the page puts the person in a different status (emeritus: -000075; In Memoriam: -000359). PERSON-001199's page styles the person "David Wang"; its image alt text links both name forms, and EVD-283152 already accepted it.

## check.py
`python3 tasks/people-identifier-urls-2026-11-18/check.py` (reads stored pages under the S/persist path). Recounts the frame at base and now (csv, and an independent raw-line count), proves 0 identifier URLs remain on people rows, every URL cell of every frame row equals its planned outcome (replaced with the planned URL, or blanked; other URLs preserved), each replacement's evidence rows and witness quotes equal the plan's own quote for that person, each quote is found in order in its sha256-checked stored page and its witness digest is bound to its URL in the fetch manifest, no base evidence row changed, new ids only in EVD-396100..396199, people changes confined to 29 rows and 4 columns; then injects 12 defects and requires each to be caught. `build.py` writes witness files, then evidence, then people last (both via atomic replace), so a failed write is recovered by re-running; a second run says "nothing to do".

## Proposed follow-ups (not done here; owner or controller)
1. Pattern gap: other account-style identifiers pass the V-62 pattern: a `?unid=` Utah BME profile (PERSON-001304 sources), `researchdirectory.uc.edu/p/<shortname>` (PERSON-000104 sources and EVD-333190), `experts.colorado.edu/...fisid_<id>` (PERSON-000779). Rule for owner: widen the rule or accept.
2. Role or status mismatches, role columns unchanged: PERSON-000051 (interim director not on the page; the page names PERSON-000052 as director), PERSON-001037 (title field Associate Professor vs overview assistant; controller's call above), PERSON-000075 (emeritus vs role `professor`), PERSON-000359 (deceased January 2026 per an unfetched search result vs a live row), PERSON-001199 (page name "David Wang" vs "Qiang Wang").
3. `dev.uakron.edu` hosts were cited on two rows' sources (PERSON-000051, -000077); both are now blanked or replaced.

## Not checked
No page was re-read beyond the quoted facts; specialties on rows other than 925 and 1199 were not re-verified (the old URLs carried no specialty evidence). The persist cache is outside the repo, so `check.py` needs it. Raw pages are not committed (only hashes and quotes).
