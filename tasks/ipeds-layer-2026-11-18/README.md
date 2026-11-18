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

## Result

All nine criteria hold.

- **Equality with programs-db.** Every one of the 825 programs and 10,486 completion rows equals the programs-db build,
  compared per row: first and last year, years seen, total awards, status, level and awards per year. The polymer
  series and the 35 / 27 figure are unchanged.
- **One deliberate difference: certificate labels (124 programs).** Each canonical certificate level now carries one
  label naming the codes merged into it, for example "Cert under 1yr (codes 1, 30, 31)". Before, a program took the
  label of whichever raw row came first, so a code-30 "under 12 weeks" program could read "12wk-1yr".

## Review fixes (codex, deep, on 23d9786: UNSOUND, 7 findings, all fixed)

| # | Finding | Fix |
|-|-|-|
| 1 | `ipeds_fetch_nces.py` imported the old module name | Imports `ipeds_fetch` |
| 2 | A failed page or CIP request silently wrote a smaller raw file | `paged()` aborts on a later-page failure; a served year with a failed CIP, or any failed directory request, aborts the refresh with the raw file unchanged (tested) |
| 3 | Parity alone could not catch a program whose institution has no directory entry | The build refuses it (tested) |
| 4 | The row-loss guard keyed completions on `program_key` alone | Composite key (`program_key`, `year`) in `check_row_loss.py` |
| 5 | Certificate code 30 inherited code 31's label | One explicit label per canonical level |
| 6 | V-63 skipped silently when the whole layer was absent | A missing raw file is a V-63 error |
| 7 | "343 institutions conferred an award" | 343 reported; 310 conferred at least one award, and 33 reported only zeros |

## Review fixes (grok, deep, on 7025e74: UNSOUND)

| Finding | Disposition |
|-|-|
| Failures at the series frontier read as "end of series" and could shorten the raw file | Fixed: a pull that ends before the existing raw file is refused |
| A directory backfill miss was still written | Fixed: the fetcher refuses to write while any institution lacks a directory entry |
| The 60-page backstop returned a partial list | Fixed: it aborts |
| V-63 caught only `SystemExit`, so a malformed raw file crashed the validator | Fixed: any derivation error is reported as a V-63 error |
| `closed_after` is a served directory year, not a fall label | Documented in §4.23 as the served Urban directory year |
| Codes 30 and 31 merge although both exist after 2020 | Kept by design: the merge keeps one program continuous across the 2020 re-coding, and the label names the merged codes (§4.23) |
| A CRLF checkout would fail parity | Not reproduced: `.gitattributes` pins `*.csv text eol=lf` |
| `export_release` unit text, the "27 of 35" wording and the changelog order | Fixed |

Not tested: the frontier and backfill refusals run inside the networked `main()` of `ipeds_fetch.py`. The pagination
abort and the orphan refusal are tested.

## Out of scope (phase 2, each an owner question)

- **Hand-researched layers** in polymer-programs-db: US non-degree credentials (29), global programs (101), society
  chapters (364) and program aliases (36). Each needs its own table, or rows in an existing one, under the evidence
  contract.
- **CIP-invisible programs** (`hand_additions.tsv`: University of Chicago PME and Dartmouth Thayer). These are
  program records, so they belong in `data/programs.csv` with evidence rows, not in a federal reference table.
- **College Scorecard** field-of-study data.
- **Never moving:** the faculty-census counts, the vault layer and the conference-participation layer. They stay in
  the private repository for the reasons given in its `PUBLIC_VERDICTS.md`.
