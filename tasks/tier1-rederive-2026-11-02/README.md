# tier1_qualifier re-derivation packet (2026-11-02)

**Lane:** Claude Code, tooling + packet only. No `data/` edits, no IDs allocated.
**Pinned base:** `main` at `648c109` (Pass 40c). If `data/` has moved, re-run the
script instead of trusting `changes.csv`; it derives from whatever tree it reads.

## Why

Pass 40a's commit message says "tier1 re-derived", but the stored column was not
refreshed. Before pass 40 the validator reported **0** V-29 drift warnings. At
`648c109` it reports **48**. These are exactly the organizations the P1 packet
predicted would cross the 250-employee line once its band edits landed
(`tasks/p1-crm-scrub-2026-11-01/REPORT.md` and `band_actions.csv`:
`stored_in_250plus` ≠ `new_in_250plus`). The reconciliation is ID-for-ID: the 48
organization IDs here equal the 48 that `band_actions.csv` predicts, with the
same gain/lose direction for each (AGENTS.md §2 rule 10c).

The repo had no script that writes the derivation. The rules lived only inside
`scripts/validate.py` (`derive_tier1_set`), which checks drift but never refreshes
the column. This packet adds `scripts/derive_tier1.py`.

## What changes (organization rows, all shards)

| change_class | organization rows | cause |
|---|---|---|
| `lose:employees_250plus` | 41 | P1 band CLEAR (30) or REPLACE below 250 (11) |
| `gain:employees_250plus` | 7 | P1 band REPLACE into 250+ |
| `basis_refresh` (qualifier set unchanged) | 5 | stale basis text, listed below |
| **total** | **53** | 51 in `organizations_OH.csv`, 1 in `organizations_TN.csv`, 1 in `organizations_TX.csv` |

The `basis_refresh` rows:
- **ORG-000846, ORG-001328, ORG-001425:** P1 REPLACE moved the Ohio band within 250+, so the basis clause still quotes the old band.
- **ORG-000132, ORG-003067:** held non-closed sites now span fewer states than the `national_footprint` basis says (12→8 and 11→7). Sites were repointed in pass 29 and the basis was not regenerated.

Only `tier1_qualifier` and `tier1_qualifier_basis` change. Every other column and
every other row stays byte-identical (the script verifies the csv round-trip
before writing).

`changes.csv` lists every changed row with old and new values for the pass
journal (SCHEMA §4.4: "changed rows are listed in the pass journal").
`check_output.txt` is the check-mode run that produced it.

## Apply (integrator of record)

```bash
cp -r data /tmp/atlas_t1 && python3 scripts/derive_tier1.py --data-dir /tmp/atlas_t1 --write --refresh-basis
ATLAS_DATA_DIR=/tmp/atlas_t1 python3 scripts/validate.py   # expect: passed, zero "tier1_qualifier drift" warnings
python3 scripts/derive_tier1.py --write --refresh-basis --i-am-the-integrator
python3 scripts/validate.py
```

Drop `--refresh-basis` to fix only the 48 drift rows and leave the 5 stale basis
strings. The parity test (`scripts/test_derive_tier1.py`) runs the full refresh on
a copy of `data/` and requires zero V-29 drift from the validator.

## Not in scope

- **Re-sourcing lost bands.** Several large multi-state parents lose
  `employees_250plus` because no public Ohio band is held for them (P1 REPORT).
  Restoring them is a research lane (OSHA ITA / inspection per Ohio
  establishment), under the R13 precedence.
- **`last_edited_by`.** Not touched (`apply_p1_crm_scrub.py` does not stamp it either). Whether a
  derived-field refresh stamps it is the integrator's call.
