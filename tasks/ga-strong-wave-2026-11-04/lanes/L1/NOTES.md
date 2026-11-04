# Lane L1 notes (GA STRONG wave, 2026-11-04)

Input: 17 clusters. All 17 have a verdict in verdicts.csv.

## UNFINISHED
None. Every cluster in input.csv has a row. Two rows need a follow-up (below).

## Counts (verdict, tier)
- VERIFIED_NEW_ORG, tier C: 8 (IMS Gear, Custom Profiles, Kumho Tire Georgia, Austin Urethane, Gerresheimer Peachtree City, Thomson Plastics, SK Microworks America, Cady Bag)
- VERIFIED_NEW_SITE, tier B: 5 (Freudenberg LaGrange, Primex Oakwood, Conwed Athens, Behr McDonough, Millwork & Panel Social Circle)
- REJECT: 2 (Enchem America, scope; BioLab Conyers, scope plus closure)
- STILL_UNCERTAIN: 1 (Hanwha Advanced Materials Georgia)
- DUPLICATE_OF: 1 (SNF Riceboro -> SITE-005339)

## Method
- atlas.py dedupe-check run for every cluster (name, street, city, zip). No step-3 street hits. Name hits: SNF (ORG-004219), Freudenberg (ORG-000851), Primex (ORG-003504), Behr (ORG-001610), Millwork & Panel (ORG-004212, found beyond the input hits). Conwed (ORG-003466) was found by a name scan of the org shards.
- Pages read with WebFetch and with curl (exact-text check, because WebFetch paraphrases quotes). Each own_quote was read from fetched text, one continuous span, 25 words or fewer.
- No data/ edits, no git.

## Items the integrator should look at
1. Entity-boundary calls (new org vs site under a held org), made toward the "false split is cheap" side or the attach side as noted per row:
   - Kumho Tire Georgia: proposed new org; sibling of ORG-001843 (Kumho America Technical Center, Akron).
   - Gerresheimer Peachtree City: proposed new org; held ORG-000854 is Gerresheimer Primary Packaging Plastics, Berlin OH.
   - Freudenberg LaGrange: attached to ORG-000851 (Freudenberg-NOK Sealing Technologies, Milan OH, described as packaging/distribution). Weakest attach in the lane.
   - Millwork & Panel: attached to ORG-004212 (Claremont NC); CertainTeed LLC ORG-002738 is the other possible parent.
2. Thomson Plastics: live thomsonplastics.com serves a hosting default page, so own_url is a Wayback copy of the company page. Availability signal only, not a closure. Trade press reports an acquisition by Amara Industries in Dec 2025 (not checked at the primary).
3. IMS Gear: own-site witness is a job PDF on jobs.imsgear.com, not a plant page. HQ is German (INTL shard).
4. Gerresheimer: the Peachtree page does not itself say "plastic"; scope relies on the Medical Systems injection molding page and the mold-building statement.
5. Hanwha (STILL_UNCERTAIN): settling fact is a Hanwha/HAGA-owned page stating EVA film production at the Bartow site. Federal rows and the Qcells blog (a sister company) support operation.
6. Counties not in the federal row were supplied by the lane: Peachtree City (Fayette), Thomson (McDuffie), Covington (Newton), Hanwha (Bartow). ZIP differences on own sites: Austin Urethane 31719 vs 31709, Conwed 30608 vs 30601. Federal values kept.
7. Behr quote is from an EPD PDF on behr.com that names McDonough among three production facilities; the plant address comes from jobs.masco.com/behrpaint locations.
8. Several `processes` and `materials` cells are blank on purpose: the page did not state them for that plant (Primex, Conwed, Kumho materials, Millwork processes). A few tags are soft and flagged in the row note (coating_formulation, films_flexible_packaging, laminating).

## Not done
- No Form 5500 check was run for either REJECT; the BioLab reject rests on scope first, and neither cluster carries a 5500 sponsor row.
- Own-site Hanwha, Enchem and BioLab company pages were not fetched (not resolvable or not needed for scope).
