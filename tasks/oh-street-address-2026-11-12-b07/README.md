# Ohio street addresses, batch 07 (own-site route), 2026-11-12

Same claim, method, checks and scripts as batch 01 (`tasks/oh-street-address-2026-11-12-b01/README.md`), with the batch 02/03 builder
changes (cross-batch overlap check, street-to-ZIP quote trim, suite-conflict flag). Branch `agent/grok/oh-street-address-2026-11-12-b07`. Evidence IDs EVD-340600–EVD-340614
(lane range EVD-340000–349999).

## Frame
Next 100 (or remaining) rows of the frozen PIC-18 frame after the earlier batches: the last 34 rows: 9 Tuscarawas, 5 Richland, 4 Ashland, 5 Erie, 11 Huron; SITE-001165 … SITE-002037. Conflict-held rows excluded; disjoint
from all earlier batches. `frame.csv` frozen.

## Result (unit: active Ohio site rows in this frame)
- 34 rows: **15 VERIFIED** (tiers A 2, B 2, C 5, U 6), **19 STILL_UNCERTAIN**, 0 REJECT. Raw re-check 15/15
  passed. Fetches: 162 attempts, 108 2xx.
- Holds (each with its settling fact in `holds.csv`): 10 pages read but no street at the recorded city; 4 fetch unavailable (not absence); 3 no held website; 1 own-page street disagrees with notes; 1 several streets at the recorded city.
- Only `street_address` on 15 site rows plus 15 appended `own_site`/`address`/`supports_A` evidence rows (ADDRESS-OVERLAP LEAD notes where
  flagged). No county, ZIP, coordinates, tier, status, ring or registry change; no creates, deletes or merges.
- Active Ohio site rows with a street: 466 → 481 of 1877 on this branch (other open batches not included).

## Address-first flags (no merge made)
- SITE-002037: ADDRESS-OVERLAP: SITE-002855 (ORG-002080 Mitsubishi Chemical Performance Polymers)

## Other leads (`leads.csv`)
street_variant: 1
