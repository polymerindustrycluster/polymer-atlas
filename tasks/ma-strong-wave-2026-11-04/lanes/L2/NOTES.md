# Lane L2 notes (MA STRONG wave, 2026-11-04)

Input: `input.csv`, 19 clusters. Output: `verdicts.csv` (19 rows, one per cluster).

## Counts
| Verdict | Tier | n | Clusters |
|-|-|-|-|
| VERIFIED_NEW_SITE | B | 4 | 00271 Universal Plastics (ORG-000620), 00277 Pexco (ORG-002534), 00143 Berry/Amcor Easthampton (ORG-002544), 00258 Rogers Foam (ORG-002535) |
| VERIFIED_NEW_SITE | C | 1 | 00367 Cuming Microwave (ORG-000088 PPG) |
| VERIFIED_NEW_ORG | C | 10 | 00301 Polyvinyl Films, 00414 CDF, 00317 Pittsfield Plastics Eng., 00403 Sinicon, 00454 Plastic Distributors & Fabricators, 00512 UFP Technologies, 00137 Barbour Corporation, 00557 Primary Colors, 00373 Hi-De Liners, 00355 MTD Micro Molding |
| STILL_UNCERTAIN | - | 3 | 00329 CAI, 00264 Nyacol, 00159 Sealed Air Holyoke |
| REJECT | - | 1 | 00447 Blank Industries (ice melt / salt; no polymer) |
| DUPLICATE_OF | - | 0 | no `sites_*.csv` street hit for any cluster (dedupe step 3 = 0 hits on all 19) |

## Method
- `python scripts/atlas.py dedupe-check` (name + street + city) for all 19, plus extra name and domain probes (UFP, Nyacol, Amcor, Cuming, PPG, Evantic, CDF, Barbour, Dallas Plastics, Magnera, Hi-De, domains hideliners.com and stretchtite.com). `atlas.py show` on ORG-002534/-002535/-002544/-000566/-000620.
- Own-site text came from WebFetch and WebSearch for discovery, then a read-only GET of each own_url (plain HTTP, tags stripped, whitespace collapsed) to check that every `own_quote` is a continuous exact span. Result: 16 of 19 quotes re-matched byte for byte this session (all rows with a quote that passes the check; word counts all <= 25). Three (CDF, Sinicon, Pexco) returned HTTP 403 on the re-check, a bot wall that appeared after repeated fetches; each of those spans was read earlier in the session from the live page (CDF and Sinicon via the plain GET, Pexco via WebFetch confirmation), so they are expected to match but the integrator should re-fetch them.
- A failed fetch was never used as evidence. No closure evidence was found for any cluster (so no closure REJECT).

## Items for the integrator
1. **HQ conflicts on held orgs.** pexco.com lists Atlanta GA as headquarters, Atlas has ORG-002534 at Morrisville PA. rogersfoam.com says Somerville MA is Corporate Headquarters, Atlas has ORG-002535 at Morrisville PA. ORG-000620 (Universal Plastics Group, Middlefield OH) may really be a Holyoke-based group (Holyoke prints as the group's contact address, company was founded in Massachusetts). Correct HQ/shard if confirmed; I changed nothing.
2. **Berry/Amcor 00143.** The Easthampton plant is a tube-extrusion plant now operated by Amcor (Amcor release 2026-04-21). Choose ORG-002544 (Berry Global) or an Amcor org (ORG-002907 / ORG-000665). It is a tube plant, not film.
3. **00367 Cuming.** No PPG page I could read names Avon, so tier C even though a held parent exists. Scope is a filled epoxy/silicone resin product; owner may want to look.
4. **Owner-ruling candidates (AGENTS rule 9), held as STILL_UNCERTAIN:** CAI (ink maker, binder not stated on any page read) and Nyacol (inorganic oxide additives incl. antimony pentoxide flame-retardant synergists and "polymer concentrates"). Settling facts are in each row.
5. **00454 PDF.** The federal row names Plastic Distributors & Fabricators; its domain now serves Evantic (Houston TX), which is not held. I proposed PDF as the org with Evantic as parent in the note. Process and material tags are Evantic-wide statements, provisional.
6. **00301 Polyvinyl Films.** Own site prints 38 Providence Rd, Sutton, and says "two manufacturing plants"; 19 Depot St (the federal and EPA TRI address) is not printed. Keep the federal street, flag it.
7. **00512 UFP.** 100 Hale St is HQ. Own site gives company-wide capabilities only. A 10-K says Haverhill, Byfield and Georgetown operations moved to Newburyport (SEC, not own-site).
8. **00159 Sealed Air Holyoke.** Own pages confirm an operating Holyoke facility, none states the product. Likely a B once a plant-activity page is found.
9. Input quirks: 00414 street/city columns were a single polluted string (split); 00447 county 'Middlesex County' normalized; 00447, 00557, 00512 counties blank or odd and filled from the city.
10. Vocabulary: `blow_molding` (umbrella, CDF) used only because the page gives no subtype; `thermoforming_unspecified` used for UFP/PDF; `extrusion_unspecified` for Easthampton tubes; `molding_unspecified` for MTD. Nothing outside SCHEMA 3.1/3.2.

## Not done
- No Form 5500 address check was needed (no closure REJECT). The Blank Industries REJECT is a scope reject, not a closure.
- Did not open pic-rag, CRM or any private source. No personal data recorded (no names, emails or phones).
