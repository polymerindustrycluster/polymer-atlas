#!/usr/bin/env python3
"""Build the polymer-industry "economic pulse" reference set (context data).

Reference data, NOT canonical Atlas data: nothing here is merged into data/ and
nothing here changes a record, tier, status or count in the Atlas.

Writes (relative to the repo root):
  docs/indicators/indicators_series.csv   long format: source, series_id, title,
                                          units, frequency, geo, date, value
  docs/indicators/catalog.csv             one row per series
  docs/indicators/README.md               only the block between the
                                          SUMMARY:BEGIN / SUMMARY:END markers,
                                          and only with --update-readme

Sources (all pulled live, series IDs verified against each API's own metadata
endpoint before any data is kept; a missing or mismatched ID aborts the run):
  FRED  (St. Louis Fed)  PPI by industry, industrial production, CES employment
  BLS   API v2           CES average hourly earnings, NAICS 326 (employment is
                         pulled only to cross-check FRED)
  BEA   Regional         SAGDP2 (current $) and SAGDP9 (chained 2017 $), line 33
                         "Plastics and rubber products manufacturing (326)"
  EIA   API v2           industrial electricity price, industrial natural gas
                         price, Mont Belvieu propane spot price

SECRETS: API keys are read from environment variables only (FRED_API_KEY,
BEA_API_KEY, BLS_API_KEY, EIA_API_KEY). Keys are never written anywhere: cache
filenames are hashes of the request with the key removed, BEA responses are
scrubbed of the echoed UserID before they are cached, every cached body is
checked for key strings, and URLs recorded in catalog.csv use <KEY>.

Usage:
  set -a; . /root/.config/polymer-atlas/api_keys.env; set +a
  python3 scripts/build_indicators.py [--refresh] [--update-readme]
Stdlib only. Raw responses are cached in /tmp/claude-0/indicators_raw/ (re-runs
read the cache unless --refresh is given, so a re-run reproduces the same files).
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "docs" / "indicators"
QCEW_STATE = REPO / "docs" / "denominators" / "qcew_state_polymer_2023_2024.csv"
DEFAULT_CACHE = Path("/tmp/claude-0/indicators_raw")
RETRIEVED = "2026-11-01"
START_YEAR = 2016  # monthly pulls start 2016-01; BEA LAST10 = 2016..2025

KEY_VARS = ("FRED_API_KEY", "BEA_API_KEY", "BLS_API_KEY", "EIA_API_KEY")

FRED_SERIES = [
    # (series_id, short role note)
    ("PCU325211325211", "PPI plastics material and resin manufacturing (NAICS 325211)"),
    ("PCU325212325212", "PPI synthetic rubber manufacturing (NAICS 325212)"),
    ("PCU32613261", "PPI plastics product manufacturing (NAICS 3261)"),
    ("PCU326326", "PPI plastics and rubber products manufacturing (NAICS 326)"),
    ("PCU32623262", "PPI rubber product manufacturing (NAICS 3262)"),
    ("IPG326S", "Industrial production, NAICS 326"),
    ("IPG3261S", "Industrial production, NAICS 3261"),
    ("IPG3262S", "Industrial production, NAICS 3262"),
    ("IPG3252S", "Industrial production, NAICS 3252"),
    ("CES3232600001", "All employees, NAICS 326"),
]

# BLS: (series_id, expected measure_data_type substring, units label, publish?)
BLS_SERIES = [
    ("CES3232600003", "AVERAGE HOURLY EARNINGS OF ALL EMPLOYEES", "Dollars per hour", True),
    ("CES3232600008", "AVERAGE HOURLY EARNINGS OF PRODUCTION AND NONSUPERVISORY EMPLOYEES",
     "Dollars per hour", True),
    ("CES3232600001", "ALL EMPLOYEES, THOUSANDS", "Thousands of persons", False),  # cross-check only
]

BEA_LINE = "33"
BEA_LINE_EXPECT = "Plastics and rubber products manufacturing (326)"
BEA_TABLES = [("SAGDP2", "Millions of current dollars"), ("SAGDP9", "Millions of chained 2017 dollars")]

STATE_POSTAL = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
    "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
    "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
    "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
    "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}

EIA_STATES = ["OH", "PA", "US"]
EIA_GAS_AREA = {"OH": "SOH", "PA": "SPA", "US": "NUS"}
EIA_PROPANE = "EER_EPLLPA_PF4_Y44MB_DPG"


# --------------------------------------------------------------------------
# secrets and HTTP with key-free cache
# --------------------------------------------------------------------------
def load_keys():
    keys = {}
    for v in KEY_VARS:
        val = os.environ.get(v, "")
        if not val:
            sys.exit(f"error: environment variable {v} is not set "
                     "(load it with: set -a; . /root/.config/polymer-atlas/api_keys.env; set +a)")
        keys[v] = val
    return keys


class Http:
    def __init__(self, keys, cache_dir, refresh):
        self.keys = keys
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.refresh = refresh
        self.network_calls = 0

    def redact(self, text):
        for k in self.keys.values():
            text = text.replace(k, "<KEY>")
        return text

    def _cache_path(self, method, clean_url, clean_body):
        h = hashlib.sha256(f"{method}\n{clean_url}\n{clean_body}".encode()).hexdigest()[:24]
        return self.cache_dir / f"{h}.json"

    def _scrub_and_check(self, text):
        """Drop echoed credentials (BEA echoes UserID) and refuse to cache a key."""
        try:
            obj = json.loads(text)
        except ValueError:
            obj = None
        if isinstance(obj, dict):
            req = obj.get("BEAAPI", {}).get("Request", {})
            for p in req.get("RequestParam", []):
                if str(p.get("ParameterName", "")).upper() in ("USERID", "REGISTRATIONKEY", "API_KEY"):
                    p["ParameterValue"] = "<KEY>"
            text = json.dumps(obj, sort_keys=True)
        for k in self.keys.values():
            if k in text:
                raise RuntimeError("API key found in response body; refusing to cache it")
        return text

    def get_json(self, method, url, params, key_param=None, key_value=None, body=None, body_key=None):
        """params: dict of query parameters WITHOUT the key. key_param/key_value is added on the
        wire only. For POST, body is a dict and body_key the field holding the key."""
        clean_url = url + ("?" + urllib.parse.urlencode(sorted(params.items())) if params else "")
        clean_body = json.dumps(body, sort_keys=True) if body is not None else ""
        path = self._cache_path(method, clean_url, clean_body)
        if path.exists() and not self.refresh:
            return json.loads(path.read_text())
        wire = dict(params)
        if key_param:
            wire[key_param] = key_value
        full = url + ("?" + urllib.parse.urlencode(wire) if wire else "")
        data = None
        headers = {"User-Agent": "polymer-atlas-indicators/1.0"}
        if method == "POST":
            wire_body = dict(body)
            if body_key:
                wire_body[body_key] = key_value
            data = json.dumps(wire_body).encode()
            headers["Content-type"] = "application/json"
        last = None
        for attempt in range(4):
            try:
                req = urllib.request.Request(full, data=data, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=90) as r:
                    text = r.read().decode("utf-8")
                self.network_calls += 1
                obj = json.loads(text)
                if "BEAAPI" in obj and "Error" in obj["BEAAPI"]:
                    raise RuntimeError("BEA error " + json.dumps(obj["BEAAPI"]["Error"]))
                cleaned = self._scrub_and_check(text)
                path.write_text(cleaned)
                return json.loads(cleaned)
            except (urllib.error.URLError, RuntimeError, ValueError, TimeoutError) as e:
                last = self.redact(f"{type(e).__name__}: {e}")
                time.sleep(2 * (attempt + 1))
        raise SystemExit(f"error: request failed for {self.redact(clean_url)}: {last}")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


class Collector:
    def __init__(self):
        self.rows = []      # (source, series_id, title, units, frequency, geo, date, value)
        self.catalog = {}   # series_id -> dict

    def add_series(self, source, series_id, title, units, frequency, geo, obs, url, seasonal="", notes=""):
        obs = sorted((d, v) for d, v in obs if v is not None)
        if not obs:
            raise SystemExit(f"error: no usable observations for {series_id}")
        for d, v in obs:
            self.rows.append((source, series_id, title, units, frequency, geo, d, v))
        if frequency.lower() == "monthly":
            have = {d[:7] for d, _ in obs}
            d0, d1 = obs[0][0], obs[-1][0]
            gaps, d = [], d0
            while d < d1:
                if d[:7] not in have:
                    gaps.append(d[:7])
                d = shift_date(d, -1)
            if gaps:
                notes += (f"; {len(gaps)} month(s) with no published value between first and latest "
                          f"observation: " + ", ".join(gaps[:24]) + (" ..." if len(gaps) > 24 else ""))
        self.catalog[series_id] = dict(
            series_id=series_id, source=source, title=title, units=units, frequency=frequency,
            geo=geo, source_url=url, retrieved=RETRIEVED, latest_date=obs[-1][0],
            latest_value=obs[-1][1], first_date=obs[0][0], n_obs=len(obs),
            seasonal_adjustment=seasonal, notes=notes)


def fmt(v):
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return s if s else "0"


# --------------------------------------------------------------------------
# FRED
# --------------------------------------------------------------------------
def pull_fred(http, keys, col):
    base = "https://api.stlouisfed.org/fred"
    for sid, role in FRED_SERIES:
        meta = http.get_json("GET", f"{base}/series", {"series_id": sid, "file_type": "json"},
                             "api_key", keys["FRED_API_KEY"])
        if "seriess" not in meta or not meta["seriess"]:
            raise SystemExit(f"error: FRED series {sid} does not exist")
        m = meta["seriess"][0]
        if m["id"] != sid:
            raise SystemExit(f"error: FRED returned {m['id']} for {sid}")
        p = {"series_id": sid, "file_type": "json", "observation_start": f"{START_YEAR}-01-01"}
        o = http.get_json("GET", f"{base}/series/observations", p, "api_key", keys["FRED_API_KEY"])
        obs = [(x["date"], fnum(x["value"])) for x in o["observations"]]  # "." -> None (skipped)
        url = (f"{base}/series/observations?series_id={sid}&api_key=<KEY>&file_type=json"
               f"&observation_start={START_YEAR}-01-01")
        notes = f"{role}; FRED last_updated {m.get('last_updated', '')}"
        col.add_series("FRED", sid, m["title"], m["units"], m["frequency"], "US", obs, url,
                       m.get("seasonal_adjustment_short", ""), notes)


# --------------------------------------------------------------------------
# BLS API v2
# --------------------------------------------------------------------------
def pull_bls(http, keys, col):
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    this_year = int(RETRIEVED[:4])
    ids = [s[0] for s in BLS_SERIES]
    body = {"seriesid": ids, "startyear": str(START_YEAR), "endyear": str(this_year), "catalog": True}
    d = http.get_json("POST", url, {}, "registrationkey", keys["BLS_API_KEY"], body=body,
                      body_key="registrationkey")
    if d.get("status") != "REQUEST_SUCCEEDED":
        raise SystemExit(f"error: BLS status {d.get('status')} {d.get('message')}")
    got = {s["seriesID"]: s for s in d["Results"]["series"]}
    parsed = {}
    for sid, expect, units, publish in BLS_SERIES:
        s = got.get(sid)
        if not s or not s.get("data"):
            raise SystemExit(f"error: BLS series {sid} returned no data")
        cat = s.get("catalog") or {}
        if expect not in (cat.get("measure_data_type") or ""):
            raise SystemExit(f"error: BLS {sid} measure type {cat.get('measure_data_type')!r} != {expect!r}")
        obs, prelim = [], []
        for x in s["data"]:
            if not re.fullmatch(r"M(0[1-9]|1[0-2])", x["period"]):
                continue
            date = f"{x['year']}-{x['period'][1:]}-01"
            obs.append((date, fnum(x["value"])))
            if any(f.get("code") == "P" for f in x.get("footnotes", []) if f):
                prelim.append(date[:7])
        parsed[sid] = (cat, obs, prelim)
    # cross-check BLS employment against FRED (same series, same data)
    fred_emp = {r[6]: r[7] for r in col.rows if r[1] == "CES3232600001"}
    mism = [(dt, v, fred_emp[dt]) for dt, v in parsed["CES3232600001"][1]
            if dt in fred_emp and abs(v - fred_emp[dt]) > 1e-9]
    xcheck = (f"BLS vs FRED CES3232600001: {len(parsed['CES3232600001'][1])} BLS months, "
              f"{len(mism)} mismatches against FRED over overlapping months")
    print("[bls] " + xcheck)
    col.xcheck = xcheck
    for sid, expect, units, publish in BLS_SERIES:
        if not publish:
            continue
        cat, obs, prelim = parsed[sid]
        title = cat.get("series_title") or sid
        note = "BLS CES; catalog title as served; preliminary months (footnote P): " + (
            ", ".join(prelim) if prelim else "none")
        post = ('POST https://api.bls.gov/publicAPI/v2/timeseries/data/ body={"seriesid":["%s"],'
                '"startyear":"%d","endyear":"%d","registrationkey":"<KEY>","catalog":true}'
                % (sid, START_YEAR, this_year))
        col.add_series("BLS", sid, title, units, "Monthly", "US", obs, post, "SA" if sid.startswith("CES") else "NSA", note)


# --------------------------------------------------------------------------
# BEA Regional
# --------------------------------------------------------------------------
def top_states_by_qcew():
    """Top 10 states by 2024 private NAICS 326 establishments (QCEW file); OH and PA are
    confirmed members and are asserted, not force-added."""
    est = {}
    with open(QCEW_STATE, newline="") as f:
        for r in csv.DictReader(f):
            fips = r["area_fips"]
            if r["industry_code"] == "326" and r["year"] == "2024" and fips.endswith("000") \
                    and fips[:2] in STATE_POSTAL and r["annual_avg_estabs"]:
                est[fips] = int(r["annual_avg_estabs"])
    ranked = sorted(est.items(), key=lambda t: (-t[1], t[0]))[:10]
    fips_list = [k for k, _ in ranked]
    for need in ("39000", "42000"):
        if need not in fips_list:
            raise SystemExit(f"error: {need} not in QCEW top 10; revisit the geography rule")
    return ranked


def pull_bea(http, keys, col):
    ranked = top_states_by_qcew()
    geos = ["00000"] + [k for k, _ in ranked]
    base = "https://apps.bea.gov/api/data"
    common = {"ResultFormat": "JSON"}
    # 1. verify the line code against the table's own parameter values
    for table, _ in BEA_TABLES:
        p = dict(common, method="GetParameterValuesFiltered", datasetname="Regional",
                 TargetParameter="LineCode", TableName=table)
        d = http.get_json("GET", base, p, "UserID", keys["BEA_API_KEY"])
        vals = {x["Key"]: x["Desc"] for x in d["BEAAPI"]["Results"]["ParamValue"]}
        if BEA_LINE_EXPECT not in vals.get(BEA_LINE, ""):
            raise SystemExit(f"error: BEA {table} line {BEA_LINE} is {vals.get(BEA_LINE)!r}")
    # 2. county table: record that no 326 line exists
    d = http.get_json("GET", base, dict(common, method="GetParameterValuesFiltered", datasetname="Regional",
                                        TargetParameter="LineCode", TableName="CAGDP2"),
                      "UserID", keys["BEA_API_KEY"])
    cvals = {x["Key"]: x["Desc"] for x in d["BEAAPI"]["Results"]["ParamValue"]}
    county_mfg = sorted(v.split(": ", 1)[-1] for v in cvals.values() if "anufactur" in v)
    has326 = any("(326)" in v or "lastics" in v for v in cvals.values())
    col.county_note = (f"CAGDP2 (county GDP by industry) lines mentioning manufacturing: {county_mfg}; "
                       f"a NAICS 326 / plastics-and-rubber line exists: {has326}")
    print("[bea] " + col.county_note)
    # 3. state data
    for table, units in BEA_TABLES:
        p = dict(common, method="GetData", datasetname="Regional", TableName=table, LineCode=BEA_LINE,
                 GeoFips=",".join(geos), Year="LAST10")
        d = http.get_json("GET", base, p, "UserID", keys["BEA_API_KEY"])
        res = d["BEAAPI"]["Results"]
        stat = res["Statistic"]
        if BEA_LINE_EXPECT.split(" (")[0] not in stat:
            raise SystemExit(f"error: BEA {table} statistic {stat!r}")
        if res["UnitOfMeasure"] != units:
            raise SystemExit(f"error: BEA {table} unit {res['UnitOfMeasure']!r} != {units!r}")
        upd = " ".join(n["NoteText"] for n in res.get("Notes", []) if n["NoteText"].startswith("Last updated"))
        by = defaultdict(dict)
        names = {}
        skipped = defaultdict(list)
        for r in res["Data"]:
            names[r["GeoFips"]] = r["GeoName"]
            v = fnum(r["DataValue"])
            if v is None:
                skipped[r["GeoFips"]].append(f"{r['TimePeriod']}={r['DataValue']}")
            else:
                by[r["GeoFips"]][r["TimePeriod"]] = v
        for g in geos:
            if g not in by:
                raise SystemExit(f"error: BEA {table} returned no numeric data for {g}")
            geo = "US" if g == "00000" else STATE_POSTAL[g[:2]]
            sid = f"{table}-{BEA_LINE}@{g}"
            obs = [(f"{y}-01-01", v) for y, v in by[g].items()]  # annual; date = year start
            gurl = ("https://apps.bea.gov/api/data?UserID=<KEY>&method=GetData&datasetname=Regional"
                    f"&TableName={table}&LineCode={BEA_LINE}&GeoFips={g}&Year=LAST10&ResultFormat=JSON")
            note = (f"BEA Regional {table} line {BEA_LINE}; {stat}; annual, 'date' is Jan 1 of the data year; "
                    f"{upd}")
            if skipped[g]:
                note += "; non-numeric cells omitted: " + ", ".join(skipped[g])
            if g == "00000":
                note += "; US = BEA national total as published in the state table"
            col.add_series("BEA", sid, f"{stat} - {names[g]}", units, "Annual", geo, obs, gurl, "", note)
    col.bea_geos = geos
    col.qcew_rank = ranked


# --------------------------------------------------------------------------
# EIA API v2
# --------------------------------------------------------------------------
def eia_facets(http, keys, route, facet):
    d = http.get_json("GET", f"https://api.eia.gov/v2/{route}/facet/{facet}", {}, "api_key", keys["EIA_API_KEY"])
    return {f["id"]: f["name"] for f in d["response"]["facets"]}


def eia_data(http, keys, route, params):
    """Paginate (5000-row cap) and return all rows."""
    out, offset = [], 0
    while True:
        p = dict(params, offset=str(offset), length="5000")
        d = http.get_json("GET", f"https://api.eia.gov/v2/{route}/data", p, "api_key", keys["EIA_API_KEY"])
        rows = d["response"]["data"]
        out.extend(rows)
        total = int(d["response"]["total"])
        offset += len(rows)
        if not rows or offset >= total:
            return out


def eia_params(value_field, facets):
    p = {"frequency": "monthly", "data[0]": value_field, "start": f"{START_YEAR}-01",
         "sort[0][column]": "period", "sort[0][direction]": "asc"}
    for fac, vals in facets.items():
        for i, v in enumerate(vals):
            p[f"facets[{fac}][{i}]"] = v
    return p


def eia_url(route, value_field, facets):
    q = ["api_key=<KEY>", "frequency=monthly", f"data[0]={value_field}", f"start={START_YEAR}-01"]
    for fac, vals in facets.items():
        q += [f"facets[{fac}][]={v}" for v in vals]
    return f"https://api.eia.gov/v2/{route}/data?" + "&".join(q)


def pull_eia(http, keys, col):
    # electricity: industrial average retail price
    states = eia_facets(http, keys, "electricity/retail-sales", "stateid")
    sectors = eia_facets(http, keys, "electricity/retail-sales", "sectorid")
    if "IND" not in sectors:
        raise SystemExit("error: EIA sector IND not found")
    for st in EIA_STATES:
        if st not in states:
            raise SystemExit(f"error: EIA stateid {st} not found")
        facets = {"sectorid": ["IND"], "stateid": [st]}
        rows = eia_data(http, keys, "electricity/retail-sales", eia_params("price", facets))
        obs = [(r["period"] + "-01", fnum(r["price"])) for r in rows]
        units = rows[0]["price-units"]
        miss = sorted(r["period"] for r in rows if fnum(r["price"]) is None)
        note = (f"EIA electricity/retail-sales, sector IND ({sectors['IND']}), state {states[st]}; "
                "average retail price of electricity to ultimate customers (cents per kWh)")
        if miss:
            note += "; null months omitted: " + ", ".join(miss)
        col.add_series("EIA", f"electricity/retail-sales:price:IND:{st}",
                       f"Average retail price of electricity, industrial sector - {states[st]}",
                       units.capitalize(), "Monthly", st, obs,
                       eia_url("electricity/retail-sales", "price", facets), "NSA", note)
    # natural gas: industrial price
    areas = eia_facets(http, keys, "natural-gas/pri/sum", "duoarea")
    procs = eia_facets(http, keys, "natural-gas/pri/sum", "process")
    if "PIN" not in procs:
        raise SystemExit("error: EIA process PIN not found")
    for st in EIA_STATES:
        area = EIA_GAS_AREA[st]
        if area not in areas:
            raise SystemExit(f"error: EIA duoarea {area} not found")
        facets = {"process": ["PIN"], "duoarea": [area]}
        rows = eia_data(http, keys, "natural-gas/pri/sum", eia_params("value", facets))
        sids = {r["series"] for r in rows}
        if len(sids) != 1:
            raise SystemExit(f"error: EIA gas {area} returned series {sids}")
        sid = sids.pop()
        obs = [(r["period"] + "-01", fnum(r["value"])) for r in rows]
        miss = sorted(r["period"] for r in rows if fnum(r["value"]) is None)
        note = f"EIA natural-gas/pri/sum, process PIN ({procs['PIN']}), duoarea {area}; EIA series {sid}"
        if miss:
            note += "; null months omitted (EIA published no value): " + ", ".join(miss)
        title = rows[0]["series-description"].split(" (")[0]
        col.add_series("EIA", f"natural-gas/pri/sum:{sid}", title, "Dollars per thousand cubic feet",
                       "Monthly", st, obs, eia_url("natural-gas/pri/sum", "value", facets), "NSA", note)
    # propane at Mont Belvieu (no ethane spot series exists in EIA spot prices)
    series = eia_facets(http, keys, "petroleum/pri/spt", "series")
    if EIA_PROPANE not in series:
        raise SystemExit("error: EIA propane spot series not found")
    col.eia_spot_series = sorted(series.values())
    col.ethane_available = any("thane" in v and "Propane" not in v for v in series.values())
    facets = {"series": [EIA_PROPANE]}
    rows = eia_data(http, keys, "petroleum/pri/spt", eia_params("value", facets))
    obs = [(r["period"] + "-01", fnum(r["value"])) for r in rows]
    col.add_series("EIA", f"petroleum/pri/spt:{EIA_PROPANE}", series[EIA_PROPANE].replace(" (Dollars per Gallon)", ""),
                   "Dollars per gallon", "Monthly", "Mont Belvieu TX", obs,
                   eia_url("petroleum/pri/spt", "value", facets), "NSA",
                   "EIA petroleum/pri/spt, monthly frequency as served by EIA. "
                   "Feedstock context only. EIA publishes no ethane spot series (spot series list has "
                   f"{len(series)} entries; ethane present: {col.ethane_available})")


# --------------------------------------------------------------------------
# outputs
# --------------------------------------------------------------------------
def write_csvs(col):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "indicators_series.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["source", "series_id", "title", "units", "frequency", "geo", "date", "value"])
        for r in sorted(col.rows, key=lambda r: (r[0], r[1], r[6])):
            w.writerow(list(r[:7]) + [fmt(r[7])])
    cols = ["series_id", "source", "title", "units", "frequency", "geo", "source_url", "retrieved",
            "latest_date", "latest_value", "first_date", "n_obs", "seasonal_adjustment", "notes"]
    with open(OUT_DIR / "catalog.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for sid in sorted(col.catalog, key=lambda s: (col.catalog[s]["source"], s)):
            c = dict(col.catalog[sid])
            c["latest_value"] = fmt(c["latest_value"])
            w.writerow(c)


def series_map(col):
    m = defaultdict(dict)
    for r in col.rows:
        m[r[1]][r[6]] = r[7]
    return m


def shift_date(date, months):
    y, mo = int(date[:4]), int(date[5:7])
    t = y * 12 + (mo - 1) - months
    return f"{t // 12:04d}-{t % 12 + 1:02d}-01"


def pct(cur, prev):
    if prev in (None, 0) or cur is None:
        return "n/a"
    s = f"{(cur / prev - 1) * 100:+.1f}%"
    return "+0.0%" if s == "-0.0%" else s


def changes(col, sid):
    c = col.catalog[sid]
    obs = series_map(col)[sid]
    ld = c["latest_date"]
    step = 12 if c["frequency"] == "Annual" else 1
    d1 = shift_date(ld, 12)
    d5 = shift_date(ld, 60)
    return obs[ld], pct(obs[ld], obs.get(d1)), pct(obs[ld], obs.get(d5)), d1, d5


def period_label(c):
    return c["latest_date"][:4] if c["frequency"] == "Annual" else c["latest_date"][:7]


def build_summary(col):
    L = []
    cat = col.catalog

    def mrow(sid, label):
        v, c1, c5, d1, d5 = changes(col, sid)
        c = cat[sid]
        L.append(f"| {label} | `{sid}` | {c['units']} | {fmt(v)} | {period_label(c)} | {c1} | {c5} |")

    head = ("| Series | ID | Units | Latest | Period | 1-yr change | 5-yr change |\n"
            "|---|---|---|---:|---|---:|---:|")
    sections = [
        ("Prices (PPI, NSA indexes; FRED / BLS)", [
            ("PCU325211325211", "PPI plastics material and resin mfg (325211)"),
            ("PCU325212325212", "PPI synthetic rubber mfg (325212)"),
            ("PCU32613261", "PPI plastics products mfg (3261)"),
            ("PCU32623262", "PPI rubber products mfg (3262)"),
            ("PCU326326", "PPI plastics and rubber products mfg (326)")]),
        ("Output, employment, earnings (national, SA; FRED / BLS)", [
            ("IPG326S", "Industrial production, NAICS 326"),
            ("IPG3261S", "Industrial production, NAICS 3261"),
            ("IPG3262S", "Industrial production, NAICS 3262"),
            ("IPG3252S", "Industrial production, NAICS 3252"),
            ("CES3232600001", "All employees, NAICS 326"),
            ("CES3232600003", "Avg hourly earnings, all employees, NAICS 326"),
            ("CES3232600008", "Avg hourly earnings, production and nonsupervisory, NAICS 326")]),
        ("Energy and feedstock cost context (EIA, monthly, NSA)", [
            ("electricity/retail-sales:price:IND:OH", "Industrial electricity price, Ohio"),
            ("electricity/retail-sales:price:IND:PA", "Industrial electricity price, Pennsylvania"),
            ("electricity/retail-sales:price:IND:US", "Industrial electricity price, US"),
            ("natural-gas/pri/sum:N3035OH3", "Industrial natural gas price, Ohio"),
            ("natural-gas/pri/sum:N3035PA3", "Industrial natural gas price, Pennsylvania"),
            ("natural-gas/pri/sum:N3035US3", "Industrial natural gas price, US"),
            (f"petroleum/pri/spt:{EIA_PROPANE}", "Propane spot price, Mont Belvieu TX")]),
    ]
    for title, items in sections:
        L.append(f"\n**{title}**\n")
        L.append(head)
        for sid, label in items:
            mrow(sid, label)

    # BEA tables
    geos = col.bea_geos
    postal = lambda g: "US" if g == "00000" else STATE_POSTAL[g[:2]]
    us_cur = series_map(col)["SAGDP2-33@00000"]
    latest_y = cat["SAGDP2-33@00000"]["latest_date"]
    y1, y5 = shift_date(latest_y, 12), shift_date(latest_y, 60)
    ly = latest_y[:4]
    L.append(f"\n**BEA GDP by state, Plastics and rubber products manufacturing (NAICS 326), "
             f"current dollars (SAGDP2 line 33), {ly}**\n")
    L.append(f"| Geography | QCEW 2024 NAICS 326 private establishments (rank) | GDP {ly}, $ millions | "
             f"1-yr change | 5-yr change | Share of US GDP {ly} | Share {y5[:4]} |\n|---|---:|---:|---:|---:|---:|---:|")
    est = dict(col.qcew_rank)
    rank = {k: i + 1 for i, (k, _) in enumerate(col.qcew_rank)}
    for g in geos:
        sm = series_map(col)[f"SAGDP2-33@{g}"]
        v = sm[latest_y]
        sh = f"{v / us_cur[latest_y] * 100:.1f}%" if g != "00000" else "100%"
        sh5 = (f"{sm[y5] / us_cur[y5] * 100:.1f}%" if (g != "00000" and y5 in sm and y5 in us_cur) else
               ("100%" if g == "00000" else "n/a"))
        q = f"{est[g]:,} (#{rank[g]})" if g in est else "-"
        L.append(f"| {postal(g)} | {q} | {v:,.0f} | {pct(v, sm.get(y1))} | {pct(v, sm.get(y5))} | {sh} | {sh5} |")
    L.append(f"\n**Ohio and Pennsylvania share of US NAICS 326 GDP, by year** "
             "(state GDP / US GDP, both SAGDP2 current dollars)\n")
    years = sorted(us_cur)
    L.append("| Year | " + " | ".join(y[:4] for y in years) + " |")
    L.append("|---|" + "---:|" * len(years))
    for g, nm in (("39000", "Ohio"), ("42000", "Pennsylvania")):
        sm = series_map(col)[f"SAGDP2-33@{g}"]
        L.append(f"| {nm} | " + " | ".join(f"{sm[y] / us_cur[y] * 100:.1f}%" if y in sm else "n/a" for y in years) + " |")
    sm_oh, sm_pa = series_map(col)["SAGDP2-33@39000"], series_map(col)["SAGDP2-33@42000"]
    L.append("| OH + PA | " + " | ".join(f"{(sm_oh[y] + sm_pa[y]) / us_cur[y] * 100:.1f}%" for y in years) + " |")

    # real GDP
    L.append(f"\n**BEA real GDP by state, NAICS 326 (SAGDP9 line 33, millions of chained 2017 dollars)**\n")
    L.append(f"| Geography | {ly} | 1-yr change | 5-yr change |\n|---|---:|---:|---:|")
    for g in geos:
        sm = series_map(col)[f"SAGDP9-33@{g}"]
        ld = cat[f"SAGDP9-33@{g}"]["latest_date"]
        v = sm[ld]
        L.append(f"| {postal(g)} | {v:,.0f} | {pct(v, sm.get(shift_date(ld, 12)))} | {pct(v, sm.get(shift_date(ld, 60)))} |")
    return "\n".join(L).strip() + "\n"


def update_readme(summary):
    path = OUT_DIR / "README.md"
    text = path.read_text()
    b, e = "<!-- SUMMARY:BEGIN -->", "<!-- SUMMARY:END -->"
    if b not in text or e not in text:
        sys.exit("error: README.md lacks SUMMARY markers")
    head, rest = text.split(b, 1)
    _, tail = rest.split(e, 1)
    path.write_text(head + b + "\n" + summary + e + tail)


def verify_no_keys(keys):
    """Belt and braces: none of the key values may appear in any written file."""
    bad = []
    for p in list(OUT_DIR.glob("*")) + [Path(__file__)]:
        t = p.read_text()
        bad += [p.name for k in keys.values() if k in t]
    if bad:
        raise SystemExit(f"error: key material found in {sorted(set(bad))}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    ap.add_argument("--refresh", action="store_true", help="ignore the cache and re-fetch")
    ap.add_argument("--update-readme", action="store_true", help="rewrite the README summary block")
    ap.add_argument("--print-summary", action="store_true")
    a = ap.parse_args()
    keys = load_keys()
    http = Http(keys, a.cache_dir, a.refresh)
    col = Collector()
    pull_fred(http, keys, col)
    pull_bls(http, keys, col)
    pull_bea(http, keys, col)
    pull_eia(http, keys, col)
    write_csvs(col)
    summary = build_summary(col)
    if a.print_summary:
        print(summary)
    if a.update_readme:
        update_readme(summary)
    verify_no_keys(keys)
    print(f"[done] {len(col.catalog)} series, {len(col.rows)} observations, "
          f"{http.network_calls} network calls; cache {a.cache_dir}")
    print("[note] " + col.xcheck)
    print("[note] ethane spot series in EIA spot list: %s" % col.ethane_available)


if __name__ == "__main__":
    main()
