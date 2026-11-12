# UCSB depth pass — lane notes (2026-11-12)

## Witness architecture (what counted as a program tie)

UCSB's one Atlas program row is the **BioPACIFIC MIP** (PROG-000071), an NSF Materials
Innovation Platform run jointly at UCSB and UCLA. Per the brief, only the MIP's own
published rosters tie a person to it. The governing source is the MIP's own people
directory (`biopacificmip.org/people`), whose Faculty listing names 25 faculty across
both campuses, each with an individual faculty page under
`biopacificmip.org/people/faculty/<slug>`. **8 of the 18 pool people** appear on that
roster and carry individual faculty pages; each links.csv LINK quote is the header of
the person's own BioPACIFIC faculty page (name and role as the MIP itself styles them).
Two are stronger than a bare roster listing: Hawker's page styles him "Co-PI, NSF
BioPACIFIC MIP" and Read de Alaniz's styles him "Director, NSF BioPACIFIC MIP".

The MIP's in-house research and user-project listing pages
(`/research/house-research`, `/research/user-projects`) render their project content
dynamically — the fetched HTML carried no person names at all. That is an availability
limitation, not evidence that no other pool person serves on a project team; the
published people/faculty roster governed, and verdicts rest on it alone.

## NO_WITNESS affiliation inventory (10 people — actual homes, named per the brief)

None of the following appears on the BioPACIFIC people roster or holds a BioPACIFIC
faculty page. Employment in a UCSB department was never treated as a link.

- **Chabinyc (PERSON-000128)** — Materials; office in the Materials Research Laboratory
  (MRL), Elings Hall, per the current Materials directory. No BioPACIFIC tie found.
- **Nguyen (PERSON-000129)** — Director, Center for Polymers and Organic Solids (CPOS),
  per the CPOS faculty page ("Thuc-Quyen Nguyen | CPOS Director | Professor, Chemistry
  & Biochemistry"). CPOS is a different center from BioPACIFIC; not a link.
- **Abu-Omar (PERSON-000134)** — Chemistry & Biochemistry profile (Mellichamp Chair in
  Green Chemistry); no center roster tie to BioPACIFIC found.
- **Waite (PERSON-000135)** — Distinguished Professor, MCDB; his recorded profile is an
  affiliate page of the Interdepartmental Graduate Program in Marine Sciences (IGPMS).
  That page returned HTTP 403 on fetch (availability only); no BioPACIFIC tie found on
  any fetched page.
- **Saleh (PERSON-000136)** — Materials Department Chair; "Professor, Materials, Physics
  and Interdisciplinary Quantitative Biosciences Program" per the Materials directory.
  A department chairmanship is an administrative role, not a BioPACIFIC tie.
- **Scott (PERSON-000137)** — Chemical Engineering catalysis group (Mellichamp Chair in
  Sustainable Catalytic Processing); the department's catalysis research page describes
  the Scott group's olefin-polymerization and plastics-upcycling work. No BioPACIFIC
  tie found. (Caution taken: the one "Scott" on the BioPACIFIC people roster is
  **M. Scott Shell**, a different person — he is not in this pool and no row was made.)
- **Carlini (PERSON-000138)** — current Chemistry & Biochemistry profile; no BioPACIFIC
  tie found.
- **Dogic (PERSON-000139)** — Professor of Experimental Physics, Physics (Broida Hall;
  dogiclab.physics.ucsb.edu), per his current UCSB science page. The Brandeis mentions
  on that page are biographical (his PhD institution and a 2007–2017 appointment before
  he moved to UCSB) — he has NOT left UCSB. No BioPACIFIC tie found.
- **Safinya (PERSON-000140)** — current College of Engineering profile (Materials,
  Physics, MCDB); no BioPACIFIC tie found.
- **Han (PERSON-000141)** — CPOS faculty page ("Grace Han | Associate Professor,
  Chemistry and Biochemistry"), with sustainable-polymer work stated there. CPOS
  membership is not a BioPACIFIC tie.

## Fills

4 of the 5 gap cells filled, all from biopacificmip.org's own pages (About, home,
Research, MIP Facilities). **scale_band was left blank**: the site's published size
facts are the NSF award number/dollars (DMR-2445868) and qualitative community
language — no published band or self-characterizing size statement; a dollar figure
is not a band under the standing discipline.

## Title-currency flags (records not edited by this pass)

- **Pitenis (PERSON-000133)** — the BioPACIFIC faculty page styles her "Assistant
  Professor" while the Atlas record (and UCSB Materials) say Associate Professor;
  the MIP page lags a promotion. Her LINK is unaffected.
- **Helgeson (PERSON-000131)** — the BioPACIFIC site's directory header styles him
  "Professor" (as does the Atlas record), but the bio paragraph on his own BioPACIFIC
  faculty page still calls him "Associate Professor" — an internal inconsistency on
  the MIP site itself; the record stands.
- **Chabinyc (PERSON-000128)** — the current Materials directory styles him
  "Distinguished Professor, Materials" against the record's "Professor, Materials" —
  a promotion since the record was made; flagged for a title-refresh look.

## Failed fetches (availability only — never treated as absence)

- `igpms.ucsb.edu/people/affiliates/herbert-waite`: HTTP 403.
- BioPACIFIC `/research/house-research` and `/research/user-projects`: fetched (200)
  but their project listings render dynamically; no person names in the static HTML.

## Paid calls

None. All sources were fetched directly (curl). No Tavily/Exa/Firecrawl use.
