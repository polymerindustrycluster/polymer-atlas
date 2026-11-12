# UMass Amherst depth pass — lane notes (2026-11-12)

## Witness architecture (what counted as a program tie)

- **PSE (PROG-000059):** the department's Faculty Listing page
  (`umass.edu/polymer-science/faculty`) — a single page with Faculty, Research
  Professors and Lecturers, Adjunct Professors, and Professor Emeritus sections.
  All 20 PSE links rest on that page. Quotes are listing segments from it,
  space-joined in reading order (the NC State catalog-roster convention).
- **MSE (PROG-000100):** the MSE Interdisciplinary Graduate Program's own faculty
  page (`websites.umass.edu/mseidgp/faculty/`), which lists program faculty with
  home department and research areas. All 6 MSE links rest on that page; quotes
  are the listing's name / department / research-area cells, space-joined in
  reading order.
- Employment at UMass Amherst or in a home department was never treated as a
  link; the two NO_WITNESS people are recorded in Chemical Engineering with no
  published tie to either program's listing.

## Dual links

- **Sarah L. Perry (PERSON-000230)** — named in the PSE Faculty Listing's
  Adjunct Professors section and on the MSE IDGP faculty roster (Chemical
  Engineering). Both rows returned; her tenure home is Chemical Engineering and
  the MSE listing is a core program roster, while the PSE tie is adjunct — the
  integrator may weigh primacy.
- **Steve Granick (PERSON-000242)** — full PSE faculty (Robert K. Barrett
  Professor on the PSE listing) and on the MSE IDGP roster under Polymer
  Science & Engineering. Both rows returned; PSE is plainly his home program.
  Note his pool `public_profile_url` points at the MSE page.

## Borderline calls

- **Weiguo Hu (PERSON-001055) — the weakest link in the packet.** He is listed
  on the PSE Faculty Listing page, but under "Research Professors and
  Lecturers" as NMR Director. The brief makes the department's faculty
  directory the program tie, so the verdict is LINK; flagged because he is
  research staff rather than tenure-line faculty (Atlas Gate A treats staff
  titles cautiously for admissions — this is a link on an existing record, and
  the tie is to the department whose NMR facility he directs).
- **Substring caution (checked, not a defect):** the MSE roster's "Shubha
  Tewari" (Physics) is not Gregory N. Tew (PERSON-000229); Tew's link is
  PSE-only. Similarly "Guangyu Xu" (ECE) on the MSE roster is not Yanfei Xu.

## Unfilled gaps (no honest fill found — not treated as absence)

- **PROG-000059 specialty_processes / specialty_materials:** PSE publishes its
  scope as six research themes, not as a process or materials taxonomy. The
  specifics that exist (roll-to-roll patterning, nanocellulose, imprint
  patterning) appear on individual research-group pages — group grain, not
  program grain — so both fields were left blank rather than inferred,
  consistent with the Ohio pass's generic-phrase holds.
- **PROG-000100 specialty_processes / specialty_materials:** the MSE program
  page publishes a field list (used for research_areas) but no process or
  material-class phrase at program grain. Left blank.
- **PROG-000100 scale_band:** no enrollment figure, band, or size
  self-characterization appears on the MSE program page or the IDGP site
  pages checked (program page, IDGP home, IDGP faculty). Left blank.
- **PROG-000100 facilities_note** is a structural note, not a facility
  listing: the program is interdepartmental and publishes no dedicated
  facility; the note says so, on the program page's own description, so the
  blank is explained rather than silent.

## Suspected record defects / currency flags

- **Horst Henning Winter (PERSON-000232) — possible stale record.** Recorded
  as Distinguished Professor of Chemical Engineering with an adjunct PSE
  appointment, but he appears on neither current listing: the PSE Faculty
  Listing's Adjunct Professors section names only Sarah Perry, and the MSE
  IDGP roster does not include him. NO_WITNESS for both programs. A listing
  change is a flag, not proof of retirement or departure.
- **John Klier (PERSON-000236) — no program tie published.** A Chemical
  Engineering professor whose recorded specialties are squarely polymer
  colloids/emulsion polymers, yet he is on neither the PSE Faculty Listing
  nor the MSE IDGP roster. NO_WITNESS; the record itself is not contradicted
  (home-department employment stands), but no program link can be banked.
- No pool person was found to have plainly left UMass Amherst, and no
  recorded specialty was contradicted by a current page.

## Failed fetches

None. Every URL fetched returned 200 (PSE home, directory, faculty listing,
research, shared instrumentation, history, and one research-area page; the
College of Engineering MSE page; the MSE IDGP home and faculty pages).

## Paid calls

None. All sources were fetched directly (curl) from umass.edu /
websites.umass.edu. No Tavily/Exa/Firecrawl use, and no web search was needed —
the pool's own profile URLs and the two program URLs in the worklist led to
every witness page.
