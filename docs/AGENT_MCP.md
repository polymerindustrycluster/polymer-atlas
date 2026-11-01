# Atlas MCP server — read-only query access for agent harnesses

`scripts/atlas_mcp_server.py` is a stdio [MCP](https://modelcontextprotocol.io)
server over the generated SQLite database (`build/polymer-atlas.db`). It lets
any MCP-capable harness (Claude Code, Codex, Grok, Muse, Antigravity, …) query
the Atlas with tools instead of grepping 100+ CSV shards.

The CSVs under `data/` stay canonical (AGENTS.md §1). This server reads a
*generated* copy; it can never change the Atlas.

## Setup

1. Build the database (generated, gitignored; re-run whenever `data/` changes):

   ```bash
   python3 scripts/build_sqlite.py
   ```

2. Install the `mcp` Python package (v2.x; the server uses
   `mcp.server.mcpserver.MCPServer`). The tool functions themselves are stdlib
   only, so the unit tests run without it.

3. Register the server.

   **Claude Code** (run from the repo root):

   ```bash
   claude mcp add atlas -- python3 scripts/atlas_mcp_server.py
   ```

   Use absolute paths if you register it at user scope or launch from another
   directory:

   ```bash
   claude mcp add atlas -- python3 /abs/path/polymer-atlas/scripts/atlas_mcp_server.py --db /abs/path/polymer-atlas/build/polymer-atlas.db
   ```

   **Any other stdio MCP harness** — generic config JSON:

   ```json
   {
     "mcpServers": {
       "atlas": {
         "command": "python3",
         "args": [
           "/abs/path/polymer-atlas/scripts/atlas_mcp_server.py",
           "--db", "/abs/path/polymer-atlas/build/polymer-atlas.db"
         ]
       }
     }
   }
   ```

   `--db` is optional (default: `build/polymer-atlas.db` next to `scripts/`).
   If the file is missing the server exits with a message telling you to run
   `scripts/build_sqlite.py`.

## Tools

Every result carries `as_of` (git HEAD short sha + db build time, plus a ready
`cite` string such as `atlas@a3e59e7 db@2026-11-01T11:31:04Z`). Cite it when
you report what you read. `as_of.warning` appears if the db is older than the
latest commit — rebuild before trusting it for current state. Search/list tools
return `total_matching` (the true count) and `returned` (capped by `limit`),
plus a `unit` string naming what a row is.

| Tool | Purpose |
|---|---|
| `search_organizations(query, state=None, ring=None, limit=25, include_ecosystem=False)` | Case-insensitive substring over `legal_name` / `trade_names` (and `website` when the query looks like a domain). `state` = HQ state; `ring` = `ring_primary`. `include_ecosystem=True` adds Ring 5 ecosystem entities. Unit: parent organizations. |
| `get_record(record_id)` | Any `ORG-` / `SITE-` / `PROG-` / `PERSON-` / `EVD-` / `EVT-` / `REL-` / `CAP-` id. Returns the row plus linked context: for an organization its sites, parent / children / successor, evidence rows, relationships, registry links, capability rollup, event participation (ecosystem institutions: programs and public people); for a site its organization, capabilities and evidence; etc. Related lists are capped and report totals. |
| `find_sites(state, county, naics_prefix, process, material, ring, operating_status='active', limit=50)` | Establishment search. `process` / `material` match the `;`-separated multi-value columns by exact **token** (case-insensitive), never substring; `"a;b"` requires all tokens. `ring` uses the site's ring, falling back to its organization's. Pass `operating_status='any'` for all statuses. Unit: sites (establishments). |
| `find_capabilities(term, state=None, limit=50, include_withdrawn=False)` | Search `site_capabilities` (process / material / product_form tags with provenance) joined to site and organization. Unit: capability records (site × term); `distinct_sites_matching` gives sites. |
| `find_programs(query=None, state=None, limit=25)` | Academic / training programs joined to the institution name. |
| `find_people(specialty=None, institution=None, limit=25)` | Professors and federal-lab research staff — public professional facts only (AGENTS.md §6). Returns exactly the `people.csv` columns (name, institution, role, specialties, public profile URL, sources, tier, date) and nothing else; `specialty` is token-matched; `institution` is an `ORG-` id or a name substring. |
| `run_select(sql, limit=200)` | One `SELECT` / `WITH … SELECT` statement; rows capped at `limit` (hard max 1000), 15 s time limit. `has_token(col, 'tok')` is available as an exact `;`-token matcher. |
| `schema_info()` | All tables and views with columns and row counts, pointers to `docs/SCHEMA.md` and `AGENTS.md`, the counting-honesty reminder and the read-only notice. Start here if unsure. |

## Read-only guarantee

Three independent layers:

1. The SQLite file is opened with `file:…?mode=ro` (the OS-level handle is
   read-only) and `PRAGMA query_only=ON`.
2. `run_select` accepts only a single `SELECT` / `WITH` statement — comments
   are stripped, quotes are honoured, and a second statement, `INSERT` /
   `UPDATE` / `DELETE` / DDL / `ATTACH` / `PRAGMA` / `VACUUM` / transaction
   control are rejected before reaching SQLite.
3. `run_select` also runs under a deny-by-default SQLite authorizer that
   permits only SELECT / READ / FUNCTION / RECURSIVE actions, so even a
   CTE-wrapped write cannot execute.

All tools are annotated `readOnlyHint=true`. The server has no tool that
writes data, files, or git state. It reads a generated db, so it also never
touches `data/`.

**Changes to the Atlas do not go through this server.** Follow AGENTS.md: claim
a task in `tasks/QUEUE.md`, work on an `agent/<harness>/<task-slug>` branch,
produce verdict / evidence packets (lanes never edit `data/`; one integrator of
record writes), run `python3 scripts/validate.py`, and open a PR. Derived
fields (`tier1_qualifier`, coordinates) remain hands-off; coordinates are
reference data, never evidence.

## Answers must still cite sources and name units

The server makes reading fast; it does not relax the rules:

- **Name the unit and the filter** for every count (AGENTS.md §7): "Ohio
  establishments (sites) with `operating_status=active`: 1,884", not "1,884
  companies". Organizations, sites, ecosystem entities, programs and people are
  different units — `find_*` results say which unit a `total_matching` counts.
- **Cite** the record id(s), the record's own `sources`, and the `as_of.cite`
  string. A directory-assigned NAICS code is still `directory_assigned`;
  platform or roster categories are discovery leads, not scope evidence
  (AGENTS.md §4).
- **Tiers matter.** Report `verification_tier` alongside a fact; tier `U` /
  `C` rows are unverified or candidate.
- **Don't treat a null as a negative.** A site without `processes` tags is
  simply untagged; it is excluded from process/material filters, not shown to
  lack the capability.
- **People and membership:** only public facts in the CSVs are returned; never
  supplement them from private systems (AGENTS.md §5.1, §6).

## Tests

```bash
python3 -m unittest scripts/test_atlas_mcp_server.py
```

The tests build a tiny fixture database in a temp directory and call the tool
functions directly (no real db required), including rejection of
`INSERT` / `UPDATE` / `DELETE` / `ATTACH` / `PRAGMA` writes and multi-statement
input.
