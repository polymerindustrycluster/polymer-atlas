# Residual HQ2 — lane B packet

Researcher: residual-hq2-b. Observed 2026-11-06. Frozen input: 30 allocated organization records, SHA-256 `0d6f9fd6fd533a3c580b8d8a10a0947de088d7c97925b1b304c4fc0d58bb159b`.

`verdicts.csv` contains exactly one verdict/outcome per allocated ID: **7 HQ_FOUND proposals and 23 STILL_UNKNOWN holds**. Positives: DiversiTech, IDEX Health & Science LLC, HB&G Building Products, Wabash National Corporation, APG Polytech LLC, Chemline Inc, Bomar Specialties LLC. APG uses the exact entity's state-registry **Principal Office Address**; no plant-only or mailing-only inference. Counties are empty because this lane did not obtain county evidence. The integrator must independently refetch positives and decide application; this packet changes no canonical data or IDs.

Every hold names the settling fact. In particular, Hyundai Transys entity grain remains unresolved; GEZOLAN, JLOK and Lewcott do not inherit their groups' HQ; Wm. T. Burnett & Co does not inherit the holding LLC corporate office without exact-entity linkage. Zanini's lapsed entity-supplied LEI points to the Spanish parent address and is held for independent subsidiary confirmation. ELANTAS PDG and Chemtrusion have useful indexed HQ leads but failed raw retrieval, so they remain holds.

`receipts.csv` records all **87 raw-fetch attempts**, URL, HTTP result, raw SHA-256 and temporary cache path. Maximum is six attempts per organization. HTTP outcomes: 68×200, 6×404, 4×403, 3×000, 3×401, 3×406. The three HTTP 000 attempts have explicitly saved zero-byte response bodies. Fetches used browser-UA curl; failed Jina anonymous retries count against the same cap. Search-result leads were never admitted without raw retrieval. Raw HTML/PDF and temporary research code remain only under `/tmp/residual-hq2-b/`; do not commit that cache. PDF text used `pdftotext -layout`. ` || ` separates two excerpts from one page, totaling at most 25 whitespace-delimited words per positive source.

Check, from repository root:

```sh
python3 tasks/residual-hq-2-2026-11-06/lanes/b/check_packet.py
```

Passed: 30/30 unique allocated IDs, names unchanged, exact coverage, bounded fetch counts reconciled to receipts, all 87 raw hashes, every positive quote matched as contiguous normalized words in source order within each excerpt. Three real source/parser cases: Wabash HTML HQ sentence; IDEX split HQ label/address; Bomar PDF HQ footer. Missing-row, duplicate-ID and invented-quote mutations all failed as intended. The check fails if any raw cache file cannot be inspected; rerunning requires the temporary cache and pdftotext.

Only this lane's output files were written; input.csv is unchanged. No data, queue, tracker, settings, branch or commit edits. Repository-wide validation and integration approval belong to the parent; no integration or independent second-family review is claimed here. The Mac data-estate search reported missing Windows-only inventories, so it is not evidence that those sources are absent.
