# entity_type from the legal name — 2026-11-22 (applied in this PR, both Ohio frames)

**Why:** the company-owner review (19 of 20 sampled PIC-18 records had `entity_type` = `unknown` beside a legal name ending in LLC, Inc. or Corp.).
Owner rulings 2026-11-22: "Add 'corporation'" (a plain `corporation` value, SCHEMA v1.19.3). Built on `origin/main` 22b1109e (`BASE_REF`). Unit: `organizations` rows, all statuses.

## Rule (`rules.py`, used by `build.py` and `check.py`)
Fill `entity_type` only where the cell is blank or `unknown`, from the **final** suffix of `legal_name`:

| Suffix at the end of `legal_name` | Value |
|---|---|
| LLC, L.L.C., Limited Liability Company | `llc` |
| LP, L.P., LLP, L.L.P., LLLP, Limited (Liability) Partnership | `partnership` |
| Inc, Inc., Incorporated, Corp, Corp., Corporation | `corporation` |

`corporation` is not `corporation_public` or `corporation_private`: public or private is never guessed. **Held:** Co / Company / Ltd / Limited (stay `unknown`); no suffix; a second legal form in the name
("Foo Co., LLC", "Foo Corp. Inc."; "Co" or "Company" inside a name before Inc is a name word); a dba / "/" / parenthesis form; a non-US or unplaced HQ; a non-empty `stock_ticker` (a ticker is a lead for
`corporation_public`, which is the owner's to rule, not a suffix fact); a cell that already holds a value. No `ownership_type`, parent or subsidiary status is touched.

## Yield (unit: organizations rows; frame = HQ county or any non-closed site county in PIC-18 / other Ohio)
| Frame | `corporation` | `llc` | `partnership` | total |
|---|---|---|---|---|
| PIC-18 | **456** | 110 | 4 | **570** |
| other Ohio | **327** | 118 | 0 | **445** |
Not in the packet: 152 LLC/LP rows outside Ohio, and their corporation counterparts.

## Reconciling the earlier "590 PIC-18 corporate-suffix holds" against "570 rows in held_corporate_suffix.csv"
Unit: PIC-18-frame organizations rows whose legal name ends in a corporate-style word (Inc, Corp, Co, Company, Ltd, Limited and variants), on the same base data:
**595** such rows; minus 5 that are also dba/parenthesis forms = **590** (the number the first README gave, counted across every `entity_type` value); of those 590, 20 already hold a value (14 `corporation_private`, 6 `corporation_public`) leaving **570** with a blank or `unknown` cell — the rows the earlier `held_corporate_suffix.csv` listed (570 in PIC-18; the file's 1,582 rows are all frames). The first README mislabelled 590 as "held" without saying it counted the 20.
Fate of the 570: **456 filled `corporation`**, 105 stay `unknown` (Co, Company, Ltd, Limited), 6 held for a ticker, 3 held as foreign/unplaced. The 20 that already hold a value are not changed.

## Canary (25 rows, `canary-25/frame.csv`, `python3 canary.py`)
19 fills (13 PIC-18 `corporation`, 3 `llc`, 1 `partnership`, 2 other-Ohio `corporation`), 3 Co/Company held (Neff-Perkins Company, Buckeye Rubber & Packing Co., Ashtabula Rubber Co.), 1 ticker held (PPG Industries, Inc.), 1 conflicting forms (Southwest Gasket Company, LLC), 1 dba (OEM/Miller).
Read as the owner: every `corporation` fill is a name that says Inc or Corp and nothing in its description contradicts it; the two the first canary flagged still stand (ORG-000550/ORG-000551 become `partnership` from LLP/LP). Held rows read right: a person reading "Buckeye Rubber & Packing Co." cannot tell the form either, and PPG's ticker makes `corporation_public` the likely value, which the rule does not guess.

## Check (`python3 tasks/entity-type-from-name-2026-11-22/check.py`)
Recomputes all 1,015 cells with `rules.py` **and** an independent assertion (every change is a blank/unknown cell whose name ends in a standalone LLC, LP or Inc/Corp form, with an `after` that is in `docs/schema/vocab.json`; every such Ohio-frame row is a change or a listed hold), fails on a planted wrong value, omission and overwrite, requires blank-or-unknown `before`, scratch apply with validator output identical to base and a cell-for-cell diff. The working-tree check tolerates cells of other columns (the `ohio-statewide-labels` packet shares the shards). 24 known-answer cases cover every hold.
`entity_type` is not validated by `scripts/validate.py` today (no V-rule reads it): this PR does not add one.

## Applying
`BASE_REF` pins the commit built on; rebuild on the then-current main (`python3 build.py`, `check.py`) if anything merges first. `common.apply_changes` refuses any cell whose current value is not the packet's `before`.
Not checked: legal names are taken as recorded; no row was compared against a source.
