# Wave 3, lane 7 — program-first trio (+ Pittsburg State + GRCC fold-ins)

Packet-only lane: nothing in `data/` was edited, nothing pushed. Data read
from `~/workspace/atlas-p2-2026-11-12/data/` (== main `f2c7c814`). All
witnesses are the institutions' own pages, fetched 2026-11-12. Paid calls: 0.
Primary fetches: 19 across 7 program rows / 5 institutions (cap ~6 per
program respected).

## ⚠ Premise correction — UW-Stout (read first, integrator)

The lane brief (and the original wave-3 plan) assumed UW-Stout was **absent
from the Atlas entirely**. That is wrong. It was an en-dash name-match
failure in the gap-analysis query ("Wisconsin–Stout" with an en dash does
not match a hyphen search). Ground truth from the CSVs:

- Institution **ORG-002090, University of Wisconsin–Stout** (ecosystem,
  Menomonie WI, IPEDS 240417, ROR https://ror.org/01gb8pc70) — carried
  since 2026-10-29.
- Program **PROG-000005, Plastics Engineering** (B.S., ABET-accredited,
  CIP 14.3201) at **3/5 depth cells** (specialty_processes
  `injection_molding`; specialty_materials `thermoplastics;bioplastics_biobased`;
  facilities_note present).
- **3 recorded people** (Jordan PERSON-000120, Zheng PERSON-000122,
  Kramschuster PERSON-000123), 0 linked.

Per the ABET/IPEDS cross-check lane's correction, the Stout arm was
reframed mid-lane from discovery-from-scratch to **depth completion +
link pass**. No institution/program rows are proposed for Stout.

## Counts (unit + filter stated)

- Program rows treated: **6 carried program rows** received depth passes
  (Ferris 2, Cal Poly 1, Stout 1, Pittsburg Plastics 1, GRCC 1), and
  **1 new program row is proposed** (Pittsburg Polymer Chemistry).
- Depth cells (of specialty_processes / specialty_materials /
  research_areas / facilities_note / scale_band): carried rows move from
  **9/30 filled to 20/30** if all FILL rows apply (Ferris Plastics 3→3
  cells with a content addition; Ferris Rubber 0→3; Cal Poly 0→2;
  Stout 3→4; Pittsburg Plastics 0→4; GRCC 0→1). Held cells: 14, each with
  its reason in `fills.csv`.
- Recorded people checked: **12** (Cal Poly 4, Stout 3, Pittsburg 5).
  Verdicts: **9 LINK** (2 of them conditional on the proposed Polymer
  Chemistry row), **1 already-linked, currency confirmed** (Costanzo,
  with a `lab_url` witness), **1 NO_WITNESS** (Jones), plus Norton's
  second-program support banked as a note.
- Census candidates adjudicated: **4 named people** (1 VERIFIED,
  1 REJECT, 2 STILL_UNCERTAIN). GRCC: no census (per brief; its program
  page names no faculty — only the Department of Manufacturing contact).

## Ferris State (ORG-002089) — Big Rapids, MI

**PROG-000003 Plastics Engineering Technology (was 3/5).** The program page
is lab-rich: Processing Lab (injection molding, thermoforming, extrusion),
Decorating & Assembly (ultrasonic welding, heat staking, solvent bonding,
pad printing, hot stamping), Robotics, Rubber, Testing, and Tooling labs —
the existing fills already reflect most of it. One content fill:
`extrusion_unspecified` added to specialty_processes (subtype never
stated). research_areas and scale_band HELD: no research claim (teaching
program; its Testing Lab is instructional, not a characterization
facility), and the only scale facts are a 16:1 ratio (never converts) and
"SMALL Class Sizes" (class size ≠ enrollment).

**PROG-000152 Rubber Engineering Technology (was 0/5 → 3/5).** The
2025-26 catalog confirms the brief's claim verbatim: the B.S. "is the only
program of its kind in the United States." Fills: `rubber_mixing_compounding`
(catalog: "mixing and testing of rubber compounds"; PLTS 461 Rubber
Compounding), `elastomers_rubber`, a Rubber Lab facilities_note, and the
row's empty city/state/county (Big Rapids / MI / Mecosta, from the
catalog contact block). Currency: the program page still states
"currently not admitting students" — the row's `admissions_status =
not_admitting` (set 2026-11-02) stands confirmed; the catalog still
carrying the curriculum is normal teach-out behavior, not a contradiction.
research_areas HELD (`elastomer_science` is the candidate slug if teaching
programs are ever tagged — not applied).

**Census (0 people were recorded).** Tom Van Pernis — **VERIFIED**:
Associate Professor and Program Coordinator, styled on the program's own
page; proposed primary link PROG-000003. Robert Speirs III — **REJECT**:
Ferris's own 2025 news styles him Professor Emeritus; emeritus fails
Gate A for new people. The rest of the plastics/rubber faculty roster is
**not published on the program or school pages** (the school page names
no faculty; the legacy program page redirects to the plastics homepage) —
census remainder is STILL_UNCERTAIN as a class, settling fact: a
published program faculty/staff page. Banked, not proposed: the school
page names AAS feeders (Plastics Technology AAS; Plastics/Polymer
Technology AAS in the rubber catalog) that have no program rows — no
program-page witness was fetched for them in this lane.

## Cal Poly SLO (ORG-004638) — San Luis Obispo, CA

**PROG-000112 Polymers and Coatings Science, M.S. (was 0/5 → 2/5).**
Fills: `coatings` (specialty_materials — the credential's own subject,
stated on the catalog page) and a facilities_note naming the Kenneth N.
Edwards Western Coatings Technology Center (short courses, testing
services, contract research; WCTC page already sat in the row's sources).
HELD: specialty_processes (`coating_formulation` never stated verbatim —
not inferred from the program name), research_areas (no §3.5 topic named
at program level; the rich topics live on person pages), scale_band (no
enrollment anywhere).

**People (4 recorded, 1 was linked).**
- Shanju Zhang PERSON-001379 — **LINK**. Teaches the program's own
  courses (CHEM 444/447 Polymers and Coatings; CHEM 544/547 Polymer
  Physical Chemistry) and is the named contact for the blended B.S./M.S.
  on the graduate-program page. No `lab_url` minted (her profile's
  Research Website link did not resolve to a distinct lab domain).
- Erik D. Sapper PERSON-001378 — **LINK**. Associate Professor;
  specialties "Coatings, Polymers, Test Method Development, Service Life
  Prediction"; his own M.S. is this program (Cal Poly, 2007).
- Philip Costanzo PERSON-001441 — already linked; currency confirmed
  (still Professor, specialty Polymers). **`lab_url` witness:** his
  profile links "Research Website: Costanzo-lab.com" → propose
  `lab_url = https://costanzo-lab.com`. No title fix (recorded styling
  still matches).
- Seamus D. Jones PERSON-001220 — **NO_WITNESS**. He sits in Materials
  Engineering (his recorded profile is the MATE faculty page); nothing
  ties him to the Chemistry & Biochemistry M.S., and no MATE program row
  is carried to receive him. Settling fact in `links.csv`.

## UW-Stout (ORG-002090) — Menomonie, WI

**PROG-000005 Plastics Engineering (was 3/5 → 4/5).** Program page
re-confirms ABET EAC accreditation, paid co-op at end of sophomore/junior
year, and capstone. Fills: facilities_note enriched with the page's named
donated equipment (Arburg 66T electric, Van Dorn 35T/55T, Engel 35T
injection molding machines; lab in the Jarvis Hall Tech Wing);
research_areas `degradation_biodegradation` **flagged** (see weakest
links). specialty_processes HELD beyond `injection_molding` ("advanced
processing techniques" is generic — the row's original verdict held the
same line). scale_band HELD (only outcomes published).

**People (3 recorded, 0 linked → 3 LINK).** All three are named on the
program's own page (advisory committee table) in program roles: Alex M.
Jordan (Program Director), Wei Zheng (Professor), Adam Kramschuster
(Professor). Program faculty of record at a teaching institution — the
program page is the witness for all three. Census: Matt Ray
(Associate Professor, on the advisory committee) and David Ding
(Professor/Interim Dean) are STILL_UNCERTAIN — advisory membership is
not program-faculty styling; the directory page this lane fetched was a
department-level (Engineering & Technology) listing, which styles nobody
as plastics faculty.

## Pittsburg State (ORG-002092) — Pittsburg, KS (fold-in)

**PROG-000006 Plastics Engineering Technology (was 0/5 → 4/5).** The
program page re-confirms ABET ETAC accreditation. All four depth fills
rest on the program's own faculty pages (the program page itself is
marketing-level): Herring (injection_molding; blow_molding; Plastic
Processing Laboratory), Norton (thermoplastics; thermosets via PET
371/375), and recycling_circularity from all three faculty pages'
research interests. scale_band HELD (100% placement is an outcome).

**Proposed row — Polymer Chemistry, B.S.** (`proposed_rows.csv`). Settled
on the institution's own program page: "one of only three undergraduate
polymer chemistry programs in the nation," Department of Chemistry,
offered with the Plastics Engineering Technology program and the Kansas
Polymer Research Center. CIP 40.0507 per the cross-check lane (integrator
to confirm against IPEDS at application). Depth in the draft rests on the
2025-26 degree map (CHEM 625/626 Polymer Synthesis → `polymerization` +
`polymer_synthesis`; CHEM 680 Physical Properties of Polymers →
`polymer_physics`). HELD in the draft: specialty_materials,
facilities_note ("state-of-the-art equipment" is generic), scale_band
("average class size of 15" is class size, not enrollment).
Banked, not proposed: a Kansas Polymer Research Center / NIMA center row
— named on the program page but no center-page witness was fetched.

**People (5 recorded, 0 linked → 5 LINK).** Book (program coordinator —
strongest link in the packet), Herring, and Norton → PROG-000006.
Norton's page also shows her supporting Polymer Chemistry majors and
mentoring its graduate research; `program_org_id` is single-valued and
her teaching home is PET, so the second program is banked as a note only.
Gupta and Gashti (both Chemistry) → **LINK conditional on the proposed
Polymer Chemistry row** — see weakest links.

## GRCC — Grand Rapids Community College (ORG-002091) (fold-in)

**PROG-000004 Plastics-Polymer Engineering Technology, A.A.A.S. (was
0/5 → 1/5).** Depth pass only, per brief. One fill, fully verbatim:
specialty_processes `injection_molding;blow_molding;extrusion_unspecified;
thermoforming_unspecified` ("injection molding… will be emphasized…
You will also learn blow molding, extrusion, thermoforming"). HELD:
specialty_materials (none named), facilities_note (no lab named on the
program page — the linked program brochure or the Department of
Manufacturing page is the settling source), research_areas (terminal
associate teaching grain), scale_band (completions are a flow, not
enrollment — and the cross-check lane's ~23/yr completer figure vs. the
row's IPEDS 8 for 2024 differ by year/cut; neither converts). The program
page names **no program faculty** (only the Department of Manufacturing
contact), so the brief's conditional faculty note is discharged as a
negative: none to note.

## Weakest links (integrator: check these first)

1. **Gupta + Gashti → proposed Polymer Chemistry row (weakest in the
   packet).** Both rest on: department membership (Chemistry) + tier-A
   recorded polymer specialties, where the recorded profile source is a
   university news article and the program page names no faculty. If the
   integrator wants a person-level program witness, hold both as
   STILL_UNCERTAIN pending a Chemistry faculty page styling them as
   polymer chemistry faculty. The links are also void if the proposed
   row is not created.
2. **Stout research_areas `degradation_biodegradation`** — rests on a
   curriculum marketing line ("Learn how to create biodegradable and
   compostable plastics"), not a research statement. Marked FILL-FLAGGED
   in `fills.csv`; dropping it costs nothing else in the packet.
3. **Stout people links** — the witness is the program page's advisory
   committee table (program roles at a teaching institution), not a
   dedicated faculty roster page. Consistent with the lane brief's
   teaching-institution rule, but it is a thinner witness than Book's
   coordinator page at Pittsburg.

## Holds summary (all verbatim, all in fills.csv)

Out-of-vocabulary or unstated material was never mapped: Ferris robotics
(no §3.1 slug); Ferris rubber molding/extrusion/calendering subtypes
(never stated); Cal Poly `coating_formulation` (never stated verbatim);
GRCC "many secondary processes" (generic); Stout "advanced processing
techniques" (generic); Polymer Chemistry "state-of-the-art equipment"
(generic). Scale_band is HELD on every row in this lane — no program in
scope publishes enrollment, and ratios, class sizes, salaries, placement
rates, and completion flows never convert under the v1.13 rule.


---

## Integration record (integrator, 2026-11-12 — wave-3 unit 10, UW-Stout slice ONLY)

Applied by the integrator of record from this packet to
`agent/spaghetti/wave3-stout-depth`, built off origin/main `20283721`
(post PR #285 — this unit's base already carries the Minnesota and
Southern Miss units' data, EVD-333539..EVD-333594 and PERSON-002117).
This unit applied **only the UW-Stout slice**; the Ferris and Cal Poly
slices integrated as their own units, and the Pittsburg State + GRCC
slices integrate as the next unit. Packet files copied as authored
(README.md, fills.csv, links.csv, census.csv); `proposed_rows.csv` not
copied — it carries only the Pittsburg slice's proposed row.

**Program fills (1 row, PROG-000005 Plastics Engineering, ORG-002090;
depth stays 3/5 with an enriched `facilities_note`):** `facilities_note`
enriched from "Plastics Engineering Lab" to the packet's named-equipment
text (Jarvis Hall Technology Wing; Arburg 66T electric, Van Dorn 35T
and 55T, Engel 35T injection molding machines). The packet's
`research_areas` fill (`degradation_biodegradation`) was **dropped by
integrator ruling** — see the FILL-FLAGGED paragraph below — so
`research_areas` remains empty (its pre-build value). `last_verified`
stays 2026-11-12 on PROG-000005 (the row still changed). Held as
adjudicated: `specialty_processes` beyond `injection_molding`
("advanced processing techniques" is generic) and `scale_band`
(outcomes and completions never convert).

**⚠ FILL-FLAGGED — the `degradation_biodegradation` basis, carried
verbatim from `fills.csv`:** "Curriculum-basis fill (a stated learning
topic, not a research claim) — the weakest fill in this packet; drop it
if the integrator requires research-grade basis for degree rows." The
fill rests on the program page's stated topic line ("Learn how to
create biodegradable and compostable plastics to help protect the
earth"). **Integrator ruling (2026-11-12 follow-up): DROP the fill.**
The lane flagged the basis as a curriculum line (a learning topic),
"not a research claim," and conditioned it on the integrator not
requiring a research-grade basis for degree rows; the integrator
**does** require it — `research_areas` on a degree row rest on the
program's research statements, not curriculum topics. Nothing from
this unit is published yet, so the build was corrected cleanly:
`research_areas` is back to empty, the degradation evidence row was
removed, and the unit's remaining evidence rows were renumbered
contiguously (facilities row EVD-333726; the three link rows now
EVD-333727, EVD-333728, EVD-333729). The `facilities_note` enrichment
stands; PROG-000005's depth is 3/5 with an enriched facilities note.

**Links (3):** PERSON-000120 (Jordan), PERSON-000122 (Zheng),
PERSON-000123 (Kramschuster) each took `program_org_id = PROG-000005`
as PRIMARY, one evidence row each, `last_verified` → 2026-11-12.
Witness for all three: named on the program's own page advisory
committee in program roles (Jordan = Program Director) — program
faculty of record at a teaching institution, per the packet's stated
basis. No title changes (none adjudicated).

**No action, as adjudicated:** Matt Ray and David Ding
(`census.csv` STILL_UNCERTAIN — advisory listing does not establish
faculty standing) received NO link and NO evidence row; neither has a
people record. No new people or program records in this unit.

**Evidence:** EVD-333726..EVD-333729 — 4 rows (1 in
evidence_programs.csv: the facilities fill, after the degradation row
was removed under the ruling above; 3 in evidence_people.csv: the
three links, renumbered EVD-333727..EVD-333729). Allocation note: this unit's range starts at EVD-333726
because the wave-3 units ahead of it in merge order (Lehigh through
Cal Poly) consumed EVD-333595..EVD-333725 on their own branches; this
tree's own scan max is EVD-333594. Next free EVD-333730. QUEUE: the
Southern Miss claim is flipped to done (PR #285, merged) — the P2 and
Minnesota claims already stand done on this main (PRs #283/#284) — and
this pass's claim is added, per the standing pattern.
