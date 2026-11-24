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

COLUMN = "entity_type"
from rules import classify, US

STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())
def expected(base):
    for file, row in C.tagged(base, "organizations_*.csv"):
        if row["hq_country"].strip().upper() not in US | {""} or row["hq_state"].strip().upper() not in STATES:
            continue
        if row[COLUMN] not in {"", "unknown"} or row["stock_ticker"].strip():
            continue
        value, reason, suffix = classify(row)
        if reason == "fill":
            compact = re.sub(r"[^a-z]", "", suffix.lower())
            if compact in {"llc", "limitedliabilitycompany"}:
                form = "llc"
            elif compact in {"inc", "incorporated", "corp", "corporation"}:
                form = "corporation"
            else:
                assert compact in {"lp", "llp", "lllp", "limitedpartnership", "limitedliabilitypartnership"}
                form = "partnership"
            yield file, row["org_id"], row[COLUMN], form

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

