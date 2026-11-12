# Georgia Tech academic depth pass (2026-11-12)

`claimed:spaghetti 2026-11-12` (QUEUE line lands with this pass's integration PR, per the
standing packet pattern.)

Third school in the by-school scaling sequence (Ohio PR #269; NC State trial 2026-11-11).
Owner go-ahead 2026-11-12: "Time to run more scans?" — research lanes run while the owner
travels; all pushes batch for his approval on return.

## Scope (measured 2026-11-12)

- **4 active program rows** at Georgia Tech (ORG-002844): PROG-000050 Center for Composite
  and Hybrid Materials Interfacing (center), PROG-000099 Materials Science and Engineering
  (degree), PROG-000143 Materials Science and Engineering — Polymer and Fiber Materials
  (degree), PROG-000304 Multidisciplinary Composites Certificate Program (certificate).
  19 blank depth cells across the five watched fields.
- **27 people** recorded at Georgia Tech, **0** carrying `program_org_id`.

## Discipline (same as the Ohio and NC State passes)

- Georgia Tech's own pages are the citation of record (mse.gatech.edu and center pages;
  catalog pages where they carry program-grain rosters).
- **The two MSE degree rows need care:** PROG-000143 is the polymer/fiber-specific program.
  A witness ties a person to 000143 only when the page names them in the polymer/fiber
  context specifically (a research-area grouping, a profile naming the polymer area); a
  general MSE faculty roster ties to PROG-000099. When both exist, return both rows and say
  which is stronger in notes.md.
- People→program links require a **person-level witness**; employment in MSE or a home
  department alone is NOT a link. The Composites Certificate (PROG-000304) rarely publishes
  per-person faculty ties — absence of one is NO_WITNESS, never forced.
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

**Fills applied:** PROG-000050 research_areas += composites_mechanics (interface
engineering and joining of hybrid structures), specialty_materials += composites_frp,
facilities_note as proposed; **record URL repointed** from the UTK-hosted page
(fcmf.utk.edu) to the center's own Georgia Tech site (chmi.isye.gatech.edu) — the
ecosystem rollup is unaffected (a degree program sorts first). PROG-000099
facilities_note + scale_band = large (published enrollment 262 undergraduate + 228
graduate = 490, S3 mapping). PROG-000143 specialty_processes +=
polymerization;recycling_unspecified and research_areas += polymer_synthesis, both
mapped from the school's own polymer-research sentence; facilities_note as proposed;
scale_band = large (the school's own "one of the largest polymer research portfolios
amongst MSE programs in the US" — qualitative self-characterization, S3).
PROG-000304 specialty_materials += composites_frp + facilities_note composed from
the two proposed rows (hands-on laboratories; CERC forum).

**Fills held, with reasons:** PROG-000050 specialty_processes (joining/interfacing —
no §3.1 slug claims structural joining) and scale_band ("3-Site NSF IUCRC" is
structure, not size). PROG-000099 research_areas / specialty_processes /
specialty_materials — the research page's all-materials lists are program-general;
the school's polymer-specific depth stands on PROG-000143, its own row (its
"process-structure-property-performance paradigm" is a framing phrase, not a
process). PROG-000143 specialty_materials (named polymer classes — topologically
complex, shape-memory, conjugated, block — with no controlled term). PROG-000304
research_areas (certificate; §4.11 research-programs-only, per the UMass Lowell
precedent) and specialty_processes ("composites processes", generic).

**Links (41 witness rows banked; 21 primaries set; 6 NO_WITNESS stand):** dual
099+143 witnesses → PROG-000143 primary (19 people; the 143 witness is the
polymer-specific one in every dual case, per the packet's architecture note).
099-only → 099 primary (Stingelin, Temenoff). Yao → 143 primary under the standing
degree-over-center rule; his CHMI site-director row — the lane's strongest single
tie — is banked as evidence on PROG-000050 with the 099 row. Ratcliff's 143 row
stands (her own profile's research-taxonomy tag names polymer electrochemistry —
the packet's weakest LINK, flagged, not overruled).

**Flags checked, no edits:** Gutekunst's record already carries his home
department's styling (Associate Professor, Chemistry & Biochemistry) — the stale
page is MSE's courtesy directory, not the record. Russo's Professor/Hightower
styling matches his record; the directory's emeritus-adjacent placement is a
layout inference, not evidence. Temenoff's MSE profile carries another research
area's keywords — a Georgia Tech-side data error, recorded here only.
