# Lane L1 notes (TX STRONG wave, 2026-11-04)

Input: 21 clusters. Output: `verdicts.csv` (21 rows). No `data/` edits, no git.

## Counts
| Verdict | Tier | n |
|-|-|-|
| VERIFIED_NEW_SITE | B | 5 |
| VERIFIED_NEW_ORG | C | 13 |
| STILL_UNCERTAIN | - | 3 |
| REJECT / DUPLICATE_OF | - | 0 |

## Dedupe
- `atlas.py dedupe-check` (name + street + city + zip) run for all 21. No street hit anywhere, so no DUPLICATE_OF.
- Held-org hits used as parents: ORG-002462 (Technimark), ORG-000132 (Sherwin-Williams), ORG-000315 (Dura-Line), ORG-000760 (Corvac).
- False name hits, not used: ORG-002923 Best Diamond Plastics (Chicago straws) for Diamond Plastics Corp; ORG-003188 Heritage Plastics Inc (Picayune MS mineral concentrates, its own note says it is not the PVC-conduit firm) for Atkore/Heritage; ORG-002858..2921 on North West Rubber (unrelated).
- Sherwin-Williams Garland: held SITE-004939 is 701 Shiloh Rd (75042, fire plant). 2802 W. Miller Rd (75041) is a separate "Garland Paint" entry on Sherwin's own ISO certificate and has its own FRS ID, so I called it a new site, not a duplicate. Integrator should confirm the two are distinct before applying.

## Flags for the integrator (held-record problems found on the way)
- ORG-002462 Technimark, LLC is recorded with HQ Latrobe PA and NAICS 236210; Technimark's own page prints world HQ as Asheboro NC (SITE-005037 is the Asheboro plant).
- ORG-000760 Corvac Composites is recorded with HQ Greenfield OH; Corvac's own site prints global HQ Kentwood MI.
- Enduraplas federal variants include "Tank Holding Corp" / "Premia Group"; held ORG-003687 Tank Holding Corp. is not linked on any Enduraplas page I read. Left unlinked.
- Poly-America's page names Up North Plastics (held as ORG-004180); parent link is an integrator call.
- ESCO Plastics: Colson Group bought it 1 Jul 2025; Colson is not held.
- North West Rubber has a Canadian HQ (Abbotsford BC); org shard placement needs a ruling.

## Method limits
- Page text came through a summarising fetch tool, so quotes taken from HTML pages may differ in punctuation. The integrator re-fetches `own_url` per the brief; three quotes with commas or dashes (Evantic, Corvac, Enduraplas) are the most likely to need a spacing fix. PDF quotes (Hempel, Atkore, Diamond, both Sherwin rows) were read directly with pdftotext and are exact apart from line breaks flattened to spaces.
- The two Sherwin certificate rows rest on a 5 May 2015 ISO attachment. Liveness comes from the 2026 federal rows, not the certificate.
- Federal-only sites (SPR, CKS) have company-level scope evidence but no page naming the plant, so they are C.
- CKS: third-party sources hint the Felix St address may be old (Alliance Gateway Fwy address appears elsewhere). That is not a dated closure, so no REJECT.
- Form 5500 check: no REJECT was issued, so the 5500 gate did not apply.

## STILL_UNCERTAIN, with settling facts
- LF-TX-00019 Fritz Industries: a product page or SDS showing a polymer/resin/coating product made at Mesquite. Home page shows oilfield and aquatics chemistry only; leans out of scope.
- LF-TX-00683 GPS Paints: a company page or label showing paint manufacture at 301 W Hurst Blvd. Only trademarks and renovation permits found; no company site.
- LF-TX-00438 Regency Plastics-Ubly (El Paso): a page naming the El Paso plant and what it molds. regencyplastics.com returned no readable body; nothing found on "Sierra Plastics".

## Not checked
No Form 5500 bulk (EFAST2) lookups, no TCEQ or Texas SOS lookups, and no trade-press closure search beyond one query per company, so a closure could still exist for any row.
