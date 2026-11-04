# Lane L2 notes (GA STRONG wave, 2026-11-04)

17 clusters. Counts (unit: input clusters): VERIFIED_NEW_ORG 8 (all tier C), VERIFIED_NEW_SITE 1 (tier B), REJECT 5, STILL_UNCERTAIN 3, DUPLICATE_OF 0.

Dedupe: `atlas.py dedupe-check` (name, street, city, zip) run for all 17. Street step 3 found 0 hits everywhere. Name hits only for Toyo (ORG-003097, ORG-003109), Dart (ORG-002441, ORG-002474) and Kraton (ORG-000925). Piedmont has a parent candidate (HEXPOL Compounding ORG-000103, found by a HEXPOL name search, not by the Piedmont check).

## Verified
- Toyo (LF-GA-00246): new site under ORG-003097, tier B (own press release names the White, Georgia factory).
- New orgs, tier C: Selit, Crown USA, Enplas USA, Resilux America, NIBCO, Polytech Fibers, Piedmont Resin Supply, GreenView Floors.

## Rejects (scope, not closure; no Form 5500 closure check needed)
Momar (maintenance chemicals/greases), J&S Chemical (die-casting lubricants), Pyrotechnic Specialties (energetics), Prayon (phosphates), Symrise (fragrance ingredients). No closure rejects.

## Still uncertain
- Dart Lithonia: page names the site but not the product. Likely VERIFIED_NEW_SITE (ORG-002441) once a page states the product.
- Kraton Savannah: pine-chemical resins; scope is an owner ruling (AGENTS 2 rule 9), not self-ruled.
- Sasco Albany: rubber anti-tack/release agents; same owner-ruling issue (Ring 3 chemical supply?); no own page names Albany.

## Flags for the integrator
- NIBCO: quote comes from a search excerpt of nibco.com/join-our-team/locations/greensboro-georgia/ because WebFetch returned an empty page. Re-fetch before applying.
- Crown USA: scope borderline (thermoplastic pavement marking); a MapQuest "Closed" label is not dated evidence and was ignored. Possible extra sites (Thomaston GA, Foley AL) unverified.
- Polytech Fibers: fibers are only a secondary NAICS in SCHEMA 2.2 with no edge-case ruling. Assumed in scope, easy to revoke. Second plant at 132 Polytech Drive not in the federal row.
- Piedmont: the HEXPOL plant page returned 403; street rests on the federal row. Parent link to ORG-000103 is the integrator's call.
- Enplas: group site says "Atlanta, GA" manufacturing; Marietta street comes from the privacy policy (via search excerpt) and the federal row.
- Selit and Resilux: quotes are activity-only because Commerce / Pendergrass appear only in address or list blocks. Resilux plant-level facts are on resilux.com/en/about-us/business-units.
- Symrise reject quote comes from a trade-press page (Area Development), not an own-site page; the Symrise site fetch gave no plant-level text.
- Counties left blank where the federal row had none. No own-site page contradicted a federal address.

## Fetch notes
Failed fetches (certificate errors for enplasusa.com, crowntechnology.com, jschem.com; 404s; JS-rendered nibco.com and dartcontainer.com) were treated as route unavailability, not evidence. Fetch tool summaries are model-paraphrased in places; every quote above is as returned in quotation marks by the fetch, and the integrator re-checks them.
