# PR #193 L14 change feed — Grok clerk

VERDICT: APPROVE. Head `0f0551f3add23fae838f67176f9a9ed5f1e33aa2`. 0 findings. Remain draft: `review-packet.json` rounds and receipts are empty. This is the Grok family only.

Merge-base with origin/main: `8a5821b37e30`. origin/main during the run moved from `ca9480fa5d4a` to `09df9e9d7ff0`. The packet revision field is `a2a0a1e54b7a`; the seal commit only adds `review-packet.json`. Scripts are unchanged from `afbd4e9`. Controller token `a990c645` is not a commit, blob, or packet sha256 on this branch.

## Scope

`git diff --stat 8a5821b37e30..0f0551f` is 14 files, 1502 insertions: `scripts/build_changelog.py`, `scripts/test_build_changelog.py`, and `tasks/change-feed-2026-11-06/*`. No `data/`, `docs/SCHEMA.md`, or `.github/workflows` change. `implementation.patch` sha256 `84765f8c3ab334b10918e5ec18177ced39efa0bb765eb8f15eae675def6b56b7` and its bytes equal `git diff 8a5821b37e30 HEAD --` the two scripts (23574 bytes). Packet file sha256s match `review-packet.json`. `.github/workflows/pages.yml` still has `fetch-depth: 1`.

## Checks re-run

- `python3 -m unittest scripts.test_build_changelog`: 5 tests OK, 2.683s.
- `uv run --no-project --with pytest python3 -m pytest -q scripts/`: 226 passed, 1 skipped, 45 subtests, 63.76s. The skip is `scripts/test_atlas_mcp_server.py` (`mcp` not installed).
- `python3 scripts/validate.py` exit 0: 4972 organizations, 7025 sites, 36720 evidence on this branch tree. Pre-existing V-29 warnings. `real-check.json` sha256 stayed `a91efd2b0e167e0b5d730e8153af6c9dc061e4a4540c747751ab6c917ccf9482`. `git status` clean. `check_real_history.py` was not run; it rewrites that receipt from whatever `origin/main` is.

## Pinned main `c2674712c0c9`

`build(repo, c2674712c0c9f8aeefac9179597b8a4c6e5eda5f)` twice. 214 entries = 78 PR + 136 direct. Replay byte-identical. `feed.xml` sha256 `5eb7d7ad95711090c8348bc1bfe3e8cc072b3cf3816b98e3b6bc6de3cd2f7335`. `CHANGELOG.md` sha256 `ab8d4f6ab75659eb4239c88071e671c719b681dcfb4d8dbb5b3c73cfa399cfa3`. Both match `real-check.json`. Atom: 214 entries, 214 unique commit ids, content type text. Evidence balance first-seen + restorations − removals = 36606 = unique `evidence_id` at the pin. Generated `build/changelog/` was deleted afterward (`build/` is gitignored).

Independent of the packet writer:

- PR #140 `85b85600c77e`: equipment ids 34 new / 0 lost. Generator created 34.
- PR #143 `547d51b882ad`: site ids 18 new / 0 lost. New evidence `record_table=sites` 126. Generator matches.
- PR #133 `f437e0b89149`: ORG-000132 tier C→A, status stays active, tier list length 1. Relationships 356→357, only new id REL-000400. Generator also counts 11 organization evidence rows; the known-answer assert is the tier list.

## Attacks

- Legacy ORG-000101/102/103: ecosystem rows created at `46b8953a9433`, organization rows created later at `5977ffcfb063` as separate keys, ecosystem rows removed at `20d77389709d`. No cross-table transfer and no tier change on the organization-create commit. Later tier edits are on the organization row (U→A or U→B).
- `registry_links.site_id` appears at `16daedfcc4b1` (PR #17). Prior snapshot 2376 rows and no site column; that commit is 5148 rows, 2304 with a site id. 2376+2772=5148. Generator created 2772 registry rows and did not mass-remove. Empty site keys stayed put.
- PR #68 `bac580939d9a` removes 3351 registry rows. PR #129 `9d699789c9c1` restores 3348 previously seen keys. Those are not creations. The 3-row gap matches the held keys that were not restored.
- First-parent subjects on the pin: 96 match a merge or squash marker, 0 duplicate PR numbers, 0 odd parent shapes. 96/96 SHAs equal GitHub `mergeCommit.oid` (`gh pr list --state merged`). 78 of those commits touch a supported data CSV and become feed entries. Unmarked subjects such as `Merge PR #4` stay commit entries, which the spec allows.
- Every historical `data/` path on the pin, on this branch, and on origin/main is a supported table or `inclusion_log` (excluded). No nested CSV.
- Atom entry bodies contain no token outside ids, table names, controlled statuses/tiers, counts, and the fixed words. No email, phone, `CRM`, `mailto:`, or URL beyond the repo and the Atom namespace.
- Real-newline probes raise before a write: missing key columns, short row, duplicate header, extra field. The committed unit-test strings for two missing-column cases use a literal backslash-n, so they are weaker than they look; the product check still raises on a real two-line CSV.
- Current `origin/main` `09df9e9d7ff0` also generates: 227 entries = 91 PR + 136 direct, no duplicate PR labels, and the same three known answers (34 / 18 / ORG-000132 C→A). Output deleted. Direct-commit count stayed 136; the 13 new entries are PR merges.

## Not a finding

`check_real_history.py` pins whatever `origin/main` resolves to and overwrites `real-check.json`. The committed receipt is the c267471 run. README says both. Re-running the named command on a moved main would change the receipt even when the asserts pass. The generator itself accepts an explicit ref.
