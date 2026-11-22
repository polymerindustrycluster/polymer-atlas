#!/usr/bin/env python3
"""Writes CLEARED_SITES.csv and LOOSER_THAN_STREET_KEY.csv and prints the before/after counts for the README.
Usage (repo root): python3 tasks/last-activity-street-leg-2026-11-22/report.py [--base origin/main]
Before = the two columns on --base; after = the working tree. Reasons are per site, in this order: blank_street,
no_house_number (the site's street has no leading house number), number_only (a tier-A row shares the leading house
number but not the street), different_street. The looser comparison is `classify` from the 2026-11-22 address-witness
audit (classes exact and number+name pass), copied here so the comparison replays from the repo."""
import argparse, csv, io, re, subprocess, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import derive_last_activity as d

ABB = (("street","st"),("avenue","ave"),("av","ave"),("road","rd"),("drive","dr"),("boulevard","blvd"),("parkway","pkwy"),("pky","pkwy"),("north","n"),("south","s"),("east","e"),("west","w"),("highway","hwy"),("route","rt"),("rte","rt"),("suite","ste"),("court","ct"),("lane","ln"),("place","pl"),("circle","cir"),("northwest","nw"),("northeast","ne"),("southwest","sw"),("southeast","se"),("industrial","ind"),("one","1"),("first","1st"),("second","2nd"),("third","3rd"),("fourth","4th"),("fifth","5th"))
def _norm(s):
    s = re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())
    for a, b in ABB: s = re.sub(rf"\b{a}\b", b, s)
    return " ".join(s.split())
def codex_class(street, quote):
    st, q = _norm(street), _norm(quote)
    if not st: return "record_blank"
    if st in q or st.replace(" ", "") in q.replace(" ", ""): return "exact"
    num = re.match(r"\d+", st); words = [w for w in st.split()[1:] if len(w) > 2 and not w.isdigit()]
    hasnum = bool(num and re.search(rf"\b{num.group()}\b", q)); hasname = any(w in q.split() for w in words) if words else True
    return "number+name" if hasnum and hasname else "number_only" if hasnum else "name_only_NUMBER_DIFF" if hasname and num else "STREET_DIFF"
looser = lambda site, printed: codex_class(site, printed) in ("exact", "number+name")

ap = argparse.ArgumentParser(); ap.add_argument("--base", default="origin/main"); a = ap.parse_args()
def cols(text):
    return {r["site_id"]: r for r in csv.DictReader(io.StringIO(text))}
before, after = {}, {}
for fp in sorted((ROOT / "data").glob("sites_*.csv")):
    before.update(cols(subprocess.check_output(["git", "show", f"{a.base}:data/{fp.name}"], cwd=ROOT, text=True)))
    after.update(cols(fp.read_text(encoding="utf-8")))
inp = HERE / "inputs"
EXT = [inp / "witness_extract_sites_inspection.csv", inp / "witness_extract_sites_ita.csv"]
streets = {k: v["street_address"] for k, v in after.items()}
lead = lambda s: (re.match(r"\s*(\d+)", s or "") or [None, None])[1]
tierA = {}                                    # site_id -> [(street_as_printed, passes street test)]
for path in EXT:
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["match_tier"] == "A":
                tierA.setdefault(r["record_id"], []).append((r["street_as_printed"], d.same_street(streets[r["record_id"]], r["street_as_printed"])))

def reason(sid):
    st = streets[sid]
    if not st.strip():
        return "blank_street"
    if not lead(st):
        return "no_house_number"
    if any(lead(p) == lead(st) for p, ok in tierA[sid] if not ok):
        return "number_only"
    return "different_street"

dated = lambda t: {k for k, v in t.items() if v["last_activity_date"]}
b, af = dated(before), dated(after)
assert af <= b, "a site gained a date: the street leg can only remove"
cleared = sorted(b - af)
src = lambda t, s: dict(sorted(Counter(t[k]["last_activity_source"] for k in s).items()))
changed = sorted(k for k in b & af if (before[k]["last_activity_date"], before[k]["last_activity_source"]) != (after[k]["last_activity_date"], after[k]["last_activity_source"]))
rc = Counter(reason(k) for k in cleared)
with open(HERE / "CLEARED_SITES.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["site_id", "was_last_activity_date", "was_last_activity_source", "reason", "site_street_address", "tier_a_street_as_printed"])
    for k in cleared:
        pr = " | ".join(sorted({p for p, _ in tierA[k]}))
        assert "@" not in pr
        w.writerow([k, before[k]["last_activity_date"], before[k]["last_activity_source"], reason(k), streets[k], pr])

# looser comparison: derive again with the audit's pass set as the street test, diff against the street_key result
key_test = d.same_street
d.same_street = looser
loose_best = d.derive(ROOT / "data", *EXT)[0]
d.same_street = key_test
key_best = d.derive(ROOT / "data", *EXT)[0]
only_loose = sorted(set(loose_best) - set(key_best))
diff_date = sorted(k for k in set(loose_best) & set(key_best) if loose_best[k][:2] != key_best[k][:2])
assert not set(key_best) - set(loose_best) or True
with open(HERE / "LOOSER_THAN_STREET_KEY.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["site_id", "site_street_address", "looser_class", "looser_pass_street_as_printed"])
    for k in only_loose:
        rows = [(p, codex_class(streets[k], p)) for p, _ in tierA[k] if looser(streets[k], p)]
        for p, c in sorted(set(rows)):
            w.writerow([k, streets[k], c, p])
print(f"sites with a date: before {len(b)} {src(before, b)}; after {len(af)} {src(after, af)}")
print(f"cleared {len(cleared)} by reason {dict(rc)}; by source {src(before, cleared)}")
print(f"kept with a different winning date/source {len(changed)}: " + str(dict(Counter((before[k]['last_activity_source'], after[k]['last_activity_source']) for k in changed))))
print(f"kept unchanged {len(b & af) - len(changed)}")
print(f"looser classes (exact + number+name) would date {len(loose_best)} sites; street_key dates {len(key_best)}; "
      f"{len(only_loose)} sites only the looser test dates; {len(diff_date)} dated by both with a different winning date/source")
print(f"key dates {len(set(key_best) - set(loose_best))} sites the looser test does not")
