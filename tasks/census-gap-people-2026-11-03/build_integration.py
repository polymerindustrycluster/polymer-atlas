#!/usr/bin/env python3
"""Integrate the census-gap researcher lanes (lanes/L*/) into data rows.

    python3 tasks/census-gap-people-2026-11-03/build_integration.py --data-dir data \
        --hd HD2024.csv --ipeds-ror <polymer-programs-db>/incoming/ipeds_ror.tsv --ror-cache <dir> [--apply --i-am-the-integrator]

Without --apply it writes the integration packet (this folder): people_rows.csv,
institution_rows.csv, evidence_append.csv, holds.csv and prints counts. With
--apply it appends those rows to the data files (byte-preserving appends).

Admission rules (SCHEMA 4.9 and 1, AGENTS.md 3 and 6)
  * person: lane verdict VERIFIED; role in the university professor vocabulary
    (Gate A rank line, v1.7.5); Gate A and Gate B URLs and the profile URL all on
    the university's own domain; quotes present; no '@' in any URL; not already
    held (normalized name already in people.csv -> held as a possible duplicate).
  * institution: an already-held record is reused (UConn). A new university
    record is created only for a school with >= 2 admitted people (the faculty-
    cluster reading of the Ring 5 inclusion rule; the TAMU pass-37 anchor
    precedent): identity from IPEDS HD2024, ROR only when the crosswalk lead
    verifies at api.ror.org, polymer_program=false (no program rows are built in
    this pass; a named polymer unit is recorded in notes as a program lead).
  * IDs: ORG ids above the tree-wide max over organizations_*.csv + ecosystem.csv,
    PERSON ids above the people.csv max, EVD ids above the max over every evidence shard;
    gaps are never filled.
"""
import argparse, csv, glob, io, json, re, sys, urllib.request
from pathlib import Path

csv.field_size_limit(10 ** 9)
HERE = Path(__file__).resolve().parent
TODAY = "2026-11-03"
BY = "claude-code census-gap-wave-2026-11-03"
ROLES = {"professor", "associate_professor", "assistant_professor", "research_professor", "center_director_professor"}
SCHOOLS = {  # school_key -> IPEDS UNITID (HD2024 exact name match)
    "stanford": "243744", "ucberkeley": "110635", "ucla": "110662", "ucsd": "110680", "usc": "123961",
    "utah": "230764", "uw": "236948", "rice": "227757", "utk": "221759", "jhu": "162928", "umd": "163286",
    "duke": "198419", "columbia": "190150", "nyu": "193900", "yale": "130794", "northeastern": "167358",
    "uconn": "129020",
}
# Connecticut: IPEDS now reports planning regions; Atlas CT rows use the legacy county (New Haven, Hartford, ...).
COUNTY_OVERRIDE = {"yale": "New Haven"}
# Integrator review of every VERIFIED Gate B quote (2026-11-03): held, with the deciding fact.
INTEGRATOR_HOLDS = {
    ("usc", "steven nutt"): "Gate B quote is the Gill Composites Center's page, not person-level; his own profile says only 'composites'",
    ("utah", "mingnan chen"): "Gate B quote is a department research-area listing, not person-level",
    ("utah", "jules magda"): "Gate B quote is the department strengths page; needs his own profile or lab page",
    ("rice", "jeffrey hartgerink"): "Gate B quote ('peptide nanofibers, and hydrogels') names no polymer object",
}
DOMAINS = {"uw": ["washington.edu", "uw.edu"], "ucsd": ["ucsd.edu"], "umd": ["umd.edu"], "jhu": ["jhu.edu", "jhmi.edu"],
           "uconn": ["uconn.edu"], "utk": ["utk.edu", "tennessee.edu"], "usc": ["usc.edu"]}


def read(p, delim=","):
    with open(p, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader([l for l in fh if not l.startswith("#")], delimiter=delim))


def host(u):
    return re.sub(r"^https?://", "", (u or "").strip().lower()).split("/")[0]


def on_domain(u, doms):
    h = host(u)
    return bool(h) and any(h == d or h.endswith("." + d) for d in doms)


def nname(s):
    s = re.sub(r"\b(dr|prof|professor|phd|ph\.d)\b\.?", " ", (s or "").lower())
    s = re.sub(r"\b[a-z]\b\.?", " ", re.sub(r"[^a-z\s-]", " ", s.replace(".", " ")))   # drop initials
    return " ".join(s.replace("-", " ").split())


def ror_ok(rid, cache, state, names, doms):
    key = rid.rsplit("/", 1)[-1]
    p = cache / f"{key}.json"
    if not p.exists():
        try:
            with urllib.request.urlopen(f"https://api.ror.org/v2/organizations/{key}", timeout=30) as r:
                p.write_bytes(r.read())
        except Exception as e:
            return False, f"ROR fetch failed: {e}"
    rec = json.loads(p.read_text())
    g = (rec.get("locations") or [{}])[0].get("geonames_details", {})
    rn = {re.sub(r"[^a-z0-9]+", " ", n.get("value", "").lower()).strip() for n in rec.get("names", [])}
    rd = set(rec.get("domains", []))
    if rec.get("status") != "active" or g.get("country_code") != "US" or not (g.get("country_subdivision_code") or "").endswith(state):
        return False, "ROR status/country/state disagree"
    if not (rd & set(doms) or rn & {re.sub(r"[^a-z0-9]+", " ", n.lower()).strip() for n in names}):
        return False, "ROR name/domain disagree"
    return True, ""


def append_rows(path, rows):
    raw = path.read_bytes()
    nl = b"\r\n" if b"\r\n" in raw else b"\n"
    if not raw.endswith(nl):
        sys.exit(f"{path} does not end with a newline")
    hdr = next(csv.reader(io.StringIO(raw.decode("utf-8"))))
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator=nl.decode())
    for r in rows:
        w.writerow([r.get(c, "") for c in hdr])
    path.write_bytes(raw + buf.getvalue().encode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--hd", required=True)
    ap.add_argument("--ipeds-ror", required=True)
    ap.add_argument("--ror-cache", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data, cache = Path(a.data_dir).resolve(), Path(a.ror_cache)
    cache.mkdir(parents=True, exist_ok=True)
    hd = {r["UNITID"]: r for r in read(a.hd)}
    xw = {r["unitid"]: r for r in read(a.ipeds_ror, "\t")}
    eco = read(data / "ecosystem.csv")
    orgs = [r for f in sorted(data.glob("organizations_*.csv")) for r in read(f)]
    people = read(data / "people.csv")
    ev = [r for f in sorted(data.glob("evidence*.csv")) for r in read(f)]   # sharded at SCHEMA v1.8
    held_by_unitid = {r["ipeds_unitid"]: r for r in eco if r["ipeds_unitid"] and not r["parent_institution_org_id"]}
    held_ror = {r["ror_id"] for r in eco if r["ror_id"]}
    held_names = {nname(p["full_name"]): p["person_id"] for p in people}
    next_org = max(int(r["org_id"][4:]) for r in eco + orgs if re.fullmatch(r"ORG-\d+", r["org_id"])) + 1
    next_person = max(int(p["person_id"][7:]) for p in people) + 1
    next_evd = max(int(e["evidence_id"][4:]) for e in ev if re.fullmatch(r"EVD-\d+", e["evidence_id"])) + 1

    lane_inst, lane_people = {}, []
    for d in sorted(HERE.glob("lanes/L*")):
        for r in (read(d / "institutions.csv") if (d / "institutions.csv").exists() else []):
            lane_inst[r["school_key"].strip()] = r | {"_lane": d.name}
        for r in (read(d / "people.csv") if (d / "people.csv").exists() else []):
            lane_people.append(r | {"_lane": d.name})

    holds, admitted, seen = [], {}, set()
    for r in lane_people:
        k = r["school_key"].strip()
        h = hd.get(SCHOOLS.get(k, ""), {})
        doms = DOMAINS.get(k) or [host(h.get("WEBADDR", "")).removeprefix("www.")]
        why = []
        if r["verdict"].strip() != "VERIFIED":
            continue
        if k not in SCHOOLS: why.append("unknown school_key")
        if r["role"].strip() not in ROLES: why.append(f"role {r['role']!r} outside the university professor vocabulary")
        for col in ("public_profile_url", "gate_a_url", "gate_b_url"):
            if not on_domain(r[col], doms): why.append(f"{col} not on {doms[0]}")
            if "@" in r[col]: why.append(f"{col} embeds '@'")
        if not r["gate_a_quote"].strip() or not r["gate_b_quote"].strip(): why.append("gate quote missing")
        if not r["role_as_published"].strip() or not r["full_name"].strip(): why.append("name or styling missing")
        nn = nname(r["full_name"])
        flag = r.get("already_in_atlas", "").strip()
        flagged = bool(re.search(r"PERSON-\d+", flag)) or flag.lower() in {"yes", "true", "y"}
        if nn in held_names or flagged: why.append(f"possible duplicate of {held_names.get(nn) or flag}")
        if (k, nn) in seen: why.append("duplicate inside the packet")
        if (k, nn) in INTEGRATOR_HOLDS: why.append("integrator review: " + INTEGRATOR_HOLDS[(k, nn)])
        if why:
            holds.append({"record": "person", "school_key": k, "name": r["full_name"], "lane": r["_lane"], "reason": "; ".join(why)})
            continue
        seen.add((k, nn))
        admitted.setdefault(k, []).append(r)

    inst_rows, people_rows, ev_rows, inst_id = [], [], [], {}
    for k, ppl in sorted(admitted.items()):
        u = SCHOOLS[k]
        if u in held_by_unitid:
            inst_id[k] = held_by_unitid[u]["org_id"]
            continue
        if len(ppl) < 2:
            for r in ppl:
                holds.append({"record": "person", "school_key": k, "name": r["full_name"], "lane": r["_lane"],
                              "reason": "school has <2 admitted people: no faculty cluster, institution not created"})
            continue
        h, li = hd[u], lane_inst.get(k, {})
        oid = f"ORG-{next_org:06d}"; next_org += 1
        inst_id[k] = oid
        web = "https://" + host(h["WEBADDR"]) + "/"
        ror = ""
        cand = (xw.get(u) or {}).get("ror", "").strip()
        if cand:
            full = "https://ror.org/" + cand.rsplit("/", 1)[-1]
            ok, why = ror_ok(full, cache, h["STABBR"], [h["INSTNM"], li.get("legal_name_as_published", "")], [host(h["WEBADDR"]).removeprefix("www.")] + DOMAINS.get(k, []))
            if ok and full not in held_ror:
                ror = full
            else:
                holds.append({"record": "ror", "school_key": k, "name": h["INSTNM"], "lane": "", "reason": why or "ROR already held"})
        unit = ""
        if li.get("polymer_unit_name", "").strip():
            unit = f" Polymer program lead (not built in this pass): {li['polymer_unit_name'].strip()} ({li.get('polymer_unit_url', '').strip()})."
        name = (li.get("legal_name_as_published") or "").strip() or h["INSTNM"]
        inst_rows.append({
            "org_id": oid, "legal_name": name, "ecosystem_subtype": "university_college", "polymer_program": "false",
            "polymer_program_name": "", "generalist": "false", "services_offered": "degrees", "geography_served": "national",
            "city": h["CITY"], "state": h["STABBR"], "county": COUNTY_OVERRIDE.get(k) or re.sub(r"\s+(County|Parish)$", "", h["COUNTYNM"]).strip(),
            "website": web, "description_1line": "", "pic_relevance": "research_partner", "status": "active",
            "sources": "; ".join(s for s in [web, "NCES IPEDS HD2024 UNITID " + u, ror] if s),
            "verification_tier": "A", "last_verified": TODAY, "created_by": BY,
            "notes": (f"Created {TODAY} (census-gap researcher wave) to anchor {len(ppl)} verified people records, each passing "
                      f"Gate A and Gate B on the university's own pages. Identity and UNITID {u} from IPEDS HD2024 "
                      f"(fetched {TODAY}); school list was a discovery lead only." + unit + (" ROR verified at api.ror.org " + TODAY + "." if ror else "")),
            "record_grain": "institution", "pic_member": "false", "ipeds_unitid": u, "ror_id": ror,
        })
        if ror:
            held_ror.add(ror)
        ev_rows.append({"evidence_id": f"EVD-{next_evd:06d}", "record_table": "ecosystem", "record_id": oid, "claim_type": "existence",
                        "claim_detail": f"{h['INSTNM']} ({h['CITY']}, {h['STABBR']}) is IPEDS UNITID {u}, web {host(h['WEBADDR'])}.",
                        "source_class": "registry", "source_ref": "https://nces.ed.gov/ipeds/datacenter/data/HD2024.zip",
                        "observed_date": TODAY, "tier_effect": "supports_B", "created_by": BY,
                        "notes": f"HD2024.csv fetched {TODAY} from NCES"}); next_evd += 1
        ev_rows.append({"evidence_id": f"EVD-{next_evd:06d}", "record_table": "ecosystem", "record_id": oid, "claim_type": "existence",
                        "claim_detail": f"{name} operates at {h['CITY']}, {h['STABBR']} (the university's own site).",
                        "source_class": "own_site", "source_ref": web, "observed_date": TODAY, "tier_effect": "supports_A",
                        "created_by": BY, "notes": ""}); next_evd += 1
        ev_rows.append({"evidence_id": f"EVD-{next_evd:06d}", "record_table": "ecosystem", "record_id": oid, "claim_type": "scope",
                        "claim_detail": f"Polymer faculty cluster: {len(ppl)} faculty whose own university pages state polymer research "
                                        f"(e.g. {ppl[0]['full_name']}: \"{ppl[0]['gate_b_quote'].strip()[:120]}\").",
                        "source_class": "own_site", "source_ref": ppl[0]["gate_b_url"].strip(),
                        "observed_date": TODAY, "tier_effect": "supports_A", "created_by": BY, "notes": ""}); next_evd += 1

    for k, ppl in sorted(admitted.items()):
        if k not in inst_id:
            continue
        for r in ppl:
            srcs = list(dict.fromkeys(s.strip() for s in (r["public_profile_url"], r["gate_a_url"], r["gate_b_url"]) if s.strip()))
            specs = "; ".join(dict.fromkeys(x.strip() for x in r["research_specialties"].split(";") if x.strip()))
            people_rows.append({"person_id": f"PERSON-{next_person:06d}", "full_name": r["full_name"].strip(),
                                "institution_org_id": inst_id[k], "program_org_id": "", "role": r["role"].strip(),
                                "role_as_published": r["role_as_published"].strip(), "research_specialties": specs,
                                "public_profile_url": r["public_profile_url"].strip(), "sources": ";".join(srcs),
                                "verification_tier": "A", "last_verified": TODAY})
            next_person += 1

    def write(name, cols, rows):
        with open(HERE / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n", extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    write("institution_rows.csv", list(eco[0].keys()), inst_rows)
    write("people_rows.csv", list(people[0].keys()), people_rows)
    write("evidence_append.csv", list(ev[0].keys()), ev_rows)
    write("holds.csv", ["record", "school_key", "name", "lane", "reason"], holds)
    per = {k: sum(1 for p in people_rows if p["institution_org_id"] == inst_id.get(k)) for k in SCHOOLS}
    print("people admitted per school:", {k: v for k, v in per.items() if v})
    print(f"institutions created {len(inst_rows)} ({sum(1 for r in inst_rows if r['ror_id'])} with ROR); people {len(people_rows)}; "
          f"evidence {len(ev_rows)}; holds {len(holds)}")
    if a.apply:
        if data == (Path(__file__).resolve().parents[2] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        append_rows(data / "ecosystem.csv", inst_rows)
        append_rows(data / "people.csv", people_rows)
        if ev_rows:
            append_rows(data / "evidence_ecosystem.csv", ev_rows)
        print("applied")


if __name__ == "__main__":
    main()
