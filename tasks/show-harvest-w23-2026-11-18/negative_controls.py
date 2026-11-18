"""Negative controls for this pass's review_decisions.csv loader (decisions.py) and check.py: every counterexample the
cross-family review of PR #384 raised. Each case mutates a file, runs check.py, expects it to fail, then restores the
file's original bytes. Exit 0 = every control failed check.py as required.
    python3 tasks/show-harvest-w23-2026-11-18/negative_controls.py      (from the repo root)"""
import csv, io, subprocess, sys
from pathlib import Path

T = Path("tasks/show-harvest-w23-2026-11-18")
DEC, PK, TAB = T / "review_decisions.csv", T / "participation_append.csv", Path("data/event_participation.csv")
orig = {p: p.read_bytes() for p in (DEC, PK, TAB)}
dec_lines = orig[DEC].decode("utf-8").split("\n")  # header + 7 rows + trailing ""
baystar_npe = next(l for l in dec_lines if l.startswith("accept,npe-the-plastics-show"))
trelleborg = next(l for l in dec_lines if ",Trelleborg," in l)


def run(label, files):
    for p, b in files.items():
        p.write_bytes(b)
    r = subprocess.run([sys.executable, str(T / "check.py")], capture_output=True, text=True)
    for p, b in orig.items():
        p.write_bytes(b)
    last = (r.stderr or r.stdout).strip().splitlines()[-1][:150]
    print(("PASS " if r.returncode else "MISS ") + label, "|", last)
    return r.returncode != 0


def dec(lines):
    return {DEC: "\n".join(lines).encode("utf-8")}


ok = []
# loader cases (both reviewers)
i = dec_lines.index(baystar_npe)
ok.append(run("bogus row before a valid duplicate", dec(dec_lines[:i] + [baystar_npe.replace("accept,", "bogus,", 1)] + dec_lines[i:])))
ok.append(run("extra field before a valid duplicate", dec(dec_lines[:i] + [baystar_npe + ",extra"] + dec_lines[i:])))
ok.append(run("hold then accept, same key", dec(dec_lines[:i] + [baystar_npe.replace("accept,", "hold,", 1)] + dec_lines[i:])))
ok.append(run("exact duplicate row", dec(dec_lines[:i] + [baystar_npe] + dec_lines[i:])))
ok.append(run("empty org_id", dec([l.replace(",ORG-002944,", ",,") for l in dec_lines])))
ok.append(run("empty reason on an accept", dec([l if l != baystar_npe else l.rsplit(",", 1)[0].rsplit(',"', 1)[0] + ',' for l in dec_lines])))
ok.append(run("event_id not the show's series", dec([l.replace(",EVT-000069,exhibitor,2027,Trelleborg", ",EVT-999999,exhibitor,2027,Trelleborg") for l in dec_lines])))
ok.append(run("accept with wrong event_id", dec([l if l != baystar_npe else l.replace(",EVT-000001,", ",EVT-999999,") for l in dec_lines])))
ok.append(run("hold names another org (Trelleborg -> ORG-003071)", dec([l if l != trelleborg else l.replace("ORG-004243", "ORG-003071") for l in dec_lines])))
ok.append(run("unknown org_id", dec([l if l != trelleborg else l.replace("ORG-004243", "ORG-999999") for l in dec_lines])))
ok.append(run("bad year", dec([l if l != trelleborg else l.replace(",2027,Trelleborg", ",27,Trelleborg") for l in dec_lines])))
ok.append(run("bad role", dec([l if l != trelleborg else l.replace(",exhibitor,2027,Trelleborg", ",attendee,2027,Trelleborg") for l in dec_lines])))

# row cases (check.py)
rows = list(csv.DictReader(io.StringIO(orig[PK].decode("utf-8"))))
fields = list(rows[0])
def plant(label, **kw):
    extra = dict(rows[0], participation_id="EVP-999999", **kw)
    b = io.StringIO(); csv.DictWriter(b, fieldnames=fields, lineterminator="\n").writerow(extra)
    return run(label, {PK: orig[PK] + b.getvalue().encode(), TAB: orig[TAB] + b.getvalue().encode()})
src = lambda n: f'x (read 2026-11-09; listed as "{n}")'
ok.append(plant("held Trelleborg listed as 'Trelleborg Corp'", event_id="EVT-000069", edition_year="2027", org_id="ORG-004243", sources=src("Trelleborg Corp")))
ok.append(plant("held Aaron listed as 'Aaron Industries Inc.'", event_id="EVT-000001", edition_year="2027", org_id="ORG-004008", sources=src("Aaron Industries Inc.")))
ok.append(plant("Blueshift with the phrase only", event_id="EVT-000035", edition_year="2027", org_id="ORG-003852", sources=src("Blueshift"),
                notes="Exhibitor name NOT adjudicated the same entity by cross-family review; remains held."))
ok.append(plant("Baystar in the wrong year", event_id="EVT-000001", edition_year="2024", org_id="ORG-003071", sources=src("Baystar"),
                notes="matched a trade name, adjudicated the same entity by cross-family review"))
print(f"{sum(ok)} of {len(ok)} negative controls fail check.py as required")
sys.exit(0 if all(ok) else 1)
