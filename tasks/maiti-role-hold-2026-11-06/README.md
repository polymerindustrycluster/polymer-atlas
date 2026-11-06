# Maiti role hold (2026-11-06)

Owner ruling in session, 2026-11-06: "Deputy Group Leader" does not fold to `group_leader` (SCHEMA v1.11.1, §4.9).
PR #149 had mapped PERSON-000621 Amitesh Maiti's published title "Deputy Group Leader, Multiscale Modeling" to
`group_leader` without a ruling; Kroonblawd was withdrawn from #235 for the same mapping.

| Record | Column | Before | After |
|-|-|-|-|
| PERSON-000621 | `role` | `group_leader` | `research_scientist` (its value before PR #149) |

`role_as_published` keeps the exact current title. No evidence row is edited (append-only); the title evidence
stays true. One people row changes; no other data file is touched.

Checks: `python3 scripts/validate.py` OK; `python3 scripts/check_row_loss.py --base origin/main` OK.
