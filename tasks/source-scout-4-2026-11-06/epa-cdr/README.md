# EPA2024 Chemical Data Reporting — CORROBORATION_ONLY

[Official access page](https://www.epa.gov/chemical-data-reporting/access-chemical-data-reporting-data) links the public2024 CSV ZIP; HTTP200, keyless bulk download works. [2024 public CSV ZIP](https://www.epa.gov/system/files/other-files/2026-04/2024-cdr-public-csv-data.zip), SHA256 `6a7479102ef22ea2a8f082baf51c03614077fd31a2ecdb00336c084490b084ab`. No ChemView UI scraping needed. Data are reports for2020–2023, not2024–2026 operating observations. The ZIP includes manufacture/import, industrial processing/use, consumer/commercial use, national aggregates and dictionary PDF.

[EPA standard data license](https://edg.epa.gov/data/EPA_Data_License.html), raw-checked:
> all data produced by the U.S EPA is by default in the public domain

The qualifier is “Unless otherwise specified”; source metadata and publication limitations still govern. Only the published nonconfidential CDR extract is used; no CBI/suppressed value is inferred or decoded. No individual contacts or coordinates exported.

Count/filter: Manufacture-Import file **50,433 chemical-report rows**, **4,528 nonempty EPA-TSCA site IDs**. Exact leading six-digit site NAICS in any of three reported code fields, prefix3252 or326: **2,924 chemical-report rows / 290 distinct TSCA site IDs**. That is a core-NAICS discovery slice, not a new scope/ring rule, not all polymer entities and not290 manufacturing plants. Sites may be importers or reporting offices; CBI/NKRA/blank values stay categorical unknowns. Industrial-use NAICS downstream categories are not used as reporter facts.

Independent DuckDB SQL over a strict cp1252→UTF8 conversion and Python's CSV parser agree on all four counts. The earlier loose substring filter returned291 because it admitted wire-products code332618; it was rejected. Known-answer tests include325211,326299,326199 positives and332618/325199/CBI/NKRA/incidental-digits negatives. Source file SHA256 `fcbce4fb8ec8c84d704ec2075cd14d87f919e3fc257e7b524f3ad56a1e29471e`. No guessed totals or silently skipped parser rows.

`frame.csv` holds the290 reporter-site IDs and minimal public business fields. Rows are grouped by the source TSCA ID; variants are preserved as semicolon-separated values, and address_variants exposes conflicts rather than choosing one. IDs verified in the source extract, **no registry link applied**. `chemical_reporting_rows` sum2924. Never sum nested NAICS groups or treat chemical rows as sites.

20-site sample: seed20261106, sorted TSCA IDs, uniform without replacement. **5 DUPLICATE_OF held sites, 15 STILL_UNCERTAIN, 0 VERIFIED new sites**; **0/20=0%, Wilson95%CI 0–16.11%**. This is a **dated bulk-evidence/current-sufficiency** scout, not a six-fetch own-site campaign or evidence that these15 sites do not exist. No current operating-status inference; zero verified-new here does not measure the maximum discovery potential. Source vintage and settling fact are in each row.

Dedupe: shared all-shard atlas.dedupe by reporter name, street plus locality, aliases/notes; domain unavailable. At site grain, a held parent alone never makes the sampled site a duplicate. Only singleton exact street/locality hits are DUPLICATE_OF; explicit duplicate_of terminates at held SITE IDs. Operator matching/current names remain for integration; no operator reassignment or merge performed. No closure REJECTs.

Re-run:
```
curl -L --fail 'https://www.epa.gov/system/files/other-files/2026-04/2024-cdr-public-csv-data.zip' -o /tmp/l5b-cdr.zip
python3 -m zipfile -e /tmp/l5b-cdr.zip /tmp/l5b-cdr
python3 tasks/source-scout-4-2026-11-06/epa-cdr/build.py '/tmp/l5b-cdr/2024 CDR Manufacture-Import Information.csv'
python3 tasks/source-scout-4-2026-11-06/check.py
```

| Hold | Settling fact | Recommendation |
|---|---|---|
|15 uncertain sampled reporter sites | Current own-site operator/process/address evidence, distinguishing reporting/import office | CORROBORATION_ONLY; use dated CDR to corroborate known sites, not current-status automation |
