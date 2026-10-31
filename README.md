# Polymer Industry Atlas — Ohio & Northeast Ohio

> **2026-10-31 source update:** [Reconciliation results](docs/reviews/F5_SOURCE_RECONCILIATION_2026-10-31.md) now reproduce PA/OH state benchmarks, the 1,797-facility ledger and all 2,199 creation-map rows. PIC-12 aggregate cells and seven ledger link-outcome discrepancies remain open. Earlier missing-source statements below are historical.

An open, source-backed database of the polymer / plastics / rubber industry:
companies, plants, materials producers, the value chain, downstream OEMs, and
the ecosystem (universities, associations, nonprofits, economic development)
that supports them.

Built for the Polymer Industry Cluster (PIC), Greater Akron Chamber — and
built to be built *by many hands*: human researchers and multiple AI agent
harnesses (Muse, Claude Code, Codex, Grok, others) contributing through
the same rules, the same schema, and pull requests.

## Why this exists

Reported industry totals depend on geography, year, industrial definition and
whether the unit is a parent organization or a physical establishment. This
Atlas reports those units separately. Historical external estimates are in
`docs/SOURCE_COUNT_RECONCILIATION.md`; they are not current Atlas totals.

## How the data is organized

- **Canonical data = CSV** in `data/` (flat, diff-able, merge-able in git).
- **SQLite is generated** from the CSVs by `scripts/build_sqlite.py` and
  attached to GitHub Releases. Never edit the .db file directly — binary
  files cannot be merged when five agents work in parallel.
- Three record levels:
  - `data/organizations_<TAG>.csv` — one row per parent organization,
    sharded by HQ state (SCHEMA Appendix C)
  - `data/sites_<TAG>.csv` — one row per physical establishment (plant, HQ, R&D
    center, lab, warehouse). **This is the unit PIC maps and counts.**
  - `data/ecosystem.csv` — Ring 5 entities (schools, associations, EDOs…)
- `data/events.csv` — recurring industry event series (SCHEMA §4.12)
- `data/event_participation.csv` — harvested per-edition participation (exhibitor / sponsor / speaker / organizer / host) for held organizations
- Canonical = the shards; merged `organizations_all.csv` / `sites_all.csv`
  exports are generated release artifacts (in `build/`), never committed to `data/`.
- `data/inclusion_log.csv` — every borderline include/exclude decision,
  with the rule cited. This log is how 10 researchers stay consistent.

## The five rings

| Ring | Name | One-line test |
|---|---|---|
| 1 | Core Producers & Processors | Physically transforms resin/rubber, or its headline product *is* plastic/rubber |
| 2 | Materials, Compounding & Formulated Polymers | Sells a material whose functional ingredient is a polymer/resin/elastomer |
| 3 | Value Chain | Tooling, machinery, distribution, recycling, testing/R&D serving polymer firms |
| 4 | Downstream OEMs & Heavy Users | Passes 2 of 3: polymer volume/value, performance dependence, local decision-making |
| 5 | Ecosystem | Named polymer program, or generalist ED/workforce org for an in-scope geography |

Full rules, NAICS map, controlled vocabularies, and entity-resolution
(dedupe) rules: `docs/SCHEMA.md`.

## Verification tiers

Every record carries one: **A** primary source (company site, SEC/SOS/SAM
filing) · **B** authoritative directory (Plastics News, Rubber News,
Thomasnet verified, association/EDO directory) · **C** single secondary
source · **U** unverified candidate (not counted in headline totals).
A record's tier is the tier of its *weakest must-have field*.

## Using the data

```bash
python3 scripts/build_sqlite.py        # builds build/polymer-atlas.db
sqlite3 build/polymer-atlas.db "SELECT legal_name, hq_city FROM organizations WHERE ring_primary=1;"
python3 scripts/validate.py            # run before every PR
```

## Contributing — especially for agents

Read `AGENTS.md` first. It is the binding protocol for every contributor,
human or AI: branch + PR for outside contributions (campaign integration
passes land on `main` only under AGENTS.md §2 campaign mode, with per-push
owner approval), claim a task in `tasks/QUEUE.md`, dedupe before creating,
provenance on every record, no licensed-dataset copying, no personal
contact data, tombstone — never delete.

## Licensing — read this before reusing

- Original database content compiled here: **CC BY 4.0** (same model as
  PIC's Evidence Room; scripts MIT).
- **Licensed sources (Plastics News, Rubber News, D&B, etc.) are discovery
  leads only.** Their datasets, rankings, and text are *not* republished
  here. Facts are independently verified against primary/public sources
  and cited to those sources. See `AGENTS.md` §5.

## Status

**Pinned inventory — 2026-10-30:** source commit
`eceead3a5a59b7a51d13b2ad61d6070e4cfc9a05` (observed 21:32 UTC).
The canonical CSVs contain **4,179 organization rows, 5,770 site rows and
206 ecosystem rows**, all statuses and all verification tiers, including
candidates and tombstones. These are not counts of active companies or unique
ultimate parents. There are also 2,373 registry-link rows and 12,876 evidence rows.

See the [public-count audit](docs/reviews/F5_PUBLIC_COUNTS_2026-10-30.md) for
current state/county cuts, TRI accounting, evidence/matching refreshes, input
fingerprints, and Ohio/Pennsylvania QCEW limitations. Count ratios are not
matched-facility coverage; a missing denominator is not zero.

Historical scaffold v0.1 (2026-10-28) began with 8 prototype organization rows
and 3 ecosystem anchors. The coverage build has since expanded beyond Ohio;
see `tasks/QUEUE.md`. Historical reports retain their dates and must not be
quoted as today's inventory.
