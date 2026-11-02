#!/usr/bin/env python3
"""Build the Atlas map/graph hybrid: sites on a US map that morph into a network.

    python3 scripts/build_geo_graph.py                  # -> build/graph/map.html
    python3 scripts/build_geo_graph.py --fragment OUT   # body-only page (for hosts that add their own skeleton)

Geography mode: every site with coordinates sits at its address on an Albers USA
map (state outlines, PIC-12 counties highlighted), with optional "company network"
arcs linking each site to its parent's other sites. Network mode: the same dots fly
into a force-directed layout around the capability tags their organization carries
(see scripts/build_graph.py for the tag model), so the industry's structure and its
geography can be compared on one canvas.

Coordinates are reference data (AGENTS.md section 1): they place dots and are never
evidence. Only public fields are written (AGENTS.md section 6). Map geometry: us-atlas
counties-albers-10m (ISC licence, scripts/assets/us-atlas/). Libraries: d3 (projection,
zoom, quadtree), topojson-client, Graphology + ForceAtlas2 (network layout). Stdlib only.
"""
import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("build_graph", HERE / "build_graph.py")
bg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bg)

GEO = HERE / "assets" / "us-atlas" / "counties-albers-10m.json"
D3 = "https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"
TOPOJSON = "https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"
TAG_KINDS = {"proc", "mat", "mkt"}


def build_data():
    nodes, edges = bg.build_graph()
    idx = {n["id"]: i for i, n in enumerate(nodes)}
    sites = [s for s in bg.shards("sites") if s.get("operating_status") != "closed"]
    # org -> tag node indices (vocabulary + shared free-text tags), from the main graph
    org_tags = defaultdict(list)
    for i, j, t in edges:
        a, b = (i, j) if nodes[i]["k"] in ("org", "eco") else (j, i)
        if nodes[b]["k"] in TAG_KINDS and nodes[a]["k"] in ("org", "eco"):
            org_tags[a].append(b)
    orgs, org_pos, tags, tag_pos, out_sites = [], {}, [], {}, []

    def org_ref(i):
        if i not in org_pos:
            n = nodes[i]
            org_pos[i] = len(orgs)
            orgs.append({k: n[k] for k in ("id", "l", "r", "c", "s", "w", "d", "m") if k in n})
        return org_pos[i]

    def tag_ref(i):
        if i not in tag_pos:
            n = nodes[i]
            tag_pos[i] = len(tags)
            tags.append({"l": n["l"], "k": n["k"], "x": n.get("x", 0)})
        return tag_pos[i]

    for s in sites:
        try:
            lat, lon = float(s["latitude"]), float(s["longitude"])
        except (TypeError, ValueError):
            continue
        oi = idx.get(s["org_id"])
        if oi is None:
            continue
        o = org_ref(oi)
        out_sites.append({"n": s["site_name"], "o": o, "c": s["city"], "s": s["state"], "y": s["county"],
                          "p": int(s["state"] == "OH" and s["county"] in bg.PIC12),
                          "la": round(lat, 4), "lo": round(lon, 4)})
    org_tag_list = {}
    for i, o in org_pos.items():
        org_tag_list[o] = sorted({tag_ref(t) for t in org_tags.get(i, [])})
    for o, rec in enumerate(orgs):
        rec["t"] = org_tag_list.get(o, [])
    return {"sites": out_sites, "orgs": orgs, "tags": tags, "held_sites": len(sites)}


PAGE = r"""<title>Polymer Atlas Map</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600&family=Barlow:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: one full-bleed canvas (map <-> network); control rail docked left, detail card right; both stack on phones. */
:root {
  --bg: #eef1f6; --panel: #ffffff; --panel-2: #f5f7fb; --fg: #172033; --muted: #5d6679; --line: #d6dce7;
  --land: #e2e7f0; --border: #c2cad8; --p12: #d9e4f7; --p12-line: #2f6fd6; --accent: #2f6fd6;
  --arc: rgba(40, 56, 92, .14); --arc-hi: rgba(47, 111, 214, .85);
  --ring1: #2f78c9; --ring2: #c4851c; --ring3: #7a5cc4; --ring4: #c2456f; --ring5: #138a7d; --ringx: #7b8496;
  --proc: #1d5fae; --mat: #9a6408; --mkt: #a3325b; --free: #9aa3b5;
  --f-display: "Barlow Condensed", "Arial Narrow", system-ui, sans-serif;
  --f-body: "Barlow", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0c1220; --panel: #131b2c; --panel-2: #192236; --fg: #e3e8f3; --muted: #8e99b2; --line: #26324b;
  --land: #162036; --border: #2b3854; --p12: #1b2c4d; --p12-line: #7fb0ff; --accent: #7fb0ff;
  --arc: rgba(150, 175, 225, .12); --arc-hi: rgba(127, 176, 255, .9);
  --ring1: #5aa3f0; --ring2: #e9b04f; --ring3: #a68cf0; --ring4: #ec7ea3; --ring5: #3fc7b6; --ringx: #8c95a8;
  --proc: #9cc5ff; --mat: #ffd27f; --mkt: #ffa7c6; --free: #59627a; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #0c1220; --panel: #131b2c; --panel-2: #192236; --fg: #e3e8f3; --muted: #8e99b2; --line: #26324b;
  --land: #162036; --border: #2b3854; --p12: #1b2c4d; --p12-line: #7fb0ff; --accent: #7fb0ff;
  --arc: rgba(150, 175, 225, .12); --arc-hi: rgba(127, 176, 255, .9);
  --ring1: #5aa3f0; --ring2: #e9b04f; --ring3: #a68cf0; --ring4: #ec7ea3; --ring5: #3fc7b6; --ringx: #8c95a8;
  --proc: #9cc5ff; --mat: #ffd27f; --mkt: #ffa7c6; --free: #59627a; color-scheme: dark }
html, body { height: 100%; }
body { background: var(--bg); color: var(--fg); font: 15px/1.45 var(--f-body); overflow: hidden; }
canvas#cv { position: fixed; inset: 0; width: 100%; height: 100%; cursor: grab; touch-action: none; }
canvas#cv:active { cursor: grabbing; }
.rail { position: fixed; top: calc(12px + env(safe-area-inset-top, 0px)); left: max(16px, env(safe-area-inset-left, 0px)); width: 296px;
  max-height: calc(100% - 24px - env(safe-area-inset-top, 0px) - env(safe-area-inset-bottom, 0px)); overflow: auto; z-index: 2;
  display: flex; flex-direction: column; gap: 14px; padding: 16px; border-radius: 10px; border: 1px solid var(--line);
  background: color-mix(in srgb, var(--panel) 92%, transparent); backdrop-filter: blur(8px); }
.brand h1 { margin: 0; font: 600 26px/1 var(--f-display); letter-spacing: .02em; }
.brand p { margin: 2px 0 0; color: var(--muted); font-size: 13px; }
.morph { display: grid; grid-template-columns: 1fr 1fr; gap: 0; border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
.morph button { padding: 10px 6px; border: 0; background: var(--panel-2); color: var(--muted); font: 600 15px/1 var(--f-display); letter-spacing: .06em; text-transform: uppercase; cursor: pointer; }
.morph button[aria-pressed="true"] { background: var(--accent); color: var(--panel); }
.morph button:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }
.stat { font: 500 12px/1.45 var(--f-mono); color: var(--muted); font-variant-numeric: tabular-nums; }
.stat b { color: var(--fg); font-weight: 500; }
fieldset { border: 0; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
legend { font: 600 12px/1 var(--f-display); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }
.btns { display: flex; gap: 6px; flex-wrap: wrap; }
.btn { padding: 6px 10px; border-radius: 6px; border: 1px solid var(--line); background: var(--panel-2); color: var(--fg); cursor: pointer; font: 500 13px var(--f-body); }
.btn:hover { border-color: var(--accent); }
.btn:focus-visible { outline: 2px solid var(--accent); }
.toggles { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 10px; }
.toggles label, .opt { display: flex; align-items: center; gap: 7px; font-size: 13.5px; cursor: pointer; }
.sw { width: 10px; height: 10px; border-radius: 50%; flex: none; }
input[type=checkbox] { accent-color: var(--accent); margin: 0; }
.search { position: relative; }
.search input { width: 100%; box-sizing: border-box; padding: 9px 11px; border-radius: 7px; border: 1px solid var(--line); background: var(--panel-2); color: var(--fg); font: 14px var(--f-body); }
.search input:focus { outline: 2px solid var(--accent); outline-offset: -1px; }
.sugg { position: absolute; left: 0; right: 0; top: calc(100% + 4px); background: var(--panel); border: 1px solid var(--line); border-radius: 7px; overflow: hidden; z-index: 5; }
.sugg button { display: flex; width: 100%; justify-content: space-between; gap: 8px; padding: 7px 10px; border: 0; background: none; color: var(--fg); font: 13.5px var(--f-body); text-align: left; cursor: pointer; }
.sugg button:hover, .sugg button:focus-visible { background: var(--panel-2); outline: none; }
.sugg small { color: var(--muted); font: 11px var(--f-mono); white-space: nowrap; }
.hint, .foot { margin: 0; font-size: 12.5px; color: var(--muted); }
.foot { font: 11px/1.4 var(--f-mono); }
.card { position: fixed; top: calc(12px + env(safe-area-inset-top, 0px)); right: max(16px, env(safe-area-inset-right, 0px)); width: 330px;
  max-height: calc(100% - 24px - env(safe-area-inset-top, 0px) - env(safe-area-inset-bottom, 0px)); overflow: auto; z-index: 3;
  background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
.card .kind { font: 600 12px/1 var(--f-display); letter-spacing: .12em; text-transform: uppercase; }
.card h2 { margin: 0; font: 600 24px/1.1 var(--f-display); text-wrap: balance; }
.card p { margin: 0; }
.card h3 { margin: 4px 0 0; font: 600 12px/1 var(--f-display); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
.card a { color: var(--accent); }
.close { position: absolute; top: 10px; right: 10px; border: 0; background: none; color: var(--muted); font-size: 20px; cursor: pointer; line-height: 1; padding: 4px 8px; }
.chips { display: flex; flex-wrap: wrap; gap: 5px; }
.chip { border: 1px solid var(--line); background: var(--panel-2); color: var(--fg); border-radius: 999px; padding: 3px 9px; font: 12.5px var(--f-body); cursor: pointer; }
.chip:hover, .chip:focus-visible { border-color: var(--accent); outline: none; }
.tip { position: fixed; pointer-events: none; z-index: 4; background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 5px 8px; font-size: 13px; max-width: 260px; }
.tip small { display: block; color: var(--muted); font: 11px var(--f-mono); }
.mobile-toggle { display: none; }
@media (max-width: 720px) {
  .rail { right: max(16px, env(safe-area-inset-right, 0px)); width: auto; max-height: 55%; }
  .rail.collapsed > :not(.brand):not(.morph) { display: none; }
  .mobile-toggle { display: inline-block; margin-top: 8px; }
  .card { left: max(16px, env(safe-area-inset-left, 0px)); width: auto; top: auto; bottom: calc(12px + env(safe-area-inset-bottom, 0px)); max-height: 45%; }
}
</style>

<canvas id="cv" aria-label="Map of polymer industry sites that can morph into a capability network"></canvas>
<div class="tip" id="tip" hidden></div>

<aside class="rail" id="rail">
  <div class="brand">
    <h1>Polymer Atlas Map</h1>
    <p>Where the industry is, and how it connects.</p>
    <button class="btn mobile-toggle" id="railToggle" type="button" aria-expanded="false">Show controls</button>
  </div>
  <div class="morph" role="group" aria-label="View">
    <button type="button" id="m-geo" aria-pressed="true">Geography</button>
    <button type="button" id="m-net" aria-pressed="false">Network</button>
  </div>
  <div class="search">
    <input id="q" type="search" placeholder="Find a company or city" autocomplete="off" aria-label="Search sites">
    <div class="sugg" id="sugg" hidden></div>
  </div>
  <div class="stat" id="stat"></div>
  <fieldset>
    <legend>Zoom to</legend>
    <div class="btns">
      <button class="btn" type="button" id="z-us">United States</button>
      <button class="btn" type="button" id="z-oh">Ohio</button>
      <button class="btn" type="button" id="z-p12">PIC-12</button>
    </div>
  </fieldset>
  <fieldset>
    <legend>Show</legend>
    <div class="toggles" id="rings"></div>
    <label class="opt"><input type="checkbox" id="arcs" checked>Company networks (sites of one parent)</label>
    <label class="opt"><input type="checkbox" id="p12only">Only PIC-12 sites</label>
  </fieldset>
  <p class="hint" id="modeHint"></p>
  __HOME__<p class="foot" id="foot"></p>
</aside>
<section class="card" id="card" hidden aria-live="polite"></section>

<script src="__D3__"></script>
<script src="__TOPOJSON__"></script>
<script src="__GRAPHOLOGY__"></script>
<script src="__GRAPHOLOGY_LIB__"></script>
<script id="geo-data" type="application/json">__GEO__</script>
<script id="atlas-data" type="application/json">__DATA__</script>
<script>
(() => {
  const D = JSON.parse(document.getElementById("atlas-data").textContent);
  const US = JSON.parse(document.getElementById("geo-data").textContent);
  const PIC12 = new Set(["Ashtabula","Cuyahoga","Geauga","Lake","Lorain","Mahoning","Medina","Portage","Stark","Summit","Trumbull","Wayne"]);
  const RING = { "1": "Ring 1 · producers & processors", "2": "Ring 2 · materials & compounding", "3": "Ring 3 · value chain", "4": "Ring 4 · OEMs & heavy users", "5": "Ring 5 · ecosystem", "": "Ring not set" };
  const $ = (id) => document.getElementById(id);
  const cv = $("cv"), ctx = cv.getContext("2d");
  let P = {};
  const readTheme = () => { const s = getComputedStyle(document.documentElement), g = (n) => s.getPropertyValue(n).trim();
    P = { land: g("--land"), border: g("--border"), p12: g("--p12"), p12line: g("--p12-line"), arc: g("--arc"), arcHi: g("--arc-hi"),
      accent: g("--accent"), fg: g("--fg"), muted: g("--muted"), panel: g("--panel"), line: g("--line"), bg: g("--bg"),
      ring: { "1": g("--ring1"), "2": g("--ring2"), "3": g("--ring3"), "4": g("--ring4"), "5": g("--ring5"), "": g("--ringx") },
      proc: g("--proc"), mat: g("--mat"), mkt: g("--mkt"), free: g("--free"),
      font: getComputedStyle(document.body).fontFamily }; };
  readTheme();

  // --- geography (us-atlas is pre-projected to a 975x610 Albers USA frame) -------------
  const W = 975, H = 610;
  const proj = d3.geoAlbersUsa().scale(1300).translate([487.5, 305]);
  const states = topojson.feature(US, US.objects.states).features;
  const ohioCounties = topojson.feature(US, US.objects.counties).features.filter((f) => String(f.id).startsWith("39"));
  const p12Counties = ohioCounties.filter((f) => PIC12.has(f.properties.name));
  const ohio = states.find((f) => f.properties.name === "Ohio");
  const statePaths = states.map((f) => new Path2D(d3.geoPath()(f)));
  const ohCountyPath = new Path2D(ohioCounties.map((f) => d3.geoPath()(f)).join(""));
  const p12Path = new Path2D(p12Counties.map((f) => d3.geoPath()(f)).join(""));

  const S = D.sites, O = D.orgs, T = D.tags;
  const geo = new Float32Array(S.length * 2), net = new Float32Array(S.length * 2 + T.length * 2), cur = new Float32Array(S.length * 2);
  let placed = 0;
  S.forEach((s, i) => { const p = proj([s.lo, s.la]); s.ok = !!p; if (p) { geo[2 * i] = p[0]; geo[2 * i + 1] = p[1]; placed++; } });
  cur.set(geo);
  const sitesByOrg = new Map();
  S.forEach((s, i) => { if (!s.ok) return; if (!sitesByOrg.has(s.o)) sitesByOrg.set(s.o, []); sitesByOrg.get(s.o).push(i); });
  // anchor each company network on its headquarters-city site (falls back to the first site)
  for (const [o, list] of sitesByOrg) {
    const hq = list.findIndex((i) => S[i].c && O[o].c && S[i].c.toLowerCase() === O[o].c.toLowerCase() && S[i].s === O[o].s);
    if (hq > 0) list.unshift(...list.splice(hq, 1));
  }
  const tagSites = new Uint32Array(T.length);
  S.forEach((s) => { if (s.ok) for (const t of O[s.o].t) tagSites[t]++; });
  const labelCut = [...tagSites].filter((_, n) => !T[n].x).sort((a, b) => b - a)[30] || 0;

  const state = { mode: "geo", t: 0, rings: { "1": 1, "2": 1, "3": 1, "4": 1, "5": 1, "": 1 }, arcs: true, p12only: false,
    hover: -1, org: -1, netReady: false };
  const color = (i) => P.ring[(O[S[i].o].r) || ""] || P.ring[""];
  const visible = (i) => S[i].ok && state.rings[O[S[i].o].r || ""] && (!state.p12only || S[i].p);

  // --- network layout: sites + capability tags, ForceAtlas2 in a worker ------------------
  const netTagOn = new Uint8Array(T.length);
  function computeNetwork() {
    const g = new graphology.Graph({ type: "undirected" });
    S.forEach((s, i) => { if (s.ok) g.addNode("s" + i, { x: geo[2 * i], y: geo[2 * i + 1], size: 1 }); });
    S.forEach((s, i) => {
      if (!s.ok) return;
      for (const t of O[s.o].t) { const k = "t" + t; if (!g.hasNode(k)) g.addNode(k, { x: W / 2 + Math.cos(t) * 200, y: H / 2 + Math.sin(t) * 200, size: 3 }); g.mergeEdge("s" + i, k); }
      const hub = sitesByOrg.get(s.o)[0]; if (hub !== i) g.mergeEdge("s" + i, "s" + hub);
    });
    const settings = Object.assign(graphologyLibrary.layoutForceAtlas2.inferSettings(g), { barnesHutOptimize: true, gravity: 0.5,
      strongGravityMode: true, scalingRatio: 12, outboundAttractionDistribution: false, slowDown: 3 });
    const finish = () => {
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      g.forEachNode((k, a) => { x0 = Math.min(x0, a.x); x1 = Math.max(x1, a.x); y0 = Math.min(y0, a.y); y1 = Math.max(y1, a.y); });
      const sc = Math.min((W - 80) / (x1 - x0 || 1), (H - 60) / (y1 - y0 || 1));
      const fx = (x) => 40 + (x - x0) * sc + ((W - 80) - (x1 - x0) * sc) / 2, fy = (y) => 30 + (y - y0) * sc + ((H - 60) - (y1 - y0) * sc) / 2;
      g.forEachNode((k, a) => {
        const n = +k.slice(1);
        if (k[0] === "s") { net[2 * n] = fx(a.x); net[2 * n + 1] = fy(a.y); }
        else { const o = 2 * S.length + 2 * n; net[o] = fx(a.x); net[o + 1] = fy(a.y); netTagOn[n] = 1; }
      });
      state.netReady = true; $("m-net").disabled = false; $("m-net").textContent = "Network";
      if (state.pendingNet) { state.pendingNet = false; setMode("net"); }
    };
    try {
      const fa2 = new graphologyLibrary.FA2Layout(g, { settings });
      fa2.start(); setTimeout(() => { fa2.stop(); finish(); fa2.kill(); }, 4000);
    } catch (e) { graphologyLibrary.layoutForceAtlas2.assign(g, { iterations: 150, settings }); finish(); }
  }

  // --- canvas + zoom --------------------------------------------------------------------
  let dpr = 1, vw = 0, vh = 0, tf = d3.zoomIdentity, base = { k: 1, x: 0, y: 0 };
  function resize() {
    dpr = window.devicePixelRatio || 1; vw = innerWidth; vh = innerHeight;
    cv.width = vw * dpr; cv.height = vh * dpr;
    const railW = vw > 720 ? 330 : 0, k = Math.min((vw - railW - 32) / W, (vh - 32) / H);
    base = { k, x: railW + (vw - railW - W * k) / 2, y: (vh - H * k) / 2 };
    draw();
  }
  const zoom = d3.zoom().scaleExtent([0.6, 40]).on("zoom", (e) => { tf = e.transform; draw(); });
  d3.select(cv).call(zoom);
  function zoomTo(x0, y0, x1, y1, ms = 900) {
    const w = (x1 - x0) * base.k, h = (y1 - y0) * base.k, railW = vw > 720 ? 330 : 0;
    const k = Math.min(40, 0.85 * Math.min((vw - railW) / w, vh / h));
    const cx = (x0 + x1) / 2 * base.k, cy = (y0 + y1) / 2 * base.k;
    const t = d3.zoomIdentity.translate(railW / 2 + vw / 2 - base.x - k * cx, vh / 2 - base.y - k * cy).scale(k);
    d3.select(cv).transition().duration(matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : ms).call(zoom.transform, t);
  }
  const boundsOf = (f) => d3.geoPath().bounds(f);

  // --- draw ---------------------------------------------------------------------------
  function draw() {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = P.bg; ctx.fillRect(0, 0, vw, vh);
    ctx.save();
    ctx.translate(base.x + tf.x, base.y + tf.y); ctx.scale(tf.k * base.k, tf.k * base.k);
    const px = 1 / (tf.k * base.k), mapA = 1 - state.t;
    if (mapA > 0.01) {
      ctx.globalAlpha = mapA;
      ctx.fillStyle = P.land; ctx.strokeStyle = P.border; ctx.lineWidth = px;
      for (const p of statePaths) { ctx.fill(p); ctx.stroke(p); }
      if (tf.k > 2.5) { ctx.lineWidth = 0.5 * px; ctx.stroke(ohCountyPath); }
      ctx.fillStyle = P.p12; ctx.fill(p12Path); ctx.strokeStyle = P.p12line; ctx.lineWidth = 1.2 * px; ctx.stroke(p12Path);
      ctx.globalAlpha = 1;
    }
    // links
    const sel = state.org;
    if (state.t < 0.5 && state.arcs) {
      ctx.lineWidth = 0.8 * px;
      for (const [o, list] of sitesByOrg) {
        if (list.length < 2) continue;
        const hi = o === sel;
        if (sel >= 0 && !hi) continue;
        const h = list[0];
        if (!visible(h)) continue;
        ctx.strokeStyle = hi ? P.arcHi : P.arc; ctx.lineWidth = (hi ? 1.6 : 0.7) * px;
        ctx.beginPath();
        for (let m = 1; m < list.length; m++) {
          const i = list[m]; if (!visible(i)) continue;
          const x0 = cur[2 * h], y0 = cur[2 * h + 1], x1 = cur[2 * i], y1 = cur[2 * i + 1];
          const mx = (x0 + x1) / 2, my = (y0 + y1) / 2 - Math.hypot(x1 - x0, y1 - y0) * 0.18;
          ctx.moveTo(x0, y0); ctx.quadraticCurveTo(mx, my, x1, y1);
        }
        ctx.stroke();
      }
    }
    if (state.t > 0.02 && state.netReady) {
      ctx.globalAlpha = Math.min(1, state.t) * (sel >= 0 ? 0.9 : 0.5); ctx.lineWidth = 0.5 * px;
      ctx.strokeStyle = sel >= 0 ? P.arcHi : P.arc; ctx.beginPath();
      S.forEach((s, i) => { if (!visible(i) || (sel >= 0 && s.o !== sel)) return;
        for (const t of O[s.o].t) { const o = 2 * S.length + 2 * t; ctx.moveTo(cur[2 * i], cur[2 * i + 1]); ctx.lineTo(net[o], net[o + 1]); } });
      ctx.stroke(); ctx.globalAlpha = 1;
    }
    // sites
    const r = Math.max(1.6, Math.min(3.2, 1.6 + Math.log2(tf.k))) * px;
    for (let i = 0; i < S.length; i++) {
      if (!visible(i)) continue;
      const dim = sel >= 0 && S[i].o !== sel;
      ctx.globalAlpha = dim ? 0.18 : 0.9; ctx.fillStyle = color(i);
      ctx.beginPath(); ctx.arc(cur[2 * i], cur[2 * i + 1], dim ? r * 0.8 : r, 0, 6.2832); ctx.fill();
    }
    ctx.globalAlpha = 1;
    // tags (network mode)
    if (state.t > 0.02 && state.netReady) {
      ctx.globalAlpha = Math.min(1, state.t);
      ctx.font = `600 ${12 * px}px ${P.font}`; ctx.textBaseline = "middle";
      T.forEach((t, n) => {
        if (!netTagOn[n]) return;
        const o = 2 * S.length + 2 * n, x = net[o], y = net[o + 1];
        ctx.fillStyle = t.x ? P.free : P[t.k];
        ctx.beginPath(); ctx.arc(x, y, (2.5 + Math.sqrt(tagSites[n]) * 0.35) * px, 0, 6.2832); ctx.fill();
        if ((!t.x && tagSites[n] >= labelCut) || (!t.x && tf.k > 2.2) || tf.k > 5) {
          ctx.lineWidth = 3 * px; ctx.strokeStyle = P.bg; ctx.strokeText(t.l, x + 6 * px, y);
          ctx.fillStyle = P.fg; ctx.fillText(t.l, x + 6 * px, y); }
      });
      ctx.globalAlpha = 1;
    }
    // hover ring
    if (state.hover >= 0) {
      const i = state.hover; ctx.strokeStyle = P.accent; ctx.lineWidth = 2 * px;
      ctx.beginPath(); ctx.arc(cur[2 * i], cur[2 * i + 1], r + 3 * px, 0, 6.2832); ctx.stroke();
    }
    ctx.restore();
  }

  // --- morph --------------------------------------------------------------------------
  let anim = null;
  function setMode(m) {
    if (m === "net" && !state.netReady) { state.pendingNet = true; $("m-net").textContent = "Arranging…"; return; }
    state.mode = m; $("m-geo").setAttribute("aria-pressed", String(m === "geo")); $("m-net").setAttribute("aria-pressed", String(m === "net"));
    $("modeHint").textContent = m === "geo"
      ? "Each dot is a site at its address. Arcs join the sites of one parent company."
      : "Sites cluster around the processes and materials their company works with. Sites with no capability data drift to the edge.";
    const from = state.t, to = m === "net" ? 1 : 0, t0 = performance.now();
    const dur = matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 1600;
    cancelAnimationFrame(anim);
    const step = (now) => {
      const u = dur ? Math.min(1, (now - t0) / dur) : 1, e = u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
      state.t = from + (to - from) * e;
      for (let i = 0; i < S.length; i++) { cur[2 * i] = geo[2 * i] + (net[2 * i] - geo[2 * i]) * state.t; cur[2 * i + 1] = geo[2 * i + 1] + (net[2 * i + 1] - geo[2 * i + 1]) * state.t; }
      quad = null; draw();
      if (u < 1) anim = requestAnimationFrame(step);
    };
    anim = requestAnimationFrame(step);
    if (m === "net") d3.select(cv).transition().duration(dur).call(zoom.transform, d3.zoomIdentity);
  }
  $("m-geo").onclick = () => setMode("geo");
  $("m-net").onclick = () => setMode("net");

  // --- hit testing ----------------------------------------------------------------------
  let quad = null;
  const getQuad = () => quad || (quad = d3.quadtree().x((i) => cur[2 * i]).y((i) => cur[2 * i + 1]).addAll(S.map((_, i) => i).filter(visible)));
  function pick(ev) {
    const rect = cv.getBoundingClientRect();
    const x = (ev.clientX - rect.left - base.x - tf.x) / (tf.k * base.k), y = (ev.clientY - rect.top - base.y - tf.y) / (tf.k * base.k);
    const hit = getQuad().find(x, y, 8 / (tf.k * base.k));
    return hit == null ? -1 : hit;
  }
  cv.addEventListener("pointermove", (ev) => {
    const i = pick(ev), tip = $("tip");
    if (i !== state.hover) { state.hover = i; draw(); }
    if (i < 0) { tip.hidden = true; return; }
    const s = S[i];
    tip.replaceChildren(document.createTextNode(s.n), Object.assign(document.createElement("small"), { textContent: `${O[s.o].l} · ${[s.c, s.s].filter(Boolean).join(", ")}` }));
    tip.hidden = false; tip.style.left = Math.min(ev.clientX + 14, vw - 270) + "px"; tip.style.top = (ev.clientY + 14) + "px";
  });
  cv.addEventListener("pointerleave", () => { $("tip").hidden = true; state.hover = -1; draw(); });
  cv.addEventListener("click", (ev) => { const i = pick(ev); selectOrg(i >= 0 ? S[i].o : -1, i); });

  // --- detail card ----------------------------------------------------------------------
  const el = (t, p = {}, ...k) => { const e = document.createElement(t); Object.assign(e, p); e.append(...k); return e; };
  function selectOrg(o, focusSite = -1) {
    state.org = o; draw();
    const card = $("card");
    if (o < 0) { card.hidden = true; return; }
    const org = O[o], list = sitesByOrg.get(o) || [];
    const kids = [el("button", { className: "close", type: "button", textContent: "×", ariaLabel: "Close details", onclick: () => selectOrg(-1) }),
      el("div", { className: "kind", textContent: RING[org.r || ""] || "Company", style: `color:${P.ring[org.r || ""]}` }),
      el("h2", { textContent: org.l })];
    if (org.d) kids.push(el("p", { textContent: org.d }));
    if (org.w) kids.push(el("p", {}, el("a", { href: org.w, target: "_blank", rel: "noopener", textContent: org.w.replace(/^https?:\/\//, "").replace(/\/$/, "") })));
    if (org.t.length) kids.push(el("h3", { textContent: `Capabilities · ${org.t.length}` }),
      el("div", { className: "chips" }, ...org.t.map((t) => el("span", { className: "chip", textContent: T[t].l }))));
    kids.push(el("h3", { textContent: `Sites on the map · ${list.length}` }),
      el("div", { className: "chips" }, ...list.map((i) => el("button", { className: "chip", type: "button",
        textContent: [S[i].c, S[i].s].filter(Boolean).join(", ") || S[i].n, onclick: () => zoomToSites([i]) }))));
    card.replaceChildren(...kids); card.hidden = false;
    if (state.mode === "geo") zoomToSites(focusSite >= 0 && list.length > 40 ? [focusSite] : list);
  }
  function zoomToSites(list) {
    if (!list.length) return;
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const i of list) { x0 = Math.min(x0, cur[2 * i]); x1 = Math.max(x1, cur[2 * i]); y0 = Math.min(y0, cur[2 * i + 1]); y1 = Math.max(y1, cur[2 * i + 1]); }
    const pad = 30; zoomTo(x0 - pad, y0 - pad, x1 + pad, y1 + pad);
  }

  // --- controls -------------------------------------------------------------------------
  $("rings").append(...["1", "2", "3", "4", "5", ""].map((r) => {
    const cb = el("input", { type: "checkbox", checked: true, id: "r" + (r || "x") });
    cb.onchange = () => { state.rings[r] = cb.checked ? 1 : 0; quad = null; draw(); stats(); };
    return el("label", {}, cb, el("span", { className: "sw", style: `background:var(--ring${r || "x"})` }),
      document.createTextNode(r ? `Ring ${r}` : "Ring not set"));
  }));
  $("arcs").onchange = (e) => { state.arcs = e.target.checked; draw(); };
  $("p12only").onchange = (e) => { state.p12only = e.target.checked; quad = null; draw(); stats(); };
  $("z-us").onclick = () => d3.select(cv).transition().duration(800).call(zoom.transform, d3.zoomIdentity);
  $("z-oh").onclick = () => { if (state.mode !== "geo") setMode("geo"); const b = boundsOf(ohio); zoomTo(b[0][0], b[0][1], b[1][0], b[1][1]); };
  $("z-p12").onclick = () => { if (state.mode !== "geo") setMode("geo"); const b = d3.geoPath().bounds({ type: "FeatureCollection", features: p12Counties }); zoomTo(b[0][0], b[0][1], b[1][0], b[1][1]); };
  $("railToggle").onclick = () => { const c = $("rail").classList.toggle("collapsed"); $("railToggle").textContent = c ? "Show controls" : "Hide controls"; $("railToggle").setAttribute("aria-expanded", String(!c)); };
  if (matchMedia("(max-width: 720px)").matches) $("rail").classList.add("collapsed");

  const LBL = O.map((o) => o.l.toLowerCase());
  $("q").addEventListener("input", () => {
    const q = $("q").value.trim().toLowerCase(), box = $("sugg");
    if (q.length < 2) { box.hidden = true; return; }
    const hits = [];
    for (let o = 0; o < O.length && hits.length < 30; o++) if (LBL[o].includes(q) && sitesByOrg.has(o)) hits.push(["o", o]);
    const cities = new Map();
    S.forEach((s, i) => { if (s.ok && s.c && s.c.toLowerCase().startsWith(q)) { const k = `${s.c}, ${s.s}`; if (!cities.has(k)) cities.set(k, []); cities.get(k).push(i); } });
    hits.sort((a, b) => (LBL[a[1]].startsWith(q) ? 0 : 1) - (LBL[b[1]].startsWith(q) ? 0 : 1));
    const items = hits.slice(0, 6).map(([, o]) => el("button", { type: "button", onclick: () => { box.hidden = true; $("q").value = O[o].l; if (state.mode !== "geo") setMode("geo"); selectOrg(o); } },
      el("span", { textContent: O[o].l }), el("small", { textContent: `${(sitesByOrg.get(o) || []).length} site(s)` })));
    for (const [k, list] of [...cities].slice(0, 3)) items.push(el("button", { type: "button", onclick: () => { box.hidden = true; if (state.mode !== "geo") setMode("geo"); zoomToSites(list); } },
      el("span", { textContent: k }), el("small", { textContent: `${list.length} site(s)` })));
    box.replaceChildren(...items); box.hidden = items.length === 0;
  });

  function stats() {
    let n = 0, p = 0; for (let i = 0; i < S.length; i++) if (visible(i)) { n++; if (S[i].p) p++; }
    $("stat").innerHTML = `<b>${n.toLocaleString()}</b> sites shown · <b>${p.toLocaleString()}</b> in PIC-12<br>${placed.toLocaleString()} of ${D.held_sites.toLocaleString()} non-closed sites have coordinates`;
  }
  const retheme = () => { readTheme(); draw(); };
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", retheme);
  new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  addEventListener("resize", resize);
  $("foot").textContent = `Built from data/ at ${D.commit} · ${D.built} · site positions are interpolated from addresses (reference data, not evidence)`;
  $("m-net").disabled = true; $("m-net").textContent = "Arranging…";
  setMode("geo"); stats(); resize();
  (window.requestIdleCallback || ((f) => setTimeout(f, 300)))(computeNetwork);
})();
</script>
"""


def page(data, fragment, home=""):
    data.update({"commit": bg.commit(), "built": __import__("datetime").date.today().isoformat()})
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    geo = GEO.read_text(encoding="utf-8").replace("</", "<\\/")
    body = (PAGE.replace("__D3__", D3).replace("__TOPOJSON__", TOPOJSON).replace("__GRAPHOLOGY__", bg.GRAPHOLOGY)
            .replace("__GRAPHOLOGY_LIB__", bg.GRAPHOLOGY_LIB).replace("__GEO__", geo).replace("__DATA__", blob).replace("__HOME__", bg.home_link(home)))
    if fragment:
        return body
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<style>body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n' + body + "\n</body>\n</html>\n")


def main():
    ap = argparse.ArgumentParser(description="Build the Atlas map/graph hybrid (single HTML file).")
    ap.add_argument("--out", default=str(bg.ROOT / "build" / "graph" / "map.html"))
    ap.add_argument("--fragment", metavar="OUT")
    ap.add_argument("--home", default="", help="href of an 'Atlas home' link")
    a = ap.parse_args()
    data = build_data()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(dict(data), False, a.home), encoding="utf-8")
    if a.fragment:
        Path(a.fragment).parent.mkdir(parents=True, exist_ok=True)
        Path(a.fragment).write_text(page(dict(data), True), encoding="utf-8")
    print(f"map: {len(data['sites'])} sites with coordinates (of {data['held_sites']} non-closed), "
          f"{len(data['orgs'])} orgs, {len(data['tags'])} tags -> {out} ({out.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
