# Verification

Run from the repository root with the Atlas shared store mounted.

| Command | Result on the packet |
|---|---|
| `python3 -I tasks/pic18-street-gaps-2026-11-24/build.py` twice | First run applies the two shards. Second run writes zero shards. |
| `python3 -I tasks/pic18-street-gaps-2026-11-24/check.py` | Replays both raw filing rows and hashes. Verifies two street cells, one appended evidence row per fill, 153 held sites, row counts and the exact corrected ledger. |
| `python3 scripts/validate.py` | Validation passed. |
| `python3 -m unittest discover -s scripts -p test_validate.py -k test_v65_baseline_still_warns_only` | Passes after removing the cured SITE-000678 entry from the V-65 debt baseline. |
| `python3 scripts/check_evidence_binding.py --new-since origin/main` | Two new rows, both PASS. |
| `python3 scripts/check_evidence_binding.py --provenance-since origin/main` | Both evidence rows resolve to this task's check. |
| `python3 scripts/check_row_loss.py --base origin/main` | No keyed row removed. |

The check rejects six planted defects. They cover a different street, a mailing role, a registered-agent role, an omitted corrected claim, a duplicate corrected claim and a truncated CSV row. The verified input frame holds 879 active tier A–C PIC-18 site rows, of which 155 had a blank street on the pinned base.
