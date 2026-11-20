council-ask: codex effort=deep -> model=gpt-6-astra reasoning=max
VERDICT: UNSOUND

FINDINGS:

- **High — [scripts/validate.py:698](C:/Users/JohnSwanson/Documents/pic-github/_wt/atlas-evdleak/scripts/validate.py:698), V-68 tier predicate:** Blank or invalid ecosystem tiers bypass both floors. V-65 checks only A/B; V-68 checks only C/U; ecosystem lacks the tier-enum validation present for the other four tables. Reproduced with a new active ecosystem record, `ORG-013802`, without evidence: tier `C` produces a V-68 error, but `""`, whitespace, and `"X"` each produce **exit 0**. The new tests do not exercise this boundary.

For valid tiers, transitions correctly switch enforcement between the rules without double-reporting. A/B tombstones remain exempt; C/U tombstones remain covered, as specified. The 858-key baseline reconciles exactly.

All 17 relevant tests pass. The synthetic `EVD-999999` archive link matches its source URL and satisfies V-66/V-59.
