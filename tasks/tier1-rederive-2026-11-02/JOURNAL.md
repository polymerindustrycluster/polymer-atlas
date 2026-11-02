# Pass journal: tier1_qualifier re-derivation (2026-11-02)

**Integrator for this pass:** claude-code. The repo owner asked for this pass in
session on 2026-11-02. It goes in as a small single-purpose data PR (AGENTS.md
§2 rule 4), not a campaign push.
**Base:** `main` at `648c109` (re-checked against `origin/main` right before
applying; unchanged).
**Scope, fixed before applying:** exactly the 53 organization rows in
`changes.csv`. Only `tier1_qualifier` and `tier1_qualifier_basis` change. No
other column, row, file, or ID is touched.

## Pre-pass backups (sha256 of the files as held at `648c109`)

| file | sha256 before | sha256 after |
|---|---|---|
| `data/organizations_OH.csv` | `55c9e722e206018f75e72d76ad5f04f9c145450165452db087e17f81bb887202` | `a8d9952450e0b94f190e0819c0db7315395973b1928926e8874e1a35fe5b27ee` |
| `data/organizations_TN.csv` | `3d1b8ae00e22a1cd0a8a53639c4d52cd146b89ba6ebac4753c660610ce8eab6e` | `3f264cf5102b64447562321ba3ba1bfc37ac47e4af66413efb68e3c6b55aaf88` |
| `data/organizations_TX.csv` | `4813a8811caa8bcb9c61f908bf023e720f890e7d288f934e9ad673bd8643d0ea` | `e81e97124d368bbd3db7efb6e6284cd04cde2de6d426d801a1dc94dbc6d2d9bd` |

The pre-pass files are recoverable byte-for-byte from `648c109`.

## Steps

1. Rehearsed on a copy of `data/`:
   `derive_tier1.py --data-dir <copy> --write --refresh-basis` applied 53 row
   changes across 3 files. The validator then passed with 0 V-29 drift warnings.
2. Applied the same command to `data/` with `--i-am-the-integrator`.
3. Checked the applied diff against `changes.csv`: the same 53 organization IDs,
   the same new values, and only the two derived columns differ.
4. Ran `python3 scripts/validate.py` and got **OK — validation passed**.
   - Warnings went from 157 to 109. The 48 removed are all V-29 qualifier drift.
   - The 5 basis-only refreshes never raised a warning.
5. Ran `python3 -m unittest discover -s scripts -p 'test_*.py'`: all tests pass.
6. Re-ran `derive_tier1.py --refresh-basis` in check mode: 0 drift and 0 stale
   basis clauses.

## Changed rows (organization rows)

| change_class | rows |
|---|---|
| `lose:employees_250plus` | 41 |
| `gain:employees_250plus` | 7 |
| `basis_refresh` | 5 |
| **total** | **53** (OH shard 51, TN 1, TX 1) |

The per-row old and new values are in `changes.csv`. The gain/lose rows match
`tasks/p1-crm-scrub-2026-11-01/band_actions.csv` (`stored_in_250plus` ≠
`new_in_250plus`) ID-for-ID.

## Not done in this pass

- **No evidence rows.** The fields are derived, not claims.
- **`last_edited_by` not stamped.** See README.
- **No band research.** Lost bands are a separate research lane in QUEUE.
- **Not campaign mode, so no snapshot sync-log entry.**
