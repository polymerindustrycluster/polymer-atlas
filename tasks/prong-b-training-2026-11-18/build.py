#!/usr/bin/env python3
"""Non-degree plastics-processing training into data/programs.csv under SCHEMA v1.15.1 (owner ruling 2026-11-18: prong (b)
is met when a training program's own page states plastics processing). Applies packet.csv rows whose existence AND scope quotes both passed the raw check
(rawcheck.csv: an independent Firecrawl/Jina re-fetch, word-sequence match). Each row gets an existence and a scope
evidence row (own_site, supports_A). RJG Train the Trainer stays held (see README).
Idempotent: a program already present (same institution and name) is skipped.

    python3 tasks/credentials-programs-2026-11-18/build.py [--apply]
"""
import csv, io, sys
from pathlib import Path

T = Path(__file__).resolve().parent
ROOT = T.parents[1]
DATE, BY = "2026-11-18", "claude-code prong-b-training-2026-11-18"
PROG0, EVD0 = 352, 397110  # above main and every open PR on 2026-11-18


def read(p):
    raw = p.read_bytes(); eol = "\r\n" if b"\r\n" in raw[:4096] else "\n"
    r = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    return r.fieldnames, list(r), eol


def write(p, head, rows, eol):
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=head, lineterminator=eol); w.writeheader(); w.writerows(rows)
    p.write_bytes(buf.getvalue().encode("utf-8"))


def main():
    packet = list(csv.DictReader(open(T / "packet.csv", encoding="utf-8")))
    raw = {r["key"]: r["raw"] for r in csv.DictReader(open(T / "rawcheck.csv", encoding="utf-8"))}
    ph, progs, pe = read(ROOT / "data/programs.csv")
    eh, ev, ee = read(ROOT / "data/evidence_programs.csv")
    have = {(p["institution_org_id"], p["program_name"]) for p in progs}
    ids, evids = {p["program_id"] for p in progs}, {e["evidence_id"] for e in ev}
    new_p, new_e, n = [], [], 0
    for r in packet:
        if any(raw.get(f"{r['key']}|{c}") != "yes" for c in ("existence", "scope", "engagement")):
            print("not applied (raw check):", r["key"]); continue
        if (r["institution_org_id"], r["program_name"]) in have:
            continue
        pid = f"PROG-{PROG0 + n:06d}"; i = n; n += 1
        assert pid not in ids
        row = {c: "" for c in ph}
        row.update(program_id=pid, institution_org_id=r["institution_org_id"], program_name=r["program_name"],
                   program_type=r["program_type"], credential_types=r["credential_types"], level=r["level"],
                   description_1line=r["description_1line"], url=r["url"], public_door_url=r["url"],
                   admissions_status="unknown", status="active", sources=r["url"], verification_tier="A",
                   last_verified=DATE, created_by=BY,
                   notes=(f"Created {DATE} under SCHEMA v1.15.1 (owner ruling {DATE}: non-degree training whose own page states plastics "
                          f"processing meets prong (b)). SCHEMA section 4.11 prong {r['prong']} on the provider's own page; "
                          f"existence and scope quotes raw-checked by independent re-fetch. admissions_status unknown: "
                          f"no dated intake was checked. engagement_modes basis (raw-checked): '{r['engagement_quote']}'. "
                          f"credential_types, location and specialty fields left blank, unverified."))
        if r["program_type"] == "apprenticeship":
            row["apprenticeship_registered"] = "true"
        row["engagement_modes"] = r["engagement_modes"]
        new_p.append(row)
        for k, (claim, q) in enumerate((("existence", r["existence_quote"]), ("scope", r["scope_quote"]))):
            eid = f"EVD-{EVD0 + 2 * i + k:06d}"
            assert eid not in evids
            new_e.append(dict(evidence_id=eid, record_table="programs", record_id=pid, claim_type=claim,
                              claim_detail=(f"{r['program_name']} exists as recorded" if claim == "existence"
                                            else f"plastics-processing scope (SCHEMA section 4.11 prong {r['prong']})"),
                              source_class="own_site", source_ref=r["url"], observed_date=DATE, tier_effect="supports_A",
                              created_by=BY, notes="Raw words in order: " + q))
    print(f"programs +{len(new_p)}; evidence +{len(new_e)}")
    # SCHEMA 4.11 rollup (validator V-16): an institution's polymer_program_name / _url follow its program rows
    TYPE_PREC = {"degree": 0, "center": 1, "certificate": 2, "apprenticeship": 3, "training": 4, "lab_facility": 5, "course": 6}
    xh, eco, xe = read(ROOT / "data/ecosystem.csv")
    allp = progs + new_p
    touched = {p["institution_org_id"] for p in new_p}
    for r in eco:
        if r["org_id"] in touched and r.get("record_grain") == "institution":
            P = sorted((p for p in allp if p["institution_org_id"] == r["org_id"] and p.get("status") != "tombstoned"),
                       key=lambda p: (TYPE_PREC[p["program_type"]], p["program_name"].strip().lower()))
            r["polymer_program_name"] = "; ".join(p["program_name"].strip() for p in P)
            r["polymer_program_url"] = P[0]["url"].strip()
            if r.get("polymer_program") == "false":
                r["polymer_program"] = "true"
            print("rollup updated:", r["org_id"])
    if "--apply" in sys.argv and new_p:
        write(ROOT / "data/programs.csv", ph, progs + new_p, pe)
        write(ROOT / "data/evidence_programs.csv", eh, ev + new_e, ee)
        write(ROOT / "data/ecosystem.csv", xh, eco, xe)
        print("written")


if __name__ == "__main__":
    main()
