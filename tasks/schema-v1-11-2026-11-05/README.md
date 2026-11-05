# Schema v1.11 (2026-11-05)

This implements three items of `tasks/OWNER_BATTERY_2026-11-04.md`, all ruled (a): B-NEWS, B-LINKEDIN and
B-ARCHIVE. B-ARCHIVE's storage form was ruled on 2026-11-05 (see the addendum in that file).

## Changes
- **SCHEMA §4.4** gains three optional organization columns, present on every row and born empty:
  - `newsroom_url`: the organization's own news page, on the same registrable domain as `website`;
  - `newsroom_feed_url`: its RSS or Atom feed;
  - `linkedin_url`: a navigation link only, never an evidence row or a monitoring source.
- **SCHEMA §4.22, new:** `data/archive_links.csv` (`evidence_id, archive_ref, captured_at, created_by`), born empty.
  It holds the Wayback capture of an evidence row's page. It is a side table so that no evidence row or builder header
  changes, and it is named outside the `evidence_*.csv` shard pattern because it is not an evidence shard.
- **Validator:**
  - V-3c requires the three columns;
  - V-58 checks URL shape, keeps `newsroom_url` on the website's own domain, and checks the `linkedin.com/company/`
    form;
  - V-59 checks the archive table's field set, its evidence-id FK, the `web.archive.org/web/<14-digit>/` URL shape,
    the date, and one row per evidence id.
- **`build_sqlite.py`** loads `archive_links`.
- **QUEUE.md:** the news monitor switch-on is ruled, but its code lives in another harness's working area.

## Data step (`add_columns.py`, idempotent)
All 50 organization shards gain the three empty columns: 4,945 rows. Every existing value was compared with main and
none differs. Each shard keeps its line endings.

## Checks
- `python scripts/validate.py` exits 0.
- `python -m unittest scripts.test_validate scripts.test_audit_evidence_coverage scripts.test_derive_tier1` ran 71
  tests, all OK.
- The 6 new tests cover V-58 and V-59: an own-domain newsroom passes, an off-domain one fails, a personal LinkedIn URL
  fails, a good archive link passes, a non-Wayback archive link fails, and both a dangling and a duplicate archive
  link fail.
