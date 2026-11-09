# Worker brief: Atlas schema v1.12 (events crosswalk + attendee role)

**Repo:** this worktree of polymer-atlas, on branch `agent/codex/schema-v1-12`. Read `AGENTS.md`, then `docs/SCHEMA.md`
§4.12 (events and participation) and its revision history at the top, before changing anything.

**Pattern to copy:** schema v1.11, commit `3c7cca5`, which added the columns plus `tasks/schema-v1-11-2026-11-05/`. Run
`git show 3c7cca5 -- docs/SCHEMA.md scripts/validate.py scripts/test_validate.py scripts/build_sqlite.py tasks/` and
mirror its structure:
- a dated revision entry;
- the field rows;
- validator rules with tests;
- the SQLite column;
- a task folder with a README and the script that applied the change.

## The two changes (owner decisions, 2026-11-06)

### 1. `events.csv` gains a `pic_events_slug` column (B-CROSSWALK)
- **Meaning:** the series' identity in PIC's conferences list (repo `polymerindustrycluster/conferences`,
  `data/series/<slug>.yaml`). It is the join key between the two repositories. The conferences repo holds edition
  facts (dates, place); the Atlas holds participation.
- **Format:** nullable. One slug, or several separated by `;` when the conferences list splits one Atlas series into
  several (e.g. a rubber group's winter, spring and fall meetings). Each slug matches `^[a-z0-9]+(-[a-z0-9]+)*$`.
- **Validator V-60:**
  - an error on a malformed slug;
  - an error when the same slug appears on two event rows.

  Existence in the other repo is NOT checked here, because CI cannot see that repo. Say so in the field row.
- **Data:** populate the column from `tasks/schema-v1-12/crosswalk.csv`, using its `event_id` and `pic_events_slug`
  columns (71 rows; 64 have a value). Add the column as the LAST column of `events.csv`. Write the change with a small
  script, `tasks/schema-v1-12/add_crosswalk.py`, as v1.11 did, and keep every other byte of `events.csv` unchanged.

### 2. `event_participation.role` gains `attendee`
- **Definition (put it in §4.12.2's role notes, verbatim in substance):** the organization attended a specific
  edition, as shown by a list the ORGANIZER itself published: a post-show report, a delegate-company list, or a
  brochure's "companies attending <edition>".
  - Generic marketing with no named edition ("attendees include companies like …") never mints a row.
  - A pre-show "registered" list is valid only as of its `evidence_date`, with the same pre-show note as exhibitor
    rosters.
  - Organizations only, as for every role (§6).
- **Implementation:** update the role vocabulary wherever it is enforced (validator and vocabulary export), and add a
  test that `attendee` passes and a typo (`attendees`) fails.

## Checks: the controller re-runs these, and each must exit 0
`python3 scripts/validate.py`
`python3 scripts/export_vocab.py --check` (regenerate the vocabulary export if the role change requires it, as v1.11 did)
`python3 -m unittest scripts.test_validate`
`python3 scripts/build_sqlite.py`

## Limits
- **Change only these:** `docs/SCHEMA.md`, `scripts/validate.py`, `scripts/test_validate.py`,
  `scripts/build_sqlite.py`, the vocabulary export file if `export_vocab` regenerates it, `data/events.csv` (the new
  column only) and `tasks/schema-v1-12/`.
- **Don't touch** any other data file, `tasks/QUEUE.md` (another session edits it), git config, or remotes.
- **Don't commit or push.** The controller reviews the diff and commits.
- **Every new validator rule** needs a test that fails without the rule.
