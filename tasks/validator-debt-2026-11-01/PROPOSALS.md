# Validator debt packet — 2026-11-01 (V-45 … V-49)

**What this is:** a packet, not a data change. On 2026-11-01, `scripts/validate.py`
gained five rules that enforce SCHEMA "MUST" lines nothing checked before (see the
V-45..V-49 block in the validator). The site and organization rows that already
broke those rules are listed in `scripts/validate_debt_baseline.json`. Those rows
only produce warnings, so `main` still validates. **Any new violation is an error.**

Nothing under `data/` was edited. Each fix below is for the integrator of record
(AGENTS.md §2 rule 7) to apply. Vocabulary questions are owner rulings
(AGENTS.md §2 rule 9) and are marked **OWNER**. Once a row is fixed, delete its ID
from the baseline file. The validator lists rows that now pass.

Pinned at commit `a3e59e7`. All counts are site rows or organization rows across
all tiers and statuses, taken from the canonical shards at that commit.

## V-45 — `site_type` outside the SCHEMA §4.5 enum (175 site rows)

File: `v45_site_type_proposals.csv`. One row per site, with its current value, a
proposed value, and a decision class.

| Class | Rows | Meaning |
|---|---:|---|
| `synonym` | 139 | Same meaning, different spelling: `office_hq`/`hq_office`→`hq_only` (75), `distribution_center`/`warehouse`/`distribution`→`warehouse_distribution` (36), `recycling_plant`→`recycling_facility` (18), `lab_r_and_d`/`tech_center`→`rd_center` (10). **Recommend: apply as a single mechanical pass.** |
| `judgement` | 12 | `branch` (11, a distributor branch: `sales_office` or `warehouse_distribution` depending on whether it holds stock) and `office_warehouse` (1). Read each row before applying. |
| `owner` | 24 | Compound or free-text values (`"hq; laboratory"`, `"North America HQ; service, parts and repair shops; …"`), 11 plain `office`, 1 `service_center`, 1 blank. |

**OWNER battery items proposed:**
- **B-V45-1:** Is a non-HQ, non-sales office (engineering or customer office) in
  scope as a site? If so, add a `office_other` enum value. If not, these rows
  are out of scope. *Recommendation:* add `office_other`. The rows are cheap to
  hold and are useful for footprint maps.
- **B-V45-2:** Mixed-use addresses: one `site_type` (the dominant physical
  function) plus a note, or a multi-value field? *Recommendation:* keep a single
  value, choose the dominant function, and record the rest in notes. The ring
  and NAICS rules already work this way.
- **B-V45-3:** `service_center` (service/repair for machinery) maps to
  `tool_shop` or needs a new value? *Recommendation:* new value `service_repair`,
  because Ring 3 machinery service is a real value-chain function.

## V-46 — site `ring_primary` blank (383 site rows)

File: `v46_site_ring_blank_worklist.csv`. 350 of these are `manufacturing_plant`.
By state: TX 60, OH 34, IL 22, MI 18, NC 15 lead the list. Most appear to be
TRI-era creations. **No mechanical fix exists.** The site ring comes from
site-specific facts (SCHEMA §1, Parker rule) and must never be copied from the
parent. *Recommendation:* a lane task (QUEUE: "Site ring backfill") that assigns
rings from each site's evidence rows and NAICS, with one evidence row per
assignment.

## V-47 — NAICS provenance missing or outside the vocabulary (312 rows: 295 site, 17 org)

File: `v47_naics_provenance_worklist.csv`.

| Pattern | Rows | Proposed fix |
|---|---:|---|
| site `government_filing` with blank confidence | 199 | Set confidence from the filing. A TRI facility-reported NAICS is `high`. **Integrator check:** confirm the filing is TRI/FRS from the site's evidence rows. |
| site NAICS with blank source type and blank confidence | 78 | Breaks AGENTS.md §4 outright. Find the source in the site's evidence or notes. If none is found, set `researcher_inferred` / `low`. |
| `company_website` / `own_site` (13 rows) | 13 | Map to `company_disclosed`. Same meaning, and the four-value vocabulary is binding. |
| `low-medium` / `medium-high` confidence | 18 | Round down (`low` / `medium`). The SCHEMA vocabulary is `high`, `medium`, `low` only. *OWNER* only if a five-point scale is preferred. |

## V-48 — employee band outside the SCHEMA §4.4 bands (20 site rows)

File: `v48_employee_band_worklist.csv`. Values such as `100-199`, `1000-2499`,
`200-499` and `201-500` come from other directories' banding. One row holds free
text with a precise headcount, which SCHEMA §4.4 forbids. Rebanding a range that
straddles a boundary (e.g. `200-499` vs the 100-249 / 250-499 bands) cannot be
done honestly. Re-source those rows or set `unknown`. Rebanding is exact only
where the source range sits inside one band.

## V-49 — `markets_served` values outside the SCHEMA §3.3 vocabulary (8 organization rows)

ORG-001478, ORG-001481, ORG-001484 … ORG-001489 (organizations_OH.csv) carry free
text such as `automotive`, `automotive/EV`, `medical devices` and
`automotive (Honda, Toyota, Subaru)`. Proposed mapping: `automotive*`→`automotive_oem`
(confirm OEM vs aftermarket from the source), `medical devices`→`medical_device`,
`electronics`→`electronics_electrical`. Values with no enum match (`cosmetics`,
`motorcycle`, `sports and commercial flooring`, and `plastics/coatings/inks`, which are
materials, not markets) → `other_specified_in_notes` with the text moved to notes.
Customer names belong in notes, never in the value.

## How the baseline works (for every harness)

- `python3 scripts/validate.py` warns once per rule with the debt count.
- `python3 scripts/validate.py --debt-details` lists every grandfathered row.
- A row in the baseline that now passes is reported, so its ID can be deleted.
- **Never add an ID to the baseline to get a new row through.** The baseline only
  shrinks. Regenerating it needs an owner-approved PR.
- `python3 -m unittest scripts/test_validate.py` mutation-tests these rules.
