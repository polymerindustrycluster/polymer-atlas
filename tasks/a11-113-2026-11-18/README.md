# Blind audit 11 correction A11-113 — 2026-11-18

Lane `atlas-w18-backlog` (Claude Sonnet 5.5). One draft PR, no merge. Writes: `data/registry_links.csv` (one row removed) and this folder's `REMOVALS.csv`.
First user: PIC cluster reporting analyst (registry-link counts). Review date: 2026-12-16 (non-use is a finding if those counts are not read).

## What and why
Blind audit 11 (`tasks/blind-audit-11-2026-11-17/adjudication.json`, id A11-113, `change_class` uei_links, grade **CREATION_ERROR**) found one UEI registry link wrongly created on ORG-000889. This PR removes that one link, as the adjudication directs ("retire"; the basis is held privately under R-SAM). Records are not deleted: the organization, its sites and its other registry links (FRS and TRI links) are untouched.

R-SAM: no SAM API was called; no SAM entity name or address is written in any file or in the PR text. The key is read from the adjudication at build time; the link is referred to as "the A11-113 UEI link".

## Mechanism
The removal is declared in `REMOVALS.csv` (table `registry_links`, key `org_id|registry|registry_id|site_id`, reason), the manifest `scripts/check_row_loss.py` reads; precedent: `tasks/dedupe-medium-apply-2026-11-06/REMOVALS.csv`. Without that row `check_row_loss.py` fails ("registry_links: 1 removed"), as tested.

## Result (unit: registry links, `data/registry_links.csv`, all registries)
| Unit | Count |
|---|---|
| Links before / after | 6,025 / 6,024 |
| Links removed (the A11-113 UEI link) | 1 |
| Other UEI links kept (all organizations) | 617 |
| Applied / held | 1 applied, 0 held |
| Data files changed | 1 (`data/registry_links.csv`) |

## Checks run
- `python3 tasks/a11-113-2026-11-18/check.py`: recomputes against the pinned base (`base.txt`); the removed keys equal the one CREATION_ERROR uei_links item counted independently in the adjudication; every kept row unchanged and in order; `REMOVALS.csv` lists exactly the removed key; only `registry_links.csv` changed under `data/`; `check_row_loss.py` passes; `build.py` has no network code, writes each file atomically (temp file in the same directory, flush, fsync, `os.replace`), asserts base minus one row before writing, and is idempotent. It asserts the full row count against the base (6,024 = 6,025 − 1) and fails on 6 injected defects: a removal without a REMOVALS row, a second UEI link removed, a second non-UEI link removed, the A11-113 link left in place, a kept row altered, a truncated file (100 rows). It also replays Codex's cut-short-write reproduction (PR #382 review) on a temp copy: a write that dies after 100 rows leaves the target intact with no temp file, the retry gives 6,024 links, and a target already truncated to 100 rows makes the builder refuse instead of reporting success.
- Dependents of the removed link: `scripts/derive_tier1.py` in check mode reports 0 organizations with qualifier drift, identical with and without this change (the organization's tier-1 basis rests on its TRI link, which is kept); no organization evidence row of ORG-000889 cites a UEI or SAM source.
- `python3 scripts/validate.py`: 0 errors. `check_row_loss.py --base origin/main`: OK with the manifest, fails without it. `export_vocab.py --check`: current.

## Self-refute (contract rule 15)
- self-refute: grain — 1 row checked, 0 changed. The key names the organization-grain UEI link (empty site_id); no site-grain row is touched.
- self-refute: founding — 0 rows checked (no date or founding claim).
- self-refute: strength — 0 rows checked (a removal adds no evidence).
- self-refute: truncated quote — 0 rows checked (no quote).
- self-refute: attribution — 1 row checked, 0 changed. The grade is the audit's: reviewer A CREATION_ERROR, reviewer B UNRESOLVED, adjudicated CREATION_ERROR; this PR does not re-judge it.

## Not checked
- The SAM basis (held privately under R-SAM; not read or reproduced here). Whether ORG-000889 should carry a different UEI link: that is a separate verification, not part of this PR. `tasks/QUEUE.md` is not touched (contract rule 9): its blind-audit-11 corrections line still lists A11-113 as open until the controller updates it.
- `scripts/` untouched, so the unit-test run was skipped. The two-family refute review is the controller's.

## Proposed follow-ups (not in this PR)
- A11-047 (ProVia `newsroom_feed_url`): held until `organizations_OH.csv` is free.
