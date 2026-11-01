#!/usr/bin/env python3
"""build_osha_inspections.py - DOL OSHA inspections -> polymer establishment leads for the Atlas.

Stdlib only; re-runnable; READ-ONLY on data/ (it never writes under data/).
Imports the Atlas loader/matcher from the sibling scripts/build_echo_spine.py
(same normalizers and the same match ladder, so the two spines are comparable).

Route
  DOL Open Data Portal v4, dataset OSHA / Inspection (catalog id 10334):
      https://apiprod.dol.gov/v4/get/OSHA/inspection/json?...&X-API-KEY=<KEY>
  The key is read ONLY from the environment (DOL_API_KEY) and is sent ONLY as the
  X-API-KEY query parameter (the header form returns 401).  It is never written
  to a file, a log line or a cache filename: every cached page is named by the
  SHA-256 of the key-stripped URL, so a cache can be replayed without a key.
  Field list: .../json/metadata?X-API-KEY=<KEY>  (36 fields; used here: activity_nr,
  estab_name, site_address, site_city, site_state, site_zip, owner_type, sic_code,
  naics_code, insp_type, nr_in_estab, open_date, close_case_date).
  Filter: filter_object = {"and":[{"field":"naics_code","operator":"like","value":"326%"},
  {"field":"open_date","operator":"gte","value":"2019-01-01"}]}; paging = limit/offset with
  sort_by=activity_nr&sort=asc (stable order).  One request series per NAICS family
  (3252, 3255, 3259, 326), sequential, a pause between requests; a 429 stops the run.

What it does
  1. Pulls inspections opened 2019-01-01 or later whose naics_code starts with 3252,
     3255, 3259 or 326 (server-side filter; the date is re-checked locally).
  2. Aggregates to establishments (normalized name + normalized street + state + zip5):
     latest inspection date, inspection count, NAICS (latest), nr_in_estab (latest valid).
  3. Matches establishments to Atlas sites with the ECHO spine ladder (street + locality
     + name; operator rule, AGENTS 3).  Verdicts: MATCH_SITE / POSSIBLE / NO_MATCH.
  4. Writes under --out-dir: establishments.csv, site_matches.csv, band_proposals.csv
     (MATCH_SITE only, site grain), leads_by_state.csv, REPORT.md.

Doctrine (AGENTS.md / docs/SCHEMA.md)
  - Lead/proposal product only; nothing here is Atlas data, a tier or a status change.
  - An inspection is activity evidence (the establishment existed and was inspected on
    that date); it is never a status change.  A failed or empty fetch is never evidence.
  - OSHA NAICS is inspector-recorded; addresses are site addresses; inspected is not in
    scope.  nr_in_estab is an OSHA-recorded figure: it supports a band PROPOSAL only
    (SCHEMA 4.4 bands, 4.5 employee_band_site), never a precise headcount.
  - Coordinates are not used.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, os.pardir))
DEFAULT_OUT = os.path.join(REPO, "tasks", "osha-spine-2026-11-01")
DEFAULT_CACHE = "/tmp/claude-0/osha_dol/cache"

API = "https://apiprod.dol.gov/v4/get/OSHA/inspection/json"
FAMILIES = ("3252", "3255", "3259", "326")
SINCE = "2019-01-01"
PAGE = 1000
PAUSE = 0.4

BANDS = [(1, 9, "1-9"), (10, 49, "10-49"), (50, 99, "50-99"), (100, 249, "100-249"), (250, 499, "250-499"),
         (500, 999, "500-999"), (1000, 4999, "1000-4999")]
BAND_VOCAB = {b[2] for b in BANDS} | {"5000+", "unknown"}


def load_echo():
    path = os.path.join(HERE, "build_echo_spine.py")
    if not os.path.exists(path):
        sys.exit("scripts/build_echo_spine.py is required (shared Atlas loader and match ladder)")
    spec = importlib.util.spec_from_file_location("build_echo_spine", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["build_echo_spine"] = mod
    spec.loader.exec_module(mod)
    return mod


E = load_echo()


def band_of(n):
    if n is None or n < 1:
        return ""
    for lo, hi, name in BANDS:
        if lo <= n <= hi:
            return name
    return "5000+"


# ------------------------------------------------------------------ DOL fetch (key never persisted)
class RateLimited(Exception):
    pass


def _scrub(text, key):
    return text.replace(key, "<KEY>") if key else text


def fetch_page(params, cache_dir, key, stats):
    """params: dict of query params WITHOUT the key.  Returns parsed JSON (list of rows).
    Cache file = sha256 of the key-stripped URL."""
    clean = API + "?" + urllib.parse.urlencode(params)
    name = hashlib.sha256(clean.encode()).hexdigest() + ".json"
    path = os.path.join(cache_dir, name)
    if os.path.exists(path):
        stats["pages_cached"] += 1
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)["data"]
    if not key:
        sys.exit("cache miss and DOL_API_KEY is not set in the environment")
    url = clean + "&X-API-KEY=" + urllib.parse.quote(key, safe="")
    last = ""
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "polymer-atlas-osha-lane/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                body = r.read()
            data = json.loads(body.decode("utf-8"))
            if not isinstance(data, dict) or "data" not in data:
                raise ValueError("unexpected payload shape")
            os.makedirs(cache_dir, exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh)
            stats["pages_fetched"] += 1
            time.sleep(PAUSE)
            return data["data"]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise RateLimited(_scrub(str(e), key))
            last = "HTTP %s" % e.code
            if e.code in (401, 403, 400):
                sys.exit("DOL API refused the request (%s) - stopping; not evidence about the data" % last)
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as e:
            last = _scrub(type(e).__name__ + ": " + str(e), key)
        time.sleep(2 * (attempt + 1))
    sys.exit("fetch failed after retries (%s) - availability signal only; stopping" % last)


def pull_inspections(cache_dir, key):
    stats = Counter()
    rows = {}
    per_family = Counter()
    for fam in FAMILIES:
        filt = {"and": [{"field": "naics_code", "operator": "like", "value": fam + "%"},
                        {"field": "open_date", "operator": "gte", "value": SINCE}]}
        offset = 0
        while True:
            params = {"limit": PAGE, "offset": offset, "sort_by": "activity_nr", "sort": "asc",
                      "filter_object": json.dumps(filt, separators=(",", ":"))}
            page = fetch_page(params, cache_dir, key, stats)
            stats["requests_" + fam] += 1
            for r in page:
                an = str(r.get("activity_nr"))
                if an in rows:
                    stats["dup_activity_nr_dropped"] += 1
                    continue
                r["_family"] = fam
                rows[an] = r
                per_family[fam] += 1
            if len(page) < PAGE:
                break
            offset += PAGE
    return rows, per_family, stats


# ------------------------------------------------------------------ aggregation
def d10(s):
    s = (s or "").strip()
    return s[:10] if re.match(r"\d{4}-\d{2}-\d{2}", s) else ""


def clean_name(s):
    s = (s or "").strip()
    s = re.sub(r"^\s*(?:[A-Za-z]{2}\d{6,}|\d{4,})\s*[-:]\s*", "", s)   # '160609 - ARMACELL' / 'WA317966422 - CARLISLE' -> bare name
    return s


def num(s):
    try:
        return int(str(s).strip())
    except (TypeError, ValueError):
        return None


def aggregate(rows):
    est = {}
    out_of_window = 0
    for r in rows.values():
        od = d10(r.get("open_date"))
        if not od or od < SINCE:
            out_of_window += 1
            continue
        st = (r.get("site_state") or "").strip().upper()
        nm = clean_name(r.get("estab_name"))
        sk = E.street_key(r.get("site_address"))
        z5 = E.zip5(r.get("site_zip"))
        city = E.squash(r.get("site_city"))
        key = (E.name_key(nm), sk if sk else "city:" + city, st, z5)
        e = est.setdefault(key, {"insp": []})
        e["insp"].append({
            "activity_nr": str(r["activity_nr"]), "open_date": od, "close": d10(r.get("close_case_date")),
            "naics": (r.get("naics_code") or "").strip(), "sic": (r.get("sic_code") or "").strip(),
            "nr": num(r.get("nr_in_estab")), "name": nm, "street": (r.get("site_address") or "").strip(),
            "city": (r.get("site_city") or "").strip(), "state": st, "zip": (r.get("site_zip") or "").strip(),
            "owner_type": (r.get("owner_type") or "").strip(), "insp_type": (r.get("insp_type") or "").strip(),
        })
    ests = []
    for key, e in est.items():
        insp = sorted(e["insp"], key=lambda i: (i["open_date"], i["activity_nr"]))
        last = insp[-1]
        withn = [i for i in insp if i["nr"] and i["nr"] > 0]
        nrl = withn[-1] if withn else None
        bands = sorted({band_of(i["nr"]) for i in withn}, key=lambda b: [x[2] for x in BANDS].index(b) if b in [x[2] for x in BANDS] else 99)
        est_key = "OSHAE-" + hashlib.sha1("|".join(key).encode()).hexdigest()[:10]
        ests.append({
            "est_key": est_key, "name": last["name"], "street": last["street"], "city": last["city"],
            "state": last["state"], "zip": last["zip"], "naics_latest": last["naics"],
            "naics_all": ";".join(sorted({i["naics"] for i in insp})),
            "sic_latest": last["sic"], "owner_types": ";".join(sorted({i["owner_type"] for i in insp if i["owner_type"]})),
            "inspection_count": len(insp), "first_inspection": insp[0]["open_date"],
            "latest_inspection": last["open_date"], "latest_activity_nr": last["activity_nr"],
            "nr_in_estab_latest_insp": last["nr"] if last["nr"] is not None else "",
            "nr_in_estab_latest_valid": nrl["nr"] if nrl else "",
            "nr_latest_valid_activity_nr": nrl["activity_nr"] if nrl else "",
            "nr_latest_valid_open_date": nrl["open_date"] if nrl else "",
            "nr_inspections_with_value": len(withn),
            "bands_seen": ";".join(bands),
            "name_variants": ";".join(sorted({i["name"] for i in insp}))[:200],
            "insp": insp,
        })
    ests.sort(key=lambda d: (d["state"], d["city"].lower(), d["name"].lower(), d["est_key"]))
    return ests, out_of_window


# ------------------------------------------------------------------ matching (via the ECHO ladder)
def to_fac(e):
    return {"registry_id": e["est_key"], "facility_name": e["name"], "street": e["street"], "city": e["city"],
            "state": e["state"], "zip": e["zip"], "tri_ids": ""}


def classify_band(existing, proposed):
    ex = (existing or "").strip()
    if ex in ("", "unknown"):
        return "fills_%s" % ("unknown" if ex else "blank")
    if ex == proposed:
        return "matches_existing"
    if ex in BAND_VOCAB:
        return "conflicts_existing"
    return "existing_nonstandard_value"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cache-dir", default=DEFAULT_CACHE, help="raw page cache (outside the repo; file names are key-free hashes)")
    ap.add_argument("--data-dir", default=os.path.join(REPO, "data"))
    ap.add_argument("--qcew", default=os.path.join(REPO, "docs", "denominators", "qcew_state_polymer_2023_2024.csv"))
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--as-of", default=date.today().isoformat())
    a = ap.parse_args(argv)
    as_of = date.fromisoformat(a.as_of)
    key = os.environ.get("DOL_API_KEY", "").strip()

    try:
        rows, per_family, fstats = pull_inspections(a.cache_dir, key)
    except RateLimited as e:
        sys.exit("RATE LIMITED (HTTP 429): %s - stopped; re-run later (cached pages are kept)" % e)
    ests, out_of_window = aggregate(rows)
    ids = [e["est_key"] for e in ests]
    assert len(ids) == len(set(ids)), "est_key not unique"                       # AGENTS 2 rule 10b
    n_insp_agg = sum(e["inspection_count"] for e in ests)
    assert n_insp_agg == len(rows) - out_of_window, "inspection reconciliation failed"   # rule 10c

    A = E.Atlas(a.data_dir)
    recs = E.match_facilities([to_fac(e) for e in ests], A)
    by_key = {e["est_key"]: e for e in ests}
    for r in recs:
        r["e"] = by_key[r["f"]["registry_id"]]
        r["lead"], r["lead_ref"] = E.lead_class(r, A) if r["verdict"] == "NO_MATCH" else ("", "")
    assert len(recs) == len(ests)

    os.makedirs(a.out_dir, exist_ok=True)
    W = lambda name: open(os.path.join(a.out_dir, name), "w", newline="", encoding="utf-8")

    # ---- establishments.csv
    ecols = ["est_key", "name", "street", "city", "state", "zip", "naics_latest", "naics_all", "sic_latest",
             "owner_types", "inspection_count", "first_inspection", "latest_inspection", "latest_activity_nr",
             "nr_in_estab_latest_insp", "nr_in_estab_latest_valid", "nr_latest_valid_activity_nr",
             "nr_latest_valid_open_date", "nr_inspections_with_value", "bands_seen", "name_variants"]
    with W("establishments.csv") as fh:
        w = csv.DictWriter(fh, ecols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(ests)

    # ---- site_matches.csv
    def recent3(d):
        return bool(d) and (as_of - date.fromisoformat(d)).days <= 3 * 365

    mcols = ["est_key", "name", "street", "city", "state", "zip", "naics_latest", "inspection_count",
             "latest_inspection", "verdict", "match_strength", "basis", "site_id", "org_id", "site_name",
             "site_operating_status", "site_street_source", "name_sim", "alt_site_ids", "osha_estabs_at_site",
             "lead_class", "lead_ref", "liveness_note"]
    per_site = defaultdict(list)
    for r in recs:
        if r["verdict"] == "MATCH_SITE":
            per_site[r["site_id"]].append(r["e"]["est_key"])
    mrows = []
    for r in sorted(recs, key=lambda r: (r["e"]["state"], r["e"]["city"].lower(), r["e"]["name"].lower(), r["e"]["est_key"])):
        e = r["e"]
        s = A.site_by_id.get(r["site_id"]) if r["site_id"] else None
        note = ""
        if r["verdict"] in ("MATCH_SITE", "POSSIBLE") and s["operating_status"] in ("closed", "idled", "active_idled_partial"):
            note = "%satlas_status_%s_but_osha_inspection_%s%s" % (
                "possible_match_" if r["verdict"] == "POSSIBLE" else "",
                s["operating_status"], e["latest_inspection"], "_within_3y" if recent3(e["latest_inspection"]) else "")
            note += ";reverification_lead_only_not_a_status_change"
        elif r["verdict"] == "MATCH_SITE" and recent3(e["latest_inspection"]):
            note = "osha_inspection_within_3y"
        mrows.append({
            "est_key": e["est_key"], "name": e["name"], "street": e["street"], "city": e["city"], "state": e["state"],
            "zip": e["zip"], "naics_latest": e["naics_latest"], "inspection_count": e["inspection_count"],
            "latest_inspection": e["latest_inspection"], "verdict": r["verdict"], "match_strength": r["strength"],
            "basis": r["basis"], "site_id": r["site_id"], "org_id": s["org_id"] if s else "",
            "site_name": s["site_name"] if s else "", "site_operating_status": s["operating_status"] if s else "",
            "site_street_source": A.site_prof[r["site_id"]]["street_src"] if s else "",
            "name_sim": r["name_sim"], "alt_site_ids": r["alts"],
            "osha_estabs_at_site": len(per_site[r["site_id"]]) if r["verdict"] == "MATCH_SITE" else "",
            "lead_class": r["lead"], "lead_ref": r["lead_ref"], "liveness_note": note})
    with W("site_matches.csv") as fh:
        w = csv.DictWriter(fh, mcols, lineterminator="\n")
        w.writeheader()
        w.writerows(mrows)

    # ---- band_proposals.csv (MATCH_SITE only; one row per site; site grain only)
    pcols = ["site_id", "org_id", "site_name", "state", "est_key", "osha_estab_name", "match_strength",
             "current_employee_band_site", "proposed_employee_band_site", "relation_to_current", "nr_in_estab",
             "inspection_activity_nr", "inspection_open_date", "employee_count_source_date", "nr_age_years",
             "bands_seen_all_inspections", "band_stable", "n_inspections_with_nr", "latest_inspection_has_nr",
             "osha_estabs_at_site", "source_class", "basis", "scope_note"]
    prows = []
    for sid, keys in sorted(per_site.items()):
        cands = [by_key[k] for k in keys if by_key[k]["nr_in_estab_latest_valid"] != ""]
        if not cands:
            continue
        e = max(cands, key=lambda d: (d["nr_latest_valid_open_date"], d["nr_latest_valid_activity_nr"]))
        r = next(r for r in recs if r["e"]["est_key"] == e["est_key"])
        s = A.site_by_id[sid]
        n = e["nr_in_estab_latest_valid"]
        band = band_of(n)
        od = e["nr_latest_valid_open_date"]
        prows.append({
            "site_id": sid, "org_id": s["org_id"], "site_name": s["site_name"], "state": s["state"],
            "est_key": e["est_key"], "osha_estab_name": e["name"], "match_strength": r["strength"],
            "current_employee_band_site": s.get("employee_band_site", ""), "proposed_employee_band_site": band,
            "relation_to_current": classify_band(s.get("employee_band_site", ""), band),
            "nr_in_estab": n, "inspection_activity_nr": e["nr_latest_valid_activity_nr"], "inspection_open_date": od,
            "employee_count_source_date": od, "nr_age_years": "%.1f" % ((as_of - date.fromisoformat(od)).days / 365.25),
            "bands_seen_all_inspections": e["bands_seen"],
            "band_stable": "Y" if ";" not in e["bands_seen"] else "N",
            "n_inspections_with_nr": e["nr_inspections_with_value"],
            "latest_inspection_has_nr": "Y" if e["nr_latest_valid_activity_nr"] == e["latest_activity_nr"] else "N",
            "osha_estabs_at_site": len(keys), "source_class": "government_filing",
            "basis": "OSHA inspection %s opened %s: nr_in_estab %s → %s" % (e["nr_latest_valid_activity_nr"], od, n, band),
            "scope_note": "site band only; never to org or other sites; band not headcount"})
    with W("band_proposals.csv") as fh:
        w = csv.DictWriter(fh, pcols, lineterminator="\n")
        w.writeheader()
        w.writerows(prows)

    # ---- leads_by_state.csv
    gaps = E.qcew_gap(a.qcew, A)
    by_state = defaultdict(Counter)
    for r in recs:
        e = r["e"]
        c = by_state[e["state"]]
        c["inspections"] += e["inspection_count"]
        c["establishments"] += 1
        c[r["verdict"]] += 1
        if r["verdict"] == "NO_MATCH":
            c["lead_" + r["lead"]] += 1
            if recent3(e["latest_inspection"]):
                c["no_match_recent3y"] += 1
    gap_rank = {s: i + 1 for i, s in enumerate(sorted(gaps, key=lambda s: -gaps[s][2]))}
    ordered = sorted(by_state, key=lambda s: (-(gaps[s][2]) if s in gaps else 10 ** 9, s))
    lcols = ["state", "qcew_2023_326_private_estabs", "atlas_strict_326_sites", "qcew_gap", "gap_rank",
             "osha_inspections", "osha_establishments", "match_site", "possible", "no_match",
             "no_match_latest_inspection_within_3y", "no_match_net_new_lead",
             "no_match_name_equals_held_org_other_location", "no_match_held_org_same_name_city_diff_address"]
    with W("leads_by_state.csv") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(lcols)
        for s in ordered:
            c = by_state[s]
            q = gaps.get(s)
            w.writerow([s, q[0] if q else "", q[1] if q else "", q[2] if q else "", gap_rank.get(s, ""),
                        c["inspections"], c["establishments"], c["MATCH_SITE"], c["POSSIBLE"], c["NO_MATCH"],
                        c["no_match_recent3y"], c["lead_NET_NEW_LEAD"], c["lead_NAME_EQUALS_HELD_ORG_OTHER_LOCATION"],
                        c["lead_HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS"]])
    tot = Counter()
    for c in by_state.values():
        tot.update(c)
    assert tot["establishments"] == len(ests) and tot["inspections"] == n_insp_agg
    assert tot["MATCH_SITE"] + tot["POSSIBLE"] + tot["NO_MATCH"] == len(ests)

    write_report(a, A, rows, per_family, fstats, out_of_window, ests, recs, prows, by_state, gaps, ordered,
                 per_site, as_of)
    print("inspections:", len(rows), "establishments:", len(ests),
          {k: tot[k] for k in ("MATCH_SITE", "POSSIBLE", "NO_MATCH")}, "band_proposals:", len(prows),
          "pages_fetched:", fstats["pages_fetched"], "pages_cached:", fstats["pages_cached"])
    return 0


def pct(n, d):
    return "%.1f%%" % (100.0 * n / d) if d else "n/a"


def write_report(a, A, rows, per_family, fstats, out_of_window, ests, recs, prows, by_state, gaps, ordered,
                 per_site, as_of):
    f = lambda x: format(x, ",")
    n = len(ests)
    v = Counter(r["verdict"] for r in recs)
    kinds = Counter(r["kind"] for r in recs if r["verdict"] == "MATCH_SITE")
    pk = Counter(r["kind"] for r in recs if r["verdict"] == "POSSIBLE")
    n_insp = sum(e["inspection_count"] for e in ests)
    fam4 = Counter()
    owner = Counter()
    for r in rows.values():
        fam4[(r.get("naics_code") or "")[:4]] += 1
        owner[(r.get("owner_type") or "").strip() or "blank"] += 1
    sites_with_street = sum(1 for p in A.site_prof.values() if p["street_key"])
    recent3 = lambda d: bool(d) and (as_of - date.fromisoformat(d)).days <= 3 * 365
    yr = Counter(e["latest_inspection"][:4] for e in ests)
    n_recent = sum(1 for e in ests if recent3(e["latest_inspection"]))
    ms = [r for r in recs if r["verdict"] == "MATCH_SITE"]
    ms_recent = sum(1 for r in ms if recent3(r["e"]["latest_inspection"]))
    matched_sites = set(per_site)
    multi = [s for s, k in per_site.items() if len(k) > 1]
    conflict = [r for r in ms if A.site_by_id[r["site_id"]]["operating_status"] in ("closed", "idled", "active_idled_partial")]
    conflict_poss = [r for r in recs if r["verdict"] == "POSSIBLE" and r["site_id"] and
                     A.site_by_id[r["site_id"]]["operating_status"] in ("closed", "idled", "active_idled_partial")]
    with_nr = sum(1 for e in ests if e["nr_in_estab_latest_valid"] != "")
    rel = Counter(p["relation_to_current"] for p in prows)
    pband = Counter(p["proposed_employee_band_site"] for p in prows)
    stable = Counter(p["band_stable"] for p in prows)
    latest_has = Counter(p["latest_inspection_has_nr"] for p in prows)
    ages = sorted(float(p["nr_age_years"]) for p in prows)
    ebands = Counter(band_of(e["nr_in_estab_latest_valid"]) for e in ests if e["nr_in_estab_latest_valid"] != "")
    ms_with_nr = len(prows)
    ms_no_nr = len({r["site_id"] for r in ms}) - ms_with_nr
    nm = [r for r in recs if r["verdict"] == "NO_MATCH"]
    lead = Counter(r["lead"] for r in nm)
    nm_recent = sum(1 for r in nm if recent3(r["e"]["latest_inspection"]))
    no_state = sum(1 for e in ests if not e["state"])
    L = []
    P = L.append
    P("# OSHA inspections polymer-establishment spine - %s" % as_of.isoformat())
    P("")
    P("**Status: lead and proposal product, not Atlas data.** Nothing here edits `data/`, allocates an ID, sets a tier "
      "or changes a status. Built by `scripts/build_osha_inspections.py` (stdlib; re-runnable; shares the Atlas loader "
      "and match ladder of `scripts/build_echo_spine.py`). Packet lane output: the integrator of record decides what, "
      "if anything, is applied. `est_key` values are local row keys (hash of the aggregation key), not Atlas IDs.")
    P("")
    P("## 1. Route, filters, raw counts")
    P("")
    P("- **Route:** DOL Open Data Portal v4, dataset OSHA / Inspection (catalog id 10334; found in the 45-dataset catalog "
      "noted in `ROUTE_REPORT.md`). Endpoint: `https://apiprod.dol.gov/v4/get/OSHA/inspection/json?<params>&X-API-KEY=<KEY>`. "
      "The key (free DOL portal key, `DOL_API_KEY`) works only as a query parameter (header form returns 401); it is read "
      "from the environment, never written to any repo file, log or cache filename. Cache = one file per page named by the "
      "SHA-256 of the key-stripped URL, kept outside the repo (`%s`), so the run can be replayed without a key." % a.cache_dir)
    P("- **Metadata:** `.../json/metadata?X-API-KEY=<KEY>` lists 36 fields. Used: `activity_nr`, `estab_name`, "
      "`site_address`, `site_city`, `site_state`, `site_zip`, `owner_type`, `sic_code`, `naics_code`, `insp_type`, "
      "`nr_in_estab` (dictionary: \"Number of employees in establishment\", varchar, 0 <= N), `open_date`, "
      "`close_case_date`. `naics_code` and `open_date` are filterable server-side.")
    P("- **Filter (server side, per NAICS family, sequential):** `filter_object` = `naics_code like '<family>%%'` AND "
      "`open_date gte %s`, for families 3252, 3255, 3259, 326; paging `limit=%d`, `offset`, `sort_by=activity_nr&sort=asc` "
      "(stable order), %.1fs pause between requests; %s pages in total (the first live run fetched all of them with no "
      "rate limiting or error responses; a 429 would stop the run, and re-runs replay from the key-free cache)." % (
          SINCE, PAGE, PAUSE, f(fstats["pages_fetched"] + fstats["pages_cached"])))
    P("- **Date re-check (local):** %s rows fell outside the window and were dropped; %s duplicate `activity_nr` rows dropped." % (
        f(out_of_window), f(fstats["dup_activity_nr_dropped"])))
    P("- **Raw result:** **%s inspections** (unit: OSHA inspection records, one `activity_nr` each; opened %s or later; "
      "NAICS under 3252/3255/3259/326). By family: %s." % (
          f(len(rows)), SINCE, "; ".join("%s: %s" % (k, f(per_family[k])) for k in FAMILIES)))
    P("- By 4-digit NAICS prefix (inspection counts): %s." % "; ".join("%s: %s" % (k, f(c)) for k, c in sorted(fam4.items())))
    P("- By `owner_type` (A private, B local govt, C state govt, D federal): %s. Not filtered; government-owned "
      "establishments are included as inspected." % "; ".join("%s: %s" % (k, f(c)) for k, c in owner.most_common()))
    P("")
    P("## 2. Establishments")
    P("")
    P("Aggregation key = normalized name (numeric `160609 - ` style prefixes stripped; Inc/LLC/Corp/The removed) + "
      "normalized street (suffix and direction canonicalized; unit/suite removed; falls back to city when no street) + "
      "state + zip5. **%s establishments** (unit: distinct aggregation keys, state + name + address) across **%s "
      "inspections** (reconciles to section 1: %s raw minus %s out of window). Establishments in %d states/territories "
      "(%s with a blank state). One physical address can appear as more than one establishment when OSHA recorded "
      "different names there (rebrand, co-tenant, name typo); that is left visible, not merged." % (
          f(n), f(n_insp), f(len(rows)), f(out_of_window), len({e["state"] for e in ests if e["state"]}), f(no_state)))
    P("")
    P("Establishments by state (unit: establishments; inspections in parentheses), top 15 by establishment count: " +
      "; ".join("%s %s (%s)" % (s, f(c["establishments"]), f(c["inspections"])) for s, c in
                sorted(by_state.items(), key=lambda kv: -kv[1]["establishments"])[:15]) +
      ". All states: `leads_by_state.csv`.")
    P("")
    P("Latest-inspection year (unit: establishments): " + "; ".join("%s %s" % (y, f(c)) for y, c in sorted(yr.items())) + ".")
    P("")
    P("## 3. Match to Atlas sites")
    P("")
    P("Atlas side: %s site rows (all shards, any status/tier); a usable street key exists for %s (%s) - from the "
      "`street_address` column where filled, otherwise a heuristic read of `Street...:` phrases in `notes` (the Atlas "
      "often keeps the street in notes). Sites with no street key can match only on **name + zip/city**; those matches "
      "are labelled `name_zip_street_unknown` / `name_city_street_unknown` / `name_zip_weak` in `basis`. Ladder "
      "(identical to the ECHO spine; operator rule AGENTS 3): street exact + state + (zip5 or city) + name agreement = "
      "MATCH_SITE; street exact with a different name = POSSIBLE (co-tenant or successor operator); street unknown on "
      "either side + same zip5 + strong name = MATCH_SITE (moderate); same city + strong name, or weaker name, = "
      "POSSIBLE; ties at the top rank = POSSIBLE; both streets present but different is never a match. Coordinates are "
      "not used." % (f(len(A.sites)), f(sites_with_street), pct(sites_with_street, len(A.sites))))
    P("")
    P("| Verdict | Establishments |")
    P("|---|---:|")
    for k in ("MATCH_SITE", "POSSIBLE", "NO_MATCH"):
        P("| %s | %s |" % (k, f(v[k])))
    P("| **Total** | **%s** |" % f(n))
    P("")
    P("**Match rate (unit: OSHA establishments matched to an Atlas site row):** MATCH_SITE = %s of %s (**%s**); "
      "MATCH_SITE + POSSIBLE = %s. This is an establishment-to-site match rate, **not Atlas coverage**: OSHA lists "
      "inspected establishments only (programmed and unprogrammed), and the Atlas holds sites for which no inspection "
      "occurred since %s." % (f(v["MATCH_SITE"]), f(n), pct(v["MATCH_SITE"], n), pct(v["MATCH_SITE"] + v["POSSIBLE"], n), SINCE))
    P("")
    P("MATCH_SITE by basis: " + "; ".join("`%s` %s" % (k, f(c)) for k, c in kinds.most_common()) + ". POSSIBLE by best basis: " +
      "; ".join("`%s` %s" % (k, f(c)) for k, c in pk.most_common()) + ".")
    P("")
    P("Distinct Atlas sites reached by at least one MATCH_SITE establishment: %s (unit: site rows); %s of them are "
      "reached by more than one OSHA establishment key (name variants at one address)." % (f(len(matched_sites)), f(len(multi))))
    P("")
    P("## 4. Employee-band proposals (`band_proposals.csv`)")
    P("")
    P("`nr_in_estab` is OSHA's recorded number of employees in the establishment at inspection (an OSHA-recorded "
      "figure, source class `government_filing`). It supports an `employee_band_site` **proposal** for **MATCH_SITE "
      "rows only**, at **site grain only** - never pushed to the organization or to other sites of the org (SCHEMA 4.5: "
      "never allocate parent headcount pro-rata; SCHEMA 4.4: band only, never a precise headcount stored as fact). "
      "Basis text per row: `OSHA inspection <activity_nr> opened <date>: nr_in_estab N → band`; "
      "`employee_count_source_date` = that inspection's open date. The value used is the most recent inspection of the "
      "establishment that carries a non-zero `nr_in_estab` (`latest_inspection_has_nr` says whether that is also the "
      "latest inspection). Zero or blank `nr_in_estab` is treated as missing, not as a count.")
    P("")
    P("- Establishments with a usable `nr_in_estab` (unit: establishments): %s of %s; by band: %s." % (
        f(with_nr), f(n), "; ".join("%s %s" % (b, f(c)) for b, c in sorted(ebands.items(), key=lambda kv: [x[2] for x in BANDS + [(0, 0, "5000+")]].index(kv[0])))))
    P("- **Band proposals: %s** (unit: Atlas site rows; one per matched site, using the latest valid value among its "
      "matched establishment keys). MATCH_SITE sites without any usable `nr_in_estab`: %s." % (f(len(prows)), f(ms_no_nr)))
    P("- Relation to the site's current `employee_band_site`: %s." % "; ".join("%s %s" % (k, f(c)) for k, c in rel.most_common()))
    P("- Proposed bands: %s." % "; ".join("%s %s" % (k, f(c)) for k, c in sorted(pband.items(), key=lambda kv: [x[2] for x in BANDS + [(0, 0, "5000+")]].index(kv[0]))))
    P("- Band stability across all of a site's inspections that carry a value: same band every time %s; varies %s. "
      "The value is from the latest inspection with a count; it is %s years old at the median (range %s to %s). The "
      "latest inspection itself carries the count for %s of the proposals." % (
          f(stable["Y"]), f(stable["N"]), ("%.1f" % ages[len(ages) // 2]) if ages else "n/a",
          ("%.1f" % ages[0]) if ages else "n/a", ("%.1f" % ages[-1]) if ages else "n/a", f(latest_has["Y"])))
    P("- Rows with `relation_to_current = conflicts_existing` or `band_stable = N` deserve integrator review before "
      "any apply; `fills_unknown` / `fills_blank` rows are the straightforward ones. Existing site values outside the "
      "SCHEMA 4.4 vocabulary (e.g. `100-199`) are flagged `existing_nonstandard_value` and never overwritten by this packet.")
    P("")
    P("## 5. Liveness (activity signal only)")
    P("")
    P("`latest_inspection` is the open date of the establishment's most recent OSHA inspection in the window. It is an "
      "**activity signal only**: it shows OSHA inspected that establishment on that date, i.e. it existed and operated "
      "enough to be inspected. It is never a status change (AGENTS 3: status changes need dated primary evidence), and "
      "the **absence** of an inspection is nothing - most plants are never inspected in a given year, and a failed or "
      "empty fetch is never evidence of closure. Of %s establishments, %s have a latest inspection within 3 years of %s; "
      "of %s MATCH_SITE establishments, %s do. **%s MATCH_SITE establishments** map to an Atlas site recorded as "
      "closed/idled, and %s POSSIBLE establishments point at a closed/idled site (`liveness_note` in "
      "`site_matches.csv`): re-verification leads for the integrator, not a status change either way (an inspection "
      "at a possibly different operator of the same address does not show the recorded operator is active)." % (
          f(n), f(n_recent), as_of.isoformat(), f(len(ms)), f(ms_recent), f(len(conflict)), f(len(conflict_poss))))
    P("")
    P("## 6. NO_MATCH leads by state, sorted by QCEW gap")
    P("")
    P("NO_MATCH = no Atlas site candidate cleared the ladder. It is a **lead, not a finding of absence** (name or "
      "street form may differ). `lead_class`: `NET_NEW_LEAD` (no Atlas org with this normalized name), "
      "`NAME_EQUALS_HELD_ORG_OTHER_LOCATION` (likely another site of a held org; AGENTS 3 steps 2/4), "
      "`HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS` (strongly similar name at another street in the same city/zip). "
      "**%s NO_MATCH establishments** (unit: OSHA establishments): %s NET_NEW_LEAD, %s NAME_EQUALS_HELD_ORG_OTHER_LOCATION, "
      "%s HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS; %s have a latest inspection within 3 years." % (
          f(v["NO_MATCH"]), f(lead["NET_NEW_LEAD"]), f(lead["NAME_EQUALS_HELD_ORG_OTHER_LOCATION"]),
          f(lead["HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS"]), f(nm_recent)))
    P("")
    P("Sort key = QCEW gap per `docs/denominators/README.md`: QCEW 2023 private establishments, NAICS 326, minus Atlas "
      "strict 326 sites (`operating_status` active/unknown, tier A-C, `naics_primary` starts 326), recomputed from "
      "`data/sites_*.csv` at run time. The gap is a count difference, not a matched-facility coverage figure, and the "
      "NO_MATCH pool per state is **not** an estimate of it (OSHA lists inspected establishments over four NAICS "
      "families, QCEW counts 326 reporting units). Top 20 by gap:")
    P("")
    P("| Gap rank | State | QCEW gap (326) | OSHA establishments | MATCH_SITE | NO_MATCH | NO_MATCH, inspected within 3y | of which NET_NEW_LEAD |")
    P("|---:|---|---:|---:|---:|---:|---:|---:|")
    shown = 0
    for s in ordered:
        if s not in gaps:
            continue
        shown += 1
        if shown > 20:
            break
        c = by_state[s]
        P("| %d | %s | %s | %s | %s | %s | %s | %s |" % (shown, s, f(gaps[s][2]), f(c["establishments"]), f(c["MATCH_SITE"]),
                                                       f(c["NO_MATCH"]), f(c["no_match_recent3y"]), f(c["lead_NET_NEW_LEAD"])))
    P("")
    P("Full table (every state with OSHA establishments, gap-sorted): `leads_by_state.csv`; the individual NO_MATCH "
      "establishments with `lead_class` are the `verdict = NO_MATCH` rows of `site_matches.csv`.")
    P("")
    P("## 7. Caveats (binding on any reader)")
    P("")
    P("- **OSHA NAICS is inspector-recorded**, assigned by the compliance officer at the inspection (the dataset also "
      "carries a legacy `sic_code`); it can be wrong, stale or coarse. It is a `government_filing` value for the "
      "inspected establishment at best, never a company fact, never a ring decision, and never overwrites a site NAICS "
      "with its own source (SCHEMA 2.1, AGENTS 4). `naics_all` shows every code seen at one establishment.")
    P("- **Addresses are site addresses** (the inspected worksite), not a mailing or HQ address; some are free-text "
      "descriptions (\"APPROX. 1/2 mile ...\") that yield no street key, and construction-style or multi-site "
      "entries exist. Mailing fields were not used.")
    P("- **Inspected does not mean in scope.** The NAICS filter catches plastics, rubber, resin and chemical-product "
      "establishments, but also coded-in neighbours (e.g. 325920 explosives, which SCHEMA 2.2 marks exclude-by-default, "
      "and other 3259 codes that 2.2 lists as secondary or not at all) and mis-coded establishments. Every NO_MATCH row is a lead needing ring/scope adjudication - an "
      "owner-ruling-adjacent question this lane does not settle (AGENTS 2.9).")
    P("- **Leads only.** No row is a verdict in the AGENTS 2.8 grammar (not VERIFIED, REJECT, STILL_UNCERTAIN or "
      "DUPLICATE_OF); they are match candidates and band proposals for the integrator.")
    P("- **`nr_in_estab`** is an inspection-time figure of uncertain definition (establishment or inspected portion; "
      "often rounded, sometimes carried over between inspections). It is a band input with a date, not a headcount; "
      "see `nr_age_years` and `band_stable`.")
    P("- **Window and coverage.** Only inspections opened %s or later; OSHA inspection records include state-plan "
      "states' data as loaded by DOL; completeness of the DOL extract by state was not verified. An establishment "
      "inspected before 2019 only is outside this file, and that is not evidence of anything." % SINCE)
    P("- **Counts name their unit:** inspections = records; establishments = aggregation keys (not facilities, not "
      "companies, not Atlas sites).")
    P("")
    P("## 8. Reproduce")
    P("")
    P("```")
    P("set -a; . /root/.config/polymer-atlas/api_keys.env; set +a   # DOL_API_KEY from the environment only")
    P("python3 scripts/build_osha_inspections.py --as-of %s" % as_of.isoformat())
    P("# first-page probe (key shown as <KEY>):")
    P("#   https://apiprod.dol.gov/v4/get/OSHA/inspection/json?limit=1&X-API-KEY=<KEY>")
    P("```")
    P("")
    with open(os.path.join(a.out_dir, "REPORT.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
