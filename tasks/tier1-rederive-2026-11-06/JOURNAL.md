# tier1_qualifier re-derive (2026-11-06)

Integrator pass. After the registry-links restore (#129) merged, `scripts/derive_tier1.py` reported 52 organizations
whose stored `tier1_qualifier` lags the derivation (V-29 drift). All 52 are `gain:national_footprint`: organizations
that reached active sites in 3 or more states through the November state waves. No organization loses a qualifier.
This confirms that no pass ran `--write` while the registry links were missing.

Command, rehearsed first on a copy of `data/` (identical `changes.csv`):

    python3 scripts/derive_tier1.py --packet tasks/tier1-rederive-2026-11-06 --write --i-am-the-integrator

| Check | Result |
|-|-|
| Rows changed (unit: organization rows) | 52, across 19 organization shards; listed in `changes.csv` |
| Change classes | 52 `gain:national_footprint` |
| `python3 scripts/validate.py` | OK; V-29 drift warnings 52 → 0 |
| Row-loss guard vs `origin/main` | OK |

Only the derived columns `tier1_qualifier` and `tier1_qualifier_basis` are touched (AGENTS §1: refreshed by the
derivation procedure, never hand-edited).
