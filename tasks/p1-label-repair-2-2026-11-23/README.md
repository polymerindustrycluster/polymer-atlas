# ATLAS-38 public label repair 2

This is one of three repair packets in the combined public-cell PR.
The 151 reviewed corrections consist of 73 published descriptions
(70 organization descriptions and three event fields) and 78
organization NAICS source names. NAICS code, source type and
confidence are retained. The lane's second reader passed 60 of 60
seeded receipts. The strict broad scan remains open. The sealed packet
keeps 722 targeted holds.

The shared-store manifest pins four source bodies, including the
privacy-minimized OSHA projection. The pinned packet replay checks
the original OSHA input and the projection against the sourced rows.

## Replay

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 -I tasks/p1-label-repair-2-2026-11-23/check.py --at HEAD --render
```

The check covers all three claim ledgers, the exact data delta, the
fresh URL and website scans, and the rendered AHFA and website probes.
Replay the original label rules and remaining holds in the sealed
packet with its `--store` and `--packet-only` options.
