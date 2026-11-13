# Ohio street addresses, batch 05 (own-site route), 2026-11-12

Same claim, method, checks and scripts as batch 01 (`tasks/oh-street-address-2026-11-12-b01/README.md`), with the batch 02/03 builder
changes (cross-batch overlap check, street-to-ZIP quote trim, suite-conflict flag). Branch `agent/grok/oh-street-address-2026-11-12-b05`. Evidence IDs EVD-340400–EVD-340427
(lane range EVD-340000–349999).

## Frame
Next 100 (or remaining) rows of the frozen PIC-18 frame after the earlier batches: 63 Cuyahoga + 35 Lake + 2 Geauga, SITE-000642 … SITE-000213. Conflict-held rows excluded; disjoint
from all earlier batches. `frame.csv` frozen.

## Result (unit: active Ohio site rows in this frame)
- 100 rows: **28 VERIFIED** (tiers A 6, B 6, C 9, U 7), **72 STILL_UNCERTAIN**, 0 REJECT. Raw re-check 28/28
  passed. Fetches: 449 attempts, 291 2xx.
- Holds (each with its settling fact in `holds.csv`): 38 pages read but no street at the recorded city; 17 fetch unavailable (not absence); 8 no held website; 4 own-page street disagrees with notes; 2 ZIP conflict; 1 same-operator sibling sites in the city; 1 raw re-fetch failed; 1 other.
- Only `street_address` on 28 site rows plus 28 appended `own_site`/`address`/`supports_A` evidence rows (ADDRESS-OVERLAP LEAD notes where
  flagged). No county, ZIP, coordinates, tier, status, ring or registry change; no creates, deletes or merges.
- Active Ohio site rows with a street: 466 → 494 of 1877 on this branch (other open batches not included).

## Address-first flags (no merge made)
- SITE-001573: ADDRESS-OVERLAP: SITE-000477 (ORG-000446 MMI Textiles, Inc. — Brooklyn, pending b04)

## Other leads (`leads.csv`)
own_site_other_city_address: 9, zip_conflict: 2, zip_field_defect: 2, mail_unit_lead: 1
