# Two §3.1 process terms and SITE-000562: owner ruling 2026-11-18b item 2 (SCHEMA v1.16)

Branch `agent/claude-code/process-terms-2026-11-18b`. Base `f35fb750` (PR #393 merged). Ruling: `tasks/owner-rulings-2026-11-18b/README.md` item 2.

## Vocabulary (SCHEMA §3.1, validator PROCESSES, vocabulary export)
| Term | Placed | Also |
|---|---|---|
| `rubber_molding_transfer` (rubber transfer molding) | §3.1 rubber/elastomer group, beside `rubber_molding_compression` | joins the `rubber_molding` ROLLUP line (§3.6 crosswalk) |
| `composites_spray_up` (spray-up open molding, distinct from `composites_hand_layup`) | §3.1 composites group, beside `composites_hand_layup` | none |
`scripts/validate.py` PROCESSES has both; `docs/schema/vocab.json` regenerated (`python3 scripts/export_vocab.py`; `--check` passes). SCHEMA version line v1.16 and a revision-history entry cite the rulings file.
v1.15 was taken at this base (PR #393); #395 (open) uses v1.14.1, so v1.16 is the next free number. No SCHEMA or validator conflict on merging origin/main.

## Data (unit: `sites_OH.csv` site rows and `evidence_sites_OH.csv` rows)
| Item | Count |
|---|---|
| SITE-000562 `processes` gets `rubber_molding_transfer` (union; `recycling_recovery;rubber_molding_compression` kept in order) | **1** site row, 1 cell |
| New evidence rows (EVD-397200, `scope`, `own_site`, `supports_C`) | **1** |
| `composites_spray_up` applied to sites | **0** (SITE-000248 and the permit sites are for the permit lane) |
| `site_capabilities` rows | 0 changed (580 at base and now) |
- **Tier:** SITE-000562 is **tier C** at this base (`verification_tier` C), so a services-menu term (supports_C) may union into `processes`; on tier A or B it would be a `site_capabilities` row only (owner ruling 2026-11-14), and `build.py` refuses that case.
- **Source:** the stored page of PR #381 (`tasks/cap-term-unions-2026-11-18/`, the held row; page hash `0c2c59b5…`). Quote: "Services Compression Molding Transfer Molding Tooling Custom Moldings", a services-menu line, so `supports_C`. The locality witness is the same as for the merged compression row EVD-396503 (the contact page's shipping address line: 350 State Street, Wadsworth, OH 44281). The words are validated in order against the stored page by the CAP2A helper (sha256, words in order, term in the vocabulary).
- Only `processes` changed on that row (no `sources`, `notes`, `last_verified` or tier change; AGENTS rule 13).

## Holds
None in this PR. Not applied here by design: `composites_spray_up` on SITE-000248 and the permit sites (permit lane); ORG-001855 (spiral-wound paper/phenolic tube) stays held (ruling item 2).

## Rule 15 self-refute
- self-refute: grain — 1 row checked, 0 changed. The menu is on the organization's own site; the one-site organization's locality witness is its shipping address in Wadsworth (the page labels it "Shipping Address", not a mailing address; it is the same witness the merged EVD-396503 uses).
- self-refute: founding — 0 rows checked (no founding claim), 0 changed.
- self-refute: strength — 1 row checked, 0 changed: a menu line stays `supports_C`, on a tier C site.
- self-refute: truncated quote — 1 quote checked, 0 changed: the quote contains the words "Transfer Molding" that carry the claim.
- self-refute: attribution — 1 row checked, 0 changed: the page is Profile Rubber's own site, not a parent, sister or customer page. Residual risk: "Transfer Molding" on a rubber molder's menu is read as rubber transfer molding by the ruling, which applies the term to this held row.

## check.py
`python3 tasks/process-terms-2026-11-18b/check.py` recomputes from the files at the merge-base (not from build.py's output):
- Vocabulary: the PROCESSES vocabulary export, the §3.1 term set and the validate.py PROCESSES set (read with Python's `ast`, the full literal: 85 terms now, 83 at the base) each equal the base set plus exactly the two new terms; the `rubber_molding` rollup members equal the base members plus exactly `rubber_molding_transfer` (a swapped member fails).
- Data: SITE-000562 is tier C; `sites_OH.csv` has the base row count, unique ids and rows equal to the base rows with only SITE-000562 `processes` changed (one csv-counted changed row against an independent `git diff --numstat` count of 1/1); `site_capabilities` unchanged; `evidence_sites_OH.csv` has exactly base + 1 rows, unique ids, the base rows intact and in order, and the one new row equal in every field to the planned row, with an id above the base maximum across all shards (EVD-397115 at the base) and above the floor.
- Evidence quality: the packet is pinned to the one approved witness (`build.WITNESS`: the Services menu entry naming Transfer Molding, with its exact quote, URL, manifest sha256 and files; any other quote or URL fails, including a true sentence on the compression page). The quote carries the word of the term ("transfer"; a "Compression Molding" quote fails), is found in order in the sha256-checked stored page, and the cited URL and the locality URL are the corpus-manifest entries (url, sha256, files, organization) of the stored pages (swapped URLs fail).
- 19 injected defects in the committed result, each required to be caught: a term not in §3.1 written to `processes`; a write to another column of the same site; a write to SITE-000248; an old term removed; evidence strength raised; an id filling a gap below the maximum; a base evidence row edited; a term missing from the vocabulary export; a new term missing from validate.py; an existing term (`rubber_molding_unspecified`) deleted from validate.py; the rollup line not updated; a rollup member swapped for a plastics subtype; a `site_capabilities` row added; a quote supporting compression molding only; the Codex probe (a true sentence on the real compression page that does not claim the service, with that page's genuine manifest entry, its real page text and a complete, internally consistent evidence row regenerated from the alternate decision): with the approved-witness pin on, the approved-witness failure is the only failure; with the pin disabled the same injection is not caught (0 failures), so it tests the pin and nothing else; swapped cited and locality URLs; an unrelated site row dropped; an evidence row duplicated; an unrelated evidence row dropped.
- `build.py` replayed on disposable copies of the base: a clean build reproduces the committed shard bytes; a replay on the applied shards writes nothing (mtime unchanged); it refuses, before any write and leaving inputs unchanged, a compression-only quote, the Codex probe, swapped URLs, a base with one site and one evidence row removed, a base with a duplicated evidence row, and a tier A row.
`build.py` appends the evidence row with `scripts/shard_io.py append_sorted` (CONTRACT rule 6); the site cell is edited with a same-directory atomic replace (the shared helper only appends).

## Proposed follow-ups (not done here)
1. `composites_spray_up` application to SITE-000248 and the permit-lane sites.
2. A `site_capabilities` row for `rubber_molding_transfer` on SITE-000562 (the CAP rows at this site predate the term; §3.6 maps it to the `rubber_molding` rollup).
3. SITE-000562 `site_type` is `recycling_facility` while its own site describes custom molded rubber products (carried from PR #381; not touched).

## Not checked
No live page was re-fetched (the stored 2026-11-16 page was re-read); the other menu items of the page (Compression Molding, Tooling) are PR #381's and unchanged.
