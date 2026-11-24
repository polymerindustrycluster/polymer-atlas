"""Seeded 25-record canary (seed 20261122): 9 rows forced by a code-read marker (one per marker, so the dependency check inspects positives),
then seeded random fill stratified over tiers and both tables. Persons excluded (DESIGN §8)."""
import random, re, json
from corpus import run
from person_scan import scan
orgs, sites = run()
rows = [r for r in orgs + sites if r["notes"].strip() and not scan(r["notes"])]
rng = random.Random(20261122)
MARK = [  # (label, table, regex on notes)
    ("settling-fact", "organizations", r"Settling fact:"), ("settling-fact", "sites", r"Settling fact:"),
    ("parcel-queue", "sites", r"parcel candidate queue"), ("tombstone", "sites", r"tombstoned as duplicate of SITE-\d{6}"),
    ("WARN", "sites", r"\bWARN\b"), ("CERT-SITE", "sites", r"CERT-SITE"), ("CAPABILITY-QUEUE", "sites", r"CAPABILITY-QUEUE"),
    ("FEI", "organizations", r"\bFEI\W{0,3}\d{6,10}\b"), ("street-only-in-notes", "sites", None)]
chosen = {}
for label, tbl, rx in MARK:
    if rx is None:
        pool = [r for r in rows if r["_table"] == tbl and not r["street_address"].strip() and re.search(r"Street[^:]{0,40}:\s*\d", r["notes"])]
    else:
        pool = [r for r in rows if r["_table"] == tbl and re.search(rx, r["notes"])]
    pool = sorted((r for r in pool if r["_id"] not in chosen), key=lambda r: r["_id"])
    r = rng.choice(pool); chosen[r["_id"]] = (r, label)
need = {("organizations", "A"): 2, ("organizations", "B"): 2, ("organizations", "C"): 1, ("sites", "B"): 2, ("sites", "C"): 2, ("sites", "A"): 1, ("sites", "U"): 1, ("organizations", "U"): 1, ("sites", "B2"): 1, ("organizations", "B2"): 1, ("sites", "C2"): 1, ("organizations", "C2"): 1}
for (tbl, tier), n in need.items():
    t = tier[0]
    pool = sorted((r for r in rows if r["_table"] == tbl and r["verification_tier"] == t and r["_id"] not in chosen), key=lambda r: r["_id"])
    for r in rng.sample(pool, n if len(chosen) + n <= 25 else 25 - len(chosen)): chosen[r["_id"]] = (r, "random-" + t)
    if len(chosen) >= 25: break
ids = sorted(chosen)
print(len(ids), ids)
json.dump({i: chosen[i][1] for i in ids}, open("canary_ids.json", "w"), indent=1)
