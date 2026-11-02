# Capability vocabulary normalization, mechanical subset (2026-11-02)

**Integrator for this pass:** claude-code. The owner requested this pass in
session on 2026-11-02, and it goes in as a PR.

**Why:** older site and organization rows hold capability values as free text,
such as `injection molding`, `PVC` or `polyethylene`, instead of SCHEMA §3.1–§3.3
terms. Search, the graph explorers and supplier matching only see vocabulary
terms. Before today only about 21% of site `processes` tokens were
in-vocabulary.

## Rule (`build_edits.py`; its docstring holds the full table)

A token is rewritten only when one of these applies:
- **SPELLING:** lowercase, spaces/hyphens → `_` gives a vocabulary term.
  244 tokens, e.g. `injection molding` → `injection_molding`, `PVC` → `pvc`.
- **EQUIV:** it names the same thing as the term. 1,389 tokens, in three kinds:
  - the full name or a standard abbreviation (`polyethylene` / `HDPE` →
    `polyethylene_pe`, `nylon` → `nylon_pa`, `pultrusion` →
    `composites_pultrusion`);
  - a member of the vocabulary's own family bucket (`PTFE` → `fluoropolymers`);
  - a two-sided term, which maps to both (`polyurethane foam` →
    `polyurethane_pu` + `foams_polymeric`).

Ambiguous values are never mapped. For example, `acrylic` (PMMA sheet, or
acrylic adhesives and coatings?) and `extrusion` (profile, pipe, film?) are
left as they are. Unmapped tokens stay verbatim, in-vocabulary tokens are
untouched, and no value is added that the record did not already state.
`mapping_used.csv` lists every mapping used, with token counts.

## Applied

- **Cell edits:** **1,210** over **1,044 records** (sites and organizations) in
  51 files, hash-checked through `scripts/apply_p1_crm_scrub.py --packet-dir`.
- **Tokens mapped:** 1,633.
- **Site tokens now in vocabulary:**
  - `processes` 2,124 of 5,784 (37%);
  - `materials` 3,330 of 6,659 (50%).

  These figures include today's capability passes.
- **V-49 debt:** shrinks by 2. ORG-001484 and ORG-001488 change `automotive` →
  `automotive_unspecified`; the baseline was updated in the same pass.
- **Evidence:** no rows added. Every value restates what the record already
  said, in vocabulary form, which is the same footing as the V-45 synonym fixes
  (battery R1).

## Ruling candidates (`ruling_candidates.csv`: 163 values used ≥5 times)

The biggest are legacy category tags that are not processes (`distribution`
167, `machinery_equipment` 130, `tooling_mold_die` 108, `recycling_recovery` 41,
`service` 30), plus generic or ambiguous terms:
- processes: `extrusion` 71, `compounding` 59, `fabrication` 30, `machining`
  21, `coating` 19, `molding` 19;
- materials: `fiberglass` 61, `plastic`/`plastics` 60, `acrylic` 30,
  `carbon black` 27, `plastic films` 22, `gel coat(s)` 35, `resins` 18.

Each needs an owner choice: map it, move it to notes, or add a term.

## Checks

- **Rehearsal:** on a copy, validate.py passed. The only warning changes were
  the 2 V-49 rows that now pass.
- **Applied tree:** byte-identical to the rehearsal copy. validate.py OK,
  tier1 drift 0, all tests pass.
