#!/usr/bin/env python3
"""OMG Thermoforming reframing correction (2026-11-11). The last of the four findings the licensed-source
cleanup lanes surfaced in PR #258, adjudicated in tasks/licensed-source-cleanup-2-2026-11-11/ and evidenced
in PR #266: OMG srl's own agents-and-distributors page lists 3407 Avenue D, Arlington TX in its US
agent/distributor network (omgusa.net), and no public page names OMG Thermoforming Inc. as a subsidiary of
OMG srl. Evidence rows EVD-333050 (existence), EVD-333051 (scope) and EVD-333052 (parent) record the three
original claims as contradicted. This packet corrects the two records to match that evidence.

    python3 tasks/omg-reframing-2026-11-11/build.py --data-dir data [--apply --i-am-the-integrator]

Changes:
- ORG-003807: description rewritten (agent/distributor presence, not a subsidiary); ultimate_parent_name
  cleared (the asserted parent link is supported by no public source; parent_org_id was already blank and
  no relationships row references the org, so no parity impact); sources rewritten to public citations
  only — the Plastics News citation comes out under AGENTS §5; notes carry the correction and cite the
  contradicting evidence rows; last_verified and last_activity_evidence_date 2026-11-11; tier held at C.
- SITE-004251: site_type hq_only -> sales_office; sources rewritten the same way; notes carry the
  correction and mark the est.-2018 / size details as original-packet, not re-verified; tier held at B
  (address and sales function corroborated by the parent's own current page).
- One inclusion_log row recording the correction. No new evidence rows: EVD-333050..52 are the evidence.
"""
import argparse, csv, io, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATE = "2026-11-11"
AGENTS_PAGE = "https://www.omgitaly.com/agenti-e-distributori"


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def header(p):
    return next(csv.reader(open(p, encoding="utf-8")))


def write(p, rows):
    eol = "\r\n" if b"\r\n" in p.read_bytes()[:4096] else "\n"
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header(p), lineterminator=eol, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    p.write_bytes(buf.getvalue().encode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--i-am-the-integrator", action="store_true")
    a = ap.parse_args()
    data = Path(a.data_dir).resolve()
    if a.apply and data == (HERE.parents[1] / "data").resolve() and not a.i_am_the_integrator:
        sys.exit("editing the real data/ is integrator work; pass --i-am-the-integrator")

    orgs = read(data / "organizations_TX.csv")
    sites = read(data / "sites_TX.csv")
    org = next((r for r in orgs if r["org_id"] == "ORG-003807"), None)
    assert org and org["ultimate_parent_name"] == "OMG srl" and org["description_1line"].startswith("US subsidiary"), \
        "ORG-003807 not in its expected pre-state"
    site = next((r for r in sites if r["site_id"] == "SITE-004251"), None)
    assert site and site["site_type"] == "hq_only", "SITE-004251 not in its expected pre-state"
    rels = read(data / "relationships.csv")
    assert not any("ORG-003807" in (r.get("from_org_id", ""), r.get("to_org_id", "")) for r in rels), \
        "a relationships row references ORG-003807 — stop and reassess the parent-field edit"

    log = ["org ORG-003807: subsidiary framing corrected to agent/distributor; ultimate_parent_name cleared; sources -> public only",
           "site SITE-004251: site_type hq_only -> sales_office; sources -> public only; notes corrected"]

    org = dict(org)
    org["ultimate_parent_name"] = ""
    org["description_1line"] = ("US sales and distribution presence for Italy's OMG srl thermoforming machines, "
                                "based in Arlington TX; the parent's own site lists the address in its "
                                "agent/distributor network")
    org["sources"] = (f"{AGENTS_PAGE} (the parent's own agents-and-distributors page, listing the Arlington TX "
                      "address in its US agent network, read 2026-11-11); place listing at 3407 Avenue D, "
                      "Arlington TX tied to omgitaly.com; http://omgitaly.com/")
    org["notes"] = org["notes"].rstrip() + (
        " [Reframing correction 2026-11-11] The record was created in pass 18 as a US subsidiary of OMG srl on "
        "Plastics News reporting. The parent's own agents-and-distributors page lists this address in OMG srl's "
        "US agent/distributor network (omgusa.net), and no public page names OMG Thermoforming Inc. as a "
        "subsidiary; evidence rows EVD-333050 (existence), EVD-333051 (scope) and EVD-333052 (parent), minted "
        "in PR #266, record the three original claims as contradicted. ultimate_parent_name is cleared: the "
        "asserted parent link is supported by no public source — if a corporate record surfaces, restore it by "
        "follow-up PR. The Plastics News citations are removed from sources under AGENTS §5 (a licensed source "
        "is a discovery lead, never a citation).")
    org["last_verified"] = DATE
    org["last_activity_evidence_date"] = DATE

    site = dict(site)
    site["site_type"] = "sales_office"
    site["sources"] = (f"OMG srl's own agents-and-distributors page ({AGENTS_PAGE}), listing 3407 Avenue D, "
                       "Arlington TX in its US agent network, read 2026-11-11; place listing tied to omgitaly.com")
    site["notes"] = site["notes"].rstrip() + (
        " [Reframing correction 2026-11-11] Not a subsidiary facility: the address is OMG srl's US "
        "agent/distributor location per the parent's own agents page (see ORG-003807 notes and "
        "EVD-333050..EVD-333052). site_type corrected hq_only -> sales_office. The est.-2018 and ~15,000 sq ft "
        "details above come from the original pass-18 packet and are not re-verified; the sales function and "
        "the address are corroborated by the parent's current page.")
    site["last_verified"] = DATE

    incl = {"date": DATE, "entity": "ORG-003807 / SITE-004251", "decision": "reframing correction applied",
            "rule_cited": "AGENTS §5 (licensed sources are discovery leads only; facts stand on public sources) + §3 evidence standard",
            "researcher": "spaghetti",
            "notes": "Subsidiary framing contradicted by the parent's own agents page (EVD-333050..52, PR #266): "
                     "Arlington TX is OMG srl's US agent/distributor location. ultimate_parent_name cleared; "
                     "site_type -> sales_office. Tombstoning the site as not-an-establishment was NOT taken; "
                     "it remains an owner call."}
    log.append("inclusion_log: +1 row (reframing correction)")

    print("\n".join(log))
    if a.apply:
        write(data / "organizations_TX.csv", [org if r["org_id"] == "ORG-003807" else r for r in orgs])
        write(data / "sites_TX.csv", [site if r["site_id"] == "SITE-004251" else r for r in sites])
        ipath = data / "inclusion_log.csv"
        write(ipath, read(ipath) + [incl])
        print("applied")


if __name__ == "__main__":
    main()
