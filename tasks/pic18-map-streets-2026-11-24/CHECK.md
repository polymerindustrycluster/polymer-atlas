# Verification

Run from the repository root with the Atlas shared store mounted.

| Command | Result on the packet |
|---|---|
| `python3 -I tasks/pic18-map-streets-2026-11-24/build.py` | Rewrites BASIS.csv from the packets; 153 sites, 1 filled. |
| `python3 -I tasks/pic18-map-streets-2026-11-24/check.py` | PASS: one fill through every leg and the binding gate with capture replay, one changed cell, ledger equals the changed cells, release record equals the stored capture, 17 planted defects rejected. |
| `python3 scripts/validate.py` | OK. The cured V-68 baseline entry for SITE-000011 is removed. |
| `python3 -m unittest discover -s scripts -p test_validate.py -k test_v65_baseline_still_warns_only` | OK |
| `python3 scripts/check_evidence_binding.py --new-since origin/main` | 1 row, PASS `map_listing_street_bound`. |
| `python3 scripts/check_evidence_binding.py --verify-proofs origin/main --map-store <store>` | 1 row, PASS. |
| `python3 scripts/check_evidence_binding.py --provenance-since origin/main` | The row resolves to this task's check. |
| `python3 scripts/check_row_loss.py --base origin/main` | No keyed row removed. |

Planted defects, each rejected for its own reason: listing name not held, listing in another city, street differs from the second source, same-provider second source, unknown-origin second source, non-blank base street, closed listing, mailing role, PO box street, a `contradicts` row as second source, capture whose SHA-256 differs, listing ZIP differs from the held ZIP. A control (the same second source without `contradicts`) passes first, so the contradicts plant fails for the intended reason.
