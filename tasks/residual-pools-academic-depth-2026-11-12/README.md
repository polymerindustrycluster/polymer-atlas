# Wave 3 — Residual pools link pass: Ohio State + UT Knoxville (2026-11-12)

Packet-only lane (wave-3 plan, lane 8). No `data/` files were edited and
nothing was pushed. Data read from `~/workspace/atlas-p2-2026-11-12/data/`
(== main `f2c7c814`). All fetches were free routes (browser text fetch +
web search); **paid calls: zero**.

## Counts (unit + filter stated)

Filter: people rows in `data/people.csv` whose `institution_org_id` is the
institution's org row AND whose `program_org_id` is empty, re-attempted
2026-11-12 against that institution's carried rows in `data/programs.csv`.
People already carrying `program_org_id` were not re-examined and are
never relinked.

| Institution | Org | Carried program rows | Pool (people, unlinked) | LINK | NO_WITNESS | Linked after pass (people) |
|---|---|---|---|---|---|---|
| The Ohio State University | ORG-001284 | 4 — PROG-000017 CEMAS, PROG-000018 PSRF, PROG-000019 PENRA, PROG-000108 MSE (degree) | 27 of 33 recorded | 0 | 27 | 6 of 33 (unchanged) |
| University of Tennessee at Knoxville | ORG-004681 | 1 — PROG-000154 MSE (degree, MS/PhD) | 15 of 19 recorded | 1 | 14 | 5 of 19 |
| **Total** | | | **42 people** | **1** | **41** | |

The one LINK: **PERSON-002108 Weinan Xu → PROG-000154** (UTK MSE), on the
department's own profile page: "assistant professor in the Department of
Materials Science and Engineering … research focuses on the development
of sustainable/functional polymer composites" — plus his listing on the
MSE core faculty roster. Degree-program primary; no second program
witnessed, so nothing banked. No `lab_url` is published on his profile
page; no new `lab_url` witnesses were captured anywhere in this pass.

## What changed vs the earlier NO_WITNESS set

**Ohio State:** all 27 unlinked people were already NO_WITNESS in the
Ohio depth pass (lane B, 2026-11-11, PR #269), which read the complete
MSE Department Faculty directory, the PENRA member pages, the PSRF page,
and the CEMAS industry page. This pass spent its fetches only on surfaces
lane B had not read: the MSE Polymers research-area page (names no
faculty), the CEMAS directory (names MSE faculty/CEMAS staff only — no
pool person), both pages of the CBE research-faculty directory, Ho's
CBE profile, and re-reads of PENRA Researchers and the PSRF page.
**No verdict changed.** Two genuine deltas, both recorded as flags, not
verdicts:

- **Watkins (PERSON-000033)** is now styled **Professor** (Chemistry and
  Biochemistry + CBE joint) on OSU's CBE directory; the record still says
  Associate Professor. Title flag in `currency_flags.csv`.
- **Ho (PERSON-000037)** — see weakest links below.

**UT Knoxville:** there was no earlier link pass and no earlier
NO_WITNESS set — this is the first attempt on the 15. The four existing
links (Advincula, Vogiatzis, Zawodzinski, Norwood) predate this lane and
were left untouched per the no-relink rule.

## Why the yield is ~zero — the structural finding

This residual is a **program-row gap, not a witness gap**. At both
institutions the recorded polymer faculty sit overwhelmingly in units
the Atlas does not row:

- **OSU:** CBE (Ho, Sangoro, Hall, Cooper, Wang, Palmer, Han — the CBE
  directory itself tags Sangoro/Hall/Wang/Watkins with a "Polymers,
  Nanomaterials" research area) and Chemistry (Watkins, Sevov, McGrier,
  Bong, Olesik, Wyzgoski) have no degree-program rows. The four carried
  rows are one degree program (MSE, whose own directory was read in
  full — only the 6 already-linked pool people appear) and three
  facilities/centers (CEMAS, PSRF, PENRA) whose pages name staff and a
  handful of investigators, not faculty rosters.
- **UTK:** Chemistry (Dadmun, B. Zhao, Long, Brantley, Kilbey-joint),
  CBE (Stein, Doxastakis, Khomami, Edwards, Corder, Kilbey-joint), CEE
  (Penumadu — IAMM), MAE (Compton, Duty), and UTORII (Popov) are all
  unrowed. MSE's core **and** joint faculty rosters were read in full;
  none of the 14 appears on either. Their center homes (SMaRT, IAMM)
  are likewise unrowed.

Link completion for these pools therefore waits on program-row
*creation* decisions (CBE/Chemistry degree rows; SMaRT/IAMM center
rows) — discovery-lane and owner-scope material, deliberately outside
this packet. Do not re-run this lane against the same carried rows; it
will return the same 41 verdicts.

## Weakest links / near-misses

- **Xu → PROG-000154 is the packet's only LINK and it is strong** —
  the program unit's own profile page carries both the faculty styling
  (Gate A) and the polymer research statement (Gate B). No weak LINK
  ships in this packet.
- **Ho (PERSON-000037) is the weakest NO_WITNESS and the one judgment
  call.** His CBE-hosted profile styles him Distinguished Professor in
  CBE *and MSE* with polymer-membrane expertise — on its face a
  membership claim for PROG-000108. Against it: MSE's own current
  faculty directory omits him, and he is absent from CBE's current
  research-faculty directory. A home-department bio sentence was not
  upgraded over the program's own roster. Settling fact: his appearance
  on any MSE-owned roster/program page (or an MSE page naming him
  emeritus, which would settle it the other way).
- **Polyák (PERSON-000096) → PENRA** remains NO_WITNESS on the same
  basis as lane B: PENRA's own pages name Cornish, Cardina, Fresnedo,
  Michel, Shah — not him. Research-group membership (Puskas group) is
  not program membership.

## Currency and title flags (`currency_flags.csv`)

**Zero departure flags.** No institution page read in this pass shows
any pool person at a new institution or newly styled emeritus. (Lee,
PERSON-000036, sits in CBE's Faculty Emeriti section, but the record
already styles him emeritus — consistent, not a flag. Cooper,
PERSON-001324, is styled as current faculty — no flag.) The file
carries three flag-only rows: Watkins's stale title (above), and
directory-absence observations for Ho and Han (PERSON-000038), each
explicitly marked `departure_witnessed=no` so no one infers a departure
from a directory omission.

Also flagged in `links.csv` notes, for the integrator: PERSON-001196
(Popov) is carried with a Cyrillic `full_name` and quote debris inside
`role_as_published` — a record-hygiene defect from an earlier pass,
flagged only, not adjudicated here.

## Method / fetch log

Program clusters and primary fetches (cap ~6 per cluster; all under):
OSU–MSE: MSE research index + Polymers area page (directory itself read
in full by Ohio lane B and relied on, not re-fetched). OSU–CEMAS:
directory via search + listing. OSU–PENRA: Researchers page re-read.
OSU–PSRF: facility page re-read. OSU–CBE (context/currency only — CBE
is unrowed): directory pp. 1–2, Ho profile. UTK–MSE: core faculty
roster, joint faculty roster, Xu profile. Searches: 3 (OSU MSE
affiliated faculty; UTK MSE joint appointments; CEMAS directory).
Failed/odd fetches: none blocking. Availability caveats: the fetched
PENRA Researchers copy carries a 2025-01-24 crawl stamp and Ho's
profile copy a 2026-06-02 crawl stamp — both are recorded as the copy
actually read; neither caveat changes a verdict, since both verdicts
rest on multiple surfaces.

## Integration record (integrator of record, 2026-11-12)

**Applied** on branch `agent/spaghetti/wave3-residual-pools-depth` from
origin/main `616dad40f3a6430433cbc6543fd72a931cfb53d6` (build only —
not pushed; PR follows the standing batched-approval pattern).
Build script: `~/workspace/atlas-resync-2026-11-10/build_residuals_wave3.py`;
pre-pass backups: `~/workspace/atlas-wave3-residuals-backups-2026-11-12/`.

**This unit's real output is the finding, not the link count.** Of the
packet's 42 verdicts (Ohio State 27 NO_WITNESS; UT Knoxville 1 LINK +
14 NO_WITNESS), exactly **1 produced a link**. The other 41 records are
byte-untouched and carry no new evidence rows: the residual is a
**program-row gap, not a witness gap** — the recorded polymer faculty
sit in units the Atlas does not row (OSU CBE and Chemistry; UTK
Chemistry, CBE, CEE, MAE, UTORII, and the SMaRT/IAMM centers). No new
program rows are created in this unit; row creation for those units is
an owner-scope decision the packet names. Do not re-run this lane
against the same carried rows.

- **Link applied (1)** — **PERSON-002108 Weinan Xu → PROG-000154**
  (UTK Materials Science and Engineering), on the department's own
  profile page: "Weinan Xu is currently an assistant professor in the
  Department of Materials Science and Engineering at the University of
  Tennessee, Knoxville. His current research focuses on the development
  of sustainable/functional polymer composites and their advanced
  manufacturing." — plus his listing on the MSE core faculty roster.
  Changed fields: `program_org_id` + `last_verified` (2026-11-12)
  only. Evidence row **EVD-333744** (`scope`, `own_site`,
  `supports_C` from the record's own tier C). Degree-program primary;
  no second program witnessed, nothing banked; no `lab_url` is
  published on his profile page and none was set. UTK linked after
  pass: 5 of 19 recorded people; Ohio State unchanged at 6 of 33.
- **P1 title refresh applied (1)** — **PERSON-000033 Davita L.
  Watkins** (Ohio State): the packet's `currency_flags.csv` quotes the
  current styling verbatim with its URL — OSU's CBE research-faculty
  directory (cbe.osu.edu/people/faculty, read 2026-11-12) styles her
  "Professor, Chemistry and Biochemistry; Professor, Chemical and
  Biomolecular Engineering" with research areas including "Polymers,
  Nanomaterials". `role` associate_professor → professor;
  `role_as_published` "Associate Professor" → "Professor, Chemistry
  and Biochemistry; Professor, Chemical and Biomolecular Engineering";
  `last_verified` → 2026-11-12. Evidence row **EVD-333745** (`scope`,
  `own_site`, `supports_A` from her tier A); the stale styling is
  preserved in that row. No link verdict rests on the directory page:
  CBE and Chemistry carry no program rows, and her record remains
  unlinked.
- **NO_WITNESS (41)** — no link, no person evidence row, records
  byte-untouched (asserted in the build script and by row-level diff
  against the pre-pass backups). Ho (PERSON-000037) stays unlinked:
  his CBE-hosted profile's joint-MSE styling was not upgraded over
  MSE's own directory, which omits him; the settling fact is his
  appearance on an MSE-owned roster or program page.
- **Flag carried verbatim, not actioned** — the packet's note on
  PERSON-001196 (Popov), from `links.csv`: "RECORD DEFECT flagged for
  integrator: full_name is carried in Cyrillic and role_as_published
  contains embedded quote debris from a source snippet. Flag only; not
  adjudicated in this lane." His record is byte-untouched in this unit
  (asserted in the build script); the correction needs its own sourced
  pass. (Current carried values: `full_name` "И. И. Попов";
  `role_as_published` carries a source-snippet fragment with embedded
  quotes.)
- **Evidence minted (2 rows)** — EVD-333744..EVD-333745, both in
  `data/evidence_people.csv`. Allocation starts at EVD-333744 per the
  serial sequence — preceding wave-3 units consumed EVD-333539..
  EVD-333743 on their own branches (this tree's scan max is
  EVD-333660; the gap does not exist on this branch and was not
  backfilled). **Next free: EVD-333746.**
- **QUEUE** — the Texas A&M claim, the one straggler still standing
  `claimed` on current main, is flipped to `done 2026-11-12
  (PR #288, merged)` per the git log; the P2, Minnesota, Southern
  Miss, Lehigh, and Auburn claims already stood done at their real PR
  numbers (#283–#287). This unit's claim is added below it.
- **Gates** — `scripts/validate.py`: "OK — validation passed."
  (warnings only the standing classes; none names this unit's
  records). `scripts/check_row_loss.py --base origin/main`:
  "row-loss guard: OK — no keyed row removed from data/ since
  origin/main (merge-base 616dad40f3)". No REMOVALS.csv.
