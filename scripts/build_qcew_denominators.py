#!/usr/bin/env python3
"""Build QCEW polymer-industry denominator reference files from BLS open data.

Reference data only: the outputs under docs/denominators/ are official-source
denominators, NOT canonical Atlas data (never merged into data/).

Source: BLS Quarterly Census of Employment and Wages (QCEW) open-data CSV
slices, annual averages ("a"), one file per (year, industry):
    https://data.bls.gov/cew/data/api/<YEAR>/a/industry/<INDUSTRY>.csv
Area titles:
    https://data.bls.gov/cew/doc/titles/area/area_titles.csv
Docs: https://www.bls.gov/cew/additional-resources/open-data/csv-data-slices.htm

Filters: own_code == 5 (private ownership); state rows = agglvl 55-58
(state, NAICS 3/4/5/6-digit), county rows = agglvl 75-78 (county, same), and
national rows = agglvl 15-18 (area US000). Disclosure handling: for rows with
disclosure_code 'N' BLS publishes annual_avg_emplvl, total_annual_wages and
avg_annual_pay as ZEROS (they are withheld, not zero). This script NEVER carries
those zeros: those three fields are written empty and disclosure_code stays 'N'.
annual_avg_estabs is kept as published on N rows (BLS withholds employment and
wages, not the establishment count; the raw estabs value is non-zero on N rows
and county values reconcile to state totals - see docs/denominators/README.md).
A field that is blank in the source stays blank.

Stdlib only. Usage:
    python3 scripts/build_qcew_denominators.py --raw-dir /tmp/claude-0/qcew_raw
    python3 scripts/build_qcew_denominators.py            # downloads to a temp dir
    python3 scripts/build_qcew_denominators.py --coverage-md   # also print
        the Atlas-vs-QCEW coverage tables (markdown) to stdout

Raw files in --raw-dir are named <YEAR>_<INDUSTRY>.csv and area_titles.csv.
A failed fetch is reported on stderr as BLOCKED and that slice is absent from
the outputs (never filled with zeros).
"""
import argparse
import csv
import glob
import os
import sys
import tempfile
import urllib.request
from collections import defaultdict

YEARS = (2023, 2024)
INDUSTRIES = ("326", "3261", "3262", "3252", "325211", "325212", "3259", "325991")
SLICE_URL = "https://data.bls.gov/cew/data/api/{year}/a/industry/{ind}.csv"
TITLES_URL = "https://data.bls.gov/cew/doc/titles/area/area_titles.csv"
STATE_AGGLVL = {"55", "56", "57", "58"}
COUNTY_AGGLVL = {"75", "76", "77", "78"}
NATIONAL_AGGLVL = {"15", "16", "17", "18"}
NUM_FIELDS = ("annual_avg_estabs", "annual_avg_emplvl", "total_annual_wages", "avg_annual_pay")
OUT_FIELDS = ("year", "area_fips", "area_title", "industry_code", "own_code", "agglvl_code",
              "annual_avg_estabs", "annual_avg_emplvl", "total_annual_wages",
              "avg_annual_pay", "disclosure_code")
PIC12 = {  # county FIPS -> expected BLS title (verified against area_titles.csv at build)
    "39007": "Ashtabula County, Ohio", "39035": "Cuyahoga County, Ohio",
    "39055": "Geauga County, Ohio", "39085": "Lake County, Ohio",
    "39093": "Lorain County, Ohio", "39099": "Mahoning County, Ohio",
    "39103": "Medina County, Ohio", "39133": "Portage County, Ohio",
    "39151": "Stark County, Ohio", "39153": "Summit County, Ohio",
    "39155": "Trumbull County, Ohio", "39169": "Wayne County, Ohio",
}
STATE_FIPS_TO_USPS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT",
    "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL",
    "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD",
    "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE",
    "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
    "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV",
    "55": "WI", "56": "WY", "72": "PR",
}
UA = {"User-Agent": "polymer-atlas-qcew-reference-build (research; johnpswan@gmail.com)"}


def fetch(url, dest):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())


def ensure_raw(raw_dir, download):
    """Return (set of missing slice labels, errors dict)."""
    os.makedirs(raw_dir, exist_ok=True)
    wanted = [(None, TITLES_URL, os.path.join(raw_dir, "area_titles.csv"))]
    for y in YEARS:
        for i in INDUSTRIES:
            wanted.append(((y, i), SLICE_URL.format(year=y, ind=i),
                           os.path.join(raw_dir, f"{y}_{i}.csv")))
    errors = {}
    for key, url, dest in wanted:
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            continue
        if not download:
            errors[key or "titles"] = "not in raw-dir and download disabled"
            continue
        try:
            fetch(url, dest)
        except Exception as e:  # recorded, never papered over
            errors[key or "titles"] = f"{type(e).__name__}: {e} ({url})"
            if os.path.exists(dest):
                os.remove(dest)
    return errors


def load_titles(raw_dir):
    p = os.path.join(raw_dir, "area_titles.csv")
    with open(p, newline="", encoding="utf-8-sig") as f:
        return {r["area_fips"]: r["area_title"] for r in csv.DictReader(f)}


def parse_slice(path, year, ind, titles):
    """Yield (kind, outrow) for own_code 5 rows of interest."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["own_code"] != "5" or r["industry_code"] != ind or r["year"] != str(year):
                continue
            if r["qtr"] != "A":
                continue
            fips, agg = r["area_fips"], r["agglvl_code"]
            if agg in STATE_AGGLVL:
                kind = "state"
            elif agg in NATIONAL_AGGLVL and fips == "US000":
                kind = "national"
            elif agg in COUNTY_AGGLVL and fips[:2] in ("39", "42"):
                kind = "county"
            else:
                continue
            suppressed = r["disclosure_code"] == "N"
            out = {
                "year": r["year"], "area_fips": fips,
                "area_title": titles.get(fips, ""), "industry_code": ind,
                "own_code": r["own_code"], "agglvl_code": agg,
                "disclosure_code": r["disclosure_code"],
            }
            for k in NUM_FIELDS:
                withheld = suppressed and k != "annual_avg_estabs"
                out[k] = "" if withheld else r[k]
            yield kind, out


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows.sort(key=lambda r: (r["year"], r["area_fips"], r["industry_code"]))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def atlas_numerators(repo):
    """{(usps, code): [all_rows, strict_rows]} over data/sites_*.csv, US sites only.

    all   = any tier, any operating_status, naics_primary startswith code
    strict= operating_status in (active, unknown) AND verification_tier in A/B/C
    State = the physical `state` column of the row.
    """
    codes = INDUSTRIES
    res = defaultdict(lambda: [0, 0])
    for p in sorted(glob.glob(os.path.join(repo, "data", "sites_*.csv"))):
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("country", "US") not in ("US", ""):
                    continue
                n = r["naics_primary"]
                if not n:
                    continue
                strict = (r["operating_status"] in ("active", "unknown")
                          and r["verification_tier"] in ("A", "B", "C"))
                for c in codes:
                    if n.startswith(c):
                        res[(r["state"], c)][0] += 1
                        if strict:
                            res[(r["state"], c)][1] += 1
    return res


def coverage_md(state_rows, repo):
    num = atlas_numerators(repo)
    q = {}  # (usps, ind) -> estabs or None(suppressed) for 2023
    for r in state_rows:
        if r["year"] != "2023" or not r["area_fips"].endswith("000"):
            continue
        usps = STATE_FIPS_TO_USPS.get(r["area_fips"][:2])
        if r["area_fips"] == "US000" or not usps:
            continue
        q[(usps, r["industry_code"])] = (int(r["annual_avg_estabs"])
                                         if r["annual_avg_estabs"] != "" else None)  # None = blank in source
    states = sorted({s for s, _ in q})
    lines = []
    for code in ("326", "3261", "3262", "3252", "3259"):
        rows = []
        for s in states:
            qe = q.get((s, code))
            a_all, a_strict = num.get((s, code), [0, 0])
            rows.append((s, qe, a_all, a_strict))
        rows.sort(key=lambda t: (-(t[1] if t[1] is not None else -1), t[0]))
        tq = sum(t[1] for t in rows if t[1] is not None)
        lines.append(f"\n#### NAICS {code}\n")
        lines.append("| State | QCEW 2023 private estabs | Atlas all rows | Atlas strict | "
                     "All / QCEW | Strict / QCEW | Gap (QCEW - strict) |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for s, qe, a, st in rows:
            if qe is None:
                lines.append(f"| {s} | suppressed | {a} | {st} | n/a | n/a | n/a |")
            else:
                pa = f"{100*a/qe:.1f}%" if qe else "n/a"
                ps = f"{100*st/qe:.1f}%" if qe else "n/a"
                lines.append(f"| {s} | {qe} | {a} | {st} | {pa} | {ps} | {qe-st} |")
        sup = [s for s, qe, _, _ in rows if qe is None]
        ta = sum(t[2] for t in rows)
        ts = sum(t[3] for t in rows)
        lines.append(f"| **Sum of listed states** | **{tq}** | **{ta}** | **{ts}** | "
                     f"{100*ta/tq:.1f}% | {100*ts/tq:.1f}% | {tq-ts} |")
        if sup:
            lines.append(f"\nSuppressed state cells excluded from the QCEW sum: {', '.join(sup)}.")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--raw-dir", help="dir holding <year>_<ind>.csv + area_titles.csv "
                    "(missing files are downloaded unless --no-download)")
    ap.add_argument("--no-download", action="store_true")
    ap.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--coverage-md", action="store_true")
    a = ap.parse_args()

    raw_dir = a.raw_dir or tempfile.mkdtemp(prefix="qcew_raw_")
    errors = ensure_raw(raw_dir, not a.no_download)
    if "titles" in errors:
        sys.exit(f"BLOCKED: area titles unavailable: {errors['titles']}")
    titles = load_titles(raw_dir)

    for fips, want in PIC12.items():
        if titles.get(fips) != want:
            sys.exit(f"PIC-12 FIPS check FAILED: {fips} -> {titles.get(fips)!r}, expected {want!r}")
    print("PIC-12 county FIPS verified against area_titles.csv:", file=sys.stderr)
    for fips, t in PIC12.items():
        print(f"  {fips} {titles[fips]}", file=sys.stderr)

    state_rows, county_rows = [], []
    for y in YEARS:
        for i in INDUSTRIES:
            if (y, i) in errors:
                print(f"BLOCKED slice {y}/{i}: {errors[(y, i)]}", file=sys.stderr)
                continue
            for kind, row in parse_slice(os.path.join(raw_dir, f"{y}_{i}.csv"), y, i, titles):
                if kind in ("state", "national"):
                    state_rows.append(row)
                else:
                    county_rows.append(row)

    out = os.path.join(a.repo, "docs", "denominators")
    write_csv(os.path.join(out, "qcew_state_polymer_2023_2024.csv"), state_rows)
    write_csv(os.path.join(out, "qcew_county_polymer_ohio_pa_2023_2024.csv"), county_rows)
    print(f"wrote {len(state_rows)} state/national rows and {len(county_rows)} county rows",
          file=sys.stderr)
    if a.coverage_md:
        print(coverage_md(state_rows, a.repo))


if __name__ == "__main__":
    main()
