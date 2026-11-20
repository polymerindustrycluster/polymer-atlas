#!/usr/bin/env python3
"""Task check: the pilot's applied rows are exactly the both-SOUND rows, present once in data/, and the funnel reconciles.

    python tasks/evidence-backfill-url-pilot-2026-11-20/check.py      (from the repo root; exit 1 on any failure)
"""
import csv, glob, json, sys
from collections import Counter
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parents[1]
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig", newline="")))


def verdicts(name):
    t = (T / name).read_text(encoding="utf-8")
    return {(v["record_id"], v["claim_type"]): v["verdict"] for v in json.loads(t[t.index("{"):t.rindex("}") + 1])["verdicts"]}


fail = []
sample, ledger, packet = rd(T / "sample.csv"), rd(T / "ledger.csv"), rd(T / "packet_rows.csv")
applied, withheld = rd(T / "applied.csv"), rd(T / "withheld.csv")
full = [verdicts("review_codex.json"), verdicts("review_agy.json")]  # each covers every packet row
re_ = [verdicts(n) for n in ("rereview_codex.json", "rereview_agy.json")]  # windowed re-review of rows quoted past char 6000
sound = lambda k: all(v.get(k) == "SOUND" for v in full) and all(v[k] == "SOUND" for v in re_ if k in v)
if len(ledger) != len(sample) or {l["record_id"] for l in ledger} != {s["record_id"] for s in sample}:
    fail.append("ledger does not cover the sample one-to-one")
if len(applied) + len(withheld) != len(packet):
    fail.append(f"applied {len(applied)} + withheld {len(withheld)} != packet {len(packet)}")
for k in {(r["record_id"], r["claim_type"]) for r in packet}:
    if any(k not in v for v in full):
        fail.append(f"unreviewed packet row {k}")
for a in applied:
    k = (a["record_id"], a["claim_type"])
    if a["claim_type"] == "liveness":
        fail.append(f"{a['evidence_id']} applies a liveness row; liveness is held for an owner ruling")
    if not sound(k):
        fail.append(f"{a['evidence_id']} applied without SOUND from every review")
    if not sound((k[0], "existence")):
        fail.append(f"{a['evidence_id']} applied on a record whose existence row was not SOUND in every review")
# round 2 (owner rulings 2026-11-20): withheld rows both families judged SOUND under the amended brief
applied2 = rd(T / "applied_round2.csv") if (T / "applied_round2.csv").exists() else []
r2 = [verdicts("rereview2_codex.json"), verdicts("rereview2_agy.json")] if applied2 else []
held = {(w["record_id"], w["claim_type"]) for w in withheld}
ok_exist = {a["record_id"] for a in applied if a["claim_type"] == "existence"} | \
           {k[0] for k in held if k[1] == "existence" and r2 and all(v.get(k) == "SOUND" for v in r2)}
for a in applied2:
    k = (a["record_id"], a["claim_type"])
    if k not in held or a["claim_type"] == "liveness":
        fail.append(f"{a['evidence_id']} round-2 row was not a withheld existence/address row")
    if not all(v.get(k) == "SOUND" for v in r2):
        fail.append(f"{a['evidence_id']} round-2 row lacks SOUND from both families")
    if k[0] not in ok_exist:
        fail.append(f"{a['evidence_id']} round-2 row on a record with no SOUND existence row")
applied = applied + applied2
ids = [a["evidence_id"] for a in applied]
if ids != [f"EVD-{n:06d}" for n in range(410001, 410001 + len(ids))]:
    fail.append("applied IDs are not EVD-410001.. contiguous")
tree = Counter()
rows = {}
for f in glob.glob(str(ROOT / "data" / "evidence_*.csv")):
    for r in rd(f):
        tree[r["evidence_id"]] += 1
        rows[r["evidence_id"]] = (Path(f).name, r)
for a in applied:
    if tree[a["evidence_id"]] != 1:
        fail.append(f"{a['evidence_id']} appears {tree[a['evidence_id']]} times tree-wide")
        continue
    fname, r = rows[a["evidence_id"]]
    if fname != f"evidence_{a['record_table']}_{a['_shard']}.csv":
        fail.append(f"{a['evidence_id']} is in {fname}, not its home shard")
    if any(r[c] != a[c] for c in r):
        fail.append(f"{a['evidence_id']} differs from applied.csv")
print("\n".join(fail) or f"OK: {len(applied)} applied rows ({len(applied2)} in round 2), {len(withheld) - len(applied2)} withheld, "
      f"{len(ledger)} sampled records reconcile")
sys.exit(1 if fail else 0)
