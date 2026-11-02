# Validator debt: ruled mechanical subset (2026-11-02)

**Integrator for this pass:** claude-code. The repo owner asked for this pass in
session on 2026-11-02. It goes in as a small single-purpose data change on
branch `claude/amazing-allen-778h7c` (AGENTS.md §2 rule 4), not a campaign push.
**Base:** `46366c2`, which is `main` `648c109` plus the tier1 re-derivation.
That pass touched only `tier1_qualifier` / `tier1_qualifier_basis` on
organizations, so there is no column overlap with this pass.
**Rulings:** owner battery 2026-11-01, ruled "all as recommended":
- R1: site_type vocabulary.
- R4: keep the three-point confidence scale and round down.

The QUEUE line "Integrator — validator debt, now fully ruled" names
`v47_naics_proposals.csv` as the V-47 path.

## What was applied

| packet | edit_class | edits | records |
|---|---|---:|---:|
| `v45/` | `V45_SYNONYM`: same meaning, enum spelling (e.g. `office_hq` → `hq_only`, `distribution_center` → `warehouse_distribution`, `recycling_plant` → `recycling_facility`) | 139 | 139 site rows |
| `v47/` | `V47_GOVFILING_CONFIDENCE`: confidence set on rows that already carry `government_filing` | 198 | 198 site rows |
| `v47/` | `V47_GOVFILING_SOURCE_AND_CONFIDENCE`: blank source type → `government_filing`, plus confidence | 144 | 72 site rows |
| `v47/` | `V47_CONFIDENCE_ROUNDING`: `low-medium` → `low`, `medium-high` → `medium` (R4) | 19 | 10 site + 9 organization rows |
| `v47/` | `V47_CONFIDENCE_SET`: SITE-003207, `researcher_inferred` → `medium` | 1 | 1 site row |
| **total** | | **501** | **429 rows** (420 site, 9 organization) in 39 files |

V-45 debt baseline: 175 → 36. V-47 debt baseline: 312 → 22. Only the named
columns change (`site_type`; `naics_primary_source_type`, `naics_confidence`).
Per-file hashes before and after are in `file_hashes.csv`.

## Checks run before an edit was written (`build_edits.py`)

- **Every proposal:** the current cell must equal the proposal's "current" value
  (no drift since the desk packet), and the new value must be in the validator
  vocabulary.
- **Every `government_filing` row:** a cited evidence row must exist for that
  same record, with `claim_type=code` and `source_class=government_filing`, and
  must **print the record's `naics_primary`**.
- **`high` rows:** the cited code row must also come from a TRI facility record.
- **Apply:** `scripts/apply_p1_crm_scrub.py --packet-dir …` was reused. It is
  all-or-nothing, checks the old-value hash of every cell, and rewrites only
  touched files. A rehearsal on a copy gave exactly 139 V-45 and 290 V-47
  baselined rows passing.

## Held (6 records, `v47/holds.csv`): not applied, still baselined

- **SITE-003018, -003020, -003021, -003022, -003023 (Chemours):** the cited
  evidence says the code is "as stated in the TRI facility record" but does not
  print the number. **Settling fact:** the TRI record's NAICS equals
  `naics_primary`. The desk packet flagged this for integrator confirmation.
- **SITE-001115:** the proposal changes a blank source type to
  `researcher_inferred`/`low`. That is a judgement on directory-only sources,
  not a mechanical fix.

## Not in this pass (still open in QUEUE)

- **V-45, 36 rows:** 12 judgement rows and 24 owner rows. They need a per-row
  reading against `office_other` / `service_repair` (R1a/R1c).
- **V-47, the 15 `company_website`/`own_site` rows:** the desk packet verdict is
  STILL_UNCERTAIN. Mapping them to `company_disclosed` is **not** recommended
  (SCHEMA §2.1).
- **V-46 ring backfill (203 VERIFIED, of which 87 are NAICS-led and ride
  R9/§2.1 review), V-48, V-49.**

No evidence rows were added. Every changed value is a spelling normalization or
a provenance label backed by evidence rows already held, cited in each edit's
`rationale`. No IDs were allocated.

Rebuild against the pre-pass tree:

```bash
git archive 46366c2 data | tar -x -C /tmp/pre
python3 tasks/validator-debt-apply-2026-11-02/build_edits.py --data-dir /tmp/pre/data
```

Applying both packets to that tree reproduces the committed `data/`
byte-for-byte; this was checked. Against the post-pass tree every proposal
reports drift and the packets come out empty.
