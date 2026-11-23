#!/usr/bin/env python3
"""Reconcile the pre-ruling filter table (corporate suffix accepted, filing year within 5 years of 2026: 87 organizations)
with the rebuilt packet, site by site. Re-runs build.py's own evaluate() under the pre-ruling rules (old corporate-word set
with `north`/`america` as single words, age applied AFTER selection to the chosen fill, no window test), then compares.
usage: reconcile_87_to_97.py --cache DIR --out reconcile.csv"""
import argparse, csv, sys
from collections import defaultdict, Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B

ap = argparse.ArgumentParser(); ap.add_argument("--cache", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
orgs, sites = B.load_atlas(); fr, _, _ = B.frame(orgs, sites)
active = [s for s in sites if s["operating_status"] == "active"]; active_n = Counter(s["org_id"] for s in active); by_street = defaultdict(list)
for s in active:
    if s["street_address"].strip(): s["_held"] = B.held_names(s, orgs); by_street[B.street_key(s["street_address"])].append(s)
ix = {k: B.index(B.unify(B.rd(f"{a.cache}/{f}.csv"), k)) for k, f in (("ita", "ita_oh"), ("insp", "insp_oh"), ("f5500", "f5500_oh"))}
packet = {r["site_id"]: r for r in csv.DictReader(open(Path(__file__).resolve().parent / "packet.csv"))}
holds = {r["site_id"]: r for r in csv.DictReader(open(Path(__file__).resolve().parent / "holds.csv"))}
def run(corp, cutoff, window):
    B.CORP = corp; B.CUTOFF = cutoff; B.WINDOW_LO = window; out = {}
    for s in fr:
        if not s["street_address"].strip() or not B.same_street(s["street_address"], s["street_address"]): continue
        held = B.held_names(s, orgs); s["_held"] = held
        pk = {k: B.classify(s, held, ix[k])[0] for k in ix}; near = {k: w for k in ix if (w := B.would_be_band(k, B.classify(s, held, ix[k])[1]))}
        out[s["site_id"]] = B.evaluate(s, "suffix", pk, active_n, by_street, near)
    return out
NEW_CORP = set(B.CORP)
OLD_CORP = {"inc", "llc", "corp", "corporation", "co", "company", "ltd", "lp", "holdings", "us", "usa", "north", "america", "group", "incorporated"}
old = run(OLD_CORP, "0000-00-00", "0000-00-00")
old87 = {sid: r[1] for sid, r in old.items() if r[0] == "fill" and 2026 - r[1]["year"] <= 5}
org_of = {s["site_id"]: s["org_id"] for s in fr}
orgs_old = {org_of[s] for s in old87}
print("pre-ruling reproduction: sites", len(old87), "organizations", len(orgs_old))
# classify each difference
rows = []
for sid in sorted(set(old87) | set(packet)):
    o, n = old87.get(sid), packet.get(sid)
    if o and n: continue
    if n and not o:
        why = "entered"; oo = old.get(sid)
        if oo and oo[0] == "fill": why = "entered: pre-ruling chosen fill was older than 5 years and was dropped after selection; a recent source now fills (precedence falling through)"
        elif oo and oo[0] == "hold": why = f"entered: pre-ruling hold {oo[1]} no longer applies once stale filings are ignored"
        else: why = "entered: other (see candidates_all.csv)"
        rows.append((sid, org_of[sid], "entered", n["source"], n["band"], why))
    else:
        h = holds.get(sid)
        rows.append((sid, org_of[sid], "left", o["source"], o["band"], f"left: now held {h['reason'] if h else '?'}"))
with open(a.out, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["site_id", "org_id", "direction", "source", "band", "reason"]); w.writerows(rows)
print(Counter((r[2], r[5].split(":")[0] + ":" + r[5].split(":")[1][:60]) for r in rows))
print("packet organizations", len({p["org_id"] for p in packet.values()}), "entered orgs", len({r[1] for r in rows if r[2] == "entered"}), "left orgs", len({r[1] for r in rows if r[2] == "left"}))
