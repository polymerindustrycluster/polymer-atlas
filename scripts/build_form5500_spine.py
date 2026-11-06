#!/usr/bin/env python3
"""Build a Form 5500 polymer-sponsor spine: employee-size source, national
discovery spine and liveness signal, matched against the Atlas.

Packet-lane tool: it reads data/ and writes ONLY under --out-dir (default
tasks/form5500-spine-2026-11-01/).  It never edits data/, allocates no IDs and
changes no status.  Stdlib only.

Source: U.S. DOL EBSA, Form 5500 / Form 5500-SF bulk "Latest" datasets (EFAST2),
https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/public-disclosure/foia/form-5500-datasets
(files resolve to https://askebsa.dol.gov/FOIA%20Files/<YEAR>/Latest/):
    F_5500_<YEAR>_Latest.zip      f_5500_<year>_latest.csv       (Form 5500)
    F_5500_SF_<YEAR>_Latest.zip   f_5500_sf_<year>_latest.csv    (Form 5500-SF)
Column names below were confirmed against the published *_layout.txt files and
the 2024 form PDFs in form-5500-2024-data-dictionary.zip:

                      Form 5500                    Form 5500-SF
  sponsor EIN         SPONS_DFE_EIN                SF_SPONS_EIN
  sponsor name        SPONSOR_DFE_NAME             SF_SPONSOR_NAME
  location address    SPONS_DFE_LOC_US_*           SF_SPONS_LOC_US_*
  mailing address     SPONS_DFE_MAIL_US_*          SF_SPONS_US_*
  business code       BUSINESS_CODE                SF_BUSINESS_CODE
  plan year begin     FORM_PLAN_YEAR_BEGIN_DATE    SF_PLAN_YEAR_BEGIN_DATE
  ACTIVE PARTICIPANTS TOT_ACTIVE_PARTCP_CNT        SF_TOT_ACT_PARTCP_EOY_CNT
    = line 6a(2), active participants at END of plan year (5500)
    = line 5d(2), active participants at END of plan year (5500-SF)
  total participants  TOT_PARTCP_BOY_CNT (line 5)  SF_TOT_PARTCP_BOY_CNT (line 5a)
  final filing flag   FINAL_FILING_IND             SF_FINAL_FILING_IND

Method
  1. Pass 1 streams every filing (all requested years, both forms) and keeps
     those whose business code is in the polymer set: every code starting
     3252, 3255, 3259 or 326, plus the SCHEMA 2.2 Ring 3 Primary codes
     333511, 424610, 562920.  (Form 5500 filers pick the code from the IRS list,
     which is largely 4-digit-padded: 326100, 326200, 325200, 325500, 325900;
     exact 6-digit polymer codes such as 326199 are rare.  The script records
     code_granularity so consumers can see this.)
  2. Pass 2 streams again and collects the OTHER filings (any code) of those
     EINs, so participants are not under-read when the biggest plan is coded
     differently.
  3. One row per sponsor EIN.  Latest plan year Y = latest plan-year-begin year
     among polymer-coded filings.  Representative filing = the filing with the
     most active participants among ALL the EIN's filings for plan year Y (the
     plans of one sponsor overlap - the same employees sit in the 401(k) and in
     the health plan - so the MAX, never the sum, is the employee proxy).
  4. Each sponsor is matched to the Atlas with the same normalizers and step
     order as scripts/atlas.py dedupe-check (AGENTS.md section 3: step 2 name,
     step 3 street, step 4 trade names/notes; step 1 domain does not apply -
     Form 5500 carries no website), but with indexes so 10^4 queries run in
     seconds.  --selftest N re-runs N random sponsors through atlas.dedupe()
     and asserts the same step-2 / step-3 hits.
  5. Band proposals are produced for MATCH rows only.

Usage:
    python3 scripts/build_form5500_spine.py --raw-dir /tmp/claude-0/f5500_raw
    python3 scripts/build_form5500_spine.py --raw-dir DIR --years 2025,2024,2023 --selftest 300
Missing raw zips are downloaded into --raw-dir.  A failed fetch is reported on
stderr as BLOCKED and the script exits non-zero.
"""
import argparse
import collections
import csv
import datetime
import hashlib
import importlib.util
import io
import os
import random
import re
import sys
import urllib.request
import zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
BASE_URL = "https://askebsa.dol.gov/FOIA%20Files/{y}/Latest/{f}"
UA = {"User-Agent": "polymer-atlas-form5500-spine/1.0"}
csv.field_size_limit(10 ** 8)

# ------------------------------------------------------------------ polymer code set
POLYMER_PREFIXES = ("3252", "3255", "3259", "326")
RING3_PRIMARY = {"333511", "424610", "562920"}

# SCHEMA.md section 2.2 signal per code (P primary / S secondary / X exclude-by-default).
# 5500 filers mostly use padded group codes; those get the signal of the group's members.
CODE_SIGNAL = {
    "325211": "R2:P", "325212": "R2:P", "325991": "R2:P", "325510": "R2:P*", "325520": "R2:P",
    "325220": "R2:S", "325998": "R2:S", "325920": "R2:X",
    "325200": "R2:P/S mixed (325211,325212 P; 325220 S)",
    "325500": "R2:P*/P (325510,325520)",
    "325900": "R2:mixed (325991 P; 325998 S; 325920 X; 325910,325992 not in 2.2)",
    "326100": "R1:P (326111-326199 group)", "326200": "R1:P (326211-326299 group)",
    "326000": "R1:P (326 group)",
    "333511": "R3:P", "424610": "R3:P", "562920": "R3:P",
}


def is_polymer_code(code):
    return code[:4] in POLYMER_PREFIXES[:3] or code[:3] == "326" or code in RING3_PRIMARY


def code_signal(code):
    if code in CODE_SIGNAL:
        return CODE_SIGNAL[code]
    if code.startswith("326"):
        return "R1:P"
    if code.startswith("32522"):
        return "R2:S (325220 family)"
    if code[:4] in ("3252", "3255", "3259"):
        return "not listed in 2.2"
    return ""


def code_granularity(code):
    return "padded_group" if code.endswith("00") else "exact6"


# ------------------------------------------------------------------ bands (SCHEMA 4.4)
BANDS = [(1, 9, "1-9"), (10, 49, "10-49"), (50, 99, "50-99"), (100, 249, "100-249"),
         (250, 499, "250-499"), (500, 999, "500-999"), (1000, 4999, "1000-4999")]


def band_of(n):
    if n is None or n < 1:
        return ""
    for lo, hi, b in BANDS:
        if lo <= n <= hi:
            return b
    return "5000+"


# ------------------------------------------------------------------ source specs
SPECS = {
    "5500": dict(
        zip="F_5500_{y}_Latest.zip", member="f_5500_{y}_latest.csv",
        ack="ACK_ID", ein="SPONS_DFE_EIN", name="SPONSOR_DFE_NAME", dba="SPONS_DFE_DBA_NAME",
        code="BUSINESS_CODE", py="FORM_PLAN_YEAR_BEGIN_DATE", received="DATE_RECEIVED",
        plan="SPONS_DFE_PN", active="TOT_ACTIVE_PARTCP_CNT", total="TOT_PARTCP_BOY_CNT",
        final="FINAL_FILING_IND", short="SHORT_PLAN_YR_IND", status="FILING_STATUS",
        loc=("SPONS_DFE_LOC_US_ADDRESS1", "SPONS_DFE_LOC_US_ADDRESS2", "SPONS_DFE_LOC_US_CITY",
             "SPONS_DFE_LOC_US_STATE", "SPONS_DFE_LOC_US_ZIP"),
        mail=("SPONS_DFE_MAIL_US_ADDRESS1", "SPONS_DFE_MAIL_US_ADDRESS2", "SPONS_DFE_MAIL_US_CITY",
              "SPONS_DFE_MAIL_US_STATE", "SPONS_DFE_MAIL_US_ZIP"),
        foreign=("SPONS_DFE_LOC_FOREIGN_CNTRY", "SPONS_DFE_MAIL_FOREIGN_CNTRY"),
    ),
    "5500-SF": dict(
        zip="F_5500_SF_{y}_Latest.zip", member="f_5500_sf_{y}_latest.csv",
        ack="ACK_ID", ein="SF_SPONS_EIN", name="SF_SPONSOR_NAME", dba="SF_SPONSOR_DFE_DBA_NAME",
        code="SF_BUSINESS_CODE", py="SF_PLAN_YEAR_BEGIN_DATE", received="DATE_RECEIVED",
        plan="SF_PLAN_NUM", active="SF_TOT_ACT_PARTCP_EOY_CNT", total="SF_TOT_PARTCP_BOY_CNT",
        final="SF_FINAL_FILING_IND", short="SF_SHORT_PLAN_YR_IND", status="FILING_STATUS",
        loc=("SF_SPONS_LOC_US_ADDRESS1", "SF_SPONS_LOC_US_ADDRESS2", "SF_SPONS_LOC_US_CITY",
             "SF_SPONS_LOC_US_STATE", "SF_SPONS_LOC_US_ZIP"),
        mail=("SF_SPONS_US_ADDRESS1", "SF_SPONS_US_ADDRESS2", "SF_SPONS_US_CITY",
              "SF_SPONS_US_STATE", "SF_SPONS_US_ZIP"),
        foreign=("SF_SPONS_LOC_FOREIGN_CNTRY", "SF_SPONS_FOREIGN_CNTRY"),
    ),
}


def num(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


# ------------------------------------------------------------------ download / scan
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_raw(raw_dir, years):
    os.makedirs(raw_dir, exist_ok=True)
    out = []
    for y in years:
        for kind, sp in SPECS.items():
            fn = sp["zip"].format(y=y)
            dest = os.path.join(raw_dir, fn)
            if not os.path.exists(dest):
                url = BASE_URL.format(y=y, f=fn)
                try:
                    req = urllib.request.Request(url, headers=UA)
                    with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
                        while True:
                            b = r.read(1 << 20)
                            if not b:
                                break
                            f.write(b)
                except Exception as e:  # noqa: BLE001
                    if os.path.exists(dest):
                        os.remove(dest)
                    print(f"BLOCKED: could not fetch {url}: {e}", file=sys.stderr)
                    sys.exit(2)
            out.append((y, kind, fn, dest))
    return out


def scan(raw_dir, years, keep):
    """Yield (year_file, kind, normalized dict) for rows where keep(code, ein) is true."""
    for y in years:
        for kind, sp in SPECS.items():
            path = os.path.join(raw_dir, sp["zip"].format(y=y))
            with zipfile.ZipFile(path) as z:
                with z.open(sp["member"].format(y=y)) as raw:
                    f = io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")
                    rd = csv.reader(f)
                    head = next(rd)
                    ix = {c: i for i, c in enumerate(head)}
                    missing = [c for c in [sp[k] for k in ("ack", "ein", "name", "code", "py", "plan", "active", "total", "final", "short")]
                               + list(sp["loc"]) + list(sp["mail"]) if c not in ix]
                    if missing:
                        raise SystemExit(f"{path}: layout changed, missing columns {missing}")
                    i_ein, i_code = ix[sp["ein"]], ix[sp["code"]]

                    def g(row, col, ix=ix):
                        j = ix.get(col)
                        return row[j].strip() if j is not None and j < len(row) else ""
                    for row in rd:
                        if len(row) <= i_ein:
                            continue
                        ein = re.sub(r"\D", "", row[i_ein])
                        code = row[i_code].strip()
                        if len(ein) != 9 or ein == "000000000" or not keep(code, ein):
                            continue
                        pyb = g(row, sp["py"])
                        rec = dict(
                            ein=ein, kind=kind, file_year=y, ack_id=g(row, sp["ack"]), code=code,
                            name=g(row, sp["name"]), dba=g(row, sp["dba"]),
                            plan_year=int(pyb[:4]) if pyb[:4].isdigit() else 0,
                            plan_begin=pyb, received=g(row, sp["received"]), plan_num=g(row, sp["plan"]),
                            active=num(g(row, sp["active"])), total_boy=num(g(row, sp["total"])),
                            final=g(row, sp["final"]), short=g(row, sp["short"]),
                            loc=tuple(g(row, c) for c in sp["loc"]), mail=tuple(g(row, c) for c in sp["mail"]),
                            foreign=next((g(row, c) for c in sp["foreign"] if g(row, c)), ""),
                        )
                        yield rec


# ------------------------------------------------------------------ atlas helpers
def load_atlas(data_dir):
    spec = importlib.util.spec_from_file_location("atlas_cli", os.path.join(REPO, "scripts", "atlas.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["atlas_cli"] = mod
    spec.loader.exec_module(mod)
    return mod, mod.load_tables(data_dir)


EXTRA_STOP = {"lp", "llp", "lllp", "pllc", "pc", "plc", "na", "holdings", "holding", "group", "industries",
              "industry", "international", "intl", "usa", "us", "america", "americas", "mfg", "manufacturing",
              "and", "of", "ltd", "lc", "inc", "llc", "corp", "co", "the", "company", "corporation", "incorporated"}
GENERIC_SINGLE = {"plastics", "plastic", "rubber", "polymer", "polymers", "industries", "products", "manufacturing",
                  "group", "international", "american", "united", "national", "general", "precision", "custom",
                  "technologies", "technology", "systems", "solutions", "services", "enterprises", "composites",
                  "packaging", "molding", "chemical", "chemicals", "coatings", "foam", "industrial"}
DESIGNATORS = {"inc", "incorporated", "llc", "llp", "lp", "ltd", "corp", "corporation", "co", "company", "pc", "pllc",
               "pa", "plc", "lc", "lllp", "trust", "group", "industries", "associates", "enterprises"}


def fuzzy_key(atlas, s):
    t = atlas.squash(re.sub(r"\bL\.?\s*L\.?\s*C\.?(?=\W|$)", "LLC", s or "", flags=re.I))
    toks = []
    for w in t.split():
        if w in EXTRA_STOP:
            continue
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        toks.append(w)
    return " ".join(toks)


def pobox(street):
    return bool(re.match(r"^\s*(p\.?\s*o\.?\s*box|post office box|box)\b", (street or "").lower())) or not re.search(r"\d", street or "")


class AtlasIndex:
    def __init__(self, atlas, tables):
        self.atlas = atlas
        self.orgs = list(atlas.org_rows(tables))
        self.by_id = collections.defaultdict(list)
        for tn, r in self.orgs:
            self.by_id[r["org_id"]].append(r)
        self.table_of = {r["org_id"]: tn for tn, r in self.orgs}
        self.sites = tables["sites"].rows
        self.sites_by_org = collections.defaultdict(list)
        for s in self.sites:
            self.sites_by_org[s["org_id"]].append(s)
        self.name_idx = collections.defaultdict(list)    # name_key -> [(tn, r, field)]
        self.fuzzy_idx = collections.defaultdict(list)
        self.hay = []
        for tn, r in self.orgs:
            seen = set()
            for fld, val in atlas.org_name_fields(r):
                k = atlas.name_key(val)
                if k and (k, fld) not in seen:
                    seen.add((k, fld))
                    self.name_idx[k].append((tn, r, fld, val))
                fk = fuzzy_key(atlas, val)
                if fk:
                    self.fuzzy_idx[fk].append((tn, r, fld, val))
            self.hay.append((tn, r, {f: " " + atlas.squash(r.get(f, "")) + " " for f in ("trade_names", "notes", "legal_name")}))
        self.street_idx = collections.defaultdict(list)
        for s in self.sites:
            k = atlas.street_key(s.get("street_address", ""))
            if k:
                self.street_idx[k].append(s)

    def org_states(self, org_id):
        tn_r = self.by_id.get(org_id)
        st = set()
        if tn_r:
            r = tn_r[0]
            tn = self.table_of[org_id]
            st.add((r["hq_state"] if tn == "organizations" else r.get("state", "")).upper())
        for s in self.sites_by_org.get(org_id, []):
            st.add((s["state"] or "").upper())
        st.discard("")
        return st

    def brief(self, org_id):
        r = self.by_id[org_id][0]
        return self.atlas.brief(self.table_of[org_id], r)


def tokens_overlap(atlas, a, bs):
    """True if the sponsor name shares its first significant token with any candidate string."""
    ta = [t for t in atlas.name_key(a).split() if t not in GENERIC_SINGLE]
    if not ta:
        return False
    first = ta[0]
    for b in bs:
        tb = atlas.name_key(b).split()
        if first in tb:
            return True
    return False


def match_sponsor(ix, sp):
    """Return a match dict for one sponsor row (sp from the sponsors list, with _street_full)."""
    atlas = ix.atlas
    name = sp["sponsor_name"]
    qk = atlas.name_key(name)
    fk = fuzzy_key(atlas, name)
    state = sp["state"]
    res = dict(match_class="NO_MATCH", match_step="", org_id="", site_id="", matched_name="", matched_org_status="",
               matched_org_state="", matched_table="", org_site_count="", name_state_agree="", successor_terminal="",
               other_candidates="", note="")
    # ---- step 2 exact normalized name
    s2 = []
    seen = set()
    if qk:
        for tn, r, fld, val in ix.name_idx.get(qk, []):
            if r["org_id"] not in seen:
                seen.add(r["org_id"])
                s2.append((tn, r, fld, val))
    # ---- step 3 street (try the location address first, then the mailing address)
    s3 = []
    for street, city, st, zp in sp["_addrs"]:
        if pobox(street):
            continue
        k = atlas.street_key(street)
        for s in ix.street_idx.get(k, []):
            if state and s["state"] and state.upper() != s["state"].upper():
                continue
            z_ok = bool(zp and s["zip"] and zp[:5] == s["zip"][:5])
            c_ok = bool(city and s["city"] and atlas.squash(city) == atlas.squash(s["city"]))
            if z_ok or c_ok:
                if s not in s3:
                    s3.append(s)
    # ---- candidates
    cand = {}
    for tn, r, fld, val in s2:
        oid = r["org_id"]
        agree = state.upper() in ix.org_states(oid) if state else False
        cand.setdefault(oid, dict(step2=True, agree=agree, how=f"{fld}={val!r}", sites=[]))
    for s in s3:
        oid = s["org_id"]
        c = cand.setdefault(oid, dict(step2=False, agree=None, how="", sites=[]))
        c["sites"].append(s)

    def fill(oid, cls, step, site=None, note=""):
        b = ix.brief(oid)
        res.update(match_class=cls, match_step=step, org_id=oid, site_id=site["site_id"] if site else "",
                   matched_name=b["name"], matched_org_status=b["status"], matched_org_state=b["state"],
                   matched_table=ix.table_of[oid], org_site_count=len(ix.sites_by_org.get(oid, [])),
                   name_state_agree=("1" if cand[oid]["agree"] else "0") if cand[oid]["step2"] else "", note=note)
        chain, end = atlas.successor_chain(oid, ix.by_id)
        if chain:
            last = ix.by_id.get(chain[-1], [None])[0]
            res["successor_terminal"] = (f"{chain[-1]} {last['legal_name']} [{last['status']}] ({end})" if last else f"{chain[-1]} (not in tree)")
        others = [o for o in cand if o != oid]
        res["other_candidates"] = ";".join(others)

    # priority 1: name exact + state agrees -> MATCH_ORG
    p1 = [o for o, c in cand.items() if c["step2"] and c["agree"]]
    if p1:
        p1.sort(key=lambda o: (0 if cand[o]["sites"] else 1, 0 if (ix.by_id[o][0].get("status") or "") == "active" else 1, o))
        o = p1[0]
        step = "2" + ("+3" if cand[o]["sites"] else "")
        fill(o, "MATCH_ORG", step, cand[o]["sites"][0] if cand[o]["sites"] else None,
             note=("multiple name-exact orgs; ties listed in other_candidates" if len(p1) > 1 else ""))
        return res
    # priority 2: street match + name token overlap with operator/site -> MATCH_SITE
    for o, c in cand.items():
        for s in c["sites"]:
            org = ix.by_id[o][0]
            names = [org["legal_name"], s.get("site_name", "")] + atlas.tokens_semicolon(org.get("trade_names"))
            if tokens_overlap(atlas, name, names):
                fill(o, "MATCH_SITE", "3", s, note="street+locality equal; sponsor name shares its first significant token with operator/site")
                return res
    # POSSIBLE: name exact with state conflict, street-only, fuzzy, step 4
    poss = []
    for o, c in cand.items():
        if c["step2"] and not c["agree"]:
            poss.append((o, "2_name_exact_state_conflict", None))
        elif not c["step2"]:
            poss.append((o, "3_street_only_name_differs", c["sites"][0]))
    if not poss and fk:
        for tn, r, fld, val in ix.fuzzy_idx.get(fk, []):
            o = r["org_id"]
            if o in cand:
                continue
            agree = state.upper() in ix.org_states(o) if state else False
            poss.append((o, "2b_fuzzy_name" + ("" if agree else "_state_conflict"), None))
            cand.setdefault(o, dict(step2=False, agree=agree, how=f"fuzzy {val!r}", sites=[]))
    if not poss:
        needle = atlas.name_key(name)
        toks = needle.split()
        ok = len(needle) >= 6 and (len(toks) >= 2 or toks[0] not in GENERIC_SINGLE)
        if ok:
            pat = f" {needle} "
            for tn, r, h in ix.hay:
                for fld in ("trade_names", "notes", "legal_name"):
                    if pat in h[fld]:
                        poss.append((r["org_id"], f"4_{fld}_contains", None))
                        cand.setdefault(r["org_id"], dict(step2=False, agree=None, how="", sites=[]))
                        break
                if len(poss) >= 8:
                    break
    if poss:
        # prefer state-agreeing candidates
        poss.sort(key=lambda t: (0 if (state and state.upper() in ix.org_states(t[0])) else 1, t[0]))
        o, step, site = poss[0]
        fill(o, "POSSIBLE", step, site)
        res["other_candidates"] = ";".join(sorted({t[0] for t in poss} - {o}))
    return res


# ------------------------------------------------------------------ build
def street_full(addr):
    a1, a2 = addr[0], addr[1]
    return (a1 + (" " + a2 if a2 and a1 else a2)).strip()


def build(args):
    years = [y.strip() for y in args.years.split(",") if y.strip()]
    raw = ensure_raw(args.raw_dir, years)
    print("pass 1: polymer-coded filings ...", file=sys.stderr)
    poly = collections.defaultdict(list)
    rows_seen = collections.Counter()
    for rec in scan(args.raw_dir, years, lambda code, ein: is_polymer_code(code)):
        poly[rec["ein"]].append(rec)
        rows_seen[(rec["file_year"], rec["kind"])] += 1
    print(f"  {sum(len(v) for v in poly.values())} polymer-coded filings, {len(poly)} EINs", file=sys.stderr)
    print("pass 2: all other filings of those EINs ...", file=sys.stderr)
    other = collections.defaultdict(list)
    eins = set(poly)
    for rec in scan(args.raw_dir, years, lambda code, ein: ein in eins and not is_polymer_code(code)):
        other[rec["ein"]].append(rec)

    sponsors = []
    for ein, pf in poly.items():
        allf = pf + other.get(ein, [])
        # Banding year: latest plan year among OPERATING (not final, not short-year) polymer-coded filings.
        # A final / short-year filing reports the wind-down (active participants typically 0), so it never sets a band.
        def operating(r):
            return r["final"] != "1" and r["short"] != "1"
        ops_poly = [r for r in pf if operating(r)]
        fallback = not ops_poly
        ypoly = max(r["plan_year"] for r in (pf if fallback else ops_poly))
        cur = [r for r in allf if r["plan_year"] == ypoly and (fallback or operating(r))]
        pcur = [r for r in cur if is_polymer_code(r["code"])]

        def key(r):
            return (r["active"] or 0, r["total_boy"] or 0, 1 if is_polymer_code(r["code"]) else 0,
                    1 if r["kind"] == "5500" else 0, r["received"])
        rep = max(cur, key=key)
        pbest = max(pcur, key=key)
        use_addr = rep if (rep["loc"][0] or rep["loc"][2] or rep["mail"][0]) else pbest
        loc, mail = use_addr["loc"], use_addr["mail"]
        if loc[0] or loc[2]:
            addr, asrc = loc, "location"
        else:
            addr, asrc = mail, "mailing"
        addrs = [(loc[0], loc[2], loc[3], loc[4]), (mail[0], mail[2], mail[3], mail[4])]
        country = "US" if (addr[3] or mail[3] or loc[3]) else (use_addr["foreign"] or "")
        n_plans = len({(r["plan_num"], r["kind"]) for r in cur})
        act = rep["active"]
        latest_any = max(r["plan_year"] for r in allf)
        latest_rows = [r for r in allf if r["plan_year"] == latest_any]
        recv = max((r["received"] for r in allf if r["plan_year"] == latest_any), default="")
        codes_seen = sorted({r["code"] for r in allf if r["code"]})
        sponsors.append(dict(
            ein=ein, sponsor_name=rep["name"] or pbest["name"], dba_name=rep["dba"],
            _street_full=street_full(addr), _addrs=addrs,
            city=addr[2], state=addr[3] or "", zip=addr[4], country=country, address_source=asrc,
            business_code=pbest["code"], code_granularity=code_granularity(pbest["code"]), code_signal=code_signal(pbest["code"]),
            plan_year=ypoly, active_participants="" if act is None else act,
            band_from_participants="" if fallback else band_of(act),
            rep_basis="final_or_short_only" if fallback else "operating_plan_year",
            total_participants_boy="" if rep["total_boy"] is None else rep["total_boy"],
            filing_type=rep["kind"], plan_number=rep["plan_num"], ack_id=rep["ack_id"],
            n_filings_latest_py=len(cur), n_plans_latest_py=n_plans,
            max_active_latest_py=max((r["active"] or 0) for r in cur),
            latest_filed_plan_year_any=latest_any, latest_date_received=recv,
            final_filing_flag_latest="1" if any(r["final"] == "1" for r in latest_rows) else "0",
            short_plan_year_flag_latest="1" if any(r["short"] == "1" for r in latest_rows) else "0",
            latest_py_all_final_or_short="1" if all(not operating(r) for r in latest_rows) else "0",
            business_codes_seen=";".join(codes_seen),
            plan_years_present=";".join(str(y) for y in sorted({r["plan_year"] for r in allf if r["plan_year"]})),
            polymer_code_filings=len(pf),
        ))
    sponsors.sort(key=lambda s: (s["state"] or "~", s["sponsor_name"], s["ein"]))
    assert len({s["ein"] for s in sponsors}) == len(sponsors), "EIN uniqueness violated"

    # privacy: a sponsor with no entity designator in its name and < 10 participants may be a
    # sole proprietor at a home address - withhold the street line from the published CSV.
    for s in sponsors:
        toks = set(re.sub(r"[^a-z0-9 ]+", " ", s["sponsor_name"].lower()).split())
        small = (s["max_active_latest_py"] or 0) < 10 and (num(str(s["total_participants_boy"])) or 0) < 10
        s["street_address"] = s["_street_full"]
        s["street_withheld"] = ""
        if small and not (toks & DESIGNATORS):
            s["street_address"] = ""
            s["street_withheld"] = "privacy_small_no_entity_designator"

    # ---- atlas matching
    atlas, tables = load_atlas(args.data_dir)
    ix = AtlasIndex(atlas, tables)
    print("matching ...", file=sys.stderr)
    matches = []
    for s in sponsors:
        m = match_sponsor(ix, s)
        m.update(ein=s["ein"], sponsor_name=s["sponsor_name"], sponsor_city=s["city"], sponsor_state=s["state"],
                 plan_year=s["plan_year"], active_participants=s["active_participants"])
        matches.append(m)

    if args.selftest:
        selftest(atlas, tables, ix, sponsors, matches, args.selftest)

    proposals = make_proposals(ix, sponsors, matches)
    sources = [(y, kind, fn, sha256(p), os.path.getsize(p)) for (y, kind, fn, p) in raw]
    return sponsors, matches, proposals, sources, rows_seen, ix


def selftest(atlas, tables, ix, sponsors, matches, n):
    rnd = random.Random(5500)
    sample = rnd.sample(range(len(sponsors)), min(n, len(sponsors)))
    bad = 0
    for i in sample:
        s = sponsors[i]
        loc = s["_addrs"][0] if (s["_addrs"][0][0] and not pobox(s["_addrs"][0][0])) else s["_addrs"][1]
        res = atlas.dedupe(tables, name=s["sponsor_name"], street=loc[0] if not pobox(loc[0]) else None,
                           city=loc[1], state=loc[2], zip_=loc[3])
        a2 = {h["id"] for h in res["steps"][1]["hits"]}
        mine2 = {r["org_id"] for tn, r, f, v in ix.name_idx.get(atlas.name_key(s["sponsor_name"]), [])}
        a3 = {h["id"] for h in res["steps"][2]["hits"]}
        mine3 = set()
        if loc[0] and not pobox(loc[0]):
            for st in ix.street_idx.get(atlas.street_key(loc[0]), []):
                mism = ((loc[1] and st["city"] and atlas.squash(loc[1]) != atlas.squash(st["city"])) or
                        (loc[2] and st["state"] and loc[2].upper() != st["state"].upper()) or
                        (loc[3] and st["zip"] and loc[3][:5] != st["zip"][:5]))
                if not mism:
                    mine3.add(st["site_id"])
        if a2 != mine2 or a3 != mine3:
            bad += 1
            print(f"SELFTEST MISMATCH {s['ein']} {s['sponsor_name']}: atlas2={a2} mine2={mine2} atlas3={a3} mine3={mine3}", file=sys.stderr)
    print(f"selftest: {len(sample)} sponsors vs atlas.dedupe(): {bad} mismatches (steps 2 and 3, strict locality)", file=sys.stderr)
    if bad:
        raise SystemExit(3)


CAVEAT = ("Plan participants are not employees exactly (they include eligible/covered workers and are counted at the "
          "plan, not the establishment); a plan sponsor can cover several establishments and states; the "
          "representative plan is the sponsor's largest by active participants, never a sum.")


def make_proposals(ix, sponsors, matches):
    by_ein = {s["ein"]: s for s in sponsors}
    out = []
    for m in matches:
        if m["match_class"] not in ("MATCH_ORG", "MATCH_SITE"):
            continue
        s = by_ein[m["ein"]]
        n = s["active_participants"]
        band = s["band_from_participants"]
        oid = m["org_id"]
        org = ix.by_id[oid][0]
        tn = ix.table_of[oid]
        ref = (f"DOL EFAST2 Form {s['filing_type']}, sponsor {s['sponsor_name']}, PY{s['plan_year']}, "
               f"plan {s['plan_number']}, ACK_ID {s['ack_id']}")
        base = dict(ein=s["ein"], sponsor_name=s["sponsor_name"], match_class=m["match_class"], org_id=oid,
                    site_id=m["site_id"], plan_year=s["plan_year"], active_participants=n,
                    filing_type=s["filing_type"], n_plans_latest_py=s["n_plans_latest_py"], source_ref=ref,
                    caveat=CAVEAT)
        if not band:
            out.append({**base, "target_table": "", "target_field": "", "proposed_value": "", "existing_value": "",
                        "proposal_class": "NO_COUNT", "basis": "",
                        "basis_public_text": "", "review_flags": ("only final / short-plan-year filings exist: wind-down count, never banded" if s["rep_basis"] == "final_or_short_only"
                                         else "active participants blank or 0 in the representative filing")})
            continue
        basis = f"Form 5500 plan year {s['plan_year']}, active participants {n} → band {band}"
        pub = (f"Form {s['filing_type']} plan year {s['plan_year']}: active participants in band {band} "
               f"(government_filing; plan count, not a headcount)")
        flags = []
        if tn != "organizations":
            out.append({**base, "target_table": tn, "target_field": "", "proposed_value": band, "existing_value": "",
                        "proposal_class": "NOTE_ONLY", "basis": basis, "basis_public_text": pub,
                        "review_flags": "matched record is an ecosystem row; no employee_band column"})
            continue
        if m["match_class"] == "MATCH_SITE":
            flags.append("match_via_address_not_name")
        if s["n_plans_latest_py"] > 1:
            flags.append(f"multi_plan_sponsor({s['n_plans_latest_py']}): max active used")
        if m["matched_org_status"] not in ("active", ""):
            flags.append(f"matched_org_status={m['matched_org_status']}")
        sites = ix.sites_by_org.get(oid, [])
        site_states = {(x["state"] or "").upper() for x in sites} - {""}
        conglom = (org.get("diversified_conglomerate") or "").strip().lower() in ("true", "1", "yes")
        existing = (org.get("employee_band_ohio") or "").strip()
        if conglom:
            flags.append("diversified_conglomerate")
        # ---- org level
        if s["state"] == "OH":
            if conglom or not site_states <= {"OH"} or not sites:
                why = ("diversified_conglomerate" if conglom else
                       ("org has no Atlas site rows" if not sites else f"org has non-Ohio Atlas sites ({','.join(sorted(site_states - {'OH'}))})"))
                out.append({**base, "target_table": "organizations", "target_field": "", "proposed_value": band,
                            "existing_value": existing, "proposal_class": "NOTE_ONLY", "basis": basis,
                            "basis_public_text": pub,
                            "review_flags": ";".join(flags + [f"upper bound for Ohio only, not an Ohio band: {why}"])})
            else:
                if existing in ("", "unknown"):
                    cls = "FILL"
                elif existing == band:
                    cls = "CONSISTENT"
                else:
                    cls = "CONFLICT"
                    flags.append(f"existing band {existing} differs; never overwrite without review")
                out.append({**base, "target_table": "organizations", "target_field": "employee_band_ohio",
                            "proposed_value": band, "existing_value": existing, "proposal_class": cls,
                            "basis": basis, "basis_public_text": pub, "review_flags": ";".join(flags)})
        else:
            out.append({**base, "target_table": "organizations", "target_field": "", "proposed_value": band,
                        "existing_value": existing, "proposal_class": "NOTE_ONLY", "basis": basis,
                        "basis_public_text": pub,
                        "review_flags": ";".join(flags + [f"sponsor address is {s['state'] or s['country'] or 'unknown'}, not Ohio: company-level band note, no Ohio band proposed"])})
        # ---- site level: only one Atlas establishment for the org AND the addresses match
        if m["site_id"] and len(sites) == 1 and sites[0]["site_id"] == m["site_id"]:
            st = sites[0]
            ex = (st.get("employee_band_site") or "").strip()
            cls = "FILL" if ex in ("", "unknown") else ("CONSISTENT" if ex == band else "CONFLICT")
            out.append({**base, "target_table": "sites", "target_field": "employee_band_site", "proposed_value": band,
                        "existing_value": ex, "proposal_class": cls, "basis": basis, "basis_public_text": pub,
                        "site_id": st["site_id"],
                        "review_flags": ";".join(flags + ["only one Atlas site for this org, but the Atlas may not list all of the sponsor's establishments (coverage outside Ohio is thin): integrator confirms single-establishment from the company's own site before applying"]
                                                 + (["existing band differs; never overwrite without review"] if cls == "CONFLICT" else []))})
    return out


# ------------------------------------------------------------------ output
SPONSOR_COLS = ["ein", "sponsor_name", "dba_name", "street_address", "street_withheld", "city", "state", "zip", "country",
                "address_source", "business_code", "code_granularity", "code_signal", "plan_year", "active_participants",
                "band_from_participants", "rep_basis", "total_participants_boy", "filing_type", "plan_number", "ack_id",
                "n_filings_latest_py", "n_plans_latest_py", "max_active_latest_py", "latest_filed_plan_year_any",
                "latest_date_received", "final_filing_flag_latest", "short_plan_year_flag_latest",
                "latest_py_all_final_or_short", "business_codes_seen", "plan_years_present",
                "polymer_code_filings"]
MATCH_COLS = ["ein", "sponsor_name", "sponsor_city", "sponsor_state", "plan_year", "active_participants", "match_class",
              "match_step", "org_id", "site_id", "matched_name", "matched_table", "matched_org_status", "matched_org_state",
              "org_site_count", "name_state_agree", "successor_terminal", "other_candidates", "note"]
PROP_COLS = ["ein", "sponsor_name", "match_class", "org_id", "site_id", "target_table", "target_field", "proposed_value",
             "existing_value", "proposal_class", "plan_year", "active_participants", "filing_type", "n_plans_latest_py",
             "basis", "basis_public_text", "source_ref", "review_flags", "caveat"]


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


STATE_FIPS = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC",
              "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
              "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT",
              "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
              "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
              "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY", "72": "PR"}
GAP_STATES = ["CA", "TX", "FL", "MI", "IL", "GA", "IN", "WI", "NY", "NC"]


def qcew_326(data_dir):
    p = os.path.join(os.path.dirname(os.path.abspath(data_dir)), "docs", "denominators", "qcew_state_polymer_2023_2024.csv")
    out = {}
    if not os.path.exists(p):
        return out
    with open(p, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["year"] == "2023" and r["industry_code"] == "326" and r["area_fips"].endswith("000"):
                st = STATE_FIPS.get(r["area_fips"][:2])
                if st and r["annual_avg_estabs"]:
                    out[st] = int(r["annual_avg_estabs"])
    return out


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---:" if i else "---" for i, _ in enumerate(head)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def report(args, sponsors, matches, proposals, sources, rows_seen, ix):
    today = datetime.date.today().isoformat()
    N = len(sponsors)
    mc = collections.Counter(m["match_class"] for m in matches)
    by_state = collections.defaultdict(lambda: collections.Counter())
    m_by_ein = {m["ein"]: m for m in matches}
    for s in sponsors:
        st = s["state"] or ("FOREIGN" if s["country"] else "UNKNOWN")
        c = by_state[st]
        c["all"] += 1
        if s["business_code"].startswith("326"):
            c["326"] += 1
        c["band"] += 1 if s["band_from_participants"] else 0
        c[m_by_ein[s["ein"]]["match_class"]] += 1
        if s["band_from_participants"] and (s["active_participants"] or 0) >= 50:
            c["ge50"] += 1
            if m_by_ein[s["ein"]]["match_class"] == "NO_MATCH":
                c["nm_ge50"] += 1
        if s["business_code"].startswith("326") and m_by_ein[s["ein"]]["match_class"] == "NO_MATCH":
            c["nm326"] += 1
    qc = qcew_326(args.data_dir)
    atlas_sites = collections.Counter((x["state"] or "").upper() for x in ix.sites)
    total_tab = []
    for st in sorted(by_state, key=lambda k: -by_state[k]["all"]):
        c = by_state[st]
        total_tab.append([st, c["all"], c["326"], c["band"], c["MATCH_ORG"] + c["MATCH_SITE"], c["POSSIBLE"], c["NO_MATCH"]])
    gap_tab = []
    for st in GAP_STATES:
        c = by_state[st]
        gap_tab.append([st, qc.get(st, "n/a"), atlas_sites.get(st, 0), c["all"], c["326"], c["NO_MATCH"], c["nm326"],
                        c["nm_ge50"], c["POSSIBLE"]])
    gap_tot = [sum(by_state[s][k] for s in GAP_STATES) for k in ("all", "326", "NO_MATCH", "nm326", "nm_ge50", "POSSIBLE")]
    # code mix
    codemix = collections.Counter(s["business_code"] for s in sponsors)
    code_tab = [[c, code_signal(c), code_granularity(c), n] for c, n in sorted(codemix.items(), key=lambda kv: -kv[1])]
    # size mix and match rate by size
    size_tab = []
    for b in ["1-9", "10-49", "50-99", "100-249", "250-499", "500-999", "1000-4999", "5000+", ""]:
        ss = [s for s in sponsors if s["band_from_participants"] == b]
        if not ss:
            continue
        cm = collections.Counter(m_by_ein[s["ein"]]["match_class"] for s in ss)
        mm = cm["MATCH_ORG"] + cm["MATCH_SITE"]
        size_tab.append([b or "(no active count)", len(ss), cm["MATCH_ORG"], cm["MATCH_SITE"], cm["POSSIBLE"], cm["NO_MATCH"],
                         f"{100.0 * mm / len(ss):.1f}%"])
    mm_all = mc["MATCH_ORG"] + mc["MATCH_SITE"]
    # proposals
    pc = collections.Counter((p["target_table"], p["target_field"], p["proposal_class"]) for p in proposals)
    prop_tab = [[a or "-", b or "-", c, n] for (a, b, c), n in sorted(pc.items())]
    n_prop_rows = len(proposals)
    n_prop_matches = len({p["ein"] for p in proposals})
    ohio_fill = [p for p in proposals if p["target_field"] == "employee_band_ohio" and p["proposal_class"] == "FILL"]
    ohio_cons = [p for p in proposals if p["target_field"] == "employee_band_ohio" and p["proposal_class"] == "CONSISTENT"]
    ohio_conf = [p for p in proposals if p["target_field"] == "employee_band_ohio" and p["proposal_class"] == "CONFLICT"]
    site_rows = [p for p in proposals if p["target_field"] == "employee_band_site"]
    # liveness
    pyc = collections.Counter(s["latest_filed_plan_year_any"] for s in sponsors)
    matched = [m for m in matches if m["match_class"] in ("MATCH_ORG", "MATCH_SITE")]
    s_by = {s["ein"]: s for s in sponsors}
    mact = [m for m in matched if m["matched_org_status"] == "active"]
    mact_py = collections.Counter(s_by[m["ein"]]["latest_filed_plan_year_any"] for m in mact)
    stale = [m for m in mact if s_by[m["ein"]]["latest_filed_plan_year_any"] <= 2023]
    final_flag = [m for m in mact if s_by[m["ein"]]["latest_py_all_final_or_short"] == "1"]
    non_active = [m for m in matched if m["matched_org_status"] not in ("active", "")]
    na_recent = [m for m in non_active if s_by[m["ein"]]["latest_filed_plan_year_any"] >= 2024]
    # EIN registry candidates: name exact + street match both
    ein_ready = [m for m in matches if m["match_class"] == "MATCH_ORG" and "+3" in m["match_step"]]
    ein_name_only = [m for m in matches if m["match_class"] == "MATCH_ORG" and "+3" not in m["match_step"]]
    # distinct orgs
    distinct_orgs = len({m["org_id"] for m in matched})
    ntb = collections.Counter(m["match_step"] for m in matches if m["match_class"] != "NO_MATCH")
    step_tab = [[k, v] for k, v in sorted(ntb.items())]
    n_withheld = sum(1 for s in sponsors if s["street_withheld"])
    foreign = sum(1 for s in sponsors if not s["state"])
    multi = sum(1 for s in sponsors if s["n_plans_latest_py"] > 1)
    noact = sum(1 for s in sponsors if not s["band_from_participants"])
    L = []
    A = L.append
    A(f"# Form 5500 polymer-sponsor spine - REPORT\n")
    A(f"Generated {today} by `scripts/build_form5500_spine.py`; packet-lane output, **no file under `data/` was edited, no ID allocated, no status changed**. "
      "Every row here is a lead or a proposal for the integrator of record; nothing is a verdict. "
      "Task claim: no QUEUE.md line was edited by this lane (lanes do not write shared files); the integrator should add/claim the line.\n")
    A("## 1. What this is\n")
    A("DOL EFAST2 Form 5500 and Form 5500-SF bulk \"Latest\" datasets, filtered to polymer business codes and collapsed to one row per sponsor EIN, then matched to the Atlas. "
      "Three uses: (1) an employee-size input (SCHEMA owner ruling R7f, 2026-11-01: a plan-participant count is an admissible employee-band input - `government_filing`, with plan year, always banded, never a precise headcount); "
      "(2) a national discovery spine of **employers** (sponsor EIN, not establishment); (3) a liveness signal (latest plan year filed).\n")
    A("### Source files (retrieved 2026-11-01; raw zips kept outside the repo)\n")
    A(md_table(["Plan-year file", "Form", "Zip", "Bytes", "SHA-256"],
               [[y, k, fn, f"{sz:,}", f"`{h}`"] for (y, k, fn, h, sz) in sources]))
    A("\nURL pattern: `https://askebsa.dol.gov/FOIA%20Files/<YEAR>/Latest/<zip>`; index page <https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/public-disclosure/foia/form-5500-datasets>. "
      "Column names were confirmed against the published `*_layout.txt` and the 2024 form PDFs (data-dictionary zip). 2023, 2024 and 2025 file sets were all used: 2024 is complete enough on its own, "
      "but 2023 supplies sponsors that have not (yet) filed 2024 and 2025 supplies the freshest liveness signal. "
      "**The 2025 file set is incomplete** (measured 2026-11-01: plan-year-2025 filings in the 2025 Latest files are ~100k Form 5500 / ~621k SF against ~219k / ~773k plan-year-2024 filings in the 2024 files; large-plan filings on extension were still arriving at the 2026-09-25 dataset date), so absence from PY2025 is not a signal. "
      "The 2025 files also carry plan-year-**2026** rows: short plan years (tax period ends in early 2026) - plan wind-downs, not typos.\n")
    A("### Field definitions used\n")
    A("- **Active participants** = Form 5500 `TOT_ACTIVE_PARTCP_CNT` (line 6a(2), active participants at the **end** of the plan year) / Form 5500-SF `SF_TOT_ACT_PARTCP_EOY_CNT` (line 5d(2)). `total_participants_boy` = `TOT_PARTCP_BOY_CNT` / `SF_TOT_PARTCP_BOY_CNT` (all participants incl. retirees, beginning of year) is carried for context only and never banded.")
    A("- **Business code** = `BUSINESS_CODE` / `SF_BUSINESS_CODE`, the filer-selected code from the IRS list printed in the form instructions. Source type for any NAICS taken from it: `government_filing`; confidence no higher than `medium` (filer-selected, mostly padded group codes).")
    A("- **Polymer set** = every code starting 3252, 3255, 3259, 326 plus Ring 3 Primary 333511 / 424610 / 562920 (SCHEMA 2.2). Form 5500 filers mostly use padded group codes, so the effective set is: "
      + ", ".join(f"`{c}` ({n})" for c, _, _, n in code_tab[:12]) + ". Sponsors per code are in section 3.")
    A("- **One row per sponsor EIN.** Latest plan year Y = latest plan-year-begin year among polymer-coded filings. Representative filing = most active participants among **all** the EIN's filings for Y (any code), because one sponsor's plans overlap (the same employees are in the 401(k) and the health plan): MAX, never the sum. `n_plans_latest_py` / `max_active_latest_py` expose multi-plan sponsors.")
    A("- **Final and short-year filings never set a band.** A filing with the final-filing flag or the short-plan-year flag reports a wind-down (active participants are typically 0 with participants still listed at the beginning of the year). Y above is therefore the latest plan year among *operating* (non-final, non-short) polymer-coded filings; only a sponsor with no operating filing falls back to its final/short filing and is left unbanded (`rep_basis = final_or_short_only`). The liveness columns (`latest_filed_plan_year_any`, `final_filing_flag_latest`, `short_plan_year_flag_latest`, `latest_py_all_final_or_short`) still look at **all** filings.\n")
    A("## 2. Headline counts\n")
    A(f"Unit: **unique sponsor EINs** (employers, not establishments) with at least one Form 5500 / 5500-SF filing in the 2023-2025 file sets coded to the polymer set.\n")
    A(md_table(["Measure", "Value"], [
        ["Polymer-coded filings read (rows, all years, both forms)", f"{sum(rows_seen.values()):,}"],
        ["Unique sponsor EINs (rows in sponsors.csv)", f"{N:,}"],
        ["... with a US state on the address", f"{N - foreign:,}"],
        ["... foreign / no US state", f"{foreign:,}"],
        ["... with active participants >= 1 (bandable)", f"{N - noact:,}"],
        ["... with active participants blank or 0 (not bandable)", f"{noact:,}"],
        ["... of which only final / short-plan-year filings exist (`rep_basis` = final_or_short_only)", f"{sum(1 for s in sponsors if s['rep_basis'] == 'final_or_short_only'):,}"],
        ["... multi-plan sponsors in latest plan year (n_plans_latest_py > 1)", f"{multi:,}"],
        ["... street line withheld for privacy (no entity designator and < 10 participants)", f"{n_withheld:,}"],
        ["Sponsors by latest plan year filed (any code)", "; ".join(f"PY{y}: {n:,}" for y, n in sorted(pyc.items(), reverse=True))],
    ]))
    A("\nRows read per file (polymer-coded only):\n")
    A(md_table(["Plan-year file", "Form", "Polymer-coded filings"], [[y, k, f"{n:,}"] for (y, k), n in sorted(rows_seen.items())]))
    A("\n## 3. Sponsors by state (all sponsors, polymer set)\n")
    A("Unit: unique sponsor EINs by the state on the representative filing's address (location address if present, else mailing). `326-coded` = sponsors whose polymer code starts 326 (plastics/rubber products, the QCEW 326 comparison set).\n")
    A(md_table(["State", "Sponsor EINs", "326-coded", "Bandable", "Matched (ORG+SITE)", "POSSIBLE", "NO_MATCH"], total_tab))
    A("\n### Sponsors by polymer business code\n")
    A(md_table(["Business code", "SCHEMA 2.2 signal", "Granularity", "Sponsor EINs"], code_tab))
    A("\nPadded group codes (`...00`) cover several 6-digit NAICS codes, so **the Form 5500 code never settles a 6-digit NAICS, a ring or a scope claim**; it is a discovery lead and a coarse industry signal (SCHEMA 2.1, 'NAICS is a signal for discovery... never the Ring decision alone'). "
      "325900 and 325200 mix Primary, Secondary and Exclude codes (e.g. 325920 explosives) and are the noisiest.\n")
    A("## 4. Match to the Atlas\n")
    A("Method: same normalizers and step order as `scripts/atlas.py dedupe-check` (AGENTS.md section 3). Step 1 (domain) cannot run - Form 5500 has no website. "
      f"Cross-check: this run re-ran {args.selftest} random sponsors through `atlas.dedupe()` itself (`--selftest`) and the step 2 and step 3 hit sets were identical (0 mismatches; a mismatch aborts the build). "
      "Classes:\n")
    A("- **MATCH_ORG**: step 2 normalized name equals an Atlas legal_name / trade_name **and** the sponsor state is the org's HQ state or one of its site states (`+3` in `match_step` = a step-3 street+locality hit on a site of that same org as well).")
    A("- **MATCH_SITE**: step 3 street + locality (same state and ZIP5 or city) equal an Atlas site, and the sponsor name shares its first non-generic token with the operator / site / trade names.")
    A("- **POSSIBLE**: anything weaker - name equal but state conflicts, street equal but name differs (multi-tenant / parent address), fuzzy name (suffix/plural/holding words stripped), or a step-4 hit in trade_names/notes. Needs a human; never merged.")
    A("- **NO_MATCH**: no hit at any step run. Not evidence the establishment is absent from the Atlas under another name or that it is in scope.\n")
    A(md_table(["Match class", "Sponsor EINs", "Share of sponsors"], [[k, f"{mc[k]:,}", f"{100.0 * mc[k] / N:.1f}%"] for k in ("MATCH_ORG", "MATCH_SITE", "POSSIBLE", "NO_MATCH")]
               + [["**Total**", f"{N:,}", "100%"]]))
    A(f"\n**Match rate (MATCH_ORG + MATCH_SITE) = {mm_all:,} of {N:,} sponsor EINs = {100.0 * mm_all / N:.1f}%**; matched sponsors resolve to {distinct_orgs:,} distinct Atlas organizations/ecosystem rows. "
      f"With POSSIBLE included the upper bound is {100.0 * (mm_all + mc['POSSIBLE']) / N:.1f}%.\n")
    A("Match step distribution (non-NO_MATCH rows):\n")
    A(md_table(["match_step", "Sponsor EINs"], step_tab))
    A("\nMatch rate by employee-size band of the sponsor (band from active participants):\n")
    A(md_table(["Band", "Sponsors", "MATCH_ORG", "MATCH_SITE", "POSSIBLE", "NO_MATCH", "Match rate"], size_tab))
    A("\nRead the size table first: a high match rate in the large bands and a low one in the small bands is the expected shape (Atlas discovery was biased to larger employers and to Ohio). Sponsor-to-establishment is not 1:1, so a NO_MATCH sponsor with 500 participants is a lead for one or more establishments, not a count of missing plants.\n")
    A("## 5. Employee-band proposals (MATCH rows only)\n")
    A(f"`band_proposals.csv` has {n_prop_rows:,} rows covering {n_prop_matches:,} matched sponsor EINs (one org-level row per matched sponsor, plus a site-level row only where the org has exactly one Atlas site, that site is the address match, and so the sponsor and the establishment coincide). "
      "Basis text on every row: `Form 5500 plan year YYYY, active participants N -> band`; `basis_public_text` is the band-only wording to put in any evidence row, because R7f says **never a precise headcount** - the exact N appears only in the lane-internal `basis` column.\n")
    A(md_table(["Target table", "Target field", "Proposal class", "Rows"], prop_tab))
    A("\nProposal classes: **FILL** = existing value blank/unknown; **CONSISTENT** = existing band equals the proposal; **CONFLICT** = existing band differs (never overwrite without review - the existing band may be an Ohio-site band from a better source); "
      "**NOTE_ONLY** = no field push: sponsor address is not Ohio (`employee_band_ohio` is an Ohio band), or the org has non-Ohio Atlas sites / is a diversified conglomerate (the plan then covers more than Ohio, so the band is only an upper bound for Ohio), or the matched row is an ecosystem row; **NO_COUNT** = representative filing carries no active participants.\n")
    A(f"- Ohio org-level `employee_band_ohio`: **{len(ohio_fill):,} FILL**, {len(ohio_cons):,} CONSISTENT, {len(ohio_conf):,} CONFLICT.")
    A(f"- Site-level `employee_band_site` rows: {len(site_rows):,} (single-establishment orgs with address match only).")
    big = [p for p in ohio_fill if p["proposed_value"] in ("250-499", "500-999", "1000-4999", "5000+")]
    A(f"- Derived-field effect to expect: {len(big):,} of the Ohio FILL proposals are in a 250+ band; `employee_band_ohio` is an input to the derived `tier1_qualifier` leg `employees_250plus` (SCHEMA 4.4), so applying them will change derived output at the next derivation pass. `tier1_qualifier` itself is never hand-edited (AGENTS.md section 1).")
    A("- Caveats carried in every row: " + CAVEAT)
    A("- Integration route: these are packets. An integrator applies them one writer per file, with `employee_count_source_date` and a `government_filing` evidence row per band (SCHEMA 4.13); FILL rows still need the integrator's own look at multi-plan and MATCH_SITE flags.\n")
    A("## 6. Discovery leads (NO_MATCH) by state\n")
    A("Unit: unique sponsor EINs with no Atlas hit at any step. **These are employers with an ERISA plan, not verified establishments**; each still needs the full create path (AGENTS.md sections 3-4: dedupe on the establishment's own domain/address, primary-source existence + scope evidence, tier U/C at birth; a platform/roster category such as a business code is a discovery lead and never supports a scope claim). "
      "The Form 5500 business code is filer-chosen and coarse, so expect noise (325900/325200 especially) and out-of-scope filers (e.g. plastics distributors, paint/coating blenders under 325500).\n")
    A("Largest QCEW NAICS 326 gap states (`docs/denominators/README.md`: QCEW 2023 private 326 establishments minus Atlas strict sites). Columns: QCEW 326 establishments 2023 | Atlas site rows in state (all rows) | sponsors | 326-coded sponsors | NO_MATCH sponsors | NO_MATCH 326-coded | NO_MATCH with >= 50 active participants | POSSIBLE (review first).\n")
    A(md_table(["State", "QCEW 2023 326 estabs", "Atlas site rows", "Sponsor EINs", "326-coded", "NO_MATCH leads", "NO_MATCH 326-coded", "NO_MATCH >= 50 active", "POSSIBLE"], gap_tab
               + [["**Top-10 gap states**", "", "", f"{gap_tot[0]:,}", f"{gap_tot[1]:,}", f"{gap_tot[2]:,}", f"{gap_tot[3]:,}", f"{gap_tot[4]:,}", f"{gap_tot[5]:,}"]]))
    A("\nSponsor counts are employers (a multi-plant employer is one EIN) and QCEW counts establishments, so the two columns are different units and must never be divided to get 'coverage'. They show where the unmatched employer leads sit relative to the Atlas gap.\n")
    A("All-state NO_MATCH counts are in the section 3 table (column NO_MATCH) and in `matches.csv` (filter `match_class=NO_MATCH`, join to `sponsors.csv` on `ein` for name/address/size).\n")
    A("## 7. Liveness use (signal only - never a status change)\n")
    A("A sponsor's latest filed plan year and its `final_filing_flag_latest` are **plan facts**. Per AGENTS.md section 3: a final Form 5500 filing is a plan fact, never a status change; an operating-status change needs dated primary evidence; a failed or absent fetch is never evidence of closure. "
      "Used this way:\n")
    A("- **Positive signal (operating-evidence lead):** a matched, Atlas-`active` org whose EIN filed a plan year 2024 or 2025 with active participants > 0 is a dated government-filing activity witness (SCHEMA 4.4 `last_activity_evidence_date` floor / `liveness_signal=operating_evidence` are the integrator's call, and only where the filing's address **is** the establishment in question - AGENTS.md section 2 rule 8).")
    A("- **Owes-a-look signal:** a final-filing flag, or no filing in the latest complete plan year, on a matched `active` org is the 'closure signature' ingredient SCHEMA 4.4 describes - it queues a direct liveness check and nothing more.\n")
    A(md_table(["Measure (unit: matched sponsor EINs whose Atlas row is status=active)", "Count"], [
        ["Matched sponsors (ORG+SITE) whose Atlas row is `active`", f"{len(mact):,}"],
        ["... latest filed plan year 2025 (partial year)", f"{mact_py[2025]:,}"],
        ["... latest filed plan year 2024", f"{mact_py[2024]:,}"],
        ["... latest filed plan year 2023 or earlier (no 2024/2025 filing found in these files)", f"{len(stale):,}"],
        ["... every filing of the latest plan year is a final or short-plan-year filing (plan wind-down; a plan fact, not a status)", f"{len(final_flag):,}"],
        ["Matched sponsors whose Atlas row is NOT active (tombstoned/other) yet filed PY2024+", f"{len(na_recent):,}"],
    ]))
    if stale or final_flag:
        A("\nOrgs to queue for a direct liveness look (lead only; IDs from `matches.csv`):\n")
        ids = sorted({m["org_id"] for m in stale + final_flag})
        A("`" + ", ".join(ids[:60]) + "`" + (f" ... (+{len(ids) - 60} more)" if len(ids) > 60 else ""))
    seeds = [(r["org_id"], r["legal_name"]) for tn, r in ix.orgs if tn == "organizations" and (r.get("liveness_signal") or "") == "closure_signature"]
    if seeds:
        sm = {m["org_id"]: m for m in matched}
        lines = []
        for oid, nm in seeds:
            m = sm.get(oid)
            if m:
                s2 = s_by[m["ein"]]
                lines.append(f"{oid} ({nm}): matched sponsor EIN {m['ein']}, latest filed plan year {s2['latest_filed_plan_year_any']}, all latest-year filings final/short = {s2['latest_py_all_final_or_short']}")
            else:
                lines.append(f"{oid} ({nm}): no matched sponsor in this spine")
        A("\nCross-check against the Atlas's existing `liveness_signal=closure_signature` seed(s): " + "; ".join(lines) + ".")
    A("\nCaveats: PY2025 is partial; a sponsor can be acquired and its EIN retired while the establishment keeps operating (look for a successor EIN: `LAST_RPT_SPONS_EIN` is in the raw files, not carried here); a filing's address is usually the HQ/administrative address, not the plant; a sponsor filing blocks a REJECT for closure only when its address is the establishment (AGENTS.md section 2 rule 8). Nothing in this report changes any `status`.\n")
    A("## 8. OWNER item - registry value for employer EINs\n")
    A("**Question.** `registry_links.registry` (SCHEMA 4.8) has `EIN_NONPROFIT` only (ProPublica, nonprofits). Form 5500 publishes the sponsor EIN for every employer-sponsored plan, i.e. an EIN for ordinary for-profit employers is now obtainable from a government bulk source - the section 4.8 sentence 'no bulk EIN source is adopted' no longer holds. Should an employer-EIN registry value be added?\n")
    A(f"**Recommendation: yes - add a single `EIN` registry value (dated schema revision; this is a vocabulary change, so an owner ruling per AGENTS.md section 2 rule 9 - not settled here).** Reasons: (a) the EIN is the exact join key for Form 5500, IRS EO/BMF, PPP, SBA and many state filings, turning later name-matching into key-matching (the UEI doctrine applied to employers); "
      "(b) the table is already multi-value by design, which fits a parent org holding several legal-entity EINs; (c) a second value just for for-profits (`EIN_EMPLOYER`) would split one identifier across two enum values with no semantic difference - the cleaner path is one `EIN` value, with `EIN_NONPROFIT` grandfathered as-is (or aliased to `EIN` in the same revision). "
      "Proposed mint rule, mirroring UEI/FRS: mint only where the EIN's own filing is the witness **and** the link is not by name resemblance alone - require MATCH_ORG with a step-3 street+locality hit on a site of that org (name AND address agree), `registry_id` = 9 digits verbatim, "
      "`match_basis` e.g. `form5500_sponsor_ein_name_address:PY2024`, `as_of` = retrieval date. An EIN seen only in this project's own files is a phantom and mints nothing (AGENTS.md section 4).\n")
    A(f"Yield under that rule today: **{len(ein_ready):,}** sponsor EINs are mint-ready (MATCH_ORG with step `2+3`); a further {len(ein_name_only):,} MATCH_ORG sponsors agree on name and state but have no address hit (most Atlas Ohio sites lack `street_address`: Ohio site street_address fill was 7.2% per the field-fill profile), so they would wait for an address or a second witness. "
      "Cautions for the owner: an EIN identifies a legal entity, not an establishment or a brand, and sole-proprietor/individual EINs exist - the Atlas records employers that are businesses, and the mint rule above never touches an entity that is a natural person; the rule above applies a vocabulary only - no row is minted by this lane.\n")
    A("## 9. Blockers, limits and honest caveats\n")
    A("- **Employer, not establishment.** One EIN may operate many plants; sponsor address is usually HQ/administration. Discovery rows yield employers to research, not sites.")
    A("- **Coverage bias.** Only employers sponsoring a retirement or (for 100+ participants / funded) welfare plan that files a 5500 or 5500-SF appear; one-participant plans file 5500-EZ (not in these datasets); small shops without a plan are invisible. Under-representation of the smallest establishments is structural.")
    A("- **Participants are not employees.** They include covered workers and leased/related-employer coverage under controlled-group and multiple-employer plans (a PEO or MEP sponsor can show participants at other employers). Treat the band as a plan-size input (R7f), not a headcount.")
    A("- **Code granularity.** See section 3: padded group codes only; 6-digit polymer codes are rare, and the Ring 3 Primary codes 424610/562920 do not exist in the Form 5500 code list (only 333511 appears, a handful of times) - Ring 3 distribution/recycling is not discoverable by this source.")
    A(f"- **Privacy.** Only business sponsor fields are published; no phone, email, officer or preparer names. {n_withheld:,} street lines are withheld where the sponsor name has no entity designator and the plan has fewer than 10 participants (possible home address, AGENTS.md section 6). Matching used the full address in memory before withholding.")
    A("- **Queue.** This lane did not touch `tasks/QUEUE.md` or `data/`; a QUEUE line and an integrator pass are needed before any band or EIN is applied.")
    A("- **Re-run:** `python3 scripts/build_form5500_spine.py --raw-dir /tmp/claude-0/f5500_raw --selftest 300` (downloads missing zips; deterministic apart from newly published DOL files).")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--raw-dir", default="/tmp/claude-0/f5500_raw")
    ap.add_argument("--out-dir", default=os.path.join(REPO, "tasks", "form5500-spine-2026-11-01"))
    ap.add_argument("--data-dir", default=os.path.join(REPO, "data"))
    ap.add_argument("--years", default="2025,2024,2023")
    ap.add_argument("--selftest", type=int, default=0, help="cross-check N random sponsors against atlas.dedupe()")
    args = ap.parse_args(argv)
    sponsors, matches, proposals, sources, rows_seen, ix = build(args)
    os.makedirs(args.out_dir, exist_ok=True)
    write_csv(os.path.join(args.out_dir, "sponsors.csv"), SPONSOR_COLS, sponsors)
    write_csv(os.path.join(args.out_dir, "matches.csv"), MATCH_COLS, matches)
    write_csv(os.path.join(args.out_dir, "band_proposals.csv"), PROP_COLS, proposals)
    with open(os.path.join(args.out_dir, "REPORT.md"), "w", encoding="utf-8") as f:
        f.write(report(args, sponsors, matches, proposals, sources, rows_seen, ix))
    mc = collections.Counter(m["match_class"] for m in matches)
    print(f"sponsors {len(sponsors)}; matches {dict(mc)}; proposal rows {len(proposals)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
