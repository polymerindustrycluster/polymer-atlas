"""Negative controls for this pass's check.py. Each plants one row copied from a real row of this pass with a single
defect, runs check.py, and passes only if check.py fails WITH THE EXPECTED MESSAGE and, unless marked not strict, for
that one reason only; then the original bytes are restored. Exit 0 = every control failed as required.
    python3 tasks/owner-rulings-2026-11-19d/negative_controls.py      (from the repo root)"""
import csv, io, subprocess, sys
from pathlib import Path

T = Path("tasks/owner-rulings-2026-11-19d")
PK, TAB = T / "participation_append.csv", Path("data/event_participation.csv")
orig = {p: p.read_bytes() for p in (PK, TAB)}
rows = list(csv.DictReader(io.StringIO(orig[PK].decode("utf-8"))))
fields, ok, base = list(rows[0]), [], rows[0]
ORG = {o["legal_name"]: o["org_id"] for f in sorted(Path("data").glob("organizations_*.csv"))
       for o in csv.DictReader(open(f, encoding="utf-8", newline=""))}
# an organization this list does not mint, so only the defect under test fires
FREE = dict(org_id=ORG["Hexcel Corporation"], listed="Hexcel Corporation")


def plant(label, expect, strict=True, **kw):
    listed = kw.pop("listed", None)
    extra = dict(base, participation_id="EVP-999999", **kw)
    if listed:
        extra["sources"] = f'{extra["evidence_source_url"]} (read 2026-11-06; listed as "{listed}")'
    b = io.StringIO(); csv.DictWriter(b, fieldnames=fields, lineterminator="\n").writerow(extra)
    for p in (PK, TAB):
        p.write_bytes(orig[p] + b.getvalue().encode("utf-8"))
    r = subprocess.run([sys.executable, str(T / "check.py")], capture_output=True, text=True)
    for p, by in orig.items():
        p.write_bytes(by)
    out = r.stdout + r.stderr
    good = r.returncode != 0 and expect in out and (not strict or out.count("('EVP-999999'") == 1)
    print(("PASS " if good else "MISS ") + label, "| expected:", expect, "|", out.strip().splitlines()[-1][:110])
    ok.append(good)


plant("another year (2025)", "not an EVT-000077 2026 attendee row", **FREE, edition_year="2025")
plant("another event (Great Lakes)", "not an EVT-000077 2026 attendee row", **FREE, event_id="EVT-000082")
plant("another role (sponsor)", "not an EVT-000077 2026 attendee row", **FREE, role="sponsor")
plant("a duplicate of a real row", "duplicate (event, org, year, role) in the table")
plant("the ruling's note dropped", "notes lack the ruling's note", **FREE,
      notes=base["notes"].replace("owner ruling 2026-11-19d", "owner ruling"))
plant("a role_detail on an attendee row", "attendee row with a role_detail", **FREE, role_detail="Booth 12")
plant("an edition_state the conferences repo did not give", "edition fields set", **FREE, edition_state="Germany")
plant("edition dates the conferences repo did not give", "edition fields set", **FREE,
      edition_dates="2026-09-15 to 2026-09-17")
plant("a tier other than A", "verification_tier is not A", **FREE, verification_tier="B")
# not strict: a URL that is not the list also fails the first check
plant("sources citing another URL", "sources does not cite the list", strict=False, org_id=FREE["org_id"],
      sources='https://www.pcimag.com/coatings-conference (read 2026-11-06; listed as "Hexcel Corporation")')
plant("a trade-name hit (Nouryon)", "listed name is not the org's legal name", **dict(FREE, listed="Nouryon",
                                                                                      org_id=ORG["Nouryon Chemicals LLC"]))
# not strict: a page label is no organization's legal name either. (The list's other drop, a person's name, is never
# written here: the drop lists store hashes so that no name of a person enters this public repo.)
plant("a controller-dropped name (the page label \"More Videos\")", "controller drop", strict=False,
      **dict(FREE, listed="More Videos"))
plant("a bare group name held by #411 (Sun Chemical)", "name held (CONTROLLER_HOLDS or HOLDS)",
      **dict(FREE, listed="Sun Chemical", org_id=ORG["Sun Chemical Corporation"]))
plant("the bare Arkema this pass holds", "name held (CONTROLLER_HOLDS or HOLDS)",
      **dict(FREE, listed="Arkema", org_id=ORG["Arkema Inc."]))
print(f"{sum(ok)} of {len(ok)} controls failed check.py as required")
sys.exit(0 if all(ok) else 1)
