# Lane L2 notes (WI STRONG wave, 2026-11-04)

Unit: 16 lead-fusion STRONG clusters (WI establishments) in `input.csv`. Output: `verdicts.csv`, 16 rows.

**Overwrite warning.** `verdicts.csv` and `NOTES.md` already held an earlier L2 pass (written 10:48-10:49) when this pass started. This pass wrote over `verdicts.csv` without reading it first, so the earlier verdict rows are not recoverable from this lane. The earlier notes were read before this rewrite and their calls are reconciled below. The integrator should check whether another L2 run was active.

## Counts (verdict, tier)
- VERIFIED_NEW_ORG tier C: 5 (ASYST, Protect-All, Northland Plastics, Tigre USA, Plastocon)
- VERIFIED_NEW_SITE tier B: 1 (Hentzen Coatings, Milwaukee Liquid Plant, under ORG-003966)
- VERIFIED_NEW_SITE tier C: 2 (Reynolds Presto Appleton under ORG-002892; Amcor New London Industrial Loop under ORG-000665)
- DUPLICATE_OF: 2 (Inpro -> SITE-005751; Amcor South Oshkosh -> SITE-004903)
- REJECT: 2 (RBP Chemical, EMCO Chemical Distributors), both scope rejects, not closures
- STILL_UNCERTAIN: 4 (Torginol, Fathom/Midwest Composite, Custom-Pak Products, Stowe Woodward)

Total: 5+1+2+2+2+4 = 16.

## Method
- Dedupe with `scripts/atlas.py dedupe-check` (name, street, city, zip) plus a direct read of `data/sites_WI.csv` and `evidence_*` for held orgs. No data edits, no git.
- Own-site pages read with WebFetch (a small-model summarizer). Quotes therefore need re-fetching: the integrator should check each `own_quote` against `own_url`. Weakest for exactness: Hentzen ("Corporate Headquarters / Milwaukee Liquid Plant" may be two page elements), ASYST and Protect-All (single-sentence fragments), Northland (a heading).
- Failed routes, never treated as evidence: businesswire.com (403), amcor.com careers REQ pages (404), reynoldsconsumerproducts.com location and brand pages (404), inprocorp.com home and about (empty/404), torginol.com /company/about-us and /products/flake (404), hentzen.com /about-us (404), protectall.com (redirects to an unrelated domain; use protect-all.com).

## Calls the integrator should look at
- Inpro: DUPLICATE_OF:SITE-005751 rests on held evidence EVD-011803 (S80 W18766 and S81 W18901 are the same Apollo Drive campus), plus inprocorp.com/contact-us printing S80 W18766 as World HQ. The street search alone missed it.
- Amcor Oshkosh Badger Ave: held SITE-004903 street is '2251/2450/2451 BADGER AVE', so the plain street search missed it.
- Amcor New London: held SITE-003144 is 718 High St (former Bemis/Curwood flexible-packaging plant, ~500 workers in 2019). 755 Industrial Loop Rd matches an Amcor 'AF New London Healthcare WI' unit on job tags. Created as a site, tier C, with a duplicate-risk flag. If the integrator learns 755 Industrial Loop is a re-address of 718 High St, fold it.
- Hentzen: the Mill Road plant is the 'Milwaukee Liquid Plant'. A second plant, 'Milwaukee Powder Plant', 8200 N Faulkner Rd 53224, needs its own site record (probably ECHO 110070739568).
- Reynolds Presto Appleton: scope evidence is an expired Reynolds job posting ('our fast-paced plant in Appleton, WI'; 'Produce and package plastic and disposer bags') hosted on career.com, not the company site. Tier C only. The earlier pass held this as uncertain; this pass accepts the federal-only C route in the brief.
- Tigre USA: own site gives no location; scope rests on federal NAICS 326122 plus 2007 trade press and 2026 job listings for the Janesville plant. No own_quote, no HQ. Weakest of the verified rows; the integrator may prefer STILL_UNCERTAIN.
- Stowe Woodward: held as STILL_UNCERTAIN under SCHEMA B14 (no parent-capability inheritance). The Neenah poly-operator posting is Andritz's and names no street; Valmet runs a separate Neenah roll-cover plant.
- Torginol: no fetched page says what the flake is made of or that Sheboygan is the plant. Product is likely resin-based decorative flake (Ring 2 or flooring additive); scope call is not made.
- Fathom: Hartland is the HQ address and a listed process site ('3D printing, CNC machining, molding, and assembly and finishing'), but metals are mixed in and no polymer share is stated.
- Custom-Pak: contract packager of paint; fill-only would be Ring 3 contract services, not coatings formulation.
- RBP and EMCO: rejected on scope (chemical blending / chemical distribution with no polymer product named). EMCO as a Ring 3 polymer-vertical distributor would be an owner ruling, not made here.
- County blanks: Janesville (Rock) filled from the city; Oconomowoc left blank because the city straddles Waukesha and Jefferson counties.

## Not done
- Form 5500 check not run: no REJECT was for closure or no-establishment. No dated closure was found for any cluster.
- No tier proposed for STILL_UNCERTAIN, DUPLICATE_OF or REJECT rows.
- NAICS primary filled only where the set had a clear lead (ASYST 326199, Hentzen 325510, Amcor New London 326112, Stowe Woodward 326291); blank elsewhere.
