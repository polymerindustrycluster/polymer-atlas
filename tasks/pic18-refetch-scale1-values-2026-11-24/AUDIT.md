# Audit record for the refetch scale-1 value fills (#559)

Label: claude-code pic18-refetch-scale1-values-2026-11-24
Result: PASS
Sample: the six evidence rows EVD-483137 to EVD-483142 on four owners (the whole batch as `main` holds it under this label; the merge commit's title says eight values on five owners, which `main` does not show)
Reviewers: GPT-6.2 Astra at 25f6241c (PR comment 7146240242) and Gemini 4 Hydrogen at c20b15ef (PR comment 7146065411)

Added by the next data PR, `tasks/hq-blank-city-2026-11-25/`, as AGENTS section 2a rule 5 allows. It cites the review records on #559; it is not a fresh audit. `git diff 529b86dd 25f6241c -- data/` is empty and so is `git diff 529b86dd` against the final PR head, and the only change between Gemini's approval (`c20b15ef`) and GPT's (`25f6241c`) is `check.py` and its README line. The merged head `a14f7aed` is `25f6241c` plus a merge of main. Gemini's approval is therefore not at the exact final head. The controller may replace this file with a different audit.
