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

COLUMN = "public_profile_url"
def expected(base):
    rows = C.read_csv(base / "people.csv")
    for row in rows:
        root = urlsplit(row[COLUMN])
        if not root.hostname or root.query or root.fragment:
            continue
        if root.path not in {"", "/"} and not re.fullmatch("/index[.][^/]+", root.path, re.I):
            continue
        for peer in rows:
            other = urlsplit(peer[COLUMN])
            if peer["person_id"] == row["person_id"] or root.hostname != other.hostname or not other.hostname.endswith(".edu"):
                continue
            path = other.path.lower()
            if other.hostname.startswith("profiles.") or path.startswith(("/directory/", "/person/", "/faculty_staff/listing/")):
                if peer["full_name"].split()[-1].lower() in re.split("[^a-z]+", path):
                    yield "people.csv", row["person_id"], row[COLUMN], ""
                    break

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

