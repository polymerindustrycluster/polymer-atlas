# Wave 4 school pass — Carnegie Mellon University (ORG-002778)

Lane: wave-4 CMU research lane (spaghetti subagent), 2026-11-12. PACKET ONLY — no repo
data written, no branch, no PR. Base: origin/main `79b1f42b` (re-derived from
origin/main in-session). Paid calls: **zero** (browser search + direct page fetches
only; all witnesses on cmu.edu / mse.engineering.cmu.edu / cheme.engineering.cmu.edu /
chem.cmu.edu pages). Failed fetches: none — every page attempted resolved. Two
third-party items appeared in search output (a ceramics.org profile, a job posting)
and were **not** relied on for any cell.

Depth = the 5 cells `research_areas`, `specialty_processes`, `specialty_materials`,
`facilities_note`, `scale_band` (the wave convention).

## Verdicts — carried rows (unit: the 3 carried ORG-002778 program rows at depth 0/5)

| Row | Verdict | Result |
|---|---|---|
| PROG-000125 Materials Science and Engineering [degree] | VERIFIED fills | 4 fill rows covering **3 of 5** depth cells (research_areas, specialty_materials, facilities_note → 3/5). specialty_processes + scale_band held — see below. |
| PROG-000043 Center for Macromolecular Engineering [center] | VERIFIED fills | 2 fill rows covering **2 of 5** depth cells (research_areas, specialty_processes → 2/5). Rest held. |
| PROG-000042 Colloids, Polymers, and Surfaces (CPS) minor [course] | No honest fill — 0 rows proposed | Course-type row. §4.11 reserves `research_areas` for research programs; the minor's own page states a curriculum (45 units, named polymer courses), not §3.1 processes or §3.2 materials; no scale or facilities statement is published. The row stands as carried at 0/5 — this is a fill assessment, not a row verdict. |

Held cells, with reasons:
- PROG-000125 `specialty_processes`: no process is stated at program level on MSE's
  own research pages (polymer processing appears only on a person's bio — O'Connor —
  which is person-level and does not fill a program cell).
- PROG-000125 `scale_band`: the only size figure found (~120 undergraduates) sits on
  a third-party site (ceramics.org), not the institution's own pages, and S3 converts
  only institution-published enrollment or qualitative self-characterizations. Held.
- PROG-000043 `specialty_materials` / `facilities_note` / `scale_band`: not stated on
  the pages fetched.

## Verdicts — people (unit: the 15 people at ORG-002778 with blank `program_org_id` on origin/main)

**12 LINK · 1 BANKED · 2 NO_WITNESS** (links.csv, one row per person).

- LINK → PROG-000125 (MSE degree): Bockstaller (PERSON-000336), O'Connor
  (PERSON-000342), Bettinger (PERSON-000347 — his own BME profile styles him
  "Professor, Biomedical Engineering and Materials Science & Engineering", making
  MSE his degree-program primary).
- LINK → PROG-000043 (CME center): Matyjaszewski (PERSON-000338). LINK, not BANKED:
  he founded and directs the center, has no degree-program row of his own, and the
  center is his witnessed home program in the polymer layer — the primary-home rule
  puts `program_org_id` there.
- LINK → proposed Chemistry row (8): Kowalewski (PERSON-000337), Noonan
  (PERSON-000339), Peteanu (PERSON-000344), Gil (PERSON-000345), Sydlik
  (PERSON-000346), Washburn (PERSON-000348), Yaron (PERSON-000349), Das
  (PERSON-001382). **Contingency:** these 8 links exist only if the proposed
  Chemistry row is created. If it is declined, they fall back to NO_WITNESS (no
  other carried program tie), except that Gil also directs the NMR Center — a
  facility, not a carried row.
- BANKED → PROG-000125: Majidi (PERSON-000343) — MSE courtesy-faculty listing
  witnessed on MSE's own directory; home department (MechE) unrowed. Evidence only;
  `program_org_id` stays blank.
- NO_WITNESS: Chan (PERSON-000340) and Tilton (PERSON-000341) — both pass Gate A +
  Gate B on CMU's own pages but have no linkable program tie (ChemE row fails
  prong (b); see below). Settling facts are in links.csv.

Banked-eligible affiliations beyond the dispositions above (witnessed on CMU's own
pages; evidence rows only, `program_org_id` unchanged, mint at integrator's
discretion): Matyjaszewski → Chemistry row (professorship, if created);
Bockstaller → Chemistry row (Chemistry affiliated-faculty listing);
Sydlik → PROG-000125 (MSE courtesy listing); Washburn → PROG-000125 (MSE courtesy
listing).

Gate notes: Gil is styled "Research Professor, Chemistry; Director, NMR Center" —
research-professor ranks count under Gate A (§4.9, v1.7.5), judged on the
institution's own styling as instructed. Peteanu's and Das's roster tags on the
Chemistry people page do not say "Polymer"; their Gate B witnesses are their own
Chemistry profiles (quoted in links.csv), not the roster tags. Title check (P1
rider): all 15 records' `role_as_published` values match the current CMU rosters as
fetched — no stale titles flagged.

## Department-row tests — §4.11 prong (b) (unit: departments housing the 15-person pool)

- **Chemistry — VERIFIED, row drafted** (proposed_rows.csv). The college's own page
  states the Chemistry B.S. "has specializations in biochemistry, **polymer
  science**, computational chemistry, environmental science, health professions and
  management" (cmu.edu/mcs), and the department's research page names "**Polymers,
  Materials & Nanoscience**" as one of its research areas. That is prong (b) in its
  strong form (a named polymer specialization of the degree itself, plus a named
  polymer research area). Draft restricted to the polymer slice
  (`polymer_synthesis;characterization_methods`); credentials bs;phd as attested —
  **an M.S. was not attested on the pages fetched and is not asserted**; cip_code
  left blank (IPEDS pull owed).
- **Chemical Engineering — REJECT** (no degree row drafted). Deciding fact: ChemE's
  own research index names exactly seven research areas (air quality and climate;
  autonomous and data-driven sciences; biotechnology and pharmaceutical
  engineering; catalysis and surface science; energy, decarbonization, and
  sustainability; process systems engineering; soft materials and complex fluids) —
  none names polymers — and its soft-materials area statement, read in full, names
  colloidal suspensions, gels, emulsions, foams and formulated products, not
  polymers. Polymer themes inside a broader named area are prong-(c) corroboration
  only (UTK CBE precedent). This refuses only a ChemE *degree* row: ChemE's named
  polymer credential already exists as PROG-000042 under prong (a). Consequence:
  Chan and Tilton stay unlinked (above).
- **Mechanical Engineering — STILL_UNCERTAIN** (not drafted). One pool member
  (Majidi) sits there; no MechE page fetched names polymers as a research area,
  track, or concentration of its degrees. Settling fact: a MechE research-areas or
  degree page naming polymers.
- **Biomedical Engineering — not tested.** Its one pool member (Bettinger) resolves
  to the MSE degree row as primary; no BME department page was fetched.

## Census (unit: current faculty on the rosters fetched — Chemistry people page, MSE directory, ChemE research pages)

**2 candidates** (census.csv): Alan J. Russell and Lynn Walker, both styled with a
"Polymer" research-area tag on CMU's own Chemistry roster (Affiliated Faculty) and
both confirmed absent from people.csv on origin/main. Caveat carried in census.csv:
confirm their current ChemE home styling at mint — neither appears on the ChemE
soft-materials area faculty list as fetched. The MSE directory carries no
research-area tags, so no MSE-roster candidate could be witnessed from the roster
alone; Feinberg and Cohen-Karni (BME/MSE) were **not** counted — no polymer witness
on the roster pages fetched.

## Weakest links (named, in order)

1. **Tilton (PERSON-000341) NO_WITNESS** — on the CMU pages opened, his tie is a
   program tie to a course-type row (directs the CPS minor) and no opened page
   states his own polymer research; his record's specialties rest on his
   engineering.cmu.edu bio, cited in the record but not re-opened in this pass.
2. **Majidi (PERSON-000343) BANKED** — the polymer witness quote rides on his
   record's previously cited CMU experts page, not re-fetched in this pass (the
   MSE courtesy listing itself was re-fetched and is current).
3. **PROG-000043 `specialty_processes`** — the ATRP quote sits on the Chemistry
   department's research page describing the center (the institution's own page,
   but not the center's own site; the maty group site carries no center scope
   statement beyond the director's bio).
4. **Bettinger (PERSON-000347)** — his BME profile page's crawl is dated
   2026-02-25; it is the record's own cited source and no contradicting styling
   was found.
5. **Proposed Chemistry row URL** — the department research page was served at the
   legacy chem.cmu.edu address (`http://www.chem.cmu.edu/research/traditional.html`);
   the integrator may repoint to the canonical cmu.edu/chemistry research page if
   it resolves at build.

## Fetch log (summary)

4 searches (MSE research areas; CME/maty members; Chemistry research areas;
ChemE research areas) + 15 page opens, all CMU's own pages: MSE research index,
MSE soft-and-bioactive-materials area page, MSE directory (incl. its
soft-materials-filtered view), O'Connor MSE bio, CPS minor page, ChemE
soft-materials area page, ChemE Chan Group page, Chemistry people roster,
Chemistry research page, MCS college page, MCS research-areas page, Matyjaszewski
(CME director) page, and the Bettinger (BME), Das, Peteanu, and Washburn profiles.
Zero failed fetches; zero paid calls.

---

## INTEGRATION RECORD (integrator of record: spaghetti, 2026-11-12)

Built on origin/main `848175b981848cf9cd62956b6cdf6680ac234ee7` (PR #302 head) in worktree `~/workspace/atlas-w4-cmu-build-2026-11-12`, branch `agent/spaghetti/wave4-cmu-2026-11-12`. The packet files above stand **as authored**; everything below is the integrator's record of application. Pre-pass backups: `~/workspace/atlas-w4-cmu-backups-2026-11-12/`. Build script: `~/workspace/atlas-resync-2026-11-10/build_w4_cmu.py` (packet CSVs read programmatically — quotes, URLs, and notes were never retyped). ID allocation: the Penn wave-4 unit merges before this unit in sequence and allocated first, so this unit's floors were set above Penn's ranges by the brief — **PROG-000344 / PERSON-002153 / EVD-333951** — regardless of this base's tree maxima (PROG-000342 / PERSON-002143 / EVD-333905, scanned and asserted at build). Local build only — nothing pushed, no PR.

**Program CREATE — 1:** PROG-000344 **Chemistry** (degree, ORG-002778), packet cells verbatim except: `program_id` allocated; `notes` prepended with the allocation marker and the repoint note below; `url` repointed (next paragraph). EVD-333951 (existence, MCS college page — the B.S. polymer-science specialization, §4.11 prong (b)) + EVD-333952 (scope, department research page naming "Polymers, Materials & Nanoscience"; `research_areas` restricted to the polymer slice `polymer_synthesis;characterization_methods`). `credential_types` bs;phd as attested (M.S. unattested, not asserted); `cip_code` blank (IPEDS pull owed). Both evidence rows `supports_A` on the row's own tier A.

**URL repoint (integrator, under the packet's own license):** the drafted `url` was the legacy `http://www.chem.cmu.edu/research/traditional.html`; packet README weakest link 5 licenses the integrator to repoint to the canonical cmu.edu/chemistry research page if it resolves at build. It resolves (HTTP 200) and the integrator read it at build (2026-11-12): it names the same "Polymers, Materials & Nanoscience" research area. The row's `url` is therefore `https://www.cmu.edu/chemistry/research/`; the legacy address stands as EVD-333952's `source_ref` (the lane's witness) and in the row's `sources` (packet-verbatim). The seam is carried here and in EVD-333952's notes for the verifier.

**Depth fills — 6 packet fill rows applied:** PROG-000125 (MSE degree) 0/5 → **3/5**: `research_areas` = `biomedical_polymers;composites_unspecified` (EVD-333953, EVD-333954), `specialty_materials` = `composites_unspecified` (EVD-333955), `facilities_note` (EVD-333956); `specialty_processes` + `scale_band` held per the packet (no program-level process on MSE's own research pages; the only size figure is third-party, which S3 does not convert). PROG-000043 (Center for Macromolecular Engineering) 0/5 → **2/5**: `research_areas` = `polymer_synthesis` (EVD-333957), `specialty_processes` = `polymerization` (EVD-333958); the ATRP witness's posture (Chemistry department page, not the center's own site — packet weakest link 3) is carried in EVD-333958's notes. **PROG-000042 (CPS minor) byte-untouched** — course grain, no fills proposed or applied. Changed program rows carry `last_verified` → 2026-11-12 and no other cell changes (row-level diff vs backups verified).

**People — 15 dispositions applied (links.csv order; one scope evidence row each, `own_site`, tier_effect from the person's own tier — all 15 carried records are tier A → `supports_A`):**
- **LINK 12** (`program_org_id` set + `last_verified` → 2026-11-12; no other cells): → PROG-000125: Bockstaller PERSON-000336 (EVD-333959), O'Connor PERSON-000342 (EVD-333965), Bettinger PERSON-000347 (EVD-333971). → PROG-000043: Matyjaszewski PERSON-000338 (EVD-333962) — the center is his witnessed home program as founder/director; he has no degree-program row of his own (integrator ruling 2, per packet). → PROG-000344 (the new Chemistry row): Kowalewski PERSON-000337 (EVD-333961), Noonan PERSON-000339 (EVD-333964), Peteanu PERSON-000344 (EVD-333967), Gil PERSON-000345 (EVD-333968 — Gate A as Research Professor under §4.9; his record already carries role `research_professor`), Sydlik PERSON-000346 (EVD-333969), Washburn PERSON-000348 (EVD-333972), Yaron PERSON-000349 (EVD-333974), Das PERSON-001382 (EVD-333975).
- **BANKED 1**: Majidi PERSON-000343 → PROG-000125 (EVD-333966) — evidence only; his people row is byte-untouched, `program_org_id` stands blank (home department MechE unrowed; its prong-(b) test stands STILL_UNCERTAIN in the packet).
- **Secondary banks 4** (evidence only; `program_org_id` unchanged; minted in this build per the brief): Matyjaszewski → PROG-000344 (EVD-333963, Chemistry professorship — corroborated at build on the live Chemistry roster, read 2026-11-12, which carries his entry as "J. C. Warner University Professor of Natural Sciences; Director, Center for Macromolecular Engineering"); Bockstaller → PROG-000344 (EVD-333960, Chemistry affiliated-faculty listing — the same roster page as his LINK witness; corroborated live at build); Sydlik → PROG-000125 (EVD-333970, MSE courtesy listing — corroborated at build on the live MSE directory: "Courtesy Faculty, Biomedical Engineering, Materials Science and Engineering"); Washburn → PROG-000125 (EVD-333973, MSE courtesy listing per the packet — build posture stated in the row's notes: the live MSE directory confirms his entry and styling, but the explicit "Courtesy Faculty" label text was not visible in the integrator's extract for his entry; weakest of the four, flagged for the verifier).
- **NO_WITNESS 2 — byte-untouched, no evidence:** Chan PERSON-000340, Tilton PERSON-000341 (ChemE degree row REJECT under prong (b) per the packet; settling facts in links.csv).

**Census mints — 2 (both at ORG-002778, role `professor`, tier B, recorded UNLINKED with the Chemistry affiliation BANKED):**
- PERSON-002153 **Alan J. Russell** — EVD-333976 (existence) + EVD-333977 (banked scope → PROG-000344; Gate B witness "Research Areas: Polymer, Biomaterials").
- PERSON-002154 **Lynn Walker** — EVD-333978 (existence) + EVD-333979 (banked scope → PROG-000344; Gate B witness "Research Areas: Polymer, Nanoscience, Imaging").
- **Adjudication (integrator ruling 4):** the packet styles both as Chemical Engineering faculty (Affiliated Faculty on the Chemistry roster) but does not settle a primary program home, and ChemE has no carried row — its degree row failed prong (b) in this same pass. Per the brief, both are minted with the packet's styling verbatim and the witnessed Chemistry affiliation is banked rather than forcing a primary; `program_org_id` stands blank on both. The census caveat (confirm ChemE home styling at mint; neither appears on the ChemE soft-materials area faculty list as fetched) rides verbatim in all four evidence rows' notes; the integrator's build-time corroboration (live Chemistry roster, read 2026-11-12, carries both entries with the packet's stylings and research-area tags exactly) is recorded in the existence rows.
- **Tier ruling (integrator, documented for the verifier):** B for both mints — both gates rest on the single Chemistry roster page (professorship styling + the roster's own Polymer research-area tag); no individual profile page was witnessed in the packet and the ChemE home styling is unconfirmed. Precedent: the MatSE link-pass roster-grade mints graded B (PR #302). `tier_effect` follows each mint's own tier (`supports_B`, all four rows). `research_specialties` left blank on both (the packet assigns no §3.1/§3.2 vocabulary values; none inferred). No §4.21 identifiers minted in this unit.

**Ecosystem rollup — ORG-002778 recomputed (V-16):** recomputation was first verified to reproduce the carried rollup exactly on the pre-build program set (zero drift). `polymer_program_name`: "Materials Science and Engineering; Center for Macromolecular Engineering; Colloids, Polymers, and Surfaces (CPS) minor" → "**Chemistry**; Materials Science and Engineering; Center for Macromolecular Engineering; Colloids, Polymers, and Surfaces (CPS) minor" (Chemistry joins as the alphabetically first degree row); `polymer_program_url`: the MSE course-catalog URL → `https://www.cmu.edu/chemistry/research/` (first sorted program's URL, mechanically required by V-16); `last_verified` → 2026-11-12. No other ecosystem row moved (row-level diff vs backups verified).

**P1 title-refresh rider:** the packet's title check found all 15 records' `role_as_published` values matching the current CMU rosters as fetched — **no title fixes applied in this unit** (nothing flagged, nothing to apply).

**Counts (unit + filter):** programs: +1 created (PROG-000344), 2 changed (PROG-000125, PROG-000043 — depth cells + `last_verified` only), PROG-000042 and all other rows byte-identical. People: 12 changed (LINKs; exactly `program_org_id` + `last_verified` per row), +2 created (census mints), 3 of the disposition set byte-untouched (1 BANKED + 2 NO_WITNESS). Ecosystem: 1 row changed (ORG-002778 rollup fields + `last_verified`). Evidence: 29 rows appended, EVD-333951..EVD-333979 (8 to `evidence_programs.csv`, 21 to `evidence_people.csv`; byte-prefix pure appends verified). Next frees: **PROG-000345 / PERSON-002155 / EVD-333980** (above this unit's floors; tree maxima on the base stood at PROG-000342 / PERSON-002143 / EVD-333905 — the gap to the floors is the Penn unit's in-sequence allocation).

**QUEUE:** prior claims stand exactly as they are on this base (the MatSE link-pass claim still reads `claimed` although PR #302 has merged — left as-is per instruction; no Penn wave-4 claim stands on this base — left absent); this unit's claim added directly below the MatSE claim.

**Gates (run on the built tree):** `scripts/validate.py` → "OK — validation passed." (totals: 5,024 organizations, 408 ecosystem rows, 1,479 people rows, 210 program rows, 40,997 evidence rows; warnings only the standing classes — V-16 un-decomposed claim ORG-004649, V-38 placement queue, V-44 code assignments — none naming this unit's records). `scripts/check_row_loss.py --base origin/main` → "row-loss guard: OK — no keyed row removed from data/ since origin/main (merge-base 848175b981)". No REMOVALS.csv.
