#!/usr/bin/env python3
"""Static site generator for the Polymer Industry Atlas. Stdlib only.

Reads build/polymer-atlas.db (building it with scripts/build_sqlite.py when it
is missing) and writes a self-contained static site to build/site/:

    index.html            what the Atlas is, headline counts (unit + filter)
    map.html + sites.json Leaflet map of sites that carry coordinates
    search.html + orgs.json  client-side search over organizations/ecosystem
    counties/index.html, counties/<county>.html   PIC-12 Ohio county pages
    orgs/<org_id>.html    one page per organization and ecosystem org
    style.css, map.js, search.js

The CSVs in data/ stay canonical; this script only reads the generated SQLite
file and a reference CSV, and never touches data/. build/ is gitignored, so
nothing generated here is ever committed (AGENTS.md section 1).

Privacy (AGENTS.md section 6): only whitelisted public business fields are
rendered. Free-text `notes`, `created_by`, `pic_relevance` and other internal
columns are never written to a page. People appear only as name / role /
specialty / public profile URL, on their institution's page.

Usage:
    python3 scripts/build_site.py [--db PATH] [--out DIR] [--qcew CSV]
                                  [--rebuild-db] [--repo-url URL]
"""
import argparse
import csv
import datetime
import html
import json
import re
import shutil
import sqlite3
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "build" / "polymer-atlas.db"
DEFAULT_OUT = ROOT / "build" / "site"
DEFAULT_QCEW = ROOT / "docs" / "denominators" / "qcew_county_polymer_ohio_pa_2023_2024.csv"
DEFAULT_REPO = "https://github.com/polymerindustrycluster/polymer-atlas"

LEAFLET = "https://unpkg.com/leaflet@1.9.4/dist/"
LEAFLET_CSS_SRI = "sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
LEAFLET_JS_SRI = "sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="

PIC12 = ["Ashtabula", "Cuyahoga", "Geauga", "Lake", "Lorain", "Mahoning",
         "Medina", "Portage", "Stark", "Summit", "Trumbull", "Wayne"]

RINGS = {
    "1": "Core Producers & Processors",
    "2": "Materials, Compounding & Formulated Polymers",
    "3": "Value Chain",
    "4": "Downstream OEMs & Heavy Users",
    "5": "Ecosystem",
}
RING_TESTS = {
    "1": "Physically transforms resin/rubber, or its headline product is plastic/rubber.",
    "2": "Sells a material whose functional ingredient is a polymer, resin or elastomer.",
    "3": "Tooling, machinery, distribution, recycling, testing/R&D serving polymer firms.",
    "4": "Passes 2 of 3: polymer volume/value, performance dependence, local decision-making.",
    "5": "Named polymer program, or generalist economic-development/workforce org for an in-scope geography.",
}
TIERS = {
    "A": ("Primary source", "company website, SEC / Ohio SOS / SAM.gov filing"),
    "B": ("Authoritative directory", "trade directory, association or economic-development directory, government dataset"),
    "C": ("Single secondary source", "one secondary source only"),
    "U": ("Unverified candidate", "not counted in headline totals"),
}
TIER_ORDER = ["A", "B", "C", "U"]
TOMBSTONE_STATUSES = {"acquired", "merged", "closed"}

NAICS3 = {
    "211": "Oil and gas extraction", "212": "Mining (except oil and gas)",
    "221": "Utilities", "237": "Heavy and civil engineering construction",
    "238": "Specialty trade contractors", "311": "Food manufacturing",
    "312": "Beverage and tobacco product manufacturing", "313": "Textile mills",
    "314": "Textile product mills", "315": "Apparel manufacturing",
    "316": "Leather and allied product manufacturing", "321": "Wood product manufacturing",
    "322": "Paper manufacturing", "323": "Printing and related support activities",
    "324": "Petroleum and coal products manufacturing", "325": "Chemical manufacturing",
    "326": "Plastics and rubber products manufacturing",
    "327": "Nonmetallic mineral product manufacturing", "331": "Primary metal manufacturing",
    "332": "Fabricated metal product manufacturing", "333": "Machinery manufacturing",
    "334": "Computer and electronic product manufacturing",
    "335": "Electrical equipment, appliance and component manufacturing",
    "336": "Transportation equipment manufacturing", "337": "Furniture and related product manufacturing",
    "339": "Miscellaneous manufacturing", "423": "Merchant wholesalers, durable goods",
    "424": "Merchant wholesalers, nondurable goods",
    "425": "Wholesale trade agents and brokers", "441": "Motor vehicle and parts dealers",
    "484": "Truck transportation", "488": "Support activities for transportation",
    "493": "Warehousing and storage", "512": "Motion picture and sound recording industries",
    "513": "Publishing industries", "541": "Professional, scientific and technical services",
    "551": "Management of companies and enterprises",
    "561": "Administrative and support services",
    "562": "Waste management and remediation services", "611": "Educational services",
    "621": "Ambulatory health care services", "622": "Hospitals",
    "811": "Repair and maintenance", "813": "Religious, grantmaking, civic, professional and similar organizations",
    "921": "Executive, legislative and general government",
}

SOURCE_CLASS_NOTE = ("Counts on this site always name their unit (organization rows, "
                     "site rows) and their filter. Site rows are physical establishments; "
                     "organization rows are parent organizations. They are never "
                     "interchangeable.")

# --------------------------------------------------------------------------
# small helpers


def esc(value):
    """HTML-escape any value (None -> empty string). Used on every field."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def fmt_int(n):
    return f"{n:,}"


def safe_id(value):
    """Filesystem/URL-safe page stem for a record id."""
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(value))


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def vocab(value):
    """Controlled-vocabulary multi-value field -> readable text (still unescaped)."""
    if not value:
        return ""
    return ", ".join(v.strip().replace("_", " ") for v in str(value).split(";") if v.strip())


def nonempty(value):
    return value is not None and str(value).strip() != ""


URL_RE = re.compile(r"https?://[^\s<>\"')\]]+")


def linkify(text):
    """Escape text and turn http(s) URLs into links. Nothing else becomes markup."""
    text = "" if text is None else str(text)
    out, pos = [], 0
    for m in URL_RE.finditer(text):
        url = m.group(0).rstrip(".,;:")
        out.append(esc(text[pos:m.start()]))
        out.append(f'<a href="{esc(url)}" rel="noopener nofollow">{esc(url)}</a>')
        pos = m.start() + len(url)
    out.append(esc(text[pos:]))
    return "".join(out)


# Source items that point at private/internal workflow material are not shown
# on the public site (AGENTS.md section 5.1: the PIC CRM is never a cited
# source; staging paths are workshop-area references). The repository CSVs
# keep the full source text; the page says how many items were left out.
INTERNAL_SOURCE_RE = re.compile(r"\bCRM\b|\(staging\b|\bstaging working/|\(working/[\w.-]+/", re.I)


CRM_RE = re.compile(r"\bCRM\b")


def lede(text):
    """Description paragraph; text that references the private PIC CRM is withheld."""
    if not nonempty(text):
        return ""
    if CRM_RE.search(str(text)):
        return ('<p class="muted">The one-line description is withheld from this view because it refers to '
                "internal material; see the repository CSV.</p>")
    return f'<p class="lede">{esc(text)}</p>'


def source_list(sources):
    if not nonempty(sources):
        return '<p class="muted">No source text recorded.</p>'
    parts = [p.strip() for p in re.split(r";\s+", str(sources)) if p.strip()]
    shown = [p for p in parts if not INTERNAL_SOURCE_RE.search(p)]
    hidden = len(parts) - len(shown)
    out = '<ul class="sources">' + "".join(f"<li>{linkify(p)}</li>" for p in shown) + "</ul>" if shown else ""
    if hidden:
        out += (f'<p class="small muted">{hidden} internal workflow reference{"s" if hidden != 1 else ""} '
                "omitted from this view; the repository's CSV holds the full source text.</p>")
    return out or '<p class="muted">No source text recorded.</p>'


def safe_href(url):
    """Return the url only if it is an http(s) URL (never javascript: etc.)."""
    if nonempty(url) and re.match(r"^https?://", str(url).strip(), re.I):
        return str(url).strip()
    return None


def ext_link(url, text=None):
    href = safe_href(url)
    if not href:
        return esc(text if text is not None else url)
    return f'<a href="{esc(href)}" rel="noopener nofollow">{esc(text if text is not None else href)}</a>'


def ring_badge(ring, inherited=False):
    if not nonempty(ring):
        return '<span class="badge ring-x" title="Ring not recorded">Ring n/a</span>'
    r = str(ring)
    title = RINGS.get(r, "")
    star = '<abbr title="Site ring not recorded; shown from the parent organization record">*</abbr>' if inherited else ""
    return f'<span class="badge ring-{esc(r)}" title="{esc(title)}">Ring {esc(r)}</span>{star}'


def tier_badge(tier):
    if not nonempty(tier):
        return '<span class="badge tier-x">n/a</span>'
    t = str(tier)
    title = TIERS.get(t, ("", ""))[0]
    return f'<span class="badge tier-{esc(t)}" title="{esc(title)}">Tier {esc(t)}</span>'


def status_badge(status):
    if not nonempty(status):
        return ""
    cls = "ok" if status == "active" else "warn"
    return f'<span class="badge status-{cls}">{esc(str(status).replace("_", " "))}</span>'


def naics_label(code, ref_titles=None):
    code = str(code or "")
    if ref_titles and code in ref_titles:
        return ref_titles[code]
    return NAICS3.get(code[:3], "") if len(code) == 3 else ""


# --------------------------------------------------------------------------
# data loading


def table_exists(con, name):
    return con.execute("SELECT 1 FROM sqlite_master WHERE name=? AND type IN ('table','view')",
                       (name,)).fetchone() is not None


def rows_of(con, name):
    """All rows of a table as plain dicts ([] if the table does not exist)."""
    if not table_exists(con, name):
        return []
    cur = con.execute(f'SELECT * FROM "{name}"')
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


class Atlas:
    """In-memory view of the tables the site needs."""

    def __init__(self, con):
        self.orgs = {r["org_id"]: r for r in rows_of(con, "organizations")}
        self.eco = {r["org_id"]: r for r in rows_of(con, "ecosystem")}
        self.sites = rows_of(con, "sites")
        self.programs = rows_of(con, "programs")
        self.people = rows_of(con, "people")
        self.rels = rows_of(con, "relationships")
        self.ref_titles = {r["code_value"]: r["code_title"] for r in rows_of(con, "ref_codes")
                           if r.get("code_system") == "NAICS" and r.get("code_value")}
        self.sites_by_org = defaultdict(list)
        for s in self.sites:
            self.sites_by_org[s["org_id"]].append(s)
            s["_ring"], s["_ring_inherited"] = self.effective_ring(s)
        self.children = defaultdict(list)
        for o in self.orgs.values():
            if nonempty(o.get("parent_org_id")):
                self.children[o["parent_org_id"]].append(o)
        self.programs_by_inst = defaultdict(list)
        for p in self.programs:
            self.programs_by_inst[p.get("institution_org_id")].append(p)
        self.people_by_inst = defaultdict(list)
        for p in self.people:
            self.people_by_inst[p.get("institution_org_id")].append(p)
        self.merged_into = {}
        for r in self.rels:
            if r.get("relationship_type") == "merged_into":
                self.merged_into[r["from_org_id"]] = r["to_org_id"]

    def effective_ring(self, site):
        if nonempty(site.get("ring_primary")):
            return str(site["ring_primary"]), False
        parent = self.orgs.get(site["org_id"])
        if parent and nonempty(parent.get("ring_primary")):
            return str(parent["ring_primary"]), True
        if site["org_id"] in self.eco:
            return "5", True
        return None, False

    def name_of(self, org_id):
        if org_id in self.orgs:
            return self.orgs[org_id]["legal_name"]
        if org_id in self.eco:
            return self.eco[org_id]["legal_name"]
        return None

    def org_link(self, org_id, orgs_dir=""):
        """Link to an organization/ecosystem page if the record is held.
        orgs_dir is the relative path to the orgs/ folder ('' from inside it,
        '../orgs/' from counties/)."""
        name = self.name_of(org_id)
        if name is None:
            return esc(org_id)
        return f'<a href="{orgs_dir}{esc(safe_id(org_id))}.html">{esc(name)}</a>'


def load_qcew(path):
    """{county name: row} for Ohio, 2023, private (own_code 5), NAICS 326."""
    out = {}
    if not path or not Path(path).exists():
        return out
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r["year"] == "2023" and r["industry_code"] == "326" and r["own_code"] == "5"
                    and r["area_title"].endswith(", Ohio") and r["area_title"].count(" County") == 1):
                out[r["area_title"].split(" County")[0]] = r
    return out


def git_info(repo_root):
    """Short sha, commit date and dirty flag for the 'as of' line."""
    def run(*args):
        try:
            return subprocess.run(["git", "-C", str(repo_root), *args], capture_output=True,
                                  text=True, timeout=20, check=True).stdout.strip()
        except Exception:
            return ""
    sha = run("rev-parse", "--short", "HEAD")
    if not sha:
        return {"sha": "unknown", "date": "unknown", "dirty": False}
    return {"sha": sha, "date": run("log", "-1", "--format=%cs") or "unknown",
            "dirty": bool(run("status", "--porcelain", "--", "data"))}


# --------------------------------------------------------------------------
# page layout

NAV = [("index", "Home", "index.html"), ("map", "Map", "map.html"),
       ("search", "Search", "search.html"), ("counties", "Ohio counties", "counties/index.html"),
       ("graph", "Graph", "graph/index.html"), ("geo", "Map + network", "graph/map.html"),
       ("shows", "Trade shows", "graph/events.html")]


class Ctx:
    def __init__(self, atlas, qcew, git, repo_url, built_on, db_date):
        self.atlas, self.qcew, self.git, self.repo_url = atlas, qcew, git, repo_url
        self.built_on, self.db_date = built_on, db_date

    def asof(self):
        g = self.git
        dirty = " plus uncommitted local data changes" if g["dirty"] else ""
        return (f"Repository commit {esc(g['sha'])} ({esc(g['date'])}){dirty}; "
                f"database built {esc(self.db_date)}; site generated {esc(self.built_on)}.")


def page(ctx, title, body, root="", active="", description="", head_extra="", scripts=""):
    nav = "".join(
        '<li><a href="%s%s"%s>%s</a></li>' % (root, href, ' aria-current="page"' if key == active else "", label)
        for key, label, href in NAV)
    desc = esc(description or "Open, source-backed database of the US polymer, plastics and rubber industry.")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="description" content="{desc}">
<title>{esc(title)} | Polymer Industry Atlas</title>
<link rel="stylesheet" href="{root}style.css">
{head_extra}
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header class="site-header">
<div class="wrap">
<a class="brand" href="{root}index.html">Polymer Industry Atlas</a>
<nav aria-label="Main"><ul>{nav}</ul></nav>
</div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site-footer">
<div class="wrap">
<p>Polymer Industry Atlas, built for the Polymer Industry Cluster (PIC), Greater Akron Chamber.
Data license: <a href="https://creativecommons.org/licenses/by/4.0/" rel="noopener">CC BY 4.0</a>.
Source and data: <a href="{esc(ctx.repo_url)}" rel="noopener">{esc(ctx.repo_url)}</a>.</p>
<p class="muted">{ctx.asof()}</p>
<p class="muted">Coordinates are reference data, never evidence. A missing figure is not a zero.
Counts here are database rows, not industry totals.</p>
</div>
</footer>
{scripts}
</body>
</html>
"""


def table_wrap(inner, label):
    return f'<div class="table-wrap" role="region" aria-label="{esc(label)}" tabindex="0">{inner}</div>'


def tier_counts_row(counter):
    return "".join(f"<td class=\"num\">{fmt_int(counter.get(t, 0))}</td>" for t in TIER_ORDER)


def breakdown_table(title_col, groups, order, label_fn, caption):
    """groups: key -> list of site rows; columns by tier."""
    head = "".join(f"<th scope=\"col\" class=\"num\">Tier {t}</th>" for t in TIER_ORDER)
    body, total = [], Counter()
    for key in order:
        rows = groups.get(key, [])
        c = Counter((r.get("verification_tier") or "?") for r in rows)
        total.update(c)
        body.append(f"<tr><th scope=\"row\">{label_fn(key)}</th>{tier_counts_row(c)}"
                    f"<td class=\"num\"><strong>{fmt_int(len(rows))}</strong></td></tr>")
    n_total = sum(total.values())
    body.append(f"<tr class=\"total\"><th scope=\"row\">Total</th>{tier_counts_row(total)}"
                f"<td class=\"num\"><strong>{fmt_int(n_total)}</strong></td></tr>")
    return table_wrap(
        f"<table><caption>{esc(caption)}</caption><thead><tr><th scope=\"col\">{esc(title_col)}</th>{head}"
        f"<th scope=\"col\" class=\"num\">Site rows</th></tr></thead><tbody>{''.join(body)}</tbody></table>",
        caption)


# --------------------------------------------------------------------------
# CSS / JS assets

CSS = """
:root{
  --bg:#ffffff;--fg:#1b1f23;--muted:#586069;--line:#d0d7de;--panel:#f6f8fa;--accent:#0b5cad;
  --accent-fg:#ffffff;--warn-bg:#fff4ce;--warn-fg:#5c4400;--ok-bg:#dff5e3;--ok-fg:#14532d;
  --r1:#0072B2;--r2:#E69F00;--r3:#009E73;--r4:#CC79A7;--r5:#6d4fb3;--rx:#777777;
}
@media (prefers-color-scheme: dark){
  :root{--bg:#0f1317;--fg:#e6edf3;--muted:#9aa4af;--line:#30363d;--panel:#161b22;--accent:#58a6ff;
  --accent-fg:#0b0f14;--warn-bg:#3b2f00;--warn-fg:#ffd866;--ok-bg:#0f3320;--ok-fg:#7ee2a0;
  --r1:#4aa3df;--r2:#f2b84b;--r3:#2cc39a;--r4:#e29bc2;--r5:#a58be0;--rx:#9aa4af;}
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:0 16px}
a{color:var(--accent)}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,[tabindex]:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.skip{position:absolute;left:-999px;top:0;background:var(--accent);color:var(--accent-fg);padding:8px 12px;z-index:1000}
.skip:focus{left:8px;top:8px}
.site-header{border-bottom:1px solid var(--line);background:var(--panel)}
.site-header .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 24px;padding-top:10px;padding-bottom:10px}
.brand{font-weight:700;font-size:1.1rem;text-decoration:none;color:var(--fg)}
nav ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:4px 16px}
nav a{text-decoration:none;padding:4px 2px;border-bottom:2px solid transparent}
nav a[aria-current=page],nav a:hover{border-bottom-color:var(--accent)}
main{padding-top:24px;padding-bottom:40px}
h1{font-size:1.8rem;line-height:1.25;margin:.2em 0 .4em}
h2{font-size:1.3rem;margin:1.8em 0 .5em;border-bottom:1px solid var(--line);padding-bottom:.2em}
h3{font-size:1.1rem;margin:1.4em 0 .4em}
.lede{font-size:1.1rem;color:var(--muted);max-width:60em}
.muted{color:var(--muted)}
.small{font-size:.9rem}
.site-footer{border-top:1px solid var(--line);background:var(--panel);padding:16px 0;font-size:.9rem}
.site-footer p{margin:.3em 0}
.table-wrap{overflow-x:auto;margin:.6em 0 1.2em;border:1px solid var(--line);border-radius:6px}
table{border-collapse:collapse;width:100%;font-size:.95rem}
caption{text-align:left;padding:8px 10px;font-weight:600;color:var(--muted)}
th,td{padding:6px 10px;border-top:1px solid var(--line);text-align:left;vertical-align:top}
thead th{background:var(--panel);border-top:0;white-space:nowrap}
tbody th{font-weight:600}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tr.total th,tr.total td{background:var(--panel)}
.badge{display:inline-block;padding:0 7px;border-radius:10px;font-size:.8rem;line-height:1.5;border:1px solid var(--line);white-space:nowrap;background:var(--panel)}
.ring-1{border-color:var(--r1);color:var(--r1)}.ring-2{border-color:var(--r2);color:var(--r2)}
.ring-3{border-color:var(--r3);color:var(--r3)}.ring-4{border-color:var(--r4);color:var(--r4)}
.ring-5{border-color:var(--r5);color:var(--r5)}.ring-x{border-color:var(--rx);color:var(--rx)}
.status-ok{background:var(--ok-bg);color:var(--ok-fg);border-color:transparent}
.status-warn{background:var(--warn-bg);color:var(--warn-fg);border-color:transparent}
.tier-U{border-style:dashed}
.banner{border:1px solid var(--line);border-left:6px solid var(--rx);background:var(--panel);padding:10px 14px;margin:1em 0;border-radius:4px}
.banner.tombstone{border-left-color:#c0392b;background:var(--warn-bg);color:var(--warn-fg)}
.banner.tombstone a{color:inherit;font-weight:600}
.banner.note{border-left-color:var(--accent)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin:1em 0}
.card{border:1px solid var(--line);border-radius:8px;padding:12px 14px;background:var(--panel)}
.card .big{font-size:1.9rem;font-weight:700;line-height:1.1;font-variant-numeric:tabular-nums}
.card .unit{font-weight:600;margin-top:4px}
.card .filter{color:var(--muted);font-size:.9rem}
dl.fields{display:grid;grid-template-columns:minmax(9em,14em) 1fr;gap:6px 16px;margin:.6em 0}
dl.fields dt{font-weight:600;color:var(--muted)}
dl.fields dd{margin:0;overflow-wrap:anywhere}
@media (max-width:600px){dl.fields{grid-template-columns:1fr}dl.fields dt{margin-top:.5em}}
ul.sources{margin:.3em 0;padding-left:1.2em}
ul.sources li{overflow-wrap:anywhere;margin:.2em 0}
article.site{border:1px solid var(--line);border-radius:8px;padding:6px 14px 10px;margin:12px 0}
article.site h3{margin:.5em 0 .2em}
article.site:target{outline:3px solid var(--accent)}
details{margin:.4em 0}
summary{cursor:pointer}
.filters{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:1em 0}
fieldset{border:1px solid var(--line);border-radius:6px;padding:8px 12px;margin:0;min-width:0}
legend{font-weight:600;padding:0 4px}
fieldset label{display:block;padding:1px 0}
.scroll{max-height:12em;overflow-y:auto}
.swatch{display:inline-block;width:.9em;height:.9em;border-radius:50%;margin-right:6px;vertical-align:-1px;border:1px solid var(--fg)}
button,select,input[type=search]{font:inherit;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:6px 10px}
button{cursor:pointer;background:var(--panel)}
input[type=search]{width:100%;max-width:34em}
#map{height:70vh;min-height:380px;border:1px solid var(--line);border-radius:6px}
.btn-row{display:flex;flex-wrap:wrap;gap:6px;margin:.4em 0}
ul.results{list-style:none;padding:0}
ul.results li{border-top:1px solid var(--line);padding:8px 0}
ul.results .meta{color:var(--muted);font-size:.9rem}
.leaflet-popup-content{color:#1b1f23}
.leaflet-popup-content a{color:#0b5cad}
@media print{.site-header nav,.skip,.filters,#map{display:none}}
"""

MAP_JS = r"""(function () {
  'use strict';
  var COLORS = {'1': '#0072B2', '2': '#E69F00', '3': '#009E73', '4': '#CC79A7', '5': '#6d4fb3', 'x': '#777777'};
  var RING_NAMES = {'1': 'Core Producers & Processors', '2': 'Materials, Compounding & Formulated Polymers',
    '3': 'Value Chain', '4': 'Downstream OEMs & Heavy Users', '5': 'Ecosystem'};
  var status = document.getElementById('map-status');
  function el(tag, text, attrs) {
    var n = document.createElement(tag);
    if (text !== undefined && text !== null) n.textContent = text;
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    return n;
  }
  if (typeof L === 'undefined') {
    status.textContent = 'The map library (Leaflet) could not be loaded. Check your connection; the county pages and search still work offline.';
    return;
  }
  fetch('sites.json').then(function (r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }).then(init).catch(function (e) {
    status.textContent = 'Could not load sites.json (' + e.message + '). If you opened this file directly from disk, serve the folder over http instead (see docs/SITE_HOWTO.md).';
  });

  function init(data) {
    var C = {}; data.cols.forEach(function (c, i) { C[c] = i; });
    var rows = data.rows;
    var map = L.map('map', {preferCanvas: true}).setView([40.5, -96], 4);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    var canvas = L.canvas({padding: 0.5});
    var group = L.layerGroup().addTo(map);
    var markers = rows.map(function (r) {
      var key = r[C.ring] || 'x';
      var m = L.circleMarker([r[C.lat], r[C.lon]], {
        renderer: canvas, radius: 5, weight: 1, color: '#222', fillColor: COLORS[key] || COLORS.x, fillOpacity: 0.85
      });
      m.bindPopup(function () { return popup(r); });
      return m;
    });

    function popup(r) {
      var box = el('div');
      box.appendChild(el('strong', r[C.name]));
      var org = data.orgs[r[C.org]];
      var lines = [];
      var p = el('div'); p.appendChild(document.createTextNode('Parent organization: '));
      if (org) { p.appendChild(el('a', org, {href: 'orgs/' + r[C.org] + '.html'})); }
      else { p.appendChild(document.createTextNode(r[C.org])); }
      box.appendChild(p);
      box.appendChild(el('div', 'City: ' + [r[C.city], r[C.st]].filter(Boolean).join(', ')));
      var ring = r[C.ring] ? 'Ring ' + r[C.ring] + ' (' + (RING_NAMES[r[C.ring]] || '') + ')' + (r[C.inh] ? ' *' : '') : 'Ring not recorded';
      box.appendChild(el('div', ring));
      box.appendChild(el('div', 'Verification tier: ' + (r[C.tier] || 'n/a')));
      box.appendChild(el('div', 'Operating status: ' + (r[C.status] || 'n/a').replace(/_/g, ' ')));
      if (r[C.inh]) box.appendChild(el('div', '* site ring not recorded; parent organization ring shown', {'class': 'small'}));
      box.appendChild(el('div', 'Coordinates: reference data (interpolated), not evidence.', {'class': 'small'}));
      return box;
    }

    function checked(name) {
      return Array.prototype.slice.call(document.querySelectorAll('input[name="' + name + '"]:checked'))
        .map(function (i) { return i.value; });
    }
    function apply(fit) {
      var rings = checked('ring'), tiers = checked('tier'), states = checked('state');
      var allStatus = document.getElementById('f-allstatus').checked;
      var rs = {}, ts = {}, ss = {};
      rings.forEach(function (v) { rs[v] = 1; }); tiers.forEach(function (v) { ts[v] = 1; });
      states.forEach(function (v) { ss[v] = 1; });
      group.clearLayers();
      var shown = [];
      rows.forEach(function (r, i) {
        if (!rs[r[C.ring] || 'x']) return;
        if (!ts[r[C.tier] || 'x']) return;
        if (!ss[r[C.st] || 'x']) return;
        if (!allStatus && r[C.status] !== 'active') return;
        group.addLayer(markers[i]); shown.push(markers[i]);
      });
      status.textContent = 'Showing ' + shown.length.toLocaleString() + ' of ' + rows.length.toLocaleString() +
        ' site rows that have coordinates (filters applied: ring, tier, state' + (allStatus ? '' : ', operating status active only') + ').';
      if (fit && shown.length) {
        map.fitBounds(L.featureGroup(shown).getBounds().pad(0.05), {maxZoom: 11});
      }
    }
    Array.prototype.forEach.call(document.querySelectorAll('#filters input'), function (i) {
      i.addEventListener('change', function () { apply(false); });
    });
    function setStates(fn) {
      Array.prototype.forEach.call(document.querySelectorAll('input[name="state"]'), function (i) { i.checked = fn(i.value); });
      apply(true);
    }
    document.getElementById('st-all').addEventListener('click', function () { setStates(function () { return true; }); });
    document.getElementById('st-none').addEventListener('click', function () { setStates(function () { return false; }); });
    document.getElementById('st-oh').addEventListener('click', function () { setStates(function (v) { return v === 'OH'; }); });
    document.getElementById('fit').addEventListener('click', function () { apply(true); });
    apply(true);
  }
})();
"""

SEARCH_JS = r"""(function () {
  'use strict';
  var q = document.getElementById('q'), ringSel = document.getElementById('ring'),
      stSel = document.getElementById('state'), tomb = document.getElementById('tomb'),
      out = document.getElementById('results'), count = document.getElementById('count');
  var recs = [], C = {};
  function norm(s) { return (s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim(); }
  function el(tag, text, attrs) {
    var n = document.createElement(tag);
    if (text !== undefined && text !== null) n.textContent = text;
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    return n;
  }
  fetch('orgs.json').then(function (r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }).then(function (d) {
    d.cols.forEach(function (c, i) { C[c] = i; });
    recs = d.rows.map(function (r) {
      return {r: r, name: norm(r[C.name]), hay: norm([r[C.name], r[C.trade], r[C.city], r[C.st]].join(' '))};
    });
    var states = {};
    d.rows.forEach(function (r) { if (r[C.st]) states[r[C.st]] = 1; });
    Object.keys(states).sort().forEach(function (s) { stSel.appendChild(el('option', s, {value: s})); });
    var m = /[?&]q=([^&]*)/.exec(location.search);
    if (m) q.value = decodeURIComponent(m[1].replace(/\+/g, ' '));
    run();
  }).catch(function (e) {
    count.textContent = 'Could not load orgs.json (' + e.message + '). If you opened this file directly from disk, serve the folder over http instead (see docs/SITE_HOWTO.md).';
  });
  var timer;
  function later() { clearTimeout(timer); timer = setTimeout(run, 120); }
  [q, ringSel, stSel, tomb].forEach(function (n) { n.addEventListener('input', later); n.addEventListener('change', later); });
  function run() {
    var query = norm(q.value), terms = query ? query.split(' ') : [];
    var ring = ringSel.value, st = stSel.value, inclTomb = tomb.checked;
    var hits = [];
    recs.forEach(function (x) {
      var r = x.r;
      if (ring && String(r[C.ring] || '') !== ring) return;
      if (st && r[C.st] !== st) return;
      if (!inclTomb && ['acquired', 'merged', 'closed'].indexOf(r[C.status]) >= 0) return;
      var score = 3;
      if (terms.length) {
        for (var i = 0; i < terms.length; i++) if (x.hay.indexOf(terms[i]) < 0) return;
        if (x.name.indexOf(query) === 0) score = 0;
        else if (x.name.indexOf(query) >= 0) score = 1;
        else if (terms.every(function (t) { return x.name.indexOf(t) >= 0; })) score = 2;
      } else if (!ring && !st) { return; }
      hits.push([score, r[C.status] === 'active' ? 0 : 1, x.name, r]);
    });
    hits.sort(function (a, b) { return a[0] - b[0] || a[1] - b[1] || (a[2] < b[2] ? -1 : a[2] > b[2] ? 1 : 0); });
    out.textContent = '';
    var cap = 200;
    hits.slice(0, cap).forEach(function (h) {
      var r = h[3], li = el('li');
      li.appendChild(el('a', r[C.name], {href: 'orgs/' + r[C.id] + '.html'}));
      var meta = [r[C.kind] === 'e' ? 'Ecosystem organization' : 'Organization',
        [r[C.city], r[C.st]].filter(Boolean).join(', '),
        r[C.ring] ? 'Ring ' + r[C.ring] : '', r[C.tier] ? 'Tier ' + r[C.tier] : '',
        r[C.status] && r[C.status] !== 'active' ? 'status: ' + String(r[C.status]).replace(/_/g, ' ') : ''
      ].filter(Boolean).join(' | ');
      li.appendChild(el('div', meta, {'class': 'meta'}));
      out.appendChild(li);
    });
    if (!terms.length && !ring && !st) count.textContent = 'Type a name, trade name or city to search ' + recs.length.toLocaleString() + ' organization rows (organizations and ecosystem organizations, all statuses and tiers).';
    else count.textContent = hits.length.toLocaleString() + ' organization row' + (hits.length === 1 ? '' : 's') + ' match' + (hits.length > cap ? ' (showing the first ' + cap + ')' : '') + '.';
  }
})();
"""


# --------------------------------------------------------------------------
# pages


def active_ab(sites):
    return [s for s in sites if s.get("operating_status") == "active"
            and s.get("verification_tier") in ("A", "B", "C")]


def build_index(ctx):
    a = ctx.atlas
    sites = a.sites
    oh = [s for s in sites if s.get("state") == "OH"]
    pic = [s for s in oh if s.get("county") in PIC12]
    n_org_active = [o for o in a.orgs.values() if o.get("status") == "active"
                    and o.get("verification_tier") in ("A", "B", "C")]
    oh_active_org_ids = {s["org_id"] for s in active_ab(oh)}
    parents_oh = [o for o in n_org_active if o["org_id"] in oh_active_org_ids]
    eco_active = [e for e in a.eco.values() if e.get("status") == "active"
                  and e.get("verification_tier") in ("A", "B", "C")]
    prog_active = [p for p in a.programs if p.get("status") == "active"]
    u_sites = [s for s in sites if s.get("verification_tier") == "U"]
    u_orgs = [o for o in a.orgs.values() if o.get("verification_tier") == "U"]
    with_coords = [s for s in sites if nonempty(s.get("latitude"))]

    def card(num, unit, filt):
        return (f'<div class="card"><div class="big">{fmt_int(num)}</div>'
                f'<div class="unit">{esc(unit)}</div><div class="filter">{esc(filt)}</div></div>')

    cards = "".join([
        card(len(active_ab(sites)), "Site rows", "All locations held (US states, territories and a few non-US rows); operating status active; verification tiers A-C"),
        card(len(active_ab(oh)), "Ohio site rows", "State = OH; operating status active; verification tiers A-C"),
        card(len(active_ab(pic)), "PIC-12 county site rows", "Ohio county in the 12 PIC counties; operating status active; tiers A-C"),
        card(len(n_org_active), "Organization rows (parents)", "Status active; verification tiers A-C; all states"),
        card(len(parents_oh), "Parent organization rows with an Ohio footprint", "Organization status active, tiers A-C, and at least one active Ohio site row in tiers A-C"),
        card(len(eco_active), "Ecosystem organization rows", "Ring 5 (schools, associations, economic development, labs); status active; tiers A-C"),
        card(len(prog_active), "Program rows", "Education, training and research programs with status active; all tiers"),
    ])
    ring_groups = defaultdict(list)
    for s in active_ab(sites):
        ring_groups[s["_ring"] or "?"].append(s)
    ring_rows = "".join(
        f'<tr><th scope="row">{ring_badge(r)} {esc(RINGS.get(r, "Ring not recorded"))}</th>'
        f'<td class="num">{fmt_int(len(ring_groups.get(r, [])))}</td>'
        f'<td>{esc(RING_TESTS.get(r, ""))}</td></tr>'
        for r in ["1", "2", "3", "4", "5", "?"] if r != "?" or ring_groups.get("?"))
    ring_tbl = table_wrap(
        "<table><caption>Site rows by ring (operating status active; tiers A-C; all states)</caption>"
        "<thead><tr><th scope=\"col\">Ring</th><th scope=\"col\" class=\"num\">Site rows</th>"
        f"<th scope=\"col\">One-line test</th></tr></thead><tbody>{ring_rows}</tbody></table>",
        "Site rows by ring")
    tier_rows = "".join(
        f'<tr><th scope="row">{tier_badge(t)}</th><td>{esc(TIERS[t][0])}</td><td>{esc(TIERS[t][1])}</td></tr>'
        for t in TIER_ORDER)
    tier_tbl = table_wrap(
        "<table><caption>Verification tiers</caption><thead><tr><th scope=\"col\">Tier</th>"
        "<th scope=\"col\">Meaning</th><th scope=\"col\">Typical sources</th></tr></thead>"
        f"<tbody>{tier_rows}</tbody></table>", "Verification tiers")
    body = f"""
<h1>Polymer Industry Atlas</h1>
<p class="lede">An open, source-backed database of the US polymer, plastics and rubber industry: companies,
plants, materials producers, the value chain, downstream OEMs, and the ecosystem of universities,
associations, nonprofits and economic-development organizations that supports them. Built for the
Polymer Industry Cluster (PIC), Greater Akron Chamber, with a focus on Ohio and Northeast Ohio.</p>
<p><a href="map.html">Open the map</a> &middot; <a href="search.html">Search organizations</a> &middot;
<a href="counties/index.html">Ohio county one-pagers (PIC-12)</a></p>

<h2 id="counts">Headline counts</h2>
<p>{esc(SOURCE_CLASS_NOTE)} Verification tier U (unverified candidates) is not counted in the headline
figures below: there are {fmt_int(len(u_sites))} tier U site rows and {fmt_int(len(u_orgs))} tier U
organization rows held but excluded here.</p>
<div class="cards">{cards}</div>
<p class="small muted">All figures are rows in the Atlas, not industry totals, and not unique ultimate
parents. Official benchmarks (BLS QCEW) are shown on the county pages as count benchmarks, not matched
coverage. For comparison, the database holds {fmt_int(len(sites))} site rows, {fmt_int(len(a.orgs))}
organization rows and {fmt_int(len(a.eco))} ecosystem organization rows in total, across all statuses and all
tiers (including candidates and tombstones); {fmt_int(len(with_coords))} of the site rows carry
reference coordinates.</p>

<h2 id="rings">The five rings</h2>
{ring_tbl}
<p class="small muted">A site's ring may differ from its parent's. Where a site row has no ring recorded,
pages show the parent organization's ring, marked with an asterisk.</p>

<h2 id="tiers">Verification tiers</h2>
{tier_tbl}
<p class="small muted">A record's tier is the tier of its weakest must-have field.</p>

<h2 id="about">About the data</h2>
<ul>
<li>Canonical data is CSV in the <a href="{esc(ctx.repo_url)}" rel="noopener">project repository</a>.
This site is generated from it and carries no data of its own.</li>
<li>Every record carries at least one source, a verification tier and the date it was last verified.
NAICS codes are shown with their provenance because companies rarely publish a corporate 6-digit NAICS.</li>
<li>Licensed sources (trade-press rankings, commercial databases) are discovery leads only and are never
republished; every fact is cited to a primary or public source.</li>
<li>Coordinates on the map are reference data (interpolated from addresses, not rooftop) and are never evidence.</li>
<li>No personal contact data is published. University and federal-laboratory researchers appear only with
publicly stated name, role, research specialty and public profile URL, on their institution's page.
To request a correction or removal, open an issue in the repository.</li>
</ul>
<h2 id="license">License and attribution</h2>
<p>Original database content compiled here is licensed
<a href="https://creativecommons.org/licenses/by/4.0/" rel="noopener">CC BY 4.0</a>; scripts are MIT.
Please attribute "Polymer Industry Atlas, Polymer Industry Cluster (PIC), Greater Akron Chamber".</p>
<p class="muted">{ctx.asof()}</p>
"""
    return page(ctx, "Home", body, "", "index")


def build_map_page(ctx, data_rows):
    states = sorted({r[6] for r in data_rows if r[6]})
    rings_cb = "".join(
        f'<label><input type="checkbox" name="ring" value="{r}" checked> '
        f'<span class="swatch" style="background:var(--r{r})"></span>Ring {r}: {esc(RINGS[r])}</label>'
        for r in RINGS)
    rings_cb += ('<label><input type="checkbox" name="ring" value="x" checked> '
                 '<span class="swatch" style="background:var(--rx)"></span>Ring not recorded</label>')
    tiers_cb = "".join(
        f'<label><input type="checkbox" name="tier" value="{t}" checked> Tier {t}: {esc(TIERS[t][0])}</label>'
        for t in TIER_ORDER)
    states_cb = "".join(
        f'<label><input type="checkbox" name="state" value="{esc(s)}" checked> {esc(s)}</label>' for s in states)
    n_sites = len(ctx.atlas.sites)
    body = f"""
<h1>Map of sites</h1>
<p class="lede">Physical establishments (site rows) that have coordinates, colored by ring. Use the filters to
narrow by ring, verification tier and state. Click a dot for details and a link to the parent organization.</p>
<div class="banner note"><strong>Coordinates are reference data.</strong> They are interpolated from street
addresses (not rooftop locations) and are never evidence of a site's existence, scope or verification tier.
{fmt_int(len(data_rows))} of {fmt_int(n_sites)} site rows carry coordinates; the others are not on the map.
By default only sites with operating status active are shown. Dots for Ring 5 are
ecosystem organizations. A ring marked with an asterisk in a popup is inherited from the parent
organization because the site row has no ring of its own.</div>
<form id="filters" onsubmit="return false">
<div class="filters">
<fieldset><legend>Ring</legend>{rings_cb}</fieldset>
<fieldset><legend>Verification tier</legend>{tiers_cb}
<label><input type="checkbox" id="f-allstatus"> Include closed, idled and unknown-status sites</label></fieldset>
<fieldset><legend>State</legend>
<div class="btn-row"><button type="button" id="st-all">All</button><button type="button" id="st-oh">Ohio only</button><button type="button" id="st-none">None</button></div>
<div class="scroll">{states_cb}</div></fieldset>
</div>
<div class="btn-row"><button type="button" id="fit">Zoom to visible sites</button></div>
</form>
<p id="map-status" role="status" aria-live="polite">Loading map data...</p>
<div id="map" role="application" aria-label="Map of polymer industry sites"></div>
<noscript><p>The map needs JavaScript. County pages and search are available without the map.</p></noscript>
<p class="small muted">The map is not keyboard-navigable; every site on it is also listed on its
<a href="counties/index.html">county page</a> (PIC-12) or its organization page, reachable via
<a href="search.html">search</a>. Map tiles &copy; OpenStreetMap contributors.</p>
"""
    head = (f'<link rel="stylesheet" href="{LEAFLET}leaflet.css" integrity="{LEAFLET_CSS_SRI}" crossorigin="">')
    scripts = (f'<script src="{LEAFLET}leaflet.js" integrity="{LEAFLET_JS_SRI}" crossorigin=""></script>\n'
               '<script src="map.js"></script>')
    return page(ctx, "Map", body, "", "map", "Map of polymer industry sites by ring.", head, scripts)


def sites_json(ctx):
    """Compact site data for the map (only rows with coordinates)."""
    a = ctx.atlas
    cols = ["id", "lat", "lon", "name", "org", "city", "st", "ring", "inh", "tier", "status"]
    rows, orgs = [], {}
    for s in a.sites:
        try:
            lat, lon = float(s["latitude"]), float(s["longitude"])
        except (TypeError, ValueError, KeyError):
            continue
        rows.append([s["site_id"], round(lat, 5), round(lon, 5), s.get("site_name") or "",
                     s["org_id"], s.get("city") or "", s.get("state") or "",
                     s["_ring"] or "", 1 if s["_ring_inherited"] else 0,
                     s.get("verification_tier") or "", s.get("operating_status") or ""])
        orgs[s["org_id"]] = a.name_of(s["org_id"]) or ""
    return {"cols": cols, "orgs": orgs, "rows": rows}


def build_search_page(ctx, n):
    ring_opts = '<option value="">Any ring</option>' + "".join(
        f'<option value="{r}">Ring {r}: {esc(RINGS[r])}</option>' for r in RINGS)
    body = f"""
<h1>Search organizations</h1>
<p class="lede">Search {fmt_int(n)} organization rows (organizations and ecosystem organizations; all statuses
and all verification tiers) by name, trade name or city. Results are records, not unique companies.</p>
<form onsubmit="return false" role="search">
<p><label for="q"><strong>Name, trade name or city</strong></label><br>
<input type="search" id="q" autocomplete="off" autofocus></p>
<div class="filters">
<p><label for="ring">Ring</label><br><select id="ring">{ring_opts}</select></p>
<p><label for="state">HQ state</label><br><select id="state"><option value="">Any state</option></select></p>
<p><label><input type="checkbox" id="tomb" checked> Include closed, acquired and merged records</label></p>
</div>
</form>
<p id="count" role="status" aria-live="polite">Loading index...</p>
<ul id="results" class="results"></ul>
<noscript><p>Search needs JavaScript.</p></noscript>
"""
    return page(ctx, "Search", body, "", "search", "Search the Atlas by organization name.", "",
                '<script src="search.js"></script>')


def orgs_json(ctx):
    a = ctx.atlas
    cols = ["id", "name", "trade", "city", "st", "ring", "kind", "status", "tier"]
    rows = []
    for o in a.orgs.values():
        rows.append([safe_id(o["org_id"]), o.get("legal_name") or "", o.get("trade_names") or "",
                     o.get("hq_city") or "", o.get("hq_state") or "", o.get("ring_primary") or "",
                     "o", o.get("status") or "", o.get("verification_tier") or ""])
    for e in a.eco.values():
        rows.append([safe_id(e["org_id"]), e.get("legal_name") or "", "", e.get("city") or "",
                     e.get("state") or "", "5", "e", e.get("status") or "", e.get("verification_tier") or ""])
    rows.sort(key=lambda r: (r[1].lower(), r[0]))
    return {"cols": cols, "rows": rows}


def dl(pairs):
    """Definition list from (label, html) pairs; empty values are skipped."""
    items = "".join(f"<dt>{esc(k)}</dt><dd>{v}</dd>" for k, v in pairs if v not in (None, ""))
    return f'<dl class="fields">{items}</dl>' if items else ""


def site_article(s, a):
    addr = ", ".join(x for x in [s.get("street_address"), s.get("city")] if nonempty(x))
    region = " ".join(x for x in [s.get("state"), s.get("zip")] if nonempty(x))
    if region:
        addr = f"{addr}, {region}" if addr else region
    county = f"{s['county']} County" if nonempty(s.get("county")) else ""
    naics = ""
    if nonempty(s.get("naics_primary")):
        naics = esc(s["naics_primary"])
        if nonempty(s.get("naics_primary_source_type")):
            naics += f" ({esc(str(s['naics_primary_source_type']).replace('_', ' '))}"
            if nonempty(s.get("naics_confidence")):
                naics += f", confidence {esc(s['naics_confidence'])}"
            naics += ")"
    fields = dl([
        ("Address", esc(addr)), ("County", esc(county)), ("Site type", esc(vocab(s.get("site_type")))),
        ("Ring", ring_badge(s["_ring"], s["_ring_inherited"]) if s["_ring"] else ""),
        ("Operating status", status_badge(s.get("operating_status"))),
        ("Verification tier", tier_badge(s.get("verification_tier"))),
        ("Last verified", esc(s.get("last_verified"))),
        ("NAICS (site)", naics), ("Processes", esc(vocab(s.get("processes")))),
        ("Materials", esc(vocab(s.get("materials")))),
        ("Markets served", esc(vocab(s.get("markets_served")))),
        ("Site employee band", esc(s.get("employee_band_site"))),
    ])
    return (f'<article class="site" id="{esc(safe_id(s["site_id"]))}">'
            f'<h3>{esc(s.get("site_name") or s["site_id"])} <span class="muted small">{esc(s["site_id"])}</span></h3>'
            f'{fields}<details><summary>Sources for this site</summary>{source_list(s.get("sources"))}</details></article>')


def program_table(programs, a, with_inst=False, root=""):
    if not programs:
        return ""
    head = ("<th scope=\"col\">Program</th>" + ("<th scope=\"col\">Institution</th>" if with_inst else "") +
            "<th scope=\"col\">Type</th><th scope=\"col\">Level</th><th scope=\"col\">Tier</th>")
    body = ""
    for p in sorted(programs, key=lambda p: (p.get("program_name") or "")):
        name = esc(p.get("program_name"))
        href = safe_href(p.get("url") or p.get("public_door_url"))
        if href:
            name = f'<a href="{esc(href)}" rel="noopener nofollow">{name}</a>'
        body += (f"<tr><td>{name}</td>"
                 + (f"<td>{a.org_link(p.get('institution_org_id'), root)}</td>" if with_inst else "")
                 + f"<td>{esc(vocab(p.get('program_type')))}</td><td>{esc(vocab(p.get('level')))}</td>"
                 f"<td>{tier_badge(p.get('verification_tier'))}</td></tr>")
    return table_wrap(f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>", "Programs")


def people_block(people, ctx):
    """Professors / federal-lab research staff: only the public professional facts in people.csv."""
    if not people:
        return ""
    rows = ""
    for p in sorted(people, key=lambda p: (p.get("full_name") or "")):
        name = esc(p.get("full_name"))
        href = safe_href(p.get("public_profile_url"))
        if href and "@" in href:        # a profile URL embedding an email address is not published
            href = None
        if href:
            name = f'<a href="{esc(href)}" rel="noopener nofollow">{name}</a>'
        role = p.get("role_as_published") or str(p.get("role") or "").replace("_", " ")
        rows += (f"<tr><td>{name}</td><td>{esc(role)}</td>"
                 f"<td>{esc(vocab(p.get('research_specialties')))}</td></tr>")
    tbl = table_wrap("<table><thead><tr><th scope=\"col\">Name</th><th scope=\"col\">Role (as published)</th>"
                     f"<th scope=\"col\">Research specialties</th></tr></thead><tbody>{rows}</tbody></table>",
                     "Researchers")
    return (f"<h2>Researchers ({fmt_int(len(people))} public profile rows)</h2>"
            "<p class=\"small muted\">Name, role, research specialty and the public profile page, each from "
            "the institution's own public pages. To request a correction or removal, "
            f"<a href=\"{esc(ctx.repo_url)}/issues\" rel=\"noopener\">open an issue</a>.</p>{tbl}")


def tombstone_banner(rec, successor_id, a, kind):
    status = rec.get("status")
    if status in TOMBSTONE_STATUSES:
        when = f" as of {esc(rec.get('status_date'))}" if nonempty(rec.get("status_date")) else ""
        succ = ""
        if successor_id:
            succ = f' Successor record: {a.org_link(successor_id)}.'
        return (f'<div class="banner tombstone" role="note"><strong>Tombstone record: {esc(status)}{when}.</strong> '
                f'This {kind} is kept for history and is not counted as operating.{succ}</div>')
    if status and status != "active":
        return (f'<div class="banner" role="note"><strong>Status: {esc(str(status).replace("_", " "))}.</strong> '
                'Operating status has not been established by dated evidence.</div>')
    return ""


def build_org_page(ctx, o):
    a = ctx.atlas
    oid = o["org_id"]
    successor = o.get("successor_org_id") or a.merged_into.get(oid)
    parent = ""
    if nonempty(o.get("parent_org_id")):
        parent = a.org_link(o["parent_org_id"])
    ult = o.get("ultimate_parent_name")
    ult = esc(ult) if nonempty(ult) and ult != o.get("legal_name") else ""
    kids = a.children.get(oid, [])
    kids_html = ""
    if kids:
        kids_html = "<ul>" + "".join(
            f"<li>{a.org_link(k['org_id'])} {status_badge(k.get('status')) if k.get('status') != 'active' else ''}</li>"
            for k in sorted(kids, key=lambda k: k["legal_name"] or "")) + "</ul>"
    naics = ""
    if nonempty(o.get("naics_primary")):
        naics = esc(o["naics_primary"])
        lab = naics_label(o["naics_primary"], a.ref_titles)
        if lab:
            naics += f" ({esc(lab)})"
        bits = []
        if nonempty(o.get("naics_primary_source_type")):
            bits.append("source type: " + esc(str(o["naics_primary_source_type"]).replace("_", " ")))
        if nonempty(o.get("naics_confidence")):
            bits.append("confidence: " + esc(o["naics_confidence"]))
        if bits:
            naics += f' <span class="muted">({"; ".join(bits)})</span>'
    hq = ", ".join(x for x in [o.get("hq_city"), o.get("hq_state")] if nonempty(x))
    member = ""
    if o.get("pic_member") == "true":
        member = "PIC member (public member list)"
        if safe_href(o.get("membership_source_url")):
            member = f'<a href="{esc(o["membership_source_url"])}" rel="noopener nofollow">{member}</a>'
        else:
            member = esc(member)
    rings = ring_badge(o.get("ring_primary")) if nonempty(o.get("ring_primary")) else ""
    if nonempty(o.get("ring_secondary")):
        rings += f' <span class="muted">secondary:</span> {ring_badge(o["ring_secondary"])}'
    site_rows = sorted(a.sites_by_org.get(oid, []), key=lambda s: (s.get("state") or "", s.get("city") or "", s["site_id"]))
    n_active = sum(1 for s in site_rows if s.get("operating_status") == "active")
    sites_html = ""
    if site_rows:
        sites_html = (f"<h2>Sites ({fmt_int(len(site_rows))} site rows; {fmt_int(n_active)} with operating status active)</h2>"
                      "<p class=\"small muted\">Site rows are physical establishments (plants, headquarters, "
                      "labs, warehouses). Each is owned by the operator."
                      + (" An asterisk (*) next to a ring means the site row records no ring, so the parent organization's ring is shown."
                         if any(s["_ring_inherited"] for s in site_rows) else "") + "</p>"
                      + "".join(site_article(s, a) for s in site_rows))
    fields = dl([
        ("Record ID", esc(oid)), ("Status", status_badge(o.get("status"))),
        ("Status date", esc(o.get("status_date"))), ("Ring", rings),
        ("Entity type", esc(vocab(o.get("entity_type")))),
        ("Headquarters", esc(hq)), ("Website", ext_link(o.get("website"))),
        ("Parent organization", parent), ("Ultimate parent (as named)", ult),
        ("Year founded", esc(o.get("year_founded"))), ("Stock ticker", esc(o.get("stock_ticker"))),
        ("Ownership", esc(vocab(o.get("ownership_type")))),
        ("Primary NAICS", naics), ("Processes", esc(vocab(o.get("processes")))),
        ("Materials", esc(vocab(o.get("materials")))),
        ("Markets served", esc(vocab(o.get("markets_served")))),
        ("Certifications", esc(vocab(o.get("certifications")))),
        ("Ohio employee band", esc(o.get("employee_band_ohio"))),
        ("PIC membership", member),
        ("Verification tier", tier_badge(o.get("verification_tier"))),
        ("Last verified", esc(o.get("last_verified"))),
    ])
    body = f"""
<p class="small"><a href="../search.html">Search</a> &rsaquo; Organization</p>
<h1>{esc(o.get("legal_name"))}</h1>
{('<p class="muted">Also known as: ' + esc(vocab(o.get("trade_names"))) + '</p>') if nonempty(o.get("trade_names")) else ''}
{tombstone_banner(o, successor, a, "organization record")}
{lede(o.get("description_1line"))}
{fields}
{('<h2>Subsidiary and child organizations</h2>' + kids_html) if kids_html else ''}
{sites_html}
<h2>Sources</h2>
<p class="small muted">Organization-level sources. Last verified {esc(o.get("last_verified")) or "n/a"}; tier {esc(o.get("verification_tier")) or "n/a"}.</p>
{source_list(o.get("sources"))}
"""
    return page(ctx, o.get("legal_name") or oid, body, "../", "",
                f"{o.get('legal_name') or oid}: Polymer Industry Atlas record.")


def build_eco_page(ctx, e):
    a = ctx.atlas
    eid = e["org_id"]
    successor = a.merged_into.get(eid)
    loc = ", ".join(x for x in [e.get("city"), e.get("state")] if nonempty(x))
    county = f"{e['county']} County" if nonempty(e.get("county")) else ""
    member = ""
    if e.get("pic_member") == "true":
        member = "PIC member (public member list)"
        if safe_href(e.get("membership_source_url")):
            member = f'<a href="{esc(e["membership_source_url"])}" rel="noopener nofollow">{member}</a>'
        else:
            member = esc(member)
    parent_inst = a.org_link(e["parent_institution_org_id"]) if nonempty(e.get("parent_institution_org_id")) else ""
    fields = dl([
        ("Record ID", esc(eid)), ("Status", status_badge(e.get("status"))),
        ("Ring", ring_badge("5")),
        ("Ecosystem type", esc(vocab(e.get("ecosystem_subtype")))),
        ("Part of", parent_inst),
        ("Location", esc(loc)), ("County", esc(county)), ("Website", ext_link(e.get("website"))),
        ("Polymer program", esc(e.get("polymer_program_name") or "")),
        ("Program page", ext_link(e.get("polymer_program_url"))),
        ("Services offered", esc(vocab(e.get("services_offered")))),
        ("Geography served", esc(vocab(e.get("geography_served")))),
        ("Industry partnership modes", esc(vocab(e.get("industry_partnership_modes")))),
        ("Technology areas", esc(vocab(e.get("technology_areas")))),
        ("PIC membership", member),
        ("Verification tier", tier_badge(e.get("verification_tier"))),
        ("Last verified", esc(e.get("last_verified"))),
    ])
    progs = a.programs_by_inst.get(eid, [])
    progs_html = (f"<h2>Programs ({fmt_int(len(progs))} program rows)</h2>" + program_table(progs, a)) if progs else ""
    site_rows = sorted(a.sites_by_org.get(eid, []), key=lambda s: (s.get("state") or "", s.get("city") or ""))
    sites_html = ""
    if site_rows:
        sites_html = (f"<h2>Locations ({fmt_int(len(site_rows))} site rows)</h2>"
                      + "".join(site_article(s, a) for s in site_rows))
    body = f"""
<p class="small"><a href="../search.html">Search</a> &rsaquo; Ecosystem organization</p>
<h1>{esc(e.get("legal_name"))}</h1>
{tombstone_banner(e, successor, a, "ecosystem record")}
{lede(e.get("description_1line"))}
{fields}
{progs_html}
{people_block(a.people_by_inst.get(eid, []), ctx)}
{sites_html}
<h2>Sources</h2>
<p class="small muted">Last verified {esc(e.get("last_verified")) or "n/a"}; tier {esc(e.get("verification_tier")) or "n/a"}.</p>
{source_list(e.get("sources"))}
"""
    return page(ctx, e.get("legal_name") or eid, body, "../", "",
                f"{e.get('legal_name') or eid}: Polymer Industry Atlas ecosystem record.")


def build_county_page(ctx, county):
    a = ctx.atlas
    sites = [s for s in a.sites if s.get("state") == "OH" and s.get("county") == county]
    active = [s for s in sites if s.get("operating_status") == "active"]
    not_active = len(sites) - len(active)
    org_ids = {s["org_id"] for s in active}
    ring_groups = defaultdict(list)
    for s in active:
        ring_groups[s["_ring"] or "?"].append(s)
    ring_order = [r for r in ["1", "2", "3", "4", "5", "?"] if r != "?" or ring_groups.get("?")]
    ring_tbl = breakdown_table(
        "Ring", ring_groups, ring_order,
        lambda r: (ring_badge(r) + " " + esc(RINGS[r])) if r in RINGS else "Ring not recorded",
        f"{county} County site rows by ring (Ohio; operating status active; all tiers)")
    naics_groups = defaultdict(list)
    for s in active:
        n = (s.get("naics_primary") or "")[:3] or "?"
        naics_groups[n].append(s)
    naics_order = sorted(naics_groups, key=lambda n: (-len(naics_groups[n]), n))

    def naics_lbl(n):
        if n == "?":
            return "Not stated at site level"
        lab = naics_label(n, a.ref_titles)
        return f"{esc(n)} {esc(lab)}".strip()
    naics_tbl = breakdown_table(
        "NAICS (first 3 digits)", naics_groups, naics_order, naics_lbl,
        f"{county} County site rows by site NAICS, first 3 digits (Ohio; operating status active; all tiers)")

    q = ctx.qcew.get(county)
    if q:
        def qv(k, money=False):
            v = q.get(k)
            if not nonempty(v):
                return "withheld"
            return ("$" if money else "") + fmt_int(int(float(v)))
        disc = (f' BLS disclosure code: {esc(q["disclosure_code"])}.' if nonempty(q.get("disclosure_code")) else "")
        qcew_html = f"""<div class="banner note"><strong>BLS QCEW 2023 benchmark, private-sector NAICS 326
(Plastics and Rubber Products Manufacturing), {esc(county)} County, Ohio.</strong> This is a <em>count
benchmark</em>, not matched coverage: it counts establishments and jobs in one NAICS sector, while the Atlas
rows above span Rings 1-5 and many NAICS codes. Do not divide one by the other as a coverage rate.</div>
{table_wrap(f'''<table><caption>QCEW annual averages, 2023, private ownership, NAICS 326, FIPS {esc(q["area_fips"])}</caption>
<thead><tr><th scope="col" class="num">Establishments (annual average)</th><th scope="col" class="num">Employment (annual average)</th>
<th scope="col" class="num">Total annual wages</th><th scope="col" class="num">Average annual pay</th></tr></thead>
<tbody><tr><td class="num">{qv("annual_avg_estabs")}</td><td class="num">{qv("annual_avg_emplvl")}</td>
<td class="num">{qv("total_annual_wages", True)}</td><td class="num">{qv("avg_annual_pay", True)}</td></tr></tbody></table>''', "QCEW benchmark")}
<p class="small muted">Source: BLS Quarterly Census of Employment and Wages,
<a href="https://data.bls.gov/cew/data/api/2023/a/industry/326.csv" rel="noopener">2023 annual, industry 326</a>,
as compiled in docs/denominators/ of the repository.{disc} "withheld" means BLS published the row without
that figure; it is not zero.</p>"""
    else:
        qcew_html = ('<p class="muted">No QCEW 2023 NAICS 326 row is available for this county in the '
                     'bundled benchmark file. A missing row is not a zero.</p>')

    srows = sorted(active, key=lambda s: (s["_ring"] or "9", (s.get("site_name") or "").lower()))
    body_rows = ""
    for s in srows:
        parent_name = a.name_of(s["org_id"]) or s["org_id"]
        body_rows += (
            f'<tr><td><a href="../orgs/{esc(safe_id(s["org_id"]))}.html#{esc(safe_id(s["site_id"]))}">{esc(s.get("site_name") or s["site_id"])}</a></td>'
            f'<td>{a.org_link(s["org_id"], "../orgs/") if a.name_of(s["org_id"]) else esc(parent_name)}</td>'
            f'<td>{esc(s.get("city"))}</td><td>{ring_badge(s["_ring"], s["_ring_inherited"])}</td>'
            f'<td>{esc(vocab(s.get("processes")))}</td><td>{tier_badge(s.get("verification_tier"))}</td></tr>')
    sites_tbl = table_wrap(
        "<table><caption>Site rows (Ohio; this county; operating status active; all tiers)</caption><thead><tr>"
        "<th scope=\"col\">Site</th><th scope=\"col\">Parent organization</th><th scope=\"col\">City</th>"
        "<th scope=\"col\">Ring</th><th scope=\"col\">Processes</th><th scope=\"col\">Tier</th></tr></thead>"
        f"<tbody>{body_rows}</tbody></table>", f"{county} County sites") if srows else "<p>No active site rows.</p>"

    progs = [p for p in a.programs if p.get("state") == "OH" and p.get("county") == county
             and p.get("status") == "active"]
    eco = sorted((e for e in a.eco.values() if e.get("state") == "OH" and e.get("county") == county),
                 key=lambda e: e["legal_name"] or "")
    eco_rows = "".join(
        f'<tr><td><a href="../orgs/{esc(safe_id(e["org_id"]))}.html">{esc(e["legal_name"])}</a></td>'
        f'<td>{esc(vocab(e.get("ecosystem_subtype")))}</td><td>{esc(e.get("city"))}</td>'
        f'<td>{status_badge(e.get("status"))}</td><td>{tier_badge(e.get("verification_tier"))}</td></tr>'
        for e in eco)
    eco_html = (table_wrap(
        "<table><caption>Ecosystem organization rows located in this county (all statuses, all tiers)</caption><thead><tr>"
        "<th scope=\"col\">Organization</th><th scope=\"col\">Type</th><th scope=\"col\">City</th>"
        "<th scope=\"col\">Status</th><th scope=\"col\">Tier</th></tr></thead>"
        f"<tbody>{eco_rows}</tbody></table>", "Ecosystem organizations") if eco else "<p>None recorded.</p>")
    progs_html = program_table(progs, a, with_inst=True, root="../orgs/") if progs else "<p>None recorded.</p>"

    body = f"""
<p class="small"><a href="index.html">Ohio counties</a> &rsaquo; {esc(county)}</p>
<h1>{esc(county)} County, Ohio</h1>
<p class="lede">One-page summary of the polymer industry records the Atlas holds for {esc(county)} County,
a PIC-12 county. {esc(SOURCE_CLASS_NOTE)}</p>
<div class="cards">
<div class="card"><div class="big">{fmt_int(len(active))}</div><div class="unit">Site rows</div><div class="filter">{esc(county)} County, Ohio; operating status active; all verification tiers</div></div>
<div class="card"><div class="big">{fmt_int(len(org_ids))}</div><div class="unit">Organization rows with an active site row here</div><div class="filter">distinct parent organizations of those site rows; all tiers</div></div>
<div class="card"><div class="big">{fmt_int(len(eco))}</div><div class="unit">Ecosystem organization rows</div><div class="filter">located in the county; all statuses and tiers</div></div>
<div class="card"><div class="big">{fmt_int(len(progs))}</div><div class="unit">Program rows</div><div class="filter">located in the county; status active; all tiers</div></div>
</div>
{f'<p class="small muted">{fmt_int(not_active)} further site row(s) in this county have another operating status (closed, idled, unknown, pre-revenue) and are not listed or counted.</p>' if not_active else ''}
<h2>Establishments by ring</h2>
{ring_tbl}
<p class="small muted">An asterisk (*) marks a ring inherited from the parent organization because the site row records none.
Tier U rows are candidates; they are included here because this page shows all tiers.</p>
<h2>Establishments by NAICS (3-digit)</h2>
{naics_tbl}
<p class="small muted">The site's own NAICS code is used. NAICS values are not company facts by default; see each site's provenance on its organization page.</p>
<h2>Benchmark: BLS QCEW</h2>
{qcew_html}
<h2>Sites</h2>
{sites_tbl}
<h2>Programs in {esc(county)} County</h2>
{progs_html}
<h2>Ecosystem organizations in {esc(county)} County</h2>
{eco_html}
"""
    return page(ctx, f"{county} County", body, "../", "counties",
                f"{county} County, Ohio: polymer industry establishments by ring and NAICS, programs, ecosystem and QCEW benchmark.")


def build_counties_index(ctx):
    a = ctx.atlas
    all_sites = defaultdict(list)
    for s in a.sites:
        if s.get("state") == "OH" and nonempty(s.get("county")):
            all_sites[s["county"]].append(s)
    eco_n, prog_n = Counter(), Counter()
    for e in a.eco.values():
        if e.get("state") == "OH" and nonempty(e.get("county")):
            eco_n[e["county"]] += 1
    for p in a.programs:
        if p.get("state") == "OH" and nonempty(p.get("county")) and p.get("status") == "active":
            prog_n[p["county"]] += 1
    names = sorted(set(all_sites) | set(PIC12) | set(eco_n))

    def row(c):
        sites = all_sites.get(c, [])
        n_act = sum(1 for s in sites if s.get("operating_status") == "active")
        label = (f'<a href="{esc(slug(c))}.html">{esc(c)}</a>' if c in PIC12 else esc(c))
        q = ctx.qcew.get(c)
        qn = fmt_int(int(float(q["annual_avg_estabs"]))) if q and nonempty(q.get("annual_avg_estabs")) else "n/a"
        return (f'<tr><th scope="row">{label}</th><td>{"PIC-12" if c in PIC12 else ""}</td>'
                f'<td class="num">{fmt_int(n_act)}</td><td class="num">{fmt_int(len(sites))}</td>'
                f'<td class="num">{fmt_int(eco_n.get(c, 0))}</td><td class="num">{fmt_int(prog_n.get(c, 0))}</td>'
                f'<td class="num">{qn}</td></tr>')
    pic_rows = "".join(row(c) for c in PIC12)
    other_rows = "".join(row(c) for c in names if c not in PIC12)
    head = ("<thead><tr><th scope=\"col\">County</th><th scope=\"col\">Group</th>"
            "<th scope=\"col\" class=\"num\">Site rows, active, all tiers</th>"
            "<th scope=\"col\" class=\"num\">Site rows, all statuses</th>"
            "<th scope=\"col\" class=\"num\">Ecosystem organization rows</th>"
            "<th scope=\"col\" class=\"num\">Program rows, active</th>"
            "<th scope=\"col\" class=\"num\">QCEW 2023 private NAICS 326 establishments (benchmark)</th></tr></thead>")
    body = f"""
<h1>Ohio counties</h1>
<p class="lede">County one-pagers for the 12 PIC-12 counties (Ashtabula, Cuyahoga, Geauga, Lake, Lorain,
Mahoning, Medina, Portage, Stark, Summit, Trumbull, Wayne). Other Ohio counties are listed with counts only.</p>
<p>All counts are Atlas database rows by the unit named in the column heading. The QCEW column is a
count benchmark from BLS, not matched coverage; "n/a" means the bundled benchmark file has no row for that
county, which is not a zero. County is taken from each site's physical address.</p>
<h2>PIC-12 counties</h2>
{table_wrap(f"<table><caption>PIC-12 counties</caption>{head}<tbody>{pic_rows}</tbody></table>", "PIC-12 counties")}
<h2>Other Ohio counties</h2>
{table_wrap(f"<table><caption>Other Ohio counties with at least one Atlas row</caption>{head}<tbody>{other_rows}</tbody></table>", "Other Ohio counties")}
"""
    return page(ctx, "Ohio counties", body, "../", "counties")


# --------------------------------------------------------------------------
# driver


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_site(db_path, out_dir, qcew_path=None, repo_url=DEFAULT_REPO, git=None, today=None):
    """Build the whole site. Returns {'pages': n, 'bytes': n, 'counts': {...}}."""
    db_path, out_dir = Path(db_path), Path(out_dir)
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        atlas = Atlas(con)
    finally:
        con.close()
    today = today or datetime.date.today().isoformat()
    db_date = datetime.datetime.fromtimestamp(db_path.stat().st_mtime).date().isoformat()
    ctx = Ctx(atlas, load_qcew(qcew_path), git or git_info(ROOT), repo_url, today, db_date)

    out_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("orgs", "counties"):          # only generated subdirs are cleared
        if (out_dir / sub).exists():
            shutil.rmtree(out_dir / sub)

    write(out_dir / "style.css", CSS.strip() + "\n")
    write(out_dir / "map.js", MAP_JS)
    write(out_dir / "search.js", SEARCH_JS)
    write(out_dir / ".nojekyll", "")
    write(out_dir / "index.html", build_index(ctx))

    sj = sites_json(ctx)
    assert sj["cols"][6] == "st"
    write(out_dir / "sites.json", json.dumps(sj, separators=(",", ":"), ensure_ascii=False))
    write(out_dir / "map.html", build_map_page(ctx, sj["rows"]))
    oj = orgs_json(ctx)
    write(out_dir / "orgs.json", json.dumps(oj, separators=(",", ":"), ensure_ascii=False))
    write(out_dir / "search.html", build_search_page(ctx, len(oj["rows"])))

    write(out_dir / "counties" / "index.html", build_counties_index(ctx))
    for c in PIC12:
        write(out_dir / "counties" / f"{slug(c)}.html", build_county_page(ctx, c))
    for o in atlas.orgs.values():
        write(out_dir / "orgs" / f"{safe_id(o['org_id'])}.html", build_org_page(ctx, o))
    for e in atlas.eco.values():
        if e["org_id"] in atlas.orgs:      # id clash would silently overwrite a page
            raise SystemExit(f"record id {e['org_id']} exists in both organizations and ecosystem")
        write(out_dir / "orgs" / f"{safe_id(e['org_id'])}.html", build_eco_page(ctx, e))

    files = [p for p in out_dir.rglob("*") if p.is_file()]
    html_files = [p for p in files if p.suffix == ".html"]
    return {"pages": len(html_files), "files": len(files), "bytes": sum(p.stat().st_size for p in files),
            "org_pages": len(atlas.orgs), "eco_pages": len(atlas.eco),
            "county_pages": len(PIC12), "map_sites": len(sj["rows"])}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--db", default=str(DEFAULT_DB), help="SQLite database (default build/polymer-atlas.db)")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="output directory (default build/site)")
    ap.add_argument("--qcew", default=str(DEFAULT_QCEW), help="QCEW county benchmark CSV")
    ap.add_argument("--repo-url", default=DEFAULT_REPO)
    ap.add_argument("--rebuild-db", action="store_true", help="run scripts/build_sqlite.py first")
    args = ap.parse_args(argv)
    db = Path(args.db)
    if args.rebuild_db or (not db.exists() and db.resolve() == DEFAULT_DB.resolve()):
        print("Building database with scripts/build_sqlite.py ...")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_sqlite.py")], check=True, cwd=ROOT,
                       stdout=subprocess.DEVNULL)
    if not db.exists():
        raise SystemExit(f"database not found: {db}")
    res = build_site(db, args.out, args.qcew, args.repo_url)
    print(f"Built {args.out}: {res['pages']} HTML pages "
          f"({res['org_pages']} organization, {res['eco_pages']} ecosystem, {res['county_pages']} county + index, "
          f"index/map/search), {res['files']} files, {res['bytes'] / 1e6:.1f} MB; "
          f"{res['map_sites']} site rows on the map")


if __name__ == "__main__":
    main()
