#!/usr/bin/env python3
"""Check that a registry integration appends exactly the approved packet."""
import argparse
import csv
import io
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = "data/registry_links.csv"
PACKET = Path(__file__).with_name("packet.csv").relative_to(ROOT).as_posix()
FIELDS = ("org_id", "registry", "registry_id", "match_basis", "as_of", "site_id")


def git(*args):
    return subprocess.check_output(["git", "-C", ROOT, *args])


def index(rows, label):
    indexed = {}
    for row in rows:
        key = (row["site_id"], row["registry"], row["registry_id"])
        if not all(key) or key in indexed:
            raise ValueError(f"{label} contains a missing or duplicate link key: {key}")
        indexed[key] = tuple(row[field] for field in FIELDS)
    return indexed


def rows(data, fields=None):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""), fieldnames=fields, strict=True)
    result = list(reader)
    if any(None in row or None in row.values() for row in result):
        raise ValueError("CSV contains an incomplete or over-wide row")
    return tuple(reader.fieldnames or ()), result


def check_rows(before, after, approved):
    if not after.startswith(before):
        raise ValueError("existing registry file bytes changed")
    _, actual_rows = rows(after[len(before):], FIELDS)
    actual = index(actual_rows, "appended rows")
    extra = actual.keys() - approved.keys()
    missing = approved.keys() - actual.keys()
    if extra or missing:
        raise ValueError(f"registry link keys differ: {len(extra)} extra, {len(missing)} missing")
    if actual != approved:
        raise ValueError("canonical fields of an appended link differ from the approved packet")
    return actual_rows


def negative_controls(before, after, approved, first):
    used = {key[2] for key in approved}
    new_id = "0" * 12 if "0" * 12 not in used else "9" * 12
    altered = {**first, "registry_id": new_id}
    buf = io.StringIO(newline="")
    csv.DictWriter(buf, FIELDS, lineterminator="\n").writerow(altered)
    planted = buf.getvalue().encode("utf-8")
    # The altered-row plant replaces the first appended row in memory.
    first_record_end = after.index(b"\n", len(before)) + 1
    for label, candidate, expected in (
        ("extra link", after + planted, "1 extra, 0 missing"),
        ("altered registry_id", before + planted + after[first_record_end:], "1 extra, 1 missing"),
    ):
        try:
            check_rows(before, candidate, approved)
        except ValueError as exc:
            if not str(exc).endswith(expected):
                raise ValueError(f"planted {label} failed for an unexpected reason: {exc}") from exc
            print(f"Rejected planted {label} ({exc})")
        else:
            raise ValueError(f"planted {label} passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main", help="pre-application baseline ref")
    args = parser.parse_args()
    base = git("rev-parse", "--verify", args.base + "^{commit}").decode().strip()
    before = git("show", f"{base}:{REGISTRY}")
    approved_bytes = git("show", f"{base}:{PACKET}")
    if (ROOT / PACKET).read_bytes() != approved_bytes:
        raise ValueError("the approved packet changed")
    packet_header, packet_rows = rows(approved_bytes)
    base_header, base_rows = rows(before)
    if base_header != FIELDS or packet_header[:len(FIELDS)] != FIELDS:
        raise ValueError("canonical registry columns differ")
    approved = index(packet_rows, "approved packet")
    if len(approved) != 206 or approved.keys() & index(
        (row for row in base_rows if row["site_id"]), "baseline facility links"
    ).keys():
        raise ValueError("the baseline or approved 206-link packet differs from the integration scope")
    other = ("data/", f":(exclude){REGISTRY}")
    if git("diff", "--name-only", base, "--", *other) or git("ls-files", "--others", "--exclude-standard", "--", *other):
        raise ValueError(f"other data paths differ from {args.base}")
    after = (ROOT / REGISTRY).read_bytes()
    actual = check_rows(before, after, approved)
    print(f"All {len(actual)} appended rows equal the approved packet; other data paths match {args.base} ({base[:8]})")
    negative_controls(before, after, approved, actual[0])


if __name__ == "__main__":
    main()
