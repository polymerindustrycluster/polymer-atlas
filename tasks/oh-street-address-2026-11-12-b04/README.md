# Ohio street addresses, batch 04 (own-site route), 2026-11-12

Same claim, method, checks and scripts as batch 01 (`tasks/oh-street-address-2026-11-12-b01/README.md`), with the batch 02/03 builder
changes (cross-batch overlap check, street-to-ZIP quote trim, suite-conflict flag). Branch `agent/grok/oh-street-address-2026-11-12-b04`. Evidence IDs EVD-340300–EVD-340346
(lane range EVD-340000–349999).

## Frame
Next 100 (or remaining) rows of the frozen PIC-18 frame after the earlier batches: 15 Wayne + 85 Cuyahoga, SITE-000382 … SITE-000614. Conflict-held rows excluded; disjoint
from all earlier batches. `frame.csv` frozen.

## Result (unit: active Ohio site rows in this frame)
- 100 rows: **47 VERIFIED** (tiers A 5, B 3, C 19, U 20), **53 STILL_UNCERTAIN**, 0 REJECT. Raw re-check 47/47
  passed. Fetches: 485 attempts, 339 2xx.
- Holds (each with its settling fact in `holds.csv`): 29 pages read but no street at the recorded city; 13 fetch unavailable (not absence); 7 no held website; 2 ZIP conflict; 1 same-operator sibling sites in the city; 1 mailing/warehouse/PO context only.
- Only `street_address` on 47 site rows plus 47 appended `own_site`/`address`/`supports_A` evidence rows (ADDRESS-OVERLAP LEAD notes where
  flagged). No county, ZIP, coordinates, tier, status, ring or registry change; no creates, deletes or merges.
- Active Ohio site rows with a street: 466 → 513 of 1877 on this branch (other open batches not included).

## Address-first flags (no merge made)
- SITE-000108: SAME-ADDRESS sites: SITE-000107 (ORG-000108 HP Manufacturing — Cleveland)

## Other leads (`leads.csv`)
own_site_other_city_address: 8, zip_conflict: 2
