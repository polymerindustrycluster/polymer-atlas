# tier1_qualifier re-derive 2 (2026-11-06)

Integrator pass at campaign end. `scripts/derive_tier1.py` reported 21 organizations whose stored `tier1_qualifier`
lags the derivation (V-29 drift) after the 2026-11-06 merges.

Command, previewed first without `--write` (identical `changes.csv`):

    python3 scripts/derive_tier1.py --packet tasks/tier1-rederive-2-2026-11-06 --write --i-am-the-integrator

| Check | Result |
|-|-|
| Rows changed (unit: organization rows) | 21; listed in `changes.csv` |
| Change classes | 19 `gain:national_footprint`, 2 `lose:national_footprint` |
| `python3 scripts/validate.py` | OK; V-29 drift warnings 21 → 0 |
| Row-loss guard vs `origin/main` | OK |

The two losses were checked by hand before writing:
- ORG-001336 Yokohama TWS North America: its Spartanburg SC plant (SITE-012023) is `closed` on dated issuer evidence
  added 2026-11-06, leaving active sites in IA and OH only (2 states).
- ORG-002260 J-M Manufacturing Co. Inc.: merged into ORG-002261 at integration pass 18; it holds no active site.

Only the derived columns `tier1_qualifier` and `tier1_qualifier_basis` are touched (AGENTS §1: refreshed by the
derivation procedure, never hand-edited).
