# Polymer / Plastics / Rubber Industry Database — Taxonomy & Record Schema

**Owner:** Polymer Industry Cluster (PIC), Greater Akron Chamber — Director of Innovation Portfolio
**Version:** v1.6.2 — 2026-10-30 (events battery-release micro-revision:
§4.12.1 `coatings_finishing` subject_scope value added under owner
ruling 2026-10-30 (events-pass battery item ii); applied in the events
battery-release pass).
Prior: v1.6.1 — 2026-10-30 (pass-16 micro-revision: §3.6
`carbon_black` material term added under owner ruling 7A; §4.14
CPChem dual-parent exception documented under owner ruling 10A;
applied in integration pass 16).
Prior: v1.6 — 2026-10-30 (the combined v1.5 + v1.6 revision:
events layer (§4.12); evidence records (§4.13), relationship records
(§4.14), capability records (§3.6 + §4.15), liveness + Tier-1 qualifier
fields (§4.4), site `county_source` / `site_group_id` (§4.5); validators
V-17–V-33; owner rulings 2026-10-30; applied 2026-10-30 in integration
pass 14, against the post-pass-13 repo).
Prior: v1.5 — 2026-10-30 (events layer, §4.12; applied in the same pass,
Stage A); v1.4 — 2026-10-29 (`ownership_type` vocabulary adopted (§4.4);
`UEI` added to the §4.8 registry enum; owner ruled 2026-10-29 in the
consolidated batch ("all as recommended"); applied 2026-10-29 in
integration pass 12, against the post-pass-11 repo); v1.3 — 2026-10-29
(§4.6 drift fix, institutional identifiers, and the programs table;
owner directed the increment 2026-10-29 per the schema-v1.3 note
reconciliation; applied 2026-10-29 in the schema v1.3 micro-pass,
against the post-network-application repo)
**Status:** This document defines classification and record structure. It does not contain the company list.
**Change basis:** v1.1 (decision memo 2026-10-29 §1, option (a): Tier 1 + Tier 2) and v1.2
(repo change proposals S1–S4, 2026-10-29) adopted together as one dated revision. New or
changed text in this revision is marked **[v1.1]** / **[v1.2]** at the paragraph or row level.
The v1.3 increment's text is marked **[v1.3]** the same way.
The v1.4 increment's text is marked **[v1.4]** the same way.
The v1.5 increment's text is marked **[v1.5]** and the v1.6 increment's **[v1.6]** the same way.
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

#### 3.6 Capabilities (`capability terms`) **[v1.6]**

Capabilities are what a site **offers or runs, as the company itself
states it** — recorded per site in `data/site_capabilities.csv` (§4.15),
one row per (site, capability). They are *not* a second copy of
`processes[]` / `materials[]`: those fields remain the §3.1/§3.2
researcher tags on org and site records, with their own provenance
grammar. A capability row is a single sourced claim with the strict
two-value provenance of §4.15, which is why the layer is separate.

**§3.6.1 Non-duplication rule (binding).** Where a §3.1 process term
or a §3.2 material term already states the capability, the capability
term **is that string** — referenced, never redefined. Two lists with
near-identical terms is how vocabularies fork. A capability term is
NEW only where §3 has a genuine gap, and each NEW term below names
its gap. Four terms are **rollup umbrellas**: capability grain is
coarser than process-tag grain, so where §3.1 splits a process into
subtypes and offers no umbrella, the capability term is the umbrella
and the table states exactly which §3.1 subtypes roll into it.
Umbrella and NEW capability terms are valid **only** in
`site_capabilities.csv`; they are never valid values of `processes[]`
or `materials[]`, and minting one there is a vocabulary violation
under Appendix B exactly as an improvised §3 tag is.

**§3.6.2 Grain rule.** A capability term states the family, not the
variant. Subtype evidence (micro-molding, LSR, blown vs cast film)
stays in `processes[]` at §3.1 grain; the capability row carries the
umbrella. Conversely a capability row never *creates* a §3 tag: the
two layers cite their own sources independently.

**§3.6.3 Additions.** New capability terms arrive only by dated
schema revision (Appendix B), seeded by the queue discipline: a
researcher who meets a real capability with no §3.6 term writes **no
row**, records the capability verbatim in the site's `notes` prefixed
`CAPABILITY-QUEUE:` (the §3 `*_other_note` discipline applied to this
layer), and the queue is reviewed at the next schema prep. Lane
improvisation is forbidden.

**The seed vocabulary (58 terms).** Mapping column: `= §3.1` / `= §3.2`
means the identical string in that list (REFERENCE); `ROLLUP` lists
the §3.1 subtypes it covers; `NEW` states the gap.

*`capability_type = material` (25) — what the site works in or sells
as material:*

| Term | Mapping |
|---|---|
| `thermoplastics` | = §3.2 family |
| `thermosets` | = §3.2 family |
| `elastomers_rubber` | = §3.2 family (the rubber-compounds axis) |
| `thermoplastic_elastomers_tpe_tpu` | = §3.2 family (carries TPU) |
| `thermoplastic_olefin_tpo` | NEW — §3.2 has no TPO term; TPO compounds are sold and specified as their own class and do not honestly ride the TPE/TPU family string |
| `silicones` | = §3.2 family |
| `fluoropolymers` | = §3.2 family |
| `polyethylene_pe` | = §3.2 |
| `polypropylene_pp` | = §3.2 |
| `pvc` | = §3.2 |
| `pet_petg` | = §3.2 |
| `polystyrene_ps_hips` | = §3.2 |
| `polycarbonate_pc` | = §3.2 |
| `nylon_pa` | = §3.2 |
| `abs` | = §3.2 |
| `acetal_pom` | = §3.2 |
| `polyurethane_pu` | = §3.2 |
| `epoxy` | = §3.2 (thermoset-resin anchor) |
| `bioplastics_biobased` | = §3.2 family (the bio-polymers axis; `pla`/`pha` stay §3.2-grain only) |
| `recycled_content_pcr_pir` | = §3.2 family (recycled/reclaim streams as material) |
| `custom_compounds` | NEW — §3 states compounding only as a *process* (§3.1 `custom_compounding`); a compounder's sellable material class, chemistry unstated, has no §3.2 string |
| `inks_colorants_masterbatch` | = §3.2 family (masterbatch/color concentrates as material; the process side is §3.1 `color_masterbatch` — the axis decides the string) |
| `coatings` | = §3.2 family |
| `adhesives_sealants` | = §3.2 family |
| `carbon_black` | NEW — §3.2 names the rubber/elastomer families but carries no carbon black string; carbon black is a produced, specified material class (reinforcing and specialty carbons) at Cabot/Orion-class plants and does not honestly ride `elastomers_rubber`. Added by owner ruling 7A, 2026-10-30 (v1.6.1) |

Deliberately *not* seeded at material grain: the specific elastomer
compounds (`sbr`, `epdm`, `nitrile_nbr`, `neoprene_cr`, `viton_fkm`,
`natural_rubber_nr`), `peek_high_performance`, `phenolic`,
`melamine_urea_formaldehyde`, and the composites families
(`composites_frp` et al.). They remain §3.2 tags; if harvest volume
shows companies disclosing at that grain, the queue (§3.6.3) is the
route to promote them — the seed stays at resin-family grain as
designed.

*`capability_type = process` (18) — what the site runs:*

| Term | Mapping |
|---|---|
| `injection_molding` | = §3.1 (capability grain: `injection_molding_micro`, `injection_molding_lsr_silicone`, `insert_overmolding`, `two_shot_molding` roll into it) |
| `blow_molding` | = §3.1 legacy umbrella (covers `blow_molding_extrusion` / `_injection` / `_stretch`) |
| `extrusion` | ROLLUP — §3.1 has subtypes only: `extrusion_film_blown`, `extrusion_film_cast`, `extrusion_sheet`, `extrusion_profile`, `extrusion_pipe_tube`, `extrusion_wire_cable_coating`, `foam_extrusion` |
| `thermoforming` | ROLLUP — §3.1 has `thermoforming_vacuum` + `thermoforming_pressure` only |
| `rotational_molding` | = §3.1 |
| `compression_molding` | = §3.1 (plastics/composites grain; rubber compression is `rubber_molding` below) |
| `rubber_molding` | ROLLUP — §3.1 `rubber_molding_compression` + `rubber_molding_injection` |
| `rubber_mixing_compounding` | = §3.1 |
| `compounding` | ROLLUP — §3.1 `compounding_extrusion` + `custom_compounding` |
| `color_masterbatch` | = §3.1 (process side; cf. the material-axis string above) |
| `calendering` | = §3.1 — spelling is `calendering` (covers `rubber_calendering` at capability grain) |
| `composites_pultrusion` | = §3.1 (the process the shorthand "pultrusion" names) |
| `reaction_injection_molding` | NEW — RIM/RRIM has no §3.1 term at any grain; a real, separately marketed process (polyurethane structural parts) |
| `additive_manufacturing_polymer` | = §3.1 (`additive_manufacturing_polymer_production` rolls into it) |
| `polymerization` | = §3.1 (resin production as a capability) |
| `recycling_mechanical` | = §3.1 (covers `regrind_pelletizing`; chemical routes stay §3.1-grain until a company discloses one as a headline capability — queue route) |
| `coating_formulation` | = §3.1 (makes coatings; contrast §3.1 `coating_applying`, which is not seeded — applying is a trade service, not a disclosed plant capability at this grain) |
| `adhesive_sealant_formulation` | = §3.1 |

*`capability_type = product_form` (15) — what shape leaves the site.
This is the genuinely new axis: §3 has no product-form vocabulary.
All NEW; definitions are the boundary rules:*

| Term | Definition (boundary) |
|---|---|
| `film_sheet` | Thin-gauge film and sheet (flexible to semi-rigid web goods) |
| `sheet_plate` | Thick-gauge sheet, plate, and stock shapes sold as material (the SIMONA/Rowmark class) — gauge/stock-shape intent is the boundary vs `film_sheet` |
| `pipe_profile` | Pipe, tube-stock profiles, and extruded profile shapes (NAICS 326121/326122 class) |
| `tubing` | General/industrial tubing and hose-adjacent tubular goods not in `hose_belting` |
| `medical_tubing` | Medical-grade tubing (device/catheter class) — used only where the disclosure is medical; general tubing is `tubing` |
| `hose_belting` | Hose and belting products (NAICS 326220 class) |
| `foam_products` | Foam articles and foam stock (bead, slab, molded foam goods) |
| `fiber_filament` | Fiber, filament, yarn, and nonwoven web as the product |
| `bottles_containers` | Blow-/injection-molded bottles and rigid containers |
| `bags_pouches` | Bags, pouches, and converted flexible packaging |
| `molded_parts` | Molded components/parts as the product (the custom-molder default form) |
| `wire_cable` | Jacketed wire & cable as the product |
| `gaskets_seals` | Gaskets, seals, and sealing devices |
| `tires` | Tires (new and retread product; the *process* distinction stays in §3.1) |
| `flooring` | Resilient flooring products (NAICS 326192 class) |

## 4. Record Schema Organizations and sites are stored as per-state shard files under the placement function in Appendix C; all field rules in this section apply to the union of a table’s shards.

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
| `tier1_qualifier` **[v1.6]** | multi-valued enum, `;`-separated | Derived | Subset of `public_parent` \| `tri_reporter` \| `employees_250plus` \| `national_footprint`, in that fixed order, or empty. **Derived, never hand-asserted:** the column is derivation output, recomputed from the derivation rules below and diffed at each integration pass, like the §4.11 rollup — a hand edit is a validator warning (V-29) and is overwritten at the next pass. An empty value asserts nothing: the org may be unmeasured on every leg (e.g. no employee band populated), which is not evidence it fails any leg |
| `tier1_qualifier_basis` **[v1.6]** | string | Derived | One short clause per value present in `tier1_qualifier`, in the same order, stating the derivation input verbatim — e.g. `public_parent: stock_ticker=SHW; employees_250plus: employee_band_ohio=1000-4999`. Present iff `tier1_qualifier` is non-empty (V-29). Also derivation output, regenerated with the qualifier |
| `employee_band` **[v1.1]** | enum §4.4 bands | Nice (Ohio band = MUST if known) | The adopted Tier-2 band field. READING (flagged in the implementation plan): the existing populated column `employee_band_ohio` is this field's Ohio instance and is NOT duplicated by a second column; CRM-banked employee counts land in `employee_band_ohio` as banded values with provenance (see the migration notes). `employee_band_global` remains as defined above. |
| `ownership_type` **[v1.1]** **[v1.4]** | enum | Nice | `public_company` \| `private_company` \| `private_equity_portfolio` \| `family_owned` \| `employee_owned` \| `nonprofit` \| `government` \| `academic` \| `cooperative` \| `unknown`. Distinct from `entity_type` (legal form): this records control. Only from a primary/authoritative source; never inferred from size or name. (Vocabulary **adopted 2026-10-29 — v1.4**; at v1.1 the adoption named the field, not its values, and the values were carried as proposed until this revision.) |
| `certifications[]` **[v1.1]** | controlled vocab §3.4 | Nice | Promoted from the §3.4 nice-to-have list to a stored column on organizations. Values only from §3.4; self-disclosed or certificate-evidenced only. |
| `website` | URL | **MUST** if exists; explicit `none_found` otherwise | Own domain only; a LinkedIn page goes in `sources`, not `website` |
| `description_1line` | string ≤180 chars | **MUST** | Researcher-written, factual, no marketing copy-paste: "Custom injection molder, medical + automotive, Akron" |
| `pic_relevance[]` / `pic_relationship_stage` / `pic_relevance_note` | §4.3 | **MUST** | At minimum `potential_member` / `partner` / `watchlist` / `not_a_fit` |
| `status` + `status_date` + `status_source` + `successor_org_id` | §4.2 | **MUST** | |
| `sources[]` | array of {url/name, date_accessed, tier} | **MUST** | Every record has ≥1 source; must-have fields each traceable via `field_sources` |
| `field_sources` | map field→source index | **MUST** for name, address, ring, NAICS | Lightweight: only must-have fields need per-field mapping in v1 |
| `verification_tier` | A/B/C/U | **MUST** | Per §4.1 weakest-must-have rule |
| `last_verified` | date | **MUST** | Date a human/agent actually checked primary fields, not scrape date alone |
| `last_activity_evidence_date` **[v1.6]** | date, nullable | **MUST** (populated by the floor backfill, §6) | The freshest date, as of the record's last verification, for which dated **operating** evidence was in hand — the entity's own live site, a dated filing with active participants, a dated government record of activity, a §4.12 participation harvest, dated press of an operating event. It asserts exactly this and no more: *"activity evidence at least this fresh was in hand at last verification."* It is a **floor, not a last-seen date**: the entity may well have operated later, unwitnessed by us. Legal-existence evidence (a registry's "active" entity status, Ohio SOS standing) never sets or advances this field — existence is not activity (the GroundScape doctrine). The field is monotonic: it advances only on a dated operating observation (recorded, from application, as a `liveness`/`activity` evidence row under §4.13), and never moves backward. At application it is backfilled `:= last_verified` for every organization (derivation and counts in the applying plan), because the campaign's verification standard required the activity check — own site or dated primary evidence — for every verified verdict those `last_verified` dates record |
| `liveness_signal` **[v1.6]** | enum, nullable (empty allowed) | Nice (seeded only per §6) | `operating_evidence` \| `closure_signature` \| `sos_confirmed_closed` \| `sos_active`. A **pre-status instrument**: it records a liveness posture that has been observed but has **not** (yet) become a §4.2 status motion. `operating_evidence` = dated operating evidence observed since last verification, not yet integrated into a verdict. `closure_signature` = the assembled pattern audit 6 named on ORG-002148 — final benefit-plan filing with no successor plan-year filing, own site suspended/dead, no affirmative closure document — a signature that *owes a direct liveness determination*, never itself a closure. `sos_confirmed_closed` = an Ohio SOS (or home-state equivalent) entity record affirmatively showing dissolution/cancellation — the one signal that is itself a primary status witness; setting it obliges the same pass to bring the status motion it evidences (validator V-24 errors on `sos_confirmed_closed` standing next to `status=active` with no motion — the pair is a contradiction, not a posture). `sos_active` = the registry shows the entity legally extant — recorded, where a lane ran the pull, **as legal existence only**: Ohio SOS "Active" means never dissolved, not operating, and this value can never advance `last_activity_evidence_date`, raise a tier, or answer a `closure_signature`. Empty is the normal state: **no signal is asserted for a record no liveness observation has been made on**, and absence of a signal asserts nothing in either direction |
| `monitor_watch` **[v1.6]** | boolean (`true`/`false`), default `false` | **MUST** (column present on every row; `false` unless seeded or set) | Flags the organization for first-check treatment by the daily news monitor (contract in §5 of the lane file / the §4.4 note below). Watch is a **queue flag, not an assertion**: it records that a named reason exists to look at this organization first and often — an open liveness question, a `closure_signature`, a pending settling fact a news event could supply. Setting or clearing it changes no status, no tier, and no date. A monitor hit on a watched organization is a re-verification queue item, never an automatic status change (§5) |
| `created_by` / `created_date` / `last_edited_by` | string/date | **MUST** | Researcher/agent ID for dedupe accountability |
| `certifications[]`, revenue band, key contacts, LinkedIn URL, logos, patent counts | — | Nice | Contacts are a separate, access-controlled table in v2 — do NOT store personal emails/phones in v1 org record |

**Note on the trio as a system [v1.6].** The three fields separate
three things the free-text notes previously blurred: how fresh our
operating evidence is (`last_activity_evidence_date` — a fact about
*our evidence*, not about the company), what an unresolved liveness
observation currently looks like (`liveness_signal` — a posture
awaiting a determination), and where finite monitoring attention goes
first (`monitor_watch` — an allocation, not a finding). A record may
carry any combination the observations support, subject to V-24's
contradiction bars. None of the three ever substitutes for §4.2's
status grammar: status still changes only on a dated, sourced verdict,
and `status_date`/`status_source` remain the closure record when a
determination lands.

**Tier-1 qualifier derivation [v1.6] (binding).** The qualifier marks
the organizations the majors-first doctrine routes verification effort
toward. Each value is derived from data the Atlas already holds, by
exactly one rule:

- **`public_parent`** — `stock_ticker` is non-empty (the org's own
  listing), OR the org holds a `registry_links` row with registry
  `SEC_CIK` (its own EDGAR filer identity) or `SEC_CIK_PARENT_FILER`
  (a subsidiary of a public filer). The value names the *lineage's*
  public status — the org is public or its parent filer is — and
  `tier1_qualifier_basis` distinguishes the three inputs
  (`stock_ticker=…` / `sec_cik=…` / `sec_cik_parent_filer=… (filer
  name)`). `entity_type=corporation_public` and
  `ownership_type=public_company` are cross-check signals only, never
  sufficient and never necessary: at v1.6 birth the first covers only
  5 of the 29 derived orgs and the second is populated on none, so
  either as a rule would silently drop verified majors. A
  `corporation_public` org the derivation misses is a derivation
  warning naming its settling fact (ticker/CIK evidence), not a
  hand-assertion opportunity.
- **`tri_reporter`** — the org holds a `registry_links` row with
  registry `TRI_TRIFID`. No other derivation exists: TRI reporting is
  a facility-, chemical-, and threshold-specific federal fact, and
  inferring it from NAICS, ring, or site notes would fabricate it
  (§4.8's no-speculative-minting doctrine applies unchanged). At v1.6
  birth `registry_links` carries **zero** `TRI_TRIFID` rows, so this
  value ships with a birth count of 0 and activates automatically as
  waves mint TRI links on exact facility matches.
- **`employees_250plus`** — `employee_band_ohio` ∈ {`250-499`,
  `500-999`, `1000-4999`, `5000+`}. The populated band column is the
  **Ohio** band, so the value asserts precisely **≥250 Ohio
  employees** — the footprint PIC can visit and report — and nothing
  about global headcount. A global reading would require a populated
  global band; organizations.csv carries no `employee_band_global`
  column in the data (the §4.4 draft field was never landed as a
  populated column), so no global derivation is taken.
- **`national_footprint`** — the org's held sites with
  `operating_status ≠ closed` span **≥3 distinct states**. The
  threshold is ≥3, not ≥2: in the post-pass-13 tree every multi-state
  org spans exactly {OH, PA} — an Ohio-plus-Pennsylvania footprint is
  regional, and calling it national would misstate 42 orgs. At ≥3 the
  value ships with a birth count of 0 and populates as EDGAR
  Exhibit-21 and majors site builds extend held site coverage beyond
  the OH/PA frame. A closed site is history, not footprint, and does
  not count toward the span (at birth the ≥2/≥3 counts are identical
  under all-sites and non-closed readings — the choice costs nothing
  today and keeps the semantics current-state).

**Scope.** The qualifier lives on organizations.csv only. Ecosystem
records do not carry it — the majors doctrine routes company
verification, and a university or association is not made a "major" by
this flag. Refresh is part of each integration pass: derivations
rerun over the post-pass tree, changed rows are listed in the pass
journal, and V-29 warns — never errors — on drift, because a
mid-pass tree legitimately disagrees with a not-yet-refreshed column.

---

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
| `county_source` **[v1.6]** | enum, nullable | Nice | How this site's `county` was settled: `parcel` \| `physical_address` \| `geocoder_centroid` \| `directory`. **Doctrine:** county settles from the physical address (AGENTS.md §4 — never from the mailing city). Parcel evidence **outranks** a geocoder centroid and a postal/directory city, in that order and without exception: a county auditor/GIS parcel record for the site's situs is the strongest county evidence the Atlas takes. A centroid **never** corrects a recorded county (the §4.5 `geocode_precision` rule, restated for this field: `county_source=geocoder_centroid` is honest only where `geocode_precision ∈ {zip_centroid, city_centroid}` — a centroid-*derived* county is a weak claim and is labeled as one, and a later parcel or address-exact source replaces it, never the reverse). `physical_address` = the county was read from the site's physical street address (address-exact geocode or the address as published for that site). `directory` = the county rests on a directory-class source's address and nothing stronger — a labeled weak claim, set only by per-record adjudication, never derived in bulk from a record's source list. **Blank is an honest unknown, not a defect:** most sites carry no per-fact county provenance in their current record text, and a blank `county_source` asserts nothing about the county's correctness |
| `site_group_id` **[v1.6]** | string, `GRP-######`, nullable | Nice | Campus grouping: sites sharing one physical campus — contiguous or single-address grounds under one **or multiple** operators — carry the same group ID. Minted **only** where an adjudication or primary evidence states that two or more held sites share the campus (the A3 co-location rulings are the model); never inferred from address similarity alone, and never from a shared mailing city. Group IDs are allocated at integration only. A group must contain **≥2 sites at application close** — a singleton group is a validator error (V-33), so a group whose second site is retired loses its ID at the same pass (the surviving site's field is cleared, the ID is never reused). Group members share `city` + `state`. Grouping asserts co-location only: it is not a merge, not an operator claim, and changes no §5.3 analysis — two sites at one address remain two sites, under the operator rule |
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
| `member_or_open_to` | string | Nice |

> **Subtype waiver (owner ruling 2026-10-30; integration pass 15):** a merged-status tombstone row in `ecosystem.csv` that names a `programs.csv` successor record is exempt from the `ecosystem_subtype` MUST above. The tombstone exists so a published org_id keeps resolving (AGENTS.md §3: never delete; ids are never reused); its live substance sits on the successor program row, and forcing a subtype value onto it would fabricate a classification the record no longer carries. The exemption is documented here and in `scripts/validate.py` at V-8; it applies to merged tombstones only — every live ecosystem record still carries a subtype. E.g., association membership criteria, lab access model |
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
| `registry` | enum | `LEI` \| `OHIO_SOS_CHARTER` \| `WIKIDATA` \| `SEC_CIK` \| `SEC_CIK_PARENT_FILER` \| `FRS` \| `TRI_TRIFID` \| `FDA_FEI` \| `EIN_NONPROFIT` \| `UEI` **[v1.4]** (extensible only by dated revision) |
| `registry_id` | string | Verbatim as the registry carries it (charter numbers verbatim incl. leading zeros; CIKs zero-padded to 10) |
| `match_basis` | string | How the match was established, e.g. `gleif_exact_confident`, `wikidata_confident_match`, `edgar_ex21_subsidiary_of_filer:<filer name>` — a guarded no-hit is never recorded as a negative fact |
| `as_of` | date | The date the registry record was retrieved/verified |
**UEI [v1.4].** `UEI` is the SAM.gov **Unique Entity ID** — the
identifier SAM.gov assigns to an entity registered to do business with the
U.S. federal government, and the recipient key on USAspending award
records. `registry_id` carries the UEI verbatim as SAM.gov or
USAspending carries it (§4.8's verbatim rule; no normalization, no
case-folding). A UEI row is minted **only on an exact UEI match**: the
UEI itself — taken from a SAM.gov Entity Management record or a
USAspending recipient record — is the match, recorded in `match_basis`
in the established style (e.g. `sam_exact_uei`,
`usaspending_exact_uei`), with `as_of` = the retrieval date. A name
resemblance, however strong, never mints a UEI row; name matching is how
a candidate is *found*, the shared UEI is how it is *linked* — the same
guarded-no-hit doctrine as the rest of this table applies, and an org
with no UEI row asserts nothing (most Atlas organizations are not
federal contractors or grantees and will never hold one). **Dedupe
purpose:** UEI is the exact join key for USAspending recipient records
(and for UEI-bearing federal award files such as the SBIR award files),
so federal-award discovery and corroboration can key-match instead of
name-matching — the FRS/TRI/FDA mechanics of this table, applied to the
federal-awards source class.

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

### 4.12 Event records **[v1.5]** (`data/events.csv`, `data/event_participation.csv`)

Two tables, one idea: the industry's recurring convenings are an evidence
layer over the organizations the Atlas already holds. Events own **no
ring and no NAICS** — §§1–2 decide what is in scope, and an event row
never makes an organization in-scope. What the layer records is (a) the
qualifying event *series* themselves, and (b) dated, harvested proof
that a held organization exhibited, sponsored, spoke, organized, or
hosted at a specific edition. Series facts live in `events.csv`;
everything about a specific edition lives in `event_participation.csv`,
because per-edition facts exist only where a harvest exists.

#### 4.12.1 Series records (`data/events.csv`) — one row per series, never per edition

| Field | Type | v1.5? | Notes |
|---|---|---|---|
| `event_id` | string, immutable, `EVT-######` | **MUST** | Never reused; allocated at integration only, next-free at application (first allocation `EVT-000001`). A discontinued or merged series keeps its row, tombstoned by `status` per §5.5 — series rows are never deleted |
| `name` | string | **MUST** | The series' current official name as the organizer styles it, **without** edition year or city ("NPE: The Plastics Show", not "NPE2027"; "ANTEC", not "ANTEC 2026 Pittsburgh"). Edition tokens live in `event_participation.edition_year` / `edition_name` |
| `trade_names[]` | string[] | as applicable | Former names and absorbed predecessor series, per the §5.4 rebrand grammar: a renamed-but-continuing series keeps its `event_id` and records the former name here; a series formed by merger records each predecessor here (Global Polymer Summit records the International Elastomer Conference and the International Tire Exposition and Conference) |
| `organizer_org_id` | FK → organizations ∪ ecosystem | nullable | The organizer, when the Atlas holds it (association, chamber, university, publisher). Nullable **by design**: most commercial organizers are out-of-scope companies the Atlas does not hold, and v1.5 creates no organization records as a side effect. An organizer record is created only through the normal §4.7 gate, as its own motion |
| `organizer_name` | string | **MUST** iff `organizer_org_id` empty | The organizer as it styles itself. When the FK is later resolved, `organizer_name` is retained as the as-published styling. Validator V-17 errors when both are empty |
| `event_format` | enum | **MUST** | `expo` \| `conference` \| `technical_conference` \| `summit` \| `meeting_series` — distinguishes floor shows (exhibitor rosters harvestable) from program events (speaker/sponsor lists harvestable) from recurring technical meetings (rosters rarely published; participation rows will be sparse by nature, not by neglect) |
| `cadence` | enum | **MUST** | `annual` \| `biennial` \| `triennial` \| `irregular` — the series' stated rhythm, from the organizer |
| `cadence_note` | string | **MUST** iff `cadence=irregular` | e.g., PTXPO: "annual 2025–2026 editions; organizer states biennial from the 2028 edition" |
| `typical_timing` | string | Nice | Free text only ("early May", "fall, usually September–October"). This is the **only** timing content at series grain: the schema carries **no** speculative date fields — no next-edition date, no edition calendar. Announced edition dates are per-edition facts and ride `event_participation.edition_dates` once a harvest exists |
| `home_city` / `home_state` | string | as applicable | The series' customary home, for fixed series only; **both empty for rotating series** (the rotation is stated in `geography_note`). `home_state` is a USPS code for US series; for international series `home_city` carries the city and `geography_note` the country, `home_state` empty |
| `home_region` | enum | **MUST** | `ne_ohio` \| `ohio` \| `national_us` \| `international` — the §4.4 geography grammar applied to a series: where the series lives, not where one edition landed |
| `geography_note` | string | Nice | Rotation pattern or home-venue note, with **named exemplars only** — editions that actually ran or are announced by the organizer. No speculative future cities |
| `subject_scope[]` | enum[] | **MUST** (≥1) | Class-local vocabulary (this list only; extensible only by dated revision): `plastics_general` · `rubber_elastomers` · `compounding_formulation` · `recycling_circularity` · `composites` · `tooling_molds` · `plastics_processing_technology` · `polyurethanes` · `silicones` · `foams` · `adhesives_sealants` · `cluster_convening` · `coatings_finishing` (added by dated revision 2026-10-30, v1.6.2 — see revision history). This is the field the qualification test reads. The §3 vocabularies are **not** reused: they tag what a company *does*; `subject_scope` tags what an event is *about* |
| `subject_note` | string | Nice | One line: the organizer's own subject statement, as published |
| `event_url` | URL | **MUST** | The series' own site, on the organizer's domain |
| `status` | §4.2 vocab | **MUST** | Series semantics: `active` (series running) · `closed` (discontinued) · `merged` (folded into a named successor — the successor's `event_id` is named in `notes`) · `unknown`. Every non-`active` status REQUIRES `status_date` and `status_source` (§4.2). A single deferred or postponed **edition** does not change series status — note the deferral; status changes when the series itself ends |
| backbone (`status_date`, `status_source`, `sources[]`, `verification_tier`, `last_verified`, `pic_relevance[]`, `created_by`, `notes`) | §4.1/§4.2/§4.3 | **MUST** | Tier grammar at this grain: the organizer's own site/program = A-equivalent; trade press or association directory = B; a lone aggregator listing = C. A series row is never U — a series that cannot reach C is not seeded |

**Backbone fields deliberately not carried, with reasons.** NAICS and
its §2.1 provenance: company-identity apparatus, meaningless for a
series. `processes[]` / `materials[]` / `markets_served[]` (§3): they
tag companies. `county`: county belongs to editions, and editions carry
city/state as harvested — an Ohio edition's county, if ever needed, is
derived at report time from the edition city, never stored. A
`next_edition_date` or any edition calendar: speculative dates rot, and
this schema does not publish plans as facts.

**The qualification test (the named-subject test — binding).** An event
series is created only when **one** prong holds:

- **(a) Named-subject prong.** The series' **primary subject**, as
  stated by the organizer's own name, program, and exhibitor
  composition, is polymers, plastics, or rubber — including the
  schema-recognized subfields: elastomers, silicones, polyurethanes,
  polymeric foams, polymer composites, plastics recycling/circularity,
  compounding/formulation, plastics processing and tooling. This
  mirrors the §4.6/§4.11 named-program test: the subject must be
  **named**, never inferred from who attends.
- **(b) PIC prong.** The series is owned or operated by the Polymer
  Industry Cluster. (PC3 qualifies on this prong; its `subject_scope`
  still records what it actually convenes.)

**Explicit non-qualifiers.** A material-agnostic primary subject —
packaging, medical devices, general manufacturing, general chemicals —
fails prong (a) however large the polymer contingent. A polymer track,
pavilion, or co-located corner inside a general show never qualifies
the parent series; a separately organized, separately named plastics
series is its own candidate. Exhibitor overlap with the Atlas proves
nothing: the test reads the event's subject, not its roster.

**Worked seams (binding precedent, logged in Appendix A at application).**

1. **Pack Expo (PMMI) — OUT.** Primary subject is packaging across all
   materials. It is among the largest US shows and heavily
   polymer-attended, and it is still out: attendance is not subject.
   Its banked 2026 roster keeps its staging role as a discovery and
   corroboration source, unchanged; because no series row exists, no
   participation rows are minted from it.
2. **CAMX (ACMA/SAMPE) — IN.** Composites are polymer-matrix materials
   in this schema's own treatment (§1 Ring 1 counts composites
   fabricators; §2 carries composites-adjacent handling). The
   "advanced materials" tail of the exhibitor mix does not dilute the
   named primary subject.
3. **MD&M West / Plastec West — BOTH OUT, for two different reasons.**
   Plastec West no longer exists as a separately organized series (it
   was folded into the unified MD&M West from the 2026 edition), so
   there is nothing to seed. MD&M West's primary subject is medical
   design & manufacturing, with plastics one sector among several —
   the polymer-corner case, which prong (a) excludes.

Borderline calls are logged in the inclusion log (Appendix A) with the
prong cited; seams stay flagged until the owner rules — a seed row
never settles a seam by landing.

**Dedupe for series (§5 applied).** Match on `event_url` domain, then
normalized series name with edition tokens (year, city, edition number)
stripped, then `trade_names[]`. Co-located siblings are **distinct**
series — the AMI Cleveland umbrella and each named component expo are
separate rows; Foam Expo North America and Adhesives & Bonding Expo
likewise — cross-referenced in `notes` and seeded when first
harvested. Similar names are not the same series: the **Global Polymer
Summit** (Rubber Division, ACS) and the **Global Plastics Summit**
(PLASTICS / S&P Global) are different events that share an acronym;
both are seeded, each noting the other. When in doubt, don't merge.

#### 4.12.2 Participation records (`data/event_participation.csv`) — one row per organization × edition × role

| Field | Type | v1.5? | Notes |
|---|---|---|---|
| `participation_id` | string, immutable, `EVP-######` | **MUST** | Never reused; allocated at integration only |
| `event_id` | FK → events | **MUST** | The series the edition belongs to |
| `org_id` | FK → organizations ∪ ecosystem | **MUST** | The participating organization **as named by the harvest**, resolved to a held record. Participation never creates organization records: a harvested name with no held record stays a staging discovery candidate until the organization passes the normal §4.7 gate, and only then gains participation rows — backfilled from the banked harvest and cited as such |
| `edition_year` | integer | **MUST** | The edition's year, on the harvest's own year basis |
| `edition_name` | string | as applicable | The name the edition actually ran under, when it differs from the series' current name. Predecessor-name editions attach to the successor series row: IEC 2022/2024 editions attach to Global Polymer Summit with `edition_name = "International Elastomer Conference"` |
| `role` | enum | **MUST** | `exhibitor` \| `sponsor` \| `speaker` \| `organizer` \| `host` — exactly one per row; an organization with two roles at one edition carries two rows |
| `role_detail` | string | Nice | As the harvest prints it: booth number, sponsor level, session/track. Verbatim harvest text only, subject to the §6 screen below |
| `edition_dates` | string | as harvested | The edition's dates **as printed by the harvest** ("September 21–24, 2026"). Per-edition facts live here and nowhere else — there is no edition table and no speculative calendar |
| `edition_city` / `edition_state` | string | as harvested | Where **this** edition ran. `edition_state` is a USPS code, or the full country name for international editions. The series' `home_*` fields are never copied down as a substitute: an edition's city comes from the harvest or stays empty |
| `evidence_source_name` | string | **MUST** | The harvest's identity: publication + publisher ("IEC 2024 Official Conference Guide — Rubber Division, ACS"; "NPE2027 exhibitor roster — MapYourShow / PLASTICS") |
| `evidence_source_url` | URL | **MUST** | The list's published location — or the staging manifest pointer when the live location has decayed. Decay is expected; the banked snapshot is the record |
| `evidence_date` | date | **MUST** | The list's own as-of date where printed ("As of Aug. 16, 2024"), else the retrieval date. A pre-show roster's `evidence_date` is its listing date, and the row's `notes` state the roster was still filling |
| backbone (`sources[]`, `verification_tier`, `last_verified`, `created_by`, `notes`) | §4.1 | **MUST** | Tier grammar at this grain: the organizer's own published roster/guide/directory is **A-equivalent for the fact of participation** — it is the primary source for who exhibited; a trade-press republication = B; an aggregator scrape = C. A row below B is not minted: participation is a factual claim, not a candidate |

**The harvest-only rule (binding).**

1. A participation row is created **only** from an actually-harvested
   list in hand — the organizer's published exhibitor roster, show
   guide/directory, sponsor list, or program/speaker list for a
   specific edition — with the list's identity and `evidence_date`
   recorded on the row. Marketing pages, announcements, press
   roundups, social posts, and memory **never** mint rows; they may
   support the series row's own fields. If no list was harvested, the
   edition contributes zero rows, however certain attendance seems.
2. **Snapshot perishability.** Exhibitor rosters decay: endpoints
   empty out after the edition passes and guides go inaccessible. Each
   current edition of a seeded expo is snapshotted into staging
   promptly, with a manifest entry, **before** any minting pass reads
   it. Minting reads the banked snapshot, never the live site.
3. **Refresh-diff.** A re-snapshot of the same edition diffs against
   the prior snapshot; only new or changed names mint or amend rows. A
   name disappearing from a still-filling pre-show roster does **not**
   delete a minted row — the change is recorded in the row's `notes`
   and the row stands until the post-show roster settles. Rosters
   churn; the Atlas records the harvest, not the churn.
4. **Terms-gated lists mint nothing.** A published exhibitor/sponsor
   list is public marketing material by design; an attendee-platform
   list carrying attendees-only / no-solicitation terms is not, and is
   documented in the manifest rather than banked (the GoeShow IEC
   lists are the standing example). When in doubt, document and do
   not bank.
5. **Personal data (§6 applies with full force).** There is **no
   person field in this table by construction**. `speaker` rows attach
   to the speaker's **organization**; where a harvest names individual
   speakers, the organization is the record and the individual's name
   is not transcribed — not into `role_detail`, not into `notes`.
   Exhibitor contact blocks printed in some directories (phone
   numbers, personal emails) are never transcribed; the staging
   tradeshow manifest already flags which banked directories print
   them.

**Uses and limits (binding interpretation).**

- **Activity attestation.** A participation row is dated evidence that
  the named entity was operating, and presenting itself in this
  industry, at the edition date. In a verification packet it may serve
  as **one corroborating leg** — at the tier the harvest earns — for
  the exhibiting entity's activity in that year.
- **Limits.** The exhibitor is often a parent, division, or sales
  organization, **not the plant**: a row attests the named
  organization and says nothing by itself about any site. It proves
  activity, **not scope** — presence never substitutes for the §1/§2
  scope determination, which reads the exhibitor's own words (its
  directory description, its own site) as usual. A row never raises a
  verification tier by itself; it corroborates.
- **Majors-detection signal.** Under the majors-first doctrine,
  exhibiting at a qualifying national event is a Tier-1/2 detection
  signal in a state's majors spine: it **routes** verification effort
  toward the exhibitor. It is a signal — not a tier input, and never
  a verification.
- **Counting.** Participation rows are never headline counts. Reports
  state them as "N organizations with harvested participation at
  \<event\> \<year\>", never as coverage.

### 4.13 Evidence records **[v1.6]** (`data/evidence.csv`)

Until this revision, a record's evidence lived in its free-text
`sources[]` string and its verdict file in staging: adequate for a
human reader, invisible to the validator, and — as the campaign's two
costliest evidence failures showed — capable of carrying a citation
that existed nowhere outside our own files. This section gives the
Atlas a per-claim evidence layer: one row per (record, claim, source)
observation, so that *which source supports which fact, at what
strength, as of when* is data, not prose.

The table is an **evidence layer over** the four record tables, in the
same posture as §4.12's events layer: an evidence row never makes a
record in-scope, never creates a record, and never by itself raises a
verification tier. It records what a lane actually observed.

| Field | Type | v1.6? | Notes |
|---|---|---|---|
| `evidence_id` | string, immutable, `EVD-######` | **MUST** | Never reused; allocated at integration only, next-free at application (first allocation `EVD-000001`). Evidence rows are never deleted; a superseded or refuted observation is answered by a later row (typically `tier_effect=contradicts`, or a fresher `supports_*` row), never by editing the earlier row away |
| `record_table` | enum | **MUST** | `organizations` \| `sites` \| `ecosystem` \| `programs` — the table the evidenced record lives in. People records (§4.9) are **not** an evidence-table class at this revision: their every field already traces to a single cited public page per record, and the class is deliberately out of scope here (see the open questions in the lane file) |
| `record_id` | FK → the table named in `record_table` | **MUST** | `ORG-######` for organizations and ecosystem rows (ecosystem records carry org_ids), `SITE-######` for sites, `PROG-######` for programs. Validator V-22 resolves the FK against the named table only |
| `claim_type` | enum | **MUST** | `existence` \| `activity` \| `scope` \| `address` \| `parent` \| `liveness` \| `code` — exactly one per row; an observation bearing on two claims carries two rows. `existence` = the entity is the entity claimed (legal name / identity). `activity` = the entity performs the claimed primary activity (the §1 test evidence). `scope` = the activity is in-scope polymer work under §§1–2 (the Ring decision's evidence). `address` = a stated address (HQ or site) is the entity's address, county included. `parent` = a stated parent / operator linkage. `liveness` = the entity was operating (or had ceased) at a date. `code` = a stated code (NAICS primary; CIP at program grain) and its §2.1 provenance |
| `claim_detail` | string | **MUST** | Short, specific: which field or fact the row bears on, in the record's own terms ("hq_address + hq_county (Erie)", "naics_primary 326199", "ring_primary 1 via thermoforming on own site", "status active at 2026-10-29"). Never a bare field name when a value is in dispute, and never a narrative — the narrative lives in the verdict file the row's lane produced |
| `source_class` | enum | **MUST** | `own_site` \| `government_filing` \| `registry` \| `directory` \| `press` \| `platform_category` \| `harvest_roster` — the class of the witness, not its prestige. `own_site` = the entity's own domain / own issued document. `government_filing` = a dated filing or government record of fact (Form 5500, TRI, WARN, SEC, court record). `registry` = a registry record keyed by an identifier (EPA FRS, GLEIF, Ohio SOS, SAM.gov, IPEDS/ROR identity records). `directory` = an authoritative directory listing (trade-association member directory, EDO directory, verified Thomasnet-class listing). `press` = dated news / trade-press reporting of a specific fact. `platform_category` = a platform-assigned category or profile label (Google Places category, LinkedIn industry, aggregator classification). `harvest_roster` = a harvested list under §4.12's harvest-only rule (exhibitor / sponsor / speaker roster for a named edition) |
| `source_ref` | string | **MUST** | The witness itself, citable by a stranger: a URL, or a named source plus its identifier where the source is keyed ("EPA FRS registry 110070870004"; "DOL EFAST2 Form 5500, sponsor THE ARTHUR CORPORATION, PY2023, plan 501"). A staging path is admissible **only** in the one case the grep rule below defines (a named raw extract a registry citation resolves into). A reference to our own verdict files, lane notes, or integration journals is **never** a `source_ref` — those are claims about evidence, not evidence (see the grep rule) |
| `observed_date` | date | **MUST** | The date the lane observed the witness — for a filing, the filing's own as-of / period date where the row's force depends on it, with the retrieval date in `notes`; for a roster, the §4.12 `evidence_date` grammar. Never a scrape-batch date alone where the witness carries its own date |
| `tier_effect` | enum | **MUST** | `supports_A` \| `supports_B` \| `supports_C` \| `contradicts` — how this row bears on the record's tier **for this claim**. The class-to-effect ceiling is §4.1's ladder restated per class: `own_site` and `government_filing` may carry `supports_A`; `registry` and `directory` may carry at most `supports_B` (a registry/directory *address* alone caps at `supports_C`, per the settled seam-2 ruling); `press` and `harvest_roster` may carry at most `supports_B` and corroborate rather than carry (a roster row is, per §4.12, A-equivalent *for the fact of participation* — as an evidence row that fact is a `liveness`/`activity` claim, and its effect is still capped at `supports_B` here, because participation attests the named organization, not its plant or scope); `platform_category` may carry at most `supports_C`, and for a `scope` claim carries **no** supporting effect at all (the PMIR rule, below). `contradicts` is class-free: any class may contradict, and an `own_site` contradiction is the strongest refutation the system records |
| `created_by` | string | **MUST** | The lane / researcher ID that produced the observation, in the `created_by` grammar of the record tables |
| `notes` | string | Nice | One line: the observation's posture ("roster still filling at harvest"; "fetch via search-index retrieval of the exact URL; direct fetch HTTP 000 — availability noted, content dated 2024-11-14"). Licensed-source discovery provenance, where it exists, lives **here and only here** (see §5 interplay, below) |

**Backbone fields deliberately not carried, with reasons.** The record
tables' `sources[]`, `verification_tier`, and `last_verified` are not
duplicated onto evidence rows: the row *is* a source, its
`tier_effect` is claim-local rather than record-global, and its
`observed_date` is the verification date for this observation. No
`status` field: an evidence row does not age out — a later row answers
it. No free-text evidence blob: the witness is cited, not copied —
copying source content into the repo is exactly what §5 forbids for
licensed sources and what citation discipline forbids for all sources.

#### Migration posture — the table is born empty **[v1.6]**

`data/evidence.csv` is created at application with its header and
**zero rows**. No legacy evidence is backfilled into it, and the
free-text `sources[]` strings on the existing records are
**grandfathered as they stand** — not rewritten, not parsed, not
re-expressed as rows. The reasons are the campaign's own lessons,
stated plainly:

1. **A backfill would mint citations nobody re-read.** The legacy
   `sources` strings are summaries written at verdict time ("own site;
   Form 5500 sponsor is Huron, OH (PY2023)"), not observation records.
   Mechanically exploding them into rows would manufacture thousands
   of evidence rows whose `observed_date`, `claim_detail`, and
   `tier_effect` were never observed as such — the table's entire
   value is that a row means *a lane stood in front of this witness
   and recorded what it bore on this claim*. A parsed string does not
   mean that.
2. **The lossy direction is the dangerous one.** Several legacy
   strings compress multiple witnesses and multiple claims into one
   line; any deterministic split mis-assigns effects to claims, and
   any non-deterministic split is a re-verification wave wearing a
   migration's clothes. If a legacy record's evidence is ever needed
   at row grain, the honest route is the standing one: a
   re-verification lane that observes the witnesses and writes rows —
   at which point the rows are real.
3. **Nothing is lost by the empty birth.** The legacy strings remain
   on the records, the verdict files remain in staging, and §4.1's
   tier semantics for records without evidence rows are unchanged
   (below). The table disciplines the future; it does not pretend to
   re-try the past.

A record **gains** evidence rows only when a post-application lane
creates or changes it, under the lane-brief contract below.
"Changes" means any field motion, tier motion, or status motion
applied by an integration pass; a purely mechanical pass that touches
no claim (a column addition, a formatting normalization) mints no
rows, and the pass journal says so.

#### The lane-brief contract **[v1.6]**

From application forward, every verification or integration lane
writes evidence rows for every record it creates or changes, and **a
verdict without evidence rows for its must-have claims does not
integrate** — the integrator returns the packet rather than applying
it. The must-have claims, mirroring the §4.7 gate field-for-field, are
the claims a record may not ship unverified:

- **organizations:** `existence` (legal name), `address` (HQ address
  + county), `scope` (Ring / primary activity under §§1–2), `code`
  (NAICS primary with its §2.1 provenance) — plus `activity` **and**
  `liveness` whenever the verdict asserts or retains `status=active`
  (the activity check is a standing rule of the campaign: a registry
  or directory row proves existence, never current operation), and
  `parent` whenever the motion sets or changes `parent_org_id` or an
  operator linkage.
- **sites:** `existence` (the site is the operator's site at that
  address — §5.3's operator rule), `address` (street address +
  county, from the physical address), `scope` (site processes /
  primary activity), `code` (site NAICS primary with provenance),
  `parent` (the `org_id` linkage), plus `activity`/`liveness` on the
  same status condition as organizations.
- **ecosystem:** `existence`, `address` (institution locality +
  county), `scope` — at this grain the named-program test (§4.6): the
  row's witness must be the institution's own naming of the program,
  center, or service.
- **programs:** `existence` (the named program, §4.11's inclusion
  rule), `scope` (program type / specialty as the institution states
  it), `code` where a `cip_code` is set or changed (with its
  `cip_source_type` — and per §4.11, a CIP attribution is data, never
  the `scope` claim's witness).

One row per (claim, witness): a verdict resting on an own site plus a
Form 5500 writes two rows for the claims each witness actually bears
on, not one blended row. Rows are submitted in the lane's packet as a
companion `evidence_rows.csv` fragment; `evidence_id` values are
allocated by the integrator at application, never by the lane
(the standing allocation rule, §4.12's grammar applied here).

#### Tier restatement — §4.1 applied mechanically, where rows exist **[v1.6]**

§4.1's rule — *a record's tier is the tier of its weakest must-have
field* — is restated against evidence rows **for records that have
them**, as follows. Records with no evidence rows keep legacy tier
semantics untouched: their tiers stand on their `sources[]` and
verdict files exactly as before this revision, and no validator rule
in this increment re-grades them.

For a record with evidence rows, consider each must-have claim
(per the contract list above) that carries at least one row:

1. **Supported strength.** A claim's supported strength is the
   strongest `supports_*` effect among its rows, subject to the
   per-class ceilings in the field table (a claim whose only support
   is a `supports_C` row is a C-strength claim, however the lane
   narrated it).
2. **Contradiction cap.** If a claim carries a `contradicts` row
   whose `observed_date` is on or after the `observed_date` of its
   newest supporting row, the claim is **contradicted**: it supports
   nothing, and the record's tier is capped at **C** until a lane
   resolves the contradiction with a fresher supporting observation
   or the record's claim is corrected. A contradicted `existence` or
   `liveness` claim additionally owes a status review — the cap holds
   the tier; it does not silently move `status`, which changes only
   on a verdict (the WARN-is-announcement doctrine applied to our own
   table: a contradiction is an announcement, not an outcome).
3. **Restated tier.** The record's tier may not exceed the weakest
   supported strength among its evidenced must-have claims. Claims
   with no rows do not enter the computation (they are governed by
   the contract prospectively — a post-application record will have
   rows for all of them; a legacy record touched for one claim is
   restated only on the claims its lane evidenced, and the gap is
   visible in the table rather than papered over).
4. **Non-must-have claims never set the tier.** `parent`, `code`
   beyond the primary, and any Nice-field observation corroborate;
   they neither raise nor cap the tier. (NAICS primary *is* a
   must-have claim per §4.7 and does enter, at its evidenced
   strength.)

Validator V-25 (below) enforces clauses 2 and 3 mechanically on the
rows that exist. It asserts nothing about records without rows.

#### The grep rule — a registry citation must resolve **[v1.6]**

A `source_class=registry` row's `source_ref` must **resolve**: it
names an identifier that is found either (a) as a row in a named
extract held in staging under `raw/` (the `source_ref` or `notes`
carries the extract's staging path, e.g. `raw/gov/state_single_oh.zip
→ STATE_SINGLE_OH.CSV`), or (b) in a live registry response the lane
fetched and dated (the response's identifier and the fetch date are
in the row). **A citation found only in our own verdict files is a
phantom and mints nothing**: no evidence row, no tier effect, no
record motion may rest on it. The integrator greps before applying —
an unresolvable registry citation returns the packet, exactly as a
missing evidence row does.

**Worked example (binding precedent — the Cast Nylons rule).** A
site-tier burn-down verdict re-pointed SITE-000463 to Mitsubishi
Chemical Performance Polymers on a single leg: "EPA FRS state extract
lists MITSUBISHI CHEMICAL PERFORMANCE POLYMERS INC, facility MCAM-PLP,
at 4300 Hamann Pkwy, Willoughby, OH (registry 110041216546)". The
pass-12 recheck (`working/cast-nylons-recheck/cast_nylons_verdict.md`,
2026-10-29) applied what is now this rule: the cited staging extract
(`raw/gov/state_single_oh.zip` → `STATE_SINGLE_OH.CSV`) contains **no
occurrence of 110041216546** — the identifier existed nowhere but in
the burn-down's own verdict files — and live EPA FRS facility detail
for that identifier returns verbatim **"No ID matches
110041216546."** The citation was a phantom. The attribution fell;
SITE-000463 was re-pointed to its actual operator (Cast Nylons) on
primary evidence, and the phantom-based organization record was
retired. By contrast, the extract's real MCPP row — registry
**110070870004**, Bellevue, Huron County — resolves in the named
extract and is admissible the day a lane needs it. Whether the phantom
record was deleted inside FRS or mis-transcribed at read time is
unknowable from any reachable source and irrelevant to the
disposition: **a registry entry that cannot be re-read cannot carry a
claim.**

The same discipline applies, in weaker form, to every class: a
`source_ref` that names a witness no second reader could stand in
front of — a verdict file, a lane's summary prose, a search-result
snippet for a page never opened — is a claim about evidence, not
evidence, and mints nothing. (Search previews are not records; the
standing rule predates this section and is not weakened by it.)

#### The platform-category bar — the PMIR rule **[v1.6]**

A `platform_category` row can **never be the sole support for a
`scope` claim**. A platform's category ("Plastic Fabricator" on a
Places listing, an aggregator's industry label) is a discovery lead —
it routes verification effort; it states no fact about what the
entity does. A scope claim evidenced only by platform-category rows
is unevidenced: the record's scope stands on its other witnesses or
it does not stand, and validator V-23 errors on a record whose
evidenced scope rests on platform rows alone. Where a platform
category and the entity's own publications conflict, the own
publications govern, and the category row — if written at all — is
written as the lead it was, with the contradiction carried by the
own-site row's `contradicts` effect on the category's claim.

**Precedent.** PMIR LLC (ORG-000127, North Royalton) entered on a
Google Places primary category of "Plastic Fabricator," was carried
through harvest and a mechanical sweep on that category, and was
released as an in-scope coating/finishing shop in a scope ruling —
before wave 13's packet 11 finally fetched the operator's own site
(verdict W11-0222, 2026-10-29) and found a measuring-instrument
business (custom axial indicator holders; BARCOR gauge distribution)
with no polymer activity anywhere on it. The record was retired out
of scope in the pass-12 close-out, with the lesson recorded on the
record itself: *a directory category is the weakest evidence class
and can never carry a verification against the operator's own site.*
This rule generalizes that sentence from directory categories to the
platform class as a whole, and moves it from a note on one tombstone
to a validator-enforced bar on every future scope claim.

#### §5 interplay — evidence rows never carry licensed content **[v1.6]**

The evidence table is a public table in a public repo, and AGENTS.md
§5's hard line governs it without exception:

- An evidence row **cites a witness; it never reproduces one.** No
  row carries a licensed source's rankings, descriptions, datasets,
  or bulk listing content — in `claim_detail`, in `notes`, anywhere.
- A public, admissible directory (a trade-association member
  directory, an EDO directory, a public registry) may be a row's
  `source_ref` where it is genuinely the claim's witness, at its
  §4.1 class strength.
- A **licensed source of the Plastics News class** (Plastics News,
  Rubber News, D&B, Data Axle, ZoomInfo, and their class, per
  AGENTS.md §5) **can never be a `source_ref` for a load-bearing
  claim** — never the witness a must-have claim, a tier, or a status
  rests on. Such a source's role is discovery: the fact that a lead
  arrived via a licensed source may be recorded in the row's `notes`
  as provenance ("lead via Plastics News plant list; claim witnessed
  by own site"), and the claim itself must be witnessed by a primary
  or public source cited as the `source_ref`, exactly as AGENTS.md
  §5 already requires of every fact entering the repo. A row whose
  only witness is a licensed source is not written; the lane verifies
  against the public witness first, or the claim stays unwritten.
- Validator V-23 carries a tripwire for the named licensed class in
  `source_ref`, in the same posture as §4.9's CRM tripwire for people
  records: the bar is mechanical because the failure mode is known.

---

### 4.14 Relationship records **[v1.6]** (`data/relationships.csv`)

One row per directed relationship between two organization records the
Atlas already holds. The organizations table states identity; this
table states how held identities connect — parentage, succession,
merger, DBA operation, spin-off origin, and non-PIC membership — with
dates and evidence. It exists because the §4.4 columns can each state
only one undated fact per record: `parent_org_id` names one immediate
parent, `successor_org_id` names one successor, and nothing in the
columns can state a DBA relation between two records, distinguish a
merger from an acquisition, carry an effective range, or make a chain
(Eliokem → OMNOVA → Synthomer) traversable as data.

**What this table never does (binding).** A relationship row records
identity history; it never merges, splits, or tombstones anything by
itself. Record creation, merging, and tombstoning happen only through
the AGENTS.md §3 dedupe order and the §5.2 / §5.4 adjudications, in
that order, unchanged by this section. An edge is a *derived view* of
an adjudication that already happened — or, for the table-native types
below, the record of one — never a substitute for it, and never a
reason to create an organization record. **Both endpoints MUST be held
records** (in `organizations.csv` ∪ `ecosystem.csv`, tombstoned
records included — a `closed` / `acquired` / `merged` record is held;
a name with no record is unheld). An unheld endpoint means **no edge**:
the fact waits, carried by whatever field already states it
(`ultimate_parent_name`, a site name, a note), until the endpoint
passes the normal record gate on its own motion — the v1.5
participation posture (§4.12.2) applied to identity.

#### 4.14.1 Fields — one row per directed edge

| Field | Type | v1.6? | Notes |
|---|---|---|---|
| `relationship_id` | string, immutable, `REL-######` | **MUST** | Never reused; allocated at integration only, next-free at application (first allocation `REL-000001`) |
| `from_org_id` | FK → organizations ∪ ecosystem | **MUST** | The subject endpoint; direction per type in §4.14.2 |
| `relationship_type` | enum | **MUST** | `parent_of` \| `successor_of` \| `dba_of` \| `spun_off_from` \| `member_of` \| `merged_into` — exactly one per row. Extensible only by dated revision |
| `to_org_id` | FK → organizations ∪ ecosystem | **MUST** | The object endpoint. `from_org_id ≠ to_org_id` always (V-26) |
| `effective_from` | date, nullable | as evidenced | The date the relationship began (acquisition close, spin date, membership start) **only where a source on the endpoint records states it**. Never the date an edge was minted, and never a tombstone-pass date restated as a corporate date (see the backfill rule for `merged_into`) |
| `effective_to` | date, nullable | as evidenced | The date the relationship ended, where it has ended and a source states it. Empty = current or unknown; the two are distinguished in `notes` when it matters |
| `basis` | string | **MUST** | Short evidence statement: what establishes this edge, in one or two sentences, citing the adjudication (pass, packet, or record note) — e.g. "Derived from ORG-001452.parent_org_id (canonical §4.4 column); PASS 8 set the link; acquisition by ABC Technologies closed 2022-03-02 per the record's description" |
| `source_ref` | string | **MUST** | Pointer to the evidence: the endpoint record(s) and the source on them, or the pass/journal that adjudicated the edge. For generated edges, the generating column + applying pass |
| `created_by` | string | **MUST** | Researcher/agent ID of the applying integrator — edges are minted at integration only, never by a research lane directly |
| `notes` | string | Nice | Chain context, direction caveats (e.g. a dedupe consolidation that is not a corporate merger), deferred-hop notes |

#### 4.14.2 Types and direction conventions (binding)

| Type | Direction (`from` → `to`) | Reading |
|---|---|---|
| `parent_of` | parent → subsidiary | The single directed parent type. "X is a subsidiary of Y" is read as the inverse of the stored `Y parent_of X` edge — **no `subsidiary_of` type exists and none is ever stored** |
| `successor_of` | predecessor → successor | The predecessor record (tombstoned `acquired`) ceased as an independent entity through acquisition and the successor continues its operations (§5.4) |
| `merged_into` | absorbed → survivor | The predecessor record (tombstoned `merged`) was folded into the survivor. Distinguished from `successor_of` by the predecessor's §4.2 status — see the single-source rule |
| `dba_of` | DBA-operating record → legal-entity record | Two **distinct held records** where the `from` record's market identity is a DBA of the legal entity held as `to`. A DBA carried in a single record's `trade_names[]` is **not** an edge (§5.4) |
| `spun_off_from` | spun entity → origin parent | The `from` entity was separated out of the `to` entity (§5.4 spin-offs). Its later sale to a third owner is a separate `successor_of` / parent fact, not this edge |
| `member_of` | member org → association/org it belongs to | Org-to-org membership in a **held** association only. PIC membership is never a `member_of` edge — see the membership rule below |

**The single-source rule (binding).** For parent and successor facts,
the §4.4 columns on organizations.csv are canonical and this table is
a mechanical derivation of them:

- Every non-empty `parent_org_id` on record X generates exactly one
  edge `parent_org_id(X) —parent_of→ X`. Nothing else generates a
  `parent_of` edge, and no `parent_of` edge is hand-edited: a
  correction is made to the column, and the edge regenerates.
- Every non-empty `successor_org_id` on record X generates exactly one
  edge `X —type→ successor_org_id(X)`, where the type follows X's
  `status` mechanically: `acquired` → `successor_of`, `merged` →
  `merged_into`. Reclassifying an edge means re-adjudicating the
  status on the record first; the edge follows.
- Generated edges are recomputed and diffed at each integration pass,
  like the §4.11 rollup: the applying pass regenerates the three
  derived types from the columns and the file must match (V-27).
  `basis` / `source_ref` on a generated edge name the generating
  column and the pass; `effective_from` copies the predecessor's
  `status_date` **only** where that date is a sourced corporate date
  on the record — for the pass-12/13 dedupe consolidations whose
  `status_date` is the tombstone-pass date, `effective_from` stays
  empty and `basis` says so. A consolidation of duplicate records is
  record lineage, and its basis must never be worded as a corporate
  merger of two distinct companies.
- `dba_of`, `spun_off_from`, and `member_of` are **table-native**:
  no column expresses them, so they are authored edges, minted only
  by an integration pass on an adjudicated motion with `basis` +
  `source_ref`. They are never generated, and the generator never
  deletes them.

**Exception — dual-parent joint ventures (named-record, ruling
10A, 2026-10-30).** The single-source rule above assumes one parent.
Chevron Phillips Chemical Company LLC (`ORG-002910`) is owned 50/50
by Chevron Corporation (`ORG-002911`) and Phillips 66 (`ORG-002912`);
neither parent controls it, and a one-parent column value would
misstate the fact. For this record only: `parent_org_id` stays
EMPTY by design, and the two `parent_of` edges (Chevron → CPChem,
Phillips 66 → CPChem, each `effective_from` 2000-07-01 on its own
FY2025 10-K basis) are **authored by hand** as a documented
exception. The edge generator skips this record, and V-27 parity is
computed with CPChem excluded (the validator requires the two
authored exception edges to be present and excludes them from the
column-parity set). This exception is named-record-only and does
not generalize: any future dual-parent JV requires its own owner
ruling and its own named exception here before an edge is authored.

**The membership rule (binding).** PIC membership is governed by
§4.10 and recorded in `data/members.csv`; `members.csv` stays the
membership record for PIC, full stop. No `member_of` edge ever states
PIC membership — among other reasons, PIC itself holds no org record
(the Greater Akron Chamber record is its host, not PIC), so such an
edge would have no honest `to` endpoint. `member_of` is reserved for
membership in a held association or body (an ecosystem
`trade_association` record, a standards body, a consortium) where a
sourced membership fact exists outside the PIC system. At v1.6 birth
the Atlas holds no such sourced facts, so `member_of` ships with
**zero rows** — a scoped, dormant type, not a backfill target.

**Renames and same-record DBAs are not edges (binding).** A rebrand or
true legal rename with no ownership change is one record (§5.4):
`legal_name` updated, former names in `trade_names[]`. A DBA adopted
by a record is the same shape. Neither mints an edge, and no
`renamed_to` type exists — a name is not an organization, and an edge
needs two held endpoints. If a rename ever produces two held records
through a §5 adjudication, that adjudication — not this table —
decides what edge, if any, states it.

**Chains.** Edges compose: a chain is read by following `to_org_id`
into the next edge's `from_org_id` (Eliokem `successor_of` OMNOVA,
OMNOVA `successor_of` Synthomer). No transitive edges are stored —
the direct hop is the only fact asserted, and a hop whose endpoint is
unheld is simply absent, leaving the chain visibly broken rather than
silently bridged.

---

### E.1 Worked example for §4.14 — the DuPont / Qnity fence (insert after the both-endpoints-held paragraph)


> *Worked example — the DuPont / Qnity fence.* DuPont de Nemours'
> separation of its electronics business as Qnity is exactly the kind
> of fact this table exists to state — a `spun_off_from` edge with a
> spin date and a source. It is **not** stated at v1.6. Qnity holds no
> Atlas record, and DuPont's org grain itself is fenced by owner
> ruling (its Atlas presence is plant-grain records whose notes carry
> "parent structure pending owner decision"), so neither endpoint is
> available in the form the edge would need. The seed for this pair is
> therefore zero edges, deliberately: the fence governs, and an edge
> born inside a fence would be an adjudication smuggled in as data.
> The edge mints in the first pass after the fence lifts and both
> records are held through the normal gate — at which point it is a
> table-native authored edge under §4.14.2, with the spin date as
> `effective_from` and the separation source as `source_ref`.

### 4.15 Capability records **[v1.6]** (`data/site_capabilities.csv`)

One row per (site × capability): a dated, sourced claim that **this
site** works in a material, runs a process, or ships a product form,
from the governed vocabulary in §3.6. (The file name is the layer's
name — the *org capability view* is what consumers read; the rows are
site-grain, below.) This layer exists because `processes[]` /
`materials[]` tags carry record-level provenance of mixed class,
including directory assignments; a capability row may rest only on
the company's own disclosure or a government filing, so it can be
trusted at face value in a way a tag cannot.

| Field | Type | v1.6? | Notes |
|---|---|---|---|
| `capability_id` | string, immutable, `CAP-######` | **MUST** | Never reused; allocated at integration only, next-free at application (first allocation `CAP-000001`) |
| `site_id` | FK → sites | **MUST** | The PRIMARY grain. A capability is a fact about a physical site |
| `org_id` | FK → organizations ∪ ecosystem | **MUST** | The site's parent, carried for query convenience. It is **not** independent data: it must equal `sites[site_id].org_id` (validator V-31). A site re-pointed to a new parent (§5.5) takes its capability rows' `org_id` with it at the same pass |
| `capability_type` | enum | **MUST** | `material` \| `process` \| `product_form` |
| `term` | §3.6 vocabulary | **MUST** | Valid only for its `capability_type` (§3.6 table); validator V-30 enforces the pairing |
| `provenance` | enum | **MUST** | `company_disclosed` \| `government_filing` — **only these two, by construction** (see the PMIR rule below) |
| `source_ref` | string | **MUST** | The specific source: URL of the company's capability/products page, or the filing's identity (form, filer, period, item — e.g. "10-K FY2025, Item 1", "FRS facility record <id>") |
| `observed_date` | date | **MUST** | The date the source was read / the filing's period end. A capability is a claim as of this date; the layer keeps no `last_verified` — refresh mints a new row only when the claim changes, and notes the supersession |
| `withdrawn_date` **[v1.6]** | date, nullable | as applicable | The date the source withdrew the claim, where it has; empty = live claim. Withdrawn rows are never deleted and are excluded from the rollup view (owner ruling 2026-10-30) |
| `created_by` | string | **MUST** | Researcher/agent ID, as everywhere |
| `notes` | string | Nice | Grain or scope qualifiers ("compounding is toll-only at this site"), supersession history, queue cross-references |

**The provenance rule (the PMIR rule, binding).** Platform
categories and directory assignments are **forbidden** as capability
provenance — there is no enum value that admits them, so the
exclusion is structural, not a reviewer habit. Origin: pass 12's
PMIR close-out, where a Google Places primary category ("Plastic
Fabricator") asserted a plastics capability that the company's own
site refuted in full; the category was a discovery lead mistaken for
a scope fact. A directory or platform statement may *route* a
harvester to a company's own page; the row is minted only from what
that page (or a filing) says. §2.1's NAICS doctrine is the same rule
in its older form.

**Classification of the two values.** Authorship decides, the
channel does not. `company_disclosed` = the company states it: its
own website/capability statement, its SAM.gov registration, **its
SEC filings — a 10-K Item 1 business description is the company's
own disclosure that happens to travel through EDGAR**, exactly as a
SAM.gov registration *by the company* is `company_disclosed` under
§2.1. `government_filing` = a government record states it: an
FRS/TRI facility record's program description, a state incentive or
permit filing, an agency directory entry written by the agency.
A vendor or directory repeating either is neither — it mints no row.

**Grain rule (the Parker rule applied to capabilities).** Evidence
is attributed to the grain it actually names. A disclosure that ties
a capability to a site (the site's own location/capabilities page, a
filing naming the plant) mints a row for that site. An org-level
disclosure (a 10-K Item 1 segment description, a corporate
capabilities page naming no plant) mints **nothing** by itself: it
waits in the harvest packet until site-level evidence ties the
capability to a specific held site. A diversified parent's
capability is never smeared across its sites — that is the §1
Parker Hannifin split, restated for this layer.

**The org view is derived, never stored.** An organization's
capabilities are the rollup of its sites' rows (SQLite view
`org_capability_rollup`, §4 of the applying instructions). There are
no org-grain rows, no org backfill, and a capability with only
org-level evidence has no representation in this table until the
grain rule is satisfied — its absence asserts nothing (§4.8's
guarded-no-hit doctrine).

**Dedupe.** One live row per (`site_id`, `capability_type`, `term`):
a second source for the same claim strengthens `notes` /
`source_ref`, it does not mint a twin (validator V-31). If a claim is withdrawn by its source, the row is not deleted: `withdrawn_date` records the withdrawal date (owner ruling 2026-10-30: the column ships at birth), `notes` records the circumstances, and rows with a `withdrawn_date` are excluded from the org rollup view.

**Backfill posture.** The table is born **empty** except the bounded
transform specified in the applying instructions (§5.1 of this
prep): existing §3 tags convert only per-record, integrator-
adjudicated, where the carrying record's own sources support
`company_disclosed` / `government_filing` provenance for that tag.
No bulk conversion, at any tier — a record's `verification_tier` is
the tier of its weakest must-have field (§4.1) and says nothing
about a given tag's provenance.

---

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

## Appendix C — Canonical file layout: state shards

*Adopted 2026-10-30 (owner ruling 2026-10-30, "Do it"); applied in integration pass 14, Stage C. A layout revision, not a schema-content revision: no field, vocabulary, or record rule changes meaning.*

## 1. The shard map

The two establishment-scale tables are stored as **per-state shard
files** in `data/`. Every other table stays a **single file**.

| Table | Storage | Files |
|---|---|---|
| organizations | **sharded by HQ state** | `data/organizations_<TAG>.csv` |
| sites | **sharded by physical state** | `data/sites_<TAG>.csv` |
| ecosystem, programs, people, members, registry_links, inclusion_log | single | `data/<table>.csv` |
| events, event_participation (v1.5); evidence, relationships, site_capabilities (v1.6) | single | `data/<table>.csv` |

`<TAG>` is a USPS state code (`OH`, `PA`, … including `DC` and the
territories) or one of two special tags: `INTL` (organizations only)
and `US` (organizations only — the residual shard, §3).

**Lazy creation.** A shard file exists iff it holds ≥1 row. There are
no empty shard files and no placeholder shards for un-landed states.
At migration the non-empty set is: **15 organization shards** (OH, PA,
MI, TX, TN, DE, MO, CO, IN, NC, NY, NJ, KY, INTL, US) and **2 site
shards** (OH, PA) — counts in `migration_manifest.md`. A future state
pass creates its shard files the first time a row lands in them.

**Why the small tables stay single.** The largest single file at
migration is `ecosystem.csv` (128 rows, ~165 KB) — an order of
magnitude below the size that produced the push failures, and these
tables have no natural state key (a program, a link, an event is not
*in* a state the way a plant is). **Revisit thresholds:** a single
file is re-examined for partitioning when it passes **~1 MB or ~2,500
rows**, or when a natural partition key appears. Named watch items:
`event_participation.csv` (a single NPE-scale roster is ~1,700 lines;
revisit at ~5,000 rows) and `evidence.csv` (born empty at v1.6, grows
per lane; revisit at ~10,000 rows / ~2 MB, partition by year if ever).

## 2. The placement function (deterministic, binding)

Placement is a pure function of the record's own fields. It never
depends on when the record was created, on the pass that touches it,
or on how many records share its state — there is no size threshold
and no "sweep small states into the residual" exception (a threshold
would make a record's home time-dependent and break every contract in
§6).

```
org_shard(org):
    st = upper(trim(org.hq_state));  c = upper(trim(org.hq_country))
    if st ∈ USPS:            return st        # includes DC + territories
    if c ∉ {"", US, USA, UNITED STATES}:
                             return "INTL"
    return "US"                               # residual, §3

site_shard(site):
    st = upper(trim(site.state))
    if st ∈ USPS:            return st
    return UNPLACEABLE                        # §2.1
```

- An organization lives in the shard of its **HQ state**; a site
  lives in the shard of **its own physical state**. The two functions
  are independent: a TX parent's Ohio plant is in `organizations_TX`
  and `sites_OH`. Cross-shard foreign keys are normal and expected
  (at migration, `sites_OH` alone holds sites of organizations from
  16 different org shards plus ecosystem records).
- **Tombstones stay in their record's shard.** A closed, acquired, or
  merged record is never re-homed, including when its successor lives
  in another shard (the merged Hankook twin ORG-000167 stays in the
  residual shard; its survivor ORG-000204 sits in `organizations_TN`).
- Ecosystem records are not placed (single file); the 17 sites whose
  `org_id` resolves to an ecosystem record live in their state shard
  like any other site.
- `hq_state` on current data is clean — the only non-USPS value in
  2,430 rows is blank — so the function's fall-throughs are exercised
  by exactly the 22 blank-state rows (19 residual + 3 INTL). A
  non-USPS `hq_state` string (a province code, a spelled-out foreign
  region) falls through to the country test, as written.

### 2.1 Unplaceable sites

Sites have **no residual shard**: a plant is somewhere, and a state we
cannot name is a data defect, not a placement. A site whose `state`
is blank or not a USPS code cannot enter a shard; the validator
errors (V-35) and the record is held out of the pass for correction or
an owner ruling. Current data has **zero** such sites (all 2,669
carry OH or PA). Foreign physical sites are out of scope for the
Atlas today; if one is ever ruled in, it arrives with its own ruling
and an `INTL` site tag defined by that ruling — never by improvisation.

## 3. The residual shard (`organizations_US.csv`)

An organization whose HQ state is unknown *and* whose HQ country is
US or blank lands in `organizations_US.csv`. The residual shard is a
**placement-review queue, not a junk drawer**:

- Every row in it is there because a fact (its HQ state) is missing,
  and the queue's size is reported as a validator warning at every
  pass (V-38) so it can never go invisible.
- Placement is **never** inferred from the organization's sites. (At
  migration all 17 sited residual orgs have Ohio-modal sites; they
  stay residual until an HQ fact is evidenced. The site pattern is a
  review hint, recorded in the migration manifest — it is not a
  placement.)
- A residual row leaves the shard only via the move procedure (§4)
  when its HQ state is evidenced and corrected.

`organizations_INTL.csv` holds organizations whose HQ is outside the
US (at migration: 3 rows — two Belgian, one Norwegian HQ). An INTL
organization's US establishments live in their state site shards
normally (all 3 INTL orgs hold Ohio sites at migration).

## 4. The move procedure (placement correction)

When a pass corrects the fact that determines placement (an org's
`hq_state`/`hq_country`, a site's `state`), the record **moves
shards in the same pass**:

1. Delete the row from the old shard; insert it into the new shard at
   its ID-sorted position (§5). The row's content changes only by the
   corrected fact itself and the pass's normal `last_verified`/notes
   handling — a move is not a re-verification.
2. The pass journal records the move (record ID, old shard → new
   shard, the evidence for the corrected fact). A row for
   `data/inclusion_log.csv` is added when the HQ correction is itself
   a finding (an identity or scope fact), not for a typo-class fix.
3. Only the pass's integrator of record performs moves (§6.2) — a
   move touches two shards and is exactly the kind of write the
   single-writer rule exists to serialize.

A validator placement mismatch is an **error with this procedure
attached** — never a silent auto-move by any tool (§7, V-35).

## 5. Sort order and headers

- Within every shard, rows are sorted by record ID ascending
  (`org_id` / `site_id`), strictly. New rows are inserted at their
  sorted position; a pass that touches a shard closes with the shard
  in sorted order, and the validator enforces it (V-36). (Neither
  monolith is ID-sorted today; the migration imposes the order once,
  and the equality proof in the manifest — not diff review — is what
  carries that change.)
- All shards of a table carry **byte-identical headers**, inherited
  verbatim from the monolith at migration and thereafter changed only
  by a schema revision applied to every shard in one pass. A
  divergent shard header is a validator error (V-34).
- Shards are files of record lines in the repo's existing CSV dialect;
  no quoting, encoding, or line-ending convention changes.

## 6. Process contracts under shards

### 6.1 ID allocation — global, unchanged in substance

Record IDs remain **global across all shards** and are never reused.
The next-free rule survives verbatim, restated for the layout: before
allocating, the integrator scans **every shard of the table** (plus
the tombstones those shards contain — which is all of them, since
tombstones stay home) and takes max-numeric-suffix + 1, verified
against the full ID set. At migration the maxima are ORG-002774 and
SITE-002860 against 2,430 / 2,669 rows — the ID space is sparse by
design, which is why the scan, not a row count, is the rule.

### 6.2 Writers — one writer per file; shards parallelize, shared files don't

The single-writer rule is restated **per file**:

- Two integrators **may** hold **different state shards** concurrently
  (e.g., an SC pass and a PA pass in flight at once), because shard
  files are disjoint by construction. Each integrator owns its shards
  exclusively for its pass.
- The **shared files** — ecosystem, programs, people, members,
  registry_links, inclusion_log, events, event_participation,
  evidence, relationships, site_capabilities — have exactly **one
  designated writer per pass window**: the pass integrator of record.
  A shard writer who needs a shared-file change hands the motion to
  the integrator of record; they never write a shared file directly.
- **ID allocation is serialized** through the integrator of record,
  who runs the tree-wide scan (§6.1) and issues ID blocks to shard
  writers. No lane and no shard writer self-allocates.
- **Moves (§4) and dedupe adjudications** are performed only by the
  integrator of record.
- Lanes (verification, scouts, audits) write **no** data file, as
  always — they produce verdicts against frozen extracts (§6.3).

### 6.3 Frozen extracts

A lane's frozen extract is a snapshot of the whole `data/` directory
(all shards + all single files) taken at a named repo commit, plus an
extract manifest listing **each file, its row count, and its SHA-256**.
Lanes read the extract, never the live tree. A verdict that cites a
record cites its ID; the ID is shard-independent, so verdicts survive
re-sharding and moves without rework.

### 6.4 Dedupe at verdict time — restated against shards

AGENTS.md §3's searches run against the **union of all shards**:

1. website domain — across all `organizations_*.csv`;
2. normalized name — across all `organizations_*.csv`;
3. street address — across all `sites_*.csv` (one address = one site,
   owned by the operator);
4. trade names / notes / `successor_org_id` — across all shards and
   the ecosystem file.

"In doubt, don't merge" is unchanged. A search that names one shard
is a scope statement, never a dedupe.

### 6.5 Push mechanics and the size budget

Observed data points (campaign record): a ~4.2 MB push body landed
(pass 12); a ~5.43 MB body was refused with HTTP 413 (pass 13, first
attempt). The cap lies between; the working budget is therefore
**≤ 4 MB of file content per push**, planned from the pass manifest,
not discovered at push time.

- A state pass pushes **its touched shards + its touched shared
  files**. At migration sizes, a new-state pass (SC and its peers)
  pushes well under 0.5 MB. The worst steady-state case is an
  Ohio-only pass: `organizations_OH` (~2.16 MB) + `sites_OH`
  (~1.58 MB) = ~3.74 MB, ~3.9 MB if it also touches ecosystem —
  inside budget with thin headroom, so an Ohio pass whose manifest
  totals > 4 MB splits **by file class** (organization shards, then
  site shards, then shared files + docs), each push separately
  approved and read back, per campaign rule AGENTS.md §2.2.
- Read-back (campaign rule §2.2c) is **per pushed file**: every shard
  in the push is read back from the remote and verified byte-identical
  to the validated local copy. The pass's read-back checklist
  enumerates shard files by name — "the data files" is not a
  checklist entry.
- The one-time pass-14 push is split three ways by construction
  (runbook §E): ~2.9 MB + ~2.2 MB + <1 MB.

### 6.6 What consumers see

The **shards are canonical**; merged files are **generated**. The
SQLite builder (§7) unions the shards into the same downstream
tables (schema unchanged) and additionally emits merged exports —
`organizations_all.csv`, `sites_all.csv` (union, globally ID-sorted)
— into `build/` alongside `polymer-atlas.db`, as release artifacts.
Merged exports are never committed to `data/`; the validator treats
their presence there as an error (V-37), because a committed merged
file is a second canonical source waiting to drift.

## 7. Validator and builder changes (specification)

Validator rule numbers below are **provisional**: the applied
sequence runs to V-16, v1.5's draft takes V-17–V-21, v1.6's draft
takes V-22–V-33. The shard rules take the next free numbers at
application (V-34+ on the current drafts) and renumber without
semantic change if the applied set differs.

**`scripts/validate.py`**

- *Discovery.* Organizations and sites are loaded by glob
  (`data/organizations_*.csv`, `data/sites_*.csv`), each row carrying
  its source filename so every message keeps the existing
  `file:line ID` shape with the real shard name. A file matching
  `data/organizations_*.csv` whose tag is not a USPS code, `INTL`, or
  `US` is an error; a `sites_*.csv` tagged `INTL`/`US` is an error.
- *Union semantics.* Every existing check (V-1…V-33 as applied) runs
  over the union of shards, unchanged: ID uniqueness is global (a
  duplicate ID in two shards is the same error as a duplicate in one
  file), FK universes are `organizations(union) ∪ ecosystem`, member
  flag cross-checks, program rollups, and successor checks all read
  the union.
- *V-34 — shard set & headers.* Every shard of a table carries the
  identical header; the header equals the schema's field set for that
  table.
- *V-35 — placement conformance.* Every organization row's
  `org_shard()` equals its file's tag; every site row's
  `site_shard()` equals its file's tag. Mismatch is an **error**
  naming the record and the §4 move procedure. A site with a blank or
  non-USPS `state` is an error here (unplaceable, §2.1).
- *V-36 — sort.* IDs strictly ascending within each shard.
- *V-37 — monolith tripwire.* `data/organizations.csv`,
  `data/sites.csv`, and any `*_all.csv` in `data/` must not exist.
- *V-38 — residual visibility (warning, never blocks).* The summary
  reports the `organizations_US.csv` row count as the
  placement-review queue size, on the V-13 flagged-exception pattern.
- *Reporting.* The closing summary line reports **per-shard counts**
  plus the union totals, in the existing format's spirit:
  `organizations: OH 1781, PA 601, …, US 19 (2430 total)`.

**`scripts/build_sqlite.py`**

- The `organizations` and `sites` tables are built from the shard
  glob union; every other table from its single file, as today. The
  downstream SQLite schema (tables, views, indexes) is **unchanged**
  — `ohio_sites`, `pic_members`, and `institution_programs` read the
  unioned tables exactly as before.
- After the `.db` build, the builder writes the merged exports
  (§6.6) to `build/` and prints per-shard row counts so a build log
  shows the union's composition.

## 9. Decisions taken at adoption (for the record)

1. **Every non-empty org shard is created at migration** (15 files,
   including six one-row shards). The alternative — sweeping
   sub-threshold states into `organizations_US` until the state
   "lands" — was rejected: it makes placement depend on the calendar,
   which breaks the move procedure, frozen extracts, and the
   validator's placement check. Tiny shards cost nothing; a pure
   placement function is worth more than a tidy file listing.
2. **Concurrent integrators on disjoint state shards: allowed**,
   under the three serializations of §6.2 (shared files, ID
   allocation, moves — all through the integrator of record).
3. **Sites get no residual and no INTL shard** (§2.1), organizations
   get both.
4. The split carries **no schema version bump**; it is a layout
   appendix adopted by the same owner ruling that ordered it.

## Revision history

- **v1.0 — 2026-10-28.** Initial design (rings, NAICS map, §3 vocabularies, record schema, resolution rules).
- **v1.1 — adopted 2026-10-29 as part of the combined v1.2 revision.** Tier 1: `street_address` on sites; site `latitude`/`longitude` + `geocode_precision`; external registry-ID link table (§4.8); `year_founded`; `stock_ticker`. Tier 2: `employee_band`, `ownership_type`, `certifications` on organizations. (Decision memo 2026-10-29 §1, option (a).)
- **v1.2 — 2026-10-29 (this text).** People records — professors only, public facts only, CRM never a source (§4.9); program/office record grains on ecosystem (§4.6 extension) with the §3.5 research-areas supplement under the §3-first rule; PIC membership fields + spanning member table, website-public only (§4.10); `pic_relationship_stage` retired from the public files (§4.3). (Repo change proposals S1–S4; connections trio approval 2026-10-29; Phase A calibration fixes integrated: conditioned `credential_types`, `admissions_status`, the engagement-mode grain rule.)
- **v1.3 — 2026-10-29 (drafted; dated at application).** §4.6 drift fix: `polymer_program_url` column lands in ecosystem.csv with validator rule V-13 (MUST-if-claimed enforced at institution grain, with a dated pending list for unsourced claims); `ipeds_unitid` + `ror_id` identifier columns on university_college rows (V-14; identity join keys only — IPEDS/ROR assert identity, never program existence). Program records move from ecosystem grain rows to `data/programs.csv` (§4.11; V-15/V-16), adding `cip_code` with provenance, `level`, `unit_department`, and IPEDS completions fields to the v1.2 program grain; `program_type` gains `lab_facility` and `course` (apprenticeship retained); the `polymer_program_name`/`polymer_program_url` fields become the generated rollup of an institution's program rows; the inclusion rule is restated with the Lakeland rule (a CIP attribution is never program evidence); §4.9's `program_org_id` re-points to the programs table.

- **v1.4 — 2026-10-29 (owner ruling, consolidated batch "all as
  recommended"; applied in integration pass 12).** Two increments, no new
  fields and no data population. (1) The `ownership_type` vocabulary
  (§4.4) is **adopted**: the ten values carried as proposed since v1.1 are
  now the binding enum — `public_company` | `private_company` |
  `private_equity_portfolio` | `family_owned` | `employee_owned` |
  `nonprofit` | `government` | `academic` | `cooperative` | `unknown` —
  control, distinct from `entity_type` (legal form), set only from a
  primary/authoritative source and never inferred from size or name. The
  validator's `OWNERSHIP` set already enforces exactly these values; this
  revision makes the schema text catch up to the validator. (2) `UEI`
  (SAM.gov Unique Entity ID) is added to the §4.8 `registry_links`
  registry enum, with the validator's `REGISTRIES` whitelist gaining
  `UEI` in the same pass (§4.8 design note). Purpose: exact-key matching
  against SAM.gov entity registrations and USAspending recipient records,
  replacing name matching for federal-award corroboration. **No UEI rows
  are minted by this revision** — population is later wave work, only on
  an exact UEI match, and a guarded no-hit is never recorded as a negative
  fact.

- **v1.5 — 2026-10-30 (owner ruling 2026-10-30; applied in integration pass 14, Stage A).** Events layer — §4.12 adds `data/events.csv` (series grain) and `data/event_participation.csv` (harvested participation), the named-subject qualification test, the harvest-only rule, and validator rules V-17–V-21. No existing table, field, or vocabulary changes. Seeded with 27 series and 55 harvested participation rows; the A6-16 rider (audit 6) re-keys PROG-000014/PROG-000015 to Kent State ORG-000503 and clears ORG-002095's polymer_program claim. The version header moves to v1.6 at this pass's Stage B, which applies the v1.6 increment in the same pass; both revision entries are preserved.

- **v1.6 — 2026-10-30 (owner rulings 2026-10-30 — battery of 13 items, all approved; applied in integration pass 14, Stage B).** Integrity & capability increment — §3.6 capability vocabulary (57 terms); §4.4 liveness trio (`last_activity_evidence_date` floor backfilled on all 2,430 organizations; 1 `closure_signature` seed + 2 `monitor_watch` seeds) and the derived Tier-1 qualifier (birth union 71; `tri_reporter` and `national_footprint` dormant at 0); §4.5 `county_source` (parcel 32 / physical_address 753 / blank 1,884) and `site_group_id` (2 groups, 5 sites); §4.13 evidence records (`data/evidence.csv`, born empty; V-22/V-23/V-25, the tier restatement an error from day one); §4.14 relationship records (`data/relationships.csv`, born 54 = 53 generated + the authored GEON `spun_off_from` edge); §4.15 capability records (`data/site_capabilities.csv` — owner-renamed from the prep's org_capabilities.csv — born from the adjudicated tag transform WITH the `withdrawn_date` column); validators V-22–V-33. The pass's Stage C splits organizations.csv / sites.csv into per-state shards (Appendix C).
- **v1.6.1 — 2026-10-30 (owner rulings 2026-10-30 — pass-16 battery items 7A and 10A, all as recommended; applied in integration pass 16).** Micro-revision, two items only. (1) §3.6: `carbon_black` added as a NEW material capability term (vocabulary 57 → 58 terms; material 24 → 25) — §3.2 carries no carbon black string, and the class is produced and specified at plant grain by Cabot/Orion-class producers. `fumed_silica` was considered in the same ruling and NOT approved; it stays a §3.6.3 queue item. (2) §4.14: the CPChem dual-parent exception is documented (named-record exception for ORG-002910: `parent_org_id` empty by design, two hand-authored `parent_of` edges from the 50/50 parents Chevron ORG-002911 and Phillips 66 ORG-002912, generator skip, V-27 parity computed with CPChem excluded and the exception edges required present). No other table, field, or vocabulary changes.
- **v1.6.2 — 2026-10-30 (owner ruling 2026-10-30 — events-pass battery item ii, as recommended; applied in the events battery-release pass).** Micro-revision, one item only. §4.12.1: `coatings_finishing` added to the `subject_scope` vocabulary (12 → 13 values) — the list carried no coatings value, and the two coatings series seeded in the events pass (American Coatings Show & Conference EVT-000037; International Symposium on Coating Science and Technology EVT-000042) were provisionally mapped to `compounding_formulation` with the gap flagged in their `subject_note`s; both rows flip to `coatings_finishing` in the same pass and the flags are replaced with dated ruling notes. The validator's `SUBJECT_VOCAB` gains the value in the same pass. No other table, field, or vocabulary changes.
