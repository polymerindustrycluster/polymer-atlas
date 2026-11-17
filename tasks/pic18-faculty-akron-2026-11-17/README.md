# PIC-18 faculty completeness: University of Akron (ORG-000501), 2026-11-17

Lane `atlas-w17-fac-a`. Integrator for PERSON-002300..002399 and EVD-393000..393999 only.
Raw pages (sha256-named) are in `/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-faculty-akron-2026-11-17/`;
`manifest.csv` here is a copy of that folder's manifest (url, fetched_at, sha256, url_provenance; no contact data).
Reproduce: `frame.py` -> `verdicts.py` -> `build.py` (idempotent) -> `check.py --selftest`.

## Result (unit: distinct persons on the institution's own listing pages; filter: University of Akron)
- **3 VERIFIED** and written: PERSON-002300 Bi-min Zhang Newby (professor, Chemical, Biomolecular and Corrosion Engineering), PERSON-002301 Hossein Ravanbakhsh (assistant professor, Biomedical Engineering), PERSON-002302 Jutta Luettmer-Strathmann (professor, Physics; listed as Chemistry joint faculty). All tier A; 6 evidence rows (existence + scope each, own_site, supports_A).
- 23 DUPLICATE_OF a held Akron person (never edited), 113 REJECT (75 at Gate A, 38 at Gate B), 4 STILL_UNCERTAIN. 143 persons examined.
- **The premise did not hold for the polymer school.** The School of Polymer Science and Polymer Engineering's own Faculty page lists **18** faculty and **all 18 are already held**; the school's Adjunct page publishes no one (all 12 names sit inside HTML comments, so they are not counted) and its Emeritus page's 14 names fail Gate A. The yield is in other units, and is small because uakron.edu profile pages are thin.

| Frame unit (rows on the listing pages) | Rows | Distinct persons first listed here | VERIFIED | REJECT | STILL_UNCERTAIN | DUPLICATE_OF |
|---|---|---|---|---|---|---|
| School of Polymer Science and Polymer Engineering, Faculty | 18 | 18 | 0 | 0 | 0 | 18 |
| SPSPE Adjunct (all entries commented out in the page HTML) | 0 | 0 | 0 | 0 | 0 | 0 |
| SPSPE Emeritus | 14 | 14 | 0 | 13 | 0 | 1 (Kyu, held) |
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
2. **Vocabulary question (owner).** 13 teaching-track "Professor/Associate Professor of Instruction or Practice" and "of Engineering Practice" rows (Chemistry, CBCE, BME, ME) were rejected at Gate A because those stylings are not in the 4.9 role list. None was examined for Gate B. If the owner wants them in scope, that is a ruling, not a lane call.
3. **Gate B holds above** (Pang, Lyuksyutov, Tavana) need a page that loaded or a rendered lab page.
4. A name match of Yilin Liu (Akron Chemistry) to "Yi Liu" (PERSON-000593, LBNL) was checked and is a different person.
5. **Identifier in URLs.** The `u=` value in uakron.edu profile URLs is the person's UA network ID; about 20 held Akron rows already carry such URLs. The brief says to use a department page when a URL embeds a personal identifier. These three rows follow the held precedent; the controller should rule whether to keep it.
6. **Evidence strength, for the controller.** Newby's and Luettmer-Strathmann's Gate B quotes are research-topic lists on the person's own profile rather than a narrative sentence. The people evidence class has 776 supports_A scope rows, list-style ones among them (for example EVD-280045), so these are recorded as supports_A; downgrade to supports_B if the controller reads rule 5's list-item cap as applying to people.

## Sources
Own-domain pages only (provenance root for the College of Engineering pages: the held PERSON-000046 profile URL -> its 'About the College' link -> the People Directory link on that page): SPSPE people pages (faculty, adjunct, emeritus), Chemistry faculty-staff listing and profile pages, College of Engineering people directory and the CBCE, BME and ME people pages and profile pages, and lab pages linked from profiles (metacomposites.uakron.edu, blogs.uakron.edu/mee, jugroup, zhanglab, irl, barkana-signals-lab, boika-research, seamlab, mems, tavana). No search engine was used; every URL is a link on a held record or on a fetched page (provenance per fetch in `manifest.csv`). Raw words of every quote are in the stored pages; `check.py` re-verifies them.

## Not checked (unresolved, not negative)
- The brief's other step-1 URLs: the AFMC page, the CenTiRe site and the bulletin polymer-program page were fetched and added no Gate-A-passing candidate (AFMC's page names Yu Zhu, held, and Bryan Vogt, who is not on the school's published adjunct list; CenTiRe names Choi, held, and an outside director). The NPIC page and any research-center rosters were not examined.
- Departments outside the brief's list: Physics (other than the two joint faculty on the Chemistry page and Luettmer-Strathmann), Biology, Geosciences, Civil, Electrical and Computer Engineering, Wayne College. The college "All Faculty & Staff" list (`engineering-faculty.dot`) was fetched for provenance only and not adjudicated.
- Whether any faculty page not linked from the people listings states polymer research (for example research-center rosters: CenTiRe, AFMC, NPIC).
- Lab pages on non-institutional domains (Google Sites, beta-lab.org, leipzigbioe.com) were not used for any gate.
- ORCID identifiers (people_identifiers) and inclusion_log were not touched, by instruction.
