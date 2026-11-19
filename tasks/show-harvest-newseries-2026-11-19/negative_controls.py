"""Negative controls for this pass's check.py. Each plants one otherwise-valid row (copied from a real row of this
pass, so its source URL, show key and event agree) with a single defect, runs check.py, and passes only if check.py
fails WITH THE EXPECTED MESSAGE and, unless marked not strict, for that one reason only; then the original bytes are
restored. Exit 0 = every control failed as required.
    python3 tasks/show-harvest-newseries-2026-11-19/negative_controls.py      (from the repo root)"""
import csv, io, re, subprocess, sys
from pathlib import Path

T = Path("tasks/show-harvest-newseries-2026-11-19")
PK, TAB = T / "participation_append.csv", Path("data/event_participation.csv")
orig = {p: p.read_bytes() for p in (PK, TAB)}
rows = list(csv.DictReader(io.StringIO(orig[PK].decode("utf-8"))))
fields, ok = list(rows[0]), []
first = lambda ev, role: next(r for r in rows if r["event_id"] == ev and r["role"] == role)  # noqa: E731
AMPP, GL, ECS = first("EVT-000072", "exhibitor"), first("EVT-000082", "attendee"), first("EVT-000080", "exhibitor")
WB = first("EVT-000098", "sponsor")
ORG = {o["legal_name"]: o["org_id"] for f in sorted(Path("data").glob("organizations_*.csv"))
       for o in csv.DictReader(open(f, encoding="utf-8", newline=""))}


def plant(label, expect, base=AMPP, strict=True, **kw):
    listed = kw.pop("listed", None)
    kw.setdefault("edition_year", "2024")  # a year no real row of this pass uses, so only the defect under test fires
    extra = dict(base, participation_id="EVP-999999", **kw)
    if listed:
        extra["sources"] = f'{extra["evidence_source_url"]} (read 2026-11-09; listed as "{listed}")'
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


GL_LISTED = GL["sources"].split('listed as "')[1][:-2]
CTT_NOTES = GL["notes"].replace("great-lakes-coatings-conference:2027", "coatings-trends-and-technologies-summit:2027")
abroad_note = ECS["notes"].split(" Edition abroad:")[0]

plant("attendee row from a list not in ATTENDEE_LISTS (SPE Polyolefins delegates)",
      "attendee row not from an ATTENDEE_LISTS list", base=GL, listed=GL_LISTED,
      evidence_source_url="https://spe-stx.org/wp-content/uploads/2026/03/Attendees-2026-publish.xlsx")
# not strict: the registration list is also not in ATTENDEE_LISTS, so the attendee check fires on it too
plant("the Coatings Trends registration list, awaiting an owner ruling", "list awaits an owner ruling (OWNER_PENDING)",
      strict=False, base=GL, listed=GL_LISTED, event_id="EVT-000077", notes=CTT_NOTES,
      evidence_source_url="https://www.pcimag.com/coatings-conference/registered-companies")
plant("Great Lakes list used for another event", "attendee row not from an ATTENDEE_LISTS list for its event",
      base=GL, listed=GL_LISTED, event_id="EVT-000077", notes=CTT_NOTES)
plant("bare group name held at this event (Evonik, Waterborne)", "name held (CONTROLLER_HOLDS)", base=WB,
      org_id=ORG["Evonik Corporation"], listed="Evonik")
plant("a variant form of a held name (Evonik Corporation, Waterborne)", "name held (CONTROLLER_HOLDS)", base=WB,
      org_id=ORG["Evonik Corporation"], listed="Evonik Corporation")
plant("a variant form of a held name (BASF Corporation, Great Lakes)", "name held (CONTROLLER_HOLDS)", base=GL,
      org_id=ORG["BASF Corporation"], listed="BASF Corporation")
plant("trade-name hit (The Dow Chemical Company -> Dow Inc.)", "listed name is not the org's legal name",
      org_id="ORG-002913", listed="The Dow Chemical Company")
plant("ambiguous name key (ACH Foam Technologies, two orgs)", "listed name's key is held by", org_id="ORG-004921",
      listed="ACH Foam Technologies")
plant("sources cites another URL", "sources does not cite evidence_source_url",
      sources='https://example.com/list (read 2026-11-09; listed as "Chase Corp")')
plant("notes name another event's show", "is not a series of EVT-000072",
      notes=AMPP["notes"].replace("ampp-annual-conference-expo:2027", "eastern-coatings-show:2027"))
plant("a row for a series this pass does not cover (NPE)", "event is not one of the series #409 seeded",
      event_id="EVT-000001", notes=AMPP["notes"].replace("ampp-annual-conference-expo:2027", "npe-the-plastics-show:2027"))
plant("a duplicate of an existing row", "duplicate (event, org, year, role) in the table",
      edition_year=AMPP["edition_year"])
plant("attendee row with a role_detail", "attendee row with a role_detail", base=GL, role_detail="Booth 1234")
plant("personal pattern in role_detail", "personal pattern in role_detail", role_detail="Dr. Jane Doe")
plant("a role this pass does not admit (media partner)", "role not admitted", role="media_partner")
plant("abroad row without the listed country", "without a listed country equal to the org's HQ country", base=ECS,
      notes=abroad_note)
plant("abroad row whose listed country is not the HQ country", "without a listed country equal to the org's HQ "
      "country", base=ECS, notes=re.sub(r"country \([^)]+\)", "country (Germany)", ECS["notes"], count=1))
plant("abroad row with a USPS edition_state (the ICERP US/IN mis-key)", "international-series row with a USPS "
      "edition_state", base=ECS, edition_state="IN")
# not strict: a dropped label is never an organization's legal name, so the name checks also fire on it
plant("controller drop list (wave 2-3: a JEC page label)", "controller drop", strict=False, listed="10 YEARS OF "
      "INNOVATION STARTUP BOOSTER", notes=AMPP["notes"].replace("ampp-annual-conference-expo:2027", "jec-world:2027"))
print(f"{sum(ok)} of {len(ok)} negative controls fail check.py with the expected message")
sys.exit(0 if all(ok) else 1)
