# Owner battery: 2026-11-03

Every item needs the owner's ruling (AGENTS.md §2 rule 9). Each item has a recommendation, marked (a), and its
evidence. Nothing these items gate has been applied.

## B-CAMP: campaign mode after CI (AGENTS.md §2 rule 2)
Rule 2 exists because PRs ran no automated validation. Since 2026-11-02, `validate` runs on every PR and push
(QUEUE.md), so rule 2 says it is "revisited by dated revision".
- **(a) Recommended:** retire direct pushes to `main` for every harness, the orchestrator included. Every change goes
  through a PR that must pass `validate`, and the per-pass journal and pre-pass backups stay. AGENTS.md gets a dated
  revision.
- (b) Keep campaign mode, and add a passing `validate` run as a fifth condition.
- (c) No change yet.

## B-BAND: evidence `claim_type` for employee-size bands (SCHEMA §4.13)
1,996 band values carry their source and date only in `BAND-SOURCE:` notes (QUEUE.md).
- **(a) Recommended:** add `claim_type = size_band`, with source classes `government_filing` (OSHA ITA or inspection,
  Form 5500) and `own_site`, and a ceiling of `supports_B`. Then backfill one evidence row per band from
  `tasks/integration-ready-oh-pa-2026-11-02/band_updates.csv`.
- (b) Add the claim type, but do not backfill.
- (c) Keep the notes only.

## B-VOC: 164 out-of-vocabulary capability values
The proposals are in `tasks/vocab-normalize-2026-11-02/ruling_proposals.csv`, one row per value, with the summary and
the 10 hardest calls in `ruling_proposals_SUMMARY.md`. Unit: values (tokens). In total there are 164 values covering
2,061 tokens, counted over site and organization rows.

| Proposal | Values | Tokens |
|-|-:|-:|
| MAP to an existing term | 59 | 476 |
| NEW_UMBRELLA (schema revision) | 32 | 415 |
| TO_NOTE | 41 | 391 |
| WRONG_FIELD | 16 | 580 |
| DROP_NOT_CAPABILITY | 16 | 199 |

- **B-VOC-1, the 59 MAP rows.**
  - **(a) Recommended:** apply all 59.
  - (b) Apply all except the two weakest, `coating` → `coating_applying` and the gel-coat family → `coatings`.
  - (c) Hold.
- **B-VOC-2, the 13 new terms.**
  - **(a) Recommended:** add a dated SCHEMA revision with 12 of the terms:
    - eight `_unspecified` umbrellas: extrusion, compounding, fabrication, foam_production, molding, composites,
      recycling and rubber_molding;
    - `carbon_black`, `polymer_additives`, `thermoplastic_olefin_tpo` and `reaction_injection_molding`. The last
      three promote §3.6 capability terms, and `polymer_additives` is a family the vocabulary lacks.
    - `monomers_intermediates` (77 tokens) is held. It is a scope question (does `materials[]` hold monomers?), and
      until it is ruled its values go TO_NOTE.
  - (b) Add only the four smallest-regret terms: `extrusion_unspecified`, `compounding_unspecified`, `carbon_black`
    and `polymer_additives`. Everything else goes TO_NOTE.
  - (c) Add none.
- **B-VOC-3, TO_NOTE and DROP.**
  - **(a) Recommended:**
    - add to the site shards the `processes_other_note` column that SCHEMA §3 already names, plus a matching
      `materials_other_note` (a new name, part of this revision);
    - move the 41 TO_NOTE values' text there;
    - drop the 16 DROP values. These are business functions (`sales`, `headquarters`), metals and substrates, and
      generic words (`plastic`, `resin`) that state no family; §3.2 allows a record with no family.
  - (b) Append the TO_NOTE text to `notes` instead.
  - (c) Hold both.
- **B-VOC-4, the four Ring 3 labels.** These are `distribution`, `machinery_equipment`, `tooling_mold_die` and
  `recycling_recovery`, with 446 tokens plus variants. SCHEMA §1 lists them as Ring 3 subtypes, not processes, but no
  column holds a Ring 3 subtype. `site_type` already carries most of the signal: `tool_shop` on 54 of 54 sites,
  `recycling_facility` on 20 of 21, and `warehouse_distribution` on 61 of 109.
  - **(a) Recommended:** leave them as they are for now. Revisit with a dated column revision, because removing them
    loses the signal.
  - (b) Add a `ring3_subtype` column, then move them.
  - (c) Drop them from `processes`.

## People-gate questions from the census-gap follow-up wave (`tasks/census-gap-2-2026-11-03/`)
- **B-CG-1. Berkeley "Professor of the Graduate School"** (Susan J. Muller; Gate B met). Berkeley's own faculty
  retirement policy says retiring faculty "may be honored with the title of Professor of the Graduate School"
  (https://ofew.berkeley.edu/sites/default/files/temp_retirement_policy_all_2021.pdf). It is a post-retirement title.
  - **(a) Recommended:** it is outside Gate A, the same as emeritus stylings (SCHEMA §4.9).
  - (b) It counts as `professor`.
- **B-CG-2. Biopolymers as the Gate B object.** The cases are Danielle Mai (Stanford), whose stated object is
  biopolymers, and Sara Molinari (UMD), who names a biopolymer matrix as a component of engineered living materials.
  The precedent is Palmer: polymerized-protein therapeutics pass.
  - **(a) Recommended:** pass when the person's stated research engineers a biopolymer as a material (Mai). Fail when
    the biopolymer is only a component of a non-polymer research object (Molinari).
  - (b) Pass both.
  - (c) Fail both. Biological polymers are out of scope unless they are synthetic or processed polymer materials.
