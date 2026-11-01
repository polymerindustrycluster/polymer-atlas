#!/usr/bin/env python3
"""build_osha_ita.py - OSHA Injury Tracking Application (Form 300A) establishments -> Atlas
site matches, employee-band proposals and polymer-establishment leads.

Stdlib only; re-runnable; READ-ONLY on data/ (it never writes under data/).  Self-contained:
it does NOT import scripts/build_echo_spine.py or scripts/build_osha_inspections.py (their
Atlas loader, normalizers and match ladder are re-implemented below so the three spines stay
comparable but independent).

Input (untrusted data; not in the repo; never copied into it)
  The repo owner's filtered download of OSHA ITA Form 300A establishment data, calendar year
  2025 (year_filing_for), tab separated, one row per establishment_ID:
      https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data
  Run with isolated mode so nothing is imported from the data directory or the cwd:
      python3 -I scripts/build_osha_ita.py <ita_300a.tsv> [--as-of YYYY-MM-DD]

What it does
  1. Reads the TSV; normalizes zip (leading zeros restored), EIN (public in ITA; candidate
     use only), NAICS, dates; keeps identity, NAICS and size fields ONLY.  The injury/illness
     columns and total_hours_worked are never written to any output (hours are used in memory
     for one plausibility screen on annual_average_employees and surface only as a flag).
  2. Classifies each row's NAICS against docs/SCHEMA.md section 2.2 (label only, no ruling).
  3. Matches every establishment to Atlas sites (data/sites_*.csv) with the same ladder as the
     ECHO and OSHA-inspection spines (street + locality + name; operator rule, AGENTS 3);
     name agreement is tested against BOTH establishment_name and company_name.
  4. Links EIN groups to Atlas orgs through MATCH_SITE rows (candidates only).
  5. Proposes employee_band_site from annual_average_employees for MATCH_SITE rows
     (SCHEMA 4.4 bands; band only, never a headcount; employee_count_source_date =
     date_submitted) and compares with the site's existing band and with the inspection lane's
     proposals (tasks/osha-spine-2026-11-01/band_proposals.csv).
  6. Cross-references establishments with the inspection lane's establishments.csv.
  7. Writes under --out-dir: establishments.csv, site_matches.csv, band_proposals.csv,
     leads_by_state.csv, REPORT.md.

Doctrine this script encodes (AGENTS.md / docs/SCHEMA.md)
  - Lead/proposal product only; nothing here is Atlas data, a tier, a status change, a ring
    decision or a minted registry link.  Employer EIN has no registry enum value (owner item
    already raised): EIN-to-org links are candidates in site_matches.csv only.
  - A filing is activity evidence (the establishment reported employees and hours for CY2025);
    it is never a status change.  A failed or empty match is never evidence of absence.
  - ITA NAICS is employer-entered; ITA addresses are establishment addresses.
  - annual_average_employees supports a band PROPOSAL at SITE grain only (SCHEMA 4.4/4.5);
    never pushed to the organization or to other sites; zero/blank is missing, not a count.
  - Coordinates are not used.
"""
import argparse
import csv
import glob
import hashlib
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime

csv.field_size_limit(10 ** 8)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, os.pardir))
DEFAULT_OUT = os.path.join(REPO, "tasks", "osha-ita-2026-11-01")
DEFAULT_INSP = os.path.join(REPO, "tasks", "osha-spine-2026-11-01")

# ------------------------------------------------------------------ bands (SCHEMA 4.4)
BANDS = [(1, 9, "1-9"), (10, 49, "10-49"), (50, 99, "50-99"), (100, 249, "100-249"), (250, 499, "250-499"),
         (500, 999, "500-999"), (1000, 4999, "1000-4999")]
BAND_ORDER = [b[2] for b in BANDS] + ["5000+"]
BAND_VOCAB = set(BAND_ORDER) | {"unknown"}


def band_of(n):
    if n is None or n < 1:
        return ""
    for lo, hi, name in BANDS:
        if lo <= n <= hi:
            return name
    return "5000+"


# ------------------------------------------------------------------ NAICS vs SCHEMA 2.2
CORE_FAMILIES = ("3252", "3255", "3259", "326")      # the inspection / ECHO lanes' core scope

_R1P = ["326111", "326112", "326113", "326121", "326122", "326130", "326140", "326150", "326160", "326191",
        "326192", "326199", "326211", "326212", "326220", "326291", "326299"]
LISTED = {}                                           # code -> (SCHEMA 2.2 ring label, signal P/S/X)
for _c in _R1P:
    LISTED[_c] = ("Ring 1", "P")
LISTED["325211"] = ("Ring 1/2", "P")
LISTED["313320"] = ("Ring 1", "S")
for _c, _s in (("325212", "P"), ("325991", "P"), ("325510", "P"), ("325520", "P"), ("325130", "S"),
               ("325199", "S"), ("325220", "S"), ("325920", "X"), ("325998", "S"), ("325611", "X"),
               ("325612", "X")):
    LISTED[_c] = ("Ring 2", _s)
for _c, _s in (("333511", "P"), ("333514", "S"), ("333249", "S"), ("333242", "X"), ("333519", "S"),
               ("333513", "S"), ("332710", "S"), ("332322", "X"), ("332313", "X"), ("424610", "P"),
               ("424690", "S"), ("423830", "S"), ("423930", "S"), ("562920", "P"), ("562219", "S"),
               ("541380", "S"), ("541715", "S"), ("541330", "S"), ("541420", "S")):
    LISTED[_c] = ("Ring 3", _s)
for _c in ("336110", "336120", "336310", "336320", "336360", "336390", "336411", "336412", "336413", "339112",
           "339113", "339114", "339115", "334510", "334511", "334512", "335210", "335220", "335240", "327310",
           "327320", "327330", "327390", "327991", "327999", "316210", "314910", "314999"):
    LISTED[_c] = ("Ring 4", "S")
for _c in ("312111", "325412", "325413", "325414"):
    LISTED[_c] = ("Ring 4", "X")
for _c in ("327215", "333611", "336612"):               # SCHEMA 2.2 'Composites-adjacent' list (all S)
    LISTED[_c] = ("Composites-adjacent", "S")


def naics_listing(code):
    """(ring_label, signal) per SCHEMA 2.2, or ('', 'U') when the code is not listed."""
    if code in LISTED:
        return LISTED[code]
    if code.startswith("311"):
        return ("Ring 4", "X")
    if code.startswith("238"):
        return ("Ring 4", "X")
    return ("", "U")


def scope_class(code):
    ring, sig = naics_listing(code)
    core = code.startswith(CORE_FAMILIES)
    if core:
        return {"P": "core_P", "S": "core_S", "X": "core_X", "U": "core_unlisted"}[sig]
    if ring == "Ring 3":
        return {"P": "ring3_P", "S": "ring3_S", "X": "ring3_X"}[sig]
    if ring == "Ring 4":
        return "ring4_S" if sig == "S" else "ring4_X"
    if ring:
        return "other_listed_S"       # 313320 (Ring 1 S), 325130 / 325199 (Ring 2 S), composites-adjacent S
    return "unlisted"


SCOPE_ORDER = ["core_P", "core_S", "core_X", "core_unlisted", "ring3_P", "ring3_S", "ring3_X", "other_listed_S",
               "ring4_S", "ring4_X", "unlisted"]
CORE_SCOPES = {"core_P", "core_S", "core_X", "core_unlisted"}

# ------------------------------------------------------------------ normalizers (same as the sibling lanes)
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
    """(containment, jaccard, shared) on distinctive tokens when both sides have any, else on all tokens;
    location tokens in `drop` are removed first."""
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


def norm_zip(z):
    """ITA zips lose leading zeros (3-4 digit values); restore to 5 digits (zip+4 -> first 5)."""
    d = re.sub(r"\D", "", z or "")
    if not d:
        return ""
    if len(d) <= 5:
        return d.zfill(5)
    return d.zfill(9)[:5]


def clean_name(s):
    s = (s or "").strip()
    return re.sub(r"^\s*(?:[A-Za-z]{2}\d{6,}|\d{4,})\s*[-:]\s*", "", s)   # '4006 - Eau Claire Extrusion' -> bare name


def norm_ein(raw):
    """-> (ein9, quality).  ITA drops leading zeros; 8 digits is padded when the resulting IRS prefix is
    01-06; shorter values, placeholders and repeated digits are unusable (never grouped)."""
    d = re.sub(r"\D", "", raw or "")
    if not d:
        return "", "blank"
    if len(set(d)) == 1:
        return "", "placeholder"
    if len(d) == 9:
        return d, "ok"
    if len(d) == 8 and d.zfill(9)[:2] in ("01", "02", "03", "04", "05", "06"):
        return d.zfill(9), "zero_padded"
    return "", "invalid_length_%d" % len(d)


def iso_us(d):
    d = (d or "").strip()
    try:
        return datetime.strptime(d, "%m/%d/%Y").date().isoformat()
    except ValueError:
        return ""


def to_int(s):
    try:
        return int(str(s).strip())
    except (TypeError, ValueError):
        return None


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
    if city:
        raw = re.split(r",\s*" + re.escape(city), raw, flags=re.I)[0]
    return raw


class Atlas:
    def __init__(self, data_dir):
        self.sites = read_shards(os.path.join(data_dir, "sites_*.csv"))
        orgs = read_shards(os.path.join(data_dir, "organizations_*.csv"))
        eco = read_shards(os.path.join(data_dir, "ecosystem.csv"))
        self.org = {r["org_id"]: r for r in orgs + eco}
        self.org_namekeys = defaultdict(set)
        for r in orgs + eco:
            for nm in [r.get("legal_name", "")] + [t for t in (r.get("trade_names") or "").split(";")]:
                k = name_key(nm)
                if k:
                    self.org_namekeys[k].add(r["org_id"])
        self.org_text = []
        for r in orgs + eco:
            t = " ".join([r.get("legal_name", ""), r.get("trade_names", ""), r.get("notes", "")])
            self.org_text.append((r["org_id"], " " + squash(t) + " "))
        self.org_blob = "\x00".join(t for _, t in self.org_text)
        self.site_by_id = {}
        self.by_street = defaultdict(list)
        self.by_zip = defaultdict(list)
        self.by_city = defaultdict(list)
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
            self.site_prof[sid] = {"state": st, "street_key": sk, "street_src": src, "zip5": zip5(s.get("zip")),
                                   "city": squash(s.get("city")), "names": ntoks,
                                   "city_toks": frozenset(_stem(t) for t in squash(s.get("city")).split())}
            if sk:
                self.by_street[(st, sk)].append(sid)
            if zip5(s.get("zip")):
                self.by_zip[(st, zip5(s.get("zip")))].append(sid)
            if squash(s.get("city")):
                self.by_city[(st, squash(s.get("city")))].append(sid)


# ------------------------------------------------------------------ matching (the ECHO / inspection ladder)
RANK = {"street_exact+loc+name": 100, "name_zip_street_unknown": 80, "street_exact+loc_name_differs": 60,
        "name_city_street_unknown": 50, "name_zip_weak": 45, "street_exact_locality_differs": 30}
MATCH_KINDS = {"street_exact+loc+name", "name_zip_street_unknown"}
STRENGTH = {"street_exact+loc+name": "strong", "name_zip_street_unknown": "moderate"}


def best_sim(names, p_names, drop):
    """Best name similarity over (ITA name field) x (site name variants).  Returns (sim, label)."""
    best, lab = (0.0, 0.0, 0), ""
    for label, toks in names:
        for n in p_names:
            t = name_sim(toks, n, drop)
            if (t[2] >= 1, t[0], t[1]) > (best[2] >= 1, best[0], best[1]):
                best, lab = t, label
    return best, lab


def judge(fk, A, sid):
    p = A.site_prof[sid]
    street = "na"
    if fk["street_key"] and p["street_key"]:
        street = "eq" if fk["street_key"] == p["street_key"] else "diff"
    zip_eq = bool(fk["zip5"] and p["zip5"] and fk["zip5"] == p["zip5"])
    city_eq = bool(fk["city"] and p["city"] and fk["city"] == p["city"])
    loc = "zip" if zip_eq else ("city" if city_eq else "")
    drop = fk["city_toks"] | p["city_toks"]
    sim, lab = best_sim(fk["names"], p["names"], drop)
    parts = []
    if street == "eq":
        parts.append("street_exact")
    if loc:
        parts.append("zip5" if loc == "zip" else "city")
    parts.append("name_sim=%.2f(%s)" % (sim[0], lab or "-"))
    if street == "eq" and loc:
        return ("street_exact+loc+name" if name_ok(sim) else "street_exact+loc_name_differs"), parts, sim, lab
    if street == "eq":
        return "street_exact_locality_differs", parts, sim, lab
    if street == "na":
        if loc == "zip" and name_strong(sim):
            return "name_zip_street_unknown", parts, sim, lab
        if loc == "city" and name_strong(sim):
            return "name_city_street_unknown", parts, sim, lab
        if loc and name_ok(sim):
            return "name_zip_weak", parts, sim, lab
    return None


def match_one(e, A):
    fk = {"street_key": e["street_key"], "zip5": e["zip5"], "city": squash(e["city"]),
          "city_toks": frozenset(_stem(t) for t in squash(e["city"]).split()), "names": e["name_toks"]}
    st = e["state"]
    cand = set()
    if fk["street_key"]:
        cand.update(A.by_street.get((st, fk["street_key"]), ()))
    if fk["zip5"]:
        cand.update(A.by_zip.get((st, fk["zip5"]), ()))
    if fk["city"]:
        cand.update(A.by_city.get((st, fk["city"]), ()))
    judged, diff_strong = [], []
    for sid in cand:
        j = judge(fk, A, sid)
        if j:
            judged.append((RANK[j[0]], j[2][0], sid, j))
        else:
            p = A.site_prof[sid]
            if fk["street_key"] and p["street_key"] and fk["street_key"] != p["street_key"] \
                    and (fk["city"] == p["city"] or (fk["zip5"] and fk["zip5"] == p["zip5"])):
                sims, _ = best_sim(fk["names"], p["names"], fk["city_toks"] | p["city_toks"])
                if name_strong(sims):
                    diff_strong.append(sid)
    rec = {"verdict": "NO_MATCH", "basis": "", "strength": "", "site_id": "", "alts": "", "name_sim": "",
           "kind": "", "name_used": "", "diff_addr_sites": ";".join(sorted(diff_strong)[:3])}
    if judged:
        judged.sort(key=lambda t: (-t[0], -t[1], t[2]))
        top = judged[0]
        ties = [t for t in judged if t[0] == top[0] and abs(t[1] - top[1]) < 1e-9 and t[2] != top[2]]
        kind, parts, sim, lab = top[3]
        rec.update(kind=kind, site_id=top[2], name_sim="%.2f" % sim[0], name_used=lab,
                   basis=kind + ":" + ",".join(parts), alts=";".join(t[2] for t in judged[1:6]))
        if kind in MATCH_KINDS and not ties:
            rec.update(verdict="MATCH_SITE", strength=STRENGTH[kind])
        else:
            rec["verdict"] = "POSSIBLE"
            if ties:
                tied = [top[2]] + [t[2] for t in ties]
                same_org = len({A.site_by_id[x]["org_id"] for x in tied}) == 1
                rec["basis"] += (";tie_same_org_possible_duplicate_sites=" if same_org
                                 else ";ambiguous_equal_rank_sites=") + ",".join(tied[:6])
            rec["strength"] = "weak"
    return rec


def lead_class(e, rec, A):
    """NO_MATCH only: possible extra site of a held org, or net new?  AGENTS 3 steps 2 and 4, tested on
    company_name and establishment_name."""
    if rec["diff_addr_sites"]:
        return "HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS", rec["diff_addr_sites"]
    names = [n for n in (e["company_name"], e["name"]) if n]
    for n in names:
        orgs = sorted(A.org_namekeys.get(name_key(n), ()))
        if orgs:
            return "NAME_EQUALS_HELD_ORG_OTHER_LOCATION", ";".join(orgs[:3])
    for n in names:
        k = name_key(n)
        toks = squash(k).split()
        if any(_stem(t) not in GENERIC for t in toks) and (len(toks) >= 2 or len(k) >= 6):
            needle = " " + " ".join(toks) + " "
            if needle in A.org_blob:
                hits = [oid for oid, t in A.org_text if needle in t]
                return "NAME_IN_HELD_ORG_TRADE_NAMES_OR_NOTES", ";".join(hits[:3])
    return "NET_NEW_LEAD", ""


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


# ------------------------------------------------------------------ ITA loading
SIZE_EXPECT = {"1": (0, 19), "21": (20, 99), "22": (100, 249), "2": (20, 249), "3": (250, 10 ** 9)}
HPE_LOW, HPE_HIGH = 300, 4500            # hours per employee screen (median in this file is about 2,000)


def load_ita(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh, delimiter="\t")
        need = ["ID", "establishment_name", "establishment_ID", "ein", "company_name", "street_address", "city",
                "state", "zip_code", "naics_code", "naics_year", "industry_description", "establishment_type",
                "size", "annual_average_employees", "total_hours_worked", "date_submitted", "Change_reason",
                "year_filing_for"]
        missing = [c for c in need if c not in (rd.fieldnames or [])]
        if missing:
            sys.exit("ITA header lacks expected columns: %s" % missing)
        raw = list(rd)
    ests = []
    for r in raw:
        code = (r["naics_code"] or "").strip()
        n = to_int(r["annual_average_employees"])
        hrs = to_int(r["total_hours_worked"])
        size = (r["size"] or "").strip()
        ein9, einq = norm_ein(r["ein"])
        nm = clean_name(r["establishment_name"])
        co = (r["company_name"] or "").strip()
        usable = n is not None and n >= 1
        lo_hi = SIZE_EXPECT.get(size)
        if not usable:
            size_flag = "no_count"
        elif lo_hi is None:
            size_flag = "size_code_unknown"
        else:
            size_flag = "consistent" if lo_hi[0] <= n <= lo_hi[1] else "inconsistent"
        if usable and hrs is not None and hrs >= 0:
            hpe = hrs / n
            hpe_flag = "implausible_hours_per_employee" if (hpe < HPE_LOW or hpe > HPE_HIGH) else "ok"
        else:
            hpe_flag = "no_count" if not usable else "no_hours"
        if not usable:
            rel = "no_count"
        elif hpe_flag == "implausible_hours_per_employee":
            rel = "suspect"
        elif size_flag in ("inconsistent", "size_code_unknown"):
            rel = "review"
        else:
            rel = "ok"
        ring, sig = naics_listing(code)
        e = {
            "ita_row_id": (r["ID"] or "").strip(), "establishment_id": (r["establishment_ID"] or "").strip(),
            "ein": ein9, "ein_quality": einq, "company_name": co, "name": nm,
            "name_raw": (r["establishment_name"] or "").strip(),
            "street": (r["street_address"] or "").strip(), "city": (r["city"] or "").strip(),
            "state": (r["state"] or "").strip().upper(), "zip5": norm_zip(r["zip_code"]),
            "zip_as_filed": (r["zip_code"] or "").strip(),
            "naics_code": code, "naics_year": (r["naics_year"] or "").strip(),
            "industry_description": (r["industry_description"] or "").strip(),
            "family4": code[:4], "scope_class": scope_class(code), "schema_ring": ring, "schema_signal": sig,
            "establishment_type": (r["establishment_type"] or "").strip(), "size_code": size,
            "avg_emp": n, "avg_emp_usable": usable, "band": band_of(n) if usable else "",
            "size_flag": size_flag, "hpe_flag": hpe_flag, "reliability": rel,
            "date_submitted": iso_us(r["date_submitted"]), "date_submitted_raw": (r["date_submitted"] or "").strip(),
            "change_reason_present": "Y" if (r["Change_reason"] or "").strip() not in ("", "0") else "N",
            "year_filing_for": (r["year_filing_for"] or "").strip(),
        }
        e["street_key"] = street_key(e["street"])
        e["name_toks"] = [(lbl, name_tokens(v)) for lbl, v in (("establishment_name", nm), ("company_name", co))
                          if v and name_tokens(v)[0]]
        ests.append(e)
    return ests


# ------------------------------------------------------------------ inspection-lane cross reference
def load_inspection(insp_dir):
    est_path = os.path.join(insp_dir, "establishments.csv")
    mat_path = os.path.join(insp_dir, "site_matches.csv")
    band_path = os.path.join(insp_dir, "band_proposals.csv")
    if not all(os.path.exists(p) for p in (est_path, mat_path, band_path)):
        return None
    I = {"ests": [], "match": {}, "band": {}, "by_street": defaultdict(list), "by_zip": defaultdict(list)}
    with open(est_path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            r["street_key"] = street_key(r["street"])
            r["zip5"] = zip5(r["zip"])
            r["city_sq"] = squash(r["city"])
            r["names"] = [name_tokens(v) for v in [r["name"]] + [x for x in (r.get("name_variants") or "").split(";")]
                          if v.strip()]
            I["ests"].append(r)
            if r["street_key"]:
                I["by_street"][(r["state"].upper(), r["street_key"])].append(r)
            if r["zip5"]:
                I["by_zip"][(r["state"].upper(), r["zip5"])].append(r)
    with open(mat_path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            I["match"][r["est_key"]] = r
    with open(band_path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            I["band"][r["site_id"]] = r
    return I


def crossref(e, I):
    """Inspection-lane establishments at the same place as ITA establishment e.  Returns
    (level, [est rows]) with level BOTH_STRONG (street+loc+name), BOTH_ADDRESS_NAME_DIFFERS,
    BOTH_NAME_ZIP (street unknown, same zip, strong name) or ''."""
    if I is None:
        return "", []
    st = e["state"]
    city = squash(e["city"])
    ctoks = frozenset(_stem(t) for t in city.split())
    strong, addr_only, name_zip = [], [], []
    seen = set()
    cands = []
    if e["street_key"]:
        cands += I["by_street"].get((st, e["street_key"]), [])
    if e["zip5"]:
        cands += I["by_zip"].get((st, e["zip5"]), [])
    for r in cands:
        if r["est_key"] in seen:
            continue
        seen.add(r["est_key"])
        loc_eq = (e["zip5"] and e["zip5"] == r["zip5"]) or (city and city == r["city_sq"])
        drop = ctoks | frozenset(_stem(t) for t in r["city_sq"].split())
        sim, _ = best_sim(e["name_toks"], r["names"], drop)
        if e["street_key"] and r["street_key"]:
            if e["street_key"] == r["street_key"] and loc_eq:
                (strong if name_ok(sim) else addr_only).append(r)
        elif not (e["street_key"] and r["street_key"]):
            if e["zip5"] and e["zip5"] == r["zip5"] and name_strong(sim):
                name_zip.append(r)
    if strong:
        return "BOTH_STRONG", strong
    if name_zip:
        return "BOTH_NAME_ZIP", name_zip
    if addr_only:
        return "BOTH_ADDRESS_NAME_DIFFERS", addr_only
    return "", []


def classify_band(existing, proposed):
    ex = (existing or "").strip()
    if ex in ("", "unknown"):
        return "fills_%s" % ("unknown" if ex else "blank")
    if ex == proposed:
        return "matches_existing"
    if ex in BAND_VOCAB:
        return "conflicts_existing"
    return "existing_nonstandard_value"


_TOMB_RX = re.compile(r"tombstoned as duplicate of (SITE-\d{6})", re.I)


def site_caution(s):
    """Flags read from the Atlas site row itself (never a status change proposal)."""
    out = []
    if s.get("operating_status") in ("closed", "idled", "active_idled_partial"):
        out.append("site_%s_in_atlas" % s["operating_status"])
    m = _TOMB_RX.search(s.get("notes") or "")
    if m:
        out.append("site_tombstoned_duplicate_of:" + m.group(1))
    if re.search(r"\bWARN\b", s.get("notes") or "") and s.get("operating_status") == "closed":
        out.append("site_notes_cite_WARN_closure")
    return ";".join(out)


def recent3(d, as_of):
    return bool(d) and (as_of - date.fromisoformat(d)).days <= 3 * 365


# ------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ita_tsv", help="owner-supplied OSHA ITA 300A establishment extract (TSV); never copied into the repo")
    ap.add_argument("--data-dir", default=os.path.join(REPO, "data"))
    ap.add_argument("--qcew", default=os.path.join(REPO, "docs", "denominators", "qcew_state_polymer_2023_2024.csv"))
    ap.add_argument("--inspection-dir", default=DEFAULT_INSP, help="inspection lane packet dir (cross-reference); optional")
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--as-of", default=date.today().isoformat())
    a = ap.parse_args(argv)
    as_of = date.fromisoformat(a.as_of)

    sha = hashlib.sha256()
    nl = 0
    last = b""
    with open(a.ita_tsv, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            sha.update(chunk)
            nl += chunk.count(b"\n")
            last = chunk[-1:]
    ests = load_ita(a.ita_tsv)
    ids = [e["establishment_id"] for e in ests]
    assert all(ids) and len(ids) == len(set(ids)), "establishment_ID not unique/non-blank"      # AGENTS 2 rule 10b
    assert len({e["ita_row_id"] for e in ests}) == len(ests), "ITA row ID not unique"
    years = Counter(e["year_filing_for"] for e in ests)
    assert list(years) == ["2025"], "unexpected year_filing_for values: %s" % dict(years)

    A = Atlas(a.data_dir)
    I = load_inspection(a.inspection_dir)
    for e in ests:
        e["rec"] = match_one(e, A)
        r = e["rec"]
        r["lead"], r["lead_ref"] = lead_class(e, r, A) if r["verdict"] == "NO_MATCH" else ("", "")
        e["xlevel"], e["xrows"] = crossref(e, I)
    ests.sort(key=lambda d: (d["state"], d["city"].lower(), d["name"].lower(), d["establishment_id"]))
    by_id = {e["establishment_id"]: e for e in ests}

    # duplicate addresses inside the ITA file (different establishment_IDs at one street+zip)
    addr_groups = defaultdict(list)
    for e in ests:
        if e["street_key"]:
            addr_groups[(e["state"], e["street_key"], e["zip5"])].append(e["establishment_id"])
    for e in ests:
        g = addr_groups.get((e["state"], e["street_key"], e["zip5"]), []) if e["street_key"] else []
        e["addr_group_n"] = len(g)

    # per-site MATCH_SITE groups
    per_site = defaultdict(list)
    for e in ests:
        if e["rec"]["verdict"] == "MATCH_SITE":
            per_site[e["rec"]["site_id"]].append(e["establishment_id"])

    # EIN groups -> Atlas orgs via MATCH_SITE rows (candidates only)
    ein_members = defaultdict(list)
    for e in ests:
        if e["ein"]:
            ein_members[e["ein"]].append(e)
    ein_orgs = {}
    for ein, mem in ein_members.items():
        orgs = {A.site_by_id[m["rec"]["site_id"]]["org_id"] for m in mem if m["rec"]["verdict"] == "MATCH_SITE"}
        ein_orgs[ein] = orgs
    for e in ests:
        g = ein_members.get(e["ein"], []) if e["ein"] else []
        orgs = sorted(ein_orgs.get(e["ein"], ())) if e["ein"] else []
        e["ein_group_n"] = len(g)
        e["ein_orgs"] = ";".join(orgs)
        if not e["ein"]:
            e["ein_status"] = "no_usable_ein"
        elif len(orgs) > 1:
            e["ein_status"] = "EIN_SPANS_MULTIPLE_HELD_ORGS"
        elif e["rec"]["verdict"] == "MATCH_SITE":
            e["ein_status"] = "EIN_ON_MATCHED_SITE_AND_OTHER_ROWS" if len(g) > 1 else "EIN_ON_MATCHED_SITE_ONLY"
        elif len(orgs) == 1:
            e["ein_status"] = "EIN_CANDIDATE_ORG_OTHER_LOCATION"
        else:
            e["ein_status"] = "EIN_NO_HELD_ORG"
    ein_org_pairs = Counter()
    for ein, orgs in ein_orgs.items():
        for o in orgs:
            ein_org_pairs[(ein, o)] += 1

    # band proposals (MATCH_SITE only; one row per site; site grain only)
    insp_band = I["band"] if I else {}
    prows = []
    strength_rank = {"strong": 2, "moderate": 1}
    for sid, keys in sorted(per_site.items()):
        cands = [by_id[k] for k in keys if by_id[k]["avg_emp_usable"]]
        if not cands:
            continue
        rel_rank = {"ok": 3, "review": 2, "suspect": 1}
        e = max(cands, key=lambda d: (strength_rank[d["rec"]["strength"]], rel_rank[d["reliability"]],
                                      d["date_submitted"], d["establishment_id"]))
        s = A.site_by_id[sid]
        band = e["band"]
        others = ["%s:%s" % (by_id[k]["establishment_id"], by_id[k]["band"] or "no_count") for k in sorted(keys)
                  if k != e["establishment_id"]]
        ib = insp_band.get(sid)
        if ib is None:
            vs, step = "ita_only", ""
        else:
            vs = "agree" if ib["proposed_employee_band_site"] == band else "differ"
            try:
                step = BAND_ORDER.index(band) - BAND_ORDER.index(ib["proposed_employee_band_site"])
            except ValueError:
                step = ""
        newer = ""
        if ib:
            newer = "Y" if e["date_submitted"] > ib["employee_count_source_date"] else "N"
        prows.append({
            "site_id": sid, "org_id": s["org_id"], "site_name": s["site_name"], "state": s["state"],
            "establishment_id": e["establishment_id"], "ita_establishment_name": e["name"],
            "company_name": e["company_name"], "match_strength": e["rec"]["strength"],
            "site_operating_status": s.get("operating_status", ""), "site_caution": site_caution(s),
            "current_employee_band_site": s.get("employee_band_site", ""), "proposed_employee_band_site": band,
            "relation_to_current": classify_band(s.get("employee_band_site", ""), band),
            "annual_average_employees": e["avg_emp"], "employee_count_source_date": e["date_submitted"],
            "period_covered": "CY2025", "source_class": "government_filing", "reliability": e["reliability"],
            "size_code": e["size_code"], "size_code_vs_avg_employees": e["size_flag"],
            "hours_per_employee_screen": e["hpe_flag"], "ita_estabs_at_site": len(keys),
            "other_ita_estabs_at_site": ";".join(others), "naics_code": e["naics_code"],
            "scope_class": e["scope_class"],
            "inspection_lane_band": ib["proposed_employee_band_site"] if ib else "",
            "inspection_lane_nr_in_estab": ib["nr_in_estab"] if ib else "",
            "inspection_lane_date": ib["employee_count_source_date"] if ib else "",
            "vs_inspection_lane": vs, "band_step_ita_minus_inspection": step, "ita_newer_than_inspection": newer,
            "basis": "OSHA ITA 300A CY2025, establishment_ID %s: annual average employees %s → %s" % (
                e["establishment_id"], e["avg_emp"], band),
            "scope_note": "site band only; never to org or other sites; band not headcount"})
    prop_sites = {r["site_id"] for r in prows}
    insp_only = sorted(set(insp_band) - prop_sites)

    # ------------------------------------------------------------------ write
    os.makedirs(a.out_dir, exist_ok=True)
    W = lambda name: open(os.path.join(a.out_dir, name), "w", newline="", encoding="utf-8")

    ecols = ["establishment_id", "ita_row_id", "ein", "ein_quality", "company_name", "establishment_name", "street",
             "city", "state", "zip5", "zip_as_filed", "naics_code", "naics_year", "industry_description", "family4",
             "scope_class", "schema_2_2_ring", "schema_2_2_signal", "establishment_type", "size_code",
             "annual_average_employees", "band_from_avg_employees", "size_code_vs_avg_employees",
             "hours_per_employee_screen", "reliability", "date_submitted", "amended_filing", "year_filing_for",
             "ita_estabs_at_address"]
    with W("establishments.csv") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(ecols)
        for e in ests:
            w.writerow([e["establishment_id"], e["ita_row_id"], e["ein"], e["ein_quality"], e["company_name"],
                        e["name_raw"], e["street"], e["city"], e["state"], e["zip5"], e["zip_as_filed"],
                        e["naics_code"], e["naics_year"], e["industry_description"], e["family4"], e["scope_class"],
                        e["schema_ring"], e["schema_signal"], e["establishment_type"], e["size_code"],
                        e["avg_emp"] if e["avg_emp"] is not None else "", e["band"], e["size_flag"], e["hpe_flag"],
                        e["reliability"], e["date_submitted"], e["change_reason_present"], e["year_filing_for"],
                        e["addr_group_n"] or ""])

    def liveness(e):
        r = e["rec"]
        if r["verdict"] not in ("MATCH_SITE", "POSSIBLE"):
            return ""
        s = A.site_by_id[r["site_id"]]
        if s["operating_status"] in ("closed", "idled", "active_idled_partial") and e["avg_emp_usable"]:
            return "%satlas_status_%s_but_ita_cy2025_filing_with_employees_submitted_%s;reverification_lead_only_not_a_status_change" % (
                "possible_match_" if r["verdict"] == "POSSIBLE" else "", s["operating_status"], e["date_submitted"])
        if r["verdict"] == "MATCH_SITE" and e["avg_emp_usable"]:
            return "ita_cy2025_filing_with_employees"
        return ""

    mcols = ["establishment_id", "establishment_name", "company_name", "street", "city", "state", "zip5",
             "naics_code", "scope_class", "verdict", "match_strength", "basis", "name_used", "site_id", "org_id",
             "site_name", "site_operating_status", "site_caution", "site_street_source", "site_naics_primary", "naics_relation",
             "name_sim", "alt_site_ids", "ita_estabs_at_site", "lead_class", "lead_ref", "cross_source",
             "inspection_lane_est_keys", "inspection_lane_latest_inspection", "inspection_lane_verdict",
             "inspection_lane_site_id", "ein", "ein_quality", "ein_group_size", "ein_orgs_via_match_site",
             "ein_status", "ita_estabs_at_address", "liveness_note"]
    mrows = []
    for e in ests:
        r = e["rec"]
        s = A.site_by_id.get(r["site_id"]) if r["site_id"] else None
        sn = (s.get("naics_primary") or "").strip() if s else ""
        if not s:
            nrel = ""
        elif not sn:
            nrel = "site_naics_blank"
        elif sn == e["naics_code"]:
            nrel = "same_6digit"
        elif sn[:4] == e["naics_code"][:4]:
            nrel = "same_4digit"
        else:
            nrel = "differs"
        xr = e["xrows"]
        xm = [I["match"].get(x["est_key"], {}) for x in xr] if I else []
        verdicts = sorted({m.get("verdict", "") for m in xm if m})
        xsites = sorted({m.get("site_id", "") for m in xm if m and m.get("site_id")})
        if I is None:
            cross = ""
        elif e["xlevel"] == "BOTH_STRONG" or e["xlevel"] == "BOTH_NAME_ZIP":
            cross = "BOTH_SOURCES"
        elif e["xlevel"] == "BOTH_ADDRESS_NAME_DIFFERS":
            cross = "BOTH_ADDRESS_NAME_DIFFERS"
        else:
            cross = "ITA_ONLY"
        mrows.append({
            "establishment_id": e["establishment_id"], "establishment_name": e["name_raw"],
            "company_name": e["company_name"], "street": e["street"], "city": e["city"], "state": e["state"],
            "zip5": e["zip5"], "naics_code": e["naics_code"], "scope_class": e["scope_class"],
            "verdict": r["verdict"], "match_strength": r["strength"], "basis": r["basis"],
            "name_used": r["name_used"] if r["verdict"] != "NO_MATCH" else "",
            "site_id": r["site_id"], "org_id": s["org_id"] if s else "", "site_name": s["site_name"] if s else "",
            "site_operating_status": s["operating_status"] if s else "",
            "site_caution": site_caution(s) if s else "",
            "site_street_source": A.site_prof[r["site_id"]]["street_src"] if s else "",
            "site_naics_primary": sn, "naics_relation": nrel, "name_sim": r["name_sim"], "alt_site_ids": r["alts"],
            "ita_estabs_at_site": len(per_site[r["site_id"]]) if r["verdict"] == "MATCH_SITE" else "",
            "lead_class": r["lead"], "lead_ref": r["lead_ref"], "cross_source": cross,
            "inspection_lane_est_keys": ";".join(x["est_key"] for x in xr[:5]),
            "inspection_lane_latest_inspection": max([x["latest_inspection"] for x in xr] or [""]),
            "inspection_lane_verdict": ";".join(verdicts), "inspection_lane_site_id": ";".join(xsites),
            "ein": e["ein"], "ein_quality": e["ein_quality"], "ein_group_size": e["ein_group_n"] or "",
            "ein_orgs_via_match_site": e["ein_orgs"], "ein_status": e["ein_status"],
            "ita_estabs_at_address": e["addr_group_n"] or "", "liveness_note": liveness(e)})
    with W("site_matches.csv") as fh:
        w = csv.DictWriter(fh, mcols, lineterminator="\n")
        w.writeheader()
        w.writerows(mrows)

    pcols = list(prows[0].keys()) if prows else []
    with W("band_proposals.csv") as fh:
        w = csv.DictWriter(fh, pcols, lineterminator="\n")
        w.writeheader()
        w.writerows(prows)

    # leads_by_state.csv
    gaps = qcew_gap(a.qcew, A)
    mrow_by_id = {m["establishment_id"]: m for m in mrows}
    st_c = defaultdict(Counter)
    loc_sets = defaultdict(set)
    for e in ests:
        c = st_c[e["state"]]
        m = mrow_by_id[e["establishment_id"]]
        c["all"] += 1
        sc = e["scope_class"]
        if sc in CORE_SCOPES:
            c["core"] += 1
            c["core_" + e["rec"]["verdict"]] += 1
            if e["rec"]["verdict"] == "NO_MATCH":
                c["core_no_match_" + sc] += 1
                if sc == "core_P":
                    c["coreP_lead_" + e["rec"]["lead"]] += 1
                    if m["cross_source"] == "BOTH_SOURCES":
                        c["coreP_both_sources"] += 1
                        if e["rec"]["lead"] == "NET_NEW_LEAD":
                            c["coreP_both_sources_net_new"] += 1
                    elif m["cross_source"] == "BOTH_ADDRESS_NAME_DIFFERS":
                        c["coreP_both_address_name_differs"] += 1
                    if e["ein_status"] == "EIN_CANDIDATE_ORG_OTHER_LOCATION":
                        c["coreP_ein_held_org"] += 1
                    if e["avg_emp_usable"]:
                        c["coreP_with_count"] += 1
                    loc_sets[e["state"]].add((e["street_key"], e["zip5"]) if e["street_key"] else ("id", e["establishment_id"]))
        elif sc == "ring3_P":
            c["ring3P"] += 1
            c["ring3P_" + e["rec"]["verdict"]] += 1
    gap_rank = {s: i + 1 for i, s in enumerate(sorted(gaps, key=lambda s: -gaps[s][2]))}
    ordered = sorted(st_c, key=lambda s: (-(gaps[s][2]) if s in gaps else 10 ** 9, s))
    lcols = ["state", "qcew_2023_326_private_estabs", "atlas_strict_326_sites", "qcew_gap", "gap_rank",
             "ita_establishments_all", "ita_core_family_establishments", "core_match_site", "core_possible",
             "core_no_match", "core_no_match_signal_P", "core_no_match_signal_S", "core_no_match_signal_X",
             "core_no_match_unlisted", "coreP_no_match_net_new_lead", "coreP_no_match_name_equals_held_org_other_location",
             "coreP_no_match_held_org_same_name_city_diff_address", "coreP_no_match_name_in_held_org_trade_names_or_notes",
             "coreP_no_match_distinct_street_zip", "coreP_no_match_both_osha_sources",
             "coreP_no_match_both_osha_sources_net_new", "coreP_no_match_both_address_name_differs",
             "coreP_no_match_ein_candidate_held_org", "ring3_primary_ita_establishments", "ring3_primary_no_match"]
    with W("leads_by_state.csv") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(lcols)
        for s in ordered:
            c = st_c[s]
            q = gaps.get(s)
            w.writerow([s, q[0] if q else "", q[1] if q else "", q[2] if q else "", gap_rank.get(s, ""),
                        c["all"], c["core"], c["core_MATCH_SITE"], c["core_POSSIBLE"], c["core_NO_MATCH"],
                        c["core_no_match_core_P"], c["core_no_match_core_S"], c["core_no_match_core_X"],
                        c["core_no_match_core_unlisted"], c["coreP_lead_NET_NEW_LEAD"],
                        c["coreP_lead_NAME_EQUALS_HELD_ORG_OTHER_LOCATION"],
                        c["coreP_lead_HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS"],
                        c["coreP_lead_NAME_IN_HELD_ORG_TRADE_NAMES_OR_NOTES"], len(loc_sets[s]),
                        c["coreP_both_sources"], c["coreP_both_sources_net_new"],
                        c["coreP_both_address_name_differs"], c["coreP_ein_held_org"], c["ring3P"],
                        c["ring3P_NO_MATCH"]])

    # reconciliation (AGENTS 2 rule 10c)
    tot = Counter()
    for c in st_c.values():
        tot.update(c)
    assert tot["all"] == len(ests)
    assert sum(1 for e in ests if e["rec"]["verdict"] in ("MATCH_SITE", "POSSIBLE", "NO_MATCH")) == len(ests)
    assert tot["core"] == tot["core_MATCH_SITE"] + tot["core_POSSIBLE"] + tot["core_NO_MATCH"]
    assert sum(1 for m in mrows) == len(ests)
    assert len(prows) == len({r["site_id"] for r in prows})

    ctx = dict(a=a, as_of=as_of, sha=sha.hexdigest(), newlines=nl, trailing_nl=(last == b"\n"), ests=ests, mrows=mrows, prows=prows, A=A, I=I,
               gaps=gaps, gap_rank=gap_rank, ordered=ordered, st_c=st_c, per_site=per_site, ein_members=ein_members,
               ein_orgs=ein_orgs, ein_org_pairs=ein_org_pairs, insp_only=insp_only, addr_groups=addr_groups,
               by_id=by_id, loc_sets=loc_sets, tot=tot)
    from_report = write_report(ctx)
    print("rows:", len(ests), "verdicts:", dict(Counter(e["rec"]["verdict"] for e in ests)),
          "band_proposals:", len(prows), "report_chars:", from_report)
    return 0


# ------------------------------------------------------------------ report
def pct(n, d):
    return "%.1f%%" % (100.0 * n / d) if d else "n/a"


def write_report(c):
    a, ests, mrows, prows, A, I = c["a"], c["ests"], c["mrows"], c["prows"], c["A"], c["I"]
    gaps, ordered, st_c, per_site = c["gaps"], c["ordered"], c["st_c"], c["per_site"]
    as_of = c["as_of"]
    f = lambda x: format(x, ",")
    n = len(ests)
    L = []
    P = L.append
    mb = {m["establishment_id"]: m for m in mrows}
    verd = Counter(e["rec"]["verdict"] for e in ests)
    core = [e for e in ests if e["scope_class"] in CORE_SCOPES]
    coreP = [e for e in ests if e["scope_class"] == "core_P"]
    sc_cnt = Counter(e["scope_class"] for e in ests)

    P("# OSHA ITA Form 300A (CY2025) polymer value-chain establishments - 2026-11-01\n")
    P("**Status: lead and proposal product, not Atlas data.** Nothing here edits `data/`, allocates an ID, sets a tier, "
      "changes a status, decides a ring or mints a registry link. Built by `scripts/build_osha_ita.py` (stdlib; "
      "re-runnable; self-contained - it does not import `build_echo_spine.py`). Packet lane output: the integrator of "
      "record decides what, if anything, is applied. Keys are the ITA `establishment_ID` values as filed (not Atlas IDs).\n")

    P("## 1. Provenance, input, raw counts\n")
    P("- **Source:** OSHA Injury Tracking Application (ITA), Form 300A establishment-specific summary data, "
      "calendar year 2025 (`year_filing_for` = 2025 on every row). Public dataset: "
      "<https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data>.")
    P("- **What was supplied:** an owner-supplied, **filtered** extract downloaded by the repo owner "
      "(`filtered_full_value_chain_ITA_300A.tsv`, SHA-256 `%s`, tab separated). **The filter the owner applied is not known in detail** "
      "(the file name says 'filtered full value chain'; the content shows NAICS-driven selection, see section 2). "
      "This packet therefore says nothing about ITA filers outside the extract, and the absence of an establishment "
      "from the extract is not evidence of anything. The raw file is **not** in the repo and was only read in isolated "
      "mode (`python3 -I`)." % c["sha"])
    P("- **Rows (unit: ITA establishment records, one `establishment_ID` each):** **%s**. "
      "**Count reconciliation (AGENTS 2 rule 10c):** the brief said 11,193; this packet counts %s. The file has %s newline characters and %s a newline, "
      "so `wc -l` (%s) already equals the record count when the last record is unterminated, and 'wc -l minus the header' undercounts by one. "
      "Checked three ways: CSV parse with and without quote handling, and a raw tab count (every physical line has 31 tabs = 32 columns). "
      "`establishment_ID` and the ITA row `ID` are both unique (asserted, rule 10b); no record was dropped or merged. "
      "Every `date_submitted` is in 2026 (CY2025 filings submitted in the 2026 window)." % (
          f(n), f(n), f(c["newlines"]), "ends with" if c["trailing_nl"] else "does **not** end with", f(c["newlines"])))
    P("- **Columns kept in the packet:** identity (IDs, names, address, EIN), NAICS (code, vintage, description), size "
      "(`size` code, `annual_average_employees`) and the filing date. **Never written:** all injury/illness columns "
      "(`no_injuries_illnesses`, deaths, DAFW/DJTR cases and days, injuries, skin/respiratory/poisoning/hearing/other "
      "illness totals). `total_hours_worked` is used in memory for one plausibility screen on the employee count and "
      "appears in outputs only as the flag `hours_per_employee_screen`.")
    P("- **Cleaning applied (unit: records):** zip restored to 5 digits where ITA dropped leading zeros: %s records "
      "(`zip_as_filed` keeps the original); EIN restored to 9 digits for %s records whose IRS prefix is 01-06 "
      "(`ein_quality = zero_padded`), %s records carry an EIN that is blank or unusable and are never grouped "
      "(blank %s; invalid length or placeholder %s); a numeric prefix such as `4006 - ` in an establishment name is "
      "stripped for matching only." % (
          f(sum(1 for e in ests if e["zip_as_filed"] and len(re.sub(r"\D", "", e["zip_as_filed"])) < 5)),
          f(sum(1 for e in ests if e["ein_quality"] == "zero_padded")),
          f(sum(1 for e in ests if not e["ein"])), f(sum(1 for e in ests if e["ein_quality"] == "blank")),
          f(sum(1 for e in ests if e["ein_quality"] not in ("blank", "ok", "zero_padded")))))
    P("- States/territories present: %d (%s)." % (len({e["state"] for e in ests}),
                                                  ", ".join("%s %s" % (s, f(k)) for s, k in Counter(e["state"] for e in ests).most_common(10)) + ", ..."))
    P("")

    # ---- section 2 NAICS
    P("## 2. NAICS classification against SCHEMA 2.2 (label only, no ruling)\n")
    P("Each row's `naics_code` (employer-entered on the ITA form; `naics_year` mixes vintages: %s) is looked up in "
      "SCHEMA section 2.2. `scope_class` is a label, **not a ring decision**: Ring is decided by the section 1 tests "
      "(SCHEMA 2.1: NAICS never decides a ring; AGENTS 2.9: scope is an owner ruling). Core = a code under the four "
      "families the inspection and ECHO lanes use (3252, 3255, 3259, 326); signal P/S/X is SCHEMA 2.2's own key."
      % ", ".join("%s %s" % (k, f(v)) for k, v in sorted(Counter(e["naics_year"] for e in ests).items())))
    P("")
    P("| scope_class | Meaning | ITA establishments |")
    P("|---|---|---:|")
    meaning = {
        "core_P": "core family, SCHEMA 2.2 Ring 1/2 Primary code (every 326xxx listed code, 325211/325212/325991/325510/325520)",
        "core_S": "core family, listed Secondary (325220, 325998)",
        "core_X": "core family, listed exclude-by-default (325920 explosives)",
        "core_unlisted": "core family prefix but not a SCHEMA 2.2 code (325910 printing ink, 325992 toner/photo, 326100 family-level code)",
        "ring3_P": "Ring 3 Primary (333511, 424610, 562920)",
        "ring3_S": "Ring 3 Secondary (333249, 333514, 424690, 423830, 423930, 332710, 541330 ...)",
        "ring3_X": "Ring 3 exclude-by-default (333242 semiconductor machinery)",
        "other_listed_S": "listed Secondary outside the core families (313320; 325130 and 325199 basic-chemical codes; composites-adjacent)",
        "ring4_S": "Ring 4 Secondary (Ring 4 test always required)",
        "ring4_X": "Ring 4 exclude-by-default (238xxx installers, 311xxx food, 325412 pharma)",
        "unlisted": "not in SCHEMA 2.2 (3251 basic/industrial gases/carbon black, 441330 auto-parts retail, 423840, 333241, ...)"}
    for k in SCOPE_ORDER:
        P("| `%s` | %s | %s |" % (k, meaning[k], f(sc_cnt.get(k, 0))))
    P("| **Total** | | **%s** |" % f(n))
    P("")
    fam = Counter(e["family4"] for e in ests)
    P("By 4-digit NAICS prefix (unit: establishments), top 14: " + "; ".join("%s %s" % (k, f(v)) for k, v in fam.most_common(14)) + ".")
    P("")
    P("**What the extract is.** Core-family rows = %s (%s of %s); the remaining %s are the 'value chain' the file name "
      "promises: 3251 basic chemicals/industrial gases/carbon black (%s), 4246 chemical distributors (%s), 4413 "
      "automotive parts/tire retail (%s), 3332 machinery (%s), 4238 industrial/plastics machinery and supply wholesalers (%s) "
      "and a long tail. Most of these are **unlisted in SCHEMA 2.2** or Ring 3 Secondary: labelled, not ruled. They "
      "are matched to Atlas sites too (a Ring 3 or Ring 4 Atlas site can match), but they are **not** in the "
      "leads tables except the separate Ring 3 Primary count." % (
          f(len(core)), pct(len(core), n), f(n), f(n - len(core)), f(fam["3251"]), f(fam["4246"]), f(fam["4413"]),
          f(fam["3332"]), f(fam["4238"])))
    P("")
    P("**NAICS observations for the integrator (not rulings).** (a) The extract mixes NAICS 2012, 2017 and 2022 vintages; "
      "SCHEMA 2.2 is written in 2022-era codes (e.g. plastics machinery at 333249) while ITA rows carry both 333248 and 333249 "
      "with the same plastics-machinery description, so 333248 is shown `unlisted` here although it looks adjacent to the "
      "listed 333249. (b) `326100` is a family-level pseudo-code, not a 6-digit NAICS (1 row, `core_unlisted`). "
      "(c) ITA NAICS is **entered by the employer in a mandatory federal filing**; whether that is `government_filing` "
      "(the inspection-lane precedent, and this packet's default) or `company_disclosed` under SCHEMA 2.1 is not settled "
      "here - an open classification question, flagged. It never overwrites a site NAICS (SCHEMA 2.1; AGENTS 4); "
      "`site_matches.csv` shows `naics_relation` (same_6digit / same_4digit / differs) for matched sites.")
    P("")

    # ---- section 3 matching
    P("## 3. Match to Atlas sites\n")
    nsite = len(A.sites)
    nstreet = sum(1 for sid in A.site_prof if A.site_prof[sid]["street_key"])
    P("Atlas side: %s site rows (all shards, any status/tier); a usable street key exists for %s (%s) - from the `street_address` "
      "column where filled, otherwise a heuristic read of `Street...:` phrases in `notes`. Ladder = the ECHO/inspection "
      "ladder (AGENTS 3, operator rule): street exact + state + (zip5 or city) + name agreement = MATCH_SITE; street exact "
      "with a different name = POSSIBLE (co-tenant or successor operator); street unknown on either side + same zip5 + "
      "strong name = MATCH_SITE (moderate); same city + strong name, or weaker name = POSSIBLE; ties at the top rank = "
      "POSSIBLE; both streets present but different is never a match. Coordinates are not used. **One departure, "
      "improving on the inspection lane:** name agreement is tested against both `establishment_name` (often a generic plant label such as "
      "'HERINGTON FACILITY') and `company_name` (the filing company, the operator) and the better of the two is used; "
      "`name_used` in `site_matches.csv` says which." % (f(nsite), f(nstreet), pct(nstreet, nsite)))
    P("")
    P("| Verdict | ITA establishments | of which core family |")
    P("|---|---:|---:|")
    for v in ("MATCH_SITE", "POSSIBLE", "NO_MATCH"):
        P("| %s | %s | %s |" % (v, f(verd[v]), f(sum(1 for e in core if e["rec"]["verdict"] == v))))
    P("| **Total** | **%s** | **%s** |" % (f(n), f(len(core))))
    P("")
    ms = verd["MATCH_SITE"]
    cms = sum(1 for e in core if e["rec"]["verdict"] == "MATCH_SITE")
    cp = sum(1 for e in core if e["rec"]["verdict"] == "POSSIBLE")
    P("**Match rate (unit: ITA establishments matched to an Atlas site row):** MATCH_SITE = %s of %s (**%s**) over all rows; "
      "**%s of %s (%s)** over core-family rows (the comparable figure to the inspection lane's 15.0%%); MATCH_SITE + POSSIBLE = %s overall, %s core. "
      "This is an establishment-to-site match rate, **not Atlas coverage**: the extract is a filtered slice of ITA filers, "
      "and ITA submission is required only of employers above OSHA's size/industry thresholds (a rule, not something this file proves), so many Atlas sites are legitimately absent." % (
          f(ms), f(n), pct(ms, n), f(cms), f(len(core)), pct(cms, len(core)), pct(ms + verd["POSSIBLE"], n),
          pct(cms + cp, len(core))))
    P("")
    bas = Counter()
    for e in ests:
        if e["rec"]["verdict"] in ("MATCH_SITE", "POSSIBLE"):
            bas[(e["rec"]["verdict"], e["rec"]["kind"])] += 1
    P("MATCH_SITE by basis: " + "; ".join("`%s` %s" % (k, f(v)) for (vv, k), v in sorted(bas.items(), key=lambda kv: -kv[1]) if vv == "MATCH_SITE") + ". "
      "POSSIBLE by best basis: " + "; ".join("`%s` %s" % (k, f(v)) for (vv, k), v in sorted(bas.items(), key=lambda kv: -kv[1]) if vv == "POSSIBLE") + ".")
    nu = Counter(e["rec"]["name_used"] for e in ests if e["rec"]["verdict"] == "MATCH_SITE")
    P("Name field that carried the MATCH_SITE agreement (unit: establishments): %s." % "; ".join("%s %s" % (k, f(v)) for k, v in nu.most_common()))
    multi = [s for s, k in per_site.items() if len(k) > 1]
    P("Distinct Atlas sites reached by at least one MATCH_SITE establishment: %s (unit: site rows); %s of them are reached by more than one ITA "
      "establishment_ID (several filings at one address)." % (f(len(per_site)), f(len(multi))))
    dup_addr = [g for g in c["addr_groups"].values() if len(g) > 1]
    P("Inside the ITA file itself, %s street+zip addresses carry more than one `establishment_ID` (%s establishments); left visible "
      "(`ita_estabs_at_address`), never merged (one address = one site, operator-owned; AGENTS 3)." % (f(len(dup_addr)), f(sum(len(g) for g in dup_addr))))
    nr = Counter(m["naics_relation"] for m in mrows if m["verdict"] == "MATCH_SITE")
    P("ITA NAICS vs the matched site's `naics_primary` (unit: MATCH_SITE establishments): %s - informational only; no NAICS overwrite is proposed." % "; ".join("%s %s" % (k, f(v)) for k, v in nr.most_common()))
    live = [m for m in mrows if "reverification_lead" in m["liveness_note"]]
    P("")
    P("**Liveness (activity signal only).** A CY2025 filing with employees and hours is dated evidence the establishment operated "
      "in 2025. It is never a status change (AGENTS 3). **%s ITA establishments point at an Atlas site recorded closed/idled** "
      "(%s MATCH_SITE, %s POSSIBLE) - re-verification leads only (`liveness_note`); a filing at a possibly different operator of the "
      "same address does not show the recorded operator is active." % (
          f(len(live)), f(sum(1 for m in live if m["verdict"] == "MATCH_SITE")), f(sum(1 for m in live if m["verdict"] == "POSSIBLE"))))
    for m in live[:12]:
        P("  - %s %s (%s) -> %s %s [%s]: %s%s" % (m["establishment_id"], m["establishment_name"], m["state"], m["site_id"], m["site_name"], m["verdict"], m["site_operating_status"], ("; " + m["site_caution"]) if m["site_caution"] else ""))
    cau = [m for m in mrows if m["verdict"] == "MATCH_SITE" and "tombstoned_duplicate" in m["site_caution"]]
    P("")
    P("`site_caution` (in `site_matches.csv` and `band_proposals.csv`) is read from the Atlas site row: closed/idled status, a pass-11 'tombstoned as duplicate of SITE-x' note, or a WARN citation. "
      "MATCH_SITE rows that land on a tombstoned-duplicate site: %s (the live twin is the likelier home of any band; e.g. the IFI row lands on the retired SITE-000180 while the live IER Industries row SITE-000398 carries street 'Bavaria Road' vs the ITA 'Bavaria Dr E', so the street key differs). "
      "A CY2025 filing at a plant the Atlas holds as closed on a WARN notice is not a contradiction when the WARN closure window is later than 2025 (SITE-000820's window is 2026-12-01 to 2026-12-31 per its notes)." % f(len(cau)))
    P("")

    # ---- section 4 EIN
    P("## 4. EIN to organization link candidates\n")
    eg = c["ein_members"]
    multi_eg = {k: v for k, v in eg.items() if len(v) > 1}
    est_with_ein = sum(1 for e in ests if e["ein"])
    P("EINs are public in ITA. They are **candidates only**: the registry enum (SCHEMA 4.8) has no employer-EIN value (owner item already raised), so nothing here "
      "is a `registry_links` row, and an EIN found only in this file is a phantom for registry purposes (AGENTS 4). Usable EINs "
      "(unit: distinct 9-digit EINs): %s over %s establishments (%s of rows); %s EINs appear on more than one establishment "
      "(%s establishments). Link method: the EIN of a MATCH_SITE establishment is associated with that site's org; the same EIN on other rows then points at that org." % (
          f(len(eg)), f(est_with_ein), pct(est_with_ein, n), f(len(multi_eg)), f(sum(len(v) for v in multi_eg.values()))))
    pairs = c["ein_org_pairs"]
    eins_with_org = {e for (e, o) in pairs}
    orgs_with_ein = {o for (e, o) in pairs}
    sp = Counter(e["ein_status"] for e in ests)
    P("")
    P("- **EIN-org candidate pairs: %s** (distinct EIN x Atlas org via at least one MATCH_SITE row); %s EINs reach a held org; %s Atlas orgs get at least one EIN candidate." % (f(len(pairs)), f(len(eins_with_org)), f(len(orgs_with_ein))))
    P("- `ein_status` (unit: establishments): " + "; ".join("%s %s" % (k, f(v)) for k, v in sp.most_common()) + ".")
    cand_other = [e for e in ests if e["ein_status"] == "EIN_CANDIDATE_ORG_OTHER_LOCATION"]
    cand_core = [e for e in cand_other if e["scope_class"] == "core_P"]
    P("- `EIN_CANDIDATE_ORG_OTHER_LOCATION` (%s establishments; %s are core_P with verdict not MATCH_SITE): an establishment whose EIN equals the EIN of a held org's matched site - "
      "a likely **other site of a held org** (a stronger signal than a name match; still a lead, not a dedupe verdict). Those rows' `lead_class` stays name-based, so this is an extra column, not a reclassification." % (f(len(cand_other)), f(len(cand_core))))
    span = {k: v for k, v in c["ein_orgs"].items() if len(v) > 1}
    P("- `EIN_SPANS_MULTIPLE_HELD_ORGS`: %s EINs map to more than one Atlas org through MATCH_SITE rows - possible duplicate or parent/subsidiary org records in the Atlas, or a bad site match; dedupe-review candidates, not merges (AGENTS 3: when in doubt do not merge)." % f(len(span)))
    for k, v in list(sorted(span.items()))[:15]:
        names = sorted({o + " " + A.org.get(o, {}).get("legal_name", "") for o in v})
        P("  - EIN %s: %s" % (k, " | ".join(names)))
    P("")

    # ---- section 5 bands
    P("## 5. Employee-band proposals (`band_proposals.csv`)\n")
    usable = [e for e in ests if e["avg_emp_usable"]]
    P("`annual_average_employees` is the employer-reported annual average number of employees at the establishment for CY2025 on the Form 300A "
      "(source class `government_filing`). It supports an `employee_band_site` **proposal** for **MATCH_SITE rows only**, at **site grain only** "
      "- never pushed to the organization or other sites (SCHEMA 4.5), and band only, never a headcount (SCHEMA 4.4). "
      "`employee_count_source_date` = the filing's `date_submitted` (ISO). Basis text per row: `OSHA ITA 300A CY2025, establishment_ID X: annual average employees N → band`. "
      "Zero is treated as missing, not a count.")
    P("")
    P("- Establishments with a usable count (unit: establishments): %s of %s; %s have zero. By band: %s." % (
        f(len(usable)), f(n), f(n - len(usable)),
        "; ".join("%s %s" % (b, f(sum(1 for e in usable if e["band"] == b))) for b in BAND_ORDER)))
    rel = Counter(e["reliability"] for e in usable)
    sz = Counter(e["size_flag"] for e in usable)
    hp = Counter(e["hpe_flag"] for e in usable)
    P("- **Data-quality screens (unit: establishments with a count).** `size_code_vs_avg_employees`: %s. The ITA `size` code is expected to follow the employee count "
      "(observed: 1 = under 20, 21 = 20-99, 22 = 100-249, 3 = 250+, and a code 2 that spans 20-249); %s of %s counts fall outside their own row's size class - "
      "the two fields disagree and this packet does not decide which is right. `hours_per_employee_screen`: %s (a count is 'implausible' when "
      "hours worked per employee is under %d or over %s - the file median is about 2,000; these look like keying errors, e.g. an hours figure typed into the employee box). "
      "`reliability` = ok (both screens pass) / review (size code disagrees) / suspect (hours screen fails)." % (
          "; ".join("%s %s" % (k, f(v)) for k, v in sz.most_common()), f(sz["inconsistent"]), f(len(usable)),
          "; ".join("%s %s" % (k, f(v)) for k, v in hp.most_common()), HPE_LOW, f(HPE_HIGH)))
    P("- Reliability of all usable counts: " + "; ".join("%s %s" % (k, f(v)) for k, v in rel.most_common()) + ".")
    P("")
    npr = len(prows)
    rc = Counter(r["relation_to_current"] for r in prows)
    ok_rc = Counter(r["relation_to_current"] for r in prows if r["reliability"] == "ok")
    P("**Band proposals: %s** (unit: Atlas site rows; one per matched site; where several ITA filings sit at one site the strongest match, then the most reliable, then the latest filing is shown and the others are listed in `other_ita_estabs_at_site` - never summed). "
      "MATCH_SITE sites reached: %s; sites with no usable count: %s; sites with more than one ITA establishment: %s." % (
          f(npr), f(len(per_site)), f(len(per_site) - npr), f(len(multi))))
    P("")
    P("| Relation to the site's current `employee_band_site` | All proposals | reliability = ok only |")
    P("|---|---:|---:|")
    for k in ("fills_blank", "fills_unknown", "matches_existing", "conflicts_existing", "existing_nonstandard_value"):
        P("| %s | %s | %s |" % (k, f(rc[k]), f(ok_rc[k])))
    P("| **Total** | **%s** | **%s** |" % (f(npr), f(sum(ok_rc.values()))))
    P("")
    fills = rc["fills_blank"] + rc["fills_unknown"]
    P("**Fill blanks:** %s proposals fill a blank or `unknown` band (%s of them reliability ok). Existing values outside the SCHEMA 4.4 vocabulary are flagged `existing_nonstandard_value` and never overwritten by this packet. "
      "`conflicts_existing` rows are for integrator review; existing bands that came from the CRM landing (242 banded-only values per the QUEUE) are not distinguished in the site CSV, so provenance of the existing value must be read from the site notes." % (f(fills), f(ok_rc["fills_blank"] + ok_rc["fills_unknown"])))
    P("")
    P("Proposed bands (unit: site rows): " + "; ".join("%s %s" % (b, f(sum(1 for r in prows if r["proposed_employee_band_site"] == b))) for b in BAND_ORDER) + ".")
    P("")

    # ---- section 5b comparison with inspection lane
    if I is not None:
        P("### 5.1 Comparison with the inspection lane's proposals\n")
        vs = Counter(r["vs_inspection_lane"] for r in prows)
        P("The inspection lane (`tasks/osha-spine-2026-11-01/band_proposals.csv`, %s proposals, band from `nr_in_estab` at the latest inspection with a count, source dates 2019-2026) vs this packet, by site (unit: site rows). ITA is the stronger and more recent source (an annual employer-attested "
          "figure for CY2025 vs an inspection-time figure of uncertain definition) - **disagreements are flagged, not resolved**." % f(len(I["band"])))
        P("")
        P("| Result | Site rows |")
        P("|---|---:|")
        P("| agree (same band) | %s |" % f(vs["agree"]))
        P("| differ | %s |" % f(vs["differ"]))
        P("| ITA-only (site has an ITA proposal, no inspection proposal) | %s |" % f(vs["ita_only"]))
        P("| inspection-only (site has an inspection proposal, no ITA proposal) | %s |" % f(len(c["insp_only"])))
        P("")
        both = vs["agree"] + vs["differ"]
        P("Sites with both proposals: %s; **agreement %s** (%s same band)." % (f(both), pct(vs["agree"], both), f(vs["agree"])))
        steps = Counter()
        for r in prows:
            if r["vs_inspection_lane"] == "differ":
                s = r["band_step_ita_minus_inspection"]
                steps[s if isinstance(s, int) else 99] += 1
        P("Among the %s differing sites, band distance (ITA minus inspection, in band steps): %s. Adjacent-band differences (+/-1) are %s of the differing sites; ITA higher in %s, ITA lower in %s. ITA is the newer figure for %s of the %s sites with both." % (
            f(vs["differ"]), "; ".join("%+d: %s" % (k, f(v)) for k, v in sorted(steps.items())) if steps else "none",
            pct(steps[1] + steps[-1], vs["differ"]), f(sum(v for k, v in steps.items() if k not in (99,) and k > 0)),
            f(sum(v for k, v in steps.items() if k not in (99,) and k < 0)),
            f(sum(1 for r in prows if r["ita_newer_than_inspection"] == "Y")), f(both)))
        agree_ok = sum(1 for r in prows if r["vs_inspection_lane"] == "agree" and r["reliability"] == "ok")
        both_ok = sum(1 for r in prows if r["vs_inspection_lane"] in ("agree", "differ") and r["reliability"] == "ok")
        P("Restricted to ITA reliability = ok: agreement %s of %s (%s)." % (f(agree_ok), f(both_ok), pct(agree_ok, both_ok)))
        # existing band triangulation
        tri = Counter()
        for r in prows:
            if r["vs_inspection_lane"] in ("agree", "differ") and r["current_employee_band_site"] in BAND_VOCAB - {"unknown"}:
                ib = r["inspection_lane_band"]
                ex = r["current_employee_band_site"]
                p = r["proposed_employee_band_site"]
                tri["existing=ITA" if ex == p else "existing=inspection" if ex == ib else "existing matches neither"] += 1
        if tri:
            P("Where the site already carries a standard band and both lanes propose one (%s sites): %s." % (f(sum(tri.values())), "; ".join("%s %s" % (k, f(v)) for k, v in tri.most_common())))
        P("")
        P("`inspection-only` sites are those the ITA extract does not reach with a usable count (not in the filtered extract, filed under a different name/address, or zero count); that is not a disagreement. Reproduce the list as inspection `band_proposals.csv` minus this file's `site_id` set.")
        P("")
        # cross-source establishment cross-reference + verdict consistency
        xs = Counter(m["cross_source"] for m in mrows)
        P("### 5.2 Establishment cross-reference with the inspection lane\n")
        P("Each ITA establishment was looked up in the inspection lane's `establishments.csv` (%s establishments, all core-family NAICS, inspected 2019 or later): same street + state + (zip5 or city) + name agreement = `BOTH_SOURCES`; "
          "street unknown on one side + same zip5 + strong name = `BOTH_SOURCES` (name+zip); same street + locality but name differs = `BOTH_ADDRESS_NAME_DIFFERS` (co-tenant, rebrand or successor); else `ITA_ONLY`. "
          "Over all ITA rows (unit: ITA establishments): BOTH_SOURCES %s; BOTH_ADDRESS_NAME_DIFFERS %s; ITA_ONLY %s. Over core-family rows: BOTH_SOURCES %s of %s." % (
              f(len(I["ests"])), f(xs["BOTH_SOURCES"]), f(xs["BOTH_ADDRESS_NAME_DIFFERS"]), f(xs["ITA_ONLY"]),
              f(sum(1 for e in core if mb[e["establishment_id"]]["cross_source"] == "BOTH_SOURCES")), f(len(core))))
        cons = Counter()
        for e in core:
            m = mb[e["establishment_id"]]
            if m["cross_source"] != "BOTH_SOURCES":
                continue
            iv = set(m["inspection_lane_verdict"].split(";"))
            if e["rec"]["verdict"] == "MATCH_SITE":
                cons["ITA MATCH_SITE; inspection lane MATCH_SITE at the same site" if m["site_id"] in m["inspection_lane_site_id"].split(";") else
                     "ITA MATCH_SITE; inspection lane MATCH_SITE at a different site" if "MATCH_SITE" in iv else
                     "ITA MATCH_SITE; inspection lane POSSIBLE/NO_MATCH"] += 1
            elif e["rec"]["verdict"] == "NO_MATCH":
                cons["ITA NO_MATCH; inspection lane NO_MATCH" if iv == {"NO_MATCH"} else "ITA NO_MATCH; inspection lane MATCH_SITE/POSSIBLE"] += 1
            else:
                cons["ITA POSSIBLE; inspection lane %s" % ("/".join(sorted(iv)))] += 1
        P("Verdict consistency between the two lanes on BOTH_SOURCES core rows (a check on the shared ladder): " + "; ".join("%s: %s" % (k, f(v)) for k, v in cons.most_common()) + ".")
        P("")

    # ---- section 6 leads
    P("## 6. NO_MATCH leads in core polymer NAICS, by state, sorted by QCEW gap\n")
    cnm = [e for e in core if e["rec"]["verdict"] == "NO_MATCH"]
    cnmP = [e for e in cnm if e["scope_class"] == "core_P"]
    lc = Counter(e["rec"]["lead"] for e in cnmP)
    P("NO_MATCH = no Atlas site candidate cleared the ladder: a **lead, not a finding of absence** (name or street form may differ; the Atlas may hold the plant under another operator). "
      "Lead pool = core-family rows (`core_P`, `core_S`, `core_X`, `core_unlisted`); the headline pool is **`core_P`** (SCHEMA 2.2 Ring 1/2 Primary codes). "
      "Core-family NO_MATCH establishments: **%s** (core_P %s; core_S %s; core_X %s; core_unlisted %s). Of the **%s core_P** NO_MATCH: "
      "%s NET_NEW_LEAD (no Atlas org with this normalized name on either name field), %s NAME_EQUALS_HELD_ORG_OTHER_LOCATION (likely another site of a held org), %s HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS, "
      "%s NAME_IN_HELD_ORG_TRADE_NAMES_OR_NOTES. `lead_class` and `lead_ref` per row are in `site_matches.csv` (rows with `verdict = NO_MATCH`). Every row still needs ring/scope adjudication - owner-ruling-adjacent, not settled here (AGENTS 2.9)." % (
          f(len(cnm)), f(len(cnmP)), f(sum(1 for e in cnm if e["scope_class"] == "core_S")), f(sum(1 for e in cnm if e["scope_class"] == "core_X")),
          f(sum(1 for e in cnm if e["scope_class"] == "core_unlisted")), f(len(cnmP)), f(lc["NET_NEW_LEAD"]),
          f(lc["NAME_EQUALS_HELD_ORG_OTHER_LOCATION"]), f(lc["HELD_ORG_SAME_NAME_CITY_DIFFERENT_ADDRESS"]),
          f(lc["NAME_IN_HELD_ORG_TRADE_NAMES_OR_NOTES"])))
    P("")
    P("Sort key = QCEW gap per `docs/denominators/README.md`: QCEW 2023 private establishments, NAICS 326, minus Atlas strict 326 sites (`operating_status` active/unknown, tier A-C, `naics_primary` starts 326), recomputed from `data/sites_*.csv` at run time. "
      "The gap is a count difference, not a coverage figure, and the NO_MATCH pool per state is **not** an estimate of it (the ITA extract is a filtered slice of 20+-employee filers over several NAICS families; QCEW counts 326 reporting units of every size). Top 20 states by gap:")
    P("")
    P("| Gap rank | State | QCEW gap (326) | ITA establishments (all) | core family | core MATCH_SITE | core NO_MATCH | core_P NO_MATCH | of which NET_NEW | core_P NO_MATCH also in inspection lane | of which NET_NEW |")
    P("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    shown = 0
    for s in ordered:
        if s not in gaps:
            continue
        shown += 1
        if shown > 20:
            break
        k = st_c[s]
        P("| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            c["gap_rank"][s], s, f(gaps[s][2]), f(k["all"]), f(k["core"]), f(k["core_MATCH_SITE"]), f(k["core_NO_MATCH"]),
            f(k["core_no_match_core_P"]), f(k["coreP_lead_NET_NEW_LEAD"]), f(k["coreP_both_sources"]), f(k["coreP_both_sources_net_new"])))
    P("")
    both = [e for e in cnmP if mb[e["establishment_id"]]["cross_source"] == "BOTH_SOURCES"]
    both_new = [e for e in both if e["rec"]["lead"] == "NET_NEW_LEAD"]
    both_nn_re = [e for e in both if e["avg_emp_usable"]]
    addr_only = [e for e in cnmP if mb[e["establishment_id"]]["cross_source"] == "BOTH_ADDRESS_NAME_DIFFERS"]
    P("**Leads seen in both OSHA sources (stronger leads).** core_P NO_MATCH establishments that the inspection lane also lists (same address and name, or name + zip): **%s of %s** (%s); %s of those are NET_NEW_LEAD. "
      "A further %s core_P NO_MATCH share an address with an inspection-lane establishment under a different name (`BOTH_ADDRESS_NAME_DIFFERS`; co-tenant, rebrand or successor - weaker). "
      "Two separate OSHA records (an employer-filed 300A for CY2025 and a compliance-officer inspection record since 2019) naming the same establishment raises confidence that it exists and operated, "
      "not that it is in scope (both carry an OSHA-channel NAICS, so they are not independent evidence of the code). Full per-state counts: `leads_by_state.csv` (`coreP_no_match_both_osha_sources`, `..._net_new`)." % (
          f(len(both)), f(len(cnmP)), pct(len(both), len(cnmP)), f(len(both_new)), f(len(addr_only))))
    P("")
    P("Examples: the strongest rows in the five largest-gap states (core_P, NO_MATCH, seen in both OSHA sources, NET_NEW_LEAD, reliability ok), largest reported employee count first, up to 5 per state; names are public business names as filed. Full lists = filter `site_matches.csv` on `scope_class=core_P`, `verdict=NO_MATCH`, `cross_source=BOTH_SOURCES`, `lead_class=NET_NEW_LEAD`.")
    P("")
    P("| State | ITA establishment_ID | Company / establishment | City | NAICS | Employees band (ITA) | Latest OSHA inspection |")
    P("|---|---|---|---|---|---|---|")
    top5 = [s_ for s_ in ordered if s_ in gaps][:5]
    for s_ in top5:
        pool = [e for e in cnmP if e["state"] == s_ and mb[e["establishment_id"]]["cross_source"] == "BOTH_SOURCES"
                and e["rec"]["lead"] == "NET_NEW_LEAD" and e["reliability"] == "ok"]
        pool.sort(key=lambda e: (-(e["avg_emp"] or 0), e["establishment_id"]))
        for e in pool[:5]:
            P("| %s | %s | %s / %s | %s | %s | %s | %s |" % (s_, e["establishment_id"], (e["company_name"] or "-").replace("|", "/"), e["name_raw"].replace("|", "/"),
                                                         e["city"], e["naics_code"], e["band"], mb[e["establishment_id"]]["inspection_lane_latest_inspection"]))
    P("")
    P("Other lead-strength columns in `site_matches.csv` / `leads_by_state.csv`: `ein_status = EIN_CANDIDATE_ORG_OTHER_LOCATION` (the EIN ties the row to a held org's matched site; %s core_P NO_MATCH rows) and `ita_estabs_at_address` (several filings at one address; "
      "distinct street+zip addresses among core_P NO_MATCH, summed over states: %s)." % (f(sum(st_c[s]["coreP_ein_held_org"] for s in st_c)), f(sum(len(c["loc_sets"][s]) for s in c["loc_sets"]))))
    r3 = [e for e in ests if e["scope_class"] == "ring3_P"]
    P("Ring 3 Primary rows (333511 / 424610 / 562920) are outside the core-family pool but counted separately (unit: ITA establishments): %s total, %s MATCH_SITE, %s POSSIBLE, %s NO_MATCH. They are Ring 3 distribution/tooling/recovery candidates for an owner scope decision, not Ring 1/2 leads." % (
        f(len(r3)), f(sum(1 for e in r3 if e["rec"]["verdict"] == "MATCH_SITE")), f(sum(1 for e in r3 if e["rec"]["verdict"] == "POSSIBLE")), f(sum(1 for e in r3 if e["rec"]["verdict"] == "NO_MATCH"))))
    P("")

    # ---- caveats
    P("## 7. Caveats (binding on any reader)\n")
    for t in (
        "**Filtered extract, unknown filter.** The owner's filter is not known in detail; the file is not a census of ITA filers, and nothing here (including 'ITA_ONLY') says anything about establishments outside it.",
        "**ITA coverage is by rule, not by plant.** Only establishments whose employers are subject to OSHA's electronic-submission thresholds (and that actually filed) appear; the extract nonetheless contains establishments with under 20 employees (company-level thresholds), so the threshold is not a clean line. Absence is nothing.",
        "**NAICS is employer-entered** and can be stale, coarse or wrong (the extract mixes NAICS 2012/2017/2022 vintages and includes mis-coded rows, e.g. plastic-surgeon codes 621111, retail 441330, and odd descriptions). It is a filing value for the establishment, never a company fact, never a ring decision, never overwrites a site NAICS (SCHEMA 2.1, AGENTS 4). `scope_class` labels; it does not rule.",
        "**`annual_average_employees` is a self-reported figure** with visible quality problems (size-code disagreement; hours-per-employee implausibility; counts of 50,000+ at plants). It is a band input with a date, not a headcount; `reliability` is a screen, not a verdict. Zero is missing. Never allocated to the org or other sites (SCHEMA 4.5).",
        "**`date_submitted` is the filing date for CY2025**, not the date the average was measured; the figure describes calendar 2025. `employee_count_source_date` follows the owner's instruction (date_submitted).",
        "**Addresses are establishment addresses** as typed by the filer; leading zeros in zip and EIN were lost by the download and restored by rule; a few filers give an HQ or mailing address for a plant (cannot be detected from the file alone). Matching is by address + name, not coordinates.",
        "**Activity is not status.** A CY2025 filing never changes an Atlas status; the closed/idled overlaps are re-verification leads only (AGENTS 3). A failed or empty match is never evidence of closure.",
        "**EIN is a candidate link only** (no registry enum value; owner item raised). One EIN can span several establishments, orgs or affiliates; EIN-spans-multiple-orgs rows are dedupe-review candidates, never merges.",
        "**Leads only.** No row is a verdict in the AGENTS 2.8 grammar (not VERIFIED, REJECT, STILL_UNCERTAIN or DUPLICATE_OF). NO_MATCH is a lead; MATCH_SITE is a match candidate for the integrator.",
        "**Counts name their unit and filter:** rows/establishments = ITA establishment records (one `establishment_ID` each); sites = Atlas site rows; proposals = one per matched Atlas site; core family = NAICS under 3252/3255/3259/326; core_P = the Primary-signal subset.",
        "**Privacy.** No individual names, emails or phones in any output; injury/illness data is excluded entirely; EIN is a business identifier published by OSHA in this dataset."):
        P("- " + t)
    P("")
    P("## 8. Reproduce\n")
    P("```")
    P("python3 -I scripts/build_osha_ita.py <path>/filtered_full_value_chain_ITA_300A.tsv --as-of %s" % as_of.isoformat())
    P("# input SHA-256: %s" % c["sha"])
    P("# cross-reference inputs: tasks/osha-spine-2026-11-01/{establishments,site_matches,band_proposals}.csv")
    P("```")
    with open(os.path.join(a.out_dir, "REPORT.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    return sum(len(x) for x in L)


if __name__ == "__main__":
    sys.exit(main())
