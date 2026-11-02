# Rest-of-Ohio + PA capability application (2026-11-02)

**Integrator for this pass:** claude-code. The owner requested this pass in
session on 2026-11-02, and it goes in as a PR.
**Input:** the 14 lanes in `tasks/wave-oh-capabilities-2026-11-01/`:
- `oh_lane1`–`8`: Ohio sites outside PIC-12;
- `pa_lane1`–`6`: Pennsylvania.

**Pipeline:** the same as the PIC-12 pass (`tasks/capability-apply-2026-11-02/README.md`):
1. `build_integration_sets.py --packets "tasks/wave-oh-capabilities-2026-11-01/*lane*"
   --out tasks/integration-ready-oh-pa-2026-11-02` built the change sets. Its dry
   run was OK.
2. `tasks/capability-apply-2026-11-02/build_edits.py --sets … --out …` turned
   them into hash-checked cell edits and an evidence append. 0 drift holds.
3. A blind 40-row audit was run by a low-cost subagent (`audit_sample.csv`,
   `audit_results.csv`).
4. The packet was applied with `apply_p1_crm_scrub.py --packet-dir` plus
   `--append-evidence`, rehearsed on a copy first.

**Scope:** capability tag columns, `CERT-SITE` notes, and the evidence rows.
Bands, conflicts, HOLD sites and off-vocabulary fields are out of scope.

## Applied

- **Cell edits:** **1,608** over **738 records** (456 site rows, 282 organization
  rows) in 12 files. Values are only added, never removed. Tiers are unchanged.
- **Evidence:** **3,580** own-site `scope` evidence rows,
  **EVD-016322..EVD-019901** (`supports_A`, allocated above the tree-wide
  maximum EVD-016321).

**Fill-rate change (`processes` / `materials` / `markets_served`):**

| site population | rows | before | after |
|---|---:|---|---|
| Ohio sites outside PIC-12, active | 922 | 17.2% / 2.9% / 0.0% | 40.2% / 22.0% / 20.9% |
| All Ohio site rows | 2,009 | 29.8% / 16.7% / 9.4% | 40.3% / 25.4% / 19.0% |
| All PA site rows | 777 | 6.0% / 5.7% / 0.0% | 21.0% / 19.3% / 14.0% |

## Blind audit and the integrator's dispositions

**What was checked:** 40 rows (24 site, 16 organization), one per URL.
- **Quote found on page:** 36 of 36 fetched. 4 fetches failed; those are
  availability, not evidence.
- **Supports the claimed value:** yes 30, partial 5, no 1.

**Dispositions:**
- **#1 (no):** SITE-002844 Rebling, `phenolic`. The quote was truncated; the
  page names phenolic in the next sentence. **Re-cited** with "along with
  thermoset materials like epoxy, phenolic, and diallyl phthalate" (checked
  against the fetched page).
- **#13 (partial):** SITE-002214 Pittsburgh Plastics, `thermoforming_unspecified`.
  The quote was a generic definition. **Re-cited** with the company's own
  sentence: "Pittsburgh Plastics Manufacturing can thermoform plastic films and
  fabrics".
- **#31 (partial):** ORG-002601 C-I Inc., `epdm`. Single tokens from a generic
  ASTM abbreviation table. **Held**, together with the four sibling values from
  the same page (natural_rubber_nr, neoprene_cr, sbr, viton_fkm), in
  `holds.csv`. Their 5 evidence rows were removed before allocation. The org
  gets silicones only, which comes from its markets page.
- **#2 (partial):** SITE-002786 ADS Shippenville, `recycling_mechanical`. Kept:
  the site is already typed `recycling_facility`, so the process fits it. The
  quote is weak.
- **#23 (partial):** SITE-001283 Vernay, ISO 9001 site note. Kept: the site
  *is* Yellow Springs, the location row on Vernay's ISO 9001 certificate PDF.
- **#38 (partial):** ORG-000905 ISCO, `chemical_mining_metals_processing` from
  "mining and aggregate". Kept as vocabulary breadth (the same call as the
  PIC-12 audit).

**Measured rate:** 1 citation defect and 1 weak value in 36 judged rows. Both
are corrected or held above. This is a sample, not a proof for all 3,580 rows.

## Checks

- **Rehearsal:** on a copy, validate.py passed with 0 new warnings.
- **Applied tree:** byte-identical to the rehearsal copy. validate.py OK,
  `derive_tier1.py` 0 drift.

| file | sha256 before | sha256 after |
|---|---|---|
| `data/evidence.csv` | `49e30db26a442b80…` | `abeb89f7f740de69…` |
| `data/organizations_CA.csv` | `2a194282a3c274d6…` | `65cb9e9902c6a4b0…` |
| `data/organizations_KY.csv` | `f4c82f97a8c3e2eb…` | `47e73d3373e109c3…` |
| `data/organizations_MI.csv` | `ac0e65c2358d6e2d…` | `4e5a2acee82f8808…` |
| `data/organizations_MO.csv` | `c63b6f987397c63d…` | `8f34c0de906c258c…` |
| `data/organizations_NJ.csv` | `45ca0cec4dd0fd59…` | `2052078182f9e3a9…` |
| `data/organizations_NY.csv` | `e2bfaf68c5dd6330…` | `47b5af293e65ec61…` |
| `data/organizations_OH.csv` | `9b18c1941a3d9fa6…` | `6c66eae7466bd84d…` |
| `data/organizations_PA.csv` | `a9a48a271f08ca0d…` | `0e2fbf33102bf9fa…` |
| `data/organizations_TX.csv` | `3d00608f83e84e61…` | `260e831479e77f4b…` |
| `data/organizations_WI.csv` | `cf8c33ec6e41c1a6…` | `d4d7bf764d058406…` |
| `data/sites_OH.csv` | `ea8f80845fe55552…` | `8166b77ae3006a2f…` |
| `data/sites_PA.csv` | `87191f26e1be17b4…` | `22f3c6371bf01b5d…` |
