council-ask: gemini effort=deep -> model=Gemini 3.8 Flash (High)
VERDICT: SOUND

### Analysis & Review of Changes

The blocking vulnerability identified in the previous review—where a row-less grandfathered record could be repurposed or replaced in place under the same ID because the exemption key was merely `<table>:<id>`—has been properly resolved. The new composite key format `<record_table>:<record_id>:<name fingerprint>` binds the exemption to the identity of the specific entity present at adoption time.

---

### Evaluation of Key Areas

#### 1. In-Place Repurposing & Rename Detection
- **Mechanism:** `v65_key` derives an 8-character hex prefix from `sha1(re.sub(r'[^a-z0-9]+', '', (name or '').lower()).encode())`.
- **Result:** Overwriting a baselined record with a different legal/site/program/person entity alters the fingerprint. The resulting key is absent from `scripts/validate_debt_baseline.json`, causing `validate.py` to correctly flag the record under V-65 as a new violation rather than an exempted debt.
- **Contract Alignment:** Under the repository's lane-brief contract, any lane modifying an entity is required to supply evidence rows. If the lane supplies an evidence row, `(_table, rid) in _with_rows` evaluates to `True`, bypassing the presence-floor check entirely and retiring the grandfathered debt (`baselined rows now pass`).

#### 2. False Errors from Normalization
- **Behavior:** The regex `[^a-z0-9]+` strips all whitespace, punctuation, and formatting symbols after lowercasing the string.
- **Impact:** Harmless edits such as casing changes (e.g., `Acme Corp` vs. `ACME CORP`), punctuation adjustments (e.g., `Acme, Inc.` vs. `Acme Inc.`), or whitespace normalization produce identical fingerprints. Legitimate cosmetic cleanup on baselined records will not drop the baseline exemption or trigger false V-65 violations.

#### 3. Blank or Missing Names
- **Handling:** `(name or '')` guarantees that `None` or absent dictionary values fall back to an empty string `""`.
- **Hash Stability:** An empty string reliably produces SHA-1 prefix `da39a3ee` in both `build_baseline.py` and `validate.py`.
- **Uniqueness:** Because each key incorporates `<record_table>:<record_id>:`, distinct records with empty names do not collide with one another. If a blank name is later populated by a lane without adding evidence, the changed fingerprint triggers V-65 as expected (a modified record requires evidence).

#### 4. Shared ID Spaces Across Different Tables
- **Namespace Isolation:** The key format explicitly prefixes `<record_table>:`. Even though `ecosystem` and `organizations` share the `ORG-` identifier space, an ecosystem entity `ecosystem:ORG-000089:...` and an organization entity `organizations:ORG-000089:...` resolve to distinct keys.
- **Evidence Union Isolation:** In `validate.py`, `_with_rows` is indexed as `(record_table, record_id)` pairs. Evidence associated with `organizations` will not inadvertently satisfy or mask an `ecosystem` record with the same ID, and vice versa.

#### 5. Legitimate Lane Workflows
- **New Records:** Any new entity added without evidence fails V-65 (verified by `test_v65_new_record_without_evidence_fails`).
- **Gaining Evidence:** When a lane attaches an evidence row to a baselined entity, `(_table, rid)` enters `_with_rows`. The rule is satisfied, no debt is logged, and the validator outputs debt retirement (`baselined rows now pass`) while exiting 0 (verified by `test_v65_baselined_record_gaining_a_row_only_warns`).
- **Losing Evidence:** When an unbaselined entity loses its sole supporting row, V-65 fails with a new violation (verified by `test_v65_unbaselined_record_losing_its_only_row_fails`).

#### 6. End-to-End Baseline Parity
- `build_baseline.py` and `validate.py` share identical `v65_key` definitions and column mappings across all five tables (`organizations`, `sites`, `ecosystem`, `programs`, `people`).
- Baseline regeneration reconciles exactly (3,455 records) with the independent `scripts/audit_evidence_coverage.py` breakdown by table, and `validate.py` runs clean with 0 new errors against the updated baseline.

---

### Remaining Findings
None. The implementation is sound, self-consistent, and robust against in-place overwrites while preventing false positives on legitimate formatting normalizations.
