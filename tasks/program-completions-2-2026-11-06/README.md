# L13 deterministic completions application

Controller assigned all147 unapplied proposals first, on a new branch off current main,
then remaining169 national leads if time allows. Branch agent/codex/program-completions-2.
PR144 and PR160 remain independent unchanged. Controller integrator delegation unchanged.
First user: Atlas/PIC program researcher; non-use finding date2026-12-06.

## Acceptance before application

- Reconcile exactly147 proposal rows to held program IDs and current institution UNITID,
  CIP, program_type and levels. IPEDS never establishes programme existence/scope.
- Only held degree records with unambiguous matching identity/CIP/count/award-level
  coverage may receive completions fields; certificate/center/training/etc excluded.
- Recompute first-major totals from NCES raw C2024_A, excluding total/second-major
  records and non-detail award levels. Reconcile against committed completions extract
  and proposal totals; stop on conflicts. Do not narrow/expand a mixed-level count by
  self-ruling: hold mixed/mismatch/certificate-contaminated proposals for owner semantics.
- No first_year_awarded fill from a finite observation window without actual-start
  evidence/ruling. last_year_awarded explicitly means last observed positive year,
  not final award/closure. No status, tier, own-program verification date or CIP changes.
- Keep all existing evidence; add program activity evidence for applied numeric fields
  in EVD285100–289999, leaving PR144/160 allocations untouched. Source cite raw NCES
  with vintage and join key, not a task packet. Only programs/evidence_programs change.
- Idempotent builder, preimage conflicts fail before writes, old-row preservation;
  known-answer fixture before using new join; inject wrong-key/mixed-level defects.
  validate.py zeroerrors. Codex3/Grok3 deep refutes before completion approval; draft
  allowed under controller05:55/06:25 routing, only controller merges/closes.

## Semantics holds to request

The source REPORT expressly says level narrowing is an integrator/owner call, not
specified in SCHEMA. Recommend hold mixed/mismatch/postbacc contamination; keep held
counts unchanged and apply only keys whose positive awards fit the held levels.
The finite2011–2024 window and CIP recoding do not prove a true first award year;
recommend keep first_year_awarded blank until owner approves bounded-first semantics
or a primary actual-start witness. Unaffected aligned counts can proceed.

## Applied results (unit: proposal rows / held programs)

147 unique proposals adjudicated: **34 VERIFIED /81 REJECT /32 STILL_UNCERTAIN**.
REJECT here rejects a numeric-field proposal on a non-degree row under SCHEMA4.11;
it never rejects the held programme or changes status. Each32 hold has a settling
fact in verdicts.csv. All9 proposed first-year fields are separately held in
field_holds.csv, including five on otherwise eligible confirmed programs.

34 held degree programs receive112 cells: last_year_awarded34, sources34, notes34,
latest_completions5, completions_year5. **Five blank count pairs filled;29 held pairs
confirmed.** All34 last-observed-year cells filled with2024; no program row created,
no CIP/UNITID/level/status/tier/own-page verification-date edits. Sources/notes explicitly
state whole institution×CIP counts, not polymer-track headcounts. No ecosystem row edit.
34 append-only program activity evidence rows EVD285100–285133 (registry/supports_C
observations only), without changing any existing record tier or existence/scope basis.

Base commit bdb8b98, main at branch creation. Programs166→166; evidence_programs293→327.
PR144 and PR160 do not ride this branch, and their ID blocks are disjoint.

## Provenance and exact semantics

Fresh NCES `C2024_A.zip` fetched2026-11-06. Existing house parser
scripts/build_ipeds_completions.py is reused without modifying it, restricted in the
local module instance to collection year2024. source.json records the raw member hash,
URL and vintage (awards2023-07-01 to2024-06-30, provisional release as source packet).
raw_2024.csv is104 detail-level rows over the44 numeric proposal keys, with first-major
flags (all R) and second-major counts kept separate. All44 numeric proposal totals
reconcile to the fresh raw source, not merely to the old packet summary.

Independent DuckDB inspection of the full raw source:307707 raw rows =307707 unique
UNITID×CIP×MAJORNUM×AWLEVEL keys; major1 has286979 rows, major2 has20728; no other
major code. Detail award-level vocabulary checked; source aggregate/total rows and
second majors never enter the first-major totals. No extra program code is inferred.

Known answers before trusting the join: Shawnee6=1associate+5bachelor; Ferris30=
12associate+18bachelor; Everett56=10associate+7short-certificate+39certificate.
Everett's held10 is NOT overwritten with56. PROG38 and57 also stay held because their
all-level counts include postbaccalaureate awards. Neither all-level nor narrowed counts
are applied to mixed cases before an owner semantics ruling.

identity_check.csv records34 current held institution joins against fresh HD2024 name/
domain records (same2026-11-06 identity pull used in prior batch, no program evidence).
Penn State Behrend alias vs Pennsylvania State University-Penn State Erie-Behrend College
is preserved at UNITID214591, same institutional campus; no fuzzy re-pointing. Current
held institution IDs, CIP codes, types and levels must match frozen joins before writes.

No first_year_awarded inference: the finite observation window and CIP recoding can
make an old program appear new. last_year_awarded2024 means only a positive award count
observed in2024, never program closure or last-ever award. Broad14.1801 counts are the
whole MSE CIP totals, not the polymer track. All existing own-program evidence remains
unchanged; the statistical registry is never used to create or prove an in-scope program.

## Reproduce / named checks

1. Download https://nces.ed.gov/ipeds/datacenter/data/C2024_A.zip and extract member
   C2024_a.csv into `<raw>/x_C2024_A/` (case-insensitive member selection is in house parser).
2. On main's pre-application data, `python3 tasks/program-completions-2-2026-11-06/prepare.py --raw-dir <raw>`
   generates the frozen packets: PASS all44 raw totals/3 known answers,147 dispositions.
   prepare is a packet-preparation step, not the replay command after application.
3. `python3 tasks/program-completions-2-2026-11-06/check.py`: PASS147 frame/dispositions,
   all44 raw totals,112cell/34program accounting,34evidence, known mixed-count holds,
   old-row/evidence preservation, byte-identical replay, and injected wrong-UNITID plus
   wrong-shard EVD no-write failures.
4. `python3 tasks/program-completions-2-2026-11-06/build.py`: PASS112 declared cells,
   34evidence appends; second run0appends. Globally checks every preimage/join/evidence ID
   before any canonical write. New evidence uses append_sorted.
5. `python3 scripts/validate.py`: PASS zero errors. No scripts/ changes, so scripts pytest
   suite not run; task check covers this builder, existing parser known answers and failure cases.

After main moves, merge main; on conflicting owned CSVs take main's files and rerun
builder. A join/preimage drift fails closed and requires re-preparation/review, never
hand-merge numeric cells. Branch base history is pre-pass backup; README is pass journal.

## Review / remaining work

Independent deep Codex3 review pending under06:25 route; Grok3 approval recorded below. Draft allowed under
05:55 override; no completion approval or Done claim until findings resolved. Registry
counts need no fabricated natural-language quotes: exact raw numeric rows, join keys,
parser, totals and source hash are the witnesses. No personal records involved.

Controller was notified of recommendations to hold mixed/mismatch/postbacc counts and
first-year semantics; no owner ruling presumed. Remaining169 national leads are not
worked by this branch. The94 batch2 STILL_UNCERTAIN settling facts remain committed in
PR160 holds.csv and are targeted follow-ups, not silently discarded leads.

Draft PR https://github.com/polymerindustrycluster/polymer-atlas/pull/168 .
Codex3/Grok3 deep review requests queued for head72c9de9; Grok3 reviewed f67c207 (same data plus README), Codex3 verdict pending.
Earlier PR144/160 remain unchanged on their own branches and review queues.

## Grok family approval receipt

Grok/xAI clerk3thr_4g4uwqjxjv APPROVE f67c207d23f99f18e991ecc00ed550532c609c84,0findings. Independently verified 147proposals=34VERIFIED/81degree-onlynumericREJECT/32holds;112cells/34programs;5newblankcountpairs/29confirmedpairs;34registry supports_C EVD285100–133 append-only. Fresh raw C2024_a hash a7f6d0f03093eef933ea5a31474ca1289cb97c73062b7cc1245fc3cabaff7c61 matched307707unique keys (major1286979/major220728). Recomputed mixed-award Shawnee6,Ferris30,Everett56 remainunapplied;GT114 ondegreelevels only. No first-year write;2024 notclosure; institution×CIP notpolymer-trackheadcount. Check/replay/wrongUNITID+wrongshardzero-write/validate0/row-loss PASS. Latermain changes needintegratorreplay; notcontent defect. Report: reviews/168-clerk-grok-3.md incontrollerstorage. Codex3 approval remains pending; no two-family completion approval/Done claim. No freshweb or fullscriptspytest repeated for this docs-only receipt.
