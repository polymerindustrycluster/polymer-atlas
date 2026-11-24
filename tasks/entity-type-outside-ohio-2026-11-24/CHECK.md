PASS 666 expected cells. All data files compared.
wrong value rejected: [] mismatched cells [('plant.csv', 'A', 'value')]
omission rejected: [] mismatched cells [('plant.csv', 'A', 'value')]
overwrite rejected: [] mismatched cells [('plant.csv', 'B', 'value')]
truncated row rejected: plant.csv line 3: expected 3 cells, found 2

## Replay onto main after #539 and #540 (controller)

Normal merge of origin/main (27fae8f2) into the branch, with no conflicts; BASE_REF refreshed to 27fae8f2. `check.py`: PASS 666 expected cells, the four plants rejected, and CLAIMS_CHECKED.csv lists exactly the 666 changed cells (verdict `corrected`; the controller's harness counts this folder as fills). `validate.py` OK. The data delta's sorted +/- lines are identical to the delta of head 0edaca6b against 4aba1b1 (sha 4c0866c08b4009da both). Unit: organizations rows with a US HQ outside Ohio, blank or `unknown` entity_type, filled by the unchanged 2026-11-22 rules.py.
