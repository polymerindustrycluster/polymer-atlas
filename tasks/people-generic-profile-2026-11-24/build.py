from pathlib import Path
import re
import sys
from collections import defaultdict
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tasks/entity-type-from-name-2026-11-22"))
import common as C

COLUMN = "public_profile_url"

def parse_url(value):
    return urlsplit(value if "://" in value or value.startswith("//") else "//" + value)

def changes(data):
    people = C.read_csv(data / "people.csv")
    peers = defaultdict(set)
    for row in people:
        url = parse_url(row[COLUMN])
        host = url.hostname or ""
        path = url.path.lower()
        surname = row["full_name"].lower().split()[-1]
        if host.endswith(".edu") and (host.startswith("profiles.") or re.match(r"^/(person|directory|faculty_staff/listing)/", path)):
            if surname in re.findall(r"[a-z]+", path):
                peers[host].add(row["person_id"])
    for row in people:
        url = parse_url(row[COLUMN])
        if url.query or url.fragment or not re.fullmatch(r"/?(?:index\.[^/]+)?", url.path, re.I):
            continue
        if peers[url.hostname] - {row["person_id"]}:
            yield "people.csv", row["person_id"], row[COLUMN], ""

if __name__ == "__main__":
    packet = [dict(file=f, record_id=r, column=COLUMN, before=b, after=a)
              for f, r, b, a in changes(ROOT / "data")]
    C.apply_changes(ROOT / "data", packet)
    print(f"Changed {len(packet)} cells.")

