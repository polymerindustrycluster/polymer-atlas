#!/usr/bin/env python3
"""Write INPUTS.sha256: sha256 of every input this packet was built from (run from the repo root after build.py; stdlib only).
Repo files are at the commit named on the first line; raw files are the sha256 recorded in raw/MANIFEST.sha256 for each source file the packet cites."""
import csv, hashlib, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build as K

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()

lines = [f"# repo commit {subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()}; lake {K.LAKE}"]
BASE = subprocess.run(["git", "-C", str(ROOT), "merge-base", "origin/main", "HEAD"], capture_output=True, text=True).stdout.strip()
lines[0] += f"; repo files below are as at merge-base {BASE} (before this packet's evidence rows)"
for pat in ("data/organizations_*.csv", "data/sites_*.csv", "data/evidence_*.csv", "scripts/atlas.py", "scripts/derive_last_activity.py", "scripts/regions.py"):
    for p in sorted(ROOT.glob(pat)):
        blob = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE}:{p.relative_to(ROOT)}"], capture_output=True).stdout
        lines.append(f"{hashlib.sha256(blob).hexdigest()}  {p.relative_to(ROOT)}")
for p in sorted((K.LAKE / "atlas").glob("*.parquet")) + [K.LAKE / "MANIFEST.csv"]:
    lines.append(f"{sha(p)}  lake/{p.relative_to(K.LAKE)}")
used = {r["src_path_under_raw"].split("!")[0] for f in ("packet.csv",) for r in csv.DictReader(open(HERE / f, encoding="utf-8"))}
for line in open(K.LAKE.parent.parent / "raw" / "MANIFEST.sha256", encoding="utf-8"):
    s, _, p = line.rstrip("\n").partition("  ")
    p = p[2:] if p.startswith("./") else p
    if p in used:
        lines.append(f"{s}  raw/{p}")
(HERE / "INPUTS.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(len(lines), "lines")
