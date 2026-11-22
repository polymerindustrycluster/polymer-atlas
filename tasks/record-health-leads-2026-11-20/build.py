#!/usr/bin/env python3
"""Record-health leads from the 2026-11-20 evidence lanes: places where a government filing or registry record sits at an
Atlas record's place under ANOTHER company's name, or carries a closure signal. A triage packet; it edits nothing in
data/. Each lead is a reason to re-verify the record's operator, name or status, never a change by itself (AGENTS.md §3:
status changes need dated evidence; a false merge destroys data).

    python3 tasks/record-health-leads-2026-11-20/build.py      (from the repo root; writes leads.csv, prints counts)

Sources (all merged on main): the OSHA site lane, the FRS site lane and the TRI organization lane task folders. Counts
are reconciled against each lane's own ledger and review files before anything is written. Stdlib only.
"""
import csv, json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = HERE.parent
OSHA, FRS, TRI = (TASKS / f"evidence-{x}-2026-11-20" for x in ("osha-sites", "frs-sites", "tri-filings"))
COLS = ["lead_id", "lane", "lead_class", "record_table", "record_id", "tier", "atlas_name", "atlas_place", "witness",
        "witness_name", "witness_place", "reviewer_note", "suggested_check"]
CHECK = {
    "files_under_other_name": "Re-verify who operates this address: successor, affiliate, tenant, or a multi-tenant building.",
    "filer_differs_from_operator": "Re-verify the operator: the filer at this place is a different company.",
    "registry_names_other_company": "Re-verify the operator or the site name: EPA's record names another company here.",
    "tri_names_other_facility": "Review the TRI link: the linked facility names another facility or parent.",
    "closure_signal": "Re-verify operating status (a closure signal is never a closure: AGENTS.md §3).",
}
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8", newline="")))


def verdicts(folder, fam):
    out = {}
    for p in sorted(folder.glob(f"review_{fam}*.json")):
        t = p.read_text(encoding="utf-8")
        out.update({(v["record_id"], v["claim_type"]): v for v in json.loads(t[t.index("{"):t.rindex("}") + 1])["verdicts"]})
    return out


def build():
    leads = []
    add = lambda **k: leads.append({c: k.get(c, "") for c in COLS} | {"suggested_check": CHECK[k["lead_class"]]})
    # OSHA: an address-only filing (another name at the site's street), and reviewed filings rejected as another company
    led = rd(OSHA / "ledger.csv")
    codex, agy = verdicts(OSHA, "codex"), verdicts(OSHA, "agy")
    for l in led:
        common = dict(lane="osha", record_table="sites", record_id=l["site_id"], tier=l["tier"],
                      atlas_name=f"{l['operator']} / {l['site_name']}", atlas_place=f"{l['atlas_street']}, {l['city']}, {l['state']}",
                      witness=f"OSHA ITA Form 300A 2025, establishment {l['osha_establishment_id']}",
                      witness_name=" / ".join(x for x in (l["osha_establishment"], l["osha_company"]) if x.strip()),
                      witness_place=l["osha_street"])
        if l["verdict"] == "ADDR_ONLY":
            add(lead_class="files_under_other_name", **common)
        elif l["verdict"] == "ADDR+NAME":
            bad = [v for v in (codex.get((l["site_id"], "existence")), agy.get((l["site_id"], "existence"))) if v and v["verdict"] != "SOUND"]
            if bad:
                add(lead_class="filer_differs_from_operator", reviewer_note=bad[0].get("reason", ""), **common)
    # FRS: EPA's record names another company (matcher) or the reviewer rejected the name as another company
    fv = verdicts(FRS, "codex")
    for l in rd(FRS / "ledger.csv"):
        rej = fv.get((l["site_id"], "existence"))
        if l["verdict"] == "NAME_DIFF" or (rej and rej["verdict"] != "SOUND"):
            add(lane="frs", lead_class="registry_names_other_company", record_table="sites", record_id=l["site_id"], tier=l["tier"],
                atlas_name=f"{l['operator']} / {l['site_name']}", atlas_place=f"{l['atlas_street'] or '(no street)'}, {l['city']}, {l['state']}",
                witness=f"EPA FRS registry {l['frs_registry_id']}", witness_name=l["frs_name"],
                witness_place=f"{l['frs_street']}, {l['frs_city']}", reviewer_note=rej.get("reason", "") if rej and rej["verdict"] != "SOUND" else "")
    # TRI: the linked facility names another facility or parent; the closed flag
    for l in rd(TRI / "ledger.csv"):
        if l["verdict"] in ("NO_MATCH", "CLOSED"):
            add(lane="tri", lead_class="tri_names_other_facility" if l["verdict"] == "NO_MATCH" else "closure_signal",
                record_table="organizations", record_id=l["org_id"], tier=l["tier"], witness=f"EPA TRI facility {l['trifid']}",
                witness_name=" / ".join(x for x in (l["facility_name"], l["parent"]) if x.strip()), witness_place=l["facility_address"],
                reviewer_note="TRI facility closed flag (fac_closed_ind = 1)" if l["verdict"] == "CLOSED" else "")
    # Reconcile against each lane's own counts (AGENTS.md §2 rule 10c) before writing anything
    by = Counter((x["lane"], x["lead_class"]) for x in leads)
    assert by[("osha", "files_under_other_name")] == sum(l["verdict"] == "ADDR_ONLY" for l in led) == 123
    assert by[("osha", "filer_differs_from_operator")] == 9, by  # 6 rejected in #434 + 3 in part 3
    assert by[("frs", "registry_names_other_company")] == 9 + 13, by  # matcher NAME_DIFF + reviewer rejects
    assert by[("tri", "tri_names_other_facility")] == 27 and by[("tri", "closure_signal")] == 1, by
    keys = [(x["record_table"], x["record_id"], x["lane"], x["lead_class"]) for x in leads]
    assert len(keys) == len(set(keys)), "duplicate lead"
    leads.sort(key=lambda x: (x["lead_class"], x["record_table"], x["record_id"]))
    for i, x in enumerate(leads, 1):
        x["lead_id"] = f"RH-{i:04d}"
    with open(HERE / "leads.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n"); w.writeheader(); w.writerows(leads)
    print(f"{len(leads)} leads on {len({(x['record_table'], x['record_id']) for x in leads})} records: "
          + "; ".join(f"{lane}/{cls} {n}" for (lane, cls), n in sorted(by.items())))


if __name__ == "__main__":
    build()
