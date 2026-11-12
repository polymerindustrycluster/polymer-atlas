# University of Connecticut academic depth pass (2026-11-12)

`claimed:spaghetti 2026-11-12` (QUEUE line lands with this pass's integration PR, per the
standing packet pattern.)

By-school scaling wave 3, batched at the owner's instruction 2026-11-12 ("Can we batch more
school research?" / burn remaining capacity on verified data before his limit reset).
Research lanes run while the owner travels; integration serializes behind waves 1-2;
pushes batch for his approval.

## Scope (measured 2026-11-12)

- **1 active program row(s)** at University of Connecticut: PROG-000127 Polymer Science (degree, Institute of Materials Science). 5 blank depth cells across
  the five watched fields.
- **18 people** recorded at University of Connecticut, **0** carrying `program_org_id`.

## School notes

The Polymer Science program sits inside UConn's Institute of Materials Science (IMS).
The IMS / Polymer Science program's own faculty listings are the program tie. Faculty
whose pages show only a home department (Chemistry, Chemical & Biomolecular Engineering,
Materials Science & Engineering) without the Polymer Science program tie are NO_WITNESS.

## Discipline (same as the Ohio, NC State, VT, GT and wave-2 passes)

- The institution's own pages are the citation of record (department, program, and center
  pages; catalog pages where they carry program-grain rosters — check the catalog and
  program faculty listings FIRST: in the NC State and UMass Amherst passes a single
  published roster carried most links).
- People→program links require a **person-level witness** tying the named person to the
  specific program (a program faculty listing, a department page grouping faculty by
  program, a profile naming the program). Employment at the institution or in a home
  department alone is NOT a link.
- Vocabulary fills return the institution's verbatim phrase; the integrator maps to
  §3.1/§3.2/§3.5. Characterization facilities tag `research_areas[characterization_methods]`,
  never specialty_*. `scale_band` needs a published band or self-characterizing statement,
  not a raw headcount or dollar figure.
- A failed fetch is an availability signal, never evidence of absence. Effort cap ~6 fetches
  per program, ~3 per person.

## Deliverables (lane produces the packet; the integrator writes `data/`)

In this folder: `fills.csv` (program_id, field, proposed_value, source_url, verbatim_quote
≤25 words, source_kind), `links.csv` (person_id, program_id, verdict LINK|NO_WITNESS,
witness_quote, witness_url, source_kind), `notes.md` (borderline calls, failed fetches,
suspected defects).

---

## Integration record (integrator, 2026-11-12)

**Fills applied (4):** PROG-000127 research_areas mapped item-by-item
from the program Research page's own list: polymer_synthesis (Advanced
Polymer Synthesis); additive_manufacturing_science (Advanced
Manufacturing); biomedical_polymers + degradation_biodegradation
(Biodegradable and Biomedical Polymers); composites_mechanics (Hybrid
Materials and Composites); polymer_physics (Mechanics of Materials;
Structure-Function Control and Self-Assembly); recycling_circularity
(Sustainable Polymers and Polymer Recycling/Upcycling). Unmapped items:
Energy and Electronics; Environmental and Green Science; Well-Defined
Nanoparticles; Smart Materials and Nanotechnology; Molecular Dynamic
Simulations (a method). specialty_processes += polymerization only (the
About page's synthesis; characterization is a method, "engineering /
molecular design" program-general). specialty_materials += composites_unspecified;
coatings (the About page's own special-areas list; its "nanocomposites"
item takes the vocabulary's generic composites term — no nano-specific
§3.2 slug exists, the validator rejected the literal value on the first
build; the rest of the list has no §3.2 slug). facilities_note (Science 1
Research Center cores; EIRC).

**Held:** scale_band — the program's own size statement is "19 faculty
from 6 departments", a faculty count, which never converts under S3. The
packet also flags that the live faculty page lists 17 names (13 core + 4
associate) against the About page's 19: a currency discrepancy on the
institution's own pages, recorded here, not resolved by us.

**Links (12 primaries set, all PROG-000127; 6 NO_WITNESS stand):** all
twelve rest on the Polymer Program's own faculty page. Jie He
(PERSON-001295) is the weakest — his row sits in the page's core Faculty
table but lacks its "Polymer Program" tag; the table governs, as the
packet judged. McCutcheon (PERSON-001292) is NO_WITNESS: he appears only
in the Associate Faculty list and untagged — the restraint stands.
