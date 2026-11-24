from pathlib import Path
import re
import sys
from collections import defaultdict
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tasks/entity-type-from-name-2026-11-22"))
import common as C
import tempfile

COLUMN = "naics_primary_source_type"
def expected(base):
    candidates = {}
    for table in ("organizations", "sites"):
        for file, row in C.tagged(base, table + "_*.csv"):
            before = row[COLUMN]
            if row["naics_primary"] and before not in {"company_disclosed", "directory_assigned", "researcher_inferred", "government_filing"} and row["naics_confidence"] in {"low", "medium", "high"}:
                candidates[table, next(iter(row.values()))] = file, row, set()
    mapping = dict(own_site="company_disclosed", government_filing="government_filing",
                   registry="directory_assigned", directory="directory_assigned")
    for _, e in C.tagged(base, "evidence_*.csv"):
        key = e["record_table"], e["record_id"]
        if key in candidates and e["tier_effect"].startswith("supports_"):
            _, row, kinds = candidates[key]
            if row["naics_primary"] in re.findall(r"\d+", e["claim_detail"]):
                kinds.add(mapping.get(e["source_class"], "unknown"))
    for (_, rid), (file, row, kinds) in candidates.items():
        if len(kinds) < 2 and "unknown" not in kinds:
            yield file, rid, row[COLUMN], next(iter(kinds), "researcher_inferred")

def verify(want, actual, problems):
    if problems or want != actual:
        keys = [key for key in want.keys() | actual.keys() if want.get(key) != actual.get(key)]
        raise ValueError(f"{problems} mismatched cells {keys[:3]}")

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as scratch:
        base = C.export_tree((HERE / "BASE_REF").read_text().strip(), scratch)
        want = {(f, rid, COLUMN): (before, after) for f, rid, before, after in expected(base)}
        actual, problems = C.diff_trees(base, ROOT / "data")
        verify(want, actual, problems)
        print(f"PASS {len(want)} expected cells. All data files compared.")
        key = next(iter(want))
        f, rid, _ = key
        for plant in ("wrong value", "omission", "overwrite"):
            changed = actual.copy()
            if plant == "wrong value":
                changed[key] = (want[key][0], "wrong")
            elif plant == "omission":
                del changed[key]
            else:
                changed[f, rid, "last_verified"] = ("2026-11-01", "2026-11-24")
            try:
                verify(want, changed, [])
            except ValueError as err:
                print(f"{plant} rejected: {err}")
            else:
                raise AssertionError(plant)

