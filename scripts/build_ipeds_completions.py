#!/usr/bin/env python3
"""Build IPEDS completions packet files for the Polymer Atlas programs spine.

PACKET-LANE TOOL: reads data/ (never writes there) and writes only under
the --out-dir (default tasks/ipeds-completions-2026-11-01/).  Raw NCES files
are cached outside the repo (default /tmp/claude-0/ipeds_raw/).

Source: NCES IPEDS Data Center, Completions "A" files (awards by CIP x award
level x first/second major), one file per collection year:
    https://nces.ed.gov/ipeds/datacenter/data/C<YYYY>_A.zip
    (C2024_A = awards 2023-07-01..2024-06-30; "completions_year" = <YYYY>,
     the convention already used on held programs.csv rows)
Dictionary: C<YYYY>_A_Dict.zip (xlsx).  Columns used (verified from the
C2024_A dictionary, Varlist sheet):
    UNITID   unique institution id
    CIPCODE  CIP 2020 code, "NN.NNNN" (CIP-2010 in files before C2021; the
             codes used here are 'No substantive changes' 2010->2020, except
             15.0617 which is New in 2020)
    MAJORNUM 1 = first major, 2 = second major
    AWLEVEL  award level code (detail levels only are summed; the
             total levels 12/13/14/15 are never used)
    CTOTALT  grand total (with XCTOTALT status flag)
Where a collection year ships a revised file (c<YYYY>_a_rv.csv) the revised
file is used.  C2010 is not used: it predates CTOTALT (race-only columns).
C2024_A is the PROVISIONAL release (per its dictionary Introduction sheet).
Institution names/states come from HD2024 (Institutional Characteristics).
CIP titles come from CIPCode2020.csv.

Outputs (tasks/ipeds-completions-2026-11-01/):
    completions.csv         polymer-set CIP completions, all window years
    program_proposals.csv   one row per data/programs.csv row
    leads.csv               institutions with polymer-set completions and no
                            Atlas program row (DISCOVERY LEADS ONLY)
    REPORT.md               counts (with units), match results, caveats

SCHEMA constraints honoured (docs/SCHEMA.md section 4.11 / 4.6):
  * completions fields are for `degree` rows only, populated only by a pull
    keyed on the institution's ipeds_unitid x the row's cip_code, cited to
    that pull; never estimated; latest_completions requires completions_year.
    The key is UNITID x CIP (not x level), so the proposed count is the
    first-major total over ALL detail award levels at that key - the same
    convention the held rows already use (checked: Shawnee 6 = 1 assoc +
    5 bach; Ferris 30 = 12 + 18; UMass Lowell 69 incl. 5 post-bacc cert).
    The row's own levels are reported separately (level_alignment).
  * IPEDS/CIP attribution is a lead, never program evidence (named-program
    test, Lakeland rule).  Rows the schema does not let IPEDS fill are marked
    "join-key lead; institution page needed" and carry no proposed value.

Stdlib only.  Usage:
    python3 -I scripts/build_ipeds_completions.py [--raw-dir DIR] [--out-dir DIR]
                                                  [--repo DIR] [--download]
"""
import argparse
import csv
import glob
import os
import ssl
import sys
import urllib.request
import zipfile
from collections import Counter, defaultdict

BASE = "https://nces.ed.gov/ipeds/datacenter/data/"
CIP_URL = "https://nces.ed.gov/ipeds/cipcode/Files/CIPCode2020.csv"
FIRST_YEAR, LAST_YEAR = 2011, 2024          # window; C2010 lacks CTOTALT
TREND_YEARS = (2021, 2022, 2023, 2024)
LEAD_YEARS = (2022, 2023, 2024)             # "current" window for leads
RETRIEVED = "2026-11-01"

# CIP sets (titles are verified from CIPCode2020.csv at run time)
POLYMER_SPECIFIC = ("14.3201", "15.0607", "40.0507")
COMPOSITES = ("15.0617",)
BROAD_MATERIALS = ("14.1801", "40.1001")
CIP_SET = POLYMER_SPECIFIC + COMPOSITES + BROAD_MATERIALS
TIER = {}
for c in POLYMER_SPECIFIC:
    TIER[c] = "1_polymer_specific"
for c in COMPOSITES:
    TIER[c] = "2_composites"
for c in BROAD_MATERIALS:
    TIER[c] = "3_broad_materials"

AWLEVEL_NAME = {
    1: "Certificate <1 yr", 2: "Certificate 1-<2 yr", 3: "Associate's",
    4: "Certificate 2-<4 yr", 5: "Bachelor's", 6: "Postbaccalaureate certificate",
    7: "Master's", 8: "Post-master's certificate",
    17: "Doctor's research/scholarship", 18: "Doctor's professional practice",
    19: "Doctor's other", 20: "Certificate <12 wks",
    21: "Certificate 12 wks-<1 yr",
}
# Atlas level (SCHEMA 4.11) -> IPEDS AWLEVEL detail codes.  Post-bacc (6) and
# post-master's (8) certificates have no Atlas level and are never summed.
LEVEL_MAP = {
    "certificate": (1, 2, 4, 20, 21),
    "associate": (3,),
    "bachelor": (5,),
    "master": (7,),
    "doctorate": (17, 18, 19),
}
DETAIL_LEVELS = set(AWLEVEL_NAME)

# Rejected on their own catalogs per the task brief (staging verdicts that are
# not in the repo files); kept as a lead annotation only.
KNOWN_REJECTED = ("Lakeland Community College", "Lorain County Community College")
PRIORITY_STATES = ("OH", "PA")


# ----------------------------------------------------------------- fetching
def _ctx():
    cafile = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if not cafile and os.path.exists("/root/.ccr/ca-bundle.crt"):
        cafile = "/root/.ccr/ca-bundle.crt"
    return ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return
    print("download", url, file=sys.stderr)
    with urllib.request.urlopen(url, context=_ctx(), timeout=300) as r, open(dest + ".part", "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
    os.replace(dest + ".part", dest)


def extract(zpath, outdir):
    os.makedirs(outdir, exist_ok=True)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(outdir)


def ensure_raw(raw, download):
    os.makedirs(raw, exist_ok=True)
    need = [("CIPCode2020.csv", CIP_URL)]
    need += [("HD2024.zip", BASE + "HD2024.zip")]
    need += [("C%d_A.zip" % y, BASE + "C%d_A.zip" % y) for y in range(FIRST_YEAR, LAST_YEAR + 1)]
    need += [("C2024_A_Dict.zip", BASE + "C2024_A_Dict.zip")]
    for name, url in need:
        p = os.path.join(raw, name)
        if not os.path.exists(p):
            if not download:
                sys.exit("missing %s (run with --download)" % p)
            fetch(url, p)
    for name, _ in need:
        if name.endswith(".zip"):
            d = os.path.join(raw, "x_" + name[:-4])
            if not os.path.isdir(d):
                extract(os.path.join(raw, name), d)


def year_file(raw, y):
    d = os.path.join(raw, "x_C%d_A" % y)
    files = {f.lower(): f for f in os.listdir(d)}
    rv = "c%d_a_rv.csv" % y
    base = "c%d_a.csv" % y
    if rv in files:
        return os.path.join(d, files[rv]), "revised"
    return os.path.join(d, files[base]), "provisional" if y == LAST_YEAR else "final"


# ------------------------------------------------------------------ loaders
def load_cip_titles(raw):
    t = {}
    with open(os.path.join(raw, "CIPCode2020.csv"), encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            code = r["CIPCode"].strip().lstrip("=").strip('"')
            if len(code) == 7:
                t[code] = r["CIPTitle"].strip().rstrip(".")
    return t


def load_hd(raw):
    hd = {}
    with open(os.path.join(raw, "x_HD2024", "HD2024.csv"), encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            hd[r["UNITID"].strip()] = {
                "name": r["INSTNM"].strip(), "state": r["STABBR"].strip(),
                "web": r["WEBADDR"].strip(), "control": r["CONTROL"].strip(),
                "iclevel": r["ICLEVEL"].strip(), "city": r["CITY"].strip(),
            }
    return hd


CONTROL = {"1": "public", "2": "private nonprofit", "3": "private for-profit"}


def load_completions(raw, cips):
    """{(year, unitid, cip, awlevel): [first_major_total, second_major_total,
    first_flag, second_flag]}  (detail award levels only)."""
    out = {}
    src = {}
    for y in range(FIRST_YEAR, LAST_YEAR + 1):
        path, kind = year_file(raw, y)
        src[y] = (os.path.basename(path), kind)
        with open(path, encoding="utf-8-sig", newline="") as f:
            rd = csv.DictReader(f)
            for r in rd:
                cip = r["CIPCODE"].strip()
                if cip not in cips:
                    continue
                try:
                    lvl = int(r["AWLEVEL"])
                except ValueError:
                    continue
                if lvl not in DETAIL_LEVELS:
                    continue
                v = r["CTOTALT"].strip()
                n = int(v) if v else 0
                key = (y, r["UNITID"].strip(), cip, lvl)
                rec = out.setdefault(key, [0, 0, "", ""])
                if r["MAJORNUM"].strip() == "1":
                    rec[0] += n
                    rec[2] = r.get("XCTOTALT", "").strip()
                else:
                    rec[1] += n
                    rec[3] = r.get("XCTOTALT", "").strip()
    return out, src


def read_csv(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_qcew_gap(repo):
    """State gap = QCEW 2023 NAICS 326 private establishments minus Atlas
    'strict' site rows with naics_primary starting 326 (same definition as
    scripts/build_qcew_denominators.py atlas_numerators).  Reference only."""
    q = {}
    p = os.path.join(repo, "tasks", "f5-source-packet", "qcew_denominators_by_state_2023.csv")
    for r in read_csv(p):
        if r["qcew_2023_326"]:
            q[r["state_abbr"]] = int(r["qcew_2023_326"])
    strict = Counter()
    for sp in sorted(glob.glob(os.path.join(repo, "data", "sites_*.csv"))):
        for r in read_csv(sp):
            if r.get("country", "US") not in ("US", ""):
                continue
            if (r["naics_primary"].startswith("326") and r["operating_status"] in ("active", "unknown")
                    and r["verification_tier"] in ("A", "B", "C")):
                strict[r["state"]] += 1
    return sorted(((q[s] - strict[s], s) for s in q), reverse=True)


# ------------------------------------------------------------------ helpers
def sum_levels(comp, y, unitid, cip, levels):
    return sum(comp.get((y, unitid, cip, l), [0])[0] for l in levels)


def years_with(comp, unitid, cip, levels):
    return [y for y in range(FIRST_YEAR, LAST_YEAR + 1) if sum_levels(comp, y, unitid, cip, levels) > 0]


def name_ratio(a, b):
    import difflib
    n = lambda s: "".join(ch for ch in s.lower().replace("&", "and").replace("–", "-") if ch.isalnum() or ch == " ")
    return difflib.SequenceMatcher(None, n(a), n(b)).ratio()


def norm_name(x):
    x = x.lower().replace("&", " and ").replace("\u2013", " ").replace("-", " ")
    x = "".join(ch if ch.isalnum() or ch == " " else " " for ch in x)
    return " ".join(w for w in x.split() if w not in ("the", "of", "at", "inc"))


COLLEGE_WORDS = ("college", "university", "institute of technology", "polytechnic", "technical", "school of")


def lvl_list(level_field):
    return [x for x in level_field.split(";") if x]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.dirname(here))
    ap.add_argument("--raw-dir", default="/tmp/claude-0/ipeds_raw")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--download", action="store_true")
    a = ap.parse_args()
    repo = a.repo
    out = a.out_dir or os.path.join(repo, "tasks", "ipeds-completions-2026-11-01")
    os.makedirs(out, exist_ok=True)
    ensure_raw(a.raw_dir, a.download)

    cip_title = load_cip_titles(a.raw_dir)
    for c in CIP_SET:
        if c not in cip_title:
            sys.exit("CIP %s not in CIP 2020 list" % c)
    hd = load_hd(a.raw_dir)

    programs = read_csv(os.path.join(repo, "data", "programs.csv"))
    eco = {r["org_id"]: r for r in read_csv(os.path.join(repo, "data", "ecosystem.csv"))}
    orgnames = {}
    for op in sorted(glob.glob(os.path.join(repo, "data", "organizations_*.csv"))):
        for r in read_csv(op):
            orgnames[r["org_id"]] = r["legal_name"]
    pids = [r["program_id"] for r in programs]
    assert len(pids) == len(set(pids)), "program_id not unique"
    held_cips = {r["cip_code"] for r in programs if r["cip_code"]}
    extra_cips = sorted(held_cips - set(CIP_SET))
    all_cips = set(CIP_SET) | set(extra_cips)
    for c in extra_cips:
        cip_title.setdefault(c, "(not in CIP 2020)")
    comp, srcinfo = load_completions(a.raw_dir, all_cips)

    # ---- completions.csv ------------------------------------------------
    keys = sorted(comp, key=lambda k: (k[2], k[1], k[3], k[0]))
    rows_out = []
    for (y, u, cip, lvl) in keys:
        f1, f2, x1, x2 = comp[(y, u, cip, lvl)]
        if f1 == 0 and f2 == 0:
            continue
        h = hd.get(u, {})
        rows_out.append({
            "unitid": u, "institution_name": h.get("name", "(not in HD2024)"),
            "state": h.get("state", ""), "cip_code": cip, "cip_title": cip_title[cip],
            "cip_set_role": TIER.get(cip, "held_row_cip_outside_polymer_set"),
            "award_level_code": lvl, "award_level": AWLEVEL_NAME[lvl],
            "completions_year": y, "academic_year": "%d-%02d" % (y - 1, y % 100),
            "completions_first_major": f1, "first_major_flag": x1,
            "completions_second_major": f2,
            "release": srcinfo[y][1], "source_file": srcinfo[y][0],
        })
    cols = list(rows_out[0])
    with open(os.path.join(out, "completions.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows_out)

    # ---- program_proposals.csv -------------------------------------------
    cite = ("NCES IPEDS Completions C2024_A (awards 2023-07-01 to 2024-06-30; provisional release), "
            "keyed UNITID x CIP, first major, https://nces.ed.gov/ipeds/datacenter/data/C2024_A.zip, "
            "retrieved " + RETRIEVED)
    hd_norm = defaultdict(list)         # normalized HD name -> [unitid]
    for hu, hh in hd.items():
        hd_norm[norm_name(hh["name"])].append(hu)
    name_candidates = {}                # unitid -> program_ids (institution lacks ipeds_unitid in Atlas)
    held_unitids = defaultdict(set)     # unitid -> program institution org ids
    prog_rows = []
    status_ct = Counter()
    for r in programs:
        inst = eco.get(r["institution_org_id"])
        u = (inst or {}).get("ipeds_unitid", "").strip()
        if u:
            held_unitids[u].add(r["program_id"])
        levels = lvl_list(r["level"])
        cip = r["cip_code"]
        ptype = r["program_type"]
        rec = {
            "program_id": r["program_id"], "institution_org_id": r["institution_org_id"],
            "institution_in_ecosystem": "yes" if inst else "no",
            "ipeds_unitid": u, "hd2024_name": hd.get(u, {}).get("name", ""),
            "candidate_unitid_by_name": "", "candidate_unitid_hd_name": "",
            "unitid_name_check": "",
            "program_name": r["program_name"], "program_type": ptype, "level": r["level"],
            "cip_code": cip, "cip_source_type": r["cip_source_type"],
            "cip_title": cip_title.get(cip, "") if cip else "",
            "cip_in_polymer_set": ("yes" if cip in CIP_SET else ("NO" if cip else "")),
            "proposal_status": "", "proposal_reason": "",
            "prop_latest_completions": "", "prop_completions_year": "",
            "prop_first_year_awarded": "", "prop_last_year_awarded": "",
            "awarding_in_completions_year": "",
            "held_latest_completions": r["latest_completions"],
            "held_completions_year": r["completions_year"],
            "held_first_year_awarded": r["first_year_awarded"],
            "held_last_year_awarded": r["last_year_awarded"],
            "held_vs_pull": "",
            "levels_summed": "", "level_breakdown_2024": "",
            "level_alignment": "", "row_level_completions_2024": "", "includes_postbacc_cert_2024": "",
            "completions_2021": "", "completions_2022": "", "completions_2023": "", "completions_2024": "",
            "years_with_completions_2011_2024": "",
            "candidate_polymer_cips_at_institution_2024": "",
            "cip_scope_caveat": "",
            "suggested_source_citation": "",
        }
        if u:
            rec["unitid_name_check"] = ("ok" if name_ratio(inst["legal_name"], hd.get(u, {}).get("name", "")) >= 0.6
                                        else "REVIEW name differs: eco='%s'" % inst["legal_name"]) if u in hd else "UNITID not in HD2024"
        # candidate CIPs at the institution (informational)
        if u:
            cands = []
            for c in CIP_SET:
                n24 = sum(comp.get((LAST_YEAR, u, c, l), [0])[0] for l in DETAIL_LEVELS)
                if n24:
                    cands.append("%s=%d" % (c, n24))
            rec["candidate_polymer_cips_at_institution_2024"] = ";".join(cands)

        join_lead = "join-key lead; institution page needed"
        if not inst or not u:
            iname = (inst or {}).get("legal_name") or orgnames.get(r["institution_org_id"], "")
            rec["proposal_status"] = "NO_JOIN_KEY"
            if any(w in iname.lower() for w in COLLEGE_WORDS):
                cands = [c for c in hd_norm.get(norm_name(iname), []) if hd[c]["state"] == r["state"]]
                if not cands:   # fallback: all name tokens contained in exactly one same-state HD name
                    tk = set(norm_name(iname).split())
                    cands = [c for c, hh in hd.items() if hh["state"] == r["state"] and tk <= set(norm_name(hh["name"]).split())]
                if len(cands) == 1:
                    rec["candidate_unitid_by_name"] = cands[0]
                    rec["candidate_unitid_hd_name"] = hd[cands[0]]["name"]
                    name_candidates.setdefault(cands[0], []).append(r["program_id"])
                    ccs = []
                    for c in CIP_SET:
                        n24 = sum(comp.get((LAST_YEAR, cands[0], c, l), [0])[0] for l in DETAIL_LEVELS)
                        if n24:
                            ccs.append("%s=%d" % (c, n24))
                    rec["candidate_polymer_cips_at_institution_2024"] = ";".join(ccs)
            rec["proposal_reason"] = ("institution_org_id (%s) has no ipeds_unitid in the Atlas (organizations-table, non-university "
                                      "ecosystem subtype, or college record without the UNITID backfill): the pull cannot be keyed%s"
                                      % (iname, ("; HD2024 exact-name+state candidate UNITID %s recorded in candidate_unitid_by_name (unverified: integrator must backfill ecosystem.ipeds_unitid before any value lands)" % rec["candidate_unitid_by_name"]) if rec["candidate_unitid_by_name"] else ""))
        elif ptype != "degree":
            rec["proposal_status"] = join_lead
            rec["proposal_reason"] = ("SCHEMA 4.11: completions fields are degree rows only; this is a %s row, so IPEDS "
                                      "supplies the join key (UNITID) only and no value is proposed" % ptype)
            if cip:
                ref = sum(comp.get((LAST_YEAR, u, cip, l), [0])[0] for l in DETAIL_LEVELS)
                rec["completions_2024"] = ""  # deliberately blank: not a proposal
                rec["proposal_reason"] += ("; reference only (not a proposal): %s all-level first-major completions at the "
                                           "institution in 2024 = %d" % (cip, ref))
        elif not cip:
            rec["proposal_status"] = join_lead
            rec["proposal_reason"] = ("degree row carries no cip_code, so the UNITID x CIP pull cannot be keyed; the CIP must "
                                      "come from the institution's own catalog (institution_published) or be recorded as an "
                                      "ipeds_listing pair per 4.11. Informational candidates in "
                                      "candidate_polymer_cips_at_institution_2024")
        elif u not in hd:
            rec["proposal_status"] = "NO_JOIN_KEY"
            rec["proposal_reason"] = "UNITID %s is not present in HD2024" % u
        else:
            lv = []
            for l in levels:
                lv.extend(LEVEL_MAP.get(l, ()))
            lv = sorted(set(lv))
            alllv = sorted(DETAIL_LEVELS)
            rec["levels_summed"] = "all detail award levels at UNITID x CIP (first major)"
            by = {y: sum_levels(comp, y, u, cip, alllv) for y in range(FIRST_YEAR, LAST_YEAR + 1)}
            byrow = {y: sum_levels(comp, y, u, cip, lv) for y in range(FIRST_YEAR, LAST_YEAR + 1)}
            for y in TREND_YEARS:
                rec["completions_%d" % y] = by[y]
            ys = [y for y, n in by.items() if n > 0]
            rec["years_with_completions_2011_2024"] = ("%d-%d (%d yrs)" % (ys[0], ys[-1], len(ys))) if ys else ""
            bd = []
            for l in sorted(DETAIL_LEVELS):
                n = comp.get((LAST_YEAR, u, cip, l), [0])[0]
                if n:
                    bd.append("%s=%d" % (AWLEVEL_NAME[l], n))
            rec["level_breakdown_2024"] = "; ".join(bd)
            other_lv = sum(comp.get((LAST_YEAR, u, cip, l), [0])[0] for l in DETAIL_LEVELS if l not in lv and l not in (6, 8))
            if by[LAST_YEAR] == 0:
                rec["level_alignment"] = "n/a (no 2024 completions)"
            elif other_lv == 0 and byrow[LAST_YEAR] > 0:
                rec["level_alignment"] = "all 2024 completions are at the row's levels (post-baccalaureate certificates aside)"
            elif byrow[LAST_YEAR] == 0:
                rec["level_alignment"] = "LEVEL MISMATCH: none of the %d 2024 completions are at the row's levels (%s)" % (by[LAST_YEAR], r["level"])
            else:
                rec["level_alignment"] = "partial: %d of %d 2024 completions are at the row's levels (%s)" % (byrow[LAST_YEAR], by[LAST_YEAR], r["level"])
            rec["row_level_completions_2024"] = byrow[LAST_YEAR]
            pb = sum(comp.get((LAST_YEAR, u, cip, l), [0])[0] for l in (6, 8))
            rec["includes_postbacc_cert_2024"] = pb if pb else ""
            if cip in BROAD_MATERIALS:
                rec["cip_scope_caveat"] = ("broad CIP (%s %s): count is ALL institution awards in this CIP, not only the "
                                           "polymer-named program/track; do not read as polymer-program size" % (cip, cip_title[cip]))
            elif cip not in CIP_SET:
                rec["cip_scope_caveat"] = ("held CIP %s is '%s', not a polymer CIP in CIP 2020 - check the row's cip_code "
                                           "(a polymer-chemistry code would be 40.0507)" % (cip, cip_title[cip]))
            elif cip in COMPOSITES:
                rec["cip_scope_caveat"] = "composites technology CIP; count covers the whole CIP at the institution"
            else:
                rec["cip_scope_caveat"] = "count covers the whole CIP at the institution (all levels)"
            if not ys:
                rec["proposal_status"] = "NO_IPEDS_COMPLETIONS_IN_WINDOW"
                rec["proposal_reason"] = ("no first-major completions at UNITID %s x CIP %s (any level) in any year 2011-2024; "
                                          "no value proposed (absence is not a finding about the program; the held cip_code may be wrong - see candidate CIPs)" % (u, cip))
            else:
                latest_y = ys[-1]
                if by[LAST_YEAR] > 0:
                    rec["prop_latest_completions"] = by[LAST_YEAR]
                    rec["prop_completions_year"] = LAST_YEAR
                    rec["awarding_in_completions_year"] = "yes"
                else:
                    rec["awarding_in_completions_year"] = "no"
                rec["prop_last_year_awarded"] = latest_y
                if ys[0] > FIRST_YEAR:
                    rec["prop_first_year_awarded"] = ys[0]
                    fy_note = "first_year_awarded %d (zero in %d..%d before it)" % (ys[0], FIRST_YEAR, ys[0] - 1)
                else:
                    fy_note = ("first_year_awarded NOT proposed: completions already present in %d, the window floor (true "
                               "first year is <=%d and unknowable from this pull)" % (FIRST_YEAR, FIRST_YEAR))
                held_n = r["latest_completions"]
                held_y = r["completions_year"]
                if by[LAST_YEAR] > 0:
                    if held_n == "" and held_y == "":
                        rec["held_vs_pull"] = "held_blank"
                    elif held_n == str(by[LAST_YEAR]) and held_y == str(LAST_YEAR):
                        rec["held_vs_pull"] = "match"
                    else:
                        rec["held_vs_pull"] = "DIFFERS (held %s/%s vs pull %d/%d)" % (held_n, held_y, by[LAST_YEAR], LAST_YEAR)
                else:
                    rec["held_vs_pull"] = ("held %s/%s; pull has none in %d" % (held_n, held_y, LAST_YEAR)) if held_n else "held_blank; pull none in 2024"
                if by[LAST_YEAR] > 0:
                    if rec["held_vs_pull"] == "match":
                        rec["proposal_status"] = "CONFIRMS_HELD"
                    elif rec["held_vs_pull"].startswith("DIFFERS"):
                        rec["proposal_status"] = "CONFLICT_REVIEW"
                    else:
                        rec["proposal_status"] = "PROPOSE"
                    rec["proposal_reason"] = "UNITID x CIP pull, first major, all levels; " + fy_note
                else:
                    rec["proposal_status"] = "NO_COMPLETIONS_IN_LATEST_YEAR"
                    rec["proposal_reason"] = ("zero first-major completions at the key in %d; latest year with "
                                              "completions = %d (proposed as last_year_awarded only); latest_completions not proposed; %s"
                                              % (LAST_YEAR, latest_y, fy_note))
                rec["suggested_source_citation"] = cite
                if cip not in CIP_SET:
                    rec["proposal_status"] = "CIP_REVIEW" if rec["proposal_status"] != "NO_COMPLETIONS_IN_LATEST_YEAR" else rec["proposal_status"]
                    rec["proposal_reason"] += "; HELD CIP IS NOT A POLYMER CIP - resolve cip_code before landing any value"
                if rec["level_alignment"].startswith("LEVEL MISMATCH") and rec["proposal_status"] in ("PROPOSE", "CONFIRMS_HELD"):
                    rec["proposal_status"] += " (LEVEL MISMATCH - review)"
                elif rec["level_alignment"].startswith("partial") and rec["proposal_status"] in ("PROPOSE", "CONFIRMS_HELD"):
                    rec["proposal_status"] += " (LEVEL PARTIAL - review)"
        status_ct[rec["proposal_status"]] += 1
        prog_rows.append(rec)

    # shared-key check (two degree rows on the same unitid x cip with overlapping levels)
    keyc = defaultdict(list)
    for rec in prog_rows:
        if rec["proposal_status"] in ("PROPOSE", "CONFIRMS_HELD", "CONFLICT_REVIEW") and rec["ipeds_unitid"]:
            keyc[(rec["ipeds_unitid"], rec["cip_code"])].append(rec)
    shared = 0
    for k, v in keyc.items():
        if len(v) > 1:
            lv = [set(x["level"].split(";")) for x in v]
            for i in range(len(v)):
                for j in range(i + 1, len(v)):
                    if lv[i] & lv[j]:
                        for x in (v[i], v[j]):
                            x["cip_scope_caveat"] += "; SHARED KEY: another degree row has the same UNITID x CIP x level - the same IPEDS count would be double-attributed"
                        shared += 1
    with open(os.path.join(out, "program_proposals.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(prog_rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(prog_rows)

    # ---- leads.csv -----------------------------------------------------------
    gap = load_qcew_gap(repo)
    gap_states = [s for g, s in gap if s not in PRIORITY_STATES][:10]
    held_by_unitid = defaultdict(list)       # unitid -> eco rows
    for r in eco.values():
        if r["ipeds_unitid"]:
            held_by_unitid[r["ipeds_unitid"]].append(r)
    prog_unitids = {u for u in held_unitids} | set(name_candidates)
    neg_ev = set()
    for r in read_csv(os.path.join(repo, "data", "evidence.csv")):
        if r["record_table"] == "ecosystem" and "contradict" in (r["tier_effect"] + r["claim_type"]).lower():
            neg_ev.add(r["record_id"])

    inst = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))   # unitid -> year -> cip -> total
    lvl_detail = defaultdict(lambda: defaultdict(int))                  # unitid -> "cip:Level" (2024)
    for (y, u, cip, l), (f1, f2, x1, x2) in comp.items():
        if cip in CIP_SET and f1 > 0:
            inst[u][y][cip] += f1
            if y == LAST_YEAR:
                lvl_detail[u]["%s %s" % (cip, AWLEVEL_NAME[l])] += f1
    leads = []
    held_other_cip = []
    for u, yd in inst.items():
        tot = {y: sum(yd.get(y, {}).values()) for y in LEAD_YEARS}
        if sum(tot.values()) == 0:
            continue
        cips_recent = defaultdict(int)
        for y in LEAD_YEARS:
            for c, n in yd.get(y, {}).items():
                cips_recent[c] += n
        h = hd.get(u, {})
        state = h.get("state", "")
        ecos = held_by_unitid.get(u, [])
        if u in prog_unitids:
            # institution already has Atlas program rows; note polymer-specific CIPs not carried
            carried = {r["cip_code"] for r in programs
                       if eco.get(r["institution_org_id"], {}).get("ipeds_unitid") == u and r["cip_code"]}
            for c in POLYMER_SPECIFIC + COMPOSITES:
                if cips_recent.get(c) and c not in carried:
                    held_other_cip.append((u, h.get("name", ""), state, c, yd.get(LAST_YEAR, {}).get(c, 0), sorted(carried)))
            continue
        best = min(TIER[c] for c in cips_recent)
        if not ecos:
            atlas_status = "institution_not_in_atlas"
        else:
            flags = {r["polymer_program"] for r in ecos}
            if any(r["org_id"] in neg_ev for r in ecos):
                atlas_status = "institution_held_polymer_program_NEGATIVE_FINDING (own-catalog contradiction on file)"
            elif "true" in flags:
                atlas_status = "institution_held_polymer_program_claim_UNDECOMPOSED (no program rows; V-16 pending)"
            else:
                atlas_status = "institution_held_polymer_program_false_or_office_only"
        note = []
        if any(k.lower() in h.get("name", "").lower() for k in KNOWN_REJECTED):
            note.append("KNOWN REJECTED on own catalog per task brief (Lakeland rule) - do not re-lead without new catalog evidence")
        pref = h.get("name", "").split("-")[0].strip()
        sib = sorted(hu for hu in (set(held_unitids) | set(name_candidates)) if hu != u and len(pref) > 10
                     and "-" in h.get("name", "") and hd.get(hu, {}).get("name", "").split("-")[0].strip() == pref)
        if sib:
            note.append("same-system campus already in Atlas under UNITID %s (%s) - confirm this is a distinct campus before any record" % (",".join(sib), "; ".join(hd[x]["name"] for x in sib)))
        if best.startswith("3"):
            note.append("broad materials CIP only: not polymer-specific; weak lead")
        if tot[LAST_YEAR] == 0:
            note.append("no completions in %d (latest of 2022-2024 shown): possibly lapsed or reporting lag" % LAST_YEAR)
        bucket = 0 if state in PRIORITY_STATES else (1 if state in gap_states else 2)
        c24 = yd.get(LAST_YEAR, {})
        leads.append({
            "priority_bucket": {0: "0_OH_PA", 1: "1_top_QCEW_gap_state", 2: "2_other"}[bucket],
            "unitid": u, "institution_name": h.get("name", "(not in HD2024)"), "state": state,
            "city": h.get("city", ""), "control": CONTROL.get(h.get("control", ""), ""),
            "institution_website_hd2024": h.get("web", ""),
            "lead_tier": best,
            "polymer_specific_completions_2024": sum(c24.get(c, 0) for c in POLYMER_SPECIFIC),
            "composites_completions_2024": sum(c24.get(c, 0) for c in COMPOSITES),
            "broad_materials_completions_2024": sum(c24.get(c, 0) for c in BROAD_MATERIALS),
            "all_set_completions_2024": tot[2024], "all_set_completions_2023": tot[2023], "all_set_completions_2022": tot[2022],
            "cips_with_completions_2022_2024": ";".join(sorted(cips_recent)),
            "level_breakdown_2024": "; ".join("%s=%d" % kv for kv in sorted(lvl_detail[u].items())),
            "atlas_status": atlas_status,
            "atlas_ecosystem_org_ids": ";".join(r["org_id"] for r in ecos),
            "lead_basis": "IPEDS CIP listing only - discovery lead, never program evidence (SCHEMA 4.11 Lakeland rule); needs named-program test on the institution's own catalog/pages",
            "notes": "; ".join(note),
            "_k": (bucket, best, -sum(c24.get(c, 0) for c in POLYMER_SPECIFIC + COMPOSITES), -tot[2024], -sum(tot.values())),
        })
    leads.sort(key=lambda r: r["_k"] + (r["institution_name"],))
    for i, r in enumerate(leads, 1):
        r["lead_rank"] = i
        del r["_k"]
    lcols = ["lead_rank"] + [k for k in leads[0] if k != "lead_rank"]
    with open(os.path.join(out, "leads.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=lcols, lineterminator="\n")
        w.writeheader()
        w.writerows(leads)

    # ---- sanity: uniqueness / reconciliation ------------------------------------
    ck = Counter((r["unitid"], r["cip_code"], r["award_level_code"], r["completions_year"]) for r in rows_out)
    assert max(ck.values()) == 1, "duplicate completions key"
    assert len({r["unitid"] for r in leads}) == len(leads), "duplicate lead unitid"
    assert len(prog_rows) == len(programs)

    write_report(out, a, srcinfo, cip_title, rows_out, prog_rows, status_ct, leads, held_other_cip,
                 gap, gap_states, extra_cips, shared, hd)
    print("completions rows", len(rows_out), "| proposals", len(prog_rows), dict(status_ct), "| leads", len(leads))


def write_report(out, a, srcinfo, cip_title, rows_out, prog_rows, status_ct, leads, held_other_cip,
                 gap, gap_states, extra_cips, shared, hd):
    L = []
    P = L.append
    latest = [r for r in rows_out if r["completions_year"] == LAST_YEAR and r["cip_code"] in CIP_SET]
    P("# IPEDS completions packet - 2026-11-01")
    P("")
    P("Packet-lane output (AGENTS.md section 2 rule 7): nothing under `data/` was edited, no IDs allocated. "
      "Generated by `scripts/build_ipeds_completions.py` (stdlib); raw NCES files cached outside the repo "
      "(`%s`). All counts below name their unit and filter." % a.raw_dir)
    P("")
    P("## 1. Source and CIP set used")
    P("")
    P("- NCES IPEDS Completions `C<YYYY>_A` files, collection years %d-%d (awards July 1 of the prior year through June 30). "
      "`completions_year` = file year (C2024_A = AY2023-24 = 2024), the convention already on held `programs.csv` rows. "
      "C2010 excluded (no `CTOTALT`). Revised files (`*_rv`) used wherever shipped; **C2024_A is the provisional release** "
      "(its own dictionary Introduction sheet says so)." % (FIRST_YEAR, LAST_YEAR))
    P("- Columns verified from the C2024_A dictionary Varlist sheet: `UNITID`, `CIPCODE` (CIP 2020), `MAJORNUM` (1 first / 2 second major), "
      "`AWLEVEL` (detail codes 1-8, 17-21 summed; totals 12-15 never used), `CTOTALT` grand total with `XCTOTALT` flag.")
    P("- Institution names/states: HD2024. CIP titles: CIPCode2020.csv.")
    P("")
    P("| CIP 2020 | Title (from CIPCode2020.csv) | Role in this packet |")
    P("|---|---|---|")
    for c in POLYMER_SPECIFIC:
        P("| %s | %s | polymer-specific (lead tier 1) |" % (c, cip_title[c]))
    for c in COMPOSITES:
        P("| %s | %s | composites (lead tier 2; CIP is *New* in 2020, so absent before C2021) |" % (c, cip_title[c]))
    for c in BROAD_MATERIALS:
        P("| %s | %s | broad materials (lead tier 3; not polymer-specific) |" % (c, cip_title[c]))
    for c in extra_cips:
        P("| %s | %s | extracted only because a held program row carries it (outside the polymer set) |" % (c, cip_title[c]))
    P("")
    P("Corrections to the requested list, verified against CIPCode2020.csv: **14.3101 does not exist in CIP 2020** "
      "(Materials Science is 40.1001); **no 48.xxxx plastics machine technology code exists** (48.05 is Precision Metal Working; "
      "the only plastic/polymer/rubber/composite titles outside medical are 14.3201, 15.0607, 15.0617, 40.0507; no rubber CIP). "
      "15.0617 Composite Materials Technology was added and 14.28/19.0904 textile codes were left out (not requested).")
    P("")
    P("## 2. Completions extract (`completions.csv`)")
    P("")
    yrs = Counter(r["completions_year"] for r in rows_out if r["cip_code"] in CIP_SET)
    P("- Rows: %d (unit: UNITID x CIP x award level x year with first- or second-major completions > 0, years %d-%d, all %d extracted CIPs)."
      % (len(rows_out), FIRST_YEAR, LAST_YEAR, len(CIP_SET) + len(extra_cips)))
    P("- `completions_first_major` is the first-major count (MAJORNUM=1) - the basis of every proposal and lead count; "
      "second-major counts are carried in their own column and never summed in.")
    P("")
    P("**AY2023-24 (2024) polymer-set first-major completions, by CIP** (institutions = distinct UNITIDs with >0):")
    P("")
    P("| CIP | Institutions | Completions |")
    P("|---|---:|---:|")
    for c in CIP_SET:
        rr = [r for r in latest if r["cip_code"] == c]
        P("| %s %s | %d | %d |" % (c, cip_title[c], len({r["unitid"] for r in rr}), sum(r["completions_first_major"] for r in rr)))
    P("")
    P("**By award level (2024, first major, all six set CIPs):**")
    P("")
    P("| Award level | Completions |")
    P("|---|---:|")
    lc = Counter()
    for r in latest:
        lc[r["award_level"]] += r["completions_first_major"]
    for k, v in sorted(lc.items(), key=lambda kv: -kv[1]):
        P("| %s | %d |" % (k, v))
    P("")
    P("**Polymer-specific CIPs only (14.3201 + 15.0607 + 40.0507), 2024, top states by completions:**")
    P("")
    P("| State | Institutions | Completions |")
    P("|---|---:|---:|")
    sc = defaultdict(lambda: [set(), 0])
    for r in latest:
        if r["cip_code"] in POLYMER_SPECIFIC:
            sc[r["state"]][0].add(r["unitid"])
            sc[r["state"]][1] += r["completions_first_major"]
    for s, (us, n) in sorted(sc.items(), key=lambda kv: -kv[1][1])[:15]:
        P("| %s | %d | %d |" % (s, len(us), n))
    ps = [r for r in latest if r["cip_code"] in POLYMER_SPECIFIC]
    P("")
    P("Polymer-specific CIPs, 2024: %d institutions, %d first-major completions." %
      (len({r["unitid"] for r in ps}), sum(r["completions_first_major"] for r in ps)))
    P("")
    flags = Counter(r["first_major_flag"] for r in rows_out if r["completions_year"] == LAST_YEAR)
    P("`XCTOTALT` status flags on 2024 rows (rows, not completions): %s. Non-`R` flags mark imputed/derived values per the NCES "
      "dictionary; they are preserved in `first_major_flag` and not filtered." % ", ".join("%s=%d" % kv for kv in sorted(flags.items())))
    P("")
    P("## 3. Proposals (`program_proposals.csv`)")
    P("")
    P("Unit: one row per `data/programs.csv` row (%d rows)." % len(prog_rows))
    P("")
    P("| proposal_status | Program rows |")
    P("|---|---:|")
    for k, v in sorted(status_ct.items(), key=lambda kv: -kv[1]):
        P("| %s | %d |" % (k, v))
    P("")
    prop_vals = [r for r in prog_rows if r["prop_latest_completions"] != ""]
    P("- Program rows with a proposed `latest_completions`+`completions_year`: **%d** (%d confirm the held value, %d conflict with it, %d fill a blank, %d have a held CIP that is not polymer; a LEVEL MISMATCH / LEVEL PARTIAL suffix is counted with its base status)." % (
        len(prop_vals), sum(1 for r in prop_vals if r["proposal_status"].startswith("CONFIRMS_HELD")),
        sum(1 for r in prop_vals if r["proposal_status"].startswith("CONFLICT_REVIEW")),
        sum(1 for r in prop_vals if r["proposal_status"].startswith("PROPOSE")),
        sum(1 for r in prop_vals if r["proposal_status"].startswith("CIP_REVIEW"))))
    P("- Program rows with a proposed `first_year_awarded`: %d; with a proposed `last_year_awarded`: %d."
      % (sum(1 for r in prog_rows if r["prop_first_year_awarded"] != ""), sum(1 for r in prog_rows if r["prop_last_year_awarded"] != "")))
    P("- Join: degree rows with cip_code = %d; all resolved through `institution_org_id` -> `ecosystem.ipeds_unitid` -> HD2024." %
      sum(1 for r in prog_rows if r["program_type"] == "degree" and r["cip_code"]))
    rev = [r for r in prog_rows if r["unitid_name_check"].startswith("REVIEW") or r["unitid_name_check"].startswith("UNITID not")]
    P("- UNITID vs HD2024 name check (ecosystem legal_name vs HD INSTNM, similarity < 0.6 flagged): %d of %d joined rows flagged%s." % (
        len(rev), sum(1 for r in prog_rows if r["ipeds_unitid"]), (" - " + "; ".join("%s %s" % (r["program_id"], r["unitid_name_check"]) for r in rev)) if rev else ""))
    nj = [r for r in prog_rows if r["proposal_status"] == "NO_JOIN_KEY"]
    P("- NO_JOIN_KEY rows: %d (every institution_org_id lacks an `ipeds_unitid` in the Atlas). Of these, %d are colleges/universities with an exact HD2024 name+state candidate UNITID (unverified; needs an ecosystem backfill by the integrator: %s); the rest are labs, companies, associations and incubators with no IPEDS identity." % (
        len(nj), sum(1 for r in nj if r["candidate_unitid_by_name"]),
        "; ".join("%s -> %s %s" % (r["program_id"], r["candidate_unitid_by_name"], r["candidate_unitid_hd_name"]) for r in nj if r["candidate_unitid_by_name"]) or "none"))
    P("- Shared-key pairs (two degree rows, same UNITID x CIP, overlapping level): %d." % shared)
    P("")
    conf = [r for r in prog_rows if r["proposal_status"] in ("CONFLICT_REVIEW", "CIP_REVIEW")]
    if conf:
        P("**Rows to review before landing (held value vs pull, or held CIP not polymer):**")
        P("")
        P("| program_id | UNITID | institution | CIP | held | pull 2024 | note |")
        P("|---|---|---|---|---|---|---|")
        for r in conf:
            P("| %s | %s | %s | %s | %s/%s | %s | %s |" % (r["program_id"], r["ipeds_unitid"], r["hd2024_name"], r["cip_code"],
              r["held_latest_completions"], r["held_completions_year"], r["prop_latest_completions"], r["cip_scope_caveat"][:110]))
        P("")
    P("### SCHEMA constraints that limited the proposals")
    P("")
    P("1. **Degree rows only** (4.11): certificate/center/training/lab/course/apprenticeship rows get no IPEDS value even where they carry a cip_code; "
      "they are marked `join-key lead; institution page needed`. Certificate rows with an `ipeds_listing` CIP show the IPEDS count only inside `proposal_reason` as reference.")
    P("2. **Keyed pull needs a cip_code on the row**: degree rows with an empty cip_code are `join-key lead; institution page needed`; "
      "`candidate_polymer_cips_at_institution_2024` lists what IPEDS shows at the UNITID, informational only (a CIP must come from the catalog or be recorded as an `ipeds_listing` pair).")
    P("3. **Never estimated; `latest_completions` requires `completions_year`**: nothing is proposed when the mapped levels have zero 2024 completions, and `first_year_awarded` is withheld when completions already exist at the window floor (2011).")
    P("4. **IPEDS is a join key, never program evidence** (4.6 `ipeds_unitid`, 4.11 Lakeland rule): a proposal asserts a count at a CIP, not that the program exists; the held row's own-page evidence stays the basis.")
    P("5. **CIP-grain, not program-grain**: counts cover the whole CIP at the institution at the row's levels. For `14.1801` rows (Materials Engineering) this is the whole MSE-type count, not the polymer track (see `cip_scope_caveat`).")
    P("6. **The key is UNITID x CIP, not x level**: the proposed count is the first-major total over all detail award levels at that key (incl. post-baccalaureate certificates; flagged in `includes_postbacc_cert_2024`), "
      "which reproduces every held value that matches. Whether a row's own `level` set should narrow the count is not defined in SCHEMA; `level_alignment` and `row_level_completions_2024` show the narrower view without proposing it (an integrator/owner call).")
    P("7. `last_year_awarded` here means *latest year observed with completions in the pull window*; with `awarding_in_completions_year=yes` it is not a closure claim.")
    P("")
    P("## 4. Leads (`leads.csv`)")
    P("")
    P("Unit: IPEDS institutions (UNITID) with first-major completions > 0 in any of the six set CIPs during 2022-2024 whose UNITID has **no `programs.csv` row** "
      "(joined through `ecosystem.ipeds_unitid`). Sort: priority bucket (OH/PA, then top-10 NAICS 326 QCEW-gap states excluding OH/PA: %s, then others), "
      "then lead tier (polymer-specific, composites, broad materials), then 2024 polymer-specific+composites completions, then all-set completions. "
      "QCEW gap here = QCEW 2023 private NAICS 326 establishments minus Atlas strict 326 site rows (same definition as `build_qcew_denominators.py`)." % ", ".join(gap_states))
    P("")
    P("**These are discovery leads only.** A CIP listing never proves a polymer program (Lakeland and Lorain CC were rejected on their own catalogs); each needs the named-program test on the institution's own pages before any row.")
    P("")
    bt = Counter(r["lead_tier"] for r in leads)
    P("| Lead tier | Institutions |")
    P("|---|---:|")
    for k, v in sorted(bt.items()):
        P("| %s | %d |" % (k, v))
    P("")
    st = Counter(r["atlas_status"].split(" ")[0] for r in leads)
    P("Atlas status of lead institutions: " + "; ".join("%s=%d" % kv for kv in sorted(st.items())) + ".")
    P("")
    bk = Counter(r["priority_bucket"] for r in leads)
    P("By priority bucket (institutions): " + "; ".join("%s=%d" % kv for kv in sorted(bk.items())) + ".")
    P("")
    P("**Top 15 leads, polymer-specific tier only, ranked by 2024 polymer-specific completions nationally (file order differs because OH/PA/gap states sort first):**")
    P("")
    P("| # | UNITID | Institution | State | 2024 poly-specific | CIPs | Atlas status |")
    P("|---|---|---|---|---:|---|---|")
    t1 = sorted([r for r in leads if r["lead_tier"].startswith("1")], key=lambda r: (-r["polymer_specific_completions_2024"], r["institution_name"]))
    for i, r in enumerate(t1[:15], 1):
        P("| %d | %s | %s | %s | %d | %s | %s |" % (i, r["unitid"], r["institution_name"], r["state"], r["polymer_specific_completions_2024"],
          r["cips_with_completions_2022_2024"], r["atlas_status"].split(" ")[0]))
    P("")
    P("**First 15 rows in `leads.csv` order:**")
    P("")
    P("| rank | UNITID | Institution | State | bucket | tier | 2024 poly+comp | CIPs |")
    P("|---:|---|---|---|---|---|---:|---|")
    for r in leads[:15]:
        P("| %d | %s | %s | %s | %s | %s | %d | %s |" % (r["lead_rank"], r["unitid"], r["institution_name"], r["state"], r["priority_bucket"], r["lead_tier"],
          r["polymer_specific_completions_2024"] + r["composites_completions_2024"], r["cips_with_completions_2022_2024"]))
    P("")
    P("### Held institutions with polymer-specific / composites completions at a CIP no program row carries")
    P("")
    P("Not in `leads.csv` (the institution already has program rows). %d institution x CIP items (unit: UNITID x CIP with 2022-2024 completions); top 15 by 2024 completions:" % len(held_other_cip))
    P("")
    P("| UNITID | Institution | State | CIP | 2024 | CIPs on held rows |")
    P("|---|---|---|---|---:|---|")
    for u, n, s, c, v, carried in sorted(held_other_cip, key=lambda t: -t[4])[:15]:
        P("| %s | %s | %s | %s | %d | %s |" % (u, n, s, c, v, ",".join(carried) or "(none)"))
    P("")
    P("## 5. Caveats")
    P("")
    P("- IPEDS reports by institution x CIP; it does not name programs, and a CIP can be assigned to a program whose own catalog never mentions polymers (Lakeland rule). Sinclair CC reported 28 certificate completions in AY2023-24 for a program its catalog discontinued: completions can lag liveness.")
    P("- C2024_A is provisional; counts can change at final release. Held rows carrying 2024 values were drawn from the same release.")
    P("- Multi-campus systems report under separate UNITIDs (parent vs branch); a lead may be an existing Atlas institution under another UNITID - run the AGENTS.md section 3 dedupe checks before any record.")
    P("- 14.1801 / 40.1001 counts are whole-field counts and say nothing about polymer content. They are carried because held degree rows use 14.1801.")
    P("- `first_year_awarded` is bounded by the 2011 window floor and by CIP re-coding; a program re-coded to another CIP appears as a start.")
    P("- Lead state-priority uses a QCEW NAICS 326 gap proxy computed from repo files at run time; it orders review effort only.")
    P("- No personal data is involved; institution website is the HD2024 public institutional URL (a pointer, not program evidence).")
    P("")
    with open(os.path.join(out, "REPORT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
