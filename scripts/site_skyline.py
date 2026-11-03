#!/usr/bin/env python3
"""Data for the home-page "industry skyline": hex-binned site counts on an Albers USA map.

Used by scripts/build_site.py; writes nothing itself. Stdlib only.

* albers_usa(lon, lat) reproduces d3.geoAlbersUsa().scale(1300).translate([487.5, 305])
  for the lower 48. That is the frame us-atlas' *-albers-10m.json files are
  pre-projected to, so site points line up with the vendored state outlines
  (scripts/assets/us-atlas/). Alaska and Hawaii insets are not reproduced, and
  points there are skipped.
* topology_lines() decodes the TopoJSON arcs into simplified polylines (state
  borders, the PIC-18 county outlines).
* hexbins() aggregates site points into pointy-top hexagons with counts, a dominant
  ring and the top cities, for the 3D columns.
Coordinates are reference data (AGENTS.md section 1): they place columns, never evidence.
"""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

GEO = Path(__file__).resolve().parent / "assets" / "us-atlas" / "counties-albers-10m.json"
W, H = 975, 610


def _conic_equal_area(phi0, phi1):
    sy0 = math.sin(phi0)
    n = (sy0 + math.sin(phi1)) / 2
    c = 1 + sy0 * (2 * n - sy0)
    r0 = math.sqrt(c) / n

    def raw(lam, phi):
        r = math.sqrt(max(0.0, c - 2 * n * math.sin(phi))) / n
        return r * math.sin(lam * n), r0 - r * math.cos(lam * n)
    return raw


_RAW = _conic_equal_area(math.radians(29.5), math.radians(45.5))
_K, _TX, _TY = 1300.0, 487.5, 305.0
_CX, _CY = _RAW(math.radians(-0.6), math.radians(38.7))       # d3 center() is applied to the raw projection


def albers_usa(lon, lat):
    """[x, y] in the 975x610 us-atlas frame, or None outside the lower-48 window."""
    if not (24.0 <= lat <= 50.0 and -125.0 <= lon <= -66.0):
        return None
    lam = math.radians(lon + 96.0)                               # rotate([96, 0])
    lam = (lam + math.pi) % (2 * math.pi) - math.pi
    x, y = _RAW(lam, math.radians(lat))
    return _TX + _K * (x - _CX), _TY - _K * (y - _CY)


def _arcs(topo):
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    out = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        out.append(pts)
    return out


def _rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1e-9
    i, d = max(((i, abs(dy * (px - x0) - dx * (py - y0)) / L) for i, (px, py) in enumerate(pts[1:-1], 1)),
               key=lambda t: t[1])
    if d <= eps:
        return [pts[0], pts[-1]]
    return _rdp(pts[:i + 1], eps)[:-1] + _rdp(pts[i:], eps)


def _arc_ids(geom):
    t, arcs = geom["type"], geom["arcs"]
    rings = arcs if t == "Polygon" else [r for poly in arcs for r in poly]
    return {a if a >= 0 else ~a for ring in rings for a in ring}


def _rings(geom, arcs):
    """Polygon rings (as point lists) of one geometry, for point-in-polygon tests."""
    t, A = geom["type"], geom["arcs"]
    polys = [A] if t == "Polygon" else A
    out = []
    for poly in polys:
        for ring in poly:
            pts = []
            for a in ring:
                seg = arcs[a] if a >= 0 else list(reversed(arcs[~a]))
                pts.extend(seg if not pts else seg[1:])
            out.append(pts)
    return out


def point_in_rings(x, y, rings):
    inside = False
    for ring in rings:
        j = len(ring) - 1
        for i in range(len(ring)):
            xi, yi = ring[i]
            xj, yj = ring[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
                inside = not inside
            j = i
    return inside


def topology_lines(pic12_names, eps=0.35):
    topo = json.loads(GEO.read_text(encoding="utf-8"))
    arcs = _arcs(topo)
    state_ids = set()
    for g in topo["objects"]["states"]["geometries"]:
        if str(g.get("id")) in ("02", "15"):      # Alaska, Hawaii insets: no points are plotted there
            continue
        state_ids |= _arc_ids(g)
    pic_ids = set()
    for g in topo["objects"]["counties"]["geometries"]:
        if str(g.get("id", "")).startswith("39") and g.get("properties", {}).get("name") in pic12_names:
            pic_ids |= _arc_ids(g)

    def lines(ids):
        return [[round(v, 1) for p in _rdp(arcs[i], eps) for v in p] for i in sorted(ids)]
    ohio = next(g for g in topo["objects"]["states"]["geometries"] if g["properties"]["name"] == "Ohio")
    return {"borders": lines(state_ids), "pic12": lines(pic_ids), "ohio_rings": _rings(ohio, arcs)}


def hexbins(points, R=7.0):
    """points: iterable of (x, y, ring, city, state, is_pic12). Pointy-top axial hex grid of radius R."""
    bins = defaultdict(list)
    s3 = math.sqrt(3)
    for x, y, ring, city, st, pic in points:
        q, r = (s3 / 3 * x - y / 3) / R, (2 / 3 * y) / R
        cx, cz = q, r
        cy = -cx - cz
        rx, ry, rz = round(cx), round(cy), round(cz)
        dx, dy, dz = abs(rx - cx), abs(ry - cy), abs(rz - cz)
        if dx > dy and dx > dz:
            rx = -ry - rz
        elif dy > dz:
            ry = -rx - rz
        else:
            rz = -rx - ry
        bins[(rx, rz)].append((ring, city, st, pic))
    out = []
    for (q, r), items in bins.items():
        rings = Counter(i[0] or "?" for i in items)
        cities = Counter(f"{i[1].title()}, {i[2]}" for i in items if i[1])
        out.append([round(R * s3 * (q + r / 2), 2), round(R * 1.5 * r, 2), len(items), rings.most_common(1)[0][0],
                    int(any(i[3] for i in items)), " · ".join(c for c, _ in cities.most_common(3))])
    out.sort(key=lambda h: -h[2])
    return out


def payload(sites, ring_of, pic12_names, R=7.0):
    """JSON payload for skyline.js from active, tier A-C site dicts."""
    pts = []
    skipped = 0
    for s in sites:
        try:
            lat, lon = float(s.get("latitude") or ""), float(s.get("longitude") or "")
        except ValueError:
            continue
        p = albers_usa(lon, lat)
        if not p:
            skipped += 1
            continue
        pts.append((p[0], p[1], ring_of(s), s.get("city") or "", s.get("state") or "",
                    s.get("state") == "OH" and s.get("county") in pic12_names))
    lines = topology_lines(pic12_names)
    akron = albers_usa(-81.519, 41.081)
    return {"w": W, "h": H, "R": R, "n": len(pts), "outside_frame": skipped, "hex": hexbins(pts, R),
            "borders": lines["borders"], "pic12": lines["pic12"], "focus": [round(akron[0], 1), round(akron[1], 1)]}


SKYLINE_JS = r"""(function () {
  'use strict';
  var stage = document.getElementById('skyline');
  if (!stage) return;
  var tip = document.getElementById('sky-tip');
  var reduced = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var RING = { '1': 'Ring 1 · producers & processors', '2': 'Ring 2 · materials', '3': 'Ring 3 · value chain', '4': 'Ring 4 · OEMs', '5': 'Ring 5 · ecosystem', '?': 'Ring not set' };

  function fail(msg) { stage.classList.add('sky-fallback'); var p = document.createElement('p'); p.className = 'sky-note'; p.textContent = msg; stage.appendChild(p); }

  fetch(stage.getAttribute('data-src')).then(function (r) { return r.json(); }).then(function (D) {
    if (!window.THREE) return fail('3D view unavailable (the 3D library did not load). The explorers below still work.');
    var probe = document.createElement('canvas');
    if (!(probe.getContext('webgl') || probe.getContext('experimental-webgl'))) return fail('3D view needs WebGL, which this browser has turned off.');
    build(D);
  }).catch(function (e) { fail('Could not load the skyline data (' + e.message + ').'); });

  function build(D) {
    var T = THREE, W2 = D.w / 2, H2 = D.h / 2;
    var renderer = new T.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    stage.appendChild(renderer.domElement);
    var scene = new T.Scene();
    var camera = new T.PerspectiveCamera(32, 1, 1, 5000);
    scene.add(new T.HemisphereLight(0xd6f3f2, 0x05262c, 0.95));
    var sun = new T.DirectionalLight(0xffffff, 0.9); sun.position.set(-300, 600, 400); scene.add(sun);

    // state borders + PIC-18 outline
    function lines(list, color, opacity, y) {
      var pos = [];
      list.forEach(function (a) { for (var i = 0; i + 3 < a.length; i += 2) pos.push(a[i] - W2, y, a[i + 1] - H2, a[i + 2] - W2, y, a[i + 3] - H2); });
      var g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(pos, 3));
      return new T.LineSegments(g, new T.LineBasicMaterial({ color: color, transparent: true, opacity: opacity }));
    }
    scene.add(lines(D.borders, 0x3a8592, 0.5, 0));
    scene.add(lines(D.pic12, 0xb8d637, 0.95, 0.3));

    // hex columns (one instanced mesh)
    var max = D.hex[0] ? D.hex[0][2] : 1, n = D.hex.length;
    var geo = new T.CylinderGeometry(D.R * 0.86, D.R * 0.86, 1, 6); geo.translate(0, 0.5, 0);
    var mat = new T.MeshLambertMaterial({ color: 0xffffff });
    var mesh = new T.InstancedMesh(geo, mat, n);
    // PIC sequential teal (data-seq) rising into brand lime at the peaks; lime is chrome on the deep-teal stage
    var stops = [[0, [0.122, 0.353, 0.388]], [0.4, [0.184, 0.498, 0.549]], [0.7, [0.310, 0.690, 0.741]], [0.88, [0.722, 0.839, 0.216]], [1, [0.933, 0.965, 0.812]]];
    function ramp(t) {
      for (var i = 1; i < stops.length; i++) if (t <= stops[i][0]) {
        var a = stops[i - 1], b = stops[i], u = (t - a[0]) / (b[0] - a[0]);
        return new T.Color(a[1][0] + (b[1][0] - a[1][0]) * u, a[1][1] + (b[1][1] - a[1][1]) * u, a[1][2] + (b[1][2] - a[1][2]) * u);
      }
      return new T.Color(1, 1, 1);
    }
    var hgt = new Float32Array(n), delay = new Float32Array(n), m4 = new T.Matrix4(), q = new T.Quaternion(), s = new T.Vector3(), p = new T.Vector3();
    D.hex.forEach(function (h, i) {
      var t = Math.log(1 + h[2]) / Math.log(1 + max);
      hgt[i] = 3 + Math.sqrt(h[2]) * 9;
      delay[i] = Math.hypot(h[0] - D.focus[0], h[1] - D.focus[1]) / 650;
      mesh.setColorAt(i, ramp(t));
    });
    function place(k) {
      for (var i = 0; i < n; i++) {
        var u = reduced ? 1 : Math.max(0, Math.min(1, (k - delay[i]) / 0.55)); u = 1 - Math.pow(1 - u, 3);
        p.set(D.hex[i][0] - W2, 0, D.hex[i][1] - H2); s.set(1, Math.max(0.01, hgt[i] * u), 1);
        m4.compose(p, q, s); mesh.setMatrixAt(i, m4);
      }
      mesh.instanceMatrix.needsUpdate = true;
    }
    place(0); scene.add(mesh);
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;

    // camera orbit (drag to rotate; gentle sway when idle)
    var view = { az: -0.25, el: 0.95, dist: 1150, tx: 40, tz: 10 }, goal = { tx: 40, tz: 10, dist: 1150 };
    var dragging = false, last = null, idleAt = 0, t0 = performance.now();
    function resize() { var w = stage.clientWidth, h = stage.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
    resize(); window.addEventListener('resize', resize);
    var el = renderer.domElement;
    el.addEventListener('pointerdown', function (e) { dragging = true; last = [e.clientX, e.clientY]; el.setPointerCapture(e.pointerId); });
    el.addEventListener('pointerup', function () { dragging = false; idleAt = performance.now(); });
    el.addEventListener('pointermove', function (e) {
      if (dragging) {
        view.az -= (e.clientX - last[0]) * 0.006; view.el = Math.max(0.35, Math.min(1.35, view.el + (e.clientY - last[1]) * 0.004));
        last = [e.clientX, e.clientY]; tip.hidden = true; return;
      }
      hover(e);
    });
    el.addEventListener('pointerleave', function () { tip.hidden = true; });
    document.querySelectorAll('[data-sky-focus]').forEach(function (b) {
      b.addEventListener('click', function () {
        var f = b.getAttribute('data-sky-focus');
        if (f === 'ohio') { goal.tx = D.focus[0] - W2 - (stage.clientWidth > 720 ? 150 : 20); goal.tz = D.focus[1] - H2 + 30; goal.dist = 460; }
        else { goal.tx = 40; goal.tz = 10; goal.dist = 1150; }
        document.querySelectorAll('[data-sky-focus]').forEach(function (o) { o.setAttribute('aria-pressed', String(o === b)); });
      });
    });

    var ray = new T.Raycaster(), mouse = new T.Vector2();
    function hover(e) {
      var r = el.getBoundingClientRect();
      mouse.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
      ray.setFromCamera(mouse, camera);
      var hit = ray.intersectObject(mesh)[0];
      if (!hit) { tip.hidden = true; return; }
      var h = D.hex[hit.instanceId];
      tip.innerHTML = '<b>' + h[2].toLocaleString() + ' site' + (h[2] === 1 ? '' : 's') + '</b><span>' + (h[5] || '') + '</span><small>' + RING[h[3]] + ' most common' + (h[4] ? ' · PIC-18' : '') + '</small>';
      tip.hidden = false;
      tip.style.left = Math.min(e.clientX - r.left + 14, r.width - 230) + 'px'; tip.style.top = (e.clientY - r.top + 14) + 'px';
    }

    function frame(now) {
      var k = (now - t0) / 1000;
      if (k < 3) place(k);
      if (!dragging && !reduced && now - idleAt > 2500) view.az = -0.25 + Math.sin(k * 0.12) * 0.42;
      view.tx += (goal.tx - view.tx) * 0.06; view.tz += (goal.tz - view.tz) * 0.06; view.dist += (goal.dist - view.dist) * 0.06;
      camera.position.set(view.tx + view.dist * Math.cos(view.el) * Math.sin(view.az), view.dist * Math.sin(view.el), view.tz + view.dist * Math.cos(view.el) * Math.cos(view.az));
      camera.lookAt(view.tx, 0, view.tz);
      renderer.render(scene, camera);
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
})();
"""
