# Virginia Tech depth pass — lane notes (2026-11-12)

## Witness architecture (what counted as a program tie)

- **MII (PROG-000063):** MII's own "List of Current Faculty"
  (`mii.vt.edu/people/faculty.html`) — a current roster of ~70 affiliated faculty with
  per-person cards (name + title/research descriptor). **All 30 pool members appear on
  it**, under name variants noted in links.csv (e.g. pool "Guoliang (Greg) Liu" is listed
  as "Guoliang (Greg) Liu"; "C. Adrian Figg" as "Adrian Figg"; "Christopher Bryant
  Williams" as "Christopher Williams"; "Charles E. Frazier" as "Charles Frazier").
  Witness quotes are each person's roster segment in reading order, per the NC State
  roster precedent. Where a card carries no descriptor, the quote is the name as listed.
- **MACR (PROG-000119):** no published participating-faculty roster exists. The MACR
  program's own 2026-2027 Graduate Student Handbook (mii.vt.edu) defines the pool
  structurally — "MACR students must choose an individual affiliated with MII as their
  Faculty Advisor" and advisory-committee majorities must be MII-affiliated — but I did
  **not** treat MII listing alone as a MACR tie (that would link all 30 by inference).
  MACR links rest only on person-level witnesses naming the person's MACR role:
  program director (Bortner), a MACR directorship on the person's own VT profile
  (Moore), teaching a course "as part of the macromolecular science and engineering
  curriculum" (Williams), advising/co-advising MACR PhD students (Sarmah, Coote), and
  co-teaching the MACR core courses 5015/5016 (Davis). If the integrator/owner adopts
  the handbook-equivalence reading (MII-affiliated ⇒ MACR participating faculty), the
  remaining 24 MII-linked people extend mechanically — flagged here as the pass's one
  open judgment call, not silently taken.
- **MSE (PROG-000111):** department employment alone was not a link, per the brief. The
  one link (Whittington) rests on a program-level role, not employment: MII's faculty
  list styles her "Graduate Program Chair in Materials Science and Engineering" — she
  chairs the graduate program this row records. No other pool member is MSE-department
  faculty or holds an MSE program role on the pages checked.
- **CenTiRe (PROG-000029):** the center's own Faculty page
  (`centire.org/index.php/about-centire/who-is-centire/faculty`) lists five Virginia
  Tech faculty (Foroutan, Rakha, Sandu, A. Untaroiu, C. Untaroiu) and its Project
  Descriptions page was name-checked against all 30 pool surnames: **zero hits**. No
  pool member carries a CenTiRe witness; Christopher Williams's tire-retreading
  research is a DREAMS Lab line, not a CenTiRe tie on the center's pages.

## Verdict shape

Every pool member holds at least the MII link, so links.csv contains no NO_WITNESS
rows (NC State pattern: one row per person, extra rows per additional program). Per
program, the no-witness sets are: CenTiRe — all 30; MACR — 24 of 30; MSE — 29 of 30.

## Borderline calls

- **Moore → MACR (PERSON-000149).** His recorded profile (chem.vt.edu) carries his CV
  line "Director, Macromolecular Science & Engineering Graduate Degree Program (MACR),
  Virginia Tech, 2015–present". MII's current students page names **Bortner** as MACR
  Director, so the title on Moore's CV is stale; the link stands on the directorship
  itself plus corroboration that he advised a MACR PhD student (VT News, July 2023,
  the SME award article — the same article that witnesses Williams). A title refresh
  is a separate look.
- **Moore → MSE not linked.** The same CV styles him "Affiliate Professor, Department
  of Materials Science and Engineering, Virginia Tech, 2010–present" — an affiliate
  departmental appointment, which the brief's rule (department employment alone is
  not a link) excludes. Recorded here so the call is visible.
- **Whittington → MACR not linked.** A November 2020 VT News article says she "directs
  the interdisciplinary Macromolecular Science and Engineering graduate program" and
  co-taught its Macromolecular Fundamentals course (with Schulz). That directorship
  has since passed to Bortner, so on roster-currency discipline (the NC State Gorman
  precedent) I returned no MACR link for her or for Schulz — the 2020 course line for
  Schulz also never names MACR in the same sentence. Her current program role is the
  MSE graduate chair, which is linked.
- **MII scale_band** is the institute's own self-characterization ("large (and
  growing) group of affiliated faculty members"), not a band conversion of the ~70-name
  roster; the integrator may prefer to hold it with the other scale facts.
- **MACR facilities_note** chains two VT facts: MACR is MII's graduate program (its
  pages are MII's Graduate Program pages) and the Tiedemann MCL is MII's shared user
  facility (mii.vt.edu/facilities.html serves the MCL site). The quote supports the
  facility half; the program half is the site structure itself. Flagged for the
  integrator's judgment.
- **MSE research_areas** quote is the page's own "Research specializations" list,
  space-joined in reading order (the page renders it as a list); the first three
  segments are proposed and the quote carries exactly those.

## Unfilled gaps (of 18 blank cells, 13 filled)

- **CenTiRe scale_band** — no current size/enrollment statement on centire.org (a 2012
  VT News piece projected "roughly 10 projects per year"; too dated to bank).
- **MII specialty_processes / specialty_materials** — the institute publishes a mission
  focus ("macromolecular materials and interfaces", banked as research_areas) and a
  "Molecules to Manufacturing" paradigm slogan, but no verbatim specialty process or
  material-class statement; not forced.
- **MSE scale_band** — the graduate-program page publishes no size statement.
- **MACR specialty_materials** — the program's published focus areas (students.html)
  are process/area terms (mechanics, processing, structure, synthesis, adhesion,
  composites, electronics); none names a material class, and the handbook adds none.

## Suspected record defects / currency flags (records not edited by this pass)

- **Moore (PERSON-000149)** — profile CV still claims the MACR directorship
  "2015–present"; current director is Bortner (see Borderline calls).
- **Whittington (PERSON-000170)** — her recorded role ("Graduate Program Chair, MSE")
  is current per the MII list; the stale item is the 2020-era MACR directorship still
  circulating in VT News copy, not her Atlas record.
- **Sarmah (PERSON-000163)** — his recorded profile URL is a MADE lab page
  (made.vt.edu/advanced-materials.html); his own lab site (sarmah.che.vt.edu, live,
  "Assistant Professor | Chemical Engineering, Virginia Tech, 2025–Present") is the
  fresher pointer and the source of his MACR witness.
- No pool member appears to have left Virginia Tech: all 30 are on MII's current
  faculty roster, which is the strongest currency signal this pass touches.

## Failed fetches / availability

- No fetch failed outright. Two content notes: the "2026 MACR Faculty Selection Form"
  PDF linked from the MACR curriculum page is a blank signature form, not a roster
  (checked, not used); `mii.vt.edu/facilities.html` serves the Tiedemann MCL site
  directly (that content is what the facilities fills cite).

## Paid calls

None. All sources were fetched directly (curl) or found via free web search.
No Tavily/Exa/Firecrawl use.
