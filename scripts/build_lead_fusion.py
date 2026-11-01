#!/usr/bin/env python3
"""Lead fusion: cluster the NO_MATCH / POSSIBLE rows of the 2026-11-01 federal-source packets
into candidate establishments, re-check each cluster against the CURRENT Atlas, score by how
many independent source families confirm it, and write tasks/lead-fusion-2026-11-01/.

Packet-lane product (AGENTS.md section 2 rule 7): reads the packets and data/, writes only
under tasks/lead-fusion-2026-11-01/. Never edits data/, allocates no Atlas ID, sets no tier,
changes no status. Every output row is a DISCOVERY LEAD, never existence or scope evidence.

Stdlib only. Re-runnable and deterministic:
    python3 scripts/build_lead_fusion.py [--as-of 2026-11-01] [--dump-dropped PATH]
                                         [--audit-print] [--selftest 200] [--no-write]

Normalizers (name_key, street_key, squash, dedupe) are imported from scripts/atlas.py.
"""
import argparse
import csv
import datetime as dt
import difflib
import hashlib
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import atlas  # noqa: E402  (scripts/atlas.py: name_key, street_key, squash, dedupe, load_tables)

csv.field_size_limit(10 ** 8)
ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
DATA = os.path.join(ROOT, "data")
TASKS = os.path.join(ROOT, "tasks")
OUT = os.path.join(TASKS, "lead-fusion-2026-11-01")

P_ITA = os.path.join(TASKS, "osha-ita-2026-11-01")
P_OSHA = os.path.join(TASKS, "osha-spine-2026-11-01")
P_ECHO = os.path.join(TASKS, "echo-frs-spine-2026-11-01")
P_F55 = os.path.join(TASKS, "form5500-spine-2026-11-01")
P_FED = os.path.join(TASKS, "federal-leads-2026-11-01")
P_PAT = os.path.join(TASKS, "patents-pilot-2026-11-01")

FAMILIES = ["ITA", "OSHA", "ECHO", "F5500", "USASPEND", "PATENT"]
AGENCY = {"ITA": "DOL-OSHA", "OSHA": "DOL-OSHA", "ECHO": "EPA", "F5500": "DOL-EBSA", "USASPEND": "USAspending/SAM",
          "PATENT": "USPTO"}
# Address grade: 'plant' = a worksite / permitted-facility address; 'hq' = registered / mailing / HQ-grade address.
GRADE = {"ITA": "plant", "OSHA": "plant", "ECHO": "plant", "F5500": "hq", "USASPEND": "hq", "PATENT": "hq"}
NAME_PRIORITY = ["OSHA", "ITA", "ECHO", "F5500", "USASPEND", "PATENT"]
ADDR_PRIORITY = ["ITA", "OSHA", "ECHO", "F5500", "USASPEND", "PATENT"]

# Published NO_MATCH / POSSIBLE counts copied from each source packet's REPORT.md (reconciliation, AGENTS 2 rule 10c)
PUBLISHED = {
    "ITA": {"NO_MATCH": 9145, "POSSIBLE": 346, "total": 11194},
    "OSHA": {"NO_MATCH": 5256, "POSSIBLE": 246, "total": 6473},
    "ECHO": {"NO_MATCH": 13255, "POSSIBLE": 315, "total": 15920},
    "F5500": {"NO_MATCH": 4581, "POSSIBLE": 418, "total": 5897},
    "USASPEND": {"NO_MATCH": 4450, "POSSIBLE": 77, "total": 4756},
    "PATENT": {"NO_MATCH": 230, "POSSIBLE": 71, "total": 414},
}
ITA_BOTH_OSHA_PUBLISHED = {"core_P_NO_MATCH": 4376, "core_P_both_sources": 1003, "address_name_differs": 138}

CORE_PREFIX = ("3252", "3255", "3259", "326")
RING3_PRIMARY = {"333511", "424610", "562920"}
BANDS = ["1-9", "10-49", "50-99", "100-249", "250-499", "500-999", "1000-4999", "5000+"]
BAND_ORDER = {b: i for i, b in enumerate(BANDS)}
TOP_STATES = ["CA", "TX", "FL", "MI", "IL", "GA", "IN", "WI", "NY", "NC", "OH", "PA"]
USPS = atlas.USPS

GENERIC = set("""plastic plastics industries industry industrial products product manufacturing mfg group holdings holding
international intl technologies technology tech systems system packaging rubber polymer polymers molding moulding chemical
chemicals corporation america american usa us north south east west division div plant facility site location operations
enterprises solutions services service and of dba llc inc corp co company the ltd lp llp plc na films film foam coatings
coating composites composite extrusion extruded injection bag bags container containers specialty engineered materials
material""".split())
STREET_STOP = set(atlas.SUFFIX.values()) | {"n", "s", "e", "w", "ne", "nw", "se", "sw", "us", "hwy", "rte", "state"}

_STREET_PATS = [
    re.compile(r"Street(?:\s+correct(?:ion|ed)[^:]{0,20})?(?:\s*\((?:per|from)[^)]*\))?:\s*(\d[^;|\n]{2,80})", re.I),
    re.compile(r"Address[^:]{0,60}match\):\s*(\d[^;|\n]{2,80})", re.I),
]
POBOX_RE = re.compile(r"\b(p\.?\s*o\.?\s*box|post office box)\s*#?\s*\w+", re.I)


# ------------------------------------------------------------------ small helpers
def rd(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def zip5(z):
    d = re.sub(r"\D", "", z or "")
    return d[:5] if len(d) >= 5 else ""


def skey_of(street):
    """Usable street key: has a house number, is not a PO box."""
    s = (street or "").strip()
    if s and POBOX_RE.search(s):
        s = POBOX_RE.sub(" ", s).strip(" ,;-")   # keep a physical street that sits beside a PO box; a bare PO box keys nothing
    if not s:
        return ""
    k = atlas.street_key(s)
    # a house number: digits, or the Wisconsin/Illinois grid form (W158 N9332, N118W18981, S80 W18766)
    return k if re.match(r"[a-z]{0,2}\d", k) and len(k) >= 5 else ""


def street_from_notes(notes, city):
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


def dist_tokens(name):
    toks = atlas.name_key(name).split()
    return tuple(t for t in toks if t not in GENERIC and not t.isdigit())


def clean_name(n):
    n = (n or "").strip()
    n = re.sub(r"^\d{3,7}\s*-\s+", "", n)  # numeric OSHA-style prefix
    return "" if n in ("-", "--") else n


def band_of(n):
    try:
        n = int(float(n))
    except (TypeError, ValueError):
        return ""
    if n < 1:
        return ""
    for hi, b in [(9, "1-9"), (49, "10-49"), (99, "50-99"), (249, "100-249"), (499, "250-499"), (999, "500-999"),
                  (4999, "1000-4999")]:
        if n <= hi:
            return b
    return "5000+"


def parse_date(s):
    try:
        return dt.date.fromisoformat((s or "").strip()[:10])
    except ValueError:
        return None


def is_core(code):
    return code.startswith(CORE_PREFIX)


def split_semi(s):
    return [x.strip() for x in (s or "").split(";") if x.strip()]


class Row:
    __slots__ = ("family", "sid", "key", "names", "nks", "street", "skey", "housenum", "city", "csq", "state", "zip5",
                 "naics", "ein", "size_n", "size_band", "size_kind", "date", "verdict", "grade", "x", "idx", "core",
                 "ring3", "x325920", "nm")

    def __init__(self, family, sid, names, street, city, state, z, naics, ein, size_n, size_kind, date, verdict, extra):
        self.family, self.sid, self.key = family, sid, f"{family}:{sid}"
        nm = []
        for n in names:
            n = clean_name(n)
            if n and n not in nm and atlas.name_key(n):
                nm.append(n)
        self.names = nm
        self.nm = [(atlas.name_key(n), dist_tokens(n)) for n in nm]      # (name_key, distinctive tokens)
        self.nks = [k for k, _ in self.nm]
        self.street = (street or "").strip()
        self.skey = skey_of(self.street)
        m = re.match(r"([a-z]{0,2}\d+)", self.skey)
        self.housenum = m.group(1) if m else ""
        self.city = (city or "").strip()
        self.csq = atlas.squash(self.city)
        self.state = (state or "").strip().upper()
        self.zip5 = zip5(z)
        self.naics = naics
        self.ein = ein
        self.size_n = size_n
        self.size_band = band_of(size_n) if size_n not in (None, "") else ""
        self.size_kind = size_kind
        self.date = parse_date(date)
        self.verdict = verdict
        self.grade = GRADE[family]
        self.x = extra
        coded = [c for c in naics if is_core(c)]
        self.x325920 = bool(coded) and all(c == "325920" for c in coded)
        self.core = any(c != "325920" for c in coded)
        self.ring3 = any(c in RING3_PRIMARY for c in naics)
        self.idx = -1


# ------------------------------------------------------------------ loading the six source families
def load_sources(stats):
    rows = []

    # ---- ITA
    est = {r["establishment_id"]: r for r in rd(os.path.join(P_ITA, "establishments.csv"))}
    sm = rd(os.path.join(P_ITA, "site_matches.csv"))
    assert len({r["establishment_id"] for r in sm}) == len(sm) == len(est), "ITA ids not unique / not aligned"
    stats["ITA_all_rows"] = len(sm)
    for m in sm:
        if m["verdict"] not in ("NO_MATCH", "POSSIBLE"):
            continue
        e = est[m["establishment_id"]]
        ein = e["ein"] if e["ein_quality"] in ("ok", "zero_padded") and re.fullmatch(r"\d{9}", e["ein"] or "") else ""
        n = e["annual_average_employees"]
        size_n = n if (e["reliability"] != "suspect" and n not in ("", "0")) else ""
        rows.append(Row("ITA", m["establishment_id"], [e["establishment_name"], e["company_name"]], e["street"], e["city"],
                        e["state"], e["zip5"], [e["naics_code"]] if e["naics_code"] else [], ein, size_n,
                        "establishment employees (ITA CY2025 annual average)", e["date_submitted"], m["verdict"],
                        {"scope_class": m["scope_class"], "lead_class": m["lead_class"], "reliability": e["reliability"],
                         "cross_source": m["cross_source"]}))

    # ---- OSHA inspections
    est = {r["est_key"]: r for r in rd(os.path.join(P_OSHA, "establishments.csv"))}
    sm = rd(os.path.join(P_OSHA, "site_matches.csv"))
    assert len({r["est_key"] for r in sm}) == len(sm) == len(est), "OSHA ids not unique / not aligned"
    stats["OSHA_all_rows"] = len(sm)
    for m in sm:
        if m["verdict"] not in ("NO_MATCH", "POSSIBLE"):
            continue
        e = est[m["est_key"]]
        nm = [e["name"]] + split_semi(e.get("name_variants", ""))
        codes = split_semi(e.get("naics_all", "")) or ([e["naics_latest"]] if e["naics_latest"] else [])
        n = e["nr_in_estab_latest_valid"]
        rows.append(Row("OSHA", m["est_key"], nm, e["street"], e["city"], e["state"], e["zip"], codes, "",
                        n if n not in ("", "0") else "", "establishment employees (OSHA nr_in_estab, latest valid inspection)",
                        e["latest_inspection"], m["verdict"], {"lead_class": m["lead_class"]}))

    # ---- ECHO / FRS
    fac = {r["registry_id"]: r for r in rd(os.path.join(P_ECHO, "facilities.csv"))}
    sm = rd(os.path.join(P_ECHO, "site_matches.csv"))
    assert len({r["registry_id"] for r in sm}) == len(sm) == len(fac), "ECHO ids not unique / not aligned"
    stats["ECHO_all_rows"] = len(sm)
    for m in sm:
        if m["verdict"] not in ("NO_MATCH", "POSSIBLE"):
            continue
        f = fac[m["registry_id"]]
        codes = split_semi(f["naics_scope_codes"]) or split_semi(f["naics_codes"])
        rows.append(Row("ECHO", m["registry_id"], [f["facility_name"]], f["street"], f["city"], f["state"], f["zip"], codes,
                        "", "", "", f["last_activity_date"], m["verdict"],
                        {"scope_class": f["scope_class"], "signal": f["signal_class"], "county": f["county_frs"],
                         "tri_ids": split_semi(f["tri_ids"]), "noise": f["name_noise_hint"], "lead_class": m["lead_class"]}))

    # ---- Form 5500
    sp = {r["ein"]: r for r in rd(os.path.join(P_F55, "sponsors.csv"))}
    mm = rd(os.path.join(P_F55, "matches.csv"))
    assert len({r["ein"] for r in mm}) == len(mm) == len(sp), "F5500 eins not unique / not aligned"
    stats["F5500_all_rows"] = len(mm)
    for m in mm:
        if m["match_class"] not in ("NO_MATCH", "POSSIBLE"):
            continue
        s = sp[m["ein"]]
        code = s["business_code"]
        rows.append(Row("F5500", m["ein"], [s["sponsor_name"], s["dba_name"]], s["street_address"], s["city"], s["state"],
                        s["zip"], [code] if code else [], m["ein"] if re.fullmatch(r"\d{9}", m["ein"]) else "",
                        s["active_participants"] if s["active_participants"] not in ("", "0") else "",
                        "employer plan participants (Form 5500; employer level, not establishment)", s["latest_date_received"],
                        m["match_class"], {"plan_year": s["plan_year"], "address_source": s["address_source"],
                                           "street_withheld": s["street_withheld"] not in ("", "0", "N")}))

    # ---- USAspending
    rec = {r["recipient_uei"]: r for r in rd(os.path.join(P_FED, "usaspending_recipients.csv"))}
    fm = [r for r in rd(os.path.join(P_FED, "matches.csv")) if r["source"] == "USASPENDING_UEI"]
    assert len({r["source_id"] for r in fm}) == len(fm) == len(rec), "USAspending UEIs not unique / not aligned"
    stats["USASPEND_all_rows"] = len(fm)
    for m in fm:
        if m["match_class"] not in ("NO_MATCH", "POSSIBLE_REVIEW"):
            continue
        s = rec[m["source_id"]]
        mix = [c.split(":")[0] for c in split_semi(s["award_naics_mix_awards"])]
        rows.append(Row("USASPEND", m["source_id"], [s["recipient_name"]], s["recipient_street"], s["recipient_city"],
                        s["recipient_state"], s["recipient_zip5"], mix, "", "", "", "",
                        "POSSIBLE" if m["match_class"] == "POSSIBLE_REVIEW" else "NO_MATCH",
                        {"country": s["recipient_country"], "obligated": s["obligated_usd_fy22_26"]}))

    # ---- Patents
    asg = {r["assignee_id"]: r for r in rd(os.path.join(P_PAT, "assignees.csv"))}
    pm = rd(os.path.join(P_PAT, "matches.csv"))
    assert len({r["assignee_id"] for r in pm}) == len(pm) == len(asg), "patent ids not unique / not aligned"
    stats["PATENT_all_rows"] = len(pm)
    for m in pm:
        if m["match_class"] not in ("NO_MATCH", "POSSIBLE"):
            continue
        a = asg[m["assignee_id"]]
        nm = [a["assignee_name"]] + split_semi(a.get("name_variants", ""))
        rows.append(Row("PATENT", m["assignee_id"], nm, "", a["city"], a["state"], "", [], "", "", "", a["last_grant_date"],
                        m["match_class"], {"county": a["county"], "patent_count": a["patent_count"]}))
    assert len({r.key for r in rows}) == len(rows), "row keys not unique across families"
    return rows


# ------------------------------------------------------------------ name compatibility
_RANK = {"exact": 5, "exact_distinct": 4, "nospace": 4, "subset": 3, "jaccard": 2, "first": 1, "fuzzy": 1}
FIRM = ("exact", "exact_distinct", "nospace", "subset", "jaccard")


def name_compat(a_names, b_names):
    """a_names/b_names: lists of (name_key, distinctive-token tuple). Returns the best level or ''."""
    best = ""
    for ka, da in a_names:
        for kb, db in b_names:
            lvl = ""
            sa_, sb_ = ka.replace(" ", ""), kb.replace(" ", "")
            if ka and ka == kb:
                lvl = "exact"
            elif min(len(sa_), len(sb_)) >= 6 and (sa_.startswith(sb_) or sb_.startswith(sa_)):
                lvl = "nospace"       # 'TydenBrooks' / 'Tyden Brooks', 'T G Missouri' / 'TG Missouri Perryville'
            elif da and db:
                sa, sb = set(da), set(db)
                if sa == sb:
                    lvl = "exact_distinct"
                elif sa <= sb or sb <= sa:
                    lvl = "subset"
                elif len(sa & sb) / len(sa | sb) >= 0.5:
                    lvl = "jaccard"
                elif da[0] == db[0] and len(da[0]) >= 4:
                    lvl = "first"
            if not lvl and ka and kb and min(len(ka), len(kb)) >= 6 and difflib.SequenceMatcher(None, ka, kb).ratio() >= 0.88:
                lvl = "fuzzy"
            if lvl and _RANK[lvl] > _RANK.get(best, 0):
                best = lvl
    return best


# ------------------------------------------------------------------ clustering
class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if ra < rb:
            self.p[rb] = ra
        else:
            self.p[ra] = rb
        return True


def cluster_rows(rows, stats):
    uf = UF(len(rows))
    edges = Counter()              # basis -> successful unions
    not_merged = Counter()         # name/locality candidates refused because a real street differs
    row_bases = defaultdict(set)   # row idx -> edge bases it took part in
    blocked = []                   # (basis, i, j) same address, names incompatible -> not merged

    def link(i, j, basis):
        if uf.union(i, j):
            edges[basis] += 1
        row_bases[i].add(basis)
        row_bases[j].add(basis)

    # phase 1a: street + zip5 (strong); street + city where either zip5 is missing; name guard
    g_zip, g_city = defaultdict(list), defaultdict(list)
    for r in rows:
        if r.skey and r.state in USPS:
            if r.zip5:
                g_zip[(r.state, r.skey, r.zip5)].append(r.idx)
            g_city[(r.state, r.skey, r.csq)].append(r.idx)
    seen = set()
    for grp, basis in ((g_zip, "street_zip"), (g_city, "street_city")):
        for idxs in grp.values():
            for a in range(len(idxs)):
                for b in range(a + 1, len(idxs)):
                    i, j = idxs[a], idxs[b]
                    ri, rj = rows[i], rows[j]
                    if (i, j) in seen:
                        continue
                    seen.add((i, j))
                    lvl = name_compat(ri.nm, rj.nm)
                    if basis == "street_city" and ri.zip5 and rj.zip5:
                        # both ZIP5s present but different (sources disagree on the ZIP of one street address): same state,
                        # same city, same street and a firm name match is one establishment
                        if lvl in FIRM:
                            link(i, j, "street_city_zip_differs")
                        continue
                    if lvl:
                        link(i, j, basis)
                    else:
                        blocked.append((basis, i, j))
    # phase 1b: same house number + zip5 + a shared street word + a firm name match (street spelling variance)
    g_hn = defaultdict(list)
    for r in rows:
        if r.skey and r.housenum and r.zip5 and r.state in USPS:
            g_hn[(r.state, r.zip5, r.housenum)].append(r.idx)
    for idxs in g_hn.values():
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                i, j = idxs[a], idxs[b]
                ri, rj = rows[i], rows[j]
                if ri.skey == rj.skey or uf.find(i) == uf.find(j):
                    continue
                ta = [t for t in ri.skey.split()[1:] if t not in STREET_STOP]
                tb = [t for t in rj.skey.split()[1:] if t not in STREET_STOP]
                sa, sb = "".join(ta), "".join(tb)
                shared = {t for t in ta if t.isalpha() and len(t) >= 3} & {t for t in tb if t.isalpha() and len(t) >= 3}
                if (shared or (min(len(sa), len(sb)) >= 3 and (sa in sb or sb in sa))) and \
                        name_compat(ri.nm, rj.nm) in FIRM:
                    link(i, j, "housenum_zip_name")

    def located(i):
        return rows[i].skey != "" and rows[i].grade == "plant"

    def comps_now():
        d = defaultdict(list)
        for r in rows:
            d[uf.find(r.idx)].append(r.idx)
        return d

    # phase 1c: weak-only clusters (no plant-grade street) with the same name in the same locality merge with each other
    comps = comps_now()
    weak_roots = [root for root, m in comps.items() if not any(located(i) for i in m)]
    wkey = defaultdict(set)
    for root in weak_roots:
        for i in comps[root]:
            r = rows[i]
            if r.state not in USPS:
                continue
            for nk, dtk in r.nm:
                if dtk:
                    if r.csq:
                        wkey[(r.state, "c", r.csq, nk)].add(root)
                    if r.zip5:
                        wkey[(r.state, "z", r.zip5, nk)].add(root)
    def has_street(root):
        return any(rows[i].skey for i in comps[root])

    for roots in wkey.values():
        roots = sorted(roots)
        for other in roots[1:]:
            # two HQ-grade clusters that each carry a real (and therefore different) street are NOT the same place
            if has_street(roots[0]) and has_street(other):
                not_merged["weak_both_have_street"] += 1
                continue
            link(roots[0], other, "weak_name_locality")

    # phase 2: attach each weak-only cluster to the ONE located cluster sharing EIN+locality or name+locality
    comps = comps_now()
    located_roots = {root for root, m in comps.items() if any(located(i) for i in m)}
    loc_name, loc_ein = defaultdict(set), defaultdict(set)
    for root in located_roots:
        for i in comps[root]:
            r = rows[i]
            if r.state not in USPS or r.grade != "plant":
                continue
            for nk, dtk in r.nm:
                if dtk:
                    if r.csq:
                        loc_name[(r.state, "c", r.csq, nk)].add(root)
                    if r.zip5:
                        loc_name[(r.state, "z", r.zip5, nk)].add(root)
            if r.ein and r.csq:
                loc_ein[(r.state, "c", r.csq, r.ein)].add(root)
            if r.ein and r.zip5:
                loc_ein[(r.state, "z", r.zip5, r.ein)].add(root)
    ambiguous, related_name = [], []
    for root in sorted(r_ for r_ in comps if r_ not in located_roots):
        cn, ce = set(), set()
        for i in comps[root]:
            r = rows[i]
            if r.state not in USPS:
                continue
            for nk, dtk in r.nm:
                if dtk:
                    if r.csq:
                        cn |= loc_name.get((r.state, "c", r.csq, nk), set())
                    if r.zip5:
                        cn |= loc_name.get((r.state, "z", r.zip5, nk), set())
            if r.ein and r.csq:
                ce |= loc_ein.get((r.state, "c", r.csq, r.ein), set())
            if r.ein and r.zip5:
                ce |= loc_ein.get((r.state, "z", r.zip5, r.ein), set())
        weak_streets = [rows[i].skey for i in comps[root] if rows[i].skey]
        if cn and weak_streets:
            # the weak cluster carries a real street that matched no plant street: a different address of the same employer
            # (HQ, second site). Not attached by name; reported through related_clusters.
            not_merged["name_attach_refused_street_differs"] += 1
            related_name.append((root, sorted(cn), "same_name_other_street"))
            cn = set()
        if ce and weak_streets:
            # EIN + city is only a weak-street attach when the streets are compatible (same house number or a shared street word);
            # an employer's HQ address in the same city as one of its plants is not that plant
            def street_compat(tgt):
                for j in comps[tgt]:
                    rj = rows[j]
                    if not (rj.skey and rj.grade == "plant"):
                        continue
                    tj = {t for t in rj.skey.split()[1:] if t.isalpha() and len(t) >= 3 and t not in STREET_STOP}
                    for sk in weak_streets:
                        if sk.split()[0] == rj.skey.split()[0]:
                            return True
                        if tj & {t for t in sk.split()[1:] if t.isalpha() and len(t) >= 3 and t not in STREET_STOP}:
                            return True
                return False
            keep = {t for t in ce if street_compat(t)}
            if len(keep) < len(ce):
                not_merged["ein_attach_refused_street_differs"] += 1
                related_name.append((root, sorted(ce - keep), "same_ein_other_street"))
            ce = keep
        cands = cn | ce
        if len(cands) == 1:
            tgt = next(iter(cands))
            basis = "ein_locality" if ce and not cn else ("name_locality" if cn and not ce else "ein+name_locality")
            link(tgt, root, basis)
        elif len(cands) > 1:
            ambiguous.append((root, sorted(cands)))
    stats["blocked_street_name_differs"] = len(blocked)
    stats["ambiguous_weak_attach"] = len(ambiguous)
    stats["edge_unions"] = dict(edges)
    stats["not_merged"] = dict(not_merged)
    members = defaultdict(list)
    for r in rows:
        members[uf.find(r.idx)].append(r.idx)
    return members, row_bases, blocked, ambiguous, related_name


# ------------------------------------------------------------------ Atlas indexes (current data/)
class AtlasIdx:
    def __init__(self):
        self.tables = atlas.load_tables(DATA)
        self.orgs = {}
        for tn in ("organizations", "ecosystem"):
            for r in self.tables.get(tn, atlas.Table(tn)).rows:
                self.orgs[r["org_id"]] = r
        self.sites = self.tables["sites"].rows
        self.org_sites = defaultdict(list)
        self.by_street_col, self.by_street_any = defaultdict(list), defaultdict(list)
        for s in self.sites:
            self.org_sites[s["org_id"]].append(s)
            col = atlas.street_key(s.get("street_address", ""))
            s["__skey_col"] = col
            s["__skey"] = col or atlas.street_key(street_from_notes(s.get("notes", ""), s.get("city", "")))
            s["__zip5"] = zip5(s.get("zip", ""))
            s["__csq"] = atlas.squash(s.get("city", ""))
            if col:
                self.by_street_col[col].append(s)
            if s["__skey"]:
                self.by_street_any[s["__skey"]].append(s)
        self.namekey_orgs = defaultdict(set)
        for oid, r in self.orgs.items():
            for nm in [r.get("legal_name", "")] + atlas.tokens_semicolon(r.get("trade_names")):
                k = atlas.name_key(nm)
                if k:
                    self.namekey_orgs[k].add(oid)
        self.org_states = defaultdict(set)
        for oid, r in self.orgs.items():
            st = (r.get("hq_state") or r.get("state") or "").upper()
            if st:
                self.org_states[oid].add(st)
        for s in self.sites:
            if s.get("state"):
                self.org_states[s["org_id"]].add(s["state"].upper())
        # EIN -> orgs, only through the packets' own MATCH rows (an EIN seen only in this project's files mints nothing)
        self.ein_orgs = defaultdict(set)
        for m in rd(os.path.join(P_ITA, "site_matches.csv")):
            if m["verdict"] == "MATCH_SITE" and m["org_id"] and m["ein_quality"] in ("ok", "zero_padded") and m["ein"]:
                self.ein_orgs[m["ein"]].add(m["org_id"])
        for m in rd(os.path.join(P_F55, "matches.csv")):
            if m["match_class"] in ("MATCH_ORG", "MATCH_SITE") and m["org_id"]:
                self.ein_orgs[m["ein"]].add(m["org_id"])
        # TRIFIDs: verified bases drop; fuzzy bases are flag-only
        self.trifid_strong, self.trifid_fuzzy = {}, {}
        for r in self.tables["registry_links"].rows:
            if r["registry"] == "TRI_TRIFID":
                (self.trifid_fuzzy if "fuzzy" in r["match_basis"] else self.trifid_strong)[r["registry_id"]] = r["org_id"]
        self.notes_hits = {}

    def status(self, oid):
        return (self.orgs.get(oid, {}).get("status") or "").lower()

    def org_names(self, oid):
        r = self.orgs.get(oid, {})
        return [r.get("legal_name", "")] + atlas.tokens_semicolon(r.get("trade_names"))

    def build_notes_index(self, needles):
        """AGENTS 3 step 4 (flag only): which orgs mention a needle in legal/trade names or notes. One pass over org text."""
        first = defaultdict(set)
        for nd in needles:
            first[nd[0]].add(nd)
        hits = defaultdict(set)
        for oid, r in self.orgs.items():
            words = atlas.squash(" ".join([r.get("legal_name", ""), r.get("trade_names", ""), r.get("notes", "")])).split()
            for p, w in enumerate(words):
                for nd in first.get(w, ()):
                    if tuple(words[p:p + len(nd)]) == nd:
                        hits[nd].add(oid)
        self.notes_hits = hits


def locality_equal(r, s):
    return bool((r.zip5 and s["__zip5"] and r.zip5 == s["__zip5"]) or (r.csq and r.csq == s["__csq"]))


def names_agree_with_site(cl_names, atl, s):
    core = re.split(r"\s+[—-]\s+", s.get("site_name", ""))[0]
    cand = [(atlas.name_key(s.get("site_name", "")), dist_tokens(s.get("site_name", ""))), (atlas.name_key(core), dist_tokens(core))]
    for nm in atl.org_names(s["org_id"]):
        cand.append((atlas.name_key(nm), dist_tokens(nm)))
    return bool(name_compat(cl_names, [c for c in cand if c[0]]))


def recheck_cluster(rows_c, atl):
    """Re-run AGENTS 3 (name, street, trade names/successors) against the current Atlas for one cluster.
    Returns (drop_reasons [(reason, detail)], flags, refs)."""
    drops, flags, refs = [], [], []
    state = rows_c[0].state
    cl_names = []
    for r in rows_c:
        cl_names += r.nm
    plant_sk = {r.skey for r in rows_c if r.skey and r.grade == "plant"}
    sks = plant_sk or {r.skey for r in rows_c if r.skey}
    # ---- street (step 3)
    for sk in sorted(sks):
        for s in atl.by_street_any.get(sk, []):
            if (s.get("state") or "").upper() != state:
                continue
            rr = [r for r in rows_c if r.skey == sk]
            if not any(locality_equal(r, s) for r in rr):
                flags.append("STREET_MATCH_LOCALITY_DIFFERS")
                refs.append(s["site_id"])
            elif names_agree_with_site(cl_names, atl, s):
                drops.append(("held_site_street_name", f"{s['site_id']} ({s['org_id']})"))
            else:
                flags.append("COTENANT_AT_HELD_SITE")
                refs.append(s["site_id"])
    # ---- name (step 2) / EIN / TRIFID -> candidate orgs, judged at SITE level in the same locality
    org_cands = {}
    for k in {k for k, _ in cl_names}:
        for oid in atl.namekey_orgs.get(k, ()):
            if state in atl.org_states.get(oid, ()):
                org_cands.setdefault(oid, set()).add("name")
    for r in rows_c:
        if r.ein:
            for oid in atl.ein_orgs.get(r.ein, ()):
                if state in atl.org_states.get(oid, ()):
                    org_cands.setdefault(oid, set()).add("ein")
        if r.family == "ECHO":
            for t in r.x.get("tri_ids", []):
                if t in atl.trifid_strong:
                    drops.append(("held_trifid_verified", f"{t} -> {atl.trifid_strong[t]}"))
                elif t in atl.trifid_fuzzy:
                    flags.append("TRIFID_FUZZY_HELD_ORG")
                    refs.append(atl.trifid_fuzzy[t])
    for oid, how in sorted(org_cands.items()):
        tag = "+".join(sorted(how))
        local = [s for s in atl.org_sites.get(oid, [])
                 if (s.get("state") or "").upper() == state and any(locality_equal(r, s) for r in rows_c)]
        unknown = [s for s in local if not s["__skey"]]
        equal = [s for s in local if s["__skey"] and s["__skey"] in sks]
        if unknown or equal:
            s = (equal or unknown)[0]
            drops.append((f"held_org_{tag}_local_site",
                          f"{oid} {atl.orgs[oid].get('legal_name', '')} / {s['site_id']}{'' if equal else ' (site street unknown)'}"))
        else:
            flags.append("HELD_ORG_NAME_OTHER_LOCATION" if "name" in how else "HELD_ORG_EIN_OTHER_LOCATION")
            refs.append(oid)
            if atl.status(oid) in ("closed", "acquired", "merged", "tombstoned", "idled"):
                flags.append("HELD_ORG_TOMBSTONED_OR_CLOSED")
    # ---- step 4 (flag only): a held org's trade names / notes mention this name
    for k in {k for k, _ in cl_names}:
        for oid in atl.notes_hits.get(tuple(k.split()), ()):
            if oid not in org_cands and state in atl.org_states.get(oid, ()):
                flags.append("NOTES_OR_TRADE_NAME_MENTION")
                refs.append(oid)
    return drops, sorted(set(flags)), sorted(set(refs))


# ------------------------------------------------------------------ cluster summaries and scoring
def cluster_summary(c_rows):
    fams_nm = sorted({r.family for r in c_rows if r.verdict == "NO_MATCH"}, key=FAMILIES.index)
    fams_pos = sorted({r.family for r in c_rows if r.verdict == "POSSIBLE"} - set(fams_nm), key=FAMILIES.index)
    kc = Counter()
    for r in c_rows:
        for k in set(r.nks):
            kc[k] += 1
    best = ""
    if kc:
        top = max(kc.values())
        topkeys = {k for k, v in kc.items() if v == top}
        for fam in NAME_PRIORITY:
            for r in c_rows:
                if r.family == fam and not best:
                    for n in r.names:
                        if atlas.name_key(n) in topkeys:
                            best = n
                            break
    best = best or (c_rows[0].names[0] if c_rows[0].names else "")
    variants = []
    for r in c_rows:
        for n in r.names:
            if atlas.name_key(n) != atlas.name_key(best) and n not in variants:
                variants.append(n)
    # address: a plant-grade street first (ADDR_PRIORITY), then any street, then any city
    addr = None
    for pool in ([r for r in c_rows if r.skey and r.grade == "plant"], [r for r in c_rows if r.skey], [r for r in c_rows if r.city], c_rows):
        if pool:
            addr = sorted(pool, key=lambda r: (ADDR_PRIORITY.index(r.family), r.sid))[0]
            break
    ec = next((r.x["county"] for r in c_rows if r.family == "ECHO" and r.x.get("county")), "")
    pc = next((r.x["county"] for r in c_rows if r.family == "PATENT" and r.x.get("county")), "")
    county = ec.title() if ec else pc
    county_src = "ECHO FRS county (orientation only)" if ec else ("PatentsView assignee county (orientation only)" if pc else "")
    eins = sorted({r.ein for r in c_rows if r.ein})
    naics = []
    for r in c_rows:
        for c in r.naics:
            if c not in naics:
                naics.append(c)
    fam_core = sorted({r.family for r in c_rows if r.core and r.verdict == "NO_MATCH"}, key=FAMILIES.index)
    prefixes = defaultdict(set)
    for r in c_rows:
        if r.core and r.verdict == "NO_MATCH":
            for c in r.naics:
                if is_core(c) and c != "325920":
                    prefixes[c[:4]].add(r.family)
    concord = any(len(v) >= 2 for v in prefixes.values())
    size_band, size_basis = "", ""
    for fam in ("ITA", "OSHA", "F5500"):
        cand = [r for r in c_rows if r.family == fam and r.size_band]
        if cand:
            r = max(cand, key=lambda x: BAND_ORDER[x.size_band])
            size_band, size_basis = r.size_band, f"{fam}: {r.size_kind}"
            break
    size_by_src = ";".join(f"{r.family}={r.size_band}" for r in c_rows if r.size_band)
    dated = [(r.date, r.family) for r in c_rows if r.date]
    latest, latest_src = (max(dated) if dated else (None, ""))
    return {"fams_nm": fams_nm, "fams_pos": fams_pos, "best": best, "variants": variants, "addr": addr, "county": county,
            "county_src": county_src, "eins": eins, "naics": naics, "fam_core": fam_core, "concord": concord,
            "size_band": size_band, "size_basis": size_basis, "size_by_src": size_by_src, "latest": latest,
            "latest_src": latest_src}


def score_cluster(sm, c_rows, as_of):
    n_src = len(sm["fams_nm"])
    n_ag = len({AGENCY[f] for f in sm["fams_nm"]})
    s = 10 * n_src + 4 * n_ag + 3 * len(sm["fam_core"]) + (2 if sm["concord"] else 0)
    if sm["latest"]:
        age = (as_of - sm["latest"]).days
        s += 3 if age <= 365 else 2 if age <= 1095 else 1 if age <= 1826 else 0
    s += {"250-499": 3, "500-999": 3, "1000-4999": 3, "5000+": 3, "100-249": 2, "50-99": 1}.get(sm["size_band"], 0)
    pen = 0
    if sm["fams_pos"] or any(r.verdict == "POSSIBLE" for r in c_rows):
        pen += 3
    if any(r.x325920 for r in c_rows) and not any(r.core for r in c_rows):
        pen += 5
    nm_rows = [r for r in c_rows if r.verdict == "NO_MATCH"]
    if not any(GRADE[f] == "plant" for f in sm["fams_nm"]):
        pen += 4  # only HQ-grade sources (Form 5500, USAspending, patents): no plant-grade address confirms an establishment
    if n_src == 1 and any(r.family == "ECHO" and r.x.get("noise") == "Y" for r in nm_rows):
        pen += 3
    return s - pen, n_ag


def eligibility(c_rows):
    """Polymer-lead eligibility of a cluster, judged on its NO_MATCH rows only."""
    nm = [r for r in c_rows if r.verdict == "NO_MATCH"]
    if not nm:
        return "possible_only"
    if any(r.core for r in nm):
        return "core"
    if any(r.ring3 for r in nm):
        return "ring3_primary"
    if any(r.family == "PATENT" for r in nm):
        return "patent_cpc_only"
    if any(r.x325920 for r in nm):
        return "explosives_325920_only"
    return "out_of_core_naics"


def cls_of(n):
    return "STRONG" if n >= 3 else "CORROBORATED" if n == 2 else "SINGLE"


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def fmt_audit(cid, c_rows, bases, fp=""):
    out = [f"{cid} [{fp}]  rows={len(c_rows)} families={','.join(sorted({r.family for r in c_rows}, key=FAMILIES.index))} "
           f"edge_bases={','.join(sorted(bases)) or 'single'}"]
    for r in sorted(c_rows, key=lambda x: (FAMILIES.index(x.family), x.sid)):
        out.append(f"  {r.family:8s} {r.sid[:16]:16s} | {' / '.join(r.names)[:64]} | {r.street[:36]} | {r.city}, {r.state} {r.zip5} "
                   f"| naics {','.join(r.naics[:3])} | ein {r.ein or '-'} | {r.verdict}")
    return "\n".join(out)


# Hand review of the 30-cluster random sample and the 40-cluster stratified supplement: fingerprint -> (OK | DOUBTFUL | FALSE, note).
AUDIT_VERDICTS = {  # keyed by cluster fingerprint (sha1 of member row keys, first 8 hex)
    'e15009e0': ('OK', "'2760-B' vs 'Suite B': one address."),
    'b8517f5b': ('OK', ''),
    '2bb7a223': ('OK', ''),
    'ce6a8169': ('OK', ''),
    'b7e12718': ('OK', 'Decker Packaging / Decker Plastics at one address (a name change at one plant, not two plants).'),
    'b280902e': ('OK', ''),
    'e50daef7': ('OK', ''),
    '9f0343f5': ('OK', 'Westwego / Waggaman postal names, same street and ZIP.'),
    '7017b98b': ('OK', ''),
    '0388adb0': ('OK', "Two ITA filings at one address (a 'West St' label on the second)."),
    '1d11a356': ('OK', 'Baltimore / Curtis Bay postal names, same street and ZIP.'),
    'ac53df13': ('OK', ''),
    'e0079bd0': ('OK', ''),
    'be818d62': ('OK', ''),
    '10b3a910': ('OK', ''),
    'bcbb7b72': ('OK', ''),
    '829efa2b': ('OK', ''),
    'aca246c5': ('OK', "ITA 'HQ Facility' label; Form 5500 sponsor at the same street."),
    'c7347cc1': ('OK', ''),
    '411dc8ce': ('OK', ''),
    '00dcba43': ('OK', ''),
    '943cef0e': ('OK', ''),
    'db340bb5': ('OK', ''),
    '1e3990b1': ('OK', ''),
    '01e042be': ('OK', ''),
    '280a4bac': ('OK', ''),
    'ff281869': ('OK', ''),
    '724078db': ('OK', 'Utah grid address written 216 N 700 W vs 216 W 700 N (transposed), same building and bay.'),
    '426a1670': ('OK', ''),
    '4fb3afb6': ('OK', ''),
    '653657b2': ('OK', ''),
    'ede2a496': ('OK', "'Capital' vs 'Capitol' Way; Sika acquired United Gilsonite (one plant)."),
    '738e0bc5': ('OK', ''),
    'dff91565': ('OK', ''),
    '512cbe01': ('OK', ''),
    '511d16f3': ('OK', ''),
    '710a2b15': ('OK', ''),
    '64e3110a': ('OK', ''),
    'bdc62d50': ('OK', ''),
    'bea3b0d3': ('OK', 'Millwork & Panel / CertainTeed (owner) at one address.'),
    'a80e7b4f': ('OK', ''),
    'e0a1472c': ('OK', ''),
    '3abdab36': ('OK', ''),
    '85d8e201': ('OK', ''),
    '5a2edb75': ('OK', ''),
    'e8f88e5d': ('OK', 'Goodyear service centre: two ITA labels plus an OSHA inspection record at one address.'),
    '152680f8': ('OK', ''),
    'bd698dfb': ('OK', 'Two Form 5500 EINs (both POSSIBLE rows) under one Vernay entity; one plant.'),
    'f9885546': ('OK', ''),
    '85f3eccd': ('OK', ''),
    '913a2a9a': ('OK', ''),
    '1e43cec6': ('OK', "'1347 Michigan M89' vs '1347 M 89': one address."),
    'cbdfbed5': ('OK', ''),
    '9a5f3bdc': ('OK', ''),
    '0b0b3d4e': ('OK', ''),
    '91b4a97e': ('OK', '3945 vs 3855 Swenson Ave: same company, street and EIN; plausibly one campus.'),
    'd6dd08e9': ('OK', ''),
    '44e5dc64': ('OK', 'Cryopak (ITA) and its parent Integreon Global (Form 5500 sponsor) share EIN and street.'),
    '24c19b1c': ('OK', ''),
    'be591fa9': ('OK', ''),
    '91823e60': ('OK', ''),
    '377476dc': ('OK', ''),
    'd58502dd': ('DOUBTFUL', '4099 vs 4133 S Dort Hwy, Burton: same company and road, different house numbers; attached on name + city only.'),
    'daaee7df': ('OK', 'HQ-grade evidence only (USAspending SAM address and a patent assignee city).'),
    '05d248b9': ('OK', 'Km 25.4 on PR-15 in all three rows.'),
    'e85ac39d': ('DOUBTFUL', 'Rural-route and km-marker addresses in Dorado PR on both sides; no comparable street key.'),
    'ea0c33a3': ('OK', 'Km 0.6 on PR-402 in all three rows.'),
    '87911678': ('OK', ''),
    'f9946c32': ('OK', ''),
    '44184384': ('OK', 'ITA is a chemical distributor (424690), ECHO carries 325998; same plant road in Nitro.'),
}
AUDIT_NOTES = {
    "cross": ("**Reading of the cross-check.** The ITA packet's published figures reproduce exactly from its own file (1,003 BOTH_SOURCES, 138 BOTH_ADDRESS_NAME_DIFFERS, 3,235 ITA_ONLY), so there is no count error to chase. "
              "The fusion's ITA-OSHA overlaps differ from the packet's because the two use different join rules, and the differences have identified causes. "
              "(i) The fusion is looser on address spelling: its house-number + ZIP5 + shared-street-word edge and its same-street-same-city edge that tolerates a ZIP5 disagreement join rows the ITA ladder left as ITA_ONLY "
              "('Dr' vs 'Ave', 'N' vs 'S' Van Dyke, '4378 South M-18' vs '4378 M18', a mistyped ZIP). I read 28 of these joins by hand during development (14 ITA_ONLY and 14 BOTH_ADDRESS_NAME_DIFFERS): all were one address and one company. "
              "(ii) The fusion is stricter on names where the street is equal: the ITA packet counts a pair as BOTH_SOURCES on a street match plus agreement on either of ITA's two name fields, while the fusion needs "
              "a compatible name among all name variants of both rows; the 12 BOTH_SOURCES rows it does not join are same-address rows under incompatible names (Amcor / Berry Global, USG / United States Gypsum, "
              "Return Polymers / Butler-MacDonald, Zip-Pak / ITW with a ZIP typo ...), which are kept apart and cross-referenced in `related_clusters` (`colocated_other_name:`). "
              "(iii) Six BOTH_SOURCES rows differ in street form beyond the merge rules (for example a street written only as a PO box, or `#6 Capper Drive`, which `atlas.street_key` strips to nothing). "
              "Net: ITA core_P NO_MATCH rows that share a cluster with an OSHA NO_MATCH row are higher in the fusion than the packet's 1,003 plus 138; the extra joins are explained by (i), the shortfall by (ii) and (iii). Nothing was explained away: each class has a count above."),
    "blocked": ("Of these 14 blocked pairs, my reading is that roughly 8 are one establishment under a successor, parent or brand name (Alto Ingredients / Williams Ethanol Services at the Pekin plant, Spartech / PolyOne, "
                "JM Eagle / PW Eagle, PRET Advanced Materials / Wellman Plastics Recycling, Champion X / Nalco Champion, Chem-Aqua / NCH, American Plastics / Vinylex, TG Missouri) and roughly 6 are "
                "unrelated co-tenants (Compliance Staffing / Turnstone, Clean Earth / Sedgwick, Acrylic Source / All Source Plus, Enstall / PanelClaw, FRX Polymers / Triton Systems, U.S. Smokeless Tobacco / Philip Morris). "
                "That is the price of the name guard: it forgoes some true same-establishment merges (those lose a family and rank lower) to avoid fusing co-tenants. The pairs are not lost: they are listed in each cluster's "
                "`related_clusters`. (The TG Missouri pair was a normalizer gap, 'T G' vs 'TG', fixed by the no-space name rule in this run, so it no longer appears blocked.)"),
}
ARGS = None


# ------------------------------------------------------------------ main
def main(argv=None):
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default="2026-11-01")
    ap.add_argument("--dump-dropped", default="")
    ap.add_argument("--audit-print", action="store_true")
    ap.add_argument("--selftest", type=int, default=200)
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    ARGS = a
    as_of = dt.date.fromisoformat(a.as_of)
    stats = {}

    rows = load_sources(stats)
    nrows_in = Counter((r.family, r.verdict) for r in rows)
    held_rows = [r for r in rows if r.state not in USPS]
    stats["held_no_state"] = Counter((r.family, r.verdict) for r in held_rows)
    cl_rows = [r for r in rows if r.state in USPS]
    for i, r in enumerate(cl_rows):
        r.idx = i
    members, row_bases, blocked, ambiguous, related_name = cluster_rows(cl_rows, stats)

    # ---- cluster ids (unique, deterministic)
    comps = [sorted((cl_rows[i] for i in idxs), key=lambda r: r.key) for idxs in members.values()]
    comps.sort(key=lambda c: (c[0].state, c[0].key))
    seq, cid_of, cluster_list = Counter(), {}, []
    for c in comps:
        st = c[0].state
        assert all(r.state == st for r in c), "cluster crosses states"
        seq[st] += 1
        cid = f"LF-{st}-{seq[st]:05d}"
        cluster_list.append((cid, c))
        for r in c:
            cid_of[r.key] = cid
    assert len({cid for cid, _ in cluster_list}) == len(cluster_list), "cluster ids not unique"
    assert sum(len(c) for _, c in cluster_list) == len(cl_rows) == len(cid_of), "rows lost or duplicated"
    cl_by_cid = dict(cluster_list)
    stats["clusters_raw"] = len(cluster_list)
    bases_by_cluster = defaultdict(set)
    for r in cl_rows:
        bases_by_cluster[cid_of[r.key]] |= row_bases.get(r.idx, set())
    colocated = defaultdict(set)   # cluster id -> other clusters at the same street whose names are incompatible (not merged)
    for basis, i, j in blocked:
        ci, cj = cid_of[cl_rows[i].key], cid_of[cl_rows[j].key]
        if ci != cj:
            colocated[ci].add(cj)
            colocated[cj].add(ci)
    same_name_other = defaultdict(set)  # weak (HQ-grade / street-differs) cluster <-> plant cluster of the same name in the same locality
    for root, cands, tag in related_name:
        c1 = cid_of[cl_rows[root].key]
        for rt in cands:
            c2 = cid_of[cl_rows[rt].key]
            if c1 != c2:
                same_name_other[c1].add(f"{tag}:{c2}")
                same_name_other[c2].add(f"{tag}:{c1}")
    size_dist = Counter(len(c) for _, c in cluster_list)
    fam_dist = Counter(len({r.family for r in c}) for _, c in cluster_list)

    # ---- Atlas recheck
    atl = AtlasIdx()
    needles = set()
    for _, c in cluster_list:
        for r in c:
            for k in r.nks:
                nd = tuple(k.split())
                if len(nd) >= 2 or (len(nd) == 1 and len(nd[0]) >= 6 and nd[0] not in GENERIC):
                    needles.add(nd)
    atl.build_notes_index(needles)

    stats["atlas"] = (len(atl.orgs), len(atl.sites), sum(1 for x in atl.sites if x["__skey_col"]), sum(1 for x in atl.sites if x["__skey"]))
    mism = {"name": 0, "street": 0}
    tested = 0
    if a.selftest:
        rng = random.Random(7)
        for cid, c in rng.sample(cluster_list, min(a.selftest, len(cluster_list))):
            r0 = next((r for r in c if r.skey), c[0])
            nm0 = r0.names[0] if r0.names else ""
            d = atlas.dedupe(atl.tables, name=nm0 or None, street=r0.street or None, city=r0.city, state=r0.state, zip_=r0.zip5)
            s2 = {h["id"] for h in d["steps"][1]["hits"]}
            mine2 = set(atl.namekey_orgs.get(atlas.name_key(nm0), set())) if nm0 else set()
            s3 = {h["id"] for h in d["steps"][2]["hits"]} | {h["id"] for h in d["steps"][2]["other_localities"]}
            sk = atlas.street_key(r0.street)
            mine3 = {s["site_id"] for s in atl.by_street_col.get(sk, [])} if sk else set()
            tested += 1
            mism["name"] += s2 != mine2
            mism["street"] += s3 != mine3
        assert mism["name"] == 0 and mism["street"] == 0, f"indexed re-check disagrees with atlas.dedupe: {mism}"
    stats["selftest"] = (tested, mism)

    dropped, dropped_rows, dropped_examples, dropped_list, kept = Counter(), Counter(), defaultdict(list), [], []
    for cid, c in cluster_list:
        elig = eligibility(c)
        drops, flags, refs = recheck_cluster(c, atl)
        if drops:
            reason = drops[0][0]
            dropped[reason] += 1
            dropped_rows[reason] += len(c)
            if len(dropped_examples[reason]) < 6:
                dropped_examples[reason].append((cid, c[0].names[0] if c[0].names else "", c[0].city, c[0].state, drops[0][1],
                                                 sorted({r.family for r in c}, key=FAMILIES.index)))
            dropped_list.append((cid, elig, drops, c))
            continue
        kept.append((cid, c, elig, flags, refs))
    elig_ct = Counter(e for _, _, e, _, _ in kept)
    out_rows, excluded = [], defaultdict(list)
    for cid, c, elig, flags, refs in kept:
        if elig in ("core", "ring3_primary", "patent_cpc_only"):
            out_rows.append((cid, c, elig, flags, refs))
        else:
            excluded[elig].append((cid, c))
    stats["excluded"] = {k: (len(v), sum(len(c) for _, c in v)) for k, v in excluded.items()}

    # ---- output records
    recs = []
    for cid, c, elig, flags, refs in out_rows:
        sm = cluster_summary(c)
        score, n_ag = score_cluster(sm, c, as_of)
        n_src = len(sm["fams_nm"])
        ad = sm["addr"]
        srcs = ";".join(f"{r.family}:{r.sid}{'(POSSIBLE)' if r.verdict == 'POSSIBLE' else ''}"
                        for r in sorted(c, key=lambda x: (FAMILIES.index(x.family), x.sid)))
        rel = "NET_NEW"
        if "HELD_ORG_NAME_OTHER_LOCATION" in flags or "HELD_ORG_EIN_OTHER_LOCATION" in flags:
            rel = "HELD_ORG_OTHER_LOCATION"
        elif "COTENANT_AT_HELD_SITE" in flags or "STREET_MATCH_LOCALITY_DIFFERS" in flags:
            rel = "ADDRESS_AT_HELD_SITE_NAME_DIFFERS"
        sf = []
        if elig == "ring3_primary":
            sf.append("ring3_primary_only")
        if elig == "patent_cpc_only":
            sf.append("patent_cpc_only_no_naics")
        if any(r.x325920 for r in c):
            sf.append("has_325920_explosives_code")
        if any(r.family == "ECHO" and r.x.get("noise") == "Y" for r in c):
            sf.append("echo_name_noise_hint")
        if any(r.family == "F5500" and r.core for r in c) and not any(r.family != "F5500" and r.core for r in c):
            sf.append("naics_only_from_form5500_padded_code")
        if not any(GRADE[f] == "plant" for f in sm["fams_nm"]):
            sf.append("hq_grade_sources_only")
        if any(r.family == "USASPEND" for r in c):
            sf.append("usaspending_address_is_SAM_registered")
        if any(r.family == "F5500" for r in c):
            sf.append("form5500_is_employer_level")
        if any(r.family == "F5500" and r.x.get("street_withheld") for r in c):
            sf.append("form5500_street_withheld_privacy_possible_individual")
        if len({r.skey for r in c if r.skey and r.grade == "plant"}) > 1:
            sf.append("multiple_plant_street_keys")
        recs.append({
            "cluster_id": cid, "best_name": sm["best"], "name_variants": " | ".join(sm["variants"][:6]),
            "street": ad.street, "city": ad.city, "state": ad.state,
            "zip5": ad.zip5 or next((r.zip5 for r in c if r.zip5), ""), "county": sm["county"], "county_source": sm["county_src"],
            "n_sources": n_src, "n_agencies": n_ag, "n_plant_grade_families": len([f for f in sm["fams_nm"] if GRADE[f] == "plant"]),
            "source_families": ";".join(sm["fams_nm"]),
            "possible_only_families": ";".join(sm["fams_pos"]), "sources_with_ids": srcs, "eins": ";".join(sm["eins"]),
            "naics_set": ";".join(sm["naics"][:10]), "core_naics_families": len(sm["fam_core"]),
            "core_naics_4digit_concordant": "Y" if sm["concord"] else "N", "size_band": sm["size_band"],
            "size_basis": sm["size_basis"], "size_by_source": sm["size_by_src"],
            "latest_activity": sm["latest"].isoformat() if sm["latest"] else "", "latest_activity_source": sm["latest_src"],
            "score": score, "class": cls_of(n_src), "scope_class": elig, "atlas_relation": rel,
            "atlas_flags": ";".join(flags), "atlas_refs": ";".join(refs[:6]), "scope_flags": ";".join(sf),
            "related_clusters": ";".join([f"colocated_other_name:{x}" for x in sorted(colocated.get(cid, set()))[:3]] +
                                         sorted(same_name_other.get(cid, set()))[:3]),
            "cluster_basis": ";".join(sorted(bases_by_cluster[cid])) or "single_row", "n_rows": len(c), "_rows": c,
            "_fp": hashlib.sha1("|".join(sorted(r.key for r in c)).encode()).hexdigest()[:8]})

    def sortkey(r):
        d = int(r["latest_activity"].replace("-", "")) if r["latest_activity"] else 0
        return (-r["score"], -r["n_sources"], -BAND_ORDER.get(r["size_band"], -1), -d, r["cluster_id"])
    recs.sort(key=sortkey)
    cols = ["cluster_id", "best_name", "name_variants", "street", "city", "state", "zip5", "county", "county_source", "n_sources",
            "n_agencies", "n_plant_grade_families", "source_families", "possible_only_families", "sources_with_ids", "eins", "naics_set",
            "core_naics_families", "core_naics_4digit_concordant", "size_band", "size_basis", "size_by_source", "latest_activity",
            "latest_activity_source", "score", "class", "scope_class", "atlas_relation", "atlas_flags", "atlas_refs",
            "scope_flags", "related_clusters", "cluster_basis", "n_rows"]
    by_state = defaultdict(list)
    for r in recs:
        by_state[r["state"]].append(r)

    if not a.no_write:
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, "clusters.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
            w.writeheader()
            w.writerows(recs)
        with open(os.path.join(OUT, "top_leads_by_state.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["state_rank"] + cols, extrasaction="ignore", lineterminator="\n")
            w.writeheader()
            for st in TOP_STATES:
                for i, r in enumerate(by_state.get(st, [])[:50], 1):
                    w.writerow({"state_rank": i, **r})
    if a.dump_dropped:
        with open(a.dump_dropped, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["cluster_id", "eligibility", "reason", "detail", "families", "names", "street", "city", "state"])
            for cid, elig, drops, c in dropped_list:
                w.writerow([cid, elig, drops[0][0], drops[0][1], ";".join(sorted({r.family for r in c})),
                            " / ".join(c[0].names), c[0].street, c[0].city, c[0].state])

    # audit draws are ordered by a content fingerprint (sha1 of the member row keys), so they stay stable when unrelated clusters change
    multi = sorted((r for r in recs if r["n_sources"] >= 2), key=lambda r: hashlib.sha1((r["_fp"] + "audit").encode()).hexdigest())
    audit = sorted(multi[:30], key=lambda r: r["cluster_id"])
    # supplementary stratified sample: the random sample is dominated by street_zip merges, so the weaker bases get their own draw
    strata = {"housenum_zip_name": ("housenum_zip_name",), "street_city_zip_differs": ("street_city_zip_differs",),
              "name_locality": ("name_locality",), "ein_locality": ("ein_locality", "ein+name_locality"),
              "weak_name_locality": ("weak_name_locality",)}
    strat_audit, strat_pop = [], {}
    pool_ids = {r["cluster_id"] for r in audit}
    for name, keys in strata.items():
        pop = [r for r in multi if any(k in r["cluster_basis"].split(";") for k in keys)]
        strat_pop[name] = len(pop)
        pick = sorted((r for r in pop if r["cluster_id"] not in pool_ids), key=lambda r: hashlib.sha1((r["_fp"] + name).encode()).hexdigest())
        for r in sorted(pick[:8], key=lambda r: r["cluster_id"]):
            strat_audit.append((name, r))
            pool_ids.add(r["cluster_id"])
    stats["strat_pop"] = strat_pop
    if a.audit_print:
        for r in audit:
            print(fmt_audit(r["cluster_id"], r["_rows"], bases_by_cluster[r["cluster_id"]], r["_fp"]))
            print()
        print("======== STRATIFIED")
        for name, r in strat_audit:
            print("[" + name + "] " + fmt_audit(r["cluster_id"], r["_rows"], bases_by_cluster[r["cluster_id"]], r["_fp"]))
            print()
    susp = 0
    for r in multi:
        c = r["_rows"]
        bad = False
        for x in c:
            others = [y for y in c if y.family != x.family]
            if others and not any(name_compat(x.nm, y.nm) for y in others):
                bad = True
        susp += bad
    stats["auto_suspect"] = (susp, len(multi))

    # ---- reconciliation numbers
    recon = {fam: (nrows_in[(fam, "NO_MATCH")], nrows_in[(fam, "POSSIBLE")], stats[f"{fam}_all_rows"]) for fam in FAMILIES}
    ita_core_p = [r for r in rows if r.family == "ITA" and r.verdict == "NO_MATCH" and r.x["scope_class"] == "core_P"]
    ita_cross = Counter(r.x["cross_source"] for r in ita_core_p)
    nm_fams = defaultdict(set)
    any_fams = defaultdict(set)
    for cid, c in cluster_list:
        for r in c:
            any_fams[cid].add(r.family)
            if r.verdict == "NO_MATCH":
                nm_fams[cid].add(r.family)
    cross_nm, cross_any = Counter(), Counter()
    for r in ita_core_p:
        cid = cid_of.get(r.key)
        cross_nm[(r.x["cross_source"], "OSHA" in nm_fams.get(cid, set()))] += 1
        cross_any[(r.x["cross_source"], "OSHA" in any_fams.get(cid, set()))] += 1
    stats["ita_osha_cross"] = (len(ita_core_p), ita_cross, cross_nm, cross_any)
    # why the fusion and the ITA packet disagree, per row
    blocked_with_osha = defaultdict(int)
    for basis, i, j in blocked:
        for x, y in ((cl_rows[i], cl_rows[j]), (cl_rows[j], cl_rows[i])):
            if x.family == "ITA" and y.family == "OSHA":
                blocked_with_osha[x.key] += 1
    missed, extra_basis, nm_joined = Counter(), Counter(), Counter()
    for r in ita_core_p:
        cid = cid_of.get(r.key)
        has = "OSHA" in nm_fams.get(cid, set())
        cs = r.x["cross_source"]
        if cs == "BOTH_SOURCES" and not has:
            missed["same street, names incompatible (name guard)" if blocked_with_osha.get(r.key) else
                   "street / ZIP spelling beyond the merge rules, or no OSHA street key"] += 1
        elif cs != "BOTH_SOURCES" and has:
            bs = sorted(bases_by_cluster[cid] - {"weak_name_locality"}) or ["weak_name_locality"]
            extra_basis[(cs, bs[0] if len(bs) == 1 else "+".join(bs))] += 1
    stats["ita_cross_detail"] = (missed, extra_basis)
    stats["dropped"], stats["dropped_rows"] = dropped, dropped_rows
    stats["ita_rows"] = rows
    write_report(a, stats, recon, nrows_in, size_dist, fam_dist, cluster_list, kept, recs, elig_ct, excluded, dropped,
                 dropped_rows, dropped_examples, blocked, audit, strat_audit, bases_by_cluster, by_state, held_rows, cl_rows, rows)
    print(f"source rows in {len(rows)}; clustered {len(cl_rows)}; raw clusters {len(cluster_list)}; survivors {len(kept)}; "
          f"output leads {len(recs)}; classes {dict(Counter(r['class'] for r in recs))}")
    return 0


def write_report(a, stats, recon, nrows_in, size_dist, fam_dist, cluster_list, kept, recs, elig_ct, excluded, dropped,
                 dropped_rows, dropped_examples, blocked, audit, strat_audit, bases_by_cluster, by_state, held_rows, cl_rows, rows):
    if a.no_write:
        return
    L = []
    w = L.append
    cls = Counter(r["class"] for r in recs)
    n_rows_in = sum(nrows_in.values())
    w("# Lead fusion: polymer establishments not in the Atlas, ranked by independent federal sources - 2026-11-01\n")
    w("**Status: discovery-lead product, not Atlas data.** Packet lane output (AGENTS.md section 2 rule 7): nothing here edits `data/`, "
      "allocates an Atlas ID, sets a tier or changes a status. `cluster_id` values (`LF-<state>-<seq>`) are local keys of this run, never "
      "Atlas IDs. Built by `scripts/build_lead_fusion.py` (stdlib; deterministic; imports the normalizers and `dedupe` of `scripts/atlas.py`). "
      f"As-of date {a.as_of}.\n")
    w("**Every row is a lead only. It is not evidence that an establishment exists, operates or is in scope.** Several source families "
      "naming one address raises the odds that the establishment exists and operated; it proves nothing about ring, NAICS or scope "
      "(AGENTS section 4 evidence contract; SCHEMA 2.1: NAICS never decides a ring). Each lead still needs the full create path: "
      "website-domain dedupe (none of the six sources carries a domain, so AGENTS section 3 step 1 has NOT been run for any lead), name, "
      "street and trade-name dedupe on the integrator's own pass, primary-source existence and scope evidence rows (SCHEMA 4.13), "
      "tier U/C at birth, ring and scope rulings (owner rulings, AGENTS 2.9), and ID allocation above the tree-wide maximum by the integrator of record.\n")
    tot_nm = sum(recon[f][0] for f in FAMILIES)
    tot_po = sum(recon[f][1] for f in FAMILIES)
    k_r = Counter((AUDIT_VERDICTS.get(r["_fp"]) or ("UNREVIEWED", ""))[0] for r in audit)
    k_s = Counter((AUDIT_VERDICTS.get(r["_fp"]) or ("UNREVIEWED", ""))[0] for _, r in strat_audit)
    allok0 = all((PUBLISHED[f]["NO_MATCH"], PUBLISHED[f]["POSSIBLE"], PUBLISHED[f]["total"]) == recon[f] for f in FAMILIES)
    top_gap = ["CA", "TX", "FL", "MI", "IL", "GA", "IN", "WI", "NY", "NC"]
    st_strong = sorted(((sum(1 for r in lst if r["class"] == "STRONG"), st) for st, lst in by_state.items()), reverse=True)
    w("## Summary\n")
    w(f"- **Source rows in (unit: packet records, verdict NO_MATCH + POSSIBLE):** {tot_nm + tot_po:,} ({tot_nm:,} NO_MATCH + {tot_po:,} POSSIBLE) from six source families; {len(held_rows):,} with no US state are held, {len(cl_rows):,} clustered.")
    w(f"- **Clusters out (unit: candidate establishments):** {len(cluster_list):,} raw clusters; {sum(dropped.values()):,} dropped as already held in the current Atlas; {len(kept):,} survivors; "
      f"**{len(recs):,} polymer-lead clusters in `clusters.csv`**: **STRONG (>= 3 families) {cls.get('STRONG', 0):,}, CORROBORATED (2) {cls.get('CORROBORATED', 0):,}, SINGLE (1) {cls.get('SINGLE', 0):,}**.")
    w("- **STRONG clusters, top states (unit: clusters):** " + "; ".join(f"{st} {n}" for n, st in st_strong[:10]) + ". Among the ten QCEW-gap states: " +
      "; ".join(f"{st} {sum(1 for r in by_state.get(st, []) if r['class'] == 'STRONG')}" for st in top_gap) + f"; OH {sum(1 for r in by_state.get('OH', []) if r['class'] == 'STRONG')}, PA {sum(1 for r in by_state.get('PA', []) if r['class'] == 'STRONG')}.")
    w(f"- **Reconciliation (rule 10):** {'all six families reconcile exactly with the published NO_MATCH, POSSIBLE and total counts' if allok0 else 'MISMATCH, see section 3'}; the ITA-vs-OSHA overlap differs from the ITA packet's own figure for identified rule-level reasons (section 3).")
    w(f"- **Observed false-cluster rate:** {k_r['FALSE']} FALSE and {k_r['DOUBTFUL']} DOUBTFUL of {len(audit)} random multi-source clusters; stratified over the weaker merge bases {k_s['FALSE']} FALSE and {k_s['DOUBTFUL']} DOUBTFUL of {len(strat_audit)} (section 4).")
    w("- **Use:** verify STRONG clusters with a plant-grade family first; each still needs the full create path.\n")
    w("## 1. Method\n")
    w("**Inputs (rows with verdict NO_MATCH, and POSSIBLE carried separately).** Six source families, each read from its packet's match file "
      "joined to its row file: **ITA** (OSHA Form 300A CY2025, `tasks/osha-ita-2026-11-01`), **OSHA** inspections 2019+ "
      "(`osha-spine-2026-11-01`), **ECHO** (EPA ECHO/FRS active NAICS-scoped facilities, `echo-frs-spine-2026-11-01`), **F5500** (Form 5500 / 5500-SF sponsor EINs, "
      "`form5500-spine-2026-11-01`), **USASPEND** (USAspending contract recipients, the USAspending part of `federal-leads-2026-11-01`; the openFDA rows are not used), "
      "**PATENT** (PatentsView assignees, OH and PA only, `patents-pilot-2026-11-01`). Per row: name variants, street, city, state, ZIP5, NAICS codes, EIN "
      "(ITA and Form 5500 only; ITA EINs only when `ein_quality` is ok or zero_padded), a size input and the latest activity date.\n")
    w("| Family | Agency | Address grade | Size input | Activity date | NAICS input |\n|---|---|---|---|---|---|")
    w("| ITA | DOL-OSHA | plant (worksite) | annual average employees (establishment) | `date_submitted` of the CY2025 filing | employer-entered code |")
    w("| OSHA | DOL-OSHA | plant (inspected worksite) | `nr_in_estab` at the latest valid inspection | latest inspection open date | inspector-recorded, all codes seen |")
    w("| ECHO | EPA | plant (permit address) | none | `last_activity_date` | program-reported scope codes |")
    w("| F5500 | DOL-EBSA | HQ / mailing | active plan participants (employer level) | `latest_date_received` | filer-chosen padded group code (e.g. 326100) |")
    w("| USASPEND | USAspending/SAM | HQ / SAM-registered | none | none (obligations are a FY22-26 window, not a date) | award-level NAICS mix |")
    w("| PATENT | USPTO | HQ-grade, city only | none | last grant date | none (CPC C08/B29/C09J/C09D/B60C) |\n")
    w("**Not clustered, held (unit: source rows).** Rows whose state is blank or not a USPS code (foreign and no-state USAspending recipients; "
      "the AGENTS section 3 foreign-site rule: no lawful shard without an owner/schema ruling) are never clustered or scored: " +
      "; ".join(f"{k[0]} {k[1]} {v}" for k, v in sorted(stats["held_no_state"].items())) + f" (total {len(held_rows)}).\n")
    w("**Clustering** (never across states; union-find; cluster IDs asserted unique; every input row lands in exactly one cluster). Edges, in order:\n")
    w("1. **street + ZIP5** (strong): same normalized street (`atlas.street_key`; must start with a house number; PO boxes never keyed), same state, same ZIP5; "
      "or street + city when either side has no ZIP5. **Name guard:** the two rows' names must be compatible (equal normalized name; or the distinctive tokens - "
      "generic words such as plastics/industries/products removed - equal, nested, Jaccard >= 0.5 or equal first token; or near-identical spelling). "
      "A same-address pair with incompatible names is a co-tenant or rebrand (the Atlas's POSSIBLE class): it is **not merged** and is counted as blocked.")
    w("2. **house number + ZIP5 + a shared street word + a firm name match** (medium): catches street spelling variance across sources (`US-43` vs `US Hwy 43`).")
    w("3. **weak rows** (no usable street, or an HQ-grade source: Form 5500, USAspending, patents) are first merged with each other on the same normalized "
      "name + city or ZIP5 (refused when both sides carry a real, different street), then **attached to a located plant-grade cluster only when exactly one such cluster shares their EIN + city/ZIP5 "
      "(ITA <-> Form 5500) or their name + city/ZIP5 (name attach only when the weak row has no street of its own)**. When more than one candidate cluster exists the row is left unattached "
      "(ambiguous), and a weak row that carries a real street different from the plant's is a different address of the same employer: it stays its own cluster and is cross-referenced in `related_clusters` "
      "(`same_name_other_street:` or, for an EIN, `same_ein_other_street:`). An employer-level row must never fuse two plants of one company.")
    w("Deliberate deviation from the brief: the brief lists name + city + state as a medium rule. Applied to two plant-grade rows with *different* known streets it would "
      "merge two plants of one company (a second site is a second site, AGENTS section 3), so name + locality is used only where at least one side lacks a plant "
      "street (rule 3). EIN + city is likewise applied cross-family only (ITA <-> Form 5500): two ITA establishments with one EIN in one city are two establishments.\n")
    w(f"**Atlas snapshot used:** the working tree at run time: {stats['atlas'][0]:,} organization + ecosystem rows, {stats['atlas'][1]:,} site rows, {stats['atlas'][2]:,} with a `street_address` ({stats['atlas'][3]:,} with a usable street key counting the `Street...:` phrase in notes). "
      "The source packets matched against 5,773 site rows with 3,629 `street_address` values, so any address added to the Atlas since is caught here.\n")
    w("**Atlas re-check (the current `data/`, not the packets' snapshot).** Using `atlas.name_key` / `atlas.street_key` and the `atlas.dedupe` step logic, indexed "
      f"(self-tested against `atlas.dedupe()` on {stats['selftest'][0]} random clusters: {stats['selftest'][1]['name']} name-step and {stats['selftest'][1]['street']} street-step mismatches; "
      "the run aborts on any mismatch), a cluster is **dropped as already held** when: (a) a held site has the same street key in the same locality "
      "(street from `street_address`, else the `Street...:` phrase in notes) and a name that agrees with the site, its org or its trade names; (b) a held org whose normalized "
      "legal/trade name equals a cluster name, whose HQ or site states include the cluster state, holds a site in the same city/ZIP5 whose street is equal or unknown; (c) the same through an EIN "
      "that a packet tied to a held org (ITA MATCH_SITE rows, Form 5500 MATCH rows); (d) an ECHO tri_id equals a held `TRI_TRIFID` registry link with a verified (non-fuzzy) basis. "
      "Weaker hits **do not drop**; they are flags: `COTENANT_AT_HELD_SITE` (held site at this street, name differs), `STREET_MATCH_LOCALITY_DIFFERS`, "
      "`HELD_ORG_NAME_OTHER_LOCATION` / `HELD_ORG_EIN_OTHER_LOCATION` (a held org of this name or EIN has no site here: likely a new site of a held org), "
      "`TRIFID_FUZZY_HELD_ORG`, `NOTES_OR_TRADE_NAME_MENTION` (AGENTS section 3 step 4; flag only). "
      "`related_clusters` lists, without merging, other clusters at the same street under an incompatible name (`colocated_other_name:`; a co-tenant or a rebrand) and same-name / same-EIN clusters at a different street of the same city (`same_name_other_street:`, `same_ein_other_street:`).\n")
    w("**Scoring** (`score`, higher = more certain; each term is a column or derivable from one): "
      "`10 x n_sources` (distinct source families with a NO_MATCH row) `+ 4 x n_agencies` (ITA and OSHA are both DOL-OSHA, so they count as one agency) "
      "`+ 3 x` families whose NAICS is core polymer (3252/3255/3259/326, not 325920 alone) `+ 2` when two families agree on one 4-digit core prefix "
      "`+` recency of the latest dated activity (3 within 1 year of the as-of date, 2 within 3 years, 1 within 5 years) "
      "`+` size (3 for 250+, 2 for 100-249, 1 for 50-99; establishment-grain ITA first, then OSHA, then employer-level Form 5500) "
      "`- 4` if no plant-grade family (ITA, OSHA, ECHO) is among the sources (only HQ-grade Form 5500 / USAspending / patents: no worksite address confirms an establishment) "
      "`- 3` if any member row is a POSSIBLE (an Atlas candidate hit is unresolved) `- 5` if every coded row is 325920 explosives `- 3` for an ECHO name-noise hint on a single-source cluster. "
      "`class`: **STRONG** >= 3 families, **CORROBORATED** = 2, **SINGLE** = 1, counted over NO_MATCH rows only (a family that has only POSSIBLE rows is listed in `possible_only_families`, not counted). "
      "Independence caveat: ITA and OSHA inspections are different OSHA datasets (employer-filed vs compliance-officer record), and ITA/Form 5500 are both employer filings, "
      "so `n_agencies` sits beside `n_sources`; ITA and OSHA NAICS are both OSHA-channel codes (the ITA report's own caution).\n")
    w("## 2. Counts (units named)\n")
    w("### 2.1 Source rows in\n")
    w("| Family | Packet rows (unit: source records) | NO_MATCH rows read | POSSIBLE rows read | Held, no US state | Rows clustered |\n|---|---:|---:|---:|---:|---:|")
    for fam in FAMILIES:
        hn = sum(v for k, v in stats["held_no_state"].items() if k[0] == fam)
        w(f"| {fam} | {recon[fam][2]:,} | {recon[fam][0]:,} | {recon[fam][1]:,} | {hn:,} | {recon[fam][0] + recon[fam][1] - hn:,} |")
    tot_nm = sum(recon[f][0] for f in FAMILIES)
    tot_po = sum(recon[f][1] for f in FAMILIES)
    w(f"| **All** | {sum(recon[f][2] for f in FAMILIES):,} | **{tot_nm:,}** | **{tot_po:,}** | {len(held_rows):,} | **{len(cl_rows):,}** |\n")
    w("Unit: a source record is one packet row (ITA establishment_ID, OSHA aggregation key, FRS registry ID, Form 5500 sponsor EIN, USAspending UEI, PatentsView assignee). "
      "One physical establishment legitimately appears under several records and several families, which is exactly what the fusion measures. "
      f"{n_rows_in:,} NO_MATCH + POSSIBLE source rows were read; {len(cl_rows):,} entered clustering.\n")
    w("### 2.2 Clusters out\n")
    w(f"- **Raw candidate-establishment clusters** (unit: clusters of source rows, US states and territories only): **{len(cluster_list):,}** from {len(cl_rows):,} rows "
      "(assertions passed: cluster IDs unique, every row in exactly one cluster, no cluster spans two states).")
    big = sum(v for k, v in size_dist.items() if k > 8)
    w("- Cluster size (unit: source rows per cluster): " + "; ".join(f"{k} row{'s' if k > 1 else ''}: {v:,}" for k, v in sorted(size_dist.items()) if k <= 8) +
      (f"; 9 or more: {big:,} (largest {max(size_dist)})" if big else "") + ".")
    w("- Distinct source families per raw cluster (any verdict): " + "; ".join(f"{k}: {v:,}" for k, v in sorted(fam_dist.items())) + ".")
    w("- Successful merges by edge basis (unit: union operations): " + "; ".join(f"`{k}` {v:,}" for k, v in sorted(stats["edge_unions"].items())) + ".")
    nmg = stats.get("not_merged", {})
    w("- Name/locality candidates **refused because a real street differs** (unit: clusters or pairs): " + "; ".join(f"`{k}` {v:,}" for k, v in sorted(nmg.items())) + ". Such rows stay separate clusters.")
    w(f"- Same-address row pairs **blocked by the name guard** (unit: row pairs; co-tenants/rebrands, not merged): {stats['blocked_street_name_differs']:,}. "
      f"Weak (employer-level or street-less) clusters left unattached because more than one plant cluster qualified (unit: clusters): {stats['ambiguous_weak_attach']:,}.")
    w(f"- **Atlas re-check drops (unit: clusters; source rows in parentheses):** {sum(dropped.values()):,} clusters ({sum(dropped_rows.values()):,} rows) are already held in the current Atlas:")
    for k, v in dropped.most_common():
        w(f"  - `{k}`: {v:,} clusters ({dropped_rows[k]:,} rows)")
    w(f"- Survivors: **{len(kept):,} clusters**, by polymer-lead eligibility (`core` = a NO_MATCH row with core NAICS 3252/3255/3259/326, 325920 alone excluded; `ring3_primary` = only a Ring 3 Primary code; "
      f"`patent_cpc_only` = patent assignee with polymer CPC and no NAICS): " + "; ".join(f"{k} {v:,}" for k, v in elig_ct.most_common()) + ".")
    ex = stats["excluded"]
    w("- **Survivors not carried to the lead table (unit: clusters / source rows):** " + "; ".join(f"`{k}` {v[0]:,} clusters / {v[1]:,} rows" for k, v in sorted(ex.items())) +
      ". `out_of_core_naics` = ITA value-chain rows (distributors, tire retail, basic chemicals, machinery) with no core-NAICS row from any family; `possible_only` = clusters whose every row is a POSSIBLE "
      "(an Atlas candidate hit already exists; resolve in the packets' own POSSIBLE review). Nothing was ruled out of scope (scope is an owner ruling, AGENTS 2.9): these are simply not polymer-NAICS discovery leads for this table.\n")
    w(f"### 2.3 Lead table: `clusters.csv` = **{len(recs):,} clusters** (unit: candidate establishments not in the current Atlas, polymer-lead eligible)\n")
    w("| Class | Clusters | Share |\n|---|---:|---:|")
    for k in ("STRONG", "CORROBORATED", "SINGLE"):
        w(f"| {k} | {cls.get(k, 0):,} | {100 * cls.get(k, 0) / max(1, len(recs)):.1f}% |")
    w(f"| **Total** | **{len(recs):,}** | |\n")
    nfam = Counter(r["n_sources"] for r in recs)
    w("Families confirming (unit: clusters): " + "; ".join(f"{k} families: {v:,}" for k, v in sorted(nfam.items())) + ".")
    fc = Counter()
    for r in recs:
        for f in r["source_families"].split(";"):
            if f:
                fc[f] += 1
    w("Clusters containing each family (NO_MATCH rows): " + "; ".join(f"{f} {fc[f]:,}" for f in FAMILIES) + ".")
    combo = Counter(r["source_families"] for r in recs if r["class"] == "STRONG")
    w("Most common STRONG family sets (unit: clusters): " + "; ".join(f"{k} {v:,}" for k, v in combo.most_common(8)) + ".")
    ag = Counter(r["n_agencies"] for r in recs if r["class"] == "STRONG")
    w("STRONG clusters by distinct agencies (unit: clusters): " + "; ".join(f"{k} agencies: {v:,}" for k, v in sorted(ag.items())) + ".")
    pg = Counter(r["n_plant_grade_families"] for r in recs if r["class"] == "STRONG")
    pgc = Counter(r["n_plant_grade_families"] for r in recs if r["class"] == "CORROBORATED")
    w("Plant-grade families (ITA/OSHA/ECHO worksite addresses) per cluster (unit: clusters): STRONG " + "; ".join(f"{k}: {v:,}" for k, v in sorted(pg.items())) +
      "; CORROBORATED " + "; ".join(f"{k}: {v:,}" for k, v in sorted(pgc.items())) +
      ". A cluster with 0 plant-grade families is HQ-grade evidence only (flag `hq_grade_sources_only`, score -4).")
    rel = Counter(r["atlas_relation"] for r in recs)
    w("Atlas relation of the lead table (unit: clusters): " + "; ".join(f"`{k}` {v:,}" for k, v in rel.most_common()) +
      ". `HELD_ORG_OTHER_LOCATION` = a held org of this name or EIN exists in the state with no site at this location (likely a new SITE of an existing org, a different create path from a net-new org).\n")
    w("### 2.4 By state (unit: clusters in `clusters.csv`)\n")
    w("| State | STRONG | CORROBORATED | SINGLE | Total | of which NET_NEW |\n|---|---:|---:|---:|---:|---:|")
    st_rows = []
    for st, lst in by_state.items():
        c = Counter(r["class"] for r in lst)
        st_rows.append((c["STRONG"], len(lst), st, c, sum(1 for r in lst if r["atlas_relation"] == "NET_NEW")))
    st_rows.sort(key=lambda t: (-t[0], -t[1], t[2]))
    for s_, n_, st, c, nn in st_rows[:25]:
        w(f"| {st} | {c['STRONG']:,} | {c['CORROBORATED']:,} | {c['SINGLE']:,} | {n_:,} | {nn:,} |")
    w(f"\nTop 25 of {len(by_state)} states by STRONG count shown; all states are in `clusters.csv`. The QCEW gap states (`docs/denominators/README.md`: QCEW 2023 private establishments, NAICS 326, "
      "minus Atlas strict 326 sites) rank CA, TX, FL, MI, IL, GA, IN, WI, NY, NC highest; lead counts here are **not** an estimate of that gap "
      "(the sources cover inspected, permitted, plan-sponsoring or contract-winning units; QCEW counts reporting units of every size).\n")
    w("`top_leads_by_state.csv` holds the top 50 clusters per state by `score` (ties: more sources, larger size band, more recent activity) for CA, TX, FL, MI, IL, GA, IN, WI, NY, NC, OH, PA, "
      "with `state_rank`; it includes every class, so a state with fewer than 50 multi-source leads is filled with CORROBORATED then SINGLE rows. Rows per state: " +
      "; ".join(f"{st} {min(50, len(by_state.get(st, [])))}" for st in TOP_STATES) + ". The patents pilot covers OH and PA only, so only those two states can carry a sixth family.\n")
    w("## 3. Reconciliation against each source packet's published counts (AGENTS section 2 rule 10)\n")
    w("| Family | Published NO_MATCH | Read NO_MATCH | Published POSSIBLE | Read POSSIBLE | Published total | Read total | Result |\n|---|---:|---:|---:|---:|---:|---:|---|")
    allok = True
    for fam in FAMILIES:
        p = PUBLISHED[fam]
        ok = (p["NO_MATCH"], p["POSSIBLE"], p["total"]) == recon[fam]
        allok &= ok
        w(f"| {fam} | {p['NO_MATCH']:,} | {recon[fam][0]:,} | {p['POSSIBLE']:,} | {recon[fam][1]:,} | {p['total']:,} | {recon[fam][2]:,} | {'reconciles' if ok else 'MISMATCH'} |")
    w("")
    w("Published figures are copied from each packet's REPORT.md (ITA section 3: 9,145 / 346 of 11,194; OSHA section 3: 5,256 / 246 of 6,473; ECHO section 2: 13,255 / 315 of 15,920; "
      "Form 5500 section 4: 4,581 / 418 of 5,897; USAspending section 3: 4,450 NO_MATCH + 77 POSSIBLE_REVIEW of 4,756; patents section 3: 230 / 71 of 414). "
      f"**Result: {'all six families reconcile exactly (NO_MATCH, POSSIBLE and total), row for row.' if allok else 'at least one family does not reconcile; see the notes below.'}**\n")
    ita_nm = [r for r in rows if r.family == "ITA" and r.verdict == "NO_MATCH"]
    ita_core = sum(1 for r in ita_nm if r.x["scope_class"].startswith("core"))
    echo_nm = [r for r in rows if r.family == "ECHO" and r.verdict == "NO_MATCH"]
    echo_core = sum(1 for r in echo_nm if r.x["scope_class"] == "core")
    echo_r3 = sum(1 for r in echo_nm if r.x["scope_class"] == "ring3_primary")
    itap = sum(1 for r in ita_nm if r.x["scope_class"] == "core_P")
    w("Sub-split checks: " +
      f"ITA NO_MATCH in core-family scope classes (core_P/S/X/unlisted) {ita_core:,} vs published 4,921 ({'ok' if ita_core == 4921 else 'MISMATCH'}); ITA core_P NO_MATCH {itap:,} vs published 4,376 ({'ok' if itap == 4376 else 'MISMATCH'}); "
      f"ECHO core NO_MATCH {echo_core:,} vs published 12,141 and ring3_primary {echo_r3:,} vs 1,114 ({'ok' if (echo_core, echo_r3) == (12141, 1114) else 'MISMATCH'}). "
      "Record-ID uniqueness (rule 10b) is asserted on load per source (ITA establishment_ID, OSHA est_key, FRS registry_id, Form 5500 EIN, UEI, assignee_id) and across families on the `family:id` key; "
      "every input row lands in exactly one cluster (asserted). The inputs are source rows, not build-pass allocation rows, so rule 10a's creation-class whitelist has no marker, flip, repoint or fold rows to exclude.\n")
    n_p, ci, cnm, cany = stats["ita_osha_cross"]
    w("**Cross-check against the ITA packet's own `cross_source` field (rule 10c: a conflicting count is investigated, not explained away).** "
      f"The ITA report published {ITA_BOTH_OSHA_PUBLISHED['core_P_both_sources']:,} of {ITA_BOTH_OSHA_PUBLISHED['core_P_NO_MATCH']:,} core_P NO_MATCH ITA establishments as also listed by the inspection lane (`BOTH_SOURCES`) plus "
      f"{ITA_BOTH_OSHA_PUBLISHED['address_name_differs']} `BOTH_ADDRESS_NAME_DIFFERS`. Re-derived from the ITA `site_matches.csv` over the same {n_p:,} rows: `cross_source` = " +
      "; ".join(f"{k} {v:,}" for k, v in sorted(ci.items())) + ". The fusion puts an ITA core_P NO_MATCH row in a cluster that holds an OSHA NO_MATCH row as follows "
      "(ITA-reported `cross_source` | cluster holds an OSHA NO_MATCH row): " + "; ".join(f"{k[0]} | {k[1]}: {v:,}" for k, v in sorted(cnm.items())) +
      ". Same, counting an OSHA row of any verdict: " + "; ".join(f"{k[0]} | {k[1]}: {v:,}" for k, v in sorted(cany.items())) + ".\n")
    missed, extra_basis = stats["ita_cross_detail"]
    w("Where the two disagree (unit: ITA core_P NO_MATCH rows). The ITA packet says BOTH_SOURCES but the fusion has no OSHA NO_MATCH row in the cluster: " +
      "; ".join(f"{k}: {v}" for k, v in sorted(missed.items())) + ". The ITA packet says ITA_ONLY or BOTH_ADDRESS_NAME_DIFFERS but the fusion joined an OSHA row, by edge basis: " +
      "; ".join(f"{k[0]} via `{k[1]}`: {v}" for k, v in sorted(extra_basis.items())) + ".\n")
    w(AUDIT_NOTES.get("cross", "") + "\n")
    w("## 4. Cluster quality: false-cluster audit\n")
    k = Counter()
    for r in audit:
        v = AUDIT_VERDICTS.get(r["_fp"])
        k[v[0] if v else "UNREVIEWED"] += 1
    n = len(audit)
    susp, nm_ = stats["auto_suspect"]
    if "UNREVIEWED" not in k:
        lo, hi = wilson(k["FALSE"], n)
        w(f"**Hand-style audit of {n} random multi-source clusters** (the 30 clusters with the smallest `sha1(fingerprint + 'audit')` among the {nm_:,} lead-table clusters with at least 2 families, where the fingerprint is a hash of the member row keys, so the draw is deterministic and stable when unrelated clusters change; each is printed in 4.1 with its rows and judged "
          "on address, name, city/ZIP and identifiers by reading the rows, not by re-running the clustering rule):\n")
        w(f"- **OK** (all rows plausibly one establishment): {k['OK']}; **DOUBTFUL** (plausible, but a step I would not accept without a primary check): {k['DOUBTFUL']}; **FALSE** (rows from different establishments merged): {k['FALSE']}.")
        w(f"- **Observed false-cluster rate: {k['FALSE']}/{n} = {100 * k['FALSE'] / n:.1f}%** (95% Wilson interval {100 * max(lo, 0):.1f}% to {100 * hi:.1f}%); counting DOUBTFUL as false: "
          f"{k['FALSE'] + k['DOUBTFUL']}/{n} = {100 * (k['FALSE'] + k['DOUBTFUL']) / n:.1f}%. A sample of 30 cannot resolve a rate below roughly 10%; read it as an order of magnitude.")
    else:
        w(f"(audit verdicts pending: {dict(k)})")
    w(f"- **Automatic screen over all {nm_:,} lead-table clusters with at least 2 families:** {susp:,} ({100 * susp / max(1, nm_):.1f}%) contain a row whose names are incompatible with every row of every other family "
      "(it joined by address or EIN, not by name). This is an upper-bound suspect flag, not a false rate: ECHO facility labels, ITA plant labels and parent-versus-operator names legitimately differ.")
    w(f"- **Cost of the name guard:** {stats['blocked_street_name_differs']:,} same-address row pairs were not merged because the names are incompatible (4.2 samples them).\n")
    w("### 4.1 Audit sample (printed)\n")
    for r in audit:
        v = AUDIT_VERDICTS.get(r["_fp"])
        w("```")
        w(fmt_audit(r["cluster_id"], r["_rows"], bases_by_cluster[r["cluster_id"]], r["_fp"]))
        w("```")
        w(f"Verdict: **{v[0] if v else 'UNREVIEWED'}**" + (f" - {v[1]}" if v and v[1] else "") + "\n")
    w("### 4.1b Stratified supplement: the weaker merge bases\n")
    w("The random draw is dominated by `street_zip` merges (the strongest basis). To measure the weaker bases, up to 8 further multi-source clusters were drawn per basis (same fingerprint ordering, salted by basis name; a cluster can carry several bases, so strata overlap) and judged the same way. "
      "Population = lead-table clusters with at least 2 families whose `cluster_basis` contains the basis.\n")
    w("| Basis | Population (clusters) | Drawn | OK | DOUBTFUL | FALSE |\n|---|---:|---:|---:|---:|---:|")
    for nm_s, pop in stats["strat_pop"].items():
        drawn = [r for n_, r in strat_audit if n_ == nm_s]
        kk = Counter((AUDIT_VERDICTS.get(r["_fp"]) or ("UNREVIEWED", ""))[0] for r in drawn)
        w(f"| `{nm_s}` | {pop:,} | {len(drawn)} | {kk['OK']} | {kk['DOUBTFUL']} | {kk['FALSE']} |")
    w("")
    for nm_s, r in strat_audit:
        v = AUDIT_VERDICTS.get(r["_fp"])
        w("```")
        w(f"[{nm_s}] " + fmt_audit(r["cluster_id"], r["_rows"], bases_by_cluster[r["cluster_id"]], r["_fp"]))
        w("```")
        w(f"Verdict: **{v[0] if v else 'UNREVIEWED'}**" + (f" - {v[1]}" if v and v[1] else "") + "\n")
    w("### 4.2 Sample of same-address pairs blocked by the name guard\n")
    bs = random.Random(11).sample(blocked, min(14, len(blocked)))
    for basis, i, j in sorted(bs):
        ri, rj = cl_rows[i], cl_rows[j]
        w(f"- {ri.family} `{' / '.join(ri.names)[:46]}` vs {rj.family} `{' / '.join(rj.names)[:46]}` at `{ri.street[:34]}`, {ri.city}, {ri.state} {ri.zip5} ({basis})")
    w("")
    w(AUDIT_NOTES.get("blocked", "") + "\n")
    w("### 4.3 Examples of clusters dropped as already held (up to 4 per reason)\n")
    for reason, exs in dropped_examples.items():
        w(f"- `{reason}`")
        for cid, nm, city, st, detail, fams in exs[:4]:
            w(f"  - {cid} {nm[:40]} ({city}, {st}; {','.join(fams)}) -> {detail}")
    w("")
    w("## 5. Caveats (binding on any reader)\n")
    for t in [
        "**Leads only.** No cluster is a verdict in the AGENTS 2.8 grammar (not VERIFIED, REJECT, STILL_UNCERTAIN, DUPLICATE_OF). A multi-source cluster is more likely to be a real, operating establishment; it is not proof, not a scope claim, not a ring, not a tier.",
        "**Source families are not fully independent.** ITA and OSHA inspections are both DOL-OSHA; ITA and Form 5500 are employer self-filings; USAspending and Form 5500 addresses are registered or HQ-grade and often not the plant (they confirm an address only when they equal a plant-grade street). Patents only place an assignee in a city. A single-source cluster can be a real plant that sits in only one dataset.",
        "**NAICS is a signal, not a company fact** (AGENTS section 4): ITA/OSHA NAICS are OSHA-channel, ECHO NAICS is program-reported, Form 5500 codes are filer-chosen padded groups (326100, 325900 ...), USAspending NAICS describes the contract, not the firm. `core_naics_families` counts agreement of signals only; none of it may populate `naics_primary`.",
        "**Form 5500 rows are employers, not establishments**; the participant band is a plan-size input (SCHEMA R7f) at employer level, shown only as `size_basis = F5500 ...` when no establishment-grain size exists.",
        "**Privacy (AGENTS section 6).** Form 5500 sponsors whose street line the source packet withheld (no entity designator and fewer than 10 participants: a possible home address) carry no street here and are flagged `form5500_street_withheld_privacy_possible_individual`; the name and EIN of such a row are carried over from the packet as published and should be treated as possibly an individual's: do not research or publish them without a business-entity check. No emails, phones, officers or inventors are carried.",
        "**Coordinates were never read.** `county` is the ECHO FRS county (or the PatentsView county) shown for orientation only; Ohio counties need the physical address (AGENTS section 4).",
        "**Clustering is conservative on purpose.** Street spelling variance beyond rule 2, a rebranded or co-tenant operator at one address, and plant addresses that differ by building number are left as separate clusters, so some real multi-source establishments are undercounted as SINGLE. The opposite risk (false merges) is measured in section 4.",
        "**Dropped clusters are not verdicts either.** They were dropped because the current Atlas already holds a record at that address/name/EIN/TRIFID; a wrong drop is possible, mainly where a held org's same-city site has an unknown street (rule b). `--dump-dropped PATH` regenerates the drop list.",
        "**No website-domain dedupe was possible** (AGENTS section 3 step 1): none of the six sources carries a domain. Every lead must be domain-checked, and re-checked against the Atlas as it stands at integration time (the Atlas moves between passes).",
        "**Registry identifiers** (EINs in `eins`, ECHO registry IDs and UEIs inside `sources_with_ids`) are lead keys; an identifier seen only in this project's files mints no registry link (AGENTS section 4 phantom rule). EINs are public business-filer IDs carried over from the ITA and Form 5500 packets; no personal data is carried (the Form 5500 street lines the source withheld for privacy stay blank).",
        "**Territories and no-state rows**: USPS territories (PR, GU, ...) cluster like states; foreign and no-state recipients are held (section 1).",
        "**Counting honesty (AGENTS section 7):** every count above names its unit. 'Clusters' are candidate establishments built from source records, not verified establishments and not Atlas sites; they are not comparable with QCEW establishment counts.",
    ]:
        w(f"- {t}")
    w("\n## 6. Reproduce\n")
    w("```\npython3 scripts/build_lead_fusion.py --as-of 2026-11-01            # writes clusters.csv, top_leads_by_state.csv, REPORT.md\n"
      "python3 scripts/build_lead_fusion.py --audit-print --no-write      # print the 30-cluster audit sample\n"
      "python3 scripts/build_lead_fusion.py --dump-dropped /path/dropped.csv --no-write\n```")
    w("Inputs are the committed packet CSVs under `tasks/` and the current `data/`; no network, no credentials. REPORT.md is regenerated by the script; the hand-review verdicts of section 4 and the two discussion notes are stored in `AUDIT_VERDICTS` / `AUDIT_NOTES` in the script so a re-run reproduces them (a changed input changes the sample, and unreviewed clusters then show as UNREVIEWED).")
    with open(os.path.join(OUT, "REPORT.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())
