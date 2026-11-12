# Wave 3 — Auburn University (ORG-004634) — depth + link packet

**Lane:** wave-3 lane 5 (packet-only; no repo data edited, nothing pushed).
**Data read from:** `~/workspace/atlas-p2-2026-11-12/data/` (== main `f2c7c814`).
**Date:** 2026-11-12. **Paid calls: 0** (direct fetches + one web search only).

## Counts (unit + filter stated)

- **Depth pass:** 3 carried program rows at ORG-004634 (PROG-000091 degree,
  PROG-000092 certificate, PROG-000093 center) → **5 proposed fills**
  (`fills.csv`), all additive to existing cells; 0 fills for the certificate
  (held, below); 0 scale_band fills (no lawful conversion available, below).
- **Link pass:** 11 recorded people at ORG-004634 with `program_org_id`
  empty → **8 LINK, 3 NO_WITNESS** (`links.csv`). LINK split: 3 to the
  degree program PROG-000091 (degree-primary rule), 5 to the center
  PROG-000093.
- **Fetches:** 7 page fetches total (CPAC academics, CPAC home, CPAC center
  profile, CPAC REU page, Beckingham group people page, AU Bulletin faculty
  list PDF, 1 discovery search) — inside the ~6-per-program cap for every
  program (091/092: 2; 093: 5).

## Depth adjudications

### PROG-000091 — Polymer and Fiber Engineering (degree; was 2/5)

Witness: the program's own page, `https://eng.auburn.edu/cpac/academics`,
which states the M.S./Ph.D. core as "polymer chemistry, polymer processing,
structure and properties of polymers, and polymer characterization" and
specialized coursework in "mechanics of flexible structures, composite
materials, biopolymers, and fiber and film formation."

- `research_areas += polymer_physics` — "structure and properties of
  polymers" is the §3.5 definition of `polymer_physics` (structure–property
  relations). (Existing cell: `polymer_synthesis`.)
- `research_areas += characterization_methods` — core coursework in
  polymer characterization; §3.5 term. Characterization fills **neither**
  specialty field — complied with.
- `research_areas += fiber_formation` — "fiber and film formation"
  specialized coursework; §3.1 `fiber_formation` (v1.13 S2) covers the
  fiber half. The film-formation half has no slug and is held (below).
- `specialty_materials += composites_unspecified` — the page states
  "composite materials" as a program specialty area with no composite type
  named; §3.2 `composites_unspecified` is the honest value (never upgrade
  without a source).
- `specialty_processes`: **no fill.** The page's only process phrase is
  generic "polymer processing"; §3.1 carries no generic polymer-processing
  slug. Held verbatim (below).
- `scale_band`: **no fill.** The program's pages publish no enrollment
  figure and no qualitative size self-characterization. The IPEDS figure
  already on the row (2 completions, 2024) is a completion flow, not
  enrollment, and the S3 rule bars converting it.

### PROG-000092 — Graduate Certificate in Polymer Engineering (certificate; was 1/5)

- **All research-area cells HELD** per the UMass Lowell precedent
  (certificates' research areas are held), even though the academics page
  states the certificate's coursework (polymer chemistry, polymer
  characterization, polymer processing) verbatim.
- No specialty fills either: the same phrases yield no honest §3.1/§3.2
  value ("polymer processing" is generic with no slug; coursework in
  polymer chemistry is not a `polymerization` claim). Row unchanged by
  this packet.

### PROG-000093 — Center for Polymers and Advanced Composites, CPAC (center; was 2/5)

Witnesses: center home `https://eng.auburn.edu/cpac/` and the center
profile `https://eng.auburn.edu/research/centers/profiles/center-for-polymers-and-advanced-composites`.

- `research_areas += characterization_methods` — the profile page states
  the center's work as "synthesis, processing, and characterization
  research" with "specialized polymer and composite synthesis, processing,
  and characterization capabilities" and an A2LA-accredited ISO/IEC 17025
  testing laboratory. (Existing cell: `polymer_synthesis`.)
- Research-area phrases on the center home — "polymer synthesis,
  multifunctional polymers and composites, polymer & composite materials
  processing, mechanics and design" — are the same phrases held verbatim
  at pass 31; they remain **held** (below). `polymer_synthesis` is already
  carried.
- `specialty_processes` / `specialty_materials`: **no fill.** The profile
  page's process evidence is an equipment list (injection molding,
  extrusion, melt pressing, polymer 3D printers) — that is facilities
  evidence and is already carried in the row's `facilities_note`;
  equipment is not upgraded to specialty claims in this packet.
- `scale_band`: **no fill.** The profile page's counters render as
  JavaScript placeholders ("0+"); the only size statements found are
  faculty/researcher counts ("Over 25 affiliated faculty" — CPAC
  colloquium deck), and faculty-referent counts never convert under S3.

## Holds — out-of-vocabulary, verbatim (owner vocabulary questions if ever pursued)

1. "polymer processing" (generic process phrase; PROG-000091 own page) —
   no §3.1 generic slug exists.
2. "multifunctional polymers and composites" (PROG-000093 own page) —
   held at pass 31, re-witnessed 2026-11-12, still no slug.
3. "polymer and composite materials processing" (PROG-000093 own page) —
   same generic-processing gap as (1).
4. "mechanics and design" (PROG-000093 own page) — **not** mapped to
   §3.5 `composites_mechanics`: the center's phrase is generic and is not
   stated as composite mechanics/damage/durability.
5. "mechanics of flexible structures" (PROG-000091 specialized course) —
   fiber/textile-structure mechanics; no honest slug.
6. "biopolymers" (PROG-000091 specialized course) — **not** mapped to
   §3.2 `bioplastics_biobased`; the course title alone does not state a
   bio-based plastics specialty.
7. "film formation" (half of "fiber and film formation", PROG-000091) —
   no slug; the fiber half was filled as `fiber_formation`.

## Link adjudications (11 people at ORG-004634)

**Program-membership witnesses used (Auburn's own pages only):**
(a) the AU Bulletin current University Faculty list, which carries a
**(PFEN)** unit listing for faculty of the Polymer and Fiber Engineering
program; (b) the CPAC REU page, which names the center's Site PI and
project mentors with current faculty titles; (c) the Beckingham group
page for the PFEN Graduate Program Officer styling.

**LINK → PROG-000091 (degree program; degree-primary rule):**

- **PERSON-000210 Bryan S. Beckingham** — his group page styles him
  "Graduate Program Officer, Polymer & Fiber Engineering" and "Director,
  Center for Polymers and Advanced Composites." Degree program is
  primary; the CPAC directorship (PROG-000093) is banked here as the
  secondary witness, per the single-valued rule.
  **lab_url witness:** the Beckingham Polymer Research Group site —
  people page fetched at
  `https://ecm.eng.auburn.edu/wp/polymerlab/about/news/people/`; proposed
  `lab_url` is the group site root `https://ecm.eng.auburn.edu/wp/polymerlab/`
  (root derived by trimming the fetched people-page path; one-click
  confirm for the integrator).
- **PERSON-000211 Maria Lujan Auad** — Bulletin lists her twice with
  identical styling, under (PFEN) and (CHEN): PFEN program faculty.
- **PERSON-000215 Sabit Adanur** — Bulletin lists him twice with
  identical styling ("Professor, 1992, PhD MS North Carolina State, BS
  Istanbul Tech"), under (PFEN) and (MECH): PFEN program faculty.
  His polymer-processing/composites specialties are already carried on
  his record from his Auburn directory profile (tier A, 2026-10-31);
  his directory page was not re-fetched this pass.

**LINK → PROG-000093 (center; no degree-program witness, center witness present):**

- **PERSON-000217 Russell W. Mailen** — CPAC REU **Site PI**, styled
  "associate professor of aerospace engineering" on the REU page.
- **PERSON-000216 Michael P. Howard**, **PERSON-000219 Jean-Francois
  Louf**, **PERSON-000220 Cassandra Porter**, **PERSON-000218 Xinyu
  Zhang** — named CPAC REU project mentors on the center's own page,
  each styled with current rank and department (Gate A); the page's
  projects are polymer/advanced-composites research (Gate B at center
  grain).

**NO_WITNESS (3)** — Gate A/B as polymer researchers is not the gap;
no Auburn page found this pass ties them to the PFEN program or to CPAC:

- **PERSON-000212 Christopher Grieco** (Chemistry & Biochemistry) —
  Bulletin lists him (CHEM) only. Settling fact: a CPAC affiliated-faculty
  listing or PFEN page naming him.
- **PERSON-000213 Edward W. Davis** (Mechanical Engineering) — Bulletin
  (MECH) only. An Auburn news page (2024-04) styles him PI on NSF/NIST
  polymer-recycling awards — Gate B satisfied, program membership not
  witnessed. Settling fact: same as Grieco.
- **PERSON-000214 Virginia A. Davis** (Chemical Engineering) — Bulletin
  (CHEN) only; co-PI on the same polymer-recycling awards. Settling
  fact: same as Grieco.

## Title flags (P1 rider — flag only, verbatim; nothing edited)

1. **PERSON-000210 Beckingham** — recorded: "Uthlaut Family Associate
   Professor, Department of Chemical Engineering; Director, Center for
   Polymers and Advanced Composites (CPAC)". His own group page styles
   him "**Mary and John H. Sanders Associate Professor**, Dept. of
   Chemical Engineering" (+ both roles). The current Bulletin and the
   current college directory profile say "Uthlaut Family Associate
   Professor." Auburn's own pages conflict on the named chair.
2. **PERSON-000211 Auad** — recorded: "Charles E. Gavin III Distinguished
   Professor, Department of Chemical Engineering". Current Bulletin:
   "Charles E. Gavin III Distinguished Professor **and Associate Dean
   for Graduate Studies and Faculty Development, Samuel Ginn College of
   Engineering**" — an added administrative role the record lacks.
3. **PERSON-000217 Mailen** — recorded `associate_professor`. The CPAC
   REU page styles him "associate professor of aerospace engineering";
   the current Bulletin faculty list styles him "**Assistant Professor**
   (AERO)". Auburn's own pages conflict on rank.
4. **PERSON-000218 Zhang** — the Bulletin carries **two** same-name
   entries with different ranks: "ZHANG, XINYU, Associate Professor,
   2005, PhD University of Texas-Dallas, ME BE Tianjin University
   (PFEN)" and "ZHANG, XINYU, Alumni Professor (CHEN)". Whether the
   (PFEN) entry is this person (dual listing, cf. Auad/Adanur) or a
   namesake is not settled by this pass; his LINK therefore rests on the
   REU page alone, and the (PFEN) entry is flagged as a possible
   degree-program upgrade the integrator can settle via his group page
   (`https://ecm.eng.auburn.edu/wp/zhanggroup/`, already in his record's
   sources; not re-fetched this pass).

## Weakest links (read first at verification)

1. **The five PROG-000093 LINKs rest on CPAC REU mentorship.** The REU
   page is the center's own page and names a Site PI + project mentors
   for polymer/composites projects, but it is a program-activity roster,
   not a styled "affiliated faculty" list. If the verifier wants a
   stronger center-membership witness, the settling document is a CPAC
   affiliated-faculty listing (the center's colloquium deck claims "over
   25 affiliated faculty" without a public name list we could fetch).
2. **Zhang's Bulletin (PFEN) entry** — deliberately not used (see flag 4).
3. **`fiber_formation` on PROG-000091** derives from a specialized-course
   listing ("beneficial to their research"), the softest of the four
   degree fills; the other three rest on the program's stated core.

## Notes for the integrator

- All fills are **additions** (append `;value`) to the named cells;
  current values: PROG-000091 `research_areas=polymer_synthesis`,
  `specialty_materials` empty; PROG-000093 `research_areas=polymer_synthesis`.
- Beckingham's secondary witness (CPAC director → PROG-000093) should be
  banked as an evidence row only, per the single-valued rule.
- Evidence `tier_effect` follows each record's own tier (all three
  programs and all 11 people are tier A → `supports_A`); depth/link
  evidence is claim_type `scope`, source_class `own_site`, per standing
  wave practice.
- No new program rows proposed; no people added or removed; the three
  NO_WITNESS people stay unlinked with the settling facts above.

---

## Integration record (integrator, 2026-11-12)

**Fills applied (5 fills, 2 program rows changed):** PROG-000091
(Polymer and Fiber Engineering) research_areas +=
polymer_physics;characterization_methods;fiber_formation and
specialty_materials += composites_unspecified, mapped from the
program's own academics page (EVD-333621, EVD-333622); PROG-000093
(CPAC) research_areas += characterization_methods, mapped from the
center profile (EVD-333623). The institution rollup on the ORG-004634
ecosystem row is verified unchanged (no program added, removed,
renamed, or repointed, so the V-16 inputs did not move).

**Held:** PROG-000092 (Graduate Certificate) — no change at all:
research areas held per the UMass Lowell certificate precedent and no
honest specialty value was adjudicated. scale_band on all rows (no
published enrollment and no qualitative size self-characterization;
the IPEDS completions figure on PROG-000091 is a completion flow and
never converts under S3; CPAC's faculty counts never convert). The
seven out-of-vocabulary phrases in the lane README above stand held
verbatim (generic "polymer processing"; "multifunctional polymers and
composites"; "polymer and composite materials processing"; "mechanics
and design" — not mapped to composites_mechanics; "mechanics of
flexible structures"; "biopolymers" — not mapped to
bioplastics_biobased; "film formation").

**Links (8 applied; 11 people-evidence rows banked):** PROG-000091 ×3
(Beckingham PERSON-000210, Auad PERSON-000211, Adanur PERSON-000215 —
degree-primary rule), PROG-000093 ×5 (Mailen PERSON-000217, Howard
PERSON-000216, Louf PERSON-000219, Porter PERSON-000220, Zhang
PERSON-000218). Beckingham's CPAC directorship is banked as an
evidence row only (EVD-333625), per the single-valued program_org_id
rule. Beckingham's lab_url is set to the Beckingham Polymer Research
Group site under SCHEMA v1.13 S6, with its own evidence row
(EVD-333626). NO_WITNESS stands: Grieco PERSON-000212, Edward Davis
PERSON-000213, Virginia Davis PERSON-000214 — no link, no person
evidence row; settling facts in the lane README above.

**Title flags (P1 rider):** Auad's Associate Dean role APPLIED as a
role_as_published enrichment (EVD-333628) — the packet quotes the
current Bulletin styling verbatim with its URL ("Charles E. Gavin III
Distinguished Professor and Associate Dean for Graduate Studies and
Faculty Development, Samuel Ginn College of Engineering"); role stays
professor. Two conflicts on Auburn's own pages take NO change:
Beckingham's named chair (recorded and Bulletin/directory: "Uthlaut
Family Associate Professor"; his group page: "Mary and John H.
Sanders Associate Professor") and Mailen's rank (REU page: "associate
professor of aerospace engineering"; current Bulletin: "Assistant
Professor (AERO)" — recorded role stays associate_professor). The
duplicate same-name Xinyu Zhang Bulletin entries were not used;
Zhang's link rests on the CPAC REU page alone.

**Evidence:** EVD-333621..EVD-333634 (14 rows: 3 in
evidence_programs.csv, 11 in evidence_people.csv; all claim_type
scope, source_class own_site, tier_effect supports_A — every record
touched is tier A). Next free: EVD-333635. Allocation note: this
unit's range was allocated serially across the wave-3 units
(preceding units consumed EVD-333539..EVD-333620); the tree-local max
at build time was EVD-333538 and was not used. last_verified refreshed
to 2026-11-12 only on the 10 changed records (2 programs, 8 people).
validate.py PASS and the row-loss guard green on the built tree.
