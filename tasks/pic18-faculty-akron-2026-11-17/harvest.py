#!/usr/bin/env python3
"""Fetch each Gate-A-listing-pass candidate's own profile page (link on a stored listing page); write profiles.csv (name, url, sha, http)."""
import csv, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from frame import build, norm
from fetch import fetch
cands, seen = [], set()
for r in build():
    if r["gate_a_listing"] != "pass" or r["held_at_akron"] or r["unit"].startswith("SPSPE-"): continue
    k = norm(r["name"])
    if k in seen: continue
    seen.add(k); cands.append(r)
out = []
for r in cands:
    sha, code, n = fetch(r["profile_url"], f"link on {r['unit']} listing page {r['listing_sha'][:8]}")
    out.append({"name": r["name"], "unit": r["unit"], "profile_url": r["profile_url"], "sha": sha or "", "http": code})
    print(r["name"], code, n, flush=True)
from fetch import P
with open(P + "/profiles.csv", "w", newline="") as f:  # real URLs: persist only, never committed
    w = csv.DictWriter(f, ["name", "unit", "profile_url", "sha", "http"]); w.writeheader(); w.writerows(out)
