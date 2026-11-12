# Wave 4 Tranche 2 — Texas Tech University (ORG-004718) — RESEARCH PACKET

Lane: spaghetti subagent, 2026-11-12. Packet only — no repo writes, no build.
Base: origin/main db51af32 (checked by `git fetch` + `git show` of the data files).
Target carried row: PROG-000153 "Polymers & Materials Science Minor" (degree/minor), depth 0/5.
Unlinked pool at ORG-004718 pulled from `data/people.csv` on origin/main: exactly **3 people**
(PERSON-000977 Abidi, PERSON-001141 Kristufek, PERSON-001166 Wei Li — all tier A, all
`program_org_id` blank). Paid calls: **zero** (direct fetches + built-in search only).

**Headline:** this school's honest yield is a center row, not department rows. The polymer
work at Texas Tech is real and well-witnessed, but it lives in (i) an institute whose name
carries "Biopolymer" (FBRI — draftable under prong (a)) and (ii) departments whose own
pages name polymers only as themes inside differently-named areas or as person-grain
profile styling (not draftable under prong (b) as ruled). One existing person links; two
pass both gates but have no witnessed program tie and stay unlinked with settling facts.

## 1. PROG-000153 depth fills — VERDICT: no fills (0 proposed, 5 refused)

The minor's own page (https://www.depts.ttu.edu/che/undergrad/minors.php) is an
overview-plus-curriculum page: an educational-goal paragraph ("The goal of the minor is to
provide students with knowledge and skills in the polymer and materials sciences so that
they are better prepared to enter relevant industries, including semiconductor electronics,
plastics and rubber, and advanced composites") and a course list (CHE 4340 Polymer
Processing, CHE 4341 Polymerization Engineering, CHE 4342 Polymer Physics & Engineering,
CHE 5346 Polymer Viscoelasticity, CHEM 4310 Polymer Chemistry, CHE 5344 Polymers and
Materials Laboratory). It carries no research statement, no faculty, no facility
description, and no size figure. Per-field refusals with the governing rule are in
`fills.csv`. The row stays 0/5 by design — the same disposition as the other course-grain
rows held in tranche 1 (Penn PROG-000034, CMU PROG-000042).

## 2. Department-row tests (§4.11 prong (b))

A department row drafts only where the department's own pages name polymers as a
research area, track, or concentration **of its degrees**; person-level polymer work is
prong-(c) corroboration, never sufficient.

- **Chemical Engineering — STILL_UNCERTAIN (not drafted).** ChemE's own pages name its
  research areas as Bioengineering and Nanomedicine; Soft Matter and Nanotechnology;
  Computational Modeling and Data Science; Electrochemical Engineering; Energy and
  Sustainability. The Soft Matter and Nanotechnology page
  (https://Www.Depts.Ttu.Edu/che/research/soft_matter_nanomaterials/index.php) states:
  "Topics include the stability of energetic materials, glassy pharmaceuticals, colloids
  and surfactants, ionic liquids, the glass transition, polymer rheology and nonlinear
  mechanics, membranes, nanocomposites, and the behavior of material at the nanoscale."
  Polymers appear as topics *inside* a differently-named area — the UTK CBE posture the
  pilot held STILL_UNCERTAIN, not the Penn CBE posture (a concentration named in the
  degree itself). The one polymer-named credential ChemE administers is the Polymers &
  Materials Science Minor, already carried as PROG-000153; a ChemE degree row would
  duplicate it without a prong-(b) witness of its own. Settling fact: a ChemE page naming
  polymers/polymer science as a research area, track, or concentration of its B.S./M.S./
  Ph.D. degrees.
- **Chemistry and Biochemistry — STILL_UNCERTAIN (not drafted).** The TTU catalog's
  department entry (https://catalog.ttu.edu/preview_entity.php?catoid=23&ent_oid=1872)
  states: "Students seeking graduate degrees may specialize in analytical, inorganic,
  organic, physical, or theoretical chemistry; chemical education; chemical physics; or
  biochemistry" — no polymer specialization. The polymer naming on Chemistry's own pages
  is person-grain only (Kristufek's profile header "Research Area: Polymer, Materials, &
  Organic Chemistry"; Mayer's interests list "Polymers") — the Penn Chemistry posture
  from tranche 1, held STILL_UNCERTAIN there. A single course (CHEM 4310 Polymer
  Chemistry) is recordable grain, not a department row. Settling fact: a Chemistry &
  Biochemistry page (research-areas/divisions page or degree description) naming polymer
  chemistry as a research area or specialization of its degrees.
- **Plant and Soil Science — no degree row tested.** PSS's polymer-named unit is the
  Fiber & Biopolymer Research Institute, drafted below as a center under prong (a); no
  PSS degree-page polymer witness was sought once the center row grounded the links.
- **Mechanical Engineering — not tested.** No member of the unlinked pool is ME-homed,
  and no polymer witness for ME appeared on any page fetched; the minor draws one course
  from ME (ME 3311 Materials Science), which is curriculum, not a prong-(b) witness.

**Considered and refused on grain:** two single-PI units are polymer-named or
polymer-styled on ChemE's own pages — the Polymers and Condensed Matter Physics Group
(McKenna) and the Biomaterials and Surface Engineering Laboratory (Li Lab). Neither is a
program/center/facility at Atlas grain (the MCL precedent is a shared facility; a PI's
research group is what a person's `lab_url` field exists to record). No rows drafted;
both are carried in the census/links reasoning instead.

## 3. Proposed row — VERIFIED: Fiber and Biopolymer Research Institute (center, prong (a))

Drafted in `proposed_rows.csv` (packet-local key **NEW-TTU-FBRI**). §4.11 prong (a): a
center/institute named with polymer scope ("Biopolymer") on the institution's own pages.
Witnesses, all TTU's own pages:

- Existence/scope (https://www.depts.ttu.edu/fbri/): "Welcome to the FBRI at Texas Tech
  University. We are committed to serving the research needs of university researchers,
  cotton breeders, public agencies, and textile manufacturers." Mission: "(1) research
  and technology transfer in fibers and textiles; … (4) development of textile testing
  methods and instrumentation; and (5) textile manufacturing and bioproducts development."
- Davis College page (https://www.depts.ttu.edu/agriculturalsciences/About/facilities/maps/fiber.php):
  "Texas Tech University's Fiber and Biopolymer Research Institute (FBRI) is equipped and
  staffed to conduct research and development activities ranging from small-scale testing
  through large-scale manufacturing"; activities include "Researching, testing, and
  evaluating natural and man-made fibers", "Production and evaluation of yarns and
  fabrics", "Dyeing and finishing"; facilities include a "biopolymer research laboratory,
  materials evaluation laboratory, short staple spinning laboratory, weaving laboratory,
  chemical finishing laboratory, chemical properties and microscopy laboratory,
  flammability laboratory and fabric care laboratory".
- FBRI labs page (https://www.depts.ttu.edu/fbri/MSELpage.php): the Cotton Phenomics
  Laboratory "provides in-depth physical testing and evaluation for fibers, yarns, and
  fabrics" (HVI, AFIS, FAVIMAT); the Spinning Evaluation Laboratory contains
  "state-of-the-art ring spinning, compact spinning, and open-end rotor spinning
  machinery".
- TTU strategic-research page: a "Biopolymer Research Group" is listed among FBRI's
  facilities, and "In as few as 10 minutes, Texas Tech researchers can transform
  low-quality cotton fibers into a cellulose gel that can be molded into bioplastics."

Cells held blank in the draft: `scale_band` (the 110,000 sq ft figure is building size,
not a published program scale — never converts, SCHEMA v1.13 S3), `cip_code` (centers
carry none), `credential_types` (empty by design for centers).

## 4. Links — 1 LINK / 0 BANKED / 2 NO_WITNESS (details in `links.csv`)

- **PERSON-000977 Noureddine Abidi → LINK to NEW-TTU-FBRI.** Gate A (PSS's own profile):
  "Abidi is the Leidigh Endowed Professor for the Department of Plant and Soil Science
  and was appointed as the Managing Director for the Fiber & Biopolymer Research
  Institute on January 1, 2017" — FBRI's own faculty page styles him the same way
  ("Leidigh Professor (PSS) / Managing Director (FBRI)"). Gate B (same PSS profile):
  "Dr Abidi will continue his research efforts to further the understanding of
  plant-based biopolymers with special emphasis on cotton." He directs the drafted
  center, so it is his witnessed home program.
- **PERSON-001141 Samantha L. Kristufek → NO_WITNESS (program tie only).** Both gates
  pass on Chemistry's own profile ("Title: Assistant Professor"; "Research Area:
  Polymer, Materials, & Organic Chemistry, Sustainable Materials"; "Sugar-based
  Polymers with a Close-Loop Lifecycle"). No fetched page ties her to the minor, and
  the Chemistry row was refused (§2). Settling fact in `links.csv`.
- **PERSON-001166 Wei Li → NO_WITNESS (program tie only).** Both gates pass on ChemE's
  own lab page ("Wei Li / Professor"; "Feb 2026, Dr. Li has been promoted as a Full
  professor at TTU"; "develop novel functional polymer surfaces and devices for
  biomedical and energy applications"). No fetched page ties him to the minor, and the
  ChemE row was refused (§2). **Identity discipline:** this witness is Texas Tech
  ChemE's own lab page — the URL already carried on PERSON-001166's record — and is
  unambiguously about the Texas Tech Wei Li, not his UT Austin namesake.

## 5. Census — 4 VERIFIED / 3 STILL_UNCERTAIN / 1 REJECT (details in `census.csv`)

VERIFIED (no Atlas record exists for any of them; people.csv on origin/main carries
only the 3 pool members at ORG-004718):

- **Diego Gomez-Maldonado** (PSS/FBRI, Assistant Professor) — roster-grade tier B;
  "focuses on biopolymers for biomedical applications." Primary program: NEW-TTU-FBRI.
- **Julia Shamshina** (PSS/FBRI, Assistant Professor) — roster-grade tier B; Gate B
  rests on her appointment styling, "Assistant Professor in Biopolymers & Bioproducts."
  Primary program: NEW-TTU-FBRI. **Weakest VERIFIED in the packet** (see §6).
- **Rajesh Khare** (ChemE, Department Chair) — Gate B profile-grade from his group's
  own page ("applied to polymer melt, polymer network, and colloidal suspension
  systems"; "Polymer membrane based separations"); Gate A roster-grade (ChemE's Soft
  Matter faculty list + chair styling), tier B flag. Primary program: none — mint
  unlinked (MatSE-pass Mather/Zarzar pattern).
- **Michael F. Mayer** (Chemistry, Associate Professor) — profile-grade on Chemistry's
  own faculty page ("Title: Associate Professor"; interests include "Polymers";
  "persistently entangled polymeric assemblies include polyrotaxanes, polycatenanes
  and daisy-chain polymers"). Primary program: none — mint unlinked.

STILL_UNCERTAIN (do not mint): **Gregory B. McKenna** (Gate B overwhelming — his own
group is the "Polymers and Condensed Matter Physics Group" — but Gate A currency is
unwitnessed: no current rank styling found, and he is absent from ChemE's current Soft
Matter faculty list; an emeritus posture would bar admission); **Kalavathy Rajan**
(Gate B: "bio-product development from crop residues" never says polymer);
**Brendan Kelly** (Gate B: FBRI's page carries no research statement for him; fiber
phenomics as styled is testing, not yet a person-level polymer-research witness).
Settling facts are named per person in `census.csv`.

REJECT: **Christopher Turner** — Gate A passes (Research Assistant Professor is a
research-professor rank under §4.9), Gate B fails on the deciding fact that his own
roster statement names software/data analytics for cotton testing equipment, with no
polymer research stated.

Screened but not censused: the remaining names on ChemE's Soft Matter faculty list
(Chau-Chyun Chen — thermodynamics; Siva A. Vanapalli, Jeremy Marston, Glenn Zeng) carry
no polymer witness on any page fetched in this pass and were not pursued within the
fetch budget.

## 6. Weakest links (named)

1. **Shamshina's Gate B** — rests entirely on the words "Biopolymers & Bioproducts" in
   her appointment styling on a roster page; no research statement was fetched for her.
   Admitted at tier B under the brief's roster-grade allowance with the flag in
   `census.csv`; a stricter verifier demotes her to STILL_UNCERTAIN.
2. **The FBRI draft's 110,000 sq ft figure** — quoted from TTU's strategic-research and
   Davis College pages as indexed by search; those two pages were not re-opened in this
   lane. It feeds only the facilities_note (scale_band is held blank regardless), but
   the figure should be re-read at build.
3. **The two NO_WITNESS outcomes hinge on the strict prong-(b) reading** shared with
   the pilot (UTK CBE) and tranche 1 (Penn Chemistry). The facts are not in doubt —
   Li and Kristufek are current polymer faculty on their own departments' pages — only
   the grain is: no polymer-named degree row exists for either to land on. If the owner
   ever loosens prong (b) to cover a named research *theme* page, ChemE is the first
   row this packet would draft and Li its first link.

## 7. Fetch log (all Texas Tech's own pages unless noted; zero paid calls)

Opened: ChemE minors page; Li Lab page; Abidi PSS profile; Kristufek Chemistry
profile; FBRI home; ChemE Soft Matter and Nanotechnology page; FBRI faculty page;
FBRI labs page; Mayer Chemistry profile; McKenna group page; Khare group research
page. Search-indexed only (quoted in notes, flagged where load-bearing): TTU catalog
Chemistry entry; ChemE Chair's Welcome page; Davis College FBRI facilities page; TTU
strategic-research FBRI page. No failed fetches; no bot walls.

---

## Integration record (integrator, 2026-11-12 — written from the built tree)

Unit: wave-4 tranche-2 Texas Tech school pass. Worktree `~/workspace/atlas-w4-tt-build-2026-11-12`,
branch `agent/spaghetti/wave4-tranche2-texas-tech-2026-11-12`, base origin/main `db51af32`
(PR #310 head). ID floors per the integration brief (other tranche-2 units merge around this
one): PROG-000348 / PERSON-002169 / EVD-334080 — tree maxima on the base were PROG-000347 /
PERSON-002167 / EVD-334069, so the floors sit above the tree with headroom. Paid calls: zero.

**Landed, exactly per packet:**
- **PROG-000348 Fiber and Biopolymer Research Institute created** (center, §4.11 prong (a)).
  Packet cells verbatim; only the allocated ID and the notes allocation marker + sq-ft
  addendum differ from the draft (see below). Existence evidence EVD-334080, scope EVD-334081.
- **PROG-000153: NO fills.** All five depth cells refused per fills.csv (course-grain minor,
  overview-plus-curriculum page only). The row is byte-identical to the pre-pass backup —
  not even `last_verified` moved. It stays 0/5 by design.
- **1 LINK:** PERSON-000977 Abidi → PROG-000348 (program_org_id + last_verified only);
  scope evidence EVD-334082 (supports_A, his own tier).
- **2 NO_WITNESS byte-untouched:** PERSON-001141 Kristufek, PERSON-001166 Wei Li (Texas Tech)
  — gates pass, no witnessed program tie; no evidence rows minted for either. ChemE +
  Chemistry department rows NOT created (packet STILL_UNCERTAIN under prong (b) stands).
- **4 census mints:** PERSON-002169 Diego Gomez-Maldonado (assistant_professor, tier B,
  linked → PROG-000348; EVD-334083/334084), PERSON-002170 Julia Shamshina (assistant_professor,
  tier B, linked → PROG-000348; EVD-334085/334086 — the packet's weakest-VERIFIED flag is
  carried **verbatim** in her scope evidence notes, per the roster-grade precedent of
  PR #302), PERSON-002171 Rajesh Khare (tier B, minted UNLINKED, ChemE affiliation witnessed;
  EVD-334087/334088), PERSON-002172 Michael F. Mayer (tier A, minted UNLINKED, Chemistry
  affiliation witnessed; EVD-334089/334090). McKenna/Rajan/Kelly (STILL_UNCERTAIN) and
  Turner (REJECT) not minted. No §4.21 identifiers.
- **Rollup:** ORG-004718 recomputed — polymer_program_name "Polymers & Materials Science
  Minor" → "Polymers & Materials Science Minor; Fiber and Biopolymer Research Institute"
  (degree precedes center in V-16 order), polymer_program_url unchanged (the minor's page,
  still the first sorted program), last_verified refreshed. Pre-build recompute reproduced
  the carried rollup exactly (zero drift).

**Integrator judgments / deviations from the packet draft (documented per protocol):**
1. **Sq-ft re-check (packet-directed, ruling 1):** the packet's facilities_note figure was
   its weakest cell (search-indexed only). At build, TTU's strategic-research page
   (https://www.depts.ttu.edu/research/strategicresearch/fiber-biopolymer-research-institute.php)
   was re-opened live and states: "Texas Tech's FBRI, located approximately six miles east
   of the main campus, occupies 110,000 sq. ft. of space allowing researchers to conduct
   testing and evaluation from the raw fiber stage through finished textiles." **Figure
   CONFIRMED — facilities_note stands as drafted.** The program row's notes carry an
   integration addendum recording this (packet notes otherwise verbatim), and the existence
   evidence row's notes record the check. Zero other live checks were made.
2. **Khare's controlled `role`:** the packet's title_as_published is "Department Chair,
   Department of Chemical Engineering"; §4.9's enum has no chair value. Folded to
   `professor` per the standing department-chair precedent (PERSON-000042 Lapitsky,
   PERSON-000256 Budhlall, PERSON-000313 Ober — all `professor` with the chair styling
   verbatim in role_as_published). role_as_published carries the packet's title verbatim.
3. **Mayer's tier:** census.csv grades Mayer profile-grade on BOTH gates with no tier-B
   flag (contrast Khare, whose Gate A is roster-grade and tier-B-flagged in the packet).
   Minted at tier A (MatSE-pass Mather/Zarzar precedent: profile-grade gates mint at A;
   roster-grade gates mint at B). A verifier preferring uniform tier B for this unit's
   unlinked mints can demote with a one-cell change.
4. **research_specialties on mints:** landed exactly as the packet's census "Suggested
   research_specialties at mint" (Gomez-Maldonado biomedical_polymers;bioplastics_biobased;
   Khare rheology;membranes_separations;polymer_physics; Mayer polymer_synthesis;
   Shamshina none suggested → blank).

**Gates on the built tree:** `scripts/validate.py` → "OK — validation passed."
(1,505 people, 215 programs, 408 ecosystem, 41,143 evidence rows; warnings are the
standing V-38/V-44 classes only). `scripts/check_row_loss.py --base origin/main` →
"row-loss guard: OK — no keyed row removed from data/ since origin/main (merge-base
db51af320d)". Row-level diff vs pre-pass backups = exactly the adjudicated change set:
programs +1, people +4/1 changed, ecosystem 1 changed, evidence +11 pure appends,
QUEUE +1 claim line. Next frees: PROG-000349 / PERSON-002173 / EVD-334091.
