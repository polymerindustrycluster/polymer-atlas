# Michigan depth pass — lane notes (2026-11-12)

## Witness architecture (what counted as a program tie)

- **Macromolecular (PROG-000062):** the program's own Faculty and Staff page
  (`macro.engin.umich.edu/faculty-and-staff/`) is the program roster. It prints each
  member's full appointment string, so the title line on that page was taken as a
  witness for **each unit it names** — this is what dual-links Laine, Gong, Lahann,
  Ma and Kotov to PROG-000102 as well as 000062. The integrator should know this is
  the one place the pass lets a single page witness two programs.
- **MSE (PROG-000102):** MSE-site witnesses were preferred wherever one exists —
  Glotzer's own MSE profile line (used for both of her rows), the MSE Staff page's
  faculty groupings (Kim, Pena-Francesch, Tuteja), the MSE Adjunct Faculty page
  (Loebel), Kieffer's Institute for Energy Solutions profile header ("Professor of
  Materials Science and Engineering"), and Sodano's own Aerospace biography, which
  names his appointments in both departments (used for both of his rows).
- The crawled Macro roster lists 19 faculty while the program home page states
  **37 affiliated faculty** — the roster reads as core faculty only, so absence
  from it was never treated as a negative. Three 000062 links rest on the person's
  own Michigan profile instead: McNeil (LSA Chemistry profile header names
  Macromolecular Science and Engineering), Chen (same pattern), Larson (below).

## Borderline calls

- **Larson (PERSON-000439) — LINK to 000062 on his ChE profile's Experience block,**
  which lists Macromolecular Science and Engineering among his University of
  Michigan appointments (alongside Mechanical Engineering). It is a profile naming
  the program, not the program's roster; the weakest 000062 link in the packet.
- **Tuteja (PERSON-000456) — linked to 000102 only.** His recorded title claims
  Macromolecular Science and Engineering, and the MSE Staff page ties him to MSE,
  but the Macro roster does not list him and neither the ChE Polymers and Complex
  Fluids page nor his group site names the Macro program — so no 000062 row was
  taken. A witness gap, not a contradiction of the recorded title.
- **Kim (PERSON-000444) — no 000062 row,** although a staging-domain MSE overview
  (msebetaweb.engin.umich.edu) states he holds a Macromolecular joint appointment.
  The live MSE graduate page carries only the generic sentence that most MSE
  faculty hold joint appointments, and the Macro roster does not list him; the
  staging domain was not cited.
- **Loebel (PERSON-000457) — LINK to 000102 stands, but on an Adjunct listing**
  (see defect flag below).

## Suspected record defects / currency flags

- **Loebel (PERSON-000457):** the pool records her as "Assistant Professor of
  Materials Science and Engineering"; MSE's current site lists her on its
  **Adjunct Faculty** page. Her primary appointment appears to have changed since
  the record was made — `role_as_published` may be stale. The 000102 link stands
  on the current adjunct listing.
- **Waas (PERSON-000442):** NO_WITNESS is clean (Aerospace + Mechanical only, as
  recorded), but his Aerospace profile's position history is tangled — Professor
  Emeritus 2014–2018, a University of Washington chair interlude, then Michigan
  Aerospace chair 2018–2023, now styled Felix Pawlowski Collegiate Chair. Worth a
  human glance if his record is ever edited; nothing in it contradicts the pool row.

## Unfilled gaps

None. All five watched fields were filled for PROG-000062 and all four for
PROG-000102, each from the institution's own pages. Two sourcing notes:

- PROG-000062 `specialty_processes` rests on the program's own core-course
  description (Macro 412, Polymeric Materials) on the program's courses page —
  the program's own statement of what the field does, used the way the NC State
  pass used a catalog program description.
- PROG-000102 `scale_band` combines the department's self-characterization
  ("one of the oldest and largest programs in the country") with its published
  quick facts (25 core + 24 affiliated faculty; 138 students). The verbatim quote
  carries the self-characterization.

## Failed fetches (availability only — never treated as absence)

- Direct curl to macro.engin.umich.edu returned **403** and to mse.engin.umich.edu
  **403 / connection failure (000)** throughout. Every citation in this packet
  rests on the browser text fetch of the same institution pages instead.
- The MSE People directory's core **Faculty** classification view could not be
  opened directly (the classified views search returned were emeritus, research
  scientists, lecturers, staff and adjunct). Individual MSE profile pages and the
  MSE people sub-pages above were used in its place.

## Paid calls

None. All sources were fetched directly or found via free web search.
No Tavily/Exa/Firecrawl use.
