# Evidence presence floor for tier C/U, validator V-68 (2026-11-20)

**Result:** a new validator rule, V-68, fails any tier-C or tier-U organizations, sites, ecosystem, programs or people
record that has no row in `data/evidence_*.csv`. The 858 such records on main `d984d73e` are baselined, so main still
passes. No data row changes.

## Why

On 2026-11-20, 3,455 of the Atlas's records in those five tables had no evidence rows at all
(`scripts/audit_evidence_coverage.py`, main `280e6a8f`). No rule stopped a new one:
- V-25 restates tiers only for records that already have rows.
- The lane-brief contract ("a create integrates only with evidence rows") was enforced by the integrator alone.

The owner ruled 2026-11-20: close the leak with a validator rule, and record today's gaps as backlog ("Close the zero-row
leak").

**Reconciled with v1.17.** While this PR was in review, main merged SCHEMA v1.17 (#429, claimed by `spaghetti`, also
owner-approved 2026-11-20). Its V-65 ("no naked tier-A/B") requires every live tier-A/B record to carry a row at its
own strength, and grandfathers 2,747 records.
- That covers the tier-A/B part of the leak, and more strictly.
- It does not cover tier C/U. AGENTS.md §3 step 6 creates new records at tier **U or C**, so on its own V-65 does not
  stop a create with no evidence row.
- This PR was therefore renumbered from V-65 to **V-68** and scoped to tier C/U, so the two rules together cover every
  live record at every tier without reporting the same record twice. Its baseline went from 3,455 (all tiers) to 858.

## The rule

- **Scope:** every tier-C/U record in `organizations_*.csv`, `sites_*.csv`, `ecosystem.csv`, `programs.csv` and
  `people.csv`, tombstones included.
  - Technically V-68 covers every record whose tier is not A or B, so a blank or invalid tier also falls in.
  - Ecosystem rows have no tier-enum check, and without this such a record would escape both V-65 and V-68 (Codex,
    round 5).
  - No record has such a tier today, so the baseline is unchanged.
- **What counts:** a row in a `data/evidence_*.csv` shard whose `record_table` and `record_id` name the record, at any
  strength. Archive links (§4.22) and registry links (§4.8) don't count.
- **Baseline:** the existing debt mechanism (`scripts/validate_debt_baseline.json`), shrink-only.
  - A baselined record with no row only warns.
  - Once a backfill lane gives it a row, the validator warns that the entry can be removed.
  - Any tier-C/U record outside the baseline with no row is an error.
- **Keys:** `<record_table>:<record_id>:<identity fingerprint>`.
  - The table is in the key because ecosystem rows share the ORG- id space with organizations.
  - The fingerprint is the first 8 hex characters of the SHA-1 over the record's identity fields, each lowercased to
    letters and digits. The fields follow AGENTS.md §3's dedupe tests:
    - organizations: legal name, HQ city and state;
    - ecosystem: legal name, city and state;
    - sites: operator `org_id`, site name, street, city and state;
    - programs: institution and program name;
    - people: full name and institution.
- **What the fingerprint catches (Codex review findings, 2026-11-20).**
  - A baselined id overwritten in place with a different entity: no row is removed, so `check_row_loss.py` would not
    notice.
  - A baselined record renamed, moved or re-pointed without a witness.

  In each case the record drops out of the baseline and V-68 errors. The residual is an id overwritten with an entity
  that matches on every identity field, which by AGENTS.md §3's own tests is the same entity.

## Acceptance criteria

1. Without a V-68 baseline, `validate.py` reports one V-68 error per tier-C/U zero-row record and no other new errors.
   **Met:** checked on the pre-reconciliation all-tier version, which gave exit 1 with exactly 3,455 errors, nothing
   else.
2. The baseline count matches `scripts/audit_evidence_coverage.py` (tiers C and U) table by table, or the build refuses
   to write. **Met:** organizations 182, sites 613, ecosystem 52, people 10, programs 1 in both counts.
3. With the baseline, `validate.py` passes. **Met:** see the PR's evidence section.
4. Mutation tests in `scripts/test_validate.py`, `test_v68_*`, all pass:
   - an unbaselined tier-C/U record loses its only row → fails;
   - a new tier-C organization with no row → fails;
   - a baselined person gains a row → passes, with the "now pass" warning;
   - a baselined organization renamed in place → fails;
   - a baselined person moved to another institution under the same name → fails.
5. SCHEMA v1.17.1 records the rule (§4.13 "The presence floor for tier C/U" plus the changelog).
   `docs/AGENT_QUICKSTART.md` and the validator's docstring name it.
6. CI's full suite and a two-family review run before merge.

## Effect on other lanes

- A PR that creates a record at tier C or U must add at least one evidence row for it. Tier A/B creates were already
  held to V-65.
- A PR that changes an identity field of a grandfathered row-less C/U record must also add a row.
- Muse was told on crosswalk on 2026-11-20 (`johncalvin/agents`, post ptjjfw).

## Two-family review (`reviews/`, `--effort deep`)

| Round | Code reviewed | Codex | Antigravity |
|-|-|-|-|
| 1 | `<table>:<id>` keys, all tiers | UNSOUND: id reuse; brittle count in a test; dry-run exit | SOUND (nits) |
| 2 | Fixes for round 1 | UNSOUND: in-place repurposing removes no row | not re-run |
| 3 | Name fingerprint | UNSOUND: same-name different entity | SOUND |
| 4 | Identity fingerprint | UNSOUND: changes to non-identity fields aren't caught | SOUND (nits) |
| 5 | V-68 reconciliation (tier C/U, beside main's V-65) | UNSOUND: a blank or invalid ecosystem tier escapes both floors. Fixed: V-68 covers "not A/B", with test `test_v68_new_ecosystem_record_with_blank_tier_fails` | SOUND |
| 6 | Confirmation of the round-5 fix | **SOUND**: "V-68 now catches row-less records with blank or invalid tiers" | (round 5 SOUND) |

**Owner ruling on round 4 (2026-11-20, multiple choice): "Merge as is."** The rule ships as the floor for creates plus
identity changes. Widening it to every non-derived field change is a surfaced follow-up (QUEUE), not part of this PR.

## Reproduce

```
python3 tasks/evidence-presence-floor-2026-11-20/build_baseline.py           # dry run: both counts, plus drift vs the baseline
python3 tasks/evidence-presence-floor-2026-11-20/build_baseline.py --write   # refuses if V-68 is already baselined
python3 scripts/validate.py
python3 -m pytest -q scripts/test_validate.py -k v68
```
