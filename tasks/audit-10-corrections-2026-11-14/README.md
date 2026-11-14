# Blind audit 10 corrections (2026-11-14)

Applies the two confirmed FIELD_ERRORs from blind audit 10 (PR #331, `docs/reviews/BLIND_AUDIT_10_2026-11-14.md`).
Both were re-fetched by the controller before applying.

| Record(s) | Field | Before | After | Source (fetched 2026-11-14) |
|-|-|-|-|-|
| 20 rows of EVT-000046 (TPO 2026), EVP-001278..EVP-001290 and EVP-001292..EVP-001298 | `edition_dates` | 2026-09-28 to 2026-10-01 | 2026-09-28 to 2026-09-30 | Organizer schedule PDF (sha256 337fadd0…), Monday 9/28 to Wednesday 9/30, no Thursday; October 1 is only the hotel-block end. Source added to each row. |
| PROG-000314 MONET | `url`, `public_door_url` | https://monet.duke.edu/ (NXDOMAIN) | https://www.monetcci.org/ | monetcci.org (HTTP 200); Duke's 2026 Phase II release links it |
| PROG-000314 MONET | `description_1line` partner list | … UIUC, Michigan and Washington | … Morehouse College, UC San Diego, UIUC and Washington | monetcci.org/our-team: Morehouse College listed; Michigan appears only as former members marked alumni |
| ORG-004691 (generated) | `polymer_program_url` | https://monet.duke.edu/ | https://www.monetcci.org/ | §4.11 rollup recomputed with validate.py's V-16 rule |

Only the audited sample row EVP-001297 was graded; the other 19 rows are the same edition's dates from the same
harvest, so the same fact corrects them. The 10 older EVT-000046 rows already read "September 28-30, 2026".
`specialty_materials=thermosets` on PROG-000314 stands (the NSF CCI page states it). Rows changed (unit: data rows):
20 participation rows, 1 program row, 1 ecosystem row. No evidence row edited; no `last_verified` changed, because
only these fields were re-checked.

Builder: `python3 tasks/audit-10-corrections-2026-11-14/build.py --apply` (idempotent; a second run changes 0 cells).
Checks: `python3 scripts/validate.py` OK; `python3 scripts/check_row_loss.py --base origin/main` OK.
