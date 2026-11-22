#!/usr/bin/env python3
"""Check for PR last-activity-street-leg-2026-11-22. Run from the repo root:
  python3 tasks/last-activity-street-leg-2026-11-22/check.py [--base origin/main]
Asserts: (1) inputs/ match SHA256SUMS; (2) re-running the derivation from inputs/ reproduces the two data columns
exactly; (3) no other column of any sites row changed, and no row was added or removed, against --base; (4) every
dated site has a tier-A extract row at its own street, by an independent test (house number in the quote and a shared name word; not street_key); (5) no email or phone pattern in any CSV of this folder; (6) the check itself fails on a planted site that keeps a date
with a different street. Exit 0 = pass."""
import argparse, csv, hashlib, io, shutil, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import derive_last_activity as d

csv.field_size_limit(10**9)
LAST2 = ("last_activity_date", "last_activity_source")


def rows(path_or_text, text=False):
    f = io.StringIO(path_or_text) if text else open(path_or_text, newline="", encoding="utf-8")
    return list(csv.DictReader(f))


def check(data: Path, base: str, label="") -> list:
    errs = []
    inp = HERE / "inputs"
    # (1) inputs
    for line in (inp / "SHA256SUMS").read_text().splitlines():
        h, name = line.split()
        if hashlib.sha256((inp / name).read_bytes()).hexdigest() != h:
            errs.append(f"inputs/{name} does not match SHA256SUMS")
    # (2) replay
    best, _stats, _rej, files, _streets = d.derive(data, inp / "witness_extract_sites_inspection.csv", inp / "witness_extract_sites_ita.csv")
    now = {}
    for fp in files:
        for r in rows(fp):
            now[r["site_id"]] = r
            want = best.get(r["site_id"])
            exp = (want[0].isoformat(), want[1]) if want else ("", "")
            if (r["last_activity_date"], r["last_activity_source"]) != exp:
                errs.append(f"{r['site_id']}: columns {(r['last_activity_date'], r['last_activity_source'])} != derivation {exp}")
    # (3) nothing else changed
    old = {}
    for fp in files:
        old.update({r["site_id"]: r for r in rows(subprocess.check_output(["git", "show", f"{base}:data/{fp.name}"], cwd=ROOT, text=True), text=True)})
    if set(old) != set(now):
        errs.append(f"site rows added/removed: +{len(set(now) - set(old))} -{len(set(old) - set(now))}")
    for sid in set(old) & set(now):
        for c in old[sid]:
            if c not in LAST2 and old[sid][c] != now[sid][c]:
                errs.append(f"{sid}: column {c} changed")
    # (4) independent street test on every dated site
    import re
    SUFFIX = {"street", "avenue", "road", "drive", "boulevard", "highway", "parkway", "lane", "court", "circle", "place",
              "north", "south", "east", "west", "suite", "building", "route", "trail", "terrace", "square", "northeast",
              "northwest", "southeast", "southwest", "county", "hwy", "ave", "blvd", "pkwy", "pky", "ste", "trl", "cir", "ter", "tpke"}
    words = lambda x: {w for w in re.findall(r"[a-z]{3,}", (x or "").lower())} - SUFFIX
    WORDS = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"}
    def civic(site, p):                      # the site's first digit-bearing token (or leading number word) appears in the quote
        toks = (site or "").lower().split()
        if toks and toks[0] in WORDS:
            return toks[0] in (p or "").lower().split() or WORDS[toks[0]] in re.findall(r"\d+", p or "")
        t = next((t for t in toks if re.search(r"\d", t)), None)
        return bool(t) and all(n in re.findall(r"\d+", p or "") for n in re.findall(r"\d+", t))
    ok = lambda site, p: civic(site, p) and (not words(site) or bool(words(site) & words(p)))
    ext = {}
    for kind in ("inspection", "ita"):
        for r in rows(inp / f"witness_extract_sites_{kind}.csv"):
            if r["match_tier"] == "A":
                ext.setdefault(r["record_id"], []).append(r["street_as_printed"])
    for sid, r in now.items():
        if not r["last_activity_date"]:
            continue
        if not r["street_address"].strip() or not any(ok(r["street_address"], x) for x in ext.get(sid, [])):
            errs.append(f"{sid}: dated, but no tier-A extract row at its street by the independent test (street {r['street_address']!r})")
    # (6) no individual contact detail in the files this folder publishes
    em = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    ph = re.compile(r"(?<!\d)(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)|(?<!\d)\d{10}(?!\d)")
    for f in sorted(HERE.rglob("*.csv")):
        for ln, line in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
            if em.search(line) or ph.search(line):
                errs.append(f"email or phone pattern at {f.relative_to(HERE)}:{ln}")
    return errs


def plant(data: Path) -> str:
    """Give a site that the derivation cleared for a different street its old date back; return its id."""
    cleared = next(r for r in rows(HERE / "CLEARED_SITES.csv") if r["reason"] == "different_street")
    fp = next(p for p in data.glob("sites_*.csv") if f"\n{cleared['site_id']}," in p.read_text(encoding="utf-8"))
    lines = fp.read_text(encoding="utf-8").split("\n")
    i = next(i for i, l in enumerate(lines) if l.startswith(cleared["site_id"] + ","))
    lines[i] = lines[i].rsplit(",", 2)[0] + f",{cleared['was_last_activity_date']},{cleared['was_last_activity_source']}"
    fp.write_text("\n".join(lines), encoding="utf-8")
    return cleared["site_id"]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--base", default="origin/main"); a = ap.parse_args()
    errs = check(ROOT / "data", a.base)
    for e in errs[:20]:
        print("FAIL", e)
    if errs:
        print(f"FAIL: {len(errs)} problems on the real data")
        return 1
    with tempfile.TemporaryDirectory() as tmp:                       # (5) the check must catch a planted defect
        shutil.copytree(ROOT / "data", Path(tmp) / "data")
        sid = plant(Path(tmp) / "data")
        planted = check(Path(tmp) / "data", a.base)
    if not any(e.startswith(sid) for e in planted):
        print(f"FAIL: planted site {sid} (date kept with a different street) was NOT caught")
        return 1
    print(f"PASS: columns replay from inputs/; only the two columns differ from {a.base}; planted {sid} caught ({len(planted)} errors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
