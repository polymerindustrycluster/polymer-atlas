# PIC-12 capability application (2026-11-02)

**Integrator for this pass:** claude-code. The repo owner asked for this pass in
session on 2026-11-02. It goes in as a single-purpose data change on branch
`claude/amazing-allen-778h7c` (AGENTS.md §2 rule 4), not a campaign push.

**Input:** the integration-ready change sets in
`tasks/integration-ready-2026-11-01/` (commit `dfde7da`), built from the
611-site PIC-12 capability wave (pilot + tranche 1 + tranche 2 lanes, own-site
evidence only).

**Scope:** capability tag columns only:
- site `processes` / `materials` / `markets_served`, plus a `CERT-SITE:` notes
  append for site certifications (sites have no certifications column; R12
  precedent);
- organization `processes` / `materials` / `markets_served` / `certifications`;
- their evidence rows.

**Not in scope:** employee bands (`band_updates.csv`), the 665–689 rows in
`conflicts.csv`, HOLD sites, off-vocabulary existing fields, and `*_other_note`
values. These are all left for later passes.

**Base:** `3b99c44`.

## Drift check

Re-running `scripts/build_integration_sets.py` against `3b99c44` reproduced the
capability sets unchanged, except for the `tier` column on 4 organizations.
That column is informational only and comes from the P1 tier drops. The sets
were therefore used as committed.

`build_edits.py` re-checks every field against the current tree (the current
cell must equal the set's `current_*` value): **0 drift holds**.

## What is applied

| edit_class | cell edits |
|---|---:|
| `CAP_SITE_PROCESSES` | 192 |
| `CAP_SITE_MATERIALS` | 204 |
| `CAP_SITE_MARKETS_SERVED` | 181 |
| `CAP_SITE_CERT_NOTE` (site notes append) | 71 |
| `CAP_ORG_PROCESSES` | 88 |
| `CAP_ORG_MATERIALS` | 126 |
| `CAP_ORG_MARKETS_SERVED` | 157 |
| `CAP_ORG_CERTIFICATIONS` | 23 |
| **total** | **1,042 cell edits over 463 records** (282 site rows in `sites_OH.csv`; 181 organization rows in 7 organization shards) |

- **How values merge:** each value is the union of the existing in-vocabulary
  tokens and the new ones, in `docs/schema/vocab.json` order. Existing values
  are never removed.
- **Evidence:** **3,012 evidence rows** (EVD-013310..EVD-016321), allocated above
  the tree-wide maximum EVD-013309. They split into 1,899 site rows and 1,113
  organization rows, and 95 of them reconfirm a value the record already
  carried.
  - All rows are `claim_type=scope`, `source_class=own_site`,
    `tier_effect=supports_A` (the own_site ceiling, §4.13), each with a ≤25-word
    quote from the cited page.
  - Every row's claimed value is present on its record after the edits; 0 rows
    were dropped.
- **Verification tiers:** unchanged (0 tier edits).

## Effect on fill rates (`data/sites_OH.csv`)

| population | rows | processes | materials | markets_served |
|---|---:|---|---|---|
| Ohio site rows | 2,009 | 21.4% → 29.8% | 7.8% → 16.7% | 0.3% → 9.4% |
| PIC-12 active site rows | 962 | 26.2% → 43.7% | 12.8% → 31.3% | 0.7% → 19.5% |

## Rehearsal (copy of `data/`)

1. `apply_p1_crm_scrub.py --packet-dir tasks/capability-apply-2026-11-02`
   (all-or-nothing, old-value hash per cell) applied 1,042 edits across 463
   rows in 8 files.
2. `build_edits.py --append-evidence` appended 3,012 rows.
3. `validate.py` then passed, with no new warnings and none removed.
   `derive_tier1.py` reports 0 drift, so capability fields don't feed the
   qualifier.

## Rebuild

```bash
git archive 3b99c44 data | tar -x -C /tmp/pre
python3 tasks/capability-apply-2026-11-02/build_edits.py --data-dir /tmp/pre/data
```

## Blind spot-check before applying (cheap subagent)

A Haiku subagent audited a seeded random sample of **40 evidence rows** (24 site,
16 organization; one row per distinct URL). It fetched each cited page and
judged the quote. It was not shown the change sets or this pass's reasoning.
Results are in `audit_sample.csv` and `audit_results.csv`.

- **Quote found on page:** 33 of 33 fetched.
  - 7 fetches failed (403/429/500/406). That is an availability signal, not
    evidence, so those 7 were judged from the quote text only.
- **Quote supports the claimed value:** yes 31, partial 9, no 0.
- **Integrator disposition of the 9 partials:** all 9 were kept, 0 wrong.
  - **Three were factual, and I checked them against the data:**
    - #6: SITE-001316 *is* "963 Evans Ave", a facility the Shin-Etsu ISO 14001
      quote names.
    - #14: SITE-000001 is Avient Avon Lake HQ, listed as "Avon Lake Corporate,
      OH" on the certificate list.
    - #20: Lerner Molded Plastics (ORG-000417) holds exactly one site, so its
      ISO 9001 statement covers that site.
  - **Six are vocabulary-breadth or weak-quote cases, not wrong values:**
    - #2: acrylic fabrication → `plastics_fabrication_welding`.
    - #5: R2 Sealants custom formulations → `adhesive_sealant_formulation`.
    - #9: "prime or recycled content" → `recycled_content_pcr_pir`.
    - #18: "Mining" → `chemical_mining_metals_processing`.
    - #25: Neff-Perkins names natural/synthetic rubbers on its capabilities
      page.
    - #38: System Seals lists UHMWPE on its materials page.

  These quotes are weaker witnesses than the rest; a future re-verification
  rotation can tighten them.
- **Measured rate:** 0 wrong claims in 40 sampled. That bounds, but does not
  prove, the error rate across the 3,012 rows.

## Pass journal

The packet was applied to `data/` at base `e458e34` (= `3b99c44` plus the
packet commit):
1. `apply_p1_crm_scrub.py --packet-dir tasks/capability-apply-2026-11-02
   --i-am-the-integrator` applied 1,042 edits across 463 rows in 8 files.
2. `build_edits.py --append-evidence --i-am-the-integrator` appended 3,012
   rows, EVD-013310..EVD-016321.
3. `diff -r data <rehearsal copy>`: identical.
4. `validate.py`: OK. `derive_tier1.py`: 0 drift. Unit tests: all pass.

| file | sha256 before | sha256 after |
|---|---|---|
| `data/evidence.csv` | `7d8717c45691509c…` | `49e30db26a442b80…` |
| `data/organizations_DE.csv` | `e48f094a3d21855a…` | `5e7f9af65b299937…` |
| `data/organizations_MO.csv` | `3fcea77c8eb448b3…` | `c63b6f987397c63d…` |
| `data/organizations_OH.csv` | `4ea7ab790f79ee32…` | `9b18c1941a3d9fa6…` |
| `data/organizations_PA.csv` | `b7ebb8c96bee7eea…` | `a9a48a271f08ca0d…` |
| `data/organizations_TN.csv` | `3f264cf5102b6444…` | `83d69b51239f0166…` |
| `data/organizations_TX.csv` | `e81e97124d368bbd…` | `3d00608f83e84e61…` |
| `data/organizations_US.csv` | `d0059b30241a8c65…` | `1977087f75cdf10a…` |
| `data/sites_OH.csv` | `eb4aad5a5009302d…` | `ea8f80845fe55552…` |
