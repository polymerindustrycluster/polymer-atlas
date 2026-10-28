# Polymer Industry Atlas — Ohio & Northeast Ohio

An open, source-backed database of the polymer / plastics / rubber industry:
companies, plants, materials producers, the value chain, downstream OEMs, and
the ecosystem (universities, associations, nonprofits, economic development)
that supports them.

Built for the Polymer Industry Cluster (PIC), Greater Akron Chamber — and
built to be built *by many hands*: human researchers and multiple AI agent
harnesses (Muse, Claude Code, Codex, Grok, others) contributing through
the same rules, the same schema, and pull requests.

## Why this exists

There is no central database of Ohio's polymer industry. Reported counts
range from ~600 verified core plastics manufacturers (JobsOhio / Shale
Crescent USA study, after manual cleaning of 1,100+ raw hits) to 900+ once
rubber, compounding, materials, and the value chain are included. The count
depends entirely on the definition — so this database **reports every ring
and every unit separately, and never publishes a bare headline number.**

## How the data is organized

- **Canonical data = CSV** in `data/` (flat, diff-able, merge-able in git).
- **SQLite is generated** from the CSVs by `scripts/build_sqlite.py` and
  attached to GitHub Releases. Never edit the .db file directly — binary
  files cannot be merged when five agents work in parallel.
- Three record levels:
  - `data/organizations.csv` — one row per parent organization
  - `data/sites.csv` — one row per physical establishment (plant, HQ, R&D
    center, lab, warehouse). **This is the unit PIC maps and counts.**
  - `data/ecosystem.csv` — Ring 5 entities (schools, associations, EDOs…)
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
human or AI: branch + PR only, claim a task in `tasks/QUEUE.md`, dedupe
before creating, provenance on every record, no licensed-dataset copying,
no personal contact data, tombstone — never delete.

## Licensing — read this before reusing

- Original database content compiled here: **CC BY 4.0** (same model as
  PIC's Evidence Room; scripts MIT).
- **Licensed sources (Plastics News, Rubber News, D&B, etc.) are discovery
  leads only.** Their datasets, rankings, and text are *not* republished
  here. Facts are independently verified against primary/public sources
  and cited to those sources. See `AGENTS.md` §5.

## Status

Scaffold v0.1 — 2026-10-28. Seeded with the 8 primary-source-verified
companies from PIC's Oct 2026 prototype directory plus 3 ecosystem anchors.
Coverage build (PIC-12 counties → Ohio → national tiers) in phases;
see `tasks/QUEUE.md`.
