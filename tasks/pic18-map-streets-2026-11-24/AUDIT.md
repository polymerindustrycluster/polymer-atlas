# Audit record: PIC-18 map-listing street fill (PR #552)

Label: claude-code pic18-map-streets-2026-11-24
Result: PASS
Sample: 1 of 1 fill (SITE-000011, 62 N Summit St, evidence EVD-483134), replayed by both reviewing families of PR #552
Reviewers: Gemini 4 Hydrogen (PR #552 review record, comment 7139575442: Overture Parquet + store capture replay + EPA FRS note); OpenAI Codex (PR #552 review records at b29af5f and 7e5497aa)

## What was audited

Written by the merge clerk on the controller's order on 2026-11-24, from the two review
records and a check of main. The clerk did not replay the capture itself.

- **Checked on main (d0f96689, the #552 merge).** SITE-000011 (operator ORG-000012, Akron,
  OH, Summit County, tier C) has `street_address` `62 N Summit St`. EVD-483134 exists in
  `data/evidence_sites_OH.csv` for record sites/SITE-000011: claim type `address`, source
  class `platform_category`, source ref `overture-maps-places
  ddb95786-fece-4e56-b124-ca5400c3e0e0`, tier effect `supports_C`, empty `address_role`,
  created_by `claude-code pic18-map-streets-2026-11-24`. Its quote is `name: Akron Polymer
  Systems; street: 62 N Summit St; city: Akron; state: OH`. Its note records the capture
  digest `f4ebb0a2b8d32f237199864e7f19fc74f761fc03e285657241d3d4a86c8e3a1b` and the
  second source `EPA FRS facility 110044831180, STRONG match` at `62 N SUMMIT ST, Akron, OH
  44308`.
- **Gemini 4 Hydrogen** (PR #552 comment 7139575442, at head 7e5497aa). It hashed the 3
  inputs and the 3 packets (6 of 6 SHA-256 matches). It replayed Overture place
  `ddb95786-fece-4e56-b124-ca5400c3e0e0` from the pinned release Parquet part with DuckDB
  and found it byte-identical to the stored capture: Akron Polymer Systems, 62 N Summit St,
  Akron, US-OH, 44308-1941, status open, source dataset BrightQuery, not Google-derived. It
  confirmed the second source is the held EPA FRS note, independent of Overture and Google,
  a physical street, matching the held operator. It ran the packet's `check.py` (exit 0: 1
  fill, 1 changed cell, 152 held or status-lead sites, 18 planted defects rejected). The
  binding gate passed 1 of 1 (`map_listing_street_bound`); `validate.py` and the row-loss
  guard passed.
- **OpenAI Codex** (PR #552 comment 7138269501, at b29af5f2). A clean store-backed replay
  passed for SITE-000011 and reproduced all 152 hold or status-lead decisions; four
  on-disk mutations of the packet were each rejected. Its record at 7e5497aa (comment
  7139027311) carried that map-fill review forward; its own scope there was the #547 audit
  record.
- **Independence.** The builder was Claude. Both reviewing families differ from it. The
  second source is a different provider from the map listing.

Not audited: the 152 holds (they changed nothing), the tier ceiling, and any business
status.
