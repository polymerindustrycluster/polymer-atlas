# NC State depth pass — lane notes (2026-11-11)

## Witness architecture (what counted as a program tie)

- **PCC (PROG-000065):** the Wilson College people directory grouped by academic
  program (`textiles.ncsu.edu/group/academics/polymer-and-color-chemistry/`) lists the
  program's faculty; Budhathoki-Uprety's link rests on her own profile instead
  (she teaches PCC 106 and PCC 461 — the program's own courses).
- **FPS (PROG-000118):** the Graduate Catalog's faculty roster for the Fiber and
  Polymer Science (PhD) program, 2025-2026 archive PDF (catalog.ncsu.edu). FPS
  quotes in links.csv are roster segments from that list, space-joined in reading
  order under the rank heading shown.
- **MSE (PROG-000147):** MSE department pages (individual profiles on mse.ncsu.edu;
  research-group lines on the department research page) plus the current
  (2026-2027) catalog's MSE faculty roster, published on the MSE Graduate
  Certificate catalog page — the same graduate-faculty roster the department
  publishes for its graduate programs.
- Both catalog rosters include cross-appointed graduate faculty (CBE, Physics,
  Chemistry, Forest Biomaterials professors on the FPS roster; Physics/CBE/Textiles
  professors on the MSE roster). The same standard was applied to both programs:
  a published program faculty roster is a program tie, a home-department page alone
  is not.

## Borderline calls

- **Harald Ade (PERSON-000265) — MSE link is the weakest in the packet.** The MSE
  department's own people directory styles him "Professor of Physics" (a courtesy
  listing); his MSE row rests on the catalog MSE Professors roster. His FPS link
  (Full Professor, FPS roster) is unambiguous.
- **Melissa Pasquinelli (PERSON-000283) — MSE link rests on the catalog roster
  only.** She does not appear in any of the MSE research page's seven
  research-area faculty lists. Her FPS link (Full Professor, 2025-2026 roster)
  is unambiguous.
- **Catalog-year changes drove two verdicts.** Christopher B. Gorman
  (PERSON-000282) is a Full Professor on the **2024-2025** FPS roster but is
  absent from the **2025-2026** roster → NO_WITNESS. Jialong Shen (PERSON-000306)
  is on the 2024-2025 FPS roster as Practice/Research/Teaching Professor but
  absent from 2025-2026 → NO_WITNESS for FPS (his PCC link stands on the current
  college directory). The current roster governed in both cases.
- **Wendy Krause (PERSON-000304)** moved the other way: Adjunct Faculty on the
  2024-2025 FPS roster, Associate Professor on the 2025-2026 roster — her FPS
  link carries no adjunct caveat. She is also core-listed under PCC.
- **Sonja Salmon (PERSON-000303) rank discrepancy:** Wilson College pages style
  her "Professor"; the 2025-2026 FPS roster lists her under Associate Professors
  (the 2024-2025 PDF's two-column layout is ambiguous at her name). She is on
  the roster both years; the LINK is unaffected — flagged so the integrator is
  not surprised by the rank mismatch against her recorded title.
- **Xiangwu Zhang (PERSON-000299):** his Wilson College profile's academics tags
  name only Textile Engineering / TECS — no FPS tag. His FPS link rests solely on
  the catalog roster (Full Professor), which governed over the profile tags.

## Non-Atlas Wilson programs witnessed (per brief: named, never forced)

The Wilson College directory groups several pool people under programs the Atlas
does **not** carry: Budhathoki-Uprety, Salmon, Krause, Schroeder and Shen all also
carry **Textile Engineering, Chemistry and Science** (the department) group tags;
Krause, Schroeder and Shen also carry **Textile Engineering**; Seyam's profile tags
are **Textile and Apparel, Technology and Management** and the Fashion/Textile
Management programs. None of those tags was used as a witness for PCC/FPS; Seyam's
FPS link rests solely on the catalog roster. The 17 NO_WITNESS people (mostly CBE,
MAE, Physics-adjacent and Forest Biomaterials faculty) had no page tying them to
PCC, FPS or MSE — employment at NC State was never treated as a link.

## Suspected record defects / currency flags

- **Gorman (PERSON-000282):** dropped from the FPS graduate faculty roster between
  the 2024-2025 and 2025-2026 catalogs. Possible emeritus transition or departure;
  his Atlas record may be going stale. Not treated as proof of departure — a
  roster change is the flag, not the fact.
- **Pasquinelli (PERSON-000283):** a College of Natural Resources directory page
  (cnr.ncsu.edu) now carries her profile, and RTNN lists her under both TECS and
  CNR affiliations, while the recorded profile URL is a 2018 Wilson College news
  item. Possible joint appointment or college-home change since the record was
  made; her FPS Full Professor listing is current in the 2025-2026 catalog, so
  the program facts stand — the college-home framing may not.
- **Budhathoki-Uprety (PERSON-000305):** recorded as Assistant Professor; her
  Wilson College profile now styles her Associate Professor. Promotion since the
  record was made (the 2025-2026 FPS roster still lists her as Assistant
  Professor — the catalog lags the college page).
- **Shen (PERSON-000306):** the pool note "graduate catalog lists him under
  Research Faculty" reflects the 2024-2025 catalog. His profile states he began
  as Assistant Professor in August 2025 leading the Sustainable Polymer Research
  Group in TECS; the current college PCC directory lists him as Asst Professor.

## Unfilled gap

- **PROG-000065 scale_band:** no enrollment figure, band, or self-characterizing
  size statement appears on the PCC program page (checked the program page and
  the college Labs and Facilities page). Left blank rather than inferred.

## Source note on one FPS fill

- PROG-000118 `specialty_processes` quotes the **2024-2025** catalog program
  description ("the chemistry of dyeing, finishing, and other wet processes").
  The 2025-2026 PhD page carries degree requirements and the faculty roster but
  not the descriptive prose; the quoted sentence is the program's own catalog
  description of its field, and "Dyeing and finishing" is independently named on
  the current textiles.ncsu.edu program page.

## Failed fetches (availability only — never treated as absence)

- `catalog.ncsu.edu/graduate/textiles/fiber-polymer-science/` (current catalog
  HTML): connection closed on two attempts; the official archived catalog PDFs
  were used instead.
- `mse.ncsu.edu/research/equipment-and-facilities/` and
  `mse.ncsu.edu/equipment-and-facilities/`: 404. The live URL was taken from the
  site navigation: `mse.ncsu.edu/research/equipment-facilities/`.
- `textiles.ncsu.edu/research/faculty-research-areas/`: 404; the college's
  `/group/academics/…` and `/group/research/…` directory pages were used instead.
- Guessed MSE profile slugs for Tracy and Seifrid (`/people/jtracy/`,
  `/people/mseifrid/`): 404; their witnesses are the MSE research page's
  research-group lines.
- First attempt at the 2025-2026 FPS PhD PDF returned an empty reply (curl exit
  52); a retry succeeded. One catalog HTML fetch also closed mid-session and
  succeeded on the PDF route.

## Paid calls

None. All sources were fetched directly (curl) or found via free web search.
No Tavily/Exa/Firecrawl use.
