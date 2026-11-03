#!/usr/bin/env python3
"""Evidence repair, integration step: append a fresher evidence row for each weak row whose replacement source
passed the integrator's raw check. Evidence is append-only (SCHEMA 4.13): the weak row is never edited; the new
row answers it.

    python3 tasks/evidence-repair-2026-11-03/build_repair.py --data-dir data [--apply --i-am-the-integrator]

Inputs, in this folder:
- checked.csv: the population, with the deterministic check result for each weak row;
- replacements.csv: lane FOUND rows, with the integrator's raw-page check in column `raw` (yes / no / unfetchable).
A row is minted only when raw == yes. tier_effect is the weak row's tier_effect, capped by the new source class's
ceiling (own_site / government_filing: supports_A; press: supports_B). CONTRADICTED and NONE_FOUND outcomes are
reported in holds.csv and never minted. EVD ids start above EVD-022275, the highest id used by open PRs (#37).
"""
import argparse, csv, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "census-gap-people-2026-11-03"))
from build_integration import append_rows, read  # noqa: E402

TODAY, BY, EVD_FLOOR = "2026-11-03", "claude-code evidence-repair-2026-11-03", 22275
CEIL = {"own_site": "supports_A", "government_filing": "supports_A", "press": "supports_B"}
RANK = {"supports_C": 1, "supports_B": 2, "supports_A": 3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    weak = {r["evidence_id"]: r for r in read(HERE / "checked.csv")}
    ev = [r for f in sorted(data.glob("evidence*.csv")) for r in read(f)]
    evd = max([EVD_FLOOR] + [int(e["evidence_id"][4:]) for e in ev if re.fullmatch(r"EVD-\d+", e["evidence_id"])]) + 1
    tag = {}
    for table in ("sites", "organizations"):
        for f in sorted(data.glob(f"{table}_*.csv")):
            for r in read(f):
                tag[r["site_id" if table == "sites" else "org_id"]] = f"evidence_{table}_{f.stem.split('_', 1)[1]}.csv"
    for r in read(data / "ecosystem.csv"):
        tag[r["org_id"]] = "evidence_ecosystem.csv"
    out, holds = {}, []
    for r in read(HERE / "replacements.csv"):
        w = weak[r["evidence_id"]]
        if r["outcome"] != "FOUND" or r["raw"] != "yes" or r["source_class"] not in CEIL:
            holds.append({"evidence_id": r["evidence_id"], "record_id": w["record_id"], "claim_type": w["claim_type"],
                          "outcome": r["outcome"], "raw": r.get("raw", ""), "note": (r.get("note") or "")[:200]})
            continue
        te = w["tier_effect"] if w["tier_effect"] in RANK else "supports_B"
        if RANK[te] > RANK[CEIL[r["source_class"]]]:
            te = CEIL[r["source_class"]]
        row = {"evidence_id": f"EVD-{evd:06d}", "record_table": w["record_table"], "record_id": w["record_id"],
               "claim_type": w["claim_type"], "claim_detail": f"\"{r['quote'].strip()}\"",
               "source_class": r["source_class"], "source_ref": r["source_url"].strip(), "observed_date": TODAY,
               "tier_effect": te, "created_by": BY,
               "notes": f"answers {w['evidence_id']} (its cited page, re-fetched {TODAY}, no longer shows the claim: {w['check_detail'] or w['check']})"}
        evd += 1
        out.setdefault(tag[w["record_id"]], []).append(row)
    n = sum(len(v) for v in out.values())
    with open(HERE / "holds.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=["evidence_id", "record_id", "claim_type", "outcome", "raw", "note"], lineterminator="\n")
        wr.writeheader(); wr.writerows(holds)
    with open(HERE / "evidence_append.csv", "w", newline="", encoding="utf-8") as fh:
        rows = [x for v in out.values() for x in v]
        wr = csv.DictWriter(fh, fieldnames=list(ev[0].keys()), extrasaction="ignore", lineterminator="\n"); wr.writeheader(); wr.writerows(rows)
    print(f"new evidence rows {n} across {len(out)} shards;", Counter(x["claim_type"] for v in out.values() for x in v),
          "| held", len(holds), Counter((h["outcome"], h["raw"]) for h in holds))
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        for name, rows in out.items():
            if not (data / name).exists():
                sys.exit(f"{name} missing")
            append_rows(data / name, rows)
        print("applied")


if __name__ == "__main__":
    main()
