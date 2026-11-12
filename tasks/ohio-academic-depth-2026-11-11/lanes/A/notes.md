# Lane A notes — Ohio academic depth pass (2026-11-11)

Lane A: 15 programs (worklist.csv), 48 people (people_pool.csv).
Deliverables: fills.csv (37 proposed fills), links.csv (48 verdicts: 36 LINK, 12 NO_WITNESS).
All fetches were direct curl reads of institution pages plus web search leads, 2026-11-11.
**No paid API calls were used** (no Tavily / Exa / Firecrawl). No OIEx-only fills were
proposed — see the OIEx section at the end.

## Fills by field

- research_areas: 12
- specialty_processes: 6
- specialty_materials: 8
- facilities_note: 8
- scale_band: 3

Gap fields left unfilled are listed per program below; in every case the fetched
institution page did not publish the fact (a missing fact on a page is not evidence
the fact does not exist — it is simply unfilled this pass).

## Borderline calls — program fills

- **PROG-000008 (APTS) research_areas** rests on a course title ("Polymer Compounding,
  Formulating, and Testing of Plastics, Rubber, Adhesives, and Coatings"). APTS is a
  training provider with no stated research programme; the course catalogue is the
  closest published statement of subject coverage. Integrator may prefer to leave
  research_areas blank on a training row.
- **PROG-000009 (ARDL) research_areas and specialty_processes** likewise rest on course
  titles from ARDL's training catalogue, for the same reason.
- **PROG-000021 (AGPA) research_areas** carries the academy's outreach mission
  (K-12 polymer education). AGPA does no research; the other four gap fields were
  left unfilled rather than stretched. Integrator may prefer all five blank.
- **PROG-000116 (Elastomer certificate) specialty_materials** quotes the PLYS 720
  Elastomers course description in the same Akron bulletin programme page; the page
  does not publish a certificate-specific curriculum. facilities_note and scale_band
  were left blank: school-level facts are carried on PROG-000115 and duplicating
  them would double-count.
- **PROG-000031 (STEER America ADC) seam flag:** the fetched page
  (steerworld.com/en/application-development-center) is STEER's global ADC page,
  headquartered in Bengaluru, describing the ADC network including STEER America —
  it is not an Ohio-site-specific page. Both fills describe the network's activity,
  not verified US-site facts; tier accordingly or hold.
- **PROG-000015** record combines the Organic Synthesis Facility AND the Machine
  Shop, but the cited page describes the synthesis facility only. No fill asserts
  anything about the machine shop.
- **PROG-000032 (AMLCI) facilities_note left unfilled.** The institute's facilities
  are themselves separate program rows (PROG-000014, PROG-000015), and the
  facilities-overview fetch did not return the facilities page (see failed fetches).
  No scale_band is published on the fetched pages.
- **PROG-000007 (AFMC)** specialty_processes, specialty_materials and facilities_note
  left unfilled: the page's five clusters are research themes, not processes or
  materials, and the member space it mentions belongs to NPIC, not AFMC.
- **PROG-000022 (NPIC)** scale_band left unfilled: no size figure is published on the
  fetched NPIC home / pilot-processing pages. (An OIEx equipment listing corroborates
  NPIC equipment presence but publishes no size fact usable here.)
- **scale_band left unfilled** for PROG-000008, 000009, 000010, 000014, 000015,
  000030, 000031, 000032, 000033: no size fact published on the fetched pages.
  Course durations (ARDL) and cohort length (Synthe6, 12 months) are not scale.

## Borderline calls — people links

- **PERSON-000047 Henry Astley (LINK, flagged):** the SPSPE Our People directory
  lists him, but his block's Dept/Program reads **Biology**; the link rests on his
  directory title, "Associate Professor of Biology and Polymer Science". Weakest of
  the directory-basis Akron links after Wesdemiotis.
- **PERSON-000044 Chrys Wesdemiotis (LINK, flagged — weakest Akron link):** he is a
  Chemistry professor; the only person-level witness found is the SPSPE
  Sustainability research-area page naming his work. No SPSPE directory block.
- **PERSON-000053 Nita Sahai (LINK):** witnessed by the SPSPE Biomaterials
  research-area page (on the dev.uakron.edu mirror), which lists her name against
  her research topics in the page's faculty-focus list.
- **PERSON-000059 Toshikazu Miyoshi and PERSON-000075 Thein Kyu (LINK):** witnessed
  by the SPSPE Polymer Physics faculty roster; the quotes are contiguous roster
  segments under the page's "POLYMER PHYSICS FACULTY" heading, since the roster
  carries no per-person unit line. Kyu's own profile page fetch returned the SPSPE
  site shell without his profile block (availability/extraction only) — the roster
  is the witness of record.
- **PERSON-000078 Christopher W. Barney (LINK):** dual-listed — his pool profile URL
  is the College of Engineering directory, but the SPSPE Our People directory also
  carries him with Dept/Program = School of Polymer Science and Polymer
  Engineering; the SPSPE directory is the witness used.
- **PERSON-000045 Chunming Liu (LINK):** directory Dept/Program line names SPSPE
  jointly with Chemistry ("School of Polymer Science and Polymer Engineering &
  Department of Chemistry"); the link is to SPSPE as one of the two named units.
- **PERSON-000087 Samuel Sprunt (LINK, thin quote):** the AMLCI People page lists
  him as Professor in the institute's faculty block; the quote is the listing line
  itself (office given as the Science Research Building, AMLCI's building).
- **PERSON-000086 Marianne Prévôt, PERSON-000089 Elizabeth Mann, PERSON-000090
  Hao Shen, PERSON-000091 Robert J. Twieg (LINK):** witnessed by their profile
  pages hosted on the AMLCI site; the quotes are the pages' title lines naming the
  institute. For Shen this matters: his pool profile URL (kent.edu/node/420081)
  contains zero AMLCI mentions — the link rests on the separate AMLCI-hosted
  profile at kent.edu/amlci/hao-shen.
- **PERSON-000019 Antal Jakli / PERSON-000023 Oleg Lavrentovich (LINK):** one
  shared witness line from the AMLCI People page's internal advisory board listing,
  which tags each name "(Physics, AMLCI)" / "(Chemistry, AMLCI)".
- **PERSON-000024 Peter Palffy-Muhoray (LINK):** the witness styles him associate
  director of the "Glenn H. Brown Liquid Crystal Institute" — AMLCI's name before
  its September 2018 renaming (the institute's own about page carries the rename).
- Akron directory-pattern quotes: for the SPSPE Our People directory links, the
  quote is the person's consecutive directory block (Name / Title / Dept/Program)
  joined with spaces, exactly as the page lays it out.

## NO_WITNESS — what was checked

- PERSON-000056 Shing-Chung Josh Wong (Akron): Mechanical Engineering professor;
  the fetched item is an SPE Fellow news story naming him as an ME professor. No
  SPSPE tie.
- PERSON-000076 Jae-Won Choi (Akron): profile Dept/Program is Mechanical
  Engineering / Biomedical Engineering.
- PERSON-000077 Michelle S. Hoo Fatt (Akron): profile Dept/Program is Mechanical
  Engineering.
- PERSON-000079 Qixin Zhou (Akron): profile Dept/Program is Chemical, Biomolecular,
  and Corrosion Engineering.
- PERSON-001330 David A. Modarelli (Akron): Chemistry professor directing the
  Center for Laser & Optical Spectroscopy; no SPSPE tie on his page.
- PERSON-000068 Amy Heston (Walsh): directory page styles her Professor of
  Chemistry with no mention of the Center for Scientific Excellence. A co-authored
  paper with CSE's Michael Dunphy is not a unit tie.
- PERSON-000070 Clovis Linkous, PERSON-000071 Holly J. Martin (YSU): the pool
  offers only YSU catalogue PDFs; no person-level witness tying either to the
  Youngstown Advanced Manufacturing Innovation Center was located within the
  effort cap.
- PERSON-000072 Peter Norris (YSU): his research page is Chemistry-only.
- PERSON-000073 Sina Bakhtar Chavari (YSU): YSU people page (joined Electrical
  Engineering, August 2025) states additive-manufacturing research but no center
  tie.
- PERSON-002014 Byung-Wook Park (YSU): YSU page ties him to Chemical Engineering /
  MSE graduate faculty, not the center.
- PERSON-002104 Michael R. Fisch (Kent State): engineering profile with zero
  AMLCI mentions.

## Failed / degraded fetches (availability signals only — never treated as absence)

- Kent State `kent.edu/amlci/facilities` and `kent.edu/amlci/affiliated-faculty`
  both returned the identical generic Kent page (redirect / soft-404 in the text
  fetch); their contents were not obtained. This is why PROG-000032's
  facilities_note is unfilled rather than asserted.
- Thein Kyu's SPSPE profile page returned the site shell without a profile block.
- The NPIC worklist URL (`uakron.edu/npic/request`) is a form stub; NPIC fills rest
  on the NPIC home and pilot-processing pages instead.
- Kent State pages were slow throughout (15–45 s per fetch); all eventually loaded
  except the two generic-page redirects above.

## Record defects spotted

1. **PROG-000033 (YSU Youngstown Advanced Manufacturing Innovation Center) —
   possible staleness.** The worklist page text carries 2014–2015-era funding and
   capability language, while a YSU news story found by web search (crawled 2026)
   says the center "officially launched less than a year ago" under director
   Bharat Yelamanchi. The Atlas row may describe the center's earlier incarnation.
   The specialty_materials fill is quoted from the current centre page as fetched,
   but the row's description/dates deserve an integrator look.
2. **PERSON-002014 (Byung-Wook Park) — source-page title inconsistency.** The
   pool's role_as_published ("Associate Professor") matches his YSU page's title
   line, but the same page's bio text calls him "Assistant Professor". The Atlas
   record follows the title line; the bio appears stale. Flagged, not changed
   (lanes do not edit data/).

## Ohio Innovation Exchange (OIEx) — yield, honestly graded: LOW / lead-only

OIEx was used through web search only. Yield:

- It surfaced one corroborating equipment listing — a Bruker Dimension Icon AFM at
  the National Polymer Innovation Center (240 South Forge St, Akron) on
  people.ohioinnovationexchange.org — which corroborates NPIC's equipment
  presence but supported **no fill** (no scale_band or facilities fact was taken
  from it).
- **Zero of the 37 fills rest on OIEx; zero fills carry source_kind=oiex.**
  Every proposed fill rests on an institution page. OIEx functioned here purely
  as a discovery/corroboration lead, and a weak one for this lane's institutions:
  its expert/facility coverage did not surface a single fact the institution
  pages did not state better.
