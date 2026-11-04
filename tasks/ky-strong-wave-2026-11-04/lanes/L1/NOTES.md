# Lane L1 notes (KY STRONG wave, 2026-11-04)

15 clusters in, 15 verdict rows out (`verdicts.csv`). 7 VERIFIED_NEW_SITE, 6 VERIFIED_NEW_ORG, 2 STILL_UNCERTAIN, 0 REJECT, 0 DUPLICATE_OF.
Every `own_quote` was re-checked by script against the fetched `own_url` (direct, page source or Jina); all 13 matched.

## Verdicts
| cluster | verdict | target | tier |
|-|-|-|-|
| LF-KY-00127 Flex Films USA | NEW_ORG | Flex Films (USA) Inc. | C |
| LF-KY-00011 RussTech | NEW_ORG (scope flag) | RussTech, Inc. | C |
| LF-KY-00066 Dart Horse Cave | NEW_SITE | ORG-002441 | B |
| LF-KY-00173 ViWinTech | NEW_ORG | ViWinTech Windows & Doors | C |
| LF-KY-00110 Coroplast Vanceburg | NEW_SITE | ORG-003476 Inteplast | B |
| LF-KY-00018 H.B. Fuller Paducah | NEW_SITE (closure announced) | ORG-000870 | B |
| LF-KY-00071 Green Tokai Maysville | NEW_SITE | ORG-000865 | B |
| LF-KY-00069 Jones Plastic Williamsburg | NEW_ORG | Jones Plastic & Engineering | C |
| LF-KY-00089 AGI Polymatrix | NEW_SITE | ORG-003420 Westfall Technik | B |
| LF-KY-00140 Macro Plastics Shelbyville | NEW_SITE | ORG-004957 | B |
| LF-KY-00154 TRAC Tire Services | NEW_ORG | TRAC Tire Services, LLC | C |
| LF-KY-00144 Benda-Lutz | STILL_UNCERTAIN | - | - |
| LF-KY-00073 Sun Chemical Hopkinsville | STILL_UNCERTAIN | ORG-001489 | - |
| LF-KY-00218 Gracious Living KY | NEW_ORG | Gracious Living Kentucky, Inc. | C |
| LF-KY-00196 Lastique | NEW_SITE | ORG-001477 Aurora | B |

## Integrator flags
- **Closure announced, not complete.** H.B. Fuller Paducah: WPSD (Aug 2026) reports a company announcement of closure by end of Q1 2027. Per AGENTS section 3 an announcement is not a status change; kept VERIFIED. Suggest `monitor_watch` and a re-check after Q1 2027.
- **Dedupe false positive.** Coroplast LLC (Vanceburg) is not the step-4 hit ORG-003515 Coroplast Tape Corporation (SC). Coroplast's own About page says it joined Inteplast Group in 2014, so the target is ORG-003476. Alternative model: a separate Coroplast LLC org with `parent_org_id=ORG-003476`.
- **Brand/parent matches missed by the name check** (addendum item 3): Lastique is an Aurora Material Solutions company (ORG-001477); AGI Polymatrix is Westfall Technik's DBA (ORG-003420); Macro Plastics is now IPL Macro. macroplastics.com redirects to iplschoeller.com, and ORG-000903 IPL Inc. is held. ORG-004957 probably needs `parent_org_id=ORG-000903` (integrator call).
- **HQ disagreements.** ORG-001489 Sun Chemical: Atlas HQ Amelia OH, company news releases say Parsippany NJ. ORG-003420 Westfall: Atlas Las Vegas NV, its own page footer shows Tempe AZ. ORG-004957 Macro: Atlas Union Gap WA, trade press says Fairfield CA.
- **Scope questions (not self-ruled).** RussTech: core line is concrete admixtures; only the acrylic cure-and-seal sealers are polymer (Ring 2 test 1 passes on that line). Sun Chemical and Benda-Lutz: inks and metallic pigments need a resin-binder product shown on an own page.
- **Owner-site gaps.** Gracious Living: own site never names Morgantown or Kentucky; site rests on federal rows plus trade press (tier C). Dart Horse Cave and Macro Shelbyville: own pages name the plant but not the activity; activity is company-level plus federal NAICS, so `processes` and `materials` are blank.
- **Non-US parents.** Flex Films (USA) Inc. is a UFlex group member (India); parent org not created or asserted. Gracious Living is Canadian ("Born in Canada in 1980"); HQ city not stated, left blank.
- **More KY sites for later packets, not created:** Jones Plastic HQ Jeffersontown (2410 Plantside Dr) and Rev-A-Shelf (12400 Earl Jones Way, Louisville); Dart Polymers Owensboro is already held (SITE-005057).
- **County correction:** Benda-Lutz input says "Boone County"; Independence KY is Kenton County (unchecked, entered as Kenton). ViWinTech and Gracious Living input county blank, filled from the city (McCracken, Butler).
- **Page-source / render notes:** the Green Tokai quote is in the page's meta description, not the visible body. coroplast.com returns 403 to plain fetch, so read via Jina. hbfuller.com/en/locations and the TRAC careers posting are JavaScript-rendered, so use Jina to see the quote.
- **Tier B/C rule used.** Federal source plus an own-site page naming the plant is B, including when that page shows the plant but not the activity. New organizations are C regardless.
- **Searches run per candidate:** dedupe-check by name (best name plus up to 3 variants), street, and city; ripgrep over all org and site shards for brand strings (flex film, uflex, russtech, viwintech, coroplast, inteplast, westfall, polymatrix, jones plastic, trac, benda, gracious, lastique, aurora, sun chemical, macro, green tokai, dart, fuller, IPL, eckart).
- No emails, phones or personal data are in the verdicts file. Page text was treated as data only; no embedded instructions were encountered.
