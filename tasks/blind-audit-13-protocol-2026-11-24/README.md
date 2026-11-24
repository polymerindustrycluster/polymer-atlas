# ATLAS-7 · Proposed audit after repairs

The controller presents [the owner question](OWNER_QUESTION.md) before authorizing any sample. [PROTOCOL.md](PROTOCOL.md) revises audit 12. [SIZES.md](SIZES.md) is stdout from `python3 sizes.py`. From the repository root run:

```sh
python3 tasks/blind-audit-13-protocol-2026-11-24/sizes.py --selftest
```

The check verifies known probability answers, the sizing boundary, and agreement of both published numerical tables with the calculation. The private calibration source is audit 12’s frozen draw and per-reader packet/verdict files. The histogram in the calculator contains only grouped numbers of completed and missed reads. The historical spend source is the P1 controller’s corrected usage note at 21:41 on November 23. This branch supplies a design for ruling; tooling qualification, review and execution follow separately.
