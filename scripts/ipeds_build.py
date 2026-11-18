#!/usr/bin/env python3
"""Generate the IPEDS completions layer (SCHEMA §4.23) from data/ipeds/raw_ipeds_national.json.

    python3 scripts/ipeds_build.py            # writes data/ipeds_{institutions,programs,completions}.csv
    python3 scripts/ipeds_build.py --check    # exit 1 if the committed tables differ from a fresh derivation

The three tables are GENERATED: an edit made in them is overwritten here and refused by validator V-63. Fix the
raw file (scripts/ipeds_fetch.py, scripts/ipeds_fetch_nces.py) or this derivation instead. Ported from
polymer-programs-db build_db.py (a9d89b5) with its year-label refusals unchanged; the hand-researched layers stayed
behind (tasks/ipeds-layer-2026-11-18/README.md).

THE TABLES ANSWER "WHAT PROGRAMS EXIST", which IPEDS does not answer directly. IPEDS publishes completions per year,
and a program with no completions in a year is absent from that year. A program is therefore the UNION over all years
of one (institution, CIP, award level), with first_year, last_year and totals. `status` is derived: `active` if the
last year with completions is the final year of the series, `ended` if completions stopped two or more years before,
`unclear` for the year between (one quiet year is routine).
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def data_dir():
    return Path(os.environ.get("ATLAS_DATA_DIR") or ROOT / "data")


# IPEDS RE-CODED CERTIFICATE AWARD LEVELS IN 2020. Through 2018: 1 = Cert <1yr, 3 = Cert 1-2yr; 2019 is the
# transition year (level-1 rows arrive with award_level NULL); from 2020: 31 = Cert 12wk-1yr, 32 = Cert 1-2yr. Keyed
# without canonicalisation, one continuous certificate becomes a program that "ended 2018" and one that "started
# 2020"; that once manufactured a fake 19-program closure spike (CORRECTIONS in docs/IPEDS.md, 2026-08-21).
CERT_CANON = {1: 31, 2: 32, 3: 32, 5: 33, 6: 33, 30: 31, 31: 31, 32: 32, 33: 33}
# One label per canonical certificate level, naming the codes merged into it (a first-seen raw label would call a
# code-30 "under 12 weeks" program "12wk-1yr": codex, #388). Other levels keep the source's label.
CANON_AWARD = {31: "Cert under 1yr (codes 1, 30, 31)", 32: "Cert 1-2yr (codes 2, 3, 32)", 33: "Cert 1-4yr (codes 5, 6, 33)"}
DEGREE_LEVEL = {
    -1: "unknown",  # award_level absent in the source; completions still real
    1: "certificate", 2: "certificate", 3: "certificate", 30: "certificate", 31: "certificate", 32: "certificate",
    33: "certificate", 4: "associate", 5: "certificate", 6: "certificate", 7: "bachelor", 8: "postgrad certificate",
    9: "master", 20: "doctorate", 21: "doctorate", 22: "doctorate", 23: "doctorate", 24: "doctorate",
}

# 2020 in the Urban Institute mirror is 2019's counts republished under the 2020 codebook (verified 2026-08-26). It is
# dropped at ingest, before any lifetime total is computed, and only while it EXACTLY repeats 2019.
QUARANTINED_YEARS = {2020}

# ONE YEAR CONVENTION: the FALL of the academic year (2023 = awards conferred 2023-24 = NCES C2024_A). Urban served
# 2021 and 2022 a year late and never served C2023_A, which ipeds_fetch_nces.py supplies. Urban rows (no "source")
# are re-filed by URBAN_RELABEL; NCES rows carry the file year and move back one. The raw file keeps labels as served.
URBAN_RELABEL = {2021: 2020, 2022: 2021}

INST_FIELDS = ["unitid", "name", "state", "city", "sector", "control", "url", "closed_after"]
PROG_FIELDS = ["program_key", "unitid", "cip", "cip_title", "cip_group", "award_level", "award", "level",
               "first_year", "last_year", "years_seen", "total_awards", "status"]
COMP_FIELDS = ["program_key", "year", "awards"]
TABLES = {"ipeds_institutions.csv": INST_FIELDS, "ipeds_programs.csv": PROG_FIELDS, "ipeds_completions.csv": COMP_FIELDS}


def canon_level(lvl):
    return CERT_CANON.get(lvl, lvl)


def fall_label(r):
    if (r.get("source") or "").startswith("NCES"):
        return r["year"] - 1
    return URBAN_RELABEL.get(r["year"], r["year"])


def _signature(rows, year):
    """Total awards per (institution, CIP) in one Urban year (totals: 2019 holds one count under a NULL level that
    2020 splits across two codes, so a row-level comparison cannot be exact)."""
    totals = Counter()
    for r in rows:
        if r["year"] == year and not r.get("source"):
            totals[(r["unitid"], r["cip"])] += r["awards"]
    return +totals


def file_years(raw):
    """Quarantine, then put every row on the fall label. Refuses (SystemExit), rather than builds, on any sign the map
    is wrong: a quarantined year that no longer repeats its predecessor, a label clash, a hole, labels out of their
    served order, or a series that does not start and end where the metadata says it should."""
    rows, meta = raw["rows"], raw["meta"]
    for q in QUARANTINED_YEARS:
        dup, prev = _signature(rows, q), _signature(rows, q - 1)
        if dup and dup != prev:
            changed = sorted(set(dup) ^ set(prev) | {k for k in dup if dup[k] != prev.get(k)})
            raise SystemExit(f"refusing to build: quarantined {q} no longer repeats {q - 1} "
                             f"({len(changed)} institution-CIP totals differ, e.g. {changed[:3]}); "
                             f"re-check the mirror before dropping it")
    rows = [r for r in rows if not (r["year"] in QUARANTINED_YEARS and not r.get("source"))]
    origin, relabelled = {}, []
    for r in rows:
        y = fall_label(r)
        origin.setdefault(y, set()).add((r.get("source") or "urban", r["year"]))
        relabelled.append(dict(r, year=y))
    clashes = {y: sorted(o) for y, o in origin.items() if len(o) > 1}
    if clashes:
        raise SystemExit("refusing to build: two served years landed on one year: " + str(clashes))
    years = sorted(origin)
    holes = sorted(set(range(years[0], years[-1] + 1)) - set(years))
    if holes:
        raise SystemExit("refusing to build: the year series has holes at " + str(holes))
    for family in ("urban", "NCES"):  # a swapped map (2021 <-> 2022) passes the clash and hole checks and fails here
        pairs = sorted((served, y) for y, o in origin.items() for src, served in o if src.startswith(family))
        if any(b[1] <= a[1] for a, b in zip(pairs, pairs[1:])):
            raise SystemExit(f"refusing to build: {family} labels are out of served order: {pairs}")
    nces = (meta.get("nces_direct") or {}).get("years")
    want_end = max(nces) - 1 if nces else meta["years"][1]
    if (years[0], years[-1]) != (meta["years"][0], want_end):
        raise SystemExit(f"refusing to build: series {years[0]}-{years[-1]}, metadata says "
                         f"{meta['years'][0]}-{want_end}; a year is missing at an end")
    return relabelled, years


def derive(raw):
    """(institutions, programs, completions, years) as lists of dicts of strings, in their committed order."""
    rows, years = file_years(raw)
    final_year = years[-1]
    s = lambda v: "" if v is None else str(v)
    insts = [{"unitid": u, "name": d.get("name") or f"unitid {u}", "state": s(d.get("state")), "city": s(d.get("city")),
              "sector": s(d.get("sector")), "control": s(d.get("control")), "url": s(d.get("url")),
              "closed_after": s(d.get("closed_after"))}
             for u, d in sorted(raw["directory"].items(), key=lambda kv: int(kv[0]))]
    # The union across years IS the enumeration. NULL award levels (21 rows, 17 with real completions) are kept at
    # level -1 / "unknown" rather than dropped, so totals stay honest.
    prog = {}
    for r in rows:
        lvl = -1 if r["award_level"] is None else canon_level(r["award_level"])
        p = prog.setdefault((r["unitid"], r["cip"], lvl), {
            "cip_title": r["cip_title"], "group": r["group"],
            "award": "Unreported award level" if r["award_level"] is None else CANON_AWARD.get(lvl, r["award"]),
            "years": {}})
        p["years"][r["year"]] = p["years"].get(r["year"], 0) + r["awards"]
    progs, comps = [], []
    named = {int(u) for u in raw["directory"]}
    for (unitid, cip, lvl), p in sorted(prog.items()):
        active = {y: n for y, n in p["years"].items() if n > 0}
        if not active:  # a row of pure zeros is IPEDS reporting an absence, not evidence of a program
            continue
        if unitid not in named:  # parity alone cannot catch this: both tables would be derived without it
            raise SystemExit(f"refusing to build: program {unitid}-{cip}-{lvl} has no directory entry for {unitid}")
        first, last = min(active), max(active)
        key = f"{unitid}-{cip}-{lvl}"
        progs.append({"program_key": key, "unitid": str(unitid), "cip": cip, "cip_title": p["cip_title"],
                      "cip_group": p["group"], "award_level": str(lvl), "award": p["award"],
                      "level": DEGREE_LEVEL.get(lvl, "unknown"), "first_year": str(first), "last_year": str(last),
                      "years_seen": str(len(active)), "total_awards": str(sum(active.values())),
                      "status": "active" if last >= final_year else "unclear" if last >= final_year - 1 else "ended"})
        comps += [{"program_key": key, "year": str(y), "awards": str(n)} for y, n in sorted(p["years"].items())]
    return insts, progs, comps, years


def render(fields, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader(); w.writerows(rows)
    return buf.getvalue()


def expected(data=None):
    """{table file name: exact expected text} from the raw file in the data directory."""
    data = data or data_dir()
    raw = json.load(open(data / "ipeds" / "raw_ipeds_national.json", encoding="utf-8"))
    insts, progs, comps, _ = derive(raw)
    return dict(zip(TABLES, (render(f, r) for f, r in zip(TABLES.values(), (insts, progs, comps)))))


def mismatches(data=None):
    """Table files that are missing or differ from a fresh derivation of the raw file (validator V-63)."""
    data = data or data_dir()
    return [f for f, text in expected(data).items()
            if not (data / f).exists() or (data / f).read_bytes().decode("utf-8") != text]


def summary(progs, comps, years):
    final = years[-1]
    poly = {p["program_key"]: p for p in progs if p["cip_group"] == "polymer"}
    series = Counter()
    for c in comps:
        if c["program_key"] in poly:
            series[int(c["year"])] += int(c["awards"])
    sustained = {p["unitid"] for p in poly.values() if int(p["total_awards"]) >= 50
                 and int(p["last_year"]) - int(p["first_year"]) >= 10}
    current = {poly[c["program_key"]]["unitid"] for c in comps
               if c["program_key"] in poly and c["year"] == str(final) and int(c["awards"]) > 0}
    return series, len(sustained), len(sustained & current), final


def main():
    data = data_dir()
    if "--check" in sys.argv:
        bad = mismatches(data)
        print("ipeds tables: " + ("differ from a fresh derivation: " + ", ".join(bad) if bad else "match the raw file"))
        sys.exit(1 if bad else 0)
    for f, text in expected(data).items():
        (data / f).write_bytes(text.encode("utf-8"))
    raw = json.load(open(data / "ipeds" / "raw_ipeds_national.json", encoding="utf-8"))
    insts, progs, comps, years = derive(raw)
    series, sus, sus_now, final = summary(progs, comps, years)
    print(f"ipeds layer {years[0]}-{final}: {len(insts)} institutions, {len(progs)} programs, {len(comps)} program-years")
    print("  polymer completions: " + ", ".join(f"{y}: {series[y]}" for y in (1991, 2007, 2016, 2019, 2023)))
    print(f"  sustained (>=50 awards, >=10-year span, one program): {sus} institutions, {sus_now} with completions in {final}")


if __name__ == "__main__":
    main()
