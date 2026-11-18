#!/usr/bin/env python3
"""Frame for the national capability batch b01: writes slice.csv (100 sites) from the pinned base tree (base.txt).

A site qualifies when it is: active; outside Ohio (the PIC-18 lanes own Ohio); ring_primary 1-2; BOTH processes and
materials blank; owned by an active organization with a website; and the organization's only active Atlas site, so a
company page's process statement can be tied to this one establishment. 100 are drawn with a fixed seed.

    python3 tasks/capability-national-b01-2026-11-18/frame.py
"""
import csv, io, random, subprocess
from collections import Counter
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parents[1]
BASE = (T / "base.txt").read_text().strip()
SEED, N = 20261118, 100


def base_rows(prefix):
    names = subprocess.check_output(["git", "ls-tree", "--name-only", BASE, "data/"], cwd=ROOT, text=True).split()
    out = []
    for f in names:
        if f.startswith(prefix) and not f.endswith("_all.csv"):
            out += list(csv.DictReader(io.StringIO(subprocess.check_output(["git", "show", f"{BASE}:{f}"], cwd=ROOT,
                                                                            text=True, encoding="utf-8"))))
    return out


def frame():
    sites, orgs = base_rows("data/sites_"), {o["org_id"]: o for o in base_rows("data/organizations_")}
    active = [s for s in sites if s["operating_status"] == "active"]
    per_org = Counter(s["org_id"] for s in active)
    pool = sorted((s for s in active
                   if s["state"] != "OH" and s["ring_primary"] in ("1", "2")
                   and not s["processes"].strip() and not s["materials"].strip()
                   and per_org[s["org_id"]] == 1
                   and orgs.get(s["org_id"], {}).get("status") == "active"
                   and orgs[s["org_id"]].get("website", "").strip()), key=lambda s: s["site_id"])
    pick = sorted(random.Random(SEED).sample(pool, N), key=lambda s: s["site_id"])
    return pool, [{"site_id": s["site_id"], "org_id": s["org_id"], "state": s["state"], "city": s["city"],
                   "street_address": s["street_address"], "verification_tier": s["verification_tier"],
                   "site_name": s["site_name"], "website": orgs[s["org_id"]]["website"].strip()} for s in pick]


if __name__ == "__main__":
    pool, rows = frame()
    assert len({r["site_id"] for r in rows}) == N and len({r["org_id"] for r in rows}) == N
    with open(T / "slice.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print(f"pool {len(pool)}; slice {len(rows)}; states {Counter(r['state'] for r in rows).most_common(6)}; "
          f"tiers {Counter(r['verification_tier'] for r in rows)}")
