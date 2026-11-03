# Cleanup pass: duplicates, exact titles, nonexistent ROR ids, an email URL (2026-11-03)

**Integrator for this pass:** claude-code. The pass follows the review of passes 41–46 and applies the owner's decisions
taken in session on 2026-11-03 (multiple choice):
- duplicates: merge each into the older record;
- role titles: re-read the cited page;
- line endings: LF everywhere.

**Builder:** `build_cleanup.py`. Its docstring holds the rules; `edits.csv`, `removals.csv`, `inclusion_log_append.csv`
and `holds.csv` are its output.

## Applied

| Item | Rows | Rule |
|---|---:|---|
| Duplicate people merged and removed | 14 | Same person and same institution twice, the second copy created by pass 45. The older id is kept and the copy's row removed; its id is retired and never reused. The keeper takes the copy's extra sources (10), a personal profile URL where the keeper had a shared listing page (3), and a printed title where the keeper's was narrative (1). Each removal is logged in `data/inclusion_log.csv`. |
| `role_as_published` set to the exact printed title | 47 | Six cheap lanes re-read each record's cited pages (`tasks/role-title-recheck-2026-11-03/`). A title is applied only if all of these hold: the lane CONFIRMED it; it reads as a title, with no quotes, narrative, name or `\|`; its page is one the record already cites; and the page's rank agrees with the record's `role`. |
| Nonexistent ROR ids replaced | 6 | Bowling Green, Ohio U, Ferris State, UW–Stout, Grand Rapids CC and Pittsburg State. api.ror.org said "does not exist". Each was replaced by the programs-db crosswalk candidate, which verified active, US, same state, and name or domain agree. |
| Nonexistent ROR id cleared | 1 | UA Research Foundation (ORG-002104) is a sub-unit of the University of Akron. A sub-unit never carries the parent's ROR (V-14). |
| Email-bearing source URL dropped | 1 | PERSON-000366: a `…/zhaox@mit.edu` URL in `sources` (AGENTS.md §6). |

## Held (`holds.csv`, 214 title rows): no change made

| Reason | Rows |
|---|---:|
| Lane could not confirm a title | 151 |
| Page rank differs from the record's `role` | 45 |
| Lane line is not a clean title | 14 |
| Title page is not one the record cites | 4 |

- **Could not confirm:** mostly 403/503 responses, rate limits, or pages with no title line. Some hosts did not resolve in this session (nrel.gov, docs.nrel.gov). These are availability signals, not evidence.
- **Rank differs:** each disagreement needs one check to settle both `role` and the title together. The list includes possible promotions and possibly stale pages.

## Verification

- Every edit is hash-checked against the current cell.
- Removals check a whole-row hash.
- `python3 scripts/validate.py` passes.

## Follow-up: rank re-check of the 45 rank disagreements (owner decision 2026-11-03, option 2a)

Two cheap lanes re-read each person's current official pages (`tasks/role-rank-recheck-2026-11-03/`).

| Verdict | People | Action |
|---|---:|---|
| UPDATE | 7 | `role` and `role_as_published` changed together, as hash-checked edits |
| KEEP | 27 | The record's rank stands; the disagreeing page was stale or styled a named chair without a rank word |
| CANNOT_CONFIRM | 11 | Left as is; each row names the fact that would settle it |

The 7 updates:
- Tenhaeff: to associate professor.
- Riaz: to assistant professor.
- Foudazi, Cortes and Edwards: to professor.
- Liu: to associate professor.
- Sahoo: to research professor.

