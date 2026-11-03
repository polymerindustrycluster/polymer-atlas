#!/usr/bin/env python3
"""Build the Atlas graph explorer: an interactive, Obsidian-style network view.

    python3 scripts/build_graph.py                  # -> build/graph/index.html
    python3 scripts/build_graph.py --fragment OUT   # body-only page (for hosts that add their own <html> skeleton)

Reads the canonical CSVs in data/ (read-only) and writes ONE self-contained HTML
file with the graph data inlined. build/ is gitignored; nothing generated here is
committed (AGENTS.md section 1). Rendering uses Sigma.js (WebGL) + Graphology
(ForceAtlas2 layout, Louvain communities), loaded from pinned CDN builds.

Graph model
  nodes  organizations (non-tombstoned), ecosystem organizations, and capability
         tags (processes / materials / markets_served values, like Obsidian tags),
         plus event series.
  edges  org - tag     the org's own tags plus the union of its sites' tags
         eco - tag     an institution's polymer programs' specialty processes/materials
         org - org     parent_of (relationships.csv, generated from parent_org_id)
         org - assoc   member_of (association membership, public directory snapshots)
         event - org   event_participation.csv

Privacy (AGENTS.md section 6): only whitelisted public business fields are
written: name, kind, ring, HQ city/state/county, site count, website,
description_1line, and the public PIC membership flag. People records, notes,
sources, pic_relevance and every internal column are never written.
Stdlib only.
"""
import sys
import argparse
import csv
import glob
import html
import json
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from regions import PIC18, REGION_LABEL  # noqa: E402  (AGENTS.md section 8; owner ruling 2026-11-03)
PIC12 = set(PIC18)  # the reporting region; the name is kept because the explorers' "p" flag and tests use it
TOMBSTONE = {"merged", "acquired", "closed"}
FREE_MIN = 3   # a free-text tag must be shared by this many organizations to appear
TAG_FIELDS = (("processes", "proc"), ("materials", "mat"), ("markets_served", "mkt"))
GRAPHOLOGY = "https://cdnjs.cloudflare.com/ajax/libs/graphology/0.25.4/graphology.umd.min.js"
GRAPHOLOGY_LIB = "https://cdn.jsdelivr.net/npm/graphology-library@0.8.0/dist/graphology-library.min.js"
SIGMA = "https://cdnjs.cloudflare.com/ajax/libs/sigma.js/2.4.0/sigma.min.js"


def read(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def shards(prefix):
    return [r for p in sorted(DATA.glob(f"{prefix}_*.csv")) for r in read(p)]


def vals(s):
    return [v.strip() for v in (s or "").split(";") if v.strip()]


def https(url):
    url = (url or "").strip()
    if not url or url == "none_found":
        return ""
    return url if url.startswith(("http://", "https://")) else "https://" + url


def vocab():
    v = json.loads((ROOT / "docs" / "schema" / "vocab.json").read_text(encoding="utf-8"))["vocabularies"]
    return {"proc": set(v["PROCESSES"]["values"]), "mat": set(v["MATERIALS"]["values"]),
            "mkt": set(v["MARKETS"]["values"])}


def build_graph():
    VOC = vocab()  # tags come from the controlled vocabularies only; free text is skipped
    orgs = [r for r in shards("organizations") if r["status"] not in TOMBSTONE]
    eco = [r for r in read(DATA / "ecosystem.csv") if r["status"] not in TOMBSTONE]
    sites = [r for r in shards("sites") if r.get("operating_status") != "closed"]
    rel = read(DATA / "relationships.csv")
    programs = read(DATA / "programs.csv")
    events = read(DATA / "events.csv")
    part = read(DATA / "event_participation.csv")

    nodes, index = [], {}

    def add(nid, **a):
        if nid in index:
            return index[nid]
        index[nid] = len(nodes)
        nodes.append({"id": nid, **a})
        return index[nid]

    sites_by_org = defaultdict(list)
    for s in sites:
        sites_by_org[s["org_id"]].append(s)

    for r in orgs:
        ss = sites_by_org.get(r["org_id"], [])
        oh = r["hq_state"] == "OH" or any(s["state"] == "OH" for s in ss)
        p12 = (r["hq_state"] == "OH" and r["hq_county"] in PIC12) or any(
            s["state"] == "OH" and s["county"] in PIC12 for s in ss)
        add(r["org_id"], k="org", l=r["legal_name"], r=r["ring_primary"] or "", c=r["hq_city"], s=r["hq_state"],
            n=len(ss), oh=int(oh), p=int(p12), m=int(r.get("pic_member") == "true"),
            w=https(r["website"]), d=r["description_1line"])
    for r in eco:
        oh = r["state"] == "OH"
        add(r["org_id"], k="eco", g=r["ecosystem_subtype"] or "other", l=r["legal_name"], r="5", c=r["city"],
            s=r["state"], n=len(sites_by_org.get(r["org_id"], [])), oh=int(oh),
            p=int(oh and r["county"] in PIC12), m=int(r.get("pic_member") == "true"),
            w=https(r["website"]), d=r["description_1line"])

    edges = set()

    def link(a, b, t):
        if a in index and b in index and a != b:
            i, j = sorted((index[a], index[b]))
            edges.add((i, j, t))

    # capability tags: an org's own tags plus the union of its sites' tags.
    # Values are spelling-normalized (lowercase, spaces/hyphens -> "_"); a value in the
    # controlled vocabulary becomes a tag; anything else is a free-text tag (x=1), kept
    # only when at least FREE_MIN organizations share it.
    norm = lambda v: "_".join(v.lower().replace("-", " ").replace("/", " ").split())
    org_tags, free_count = {}, defaultdict(int)
    for r in orgs:
        for field, t in TAG_FIELDS:
            tags = {norm(v) for v in vals(r[field])}
            for s in sites_by_org.get(r["org_id"], []):
                tags.update(norm(v) for v in vals(s.get(field)))
            tags.discard("")
            org_tags[(r["org_id"], t)] = tags
            for v in tags - VOC[t]:
                free_count[(t, v)] += 1
    for (oid, t), tags in org_tags.items():
        for v in tags:
            free = v not in VOC[t]
            if free and free_count[(t, v)] < FREE_MIN:
                continue
            add(f"{t}:{v}", k=t, l=v.replace("_", " "), **({"x": 1} if free else {}))
            link(oid, f"{t}:{v}", t + ("x" if free else ""))
    # institutions -> tags they teach or research (program specialties)
    for p in programs:
        inst = p["institution_org_id"]
        for field, t in (("specialty_processes", "proc"), ("specialty_materials", "mat")):
            for v in set(vals(p.get(field))) & VOC[t]:
                add(f"{t}:{v}", k=t, l=v.replace("_", " "))
                link(inst, f"{t}:{v}", "prog")
    for e in rel:
        if e["relationship_type"] == "parent_of":
            link(e["from_org_id"], e["to_org_id"], "own")
        elif e["relationship_type"] == "member_of":
            link(e["from_org_id"], e["to_org_id"], "assoc")
    ev_names = {e["event_id"]: e["name"] for e in events}
    for p in part:
        if p["org_id"] in index and p["event_id"] in ev_names:
            add(p["event_id"], k="event", l=ev_names[p["event_id"]])
            link(p["event_id"], p["org_id"], "event")

    # tag / event nodes inherit geography from the orgs they touch (for scope filters)
    deg = defaultdict(int)
    for i, j, _ in edges:
        deg[i] += 1
        deg[j] += 1
        for a, b in ((i, j), (j, i)):
            if nodes[a]["k"] in ("proc", "mat", "mkt", "event"):
                nodes[a]["oh"] = nodes[a].get("oh", 0) or nodes[b].get("oh", 0)
                nodes[a]["p"] = nodes[a].get("p", 0) or nodes[b].get("p", 0)
    return nodes, sorted(edges)


def commit():
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


PAGE = r"""<title>Polymer Atlas Graph</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
@font-face { font-family: "Lato"; font-weight: 400; font-display: swap; src: url(../fonts/lato-400-latin.woff2) format("woff2"); }
@font-face { font-family: "Lato"; font-weight: 700; font-display: swap; src: url(../fonts/lato-700-latin.woff2) format("woff2"); }
/* Layout: full-bleed WebGL canvas; a docked control rail on the left, a detail card on the right; both stack over the canvas on phones. */
:root {
  --bg: #faf9f7; --panel: #ffffff; --panel-2: #f1f2f0; --fg: #2b2c2a; --muted: #656661; --line: #ddd9d2;
  --accent: #15727f; --accent-hover: #995480; --edge: #e4e1db; --edge-hi: #15727f; --dim: #e7e5e0;
  --ring1: #4099ac; --ring2: #bb780e; --ring3: #985a80; --ring4: #d5613b; --ring5: #2f6672; --ringx: #8d908b;
  --proc: #073f49; --mat: #6f8200; --mkt: #5c2f4f; --event: #585955; --free: #b9bbb6; --label: #2b2c2a;
  --f-display: "Lato", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  --f-body: var(--f-display);
  --f-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #052e36; --panel: #073f49; --panel-2: #0a4a55; --fg: #eef3f2; --muted: #a9c2c3; --line: #1d5662;
  --accent: #66d7de; --accent-hover: #dba8c9; --edge: #0c3f48; --edge-hi: #66d7de; --dim: #0e4650;
  --ring1: #66c0d2; --ring2: #e0a040; --ring3: #c98ab2; --ring4: #f08a64; --ring5: #9cc3ca; --ringx: #b0b3ae;
  --proc: #eef3f2; --mat: #b8d637; --mkt: #f2b6d6; --event: #c8d2d0; --free: #3c6b73; --label: #eef3f2; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #052e36; --panel: #073f49; --panel-2: #0a4a55; --fg: #eef3f2; --muted: #a9c2c3; --line: #1d5662;
  --accent: #66d7de; --accent-hover: #dba8c9; --edge: #0c3f48; --edge-hi: #66d7de; --dim: #0e4650;
  --ring1: #66c0d2; --ring2: #e0a040; --ring3: #c98ab2; --ring4: #f08a64; --ring5: #9cc3ca; --ringx: #b0b3ae;
  --proc: #eef3f2; --mat: #b8d637; --mkt: #f2b6d6; --event: #c8d2d0; --free: #3c6b73; --label: #eef3f2; color-scheme: dark }
html, body { height: 100%; }
body { background: var(--bg); color: var(--fg); font: 15px/1.45 var(--f-body); overflow: hidden; }
#stage { position: fixed; inset: 0; }
.rail { position: fixed; top: calc(12px + env(safe-area-inset-top, 0px)); left: max(16px, env(safe-area-inset-left, 0px));
  width: 300px; max-height: calc(100% - 24px - env(safe-area-inset-top, 0px) - env(safe-area-inset-bottom, 0px));
  overflow: auto; display: flex; flex-direction: column; gap: 14px; padding: 16px; background: color-mix(in srgb, var(--panel) 92%, transparent);
  border: 1px solid var(--line); border-radius: 10px; backdrop-filter: blur(8px); z-index: 2; }
.brand { display: flex; flex-direction: column; gap: 2px; }
.brand h1 { margin: 0; font: 600 26px/1 var(--f-display); letter-spacing: .02em; text-wrap: balance; }
.brand p { margin: 0; color: var(--muted); font-size: 13px; }
.stat { font: 500 12px/1.4 var(--f-mono); color: var(--muted); font-variant-numeric: tabular-nums; }
.stat b { color: var(--fg); font-weight: 500; }
fieldset { border: 0; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
legend { font: 600 12px/1 var(--f-display); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }
.seg { display: grid; grid-template-columns: repeat(3, 1fr); background: var(--panel-2); border: 1px solid var(--line); border-radius: 7px; padding: 2px; }
.seg input { position: absolute; opacity: 0; pointer-events: none; }
.seg label { text-align: center; padding: 6px 4px; border-radius: 5px; cursor: pointer; font-size: 13px; color: var(--muted); }
.seg input:checked + label { background: var(--panel); color: var(--fg); box-shadow: 0 0 0 1px var(--line); font-weight: 600; }
.seg input:focus-visible + label { outline: 2px solid var(--accent); }
.toggles { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 10px; }
.toggles label, .opt { display: flex; align-items: center; gap: 7px; font-size: 13.5px; cursor: pointer; }
.sw { width: 10px; height: 10px; border-radius: 50%; flex: none; }
input[type=checkbox] { accent-color: var(--accent); margin: 0; }
.search { position: relative; }
.search input { width: 100%; box-sizing: border-box; padding: 9px 11px; border-radius: 7px; border: 1px solid var(--line);
  background: var(--panel-2); color: var(--fg); font: 14px var(--f-body); }
.search input:focus { outline: 2px solid var(--accent); outline-offset: -1px; }
.sugg { position: absolute; left: 0; right: 0; top: calc(100% + 4px); background: var(--panel); border: 1px solid var(--line);
  border-radius: 7px; overflow: hidden; z-index: 5; }
.sugg button { display: flex; width: 100%; justify-content: space-between; gap: 8px; padding: 7px 10px; border: 0; background: none;
  color: var(--fg); font: 13.5px var(--f-body); text-align: left; cursor: pointer; }
.sugg button:hover, .sugg button:focus-visible { background: var(--panel-2); outline: none; }
.sugg small { color: var(--muted); font-family: var(--f-mono); font-size: 11px; white-space: nowrap; }
.legend { display: flex; flex-direction: column; gap: 4px; font-size: 13px; }
.legend div { display: flex; align-items: center; gap: 8px; }
.btns { display: flex; gap: 6px; flex-wrap: wrap; }
.btn { padding: 6px 10px; border-radius: 6px; border: 1px solid var(--line); background: var(--panel-2); color: var(--fg); cursor: pointer; font: 500 13px var(--f-body); }
.btn:hover { border-color: var(--accent); }
.btn:focus-visible { outline: 2px solid var(--accent); }
.card { position: fixed; top: calc(12px + env(safe-area-inset-top, 0px)); right: max(16px, env(safe-area-inset-right, 0px)); width: 340px;
  max-height: calc(100% - 24px - env(safe-area-inset-top, 0px) - env(safe-area-inset-bottom, 0px)); overflow: auto; z-index: 3;
  background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
.card .kind { font: 600 12px/1 var(--f-display); letter-spacing: .12em; text-transform: uppercase; }
.card h2 { margin: 0; font: 600 24px/1.1 var(--f-display); text-wrap: balance; }
.card p { margin: 0; }
.meta { display: grid; grid-template-columns: auto 1fr; gap: 3px 12px; font-size: 13.5px; }
.meta dt { color: var(--muted); }
.meta dd { margin: 0; min-width: 0; overflow-wrap: anywhere; }
.mono { font-family: var(--f-mono); font-size: 12px; }
.chips { display: flex; flex-wrap: wrap; gap: 5px; }
.chip { border: 1px solid var(--line); background: var(--panel-2); color: var(--fg); border-radius: 999px; padding: 3px 9px; font: 12.5px var(--f-body); cursor: pointer; }
.chip:hover, .chip:focus-visible { border-color: var(--accent); outline: none; }
.card h3 { margin: 4px 0 0; font: 600 12px/1 var(--f-display); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
.close { position: absolute; top: 10px; right: 10px; border: 0; background: none; color: var(--muted); font-size: 20px; cursor: pointer; line-height: 1; padding: 4px 8px; }
.card a { color: var(--accent); }
.hint { font-size: 12.5px; color: var(--muted); }
.foot { font: 11px/1.4 var(--f-mono); color: var(--muted); }
.mobile-toggle { display: none; }
@media (max-width: 720px) {
  .rail { left: max(16px, env(safe-area-inset-left, 0px)); right: max(16px, env(safe-area-inset-right, 0px)); width: auto; max-height: 55%; }
  .rail.collapsed > :not(.brand) { display: none; }
  .mobile-toggle { display: inline-block; align-self: flex-start; }
  .card { left: max(16px, env(safe-area-inset-left, 0px)); right: max(16px, env(safe-area-inset-right, 0px)); width: auto; top: auto;
    bottom: calc(12px + env(safe-area-inset-bottom, 0px)); max-height: 45%; }
}
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; } }
</style>

<div id="stage" role="img" aria-label="Network graph of polymer organizations and capability tags"></div>

<aside class="rail" id="rail">
  <div class="brand">
    <h1>Polymer Atlas Graph</h1>
    <p>Organizations, institutions and the capabilities that link them.</p>
    <button class="btn mobile-toggle" id="railToggle" type="button" aria-expanded="false">Show controls</button>
  </div>
  <div class="search">
    <input id="q" type="search" placeholder="Find a company, institution or tag" autocomplete="off" aria-label="Search the graph">
    <div class="sugg" id="sugg" hidden></div>
  </div>
  <div class="stat" id="stat"></div>
  <fieldset>
    <legend>Scope</legend>
    <div class="seg" role="radiogroup">
      <input type="radio" name="scope" id="sc-p12" value="p12"><label for="sc-p12">PIC-18</label>
      <input type="radio" name="scope" id="sc-oh" value="oh" checked><label for="sc-oh">Ohio</label>
      <input type="radio" name="scope" id="sc-all" value="all"><label for="sc-all">All</label>
    </div>
  </fieldset>
  <fieldset>
    <legend>Links</legend>
    <div class="toggles">
      <label><input type="checkbox" id="L-proc" checked><span class="sw" style="background:var(--proc)"></span>Processes</label>
      <label><input type="checkbox" id="L-mat" checked><span class="sw" style="background:var(--mat)"></span>Materials</label>
      <label><input type="checkbox" id="L-mkt"><span class="sw" style="background:var(--mkt)"></span>Markets</label>
      <label><input type="checkbox" id="L-prog" checked><span class="sw" style="background:var(--ring5)"></span>Programs</label>
      <label><input type="checkbox" id="L-own" checked><span class="sw" style="background:var(--ringx)"></span>Ownership</label>
      <label><input type="checkbox" id="L-assoc" checked><span class="sw" style="background:var(--ring5)"></span>Associations</label>
      <label><input type="checkbox" id="L-event"><span class="sw" style="background:var(--event)"></span>Events</label>
    </div>
    <label class="opt"><input type="checkbox" id="free" checked><span class="sw" style="background:var(--free)"></span>Include free-text tags</label>
    <label class="opt"><input type="checkbox" id="orph" checked>Hide unlinked organizations</label>
  </fieldset>
  <fieldset>
    <legend>Color</legend>
    <div class="seg" role="radiogroup">
      <input type="radio" name="color" id="co-ring" value="ring" checked><label for="co-ring">Ring</label>
      <input type="radio" name="color" id="co-comm" value="comm"><label for="co-comm">Clusters</label>
      <input type="radio" name="color" id="co-pic" value="pic"><label for="co-pic">Members</label>
    </div>
    <div class="legend" id="legend"></div>
  </fieldset>
  <div class="btns">
    <button class="btn" id="relayout" type="button">Re-run layout</button>
    <button class="btn" id="fit" type="button">Fit view</button>
  </div>
  <p class="hint">Hover a node to light up its neighbours. Click for details. Scroll to zoom, drag to pan.</p>
  __HOME__<p class="foot" id="foot"></p>
</aside>

<section class="card" id="card" hidden aria-live="polite"></section>

<script src="__GRAPHOLOGY__"></script>
<script src="__GRAPHOLOGY_LIB__"></script>
<script src="__SIGMA__"></script>
<script id="atlas-data" type="application/json">__DATA__</script>
<script>
(() => {
  const RAW = JSON.parse(document.getElementById("atlas-data").textContent);
  const NODES = RAW.nodes, EDGES = RAW.edges;
  const lib = window.graphologyLibrary;
  const RING_NAMES = { "1": "Ring 1 · producers & processors", "2": "Ring 2 · materials & compounding", "3": "Ring 3 · value chain",
    "4": "Ring 4 · OEMs & heavy users", "5": "Ring 5 · ecosystem", "": "Ring not set" };
  const KIND_NAMES = { proc: "Process", mat: "Material", mkt: "Market", event: "Event series" };
  const ECO_NAMES = { university_college: "University / college", trade_association: "Trade association",
    government_lab_agency: "Government lab / agency", nonprofit_rd_consortium: "R&D consortium", economic_development: "Economic development",
    workforce_training_provider: "Workforce training", funder_capital: "Funder / capital", accelerator_incubator: "Accelerator / incubator",
    university_tech_transfer: "Tech transfer office", standards_body: "Standards body" };
  const $ = (id) => document.getElementById(id);
  const css = () => { const s = getComputedStyle(document.documentElement); const g = (n) => s.getPropertyValue(n).trim();
    return { ring: { "1": g("--ring1"), "2": g("--ring2"), "3": g("--ring3"), "4": g("--ring4"), "5": g("--ring5"), "": g("--ringx") },
      proc: g("--proc"), mat: g("--mat"), mkt: g("--mkt"), event: g("--event"), free: g("--free"), edge: g("--edge"), edgeHi: g("--edge-hi"),
      dim: g("--dim"), label: g("--label"), accent: g("--accent"), muted: g("--muted"), panel: g("--panel"), line: g("--line") }; };
  let P = css();

  const state = { scope: "oh", layers: { proc: 1, mat: 1, mkt: 0, prog: 1, own: 1, assoc: 1, event: 0 }, orph: true,
    color: "ring", free: true, hovered: null, selected: null, neigh: new Set() };
  let G = null, renderer = null, fa2 = null, settleTimer = null, comm = {}, commColors = [];

  function inScope(n) { return state.scope === "all" || (state.scope === "oh" ? n.oh : n.p); }
  function edgeOn(t) { const free = t.endsWith("x"); return !!state.layers[free ? t.slice(0, -1) : t] && (!free || state.free); }

  function build() {
    const g = new graphology.Graph({ type: "undirected" });
    const keep = new Set();
    NODES.forEach((n, i) => { if (inScope(n)) keep.add(i); });
    const deg = new Map();
    const es = [];
    for (const [i, j, t] of EDGES) {
      if (!edgeOn(t) || !keep.has(i) || !keep.has(j)) continue;
      es.push([i, j, t]); deg.set(i, (deg.get(i) || 0) + 1); deg.set(j, (deg.get(j) || 0) + 1);
    }
    for (const i of keep) {
      const n = NODES[i], d = deg.get(i) || 0;
      const isTag = n.k === "proc" || n.k === "mat" || n.k === "mkt" || n.k === "event";
      if (isTag && d === 0) continue;
      if (!isTag && d === 0 && state.orph) continue;
      const size = isTag ? 3 + Math.sqrt(d) * 1.15 : 2.2 + Math.sqrt(n.n || 0) * 0.9 + (n.k === "eco" ? 1.4 : 0);
      const a = (i * 2.399963) % (2 * Math.PI), rad = isTag ? 40 + (i % 23) * 3 : 90 + (i % 211);
      g.addNode(String(i), { x: Math.cos(a) * rad, y: Math.sin(a) * rad, size: Math.min(size, isTag ? 15 : 12), label: n.l, idx: i, tag: isTag });
    }
    for (const [i, j, t] of es) {
      const a = String(i), b = String(j);
      if (g.hasNode(a) && g.hasNode(b) && !g.hasEdge(a, b)) g.addEdge(a, b, { t, size: t === "own" || t === "assoc" ? 1.1 : 0.45 });
    }
    return g;
  }

  function baseColor(i) {
    const n = NODES[i];
    if (n.x) return P.free;
    if (n.k === "proc" || n.k === "mat" || n.k === "mkt" || n.k === "event") return P[n.k];
    if (state.color === "comm") return commColors[comm[i] % commColors.length] || P.ring[""];
    if (state.color === "pic") return n.m ? P.accent : P.dim;
    return P.ring[n.k === "eco" ? "5" : (n.r || "")] || P.ring[""];
  }

  // Sigma's WebGL colour parser needs hex/rgb, not CSS4 hsl()
  function hex(h, s, l) {
    const f = (n) => { const k = (n + h / 30) % 12, a = s * Math.min(l, 1 - l);
      return Math.round(255 * (l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1)))).toString(16).padStart(2, "0"); };
    return `#${f(0)}${f(8)}${f(4)}`;
  }
  function computeCommunities() {
    comm = {};
    try {
      const parts = lib.communitiesLouvain(G, { resolution: 1 });
      const sizes = {};
      for (const k in parts) sizes[parts[k]] = (sizes[parts[k]] || 0) + 1;
      const order = Object.keys(sizes).sort((a, b) => sizes[b] - sizes[a]);
      const rank = {}; order.forEach((c, r) => rank[c] = r);
      for (const k in parts) comm[G.getNodeAttribute(k, "idx")] = rank[parts[k]];
      const dark = matchMedia("(prefers-color-scheme: dark)").matches && document.documentElement.dataset.theme !== "light"
        || document.documentElement.dataset.theme === "dark";
      commColors = order.map((_, r) => hex((r * 137.508 + 205) % 360, dark ? 0.70 : 0.62, dark ? 0.66 : 0.42));
    } catch (e) { commColors = []; }
  }

  function legend() {
    const L = $("legend");
    let items = [];
    if (state.color === "ring") items = ["1", "2", "3", "4", "5"].map((r) => [P.ring[r], RING_NAMES[r]]);
    else if (state.color === "pic") items = [[P.accent, "PIC member (public list)"], [P.dim, "Not on the public member list"]];
    else items = [[commColors[0] || P.muted, "Colour = cluster found by Louvain community detection"]];
    items.push([P.proc, "Process tag"], [P.mat, "Material tag"]);
    if (state.layers.mkt) items.push([P.mkt, "Market tag"]);
    if (state.layers.event) items.push([P.event, "Event series"]);
    if (state.free) items.push([P.free, "Free-text tag, not yet in the vocabulary"]);
    L.replaceChildren(...items.map(([c, t]) => { const d = document.createElement("div"); const s = document.createElement("span");
      s.className = "sw"; s.style.background = c; d.append(s, document.createTextNode(t)); return d; }));
  }

  function stats() {
    let orgs = 0, eco = 0, tags = 0;
    G.forEachNode((k, a) => { const n = NODES[a.idx]; if (n.k === "org") orgs++; else if (n.k === "eco") eco++; else tags++; });
    const scope = { p12: "PIC-18 footprint", oh: "Ohio footprint", all: "all records" }[state.scope];
    $("stat").innerHTML = `<b>${orgs.toLocaleString()}</b> organizations · <b>${eco.toLocaleString()}</b> institutions &amp; groups · <b>${tags.toLocaleString()}</b> tags · <b>${G.size.toLocaleString()}</b> links <br>${scope}`;
  }

  function fa2Settings() {
    const s = lib.layoutForceAtlas2.inferSettings(G);
    return Object.assign(s, { barnesHutOptimize: G.order > 800, barnesHutTheta: 0.6, gravity: 0.35, strongGravityMode: true,
      scalingRatio: 14, outboundAttractionDistribution: true, linLogMode: false, adjustSizes: false, slowDown: 4 });
  }
  function startLayout(ms) {
    if (fa2) { fa2.kill(); fa2 = null; }
    clearTimeout(settleTimer);
    const settings = fa2Settings();
    const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const Worker = lib.FA2Layout;
    if (Worker && !reduced) {
      try {
        fa2 = new Worker(G, { settings });
        fa2.start();
        settleTimer = setTimeout(() => { if (fa2) { fa2.stop(); } }, ms);
        return;
      } catch (e) { fa2 = null; }
    }
    lib.layoutForceAtlas2.assign(G, { iterations: 220, settings });
  }

  function render(relayout = true) {
    if (fa2) { fa2.kill(); fa2 = null; }
    G = build();
    // pre-settle synchronously so the first frame already has structure
    try { lib.layoutForceAtlas2.assign(G, { iterations: G.order > 2000 ? 60 : 120, settings: fa2Settings() }); } catch (e) {}
    computeCommunities();
    if (renderer) renderer.kill();
    renderer = new Sigma(G, $("stage"), {
      renderEdgeLabels: false, labelFont: getComputedStyle(document.body).fontFamily, labelSize: 12, labelWeight: "500",
      labelColor: { color: P.label }, labelRenderedSizeThreshold: 7, defaultEdgeColor: P.edge, zIndex: true,
      nodeReducer, edgeReducer, minCameraRatio: 0.03, maxCameraRatio: 6, hoverRenderer: drawHover, hideEdgesOnMove: true,
    });
    renderer.on("enterNode", ({ node }) => { setHover(node); });
    renderer.on("leaveNode", () => { setHover(null); });
    renderer.on("clickNode", ({ node }) => select(+G.getNodeAttribute(node, "idx")));
    renderer.on("clickStage", () => select(null));
    legend(); stats();
    if (state.selected != null && !G.hasNode(String(state.selected))) select(null);
    if (relayout) startLayout(G.order > 3000 ? 9000 : 6000);
  }

  function drawHover(ctx, d, st) {
    if (!d.label) return;
    const size = st.labelSize, pad = 6;
    ctx.font = `${st.labelWeight} ${size}px ${st.labelFont}`;
    const w = ctx.measureText(d.label).width + pad * 2, h = size + pad * 1.4;
    const x = d.x + d.size + 6, y = d.y - h / 2;
    ctx.beginPath(); ctx.arc(d.x, d.y, d.size + 2.5, 0, Math.PI * 2); ctx.lineWidth = 2; ctx.strokeStyle = P.accent; ctx.stroke();
    ctx.beginPath(); ctx.roundRect ? ctx.roundRect(x, y, w, h, 5) : ctx.rect(x, y, w, h);
    ctx.fillStyle = P.panel; ctx.fill(); ctx.lineWidth = 1; ctx.strokeStyle = P.line; ctx.stroke();
    ctx.fillStyle = P.label; ctx.textBaseline = "middle"; ctx.fillText(d.label, x + pad, d.y + 0.5); ctx.textBaseline = "alphabetic";
  }

  function setHover(node) {
    state.hovered = node;
    state.neigh = node ? new Set(G.neighbors(node)) : (state.selected != null && G.hasNode(String(state.selected)) ? new Set(G.neighbors(String(state.selected))) : new Set());
    renderer.refresh({ skipIndexation: true });
  }

  function focusKey() { return state.hovered ?? (state.selected != null && G.hasNode(String(state.selected)) ? String(state.selected) : null); }

  function nodeReducer(key, a) {
    const r = { ...a, color: baseColor(a.idx) };
    const f = focusKey();
    if (f) {
      if (key === f) { r.highlighted = true; r.zIndex = 2; r.forceLabel = true; }
      else if (state.neigh.has(key)) { r.zIndex = 1; r.forceLabel = state.neigh.size < 40 || a.tag; }
      else { r.color = P.dim; r.label = ""; r.zIndex = 0; }
    } else if (a.tag && a.size > 9) r.forceLabel = true;
    return r;
  }
  function edgeReducer(key, a) {
    const f = focusKey();
    const r = { ...a, color: P.edge };
    if (f) {
      const [s, t] = G.extremities(key);
      if (s === f || t === f) { r.color = P.edgeHi; r.size = (a.size || 0.6) + 0.6; r.zIndex = 1; }
      else r.hidden = true;
    }
    return r;
  }

  function el(tag, props = {}, ...kids) { const e = document.createElement(tag); Object.assign(e, props); e.append(...kids); return e; }

  function select(i) {
    state.selected = i;
    const card = $("card");
    try { history.replaceState(null, "", i == null ? location.pathname + location.search : "#" + encodeURIComponent(NODES[i].id)); } catch (e) {}
    if (i == null) { card.hidden = true; setHover(null); return; }
    const n = NODES[i], key = String(i);
    if (!G.hasNode(key)) { card.hidden = true; return; }
    const kind = n.k === "org" ? (RING_NAMES[n.r] || "Company") : n.k === "eco" ? (ECO_NAMES[n.g] || "Ecosystem")
      : n.x ? `${KIND_NAMES[n.k]} · free text, not in the vocabulary` : KIND_NAMES[n.k];
    const color = baseColor(i);
    const kids = [
      el("button", { className: "close", type: "button", ariaLabel: "Close details", textContent: "×", onclick: () => select(null) }),
      el("div", { className: "kind", textContent: kind, style: `color:${color}` }),
      el("h2", { textContent: n.l }),
    ];
    if (n.d) kids.push(el("p", { textContent: n.d }));
    if (n.k === "proc" || n.k === "mat") kids.push(el("p", {}, el("a", { href: "../experts.html?q=" + encodeURIComponent(n.l),
      textContent: "Who teaches or researches " + n.l + "? \u2192" })));
    if (n.k === "org" || n.k === "eco") {
      const meta = el("dl", { className: "meta" });
      const row = (k, v) => { if (v !== "" && v != null) meta.append(el("dt", { textContent: k }), el("dd", {}, v)); };
      row("Atlas ID", el("span", { className: "mono", textContent: n.id }));
      row("Headquarters", [n.c, n.s].filter(Boolean).join(", "));
      if (n.k === "org") row("Sites held", String(n.n || 0));
      if (n.m) row("PIC", "Member (public list)");
      if (n.w) row("Website", el("a", { href: n.w, target: "_blank", rel: "noopener", textContent: n.w.replace(/^https?:\/\//, "").replace(/\/$/, "") }));
      kids.push(meta);
      kids.push(el("p", { className: "open" }, el("a", { href: "__ORGBASE__" + encodeURIComponent(n.id) + ".html",
        textContent: "Open " + n.l + " in the Atlas \u2192" })));
    }
    const nb = G.neighbors(key).map(Number);
    const groups = [["Processes", "proc"], ["Materials", "mat"], ["Markets", "mkt"], ["Event series", "event"]];
    for (const [title, k] of groups) {
      const items = nb.filter((j) => NODES[j].k === k);
      if (items.length) kids.push(el("h3", { textContent: `${title} · ${items.length}` }), chips(items));
    }
    const orgsN = nb.filter((j) => NODES[j].k === "org" || NODES[j].k === "eco");
    if (orgsN.length) {
      orgsN.sort((a, b) => (NODES[b].n || 0) - (NODES[a].n || 0));
      const title = (n.k === "org" || n.k === "eco") ? "Linked organizations" : "Organizations with this tag";
      kids.push(el("h3", { textContent: `${title} · ${orgsN.length}` }), chips(orgsN.slice(0, 60)));
      if (orgsN.length > 60) kids.push(el("p", { className: "hint", textContent: `Showing the 60 with the most sites. Zoom into the graph for the rest.` }));
    }
    card.replaceChildren(...kids);
    card.hidden = false;
    setHover(null);
    const d = renderer.getNodeDisplayData(key);
    if (d) renderer.getCamera().animate({ x: d.x, y: d.y, ratio: Math.min(renderer.getCamera().ratio, 0.6) }, { duration: 500 });
  }
  function chips(list) { return el("div", { className: "chips" }, ...list.map((j) =>
    el("button", { className: "chip", type: "button", textContent: NODES[j].l, onclick: () => select(j) }))); }

  // search
  const LBL = NODES.map((n) => n.l.toLowerCase());
  $("q").addEventListener("input", () => {
    const q = $("q").value.trim().toLowerCase(), box = $("sugg");
    if (q.length < 2) { box.hidden = true; return; }
    const hits = [];
    for (let i = 0; i < NODES.length && hits.length < 40; i++) if (LBL[i].includes(q)) hits.push(i);
    hits.sort((a, b) => (LBL[a].startsWith(q) ? 0 : 1) - (LBL[b].startsWith(q) ? 0 : 1) || LBL[a].length - LBL[b].length);
    box.replaceChildren(...hits.slice(0, 8).map((i) => {
      const n = NODES[i];
      const sub = n.k === "org" ? [n.c, n.s].filter(Boolean).join(", ") : n.k === "eco" ? (ECO_NAMES[n.g] || "Ecosystem") : KIND_NAMES[n.k];
      return el("button", { type: "button", onclick: () => goTo(i) }, el("span", { textContent: n.l }), el("small", { textContent: sub || "" }));
    }));
    box.hidden = hits.length === 0;
  });
  $("q").addEventListener("keydown", (e) => { if (e.key === "Enter") { const b = $("sugg").querySelector("button"); if (b) b.click(); } });
  function goTo(i) {
    $("sugg").hidden = true; $("q").value = NODES[i].l;
    if (!G.hasNode(String(i))) {
      const n = NODES[i];
      state.scope = "all"; $("sc-all").checked = true; state.orph = false; $("orph").checked = false;
      if (n.k in state.layers) { state.layers[n.k] = 1; $("L-" + n.k).checked = true; }
      render();
    }
    select(i);
  }

  // controls
  document.querySelectorAll('input[name=scope]').forEach((r) => r.addEventListener("change", () => { state.scope = r.value; render(); }));
  document.querySelectorAll('input[name=color]').forEach((r) => r.addEventListener("change", () => { state.color = r.value; legend(); renderer.refresh({ skipIndexation: true }); }));
  for (const k of Object.keys(state.layers)) $("L-" + k).addEventListener("change", (e) => { state.layers[k] = e.target.checked ? 1 : 0; render(); });
  $("orph").addEventListener("change", (e) => { state.orph = e.target.checked; render(); });
  $("free").addEventListener("change", (e) => { state.free = e.target.checked; render(); });
  $("relayout").addEventListener("click", () => startLayout(7000));
  $("fit").addEventListener("click", () => renderer.getCamera().animate({ x: 0.5, y: 0.5, ratio: 1, angle: 0 }, { duration: 400 }));
  $("railToggle").addEventListener("click", () => { const r = $("rail"); const c = r.classList.toggle("collapsed");
    $("railToggle").textContent = c ? "Show controls" : "Hide controls"; $("railToggle").setAttribute("aria-expanded", String(!c)); });
  if (matchMedia("(max-width: 720px)").matches) $("rail").classList.add("collapsed");
  const retheme = () => { P = css(); computeCommunities(); if (renderer) { renderer.setSetting("labelColor", { color: P.label });
    renderer.setSetting("defaultEdgeColor", P.edge); renderer.refresh({ skipIndexation: true }); } legend(); };
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", retheme);
  new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  $("foot").textContent = `Built from data/ at ${RAW.commit} · ${RAW.built} · public fields only`;
  render();
  // deep links: graph/index.html#ORG-000001 (also any tag or event id) opens with that node selected
  const IDX = new Map(NODES.map((n, i) => [n.id, i]));
  const fromHash = () => { const id = decodeURIComponent(location.hash.slice(1)); if (IDX.has(id)) goTo(IDX.get(id)); };
  addEventListener("hashchange", fromHash);
  if (location.hash) setTimeout(fromHash, 50);
})();
</script>
"""


def home_link(href, tag="p", cls="hint", style=""):
    """Optional link back to the Atlas site (used when the explorers are published next to it)."""
    if not href:
        return ""
    st = f' style="{style}"' if style else ""
    return f'<{tag} class="{cls}"{st}><a href="{html.escape(href)}">&larr; Polymer Industry Atlas</a></{tag}>'


def org_base(home):
    """Where the Atlas organization pages live relative to an explorer page: next to the home link's index.html,
    or the public site when the explorer is built standalone."""
    if home:
        return (home.rsplit("/", 1)[0] + "/orgs/") if "/" in home else "orgs/"
    return "https://polymerindustrycluster.github.io/polymer-atlas/orgs/"


def page(nodes, edges, fragment, home=""):
    data = {"nodes": nodes, "edges": [[i, j, t] for i, j, t in edges], "commit": commit(),
            "built": __import__("datetime").date.today().isoformat()}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    body = (PAGE.replace("__GRAPHOLOGY__", GRAPHOLOGY).replace("__GRAPHOLOGY_LIB__", GRAPHOLOGY_LIB)
            .replace("__SIGMA__", SIGMA).replace("__DATA__", blob).replace("__HOME__", home_link(home)).replace("__ORGBASE__", org_base(home)))
    if fragment:
        return body
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<style>body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n'
            + body + "\n</body>\n</html>\n")


def main():
    ap = argparse.ArgumentParser(description="Build the Atlas graph explorer (single HTML file).")
    ap.add_argument("--out", default=str(ROOT / "build" / "graph" / "index.html"))
    ap.add_argument("--fragment", metavar="OUT", help="also write a body-only page (no <html>/<head> skeleton) to OUT")
    ap.add_argument("--home", default="", help="href of an 'Atlas home' link (e.g. ../index.html when published with the site)")
    a = ap.parse_args()
    nodes, edges = build_graph()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(nodes, edges, False, a.home), encoding="utf-8")
    if a.fragment:
        Path(a.fragment).parent.mkdir(parents=True, exist_ok=True)
        Path(a.fragment).write_text(page(nodes, edges, True), encoding="utf-8")
    kinds = defaultdict(int)
    for n in nodes:
        kinds[n["k"]] += 1
    print(f"graph: {len(nodes)} nodes ({', '.join(f'{k} {v}' for k, v in sorted(kinds.items()))}), {len(edges)} edges -> {out}"
          + (f" (+ fragment {a.fragment})" if a.fragment else ""))
    print(f"size: {out.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
