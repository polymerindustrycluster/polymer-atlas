# Lane L1b notes (FL STRONG wave, 2026-11-04)

Picks up the 4 clusters L1 left unfinished. Output: `verdicts.csv` (4 rows, same header as L1).

## Results
- LF-FL-00433 American Vinyl Company: VERIFIED_NEW_ORG, tier C. avcplastics.com/about says all production is at the Hialeah and Tampa facilities; /locations prints 6715 N 53rd St, Tampa 33610; home page says PVC profiles by custom vinyl extrusion.
- LF-FL-00096 Sun Coatings, LLC: VERIFIED_NEW_ORG, tier C. suncoatings.com/pages/company says all products are manufactured in Tampa (latex and solvent paints, adhesives, caulks); /pages/contact-us prints 4701 E. 7th Avenue, Tampa 33605. L1's search-summary lead is now confirmed verbatim.
- LF-FL-00089 Speedling, Incorporated: VERIFIED_NEW_ORG, tier C. speedling.com/eps-and-hort says expanded polystyrene beads are molded into trays and containers; /our-story/locations/ gives corporate address 4447 Old US Hwy 41, Ruskin.
- LF-FL-00062 Sentry Industries, Inc.: REJECT (scope). sentryindustries.net shows a sodium hypochlorite (bleach) and pool-chemical plant at the federal address; plastic totes and crates are listed only as goods.

Counts (4 rows): VERIFIED_NEW_ORG 3, REJECT 1. Tiers: C 3, blank 1.

## Items for the integrator
1. American Vinyl and Aurora: the ITA alias "Aurora Material Solutions - FLUS02PR" sits on this plant. Aurora is held (ORG-001477), but the AVC site says "A family operation since 1966" and never mentions Aurora; two web searches found no source linking them. Do not fold into ORG-001477 without a dated ownership source. If one is found, this becomes a subsidiary org with parent ORG-001477.
2. American Vinyl HQ is blank (site never says which of Hialeah or Tampa is HQ). Quote is `plant_only`; PVC extrusion comes from the home page, so the processes and materials are company-wide, not Tampa-specific.
3. Speedling: the witness is community-level (Sun City, the Ruskin-area name). The EPS building has no printed street; 4447 Old US Hwy 41 S is the corporate office address, which the locations page places next to the EPS plant ("just down the road from the nursery attached to our corporate office"). Speedling is mainly a plant-plug nursery with an EPS side line. Dedupe note: all three of my new-org names had no hit in `data/organizations_*.csv` / `sites_*.csv` (rg on American Vinyl, avcplastics, Vartek, suncoatings, sunkote, speedling, sentry industries). Only ICP/Aurora rows (unrelated shards) matched the Sun Coatings/AVC searches.
4. Sun Coatings: ICP Group ownership is not on the own site (it comes from L1 notes), so no parent link is recorded.
5. NAICS picks (326121, 325510, 326140, 325998) come from each row's `naics_set`; none is company-disclosed.
6. Sentry: sentryindustries.net served an expired TLS certificate. I read it with certificate checking off (read-only GET) and treat that as an availability issue, not evidence. Reopen only if a page says Sentry molds or extrudes the totes itself.

## Method
Read-only GET with tag strip (python -I), WebSearch for ownership leads. Every `own_quote` was checked as an exact substring of a fresh fetch of `own_url` (4 of 4 found, 12 to 23 words). No data/ edits, no git. No closure notice found for any row.
