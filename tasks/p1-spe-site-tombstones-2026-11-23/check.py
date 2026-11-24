#!/usr/bin/env python3
"""Replay retirement of two SPE site records represented in ecosystem."""
import argparse
import io
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHARD = "data/sites_OH.csv"
SECTIONS = {
    "SITE-000091": ("ORG-000091", "Akron"),
    "SITE-000163": ("ORG-000163", "Cleveland"),
}

lib = runpy.run_path(str(HERE.parent / "p1-tempid-notes-all-2026-11-23/check.py"))
git, read, require, csv_bytes = (lib[name] for name in ("git", "read", "require", "csv_bytes"))


def replay(base):
    all_ecosystem = read(git("show", f"{base}:data/ecosystem.csv"))
    expected_org_ids = {org for org, _ in SECTIONS.values()}
    ecosystem = [r for r in all_ecosystem if r["org_id"] in expected_org_ids]
    require(len(ecosystem) == len({r["org_id"] for r in ecosystem}) == 2, "Expected both existing ecosystem sections")
    by_id = {r["org_id"]: r for r in ecosystem}
    for org, city in SECTIONS.values():
        row = by_id[org]
        require(row["legal_name"] == f"Society of Plastics Engineers - {city} Section"
                and row["state"] == "OH" and row["city"] == city
                and row["ecosystem_subtype"] == "trade_association" and row["status"] == "active",
                f"{org}: underlying ecosystem association differs")

    before = git("show", f"{base}:{SHARD}")
    lines = list(io.StringIO(before.decode(), newline=""))
    reader = read(before)
    end, output, seen = 1, [lines[0]], set()
    ending = "\r\n" if lines[0].endswith("\r\n") else "\n"
    for row in reader:
        start, end = end, reader.line_num
        sid = row["site_id"]
        if sid not in SECTIONS:
            output.extend(lines[start:end])
            continue
        org, city = SECTIONS[sid]
        require(sid not in seen and row["org_id"] == org and row["city"] == city and row["state"] == "OH"
                and row["site_name"] == f"{by_id[org]['legal_name']} — {city}"
                and row["verification_tier"] == "U" and row["operating_status"] == "active",
                f"{sid}: held site differs")
        seen.add(sid)
        row["operating_status"] = "closed"
        note = (f"2026-11-23 site record retired under the SPE ecosystem ruling in DECISIONS.md. "
                f"The section remains active in ecosystem as {org}. This records a classification correction.")
        row["notes"] = f"{row['notes']} {note}" if row["notes"] else note
        output.append(csv_bytes(reader.fieldnames, ([row[c] for c in reader.fieldnames],),
                                include_header=False, ending=ending).decode())
    require(seen == SECTIONS.keys(), "Expected both site rows")
    keys = ("table", "record_id", "field", "verdict", "evidence_id")
    claims = csv_bytes(keys, (("sites", sid, field, "corrected", "") for sid in sorted(seen)
                             for field in ("notes", "operating_status")))
    return before, "".join(output).encode(), claims


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--at", default="HEAD")
    parser.add_argument("--base")
    parser.add_argument("--apply-backup", type=Path)
    args = parser.parse_args()
    base = args.base or git("merge-base", args.at, "origin/main").decode().strip()
    before, after, claims = replay(base)
    ledger = HERE / "CLAIMS_CHECKED.csv"
    if args.apply_backup:
        require((ROOT / SHARD).read_bytes() == before, "Current site shard differs from base")
        args.apply_backup.mkdir(parents=True, exist_ok=True)
        backup = args.apply_backup / Path(SHARD).name
        require(not backup.exists() or backup.read_bytes() == before, "Existing backup differs from base")
        backup.write_bytes(before)
        (ROOT / SHARD).write_bytes(after)
        ledger.write_bytes(claims)
    else:
        require(git("diff", "--name-only", base, args.at, "--", "data/").decode().splitlines() == [SHARD],
                "Canonical diff contains other paths")
        require(git("show", f"{args.at}:{SHARD}") == after, "Applied site bytes differ")
        require(git("show", f"{args.at}:{ledger.relative_to(ROOT)}") == claims, "Claims ledger differs")
    print("PASS: two existing ecosystem entries confirmed, two site tombstones, four corrected cells")


if __name__ == "__main__":
    main()
