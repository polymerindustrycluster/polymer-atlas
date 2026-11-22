"""PIC-18 site size bands from OSHA ITA Form 300A (CY2025), SCHEMA §1 R13 source 1. Fixed 23-pair frame (frame.csv).

    python3 build.py [--apply] [--base REF]   plans from frame.csv + current data/ + tasks/osha-ita-2026-11-01/establishments.csv,
                                              writes verdicts.csv, fills.csv, evidence_rows.csv, counts.json; --apply edits data/ (idempotent).
A band is written only when ALL hold: the ITA street is the record's street_address (street_key equal, or a named
judgment in STREET_JUDGED), the ITA name is the operator (name_key equal, or NAME_JUDGED), ITA reliability is ok,
the cell is blank, the establishment is bound to exactly one site record, and no other source seen for the site
(OSHA inspection spine) is more than one band away. Everything else is held, STILL_UNCERTAIN with the settling fact."""
import argparse, csv, io, json, re, subprocess, sys
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
csv.field_size_limit(10 ** 9)

CREATED_BY = "claude-code pic18-size-ita-2026-11-22"
OBSERVED = "2026-11-01"  # date the CY2025 file was extracted into the repo; nothing was re-read from the source today
EVD_FIRST, EVD_LAST = 480000, 480099  # reserved for this lane
BANDS = ["1-9", "10-49", "50-99", "100-249", "250-499", "500-999", "1000-4999", "5000+"]
ITA = ROOT / "tasks/osha-ita-2026-11-01/establishments.csv"
SPINE = ROOT / "tasks/osha-spine-2026-11-01/band_proposals.csv"

# Judgments the key functions cannot make; each is a named, reasoned exception (README "Judgment calls").
STREET_JUDGED = {
    "SITE-000264": "Enterprise Parkway / Enterprises pkwy: plural in the filing; same number, same city (Seville), one ITA establishment at the address",
    "SITE-000620": "1700A / 1700 Old Mansfield: unit letter on the record's number; same operator, same city, one ITA establishment at the address, no other Speed site on the street",
    "SITE-001109": "Commercial / Commerical: typo in the filing; same number, same city, same operator",
}
NAME_JUDGED = {
    "SITE-000383": "ITA 'Graphic Arts Systems Inc' vs the record's own trade name 'Graphic Art Systems Inc' (one letter); same operator at the same street",
}
ABBR = {"road": "rd", "street": "st", "avenue": "ave", "parkway": "pkwy", "boulevard": "blvd", "drive": "dr", "north": "n", "south": "s",
        "east": "e", "west": "w", "highway": "hwy", "lane": "ln", "court": "ct", "route": "rte"}
DIRS = {"n", "s", "e", "w", "ne", "nw", "se", "sw"}
CORP = {"inc", "llc", "corp", "corporation", "company", "co", "the", "ltd", "division", "facility", "plant"}


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write(p, rows, fields):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n"); w.writeheader(); w.writerows(rows)


def street_key(s):
    t = re.sub(r"[^a-z0-9 ]", " ", (s or "").lower().replace(".", "")).split()
    for stop in ("suite", "ste", "unit"):  # drop the unit tail
        if stop in t: t = t[:t.index(stop)]
    t = [ABBR.get(w, w) for w in t]
    while len(t) > 1 and t[-1] in DIRS: t.pop()  # trailing quadrant only; a leading N/S/E/W is part of the street
    return " ".join(t)


def name_key(s):
    return " ".join(w for w in re.sub(r"[^a-z0-9 ]", " ", (s or "").lower().replace("&", " and ")).split() if w not in CORP)


def band_of(n):
    return next(b for hi, b in zip((9, 49, 99, 249, 499, 999, 4999, 10 ** 9), BANDS) if n <= hi)


def load():
    sites, orgs, shard = {}, {}, {}
    for p in sorted((ROOT / "data").glob("sites_*.csv")):
        for r in read(p): sites[r["site_id"]] = r; shard[r["site_id"]] = p.stem.split("_", 1)[1]
    for p in sorted((ROOT / "data").glob("organizations_*.csv")):
        for r in read(p): orgs[r["org_id"]] = r
    return sites, orgs, shard


def bound_sites(est):
    """Every site record, tree-wide, carrying an evidence row that cites this ITA establishment_id."""
    pat = re.compile(rf"establishment_id {est}\b")
    return {e["record_id"] for p in (ROOT / "data").glob("evidence_sites_*.csv") for e in read(p) if pat.search(e["source_ref"])}


def base_max_evd(base):
    names = [n for n in subprocess.check_output(["git", "ls-tree", "--name-only", base, "data/"], cwd=ROOT, text=True).split()
             if Path(n).name.startswith("evidence_")]
    return max(int(r["evidence_id"][4:]) for n in names for r in csv.DictReader(io.StringIO(subprocess.check_output(["git", "show", f"{base}:{n}"], cwd=ROOT, text=True)))
               if re.fullmatch(r"EVD-\d+", r["evidence_id"]))


def my_evidence():
    return {e["record_id"]: e["evidence_id"] for p in (ROOT / "data").glob("evidence_sites_*.csv") for e in read(p) if e["created_by"] == CREATED_BY}


def plan():
    sites, orgs, shard = load()
    ita = {r["establishment_id"]: r for r in read(ITA)}
    spine = {r["site_id"]: r for r in read(SPINE)}
    mine = my_evidence()
    verdicts = []
    for fr in read(D / "frame.csv"):
        sid, est = fr["site_id"], fr["establishment_id"]
        s, i = sites[sid], ita[est]
        o = orgs[s["org_id"]]
        site_names = {name_key(re.split(r" [—–-] ", s["site_name"])[0]), name_key(o["legal_name"])} | {name_key(t) for t in o["trade_names"].split(";") if t.strip()}
        ita_names = {name_key(re.split(r" [—–-] ", i["establishment_name"])[0]), name_key(i["establishment_name"]), name_key(i["company_name"])} - {""}
        n = int(i["annual_average_employees"]); band = band_of(n)
        why = []
        street = s["street_address"].strip()
        if not street: why.append("no recorded street_address (settles: an address pass that records the street, then re-test)")
        elif street_key(street) != street_key(i["street"]) and sid not in STREET_JUDGED:
            why.append(f"different street: record {street!r}, ITA {i['street']!r} (settles: which address is the establishment's)")
        if not (site_names & ita_names) and sid not in NAME_JUDGED: why.append("ITA name is not tied to the operator by the record (settles: a record name or trade name equal to the ITA name)")
        if i["reliability"] != "ok": why.append(f"ITA reliability={i['reliability']!r}, size_code_vs_avg={i['size_code_vs_avg_employees']!r} (settles: an amended filing or a second source for the count)")
        cell = s["employee_band_site"].strip()
        if cell and not (cell == band and sid in mine): why.append("band cell not blank")  # a cell this pass already filled is not a hold
        bs = bound_sites(est)
        if bs != {sid}: why.append(f"establishment bound to {len(bs)} site records {sorted(bs)}: dedupe lead, never merged here (settles: an integrator dedupe ruling)")
        if i["ita_estabs_at_address"] != "1": why.append("more than one ITA establishment at the address")
        sp = spine.get(sid)
        if sp:
            seen = set(sp["bands_seen_all_inspections"].split(";")) | {sp["proposed_employee_band_site"]}
            far = sorted(b for b in seen if b and abs(BANDS.index(b) - BANDS.index(band)) > 1)
            if far: why.append(f"R13: OSHA inspection nr_in_estab bands {far} are more than one band from ITA {band} (settles: review of which count is the establishment's)")
        verdicts.append(dict(site_id=sid, establishment_id=est, org_id=s["org_id"], controller_disposition=fr["controller_disposition"],
                             disposition="held" if why else "applied", verdict="STILL_UNCERTAIN" if why else "VERIFIED",
                             ita_band=band, ita_filed=i["date_submitted"], record_street=street, ita_street=i["street"],
                             street_rule=("judged" if sid in STREET_JUDGED else "key_equal" if street and street_key(street) == street_key(i["street"]) else "no"),
                             name_rule=("judged" if sid in NAME_JUDGED else "key_equal" if site_names & ita_names else "no"),
                             reasons=" | ".join(why)))
    return verdicts, sites, shard


def rows_for(verdicts, shard, first, mine):
    fills, evs = [], []
    k = 0
    for v in (x for x in verdicts if x["disposition"] == "applied"):
        sid, band = v["site_id"], v["ita_band"]
        if sid in mine: eid = mine[sid]
        else: eid = f"EVD-{first + k}"; k += 1
        fills.append(dict(site_id=sid, shard=shard[sid], field="employee_band_site", old="", new=band, establishment_id=v["establishment_id"], evidence_id=eid, filed=v["ita_filed"]))
        evs.append(dict(evidence_id=eid, record_table="sites", record_id=sid, claim_type="size_band",
                        claim_detail=f"employee_band_site={band}: OSHA ITA 300A CY2025, establishment_ID {v['establishment_id']}: annual average employees in {band} (band only, not a headcount)",
                        source_class="government_filing",
                        source_ref=f"OSHA ITA Form 300A CY2025, establishment_id {v['establishment_id']} (https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data)",
                        observed_date=OBSERVED, tier_effect="supports_B", created_by=CREATED_BY,
                        notes=f"ITA filing dated {v['ita_filed']}; street and operator name re-tested against the record's street_address and names; blank-only fill; no organization band written", address_role=""))
    return fills, evs


def append_tail(path, rows):
    """Byte-preserving append: the shard has 30 pre-existing out-of-order spots, so re-sorting it would rewrite other waves' rows."""
    raw = path.read_bytes()
    assert raw.endswith(b"\n") and b"\r\n" not in raw, "shard must be LF and end with a newline"
    hdr = next(csv.reader(io.StringIO(raw.decode("utf-8"))))
    buf = io.StringIO(); w = csv.writer(buf, lineterminator="\n")
    for r in rows: w.writerow([r.get(c, "") for c in hdr])
    path.write_bytes(raw + buf.getvalue().encode("utf-8"))


def note_of(f):
    return f"BAND-SOURCE: employee_band_site={f['new']} from OSHA ITA Form 300A CY2025, filed {f['filed']} (government_filing; band only, not a headcount)."


def apply(fills, evs, base):
    mx = base_max_evd(base)
    assert all(EVD_FIRST <= int(e["evidence_id"][4:]) <= EVD_LAST and int(e["evidence_id"][4:]) > mx for e in evs), f"evidence IDs outside the reserved block or not above the tree max {mx}"
    for sh in sorted({f["shard"] for f in fills}):
        mine = {f["site_id"]: f for f in fills if f["shard"] == sh}
        p = ROOT / "data" / f"sites_{sh}.csv"; rows = read(p); n_before = len(rows)
        for r in rows:
            f = mine.get(r["site_id"])
            if not f: continue
            assert r["employee_band_site"] in ("", f["new"]), "refuse a non-blank cell"
            r["employee_band_site"] = f["new"]
            if note_of(f) not in r["notes"]: r["notes"] = (r["notes"].rstrip() + " " if r["notes"].strip() else "") + note_of(f)
        assert len(rows) == n_before
        write(p, rows, list(rows[0]))
        ev_p = ROOT / "data" / f"evidence_sites_{sh}.csv"
        have = {e["record_id"] for e in read(ev_p) if e["created_by"] == CREATED_BY}
        new = [e for e in evs if e["record_id"] in mine and e["record_id"] not in have]  # idempotent: never a second row for a filled site
        if new: append_tail(ev_p, new)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); ap.add_argument("--base", default="origin/main"); a = ap.parse_args()
    verdicts, sites, shard = plan()
    fills, evs = rows_for(verdicts, shard, max(EVD_FIRST, base_max_evd(a.base) + 1), my_evidence())
    write(D / "verdicts.csv", verdicts, list(verdicts[0])); write(D / "fills.csv", fills, list(fills[0])); write(D / "evidence_rows.csv", evs, list(evs[0]))
    c = Counter(v["disposition"] for v in verdicts)
    (D / "counts.json").write_text(json.dumps(dict(frame=len(verdicts), dispositions=dict(c), fills=len(fills), organizations_filled=len({sites[f["site_id"]]["org_id"] for f in fills}),
                                                   fills_by_band=dict(Counter(f["new"] for f in fills))), indent=2, sort_keys=True) + "\n")
    if a.apply: apply(fills, evs, a.base)
    print((D / "counts.json").read_text())


if __name__ == "__main__":
    main()
