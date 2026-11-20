#!/usr/bin/env python3
"""Task check for the TRI lane (exit 1 on any failure). From the repo root:

    python3 tasks/evidence-tri-filings-2026-11-20/check.py

- the ledger covers the frame one-to-one, and the packet is exactly its WITNESS / WITNESS_PARENT rows;
- applied + withheld = packet, and every applied row is SOUND in both review families;
- applied IDs run contiguously from EVD-410026, each present once tree-wide, in its home shard, equal to applied.csv;
- every applied row cites the filing by name (no URL, so V-66 archive-at-capture does not apply) and carries no
  personal contact data (no '@', no phone-like digit run);
- no applied record is still listed in V-65's baseline once it carries a supports_A row.
"""
import csv, glob, json, re, sys
from collections import Counter
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parents[1]
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))
fail = []
frame, ledger, packet = rd(T / "frame.csv"), rd(T / "ledger.csv"), rd(T / "packet_rows.csv")
applied, withheld = rd(T / "applied.csv"), rd(T / "withheld.csv")


def verdicts(*names):
    out = {}
    for n in names:
        t = (T / n).read_text(encoding="utf-8")
        out.update({(v["record_id"], v["claim_type"]): v["verdict"] for v in json.loads(t[t.index("{"):t.rindex("}") + 1])["verdicts"]})
    return out


codex, agy = verdicts("review_codex.json"), verdicts("review_agy_1.json", "review_agy_2.json")
if [r["org_id"] for r in ledger] != [r["org_id"] for r in frame]:
    fail.append("ledger does not cover the frame one-to-one")
if {r["record_id"] for r in packet} != {l["org_id"] for l in ledger if l["verdict"] in ("WITNESS", "WITNESS_PARENT")}:
    fail.append("packet is not exactly the ledger's witnessed records")
if len(applied) + len(withheld) != len(packet):
    fail.append(f"applied {len(applied)} + withheld {len(withheld)} != packet {len(packet)}")
for a in applied:
    k = (a["record_id"], a["claim_type"])
    if codex.get(k) != "SOUND" or agy.get(k) != "SOUND":
        fail.append(f"{a['evidence_id']} applied without SOUND from both families")
    if re.match(r"https?://", a["source_ref"].strip()):
        fail.append(f"{a['evidence_id']} cites a URL; this lane cites the filing by name")
    if re.search(r"@|\d{3}\D{0,2}\d{3}\D?\d{4}", a["claim_detail"] + " " + a["notes"]):
        fail.append(f"{a['evidence_id']} carries something that looks like personal contact data")
ids = [a["evidence_id"] for a in applied]
if ids != [f"EVD-{n:06d}" for n in range(410026, 410026 + len(ids))]:
    fail.append("applied IDs are not EVD-410026.. contiguous")
tree, rows = Counter(), {}
for f in glob.glob(str(ROOT / "data" / "evidence_*.csv")):
    for r in rd(f):
        tree[r["evidence_id"]] += 1
        rows[r["evidence_id"]] = (Path(f).name, r)
for a in applied:
    if tree[a["evidence_id"]] != 1:
        fail.append(f"{a['evidence_id']} appears {tree[a['evidence_id']]} times tree-wide"); continue
    fname, r = rows[a["evidence_id"]]
    if fname != f"evidence_organizations_{a['_shard']}.csv":
        fail.append(f"{a['evidence_id']} is in {fname}, not its home shard")
    if any(r[c] != a[c] for c in r):
        fail.append(f"{a['evidence_id']} differs from applied.csv")
v65 = set(json.loads((ROOT / "scripts" / "validate_debt_baseline.json").read_text(encoding="utf-8"))["rules"]["V-65"])
left = sorted(a["record_id"] for a in applied if a["tier_effect"] == "supports_A" and a["record_id"] in v65)
if left:
    fail.append(f"evidenced records still in the V-65 baseline: {', '.join(left)}")
print("\n".join(fail) or f"OK: {len(applied)} applied rows on {len({a['record_id'] for a in applied})} organizations, "
      f"{len(withheld)} withheld; frame {len(frame)}, packet {len(packet)}")
sys.exit(1 if fail else 0)
