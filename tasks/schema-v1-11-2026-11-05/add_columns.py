#!/usr/bin/env python3
"""Schema v1.11 data step (2026-11-05): append the three optional organization columns, empty, to every organization
shard, and create the empty §4.22 evidence archive table. No existing value changes; each shard keeps its line endings.

    python3 tasks/schema-v1-11-2026-11-05/add_columns.py --data-dir data
"""
import argparse, csv, io
from pathlib import Path

NEW = ["newsroom_url", "newsroom_feed_url", "linkedin_url"]
ARCHIVE = ["evidence_id", "archive_ref", "captured_at", "created_by"]

ap = argparse.ArgumentParser()
ap.add_argument("--data-dir", required=True)
data = Path(ap.parse_args().data_dir)
n_rows = n_files = 0
for p in sorted(data.glob("organizations_*.csv")):
    raw = p.read_bytes()
    eol = "\r\n" if b"\r\n" in raw[:4096] else "\n"
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"), newline="")))
    head = next(csv.reader(io.StringIO(raw.decode("utf-8"), newline="")))
    if set(NEW) <= set(head):
        continue  # already applied: the step is idempotent
    assert not set(NEW) & set(head), f"{p.name}: partially applied"
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=head + NEW, lineterminator=eol)
    w.writeheader()
    for r in rows:
        w.writerow({**r, **{c: "" for c in NEW}})
    p.write_bytes(buf.getvalue().encode("utf-8"))
    n_rows += len(rows); n_files += 1
arc = data / "archive_links.csv"  # outside the evidence_*.csv shard pattern on purpose
if not arc.exists():
    arc.write_bytes((",".join(ARCHIVE) + "\n").encode("utf-8"))
print(f"{n_files} organization shards, {n_rows} rows gained {len(NEW)} empty columns; archive_links.csv present")
