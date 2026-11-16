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

**Not decided, held:** the program row PROG-000329 (the institute itself, type `center`) still stands under
ORG-013503. Whether it stays is the same scope question at program grain and was not put to the owner; it is not
changed here.

## R-REVIEW-FAMILY: the second review family

Grok can no longer review (usage balance exhausted, 2026-11-14). Ruled: **Gemini is the standing second family;
if Gemini is unavailable, a Claude Opus reviewer may stand in on pull requests that Codex wrote.** Codex always
reviews. Recorded in `DECISIONS.md`.
