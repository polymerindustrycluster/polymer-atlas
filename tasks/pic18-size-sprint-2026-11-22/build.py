#!/usr/bin/env python3
"""PIC-18 size-sprint packet (SCHEMA §1 R13). Packet lane: reads data/ and the raw store, writes ONLY under --out.
Matches raw filings to sites itself (street_key + held name); trusts no earlier match file.
Stage 1 (extract_oh.py) streams the store to an Ohio-only cache; this script does the matching.
usage: build.py --cache DIR --out DIR [--sample N --seed 20261122]  (sample = canary: first N of a seeded shuffle of the frame)"""
import argparse, csv, glob, random, re, sys
from collections import defaultdict, Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from atlas import street_key, name_key, site_name_key, org_name_fields, squash  # noqa: E402
from derive_last_activity import same_street  # noqa: E402
from regions import PIC18  # noqa: E402
csv.field_size_limit(10**9)
BANDS = ["1-9", "10-49", "50-99", "100-249", "250-499", "500-999", "1000-4999", "5000+"]
UPPER = [9, 49, 99, 249, 499, 999, 4999]

def band_of(n):
    n = int(n)
    if n < 1: return ""
    for i, hi in enumerate(UPPER):
        if n <= hi: return BANDS[i]
    return "5000+"
def num(v):
    try: return int(float((v or "").replace(",", "")))
    except ValueError: return 0
def dist(a, b): return abs(BANDS.index(a) - BANDS.index(b))
def zip5(z): return re.sub(r"\D", "", z or "")[:5]

def load_atlas(data=None):
    data = Path(data) if data else ROOT / "data"; orgs = {}
    for f in glob.glob(str(data / "organizations_*.csv")) + [str(data / "ecosystem.csv")]:
        for r in csv.DictReader(open(f, newline="", encoding="utf-8")):
            r.setdefault("legal_name", r.get("name", "")); orgs[r["org_id"]] = r
    sites = [r for f in sorted(glob.glob(str(data / "sites_*.csv"))) for r in csv.DictReader(open(f, newline="", encoding="utf-8"))]
    return orgs, sites

def org_names(o, orgs, depth=0):
    """(key, display) pairs for every name the org holds, plus named parent(s)."""
    out = {name_key(v): v for _, v in org_name_fields(o) if name_key(v)}
    if o.get("ultimate_parent_name") and name_key(o["ultimate_parent_name"]): out.setdefault(name_key(o["ultimate_parent_name"]), "parent:" + o["ultimate_parent_name"])
    p = orgs.get(o.get("parent_org_id") or "")
    if p and depth < 3:
        for k, v in org_names(p, orgs, depth + 1).items(): out.setdefault(k, v if v.startswith("parent:") else "parent:" + v)
    return out
def held_names(site, orgs):
    h = dict(org_names(orgs.get(site["org_id"], {"legal_name": ""}), orgs))
    for v in (site["site_name"], ):
        for k in (name_key(v), site_name_key(v, site["city"])):
            if k: h[k] = site["site_name"]
    return h
def name_hit(held, *names):
    for n in names:
        for k in {name_key(n), site_name_key(n, "")}:
            if k and k in held: return held[k]
    return None

REGIONS = {"pic18": lambda c: c in PIC18, "ohio_outside_pic18": lambda c: bool(c) and c not in PIC18}   # the region is a parameter (controller 2026-11-22)

def frame(orgs, sites, region="pic18"):
    gt = defaultdict(list); in_region = REGIONS[region]
    for s in sites:
        if s["state"] == "OH" and in_region(s["county"]) and s["operating_status"] == "active" and s["verification_tier"] in ("A", "B", "C"):
            gt[s["org_id"]].append(s)
    toks = lambda v: {t.strip() for t in (v or "").split(";") if t.strip() and t.strip() != "unknown"}
    unk = [o for o, ss in gt.items() if not (set().union(*(toks(s["employee_band_site"]) for s in ss)) or toks(orgs.get(o, {}).get("employee_band_ohio")))]
    return sorted((s for o in unk for s in gt[o]), key=lambda s: s["site_id"]), len(gt), len(unk)

DIRS = {"n", "s", "e", "w", "ne", "nw", "se", "sw", "north", "south", "east", "west"}
SUFX = {"st", "ave", "rd", "dr", "blvd", "hwy", "ln", "ct", "pl", "pkwy", "cir", "way", "trl", "street", "avenue", "road", "drive", "lane", "court", "parkway", "circle", "trail", "boulevard", "highway"}
CORP = {"inc", "incorporated", "llc", "corp", "corporation", "co", "company", "ltd", "limited", "lp", "llp", "holdings", "holding", "group", "us", "usa", "americas"}   # owner ruling 2026-11-22 B (plus the phrase "north america")
WINDOW_LO = "2020-11-22"   # one year before the cutoff: pending-owner window (controller 2026-11-22)
CUTOFF = "2021-11-22"   # owner ruling 2026-11-22 A: a filing sets a band only if its source date is on or after this
RANK = {"exact": 3, "corporate_suffix_only": 2, "contained_other": 1, "not_held": 0, "parent_name_lead": 0}   # owner ruling 2026-11-22 (round 9): a filing that names only a recorded parent never binds by machine
LEVELS = {"strict": 3, "suffix": 2, "contain": 1}   # minimum name rank each level accepts
SIZE_BANDS = {"1": {"1-9", "10-49"}, "21": {"10-49", "50-99"}, "22": {"100-249"}, "2": {"10-49", "50-99", "100-249"}, "3": {"250-499", "500-999", "1000-4999", "5000+"}}

def coll(k):
    """collapse runs of single letters ("h b chemical" -> "hb chemical"): dotted initials are a spelling, not a different name"""
    out, run = [], ""
    for t in k.split():
        if len(t) == 1 and t.isalpha(): run += t; continue
        if run: out.append(run); run = ""
        out.append(t)
    if run: out.append(run)
    return " ".join(out)

def drop_na(toks):
    """remove the corporate phrase "north america" from extra tokens"""
    out, i = [], 0
    while i < len(toks):
        if toks[i:i + 2] == ["north", "america"]: i += 2
        else: out.append(toks[i]); i += 1
    return out

def _best(held, names):
    """-> (class, held display name) best over the filing's names. exact | corporate_suffix_only | contained_other | not_held"""
    best = ("not_held", "")
    held = {coll(k): v for k, v in held.items()}
    for n in names:
        fk = {coll(name_key(n)), coll(site_name_key(n, ""))} - {""}
        hit = next((held[k] for k in fk if k in held), None)
        if hit: return "exact", hit
        ft = coll(name_key(n)).split()
        for hk, disp in held.items():
            ht = hk.split()
            if not ht or not ft: continue
            c = "not_held"
            if ft[:len(ht)] == ht and len(ft) > len(ht) and set(drop_na(ft[len(ht):])) <= CORP: c = "corporate_suffix_only"
            elif min(len(ft), len(ht)) >= 2 and (set(ft) <= set(ht) or set(ht) <= set(ft)): c = "contained_other"
            if RANK[c] > RANK[best[0]]: best = (c, disp)
    return best

BIZ = set("""inc incorporated llc corp corporation co company companies ltd lp llp plc usa us group holdings holding industries industrial industry plastics plastic rubber polymer polymers chemical chemicals
products product manufacturing mfg machine machines machining tool tooling mold molding foam foams metal metals steel supply services service systems technologies technology tech international american america
center centre hospital hospitals university college school city county church association society institute laboratory laboratories labs lab associates partners enterprises engineering equipment
packaging packaged printing graphics coatings coating paint adhesives composites fiberglass fibre fiber glass wire cable seal seals sealing gasket extrusion extrusions extruded fabricating fabrication
distribution distributors logistics transport trucking freight energy power electric electrical medical dental health care clinic pharmacy foods food farm farms mills mill works plant
division dept department management consulting solutions design designs controls control instruments instrument optical vision labs research development bag bags box boxes container containers
tire tires auto automotive truck trailer trailers marine boat boats pool pools roofing roof building buildings construction contractors contracting concrete cement stone wood lumber furniture
global national united first general universal precision quality superior advanced applied custom premier standard pioneer summit eagle star""".split())
def personal(n):
    """an individual's name: two or three alphabetic words (initials allowed), none a business word"""
    if not re.fullmatch(r"[A-Za-z][A-Za-z .,'-]*", n.strip()): return False
    toks = [t.strip(".,'-").lower() for t in n.replace(",", " ").split()]; toks = [t for t in toks if t]
    return 2 <= len(toks) <= 3 and not any(t in BIZ for t in toks)
def scrub(text, per_kind, notes=None):
    """replace, in a hold's free text, every source name of this site's candidate rows that looks like an individual (names of natural persons never enter the public task files)"""
    names = {n for k in per_kind for e, _, _ in per_kind[k] for n in e["names"]} | {n for k in (notes or {}) for _, e, _ in notes[k] for n in e["names"]}
    for n in sorted((n for n in names if personal(n)), key=len, reverse=True): text = text.replace(n, "[individual filer]")
    return text

def parent_match(held, names):
    """True when a filing name matches a recorded parent (exact or corporate words), whatever it also matches"""
    return _best({k: v for k, v in held.items() if v.startswith("parent:")}, names)[0] in ("exact", "corporate_suffix_only")

PARENT_FACT = "a filing names a recorded parent, not the operator (owner ruling 2026-11-22, round 9: a parent name never binds by machine); a record link or the operator's own page tying the establishment to this operator would settle it"
def parent_lead_any(held, per_kind):
    return any(fresh(e) and parent_match(held, e["names"]) and RANK[c] < 2 for k in per_kind for e, c, _ in per_kind[k])

def name_class(held, names):
    """own names only bind. A filing that matches only a recorded parent (exact or corporate words) is `parent_name_lead`: never a held name."""
    own = {k: v for k, v in held.items() if not v.startswith("parent:")}
    best = _best(own, names)
    if RANK[best[0]] == 0:
        par = _best({k: v for k, v in held.items() if v.startswith("parent:")}, names)
        if par[0] in ("exact", "corporate_suffix_only"): return ("parent_name_lead", par[1])
    return best

def civic(t): return re.sub(r"(?<=\d)[a-z]$", "", t)
def near_street(site_street, printed):
    """Same civic number (a trailing unit letter ignored) and same street-name words once directionals and the suffix word are dropped; street_key differs."""
    ta, tb = street_key(site_street).split(), street_key(printed).split()
    if not ta or not tb or ta == tb or civic(ta[0]) != civic(tb[0]) or not re.search(r"\d", ta[0]): return False
    core = lambda t: [x for x in t[1:] if x not in DIRS and x not in SUFX]
    return bool(core(ta)) and core(ta) == core(tb)

def zip5(z): return re.sub(r"\D", "", z or "")[:5]
def city_ok(site, city, zp): return squash(city) == squash(site["city"]) or bool(zip5(zp) and zip5(zp) == zip5(site["zip"]))
def rd(p): return list(csv.DictReader(open(p, newline="", encoding="utf-8")))

def unify(rows, kind):
    out = []
    for r in rows:
        if kind == "ita": addrs, names = [(r["street_address"], r["city"], r["zip_code"])], [r["establishment_name"], r["company_name"]]
        elif kind == "insp": addrs, names = [(r["site_address"], r["site_city"], r["site_zip"])], [r["estab_name"]]
        else: addrs, names = [(r["loc1"], r["loccity"], ""), (r["mail1"], r["mailcity"], "")], [r["sponsor"], r["dba"]]
        for st, c, z in addrs:
            if st.strip(): out.append(dict(r=r, st=st, city=c, zip=z, names=[n for n in names if n.strip()], kind=kind))
    return out
def index(entries):
    ex, nr = defaultdict(list), defaultdict(list)
    for e in entries:
        k = street_key(e["st"])
        if not k: continue
        ex[k].append(e); nr[(civic(k.split()[0]), squash(e["city"]))].append(e)
    return ex, nr

WITHDRAW = set()

def shown_st(e):
    """a Form 5500 sponsor mailing line is never published (owner round 12); equality is still tested on it"""
    return "[mailing street not published]" if e["kind"] == "f5500" else e["st"]

def year_of(e):
    r = e["r"]
    return int(float(r["year_filing_for"])) if e["kind"] == "ita" else int(r["open_date"][:4]) if e["kind"] == "insp" else int(r["plan_year"][:4])
def source_date(e):
    """ITA: 31 Dec of the filing year; inspection: open date; Form 5500: plan year end (tax period end, else begin + 1 year - 1 day)"""
    r = e["r"]
    if e["kind"] == "ita": return f"{int(float(r['year_filing_for']))}-12-31"
    if e["kind"] == "insp": return r["open_date"][:10]
    b = r["plan_year"][:10]
    return r["tax_prd"][:10] if r.get("tax_prd") and r["tax_prd"][:10] >= b else f"{int(b[:4]) + 1}{b[4:]}"
def fresh(e): return source_date(e) >= CUTOFF

def count_of(e):
    r = e["r"]; return num(r["annual_average_employees"] if e["kind"] == "ita" else r["nr_in_estab"] if e["kind"] == "insp" else r["active"])

def classify(site, held, ix):
    """-> (street_equal [(entry, class, held_name)], notes [(kind, entry, text)]) for one source index"""
    ex, nr = ix; eq, notes = [], []
    sk = street_key(site["street_address"])
    for e in ex.get(sk, []):
        if not same_street(site["street_address"], e["st"]): continue
        c, h = name_class(held, e["names"])
        if city_ok(site, e["city"], e["zip"]): eq.append((e, c, h))
        elif c == "exact": notes.append(("street_equal_city_conflict", e, f"street equal and name held but city {e['city']!r} / ZIP {e['zip']!r} conflict with the site"))
    for e in nr.get((civic(sk.split()[0]), squash(site["city"])), []) if sk else []:
        if street_key(e["st"]) != sk and near_street(site["street_address"], e["st"]) and name_class(held, e["names"])[0] == "exact":
            notes.append(("street_near_differs", e, f"name held, street {shown_st(e)!r} vs site {site['street_address']!r} differs in suffix/directional/unit letter only"))
    return eq, notes

def size_flag(r):
    """ITA size code vs annual average (SCHEMA-independent): consistent | code_conflicts_with_average | no_code"""
    try: code = str(int(float(r["size"])))
    except ValueError: return "no_code"
    if code not in SIZE_BANDS: return "no_code"
    b = band_of(num(r["annual_average_employees"])) if num(r["annual_average_employees"]) >= 1 else ""
    return "consistent" if not b or min(dist(b, x) for x in SIZE_BANDS[code]) <= 1 else "code_conflicts_with_average"

PARTIAL_NAME = re.compile(r"\b(unions?|bargain\w*|collective\w*|steel\s*workers?|teamsters?|hourly|salaried|ufcw|uaw|ibew|iuoe|laborers|pipefitters|plumbers|carpenters|machinists|retirees?)\b|\blocal\s*(no\.?|#)?\s*\d", re.I)
def partial_plan(r):
    """Form 5500 fields tested: PLAN_NAME / SF_PLAN_NAME (union, bargaining, hourly, salaried, local-number words), COLLECTIVE_BARGAIN_IND (main form only; the 5500-SF has no such field),
    and TYPE_PENSION_BNFT_CODE / TYPE_WELFARE_BNFT_CODE (a welfare-only plan counts benefit enrolment, not the workforce). Returns the reason or ''."""
    if PARTIAL_NAME.search(r["plan_name"] or ""): return "plan name says union, bargaining, hourly, salaried or a numbered local"
    if (r.get("cb") or "").strip() == "1": return "collective bargaining indicator set"
    if (r.get("welfare") or "").strip() and not (r.get("pension") or "").strip(): return "welfare-benefit plan only (no pension feature code)"
    return ""

def choose(kind, ok, n_active=None, peers=()):
    """ok = [(entry, class, held_name)] already filtered to the accepted name level. -> ('fill', payload) | ('hold', reason, detail, blocking)"""
    if kind == "ita":
        by = defaultdict(list)
        for e, c, h in ok:
            if count_of(e) >= 1: by[year_of(e)].append((e, c, h))
        if not by: return ("hold", "ita_no_positive_count", "name+street ITA filings carry no positive annual average employees", False)
        y = max(by); rows = by[y]
        if len({squash(e["r"]["establishment_name"]) for e, _, _ in rows}) > 1: return ("hold", "ita_multiple_establishments_at_street", f"CY{y} has {len({squash(e['r']['establishment_name']) for e, _, _ in rows})} ITA establishments at this street under held names; which one is this site (or their sum) settles it", True)
        mine = {squash(e["r"]["establishment_name"]) for e, _, _ in rows}; co = {name_key(e["r"]["company_name"]) for e, _, _ in rows} - {""}; eins = {e["r"]["ein"] for e, _, _ in rows} - {""}
        first = {coll(name_key(n)).split()[0] for e, _, _ in rows for n in (e["r"]["establishment_name"], e["r"]["company_name"]) if len(coll(name_key(n)).split()) > 0 and len(coll(name_key(n)).split()[0]) >= 4}
        oth = [e for e, pc in peers if year_of(e) == y and squash(e["r"]["establishment_name"]) not in mine and (RANK[pc] >= 1 or (name_key(e["r"]["company_name"]) in co) or (e["r"]["ein"] and e["r"]["ein"] in eins) or any(coll(name_key(n)).split()[:1] and coll(name_key(n)).split()[0] in first for n in (e["r"]["establishment_name"], e["r"]["company_name"])))]
        if oth: return ("hold", "ita_multiple_establishments_at_street", f"CY{y}: other ITA establishment(s) of the same company at this street ({sorted({e['r']['establishment_name'] for e in oth})[:3]}); whether this site is one of them or all of them settles it", True)
        bands = {band_of(count_of(e)) for e, _, _ in rows}
        if len(bands) > 1: return ("hold", "ita_latest_year_rows_disagree", f"CY{y} name+street rows give bands {sorted(bands, key=BANDS.index)}", True)
        e, c, h = max(rows, key=lambda t: t[0]["r"]["submitted"] or ""); b = band_of(count_of(e))
        if size_flag(e["r"]) == "code_conflicts_with_average": return ("hold", "ita_size_code_inconsistent", f"CY{y}: size code {e['r']['size']} vs annual average band {b}; an amended filing or a second source settles it", True)
        for y2, rs in by.items():
            if y - 2 <= y2 < y and any(dist(b, band_of(count_of(e2))) > 1 for e2, _, _ in rs):
                return ("hold", "ita_years_disagree", f"CY{y} band {b} vs CY{y2} band {sorted({band_of(count_of(e2)) for e2, _, _ in rs}, key=BANDS.index)}", True)
        return ("fill", dict(source="osha_ita", r13=1, e=e, year=y, band=b, matched_name=h, name_match=c, filing_name=e["r"]["establishment_name"]))
    if kind == "insp":
        ok = [t for t in ok if count_of(t[0]) >= 1 and t[0]["r"]["open_date"][:4].isdigit()]
        if not ok: return ("hold", "insp_no_positive_count", "name+street inspections carry no positive nr_in_estab", False)
        d = max(t[0]["r"]["open_date"][:10] for t in ok); latest = [t for t in ok if t[0]["r"]["open_date"][:10] == d]
        bands = {band_of(count_of(t[0])) for t in latest}
        if len(bands) > 1: return ("hold", "insp_latest_date_rows_disagree", f"inspections opened {d} give bands {sorted(bands, key=BANDS.index)}", True)
        e, c, h = latest[0]
        return ("fill", dict(source="osha_inspection", r13=2, e=e, year=int(d[:4]), band=band_of(count_of(e)), matched_name=h, name_match=c, filing_name=e["r"]["estab_name"]))
    if ok and all(t[2].startswith("parent:") for t in ok): return ("hold", "f5500_sponsor_is_parent", "the plan sponsor matches only a named parent of this operator; a plan count is that company's, not this site's", False)
    ok = [t for t in ok if not t[2].startswith("parent:")]
    ok = [t for t in ok if count_of(t[0]) >= 1]
    if not ok: return ("hold", "f5500_no_active_participants", "name+street plans report 0 active participants", False)
    if n_active != 1: return ("hold", "f5500_not_single_establishment", f"organization has {n_active} active sites in the Atlas; R13 source 3 needs exactly 1", False)
    plans = {(t[0]["r"]["ein"], t[0]["r"]["pn"] or t[0]["r"]["plan_name"]) for t in ok}
    if len(plans) > 1: return ("hold", "f5500_multiple_plans", f"the sponsor files {len(plans)} plans in the window (EIN + plan number); none is taken (owner question: a single whole-company plan)", False)
    why = partial_plan(ok[0][0]["r"])
    if why: return ("hold", "f5500_partial_plan", f"the one plan is not shown to cover the whole workforce: {why}", False)
    y = max(year_of(t[0]) for t in ok); top = max((t for t in ok if year_of(t[0]) == y), key=lambda t: count_of(t[0])); b = band_of(count_of(top[0]))
    allb = {band_of(count_of(t[0])) for t in ok}
    if any(dist(b, x) > 1 for x in allb): return ("hold", "f5500_plans_disagree", f"plan bands across plan years 2023-2025 {sorted(allb, key=BANDS.index)}; latest-year top plan {b}", False)
    e, c, h = top
    return ("fill", dict(source="form5500", r13=3, e=e, year=y, band=b, matched_name=h, name_match=c, filing_name=e["r"]["sponsor"]))

def window_conflicts(per_kind, need, n_active, band):
    """every source dated on or after the cutoff at this street under a held name, a rejected candidate included, that is more than one band from `band`.
    Form 5500 plans count only for an organization with exactly one active site (R13 source 3)."""
    out = []
    for kind in per_kind:
        if kind == "f5500" and n_active != 1: continue
        for e, c, h in per_kind[kind]:
            if RANK[c] >= need and fresh(e) and count_of(e) >= 1 and dist(band_of(count_of(e)), band) > 1:
                out.append((e["kind"], source_date(e), band_of(count_of(e))))
    return sorted(set(out), key=lambda t: t[1], reverse=True)

def evaluate(site, level, per_kind, active_n, by_street, near, notes=None):
    """per_kind = {kind: street_equal list}. -> ('fill', payload) | ('hold', reason, detail) | ('none',)"""
    need = LEVELS[level]; fills, holds, stale = [], [], False
    for kind in ("ita", "insp", "f5500"):
        ok = [t for t in per_kind[kind] if RANK[t[1]] >= need]
        if not ok: continue
        if not any(fresh(t[0]) for t in ok): stale = True
        ok = [t for t in ok if fresh(t[0])]
        if not ok: continue
        r = choose(kind, ok, active_n[site["org_id"]], [(t[0], t[1]) for t in per_kind["ita"]] if kind == "ita" else ())
        (fills if r[0] == "fill" else holds).append(r[1] if r[0] == "fill" else r[1:])
    block = [h for h in holds if h[2]]
    if block: return ("hold", block[0][0], block[0][1])
    if not fills:
        if holds: return ("hold", holds[0][0], holds[0][1])
        return ("hold", "stale_over_5_years", f"filing(s) at this street under a held name are all dated before {CUTOFF}; a lead only (owner ruling 2026-11-22 A)") if stale else ("none",)
    top = dict(fills[0]); others = fills[1:]
    conf = window_conflicts(per_kind, need, active_n[site["org_id"]], top["band"])
    if conf: return ("hold", "sources_disagree_in_window", f"R13: fill {top['band']} from {top['source']} {top['year']}, but source(s) dated on or after {CUTOFF} at this street under a held name give: " + "; ".join(f"{k} {d} {b}" for k, d, b in conf[:6]))
    # assumption (controller 2026-11-22): a filing older than the limit is ignored as a band source AND as a conflicting source,
    # except one dated in the year before the cutoff that disagrees by >1 band: those sites are held pending the owner
    for kind in per_kind:
        win = [t for t in per_kind[kind] if RANK[t[1]] >= need and WINDOW_LO <= source_date(t[0]) < CUTOFF and count_of(t[0]) >= 1]
        bad = [t for t in win if dist(band_of(count_of(t[0])), top["band"]) > 1]
        if bad: return ("hold", "near_cutoff_source_disagrees", f"{kind} filing dated {source_date(bad[0][0])} (within a year before the {CUTOFF} cutoff) gives band {band_of(count_of(bad[0][0]))} against the fill {top['band']} from {top['source']} {top['year']}; pending the owner")
    # superseded: the same plant (held name, near-identical street or conflicting city) filed in a later year than the fill
    sup = sorted({f"{year_of(e)} {k}" for k, ns in (notes or {}).items() for t, e, _ in ns if t in ("street_near_differs", "street_equal_city_conflict") and year_of(e) > top["year"]})
    if sup: return ("hold", "superseded_by_later_filing", f"fill from {top['source']} {top['year']}, but the same held name filed in later year(s) at a near-identical street or with a conflicting city/ZIP: {'; '.join(sup)}; the later filing shows the fill is superseded")
    # operator-change test: a later filing at this street, any source, under a name this level does not accept
    later = sorted({f"{year_of(e)} {e['names'][0]!r}" for kind in per_kind for e, c, _ in per_kind[kind] if RANK[c] < need and year_of(e) > top["year"]})
    top["later_other_name"] = "; ".join(later)
    if later: return ("hold", "later_filing_other_name", f"fill from {top['source']} {top['year']} but later filing(s) at this street under another name: {'; '.join(later)} (operator may have changed)")
    for o in by_street.get(street_key(site["street_address"]), []):
        if o["site_id"] != site["site_id"] and same_street(site["street_address"], o["street_address"]) and city_ok(site, o["city"], o["zip"]):
            if o["org_id"] == site["org_id"] or name_class(o["_held"], top["e"]["names"])[0] == "exact":
                return ("hold", "filing_binds_two_sites", f"the same street and name also fit active site {o['site_id']}; one filing cannot size two site records (dedupe or which-site ruling settles it)")
    for k, (nb, ny) in near.items():
        if ["ita", "insp", "f5500"].index(k) < ["ita", "insp", "f5500"].index({"osha_ita": "ita", "osha_inspection": "insp", "form5500": "f5500"}[top["source"]]) and nb != top["band"]:
            return ("hold", "near_street_filing_differs_from_fill", f"a higher-precedence {k} filing at a near-identical street (suffix/directional/unit letter) would give {nb} ({ny}) against the fill {top['band']} from {top['source']} {top['year']}; confirm the street to settle which applies")
    top["also"] = ";".join(f"{f['source']}={f['band']}" for f in others)
    return ("fill", top)

def would_be_band(kind, notes):
    """(band, year) the excluded near-street / city-conflict rows would give, else None (informational only)"""
    cand = [(e, "exact", e["names"][0]) for t, e, _ in notes if t in ("street_near_differs", "street_equal_city_conflict") and fresh(e)]
    if not cand: return None
    r = choose(kind, cand, 1)
    return (r[1]["band"], r[1]["year"]) if r[0] == "fill" else None
def would_be(kind, notes, site):
    w = would_be_band(kind, notes)
    return f"would give {w[0]} (year {w[1]}) if the street were the same" if w else "" 

MAN = {}
for ln in open(a_man := "/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store/raw/MANIFEST.sha256"):
    h, _, pth = ln.rstrip("\n").partition("  ")
    MAN[pth] = h

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cache", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--region", default="pic18", choices=sorted(REGIONS)); ap.add_argument("--frame-size", action="store_true", help="print the frame size for --region and stop (builds nothing)"); ap.add_argument("--withdraw-source", action="append", default=[], help="a source whose fills go to holds as withdrawn to a follow-up (e.g. form5500)"); ap.add_argument("--data-dir"); ap.add_argument("--candidates-out", help="where to write candidates_all.csv (it lists unselected third-party filers, so it is not kept in the repo)"); ap.add_argument("--sample", type=int); ap.add_argument("--seed", type=int, default=20261122)
    ap.add_argument("--site-list", help="file of site_ids: run exactly these (any status/tier), frame-agnostic, for cross-lane comparison"); a = ap.parse_args()
    global WITHDRAW; WITHDRAW = set(a.withdraw_source)
    orgs, sites = load_atlas(a.data_dir); fr, n_org, n_unk = frame(orgs, sites, a.region)
    if a.frame_size:
        print(f"region {a.region}: organization rows with an active tier A-C Ohio site {n_org}; size-unknown {n_unk}; frame sites {len(fr)}; with street {sum(1 for s in fr if s['street_address'].strip())}"); return
    print(f"PIC-18 org rows {n_org}; size-unknown {n_unk}; frame sites {len(fr)}; with street {sum(1 for s in fr if s['street_address'].strip())}")
    active = [s for s in sites if s["operating_status"] == "active"]; active_n = Counter(s["org_id"] for s in active)
    by_street = defaultdict(list)
    for s in active:
        if s["street_address"].strip():
            s["_held"] = held_names(s, orgs); by_street[street_key(s["street_address"])].append(s)
    sel = sorted(fr, key=lambda s: s["site_id"])
    if a.site_list:
        want = set(open(a.site_list).read().split()); sel = [s for s in sorted(sites, key=lambda s: s["site_id"]) if s["site_id"] in want]
    if a.sample: random.Random(a.seed).shuffle(sel); sel = sel[:a.sample]
    ix = {k: index(unify(rd(f"{a.cache}/{f}.csv"), k)) for k, f in (("ita", "ita_oh"), ("insp", "insp_oh"), ("f5500", "f5500_oh"))}
    packet, holds, cands, nostreet, disp = [], [], [], [], {}
    for s in sel:
        sid, oid = s["site_id"], s["org_id"]
        if not s["street_address"].strip() or not street_key(s["street_address"]):
            holds.append((sid, oid, "no_street", "site has no street_address; the operating street from the operator's own page or a registry would settle it", ""))
            nostreet.append((sid, oid, s["city"], "yes" if any(o["street_address"].strip() for o in sites if o["org_id"] == oid and o["site_id"] != sid) else "no", "yes" if any(o["street_address"].strip() for o in sites if o["org_id"] == oid and o["site_id"] != sid and o["operating_status"] == "active") else "no")); continue
        if not same_street(s["street_address"], s["street_address"]):
            holds.append((sid, oid, "street_not_civic", "street_address has no civic number or is a PO box; the operating street would settle it", s["street_address"])); continue
        held = held_names(s, orgs); s["_held"] = held
        per_kind, notes = {}, {}
        for kind in ("ita", "insp", "f5500"): per_kind[kind], notes[kind] = classify(s, held, ix[kind])
        near = {k: w for k in notes if (w := would_be_band(k, notes[k]))}
        res = {lv: evaluate(s, lv, per_kind, active_n, by_street, near, notes) for lv in LEVELS}
        disp[sid] = res
        for kind in per_kind:
            for e, c, h in per_kind[kind]:
                r = e["r"]
                cands.append([sid, oid, kind, "raw/" + r["file"], f"{r['member']}|row={r['row']}|id={r['rid']}", year_of(e), source_date(e), "yes" if fresh(e) else "no (stale_over_5_years)", 2026 - year_of(e), "; ".join(e["names"][:2]), e["st"], c, band_of(count_of(e)) if count_of(e) >= 1 else "", size_flag(r) if kind == "ita" else "",
                              *[(f"FILL {res[lv][1]['source']} {res[lv][1]['band']} age {2026 - res[lv][1]['year']}" if res[lv][0] == "fill" else f"HOLD {res[lv][1]}" if res[lv][0] == "hold" else "none") for lv in LEVELS]])
        st = res["suffix"]
        nearinfo = [f"[{k} near-street row excluded] {w}" for k in notes if (w := would_be(k, notes[k], s))]
        if st[0] == "fill" and st[1]["source"] in WITHDRAW:
            holds.append((sid, oid, f"{st[1]['source']}_withdrawn_to_followup", "withdrawn from this PR to a follow-up packet after review round 2 (a second plan number under the same EIN, a later return of the same plan, and the owner question on whole-company plans); the band it would give is kept in that packet, not here", f"band {st[1]['band']} from {st[1]['source']} year {st[1]['year']}")); continue
        if st[0] == "fill":
            p = st[1]; p["note"] = " ".join(nearinfo); packet.append((sid, oid, p))
        elif st[0] == "hold":
            nt = " | ".join(f"[{k}] {t}: {e['names'][:2]} @ {shown_st(e)!r}" for k in notes for _, e, t in notes[k])[:500]
            fact = {"street_near_differs": "confirm the site's street against the operator's own page; the named filing would then apply", "ita_multiple_establishments_at_street": "which ITA establishment is this site (or whether the site covers all of them)",
                    "later_filing_other_name": "whether the later filing's operator is the same business (a successor/trade-name link) settles it", "filing_binds_two_sites": "a dedupe or which-site ruling for the two site records", "sources_disagree": "review of which count is this establishment's"}.get(st[1], "see detail")
            reason, detail = st[1], (st[2] + (" || " + nt if nt else ""))[:900]
            if reason in ("stale_over_5_years", "name_not_held") and parent_lead_any(held, per_kind):
                detail = f"was {reason}; " + detail; reason = "parent_name_lead"; fact = PARENT_FACT
            holds.append((sid, oid, reason, fact, scrub(detail, per_kind, notes)))
        else:
            near = [(k, e) for k in notes for t, e, _ in notes[k] if t == "street_near_differs"]
            if near:
                nt = " | ".join(f"[{k}] {t}: {e['names'][:2]} @ {shown_st(e)!r} {would_be(k, notes[k], s)}" for k in notes for t, e, _ in notes[k] if t == "street_near_differs")
                holds.append((sid, oid, "street_near_differs", "confirm the site's street against the operator's own page; the named filing would then apply", scrub(nt[:900], per_kind, notes)))
            else:
                anyeq = any(per_kind[k] for k in per_kind)
                if parent_lead_any(held, per_kind):
                    holds.append((sid, oid, "parent_name_lead", PARENT_FACT, scrub("; ".join(f"[{k}] {t[0]['names'][:2]} ({t[1]})" for k in per_kind for t in per_kind[k][:3])[:500], per_kind))); continue
                holds.append((sid, oid, "name_not_held" if anyeq else "no_filing_at_street", "a record link (parent / trade name) tying the filing's company name to this operator would settle it, or the filing is another tenant" if anyeq else "no ITA, inspection or Form 5500 row in the raw store at this street", scrub("; ".join(f"[{k}] {t[0]['names'][:2]} ({t[1]})" for k in per_kind for t in per_kind[k][:3])[:500], per_kind)))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    def wcsv(name, hdr, rows):
        with open(out / name, "w", newline="") as f: w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
    wcsv("packet.csv", ["site_id", "org_id", "source", "source_file", "file_sha256", "row_locator", "filing_year", "source_date", "age_years", "band", "r13_source", "name_match", "matched_name", "filing_name", "filing_street", "other_sources", "note"],
         [[sid, oid, p["source"], "raw/" + p["e"]["r"]["file"], MAN["./" + p["e"]["r"]["file"]], f"{p['e']['r']['member']}|row={p['e']['r']['row']}|id={p['e']['r']['rid']}", p["year"], source_date(p["e"]), 2026 - p["year"], p["band"], p["r13"], p["name_match"], p["matched_name"], p["filing_name"], shown_st(p["e"]), p.get("also", ""), p.get("note", "")] for sid, oid, p in packet])
    wcsv("holds.csv", ["site_id", "org_id", "reason", "settling_fact", "detail"], holds)
    CAND_HDR = ["site_id", "org_id", "source", "source_file", "row_locator", "filing_year", "source_date", "on_or_after_2021-11-22", "age_years", "filing_names", "filing_street", "name_match", "band_of_row", "ita_size_code_check", "disposition_exact_only", "disposition_corporate_suffix_accepted (RULED)", "disposition_containment_accepted"]
    if a.candidates_out:
        with open(a.candidates_out, "w", newline="") as f: w = csv.writer(f); w.writerow(CAND_HDR); w.writerows(cands)
    wcsv("frame.csv", ["site_id", "org_id", "site_name", "street_address", "city", "zip", "county"], [[s[k] for k in ("site_id", "org_id", "site_name", "street_address", "city", "zip", "county")] for s in sel])
    wcsv("no_street_sites.csv", ["site_id", "org_id", "city", "org_has_another_site_with_street_any_status", "org_has_another_active_site_with_street"], nostreet)
    # org-level fill counts per name level, with the ruled 5-year limit and (for the record) without it
    global CUTOFF
    def orgs_filled(): return {lv: len({s["org_id"] for s in sel if s["site_id"] in disp and disp[s["site_id"]][lv][0] == "fill"}) for lv in LEVELS}
    tab = orgs_filled(); ruled = CUTOFF; CUTOFF = "0000-00-00"; disp0 = disp; disp = {}
    for s in sel:
        if s["site_id"] in disp0:
            held = s["_held"]; pk = {k: classify(s, held, ix[k])[0] for k in ("ita", "insp", "f5500")}
            near = {}
            disp[s["site_id"]] = {lv: evaluate(s, lv, pk, active_n, by_street, near) for lv in LEVELS}
    tab0 = orgs_filled(); CUTOFF = ruled
    import json
    with open(out / "counts.json", "w") as f:
        json.dump({"frame_sites": len(sel), "orgs_in_selection": len({s["org_id"] for s in sel}), "orgs_filled_with_5y_limit": tab, "orgs_filled_no_age_limit_reference": tab0,
                   "packet_fills_by_source": dict(Counter(p["source"] for _, _, p in packet)), "holds_by_reason": dict(Counter(h[2] for h in holds))}, f, indent=1)
    print(f"selected {len(sel)}: fills {len(packet)}; holds {len(holds)}", dict(Counter(h[2] for h in holds)), dict(Counter(p['source'] for _, _, p in packet)))
    print("orgs filled with the 5-year limit (exact / +corporate suffix [RULED] / +containment):", tab, "| no age limit:", tab0)

if __name__ == "__main__": main()
