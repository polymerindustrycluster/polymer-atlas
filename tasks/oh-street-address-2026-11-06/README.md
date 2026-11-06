# Ohio street addresses — L2, 2026-11-06

Claim: atlas-L2-oh-address / IDEAS B-04; controller thr_9i2c6byhcz delegates application to this lane (2026-11-06 message). This explicit delegation authorizes data integration under AGENTS §2.7. Only street_address and supporting sources change; county, county_source, tiers and status do not.

Acceptance: fill blank streets of active Ohio site rows only from site-keyed primary/federal evidence; exact normalized city, ZIP5 and county agreement; physical street only; conflicting sources held. Evidence append-only in EVD-150000–159999. Idempotent builder, validate.py zero errors, independent seeded 30-fill fresh-source audit, Codex and Grok deep refutes before PR.

First user: Atlas integrator/controller, on PR review 2026-11-06. Non-use finding date: 2026-11-13 (controller checks adoption).

Baseline bd57a08: 1,883 active Ohio site rows, 143 streets (7.59%), 1,740 blanks. Brief's 1,955/146/1,809 differs from current main; do not combine denominators. Six existing address evidence rows cover blanks, but none quotes a street, so none qualifies for reuse. Registry input is a verbatim site-keyed FRS subset of registry_links.csv from restore branch commit 08b60bab86a959180e9810d479d7b45d55f313ca; 301 FRS links cover 283 blank active Ohio sites. No registry links are changed.

§4.5 county_source describes the county's actual adjudication, not street presence. It stays unchanged. FRS address evidence is registry/supports_C (§4.13); A/B rows without stronger address evidence are held, never demoted to make validation pass.

Controller rulings (2026-11-06): inherited bulk federal extracts explicitly supersede brief §4's fresh-fetch requirement for these extracts only; website quotes still require raw re-fetch. CY2025 ITA rows cite https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv, observed 2026-11-01, with establishment_ID, date_submitted and supplied-extract SHA-256 in notes. The controller initially named the prior CY2024 ZIP, then confirmed the CY2025 correction after this lane identified the vintage mismatch. A/B rows still require an own-site witness or HOLD. Direct OSHA bulk download returned 403; Jina returned 401 (anonymous network reputation); neither is evidence against any establishment.

FRS transport: per-ID concurrency hit the service's six-request/minute limit; 429s are availability only. Resumable fetches use the documented county selector at 12-second spacing. County queries retain only registry IDs in the frozen site-keyed input, with total response count, retained count and whole-response SHA-256 in county_fetch_log.csv. Each retained JSON is an unaltered facility object, wrapped in the same Results/FRSFacility schema; no discovery is performed on unrelated records. State-only queries require another selector. API: https://www.epa.gov/frs/frs-api.

Allocation clarification, controller 2026-11-06: Ohio retains EVD-150000–154999; Pennsylvania continuation separately reserves EVD-155000–159999. Sparse Ohio evidence IDs use each site's position in the frozen blank cohort, so later holds never recycle an ID.

Input minimization: registry_links_input.csv retains only the 301 verbatim FRS link rows for the 283 blank active Ohio sites. Full restore-branch source-file SHA-256: b830d047d4bedc576b7628cf0bbdebf685a6288cb2ed4d2ddbf1700d9e741953. No unrelated registry rows are copied into the lane.

Final bounded pass: 143 street fills, with one address evidence row each; active Ohio site rows filled **143/1,883 (7.59%) → 286/1,883 (15.19%)**. No new site or organization records, no dedupe/merge, no inclusion-log calls. Record tiers unchanged: C 102, U 34, A 6, B 1. Address evidence classes: inherited ITA government_filing 124 (supports_A), fresh FRS registry 12 (supports_C), raw operator own_site 7 (supports_A). Evidence IDs are sparse within 150000–151739. Sources are added to each changed row; street_address is the only other changed column.

The initial 301-ID FRS fetch encountered 298 request-limit failures; conservative retries retained 22 fresh facility JSONs. County-wide queries also exceeded the API process limit and were abandoned. Failed requests never supplied a value or a negative verdict. Source access limits are a major coverage limit of this pass; holds are unresolved work, not rejected establishments. Own-site checks covered 112 packet rows (some duplicate site IDs) across operator pages; 28 matched address blocks, then conflict/tier adjudication admitted only seven of these as the fill's witness.

| Holds filter (overlapping counts; unit: blank active Ohio site rows) | Count | Settling fact / recommended reading |
|---|---:|---|
| All STILL_UNCERTAIN | 1,597 | Per-site reasons in holds.csv; no street filled |
| No admissible site-keyed witness available | 1,480 | Physical street from an own page or exact/strong government record with agreeing city/ZIP |
| A/B site lacks raw own-site address witness | 759 | Operator location/contact address, under controller's tier restriction |
| ITA city/ZIP missing or conflicting | 82 | Confirm physical locality and ZIP; no city/ZIP correction in this pass |
| Existing notes street conflicts with candidate | 82 | Dated location/address adjudication; suite differences held (§2.8 conflicts instruction) |
| Two admitted sources disagree on street | 2 | Source reconciliation; never choose whichever is convenient |
| Fresh FRS locality/ZIP conflict | 3 | Confirm site-specific registry linkage and physical address |

Named checks:

- `python3 tasks/oh-street-address-2026-11-06/build.py --known`: three held known street/city/ZIP answers, **3/3 passed**. Injected wrong city, ZIP, county and PO-box cases rejected.
- `python3 tasks/oh-street-address-2026-11-06/check.py`: **PASS, 143 fills**, only street/sources change, repeat build byte-identical, injected new street conflict refused. This check uses a temporary data tree.
- `python3 scripts/validate.py`: **OK — validation passed, 0 errors**. Existing warnings unchanged.
- `python3 -m unittest discover -s scripts -p 'test_*.py'`: **221 tests, OK, one existing skip** (93.015 s). No scripts/ files changed.
- `python3 tasks/oh-street-address-2026-11-06/audit.py`: **30 sampled fill rows**, Random(20261106), sorted site IDs; **0/30 detected address errors**. **ITA transcription errors 0/22 sampled ITA fills**; all other eight sampled fills had their cited witness freshly checked. **Fresh independent corroboration 14/30 (46.67%); not independently checkable 16/30 (53.33%)**. The latter had no exact/strong site-keyed FRS alternative in held packets; this is missing corroboration, never called a fresh-source pass. No fresh ITA CSV download is claimed. The controller explicitly approved these separate rates on 2026-11-06. `audit_discovery.csv` preserves the earlier, interrupted discovery sample: SITE-000809's Hwy/Road discrepancy triggered HOLD and the expanded notes conflict gate before the final sample was selected.

Rebuild on fresh main: restore main's two Ohio data files, then run `build.py --apply`, `check.py`, `validate.py`. The builder refuses changed locality, county provenance, operator, tier or already populated conflicting street instead of overwriting. Pre-pass data backups are local under backups/ and excluded from the PR. No automatic acceptance of a changed snapshot.

Review route: controller 05:55 clerk ruling supersedes the brief council-only route and order; this branch is pushed as a draft for the designated Codex/Grok reviewer threads. Council attempts were refused before provider launch by the shared hard40/600s guard (no verdict). Both required families have now approved the substantive output; verdicts below supersede the pending status.

    
Final independent completion refutes (substantive head50ac7a22afff4be038d6bc8a88316b1b6ec6a0c5):

- Codex/OpenAI, R-codex-2 thr_mdr3gn2xmm: **APPROVE,0blocking findings**. Traced all143 fills to exact/strong ITA/operator links, fresh FRS/locality and own pages; independent fresh own7/7, three live calibration answers and injected locality/PO-box cases pass. Validator/check/row-loss guard/fresh-main replay pass; seven protected-field/status drifts reject before writes. Reproduced final audit exactly:ITA0/22transcription,14/30freshcorroboration,16/30uncheckable,0addresserrors. Counts,tiers,sourceceilings,all301inputlinks and frozenbaseline reconcile. Receipt:controller reviews/134-clerk-codex-2.md.
- Grok/xAI, R-grok-2 thr_f2fcbx6tq8: **APPROVE,0findings**. Recomputed143street edits,143append-only evidence,143→286/1883coverage,C102U34A6B1; all124ITA matches and12FRS JSONs agree. Live own7/7quotes and four FRS responses match. Validator/check/row-loss pass,globalIDs unique/in-block and absent from main; audit rates reconcile. All target143rows unchanged on fresh main9d69978; replay-on-main is the integration recipe, not a defect. Receipt:controller reviews/134-clerk-grok-2.md.

Fresh-main integration: controller06:12 LF exception applied, then main9d69978 merged (includes restored registry links). Took main's two Ohio data files and re-ran the unchanged builder, preserving fresh-main pre-pass backups locally. Named check and validator0errors re-pass. Separate keyed comparison proves every main site/evidence key retained, all legacy evidence unchanged, exactly143 street/source-only site edits and143 evidence appends. Net federal-frame/registry_links diff vs main is zero. Reviewed data/logic unchanged; only main integration and this verdict record added. No issue closure or merge performed by L2.
