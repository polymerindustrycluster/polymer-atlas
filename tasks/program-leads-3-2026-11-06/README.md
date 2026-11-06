# L13 program leads — continuation batch 2

Controller's 2026-11-06 06:30 BOARD assignment: next100 of269 pending leads,
new branch agent/codex/program-leads-3 from main9489b60. PR144 stays unchanged.
Integrator of record controller thr_9i2c6byhcz delegates this application.
First user: PIC/Atlas program-introduction researcher; non-use finding 2026-12-06.

## Acceptance criteria (before research/application)

- input.csv is exactly the first100 original-order pending rows after excluding
  PR144's six pending rows. source_row preserves original worklist row number.
  The frame definition is state not literally OH/PA and held_same_name=False;
  source blank-state rows remain in this inherited frame and are not claimed as
  verified non-OH institutions. 169 pending rows remain outside this batch.
- Exactly one legal verdict per input lead, no IPEDS/CIP-only program creation.
- A create needs a named own-site program under SCHEMA4.11, raw quote matches,
  existing institution or institution-only ecosystem creation after domain/name/
  UNITID/ROR dedupe. ROR remains blank unless verified at api.ror.org.
- Evidence is append-only and covers every added/changed fact; no closure inference
  from unavailable pages or lead descriptions. Owner scope/vocabulary cases held.
- Deterministic packet accounting, duplicate-ID failure, old-row preservation,
  idempotent replay and validate.py zeroerrors. Known-answer calibration before
  trusting matcher. Yield verified/worked leads alongside prior4/49 with units.
- Codex3/Grok3 clerk refutes (06:25 BOARD) before completion approval. Draft PR
  allowed for review under05:55 override; only controller merges/closes tasks.

Existing blocks: PROG000301–000499, ORG013000–013199 institution rows only,
EVD285010–289999, deliberately disjoint from PR144's PROG300/EVD285000–285002.
Only data/programs.csv, evidence_programs.csv, ecosystem.csv,
evidence_ecosystem.csv may change, through this task's idempotent builder.

## Cross-thread instructions

06:12 controller main-normalization recipe supersedes inherited federal-frame
no-touch constraint narrowly for taking main's LF versions. On branch switch,
those two paths were checked out from origin/main before switching to the new
main-based branch; no commit or update to PR144, and no net federal-frame diff.
New reviewers: Codex3 thr_jukpm97t9c / Grok3 thr_4g4uwqjxjv. Re-reviews of
PR144 go to whichever clerk actually refutes that PR.

## Results and yield (unit: input leads)

100 screened/adjudicated leads = **4 VERIFIED +2 DUPLICATE_OF +94 STILL_UNCERTAIN**.
No REJECT, no closure/absence assertion. Verified yield **4/100 worked leads (4.0%)**,
next to the prior OH/PA requested **4/49 leads (8.2%)** applied-program comparison.
Prior numerator is applied program rows; this batch's four verified leads each yield
one program. Selection and research depth differ; no national prevalence or improvement
claim follows. Holds are initial route screening plus selected deeper catalog checks,
not exhaustive six-fetch searches. All100 have route receipts; 169 pending leads remain
unworked beyond this batch, along with147 completions proposals. PR144's six pending
leads and four calibration rows are excluded from this batch denominator.

Applied packet:

- +4 Tier A program rows PROG000301–000304: Davis Composites certificate; Paulson
  University Online Training; UWM Plastics Technology Certificate; Georgia Tech
  Multidisciplinary Composites Certificate Program. No existing program row edited.
- +2 Tier C institution rows ORG013000–013001 (UWM and Davis). +18 append-only
  evidence rows EVD285010–285027:11 program and7 ecosystem. GT rollup regenerated;
  its lead URL retained. No institution tier upgrade, registry-link row or ROR assertion.
- UMass historic University of Lowell lead maps directly to held PROG000057;
  IYRS discovery-grant lead yields held Composites Technology PROG000082. Neither
  discovery label is the program evidence: fresh institution pages carry the names.
- No seam is integrated. Existing institution parent ORG002934 hosts Paulson's
  branded offer; new commercial parents remain outside this institution-only grant.

## Sources and known answers

Institution own program URLs are in programs.csv, quotes.csv and rawcheck.csv. All16
quoted strings matched on6 freshly fetched pages (4 new programs +2 duplicates), with
zero skipped quotes and a fabricated negative rejected. Source hashes/redirects recorded.
Davis HTML timed out but its own catalog-year2026 PDF downloaded. pdftotext returned
no text; render plus Tesseract OCR recovered the heading/credential, checked visually
against the rendered page. Macomb PDF was separately extracted with pdftotext; its
revision5/2019 is why current offering remains held. No raw HTML/PDF is shipped: it
contains unnecessary staff contacts. Research downloads stay in /tmp/l13b-pages.

Three held-program known-answer positives (Stout, Winona, WWU former name) and the
fabricated negative passed before population fetching; calibration.json preserves
URLs, hashes and outcomes. The word normalizer is reused from evidence-repair-2/prep.py.
PDF extraction explicitly fails on unread content; no blank parse can yield a positive.

NCES HD2024.zip was freshly downloaded2026-11-06, extracted with UTF-8 BOM handling,
and queried with DuckDB. identity_source.json records hash/source; identity_ipeds.csv
contains only UNITID/name/city/state/county/domain for5 candidates (2 applied). No
IPEDS program or completions field is used. Fresh UNITID240453 identifies UWM itself,
not Flex491288. Dedupe CLI searches domain, normalized name, trade names/notes across
all org shards +ecosystem; UNITID uniqueness checked before creating. ROR stays blank
for new institutions, and all existing ROR values remain untouched.

## Holds / owner questions

Every one of94 holds has its own settling fact in holds.csv, plus source-row and attempted
URLs/statuses. A failed route, sparse homepage or search result is not program absence.

| Case | Settling fact / recommendation |
|---|---|
| L13B017 Georgia State | Input ORG004701 points at University of Georgia/uga.edu. Resolve exact institution +named program; do not repoint a held identity from this weak join. |
| L13B020 Macomb | Current named certificate offer; only5/2019 PDF plus generic current apprenticeship page confirmed. No closure inference. |
| L13B022 Ogden-Weber | Named current composites offer/future starts read, but awarded credential/program type not explicit in raw section; obtain catalog award statement. No certificate inferred from staff biography. |
| L13B094 Iowa State / broad-materials seam cases | Current degree page with named polymer track/concentration/research area, or owner seam ruling. Isolated polymer electives not promoted. Recommendation: hold until named track exists; no blanket exclusion of materials programs. |
| Commercial training / multi-provider identities | Establish exact held operator/parent, or owner permission for a suitable institution grain; no new commercial parent under this block. |
| GONE/CLOSED inherited labels | Dated primary operating outcome plus Form5500 gate before any closure REJECT; no such action in this batch. |

UWM admits into at least one future certificate course; other required courses are not
currently scheduled. It is not a guarantee of an immediately completable three-course
sequence. Davis admissions unknown due unavailable HTML; PDF establishes certificate,
not a current intake. Paulson own page invites account setup and explicitly offers
worldwide access. Georgia Tech describes certificate declaration/approval and independent
research projects; no capstone requirement is asserted.

## Named runnable checks

- research.py initial run: PASS3 known positives +fabricated negative before population.
  Initial/followup/final/credential/duplicate fetches JSON record113 routes, with the
  shared Elgin route attributed to both of its leads. Source lookups are discovery,
  not automatic positive verdicts. No registry endpoint/IPEDS program query used.
- `python3 tasks/program-leads-3-2026-11-06/rawcheck.py`: PASS16/16 quotes on6 own pages;
  zero skipped; fabricated quote rejected, including OCR-extracted Davis document.
- `python3 tasks/program-leads-3-2026-11-06/check.py`: PASS exact next100/269 frame,
 100 unique legal verdicts, duplicate targets, evidence coverage, no completions,
 old-row preservation, byte-identical replay, and two injected no-write failures
 (occupied ID drift and same EVD in wrong shard).
- `python3 tasks/program-leads-3-2026-11-06/build.py`: PASS4 programs/2 institutions/
 18 evidence; rerun0 appends. append_sorted used; all collisions checked before writes.
- `python3 scripts/validate.py`: PASS zero errors. Initial V23 failure (fresh NCES
 download marker omitted in evidence notes) fixed in frozen packet, restored main's
 four data files, replayed; no prior/published evidence edited.

No scripts/ files touched; scripts pytest suite not run. The task-specific checks cover
the added fetch/parser/matcher/builder behavior. To update main, merge current main under
the controller recipe; on CSV conflicts take main's four data files and rerun this builder.
Never hand-merge CSVs. Branch base history is the pre-pass backup; this is the pass journal.

## Independent review

Pending Codex3 thr_jukpm97t9c +Grok3 thr_4g4uwqjxjv, under controller06:25 routing.
Draft PR permitted by05:55 override; no completion approval or Done claim until both
families return and findings are fixed/held. Reviewer requests use queue by explicit
controller exception. PR144 remains unchanged on its own branch and independent queue.
