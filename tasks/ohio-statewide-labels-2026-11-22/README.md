# ohio_statewide -> ohio_other for a named Ohio county outside PIC-18 — 2026-11-22

**Why:** `hq_in_scope` = `ohio_statewide` is outside the SCHEMA §4.4 enum and undefined. Owner round-13 ruling (2026-11-22, with "PIC-18 exactly"): the rows that still carry it with a named Ohio HQ county outside PIC-18 get `ohio_other`; rows with no county stay held. Built on `origin/main` 22b1109e. Unit: `organizations` rows, all statuses.

## Rule (`rules.py`)
`hq_in_scope` = `ohio_statewide`, `hq_state` = OH, `hq_county` a valid Ohio county (repo county shapes) not in PIC-18 (`scripts/regions.py`), and no non-closed Ohio site in the same city in a different county → `ohio_other`. Anything else is held and listed in `holds.csv`.

## Yield
**79** rows relabelled (frame: other Ohio). **5** held: no county (`holds.csv`, `hold_county_blank`). Zero rows are held for a PIC-18 county (the 10 in PIC-18 were relabelled `ne_ohio` by #470) or a county that looks wrong. After this PR no organization row carries `ohio_statewide` with a named county, and none carries `pic12`; 5 `ohio_statewide` remain.

## Check (`python3 tasks/ohio-statewide-labels-2026-11-22/check.py`)
Recomputes all 79 cells, an independent assertion (label, state, named county, not in PIC-18; recall: every `ohio_statewide` base row is a change or a listed hold), planted wrong/omission/overwrite fail, scratch apply with identical validator output and a cell-for-cell diff; 7 known-answer cases. No canary: 79 rows, one rule, one column.
