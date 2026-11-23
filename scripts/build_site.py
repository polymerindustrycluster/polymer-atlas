#!/usr/bin/env python3
"""Static site generator for the Polymer Industry Atlas. Stdlib only.

Reads build/polymer-atlas.db (building it with scripts/build_sqlite.py when it
is missing) and writes a self-contained static site to build/site/:

    index.html            what the Atlas is, headline counts (unit + filter)
    directory.html        Northeast Ohio polymer companies (the "Find companies" page)
    skyline.html          the 3D skyline (the only page that loads three.js)
    map.html + sites.json Leaflet map of sites that carry coordinates
    search.html + orgs.json  client-side search over organizations/ecosystem
    counties/index.html, counties/<county>.html   Ohio county pages (PIC-18 first)
    orgs/<org_id>.html    one page per organization and ecosystem org
    style.css, shell.js, sortable.js, map.js, search.js

Every page, the three graph pages of build_graph.py, build_geo_graph.py and
build_events_3d.py included, is rendered by page() below: one header, five-item
menu, footer and stylesheet.

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
import importlib.util
import csv
import io
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

# JavaScript libraries are vendored (scripts/assets/vendor/<lib>/, npm registry pins, see vendor_libs.py) and published at vendor/<lib>/.
VENDOR_LIBS = ("3d-force-graph", "d3", "graphology", "graphology-library", "leaflet", "sigma", "topojson-client")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from regions import PIC18, JOBSOHIO_REGION, REGION_LABEL  # noqa: E402  (AGENTS.md section 8)
PIC12 = PIC18  # the reporting region: PIC-18 since the owner ruling of 2026-11-03 (name kept for callers)

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


def plural(n, one, many=None):
    """'1 site row', '2 site rows': a count with its unit, in the right number."""
    return f"{fmt_int(n)} {one if n == 1 else (many or one + 's')}"


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


# Free text from source strings and evidence rows (claim text, notes, citations) is never published: it can quote a scraped
# page or name a person, and no pattern filter makes free text safe. Pages show structured fields and the source links only.
def public_url(url):
    """An http(s) link that is not an email address or a personal profile page."""
    return bool(safe_href(url)) and "@" not in url and not re.search(r"linkedin\.com/(in|pub)/", url, re.I)


def source_urls(text):
    """Distinct public URLs in a source string, in order: the only part of a citation the site shows."""
    seen = []
    for m in URL_RE.finditer(str(text or "")):
        u = m.group(0).rstrip(".,;:")
        if public_url(u) and u not in seen:
            seen.append(u)
    return seen


def url_links(urls):
    return " ".join(f'<a href="{esc(u)}" rel="noopener nofollow">{esc(u)}</a>' for u in urls)


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
    urls = source_urls(sources)
    if not urls:
        return '<p class="muted">No source link recorded.</p>'
    return '<ul class="sources">' + "".join(f"<li>{url_links([u])}</li>" for u in urls) + "</ul>"


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
        # [v1.9] equipment (SCHEMA 4.19) and people engagement (4.20); live rows only (no withdrawn_date)
        self.equipment_by_host = defaultdict(list)
        for r in rows_of(con, "equipment"):
            if not (r.get("withdrawn_date") or "").strip():
                self.equipment_by_host[r.get("host_org_id")].append(r)
        self.engagement_by_person = defaultdict(list)
        for r in rows_of(con, "people_engagement"):
            if not (r.get("withdrawn_date") or "").strip():
                self.engagement_by_person[r.get("person_id")].append(r)
        self.rels = rows_of(con, "relationships")
        self.evidence = defaultdict(list)   # (record_table, record_id) -> evidence rows (SCHEMA 4.13)
        for r in rows_of(con, "evidence"):
            self.evidence[(r.get("record_table"), r.get("record_id"))].append(r)
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

# The five menu items (owner ruling 2026-11-23, ATLAS-40). Map is the street map; the other three map and graph views and the
# 3D skyline sit one click away in the "Views" strip shown under the header on those pages.
NAV = [("directory", "Find companies", "directory.html"), ("map", "Map", "map.html"), ("counties", "Counties", "counties/index.html"),
       ("experts", "Research & programs", "experts.html"), ("about", "About the data", "index.html#method")]
VIEWS = [("map", "Street map", "map.html"), ("geo", "Map + network", "graph/map.html"), ("graph", "Industry graph", "graph/index.html"),
         ("shows", "Trade shows in 3D", "graph/events.html"), ("sky", "3D skyline", "skyline.html")]
# Fonts and three.js are self-hosted (copied from scripts/assets/ into the site) so the site keeps
# its rule of no third-party requests outside the street map (test_external_requests_only_on_map_page).
FONT_FILES = ["lato-400-latin", "lato-700-latin"]
THREE_JS = "vendor/three.min.js"
SITE_URL = "https://polymerindustrycluster.github.io/polymer-atlas/"   # absolute base for social-preview images and the 404 page
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0b1120"/>'
           '<rect x="12" y="34" width="9" height="18" rx="2" fill="#40a6d6"/><rect x="27.5" y="14" width="9" height="38" rx="2" fill="#ffd27f"/>'
           '<rect x="43" y="26" width="9" height="26" rx="2" fill="#7fb0ff"/></svg>')   # three.js r128 (MIT), scripts/assets/three/


class Ctx:
    def __init__(self, atlas, qcew, git, repo_url, built_on, db_date):
        self.atlas, self.qcew, self.git, self.repo_url = atlas, qcew, git, repo_url
        self.built_on, self.db_date = built_on, db_date

    def asof(self):
        g = self.git
        dirty = " plus uncommitted local data changes" if g["dirty"] else ""
        built = f"database built {esc(self.db_date)}; " if self.db_date else ""
        return (f"Repository commit {esc(g['sha'])} ({esc(g['date'])}){dirty}; "
                f"{built}site generated {esc(self.built_on)}.")


def page(ctx, title, body, root="", active="", description="", head_extra="", scripts="", main_class="wrap", main_attrs=""):
    """The one shell every built page goes through, the graph pages included (build_graph.py and friends import this).
    root: path from the page to the site root; main_class "viz" makes <main> a full-width stage for the explorers."""
    nav = "".join(
        '<li><a href="%s%s"%s>%s</a></li>' % (root, href, ' aria-current="page"' if key == active else "", esc(label))
        for key, label, href in NAV)
    views = ""
    if active in {k for k, _, _ in VIEWS}:
        views = ('<nav class="views" aria-label="Views"><div class="wrap"><ul>' + "".join(
            '<li><a href="%s%s"%s>%s</a></li>' % (root, href, ' aria-current="page"' if key == active else "", esc(label))
            for key, label, href in VIEWS) + "</ul></div></nav>")
    desc = esc(description or "Open, source-backed database of the US polymer, plastics and rubber industry.")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="description" content="{desc}">
<title>{esc(title) + " | Polymer Industry Atlas" if title != "Home" else "Polymer Industry Atlas"}</title>
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<meta property="og:site_name" content="Polymer Industry Atlas">
<meta property="og:title" content="{esc(title if title != "Home" else "Polymer Industry Atlas")}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE_URL}og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{root}style.css">
<noscript><style>.menu-btn{{display:none}}.site-header nav{{display:block}}</style></noscript>
{head_extra}
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header class="site-header">
<div class="wrap">
<a class="brand" href="{root}index.html"><img src="{root}brand/pic-mark-white.svg" alt="" width="30" height="30">Polymer Industry Atlas</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
<nav id="site-nav" aria-label="Main"><ul>{nav}</ul></nav>
</div>
</header>
{views}
<main id="main" class="{main_class}" tabindex="-1"{main_attrs}>
{body}
</main>
<footer class="site-footer">
<div class="wrap">
<div class="footer-brand"><img src="{root}brand/pic-logo-white-no-tagline.svg" alt="Polymer Industry Cluster" width="105" height="56">
<span>The Atlas is an open-data project of the Polymer Industry Cluster,<br>powered by the Greater Akron Chamber.</span></div>
<p>Polymer Industry Atlas, built for the Polymer Industry Cluster (PIC), Greater Akron Chamber.
Data license: <a href="https://creativecommons.org/licenses/by/4.0/" rel="noopener">CC BY 4.0</a>.
Source and data: <a href="{esc(ctx.repo_url)}" rel="noopener">{esc(ctx.repo_url)}</a>.</p>
<p class="downloads"><strong>Take the data with you:</strong>
<a href="{root}directory.csv">Northeast Ohio polymer companies (CSV, all rows)</a> ·
<a href="{esc(ctx.repo_url)}/releases/latest" rel="noopener">Latest data release (GitHub)</a></p>
<p class="muted">{ctx.asof()}</p>
<p class="muted">Coordinates are reference data, never evidence. A missing figure is not a zero.
Counts here are database rows, not industry totals.</p>
</div>
</footer>
<script src="{root}shell.js" defer></script>
<script src="{root}sortable.js" defer></script>
{scripts}
</body>
</html>
"""


EXPLORER_JS = r"""(function () {
  'use strict';
  // The graph, map + network and trade-show pages: on a screen 720 px or wider, load the page's libraries (data-libs, in order) and
  // then its script (data-boot); below that the page shows its plain summary and loads none of them.
  var main = document.getElementById('main');
  if (!main || !main.hasAttribute('data-boot') || matchMedia('(max-width: 719.98px)').matches) return;
  var urls = (main.getAttribute('data-libs') || '').split(' ').filter(Boolean).concat(main.getAttribute('data-boot'));
  urls.forEach(function (u) {
    var s = document.createElement('script'); s.src = u; s.async = false;   // async = false: run in the order listed
    s.onerror = function () { var st = document.getElementById('stage'); if (st) st.textContent = 'Could not load ' + u + '.'; };
    document.head.appendChild(s);
  });
})();
"""


SHELL_JS = r"""(function () {
  'use strict';
  // Phone menu: the Menu button shows and hides the main nav; Escape closes it and returns focus to the button.
  var btn = document.querySelector('.menu-btn'), nav = document.getElementById('site-nav');
  if (!btn || !nav) return;
  function set(open) { btn.setAttribute('aria-expanded', open ? 'true' : 'false'); }
  btn.addEventListener('click', function () { set(btn.getAttribute('aria-expanded') !== 'true'); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && btn.getAttribute('aria-expanded') === 'true') { set(false); btn.focus(); }
  });
  nav.addEventListener('click', function (e) { if (e.target.closest('a')) set(false); });
})();
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

EXPERTS_JS = r"""(function () {
  'use strict';
  // Two views. "Browse": institutions grouped by state with researcher/program counts (the default with no
  // search). "Results": compact one-line rows grouped by institution, shown once a search, filter or
  // institution is chosen. URL keeps ?q=, ?state=, ?inst= so every view is linkable.
  var $ = function (id) { return document.getElementById(id); };
  var D = null, PAGE = 60, limit = PAGE;
  var params = new URLSearchParams(location.search);
  var inst = params.get('inst') || '';
  $('q').value = params.get('q') || '';
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function chip(t) { return '<button type="button" class="xchip" data-q="' + esc(t) + '">' + esc(t) + '</button>'; }
  function instName(id) { return (D.insts[id] || [id])[0]; }
  function place(id) { var i = D.insts[id] || []; return [i[1], i[2]].filter(Boolean).join(', '); }
  fetch('experts.json').then(function (r) { return r.json(); }).then(function (d) {
    D = d;
    D.pc = {}; D.gc = {};
    D.people.forEach(function (p) { D.pc[p[3]] = (D.pc[p[3]] || 0) + 1; });
    D.programs.forEach(function (g) { D.gc[g[1]] = (D.gc[g[1]] || 0) + 1; });
    var states = {}; Object.keys(D.insts).forEach(function (k) { if (D.insts[k][2]) states[D.insts[k][2]] = 1; });
    Object.keys(states).sort().forEach(function (s) { var o = document.createElement('option'); o.value = s; o.textContent = s; $('state').appendChild(o); });
    $('state').value = params.get('state') || '';
    var freq = {}, generic = { polymers: 1, polymer: 1, plastics: 1 };
    D.people.forEach(function (p) { p[2].forEach(function (s) { if (!generic[s.toLowerCase()]) freq[s] = (freq[s] || 0) + 1; }); });
    $('chips').innerHTML = '<span class="muted small">Common specialties:</span> ' + Object.keys(freq).sort(function (a, b) { return freq[b] - freq[a]; }).slice(0, 14).map(chip).join('');
    D.peopleHay = D.people.map(function (p) { var i = D.insts[p[3]] || []; return [p[0], p[1], p[2].join(' '), i[0], i[1], i[2]].join(' | ').toLowerCase(); });
    D.progHay = D.programs.map(function (g) { var i = D.insts[g[1]] || []; return [g[0], g[2], g[3], g[4], g[5].join(' '), i[0], i[1], i[2]].join(' | ').toLowerCase(); });
    run();
  }).catch(function (e) { $('count').textContent = 'Could not load the finder data (' + e.message + ').'; });

  function matches(hay, words) { for (var k = 0; k < words.length; k++) if (hay.indexOf(words[k]) === -1) return false; return true; }
  function setView(v) {
    $('browse').hidden = v !== 'browse'; $('ppl').hidden = $('prg').hidden = v === 'browse';
    Array.prototype.forEach.call($('tabs').querySelectorAll('button'), function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-view') === v)); });
  }
  function group(rows, instIdx, render, az) {
    var by = {}, order = [];
    rows.forEach(function (r) { var k = r[instIdx]; if (!by[k]) { by[k] = []; order.push(k); } by[k].push(r); });
    order.sort(function (a, b) { return az ? instName(a).localeCompare(instName(b)) : (by[b].length - by[a].length || instName(a).localeCompare(instName(b))); });
    return order.map(function (k) {
      return '<div class="xgroup"><h3><a href="orgs/' + encodeURIComponent(k) + '.html">' + esc(instName(k)) + '</a> <span class="muted">' + esc(place(k)) + ' · ' + by[k].length + '</span></h3><ul class="xrows">' + by[k].map(render).join('') + '</ul></div>';
    }).join('');
  }
  function specs(list) { return list.length ? '<span class="xs">' + list.slice(0, 4).map(chip).join('') + (list.length > 4 ? '<span class="muted small">+' + (list.length - 4) + '</span>' : '') + '</span>' : ''; }
  var WORDS = [], FLAT = false;
  // "Why this matched": which fields hold at least one search word (OIEx-style), shown only during a search.
  function why(fields) {
    if (!WORDS.length) return '';
    var hit = fields.filter(function (f) { var v = String(f[1] || '').toLowerCase(); return WORDS.some(function (w) { return v.indexOf(w) !== -1; }); }).map(function (f) { return f[0]; });
    return hit.length ? '<span class="xwhy">Matched in ' + hit.join(', ') + '</span>' : '';
  }
  function instLine(id) { return FLAT ? '<span class="xr">' + esc(instName(id)) + (place(id) ? ', ' + esc(place(id)) : '') + '</span>' : ''; }
  function personRow(p) {
    var name = p[4] ? '<a href="' + esc(p[4]) + '" rel="noopener nofollow">' + esc(p[0]) + '</a>' : esc(p[0]);
    var i = D.insts[p[3]] || [];
    var open = p[5] && p[5].length ? '<span class="xopen">Open to: ' + esc(p[5].join(', ')) + '</span>' : '';
    return '<li><span class="xn">' + name + instLine(p[3]) + '</span><span class="xr">' + esc(p[1]) + open + '</span><span class="xsw">' + specs(p[2]) +
      why([['name', p[0]], ['title', p[1]], ['specialties', p[2].join(' ')], ['institution', i[0]], ['location', [i[1], i[2]].join(' ')]]) + '</span></li>';
  }
  function programRow(g) {
    var name = g[6] ? '<a href="' + esc(g[6]) + '" rel="noopener nofollow">' + esc(g[0]) + '</a>' : esc(g[0]);
    var i = D.insts[g[1]] || [];
    return '<li><span class="xn">' + name + instLine(g[1]) + '</span><span class="xr">' + esc([g[2], g[3], g[4]].filter(Boolean).join(' · ')) + '</span><span class="xsw">' + specs(g[5]) +
      why([['program name', g[0]], ['type and level', [g[2], g[3], g[4]].join(' ')], ['specialties', g[5].join(' ')], ['institution', i[0]], ['location', [i[1], i[2]].join(' ')]]) + '</span></li>';
  }
  function lastName(n) { var w = String(n).replace(/\(.*?\)/g, '').trim().split(/\s+/); return (w[w.length - 1] || '').toLowerCase(); }
  function flat(rows, render, key) {
    return '<div class="xgroup"><ul class="xrows">' + rows.slice().sort(function (a, b) { return key(a).localeCompare(key(b)); }).map(render).join('') + '</ul></div>';
  }
  // Facet counts: each State / Institution type option shows how many results it would give with the other filters as they are.
  function facetCounts(words, show) {
    var by = { state: {}, kind: {} }, st = $('state').value, kind = $('kind').value;
    function tally(instId, hay) {
      if (inst && instId !== inst) return; if (!matches(hay, words)) return;
      var i = D.insts[instId] || ['', '', '', ''];
      if (!kind || i[3] === kind) by.state[i[2]] = (by.state[i[2]] || 0) + 1;
      if (!st || i[2] === st) by.kind[i[3]] = (by.kind[i[3]] || 0) + 1;
    }
    if (show !== 'programs') D.people.forEach(function (p, k) { tally(p[3], D.peopleHay[k]); });
    if (show !== 'people') D.programs.forEach(function (g, k) { tally(g[1], D.progHay[k]); });
    Array.prototype.forEach.call($('state').options, function (o) {
      if (!o.dataset.base) o.dataset.base = o.textContent;
      if (o.value) { var n = by.state[o.value] || 0; o.textContent = o.dataset.base + ' (' + n.toLocaleString() + ')'; o.disabled = !n && o.value !== st; }
    });
    Array.prototype.forEach.call($('kind').options, function (o) {
      if (!o.dataset.base) o.dataset.base = o.textContent;
      if (o.value) o.textContent = o.dataset.base + ' (' + (by.kind[o.value] || 0).toLocaleString() + ')';
    });
  }
  function browse(st, kind) {
    // One compact table: a state header row, then one line per institution (name, city, researchers, programs).
    var by = {};
    Object.keys(D.insts).forEach(function (k) {
      var i = D.insts[k]; if (!(D.pc[k] || D.gc[k])) return;
      if ((st && i[2] !== st) || (kind && i[3] !== kind)) return;
      (by[i[2] || 'Other'] = by[i[2] || 'Other'] || []).push(k);
    });
    var sts = Object.keys(by).sort(function (a, b) { return (a === 'OH' ? -1 : b === 'OH' ? 1 : a.localeCompare(b)); });
    var tot = function (k) { return (D.pc[k] || 0) + (D.gc[k] || 0); };
    $('insts').innerHTML = '<div class="table-wrap"><table class="xtable"><thead><tr><th scope="col">Institution</th><th scope="col">City</th>' +
      '<th scope="col" class="num">Researchers</th><th scope="col" class="num">Programs</th></tr></thead>' +
      sts.map(function (s) {
        var ks = by[s].sort(function (a, b) { return tot(b) - tot(a) || instName(a).localeCompare(instName(b)); });
        return '<tbody><tr class="xst"><th colspan="4" scope="colgroup">' + esc(s) + ' <span class="muted">' + ks.length + ' institution' + (ks.length === 1 ? '' : 's') + '</span></th></tr>' +
          ks.map(function (k) {
            return '<tr><th scope="row"><button type="button" class="xinst" data-inst="' + esc(k) + '">' + esc(instName(k)) + '</button></th>' +
              '<td data-label="City">' + esc(D.insts[k][1] || '') + '</td><td class="num" data-label="Researchers">' + (D.pc[k] || '') +
              '</td><td class="num" data-label="Programs">' + (D.gc[k] || '') + '</td></tr>';
          }).join('') + '</tbody>';
      }).join('') + '</table></div>';
    return sts.reduce(function (n, s) { return n + by[s].length; }, 0);
  }
  function run() {
    if (!D) return;
    var q = $('q').value.trim().toLowerCase(), st = $('state').value, kind = $('kind').value, show = $('show').value;
    var words = q.split(/\s+/).filter(Boolean), filtered = !!(q || inst);
    WORDS = words; FLAT = $('sort').value === 'name';
    facetCounts(words, show);
    var instOk = function (id) { var i = D.insts[id] || ['', '', '', '']; return (!inst || id === inst) && (!st || i[2] === st) && (!kind || i[3] === kind); };
    var ppl = [], prg = [];
    if (show !== 'programs') D.people.forEach(function (p, k) { if (instOk(p[3]) && matches(D.peopleHay[k], words)) ppl.push(p); });
    if (show !== 'people') D.programs.forEach(function (g, k) { if (instOk(g[1]) && matches(D.progHay[k], words)) prg.push(g); });
    var n = function (k, one, many) { return k.toLocaleString() + ' ' + (k === 1 ? one : many); };
    var view = $('tabs').getAttribute('data-forced') || (filtered ? 'results' : 'browse');
    var nInst = browse(st, kind);
    $('count').innerHTML = esc((show === 'programs' ? '' : n(ppl.length, 'researcher record', 'researcher records')) +
      (show === 'both' ? ' and ' : '') + (show === 'people' ? '' : n(prg.length, 'program record', 'program records')) +
      (show !== 'both' && ppl.length + prg.length === 1 ? ' matches' : ' match') +
      (view === 'browse' ? ', at ' + nInst.toLocaleString() + ' institutions' : '') + '.') +
      (inst ? ' <span class="xfilter">Institution: <b>' + esc(instName(inst)) + '</b> <button type="button" class="xchip" id="noinst">remove</button></span>' : '');
    if ($('noinst')) $('noinst').onclick = function () { inst = ''; limit = PAGE; run(); };
    setView(view);
    $('empty').hidden = ppl.length + prg.length > 0;
    var pp = ppl.slice(0, limit), gg = prg.slice(0, limit);
    var instaz = $('sort').value === 'instaz';
    var grp = function (rows, idx, render, key) { return FLAT ? flat(rows, render, key) : group(rows, idx, render, instaz); };
    $('people').innerHTML = grp(pp, 3, personRow, function (p) { return lastName(p[0]); }) + (ppl.length > limit ? '<button type="button" class="xmore" data-more="1">Show more researchers (' + (ppl.length - limit).toLocaleString() + ' left)</button>' : '');
    $('programs').innerHTML = grp(gg, 1, programRow, function (g) { return String(g[0]).toLowerCase(); }) + (prg.length > limit ? '<button type="button" class="xmore" data-more="1">Show more programs (' + (prg.length - limit).toLocaleString() + ' left)</button>' : '');
    if (view === 'results') { $('ppl').hidden = show === 'programs' || !ppl.length; $('prg').hidden = show === 'people' || !prg.length; }
    var u = new URLSearchParams(); if (q) u.set('q', $('q').value.trim()); if (st) u.set('state', st); if (inst) u.set('inst', inst);
    try { history.replaceState(null, '', u.toString() ? '?' + u.toString() : location.pathname); } catch (e) {}
  }
  var t = null;
  $('q').addEventListener('input', function () { clearTimeout(t); limit = PAGE; $('tabs').removeAttribute('data-forced'); t = setTimeout(run, 120); });
  ['state', 'kind', 'show', 'sort'].forEach(function (id) { $(id).addEventListener('change', function () { limit = PAGE; if (id === 'sort') $('tabs').setAttribute('data-forced', 'results'); run(); }); });
  $('clear').addEventListener('click', function () {
    $('q').value = ''; $('state').value = ''; $('kind').value = ''; $('show').value = 'both'; inst = ''; limit = PAGE; $('tabs').removeAttribute('data-forced'); run(); $('q').focus();
  });
  $('tabs').addEventListener('click', function (e) {
    var b = e.target.closest('button[data-view]'); if (!b) return; $('tabs').setAttribute('data-forced', b.getAttribute('data-view')); run();
  });
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.xchip[data-q]');
    if (b) { $('q').value = b.getAttribute('data-q'); limit = PAGE; $('tabs').removeAttribute('data-forced'); run(); $('q').focus(); window.scrollTo({ top: 0, behavior: 'smooth' }); return; }
    var i = e.target.closest && e.target.closest('.xinst[data-inst]');
    if (i) { inst = i.getAttribute('data-inst'); limit = PAGE; $('tabs').removeAttribute('data-forced'); run(); window.scrollTo({ top: 0, behavior: 'smooth' }); return; }
    var m = e.target.closest && e.target.closest('.xmore');
    if (m) { limit += PAGE * 2; run(); }
  });
})();
"""


SORTABLE_JS = r"""(function () {
  'use strict';
  // Progressive enhancement: click a column header to sort; long tables get a filter box.
  // data-nosort: no sort buttons. data-nocsv: no download. data-nofilter: no filter box. Rows with class "total" stay at the bottom.
  function key(cell) {
    if (!cell) return { n: null, t: '' };
    var raw = (cell.getAttribute('data-sort') || cell.textContent || '').trim();
    var num = raw.replace(/[,$%\s]/g, '');
    if (/^-?\d+(\.\d+)?$/.test(num)) return { n: parseFloat(num), t: raw.toLowerCase() };
    return { n: null, t: raw.toLowerCase() };
  }
  // "Download these rows (CSV)": exactly the rows and columns on screen. Filtered-out rows and total rows are left out.
  function csvCell(c) {
    var s = (c.getAttribute('data-csv') !== null ? c.getAttribute('data-csv') : c.textContent).replace(/\s+/g, ' ').trim();
    if (/^[=+@]/.test(s) || /^-(?!\d)/.test(s)) s = "'" + s;   // spreadsheets would run a leading = + @ - as a formula
    return /[",]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : many); }
  function csvButton(table) {
    var cap = table.caption ? table.caption.textContent : document.title;
    var b = document.createElement('button'); b.type = 'button'; b.textContent = 'Download these rows (CSV)';
    b.addEventListener('click', function () {
      var head = table.tHead.rows[table.tHead.rows.length - 1];
      var lines = [Array.prototype.map.call(head.cells, csvCell).join(',')];
      Array.prototype.forEach.call(table.tBodies[0].rows, function (r) {
        if (r.hidden || r.classList.contains('total')) return;
        lines.push(Array.prototype.map.call(r.cells, csvCell).join(','));
      });
      var name = cap.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60) + '-' + new Date().toISOString().slice(0, 10) + '.csv';
      var a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob(['\ufeff' + lines.join('\r\n') + '\r\n'], { type: 'text/csv;charset=utf-8' }));
      a.download = name; document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    });
    return b;
  }
  // The one toolbar above a table: row count, optional filter box, Download these rows (CSV), Copy link.
  function toolbar(table, rows, filterable, withCsv, idx) {
    var body = table.tBodies[0], wrap = table.closest('.table-wrap') || table;
    var data = rows.filter(function (r) { return !r.classList.contains('total'); });
    var bar = document.createElement('div'); bar.className = 'tbar';
    var count = document.createElement('span'); count.className = 'tcount'; count.setAttribute('aria-live', 'polite');
    function show(n) { count.textContent = n === data.length ? plural(n, 'row', 'rows') : n + ' of ' + plural(data.length, 'row', 'rows'); }
    show(data.length); bar.appendChild(count);
    if (filterable) {
      var box = document.createElement('label'); box.className = 'tfilter';
      var inp = document.createElement('input'); inp.type = 'search'; inp.id = 'tfilter-' + idx; inp.placeholder = 'Filter these rows';
      box.appendChild(document.createTextNode('Filter')); box.appendChild(inp); bar.appendChild(box);
      inp.addEventListener('input', function () {
        var q = inp.value.trim().toLowerCase(), shown = 0;
        Array.prototype.forEach.call(body.rows, function (r) {
          var hit = !q || r.classList.contains('total') || r.textContent.toLowerCase().indexOf(q) !== -1;
          r.hidden = !hit; if (hit && !r.classList.contains('total')) shown++;
        });
        show(shown);
      });
    }
    if (withCsv) bar.appendChild(csvButton(table));
    var msg = document.createElement('span'); msg.className = 'tmsg'; msg.setAttribute('role', 'status');
    var copy = document.createElement('button'); copy.type = 'button'; copy.textContent = 'Copy link';
    copy.addEventListener('click', function () {
      var done = function (t) { msg.textContent = t; setTimeout(function () { msg.textContent = ''; }, 2500); };
      if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(function () { done('Link copied'); }, function () { done('Copy failed: copy the address bar'); });
      else done('Copy the address bar');
    });
    bar.appendChild(copy); bar.appendChild(msg);
    wrap.parentNode.insertBefore(bar, wrap);
  }
  function enhance(table, idx) {
    var head = table.tHead, body = table.tBodies[0];
    if (!head || !body) return;
    var rows = Array.prototype.slice.call(body.rows);
    if (rows.length < 2) return;
    var ths = head.rows[head.rows.length - 1].cells;
    if (!table.hasAttribute('data-nosort')) Array.prototype.forEach.call(ths, function (th, col) {   // data-nosort: no sort buttons; the toolbar stays
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'sort';
      while (th.firstChild) b.appendChild(th.firstChild);
      th.appendChild(b); th.setAttribute('aria-sort', 'none');
      b.addEventListener('click', function () {
        var dir = th.getAttribute('aria-sort') === 'ascending' ? 'descending' : 'ascending';
        Array.prototype.forEach.call(ths, function (o) { o.setAttribute('aria-sort', 'none'); });
        th.setAttribute('aria-sort', dir);
        var sign = dir === 'ascending' ? 1 : -1;
        var all = Array.prototype.slice.call(body.rows);
        var pinned = all.filter(function (r) { return r.classList.contains('total'); });
        var sortable = all.filter(function (r) { return !r.classList.contains('total'); });
        sortable.map(function (r, i) { return { r: r, k: key(r.cells[col]), i: i }; }).sort(function (a, b) {
          var ea = a.k.t === '' || a.k.t === '\u2014', eb = b.k.t === '' || b.k.t === '\u2014';
          if (ea !== eb) return ea ? 1 : -1;                       // blanks always last
          var c = (a.k.n !== null && b.k.n !== null) ? a.k.n - b.k.n : a.k.t.localeCompare(b.k.t, undefined, { numeric: true });
          return c * sign || a.i - b.i;
        }).forEach(function (o) { body.appendChild(o.r); });
        pinned.forEach(function (r) { body.appendChild(r); });
      });
    });
    var filterable = rows.length > 12 && !table.hasAttribute('data-nofilter');   // data-nofilter: the page filters its own rows
    var withCsv = !table.hasAttribute('data-nocsv');
    if (filterable || withCsv) toolbar(table, rows, filterable, withCsv, idx);
  }
  // Phone layout: every cell carries its column heading, so CSS can stack a row as a labelled card.
  function label(table) {
    var head = table.tHead; if (!head) return;
    var names = Array.prototype.map.call(head.rows[head.rows.length - 1].cells, function (c) { return c.textContent.trim(); });
    if (names.length < 3) return;
    table.classList.add('stack');
    Array.prototype.forEach.call(table.tBodies, function (b) {
      Array.prototype.forEach.call(b.rows, function (r) {
        Array.prototype.forEach.call(r.cells, function (c, i) { if (names[i]) c.setAttribute('data-label', names[i]); });
      });
    });
  }
  // A link to #SITE-... opens that collapsed site row.
  function openTarget() {
    var id = decodeURIComponent(location.hash.slice(1)); if (!id) return;
    var el = document.getElementById(id); if (el && el.tagName === 'DETAILS') { el.open = true; el.scrollIntoView(); }
  }
  function init() {
    Array.prototype.forEach.call(document.querySelectorAll('.table-wrap table'), function (t, i) { label(t); enhance(t, i); });
    openTarget(); addEventListener('hashchange', openTarget);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
"""


CSS = """
/* Polymer Industry Atlas — styled to the PIC Design System (product/public tier).
   Values come from the PIC token file (colors_and_type.css, generated from pic-tokens.source.json)
   and the PIC Evidence Room: Lato; paper + charcoal ink; action teal #15727f (the AA-safe split of
   brand blue) with the brand's teal-to-purple hover; deep teal (#073F49 / #052E36) for dark surfaces;
   lime #B8D637 only as an accent on dark; data colours from the engineered data-* palette (ADR-012),
   never as text (they are 3:1 non-text colours). PIC has no dark theme: the dark scheme below is
   derived from its deep-teal family. */
@font-face{font-family:"Lato";font-weight:400;font-style:normal;font-display:swap;src:url(fonts/lato-400-latin.woff2) format("woff2")}
@font-face{font-family:"Lato";font-weight:700;font-style:normal;font-display:swap;src:url(fonts/lato-700-latin.woff2) format("woff2")}
:root{
  --bg:#faf9f7;--panel:#ffffff;--panel-2:#f1f2f0;--fg:#2b2c2a;--muted:#656661;--line:#ddd9d2;
  --accent:#15727f;--accent-hover:#995480;--accent-fg:#ffffff;
  --deep:#073f49;--deeper:#052e36;--blue-dark:#0c6473;--on-deep:#f3f7f6;--on-deep-muted:#a9c6c8;--lime:#b8d637;--light-blue:#66d7de;
  --f-display:"Lato",-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;--f-body:var(--f-display);
  --f-mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
  --warn-bg:#fff2db;--warn-fg:#935406;--ok-bg:#e2f3ec;--ok-fg:#166a45;--danger:hsl(350 72% 43%);
  --r1:#4099ac;--r2:#bb780e;--r3:#985a80;--r4:#d5613b;--r5:#809800;--rx:#8d908b;
  --shadow-sm:0 1px 2px rgba(27,29,27,.06),0 1px 1px rgba(27,29,27,.04);--shadow-md:0 4px 12px rgba(27,29,27,.08),0 2px 4px rgba(27,29,27,.04);
  --shadow-lg:0 12px 28px rgba(27,29,27,.10),0 4px 8px rgba(27,29,27,.05);
  /* type scale (Lato 400/700) and spacing, used by the shell and the explorers */
  --t-xs:.78rem;--t-sm:.9rem;--t-md:1rem;--t-lg:1.15rem;--t-xl:1.5rem;--t-2xl:2.25rem;
  --s-1:4px;--s-2:8px;--s-3:12px;--s-4:16px;--s-5:24px;--s-6:32px;
  /* data-visualisation colours of the explorer pages (graph, map + network, trade shows) */
  --edge:#e4e1db;--edge-hi:#15727f;--dim:#e7e5e0;--label:#2b2c2a;--event:#585955;--free:#b9bbb6;
  --proc:#073f49;--mat:#3a5a8c;--mkt:#5c2f4f;
  --land:#ece9e3;--border:#d2cdc4;--p12:#eef4d6;--p12-line:#6f8200;--arc:rgba(7,63,73,.16);--arc-hi:rgba(21,114,127,.9);
}
@media (prefers-color-scheme: dark){
  :root{--bg:#052e36;--panel:#073f49;--panel-2:#0a4a55;--fg:#eef3f2;--muted:#a9c2c3;--line:#1d5662;
  --accent:#66d7de;--accent-hover:#dba8c9;--accent-fg:#052e36;
  --warn-bg:#3d2a06;--warn-fg:#ffcf85;--ok-bg:#123f30;--ok-fg:#9fe0bf;--danger:hsl(350 80% 72%);
  --r1:#66c0d2;--r2:#e0a040;--r3:#c98ab2;--r4:#f08a64;--r5:#b8d637;--rx:#b0b3ae;
  --shadow-sm:none;--shadow-md:0 4px 12px rgba(0,0,0,.25);--shadow-lg:0 12px 28px rgba(0,0,0,.35);color-scheme:dark;
  --edge:#0c3f48;--edge-hi:#66d7de;--dim:#0e4650;--label:#eef3f2;--event:#c8d2d0;--free:#3c6b73;
  --proc:#eef3f2;--mat:#9db8e8;--mkt:#f2b6d6;
  --land:#0a3f48;--border:#1d5662;--p12:#1f4a33;--p12-line:#b8d637;--arc:rgba(102,215,222,.14);--arc-hi:rgba(102,215,222,.9)}
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 var(--f-body);overflow-x:clip}
.wrap{max-width:1200px;margin:0 auto;padding:0 16px}
a{color:var(--accent);text-underline-offset:2px;transition:color .15s}
a:hover{color:var(--accent-hover);text-decoration-thickness:2px}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,[tabindex]:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.skip{position:absolute;left:-999px;top:0;background:var(--accent);color:var(--accent-fg);padding:8px 12px;z-index:1000}
.skip:focus{left:8px;top:8px}
.site-header{position:relative;z-index:5;background:var(--deep);color:var(--on-deep)}
.site-header a{color:var(--on-deep)}
.site-header .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 24px;padding-top:10px;padding-bottom:10px}
.brand{display:inline-flex;align-items:center;gap:10px;font:700 1.15rem/1 var(--f-display);text-decoration:none;color:var(--on-deep)}
.brand img{width:30px;height:30px;display:block}
.brand:hover{color:var(--on-deep)}
main:focus{outline:none}
.site-header nav ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:4px 18px}

.site-header nav a{text-decoration:none;padding:6px 0;border-bottom:2px solid transparent;font:700 .76rem/1 var(--f-display);letter-spacing:.1em;text-transform:uppercase}
.site-header nav a:hover{color:#fff;border-bottom-color:var(--light-blue)}
.site-header nav a[aria-current=page]{border-bottom-color:var(--lime)}
main{padding-top:24px;padding-bottom:48px}
h1{font:700 2.25rem/1.15 var(--f-display);margin:.2em 0 .4em;text-wrap:balance}
h2{font:700 1.5rem/1.2 var(--f-display);margin:1.8em 0 .5em;border-bottom:1px solid var(--line);padding-bottom:.3em;text-wrap:balance}
h3{font:700 1.15rem/1.25 var(--f-display);margin:1.4em 0 .4em}
.lede{font-size:1.1rem;color:var(--muted);max-width:60em}
.muted{color:var(--muted)}
.small{font-size:.9rem}
.site-footer{background:var(--deep);color:var(--on-deep-muted);padding:28px 0 32px;font-size:.9rem}
.site-footer a{color:var(--light-blue)}
.site-footer a:hover{color:#fff}
.site-footer p{margin:.35em 0}
.site-footer .muted{color:var(--on-deep-muted)}
.footer-brand{display:flex;align-items:center;gap:18px;flex-wrap:wrap;margin-bottom:12px;color:var(--on-deep)}
.footer-brand img{height:56px;width:auto;display:block}
.table-wrap{overflow-x:auto;margin:.6em 0 1.2em;border:1px solid var(--line);border-radius:8px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:.95rem}
caption{text-align:left;padding:10px 12px;font-weight:700;color:var(--muted)}
th,td{padding:7px 12px;border-top:1px solid var(--line);text-align:left;vertical-align:top}
thead th{background:var(--panel-2);border-top:0;font-size:.74rem;line-height:1.3;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);vertical-align:bottom}
thead th.num{max-width:10em}
select{max-width:100%}
@media (max-width:640px){
  .table-wrap:has(table.stack){overflow-x:visible}
  table.stack thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
  table.stack caption{display:block}
  table.stack,table.stack tbody,table.stack tr{display:block;width:100%}
  table.stack tr{border-top:1px solid var(--line);padding:8px 0;display:grid;grid-template-columns:1fr 1fr}
  table.stack tbody th,table.stack td:not(.num){grid-column:1/-1}
  table.stack td.num{flex-direction:column;align-items:flex-start;gap:0;text-align:left;padding:4px 14px}
  table.stack td.num::before{font-size:.68rem;line-height:1.25}
  table.stack th,table.stack td{display:flex;justify-content:space-between;align-items:baseline;gap:14px;border:0;padding:3px 14px;text-align:right;white-space:normal}
  table.stack tbody th{font-size:1rem;text-align:left;padding-top:4px;justify-content:flex-start;flex-wrap:wrap}
  table.stack tbody th[data-label]::before{display:none}
  table.stack td::before{content:attr(data-label);flex:0 1 auto;text-align:left;color:var(--muted);font-size:.74rem;letter-spacing:.04em;text-transform:uppercase;font-weight:400}
  table.stack td:empty{display:none}
  table.stack tr.total{background:var(--panel-2)}
}
tbody th{font-weight:700}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tr.total th,tr.total td{background:var(--panel-2)}
.badge{display:inline-flex;align-items:center;gap:5px;padding:0 8px;border-radius:999px;font-size:.8rem;line-height:1.6;border:1px solid var(--line);white-space:nowrap;background:var(--panel);color:var(--fg)}
.ring-1,.ring-2,.ring-3,.ring-4,.ring-5,.ring-x{color:var(--fg)}
.ring-1::before,.ring-2::before,.ring-3::before,.ring-4::before,.ring-5::before,.ring-x::before{content:"";width:8px;height:8px;border-radius:50%;flex:none}
.ring-1{border-color:var(--r1)}.ring-1::before{background:var(--r1)}.ring-2{border-color:var(--r2)}.ring-2::before{background:var(--r2)}
.ring-3{border-color:var(--r3)}.ring-3::before{background:var(--r3)}.ring-4{border-color:var(--r4)}.ring-4::before{background:var(--r4)}
.ring-5{border-color:var(--r5)}.ring-5::before{background:var(--r5)}.ring-x{border-color:var(--rx)}.ring-x::before{background:var(--rx)}
.status-ok{background:var(--ok-bg);color:var(--ok-fg);border-color:transparent}
.status-warn{background:var(--warn-bg);color:var(--warn-fg);border-color:transparent}
.tier-U{border-style:dashed}
.banner{border:1px solid var(--line);background:var(--panel-2);padding:12px 16px;margin:1em 0;border-radius:8px}
.banner.tombstone{border-color:var(--warn-fg);background:var(--warn-bg);color:var(--warn-fg)}
.banner.tombstone a{color:inherit;font-weight:700}
.banner.note{border-color:var(--accent)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin:1em 0}
.card{border:1px solid var(--line);border-radius:8px;padding:14px 16px;background:var(--panel);box-shadow:var(--shadow-sm)}
.card .big{font:700 2rem/1.1 var(--f-display);font-variant-numeric:tabular-nums;color:var(--accent)}
.card .unit{font-weight:700;margin-top:4px}
.card .filter{color:var(--muted);font-size:.9rem}
dl.fields{display:grid;grid-template-columns:minmax(9em,14em) 1fr;gap:6px 16px;margin:.6em 0}
dl.fields dt{font-weight:700;color:var(--muted)}
dl.fields dd{margin:0;overflow-wrap:anywhere}
@media (max-width:600px){dl.fields{grid-template-columns:1fr}dl.fields dt{margin-top:.5em}}
ul.sources{margin:.3em 0;padding-left:1.2em}
ul.sources li{overflow-wrap:anywhere;margin:.2em 0}
details.site{border:1px solid var(--line);border-radius:8px;margin:8px 0;background:var(--panel)}
details.site>summary{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr) auto;gap:4px 16px;align-items:center;padding:10px 16px;cursor:pointer;list-style:none}
details.site>summary::-webkit-details-marker{display:none}
details.site>summary::before{content:"";grid-row:1/3;display:none}
details.site>summary:hover .s-name{color:var(--accent-hover)}
details.site .s-name{font-weight:700;color:var(--accent)}
details.site .s-meta{color:var(--muted);font-size:.92rem}
details.site .s-badges{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
details.site[open]>summary{border-bottom:1px solid var(--line)}
details.site .s-body{padding:4px 16px 12px}
details.site:target{outline:3px solid var(--accent)}
details.srcs>summary{cursor:pointer;color:var(--muted);font-size:.92rem}
abbr[title]{text-decoration:none;cursor:help}
@media (max-width:720px){details.site>summary{grid-template-columns:1fr}details.site .s-badges{justify-content:flex-start}}
details{margin:.4em 0}
summary{cursor:pointer}
.filters{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:1em 0}
fieldset{border:1px solid var(--line);border-radius:8px;padding:8px 12px;margin:0;min-width:0;background:var(--panel)}
legend{font-weight:700;padding:0 4px}
fieldset label{display:block;padding:1px 0}
.scroll{max-height:12em;overflow-y:auto}
.swatch{display:inline-block;width:.9em;height:.9em;border-radius:50%;margin-right:6px;vertical-align:-1px;border:1px solid var(--fg)}
button,select,input[type=search]{font:inherit;color:var(--fg);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:7px 11px;min-height:40px}
button{cursor:pointer;background:var(--panel)}
button:hover{border-color:var(--accent)}
input[type=search]{width:100%;max-width:34em;font-size:16px}
#map{height:70vh;min-height:380px;border:1px solid var(--line);border-radius:8px}
.btn-row{display:flex;flex-wrap:wrap;gap:6px;margin:.4em 0}
ul.results{list-style:none;padding:0}
ul.results li{border-top:1px solid var(--line);padding:10px 0}
ul.results .meta{color:var(--muted);font-size:.9rem}
.leaflet-popup-content{color:#2b2c2a}
.leaflet-popup-content a{color:#15727f}
@media print{.site-header nav,.menu-btn,.views,.skip,.filters,#map{display:none}}

/* ---- home: industry skyline hero (deep-teal stage) + explorers ---- */
.hero{position:relative;margin:-24px calc(50% - 50vw) 0;background:radial-gradient(120% 90% at 65% 35%,#0c6473 0%,#073f49 42%,#052e36 75%);color:var(--on-deep);overflow:hidden}
.hero-stage{position:relative;height:min(78vh,720px);min-height:460px}
#skyline{position:absolute;inset:0}
.hero-stage::before{content:"";position:absolute;inset:0;z-index:1;pointer-events:none;background:linear-gradient(90deg,rgba(5,46,54,.94) 0%,rgba(5,46,54,.78) 30%,rgba(5,46,54,0) 52%)}
@media (max-width:720px){.hero-stage::before{background:linear-gradient(180deg,rgba(5,46,54,.94) 0%,rgba(5,46,54,.82) 55%,rgba(5,46,54,0) 80%)}}
#skyline canvas{display:block;width:100%;height:100%;cursor:grab;touch-action:pan-y}
#skyline canvas:active{cursor:grabbing}
.hero-copy{position:absolute;left:max(16px,calc(50% - 584px));top:32px;max-width:min(480px,calc(100% - 32px));pointer-events:none;z-index:2}
.hero-copy *{pointer-events:auto}
.eyebrow{font:700 .75rem/1 var(--f-display);letter-spacing:.18em;text-transform:uppercase;color:var(--lime)}
.hero h1{font-size:clamp(2.3rem,5vw,3.9rem);line-height:1.05;margin:.25em 0 .35em;color:#fff}
.hero h1 em{font-style:normal;color:var(--lime)}
.hero p.lede{color:var(--on-deep-muted);font-size:1.05rem;margin:0 0 1rem}
.hero-stats{display:flex;gap:24px;flex-wrap:wrap;margin:0 0 1.2rem}
.hero-stats div{display:flex;flex-direction:column}
.hero-stats b{font:700 2.1rem/1 var(--f-display);color:#fff;font-variant-numeric:tabular-nums}
.hero-stats small{font:400 .8rem/1.35 var(--f-display);color:var(--on-deep-muted);max-width:15em;margin-top:4px}
.cta{display:flex;gap:8px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;min-height:44px;padding:0 18px;border-radius:8px;border:1px solid rgba(255,255,255,.35);background:transparent;color:#fff;
  font:700 .95rem/1 var(--f-display);text-decoration:none;cursor:pointer;transition:background .15s,border-color .15s,color .15s}
.btn:hover{border-color:#fff;color:#fff;background:rgba(255,255,255,.08)}
.btn.primary{background:#fff;color:var(--deep);border-color:#fff}
.btn.primary:hover{background:var(--light-blue);border-color:var(--light-blue);color:var(--deeper)}
.hero-tools{position:absolute;right:max(16px,calc(50% - 584px));bottom:18px;display:flex;gap:6px;z-index:2;align-items:center}
.hero-tools .btn{min-height:36px;padding:0 12px;font-size:.82rem}
.hero-tools .btn[aria-pressed=true]{border-color:#fff;background:rgba(255,255,255,.12)}
.hero-hint{font:400 .78rem/1.3 var(--f-display);color:var(--on-deep-muted);margin-right:6px}
.hero-legend{position:absolute;left:max(16px,calc(50% - 584px));bottom:18px;z-index:2;font:400 .78rem/1.3 var(--f-display);color:var(--on-deep-muted);display:flex;gap:10px;align-items:center}
.ramp{width:120px;height:8px;border-radius:4px;background:linear-gradient(90deg,#1f5a63,#2f7f8c,#4fb0bd,#b8d637,#eef6cf)}
#sky-tip{position:absolute;z-index:3;pointer-events:none;background:rgba(5,46,54,.96);border:1px solid #1d5662;border-radius:8px;padding:8px 11px;font-size:.88rem;display:flex;flex-direction:column;gap:2px;max-width:240px;color:var(--on-deep)}
#sky-tip b{font:700 1.2rem/1 var(--f-display);color:var(--lime)}
#sky-tip small{color:var(--on-deep-muted);font-size:.75rem}
.sky-fallback{display:flex;align-items:flex-end;justify-content:flex-end}
.sky-note{margin:0 16px 64px;color:var(--on-deep-muted);font-size:.9rem;max-width:30em;text-align:right}
.explore{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:28px 0 8px}
.xcard{display:flex;flex-direction:column;gap:8px;padding:20px;border-radius:8px;background:var(--panel);border:1px solid var(--line);text-decoration:none;color:var(--fg);box-shadow:var(--shadow-md);transition:box-shadow .15s,border-color .15s}
.xcard:hover{box-shadow:var(--shadow-lg);border-color:var(--accent-hover);color:var(--fg)}
.xcard svg{width:100%;height:84px;display:block}
.xcard h3{margin:0;font-size:1.25rem}
.xcard p{margin:0;color:var(--muted);font-size:.95rem}
.xcard .go{margin-top:auto;font:700 .9rem/1 var(--f-display);color:var(--accent)}
.xcard:hover .go{color:var(--accent-hover)}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
details.more{border:1px solid var(--line);border-radius:8px;background:var(--panel);padding:4px 18px;margin:10px 0}
details.more summary{cursor:pointer;font:700 1.1rem/1.2 var(--f-display);padding:12px 0}
details.more[open] summary{border-bottom:1px solid var(--line);margin-bottom:8px}
@media (max-width:720px){.hero-stage{height:780px}.hero-copy{top:40px}.hero-stats b{font-size:1.7rem}.hero-tools{left:16px;right:auto;bottom:14px}.hero-legend{display:none}}
@media (prefers-reduced-motion:reduce){.xcard,a,.btn{transition:none}}

/* ---- sortable tables (sortable.js; progressive enhancement) ---- */
th[aria-sort] button.sort{all:unset;cursor:pointer;display:inline;white-space:normal;font:inherit;color:inherit;letter-spacing:inherit;text-transform:inherit;text-align:inherit}
th[aria-sort] button.sort:hover{color:var(--accent-hover)}
th[aria-sort] button.sort:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
th[aria-sort] button.sort::after{content:"";display:inline-block;vertical-align:middle;margin:0 0 0 5px;width:0;height:0;border-left:4px solid transparent;border-right:4px solid transparent;border-top:5px solid currentColor;opacity:.3}
th[aria-sort=ascending] button.sort::after{border-top:0;border-bottom:5px solid currentColor;opacity:.9}
th[aria-sort=descending] button.sort::after{opacity:.9}

.tfilter{display:flex;gap:8px;align-items:center;margin:.8em 0 -.4em;font-size:.9rem;color:var(--muted)}
.tfilter input{padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--fg);font:inherit;min-width:0;width:16em;max-width:60%;min-height:40px}

.tdl{margin:-.6em 0 1.2em}
.downloads{margin:.4em 0}
.facets{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px;margin:.6em 0}
details.facet{border:1px solid var(--line);border-radius:8px;background:var(--panel);padding:6px 12px;margin:0}
details.facet summary{font-weight:700;min-height:32px;display:flex;align-items:center;gap:4px}
details.facet .sel{font-weight:400;color:var(--accent)}
details.facet .opts{max-height:15em;overflow-y:auto;padding:4px 0}
details.facet label.opt{display:flex;gap:6px;align-items:baseline;padding:2px 0}
details.facet label.opt .t{flex:1}
details.facet label.opt .n{color:var(--muted);font-variant-numeric:tabular-nums}
details.facet label.opt.zero{opacity:.55}
a.url{display:inline-block;max-width:15em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;vertical-align:bottom}
#ptable td{font-size:.9rem}
.explore-links{display:flex;gap:8px;flex-wrap:wrap;margin:.2em 0 1em}
.pill{display:inline-flex;align-items:center;gap:6px;min-height:36px;padding:0 14px;border-radius:999px;border:1px solid var(--accent);background:var(--panel);
  font:700 .88rem/1 var(--f-display);text-decoration:none;color:var(--accent);transition:color .15s,border-color .15s}
.pill:hover{border-color:var(--accent-hover);color:var(--accent-hover)}
.notfound{padding:48px 0 24px}.notfound .big404{font:700 6rem/1 var(--f-display);color:var(--accent);margin:0}
/* ---- programs & researchers finder ---- */
.eyebrow-ink{font:700 .75rem/1 var(--f-display);letter-spacing:.18em;text-transform:uppercase;color:var(--accent);margin:1.4em 0 0}
.xempty{border:1px dashed var(--line);border-radius:8px;padding:18px;margin:0 0 1.5em}
.xempty button{margin-left:.4em}
.xfinder .filters{grid-template-columns:repeat(auto-fill,minmax(180px,240px));gap:10px 20px;margin:.8em 0 .6em}
.xfinder .filters p{margin:0}
.xfinder .filters select{width:100%;margin-top:4px}
.xfinder .xq{margin-bottom:0}
.xfinder .xq input{display:block;margin-top:6px;max-width:42em;min-height:44px;font-size:17px}
.xchips{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:.4em 0 1em}
.xchip{min-height:32px;padding:0 11px;border-radius:999px;border:1px solid var(--line);background:var(--panel);color:var(--fg);font:400 .86rem/1 var(--f-body);cursor:pointer}
.xchip:hover{border-color:var(--accent-hover);color:var(--accent-hover)}
.xtabs{display:flex;gap:0;margin:.4em 0 1em;border:1px solid var(--line);border-radius:8px;width:max-content;max-width:100%;overflow:hidden}
.xtabs button{all:unset;cursor:pointer;padding:8px 16px;font:700 .88rem/1.2 var(--f-display);color:var(--muted)}
.xtabs button[aria-pressed=true]{background:var(--accent);color:#fff}
.xtabs button:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.xtable tr.xst th{background:var(--panel-2);font-size:.95rem;padding-top:10px}
.xtable tr.xst th .muted{font-weight:400;font-size:.85rem}
.xtable td,.xtable th{padding:5px 12px}
.xinst{all:unset;cursor:pointer;font-weight:700;color:var(--accent)}
.xinst:hover{color:var(--accent-hover);text-decoration:underline}
.xinst:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (max-width:640px){.xtable th:nth-child(2),.xtable td:nth-child(2){display:none}.xtable td,.xtable th{padding:6px 10px}}
.xgroup{margin:0 0 1em;border:1px solid var(--line);border-radius:8px;background:var(--panel)}
.xgroup h3{margin:0;padding:9px 14px;font-size:1rem;background:var(--panel-2);border-radius:8px 8px 0 0}
.xgroup h3 .muted{font-weight:400;font-size:.88rem}
.xrows{list-style:none;margin:0;padding:0}
.xrows li{display:grid;grid-template-columns:minmax(10em,1.1fr) minmax(0,1.6fr) minmax(0,1.6fr);gap:4px 16px;align-items:baseline;padding:7px 14px;border-top:1px solid var(--line)}
.xrows .xn{font-weight:700;display:flex;flex-direction:column}.xrows .xn .xr{font-weight:400}.xrows .xr{color:var(--muted);font-size:.9rem}
.xrows .xsw{display:flex;flex-direction:column;gap:3px}
.xwhy{color:var(--muted);font-size:.78rem;font-style:italic}
.xopen{display:block;margin-top:3px;color:var(--fg);font-size:.82rem;font-weight:700}
.xrows .xs{display:flex;flex-wrap:wrap;gap:4px;align-items:center}
.xrows .xs .xchip{min-height:24px;font-size:.78rem;padding:0 8px;background:var(--panel-2);border-color:transparent}
.xmore{all:unset;cursor:pointer;display:block;margin:.4em 0 1.4em;padding:10px 16px;border:1px solid var(--accent);border-radius:8px;color:var(--accent);font-weight:700;text-align:center}
.xmore:hover{border-color:var(--accent-hover);color:var(--accent-hover)}
.xfilter{display:inline-flex;gap:6px;align-items:center;margin-left:8px;font-weight:400}
@media (max-width:720px){.xrows li{grid-template-columns:1fr}}
#count{font-weight:700}

/* ---- phone menu and the Views strip (shell) ---- */
.menu-btn{display:none;align-items:center;min-height:44px;padding:0 var(--s-4);border:1px solid rgba(255,255,255,.4);border-radius:8px;background:transparent;color:var(--on-deep);font:700 var(--t-sm)/1 var(--f-display);cursor:pointer}
.menu-btn:hover{border-color:#fff;background:rgba(255,255,255,.08)}
.menu-btn:focus-visible{outline:3px solid var(--light-blue)}
.menu-btn[aria-expanded=true]{background:rgba(255,255,255,.14);border-color:#fff}
@media (max-width:720px){
  .menu-btn{display:inline-flex}
  .site-header .wrap{flex-wrap:wrap}
  .site-header nav{display:none;width:100%}
  .menu-btn[aria-expanded=true]+nav{display:block}
  .site-header nav ul{flex-direction:column;gap:0;padding-bottom:var(--s-2)}
  .site-header nav a{display:block;padding:14px 0;border-bottom:1px solid rgba(255,255,255,.14);font-size:var(--t-sm)}
}
.views{background:var(--panel-2);border-bottom:1px solid var(--line)}
.views ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:0 var(--s-5)}
.views a{display:inline-flex;align-items:center;min-height:44px;font:700 var(--t-sm)/1.2 var(--f-display);text-decoration:none;border-bottom:3px solid transparent;color:var(--fg)}
.views a:hover{color:var(--accent-hover)}
.views a[aria-current=page]{border-bottom-color:var(--accent);color:var(--accent)}

/* ---- static home hero ---- */
.hero-static{margin:-24px calc(50% - 50vw) 0;padding:48px 0 44px;background:radial-gradient(120% 140% at 70% 0%,#0c6473 0%,#073f49 45%,#052e36 80%);color:var(--on-deep)}
.hero-static .wrap{max-width:1200px}
.hero-static h1{font-size:clamp(2.1rem,5vw,3.4rem);line-height:1.08;margin:.25em 0 .35em;color:#fff;max-width:16em}
.hero-static h1 em{font-style:normal;color:var(--lime)}
.hero-static .lede{color:var(--on-deep-muted);max-width:40em;margin:0 0 var(--s-4)}
.hero-static .hero-stats{margin:0 0 var(--s-5)}
.hero-static .hero-links{margin:var(--s-4) 0 0}
.hero-static .hero-links a{color:var(--light-blue);font-weight:700}
.hero-static .hero-links a:hover{color:#fff}

/* ---- one table toolbar, above every table: count, filter, Download these rows (CSV), Copy link ---- */
.tbar{display:flex;flex-wrap:wrap;gap:var(--s-2) var(--s-4);align-items:center;margin:var(--s-4) 0 var(--s-2)}
.tbar .tcount{font-weight:700;margin-right:auto}
.tbar .tfilter{margin:0}
.tbar button{min-height:44px}
.tbar .tmsg{color:var(--muted);font-size:var(--t-sm)}

/* ---- explorers: the graph, map + network and trade-show pages render inside the shell as one full-width stage ---- */
main.viz{max-width:none;padding:0;position:relative;height:max(540px,calc(100svh - 140px));overflow:hidden;font-size:15px;line-height:1.45}
.viz h1,.viz h2,.viz h3{border:0;margin:0;padding:0;text-wrap:balance}
.viz .stage,.viz canvas.stage{position:absolute;inset:0;width:100%;height:100%}
.viz .rail{position:absolute;top:12px;left:var(--s-4);width:300px;max-height:calc(100% - 24px);overflow:auto;z-index:2;display:flex;flex-direction:column;gap:14px;padding:var(--s-4);
  background:color-mix(in srgb,var(--panel) 92%,transparent);border:1px solid var(--line);border-radius:10px;backdrop-filter:blur(8px)}
.viz .vhead h1{font:700 var(--t-xl)/1.1 var(--f-display)}
.viz .vhead p{margin:2px 0 0;color:var(--muted);font-size:13px}
.viz .stat{font:500 12px/1.45 var(--f-body);color:var(--muted);font-variant-numeric:tabular-nums}
.viz .stat b{color:var(--fg);font-weight:700}
.viz fieldset{border:0;margin:0;padding:0;display:flex;flex-direction:column;gap:6px;background:none;border-radius:0}
.viz legend{font:700 12px/1 var(--f-display);letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;padding:0}
.viz .btns{display:flex;gap:6px;flex-wrap:wrap}
.viz .btn{display:inline-flex;align-items:center;min-height:36px;padding:6px 10px;border-radius:6px;border:1px solid var(--line);background:var(--panel-2);color:var(--fg);cursor:pointer;font:700 13px/1.2 var(--f-body);text-decoration:none}
.viz .btn:hover{border-color:var(--accent);background:var(--panel-2);color:var(--fg)}
.viz .btn.primary{background:var(--accent);color:var(--accent-fg);border-color:var(--accent)}
.viz .btn[aria-pressed=true]{border-color:var(--accent);color:var(--accent)}
.viz .seg{display:grid;grid-template-columns:repeat(3,1fr);background:var(--panel-2);border:1px solid var(--line);border-radius:7px;padding:2px}
.viz .seg input{position:absolute;opacity:0;pointer-events:none}
.viz .seg label{display:flex;align-items:center;justify-content:center;min-height:36px;border-radius:5px;cursor:pointer;font-size:13px;color:var(--muted)}
.viz .seg input:checked+label{background:var(--panel);color:var(--fg);box-shadow:0 0 0 1px var(--line);font-weight:700}
.viz .seg input:focus-visible+label{outline:3px solid var(--accent)}
.viz .morph{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.viz .morph button{min-height:44px;padding:0 6px;border:0;border-radius:0;background:var(--panel-2);color:var(--muted);font:700 15px/1 var(--f-display);cursor:pointer}
.viz .morph button[aria-pressed=true]{background:var(--accent);color:var(--accent-fg)}
.viz .morph button:focus-visible{outline:3px solid var(--accent);outline-offset:-3px}
.viz .toggles{display:grid;grid-template-columns:1fr 1fr;gap:0 10px}
.viz .toggles label,.viz .opt{display:flex;align-items:center;gap:8px;min-height:28px;font-size:13.5px;cursor:pointer}
.viz input[type=checkbox]{accent-color:var(--accent);margin:0;width:18px;height:18px;flex:none}
.viz .sw{width:10px;height:10px;border-radius:50%;flex:none;display:inline-block}
.viz .search{position:relative}
.viz .search input{width:100%;max-width:none;box-sizing:border-box;min-height:40px;padding:9px 11px;border-radius:7px;border:1px solid var(--line);background:var(--panel-2);color:var(--fg);font:14px var(--f-body)}
.viz .sugg{position:absolute;left:0;right:0;top:calc(100% + 4px);background:var(--panel);border:1px solid var(--line);border-radius:7px;overflow:hidden;z-index:5}
.viz .sugg button{display:flex;width:100%;justify-content:space-between;gap:8px;min-height:36px;padding:7px 10px;border:0;border-radius:0;background:none;color:var(--fg);font:13.5px var(--f-body);text-align:left;cursor:pointer}
.viz .sugg button:hover,.viz .sugg button:focus-visible{background:var(--panel-2)}
.viz .sugg small{color:var(--muted);font-size:11px;white-space:nowrap}
.viz .hint,.viz .foot{margin:0;font-size:12.5px;color:var(--muted)}
.viz .foot{font-size:11px;line-height:1.4}
.viz .card{position:absolute;top:12px;right:var(--s-4);width:340px;max-height:calc(100% - 24px);overflow:auto;z-index:3;box-shadow:none;
  background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:var(--s-4);display:flex;flex-direction:column;gap:10px}
.viz .card .kind{font:700 12px/1 var(--f-display);letter-spacing:.12em;text-transform:uppercase}
.viz .card h2{font:700 24px/1.1 var(--f-display)}
.viz .card p{margin:0}
.viz .card h3{margin:4px 0 0;font:700 12px/1 var(--f-display);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.viz .card a{color:var(--accent)}
.viz .meta{display:grid;grid-template-columns:auto 1fr;gap:3px 12px;font-size:13.5px;margin:0}
.viz .meta dt{color:var(--muted)}
.viz .meta dd{margin:0;min-width:0;overflow-wrap:anywhere}
.viz .mono{font-size:12px}
.viz .chips{display:flex;flex-wrap:wrap;gap:5px}
.viz .chip{display:inline-block;border:1px solid var(--line);background:var(--panel-2);color:var(--fg);border-radius:999px;padding:3px 9px;font:12.5px var(--f-body);cursor:pointer}
.viz .chip:hover,.viz .chip:focus-visible{border-color:var(--accent)}
.viz .close{position:absolute;top:6px;right:6px;border:0;background:none;color:var(--muted);font-size:20px;cursor:pointer;line-height:1;min-height:44px;min-width:44px;padding:0}
.viz .legend{display:flex;flex-direction:column;gap:4px;font-size:13px}
.viz .legend div{display:flex;align-items:center;gap:8px}
.viz .tip{position:absolute;pointer-events:none;z-index:4;background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:5px 8px;font-size:13px;max-width:260px}
.viz .tip small{display:block;color:var(--muted);font-size:11px}
/* the trade-show stage is deliberately dark, in both colour schemes: a single look for big screens */
.viz.dark{--bg:#052e36;--panel:rgba(7,63,73,.9);--panel-2:#0a4a55;--fg:#eef3f2;--muted:#a9c2c3;--line:rgba(102,215,222,.24);--accent:#66d7de;--accent-hover:#dba8c9;--accent-fg:#052e36;
  --r1:#66c0d2;--r2:#e0a040;--r3:#c98ab2;--r4:#f08a64;--r5:#b8d637;--rx:#b0b3ae;background:var(--bg);color:var(--fg);color-scheme:dark}
.viz.dark a{color:var(--accent)}
/* below 720 px an explorer is a plain summary with links (explorer.js loads nothing there); the legend and the shell header stay */
.viz-summary{display:none}
.viz-summary .vlegend{list-style:none;margin:0;padding:0;display:grid;gap:var(--s-2)}
.viz-summary .vlegend li{display:flex;align-items:center;gap:var(--s-2)}
.viz-summary .sw{width:12px;height:12px;border-radius:50%;flex:none;display:inline-block}
.viz-summary .btns{margin:var(--s-4) 0}
@media (max-width:719.98px){
  main.viz{height:auto;overflow:visible}
  .viz-summary{display:block;padding:var(--s-5) var(--s-4)}
  .viz .stage,.viz .rail,.viz .card,.viz .tip,.viz .title,.viz .bar,.viz .caption{display:none!important}
}
@media (prefers-reduced-motion:reduce){.viz *{scroll-behavior:auto!important}}

"""

MAP_JS = r"""(function () {
  'use strict';
  // Ring colours come from the page's own tokens (--r1..--r5, --rx in style.css), so the dots, the key and every other page agree.
  var COLORS = {};
  function readColors() { var css = getComputedStyle(document.documentElement); ['1', '2', '3', '4', '5', 'x'].forEach(function (k) { COLORS[k] = css.getPropertyValue('--r' + k).trim(); }); }
  readColors();
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
      m.ringKey = key;
      m.bindPopup(function () { return popup(r); });
      return m;
    });
    matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {   // the key follows the scheme; so do the dots
      readColors(); markers.forEach(function (m) { m.setStyle({fillColor: COLORS[m.ringKey] || COLORS.x}); });
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
      var pic = document.getElementById('f-pic18'), picOnly = pic.checked, picCounties = pic.getAttribute('data-counties').split(',');
      var rs = {}, ts = {}, ss = {};
      rings.forEach(function (v) { rs[v] = 1; }); tiers.forEach(function (v) { ts[v] = 1; });
      states.forEach(function (v) { ss[v] = 1; });
      group.clearLayers();
      var shown = [];
      rows.forEach(function (r, i) {
        if (!rs[r[C.ring] || 'x']) return;
        if (!ts[r[C.tier] || 'x']) return;
        if (!ss[r[C.st] || 'x']) return;
        if (picOnly && !(r[C.st] === 'OH' && picCounties.indexOf(r[C.co]) >= 0)) return;
        if (!allStatus && r[C.status] !== 'active') return;
        group.addLayer(markers[i]); shown.push(markers[i]);
      });
      status.textContent = 'Showing ' + shown.length.toLocaleString() + ' of ' + rows.length.toLocaleString() +
        ' site rows that have coordinates (filters applied: ring, tier, state' + (picOnly ? ', PIC-18 counties only' : '') + (allStatus ? '' : ', operating status active only') + ').';
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

DIRECTORY_JS = r"""(function () {
  'use strict';
  // Directory. Rows load from directory.json (one per owner and county, sorted by county then name) and are
  // drawn PAGE at a time. Within one filter the choices are OR; across filters they are AND. "_" is the unknown option
  // (a row with no tokens).
  var PAGE = __PAGE__;
  var form = document.getElementById('dfilters'), list = document.getElementById('dlist');
  if (!form || !list) return;
  document.getElementById('dfind').hidden = false;   // without JavaScript this part stays hidden; the noscript note and directory/ pages serve instead
  var body = document.getElementById('dtable').tBodies[0], q = document.getElementById('dq');
  var status = document.getElementById('dstatus'), left = document.getElementById('dleft');
  var prev = document.getElementById('dprev'), next = document.getElementById('dnext'), pos = document.getElementById('dpos');
  var F = ['co', 'ring', 'tier', 'band', 'proc', 'mat', 'mkt', 'own'];
  var PARAM = {co: 'county', ring: 'ring', tier: 'tier', band: 'employees', proc: 'process', mat: 'material', mkt: 'market', own: 'ownership'};
  var NAME = {co: 'county', ring: 'ring', tier: 'site tier', band: 'employee band', proc: 'process', mat: 'material', mkt: 'market', own: 'ownership'};
  var COLS = ['Street address', 'Ring', 'Site tier', 'Process', 'Material', 'Market', 'Employees', 'Ownership', 'Evidence rows',
              'Organization record (status, tier)', 'Website'];
  var boxes = {}, data = [], hits = [], page = 0;
  status.textContent = 'Loading the list...';
  F.forEach(function (f) { boxes[f] = Array.prototype.slice.call(form.querySelectorAll('input[name="' + f + '"]')); });
  function chosen(f) { return boxes[f].filter(function (b) { return b.checked; }).map(function (b) { return b.value; }); }
  function pass(r, f, sel) {
    if (!sel.length) return true;
    var t = r.tok[f];
    if (!t.length) return sel.indexOf('_') >= 0;
    return sel.some(function (v) { return t.indexOf(v) >= 0; });
  }
  function values(r) {   // the text of each column after the name, as on screen and in the download
    var s = r.show;
    return [r.addr.join('; '), s.ring, s.tier, s.proc, s.mat, s.mkt, s.band, s.own, String(r.ev), r.org, r.web || 'unknown'];
  }
  function fromUrl() {
    var u = new URLSearchParams(location.search);
    q.value = u.get('q') || '';
    F.forEach(function (f) {
      var want = (u.get(PARAM[f]) || '').split(',').filter(Boolean);
      boxes[f].forEach(function (b) { b.checked = want.indexOf(b.value) >= 0; });
    });
  }
  function toUrl() {
    var u = new URLSearchParams();
    if (q.value.trim()) u.set('q', q.value.trim());
    F.forEach(function (f) { var c = chosen(f); if (c.length) u.set(PARAM[f], c.join(',')); });
    var s = u.toString();
    history.replaceState(null, '', location.pathname + (s ? '?' + s : ''));
  }
  function el(tag, text, attrs) {
    var n = document.createElement(tag);
    if (text !== undefined && text !== null) n.textContent = text;
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    return n;
  }
  function cell(i, label, v, r) {
    var td = el('td', null, {'data-label': label});
    if (i === 0) {   // one line per street address
      r.addr.forEach(function (a, k) { if (k) td.appendChild(el('br')); td.appendChild(document.createTextNode(a)); });
    } else if (i === 8) {
      td.className = 'num';
      td.appendChild(el('a', v, {href: 'orgs/' + r.id + '.html#evidence'}));
    } else if (i === 10 && r.web) {
      td.appendChild(el('a', v, {href: r.web, 'class': 'url', rel: 'noopener nofollow'}));
    } else {
      td.textContent = v;
      if (v === 'unknown') td.className = 'muted';
    }
    return td;
  }
  function render() {
    var pages = Math.max(1, Math.ceil(hits.length / PAGE)), perCounty = {};
    hits.forEach(function (r) { perCounty[r.co] = (perCounty[r.co] || 0) + 1; });
    page = Math.min(page, pages - 1);
    body.textContent = '';
    var last = null;
    hits.slice(page * PAGE, page * PAGE + PAGE).forEach(function (r) {
      if (r.co !== last) {   // county heading row
        var h = el('tr', null, {'class': 'total'}), th = el('th', r.co + ' County: ' + perCounty[r.co].toLocaleString() + ' owners',
          {scope: 'colgroup', colspan: String(COLS.length + 1)});
        h.appendChild(th); body.appendChild(h); last = r.co;
      }
      var tr = el('tr'), th2 = el('th', null, {scope: 'row'});
      th2.appendChild(el('a', r.name, {href: 'orgs/' + r.id + '.html'}));
      if (r.member) { th2.appendChild(document.createTextNode(' ')); th2.appendChild(el('span', 'PIC member', {'class': 'badge'})); }
      tr.appendChild(th2);
      values(r).forEach(function (v, i) { tr.appendChild(cell(i, COLS[i], v, r)); });
      body.appendChild(tr);
    });
    var from = hits.length ? page * PAGE + 1 : 0, to = Math.min(hits.length, page * PAGE + PAGE);
    pos.textContent = 'Rows ' + from.toLocaleString() + ' to ' + to.toLocaleString() + ' of ' + hits.length.toLocaleString() + ' (page ' + (page + 1) + ' of ' + pages + ')';
    prev.disabled = page === 0;
    next.disabled = page >= pages - 1;
  }
  function run() {
    var sel = {}, term = q.value.trim().toLowerCase(), counts = {};
    F.forEach(function (f) { sel[f] = chosen(f); counts[f] = {}; });
    hits = [];
    data.forEach(function (r) {
      var ok = {}, all = true;
      F.forEach(function (f) { ok[f] = pass(r, f, sel[f]); if (!ok[f]) all = false; });
      var okq = !term || r.name.toLowerCase().indexOf(term) >= 0;
      if (all && okq) hits.push(r);
      F.forEach(function (f) {   // counts for one filter: rows that pass every OTHER filter
        if (!okq || !F.every(function (g) { return g === f || ok[g]; })) return;
        var t = r.tok[f];
        if (!t.length) t = ['_'];
        t.forEach(function (v) { counts[f][v] = (counts[f][v] || 0) + 1; });
      });
    });
    var notes = [];
    F.forEach(function (f) {
      boxes[f].forEach(function (b) {
        var n = counts[f][b.value] || 0;
        b.parentNode.querySelector('.n').textContent = n.toLocaleString();
        b.parentNode.classList.toggle('zero', n === 0 && !b.checked);
      });
      var c = sel[f].length, u = counts[f]['_'] || 0;
      boxes[f][0].closest('details').querySelector('.sel').textContent = c ? ' (' + c + ' chosen)' : '';
      if (c && sel[f].indexOf('_') < 0 && u) notes.push(u.toLocaleString() + ' with unknown ' + NAME[f]);
    });
    status.textContent = 'Showing ' + hits.length.toLocaleString() + ' of ' + data.length.toLocaleString() + ' rows (one per owner and county).';
    left.textContent = notes.length ? 'Left out because the field is unknown (within your other choices): ' + notes.join('; ') + '. Choose "Unknown" in that filter to see them.' : '';
    page = 0;
    render();
    toUrl();
  }
  function csvCell(s) {
    s = String(s).replace(/\s+/g, ' ').trim();
    if (/^[=+@]/.test(s) || /^-(?!\d)/.test(s)) s = "'" + s;   // spreadsheets would run a leading = + @ - as a formula
    return /[",]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  document.getElementById('ddl').addEventListener('click', function () {   // every filtered row, not only the page on screen
    var lines = [['County', 'Organization', 'PIC member'].concat(COLS).map(csvCell).join(',')];
    hits.forEach(function (r) { lines.push([r.co, r.name, r.member ? 'yes' : ''].concat(values(r)).map(csvCell).join(',')); });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob(['﻿' + lines.join('\r\n') + '\r\n'], {type: 'text/csv;charset=utf-8'}));
    a.download = 'northeast-ohio-polymer-companies-' + new Date().toISOString().slice(0, 10) + '.csv';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  });
  document.getElementById('dcopy').addEventListener('click', function () {   // the address bar holds the filters
    var msg = document.getElementById('dmsg'), done = function (t) { msg.textContent = t; setTimeout(function () { msg.textContent = ''; }, 2500); };
    if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(function () { done('Link copied'); }, function () { done('Copy failed: copy the address bar'); });
    else done('Copy the address bar');
  });
  function turn(d) { page += d; render(); status.focus(); }
  prev.addEventListener('click', function () { turn(-1); });
  next.addEventListener('click', function () { turn(1); });
  var timer;
  form.addEventListener('change', run);
  q.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(run, 120); });
  fetch('directory.json').then(function (r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }).then(function (d) {
    data = d.rows;
    list.hidden = false;
    document.getElementById('ddl').disabled = false; document.getElementById('dcopy').disabled = false;
    fromUrl(); run();
  }).catch(function (e) {
    status.textContent = 'Could not load directory.json (' + e.message + '). If you opened this file directly from disk, serve the folder over http instead (see docs/SITE_HOWTO.md). The county pages and directory.csv hold the same rows.';
  });
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
    else count.textContent = hits.length.toLocaleString() + ' organization row' + (hits.length === 1 ? ' matches' : 's match') + (hits.length > cap ? ' (showing the first ' + cap + ')' : '') + '.';
  }
})();
"""


# --------------------------------------------------------------------------
# pages


_sk_spec = importlib.util.spec_from_file_location("site_skyline", Path(__file__).resolve().parent / "site_skyline.py")
skyline = importlib.util.module_from_spec(_sk_spec)
_sk_spec.loader.exec_module(skyline)

GLYPHS = {
    "directory": '<svg viewBox="0 0 240 84" aria-hidden="true"><g fill="none" stroke="var(--line)" stroke-width="1.4"><rect x="40" y="10" width="160" height="64" rx="6"/>'
                 '<line x1="40" y1="28" x2="200" y2="28"/><line x1="40" y1="44" x2="200" y2="44"/><line x1="40" y1="60" x2="200" y2="60"/>'
                 '<line x1="92" y1="10" x2="92" y2="74"/><line x1="150" y1="10" x2="150" y2="74"/></g><rect x="48" y="33" width="36" height="6" rx="3" fill="var(--accent)"/>'
                 '<rect x="100" y="49" width="40" height="6" rx="3" fill="var(--r2)"/><rect x="158" y="33" width="30" height="6" rx="3" fill="var(--r1)"/></svg>',
    "graph": '<svg viewBox="0 0 240 84" aria-hidden="true"><g stroke="var(--line)" stroke-width="1.2">'
             '<line x1="40" y1="42" x2="96" y2="20"/><line x1="40" y1="42" x2="92" y2="66"/><line x1="96" y1="20" x2="150" y2="40"/>'
             '<line x1="92" y1="66" x2="150" y2="40"/><line x1="150" y1="40" x2="204" y2="22"/><line x1="150" y1="40" x2="200" y2="64"/>'
             '<line x1="96" y1="20" x2="92" y2="66"/></g><g><circle cx="40" cy="42" r="6" fill="var(--r1)"/><circle cx="96" cy="20" r="5" fill="var(--r2)"/>'
             '<circle cx="92" cy="66" r="5" fill="var(--r1)"/><circle cx="150" cy="40" r="11" fill="var(--accent)"/><circle cx="204" cy="22" r="5" fill="var(--r3)"/>'
             '<circle cx="200" cy="64" r="6" fill="var(--r2)"/></g></svg>',
    "geo": '<svg viewBox="0 0 240 84" aria-hidden="true"><path d="M20 60 Q70 8 120 40 T220 30" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="3 4"/>'
           '<path d="M30 30 Q90 70 150 52 T225 66" fill="none" stroke="var(--r2)" stroke-width="1.5" stroke-dasharray="3 4"/>'
           + "".join(f'<circle cx="{20 + (i * 37) % 205}" cy="{14 + (i * 23) % 60}" r="{2 + i % 3}" fill="var(--r{1 + i % 3})"/>' for i in range(22)) + '</svg>',
    "shows": '<svg viewBox="0 0 240 84" aria-hidden="true"><ellipse cx="120" cy="42" rx="96" ry="26" fill="none" stroke="var(--line)"/>'
             '<ellipse cx="120" cy="42" rx="60" ry="16" fill="none" stroke="var(--line)"/><circle cx="120" cy="42" r="10" fill="var(--lime)"/>'
             '<circle cx="34" cy="38" r="5" fill="var(--r1)"/><circle cx="196" cy="52" r="6" fill="var(--r2)"/><circle cx="160" cy="28" r="4" fill="var(--r3)"/>'
             '<circle cx="80" cy="56" r="4" fill="var(--r4)"/></svg>',
    "experts": '<svg viewBox="0 0 240 84" aria-hidden="true"><g fill="none" stroke="var(--line)" stroke-width="1.4">'
               '<path d="M70 42 L120 22 L170 42 L120 62 Z"/></g><circle cx="120" cy="22" r="9" fill="var(--accent)"/>'
               '<circle cx="70" cy="42" r="6" fill="var(--r1)"/><circle cx="170" cy="42" r="6" fill="var(--r3)"/>'
               '<circle cx="120" cy="62" r="6" fill="var(--r2)"/><rect x="100" y="70" width="40" height="5" rx="2" fill="var(--line)"/></svg>',
    "counties": '<svg viewBox="0 0 240 84" aria-hidden="true">' + "".join(
        f'<polygon points="{x},{y - 12} {x + 10},{y - 6} {x + 10},{y + 6} {x},{y + 12} {x - 10},{y + 6} {x - 10},{y - 6}" '
        f'fill="var(--{c})" opacity="{o}"/>'
        for x, y, c, o in [(60, 30, "r1", .9), (80, 30, "accent", 1), (100, 30, "r1", .6), (70, 48, "r2", .8), (90, 48, "r1", .9),
                           (110, 48, "r3", .7), (130, 48, "r1", .4), (100, 66, "r2", .5), (120, 30, "r1", .3), (140, 30, "r3", .5)]) + '</svg>',
}


def active_ab(sites):
    return [s for s in sites if s.get("operating_status") == "active"
            and s.get("verification_tier") in ("A", "B", "C")]


# --------------------------------------------------------------------------
# Northeast Ohio polymer companies (directory.html): one row per owner (organization or ecosystem record) and PIC-18 county,
# built from the organization's active tier A-C site rows in that county

UNKNOWN_VALUES = {"", "unknown"}       # blank and the literal vocabulary value both mean "nothing recorded"
BAND_MINS = (50, 100, 250, 500, 1000)  # "N or more" shortcuts: a band whose lower bound is at least N
DIRECTORY_PAGE = 50                    # rows rendered at a time, on screen and in the page script
DIRECTORY_FACETS = [("co", "County"), ("ring", "Ring"), ("tier", "Site tier"), ("band", "Employees"),
                    ("proc", "Process"), ("mat", "Material"), ("mkt", "Market"), ("own", "Ownership")]
MEMBER_YES = "on the public member list"   # AGENTS.md section 5.1: the only membership wording; absence is never stated
def known(values):
    return sorted({v for v in values if v not in UNKNOWN_VALUES})


def tok(value):
    """Filter token: one space-free word, so a row can carry several."""
    return re.sub(r"\s+", "_", str(value).strip())


def band_floor(band):
    m = re.match(r"\d+", band)
    return int(m.group()) if m else None


def pic18_active_sites(sites):
    """The PIC-18 headline set: Ohio county in PIC-18, operating status active, verification tier A-C."""
    return active_ab([s for s in sites if s.get("state") == "OH" and s.get("county") in PIC12])


def evidence_view(a, table, rid):
    """One record's evidence rows (SCHEMA 4.13)."""
    return a.evidence.get((table, rid), [])


def org_evidence_count(a, oid):
    """Evidence rows the organization page shows: the organization's own plus those of all its site rows."""
    table = "organizations" if oid in a.orgs else "ecosystem"
    return (len(evidence_view(a, table, oid))
            + sum(len(evidence_view(a, "sites", s["site_id"])) for s in a.sites_by_org.get(oid, [])))


def site_address(s):
    """Street, city, state and ZIP as recorded; a missing street says so (158 of the PIC-18 site rows have none)."""
    street = str(s.get("street_address") or "").strip() or "Street not recorded"
    region = " ".join(x for x in [s.get("state"), s.get("zip")] if nonempty(x))
    return ", ".join(x for x in [street, s.get("city"), region] if nonempty(x))


def directory_rows(a):
    """One dict per owner and PIC-18 county, from that owner's PIC-18 active tier A-C site rows there. An owner is an
    organization record or an ecosystem record (787 and 7 at the time of writing).

    An owner with sites in two counties has two rows, so a county's row count is its owner count.
    Employee band: the band on the row's site rows, else the organization's Ohio band. Process, material and market
    follow the same rule. Each of those fields is (tokens, basis); no tokens means unknown."""
    by_key = defaultdict(list)
    for s in pic18_active_sites(a.sites):
        by_key[(s["org_id"], s["county"])].append(s)
    rows = []
    for (oid, county), sites in by_key.items():
        rec = a.orgs.get(oid) or a.eco.get(oid) or {}

        def pick(site_field, org_field):
            t = known(v for s in sites for v in vals(s.get(site_field)))
            if t:
                return t, "site"
            t = known(vals(rec.get(org_field)))
            return (t, "org record") if t else ([], "")
        rows.append({
            "id": oid, "name": rec.get("legal_name") or oid, "website": safe_href(rec.get("website")) or "",
            "hq_city": rec.get("hq_city") or rec.get("city") or "", "hq_state": rec.get("hq_state") or rec.get("state") or "",
            "county": county, "eco": oid not in a.orgs, "addr": sorted({site_address(s) for s in sites}), "n_sites": len(sites),
            "rings": known(s["_ring"] for s in sites if s["_ring"]), "ring_sites": Counter(s["_ring"] or "_" for s in sites),
            "tiers": sorted({s["verification_tier"] for s in sites}),
            "proc": pick("processes", "processes"), "mat": pick("materials", "materials"),
            "mkt": pick("markets_served", "markets_served"), "band": pick("employee_band_site", "employee_band_ohio"),
            "own": known(vals(rec.get("ownership_type"))), "member": rec.get("pic_member") == "true",
            "evidence": org_evidence_count(a, oid), "status": rec.get("status") or "", "org_tier": rec.get("verification_tier") or "",
        })
    rows.sort(key=lambda r: (r["county"], r["name"].lower(), r["id"]))
    return rows


def row_tokens(r, key):
    """The filter tokens one row carries for one facet (none = unknown)."""
    if key == "co":
        return [tok(r["county"])]
    if key == "ring":
        return r["rings"]
    if key == "tier":
        return r["tiers"]
    if key == "band":
        bands = r["band"][0]
        mins = sorted({n for b in bands for n in BAND_MINS if (band_floor(b) or 0) >= n})
        return [tok(b) for b in bands] + [f"min{n}" for n in mins]
    if key == "own":
        return [tok(o) for o in r["own"]]
    return [tok(t) for t in r[key][0]]


def facet_options(rows, key):
    """[(token, label, count over all rows)] in display order; the unknown option is added by the caller."""
    counts = Counter(t for r in rows for t in row_tokens(r, key))
    labels = {}
    for r in rows:
        if key in ("proc", "mat", "mkt"):
            labels.update({tok(t): vocab(t) for t in r[key][0]})
        elif key == "own":
            labels.update({tok(t): vocab(t) for t in r["own"]})
        elif key == "band":
            labels.update({tok(b): b for b in r["band"][0]})
    if key == "co":
        order = sorted(counts)
        labels = {c: c for c in order}
    elif key == "ring":
        order = sorted(counts)
        labels = {x: f"Ring {x}: {RINGS.get(x, '')}" for x in order}
    elif key == "tier":
        order = sorted(counts)
        labels = {x: f"Tier {x}: {TIERS[x][0]}" for x in order}
    elif key == "band":
        mins = [f"min{n}" for n in BAND_MINS]
        exact = sorted((t for t in counts if not t.startswith("min")), key=lambda t: (band_floor(t) or 0, t))
        order = mins + exact
        labels.update({f"min{n}": f"{n} or more (band starts at {n}+)" for n in BAND_MINS})
    else:
        order = sorted(counts, key=lambda t: (-counts[t], labels[t]))
    return [(t, labels[t], counts.get(t, 0)) for t in order]


def facet_html(rows, key, heading, open_):
    opts = facet_options(rows, key)
    n_unknown = sum(1 for r in rows if not row_tokens(r, key))
    opts.append(("_", "Unknown (nothing recorded)", n_unknown))
    items = "".join(
        f'<label class="opt"><input type="checkbox" name="{key}" value="{esc(t)}"> '
        f'<span class="t">{esc(label)}</span> <span class="n">{n}</span></label>' for t, label, n in opts)
    return (f'<details class="facet"{" open" if open_ else ""}><summary>{esc(heading)}<span class="sel"></span></summary>'
            f'<div class="opts">{items}</div></details>')


def cell_text(tokens, basis, always_basis=False):
    """A value for the list: readable vocabulary, with its basis when it comes from the organization's own record."""
    if not tokens:
        return "unknown"
    text = vocab(";".join(tokens))
    return f"{text} ({basis})" if basis and (always_basis or basis == "org record") else text


def directory_json(rows):
    """directory.json: the list the page renders 50 rows at a time. Tokens drive the filters; show is the text on screen."""
    out = []
    for r in rows:
        out.append({
            "id": r["id"], "name": r["name"], "co": r["county"], "addr": r["addr"], "member": r["member"],
            "web": r["website"], "ev": r["evidence"],
            "org": ", ".join(x for x in [str(r["status"]).replace("_", " ") if r["status"] else "status unknown",
                                         f"tier {r['org_tier']}" if r["org_tier"] else ""] if x),
            "tok": {k: row_tokens(r, k) for k, _ in DIRECTORY_FACETS},
            "show": {"ring": ", ".join(r["rings"]) or "unknown", "tier": ", ".join(r["tiers"]),
                     "proc": cell_text(*r["proc"]), "mat": cell_text(*r["mat"]), "mkt": cell_text(*r["mkt"]),
                     "band": cell_text(*r["band"], always_basis=True), "own": cell_text(r["own"], "")}})
    return {"rows": out}


def directory_csv(rows, base_url):
    """directory.csv (and its copy prospects.csv): one row per owner and PIC-18 county; unknown is written out,
    never left blank. public_member_list is "yes" only for an organization on the public PIC member list; it is blank
    otherwise, which is not a statement about membership."""
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\r\n")
    w.writerow(["org_id", "organization", "website", "hq_city", "hq_state", "pic18_counties", "pic18_site_rows", "rings",
                "site_tiers", "processes", "processes_basis", "materials", "materials_basis", "markets", "markets_basis",
                "employee_band", "employee_band_basis", "ownership", "public_member_list", "evidence_rows",
                "org_record_status", "org_record_tier", "atlas_page", "pic18_site_addresses"])

    def safe(v):   # spreadsheets run a leading = + @ - as a formula
        v = str(v)
        return "'" + v if re.match(r"[=+@]|-(?!\d)", v) else v

    def cell(tokens):   # readable vocabulary, as on the page
        return "; ".join(t.replace("_", " ") for t in tokens) if tokens else "unknown"
    for r in rows:
        w.writerow([safe(x) for x in [
            r["id"], r["name"], r["website"] or "unknown", r["hq_city"], r["hq_state"], r["county"],
            r["n_sites"], cell(r["rings"]), "; ".join(r["tiers"]),
            cell(r["proc"][0]), r["proc"][1] or "unknown", cell(r["mat"][0]), r["mat"][1] or "unknown",
            cell(r["mkt"][0]), r["mkt"][1] or "unknown", cell(r["band"][0]), r["band"][1] or "unknown",
            cell(r["own"]), "yes" if r["member"] else "", r["evidence"],
            r["status"] or "unknown", r["org_tier"] or "unknown", f"{base_url}orgs/{safe_id(r['id'])}.html",
            "; ".join(r["addr"])]])
    return out.getvalue()


DIRECTORY_HEAD = ["Organization", "Street address", "Ring", "Site tier", "Process", "Material", "Market", "Employees",
                  "Ownership", "Evidence rows", "Organization record (status, tier)", "Website"]


def summary_table(label, rows, caption):
    """Summary table: (label, link or None, owners, site rows) lines plus the All PIC-18 total."""
    def name(text, href):
        return f'<a href="{esc(href)}">{esc(text)}</a>' if href else esc(text)
    body = "".join(
        f'<tr><th scope="row">{name(text, href)}</th>'
        f'<td class="num">{fmt_int(n_org)}</td><td class="num">{fmt_int(n_site)}</td></tr>' for text, href, n_org, n_site in label)
    total = (f'<tr class="total"><th scope="row">All PIC-18</th><td class="num">{fmt_int(len({r["id"] for r in rows}))}</td>'
             f'<td class="num">{fmt_int(sum(r["n_sites"] for r in rows))}</td></tr>')
    return (f'<table data-nosort data-nofilter data-nocsv><caption>{esc(caption)}</caption><thead><tr>'
            f'<th scope="col">{esc(caption.rsplit(" ", 1)[1].capitalize())}</th><th scope="col" class="num">Owners</th>'
            f'<th scope="col" class="num">Site rows</th></tr></thead><tbody>{body}{total}</tbody></table>')


def build_directory_page(ctx, rows):
    n_orgs = len({r["id"] for r in rows})
    n_eco = len({r["id"] for r in rows if r["eco"]})
    n_sites = sum(r["n_sites"] for r in rows)
    counties = sorted({r["county"] for r in rows})
    by_county = [(c, f"directory.html?county={c}#find", sum(1 for r in rows if r["county"] == c),
                  sum(r["n_sites"] for r in rows if r["county"] == c)) for c in counties]
    ring_keys = sorted({k for r in rows for k in r["ring_sites"]}, key=lambda k: (k == "_", k))
    by_ring = [(f"Ring {k}: {RINGS.get(k, '')}" if k != "_" else "Ring not recorded", None,
                len({r["id"] for r in rows if r["ring_sites"].get(k)}), sum(r["ring_sites"].get(k, 0) for r in rows))
               for k in ring_keys]
    cap = "owners with an active tier A-C site row, by"
    summary = (table_wrap(summary_table(by_county, rows, f"PIC-18 {cap} county"), "Counts by county")
               + table_wrap(summary_table(by_ring, rows, f"PIC-18 {cap} ring"), "Counts by ring"))
    facets = "".join(facet_html(rows, k, h, k in ("co", "ring", "tier", "band")) for k, h in DIRECTORY_FACETS)
    num = ' class="num"'
    head = "".join(f'<th scope="col"{num if h == "Evidence rows" else ""}>{esc(h)}</th>' for h in DIRECTORY_HEAD)
    county_links = " · ".join(f'<a href="directory/{slug(c)}.html">{esc(c)} ({fmt_int(sum(1 for r in rows if r["county"] == c))})</a>'
                              for c in counties)
    body = f"""
<h1>Northeast Ohio polymer companies</h1>
<p class="lede">{fmt_int(n_orgs)} owners of active, tier A-C site rows in the 18 PIC counties: {fmt_int(n_orgs - n_eco)} organization records and
{fmt_int(n_eco)} ecosystem records, with {fmt_int(n_sites)} such site rows. Each count below is owners with an active tier A-C site row in that county or ring.</p>
{summary}
<p>This page lists companies in the 18 PIC counties. For any other company in the Atlas, in any state,
<a href="search.html">search every organization</a>.</p>
<p class="small muted">An owner with site rows in more than one county or ring is counted in each, so these columns can
add up to more than the All PIC-18 line. Counts are owners, not unique ultimate parents.</p>
<noscript><p>Search, filters and the paged list need JavaScript. Without it, browse by county, {DIRECTORY_PAGE} rows a page, with street addresses:
{county_links}. Every row is also in <a href="directory.csv">directory.csv</a>.</p></noscript>
<div id="dfind" hidden>
<h2 id="find">Find a company</h2>
<p>Search by name, narrow with the filters, and download what you see. The address bar holds your choices, so you can send the link.
A <span class="badge">PIC member</span> badge marks an owner on PIC's public member list.</p>
<details class="more"><summary>How to read the list</summary>
<p><strong>Unknown means nothing is recorded: not zero, not small.</strong> Every filter shows how many rows are unknown.</p>
<p>One row per owner and county, grouped by county; an owner with site rows in two counties is listed under both,
with the street addresses of the site rows in that county. Ring and site tier list every value among those site rows; within one
filter the choices are "or", across filters "and". Street addresses are as recorded; a site row with no street says so.</p>
<p><strong>Employees</strong> is the band recorded on the site rows in that county, otherwise the organization's Ohio band, and each row
says which (site or org record). Process, material and market follow the same rule and say so when they come from the organization's
own row. Bands are bands, never headcounts. "N or more" means the band starts at N or higher.</p></details>
<form id="dfilters" onsubmit="return false" role="search" aria-label="Find a company">
<p><label for="dq"><strong>Name contains</strong></label><br><input type="search" id="dq" autocomplete="off"></p>
<div class="facets">{facets}</div>
<p><a href="directory.html">Clear all filters</a></p>
</form>
<div class="tbar"><span id="dstatus" class="tcount" role="status" aria-live="polite" tabindex="-1"></span>
<button type="button" id="ddl" disabled>Download these rows (CSV)</button><button type="button" id="dcopy" disabled>Copy link</button>
<span class="tmsg" id="dmsg" role="status"></span></div>
<p id="dleft" class="small" aria-live="polite"></p>
<div id="dlist" hidden>
{table_wrap(f'<table id="dtable" class="stack" data-nosort data-nofilter data-nocsv><caption>Northeast Ohio polymer companies: owners by PIC-18 county (operating status active; verification tiers A-C)</caption><thead><tr>{head}</tr></thead><tbody></tbody></table>', "Northeast Ohio polymer companies")}
<p id="dpager"><button type="button" id="dprev">Previous {DIRECTORY_PAGE}</button> <span id="dpos"></span> <button type="button" id="dnext">Next {DIRECTORY_PAGE}</button></p>
<p class="small muted">The download saves every row that matches your filters, not only the {DIRECTORY_PAGE} on screen. For the whole table,
take <a href="directory.csv">directory.csv</a> ({fmt_int(len(rows))} rows, one per owner and county, unfiltered).
Evidence rows count the claim-level evidence on the owner's page (its own and its site rows').
Website is the owner's recorded website. No contact people are published.</p>
</div>
</div>
"""
    return page(ctx, "Northeast Ohio polymer companies", body, "", "directory",
                "Polymer companies in the 18 Northeast Ohio PIC counties: counts by county and ring, then search, filter and download the list with street addresses.",
                "", '<script src="directory.js" defer></script>')


def directory_static_pages(ctx, rows):
    """{file name: html} for directory/<county>.html, <county>-2.html ...: the same rows, 50 a page, for readers without JavaScript."""
    out = {}
    for c in sorted({r["county"] for r in rows}):
        crows = [r for r in rows if r["county"] == c]
        pages = -(-len(crows) // DIRECTORY_PAGE)
        names = [f"{slug(c)}.html" if n == 1 else f"{slug(c)}-{n}.html" for n in range(1, pages + 1)]
        badge = ' <span class="badge">PIC member</span>'
        for n, name in enumerate(names, 1):
            part = crows[(n - 1) * DIRECTORY_PAGE:n * DIRECTORY_PAGE]
            trs = "".join(
                f'<tr><th scope="row"><a href="../orgs/{esc(safe_id(r["id"]))}.html">{esc(r["name"])}</a>'
                f'{badge if r["member"] else ""}</th><td>{"<br>".join(esc(x) for x in r["addr"])}</td>'
                f'<td>{esc(", ".join(r["rings"]) or "unknown")}</td><td>{esc(", ".join(r["tiers"]))}</td>'
                f'<td>{esc(cell_text(*r["proc"]))}</td><td>{esc(cell_text(*r["band"], always_basis=True))}</td></tr>' for r in part)
            nav = " · ".join(x for x in [
                f'<a href="{names[n - 2]}">Previous {DIRECTORY_PAGE}</a>' if n > 1 else "",
                f'<a href="{names[n]}">Next {DIRECTORY_PAGE}</a>' if n < pages else "",
                '<a href="../directory.html">Counts for all counties</a>'] if x)
            tbl = table_wrap(
                f'<table data-nosort><caption>{esc(c)} County owners with an active tier A-C site row, '
                f'rows {(n - 1) * DIRECTORY_PAGE + 1} to {(n - 1) * DIRECTORY_PAGE + len(part)} of {len(crows)}</caption><thead><tr>'
                '<th scope="col">Owner</th><th scope="col">Street address</th><th scope="col">Ring</th><th scope="col">Site tier</th>'
                f'<th scope="col">Process</th><th scope="col">Employees</th></tr></thead><tbody>{trs}</tbody></table>', f"{c} County owners")
            body = (f'<h1>{esc(c)} County: Northeast Ohio polymer companies</h1>\n'
                    f'<p class="lede">{plural(len(crows), 'owner')} with an active tier A-C site row in {esc(c)} County; page {n} of {pages}. '
                    f'This plain page needs no JavaScript; <a href="../directory.html">the directory</a> adds search and filters.</p>\n'
                    f'<p>{nav}</p>\n{tbl}\n<p>{nav}</p>')
            out[name] = page(ctx, f"Northeast Ohio polymer companies: {c} County", body, "../", "directory",
                             f"Polymer companies in {c} County, Ohio, with street addresses, {DIRECTORY_PAGE} a page.")
    return out


# prospects.html is kept so links shared before the rename work. It sends the reader to the directory with the query string
# (saved filters) and hash intact; without JavaScript the refresh tag does the plain redirect.
PROSPECTS_REDIRECT_JS = "location.replace('directory.html' + location.search + location.hash);\n"


def build_prospects_stub(ctx):
    return page(ctx, "This page has moved",
                '<h1>This page has moved</h1>\n<p class="lede">The list is now <a href="directory.html">Northeast Ohio polymer companies</a>.</p>',
                "", "", "", '<noscript><meta http-equiv="refresh" content="0; url=directory.html"></noscript>\n<script src="prospects.js"></script>')


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
        card(len(active_ab(pic)), "PIC-18 county site rows", "Ohio county in the 18 PIC counties (NEO-SMART region); operating status active; tiers A-C"),
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
        "<table data-nosort><caption>Verification tiers</caption><thead><tr><th scope=\"col\">Tier</th>"
        "<th scope=\"col\">Meaning</th><th scope=\"col\">Typical sources</th></tr></thead>"
        f"<tbody>{tier_rows}</tbody></table>", "Verification tiers")
    def xcard(href, glyph, title, text):
        return (f'<a class="xcard" href="{href}">{GLYPHS[glyph]}<h3>{esc(title)}</h3><p>{esc(text)}</p>'
                f'<span class="go">Open &rarr;</span></a>')

    explore = "".join([
        xcard("directory.html", "directory", "Northeast Ohio polymer companies",
              "Companies in the 18 PIC counties: counts by county and ring, then search, filter by process, size and more, and download the list with street addresses."),
        xcard("map.html", "geo", "Street map",
              "Every mapped site on a street map, filtered by ring, tier and state."),
        xcard("graph/index.html", "graph", "Industry graph",
              "Companies, institutions and the processes and materials that connect them. Hover to trace a supply web."),
        xcard("graph/map.html", "geo", "Map + network",
              "Every mapped site, with company networks drawn across the map. Then morph geography into structure."),
        xcard("graph/events.html", "shows", "Trade shows in 3D",
              "Which companies exhibit where, as a 3D network with a presentation mode for the big screen."),
        xcard("experts.html", "experts", "Programs & researchers",
              "Find who teaches and researches polymers: search faculty, lab scientists and programs by specialty."),
        xcard("counties/index.html", "counties", "PIC-18 county pages",
              "One page per Northeast Ohio county: establishments by ring, programs, and the official benchmark."),
    ])
    body = f"""
<section class="hero-static" aria-labelledby="hero-title">
<div class="wrap">
<div class="eyebrow">Open data · Polymer Industry Cluster</div>
<h1 id="hero-title">The polymer industry, <em>mapped.</em></h1>
<p class="lede">Plants, processors, materials makers, OEMs and the schools and groups behind them,
every fact tied to a public source. Built in Akron for Northeast Ohio, growing nationally.</p>
<div class="hero-stats">
<div><b>{fmt_int(len(active_ab(sites)))}</b><small>active site rows (tiers A–C)<br>across all states</small></div>
<div><b>{fmt_int(len(active_ab(oh)))}</b><small>in Ohio</small></div>
<div><b>{fmt_int(len(active_ab(pic)))}</b><small>in the 18 PIC counties</small></div>
</div>
<div class="cta"><a class="btn primary" href="directory.html">Find companies</a><a class="btn" href="map.html">Map</a>
<a class="btn" href="counties/index.html">Counties</a></div>
<p class="hero-links"><a href="search.html">Search every organization, any state</a> · <a href="skyline.html">View the 3D skyline</a></p>
</div>
</section>

<h2 id="explore">Explore</h2>
<div class="explore">{explore}</div>

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

<h2 id="method">How the Atlas works</h2>
<details class="more"><summary>Verification tiers</summary>
{tier_tbl}
<p class="small muted">A record's tier is the tier of its weakest must-have field.</p>
</details>
<details class="more"><summary>About the data</summary>
<ul>
<li>Canonical data is CSV in the <a href="{esc(ctx.repo_url)}" rel="noopener">project repository</a>.
This site is generated from it and carries no data of its own.</li>
<li>Every record carries at least one source, a verification tier and the date it was last verified.
NAICS codes are shown with their provenance because companies rarely publish a corporate 6-digit NAICS.</li>
<li>Licensed sources (trade-press rankings, commercial databases) are discovery leads only and are never
republished; every fact is cited to a primary or public source.</li>
<li>Coordinates on the maps are reference data (interpolated from addresses, not rooftop) and are never evidence.</li>
<li>No personal contact data is published. University and federal-laboratory researchers appear only with
publicly stated name, role, research specialty and public profile URL, on their institution's page.
To request a correction or removal, open an issue in the repository.</li>
</ul>
</details>
<details class="more"><summary>License and attribution</summary>
<p>Original database content compiled here is licensed
<a href="https://creativecommons.org/licenses/by/4.0/" rel="noopener">CC BY 4.0</a>; scripts are MIT.
Please attribute "Polymer Industry Atlas, Polymer Industry Cluster (PIC), Greater Akron Chamber".</p>
</details>
"""
    return page(ctx, "Home", body, "", "index")


def build_skyline_page(ctx):
    """The 3D skyline (three.js), one click from the home page on its own page: the only page that loads three.js."""
    a = ctx.atlas
    sites = a.sites
    oh = [s for s in sites if s.get("state") == "OH"]
    pic = [s for s in oh if s.get("county") in PIC12]
    sky = skyline.payload(active_ab(sites), lambda x: x["_ring"] or "?", set(PIC12))
    ctx.skyline = sky
    top = "".join(f"<li>{plural(h[2], 'site row')}: {esc(h[5])}</li>" for h in sky["hex"][:10])
    body = f"""
<section class="hero" aria-labelledby="hero-title">
<div class="hero-stage">
<div id="skyline" data-src="skyline.json" role="img"
 aria-label="3D map of the United States with hexagonal columns whose height shows how many polymer industry site rows the Atlas holds in each area; the tallest stand in Northeast Ohio."></div>
<div id="sky-tip" hidden></div>
<div class="hero-copy">
<div class="eyebrow">3D skyline</div>
<h1 id="hero-title">Where the site rows <em>stand.</em></h1>
<p class="lede">Hexagonal columns over the United States: the taller the column, the more active site rows the Atlas holds there.</p>
<div class="hero-stats">
<div><b>{fmt_int(len(active_ab(sites)))}</b><small>active site rows (tiers A–C)<br>across all states</small></div>
<div><b>{fmt_int(len(active_ab(pic)))}</b><small>in the 18 PIC counties</small></div>
</div>
<div class="cta"><a class="btn primary" href="directory.html">Find companies</a><a class="btn" href="map.html">Map</a></div>
</div>
<div class="hero-legend"><span>Fewer sites</span><span class="ramp"></span><span>More</span><span>· hex ≈ 30 mi</span></div>
<div class="hero-tools"><span class="hero-hint">Drag to rotate</span>
<button class="btn" type="button" data-sky-focus="us" aria-pressed="true">United States</button>
<button class="btn" type="button" data-sky-focus="ohio" aria-pressed="false">Northeast Ohio</button></div>
</div>
</section>
<div class="sr-only"><p>Largest clusters of site rows on the 3D map:</p><ol>{top}</ol></div>
<p class="small muted">The 3D map shows {fmt_int(sky["n"])} active, tier A-C site rows with reference coordinates in the lower 48
states, binned into hexagons; column height follows the count. Lime outlines mark the PIC-18 counties.
Positions are interpolated from addresses and are never evidence.</p>
"""
    return page(ctx, "3D skyline", body, "", "sky",
                scripts=f'<script src="{THREE_JS}" defer></script>\n<script src="skyline.js" defer></script>')


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
<fieldset><legend>Area</legend>
<label><input type="checkbox" id="f-pic18" checked data-counties="{esc(",".join(PIC12))}"> Only the 18 PIC counties (Ohio)</label></fieldset>
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
<a href="counties/index.html">county page</a> (PIC-18) or its organization page, reachable via
<a href="search.html">search</a>. Map tiles &copy; OpenStreetMap contributors.</p>
"""
    head = '<link rel="stylesheet" href="vendor/leaflet/leaflet.css">'
    scripts = ('<script src="vendor/leaflet/leaflet.js"></script>\n'
               '<script src="map.js"></script>')
    return page(ctx, "Street map", body, "", "map", "Street map of polymer industry sites by ring.", head, scripts)


def sites_json(ctx):
    """Compact site data for the map (only rows with coordinates)."""
    a = ctx.atlas
    cols = ["id", "lat", "lon", "name", "org", "city", "st", "ring", "inh", "tier", "status", "co"]
    rows, orgs = [], {}
    for s in a.sites:
        try:
            lat, lon = float(s["latitude"]), float(s["longitude"])
        except (TypeError, ValueError, KeyError):
            continue
        rows.append([s["site_id"], round(lat, 5), round(lon, 5), s.get("site_name") or "",
                     s["org_id"], s.get("city") or "", s.get("state") or "",
                     s["_ring"] or "", 1 if s["_ring_inherited"] else 0,
                     s.get("verification_tier") or "", s.get("operating_status") or "", s.get("county") or ""])
        orgs[s["org_id"]] = a.name_of(s["org_id"]) or ""
    return {"cols": cols, "orgs": orgs, "rows": rows}


def vals(value):
    """';'-separated multi-value field -> list of stripped values."""
    return [v.strip() for v in str(value or "").split(";") if v.strip()]


def org_field_sources(org, sites, field):
    """Map each recorded token to its supplying rows. None denotes the company row."""
    sources = {token: [None] for token in vals(org.get(field))}
    for site in sites:
        if (site.get("operating_status") or "").strip() == "closed":
            continue
        for token in dict.fromkeys(vals(site.get(field))):
            sources.setdefault(token, []).append(site)
    return sources


SPEC_LABELS = {  # controlled-vocabulary tokens whose plain underscore->space form reads badly
    "polyethylene_pe": "polyethylene (PE)", "polypropylene_pp": "polypropylene (PP)",
    "polyurethane_pu": "polyurethane (PU)", "pet_petg": "PET / PETG", "sbr": "SBR",
    "composites_frp": "composites (FRP)", "composites_rtm_infusion": "composites (RTM, infusion)",
    "thermoplastic_elastomers_tpe_tpu": "thermoplastic elastomers (TPE/TPU)",
    "elastomers_rubber": "elastomers & rubber", "adhesives_sealants": "adhesives & sealants",
    "bioplastics_biobased": "bioplastics & bio-based", "recycling_circularity": "recycling & circularity",
    "membranes_separations": "membranes & separations", "films_flexible_packaging": "films & flexible packaging",
    "degradation_biodegradation": "degradation & biodegradation", "extrusion_film_blown": "blown film extrusion",
    "extrusion_film_cast": "cast film extrusion", "thermoforming_vacuum": "thermoforming (vacuum)",
    "compounding_extrusion": "compounding & extrusion", "printing_decorating_plastics": "printing & decorating plastics",
    "mold_tool_making": "mold & tool making", "rubber_mixing_compounding": "rubber mixing & compounding",
    "rubber_molding_injection": "rubber molding (injection)", "additive_manufacturing_polymer": "additive manufacturing (polymer)",
    "additive_manufacturing_metal": "additive manufacturing (metal)", "additive_manufacturing_science": "additive manufacturing science",
    "composites_hand_layup": "composites (hand layup)", "composites_carbon": "composites (carbon)",
}
SPEC_DROP = {"other_specified_in_notes"}


def norm_specialty(v):
    """Display form of a research specialty. Vocabulary tokens get readable labels; free text keeps its
    wording and acronyms (only a sentence-case capital is lowered). '' for placeholder values."""
    v = (v or "").strip().strip(".;,").strip()
    if not v or v.lower() in SPEC_DROP:
        return ""
    if v.lower() in SPEC_LABELS:
        return SPEC_LABELS[v.lower()]
    if re.fullmatch(r"[a-z0-9_]+", v):
        return v.replace("_", " ")
    v = re.sub(r"\s+", " ", v)
    if re.match(r"[A-Z][a-z]", v) and not re.match(r"[A-Z][a-z]+[A-Z]", v):  # 'Polymer physics' -> 'polymer physics', keep 'BioMEMS'
        v = v[0].lower() + v[1:]
    return v


def specs_of(values):
    out, seen = [], set()
    for x in values:
        d = norm_specialty(x)
        if d and d.lower() not in seen:
            seen.add(d.lower()); out.append(d)
    return sorted(out, key=str.lower)


CRED_LABELS = {"bs": "BS", "ms": "MS", "phd": "PhD", "aas_associate": "AAS", "certificate": "certificate",
               "registered_apprenticeship": "registered apprenticeship"}


LAB_TYPES = {"government_lab_agency", "nonprofit_rd_consortium"}


def experts_json(ctx):
    """Researchers + programs for experts.html. Public professional facts only, exactly as institution pages show them."""
    a = ctx.atlas
    insts, people, programs = {}, [], []

    def inst(oid):
        if oid not in insts:
            e = a.eco.get(oid) or a.orgs.get(oid) or {}
            sub = e.get("ecosystem_subtype") or ""
            insts[oid] = [e.get("legal_name") or oid, e.get("city") or "", e.get("state") or "",
                          "lab" if sub in LAB_TYPES else ("edu" if sub.startswith(("university", "k12", "workforce")) else "other")]
        return oid

    for p in a.people:
        href = safe_href(p.get("public_profile_url")) or ""
        if "@" in href:
            href = ""
        specs = specs_of(vals(p.get("research_specialties")))
        role = p.get("role_as_published") or str(p.get("role") or "").replace("_", " ")
        modes = sorted({str(g.get("mode") or "").replace("_", " ") for g in a.engagement_by_person.get(p.get("person_id"), [])} - {""})
        people.append([p.get("full_name") or "", role, specs, inst(p.get("institution_org_id")), href, modes])
    for g in a.programs:
        if g.get("status") not in ("active", "", None):
            continue
        href = safe_href(g.get("url") or g.get("public_door_url")) or ""
        specs = specs_of(x for f in ("specialty_processes", "specialty_materials", "research_areas") for x in vals(g.get(f)))
        creds = ", ".join(CRED_LABELS.get(c, c.replace("_", " ")) for c in vals(g.get("credential_types")))
        level = "" if creds or g.get("level") == "none" else ", ".join(vals(g.get("level"))).replace("_", " ")
        ptype = str(g.get("program_type") or "").replace("_", " ")
        if creds == ptype:  # 'certificate · certificate'
            creds = ""
        programs.append([g.get("program_name") or "", inst(g.get("institution_org_id")), ptype, level, creds, specs, href])
    return {"insts": insts, "people": people, "programs": programs}


def build_experts_page(ctx, n_people, n_programs):
    body = f"""
<p class="eyebrow-ink">Programs &amp; researchers</p>
<h1>Who teaches and researches polymers</h1>
<p class="lede">Search {fmt_int(n_people)} researcher records (university faculty and federal-laboratory
research staff) and {fmt_int(n_programs)} active program records by name, research specialty, institution or state.
Try a specialty such as <a href="?q=rheology">rheology</a>, <a href="?q=elastomers">elastomers</a> or
<a href="?q=biomedical+polymers">biomedical polymers</a>.</p>
<form onsubmit="return false" role="search" class="xfinder">
<p class="xq"><label for="q"><strong>Name, specialty or institution</strong></label>
<input type="search" id="q" autocomplete="off" placeholder="e.g. rheology Ohio"></p>
<div class="filters">
<p><label for="state">State</label><br><select id="state"><option value="">Any state</option></select></p>
<p><label for="kind">Institution type</label><br><select id="kind"><option value="">Any</option>
<option value="edu">Universities, colleges and training</option><option value="lab">Federal labs and research consortia</option></select></p>
<p><label for="show">Show</label><br><select id="show"><option value="both">Researchers and programs</option>
<option value="people">Researchers only</option><option value="programs">Programs only</option></select></p>
<p><label for="sort">Sort results</label><br><select id="sort"><option value="inst">By institution, most matches first</option>
<option value="instaz">By institution, A to Z</option><option value="name">By name, A to Z (one list)</option></select></p>
</div>
</form>
<div class="xchips" id="chips" aria-label="Common research specialties"></div>
<p id="count" role="status" aria-live="polite">Loading...</p>
<div id="empty" class="xempty" hidden><strong>Nothing matches.</strong> Try fewer words or a broader specialty,
or <button type="button" class="xchip" id="clear">clear the search and filters</button></div>
<nav class="xtabs" aria-label="View" id="tabs"><button type="button" data-view="browse" aria-pressed="true">Browse by institution</button><button type="button" data-view="results" aria-pressed="false">Results list</button></nav>
<section id="browse" aria-labelledby="browse-h"><h2 id="browse-h" class="sr-only">Institutions</h2><div id="insts"></div></section>
<section id="ppl" aria-labelledby="ppl-h" hidden><h2 id="ppl-h">Researchers</h2><div id="people"></div></section>
<section id="prg" aria-labelledby="prg-h" hidden><h2 id="prg-h">Programs</h2><div id="programs"></div></section>
<p class="small muted">Researchers appear with their publicly stated name, role, research specialties and
public profile page, from their institution's own pages; no contact details are published. Specialties are
shown as the institution words them, lightly normalized for search. To request a correction or removal,
<a href="{esc(ctx.repo_url)}/issues" rel="noopener">open an issue</a>.</p>
<noscript><p>The finder needs JavaScript. Every researcher and program is also listed on its institution's page.</p></noscript>
"""
    return page(ctx, "Programs & researchers", body, "", "experts",
                "Find polymer programs and researchers by specialty, institution or state.", "",
                '<script src="experts.js"></script>')


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


EVIDENCE_CLASS = {"own_site": "Company's own site", "government_filing": "Government filing", "registry": "Registry record",
                  "directory": "Directory listing", "press": "News or trade press",
                  "platform_category": "Platform category (a lead, not proof)", "harvest_roster": "Roster list (a lead, not proof)"}
EVIDENCE_CLAIM = {"existence": "Exists", "activity": "Does the work", "scope": "Polymer scope", "address": "Address",
                  "parent": "Parent link", "liveness": "Operating", "code": "Code", "size_band": "Size band"}


def evidence_strength(effect):
    if effect == "contradicts":
        return "Contradicts the record"
    t = str(effect or "").replace("supports_", "")
    return f"Supports tier {t} ({TIERS[t][0].lower()})" if t in TIERS else str(effect or "")


def evidence_table(rows, caption, nocsv=False):
    """Claim type, source class, strength, date and source links for each evidence row. Never the claim text, lane id or notes."""
    order = list(EVIDENCE_CLAIM)
    rows = sorted(sorted(rows, key=lambda r: r.get("observed_date") or "", reverse=True),
                  key=lambda r: order.index(r["claim_type"]) if r.get("claim_type") in order else len(order))
    body = "".join(
        f'<tr><td>{esc(EVIDENCE_CLAIM.get(r.get("claim_type"), r.get("claim_type")))}</td>'
        f'<td>{esc(EVIDENCE_CLASS.get(r.get("source_class"), r.get("source_class")))}</td>'
        f'<td>{esc(evidence_strength(r.get("tier_effect")))}</td><td>{esc(r.get("observed_date"))}</td>'
        f'<td>{url_links(source_urls(r.get("source_ref"))) or "&mdash;"}</td></tr>' for r in rows)
    return table_wrap(
        f'<table{" data-nocsv" if nocsv else ""}><caption>{esc(caption)}</caption><thead><tr><th scope="col">Claim</th>'
        '<th scope="col">Source class</th><th scope="col">Strength</th><th scope="col">Observed</th><th scope="col">Source</th>'
        f'</tr></thead><tbody>{body}</tbody></table>', caption)


def evidence_section(a, table, rec, kind):
    """The record's evidence rows; records with none yet fall back to the source links on the record."""
    shown = evidence_view(a, table, rec["org_id"])
    if not shown:
        return (f'<h2 id="evidence">Sources</h2><p class="small muted">No claim-level evidence rows are recorded for this {kind} yet; '
                f'the source links on the record are shown. Last verified {esc(rec.get("last_verified")) or "n/a"}; '
                f'tier {esc(rec.get("verification_tier")) or "n/a"}.</p>{source_list(rec.get("sources"))}')
    n_sites = sum(len(evidence_view(a, "sites", x["site_id"])) for x in a.sites_by_org.get(rec["org_id"], []))
    more = f"; {plural(n_sites, 'more row')} listed with its sites above" if n_sites else ""
    return (f'<h2 id="evidence">Evidence ({plural(len(shown), 'row')} for this {kind}{more})</h2>'
            '<p class="small muted">Each row is one observation: the claim, the class of source, how strongly it supports the '
            "record's tier, when it was observed, and where. The wording of each claim stays in the repository's data; "
            "follow the source link to check it. Rows from a platform category or a roster list are leads, "
            f'never proof of scope. Last verified {esc(rec.get("last_verified")) or "n/a"}; '
            f'tier {esc(rec.get("verification_tier")) or "n/a"}.</p>'
            f'{evidence_table(shown, "Evidence for " + str(rec.get("legal_name") or rec["org_id"]))}')


def member_field(rec):
    if rec.get("pic_member") != "true":
        return ""   # the flag is the public member list only: never say an organization is not on it
    href = safe_href(rec.get("membership_source_url"))
    return f'<a href="{esc(href)}" rel="noopener nofollow">{MEMBER_YES}</a>' if href else esc(MEMBER_YES)


def site_evidence(a, s):
    shown = evidence_view(a, "sites", s["site_id"])
    if not shown:
        return f'<details class="srcs"><summary>Sources for this site</summary>{source_list(s.get("sources"))}</details>'
    return (f'<details class="srcs"><summary>Evidence for this site ({plural(len(shown), 'row')})</summary>'
            f'{evidence_table(shown, "Evidence for " + str(s.get("site_name") or s["site_id"]), nocsv=True)}</details>')


def site_article(s, a, open_=False):
    """One site as a collapsible row: a one-line summary (place, type, ring, status, tier) that opens to the full record."""
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
    place = ", ".join(x for x in [s.get("city"), s.get("state")] if nonempty(x))
    meta = " · ".join(x for x in [esc(place), esc(vocab(s.get("site_type")))] if x)
    badges = " ".join(x for x in [ring_badge(s["_ring"], s["_ring_inherited"]) if s["_ring"] else "",
                                  status_badge(s.get("operating_status")), tier_badge(s.get("verification_tier"))] if x)
    return (f'<details class="site" id="{esc(safe_id(s["site_id"]))}"{" open" if open_ else ""}>'
            f'<summary><span class="s-name">{esc(s.get("site_name") or s["site_id"])}</span>'
            f'<span class="s-meta">{meta}</span><span class="s-badges">{badges}</span></summary>'
            f'<div class="s-body"><p class="muted small">{esc(s["site_id"])}</p>{fields}'
            f'{site_evidence(a, s)}</div></details>')


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
    return (f"<h2>Researchers ({plural(len(people), 'public profile row')})</h2>"
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


def org_field_html(org, sites, field):
    if not sites:
        return esc(vocab(org.get(field)))
    items = []
    for token, sources in org_field_sources(org, sites, field).items():
        origins = []
        for site in sources:
            if site is None:
                origins.append("Company row")
                continue
            tier = site.get("verification_tier")
            detail = f" · {TIERS[tier][0].lower()}" if tier in ("C", "U") else ""
            origins.append(f'{esc(site.get("site_name") or site["site_id"])} {tier_badge(tier)}{detail}')
        items.append(f'<div>{esc(vocab(token))} <span class="muted small">({" / ".join(origins)})</span></div>')
    return "".join(items)


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
    rings = ring_badge(o.get("ring_primary")) if nonempty(o.get("ring_primary")) else ""
    if nonempty(o.get("ring_secondary")):
        rings += f' <span class="muted">secondary:</span> {ring_badge(o["ring_secondary"])}'
    site_rows = sorted(a.sites_by_org.get(oid, []), key=lambda s: (s.get("state") or "", s.get("city") or "", s["site_id"]))
    n_active = sum(1 for s in site_rows if s.get("operating_status") == "active")
    sites_html = ""
    if site_rows:
        sites_html = (f"<h2>Sites ({plural(len(site_rows), 'site row')}; {fmt_int(n_active)} with operating status active)</h2>"
                      "<p class=\"small muted\">Site rows are physical establishments (plants, headquarters, "
                      "labs, warehouses). Each is owned by the operator."
                      + (" An asterisk (*) next to a ring means the site row records no ring, so the parent organization's ring is shown."
                         if any(s["_ring_inherited"] for s in site_rows) else "") + "</p>"
                      + "".join(site_article(s, a, len(site_rows) <= 3) for s in site_rows))
    fields = dl([
        ("Record ID", esc(oid)), ("Status", status_badge(o.get("status"))),
        ("Status date", esc(o.get("status_date"))), ("Ring", rings),
        ("Entity type", esc(vocab(o.get("entity_type")))),
        ("Headquarters", esc(hq)), ("Website", ext_link(o.get("website"))),
        ("Parent organization", parent), ("Ultimate parent (as named)", ult),
        ("Year founded", esc(o.get("year_founded"))), ("Stock ticker", esc(o.get("stock_ticker"))),
        ("Ownership", esc(vocab(o.get("ownership_type")))),
        ("Primary NAICS", naics), ("Processes", org_field_html(o, site_rows, "processes")),
        ("Materials", org_field_html(o, site_rows, "materials")),
        ("Markets served", org_field_html(o, site_rows, "markets_served")),
        ("Certifications", esc(vocab(o.get("certifications")))),
        ("Ohio employee band", esc(o.get("employee_band_ohio"))),
        ("Public member list", member_field(o)),
        ("Verification tier", tier_badge(o.get("verification_tier"))),
        ("Last verified", esc(o.get("last_verified"))),
    ])
    body = f"""
<p class="small"><a href="../search.html">Search</a> &rsaquo; Organization</p>
<h1>{esc(o.get("legal_name"))}</h1>
{('<p class="muted">Also known as: ' + esc(vocab(o.get("trade_names"))) + '</p>') if nonempty(o.get("trade_names")) else ''}
{tombstone_banner(o, successor, a, "organization record")}
{lede(o.get("description_1line"))}
{explore_links(o["org_id"], o.get("status"), any(nonempty(x.get("latitude")) for x in a.sites if x.get("org_id") == o["org_id"]))}
{fields}
{('<h2>Subsidiary and child organizations</h2>' + kids_html) if kids_html else ''}
{equipment_block(a.equipment_by_host.get(o["org_id"], []))}
{sites_html}
{evidence_section(a, "organizations", o, "organization")}
"""
    return page(ctx, o.get("legal_name") or oid, body, "../", "",
                f"{o.get('legal_name') or oid}: Polymer Industry Atlas record.")


def explore_links(oid, status, on_map):
    """'See in graph / on the map' deep links (graph/index.html#ID, graph/map.html#ID); tombstones are not graph nodes."""
    if status in ("merged", "acquired", "closed"):
        return ""
    links = [f'<a class="pill" href="../graph/index.html#{esc(oid)}">See in the industry graph</a>']
    if on_map:
        links.append(f'<a class="pill" href="../graph/map.html#{esc(oid)}">See its sites on the map</a>')
    return '<p class="explore-links">' + " ".join(links) + "</p>"


def equipment_block(rows):
    """[v1.9] Instruments and pilot lines the host lists on its own pages (SCHEMA 4.19)."""
    if not rows:
        return ""
    body = "".join(
        f'<tr><th scope="row">{esc(r.get("name"))}</th><td>{esc(str(r.get("equipment_class") or "").replace("_", " "))}</td>'
        f'<td>{esc(str(r.get("access_mode") or "").replace("_", " "))}</td>'
        + (f'<td><a href="{esc(safe_href(r.get("source_ref")))}" rel="noopener nofollow">host page</a></td></tr>' if safe_href(r.get("source_ref")) else '<td></td></tr>')
        for r in sorted(rows, key=lambda r: (r.get("equipment_class") or "", (r.get("name") or "").lower())))
    return (f"<h2>Equipment and testing ({plural(len(rows), 'equipment row')})</h2>"
            '<p class="small muted">Instruments and pilot lines this organization lists on its own pages. Ask the host about access.</p>'
            + table_wrap('<table><thead><tr><th scope="col">Equipment</th><th scope="col">Class</th><th scope="col">Access</th>'
                         f'<th scope="col">Source</th></tr></thead><tbody>{body}</tbody></table>', "Equipment"))


def build_eco_page(ctx, e):
    a = ctx.atlas
    eid = e["org_id"]
    successor = a.merged_into.get(eid)
    loc = ", ".join(x for x in [e.get("city"), e.get("state")] if nonempty(x))
    county = f"{e['county']} County" if nonempty(e.get("county")) else ""
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
        ("Public member list", member_field(e)),
        ("Verification tier", tier_badge(e.get("verification_tier"))),
        ("Last verified", esc(e.get("last_verified"))),
    ])
    progs = a.programs_by_inst.get(eid, [])
    progs_html = (f"<h2>Programs ({plural(len(progs), 'program row')})</h2>" + program_table(progs, a)) if progs else ""
    site_rows = sorted(a.sites_by_org.get(eid, []), key=lambda s: (s.get("state") or "", s.get("city") or ""))
    sites_html = ""
    if site_rows:
        sites_html = (f"<h2>Locations ({plural(len(site_rows), 'site row')})</h2>"
                      + "".join(site_article(s, a, len(site_rows) <= 3) for s in site_rows))
    body = f"""
<p class="small"><a href="../search.html">Search</a> &rsaquo; Ecosystem organization</p>
<h1>{esc(e.get("legal_name"))}</h1>
{explore_links(e["org_id"], e.get("status"), False)}
{tombstone_banner(e, successor, a, "ecosystem record")}
{lede(e.get("description_1line"))}
{fields}
{progs_html}
{people_block(a.people_by_inst.get(eid, []), ctx)}
{equipment_block(a.equipment_by_host.get(eid, []))}
{sites_html}
{evidence_section(a, "ecosystem", e, "ecosystem record")}
"""
    return page(ctx, e.get("legal_name") or eid, body, "../", "",
                f"{e.get('legal_name') or eid}: Polymer Industry Atlas ecosystem record.")


def process_table(sites, county):
    """Site rows by recorded process (a site row can list several, so rows do not sum to the total)."""
    counts, n_unknown = Counter(), 0
    for s in sites:
        t = known(vals(s.get("processes")))
        counts.update(t)
        n_unknown += not t
    rows = "".join(f'<tr><th scope="row">{esc(vocab(t))}</th><td class="num">{fmt_int(n)}</td></tr>'
                   for t, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
    rows += (f'<tr><th scope="row">Unknown (no process recorded on the site row)</th><td class="num" data-sort="{n_unknown}">'
             f'{fmt_int(n_unknown)}</td></tr>'
             f'<tr class="total"><th scope="row">All site rows (each can list several processes)</th>'
             f'<td class="num">{fmt_int(len(sites))}</td></tr>')
    return table_wrap(
        f'<table><caption>{esc(county)} County site rows by process (Ohio; operating status active; tiers A-C)</caption>'
        f'<thead><tr><th scope="col">Process</th><th scope="col" class="num">Site rows</th></tr></thead><tbody>{rows}</tbody></table>',
        f"{county} County site rows by process")


def band_table(sites, a, county):
    """Site rows by employee band: the site's own band, else the parent organization's Ohio band, in separate columns."""
    own, parent, n_unknown = Counter(), Counter(), 0
    for s in sites:
        b = s.get("employee_band_site") or ""
        rec = a.orgs.get(s["org_id"]) or a.eco.get(s["org_id"]) or {}
        pb = rec.get("employee_band_ohio") or ""
        if b not in UNKNOWN_VALUES:
            own[b] += 1
        elif pb not in UNKNOWN_VALUES:
            parent[pb] += 1
        else:
            n_unknown += 1
    rows = "".join(
        f'<tr><th scope="row">{esc(b)}</th><td class="num">{fmt_int(own[b])}</td><td class="num">{fmt_int(parent[b])}</td>'
        f'<td class="num">{fmt_int(own[b] + parent[b])}</td></tr>'
        for b in sorted(set(own) | set(parent), key=lambda b: (band_floor(b) or 0, b)))
    rows += (f'<tr><th scope="row">Unknown (no site band and no parent band)</th><td class="num"></td><td class="num"></td>'
             f'<td class="num" data-sort="{n_unknown}">{fmt_int(n_unknown)}</td></tr>'
             f'<tr class="total"><th scope="row">All site rows</th><td class="num">{fmt_int(sum(own.values()))}</td>'
             f'<td class="num">{fmt_int(sum(parent.values()))}</td><td class="num">{fmt_int(len(sites))}</td></tr>')
    return table_wrap(
        f'<table><caption>{esc(county)} County site rows by employee band (Ohio; operating status active; tiers A-C)</caption>'
        '<thead><tr><th scope="col">Employee band</th><th scope="col" class="num">Site rows with this site band</th>'
        '<th scope="col" class="num">No site band; parent\'s Ohio band</th><th scope="col" class="num">Site rows</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>', f"{county} County site rows by employee band")


def build_county_page(ctx, county):
    a = ctx.atlas
    sites = [s for s in a.sites if s.get("state") == "OH" and s.get("county") == county]
    active = [s for s in sites if s.get("operating_status") == "active"]
    not_active = len(sites) - len(active)
    ac = active_ab(sites)   # the tier A-C basis of the headline counts
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
{("a PIC-18 county (" + JOBSOHIO_REGION[county] + " region)") if county in PIC12 else "outside the PIC-18 counties"}. {esc(SOURCE_CLASS_NOTE)}</p>
<div class="cards">
<div class="card"><div class="big">{fmt_int(len(active))}</div><div class="unit">Site rows</div><div class="filter">{esc(county)} County, Ohio; operating status active; all verification tiers</div></div>
<div class="card"><div class="big">{fmt_int(len(ac))}</div><div class="unit">Site rows, tiers A-C</div><div class="filter">{esc(county)} County, Ohio; operating status active; verification tiers A-C (the basis of the headline counts)</div></div>
<div class="card"><div class="big">{fmt_int(len(org_ids))}</div><div class="unit">Organization rows with an active site row here</div><div class="filter">distinct parent organizations of those site rows; all tiers</div></div>
<div class="card"><div class="big">{fmt_int(len(eco))}</div><div class="unit">Ecosystem organization rows</div><div class="filter">located in the county; all statuses and tiers</div></div>
<div class="card"><div class="big">{fmt_int(len(progs))}</div><div class="unit">Program rows</div><div class="filter">located in the county; status active; all tiers</div></div>
</div>
{f'<p class="small muted">{plural(not_active, 'further site row')} in this county {'has' if not_active == 1 else 'have'} another operating status (closed, idled, unknown, pre-revenue) and are not listed or counted.</p>' if not_active else ''}
<h2>Establishments by ring</h2>
{ring_tbl}
<p class="small muted">An asterisk (*) marks a ring inherited from the parent organization because the site row records none.
Tier U rows are candidates; they are included here because this page shows all tiers.</p>
<h2>Establishments by NAICS (3-digit)</h2>
{naics_tbl}
<p class="small muted">The site's own NAICS code is used. NAICS values are not company facts by default; see each site's provenance on its organization page.</p>
<h2>Establishments by process</h2>
{process_table(ac, county) if ac else "<p>No active tier A-C site rows.</p>"}
<p class="small muted">Process is what the site row records. Unknown means none is recorded, not that there is none.</p>
<h2>Establishments by employee band</h2>
{band_table(ac, a, county) if ac else "<p>No active tier A-C site rows.</p>"}
<p class="small muted">Bands, not headcounts. Where a site row records no band, the parent organization's Ohio band is counted in its own column.</p>
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


def ohio_counties(a):
    """PIC-18 plus every Ohio county where the Atlas holds a site or ecosystem row: each gets a one-pager."""
    names = set(PIC12)
    names |= {s["county"] for s in a.sites if s.get("state") == "OH" and nonempty(s.get("county"))}
    names |= {e["county"] for e in a.eco.values() if e.get("state") == "OH" and nonempty(e.get("county"))}
    return sorted(names)


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
        n_ac = len(active_ab(sites))
        label = f'<a href="{esc(slug(c))}.html">{esc(c)}</a>'
        q = ctx.qcew.get(c)
        qn = fmt_int(int(float(q["annual_avg_estabs"]))) if q and nonempty(q.get("annual_avg_estabs")) else "n/a"
        return (f'<tr><th scope="row">{label}</th><td>{("PIC-18 · " + JOBSOHIO_REGION[c]) if c in PIC12 else ""}</td>'
                f'<td class="num"><strong>{fmt_int(n_ac)}</strong></td><td class="num">{fmt_int(n_act)}</td><td class="num">{fmt_int(len(sites))}</td>'
                f'<td class="num">{fmt_int(eco_n.get(c, 0))}</td><td class="num">{fmt_int(prog_n.get(c, 0))}</td>'
                f'<td class="num">{qn}</td></tr>')
    pic_rows = "".join(row(c) for c in PIC12)
    tot = lambda f: sum(f(all_sites.get(c, [])) for c in PIC12)   # noqa: E731
    pic_ac = tot(lambda ss: len(active_ab(ss)))
    pic_rows += (f'<tr class="total"><th scope="row">PIC-18 total</th><td></td>'
                 f'<td class="num"><strong>{fmt_int(pic_ac)}</strong></td>'
                 f'<td class="num">{fmt_int(tot(lambda ss: sum(1 for s in ss if s.get("operating_status") == "active")))}</td>'
                 f'<td class="num">{fmt_int(tot(len))}</td><td class="num">{fmt_int(sum(eco_n.get(c, 0) for c in PIC12))}</td>'
                 f'<td class="num">{fmt_int(sum(prog_n.get(c, 0) for c in PIC12))}</td><td></td></tr>')
    other_rows = "".join(row(c) for c in names if c not in PIC12)
    head = ("<thead><tr><th scope=\"col\">County</th><th scope=\"col\">Group</th>"
            "<th scope=\"col\" class=\"num\">Site rows, active, tiers A-C (headline basis)</th>"
            "<th scope=\"col\" class=\"num\">Site rows, active, all tiers</th>"
            "<th scope=\"col\" class=\"num\">Site rows, all statuses</th>"
            "<th scope=\"col\" class=\"num\">Ecosystem organization rows</th>"
            "<th scope=\"col\" class=\"num\">Program rows, active</th>"
            "<th scope=\"col\" class=\"num\">QCEW 2023 private NAICS 326 establishments (benchmark)</th></tr></thead>")
    body = f"""
<h1>Ohio counties</h1>
<p class="lede">County one-pagers for the 18 PIC-18 counties, the NEO-SMART region: the 14 counties of JobsOhio's
Team NEO region (Ashland, Cuyahoga, Erie, Geauga, Huron, Lake, Lorain, Medina, Portage, Richland, Stark, Summit,
Tuscarawas, Wayne) and the 4 of its Lake to River region (Ashtabula, Columbiana, Mahoning, Trumbull). The same
one-pager exists for every other Ohio county where the Atlas holds at least one row.</p>
<p>The PIC-18 counties' "tiers A-C" column adds up to <strong>{fmt_int(pic_ac)}</strong> site rows: the PIC-18 headline on the
home page (Ohio county in PIC-18; operating status active; verification tiers A-C). The "all tiers" column also counts tier U
candidates. All counts are Atlas database rows by the unit named in the column heading. The QCEW column is a
count benchmark from BLS, not matched coverage; "n/a" means the bundled benchmark file has no row for that
county, which is not a zero. County is taken from each site's physical address.</p>
<h2>PIC-18 counties</h2>
{table_wrap(f"<table><caption>PIC-18 counties (NEO-SMART region: JobsOhio Team NEO and Lake to River)</caption>{head}<tbody>{pic_rows}</tbody></table>", "PIC-18 counties")}
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
    for sub in ("orgs", "counties", "directory"):          # only generated subdirs are cleared
        if (out_dir / sub).exists():
            shutil.rmtree(out_dir / sub)

    write(out_dir / "style.css", CSS.strip() + "\n")
    write(out_dir / "map.js", MAP_JS)
    write(out_dir / "search.js", SEARCH_JS)
    write(out_dir / "directory.js", DIRECTORY_JS.replace("__PAGE__", str(DIRECTORY_PAGE)))
    write(out_dir / "sortable.js", SORTABLE_JS)
    write(out_dir / "shell.js", SHELL_JS)
    write(out_dir / "explorer.js", EXPLORER_JS)
    shutil.copyfile(Path(__file__).resolve().parent / "assets" / "brand" / "pic-mark-color.svg", out_dir / "favicon.svg")
    og = Path(__file__).resolve().parent / "assets" / "og-image.jpg"
    if og.exists():
        shutil.copyfile(og, out_dir / "og-image.jpg")
    base = "/" + SITE_URL.split("://", 1)[1].split("/", 1)[1] if SITE_URL.count("/") > 3 else "/"
    write(out_dir / "404.html", page(ctx, "Page not found", f"""<div class="notfound">
<p class="big404">404</p>
<h1>That page isn't in the Atlas.</h1>
<p class="lede">The link may be old, or the record may have been renamed or merged. Records are never deleted:
search for the company by name, or start from one of the views below.</p>
<p class="explore-links"><a class="pill" href="{base}search.html">Search organizations</a>
<a class="pill" href="{base}graph/map.html">Map + network</a><a class="pill" href="{base}graph/index.html">Industry graph</a>
<a class="pill" href="{base}index.html">Home</a></p></div>""", base))
    write(out_dir / ".nojekyll", "")
    write(out_dir / "index.html", build_index(ctx))
    write(out_dir / "skyline.html", build_skyline_page(ctx))
    write(out_dir / "skyline.json", json.dumps(ctx.skyline, separators=(",", ":")))
    write(out_dir / "skyline.js", skyline.SKYLINE_JS)
    assets = Path(__file__).resolve().parent / "assets"
    (out_dir / "fonts").mkdir(exist_ok=True)
    (out_dir / "vendor").mkdir(exist_ok=True)
    for f in FONT_FILES:
        shutil.copyfile(assets / "fonts" / f"{f}.woff2", out_dir / "fonts" / f"{f}.woff2")
    shutil.copyfile(assets / "fonts" / "lato-OFL.txt", out_dir / "fonts" / "lato-OFL.txt")
    (out_dir / "brand").mkdir(exist_ok=True)
    for f in ("pic-mark-white.svg", "pic-mark-color.svg", "pic-logo-white-no-tagline.svg"):
        shutil.copyfile(assets / "brand" / f, out_dir / "brand" / f)
    shutil.copyfile(assets / "three" / "three.min.js", out_dir / "vendor" / "three.min.js")
    for lib in VENDOR_LIBS:                  # the explorers' libraries and Leaflet, each with its LICENSE and SHA256SUMS
        shutil.copytree(assets / "vendor" / lib, out_dir / "vendor" / lib, dirs_exist_ok=True)
    shutil.copyfile(assets / "three" / "LICENSE", out_dir / "vendor" / "three-LICENSE.txt")

    sj = sites_json(ctx)
    assert sj["cols"][6] == "st"
    write(out_dir / "sites.json", json.dumps(sj, separators=(",", ":"), ensure_ascii=False))
    write(out_dir / "map.html", build_map_page(ctx, sj["rows"]))
    oj = orgs_json(ctx)
    write(out_dir / "orgs.json", json.dumps(oj, separators=(",", ":"), ensure_ascii=False))
    write(out_dir / "search.html", build_search_page(ctx, len(oj["rows"])))
    xj = experts_json(ctx)
    write(out_dir / "experts.json", json.dumps(xj, separators=(",", ":"), ensure_ascii=False))
    write(out_dir / "experts.js", EXPERTS_JS)
    write(out_dir / "experts.html", build_experts_page(ctx, len(xj["people"]), len(xj["programs"])))

    directory = directory_rows(atlas)
    write(out_dir / "directory.html", build_directory_page(ctx, directory))
    write(out_dir / "directory.json", json.dumps(directory_json(directory), separators=(",", ":"), ensure_ascii=False))
    for name in ("directory.csv", "prospects.csv"):   # prospects.csv is a copy, so links shared before the rename still work
        with open(out_dir / name, "w", newline="", encoding="utf-8-sig") as f:   # BOM: Excel reads it as UTF-8
            f.write(directory_csv(directory, SITE_URL))
    write(out_dir / "prospects.html", build_prospects_stub(ctx))
    write(out_dir / "prospects.js", PROSPECTS_REDIRECT_JS)
    for name, html_ in directory_static_pages(ctx, directory).items():
        write(out_dir / "directory" / name, html_)
    write(out_dir / "counties" / "index.html", build_counties_index(ctx))
    county_names = ohio_counties(atlas)
    for c in county_names:
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
            "county_pages": len(county_names), "map_sites": len(sj["rows"])}


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
