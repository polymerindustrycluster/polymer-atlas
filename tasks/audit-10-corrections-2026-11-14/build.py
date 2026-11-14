"""Apply the two confirmed field errors from blind audit 10 (PR #331). Idempotent: python3 build.py [--apply]."""
import csv, io, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TPO_SCHEDULE = "https://auto-tpo.com/wp-content/uploads/2026/09/TPOSchedule-rev2-9_15_26-FINAL.pdf"
MONET = "https://www.monetcci.org/"
MONET_TEAM = "https://www.monetcci.org/our-team"
OLD_DESC = ("partners Columbia, Johns Hopkins, MIT, Northwestern, UC San Diego, UIUC, Michigan and Washington.")
NEW_DESC = ("partners Columbia, Johns Hopkins, MIT, Northwestern, Morehouse College, UC San Diego, UIUC and Washington.")


def load(name):
    text = (ROOT / "data" / name).read_text(encoding="utf-8")
    r = csv.DictReader(io.StringIO(text, newline=""))
    return r.fieldnames, list(r)


def save(name, header, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    (ROOT / "data" / name).write_bytes(buf.getvalue().encode("utf-8"))


def add_source(value, url):
    parts = [p.strip() for p in value.split(";") if p.strip()]
    return value if url in parts else (value + "; " + url if value else url)


changes = []
h, evp = load("event_participation.csv")
for r in evp:
    if r["event_id"] == "EVT-000046" and r["edition_year"] == "2026" and r["edition_dates"] == "2026-09-28 to 2026-10-01":
        r["edition_dates"] = "2026-09-28 to 2026-09-30"
        r["sources"] = add_source(r["sources"], TPO_SCHEDULE)
        changes.append(("event_participation", r["participation_id"], "edition_dates"))
hp, progs = load("programs.csv")
for r in progs:
    if r["program_id"] == "PROG-000314":
        if r["url"] != MONET or r["public_door_url"] != MONET:
            r["url"] = r["public_door_url"] = MONET
            changes.append(("programs", "PROG-000314", "url;public_door_url"))
        if OLD_DESC in r["description_1line"]:
            r["description_1line"] = r["description_1line"].replace(OLD_DESC, NEW_DESC)
            changes.append(("programs", "PROG-000314", "description_1line"))
        r["sources"] = add_source(add_source(r["sources"], MONET), MONET_TEAM)
# Recompute the generated §4.11 rollup for the program's institution, with validate.py's V-16 rule.
TYPE_PREC = {"degree": 0, "center": 1, "certificate": 2, "apprenticeship": 3, "training": 4, "lab_facility": 5, "course": 6}
he, eco = load("ecosystem.csv")
inst = next(r["institution_org_id"] for r in progs if r["program_id"] == "PROG-000314")
P = sorted((p for p in progs if p["institution_org_id"] == inst and p.get("status", "").strip() != "tombstoned"),
           key=lambda p: (TYPE_PREC[p["program_type"].strip()], p["program_name"].strip().lower()))
for r in eco:
    if r["org_id"] == inst and r.get("record_grain", "").strip() == "institution":
        want = (P[0].get("url") or "").strip()
        if r["polymer_program_url"].strip() != want:
            r["polymer_program_url"] = want
            changes.append(("ecosystem", inst, "polymer_program_url (generated rollup)"))
print(f"cells to change: {len(changes)}")
for c in changes: print("  ", *c)
if "--apply" in sys.argv and changes:
    save("event_participation.csv", h, evp); save("programs.csv", hp, progs); save("ecosystem.csv", he, eco); print("applied")
