#!/usr/bin/env python3
"""Discovery leads from polymer-programs-db's hand-research layers, checked
against the Atlas. LEADS ONLY: nothing here is evidence (SCHEMA 4.11, the
Lakeland rule); every lead needs the named-program test on the institution's
own pages before any record. Each lead carries the public URL its layer cites.

Layers used: ABET accredited programs, hand_additions (programs invisible to a
CIP census), US non-degree credentials, Ohio program history, closure and
TAACCCT grant checks, polymer-specific society chapters (SPE / ACS Rubber
Division / ACS POLY-PMSE; generic Material Advantage chapters are left out),
and active polymer-CIP programs (census_program_keys) whose UNITID has no Atlas
record. Layers that come from PIC's internal vault or the faculty census are
NOT used: internal material never enters this public repo.

    python3 tasks/programs-db-crosswalk-2026-11-03/build_leads.py --data-dir data --programs-db <polymer-programs-db> --hd <HD2024.csv>
"""
import argparse, csv, glob, re
from pathlib import Path

OUT = Path(__file__).resolve().parent
STOP = {"university", "of", "the", "college", "community", "and", "at", "campus", "main", "state", "technical", "institute"}


def read(p, delim="\t"):
    with open(p, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader([l for l in fh if not l.startswith("#")], delimiter=delim))


def norm(s):
    s = re.sub(r"\(.*?\)", " ", (s or "").lower().replace("&", " and "))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--programs-db", required=True)
    ap.add_argument("--hd", required=True)
    a = ap.parse_args()
    data, pdb = Path(a.data_dir), Path(a.programs_db)
    held = [r for f in [data / "ecosystem.csv", *sorted(data.glob("organizations_*.csv"))] for r in read(f, ",")]
    by_name = {norm(r["legal_name"]): r["org_id"] for r in held}
    by_unitid = {r.get("ipeds_unitid"): r["org_id"] for r in held if r.get("ipeds_unitid")}
    hd = {r["UNITID"]: r for r in read(a.hd, ",")}

    def match(name, unitid=""):
        if unitid and unitid in by_unitid:
            return by_unitid[unitid], "unitid"
        n = norm(name)
        if n in by_name:
            return by_name[n], "exact name"
        nt = set(n.split()) - STOP
        hits = {oid for k, oid in by_name.items() if nt and set(k.split()) - STOP == nt}
        if len(hits) == 1:                # same distinctive words, e.g. 'Ohio State University' = 'The Ohio State University'
            return hits.pop(), "name, generic words ignored (check)"
        return "", ""

    leads = []
    def add(layer, inst, state, what, url, note="", unitid=""):
        oid, how = match(inst, unitid)
        leads.append({"layer": layer, "institution": inst, "state": state, "program_or_signal": what[:200],
                      "public_url": url, "atlas_org_id": oid, "atlas_match": how, "note": note[:200]})

    inc = pdb / "incoming"
    for r in read(inc / "abet_programs.tsv"):
        add("abet_accredited", r["institution"], r["state"], f"{r['program_name']} ({r['degree_level']}, ABET {r['commission']} since {r['accredited_since']})", r["url"])
    for line in open(pdb / "hand_additions.tsv", encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        p = line.rstrip("\n").split("\t")
        if len(p) >= 9 and p[0].isdigit():
            add("cip_invisible_program", p[1], p[2], f"{p[4]} ({p[5]})", p[-1] if p[-1].startswith("http") else "", p[7], p[0])
    for r in read(inc / "us_credentials.tsv"):
        add("non_degree_credential", r["provider"], r["state"], r["credential_name"], r["url"], r["provider_type"])
    for r in read(inc / "ohio_program_history.tsv"):
        add("ohio_program_history", r["institution"], "OH", r["programme"], r["evidence_url"], f"ended: {r['ended'][:80]}")
    for r in read(inc / "closure_verification.tsv"):
        add("closure_check", r["institution"], "", f"{r['verdict']}: {r['current_program_if_any']}", r["url"], r["confidence"])
    for r in read(inc / "grant_funding_check.tsv"):
        add("taaccct_grant_check", r["institution"], r["state"], f"{r['verdict']}: {r['grant_name']}", r["url"], r["confidence"])
    for f in ("society_chapters.tsv", "society_chapters_pass2.tsv"):
        for r in read(inc / f):
            if re.search(r"\bSPE\b|Plastics Engineers|Rubber|POLY|PMSE|Polymer", r["society"] + " " + r["chapter_or_signal"]):
                add("society_chapter", r["institution"], r["state"], f"{r['society']}: {r['chapter_or_signal']}", r["url"])
    keys = list(csv.DictReader(open(inc / "college-scorecard" / "census_program_keys.csv", encoding="utf-8")))
    seen = set()
    for k in keys:
        if k["cip_group"] == "polymer" and k["status"] == "active" and k["unitid"] not in by_unitid and k["unitid"] not in seen:
            seen.add(k["unitid"])
            h = hd.get(k["unitid"], {})
            add("ipeds_active_polymer_cip", h.get("INSTNM", k["unitid"]), h.get("STABBR", ""), f"CIP {k['cip']} {k['cip_title']} ({k['level']}, {k['first_year']}-{k['last_year']})",
                "https://" + h.get("WEBADDR", "").replace("https://", "").replace("http://", "") if h.get("WEBADDR") else "",
                "IPEDS listing is a lead only (Lakeland rule)", k["unitid"])

    cols = ["layer", "institution", "state", "program_or_signal", "public_url", "atlas_org_id", "atlas_match", "note"]
    with open(OUT / "leads.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n"); w.writeheader(); w.writerows(leads)
    import collections
    c = collections.Counter((l["layer"], bool(l["atlas_org_id"])) for l in leads)
    for layer in dict.fromkeys(l["layer"] for l in leads):
        print(f"{layer:26s} leads {c[(layer, True)] + c[(layer, False)]:4d}  institution held {c[(layer, True)]:4d}  not held {c[(layer, False)]:4d}")


if __name__ == "__main__":
    main()
