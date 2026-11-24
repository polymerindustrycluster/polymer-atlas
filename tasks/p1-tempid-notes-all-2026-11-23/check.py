#!/usr/bin/env python3
"""Apply or verify the approved temp-ID notes against the application base."""
import argparse
from collections import Counter
import csv
import hashlib
import io
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKET = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist" / HERE.name
PIN = "77e5b6f4b7a10eded4d052bec03a26d4a0290710"
KEYS = {"organizations": "org_id", "sites": "site_id"}
SHARD = re.compile(r"data/(organizations|sites)_[A-Z]+\.csv")
TEMP = re.compile(r"\bNEW(?:SITE)?:")
CLAIMS = ("table", "record_id", "field", "verdict", "evidence_id")
HOLDS = ("table", "record_id", "field", "origin", "reason")


def require(ok, reason):
    if not ok:
        raise SystemExit(reason)


def git(*args):
    return subprocess.check_output(("git", *args), cwd=ROOT)


def read(blob):
    return csv.DictReader(io.StringIO(blob.decode(), newline=""))


def csv_bytes(header, rows, *, include_header=True, ending="\n"):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator=ending)
    if include_header:
        writer.writerow(header)
    writer.writerows(rows)
    return output.getvalue().encode()


def replay(base, manifest, packet):
    require(manifest == (packet / "SHA256SUMS").read_bytes(), "Sealed packet manifest differs")
    hashes = dict(line.split("  ", 1)[::-1] for line in manifest.decode().splitlines())
    inputs = {}
    for name in ("edits.csv", "holds.csv"):
        source = (packet / name).read_bytes()
        require(hashlib.sha256(source).hexdigest() == hashes[name], f"{name}: sealed hash differs")
        inputs[name] = list(read(source))
    edits, holds = {}, {}
    for name, out in (("edits.csv", edits), ("holds.csv", holds)):
        for row in inputs[name]:
            key = (row["table"], row["record_id"])
            require(key[0] in KEYS and row["field"] == "notes" and key not in out, f"{key}: invalid packet key")
            out[key] = row
    require(len(edits) == 3380 and len(holds) == 29 and not edits.keys() & holds.keys(), "Packet counts or disjointness differ")
    require(all(row["old"] != row["new"] and not TEMP.search(row["new"]) for row in edits.values()),
            "Packet contains a no-op or a remaining temporary ID")

    paths, matched, applied, drift, tiers = {}, set(), [], {}, Counter()
    relevant = edits.keys() | holds.keys()
    for path in git("ls-tree", "-r", "--name-only", base, "data/").decode().splitlines():
        match = SHARD.fullmatch(path)
        if not match:
            continue
        table = match[1]
        body = git("show", f"{base}:{path}")
        lines = list(io.StringIO(body.decode(), newline=""))
        rows = read(body)
        ended, output = 1, [lines[0]]
        ending = "\r\n" if lines[0].endswith("\r\n") else "\n"
        touched = False
        for row in rows:
            start, ended = ended, rows.line_num
            key = table, row[KEYS[table]]
            if key in relevant:
                require(key not in matched, f"{key}: duplicate record on base")
                matched.add(key)
            edit = edits.get(key)
            if edit and row["notes"] == edit["old"]:
                row["notes"] = edit["new"]
                output.append(csv_bytes(rows.fieldnames, ([row[c] for c in rows.fieldnames],),
                                        include_header=False, ending=ending).decode())
                applied.append(key)
                tiers[row["verification_tier"]] += 1
                touched = True
            else:
                output.extend(lines[start:ended])
                if edit:
                    drift[key] = "Current notes differ from the sealed old cell. Review against current main."
        if touched:
            paths[path] = body, "".join(output).encode()
    for key in edits.keys() - matched:
        drift[key] = "Record absent from current main. Review before attempting the edit."
    require(len(applied) + len(drift) == len(edits), "Edit dispositions do not reconcile")
    queue = {key: ("packet", row["reason"]) for key, row in holds.items()}
    queue.update({key: ("base-drift", reason) for key, reason in drift.items()})
    artifacts = {
        "CLAIMS_CHECKED.csv": csv_bytes(CLAIMS, ((*key, "notes", "corrected", "") for key in sorted(applied))),
        "OPEN_QUEUE.csv": csv_bytes(HOLDS, ((*key, "notes", *queue[key]) for key in sorted(queue))),
    }
    summary = (f"{len(applied)} notes updated in {len(paths)} CSV files, "
               f"{len(holds)} packet holds and {len(drift)} base-drift holds. "
               f"Tables {dict(sorted(Counter(key[0] for key in applied).items()))}, tiers {dict(sorted(tiers.items()))}.")
    return paths, artifacts, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--at", default="HEAD")
    parser.add_argument("--base")
    parser.add_argument("--packet", type=Path, default=PACKET)
    parser.add_argument("--apply-backup", type=Path)
    args = parser.parse_args()
    base = args.base or git("merge-base", args.at, "origin/main").decode().strip()
    git("merge-base", "--is-ancestor", PIN, base)
    if args.apply_backup:
        manifest = (HERE / "PACKET.sha256").read_bytes()
    else:
        manifest = git("show", f"{args.at}:{HERE.relative_to(ROOT)}/PACKET.sha256")
    paths, artifacts, summary = replay(base, manifest, args.packet)

    if args.apply_backup:
        args.apply_backup.mkdir(parents=True, exist_ok=True)
        for path, (before, after) in paths.items():
            require((ROOT / path).read_bytes() == before, f"{path}: worktree differs from the application base")
            backup = args.apply_backup / Path(path).name
            require(not backup.exists() or backup.read_bytes() == before, f"{path}: existing backup differs")
            backup.write_bytes(before)
        for path, (_, after) in paths.items():
            (ROOT / path).write_bytes(after)
        for name, body in artifacts.items():
            (HERE / name).write_bytes(body)
    else:
        delta = set(git("diff", "--name-only", base, args.at, "--", "data/").decode().splitlines())
        require(delta == paths.keys(), "Canonical changed path set differs")
        for path, (_, after) in paths.items():
            require(git("show", f"{args.at}:{path}") == after, f"{path}: applied bytes differ")
        for name, body in artifacts.items():
            require(git("show", f"{args.at}:{HERE.relative_to(ROOT)}/{name}") == body, f"{name}: ledger differs")
    print("PASS:", summary)


if __name__ == "__main__":
    main()
