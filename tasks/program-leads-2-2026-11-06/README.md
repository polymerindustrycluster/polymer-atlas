# L13 national named-program leads — batch 1

Integrator delegation: controller thr_9i2c6byhcz, lane atlas-L13-program-leads.
Branch `agent/codex/program-leads-2`; pre-pass backup is branch base history.
First user: Atlas/PIC program-introduction researcher. Non-use finding date: 2026-12-06;
controller owns task status and usage follow-up.

## Scope and acceptance

Fixed input: 6 explicitly selected non-OH/PA named-program leads at already-held institutions
from `tasks/program-leads-2026-11-03/worklist.csv` (input.csv). This is a purposeful batch,
not a random sample or national prevalence estimate. Every selected lead must have exactly
one legal verdict, with raw own-page quote verification, duplicate chains ending in held
records, and existence/scope evidence for every new program. Apply only owned files through
an idempotent builder, with reserved IDs and V-8..V-16 validation. No IPEDS proposal is
program evidence. No organization or registry identifier is created.

## Results (unit: input leads)

6 worked pending leads = 1 VERIFIED + 4 DUPLICATE_OF + 1 STILL_UNCERTAIN; 0 REJECT.
Verified yield: **1/6 worked pending leads = 16.7%**, beside the prior OH/PA applied-program
comparison **4/49 leads = 8.2%** requested by the lane brief. Prior numerator is applied
program rows, whereas this batch's numerator is VERIFIED leads; this batch happens to
map one-to-one. No statistical improvement claim follows from these selected batches.

- Programs: +1 Tier A row, PROG-000300 (Plastics Engineering Seminars, UMass Lowell).
- Institutions: 0 created; no institution tier changes. ORG-002846 rollup name updated;
  its lead URL remains unchanged.
- Evidence: +2 program rows EVD-285000–285001, +1 ecosystem scope row EVD-285002.
- No inclusion-log changes: direct §4.11(a) named plastics training, no seam ruling.
- GRCC's certificate is already within PROG-000004 (aas_associate;certificate), and
  Southern Mississippi's BS already within PROG-000060 (bs;ms;phd). Do not split those
  consolidated held records in this pass. WWU explicitly calls Polymer Materials
  Engineering the former name of held PROG-000081.

## Holds

| Lead | Verdict | Settling fact / recommendation |
|---|---|---|
| L13-001 Ferris Plastics Institute | STILL_UNCERTAIN | Own live page lists only May 20–22, 2025 workshop dates. Obtain a current/forthcoming offering or direct institutional confirmation before asserting current training availability. No closure or rejection inferred. |

UMass Lowell publishes a Summer 2026 schedule and describes the standing seminars offer.
`admissions_status=unknown`: no future intake is established as of 2026-11-06. This is not
an enrollment guarantee. The new program is the named seminars offer, not one row per course.

## Provenance and checks

Only the institutions' own program pages are used, listed in verdicts.csv and calibration.csv. Every quote was
re-fetched with curl/browser UA and checked as ordered words on 2026-11-06. The house
normalizer is reused from evidence-repair-2/prep.py; raw HTML is not shipped (it includes
unneeded staff contacts). rawcheck.csv records URL/date/SHA-256 and the exact quote.

`dedupe.json` preserves `scripts/atlas.py dedupe-check --domain ... --name ... --json`
results across organization shards and ecosystem. UNITID/ROR are unchanged; no API ROR
claim is made. All duplicate targets exist directly in programs.csv (no unresolved chain).

Named checks:

- `python3 tasks/program-leads-2-2026-11-06/rawcheck.py`: PASS, 10/10 source quotes (6 pending + 4 calibration),
  0 skipped. First three checks are known held programs Pittsburg, Stout and Winona;
  all match, and a fabricated quote is rejected on all 10 pages.
- `python3 tasks/program-leads-2-2026-11-06/check.py`: PASS, input/verdict/raw yield,
  duplicate targets, evidence coverage, preservation of prior rows, byte-identical replay,
  and deliberate reserved-ID collision rejected.
- `python3 tasks/program-leads-2-2026-11-06/build.py`: PASS, applies packet and generates
  the §4.11 institution rollup from all current linked programs.
- `python3 scripts/validate.py`: PASS, zero errors (baseline and applied tree).

No scripts/ files changed; the scripts pytest suite was not run. The task-local check
covers the new builder and replay failure mode.

## Rebase/rebuild

Restore main's four owned data files, then run build.py and check.py followed by validate.py.
The packet has fixed IDs: collisions or changes to an existing packet row fail closed.
Evidence appends use scripts/shard_io.append_sorted; existing evidence is never edited.

## Review journal

Controller's 2026-11-06 05:55 BOARD ruling supersedes the original council-only gate:
assigned Codex/Grok refute clerks may review the draft PR. Queue-mode messages are explicitly
authorized for these clerk requests only. council-doctor passed, but no deep council call
was launched because the controller reported fleet saturation. Independent verdicts pending.

Frame reconciliation: worklist.csv has 353 rows. Non-OH/PA rows number 294,
of which 19 are already held_same_name=True and **275 are pending (False)**.
An initial 10-row selection included 4 already-held positives; they are now
separate calibration_input.csv/calibration.csv and excluded from worked/yield.
The 6 pending input leads are within the requested 275-lead frame; **269 pending
leads remain unworked**, plus the 147 completions proposals. This correction
supersedes the initial controller message reporting 10 worked/8 duplicates.

## Not worked

This batch does not claim the rest of the national worklist or the 147 unapplied completions
proposals as worked. No IPEDS completions/CIP fields were applied. Wider state/name variants
in the input are retained unchanged; no national denominator inferred from them. The
Mac's data-estate catalogue search reported Windows-only inventory gaps; the supplied
committed worklist and fresh public institution pages suffice for this batch.
