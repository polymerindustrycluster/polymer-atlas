"""Negative controls for this pass's check.py. Each plants one row copied from a real row of this pass with a single
defect, runs check.py, and passes only if check.py fails WITH THE EXPECTED MESSAGE and, unless marked not strict, for
that one reason only; then the original bytes are restored. No control writes a person's name.
    python3 tasks/show-harvest-muse-leads-2026-11-20/negative_controls.py      (from the repo root)"""
import csv, io, subprocess, sys
from pathlib import Path

T = Path("tasks/show-harvest-muse-leads-2026-11-20")
PK, TAB = T / "participation_append.csv", Path("data/event_participation.csv")
orig = {p: p.read_bytes() for p in (PK, TAB)}
rows = list(csv.DictReader(io.StringIO(orig[PK].decode("utf-8"))))
fields, ok = list(rows[0]), []
first = lambda ev, role: next(r for r in rows if r["event_id"] == ev and r["role"] == role)  # noqa: E731
AMPP, MEX, REG = first("EVT-000072", "exhibitor"), first("EVT-000085", "exhibitor"), first("EVT-000077", "attendee")
RT = next(r for r in rows if "listed as \"Alberdingk Boley, Inc\"" in r["sources"])
ORG = {o["legal_name"]: o["org_id"] for f in sorted(Path("data").glob("organizations_*.csv"))
       for o in csv.DictReader(open(f, encoding="utf-8", newline=""))}
FREE = dict(org_id=ORG["Hexcel Corporation"], listed="Hexcel Corporation")  # no row of this pass at these events
P_RULING = " A rule (i) hold binds a bare group name only; this listing names the US entity itself (owner ruling 2026-11-20)."


def plant(label, expect, base=AMPP, strict=True, **kw):
    listed = kw.pop("listed", None)
    extra = dict(base, participation_id="EVP-999999", **kw)
    if listed:
        extra["sources"] = f'{extra["evidence_source_url"]} (read 2026-11-19; listed as "{listed}")'
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


plant("a duplicate of a real row", "duplicate (event, org, year, role) in the table")
plant("a row filed under another year than its list", "does not match its list's event, year, role or note", **FREE,
      edition_year="2024")
plant("a row filed under another role than its list", "does not match its list's event, year, role or note", **FREE,
      role="sponsor")
plant("the list's note dropped", "does not match its list's event, year, role or note", **FREE,
      notes=AMPP["notes"].replace("as of March 20, 2025", "as of March 2025"))
plant("an attendee row from a Muse-lead list (not strict: its role is not the list's)", "attendee row from a Muse-lead",
      strict=False, **FREE, role="attendee")
plant("a registration-list attendee row without the ruling's note", "not an admitted registration-list attendee",
      base=REG, strict=False, org_id=ORG["Hexcel Corporation"], listed="Hexcel Corporation",
      notes=REG["notes"].replace(" (owner ruling 2026-11-20)", ""))
# Registration-list controls: each changes ONE field of an otherwise admissible registration row. The citation keeps
# the list's real read date (REG's), since plant()'s `listed=` would write another date and trip the date check.
# Not strict: the planted org (under no hold) also makes the ruling's note disagree with its hold.
REG_CITE = dict(base=REG, strict=False, org_id=ORG["Hexcel Corporation"],
                sources=REG["sources"].rsplit("listed as", 1)[0] + 'listed as "Hexcel Corporation")')
plant("a registration-list row whose evidence_date is not its read date", "not an admitted registration-list attendee",
      **REG_CITE, evidence_date="2026-09-09")
plant("a registration-list row with a consistent but wrong date in evidence_date and sources",
      "not an admitted registration-list attendee", **dict(REG_CITE, evidence_date="2026-09-09",
                                                             sources=REG_CITE["sources"].replace(REG["evidence_date"], "2026-09-09")))
plant("a registration-list row with an edition_name", "not an admitted registration-list attendee", **REG_CITE,
      edition_name="Coatings Trends 2026")
plant("a registration-list row whose citation gives another read date", "not an admitted registration-list attendee",
      **dict(REG_CITE, sources=REG_CITE["sources"].replace(REG["evidence_date"], "2026-09-09")))
plant("sources citing another URL", "sources does not cite evidence_source_url", org_id=FREE["org_id"],
      sources='https://ace.ampp.org/ (read 2026-11-19; listed as "Hexcel Corporation")')
plant("a trade-name hit (Nouryon)", "listed name is not the org's legal name",
      **dict(FREE, listed="Nouryon", org_id=ORG["Nouryon Chemicals LLC"]))
plant("a bare group name under a #411 hold (Armacell at AMPP)", "name held (a bare group name",
      **dict(FREE, listed="Armacell", org_id=ORG["Armacell LLC"]))
plant("the bare name this pass holds (Evonik at Coatings Trends; not strict: its note is the speaker list's)",
      "name held (a bare group name", base=first("EVT-000077", "speaker"), strict=False,
      **dict(FREE, listed="Evonik", org_id=ORG["Evonik Corporation"]))
plant("an explicit form under a hold, without the ruling's note", "owner ruling 2026-11-20 note and hold disagree",
      base=RT, org_id=RT["org_id"], edition_year="2024", notes=RT["notes"].replace(P_RULING, ""), strict=False)
plant("the ruling's note on a row under no hold", "owner ruling 2026-11-20 note and hold disagree", **FREE,
      notes=AMPP["notes"] + P_RULING)
plant("an abroad row whose listed country is not the org's HQ country", "abroad row without a listed country", base=MEX,
      notes=MEX["notes"].replace("(United States of America)", "(Germany)"), edition_year="2026",
      org_id=ORG["Hexcel Corporation"], listed="Hexcel Corporation", strict=False)
plant("a national row with a foreign edition_state", "abroad row without a listed country", **FREE,
      edition_state="Germany")
plant("a tier other than A", "verification_tier is not A", **FREE, verification_tier="B")
plant("evidence_date set to the read date on a list that prints its as-of date",
      "evidence_date is not the list's as-of date", **FREE, evidence_date="2026-11-19")
plant("an EXPOPLAST row without its edition name", "edition_name is not the name", base=first("EVT-000081", "exhibitor"),
      org_id=ORG["Hexcel Corporation"], listed="Hexcel Corporation", edition_name="", strict=False)
plant("a pre-show list's row without the pre-show note", "pre-show note and the list's as-of date disagree", **FREE,
      notes=AMPP["notes"].replace(" Pre-show list: the organizer's list predates the edition.", ""))
plant("a pre-show note on a list read after its edition (Carbon Fiber agenda)", "pre-show note and the list's as-of",
      base=first("EVT-000074", "speaker"), org_id=ORG["Arkema Inc."], listed="Arkema Inc.",
      notes=first("EVT-000074", "speaker")["notes"] + " Pre-show list: the organizer's list predates the edition.")
print(f"{sum(ok)} of {len(ok)} controls failed check.py as required")
sys.exit(0 if all(ok) else 1)
