# PIC-18 evidence settlement (G8a)

Built by: Codex GPT-6.2 Sol (atlas-p1-integrator-1), 2026-11-23.

This applies the “Settle PIC-18 first” ruling and the owner's 16:18
decision, “Keep row, mark unverified (2026-11-23)”. The owner assigned
gate extensions to a separate PR. The audit draw remains controller-gated.

## Published changes

The 270 claim checks comprise 221 verified, 24 corrected and 25 withdrawn.
Of those, 249 are evidence-claim decisions and 21 are canonical cell
decisions. There are 34 changed canonical cells including 13 protocol
notes. Eight observations are appended, seven at supports_C and one at
supports_B. Two carry exact-byte own-site proofs and public archive links.
The six structured observations independently rejoin the original OSHA
and RCRA downloads as well as the source index rows.

Pittsburgh Paints' own page explicitly puts its headquarters in Cranberry
Township, Pennsylvania. The organization moves to the PA shard with
derived national_us scope. The unsupported Ohio HQ county is blanked.
The Huron plant keeps its site record and its separate evidence. King
Machine uses a separate, exact own-site existence quote from its
already reviewed archive.

## Scope and floor holds

The 38 sibling checks show which cited pages carry the same defect as
the ruled row. Seventeen claims qualify for prospective scope withdrawal.
Nine are withdrawn and their held affected values are removed. The
Lattice site's eight are retained under V-68. The JK Plastics homepage
lacks the site locality, while its horticultural, windows and custom
pages print it. The MES generic market list is distinct from the page's
material and production wording. Dover's unsupported agriculture value
is removed. The six previously verified Dover claims retain their reader
decisions.

The expanded preflight lists 34 evidence IDs on 22 records at their
evidence floors (17 V-68 records and five V-65 records), including
Intertex and Lattice. `floor-blockers.csv` gives the projected supported
tier under §4.13 for each record/evidence pair. The owner-authorized
records retain their historical rows and receive the specified tier and
note treatment. Enpac ORG-001762 moves from B to U under the controller's
16:32 clarification.
`RE_ADMISSION.csv` lists the 18 gate-limited rows for the later gate PR,
including the Lincoln EDGAR route.

The 20 evidence withdrawals are explicit ledger dispositions. Prior
evidence and archive data remain append-only. Evidence already in
`data/` keeps its historical ID and content.

## Audit frame

The PIC-18 owner census moves from 794 to 792 owners of active tier A–C
sites. Beacon ORG-001511 leaves after SITE-001575 moves to U. ORG-001197
leaves after SITE-001296 moves to U because its other sites fall outside
PIC-18. The controller confirmed both departures. At the resulting
792-owner denominator, 305 have unknown process, 303 have unknown
market, and 372 have unknown size. The count changes reflect the frame
departures. The separate audit strata are listed for the tier marks.

| Record | Prior tier | Audit frame at `1600f540` |
|---|---|---|
| `ORG-000068` | C | PIC18_RECORDS |
| `ORG-000206` | B | PIC18_RECORDS |
| `ORG-000212` | B | PIC18_RECORDS |
| `ORG-000265` | B | PIC18_RECORDS |
| `ORG-000404` | B | PIC18_RECORDS |
| `ORG-001397` | B | PIC18_RECORDS |
| `ORG-001762` | B | outside |
| `ORG-001832` | B | PIC18_RECORDS |
| `ORG-001857` | B | PIC18_RECORDS |
| `ORG-001886` | B | PIC18_RECORDS |
| `ORG-002011` | A | PIC18_RECORDS |
| `SITE-001296` | C | PIC18_RECORDS |
| `SITE-001575` | C | PIC18_RECORDS |

## Replay

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/p1-pic18-settle-2026-11-23/check.py --at HEAD
```

The replay verifies the two reader sets, the final 56 re-citation decisions
and the sibling cases, the evidence floors, the 166 used archive or live
body hashes, the two index hashes, the three original registry downloads,
the canonical diff and the claim and hold ledgers. Of 162 staged original
bodies, three belong only to recitation proposals superseded before
integration. The seven supplemental captures support the final sibling
and Intertex replay. Source files are in the private store by checksum.
The check covers neither unaudited evidence outside the input populations
nor present operation based on a live inspection.
