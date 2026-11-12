# Michigan State academic depth pass — lane notes (2026-11-12)

## Witness architecture (what counted as a program tie)

- **School of Packaging (PROG-000066):** the school's own Team directory
  (`msu-prod.dotcmscloud.com/packaging/our-team/`, the School of Packaging site) lists each
  pool packaging person with a faculty title: Auras, Rabnawaz, Muzata, Matuana, Almenar,
  Yang. All six LINK.
- **C3PS (PROG-000073):** the center's own researchers page (c3ps.org/researchers) lists
  eight pool members as "Lead Site — Michigan State University" researchers: Muzata,
  Rabnawaz, Narayan, Auras, Cheng, Yang, Ferrier, Szczepanski. All eight LINK. The center's
  data also styles Rabnawaz "Center Director"; his School of Packaging profile page
  (msu-prod.dotcms.cloud/people/rabnawaz) independently calls him "Fouding Director"
  [sic — the site's spelling] of the NSF IUCRC for Plastic, Paper, and Hybrid Packaging
  End-of-Life Solutions (C3PS).
- **MSE (PROG-000103):** see the borderline call below — no per-program faculty roster
  exists at MSU; the ChEMS directory and individual College of Engineering profiles are
  department-grain only and were NOT used as MSE witnesses.

## Borderline calls

- **MSE polymer cluster (6 LINKs, flagged for integrator review).** MSU's MSE program is
  administered inside the combined ChEMS department, which publishes no MSE-only faculty
  roster. The one program-grain enumeration found is the MSE graduate program's own
  "Top 12 Reasons to Pursue Your Materials Science & Engineering Graduate Degree at MSU"
  list, hosted on the program's pages at egr.msu.edu (nicholasgroup/positions.php), which
  names the program's polymer-research faculty: "With 8 faculty performing polymer research
  (Shiwang Cheng, John Dorgan, Larry Drzal, Robert Ferrier, K Jayaraman, Andre Lee,
  Richard Lunt, and Ramani Narayan)". I linked the six named pool members who are ALSO
  corroborated as current ChEMS faculty by the current ChEMS Directory
  (engineering.msu.edu/departments/chems/directory): Cheng, Drzal, Ferrier, Jayaraman,
  Andre Lee, Narayan. Caveats the integrator should weigh: (1) the page is a research
  group's recruiting page reproducing the program's list, and it is undated; (2) the
  polymer sentence attributes the cluster to "the CHEMS department" while the sibling
  metals sentence attributes its cluster to "the MSE program" — the grain is mixed, though
  the list's whole context is MSE-program recruitment (applicants are directed to the MSE
  PhD program). If the integrator judges this department-grain after all, these six rows
  should flip to NO_WITNESS; every other verdict in the packet is unaffected.
- **Dorgan (PERSON-000381) — NO_WITNESS despite being named in that cluster.** He is the
  one named person NOT corroborated by the current ChEMS Directory (see suspected defects).
  His MSE verdict turns on the same call above; either way he has no second, current
  program source.
- **Cheng's directory role is ChE-side** ("ChE Graduate Program Advisor, Associate
  Professor" in the ChEMS Directory). His PROG-000103 link rests only on the program
  page's polymer cluster; his PROG-000073 link is independent (C3PS researchers page).
- **MSE specialty_processes fill is curriculum-derived.** The B.S. program page's own
  curriculum names the core course "MSE 370: Synthesis and Processing of Materials";
  the proposed phrase is that verbatim course title, not a research-process claim.
- **MSE facilities_note left blank.** No MSE-program-grain facilities description was
  found on MSU pages within the fetch budget: the B.S. page is curriculum/ABET prose,
  and the ChEMS research page is a department portfolio overview without named
  facilities. The gap stays a gap rather than borrowing C3PS's hub description
  (Engineering-Department grain, center context).
- **SoP specialty_processes** rests on a single named process space (the Plastipak
  Processing Lab's "advanced plastic processing techniques", MSU Innovation Center).
  The school's broader process vocabulary (extrusion, converting, testing) appears on
  non-institution pages and was not used.

## Suspected record defects / currency flags

- **Dorgan (PERSON-000381) — currency discrepancy, NOT a departure finding.** The current
  ChEMS Directory omits him entirely, and it styles Richard Lunt as holder of the
  David L. and Denise M. Lamp Endowed Chair, while the pool records Dorgan as the Lamp
  Chair and older MSU pages call him its first/current holder. Against that, MSU
  Engineering news (page updated 2026-03-21) still styles him "professor in the
  Department of Chemical Engineering and Materials Science", and course records show him
  teaching CHE 822 in Spring 2026. Mixed signals — possible directory omission, chair
  transition, or status change; the integrator may want a direct check before any edit.
- **Drzal (PERSON-000387) — title discrepancy.** Pool: "University Distinguished Professor
  of Chemical Engineering and Materials Science". The current ChEMS Directory styles him
  "Adjunct Professor" in the same department. His program links are unaffected, but the
  recorded role looks stale.
- **Rabnawaz (PERSON-000378) — title discrepancy.** Pool: "Associate Professor, School of
  Packaging". The school's current Team directory and his profile page both style him
  "Full Professor" (profile: "Full Professor in the School of Packaging"). Promotion
  since the record was made.
- **Matuana (PERSON-000391) — title discrepancy.** Pool: "Professor and Associate
  Director, School of Packaging". The current Team directory lists him as Professor only,
  and lists Auras as the school's Associate Director.
- Promislow (PERSON-000385, Mathematics), Hickner (PERSON-000384), Ilsoon Lee
  (PERSON-000390), Xinyue Liu (PERSON-000394) and Yilin Zhang (PERSON-000395) returned
  NO_WITNESS: no page ties any of them to the School of Packaging, C3PS, or an MSE
  program listing. Hickner is a near-miss worth noting — a senior polymer-membrane
  researcher in ChEMS who appears in neither the C3PS researcher list nor the MSE
  program page's polymer cluster; department employment alone was not treated as a link.

## Failed fetches (availability only — never treated as absence)

- `canr.msu.edu/packaging/` and `c3ps.org/` return JavaScript shells to plain curl
  (near-empty text). Content was recovered from the sites' own rendered pages via the
  browser text fetch, and for C3PS additionally from the site's own published data
  bundle; the researchers and research pages were then read in rendered form.
- `egr.msu.edu/chems/` is an intranet login page, not the public department site; the
  public ChEMS pages live under engineering.msu.edu/departments/chems/.
- `egr.msu.edu/people/profile/chengsh9` (the pool's recorded profile URL for Cheng)
  redirects to the general College of Engineering faculty directory; his current
  profile is at engineering.msu.edu/directory/faculty/chengsh9. The integrator may
  want to repoint the recorded URL.
- One pattern-derived URL (engineering.msu.edu/departments/chems/research) WAS the
  department's live research page and was used only as context (department-grain
  portfolio prose; nothing in the packet cites it).

## Paid calls

None. All sources were fetched directly (curl / browser text fetch) or found via free
web search. No Tavily/Exa/Firecrawl use.
