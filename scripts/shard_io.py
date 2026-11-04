#!/usr/bin/env python3
"""Shared shard writer for builders (owner battery 2026-11-04, B-GUARDS).

    from shard_io import append_sorted          # with scripts/ on sys.path
    append_sorted(data / "organizations_US.csv", new_rows, "org_id")

Appends rows to a shard and keeps it id-ascending (V-36), LF line endings (V-56) and the shard's own header. It refuses
an id that is already present, because ids are never reused (AGENTS.md §3). Existing rows are never changed, only
re-ordered among the new ones. A builder that appends at the end of a shared shard breaks V-36 whenever two waves
write to it.
"""
import csv, io
from pathlib import Path


def append_sorted(path, rows, id_col):
    path = Path(path)
    text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    rdr = csv.DictReader(io.StringIO(text, newline=""))
    header, old = rdr.fieldnames, list(rdr)
    have = {r[id_col] for r in old}
    dup = [r[id_col] for r in rows if r[id_col] in have]
    if dup:
        raise ValueError(f"{path.name}: ids already present {dup[:5]} (AGENTS.md §3: never reuse an id)")
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n", extrasaction="ignore")
    w.writeheader(); w.writerows(sorted(old + list(rows), key=lambda r: r[id_col]))
    path.write_bytes(buf.getvalue().encode("utf-8"))


if __name__ == "__main__":  # self-check on a temp shard
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "organizations_XX.csv"
        p.write_bytes(b"org_id,legal_name\r\nORG-000002,B\r\nORG-000009,C\r\n")
        append_sorted(p, [{"org_id": "ORG-000005", "legal_name": "new"}], "org_id")
        assert p.read_bytes() == b"org_id,legal_name\nORG-000002,B\nORG-000005,new\nORG-000009,C\n", p.read_bytes()
        try:
            append_sorted(p, [{"org_id": "ORG-000009", "legal_name": "dup"}], "org_id"); raise SystemExit("dup not refused")
        except ValueError:
            pass
    print("shard_io self-check ok")
