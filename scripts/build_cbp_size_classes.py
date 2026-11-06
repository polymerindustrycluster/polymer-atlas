#!/usr/bin/env python3
"""Build CBP establishment-by-employment-size-class reference data (polymer NAICS).

Reference data only: the outputs under docs/denominators/ are official-source
denominators, NOT canonical Atlas data (never merged into data/). CBP is a
different frame from the QCEW denominators in the same folder (see
docs/denominators/CBP_SIZE_CLASSES.md): the two are never blended in one ratio.

Source: U.S. Census Bureau County Business Patterns (CBP) 2023 bulk text files
(no API, no key):
    https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23us.zip   (nation)
    https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23st.zip   (states)
    https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip   (counties)
County names only (never data) come from the Census reference file
    https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt
Record layouts (verified field names): the "U.S." (2018-2023), "State" (2020-)
and "County" (2020-2023) layouts linked from
    https://www.census.gov/programs-surveys/cbp/technical-documentation/record-layouts.html

Fields used: naics, lfo (nation/state files; '-' = all legal forms; the county
file has no lfo column and is all-forms), est (total establishments) and the
establishment-count size-class columns n<5, n5_9, n10_19, n20_49, n50_99,
n100_249, n250_499, n500_999, n1000. Per the layouts those establishment-count
fields have no noise flag; the only flag value is 'N' ("Not available or not
comparable"). The methodology page says that beginning with reference year 2017
a cell is published only if it holds three or more establishments. This script
NEVER turns an 'N' cell into zero: the estab value is written empty and
estab_flag stays 'N'. The total (EST) is always as published.

Filters: NAICS 326, 3261, 3262, 3252, 3259 (CBP stores them padded, e.g.
'326///'); US (all legal forms), the 50 states + DC, and every Ohio (39) and
Pennsylvania (42) county that has a row (the PIC-18 counties are inside Ohio).
The county zip is stream-filtered row by row; it is never loaded whole.

Stdlib only. Usage:
    python3 scripts/build_cbp_size_classes.py --raw-dir /tmp/claude-0/cbp_raw
    python3 scripts/build_cbp_size_classes.py --tables-md > tables.md
Missing raw files are downloaded into --raw-dir. A failed fetch is reported on
stderr as BLOCKED and the script exits non-zero (nothing is filled with zeros).
"""
import argparse
import csv
import hashlib
import io
import os
import sys
import urllib.request
import zipfile
from collections import OrderedDict

YEAR = 2023
BASE = "https://www2.census.gov/programs-surveys/cbp/datasets/2023/"
FILES = OrderedDict([
    ("us", ("cbp23us.zip", "cbp23us.txt")),
    ("state", ("cbp23st.zip", "cbp23st.txt")),
    ("county", ("cbp23co.zip", "cbp23co.txt")),
])
COUNTY_NAMES_URL = "https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt"
COUNTY_NAMES_FILE = "national_county2020.txt"
UA = {"User-Agent": "polymer-atlas-cbp-reference-build (research; johnpswan@gmail.com)"}

# CBP pads NAICS to 6 characters with '/'.
NAICS = OrderedDict([
    ("326///", ("326", "Plastics and Rubber Products Manufacturing")),
    ("3261//", ("3261", "Plastics Product Manufacturing")),
    ("3262//", ("3262", "Rubber Product Manufacturing")),
    ("3252//", ("3252", "Resin, Synthetic Rubber, and Artificial and Synthetic Fibers and Filaments Manufacturing")),
    ("3259//", ("3259", "Other Chemical Product and Preparation Manufacturing")),
])
# (CBP column, size_code, label). CBP's first class is "<5" (formerly "1 to 4"):
# per CBP methodology it includes establishments that reported no mid-March paid
# employees but paid wages at some time in the year.
SIZES = [
    ("n<5", "lt5", "<5 employees (CBP '<5', formerly 1-4)"),
    ("n5_9", "5_9", "5-9 employees"),
    ("n10_19", "10_19", "10-19 employees"),
    ("n20_49", "20_49", "20-49 employees"),
    ("n50_99", "50_99", "50-99 employees"),
    ("n100_249", "100_249", "100-249 employees"),
    ("n250_499", "250_499", "250-499 employees"),
    ("n500_999", "500_999", "500-999 employees"),
    ("n1000", "1000plus", "1,000+ employees"),
]
BANDS = OrderedDict([
    ("<20", ["lt5", "5_9", "10_19"]),
    ("20-99", ["20_49", "50_99"]),
    ("100+", ["100_249", "250_499", "500_999", "1000plus"]),
])
from regions import PIC18

PIC_COUNTIES = OrderedDict(("39" + fips, name + " County") for fips, name in [
    ("005", "Ashland"), ("007", "Ashtabula"), ("029", "Columbiana"), ("035", "Cuyahoga"),
    ("043", "Erie"), ("055", "Geauga"), ("077", "Huron"), ("085", "Lake"),
    ("093", "Lorain"), ("099", "Mahoning"), ("103", "Medina"), ("133", "Portage"),
    ("139", "Richland"), ("151", "Stark"), ("153", "Summit"), ("155", "Trumbull"),
    ("157", "Tuscarawas"), ("169", "Wayne"),
] if name in PIC18)
assert {n.removesuffix(" County") for n in PIC_COUNTIES.values()} == set(PIC18)
# Top-15 NAICS 326 gap states, in the rank order of docs/denominators/README.md
# ("Top 15 areas by gap (QCEW minus strict Atlas), NAICS 326").
TOP15 = ["CA", "TX", "FL", "MI", "IL", "GA", "IN", "WI", "NY", "NC", "SC", "NJ", "TN", "MN", "MO"]
STATE_FIPS_TO_USPS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT",
    "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL",
    "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD",
    "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE",
    "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
    "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV",
    "55": "WI", "56": "WY",
}
USPS_TO_FIPS = {v: k for k, v in STATE_FIPS_TO_USPS.items()}
OUT_FIELDS = ("year", "geo_level", "geo_fips", "geo_usps", "geo_name", "naics", "naics_title",
              "size_code", "size_label", "estab", "estab_flag", "estab_total_row",
              "legal_form", "source_file")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure(raw_dir, name, url):
    dest = os.path.join(raw_dir, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return dest
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
    except Exception as exc:  # noqa: BLE001 - report and stop, never fill
        if os.path.exists(dest):
            os.remove(dest)
        sys.exit("BLOCKED: could not fetch %s (%s)" % (url, exc))
    return dest


def stream_rows(zip_path, member):
    """Yield dict rows from one text member, lowercase header, streaming."""
    with zipfile.ZipFile(zip_path) as zf, zf.open(member) as fh:
        yield from csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1", newline=""))


def load_county_names(path):
    names = {}
    with open(path, encoding="latin-1", newline="") as f:
        for r in csv.DictReader(f, delimiter="|"):
            names[r["STATEFP"] + r["COUNTYFP"]] = (r["COUNTYNAME"], r["STATE"])
    return names


def cell(raw):
    """Return (int or None, flag). 'N' -> (None, 'N'); never zero for a suppressed cell."""
    v = raw.strip()
    if v == "N" or v == "":
        return None, (v or "N")
    return int(v), ""


def build(raw_dir):
    paths = {}
    for key, (zname, _member) in FILES.items():
        paths[key] = ensure(raw_dir, zname, BASE + zname)
    names_path = ensure(raw_dir, COUNTY_NAMES_FILE, COUNTY_NAMES_URL)
    cnames = load_county_names(names_path)
    for fips, nm in PIC_COUNTIES.items():
        got = cnames.get(fips, ("<missing>", ""))[0]
        if got != nm:
            sys.exit("ABORT: PIC-18 FIPS %s expected %r, Census reference file says %r" % (fips, nm, got))

    out = []  # one dict per output row
    seen = set()

    def emit(level, fips, usps, name, nkey, row, lfo, src):
        code, title = NAICS[nkey]
        est = int(row["est"])
        key = (level, fips, code)
        if key in seen:
            sys.exit("ABORT: duplicate key %r" % (key,))
        seen.add(key)
        base = dict(year=YEAR, geo_level=level, geo_fips=fips, geo_usps=usps, geo_name=name,
                    naics=code, naics_title=title, estab_total_row=est, legal_form=lfo,
                    source_file=src)
        out.append(dict(base, size_code="all", size_label="All establishments (EST)",
                        estab=est, estab_flag=""))
        pub = 0
        has_n = False
        for col, scode, label in SIZES:
            val, flag = cell(row[col])
            if val is not None:
                pub += val
            else:
                has_n = True
            out.append(dict(base, size_code=scode, size_label=label,
                            estab="" if val is None else val, estab_flag=flag))
        if not has_n and pub != est:
            sys.exit("ABORT: %s %s %s: no N cell but size classes sum %d != EST %d"
                     % (level, fips, code, pub, est))

    for r in stream_rows(paths["us"], FILES["us"][1]):
        if r["naics"] in NAICS and r["lfo"] == "-":
            emit("US", "US", "US", "United States", r["naics"], r, "-", FILES["us"][1])
    for r in stream_rows(paths["state"], FILES["state"][1]):
        if r["naics"] in NAICS and r["lfo"] == "-":
            usps = STATE_FIPS_TO_USPS.get(r["fipstate"])
            if usps is None:
                sys.exit("ABORT: unexpected state FIPS %s" % r["fipstate"])
            emit("state", r["fipstate"], usps, usps, r["naics"], r, "-", FILES["state"][1])
    for r in stream_rows(paths["county"], FILES["county"][1]):
        if r["fipstate"] in ("39", "42") and r["naics"] in NAICS:
            fips = r["fipstate"] + r["fipscty"]
            nm, usps = cnames.get(fips, ("", STATE_FIPS_TO_USPS[r["fipstate"]]))
            emit("county", fips, usps, nm, r["naics"], r, "(all; no lfo column)", FILES["county"][1])
    return out, paths, names_path


def write_csv(out, dest):
    with open(dest, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS, lineterminator="\n")
        w.writeheader()
        for r in out:
            w.writerow(r)


# ---------------------------------------------------------------- tables ----

def index(out):
    """(level, fips, naics) -> {'est': int, 'cells': {size_code: int|None}}"""
    idx = {}
    for r in out:
        d = idx.setdefault((r["geo_level"], r["geo_fips"], r["naics"]), {"cells": {}})
        if r["size_code"] == "all":
            d["est"] = int(r["estab"])
        else:
            d["cells"][r["size_code"]] = None if r["estab_flag"] == "N" else int(r["estab"])
    return idx


def band_stats(parts):
    """parts: list of (est, cells). Returns est_total, resid, {band: (pub, has_n)}."""
    est = sum(p[0] for p in parts)
    pub_all = 0
    bands = {b: [0, False] for b in BANDS}
    for _e, cells in parts:
        for b, codes in BANDS.items():
            for c in codes:
                v = cells.get(c)
                if v is None:
                    bands[b][1] = True
                else:
                    bands[b][0] += v
                    pub_all += v
    return est, est - pub_all, {b: tuple(v) for b, v in bands.items()}


def pct(x):
    return "%.1f%%" % (100.0 * x)


def share_cell(est, resid, pub, has_n):
    """Share of EST. Exact when the band has no N cell; else lower-upper bound where the
    upper bound adds every establishment sitting in N cells (EST - published cells)."""
    lo = pub / est
    if not has_n or resid == 0:
        return pct(lo)
    hi = (pub + resid) / est
    return "%s-%s" % ("%.1f" % (100 * lo), pct(hi))


def band_row(label, parts):
    est, resid, bands = band_stats(parts)
    cells = [share_cell(est, resid, *bands[b]) for b in BANDS]
    nflag = "yes (%d estab in N cells)" % resid if resid else "no"
    return "| %s | %s | %s | %s |" % (label, "{:,}".format(est), " | ".join(cells), nflag)


def parts_for(idx, level, fips_list, naics):
    parts, missing = [], []
    for f in fips_list:
        d = idx.get((level, f, naics))
        if d is None:
            missing.append(f)
        else:
            parts.append((d["est"], d["cells"]))
    return parts, missing


def fmt(v, comma=True):
    return "N" if v is None else ("{:,}".format(v) if comma else str(v))


def tables_md(out):
    idx = index(out)
    L = []
    hdr_band = "| Geography | Establishments (EST) | <20 employees | 20-99 | 100+ | Any N-flagged cell? |\n|---|---:|---:|---:|---:|---|"

    # 1. national 326 by size class
    d = idx[("US", "US", "326")]
    L.append("#### Table 1. United States, NAICS 326, CBP 2023: establishments by employment-size class\n")
    L.append("Unit and filter: **employer establishments** (CBP `EST` and `N*` fields), NAICS 326 (2017 NAICS), all legal forms, United States (50 states + DC), mid-March 2023 employment-size class, all published (no `N` flag in any national cell).\n")
    L.append("| Size class (CBP column) | Establishments | Share of 326 EST |\n|---|---:|---:|")
    for col, scode, label in SIZES:
        v = d["cells"][scode]
        L.append("| %s (`%s`) | %s | %s |" % (label, col, fmt(v), pct(v / d["est"]) if v is not None else "N"))
    L.append("| **All (EST)** | **%s** | 100.0%% |\n" % "{:,}".format(d["est"]))

    # 2. national bands, five NAICS
    L.append("#### Table 2. United States, CBP 2023: share of establishments by band, five NAICS\n")
    L.append("Unit and filter: **share of employer establishments** in the NAICS, all legal forms, United States. Bands are sums of CBP size classes: <20 = `<5` + `5-9` + `10-19` (below OSHA ITA's 20-employee reach); 20-99 = `20-49` + `50-99`; 100+ = `100-249` + `250-499` + `500-999` + `1000+`. No national cell is `N`, so bands are exact.\n")
    L.append(hdr_band)
    for nk, (code, title) in NAICS.items():
        parts, _ = parts_for(idx, "US", ["US"], code)
        L.append(band_row("US, NAICS %s" % code, parts))
    L.append("")

    # 3. top-15 gap states, 326
    L.append("#### Table 3. Top-15 gap states, NAICS 326, CBP 2023: share of establishments by band\n")
    L.append("Unit and filter: **share of employer establishments**, NAICS 326, all legal forms, state-level CBP rows, in the NAICS 326 gap-rank order of `docs/denominators/README.md` (QCEW minus strict Atlas; that ranking uses QCEW and is not recomputed here). Where a band contains an `N` cell the cell shows `low-high%`: low = published cells only; high = low plus every establishment sitting in `N` cells (`EST` minus published cells), a bound and not an estimate.\n")
    L.append(hdr_band)
    for usps in TOP15:
        parts, miss = parts_for(idx, "state", [USPS_TO_FIPS[usps]], "326")
        L.append(band_row(usps, parts) if parts else "| %s | no row | | | | |" % usps)
    L.append("")
    L.append("#### Table 3b. Top-15 gap states, NAICS 326, CBP 2023: establishments by size class\n")
    L.append("Unit and filter: **employer establishments**, NAICS 326, all legal forms. `N` = CBP's flag for a not-available cell; it is not zero. Last column = establishments in `N` cells (`EST` minus published cells; arithmetic residual, not an official value).\n")
    L.append("| State | EST | <5 | 5-9 | 10-19 | 20-49 | 50-99 | 100-249 | 250-499 | 500-999 | 1000+ | In N cells |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for usps in TOP15:
        d = idx.get(("state", USPS_TO_FIPS[usps], "326"))
        if d is None:
            L.append("| %s | no row |" % usps)
            continue
        resid = d["est"] - sum(v for v in d["cells"].values() if v is not None)
        L.append("| %s | %s | %s | %s |" % (usps, "{:,}".format(d["est"]),
                 " | ".join(fmt(d["cells"][s]) for _c, s, _l in SIZES), resid))
    L.append("")

    # 4. PIC-18
    L.append("#### Table 4. PIC-18 counties, NAICS 326, CBP 2023: share of establishments by band\n")
    L.append("Unit and filter: **share of employer establishments**, NAICS 326, all legal forms, county-level CBP rows (the county file has no legal-form column). The `PIC-18 sum` row adds the 18 counties' published cells; its `N`-cell residual is summed over counties, so its bounds are for the sum of published county rows. Bounds as in Table 3.\n")
    L.append(hdr_band)
    pic_fips = list(PIC_COUNTIES)
    for f in pic_fips:
        parts, miss = parts_for(idx, "county", [f], "326")
        label = "%s (%s)" % (PIC_COUNTIES[f].replace(" County", ""), f)
        L.append(band_row(label, parts) if parts else "| %s | no row | | | | |" % label)
    parts, miss = parts_for(idx, "county", pic_fips, "326")
    L.append(band_row("**PIC-18 sum** (%d of 18 counties with a row)" % len(parts), parts))
    L.append("")
    L.append("#### Table 4b. PIC-18 counties, NAICS 326, CBP 2023: establishments by size class\n")
    L.append("Unit and filter: **employer establishments**, NAICS 326, all legal forms. `N` is not zero.\n")
    L.append("| County (FIPS) | EST | <5 | 5-9 | 10-19 | 20-49 | 50-99 | 100-249 | 250-499 | 500-999 | 1000+ | In N cells |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    tot = {s: 0 for _c, s, _l in SIZES}
    tn = {s: False for _c, s, _l in SIZES}
    est_t = resid_t = 0
    for f in pic_fips:
        d = idx.get(("county", f, "326"))
        label = "%s (%s)" % (PIC_COUNTIES[f].replace(" County", ""), f)
        if d is None:
            L.append("| %s | no row |" % label)
            continue
        resid = d["est"] - sum(v for v in d["cells"].values() if v is not None)
        est_t += d["est"]
        resid_t += resid
        for s, v in d["cells"].items():
            if v is None:
                tn[s] = True
            else:
                tot[s] += v
        L.append("| %s | %s | %s | %s |" % (label, d["est"], " | ".join(fmt(d["cells"][s]) for _c, s, _l in SIZES), resid))
    L.append("| **PIC-18 sum of published cells** | **%s** | %s | %s |" % (
        est_t, " | ".join(("%s%s" % (tot[s], "+N" if tn[s] else "")) for _c, s, _l in SIZES), resid_t))
    L.append("")
    L.append("`+N` in the sum row marks a class where at least one county cell is `N`, so the figure is a published-cells-only lower bound.\n")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw-dir", default="/tmp/claude-0/cbp_raw")
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--out-csv", default=os.path.join(here, "..", "docs", "denominators", "cbp_size_classes_polymer.csv"))
    ap.add_argument("--tables-md", action="store_true", help="print the markdown tables to stdout instead of writing the CSV")
    args = ap.parse_args()
    os.makedirs(args.raw_dir, exist_ok=True)
    out, paths, names_path = build(args.raw_dir)
    for p in list(paths.values()) + [names_path]:
        print("sha256 %s  %s" % (sha256(p), os.path.basename(p)), file=sys.stderr)
    if args.tables_md:
        print(tables_md(out))
        return
    write_csv(out, args.out_csv)
    print("wrote %d rows to %s" % (len(out), os.path.normpath(args.out_csv)), file=sys.stderr)


if __name__ == "__main__":
    main()
