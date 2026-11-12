# Ohio street addresses, batch 02 (own-site route), 2026-11-12

Same claim, method, checks and scripts as batch 01 (`tasks/oh-street-address-2026-11-12-b01/README.md`). Branch
`agent/grok/oh-street-address-2026-11-12-b02`. Evidence IDs EVD-340100–EVD-340142 (lane range EVD-340000–349999).

## Frame
The next 100 rows of the same frozen PIC-18 frame after batch 01: 86 Summit rows and the first 14 Portage rows, SITE-000450 …
SITE-000594 in county then site_id order. Conflict-held rows are excluded and batch 01's rows are disjoint. `frame.csv` is frozen.

One addition since batch 01: the overlap check now also compares streets across this batch and the pending batch 01 fills.

## Result (unit: active Ohio site rows in this frame)
- 100 rows: **43 VERIFIED**, **57 STILL_UNCERTAIN**, 0 REJECT. VERIFIED by tier: A 11, B 6, C 15, U 11.
- Raw re-check: 43 of 43 passed.
- Fetches: 472 attempts, 332 returned 2xx.
- Hold reasons, each with its settling fact in `holds.csv`:
  - 30: pages read but no street at the recorded city;
  - 10: fetch unavailable;
  - 9: no held website;
  - 4: own-page street disagrees with the street in notes;
  - 3: same-operator sibling sites in the city;
  - 1: ZIP conflict.
- Only `street_address` changes on 43 site rows, plus 43 appended `own_site` / `address` / `supports_A` evidence rows. SITE-000450,
  SITE-000454 and SITE-000370 also get an ADDRESS-OVERLAP LEAD note. Nothing else changes.
- Ohio coverage: active Ohio site rows with a street go from 466 to 509 of 1,877 on this branch (batch 01 is not included).

## Address-first flags (no merge made)
- SITE-000450 Little Tikes (ORG-000421) and SITE-000454 LT Molding Solutions (ORG-000424) are both at 2180 Barlow Rd, Hudson.
  Little Tikes lists LT Molding as "a division of Little Tikes".
- SITE-000370 Four Seasons Industries shares 10421 Industrial Dr, Garrettsville with SITE-000318 DCA Construction Products.
- SITE-001316 and SITE-001317 (plus SITE-000608) are three Shin-Etsu Silicones sites in Akron, and the own site gives one street,
  1150 Damar Dr. They are held.

## Other leads (`leads.csv`)
- ZIP conflict: SITE-001569 VisionAir. The own page gives 44311, but the record says 44306.
- Own site prints another city:
  - SITE-001539: Stow;
  - SITE-001708: North Canton;
  - SITE-002032: several plants elsewhere in Ohio;
  - SITE-000188: Ravenna.
- Notes-street disagreements are held: Steere ×3 (285 Commerce St vs notes) and Circle Mold.
- SITE-001593 Mabel Dental Lab: the own page prints Ste C (HQ) and Ste A (footer). Ste C is filled; it agrees with the FDA street in notes.
