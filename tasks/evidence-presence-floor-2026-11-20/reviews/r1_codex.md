council-ask: codex effort=deep -> model=gpt-6-astra reasoning=max
VERDICT: UNSOUND

1. **scripts/validate.py — V-65 baseline key construction. Severity: blocking.**  
   Same-table ID reuse inherits grandfathering. Take a baselined `organizations:X`, delete the original record while retaining its baseline entry, then create a different organization using `X`, without evidence. V-65 emits the same baselined key and only warns; it does not reject the new record. `<table>:<id>` prevents cross-table collisions, but cannot distinguish successive records using the same key. No enforced prohibition on ID reuse is supplied. The unconditional “a create with no row … fails” claim therefore exceeds what this rule establishes.

2. **scripts/test_validate.py — `test_v65_baselined_record_gaining_a_row_only_warns`, final assertion. Severity: should-fix.**  
   Merge the documented PR #427 while retaining its 16 now-satisfied baseline entries, which the debt mechanism permits. This test then expects `"V-65: 1 baselined rows now pass"`, but the count becomes **16 or 17**, depending on whether its selected person was among those backfilled. Valid backfill therefore breaks the test.

   This is brittleness, not vacuity: deleting V-65 would remove the two negative tests’ required diagnostics and make all 3,455 baseline entries “now pass,” failing the third test’s count assertion.

3. **tasks/evidence-presence-floor-2026-11-20/build_baseline.py — existing-V-65 guard before `if "--write"`. Severity: nit.**  
   Run the README’s no-argument reproduction command on this branch. It prints both counts, then exits unsuccessfully with “regenerating it needs an owner-approved PR,” despite requesting no write. The unconditional guard makes the documented dry run report a regeneration failure on the checked-in baseline.
