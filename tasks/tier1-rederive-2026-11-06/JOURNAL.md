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

## Re-run on current main (after the Codex clerk's finding)
Codex (R-codex-2) found the first run stale: waves merged after it added 4 more national_footprint gains, and 2 basis
strings went out of date. The branch now takes main's data files (main fb99047) and re-runs the derivation with
`--refresh-basis` (as in the 2026-11-02 precedent):

    python3 scripts/derive_tier1.py --packet tasks/tier1-rederive-2026-11-06 --write --refresh-basis --i-am-the-integrator

| Check | Result |
|-|-|
| Rows changed (unit: organization rows) | 98, across 27 shards: 58 `gain:national_footprint` + 40 `basis_refresh` |
| Columns changed vs main | `tier1_qualifier` (58 rows), `tier1_qualifier_basis` (98 rows); no other column |
| Dry run after write | 0 changes |
| `validate.py` | OK; 0 V-29 warnings |

More state waves will add footprint gains after this lands. The derivation is re-run whenever V-29 reports drift.
