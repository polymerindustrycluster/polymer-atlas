from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tasks/entity-type-from-name-2026-11-22"))
import common as C
import csv
import json
import subprocess
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
        if key in candidates:
            _, row, kinds = candidates[key]
            if row["naics_primary"] in re.findall(r"\d+", e["claim_detail"].split("quote:", 1)[-1] if "quote:" in e["claim_detail"] else ""):
                kinds.add(mapping.get(e["source_class"], "unknown") if e["tier_effect"].startswith("supports_") else "unknown")
    for (_, rid), (file, row, kinds) in candidates.items():
        if len(kinds) < 2 and "unknown" not in kinds:
            yield file, rid, row[COLUMN], next(iter(kinds), "researcher_inferred")

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
        path = "scripts/validate_debt_baseline.json"
        ref = (HERE / "BASE_REF").read_text().strip()
        state = json.loads(subprocess.check_output(["git", "-C", ROOT, "show", f"{ref}:{path}"]))
        repaired = {rid for _, rid, _ in want}
        state["rules"]["V-47"] = [rid for rid in state["rules"]["V-47"] if rid not in repaired]
        if state != json.loads((ROOT / path).read_text()):
            raise ValueError("Debt baseline differs from the expected V-47 shrink")
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
