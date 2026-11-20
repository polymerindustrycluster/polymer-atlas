# Final review: Polymer Atlas validator rule V-65 (presence floor), round 3

Earlier rounds (Codex, blocking):
1. A new record reusing a baselined id inherits the exemption.
2. A baselined id overwritten in place with a different entity: no row is removed, so check_row_loss.py is silent.
3. A different entity with the SAME name overwritten under the same id (for example, a person of the same full_name at
   another institution).

**Current design.** Baseline keys are `<record_table>:<record_id>:<identity fingerprint>`. The fingerprint is
`sha1("|".join(re.sub('[^a-z0-9]+','',v.lower()) for v in identity_fields))[:8]`. The identity fields follow the
Atlas's own dedupe tests (AGENTS.md §3: website domain, normalized name, street address, operator rule):
- organizations: legal_name, hq_city, hq_state;
- ecosystem: legal_name, city, state;
- sites: org_id (operator), site_name, street_address, city, state;
- programs: institution_org_id, program_name;
- people: full_name, institution_org_id.

A baselined row-less record whose identity fields change (renamed, moved, re-pointed, repurposed) gets a key that isn't
in the baseline, so V-65 errors. The schema's lane-brief contract already requires evidence rows for any record a lane
creates OR changes, so requiring a row for an identity change is consistent.

**Residual, and why it stays.** An id overwritten with an entity that matches on every identity field is, by the Atlas's
own dedupe tests, the same entity. Hashing the whole row would close even that, but automated derivation passes touch
grandfathered rows without new claims: tier1_qualifier re-derivation (AGENTS.md §1: derived, hands-off), county and ZIP
reference fills, geocodes. Each would then fail V-65 for thousands of records.

Please judge whether the residual is acceptable for a guard whose job is to stop zero-evidence creates and changes by
contributor lanes.

**Observed.**
- After regeneration, `validate.py` exits 0 with "V-65: 3455 baselined rows still violate" and 0 new V-65 errors, so
  build_baseline.py's keys equal validate.py's.
- Counts are reconciled table by table with `scripts/audit_evidence_coverage.py`.
- The 5 V-65 tests pass:
  - unbaselined record loses its only row;
  - new record with no row;
  - baselined record gains a row;
  - repurposed in place (renamed);
  - same-name person moved to another institution.
- The first three were verified to fail with the rule disabled.

Return VERDICT: SOUND or UNSOUND, then any remaining FINDINGS (file/hunk, concrete failure scenario, severity:
blocking, should-fix or nit). No generic advice.

## Baseline sample
