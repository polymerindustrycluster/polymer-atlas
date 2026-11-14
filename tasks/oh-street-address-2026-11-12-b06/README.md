# Ohio street addresses, batch 06 (own-site route), 2026-11-12

Same claim, method, checks and scripts as batch 01 (`tasks/oh-street-address-2026-11-12-b01/README.md`), with the batch 02/03 builder
changes (cross-batch overlap check, street-to-ZIP quote trim, suite-conflict flag). Branch `agent/grok/oh-street-address-2026-11-12-b06`. Evidence IDs EVD-340500–EVD-340540
(lane range EVD-340000–349999).

## Frame
Next 100 (or remaining) rows of the frozen PIC-18 frame after the earlier batches: 23 Geauga, 17 Lorain, 19 Mahoning, 12 Trumbull, 11 Ashtabula, 6 Columbiana, 12 Tuscarawas; SITE-000237 … SITE-001137. Conflict-held rows excluded; disjoint
from all earlier batches. `frame.csv` frozen.

## Result (unit: active Ohio site rows in this frame)
- 100 rows: **41 VERIFIED** (tiers A 7, B 6, C 15, U 13), **59 STILL_UNCERTAIN**, 0 REJECT. Raw re-check 41/41
  passed. Fetches: 478 attempts, 311 2xx.
- Holds (each with its settling fact in `holds.csv`): 34 pages read but no street at the recorded city; 13 fetch unavailable (not absence); 5 no held website; 2 mailing/warehouse/PO context only; 1 own-page street disagrees with notes; 1 same-operator sibling sites in the city; 1 other; 1 raw re-fetch failed; 1 several streets at the recorded city.
- Only `street_address` on 41 site rows plus 41 appended `own_site`/`address`/`supports_A` evidence rows (ADDRESS-OVERLAP LEAD notes where
  flagged). No county, ZIP, coordinates, tier, status, ring or registry change; no creates, deletes or merges.
- Active Ohio site rows with a street: 466 → 507 of 1877 on this branch (other open batches not included).

## Address-first flags (no merge made)
- SITE-001308: ADDRESS-OVERLAP: SITE-000460 (ORG-000430 Mar-Bal Inc. — Chagrin Falls)
- SITE-001122: SITE-001122 (recorded Baltic) own site prints 5479 Gundy Drive, Midvale, the street filled in this batch for SITE-000909 Flex Technologies; possible common operator or relocation. No merge made.

## Other leads (`leads.csv`)
own_site_other_city_address: 7, mail_unit_lead: 1
