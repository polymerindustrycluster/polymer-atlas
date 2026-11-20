council-ask: gemini effort=deep -> model=Gemini 3.8 Flash (High)
### Judgment on the Residual

The residual is **acceptable** for the validator's stated role (stopping zero-evidence creates and changes by contributor lanes):

1. **Alignment with Atlas deduplication semantics:** By the Atlas's own AGENTS.md §3 deduplication criteria, an entity matching on every identity field (`legal_name` + location for organizations/ecosystem; operator + site name + address for sites; institution + program/person name for programs/people) is the same entity. An overwrite matching all identity fields is functionally an attribute update to the same entity, not a repurposing.
2. **Operational necessity for automated pipeline passes:** Full-row hashing would cause severe fragility. Automated derivation passes (`tier1_qualifier` re-derivation per AGENTS.md §1, county/ZIP reference fills, geocoding coordinates) modify grandfathered rows without introducing new evidence claims. A full-row hash would invalidate baseline keys for thousands of untouched entities, breaking routine data maintenance.
3. **Threat model coverage:** A contributor lane repurposing or reusing an ID for a genuinely distinct entity will inevitably alter the legal name, site address, or parent institution/operator, which changes the 8-character SHA-1 fingerprint and trips V-65.

---

### VERDICT: SOUND

The design and implementation across `validate.py`, `test_validate.py`, and `build_baseline.py` cleanly resolve the earlier Codex blocking issues (reusing baselined IDs, in-place repurposing, and same-name entities across different institutions). The key format `<record_table>:<record_id>:<identity fingerprint>` correctly isolates shared ID spaces (such as `ORG-` between organizations and ecosystem) and enforces the presence floor contract.

---

### FINDINGS

#### 1. `scripts/validate.py` (line 608)
- **Hunk:**
  ```python
  import hashlib
  V65_TABLES = (("organizations", orgs, "org_id", ("legal_name", "hq_city", "hq_state")),
  ```
- **Scenario:** `import hashlib` is placed inline inside the rule block rather than at the top of the file with the other standard library imports (`import csv, json, os, re, sys` at line 32). While valid in Python, it deviates from the module structure.
- **Severity:** Nit

#### 2. `scripts/test_validate.py` (lines 685–688)
- **Hunk:**
  ```python
  @staticmethod
  def _v65_ids(table):
      """Record ids baselined under V-65 for one table (keys are <table>:<id>:<name fingerprint>)."""
      return [k.split(":")[1] for k in sorted(BASELINE.get("V-65", [])) if k.startswith(f"{table}:")]
  ```
- **Scenario:** The docstring states `(keys are <table>:<id>:<name fingerprint>)`. Following round 3, the key incorporates the composite identity fields (including location and parent org/institution), making it an identity fingerprint rather than just a name fingerprint.
- **Severity:** Nit

#### 3. `scripts/validate.py` (line 616) & `tasks/.../build_baseline.py` (line 25)
- **Hunk:**
  ```python
  def v65_key(table, rid, values):
      ident = "|".join(re.sub(r"[^a-z0-9]+", "", (v or "").lower()) for v in values)
      return f"{table}:{rid}:{hashlib.sha1(ident.encode()).hexdigest()[:8]}"
  ```
- **Scenario:** `re.sub(r"[^a-z0-9]+", "", (v or "").lower())` strips all non-ASCII characters without prior unicode decomposition (e.g., `"Société"` normalizes to `"socit"` instead of `"societe"`). While internal consistency between `build_baseline.py` and `validate.py` prevents false positives, two distinct names differing only in accented letters (e.g., `"Müller"` -> `"mller"` vs `"Muller"` -> `"muller"`) normalize differently, whereas a name change dropping an accent (e.g., `"Société"` -> `"Societe"`) is treated as an identity change requiring evidence.
- **Severity:** Nit
