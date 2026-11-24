# V-55 vocabulary repair · 2026-11-23

Integrating worker: atlas-p1-vocab-repair. The only input is the canonical
organization and site shards at pre-pass commit
`d69c4099dd08ecf7a14f762e3328718438bb0fe9`. That commit is the backup for
every shard. The pass adds no records and makes no new source claims.

Acceptance requires clearing or itemizing all V-55 debt, accounting for
every original capability value, and preserving all rows and unrelated
cells. The PIC-18 process measure must be reconciled and the site and
release tests must pass before review. See [CHECK.md](CHECK.md).

## Pass journal

1. Ran the base validator and counted 2,884 organization and site records
   with active V-55 debt.
2. Ran `python3 tasks/p1-vocab-repair-2026-11-23/build.py`. It rewrote all
   50 organization shards to add the columns and repaired values across
   the site shards. A repeat rewrote zero shards.
3. Removed the 2,884 cleared record IDs from the V-55 debt baseline. The
   lexicon used by the release now also applies to the two capability
   notes on organizations and sites.
4. Replayed the pass against every shard and ran the validator, site and
   release tests, and artifact builds. See [CHECK.md](CHECK.md).

| Unit, all statuses | Organizations | Sites |
|---|---:|---:|
| Canonical records before and after | 5,026 | 7,196 |
| Records with changes to capability or other-note values | 114 | 2,415 |
| Original process values moved to the other-note | 118 | 2,799 |
| Original material values moved to the other-note | 26 | 2,492 |
| Previously off-vocabulary Ring 3 process tokens retained | 145 | 243 |
| Original values re-encoded after all parts matched | 0 | 0 |

Movement counts are occurrences in the pre-pass process and material
fields. Identical note entries occupy one slot. The 2,529 records that
changed values plus the 355 records that cleared through the Ring 3
allowance alone account for all 2,884 V-55 records. No evidence source
was fetched and no record received a new verification tier.
