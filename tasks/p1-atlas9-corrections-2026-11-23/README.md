# ATLAS-9 PIC-18 corrections

Built by: Codex GPT-6.2 Sol
Integrator: atlas-p1-integrator-1
Base: `24f71798`

The first packet covers 234 evidence IDs from the PIC-18 failed-screen queue.
The independent reread covers the 37 approved cross-family assignments. All
37 first received VERIFIED. The reread verified 33 and held four. The sealed
packet checksums are in `PACKET.sha256`.

| Disposition unit | Verified | Corrected | Withdrawn | Queued |
| --- | ---: | ---: | ---: | ---: |
| Sealed evidence-ID packet decisions | 189 | 1 | 3 | 41 |
| Applied evidence-ID decisions after the controller ruling | 189 | 2 | 2 | 41 |
| Canonical HQ cells changed | 0 | 6 | 2 | 0 |

Of the 189 verified evidence claims, 156 stand on the first read and 33 stand
on both reads. `PACKET_DISPOSITIONS.csv` records the original and applied
decisions for every evidence ID. `CLAIMS_CHECKED.csv` has 201 rows for the
193 checked evidence claims and eight changed canonical cells. The 41 open
items have settling facts in `OPEN_QUEUE.csv`. The other 293 screen-5-only
evidence IDs remain outside this pass.

## Headquarters and streets

- **King Machine Molds (ORG-000019)** moves from the Ohio shard to North
  Carolina. Its archived corporate history states Charlotte, North Carolina,
  and describes the Westinghouse Boulevard facility becoming company
  headquarters. The dated history uses past tense and has one headquarters
  statement. The controller accepted that contiguous quote for the correction.
  The Akron establishment keeps its existing Ohio site record. [King Machine corporate page](https://kingmachinemolds.com/corporate/)
- **Total Plastics (ORG-001907)** moves from the Ohio shard to Michigan. Its
  current contact page identifies Kalamazoo as headquarters. The earlier
  Cleveland-area citation identifies a branch. [Total Plastics headquarters](https://totalplastics.com/contact-us/)
- Both headquarters states determine the existing `national_us` scope value.
  Each prior Ohio headquarters county is withdrawn and the replacement county
  remains unknown. Two new own-site address observations support tier C and
  have two archive links and two exact-byte binding proofs.
- **Swagelok Solon (SITE-000156)** has two withdrawn evidence assertions and
  an already-blank canonical street. Both old evidence rows and their archive
  records are retained as part of the historical ledger.

## Reproduction

`python3 -I tasks/p1-atlas9-corrections-2026-11-23/check.py --at <head>`
verifies the sealed inputs, replays each source packet and exact proof, checks
each claim and queue row, and compares the complete canonical diff to the
approved corrections. The Ohio site shard and the previous evidence records
are included in the diff comparison.
