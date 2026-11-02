#!/usr/bin/env python3
"""Build hash-checked edits.csv packets for the ruled, mechanical subset of the
2026-11-01 validator debt (V-45 synonyms, V-47 VERIFIED provenance rows).

Inputs: tasks/validator-debt-2026-11-01/v45_site_type_proposals.csv and
v47_naics_proposals.csv (owner battery 2026-11-01, ruled "all as recommended";
R1 site_type, R4 three-point confidence). Every proposal is re-checked against
the current data/ before it becomes an edit; anything that fails a check is
written to holds.csv instead. Output format is the one
scripts/apply_p1_crm_scrub.py applies (--packet-dir), all-or-nothing with
old-value hashes.

    python3 tasks/validator-debt-apply-2026-11-02/build_edits.py --data-dir <pre-pass data dir>

Run it against the pre-pass tree (e.g. `git archive 46366c2 data | tar -x -C /tmp/pre`).
Against the post-pass tree every proposal reports drift and the packets come out empty.
"""
import argparse, csv, hashlib, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_ap = argparse.ArgumentParser()
_ap.add_argument("--data-dir", required=True)
DATA = Path(_ap.parse_args().data_dir)
SRC = ROOT / "tasks" / "validator-debt-2026-11-01"
OUT = Path(__file__).resolve().parent
SITE_TYPES = {"manufacturing_plant", "hq_only", "hq_and_plant", "rd_center", "lab_testing", "warehouse_distribution",
              "sales_office", "tool_shop", "recycling_facility", "training_center", "campus", "virtual_incubator",
              "office_other", "service_repair"}
SOURCE_TYPES = {"company_disclosed", "government_filing", "directory_assigned", "researcher_inferred"}
CONF = {"high", "medium", "low"}
COLS = ["file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"]
HOLD_COLS = ["rule", "row_id", "file", "reason"]


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load(fname):
    with open(DATA / fname, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        key = rd.fieldnames[0]
        return {r[key]: r for r in rd}


tables = {}
def row(fname, rid):
    if fname not in tables:
        tables[fname] = load(fname)
    return tables[fname].get(rid)


with open(DATA / "evidence.csv", newline="", encoding="utf-8") as fh:
    EVD = {r["evidence_id"]: r for r in csv.DictReader(fh)}


def write(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def v45():
    edits, holds = [], []
    with open(SRC / "v45_site_type_proposals.csv", newline="", encoding="utf-8") as fh:
        for p in csv.DictReader(fh):
            if p["decision_class"] != "synonym":
                continue
            r = row(p["shard"], p["site_id"])
            if r is None:
                holds.append({"rule": "V-45", "row_id": p["site_id"], "file": p["shard"], "reason": "row not found in that shard"}); continue
            cur = r["site_type"]
            if cur != p["current_site_type"]:
                holds.append({"rule": "V-45", "row_id": p["site_id"], "file": p["shard"], "reason": f"drift: current {cur!r} != proposal {p['current_site_type']!r}"}); continue
            if p["proposed_site_type"] not in SITE_TYPES:
                holds.append({"rule": "V-45", "row_id": p["site_id"], "file": p["shard"], "reason": f"proposed {p['proposed_site_type']!r} not in enum"}); continue
            edits.append({"file": p["shard"], "row_id": p["site_id"], "column": "site_type", "old_sha256": sha(cur),
                          "new_value": p["proposed_site_type"], "edit_class": "V45_SYNONYM",
                          "rationale": f"{cur} -> {p['proposed_site_type']}: {p['rationale']} (battery 2026-11-01 R1)"})
    return edits, holds


def v47():
    edits, holds = [], []
    with open(SRC / "v47_naics_proposals.csv", newline="", encoding="utf-8") as fh:
        for p in csv.DictReader(fh):
            rid, fn = p["record_id"], p["shard"]
            if p["verdict"] != "VERIFIED":
                continue
            r = row(fn, rid)
            if r is None:
                holds.append({"rule": "V-47", "row_id": rid, "file": fn, "reason": "row not found in that shard"}); continue
            st, cf = r["naics_primary_source_type"], r["naics_confidence"]
            if st != p["current_source_type"] or cf != p["current_confidence"]:
                holds.append({"rule": "V-47", "row_id": rid, "file": fn, "reason": f"drift: current ({st!r},{cf!r}) != proposal"}); continue
            nst, ncf = p["proposed_source_type"], p["proposed_confidence"]
            if nst not in SOURCE_TYPES or ncf not in CONF:
                holds.append({"rule": "V-47", "row_id": rid, "file": fn, "reason": f"proposal ({nst!r},{ncf!r}) outside vocabulary"}); continue
            if nst == "government_filing":
                ids = re.findall(r"EVD-\d{6}", p["basis"])
                code = (r.get("naics_primary") or "").strip()
                ok = [e for e in (EVD.get(i) for i in ids) if e and e["record_id"] == rid and e["claim_type"] == "code"
                      and e["source_class"] == "government_filing"]
                if not ok:
                    holds.append({"rule": "V-47", "row_id": rid, "file": fn, "reason": f"no cited government_filing code evidence row for this record ({','.join(ids) or 'none cited'})"}); continue
                codes = {c for e in ok for c in re.findall(r"\b\d{6}\b", e["claim_detail"])}
                if code not in codes:
                    holds.append({"rule": "V-47", "row_id": rid, "file": fn, "reason": f"naics_primary {code!r} not printed in the cited code evidence ({sorted(codes) or 'no 6-digit code printed'})"}); continue
                if ncf == "high" and not any("TRI" in e["source_ref"] or "TRI" in e["claim_detail"] for e in ok):
                    holds.append({"rule": "V-47", "row_id": rid, "file": fn, "reason": "high proposed but cited code row is not a TRI facility record"}); continue
                why = f"{ok[0]['evidence_id']} states NAICS {code} ({ok[0]['source_ref'][:80]})"
                cls = "V47_GOVFILING_CONFIDENCE" if st == nst else "V47_GOVFILING_SOURCE_AND_CONFIDENCE"
            else:
                if st != nst:
                    holds.append({"rule": "V-47", "row_id": rid, "file": fn, "reason": "source-type change on a non-filing row is not mechanical"}); continue
                why = p["basis"][:160]
                cls = "V47_CONFIDENCE_ROUNDING" if cf in ("low-medium", "medium-high") else "V47_CONFIDENCE_SET"
            if st != nst:
                edits.append({"file": fn, "row_id": rid, "column": "naics_primary_source_type", "old_sha256": sha(st),
                              "new_value": nst, "edit_class": cls, "rationale": why})
            if cf != ncf:
                edits.append({"file": fn, "row_id": rid, "column": "naics_confidence", "old_sha256": sha(cf),
                              "new_value": ncf, "edit_class": cls, "rationale": why})
    return edits, holds


if __name__ == "__main__":
    for name, fn in (("v45", v45), ("v47", v47)):
        edits, holds = fn()
        d = OUT / name
        d.mkdir(exist_ok=True)
        write(d / "edits.csv", COLS, edits)
        write(d / "holds.csv", HOLD_COLS, holds)
        print(f"{name}: {len(edits)} edits over {len({e['row_id'] for e in edits})} rows; {len(holds)} holds")
