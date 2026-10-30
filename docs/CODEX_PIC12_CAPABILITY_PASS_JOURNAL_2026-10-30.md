# PIC-12 capability enrichment — local integration journal

- Task and PR: [PIC-12 capability enrichment #2](https://github.com/polymerindustrycluster/polymer-atlas/pull/2).
- Baseline: `3036121b0245bee1e6b1c8f46ed63c0a39821226`; task-claim branch originally started at `97ba36c`.
- Integrator of record: **codex-dot / build_atlas_quality_prs**, designated by parent orchestrator. The integrator serialized the CAP allocation and delegated the bounded local application to the capability worker; no competing writer edited this file.
- Research: 20 existing PIC-12 Ohio sites reviewed against public first-party sources. Final scoped verdicts: 10 VERIFIED for listed capabilities only; 10 STILL_UNCERTAIN with explicit settling facts. No full-site verification, operating-status, classification, certification or verification-tier changes.
- Application: on 2026-10-30 at approximately 15:22 UTC, before fetching the subsequent AGENTS swim-lanes amendment, appended 36 claims to `data/site_capabilities.csv`: 20 material, 9 process, 7 product-form rows across 10 existing sites. Confirmed maximum existing ID 461, zero duplicate live tuples, and allocated CAP-000462 through CAP-000497 under the integrator's instruction.
- Mutation boundary: capability CSV only; no organization, site, evidence, relationship, or other canonical file edited. Existing 157590-byte capability prefix preserved exactly. CAP claims use their own schema §4.15 provenance; no new or modified site/org must-have claims require evidence rows.
- Reservation: IDs are provisional on this branch, **not a main lock**. Current upstream maximum, collisions, live tuples, and site/org identity hashes must be rechecked immediately before merge. No gap filling or silent identity relinking.
- Backup: the original capability bytes were captured and checked in memory before application. A filesystem backup was reconstructed afterward from immutable baseline `3036121`, at `/workspace/scratch/476f38d3e773/atlas-site-research/backups/site_capabilities.before-pic12-3036121.csv`. This is not claimed to be a contemporaneous pre-pass disk backup; its SHA-256 is recorded in the review manifest and matches the original byte-prefix checksum. The newer pre-pass-backup rule was read after the initial application; this timing is disclosed rather than backdated.
- Protocol reconciliation: read AGENTS amendment `9d7a33f`, merged `origin/main` locally, and updated only documentation/queue to the new verdict grammar and explicit integrator journal. No further data edits were made in reconciliation. Future data applications require a filesystem backup before mutation.
- Validation: `python3 scripts/validate.py` passes (warnings retained), `python3 scripts/build_sqlite.py` passes with 497 capability rows. Generated database/exports excluded. `git diff --check` passes.
- Publication: connector publication belongs to the integrator; no local push, main mutation, or merge authorization. PR remains for human review and merge.

Source URLs, bounded facts, publication/observation distinctions, all 20 decisions, identity-row hashes, and premerge checks are in `CODEX_PIC12_CAPABILITY_REVIEW_2026-10-30.json`.

## Latest upstream reconciliation — 2026-10-30 15:59 UTC

Merged pass18 main `f928257`. All 20 frozen identity fingerprints (10 sites and 10 organizations) match the research baseline; no affected-row holds are required for identity drift. Upstream still contains 461 capability rows with maximum CAP-000461, and none of the 36 proposed tuples or allocated IDs collide. Its original capability bytes are still preserved exactly. Only the four PR-owned paths are intended for connector publication, not pass18's upstream data changes.

Validation is **currently blocked by 49 upstream errors**: the proposed tree and an isolated pristine f928257 worktree produce the exact same error multiset; zero extra errors are introduced by this PR. Missing organization foreign keys are among the errors. Logs: `/tmp/atlas-cap-validator.log` and `/tmp/atlas-pass18-baseline-validator.log`. SQLite build succeeds with 497 capability rows. Latest checked dataset totals: 3485 organizations, 4244 sites, 6640 evidence rows, 331 relationships, and 782 participation rows.

Do not describe this latest tree as validation-passed or ready to merge. Await upstream repair and rerun the gate; this capability PR makes no unrelated fixes. The earlier clean validation result applies only to its earlier baseline.
