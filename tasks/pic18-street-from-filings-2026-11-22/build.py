#!/usr/bin/env python3
"""25-site TRIAL: propose a street for a no-street PIC-18 site from government files (owner 2026-11-22, "Government files as a street source").
A street is PROPOSED only if (a) the organization has exactly one active site in that city+state; (b) each source family has exactly one
establishment (one street_key) in that city+state under a held name (exact or corporate-words); (c) the filing is dated on/after 2021-11-22;
(d) a SECOND independent source family gives the same street_key under a held name. One family alone is a lead. Two families that
each name one establishment but different streets are reported as DISAGREEING (the batch-5 failure).
Families: osha = ITA 300A + inspection; epa = RCRA / ICIS-AIR / NPDES (dated by the facility's latest evaluation, FCE/PCE or inspection).
FRS rows carry no date: listed, never counted. Own names only (site, legal, trade names); a match on a named parent only is held.
usage: build.py --cache DIR --out DIR"""
import argparse, csv, glob, random, sys
from collections import defaultdict, Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "pic18-size-sprint-2026-11-22"))
import build as B  # noqa: E402  (size-sprint matcher: name classes, street_key, same_street, CUTOFF, MAN)
from derive_last_activity import has_civic_number  # noqa: E402
csv.field_size_limit(10**9)
OK_NAME = ("exact", "corporate_suffix_only")

def civic_key(street):
    k = B.street_key(street)
    return k if k and has_civic_number(k) and len(k.split()) >= 2 else ""

EPA_UNDATED_OK = False   # sensitivity only (--epa-undated-counts): an EPA registry row with no dated event counts as current (snapshot 2026-11-21)

def candidates_for(site, held_own, held_all, ita, insp, epa):
    """-> list of dicts, one per raw row in the site's city+state with a held name. `counts` says whether it can support a proposal."""
    out = []; city = B.squash(site["city"])
    def add(fam, src, r, names, street, c, z, date, loc_extra):
        if B.squash(c) != city: return
        nm, held = B.name_class(held_own, names); nmp = B.name_class(held_all, names)[0]
        if nm not in OK_NAME:
            if nmp in OK_NAME: out.append(dict(family=fam, source=src, r=r, name=names[0], street=street, city=c, zip=z, date=date, name_match="parent_only", counts="no: matches only a named parent", **loc_extra))
            return
        why = "yes"
        if not civic_key(street): why = "no: street has no civic number or is a PO box"
        elif not date: why = "no: undated source"
        elif date < B.CUTOFF: why = "no: dated before 2021-11-22"
        out.append(dict(family=fam, source=src, r=r, name=names[0], street=street, city=c, zip=z, date=date, name_match=nm, counts=why, **loc_extra))
    for r in ita:
        add("osha", "osha_ita", r, [r["establishment_name"], r["company_name"]], r["street_address"], r["city"], r["zip_code"], f"{int(float(r['year_filing_for']))}-12-31", dict(date_locator=""))
    for r in insp:
        add("osha", "osha_inspection", r, [r["estab_name"]], r["site_address"], r["site_city"], r["site_zip"], r["open_date"][:10], dict(date_locator=""))
    for r in epa:
        loc = f"{r['event_member']}|row={r['event_row']}" if r["event_row"] else ""
        add("epa", "epa_" + r["family"], r, [r["name"]], r["street"], r["city"], r["zip"], r["event_date"] or ("2026-11-21" if EPA_UNDATED_OK else ""), dict(date_locator=(r["event_file"] + "|" + loc) if loc else ""))
    return out

def decide(site, n_active_city, cands):
    """-> (disposition, reason, detail, proposed_key). disposition: proposal | hold"""
    if n_active_city != 1: return ("hold", "org_has_multiple_active_sites_in_city", f"{n_active_city} active sites of the organization in this city and state", "")
    fam = defaultdict(set)
    for c in cands:
        if c["counts"] == "yes": fam[c["family"]].add(civic_key(c["street"]))
    if not fam:
        if any(c["name_match"] == "parent_only" for c in cands): return ("hold", "parent_name_only", "only a named parent's name matches a filing in this city", "")
        if any(c["counts"].startswith("no: dated") for c in cands): return ("hold", "stale_only", "held-name filings in this city are all dated before 2021-11-22 (leads)", "")
        if any(c["counts"].startswith("no: undated") for c in cands): return ("hold", "undated_only", "only an undated FRS row names it; FRS cannot support a proposal", "")
        return ("hold", "no_candidate", "no held-name row in this city in OSHA ITA, OSHA inspection or EPA ECHO", "")
    multi = {f: k for f, k in fam.items() if len(k) > 1}; one = {f: next(iter(k)) for f, k in fam.items() if len(k) == 1}
    if multi: return ("hold", "multiple_establishments", "; ".join(f"{f}: {sorted(k)}" for f, k in multi.items()) + " (more than one street under a held name in this city)", "")
    if len(one) == 1: return ("hold", "one_source_lead", f"only {next(iter(one))} names a street ({next(iter(one.values()))}); a second independent family is needed", "")
    if len(set(one.values())) > 1: return ("hold", "SOURCES_DISAGREE", "; ".join(f"{f}: {k}" for f, k in one.items()), "")
    zs = {B.zip5(c["zip"]) for c in cands if c["counts"] == "yes"} - {""}
    if site["zip"] and B.zip5(site["zip"]) and zs and B.zip5(site["zip"]) not in zs: return ("hold", "zip_conflict", f"site ZIP {site['zip']} vs filing ZIPs {sorted(zs)}", "")
    return ("proposal", "", "", next(iter(one.values())))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cache", required=True); ap.add_argument("--out", required=True); ap.add_argument("--epa-undated-counts", action="store_true", help="sensitivity only"); ap.add_argument("--parents", action="store_true", help="sensitivity only: let a named parent's name count as a held name"); a = ap.parse_args()
    global EPA_UNDATED_OK; EPA_UNDATED_OK = a.epa_undated_counts
    orgs, sites = B.load_atlas()
    frame = sorted(r["site_id"] for r in csv.DictReader(open(HERE.parent / "pic18-size-sprint-2026-11-22/no_street_sites.csv")))
    random.Random(20261122).shuffle(frame); sel = frame[:25]; sd = {s["site_id"]: s for s in sites}
    ita = [r for r in B.rd(f"{a.cache}/ita_oh.csv")]; insp = B.rd(f"{a.cache}/insp_oh.csv"); epa = B.rd(f"{a.cache}/epa_oh.csv")
    active = [s for s in sites if s["operating_status"] == "active"]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rows_c, rows_p, rows_h, dis = [], [], [], {}
    for sid in sel:
        s = sd[sid]; held_all = B.held_names(s, orgs); held_own = held_all if a.parents else {k: v for k, v in held_all.items() if not v.startswith("parent:")}
        n_city = sum(1 for t in active if t["org_id"] == s["org_id"] and B.squash(t["city"]) == B.squash(s["city"]) and t["state"] == s["state"])
        cands = candidates_for(s, held_own, held_all, ita, insp, epa)
        d = decide(s, n_city, cands); dis[sid] = d
        for c in cands:
            r = c["r"]; f = r["file"]; m = B.MAN.get("./" + f, "")
            rows_c.append([sid, s["org_id"], c["family"], c["source"], "raw/" + f, m, f"{r['member']}|row={r['row']}|id={r['rid'] if 'rid' in r and c['source'].startswith('osha') else r['id']}", c["name"], c["street"], c["city"], c["zip"], c["date"], c["date_locator"], c["name_match"], c["counts"]])
        if d[0] == "proposal":
            keys = [c for c in cands if c["counts"] == "yes"]
            rows_p.append([sid, s["org_id"], s["site_name"], s["city"], d[3], " | ".join(sorted({f"{c['source']}: {c['street']} ({c['date']})" for c in keys}))])
        else: rows_h.append([sid, s["org_id"], d[1], d[2]])
    def w(name, hdr, rows):
        with open(out / name, "w", newline="") as f: x = csv.writer(f); x.writerow(hdr); x.writerows(rows)
    w("candidates.csv", ["site_id", "org_id", "family", "source", "source_file", "file_sha256", "row_locator", "filing_name", "filing_street", "filing_city", "filing_zip", "date", "date_locator", "name_match", "counts_toward_proposal"], rows_c)
    w("proposals.csv", ["site_id", "org_id", "site_name", "city", "proposed_street_key", "evidence"], rows_p)
    w("holds.csv", ["site_id", "org_id", "reason", "detail"], rows_h)
    w("frame.csv", ["site_id", "org_id", "site_name", "city", "zip"], [[i, sd[i]["org_id"], sd[i]["site_name"], sd[i]["city"], sd[i]["zip"]] for i in sel])
    print("25 sites:", Counter("proposal" if d[0] == "proposal" else d[1] for d in dis.values()))

if __name__ == "__main__": main()
