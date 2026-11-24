PASS 15 expected cells. All data files compared.
wrong value rejected: [] mismatched cells [('plant.csv', 'A', 'value')]
omission rejected: [] mismatched cells [('plant.csv', 'A', 'value')]
overwrite rejected: [] mismatched cells [('plant.csv', 'B', 'value')]
truncated row rejected: plant.csv line 3: expected 3 cells, found 2

## Round 3 fix (Codex r2 finding at 913f0272)

The quote reader now matches the `quote:` label in any letter case. A code that appears in claim_detail outside a parsed quote (a standalone quotation, an unlabelled line) holds the row; it is never inferred. build.py `located()` and check.py `quoted()` carry known-answer cases: lower-case label, capitalised label, standalone quotation (hold), absent code, and a longer number containing the six digits (no match).
Rerun on the pinned base: the builder yields the same 15 cells, all `researcher_inferred`; `check.py` PASS 15 expected cells, with the four plants rejected; `validate.py` OK. data/ is unchanged from 913f0272.
