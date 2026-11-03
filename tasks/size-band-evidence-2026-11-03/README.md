# Size-band evidence backfill (2026-11-03)

**Owner ruling:** B-BAND (a), 2026-11-03 (`tasks/OWNER_BATTERY_2026-11-03.md`). The integrator for this pass is
claude-code.

## Applied

| Change | Rows | Unit and filter |
|-|-:|-|
| `docs/SCHEMA.md` §4.13 `claim_type` gains `size_band`, plus a revision-log entry | | Source classes `government_filing` or `own_site`; ceiling `supports_B`; not a must-have claim |
| `scripts/validate.py` V-22 enforces the classes and ceiling. `docs/schema/vocab.json` is regenerated, and `scripts/audit_evidence_coverage.py` accepts the new type | | |
| `data/evidence_{sites,organizations}_<TAG>.csv` | +1,996 (EVD-020280 to EVD-022275) | One `size_band` row per band applied on 2026-11-02 (`band_updates.csv` rows with status APPLY and action fill), across 49 shards |

By source:

| Source | Evidence rows |
|-|-:|
| OSHA ITA Form 300A | 1,384 |
| OSHA inspection | 334 |
| Form 5500 active participants | 278 |

Each row traces to its source packet row, through `packet_refs` and the packet's `band_proposals.csv`. A row is
written only when the record still carries that band in `employee_band_site` or `employee_band_ohio`. 0 were held.

EVD ids start above EVD-020279, the highest id used by open PRs (#26 and #35).

`python scripts/validate.py` exits 0. The unit tests (`python -m unittest discover -s scripts -p "test_*.py"`) also
exit 0.

## Rebuild

`python3 tasks/size-band-evidence-2026-11-03/build_evidence.py --data-dir <pre-pass data> --apply`
