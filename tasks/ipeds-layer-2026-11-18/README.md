# IPEDS completions layer: polymer-programs-db moves into the Atlas (2026-11-18)

**Owner ruling, 2026-11-18.** Asked where the public copy of polymer-programs-db should go, the owner answered **"Into
the Atlas"**. This pass is phase 1 of that move: the federal IPEDS layer.

## Acceptance criteria (written before the build)

1. **Three new tables in `data/`:** `ipeds_institutions.csv`, `ipeds_programs.csv` and `ipeds_completions.csv`.
   `scripts/ipeds_build.py` generates them from `data/ipeds/raw_ipeds_national.json`. They are never hand-edited.
2. **Counts match programs-db.** For IPEDS rows only, they equal polymer-programs-db's build at a9d89b5:
   - 343 institutions, 825 programs and 10,486 program-years.
   - Polymer completions: 1991 476, 2007 379, 2016 970, 2023 617.
   - Sustained programs: 35 institutions, 27 of them with completions in 2023.
3. **Validator rule V-63** checks:
   - the field sets;
   - key uniqueness;
   - that every program resolves to an institution and every completion row to a program;
   - **parity**: re-deriving from the raw file must reproduce all three tables exactly.

   A hand edit to any table must fail `validate.py`, and a mutation test shows it does.
4. **Year-label refusals.** `scripts/test_ipeds_year_labels.py` runs in CI's unittest discovery. Every wrong year map is
   still refused.
5. **SQLite build.** `scripts/build_sqlite.py` loads the three tables.
6. **SCHEMA v1.14 §4.23** documents the layer:
   - it is reference data: never evidence, never a tier input, never edited by hand;
   - years follow the fall-label convention;
   - the caveat that goes with any quoted count;
   - the owner ruling.
7. **`docs/IPEDS.md`** carries the public reading guide and the corrections log.
8. **No personal data.** No person, faculty-count, vault or conference layer comes across, and the leak scan is clean.
9. **Clean checks.** `validate.py` exits 0 on the committed tree, and the row-loss guard passes; the change only adds
   rows.

## Out of scope (phase 2, each an owner question)

- **Hand-researched layers** in polymer-programs-db: US non-degree credentials (29), global programs (101), society
  chapters (364) and program aliases (36). Each needs its own table, or rows in an existing one, under the evidence
  contract.
- **CIP-invisible programs** (`hand_additions.tsv`: University of Chicago PME and Dartmouth Thayer). These are
  program records, so they belong in `data/programs.csv` with evidence rows, not in a federal reference table.
- **College Scorecard** field-of-study data.
- **Never moving:** the faculty-census counts, the vault layer and the conference-participation layer. They stay in
  the private repository for the reasons given in its `PUBLIC_VERDICTS.md`.
