council-ask: codex effort=deep -> model=gpt-6-astra reasoning=max
VERDICT: UNSOUND

FINDINGS:

- **Blocking — `scripts/validate.py`, `v65_key` / V-65 hunk:** A different entity with the same name still inherits the exemption. For example, replace a row-less baselined person with another person having the same `full_name`, retaining `person_id` while replacing their affiliation and identifying details. The baseline key remains identical, so V-65 raises no new error; no row disappears, so `check_row_loss.py` remains silent. The new mutation test covers only replacements whose normalized name changes.
