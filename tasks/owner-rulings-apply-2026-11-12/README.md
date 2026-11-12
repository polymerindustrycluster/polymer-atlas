# Apply owner rulings — 2026-11-12

Applies the nine **OWNER-ACCEPTED (a)** rulings from the packet in PR #313 (`tasks/owner-rulings-2026-11-12/README.md`).

Owner quote, 12:51pm America/New_York on 2026-11-12: "Yes, go with your recommendation on all 9 rulings."

This PR is branch-and-PR only. It does not merge, does not push to `main`, does not touch CI `vocab.json` / EVD-333167, and does not fill Ohio streets. New evidence IDs are from the reserved range EVD-350000–EVD-359999 (this pass: EVD-350230–EVD-350237) after re-checking main and open PRs. No new org or site IDs were minted. Public professional facts only; no contact data from fetched pages was copied into the repo. No banned sources.

Sanitized own-site extracts (phones and a media-contact email omitted) are in `raw/`.

## Per-ruling application

1. **H-CHROMAFLO.** QUEUE item marked `done 2026-11-12`. `ORG-013200` already tombstones Chromaflo → Vibrantz `ORG-000007` on main (`status=acquired`, `status_date=2022-04-21`). No second tombstone. Ohio shard not edited.

2. **H-HANKOOK.** Confirmed: `ORG-000167` already stands on main as `status=merged`, `status_date=2026-10-29`, `successor_org_id=ORG-000204`. Applied: `SITE-000174` in `data/sites_OH.csv` has `org_id` repointed from `ORG-000167` to `ORG-000204`; `operating_status` stays `closed` as a record-level fold, not a plant-closure finding; `street_address` left blank; notes updated; `last_verified=2026-11-12`. `SITE-000215` was not edited. Conflict note: this is a one-line edit in `sites_OH.csv`, which is also touched by Ohio street-fill / capabilities PRs #307, #314, #315, #317–#321. Those PRs did not change the `SITE-000174` row at the time of this pass, but later rebases may conflict on that line.

3. **H-ROECHLING.** QUEUE item marked `done 2026-11-12`. `SITE-000589` already under `ORG-000551` after the 2026-10-29 A2 unwind. No further data change.

4. **H-PA-STREET** (`SITE-002364` ↔ `SITE-002304`). Owner-confirmed hold. No merge (address-first flag). Recorded in `data/inclusion_log.csv`.

5. **H-TARKETT** (`SITE-003477` / `SITE-003478`). Owner-confirmed hold. Sites not repointed. Recorded in `inclusion_log.csv`.

6. **H-DANIMER** (`SITE-003134`). Owner-confirmed hold. No repoint. Recorded in `inclusion_log.csv`.

7. **S-CRM-AZ** (QMS-AZ-23). Owner-confirmed hold in this pass. Recommendation (a) accepted the approach of recording a legal name that does not trip V-50 and then creating from ITA/OSHA witnesses, but (a) itself says not to self-rule the string. The owner did not pick the exact recorded legal-name form or grant a V-50 allow-list change. CI `vocab.json` / EVD-333167 not touched. No org/site created. Recorded in `inclusion_log.csv`.

8. **S-SCOPE.**
   - QMS-AL-09 Lenzing Axis lyocell: **REJECT** (inclusion_log only). Out of Rings 1–2; owner did not extend scope to regenerated cellulosic fiber. No record created.
   - QMS-AZ-01 / LF-RI-00043 Fujifilm Electronic Materials (Mesa and North Kingstown) and QMS-AZ-11 Shin-Etsu MicroSi Phoenix: **owner-confirmed HOLD** for a site-level own-page or manufacturing witness. No create.
   - QMS-CO-04 / QMS-CO-11 Boulder Scientific Mead and Longmont: **REJECT** (inclusion_log only). Catalysts remain out of Rings 1–2 under the precursor-only doctrine. No record created.
   - QMS-WV-09 ICL-IP Gallipolis Ferry: **owner-confirmed HOLD** for an own-page product identity. This candidate is in West Virginia, not Ohio; no Ohio file was edited.

9. **S-PPC-PAYSON.** Applied the (a) fold of plant-as-org `ORG-006226` into `ORG-004209` and repointed `SITE-008292`, on 2026-11-12 own-site witnesses:
   - `https://ppcflex.com/locations/payson-ut/` names 213 Temkin Way, Payson, UT 84651 (same street as `SITE-008292`).
   - `https://ppcflex.com/locations/` lists Payson, UT; North Salt Lake, UT; and Columbus, OH.
   - `https://ppcflex.com/blog/ppc-flex-announces-strategic-acquisition-of-sudpacks-us-operations/` (dateline January 12, 2026) states that PPC Flex, headquartered in Buffalo Grove, IL, operates twelve manufacturing facilities including Payson, UT, North Salt Lake, UT, and Columbus, OH.
   - `https://ppcflex.com/blog/fisher-container-overview/` (May 16, 2019) publishes the Fisher Container legacy on the same domain; `ORG-004209` already lists Fisher Container Holdings LLC as `ultimate_parent_name`. The North Salt Lake location page is city-level only and does not name 95 South Riverbend Way.

   `ORG-006226`: `status=merged`, `status_date=2026-11-12`, `successor_org_id=ORG-004209`. `SITE-008292` remains `active` (the plant is operating; the fold is of the plant-as-org record). `ORG-004209` gained trade name `PPC Flex` and website `https://ppcflex.com/`. Evidence EVD-350230–EVD-350237. Generated `merged_into` edge REL-000472 (`ORG-006226` → `ORG-004209`) from the successor column (effective_from empty: tombstone-pass date is not restated as a corporate date). The fold is not address-first (Payson and North Salt Lake are different streets and cities).

   **Held (could not fully apply the identity-bridge half of (a) in this PR):** the same own-site pages are a dated legal identity bridge among `ORG-001029` (ppcflex.com; Columbus plant `SITE-001111`), `ORG-004209`, and the Payson plant. Folding `ORG-001029` / `SITE-001111` would require editing `organizations_OH.csv` and `sites_OH.csv` beyond the authorized one-line Hankook edit. That Ohio half is held to avoid colliding with open Ohio street-fill and capabilities PRs (#307, #314, #315, #317–#321). The bridge is recorded in notes and evidence on the Utah records for a later Ohio-safe fold.

## QUEUE.md

Three surgical status-line edits (Chromaflo, Hankook, Röchling). PR #307 also appends one claimed Ohio-streets line at the end of this file; the edits here are on earlier Phase 1 lines and should merge cleanly with that append.

## IDs

- No new `ORG-` or `SITE-` IDs. Next-free relationship id on main was REL-000471; this pass adds generated edge REL-000472.
- Evidence: EVD-350230, EVD-350231, EVD-350232, EVD-350233, EVD-350234, EVD-350237 on `evidence_organizations_UT.csv`; EVD-350235, EVD-350236 on `evidence_sites_UT.csv`.
- Open-PR check at write time: #308 used EVD-350000–350016; #309 used EVD-350100–350116; #311 used EVD-350200–350229. Main reserved-range occupancy was empty.

## Validator

`python3 scripts/validate.py` was run locally before opening the PR.
