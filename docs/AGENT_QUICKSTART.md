# Agent quickstart — Polymer Atlas

For any harness (Grok, Muse, Dot, Duet, Claude Code, Codex, …) and for humans.
This is a **map, not a substitute**. AGENTS.md is binding and wins every conflict.
Read it in full before your first edit. Read the SCHEMA sections your task touches.
You do not need all 200 KB of SCHEMA.md.

## 1. Orient (5 minutes)

```bash
python3 scripts/validate.py              # must pass on a clean checkout
python3 scripts/build_sqlite.py          # builds build/polymer-atlas.db (generated, never committed)
python3 scripts/atlas.py next-id --all   # every ID namespace and its next free ID
```

- **What exists:** `docs/reviews/FIELD_FILL_PROFILE_2026-11-01.md` (fill rates and gaps),
  `docs/denominators/README.md` (official QCEW establishment counts and coverage
  ratios by state), `tasks/QUEUE.md` (claimable work), `docs/IDEAS_AND_RESOURCES.md`
  (unworked ideas and sources).
- **Allowed values:** `docs/schema/vocab.json`, a derived copy of the validator's
  vocabularies. A value not listed there goes in notes and gets flagged. Never invent one.
- **Query instead of grep:** the read-only MCP server (`docs/AGENT_MCP.md`), or
  `python3 scripts/atlas.py show ORG-000001`.

## 2. The rules that cause real damage when broken

1. **Claim first.** Mark a task in `tasks/QUEUE.md` (`claimed:<your-id> <date>`) on
   your branch. One task = one branch = one PR. **Never push to `main`.** Campaign
   mode belongs only to the orchestrator, with per-push owner approval.
2. **Lanes produce packets; one integrator writes `data/`.** Wave-scale research
   arrives as packet files (CSV + report under `tasks/…`), never as edits to
   `data/`. Small single-purpose data PRs are the only exception.
3. **Dedupe before you create:** `python3 scripts/atlas.py dedupe-check --domain … --name … --street …`.
   It runs AGENTS.md §3 steps 1–5 across all shards; step 5 searches `sites.site_name` (a `- <city>` suffix is ignored). Step 2 also matches a name written in parentheses (`(formerly X)`, `(fka X)`, `(f/k/a X)`, `(previously X)`, `(dba X)`). When in doubt, **don't merge**:
   create or link the record and flag it.
4. **IDs come from the tree-wide maximum, never a gap:** `python3 scripts/atlas.py next-id ORG`.
   Organization and ecosystem rows share the `ORG-` namespace. Only the integrator
   allocates IDs. Packets leave them blank.
5. **No naked facts.** Every record has ≥1 source, a tier and `last_verified`. A
   create integrates only with evidence rows (`data/evidence.csv`, SCHEMA §4.13)
   for its existence and scope claims.
6. **NAICS is never a company fact by default.** It always carries
   `naics_primary_source_type` (company_disclosed | government_filing |
   directory_assigned | researcher_inferred) plus confidence high | medium | low.
7. **Sites belong to the operator** (who runs the process), never the brand owner.
   Never push parent facts (NAICS, ring, headcount, processes) down to a site
   without a site source.
8. **Verdicts are exactly:** VERIFIED · REJECT (with the deciding fact) ·
   STILL_UNCERTAIN (with the fact that would settle it) · DUPLICATE_OF (with a chain
   that ends at a held record). Spend at most ~6 primary fetches per organization.
   **A failed fetch (403, timeout, bot wall) is never evidence of anything.**
9. **Status changes need dated evidence.** A WARN notice alone settles nothing. Run
   the Form 5500 check before any closure REJECT. Never delete a record. Tombstone it.
10. **Licensed sources** (Plastics News, Rubber News, D&B, Data Axle, ZoomInfo…)
    are discovery leads only. Nothing from them enters the repo. Cite the
    primary/public source you verified against.
11. **No personal contact data, ever.** People records are professors and
    federal-lab research staff, with public professional facts only. **The PIC CRM
    is never a source.** The PIC membership flag comes only from the public PIC
    website list.
12. **Counts name their unit and filter** ("Ohio establishments, tiers A–C, NAICS 326").
    Organizations ≠ sites ≠ companies. A count ratio is not matched coverage.
13. **Scope, ring and vocabulary questions are owner rulings.** Write them up as
    battery items with a recommendation. Don't settle them in a PR.
14. **Never edit or commit** `build/`, the `.db`, or merged `*_all.csv` exports.
    Derived fields (`tier1_qualifier`, coordinates) are hands-off. Coordinates are
    never evidence. The integrator refreshes `tier1_qualifier` with
    `scripts/derive_tier1.py` (check mode is read-only and safe for anyone).
15. **Only `data/`, `docs/`, `scripts/`, `tasks/` travel.** Nothing from local staging gets committed.

## 3. Before you open a PR

```bash
python3 scripts/validate.py                       # must print "OK — validation passed."
python3 scripts/check_row_loss.py --base origin/main  # no keyed row may vanish; declare intended removals in REMOVALS.csv
python3 scripts/export_vocab.py --check           # if you touched validator vocabularies
python3 -m unittest discover -s scripts -p 'test_*.py'   # all tests (~12 s)
```

- **Grandfathered debt.** The validator warns about rows listed in
  `scripts/validate_debt_baseline.json` (V-45..V-51). Any *new* violation is an
  error. Never add IDs to the baseline to get past it. Fixing a baselined row
  shrinks the list. See `tasks/validator-debt-2026-11-01/`.
- **PR description:** state the task claimed, sources used, rows added or
  changed, the count at each tier, the dedupe searches you ran, and any
  `inclusion_log.csv` entries (AGENTS.md §2 rule 6).
- **Check for overlap.** Look at open draft PRs first: they may hold claims. Some
  are stale; check the QUEUE line for the PR's status.

## 4. Where to look in SCHEMA.md (grep the heading)

| Need | Section |
|---|---|
| Is it in scope? Which ring? | `## 1. Ring Model`, `### Edge Cases — Decided`, owner-ruling blocks |
| NAICS rules | `### 2.1 Critical provenance rule` |
| Vocabularies (human-readable) | `## 3.` (or `docs/schema/vocab.json`) |
| Org / site / ecosystem fields | `### 4.4`, `### 4.5`, `### 4.6` |
| Evidence rows and tier ceilings | `### 4.13` |
| Relationships (generated, not authored) | `### 4.14` |
| Dedupe and entity resolution | `## 5.` |
| Which shard a record goes in | `## Appendix C` (or `atlas.py shard-of`) |

Shared own-site cache and quote check: `python3 scripts/site_corpus.py crawl` or `python3 scripts/site_corpus.py rawcheck URL QUOTE` (`--cache-dir` outside the repo); receipts/index and per-group coverage stay in controller storage. Quote presence is not claim support; `wrong_page` and `unfetchable` require review.

For local keyed CSV merges, run `scripts/setup_merge_driver.sh` in each checkout. It registers a Git merge driver in local configuration and attributes; conflicting edits, changed headers, and deletions still require manual resolution and the row-loss guard remains mandatory.
