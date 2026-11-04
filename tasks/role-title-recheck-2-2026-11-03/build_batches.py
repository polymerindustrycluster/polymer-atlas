#!/usr/bin/env python3
"""Role-title re-check, wave 2 (2026-11-03): lane inputs for the people whose role_as_published is still narrative.

    python3 tasks/role-title-recheck-2-2026-11-03/build_batches.py --data-dir data
        -> lanes/batch<N>.csv (25 rows each), nrel_held.csv

Who: the 214 holds of tasks/atlas-cleanup-2026-11-03/holds.csv on role_as_published, minus the 45 rank
disagreements (settled by tasks/role-rank-recheck-2026-11-03), plus that re-check's 27 KEEP rows, whose rank now
stands but whose title is still narrative. People whose cited pages are all on nrel.gov are listed in nrel_held.csv
instead: nrel.gov stopped resolving on 2026-11-03 and their URLs are re-pointed by the NREL packet first.
Stdlib only.
"""
import argparse, csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COLS = ["person_id", "full_name", "institution_org_id", "role", "role_as_published", "public_profile_url", "sources"]


def read(p):
    with open(p, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(ROOT / "data"))
    args = ap.parse_args()
    people = {p["person_id"]: p for p in read(Path(args.data_dir) / "people.csv")}
    holds = read(ROOT / "tasks" / "atlas-cleanup-2026-11-03" / "holds.csv")
    rank = [r for f in sorted((ROOT / "tasks" / "role-rank-recheck-2026-11-03" / "lanes").glob("batch*_out.csv"))
            for r in read(f)]
    ids = [h["record"] for h in holds if h["item"] == "role_as_published" and not h["reason"].startswith("page rank differs")]
    ids += [r["person_id"] for r in rank if r["verdict"] == "KEEP"]
    ids = [i for i in dict.fromkeys(ids) if i in people]  # removed duplicates drop out
    rows, nrel = [], []
    for i in ids:
        p = people[i]
        urls = [u for u in [p["public_profile_url"]] + p["sources"].split(";") if u.strip()]
        (nrel if urls and all("nrel.gov" in u for u in urls) else rows).append({c: p[c] for c in COLS})
    assert len({r["person_id"] for r in rows}) == len(rows)
    (HERE / "lanes").mkdir(exist_ok=True)
    for n in range(0, len(rows), 25):
        with open(HERE / "lanes" / f"batch{n // 25 + 1}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n"); w.writeheader(); w.writerows(rows[n:n + 25])
    with open(HERE / "nrel_held.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n"); w.writeheader(); w.writerows(nrel)
    print(f"people needing a title: {len(ids)}; to lanes: {len(rows)} in {(len(rows) + 24) // 25} batches; "
          f"NREL-only (held for the NREL packet): {len(nrel)}")


if __name__ == "__main__":
    main()
