# Polymer / Plastics / Rubber Industry Database — Taxonomy & Record Schema

**Owner:** Polymer Industry Cluster (PIC), Greater Akron Chamber — Director of Innovation Portfolio
**Version:** v1.3 — 2026-10-29 (the v1.3 increment to the combined v1.2 revision:
§4.6 drift fix, institutional identifiers, and the programs table; owner directed
the increment 2026-10-29 per the schema-v1.3 note reconciliation; applied
2026-10-29 in the schema v1.3 micro-pass, against the post-network-application repo)
**Status:** This document defines classification and record structure. It does not contain the company list.
**Change basis:** v1.1 (decision memo 2026-10-29 §1, option (a): Tier 1 + Tier 2) and v1.2
(repo change proposals S1–S4, 2026-10-29) adopted together as one dated revision. New or
changed text in this revision is marked **[v1.1]** / **[v1.2]** at the paragraph or row level.
The v1.3 increment's text is marked **[v1.3]** the same way.
Sections without a mark are carried from v1.0 unchanged.
**Scope:** Northeast Ohio primary; Ohio statewide secondary; national for parents, OEMs, and ecosystem entities with an Ohio footprint or direct PIC relevance.

**How to use this document:** A researcher classifying a new entity should be able to (1) assign a Ring in <2 minutes using §1, (2) assign NAICS + provenance using §2, (3) tag processes/materials/markets from the controlled vocabularies in §3 only — no free-text inventions, and (4) create a record that dedupes identically to another researcher's record using §5.

---

## 1. Ring Model — Concentric Inclusion

Rings are about *polymer relevance and PIC actionability*, not company size or prestige. An entity gets **exactly one primary Ring** at the Parent level and may get a different Ring at an individual Establishment level (see §5.3). Never assign two primary Rings to the same record; use `secondary_ring` for the second-best fit.

| Ring | Short name | One-line test |
|---|---|---|
| **1** | Core Producers & Processors | Makes a polymer, or shapes polymer/rubber into a product/component as its primary activity at that site |
| **2** | Materials, Compounding & Formulated Polymers | Creates the formulation — resin, compound, masterbatch, coating, adhesive, sealant, ink — that someone else shapes or applies |
| **3** | Value Chain | Enables production without being the material or the final shaper: tooling, machinery, automation, distribution, recycling, testing/R&D services |
| **4** | Downstream OEMs & Heavy Polymer Users | Buys polymer in volume and its product performance, cost, or compliance materially depends on polymer choice — but polymer is not its sold product identity |
| **5** | Ecosystem | Does not buy/sell/make polymer commercially, but shapes talent, capital, knowledge, standards, or convening for those who do |

### Ring 1 — Core Producers & Processors

**Definition:** Establishments whose primary output is (a) a polymer resin/material sold as material, or (b) a shaped solid/foam/film/rubber article where polymer/rubber is the dominant material by value or function. Includes plastics processors, rubber goods manufacturers, tire manufacturers, foamers, film/sheet, pipe/profile, composites fabricators where resin+fiber is the product.

**Inclusion rule (<2 min):**
1. Does the site physically transform resin/rubber/compound — melt, mix, cure, vulcanize, polymerize, foam, lay up — on site? If YES → Ring 1.
2. OR is the company's headline product (website hero / directory listing) itself made of plastic/rubber? If YES → Ring 1.
Either YES is sufficient. No employee minimum.

**Exclusion rule:** No physical transformation on site and polymer is only packaging, office use, or a purchased sub-component assembled with metal/electronics → not Ring 1; test for Ring 4. Outsourced molding with only design/sales at the Ohio site → record the Ohio site as Ring 3 (sales/design) or Ring 4, and note the contract manufacturer separately if known.

**Examples in:** Injection molder, blow molder, extruder, thermoformer, tire plant, rubber mixer/molder, foam fabricator, plastics fabricator/machinist, production polymer 3D-printing bureau (see edge cases), composites molder.

### Ring 2 — Materials, Compounding & Formulated Polymers

**Definition:** Producers of formulated polymer-containing materials sold by chemistry/performance, not by final shape: custom compounders, color/masterbatch, resin producers not captured cleanly in Ring 1 polymerization, elastomer compounders, and — by deliberate PIC decision — paints/coatings, adhesives, sealants, caulks, inks, and rubber chemicals/additives where polymer/resin is the functional binder.

**Inclusion rule (<2 min):**
1. Does it sell a material whose data sheet lists a polymer/resin/elastomer as the primary functional ingredient? If YES → Ring 2.
2. OR does it compound, blend, polymerize, disperse, or formulate to a customer specification (toll or proprietary)? If YES → Ring 2.
A company that *both* compounds and molds: Ring 2 at Parent if compounding is the marketed identity, Ring 1 at the molding Establishment(s). Pick one primary; record the other in `secondary_ring`.

**Exclusion rule:** Sells commodity chemicals, solvents, pigments, fillers, or equipment with no polymer-specific formulation → not Ring 2; test Ring 3 if it predominantly serves polymer customers (≥50% polymer-industry revenue/customer claim), otherwise exclude. Retail paint stores, hardware stores → exclude (they are establishments of a Ring 2 parent, not separate records).

**Boundary with Ring 1:** Polymerization of resin = Ring 1 in NAICS terms (325211) but Ring 2 in PIC logic when sold as material. **Ruling:** Standalone resin plants are coded **Ring 1, `subtype=resin_production`** for NAICS fidelity, and are *also* discoverable via a Ring 2 search filter (`materials_producer=true`). This is the single intentional cross-ring filter in the system — it prevents double-counting while preserving both views. All other compounders/formulators are Ring 2 primary.

### Ring 3 — Value Chain

**Definition:** For-profit suppliers and service firms whose customers are predominantly Ring 1/2/4 firms and whose offer is specific to polymer production or polymer product lifecycle.

Subtypes (required field, pick one): `tooling_mold_die` | `machinery_equipment` | `automation_robotics` | `distribution` | `recycling_recovery` | `testing_lab` | `rd_design_engineering` | `contract_services` (assembly, decorating, secondary ops, warehousing for polymer firms) | `chemical_equipment_supply_polymer_specific`.

**Inclusion rule (<2 min):**
1. Would ≥50% of its customers plausibly be polymer/plastics/rubber firms, OR does it explicitly market to plastics/rubber on its website/directory listing? If YES → Ring 3.
2. AND it performs the service itself in Ohio (stocking distributor warehouse counts; a manufacturer's rep with no stock/staff beyond 1 remote rep does *not* — record as Parent-only, `ohio_presence=rep_only`).
General machine shops, general engineering firms, general labs: include ONLY if they claim a plastics/rubber specialty, hold a polymer-relevant certification (e.g., ISO for medical molding support), or appear in a polymer directory (Plastics News, Rubber News, Thomas polymer category). Otherwise exclude to keep Ring 3 from swallowing all of Ohio manufacturing.

**Exclusion rule:** General logistics, staffing, accounting, IT, real estate, utilities → exclude even if they have polymer clients, unless they have a named, dedicated plastics vertical (then Ring 3, `subtype=contract_services`, tag `dedicated_vertical`).

### Ring 4 — Downstream OEMs & Heavy Polymer Users

**Definition:** End-product manufacturers and brand owners in automotive, medical device, construction/building products, packaging *users* (food, consumer goods fillers), appliances, aerospace, agriculture, and consumer products, where polymer is not the sold identity but is a major input.

**Polymer-Relevance Test — inclusion requires 2 of 3 (record which two in `ring4_test`):**
- **A. Volume/Value:** Polymer parts/materials are ≥15% of bill of materials by cost, OR the site operates captive molding/extrusion/thermoforming, OR it employs dedicated plastics engineers/buyers.
- **B. Performance:** Product function, safety, regulatory clearance, or failure mode materially depends on polymer selection (e.g., fluid contact, sealing, insulation, sterile barrier, structural composite, tire/road contact via purchased components does *not* count alone).
- **C. Decision locality:** Polymer/material or supplier decisions are made, specified, or tested at the Ohio site (not purely purchased as finished assemblies specified elsewhere).
Need A+B, A+C, or B+C. One alone = `watchlist`, not a full Ring 4 record.

**Inclusion rule (<2 min):** Apply the 2-of-3 test from website, job postings, patents, captive-process evidence, or directory description. If evidence is not findable in 2 minutes, code `verification_tier=U`, `ring=4`, `status_candidate=needs_test` — do not spend 20 minutes proving it in v1 sweep.

**Exclusion rule:** Any manufacturer that merely *uses* plastic packaging, plastic pallets, office plastics, or buys finished plastic components off-the-shelf with no specification role → exclude. Retailers, hospitals, construction contractors (installers, not manufacturers) → exclude; their suppliers may qualify.

### Ring 5 — Ecosystem

**Definition:** Non-commercial or mission entities that support the polymer industry as a system.

Subtypes (required): `university_college` | `k12_cte_workforce` | `trade_association` | `nonprofit_rd_consortium` | `economic_development` | `workforce_training_provider` | `accelerator_incubator` | `funder_capital` | `government_lab_agency` | `standards_body` | `museum_education_outreach`.

**Inclusion rule (<2 min):**
1. Does it have a named polymer/plastics/rubber program, center, curriculum, membership, fund, or service — not just a generic chemistry/manufacturing offer? If YES → Ring 5.
2. OR is it a general economic-development / workforce org for a geography in scope (county/state EDO, Ohio MEP, etc.)? If YES → Ring 5, tag `generalist=true`.
Generic universities with only a standard chemistry degree and no polymer program/center/faculty cluster → Parent record in Ring 5 with `polymer_program=false` only if in NE Ohio; otherwise exclude. National associations with no Ohio chapter still included at Parent level if Ohio firms are members (e.g., SPE, ACS Rubber Division, Plastics Industry Association).

**Exclusion rule:** Individual consultants, individual professors (record under their institution), for-profit training sold as a product with no cohort/workforce mission (→ Ring 3 `rd_design_engineering` if polymer-specific), and general chambers of commerce with no polymer/manufacturing focus except PIC's host and direct partners (tag those `partner`).

### Edge Cases — Decided (binding precedent for researchers)

| Entity / type | Ruling | Reasoning a researcher should cite |
|---|---|---|
| **Sherwin-Williams** (Cleveland HQ; paints/coatings) | **INCLUDE — Ring 2 Parent.** Establishments: HQ + R&D + manufacturing plants = Ring 2; retail stores = DO NOT create establishments. | Coatings are formulated polymers (resin binder is the functional ingredient). Passes Ring 2 test 1. Retail exclusion prevents ~4,000 store records from drowning the database. Tag: `materials=[coatings]`, `pic_relevance=potential_member, anchor`. |
| **Parker Hannifin** (Mayfield Heights HQ; diversified motion/control) | **INCLUDE, SPLIT — Parent = Ring 4 `diversified_conglomerate=true`; polymer divisions/plants = Ring 1/3 establishments under that Parent.** Engineered Materials / sealing & hose sites that mold/mix rubber/polymer = Ring 1 establishments. Filtration, hydraulics metal sites = no establishment record unless they pass Ring 4 test at site level. | Whole-company inclusion as Ring 1 would misstate it; whole-company exclusion would lose one of NE Ohio's largest polymer-component producers. Parent-vs-site split (§5) exists for exactly this case. Never count Parent headcount as polymer headcount — use site band only. |
| **STERIS** (Mentor; sterilization, infection prevention) | **WATCHLIST — Ring 4 candidate, NOT a full record in v1 unless a specific Ohio site manufactures polymer consumables in-house.** Corporate HQ alone does not pass. | Primary product is sterilization equipment/services and sterile processing; polymer consumables are important but specification/manufacturing evidence for Ohio sites is not headline-evident. Fails Ring 4 test on publicly quick evidence (needs B+C verified). Re-test if a consumables plant is identified — that plant would be Ring 1/4. Tagging it Ring 1/2 would be half-assed inclusion by brand familiarity. |
| **GOJO** (Akron; skin health, PURELL) | **EXCLUDE from Rings 1–4 as Parent; INCLUDE a single Establishment ONLY if in-house dispenser molding/assembly at that site is verified.** Tag the Parent note in exclusion log. | Core chemistry is soap/sanitizer (NAICS 325611), not polymer formulation — binder test fails. Dispensers are polymer-heavy, but if molding is outsourced, GOJO is a packaging/component buyer, not a processor. This is the template ruling for soap/cosmetics/food firms with plastic dispensers/packaging: packaging alone ≠ inclusion. |
| **Tire retreader** (independent retread shop / franchised retreader) | **INCLUDE — Ring 1, `subtype=retread`, if it cures/bonds new tread on site; Ring 3 `contract_services` if it only inspects/mounts and sends curing elsewhere.** Franchise location = Establishment under franchisor Parent; independent = its own Parent. | Retreading physically transforms rubber (buffing, cementing, curing/vulcanizing) — passes Ring 1 transformation test. It is manufacturing, not retail tire sales. Pure tire dealers/installers with no curing → exclude. |
| **3D-printing / additive service bureau** | **INCLUDE — Ring 1 if ≥50% polymer work or it offers production/end-use polymer parts; Ring 3 `rd_design_engineering` if prototyping-only / mostly metal / design-only.** No size floor. | Polymer AM is a shaping process (§3). A 3-person production bureau is more PIC-relevant than a large general machine shop. Record `processes=[additive_manufacturing_polymer]` and material tags per printer fleet if known. Pure reseller of printers → Ring 3 `machinery_equipment`. |
| **Distributor with no manufacturing** | **INCLUDE — Ring 3, `subtype=distribution`.** Stocking Ohio warehouse = Establishment; sales-office-only = Parent record with `ohio_presence=sales_office`. | Distribution is explicitly Ring 3. No-manufacturing is not a disqualifier. Must be polymer-material/equipment specific (resin, sheet, rubber, compounding inputs) — general industrial distributors (Grainger-type) excluded unless they have a dedicated plastics division/warehouse category. |
| **GOJO / soap-type near-miss (general rule)** | See GOJO above. | Apply to cosmetics, cleaning chemicals, pharma fillers: need captive polymer process or Ring 4 2-of-3. |
| **Bridgestone / Goodyear-type tire OEMs** | Ring 1 Parent + every Ohio R&D/manufacturing Establishment as Ring 1. Global HQs outside Ohio still get Parent records if Ohio footprint is major; flag `hq_outside_ohio=true`. | Tire is core rubber. R&D centers count as Establishments with `site_type=rd_center`, not Ring 5. |
| **Household-name diversified: Eaton, Timken, Lincoln Electric, Moen/fortune brands, Diebold Nixdorf** | Do NOT auto-include. Apply site-level Ring 4 test individually. Moen-type (plastics in faucets, captive molding historically) likely passes A+B; electrical/metal-dominant firms often fail B/C at Ohio sites. Default when unsure: `watchlist`. | Familiarity and size are not inclusion criteria. The test, not the brand, decides. |
| **Waste hauler that also runs a plastics MRF / reclaimer** | Hauling-only sites = exclude. MRF/reprocessing site = Ring 3 `recycling_recovery` Establishment (Ring 1 if it pelletizes/washes to saleable flake/pellet — then `secondary_ring=3`). | Function at the site decides, not the parent's SIC. |
| **University spinout / startup with no plant yet** | Include as Parent, Ring by intended process (usually 1 or 2), `status=pre_revenue` / `site_type=hq_virtual`, address = incubator/lab if that is its real base. | PIC's prospect pipeline needs pre-plant startups. Virtual/HQ-only is a valid Establishment type; do not invent a plant address. |

---

## 2. NAICS Map

### 2.1 Critical provenance rule — read first

**Companies almost never publish their own corporate 6-digit NAICS.** The code on a profile was almost always assigned by a directory, a data vendor, SBA/IRS filing logic, or a prior researcher. Treating a directory NAICS as a company fact was the known failure mode in John's 2026-10-01 prototype.

Therefore every NAICS value MUST carry provenance (see schema §4):

```
naics_primary: "326199"
naics_primary_source_type: directory_assigned | company_disclosed | government_filing | researcher_inferred
naics_primary_source_name: "Plastics News" | "D&B" | "Thomasnet" | "SAM.gov" | ...
naics_primary_confidence: high | medium | low
naics_secondary: ["325991", ...]   # each with same provenance fields in naics_secondary_detail[]
```

Rules:
- `company_disclosed` only if the company itself states it (capabilities statement, SAM.gov registration by the company, 10-K). A vendor repeating it is still `directory_assigned`.
- `researcher_inferred` is allowed and expected in v1 — infer from primary process/product, set confidence honestly, and never upgrade it to `directory_assigned` later without a source.
- If two directories disagree, keep the process-consistent code as primary, list the other as secondary, set confidence = `medium`, add a note. Do not average or pick the more prestigious directory.
- NAICS is a **signal for discovery and filtering, never the Ring decision alone**. Ring (§1 tests) outranks NAICS. A 326199 firm can be Ring 4 at Parent level; a 332710 machine shop can be Ring 1 at a plastics-only site.

**Signal strength key:** **P** = Primary signal — code alone justifies pulling the firm into the candidate queue. **S** = Secondary signal — code alone is NOT sufficient; needs the §1 test / polymer-specialty evidence. **X** = Exclude-by-default — pull only with explicit polymer evidence; these codes generate mostly noise.

### 2.2 Codes by Ring

#### Ring 1 — Core

| NAICS | Title (short) | Signal |
|---|---|---|
| 326111 | Plastics Bag & Pouch Mfg | P |
| 326112 | Plastics Packaging Film & Sheet | P |
| 326113 | Unlaminated Plastics Film & Sheet | P |
| 326121 | Unlaminated Plastics Profile Shape Mfg | P |
| 326122 | Plastics Pipe & Pipe Fitting Mfg | P |
| 326130 | Laminated Plastics Plate/Sheet/Shape | P |
| 326140 | Polystyrene Foam Product Mfg | P |
| 326150 | Urethane & Other Foam (ex. Polystyrene) | P |
| 326160 | Plastics Bottle Mfg | P |
| 326191 | Plastics Plumbing Fixture Mfg | P |
| 326192 | Resilient Floor Covering Mfg | P |
| 326199 | All Other Plastics Product Mfg — *largest bucket; includes composites, custom molding* | P |
| 326211 | Tire Mfg (except Retreading) | P |
| 326212 | Tire Retreading | P |
| 326220 | Rubber & Plastics Hoses & Belting Mfg | P |
| 326291 | Rubber Product Mfg for Mechanical Use | P |
| 326299 | All Other Rubber Product Mfg | P |
| 325211 | Plastics Material & Resin Mfg *(Ring 1 subtype resin_production; filterable as Ring 2 — see §1)* | P |
| 313320 | Fabric Coating Mills *(rubber/polymer-coated textiles)* | S |

#### Ring 2 — Materials & Formulated Polymers

| NAICS | Title | Signal |
|---|---|---|
| 325211 | Plastics Material & Resin Mfg *(cross-listed; see above)* | P |
| 325212 | Synthetic Rubber Mfg | P |
| 325991 | Custom Compounding of Purchased Resins | P |
| 325510 | Paint & Coating Mfg | P* |
| 325520 | Adhesive Mfg *(incl. sealants/caulks in practice)* | P |
| 325130 | Synthetic Dye & Pigment Mfg *(only masterbatch/colorant producers for polymers)* | S |
| 325199 | All Other Basic Organic Chemical Mfg *(monomers, polymer intermediates)* | S |
| 325220 | Artificial & Synthetic Fibers & Filaments Mfg | S |
| 325920 | Explosives Mfg | X — exclude unless polymer binder evidence |
| 325998 | All Other Misc. Chemical Product Mfg *(release agents, polymer additives, specialty)* | S |
| 325611 | Soap & Other Detergent Mfg *(GOJO-type)* | X — NOT a Ring 2 signal; see edge case |
| 325612 | Polish & Other Sanitation Goods Mfg | X |
| 424690 / 424610 detail | See Ring 3 for distribution codes | — |

\* 325510 is Primary for *manufacturers*, but every retail/dealer record with this code is excluded per Sherwin-Williams ruling.

#### Ring 3 — Value Chain

| NAICS | Title | Signal | Subtype |
|---|---|---|---|
| 333511 | Industrial Mold Mfg | P | tooling_mold_die |
| 333514 | Special Die & Tool, Die Set, Jig & Fixture Mfg | S | tooling_mold_die |
| 333249 | Other Industrial Machinery Mfg *(plastics/rubber machinery lives here in 2022 NAICS)* | S | machinery_equipment |
| 333242 | Semiconductor Machinery — **not** plastics machinery | X | — |
| 333519 / 333513 etc. legacy codes | Pre-2022 plastics machinery codes in old directories | S | machinery_equipment — map forward, note legacy code in provenance |
| 332710 | Machine Shops; Turned Product; Screw, Nut & Bolt Mfg *(use 332710 shops only)* | S | tooling / fabrication — requires plastics specialty claim |
| 332322 / 332313 | Sheet Metal / Ornamental — machine builders' subsuppliers | X | — |
| 424610 | Plastics Materials & Basic Shapes Merchant Wholesalers | P | distribution |
| 424690 | Other Chemical & Allied Products Merchant Wholesalers *(resin/compound distribution)* | S | distribution |
| 423830 | Industrial Machinery & Equipment Merchant Wholesalers | S | distribution / machinery |
| 423930 | Recyclable Material Merchant Wholesalers | S | recycling_recovery |
| 562920 | Materials Recovery Facilities | P | recycling_recovery |
| 562219 | Other Nonhazardous Waste Treatment & Disposal *(chemical recycling / pyrolysis often coded here)* | S | recycling_recovery |
| 541380 | Testing Laboratories & Services | S | testing_lab — requires polymer/materials scope |
| 541715 | R&D in Physical, Engineering & Life Sciences *(ex. biotech)* | S | rd_design_engineering |
| 541330 | Engineering Services | S | rd_design_engineering — requires polymer specialty |
| 541420 | Industrial Design Services | S | rd_design_engineering |
| 326199 / 326291 as secondary | When a Ring 1 code appears on a pure service/secondary-ops firm | S | contract_services |

#### Ring 4 — Downstream OEMs / Heavy Users (all Secondary signal — Ring 4 test always required)

| NAICS | Title | Typical polymer relevance |
|---|---|---|
| 336110 / 336120 | Automobile / Light & Heavy Truck Mfg | Interiors, under-hood, EV battery enclosures |
| 336310 / 336320 / 336360 / 336390 | Motor Vehicle Gasoline Engine, Electrical, Seating/Interior Trim, Other Parts | Seating foam, trim, seals, wire harness |
| 336411 / 336412 / 336413 | Aircraft & Parts | Composites, interiors |
| 339112 / 339113 / 339114 / 339115 | Surgical/Medical Instrument, Appliance & Supplies, Dental, Ophthalmic | Molded devices, disposables, housings |
| 334510 / 334511 / 334512 | Electromedical, Search/Detection, Controls | Housings, seals, overmolding |
| 335210 / 335220 / 335240 | Small / Major Appliances, Commercial Equipment | Housings, insulation foam, gaskets |
| 327310 / 327320 / 327330 / 327390 | Cement & Concrete Products | Polymer-modified, formwork, admixture users — S/X borderline |
| 327991 / 327999 | Cut Stone / Misc. Nonmetallic Mineral *(solid-surface, composites-adjacent)* | S |
| 326192 cross-ref | Flooring OEMs already in Ring 1 if they manufacture the polymer product | — |
| 311xxx / 312111 | Food / Soft Drink Mfg *(packaging users)* | X by default — only captive blow/injection or sterile-barrier specifiers pass |
| 325412 / 325413 / 325414 | Pharmaceutical / In-Vitro / Biological | X by default — same packaging rule as GOJO |
| 238xxx | Construction contractors | X — installers excluded per §1 |
| 316210 | Footwear Mfg | S — polymer soles/EVA often Ring 1 at site level |
| 314910 / 314999 | Textile Bag / Misc. Textile | S — coated/laminated textiles |

#### Ring 5 — Ecosystem (all Secondary signal — named polymer program test in §1 applies)

| NAICS / type proxy | Title | Notes |
|---|---|---|
| 611310 | Colleges, Universities & Professional Schools | Polymer programs: UAkron, CWRU, Kent State, etc. |
| 611210 / 611519 | Junior Colleges / Technical & Trade Schools | CTE, apprenticeship, processing certificates |
| 541720 | R&D in Social Sciences / Humanities — **not** polymer R&D | X |
| 813910 | Business Associations | Trade associations (SPE, ACS Rubber Division, OMA, etc.) |
| 813920 | Professional Organizations | S |
| 813312 / 813319 | Environment / Other Social Advocacy & Civic | Only with named polymer/sustainability program |
| 926110 / 926130 | Administration of General / Energy & Resource Programs | Government agencies/labs |
| 522320 / 523930 | Financial / Investment Advice *(funders)* | Only dedicated manufacturing/polymer funds; general banks = exclude |
| 541611 / 541618 | Management / Other Management Consulting *(EDOs, MEPs often coded here or 813)* | Generalist EDOs included per §1 with `generalist=true` |

#### Composites-adjacent — handle with care

Composites straddle NAICS. Do NOT create a separate ring. Tag `materials` includes `composites_frp` / `composites_carbon` / `composites_thermoset` and search across:
- **326199 / 326130** (P) — most FRP molders land here.
- **327215** Glass Product Mfg Made of Purchased Glass (S), **327999** (S), **325220** fibers (S), **336411/336413** aerospace composites (S, Ring 4 test), **333611 / 336612** wind/boat (S). A fiberglass *raw material* producer = Ring 2; a fiberglass *part* molder = Ring 1; a boat/aircraft OEM using composites = Ring 4.

### 2.3 Discovery implication

Because ~900 Ohio polymer firms is the reported scale, NAICS-only discovery will both over-pull (332710, 541330, 325510 retail noise) and under-pull (firms mis-coded to a parent's NAICS, startups with no directory record). The sweep plan must therefore pair NAICS pulls with directory pulls (Plastics News, Rubber News, Thomasnet, Ohio Manufacturers' Association, county EDO lists) and process-keyword pulls — NAICS is the dedupe/filter layer, not the sole source. Record the discovery source in `sources[]` on every record so coverage can be audited by source.

---

## 3. Process / Capability Taxonomy — Controlled Vocabularies

**Rules:** Use ONLY terms below. If a real process does not fit, set `processes_other_note` (free text, reviewed monthly for vocabulary additions) — do not invent a new tag inline. Multiple values allowed everywhere. Suffix `_tolled` / `_captive` only via the separate boolean fields `offers_tolling`, `captive_only`, not by creating variant terms. Case: `snake_case` exactly as written.

### 3.1 Processes (`processes[]`)

**Primary shaping — plastics:**
`injection_molding` · `injection_molding_micro` · `injection_molding_lsr_silicone` · `insert_overmolding` · `two_shot_molding` · `blow_molding_extrusion` · `blow_molding_injection` · `blow_molding_stretch` · `extrusion_film_blown` · `extrusion_film_cast` · `extrusion_sheet` · `extrusion_profile` · `extrusion_pipe_tube` · `extrusion_wire_cable_coating` · `thermoforming_vacuum` · `thermoforming_pressure` · `rotational_molding` · `compression_molding` · `transfer_molding` · `calendering` · `foam_molding_bead` · `foam_molding_structural` · `foam_extrusion` · `foam_fabrication` · `blow_molding` *(legacy umbrella — use only when subtype unknown)*

**Primary shaping — rubber / elastomer:**
`rubber_mixing_compounding` · `rubber_molding_compression` · `rubber_molding_injection` · `rubber_extrusion` · `rubber_calendering` · `tire_manufacturing` · `tire_retreading` · `latex_dipping_foaming` · `hose_belting_manufacturing` · `vulcanization_curing_services`

**Materials production / formulation:**
`polymerization` · `compounding_extrusion` · `custom_compounding` · `color_masterbatch` · `pulverizing_grinding_resin` · `coating_formulation` · `adhesive_sealant_formulation` · `ink_formulation` · `silicone_formulation`

**Composites:**
`composites_hand_layup` · `composites_rtm_infusion` · `composites_pultrusion` · `composites_filament_winding` · `composites_compression_smc_bmc` · `composites_prepreg_autoclave`

**Additive:**
`additive_manufacturing_polymer` · `additive_manufacturing_polymer_production` *(end-use; implies Ring 1 candidacy)* · `additive_manufacturing_metal` *(record only as secondary capability)*

**Secondary / finishing / other:**
`plastics_machining_cnc` · `plastics_fabrication_welding` · `die_cutting_converting` · `laminating` · `coating_applying` *(contrast: `coating_formulation` = makes it)* · `printing_decorating_plastics` · `assembly_secondary_ops` · `ultrasonic_solvent_bonding` · `recycling_mechanical` · `recycling_chemical_pyrolysis` · `recycling_chemical_solvolysis` · `regrind_pelletizing` · `mold_tool_making` · `tooling_repair_maintenance`

### 3.2 Materials (`materials[]`)

**Families (always tag at least one family if known):**
`thermoplastics` · `thermosets` · `elastomers_rubber` · `thermoplastic_elastomers_tpe_tpu` · `silicones` · `fluoropolymers` · `bioplastics_biobased` · `recycled_content_pcr_pir` · `composites_frp` · `composites_carbon` · `composites_thermoset` · `composites_thermoplastic` · `foams_polymeric` · `films_flexible_packaging` · `coatings` · `adhesives_sealants` · `inks_colorants_masterbatch`

**Specific resins/compounds (tag when explicitly claimed — do not infer from family):**
`abs` · `polyethylene_pe` · `polypropylene_pp` · `pvc` · `pet_petg` · `polystyrene_ps_hips` · `polycarbonate_pc` · `nylon_pa` · `acetal_pom` · `peek_high_performance` · `epoxy` · `polyurethane_pu` · `phenolic` · `melamine_urea_formaldehyde` · `natural_rubber_nr` · `sbr` · `epdm` · `nitrile_nbr` · `neoprene_cr` · `viton_fkm` · `pla` · `pha` · `other_specified_in_notes`

### 3.3 Markets Served (`markets_served[]`)

`automotive_oem` · `automotive_aftermarket` · `aerospace_defense` · `medical_device` · `pharmaceutical_biotech` · `dental` · `construction_building_products` · `infrastructure_civil` · `packaging_consumer` · `packaging_industrial` · `packaging_food_beverage` · `consumer_goods_housewares` · `appliances` · `electronics_electrical` · `industrial_machinery` · `agriculture` · `marine` · `rail_transportation` · `energy_oil_gas` · `energy_renewables_battery` · `water_wastewater` · `lawn_garden_recreation` · `toys_sporting_goods` · `footwear_apparel` · `furniture_office` · `general_industrial` · `other_specified_in_notes`

### 3.4 Certifications / capabilities (nice-to-have controlled list, `certifications[]`)

`iso_9001` · `iso_14001` · `iatf_16949` · `iso_13485` · `as9100` · `fda_registered` · `cleanroom_iso7` · `cleanroom_iso8` · `itar` · `ul_recognized` · `nsf_certified_products` · `glp_gmp` — plus booleans: `offers_tolling` · `captive_only` · `exporter` · `woman_minority_veteran_owned` *(only when self-disclosed by a primary/authoritative source; never inferred from name/photo)*.

---

### 3.5 Research areas — supplement for program / office / people records **[v1.2]**

**§3-first rule (binding on taggers):** use a §3.1/§3.2 term wherever it honestly fits;
a supplement term is used only when no §3 term states the specialty. The supplement is
not a parallel system. It applies to `research_areas[]` on program, office, and people
records (§4.6, §4.9); company records do not use it. Source: Phase A program schema
draft (2026-10-29), adopted with this revision. Calibration finding carried with the
vocabulary: `characterization_methods` is load-bearing — characterization facilities
(electron microscopy / analytical) have no §3.1 process term, and this term is the
only honest tag for them.

| Term | Definition |
|---|---|
| `polymer_physics` | Structure–property relations, thermodynamics, and statistical mechanics of polymer systems |
| `rheology` | Flow and deformation behavior of polymer melts, solutions, and soft solids |
| `polymer_synthesis` | Design and execution of polymerization reactions and polymer architectures |
| `degradation_biodegradation` | Environmental, thermal, and biological breakdown of polymers and its measurement |
| `recycling_circularity` | Mechanical/chemical recycling science, design-for-recycling, and circular material systems |
| `composites_mechanics` | Mechanics, damage, and durability of polymer-matrix composite materials |
| `membranes_separations` | Polymer membranes and barrier/separation science |
| `biomedical_polymers` | Polymers for medical devices, drug delivery, and tissue engineering |
| `additive_manufacturing_science` | Materials and process science of polymer additive manufacturing (beyond operating the process) |
| `characterization_methods` | Development or expert application of analytical methods for polymer structure/properties |
| `sustainable_feedstocks` | Bio-based, waste-derived, or low-carbon feedstocks for polymer production |
| `elastomer_science` | Rubber elasticity, vulcanization chemistry, and elastomer network science |

§3-first examples: a processing professor is tagged `injection_molding` (§3.1), not a
supplement term; a coatings formulator is `coating_formulation` (§3.1) +
`adhesives_sealants` (§3.2); biodegradation research takes
`degradation_biodegradation` because no §3 term states it.

---

## 4. Record Schema

### 4.1 Verification tiers (applies per-record; per-field source in `field_sources`)

| Tier | Meaning | Minimum evidence |
|---|---|---|
| **A** | Primary source | Company website (own domain), SEC/10-K, SAM.gov / Ohio SOS filing, company-issued capabilities statement, direct company confirmation |
| **B** | Authoritative directory | Plastics News, Rubber News, Thomasnet (verified listing), D&B, state/county EDO directory, trade-association member directory, university/center official page |
| **C** | Single secondary | Local news, LinkedIn company page alone, Google Business Profile alone, job posting, single aggregator (ZoomInfo-type) with no corroboration |
| **U** | Unverified / candidate | Inferred NAICS only, scraped list with no profile page, Ring 4 test not yet passed, address unconfirmed |

Promotion rule: C → B requires a second independent source or one B source. B → A requires a primary source for at least legal name + address + primary activity. A record's tier = the tier of its *weakest must-have field* — a glossy website does not make an unconfirmed plant address Tier A.

### 4.2 Status vocabulary (`status`)

`active` · `active_idled_partial` *(site operating below normal / one line down)* · `idled` *(mothballed, not closed, per a dated source)* · `closed` · `acquired` *(use with `successor_org_id`)* · `merged` · `relocated_in_scope` · `relocated_out_of_scope` · `pre_revenue` · `unknown` — Every non-`active` status REQUIRES `status_date` and `status_source`. Never delete a closed/acquired record; tombstone it (see §5.5).

### 4.3 PIC relevance (`pic_relevance[]` + `pic_relationship`)

Tags (multi-select): `current_member` · `former_member` · `potential_member` · `prospect_active_outreach` · `partner` · `sponsor_funder` · `customer_of_members` · `supplier_to_members` · `workforce_pipeline` · `research_partner` · `watchlist` · `not_a_fit` · `do_not_contact`
Plus single-select `pic_relationship_stage`: `uncontacted` | `identified` | `engaged` | `member_partner` | `lapsed` | `excluded`.
**[v1.2] `pic_relationship_stage` is RETIRED from the public files at this revision.** It is
relationship data, not public data: the column is removed from `organizations.csv` at
application, its values are archived in staging (never deleted), and no public file may
carry it again. `pic_relevance[]` tags and `pic_relevance_note` are unaffected. Membership
*status* is a separate, public fact governed by §4.10 — it is not relationship data.
`watchlist` + `not_a_fit` require a one-line `pic_relevance_note` stating why (e.g., GOJO/STERIS rulings).

### 4.4 Level A — Parent Organization

One record per ultimate controlling organization operating in scope. A Parent may have zero Ohio manufacturing sites (HQ-only, sales-only, holding) — that is valid if flagged.

| Field | Type | v1? | Notes |
|---|---|---|---|
| `org_id` | string, immutable, `ORG-######` | **MUST** | Never reuse after merge/closure |
| `legal_name` | string | **MUST** | As in Ohio SOS / SEC / own site legal footer. E.g., "Avient Corporation" |
| `trade_names[]` | string[] | **MUST** | DBA / former / brand-operating names: ["GEON", "PolyOne"] |
| `parent_org_id` | FK → org_id, nullable | **MUST** | Immediate parent if this org is a subsidiary that still warrants its own Parent record (see §5.2 threshold) |
| `ultimate_parent_name` + `ultimate_parent_country` | string | **MUST** if subsidiary | Free name if ultimate parent is out-of-scope and has no org_id |
| `entity_type` | enum | **MUST** | `corporation_public` \| `corporation_private` \| `llc` \| `partnership` \| `sole_proprietor` \| `nonprofit` \| `government` \| `academic` \| `cooperative` \| `unknown` |
| `ring_primary` / `ring_secondary` | enum 1–5 / nullable | **MUST** | Per §1. Parent ring may differ from site rings |
| `ring4_test` | string, e.g. "A+B" | MUST if Ring 4 | Which two prongs passed |
| `diversified_conglomerate` | boolean | **MUST** | True for Parker-type parents; suppresses whole-co headcount rollups |
| `hq_address` (street, city, state, ZIP) + `hq_county` + `hq_country` | structured | **MUST** | County is required — PIC reporting is county-based. Use Census county, not mailing-city assumption |
| `hq_in_scope` | enum | **MUST** | `ne_ohio` \| `ohio_other` \| `national_us` \| `international` — NE Ohio = Ashland, Ashtabula, Carroll, Columbiana, Cuyahoga, Erie, Geauga, Holmes, Huron, Lake, Lorain, Mahoning, Medina, Portage, Richland, Stark, Summit, Trumbull, Tuscarawas, Wayne (PIC/GAC 19-county working definition — confirm once, then freeze in code) |
| `naics_primary` + provenance block (§2.1) | string + object | **MUST** | Primary + provenance are one atomic unit; no naked NAICS |
| `naics_secondary[]` + provenance | array | Nice | Strongly encouraged; required if a second code appears in any source |
| `processes[]` / `materials[]` / `markets_served[]` | controlled vocab §3 | **MUST** (at least processes OR materials non-empty) | Parent = union of sites, but do not backfill a site's process to Parent unless Parent claims it corporately — note in field source |
| `employee_band_global` / `employee_band_ohio` | enum | Nice (Ohio band = MUST if known) | Bands: `1-9` \| `10-49` \| `50-99` \| `100-249` \| `250-499` \| `500-999` \| `1000-4999` \| `5000+` \| `unknown`. Never store a precise headcount as fact; if a source gives one, store band + `employee_count_source_date` |
| `founded_year` | integer | Nice | |
| `year_founded` **[v1.1]** | integer | Nice | ADOPTED NAME for the founding-year field: `year_founded` supersedes the v1.0 draft label `founded_year` above (the two rows are one field; the v1.1 adoption text governs the name). Legal-entity formation year where a source states it; multi-inception conflicts (e.g., rename years) stay unresolved in notes until a formation convention is ruled — never silently pick one. |
| `stock_ticker` **[v1.1]** | string | Nice | Exchange ticker for public orgs, **always with an as-of date in `field_sources`** — tickers are dated claims (a delisted ticker persisted in Wikidata is the known failure). Public parents only; never inferred. |
| `employee_band` **[v1.1]** | enum §4.4 bands | Nice (Ohio band = MUST if known) | The adopted Tier-2 band field. READING (flagged in the implementation plan): the existing populated column `employee_band_ohio` is this field's Ohio instance and is NOT duplicated by a second column; CRM-banked employee counts land in `employee_band_ohio` as banded values with provenance (see the migration notes). `employee_band_global` remains as defined above. |
| `ownership_type` **[v1.1]** | enum | Nice | `public_company` \| `private_company` \| `private_equity_portfolio` \| `family_owned` \| `employee_owned` \| `nonprofit` \| `government` \| `academic` \| `cooperative` \| `unknown`. Distinct from `entity_type` (legal form): this records control. Only from a primary/authoritative source; never inferred from size or name. (Vocabulary proposed in the implementation package — the adoption named the field, not its values.) |
| `certifications[]` **[v1.1]** | controlled vocab §3.4 | Nice | Promoted from the §3.4 nice-to-have list to a stored column on organizations. Values only from §3.4; self-disclosed or certificate-evidenced only. |
| `website` | URL | **MUST** if exists; explicit `none_found` otherwise | Own domain only; a LinkedIn page goes in `sources`, not `website` |
| `description_1line` | string ≤180 chars | **MUST** | Researcher-written, factual, no marketing copy-paste: "Custom injection molder, medical + automotive, Akron" |
| `pic_relevance[]` / `pic_relationship_stage` / `pic_relevance_note` | §4.3 | **MUST** | At minimum `potential_member` / `partner` / `watchlist` / `not_a_fit` |
| `status` + `status_date` + `status_source` + `successor_org_id` | §4.2 | **MUST** | |
| `sources[]` | array of {url/name, date_accessed, tier} | **MUST** | Every record has ≥1 source; must-have fields each traceable via `field_sources` |
| `field_sources` | map field→source index | **MUST** for name, address, ring, NAICS | Lightweight: only must-have fields need per-field mapping in v1 |
| `verification_tier` | A/B/C/U | **MUST** | Per §4.1 weakest-must-have rule |
| `last_verified` | date | **MUST** | Date a human/agent actually checked primary fields, not scrape date alone |
| `created_by` / `created_date` / `last_edited_by` | string/date | **MUST** | Researcher/agent ID for dedupe accountability |
| `certifications[]`, revenue band, key contacts, LinkedIn URL, logos, patent counts | — | Nice | Contacts are a separate, access-controlled table in v2 — do NOT store personal emails/phones in v1 org record |

### 4.5 Level B — Establishment / Site

One record per distinct physical location (plant, HQ office if separate from plant, R&D center, warehouse, lab). **This is the unit PIC visits, maps, and counts for Ohio footprint.** Most Ohio ~900-firm counts are establishment counts — keep Parent and Establishment counts explicitly separate in all reporting.

| Field | Type | v1? | Notes |
|---|---|---|---|
| `site_id` | string, `SITE-######` | **MUST** | |
| `org_id` | FK → Parent | **MUST** | Every site has exactly one Parent at a time; ownership changes create a new linkage with dates (see §5.5) |
| `site_name` | string | **MUST** | As signed/listed: "Avient — Avon Lake Plant". Default = `{Parent trade name} — {City}` |
| `site_type` | enum | **MUST** | `manufacturing_plant` \| `hq_only` \| `hq_and_plant` \| `rd_center` \| `lab_testing` \| `warehouse_distribution` \| `sales_office` \| `tool_shop` \| `recycling_facility` \| `training_center` \| `campus` \| `virtual_incubator` |
| `address_street/city/state/zip` + `county` + `lat_lon` (optional in v1) | structured | **MUST** (lat/lon Nice) | Physical address, not PO Box if a physical address exists. County MUST be from address geocode/official source |
| `street_address` **[v1.1]** | string | **MUST** if known | The street component as its own column (in the CSV it is the single `street_address` column alongside `city`/`state`/`zip`). This is the address-first matching key the v1.0 layout lacked: street addresses previously lived only inside notes, which capped every address join. Backfilled ONLY from named sources already on the record (own-site address, filing, parcel record) — no unsourced bulk backfill. |
| `latitude` / `longitude` **[v1.1]** | decimal | Nice | From the Census batch geocoder or the coordinates supplement; always paired with `geocode_precision`. |
| `geocode_precision` **[v1.1]** | enum | MUST if lat/lon present | `rooftop` \| `parcel` \| `address_interpolated` \| `zip_centroid` \| `city_centroid`. A centroid value never corrects a recorded county and is never presented as a rooftop location. |
| `ring_primary` (site-level) | enum 1–5 | **MUST** | May differ from Parent (Parker rule) |
| `naics_primary` + provenance | §2.1 | **MUST** | Site NAICS often differs from Parent NAICS — never copy Parent NAICS to site without a site source or `researcher_inferred` flag |
| `processes[]` / `materials[]` / `markets_served[]` | §3 | **MUST** (processes required for Ring 1/2/3 sites) | Site-level truth; this is the most valuable field set in the DB |
| `employee_band_site` | enum §4.4 | **MUST** if any source gives it; else `unknown` | Never allocate Parent headcount pro-rata to sites |
| `operating_status` + dates | §4.2 vocab per site | **MUST** | A Parent can be `active` while a site is `idled`/`closed` |
| `website_site_page` | URL | Nice | Plant page / location page if distinct |
| `sources[]` / `verification_tier` / `last_verified` | §4.1 | **MUST** | Same rules as Parent |
| Square footage, line/press counts, press tonnage range, cleanroom class detail, shift count, rail/truck access | — | Nice | High value for PIC site-selector / expansion work; collect opportunistically in v1, systematically in v2 |
| `site_notes` | free text | Nice | Idling, expansion, fire, sale — each note dated + sourced inline |

### 4.6 Level C — Ecosystem Entity

Use for Ring 5 only. Ecosystem entities get a Parent-shaped record PLUS this extension; they do NOT get Establishment records unless they have multiple distinct campuses/centers in scope (then each center is a site with `site_type=campus/training_center`).

| Field | Type | v1? | Notes |
|---|---|---|---|
| All Parent MUST fields (org_id, legal_name, entity_type=`nonprofit/academic/government`, ring=5, HQ address+county, website, description, sources, tier, last_verified, status, pic_relevance) | — | **MUST** | Same backbone — one dedupe system for all entities |
| `ecosystem_subtype` | enum §1 Ring 5 | **MUST** | |
| `polymer_program_name` + `polymer_program_url` | string/URL | **MUST** if claimed | The named program is the inclusion evidence; "has a chemistry department" is not a program name. Since v1.3 the field is live in the data: validator rule V-13 fails an institution-grain row claiming `polymer_program=true` with no URL, and fails a URL on a row claiming false (no orphan evidence). Once the institution has program rows in `data/programs.csv` (§4.11), this field and `polymer_program_name` are the generated rollup defined there — the URL of the institution's lead program row. |
| `polymer_program` | boolean | **MUST** | False allowed only for NE Ohio generalists (see §1) |
| `generalist` | boolean | **MUST** | True for county EDOs, general workforce boards, Ohio MEP, etc. |
| `services_offered[]` | controlled: `degrees` \| `certificates` \| `apprenticeship` \| `incumbent_worker_training` \| `rd_facilities_access` \| `testing_access` \| `funding_grants` \| `funding_capital` \| `site_selection` \| `convening_events` \| `k12_outreach` \| `technical_assistance` | **MUST** (≥1) | |
| `geography_served` | enum + counties[] | **MUST** | `site_local` \| `county` \| `ne_ohio` \| `ohio` \| `national` \| `international` |
| `member_or_open_to` | string | Nice | E.g., association membership criteria, lab access model |
| `parent_institution_org_id` | FK, nullable | Nice→MUST if center-within-university | E.g., a polymer center inside a university: center may be its own Ecosystem record linked to the university Parent — see §5.2 |
| `ipeds_unitid` | string (6 digits) | university_college rows | The institution's UNITID in the IPEDS Institutional Characteristics directory (NCES). An identity join key only: it asserts *which institution this record is*, never that a program exists — program claims are decided by the named-program test on the institution's own pages (§4.11), and third-party/IPEDS program attributions are leads, not evidence (Lakeland rule, Phase B 2026-10-29). |
| `ror_id` | string (canonical URI `https://ror.org/…`) | university_college rows | The institution's Research Organization Registry record. Same doctrine as `ipeds_unitid`: identity evidence, never activity or program evidence. Validator V-14 confines both fields to `university_college` rows and enforces their uniqueness across the file — the same campus cannot be entered twice under two names. |


**[v1.2] Record grains (proposal S2, as drafted by Phase A).** Ecosystem records carry a
grain discriminator, `record_grain`: `institution` | `program` | `office`. All existing
ecosystem rows backfill to `record_grain=institution` at application. (Naming reading,
flagged in the implementation plan: proposal S2 wrote `entity_grain`; the landed Phase A
draft — the more specific, later text — uses `record_grain`, and `record_grain` governs.)

> **[v1.3]** Program-grain records move to their own table, `data/programs.csv`
> (§4.11). `record_grain` on ecosystem narrows to `institution` | `office`;
> a program-grain row in ecosystem.csv is a validator error (V-8 as amended).
> Office grain is unchanged. The program-only grain columns retired from
> ecosystem.csv at the migration are listed in §4.11; their values live in
> the programs table.

**Program records** (`record_grain=program`) — a named degree, center, certificate, or
apprenticeship; the program, not the university, is the unit an introduction targets:

| Field | Type | v1.2? | Notes |
|---|---|---|---|
| `program_name` | string | **MUST** | As the institution styles it; the named program is the Ring 5 inclusion evidence |
| `parent_institution_org_id` | FK → institution record (organizations ∪ ecosystem) | **MUST** | §4.6's `parent_institution_org_id`, promoted to MUST at this grain |
| `program_type` | enum | **MUST** | `degree` \| `certificate` \| `apprenticeship` \| `center` \| `training` — exactly one; a center that also grants degrees is `center`, with the degrees in `credential_types[]` |
| `credential_types[]` | enum[] | MUST **only for** `degree`/`certificate`/`apprenticeship` types | `phd` · `ms` · `bs` · `aas_associate` · `certificate` · `registered_apprenticeship` · `incumbent_worker_training` · `noncredit_workforce`. **Calibration fix (Phase A, 2026-10-29): as an unconditional MUST this field failed every center in the sample (0/7 grant credentials); it is therefore conditioned on program type, and `center`/`training` records carry it empty by design.** |
| `program_url` | URL | **MUST** | The program's own public page (Tier A primary source) |
| `specialty_processes[]` / `specialty_materials[]` | §3.1 / §3.2 vocab | as evidenced | Never inferred beyond the program's own page. Characterization facilities fill neither — they tag `research_areas[characterization_methods]` (§3.5) |
| `research_areas[]` | §3.5 supplement | research programs only | §3 terms first wherever they honestly fit |
| `engagement_modes[]` | enum[] | **MUST** (≥1) | Extends §4.6 `services_offered[]`: `research_collaboration` · `student_projects_capstone` · `internships_coops` · `testing_characterization_access` · `lab_facility_access` · `licensing_tech_transfer` · `training_seats_open_enrollment` · `customized_employer_training`. **Grain rule (Phase A calibration): degree pages publish student-facing modes only; center pages publish employer-facing modes. A degree record carrying only student-facing modes is complete, not thin — the skew is a fact about the source.** |
| `apprenticeship_registered` | boolean | training/apprenticeship types | From the public DOL/state apprenticeship registry only |
| `employer_custom_training` | boolean | training types | Institution states it will run a cohort for one employer |
| `admissions_status` | enum | training/program types | `admitting` \| `not_admitting` \| `unknown` — Phase A calibration rider: a link's liveness ≠ a program's liveness; training records require an admissions-status check at verification |
| `facilities_note` | free text, sourced | Nice | Publicly stated labs/equipment |
| `scale_band` | enum (band precedent) | Nice | Only where the institution itself publishes it; banded, never a precise headcount. Calibration: enrollment bands filled 0/12 — pages publish outcomes instead; expect this field to stay sparse |
| `public_door_url` | URL | **MUST** | The program's public contact/admissions/partnership **page** — never a person's email (§6) |

**Office records** (`record_grain=office`) — a university's tech-transfer / licensing
office, under its institution record:

| Field | Type | v1.2? | Notes |
|---|---|---|---|
| `office_name` | string | **MUST** | As the university styles it |
| `parent_institution_org_id` | FK | **MUST** | Grain rules from Phase A calibration: an independent R&D institute that licenses its own IP (Battelle class) is office-grain under itself as parent; a cross-institution portal (DOE Lab Partnering Service class) is a national-channel office; hospital/system offices that present as sections or venture arms pass if they *function as the licensing door on an own page* — a standalone site is not required |
| `tto_url` | URL | **MUST** | The office's own public page — the door |
| `industry_partnership_modes[]` | enum[] | **MUST** (≥1) | `licensing` · `sponsored_research` · `startup_formation` · `materials_transfer` · `facility_access`, from the office's own published offer |
| `technology_areas[]` | §3.1/§3.2 vocab where they map; sourced free text otherwise | as evidenced | The office's stated portfolio themes |
| `public_door_url` | URL | **MUST** | Generic industry-contact page. **Office phone numbers are never carried** — §6 permits public switchboards only where a schema field exists; no such field exists at this grain |

Program and office records keep the §4.6 backbone (Parent MUST fields, `sources[]`,
`verification_tier`, `last_verified`, `status`, `pic_relevance`). Tier grammar at these
grains: the institution's own program/office page = A-equivalent; state registry /
accreditor / association directory = B; lone aggregator = C.

### 4.7 v1 Must-Have Summary (the "no record ships without these" gate)

A v1 record is **complete** only if it has: legal name, trade names (or explicit empty), entity type, ring_primary (+ Ring 4 test if Ring 4, + subtype if Ring 3/5), HQ/site address with **county**, NAICS primary **with provenance block**, at least one of processes/materials, 1-line description, website or `none_found`, status, ≥1 source, verification tier, last_verified, PIC relevance + stage, and creator ID. Everything else is enrichment. An incomplete candidate lives in a staging queue with `verification_tier=U` — it is not counted in headline totals.

---

### 4.8 External registry-ID link table **[v1.1]** (`data/registry_links.csv`)

Registry identity is recorded **once**, in its own table, instead of being re-derived
every wave. One row per (organization, registry, identifier); multi-value by design —
an org may hold several LEIs and they are never collapsed to one.

| Field | Type | Notes |
|---|---|---|
| `org_id` | FK → organizations ∪ ecosystem | **MUST** |
| `registry` | enum | `LEI` \| `OHIO_SOS_CHARTER` \| `WIKIDATA` \| `SEC_CIK` \| `SEC_CIK_PARENT_FILER` \| `FRS` \| `TRI_TRIFID` \| `FDA_FEI` \| `EIN_NONPROFIT` (extensible only by dated revision) |
| `registry_id` | string | Verbatim as the registry carries it (charter numbers verbatim incl. leading zeros; CIKs zero-padded to 10) |
| `match_basis` | string | How the match was established, e.g. `gleif_exact_confident`, `wikidata_confident_match`, `edgar_ex21_subsidiary_of_filer:<filer name>` — a guarded no-hit is never recorded as a negative fact |
| `as_of` | date | The date the registry record was retrieved/verified |

Seed population: the adjudicated GLEIF / Wikidata / EDGAR crosswalk (141 of its 142
seed orgs carry into the table at application; the one holdout is named in the
implementation package's match audit). Non-hits are provenance only — the table never
records "unregistered" or "no parent". EIN appears only via ProPublica for nonprofits
(`EIN_NONPROFIT`); EIN yield from GLEIF/Wikidata/EDGAR was zero and no bulk EIN source
is adopted. FRS / TRI / FDA registries join by the same mechanics when a wave produces
org-keyed matches — no rows are minted speculatively.

### 4.9 People records **[v1.2]** (`data/people.csv`) — professors only

Structure adopted at this revision; **records are built only in their own scoped
professor passes** — adopting this section creates no records.

| Field | Type | Notes |
|---|---|---|
| `person_id` | string, immutable, `PERSON-######` | Never reused |
| `full_name` | string | As published on the institution's page |
| `institution_org_id` | FK → organizations ∪ ecosystem | **MUST** |
| `program_org_id` | FK → `data/programs.csv` (§4.11), nullable. (At v1.2 this pointed at program-grain ecosystem records; programs moved to their own table at v1.3 and the reference follows them. Validator V-11 as amended.) | Where the public page ties the person to a held program |
| `role` | controlled | The institution's own styling, recorded verbatim in `role_as_published`; the controlled value is one of: `professor` \| `associate_professor` \| `assistant_professor` \| `research_professor` \| `center_director_professor` (directors/program leads qualify **only** if they also hold a publicly stated professor title) |
| `role_as_published` | string | The institution's exact words — never normalized or inferred |
| `research_specialties[]` | §3.1/§3.2 vocab first, §3.5 supplement where needed | As publicly stated on the cited page |
| `public_profile_url` | URL | Their own faculty/lab page |
| `sources[]` | public citations only | **MUST**, ≥1 per record, every field traceable to a public university/program/lab page |
| `verification_tier` / `last_verified` | §4.1 | Shortest refresh leash in the layer; a vanished/changed profile downgrades the record to U |

**Hard constraints (validator-enforced):** no email, phone, or address field exists in
this class; the PIC CRM is **not an admissible source** — no field, name, or record's
existence may derive from CRM data, and there is no CRM export/extract/cross-check step
for people anywhere in the pipeline; researchers, staff scientists, and postdocs are
not recorded; removal on request is honored at the next pass.

### 4.10 PIC membership **[v1.2]**

Membership is published **only** where it is already public (AGENTS.md §5.x as amended):

- On organizations and ecosystem records: `pic_member` (boolean), `member_since`
  (year, nullable), `membership_source_url`. `membership_source_url` is **required
  when `pic_member` is true and admissible only as a public PIC website member-list
  URL** — the validator rejects any other source class for this field. `member_since`
  is populated **only where the public source states it**; a join year known only from
  the CRM stays blank. CRM-derived values are inadmissible by construction.
- The spanning record lives in **`data/members.csv`**, the member table: one row per
  website-listed member, spanning organizations ∪ ecosystem ∪ member-only rows
  (members with no Atlas record — ecosystem-class, government, service-class, and
  unresolved-display-name members — exist as member-only rows and never enter the
  company census by virtue of membership). Columns: `member_row_id` (`MBR-######`),
  `display_name` (as displayed), `member_tier` (as displayed, e.g. `Investing
  Partners` / `Cornerstone Partners`), `record_class`
  (`organization` | `ecosystem` | `member_only`), `org_id` (FK, nullable — null iff
  `record_class=member_only`), `member_since`, `membership_source_url`,
  `snapshot_date`, `notes`.
- The website list is the source of record, refreshed by snapshot → diff →
  assert-first packets (monthly + event-driven; full reconciliation, not sampling).
  A roster listing proves membership, never current operation — member records follow
  the same verification standard as every record. Member elevation (badge,
  members-first sort, members-only filter) is a **presentation rule** in generated
  outputs (§4.10's SQLite view), never a data privilege.

### 4.11 Program records **[v1.3]** (`data/programs.csv`)

One row per named program at an institution — the unit an introduction
actually targets. Programs were ecosystem `record_grain=program` rows at
v1.2; since v1.3 they live in this table. Offices remain ecosystem
office-grain rows (§4.6); institutions remain ecosystem institution rows
(or organization records), and this table keys to them.

| Field | Type | v1.3? | Notes |
|---|---|---|---|
| `program_id` | string, immutable, `PROG-######` | **MUST** | Never reused; allocated at integration only |
| `institution_org_id` | FK → organizations ∪ ecosystem | **MUST** | The institution the program belongs to |
| `program_name` | string | **MUST** | As the institution styles it; the named program is the Ring 5 inclusion evidence |
| `program_type` | enum | **MUST** | `degree` \| `certificate` \| `apprenticeship` \| `center` \| `training` \| `lab_facility` \| `course` — exactly one; a center that also grants degrees is `center`, with the degrees in `credential_types[]` |
| `credential_types[]` | enum[] | MUST only for `degree`/`certificate`/`apprenticeship` types | `phd` · `ms` · `bs` · `aas_associate` · `certificate` · `registered_apprenticeship` · `incumbent_worker_training` · `noncredit_workforce` (the v1.2 conditioning carries over: centers grant no credentials and carry it empty by design) |
| `level[]` | enum[] | **MUST** | `certificate` \| `associate` \| `bachelor` \| `master` \| `doctorate` \| `none`. Derived from `credential_types[]` by the fixed map (phd→doctorate, ms→master, bs→bachelor, aas_associate→associate, certificate→certificate; apprenticeship/training credentials map to none); validator V-15 enforces the derivation, so the two fields cannot drift |
| `cip_code` | string `NN.NNNN` (CIP-2020) | nullable | **Data, never evidence** — see the inclusion rule below. Carries `cip_source_type` (`institution_published` \| `ipeds_listing` \| `researcher_inferred`), the §2.1 provenance grammar applied to CIP; the pair is recorded together or not at all |
| `unit_department` | string | Nice | The administering school/department/unit, as published |
| `description_1line` | string | **MUST** | Backbone parity with ecosystem records |
| `url` | URL | **MUST** | The program's own public page (Tier A primary source) |
| `public_door_url` | URL | **MUST** | The program's public contact/admissions/partnership page — never a person's email (§6) |
| `first_year_awarded` / `last_year_awarded` / `latest_completions` / `completions_year` | year / year / integer / year | degree rows only, nullable | IPEDS Completions data, populated only by a completions pull keyed on the institution's `ipeds_unitid` (§4.6) × `cip_code`, and cited to that pull in `sources[]`. Never estimated; `latest_completions` requires `completions_year` |
| `specialty_processes[]` / `specialty_materials[]` | §3.1 / §3.2 vocab | as evidenced | Never inferred beyond the program's own page. Characterization facilities fill neither — they tag `research_areas[characterization_methods]` (§3.5) |
| `research_areas[]` | §3.5 supplement | research programs only | §3 terms first wherever they honestly fit |
| `engagement_modes[]` | enum[] | **MUST** (≥1) | The §4.6 program-grain set. Grain rule (Phase A): degree pages publish student-facing modes only; center pages publish employer-facing modes — a degree record carrying only student-facing modes is complete, not thin |
| `apprenticeship_registered` | boolean | training/apprenticeship types | From the public DOL/state apprenticeship registry only |
| `employer_custom_training` | boolean | training types | Institution states it will run a cohort for one employer |
| `admissions_status` | enum | program types | `admitting` \| `not_admitting` \| `unknown` — a link's liveness ≠ a program's liveness; training/program records require an admissions-status check at verification |
| `facilities_note` | free text, sourced | Nice | Publicly stated labs/equipment |
| `scale_band` | enum (band precedent) | Nice | Only where the institution itself publishes it; banded, never a precise headcount |
| `geography_served` | §4.6 vocab | **MUST** | Workforce programs are place-bound; research programs are not |
| `city` / `state` / `county` | string | **MUST** | The campus locality as published; Ohio rows follow the physical-address county rule. Defaults to the institution's values; multi-campus systems carry per-campus values |
| backbone (`status`, `sources[]`, `verification_tier`, `last_verified`, `pic_relevance`, `created_by`, `notes`) | §4.2/§4.6 | **MUST** | Tier grammar at this grain: the institution's own program page = A-equivalent; state registry / accreditor / association directory = B; lone aggregator = C |

**Inclusion rule (the named-program test, restated for this grain).** A
program row is created only when, on the institution's own public pages or
official catalog: (a) a program, center, institute, or credential is named
and is polymer, plastics, rubber, composites, or coatings **by name**; or
(b) a degree or certificate's own published description names a **polymer
track, concentration, or research area**; or (c) a **facility or service
states polymer** materials, processes, or characterization services as its
offer (`program_type=lab_facility`). A CIP code never satisfies (a)–(c): an
IPEDS or third-party program attribution is a discovery lead, and a program
so attributed that the institution's own catalog does not carry is not a
program (Lakeland rule, Phase B 2026-10-29). A single named course is
recordable (`program_type=course`) but does not by itself make its
institution pass §4.6's named-program test. `admissions_status` is a
verification field, never an inclusion criterion. Borderline calls are
logged in the inclusion log (Appendix A) with the prong cited; institution-
level seam cases (a polymer track inside a general degree) stay flagged as
seams until the owner rules — a program row never settles a seam by landing.

**The rollup.** An institution's ecosystem `polymer_program_name` is a
generated rollup of its program rows in this table: the non-tombstoned
rows' `program_name` values, ordered by program_type precedence (degree,
center, certificate, apprenticeship, training, lab_facility, course) then
name, joined with `"; "`. Its `polymer_program_url` (§4.6) is the `url` of
the first row in that order. The rollup binds only when at least one program
row exists; an institution claiming a program with no rows yet keeps its
existing text and is reported by the validator (V-16) as an un-decomposed
claim — a visible pending state, not an error.

**Migration note.** The v1.2 program-grain columns on ecosystem.csv
(`program_name`, `program_type`, `credential_types`, `program_url`,
`specialty_processes`, `specialty_materials`, `research_areas`,
`engagement_modes`, `apprenticeship_registered`, `employer_custom_training`,
`admissions_status`, `facilities_note`, `scale_band`) are retired at this
revision; program values live in this table. `parent_institution_org_id`,
`public_door_url`, and the office-grain columns remain on ecosystem.csv.

## 5. Entity Resolution Rules — Dedupe Identically

**Goal:** Three researchers given the same firm reach the same Parent/Site split, the same canonical name, and the same merge decision. When in doubt, **do not merge** — link with `related_org_ids[]` + note and flag for review. A false merge destroys data; a false split is cheap to fix.

### 5.1 Canonical name

1. Canonical `legal_name` = Ohio Secretary of State / SEC / company's own legal footer, in that priority order. Title case, keep legal suffix in a separate `legal_suffix` note if it creates variants (store display name without "Inc."/"LLC" in `trade_names` search index).
2. Search/dedupe key (system-generated, never hand-typed): normalized = lowercase, strip punctuation/suffixes (inc, llc, corp, co, company, the), collapse whitespace, strip city name. Match on key + county + domain before creating a new record.
3. **Domain is the strongest dedupe signal.** Same own-domain website = presumptive same Parent (rebuttable only for conglomerate brand microsites — see 5.2). Same address + different domain = presumptive different Parents (co-location, incubator, contract manufacturing are common in Ohio polymer).
4. Never use an acronym alone as legal name if the expansion is known (SPE, ACS are exceptions — acronym *is* the canonical name for those associations; store expansion in trade_names).

### 5.2 Parent vs. subsidiary vs. division vs. brand

Create a **separate Parent record** for a subsidiary/brand ONLY if it meets **2 of 3**:
- (i) Operates under a distinct trade name in the market (customers buy from that name),
- (ii) Has its own Ohio Establishment(s) distinct from the parent's other Ohio sites, OR its own HQ,
- (iii) Has its own website/domain or distinct directory listings as a standalone company.
Otherwise it is a **brand/division**: record it in the Parent's `trade_names[]` + `divisions_brands[]` (name, note, Ohio sites) and create its Ohio locations as Establishments under the controlling Parent. Divisions never get org_ids.

**Worked rulings (binding):**

| Case | Structure |
|---|---|
| **Avient / GEON** | **CORRECTED by owner ruling 2026-10-28 (John Swanson): GEON Performance Solutions is its OWN Parent record** (HQ Westlake, OH; ultimate parent SK Capital Partners). GEON was spun out of PolyOne (now Avient) in 2019 and operates as a standalone compounder; it is NOT an Avient division or brand. The v1.0 draft of this section ruled the opposite - that ruling is void. Foster Corporation, acquired by GEON, is recorded as a GEON division unless it independently meets the 2-of-3 test. Lesson encoded: spinout status must be checked against current ownership sources, never inferred from historical lineage. |
| **RPM International / Day-Glo** | Parent: **RPM International Inc.** (Medina HQ). **Day-Glo Color Corp.** (Cleveland) MEETS 2-of-3 (distinct market name, distinct Cleveland plant/HQ history, standalone listings/website presence) → Day-Glo gets its **own Parent record** with `parent_org_id → RPM`, `ultimate_parent_name=RPM International`. Same test applied to each RPM subsidiary individually — do not bulk-create or bulk-suppress RPM children. |
| **Vibrantz / Chromaflo** | Parent chain flipped by acquisition: Chromaflo Technologies (Ashtabula) was acquired into what is now **Vibrantz Technologies**. Current controlling Parent = **Vibrantz** (out-of-state HQ, `hq_in_scope=national_us`). Chromaflo = former independent Parent, tombstoned `acquired`, `successor_org_id → Vibrantz`, with its Ashtabula site(s) re-linked to Vibrantz as Establishments (site linkage carries `valid_from` = acquisition close date). New records are created under Vibrantz; "Chromaflo" persists in `trade_names[]` because the market still uses it. |
| **Synthomer / OMNOVA legacy** | OMNOVA Solutions (Beachwood HQ, Akron-area plants historically) was acquired by Synthomer (UK). OMNOVA Parent = tombstone `acquired → Synthomer plc (ultimate, international)`. Create/reuse a **Synthomer** Parent record for the Ohio footprint (US operating parent if one is the employer/operator of record). Ohio plants formerly listed as OMNOVA = Establishments under Synthomer, `site_name` may retain "formerly OMNOVA" in notes for 5 years, not in canonical site_name. Legacy OMNOVA NAICS/listings are sources, not separate live records. |
| **Goodyear / Cooper, Bridgestone / Firestone-type legacy brands** | Same pattern: acquired brand with continuing Ohio plants = brand in `divisions_brands[]` unless it still meets 2-of-3 as a market-facing subsidiary (Cooper as a Goodyear subsidiary post-acquisition: assess on current market operation, not pre-acquisition independence). When unsure, default to division (no org_id) + detailed note — reviewers can promote a division to Parent, but demoting a duplicate Parent is messier. |

### 5.3 Plant vs. HQ vs. brand site

- One physical address = one Establishment, even if two Parents claim it (contract manufacturer + brand owner co-located): create the site under the **operator** (who runs the process), link the other Parent via `related_org_ids` + note. Never duplicate the address as two sites.
- HQ in an office building with no plant/lab = `hq_only` site (create it — PIC needs the HQ pin — but exclude `hq_only` sites from "plant counts" in reporting).
- A campus with a plant + R&D center at one address = ONE Establishment, `site_type=hq_and_plant` or `manufacturing_plant`, with R&D noted in processes/notes. Two addresses across the street with separate operations = two Establishments.
- Sales rep's home, a PO Box, a registered-agent address (e.g., CT Corporation, Columbus agent addresses) = NEVER an Establishment. This single rule prevents the largest known source of phantom Ohio sites.

### 5.4 Name variants, mergers, and history

- All former names, spelling variants, and directory misspellings that a searcher might use go in `trade_names[]` / `name_variants[]` (nice-to-have field, mandatory when a variant is encountered in a source). The database must find "Poly One", "PolyOne", and "Avient" as the same lineage.
- **M&A handling:** Acquired org is never deleted and its org_id is never reused. Set `status=acquired/merged`, `status_date`=close date (announcement date if close unknown, noted as such), `successor_org_id`, keep its historical Establishments linked historically, and create new Establishment linkages under the successor with `valid_from`. If only a division/assets were sold, tombstone only if the legal entity ceased; otherwise keep the Parent `active` with a dated note and adjust sites.
- **Spin-offs:** New Parent for the spun entity from spin date; historical linkage noted both ways. Pre-spin sites belong historically to the old Parent, currently to the new one.
- **Rebrands with no ownership change** (e.g., PolyOne → Avient, 2020): SAME org_id, update `legal_name`, push old name to `trade_names[]`, note `name_change_date`. A rebrand is not an acquisition.

### 5.5 Idled / closed sites

- `idled` requires a dated source (news, WARN notice, company statement, EDO confirmation) — a quiet plant or an old Google review is not evidence of idling. Without a dated source, keep `active` and add a dated `site_notes` concern.
- Closed sites stay in the database forever as tombstones with closure date/source. They are excluded from "active" counts by filter, never by deletion — PIC needs closure history for workforce and site-reuse work.
- Ohio WARN Act filings are a Tier B source for closures/mass layoffs and should be a standing sweep source.
- If a closed site reopens under a new operator, the OLD Establishment is closed and a NEW Establishment (new site_id, new org_id linkage) is created at that address. Do not resurrect the old site_id under a new owner.

### 5.6 Researcher workflow — the 2-minute dedupe check (in order, stop at first hit)

1. Search by **domain** → hit? Use that Parent.
2. Search by **normalized name key** (§5.1.2) → hit? Check county/domain — same firm or namesake in another state?
3. Search by **address** → hit? Operator rule (§5.3) applies.
4. Search by **trade_names / name_variants** → hit? You found a rebrand/acquisition lineage; follow `successor_org_id`.
5. No hit → create new record, Tier U/C until §4.7 gate is met, and log the searches you ran in the record's creation note so a reviewer can see dedupe was attempted.

### 5.7 Geography & counting rules (so totals are honest)

- Headline counts must ALWAYS state the unit: "Parents with an Ohio footprint: N" vs. "Ohio Establishments: M" vs. "NE Ohio Establishments: K". Never publish a bare "900 companies" number without the unit and the Ring filter.
- A Parent counts for Ohio if it has ≥1 Ohio Establishment (including `hq_only`). A Parent counts for NE Ohio if ≥1 Establishment is in the §4.4 county list.
- National Parents with no Ohio site are included ONLY in Ring 5 (associations) or as ultimate-parent stubs for Ohio subsidiaries — they do not inflate Ohio counts.
- Franchise/franchisee: franchisor = Parent stub; each independently owned Ohio location = its own Parent if independently owned (tire retreader rule), or an Establishment of the franchisor if company-owned. Ownership, not signage, decides — if unknown, default to Establishment + `ownership_unverified` note.

---

## Appendix A — Inclusion / Exclusion Log (required practice)

Every borderline decision that is NOT obvious from §1 — every Ring 4 test, every GOJO/STERIS-type exclusion, every division-vs-Parent call — gets a one-line log entry (entity, decision, test/prongs or rule cited, date, researcher) in a shared log reviewed monthly. Precedents in the log upgrade into §1 edge cases at each schema revision. This log is how the database stays consistent when the swarm scales — it is not optional paperwork.

## Appendix B — Schema Change Control

Controlled vocabularies (§3) and Ring rules (§1) change only by a dated revision to this document. Researchers who encounter a misfit use `*_other_note` + flag it; they do not improvise tags or rings. Review other-notes monthly; promote recurring notes into the vocabulary with a version bump.

*End of v1.0 design.*

---

## Revision history

- **v1.0 — 2026-10-28.** Initial design (rings, NAICS map, §3 vocabularies, record schema, resolution rules).
- **v1.1 — adopted 2026-10-29 as part of the combined v1.2 revision.** Tier 1: `street_address` on sites; site `latitude`/`longitude` + `geocode_precision`; external registry-ID link table (§4.8); `year_founded`; `stock_ticker`. Tier 2: `employee_band`, `ownership_type`, `certifications` on organizations. (Decision memo 2026-10-29 §1, option (a).)
- **v1.2 — 2026-10-29 (this text).** People records — professors only, public facts only, CRM never a source (§4.9); program/office record grains on ecosystem (§4.6 extension) with the §3.5 research-areas supplement under the §3-first rule; PIC membership fields + spanning member table, website-public only (§4.10); `pic_relationship_stage` retired from the public files (§4.3). (Repo change proposals S1–S4; connections trio approval 2026-10-29; Phase A calibration fixes integrated: conditioned `credential_types`, `admissions_status`, the engagement-mode grain rule.)
- **v1.3 — 2026-10-29 (drafted; dated at application).** §4.6 drift fix: `polymer_program_url` column lands in ecosystem.csv with validator rule V-13 (MUST-if-claimed enforced at institution grain, with a dated pending list for unsourced claims); `ipeds_unitid` + `ror_id` identifier columns on university_college rows (V-14; identity join keys only — IPEDS/ROR assert identity, never program existence). Program records move from ecosystem grain rows to `data/programs.csv` (§4.11; V-15/V-16), adding `cip_code` with provenance, `level`, `unit_department`, and IPEDS completions fields to the v1.2 program grain; `program_type` gains `lab_facility` and `course` (apprenticeship retained); the `polymer_program_name`/`polymer_program_url` fields become the generated rollup of an institution's program rows; the inclusion rule is restated with the Lakeland rule (a CIP attribution is never program evidence); §4.9's `program_org_id` re-points to the programs table.
