#!/usr/bin/env python3
"""Build the Atlas graph explorer: an interactive, Obsidian-style network view.

    python3 scripts/build_graph.py                  # -> build/graph/index.html (published next to style.css one level up; scripts/build_pages.py)

Reads the canonical CSVs in data/ (read-only) and writes ONE HTML file with the graph
data inlined, rendered inside the shared page shell of scripts/build_site.py (header,
menu, footer, style.css). build/ is gitignored; nothing generated here is
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site  # noqa: E402  (the one page shell, tokens and style.css)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from regions import PIC18, REGION_LABEL  # noqa: E402  (AGENTS.md section 8; owner ruling 2026-11-03)
PIC12 = set(PIC18)  # the reporting region; the name is kept because the explorers' "p" flag and tests use it
TOMBSTONE = {"merged", "acquired", "closed"}
FREE_MIN = 3   # a free-text tag must be shared by this many organizations to appear
TAG_FIELDS = (("processes", "proc"), ("materials", "mat"), ("markets_served", "mkt"))
# Libraries are vendored (scripts/assets/vendor/, npm registry pins); the page loads them from <root>vendor/ on screens 720 px or wider.
GRAPH_LIBS = ("graphology/graphology.umd.min.js", "graphology-library/graphology-library.min.js", "sigma/sigma.min.js")


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
    url = url if url.startswith(("http://", "https://")) else "https://" + url
    return "" if build_site.embeds_email(url) else url   # the site's one link policy: no email address in a published link


def vocab():
    v = json.loads((ROOT / "docs" / "schema" / "vocab.json").read_text(encoding="utf-8"))["vocabularies"]
    return {"proc": set(v["PROCESSES"]["values"]), "mat": set(v["MATERIALS"]["values"]),
            "mkt": set(v["MARKETS"]["values"])}


def public_description(text):
    """The one-line description, unless it refers to the private PIC CRM or carries build and review wording (the filter the ledes use)."""
    return "" if build_site.internal_wording(text) else text


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
            w=https(r["website"]), d=public_description(r["description_1line"]))
    for r in eco:
        oh = r["state"] == "OH"
        add(r["org_id"], k="eco", g=r["ecosystem_subtype"] or "other", l=r["legal_name"], r="5", c=r["city"],
            s=r["state"], n=len(sites_by_org.get(r["org_id"], [])), oh=int(oh),
            p=int(oh and r["county"] in PIC12), m=int(r.get("pic_member") == "true"),
            w=https(r["website"]), d=public_description(r["description_1line"]))

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
            add(f"{t}:{v}", k=t, l=build_site.vocab_label(v), **({"x": 1} if free else {}))
            link(oid, f"{t}:{v}", t + ("x" if free else ""))
    # institutions -> tags they teach or research (program specialties)
    for p in programs:
        inst = p["institution_org_id"]
        for field, t in (("specialty_processes", "proc"), ("specialty_materials", "mat")):
            for v in set(vals(p.get(field))) & VOC[t]:
                add(f"{t}:{v}", k=t, l=build_site.vocab_label(v))
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


PAGE = r"""<div id="stage" class="stage" role="img" aria-label="Network graph of polymer organizations and capability tags"></div>

<aside class="rail" id="rail">
  <div class="vhead">
    <h1>Industry graph</h1>
    <p>Organizations, institutions and the capabilities that link them.</p>
  </div>
  <div class="search">
    <input id="q" type="search" placeholder="Find a company, institution or tag" autocomplete="off" aria-label="Search the graph">
    <div class="sugg" id="sugg" hidden></div>
  </div>
  <div class="stat" id="stat"></div>
  <fieldset>
    <legend>Scope</legend>
    <div class="seg" role="radiogroup">
      <input type="radio" name="scope" id="sc-p12" value="p12" checked><label for="sc-p12">PIC-18</label>
      <input type="radio" name="scope" id="sc-oh" value="oh"><label for="sc-oh">Ohio</label>
      <input type="radio" name="scope" id="sc-all" value="all"><label for="sc-all">All</label>
    </div>
  </fieldset>
  <fieldset>
    <legend>Links</legend>
    <div class="toggles">
      <label><input type="checkbox" id="L-proc" checked><span class="sw" style="background:var(--proc)"></span>Processes</label>
      <label><input type="checkbox" id="L-mat" checked><span class="sw" style="background:var(--mat)"></span>Materials</label>
      <label><input type="checkbox" id="L-mkt"><span class="sw" style="background:var(--mkt)"></span>Markets</label>
      <label><input type="checkbox" id="L-prog" checked><span class="sw" style="background:var(--r5)"></span>Programs</label>
      <label><input type="checkbox" id="L-own" checked><span class="sw" style="background:var(--rx)"></span>Ownership</label>
      <label><input type="checkbox" id="L-assoc" checked><span class="sw" style="background:var(--r5)"></span>Associations</label>
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
</aside>

<section class="card" id="card" hidden aria-live="polite"></section>

"""


SCRIPT = r"""(async () => {
  const RAW = await fetch("graph.json").then((r) => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); });
  const NODES = RAW.nodes, EDGES = RAW.edges;
  const lib = window.graphologyLibrary;
  const RING_NAMES = __RING_NAMES__;   // from RINGS in build_site.py, the one list of ring names
  const KIND_NAMES = { proc: "Process", mat: "Material", mkt: "Market", event: "Event series" };
  const ECO_NAMES = { university_college: "University / college", trade_association: "Trade association",
    government_lab_agency: "Government lab / agency", nonprofit_rd_consortium: "R&D consortium", economic_development: "Economic development",
    workforce_training_provider: "Workforce training", funder_capital: "Funder / capital", accelerator_incubator: "Accelerator / incubator",
    university_tech_transfer: "Tech transfer office", standards_body: "Standards body" };
  const $ = (id) => document.getElementById(id);
  const css = () => { const s = getComputedStyle(document.documentElement); const g = (n) => s.getPropertyValue(n).trim();
    return { ring: { "1": g("--r1"), "2": g("--r2"), "3": g("--r3"), "4": g("--r4"), "5": g("--r5"), "": g("--rx") },
      proc: g("--proc"), mat: g("--mat"), mkt: g("--mkt"), event: g("--event"), free: g("--free"), edge: g("--edge"), edgeHi: g("--edge-hi"),
      dim: g("--dim"), label: g("--label"), accent: g("--accent"), muted: g("--muted"), panel: g("--panel"), line: g("--line") }; };
  let P = css();

  const state = { scope: "p12", layers: { proc: 1, mat: 1, mkt: 0, prog: 1, own: 1, assoc: 1, event: 0 }, orph: true,
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
    else if (state.color === "pic") items = [[P.accent, "PIC member"]];   // the public member list only; absence is never stated (AGENTS 5.1)
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
  const retheme = () => { P = css(); computeCommunities(); if (renderer) { renderer.setSetting("labelColor", { color: P.label });
    renderer.setSetting("defaultEdgeColor", P.edge); renderer.refresh({ skipIndexation: true }); } legend(); };
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", retheme);
  render();
  // deep links: graph/index.html#ORG-000001 (also any tag or event id) opens with that node selected
  const IDX = new Map(NODES.map((n, i) => [n.id, i]));
  const fromHash = () => { const id = decodeURIComponent(location.hash.slice(1)); if (IDX.has(id)) goTo(IDX.get(id)); };
  addEventListener("hashchange", fromHash);
  if (location.hash) setTimeout(fromHash, 50);
})().catch((e) => { document.getElementById("stage").textContent = "Could not load the graph (" + e.message + "). Serve the site over http rather than opening the file."; });
"""


def shell_ctx():
    """The footer's context for pages built from the CSVs rather than from the database."""
    today = __import__("datetime").date.today().isoformat()
    return build_site.Ctx(None, None, build_site.git_info(ROOT), build_site.DEFAULT_REPO, today, None)


def org_base(root):
    """Where the Atlas organization pages live relative to an explorer page (root: path from the page to the site root)."""
    return root + "orgs/"


def ring_names():
    """JSON for the script: the site's one list of ring names, so the graph and the tables never disagree."""
    names = {r: f"Ring {r} \u00b7 {n}" for r, n in build_site.RINGS.items()}
    names[""] = "Ring not set"
    return json.dumps(names, ensure_ascii=False)


def summary(title, lede, facts, root):
    """What a phone gets instead of the canvas (explorer.js loads nothing below 720 px): the same page as text, with the way
    to the company list and the ring colours."""
    legend = "".join(f'<li><span class="sw" style="background:var(--r{r})"></span>Ring {r} \u00b7 {html.escape(n)}</li>'
                     for r, n in build_site.RINGS.items())
    return (f'<section class="viz-summary" aria-labelledby="vs-title"><h1 id="vs-title">{html.escape(title)}</h1>'
            f'<p class="lede">{lede}</p>{facts}'
            f'<p class="hint">The picture needs a screen 720 px wide or more. Find companies lists the companies in the 18 PIC counties, with street '
            f'addresses; Search finds any organization in the Atlas, in any state.</p>'
            f'<div class="btns"><a class="btn primary" href="{root}directory.html">Find companies</a> '
            f'<a class="btn" href="{root}search.html">Search all states</a> <a class="btn" href="{root}map.html">Street map</a> '
            f'<a class="btn" href="{root}counties/index.html">Counties</a></div>'
            f'<h2>Ring colours</h2><ul class="vlegend">{legend}</ul></section>')


def explorer_page(title, active, description, body, root, libs, boot, head_extra="", main_class="viz"):
    """One explorer page in the shared shell: summary and stage in <main>, libraries and script loaded by explorer.js."""
    attrs = f' data-libs="{" ".join(root + "vendor/" + lib for lib in libs)}" data-boot="{boot}"'
    return build_site.page(shell_ctx(), title, body, root, active, description, head_extra,
                           f'<script src="{root}explorer.js" defer></script>', main_class, attrs)


def write_explorer(out, html_text, boot, script_text, data_name, data_text):
    """The page, its script and its data, side by side (the data is fetched on screens 720 px or wider, never on a phone)."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_text, encoding="utf-8")
    (out.parent / boot).write_text(script_text, encoding="utf-8")
    (out.parent / data_name).write_text(data_text, encoding="utf-8")


def data_text(nodes, edges):
    data = {"nodes": nodes, "edges": [[i, j, t] for i, j, t in edges], "commit": commit(),
            "built": __import__("datetime").date.today().isoformat()}
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def script_text(root="../"):
    return SCRIPT.replace("__ORGBASE__", org_base(root)).replace("__RING_NAMES__", ring_names())


def page(nodes, edges, root="../"):
    kinds = defaultdict(int)
    for n in nodes:
        kinds[n["k"]] += 1
    facts = (f'<p><strong>{kinds["org"]:,}</strong> organization rows, <strong>{kinds["eco"]:,}</strong> ecosystem organization rows, '
             f'<strong>{kinds["proc"] + kinds["mat"] + kinds["mkt"]:,}</strong> capability tags (processes, materials, markets) and '
             f'<strong>{kinds["event"]:,}</strong> event series, joined by <strong>{len(edges):,}</strong> links. '
             f'Filter: organizations that are not closed, acquired or merged; all states, all verification tiers.</p>')
    body = summary("Industry graph", "Companies, institutions and the processes and materials that connect them, drawn as a network.",
                   facts, root) + PAGE
    return explorer_page("Industry graph", "graph",
                         "Companies, institutions and the processes and materials that connect them, as a network you can explore.",
                         body, root, GRAPH_LIBS, "graph.js")


def main():
    ap = argparse.ArgumentParser(description="Build the Atlas graph explorer: graph/index.html with graph.js and graph.json beside it.")
    ap.add_argument("--out", default=str(ROOT / "build" / "graph" / "index.html"))
    ap.add_argument("--root", default="../", help="path from the page to the site root (style.css, brand/, orgs/); ../ when published as graph/index.html")
    a = ap.parse_args()
    nodes, edges = build_graph()
    out = Path(a.out)
    write_explorer(out, page(nodes, edges, a.root), "graph.js", script_text(a.root), "graph.json", data_text(nodes, edges))
    kinds = defaultdict(int)
    for n in nodes:
        kinds[n["k"]] += 1
    print(f"graph: {len(nodes)} nodes ({', '.join(f'{k} {v}' for k, v in sorted(kinds.items()))}), {len(edges)} edges -> {out}")
    print(f"size: {out.stat().st_size / 1e3:.0f} kB page, {(out.parent / 'graph.json').stat().st_size / 1e6:.2f} MB data")


if __name__ == "__main__":
    main()
