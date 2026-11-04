# Worker contract: apply owner rulings B-VOC-1 to B-VOC-4 (2026-11-03)

You are a bounded implementation worker. The controller (claude-code) reviews your diff, runs verification and owns
the PR. **Never run git, never push, and never touch anything outside this worktree**
(`C:\Users\JohnSwanson\Documents\pic-github\_wt\atlas-vocab`).

## Read first
- `AGENTS.md`, `docs/SCHEMA.md` §3 (lines ~616–700) and its revision log at the end. A vocabulary change needs a
  dated schema revision.
- `tasks/OWNER_BATTERY_2026-11-03.md`, items B-VOC-1 to B-VOC-4. All were **ruled (a)**.
- `tasks/vocab-normalize-2026-11-02/ruling_proposals.csv`: 164 rows, columns field, value, tokens, proposal, target,
  rationale. `ruling_proposals_SUMMARY.md` sits beside it.
- `tasks/vocab-normalize-2026-11-02/build_edits.py`: the earlier mechanical pass. Reuse its tokenizing and
  hash-checked edit style.

## What the rulings mean (do exactly this)

**1. SCHEMA revision.** Add a dated revision entry ("2026-11-03, owner battery B-VOC") and add these terms to §3.1
and §3.2:
- **Processes:** `extrusion_unspecified`, `compounding_unspecified`, `fabrication_unspecified`,
  `foam_production_unspecified`, `molding_unspecified`, `recycling_unspecified`, `rubber_molding_unspecified`,
  `reaction_injection_molding`.
- **Materials:** `carbon_black`, `polymer_additives`, `thermoplastic_olefin_tpo`, `composites_unspecified`.
- **Field placement:** these lists are a starting point. If `ruling_proposals.csv` puts a term's values in the
  *other* field, follow the CSV, and report it.
- **Annotation:** mark each `_unspecified` term "type not stated; never upgraded without a source", following the
  `thermoforming_unspecified` precedent.
- **`monomers_intermediates` is NOT added.** Its values are treated as TO_NOTE.

**2. New columns.** Add `processes_other_note` and `materials_other_note` to **every site shard**
(`data/sites_*.csv`).
- Place them right after `processes` and `materials` respectively. If the validator requires a fixed column order,
  append them at the end instead.
- Document them in SCHEMA's site-table field list.
- Update `scripts/validate.py` so these columns are accepted, along with any column list in `scripts/`, the builders
  or the tests that enumerates site columns. Grep first.

**3. Validator vocabulary.** Add the 12 new terms to `PROCESSES` / `MATERIALS` in `scripts/validate.py`, and to any
other vocabulary copy you find by grep, such as `atlas_mcp_server.py` or `build_pages.py`.

**4. Data edits** on site shards (`processes` and `materials` fields only), keyed by `ruling_proposals.csv`:

| Proposal | Edit |
|-|-|
| MAP | Replace the token with `target`, which may be `;`-separated. Dedupe within the cell and keep the order. |
| NEW_UMBRELLA | Replace the token with its new term, except `monomers_intermediates` targets, which are handled as TO_NOTE. |
| TO_NOTE | Remove the token from the field, and append the original text to that row's `*_other_note` cell (`;`-joined, deduped). |
| DROP_NOT_CAPABILITY | Remove the token. |
| WRONG_FIELD | **Leave untouched.** This covers the Ring 3 labels (B-VOC-4: kept until a column ruling) and the product forms (not ruled). |

**Organization shards:** if the 164 values also occur in `data/organizations_*.csv` `processes` or `materials`,
apply MAP, NEW_UMBRELLA and DROP the same way. Do **not** apply TO_NOTE there, because organizations have no
other-note column; leave those tokens and count them. Report the counts.

**5. How to apply.**
- Write `tasks/vocab-rulings-2026-11-03/build_edits.py` (stdlib only). It runs a dry run by default and takes
  `--apply`. In one pass it must:
  - add the two columns;
  - rewrite the cells;
  - write `edits_log.csv` with these columns: file, row_id, column, old_value, new_value, proposal, value.
- The script must assert its own reconciliation. For each of the 164 values, it compares tokens matched against tokens
  changed or held, broken down by file class (sites vs organizations), and prints a per-proposal table.
- A matched token that is not accounted for is a failure. AGENTS §2 rule 10c: reconcile counts, and never explain
  them away.
- Keep each file's line endings (LF) and its existing column order.
- Run it with `--apply`, then run `python scripts/validate.py` and `python -m unittest discover -s scripts -p "test_*.py"`.
  Both must pass. If a test enumerates columns, fix the test fixture minimally and report it.

**6. Write `tasks/vocab-rulings-2026-11-03/README.md`.** Cover:
- what was applied;
- the reconciliation table (values, tokens, rows; units named);
- what was deliberately left: WRONG_FIELD, organization TO_NOTE, and `monomers_intermediates`;
- before and after shares of in-vocabulary tokens for site `processes` and `materials`.

## Hard limits
- No other vocabulary changes.
- No `tier1_qualifier` edits; it is derived.
- No edits outside `processes`, `materials`, the two new columns, SCHEMA, `scripts/` and this task folder.
- No network access is needed.

## Final output
Write `tasks/vocab-rulings-2026-11-03/WORKER_REPORT.json` with:
- `files_changed` (a list);
- `schema_terms_added`;
- `reconciliation`: per proposal, `values`, `tokens_matched`, `tokens_changed`, `tokens_held`;
- `validate_exit`;
- `tests_exit`;
- `deviations` (anything you did differently from this contract, and why).
