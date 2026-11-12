# Penn State MatSE link pass — research packet — 2026-11-12

**Lane:** Penn State MatSE link pass (packet-only — no repo data edited, no
branches, no PRs). **Authorized:** owner-approved 2026-11-12 as the follow-on
to the carried-rows unit. **Data read from:** `origin/main` at
`79b1f42b40f3e9580ed19b4e0f29b162f1cc923a` (PR #299 head), read via
`~/workspace/atlas-p2-2026-11-12`. **Rules read:** repo `AGENTS.md`,
`docs/SCHEMA.md`, and the carried-rows packet
(`working/carried-rows-verify-2026-11-12/`), which VERIFIED the two rows this
pass links to. **Paid calls: zero** (direct fetches of Penn State's own pages
plus two web searches; no Tavily/Exa/Firecrawl).

## Targets (not yet on main — integrator maps these keys to allocated IDs)

- **MATSE-NEW** — the MatSE graduate degree row drafted in the carried-rows
  packet (Intercollege Graduate Degree Program in Materials Science and
  Engineering, `degree`, ms;phd, tier A, ORG-002775). The packet flags a
  grain seam (graduate-only as drafted vs. an all-levels department row);
  every LINK in this packet rests on the person's association with the
  department/IGDP, so the dispositions hold under either grain.
- **MCL-NEW** — the Materials Characterization Laboratory `lab_facility`
  row drafted in the same packet (ORG-002775, tier B).
- **Carried set re-derived for ORG-002775:** exactly one active program row
  exists at the institution today — **PROG-000037** (Polymer Science Minor
  (University Park), `course`, tier A). The Behrend rows a reader might
  expect here (PROG-000035 Plastics Engineering Technology, PROG-000163
  Polymer Engineering and Science, B.S.) sit under **ORG-002779** (Penn
  State Behrend's own ecosystem row), not ORG-002775, so they are outside
  this pass's same-institution target set.

## Method

For each of the 18 people, the person's recorded `public_profile_url` was
fetched and read for two things: Gate A styling (the institution styles
them as current faculty; research-professor ranks qualify) and Gate B (a
person-level polymer-research statement on the same or another Penn State
page). Dispositions:

- **LINK** (set `program_org_id`) — the person's witnessed home is MatSE:
  their directory record carries Unit = Department of Materials Science
  and Engineering, or styles them as a MatSE professor in MatSE's own
  directory/roster, with the IGDP-association line present in most cases.
  Degree program primary per the standing rule.
- **BANKED** (evidence only, `program_org_id` unchanged) — home unit is
  another department, but a MatSE/IGDP affiliation is witnessed: the
  IGDP-association line on the MatSE directory profile (Vogt), a joint
  MatSE title styling (Milner), or Penn State News' statement of IGDP
  affiliation plus a MatSE professorship (Kim).
- **NO_WITNESS** — no link proposed: either no MatSE affiliation is
  witnessed anywhere on Penn State's own pages (Elacqua), or the person is
  styled at another campus (Rhoades and Zhang at Behrend, Mathers at New
  Kensington), where the note carries the campus fact and the settling
  fact. No link in this packet papers over a wrong institution assignment;
  re-homing is owner-gated.

**MCL-NEW received no links and no banks.** None of the 18 is styled with
an MCL role (staff, director, or facility leadership) on any Penn State
page read; MCL sits inside the Materials Research Institute, whose
leadership is not among these records. A MatSE faculty member's
characterization work is not an MCL affiliation, so no courtesy banks were
proposed. **PROG-000037 received no links or banks either** — it is an
undergraduate minor (course-type row); no person in scope is witnessed as
its faculty home, and graduate-program primaries govern.

## Counts (unit + filter)

- **Unit: people records with `institution_org_id = ORG-002775` and blank
  `program_org_id` on origin/main `79b1f42b` — 18 of 18 such records**
  (the institution carries no linked people today).
- **LINK 11** — all to MATSE-NEW: Colby PERSON-000703, Hickey
  PERSON-000722, Gomez PERSON-000759, Lopez PERSON-000824, Hasegawa
  PERSON-000825, Sinha PERSON-000831, van der Vlies PERSON-000835, Xu
  PERSON-000836, Qing Wang PERSON-000960, Qiming Zhang PERSON-001097,
  Manias PERSON-001394.
- **BANKED 3** — all to MATSE-NEW: Vogt PERSON-000762, Milner
  PERSON-000764, Kim PERSON-000778.
- **NO_WITNESS 4** — Elacqua PERSON-000735 (no MatSE affiliation
  witnessed), Rhoades PERSON-000765 (Behrend), Zhang PERSON-000777
  (Behrend), Mathers PERSON-000784 (New Kensington).
- **Census: 5 candidates** in `census.csv` (below).

## Census

Method: the full MatSE IGDP faculty roster (~104 entries, both pages
read in full) plus the MatSE directory were screened name-by-name against
all of `people.csv`; emeritus faculty, ARL/lab staff not styled as MatSE
faculty, and teaching-only stylings were screened out, and surviving
polymer-plausible names were checked on their own Penn State profile
pages for an explicit polymer statement. **5 people meet Gate A + Gate B
with no Atlas record anywhere:** Patrick T. Mather, Lauren D. Zarzar,
Nutifafa Doumon, Dipanjan Pan, Clive A. Randall — see `census.csv` for
styling and witness quotes. For Doumon, Pan, and Randall the Gate B
witness is roster-grade (MatSE's own Polymers research-area expert
listing) and is flagged as such in the census notes.

Screened but **not** witnessed, so not in the census: Zoubeida Ounaies
(MatSE profile as fetched states no polymer research, and she is not on
the Polymers experts page — settling fact: a Penn State page stating her
electroactive-polymer research), Ayusman Sen and Danielle Reifsnyder
Hickey (their MatSE profile pages state no polymer research), Elizabeth
Elacqua (in `links.csv` as NO_WITNESS — she has a record; her gap is an
affiliation witness, not a census gap).

## Weakest links (integrator/verifier attention, in order)

1. **Gomez LINK (PERSON-000759)** — the browser served a cached copy of
   his MatSE profile crawled **2024-09-16**; the current IGDP roster
   styles him by his College of Engineering associate-dean role. The LINK
   rests on the profile's professor styling + IGDP line + Steidle office.
   Re-open the live page at application; under a strict ChemE-primary
   reading this row flips to BANKED.
2. **Milner BANKED (PERSON-000764)** — the bank rests on joint-title
   styling alone: he is absent from the current IGDP faculty roster
   (absence verified by text search of the roster page, 2026-11-12), his
   profile carries no IGDP line, and the fetched copy is a 2026-01-13
   crawl. If roster-grade affiliation is required for banks, he drops to
   NO_WITNESS.
3. **Qiming Zhang LINK (PERSON-001097)** — his MatSE directory page as
   rendered carries no Unit field; the LINK rests on MatSE directory
   membership + IGDP roster listing + the record's own sourcing.
4. **Kim BANKED (PERSON-000778)** — the affiliation witness is current
   (Penn State News, 2025-06-25), but the polymer witness is his group's
   "Past Research" page (crawl 2026-01-24), not a current research
   statement; his MatSE directory page itself states no polymer interest.
5. **Stale crawls generally** — four fetches returned cached copies
   (Gomez 2024-09-16; Milner 2026-01-13; Kim group page 2026-01-24; Wenhan
   Xu 2026-02-16). Quotes are verbatim from Penn State's own pages as
   cached; nothing in the packet treats a stale page as evidence of a
   negative.

## Fetch log (summary)

28 page fetches + 2 searches, all on Penn State's own domains
(matse.psu.edu, science.psu.edu, ems.psu.edu, behrend.psu.edu,
newkensington.psu.edu, psu.edu, sites.psu.edu, cee.psu.edu via search
extract): 16 of the 18 recorded profile URLs (Rhoades' and Zhang's
dispositions rest on the Behrend directory page, fetched directly;
Mathers' on his recorded New Kensington story URL), the IGDP faculty
roster (read in full, both halves; two text searches run against it), the
Behrend Plastics Engineering Technology directory, the MatSE Polymers
research-experts page, and 5 census-candidate profiles (Mather, Zarzar,
Ounaies, Sen, D. Hickey) plus Seong Kim's group page. **No fetch failed
outright**; no absence in this packet rests on a failed fetch — the two
roster absences (Elacqua, Milner) were verified by text search over a
successfully fetched page. **Paid calls: zero.**

## Deliverables

- `README.md` (this file) — method, counts, census method, weakest links.
- `links.csv` — 18 rows, one per in-scope person: person_id, full_name,
  disposition (LINK / BANKED / NO_WITNESS), target (MATSE-NEW / blank),
  witness_quote, witness_url, note.
- `census.csv` — 5 rows: full_name, role_as_styled, gate_a_quote,
  gate_a_url, gate_b_quote, gate_b_url, note.

---

## INTEGRATION RECORD (integrator of record: spaghetti, 2026-11-12)

Built on origin/main `1880d2446ce88591b451f3da295b801a30026896` (PR #301 head) in worktree `~/workspace/atlas-matse-links-build-2026-11-12`, branch `agent/spaghetti/matse-link-pass-2026-11-12`. The packet files above stand **as authored**; everything below is the integrator's record of application. Pre-pass backups: `~/workspace/atlas-matse-links-backups-2026-11-12/`. Build script: `~/workspace/atlas-resync-2026-11-10/build_matse_links.py` (packet CSVs read programmatically — quotes, URLs, and notes were never retyped).

**Applied — 18 dispositions against PROG-000340 (MatSE graduate degree row, tier A, created PR #301):**
- **LINK 11** — `program_org_id` set to PROG-000340 (+ `last_verified` → 2026-11-12; no other cells): Colby PERSON-000703 (EVD-333882), R. Hickey PERSON-000722 (EVD-333883), Gomez PERSON-000759 (EVD-333884), Lopez PERSON-000824 (EVD-333888), Hasegawa PERSON-000825 (EVD-333889), Sinha PERSON-000831 (EVD-333890), van der Vlies PERSON-000835 (EVD-333891), Wenhan Xu PERSON-000836 (EVD-333892), Qing Wang PERSON-000960 (EVD-333893), Qiming Zhang PERSON-001097 (EVD-333894), Manias PERSON-001394 (EVD-333895). One scope evidence row each, built from the packet's witness quote + URL (claim_type `scope`, source_class `own_site`, tier_effect from the person's own tier — all 11 are tier A → `supports_A`).
- **BANKED 3** — evidence only; people rows byte-untouched, `program_org_id` unchanged: Vogt PERSON-000762 (EVD-333885, IGDP-association line), Milner PERSON-000764 (EVD-333886, joint MatSE title styling — the packet's roster-absence caveat rides in the row's notes), Kim PERSON-000778 (EVD-333887, Penn State News IGDP-affiliation witness). All `supports_A` on the subjects' own tier A.
- **NO_WITNESS 4** — byte-untouched, no people-row or evidence changes: Elacqua PERSON-000735, Rhoades PERSON-000765, Zhang PERSON-000777, Mathers PERSON-000784. Rhoades/Zhang re-homing remains owner-gated and untouched.
- **PROG-000341 (MCL)** — zero dispositions, as the packet assigns.

**Census mints 5 (PERSON-002139..002143, all at ORG-002775, each with existence + scope evidence):**
- PERSON-002139 **Patrick T. Mather** — `professor`, tier A, **unlinked + banked** (EVD-333896 existence, EVD-333897 banked scope): the packet styles his primary record as a Chemical Engineering professorship plus the Schreyer Honors College deanship, with the MatSE tie carried by the IGDP-association line on his MatSE directory profile — the Vogt bank basis. The census note's instruction (record at ORG-002775 with the affiliation stated, not as a MatSE-unit professor) is carried in EVD-333897.
- PERSON-002140 **Lauren D. Zarzar** — `associate_professor`, tier A, **unlinked + banked** (EVD-333898, EVD-333899): home unit Chemistry per the census; joint MatSE styling + IGDP line banked on the Milner/Vogt basis; the packet's thinner-witness note rides in EVD-333899.
- PERSON-002141 **Nutifafa Doumon** — `assistant_professor`, tier B, **LINK** `program_org_id` = PROG-000340 (EVD-333900, EVD-333901): the IGDP roster styles him in the Department of Materials Science and Engineering (department of record).
- PERSON-002142 **Dipanjan Pan** — `professor`, tier B, **LINK** (EVD-333902, EVD-333903): same department-of-record basis.
- PERSON-002143 **Clive A. Randall** — `professor`, tier B, **LINK** (EVD-333904, EVD-333905): same basis.
- **Tier ruling (integrator, documented for the verifier):** Mather + Zarzar grade A — both gates witnessed on their own full MatSE directory profile pages. Doumon, Pan, and Randall grade B — their Gate B witness is MatSE's own Polymers research-area expert listing (roster-grade, per the packet's own flag, carried **verbatim** in EVD-333901/333903/333905) and their Gate A styling is the IGDP roster entry; tier_effect follows each mint's own tier (`supports_B`). `research_specialties` left blank on all five mints (roster-unit precedent: the packet assigns no §3.1/§3.2 vocabulary values, and none were inferred). No §4.21 identifiers minted in this unit.

**Gomez (PERSON-000759) — integrator ruling:** LINK applied per the packet and the owner's brief, **not** flipped to BANKED. The packet's staleness caveat ("CAUTION: the fetch returned a cached copy of this page crawled 2024-09-16; the current IGDP roster (crawled 2026-11-12) lists him under his College of Engineering associate-dean role…") is carried **verbatim** in EVD-333884's notes, with the packet note in full. **P1 title-refresh follow-up:** PERSON-000759 Enrique Daniel Gomez — re-open the live MatSE profile; his current styling (College of Engineering associate-dean role vs. the 2024-crawled professor styling) and the ChemE-primary question settle there.

**Counts (unit + filter):** people rows changed 11 of 1,472 carried (LINKs, exactly `program_org_id` + `last_verified` per row); people rows created 5 (census mints); people rows byte-untouched among the disposition set 7 (3 BANKED + 4 NO_WITNESS); evidence rows appended 24 (EVD-333882..EVD-333905, pure appends to `data/evidence_people.csv`); programs/ecosystem/identifiers files unmodified. Next frees: PERSON-002144, EVD-333906.

**QUEUE:** the carried-rows claim is flipped to `done 2026-11-12 (PR #301, merged)`; the pilot (#298), lane A (#299), and lane B (#300) claims already read done — no stragglers; this unit's claim added below the carried-rows line.

**Gates (run on the built tree):** `scripts/validate.py` → "OK — validation passed." (totals: 5,024 organizations, 408 ecosystem rows, 1,477 people rows, 209 program rows, 40,968 evidence rows; warnings only the standing classes — V-16 un-decomposed claim ORG-004649, V-38 placement queue, V-44 code assignments — none naming this unit's records). `scripts/check_row_loss.py --base origin/main` → "row-loss guard: OK — no keyed row removed from data/ since origin/main (merge-base 1880d2446c)". Row-level diff vs backups: people +5 appends / exactly 11 changed (cells above) / 0 removed; evidence pure appends; no REMOVALS.csv.
