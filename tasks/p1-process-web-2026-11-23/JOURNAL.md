# P1 process application journal

Base `0b191fe6`. The integrator made private byte-for-byte pre-pass backups of the four Ohio data shards and `archive_links.csv`. `scripts/atlas.py next-id EVD` returned EVD-483026. Final mint EVD-483026 through EVD-483039. Every change to an existing Atlas row is a blank `processes` fill.

The archived route followed the owner's round 21 authenticated Save Page Now ruling. Ten jobs returned timestamps. The Pioneer refs predate the mint because Save Page Now deduplicated to November 16 captures, whose exact archived bodies preserve both reviewed quotes. The integrator independently replayed the cited pages. Polymer Packaging uses its existing November 16 capture.

The Technoform archive carries the exact quote at offset 276 and its stable decoded hash attested by Sonnet on November 23. It is stored in the controller's immutable Wayback provenance folder. The other proof inputs use the prior private capture folder. The held Dudick archive had 51 extracted characters with no company or process wording. The two Blair Rubber rows remain held under the controller's earlier decision on byte drift.

| Check | Result |
| --- | --- |
| `lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/p1-process-web-2026-11-23/check.py` | PASS. Fourteen proofs and archive links, eleven process cell fills and four held proposals. A planted one-character proof offset failed. |
| `lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/validate.py` | PASS. The final mint has no V-66 errors. |
| `lockf -k /tmp/polymer-atlas-heavy.lock python3 scripts/check_row_loss.py --base origin/main` | PASS. No keyed row lost. |
| Main binding checker on a local two-parent merge preview | PASS. All 14 decoded byte proofs replayed from their actual routes. |
| `python3 scripts/check_evidence_binding.py --provenance-since origin/main` and `python3 scripts/check_account_urls.py` | PASS. The new evidence resolves to the task's replay and no account URL was found. |

The PIC-18 coverage check reproduced the base denominator of 794 and the movement from 320 to 312 process-unknown owners. No unrelated record attributes changed.
