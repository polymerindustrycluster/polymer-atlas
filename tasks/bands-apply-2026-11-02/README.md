# Employee bands under R13 (2026-11-02)

**Integrator for this pass:** claude-code. The owner requested this pass in
session on 2026-11-02, and it goes in as a PR.
**Ruling:** owner battery 2026-11-01, R13 (SCHEMA v1.7.7 §1). The site-band
precedence is:
1. OSHA ITA (Form 300A, latest calendar year);
2. then the latest OSHA inspection;
3. then Form 5500, for single-establishment organizations only.

Any source more than one band away from the pick sends the row to review.
Ohio organization bands come from Form 5500 (R7f).

**Input:** `tasks/integration-ready-oh-pa-2026-11-02/band_updates.csv`. It was
rebuilt on 2026-11-02 against the current tree, so it reflects the pass-40 P1
band edits. Only `status = APPLY` and `action = fill` rows are applied.

## Applied

| edit class | rows | column |
|---|---:|---|
| `BAND_SITE_ITA` | 1,384 | `sites.employee_band_site` |
| `BAND_SITE_INSPECTION` | 334 | `sites.employee_band_site` |
| `BAND_SITE_FORM5500` | 76 | `sites.employee_band_site` (single-establishment orgs) |
| `BAND_ORG_OHIO_FORM5500` | 202 | `organizations.employee_band_ohio` |
| `BAND_SOURCE_NOTE` | 1,996 | `notes` append: `BAND-SOURCE: … from <source>, <date> …` |

That is **3,992 cell edits over 1,996 records** in 49 files, with 0 drift holds.
The edits were hash-checked by `scripts/apply_p1_crm_scrub.py --packet-dir`.

**Coverage, as rows with an in-vocabulary band:**

| population | before | after |
|---|---:|---:|
| Site rows, all states (5,773) | 85 | 1,879 |
| Ohio site rows (2,009) | 15 | 428 |
| Ohio organizations (`employee_band_ohio`, 1,800) | 83 | 285 |

**tier1 qualifier:** re-derived with `scripts/derive_tier1.py --refresh-basis
--write`. **13 organizations gain `employees_250plus`**, all from public
Form 5500 bands; 0 lose it. The rows are listed in `tier1/changes.csv`.

## Not applied

- **147 REVIEW rows** (140 site, 7 organization): the sources disagree by more
  than one band, or the pick differs from an in-vocabulary band already held.
- **139 SKIP rows:** OSHA ITA flagged the reliability as not ok.
- **60 no-op rows:** the band is already equal.

## Open item for the owner

**Size bands have no evidence `claim_type`.** SCHEMA §4.13 lists no
`claim_type` for an employee band. Until one is named, the source and date
travel in the `BAND-SOURCE:` notes append (as in the pass-40 P1 band edits) and
in `band_updates.csv`. This is queued as a ruling item and is not self-ruled.

## Checks

- **Rehearsal:** on a copy, validate.py passed with 0 new warnings. The applied
  tree is byte-identical to the rehearsal copy.
- **After applying:** validate.py OK and all unit tests pass.
