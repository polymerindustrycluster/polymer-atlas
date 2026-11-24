#!/usr/bin/env python3
"""Apply the owner-approved V-55 migration to the canonical shards."""
import csv
import io
import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
FIELDS = ("processes", "materials")
SEPARATORS = re.compile(r",|\band\b")
UNDERSCORES = str.maketrans(" -/", "___")


def exact_tokens(value):
    return [
        part.strip().removesuffix(" (secondary)").translate(UNDERSCORES)
        for part in SEPARATORS.split(value.lower())
    ]


def repair(row, field, allowed):
    raw = row[field].split(";")
    bad = [v for v in raw if v.strip() and v.strip() not in allowed]
    note = field + "_other_note"
    row.setdefault(note, "")
    if not bad:
        return
    kept = [v for v in raw if v not in bad]
    notes = row[note].split(";") if row[note] else []
    seen = {v.strip() for v in kept}
    for original in bad:
        tokens = exact_tokens(original)
        if all(token in allowed for token in tokens):
            for token in tokens:
                if token not in seen:
                    kept.append(token)
                    seen.add(token)
        else:
            notes.append(original)
    row[field] = ";".join(v for v in kept if v.strip())
    row[note] = ";".join(dict.fromkeys(notes))


def build():
    vocabulary = json.loads((ROOT / "docs/schema/vocab.json").read_text())["vocabularies"]
    processes = set(vocabulary["PROCESSES"]["values"])
    ring3_processes = processes | set(vocabulary["RING3_PROCESSES"]["values"])
    materials = set(vocabulary["MATERIALS"]["values"])
    changed = 0
    for grain in ("organizations", "sites"):
        paths = sorted(DATA.glob(f"{grain}_*.csv"))
        if not paths:
            raise SystemExit(f"Missing {grain} shards")
        for path in paths:
            original = path.read_bytes()
            reader = csv.DictReader(io.StringIO(original.decode(), newline=""), strict=True)
            header = list(reader.fieldnames)
            for field in FIELDS:
                note = field + "_other_note"
                if note not in header:
                    header.insert(header.index(field) + 1, note)

            out = io.StringIO(newline="")
            writer = csv.DictWriter(out, header, lineterminator="\n")
            writer.writeheader()
            for row in reader:
                if None in row or None in row.values():
                    raise SystemExit(f"{path.name}: malformed CSV row at line {reader.line_num}")
                allowed = ring3_processes if row["ring_primary"].strip() == "3" else processes
                repair(row, "processes", allowed)
                repair(row, "materials", materials)
                writer.writerow(row)
            built = out.getvalue().encode()
            if built != original:
                with NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
                    tmp.write(built)
                    temp_path = Path(tmp.name)
                temp_path.chmod(path.stat().st_mode & 0o777)
                temp_path.replace(path)
                changed += 1
    print(f"{changed} organization or site shard files rewritten")


if __name__ == "__main__":
    build()
