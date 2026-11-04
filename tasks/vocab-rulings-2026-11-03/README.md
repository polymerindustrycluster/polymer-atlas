# Owner vocabulary rulings B-VOC-1 through B-VOC-4

Claim: `claimed:codex-vocab-rulings 2026-11-03`, under the controller's
`WORKER_CONTRACT.md`. The controller owns queue updates, independent completion
review and the PR. This packet is for that controller's immediate integration
review; it does not close a tracked commitment.

Authority: `tasks/OWNER_BATTERY_2026-11-03.md`, every B-VOC item ruled (a).
The immutable input is `tasks/vocab-normalize-2026-11-02/ruling_proposals.csv`.
No external research or new source claims were introduced.

## Applied scope

- SCHEMA v1.9.1, dated **2026-11-03, owner battery B-VOC**: eight process
  terms and four material terms; every unspecified term carries the required
  "type not stated; never upgraded without a source" annotation.
- `processes_other_note` and `materials_other_note` immediately follow their
  respective fields in all **50 held site shards**. Existing column order is
  otherwise preserved. The validator now requires both columns.
- **1,583 distinct cells on 1,025 distinct records** changed capability/note
  content. Header additions also affect site rows whose content is unchanged.
  **51 canonical files** changed: 50 site shards and `organizations_OH.csv`.
- Validator vocabulary and its generated `docs/schema/vocab.json` agree.
  The SQLite/release builders discover columns from CSV headers; graph and MCP
  vocabulary consumers read the shared vocabulary. No duplicate vocabulary or
  fixed production site header needed another implementation change.
- All original row order, IDs, unrelated fields, and LF line endings were
  preserved. `tier1_qualifier` and its basis were not changed.

## Reconciliation

Units: a **value** is one `(field, original token)` proposal; a **token** is
one occurrence in a canonical cell; a **row** is one record within its file
class. Row counts are distinct within each table row below and overlap across
proposals. Values present in both file classes are likewise not additive.

| File class | Proposal | Values present | Tokens matched | Tokens changed | Tokens held | Rows matched | Rows changed | Rows held |
|-|-|-:|-:|-:|-:|-:|-:|-:|
| sites | MAP | 59 | 469 | 469 | 0 | 379 | 379 | 0 |
| sites | NEW_UMBRELLA | 32 | 408 | 408 | 0 | 355 | 355 | 0 |
| sites | TO_NOTE | 41 | 381 | 381 | 0 | 321 | 321 | 0 |
| sites | DROP_NOT_CAPABILITY | 16 | 197 | 197 | 0 | 181 | 181 | 0 |
| sites | WRONG_FIELD | 16 | 381 | 0 | 381 | 329 | 0 | 329 |
| organizations | MAP | 5 | 7 | 7 | 0 | 7 | 7 | 0 |
| organizations | NEW_UMBRELLA | 4 | 7 | 7 | 0 | 7 | 7 | 0 |
| organizations | TO_NOTE | 4 | 10 | 0 | 10 | 10 | 0 | 10 |
| organizations | DROP_NOT_CAPABILITY | 2 | 2 | 2 | 0 | 2 | 2 | 0 |
| organizations | WRONG_FIELD | 4 | 199 | 0 | 199 | 199 | 0 | 199 |

| Original proposal | Values | Tokens matched | Tokens changed | Tokens held |
|-|-:|-:|-:|-:|
| MAP | 59 | 476 | 476 | 0 |
| NEW_UMBRELLA | 32 | 415 | 415 | 0 |
| TO_NOTE | 41 | 391 | 381 | 10 |
| DROP_NOT_CAPABILITY | 16 | 199 | 199 | 0 |
| WRONG_FIELD | 16 | 580 | 0 | 580 |
| Total | 164 | 2061 | 1471 | 590 |

Every value's live count equals its historical `tokens` count, and every
file-class count satisfies matched = changed + held. The per-value detail,
including zero matches in a file class, is retained in `reconciliation.json`.
NEW_UMBRELLA totals retain the input proposal classification: **77 site tokens
across nine monomer/intermediate values** instead use effective TO_NOTE. No
such occurrence was found in organization fields. Thus the site transfer to
other-note columns comprises 381 original TO_NOTE tokens plus those 77 tokens.

## Deliberate holds

- All **580 WRONG_FIELD tokens** remain: 381 site and 199 organization
  occurrences, covering Ring 3 labels and product forms. No subtype column or
  new capability records were invented.
- The **10 organization TO_NOTE tokens** remain in capability cells:
  `tooling` (3), `cast_polymer` (4), `acrylic emulsions` (1), and
  `vinyl_window_manufacturing` (2). No organization note column was added.
- `monomers_intermediates` is not vocabulary. The 77 original site occurrences
  survive as text in `materials_other_note`, pending a scope ruling.
- No field-placement deviation: all approved terms occur in the fields named
  in the contract and proposal CSV.

## Site vocabulary coverage

Denominator: all nonempty semicolon-separated token occurrences in the named
field across all held site shards, without filtering by operating status,
ring or geography. Before uses the pre-revision vocabulary; after uses the
approved vocabulary and edited cells. Removals and deduplication change the
denominator. These are structured-data coverage shares, not evidence upgrades.

| Site field | Before in-vocabulary / all tokens | Before share | After in-vocabulary / all tokens | After share |
|-|-:|-:|-:|-:|
| processes | 2124 / 5784 | 36.72% | 2532 / 5574 | 45.43% |
| materials | 3330 / 6659 | 50.01% | 3740 / 6232 | 60.01% |

## Reproduction and rollback

`python tasks/vocab-rulings-2026-11-03/build_edits.py` makes a dry-run plan
and `edits_log.csv`; `--apply` requires an identical plan and checks all input
hashes before writing. This is a one-pass migration: rerunning it on applied
shards intentionally fails, rather than replacing the original receipts.

The pre-pass backups were kept **out of the repo** in the integrator's local scratch area, because they are 51 full
shard copies. They can also be regenerated from this branch's parent commit (`git show origin/main:data/<file>`).
`rollback_manifest.json` names each original destination and backup hash.
Restore only against a reviewed current-state diff; later edits must not be
overwritten. `dry_run.json` and `reconciliation.json` preserve input/output
hashes and the complete reconciliation. These local backups are rollback
artifacts, not additional canonical shards.

Each edit-log entry gives the original and final cell plus a contributing
proposal/value. A cell can have several entries; count unique
`(file, row_id, column)` for changed cells. During simplification review, 99
note entries attributed to unrelated MAP/DROP/approved-umbrella tokens were
removed. Note entries now identify only effective TO_NOTE contributors. The
canonical data did not require a correction.

## Verification and limits

- `python scripts/validate.py`: **exit 0**, `OK — validation passed.` Existing
  warnings remain in `validate.log`.
- `python -m unittest scripts/test_vocab_rulings.py`: **exit 0**, five tests;
  includes deliberately broken reconciliation counts and historical totals.
- `python tasks/vocab-rulings-2026-11-03/verify_application.py`: **exit 0**,
  `APPLICATION_AUDIT=PASS`, every input/output hash, header and untouched field
  checked against the retained backups. This is read-back/preservation
  verification; expected mapping content reuses the migration's rewrite function.
- `python -m unittest discover -s scripts -p "test_*.py"`: **exit 0**, `OK (skipped=1)`. The integrator re-ran it
  in its own shell. In the worker's sandbox the literal command hit a Windows temp-directory ACL problem, and the
  worker then passed the same 196 tests through a temp-dir wrapper, which is not committed. The existing MCP tool-registration test is skipped
  because the optional `mcp` package is not installed. Git provenance execution
  is deliberately unavailable under the contract's no-Git constraint.
- `python scripts/export_vocab.py --check`: **exit 0**, vocabulary current.

The literal requested unittest discovery initially exited 1: Windows Python
3.14's private temporary-directory ACLs caused permission failures, and the
matching test still expected `carbon_black` to be invalid. The latter fixture
now expects the approved term and continues rejecting the unnormalized
`carbon black` alias. Site-column fixtures were minimally extended in the CLI,
MCP and site-builder tests. A validator mutation test removes each new note
column and requires failure.

`run_tests.py` runs the same discovery suite with inherited ACLs for temporary
directories within this task folder, restoring `os.mkdir` afterward. Test
commands use a PATH without Git and TEMP/TMP inside this task. This is an
execution-environment deviation from the literal command; it adds no skips or
weakened assertions beyond the suite's existing optional-dependency skip. The
initial failed run's temporary directories are
left for controller cleanup; no access-control repair was attempted on them.

The required read-only code-simplifier review approved the corrected helpers.
No Git command, network access, commit, push, PR or tracker change was made.
The controller retains integration and independent-family approval duties.
