council-ask: gemini effort=deep -> model=Gemini 3.8 Flash (High)
VERDICT: SOUND

### FINDINGS
None. The reconciliation between main's V-65 and PR V-68 is airtight across all four criteria:

---

### Detailed Analysis of the Reconciliation

#### 1. Coverage of Live Records Across All Tiers
- **Tier A & Tier B**: Covered by main's **V-65** ("no naked tier-A/B"). Every live tier-A record requires at least one supporting row at `supports_A`, and every live tier-B record requires at least one supporting row at `supports_B` or stronger. Zero-row records count as naked.
- **Tier C & Tier U**: Covered by **V-68** (SCHEMA §4.13 presence floor). Every record across all five entity tables (`organizations`, `sites`, `ecosystem`, `programs`, `people`) whose `verification_tier` is `C` or `U` must carry at least one row in `data/evidence_*.csv`.
- Together, the partition $\{A, B\} \cup \{C, U\}$ covers every valid verification tier defined in the schema across all entity tables. Every live record at every tier is subject to an evidence floor.

#### 2. Gap and Leak Analysis (Tier Changes, Blank Tiers, Tombstones)
- **Tier Changes**:
  - **Promotion ($C/U \to A/B$)**: If a row-less record baselined under V-68 is promoted to tier A or B, its new tier takes it outside V-68's check (`verification_tier in ("C", "U")`), but places it directly into V-65. Because V-65's adoption baseline was frozen at 2,747 plain-ID keys on main, the promoted record is unbaselined in V-65 and immediately fails as a new violation.
  - **Demotion ($A/B \to C/U$)**: If a row-less record baselined under V-65 is demoted to tier C or U, it exits V-65 and enters V-68. Because V-68's baseline was generated strictly from records that were tier C or U on adoption day (858 keys), the demoted record is unbaselined in V-68 and immediately fails as a new violation.
  - **Intra-tier switch ($C \leftrightarrow U$)**: Both tiers are evaluated identically by V-68 (presence of $\ge 1$ evidence row). Furthermore, `v68_key` computes its fingerprint over entity identity fields (`legal_name`, locations, institutions) rather than `verification_tier`. Thus, a baselined record transitioning between C and U retains the exact same baseline key and does not spuriously drop out or leak.
- **Blank Tier**:
  - A blank or whitespace `verification_tier` evaluates to false under both V-65 (`tier in ("A", "B")`) and V-68 (`tier in ("C", "U")`). However, `verification_tier` is a mandatory schema enum field. Records with missing or blank tiers fail schema validation at the gate; when assigned any valid tier pursuant to AGENTS.md §3 step 6, they are immediately captured by V-68 (if created at C/U) or V-65 (if created at A/B).
- **Tombstones**:
  - Main's V-65 explicitly exempts tombstones (`status=merged` for organizations/ecosystem; `status=tombstoned` for programs) because inactive historical entities at tier A/B do not require ongoing active claim support.
  - V-68 scopes to tier C/U with tombstones included (pre-existing tier C/U tombstones without evidence rows are grandfathered in V-68's 858 baseline keys). An unbaselined tier C/U entity cannot bypass V-68 by tombstoning itself without evidence; nor can it evade evidence checks by transitioning to tier A/B, as that triggers V-65's unbaselined verification requirement.

#### 3. Double-Reporting
- **No Overlap**: V-65 applies strictly to `verification_tier in ("A", "B")`, while V-68 applies strictly to `(r.get("verification_tier") or "").strip() in ("C", "U")`. Because a record's `verification_tier` cannot simultaneously be in both sets, no record can violate both rules.
- **Cross-Table Namespace Isolation**: In V-68, `_with_rows` indexes `(record_table, record_id)` pairs, and `v68_key` prefixes each key with `<table>:<id>:<fingerprint>`. Even though `organizations` and `ecosystem` share the `ORG-` ID space, they are partitioned by table name in both matching and debt reporting, preventing cross-table collisions or duplicate reports.

#### 4. Soundness of Unit Tests
- `test_v68_unbaselined_record_losing_its_only_row_fails`: Targets a single-evidence C/U organization where the evidence ID is not archived, ensuring that deleting the row tests V-68 cleanly without tripping collateral V-66 dangling archive link failures.
- `test_v68_new_record_without_evidence_fails`: Creates an unevidenced tier-C record above the shared `ORG-` ID ceiling, confirming new unbaselined creations are blocked.
- `test_v68_baselined_record_gaining_a_row_only_warns`: Correctly adds both an evidence row with a matching tier effect and an archive link row in `archive_links.csv` for synthetic `EVD-999999`. Because `EVD-999999` exceeds the ID threshold where V-66 mandates archive-at-capture, providing this companion link properly satisfies V-66 while asserting that V-68 debt shrinks cleanly.
- `test_v68_baselined_record_repurposed_in_place_fails` & `test_v68_baselined_person_same_name_other_institution_fails`: Confirm that in-place repurposing or entity moves change the identity fingerprint, removing the entity from the baseline and producing a new violation.
