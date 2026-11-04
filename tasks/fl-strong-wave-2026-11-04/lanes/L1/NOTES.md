# Lane L1 notes (FL STRONG wave, 2026-11-04)

Status: PARTIAL write, made before a laptop hibernate. 21 of 25 clusters have a row in verdicts.csv.

## UNFINISHED (no row in verdicts.csv)
- LF-FL-00433 American Vinyl Company, 6715 N 53rd St, Tampa. Directories say it is a PVC profile/hose extruder (Vartek plant bought; 80,000 sq ft). Next: read avcplastics.com (or the site that resolves) for a page naming Tampa and the extrusion work. Atlas dedupe by name: no hit. Aurora Material Solutions is only an ITA alias; Aurora's own plant list has no Florida site, so do not use Aurora pages as the witness.
- LF-FL-00096 Sun Coatings, LLC, 4701 E 7th Ave, Tampa. Lead: suncoatings.com (company page) reportedly says "all our products are manufactured locally in Tampa, Florida" (from a search summary, NOT yet verified verbatim) and lists latex and solvent paints, wallpaper adhesives and caulks; contact page prints the 7th Avenue address. Owned by ICP Group since Jan 2021 (ICP legal entities list includes Sun Coatings, LLC). Atlas dedupe by name: no hit. Likely VERIFIED_NEW_ORG tier C (coatings, Ring 2).
- LF-FL-00089 Speedling, Incorporated, 4447 Old US Hwy 41 S, Ruskin. Lead: speedling.com text "Speedling's EPS manufacturing facility offers expanded polystyrene boxes, lids and trays." and footer address "4447 Old Hwy 41 S Ruskin, FL 33570". Need to confirm exact characters (apostrophe) with a raw fetch. Atlas dedupe by name: no hit. Likely VERIFIED_NEW_ORG tier C; materials polystyrene_ps_hips / foams_polymeric; note the company is mainly a plant-plug grower, with an EPS side line.
- LF-FL-00062 Sentry Industries, Inc., 5687 NW 36th Ave, Miami. Nothing found beyond a Fastdol profile (NAICS 325998, OSHA fatality investigation). Next: find the company site or a product description; default is STILL_UNCERTAIN.

## Low-confidence calls to re-check
- REJECTs resting on directories or one page: LF-FL-00253 (Premier Water), LF-FL-00099 (Nova Pressroom), LF-FL-00025 (Chemical Systems of Orlando), LF-FL-00004 (Sunbelt), LF-FL-00011 (Symrise). Each row says what would reopen it.
- LF-FL-00346 TSE tier: the witness is city-level, so B is by the brief's wording; C is defensible.
- LF-FL-00342 Mannington: own page says Eustis, not Umatilla (assumed same plant, tier C).
- LF-FL-00069 Dart and LF-FL-00376 WinCup: the input's current_atlas_hits missed held orgs ORG-002441 and ORG-000984 (name differs from the federal legal name). I used VERIFIED_NEW_SITE under those orgs. Worth checking the dedupe step that built the input.

## Counts so far (21 rows)
VERIFIED_NEW_SITE 7 (TSE, ADS x2, Dart, Mannington, WinCup, Altium), VERIFIED_NEW_ORG 6 (Maclan, Richard's, King Plastic, Atkore, Lidworks, Spartan Composites), REJECT 6 (Premier, Nova, Chemical Systems, SynQuest, Sunbelt, Symrise), STILL_UNCERTAIN 2 (EAM, Imperial Foam). Tiers (checked by parsing the CSV): B 4 (TSE, ADS x2, Dart), C 9 (6 new orgs plus Mannington, WinCup, Altium), blank 8 (6 rejects, 2 uncertain).

## Method
Own-site text read with a read-only GET and tag strip (python -I), plus WebFetch/WebSearch. No data/ edits, no git. Atlas lookups: `atlas.py show` for held orgs, `atlas.py dedupe-check --name ... --state FL` for new-org names. No closure notice found for any verified row.
