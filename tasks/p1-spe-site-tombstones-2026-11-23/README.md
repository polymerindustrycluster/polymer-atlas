# Retire two SPE site records

This applies the 2026-11-23 owner ruling “Ecosystem, not sites” after
blind audit 12 was drawn and #528 was merged.

| Site tombstone | Existing active ecosystem section |
| --- | --- |
| SITE-000091 | ORG-000091, Society of Plastics Engineers Akron Section |
| SITE-000163 | ORG-000163, Society of Plastics Engineers Cleveland Section |

Both historic rows are retained. The two records use `closed` as the
site tombstone convention, following prior row retirements such as
SITE-000174 and SCHEMA §5.5. Their existing notes gain the date and
classification rationale. Both existing ecosystem records continue
to carry the active sections at the trade-association subtype.

## Check

```sh
lockf -k /tmp/polymer-atlas-heavy.lock python3 tasks/p1-spe-site-tombstones-2026-11-23/check.py --at HEAD
```

The check matches the existing ecosystem organizations to both
historic site rows, then proves the exact site shard and claim ledger
after the two status changes and two note additions. The data diff
contains only the Ohio sites shard.
