# CBP PIC-18 reconciliation, 2026-11-06

The requested six counties were **already present** in the existing CSV. A fresh four-file bulk rebuild produced **5,190 rows byte-identical to HEAD**, so adding rows would duplicate data. What was stale was the builder/report's PIC-12 county selection. It now imports regions.PIC18, covers 18 counties and refreshes docs/denominators/CBP_SIZE_CLASSES.md.

Six added Ohio counties: Ashland 39005, Columbiana 39029, Erie 39043, Huron 39077, Richland 39139, Tuscarawas 39157. Together: **160 rows** (16 published county×NAICS groups × all plus nine size classes); NAICS filters 326/3261/3262/3252/3259, CBP 2023 employer establishments, all legal forms. Some county×NAICS combinations have no published row: not synthesized as zero. The six NAICS 326 total rows sum to **50 establishments**; the PIC-18 NAICS 326 total is **401 establishments**. Nested NAICS are never summed together.

`api_totals.json`: fresh Census API output for all Ohio counties, same vintage/NAICS and EMPSZES=001; fetched using environment CENSUS_API_KEY. URLs are constructed in fetch_totals.py without recording the key. All **16 published county/NAICS totals match ESTAB**. `../build.py` asserts exact key-set and value equality, so a missing or extra published combination fails. Size-class suppressed N values stay N/empty; they are not API establishment totals and are never filled with zero.

Reproduce from repo root:

```
python3 scripts/build_cbp_size_classes.py --raw-dir /tmp/l5-cbp
python3 scripts/build_cbp_size_classes.py --raw-dir /tmp/l5-cbp --tables-md
python3 tasks/source-scout-3-2026-11-06/cbp/fetch_totals.py
python3 tasks/source-scout-3-2026-11-06/build.py
```

Bulk hashes (SHA256):

- cbp23us.zip: 3f9018f807f1ffd7bcbb00690f9792573bc2bc6bb4cfab9df14ca7ab3eac0862
- cbp23st.zip: 9fc306ecc4f9633092e2432c2db2acdf53798da0480e6f6beeb953d583b41ede
- cbp23co.zip: e9539e96ceb91608ad44ab1cfc651d7c1ff9b88bddfe7a8ff64134ccde6e9603
- national_county2020.txt: 9f6e5f6eb6ac2f5e9a36d5fd01dec77991bddc75118f748a069441a4782970d6

Census public official reference data; no organization fact or evidence row added. Source record layouts and methodological constraints remain in the denominator report.
