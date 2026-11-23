"""Seeded stratified 200-note sample (100 org, 100 site rows; every tier); seed 20261122."""
import random, csv, sys
from load import load
QUOTA = {"organizations": {"A": 21, "B": 52, "C": 22, "U": 5}, "sites": {"A": 14, "B": 47, "C": 33, "U": 6}}
def sample():
    out = []
    for t, k in (("organizations", "org_id"), ("sites", "site_id")):
        rows = [r for r in load(t) if r["notes"].strip()]
        rng = random.Random(20261122)
        for tier, n in QUOTA[t].items():
            pool = sorted((r for r in rows if r["verification_tier"] == tier), key=lambda r: r[k])
            for r in rng.sample(pool, n):
                out.append({"table": t, "id": r[k], "tier": tier, "file": r["_file"], "line": r["_line"], "created_by": r["created_by"], "notes": r["notes"]})
    return out
if __name__ == "__main__":
    s = sample()
    a, b = int(sys.argv[1]), int(sys.argv[2])
    for i, r in enumerate(s[a:b], a):
        print(f"#{i} {r['id']} {r['tier']} | {r['notes']}\n")
