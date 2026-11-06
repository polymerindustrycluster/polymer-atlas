#!/usr/bin/env python3
"""Append the owner-supplied v1.12 crosswalk, preserving all existing CSV bytes.

Run from the repo root: python3 tasks/schema-v1-12/add_crosswalk.py
"""
import argparse
import csv
import io
import re
from pathlib import Path

TASK = Path(__file__).resolve().parent
EVENTS = TASK.parent.parent / "data" / "events.csv"
COLUMN = "pic_events_slug"


def append_crosswalk(raw, mapping):
    lines = raw.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(raw.decode("utf-8"), newline=""))
    header = next(reader)
    assert COLUMN not in header, "crosswalk column already present"
    values = [COLUMN]
    ends = [reader.line_num]
    ids = []
    for row in reader:
        assert len(row) == len(header), "malformed events row"
        event_id = row[header.index("event_id")]
        ids.append(event_id)
        values.append(mapping[event_id])
        ends.append(reader.line_num)
    assert len(ids) == len(set(ids)), "duplicate event IDs"
    assert set(ids) == set(mapping), "crosswalk and events IDs differ"
    chunks, original, start = [], [], 0
    for index, (end, value) in enumerate(zip(ends, values)):
        assert index == 0 or not value or all(
            re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug) for slug in value.split(";")
        ), f"malformed crosswalk: {value!r}"
        record = b"".join(lines[start:end])
        body = record.rstrip(b"\r\n")
        eol = record[len(body):]
        suffix = b"," + value.encode("ascii")
        chunks.append(body + suffix + eol)
        original.append(chunks[-1][:len(body)] + eol)
        start = end
    assert b"".join(original) == raw, "existing CSV bytes changed or skipped"
    result = b"".join(chunks)
    parsed = list(csv.reader(io.StringIO(result.decode("utf-8"), newline="")))
    before = list(csv.reader(io.StringIO(raw.decode("utf-8"), newline="")))
    assert [row[:-1] for row in parsed] == before, "existing CSV values changed"
    assert [row[-1] for row in parsed] == values, "crosswalk values differ"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    with (TASK / "crosswalk.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    mapping = {row["event_id"]: row[COLUMN] for row in rows}
    assert len(rows) == len(mapping) == 71, "expected 71 unique crosswalk event IDs"
    assert sum(bool(value) for value in mapping.values()) == 64, "expected 64 mapped series"
    slugs = [slug for value in mapping.values() if value for slug in value.split(";")]
    assert len(slugs) == len(set(slugs)), "duplicate crosswalk slugs"
    raw = EVENTS.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    if COLUMN in reader.fieldnames:
        assert reader.fieldnames[-1] == COLUMN, "crosswalk must be last"
        current = list(reader)
        assert len(current) == len(mapping)
        assert {row["event_id"]: row[COLUMN] for row in current} == mapping
        print("Crosswalk already applied; no bytes written")
        return
    result = append_crosswalk(raw, mapping)
    print(f"Plan: append {COLUMN} to {len(rows)} event series, 64 mapped; existing bytes verified")
    if args.dry_run:
        return
    backup = TASK / "events.before.csv"
    if backup.exists():
        assert backup.read_bytes() == raw, "backup differs; refusing overwrite"
    else:
        backup.write_bytes(raw)
    EVENTS.write_bytes(result)
    assert EVENTS.read_bytes() == result
    print(f"Appended {COLUMN}: {len(rows)} event series, 64 mapped; existing bytes preserved")
    print(f"Rollback: restore data/events.csv from {backup.relative_to(TASK.parent.parent)}")


if __name__ == "__main__":
    main()
