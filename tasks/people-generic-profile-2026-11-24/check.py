from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tasks/entity-type-from-name-2026-11-22"))
import common as C
import csv
import tempfile

COLUMN = "public_profile_url"
def expected(base):
    rows = C.read_csv(base / "people.csv")
    for row in rows:
        root = urlsplit(row[COLUMN])
        if not root.hostname:
            root = urlsplit("//" + row[COLUMN])
        if not root.hostname or root.query or root.fragment:
            continue
        if root.path not in {"", "/"} and not re.fullmatch("/index[.][^/]+", root.path, re.I):
            continue
        for peer in rows:
            other = urlsplit(peer[COLUMN])
            if not other.hostname:
                other = urlsplit("//" + peer[COLUMN])
            if peer["person_id"] == row["person_id"] or root.hostname != other.hostname or not other.hostname.endswith(".edu"):
                continue
            path = other.path.lower()
            if other.hostname.startswith("profiles.") or path.startswith(("/directory/", "/person/", "/faculty_staff/listing/")):
                if peer["full_name"].split()[-1].lower() in re.split("[^a-z]+", path):
                    yield "people.csv", row["person_id"], row[COLUMN], ""
                    break

def compare(base, tree, want):
    for file in tree.rglob("*.csv"):
        original = base / file.relative_to(tree)
        if original.exists() and original.read_bytes() != file.read_bytes():
            for path in (original, file):
                with path.open(newline="") as stream:
                    rows = csv.reader(stream)
                    width = len(next(rows, []))
                    for row in rows:
                        if len(row) != width:
                            raise ValueError(f"{path.name} line {rows.line_num}: expected {width} cells, found {len(row)}")
    actual, problems = C.diff_trees(base, tree)
    if problems or want != actual:
        keys = [key for key in want.keys() | actual.keys() if want.get(key) != actual.get(key)]
        raise ValueError(f"{problems} mismatched cells {keys[:3]}")

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as scratch:
        base = C.export_tree((HERE / "BASE_REF").read_text().strip(), scratch)
        want = {(f, rid, COLUMN): (before, after) for f, rid, before, after in expected(base)}
        compare(base, ROOT / "data", want)
        print(f"PASS {len(want)} expected cells. All data files compared.")

        # Exercise the same disk reader and comparator on a two-row extract.
        before = Path(scratch) / "before"
        after = Path(scratch) / "after"
        before.mkdir()
        after.mkdir()
        good = "id,value,other\nA,old,held\nB,keep,held\n"
        (before / "plant.csv").write_text(good)
        correct = good.replace("A,old", "A,new")
        example = {("plant.csv", "A", "value"): ("old", "new")}
        (after / "plant.csv").write_text(correct)
        compare(before, after, example)
        for plant, content in (("wrong value", correct.replace("A,new", "A,bad")),
                               ("omission", good),
                               ("overwrite", correct.replace("B,keep", "B,new")),
                               ("truncated row", correct.replace("B,keep,held", "B,keep"))):
            (after / "plant.csv").write_text(content)
            try:
                compare(before, after, example)
            except ValueError as err:
                print(f"{plant} rejected: {err}")
            else:
                raise AssertionError(plant)
