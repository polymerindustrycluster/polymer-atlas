"""Negative controls for this pass's check.py. Each plants one otherwise-valid row (copied from a real row of this
pass, so its source URL, show key and event agree) with a single defect, runs check.py, and passes only if check.py
fails WITH THE EXPECTED MESSAGE; then the original bytes are restored. Exit 0 = every control failed as required.
    python3 tasks/show-harvest-rulings-2026-11-19/negative_controls.py      (from the repo root)"""
import csv, io, subprocess, sys
from pathlib import Path

T = Path("tasks/show-harvest-rulings-2026-11-19")
PK, TAB = T / "participation_append.csv", Path("data/event_participation.csv")
orig = {p: p.read_bytes() for p in (PK, TAB)}
rows = list(csv.DictReader(io.StringIO(orig[PK].decode("utf-8"))))
fields, base, ok = list(rows[0]), rows[0], []
URL = base["evidence_source_url"]


def plant(label, expect, strict=True, **kw):
    listed, extra_ok = kw.pop("listed", None), not strict
    kw.setdefault("edition_year", "2025")  # a year no real row of this pass uses, so only the defect under test fires
    extra = dict(base, participation_id="EVP-999999", **kw)
    if listed:
        extra["sources"] = f'{extra["evidence_source_url"]} (read 2026-11-09; listed as "{listed}")'
    b = io.StringIO(); csv.DictWriter(b, fieldnames=fields, lineterminator="\n").writerow(extra)
    for p, add in ((PK, b.getvalue()), (TAB, b.getvalue())):
        p.write_bytes(orig[p] + add.encode("utf-8"))
    r = subprocess.run([sys.executable, str(T / "check.py")], capture_output=True, text=True)
    for p, by in orig.items():
        p.write_bytes(by)
    out = r.stdout + r.stderr
    # the planted row must fail for exactly one reason, the one under test
    good = r.returncode != 0 and expect in out and (extra_ok or out.count("('EVP-999999'") == 1)
    print(("PASS " if good else "MISS ") + label, "| expected:", expect, "|", out.strip().splitlines()[-1][:110])
    ok.append(good)


plant("attendee row from a list not in ATTENDEE_LISTS (SPE Polyolefins delegates)",
      "attendee row not from an ATTENDEE_LISTS list", evidence_source_url=
      "https://spe-stx.org/wp-content/uploads/2026/03/Attendees-2026-publish.xlsx", listed="A&P Technology, Inc")
plant("controller-held bare group name (Arkema)", "held name", org_id="ORG-002224", listed="Arkema")
plant("trade-name hit (The Dow Chemical Company -> Dow Inc.)", "listed name is not the org's legal name",
      org_id="ORG-002913", listed="The Dow Chemical Company")
plant("sources cites another URL", "sources does not cite evidence_source_url",
      sources='https://example.com/list (read 2026-11-09; listed as "A&P Technology, Inc")')
plant("notes name another event's show", "is not a series of EVT-000035",
      notes=base["notes"].replace("sampe-conference-and-exhibition:2027", "npe-the-plastics-show:2027"))
plant("a sponsor row that is not an alt-text name", "non-attendee row is not an alt-text name", role="sponsor")
plant("ambiguous name key (ACH Foam Technologies, two orgs)", "listed name's key is held by", org_id="ORG-004921",
      listed="ACH Foam Technologies")
# second round (codex + agy on #404)
alt = " Listed by the organizer as a logo's alt text (counts as on the page under the owner ruling of 2026-11-18)."
plant("combined-list exclusion: Foam Expo speaker page (codex)", "combined-list exclusion (COMBINED)",
      event_id="EVT-000020", role="speaker", edition_year="2027", org_id="ORG-000683", listed="Bostik",
      notes="Speaker name matched to the org by exact normalized legal name; list banked in staging "
            "(harvest-2026-11, foam-expo-north-america:2027)." + alt)
# not strict: a dropped label is never an organization's legal name, so the name checks also fire on it
plant("controller drop list (wave 2-3: a JEC page label)", "controller drop", strict=False, event_id="EVT-000029",
      role="exhibitor", listed="10 YEARS OF INNOVATION STARTUP BOOSTER",
      notes="Exhibitor name matched; list banked in staging (harvest-2026-11, jec-world:2027)." + alt)
plant("SAMPE list used for another event (agy)", "attendee row not from an ATTENDEE_LISTS list for its event",
      event_id="EVT-000001", notes=base["notes"].replace("sampe-conference-and-exhibition:2027", "npe-the-plastics-show:2027"))
plant("a duplicate of an existing row (agy)", "duplicate (event, org, year, role) in the table",
      edition_year=base["edition_year"])
plant("attendee row with a role_detail (agy)", "attendee row with a role_detail", role_detail="Booth 1234")
plant("personal pattern in role_detail (agy)", "personal pattern in role_detail", role="sponsor",
      role_detail="Dr. Jane Doe", notes=base["notes"] + alt)
plant("newly held bare group name (Sun Chemical)", "held name", org_id="ORG-001489", listed="Sun Chemical")
# confirmation round (codex): a script/style tag's title attribute is not page text (build.py's reader, tested directly)
sys.path.insert(0, str(T))
import build as B  # noqa: E402
page = '<style title="Bostik">.sponsor{display:none}</style><img alt="Sika" src="x.png"><a title="Mapei">x</a>'
got = B.text(page, alt=True)
good = "bostik" not in got and "sika" in got and "mapei" in got
print(("PASS " if good else "MISS ") + "script/style title is not alt text | read:", got)
ok.append(good)
print(f"{sum(ok)} of {len(ok)} negative controls fail check.py with the expected message")
sys.exit(0 if all(ok) else 1)
