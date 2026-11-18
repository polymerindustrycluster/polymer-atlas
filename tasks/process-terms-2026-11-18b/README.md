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
`python3 tasks/process-terms-2026-11-18b/check.py` recomputes from the files at the merge-base: both terms absent from the base vocabulary and present in SCHEMA §3.1, validate.py PROCESSES and `vocab.json`; the rollup line carries the rubber term; exactly one site row changed (csv count and an independent `git diff --numstat` line count agree), only `processes`, old values in order plus one appended term, appended term in the vocabulary; no other site (including SITE-000248) or `site_capabilities` row changed; exactly one evidence row added and equal in every field to the planned row; every base evidence row intact; the quote is found in order in the stored page. It then injects 10 defects (a term not in §3.1 written to `processes`; a write to another column of the same site; a write to SITE-000248; an old term removed; evidence strength raised; a base evidence row edited; a term missing from the vocabulary export; a term missing from validate.py; the rollup line not updated; a `site_capabilities` row added) and requires each caught. The legacy `recycling_recovery` value is an old cell value and is not retested.
`build.py` is idempotent (a second run changes nothing) and refuses a non-tier-C site.

## Proposed follow-ups (not done here)
1. `composites_spray_up` application to SITE-000248 and the permit-lane sites.
2. A `site_capabilities` row for `rubber_molding_transfer` on SITE-000562 (the CAP rows at this site predate the term; §3.6 maps it to the `rubber_molding` rollup).
3. SITE-000562 `site_type` is `recycling_facility` while its own site describes custom molded rubber products (carried from PR #381; not touched).

## Not checked
No live page was re-fetched (the stored 2026-11-16 page was re-read); the other menu items of the page (Compression Molding, Tooling) are PR #381's and unchanged.
