#!/usr/bin/env python3
"""Task check for the Form 5500 lane (exit 1 on any failure). From the repo root:

    python3 tasks/evidence-form5500-orgs-2026-11-20/check.py            # before review: packet checks only

- ledger and bundle carry only whitelisted business fields (no signer, phone or care-of data);
- the packet is one existence row per witnessed ledger org (EIN+NAME, NAME+CITY), at most one address and one liveness
  row each; every row cites the ledger's ACK_ID; liveness rows carry the plan-year end as observed_date, an end on or
  after 2024-11-20, active participants > 0, and no final filing;
- once applied: applied + withheld = packet; every applied row is SOUND in every family that reviewed (Codex always,
  Antigravity when present) on an org whose existence was accepted, and carries the waiver note iff Codex reviewed alone;
  rows are government_filing at supports_A (supports_U on tier U); IDs run contiguously from EVD-410701, once tree-wide,
  in the org's home shard, equal to applied.csv; no evidenced org is still listed in V-65 or V-68.
"""
import csv, glob, json, re, sys
from collections import Counter
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parents[1]
START, LIVE_FROM = 410701, "2024-11-20"
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))
fail = []
LEDGER_COLS = ["org_id", "tier", "verdict", "legal_name", "hq_city", "hq_state", "atlas_eins", "filing_eins", "sponsor", "dba",
               "form", "plan_year_end", "active", "final", "loc_city", "loc_state", "mail_city", "mail_state", "ack_id"]
ledger, packet = rd(T / "ledger.csv"), rd(T / "packet_rows.csv")
if list(ledger[0]) != LEDGER_COLS:
    fail.append(f"ledger columns are not the whitelist: {list(ledger[0])}")
bundle_text = (T / "review_bundle.json").read_text(encoding="utf-8")
if re.search(r"SIGNED|PHONE|CARE_OF|signer|phone", bundle_text):
    fail.append("review bundle carries a signer/phone/care-of field")
led = {l["org_id"]: l for l in ledger}
wit = {o for o, l in led.items() if l["verdict"] in ("EIN+NAME", "NAME+CITY")}
c = Counter((p["record_id"], p["claim_type"]) for p in packet)
if {o for o, ct in c if ct == "existence"} != wit or any(v > 1 for v in c.values()) or {o for o, _ in c} != wit:
    fail.append("packet is not one existence row per witnessed org with at most one address and one liveness row")
for p in packet:
    l = led[p["record_id"]]
    if f"ACK_ID {l['ack_id']} " not in p["source_ref"] or re.match(r"https?://", p["source_ref"]) or "@" in p["claim_detail"] + p["notes"]:
        fail.append(f"{p['record_id']} {p['claim_type']} does not cite the ledger ACK_ID by name, or carries a URL or '@'")
    if p["claim_type"] == "liveness" and not (p["observed_date"] == l["plan_year_end"] >= LIVE_FROM and int(l["active"] or 0) > 0 and l["final"] != "1"):
        fail.append(f"{p['record_id']} liveness row breaks ruling 8 (end {l['plan_year_end']}, active {l['active']}, final {l['final']})")

if (T / "applied.csv").exists():
    applied, withheld = rd(T / "applied.csv"), rd(T / "withheld.csv")
    fams = {}
    for name in ("codex", "agy"):
        for p in sorted(T.glob(f"review_{name}_*.json")):
            t = p.read_text(encoding="utf-8")
            fams.setdefault(name, {}).update({(v["record_id"], v["claim_type"]): v["verdict"] for v in json.loads(t[t.index("{"):t.rindex("}") + 1])["verdicts"]})
    if "codex" not in fams:
        fail.append("applied without Codex verdicts")
    if len(applied) + len(withheld) != len(packet):
        fail.append(f"applied {len(applied)} + withheld {len(withheld)} != packet {len(packet)}")
    sound = lambda k: all(v.get(k) == "SOUND" for v in fams.values())
    bad = {o for o in wit if not sound((o, "existence"))}
    for x in applied:
        if not sound((x["record_id"], x["claim_type"])) or x["record_id"] in bad:
            fail.append(f"{x['evidence_id']} applied without SOUND from every reviewing family on an accepted org")
        if ("owner's waiver of 2026-11-20" in x["notes"]) == ("agy" in fams):
            fail.append(f"{x['evidence_id']} waiver note does not match the families that reviewed")
        eff = "supports_U" if led[x["record_id"]]["tier"] == "U" else "supports_A"
        if x["source_class"] != "government_filing" or x["tier_effect"] != eff:
            fail.append(f"{x['evidence_id']} is {x['source_class']}/{x['tier_effect']}, expected government_filing/{eff}")
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
        if fname != f"evidence_organizations_{x['_shard']}.csv" or any(r[k] != x[k] for k in r):
            fail.append(f"{x['evidence_id']} is not in its home shard or differs from applied.csv")
    base = json.loads((ROOT / "scripts" / "validate_debt_baseline.json").read_text(encoding="utf-8"))["rules"]
    done = {x["record_id"] for x in applied}
    left = sorted(done & set(base["V-65"])) + sorted(k for k in base["V-68"] if k.startswith("organizations:") and k.split(":")[1] in done)
    if left:
        fail.append(f"evidenced orgs still baselined: {', '.join(left[:10])}")
    summary = f"OK: {len(applied)} applied rows on {len(done)} orgs ({'+'.join(sorted(fams))}), {len(withheld)} withheld; "
else:
    summary = "OK (not yet reviewed or applied): "
print("\n".join(fail) or summary + f"packet {len(packet)} rows on {len(wit)} orgs ({dict(Counter(p['claim_type'] for p in packet))})")
sys.exit(1 if fail else 0)
