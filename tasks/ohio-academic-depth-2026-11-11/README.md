# Ohio academic depth pass (2026-11-11)

Owner instruction 2026-11-11: "do the ohio academic sweep first." Scope: the Atlas's Ohio academic layer —
every active program row seated in Ohio, enriched in the fields PIC actually uses, plus the missing
program-level linkage for the people already recorded at those institutions.

## Scope (measured 2026-11-11, unit: active program rows)

- **39 active program rows at 19 Ohio institutions/providers** (program `state` = OH, or the institution
  record's state = OH; the union — 34 rows carry OH themselves, 5 more resolve through their institution).
- Field gaps across the 39: `research_areas` blank on ~32, `specialty_processes` ~31,
  `specialty_materials` ~30, `facilities_note` ~31, `scale_band` ~37 (vocabulary in use: small/medium).
- **132 people** are recorded at 11 of those institutions (Ohio State 33, Akron 26, CWRU 25, Kent State 15,
  Cincinnati 11, YSU 6, Ohio University 5, Toledo 4, Dayton 4, Shawnee 2, Walsh 1); **0** of them carry a
  `program_org_id`. Nationally only 10 people rows carry one.
- IPEDS is not the gap: 6 of the 7 Ohio degree programs already carry CIP + completions (Toledo's Polymer
  Institute graduate program is the exception; lanes may settle it if the catalog states the CIP plainly,
  but no lane forces a CIP).

## Source discipline

- **Institution pages are the citation of record** (AGENTS §4/§5 discipline; the 2026-10-29 source ruling:
  the Ohio Innovation Exchange is a **lead source** — records cite institutions' own pages).
- **Ohio Innovation Exchange (OIEx)** is in scope as a lead and corroboration source: expert profiles,
  research-area listings, and facility/equipment listings. A fill that can rest only on OIEx is returned
  flagged `source_kind=oiex` and the integrator tiers it accordingly; it is never silently upgraded.
- A failed fetch (403, timeout, bot wall, 500) is an availability signal, never evidence of absence
  (AGENTS §2 rule 8). Effort cap ~6 fetches per program.
- People→program links require a **person-level witness**: an institution or OIEx page that ties the named
  person to the program/unit (a program faculty listing, a center member page, a profile naming the unit).
  Employment at the institution alone is NOT a link. Verdicts: LINK (with quote + URL) or NO_WITNESS.

## Lane deliverables (lanes produce packets; the integrator writes `data/`)

Per lane, in `lanes/<lane>/`:
- `fills.csv` — program_id, field, proposed_value, source_url, verbatim_quote (≤25 words), source_kind
  (institution_page | oiex | other_public). For the vocabulary fields (`research_areas`,
  `specialty_processes`, `specialty_materials`) give the institution's verbatim phrase; the integrator
  maps to the controlled vocabulary. `facilities_note` and `scale_band` fills need a published fact
  (equipment/facility description; faculty/student/size figures) quoted, not an impression.
- `links.csv` — person_id, program_id, verdict, witness_quote, witness_url, source_kind.
- `notes.md` — borderline calls, failed fetches, and anything that smells like a record defect.

## Flagged for lane C

Shawnee State carries **two** degree rows named "Plastics Engineering Technology" (PROG-000001 and
PROG-000148). Settle whether they are one program recorded twice (a dedupe alarm for the integrator) or
two distinct credentials (BS vs AAS) whose rows need credential disambiguation — from Shawnee's current
catalog, quoted.

## Integration

The integrator applies fills as cell edits with append-only evidence rows (claim types per §4.13),
sets `program_org_id` on LINK-verdict people with a person-level evidence row each, refreshes
`last_verified` only on rows actually changed, and lands the pass as one PR with validate + row-loss
guard green.

## Integration record (2026-11-11)

All three lanes returned (A: 37 fills, 36 LINK / 12 NO_WITNESS; B: 45 fill rows, 29 LINK verdicts
covering 24 people; C: 30 fills, 6 LINK verdicts / 5 people, 21 NO_WITNESS). Every applied fill rests
on an institution page. **OIEx supported zero fills and zero links** — graded honestly by the lanes:
A low/lead-only (one corroborating equipment listing), B none (profile/facility pages are
script-driven and exposed no fetchable text), C low (profiles record institution-grain group
membership, not program grain). Applied after integrator mapping to the §3.1/§3.2/§3.5 vocabularies:

- **27 program rows changed**: 21 gained vocabulary cells (research_areas / specialty_processes /
  specialty_materials unions) and 22 gained a facilities_note (set only where the cell was blank);
  61 append-only evidence rows (EVD-333059..EVD-333120, one allocated ID unused), each quoting the
  institution page verbatim. Renaming PROG-000148 also recomputed Shawnee State's §4.11 ecosystem
  rollup (ORG-001298 polymer_program_name) in the same pass, per validator V-16.
- **65 people gained `program_org_id`**; 71 LINK witnesses banked as evidence_people rows. The field
  is single-valued: it holds the degree program where the person has one, else the witnessed center;
  additional witnessed programs (Maia→CAPP, Zhu→Soft Matter Characterization Lab, French→SDLE,
  Bruckman→SDLE + MDS-Rely, Lawrence→Toledo graduate program) are carried as evidence rows. Three
  linked CWRU people (Jamieson, Schiraldi, Blackwell) are styled Professor Emeritus on the same
  department roster that witnesses the link; the link records that roster affiliation of an existing
  record — no new person was admitted by this pass.
- **PROG-000148 renamed** "Plastics Engineering Technology Minor" (see integrator-notes.md: it is the
  Minor, not a duplicate BS; the 2026-2027 Shawnee catalog lists exactly BS / Minor / Certificate —
  no AAS exists, so no record was created). program_type stays `degree`, per the PROG-000131 /
  PROG-000153 precedent for minor-carrying rows.
- **Record URLs repointed** to the citable program pages: PROG-000011 (was the generic iLab landing
  page), PROG-000028 (was the Macromolecular department page).

### Held fills (proposed by lanes, NOT applied — with reason)

- **All scale_band fills (14 published size facts)** — §4.11: the field is banded by precedent (in
  use: small ×5, medium ×2 across programs) and "banded, never a precise headcount"; no published
  mapping converts faculty counts, student ratios, funding totals, or credit hours into bands, and
  minting thresholds is an owner vocabulary ruling (AGENTS §2 rule 9). The facts are preserved in
  the lane fills.csv files (e.g. AFMC "over 30 faculty and over 350 students"; Akron SPSPE "one of
  the largest and broadest in the U.S.").
- **Characterization-facility specialty fills** (PROG-000011, 000014, 000017, 000026) — §4.11:
  characterization facilities fill neither specialty field; all four already carry
  research_areas[characterization_methods].
- **Liquid-crystal vocabulary gap** — PROG-000015 specialty_materials and PROG-000032
  research_areas / specialty_materials have no honest §3 slug. AMLCI's two facility rows and its 14
  people links landed; its topic cells did not. A liquid-crystals term is an owner vocabulary
  question, proposed here, not self-ruled.
- **Course-title / outreach research_areas** (PROG-000008, 000009, 000021, 000116) — §4.11
  research_areas is for research programs; the lane-flagged bases were course topics, an outreach
  mission, and a certificate's own name.
- **STEER PROG-000031, both fills** — the only sources are STEER's global (Bengaluru HQ) ADC pages,
  not an Ohio-site page. An Ohio-site page naming the Uniontown center's work settles it.
- **Generic or out-of-scope phrases**, each recorded in the lane notes — e.g. PROG-000018
  specialty_materials (pyrophoric catalysts/reagents are not a polymer material), PROG-000106
  specialty_materials (an ABET criteria list naming metals/ceramics), PROG-000013 research_areas (a
  services list), PROG-000012 specialty_materials (a photovoltaic backsheet laminate),
  PROG-000025/000094 research_areas (program self-names), PROG-000033 specialty_materials
  (metal/ceramic/plastic across AM; the row already carries its AM processes), PROG-000115
  research_areas (a funded-areas list — nanotechnologies, biomimicry, energy generation, batteries,
  photonics — with no honest slugs), PROG-000001 specialty_processes ("plastics manufacturing and
  processing", generic). Northwest State PROG-000150/151 received no fills: the Acalog catalog is
  WAF-blocked from the lane environment and the college site carries no program-detail pages —
  availability, not absence.

### Defects flagged by lanes (not acted on in this PR)

- **PERSON-000066 / PERSON-001331** — Erick Vasquez (University of Dayton) appears as two people
  records under name variants with the identical profile URL. A dedupe merge packet (the PR
  #264/#265 pattern) is the follow-up; not merged inside this pass.
- **PERSON-000030 "Adam Miller" (Shawnee)** — no witness found anywhere; Shawnee's Engineering
  Technology faculty page names Larry (Skip) Miller for Plastics Engineering Technology. Possible
  stale or misattributed record. A guarded no-hit is not a negative fact, so the record stands
  pending a source recheck.
- **PROG-000033 (YSU center)** — the record's own notes already carry the stale-page risk; a 2026
  YSU news story describes the center's relaunch under its new director (linked here as its one
  program person). A description refresh is a separate look, not this pass.
- **Toledo PROG-000025 CIP** — the graduate-program page states no CIP and routes the degree
  through Chemical Engineering; the CIP cell stays blank, not forced.
