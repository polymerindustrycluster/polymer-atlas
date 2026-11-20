#!/usr/bin/env python3
"""TRI lane: existence witnesses for zero-evidence organizations from their EPA TRI facility records.

    python3 tasks/evidence-tri-filings-2026-11-20/build.py frame .  <corpus>   # frame.csv from this tree
    python3 tasks/evidence-tri-filings-2026-11-20/build.py fetch    <corpus>   # live: data.epa.gov efservice, cached
    python3 tasks/evidence-tri-filings-2026-11-20/build.py match .  <corpus>   # ledger.csv, packet_rows.csv, review bundle
    python3 tasks/evidence-tri-filings-2026-11-20/build.py selftest            # offline matcher checks

A TRI facility record is a filing the facility makes to EPA: SCHEMA §4.13 source_class `government_filing`
(A-capable). The witness test is identity: the record's facility name, or its parent-company name, equals the
organization's legal, trade or dba name after normalization (case, punctuation, legal suffixes). A closed-facility flag,
a near-miss name, or no match produces no row. Rows cite the filing by name and TRIFID (a named-source citation, so
SCHEMA §4.22 / V-66 archive-at-capture does not apply). TRI contact fields (names, emails, phones) are dropped at
fetch and never cached, printed or written (AGENTS.md §6).
"""
import csv, glob, json, re, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OBSERVED = "2026-11-20"
CREATED_BY = "claude-code-evd-tri-lane"
PERSONAL = re.compile(r"contact|phone|email", re.I)
# PR #427 (URL-lead pilot) evidences these records; leave them to it.
PILOT = {"ORG-001451", "ORG-001535", "ORG-001560", "ORG-001743", "ORG-001765", "ORG-001883", "ORG-001896",
         "ORG-001914", "ORG-002074", "ORG-002230", "ORG-002311", "ORG-002503", "ORG-002666"}
SUFFIX = re.compile(r"\b(incorporated|inc|llc|l l c|corporation|corp|company|co|ltd|limited|lp|llp|the)\b")


def norm(s):
    s = re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower().replace("&", " and "))
    return re.sub(r"\s+", " ", SUFFIX.sub(" ", s)).strip()


def names_of(org):
    raw = [org["legal_name"]] + [t for t in (org.get("trade_names") or "").split(";")]
    out = set()
    for n in raw:
        for part in re.split(r"\b(?:dba|d/b/a|d\.b\.a\.)\b", n, flags=re.I):
            for v in (part, re.sub(r"\(.*?\)|\(.*$", " ", part)):  # with and without parentheticals, closed or not
                if norm(v):
                    out.add(norm(v))
    return out


def facility_names(fac):
    """(field, normalized name) candidates; a trailing ' - <city>' or '/ <city>' plant label is also tried without it."""
    city = norm(fac.get("city_name"))
    out = []
    for field in ("facility_name", "standardized_parent_company", "parent_co_name"):
        v = (fac.get(field) or "").strip()
        if not v or v.upper() == "NA":
            continue
        out.append((field, norm(v)))
        stem = re.split(r"\s+-\s+|\s*/\s*", v)
        if len(stem) > 1 and norm(stem[-1]) in (city, norm(city + " plant")):
            out.append((field, norm(" ".join(stem[:-1]))))
    return out


def rd(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def wr(p, rows, fields):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def frame(repo, corpus):
    data = Path(repo) / "data"
    with_rows = {r["record_id"].strip() for f in data.glob("evidence_*.csv") for r in rd(f) if r["record_table"] == "organizations"}
    orgs = {}
    for f in sorted(data.glob("organizations_*.csv")):
        for r in rd(f):
            orgs[r["org_id"]] = dict(r, _shard=f.stem.split("_", 1)[1])
    links = {}
    for r in rd(data / "registry_links.csv"):
        if r["registry"] == "TRI_TRIFID":
            links.setdefault(r["org_id"].strip(), []).append(r)
    out = []
    for oid, o in sorted(orgs.items()):
        if oid in with_rows or oid in PILOT or oid not in links or o["status"] != "active":
            continue
        out.append({"org_id": oid, "legal_name": o["legal_name"], "trade_names": o.get("trade_names", ""),
                    "hq_city": o["hq_city"], "hq_state": o["hq_state"], "tier": o["verification_tier"], "shard": o["_shard"],
                    "trifids": ";".join(sorted({l["registry_id"] for l in links[oid]})),
                    "match_bases": ";".join(sorted({l["match_basis"] for l in links[oid]}))})
    assert len({r["org_id"] for r in out}) == len(out)
    Path(corpus).mkdir(parents=True, exist_ok=True)
    wr(HERE / "frame.csv", out, list(out[0]))
    from collections import Counter
    print(f"frame: {len(out)} active zero-evidence organizations with a TRI link; tiers {dict(Counter(r['tier'] for r in out))}")


def fetch(corpus):
    cache = Path(corpus) / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    ids = sorted({t for r in rd(HERE / "frame.csv") for t in r["trifids"].split(";")})
    log = []
    for tid in ids:
        f = cache / f"{tid}.json"
        if not f.exists():
            url = f"https://data.epa.gov/efservice/tri_facility/tri_facility_id/{tid}/JSON"
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-client/1.0"}), timeout=60) as r:
                    rows = [{k: v for k, v in row.items() if not PERSONAL.search(k)} for row in json.load(r)]
                f.write_text(json.dumps({"url": url, "fetched": time.strftime("%Y-%m-%d"), "rows": rows}, indent=1), encoding="utf-8")
                time.sleep(0.4)
            except Exception as e:  # a failed fetch is an availability signal, never a verdict
                log.append({"trifid": tid, "error": type(e).__name__}); continue
        log.append({"trifid": tid, "error": ""})
    wr(HERE / "fetch.csv", log, ["trifid", "error"])
    print(f"fetch: {sum(1 for l in log if not l['error'])} of {len(ids)} TRIFIDs cached")


def match(repo, corpus):
    cache = Path(corpus) / "cache"
    ledger, packet, bundle = [], [], []
    for o in rd(HERE / "frame.csv"):
        names = names_of(o)
        best = None
        for tid in o["trifids"].split(";"):
            f = cache / f"{tid}.json"
            rows = json.loads(f.read_text(encoding="utf-8"))["rows"] if f.exists() else None
            if not rows:
                cand = {"trifid": tid, "verdict": "NO_RECORD" if rows == [] else "FETCH_FAIL"}
            else:
                fac = rows[0]
                hits = [(fld, n) for fld, n in facility_names(fac) if n in names]
                near = max((len(set(n.split()) & set(m.split())) / len(set(n.split()) | set(m.split()))
                            for _, n in facility_names(fac) for m in names if n and m), default=0)
                verdict = ("CLOSED" if fac.get("fac_closed_ind") == "1" else
                           "WITNESS" if any(fld == "facility_name" for fld, _ in hits) else
                           "WITNESS_PARENT" if hits else "NEAR" if near >= 0.75 else "NO_MATCH")
                cand = {"trifid": tid, "verdict": verdict, "fac": fac, "field": hits[0][0] if hits else ""}
            rank = ["WITNESS", "WITNESS_PARENT", "CLOSED", "NEAR", "NO_MATCH", "NO_RECORD", "FETCH_FAIL"].index(cand["verdict"])
            if best is None or rank < best[0] or (rank == best[0] and cand.get("fac", {}).get("state_abbr") == o["hq_state"]):
                best = (rank, cand)
        c = best[1]
        fac = c.get("fac", {})
        where = f"{fac.get('street_address', '')}, {fac.get('city_name', '')}, {fac.get('state_abbr', '')}".strip(", ")
        ledger.append({"org_id": o["org_id"], "tier": o["tier"], "trifid": c["trifid"], "verdict": c["verdict"],
                       "facility_name": fac.get("facility_name", ""), "parent": fac.get("standardized_parent_company", ""),
                       "facility_address": where, "matched_field": c.get("field", "")})
        if c["verdict"] in ("WITNESS", "WITNESS_PARENT"):
            fname, parent = fac.get("facility_name", ""), fac.get("standardized_parent_company") or fac.get("parent_co_name", "")
            detail = (f"EPA TRI facility record TRIFID {c['trifid']} names facility '{fname}'"
                      + (f" with parent company '{parent}'" if parent and parent.upper() != "NA" else "")
                      + f" at {where}; matches the record's legal/trade name '{o['legal_name']}' on the "
                      + ("facility name" if c["verdict"] == "WITNESS" else "parent-company name"))
            packet.append({"record_table": "organizations", "record_id": o["org_id"], "claim_type": "existence",
                           "claim_detail": detail, "source_class": "government_filing",
                           "source_ref": f"EPA TRI facility record TRIFID {c['trifid']} (data.epa.gov efservice tri_facility)",
                           "observed_date": OBSERVED, "tier_effect": "supports_U" if o["tier"] == "U" else "supports_A",
                           "created_by": CREATED_BY,
                           "notes": (f"Fetched {OBSERVED} from data.epa.gov/efservice/tri_facility; registry_links match_basis "
                                     f"{o['match_bases']}; TRI contact fields not retained; record tier unchanged."),
                           "_shard": o["shard"]})
            bundle.append({"record_id": o["org_id"], "claim_type": "existence",
                           "atlas": {k: o[k] for k in ("legal_name", "trade_names", "hq_city", "hq_state", "tier")},
                           "tri": {k: fac.get(k, "") for k in ("tri_facility_id", "facility_name", "parent_co_name",
                                                               "standardized_parent_company", "street_address", "city_name",
                                                               "state_abbr", "fac_closed_ind")},
                           "proposed_claim_detail": detail})
    wr(HERE / "ledger.csv", ledger, list(ledger[0]))
    wr(HERE / "packet_rows.csv", packet, list(packet[0]))
    (Path(corpus) / "review_bundle.json").write_text(json.dumps(bundle, indent=1), encoding="utf-8")
    from collections import Counter
    print(f"match: {dict(Counter(l['verdict'] for l in ledger))}; packet {len(packet)} rows")


def plant(corpus):
    """Defect injection: score every framed organization against ANOTHER organization's TRI records (rotated by one).
    A matcher that admits coincidental names would witness some of these; the expected count is 0."""
    cache = Path(corpus) / "cache"
    fr = rd(HERE / "frame.csv")
    hits = []
    for i, o in enumerate(fr):
        other = fr[(i + 1) % len(fr)]
        for tid in other["trifids"].split(";"):
            f = cache / f"{tid}.json"
            rows = json.loads(f.read_text(encoding="utf-8"))["rows"] if f.exists() else []
            if rows and any(n in names_of(o) for _, n in facility_names(rows[0])):
                hits.append(f"{o['org_id']} <- {other['org_id']} {tid}")
    print(f"plant: {len(hits)} witnesses from {len(fr)} mismatched pairings (expect 0){': ' + '; '.join(hits) if hits else ''}")
    return len(hits)


def selftest():
    o = {"legal_name": "AAH Acquisition LLC dba Snap-Tite Hose", "trade_names": ""}
    assert "snap tite hose" in names_of(o) and "aah acquisition" in names_of(o)
    assert names_of({"legal_name": "DuPont (Circleville plant", "trade_names": ""}) == {"dupont", "dupont circleville plant"}
    fac = {"facility_name": "DANFOSS POWER SOLUTIONS - VAN WERT", "city_name": "VAN WERT",
           "standardized_parent_company": "NA", "parent_co_name": "NA"}
    assert ("facility_name", "danfoss power solutions") in facility_names(fac)
    assert norm("Fresh Products, Inc.") == norm("FRESH PRODUCTS LLC") == "fresh products"
    assert norm("Leggett & Platt") != norm("L & P Berwick Div Leggett & Platt")
    assert not PERSONAL.search("facility_name") and PERSONAL.search("asgn_public_contact_email")
    print("selftest ok")


if __name__ == "__main__":
    mode = sys.argv[1]
    {"frame": lambda: frame(sys.argv[2], sys.argv[3]), "fetch": lambda: fetch(sys.argv[2]),
     "match": lambda: match(sys.argv[2], sys.argv[3]), "plant": lambda: sys.exit(1 if plant(sys.argv[2]) else 0),
     "selftest": selftest}[mode]()
