#!/usr/bin/env python3
"""Assemble the public GitHub Pages site into build/pages/ (generated, never committed).

    python3 scripts/build_pages.py            # build/pages/ = static site + graph explorers
    python3 scripts/build_pages.py --out DIR

Layout of the output:
    index.html, map.html, search.html, counties/, orgs/ ...   scripts/build_site.py (from a fresh SQLite build)
    graph/index.html    scripts/build_graph.py      (Sigma.js graph explorer)
    graph/map.html      scripts/build_geo_graph.py  (map / network hybrid)
    graph/events.html   scripts/build_events_3d.py  (3D trade-show presentation)
    .nojekyll           serve files as-is (no Jekyll processing)

Every page is generated from the canonical CSVs in data/ and writes public fields
only (AGENTS.md section 6). The GitHub Actions workflow in docs/ci/pages.yml runs
this script on each push to main and deploys build/pages/. Stdlib only.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(*args):
    print("+", " ".join(str(a) for a in args), flush=True)
    subprocess.run([sys.executable, *map(str, args)], check=True, cwd=ROOT)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=str(ROOT / "build" / "pages"))
    a = ap.parse_args()
    out = Path(a.out).resolve()
    if out == ROOT or ROOT / "data" in (out, *out.parents):
        sys.exit("refusing to write into the repository root or data/")
    if out.exists():
        shutil.rmtree(out)
    run(SCRIPTS / "build_sqlite.py")                       # -> build/polymer-atlas.db
    db = ROOT / "build" / "polymer-atlas.db"
    run(SCRIPTS / "build_site.py", "--db", db, "--out", out)
    graph = out / "graph"
    graph.mkdir(parents=True, exist_ok=True)
    run(SCRIPTS / "build_graph.py", "--out", graph / "index.html", "--home", "../index.html")
    run(SCRIPTS / "build_geo_graph.py", "--out", graph / "map.html", "--home", "../index.html")
    run(SCRIPTS / "build_events_3d.py", "--out", graph / "events.html", "--home", "../index.html")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    pages = sum(1 for _ in out.rglob("*.html"))
    size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    print(f"pages: {pages} HTML files, {size / 1e6:.1f} MB -> {out}")


if __name__ == "__main__":
    main()
