#!/usr/bin/env python3
"""Apply the 2026-11-09 review (codex + grok sample of 60, then a trade-name check of all 161) to this wave.
- Drop 7 rows: a parent or brand name credited as a different entity, an undated source page, a business-unit mismatch.
- Where the notes' staging key names a later edition than the row's edition_year, say which year the row follows.
Edits data/event_participation.csv and participation_append.csv the same way, so the packet and the table agree.
    python3 tasks/show-harvest-w1-2026-11-06/review_fixes.py
"""
import csv, io, re
from pathlib import Path
HERE = Path(__file__).resolve().parent
DROP = {
    "EVP-001255": "listed 'Coperion' is a distinct company; it was credited to its parent Hillenbrand via a trade name",
    "EVP-001213": "listed 'Cimatron' is a distinct CAD/CAM business; it was credited to SigmaTEK via a trade name",
    "EVP-001211": "listed 'Barnes Molding Solutions' is the umbrella brand; it was credited to Synventive via a trade name",
    "EVP-001291": "a bare 'Continental' collides with several companies; it cannot be pinned to Continental AG",
    "EVP-001155": "the sponsor page is undated, so the edition year is unresolved",
    "EVP-001157": "the sponsor page is undated, so the edition year is unresolved",
    "EVP-001301": "listed as Amcor Flexibles; the held record is a rigid-PET plant, a different business unit",
}


def fix(path):
    raw = path.read_bytes()
    eol = "\r\n" if b"\r\n" in raw[:4096] else "\n"
    rdr = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    head, rows = rdr.fieldnames, list(rdr)
    keep, dropped, noted = [], 0, 0
    for r in rows:
        if r["participation_id"] in DROP:
            dropped += 1; continue
        k = re.search(r":(\d{4})\)", r.get("notes") or "")
        if k and k.group(1) != r["edition_year"] and "row year follows" not in r["notes"]:
            r["notes"] += f" The staging key's year ({k.group(1)}) is the harvest's edition label; the row year follows the year printed in the source."
            noted += 1
        keep.append(r)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=head, lineterminator=eol); w.writeheader(); w.writerows(keep)
    path.write_bytes(buf.getvalue().encode("utf-8"))
    return dropped, noted


d1 = fix(HERE.parents[1] / "data" / "event_participation.csv")
d2 = fix(HERE / "participation_append.csv")
assert d1 == d2, (d1, d2)  # the table and the packet must agree
with open(HERE / "review_drops.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n"); w.writerow(["participation_id", "reason"]); w.writerows(sorted(DROP.items()))
print(f"dropped {d1[0]}; notes clarified {d1[1]}")
