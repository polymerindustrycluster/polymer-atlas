from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tasks/entity-type-from-name-2026-11-22"))
import common as C
import csv
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
        with (HERE / "CLAIMS_CHECKED.csv").open(newline="") as fh:
            ledger = [(r["table"], r["record_id"], r["field"], r["verdict"]) for r in csv.DictReader(fh)]
        claimed = sorted(ledger)  # a list, not a set: a duplicate row would inflate the outcome tally
        if claimed != sorted(("organizations", rid, COLUMN, "corrected") for _, rid, _ in want):
            raise ValueError("CLAIMS_CHECKED.csv must list each changed cell exactly once and nothing else")
        print(f"PASS CLAIMS_CHECKED.csv lists the {len(claimed)} changed cells, each once.")
        dup = claimed + claimed[:1]
        if dup == sorted(("organizations", rid, COLUMN, "corrected") for _, rid, _ in want):
            raise AssertionError("duplicate-row plant not caught")
        print("duplicate claim row rejected (plant)")

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
