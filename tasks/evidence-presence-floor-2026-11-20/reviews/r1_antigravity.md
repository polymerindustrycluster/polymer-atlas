council-ask: gemini effort=deep -> model=Gemini 3.8 Flash (High)
**VERDICT: SOUND**

The core validator rule V-65 is correct, the debt-loop ordering is sound, none of the mutation tests are vacuous, and the schema specification is accurate. The rule cannot be refuted on correctness or integrity grounds. However, there are implementation defects in the helper script's reproduction flow, test file resource management, and whitespace handling detailed in the findings below.

---

### FINDINGS

#### 1. Premature guard in `build_baseline.py` breaks documented dry-run reproduction
- **File & Lines:** `tasks/evidence-presence-floor-2026-11-20/build_baseline.py:45-47` (and `tasks/evidence-presence-floor-2026-11-20/README.md:57-58`)
- **Concrete failure scenario:** 
  - **Inputs:** Reviewer or CI runs the dry-run reproduction command documented in `README.md`:  
    `python3 tasks/evidence-presence-floor-2026-11-20/build_baseline.py` (without `--write`).
  - **Wrong outcome:** In `build_baseline.py`, the check `if "V-65" in doc["rules"]:` executes unconditionally at line 45 *before* checking `if "--write" in sys.argv:`. Because V-65 is already committed to `validate_debt_baseline.json` on this branch, line 46 calls `sys.exit("V-65 already baselined; regenerating it needs an owner-approved PR...")` and aborts with exit code 1. `README.md` lines 57–58 claims the unflagged command is a `"dry run: both counts, no write"` and that `--write` is what `"refuses if V-65 is already baselined"`. The guard should be nested inside `if "--write" in sys.argv:` so dry runs can verify counts without failing.
- **Severity:** should-fix

#### 2. Unclosed file descriptors in `test_validate.py` cause file lock hazards on Windows
- **File & Lines:** `scripts/test_validate.py:704-706, 714`
- **Concrete failure scenario:**
  - **Inputs:** Running test suite on Windows (`test_v65_new_record_without_evidence_fails` and `test_v65_baselined_record_gaining_a_row_only_warns`).
  - **Wrong outcome:** 
    - Line 704: `open(p, newline="", encoding="utf-8")` is invoked inside a generator comprehension iterating over `[*self.data.glob("organizations_*.csv"), self.data / "ecosystem.csv"]` without a context manager or explicit `.close()`.
    - Line 714: `open(self.data / "people.csv", newline="", encoding="utf-8")` is similarly opened unclosed inside a `next(...)` generator.
    - On Windows, unclosed file descriptors retain OS-level file locks. If subsequent tests, concurrent runners, or temporary directory cleanup routines (`tearDown` / `shutil.rmtree`) attempt to modify or delete these files, the OS raises `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process`.
- **Severity:** should-fix

#### 3. Unstripped `record_table` in `evidence` set leaves whitespace vulnerability
- **File & Lines:** `scripts/validate.py:606`
- **Concrete failure scenario:**
  - **Inputs:** An evidence shard row has trailing whitespace in `record_table` (e.g., `record_table="organizations "`, `record_id="ORG-000100"`).
  - **Wrong outcome:** `_with_rows` stores `("organizations ", "ORG-000100")` because line 606 strips `r["record_id"]` but does not strip `r["record_table"]`. The loop at lines 607–610 checks `("organizations", "ORG-000100") not in _with_rows`, which evaluates to `True`. The validator erroneously flags the organization as having no evidence row under V-65 despite an evidence row being present. Line 606 should use `(r["record_table"].strip(), r["record_id"].strip())`.
- **Severity:** nit

#### 4. Brittle tier assumption in `test_v65_baselined_record_gaining_a_row_only_warns`
- **File & Lines:** `scripts/test_validate.py:716`
- **Concrete failure scenario:**
  - **Inputs:** The baseline list under `BASELINE["V-65"]` is sorted alphabetically; `next(k ... if k.startswith("people:"))` selects the first baselined person.
  - **Wrong outcome:** Line 716 uses `tier_effect="supports_U" if tier == "U" else "supports_A"`. If the first baselined person's `verification_tier` were ever `B` or `C`, appending an evidence row with `supports_A` would cause V-25 (tier restatement) to fail due to tier mismatch between the record's tier and its evidence rows, causing `test_v65_baselined_record_gaining_a_row_only_warns` to fail with exit code 1 for reasons unrelated to V-65.
- **Severity:** nit

#### 5. Theoretical baseline masking via recycled identifiers
- **File & Lines:** `scripts/validate.py:612` (and `scripts/validate_debt_baseline.json`)
- **Concrete failure scenario:**
  - **Inputs:** A baselined zero-row organization (e.g. `organizations:ORG-000123`) is deleted in an upstream change. A subsequent PR introduces a brand-new organization that reuses the retired ID `ORG-000123` without shipping an evidence row.
  - **Wrong outcome:** `validate.py` calls `debt("V-65", "organizations:ORG-000123", ...)`. Because `organizations:ORG-000123` exists in `DEBT_BASELINE["V-65"]`, the validator issues only a warning rather than failing CI with an error. The zero-row leak occurs undetected for that record. (Mitigated by Atlas's strict monotonic ID allocation rules).
- **Severity:** nit

---

### ADVERSARIAL ANALYSIS ACROSS SPECIFIC CHECKS

1. **Correctness (Shard Layout, IDs, Whitespace, Table Names):**
   - **Table names:** In evidence rows, `record_table` matches `organizations|sites|ecosystem|programs|people`. Both `build_baseline.py` and `audit_evidence_coverage.py` independently produced identical counts across all 5 tables (1340, 1840, 133, 10, 132).
   - **Whitespace:** Both `validate.py:606, 610` and `build_baseline.py:26-27` call `.strip()` on both the evidence row's `record_id` and the entity's ID column (`org_id`, `site_id`, etc.), preventing ID whitespace mismatches.
   - **Ecosystem / Organization overlap:** Ecosystem records share the `ORG-` id space with `organizations`, but their disjoint sets and the `<table>:<id>` key schema in `_with_rows` and `DEBT_BASELINE` prevent cross-table collisions or false matches.

2. **Debt-Loop Ordering:**
   - The V-65 block in `scripts/validate.py` runs at lines 605–614, immediately preceding `DEBT_DETAILS = "--debt-details" in sys.argv` and `for rule in sorted(set(DEBT_FOUND) | set(DEBT_BASELINE)):` (line 616).
   - All `debt("V-65", ...)` calls register before the comparison loop. Unbaselined zero-row records error; baselined records warn; baselined records gaining rows trigger `"V-65: N baselined rows now pass"`.

3. **Baseline Masking:**
   - Because baseline keys are composite strings (`f"{_table}:{rid}"`), collision between `ecosystem:ORG-000100` and `organizations:ORG-000100` is impossible.
   - If an ecosystem record is moved to organizations without an evidence row, it will be flagged as `organizations:ORG-000100` (which is not in the baseline) and will error, preventing leakage.

4. **Test Non-Vacuity:**
   - `test_v65_unbaselined_record_losing_its_only_row_fails`: Deleting the sole evidence row drops the count to 0. Because V-25 restates tiers only where rows exist, V-25 does not fire; only V-65 fires. If V-65 is removed from `validate.py`, the validator exits 0 and `assert_fails_with("... (V-65")` fails.
   - `test_v65_new_record_without_evidence_fails`: Creates a new record with `top + 1`. If V-65 is deleted, no rule emits `has no evidence row`, causing the test to fail.
   - `test_v65_baselined_record_gaining_a_row_only_warns`: If V-65 is deleted from `validate.py`, `DEBT_FOUND["V-65"]` is empty, so all 3,455 baselined keys appear to pass, outputting `"V-65: 3455 baselined rows now pass"`. The assertion for `"V-65: 1 baselined rows now pass"` fails.
   - **Conclusion:** None of the tests are vacuous.

5. **Side Effects & Workflow:**
   - In-flight PRs adding evidence rows to baselined records emit only informational warnings ("now pass") and pass validation with exit code 0.
   - Only PRs attempting to create new entities without evidence rows are blocked, which satisfies the explicit mandate of owner ruling 2026-11-20.
