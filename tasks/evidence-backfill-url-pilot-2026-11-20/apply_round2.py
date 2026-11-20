#!/usr/bin/env python3
"""Round 2 (owner rulings 2026-11-20 on contact-page address and short-name existence): append the withheld rows that
BOTH families judged SOUND under the amended brief (rereview2_brief.md). A row's record must also have a SOUND
existence row, from round 1 (every review) or round 2 (both families). IDs continue after applied.csv.

    python apply_round2.py <atlas repo>      (reads and writes this task folder; appends to data/evidence_* shards)
"""
import csv, json, sys
from pathlib import Path

atlas = Path(sys.argv[1])
T = Path(__file__).resolve().parent
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig", newline="")))
FIELDS = ["evidence_id", "record_table", "record_id", "claim_type", "claim_detail", "source_class", "source_ref",
          "observed_date", "tier_effect", "created_by", "notes"]


def verdicts(name):
    t = (T / name).read_text(encoding="utf-8")
    return {(v["record_id"], v["claim_type"]): v["verdict"] for v in json.loads(t[t.index("{"):t.rindex("}") + 1])["verdicts"]}


r2 = [verdicts("rereview2_codex.json"), verdicts("rereview2_agy.json")]
applied1 = rd(T / "applied.csv")
asked = {(w["record_id"], w["claim_type"]) for w in rd(T / "withheld.csv")}
for v in r2:
    assert set(v) <= asked, "round-2 verdict for a row that was not withheld"
ok2 = lambda k: all(v.get(k) == "SOUND" for v in r2)
exists_ok = {a["record_id"] for a in applied1 if a["claim_type"] == "existence"} | {k[0] for k in asked if k[1] == "existence" and ok2(k)}
shard = {s["record_id"]: s["shard"] for s in rd(T / "sample.csv")}
n = int(applied1[-1]["evidence_id"].split("-")[1]) + 1
out = []
for r in rd(T / "packet_rows.csv"):
    k = (r["record_id"], r["claim_type"])
    if k in asked and ok2(k) and k[0] in exists_ok:
        out.append({"evidence_id": f"EVD-{n:06d}", **{f: r[f] for f in FIELDS[1:]}, "_shard": shard[k[0]]}); n += 1
for x in out:
    with open(atlas / "data" / f"evidence_{x['record_table']}_{x['_shard']}.csv", "a", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerow([x[f] for f in FIELDS])
if out:
    with open(T / "applied_round2.csv", "w", encoding="utf-8", newline="") as fh:
        d = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n"); d.writeheader(); d.writerows(out)
print(f"round 2 applied {len(out)} rows ({out[0]['evidence_id'] if out else '-'}..{out[-1]['evidence_id'] if out else '-'}) "
      f"on {len({x['record_id'] for x in out})} records")
