#!/usr/bin/env python3
"""Backfill `size_band` evidence rows for the employee-size bands applied on 2026-11-02 (owner ruling B-BAND (a),
2026-11-03, tasks/OWNER_BATTERY_2026-11-03.md).

    python3 tasks/size-band-evidence-2026-11-03/build_evidence.py --data-dir data [--apply --i-am-the-integrator]

One evidence row per APPLY/fill row of tasks/integration-ready-oh-pa-2026-11-02/band_updates.csv, traced to its
source packet row (packet_refs -> tasks/<packet>-2026-11-01/band_proposals.csv:<line>). A row is written only when
the record still carries the applied band in its band field; anything else is held (holds.csv). Rows go to the
record's own evidence shard (evidence_<sites|organizations>_<TAG>.csv). source_class government_filing,
tier_effect supports_B (the B-BAND ceiling). EVD ids start above EVD-020279, the highest id used by open PRs
(#26: 020270-020271; #35: 020272-020279).
"""
import argparse, csv, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = HERE.parent
sys.path.insert(0, str(TASKS / "census-gap-people-2026-11-03"))
from build_integration import append_rows, read  # noqa: E402

BY, OBSERVED, EVD_FLOOR = "claude-code size-band-evidence-2026-11-03", "2026-11-01", 20279
PACKETS = {"osha-ita": "osha-ita-2026-11-01", "osha-spine": "osha-spine-2026-11-01", "form5500-spine": "form5500-spine-2026-11-01"}
FIELD = {"sites": "employee_band_site", "organizations": "employee_band_ohio"}


def source_ref(kind, p):
    if kind == "osha-ita":
        return f"OSHA ITA Form 300A {p['period_covered']}, establishment_id {p['establishment_id']} (https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data)"
    if kind == "osha-spine":
        return f"https://www.osha.gov/ords/imis/establishment.inspection_detail?id={p['inspection_activity_nr']}"
    return p["source_ref"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    where = {}  # record_id -> (table, tag, row)
    for table in ("sites", "organizations"):
        for f in sorted(data.glob(f"{table}_*.csv")):
            tag = f.stem.split("_", 1)[1]
            for r in read(f):
                where[r["site_id" if table == "sites" else "org_id"]] = (table, tag, r)
    ev = [r for f in sorted(data.glob("evidence*.csv")) for r in read(f)]
    have = {(e["record_id"], e["claim_type"]) for e in ev}
    evd = max([EVD_FLOOR] + [int(e["evidence_id"][4:]) for e in ev if re.fullmatch(r"EVD-\d+", e["evidence_id"])]) + 1
    packet_rows = {k: list(csv.reader(open(TASKS / d / "band_proposals.csv", newline="", encoding="utf-8")))
                   for k, d in PACKETS.items()}  # ":<n>" = CSV record n, header = 1

    out, holds = {}, []
    for u in read(TASKS / "integration-ready-oh-pa-2026-11-02" / "band_updates.csv"):
        if (u["status"], u["action"]) != ("APPLY", "fill"):
            continue
        rid, table = u["record_id"], u["record_table"]
        kind = {"ita": "osha-ita", "inspection": "osha-spine", "form5500": "form5500-spine"}[u["pick_source"]]
        ref = next(x for x in u["packet_refs"].split("|") if x.startswith(kind + "/"))  # refs list every source seen
        line = int(ref.split(":")[1])
        p = dict(zip(packet_rows[kind][0], packet_rows[kind][line - 1]))
        loc = where.get(rid)
        why = []
        if not loc: why.append("record not found")
        elif loc[2].get(FIELD[table], "") != u["pick_band"]:
            why.append(f"record band {loc[2].get(FIELD[table], '')!r} != applied {u['pick_band']!r}")
        if rid not in (p.get("site_id"), p.get("org_id")): why.append("packet row does not match record")
        if (rid, "size_band") in have: why.append("size_band evidence already present")
        if why:
            holds.append({"record_id": rid, "packet_refs": u["packet_refs"], "reason": "; ".join(why)}); continue
        _, tag, _ = loc
        row = {"evidence_id": f"EVD-{evd:06d}", "record_table": table, "record_id": rid, "claim_type": "size_band",
               "claim_detail": f"{FIELD[table]}={u['pick_band']}: {p['basis']} (band only, not a headcount)",
               "source_class": "government_filing", "source_ref": source_ref(kind, p), "observed_date": OBSERVED,
               "tier_effect": "supports_B", "created_by": BY, "notes": f"backfill of 2026-11-02 band; packet {u['packet_refs']}"}
        evd += 1
        out.setdefault(f"evidence_{table}_{tag}.csv", []).append(row)
    n = sum(len(v) for v in out.values())
    with open(HERE / "holds.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["record_id", "packet_refs", "reason"], lineterminator="\n"); w.writeheader(); w.writerows(holds)
    print(f"evidence rows {n} across {len(out)} shards; held {len(holds)}", Counter(h["reason"].split(" '")[0] for h in holds))
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        for name, rows in out.items():
            if not (data / name).exists():
                sys.exit(f"{name} missing: shard must exist before appending")
            append_rows(data / name, rows)
        print("applied")


if __name__ == "__main__":
    main()
