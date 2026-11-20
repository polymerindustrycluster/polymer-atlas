#!/usr/bin/env python3
"""Task check for the OSHA lane (exit 1 on any failure). From the repo root:

    python3 tasks/evidence-osha-sites-2026-11-20/check.py

- the packet is exactly three rows (existence, address, liveness) per ADDR+NAME ledger site;
- applied + withheld = packet; every applied row is SOUND in both families, and no applied row sits on a site whose
  existence row either family rejected;
- applied IDs run contiguously from EVD-410106, each present once tree-wide, in its home shard, equal to applied.csv;
- every applied row cites the filing by name (no URL: V-66 does not apply) and carries no '@';
- no evidenced site is still listed in V-65 (tier A/B) or V-68 (tier C/U).
"""
import csv, glob, json, re, sys
from collections import Counter
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parents[1]
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))
fail = []
ledger, packet, applied, withheld = rd(T / "ledger.csv"), rd(T / "packet_rows.csv"), rd(T / "applied.csv"), rd(T / "withheld.csv")


def verdicts(pattern):
    out = {}
    for p in sorted(T.glob(pattern)):
        t = p.read_text(encoding="utf-8")
        out.update({(v["record_id"], v["claim_type"]): v["verdict"] for v in json.loads(t[t.index("{"):t.rindex("}") + 1])["verdicts"]})
    return out


codex, agy = verdicts("review_codex_*.json"), verdicts("review_agy_*.json")
witnessed = {l["site_id"] for l in ledger if l["verdict"] == "ADDR+NAME"}
if Counter((p["record_id"], p["claim_type"]) for p in packet) != Counter((s, c) for s in witnessed for c in ("existence", "address", "liveness")):
    fail.append("packet is not exactly existence+address+liveness per ADDR+NAME site")
if len(applied) + len(withheld) != len(packet):
    fail.append(f"applied {len(applied)} + withheld {len(withheld)} != packet {len(packet)}")
bad = {s for s in witnessed if codex.get((s, "existence")) != "SOUND" or agy.get((s, "existence")) != "SOUND"}
for x in applied:
    k = (x["record_id"], x["claim_type"])
    if codex.get(k) != "SOUND" or agy.get(k) != "SOUND":
        fail.append(f"{x['evidence_id']} applied without SOUND from both families")
    if x["record_id"] in bad:
        fail.append(f"{x['evidence_id']} applied on a site whose existence row was rejected")
    if re.match(r"https?://", x["source_ref"].strip()) or "@" in x["claim_detail"] + x["notes"]:
        fail.append(f"{x['evidence_id']} cites a URL or carries an '@'")
ids = [x["evidence_id"] for x in applied]
if ids != [f"EVD-{n:06d}" for n in range(410106, 410106 + len(ids))]:
    fail.append("applied IDs are not EVD-410106.. contiguous")
tree, rows = Counter(), {}
for f in glob.glob(str(ROOT / "data" / "evidence_*.csv")):
    for r in rd(f):
        tree[r["evidence_id"]] += 1
        rows[r["evidence_id"]] = (Path(f).name, r)
for x in applied:
    if tree[x["evidence_id"]] != 1:
        fail.append(f"{x['evidence_id']} appears {tree[x['evidence_id']]} times tree-wide"); continue
    fname, r = rows[x["evidence_id"]]
    if fname != f"evidence_sites_{x['_shard']}.csv":
        fail.append(f"{x['evidence_id']} is in {fname}, not its home shard")
    if any(r[c] != x[c] for c in r):
        fail.append(f"{x['evidence_id']} differs from applied.csv")
# Part 3 (owner waiver 2026-11-20, "Codex-only for now"): rows withheld as awaiting a second family, applied on Codex alone.
part3 = rd(T / "applied_part3.csv") if (T / "applied_part3.csv").exists() else []
waiting = {(w["record_id"], w["claim_type"]) for w in withheld if w["held"].startswith("awaiting review")}
bad3 = {s for s, c in waiting if c == "existence" and codex.get((s, c)) != "SOUND"}
ids3 = [x["evidence_id"] for x in part3]
if part3 and ids3 != [f"EVD-{n:06d}" for n in range(410357, 410357 + len(ids3))]:
    fail.append("part-3 IDs are not EVD-410357.. contiguous")
for x in part3:
    k = (x["record_id"], x["claim_type"])
    if k not in waiting or codex.get(k) != "SOUND" or x["record_id"] in bad3:
        fail.append(f"{x['evidence_id']} part-3 row was not a Codex-SOUND row awaiting review on a SOUND-existence site")
    if tree[x["evidence_id"]] != 1:
        fail.append(f"{x['evidence_id']} appears {tree[x['evidence_id']]} times tree-wide"); continue
    fname, r = rows[x["evidence_id"]]
    if fname != f"evidence_sites_{x['_shard']}.csv" or any(r[c] != x[c] for c in r):
        fail.append(f"{x['evidence_id']} is not in its home shard or differs from applied_part3.csv")
applied = applied + part3
base = json.loads((ROOT / "scripts" / "validate_debt_baseline.json").read_text(encoding="utf-8"))["rules"]
done = {x["record_id"] for x in applied}
left = sorted(done & set(base["V-65"])) + sorted(k for k in base["V-68"] if k.startswith("sites:") and k.split(":")[1] in done)
if left:
    fail.append(f"evidenced sites still baselined: {', '.join(left[:10])}")
print("\n".join(fail) or f"OK: {len(applied)} applied rows on {len(done)} sites, {len(withheld)} withheld; "
      f"packet {len(packet)} rows on {len(witnessed)} sites")
sys.exit(1 if fail else 0)
