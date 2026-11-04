#!/usr/bin/env python3
"""Integrate wave-2 people lanes (census-gap follow-ups and band-A census leads) into people rows.

    python3 tasks/census-gap-2-2026-11-03/build_people.py --data-dir data --raw <raw_check.csv>
        [--school-map <tsv school_key<TAB>unitid>] [--apply --i-am-the-integrator] <lane people.csv> [...]

Admits a lane row only when: verdict VERIFIED; the raw-page check (raw_check.csv: the integrator re-fetched each gate
URL and found the quote word for word) is yes for Gate A and Gate B; role in the university professor vocabulary;
all three URLs on the institution's own domain, none embedding '@'; the institution is held (IPEDS UNITID, institution
grain); the name is not already in people.csv (normalized, initials dropped) nor twice in the packet; not in
INTEGRATOR_HOLDS. Everything else goes to holds.csv with its reason. PERSON ids are allocated above people.csv's max.
Helpers and the first wave's school map come from tasks/census-gap-people-2026-11-03/build_integration.py.
"""
import argparse, csv, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "census-gap-people-2026-11-03"))
from build_integration import DOMAINS, ROLES, SCHOOLS, append_rows, host, nname, on_domain, read  # noqa: E402

TODAY = "2026-11-03"
ROLES = ROLES | {"senior_lecturer"}  # owner ruling B-CG-3 (2026-11-03), SCHEMA 4.9 [v1.8.2]
EXTRA_DOMAINS = {  # held record carries no website, or the university publishes on a second domain
    "Carnegie Mellon University": ["cmu.edu"],
    "Pennsylvania State University-Main Campus": ["psu.edu"],
    "University of Washington-Seattle Campus": ["washington.edu", "uw.edu"],
}  # UConn Health (uchc.edu) is deliberately not added: a separate unit, so Kumbar stays held for review
NEWS = "Gate B rests on a university news item, not the person's own profile or lab page"
INTEGRATOR_HOLDS = {  # normalized name -> reason; integrator review of every VERIFIED Gate B quote, 2026-11-03
    "yang yang": "Gate B quote is the MSE department research-areas page, not person-level",
    "jenn ming yang": "Gate B quote is the MSE department research-areas page, not person-level",
    "benjamin wiley": NEWS, "randall erb": NEWS, "nikhil gupta": NEWS, "thanh nguyen": NEWS,
    "mary beth browning monroe": NEWS, "junsoo kim": NEWS,
    "keith vorst": "Gate B quote is the consortium page he directs, not person-level (Nutt precedent)",
    # B-CG-2 (ruled 2026-11-03): a biopolymer passes when the stated research engineers it as a material.
    # Schroeder ("Mineralization of biopolymers for sustainable material development") passes; Ribbeck's quote
    # describes mucins in the body rather than engineering them, so it stays held for an engineered-material quote.
    "katharina ribbeck": "B-CG-2: Gate B quote describes mucin polymers in the body, not engineering them as a material",
    "efie kokkoli": "role_as_published is a sentence fragment ('a professor of ...'), not the printed title",
    "jeff moore":"same person as the Jeffrey S. Moore row in the same lane; one record only",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--school-map")
    ap.add_argument("--out", default=str(HERE))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    ap.add_argument("lanes", nargs="+")
    a = ap.parse_args()
    data, out = Path(a.data_dir).resolve(), Path(a.out)
    schools = dict(SCHOOLS)
    if a.school_map:
        schools.update({r[0]: r[1] for r in csv.reader(open(a.school_map, encoding="utf-8"), delimiter="\t") if len(r) == 2})
    eco = read(data / "ecosystem.csv")
    by_unit = {r["ipeds_unitid"]: r for r in eco if r["ipeds_unitid"] and not r["parent_institution_org_id"]}
    orgs = {r["org_id"]: r for f in sorted(data.glob("organizations_*.csv")) for r in read(f)}
    for l in read(data / "registry_links.csv"):  # universities held as organization records (e.g. Delaware)
        if l.get("registry") == "IPEDS_UNITID" and l["org_id"] in orgs:
            by_unit.setdefault(l["registry_id"], orgs[l["org_id"]])
    people = read(data / "people.csv")
    held = {nname(p["full_name"]): p["person_id"] for p in people}
    raw = {(r["school_key"], nname(r["full_name"])): r for r in read(a.raw)}
    next_person = max(int(p["person_id"][7:]) for p in people) + 1

    rows, holds, seen = [], [], set()
    for f in a.lanes:
        for r in read(f):
            if r.get("verdict", "").strip() != "VERIFIED":
                continue
            k, nn = r["school_key"].strip(), nname(r["full_name"])
            inst = by_unit.get(schools.get(k, ""))
            site = ".".join(host(inst["website"]).split(".")[-2:]) if inst and inst.get("website") else ""
            doms = DOMAINS.get(k) or EXTRA_DOMAINS.get(k) or ([site] if site else [])
            if inst and not doms: why_inst = "institution has no website to check URLs against"
            else: why_inst = ""
            rc = raw.get((k, nn), {})
            why = []
            if not inst: why.append(f"institution not held (school_key {k!r}, UNITID {schools.get(k, '?')})")
            if why_inst: why.append(why_inst)
            if rc.get("gate_a") != "yes" or rc.get("gate_b") != "yes":
                why.append(f"raw check gate_a={rc.get('gate_a', 'none')} gate_b={rc.get('gate_b', 'none')}")
            if r["role"].strip() not in ROLES: why.append(f"role {r['role']!r} outside the university professor vocabulary")
            for col in ("public_profile_url", "gate_a_url", "gate_b_url"):
                if doms and not on_domain(r[col], doms): why.append(f"{col} not on {doms[0]}")
                if "@" in r[col]: why.append(f"{col} embeds '@'")
            if not r["role_as_published"].strip(): why.append("styling missing")
            flag = r.get("already_in_atlas", "").strip().lower()
            if nn in held or flag not in ("", "no", "false", "n"): why.append(f"possible duplicate of {held.get(nn) or flag}")
            if (k, nn) in seen: why.append("duplicate inside the packet")
            if nn in INTEGRATOR_HOLDS: why.append("integrator review: " + INTEGRATOR_HOLDS[nn])
            if why:
                holds.append({"school_key": k, "name": r["full_name"], "lane_file": Path(f).parent.name, "reason": "; ".join(why)})
                continue
            seen.add((k, nn))
            srcs = list(dict.fromkeys(s.strip() for s in (r["public_profile_url"], r["gate_a_url"], r["gate_b_url"]) if s.strip()))
            rows.append({"person_id": f"PERSON-{next_person:06d}", "full_name": r["full_name"].strip(),
                         "institution_org_id": inst["org_id"], "program_org_id": "", "role": r["role"].strip(),
                         "role_as_published": r["role_as_published"].strip(),
                         "research_specialties": "; ".join(dict.fromkeys(x.strip() for x in r["research_specialties"].split(";") if x.strip())),
                         "public_profile_url": r["public_profile_url"].strip(), "sources": ";".join(srcs),
                         "verification_tier": "A", "last_verified": TODAY})
            next_person += 1
    assert len({r["person_id"] for r in rows}) == len(rows)
    for name, cols, rs in (("people_rows.csv", list(people[0].keys()), rows),
                           ("holds.csv", ["school_key", "name", "lane_file", "reason"], holds)):
        with open(out / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(rs)
    print(f"people admitted {len(rows)}; held {len(holds)}")
    if a.apply:
        if data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
            sys.exit("appending to the real data/ is integrator work; pass --i-am-the-integrator")
        append_rows(data / "people.csv", rows)
        print("applied")


if __name__ == "__main__":
    main()
