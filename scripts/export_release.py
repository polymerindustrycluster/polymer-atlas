#!/usr/bin/env python3
"""Build a release bundle for the Polymer Industry Atlas. Stdlib only.

Produces, all under build/ (gitignored; nothing here is ever committed):

    build/release/
        polymer-atlas.db            SQLite database (from scripts/build_sqlite.py)
        data/organizations_all.csv  merged shard export (generated)
        data/sites_all.csv          merged shard export (generated)
        data/<table>.csv            every single-file table, copied from data/
        datapackage.json            Frictionless Data Package descriptor
        MANIFEST.sha256             sha256 of every other file in the bundle
        COUNTS.md                   row counts per table, with units
    build/polymer-atlas-release-<date>-<sha>.zip

The canonical data stays in data/*.csv. The release organization CSV adds
generated columns combining company and site values.
It runs scripts/build_sqlite.py first when build outputs are missing or older
than the newest data/*.csv (or with --rebuild); with --no-build it requires
them to exist and be current.

Usage:
    python3 scripts/export_release.py [--date YYYY-MM-DD] [--rebuild | --no-build]
"""
import argparse
import csv
import datetime
import glob
import hashlib
import io
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

if __package__:
    from .build_site import org_field_sources, release_withheld
else:
    from build_site import org_field_sources, release_withheld

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BUILD = ROOT / "build"
RELEASE = BUILD / "release"
DB = BUILD / "polymer-atlas.db"

REPO_URL = "https://github.com/polymerindustrycluster/polymer-atlas"
SHARDED = ("organizations", "sites", "evidence")  # evidence sharded since pass 43b (2026-11-02)

UNIT = {
    "organizations": "parent-organization rows (all HQ states and statuses)",
    "sites": "site/establishment rows (all states and statuses)",
    "ecosystem": "Ring 5 ecosystem-entity rows",
    "programs": "education/training program rows",
    "people": "people rows (professors and federal-lab research staff)",
    "members": "PIC public member-list rows",
    "events": "event-series rows",
    "event_participation": "event-participation rows (organization-level)",
    "evidence": "evidence rows (one claim-source observation each)",
    "relationships": "relationship edge rows",
    "site_capabilities": "site-capability rows",
    "registry_links": "external registry-link rows",
    "inclusion_log": "inclusion/exclusion decision rows",
    "code_assignments": "code-assignment rows",
    "ref_codes": "reference-code rows",
    "ref_code_map": "code-concordance rows",
    "archive_links": "evidence archive-capture rows (§4.22)",
    "equipment": "equipment rows",
    "people_engagement": "people-engagement rows",
    "people_identifiers": "person external-identifier rows (§4.21)",
    "ipeds_institutions": "IPEDS institutions reporting under a polymer or materials CIP, 1991-2023 (§4.23)",
    "ipeds_programs": "IPEDS programs: institution x CIP x award level ever observed (§4.23)",
    "ipeds_completions": "IPEDS program-year completion counts, 1991-2023 (§4.23)",
}

# --- type inference -------------------------------------------------------
# A type is declared only when a name hint AND every non-empty value agree;
# otherwise the field stays `string` (the safe default).
DATE_NAME = re.compile(r"(_date$|^date$|^last_verified$|^as_of$|^effective_from$|"
                       r"^effective_to$)")
NUMBER_COLS = {"latitude", "longitude"}
INTEGER_COLS = {"ring_primary", "ring_secondary", "latest_completions",
                "first_year_awarded", "last_year_awarded"}
YEAR_COLS = {"year_founded", "edition_year", "completions_year"}
BOOLEAN_COLS = {"diversified_conglomerate", "pic_member", "monitor_watch",
                "polymer_program", "generalist", "polymer_bound",
                "apprenticeship_registered", "hq_in_scope"}
MULTI_COLS = {"processes", "materials", "markets_served", "naics_secondary",
              "trade_names", "certifications", "tier1_qualifier",
              "tier1_qualifier_basis"}
ORG_SITE_FIELDS = ("processes", "materials", "markets_served")
ORG_SITE_COLUMNS = tuple(f"{field}_incl_sites" for field in ORG_SITE_FIELDS)
RE_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
RE_INT = re.compile(r"-?(0|[1-9]\d*)")
RE_NUM = re.compile(r"-?\d+(\.\d+)?")
RE_YEAR = re.compile(r"\d{4}")

DESCRIPTIONS = {
    "latitude": "WGS84 decimal degrees; reference data only, never evidence "
                "(AGENTS.md section 1). Pair with geocode_precision.",
    "longitude": "WGS84 decimal degrees; reference data only, never evidence "
                 "(AGENTS.md section 1). Pair with geocode_precision.",
    "naics_primary": "6-digit NAICS; carries naics_primary_source_type. "
                     "Never a company-disclosed fact by default (AGENTS.md "
                     "section 4).",
    "verification_tier": "A primary | B authoritative directory | C single "
                         "secondary | U unverified (SCHEMA.md 4.1).",
    "last_verified": "ISO date a contributor actually checked the record.",
    **{col: f"Generated union of {field} from the company and its site rows "
            "whose operating status is not closed. Distinct source tokens "
            "are separated by ';'. Includes all verification tiers."
       for field, col in zip(ORG_SITE_FIELDS, ORG_SITE_COLUMNS)},
}


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return ""


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        return list(rdr.fieldnames or []), list(rdr)


def write_organization_export(path, cols, orgs, sites):
    by_org = defaultdict(list)
    for site in sites:
        by_org[site["org_id"]].append(site)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[*cols, *ORG_SITE_COLUMNS])
        writer.writeheader()
        for org in orgs:
            writer.writerow({
                **org,
                **{col: ";".join(org_field_sources(org, by_org.get(org["org_id"], ()), field))
                   for field, col in zip(ORG_SITE_FIELDS, ORG_SITE_COLUMNS)},
            })


EVIDENCE_TABLES = {"evidence", "evidence_organizations", "evidence_sites"}
WITHHELD = "[withheld from this release]"   # in an evidence row, where claim_detail and source_ref must stay filled (SCHEMA 4.13, V-22); elsewhere the cell is blank


def blanked(table):
    return WITHHELD if table in EVIDENCE_TABLES else ""


HELD_MIN = 40   # a held value shorter than this is not searched for inside other cells (too likely to match ordinary text)


def held_pattern(db_path):
    """Regex of every value of at least HELD_MIN characters that release_withheld blanks in the bundled SQLite copy (read before it is blanked).
    A withheld description is often pasted whole into another record's notes; those copies are held too."""
    con = sqlite3.connect(db_path)
    held = set()
    for t, c in text_columns(con):
        held.update(v for (v,) in con.execute(f'SELECT "{c}" FROM "{t}" WHERE "{c}" IS NOT NULL') if isinstance(v, str) and len(v) >= HELD_MIN and release_withheld(t, c, v))
    con.close()
    return re.compile("|".join(re.escape(v) for v in sorted(held, key=len, reverse=True))) if held else None


def text_columns(con):
    for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall():
        for r in con.execute(f'PRAGMA table_info("{t}")').fetchall():
            if (r[2] or "").upper() in ("TEXT", ""):
                yield t, r[1]


def withheld_cell(table, field, value, held):
    return release_withheld(table, field, value) or bool(held and isinstance(value, str) and len(value) >= HELD_MIN and held.search(value))


def withhold_csv(path, table, held=None):
    """Blank, in the release copy only, every cell the site would withhold (build_site.release_withheld) or that contains a held value
    (held_pattern); returns how many. A file with nothing to withhold keeps its exact bytes."""
    raw = Path(path).read_bytes()
    text = raw.decode("utf-8")
    rows = list(csv.reader(io.StringIO(text, newline="")))
    if not rows:
        return 0
    head, n = rows[0], 0
    for r in rows[1:]:
        for i, v in enumerate(r):
            if withheld_cell(table, head[i] if i < len(head) else "", v, held):
                r[i] = blanked(table)
                n += 1
    if n:
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\r\n" if "\r\n" in text else "\n").writerows(rows)
    return n


def withhold_db(db_path, held=None):
    """The same withholding in the bundled SQLite copy (never the canonical build/polymer-atlas.db), then VACUUM so no held value stays in a free page."""
    con = sqlite3.connect(db_path)
    n = 0
    for t, c in list(text_columns(con)):
        hits = [rid for rid, v in con.execute(f'SELECT rowid, "{c}" FROM "{t}" WHERE "{c}" IS NOT NULL').fetchall() if withheld_cell(t, c, v, held)]
        for rid in hits:
            con.execute(f'UPDATE "{t}" SET "{c}" = ? WHERE rowid = ?', (blanked(t), rid))
        n += len(hits)
    con.commit()
    con.execute("VACUUM")
    con.close()
    return n


def data_inputs():
    return sorted(glob.glob(str(DATA / "*.csv")))


def build_is_current():
    outs = [DB, BUILD / "organizations_all.csv", BUILD / "sites_all.csv"]
    if not all(p.exists() for p in outs):
        return False
    newest_data = max(Path(p).stat().st_mtime for p in data_inputs())
    return min(p.stat().st_mtime for p in outs) >= newest_data


def ensure_build(mode):
    if mode == "rebuild" or (mode == "auto" and not build_is_current()):
        print("running scripts/build_sqlite.py ...")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_sqlite.py")],
                       cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    elif not build_is_current():
        sys.exit("error: build outputs missing or older than data/*.csv; "
                 "run scripts/build_sqlite.py or drop --no-build")


def single_tables():
    return sorted(Path(p).stem for p in data_inputs()
                  if not re.match(r"(organizations|sites|evidence)_", Path(p).name))


def infer_field(table, col, values):
    f = {"name": col, "type": "string"}
    nonempty = [v.strip() for v in values if v.strip()]
    ok = lambda rx: all(rx.fullmatch(v) for v in nonempty)
    if col in NUMBER_COLS and ok(RE_NUM):
        f["type"] = "number"
    elif col in INTEGER_COLS and ok(RE_INT):
        f["type"] = "integer"
    elif col in YEAR_COLS and ok(RE_YEAR):
        f["type"] = "year"
    elif DATE_NAME.search(col) and ok(RE_DATE):
        f["type"] = "date"
    elif col in BOOLEAN_COLS and all(v.lower() in ("true", "false")
                                     for v in nonempty):
        f["type"] = "boolean"
        f["trueValues"] = ["true"]
        f["falseValues"] = ["false"]
    d = DESCRIPTIONS.get(col)
    if col in MULTI_COLS:
        d = ("Multi-value field: values separated by ';', from the "
             "controlled vocabularies in docs/SCHEMA.md.")
    if d:
        f["description"] = d
    return f


def build_descriptor(version, created, tables, counts):
    """tables: name -> (published path, cols, rows)."""
    ids = {}
    for name, (_, cols, rows) in tables.items():
        for idc in ("org_id", "site_id"):
            if idc in cols:
                ids.setdefault((name, idc), {r[idc] for r in rows})
    org_ids = ids[("organizations", "org_id")]
    site_ids = ids[("sites", "site_id")]
    eco_ids = ids.get(("ecosystem", "org_id"), set())
    prog_ids = {r["program_id"] for r in tables["programs"][2]} if "programs" in tables else set()

    resources = []
    skipped_fk = []
    for name, (path, cols, rows) in tables.items():
        fields = [infer_field(name, c, [r[c] for r in rows]) for c in cols]
        schema = {"fields": fields, "missingValues": [""]}
        # primary key: first *_id column, only if it is unique in the data
        idcols = [c for c in cols if c.endswith("_id")]
        if idcols:
            vals = [r[idcols[0]] for r in rows]
            if all(vals) and len(set(vals)) == len(vals):
                schema["primaryKey"] = idcols[0]
        # foreign keys: only those that hold 100% in the data
        fks = []
        for c in cols:
            if c == "site_id" or c.endswith("_site_id"):
                target, tids, tpk = "sites", site_ids, "site_id"
            elif c == "program_org_id":  # SCHEMA §4.9: FK to programs.csv since v1.3, despite the name
                target, tids, tpk = "programs", prog_ids, "program_id"
            elif c == "org_id" or c.endswith("_org_id"):
                target, tids, tpk = "organizations", org_ids, "org_id"
            else:
                continue
            if name == target and c == tpk:
                continue
            vals = {r[c] for r in rows if r[c].strip()}
            if not vals:
                continue
            if vals <= tids:
                fks.append({"fields": c,
                            "reference": {"resource": target, "fields": tpk}})
            elif target == "organizations":
                missing = vals - tids
                n_eco = len(missing & eco_ids)
                if name == "ecosystem" and c == "org_id":
                    continue  # ecosystem's own primary key
                skipped_fk.append(
                    f"{name}.{c}: {len(missing)} distinct id(s) not in "
                    f"organizations ({n_eco} are ecosystem records, "
                    f"{len(missing) - n_eco} unresolved); the reference spans "
                    f"organizations + ecosystem, which a Data Package foreign "
                    f"key cannot express")
            else:
                skipped_fk.append(f"{name}.{c}: {len(vals - tids)} distinct "
                                  f"id(s) not in {target}")
        if fks:
            schema["foreignKeys"] = fks
        res = {
            "name": name,
            "path": path,
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "profile": "tabular-data-resource",
            "title": name.replace("_", " "),
            "description": f"{counts[name]:,} {UNIT[name]}.",
            "schema": schema,
        }
        if name in SHARDED:
            res["description"] += (" Generated union of the per-state shards "
                                   "data/%s_<TAG>.csv, ID-sorted; canonical "
                                   "data is the shards." % name)
        resources.append(res)
    return {
        "profile": "tabular-data-package",
        "name": "polymer-atlas",
        "title": "Polymer Industry Atlas",
        "description": (
            "Open, source-backed database of the US polymer / plastics / "
            "rubber industry: parent organizations, physical establishments, "
            "the ecosystem that supports them, evidence, relationships and "
            "capabilities. Built for the Polymer Industry Cluster (PIC), "
            "Greater Akron Chamber. Organizations and sites are separate "
            "units; always state the unit when quoting a count. A SQLite "
            "build of the canonical data ships alongside as polymer-atlas.db."),
        "version": version,
        "created": created,
        "homepage": REPO_URL,
        "licenses": [{
            "name": "CC-BY-4.0",
            "title": "Creative Commons Attribution 4.0 International",
            "path": "https://creativecommons.org/licenses/by/4.0/",
        }],
        "notes": ("The data is licensed CC BY 4.0 (README.md, Licensing). The "
                  "scripts that build the database and this bundle are MIT "
                  "licensed and are not part of the data license above."),
        "sources": [{"title": "polymer-atlas (canonical CSVs, schema and "
                              "scripts)", "path": REPO_URL}],
        "keywords": ["polymer", "plastics", "rubber", "manufacturing", "Ohio",
                     "economic development", "industry cluster"],
        "resources": resources,
        "x-foreignKeysNotDeclared": skipped_fk,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=datetime.date.today().isoformat(),
                    help="release date, YYYY-MM-DD (default: today)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--rebuild", action="store_true",
                   help="always re-run scripts/build_sqlite.py")
    g.add_argument("--no-build", action="store_true",
                   help="require current build outputs; do not run the builder")
    args = ap.parse_args()
    datetime.date.fromisoformat(args.date)
    ensure_build("rebuild" if args.rebuild else
                 "none" if args.no_build else "auto")

    sha = git("rev-parse", "--short=7", "HEAD") or "nogit"
    dirty = bool(git("status", "--porcelain", "--", "data"))
    tag = sha + ("-dirty" if dirty else "")
    version = f"{args.date}+{tag}"
    stem = f"polymer-atlas-release-{args.date}-{tag}"
    if dirty:
        print("note: data/ has uncommitted changes; bundle describes the "
              "working tree and is marked -dirty")

    # fresh bundle dir (inside build/ only)
    assert RELEASE.resolve().parent == BUILD.resolve()
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    (RELEASE / "data").mkdir(parents=True)

    # copy files and read them back for the descriptor
    shutil.copy2(DB, RELEASE / "polymer-atlas.db")
    held = held_pattern(RELEASE / "polymer-atlas.db")   # read before the copy is blanked
    withheld = {"database": withhold_db(RELEASE / "polymer-atlas.db", held)}   # the canonical .db and CSVs are never touched
    published = {}  # name -> (path, cols, rows)
    for t in ("sites", "organizations", "evidence"):
        path = f"data/{t}_all.csv"
        source = BUILD / f"{t}_all.csv"
        if t == "organizations":
            cols, rows = read_csv(source)
            write_organization_export(RELEASE / path, cols, rows, published["sites"][2])
        else:
            shutil.copy2(source, RELEASE / path)
        withheld[t] = withhold_csv(RELEASE / path, t, held)
        cols, rows = read_csv(RELEASE / path)
        published[t] = (path, cols, rows)
    for t in single_tables():
        shutil.copy2(DATA / f"{t}.csv", RELEASE / "data" / f"{t}.csv")
        withheld[t] = withhold_csv(RELEASE / "data" / f"{t}.csv", t, held)
        cols, rows = read_csv(RELEASE / "data" / f"{t}.csv")
        published[t] = (f"data/{t}.csv", cols, rows)
    counts = {t: len(v[2]) for t, v in published.items()}

    # integrity checks: merged exports equal shard union; DB equals CSVs
    for t in SHARDED:
        shard_n = sum(len(read_csv(p)[1])
                      for p in glob.glob(str(DATA / f"{t}_*.csv")))
        if shard_n != counts[t]:
            sys.exit(f"error: {t}_all.csv has {counts[t]} rows but shards "
                     f"hold {shard_n}; rebuild (--rebuild)")
    con = sqlite3.connect(f"file:{RELEASE / 'polymer-atlas.db'}?mode=ro", uri=True)
    for t, n in counts.items():
        (m,) = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()
        if m != n:
            sys.exit(f"error: DB table {t} has {m} rows, CSV has {n}; "
                     f"rebuild (--rebuild)")
    con.close()

    created = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    order = list(SHARDED) + sorted(t for t in published if t not in SHARDED)
    descriptor = build_descriptor(version, created,
                                  {t: published[t] for t in order}, counts)
    for res in descriptor["resources"]:
        p = RELEASE / res["path"]
        res["bytes"] = p.stat().st_size
        res["hash"] = "sha256:" + sha256_file(p)
    (RELEASE / "datapackage.json").write_text(
        json.dumps(descriptor, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")

    # COUNTS.md
    lines = [
        f"# Polymer Atlas release {version} — row counts",
        "",
        f"Git commit: `{git('rev-parse', 'HEAD') or 'unavailable'}`"
        + (" (data/ had uncommitted changes at build time)" if dirty else ""),
        f"Built: {created}",
        "",
        "Every count names its unit. Rows are table rows, all verification "
        "tiers and all statuses (closed / acquired / merged records are kept "
        "and tombstoned, never deleted). A row count of `organizations` is "
        "*parent organizations*; of `sites` is *physical establishments*; the "
        "two are not interchangeable.",
        "",
        "| table | file in bundle | unit | rows |",
        "|---|---|---|---|",
    ]
    for t in order:
        lines.append(f"| `{t}` | `{published[t][0]}` | {UNIT[t]} | "
                     f"{counts[t]:,} |")
    lines += ["", "The SQLite file `polymer-atlas.db` holds the same tables "
                  "(plus views) with identical row counts; this was checked at "
                  "export time.", "",
              "Withheld cells: the release blanks, in its own copies only, a description that "
              "carries internal build or review wording, any cell with a temporary record id "
              "of a build pass, and any cell that repeats a withheld description, the same test "
              "the website applies (a withheld evidence cell reads `[withheld from this release]` so the row keeps its claim and source). The canonical CSVs and database keep them. Cells blanked: "
              + ", ".join(f"{k} {v:,}" for k, v in sorted(withheld.items()) if v) + ".", ""]
    (RELEASE / "COUNTS.md").write_text("\n".join(lines), encoding="utf-8")

    # MANIFEST.sha256 (every file except itself; sha256sum -c compatible)
    files = sorted(p for p in RELEASE.rglob("*")
                   if p.is_file() and p.name != "MANIFEST.sha256")
    (RELEASE / "MANIFEST.sha256").write_text(
        "".join(f"{sha256_file(p)}  {p.relative_to(RELEASE).as_posix()}\n"
                for p in files), encoding="utf-8")

    # zip, with a top-level folder, stable order and timestamps
    zip_path = BUILD / f"{stem}.zip"
    if zip_path.exists():
        zip_path.unlink()
    ts = git("log", "-1", "--format=%ct", "HEAD")
    when = datetime.datetime.fromtimestamp(int(ts) if ts.isdigit() else 0,
                                           datetime.timezone.utc)
    stamp = (max(when.year, 1980), when.month, when.day, when.hour,
             when.minute, when.second)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=9) as z:
        for p in sorted(p for p in RELEASE.rglob("*") if p.is_file()):
            zi = zipfile.ZipInfo(f"{stem}/{p.relative_to(RELEASE).as_posix()}",
                                 stamp)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, p.read_bytes(), compresslevel=9)

    print(f"version        {version}")
    print(f"bundle dir     {RELEASE}")
    print(f"zip            {zip_path} ({zip_path.stat().st_size:,} bytes)")
    print(f"zip sha256     {sha256_file(zip_path)}")
    print(f"resources      {len(descriptor['resources'])}")
    print("withheld cells " + (", ".join(f"{k}={v}" for k, v in sorted(withheld.items()) if v) or "none"))
    print("counts (rows): " + ", ".join(f"{t}={counts[t]:,}" for t in order))
    if descriptor["x-foreignKeysNotDeclared"]:
        print("foreign keys not declared (data does not satisfy them):")
        for s in descriptor["x-foreignKeysNotDeclared"]:
            print("  -", s)


if __name__ == "__main__":
    main()
