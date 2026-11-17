# PIC-18 faculty completeness: University of Akron (ORG-000501), 2026-11-17

Lane `atlas-w17-fac-a`. Integrator for PERSON-002300..002399 and EVD-393000..393999 only.
Raw pages (sha256-named) are in `/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-faculty-akron-2026-11-17/`;
`manifest.csv` here is a copy of that folder's manifest (url, fetched_at, sha256, url_provenance; no contact data).
Reproduce: `frame.py` -> `verdicts.py` -> `build.py` (idempotent) -> `check.py --selftest`.

## Result (unit: distinct persons on the institution's own listing pages; filter: University of Akron)
- **3 VERIFIED** and written: PERSON-002300 Bi-min Zhang Newby (professor, Chemical, Biomolecular and Corrosion Engineering), PERSON-002301 Hossein Ravanbakhsh (assistant professor, Biomedical Engineering), PERSON-002302 Jutta Luettmer-Strathmann (professor, Physics; listed as Chemistry joint faculty). All tier A; 6 evidence rows (existence + scope each, own_site, supports_A).
- 22 DUPLICATE_OF a held Akron person (never edited), 127 REJECT (89 at Gate A, 38 at Gate B), 4 STILL_UNCERTAIN. 156 persons examined.
- **The premise did not hold for the polymer school.** The School of Polymer Science and Polymer Engineering's own Faculty page lists **18** faculty and **all 18 are already held**; the school's 12 adjunct (other institutions or industry) and 16 emeritus pages fail Gate A. The yield is in other units, and is small because uakron.edu profile pages are thin.

| Frame unit (rows on the listing pages) | Rows | Distinct persons first listed here | VERIFIED | REJECT | STILL_UNCERTAIN | DUPLICATE_OF |
|---|---|---|---|---|---|---|
| School of Polymer Science and Polymer Engineering, Faculty | 18 | 18 | 0 | 0 | 0 | 18 |
| SPSPE Adjunct | 12 | 12 | 0 | 12 | 0 | 0 |
| SPSPE Emeritus | 16 | 15 (Isayev is on both) | 0 | 15 | 0 | 0 |
| Chemistry (full-time, joint, staff) | 22 | 19 | 1 | 14 | 3 | 1 |
| Chemical, Biomolecular and Corrosion Engineering | 17 | 15 | 1 | 13 | 0 | 1 |
| Biomedical Engineering | 21 | 20 | 1 | 17 | 1 | 1 |
| Mechanical Engineering | 63 | 57 | 0 | 56 | 0 | 1 |

Rows added by tier: people.csv 3 at tier A; evidence_people.csv 6 rows. Per institution: ORG-000501 only. Persons listed in two units are counted once, under the first.
Gate B was adjudicated for the 45 candidates whose listing title passed Gate A and who were not already held; each profile page was fetched once, plus a lab page where the profile linked one on an institutional domain.

## Held (not written)
| Person | Verdict | Settling fact / recommendation | Applied or held |
|---|---|---|---|
| Yi Pang (Chemistry, Coleman Professor) | STILL_UNCERTAIN | Research text is dyes and ESIPT sensors; polymer only in publication headings. Lab page gozips.uakron.edu/~yp5 did not load (HTTP 000). Settles: his lab page or profile stating polymer research. | held |
| Sergei Lyuksyutov (Physics, joint Chemistry) | STILL_UNCERTAIN | Page is biography plus publications (polymer nanolithography titles), no research statement; lab page nebula.physics.uakron.edu/dept/faculty/sfl.htm did not load (HTTP 000). | held |
| Robert Mallik (Physics, joint Chemistry) | STILL_UNCERTAIN | Research is semiconductor thin-film surface science; polymers and SBR are substrates for a patterning technique. Gate B scope call for the owner; recommend REJECT (McComb precedent). | held |
| Hossein Tavana (BME chair) | STILL_UNCERTAIN | Profile research is cancer, microtechnology, tissue engineering; lab page tavana.uakron.edu returned only a script shell. Settles: the rendered lab page naming polymer research. | held |

## Proposed follow-ups (for the controller; no data touched)
1. **Currency of held rows.** Thein Kyu (PERSON-000075, held as professor) is styled "Distinguished Professor Emeritus" on the SPSPE Emeritus page. Toshikazu Miyoshi (PERSON-000059) and Xiong Gong (PERSON-000060) are not on the SPSPE Faculty page; Shing-Chung Josh Wong (PERSON-000056) is not on the Mechanical Engineering listing. 4.9 says a changed or vanished profile downgrades to U. Not edited here.
2. **Vocabulary question (owner).** 16 teaching-track "Professor/Associate Professor of Instruction or Practice" and "of Engineering Practice" rows (Chemistry, CBCE, BME, ME) were rejected at Gate A because those stylings are not in the 4.9 role list. None was examined for Gate B. If the owner wants them in scope, that is a ruling, not a lane call.
3. **Gate B holds above** (Pang, Lyuksyutov, Tavana) need a page that loaded or a rendered lab page.
4. The SPSPE adjunct page names persons held at other institutions (Becker, Dobrynin, Karim, Pugh, Varshney, Simmons, Vogt; Atlas keeps them at their home institutions). A name match to "Yi Liu" (PERSON-000593, LBNL) for Yilin Liu was checked and is a different person.

## Sources
Own-domain pages only: SPSPE people pages (faculty, adjunct, emeritus), Chemistry faculty-staff listing and profile pages, College of Engineering people directory and the CBCE, BME and ME people pages and profile pages, and lab pages linked from profiles (metacomposites.uakron.edu, blogs.uakron.edu/mee, jugroup, zhanglab, irl, barkana-signals-lab, boika-research, seamlab, mems, tavana). No search engine was used; every URL is a link on a held record or on a fetched page (provenance per fetch in `manifest.csv`). Raw words of every quote are in the stored pages; `check.py` re-verifies them.

## Not checked (unresolved, not negative)
- Departments outside the brief's list: Physics (other than the two joint faculty on the Chemistry page and Luettmer-Strathmann), Biology, Geosciences, Civil, Electrical and Computer Engineering, Wayne College. The college "All Faculty & Staff" list (`engineering-faculty.dot`) was fetched for provenance only and not adjudicated.
- Whether any faculty page not linked from the people listings states polymer research (for example research-center rosters: CenTiRe, AFMC, NPIC).
- Lab pages on non-institutional domains (Google Sites, beta-lab.org, leipzigbioe.com) were not used for any gate.
- ORCID identifiers (people_identifiers) and inclusion_log were not touched, by instruction.
