#!/usr/bin/env python3
"""build_echo_spine.py - EPA ECHO exporter -> polymer facility spine for the Atlas.

Stdlib only; re-runnable; READ-ONLY on data/ (it never writes under data/).

What it does
  1. Stream-filters EPA's ECHO_EXPORTER.csv (zip or csv, never fully loaded) to
     facilities whose NAICS list carries a polymer-scope 6-digit code AND whose
     FAC_ACTIVE_FLAG = Y.
        core scope : 3252xx, 3255xx, 3259xx, 326xxx   (task scope; includes the
                     SCHEMA 2.2 Ring 1/2 Primary codes, e.g. 325211/325212/325991/
                     325510/325520 and every 326xxx)
        ring3_primary scope : 333511, 424610, 562920 (SCHEMA 2.2 Ring 3 Primary)
  2. Matches each facility to Atlas sites (data/sites_*.csv): normalized street
     address + state + (zip5 or city) + name check; then name + zip/city where a
     street is missing on either side; FRS IDs recorded in site notes and TRI
     TRIFIDs held in registry_links are used as corroboration only.
  3. Writes, under --out-dir:  facilities.csv, site_matches.csv,
     leads_by_state.csv, REPORT.md.

Inputs (not in the repo; raw files stay outside it)
  curl -sS -o /tmp/claude-0/echo_raw/echo_exporter.zip \
       https://echo.epa.gov/files/echodownloads/echo_exporter.zip
  python3 scripts/build_echo_spine.py --zip /tmp/claude-0/echo_raw/echo_exporter.zip

Column dictionary: https://echo.epa.gov/tools/data-downloads (ECHO Exporter
"columns" workbook).  REGISTRY_ID is the FRS ID; FAC_ACTIVE_FLAG is Y when any
associated ICIS-Air / ICIS-NPDES / RCRA / SDWA permit is in an active status -
a PERMIT fact, not proof that the plant operates.

Doctrine this script encodes (AGENTS.md / docs/SCHEMA.md)
  - Output is a candidate/lead product.  Nothing here is Atlas data, a tier, a
    status change or a minted registry link.  FRS IDs are proposals only; an
    FRS value is verified against the ECHO extract itself (REGISTRY_ID column).
  - ECHO NAICS is program-reported: government_filing for the FACILITY, never an
    organization fact and never a ring decision (SCHEMA 2.1).
  - One address = one site owned by the operator (AGENTS 3): a street match whose
    name disagrees is POSSIBLE, not MATCH_SITE.
  - Coordinates are not used anywhere (reference data, never evidence).
  - Last inspection / action dates are liveness SIGNALS only.
"""
import argparse
import csv
import glob
import hashlib
import io
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime

csv.field_size_limit(10 ** 8)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, os.pardir))
DEFAULT_OUT = os.path.join(REPO, "tasks", "echo-frs-spine-2026-11-01")

# ------------------------------------------------------------------ scope
CORE_PREFIXES = ("3252", "3255", "3259", "326")
RING3_PRIMARY = {"333511", "424610", "562920"}
NAICS_RE = re.compile(r"\b(?:325[259]\d{2}|326\d{3}|333511|424610|562920)\b")

# SCHEMA 2.2 signal key (P primary / S secondary / X exclude-by-default).  Codes in
# scope but absent from 2.2 (e.g. 325910 printing ink) are 'U' = unlisted.
SIGNAL_P = {"325211", "325212", "325991", "325510", "325520", "333511", "424610", "562920"}
SIGNAL_S = {"325220", "325998"}
SIGNAL_X = {"325920"}


def code_signal(c):
    if c.startswith("326") or c in SIGNAL_P:
        return "P"
    if c in SIGNAL_S:
        return "S"
    if c in SIGNAL_X:
        return "X"
    return "U"


SIGNAL_ORDER = {"P": 0, "S": 1, "U": 2, "X": 3}

PROGRAMS = (("AIR_FLAG", "AIR"), ("NPDES_FLAG", "NPDES"), ("RCRA_FLAG", "RCRA"),
            ("SDWIS_FLAG", "SDWIS"), ("TRI_FLAG", "TRI"), ("GHG_FLAG", "GHG"))

NOISE_RE = re.compile(r"\b(golf|school|church|hospital|county|city of|town of|township|village of|department|dept|"
                      r"college|university|police|fire|park|cemetery|library|apartments?|condo|mobile home|"
                      r"water (?:dist|system|works)|sewer|landfill|airport|marina)\b", re.I)

STATE_NAMES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
    "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "Puerto Rico": "PR", "Virgin Islands": "VI",
}

# ------------------------------------------------------------------ normalizers
def squash(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (s or "").lower().replace("&", " and "))).strip()


_SUFFIX = {"street": "st", "avenue": "ave", "av": "ave", "road": "rd", "drive": "dr", "boulevard": "blvd",
           "highway": "hwy", "parkway": "pkwy", "pky": "pkwy", "lane": "ln", "court": "ct", "circle": "cir",
           "place": "pl", "terrace": "ter", "route": "rte", "square": "sq", "trail": "trl", "center": "ctr",
           "centre": "ctr", "expressway": "expy", "turnpike": "tpke", "industrial": "ind",
           "north": "n", "south": "s", "east": "e", "west": "w", "northeast": "ne", "northwest": "nw",
           "southeast": "se", "southwest": "sw"}
_UNIT_RE = re.compile(r"\b(suite|ste|unit|apt|apartment|bldg|building|floor|fl|room|rm|dept|department|lot)\b.*$|#.*$")
_POBOX_RE = re.compile(r"\b(p\s*o\s*box|post office box|pob|box)\s*\d", re.I)
_ROUTE_SUBS = (
    (re.compile(r"\b(?:state|st)\s+(?:route|rte|rt|road|rd|highway|hwy)\b"), "sr"),
    (re.compile(r"\b(?:county|cty|co)\s+(?:road|rd|route|rte|highway|hwy)\b"), "cr"),
    (re.compile(r"\b(?:us|u s)\s+(?:route|rte|rt|highway|hwy)\b"), "us"),
    (re.compile(r"\b(?:route|rte|rt)\b"), "rte"),
)


def street_key(s):
    """Normalized street key; '' when blank, a PO box, or has no usable token."""
    s = (s or "").strip()
    if not s or _POBOX_RE.search(s):
        return ""
    first = s.split(",")[0]
    s = first if re.search(r"\d", first) else s
    s = _UNIT_RE.sub("", s.lower())
    s = re.sub(r"\b(\d+)(st|nd|rd|th)\b", r"\1", s)
    k = squash(s)
    for rx, rep in _ROUTE_SUBS:
        k = rx.sub(rep, k)
    k = " ".join(_SUFFIX.get(t, t) for t in k.split())
    return k


NAME_STOP = {"inc", "llc", "corp", "co", "the", "ltd", "company", "corporation", "incorporated", "lp", "llp",
             "plc", "of", "and", "usa", "us", "dba", "d", "b", "a", "na"}
GENERIC = {"plastic", "plastics", "product", "products", "industry", "industries", "manufacturing", "mfg",
           "molding", "moulding", "molded", "group", "holdings", "holding", "international", "intl", "systems",
           "system", "technologies", "technology", "tech", "solutions", "packaging", "chemical", "chemicals",
           "rubber", "division", "div", "plant", "facility", "operations", "operating", "enterprises",
           "enterprise", "services", "service", "american", "america", "north", "east", "south", "west",
           "global", "specialty", "specialties", "materials", "material", "polymer", "polymers", "film",
           "films", "foam", "pipe", "tube", "compounding", "resins", "resin", "extrusion", "extruded",
           "injection", "custom", "precision", "engineered", "engineering", "composites", "corporate",
           "automotive", "auto", "industrial", "construction", "building", "builders", "coating", "coatings",
           "paint", "painting", "seating", "laboratories", "laboratory", "labs", "hq", "headquarters",
           "headquarter", "warehouse", "distribution", "recycling", "mold", "mould", "tool", "tooling",
           "machine", "machining", "fabrication", "fabricating", "supply", "sales", "mill", "mills", "works",
           "texas", "ohio", "california", "florida", "michigan", "illinois", "indiana", "georgia", "carolina",
           "pennsylvania", "york", "jersey", "tennessee", "alabama", "kentucky", "virginia", "wisconsin",
           "minnesota", "missouri", "kansas", "iowa", "oklahoma", "arkansas", "louisiana", "mississippi",
           "oregon", "washington", "colorado", "arizona", "utah", "nevada", "idaho", "massachusetts",
           "connecticut", "maryland", "delaware", "maine", "vermont", "hampshire", "nebraska", "dakota",
           "montana", "wyoming", "mexico", "hawaii", "alaska", "island", "rhode"}


def _stem(t):
    return t[:-1] if len(t) > 4 and t.endswith("s") and not t.endswith("ss") else t


def name_tokens(s):
    toks = [_stem(t) for t in squash(s).split() if t not in NAME_STOP]
    toks = [t for t in toks if t]
    dist = frozenset(t for t in toks if t not in GENERIC)
    return frozenset(toks), dist


def name_key(s):
    toks = [t for t in squash(s).split() if t not in NAME_STOP]
    return " ".join(toks or squash(s).split())


def name_sim(a, b, drop=frozenset()):
    """a, b = (all_tokens, distinctive_tokens). Location tokens in `drop` (both records' city words) are
    removed first. Returns (containment, jaccard, shared) computed on distinctive tokens when both sides have
    any, else on all tokens."""
    (aa, ad), (ba, bd) = a, b
    if drop:
        aa, ad, ba, bd = aa - drop, ad - drop, ba - drop, bd - drop
    x, y = (ad, bd) if (ad and bd) else (aa, ba)
    if not x or not y:
        return 0.0, 0.0, 0
    inter = len(x & y)
    return inter / min(len(x), len(y)), inter / len(x | y), inter


def name_ok(sim):
    return sim[2] >= 1 and sim[0] >= 0.5


def name_strong(sim):
    return sim[2] >= 1 and sim[0] >= 0.8 and sim[1] >= 0.5


def zip5(z):
    m = re.match(r"\s*(\d{5})", z or "")
    return m.group(1) if m else ""


def iso(d):
    d = (d or "").strip()
    if not d:
        return ""
    try:
        return datetime.strptime(d, "%m/%d/%Y").date().isoformat()
    except ValueError:
        return ""


# ------------------------------------------------------------------ ECHO streaming
def open_echo(zip_path, csv_path):
    if csv_path:
        return open(csv_path, newline="", encoding="utf-8", errors="replace"), None
    z = zipfile.ZipFile(zip_path)
    name = next(n for n in z.namelist() if n.upper().endswith("ECHO_EXPORTER.CSV"))
    return io.TextIOWrapper(z.open(name), encoding="utf-8", errors="replace", newline=""), name


def stream_echo(fh, notes_ids):
    """Yield (stats, facilities, notes_id_rows).  facilities: list of dict for active scoped rows."""
    rd = csv.reader(fh)
    header = next(rd)
    ix = {h: i for i, h in enumerate(header)}
    need = ["REGISTRY_ID", "FAC_NAME", "FAC_STREET", "FAC_CITY", "FAC_STATE", "FAC_ZIP", "FAC_COUNTY",
            "FAC_FIPS_CODE", "FAC_ACTIVE_FLAG", "FAC_NAICS_CODES", "CAA_NAICS", "CWA_NAICS", "RCRA_NAICS",
            "FAC_MAJOR_FLAG", "FAC_DATE_LAST_INSPECTION", "FAC_DATE_LAST_INFORMAL_ACTION",
            "FAC_DATE_LAST_FORMAL_ACTION", "FAC_DATE_LAST_PENALTY", "FAC_COMPLIANCE_STATUS", "TRI_IDS",
            "DFR_URL", "FAC_FEDERAL_FLG"] + [p for p, _ in PROGRAMS]
    missing = [c for c in need if c not in ix]
    if missing:
        sys.exit(f"ECHO header lacks expected columns: {missing}")
    g = {c: ix[c] for c in need}
    st = Counter()
    facs, notes_rows = [], []
    seen = set()
    for row in rd:
        st["rows_total"] += 1
        if len(row) <= g["FAC_NAICS_CODES"]:
            st["rows_short"] += 1
            continue
        rid = row[g["REGISTRY_ID"]].strip()
        if not rid:
            st["rows_blank_registry_id"] += 1
        if rid in notes_ids:
            notes_rows.append((rid, row[g["FAC_NAME"]], row[g["FAC_STATE"]], row[g["FAC_ACTIVE_FLAG"]],
                               row[g["FAC_NAICS_CODES"]]))
        fac_n = row[g["FAC_NAICS_CODES"]]
        prog_n = " ".join(row[g[c]] for c in ("CAA_NAICS", "CWA_NAICS", "RCRA_NAICS"))
        in_fac = NAICS_RE.findall(fac_n)
        in_prog = NAICS_RE.findall(prog_n)
        if not in_fac and not in_prog:
            continue
        st["scoped_any_flag"] += 1
        flag = row[g["FAC_ACTIVE_FLAG"]].strip().upper()
        st["scoped_flag_" + (flag or "blank")] += 1
        if flag != "Y":
            continue
        if not rid:                       # RCRA-only records ECHO has not linked to an FRS ID
            st["scoped_Y_blank_registry_id"] += 1
            continue
        if rid in seen:
            st["dup_registry_id"] += 1
            continue
        seen.add(rid)
        codes = sorted(set(NAICS_RE.findall(fac_n + " " + prog_n)))
        all_codes = sorted(set(re.findall(r"\b\d{6}\b", fac_n + " " + prog_n)))
        if not in_fac:
            st["scoped_only_via_program_naics"] += 1
        d = {
            "registry_id": rid,
            "facility_name": row[g["FAC_NAME"]].strip(),
            "street": row[g["FAC_STREET"]].strip(),
            "city": row[g["FAC_CITY"]].strip(),
            "state": row[g["FAC_STATE"]].strip().upper(),
            "zip": row[g["FAC_ZIP"]].strip(),
            "county_frs": row[g["FAC_COUNTY"]].strip(),
            "fips": row[g["FAC_FIPS_CODE"]].strip(),
            "naics_codes": " ".join(all_codes),
            "naics_scope_codes": " ".join(codes),
            "active_flag": flag,
            "programs": ";".join(lbl for col, lbl in PROGRAMS if row[g[col]].strip().upper() == "Y"),
            "major_flag": row[g["FAC_MAJOR_FLAG"]].strip(),
            "federal_flag": row[g["FAC_FEDERAL_FLG"]].strip(),
            "compliance_status": row[g["FAC_COMPLIANCE_STATUS"]].strip(),
            "last_inspection": iso(row[g["FAC_DATE_LAST_INSPECTION"]]),
            "last_informal_action": iso(row[g["FAC_DATE_LAST_INFORMAL_ACTION"]]),
            "last_formal_action": iso(row[g["FAC_DATE_LAST_FORMAL_ACTION"]]),
            "last_penalty": iso(row[g["FAC_DATE_LAST_PENALTY"]]),
            "tri_ids": row[g["TRI_IDS"]].strip(),
            "dfr_url": row[g["DFR_URL"]].strip(),
        }
        d["last_activity_date"] = max([d[k] for k in ("last_inspection", "last_informal_action",
                                                      "last_formal_action", "last_penalty")] or [""])
        sigs = [code_signal(c) for c in codes]
        d["signal_class"] = min(sigs, key=lambda s: SIGNAL_ORDER[s])
        d["scope_class"] = "core" if any(c.startswith(CORE_PREFIXES) for c in codes) else "ring3_primary"
        d["name_noise_hint"] = "Y" if NOISE_RE.search(d["facility_name"]) else ""
        facs.append(d)
    st["facilities_active_scoped"] = len(facs)
    return st, facs, notes_rows


# ------------------------------------------------------------------ Atlas loading
def read_shards(pattern):
    rows = []
    for path in sorted(glob.glob(pattern)):
        with open(path, newline="", encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                r["__file__"] = os.path.basename(path)
                rows.append(r)
    return rows


_STREET_PATS = [
    re.compile(r"Street(?:\s+correct(?:ion|ed)[^:]{0,20})?(?:\s*\((?:per|from)[^)]*\))?:\s*(\d[^;|\n]{2,80})", re.I),
    re.compile(r"Address[^:]{0,60}match\):\s*(\d[^;|\n]{2,80})", re.I),
]


def street_from_notes(notes, city):
    """Heuristic: the LAST 'Street...:' phrase wins (corrections come later). Returns raw street or ''."""
    hits = []
    for rx in _STREET_PATS:
        for m in rx.finditer(notes or ""):
            hits.append((m.start(), m.group(1)))
    if not hits:
        return ""
    raw = max(hits)[1]
    parts = re.split(r"(?<![\s.][A-Za-z])\.\s+|\s\(", raw, maxsplit=1)
    raw = parts[0].strip().rstrip(".").strip()
    if city:  # drop ', City, ST zip' tails
        raw = re.split(r",\s*" + re.escape(city), raw, flags=re.I)[0]
    return raw


FRS_ID_RE = re.compile(r"\b1\d{11}\b")


class Atlas:
    def __init__(self, data_dir):
        self.sites = read_shards(os.path.join(data_dir, "sites_*.csv"))
        orgs = read_shards(os.path.join(data_dir, "organizations_*.csv"))
        eco = read_shards(os.path.join(data_dir, "ecosystem.csv"))
        self.org = {r["org_id"]: r for r in orgs + eco}
        self.org_namekeys = defaultdict(set)      # name_key -> org_ids
        for r in orgs + eco:
            for nm in [r.get("legal_name", "")] + [t for t in (r.get("trade_names") or "").split(";")]:
                k = name_key(nm)
                if k:
                    self.org_namekeys[k].add(r["org_id"])
        self.org_text = []                        # (org_id, padded squashed legal/trade/notes text)
        for r in orgs + eco:
            t = " ".join([r.get("legal_name", ""), r.get("trade_names", ""), r.get("notes", "")])
            self.org_text.append((r["org_id"], " " + squash(t) + " "))
        self.org_blob = "\x00".join(t for _, t in self.org_text)
        self.org_sites = defaultdict(list)
        self.site_by_id = {}
        self.by_street = defaultdict(list)
        self.by_zip = defaultdict(list)
        self.by_city = defaultdict(list)
        self.by_frs = defaultdict(list)
        self.org_state_sites = defaultdict(list)
        self.site_prof = {}
        for s in self.sites:
            sid = s["site_id"]
            self.site_by_id[sid] = s
            st = (s.get("state") or "").strip().upper()
            fld = (s.get("street_address") or "").strip()
            raw, src = (fld, "street_address") if fld else (street_from_notes(s.get("notes", ""), s.get("city", "")), "notes")
            sk = street_key(raw)
            if not sk:
                src = "none"
            org = self.org.get(s["org_id"], {})
            variants = [s.get("site_name", "")]
            sn = re.split(r"\s+[—–-]\s+", s.get("site_name", ""))[0]
            variants += [sn, org.get("legal_name", "")] + [t for t in (org.get("trade_names") or "").split(";")]
            ntoks = [name_tokens(v) for v in variants if v and v.strip()]
            self.site_prof[sid] = {"state": st, "street_raw": raw if sk else "", "street_key": sk, "street_src": src,
                                   "zip5": zip5(s.get("zip")), "city": squash(s.get("city")), "names": ntoks,
                                   "city_toks": frozenset(_stem(t) for t in squash(s.get("city")).split())}
            self.org_sites[s["org_id"]].append(sid)
            self.org_state_sites[(s["org_id"], st)].append(sid)
            if sk:
                self.by_street[(st, sk)].append(sid)
            if zip5(s.get("zip")):
                self.by_zip[(st, zip5(s.get("zip")))].append(sid)
            if squash(s.get("city")):
                self.by_city[(st, squash(s.get("city")))].append(sid)
            for fid in set(FRS_ID_RE.findall(s.get("notes", ""))):
                self.by_frs[fid].append(sid)
        self.trifid_orgs = defaultdict(set)
        with open(os.path.join(data_dir, "registry_links.csv"), newline="", encoding="utf-8-sig") as fh:
            self.links = list(csv.DictReader(fh))
        for r in self.links:
            if r["registry"] == "TRI_TRIFID":
                self.trifid_orgs[r["registry_id"].strip()].add(r["org_id"])
        self.frs_links = [r for r in self.links if r["registry"] == "FRS"]


# ------------------------------------------------------------------ matching
RANK = {"street_exact+loc+name": 100, "street_exact+loc+id": 95, "name_zip_street_unknown": 80,
        "frs_id_in_notes+name+loc": 78,
        "street_exact+loc_name_differs": 60, "name_city_street_unknown": 50, "name_zip_weak": 45,
        "trifid_org+loc_no_street": 40, "street_exact_locality_differs": 30}


def judge(f, fk, A, sid, id_hit, tri_orgs):
    """Return (kind, parts, sim) for facility f vs site sid, or None when the pair is not a candidate."""
    p = A.site_prof[sid]
    fstreet = fk["street_key"]
    street = "na"
    if fstreet and p["street_key"]:
        street = "eq" if fstreet == p["street_key"] else "diff"
    zip_eq = bool(fk["zip5"] and p["zip5"] and fk["zip5"] == p["zip5"])
    city_eq = bool(fk["city"] and p["city"] and fk["city"] == p["city"])
    loc = "zip" if zip_eq else ("city" if city_eq else "")
    drop = fk["city_toks"] | p["city_toks"]
    sim = max((name_sim(fk["name"], n, drop) for n in p["names"]), key=lambda t: (t[2] >= 1, t[0], t[1]), default=(0, 0, 0))
    is_tri = A.site_by_id[sid]["org_id"] in tri_orgs
    parts = []
    if street == "eq":
        parts.append("street_exact")
    if loc:
        parts.append("zip5" if loc == "zip" else "city")
    if id_hit:
        parts.append("frs_id_in_site_notes")
    if is_tri:
        parts.append("trifid_held_for_org")
    parts.append("name_sim=%.2f" % sim[0])
    if street == "eq" and loc:
        if name_ok(sim):
            return "street_exact+loc+name", parts, sim
        if id_hit or is_tri:
            return "street_exact+loc+id", parts, sim
        return "street_exact+loc_name_differs", parts, sim
    if street == "eq":
        return "street_exact_locality_differs", parts, sim
    if street == "na":
        if loc == "zip" and name_strong(sim):
            return "name_zip_street_unknown", parts, sim
        if id_hit and loc and name_ok(sim):
            return "frs_id_in_notes+name+loc", parts, sim
        if loc == "city" and name_strong(sim):
            return "name_city_street_unknown", parts, sim
        if loc and name_ok(sim):
            return "name_zip_weak", parts, sim
        if is_tri and loc:
            return "trifid_org+loc_no_street", parts, sim
    return None


MATCH_KINDS = {"street_exact+loc+name", "street_exact+loc+id", "name_zip_street_unknown", "frs_id_in_notes+name+loc"}
STRENGTH = {"street_exact+loc+name": "strong", "street_exact+loc+id": "strong_id_corroborated_name_differs",
            "name_zip_street_unknown": "moderate", "frs_id_in_notes+name+loc": "moderate"}


def match_facilities(facs, A):
    out = []
    for f in facs:
        fk = {"street_key": street_key(f["street"]), "zip5": zip5(f["zip"]), "city": squash(f["city"]),
              "city_toks": frozenset(_stem(t) for t in squash(f["city"]).split()),
              "name": name_tokens(f["facility_name"])}
        st = f["state"]
        cand = set()
        if fk["street_key"]:
            cand.update(A.by_street.get((st, fk["street_key"]), ()))
        id_sites = set(A.by_frs.get(f["registry_id"], ()))
        cand.update(i for i in id_sites if A.site_prof[i]["state"] == st)
        tri_orgs = set()
        for t in f["tri_ids"].replace(",", " ").split():
            tri_orgs |= A.trifid_orgs.get(t, set())
        for o in tri_orgs:
            cand.update(A.org_state_sites.get((o, st), ()))
        if fk["zip5"]:
            cand.update(A.by_zip.get((st, fk["zip5"]), ()))
        if fk["city"]:
            cand.update(A.by_city.get((st, fk["city"]), ()))
        judged = []
        diff_strong = []
        for sid in cand:
            j = judge(f, fk, A, sid, sid in id_sites, tri_orgs)
            if j:
                judged.append((RANK[j[0]], j[2][0], sid, j))
            else:
                p = A.site_prof[sid]
                if fk["street_key"] and p["street_key"] and fk["street_key"] != p["street_key"] \
                        and (fk["city"] == p["city"] or (fk["zip5"] and fk["zip5"] == p["zip5"])):
                    sims = max((name_sim(fk["name"], n, fk["city_toks"] | p["city_toks"]) for n in p["names"]),
                               key=lambda t: (t[2] >= 1, t[0], t[1]))
                    if name_strong(sims):
                        diff_strong.append(sid)
        rec = {"f": f, "verdict": "NO_MATCH", "basis": "", "strength": "", "site_id": "", "alts": "",
               "name_sim": "", "kind": "", "tie_same_org": False, "diff_addr_sites": ";".join(sorted(diff_strong)[:3])}
        if judged:
            judged.sort(key=lambda t: (-t[0], -t[1], t[2]))
            top = judged[0]
            ties = [t for t in judged if t[0] == top[0] and abs(t[1] - top[1]) < 1e-9 and t[2] != top[2]]
            kind, parts, sim = top[3]
            rec.update(kind=kind, site_id=top[2], name_sim="%.2f" % sim[0],
                       basis=kind + ":" + ",".join(parts),
                       alts=";".join(t[2] for t in judged[1:6]))
            if kind in MATCH_KINDS and not ties:
                rec.update(verdict="MATCH_SITE", strength=STRENGTH[kind])
            else:
                rec["verdict"] = "POSSIBLE"
                if ties:
                    tied = [top[2]] + [t[2] for t in ties]
                    same_org = len({A.site_by_id[x]["org_id"] for x in tied}) == 1
                    rec["basis"] += (";tie_same_org_possible_duplicate_sites=" if same_org
                                     else ";ambiguous_equal_rank_sites=") + ",".join(tied[:6])
                    rec["tie_same_org"] = same_org
                rec["strength"] = "weak"
        out.append(rec)
    # a site matched by several FRS records, and an FRS record's competing claims
    per_site = defaultdict(list)
    for r in out:
        if r["verdict"] == "MATCH_SITE":
            per_site[r["site_id"]].append(r["f"]["registry_id"])
    for r in out:
        r["site_frs_count"] = len(per_site.get(r["site_id"], [])) if r["verdict"] == "MATCH_SITE" else ""
        r["site_frs_ids"] = ";".join(sorted(per_site[r["site_id"]])) if r["verdict"] == "MATCH_SITE" and len(per_site[r["site_id"]]) > 1 else ""
    return out


def lead_class(rec, A):
    """For NO_MATCH: is the facility a possible extra site of a held org, or net new?  Mirrors AGENTS 3
    steps 2 and 4 (normalized name vs legal/trade names; then trade_names/notes mentions)."""
    f = rec["f"]
    k = name_key(f["facility_name"])
    orgs = sorted(A.org_namekeys.get(k, ()))
    if rec["diff_addr_sites"]:
        return "HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS", rec["diff_addr_sites"]
    if orgs:
        return "NAME_EQUALS_HELD_ORG_OTHER_LOCATION", ";".join(orgs[:3])
    toks = squash(k).split()
    has_distinct = any(_stem(t) not in GENERIC for t in toks)
    if has_distinct and (len(toks) >= 2 or len(k) >= 6):
        needle = " " + " ".join(toks) + " "
        if needle in A.org_blob:
            hits = [oid for oid, t in A.org_text if needle in t]
            return "NAME_IN_HELD_ORG_TRADE_NAMES_OR_NOTES", ";".join(hits[:3])
    return "NET_NEW_LEAD", ""


# ------------------------------------------------------------------ gaps
def qcew_gap(qcew_csv, A):
    gap = {}
    with open(qcew_csv, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["year"] == "2023" and r["industry_code"] == "326" and r["area_fips"].endswith("000") \
                    and r["area_fips"] != "US000":
                nm = r["area_title"].split(" -- ")[0].split(",")[0].strip()
                if nm in STATE_NAMES:
                    gap[STATE_NAMES[nm]] = int(r["annual_avg_estabs"])
    strict = Counter()
    for s in A.sites:
        if s.get("operating_status") in ("active", "unknown") and s.get("verification_tier") in ("A", "B", "C") \
                and (s.get("naics_primary") or "").startswith("326"):
            strict[(s.get("state") or "").strip().upper()] += 1
    return {st: (q, strict.get(st, 0), q - strict.get(st, 0)) for st, q in gap.items()}


# ------------------------------------------------------------------ output
FAC_COLS = ["registry_id", "facility_name", "street", "city", "state", "zip", "county_frs", "naics_codes",
            "naics_scope_codes", "scope_class", "signal_class", "active_flag", "programs", "major_flag",
            "compliance_status", "last_inspection", "last_formal_action", "last_informal_action", "last_penalty",
            "last_activity_date", "tri_ids", "name_noise_hint", "dfr_url"]
MATCH_COLS = ["registry_id", "facility_name", "street", "city", "state", "zip", "scope_class", "signal_class",
              "verdict", "match_strength", "basis", "site_id", "org_id", "site_name", "site_operating_status",
              "site_street_source", "name_sim", "alt_site_ids", "site_frs_count", "site_frs_ids",
              "lead_class", "lead_ref", "liveness_note", "last_activity_date",
              "proposed_registry_links_row_org_id", "proposed_registry", "proposed_registry_id",
              "proposed_match_basis", "proposed_as_of"]


def liveness_note(rec, A, as_of):
    f = rec["f"]
    notes = []
    if rec["verdict"] == "MATCH_SITE":
        s = A.site_by_id[rec["site_id"]]
        status = s.get("operating_status", "")
        recent = bool(f["last_activity_date"]) and (as_of - date.fromisoformat(f["last_activity_date"])).days <= 3 * 365
        if status in ("closed", "idled", "active_idled_partial"):
            notes.append("atlas_status_%s_but_echo_permit_active%s" % (status, "_with_recent_activity" if recent else ""))
        elif recent:
            notes.append("echo_activity_within_3y")
    return ";".join(notes)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--zip", default="/tmp/claude-0/echo_raw/echo_exporter.zip")
    ap.add_argument("--csv", help="read an already-extracted ECHO_EXPORTER.csv instead of --zip")
    ap.add_argument("--data-dir", default=os.path.join(REPO, "data"))
    ap.add_argument("--qcew", default=os.path.join(REPO, "docs", "denominators", "qcew_state_polymer_2023_2024.csv"))
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--as-of", default=date.today().isoformat(), help="retrieval date stamped on proposed links")
    a = ap.parse_args(argv)
    as_of = date.fromisoformat(a.as_of)

    A = Atlas(a.data_dir)
    src = a.csv or a.zip
    sha = hashlib.sha256()
    with open(src, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            sha.update(chunk)
    notes_ids = set(A.by_frs)
    fh, member = open_echo(a.zip, a.csv)
    with fh:
        st, facs, notes_rows = stream_echo(fh, notes_ids)
    ids = [f["registry_id"] for f in facs]
    assert len(ids) == len(set(ids)), "REGISTRY_ID not unique in facilities"   # AGENTS 2 rule 10b

    recs = match_facilities(facs, A)
    for r in recs:
        r["lead"], r["lead_ref"] = lead_class(r, A) if r["verdict"] == "NO_MATCH" else ("", "")

    os.makedirs(a.out_dir, exist_ok=True)
    facs_sorted = sorted(facs, key=lambda d: (d["state"], d["city"], d["facility_name"], d["registry_id"]))
    with open(os.path.join(a.out_dir, "facilities.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, FAC_COLS, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(facs_sorted)

    seen_triples = set()
    rows_out = []
    for r in sorted(recs, key=lambda r: (r["f"]["state"], r["f"]["city"], r["f"]["facility_name"], r["f"]["registry_id"])):
        f = r["f"]
        s = A.site_by_id.get(r["site_id"]) if r["site_id"] else None
        row = {c: f.get(c, "") for c in ("registry_id", "facility_name", "street", "city", "state", "zip",
                                         "scope_class", "signal_class", "last_activity_date")}
        row.update(verdict=r["verdict"], match_strength=r["strength"], basis=r["basis"], site_id=r["site_id"],
                   org_id=s["org_id"] if s else "", site_name=s["site_name"] if s else "",
                   site_operating_status=s["operating_status"] if s else "",
                   site_street_source=A.site_prof[r["site_id"]]["street_src"] if s else "",
                   name_sim=r["name_sim"], alt_site_ids=r["alts"], site_frs_count=r["site_frs_count"],
                   site_frs_ids=r["site_frs_ids"], lead_class=r["lead"], lead_ref=r["lead_ref"],
                   liveness_note=liveness_note(r, A, as_of))
        if r["verdict"] == "MATCH_SITE":
            trip = (s["org_id"], "FRS", f["registry_id"])
            if trip not in seen_triples:
                seen_triples.add(trip)
                row.update(proposed_registry_links_row_org_id=s["org_id"], proposed_registry="FRS",
                           proposed_registry_id=f["registry_id"],
                           proposed_match_basis="echo_exporter_%s:%s" % (r["kind"].replace("+", "_"), r["site_id"]),
                           proposed_as_of=a.as_of)
        rows_out.append(row)
    with open(os.path.join(a.out_dir, "site_matches.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, MATCH_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows_out)

    # ---- counts (every count carries its unit and filter in REPORT.md)
    gaps = qcew_gap(a.qcew, A)
    by_state = defaultdict(Counter)
    distinct_loc = defaultdict(set)
    for r in recs:
        f = r["f"]
        c = by_state[f["state"]]
        c["facilities"] += 1
        c["facilities_" + f["scope_class"]] += 1
        c[r["verdict"]] += 1
        if r["verdict"] == "NO_MATCH":
            core_p = f["scope_class"] == "core" and f["signal_class"] == "P"
            if f["scope_class"] == "core":
                c["no_match_core"] += 1
            if core_p:
                c["no_match_core_P"] += 1
                c["lead_" + r["lead"]] += 1
                loc = (f["state"], street_key(f["street"]), zip5(f["zip"])) if street_key(f["street"]) else ("id", f["registry_id"])
                distinct_loc[f["state"]].add(loc)
                if f["name_noise_hint"]:
                    c["no_match_core_P_noise_hint"] += 1
    lead_cols = ["state", "qcew_2023_326_private_estabs", "atlas_strict_326_sites", "qcew_gap", "gap_rank",
                 "echo_active_scoped_facilities", "of_core", "of_ring3_primary", "match_site", "possible", "no_match",
                 "no_match_core", "no_match_core_signal_P", "of_which_net_new_lead",
                 "of_which_name_in_held_org_trade_names_or_notes",
                 "of_which_name_equals_held_org_other_location", "of_which_held_org_same_name_city_diff_address",
                 "of_which_name_noise_hint", "no_match_core_signal_P_distinct_street_zip"]
    ordered = sorted(by_state, key=lambda s: (-(gaps[s][2]) if s in gaps else 10 ** 9, s))
    gap_rank = {s: i + 1 for i, s in enumerate(sorted(gaps, key=lambda s: -gaps[s][2]))}
    with open(os.path.join(a.out_dir, "leads_by_state.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(lead_cols)
        for s in ordered:
            c = by_state[s]
            q = gaps.get(s)
            w.writerow([s, q[0] if q else "", q[1] if q else "", q[2] if q else "", gap_rank.get(s, ""),
                        c["facilities"], c["facilities_core"], c["facilities_ring3_primary"], c["MATCH_SITE"],
                        c["POSSIBLE"], c["NO_MATCH"], c["no_match_core"], c["no_match_core_P"],
                        c["lead_NET_NEW_LEAD"], c["lead_NAME_IN_HELD_ORG_TRADE_NAMES_OR_NOTES"],
                        c["lead_NAME_EQUALS_HELD_ORG_OTHER_LOCATION"],
                        c["lead_HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS"], c["no_match_core_P_noise_hint"],
                        len(distinct_loc[s])])

    # reconciliation (AGENTS 2 rule 10c spirit): the per-state sums must equal the facility total
    tot = Counter()
    for c in by_state.values():
        tot.update(c)
    assert tot["facilities"] == len(facs) == len(rows_out)
    assert tot["MATCH_SITE"] + tot["POSSIBLE"] + tot["NO_MATCH"] == len(facs)

    write_report(a, A, st, facs, recs, rows_out, by_state, gaps, ordered, notes_rows, sha.hexdigest(), member, as_of, distinct_loc)
    print("facilities:", len(facs), dict((k, tot[k]) for k in ("MATCH_SITE", "POSSIBLE", "NO_MATCH")))
    return 0


def pct(n, d):
    return "%.1f%%" % (100.0 * n / d) if d else "n/a"


def write_report(a, A, st, facs, recs, rows_out, by_state, gaps, ordered, notes_rows, sha, member, as_of, distinct_loc):
    n = len(facs)
    v = Counter(r["verdict"] for r in recs)
    kinds = Counter(r["kind"] for r in recs if r["verdict"] == "MATCH_SITE")
    pk = Counter(r["kind"] for r in recs if r["verdict"] == "POSSIBLE")
    core = [r for r in recs if r["f"]["scope_class"] == "core"]
    r3 = [r for r in recs if r["f"]["scope_class"] == "ring3_primary"]
    corep = [r for r in core if r["f"]["signal_class"] == "P"]
    vc = Counter(r["verdict"] for r in core)
    vcp = Counter(r["verdict"] for r in corep)
    v3 = Counter(r["verdict"] for r in r3)
    sigs = Counter(r["f"]["signal_class"] for r in recs)
    prop = [r for r in rows_out if r.get("proposed_registry_id")]
    prop_strength = Counter(r["match_strength"] for r in prop)
    tie_same_org = sum(1 for r in recs if r["tie_same_org"])
    tie_other = sum(1 for r in recs if r["verdict"] == "POSSIBLE" and "ambiguous_equal_rank_sites" in r["basis"])
    matched_sites = {r["site_id"] for r in recs if r["verdict"] == "MATCH_SITE"}
    multi = {s for s in matched_sites if sum(1 for r in recs if r["verdict"] == "MATCH_SITE" and r["site_id"] == s) > 1}
    # Atlas denominators for match-rate context
    sites_total = len(A.sites)
    core_codes_sites = [s for s in A.sites if (s.get("naics_primary") or "").startswith(CORE_PREFIXES)
                        and s.get("operating_status") in ("active", "unknown")]
    sites_with_street = sum(1 for p in A.site_prof.values() if p["street_key"])
    sites_street_field = sum(1 for p in A.site_prof.values() if p["street_src"] == "street_address")
    sites_street_notes = sum(1 for p in A.site_prof.values() if p["street_src"] == "notes")
    # liveness
    rec3 = lambda r: bool(r["f"]["last_activity_date"]) and (as_of - date.fromisoformat(r["f"]["last_activity_date"])).days <= 3 * 365
    any_act = sum(1 for r in recs if r["f"]["last_activity_date"])
    recent = sum(1 for r in recs if rec3(r))
    ms = [r for r in recs if r["verdict"] == "MATCH_SITE"]
    ms_recent = sum(1 for r in ms if rec3(r))
    conflict = [r for r in rows_out if r["liveness_note"].startswith("atlas_status_")]
    # notes-FRS verification
    notes_ids = set(A.by_frs)
    found = {}
    for rid, nm, stt, flag, naics in notes_rows:
        found[rid] = (nm, stt, flag, naics)
    notes_in_filtered = {f["registry_id"] for f in facs} & notes_ids
    id_agree = sum(1 for r in recs if r["verdict"] == "MATCH_SITE" and r["site_id"] in A.by_frs.get(r["f"]["registry_id"], ()))
    id_conflict = 0
    for r in recs:
        if r["verdict"] == "MATCH_SITE":
            sid = r["site_id"]
            notes_ids_for_site = set(FRS_ID_RE.findall(A.site_by_id[sid].get("notes", "")))
            if notes_ids_for_site and r["f"]["registry_id"] not in notes_ids_for_site:
                id_conflict += 1
    lines = []
    L = lines.append
    L("# ECHO / FRS polymer facility spine - %s" % as_of.isoformat())
    L("")
    L("**Status: lead product, not Atlas data.** Nothing here edits `data/`, mints a registry link, sets a tier or "
      "changes a status. Built by `scripts/build_echo_spine.py` (stdlib; re-runnable). Packet lane output: the "
      "integrator of record decides what, if anything, is applied.")
    L("")
    L("## 1. Source and filter")
    L("")
    L("- **Source:** EPA ECHO exporter, `https://echo.epa.gov/files/echodownloads/echo_exporter.zip` (member `%s`), "
      "retrieved %s, zip SHA-256 `%s`. Column dictionary: https://echo.epa.gov/tools/data-downloads "
      "(`echo_exporter_columns_7-16-2025_0.xlsx`); every column name used was checked against the extract header." % (
          member or os.path.basename(a.csv or ""), as_of.isoformat(), sha))
    L("- **Rows read:** %s ECHO exporter rows (unit: one ECHO record per row; %s rows carry a blank REGISTRY_ID)." % (
        format(st["rows_total"], ","), format(st["rows_blank_registry_id"], ",")))
    L("- **Scope filter (any one of):** a 6-digit NAICS code under 3252, 3255, 3259 or 326 (`core`), or a Ring 3 "
      "Primary code 333511 / 424610 / 562920 (`ring3_primary`; SCHEMA 2.2). NAICS read from `FAC_NAICS_CODES` plus "
      "the program fields `CAA_NAICS`, `CWA_NAICS`, `RCRA_NAICS`; %s facilities enter only through a program NAICS field."
      % format(st["scoped_only_via_program_naics"], ","))
    L("- **Active filter:** `FAC_ACTIVE_FLAG = Y`. ECHO's definition: *any associated ICIS-Air, ICIS-NPDES, RCRA or "
      "SDWA permit is in an active status* - a **permit** fact. In this extract the flag takes only the values Y and "
      "blank (no N occurs). NAICS-scoped rows by flag: Y = %s, N = %s, blank = %s (blank rows are dropped; a blank "
      "flag is not evidence of closure - it also covers TRI/GHG-only records and lapsed permits). Of the Y rows, %s "
      "carry a **blank REGISTRY_ID** (RCRA-only records ECHO has not linked to FRS) and are excluded because they "
      "cannot carry an FRS link; the other %s have unique non-blank REGISTRY_IDs (uniqueness asserted)." % (
          format(st["scoped_flag_Y"], ","), format(st["scoped_flag_N"], ","), format(st["scoped_flag_blank"], ","),
          format(st["scoped_Y_blank_registry_id"], ","), format(n, ",")))
    L("- **Result:** **%s active, NAICS-scoped ECHO facilities** (unit: FRS registry IDs; `facilities.csv`): "
      "%s `core` + %s `ring3_primary`." % (format(n, ","), format(len(core), ","), format(len(r3), ",")))
    L("- **SCHEMA 2.2 signal of the best matched code** (P primary / S secondary / X exclude-by-default / U in scope "
      "but not listed in 2.2): P %s, S %s, U %s, X %s." % tuple(format(sigs[k], ",") for k in "PSUX"))
    L("")
    L("## 2. Match to Atlas sites")
    L("")
    L("Atlas side: %s site rows (all shards, any status/tier). Street key from the `street_address` column for %s "
      "sites and, where that column is blank, a heuristic read of `Street...:` phrases in `notes` for a further %s "
      "(total %s = %s of site rows have a usable street key; the rest can match only on name + zip/city)." % (
          format(sites_total, ","), format(sites_street_field, ","), format(sites_street_notes, ","),
          format(sites_with_street, ","), pct(sites_with_street, sites_total)))
    L("")
    L("Method per facility (first/best hit wins; operator rule, AGENTS 3): (1) normalized street + state + (zip5 or "
      "city) + name agreement = `street_exact+loc+name`; the same with a name disagreement is **POSSIBLE** "
      "(co-tenant or successor operator), unless an FRS ID in site notes or a held TRIFID for that org corroborates "
      "(`street_exact+loc+id`); (2) where the street is missing on either side, same zip5 + strong name similarity "
      "= `name_zip_street_unknown` (moderate); same city + strong name, or same zip + weaker name = POSSIBLE; "
      "(3) two Atlas sites tied at the top rank = POSSIBLE with the tie listed. Both streets present but different "
      "is never a match (a second plant is a second site). Name similarity compares the FRS name with the site "
      "name, the org legal name and trade names on distinctive tokens (generic plastics words removed).")
    L("")
    L("| Verdict | Facilities (core + ring3_primary) | core only | core, signal P only | ring3_primary only |")
    L("|---|---:|---:|---:|---:|")
    for k in ("MATCH_SITE", "POSSIBLE", "NO_MATCH"):
        L("| %s | %s | %s | %s | %s |" % (k, format(v[k], ","), format(vc[k], ","), format(vcp[k], ","), format(v3[k], ",")))
    L("| **Total** | **%s** | **%s** | **%s** | **%s** |" % (format(n, ","), format(len(core), ","), format(len(corep), ","), format(len(r3), ",")))
    L("")
    L("**Match rate (unit: active NAICS-scoped ECHO facilities matched to an Atlas site row):** MATCH_SITE = %s of %s "
      "(**%s**); MATCH_SITE + POSSIBLE = %s. core + signal P: %s MATCH_SITE. This is a **facility-to-site match "
      "rate, not Atlas coverage**: ECHO lists permit holders only, many Atlas sites hold no EPA permit, and "
      "state-level coverage is a separate count-ratio question (see `docs/denominators/README.md`)." % (
          format(v["MATCH_SITE"], ","), format(n, ","), pct(v["MATCH_SITE"], n),
          pct(v["MATCH_SITE"] + v["POSSIBLE"], n), pct(vcp["MATCH_SITE"], len(corep))))
    L("")
    L("MATCH_SITE by basis: " + "; ".join("`%s` %s" % (k, format(c, ",")) for k, c in kinds.most_common()) + ". "
      "POSSIBLE by best basis: " + "; ".join("`%s` %s" % (k, format(c, ",")) for k, c in pk.most_common()) + ".")
    L("")
    L("Atlas sites reached by at least one MATCH_SITE facility: %s distinct sites (unit: Atlas site rows); %s of them "
      "match more than one FRS record (FRS often holds duplicate or program-specific registry IDs for one location; "
      "all are listed in `site_frs_ids`)." % (format(len(matched_sites), ","), format(len(multi), ",")))
    L("")
    L("## 3. FRS registry-link candidates")
    L("")
    L("`site_matches.csv` carries, for every MATCH_SITE row, a proposed `registry_links` row: `org_id` = the matched "
      "site's parent org, `registry` = `FRS`, `registry_id` = REGISTRY_ID verbatim, `match_basis` = "
      "`echo_exporter_<basis>:<site_id>`, `as_of` = %s. **%s candidate rows** (unit: distinct org_id + FRS ID "
      "pairs): `strong` (street + zip/city + name agree) %s; `strong_id_corroborated_name_differs` (street + zip/city "
      "agree, FRS name differs from the Atlas names, but a held TRIFID or an FRS ID in site notes corroborates - often a "
      "former operator name) %s; `moderate` (name + zip, street unknown on a side) %s. `data/registry_links.csv` "
      "holds **%s** FRS rows today, so there is no collision. A further %s facilities tie between two Atlas sites "
      "of the **same org** at one address (`tie_same_org_possible_duplicate_sites` in `basis`; the org is "
      "unambiguous but the site is not - these look like duplicate site rows in the Atlas and are a dedupe lead; no "
      "link row is proposed for them) and %s tie across different orgs." % (
          as_of.isoformat(), format(len(prop), ","), format(prop_strength["strong"], ","),
          format(prop_strength["strong_id_corroborated_name_differs"], ","),
          format(prop_strength["moderate"], ","), len(A.frs_links), format(tie_same_org, ","), format(tie_other, ",")))
    L("")
    L("**Registry-ID verification (AGENTS 4):** every REGISTRY_ID above is read from the ECHO extract's own "
      "`REGISTRY_ID` column, so none is a phantom. Separately, %s distinct FRS-shaped IDs appear in Atlas site `notes` "
      "(written by earlier gov-data passes); %s of them are present in the ECHO extract at all (any NAICS/flag) and "
      "%s are in this spine. Where an ID in notes and the matched FRS record agree: %s MATCH_SITE rows; where the "
      "site's notes name a *different* FRS ID than the one matched: %s rows (FRS holds several IDs per location - "
      "review before minting)." % (
          format(len(notes_ids), ","), format(len(found), ","), format(len(notes_in_filtered), ","),
          format(id_agree, ","), format(id_conflict, ",")))
    L("")
    L("### Grain flag - OWNER RULING NEEDED (not decided here)")
    L("")
    L("`registry_links` is **org-keyed** (SCHEMA 4.8: `org_id MUST`, PK triple org_id + registry + registry_id; "
      "validator V-6 checks only org_id existence and `registry_id` non-empty). An FRS ID is a **facility**-grain "
      "identifier: one ID names one regulated location, and an organization with N plants holds N FRS IDs, each "
      "belonging to a different site. The existing 2,156 `TRI_TRIFID` rows have the same shape and carry the "
      "site only inside free-text `match_basis`. Options for the owner: (a) keep org-keyed rows and embed "
      "`:<site_id>` in `match_basis` (this packet's proposal; no schema change; not machine-joinable); (b) add a "
      "nullable `site_id` column to `registry_links` (schema revision; FRS and TRIFID rows could then be "
      "backfilled); (c) a separate site-keyed registry table. Under any option the integrator would also need a "
      "rule for a site with several FRS IDs and for an FRS ID shared by co-located operators (SCHEMA 5.3: one "
      "address = one site under the operator). This packet takes no position; its rows are written so that "
      "(a) can be applied mechanically and (b) can be derived from the `:<site_id>` suffix.")
    L("")
    L("## 4. National discovery spine (NO_MATCH leads)")
    L("")
    L("NO_MATCH = no Atlas site candidate cleared the ladder in section 2. It is a **lead, not a finding of absence**: "
      "FRS names and streets are permit-holder grade, and the Atlas may hold the plant under a different name or a "
      "street form this normalizer did not equate. Each NO_MATCH row carries a `lead_class`: "
      "`HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS` (a held site in the same city/zip has a strongly similar name but "
      "a different street - possible address variance or second plant; `lead_ref` = site IDs), "
      "`NAME_EQUALS_HELD_ORG_OTHER_LOCATION` (the normalized FRS name equals a held org's legal or trade name - "
      "likely an additional site of a held org; AGENTS 3 step 2; `lead_ref` = org IDs), "
      "`NAME_IN_HELD_ORG_TRADE_NAMES_OR_NOTES` (the normalized name appears inside a held org's trade names or "
      "notes - AGENTS 3 step 4, rebrands/acquisitions; `lead_ref` = org IDs), `NET_NEW_LEAD` (none of these hit; "
      "still subject to the full AGENTS 3 dedupe incl. website domain, which ECHO does not carry). Rows with "
      "`name_noise_hint = Y` look like schools, golf clubs, municipal bodies, etc. that carry a stray NAICS.")
    L("")
    L("**NO_MATCH counts (unit: active NAICS-scoped ECHO facilities with no Atlas site candidate):** %s overall; core %s; "
      "core + SCHEMA 2.2 signal P %s; ring3_primary %s." % (
          format(v["NO_MATCH"], ","), format(vc["NO_MATCH"], ","), format(vcp["NO_MATCH"], ","), format(v3["NO_MATCH"], ",")))
    L("")
    L("The lead pool is FRS records, not locations: %s of the %s core + signal-P NO_MATCH facilities share a "
      "street + zip with another such record (FRS duplicates), leaving **%s distinct street + zip locations** "
      "(records without a usable street count one each). " % (
          format(vcp["NO_MATCH"] - sum(len(x) for x in distinct_loc.values()), ","), format(vcp["NO_MATCH"], ","),
          format(sum(len(x) for x in distinct_loc.values()), ",")) +
      "By state, sorted by the QCEW gap (QCEW 2023 private establishments, NAICS 326, minus Atlas strict 326 sites - "
      "the `docs/denominators/README.md` definition, recomputed from `data/sites_*.csv` at run time). Columns: "
      "gap; ECHO active scoped facilities; MATCH_SITE; NO_MATCH, core + signal P (the lead pool); of which "
      "net-new-name leads. Full table with all states and columns: `leads_by_state.csv`.")
    L("")
    L("| Gap rank | State | QCEW gap (326) | ECHO facilities | MATCH_SITE | NO_MATCH core, signal P | of which NET_NEW_LEAD |")
    L("|---:|---|---:|---:|---:|---:|---:|")
    shown = 0
    for s in ordered:
        if s not in gaps:
            continue
        c = by_state[s]
        shown += 1
        if shown > 20:
            break
        L("| %d | %s | %s | %s | %s | %s | %s |" % (shown, s, format(gaps[s][2], ","), format(c["facilities"], ","),
                                                   format(c["MATCH_SITE"], ","), format(c["no_match_core_P"], ","),
                                                   format(c["lead_NET_NEW_LEAD"], ",")))
    L("")
    L("Top-gap states are the ones where the QCEW says the most establishments exist beyond the Atlas's strict "
      "NAICS-326 site count; the ECHO lead pool per state is **not** an estimate of that gap (ECHO covers permitted "
      "facilities only, and ECHO NAICS does not map one-to-one to QCEW establishments).")
    L("")
    L("## 5. Liveness (signal only)")
    L("")
    L("`facilities.csv` carries `last_inspection`, `last_formal_action`, `last_informal_action`, `last_penalty` "
      "(ISO dates from ECHO) and `last_activity_date` = the latest of them. Of %s active scoped facilities, %s have "
      "any such date and %s have one within 3 years of %s. Among the %s MATCH_SITE facilities, %s have activity "
      "within 3 years. `liveness_note` flags MATCH_SITE rows where the Atlas site is `closed`/`idled` while the ECHO "
      "permit is still active: **%s rows** (listed in `site_matches.csv`)." % (
          format(n, ","), format(any_act, ","), format(recent, ","), as_of.isoformat(), format(len(ms), ","),
          format(ms_recent, ","), format(len(conflict), ",")))
    L("")
    L("Cautions, binding on any reader: an inspection or enforcement date shows a regulator touched the permit, "
      "not that the plant runs; a **missing** date, a blank `FAC_ACTIVE_FLAG`, or a failed match is never evidence "
      "of closure (AGENTS 3, 8). A stale active-permit flag with a closed Atlas site is a *re-verification lead*. "
      "Status changes still need dated primary or near-primary evidence (AGENTS 3); this file supplies none.")
    L("")
    L("## 6. Data-quality caveats")
    L("")
    L("- **Permit-holder grade identity.** `FAC_NAME` is the company or permit holder name as maintained by FRS; "
      "`FAC_STREET` is as maintained by FRS. Names can be a parent, a landlord, a former operator or a site label; "
      "streets can be a mailing or permit address. Treat every match as address-level evidence for the *facility "
      "record*, not for the operator's identity (operator rule, SCHEMA 5.3).")
    L("- **NAICS is program-reported.** `FAC_NAICS_CODES` aggregates codes reported to EPA programs (and FRS "
      "reconciliation). It is a `government_filing` value **for the facility** (SCHEMA 2.1 vocabulary) and "
      "must never be copied to an organization, never decide a ring, and never overwrite a site NAICS that has its "
      "own source. Stray codes are common (see `name_noise_hint`); a code under 3259 includes explosives (325920, "
      "X signal) and inks, and 325510 includes paint retail records the Sherwin-Williams ruling excludes.")
    L("- **FRS duplicates.** One location can hold several REGISTRY_IDs; one ID can be reused for a campus. Counts "
      "of facilities are counts of FRS IDs, **not** counts of establishments (AGENTS 7).")
    L("- **County.** `county_frs` is FRS-maintained and shown for orientation only; Ohio sites need the county from "
      "the physical address (AGENTS 4), not from this column.")
    L("- **QCEW gap** is blank for GU, MP (BLS state file has no such rows in `docs/denominators/`); DC is included "
      "(BLS title \"District of Columbia, not unknown\"; 1 private NAICS-326 establishment, N-flagged).")
    L("- **No coordinates** are read or output (reference data, never evidence or a match key).")
    L("- **Territories and federal facilities** are included if they pass the filter (no federal exclusion applied); "
      "Atlas has no site shard for PR/VI/GU/AS/MP, so those rows are NO_MATCH by construction and have no QCEW gap here.")
    L("- **Not used:** FRS `national_single.zip` (optional in the brief; not needed for the ECHO fields above), Form "
      "5500 / TRI cross-checks beyond held TRIFIDs, any web fetch. No verdict in this file is a REJECT or VERIFIED "
      "in the AGENTS 2.8 grammar - they are match candidates.")
    L("- **Output size.** `facilities.csv` and `site_matches.csv` are large for a PR; the integrator may prefer "
      "to split by state shard if this is applied in parts (SCHEMA Appendix C 6.5 size budget).")
    L("")
    L("## 7. Reproduce")
    L("")
    L("```")
    L("curl -sS -o /tmp/claude-0/echo_raw/echo_exporter.zip https://echo.epa.gov/files/echodownloads/echo_exporter.zip")
    L("python3 scripts/build_echo_spine.py --zip /tmp/claude-0/echo_raw/echo_exporter.zip --as-of %s" % as_of.isoformat())
    L("```")
    L("")
    with open(os.path.join(a.out_dir, "REPORT.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
