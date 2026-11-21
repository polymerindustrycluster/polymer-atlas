#!/usr/bin/env python3
"""Task check for the FRS lane (exit 1 on any failure). From the repo root:

    python3 tasks/evidence-frs-sites-2026-11-20/check.py

- the packet is one existence row per witnessed ledger site (ADDR+NAME, CITY+NAME) plus an address row for each
  tier-C/U ADDR+NAME site, and nothing for tier-B addresses (a C-strength address on a tier-B site is a V-25 error);
- applied + withheld = packet; every applied row is Codex-SOUND on a site whose existence Codex accepted, and its notes
  record the owner's Codex-only waiver;
- applied rows are `registry` class at the class ceiling (existence supports_B, address supports_C, supports_U on tier
  U), cite a registry ID that the Atlas links to that site, carry the dated fetch marker, no URL and no '@';
- applied IDs run contiguously from EVD-410477, each present once tree-wide, in its home shard, equal to applied.csv;
- no evidenced site is still listed in V-65 (tier A/B) or V-68 (tier C/U).
"""
import csv, glob, json, re, sys
from collections import Counter
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parents[1]
START = 410477
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))
fail = []
ledger, packet, applied, withheld = rd(T / "ledger.csv"), rd(T / "packet_rows.csv"), rd(T / "applied.csv"), rd(T / "withheld.csv")
codex = {}
for p in sorted(T.glob("review_codex_*.json")):
    t = p.read_text(encoding="utf-8")
    codex.update({(v["record_id"], v["claim_type"]): v["verdict"] for v in json.loads(t[t.index("{"):t.rindex("}") + 1])["verdicts"]})
tier = {l["site_id"]: l["tier"] for l in ledger}
want = Counter()
for l in ledger:
    if l["verdict"] in ("ADDR+NAME", "CITY+NAME"):
        want[(l["site_id"], "existence")] += 1
        if l["verdict"] == "ADDR+NAME" and l["tier"] in ("C", "U"):
            want[(l["site_id"], "address")] += 1
if Counter((p["record_id"], p["claim_type"]) for p in packet) != want:
    fail.append("packet is not existence per witnessed site + address per tier-C/U street match")
if len(applied) + len(withheld) != len(packet):
    fail.append(f"applied {len(applied)} + withheld {len(withheld)} != packet {len(packet)}")
links = {(r["site_id"], r["registry_id"]) for r in rd(ROOT / "data" / "registry_links.csv") if r["registry"] == "FRS"}
bad = {s for (s, c) in want if c == "existence" and codex.get((s, c)) != "SOUND"}
ceiling = {"existence": "supports_B", "address": "supports_C"}
for x in applied:
    k = (x["record_id"], x["claim_type"])
    if codex.get(k) != "SOUND" or x["record_id"] in bad:
        fail.append(f"{x['evidence_id']} applied without Codex SOUND on a SOUND-existence site")
    if "owner's waiver of 2026-11-20" not in x["notes"] or "fetched 2026-11-20" not in x["notes"]:
        fail.append(f"{x['evidence_id']} notes lack the waiver or the dated fetch marker")
    eff = "supports_U" if tier[x["record_id"]] == "U" else ceiling[x["claim_type"]]
    if x["source_class"] != "registry" or x["tier_effect"] != eff:
        fail.append(f"{x['evidence_id']} is {x['source_class']}/{x['tier_effect']}, expected registry/{eff}")
    rid = re.search(r"EPA FRS registry ID (\d+)", x["source_ref"])
    if not rid or (x["record_id"], rid[1]) not in links:
        fail.append(f"{x['evidence_id']} cites an FRS ID the Atlas does not link to {x['record_id']}")
    if re.match(r"https?://", x["source_ref"].strip()) or "@" in x["claim_detail"] + x["notes"]:
        fail.append(f"{x['evidence_id']} cites a URL or carries an '@'")
ids = [x["evidence_id"] for x in applied]
if ids != [f"EVD-{n:06d}" for n in range(START, START + len(ids))]:
    fail.append(f"applied IDs are not EVD-{START:06d}.. contiguous")
tree, rows = Counter(), {}
for f in glob.glob(str(ROOT / "data" / "evidence_*.csv")):
    for r in rd(f):
        tree[r["evidence_id"]] += 1
        rows[r["evidence_id"]] = (Path(f).name, r)
for x in applied:
    if tree[x["evidence_id"]] != 1:
        fail.append(f"{x['evidence_id']} appears {tree[x['evidence_id']]} times tree-wide"); continue
    fname, r = rows[x["evidence_id"]]
    if fname != f"evidence_sites_{x['_shard']}.csv" or any(r[c] != x[c] for c in r):
        fail.append(f"{x['evidence_id']} is not in its home shard or differs from applied.csv")
base = json.loads((ROOT / "scripts" / "validate_debt_baseline.json").read_text(encoding="utf-8"))["rules"]
done = {x["record_id"] for x in applied}
left = sorted(done & set(base["V-65"])) + sorted(k for k in base["V-68"] if k.startswith("sites:") and k.split(":")[1] in done)
if left:
    fail.append(f"evidenced sites still baselined: {', '.join(left[:10])}")
print("\n".join(fail) or f"OK: {len(applied)} applied rows on {len(done)} sites, {len(withheld)} withheld; "
      f"packet {len(packet)} rows on {sum(1 for k in want if k[1] == 'existence')} sites")
sys.exit(1 if fail else 0)
