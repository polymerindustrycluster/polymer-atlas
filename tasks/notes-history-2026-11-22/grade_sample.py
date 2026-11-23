"""Seeded samples for hand grading. usage: grade_sample.py MOVE|UNLISTED seed n"""
import random, sys
from corpus import run
orgs, sites = run()
kind, seed, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
if kind == "MOVE":
    pool = [(r["_id"], i, p["text"].strip()) for r in orgs + sites for i, p in enumerate(r["_parts"]) if p["disp"] == "MOVE" and p["kind"] not in ("pipeline-lead",) or (p["disp"] == "MOVE" and len(p["text"]) > 120)]
else:
    pool = [(r["_id"], i, p["text"].strip()) for r in orgs + sites for i, p in enumerate(r["_parts"]) if p["kind"] == "plain-unlisted"]
pool = sorted(set(pool)); random.Random(seed).shuffle(pool)
for k, (rid, i, t) in enumerate(pool[:n]): print(f"{k}\t{rid}\t{i}\t{t[:300]}")
