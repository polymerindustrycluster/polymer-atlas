# Review: Polymer Atlas validator V-68, reconciled with main's V-65 (round 5)

You reviewed this presence-floor rule before, when it was numbered V-65 and covered all tiers. Codex found three
grandfathering holes, all fixed with an identity fingerprint, and Antigravity rated it SOUND. The owner ruled "merge as
is" on Codex's round-4 scope finding. Do not re-litigate that finding.

**New since then.** Main merged SCHEMA v1.17 (#429) with its own **V-65 "no naked tier-A/B"**: a live tier-A record
needs at least one supporting row at supports_A, and a tier-B record one at supports_B or stronger.
- Zero-row records count as naked.
- Tombstones (organizations/ecosystem `status=merged`, programs `status=tombstoned`) are exempt.
- 2,747 records are grandfathered under plain-id keys.

New records are created at tier U or C (AGENTS.md §3 step 6), so main's V-65 alone doesn't stop a create with no
evidence row.

This PR is therefore renumbered **V-68** and scoped to records whose `verification_tier` is C or U (tombstones included).
- Each key is `<table>:<id>:<identity fingerprint>`, with identity-field sets per table as before.
- The baseline, regenerated on main d984d73e, holds 858 keys (organizations 182, sites 613, ecosystem 52, people 10,
  programs 1), reconciled table by table with audit_evidence_coverage.py tiers C+U.

**Observed.**
- `validate.py` exits 0 with "V-65: 2747 / V-67: 185 / V-68: 858 baselined rows still violate" and no errors.
- 12 tests pass: the 5 `test_v68_*` tests plus main's V-65, V-66, V-67 and v110 tests.

**Judge only the reconciliation.**
- Do V-65 and V-68 together cover every live record at every tier?
- Can a record fall between them, for example a tier change, a blank tier, or a tombstone?
- Does anything double-report?
- Are the tests sound under the new scope, including V-66's archive requirement for the synthetic EVD-999999 row?

Return VERDICT: SOUND or UNSOUND, then FINDINGS (file/hunk, concrete failure scenario, severity). No generic advice.

## Diff vs main (validate.py, test_validate.py, build_baseline.py)
