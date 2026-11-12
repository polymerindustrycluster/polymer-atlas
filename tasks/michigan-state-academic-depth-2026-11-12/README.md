# Michigan State University academic depth pass (2026-11-12)

`claimed:spaghetti 2026-11-12` (QUEUE line lands with this pass's integration PR, per the
standing packet pattern.)

By-school scaling wave 2, batched at the owner's instruction 2026-11-12 ("Can we batch more
school research?"). Research lanes run while the owner travels; integration serializes behind
the NC State / Virginia Tech / Georgia Tech PRs; pushes batch for his approval.

## Scope (measured 2026-11-12)

- **3 active program rows** at Michigan State University: PROG-000066 School of Packaging (degree), PROG-000073 Center for Plastic, Paper and Hybrid Packaging End-of-Life Solutions (center), PROG-000103 Materials Science and Engineering (degree). 13 blank depth cells across the
  five watched fields.
- **19 people** recorded at Michigan State University, **0** carrying `program_org_id`.

## School notes

The School of Packaging (PROG-000066) is a standalone school — its faculty directory is
the program tie. The End-of-Life center (PROG-000073) ties come from the center's own
pages. Packaging faculty are in scope here as recorded; do not force packaging people
into the MSE row or vice versa.

## Discipline (same as the Ohio, NC State, VT and GT passes)

- The institution's own pages are the citation of record (department, program, and center
  pages; catalog pages where they carry program-grain rosters).
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

**Fills applied (5):** PROG-000066 facilities_note; scale_band = large
(more than 600 students each year, S3; the "largest packaging program in
the country" characterization agrees). PROG-000073 research_areas +=
degradation_biodegradation;recycling_circularity (the center's own research
list); facilities_note. PROG-000103 scale_band = medium (B.S. enrollment
Fall 2025: 60, S3).

**Vocabulary hold (validator-caught, 2026-11-12):** both programs'
research_areas fills were drafted around the topic "packaging" — and the
§3.1/§3.2/§3.5 union has NO term for packaging science. The validator
rejected the value on the first build; stretching `membranes_separations`
(barrier science) across the whole topic list would rot the taxonomy, so
both fills are HELD and banked in fills.csv as witnesses for an owner
battery item: a §3.5 `packaging_science` candidate term. The gap is
structural — the nation's largest packaging program and a packaging center
cannot be topic-tagged today, and other packaging programs (Clemson,
Rutgers, RIT class) will hit the same wall.

**Held:** PROG-000066 specialty_processes ("advanced plastic processing
techniques" — generic) and specialty_materials (the tour's glass/paper/
plastic/metals list is program-general); PROG-000073 specialty_processes
(biodegradation/composting studies are testing activity, not §3.1 processes;
PCR performance restoration is not honestly mechanical_recycling) and
specialty_materials (generic) and scale_band (27 researchers is a headcount,
not enrollment); PROG-000103 specialty_processes (a course title, "Synthesis
and Processing of Materials", is program-general) — and its facilities_note
stays blank: no MSE-program-grain facilities source exists, as the packet
left it.

**Links (20 witness rows banked; 13 primaries set; 6 NO_WITNESS stand):**
Packaging primaries from the school's own Team directory; C3PS rows banked
for the four Packaging duals (degree before center). Narayan is dual-
witnessed (C3PS + MSE); his primary is MSE under the same degree-before-
center rule, the C3PS row banked. Szczepanski's primary is C3PS (his sole
witness). (Verifier correction, 2026-11-12: the first draft of this
paragraph wrongly called Narayan a center-only witness; the built data
followed the rule correctly throughout.) **The MSE six stand.** No MSE-only roster
exists at MSU; the six rest on the MSE polymer-faculty enumeration the
packet cites, each person corroborated as current ChEMS faculty on the
department directory. That is the same grain standard applied at UMass
Lowell (department faculty page) and UConn (program faculty page): the
program's own enumeration of its polymer faculty. The call is recorded here
so it is reversible; if it is ever judged department-grain, exactly these
six flip to NO_WITNESS. Dorgan is NOT among them — the lane excluded him on
a currency discrepancy (absent from the current directory, chair reassigned,
yet still styled professor in 2026 MSU news and teaching CHE 822): that is
explicitly not a departure finding, and his record is untouched.

**P1 title fixes (3):** Rabnawaz — Associate Professor is stale; the Team
directory and his profile style him Full Professor (role → professor).
Matuana — "and Associate Director" dropped; the directory styles him
Professor and lists Auras as Associate Director. Drzal — "University
Distinguished Professor" is stale; the current ChEMS Directory styles him
Adjunct Professor (role stays professor; no adjunct value exists in the
controlled vocabulary). Each carries its own evidence row; Drzal's is
flagged for verifier live-check given the size of the change.

**Post-verification note (integrator, 2026-11-12):** the independent
verifier's text-fetch could not extract Drzal's title line from the ChEMS
Directory (an extraction artifact), so the styling was confirmed in a
rendered browser view of the same page before this PR shipped: his entry
reads "Lawrence Drzal / Adjunct Professor / Chemical Engineering and
Materials Science". The title fix stands as built.
