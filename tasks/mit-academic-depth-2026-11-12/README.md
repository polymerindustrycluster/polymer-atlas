# Massachusetts Institute of Technology academic depth pass (2026-11-12)

`claimed:spaghetti 2026-11-12` (QUEUE line lands with this pass's integration PR, per the
standing packet pattern.)

By-school scaling wave 3, batched at the owner's instruction 2026-11-12 ("Can we batch more
school research?" / burn remaining capacity on verified data before his limit reset).
Research lanes run while the owner travels; integration serializes behind waves 1-2;
pushes batch for his approval.

## Scope (measured 2026-11-12)

- **2 active program row(s)** at Massachusetts Institute of Technology: PROG-000061 Program in Polymers and Soft Matter (degree), PROG-000101 Materials Science and Engineering (degree). 10 blank depth cells across
  the five watched fields.
- **17 people** recorded at Massachusetts Institute of Technology, **0** carrying `program_org_id`.

## School notes

The Program in Polymers and Soft Matter (PPSM, PROG-000061) is an interdisciplinary
graduate program; its published faculty listings are the program tie. The DMSE faculty
directory ties to PROG-000101. A person witnessed on both returns both rows.

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

**Fills applied (3):** PROG-000061 (PPSM) research_areas +=
polymer_synthesis;polymer_physics, mapped from the program's own
framing ("the chemistry and physics of macromolecules and biopolymers");
facilities_note on PROG-000061 (interdepartmental program; five
participating departments named) and on PROG-000101 (DMSE: its labs and
centers incl. MetLab). The institution rollup on the ecosystem row
recomputes unchanged (no program added, removed, or renamed).

**Held:** PROG-000061 specialty_processes ("Synthesis of Polymers" is a
core-curriculum course title — the Penn State / MSU course-title posture)
and specialty_materials ("biopolymers" is not `bioplastics_biobased`,
the only near slug in §3.2); PROG-000101 research_areas (mission prose),
specialty_processes ("Synthesis and Processing" is a faculty-page
taxonomy label, and generic), specialty_materials ("Soft Matter" is a
taxonomy label with no §3.2 slug); both scale_bands (only faculty
headcounts published — ~31 PPSM core, ~41 DMSE — and faculty counts
never convert under S3).

**Links (21 witnesses banked for 15 people; 2 NO_WITNESS stand):** PPSM
×15, DMSE ×6, all six DMSE witnesses dual (their PPSM witnesses banked
too). Primaries: dual-witnessed people → DMSE PROG-000101 (the tenure
home and degree-granting department); PPSM-only → PROG-000061. Langer
(PERSON-000373) stands on the PPSM Faculty page's "PPSM Affiliates"
section — an affiliate tier, named as such here and in notes.md.
NO_WITNESS stands: Hart PERSON-000368 (a homepage photo caption is not
a faculty listing) and Chung PERSON-000374.
