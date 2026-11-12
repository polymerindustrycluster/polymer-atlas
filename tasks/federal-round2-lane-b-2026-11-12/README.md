# Federal centers round 2 — verification lane B packet: DOE EFRCs/Hubs + NSF Engines

**Date:** 2026-11-12 · **Lane:** B (DOE EFRCs/Hubs + NSF Engines) · **Mode:** PACKET ONLY — no canonical writes; nothing under `data/` was edited. Input packet: `~/workspace/polymer-atlas-staging/working/wave3-2026-11-12/federal-round2-engines-doe.md`. Atlas data basis for anchors/org IDs: `~/workspace/atlas-p2-2026-11-12/data/` (read-only).
**Grain rules applied (owner-decided 2026-11-12):** EFRC rows anchor at the LEAD institution as center rows (MRSEC precedent, tier B); Engines get NO standalone rows — they are recorded as evidence on the anchor institutions' existing program rows.
**Verification standard:** each center verified on its OWN pages (center site, or the host institution's own pages where the center has no standalone site); award records were used as discovery context only, never as witnesses. Effort cap ~6 fetches per organization respected (max used: 3).
**Paid API calls: 0** (no Tavily/Exa/Firecrawl; all sources are the centers' own free web pages plus free web search).

## Counts (unit + filter)

| Population | Assigned | VERIFIED | Currency check (already carried) | Held / gated |
|---|---|---|---|---|
| DOE EFRC screen-ins from round-2 lane B | 10 centers | **9** (rows drafted, incl. CPI) | 1 (iCOUP) | CPI row verified but integration **HELD** (institution mechanics) |
| DOE Hub screen-in (ESRA, marginal) | 1 hub | **1** (scope verdict) | — | Row drafted but integration **gated** on hub = center grain ruling (not covered by the decided EFRC/Engines rules) |
| NSF Engines Type-2 (NCTISE) | 1 evidence entry | **1** (2 evidence rows drafted on PROG-000118) | — | — |
| NSF Engines Development Awards | 5 candidates | **4** with an anchor row + own-page scope witness | — | 1 with **no anchor** (Vytal — lead absent from the Atlas in every layer) |

Deliverable rows: `proposed_rows.csv` = **10 drafted center rows** (9 EFRC + ESRA); `proposed_evidence.csv` = **27 proposed evidence rows** (18 EFRC existence/scope, 2 ESRA, 1 iCOUP currency, 2 NCTISE, 4 development-award candidates).

---

## 1. DOE EFRCs — verdicts (9 VERIFIED, 1 currency check)

All nine new centers are `program_type=center`, tier B, anchored at the lead institution, per the decided grain rule. Full drafted rows in `proposed_rows.csv`; existence + scope evidence pairs in `proposed_evidence.csv`.

| Center | Lead (org ID) | Verdict | Polymer scope, verbatim from its own pages | Witness URL |
|---|---|---|---|---|
| **Center for Plastics Innovation (CPI)** | University of Delaware (ORG-003896) | **VERIFIED — integration HELD** (see §4) | "To develop energy-efficient, selective, and tolerant chemo- and bio-catalytic and synthetic pathways to valorize diverse plastics waste streams and dramatically increase circularity." | https://cpi.udel.edu/about-the-center-for-plastics-innovation-2/ |
| **FaCT** — Fast and Cooperative Ion Transport in Polymer-Based Electrolytes | Oak Ridge NL (ORG-002814) | **VERIFIED** | "To understand and control fast, correlated ion and proton transport at multiple length and time scales in polymer-based electrolytes to overcome the current limitations of energy storage and conversion technologies" | https://fact-efrc.ornl.gov/ |
| **M-WET** — Center for Materials for Water and Energy Systems | UT Austin (ORG-004651) | **VERIFIED** | "M-WET's team comprises 22 leading membrane scientists, polymer scientists, polymer physicists…"; "the highest Li+/Na+ selectivity ever reported for a polymer" | https://mwet.utexas.edu |
| **AIM for Composites** | Clemson (ORG-004639) | **VERIFIED** | "The mission of this EFRC is to build an AI-enabled inverse design approach for fundamental understanding and integrated material-manufacturing design of advanced polymer composites." | https://www.aimforcomposites.com/ |
| **REMAT** — Regenerative Energy-Efficient Manufacturing of Thermoset Polymeric Materials | UIUC (ORG-004657) | **VERIFIED** | "advance the science and transformative, circular strategy of energy-efficient manufacturing of thermoset polymers and composites"; mission adds "thermoset polymeric and composite materials with programmed end-of-life" | https://remat.illinois.edu/ |
| **SPECS** — Center for Soft PhotoElectroChemical Systems | U Arizona (ORG-004720) | **VERIFIED** | "The SPECS vision is to use low-cost, highly scalable, durable polymer (plastic) materials for energy conversion and storage technologies"; "Pi-conjugated polymers are low cost, easily scalable and printable semiconductors" | http://specs.arizona.edu/ |
| **CABES** — Center for Alkaline-Based Energy Solutions | Cornell (ORG-004633) | **VERIFIED** (URL unsettled, see §5) | Cornell's own page: "Current fuel cells and electrolyzers… use polymers to transport ions through the cell… Cornell chemists are working on alternatives, such as anion exchange membranes"; the center's own DOE technical summary (Science Driver 2): "Systematic synthesis [of] alkaline exchange membranes (AEMs), correlated ionomers…" | https://chemistry.cornell.edu/news/cornell-chemists-tackle-climate-change |
| **CHiPPS** — Center for High Precision Patterning Science | Lawrence Berkeley NL (ORG-004640) | **VERIFIED** (materials-core; weakest-link note §5) | Own About page: "Poorly controlled diffusion in reaction fronts with heterogeneous photoresists"; "design rules to build self-assembling systems… to perform as lithographic materials below 10 nm"; host lab's own CHiPPS article: "advancing bio-mimetic, sequence-specific polymers"; "highly customizable block copolymer materials for lithographic features" | https://chipps.lbl.gov/about-chipps/ |
| **CSSAS** — Center for the Science of Synthesis Across Scales | U Washington (ORG-004686) | **VERIFIED** (materials-core; weakest-link note §5) | Center's own DOE EFRC overview/research plan: "CSSAS will predict how the chemistry and sequence of inorganic, polymer and protein building blocks gives rise to ordered phases"; its DOE public abstract: "The cross-cutting synthesis of protein, polymeric and inorganic building blocks… completes our vision for CSSAS" | https://www.cssas-efrc.com/about-cssas |
| **iCOUP** — Institute for Cooperative Upcycling of Plastics | Ames NL (ORG-002818), carried as **PROG-000052** | **CURRENCY CHECK PASS** — no new row | Own page live at 2026-11-12: "We are funded by the U.S. Department of Energy's Office of Science, and we are an Energy Frontier Research Center… We combine knowledge and expertise in polymers, catalysis, materials, spectroscopy and scattering, and theory" | https://www.ameslab.gov/institute-for-cooperative-upcycling-of-plastics-icoup |

Notes on the drafted rows:
- **Class periods carried in every row's notes** (per round-2 flag 7): FaCT, AIM, REMAT, SPECS, CABES, CHiPPS, CSSAS and M-WET carry 2026-ending classes and are subject to the Feb 2026 DOE recompete FOA — read as *current on the Oct 2024 roster, renewal pending*, not closed. CPI and iCOUP run 2020–2028.
- REMAT, SPECS and CSSAS would be the **first program rows** at their hosts (UIUC, U Arizona, U Washington ecosystem rows currently carry `polymer_program=false`); CHiPPS would be LBNL's first program row (its ecosystem row claims `polymer_program=true` via the Molecular Foundry rollup with 0 rows). Ecosystem rollups recompute at integration.
- Partner lists in the row notes are the round-2 packet's (agency-level) except where the center's own page restated them (M-WET, CHiPPS, CSSAS, CPI); they are notes, not evidenced claims.

## 2. DOE Hub — ESRA

**Energy Storage Research Alliance (ESRA)**, DOE Energy Innovation Hub (est. Sep 2024), lead Argonne National Laboratory (ORG-002816).

**Verdict on the assigned question (polymer-electrolyte scope on its own pages): VERIFIED.** The settling witness named by the round-2 packet — polymer electrolytes/materials as a *named thrust* — is met. ESRA's own Research page (https://energystoragera.org/research/):

> "ST 2: Enabling soft matter omics — *Purpose*: Bridge the knowledge gap and uncover new mechanisms, in the poorly understood **organic polymeric electrode materials**, to capture the dynamic behavior of **soft ion conductors**, electro-chemo-mechanical phenomena at longer length and time scales, and interfaces."

Its homepage's impact list adds "enhance transport of ions in solids and soft matter by an order of magnitude" and "organic soft materials that enable multi-electron redox energy storage". This is materially stronger than the marginal screen-in basis (which rested on ESRA-funded output); the polymer scope is now stated in the hub's own thrust structure.

**Integration gated, not held for evidence:** a center row is drafted in `proposed_rows.csv` (disposition `VERIFIED_SCOPE__ROW_DRAFTED_GRAIN_HELD_HUB`), but ESRA is a Hub, not an EFRC, and the 2026-11-12 grain ruling decides EFRC rows and Engines evidence only. The row must not land until the owner confirms hub = center grain.

## 3. NSF Engines — evidence only (no rows)

### 3.1 NCTISE (Type-2) → evidence drafted on PROG-000118

**Anchor row: PROG-000118, Fiber and Polymer Science** (degree, Wilson College of Textiles, NC State, ORG-002851) — the carried Wilson College program row named by the round-2 packet. Two evidence rows are drafted in `proposed_evidence.csv`:

1. **Engine's own site** (https://nctise.org/), claim `scope`: "Cutting‑edge materials research, from high‑performance fabrics to renewable fibers"; "Commercialization of regenerative and circular business practices" — and the homepage's own captions place Engine work at "the Textile Protection and Comfort Center at the Wilson College of Textiles" and "NC State's Knitting Laboratory". The Engine's stated mission (round-2 packet, NSF portfolio text): environmentally sustainable textiles, smart textiles/wearables, cutting landfill textile flows, textile-to-textile circularity.
2. **NC State's own site** (NC State Extension, https://www.ces.ncsu.edu/news/turning-to-fiber-hemp-to-revitalize-agriculture-and-textiles/), claim `scope`: "That's where the National Science Foundation's Textile Innovation Engine of North Carolina comes into play. A cooperative effort between NC State University, **its Wilson College of Textiles**, Western Piedmont Community College, Manufacturing Solutions Center, Gaston Textile Technology Center, NCIdea and the N.C. Department of Commerce…"

The Engine is led by The Industrial Commons (nonprofit, Morganton NC — no Atlas record in any layer); NC State's Wilson College leads its R&D per the NSF award abstract (discovery context only, not cited as a witness). Naming note: partner pages now style the Engine "Textile Innovation Engine of North Carolina"; NCTISE remains the NSF award name.

### 3.2 Development Awards (Type-1) — evidence-only candidates

For each: the anchor institution's carried row the evidence would attach to + the scope quote from the institution's/coalition's own pages. One candidate evidence row per witnessed candidate is included in `proposed_evidence.csv` (disposition `CANDIDATE_EVIDENCE_ONLY`); no program rows are drafted for any Engine.

| Candidate | Anchor row | Scope quote (own pages) | Witness |
|---|---|---|---|
| **CWRU — "Advancing Manufacturing Technologies (OH)", Award 2302943** | **PROG-000117** Macromolecular Science and Engineering (alt: PROG-000028 CAPP), CWRU ORG-000502 | "Case Western Reserve University is the lead partner on a new Regional Innovation Engines Development Award… Phase I planning efforts will focus on… **alternatives to petroleum-based plastics, packaging, and biodegradable byproducts**. We seek to reduce embodied energy… all while transitioning to material circularity" | https://case.edu/issacs/programs/nsf-engines-advancing-manufacturing-technologies |
| **M-SPIRE — Midwest Sustainable Plastics Innovation Regional Engine, Award 2315247** | **PROG-000072** IPRIME (alt: PROG-000104 MSE), U Minnesota ORG-002855 | "The Midwest Sustainable Plastics Innovation Regional Engine (M-SPIRE), a U of M-led effort to drive the global transition to sustainable plastics… M-SPIRE would be operated out of the University of Minnesota through the College of Science and Engineering"; "Sustainable plastics must be the future, and M-SPIRE will drive innovation in this area by promoting an ecosystem to broadly facilitate translation of new technologies that promote a circular plastics economy" (Hillmyer, also director of the NSF Center for Sustainable Polymers at UMN) | https://wrc.umn.edu/news/great-lakes-renew-finalist ; https://cse.umn.edu/chem/news/m-spire-one-two-umn-affiliated-projects-named-finalists-nsf-regional-innovation-engine |
| **SHAPE — Sustainability Hub for an Alternative Packaging Ecosystem, Award 2314459** | **PROG-000066** School of Packaging (alt: PROG-000073 C3PS), Michigan State ORG-002852 | MSU's own news: "the foundation is leading the development of the Sustainability Hub for an Alternative Packaging Ecosystem, or SHAPE, initiative. Funded by a $1 million National Science Foundation Regional Engines planning grant, SHAPE is reimagining how packaging materials are recycled and reused." The coalition's own program page adds: "SHAPE is powered by the NSF Engines Development Award (Award ID 2314459)… a coalition of leading organizations, including the Michigan State University Research Foundation, Michigan State University, Ohio State University, Resource Recycling Systems (NextCycle), and Michigan's Department of Environment, Great Lakes, and Energy (EGLE)" | https://msutoday.msu.edu/news/2024/12/the-msu-research-foundation-helps-turn-spartan-discoveries-into-impact ; https://www.nextcycle.co/packaging |
| **CONFIR / NNE-PROMISE — U Maine** | **PROG-000138** Composite Materials and Structures (certificate) — UMaine's **only** carried program row, U Maine ORG-004675 | UMaine CRSF's own page: "NSF ENGINES Development Award — NNE-PROMISE: Northern New England Precision Forest Management & Advanced Forest Bioproducts Engine… Environmental Impact: Carbon negative production pathways; **Replacement of petroleum plastics**; **100% Biodegradable products**" | https://crsf.umaine.edu/confir/ |
| **Vytal Plant Science Research — "Advancing Industrial Hemp Technologies" (PA), Award 2308676** | **NONE EXISTS** — the lead (Vytal Plant Science Research, Hazleton PA nonprofit) has no record in any Atlas layer; no anchor row can be named | NSF's own rollout slides (agency framing; the entity's own site was not used as a witness in this lane): "Develop a new industrial hemp-based supply chain… Create biobased products for use in green building construction, **packaging**, foods, nutraceuticals, **textiles**, renewable energy, and land remediation." | https://nsf-gov-resources.nsf.gov/files/NSF_Engines_High-Level-Rollout-Slides-with%20MI%20UP%202.15.2024-508.pdf |

Caveats carried for the four witnessed candidates:
- **CONFIR's anchor fit is institutional, not program-grain**: PROG-000138 is a composites certificate; CONFIR/NNE-PROMISE is a forest-bioproducts coalition (CONFIR led by the Northern Forest Center per UMaine's own annual-report page; NNE-PROMISE UMaine-led, PI Rob Riley, 137+ partners). The Development Award's number does not appear on UMaine's own pages and is not asserted in the candidate evidence row.
- **SHAPE and the B1 battery**: research areas on PROG-000066/000073 are currently HELD pending the owner's proposed §3.5 `packaging_science` term. The SHAPE candidate evidence row bears on the rows' scope/participation only; it does not settle that vocabulary item.
- **M-SPIRE's own site** (advancemspire.org) did not resolve in this lane — an availability signal, not absence; the witness rests on the University of Minnesota's own pages, which are the anchor institution's own pages in any case.
- **Vytal**: with no Atlas anchor, no evidence row is drafted. Any future treatment requires first creating the lead or designating a partner anchor (Penn State is a partner and is carried, but it is not the lead; attaching lead-entity evidence to a partner's rows was not assumed).

## 4. HOLD — CPI / University of Delaware institution mechanics (known hold, not drafted around)

CPI is **fully verified** on the center's and the university's own pages (mission, EFRC identity since 2020, host, scope — §1). The drafted row is in `proposed_rows.csv` with disposition `VERIFIED_ROW_DRAFTED__INTEGRATION_HELD_INSTITUTION_MECHANICS`, and its evidence pair is flagged `HELD__INSTITUTION_MECHANICS_DELAWARE_ORG-003896`. The blocker is purely mechanical: the University of Delaware exists only as an organizations-layer record (**ORG-003896**) — no ecosystem row, no program rows — and its org record's own description already names CPI (and CHARM) among its hosted centers. Per the tasking, this lane does not draft around the hold: no ecosystem row is proposed here, and the CPI center row cannot land until the integrator/owner decides how center rows attach to organizations-only institutions (the same posture as the batch-1 CHARM row). Locality in the drafted row (Newark, DE, New Castle County) comes from the center's own published address, since the UD org record carries no city/state in the Atlas.

## 5. Weakest links (named, per packet discipline)

1. **CSSAS** — the center's own site never uses the word "polymer": its homepage frames the work as the "self- and co-assembly of high-information content building blocks", and the polymer naming ("inorganic, polymer and protein building blocks"; "protein, polymeric and inorganic building blocks") sits in the center's own DOE EFRC overview and public abstract. Verdict rests on host + EFRC identity from its own site plus scope from its own issued DOE documents. Materials-core class, as screened.
2. **CHiPPS** — the center's own About page names photoresists and self-assembling lithographic materials but not polymers; the explicit polymer systems (sequence-specific polymers, block copolymers) are named in the host lab's own CHiPPS article (Berkeley Lab/NERSC). Materials-core class, as screened.
3. **CABES** — no standalone center site URL was confirmed (round-2 residue carried forward). Verification rests on Cornell's own chemistry pages plus the center's own DOE technical summary; the drafted row's `url`/`public_door_url` carry the Cornell witness page and **must be settled by the integrator** before the row lands.
4. **ESRA grain** — scope is verified, but hub = center grain is unruled; the drafted row is gated, not merely pending.
5. **CONFIR award number** — not on UMaine's own pages; deliberately unasserted in the candidate evidence row.

## Method and residue

- Routes: centers' own sites (fact-efrc.ornl.gov, mwet.utexas.edu, aimforcomposites.com, remat.illinois.edu, specs.arizona.edu, chipps.lbl.gov, cssas-efrc.com, cpi.udel.edu, ameslab.gov, energystoragera.org, nctise.org) and anchor institutions' own pages (udel.edu catalog, chemistry.cornell.edu, ces.ncsu.edu, case.edu, umn.edu, msu.edu, umaine.edu), all free; **paid calls: 0**.
- Every count above states unit + filter. Fetch counts per organization stayed within the ~6 cap (max 3: CSSAS, CHiPPS, NCTISE).
- Residue: CPI/CHARM layer mechanics (§4); ESRA hub grain (§2); CABES own-site URL (§5.3); Vytal has no anchor and no drafted evidence (§3.2); the round-2 Development Award residue of 43 awards remains UNCHECKED at abstract level (unchanged by this lane, out of its assigned filter).

---

## Integration record (written last, from the built tree — 2026-11-12)

**Unit:** federal round-2 lane B integration (DOE EFRCs/Hubs + NSF Engines). **Worktree:** `~/workspace/atlas-laneb-build-2026-11-12`, branch `agent/spaghetti/federal-round2-lane-b-2026-11-12`, base origin/main `1f4a26c` (PRs #284–#298). **Built locally only — NOT pushed, no PR.** Build script: `~/workspace/atlas-resync-2026-11-10/build_laneb_fedround2.py`; pre-pass backups in `~/workspace/atlas-laneb-backups-2026-11-12/`. Paid calls: zero.

### Created (8 EFRC center rows, packet cells verbatim, tier B, allocated in packet order)

| Program ID | Center | Lead institution |
|---|---|---|
| PROG-000332 | Fast and Cooperative Ion Transport in Polymer-Based Electrolytes (FaCT) | ORG-002814 Oak Ridge National Laboratory |
| PROG-000333 | Center for Materials for Water and Energy Systems (M-WET) | ORG-004651 UT Austin |
| PROG-000334 | Artificially Intelligent Manufacturing Paradigm for Composites (AIM for Composites) | ORG-004639 Clemson |
| PROG-000335 | EFRC for Regenerative Energy-Efficient Manufacturing of Thermoset Polymeric Materials (REMAT) | ORG-004657 UIUC |
| PROG-000336 | Center for Soft PhotoElectroChemical Systems (SPECS) | ORG-004720 U Arizona |
| PROG-000337 | Center for Alkaline-Based Energy Solutions (CABES) | ORG-004633 Cornell |
| PROG-000338 | Center for High Precision Patterning Science (CHiPPS) | ORG-004640 Lawrence Berkeley National Laboratory |
| PROG-000339 | Center for the Science of Synthesis Across Scales (CSSAS) | ORG-004686 U Washington |

Allocations start at PROG-000332 / EVD-333851 by integrator instruction (lane A, merging after this unit, allocated PROG-000321..331 and EVD-333823..850 on its own branch; this tree's maxima at build time were PROG-000320 / EVD-333822). **Next free: PROG-000340 / EVD-333874.**

### Held out (drafted rows preserved verbatim in this packet's proposed_rows.csv)

- **CPI (University of Delaware, ORG-003896)** — NOT created. Delaware is organizations-layer only (no ecosystem row); the institution mechanics are an owner-battery item (same posture as CHARM). Its existence + scope evidence pair (disposition `HELD__INSTITUTION_MECHANICS_DELAWARE_ORG-003896`) was likewise not minted.
- **ESRA (Argonne, ORG-002816)** — NOT created. ESRA is a DOE Energy Innovation Hub, not an EFRC; hub = center grain has not been ruled by the owner. Its evidence pair (disposition `GRAIN_HELD__HUB_NOT_EFRC`) was likewise not minted.

### Evidence applied (23 rows, EVD-333851..EVD-333873, all in data/evidence_programs.csv)

- 16 rows: existence + scope for each created EFRC row (packet claim_detail verbatim with the packet's witness quote appended as "Witness: …"; tier_effect from each record's own tier B → supports_B).
- 1 row: iCOUP liveness on PROG-000052 (EVD-333867) — currency only; **PROG-000052's cells are byte-identical to base** (asserted against the pre-pass backup).
- 6 rows on carried rows under the Engines evidence-only ruling: NCTISE scope ×2 on PROG-000118 (EVD-333868..869); development-award scope rows on PROG-000117 CWRU (EVD-333870), PROG-000072 M-SPIRE (EVD-333871), PROG-000066 SHAPE (EVD-333872), PROG-000138 CONFIR/NNE-PROMISE (EVD-333873). No program rows were created for any Engine or development award; Vytal received nothing (no Atlas anchor in any layer).

### V-16 ecosystem rollups recomputed (8 institutions, all changed; before → after in the build report)

ORG-002814 (ORNL), ORG-004651 (UT Austin), ORG-004639 (Clemson), ORG-004657 (UIUC, polymer_program false→true), ORG-004720 (U Arizona, false→true), ORG-004633 (Cornell), ORG-004640 (LBNL), ORG-004686 (U Washington, false→true). Note on LBNL: its ecosystem row carried a hand-entered rollup text naming the Molecular Foundry with **zero** program rows behind it; the V-16 recomputation from the built programs.csv replaces that rollup with the computed one (CHiPPS, its first program row). Flagged for the verifier.

### QUEUE

Department-row pilot claim flipped to `done 2026-11-12 (PR #298, merged)` (straggler on this base); this unit's claim added as `claimed:spaghetti 2026-11-12`. Lane A's claim stands absent on this base (its branch carries it) and was not touched.

### Gates (verbatim, run on the final built tree)

- `scripts/validate.py` → "OK — validation passed." (totals: 5024 organizations, 7190 sites, 404 ecosystem rows, 1472 people rows, **195 program rows**, **40908 evidence rows**; only warnings are the standing V-38/V-44 classes)
- `scripts/check_row_loss.py --base origin/main` → "row-loss guard: OK — no keyed row removed from data/ since origin/main (merge-base 1f4a26c2f0)"

---

## INTEGRATION RECORD — ADDENDUM: integrator ruling correcting four tier_effect cells (2026-11-12, post-verification, pre-push)

The independent verifier returned **NOT READY on a single item (D-1)** (`working/federal-round2-verify-b-2026-11-12/lane-b-verification-2026-11-12.md`): four of the six carried-row Engines evidence rows carried the packet's drafted `tier_effect` of `supports_B`, diverging from the project's §4.13 mapping — **`tier_effect` derives from the subject record's own `verification_tier`** (the claim-local rule as applied project-wide; lane A conformed 28/28). The packet graded witness strength; the derived field follows the schema rule. **Integrator ruling: correct the four cells in-build.** The Xu older-row inconsistency (EVD-282024, supports_A on a tier-C record) is a parked defect, not a precedent. The packet files (`proposed_rows.csv` / `proposed_evidence.csv`, staging and this copied pair) remain **as authored** — they are the lane's record; this correction is an integrator ruling documented here, not a packet edit.

| Evidence | Subject | Subject tier (verified from data/programs.csv) | tier_effect: drafted/built → corrected |
|---|---|---|---|
| EVD-333868 | PROG-000118 (NCTISE scope #1) | A | supports_B → **supports_A** |
| EVD-333870 | PROG-000117 (CWRU development award) | A | supports_B → **supports_A** |
| EVD-333871 | PROG-000072 (M-SPIRE) | C | supports_B → **supports_C** |
| EVD-333873 | PROG-000138 (CONFIR/NNE-PROMISE) | A | supports_B → **supports_A** |

The other two carried-row Engines rows already conformed and were not touched (EVD-333869 supports_A on tier-A PROG-000118; EVD-333872 supports_B on tier-B PROG-000066). Post-correction row-level diff vs the pre-pass backups is exactly the build's original change set plus these four cells: programs +8 appends (PROG-000332..339), 0 changed; ecosystem exactly the 8 host rollup rows; evidence +23 rows (EVD-333851..873), each corrected row differing from its pre-correction build state in the `tier_effect` field only. Gates re-run on the corrected tree: `scripts/validate.py` → "OK — validation passed." (195 program rows, 40908 evidence rows); `scripts/check_row_loss.py --base origin/main` → "row-loss guard: OK — no keyed row removed from data/ since origin/main (merge-base 1f4a26c2f0)".
