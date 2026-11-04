# Lane L2 notes (KY STRONG wave, 2026-11-04)

14 clusters in, 14 verdicts out (`verdicts.csv`).

| Verdict | Count | Clusters |
|-|-|-|
| VERIFIED_NEW_ORG | 7 rows, 6 organizations | 00063 Jones Plastic & Engineering; 00128 Kustom Group; 00044 American Fuji Seal; 00051 + 00013 Summit Polymers (one org, two sites); 00056 Signode; 00159 Creative Packaging Company |
| VERIFIED_NEW_SITE | 5 | 00042 Washington Penn (ORG-001193); 00113 Sealed Air (ORG-000566); 00091 Greif (ORG-001824); 00055 RTP (ORG-001093); 00014 PMC Organometallix (ORG-003061) |
| DUPLICATE_OF | 1 | 00117 Zeon -> SITE-003374 |
| STILL_UNCERTAIN | 1 | 00003 Amcor Shelbyville |
| REJECT | 0 | no dated closure found anywhere |

7 + 5 + 1 + 1 = 14.

## Tier rule used
- New organization: C.
- Site under a held org: B only when an own page names the plant AND states what is made there (Greif, RTP, PMC). Otherwise C (Washington Penn, Sealed Air).

## Flags for the integrator
1. **Zeon (00117)** is the held plant under a different street number: Zeon's Locations page prints 4111 Bells Lane; the federal row (and a Zeon supplier page seen as a search snippet) says 4100. Dedupe step 3 missed it only for that reason.
2. **HQ disagreement, Washington Penn:** own Locations page puts headquarters at 480 Johnson Road, Washington PA; held ORG-001193 carries Wapakoneta OH.
3. **Scope questions (owner-ruling territory, not self-ruled):**
   - Kustom (00128): printing-ink vehicles and overprint coatings; own data sheets say phenolic/hydrocarbon resin, pages never say "polymer". Verified on SCHEMA Ring 2 (inks, coatings); drop to STILL_UNCERTAIN if the owner disagrees.
   - PMC Organometallix (00014): organotin PVC stabilizers and tin catalysts (chemical synthesis). Accepted via held parent PMC Group's Ring 2 additive scope.
   - American Fuji Seal (00044): shrink-sleeve label maker. Atlas holds comparable label converters at Ring 1 (CCL Label, Century Label). No page ties "film production" to the Bardstown plant specifically.
   - Sealed Air (00113): the only activity evidence is a 2017 Louisville air-permit notice ("polyethylene foam manufacturing facility"); Sealed Air's own pages name the address only as a foam return location. Hold if own-site evidence is required.
4. **False-positive dedupe hit:** Creative Packaging Company (Shelbyville KY, creativepackagingco.com) is not ORG-000291 Creative Packaging Concepts (Elyria OH). Matched only on notes text.
5. **ZIP correction:** PMC federal ZIP 14008 should be 41008 (own PDF prints 41008).
6. **Summit Polymers** rows 00051 and 00013 both say VERIFIED_NEW_ORG with identical org fields; create the org once. Third KY plant (Lawrenceburg, 1250 Bypass North) is not in this packet.
7. **Other sites of these orgs not in the packet** (candidates for later waves): Jones Williamsburg KY (40 Williamsburg Plastics Road) and Rev-A-Shelf (12400 Earl Jones Way, Louisville); Washington Penn Winchester KY (1550 Rolling Hills Lane); Amcor 6850 Midland Industrial Dr.
8. **Signode** own-site witness is its Signode page on smartrecruiters.com (extruder job posting) plus signode.com Locations; materials left blank (PET versus PP at Florence not stated).
9. naics_primary left blank where the federal sets give no clear primary (Fuji, Greif, PMC, Amcor). RTP 325991 and Jones 326199 are majority picks, not certain.

## Checks run
- `atlas.py dedupe-check` by name+street for all 14 and by domain for the 6 new-org websites plus rev-a-shelf.com.
- All 12 quotes re-fetched and matched (whitespace-normalized, 25 words or fewer) with `verify_quotes.py`: 12 of 12 found. Greif, Creative, PMC and RTP quotes needed Jina Reader; `own_url` stays the company URL.
- Fetch budget: about 6 per candidate; Amcor stopped at the cap without a product statement.
- Search snippets are named as such in the notes wherever used; none is a quote.
