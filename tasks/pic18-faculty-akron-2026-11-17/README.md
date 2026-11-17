# PIC-18 faculty completeness: University of Akron (ORG-000501), 2026-11-17

Lane `atlas-w17-fac-a`. Integrator for PERSON-002300..002399 and EVD-393000..393999 only.
Raw pages (sha256-named) are in `/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-faculty-akron-2026-11-17/`;
`manifest.csv` here is that folder's manifest (url, fetched_at, sha256, url_provenance) with UA network ids redacted (`u=<id>`).
Reproduce: `frame.py` -> `verdicts.py` -> `build.py` (idempotent) -> `check.py --selftest`.
**Revision 2 (after Codex review of 7095fcd):** profile URLs carrying a UA network id (`?u=`) no longer appear in data or in this packet; the two people whose only witness was such a URL are on hold; the 13 teaching-track rows are holds, not rejects; Heo's Gate B quote now shows his research.

## Result (unit: distinct persons on the institution's own listing pages; filter: University of Akron)
- **1 VERIFIED** and written: PERSON-002302 Jutta Luettmer-Strathmann (professor, Physics; joint with Chemistry), tier A, evidence EVD-393004/393005. Her witness is her own Physics Department faculty page (`nebula.physics.uakron.edu/dept/faculty/jutta/jls.htm`, a link on her Chemistry profile; the http form did not load, the https form of the same host and path did), which carries no personal identifier.
- 23 DUPLICATE_OF a held Akron person (never edited), 100 REJECT (62 Gate A, 38 Gate B), **19 STILL_UNCERTAIN** (13 teaching-track, 2 identifier-URL holds, 4 Gate B holds). 143 persons examined.
- **The premise did not hold for the polymer school.** The School of Polymer Science and Polymer Engineering's own Faculty page lists **18** faculty and **all 18 are already held**; its Adjunct page publishes no one (all 12 names sit inside HTML comments, so they are not counted) and its Emeritus page's 14 names fail Gate A.

| Frame unit (rows on the listing pages) | Rows | Distinct persons first listed here | VERIFIED | REJECT | STILL_UNCERTAIN | DUPLICATE_OF |
|---|---|---|---|---|---|---|
| School of Polymer Science and Polymer Engineering, Faculty | 18 | 18 | 0 | 0 | 0 | 18 |
| SPSPE Adjunct (all entries commented out in the page HTML) | 0 | 0 | 0 | 0 | 0 | 0 |
| SPSPE Emeritus | 14 | 14 | 0 | 13 | 0 | 1 (Kyu, held) |
| Chemistry (full-time, joint, staff) | 22 | 19 | 1 | 11 | 6 | 1 |
| Chemical, Biomolecular and Corrosion Engineering | 17 | 15 | 0 | 11 | 3 | 1 |
| Biomedical Engineering | 21 | 20 | 0 | 15 | 4 | 1 |
| Mechanical Engineering | 63 | 57 | 0 | 50 | 6 | 1 |

Rows added by tier: people.csv 1 at tier A; evidence_people.csv 2 rows. Per institution: ORG-000501 only. Persons listed in two units are counted once, under the first.
Gate B was adjudicated for the 45 candidates whose listing title passed Gate A and who were not already held.

## Held (not written)
| Person | Verdict | Settling fact / recommendation | Applied or held |
|---|---|---|---|
| Bi-min Zhang Newby (CBCE chair, Professor) | STILL_UNCERTAIN | Her own profile lists "polymer thin films", but its URL carries a UA network id and no identifier-free page states it (her lab site is Google Sites). Settles: an owner exception to cite the profile URL, or an institutional identifier-free page. Recommend the exception (about 20 held Akron rows cite such URLs). | held |
| Hossein Ravanbakhsh (BME, Assistant Professor) | STILL_UNCERTAIN | Same: profile states hydrogel and smart-polymer research; only witness is an identifier URL (his lab site beta-lab.org is not institutional). Same settling fact. Rows PERSON-002300/002301 from the first draft were withdrawn, not merged. | held |
| Yi Pang (Chemistry) | STILL_UNCERTAIN | Profile research text is dyes and sensors; polymer only in publication headings. Lab page gozips.uakron.edu/~yp5 did not load (HTTP 000). Settles: a loadable lab page or profile statement naming polymer research. | held |
| Sergei Lyuksyutov (Physics, joint Chemistry) | STILL_UNCERTAIN | Biography plus publications (polymer nanolithography titles), no research statement; lab page nebula.physics.uakron.edu/dept/faculty/sfl.htm did not load over http (the https form was not tried). Settles: a page of his own stating polymer research. | held |
| Robert Mallik (Physics, joint Chemistry) | STILL_UNCERTAIN | Research is semiconductor thin-film surface science; polymers and SBR are substrates for a patterning technique. Gate B scope call for the owner; recommend REJECT (McComb precedent). | held |
| Hossein Tavana (BME chair) | STILL_UNCERTAIN | Profile research is cancer, microtechnology, tissue engineering; lab page tavana.uakron.edu returned only a script shell. Settles: the rendered lab page naming polymer research. | held |
| 13 teaching-track persons ("Professor/Associate Professor of Instruction, Practice or Engineering Practice"; listed in `verdicts.csv` with note "Owner question") | STILL_UNCERTAIN | **Owner question (role vocabulary):** is a Professor of Instruction or Practice a Gate A professor rank? SCHEMA 4.9 (role enum; faculty-rank line v1.7.5) names research-professor and lecturer ranks only. The one precedent is a lane call (wave4-ndsu, Amiri, Professor of Practice), not an owner ruling. None examined for Gate B. | held |

## Proposed follow-ups (for the controller; no data touched)
1. **Currency of held rows.** Thein Kyu (PERSON-000075, held as professor) is styled "Distinguished Professor Emeritus" on the SPSPE Emeritus page. Toshikazu Miyoshi (PERSON-000059) and Xiong Gong (PERSON-000060) are not on the SPSPE Faculty page; Shing-Chung Josh Wong (PERSON-000056) is not on the Mechanical Engineering listing. 4.9 says a changed or vanished profile downgrades to U.
2. **Identifier URLs.** The `u=` value in uakron.edu profile URLs is the person's UA network ID; about 20 held Akron rows already carry such URLs. This lane complied with the brief and published none; the owner may want a ruling on the held ones.
3. A name match of Yilin Liu (Akron Chemistry) to "Yi Liu" (PERSON-000593, LBNL) was checked and is a different person.
4. Luettmer-Strathmann's scope quote is a research-topic list on her own page; recorded supports_A per people-class precedent (776 supports_A scope rows, list-style ones among them, for example EVD-280045). Downgrade to supports_B if the controller reads contract rule 5's list-item cap as applying to people.

## Sources
Own-domain pages only. Provenance root for the College of Engineering pages: the held PERSON-000046 profile URL -> its "About the College" link -> the People Directory link on that page. SPSPE people pages, Chemistry faculty-staff listing, CBCE/BME/ME people pages and profile pages, and lab pages linked from profiles (metacomposites.uakron.edu, blogs.uakron.edu/mee, jugroup, zhanglab, irl, barkana-signals-lab, boika-research, seamlab, mems, tavana, nebula.physics.uakron.edu). No search engine was used; provenance per fetch is in `manifest.csv`. `check.py` re-verifies every quote against the stored pages.

## Not checked (unresolved, not negative)
- The AFMC page, the CenTiRe site and the bulletin polymer-program page were fetched and added no Gate-A-passing candidate; the NPIC page and research-center rosters were not examined.
- Departments outside the brief's list: Physics (other than the joint faculty on the Chemistry page), Biology, Geosciences, Civil, Electrical and Computer Engineering, Wayne College. The college "All Faculty & Staff" list was fetched for provenance only.
- Lab pages on non-institutional domains (Google Sites, beta-lab.org, leipzigbioe.com) were not used for any gate.
- ORCID identifiers (people_identifiers) and inclusion_log were not touched, by instruction.
