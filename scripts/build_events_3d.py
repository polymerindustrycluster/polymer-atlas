#!/usr/bin/env python3
"""Build the Atlas events presentation: a 3D network of trade shows and their participants.

    python3 scripts/build_events_3d.py                  # -> build/graph/events.html (rendered in the shared shell; scripts/build_pages.py)

Event series (events.csv) are large nodes; organizations that exhibit, sponsor or
otherwise take part (event_participation.csv) orbit them, coloured by ring. Organizations
that attend several shows bridge the clusters. "Present" mode auto-tours the shows,
largest first, flying the camera to each one with a caption (organizer, home city,
participants, Ohio and PIC-18 participants) and particles running along its links;
it is meant for a big screen at an event or a board meeting.

Rendering: 3d-force-graph (three.js, d3-force-3d). Only public fields are written
(AGENTS.md section 6); participation rows name organizations only (AGENTS.md
section 6, event participation). Stdlib only.
"""
import argparse
import html
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("build_graph", HERE / "build_graph.py")
bg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bg)
plural = bg.build_site.plural

LIBS = ("3d-force-graph/3d-force-graph.min.js",)   # vendored, three.js included
ROLE_RANK = {"organizer": 6, "sponsor": 5, "speaker": 4, "exhibitor": 3, "host": 2, "attendee": 1}


def build_data():
    nodes, _ = bg.build_graph()
    idx = {n["id"]: n for n in nodes if n["k"] in ("org", "eco")}
    events = {e["event_id"]: e for e in bg.read(bg.DATA / "events.csv")}
    best, years = {}, defaultdict(set)
    for p in bg.read(bg.DATA / "event_participation.csv"):
        if p["event_id"] not in events or p["org_id"] not in idx:
            continue
        key = (p["event_id"], p["org_id"])
        if ROLE_RANK.get(p["role"], 0) > ROLE_RANK.get(best.get(key, ""), 0):
            best[key] = p["role"]
        if p["edition_year"]:
            years[p["event_id"]].add(p["edition_year"])
    out_nodes, links, seen_org = [], [], set()
    used_events = sorted({e for e, _ in best})
    for eid in used_events:
        e = events[eid]
        out_nodes.append({"id": eid, "k": "event", "l": e["name"], "org": e["organizer_name"],
                          "city": ", ".join(x for x in (e.get("home_city"), e.get("home_state")) if x),
                          "fmt": e.get("event_format", ""), "cad": e.get("cadence", ""),
                          "url": bg.https(e.get("event_url", "")), "yrs": sorted(years[eid])})
    for (eid, oid), role in sorted(best.items()):
        if oid not in seen_org:
            n = idx[oid]
            seen_org.add(oid)
            out_nodes.append({"id": oid, "k": n["k"], "l": n["l"], "r": n.get("r", ""), "c": n.get("c", ""),
                              "s": n.get("s", ""), "oh": n.get("oh", 0), "p": n.get("p", 0), "w": n.get("w", "")})
        links.append({"source": eid, "target": oid, "role": role})
    return {"nodes": out_nodes, "links": links}


PAGE = r"""<div id="stage" class="stage" role="img" aria-label="3D network of trade shows and the organizations that take part"></div>
<div class="title">
  <div class="eyebrow">Trade shows in 3D</div>
  <h1>Who shows up where</h1>
  <p id="stat"></p>
</div>
<div class="bar" role="group" aria-label="Presentation controls">
  <button class="btn primary" id="play" type="button">Present</button>
  <button class="btn" id="prev" type="button" aria-label="Previous show">‹</button>
  <button class="btn" id="next" type="button" aria-label="Next show">›</button>
  <button class="btn" id="p12" type="button" aria-pressed="false">PIC-18 spotlight</button>
  <button class="btn" id="reset" type="button">Overview</button>
  <div class="legend" id="legend"></div>
</div>
<section class="caption" id="caption" hidden aria-live="polite"></section>

"""


SCRIPT = r"""(async () => {
  const D = await fetch("trade-shows.json").then((r) => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); });
  const css = getComputedStyle(document.getElementById("stage")), v = (n) => css.getPropertyValue(n).trim();   // the dark stage scope (.viz.dark)
  const RING = { "1": v("--r1"), "2": v("--r2"), "3": v("--r3"), "4": v("--r4"), "5": v("--r5"), "": v("--rx") };
  const GOLD = v("--lime"), BG = v("--bg"), EVENT = v("--fg");
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const byId = new Map(D.nodes.map((n) => [n.id, n]));
  const evLinks = new Map(), orgEvents = new Map();
  for (const l of D.links) {
    if (!evLinks.has(l.source)) evLinks.set(l.source, []);
    evLinks.get(l.source).push(l);
    orgEvents.set(l.target, (orgEvents.get(l.target) || 0) + 1);
  }
  const events = D.nodes.filter((n) => n.k === "event").sort((a, b) => evLinks.get(b.id).length - evLinks.get(a.id).length);
  const orgs = D.nodes.filter((n) => n.k !== "event");
  const bridges = orgs.filter((o) => orgEvents.get(o.id) > 1).length;
  $("stat").textContent = `${events.length} event series · ${orgs.length} organizations with recorded participation · ${bridges} take part in more than one series`;
  $("legend").innerHTML = [["1", "Ring 1"], ["2", "Ring 2"], ["3", "Ring 3"], ["4", "Ring 4"], ["5", "Ecosystem"]]
    .map(([r, t]) => `<span><i class="sw" style="background:${RING[r]}"></i>${t}</span>`).join("") + `<span><i class="sw" style="background:${EVENT}"></i>Event series</span>`;

  const state = { current: null, org: null, p12: false, playing: false, i: -1, timer: null };
  const ORGBASE = "__ORGBASE__";
  const orgShows = new Map();
  for (const l of D.links) { if (!orgShows.has(l.target)) orgShows.set(l.target, []); orgShows.get(l.target).push(l); }
  const nodeColor = (n) => {
    if (state.org) {
      if (n.id === state.org) return GOLD;
      if (n.k === "event") return orgShows.get(state.org).some((l) => (l.source.id || l.source) === n.id) ? EVENT : "#5f8a90";
      return "#0d4a54";
    }
    if (n.k === "event") return state.current === n.id ? GOLD : state.current ? "#5f8a90" : EVENT;
    if (state.p12 && !n.p) return "#0d4a54";
    if (state.current && !evLinks.get(state.current).some((l) => (l.target.id || l.target) === n.id)) return "#0d4a54";
    return RING[n.r || ""] || RING[""];
  };

  const isLit = (l) => (state.current && (l.source.id || l.source) === state.current) || (state.org && (l.target.id || l.target) === state.org);
  const Graph = ForceGraph3D({ controlType: "orbit" })($("stage"))
    .backgroundColor(BG)
    .graphData(D)
    .nodeId("id")
    .nodeVal((n) => n.k === "event" ? 4 + evLinks.get(n.id).length * 0.9 : 0.6 + (orgEvents.get(n.id) || 1) * 0.6)
    .nodeRelSize(2.4)
    .showNavInfo(false)
    .nodeResolution(14)
    .nodeOpacity(0.92)
    .nodeColor(nodeColor)
    .nodeLabel((n) => n.k === "event"
      ? `<b>${esc(n.l)}</b><br><small>${evLinks.get(n.id).length} organizations · ${esc(n.city || n.org)}</small>`
      : `<b>${esc(n.l)}</b><br><small>${esc([n.c, n.s].filter(Boolean).join(", "))} · ${orgEvents.get(n.id)} show(s)</small>`)
    .linkColor((l) => isLit(l) ? "#b8d637" : "#3a8592")
    .linkOpacity(0.22)
    .linkWidth((l) => isLit(l) ? 0.6 : 0)
    .linkDirectionalParticles((l) => isLit(l) ? 2 : 0)
    .linkDirectionalParticleWidth(1.6)
    .linkDirectionalParticleColor(() => GOLD)
    .linkDirectionalParticleSpeed(0.006)
    .enableNodeDrag(false)
    .warmupTicks(80)
    .cooldownTime(9000)
    .onNodeClick((n) => { stop(); if (n.k === "event") show(events.findIndex((e) => e.id === n.id)); else showOrg(n); });
  Graph.d3Force("charge").strength(-34);
  Graph.d3Force("link").distance((l) => 26 + Math.min(40, evLinks.get(l.source.id || l.source).length * 0.25));

  const controls = Graph.controls();
  controls.autoRotate = !reduced; controls.autoRotateSpeed = 0.45;
  addEventListener("resize", () => Graph.width($("stage").clientWidth).height($("stage").clientHeight));

  function refresh() { Graph.nodeColor(Graph.nodeColor()).linkColor(Graph.linkColor()).linkWidth(Graph.linkWidth()).linkDirectionalParticles(Graph.linkDirectionalParticles()); }

  function fly(n, dist = 380, ms = 2200) {
    const r = Math.hypot(n.x, n.y, n.z) || 1, k = 1 + dist / r;
    Graph.cameraPosition({ x: n.x * k, y: n.y * k, z: n.z * k }, { x: n.x, y: n.y, z: n.z }, reduced ? 0 : ms);
  }

  function show(i) {
    if (i < 0 || !events.length) return;
    state.i = (i + events.length) % events.length;
    const e = events[state.i], ls = evLinks.get(e.id), ps = ls.map((l) => byId.get(l.target.id || l.target));
    state.org = null; state.current = e.id; refresh(); fly(e);
    controls.autoRotate = false;
    const oh = ps.filter((p) => p.oh).length, p12 = ps.filter((p) => p.p);
    const roles = {}; ls.forEach((l) => roles[l.role] = (roles[l.role] || 0) + 1);
    const shared = ps.filter((p) => orgEvents.get(p.id) > 1).length;
    const cap = $("caption");
    cap.dataset.eventId = e.id;
    cap.innerHTML = `
      <div class="step">Show ${state.i + 1} of ${events.length}${e.yrs.length ? " · editions " + esc(e.yrs.join(", ")) : ""}</div>
      <h2>${esc(e.l)}</h2>
      <div class="sub">${esc(e.org)}${e.city ? " · " + esc(e.city) : ""}${e.cad ? " · " + esc(e.cad) : ""}</div>
      <div class="nums">
        <div><b>${ps.length}</b><small>organizations taking part</small></div>
        <div><b>${oh}</b><small>with an Ohio footprint</small></div>
        <div><b>${p12.length}</b><small>in the PIC-18 counties</small></div>
      </div>
      <div class="sub">${Object.entries(roles).map(([r, n]) => `${n} ${esc(r)}${n === 1 ? "" : "s"}`).join(" · ")} · ${shared} also attend other series</div>
      ${p12.length ? `<div class="chips participants" role="region" aria-label="PIC-18 participants" tabindex="0">
        ${p12.map((p) => `<span class="chip" data-org-id="${esc(p.id)}">${esc(p.l)}</span>`).join("")}</div>` : ""}
      ${e.url ? `<a href="${esc(e.url)}" target="_blank" rel="noopener">Event website</a>` : ""}
      <div class="progress"><i id="prog"></i></div>`;
    cap.hidden = false;
    if (state.playing && !reduced) { const bar = $("prog"); bar.style.transition = "none"; bar.style.width = "0"; requestAnimationFrame(() => { bar.style.transition = "width 8s linear"; bar.style.width = "100%"; }); }
  }
  function showOrg(n) {
    state.current = null; state.org = n.id; refresh(); fly(n, 260);
    controls.autoRotate = false;
    const ls = orgShows.get(n.id) || [];
    const place = [n.c, n.s].filter(Boolean).join(", ");
    const ring = n.k === "eco" ? "Ecosystem organization" : (n.r ? "Ring " + n.r : "Ring not recorded");
    const cap = $("caption");
    delete cap.dataset.eventId;
    cap.innerHTML = `
      <div class="step">${esc(ring)}${n.p ? " · PIC-18 county" : n.oh ? " · Ohio footprint" : ""}</div>
      <h2>${esc(n.l)}</h2>
      ${place ? `<div class="sub">${esc(place)}</div>` : ""}
      <div class="sub">Takes part in ${ls.length} event series:</div>
      <div class="chips">${ls.map((l) => { const e = byId.get(l.source.id || l.source);
        return `<button type="button" class="chip chipbtn" data-ev="${esc(e.id)}">${esc(e.l)} <small>${esc(l.role)}</small></button>`; }).join("")}</div>
      <a href="${ORGBASE}${encodeURIComponent(n.id)}.html">Open ${esc(n.l)} in the Atlas \u2192</a>`;
    cap.hidden = false;
    cap.querySelectorAll("[data-ev]").forEach((b) => b.onclick = () => show(events.findIndex((e) => e.id === b.dataset.ev)));
    try { history.replaceState(null, "", "#" + n.id); } catch (e) {}
  }
  function play() {
    state.playing = true; $("play").textContent = "Pause";
    document.documentElement.requestFullscreen?.().catch(() => {});
    show(state.i + 1);
    clearInterval(state.timer); state.timer = setInterval(() => show(state.i + 1), 8000);
  }
  function stop() { state.playing = false; clearInterval(state.timer); $("play").textContent = "Present"; }
  function overview() {
    stop(); state.current = null; state.org = null; state.i = -1; refresh(); $("caption").hidden = true;
    Graph.zoomToFit(reduced ? 0 : 1500, 20, core); controls.autoRotate = !reduced;
  }
  $("play").onclick = () => state.playing ? stop() : play();
  $("next").onclick = () => { stop(); show(state.i + 1); };
  $("prev").onclick = () => { stop(); show(state.i - 1); };
  $("reset").onclick = overview;
  $("p12").onclick = () => { state.p12 = !state.p12; $("p12").setAttribute("aria-pressed", String(state.p12)); refresh(); };
  addEventListener("keydown", (e) => {
    if (e.target.closest && e.target.closest("input, .participants")) return;
    if (e.key === " ") { e.preventDefault(); state.playing ? stop() : play(); }
    else if (e.key === "ArrowRight") { stop(); show(state.i + 1); }
    else if (e.key === "ArrowLeft") { stop(); show(state.i - 1); }
    else if (e.key === "Escape") overview();
  });
  const core = (n) => n.k === "event" && evLinks.get(n.id).length >= 8;  // fit to the larger shows; tiny outliers otherwise shrink the view
  // deep links: graph/events.html#EVT-000001 opens on that show
  const fromHash = () => {
    const id = decodeURIComponent(location.hash.slice(1)), i = events.findIndex((e) => e.id === id);
    if (i >= 0) { stop(); show(i); } else if (byId.has(id)) { stop(); showOrg(byId.get(id)); }
  };
  addEventListener("hashchange", fromHash);
  if (location.hash) setTimeout(fromHash, 2500);
  let fitted = false;
  Graph.onEngineStop(() => { if (!fitted && !state.current) { fitted = true; Graph.zoomToFit(reduced ? 0 : 1200, 20, core); } });
  setTimeout(() => { if (!state.current) Graph.zoomToFit(reduced ? 0 : 1200, 20, core); }, 3500);
})().catch((e) => { document.getElementById("stage").textContent = "Could not load the trade shows (" + e.message + "). Serve the site over http rather than opening the file."; });
"""


STAGE_CSS = r"""/* trade-show stage: title top-left, control bar bottom-left, caption card bottom-right during the tour.
   Everything shared with the other explorers (tokens, .btn, .chips, .viz.dark) comes from style.css. */
.viz .title { position: absolute; top: 14px; left: var(--s-4); z-index: 2; max-width: min(520px, calc(100% - 32px)); pointer-events: none; }
.viz .title .eyebrow { font: 700 12px/1 var(--f-display); letter-spacing: .18em; text-transform: uppercase; color: var(--lime); }
.viz .title h1 { margin: 4px 0 0; font: 700 clamp(30px, 4.2vw, 54px)/0.95 var(--f-display); letter-spacing: .01em; }
.viz .title p { margin: 8px 0 0; color: var(--muted); font: 500 12.5px/1.5 var(--f-body); font-variant-numeric: tabular-nums; }
.viz .bar { position: absolute; left: var(--s-4); bottom: var(--s-4); z-index: 2; display: flex; gap: 6px; flex-wrap: wrap; align-items: center; max-width: calc(100% - 32px); }
.viz .bar .btn { min-height: 44px; padding: 9px 14px; border-radius: 8px; background: var(--panel); font-size: 14px; backdrop-filter: blur(6px); }
.viz .bar .btn.primary { background: var(--accent); color: var(--accent-fg); }
.viz .bar .legend { flex-direction: row; gap: 12px; flex-wrap: wrap; font-size: 12.5px; color: var(--muted); padding: 0 6px; }
.viz .bar .legend span { display: inline-flex; align-items: center; gap: 6px; }
.viz .caption { position: absolute; right: var(--s-4); bottom: var(--s-4); z-index: 2; width: min(420px, calc(100% - 32px)); background: var(--panel);
  border: 1px solid var(--line); border-radius: 12px; padding: 18px 20px; backdrop-filter: blur(10px); display: flex; flex-direction: column; gap: 10px; }
.viz .caption .step { font: 700 11.5px/1 var(--f-body); color: var(--muted); font-variant-numeric: tabular-nums; }
.viz .caption h2 { font: 700 32px/1 var(--f-display); color: var(--lime); }
.viz .caption .sub { color: var(--muted); font-size: 14px; }
.viz .nums { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.viz .nums div { display: flex; flex-direction: column; gap: 2px; }
.viz .nums b { font: 700 30px/1 var(--f-display); font-variant-numeric: tabular-nums; }
.viz .nums small { color: var(--muted); font-size: 12px; line-height: 1.25; }
.viz .participants { max-height: min(11rem, 30vh); overflow-y: auto; }
.viz .participants:focus-visible { outline: 3px solid var(--accent); }
.viz .chipbtn { background: transparent; color: var(--fg); text-align: left; }
.viz .chipbtn:hover { border-color: var(--accent); color: var(--accent); }
.viz .chipbtn small { color: var(--muted); }
.viz .progress { height: 2px; background: var(--line); border-radius: 2px; overflow: hidden; }
.viz .progress i { display: block; height: 100%; width: 0; background: var(--lime); }
.scene-tooltip { font: 13px/1.35 var(--f-body) !important; background: var(--panel) !important; border: 1px solid var(--line); border-radius: 6px; padding: 5px 8px !important; }
.scene-tooltip:empty { display: none !important; }
.scene-tooltip small { color: var(--muted); font-size: 11px; }
@media (prefers-reduced-motion: reduce) { .viz .progress i { transition: none !important; } }
"""


def script_text(root="../"):
    return SCRIPT.replace("__ORGBASE__", bg.org_base(root))


def page(data, root="../"):
    events = [n for n in data["nodes"] if n["k"] == "event"]
    size = defaultdict(int)
    for link in data["links"]:
        size[link["source"]] += 1
    top = sorted(events, key=lambda e: (-size[e["id"]], e["l"]))[:10]
    rows = "".join(f'<li>{html.escape(e["l"])}: {plural(size[e["id"]], "organization row")}</li>' for e in top)
    facts = (f'<p><strong>{len(events):,}</strong> trade-show series and <strong>{len(data["nodes"]) - len(events):,}</strong> organization rows '
             f'that exhibit, sponsor, speak or take part, joined by <strong>{len(data["links"]):,}</strong> participation links '
             f'(one per series and organization, strongest role).</p>'
             f'<h2>Largest series by organization rows</h2><ol>{rows}</ol>')
    body = bg.summary("Trade shows in 3D", "Which companies exhibit, sponsor and speak at which trade shows.", facts, root) + PAGE
    return bg.explorer_page("Trade shows in 3D", "shows",
                            "Which companies exhibit, sponsor and speak at which trade shows, as a 3D network with a presentation mode.",
                            body, root, LIBS, "trade-shows.js", f"<style>\n{STAGE_CSS}</style>", "viz dark")


def main():
    ap = argparse.ArgumentParser(description="Build the Atlas trade-shows page: graph/events.html with trade-shows.js and .json beside it.")
    ap.add_argument("--out", default=str(bg.ROOT / "build" / "graph" / "events.html"))
    ap.add_argument("--root", default="../", help="path from the page to the site root; ../ when published as graph/events.html")
    a = ap.parse_args()
    data = build_data()
    out = Path(a.out)
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    bg.write_explorer(out, page(data, a.root), "trade-shows.js", script_text(a.root), "trade-shows.json", blob)
    ev = sum(1 for n in data["nodes"] if n["k"] == "event")
    print(f"events: {ev} event series, {len(data['nodes']) - ev} organizations, {len(data['links'])} links -> {out}")


if __name__ == "__main__":
    main()
