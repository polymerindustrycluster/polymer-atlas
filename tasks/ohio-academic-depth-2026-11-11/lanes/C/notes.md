# Lane C notes — Ohio academic depth pass (2026-11-11)

Scope: 13 programs, 26 people. Fetches are institution pages via curl/search (all
quoted quotes are verbatim from a fetched page unless a line below says the quote
comes from a search engine's indexed copy of the page). No paid calls were made
(no Tavily/Exa/Firecrawl); no live browser was used.

## Shawnee State dedupe finding — PROG-000001 vs PROG-000148 (special task)

**Verdict: not one program recorded twice — do not merge.** Shawnee currently
offers four distinct plastics credentials under overlapping names. The catalog's
own "Degrees and Programs" list (2024–2025 catalog) carries them as separate
entries: "Plastics Engineering Technology AAS", "Plastics Engineering Technology
BS", and "Plastics Engineering Technology Minor"; the Engineering Technology
catalog page additionally lists "Plastics Manufacturing Certificate (12 Hours)".
(Catalog pages are WAF-blocked from this environment — see failed fetches — so
these catalog quotes are from the search engine's indexed copy of the catalog
pages, not a live fetch.)

Credential evidence:

- **BS** — Shawnee's program page (fetched live) styles it "Plastics Engineering
  Technology Bachelor of Science (BS)":
  https://www.shawnee.edu/academics/college-business-engineering-technology/engineering-technology/bachelor/plastics-engineering-technology/
  This matches PROG-000001 (credential_types `bs`, level `bachelor`, CIP
  15.0607). No change needed.
- **AAS** — the catalog's associate-degree page (2024–2025 catalog, indexed copy):
  "Our associate degree program prepares you to become a valuable and integral
  part of the plastics field." and "Graduates of this associate degree program
  have the option of continuing into the bachelor's program program in a 2+2
  fashion." (doubled "program" is the catalog's own.)
  https://catalog.shawnee.edu/preview_program.php?catoid=57&poid=3612
  The AAS is a distinct, stackable (2+2) degree. No Atlas row currently carries
  an `aas_associate` credential for Shawnee plastics.
- **Minor** — Shawnee's minor page (fetched live): "The minor requires 4–6
  courses (16 credit hours) from the Plastics Engineering Technology program."
  https://www.shawnee.edu/academics/college-business-engineering-technology/engineering-technology/minor/plastics-engineering-technology.html
- **Certificate** — "Plastics Manufacturing Certificate (12 Hours)" (catalog
  Engineering Technology page, indexed copy). This matches PROG-000149
  (credential_types `certificate`). An archived "Plastics Engineering Technology
  Certificate" appears in 2007–2010 catalogs — a different, older credential;
  do not conflate it with the current 12-hour certificate.

**What PROG-000148 most likely is:** the row itself is internally inconsistent —
program_type `degree` but credential_types `minor` and credential_level `none`.
On that internal evidence, the most consistent reading is that PROG-000148
records the **Minor** with program_type mis-set; it cannot be a second recording
of the BS (its own credential fields contradict that). Settling check for the
integrator (could not be performed here — the catalog blocks this environment):
open the row's own source URL,
https://catalog.shawnee.edu/preview_program.php?catoid=60&poid=4352, in a real
browser and read its heading. If "Minor": retitle/retype the row as the minor.
If "AAS": set credential_types to `aas_associate`, level `associate` — the row
is then the distinct associate degree. If "BS": only then is it a true duplicate
of PROG-000001.

Two conditional fills are in fills.csv for PROG-000148, one per live reading —
they are mutually exclusive, apply at most one: specialty_processes from the AAS
catalog description (quote via indexed copy of the catalog page), and scale_band
(16 credit hours) from the minor page (fetched live). PERSON-000031 (Jordan
Murrey) is linked to PROG-000001 because his faculty-page area is the Plastics
Engineering Technology program generally; if the Shawnee rows are restructured,
that link should follow the BS row.

## Toledo PROG-000025 — CIP note (special task)

Toledo's graduate-program page states no CIP code, and no plain statement of one
was found on the pages fetched. The page instead routes the degree through the
department: "For more information on the graduate program, please visit the
chemical engineering web page." The Institute describes itself as "affiliated
with the College of Engineering at the University of Toledo." Assigning the
Chemical Engineering CIP would be an inference, not a catalog statement, so none
is proposed. (Quotes: https://www.utoledo.edu/engineering/polymer-institute/gradprogram.html
and https://www.utoledo.edu/engineering/polymer-institute/)

## Borderline calls

- **PROG-000001 research_areas** rests on coursework language ("polymer
  chemistry" inside the coursework sentence), not a research statement — this is
  an undergraduate teaching program. Flagged here; drop if the integrator wants
  research_areas to mean active research only.
- **PROG-000094 (UC Polymer Research Center) research_areas** is thin: the
  center's Research Directory page gives a purpose sentence, not research areas,
  and publishes no member roster (its listed contact is William Connick). The
  center's own legacy site link ("Facility Site", an artsci.uc.edu chemistry
  centers page) returns 404. specialty_processes / specialty_materials left
  blank — nothing published on the pages reachable.
- **PERSON-000067 Scott Huelskamp → NO_WITNESS for PROG-000023 (UDRI).** His
  University of Dayton profile says: "Prior to becoming full time faculty,
  Huelskamp served as a senior composites engineer at UDRI specializing in
  advanced manufacturing techniques for the fabrication of composite and
  polymeric structures." That is a past role; his current appointment is the
  School of Engineering's Innovation Center, and UDRI's own group page names no
  members. A historical tie is recorded here rather than upgraded to a LINK.
- **PERSON-000040 Joseph G. Lawrence carries two LINK rows** (PROG-000024 and
  PROG-000025) because two different pages witness two different ties: the
  Institute Team page ("Senior Director and Associate Professor") for the
  center, and the graduate-program page naming him the graduate-studies contact
  ("Senior Director & Associate Professor, Polymer Institute") for the degree
  program.
- **PERSON-000041 Maria R. Coleman is linked to PROG-000024 only.** Her
  "Graduate Director" title (per her pool record) is a Chemical Engineering
  role; no page ties her to the Polymer Institute graduate program (PROG-000025)
  specifically.
- **PROG-000162 facilities_note** records delivery format ("All classes are
  offered in an online format") because the certificate publishes no physical
  facility; flagged as a delivery note, not a lab.
- **PROG-000020 scale_band left blank.** CAMP's Affiliate Faculty and Students
  page lists five faculty, but a headcount would be my count, not a published
  size fact; the page may also paginate its student directory.
- **PROG-000002 research_areas and scale_band left blank.** The program page is
  a course list for a workforce certificate; its only candidate phrase
  ("hands-on approach to several polymer-processing techniques with an emphasis
  on blown film and injection molding processes") is process content already
  covered by the row's existing specialty_processes, and no size fact is
  published.
- **PROG-000023 and PROG-000107 scale_band left blank** — neither the UDRI group
  page nor the UC MSE program page publishes a size figure (headcount, funding,
  enrollment).
- **PROG-000001 specialty_materials left blank** — the BS page names no specific
  polymers/materials ("different plastics" only).
- Witness quotes for directory/team pages (Wisner, Murrey, Lawrence, Coleman)
  join the page's name and title lines with a space, preserving reading order;
  the pages render them as adjacent lines/fields, not one sentence.
- Toledo equipment detail beyond the fills (from the Institute's resources
  page): an Arburg injection molding machine, twin-screw extruder and biaxial
  film stretching in processing; SEM, DSC, TGA, DMA and GPC access via the
  Center for Materials and Sensor Characterization. Not proposed as a fill
  because the resources page frames these as shared Institute/CMSC resources.

## Programs with no fills, and why

- **PROG-000150 (Northwest State "Plastics", AAS)** and **PROG-000151 (Northwest
  State Plastics Manufacturing, certificate):** the college's catalog is
  WAF-blocked (below) and its marketing site carries no program-detail page for
  either. The current catalog index (2025–2026, via search index) styles them
  "Plastics, AAS in Mechanical Engineering" and "Plastics Manufacturing,
  Certificate" — a name/credential texture lead for the integrator (the AAS row's
  credential_types `aas_associate` is already correct); no verbatim program
  description was obtainable, so no fills are proposed rather than paraphrase.
  Ohio TechNet's partner page also lists the Plastics Manufacturing certificate
  (other_public, thin) — corroboration of existence only.

## Failed fetches (availability only — not evidence of absence)

- **catalog.shawnee.edu** (all pages, incl. PROG-000148's source URL): the
  catalog platform (Acalog) answers this environment with an AWS WAF JavaScript
  challenge (HTTP 202, empty/challenge body via curl); the browser text fetch
  returned 403. Affects primary sources for PROG-000148 and PROG-000149.
- **catalog.northweststate.edu**: same Acalog/WAF behaviour (HTTP 202, empty
  body). Affects PROG-000150 and PROG-000151.
- **UC Polymer Research Center "Facility Site" link**
  (artsci.uc.edu chemistry centers page): HTTP 404.
- No other fetch failures; every other URL cited returned 200.

## Ohio Innovation Exchange (OIEx) — yield

OIEx was consulted as the brief requires: homepage fetched, and the profile
system inspected (profiles live at people.ohioinnovationexchange.org and are
syndicated from the universities' own faculty-data systems — for UC, from UC
Vita, the same source behind UC's Research Directory). Two structural limits for
this lane: profiles record group membership at institution grain ("OHIO
INNOVATION EXCHANGE GROUPS MEMBERSHIP: 1. University of Cincinnati"), not at
program/center grain, and the bio/research text mirrors the institution's own
pages. Result: **zero fills and zero links in this lane rest on OIEx**
(source_kind `oiex` used 0 times); it corroborated nothing the institution pages
did not state better. Honest grade: useful as a discovery index, low yield as a
witness for program-level depth or person→program affiliation.

## Record defects spotted (for the integrator)

1. **PROG-000148 internal inconsistency** — program_type `degree` with
   credential_types `minor` and credential_level `none` (see dedupe finding).
2. **PERSON-000066 and PERSON-001331 are the same person** — "Erick S.
   Vasquez-Guardado" and "Erick Vasquez", University of Dayton, both resolve to
   the same UD directory profile
   (udayton.edu/directory/engineering/chemical-and-materials/vasquez-guardado-erick.php),
   same title and specialty (sustainable process engineering). Duplicate people
   records — dedupe candidate. Both are NO_WITNESS here (the profile never
   mentions UDRI).
3. **PERSON-000030 "Adam Miller" (Shawnee) has no witness.** Shawnee's
   Engineering Technology faculty page lists "Larry (Skip) Miller, Professor
   Emeritus, Area: Plastics Engineering Technology" and no Adam Miller; the pool record's profile URL is a Shawnee cabinet page, not
   a program page. Possible stale or misattributed record — integrator should
   recheck its source before any link is recorded. (The same faculty page also
   lists Eli Vestich with a Plastics Engineering Technology area; not in the
   pool.)
4. Minor: PERSON-002111's pool title ("Assistant/Associate Professor, Polymer &
   Biomaterials") vs his UC Research Directory profile, which is Chemistry-only
   (Assistant Professor since August 2018). Title staleness only; verdict
   unaffected.
