Adds the C-04 public change-feed generator: python3 scripts/build_changelog.py reads full local origin/main history and writes build/changelog/CHANGELOG.md plus Atom feed.xml. Each main update lists created record IDs, status/tier transitions and new evidence counts by target table. Standard merge/squash markers identify PRs; older unmarked updates are labelled by commit. Shard moves, unique org/ecosystem transfers and restored rows are distinguished from new creations.

Only IDs, controlled values, counts and public commit/PR identifiers are rendered. Notes, claim/source text, registry identifiers, commit subjects/authors, contacts and CRM content are excluded. Malformed/ambiguous data, bad key columns, shallow history and output symlink escapes fail before artifacts are replaced. Canonical rows added/changed: 0 at every tier; no evidence allocation, inclusion log or owner ruling. Controller-assigned L14 tooling claim, packet tasks/change-feed-2026-11-06.

Checks: five throwaway-repository tests; full scripts suite 226 passed/1 skipped/45 subtests; validator0. Real pinned-main generation: 214 history entries (78 PR/136 direct), three known PR outcomes, evidence balance36,606rows, valid Atom structure/stable IDs, contact exclusion and byte-identical replay. Outputs remain uncommitted under build/. Full-history generation took50seconds. No Pages hook because its current checkout depth is1.

Codex/Grok completion refutes pending; draft. Not checked: hosted publication, feed-reader UI, external Atom validation or usage. Rebase merges without PR subject markers cannot be associated from Git alone.

🤖 Generated with Codex (bb child of thr_9i2c6byhcz)
