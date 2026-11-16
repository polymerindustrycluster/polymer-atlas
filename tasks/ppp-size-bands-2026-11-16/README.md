# Historical SBA PPP employee bands — B-PPP application, 2026-11-16

Owner: **John Swanson**, ruling in session **2026-11-16**, relayed by controller thr_9i2c6byhcz: **“Strict matches”.** PPP job counts may fill **blank employee bands only**, each labelled with its **2020 or 2021 loan date**, never overwriting an existing band, only for single-site Ohio-only organizations where borrower **name, street and city** match. Name-and-city-only matches and every other use stay leads. No NAICS restriction was adopted. The controller designated atlas-w16-ppp-scout/Codex as integrator for this bounded pass.

Acceptance: re-derive strict rule-b on pinned current main, populate only empty `organizations_OH.employee_band_ohio` and `sites_OH.employee_band_site`, add one dated size_band evidence row per fill inside EVD-376000–376999, preserve every other canonical field and existing evidence, reproduce 104/106 known-answer within-one agreement, and reject three injected defects. Packet PR #345 is unchanged. No SCHEMA or owner-rulings file is edited; this README records the supplied ruling.

## Applied pass

Base: `ef32b5ba73a2fe7924a67ce3d53e9bc1758e72de` (origin/main at pass start). On this base, PR #341 is open/unmerged; its pending 12 site fills are not part of this base. They must win over PPP if they land before integration: merge current main and re-derive before merging this PR; never resolve an overlap by overwriting the other source. `check.py` pins pre-pass snapshots and checks complete row/field diffs, so a changed band cannot silently enter this pass.

| Change | Applied | Held / excluded |
|---|---:|---|
| Organization Ohio band, previously empty | 117 organization records | All nonempty bands untouched |
| Site band, previously empty | 137 active PIC-18 site records | All nonempty bands untouched |
| `size_band` evidence | 254 appended rows | No tier/status/scope/address change |

174 organizations meet the strict rule. Proposals are one per record, not summed loan rows; an organization and its site are separate records. The 254 fills comprise **145 observations dated 2020 and 109 dated 2021**. Evidence IDs **EVD-376000–EVD-376253**, checked for tree-wide collision before application. `fills.csv` records exact field deltas and source loan IDs; `evidence_rows.csv` is the append payload. All other borrower/organization cases remain leads. `holds.csv` records 273 named-loan/organization pairs meeting the name/locality/single-site screen but failing active-site street equality or lacking a held street; these are loan/org pairs, not distinct rejected companies and never closure verdicts.

## Rule adjudication (deterministic, no new hand checks)

1. Read all organization/site shards; single-site means exactly **one active site**, and **every held site**, active or inactive, is in Ohio/US. The active site must be in PIC-18 (`scripts/regions.py`). This is the owner-adopted operational grain; unknown/unrecorded sites are not inferred away.
2. Normalize borrower name using the existing `atlas.name_key`; require equality to an organization legal name, recorded trade name or recorded former/parenthetical alias exposed by `atlas.org_name_fields`. A site-name-only match is **not** sufficient. No new registrant aliases are invented. The 117/137 results require no site-name-only fallback.
3. Borrower city equals that active site's city (case-insensitive), and both street strings are nonempty with identical `atlas.street_key` values. The matched street must be the **active** site's street, not an unrelated/inactive establishment. No postal-address or parent inference.
4. Preserve the scout privacy whitelist: named corporations, S corporations, LLCs, partnerships and LLPs only. Sole proprietors, self-employed individuals, independent contractors, unknown types and blank/redacted names are excluded. Addresses are used from the privacy-filtered cache for matching and are not copied into this task or changed in canonical data.
5. Use positive integral JobsReported only. Map with the existing Form 5500 `band_of` helper to the eight schema bands (`1-9` through `5000+`). Choose the **latest qualifying loan date per organization**, tie-break by loan number, never add loans/draws. Fill only an exactly empty target band. The organization must be in the authorized Ohio shard.

This is a dated borrower statement, not a current employment assertion, an audited employment observation, proof of jobs saved, or a new scope/liveness determination. The schema's existing `size_band` class/effect rules are followed: **government_filing**, ceiling **supports_B** (supports_U would apply on a tier-U record). No record verification tier is modified. Filled records by held tier: organizations A 65 / B 47 / C 5; sites A 54 / B 30 / C 31 / U 22. Evidence effects: 232 supports_B / 22 supports_U.

## Evidence and vintage

Official [SBA PPP FOIA release](https://data.sba.gov/dataset/ppp-foia), release 2024-09-30, license U.S. Government Works; previously fetched 2026-11-16 in the packet scout. `source_manifest.json` carries exact filenames, original full-stream hashes, filtered cache hashes and row counts. No fresh downloads or raw borrower files were needed. 1,953 privacy-filtered Ohio loan rows are the cached input, checksum-verified before each build. Source refs cite the official CSV plus its LoanNumber, not this task's output.

Each evidence claim quotes the **exact field values** BorrowerName, BorrowerAddress, BorrowerCity (all as filed), JobsReported and DateApproved from that SBA row. It labels the historical **2020/2021** figure and resulting band; the strict-matched business street and city are included to make identity auditable in each evidence row. No personal contact data is transcribed. The CSV supplies field values rather than a narrative sentence, so the evidence explicitly names the quoted source fields. `observed_date` is the source's loan date (ISO representation of DateApproved); the release's dictionary calls this column “Loan Funded Date”, while the owner brief calls it loan approval date. The underlying employment reference period is unspecified. Retrieval date **2026-11-16**, release date **2024-09-30** and full-stream source hash are in evidence notes. Neither release nor retrieval is used as the employment date. This follows §4.13's dated-filing convention and the government-filing/size_band pattern in `tasks/size-band-evidence-2026-11-03`.

Only the two band fields are authorized record edits, so no organization/site notes or added source-date columns are written. The dated evidence rows are the labels for these band values. Readers must use the attached evidence's historical loan date, not interpret the undated band column as a 2026 statement.

## Journal, rebuild and named checks

Pre-pass backups of organization/site shards and both edited evidence shards are under controller storage `persist/ppp-size-bands/pre-pass/`. They are checked byte-for-byte against the pinned base commit before validating. `base.json` identifies that base and the older scout baseline. Backups and privacy-filtered loan cache stay outside Git. `build.py` writes deterministic fills/evidence/holds/counts; `--apply` changes only the four authorized data files and uses `scripts/shard_io.append_sorted` for evidence. Reapplying is byte-idempotent; any conflicting nonblank band refuses application.

```
python3 tasks/ppp-size-bands-2026-11-16/build.py
python3 tasks/ppp-size-bands-2026-11-16/build.py --apply
python3 tasks/ppp-size-bands-2026-11-16/check.py
python3 scripts/validate.py
python3 scripts/check_row_loss.py --base origin/main
python3 scripts/export_vocab.py --check
```

`check.py` verifies every fill was blank, passes strict identity/street/city/single-site/privacy rules, equals the JobsReported band and has its exact dated evidence. It recomputes the complete proposal set, inspects whole output rows against pre-pass data, checks evidence append parity and global ID uniqueness, and proves idempotence. It rejects injected **nonblank overwrite**, **wrong band** and **wrong borrower organization** defects, plus missing **BorrowerAddress** and **BorrowerCity** evidence defects. The frozen known-answer table is independently joined back to the SBA loan figure and the original scout's Atlas bands at `be2e6084d430f1e6f9de0f66289b1d3c2570e255`: **104/106** comparable single-site Ohio organization bands remain within one band. This calibration is pinned to the original baseline, not recomputed against the newly filled bands, which would flatter agreement.

Review/validation results are recorded with the PR. The controller supplies independent two-family completion review; no issue is closed here. No new tracked commitments created. Proposed follow-up: if main changes before merging, preserve its nonempty bands and regenerate the blank-only payload before review/merge. No other PPP use is integrated.

Local verification on the applied tree: `check.py` **PASS** (104/106 known answers; all three defects rejected; byte-idempotent); `python3 scripts/validate.py` **OK — validation passed (0 errors)**; `python3 scripts/check_row_loss.py --base origin/main` **OK, no keyed row removed**; `python3 scripts/export_vocab.py --check` **current**. No `scripts/` changes, so the scripts unit suite is not required for this task. Independent completion review and GitHub validate remain controller/PR gates, not claimed here.

Codex clerk correction (PR #348, 2026-11-16): regenerated all 254 new evidence claim texts through `build.py` to quote borrower street and city exactly as filed, alongside name, jobs and loan date. The checker explicitly requires all five fields and rejects either missing location field. No fill, source, ID, date, effect or existing main evidence changed.
