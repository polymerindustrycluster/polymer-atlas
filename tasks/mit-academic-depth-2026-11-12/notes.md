# MIT depth pass — lane notes (2026-11-12)

## Witness architecture (what counted as a program tie)

- **PPSM (PROG-000061):** the program's own Faculty page (ppsm.mit.edu/faculty/) lists core
  faculty grouped by home department, plus separate "PPSM Affiliates", "PPSM Emeritus
  Faculty" and "PPSM Emeritus Affiliate Faculty" sections. 14 of the 17 pool people appear
  in the core-faculty listing; one more (Langer) appears under Affiliates (see borderline
  calls). No pool person appears in either emeritus section.
- **DMSE (PROG-000101):** the department's Faculty directory (dmse.mit.edu/people/faculty/)
  current-faculty roster. All 6 DMSE-linked pool people also appear on the PPSM page, so
  every DMSE link here is a dual witness. No pool person appears in the directory's
  Emeritus or Visiting Faculty sections.
- Employment at MIT or in a home department alone was never treated as a link.

## Borderline calls

- **Robert S. Langer (PERSON-000373) — LINK to PPSM rests on the "PPSM Affiliates" section
  of the program's Faculty page**, not the core-faculty listing. The brief counts PPSM's
  published faculty listings as the program tie, and the Affiliates section is part of that
  page; he is not in either emeritus section. Flagged so the integrator can weigh the
  affiliate tier explicitly.
- **Anastasios John Hart (PERSON-000368) — NO_WITNESS, with a near-miss on record.** The
  PPSM homepage's photo carousel includes a figure captioned "Hart Lab" alongside other
  PPSM faculty labs, but Hart does not appear on the PPSM Faculty page and is not in the
  DMSE directory; he is a Mechanical Engineering professor. A homepage photo feature is
  not a faculty listing, so the verdict is NO_WITNESS. If the owner ever rules homepage
  lab features sufficient, this is the record that changes.
- **Kwanghun Chung (PERSON-000374) — NO_WITNESS.** His recorded specialties (polymer
  science, hydrogel-tissue chemistry) are polymer-true, but he appears on neither the
  PPSM Faculty page nor the DMSE directory; a Chemical Engineering professorship alone is
  not a program tie under this pass's rule.

## Fill-source flags (for the integrator's mapping calls)

- **PROG-000061 `specialty_processes`** rests on a required core-course title on the
  program's own 2026-27 core curriculum page ("Synthesis of Polymers", subject 10.569) —
  a course-title basis, flagged in the same spirit as earlier passes' held course-title
  fills; the program publishes no prose process list on the pages checked.
- **PROG-000101 `specialty_processes` ("Synthesis and Processing") and `specialty_materials`
  ("Soft Matter")** rest on DMSE's published Materials / Research Types taxonomy labels
  (shown on the department's faculty directory filters and its research-impact taxonomy),
  not on prose descriptions. They are the department's own verbatim category names;
  flagged as taxonomy-label fills, and "Synthesis and Processing" is generic for an MSE
  department — the integrator may hold it as earlier passes held generic phrases.
- **PROG-000061 `specialty_materials` ("biopolymers")** comes from the About page's mission
  sentence naming macromolecules and biopolymers as the program's founding subject matter.
- **`scale_band` proposed for neither program.** Neither PPSM nor DMSE publishes a band or
  size self-characterization on the pages checked. Roster headcounts are visible (PPSM
  lists ~31 core faculty; the DMSE directory lists ~41 current faculty) but were NOT
  converted into a band, per the standing discipline — the conversion question remains
  the owner's, as in the Ohio/NC State/VT/GT passes.

## Name-form note

- The DMSE directory spells **"Rafael Gómez-Bombarelli"** (accented ó) where the pool
  record and the PPSM page spell "Rafael Gomez-Bombarelli". Same person (Associate
  Professor, DMSE; PPSM core faculty, computational materials / machine learning). The
  DMSE witness quote keeps the directory's accented form.

## Currency observations (records not edited by this pass)

- No pool person shows a departure signal: all 17 were accounted for on current MIT pages
  at program or home-department grain, and none appears on an emeritus roster.
- Zachary P. Smith's recorded profile URL is a ChemE news article about endowed chairs
  rather than a profile page; his current PPSM faculty listing (with research areas) is
  the fresher witness and is what the link cites.

## Failed fetches (availability only — never treated as absence)

- `https://dmse.mit.edu/about/` returned 404; the department's About content lives at
  `https://dmse.mit.edu/about-us/about-materials-science-and-engineering/` (fetched, 200)
  and was used instead. No other fetch failed.

## Paid calls

None. All sources were fetched directly (curl) from MIT's own pages. No Tavily/Exa/
Firecrawl use.
