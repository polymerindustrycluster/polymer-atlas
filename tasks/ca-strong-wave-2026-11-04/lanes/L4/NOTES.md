# Lane L4 notes (CA STRONG wave, 2026-11-04)

## UNFINISHED
None. All 19 input clusters have a verdict in verdicts.csv (checked: 19 rows, same IDs as input.csv).

## Counts (unit: LF-CA STRONG clusters in input.csv)
| Verdict | Tier | n |
|-|-|-|
| VERIFIED_NEW_ORG | C | 13 |
| VERIFIED_NEW_SITE | C | 2 (Prime Conduit Woodland -> ORG-000124; Graham Modesto -> ORG-001403) |
| STILL_UNCERTAIN | - | 3 (Insulated Products, Garcia Plastic Molding, Classic Containers) |
| REJECT | - | 1 (JP Lamborn) |
| DUPLICATE_OF | - | 0 |

No tier B: every new org is C by the brief, and both new sites lack an own-site page naming the plant.

## Dedupe
`atlas.py dedupe-check` (name, domain, street) run for every company. Only two hits: ORG-000124 (primeconduit.com) and ORG-001403 (grahampackaging.com). No street-level site hit, so no DUPLICATE_OF. The step-4 TransDigm substring hit (ORG-000562 Schneller) is a sister company, not Kirkhill's owner; no merge.

## Notable calls for the integrator
- **LF-CA-01575 + LF-CA-01178**: same organization (VPET USA, LLC; Canyon Plastics was acquired by VPET in Jan 2022, canyonplastics.com redirects to vpetusa.com). Create one org, two sites. Valencia has no own-site witness.
- **LF-CA-01000**: federal registrant is Kakuichi America Inc; the own site at the same address is Pacific Echo, Inc. Group profile lists them as two separate companies. Operator unresolved; created under Pacific Echo with a note.
- **LF-CA-00944 REJECT**: JP Lamborn makes HVAC flexible duct from a steel helix, purchased polyester/foil laminate and insulation. No closure; not a polymer-conversion site on the page evidence. Ring 4 watchlist would be an owner ruling.
- **STILL_UNCERTAIN**: Insulated Products (no polymer process stated), Garcia Plastic Molding (domains gpmolding.com and gpmplastics.com are parked; no primary page), Classic Containers (site is a wholesale bottle storefront; no molding stated). Settling fact for each is in `deciding_fact`/`note`. Fetch failures were not used as evidence.
- **LF-CA-00891 WARCO**: federal street 750 N Main is the manufacturing plant; sales/corporate is 1337 W Braden Ct.
- **LF-CA-01905 Bryant Rubber**: also has a Tijuana, Mexico plant (foreign site, no lawful shard); not part of this lane.
- **LF-CA-01058 Verdeco**: HQ is Piedmont, SC; street corrected to "8685 Bowers Ave." per own site.
- **Ray Products**: use rayplastics.com; rayproducts.com is an unrelated paperboard company.

## Method and limits
- Own-site fetches used WebFetch/WebSearch plus a local scripted page-text read. Every `own_quote` was re-checked as a substring of the page text (14 of 14 matched, whitespace-normalised across adjacent elements). Quote kind `activity_only` means the quoted span does not itself name the city; the city/address appears elsewhere on the same site and is cited in `note`.
- No Form 5500 or closure check was needed: no REJECT rests on closure.
- Processes/materials are only those the pages state. Several NAICS sets had no clear primary, so `naics_primary` is blank there.
- Not checked: California SOS entity records (legal-name suffixes for MAST, Bryant, Toray are from federal rows or unconfirmed); county of out-of-state or unstated HQs left blank.
