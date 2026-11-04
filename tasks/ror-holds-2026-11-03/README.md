# ROR holds from the programs-db crosswalk (2026-11-03)

**Integrator for this pass:** claude-code. It resolves the 10 `ror_id` holds in
`tasks/programs-db-crosswalk-2026-11-03/holds.csv`. Each verdict was made from ROR's own record (api.ror.org), and
for a renamed college from the college's own page.

**Builders:** `find_ror.py` (ROR name search → `candidates.csv`) and `build_ror.py` (verdicts → `edits.csv`,
`evidence_append.csv`, `verdicts.csv`).

## Linked (3 ecosystem rows)

| Org | Institution | ROR | Basis |
|---|---|---|---|
| ORG-004775 | Purdue University Indianapolis | 0482ksk80 "Purdue University in Indianapolis" | name agrees; active, US-IN |
| ORG-004636 | Edmonds College | 00vhfbm88 "Edmonds Community College" | ROR carries the pre-2020 name; the college's own page records the April 2020 rename |
| ORG-004625 | WSU Tech | 01j933b41 "Wichita Area Technical College" | ROR carries the pre-2018 name; the college's own page says "WSU Tech, formerly Wichita Area Technical College" |

Each link adds the ROR record to `sources`; the two renames also add the rename page there and one `existence`
evidence row each (EVD-020270, EVD-020271; `own_site`, `supports_B`). No tier changes.

## Held (7 ecosystem rows), with the settling fact

| Org | Institution | Why held |
|---|---|---|
| ORG-002779 | Penn State Behrend | ROR 01ky71w68 is withdrawn; its successor is Penn State itself (04p491231). A campus never carries the parent's ROR (V-14). |
| ORG-002780 | Pennsylvania College of Technology | No ROR record. ROR's "Penn College" (03m7qwy32) is William Penn University, Oskaloosa IA. |
| ORG-004635 | The Landing School | No ROR record. |
| ORG-004672 | Connecticut State Community College | No ROR record for the 2023 merged college. The crosswalk candidate 014a8dd26 is Capital Community College, one of the 12 merged colleges, not the same organization. |
| ORG-004777 / 004778 / 004779 | Rutgers–Camden / New Brunswick / Newark | ROR has Rutgers University (05vt9qd57) but no campus records; the parent's ROR is not a campus's. |

A held row is settled when ROR adds a record of the institution's own.

## Verification

- Edits are hash-checked against the current cells. They were rehearsed on a temp copy of `data/`, then applied with
  `scripts/apply_p1_crm_scrub.py`.
- `python3 scripts/validate.py` passes.
