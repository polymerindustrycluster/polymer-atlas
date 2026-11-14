# Skimpy-state leftover STILL_UNCERTAIN settle (2026-11-12)

Follow-up to the 2026-11-04 skimpy-state packets (`tasks/*-skimpy-2026-11-04/` and the UT pilot). Those packets left 78 `STILL_UNCERTAIN` rows, each with a named settling fact. This pass checked whether later PRs already resolved the fact on `main`, then settled what public primary evidence could settle.

**Not in this pass:** Ohio organization or site shards; people, programs, ecosystem, or Muse academic-depth / wave4 / QUEUE files. No emails. Paid API calls: 0.

**ID ledger (reserved, verified above main maxima and open PRs on 2026-11-12):** ORG-013800–ORG-013801, SITE-020000–SITE-020005, EVD-350000–350016 (CT), EVD-350100–350116 (OR/KS), EVD-350200–350229 (AR/OK). Main maxima at kickoff were ORG-013500, SITE-019101, EVD-333058 (org/site shards). No IDs in the reserved ranges were already used.

## Already resolved on main (no new row)

| ID | Outcome |
|---|---|
| QMS-AR-24 Building Materials Manufacturing LLC, Arkadelphia | Already `SITE-005437` GAF - Arkadelphia (PMMA) at 151 MCCELLAN BLVD under `ORG-004251`. Operator and product settled. |
| 3form Ecoresin plant, 955 S 3800 W, Salt Lake City | Already `SITE-008189` under `ORG-004817`, with EPA FRS 110070516125 **and** the Utah DAQ FCE memo — the named second-source settling fact is satisfied. |
| QMS-CT-30 LATICRETE Bethany | Parent `ORG-004965` is on main (PR #69 merged). Site applied in the CT PR. |
| QMS-OR-08 Carestream White City | Parent `ORG-004923` is on main (PR #64 merged). Site applied in the OR/KS PR. |
| QMS-KS-40 Wichita Fiber Glass Systems | Parent `ORG-004877` NOV Inc. is on main (PR #57 merged). Site applied in the OR/KS PR. |

ID and NH skimpy packets had **no** leftover STILL_UNCERTAIN rows (the original wave exhausted those queues).

## Applied in the 2026-11-12 data PRs

| ID | Action | Record IDs | Tier |
|---|---|---|---|
| QMS-CT-30 | Add Bethany HQ/plant under existing LATICRETE org | SITE-020000 / ORG-004965 | B |
| QMS-CT-10 | Add Thomaston plant under existing Silgan Dispensing org; operator is Silgan Dispensing Systems Thomaston Corporation (own locations page). FRS name is still the legacy Rexam name. | SITE-020001 / ORG-000278 | B |
| QMS-OR-08 | Add White City film plant under existing Carestream org | SITE-020002 / ORG-004923 | B |
| QMS-KS-40 | Add Wichita Fiber Glass Systems plant under existing NOV Inc. org (federal only, same pattern as Iuka) | SITE-020003 / ORG-004877 | C |
| QMS-AR-34 | New org HMS Mfg. Co. (HQ Troy, MI) + Little Rock injection-molding site at 6901 Lindsey Rd | ORG-013800 / SITE-020004 | org C / site B |
| QMS-OK-17 | New org Kingspan Roofing + Waterproofing, Inc. + Stillwater site at 4115 N Perkins Rd. **Not** AHF Products (ORG-004124): Armstrong wound the plant down in 2022 and AHF did not take it. **Not** folded into Kingspan Insulation LLC (ORG-004312). | ORG-013801 / SITE-020005 | org C / site B |

## Still uncertain or held for the owner

See `tasks/owner-rulings-2026-11-12.md` for hygiene items and scope/naming questions. Notable research updates that do **not** yet support a row:

- **QMS-KS-12 Fort Scott belts plant:** Timken announced (2023-11-30, quoted in Fort Scott Biz) a planned 2025 closure of 4505 Campbell Dr. A plan to close is not a dated outcome. Not created and not rejected. Held parent for the belts business is `ORG-004288` Timken SMO LLC, whose notes already record a later 2026 Gates sale that excluded some plants.
- **QMS-OR-37 Woodburn, 2257 Progress Way:** Atkore's 2022-08-31 IR release says Cascade Poly Pipe & Conduit continued operations at its Woodburn, Oregon location after the acquisition (`ORG-007207` Atkore already exists). The release does not give 2257 Progress Way. Nearby `SITE-005321` Engineered Polymer Solutions is at 2475 Progress Way. Held until an own-page or federal record ties Cascade/Atkore to 2257.
- **QMS-AZ-25 TRC-Tucson Blvd:** Operator is Tucson Rubberized Coatings (own location page at 6351 S. Tucson Blvd). That page is written as a storefront; the company homepage calls the firm a "coating manufacturing and retailer." ITA lists manufacturing NAICS at this street. Manufacturing-at-this-address is not yet tight enough to create in this pass.
- **Whitewater, Lindon:** `ORG-006131` / `SITE-008188` already exist (tier B). The original settling fact — resin/cultured marble **cast on site** vs fabricated/sold — is still inferred. The 2026-11-12 reread of whitewaterinc.com/groutfree-surfaces describes the material and says craftsmen "install" it; it does not say the Lindon address is the casting plant.
- **PPC Payson:** still an owner/integrator dedupe among ORG-001029, ORG-004209, and later ORG-006226 (see the owner-ruling packet).
- **DuPont Fort Madison (QMS-IA-13):** `SITE-002977` Axalta Fort Madison is at 803 35th St. The queue address is 801 35th St. Not treated as the same site. Current DuPont/Qnity operator at 801 remains open (Qnity fence).
- Other leftover rows keep their original settling facts; see `verdicts.csv`.

## Checks

`python3 scripts/validate.py` must pass on each data PR. Row-loss guard should be quiet (adds only; no REMOVALS).
