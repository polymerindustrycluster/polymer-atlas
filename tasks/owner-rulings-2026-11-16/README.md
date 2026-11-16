# Owner rulings, 2026-11-16

The repo owner ruled in session on 2026-11-16, as multiple choice (AGENTS.md §2 rule 9).

## R-AFFOA: is AFFOA a polymer program? (blind audit 10, record A10-003)

Blind audit 10 found that no page of AFFOA (Advanced Functional Fabrics of America, ORG-013503) states a polymer
program; the `polymer_program=true` flag was inferred because advanced fibers are polymer-based. The audit held it
for the owner.

- **Ruled (a):** clear the flag. Keep the record; set `polymer_program` back to blank until one of AFFOA's own pages
  states a polymer or fiber-polymer program.
- (b) Keep it as true by subject matter. Not chosen.

**Applied here:** ORG-013503 `polymer_program` `true` → blank (1 cell in `data/ecosystem.csv`; builder `build.py`,
idempotent). `polymer_program_name` and `polymer_program_url` are the generated §4.11 rollup of the institution's
program row and are unchanged (validator V-16 requires them while a program row exists).

## R-AFFOA-PROGRAM: the AFFOA program row

The program row PROG-000329 (the institute itself, type `center`) rests on the same inference.

- **Ruled (a), 2026-11-16:** tombstone it. It stops counting as a polymer program and can be restored if an AFFOA
  page later states polymer fiber work.
- (b) Keep the row active. Not chosen.

**Applied:** PROG-000329 `status` `active` → `tombstoned`, with a dated note (1 row in `data/programs.csv`; nothing
deleted; its 2 evidence rows stay). No person is linked to it. Validation passes: with no active program row, the
institution carries no program claim.

## R-GEO-ZIP and R-SAM (recorded here; applied in their own pull requests)

- **R-GEO-ZIP:** a ZIP from a unique Exact Census batch match may fill a blank ZIP as reference data; an existing ZIP
  is never overwritten. Applied in the Census ZIP pull request with SCHEMA v1.13.2.
- **R-SAM:** SAM.gov is used "filtered, leads only": drop every record marked as D&B-sourced or last updated before
  2022-04-04; use the rest only as discovery leads and for government-issued UEI links; copy no name or address
  from SAM into the Atlas.

## R-REVIEW-FAMILY: the second review family

Grok can no longer review (usage balance exhausted, 2026-11-14). Ruled: **Gemini is the standing second family;
if Gemini is unavailable, a Claude Opus reviewer may stand in on pull requests that Codex wrote.** Codex always
reviews. Recorded in `DECISIONS.md`.
