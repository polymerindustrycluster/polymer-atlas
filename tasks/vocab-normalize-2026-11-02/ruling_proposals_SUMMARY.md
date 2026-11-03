# Ruling proposals for out-of-vocabulary capability values (2026-11-02)

**Status:** PROPOSAL only. The owner rules (AGENTS.md §2 rule 9). Nothing under
`data/` or `docs/` was touched. Per-value rows: `ruling_proposals.csv`
(same order as `ruling_candidates.csv`).

**Input:** 164 values, 2,061 tokens (the README says 163; the file holds 164).
"Tokens" is the `tokens` column of `ruling_candidates.csv`, which counts more
rows than the site shards alone (site and organization rows). Usage was read
from the site shards joined to organization descriptions; organization rows
were not sampled separately.

## Counts by proposal

| Proposal | Values | Tokens | processes tokens | materials tokens |
|-|-|-|-|-|
| MAP | 59 | 476 | 166 | 310 |
| NEW_UMBRELLA | 32 | 415 | 252 | 163 |
| TO_NOTE | 41 | 391 | 171 | 220 |
| WRONG_FIELD | 16 | 580 | 475 | 105 |
| DROP_NOT_CAPABILITY | 16 | 199 | 48 | 151 |
| **Total** | **164** | **2,061** | **1,112** | **949** |

- **WRONG_FIELD** is two groups. (a) Four Ring 3 subtype labels plus their
  variants go to `ring3_subtype=` (475 process tokens: `distribution` 167,
  `machinery_equipment` 130, `tooling_mold_die` 108, `recycling_recovery` 41,
  and variants). SCHEMA §1 lists these as Ring 3 subtypes, not processes.
  **No CSV column holds a Ring 3 subtype today**, so applying this means
  removing them from `processes` unless the owner adds a column.
  `site_type` already carries most of the signal: `tool_shop` 54 of 54
  `tooling_mold_die` sites, `recycling_facility` 20 of 21 `recycling_recovery`
  sites, `warehouse_distribution` 61 of 109 `distribution` sites.
  (b) Product forms (`film`, `plastic sheet`, `rod`, `tube`, `hoses`, `belts`;
  105 material tokens) go to the §3.6 `product_form` capability terms. That
  layer needs a sourced §4.15 row per claim, so these cannot be moved
  mechanically.
- **TO_NOTE** targets are `processes_other_note` / `materials_other_note`. The
  site shards have no such column today (only `notes`), so the owner also
  decides where the text lands.
- **DROP_NOT_CAPABILITY** covers business functions (`service`, `sales`,
  `headquarters`, `technical service`), metals and substrates (`steel`, `tool
  steel`, `aluminum`, `wood`, `paper`), and generic words that state no family
  (`plastic`, `plastics`, `resin`, `resins`, `polymers`, `specialty polymers`,
  `compounds`). §3.2 allows a record with no family.

## NEW_UMBRELLA terms (the schema-revision asks), by token coverage

| Proposed term | Values | Tokens | Covers | Kind |
|-|-|-|-|-|
| `extrusion_unspecified` | 3 | 86 | extrusion, film extrusion, coextrusion | _unspecified |
| `monomers_intermediates` | 9 | 77 | ethylene, propylene, styrene, formaldehyde, VCM, EDC, MMA, adiponitrile, HMDA | family (scope question) |
| `compounding_unspecified` | 1 | 59 | compounding | _unspecified |
| `fabrication_unspecified` | 3 | 40 | fabrication, custom fabrication, FRP fabrication | _unspecified |
| `polymer_additives` | 5 | 39 | additives, polymer additives, plasticizers, antioxidants, rubber chemicals | family |
| `carbon_black` | 1 | 27 | carbon black | new term; promotes the §3.6 capability term (ruling 7A) |
| `foam_production_unspecified` | 3 | 24 | PU foam pouring / production (one also maps `foam_fabrication`) | _unspecified |
| `molding_unspecified` | 1 | 19 | molding | _unspecified |
| `composites_unspecified` | 1 | 14 | composites | _unspecified |
| `recycling_unspecified` | 2 | 11 | recycling, plastics recycling | _unspecified |
| `rubber_molding_unspecified` | 1 | 7 | rubber molding | _unspecified |
| `thermoplastic_olefin_tpo` | 1 | 6 | TPO | new term; promotes the §3.6 capability term |
| `reaction_injection_molding` | 1 | 6 | reaction injection molding | new term; §3.6 already seeds it |

Thirteen terms, 415 tokens. Five are not `_unspecified` umbrellas
(`monomers_intermediates`, `polymer_additives`, `carbon_black`,
`thermoplastic_olefin_tpo`, `reaction_injection_molding`); I filed them here
because the alternative is `TO_NOTE`. If the owner declines any term, the
fallback for its values is `TO_NOTE`. Smallest-regret asks: `extrusion_unspecified`,
`compounding_unspecified`, `carbon_black`, `polymer_additives`. Candidate not
proposed: `reinforcement_fibers` (`glass fiber` 13, `aramid` 9, `reinforcements` 5).

## The 10 hardest calls

1. **`fiberglass` (61) TO_NOTE.** Usually a finished FRP product, but sites such
   as a continuous-filament mat maker and a prepreg maker use it for raw glass
   fiber. 27 sites also carry `polyester_vinyl_ester_resins`. A record-conditional
   MAP to `composites_frp` (only where a polyester or gel-coat token is present)
   would recover most of it.
2. **Ring 3 labels (`distribution`, `machinery_equipment`, `tooling_mold_die`,
   `recycling_recovery`; 446 tokens plus variants) as WRONG_FIELD.** Alternative
   for `tooling_mold_die`: MAP to `mold_tool_making`. I did not, because at least
   one `tool_shop` site (a molder) and one investment-casting die shop are not
   plastics mold makers. Without a subtype column, WRONG_FIELD means loss.
3. **`extrusion` / `film extrusion` / `coextrusion` to one umbrella (86).** Film
   nuance is lost. The owner may want `extrusion_film_unspecified` as well.
4. **`acrylic` (30) TO_NOTE.** 20 of 22 sampled sites use it for PMMA shells or sheet
   (bath, spa, distributor), but acrylic adhesives appear too. Conditional MAP to
   `acrylic_pmma` where no adhesive or coating token is present.
5. **`converting`, `slitting`, `die cutting` to `die_cutting_converting` (34).**
   The term name carries "converting", but flexible-packaging bag converters are
   a stretch. Alternative: a `converting_unspecified` umbrella.
6. **`fabrication` family to `fabrication_unspecified` (40).** Most uses are
   plastic-sheet distributor-fabricators, where `plastics_fabrication_welding`
   would be right. Foam, FRP and vinyl-window uses stop me from mapping.
7. **`coating` (19) MAP to `coating_applying`.** Every sampled site is a web or
   film coater, but three of 18 sites were not read. Weakest MAP in the set.
8. **Generic material words dropped (`plastic`, `plastics`, `resin`, `resins`;
   87 tokens, plus `polymers`, `specialty polymers`, `compounds`).** DROP is my
   choice because §3.2 allows a record with no family. The cautious alternative
   is TO_NOTE, which would only store words that carry no information.
9. **`monomers_intermediates` (77 tokens, 9 values).** The question is scope:
   §3.2 lists polymers, so does `materials[]` hold monomers? If not, these become
   TO_NOTE and `caustic soda`/`chlorine`/`pyrolysis oil` are already there.
10. **Gel coat family (`gel coat`, `gel coats`, `gelcoat`, `gelcoats`; 45 tokens)
    MAP to `coatings`**, with `gel coat production` to `coating_formulation`.
    Defensible but coarse. I did not add `polyester_vinyl_ester_resins`, because
    the source does not claim the resin. Honorable mention: `vinyl` to `pvc`
    (8 tokens, lower confidence).

## Checks run

- 164 input rows, 164 output rows, same order, no key missing or extra.
- Every `MAP` target term parsed from SCHEMA §3.1-§3.4 (v1.7.6 additions
  included); none outside the vocabulary.
- Every rationale is 25 words or fewer.
- Not checked: organization rows beyond joined descriptions, and whether
  `validate.py` would accept any of the proposed `TO_NOTE` destinations (no such
  column exists on site shards).
