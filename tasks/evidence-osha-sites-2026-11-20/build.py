#!/usr/bin/env python3
"""OSHA lane: existence, address and liveness witnesses for zero-evidence Atlas sites from OSHA ITA Form 300A filings.

    python3 tasks/evidence-osha-sites-2026-11-20/build.py match . <osha.csv> <corpus>   # frame, ledger, packet, bundle
    python3 tasks/evidence-osha-sites-2026-11-20/build.py plant . <osha.csv>            # defect injection: expect 0
    python3 tasks/evidence-osha-sites-2026-11-20/build.py selftest

A Form 300A summary is a filing the establishment makes to OSHA: SCHEMA §4.13 `government_filing`, A-capable for every
claim. A site is witnessed only when a 2025 filing sits at the site's own street address (same state, street number,
first street word and city) AND carries the operator's or the site's name. An address match under another name is held
(record-health lead), never written. Liveness rows follow the owner's ruling of 2026-11-20: a government filing whose
covered period ended within 24 months witnesses liveness (calendar 2025 ended 2025-12-31). Rows cite the filing by
name and establishment ID (a named source: SCHEMA §4.22 / V-66 archive-at-capture does not apply). Stdlib only.
"""
import csv, glob, json, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OBSERVED = "2026-11-20"
CREATED_BY = "claude-code-evd-osha-lane"
OSHA_FILE = "ITA_300A_Summary_Data_2025_through_08-31-2026.csv"
OSHA_SHA = "9ea2ee5d7265cddf"  # first 16 hex of the file's sha256, fetched 2026-11-20
SUFFIX = re.compile(r"\b(incorporated|inc|llc|corporation|corp|company|co|ltd|limited|lp|llp|the)\b")
DIR = {"n", "s", "e", "w", "north", "south", "east", "west", "ne", "nw", "se", "sw"}


def norm(s):
    s = re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower().replace("&", " and "))
    return re.sub(r"\s+", " ", SUFFIX.sub(" ", s)).strip()


def street_key(s):
    """(street number, first street word): '173 Industrial Pkwy' and '173 Industrial Parkway North' agree."""
    toks = norm(s).split()
    if not toks or not toks[0].isdigit():
        return None
    word = next((t for t in toks[1:] if t not in DIR and not t.isdigit()), None)
    return (toks[0], word) if word else None


def named(names, r):
    # OSHA establishments are often named for their town ("Leola", "Nashville"); a bare city name identifies no operator
    est = {norm(r["establishment_name"]), norm(r["company_name"])} - {"", norm(r["city"])}
    return any(len(min(a, b, key=len)) >= 4 and (a == b or a in b or b in a) for a in names for b in est)


def rd(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def wr(p, rows, fields):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def load(repo, osha_csv):
    data = Path(repo) / "data"
    ev = {r["record_id"].strip() for f in data.glob("evidence_*.csv") for r in rd(f) if r["record_table"] == "sites"}
    ops = {r["org_id"]: r for f in data.glob("organizations_*.csv") for r in rd(f)}
    ops.update({r["org_id"]: r for r in rd(data / "ecosystem.csv")})
    frame = []
    for f in sorted(data.glob("sites_*.csv")):
        for s in rd(f):
            if s["site_id"] in ev or s["operating_status"] != "active" or not street_key(s["street_address"]):
                continue
            op = ops.get(s["org_id"], {})
            frame.append(dict(s, _shard=f.stem.split("_", 1)[1], _op=op.get("legal_name", ""),
                              _names=sorted({x for x in [norm(op.get("legal_name")), norm(s["site_name"])] +
                                             [norm(t) for t in (op.get("trade_names") or "").split(";")] if x})))
    idx = defaultdict(list)
    with open(osha_csv, encoding="utf-8", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh):
            k = street_key(r["street_address"])
            if k:
                idx[(r["state"].strip().upper(), k[0], k[1], norm(r["city"]))].append(r)
    return frame, idx


def best(s, idx, key_from=None):
    k = street_key((key_from or s)["street_address"])
    src = key_from or s
    cands = idx.get((src["state"].strip().upper(), k[0], k[1], norm(src["city"])), [])
    hit = next((r for r in cands if named(s["_names"], r)), None)
    return ("ADDR+NAME", hit) if hit else (("ADDR_ONLY", cands[0]) if cands else ("NONE", None))


def match(repo, osha_csv, corpus):
    frame, idx = load(repo, osha_csv)
    ledger, packet, bundle = [], [], []
    for s in frame:
        verdict, r = best(s, idx)
        ledger.append({"site_id": s["site_id"], "tier": s["verification_tier"], "verdict": verdict, "operator": s["_op"],
                       "site_name": s["site_name"], "atlas_street": s["street_address"], "city": s["city"], "state": s["state"],
                       "osha_establishment_id": r["establishment_ID"] if r else "", "osha_establishment": r["establishment_name"] if r else "",
                       "osha_company": r["company_name"] if r else "", "osha_street": r["street_address"] if r else ""})
        if verdict != "ADDR+NAME":
            continue
        eff = "supports_U" if s["verification_tier"] == "U" else "supports_A"
        where = f"{r['street_address']}, {r['city']}, {r['state']} {r['zip_code']}".strip()
        cite = f"OSHA ITA Form 300A summary, filing year {r['year_filing_for']}, establishment ID {r['establishment_ID']} (osha.gov {OSHA_FILE})"
        base = {"record_table": "sites", "record_id": s["site_id"], "source_class": "government_filing", "source_ref": cite,
                "observed_date": OBSERVED, "tier_effect": eff, "created_by": CREATED_BY, "_shard": s["_shard"]}
        note = f"Read {OBSERVED} from the OSHA ITA 300A bulk file {OSHA_FILE} (sha256 {OSHA_SHA}…); site tier unchanged."
        packet += [
            dict(base, claim_type="existence", notes=note, claim_detail=(
                f"OSHA Form 300A summary for {r['year_filing_for']} names establishment '{r['establishment_name']}'"
                + (f" of '{r['company_name']}'" if r['company_name'].strip() else "")
                + f" at {where}; matches the site's operator '{s['_op']}' at its recorded street")),
            dict(base, claim_type="address", notes=note + " County is not in the filing.", claim_detail=(
                f"street_address {s['street_address']}, {s['city']}, {s['state']}: the {r['year_filing_for']} OSHA Form 300A "
                f"summary gives {where}")),
            dict(base, claim_type="liveness", notes=note + " Liveness under owner ruling 2026-11-20 (government filing; covered "
                 "period ended within 24 months).", claim_detail=(
                f"operating in calendar {r['year_filing_for']}: OSHA Form 300A summary submitted "
                f"{r['date_submitted'][:10]} reports {r['annual_average_employees']} annual average employees")),
        ]
        bundle.append({"record_id": s["site_id"], "atlas": {"site_name": s["site_name"], "operator": s["_op"],
                       "street": s["street_address"], "city": s["city"], "state": s["state"], "tier": s["verification_tier"]},
                       "osha": {k: r[k] for k in ("establishment_ID", "establishment_name", "company_name", "street_address", "city",
                                                  "state", "zip_code", "naics_code", "industry_description", "year_filing_for",
                                                  "date_submitted", "annual_average_employees")},
                       "proposed": {p["claim_type"]: p["claim_detail"] for p in packet[-3:]}})
    Path(corpus).mkdir(parents=True, exist_ok=True)
    wr(HERE / "ledger.csv", ledger, list(ledger[0]))
    wr(HERE / "packet_rows.csv", packet, list(packet[0]))
    (HERE / "review_bundle.json").write_text(json.dumps(bundle, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"frame {len(frame)} active zero-evidence sites with a street; verdicts {dict(Counter(l['verdict'] for l in ledger))}; "
          f"packet {len(packet)} rows on {len(bundle)} sites; tiers {dict(Counter(b['atlas']['tier'] for b in bundle))}")


def plant(repo, osha_csv):
    """Defect injection: score each site's names against ANOTHER site's address bucket (rotated by one); expect 0."""
    frame, idx = load(repo, osha_csv)
    same = lambda a, b: (street_key(a["street_address"]), norm(a["city"]), a["state"]) == (street_key(b["street_address"]), norm(b["city"]), b["state"])
    hits = []
    for i, s in enumerate(frame):
        o = frame[(i + 1) % len(frame)]
        if o["org_id"] != s["org_id"] and not same(s, o) and best(s, idx, key_from=o)[0] == "ADDR+NAME":  # shared addresses are real
            hits.append(s["site_id"])
    print(f"plant: {len(hits)} ADDR+NAME from {len(frame)} mismatched pairings (expect 0){': ' + ', '.join(hits[:10]) if hits else ''}")
    return len(hits)


def selftest():
    assert street_key("173 Industrial Pkwy") == street_key("173 Industrial Parkway North")[:1] + ("industrial",)
    assert street_key("500 S. Spencer Road") == ("500", "spencer") and street_key("Route 9") is None
    assert norm("Manufacturing Specialties, Inc") == norm("Manufacturing Specialties Inc.")
    assert named(["genpak"], {"establishment_name": "Genpak Westlake", "company_name": "Genpak LLC", "city": "Westlake"})
    assert not named(["abc"], {"establishment_name": "ABC Holdings", "company_name": "", "city": "X"})  # short names never contain-match
    assert not named(["marbleon leola"], {"establishment_name": "Leola", "company_name": "Westlake Pipe", "city": "Leola"})
    print("selftest ok")


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "match":
        match(sys.argv[2], sys.argv[3], sys.argv[4])
    elif m == "plant":
        sys.exit(1 if plant(sys.argv[2], sys.argv[3]) else 0)
    else:
        selftest()
