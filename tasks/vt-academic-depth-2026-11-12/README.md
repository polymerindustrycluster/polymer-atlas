# Virginia Tech academic depth pass (2026-11-12)

`claimed:spaghetti 2026-11-12` (QUEUE line lands with this pass's integration PR, per the
standing packet pattern.)

Second school in the by-school scaling sequence (Ohio PR #269; NC State trial 2026-11-11).
Owner go-ahead 2026-11-12: "Time to run more scans?" — research lanes run while the owner
travels; all pushes batch for his approval on return.

## Scope (measured 2026-11-12)

- **4 active program rows** at Virginia Tech (ORG-002845): PROG-000029 Center for Tire
  Research (CenTiRe, center), PROG-000063 Macromolecules Innovation Institute (center),
  PROG-000111 Materials Science and Engineering (degree), PROG-000119 Macromolecular Science
  and Engineering / MACR (degree). 18 blank depth cells across the five watched fields.
- **30 people** recorded at Virginia Tech, **0** carrying `program_org_id`.

## Discipline (same as the Ohio and NC State passes)

- Virginia Tech's own pages are the citation of record (vt.edu department, center, and
  program pages; catalog pages where they carry program-grain rosters).
- People→program links require a **person-level witness** tying the named person to the
  specific program: MACR's participating-faculty publications are a program tie; MII member
  listings are a program tie; CenTiRe's own pages govern center ties. Employment in a home
  department (CBE, Chemistry, MSE, Mechanical) alone is NOT a link.
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

**Fills applied (8 evidence rows):** PROG-000029 research_areas +=
elastomer_science;polymer_physics;characterization_methods (tire materials / tire
physics & modeling / testing; "manufacturing" and "sustainability" unmapped — no slug
claims them) + facilities_note as proposed. PROG-000063 research_areas +=
polymer_physics ("macromolecular materials and interfaces") + facilities_note.
PROG-000111 research_areas += polymer_physics (structure–property relations; the
page's synthesis/processing/modeling phrases are program-general) + facilities_note.
PROG-000119 facilities_note (its "Polymer synthesis" focus already stands in
research_areas).

**Fills held, with reasons:** PROG-000029 specialty_processes (testing/manufacturing —
generic, no §3.1 slug); PROG-000111 specialty_processes + specialty_materials
(program-general MSE lists; the program's polymer depth rides on its people links);
PROG-000119 specialty_processes ("polymer processing" generic). Scale: PROG-000063's
"large (and growing) group of affiliated faculty" is a faculty characterization —
held under the S3 line (faculty-referent size statements never set scale_band);
PROG-000119's "35 graduate students per year" is a completion flow, not enrollment —
banked, not converted; PROG-000029/000111 publish no size fact.

**Links (37 witness rows banked; 30 primaries set):** MACR primaries ×5 (Bortner,
Williams, Sarmah, Coote, Davis — person-level degree witnesses). Whittington → MSE
primary (Graduate Program Chair witness), MII banked. Moore → MII primary, MACR
banked as evidence only: his MACR witness is his own profile's director claim, and
the directorship itself is stale (Bortner holds it) — the Whittington standard from
this same packet applied consistently. His recorded title (Director, MII) is not the
stale styling and is not touched. Remaining 24 → MII primaries.

**lab_url (first S6 captures):** PERSON-000163 Sarmah → https://sarmah.che.vt.edu/;
PERSON-001354 Davis → https://nanoparticles.che.vt.edu/ — the lab sites the packet's
witnesses stand on.
