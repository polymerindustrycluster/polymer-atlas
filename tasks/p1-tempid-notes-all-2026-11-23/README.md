# Apply the approved all-notes temporary-ID repair

The owner ruled “All notes, not evidence.” Apply the all-shapes packet
after the audit 12 draw at `985ed364`. Gemini 4 Hydrogen approved the
whole packet pinned to `77e5b6f4`, including the explicit
`NEW:TRIA-21` → `ORG-003102` pairing. The integrated input is the
sealed `edits.csv`.

Exact old-cell comparison on the application base produced 3,380
edits in 99 shards (701 organization and 2,679 site notes). All 29
packet holds remain in OPEN_QUEUE.csv. All 3,380 eligible old values
matched the application base. The changed records span 348 A, 2,285
B, 746 C and one U tier records. The repair changes their notes.

## Checks

Run the sealed packet's `python3 check.py --repo <checkout> --selftest`
from its private packet folder. It reconstructs the original frame,
verifies mappings and checks planted failures at the original pin.

From the application checkout, run:

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 tasks/p1-tempid-notes-all-2026-11-23/check.py --at HEAD
```

The application check verifies the sealed inputs and replays every
notes cell against the merge base. A moved or changed old value is
queued with its reason. It compares the exact reconstructed CSV
bytes and the claim and hold ledgers at the requested head.
