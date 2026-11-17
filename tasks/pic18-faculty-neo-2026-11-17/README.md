# PIC-18 faculty completeness: CWRU, Kent State, YSU, Walsh, Cleveland State, NASA Glenn (atlas-w17-fac-b, 2026-11-17)

<!-- counts: VERIFIED=3 REJECT=141 STILL_UNCERTAIN=42 DUPLICATE_OF=46 -->

**Result, stated plainly: 3 people added, not the dozens the brief hoped for.** Most polymer professors at CWRU (Macromolecular
Science and Engineering) and Kent (AMLCI) were already held. The rest fail or stall on Gate B because the institutions' directory
profiles carry no research text. 42 candidates are STILL_UNCERTAIN, which is unresolved, not negative.

## Counts (unit: candidates examined = rows in `verdicts.csv`, one per person; DUPLICATE_OF = already held, nothing written)
| Institution | Examined | VERIFIED | REJECT | STILL_UNCERTAIN | DUPLICATE_OF |
|---|---|---|---|---|---|
| CWRU | 156 | 2 | 105 | 26 | 23 |
| KENT | 33 | 1 | 10 | 8 | 14 |
| YSU | 25 | 0 | 17 | 2 | 6 |
| WALSH | 3 | 0 | 0 | 2 | 1 |
| CSU | 13 | 0 | 9 | 2 | 2 |
| NASA | 2 | 0 | 0 | 2 | 0 |
| **all** | 232 | 3 | 141 | 42 | 46 |

Rows added: **3 people (PERSON-002400..002402), 6 evidence rows (EVD-394000..394005)**, all `own_site`; tier A for Capadona and Chien, tier B for Lu (scope supports_B). By institution: CWRU 2, Kent 1, YSU 0, Walsh 0, Cleveland State 0, NASA Glenn 0.
Frame size per unit is in `frame.csv` (`listed` = professor-rank entries per CWRU engineering unit, recounted by `check.py` from the
stored directory page; other units list their examined set). Every VERIFIED row has both gate URLs, quotes <=25 words, and the
witness page stored by sha256 under the thread persist folder (`manifest.csv` there).

| VERIFIED | Gate A (rank) | Gate B (polymer) |
|---|---|---|
| Jeffrey Capadona, CWRU (PERSON-002400) | case.edu directory: Donnell Institute Professor of Biomedical Engineering | own lab page: "mechanically-dynamic polymer-based intracortical microelectrodes" |
| Zheng-Rong Lu, CWRU (PERSON-002401) | case.edu directory: M. Frank and Margaret Domiter Rudy Professor of BME | own profile: "Biodegradable macromolecular MRI contrast agents..." (list item, tier-A existence, **scope supports_B**; see owner question 3) |
| Liang-Chy Chien, Kent (PERSON-002402) | AMLCI profile: Professor, Materials Science | own profile: "develops tools and methods of fabrication polymer stabilized liquid crystals" |

## Re-screen after Codex-23's finding (2026-11-17, ~25 min)
Codex-23 found Anirban Sen Gupta falsely REJECTed. Check used: the CWRU engineering bulletins (BME, MACRO, MSE, Chemical and Biomolecular, MAE; fetched from
bulletin.case.edu, provenance in the manifest) matched by name against every CWRU REJECT/STILL_UNCERTAIN row: 79 of the CWRU rows have a bulletin
entry; entries naming a polymer/macromolecule/elastomer/hydrogel/composite object turned up two: **Sen Gupta** and **Ozan Akkus**. Both stay out of the data because their own
profile and lab pages (Sen Gupta's pathology biography page; Akkus's Tissue Fabrication and Mechanobiology Lab page, both fetched) do not state a polymer object; both are now STILL_UNCERTAIN with the bulletin line as the lead
(quoted in `verdicts.csv`). Result: 0 new VERIFIED, REJECT -2, STILL_UNCERTAIN +2. Not re-screened: CWRU rows with no bulletin entry (research-faculty and
non-bulletin names; their fetched profiles hold no polymer statement), Kent (the Kent catalog PDF returned 404; Kent REJECTs rest on AMLCI profiles that do state research naming no polymer object),
and the YSU/Cleveland State rows, which rest on catalog and department expertise lists. Recommendation for the owner: a bulletin line is institution-own roster-grade evidence (YSU catalog pages
are accepted that way for PERSON-000071); if the owner accepts it for Gate B, Sen Gupta and Akkus can be added without further fetching.

**Second sweep (Codex-23 on 9034669): REJECTs resting on a profile that states no research at all.** Peter Tandler (Walsh; profile is a 2021 teaching presentation only) flipped
REJECT to STILL_UNCERTAIN: settling fact is a person-specific research statement on a Walsh page. Sweep of every remaining Gate B REJECT: the 9 hand-written ones (Jaroniec, Genna, Ao, Belovich, Gatica,
Monty-Bromer, Ungarala, Yang) each quote a stated research/expertise line, and the 130+ generated CWRU/Kent ones were re-tested by looking for a substantive research text after the profile's research heading.
Of those, Julie Renner, Bryan Schmidt and Anuj Sharma state research (prose or topic keywords) naming no polymer object, and Robert Warburton's profile only links his lab: his lab page
(fetched, provenance in the manifest) states computational energy-storage/catalysis research, so his REJECT stays, now citing the lab page. No other flips: Gate A rejects (rank) unchanged.
Net since 9034669: REJECT -1, STILL_UNCERTAIN +1; data delta unchanged (+3 people, +6 evidence).

## Owner-ruling questions (held, not self-ruled; recommendation in each)
1. **John L. West (Kent).** AMLCI profile styles him "Trustees Research Professor" (held precedent: PERSON-000023 Lavrentovich is
   `research_professor` with the same styling). His polymer-fiber research is stated only on an undated seminar-style bio. Recommendation:
   accept the role mapping as precedent, and add him once a current page states the research.
2. **Chandra Kothapalli (Cleveland State).** Professor; the only statement ("extracellular matrix-based hydrogels and electrospun
   nanofibrous composites") is on a department research page. Is ECM-protein hydrogel work a polymer object? Recommendation: yes for hydrogels, but hold for his own profile text.
3. **Hanbin Mao (Kent).** Single-molecule biophysics of "biomacromolecules including DNA and proteins". Recommendation: not polymer research (hold).
   The same question cuts the other way for Lu, whom I verified on "macromolecular" contrast agents (a polydisulfide polymer
   class) at scope supports_B; if the owner rules macromolecule-only wording insufficient, retire PERSON-002401's scope row.

## Follow-ups for the controller (nothing written)
- **Pedro Cortes** is held as PERSON-001142 at ORG-004749 (University of Texas at El Paso) but is listed at YSU in the 2022-23 graduate catalog. Probably moved; the held row may need review.
- NASA Glenn: no staff directory reachable from held URLs or search; Meador and T. Williams (NTRS authorship only) and Goldberg (lead, not fetched) are unadjudicated.
- Michael Keating: a directory anchor whose name never appears as text on the page (`common.MISSING`), not examined.

## Provenance and honesty notes
- Frame URLs came from held records (ecosystem/programs/people URLs), links on fetched pages, or web-search results; each fetch's provenance is in the manifest.
- **13 URLs were guessed/constructed** (host variant `engineering.case.edu/about/school-directory/<slug>` from a directory link slug; 4 returned 404, and 9 pages are in the manifest) **plus 1 parent path of a held URL**. The stored ones are labelled CONSTRUCTED in the manifest, and `check.py` fails if any verdict cites one. None is cited.
- REJECT means the fetched profile has a research statement naming no polymer object; lab pages were not followed. A profile with no research statement is STILL_UNCERTAIN, never REJECT.
- Raw pages can contain emails/phones (public page bytes); none is copied into data, task files, or the manifest.

## Not checked (unresolved, not negative)
See the NOT ADJUDICATED rows in `frame.csv`: CWRU units outside the five engineering departments and Arts & Sciences other than Chemistry; Kent AMLCI affiliates in
unrelated units and Kent faculty outside AMLCI; YSU beyond two catalog listings and current rosters; Cleveland State Mechanical/Physics/Chemistry; most Walsh; NASA Glenn staff. No lab pages were followed for REJECT rows, and no ORCIDs/identifiers were touched.

## Files
`verdicts.csv` (one row per candidate), `frame.csv`, `build.py` (idempotent; writes the data rows from VERIFIED verdicts, IDs from the blocks), `check.py` (`--selftest` injects four defects),
`gen_verdicts.py` (records the judgments from stored witnesses), `fetch.py`/`view.py`/`screen.py`/`common.py` (tooling).
