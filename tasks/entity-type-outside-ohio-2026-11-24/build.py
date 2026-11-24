from pathlib import Path
import re
import sys
from collections import defaultdict
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tasks/entity-type-from-name-2026-11-22"))
import common as C

COLUMN = "entity_type"

from rules import classify

STATES = set("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split())

def changes(data):
    for file, row in C.tagged(data, "organizations_*.csv"):
        if row["hq_state"].strip().upper() in STATES:
            value, category, _ = classify(row)
            if category == "fill":
                yield file, row["org_id"], row[COLUMN], value

if __name__ == "__main__":
    packet = [dict(file=f, record_id=r, column=COLUMN, before=b, after=a)
              for f, r, b, a in changes(ROOT / "data")]
    C.apply_changes(ROOT / "data", packet)
    print(f"Changed {len(packet)} cells.")

