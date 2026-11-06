# tier1_qualifier_basis refresh (2026-11-06)

Integrator pass. After the tier1 re-derive 2 (#241), Codex's review noted 37 organizations whose stored
`tier1_qualifier_basis` text lags its inputs, though every `tier1_qualifier` is correct (e.g. a national_footprint
basis listing six states when the site rows now give seven).

Command, previewed first without `--write` (identical `changes.csv`):

    python3 scripts/derive_tier1.py --packet tasks/tier1-basis-refresh-2026-11-06 --refresh-basis --write --i-am-the-integrator

| Check | Result |
|-|-|
| Rows changed (unit: organization rows) | 37, all `basis_refresh`; listed in `changes.csv` |
| `tier1_qualifier` values changed | 0 |
| Re-run of the refresh after writing | 0 further changes |
| `python3 scripts/validate.py` | OK |
| Row-loss guard vs `origin/main` | OK |

Only the derived column `tier1_qualifier_basis` is touched (AGENTS §1: refreshed by the derivation procedure, never
hand-edited).
