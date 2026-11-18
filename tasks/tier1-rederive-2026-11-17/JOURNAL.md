# tier1_qualifier re-derive (2026-11-17)

Integrator pass at the end of the 2026-11-16..17 wave. TRI registry links merged this week give 27 Ohio organizations a
verified TRI facility link, so the derivation adds `tri_reporter` to each. Nothing else changes.

    python3 scripts/derive_tier1.py --write --i-am-the-integrator   # preview: --packet (changes.csv here)

| Check | Result |
|-|-|
| Rows changed (unit: organization rows) | 27, all `gain:tri_reporter`, all in organizations_OH.csv |
| Columns changed | tier1_qualifier 27, tier1_qualifier_basis 27; no other column |
| Re-run preview after the write | 0 rows (idempotent) |
| `python3 scripts/validate.py` | OK |
| Row-loss guard vs `origin/main` | OK |

Rows: ORG-000082, ORG-000086, ORG-000115, ORG-000201, ORG-000224, ORG-000286, ORG-000302, ORG-000315, ORG-000319, ORG-000373, ORG-000403, ORG-000533, ORG-000534, ORG-000588, ORG-000589, ORG-000635, ORG-000638, ORG-000917, ORG-000927, ORG-000936, ORG-000957, ORG-001077, ORG-001133, ORG-001387, ORG-001609, ORG-001855, ORG-001859

Only the derived columns are touched (AGENTS §1).
