# Audit record for G8a settlement

Label: p1-pic18-settle-2026-11-23
Result: PASS
Sample: census of all 270 checked claims, 34 changed cells, eight new evidence rows, two archive links and one inclusion-log entry in PR #521.
Reviewers: Codex GPT-6.2 Astra and Claude Sonnet 5.5 approved exact head eacdab91fc1aa9aa1f84c96eb6169a5a656024ca. Gemini 4 Hydrogen independently read both archived proof witnesses before admission.

Both reviewers reconciled the canonical diff, claims and tier history.
Astra verified the three original FRS links and the Pittsburgh Paints
scope entry after correction. Sonnet independently replayed both
archive bodies and the six structured witnesses and recomputed the
794-to-792 eligible-owner census. The frame check reported zero
unassignable records and one named exclusion. No audit sample was drawn.

The merged commit cd994c68042b6c1c1c65cc5af88ec416dd4ba7dd matches the
reviewed head under data/ and this task folder.
