#!/usr/bin/env python3
"""build_federal_leads.py - federal-source discovery packet (USAspending + openFDA).

READ-ONLY with respect to data/.  Produces lead/candidate files under an output
directory (default tasks/federal-leads-2026-11-01/).  Stdlib only (plus the
repo's own scripts/atlas.py normalisers, so matching uses the AGENTS.md §3
rules verbatim).  Nothing here is scope evidence: see REPORT.md caveats.

Steps (run all, or one with --step):
  usaspending  pull federal contract recipients FY2022-FY2026 whose award NAICS
               is under 3252 / 3255 / 3259 / 326 (326 -> 3261 + 3262, the only
               children; the API accepts NAICS filters of length 2, 4 or 6 only)
  fda          pull openFDA device registration & listing establishments in the
               10 QCEW gap states whose registered name contains a polymer term
  match        match both pulls to the Atlas (dedupe order of AGENTS.md §3) and
               write matches.csv + REPORT.md

USAspending (no key):
  POST https://api.usaspending.gov/api/v2/search/spending_by_award_count/   (partition sizing)
  POST https://api.usaspending.gov/api/v2/search/spending_by_award/         (award rows: UEI, name, NAICS, recipient location)
  POST https://api.usaspending.gov/api/v2/search/spending_by_category/recipient/   (in-window obligated $ per recipient UEI)
  filters: award_type_codes A,B,C,D (contracts) ; time_period action_date
           2021-10-01..2026-09-30 (FY2022-FY2026) ; naics_codes = 4-digit prefixes.

openFDA (api.data.gov key):
  GET https://api.fda.gov/device/registrationlisting.json
      ?search=registration.state_code:<ST> AND registration.name:<term>*&limit=1000&skip=<n>
  The key is read from the environment variable DATA_GOV_API_KEY ONLY and is sent
  in an HTTP Basic Authorization header (never in a URL), is never written to any
  file, cache entry or report, and any error text is scrubbed of it.

  Run:  set -a; . /root/.config/polymer-atlas/api_keys.env; set +a
        python3 scripts/build_federal_leads.py --step all
"""
import argparse
import base64
import csv
import hashlib
import importlib.util
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, os.pardir))
TODAY = "2026-11-01"

# --------------------------------------------------------------------------- config
USA_BASE = "https://api.usaspending.gov/api/v2"
NAICS_PREFIXES = ["3252", "3255", "3259", "3261", "3262"]          # 3252, 3255, 3259, 326 (=3261+3262)
FY_RANGES = [(f"{fy - 1}-10-01", f"{fy}-09-30") for fy in range(2022, 2027)]
AWARD_TYPES = ["A", "B", "C", "D"]
SPLIT_THRESHOLD = 10000          # spending_by_award silently stops after 10,000 rows per query (hasNext goes false at page 100); partitions must stay under it

FDA_URL = "https://api.fda.gov/device/registrationlisting.json"
GAP_STATES = ["CA", "TX", "FL", "MI", "IL", "GA", "IN", "WI", "NY", "NC"]
FDA_TERMS = ["plastic", "polymer", "molding", "moulding", "rubber", "extrusion", "silicone", "urethane", "composite"]
MFR_TYPES = ("Manufacture Medical Device", "Manufacture Medical Device for Another Party (Contract Manufacturer)")


def api_key():
    return os.environ.get("DATA_GOV_API_KEY", "")


def scrub(s):
    k = api_key()
    return s.replace(k, "<KEY>") if k else s


def log(*a):
    print(scrub(" ".join(str(x) for x in a)), file=sys.stderr, flush=True)


def http_json(url, body=None, headers=None, tries=6, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json", "User-Agent": "polymer-atlas-federal-leads/1.0"}
    h.update(headers or {})
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data, h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"__notfound__": True}
            last = f"HTTP {e.code}"
            if e.code not in (429, 500, 502, 503, 504):
                raise RuntimeError(scrub(f"{last} on {url.split('?')[0]}: {e.read()[:200]!r}"))
        except Exception as e:  # URLError, timeout, JSON decode
            last = type(e).__name__
        time.sleep(min(60, 2 ** i))
    raise RuntimeError(scrub(f"giving up on {url.split('?')[0]}: {last}"))


def cache_path(cache_dir, tag, parts):
    h = hashlib.sha1("|".join(parts).encode()).hexdigest()[:16]
    return os.path.join(cache_dir, f"{tag}_{h}.json")


def cached(cache_dir, tag, parts, fn):
    p = cache_path(cache_dir, tag, parts)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    v = fn()
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(v, f)
    os.replace(tmp, p)
    return v


# --------------------------------------------------------------------------- USAspending
def usa_filters(prefix, d0, d1):
    return {"award_type_codes": AWARD_TYPES,
            "time_period": [{"start_date": d0, "end_date": d1, "date_type": "action_date"}],
            "naics_codes": [prefix]}


def usa_count(prefix, d0, d1):
    r = http_json(USA_BASE + "/search/spending_by_award_count/", {"filters": usa_filters(prefix, d0, d1)})
    return r["results"]["contracts"]


def split_range(d0, d1):
    a, b = date.fromisoformat(d0), date.fromisoformat(d1)
    mid = a + (b - a) // 2
    return (a.isoformat(), mid.isoformat()), ((mid + timedelta(days=1)).isoformat(), b.isoformat())


def plan_partitions(prefix, d0, d1, cache_dir):
    n = cached(cache_dir, "ucount", [prefix, d0, d1], lambda: usa_count(prefix, d0, d1))
    if n == 0:
        return []
    if n <= SPLIT_THRESHOLD or d0 == d1:
        return [(prefix, d0, d1, n)]
    (a0, a1), (b0, b1) = split_range(d0, d1)
    return plan_partitions(prefix, a0, a1, cache_dir) + plan_partitions(prefix, b0, b1, cache_dir)


AWARD_FIELDS = ["Award ID", "Recipient Name", "Recipient UEI", "Award Amount", "NAICS", "Recipient Location"]


def pull_partition(prefix, d0, d1, n, cache_dir):
    def go():
        rows, page = [], 1
        while True:
            r = http_json(USA_BASE + "/search/spending_by_award/",
                          {"filters": usa_filters(prefix, d0, d1), "fields": AWARD_FIELDS, "limit": 100, "page": page})
            for x in r.get("results", []):
                loc = x.get("Recipient Location") or {}
                naics = (x.get("NAICS") or {}).get("code") or ""
                rows.append([x.get("generated_internal_id") or str(x.get("internal_id")), x.get("Award ID"),
                             x.get("Recipient Name") or "", x.get("Recipient UEI") or "", naics,
                             loc.get("state_code") or "", loc.get("city_name") or "", loc.get("zip5") or "",
                             loc.get("address_line1") or "", loc.get("location_country_code") or ""])
            if not r.get("page_metadata", {}).get("hasNext"):
                break
            page += 1
        return rows
    rows = cached(cache_dir, "uaward", [prefix, d0, d1], go)
    # reconcile against the count endpoint (AGENTS.md section 2 rule 10c): a short pull is truncation, never silently accepted
    if len(rows) < 0.995 * n:
        os.remove(cache_path(cache_dir, "uaward", [prefix, d0, d1]))
        raise RuntimeError(f"truncated award pull {prefix} {d0}..{d1}: got {len(rows)} of {n}; partition too large")
    return rows


def pull_category_recipients(prefix, cache_dir):
    """In-window obligated $ per recipient UEI for one NAICS prefix (transaction level)."""
    def go():
        out, page = [], 1
        while True:
            r = http_json(USA_BASE + "/search/spending_by_category/recipient/",
                          {"filters": {"award_type_codes": AWARD_TYPES,
                                       "time_period": [{"start_date": FY_RANGES[0][0], "end_date": FY_RANGES[-1][1],
                                                        "date_type": "action_date"}],
                                       "naics_codes": [prefix]},
                           "limit": 100, "page": page})
            for x in r.get("results", []):
                out.append([x.get("uei") or "", x.get("name") or "", x.get("code") or "", x.get("amount")])
            if not r.get("page_metadata", {}).get("hasNext"):
                break
            page += 1
        return out
    return cached(cache_dir, "ucat", [prefix], go)


def backfill_location(uei, cache_dir):
    """Recipient location for a UEI that the category endpoint returned but the NAICS-filtered award pull did not
    (transaction-level NAICS differs from the award's current NAICS).  One award of that UEI in the same window,
    any NAICS; the location is the recipient's registered location as USAspending carries it."""
    def go():
        r = http_json(USA_BASE + "/search/spending_by_award/",
                      {"filters": {"award_type_codes": AWARD_TYPES, "recipient_search_text": [uei],
                                   "time_period": [{"start_date": FY_RANGES[0][0], "end_date": FY_RANGES[-1][1],
                                                    "date_type": "action_date"}]},
                       "fields": ["Award Amount", "Recipient Name", "Recipient UEI", "Recipient Location"],
                       "limit": 25, "page": 1, "sort": "Award Amount", "order": "desc"})
        for x in r.get("results", []):
            if (x.get("Recipient UEI") or "") == uei:
                loc = x.get("Recipient Location") or {}
                return [loc.get("address_line1") or "", loc.get("city_name") or "", loc.get("state_code") or "",
                        loc.get("zip5") or "", loc.get("location_country_code") or ""]
        return None
    return cached(cache_dir, "uloc", [uei], go)


def run_usaspending(out_dir, cache_dir, workers):
    os.makedirs(cache_dir, exist_ok=True)
    log("usaspending: category/recipient pulls")
    cat = {}
    for p in NAICS_PREFIXES:
        rows = pull_category_recipients(p, cache_dir)
        log(f"  prefix {p}: {len(rows)} recipient rows")
        cat[p] = rows
    log("usaspending: planning partitions")
    parts = []
    for p in NAICS_PREFIXES:
        for d0, d1 in FY_RANGES:
            parts += plan_partitions(p, d0, d1, cache_dir)
    total_est = sum(x[3] for x in parts)
    log(f"  {len(parts)} partitions, {total_est} award-rows before cross-FY dedupe")
    awards, lock, done = {}, threading.Lock(), [0]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(pull_partition, p, d0, d1, n, cache_dir): (p, d0, d1, n) for p, d0, d1, n in parts}
        for f in as_completed(futs):
            rows = f.result()
            with lock:
                for r in rows:
                    awards.setdefault(r[0], r)
                done[0] += 1
                if done[0] % 10 == 0:
                    log(f"  partitions done {done[0]}/{len(parts)}; distinct awards {len(awards)}")
    log(f"usaspending: {len(awards)} distinct awards")

    rec = {}
    for gid, aid, name, uei, naics, st, city, z5, street, cc in awards.values():
        key = uei or "NOUEI:" + re.sub(r"\s+", " ", name.upper())
        r = rec.setdefault(key, {"uei": uei, "names": Counter(), "locs": Counter(), "naics": Counter(), "awards": 0})
        r["names"][name] += 1
        r["locs"][(street, city, st, z5, cc)] += 1
        r["naics"][naics] += 1
        r["awards"] += 1
    obl = defaultdict(float)
    obl_by_prefix = defaultdict(lambda: defaultdict(float))
    cat_names = {}
    for p, rows in cat.items():
        for uei, name, code, amt in rows:
            key = uei or "NOUEI:" + re.sub(r"\s+", " ", name.upper())
            obl[key] += amt or 0.0
            obl_by_prefix[key][p] += amt or 0.0
            cat_names.setdefault(key, (uei, name))
    keys = set(rec) | set(obl)
    need = sorted(k for k in keys if k not in rec and not k.startswith("NOUEI:"))
    log(f"usaspending: backfilling location for {len(need)} category-only recipients")
    backfill = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for k, loc in zip(need, ex.map(lambda u: backfill_location(u, cache_dir), need)):
            backfill[k] = loc
    out = []
    for k in keys:
        r = rec.get(k)
        if r:
            name = r["names"].most_common(1)[0][0]
            street, city, st, z5, cc = r["locs"].most_common(1)[0][0]
            mix = ";".join(f"{c}:{n}" for c, n in sorted(r["naics"].items(), key=lambda t: (-t[1], t[0])))
            aw = r["awards"]
            uei = r["uei"]
        else:
            uei, name = cat_names[k]
            street = city = st = z5 = cc = mix = ""
            aw = 0
            if backfill.get(k):
                street, city, st, z5, cc = backfill[k]
        pm = ";".join(f"{p}:{obl_by_prefix[k][p]:.2f}" for p in NAICS_PREFIXES if obl_by_prefix[k].get(p))
        if k in rec and k in obl:
            flag = ""
        elif k in rec:
            flag = "awards_only"
        else:
            flag = "category_only_loc_backfilled" if backfill.get(k) else "category_only_no_location"
        ex_aw = sum(n for c, n in r["naics"].items() if c != "325920") if r else ""
        out.append({"recipient_uei": uei, "recipient_name": name, "recipient_street": street, "recipient_city": city,
                    "recipient_state": st, "recipient_zip5": z5, "recipient_country": cc,
                    "award_naics_mix_awards": mix, "award_count": aw, "awards_excl_325920": ex_aw,
                    "obligated_usd_fy22_26": f"{obl.get(k, 0.0):.2f}", "obligated_by_naics4_usd": pm,
                    "pull_flag": flag})
    out.sort(key=lambda r: -float(r["obligated_usd_fy22_26"]))
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "usaspending_recipients.csv")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    meta = {"distinct_awards": len(awards), "recipients": len(out), "partitions": len(parts),
            "award_rows_before_dedupe": total_est,
            "category_rows": {p: len(rows) for p, rows in cat.items()},
            "category_total_usd": round(sum(obl.values()), 2)}
    with open(os.path.join(cache_dir, "usaspending_meta.json"), "w") as f:
        json.dump(meta, f)
    log("usaspending: wrote", path, meta)


# --------------------------------------------------------------------------- openFDA
def fda_query(state, term, cache_dir):
    search = f"registration.state_code:{state} AND registration.name:{term}*"

    def go():
        auth = base64.b64encode((api_key() + ":").encode()).decode()
        rows, skip = [], 0
        while True:
            url = f"{FDA_URL}?search={urllib.parse.quote(search)}&limit=1000&skip={skip}"
            r = http_json(url, headers={"Authorization": "Basic " + auth})
            if r.get("__notfound__"):
                break
            res = r.get("results", [])
            for x in res:
                reg = x.get("registration", {})
                oo = (reg.get("owner_operator") or {}).get("firm_name", "")
                # business fields only: no us_agent / official_correspondent (personal data, AGENTS.md §6)
                rows.append({"fei": reg.get("fei_number", ""), "reg_no": reg.get("registration_number", ""),
                             "name": reg.get("name", ""), "a1": reg.get("address_line_1", ""),
                             "a2": reg.get("address_line_2", ""), "city": reg.get("city", ""),
                             "state": reg.get("state_code", ""), "zip": reg.get("zip_code", ""),
                             "country": reg.get("iso_country_code", ""), "status": reg.get("status_code", ""),
                             "expiry": reg.get("reg_expiry_date_year", ""), "owner_operator": oo,
                             "etypes": x.get("establishment_type") or [],
                             "pcodes": sorted({p.get("product_code", "") for p in x.get("products", []) if p.get("product_code")})})
            total = r.get("meta", {}).get("results", {}).get("total", 0)
            skip += len(res)
            if not res or skip >= total or skip >= 25000:
                break
        return {"search": search, "rows": rows}
    return cached(cache_dir, "fda", [search], go)


def run_fda(out_dir, cache_dir):
    if not api_key():
        sys.exit("DATA_GOV_API_KEY not set in the environment (source /root/.config/polymer-atlas/api_keys.env)")
    os.makedirs(cache_dir, exist_ok=True)
    est, per_query = {}, {}
    for st in GAP_STATES:
        for term in FDA_TERMS:
            r = fda_query(st, term, cache_dir)
            per_query[f"{st}|{term}"] = len(r["rows"])
            for x in r["rows"]:
                if x["state"] != st or x["country"] not in ("US", "USA", ""):
                    continue
                e = est.setdefault(x["fei"], {"fei": x["fei"], "reg_no": x["reg_no"], "name": x["name"],
                                              "street": ", ".join(t for t in (x["a1"], x["a2"]) if t), "city": x["city"],
                                              "state": x["state"], "zip5": (x["zip"] or "")[:5], "status": x["status"],
                                              "expiry": x["expiry"], "oo": x["owner_operator"], "types": set(),
                                              "pcodes": set(), "listings": 0, "terms": set()})
                e["types"].update(x["etypes"])
                e["pcodes"].update(x["pcodes"])
                e["listings"] += 1
                e["terms"].add(term)
            log(f"fda {st} {term}: {len(r['rows'])} listing records")
    out = []
    for e in est.values():
        out.append({"fei": e["fei"], "registration_number": e["reg_no"], "establishment_name": e["name"],
                    "street": e["street"], "city": e["city"], "state": e["state"], "zip5": e["zip5"],
                    "establishment_types": ";".join(sorted(e["types"])),
                    "is_manufacturer": "Y" if any(t in MFR_TYPES for t in e["types"]) else "N",
                    "listing_records": e["listings"], "product_codes": ";".join(sorted(e["pcodes"])[:15]),
                    "owner_operator_firm": e["oo"], "reg_status_code": e["status"], "reg_expiry_year": e["expiry"],
                    "matched_name_terms": ";".join(sorted(e["terms"]))})
    out.sort(key=lambda r: (r["state"], r["establishment_name"]))
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "fda_establishments.csv")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    with open(os.path.join(cache_dir, "fda_meta.json"), "w") as f:
        json.dump({"per_query_listing_records": per_query, "establishments": len(out)}, f)
    log("fda: wrote", path, len(out), "establishments")


# --------------------------------------------------------------------------- matching
def load_atlas(data_dir):
    spec = importlib.util.spec_from_file_location("atlas_helper", os.path.join(HERE, "atlas.py"))
    atlas = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(atlas)
    return atlas, atlas.load_tables(data_dir)


DBA_RE = re.compile(r"\b(?:d/b/a|dba|doing business as|a/k/a|aka|f/k/a|fka)\b", re.I)
FEI_RE = re.compile(r"\bFEI\W{0,3}(\d{6,10})\b")


def name_variants(atlas, name):
    keys = {atlas.name_key(name)}
    for part in DBA_RE.split(name or ""):
        if part.strip():
            keys.add(atlas.name_key(part))
    return {k for k in keys if len(k) >= 3}


class AtlasIndex:
    def __init__(self, atlas, tables):
        self.atlas = atlas
        self._hay = None
        self.orgs = {}
        self.name_idx = defaultdict(set)       # name key -> org ids  (legal_name + trade_names)
        self.org_state = defaultdict(set)      # org id -> states (HQ + sites)
        self.street_idx = defaultdict(list)    # street key -> site rows
        self.fei_idx = defaultdict(set)        # FEI digits quoted in notes -> org ids
        self.link_idx = defaultdict(set)       # (registry, id) -> org ids
        for tn in ("organizations", "ecosystem"):
            for r in tables.get(tn, atlas.Table(tn)).rows:
                oid = r["org_id"]
                self.orgs[oid] = r
                for v in [r["legal_name"]] + atlas.tokens_semicolon(r.get("trade_names")):
                    for k in name_variants(atlas, v):
                        self.name_idx[k].add(oid)
                hq = r.get("hq_state") or r.get("state") or ""
                if hq:
                    self.org_state[oid].add(hq.upper())
                for m in FEI_RE.finditer((r.get("notes") or "") + " " + (r.get("sources") or "")):
                    self.fei_idx[m.group(1).lstrip("0")].add(oid)
        self.sites = {}
        for r in tables.get("sites", atlas.Table("sites")).rows:
            self.sites[r["site_id"]] = r
            if r["state"]:
                self.org_state[r["org_id"]].add(r["state"].upper())
            sk = atlas.street_key(r.get("street_address", ""))
            if sk:
                self.street_idx[sk].append(r)
            for m in FEI_RE.finditer((r.get("notes") or "") + " " + (r.get("sources") or "")):
                self.fei_idx[m.group(1).lstrip("0")].add(r["org_id"])
        for r in tables.get("registry_links", atlas.Table("registry_links")).rows:
            if r["registry"] in ("UEI", "FDA_FEI"):
                self.link_idx[(r["registry"], r["registry_id"])].add(r["org_id"])

    def describe(self, oid):
        r = self.orgs[oid]
        return f"{oid} {r['legal_name']} [{r.get('status', '')}]"

    def match(self, registry, source_id, name, street, city, state, zip5):
        atlas = self.atlas
        held = self.link_idx.get((registry, source_id)) if source_id else None
        if held:
            return self._res("ALREADY_LINKED", sorted(held), "0 registry_links exact id", "", "N")
        if registry == "FDA_FEI" and source_id.lstrip("0") in self.fei_idx:
            return self._res("MATCH_ORG", sorted(self.fei_idx[source_id.lstrip("0")]),
                             "1b FEI quoted in Atlas notes (exact id)", "", "Y", "Y")
        # step 2: normalized name (legal_name + trade_names; dba-split variants)
        ids2 = set()
        for k in name_variants(atlas, name):
            ids2 |= self.name_idx.get(k, set())
        # step 3: street address -> site -> operator org
        ids3, sites3 = set(), []
        sk = atlas.street_key(street)
        if sk and any(ch.isdigit() for ch in sk):
            for s in self.street_idx.get(sk, []):
                if state and s["state"] and s["state"].upper() != state.upper():
                    continue
                if (zip5 and s["zip"] and s["zip"][:5] != zip5[:5] and city
                        and atlas.squash(city) != atlas.squash(s["city"])):
                    continue
                ids3.add(s["org_id"])
                sites3.append(s["site_id"])
        if ids2:
            both = ids2 & ids3
            ids = sorted(both or ids2)
            agree = any(state.upper() in self.org_state.get(i, ()) for i in ids) if state else False
            extra = ("same street" if both else "name key only")
            if ids3 - ids2:
                extra += " | street also hits " + ",".join(sorted(ids3 - ids2))
            lc = "Y" if (len(ids) == 1 and (agree or both)) else "REVIEW"
            return self._res("MATCH_ORG", ids, "2 normalized name" + (" + 3 street" if both else ""), extra, lc, agree)
        if ids3:
            return self._res("MATCH_ORG", sorted(ids3), "3 street address (name differs; sites " + ",".join(sites3[:3]) + ")",
                             "address-only: operator/brand question", "REVIEW", True)
        needles = {n for n in {atlas.squash(name), atlas.name_key(name)} if len(n) >= 6}
        hits4 = set()
        if needles:
            if self._hay is None:        # squash once, not once per query
                self._hay = [(oid, " " + atlas.squash(r.get("trade_names", "")) + " ",
                              " " + atlas.squash(r.get("notes", "")) + " ") for oid, r in self.orgs.items()]
            for oid, h1, h2 in self._hay:
                if any(f" {n} " in h1 or f" {n} " in h2 for n in needles):
                    hits4.add(oid)
        if hits4:
            return self._res("POSSIBLE_REVIEW", sorted(hits4)[:8], "4 trade_names/notes substring",
                             "weak: name appears in another record's notes/trade names", "REVIEW")
        return self._res("NO_MATCH", [], "", "", "N")

    def _res(self, cls, ids, step, notes, lc, agree=None):
        return {"match_class": cls, "ids": ids, "step": step, "notes": notes, "link_candidate": lc,
                "state_agree": "" if agree is None else ("Y" if agree else "N"),
                "org_desc": " | ".join(self.describe(i) for i in ids[:6])}


def read_csv(p):
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


def money(x):
    return f"${x:,.0f}"


def run_match(out_dir, data_dir, cache_dir):
    atlas, tables = load_atlas(data_dir)
    idx = AtlasIndex(atlas, tables)
    log(f"atlas: {len(idx.orgs)} org/ecosystem rows, {len(idx.sites)} sites, name keys {len(idx.name_idx)}")
    rows = []
    usa = read_csv(os.path.join(out_dir, "usaspending_recipients.csv"))
    for r in usa:
        uei = r["recipient_uei"]
        sid = uei or ("NOUEI:" + r["recipient_name"])
        m = idx.match("UEI", uei, r["recipient_name"], r["recipient_street"], r["recipient_city"],
                      r["recipient_state"], r["recipient_zip5"])
        rows.append(("USASPENDING_UEI", sid, r["recipient_name"], r["recipient_city"], r["recipient_state"], m,
                     float(r["obligated_usd_fy22_26"]), "" if uei else "no UEI on USAspending record: cannot link"))
    fda = read_csv(os.path.join(out_dir, "fda_establishments.csv"))
    for r in fda:
        m = idx.match("FDA_FEI", r["fei"], r["establishment_name"], r["street"], r["city"], r["state"], r["zip5"])
        rows.append(("OPENFDA_FEI", r["fei"], r["establishment_name"], r["city"], r["state"], m, 0.0, ""))
    ids = Counter((s, i) for s, i, *_ in rows)
    dups = [k for k, v in ids.items() if v > 1 and not k[1].startswith("NOUEI:")]
    if dups:
        sys.exit(f"duplicate source ids in match frame (AGENTS.md section 2 rule 10b): {dups[:5]}")
    cols = ["source", "source_id", "name", "city", "state", "match_class", "atlas_ids", "match_step", "link_candidate",
            "state_agree", "atlas_org_names", "match_notes"]
    with open(os.path.join(out_dir, "matches.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for s, i, n, c, st, m, amt, extra in rows:
            w.writerow([s, i, n, c, st, m["match_class"], ";".join(m["ids"]), m["step"], m["link_candidate"],
                        m["state_agree"], m["org_desc"], "; ".join(x for x in (m["notes"], extra) if x)])
    write_report(out_dir, cache_dir, usa, fda, rows)
    log("match: wrote matches.csv and REPORT.md")


def load_meta(cache_dir, name):
    p = os.path.join(cache_dir, name)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return {}


def write_report(out_dir, cache_dir, usa, fda, rows):
    um = load_meta(cache_dir, "usaspending_meta.json")
    U = [r for r in rows if r[0] == "USASPENDING_UEI"]
    F = [r for r in rows if r[0] == "OPENFDA_FEI"]

    def stats(R):
        c = Counter(r[5]["match_class"] for r in R)
        lc = Counter(r[5]["link_candidate"] for r in R if r[5]["match_class"] in ("MATCH_ORG", "ALREADY_LINKED"))
        return c, lc

    uc, ulc = stats(U)
    fc, flc = stats(F)
    obl_total = sum(float(r["obligated_usd_fy22_26"]) for r in usa)
    obl_match = sum(r[6] for r in U if r[5]["match_class"] in ("MATCH_ORG", "ALREADY_LINKED"))
    with_uei = sum(1 for r in usa if r["recipient_uei"])
    fmap = {r["fei"]: r for r in fda}
    umap = {(r["recipient_uei"] or "NOUEI:" + r["recipient_name"]): r for r in usa}
    L = []
    A = L.append
    A("# Federal leads packet: USAspending contract recipients + openFDA device establishments")
    A("")
    A(f"Lane packet, produced {TODAY} by `scripts/build_federal_leads.py`. **Leads and link candidates only.** "
      "Nothing here is scope evidence, nothing was written under `data/`, no IDs were allocated, and every "
      "candidate below needs the integrator of record (AGENTS.md section 2 rule 7). Counts name their unit and filter.")
    A("")
    A("## 1. Routes and exact terms")
    A("")
    A("**Goal A: USAspending (no key).** Contracts only (award types A, B, C, D), `time_period` on `action_date` "
      "2021-10-01 to 2026-09-30 (FY2022 through FY2026; FY2026 closed 2026-09-30 and the pull ran 2026-11-01), "
      "`naics_codes` as 4-digit prefixes **3252, 3255, 3259, 3261, 3262** (the API accepts NAICS filters of length 2, 4 or 6 "
      "only; `326` is rejected, and 326 has exactly two 4-digit children, 3261 plastics products and 3262 rubber products). "
      "Endpoints on `https://api.usaspending.gov/api/v2/search/`:")
    A("- `spending_by_category/recipient/`: in-window obligated dollars per recipient UEI (transaction level, so "
      "`obligated_usd_fy22_26` is dollars obligated inside the window, summed over prefixes).")
    A("- `spending_by_award/` (partitioned by prefix and date range so each query stays under the 50,000-row cap; awards "
      "deduplicated on `generated_internal_id` across partitions): recipient name, UEI, award NAICS (6-digit), recipient "
      "location. Used for award counts, NAICS mix and recipient address (most frequent address across the recipient's awards).")
    A("- `spending_by_award_count/`: partition sizing.")
    A("")
    A("**Goal B: openFDA device registration and listing** (`https://api.fda.gov/device/registrationlisting.json`, api.data.gov "
      "key sent as an HTTP Basic header, shown here as `<KEY>`). One query per state x term, `limit=1000`, paged with `skip`:")
    A("")
    A("```")
    A("search  = registration.state_code:<ST> AND registration.name:<term>*")
    A("<ST>    in " + ", ".join(GAP_STATES) + "   (10 QCEW gap states; OH skipped by instruction)")
    A("<term>  in " + ", ".join(FDA_TERMS) + "   (trailing wildcard on each, so 'plastics', 'composites' match)")
    A("api_key = <KEY>   (Authorization header; never in a URL, file or cache)")
    A("```")
    A("")
    A("Name-token search only (openFDA has no leading wildcards, so a term buried inside a longer word, "
      "e.g. 'thermoplastics', is not found; 'RUBBER' as a separate word is). Listing records are collapsed to one row per FEI; "
      "`is_manufacturer` = establishment type includes 'Manufacture Medical Device' or the contract-manufacturer type. "
      "`us_agent` and `official_correspondent` (named individuals, phones) are never stored, per AGENTS.md section 6.")
    A("")
    A("## 2. Headline counts")
    A("")
    A("| Measure | Unit and filter | Count |")
    A("|---|---|---:|")
    A(f"| Distinct contract awards | awards with >=1 action FY2022-FY2026, award NAICS under 3252/3255/3259/3261/3262, de-duplicated | {um.get('distinct_awards', 0):,} |")
    A(f"| Recipient rows | distinct recipient UEIs (plus UEI-less names) in that award set | {len(usa):,} |")
    A(f"| Recipient rows with a UEI | same | {with_uei:,} |")
    A(f"| Obligated dollars | in-window obligations across all those recipients | {money(obl_total)} |")
    A(f"| FDA establishments | distinct FEIs in 10 gap states, registered name matching a polymer term | {len(fda):,} |")
    A(f"| ...of which manufacturers | FEIs with a manufacture establishment type | {sum(1 for r in fda if r['is_manufacturer']=='Y'):,} |")
    A(f"| ...of which registration status 1 | FEIs with `status_code` 1 (active) | {sum(1 for r in fda if r['reg_status_code']=='1'):,} |")
    A("")
    mixc = Counter()
    for r in usa:
        for part in filter(None, r["award_naics_mix_awards"].split(";")):
            c, n = part.split(":")
            mixc[c[:4]] += int(n)
    A("Distinct awards by award-NAICS prefix (unit: awards): " + ", ".join(f"{k}: {mixc[k]:,}" for k in NAICS_PREFIXES) + ".")
    A("")
    cat_only = [r for r in usa if r["pull_flag"].startswith("category_only")]
    A("Recipient rows per prefix from the category endpoint: " + ", ".join(f"{k}: {v:,}" for k, v in um.get("category_rows", {}).items()) +
      f". Reconciliation (AGENTS.md section 2 rule 10c): {sum(1 for r in usa if r['pull_flag']=='awards_only'):,} recipients appear only in the award pull, "
      f"{len(cat_only):,} appear only in the category pull (`pull_flag` category_only_*; {money(sum(float(r['obligated_usd_fy22_26']) for r in cat_only))} of the total). "
      "The category endpoint filters on the NAICS of each *transaction* while the award endpoint filters on the award's own current NAICS, so a recipient "
      "whose modifications carried a 3252/3255/3259/326 code but whose award rolls up under another code shows up in category only. For those rows the award "
      "count and NAICS mix are blank, and the address was backfilled from one USAspending award record of the same UEI "
      f"({sum(1 for r in usa if r['pull_flag']=='category_only_loc_backfilled'):,} backfilled, "
      f"{sum(1 for r in usa if r['pull_flag']=='category_only_no_location'):,} without a location).")
    A("")
    A("## 3. Match to the Atlas (AGENTS.md section 3 order)")
    A("")
    A("Steps run: (0) exact registry id in `registry_links.csv`; (1b) FEI quoted in Atlas notes/sources; (2) normalized name against `legal_name` and "
      "`trade_names` of organizations + ecosystem (dba/aka split variants); (3) street address against site shards; (4) trade_names/notes substring. "
      "Neither source carries a website domain, so step 1 does not run. Classes: `MATCH_ORG` (step 2 or 3 hit), `POSSIBLE_REVIEW` (step 4 only, weak), `NO_MATCH`. "
      "`link_candidate` Y = exactly one org and either same-state evidence or same street; REVIEW = several orgs, no state agreement, or address-only. "
      "Y never means 'link now'; see caveats.")
    A("")
    A("| Source | Rows | MATCH_ORG | link_candidate Y | link_candidate REVIEW | POSSIBLE_REVIEW | NO_MATCH | ALREADY_LINKED | MATCH_ORG rate |")
    A("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for lab, R, c, lc in (("USAspending recipients (UEI)", U, uc, ulc), ("openFDA establishments (FEI)", F, fc, flc)):
        n = max(len(R), 1)
        A(f"| {lab} | {len(R):,} | {c['MATCH_ORG']:,} | {lc['Y']:,} | {lc['REVIEW']:,} | {c['POSSIBLE_REVIEW']:,} | {c['NO_MATCH']:,} | {c['ALREADY_LINKED']:,} | {100*c['MATCH_ORG']/n:.1f}% |")
    A("")
    A(f"By dollars, MATCH_ORG USAspending recipients hold {money(obl_match)} of {money(obl_total)} in-window obligations "
      f"({100*obl_match/max(obl_total,1):.1f}%). Existing `UEI` and `FDA_FEI` rows in `registry_links.csv`: 0 and 0, so every candidate below is a new row.")
    A("")
    A("## 4. Registry-link candidates (for the integrator)")
    A("")
    A("Per SCHEMA section 4.8, a `UEI` row is minted only on an exact UEI match taken from the source system's own record (here the USAspending recipient "
      "record, so the UEI is verified at source), with `match_basis` `usaspending_exact_uei` and `as_of` 2026-11-01. "
      "That this recipient *is* that Atlas organization still rests on a name or address match and is the integrator's call. "
      "All candidates are in `matches.csv` (`link_candidate` Y or REVIEW). Top Y candidates by in-window obligations:")
    A("")
    ucand = sorted([r for r in U if r[5]["link_candidate"] == "Y" and r[5]["match_class"] == "MATCH_ORG"], key=lambda r: -r[6])
    A("| UEI | Recipient (city, ST) | Obligated FY22-26 | Atlas org | Step |")
    A("|---|---|---:|---|---|")
    for s, i, n, c, st, m, amt, _ in ucand[:25]:
        A(f"| {i} | {n} ({c}, {st}) | {money(amt)} | {m['org_desc']} | {m['step']} |")
    A("")
    A(f"UEI link candidates: {len(ucand):,} with link_candidate Y; {ulc['REVIEW']:,} REVIEW. "
      f"FDA_FEI link candidates: {flc['Y']:,} Y; {flc['REVIEW']:,} REVIEW. FEI identifies an *establishment* while the table is org-keyed: "
      "record the FEI against the operator org of the matched site, and treat one-FEI-many-orgs as REVIEW.")
    A("")
    A("Top FDA_FEI Y candidates:")
    A("")
    A("| FEI | Establishment (city, ST) | Atlas org | Step |")
    A("|---|---|---|---|")
    for s, i, n, c, st, m, amt, _ in [r for r in F if r[5]["link_candidate"] == "Y"][:25]:
        A(f"| {i} | {n} ({c}, {st}) | {m['org_desc']} | {m['step']} |")
    A("")
    A("## 5. Discovery leads (NO_MATCH) by state")
    A("")
    A("A lead is an unmatched federal recipient or FDA establishment a verification lane may look at. It is not an Atlas record and not in scope until "
      "verified against a primary source. A NO_MATCH is a guarded no-hit, never a negative fact.")
    A("")
    ustate = defaultdict(lambda: [0, 0.0])
    cc_of = lambda i: umap.get(i, {}).get("recipient_country", "")
    for s, i, n, c, st, m, amt, _ in U:
        if m["match_class"] == "NO_MATCH":
            lab = st or ("(no state: foreign)" if cc_of(i) not in ("", "USA") else "(no location)")
            ustate[lab][0] += 1
            ustate[lab][1] += amt
    fstate = Counter(r[4] for r in F if r[5]["match_class"] == "NO_MATCH")
    fmfr = Counter(r[4] for r in F if r[5]["match_class"] == "NO_MATCH" and fmap[r[1]]["is_manufacturer"] == "Y")
    A("**USAspending NO_MATCH recipients (unit: recipient UEIs) by recipient state, top 20 by in-window obligations:**")
    A("")
    A("| State | NO_MATCH recipients | Obligated FY22-26 |")
    A("|---|---:|---:|")
    for st, (n, amt) in sorted(ustate.items(), key=lambda t: -t[1][1])[:20]:
        A(f"| {st} | {n:,} | {money(amt)} |")
    A("")
    A("**Top 10 QCEW gap states, both sources (unit: unmatched rows):**")
    A("")
    A("| State | USAspending NO_MATCH recipients | their FY22-26 obligations | FDA NO_MATCH establishments | ...manufacturers |")
    A("|---|---:|---:|---:|---:|")
    for st in GAP_STATES:
        n, amt = ustate.get(st, [0, 0.0])
        A(f"| {st} | {n:,} | {money(amt)} | {fstate.get(st, 0):,} | {fmfr.get(st, 0):,} |")
    A("")
    A("Largest unmatched USAspending recipients in the gap states (top 5 per state by obligations; recipients whose award mix is only NAICS 325920 "
      "explosives manufacturing are left out of this table because that code, though inside the requested 3259 prefix, is not polymer work; they remain in the CSV, "
      "and `awards_excl_325920` lets a reader filter them):")
    A("")
    A("| State | Recipient (city) | UEI | Obligated FY22-26 | Award NAICS mix (code:awards) |")
    A("|---|---|---|---:|---|")
    for st in GAP_STATES:
        top = sorted([r for r in U if r[4] == st and r[5]["match_class"] == "NO_MATCH"
                      and umap.get(r[1], {}).get("awards_excl_325920", "") != "0"], key=lambda r: -r[6])[:5]
        for s, i, n, c, _, m, amt, _x in top:
            A(f"| {st} | {n} ({c}) | {i} | {money(amt)} | {umap.get(i, {}).get('award_naics_mix_awards', '')[:60]} |")
    A("")
    A("Unmatched FDA manufacturer establishments in the gap states, listing records as a rough size proxy (top 5 per state):")
    A("")
    A("| State | Establishment (city) | FEI | Terms | Listing records |")
    A("|---|---|---|---|---:|")
    for st in GAP_STATES:
        top = sorted([fmap[r[1]] for r in F if r[4] == st and r[5]["match_class"] == "NO_MATCH" and fmap[r[1]]["is_manufacturer"] == "Y"],
                     key=lambda r: -int(r["listing_records"]))[:5]
        for r in top:
            A(f"| {st} | {r['establishment_name']} ({r['city']}) | {r['fei']} | {r['matched_name_terms']} | {r['listing_records']} |")
    A("")
    A("## 6. Caveats (binding on any use of this packet)")
    A("")
    A("- **Award NAICS describes the contract, not the firm.** A distributor, defense prime or reseller can hold a 3252/3255/3259/326 award for a "
      "purchase it did not make in a plant. Recipient rows are firms that *sold under* those codes; polymer manufacturing is unproven. NAICS mix columns "
      "are award-level and must never populate an Atlas `naics_primary` (SCHEMA section 4.13 `code` claims need their own source class). "
      "3255 (paint, coatings, adhesives) is dominated by commodity purchasing and carries the most awards; 3259 includes 325920 explosives manufacturing, "
      "which tops the dollar rankings and is not polymer work.")
    A("- **Recipient address is not a plant.** USAspending carries the SAM.gov registered address (often HQ, mailing or registered-agent). "
      "Do not create a site from it; a site needs the establishment's own physical-address evidence.")
    A("- **Name matching finds candidates; only the exact UEI/FEI links.** Same-name collisions across states and subsidiary/brand relationships are real: "
      "`link_candidate=Y` filters those risks, it is not a verdict. When in doubt do not merge (AGENTS.md section 3).")
    A("- **FDA registration is not polymer scope.** A name containing 'plastic' or 'rubber' on a device registration says nothing about processes, "
      "materials or ring. FDA rows are leads (and Ring 4 test candidates for a verification lane), never scope or tier evidence. "
      "Registrations are renewed annually; `reg_expiry_year` is a registration fact, not an operating-status fact. Contract manufacturers, repackagers and "
      "specification developers appear alongside real plants.")
    A("- **Coverage limits.** FDA name search is token-based, so firms whose names carry no term are missed by design. "
      "USAspending covers contract awards only (no grants, IDV parents or subawards), and only recipients with awards under these NAICS codes in the window.")
    A("- **Foreign / no-state recipients** are in the CSV but have no lawful site shard; hold them for an owner/schema ruling (AGENTS.md section 3).")
    A("- **Registry identifiers are verified at source:** UEIs come straight from USAspending recipient records and FEIs from the openFDA record. "
      "FEIs quoted in Atlas notes were used only to detect establishments already held, never as a source of identifiers.")
    A("- **No personal data stored.** FDA agent/correspondent contacts were dropped at ingest. No individual emails, phones or home addresses are in any output.")
    A("- The Atlas is read as of the working tree on the run date; rerun after integration passes. Tier ceilings for any future evidence row built from these "
      "sources: USAspending/SAM recipient record = `registry` (supports_B at most; an address alone supports_C); openFDA listing = `government_filing` for the "
      "registration's existence only.")
    A("")
    with open(os.path.join(out_dir, "REPORT.md"), "w") as f:
        f.write("\n".join(L) + "\n")


# --------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--step", choices=["usaspending", "fda", "match", "all"], default="all")
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "tasks", "federal-leads-2026-11-01"))
    ap.add_argument("--data-dir", default=os.path.join(ROOT, "data"))
    ap.add_argument("--cache-dir", default=os.path.join(ROOT, "build", "federal_leads_cache"),
                    help="request cache (gitignored build/); holds no key")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args(argv)
    if a.step in ("usaspending", "all"):
        run_usaspending(a.out_dir, a.cache_dir, a.workers)
    if a.step in ("fda", "all"):
        run_fda(a.out_dir, a.cache_dir)
    if a.step in ("match", "all"):
        run_match(a.out_dir, a.data_dir, a.cache_dir)


if __name__ == "__main__":
    main()
