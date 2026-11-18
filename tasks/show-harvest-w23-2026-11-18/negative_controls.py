"""Negative controls for this pass's review_decisions.csv loader (decisions.py) and check.py: every counterexample the
cross-family review of PR #384 raised. Each case mutates a file, runs check.py, and passes only if check.py fails
WITH THE EXPECTED MESSAGE (a failure for some other reason proves nothing); then the file's original bytes are
restored. Planted rows are otherwise valid (their source URL, show key and event agree), so only the rule under test
can catch them. Exit 0 = every control failed as required.
    python3 tasks/show-harvest-w23-2026-11-18/negative_controls.py      (from the repo root)

Not reachable here: the loader's "both held and accepted" rule (no real org has a legal name that is another org's
trade name at these events, so any such pair first fails "hold: listed name is not this org's legal name") and
build.py's "show_key is not a harvested show" (needs the staging harvest; check.py loads without it)."""
import csv, io, subprocess, sys
from pathlib import Path

T = Path("tasks/show-harvest-w23-2026-11-18")
DEC, PK, TAB = T / "review_decisions.csv", T / "participation_append.csv", Path("data/event_participation.csv")
orig = {p: p.read_bytes() for p in (DEC, PK, TAB)}
dec_lines = orig[DEC].decode("utf-8").split("\n")  # header + 7 rows + trailing ""
baystar_npe = next(l for l in dec_lines if l.startswith("accept,npe-the-plastics-show"))
trelleborg = next(l for l in dec_lines if ",Trelleborg," in l)
ok = []


def run(label, files, expect):
    for p, b in files.items():
        p.write_bytes(b)
    r = subprocess.run([sys.executable, str(T / "check.py")], capture_output=True, text=True)
    for p, b in orig.items():
        p.write_bytes(b)
    out = r.stdout + r.stderr
    good = r.returncode != 0 and expect in out
    print(("PASS " if good else "MISS ") + label, "| expected:", expect, "|", out.strip().splitlines()[-1][:120])
    ok.append(good)


def dec(lines):
    return {DEC: "\n".join(lines).encode("utf-8")}


def swap(line, old, new):
    return dec([l if l != line else l.replace(old, new, 1) for l in dec_lines])


# --- loader cases (decisions.py, via check.py)
i = dec_lines.index(baystar_npe)
before = lambda extra: dec(dec_lines[:i] + [extra] + dec_lines[i:])  # noqa: E731
run("bogus row before a valid duplicate", before(baystar_npe.replace("accept,", "bogus,", 1)), "decision must be hold or accept")
run("extra field before a valid duplicate", before(baystar_npe + ",extra"), "needs 8 non-empty fields")
run("hold before an accept, same key", before(baystar_npe.replace("accept,", "hold,", 1)), "hold: listed name is not this org's legal name")
run("exact duplicate row", before(baystar_npe), "duplicate key (show_key")
run("empty org_id", dec([l.replace(",ORG-002944,", ",,") for l in dec_lines]), "needs 8 non-empty fields")
run("empty reason on an accept", swap(baystar_npe, baystar_npe[baystar_npe.index(',"'):], ","), "needs 8 non-empty fields")
run("event_id not the show's series", swap(trelleborg, ",EVT-000069,", ",EVT-999999,"), "show_key's series is not event_id")
run("accept with a wrong event_id", swap(baystar_npe, ",EVT-000001,", ",EVT-999999,"), "show_key's series is not event_id")
run("hold names another org", swap(trelleborg, "ORG-004243", "ORG-003071"), "hold: listed name is not this org's legal name")
run("unknown org_id", swap(trelleborg, "ORG-004243", "ORG-999999"), "org_id is not an active/unknown organization")
run("decision naming an inactive org", swap(trelleborg, "ORG-004243", "ORG-002893"), "org_id is not an active/unknown organization")
run("bad year", swap(trelleborg, ",2027,Trelleborg", ",27,Trelleborg"), "edition_year must be 4 ASCII digits")
run("non-ASCII year digits", swap(trelleborg, ",2027,Trelleborg", ",٢٠٢٧,Trelleborg"), "edition_year must be 4 ASCII digits")
run("bad role", swap(trelleborg, ",exhibitor,", ",attendee,"), "role must be exhibitor, sponsor or speaker")
run("show_key with a trailing space", swap(trelleborg, "exhibition:2027,", "exhibition:2027 ,"), "without surrounding spaces")
run("show_key without a year", swap(trelleborg, "exhibition:2027,", "exhibition,"), "show_key must be <slug>:<4 digits>")
run("same event, year and name under a second show_key",
    before(baystar_npe.replace("npe-the-plastics-show:2027", "npe-the-plastics-show:2028", 1)), "duplicate key (event_id")

# --- row cases (check.py). Each planted row is valid except for the defect under test.
rows = list(csv.DictReader(io.StringIO(orig[PK].decode("utf-8"))))
fields = list(rows[0])
SHOW = {"EVT-000001": "npe-the-plastics-show:2027", "EVT-000069": "ppxxiii-plastic-pipes-conference-and-exhibition:2027",
        "EVT-000035": "sampe-conference-and-exhibition:2027", "EVT-000047": "fakuma:2027",
        "EVT-000017": "spe-annual-blow-molding-conference-abc:2027"}
URL = {r["event_id"]: r["evidence_source_url"] for r in rows}
LEGAL = "Exhibitor name matched to the org by exact normalized legal name; "
TRADE = "Exhibitor name matched a trade name, adjudicated the same entity by cross-family review: test; "


def plant(label, expect, event, year, org, listed, show=None, prefix=LEGAL, url=None, cite=None):
    url = url or URL[event]
    extra = dict(rows[0], participation_id="EVP-999999", event_id=event, edition_year=year, org_id=org,
                 evidence_source_url=url, sources=f'{cite or url} (read 2026-11-09; listed as "{listed}")',
                 notes=f"{prefix}list banked in staging (harvest-2026-11, {show or SHOW[event]}).")
    b = io.StringIO(); csv.DictWriter(b, fieldnames=fields, lineterminator="\n").writerow(extra)
    run(label, {PK: orig[PK] + b.getvalue().encode(), TAB: orig[TAB] + b.getvalue().encode()}, expect)


HELD = "held by review_decisions.csv"
plant("held Trelleborg listed as 'Trelleborg Corp'", HELD, "EVT-000069", "2027", "ORG-004243", "Trelleborg Corp")
plant("held Aaron listed as 'Aaron Industries Inc.'", HELD, "EVT-000001", "2027", "ORG-004008", "Aaron Industries Inc.")
plant("held Aaron Industries in another year (agy)", HELD, "EVT-000001", "2026", "ORG-004008", "Aaron Industries, Inc.")
plant("held Trelleborg at PP XXIII under another show key", HELD, "EVT-000069", "2027", "ORG-004243", "Trelleborg",
      show="ppxxiii-plastic-pipes-conference-and-exhibition:2028")
plant("Blueshift with the adjudication phrase but no accept", "Blueshift Materials, Inc.", "EVT-000035", "2027",
      "ORG-003852", "Blueshift", prefix="Exhibitor name NOT adjudicated the same entity by cross-family review; ")
plant("Baystar in the wrong year", "Bayport Polymers LLC", "EVT-000001", "2024", "ORG-003071", "Baystar", prefix=TRADE)
plant("Baystar under a show the accept does not name", "Bayport Polymers LLC", "EVT-000001", "2027", "ORG-003071",
      "Baystar", show="npe-the-plastics-show:2028", prefix=TRADE)
plant("held Trelleborg under NPE's event with PP XXIII's show in its notes (codex)", "is not a series of EVT-000001",
      "EVT-000001", "2027", "ORG-004243", "Trelleborg", show=SHOW["EVT-000069"])
plant("notes with a malformed show slug (agy)", "notes lack the staging show key", "EVT-000001", "2027", "ORG-003780",
      "ADG Solutions", show="---:2027")
plant("legal-name row whose notes show is another event's", "is not a series of EVT-000017", "EVT-000017", "2026",
      "ORG-003780", "ADG Solutions", show=SHOW["EVT-000001"])
plant("ambiguous name key: ACH Foam Technologies, two orgs (codex)", "listed name's key is held by", "EVT-000001",
      "2027", "ORG-004921", "ACH Foam Technologies")
plant("sources cites an excluded list, evidence_source_url does not (codex)", "sources does not cite evidence_source_url",
      "EVT-000001", "2027", "ORG-003780", "ADG Solutions",
      cite="https://www.blowmoldingdivision.org/corporate-education-sponsors")
plant("both URL fields cite an excluded list", "excluded list", "EVT-000017", "2026", "ORG-003780", "ADG Solutions",
      url="https://www.blowmoldingdivision.org/corporate-education-sponsors")
print(f"{sum(ok)} of {len(ok)} negative controls fail check.py with the expected message")
sys.exit(0 if all(ok) else 1)
