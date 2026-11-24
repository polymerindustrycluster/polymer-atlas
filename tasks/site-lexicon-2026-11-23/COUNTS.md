# Lexicon scan counts

Hits are (surface, record, field, phrase) rows; SHOWN = published, ALLOWED = an ordinary use named in PROSE_ALLOW.

| Surface | SHOWN | ALLOWED |
|---|---|---|
| csv:directory.csv | 0 | 25 |
| csv:prospects.csv | 0 | 25 |
| json:directory.json | 0 | 837 |
| json:experts.json | 0 | 8 |
| json:graph/graph.json | 0 | 65 |
| json:graph/map-network.json | 0 | 54 |
| json:graph/trade-shows.json | 0 | 2 |
| json:orgs.json | 0 | 34 |
| json:sites.json | 0 | 38 |
| json:skyline.json | 0 | 3 |
| page | 0 | 1220 |
| release-csv | 0 | 49 |
| release-sqlite | 0 | 49 |

Notes cells with at least one hit (not withheld by design; see README):

- release-csv:code: 61
- release-csv:ecosystem.csv: 395
- release-csv:event: 1436
- release-csv:events.csv: 95
- release-csv:evidence: 23116
- release-csv:inclusion: 108
- release-csv:members.csv: 55
- release-csv:organizations: 4644
- release-csv:programs.csv: 247
- release-csv:ref: 8
- release-csv:relationships.csv: 253
- release-csv:site: 570
- release-csv:sites: 6841
- release-sqlite:code: 61
- release-sqlite:ecosystem: 395
- release-sqlite:event: 1436
- release-sqlite:events: 95
- release-sqlite:evidence: 23116
- release-sqlite:inclusion: 108
- release-sqlite:members: 55
- release-sqlite:organizations: 4644
- release-sqlite:programs: 247
- release-sqlite:ref: 8
- release-sqlite:relationships: 253
- release-sqlite:site: 570
- release-sqlite:sites: 6841

**Note, 2026-11-23, after #534.** The release-notes counts above (organizations 4,644, sites 6,841) describe the release as it was at the lexicon pass, before #534 removed the `notes` column from the release's organization and site tables. A scan of the post-#534 release counts neither. The evidence and other tables' counts are unchanged. This file is the dated record of that run and is not rewritten.
