#!/usr/bin/env python3
"""Clear the Materials Week USA slug from EVT-000023 Silicone Expo USA (codex post-merge review 2026-11-18, finding 1).
materials-week-usa is an umbrella of several co-located expos; §4.12.1 keeps co-located series distinct, so the
umbrella slug cannot identify one component. Edits data/events.csv (last column) and the crosswalk input, so
re-running tasks/schema-v1-12/add_crosswalk.py does not bring it back. Every other byte is kept.
    python3 tasks/schema-v1-12-postmerge-2026-11-18/fix.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EDITS = [
    (ROOT / "data" / "events.csv", b"\nEVT-000023,", b",materials-week-usa\n", b",\n"),
    (ROOT / "tasks" / "schema-v1-12" / "crosswalk.csv", b"\nEVT-000023,",
     b"Silicone Expo USA,materials-week-usa,curated,Silicone Expo USA now runs inside Materials Week USA (Detroit) "
     b"with Specialty Polymers World and Gaskets & Seals; reviewer to confirm umbrella vs series\n",
     b"Silicone Expo USA,,curated,Cleared 2026-11-18 (codex post-merge review): materials-week-usa is the umbrella "
     b"of several co-located expos and cannot identify Silicone Expo USA; the conferences repo has no Silicone Expo "
     b"slug yet\n"),
]
for path, row_start, old, new in EDITS:
    b = path.read_bytes()
    i = b.index(row_start) + 1
    j = b.index(b"\n", i) + 1
    row = b[i - 1:j]
    assert row.count(old) == 1, (path, row[-200:])
    path.write_bytes(b[:i - 1] + row.replace(old, new) + b[j:])
    print("edited", path.relative_to(ROOT))
