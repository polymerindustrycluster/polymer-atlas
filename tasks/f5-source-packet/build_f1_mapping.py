#!/usr/bin/env python3
"""Build the authoritative record-level TRI-class mapping for F1 (blind audit 8).

Population: every ORG/SITE created in integration passes 20-25 (from each pass's
id_allocation.csv, the file that drove the pushes).
Origin: the packet whose design key (source_key) the creation allocated from.
TRI class: worklist.csv priority_group of the creating facility's TRIFID
(P0=0 forward link, P1=1 held Tier-1 missing site, P2=2 held missing site,
P3=3 unheld w/ Tier-1 signal, P4=4 unheld single facility).
Orgs: class of the creating facility set (site designs in the same wave whose
org_ref is the org design key); primary = lowest P number; mixed flagged.
Non-TRI origins in the mixed passes are labelled, never silently dropped:
pass 20 = SC wave 1 + candidate queue Q01-Q02; pass 21 = Dot PR #6 packet.
"""
import csv, json, os
from collections import Counter, defaultdict

STG = "/home/hatch/workspace/polymer-atlas-staging/working"
WAVES = {20: "p001-p006", 21: "p007-p012", 22: "p013-p018", 23: "p019-p024", 24: "p025-p030", 25: "p031-p036"}

worklist = {}
for r in csv.DictReader(open(f"{STG}/tri-national/worklist.csv")):
    worklist[r["trifid"]] = (f"P{r['priority_group']}", r["packet_id"])

def load_designs(path):
    if not os.path.exists(path):
        return {}
    return {r[k]: r for r in csv.DictReader(open(path)) for k in [list(r.keys())[0]]}

out, unresolved = [], []
for p in range(20, 26):
    alloc = list(csv.DictReader(open(f"{STG}/integration-pass-{p}/id_allocation.csv")))
    creates = [r for r in alloc if r["class"] in ("org_create", "site_create")  # org_create_watch is a MARKER row on an org_create allocation, never a separate creation (v1 bug: double-counted 5 watch orgs)
               or (p == 25 and r["class"] == "create")]
    wave_dir = f"{STG}/tri-national/wave-{WAVES[p]}"
    tri_sites = {r["site_key"]: r for r in csv.DictReader(open(f"{wave_dir}/site_designs.csv"))}
    tri_orgs = {r["org_key"]: r for r in csv.DictReader(open(f"{wave_dir}/org_designs.csv"))}
    # org -> creating trifids (via this wave's site designs)
    org_trifids = defaultdict(set)
    for s in tri_sites.values():
        if s.get("tri_trifid"):
            org_trifids[s["org_ref"]].add(s["tri_trifid"])
    extra = {}
    if p == 20:
        for label, d in (("SC_WAVE_1", f"{STG}/sc-wave-1"), ("CANDIDATE_QUEUE_Q01_Q02", f"{STG}/candidate-queue/wave-q01-q02")):
            for kind, fn in (("site", "site_designs.csv"), ("org", "org_designs.csv")):
                for r in csv.DictReader(open(f"{d}/{fn}")):
                    extra[r["site_key"] if kind == "site" else r["org_key"]] = label
    if p == 21:
        for r in csv.DictReader(open(f"{STG}/integration-pass-21/id_allocation.csv")):
            pass  # pr6 creates identified below via non-wave keys + journal check
    for r in creates:
        rid, key = r["allocated_id"], r["source_key"]
        rtype = "ORG" if rid.startswith("ORG") else "SITE"
        row = {"record_id": rid, "record_type": rtype, "creation_pass": p,
               "origin": "", "tri_class": "", "packet_id": "", "trifids": "", "mixed_class": ""}
        if rtype == "SITE" and key in tri_sites:
            tf = tri_sites[key].get("tri_trifid", "")
            row["origin"] = "TRI"
            if tf in worklist:
                row["tri_class"], row["packet_id"] = worklist[tf]
                row["trifids"] = tf
            else:
                row["tri_class"] = "TRI_TRIFID_NOT_IN_WORKLIST"; row["trifids"] = tf
        elif rtype == "ORG" and key in tri_orgs:
            tfs = sorted(org_trifids.get(key, set()))
            classes = sorted({worklist[t][0] for t in tfs if t in worklist})
            row["origin"] = "TRI"; row["trifids"] = ";".join(tfs)
            row["packet_id"] = ";".join(sorted({worklist[t][1] for t in tfs if t in worklist}))
            if classes:
                row["tri_class"] = classes[0]
                row["mixed_class"] = "yes" if len(classes) > 1 else ""
                if len(classes) > 1:
                    row["tri_class"] = classes[0] + " (also " + ",".join(classes[1:]) + ")"
            else:
                row["tri_class"] = "TRI_ORG_NO_CREATING_SITE_DESIGN"
        elif key in extra:
            row["origin"] = "NOT_TRI"; row["tri_class"] = "NOT_TRI"; row["packet_id"] = extra[key]
        elif p == 21:
            row["origin"] = "NOT_TRI"; row["tri_class"] = "NOT_TRI"; row["packet_id"] = "DOT_PR6_PACKET (non-wave key; journal-verified below)"
        else:
            row["origin"] = "UNRESOLVED"; row["tri_class"] = "UNRESOLVED"
            unresolved.append((p, rid, key))
        out.append(row)

with open(f"{STG}/followup-queue/f1_record_tri_class_mapping.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["record_id", "record_type", "creation_pass", "origin", "tri_class", "packet_id", "trifids", "mixed_class"])
    w.writeheader(); w.writerows(out)
print("rows:", len(out))
print("by pass/type:", Counter((r["creation_pass"], r["record_type"]) for r in out))
print("origin:", Counter(r["origin"] for r in out))
print("tri_class:", Counter(r["tri_class"] for r in out))
print("UNRESOLVED:", unresolved[:20], "count:", len(unresolved))
