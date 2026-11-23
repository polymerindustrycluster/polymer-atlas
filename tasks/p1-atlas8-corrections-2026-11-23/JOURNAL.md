# P1 application journal

Applied 2026-11-23 by atlas-p1-integrator-1 from main `f3c80b0a00d7adcb1be1347b67d2b2c5b280b4d8`. The integrator made private, byte-for-byte pre-pass backups of `data/sites_OH.csv`, `data/programs.csv` and `data/evidence_sites_OH.csv` before writing them in the isolated worktree. Packet and raw input checksums are recorded alongside this journal. `python3 scripts/atlas.py next-id EVD` returned EVD-483021. This pass appended EVD-483021 through EVD-483025.

| Check | Result |
| --- | --- |
| `lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/p1-atlas8-corrections-2026-11-23/check.py` | PASS. 701 in-scope reader verdicts and 1,407 rule re-derivations reconciled to 2,016 unique claim rows, 16 changed cells, five append-only evidence rows and 86 open keys. |
| `lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/validate.py` | PASS. 47,610 evidence rows checked alongside the canonical records and links. |
| `lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/check_row_loss.py --base origin/main` | PASS. Zero keyed row losses. |
| `python3 scripts/check_evidence_binding.py --verify-proofs origin/main` | PASS. Five new evidence rows judged, all PASS. |
| `python3 scripts/check_evidence_binding.py --provenance-since origin/main` | PASS. Five additions under the label for this replay folder. |

The replay rejected two planted defects in the isolated worktree. A claim for an unreviewed site failed the claim-ledger comparison. Replacing a corrected street with a wrong civic number failed the full data comparison. The original committed bytes were restored before the final push.

A second witness-link pass filled 19 blank IDs on verified claims. Each added ID is an existing observation on the same record and citation, with the applicable claim type and the published value stated in its detail. The replay passed again. The claim dispositions, claim counts and data delta are identical to the previous head.
