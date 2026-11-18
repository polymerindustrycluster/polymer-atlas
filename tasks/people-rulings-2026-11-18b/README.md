# People identifiers and people status: owner rulings 2026-11-18b items 3 and 6 (SCHEMA v1.15, V-62 widened, V-64)

Branch `agent/claude-code/people-rulings-2026-11-18b`. Base `0720cc06`. No identifier URL is written out below: rows are named by person ID,
and the forms are described ("the unid form", "the UC `/p/` form"). Rulings: `tasks/owner-rulings-2026-11-18b/README.md` (PR #392).

## Frame (unit: `people.csv` rows with an identifier URL in `public_profile_url`, `lab_url` or `sources`)
At base: **9 rows** = 3 with the unid form (PERSON-000941, -001303, -001304) + 6 with the UC `/p/` form (PERSON-000104, -002009, -002010, -002011, -002111, -002112);
the ruling counted the same 3 + 6 at e1df30e4, so nothing changed. `check.py` recounts by the urlsplit rule and by an independent raw-text count (both 9) and shows
the pre-widening V-62 (PR #379) finds 0 of them. `evidence_people`: **13** rows cite the UC form (0 cite the unid form); none was edited. `fisid_<id>` rows (5) stay accepted.

## Applied counts
| Outcome | People rows | Detail |
|---|---|---|
| replaced with an identifier-free page + 1 new evidence row | **7** | PERSON-000941, -001303, -001304, -002009, -002010, -002111, -002112; EVD-396900..396906, all `existence`, `own_site`, `supports_A` |
| identifier URL removed, no new evidence | **2** | PERSON-000104 (its identifier-free page already carries EVD-396116 from #379), PERSON-002011 (see Holds) |
| held with the identifier left in place | **0** | see "Holds and decisions for the controller" |
| `status` / `status_date` | 1517 rows | two blank columns added last; **0** rows set |

Only `public_profile_url`, `lab_url`, `sources` and `last_verified` changed on the 9 rows (`last_verified` = 2026-11-18 on the 7 replaced rows; unchanged on the other 2),
plus the two new blank columns on every row (so every `people.csv` line differs by two trailing commas).

## Per row (all pages stored with sha256 under S/persist/people-rulings-2026-11-18b/, hashes in `witness.csv` / `manifest.csv`)
| Person | Action | Page | How the page became fetchable (rule 14) | Evidence |
|---|---|---|---|---|
| 000941 | replaced | bioscience.utah.edu faculty page | already in the row's `sources` | 396900 |
| 001303 | replaced | mse.utah.edu faculty list | already in the row's `sources` | 396901 |
| 001304 | replaced (sources only) | kramerlab.bme.utah.edu "About" page | search I ran: Jessica Kramer Stratton + biomedical engineering + Utah | 396902 |
| 002009 | replaced | ceas.uc.edu BME people page | search I ran (allowed_domains uc.edu): John Martin + biomedical engineering + Cincinnati | 396903 |
| 002010 | replaced | ceas.uc.edu chemical-environmental engineering people page | already in PERSON-002112's `sources` | 396904 |
| 002111 | replaced | artsci.uc.edu chemistry directory | already in the row's `sources` | 396905 |
| 002112 | replaced | ceas.uc.edu chemical-environmental engineering people page | already in the row's `sources` | 396906 |
| 000104 | identifier source dropped | (no new page) | n/a | none new; two other sources remain |
| 002011 | identifier removed, page kept as plain source | same CE people page | already in PERSON-002112's `sources` | none |
Each new evidence row's note carries its quote, the page-location route, the stored-page hash and "answers EVD-... (unedited)" for the old rows citing the identifier URL.

## Holds and decisions for the controller
- **PERSON-002011 (Dong; controller confirmed 2026-11-18).** The department page names him department head and holder of an eminent-scholar chair, and never says "Professor"; the row records Professor of Chemical Engineering.
  No identifier-free page states the rank, so no evidence row. The row's only source was the identifier URL, so a hold (identifier left in place) fails V-62 and blanking alone empties `sources`. I followed the PR #379 PERSON-001037 precedent
  (controller-confirmed 2026-11-18): the identifier is removed and the department page stays as a plain source, no role claim, `last_verified` unchanged. The kept page is identifier-free, names him at the institution and was reached by a rule-14 route (a source on PERSON-002112); the controller confirmed this disposition over the brief's hold branch, which would keep a V-62 failure.
  Settles it: a current identifier-free page stating the rank (the UC directory's own page does, but it is the identifier URL).
- **PERSON-001304 / PERSON-000941 look like one person** (same account; names "Jessica Kramer Stratton" and "Jessica R. Kramer"; the lab page styles "Dr. Jessica R. Kramer Stratton"). Not merged (AGENTS §3: when in doubt, do not merge); follow-up below.
- **PERSON-000359 (item 6): no dated death source was fetched, so `status` stays blank.** The department people page lists "Sandy Asher" under In Memoriam, with no date. The department notice (fetched) prints the services line "Wednesday, January 21" with no year,
  and no printed date of death. A funeral-home obituary page returned by search (for the name) did not render its body to my fetches (curl or the extraction tool): the page I stored is the chapel's generic obituary list. A search-result summary reports an obituary dated January 16, 2026 and services January 21, 2026;
  I did not fetch that text, so under rule 14 it is a lead, not evidence (and a weekday-matches-2026 inference is not a date).
  Settles it: a fetched page that prints the full date of death (the chapel's obituary entry body, or a university notice or named-outlet obituary with a date). Then `status=deceased`, `status_date` = that date, one `liveness` evidence row observed on or after it.

## Status semantics (controller ruling 2026-11-18)
`status_date` is the date of the status event the source states (the date of death), as on organizations and events. V-64: both blank, or `status` in {active, deceased} with a valid ISO `status_date` (a month or year alone cannot be stored);
`deceased` needs an `evidence_people` row for the person quoting the death with `observed_date` on or after `status_date`; `active` with a date needs no evidence-date check. (My first build read the brief's "on or before" literally; the controller ruled that wrong and it is reversed here.) Nothing populates it yet.

## V-62 widening and V-64 (scripts/people_url.py, scripts/validate.py)
V-62 now also fails a query parameter `unid` whose value starts with a letter or digit, and, on researchdirectory.uc.edu, a path segment `p` followed by a segment starting with a letter or digit; `fisid_<id>` and placeholders (`unid=<id>`, `/p/<shortname>`) pass.
V-64 (people status): as under Status semantics. Tests in `scripts/test_validate.py`:
5 for V-62 (unid in the profile URL, unid as the second query parameter in `sources`, UC `/p/` in `sources` fail; `fisid_123456` + placeholders pass; a `p` segment on another host passes) and 8 for V-64 (including: deceased with no evidence row fails; evidence observed before `status_date` fails; observed on or after passes; a bad status, a non-ISO or missing date fail; `active` with a date passes).
Planted defect: removing the two new alternatives from `people_url.py` makes the three failing-case V-62 tests fail (run once; output in the PR body).

## Rule 15 self-refute
- self-refute: grain — 7 replaced rows checked, 0 changed. Each page is the person's own department, college or lab page and names that person; PERSON-001304 uses the lab page that styles the same full name as the row.
- self-refute: founding — 0 rows checked (no founding claims), 0 changed.
- self-refute: strength — 7 evidence rows checked, 0 changed. All are `existence` at `supports_A` on `own_site` directory or faculty-list entries; V-25 accepts them. The four UC and Utah list lines are the weakest A rows.
- self-refute: truncated quote — 7 quotes checked, 0 changed. Each runs through the title (and the department where the page prints it); checked in order in the stored page and again in the note; contact details omitted.
- self-refute: attribution — 9 rows checked, 2 changed after review: PERSON-002011 got no evidence row (page does not state the rank) and PERSON-000104 got none (already evidenced); PERSON-000359 left blank (no dated source fetched).

## check.py
`python3 tasks/people-rulings-2026-11-18b/check.py` (reads stored pages under the S/persist path). Recounts the frame at base and now (urlsplit rule and an independent raw count), shows the old rule finds 0, proves 0 identifier URLs remain, the 13 UC-form evidence rows are unedited,
no base evidence row changed, new ids only in EVD-396900..396949, every quote is in its sha256-checked page, people changes are confined to the frame rows' 4 columns plus the two blank new columns, every status cell is blank, PERSON-000359 unchanged;
then injects 10 defects (identifier left on a row, old evidence edited, quote not on the page, write outside scope on a frame row and on a non-frame row, status set on an existing row, evidence id outside the block, replacement without evidence, an unaffected source dropped, evidence given to a no-evidence row) and requires each caught.
`build.py` is idempotent: a second run says "nothing to do".

## Proposed follow-ups (not done here)
1. Possible duplicate: PERSON-000941 and PERSON-001304 (same Utah account, same person). Dedupe pass or owner call.
2. `PEOPLE_PUBLIC_COLUMNS` (`scripts/atlas_mcp_server.py`) and `build_site.py` do not yet carry `status`; once a row is `deceased`, surface it there.
3. PERSON-000359: re-run the death-source fetch when a rendered obituary page or a dated university notice is reachable (see settling fact above).
4. PERSON-002011 rank: re-verify against a current page stating the rank.

## Not checked
Specialties on the replaced rows were not re-verified (the old evidence rows for scope stay). No page was re-read beyond the quoted facts. Raw pages are not committed; the persist cache is outside the repo, so `check.py` needs it.
