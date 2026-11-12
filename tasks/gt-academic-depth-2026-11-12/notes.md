# Georgia Tech depth pass — lane notes (2026-11-12)

## Witness architecture (what counted as a program tie)

- **PROG-000099 (MSE degree):** the MSE Faculty Research Overview gallery
  (`mse.gatech.edu/faculty-research-overview`), the MSE people directory
  (`mse.gatech.edu/people`), and individual MSE profile pages styling the person as
  MSE faculty.
- **PROG-000143 (MSE — Polymer and Fiber Materials):** only polymer/fiber-context
  witnesses — the structured "Research Areas" tag list on the person's own MSE
  profile page where it includes Polymers/Fibers/Textiles, or a profile research
  sentence naming polymer work. A general MSE roster alone never produced a 143 row.
- **PROG-000050 (CHMI):** the center's own site on a Georgia Tech domain
  (chmi.isye.gatech.edu). One pool person is named there: Donggang Yao, CHMI Site
  Director for Georgia Tech — his strongest program tie in this packet.
- **PROG-000304 (Composites Certificate):** the certificate page names no faculty
  (only undergraduate advising staff) → zero person links, as the brief predicted;
  absence was not forced.

## Dual MSE links — which witness is stronger

19 people carry both a 099 and a 143 row. In nearly every case the **143 witness is
the more specific one** (the profile's own research-area grouping or research
sentence naming polymers/fibers), while the 099 row rests on the MSE title/roster.
Notable gradations:

- **Reynolds (PERSON-000187):** one sentence carries both rows — it styles him
  Professor of Chemistry and Biochemistry *and* MSE "with expertise in polymer
  chemistry". The 143 tie is the stronger read of that sentence; his directory
  title is Chemistry-first.
- **Ratcliff (PERSON-000199):** the reverse — her 099 row (FRO Professor listing)
  is strong, her 143 row is the **weakest LINK in the packet**: it rests on the
  topic tag list on her own MSE profile ("LISPEM Polymer Electrochemistry …").
  Her profile's research-focus sentence names interfaces and printable electronic
  materials, not polymers. Kept as LINK because the tag is her profile's own
  research taxonomy; flagged for the integrator.
- **Qi (PERSON-000189) and Gutekunst (PERSON-000192):** their 143 rows (polymer
  research text on their MSE-hosted profiles) are stronger than their 099 rows,
  which rest on the directory's Courtesy Appointments view.
- **Yao (PERSON-000205):** three rows — CHMI Site Director (050, strongest),
  FRO Professor (099), and his profile's research keywords "fiber spinning,
  polymer processing" (143).

## Borderline calls

- **Stingelin (PERSON-000203) — NO_WITNESS for 143, the closest call in the
  packet.** She is Professor & Chair of MSE (099 LINK is unambiguous). Her MSE
  profile's research-interests sentence names "organic functional materials,
  including organic electronics" and hybrid systems — not the polymer area; the
  word polymer appears on her profile only in teaching-interests text. Under the
  brief's standard (research-area grouping or a profile naming the polymer area
  in research context) that did not clear the bar. Settling fact: an MSE page
  grouping her under the polymer/fiber research area.
- **Temenoff (PERSON-000207) — 099 only.** She appears in the MSE directory's
  Courtesy Appointments view (099 LINK, courtesy-grade, same standard as Qi and
  Gutekunst), but unlike them she has no MSE-hosted profile naming a research
  area — her MSE profile is a stub (BME contact block only), so no 143 row.
- **Srinivasarao (PERSON-000204) and Russo (PERSON-001437)** returned LINK rows on
  current Professor styling (see currency flags below).
- **PROG-000099 specialty_processes** is the school's own framing phrase
  ("process-structure-property-performance paradigm"), not a process list — the
  research overview gives no school-wide process enumeration. Returned as the
  institution's verbatim phrase; the integrator may hold it, as with the general
  materials list (the same classes quote serves research_areas and
  specialty_materials for 099, as the page states them in one sentence).
- **PROG-000143 scale_band** is a published self-characterization ("one of the
  largest polymer research portfolios amongst MSE programs in the US"), not a
  headcount; **PROG-000099 scale_band** is returned as two raw size facts
  (262 undergraduates; 228 graduate students). The same Facts & Figures page
  also states a faculty headcount of 44 (36 FTE) — noted here, not proposed.
- **PROG-000304 scale_band:** no size fact, band, or self-characterization appears
  on the certificate page — left blank rather than inferred.
- The PROG-000143 catalog page itself carries almost no descriptive prose (a
  course list and one footnote recommending polymer/fiber courses); its
  specialty/facilities fills therefore rest on the MSE research overview's
  polymer and fiber passages, which describe the school's polymer/fiber program
  in its own words.

## Suspected record defects / currency flags (records not edited by this lane)

- **Gutekunst (PERSON-000192):** the MSE directory styles him "Assistant
  Professor"; he is an Associate Professor in Chemistry & Biochemistry (the
  pool's styling). MSE directory rank appears stale.
- **Temenoff (PERSON-000207):** MSE directory/profile style her "Associate
  Professor"; BME styles her Carol Ann and David D. Flanagan Professor. Her MSE
  profile's Research Keywords ("carbon nanotubes, cold cathodes, Photovoltaics,
  supercapacitors") describe an electronics research profile, not her polymeric
  biomaterials work — a Georgia Tech-side data error worth the integrator's note.
- **Russo (PERSON-001437):** his MSE directory entry sits in the directory run
  alongside emeritus/retired listings while styling him "Professor, Hightower
  Chair in Biopolymers", and his profile and lab site (psrlab.gatech.edu) present
  as active. The placement/styling conflict is flagged, not resolved — status
  confirmation is the integrator's call. His links follow the active styling.
- **Karl Jacob (PERSON-000206):** verified still listed as an MSE FTE Professor
  with a current MSE profile (polymer/fiber research areas) — the record stands.
  Currency note only: the recorded profile URL points to bioengineering.gatech.edu
  while MSE carries his directory profile.
- **PROG-000050 record URL:** the worklist URL points to fcmf.utk.edu (a
  University of Tennessee–hosted page) although the center's own site lives on a
  Georgia Tech domain (chmi.isye.gatech.edu, linked to iucrc-chmi.org) and
  Georgia Tech is the lead site. A repoint candidate for the integrator; all
  CHMI fills and the Yao link cite the center's own GT pages.
- No pool person was found to have plainly left Georgia Tech.

## Failed fetches (availability only — never treated as absence)

- `mse.gatech.edu/facts-figures` (first guess from the nav label) returned the
  site's "Page Not Found" page; the live path is
  `mse.gatech.edu/about/factsandfigures`, which was fetched and used.
- The recorded CHMI URL (fcmf.utk.edu) was not fetched: the center's own
  Georgia Tech site superseded it as citation of record (see flag above).

## Paid calls

None. All sources were fetched directly (curl) or found via free web search.
No Tavily/Exa/Firecrawl use.
