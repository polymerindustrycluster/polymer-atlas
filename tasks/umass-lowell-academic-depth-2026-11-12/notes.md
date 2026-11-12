# UMass Lowell depth pass — lane notes (2026-11-12)

## Witness architecture (what counted as a program tie)

- **PROG-000057 (Plastics Engineering degree):** the department's own Faculty page
  (`uml.edu/engineering/plastics/faculty-staff/`) lists 14 of the 22 pool people with
  "Plastics Engineering" in their title lines. That page is the program tie. Its
  companion Affiliated Faculty page was also checked — no pool person appears there.
- **PROG-000300 (Plastics Engineering Seminars):** two program pages tie people —
  (a) the published Summer 2026 seminar schedule on the program page, whose table
  rows name each seminar's instructor (quotes in links.csv are reading-order
  segments of those rows, trimmed to ≤25 words); (b) the program's Instructors page
  (`instructors.cfm`), where each instructor block closes with a "Teaches:" line
  naming their seminar(s). Eight pool people are seminar instructors — seven of
  them also hold PROG-000057 links, so the seminar program links are second-program
  rows, exactly the dual-witness shape the earlier passes produced.
- **PROG-000058 (Graduate Certificate in Plastics Processing):** no person-level
  ties published anywhere checked (certificate page, curriculum, catalog) — zero
  LINKs, as the brief predicted. No pool person was forced into it.

## Borderline calls

- **Jinde Zhang (PERSON-000261) → PROG-000057 is the weakest link in the packet.**
  He appears in the department Faculty page's main Faculty list, but his own title
  line there reads "Assistant Research Professor, Nanomanufacturing Center" (his
  profile link on that page points to the Nano center's staff pages, not a Plastics
  profile). Counted LINK because the brief names the department's faculty pages as
  the program tie and he is in the core Faculty list (not the Affiliated list) —
  flagged so the integrator can hold it if the standard tightens. His PROG-000300
  link is independent and unambiguous (named instructor, Thermoplastic Elastomers).
- **Davide Masato (PERSON-000260) → PROG-000300** rests on the program's
  Instructors page only: his block (Padova Ph.D., micro/nano molding) closes with
  "Teaches: Precision and Micro Injection Molding." That seminar does not appear
  in the Summer 2026 schedule block on the program page — the instructors roster
  is the standing program page, so the tie stands, flagged here.
- **Instructor-block attribution on instructors.cfm:** the "Teaches:" line closes
  each instructor's block (verified against the schedule for Johnston — Injection
  Molding / Plastic Part Design — and Mead — Thermoplastic Elastomers). Quotes
  from that page should be read with that layout in mind.
- **PROG-000057 specialty_processes** quotes the department's Advanced Plastics
  Processing (PLAS.5780) course description as published on the GPS certificate
  page: PLAS.5780 is a core graduate course in the degree program (required in
  the M.S./Ph.D. curricula), and the sentence is the department's own summary of
  the common plastics manufacturing processes. The department's process labs
  (injection molding, extrusion, blow molding, compounding, thermoforming,
  recycling) corroborate but are not the cited quote.

## Deliberate non-proposals (gaps left blank, with reason)

- **PROG-000058 research_areas** and **PROG-000300 research_areas:** neither page
  makes a research claim — the certificate publishes learning outcomes and the
  seminar program publishes training topics. Under §4.11's research-programs-only
  discipline for research_areas (the Ohio pass held the same shape), no fill is
  proposed; the seminar program's topic scope is carried by its specialty_* fills.
- **PROG-000058 scale_band** is a size fact (4 courses / 12 credits, 9 months),
  not a band — banked as proposed so the owner's conversion ruling can use it,
  same posture as the Ohio/NC State scale facts.

## Suspected record defects / currency flags

- **Christopher J. Hansen (PERSON-000252):** his recorded public_profile_url
  (`sites.uml.edu/christopher-hansen/research/`) returns **HTTP 410 Gone** — the
  record's profile URL is stale. He is Mechanical & Industrial Engineering faculty
  with no Plastics Engineering tie found; NO_WITNESS stands regardless.
- **Akshay Kokil (PERSON-000259) title mismatch inside UML's own pages:** the
  department Faculty page styles him "Associate Teaching Professor"; the Seminars
  Instructors page styles him "Assistant Teaching Professor in the Plastics
  Engineering Department." Minor internal inconsistency; both links unaffected.
- **Margaret Sobkowicz (PERSON-000247)** is styled "Margaret Sobkowicz Kline" /
  "Dr. Meg Sobkowicz Kline" on current UML pages; the pool's parenthetical
  "(Sobkowicz Kline)" already anticipates this — no defect, noted for matching.
- The eight NO_WITNESS people are all real, current UML faculty in other units
  (Mechanical & Industrial Engineering ×2, Chemistry ×3, Chemical Engineering ×2,
  Physics/Center for Advanced Materials ×1). Their own profile pages were checked:
  Reuther, Ruths, Orbey and Manohar contain no "Plastics" mention at all; Kumar's
  only occurrence is a 2000 Society of Plastics Engineers conference-paper title
  in his publication list — a publication venue, not a program tie. Employment at
  UML was never treated as a link.

## Failed fetches (availability only — never treated as absence)

- `sites.uml.edu/christopher-hansen/research/` (Hansen's recorded profile): HTTP
  410 Gone (see defect flag above).
- All other fetches returned 200, including the four program/worklist URLs, the
  department About / Research / Labs / Programs-of-Study pages, the seminar
  Instructors and Facilities pages, and the remaining pool profiles.

## Paid calls

None. All sources were fetched directly (curl) plus one free web search used to
locate the Ph.D. program page's research-areas list, which was then verified on
the page itself. No Tavily/Exa/Firecrawl use.
