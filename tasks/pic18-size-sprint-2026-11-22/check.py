#!/usr/bin/env python3
"""Replay every packet row from the raw store by path and hash; fail on anything that does not replay.
For each packet row: the file's sha256 equals the packet's and MANIFEST.sha256; the row at the locator exists and carries the
locator's id; its street equals the site's street (derive_last_activity.same_street, city or ZIP agreeing); a name the record
holds is on the filing; the count behind the band is positive and bands to the packet's band; the filing year matches; the site is
in the frame (size-unknown PIC-18 org, active A-C OH site); Form 5500 rows only for an organization with one active site.
--selftest plants a wrong band and a row from a different street and requires both to be caught.
usage: check.py --packet packet.csv --raw /Volumes/.../atlas-store/raw [--selftest] [--no-hash]"""
import argparse, csv, hashlib, io, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B  # noqa: E402
csv.field_size_limit(10**9)

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""): h.update(c)
    return h.hexdigest()

def stream(path, member):
    f = io.TextIOWrapper(zipfile.ZipFile(path).open(member), encoding="utf-8-sig", errors="replace", newline="") if member else open(path, newline="", encoding="utf-8-sig", errors="replace")
    with f:
        for i, r in enumerate(csv.DictReader(f), 1): yield i, {k.lower(): v for k, v in r.items()}

def fetch_rows(raw, rows):
    """{(file, member): {ordinal: row}} streaming each file once, up to its largest wanted ordinal."""
    want = defaultdict(set)
    for p in rows:
        member, rowno, _ = parse_loc(p["row_locator"]); want[(p["source_file"], member)].add(rowno)
    got = {}
    for (fn, member), ords in want.items():
        got[(fn, member)] = {}; top = max(ords)
        for i, r in stream(f"{raw}/{fn[4:]}", member or None):
            if i in ords: got[(fn, member)][i] = r
            if i >= top: break
    return got

def parse_loc(loc):
    member, rowp, idp = loc.split("|"); return member, int(rowp.split("=", 1)[1]), idp.split("=", 1)[1]

def run(packet, raw, orgs, sites, fr_ids, man, do_hash=True):
    errs = []; active_n = Counter(s["org_id"] for s in sites if s["operating_status"] == "active"); by_site = {s["site_id"]: s for s in sites}
    hashes = {}
    got = fetch_rows(raw, packet)
    for p in packet:
        tag = p["site_id"]; s = by_site.get(tag)
        if not s: errs.append(f"{tag}: site not in Atlas"); continue
        if tag not in fr_ids: errs.append(f"{tag}: not in the frame (size-unknown PIC-18 org, active A-C OH site)")
        fn = p["source_file"]
        if man.get("./" + fn[4:]) != p["file_sha256"]: errs.append(f"{tag}: packet sha256 != MANIFEST for {fn}")
        if do_hash:
            hashes.setdefault(fn, sha(f"{raw}/{fn[4:]}"))
            if hashes[fn] != p["file_sha256"]: errs.append(f"{tag}: file on disk hashes to {hashes[fn][:12]}, packet says {p['file_sha256'][:12]}")
        member, rowno, rid = parse_loc(p["row_locator"]); r = got[(fn, member)].get(rowno)
        if r is None: errs.append(f"{tag}: no row {rowno} in {fn}"); continue
        k = p["source"]
        if k == "osha_ita":
            idv, streets, names, cnt, yr = r.get("id", ""), [(r["street_address"], r["city"], r["zip_code"])], [r["establishment_name"], r["company_name"]], B.num(r["annual_average_employees"]), str(int(float(r["year_filing_for"])))
        elif k == "osha_inspection":
            idv, streets, names, cnt, yr = r["activity_nr"], [(r["site_address"], r["site_city"], r["site_zip"])], [r["estab_name"]], B.num(r["nr_in_estab"]), r["open_date"][:4]
        elif k == "form5500":
            sf = "sponsor_dfe_name" not in r
            g = (lambda a, b: r.get(b if sf else a, ""))
            idv, names, cnt, yr = r["ack_id"], [g("sponsor_dfe_name", "sf_sponsor_name"), g("spons_dfe_dba_name", "sf_sponsor_dfe_dba_name")], B.num(g("tot_active_partcp_cnt", "sf_tot_act_partcp_eoy_cnt")), (g("form_plan_year_begin_date", "sf_plan_year_begin_date"))[:4]
            streets = [(g("spons_dfe_loc_us_address1", "sf_spons_loc_us_address1"), g("spons_dfe_loc_us_city", "sf_spons_loc_us_city"), ""), (g("spons_dfe_mail_us_address1", "sf_spons_us_address1"), g("spons_dfe_mail_us_city", "sf_spons_us_city"), "")]
            if active_n[s["org_id"]] != 1: errs.append(f"{tag}: Form 5500 row for an organization with {active_n[s['org_id']]} active sites")
        else: errs.append(f"{tag}: unknown source {k}"); continue
        if k == "osha_ita": sdate = f"{yr}-12-31"
        elif k == "osha_inspection": sdate = r["open_date"][:10]
        else:
            b = g("form_plan_year_begin_date", "sf_plan_year_begin_date")[:10]; t = g("form_tax_prd", "sf_tax_prd")[:10]; sdate = t if t and t >= b else f"{int(b[:4]) + 1}{b[4:]}"
        if sdate != p["source_date"]: errs.append(f"{tag}: source date {sdate} != packet {p['source_date']}")
        if sdate < B.CUTOFF: errs.append(f"{tag}: source date {sdate} is before {B.CUTOFF} (stale_over_5_years)")
        if idv != rid: errs.append(f"{tag}: row {rowno} carries id {idv}, locator says {rid}")
        if not any(B.same_street(s["street_address"], st) and B.city_ok(s, c, z) for st, c, z in streets): errs.append(f"{tag}: street differs: site {s['street_address']!r} vs filing {[x[0] for x in streets]}")
        nm = B.name_class(B.held_names(s, orgs), [n for n in names if n.strip()])[0]
        if nm not in ("exact", "corporate_suffix_only") or nm != p["name_match"]: errs.append(f"{tag}: filing names {names} classify as {nm}, packet says {p['name_match']}; only exact / corporate_suffix_only are accepted")
        if cnt < 1: errs.append(f"{tag}: count behind the band is not positive")
        elif B.band_of(cnt) != p["band"]: errs.append(f"{tag}: row bands to {B.band_of(cnt)}, packet says {p['band']}")
        if yr != str(p["filing_year"]): errs.append(f"{tag}: filing year {yr} != packet {p['filing_year']}")
    return errs

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--packet", required=True); ap.add_argument("--raw", required=True)
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--no-hash", action="store_true"); a = ap.parse_args()
    packet = list(csv.DictReader(open(a.packet, newline="")))
    orgs, sites = B.load_atlas(); fr, _, _ = B.frame(orgs, sites); fr_ids = {s["site_id"] for s in fr}
    man = {}
    for ln in open(f"{a.raw}/MANIFEST.sha256"):
        h, _, pth = ln.rstrip("\n").partition("  "); man[pth] = h
    errs = run(packet, a.raw, orgs, sites, fr_ids, man, not a.no_hash)
    print(f"replayed {len(packet)} packet rows: {len(errs)} failures"); [print("  FAIL", e) for e in errs[:50]]
    bad = bool(errs)
    if a.selftest:
        assert len(packet) >= 2, "selftest needs two packet rows"
        wrong = [dict(r) for r in packet[:1]]; wrong[0]["band"] = next(b for b in B.BANDS if b != wrong[0]["band"])
        e1 = run(wrong, a.raw, orgs, sites, fr_ids, man, False)
        other = next((r for r in packet[1:] if B.street_key(next(s for s in sites if s["site_id"] == r["site_id"])["street_address"]) != B.street_key(next(s for s in sites if s["site_id"] == packet[0]["site_id"])["street_address"])), None)
        planted = [dict(packet[0])]; planted[0].update({k: other[k] for k in ("source", "source_file", "file_sha256", "row_locator", "filing_year", "band")})
        e2 = run(planted, a.raw, orgs, sites, fr_ids, man, False)
        ok1, ok2 = any("bands to" in e for e in e1), any("street differs" in e for e in e2)
        old = [dict(packet[0])]; old[0]["source_date"] = "2019-12-31"
        ok3 = any("source date" in e for e in run(old, a.raw, orgs, sites, fr_ids, man, False))
        print("selftest wrong band caught:", ok1, "| row from a different street caught:", ok2, "| stale source date caught:", ok3); bad = bad or not (ok1 and ok2 and ok3)
    sys.exit(1 if bad else 0)

if __name__ == "__main__": main()
