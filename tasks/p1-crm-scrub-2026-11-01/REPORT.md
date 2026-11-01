# P1 scrub packet - REPORT (2026-11-01)

Packet-lane output for the integrator of record. **No file under `data/` was edited, no ID was allocated, no status or ring changed.** Basis: AGENTS.md section 5.1 as amended 2026-11-01 (the private PIC CRM is never a cited source for any fact in any public row, and no public row names CRM content), section 2 rules 7-9, SCHEMA v1.7.6 owner ruling P1 (and P3 for the workshop paths still in `sources`), R7f and R13 (employee-band inputs), `tasks/OWNER_BATTERY_2026-11-01.md` P1. Derived fields are untouched.

**Publishability.** This packet is committed to the public repo, so it republishes none of the removed text: `edits.csv` carries the `new_value` in clear (already scrubbed) and only a `sha256` of each old cell value; `occurrences.csv` carries neutral descriptors, not excerpts; this report names classes and counts only.

Files in this directory: `occurrences.csv` (one row per clause), `edits.csv` (603 field edits, the machine-readable packet), `band_actions.csv` (242 organizations), `holds.csv`; plus `scripts/apply_p1_crm_scrub.py`.

## 1. Counts (units named)

Census basis: case-insensitive whole-word token in every column of every `data/*.csv`: **399 occurrences in 346 fields in 305 rows** (organizations: 299 notes, 31 sources, 9 descriptions; sites: 3 notes; ecosystem: 2 notes, 1 sources; event_participation: 1 note). A further 13 cells contain the same three letters only inside registry identifiers (TRIFID values and the evidence rows that quote them); those are verified identifiers (AGENTS.md section 4), not occurrences, and are left untouched.

Classification unit = one clause (a field can hold several): **364 clauses**.

| class | clauses | meaning |
|---|---|---|
| SRC_ENTRY | 32 | a sources entry citing a non-public adjudication record (31 organizations, 1 ecosystem record) |
| BAND_FROM_CRM | 242 | a CRM-derived `employee_band_ohio` (one provenance clause per organization; 242 organizations) |
| FACT_PER_CRM | 68 | another field value with a CRM basis: 58 hq_city/establishment clauses (3 also touch process/capability/scope, 2 leave the county blank), 6 descriptions, 1 website (ecosystem), 1 ultimate parent, 2 relationship/date clauses |
| NARRATIVE | 21 | mention only; the fact rests on public evidence (own site, company announcement, filing) |
| OTHER | 1 | one third-party system label in an event-participation note, unrelated to the ruling subject; reworded so the census is zero |

Dispositions: BAND_FROM_CRM/CLEAR 165, BAND_FROM_CRM/REPLACE 77, FACT_PER_CRM/HOLD 45, FACT_PER_CRM/RESOURCE 17, FACT_PER_CRM/REWRITE 6, NARRATIVE/REWRITE 3, NARRATIVE/SCRUB_ONLY 17, NARRATIVE/SUPERSEDED 1, OTHER/SCRUB_ONLY 1, SRC_ENTRY/DROP_ENTRY 32.

## 2. Employee bands

All 242 organizations in BAND_FROM_CRM hold a CRM-derived `employee_band_ohio`. P1 bars the value, not only the sentence, so each is REPLACEd by a public band or CLEARed. Precedence (R13 adapted to an Ohio org band; always banded, never a headcount; the CRM-derived value is never used as a cross-check):

1. organization with **exactly one non-closed Ohio site**: OSHA ITA 300A (CY2025; reliability ok; size-code and hours screens consistent; one ITA establishment at the site; strong match; no site caution), then OSHA inspection employee count (strong match, latest inspection has a count, band stable), then Form 5500 only if the org holds no non-Ohio site;
2. otherwise the Form 5500 org-level Ohio proposal (sponsor address in Ohio), only if the org holds no non-Ohio site (a sponsor-level plan count is not an Ohio count for a multi-state org);
3. R13 review: a usable source that disagrees by more than one band with another usable source, or with an existing in-vocabulary site band, is **not applied**: the value is cleared and the candidate parked in `holds.csv` (BAND_REVIEW);
4. no usable public source: CLEAR.

| Result | Organizations | Note |
|---|---:|---|
| REPLACE (public band, public-basis clause in notes) | 77 | OSHA ITA 27, OSHA inspection 16, Form 5500 org-level 34; a public band equal to the current value needs no value edit |
| CLEAR, no public source matched | 152 | value emptied, clause removed |
| CLEAR, candidate not auto-applicable | 13 | 2 R13 conflicts and 11 unusable ITA/inspection rows (moderate match, reliability review or suspect, unstable inspections); candidate listed in holds, never applied |

Flags in `band_actions.csv`: 28 Form 5500 rows ask the integrator to confirm single-establishment (or an org-wide plan count) from the company's own site; 6 multi-Ohio-site organizations where the plan count is org-wide; 4 inspection counts from 2019-2020. The notes clause cites the public basis, source date (ISO for ITA/inspection; plan year for Form 5500) and "band, not a headcount"; the organizations table has no `employee_count_source_date` column, so the date lives in that clause. **Open schema point:** the Form 5500 lane asks for a `government_filing` evidence row per band, but the section 4.13 `claim_type` enum has no size/band claim. I did not improvise one (AGENTS.md section 1); evidence rows for bands need a ruling. The column `band_actions.csv: stored_in_250plus` is read from the stored `tier1_qualifier`, not from any old band.

### Tier-1 qualifier (derived; the integrator must re-run the derivation, never hand-edit)

48 organizations store `employees_250plus` today (46 in this packet, 2 outside it and unaffected). If the packet is applied, **41 lose the value (30 cleared, 11 replaced by a lower public band), 5 keep it, and 7 would gain it** (the dry run shows exactly 48 new V-29 drift warnings). `tier1_qualifier_basis` text goes stale for the same rows. Several large multi-state parents are among those that lose it; the lanes' packets hold no public Ohio band for them, so restoring them needs a research lane (ITA/inspection per Ohio establishment). Names are in the data under the ids below.

| org_id | proposed band action | public basis |
|---|---|---|
| ORG-000003 | CLEAR | - |
| ORG-000006 | CLEAR | - |
| ORG-000009 | CLEAR | - |
| ORG-000047 | CLEAR | - |
| ORG-000124 | CLEAR | - |
| ORG-000135 | CLEAR | - |
| ORG-000176 | CLEAR | - |
| ORG-000188 | CLEAR | - |
| ORG-000218 | CLEAR | - |
| ORG-000237 | CLEAR | - |
| ORG-000238 | CLEAR | - |
| ORG-000340 | CLEAR | - |
| ORG-000385 | REPLACE 100-249 | FORM5500_ORG |
| ORG-000421 | CLEAR | - |
| ORG-000451 | CLEAR | - |
| ORG-000482 | CLEAR | - |
| ORG-000500 | CLEAR | - |
| ORG-000506 | REPLACE 10-49 | FORM5500_ORG |
| ORG-000628 | REPLACE 10-49 | OSHA_INSPECTION |
| ORG-000651 | CLEAR | - |
| ORG-000671 | REPLACE 100-249 | OSHA_INSPECTION |
| ORG-000686 | CLEAR | - |
| ORG-000714 | CLEAR | - |
| ORG-000756 | CLEAR | - |
| ORG-000766 | REPLACE 100-249 | FORM5500_ORG |
| ORG-000777 | CLEAR | - |
| ORG-000782 | CLEAR | - |
| ORG-000794 | REPLACE 10-49 | OSHA_INSPECTION |
| ORG-000835 | CLEAR | - |
| ORG-000879 | REPLACE 100-249 | OSHA_ITA |
| ORG-000880 | CLEAR | - |
| ORG-000889 | REPLACE 50-99 | OSHA_ITA |
| ORG-000907 | CLEAR | - |
| ORG-000974 | CLEAR | - |
| ORG-001129 | REPLACE 100-249 | OSHA_INSPECTION |
| ORG-001336 | CLEAR | - |
| ORG-001422 | CLEAR | - |
| ORG-001442 | CLEAR | - |
| ORG-001475 | REPLACE 100-249 | FORM5500_ORG |
| ORG-001668 | REPLACE 10-49 | OSHA_ITA |
| ORG-000938 | CLEAR | - |

Keep (5):

| org_id | proposed band action | public basis |
|---|---|---|
| ORG-000589 | REPLACE 500-999 | FORM5500_ORG |
| ORG-000846 | REPLACE 500-999 | FORM5500_ORG |
| ORG-001077 | REPLACE 250-499 | OSHA_ITA |
| ORG-001328 | REPLACE 250-499 | OSHA_ITA |
| ORG-001425 | REPLACE 500-999 | OSHA_ITA |

Gain (7; verify the single-establishment/org-wide flags before relying on them):

| org_id | proposed band action | public basis |
|---|---|---|
| ORG-000057 | REPLACE 250-499 | FORM5500_ORG |
| ORG-000199 | REPLACE 250-499 | FORM5500_ORG |
| ORG-000343 | REPLACE 250-499 | FORM5500_ORG |
| ORG-000366 | REPLACE 500-999 | FORM5500_ORG |
| ORG-000414 | REPLACE 250-499 | FORM5500_ORG |
| ORG-001130 | REPLACE 500-999 | OSHA_ITA |
| ORG-001454 | REPLACE 250-499 | OSHA_ITA |

## 3. FACT_PER_CRM

Rule: re-source only where a public source is **already cited in the same row, sits in `data/evidence.csv`, or is carried by a held site/successor record**; otherwise HOLD and propose the tier the remaining public evidence supports (SCHEMA 4.1 weakest-must-have-field; 4.13 ceilings: own site or filing up to A, directory or press up to B, a registry address alone caps at C, nothing public means the address leg is unconfirmed, tier U). No new research was done and no fact was added.

### 3a. Re-sourced to public evidence already in the repo (17 clauses)

| record | field | public basis already in the repo |
|---|---|---|
| ORG-000083 | hq_city | own-site text and trade press name the recorded city; the own-domain street address is in another city (review) |
| ORG-000103 | hq_city | own-site plant address on held site record SITE-000212 (Tier A) |
| ORG-000534 | ultimate_parent_name | locations page and own-domain ISO certificate already cited in the row |
| ORG-000547 | hq_city | own-domain ISO certificate listing country headquarter functions, on held site record SITE-002777 |
| ORG-000825 | hq_city | EPA registry facility record on held site SITE-000828 (registry class caps at C) |
| ORG-000949 | hq_city | EPA registry facility records on held site SITE-001023 (registry class caps at C) |
| ORG-001076 | hq_city | own-site street address already stated in the row |
| ORG-001160 | hq_city | own-site HQ address already stated in the row |
| ORG-001381 | hq_city | row states the corporate offices; directory and own site cited in sources (ceiling B) |
| ORG-001590 | hq_city | trade reporting in the row names a plant at the recorded city; it does not state HQ (ceiling C) |
| ORG-001772 | hq_city | row cites an unnamed directory (weak; see holds) |
| ORG-001842 | hq_city | successor ORG-001568 holds a Tier A own-site site record in the city |
| ORG-001846 | hq_city | row states the current operator is based in the city |
| ORG-001863 | hq_city | held site record SITE-002132 from a verified wave packet (Tier B) |
| ORG-001871 | hq_city | successor ORG-000902: an independent verification places the same business in the city |
| ORG-001877 | hq_city | held site record SITE-002131 with street address and own-site URL (Tier B) |
| ORG-001890 | hq_city; founding year | own-site note on held site SITE-002051; the production-scope claim is held separately |

One further clause (ORG-000683) is classed NARRATIVE: it described an HQ-city change that a later pass superseded, and the current HQ city already has an own-site address evidence row.

### 3b. HOLD: needs public evidence (48 items in `holds.csv`, plus 13 band-review candidates)

* **HQ-city changes adjudicated on the CRM** (24 clauses on 22 organizations): the value stays as recorded (changing it would be a new fact or an owner-level restore decision); the note is rewritten neutrally ("no public source cited for the new value"); the tier follows the public evidence.
* **Establishments with a CRM-only location basis** (18 organizations, incl. the merged tombstone ORG-001882): the own site settles identity and activity but the city or establishment has no public source in the repo.
* **7 organizations where public evidence already in the row points to the replaced value instead** (REVERT_CANDIDATE: ORG-000191, 000239, 000273, 000676, 000777, 001013, 001908). Restore-or-research is a call for the integrator or a research lane, not for a packet.
* ORG-001225 (ecosystem): the `website` value changed on a CRM basis; it stays, tier already U.
* ORG-001814, ORG-001851: a relationship and an acquisition date with a CRM basis; clauses dropped, research lane to cite.
* ORG-001890: the production-scope claim (ring 1, NAICS 326122) conflicts between the org note and the own-site note on its site record (SCOPE_CONFLICT); ring/scope is an owner ruling, nothing changed here.
* ORG-000534 (acquisition details uncited), ORG-001772 (directory unnamed), ORG-001930 (description thin), ORG-000083 (two cities in the public evidence), ORG-001430 (recorded city matches no held site of the entity).

### 3c. Tier proposals (edit class `TIER_DROP`, independent of the text scrub)

42 organizations (A to U 1, B to C 3, B to U 27, C to U 11). Organization tier counts in the dry-run copy: A 1029 to 1028, B 2540 to 2510, C 588 to 580, U 23 to 62. The integrator may decline them wholesale with `--skip-tier-drop` (text, source and band edits do not depend on them); if the owner prefers restoring earlier values for the REVERT_CANDIDATE rows, those keep their tier. Merged tombstones (ORG-001842, 001846, 001871, 001882) get no tier edit.

| org_id | tier now | proposed | reason class |
|---|---|---|---|
| ORG-000035 | B | U | HQ city has no public source |
| ORG-000042 | C | U | HQ city has no public source |
| ORG-000169 | C | U | HQ city has no public source |
| ORG-000181 | C | U | HQ city has no public source |
| ORG-000191 | B | U | HQ city has no public source |
| ORG-000239 | B | U | HQ city has no public source |
| ORG-000273 | B | U | HQ city has no public source |
| ORG-000523 | B | U | HQ city has no public source |
| ORG-000655 | B | U | HQ city has no public source |
| ORG-000676 | B | U | HQ city has no public source |
| ORG-000777 | B | U | HQ city has no public source |
| ORG-000825 | B | C | support ceiling (registry/press only) |
| ORG-000894 | B | U | HQ city has no public source |
| ORG-000907 | A | U | HQ city has no public source |
| ORG-000925 | B | U | HQ city has no public source |
| ORG-000949 | B | C | support ceiling (registry/press only) |
| ORG-001013 | B | U | HQ city has no public source |
| ORG-001029 | B | U | HQ city has no public source |
| ORG-001157 | B | U | HQ city has no public source |
| ORG-001172 | B | U | HQ city has no public source |
| ORG-001202 | B | U | HQ city has no public source |
| ORG-001417 | B | U | HQ city has no public source |
| ORG-001430 | B | U | HQ city has no public source |
| ORG-001452 | B | U | HQ city has no public source |
| ORG-001590 | B | C | support ceiling (registry/press only) |
| ORG-001805 | C | U | establishment/city has no public source |
| ORG-001831 | C | U | establishment/city has no public source |
| ORG-001833 | C | U | establishment/city has no public source |
| ORG-001844 | B | U | establishment/city has no public source |
| ORG-001845 | B | U | establishment/city has no public source |
| ORG-001853 | B | U | establishment/city has no public source |
| ORG-001862 | C | U | establishment/city has no public source |
| ORG-001864 | B | U | establishment/city has no public source |
| ORG-001867 | C | U | establishment/city has no public source |
| ORG-001870 | C | U | establishment/city has no public source |
| ORG-001872 | B | U | establishment/city has no public source |
| ORG-001873 | B | U | establishment/city has no public source |
| ORG-001884 | B | U | establishment/city has no public source |
| ORG-001885 | B | U | establishment/city has no public source |
| ORG-001888 | B | U | establishment/city has no public source |
| ORG-001906 | C | U | establishment/city has no public source |
| ORG-001908 | C | U | establishment/city has no public source |

## 4. Text scrub

* **sources (31 organizations + 1 ecosystem record):** the non-public adjudication citation is dropped; every row keeps at least 2 entries (the script asserts at least 1). Workshop paths in the remaining entries are the separate P3 pass.
* **notes (305 fields):** the band clause is removed, or replaced in place by a public-basis clause of the form "Employee band (Ohio) <band> from <public source> (...; government_filing; band, not a headcount)"; the HQ-change clause keeps the old and new city and either a public basis or "no public source cited for the new value"; lineage tags are removed where a public source is cited beside them; location claims with a CRM basis become "held pending a public source"; clauses that only mention a mismatch keep the own-site fact.
* **descriptions (9, all truncated at 201 characters and carrying provenance text):** rewritten from public facts already in the same row, 86 to 169 characters (180 enforced): ORG-001770, 001805, 001815, 001833, 001863, 001872, 001877, 001890, 001930. ORG-001930's is thin and listed in holds.
* **sites (3 notes), ecosystem (2 notes), event_participation (1 note):** scrubbed the same way.

## 5. Dry-run (fresh temp copy of `data/`, deleted afterwards)

1. `scripts/apply_p1_crm_scrub.py --data-dir <tmp>`: **603 edits on 305 rows in 12 files** (9 organization shards DE INTL MI MO OH PA TN TX WI, sites_OH, ecosystem, event_participation). By edit class: BAND_FROM_CRM 444 (215 band values + 229 notes), BAND_FROM_CRM+FACT_PER_CRM 11, BAND_FROM_CRM+NARRATIVE 2, FACT_PER_CRM 53, FACT_PER_CRM+NARRATIVE 2, NARRATIVE 16, OTHER 1, SRC_ENTRY 32, TIER_DROP 42. The drift check compares the sha256 of each current cell with `old_sha256`; a second run on the same copy aborts with 603 hash mismatches and changes nothing; a run against the real `data/` without `--i-am-the-integrator` exits 2. The other 102 data files were byte-identical afterwards, and the 12 changed files differ only in `notes`, `employee_band_ohio`, `verification_tier`, `sources`, `description_1line` (checked cell by cell on this fresh copy).
2. `ATLAS_DATA_DIR=<tmp> python3 scripts/validate.py`: **passed, 0 errors** (before: passed, 0 errors). Warnings 111 to 159: V-50 now reports "40 baselined rows now pass" (it was "40 still violate"), plus **48 V-29 drift warnings** (stored `tier1_qualifier` vs derived; exactly the 41 + 7 organizations above, cleared by the integrator's derivation re-run). The V-45/46/47/48/49/51 baselines are unchanged.
3. **Census on the temp copy: 0 case-insensitive whole-word occurrences in any column of any data file** (399 before); raw `grep -w` over the temp directory finds 0 files. 13 cells keep the letters inside registry identifiers only.

**V-50 baseline:** all **40** V-50 entries in `scripts/validate_debt_baseline.json` (31 sources strings and 9 descriptions) become "now pass" and can be deleted in the same pass. V-50 itself checks sources and descriptions only; the 299 organization notes and 3 site notes are scrubbed anyway.

**Publishability checks on this packet** (25-character windows copied from any of the 346 old cells that held the token): (a1) windows the scrub removes from the data (absent from the scrubbed data) found in any packet file or the script: 0; (a2) stricter, any window of an old cell found in a packet file or the script outside the `new_value` column of `edits.csv` (that column is the scrubbed data itself): 0; (b) case-insensitive whole-word token in any packet file or the script other than this report: 0; in this report the word appears only as the name of the ruling's subject, never as quoted record content.

## 6. Integrator checklist

1. Claim the QUEUE line "Integrator - P1 CRM cleanup"; back up the touched files; run `scripts/apply_p1_crm_scrub.py --data-dir data --i-am-the-integrator` (campaign-mode rules 2a-2d apply to a direct push; otherwise branch/PR). Optionally `--skip-tier-drop`.
2. Re-run the tier1_qualifier derivation (basis strings too); list changed rows in the pass journal.
3. Delete the 40 V-50 baseline entries; re-run `scripts/validate.py` (expect 0 errors).
4. No evidence rows or IDs were minted. Rule the band claim-type question (section 2) before adding evidence rows.
5. Route `holds.csv` to research lanes. A hold that resolves to Tier A/B needs the lane's evidence rows (section 4.13) before the tier is restored.
6. Noted, out of scope: workshop paths in remaining `sources` (P3); V-50 checks only sources and descriptions, so consider extending it to notes; the 35 `pic_member=true` rows all carry a membership URL.
7. `edits.csv` stores a sha256 of each old cell. For enum-valued cells (tier, band) a hash can be reversed by trying the few possible values, so it hides nothing there; it is a drift check, not a secret.

## 7. Caveats

* Tier proposals apply the weakest-must-have-field rule literally; 27 B-to-U moves is a large visible change, each with a reason class above. The REVERT_CANDIDATE rows suggest the adjudication contradicted public evidence in at least 7 cases, so the owner may prefer restore-then-verify to demotion.
* Form 5500 org-level bands are sponsor-level plan counts (R7f: admissible, banded, `government_filing`).
* ITA/inspection bands go to the org only where the Atlas holds one non-closed Ohio site; it may not list every Ohio establishment.
* New clauses add no facts beyond what the row, a held site row or `evidence.csv` already stated; "held pending a public source" is a status, not a claim.
