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

## Lane results (2026-11-01)

Desk pass over repo facts only (site rows, `data/evidence.csv`, `registry_links`, SCHEMA §1, §2.1, §2.2, §4.13 and the 2026-10-31 owner rulings). No web fetches. Nothing under `data/` was edited, no IDs were allocated, no evidence rows were minted. Two files were produced, one row per worklist row: `v46_ring_proposals.csv` and `v47_naics_proposals.csv`. Counts are site rows or organization rows at the pinned commit unless stated.

### V-46 site ring backfill (383 site rows with blank `ring_primary`)

| Result | Site rows |
|---|---:|
| VERIFIED, proposed Ring 1 | 109 |
| VERIFIED, proposed Ring 2 | 92 |
| VERIFIED, proposed Ring 3 | 2 |
| **VERIFIED total** | **203** |
| STILL_UNCERTAIN (no ring proposed) | 180 |

**Basis of the 203 VERIFIED rows.** (a) 162 rows: a facility-level government NAICS (EPA TRI record; the site row's source type or a `code` evidence row) that SCHEMA §2.2 lists as a Primary signal, with consistent `processes[]`. 75 of these also have an independent site-attributed witness (own site, 10-K, permit, press). **87 are NAICS-led**: the processes look mechanically assigned from the NAICS (all 60 `325510` rows carry `coating_formulation`, all 17 `325520` rows carry `adhesive_sealant_formulation`), so the NAICS is effectively the only basis. §2.1 says NAICS never decides a ring alone; the integrator may want to hold those 87 for an owner nod (the 60 coatings and 17 adhesives rows are the bulk). (b) 41 rows: a site-attributed process or product statement (own site, ISO annex, permit, EPA letter, 10-K Item 2 product row, press) that passes a §1 test. Two of these (SITE-002858, SITE-002859) have **no evidence rows at all**; the witness lives only in `notes`, so an observing lane must write the scope row before they apply.

Never used as a reason: the parent's ring. For information only, 19 of the 203 differ from the parent org's ring (e.g. Olin Freeport epoxy resin plant Ring 1 under a Ring 2 parent; AkzoNobel Lancaster plastic-film plant Ring 1 under a Ring 2 coatings parent; STCC ethylene unit Ring 3 under a Ring 1 parent). 3 differ from the ring the creation lane itself stated (SITE-003015, SITE-003161 Enoree VAE emulsion polymerization, SITE-003179 ethylene unit).

**STILL_UNCERTAIN, by settling fact (180 site rows).** Each row carries `would_be_ring_if_settled` as information only.

| Class | Rows | Settling fact |
|---|---:|---|
| `U_SEGMENT` | 32 | Only a 10-K Item 2 segment attribution (Avient SEM/CAI, Myers Material Handling, Chemours APM); plant-level process not stated. Plant-level witness, or battery item B-V46-B |
| `U_NAICS_NOT_IN_TABLE` | 25 | TRI NAICS outside §2.2 as a Primary signal and no plant-level witness (Avery Dennison 322220 label stock, Brady, Rogers, Enpro, H.B. Fuller 332812, others) |
| `U_NAICS_PROC_CONFLICT` | 22 | NAICS and processes point to different rings (`325211` at coatings, adhesives, spray-foam and silicone plants; `326199` at an Axalta coatings plant). Resin synthesis vs blending at the address (B16 vs B28) |
| `U_ADDITIVE` | 17 | Carbon black, fumed silica, flame retardants, rubber chemicals, pigments, catalysts. No ruling covers additive/filler producers |
| `U_NONPROD` | 16 | HQ-only, sales, warehouse, R&D addresses. §1 has no ring rule for them |
| `U_MONOMER_B6B17` | 16 | Monomer/intermediate-only plants (phenol, caprolactam, amines, VAM, aniline, EO derivatives, maleic anhydride, plasticizer, HF/HCFC-22). B6/B17 would give Ring 3 but names only ethylene and EO/EG |
| `U_SEGMENT_OR_NOTIN_TABLE` | 15 | Integrated chemical complexes (Dow, Eastman, CPChem, ExxonMobil) with `polymerization` tagged by the creation lane but no plant-level witness |
| `U_SCOPE` | 13 | 11 Owens Corning mineral wool / fiberglass plants (`327993`) and 2 Solstice fluorine plants (HFO blowing agent, HFO-1234yf refrigerant): scope question, not a ring question |
| `U_PARENT_INHERITED` | 11 | Pass-4/pass-8 mechanical sweep rows whose own notes say the site NAICS/ring is inherited from the parent as `researcher_inferred` |
| `U_COMPOSITE_CORE` | 5 | Hexcel honeycomb, honeycomb-parts machining and reinforcement-fabric plants |
| `U_FIBER` | 3 | PAN precursor, UHMWPE fiber, cellulose acetate |
| `U_NAICS_TABLE_VS_B16` | 3 | `325212` is listed under Ring 2 in §2.2, but `polymerization` on site is Ring 1 under B16 (Goodyear synthetic rubber, two plants; one is an R&D office) |
| `U_NAICS_S` | 2 | Avient plants whose TRI NAICS is only a Secondary signal |

**OWNER battery items proposed (not self-ruled).** B-V46-A: ring convention for non-production sites (precedent in data: about 93% of ring-set `hq_only` rows carry the parent's ring, which sits badly with B14). B-V46-B: does a 10-K Item 2 segment attribution settle a site's ring for single-ring segments? B-V46-C: scope of mineral-wool/fiberglass plants and blowing-agent/refrigerant fluorochemical plants. B-V46-D: ring for additive, filler and catalyst producers. B-V46-E: composite-material producers (honeycomb, prepreg, reinforcement fabric). B-V46-F: `325212` table row vs B16. B-V46-G: polymer fiber producers. Also: does B6/B17 extend beyond ethylene and EO/EG?

### V-47 NAICS provenance (312 rows: 295 site, 17 organization)

| Pattern (current values) | Rows | Proposal | Verdict |
|---|---:|---|---|
| Site, `government_filing`, blank confidence | 199 | `high` 186; `medium` 12; held 1 | 198 VERIFIED, 1 STILL_UNCERTAIN |
| Site, blank source type, blank confidence | 78 | `government_filing`/`high` 76, `government_filing`/`medium` 1, `researcher_inferred`/`low` 1 | 78 VERIFIED |
| Site, `researcher_inferred`, blank confidence | 1 | `medium` (SITE-003207, inferred from an EPA process description) | VERIFIED |
| Site `researcher_inferred` / `directory_assigned`, `low-medium` or `medium-high` | 10 | `low` 8, `medium` 2, source type unchanged | VERIFIED (mechanical) |
| Site `company_website` (6) / `own_site` (1) | 7 | see below | STILL_UNCERTAIN |
| Organization `researcher_inferred` / `directory_assigned`, `low-medium` or `medium-high` | 9 | `low` 7, `medium` 2, source type unchanged | VERIFIED (mechanical) |
| Organization `company_website` (7) / `own_site` (1) | 8 | see below | STILL_UNCERTAIN |

- **`high`** only where a `code` evidence row from a facility-level government record (TRI facility record) states the code: 262 of the 277 site rows in the first two patterns. Five Chemours rows say "site NAICS as stated in the TRI facility record" without printing the number; the integrator confirms the number.
- **`medium` (13 site rows)**: 10 where the repo's own notes record the code conflicting with the documented activity (SITE-003029, -003036, -003041, -003007, -003009, -003203, -003013, -003066, -003189, -002916); SITE-003092 (code row cites a state press release, not the TRI record); SITE-003152 and -003153 (code row cites a TCEQ permit stating the pre-2022 carbon black code `325182`; the site carries TRI `325180`).
- **Held (1 site row):** SITE-003224 (Cabot Midland) cites a TRI Explorer profile only in its sources string; no `code` evidence row exists. An observing lane writes the row, then `high`.
- **Mechanical mapping `company_website`/`own_site` -> `company_disclosed` is NOT recommended for any of the 15 rows.** SCHEMA §2.1 allows `company_disclosed` only if the company itself states the code. For every row the cited page describes activity and no repo field shows a printed NAICS. Proposed fallback: `researcher_inferred`, confidence kept. Settling fact: the cited page prints the 6-digit code. Exception: ORG-002174 Parker Rust-Proof cites OSHA establishment data (a government record) in its source name; proposed `government_filing`/`medium` once the OSHA record is located (its site row SITE-002134 cites only the own site: `researcher_inferred`/`medium`).
- Rounding `low-medium` -> `low`, `medium-high` -> `medium` is exact for the vocabulary. The worklist actually holds 15 `company_website`/`own_site` rows (13 + 2) and 19 rounding rows across sites and organizations; the V-47 table above says 13 and 18.
