# Lane L1 notes (MA STRONG wave, 2026-11-04)

19 clusters in, 19 verdict rows out (22 columns each, parsed clean).

| Verdict | Count | Tier |
|-|-|-|
| VERIFIED_NEW_ORG | 11 | all C (brief: a new organization is C) |
| VERIFIED_NEW_SITE | 6 | 2 B (Inteplast Westborough, Toner East Longmeadow), 4 C |
| STILL_UNCERTAIN | 2 | none (Nypro Clinton, Harvey North Dartmouth) |
| REJECT / DUPLICATE_OF | 0 | |

## Method and limits
- Dedupe: `atlas.py dedupe-check` (name, street, city, state, zip) for all 19, plus domain/name checks on parent and brand names. No street hit, so no DUPLICATE_OF. Name hits: Altium (ORG-001408), Saint-Gobain (ORG-000035), Inteplast (ORG-003476), Toner (ORG-001851 via trade name). Polyfoam resolved by research to Altor Solutions (ORG-002146).
- WebFetch is a summarizing fetcher. Quotes were taken from its verbatim excerpts; the integrator should re-fetch each `own_url`. Two quotes carry non-ASCII characters (an en dash in the Creative Materials row, a trademark sign in Franklin Paint).
- Fetch failures (403, DNS, ECONNRESET, SSL, timeout) were treated as availability only: cri-tech.com, newenglandplastics.com, careers.altiumpkg.com, saint-gobain datasheets, inteplastef.com locations, unitedsolutions.com (parked for-sale page). None was used as evidence of closure.
- `naics_primary` is the first code in `naics_set`, which is the ITA/OSHA-carried code in the lead-fusion row. For three rows the set had a malformed or repeated token (Saint-Gobain, Toner, Inteplast); I took the repeated or first clean code. NAICS never settled scope.
- The Form 5500 check was not needed because no REJECT for closure was issued.

## Items for the integrator or owner (not self-ruled)
1. Lacerta pair: LF-MA-00227 creates the org, LF-MA-00459 is a second Mansfield site under it (same EIN 043180539). Its `held_org_id` is `PENDING:LF-MA-00227`, not an ORG id.
2. Kayaku (LF-MA-00154): epoxy photoresists for microelectronics. Verified as Ring 2 polymer coatings on the company's own self-description, but it is a borderline scope case with no precedent in SCHEMA section 1. Owner ruling if wanted.
3. Toner (LF-MA-00417): the held org ORG-001851 is Modern Mold & Tool Corp. (OH division) carrying the trade name Toner Plastics Group. Toner Plastics, Inc. (EIN 043092727) is a different legal entity, so a new site under ORG-001851 may be the wrong shape; a parent org may be better.
4. Franklin Paint (LF-MA-00034): acquired by Potters Industries 2024-08-01 (own timeline page). Potters is held as ORG-001921. Filed as a new org, not merged, with the parent link left to the integrator.
5. Nypro Clinton (LF-MA-00070): Jabil announced molding shutdown by 2026-12-01 but says NyproMold (tooling) and NP Medical continue on the campus. Re-check after Dec 1; this could become a Ring 3 tooling site rather than a closure.
6. Harvey (LF-MA-00357): window and door plant, no own-site statement of vinyl extrusion or molding at Dartmouth, so scope is unproven.
7. United Solutions (LF-MA-00294): no usable own site; owned by CREO Group since 2024-09. Filed at C on federal plus trade press. CREO Group is not in the Atlas.
8. Placon (LF-MA-00115): HQ is Madison, WI, so the org shard follows WI. The West Springfield site is the injection-molding plant (federal name PLACON IM INC).

## Dedupe searches run
Steps 1-4 on each cluster with name, street, city, zip, and, where a company domain was known, step 1 on that domain. All clean except the name hits listed above.
