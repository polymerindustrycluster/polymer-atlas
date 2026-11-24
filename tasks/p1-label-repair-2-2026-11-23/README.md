# ATLAS-38 public label repair 2

This is one of three repair packets in the combined public-cell PR.
The sealed packet proposes 151 corrections. This integration applies
136, comprising 58 description cells (55 organization and three event
fields) and 78 organization NAICS source names. NAICS code, source type
and confidence are retained. The lane's second reader passed 60 of 60
seeded receipts. The broad scan remains open, with 722 targeted packet
holds plus 15 rendered-description holds.

The controller applied the label rule, “If deletion would leave the
field empty or wrong, hold it.” All 15 previously withheld organization
descriptions identified in the first render review retain their exact
held text. Each reason appears in OPEN_QUEUE.csv. The already visible
ORG-001798 description keeps its complete manufacturing facts.
LEDE_REVIEW.csv carries the rendered decisions.

The shared-store manifest pins four source bodies, including the
privacy-minimized OSHA projection. The pinned packet replay checks
the original OSHA input and the projection against the sourced rows.

## Replay

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/p1-label-repair-2-2026-11-23/check.py --at HEAD --render
```

The check covers all three claim ledgers, the exact data delta, the
fresh URL and website scans, and the rendered descriptions, AHFA sources and website probes.
Replay the original label rules and remaining holds in the sealed
packet with its `--store` and `--packet-only` options.
