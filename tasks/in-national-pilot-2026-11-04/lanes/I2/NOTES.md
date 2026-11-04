# Lane I2 notes (2026-11-04)

18 input clusters, 18 verdicts. Unit: lead-fusion STRONG clusters (Indiana establishments), one verdict each.

| Verdict | Tier B | Tier C | No tier |
|-|-|-|-|
| VERIFIED_NEW_SITE (6) | 3 (Silgan Ligonier, MonoSol La Porte, Momentive Garrett) | 3 (Nishikawa Cooper Bremen, Amcor Franklin, Berry Goshen) | |
| VERIFIED_NEW_ORG (7) | 0 | 7 (APM, Color Master, Trivalence, American Window, Marian, Diamond Plastics, Elite Crete) | |
| REJECT (2) | | | Mays Chemical (distribution), Blue Grass Chemical (inorganic salts) |
| STILL_UNCERTAIN (3) | | | MultiSeal Evansville, GDC Goshen, C3E/Chem Tech Bristol |
| DUPLICATE_OF (0) | | | |

## Dedupe
`atlas.py dedupe-check` (name, street, city, zip, plus domain for the verified own sites) found no street (step 3) hit for any cluster, so no DUPLICATE_OF. Held-org hits resolved as new sites under ORG-004461, ORG-001115, ORG-004456, ORG-000665, ORG-002544, ORG-004233. Not merged: ORG-002923 Best Diamond Plastics (Chicago) is a different company from Diamond Plastics Corporation (Grand Island NE). ORG-004153 BRC, ORG-000880 Hexion and the other step-4 hits are notes-text matches only. Color Master is not Therma-Tru (ORG-001572): Therma-Tru's Butler plant is SITE-005038 at 601 RE Jones Rd.

## For the integrator
- Own-site quotes came from a summarizing fetch tool, not raw HTML. Re-check every `own_quote` against the page, especially the curly apostrophes (Marian, American Window) and the Momentive and Silgan spans.
- Own-site witness with plant and activity: Momentive (B), Marian (plant_and_activity, new org so C). Plant-only witnesses: Silgan, MonoSol, Trivalence. Others are activity-only or federal-only.
- Scope calls left to the owner (AGENTS §2 rule 9): American Window and Glass (vinyl window fabricator, ring 1 vs ring 4) and Marian (die-cut converter of purchased foam, rubber, silicone: ring 1 vs ring 3 contract_services).
- Trivalence: a 2025 merger into Star Plastics (ORG-003044) was seen in search snippets only (Recycling Today, PrivSource), so I did not set a parent; the site keeps the Trivalence name and shows a Star Plastics banner.
- Berry Goshen and Amcor Franklin: Amcor completed the Berry acquisition 2025-04-30. The held orgs (ORG-002544 Berry Global, HQ recorded Evansville; ORG-000665 Amcor Flexibles North America, Bellevue OH) are imperfect homes; pick the best operating entity.
- One rule for new orgs with no own page: trade press or directories do not carry polymer scope, so MultiSeal, GDC and C3E are all STILL_UNCERTAIN (identity is solid for each; the settling fact is an own-site page naming the plant and the polymer base).
- `org_hq_county` is blank for every new org because no site prints a county. Site-level `county` is the federal row's value except American Window (Vanderburgh), Marian (Marion) and Diamond (Delaware), where the federal row was blank and I derived it from the city.
- Marian materials are blank: the foam, silicone and rubber lines appear only in the home-page menu, not on the Indiana page used as `own_url`.
- B tier on a bare-address witness (Silgan, MonoSol) follows the brief's rule (federal source plus own-site witness) and matches I1's Genpak call; if the owner wants activity stated on the page, both drop to C.
- Diamond Plastics Muncie: a MapQuest 'Closed' flag was not treated as evidence; ECHO shows 2026-04 activity and ITA 2026-04-09. The site pages I could read do not name Muncie.
- No dated closure found for any cluster. Form 5500 check was not needed (no closure-based REJECT). Both REJECTs are scope rejects.
- Fetch failures (not evidence): multiseal.com (socket hang up), gdccorp.com (connection refused), gdcinc.com (parked redirect), IndustryNet (403), amcor locations (404), dpcpipe.com plants pages (404), niscoseals.com about/contact (404).
- Fetch budget was exceeded on a few clusters (about 6-8); all were stopped at the first primary signal or when sites would not resolve.
