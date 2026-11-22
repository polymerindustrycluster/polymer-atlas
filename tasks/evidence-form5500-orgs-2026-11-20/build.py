#!/usr/bin/env python3
"""Form 5500 lane: existence, HQ-address and liveness witnesses for active zero-evidence Atlas organizations from DOL
EBSA Form 5500 / 5500-SF filings (EFAST2 bulk 'Latest' datasets, plan years 2024 and 2025, fetched 2026-11-20).

    python3 tasks/evidence-form5500-orgs-2026-11-20/build.py match . <form5500 dir> <out dir>   # 2026-11-20 build (tree 01ef298e only)
    python3 tasks/evidence-form5500-orgs-2026-11-20/build.py cut . <form5500 dir>     # 2026-11-22 owner cut: packet, dropped, held, bundle
    python3 tasks/evidence-form5500-orgs-2026-11-20/build.py plant . <form5500 dir>   # defect injections: expect 0 and 0
    python3 tasks/evidence-form5500-orgs-2026-11-20/build.py selftest

A plan sponsor's filing is SCHEMA §4.13 `government_filing`, A-capable. An organization is witnessed by a sponsor whose
name (or DBA) equals the organization's legal or trade name under the house normalizer (atlas.py name_key; equality,
no containment) and either (a) carries an EIN the Atlas links to the organization, or (b) sits in the organization's
HQ city and state with exactly one sponsor EIN behind that name there. An EIN filing under another name, a name+city
hit spread over several EINs, or an EIN the 2026-11-01 spine (tasks/form5500-spine-2026-11-01) gave to another org is
held as a lead. One filing per organization is cited (latest plan-year end on or before the fetch date, preferring a
non-final filing with active participants, then most active participants, then ACK_ID). Rows:
  existence  the sponsor filing;
  address    the organization's HQ city/state, only when the sponsor's location or mailing city/state is the HQ's;
  liveness   owner ruling 2026-11-20 (ruling 8): the plan year ended within 24 months, active participants > 0, not a
             final filing (AGENTS.md §3: a final filing is a plan fact); observed_date is the plan-year end (§4.13).
Signer names, phones and care-of fields are never read. Rows cite the filing by form, plan-year end and ACK_ID (a named
source: V-66 does not apply). Stdlib only.
"""
import csv, hashlib, importlib.util, io, json, re, subprocess, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OBSERVED = "2026-11-20"
LIVE_FROM = "2024-11-20"  # 24 months before OBSERVED
CREATED_BY = "claude-code-evd-form5500-lane"
_s = importlib.util.spec_from_file_location("atlas_cli", ROOT / "scripts" / "atlas.py")
atlas = importlib.util.module_from_spec(_s); _s.loader.exec_module(atlas)
name_key = atlas.name_key
_s = importlib.util.spec_from_file_location("f5500_spine", ROOT / "scripts" / "build_form5500_spine.py")
spine = importlib.util.module_from_spec(_s); _s.loader.exec_module(spine)
TAX_PRD = {"5500": "FORM_TAX_PRD", "5500-SF": "SF_TAX_PRD"}
csv.field_size_limit(10**8)


def rd(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def wr(p, rows, fields):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def city_key(s):
    return atlas.squash(s).replace("saint ", "st ").replace("mount ", "mt ")


def frame(repo):
    data = Path(repo) / "data"
    ev = {r["record_id"].strip() for f in data.glob("evidence_*.csv") for r in rd(f) if r["record_table"] == "organizations"}
    orgs = {}
    for f in sorted(data.glob("organizations_*.csv")):
        for o in rd(f):
            if o["org_id"] in ev or o["status"] != "active":
                continue
            names = {name_key(o["legal_name"])} | {name_key(t) for t in (o["trade_names"] or "").split(";")}
            orgs[o["org_id"]] = dict(o, _shard=f.stem.split("_", 1)[1], _names={n for n in names if len(n) >= 4})
    eins = defaultdict(set)
    for r in rd(data / "registry_links.csv"):
        if r["registry"] == "EIN" and r["org_id"] in orgs:
            eins[r["org_id"]].add(re.sub(r"\D", "", r["registry_id"]))
    return orgs, eins


def filings(fdir, names, eins, acks=()):
    """Yield filings whose sponsor name/DBA key, EIN or ACK_ID is wanted (never reads signer/phone/care-of)."""
    sha = {}
    for z in sorted(Path(fdir).glob("F_5500_*_Latest.zip")):
        kind = "5500-SF" if "_SF_" in z.name else "5500"
        sp = spine.SPECS[kind]
        sha[z.name] = hashlib.sha256(z.read_bytes()).hexdigest()[:16]
        with zipfile.ZipFile(z) as zf:
            member = next(n for n in zf.namelist() if n.endswith(".csv"))
            rdr = csv.reader(io.TextIOWrapper(zf.open(member), encoding="utf-8", errors="replace", newline=""))
            head = next(rdr)
            ix = {c: i for i, c in enumerate(head)}
            cols = [sp[k] for k in ("ack", "ein", "name", "dba", "active", "final", "plan")] + [TAX_PRD[kind]] + list(sp["loc"]) + list(sp["mail"])
            assert all(c in ix for c in cols), (z.name, [c for c in cols if c not in ix])
            g = lambda row, c: row[ix[c]].strip() if ix[c] < len(row) else ""
            for row in rdr:
                if len(row) <= ix[sp["ein"]]:
                    continue
                ein = re.sub(r"\D", "", g(row, sp["ein"]))
                keys = {name_key(g(row, sp["name"])), name_key(g(row, sp["dba"]))}
                if not (keys & names or ein in eins or g(row, sp["ack"]) in acks):
                    continue
                yield dict(kind=kind, zip=z.name, sha=sha[z.name], ack=g(row, sp["ack"]), ein=ein, name=g(row, sp["name"]),
                           dba=g(row, sp["dba"]), keys=keys, active=spine.num(g(row, sp["active"])), final=g(row, sp["final"]),
                           plan_num=g(row, sp["plan"]), end=g(row, TAX_PRD[kind]),
                           loc=(g(row, sp["loc"][2]), g(row, sp["loc"][3]).upper()), mail=(g(row, sp["mail"][2]), g(row, sp["mail"][3]).upper()),
                           loc_street=g(row, sp["loc"][0]), mail_street=g(row, sp["mail"][0]))


def in_hq(f, o):
    """'location' or 'mailing' when the sponsor's address is in the HQ city/state; a location address, when given, governs."""
    hq = (city_key(o["hq_city"]), o["hq_state"].strip().upper())
    where, (c, s) = ("location", f["loc"]) if f["loc"][0] else ("mailing", f["mail"])
    return where if c and (city_key(c), s) == hq else None


def pick(fs):
    ok = [f for f in fs if re.fullmatch(r"\d{4}-\d{2}-\d{2}", f["end"]) and f["end"] <= OBSERVED]
    return max(ok, key=lambda f: (f["end"], f["final"] != "1" and (f["active"] or 0) > 0, f["active"] or 0, f["ack"]), default=None)


def classify(o, oeins, by_name, by_ein, spine_owner):
    ein_fs = [f for e in oeins for f in by_ein.get(e, [])]
    named_ein = [f for f in ein_fs if f["keys"] & o["_names"]]
    if named_ein:
        verdict, fs = "EIN+NAME", named_ein
    else:
        hits = [f for n in o["_names"] for f in by_name.get(n, []) if in_hq(f, o)]
        n_eins = {f["ein"] for f in hits}
        if len(n_eins) > 1:
            return "MULTI_EIN", hits
        if hits:
            verdict, fs = "NAME+CITY", hits
        elif ein_fs:
            return "EIN_NAME_DIFF", ein_fs
        else:
            st = [f for n in o["_names"] for f in by_name.get(n, []) if o["hq_state"].strip().upper() in (f["loc"][1], f["mail"][1])]
            return ("NAME_STATE_ONLY" if st else "NONE"), st
    # the 2026-11-01 spine, both ways: no EIN here belongs to another org, and if the spine gave this org EINs, one is here
    fs_eins = {f["ein"] for f in fs}
    if any(spine_owner.get(e, o["org_id"]) != o["org_id"] for e in fs_eins):
        return "SPINE_CONFLICT", fs
    mine = {e for e, oid in spine_owner.items() if oid == o["org_id"]}
    if mine and not mine & fs_eins:
        return "SPINE_OTHER_EIN", fs
    return verdict, fs


def load(repo, fdir):
    orgs, eins = frame(repo)
    names = {n for o in orgs.values() for n in o["_names"]}
    want_eins = {e for v in eins.values() for e in v}
    by_name, by_ein = defaultdict(list), defaultdict(list)
    for f in filings(fdir, names, want_eins):
        for k in f["keys"] & names:
            by_name[k].append(f)
        if f["ein"] in want_eins:
            by_ein[f["ein"]].append(f)
    spine_owner = {r["ein"]: r["org_id"] for r in rd(Path(repo) / "tasks/form5500-spine-2026-11-01/matches.csv")
                   if r["match_class"] in ("MATCH_ORG", "MATCH_SITE") and r["org_id"]}
    return orgs, eins, by_name, by_ein, spine_owner


def rows_for(o, verdict, f):
    eff = "supports_U" if o["verification_tier"] == "U" else "supports_A"
    form = "Form 5500-SF" if f["kind"] == "5500-SF" else "Form 5500"
    base = {"record_table": "organizations", "record_id": o["org_id"], "source_class": "government_filing",
            "source_ref": f"DOL EBSA {form}, plan year ending {f['end']}, ACK_ID {f['ack']} (EFAST2 dataset {f['zip']})",
            "observed_date": OBSERVED, "tier_effect": eff, "created_by": CREATED_BY, "_shard": o["_shard"]}
    note = (f"Read {OBSERVED} from the DOL EFAST2 bulk dataset {f['zip']} (askebsa.dol.gov, sha256 {f['sha']}…); "
            f"match {verdict}; organization tier unchanged.")
    sponsor = f"'{f['name']}'" + (f" (DBA '{f['dba']}')" if f["dba"] else "")
    trade = next((t.strip() for t in (o.get("trade_names") or "").split(";") if name_key(t) in f["keys"]), "")
    which = (f"legal name '{o['legal_name']}'" if name_key(o["legal_name"]) in f["keys"] or not trade
             else f"Atlas trade name '{trade}' (legal name '{o['legal_name']}')")
    out = [dict(base, claim_type="existence", notes=note, claim_detail=(
        f"DOL {form} for the plan year ending {f['end']} names plan sponsor {sponsor}, EIN {f['ein']}"
        + (", an EIN the Atlas links to this organization" if verdict == "EIN+NAME" else f", in {o['hq_city']}, {o['hq_state']}")
        + f"; the name matches the organization's {which}"))]
    where = in_hq(f, o)
    if where:
        out.append(dict(base, claim_type="address", notes=note, claim_detail=(
            f"HQ {o['hq_city']} {o['hq_state']}: the sponsor's {where} address in the {form} for the plan year ending "
            f"{f['end']} is in {(f['loc'] if where == 'location' else f['mail'])[0]}, {o['hq_state']}")))
    if f["end"] >= LIVE_FROM and (f["active"] or 0) > 0 and f["final"] != "1":
        out.append(dict(base, claim_type="liveness", observed_date=f["end"], notes=note + " Liveness under owner ruling "
                        "2026-11-20 (government filing; covered period ended within 24 months); observed_date is the plan-year end.",
                        claim_detail=f"operating in the plan year ending {f['end']}: the {form} reports {f['active']} active "
                                     f"participants at year end"))
    return out


def match(repo, fdir, out):
    """The 2026-11-20 build, valid only on the tree it ran on (01ef298e): the frame is the organizations with no evidence NOW,
    so a re-run after the cut finds 76, not 270. Output goes to `out`, never over this directory's record files."""
    out = Path(out)
    orgs, eins, by_name, by_ein, spine_owner = load(repo, fdir)
    ledger, packet, bundle = [], [], []
    for oid in sorted(orgs):
        o = orgs[oid]
        verdict, fs = classify(o, eins.get(oid, ()), by_name, by_ein, spine_owner)
        f = pick(fs) if fs else None
        witnessed = verdict in ("EIN+NAME", "NAME+CITY") and f is not None
        ledger.append({"org_id": oid, "tier": o["verification_tier"], "verdict": verdict if f or not fs else verdict + "_NO_DATED_FILING",
                       "legal_name": o["legal_name"], "hq_city": o["hq_city"], "hq_state": o["hq_state"],
                       "atlas_eins": ";".join(sorted(eins.get(oid, ()))), "filing_eins": ";".join(sorted({x["ein"] for x in fs})),
                       "sponsor": f["name"] if f else "", "dba": f["dba"] if f else "", "form": f["kind"] if f else "",
                       "plan_year_end": f["end"] if f else "", "active": f["active"] if f else "", "final": f["final"] if f else "",
                       "loc_city": f["loc"][0] if f else "", "loc_state": f["loc"][1] if f else "",
                       "mail_city": f["mail"][0] if f else "", "mail_state": f["mail"][1] if f else "",
                       "ack_id": f["ack"] if f else ""})
        if not witnessed:
            continue
        rows = rows_for(o, verdict, f)
        packet += rows
        bundle.append({"record_id": oid, "verdict": verdict,
                       "atlas": {k: o[k] for k in ("legal_name", "trade_names", "hq_city", "hq_state", "verification_tier", "website")}
                       | {"linked_eins": sorted(eins.get(oid, ()))},
                       "filing": {"form": f["kind"], "ack_id": f["ack"], "sponsor": f["name"], "dba": f["dba"], "ein": f["ein"],
                                  "plan_year_end": f["end"], "active_participants_eoy": f["active"], "final_filing": f["final"],
                                  "location_city_state": list(f["loc"]), "mailing_city_state": list(f["mail"])},
                       "other_eins_under_name": sorted({x["ein"] for x in fs} - {f["ein"]}),
                       "proposed": {r["claim_type"]: {"tier_effect": r["tier_effect"], "observed_date": r["observed_date"],
                                                      "claim_detail": r["claim_detail"]} for r in rows}})
    wr(out / "ledger.csv", ledger, list(ledger[0]))
    wr(out / "packet_rows.csv", packet, list(packet[0]))
    (out / "review_bundle.json").write_text(json.dumps(bundle, indent=1, ensure_ascii=False), encoding="utf-8")
    agree = sum(1 for b in bundle if spine_owner.get(b["filing"]["ein"]) == b["record_id"])
    print(f"spine (polymer-coded sponsors only) independently gives the cited EIN to the same org for {agree} of {len(bundle)}")
    print(f"frame {len(orgs)} active zero-evidence organizations ({sum(1 for v in eins.values() if v)} with an EIN link); "
          f"verdicts {dict(Counter(l['verdict'] for l in ledger))}; packet {len(packet)} rows on {len(bundle)} orgs "
          f"({dict(Counter(p['claim_type'] for p in packet))}); tiers {dict(Counter(b['atlas']['verification_tier'] for b in bundle))}")


HQ_TYPE = re.compile(r"hq|headquarters", re.I)
ORIGINAL = HERE / "packet_rows_2026-11-20.csv"
DROP_WHY = "organization evidenced since 2026-11-20"


def hq_streets(repo, orgs):
    """org_id -> {site_id: street} for ACTIVE sites whose site_type says HQ and whose city/state are the org's HQ city/state.
    Organization records carry no street field; an HQ site's street_address is the Atlas's recorded HQ street."""
    out = defaultdict(dict)
    for f in sorted((Path(repo) / "data").glob("sites_*.csv")):
        for s in rd(f):
            o = orgs.get(s["org_id"])
            if (o and s["operating_status"] == "active" and HQ_TYPE.search(s["site_type"]) and s["street_address"].strip()
                    and (city_key(s["city"]), s["state"].strip().upper()) == (city_key(o["hq_city"]), o["hq_state"].strip().upper())):
                out[s["org_id"]][s["site_id"]] = s["street_address"].strip()
    return out


PERSONAL = re.compile(r"@|c/o|\battn\b|\bcare of\b|^\s*%", re.I)


def clean_street(s):
    """A filing street line safe to publish: '' when it carries a possible person (c/o, attn, care of, a leading %, '@') or has
    no digit (a name, not a street). A business street is a public fact; a person in an address line is not (AGENTS §6)."""
    return "" if not s or PERSONAL.search(s) or not re.search(r"\d", s) else s.strip()


def gap_class(o, all_sites):
    """Why an organization has no usable HQ street (the NO_HQ_STREET breakdown)."""
    hq = (city_key(o["hq_city"]), o["hq_state"].strip().upper())
    here = lambda s: (city_key(s["city"]), s["state"].strip().upper()) == hq
    if not all_sites:
        return "NO_SITE_RECORD"
    if any(HQ_TYPE.search(s["site_type"]) and here(s) and s["operating_status"] == "active" for s in all_sites):
        return "HQ_SITE_WITHOUT_STREET"
    if any(HQ_TYPE.search(s["site_type"]) for s in all_sites):
        return "HQ_SITE_NOT_ACTIVE_OR_OUTSIDE_HQ_CITY"
    if any(here(s) and s["operating_status"] == "active" and s["street_address"].strip() for s in all_sites):
        return "ONLY_NON_HQ_SITE_IN_HQ_CITY"
    return "SITES_ELSEWHERE_ONLY"


def street_test(f, where, sites):
    """('SAME'|'DIFFERENT'|'NO_HQ_STREET'|'NO_FILING_STREET'|'PO_BOX_OR_NO_NUMBER', settling fact). The filing's street (location if it
    governs, else mailing) must equal, under atlas.street_key, the street of an Atlas HQ site in the HQ city."""
    street = f["loc_street"] if where == "location" else f["mail_street"]
    if not street or PERSONAL.search(street):
        return "NO_FILING_STREET", "the filing's street line is empty or carries a care-of/attention/e-mail marker (not quoted)"
    if spine.pobox(street):
        return "PO_BOX_OR_NO_NUMBER", "the filing's street line is a post-office box or has no street number (not quoted)"
    if not sites:
        return "NO_HQ_STREET", f"the Atlas holds no active HQ site with a street in the HQ city; the filing says '{street}'"
    for sid, st in sorted(sites.items()):
        if atlas.street_key(st) == atlas.street_key(street):
            return "SAME", f"{sid}: '{st}'"
    return "DIFFERENT", f"filing street '{street}' vs Atlas HQ site street " + "; ".join(f"{sid} '{st}'" for sid, st in sorted(sites.items()))


def cut(repo, fdir):
    """2026-11-22 owner cut ('Cut to what's new'): keep every row on an organization that still has no evidence row in
    data/evidence_organizations_*.csv, plus every liveness row; drop the other organizations' existence/address rows;
    hold a kept address row unless the filing's street equals an Atlas HQ site street."""
    repo = Path(repo)
    orig = rd(ORIGINAL)
    led = {l["org_id"]: l for l in rd(HERE / "ledger.csv")}
    orgs = {o["org_id"]: o for f in sorted((repo / "data").glob("organizations_*.csv")) for o in rd(f)}
    evidenced = {r["record_id"].strip() for f in (repo / "data").glob("evidence_*.csv") for r in rd(f)  # any table, any record_table
                 if r["created_by"] != CREATED_BY}
    lane = sorted({r["record_id"] for r in orig})
    zero = {o for o in lane if o not in evidenced and orgs.get(o, {}).get("status") == "active"}
    sites = hq_streets(repo, {o: orgs[o] for o in lane})
    acks = {led[o]["ack_id"] for o in lane}
    fil = {f["ack"]: f for f in filings(fdir, set(), set(), acks)}
    by_ack = defaultdict(set)
    for o in lane:
        by_ack[led[o]["ack_id"]].add(o)
    shared = {o: sorted(by_ack[led[o]["ack_id"]] - {o}) for o in lane if len(by_ack[led[o]["ack_id"]]) > 1}
    all_sites = defaultdict(list)
    for f_ in sorted((repo / "data").glob("sites_*.csv")):
        for s in rd(f_):
            if s["org_id"] in orgs and s["org_id"] in set(lane):
                all_sites[s["org_id"]].append(s)
    kept, dropped, held, bundle = [], [], [], []
    stats, gaps, street_all = Counter(), Counter(), {}
    for r in orig:
        o, l = r["record_id"], led[r["record_id"]]
        f = fil.get(l["ack_id"])
        same = f and (f["ein"], f["name"], f["end"], "" if f["active"] is None else str(f["active"]), f["final"]) == (
            l["filing_eins"], l["sponsor"], l["plan_year_end"], str(l["active"]), l["final"])
        if r["claim_type"] != "liveness" and o not in zero:
            dropped.append(dict(r, reason=DROP_WHY if o in evidenced else "organization no longer active")); continue
        if orgs.get(o, {}).get("status") != "active":  # a liveness row never goes onto an organization the Atlas no longer calls active
            held.append(dict(r, reason=f"organization status is now '{orgs.get(o, {}).get('status')}'; a filing never changes a status (AGENTS 3)")); continue
        if o in shared and name_key(orgs[o]["legal_name"]) not in f["keys"]:  # one filing cannot witness two organizations
            held.append(dict(r, reason=f"SHARED_FILING: ACK_ID {l['ack_id']} is also cited for {', '.join(shared[o])}, whose legal name "
                                       f"equals the sponsor; this organization matches only through an Atlas trade name. Settling fact: "
                                       f"whether the sponsor is a trade name of this legal entity or a different one (an acquirer or affiliate)")); continue
        if not same:
            held.append(dict(r, reason=f"the filing ACK_ID {l['ack_id']} is absent or changed in the 2026-11-22 EFAST2 files; "
                                       "re-run the match before review")); continue
        if r["claim_type"] == "address":
            where = in_hq(f, orgs[o])
            verdict, fact = street_test(f, where, sites.get(o, {}))
            stats[verdict] += 1
            if verdict == "NO_HQ_STREET":
                gaps[gap_class(orgs[o], all_sites.get(o, []))] += 1
            if verdict != "SAME":
                held.append(dict(r, reason=f"{verdict}: {fact}")); continue
            r = dict(r, address_role="physical" if where == "location" else "mailing",  # SCHEMA §4.13 v1.19
                     claim_detail=r["claim_detail"] + f"; the street matches the Atlas HQ site {fact}"
                     f" (filing street '{clean_street(f['loc_street'] if where == 'location' else f['mail_street'])}')")
        kept.append(r)
    assert len(kept) + len(dropped) + len(held) == len(orig), (len(kept), len(dropped), len(held), len(orig))
    flds = list(orig[0])
    wr(HERE / "packet_rows.csv", kept, flds + ["address_role"])
    wr(HERE / "dropped_rows.csv", dropped, flds + ["reason"])
    wr(HERE / "held_rows.csv", held, flds + ["reason"])
    kept_orgs = {r["record_id"] for r in kept}
    old = {b["record_id"]: b for b in json.loads((HERE / "review_bundle_2026-11-20.json").read_text(encoding="utf-8"))}
    for oid in sorted(kept_orgs):
        b, f = old[oid], fil[led[oid]["ack_id"]]
        mine = {r["claim_type"]: r for r in kept if r["record_id"] == oid}
        where = in_hq(f, orgs[oid])
        sv, sfact = street_test(f, where, sites.get(oid, {})) if where else ("NOT_IN_HQ_CITY", "the sponsor's address is not in the HQ city")
        street_all[oid] = sv
        bundle.append(dict(b, filing=dict(b["filing"], location_street=clean_street(f["loc_street"]), mailing_street=clean_street(f["mail_street"])),
                           street_check=dict(verdict=sv, fact=sfact if sv in ("SAME", "DIFFERENT") else "", note="informational for liveness; gates address only"),
                           atlas_hq_site_streets=sites.get(oid, {}), evidence_status="none" if oid in zero else "evidenced elsewhere; liveness row only",
                           proposed={k: {"tier_effect": v["tier_effect"], "observed_date": v["observed_date"], "claim_detail": v["claim_detail"]}
                                     for k, v in mine.items()}))
    (HERE / "review_bundle.json").write_text(json.dumps(bundle, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"commit {subprocess.run(['git', '-C', str(repo), 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()}: "
          f"{len(lane)} lane organizations, {len(zero)} with no evidence row in data/evidence_organizations_*.csv "
          f"(excluding this lane's own); original packet {len(orig)} rows -> kept {len(kept)} {dict(Counter(r['claim_type'] for r in kept))}, "
          f"dropped {len(dropped)} {dict(Counter(r['claim_type'] for r in dropped))}, held {len(held)} "
          f"{dict(Counter(h['reason'].split(':')[0] for h in held))}; address street test on zero-evidence orgs {dict(stats)}; "
          f"kept rows on {len(kept_orgs)} orgs; filings found {len(fil)} of {len(acks)} for {len(lane)} orgs, shared ACK_IDs {shared}; "
          f"NO_HQ_STREET breakdown {dict(gaps)}; street test over all {len(street_all)} kept orgs {dict(Counter(street_all.values()))}")


def plant(repo, fdir):
    """(1) score each witnessed org's names against ANOTHER org's HQ city/state (rotated); (2) give each EIN-linked org
    the next EIN-linked org's EINs. Expect 0 witnesses from each."""
    orgs, eins, by_name, by_ein, spine_owner = load(repo, fdir)
    ids = [oid for oid in sorted(orgs) if classify(orgs[oid], eins.get(oid, ()), by_name, by_ein, spine_owner)[0] in ("EIN+NAME", "NAME+CITY")]
    wrong = 0
    for i, oid in enumerate(ids):
        o, other = orgs[oid], orgs[ids[(i + 1) % len(ids)]]
        if (city_key(o["hq_city"]), o["hq_state"]) == (city_key(other["hq_city"]), other["hq_state"]) or o["_names"] & other["_names"]:
            continue
        wrong += classify(dict(o, hq_city=other["hq_city"], hq_state=other["hq_state"]), (), by_name, by_ein, spine_owner)[0] == "NAME+CITY"
    linked = [oid for oid in sorted(orgs) if eins.get(oid)]
    swapped = 0
    for i, oid in enumerate(linked):
        other = linked[(i + 1) % len(linked)]
        if orgs[oid]["_names"] & orgs[other]["_names"]:
            continue
        swapped += classify(dict(orgs[oid], hq_city="", hq_state=""), eins[other], by_name, by_ein, {})[0] == "EIN+NAME"
    print(f"plant: {wrong} witnesses from {len(ids)} rotated HQs (expect 0); {swapped} from {len(linked)} swapped EIN sets (expect 0)")
    return wrong + swapped


def selftest():
    o = {"org_id": "ORG-1", "hq_city": "Akron", "hq_state": "OH", "_names": {name_key("Acme Polymers, Inc.")}}
    f = lambda **k: dict(dict(kind="5500", zip="z", sha="s", ack="A1", ein="111111111", name="ACME POLYMERS INC", dba="",
                              keys={name_key("ACME POLYMERS INC")}, active=10, final="", plan_num="001", end="2025-12-31",
                              loc=("", ""), mail=("AKRON", "OH")), **k)
    assert name_key("Acme Polymers, Inc.") == name_key("ACME POLYMERS INC")
    assert in_hq(f(), o) == "mailing" and not in_hq(f(loc=("Canton", "OH")), o) and not in_hq(f(mail=("CANTON", "OH")), o)
    assert in_hq(f(loc=("AKRON", "OH"), mail=("CLEVELAND", "OH")), o) == "location"
    assert pick([f(end="2025-12-31", ack="A"), f(end="2026-12-31", ack="B")])["ack"] == "A"  # future period ends are ignored
    assert pick([f(end="2025-12-31", final="1", ack="A"), f(end="2025-12-31", ack="B")])["ack"] == "B"  # non-final preferred
    by_name = {name_key("ACME POLYMERS INC"): [f(), f(ein="222222222", ack="A2")]}
    assert classify(o, (), by_name, {}, {})[0] == "MULTI_EIN"
    assert classify(o, (), {name_key("ACME POLYMERS INC"): [f()]}, {}, {})[0] == "NAME+CITY"
    assert classify(o, (), {name_key("ACME POLYMERS INC"): [f()]}, {}, {"111111111": "ORG-2"})[0] == "SPINE_CONFLICT"
    assert classify(o, (), {name_key("ACME POLYMERS INC"): [f()]}, {}, {"999999999": "ORG-1"})[0] == "SPINE_OTHER_EIN"
    assert classify(o, (), {name_key("ACME POLYMERS INC"): [f()]}, {}, {"111111111": "ORG-1"})[0] == "NAME+CITY"
    assert classify(o, ("333333333",), {}, {"333333333": [f(ein="333333333", name="OTHER CO", keys={"other"})]}, {})[0] == "EIN_NAME_DIFF"
    oo = dict(o, org_id="ORG-1", legal_name="Acme Polymers, Inc.", verification_tier="B", _shard="OH")
    kinds = lambda **k: [r["claim_type"] for r in rows_for(oo, "NAME+CITY", f(**k))]
    assert kinds() == ["existence", "address", "liveness"] and kinds(final="1") == ["existence", "address"]
    assert kinds(end="2024-06-30") == ["existence", "address"] and kinds(active=0) == ["existence", "address"]
    assert [r["observed_date"] for r in rows_for(oo, "NAME+CITY", f())] == [OBSERVED, OBSERVED, "2025-12-31"]
    print("selftest ok")


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "match":
        match(sys.argv[2], sys.argv[3], sys.argv[4])
    elif m == "cut":
        cut(sys.argv[2], sys.argv[3])
    elif m == "plant":
        sys.exit(1 if plant(sys.argv[2], sys.argv[3]) else 0)
    else:
        selftest()
