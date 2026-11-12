# Wave 3 — Roster Candidates Verification (Lane 10) — 2026-11-12

**Packet only.** No repo data was edited and nothing was pushed. Every verdict
rests on the institution's own web pages (Gate A: institution styles the person
as current faculty, or qualifying federal-lab research staff; Gate B:
person-level polymer-research witness on the institution's own pages).
Society-roster mentions were never used as witnesses. Input worklist:
`working/discovery-scan-rosters-2026-11-12.md`. Atlas data read from
`~/workspace/atlas-p2-2026-11-12/data/` (== main `f2c7c814`; people.csv 1,450
rows). Free routes only (browser search + page fetch); **zero paid API calls.**

## Counts (unit + filter)

Unit = one roster-worklist item settled on institution pages.

| Scope | Items | VERIFIED | REJECT | STILL_UNCERTAIN | Other |
|---|---:|---:|---:|---:|---:|
| §B CARRIED_INSTITUTION_NEW_PERSON candidates | 17 | 10 | 4 | 3 | — |
| §A NEW_INSTITUTION_SIGNAL candidates (US) | 2 | 2 | 0 | 0 | — |
| Currency check (Shaoting Lin, PERSON-001355) | 1 | — | — | — | 1 NO_MOVE |
| **Total** | **20** | **12** | **4** | **3** | **1** |

Excluded per plan, untouched: the 5 non-US signals (owner scope call) and the
7 early-career/Padden names (stage-to-settle). No fetches were spent on them.

## Verdicts summary

**VERIFIED, with a program link (2):**
- C. Daniel Frisbie (Minnesota, ORG-002855) → **PROG-000104** (MSE degree;
  UMN graduate-faculty roster witness; all-polymer circuits PI per UMN MRSEC).
- Anna Duraj-Thatte (Virginia Tech, ORG-002845) → **PROG-000063** (MII center
  roster witness; the degree rows did not roster her — see weakest links).

**VERIFIED, no program link (10):** Pablo Zavattieri (Purdue), Qian Chen
(UIUC), Junsoo Kim (Northwestern), Vivian Feig (Stanford), David Kisailus
(UC Irvine), Alexandra Paterson (Kentucky), Paschalis Gkoupidenis (NC State —
currency confirmed: joined NC State faculty 2024, ex-MPI-P is prior history on
the same page), Kyungjin Kim (UConn), Oana Jurchescu (Wake Forest — new
institution), Jian Lin (Missouri–Columbia — new institution).

**REJECT (4), each with a person-level deciding fact:**
- Bryan Boudouris (Purdue) — departed; University of Alabama's directory
  states he joined UA 2024-04-01 as VP for Research + Professor. *Re-verify as
  an Alabama candidate if wanted; do not file as a plain reject.*
- Sheng Xu (UCSD) — UCSD itself reports his primary affiliation moved to
  Stanford on 2025-11-01; UCSD now styles him adjunct only. *Re-verify under
  Stanford, ORG-004688.*
- Avinash Manjula-Basavanna (Northeastern) — Senior Research Scientist on
  Northeastern's own pages; staff title, not faculty.
- Ferenc Horkay (NIH) — strongest reject of the lane: NICHD's 2025 Annual
  Report styles him "Staff Scientist (deceased)" and the section personnel
  page lists him under Former Section Members. Gate A fails on currency
  before the staff-scientist title question is even reached.

**STILL_UNCERTAIN (3), settling facts in `verdicts.csv`:**
- Xin Zhang (PNNL) — identity confirmed (not Xinyu/Xiangwu/Xiaoshi Zhang),
  but PNNL styles him only "staff scientist" and his staff page's polymer
  line is incidental; no tie to PROG-000051.
- Sanaz Farajollahi (AFRL) — no person-level AFRL-published page could be
  found or fetched; all evidence is off-domain.
- Tanya Tschirhart (NRL) — no nrl.navy.mil page naming her was retrievable;
  the NRL release ("research biologist," CBMSE) was reachable only via
  syndication, which does not count as an institution witness.

**Currency check — Shaoting Lin (PERSON-001355): NO MOVE.** The roster
signal's direction is backwards. UW–Madison's own pages show he *joined* UW
as Assistant Professor of Mechanical Engineering in August 2026 (directory
profile current; UW seminar listing Nov 2026); the MSU styling is a Nov 2024
NSF CAREER story from his prior MSU appointment, and MSU's current faculty
directory has no entry for him. The carried UW–Madison record matches the
title as currently published — keep it. No MSU program row is claimed.

## Institution-row proposals (from the two NEW_INSTITUTION_SIGNAL verdicts)

Neither institution exists in the Atlas data (verified against organizations
shards + ecosystem.csv; the Atlas carries only Missouri S&T in Rolla, which
is a different institution from Missouri–Columbia).

| Legal name (as published) | City/State | Institution URL | Candidate admitted |
|---|---|---|---|
| Wake Forest University | Winston-Salem, NC | wfu.edu (dept: physics.wfu.edu) | Oana Jurchescu — "Baker Physics Professor" (variant: "Baker Family Professor of Physics") |
| University of Missouri (styled University of Missouri–Columbia) | Columbia, MO | missouri.edu (College of Engineering: engineering.missouri.edu) | Jian Lin — Professor, William R. Kimel Faculty Fellow |

## Identifiers

**Zero ORCID iDs minted.** No candidate's institution pages linked an ORCID
iD; ORCIDs that circulate in journal/external sources were deliberately not
reported, per the §4.21 institution-page rule. Jian Lin's MU profile links a
Google Scholar profile (a §4.21-approved type since v1.13.1, institution-page
publication basis) — flagged here for the integrator rather than recorded.

## Weakest links (read before integrating)

1. **Zavattieri (VERIFIED)** — Gate B is composites-only: polymer-matrix /
   biomimetic composites and 3D-printed polymers, with no standalone
   polymer-science research line. If the owner wants Gate B to require a
   polymer-primary witness, this is the verdict that flips.
2. **Kisailus (VERIFIED)** — polymer is a genuine but *secondary* strand
   (chitin-based fibers/coatings, biobased photopolymers) inside a
   biomineralization-primary program.
3. **Duraj-Thatte's program link** rests on a center roster (MII,
   PROG-000063), not a degree program; MACR/MSE pages checked did not roster
   her. Single-valued rule is satisfied, but it is a center-grain link.
4. **Three VERIFIED people sit at institutions with carried program rows
   that do not witness them** — Junsoo Kim (Northwestern MSE rosters omit
   this ME professor), Kyungjin Kim (UConn Polymer Science: IMS affiliate
   only), Gkoupidenis (NC State's polymer degree rows do not roster an
   ECE/Physics professor). All correctly carry no `program_org_id`; a future
   roster refresh could change that.
5. **Tschirhart and Farajollahi** are availability-shaped STILL_UNCERTAINs:
   zero institution-domain witnesses were retrievable for either. Their
   settling facts are named in `verdicts.csv`; a home-browser retry against
   nrl.navy.mil / afrl.af.mil is the obvious next attempt before these are
   treated as settled negatives.
6. **Two REJECTs are really re-candidacies** (Boudouris → Alabama, Sheng Xu
   → Stanford). Filing them as terminal rejects loses two genuine polymer
   professors; the integrator should spawn fresh candidates at the new
   institutions instead.

## Files

- `verdicts.csv` — one row per settled item (20 rows): candidate,
  institution (with Atlas org_id where carried), verdict,
  title_as_published, program_org_id (blank unless a carried program row's
  own pages witness the person), witness URLs, notes with the deciding or
  settling fact.

---

## Integration record (integrator, 2026-11-12)

**Built on:** origin/main `1075945` (PRs #284–#295 merged; the residual-pools
unit merges after this one, so this unit's diff is proven against that head).
Worktree `~/workspace/atlas-wave3-roster-2026-11-12`, branch
`agent/spaghetti/wave3-roster-people`. Pre-pass backups:
`~/workspace/atlas-wave3-roster-backups-2026-11-12/`. **Not pushed; no PR
(this build step only).**

**Mints (11 people, all tier A, all from this packet's VERIFIED verdicts;
IDs allocated above the tree-wide maximum PERSON-002127):**

| Person | ID | Institution | Program |
|---|---|---|---|
| Pablo Zavattieri | PERSON-002128 | Purdue (ORG-004662) | — |
| Qian Chen | PERSON-002129 | UIUC (ORG-004657) | — |
| Junsoo Kim | PERSON-002130 | Northwestern (ORG-004650) | — |
| Vivian Feig | PERSON-002131 | Stanford (ORG-004688) | — |
| David Kisailus | PERSON-002132 | UC Irvine (ORG-004722) | — |
| Alexandra Paterson | PERSON-002133 | Kentucky (ORG-004745) | — |
| Anna Duraj-Thatte | PERSON-002134 | Virginia Tech (ORG-002845) | **PROG-000063** |
| Paschalis Gkoupidenis | PERSON-002135 | NC State (ORG-002851) | — |
| Kyungjin Kim | PERSON-002136 | UConn (ORG-004664) | — |
| Oana Jurchescu | PERSON-002137 | Wake Forest (ORG-013501, new) | — |
| Jian Lin | PERSON-002138 | Missouri–Columbia (ORG-013502, new) | — |

Each mint carries an admission `existence` evidence row (Gate A styling)
and a `scope` evidence row (Gate B witness), own_site / supports_A;
Duraj-Thatte's scope row is her PROG-000063 LINK row in the standing
format, with the packet's center-roster caveat carried in its text. The
packet's two flagged weakest VERIFIEDs stand as minted, with their
caveats carried verbatim in the scope rows: Zavattieri (composites-only
Gate B, EVD-333763) and Kisailus (secondary-strand Gate B, EVD-333771).
`research_specialties` and `lab_url` stand blank on all 11 — the packet
drafts neither cell for any roster candidate (the wave-3 mint precedent:
Behrend / Penn College / Ferris rows likewise blank; Frisbie's filled
specialties came from his school packet's drafted cells, which this
packet does not provide).

**Brief-vs-packet name differences (packet governed, per the standing
rule):** the integration brief named five candidates in forms this
packet does not carry — "David Zavattieri" (packet: **Pablo
Zavattieri**), "Michael Feig" (packet: **Vivian Feig**), "Derek
Paterson" (packet: **Alexandra Paterson**), "Ioannis Gkoupidenis"
(packet: **Paschalis Gkoupidenis**), "Vandana Duraj-Thatte" (packet:
**Anna Duraj-Thatte**). The packet's institution-page-verified names
were minted in every case.

**New institutions (2 ecosystem rows, institution grain — the
people-anchor precedent shape of ORG-004745 Kentucky / ORG-004688
Stanford: a single `ecosystem.csv` row, no organizations-shard row and
no site row; IDs allocated above the tree-wide ORG maximum
ORG-013500):**
- **ORG-013501 Wake Forest University** — Winston-Salem, NC (Forsyth);
  university_college; polymer_program=false; ipeds_unitid 199847 and
  ROR https://ror.org/0207ad724, both verified at source this pass
  (IPEDS HD2024 local extract; api.ror.org domain match on wfu.edu).
- **ORG-013502 University of Missouri-Columbia** — Columbia, MO
  (Boone); university_college; polymer_program=false; ipeds_unitid
  178396 and ROR https://ror.org/02ymw8z06 verified the same way. The
  packet's legal-name framing is preserved in the row's notes (legal
  name as published "University of Missouri", styled
  "University of Missouri–Columbia"); the campus-qualified form is
  carried as `legal_name` per the Atlas's campus precedent (cf.
  "University of California, Irvine") and to keep the record distinct
  from Missouri S&T (ORG-004736).
Each carries existence + scope evidence rows (EVD-333758..EVD-333761);
scope is person-grain (the admitted person's witnessed research
program) — no program row is created for either institution.

**Not touched (per packet + brief):** C. Daniel Frisbie — already
minted as PERSON-002117 in the Minnesota unit, not duplicated. The 4
REJECTs (Boudouris, Sheng Xu, Manjula-Basavanna, Horkay) and the 3
STILL_UNCERTAINs (Xin Zhang, Farajollahi, Tschirhart) mint nothing and
gain no rows; the packet's re-candidacy notes (Boudouris → Alabama;
Sheng Xu → Stanford ORG-004688) stand in the packet for a future lane.
Shaoting Lin PERSON-001355: NO_MOVE stands, no record motion. **No
identifier rows:** Jian Lin's MU profile links a Google Scholar profile
(a §4.21-approved type since v1.13.1, institution-page-publication
basis) — flagged here only, for a later §4.21 pass; no ORCID was
institution-page-linked for any candidate (packet §Identifiers).

**Evidence:** EVD-333758..EVD-333783 — 26 rows (4 in
evidence_ecosystem.csv: 2 existence + 2 scope; 22 in
evidence_people.csv: 11 existence + 11 scope/link), allocated above the
in-tree maximum EVD-333757 per the serial-sequence allocation (the
residuals/NSF units hold EVD-333744..EVD-333757). Next free
EVD-333784; next free PERSON-002139; next free ORG-013503.

**QUEUE:** the Pittsburg State claim (straggler on this base — its PR
#295 is in the base's git log) is flipped to done, and this pass's
claim is added, per the standing pattern.

**Validation:** `python3 scripts/validate.py` → "OK — validation
passed." (ecosystem 402→404 rows; people 1,461→1,472 rows; evidence
40,844 rows total across all evidence shards; no warning names this
unit's records).
`python3 scripts/check_row_loss.py --base origin/main` → "row-loss
guard: OK — no keyed row removed from data/ since origin/main
(merge-base 1075945d72)". Diff vs origin/main is exactly the push
allowlist in the build report.
