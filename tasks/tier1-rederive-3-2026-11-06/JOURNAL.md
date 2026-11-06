# tier1_qualifier re-derive 3 (2026-11-06)

Integrator pass after the dedupe-medium apply (#256): moving the Muncie IN plant under ORG-004865 Diamond Plastics
gave it active sites in IN, NE and TX, so the derivation adds `national_footprint`. #256's lane previewed exactly this
one gain and did not write it.

    python3 scripts/derive_tier1.py --packet tasks/tier1-rederive-3-2026-11-06 --write --i-am-the-integrator

| Check | Result |
|-|-|
| Rows changed (unit: organization rows) | 1: ORG-004865, `gain:national_footprint` |
| `python3 scripts/validate.py` | OK; V-29 drift warnings 1 → 0 |
| Row-loss guard vs `origin/main` | OK |

Only the derived columns are touched (AGENTS §1).
