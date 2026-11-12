# University of California, Santa Barbara academic depth pass (2026-11-12)

`claimed:spaghetti 2026-11-12` (QUEUE line lands with this pass's integration PR, per the
standing packet pattern.)

By-school scaling wave 3, batched at the owner's instruction 2026-11-12 ("Can we batch more
school research?" / burn remaining capacity on verified data before his limit reset).
Research lanes run while the owner travels; integration serializes behind waves 1-2;
pushes batch for his approval.

## Scope (measured 2026-11-12)

- **1 active program row(s)** at University of California, Santa Barbara: PROG-000071 BioPACIFIC MIP (center). 5 blank depth cells across
  the five watched fields.
- **18 people** recorded at University of California, Santa Barbara, **0** carrying `program_org_id`.

## School notes

The one Atlas program row is the BioPACIFIC MIP (an NSF Materials Innovation Platform).
Its own site publishes project/team rosters — those are the program tie. UCSB's polymer
faculty otherwise sit in Materials, Chemical Engineering, and Chemistry & Biochemistry;
employment there alone is NOT a link to BioPACIFIC. Return NO_WITNESS and name the
person's actual center/lab affiliations in notes.md where a page states them.

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

**Fills applied (3):** PROG-000071 research_areas += polymer_synthesis;
biomedical_polymers (the MIP's own framing: the synthetic biology and
materials nexus; biomaterial structure and function — "materials-by-design"
unmapped); specialty_processes += polymerization only (the platform
statement's automated high-throughput synthesis mapped; characterization is
a method); facilities_note (the NSF user facility spanning UCSB and UCLA).

**Held:** specialty_materials (polymers from a library of bio-sourced
monomers — the honest tag, sustainable_feedstocks, is a research-area term,
not a §3.2 material) and scale_band (the site publishes the NSF award
number and dollars; dollars never convert under S3, and no size
self-characterization is published).

**Links (8 primaries set, all PROG-000071; 10 NO_WITNESS stand):** the
eight rest on the MIP's own people directory, including its published
stylings (Read de Alaniz as Director, Hawker as Co-PI). The roster's
"Scott" is M. Scott Shell — a different person from pool record Susannah
Scott (PERSON-000137), whose own group does olefin polymerization and
plastics upcycling but carries no BioPACIFIC tie; no row was made, and the
guard is recorded here because the names invite the error. The ten
NO_WITNESS affiliations are inventoried in notes.md (Nguyen/Han to CPOS,
Chabinyc to the MRL) as future-pass worklist material.

**P1 title fix (1, verifier-checked):** Chabinyc (PERSON-000128) — the
current Materials directory styles him "Distinguished Professor, Materials"
against the record's "Professor, Materials"; role_as_published updated,
role unchanged. He is NO_WITNESS for the MIP in this pass (MRL affiliate);
the fix rests on his own department's directory. The packet's other two
flags required no edit: Pitenis (the MIP page lags her promotion; the
record is the current one) and Helgeson (an internal inconsistency on the
MIP site; its directory header agrees with the record).
