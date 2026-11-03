#!/usr/bin/env python3
"""Read-only MCP server (stdio) over the generated Polymer Atlas SQLite database.

The CSVs under data/ are canonical; build/polymer-atlas.db is a generated
artifact (scripts/build_sqlite.py).  This server only ever READS that database:
the connection is opened with ``mode=ro`` + ``PRAGMA query_only=ON``, and the
free-form ``run_select`` tool additionally runs under a SQLite authorizer that
permits nothing but SELECT/READ/FUNCTION.  Changes to the Atlas go through the
AGENTS.md PR / packet workflow, never through this server.

Usage:
    python3 scripts/atlas_mcp_server.py [--db build/polymer-atlas.db]

Register with Claude Code:
    claude mcp add atlas -- python3 scripts/atlas_mcp_server.py

Requires the ``mcp`` package (v2.x: ``mcp.server.mcpserver.MCPServer``) only to
*serve*; the tool functions themselves are plain stdlib and are unit-tested
without it (scripts/test_atlas_mcp_server.py).  stdout carries the MCP
protocol: nothing in this file prints to stdout.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as _dt
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "build" / "polymer-atlas.db"

MAX_RUN_SELECT_ROWS = 1000
RUN_SELECT_TIMEOUT_S = 15.0
MAX_LIMIT = 500

COUNTING_REMINDER = (
    "AGENTS.md §7 (counting honesty): any count you state must name its unit "
    "and filter, e.g. 'Ohio establishments (sites) with operating_status=active', "
    "'Parents with an Ohio footprint', 'Ring 1-2 establishments in PIC-18'. "
    "A bare '900 companies' is a protocol violation. Organizations, sites, "
    "ecosystem entities, programs and people are different units."
)
READ_ONLY_REMINDER = (
    "This server is strictly read-only (SQLite mode=ro, query_only=ON, authorizer "
    "on run_select). Changes to the Atlas go through AGENTS.md's PR/packet "
    "workflow: lanes produce verdict/evidence packets, one integrator writes data/. "
    "Cite the record id, its `sources`, and `as_of` for anything you report."
)
DOC_POINTERS = {
    "schema": "docs/SCHEMA.md (rings, vocabularies, field rules, tiers)",
    "protocol": "AGENTS.md (binding contributor protocol)",
    "queue": "tasks/QUEUE.md",
    "rebuild_db": "python3 scripts/build_sqlite.py  (regenerates build/polymer-atlas.db from data/*.csv)",
}

# Tables an id prefix can resolve to (whitelist -> never interpolate user text).
_ORG_TABLES = ("organizations", "ecosystem")

# People are public professional facts only; return exactly these columns.
PEOPLE_PUBLIC_COLUMNS = (
    "person_id", "full_name", "institution_org_id", "program_org_id", "role",
    "role_as_published", "research_specialties", "public_profile_url",
    "sources", "verification_tier", "last_verified",
)

_DB_PATH: Path = DEFAULT_DB


try:  # mcp 2.x: a ToolError reaches the client verbatim as an isError result
    from mcp.server.mcpserver.exceptions import ToolError as _ToolErrorBase
except ImportError:  # mcp absent/older: the tool functions still work standalone
    _ToolErrorBase = Exception


class AtlasError(ValueError, _ToolErrorBase):
    """User-facing error (bad argument, missing db, rejected SQL).

    Subclasses mcp's ToolError when available so its message is shown to the
    agent (an arbitrary exception's text is withheld by the SDK as a "crash")."""


# --------------------------------------------------------------------------
# Connection / provenance helpers
# --------------------------------------------------------------------------

def configure(db_path: str | Path) -> None:
    """Point the tool functions at a database file (used by main() and tests)."""
    global _DB_PATH
    _DB_PATH = Path(db_path)


def _has_token(col: Any, token: Any) -> int:
    """SQL helper: does the ';'-separated multi-value `col` contain `token`?

    Exact token match (case-insensitive, whitespace-trimmed) -- never substring.
    `token` may itself be ';'-separated, in which case ALL tokens must be present.
    """
    if col is None or token is None:
        return 0
    have = {t.strip().lower() for t in str(col).split(";") if t.strip()}
    want = [t.strip().lower() for t in str(token).split(";") if t.strip()]
    return int(bool(want) and all(t in have for t in want))


def _connect() -> sqlite3.Connection:
    if not _DB_PATH.exists():
        raise AtlasError(
            f"Atlas database not found at {_DB_PATH}. Run "
            "`python3 scripts/build_sqlite.py` first (it builds build/polymer-atlas.db "
            "from data/*.csv), or pass --db."
        )
    uri = f"file:{_DB_PATH.resolve().as_posix()}?mode=ro"
    con = sqlite3.connect(uri, uri=True, check_same_thread=False)
    con.execute("PRAGMA query_only=ON")
    con.row_factory = sqlite3.Row
    con.create_function("has_token", 2, _has_token, deterministic=True)
    return con


@contextlib.contextmanager
def _session():
    con = _connect()
    try:
        yield con
    finally:
        con.close()


def _git_head() -> tuple[str, int | None]:
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%h %ct"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout.split()
        return out[0], int(out[1])
    except Exception:  # not a git checkout, git missing, timeout...
        return "unknown", None


def as_of() -> dict[str, Any]:
    """Provenance stamp: git HEAD short sha + db mtime, for citing state read."""
    sha, head_ts = _git_head()
    try:
        mtime = _DB_PATH.stat().st_mtime
        built = _dt.datetime.fromtimestamp(mtime, _dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except OSError:
        mtime, built = None, None
    stamp: dict[str, Any] = {
        "git_head": sha,
        "db_built_utc": built,
        "cite": f"atlas@{sha} db@{built}",
        "note": "The db reflects the CSVs at build time, which may differ from git HEAD.",
    }
    if mtime is not None and head_ts is not None and mtime < head_ts:
        stamp["warning"] = (
            "db is older than the latest git commit; rebuild with "
            "`python3 scripts/build_sqlite.py` if you need current data."
        )
    return stamp


def _wrap(result: dict[str, Any]) -> dict[str, Any]:
    result["as_of"] = as_of()
    return result


def _rows(con: sqlite3.Connection, sql: str, params: tuple | list = ()) -> list[dict[str, Any]]:
    return [dict(r) for r in con.execute(sql, params).fetchall()]


def _one(con: sqlite3.Connection, sql: str, params: tuple | list = ()) -> dict[str, Any] | None:
    r = con.execute(sql, params).fetchone()
    return dict(r) if r else None


def _like_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _limit(n: Any, default: int, cap: int = MAX_LIMIT) -> int:
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = default
    return max(1, min(n, cap))


def _s(v: Any) -> str | None:
    """Normalize an optional string filter: strip; empty -> None."""
    if v is None:
        return None
    v = str(v).strip()
    return v or None


def _table_exists(con: sqlite3.Connection, name: str) -> bool:
    return con.execute(
        "SELECT 1 FROM sqlite_master WHERE name=? AND type IN ('table','view')", (name,)
    ).fetchone() is not None


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------

def search_organizations(
    query: str,
    state: str | None = None,
    ring: str | int | None = None,
    limit: int = 25,
    include_ecosystem: bool = False,
) -> dict[str, Any]:
    """Search parent organizations by legal_name / trade_names (case-insensitive
    substring); a query that looks like a domain (contains '.', no spaces) also
    matches `website`. `state` filters HQ state (2-letter); `ring` filters
    ring_primary ('1'-'5'). Set include_ecosystem=True to also search Ring 5
    ecosystem entities (schools, associations, EDOs). Returns one row per
    ORGANIZATION (parent), not per site."""
    q = _s(query)
    if not q:
        raise AtlasError("query is required")
    state, ring_s = _s(state), _s(ring)
    limit = _limit(limit, 25)
    pat = f"%{_like_escape(q.lower())}%"
    domainish = "." in q and " " not in q

    def build(table: str) -> tuple[str, list[Any]]:
        has_trade = table == "organizations"
        cols = (
            "org_id, legal_name, " + ("trade_names" if has_trade else "NULL AS trade_names")
            + ", city AS hq_city, state AS hq_state, '5' AS ring_primary, "
              "verification_tier, status, website, NULL AS parent_org_id"
        ) if table == "ecosystem" else (
            "org_id, legal_name, trade_names, hq_city, hq_state, ring_primary, "
            "verification_tier, status, website, parent_org_id"
        )
        conds = ["(lower(legal_name) LIKE ? ESCAPE '\\'"]
        params: list[Any] = [pat]
        if has_trade:
            conds[0] += " OR lower(trade_names) LIKE ? ESCAPE '\\'"
            params.append(pat)
        if domainish:
            conds[0] += " OR lower(website) LIKE ? ESCAPE '\\'"
            params.append(pat)
        conds[0] += ")"
        if state:
            conds.append(("hq_state" if has_trade else "state") + " = ?")
            params.append(state.upper())
        if ring_s and has_trade:
            conds.append("ring_primary = ?")
            params.append(ring_s)
        elif ring_s and ring_s != "5":
            conds.append("0")  # ecosystem entities are Ring 5 only
        sql = f"SELECT '{table}' AS record_table, {cols} FROM {table} WHERE " + " AND ".join(conds)
        return sql, params

    with _session() as con:
        sql, params = build("organizations")
        if include_ecosystem and _table_exists(con, "ecosystem"):
            sql2, params2 = build("ecosystem")
            sql, params = f"{sql} UNION ALL {sql2}", params + params2
        qlow = q.lower()
        full = (
            f"SELECT * FROM ({sql}) ORDER BY (lower(legal_name) = ?) DESC, "
            "(lower(legal_name) LIKE ? ESCAPE '\\') DESC, legal_name, org_id"
        )
        total = con.execute(f"SELECT count(*) FROM ({sql})", params).fetchone()[0]
        rows = _rows(con, full + " LIMIT ?", params + [qlow, f"{_like_escape(qlow)}%", limit])
    return _wrap({
        "unit": "organizations (parent records; not sites)" + (" + ecosystem entities" if include_ecosystem else ""),
        "filters": {"query": q, "state": state, "ring_primary": ring_s, "include_ecosystem": include_ecosystem},
        "total_matching": total,
        "returned": len(rows),
        "rows": rows,
    })


# id prefix -> (table, id column)
_ID_TABLES = {
    "SITE-": ("sites", "site_id"),
    "PROG-": ("programs", "program_id"),
    "PERSON-": ("people", "person_id"),
    "EVD-": ("evidence", "evidence_id"),
    "EVT-": ("events", "event_id"),
    "REL-": ("relationships", "relationship_id"),
    "CAP-": ("site_capabilities", "capability_id"),
}
_ORG_SUMMARY_COLS = "org_id, legal_name, hq_city, hq_state, ring_primary, verification_tier, status, website"
_EVIDENCE_CAP = 100
_CHILD_CAP = 200


def _org_summary(con: sqlite3.Connection, org_id: str | None) -> dict[str, Any] | None:
    if not org_id:
        return None
    r = _one(con, f"SELECT 'organizations' AS record_table, {_ORG_SUMMARY_COLS} FROM organizations WHERE org_id=?", (org_id,))
    if r:
        return r
    return _one(
        con,
        "SELECT 'ecosystem' AS record_table, org_id, legal_name, city AS hq_city, state AS hq_state, "
        "'5' AS ring_primary, verification_tier, status, website FROM ecosystem WHERE org_id=?",
        (org_id,),
    )


def _evidence_for(con: sqlite3.Connection, table: str, record_id: str) -> dict[str, Any]:
    if not _table_exists(con, "evidence"):
        return {"total": 0, "rows": []}
    where = "record_table=? AND record_id=?"
    total = con.execute(f"SELECT count(*) FROM evidence WHERE {where}", (table, record_id)).fetchone()[0]
    rows = _rows(con, f"SELECT * FROM evidence WHERE {where} ORDER BY evidence_id LIMIT ?", (table, record_id, _EVIDENCE_CAP))
    return {"total": total, "returned": len(rows), "rows": rows}


def _people_rows(con: sqlite3.Connection, where: str, params: list[Any], limit: int) -> list[dict[str, Any]]:
    cols = ", ".join(f"p.{c}" for c in PEOPLE_PUBLIC_COLUMNS)
    return _rows(
        con,
        f"SELECT {cols} FROM people p WHERE {where} ORDER BY p.person_id LIMIT ?",
        params + [limit],
    )


def get_record(record_id: str) -> dict[str, Any]:
    """Fetch one record by id -- ORG-######, SITE-######, PROG-######,
    PERSON-######, EVD-######, EVT-######, REL-######, or CAP-###### -- with
    its linked context: for organizations the sites, parent/children/successor,
    evidence rows, relationships, registry links, capability rollup, programs
    and public people (ecosystem institutions); for sites the operating org,
    capabilities and evidence; etc. Related lists are capped and report totals."""
    rid = _s(record_id)
    if not rid:
        raise AtlasError("record_id is required")
    rid = rid.upper()
    with _session() as con:
        if rid.startswith("ORG-"):
            out = _get_org(con, rid)
        else:
            prefix = next((p for p in _ID_TABLES if rid.startswith(p)), None)
            if prefix is None:
                raise AtlasError(
                    "Unrecognized id. Expected ORG-, SITE-, PROG-, PERSON-, EVD-, EVT-, REL- or CAP- prefix."
                )
            table, idcol = _ID_TABLES[prefix]
            if not _table_exists(con, table):
                raise AtlasError(f"table {table!r} is not present in this database")
            out = _get_other(con, table, idcol, rid)
    return _wrap(out)


def _get_org(con: sqlite3.Connection, rid: str) -> dict[str, Any]:
    for table in _ORG_TABLES:
        if not _table_exists(con, table):
            continue
        row = _one(con, f"SELECT * FROM {table} WHERE org_id=?", (rid,))
        if row:
            break
    else:
        raise AtlasError(f"{rid} not found in organizations or ecosystem")
    out: dict[str, Any] = {"record_table": table, "record": row}
    if table == "organizations":
        out["parent"] = _org_summary(con, row.get("parent_org_id"))
        out["successor"] = _org_summary(con, row.get("successor_org_id"))
        kids = _rows(con, f"SELECT {_ORG_SUMMARY_COLS} FROM organizations WHERE parent_org_id=? ORDER BY org_id LIMIT ?", (rid, _CHILD_CAP))
        out["children"] = kids
        n_sites = con.execute("SELECT count(*) FROM sites WHERE org_id=?", (rid,)).fetchone()[0]
        out["sites_total"] = n_sites
        out["sites"] = _rows(
            con,
            "SELECT site_id, site_name, site_type, street_address, city, state, county, zip, "
            "ring_primary, naics_primary, operating_status, verification_tier "
            "FROM sites WHERE org_id=? ORDER BY site_id LIMIT ?", (rid, _CHILD_CAP))
        if _table_exists(con, "org_capability_rollup"):
            out["capability_rollup"] = _rows(
                con, "SELECT capability_type, term, site_count, latest_observed_date "
                     "FROM org_capability_rollup WHERE org_id=? ORDER BY capability_type, term", (rid,))
    else:  # ecosystem
        out["parent_institution"] = _org_summary(con, row.get("parent_institution_org_id"))
        if _table_exists(con, "programs"):
            out["programs"] = _rows(
                con, "SELECT program_id, program_name, program_type, level, status, verification_tier "
                     "FROM programs WHERE institution_org_id=? ORDER BY program_id LIMIT ?", (rid, _CHILD_CAP))
        if _table_exists(con, "people"):
            out["people_total"] = con.execute(
                "SELECT count(*) FROM people WHERE institution_org_id=?", (rid,)).fetchone()[0]
            out["people"] = _people_rows(con, "p.institution_org_id=?", [rid], _CHILD_CAP)
    out["evidence"] = _evidence_for(con, table, rid)
    if _table_exists(con, "relationships"):
        out["relationships"] = _rows(
            con,
            "SELECT relationship_id, from_org_id, relationship_type, to_org_id, effective_from, "
            "effective_to, basis, source_ref FROM relationships "
            "WHERE from_org_id=? OR to_org_id=? ORDER BY relationship_id LIMIT ?",
            (rid, rid, _CHILD_CAP))
    if _table_exists(con, "registry_links"):
        out["registry_links"] = _rows(
            con, "SELECT registry, registry_id, match_basis, as_of FROM registry_links "
                 "WHERE org_id=? ORDER BY registry, registry_id", (rid,))
    if _table_exists(con, "event_participation"):
        out["event_participation"] = _rows(
            con, "SELECT participation_id, event_id, edition_year, role, verification_tier "
                 "FROM event_participation WHERE org_id=? ORDER BY edition_year DESC, participation_id LIMIT ?",
            (rid, _CHILD_CAP))
    return out


def _get_other(con: sqlite3.Connection, table: str, idcol: str, rid: str) -> dict[str, Any]:
    if table == "people":  # public professional facts only: explicit column list
        row = _one(con, f"SELECT {', '.join(PEOPLE_PUBLIC_COLUMNS)} FROM people WHERE person_id=?", (rid,))
    else:
        row = _one(con, f"SELECT * FROM {table} WHERE {idcol}=?", (rid,))
    if not row:
        raise AtlasError(f"{rid} not found in {table}")
    out: dict[str, Any] = {"record_table": table, "record": row}
    if table == "sites":
        out["organization"] = _org_summary(con, row.get("org_id"))
        if _table_exists(con, "site_capabilities"):
            out["capabilities"] = _rows(
                con, "SELECT capability_id, capability_type, term, provenance, source_ref, observed_date, withdrawn_date "
                     "FROM site_capabilities WHERE site_id=? ORDER BY capability_type, term", (rid,))
    elif table == "programs":
        out["institution"] = _org_summary(con, row.get("institution_org_id"))
        if _table_exists(con, "people"):
            out["people"] = _people_rows(con, "p.program_org_id=?", [rid], _CHILD_CAP)
    elif table == "people":
        out["institution"] = _org_summary(con, row.get("institution_org_id"))
        if row.get("program_org_id") and _table_exists(con, "programs"):
            out["program"] = _one(con, "SELECT program_id, program_name, program_type, level, status FROM programs WHERE program_id=?",
                                  (row["program_org_id"],))
    elif table == "evidence":
        rt, rr = row.get("record_table"), row.get("record_id")
        if rt in _ORG_TABLES:
            out["subject"] = _org_summary(con, rr)
        elif rt == "sites":
            out["subject"] = _one(con, "SELECT site_id, org_id, site_name, city, state, operating_status FROM sites WHERE site_id=?", (rr,))
        elif rt == "programs":
            out["subject"] = _one(con, "SELECT program_id, institution_org_id, program_name FROM programs WHERE program_id=?", (rr,))
    elif table == "events":
        if _table_exists(con, "event_participation"):
            out["participation_total"] = con.execute(
                "SELECT count(*) FROM event_participation WHERE event_id=?", (rid,)).fetchone()[0]
        out["organizer"] = _org_summary(con, row.get("organizer_org_id"))
    elif table == "relationships":
        out["from_org"] = _org_summary(con, row.get("from_org_id"))
        out["to_org"] = _org_summary(con, row.get("to_org_id"))
    elif table == "site_capabilities":
        out["site"] = _one(con, "SELECT site_id, org_id, site_name, city, state, operating_status FROM sites WHERE site_id=?", (row.get("site_id"),))
        out["organization"] = _org_summary(con, row.get("org_id"))
    if table in ("sites", "programs", "people"):
        out["evidence"] = _evidence_for(con, table, rid)
    return out


def find_sites(
    state: str | None = None,
    county: str | None = None,
    naics_prefix: str | None = None,
    process: str | None = None,
    material: str | None = None,
    ring: str | int | None = None,
    operating_status: str | None = "active",
    limit: int = 50,
) -> dict[str, Any]:
    """Find establishments (SITES -- the unit PIC maps and counts). `state`
    2-letter; `county` name (case-insensitive, 'County' suffix optional);
    `naics_prefix` digits (site naics_primary starts with it); `process` /
    `material` match the ';'-separated multi-value columns by exact TOKEN
    (case-insensitive), never substring -- pass 'a;b' to require ALL tokens;
    `ring` matches the site's ring_primary, falling back to the operating org's
    when the site's is blank; `operating_status` defaults to 'active' (pass
    'any' or null for all statuses). Only tags present at site level match;
    a site with no process/material tags is never returned for those filters.
    Returns total_matching (the honest count, unit = sites) plus up to `limit` rows."""
    state, county = _s(state), _s(county)
    naics, process, material = _s(naics_prefix), _s(process), _s(material)
    ring_s, status = _s(ring), _s(operating_status)
    limit = _limit(limit, 50)
    conds, params = [], []
    if state:
        conds.append("s.state = ?"); params.append(state.upper())
    if county:
        c = re.sub(r"\s+county$", "", county, flags=re.I).lower()
        conds.append("lower(s.county) = ?"); params.append(c)
    if naics:
        if not naics.isdigit():
            raise AtlasError("naics_prefix must be digits only")
        conds.append("s.naics_primary LIKE ?"); params.append(naics + "%")
    if process:
        conds.append("has_token(s.processes, ?)"); params.append(process)
    if material:
        conds.append("has_token(s.materials, ?)"); params.append(material)
    if ring_s:
        conds.append("COALESCE(s.ring_primary, o.ring_primary) = ?"); params.append(ring_s)
    if status and status.lower() != "any":
        conds.append("s.operating_status = ?"); params.append(status)
    where = (" WHERE " + " AND ".join(conds)) if conds else ""
    frm = "FROM sites s LEFT JOIN organizations o ON o.org_id = s.org_id"
    with _session() as con:
        total = con.execute(f"SELECT count(*) {frm}{where}", params).fetchone()[0]
        rows = _rows(
            con,
            "SELECT s.site_id, s.org_id, o.legal_name AS org_name, s.site_name, s.site_type, "
            "s.street_address, s.city, s.state, s.county, s.naics_primary, "
            "COALESCE(s.ring_primary, o.ring_primary) AS ring_primary, s.processes, s.materials, "
            "s.operating_status, s.verification_tier "
            f"{frm}{where} ORDER BY s.state, s.county, s.site_id LIMIT ?",
            params + [limit])
    return _wrap({
        "unit": "sites (establishments; not companies)",
        "filters": {"state": state, "county": county, "naics_prefix": naics, "process": process,
                    "material": material, "ring": ring_s, "operating_status": status},
        "total_matching": total,
        "returned": len(rows),
        "rows": rows,
    })


def find_capabilities(
    term: str,
    state: str | None = None,
    limit: int = 50,
    include_withdrawn: bool = False,
) -> dict[str, Any]:
    """Search site-level capability records (site_capabilities: process /
    material / product_form tags with provenance) by term (case-insensitive
    substring of the controlled `term`), joined to the site and operating
    organization. `state` filters the site's state. Withdrawn capabilities are
    excluded unless include_withdrawn=True. Unit = capability records (one per
    site x term), so distinct-site counts need run_select."""
    t = _s(term)
    if not t:
        raise AtlasError("term is required")
    state = _s(state)
    limit = _limit(limit, 50)
    conds = ["lower(c.term) LIKE ? ESCAPE '\\'"]
    params: list[Any] = [f"%{_like_escape(t.lower())}%"]
    if state:
        conds.append("s.state = ?"); params.append(state.upper())
    if not include_withdrawn:
        conds.append("c.withdrawn_date IS NULL")
    where = " WHERE " + " AND ".join(conds)
    frm = ("FROM site_capabilities c LEFT JOIN sites s ON s.site_id = c.site_id "
           "LEFT JOIN organizations o ON o.org_id = COALESCE(c.org_id, s.org_id)")
    with _session() as con:
        total = con.execute(f"SELECT count(*) {frm}{where}", params).fetchone()[0]
        distinct_sites = con.execute(f"SELECT count(DISTINCT c.site_id) {frm}{where}", params).fetchone()[0]
        rows = _rows(
            con,
            "SELECT c.capability_id, c.capability_type, c.term, c.provenance, c.source_ref, c.observed_date, "
            "c.withdrawn_date, c.site_id, s.site_name, s.city, s.state, s.county, s.operating_status, "
            "COALESCE(c.org_id, s.org_id) AS org_id, o.legal_name AS org_name "
            f"{frm}{where} ORDER BY s.state, c.term, c.capability_id LIMIT ?",
            params + [limit])
    return _wrap({
        "unit": "capability records (site x term); distinct_sites counts sites",
        "filters": {"term": t, "state": state, "include_withdrawn": include_withdrawn},
        "total_matching": total,
        "distinct_sites_matching": distinct_sites,
        "returned": len(rows),
        "rows": rows,
    })


def find_programs(query: str | None = None, state: str | None = None, limit: int = 25) -> dict[str, Any]:
    """Find academic / training programs (programs table, joined to the
    institution's name). `query` is a case-insensitive substring over program
    name, department, description, research areas, specialty processes /
    materials and institution name. `state` filters the program's state."""
    q, state = _s(query), _s(state)
    limit = _limit(limit, 25)
    conds, params = [], []
    if q:
        pat = f"%{_like_escape(q.lower())}%"
        fields = ["program_name", "unit_department", "description_1line", "research_areas",
                  "specialty_processes", "specialty_materials", "institution_name"]
        conds.append("(" + " OR ".join(f"lower(coalesce({f}, '')) LIKE ? ESCAPE '\\'" for f in fields) + ")")
        params += [pat] * len(fields)
    if state:
        conds.append("state = ?"); params.append(state.upper())
    where = (" WHERE " + " AND ".join(conds)) if conds else ""
    with _session() as con:
        total = con.execute(f"SELECT count(*) FROM institution_programs{where}", params).fetchone()[0]
        rows = _rows(
            con,
            "SELECT program_id, institution_org_id, institution_name, program_name, program_type, level, "
            "credential_types, unit_department, city, state, county, specialty_processes, specialty_materials, "
            "research_areas, admissions_status, status, url, sources, verification_tier, last_verified "
            f"FROM institution_programs{where} ORDER BY state, institution_name, program_name LIMIT ?",
            params + [limit])
    return _wrap({
        "unit": "programs (not institutions, not people)",
        "filters": {"query": q, "state": state},
        "total_matching": total, "returned": len(rows), "rows": rows,
    })


def find_people(specialty: str | None = None, institution: str | None = None, limit: int = 25) -> dict[str, Any]:
    """Find professors / federal-lab research staff. Public professional facts
    only (name, institution, role, specialties, public profile URL, sources) --
    exactly the people.csv columns, nothing else. `specialty` matches the
    ';'-separated research_specialties by exact token ('a;b' = all required);
    `institution` is an ORG id (exact) or a case-insensitive substring of the
    institution name. Unit = people records."""
    spec, inst = _s(specialty), _s(institution)
    limit = _limit(limit, 25)
    conds, params = [], []
    if spec:
        conds.append("has_token(p.research_specialties, ?)"); params.append(spec)
    if inst:
        if inst.upper().startswith("ORG-"):
            conds.append("p.institution_org_id = ?"); params.append(inst.upper())
        else:
            conds.append("lower(coalesce(i.legal_name, '')) LIKE ? ESCAPE '\\'")
            params.append(f"%{_like_escape(inst.lower())}%")
    where = (" WHERE " + " AND ".join(conds)) if conds else ""
    frm = ("FROM people p LEFT JOIN (SELECT org_id, legal_name FROM organizations "
           "UNION ALL SELECT org_id, legal_name FROM ecosystem) i ON i.org_id = p.institution_org_id")
    cols = ", ".join(f"p.{c}" for c in PEOPLE_PUBLIC_COLUMNS)
    with _session() as con:
        total = con.execute(f"SELECT count(*) {frm}{where}", params).fetchone()[0]
        rows = _rows(con, f"SELECT {cols}, i.legal_name AS institution_name {frm}{where} "
                          "ORDER BY p.institution_org_id, p.full_name LIMIT ?", params + [limit])
    return _wrap({
        "unit": "people records (public professional facts only)",
        "filters": {"specialty": spec, "institution": inst},
        "total_matching": total, "returned": len(rows), "rows": rows,
    })


# ---- run_select -----------------------------------------------------------

def _strip_sql(sql: str) -> tuple[str, bool]:
    """Remove comments; return (sql_without_comments, has_extra_statement).

    Walks the text honouring '...', "...", `...` and [...] quoting, so a ';'
    inside a literal is not a statement separator.  A trailing ';' (plus
    whitespace/comments) is allowed; any other ';' means multiple statements.
    """
    out: list[str] = []
    i, n = 0, len(sql)
    seen_semicolon = False
    extra = False
    while i < n:
        ch = sql[i]
        if sql.startswith("--", i):
            j = sql.find("\n", i)
            i = n if j < 0 else j + 1
            out.append(" ")
            continue
        if sql.startswith("/*", i):
            j = sql.find("*/", i + 2)
            i = n if j < 0 else j + 2
            out.append(" ")
            continue
        if ch in ("'", '"', "`", "["):
            close = "]" if ch == "[" else ch
            j = i + 1
            while j < n:
                if sql[j] == close:
                    if close != "]" and sql.startswith(close * 2, j):  # doubled quote escape
                        j += 2
                        continue
                    break
                j += 1
            if seen_semicolon:
                extra = True
            out.append(sql[i:j + 1])
            i = j + 1
            continue
        if ch == ";":
            seen_semicolon = True
            out.append(" ")
            i += 1
            continue
        if seen_semicolon and not ch.isspace():
            extra = True
        out.append(ch)
        i += 1
    return "".join(out).strip(), extra


_ALLOWED_AUTH = {
    sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE,
}


def _authorizer(action: int, a1: Any, a2: Any, db: Any, trigger: Any) -> int:
    return sqlite3.SQLITE_OK if action in _ALLOWED_AUTH else sqlite3.SQLITE_DENY


def run_select(sql: str, limit: int = 200) -> dict[str, Any]:
    """Run ONE read-only SELECT (or WITH ... SELECT) statement against the
    Atlas db and return up to `limit` rows (hard cap 1000). Anything else --
    INSERT/UPDATE/DELETE/DDL/ATTACH/PRAGMA, multiple statements -- is rejected
    (and the connection itself is read-only with a deny-by-default authorizer).
    Tables/views: see schema_info(). Helper: has_token(col, 'tok') = exact token
    match in a ';'-separated column. Remember AGENTS.md §7: name unit + filter
    for any count you report."""
    if not isinstance(sql, str) or not sql.strip():
        raise AtlasError("sql is required")
    cleaned, extra = _strip_sql(sql)
    if extra:
        raise AtlasError("Only a single SQL statement is allowed.")
    if not cleaned:
        raise AtlasError("Empty statement.")
    first = re.match(r"[A-Za-z]+", cleaned)
    if not first or first.group(0).upper() not in ("SELECT", "WITH"):
        raise AtlasError("Only SELECT / WITH ... SELECT statements are allowed.")
    limit = _limit(limit, 200, MAX_RUN_SELECT_ROWS)
    deadline = time.monotonic() + RUN_SELECT_TIMEOUT_S
    con = _connect()
    try:
        con.set_authorizer(_authorizer)
        con.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10000)
        try:
            cur = con.execute(cleaned)
            if cur.description is None:
                raise AtlasError("Statement returned no result set; only SELECT is allowed.")
            cols = [d[0] for d in cur.description]
            fetched = cur.fetchmany(limit + 1)
        except sqlite3.Error as e:
            raise AtlasError(f"SQL rejected or failed: {e}") from e
    finally:
        con.close()
    truncated = len(fetched) > limit
    rows = [dict(zip(cols, tuple(r))) for r in fetched[:limit]]
    return _wrap({
        "columns": cols,
        "returned": len(rows),
        "truncated": truncated,
        "row_cap": limit,
        "unit_reminder": "Name the unit and filter of any count you state (AGENTS.md §7).",
        "rows": rows,
    })


def schema_info() -> dict[str, Any]:
    """List every table and view with columns and row counts, plus pointers to
    docs/SCHEMA.md and AGENTS.md, the counting-honesty reminder (AGENTS.md §7)
    and the read-only / PR-workflow notice."""
    with _session() as con:
        objs = _rows(con, "SELECT name, type FROM sqlite_master WHERE type IN ('table','view') "
                          "AND name NOT LIKE 'sqlite_%' ORDER BY type DESC, name")
        tables = []
        for o in objs:
            name = o["name"]
            qn = '"' + name.replace('"', '""') + '"'
            cols = [r[1] for r in con.execute(f"PRAGMA table_info({qn})")]
            n = con.execute(f"SELECT count(*) FROM {qn}").fetchone()[0]
            tables.append({"name": name, "type": o["type"], "rows": n, "columns": cols})
    return _wrap({
        "db_path": str(_DB_PATH),
        "tables": tables,
        "docs": DOC_POINTERS,
        "counting_honesty": COUNTING_REMINDER,
        "read_only": READ_ONLY_REMINDER,
        "sql_helpers": ["has_token(col, 'tok') -- exact token match in a ';'-separated multi-value column"],
    })


# --------------------------------------------------------------------------
# MCP wiring
# --------------------------------------------------------------------------

TOOLS = (search_organizations, get_record, find_sites, find_capabilities,
         find_programs, find_people, run_select, schema_info)

INSTRUCTIONS = (
    "Read-only query interface to the Polymer Industry Atlas (CSV-canonical; this is the generated "
    "SQLite). Start with schema_info() if unsure. " + COUNTING_REMINDER + " " + READ_ONLY_REMINDER
)


def build_server():
    """Create the MCPServer and register the tools (imports mcp lazily)."""
    from mcp.server.mcpserver import MCPServer
    from mcp_types import ToolAnnotations

    server = MCPServer("polymer-atlas", instructions=INSTRUCTIONS)
    ann = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    for fn in TOOLS:
        server.add_tool(fn, annotations=ann)
    return server


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read-only MCP server for the Polymer Atlas (stdio).")
    ap.add_argument("--db", default=str(DEFAULT_DB), help="path to polymer-atlas.db (default: build/polymer-atlas.db)")
    args = ap.parse_args(argv)
    db = Path(args.db)
    if not db.exists():
        print(f"atlas-mcp: database not found at {db}.\n"
              "Run `python3 scripts/build_sqlite.py` to build build/polymer-atlas.db from data/*.csv, "
              "then start this server again (or pass --db).", file=sys.stderr)
        return 2
    configure(db)
    build_server().run("stdio")
    return 0


if __name__ == "__main__":
    sys.exit(main())
