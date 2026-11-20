#!/usr/bin/env python3
"""FRS lane: existence (and, for tier-C/U sites, address) witnesses for active zero-evidence B/C/U Atlas sites that hold
an FRS registry link, read from EPA's own FRS state combined files (state_single_<st>.zip, fetched 2026-11-20).

    python3 tasks/evidence-frs-sites-2026-11-20/build.py match . <frs-state dir>   # frame, ledger, packet, bundle
    python3 tasks/evidence-frs-sites-2026-11-20/build.py plant . <frs-state dir>   # defect injections: expect 0 and 0
    python3 tasks/evidence-frs-sites-2026-11-20/build.py selftest

FRS is SCHEMA §4.13 `registry`: existence caps at supports_B and an address at supports_C (V-22), so tier-B sites get an
existence row only (a C-strength address row on a tier-B site is a V-25 error) and tier-U sites get supports_U. Every
link is re-verified in EPA's extract (AGENTS.md §4 phantom rule). A site is witnessed when its FRS record is in the
site's state and city (ZIP when FRS's city field is not a name) and carries the operator's or site's name, and either
sits at the site's street (number, street word, and no conflicting street type: the reviewers rejected Road vs Drive and
Street vs Avenue in the OSHA lane) or the Atlas holds no street (existence only). Anything else is held as a
record-health lead. Rows cite the registry record by name (V-66 does not apply) with a dated fetch marker (V-23).
"""
import csv, hashlib, importlib.util, io, json, re, sys, zipfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("osha_build", HERE.parent / "evidence-osha-sites-2026-11-20" / "build.py")
osha = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(osha)
norm, street_key, rd, wr = osha.norm, osha.street_key, osha.rd, osha.wr
OBSERVED = "2026-11-20"
CREATED_BY = "claude-code-evd-frs-lane"
TYPES = {"rd": "road", "road": "road", "dr": "drive", "drive": "drive", "st": "street", "street": "street",
         "ave": "avenue", "av": "avenue", "avenue": "avenue", "blvd": "boulevard", "boulevard": "boulevard",
         "pkwy": "parkway", "parkway": "parkway", "ln": "lane", "lane": "lane", "ct": "court", "court": "court",
         "hwy": "highway", "highway": "highway", "pl": "place", "place": "place", "cir": "circle", "circle": "circle",
         "trl": "trail", "trail": "trail", "tpke": "turnpike", "turnpike": "turnpike", "pike": "pike", "way": "way"}
TYPE_SET = set(TYPES.values())
CITY = {"mt": "mount", "ft": "fort", "st": "saint", "twp": "township"}
ABBR = {"mfg": "manufacturing", "chem": "chemical", "eng": "engineering", "prod": "products", "intl": "international"}
csv.field_size_limit(10**8)


def canon(s, table=TYPES):
    return " ".join(table.get(t, t) for t in norm(s).split())


def skey(s):
    """(street number, first street word), number may carry a unit letter: '474C Pike Rd' -> ('474c', 'pike')."""
    toks = canon(s).split()
    if not toks or not re.fullmatch(r"\d+[a-z]?", toks[0]):
        return None
    word = next((t for t in toks[1:] if t not in osha.DIR and not t.isdigit()), None)
    return (toks[0], word) if word else None


def street_type(s):
    """Canonical street type after the street word ('150 Columbia St' -> 'street'); None when absent."""
    toks, k = canon(s).split(), skey(s)
    if not k:
        return None
    return next((t for t in toks[toks.index(k[1]) + 1:] if t in TYPE_SET), None)


def same_street(a, b):
    if canon(a) and canon(a) == canon(b):
        return True
    ka, kb, ta, tb = skey(a), skey(b), street_type(a), street_type(b)
    return bool(ka) and ka == kb and not (ta and tb and ta != tb)


def city(s):
    return re.sub(r" (city of|township|village)$", "", canon(s, CITY))


def same_city(s, f):
    z = s["zip"][:5]
    if z and z == (f["POSTAL_CODE"] or "")[:5]:
        return True
    # FRS's city field is sometimes a code ("122182"); without a ZIP agreement that is no match
    return bool(re.search(r"[a-z]", (f["CITY_NAME"] or "").lower())) and city(s["city"]) == city(f["CITY_NAME"])


def named(names, f):
    """('exact'|'contains', the Atlas name that matched) or None."""
    est = canon(f["PRIMARY_NAME"], ABBR)
    if not est or est == city(f["CITY_NAME"]):
        return None
    for a in sorted(names, key=lambda a: canon(a, ABBR) != est):
        a2 = canon(a, ABBR)
        if len(min(a2, est, key=len)) >= 4 and (a2 == est or a2 in est or est in a2):
            return ("exact" if a2 == est else "contains", a)
    return None


def verdict(s, f):
    if f is None:
        return "ID_MISSING"
    if f["STATE_CODE"].strip().upper() != s["state"].strip().upper() or not same_city(s, f):
        return "CITY_DIFF"
    if s["street_address"].strip() and not same_street(s["street_address"], f["LOCATION_ADDRESS"]):
        return "STREET_DIFF"
    if not named(s["_names"], f):
        return "NAME_DIFF"
    return "ADDR+NAME" if s["street_address"].strip() else "CITY+NAME"


RANK = {"ADDR+NAME": 0, "CITY+NAME": 1, "NAME_DIFF": 2, "STREET_DIFF": 3, "CITY_DIFF": 4, "ID_MISSING": 5}


def load(repo, state_dir):
    data = Path(repo) / "data"
    ev = {r["record_id"].strip() for f in data.glob("evidence_*.csv") for r in rd(f) if r["record_table"] == "sites"}
    ops = {r["org_id"]: r for f in data.glob("organizations_*.csv") for r in rd(f)}
    ops.update({r["org_id"]: r for r in rd(data / "ecosystem.csv")})
    sites = {}
    for f in sorted(data.glob("sites_*.csv")):
        for s in rd(f):
            if s["site_id"] in ev or s["operating_status"] != "active" or s["verification_tier"] not in ("B", "C", "U"):
                continue
            op = ops.get(s["org_id"], {})
            sites[s["site_id"]] = dict(s, _shard=f.stem.split("_", 1)[1], _op=op.get("legal_name", ""),
                                       _names=sorted({x for x in [norm(op.get("legal_name")), norm(s["site_name"])] +
                                                      [norm(t) for t in (op.get("trade_names") or "").split(";")] if x}))
    links = [r for r in rd(data / "registry_links.csv") if r["registry"] == "FRS" and r.get("site_id", "").strip() in sites]
    need, frs, sha = {r["registry_id"] for r in links}, {}, {}
    for z in sorted(Path(state_dir).glob("state_single_*.zip")):
        st = z.stem.split("_")[-1].upper()
        sha[st] = hashlib.sha256(z.read_bytes()).hexdigest()[:16]
        with zipfile.ZipFile(z) as zf:
            name = next(n for n in zf.namelist() if n.upper().endswith(".CSV"))
            for r in csv.DictReader(io.TextIOWrapper(zf.open(name), encoding="latin-1", newline="")):
                if r["REGISTRY_ID"] in need:
                    frs[r["REGISTRY_ID"]] = dict(r, _file=name, _zip=z.name, _sha=sha[st])
    return sites, links, frs


def match(repo, state_dir):
    sites, links, frs = load(repo, state_dir)
    by_site = {}
    for l in links:
        s, f = sites[l["site_id"]], frs.get(l["registry_id"])
        v = verdict(s, f)
        if l["site_id"] not in by_site or RANK[v] < RANK[by_site[l["site_id"]][0]]:
            by_site[l["site_id"]] = (v, l, f)
    ledger, packet, bundle = [], [], []
    for sid in sorted(by_site):
        v, l, f = by_site[sid]
        s = sites[sid]
        ledger.append({"site_id": sid, "tier": s["verification_tier"], "verdict": v, "operator": s["_op"], "site_name": s["site_name"],
                       "atlas_street": s["street_address"], "city": s["city"], "state": s["state"], "frs_registry_id": l["registry_id"],
                       "link_basis": l["match_basis"].split(":")[0], "frs_name": f["PRIMARY_NAME"] if f else "",
                       "frs_street": f["LOCATION_ADDRESS"] if f else "", "frs_city": f["CITY_NAME"] if f else "",
                       "name_match": ":".join(named(s["_names"], f) or ()) if f else ""})
        if v not in ("ADDR+NAME", "CITY+NAME"):
            continue
        tier, nm = s["verification_tier"], named(s["_names"], f)
        which = (f"site name '{s['site_name']}' (operator '{s['_op']}')" if nm[1] == norm(s["site_name"]) else
                 f"operator '{s['_op']}'" if nm[1] == norm(s["_op"]) else f"operator trade name '{nm[1]}' (operator '{s['_op']}')")
        where = f"{f['LOCATION_ADDRESS']}, {f['CITY_NAME']}, {f['STATE_CODE']} {f['POSTAL_CODE']}".strip()
        progs = ", ".join((f["PGM_SYS_ACRNMS"] or "").split(",")[:4]).strip()
        base = {"record_table": "sites", "record_id": sid, "source_class": "registry", "observed_date": OBSERVED,
                "source_ref": f"EPA FRS registry ID {l['registry_id']} (EPA FRS state combined file {f['_file']})",
                "created_by": CREATED_BY, "_shard": s["_shard"]}
        note = (f"Registry record fetched {OBSERVED} in EPA's FRS state combined file {f['_zip']} (ordsext.epa.gov, sha256 "
                f"{f['_sha']}…); the FRS link ({l['match_basis'].split(':')[0]}) re-verified in that extract; site tier unchanged.")
        rows = [dict(base, claim_type="existence", tier_effect="supports_U" if tier == "U" else "supports_B", notes=note,
                     claim_detail=(f"EPA FRS registry {l['registry_id']} lists '{f['PRIMARY_NAME']}' at {where} (FRS record created "
                                   f"{f['CREATE_DATE']}, updated {f['UPDATE_DATE']}; programs {progs or 'none listed'}); the name "
                                   f"matches the Atlas {which} " + ("at its recorded street" if v == "ADDR+NAME" else
                                   "in its recorded city (the Atlas holds no street for this site)")))]
        if v == "ADDR+NAME" and tier in ("C", "U"):
            rows.append(dict(base, claim_type="address", tier_effect="supports_U" if tier == "U" else "supports_C",
                             notes=note + " A registry address alone caps at supports_C (V-22); county not used.",
                             claim_detail=f"street_address {s['street_address']}, {s['city']}, {s['state']}: EPA FRS registry "
                                          f"{l['registry_id']} gives {where}"))
        packet += rows
        bundle.append({"record_id": sid, "verdict": v, "name_match": list(nm), "frs_link_basis": l["match_basis"].split(":")[0],
                       "atlas": {"site_name": s["site_name"], "operator": s["_op"], "street": s["street_address"], "city": s["city"],
                                 "state": s["state"], "zip": s["zip"], "tier": tier},
                       "frs": {k: f[k] for k in ("REGISTRY_ID", "PRIMARY_NAME", "LOCATION_ADDRESS", "CITY_NAME", "COUNTY_NAME",
                                                 "STATE_CODE", "POSTAL_CODE", "CREATE_DATE", "UPDATE_DATE", "PGM_SYS_ACRNMS",
                                                 "NAICS_CODES", "SIC_CODES", "SITE_TYPE_NAME")},
                       "proposed": {r["claim_type"]: {"tier_effect": r["tier_effect"], "claim_detail": r["claim_detail"]} for r in rows}})
    wr(HERE / "ledger.csv", ledger, list(ledger[0]))
    wr(HERE / "packet_rows.csv", packet, list(packet[0]))
    (HERE / "review_bundle.json").write_text(json.dumps(bundle, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"frame {len(sites)} active zero-evidence B/C/U sites; {len(links)} FRS links on {len(by_site)} sites, "
          f"{sum(1 for l in links if l['registry_id'] in frs)} found in EPA's extract; verdicts {dict(Counter(x['verdict'] for x in ledger))}; "
          f"packet {len(packet)} rows on {len(bundle)} sites ({dict(Counter(p['claim_type'] for p in packet))}); "
          f"tiers {dict(Counter(b['atlas']['tier'] for b in bundle))}")


def plant(repo, state_dir):
    """(1) score each site against ANOTHER site's FRS record (rotated by one, different operator, different city);
    (2) flip the street type of each street-matched site where both addresses carry one. Expect 0 witnesses from each."""
    sites, links, frs = load(repo, state_dir)
    pairs = [(sites[l["site_id"]], frs[l["registry_id"]]) for l in links if l["registry_id"] in frs]
    wrong = 0
    for i, (s, _) in enumerate(pairs):
        o, f = pairs[(i + 1) % len(pairs)]
        if o["org_id"] != s["org_id"] and norm(o["city"]) != norm(s["city"]) and verdict(s, f) in ("ADDR+NAME", "CITY+NAME"):
            wrong += 1
    flip = {"road": "Drive", "drive": "Road", "street": "Avenue", "avenue": "Street"}
    tried = flipped = 0
    for s, f in pairs:
        t = street_type(s["street_address"])
        if verdict(s, f) == "ADDR+NAME" and t in flip and street_type(f["LOCATION_ADDRESS"]):
            k = skey(s["street_address"])
            tried += 1
            flipped += verdict(dict(s, street_address=f"{k[0]} {k[1]} {flip[t]}"), f) == "ADDR+NAME"
    print(f"plant: {wrong} witnesses from {len(pairs)} rotated pairings (expect 0); {flipped} of {tried} street-type flips "
          f"still witnessed (expect 0)")
    return wrong + flipped


def selftest():
    assert street_type("150 Columbia Street") == "street" and street_type("150 Columbia Ave") == "avenue"
    assert not same_street("150 Columbia Street", "150 Columbia Avenue") and same_street("173 Industrial Pkwy", "173 INDUSTRIAL PARKWAY")
    assert same_street("100 Parkway Dr", "100 Parkway Drive") and street_type("100 Parkway") is None
    assert same_street("500 S Spencer Rd", "500 Spencer") and not same_street("12 Main St", "14 Main St")
    assert same_city({"city": "Akron", "zip": "44314"}, {"CITY_NAME": "AKRON", "POSTAL_CODE": "44314-1234"})
    assert same_city({"city": "Cleveland", "zip": "44110"}, {"CITY_NAME": "122182", "POSTAL_CODE": "44110"})
    assert not same_city({"city": "Cleveland", "zip": "44111"}, {"CITY_NAME": "122182", "POSTAL_CODE": "44110"})
    assert same_city({"city": "Mount Gilead", "zip": ""}, {"CITY_NAME": "MT GILEAD", "POSTAL_CODE": "43338"})
    assert same_city({"city": "Erie", "zip": ""}, {"CITY_NAME": "ERIE, CITY OF", "POSTAL_CODE": "16502"})
    assert same_street("474C Pike Rd.", "474C PIKE ROAD") and same_street("N Thomas Ave.", "N. THOMAS AVE.")
    assert same_street("7004 US Hwy 42", "7004 US-42") and not same_street("474C Pike Rd", "474B Pike Rd")
    assert named(["seaway manufacturing"], {"PRIMARY_NAME": "SEAWAY MFG CORP/ERIE", "CITY_NAME": "ERIE"}) == ("contains", "seaway manufacturing")
    assert named(["genpak"], {"PRIMARY_NAME": "GENPAK LLC", "CITY_NAME": "X"}) == ("exact", "genpak")
    assert named(["alro plastics"], {"PRIMARY_NAME": "ALRO STEEL CORP", "CITY_NAME": "X"}) is None
    assert named(["abc"], {"PRIMARY_NAME": "ABC HOLDINGS", "CITY_NAME": "X"}) is None
    assert named(["leola"], {"PRIMARY_NAME": "LEOLA", "CITY_NAME": "LEOLA"}) is None
    print("selftest ok")


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "match":
        match(sys.argv[2], sys.argv[3])
    elif m == "plant":
        sys.exit(1 if plant(sys.argv[2], sys.argv[3]) else 0)
    else:
        selftest()
