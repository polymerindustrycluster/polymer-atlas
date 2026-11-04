# Lane L2 notes (MN STRONG wave, 2026-11-04)

16 input clusters, 16 verdicts in `verdicts.csv`.

| Verdict | Count | Clusters |
|-|-|-|
| VERIFIED_NEW_ORG | 12 | 00249 REO, 00351 Velosity, 00063 Styrotech, 00140 Cortec, 00216 7-Sigma, 00282 Spectrum/Donatelle, 00251 Mikros, 00103 Acrotech, 00257 Avon, 00245 Aroplax, 00266 Fenix/Sierra, 00254 Olsen |
| VERIFIED_NEW_SITE | 3 | 00096 Entegris (ORG-002881), 00207 Flint (ORG-001611), 00128 Cortec Advanced Films (parent not yet held, see below) |
| STILL_UNCERTAIN | 1 | 00250 NTIC |
| REJECT / DUPLICATE_OF | 0 | |

## Method
- Dedupe: `atlas.py dedupe-check` took over two minutes per call (it reloads all shards), so I ran an equivalent read-only scan
  of every `organizations_*.csv` and `sites_*.csv` once: org names, trade names, websites and notes against names, brands and
  domains (reoplastics, velosity, teamvantage, styrotech, cortec/cortecvci, 7-sigma/7-s3, donatelle, spectrumplastics, mikros,
  acrotechinc, avonplastics, mastermark, aroplax, ntic/zerust/natur-tec/naturbag, fenixspc/sierrapaint/surecrete, flintgrp,
  olsentool/olson); site rows against normalised street. Result: no street duplicates anywhere; only held-org hits are
  Entegris (ORG-002881) and Flint (ORG-001611).
- Fetches through TinyFish fetch_content, Jina for the JS-rendered Flint page, pdftotext on the Cortec corporate book, SEC 10-K
  text for NTIC. Quotes were copied from pages I fetched, not search snippets.
- Tier: B = federal source + own-site witness. For VERIFIED_NEW_ORG rows the `tier` column holds the site tier (B); the org record is C per the brief.
- County values are geography (the pages do not print counties); street and ZIP come from the federal row except where noted.
- `naics_primary` is filled only where the federal set points at one code (Styrotech 326140, Cortec 325998, 7-Sigma 326299,
  Entegris 326199, Fenix 325510, Flint 325910, Cortec Advanced Films 326113); left blank elsewhere.

## Flags for the integrator
1. **Cortec pair (00140, 00128).** No Cortec record exists. Create Cortec Corporation from 00140, then attach 00128 (its
   `held_org_id` is blank). The org's Ring 1 case is the Cambridge film plant; the St. Paul HQ site is chemistry plus coatings and a foam
   infusing line, so its polymer scope is the thinner of the two (SCHEMA coatings ruling).
2. **Donatelle (00282).** Now Spectrum Plastics Group (PPC Industries, Inc., a DuPont business, bought July 2024). Proposed org is the
   operator, Donatelle a former name, DuPont as ultimate parent. Do not merge with ORG-000040 Spectrum Plastics Corp. (Cuyahoga Falls, OH). Input `fusion_refs`
   ORG-003483 (Northstar Maintenance Management) is a false match on the town name.
3. **City correction.** 7-Sigma (00216): own site says New Hope, federal row says Minneapolis.
4. **Entegris (00096).** 101 Peavey Road is a separate address from held SITE-003063 (117 Jonathan Blvd N); both are on Entegris's own list. Treated as a new site; merge as a campus if the integrator prefers.
5. **Flint (00207) scope.** Printing inks/coatings plant; no page states a resin binder or the on-site process, so processes and materials are blank. Ink-only plants may need an owner ruling. Quote needs Jina to re-fetch (JS page).
6. **NTIC (00250) STILL_UNCERTAIN.** Settling fact: a page saying what is made at Circle Pines. Also NTIC's 10-K reports an owned
   Beachwood, Ohio building (office, manufacturing, lab, warehouse) and the Atlas holds no NTIC record, so this is an Ohio lead.
7. **Weak address witnesses** (street from federal row plus search-snippet footers, not from fetched text): Avon (210 Ampe Dr), Aroplax (200 Chelsea Rd), Olsen (4060 Norex Dr). The company pages I fetched name the city and the activity.
   Avon HQ is blank (not stated on pages read).
8. **False step4 hits** in the input: Fenix (ORG-004841 Reno, ORG-002330 Exton) and Flint (ORG-004150 Hendersonville) are not related.
9. **More Velosity sites** are on its own page: CMD Forest Lake 22455 Everton Ave N, Brooklyn Park 6835 Winnetka Cir, Rogers 14194 Northdale Blvd; not in this lane. Fenix lists plants in IL, FL, TX (trade press, unfetched).
10. Cambridge ZIP: federal row 55005, Cortec's own book prints 55008. Federal ZIP kept.
11. HQ disagreements with federal rows: none beyond the 7-Sigma city.
