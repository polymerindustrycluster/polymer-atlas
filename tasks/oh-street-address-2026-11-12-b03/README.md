# Ohio street addresses, batch 03 (own-site route), 2026-11-12

This batch uses the same claim, method, checks and scripts as batch 01 (`tasks/oh-street-address-2026-11-12-b01/README.md`), with batch 02's cross-batch overlap check.

- Branch: `agent/grok/oh-street-address-2026-11-12-b03`.
- Evidence IDs: EVD-340200 to EVD-340236, from the lane range EVD-340000 to EVD-349999.

Two changes to the builder since batch 01. Neither changes the frame or the acceptance rule:
- Evidence quotes are trimmed to the street block (street to ZIP), so no emails or phone numbers are carried.
- The adjudicator flags own pages that print different suites at the same street for a manual pick.

## Frame
- The next 100 rows of the frozen PIC-18 frame after batches 01 and 02: 21 Portage, 52 Stark, 26 Medina and 1 Wayne.
- Rows already held for a conflict are excluded. The frame does not overlap batches 01 and 02.

## Result (unit: active Ohio site rows in this frame)
- 100 rows: **37 VERIFIED**, **63 STILL_UNCERTAIN**, 0 REJECT.
- VERIFIED by tier: A 13, B 4, C 9, U 11.
- Raw re-check: 37 of 37 passed.
- Fetches: 476 attempts, 325 returned 2xx.
- Holds, each with its settling fact in `holds.csv`:
  - 39: pages read, but no street at the recorded city;
  - 13: fetch unavailable;
  - 5: no website;
  - 4: several streets;
  - 2: mailing or PO context only.
- What changes: `street_address` on 37 site rows, plus 37 appended `own_site` / `address` / `supports_A` evidence rows. No other field changes.
- Ohio coverage: active Ohio site rows with a street go from 466 to 503 of 1,877 on this branch. Batches 01 and 02 are not included.

## Leads (`leads.csv`)
No address overlaps this batch. Four own sites print a different city, a possible relocation or HQ-only page:
- SITE-001512, recorded Alliance: North Royalton;
- SITE-000362, recorded Wadsworth: Middlefield;
- SITE-002904, recorded Wadsworth: 1293 S Main St, Akron (the Myers Industries street);
- SITE-000226, recorded Wooster: Hilliard.
