# Schema v1.12 (2026-11-06)

Implements the owner's B-CROSSWALK and attendee-role decisions in `BRIEF.md`.
Worker: Codex, branch `agent/codex/schema-v1-12`; controller owns the queue,
review, commit and release. No tracker or queue change is part of this task.

## Acceptance and scope

- Append `pic_events_slug` as the last `data/events.csv` column, populated
  from the supplied `crosswalk.csv` by `event_id`. Preserve every prior byte.
- V-61 rejects malformed semicolon-separated slugs, a slug repeated in one cell, and a slug on two event
  rows. Cross-repository existence is deliberately not checked by CI. (Renumbered from V-60 on 2026-11-09: V-60 is
  now the licensed-source rule, #258.)
- Add `attendee` to V-19 and the generated vocabulary. Schema §4.12.2 limits
  it to organizer-published company lists for a named edition, including
  evidence-dated pre-show registration lists with the pre-show note.
- Existing participation records and all other canonical data stay unchanged.

## Data step and rollback

`python3 tasks/schema-v1-12/add_crosswalk.py --dry-run` validated the input
and planned the append before application. Running without `--dry-run`
appended the column to 71 event-series rows: 64 mapped, 7 empty. The script
checks ID uniqueness, complete crosswalk coverage, slug syntax, duplicate
slugs, preserved bytes and parsed values before writing. A second run
confirmed the existing mapping and wrote no bytes.

The worker checked the result against `HEAD:data/events.csv`: removing only the appended column reproduced the
original byte for byte. To roll back the data step, revert this PR's `data/events.csv` change after checking for later
edits. Never overwrite later work blindly.

## SQLite and vocabulary

`scripts/build_sqlite.py` already derives table columns from CSV headers,
so it needs no source edit. Its generated `events` table has the new column
last; all 71 SQL event mappings matched the CSV, including NULL for the
7 unmapped series. Build outputs are generated artifacts, not source changes.

`python3 scripts/export_vocab.py` regenerated `docs/schema/vocab.json`;
its only change is the new `PART_ROLES` value.

## Verification

- `python3 scripts/validate.py`: exit 0, with existing data warnings.
- `python3 scripts/export_vocab.py --check`: exit 0.
- `python3 scripts/build_sqlite.py`: exit 0.
- `python3 tasks/schema-v1-12/test_crosswalk.py`: exit 0, 3 tests covering
  byte preservation (quoted/multiline/Unicode fields, line endings and no
  final newline), mismatched/duplicate IDs and malformed input.
- `python3 -m unittest scripts.test_validate`: the worker's sandbox could not create temporary directories, which is
  a Windows permission issue. So the controller ran the tests outside the sandbox, and CI runs them on Linux.

The five new validator tests cover nullable/single/multiple slugs, malformed
slugs, cross-event collisions within multi-slug values, accepted `attendee`
and rejected `attendees`. A read-only code-simplifier review caught an
overbroad header exception in the migration's slug check; it was corrected
and added to the malformed-input regression test.

## Handoff limits

No commit, push, external-repository existence check or issue closure.
`scripts/test_build_graph.py` hard-coded a role set without `attendee` or the existing `host`. The controller widened
it to the §4.12.2 enum in this PR. No attendee data rows are introduced here.
