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
import importlib.util
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

NAV = [("graph", "Graph", "graph/index.html"), ("geo", "Map + network", "graph/map.html"),
       ("shows", "Trade shows", "graph/events.html"), ("experts", "Programs & researchers", "experts.html"),
       ("search", "Search", "search.html"),
       ("counties", "Ohio counties", "counties/index.html"), ("map", "Street map", "map.html")]
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
<title>{esc(title) + " | Polymer Industry Atlas" if title != "Home" else "Polymer Industry Atlas"}</title>
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<meta property="og:site_name" content="Polymer Industry Atlas">
<meta property="og:title" content="{esc(title if title != "Home" else "Polymer Industry Atlas")}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE_URL}og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{root}style.css">
{head_extra}
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header class="site-header">
<div class="wrap">
<a class="brand" href="{root}index.html"><img src="{root}brand/pic-mark-white.svg" alt="" width="30" height="30">Polymer Industry Atlas</a>
<nav aria-label="Main"><ul>{nav}</ul></nav>
</div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site-footer">
<div class="wrap">
<div class="footer-brand"><img src="{root}brand/pic-logo-white-no-tagline.svg" alt="Polymer Industry Cluster" width="105" height="56">
<span>The Atlas is an open-data project of the Polymer Industry Cluster,<br>powered by the Greater Akron Chamber.</span></div>
<p>Polymer Industry Atlas, built for the Polymer Industry Cluster (PIC), Greater Akron Chamber.
Data license: <a href="https://creativecommons.org/licenses/by/4.0/" rel="noopener">CC BY 4.0</a>.
Source and data: <a href="{esc(ctx.repo_url)}" rel="noopener">{esc(ctx.repo_url)}</a>.</p>
<p class="muted">{ctx.asof()}</p>
<p class="muted">Coordinates are reference data, never evidence. A missing figure is not a zero.
Counts here are database rows, not industry totals.</p>
</div>
</footer>
<script src="{root}sortable.js" defer></script>
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

EXPERTS_JS = r"""(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var D = null, MAXN = 120;
  var params = new URLSearchParams(location.search);
  $('q').value = params.get('q') || '';
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function chip(t) { return '<button type="button" class="xchip" data-q="' + esc(t) + '">' + esc(t) + '</button>'; }
  function instLink(id) { var i = D.insts[id] || [id, '', '', '']; return '<a href="orgs/' + encodeURIComponent(id) + '.html">' + esc(i[0]) + '</a>' + (i[2] ? ' <span class="muted">' + esc([i[1], i[2]].filter(Boolean).join(', ')) + '</span>' : ''); }
  fetch('experts.json').then(function (r) { return r.json(); }).then(function (d) {
    D = d;
    var states = {}; Object.keys(D.insts).forEach(function (k) { if (D.insts[k][2]) states[D.insts[k][2]] = 1; });
    Object.keys(states).sort().forEach(function (s) { var o = document.createElement('option'); o.value = s; o.textContent = s; $('state').appendChild(o); });
    $('state').value = params.get('state') || '';
    var freq = {}, generic = { polymers: 1, polymer: 1, plastics: 1 };
    D.people.forEach(function (p) { p[2].forEach(function (s) { if (!generic[s.toLowerCase()]) freq[s] = (freq[s] || 0) + 1; }); });
    $('chips').innerHTML = '<span class="muted small">Common specialties:</span> ' + Object.keys(freq).sort(function (a, b) { return freq[b] - freq[a]; }).slice(0, 18).map(chip).join('');
    D.peopleHay = D.people.map(function (p) { var i = D.insts[p[3]] || []; return [p[0], p[1], p[2].join(' '), i[0], i[1], i[2]].join(' | ').toLowerCase(); });
    D.progHay = D.programs.map(function (g) { var i = D.insts[g[1]] || []; return [g[0], g[2], g[3], g[4], g[5].join(' '), i[0], i[1], i[2]].join(' | ').toLowerCase(); });
    run();
  }).catch(function (e) { $('count').textContent = 'Could not load the finder data (' + e.message + ').'; });

  function matches(hay, words) { for (var k = 0; k < words.length; k++) if (hay.indexOf(words[k]) === -1) return false; return true; }
  function run() {
    if (!D) return;
    var q = $('q').value.trim().toLowerCase(), st = $('state').value, kind = $('kind').value, show = $('show').value;
    var words = q.split(/\s+/).filter(Boolean);
    var instOk = function (id) { var i = D.insts[id] || ['', '', '', '']; return (!st || i[2] === st) && (!kind || i[3] === kind); };
    var ppl = [], prg = [];
    if (show !== 'programs') D.people.forEach(function (p, k) { if (instOk(p[3]) && matches(D.peopleHay[k], words)) ppl.push(p); });
    if (show !== 'people') D.programs.forEach(function (g, k) { if (instOk(g[1]) && matches(D.progHay[k], words)) prg.push(g); });
    var n = function (k, one, many) { return k.toLocaleString() + ' ' + (k === 1 ? one : many); };
    $('count').textContent = (show === 'programs' ? '' : n(ppl.length, 'researcher record', 'researcher records')) +
      (show === 'both' ? ' and ' : '') + (show === 'people' ? '' : n(prg.length, 'program record', 'program records')) +
      (show !== 'both' && ppl.length + prg.length === 1 ? ' matches' : ' match') + (q || st || kind ? '' : ' (all of them)') + '.';
    $('empty').hidden = ppl.length + prg.length > 0;
    $('ppl').hidden = show === 'programs' || !ppl.length;
    $('prg').hidden = show === 'people' || !prg.length;
    $('people').innerHTML = ppl.slice(0, MAXN).map(function (p) {
      var name = p[4] ? '<a href="' + esc(p[4]) + '" rel="noopener nofollow">' + esc(p[0]) + '</a>' : esc(p[0]);
      return '<li><div class="xh"><strong>' + name + '</strong><span class="muted">' + esc(p[1]) + '</span></div><div class="xi">' + instLink(p[3]) + '</div>' +
        (p[2].length ? '<div class="xs">' + p[2].map(chip).join('') + '</div>' : '') + '</li>';
    }).join('') + (ppl.length > MAXN ? '<li class="muted">Showing the first ' + MAXN + '. Narrow the search to see the rest.</li>' : '');
    $('programs').innerHTML = prg.slice(0, MAXN).map(function (g) {
      var name = g[6] ? '<a href="' + esc(g[6]) + '" rel="noopener nofollow">' + esc(g[0]) + '</a>' : esc(g[0]);
      var meta = [g[2], g[3], g[4]].filter(Boolean).join(' · ');
      return '<li><div class="xh"><strong>' + name + '</strong><span class="muted">' + esc(meta) + '</span></div><div class="xi">' + instLink(g[1]) + '</div>' +
        (g[5].length ? '<div class="xs">' + g[5].map(chip).join('') + '</div>' : '') + '</li>';
    }).join('') + (prg.length > MAXN ? '<li class="muted">Showing the first ' + MAXN + '.</li>' : '');
    var u = new URLSearchParams(); if (q) u.set('q', $('q').value.trim()); if (st) u.set('state', st);
    try { history.replaceState(null, '', u.toString() ? '?' + u.toString() : location.pathname); } catch (e) {}
  }
  var t = null;
  $('q').addEventListener('input', function () { clearTimeout(t); t = setTimeout(run, 120); });
  ['state', 'kind', 'show'].forEach(function (id) { $(id).addEventListener('change', run); });
  $('clear').addEventListener('click', function (e) {
    $('q').value = ''; $('state').value = ''; $('kind').value = ''; $('show').value = 'both'; run(); $('q').focus();
  });
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.xchip[data-q]'); if (!b) return;
    $('q').value = b.getAttribute('data-q'); run(); $('q').focus(); window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();
"""


SORTABLE_JS = r"""(function () {
  'use strict';
  // Progressive enhancement: click a column header to sort; long tables get a filter box.
  // Tables opt out with data-nosort; rows with class "total" stay at the bottom.
  function key(cell) {
    if (!cell) return { n: null, t: '' };
    var raw = (cell.getAttribute('data-sort') || cell.textContent || '').trim();
    var num = raw.replace(/[,$%\s]/g, '');
    if (/^-?\d+(\.\d+)?$/.test(num)) return { n: parseFloat(num), t: raw.toLowerCase() };
    return { n: null, t: raw.toLowerCase() };
  }
  function enhance(table, idx) {
    var head = table.tHead, body = table.tBodies[0];
    if (!head || !body || table.hasAttribute('data-nosort')) return;
    var rows = Array.prototype.slice.call(body.rows);
    if (rows.length < 2) return;
    var ths = head.rows[head.rows.length - 1].cells;
    Array.prototype.forEach.call(ths, function (th, col) {
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
    if (rows.length > 12) {
      var wrap = table.closest('.table-wrap') || table;
      var box = document.createElement('label'); box.className = 'tfilter';
      var inp = document.createElement('input'); inp.type = 'search'; inp.id = 'tfilter-' + idx;
      inp.placeholder = 'Filter ' + rows.length + ' rows';
      var count = document.createElement('span'); count.setAttribute('aria-live', 'polite');
      box.appendChild(document.createTextNode('Filter')); box.appendChild(inp); box.appendChild(count);
      wrap.parentNode.insertBefore(box, wrap);
      inp.addEventListener('input', function () {
        var q = inp.value.trim().toLowerCase(), shown = 0;
        Array.prototype.forEach.call(body.rows, function (r) {
          var hit = !q || r.classList.contains('total') || r.textContent.toLowerCase().indexOf(q) !== -1;
          r.hidden = !hit; if (hit && !r.classList.contains('total')) shown++;
        });
        count.textContent = q ? shown + ' of ' + rows.length : '';
      });
    }
  }
  function init() { Array.prototype.forEach.call(document.querySelectorAll('.table-wrap table'), enhance); }
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
}
@media (prefers-color-scheme: dark){
  :root{--bg:#052e36;--panel:#073f49;--panel-2:#0a4a55;--fg:#eef3f2;--muted:#a9c2c3;--line:#1d5662;
  --accent:#66d7de;--accent-hover:#dba8c9;--accent-fg:#052e36;
  --warn-bg:#3d2a06;--warn-fg:#ffcf85;--ok-bg:#123f30;--ok-fg:#9fe0bf;--danger:hsl(350 80% 72%);
  --r1:#66c0d2;--r2:#e0a040;--r3:#c98ab2;--r4:#f08a64;--r5:#b8d637;--rx:#b0b3ae;
  --shadow-sm:none;--shadow-md:0 4px 12px rgba(0,0,0,.25);--shadow-lg:0 12px 28px rgba(0,0,0,.35);color-scheme:dark}
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
nav ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:4px 18px}
nav a{text-decoration:none;padding:6px 0;border-bottom:2px solid transparent;font:700 .76rem/1 var(--f-display);letter-spacing:.1em;text-transform:uppercase}
.site-header nav a:hover{color:#fff;border-bottom-color:var(--light-blue)}
nav a[aria-current=page]{border-bottom-color:var(--lime)}
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
thead th{background:var(--panel-2);border-top:0;white-space:nowrap;font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
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
article.site{border:1px solid var(--line);border-radius:8px;padding:6px 16px 12px;margin:12px 0;background:var(--panel)}
article.site h3{margin:.5em 0 .2em}
article.site:target{outline:3px solid var(--accent)}
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
@media print{.site-header nav,.skip,.filters,#map{display:none}}

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
th[aria-sort] button.sort{all:unset;cursor:pointer;display:inline-flex;align-items:center;gap:5px;font:inherit;color:inherit;letter-spacing:inherit;text-transform:inherit}
th[aria-sort] button.sort:hover{color:var(--accent-hover)}
th[aria-sort] button.sort:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
th[aria-sort] button.sort::after{content:"";width:0;height:0;border-left:4px solid transparent;border-right:4px solid transparent;border-top:5px solid currentColor;opacity:.3}
th[aria-sort=ascending] button.sort::after{border-top:0;border-bottom:5px solid currentColor;opacity:.9}
th[aria-sort=descending] button.sort::after{opacity:.9}
th.num button.sort{flex-direction:row-reverse}
.tfilter{display:flex;gap:8px;align-items:center;margin:.8em 0 -.4em;font-size:.9rem;color:var(--muted)}
.tfilter input{padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--fg);font:inherit;min-width:0;width:16em;max-width:60%;min-height:40px}

.explore-links{display:flex;gap:8px;flex-wrap:wrap;margin:.2em 0 1em}
.pill{display:inline-flex;align-items:center;gap:6px;min-height:36px;padding:0 14px;border-radius:999px;border:1px solid var(--accent);background:var(--panel);
  font:700 .88rem/1 var(--f-display);text-decoration:none;color:var(--accent);transition:color .15s,border-color .15s}
.pill:hover{border-color:var(--accent-hover);color:var(--accent-hover)}
.notfound{padding:48px 0 24px}.notfound .big404{font:700 6rem/1 var(--f-display);color:var(--accent);margin:0}
@media (max-width:720px){
  .site-header .wrap{gap:6px}
  .site-header nav{width:100%;overflow-x:auto;scrollbar-width:none;-webkit-mask-image:linear-gradient(90deg,#000 88%,transparent)}
  .site-header nav::-webkit-scrollbar{display:none}
  .site-header nav ul{flex-wrap:nowrap;white-space:nowrap;gap:4px 18px;padding-right:24px}
}
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
.xlist{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:10px}
.xlist li{border:1px solid var(--line);border-radius:8px;background:var(--panel);padding:12px 14px;display:flex;flex-direction:column;gap:5px;min-width:0}
.xlist .xh{display:flex;flex-direction:column;gap:1px}
.xlist .xh .muted{font-size:.88rem}
.xlist .xi{font-size:.92rem}
.xlist .xs{display:flex;flex-wrap:wrap;gap:4px;margin-top:2px}
.xlist .xs .xchip{min-height:26px;font-size:.8rem;padding:0 9px;background:var(--panel-2);border-color:transparent}
#count{font-weight:700}

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


_sk_spec = importlib.util.spec_from_file_location("site_skyline", Path(__file__).resolve().parent / "site_skyline.py")
skyline = importlib.util.module_from_spec(_sk_spec)
_sk_spec.loader.exec_module(skyline)

GLYPHS = {
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
        "<table data-nosort><caption>Verification tiers</caption><thead><tr><th scope=\"col\">Tier</th>"
        "<th scope=\"col\">Meaning</th><th scope=\"col\">Typical sources</th></tr></thead>"
        f"<tbody>{tier_rows}</tbody></table>", "Verification tiers")
    sky = skyline.payload(active_ab(sites), lambda x: x["_ring"] or "?", set(PIC12))
    ctx.skyline = sky
    top = "".join(f"<li>{fmt_int(h[2])} site rows: {esc(h[5])}</li>" for h in sky["hex"][:10])

    def xcard(href, glyph, title, text):
        return (f'<a class="xcard" href="{href}">{GLYPHS[glyph]}<h3>{esc(title)}</h3><p>{esc(text)}</p>'
                f'<span class="go">Open &rarr;</span></a>')

    explore = "".join([
        xcard("graph/index.html", "graph", "Industry graph",
              "Companies, institutions and the processes and materials that connect them. Hover to trace a supply web."),
        xcard("graph/map.html", "geo", "Map + network",
              "Every mapped site, with company networks drawn across the map. Then morph geography into structure."),
        xcard("graph/events.html", "shows", "Trade shows in 3D",
              "Which companies exhibit where, as a 3D network with a presentation mode for the big screen."),
        xcard("experts.html", "experts", "Programs & researchers",
              "Find who teaches and researches polymers: search faculty, lab scientists and programs by specialty."),
        xcard("counties/index.html", "counties", "PIC-12 county pages",
              "One page per Northeast Ohio county: establishments by ring, programs, and the official benchmark."),
    ])
    body = f"""
<section class="hero" aria-labelledby="hero-title">
<div class="hero-stage">
<div id="skyline" data-src="skyline.json" role="img"
 aria-label="3D map of the United States with hexagonal columns whose height shows how many polymer industry site rows the Atlas holds in each area; the tallest stand in Northeast Ohio."></div>
<div id="sky-tip" hidden></div>
<div class="hero-copy">
<div class="eyebrow">Open data · Polymer Industry Cluster</div>
<h1 id="hero-title">The polymer industry, <em>mapped.</em></h1>
<p class="lede">Plants, processors, materials makers, OEMs and the schools and groups behind them,
every fact tied to a public source. Built in Akron for Northeast Ohio, growing nationally.</p>
<div class="hero-stats">
<div><b>{fmt_int(len(active_ab(sites)))}</b><small>active site rows (tiers A–C)<br>across all states</small></div>
<div><b>{fmt_int(len(active_ab(oh)))}</b><small>in Ohio</small></div>
<div><b>{fmt_int(len(active_ab(pic)))}</b><small>in the 12 PIC counties</small></div>
</div>
<div class="cta"><a class="btn primary" href="graph/map.html">Explore the map</a>
<a class="btn" href="graph/index.html">Industry graph</a><a class="btn" href="search.html">Search</a></div>
</div>
<div class="hero-legend"><span>Fewer sites</span><span class="ramp"></span><span>More</span><span>· hex ≈ 30 mi</span></div>
<div class="hero-tools"><span class="hero-hint">Drag to rotate</span>
<button class="btn" type="button" data-sky-focus="us" aria-pressed="true">United States</button>
<button class="btn" type="button" data-sky-focus="ohio" aria-pressed="false">Northeast Ohio</button></div>
</div>
</section>
<div class="sr-only"><p>Largest clusters of site rows on the 3D map:</p><ol>{top}</ol></div>
<p class="small muted">The 3D map shows {fmt_int(sky["n"])} active, tier A-C site rows with reference coordinates in the lower 48
states, binned into hexagons; column height follows the count. Lime outlines mark the PIC-12 counties.
Positions are interpolated from addresses and are never evidence.</p>

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
    return page(ctx, "Home", body, "", "index",
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
    return page(ctx, "Street map", body, "", "map", "Street map of polymer industry sites by ring.", head, scripts)


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


def vals(value):
    """';'-separated multi-value field -> list of stripped values."""
    return [v.strip() for v in str(value or "").split(";") if v.strip()]


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
        people.append([p.get("full_name") or "", role, specs, inst(p.get("institution_org_id")), href])
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
</div>
</form>
<div class="xchips" id="chips" aria-label="Common research specialties"></div>
<p id="count" role="status" aria-live="polite">Loading...</p>
<div id="empty" class="xempty" hidden><strong>Nothing matches.</strong> Try fewer words or a broader specialty,
or <button type="button" class="xchip" id="clear">clear the search and filters</button></div>
<section id="ppl" aria-labelledby="ppl-h"><h2 id="ppl-h">Researchers</h2><ul id="people" class="xlist"></ul></section>
<section id="prg" aria-labelledby="prg-h"><h2 id="prg-h">Programs</h2><ul id="programs" class="xlist"></ul></section>
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
{explore_links(o["org_id"], o.get("status"), any(nonempty(x.get("latitude")) for x in a.sites if x.get("org_id") == o["org_id"]))}
{fields}
{('<h2>Subsidiary and child organizations</h2>' + kids_html) if kids_html else ''}
{sites_html}
<h2>Sources</h2>
<p class="small muted">Organization-level sources. Last verified {esc(o.get("last_verified")) or "n/a"}; tier {esc(o.get("verification_tier")) or "n/a"}.</p>
{source_list(o.get("sources"))}
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
{explore_links(e["org_id"], e.get("status"), False)}
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
    write(out_dir / "sortable.js", SORTABLE_JS)
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
