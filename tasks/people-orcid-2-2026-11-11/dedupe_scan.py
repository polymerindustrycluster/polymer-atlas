#!/usr/bin/env python3
"""Static dedupe screen for people records (companion to the ORCID completion pass, 2026-11-11).

Groups people records by shared keys that suggest a split record. This is a screen, not a verdict:
every group is a lead for the integrator, with the fact that would settle it. The ORCID-keyed alarms
(one iD passing for two records) are produced by build.py into alarm_pairs.csv; this scan adds the
name/institution/profile-URL classes and asserts the identifier table's one-row-per-value rule.

    python3 tasks/people-orcid-2-2026-11-11/dedupe_scan.py
Writes dedupe_leads.csv in this task folder.
"""
import csv, re, sys, unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

SUFFIX = {"jr", "sr", "ii", "iii", "iv", "phd", "pe"}


def toks(s):
    s = unicodedata.normalize("NFKD", re.sub(r"\([^)]*\)", " ", s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return [t for t in re.split(r"[^a-z]+", s) if t]


def name_key(full):
    w = [t for t in toks(full) if len(t) > 1 and t not in SUFFIX]
    return (w[0], w[-1]) if len(w) >= 2 else None


def main():
    people = list(csv.DictReader(open(ROOT / "data/people.csv", encoding="utf-8")))
    ids = list(csv.DictReader(open(ROOT / "data/people_identifiers.csv", encoding="utf-8")))
    by_id = defaultdict(list)
    for r in ids:
        by_id[r["identifier_id"]].append(r["person_id"])
    collisions = {k: v for k, v in by_id.items() if len(v) > 1}
    assert not collisions, f"one-row-per-value violated: {collisions}"

    leads = []
    by_name_inst = defaultdict(list)
    by_name = defaultdict(list)
    by_url = defaultdict(list)
    for p in people:
        k = name_key(p["full_name"])
        if k:
            by_name_inst[(k, p["institution_org_id"])].append(p)
            by_name[k].append(p)
        if p["public_profile_url"].strip():
            by_url[p["public_profile_url"].strip().lower().rstrip("/")].append(p)
    for (k, inst), ps in sorted(by_name_inst.items()):
        if len(ps) > 1:
            leads.append(("same_name_same_institution", ";".join(p["person_id"] for p in ps),
                          f"{k[0]} {k[-1]} at {inst}",
                          "compare roles, profile URLs and ORCID iDs; one person at one institution is one record"))
    for url, ps in sorted(by_url.items()):
        keys = {name_key(p["full_name"]) for p in ps}
        if len(ps) > 1 and len(keys) == 1 and None not in keys:
            # a shared URL alone is normal (roster and faculty-list pages are cited by many records);
            # it is a split signal only when the records sharing it also share a name
            leads.append(("same_profile_url_same_name", ";".join(p["person_id"] for p in ps), url,
                          "two records with one name cite one page; read it and settle whether they are one person"))
    for k, ps in sorted(by_name.items()):
        insts = {p["institution_org_id"] for p in ps}
        if len(ps) > 1 and len(insts) > 1 and not any(
                set(p["person_id"] for p in ps) <= set(l[1].split(";")) for l in leads):
            leads.append(("same_name_other_institution", ";".join(p["person_id"] for p in ps),
                          f"{k[0]} {k[-1]} at {';'.join(sorted(insts))}",
                          "namesakes, a move, or a joint appointment (AGENTS S6: record once, at the primary home)"))
    with open(HERE / "dedupe_leads.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["lead_class", "person_ids", "detail", "settling_fact"])
        w.writerows(leads)
    from collections import Counter
    print(f"{len(people)} people; identifier collisions 0; leads {len(leads)}")
    for k, v in Counter(l[0] for l in leads).items():
        print(f"  {v:4d}  {k}")


if __name__ == "__main__":
    main()
