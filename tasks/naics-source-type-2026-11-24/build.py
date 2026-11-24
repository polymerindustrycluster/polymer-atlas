from pathlib import Path
import re
import sys
from collections import defaultdict
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tasks/entity-type-from-name-2026-11-22"))
import common as C

COLUMN = "naics_primary_source_type"

TYPES = {"own_site": "company_disclosed", "government_filing": "government_filing",
         "registry": "directory_assigned", "directory": "directory_assigned"}

def changes(data):
    evidence = defaultdict(list)
    for _, e in C.tagged(data, "evidence_*.csv"):
        evidence[e["record_table"], e["record_id"]].append(e)
    for table in ("organizations", "sites"):
        for file, row in C.tagged(data, table + "_*.csv"):
            rid = next(iter(row.values()))
            code = row["naics_primary"]
            before = row[COLUMN]
            if not code or before in {*TYPES.values(), "researcher_inferred"} or row["naics_confidence"] not in {"high", "medium", "low"}:
                continue
            matched = {TYPES.get(e["source_class"]) for e in evidence[table, rid]
                       if e["tier_effect"].startswith("supports_") and re.search(r"(?<!\d)" + re.escape(code) + r"(?!\d)", e["claim_detail"])}
            if not matched:
                matched.add("researcher_inferred")
            if len(matched) == 1 and None not in matched:
                yield file, rid, before, matched.pop()

if __name__ == "__main__":
    packet = [dict(file=f, record_id=r, column=COLUMN, before=b, after=a)
              for f, r, b, a in changes(ROOT / "data")]
    C.apply_changes(ROOT / "data", packet)
    print(f"Changed {len(packet)} cells.")

