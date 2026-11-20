# Evidence presence floor, validator V-65 (2026-11-20)

**Result:** a new validator rule, V-65, fails any organizations, sites, ecosystem, programs or people record that has
no row in `data/evidence_*.csv`. The 3,455 records with none on main `280e6a8f` are baselined, so main still passes.
No data row changes.

## Why

On 2026-11-20, 3,455 of the Atlas's records in those five tables had no evidence rows at all (`scripts/audit_evidence_coverage.py`).
- About 2,691 predate their evidence class and are grandfathered by SCHEMA §4.13.
- Most of the other 764 came from integration passes 16–18 at the contract cutover (2026-10-30/31).
- No rule caught them. V-25 restates tiers only for records that already have rows, and the lane-brief contract
  ("a create integrates only with evidence rows") was enforced by the integrator alone.

So a create with no rows could still land, and the backfill lanes were chasing a moving target. The owner ruled
2026-11-20: close the leak with a validator rule, with today's gaps recorded as backlog (option "Close the zero-row leak").

## The rule

- **Scope:** every record in `organizations_*.csv`, `sites_*.csv`, `ecosystem.csv`, `programs.csv` and `people.csv`.
- **What counts:** a row in a `data/evidence_*.csv` shard whose `record_table` and `record_id` name the record.
  Archive links (§4.22) and registry links (§4.8) don't count.
- **Baseline:** the existing debt mechanism (`scripts/validate_debt_baseline.json`, as V-45..V-55 and V-60 use).
  Entries are keyed `<record_table>:<record_id>:<identity fingerprint>`.
  - The table is in the key because ecosystem rows share the ORG- id space with organizations.
  - The fingerprint is the first 8 hex characters of the SHA-1 over the record's identity fields, each lowercased to
    letters and digits. The fields follow AGENTS.md §3's dedupe tests:
    - organizations: legal name, HQ city and state;
    - ecosystem: legal name, city and state;
    - sites: operator `org_id`, site name, street, city and state;
    - programs: institution and program name;
    - people: full name and institution.
  - A baselined record with no row only warns.
  - Once a backfill lane gives a baselined record a row, the validator warns that the entry can be removed; that
    is never an error.
  - Any record outside the baseline with no row is an error.
- **A floor, not the contract.** The lane-brief contract still requires a row for every must-have claim, and the
  integrator still checks that.
- **Id reuse and repurposing (Codex review findings, three rounds, 2026-11-20).** The identity fingerprint handles:
  - A baselined id overwritten in place with a different entity. No row is removed, so `check_row_loss.py` would not
    notice.
  - A baselined record renamed, moved (HQ city or state, site street) or re-pointed (site operator, person or program
    institution) without a witness.

  In each case the record drops out of the baseline and V-65 errors (tests
  `test_v65_baselined_record_repurposed_in_place_fails` and `test_v65_baselined_person_same_name_other_institution_fails`).
  The residual is an id overwritten with an entity that matches on *every* identity field. By AGENTS.md §3's own tests
  that is the same entity. Fingerprinting the whole row would close it, but it would also fail every automated pass that
  touches a grandfathered row (tier1 re-derivation, county or ZIP fills).

## Acceptance criteria (written before the change)

1. Without a V-65 baseline, `validate.py` on main reports exactly one V-65 error per zero-row record and no other new
   errors. **Met:** exit 1 with 3,455 V-65 errors, nothing else.
2. The baseline count matches `scripts/audit_evidence_coverage.py` table by table, or the build refuses to write.
   **Met:** organizations 1,340, sites 1,840, ecosystem 133, people 132, programs 10, in both counts.
3. With the baseline, `validate.py` passes. **Met:** exit 0, with one warning ("V-65: 3455 baselined rows still
   violate").
4. Mutation tests in `scripts/test_validate.py` (all pass):
   - A record outside the baseline that loses its only row fails.
   - A new organization with no row fails.
   - A baselined person who gains a row passes, with the "now pass" warning.
   - A baselined organization overwritten with a different name under the same id fails.
   - A baselined person moved to another institution under the same name fails.
   - With the V-65 `debt()` call disabled, each V-65 test fails (checked for the first three).
5. SCHEMA v1.16.5 records the rule (§4.13 "The presence floor" plus the changelog). `docs/AGENT_QUICKSTART.md` and
   the validator's docstring name it.
6. The full test suite, `check_row_loss.py` and a two-family review run before merge. Results are in the PR.

## Effect on other lanes

- A PR that creates a record must add at least one evidence row for it, or the `validate` check fails.
- A PR that changes an identity field of a grandfathered row-less record must also add a row. That covers a name, an
  HQ city or state, a site's operator, street, city or state, and a person's or program's institution. Each is a
  changed claim, and the lane-brief contract already asks for a witness.
- Muse was told on crosswalk on 2026-11-20 (`johncalvin/agents`).
- PR #427 (the URL-lead pilot) adds rows to 16 baselined records. Merged in either order, they only produce "now
  pass" warnings.

## Two-family review (`reviews/`, `--effort deep`)

| Round | Code reviewed | Codex | Antigravity |
|-|-|-|-|
| 1 | `<table>:<id>` keys | UNSOUND: id reuse; brittle exact count in a test; dry run exits non-zero | SOUND (nits: unclosed files, unstripped `record_table`) |
| 2 | Fixes for round 1; reuse said to be covered by CI row-loss | UNSOUND: in-place repurposing removes no row | not re-run |
| 3 | Name fingerprint | UNSOUND: same-name different entity | SOUND |
| 4 | Identity fingerprint (current) | UNSOUND, see below | SOUND (nits: inline import, a stale docstring, accent folding) |

**Codex's round-4 finding, held for the owner.** A contributor changes a non-identity field of a grandfathered row-less
record (for example its website) without adding a row. V-65 only warns.
- Codex reads SCHEMA §4.13's lane-brief contract ("rows for every record it creates or changes") as requiring V-65 to
  enforce changes to every substantive field.
- The owner's ruling scoped this rule to creates: "any record created after the evidence contract must carry at least
  one evidence row".
- Covering every non-derived field needs a list of derived and reference fields to exempt (tier1, county, ZIP,
  geocodes and others). It's a larger rule, so it's an owner decision, not settled in this PR (AGENTS.md §2 rule 9).
- **Owner ruling, 2026-11-20 (multiple choice): "Merge as is."** V-65 ships as the floor for creates plus identity
  changes. Widening it to every non-derived field change is a possible follow-up, not part of this PR.

Codex's round-4 nit (the drift report counted obsolete keys as repaired) is fixed: the dry run now separates
"repaired" (the record has a row) from "obsolete" (identity changed, still row-less).

## Reproduce

```
python3 tasks/evidence-presence-floor-2026-11-20/build_baseline.py           # dry run: both counts, plus drift vs the baseline
python3 tasks/evidence-presence-floor-2026-11-20/build_baseline.py --write   # refuses if V-65 is already baselined
python3 scripts/validate.py
python3 -m pytest -q scripts/test_validate.py -k v65
```
