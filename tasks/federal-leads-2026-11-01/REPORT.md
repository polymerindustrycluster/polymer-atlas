# Federal leads packet: USAspending contract recipients + openFDA device establishments

Lane packet, produced 2026-11-01 by `scripts/build_federal_leads.py`. **Leads and link candidates only.** Nothing here is scope evidence, nothing was written under `data/`, no IDs were allocated, and every candidate below needs the integrator of record (AGENTS.md section 2 rule 7). Counts name their unit and filter.

## 1. Routes and exact terms

**Goal A: USAspending (no key).** Contracts only (award types A, B, C, D), `time_period` on `action_date` 2021-10-01 to 2026-09-30 (FY2022 through FY2026; FY2026 closed 2026-09-30 and the pull ran 2026-11-01), `naics_codes` as 4-digit prefixes **3252, 3255, 3259, 3261, 3262** (the API accepts NAICS filters of length 2, 4 or 6 only; `326` is rejected, and 326 has exactly two 4-digit children, 3261 plastics products and 3262 rubber products). Endpoints on `https://api.usaspending.gov/api/v2/search/`:
- `spending_by_category/recipient/`: in-window obligated dollars per recipient UEI (transaction level, so `obligated_usd_fy22_26` is dollars obligated inside the window, summed over prefixes).
- `spending_by_award/` (partitioned by prefix and date range so each query stays under the 50,000-row cap; awards deduplicated on `generated_internal_id` across partitions): recipient name, UEI, award NAICS (6-digit), recipient location. Used for award counts, NAICS mix and recipient address (most frequent address across the recipient's awards).
- `spending_by_award_count/`: partition sizing.

**Goal B: openFDA device registration and listing** (`https://api.fda.gov/device/registrationlisting.json`, api.data.gov key sent as an HTTP Basic header, shown here as `<KEY>`). One query per state x term, `limit=1000`, paged with `skip`:

```
search  = registration.state_code:<ST> AND registration.name:<term>*
<ST>    in CA, TX, FL, MI, IL, GA, IN, WI, NY, NC   (10 QCEW gap states; OH skipped by instruction)
<term>  in plastic, polymer, molding, moulding, rubber, extrusion, silicone, urethane, composite   (trailing wildcard on each, so 'plastics', 'composites' match)
api_key = <KEY>   (Authorization header; never in a URL, file or cache)
```

Name-token search only (openFDA has no leading wildcards, so a term buried inside a longer word, e.g. 'thermoplastics', is not found; 'RUBBER' as a separate word is). Listing records are collapsed to one row per FEI; `is_manufacturer` = establishment type includes 'Manufacture Medical Device' or the contract-manufacturer type. `us_agent` and `official_correspondent` (named individuals, phones) are never stored, per AGENTS.md section 6.

## 2. Headline counts

| Measure | Unit and filter | Count |
|---|---|---:|
| Distinct contract awards | awards with >=1 action FY2022-FY2026, award NAICS under 3252/3255/3259/3261/3262, de-duplicated | 665,603 |
| Recipient rows | distinct recipient UEIs (plus UEI-less names) in that award set | 4,756 |
| Recipient rows with a UEI | same | 4,756 |
| Obligated dollars | in-window obligations across all those recipients | $10,270,217,524 |
| FDA establishments | distinct FEIs in 10 gap states, registered name matching a polymer term | 60 |
| ...of which manufacturers | FEIs with a manufacture establishment type | 57 |
| ...of which registration status 1 | FEIs with `status_code` 1 (active) | 59 |

Distinct awards by award-NAICS prefix (unit: awards): 3252: 3,019, 3255: 445,121, 3259: 59,938, 3261: 119,585, 3262: 37,940.

Recipient rows per prefix from the category endpoint: 3252: 481, 3255: 664, 3259: 1,500, 3261: 2,287, 3262: 1,692. Reconciliation (AGENTS.md section 2 rule 10c): 0 recipients appear only in the award pull, 15 appear only in the category pull (`pull_flag` category_only_*; $860,343 of the total). The category endpoint filters on the NAICS of each *transaction* while the award endpoint filters on the award's own current NAICS, so a recipient whose modifications carried a 3252/3255/3259/326 code but whose award rolls up under another code shows up in category only. For those rows the award count and NAICS mix are blank, and the address was backfilled from one USAspending award record of the same UEI (10 backfilled, 5 without a location).

## 3. Match to the Atlas (AGENTS.md section 3 order)

Steps run: (0) exact registry id in `registry_links.csv`; (1b) FEI quoted in Atlas notes/sources; (2) normalized name against `legal_name` and `trade_names` of organizations + ecosystem (dba/aka split variants); (3) street address against site shards; (4) trade_names/notes substring. Neither source carries a website domain, so step 1 does not run. Classes: `MATCH_ORG` (step 2 or 3 hit), `POSSIBLE_REVIEW` (step 4 only, weak), `NO_MATCH`. `link_candidate` Y = exactly one org and either same-state evidence or same street; REVIEW = several orgs, no state agreement, or address-only. Y never means 'link now'; see caveats.

| Source | Rows | MATCH_ORG | link_candidate Y | link_candidate REVIEW | POSSIBLE_REVIEW | NO_MATCH | ALREADY_LINKED | MATCH_ORG rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| USAspending recipients (UEI) | 4,756 | 229 | 146 | 83 | 77 | 4,450 | 0 | 4.8% |
| openFDA establishments (FEI) | 60 | 10 | 2 | 8 | 5 | 45 | 0 | 16.7% |

By dollars, MATCH_ORG USAspending recipients hold $669,034,525 of $10,270,217,524 in-window obligations (6.5%). Existing `UEI` and `FDA_FEI` rows in `registry_links.csv`: 0 and 0, so every candidate below is a new row.

## 4. Registry-link candidates (for the integrator)

Per SCHEMA section 4.8, a `UEI` row is minted only on an exact UEI match taken from the source system's own record (here the USAspending recipient record, so the UEI is verified at source), with `match_basis` `usaspending_exact_uei` and `as_of` 2026-11-01. That this recipient *is* that Atlas organization still rests on a name or address match and is the integrator's call. All candidates are in `matches.csv` (`link_candidate` Y or REVIEW). Top Y candidates by in-window obligations:

| UEI | Recipient (city, ST) | Obligated FY22-26 | Atlas org | Step |
|---|---|---:|---|---|
| JXZLMHMXAFB4 | SICPA SECURINK CORP (SPRINGFIELD, VA) | $232,204,458 | ORG-004609 SICPA Securink Corporation [active] | 2 normalized name + 3 street |
| WPMTYSB6BFN1 | GOODYEAR TIRE & RUBBER COMPANY, THE (AKRON, OH) | $65,206,195 | ORG-000003 The Goodyear Tire & Rubber Company [active] | 2 normalized name |
| V32LJNFLKBT7 | RFD BEAUFORT INC. (SHARON CENTER, OH) | $46,994,137 | ORG-001459 RFD Beaufort Inc. [active] | 2 normalized name |
| CBMZJ3Z5SC89 | GOODRICH CORPORATION (JACKSONVILLE, FL) | $45,782,003 | ORG-004307 Collins Aerospace [active] | 2 normalized name + 3 street |
| WXRTZLL25AE5 | SEEMANN COMPOSITES, LLC (GULFPORT, MS) | $41,771,192 | ORG-004067 Seemann Composites, LLC [active] | 2 normalized name + 3 street |
| GAJ1F3WQCWY5 | THE SHERWIN-WILLIAMS COMPANY (CLEVELAND, OH) | $19,994,490 | ORG-000132 The Sherwin-Williams Company [active] | 2 normalized name |
| YZJ2CGFBMVY8 | PPG INDUSTRIES INC (ALEXANDER, AR) | $15,821,584 | ORG-000088 PPG Industries, Inc. [active] | 2 normalized name + 3 street |
| T8U2LNHJ2FV5 | FIBER DYNAMICS, INC. (WICHITA, KS) | $13,290,610 | ORG-003744 Fiber Dynamics, Inc. [active] | 2 normalized name |
| PK9NC2USJJX5 | STRUCTURAL COMPOSITES INC (MELBOURNE, FL) | $8,990,583 | ORG-002939 Structural Composites, Inc. [active] | 2 normalized name + 3 street |
| YK4JFU6UVRG3 | HENTZEN COATINGS INC (MILWAUKEE, WI) | $8,340,358 | ORG-003966 Hentzen Coatings, Inc. [active] | 2 normalized name |
| LM5KEWC6RUJ5 | SELMAX CORP. (SELINSGROVE, PA) | $8,092,795 | ORG-002657 Selmax Corp. [active] | 2 normalized name + 3 street |
| E86UEFDHJWK6 | ROCKMART FUEL CONTAINMENT, LLC (ROCKMART, GA) | $7,232,232 | ORG-004038 Rockmart Fuel Containment, LLC [active] | 2 normalized name |
| PJALL9CCHNH5 | ABBEY COLOR INC (PHILADELPHIA, PA) | $4,062,884 | ORG-002583 Abbey Color Inc. [active] | 2 normalized name + 3 street |
| WJLMR4HBJS65 | ROBIN INDUSTRIES, INC. (WINESBURG, OH) | $2,442,824 | ORG-000549 Robin Industries, Inc. [active] | 2 normalized name |
| PLKEXCTRU8K3 | CPCA MANUFACTURING LLC (DAYTON, OH) | $2,213,670 | ORG-000762 CPCA Manufacturing LLC [active] | 2 normalized name |
| UEASYHKFTW44 | LAIRD PLASTICS INC (IRVING, TX) | $2,098,131 | ORG-000059 Laird Plastics [active] | 2 normalized name |
| VD1NLZGAJ2L4 | DURAMAX MARINE, LLC (HIRAM, OH) | $1,880,132 | ORG-000317 Duramax Marine, LLC [active] | 2 normalized name |
| RBUKW28TMLJ2 | PPG INDUSTRIES, INC. (HUNTSVILLE, AL) | $1,818,700 | ORG-000088 PPG Industries, Inc. [active] | 2 normalized name |
| JT4FKJQPH454 | LOC PERFORMANCE PRODUCTS LLC (PLYMOUTH, MI) | $1,635,556 | ORG-003448 Loc Performance Products, Inc. [active] | 2 normalized name + 3 street |
| SPE2YDWHDYU4 | UTAH STATE UNIVERSITY (LOGAN, UT) | $1,350,072 | ORG-004676 Utah State University [active] | 2 normalized name |
| ULNULKJMJA75 | CAAP CO., INC. (MILFORD, CT) | $1,311,295 | ORG-004582 CAAP Co Inc. [active] | 2 normalized name |
| MNMTTXY53NQ4 | BRP MANUFACTURING CO (LIMA, OH) | $960,642 | ORG-000710 BRP Manufacturing Company [active] | 2 normalized name |
| RQJGN2NZMNC4 | SALEM-REPUBLIC RUBBER CO (INC) (SEBRING, OH) | $854,733 | ORG-000194 Salem-Republic Rubber Co. [active] | 2 normalized name |
| W5UKAHMN6334 | AIRTECH INTERNATIONAL INC (HUNTINGTON BEACH, CA) | $841,486 | ORG-003838 Airtech International, Inc. [active] | 2 normalized name + 3 street |
| Y1KQH3MMQPW5 | OPSEC SECURITY INC (LANCASTER, PA) | $789,776 | ORG-002449 Opsec Security [active] | 2 normalized name + 3 street |

UEI link candidates: 146 with link_candidate Y; 83 REVIEW. FDA_FEI link candidates: 2 Y; 8 REVIEW. FEI identifies an *establishment* while the table is org-keyed: record the FEI against the operator org of the matched site, and treat one-FEI-many-orgs as REVIEW.

Top FDA_FEI Y candidates:

| FEI | Establishment (city, ST) | Atlas org | Step |
|---|---|---|---|
| 3005562032 | FORMED PLASTICS, INC. (CARLE PLACE, NY) | ORG-003643 Formed Plastics Inc. [active] | 2 normalized name + 3 street |
| 3000199132 | BOEDEKER PLASTICS, INC. (SHINER, TX) | ORG-003593 Boedeker Plastics, Inc. [active] | 2 normalized name + 3 street |

## 5. Discovery leads (NO_MATCH) by state

A lead is an unmatched federal recipient or FDA establishment a verification lane may look at. It is not an Atlas record and not in scope until verified against a primary source. A NO_MATCH is a guarded no-hit, never a negative fact.

**USAspending NO_MATCH recipients (unit: recipient UEIs) by recipient state, top 20 by in-window obligations:**

| State | NO_MATCH recipients | Obligated FY22-26 |
|---|---:|---:|
| (no state: foreign) | 217 | $2,403,751,400 |
| MO | 58 | $1,092,792,137 |
| FL | 288 | $827,950,749 |
| TN | 51 | $777,238,076 |
| NJ | 188 | $765,057,762 |
| CA | 530 | $755,229,211 |
| PA | 222 | $327,436,064 |
| WI | 82 | $307,827,653 |
| TX | 316 | $239,816,768 |
| VA | 239 | $182,487,089 |
| CT | 83 | $175,176,777 |
| MN | 71 | $148,464,361 |
| NY | 216 | $136,968,620 |
| AZ | 74 | $129,897,369 |
| IA | 20 | $104,312,975 |
| OH | 150 | $104,027,557 |
| IL | 132 | $101,535,836 |
| GA | 123 | $77,688,951 |
| UT | 38 | $77,339,546 |
| ME | 14 | $65,919,318 |

**Top 10 QCEW gap states, both sources (unit: unmatched rows):**

| State | USAspending NO_MATCH recipients | their FY22-26 obligations | FDA NO_MATCH establishments | ...manufacturers |
|---|---:|---:|---:|---:|
| CA | 530 | $755,229,211 | 10 | 10 |
| TX | 316 | $239,816,768 | 5 | 5 |
| FL | 288 | $827,950,749 | 3 | 3 |
| MI | 132 | $58,637,842 | 3 | 3 |
| IL | 132 | $101,535,836 | 2 | 2 |
| GA | 123 | $77,688,951 | 4 | 4 |
| IN | 77 | $57,578,690 | 4 | 3 |
| WI | 82 | $307,827,653 | 3 | 3 |
| NY | 216 | $136,968,620 | 10 | 8 |
| NC | 94 | $65,313,094 | 1 | 1 |

Largest unmatched USAspending recipients in the gap states (top 5 per state by obligations; recipients whose award mix is only NAICS 325920 explosives manufacturing are left out of this table because that code, though inside the requested 3259 prefix, is not polymer work; they remain in the CSV, and `awards_excl_325920` lets a reader filter them):

| State | Recipient (city) | UEI | Obligated FY22-26 | Award NAICS mix (code:awards) |
|---|---|---|---:|---|
| CA | ARMTEC COUNTERMEASURES CO (COACHELLA) | KZLLWN8U3V91 | $245,817,474 | 325998:31;325920:27 |
| CA | VINYL TECHNOLOGY, LLC (MONROVIA) | W4BLGNEXYKD9 | $17,317,410 | 326150:280;326199:9;326299:2 |
| CA | F & M MICRO PRODUCTS INC (VAN NUYS) | E89AF6FBPU56 | $13,024,165 | 326140:15926;326299:715;325998:387 |
| CA | WESTLAND TECHNOLOGIES, INC. (MODESTO) | HMBSX7Z72UK4 | $11,875,937 | 325212:18;326113:18;326299:12;326199:9;325211:7;326150:1;326 |
| CA | SPLAY, INC (SAN JOSE) | SKGEQ7VRHER3 | $10,499,098 | 325211:29;326199:25 |
| TX | HID GLOBAL CORP (AUSTIN) | P62PT7KDP437 | $75,164,559 | 325211:11 |
| TX | M-PAK, INC. (ALEDO) | QGM1VMELTHF1 | $42,551,843 | 326111:20759;326199:171;325211:1;326150:1 |
| TX | FOAMTEC INTERNATIONAL, LLC (WOODWAY) | TK6ZFFKTFJ77 | $18,388,779 | 326150:1 |
| TX | DAY & ZIMMERMANN LONE STAR LLC (TEXARKANA) | W5U1L34L2NE7 | $9,007,206 | 325998:4;325920:2 |
| TX | IGCS, LLC (GUNTER) | CJKQM8GJU6C7 | $7,768,802 | 325520:49;325510:16;325211:6;326199:1 |
| FL | JEMNI INC (NAPLES) | X2BKMNKEFKX5 | $56,901,408 | 326199:161;325992:7;326111:7 |
| FL | PATTEN CO., INC. (LAKE WORTH) | C13AYKBB3AN5 | $16,508,178 | 326299:36;325520:1 |
| FL | KAYMONT CONSOLIDATED INDUSTRIES, INC. (MELBOURNE) | JB71EWNZNXK7 | $12,700,979 | 326299:68 |
| FL | VIKING LIFE-SAVING EQUIPMENT (AMERICA), INC. (MEDLEY) | HFBBTXCR8CN5 | $9,600,766 | 326299:13;325520:1 |
| FL | GLOBAL LOGISTICS STRATEGIES INC. (CAPE CORAL) | KHMGEK1ANNJ8 | $7,237,352 | 326220:31;326122:15;326111:9;325992:5;326199:5;325211:4;3262 |
| MI | ND DEFENSE LLC (MADISON HEIGHTS) | NAX6BAMAUNG9 | $19,931,135 | 326211:6;326122:3;326220:1;326291:1 |
| MI | CADILLAC PRODUCTS PACKAGING COMPANY (TROY) | NVCSLHLLFW58 | $6,363,812 | 326112:63 |
| MI | UNITED RESIN, LLC (ROYAL OAK) | KX6MPVJ297M4 | $2,768,371 | 325520:88 |
| MI | JANELS INDUSTRIES INC (DOWAGIAC) | C899NEQ26BA4 | $2,661,408 | 326299:35;326220:11;326199:5;326113:3;325211:2;325998:2;3261 |
| MI | MIDWEST FIBERGLAS FABRICATORS, INCORPORATED (MARINE CITY) | PNHRA59ZNEJ1 | $2,304,503 | 326299:388;325212:42;326220:39;326140:36;326113:34;326291:23 |
| IL | ELASTEC INC (CARMI) | XF4NUZH88QY6 | $4,395,864 | 326199:29 |
| IL | AAR SUPPLY CHAIN, INC (WOOD DALE) | TWJNLZXJ39F1 | $4,067,474 | 326220:71;326122:22;326291:3;326299:2;325510:1 |
| IL | SUPPLIED INDUSTRIAL SOLUTIONS, INC. (GRANITE CITY) | NKFAQ2J467L3 | $2,908,161 | 325520:2;326122:2 |
| IL | BURHANI ENTERPRISES INC (CHICAGO) | QMCVMXTXA9S1 | $1,251,992 | 326220:105;325510:41;325998:39;326122:28;326299:12;325520:10 |
| IL | FORMERRA LLC (ROMEOVILLE) | CHAQV8VD6VT8 | $1,048,590 | 325211:2 |
| GA | WINDOW FILM DEPOT INC. (MARIETTA) | S2FBQ5RNF8E7 | $12,547,261 | 326113:2 |
| GA | PRECISION HOSE,INC. (STONE MOUNTAIN) | HZVFYESM3PZ3 | $6,407,048 | 325920:3;326220:3 |
| GA | MOMAR, INCORPORATED (ATLANTA) | U2TVPCY6KKD5 | $6,125,039 | 325998:790;326140:3 |
| GA | CAIL TOOL & MACHINERY, INC. (MIDLAND) | GULMA36WZL17 | $5,943,977 | 325520:20;325211:17 |
| GA | ECI DEFENSE GROUP, INC. (LAWRENCEVILLE) | CW7HJMUQB621 | $5,000,840 | 326140:48;326220:31;326122:22;326291:16;325998:4;326199:2;32 |
| IN | AM GENERAL LLC (SOUTH BEND) | FR3PVZ8T9CS5 | $23,247,667 | 326220:42;326140:18;326122:9;326111:5;326199:2;326211:2;3262 |
| IN | GTA CONTAINERS, LLC (SOUTH BEND) | N552TG268QM8 | $7,155,479 | 326299:53;326220:22;325211:8;326122:7;325520:1 |
| IN | SECURITY PAKS INTERNATIONAL LLC (CARMEL) | P9JAK2634MF3 | $7,097,761 | 326199:9 |
| IN | GTA DRUM, INC (SOUTH BEND) | JH5BQKLDUB16 | $5,979,756 | 326299:57 |
| IN | BRUGH INDUSTRIAL ENGINEERING LLC (INDIANAPOLIS) | M9HQPNYQKYY7 | $2,889,695 | 325998:1 |
| WI | OSHKOSH DEFENSE LLC (OSHKOSH) | ZMXAHH8M8VL8 | $185,590,788 | 326220:1103;326211:487;326122:346;325998:41;326140:34;326299 |
| WI | POMP'S TIRE SERVICE, INC. (NEW BERLIN) | L581EX8Y41M3 | $74,913,442 | 326211:510;326122:3 |
| WI | PERIMETER SOLUTIONS LP (GREEN BAY) | UE6XGHPHW3T7 | $5,561,200 | 325998:4 |
| WI | TYCO FIRE PRODUCTS LP (MARINETTE) | H1PAVTLJBJ88 | $4,869,600 | 325998:1 |
| WI | OCENCO INC (PLEASANT PRAIRIE) | T99DCLB5NRH7 | $3,787,356 | 326299:7 |
| NY | ECHELON SUPPLY AND SERVICE, INC. (LIVERPOOL) | QF3MD1MU1651 | $20,225,020 | 326220:401;326122:203;325510:40;326299:31;325998:22;325211:2 |
| NY | DEFENSE ENERGY SYNDICATE, LLC (BRONX) | UYUDB14NM6S9 | $20,089,013 | 325998:381 |
| NY | STAR POLY BAG, INC. (BROOKLYN) | E5FRY6A42TL5 | $11,683,283 | 326111:10271;326199:205;325520:81;325211:41;326112:4;326113: |
| NY | PIONEER INDUSTRIES, LLC (FARMINGDALE) | TGGMDYLJGVN8 | $9,528,914 | 326122:463;326220:316;325998:29;326299:24;326199:16;325211:1 |
| NY | ACCUSPEC PACKAGING CORP (DUNDEE) | NH1AJLN95KL5 | $7,821,435 | 326111:6235;326150:477;326112:14 |
| NC | GOVERNMENT SALES, LLC (MOREHEAD CITY) | J3M5EM9GLUW5 | $21,822,813 | 325998:521 |
| NC | LC INDUSTRIES INC (DURHAM) | SWFSJMS9EHB2 | $17,670,130 | 326199:33;326111:2;325510:1 |
| NC | A.M.S. NETWORK, LLC (CHARLOTTE) | E4FCE9AKZ9P9 | $6,399,901 | 325510:13;325520:11;325998:9;326113:6;325212:3;326150:3;3261 |
| NC | KIDDE TECHNOLOGIES INC (WILSON) | HLQ2CYELNCE9 | $1,496,061 | 326220:32;326111:20;325998:13;326122:1 |
| NC | COLONY TIRE CORP (EDENTON) | C2GFBNTCJT44 | $1,232,778 | 326211:45;326150:1;326299:1 |

Unmatched FDA manufacturer establishments in the gap states, listing records as a rough size proxy (top 5 per state):

| State | Establishment (city) | FEI | Terms | Listing records |
|---|---|---|---|---:|
| CA | WRIGHT ENGINEERED PLASTICS, INC. (Santa Rosa) | 1000123971 | plastic | 10 |
| CA | PLASTICS PLUS TECHNOLOGY, INC. (Redlands) | 3010156053 | plastic | 6 |
| CA | CURRIER MOS PLASTICS LLC (San Jose) | 3008513917 | plastic | 3 |
| CA | DELTA MOLDING LLC (Woodland) | 3024491894 | molding | 3 |
| CA | SMOOTH-BOR PLASTICS (Laguna Hills) | 3006666710 | plastic | 3 |
| TX | ALPHA OMEGA POLYMER TECHNOLOGIES INC. (Kennedale) | 3013385253 | polymer | 2 |
| TX | GENESIS MEDICAL PLASTICS LTD. CO. (Cypress) | 3005543241 | plastic | 2 |
| TX | Coastal Plastics (Alvin) | 3006784951 | plastic | 1 |
| TX | SOUTHWEST QUALITY MOLDING (Manvel) | 3021561312 | molding | 1 |
| TX | TEXAS INJECTION MOLDING (Houston) | 3021887565 | molding | 1 |
| FL | SEAWAY PLASTICS ENGINEERING, LLC (Brooksville) | 3027071765 | plastic | 10 |
| FL | TMF PLASTIC SOLUTIONS LLC (Bradenton) | 3017087293 | plastic | 2 |
| FL | AMERICAN INDUSTRIAL PLASTICS, LLC (Daytona Beach) | 3005796366 | plastic | 1 |
| MI | Vaupell Midwest Molding and Tooling (Constantine) | 3003595343 | molding | 13 |
| MI | PETOSKEY PLASTICS (Petoskey) | 3002696493 | plastic | 4 |
| MI | PTI Engineered Plastics (Macomb) | 3007238674 | plastic | 3 |
| IL | ADVANTECH PLASTICS, LLC (Woodstock) | 3010852338 | plastic | 3 |
| IL | WISE PLASTICS TECHNOLOGIES (West Chicago) | 3013380372 | plastic | 1 |
| GA | INSERT MOLDING SOLUTIONS, INC. (Cumming) | 3009050824 | molding | 22 |
| GA | ADCO INTL PLASTICS CORP. (MARIETTA) | 1000140341 | plastic | 3 |
| GA | H & W MOLDING, LLC (Riceboro) | 3030244488 | molding | 2 |
| GA | SILICONE MEDICAL PRODUCTS & SERVICES (Flowery Branch) | 3021821373 | silicone | 2 |
| IN | Polymer Technology Systems (Whitestown) | 3002698769 | polymer | 22 |
| IN | RESTORATION MEDICAL POLYMERS (Columbia City) | 3015916578 | polymer | 6 |
| IN | HOOSIER PLASTICS INC (Terre Haute) | 3027345187 | plastic | 1 |
| WI | EVCO PLASTICS, DIV. DON EVANS, INC. (DEFOREST) | 2124274 | plastic | 2 |
| WI | EVCO Plastics-AMP (Deforest) | 3009590187 | plastic | 1 |
| WI | F&M PLASTICS, INC. (Osceola) | 3005911383 | plastic | 1 |
| NY | TESSY PLASTICS CORP. (ELBRIDGE) | 1317202 | plastic | 10 |
| NY | ALLIANCE PRECISION PLASTICS (Gates) | 1000120295 | plastic | 4 |
| NY | Tessy Plastics Corp. (Skaneateles) | 3012806810 | plastic | 4 |
| NY | CURRIER PLASTICS (Auburn) | 1000120319 | plastic | 2 |
| NY | BO-MER PLASTICS (Auburn) | 3005768810 | plastic | 1 |
| NC | Thunderbird Molding Greensboro (Greensboro) | 3010221586 | molding | 8 |

## 6. Caveats (binding on any use of this packet)

- **Award NAICS describes the contract, not the firm.** A distributor, defense prime or reseller can hold a 3252/3255/3259/326 award for a purchase it did not make in a plant. Recipient rows are firms that *sold under* those codes; polymer manufacturing is unproven. NAICS mix columns are award-level and must never populate an Atlas `naics_primary` (SCHEMA section 4.13 `code` claims need their own source class). 3255 (paint, coatings, adhesives) is dominated by commodity purchasing and carries the most awards; 3259 includes 325920 explosives manufacturing, which tops the dollar rankings and is not polymer work.
- **Recipient address is not a plant.** USAspending carries the SAM.gov registered address (often HQ, mailing or registered-agent). Do not create a site from it; a site needs the establishment's own physical-address evidence.
- **Name matching finds candidates; only the exact UEI/FEI links.** Same-name collisions across states and subsidiary/brand relationships are real: `link_candidate=Y` filters those risks, it is not a verdict. When in doubt do not merge (AGENTS.md section 3).
- **FDA registration is not polymer scope.** A name containing 'plastic' or 'rubber' on a device registration says nothing about processes, materials or ring. FDA rows are leads (and Ring 4 test candidates for a verification lane), never scope or tier evidence. Registrations are renewed annually; `reg_expiry_year` is a registration fact, not an operating-status fact. Contract manufacturers, repackagers and specification developers appear alongside real plants.
- **Coverage limits.** FDA name search is token-based, so firms whose names carry no term are missed by design. USAspending covers contract awards only (no grants, IDV parents or subawards), and only recipients with awards under these NAICS codes in the window.
- **Foreign / no-state recipients** are in the CSV but have no lawful site shard; hold them for an owner/schema ruling (AGENTS.md section 3).
- **Registry identifiers are verified at source:** UEIs come straight from USAspending recipient records and FEIs from the openFDA record. FEIs quoted in Atlas notes were used only to detect establishments already held, never as a source of identifiers.
- **No personal data stored.** FDA agent/correspondent contacts were dropped at ingest. No individual emails, phones or home addresses are in any output.
- The Atlas is read as of the working tree on the run date; rerun after integration passes. Tier ceilings for any future evidence row built from these sources: USAspending/SAM recipient record = `registry` (supports_B at most; an address alone supports_C); openFDA listing = `government_filing` for the registration's existence only.

