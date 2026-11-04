# Lane L2 notes (NY STRONG wave, 2026-11-04)

17 input clusters, 17 verdicts in `verdicts.csv`. All 17 `own_quote` strings were re-fetched this session and found verbatim
(whitespace and curly-quote normalized); only the Mercury Paint about page needed the Jina fallback (direct fetch returned 429).

## Counts
- VERIFIED_NEW_ORG: 12 (00357 Harbec/ADDMAN, 00329 U-C Coatings, 00235 Bison Bag, 00092 Oneida Molded Plastics, 00013 Mercury Paint, 00504 CJK, 00483 Apple Rubber, 00563 ECK Plastic Arts, 00475 Rimco, 00251 Nortek Powder Coating, 00560 Aladdin, 00548 PM Plastics)
- VERIFIED_NEW_SITE: 1 (00356 Finzer Roller Palmyra under ORG-002709)
- REJECT: 3 (00488 Echelon, 00133 Fleurchem, 00059 Sumitomo Rubber USA)
- STILL_UNCERTAIN: 1 (00314 Hutchinson Industries Buffalo)
- DUPLICATE_OF: 0
- Total 17.

## Dedupe
Ran `atlas.py dedupe-check` (name, brand/alias, street, city, zip) for all 17 plus `rg` over every organization and site shard for brand
names (Rodgard, Hutchinson, Sumitomo, UC Coatings, Harbec, ADDMAN, Echelon, Aladdin, Rimco, PM Plastics, CJK, ECK, Nortek, Mercury,
Apple Rubber, Fleurchem, Bison). No street hit at any cluster. Only organization-level hits were unrelated name collisions
(Aladdin -> Mohawk ORG-004254 carpet brand; Echelon -> Hentzen ORG-003966 note text; Rimco -> Grimco MO; Hutchinson North America
ORG-004239 and Hutchinson Sealing Systems ORG-004310 are different Hutchinson entities) and Finzer (below).

## Flags for the integrator
1. **Finzer 00356.** Only a step-4 notes hit, no site at this street. Written as VERIFIED_NEW_SITE under ORG-002709
   ("Finzer Roller Inc. Willow Street", HQ Willow Street PA). Finzer's locations page lists 12 plants and states no HQ, so the held
   org's HQ is worth a look. Tier B (federal + own-site page naming the plant).
2. **Harbec 00357.** Plant is now "ADDMAN Polymer" (page: "HARBEC is now a part of ADDMAN"). Verdict creates ADDMAN Group
   (HQ Fort Myers FL, Lee County, from addmangroup.com company-overview) as the org. ADDMAN also lists polymer, metal and precision
   sites elsewhere that are not in this packet. Integrator decides whether the org of record is ADDMAN Group or Harbec Inc with an
   ADDMAN parent; the site does not state a legal-entity suffix.
3. **Scope questions (not self-ruled).**
   - 00488 Echelon: REJECT as a general industrial hose distributor/assembler. If the owner wants hose distribution and custom hose
     assembly counted as Ring 3, reopen.
   - 00329 U-C Coatings: coatings maker (latex lumber paint, waterborne stains) taken under the Ring 2 coatings decision; Anchorseal is
     a wax emulsion and the site does not say which plant makes what. Processes left blank.
   - 00356 Finzer: roll coverings in rubber, polyurethane, silicone, fluoropolymer. Same product class as held PA site.
4. **Weak plant witness (org record is solid, plant location rests on federal rows):** 00013 Mercury Paint (site never calls the
   Farragut Road building the plant; second site 3326 Merritt Ave Bronx is a distribution location), 00475 Rimco (HQ and warehouse
   at Horseheads; forming facility described only as "in the Finger Lakes Region").
5. **HQ disagreements:** none against held records. HQ cities for new orgs come from the company's own pages (address on contact or
   about page). Apple Rubber, CJK, Oneida, Bison Bag, ECK, Rimco, PM Plastics, Mercury, Nortek, Aladdin, U-C Coatings: HQ = the packet
   city. Hutchinson Industries HQ is Trenton NJ (not written, since the verdict is STILL_UNCERTAIN).
6. **Closure 00059 Sumitomo Rubber USA, Tonawanda.** Dated 7 Nov 2024 termination of all production (company's own
   srigroup.co.jp notice plus WIVB/BTPM). Form 5500 check: only Sumitomo Rubber USA sponsor in the spine is EIN 341899137 at
   105 Crosspointe Pkwy, Getzville NY, a different address, so it does not block the reject. The plant is being sold to Hwa Fong
   Rubber (USA); that operator is a possible later lead.
7. **Additional sites seen, not in this packet:** Aladdin Packaging, 40 Governor Dr, Newburgh NY 12550; Oneida Molded Plastics acquired
   Austro-Mold, Rochester NY.
8. **00314 Hutchinson Industries Buffalo (Rodgard).** STILL_UNCERTAIN. Settling fact: a Hutchinson/Rodgard page stating rubber or
   polymer runflat components are molded, mixed or cured at Buffalo (versus metal runner assembly).

## Method notes
- County: the federal rows left county blank for 00488, 00504, 00483, 00560, 00563, 00475, 00548; filled from the city/ZIP
  (Onondaga, Monroe, Erie, Suffolk, Broome, Chemung, Erie). County is derived, not printed on the company pages.
- `naics_primary`: the specific 6-digit code from `naics_set` (rollup codes ending 00 ignored); blank where none was clear.
- Processes and materials come from the cited company pages only; where a page used a different page than the quoted one, `note`
  says which.
- Search snippets were used only to find URLs; every quote was copied from a page fetched in full.
- No `data/` edits, no git. Helper scripts live in the session scratchpad, not the repo.
