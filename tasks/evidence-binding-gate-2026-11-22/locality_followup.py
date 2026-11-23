#!/usr/bin/env python3
"""Follow-up measure for the last_activity derivation (scripts/derive_last_activity.py); changes no data.

Today the derivation applies a tier-A extract row (name + city + state, built by the extract harness) when same_street()
holds, and never a tier-B row (the extract does not define tier B beyond "not A"). This script re-derives with one
change: an extract row of either tier applies when same_street() AND matching.same_locality() hold (same state, and
the printed city is the site's city or either part of a parenthetical city, or the ZIP5 values are equal). It compares
the result with the (last_activity_date, last_activity_source) pair every site carries at PIN and writes
locality_followup.csv beside itself (site ids, dates, sources and the reason only; no printed street or name).

The extract does not document what tier B means beyond "not A", and 919 tier-B rows print the site's exact city, so
tier B may also be a weaker name match. Each changed site therefore says whether the row that dates it passes the
evidence gate's own name test (check_evidence_binding: a held name, not a parent-only name, or a held name plus
corporate-form words); "rule_b" counts only those, "rule_a" counts every tier-B row. The
name test is the strict one (no parenthetical dropped; a key shared with a parent passes only on the own name's text);
the gate's designator and two-records legs are not re-applied here, so rule_b is an upper bound on what the gate would pass.

Usage: python3 tasks/evidence-binding-gate-2026-11-22/locality_followup.py
"""
import csv
import sys
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate  # noqa: E402
from matching import city_keys, corporate_form_extension, same_locality, same_street, same_zip5  # noqa: E402
from regions import PIC18  # noqa: E402

INPUTS = ROOT / "tasks/last-activity-street-leg-2026-11-22/inputs"
EXTRACTS = (("inspection", INPUTS / "witness_extract_sites_inspection.csv"), ("ita", INPUTS / "witness_extract_sites_ita.csv"))


PIN = "393c3895"  # origin/main when this was measured: the sites and the last_activity pairs compared against


def load_sites():
    sites = {r["site_id"]: r for r in gate.rows(PIN, "sites_*.csv")}
    assert len(sites) == 7196, len(sites)
    return sites


def why_local(s, r):
    """Which leg of same_locality() holds for a row it accepts: the city as written, a parenthetical part, or the ZIP."""
    q, rec = city_keys(r["city_as_printed"]), city_keys(s["city"])
    if q & city_keys(s["city"].split("(")[0]):
        return "city"
    if q & rec:
        return "parenthetical_city"
    assert same_zip5(s["zip"], r["zip_as_printed"])
    return "zip5"


def name_binds(idx, sid, name):
    """The gate's name test for a structured site row whose street passes."""
    q, oid = gate.name_keys([name]), idx.sites[sid].get("org_id")
    held, own, parents = idx.held_keys("sites", sid), idx.org_keys(oid), idx.parent_keys("sites", sid)
    on_parent = [k for k in q if k in parents or any(corporate_form_extension(p, k) for p in parents)]
    # a parent-only name, or a key shared with a parent whose text is not the site's own alone (gate: HELD)
    if on_parent and (not q & own or not {gate.squash(name)} & idx.own_texts(oid) - {gate.squash(n) for n in
                                                                                     idx.parent_names("sites", sid)}):
        return False
    return bool(q & held) or any(corporate_form_extension(h, k) for h in held for k in q)


RULES = {  # rule: (admit tier B, apply the locality test, a tier-B row also needs the gate's name test)
    "today": (False, False, False),  # derive_last_activity.py as merged: must reproduce every pair at PIN
    "tier_a_locality": (False, True, False),
    "rule_b": (True, True, True),
    "rule_a": (True, True, False),
}


def derive(sites, idx, rule):
    """-> (best {site_id: (date, label, precise, tier, leg)}, Counter of row outcomes) under one of RULES."""
    tier_b, locality, gate_names = RULES[rule]
    best, rows = {}, Counter()
    for kind, path in EXTRACTS:
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                s, tier = sites[r["record_id"].strip()], r["match_tier"].strip()
                if tier != "A" and not tier_b:
                    rows[f"{kind}.{tier}.excluded"] += 1
                    continue
                if not same_street(s["street_address"], r["street_as_printed"]):
                    rows[f"{kind}.{tier}.street_fails"] += 1
                    continue
                if locality and not same_locality(s["city"], s["state"], s["zip"], r["city_as_printed"], r["state_as_printed"],
                                     r["zip_as_printed"]):
                    rows[f"{kind}.{tier}.street_passes_locality_fails"] += 1
                    continue
                leg = why_local(s, r) if locality else "not_tested"
                if tier != "A" and gate_names and not name_binds(idx, s["site_id"], r["matched_estab_name"]):
                    rows[f"{kind}.{tier}.locality_passes_name_fails"] += 1
                    continue
                rows[f"{kind}.{tier}.applied.{leg}"] += 1
                w = r["witness_date_latest"].strip()
                d, label, precise = ((date.fromisoformat(w), "osha_inspection", True) if kind == "inspection"
                                     else (date(int(w), 12, 31), "osha_ita", False))
                cur = best.get(s["site_id"])
                if cur is None or (d, precise) > (cur[0], cur[2]):
                    best[s["site_id"]] = (d, label, precise, tier, leg)
    return best, rows


def compare(sites, best):
    out = []
    for sid, s in sorted(sites.items()):
        old = (s["last_activity_date"], s["last_activity_source"])
        b = best.get(sid)
        new = (b[0].isoformat(), b[1]) if b else ("", "")
        if old != new:
            kind = "newly_dated" if not old[0] else "cleared" if not new[0] else "date_or_source_changed"
            out.append({"site_id": sid, "state": s["state"], "county": s["county"],
                        "pic18": "yes" if s["state"] == "OH" and s["county"] in PIC18 else "no",
                        "change": kind, "old_date": old[0], "old_source": old[1], "new_date": new[0],
                        "new_source": new[1], "new_row_tier": b[3] if b else "", "new_row_locality": b[4] if b else ""})
    assert len({r["site_id"] for r in out}) == len(out)
    return out


def main():
    sites, idx = load_sites(), gate.Index.load(PIN)
    got = {"sites": len(sites), "populated_before": sum(1 for s in sites.values() if s["last_activity_date"])}
    changed = {}
    for rule in RULES:
        best, rows = derive(sites, idx, rule)
        out = changed[rule] = compare(sites, best)
        got[f"{rule}.pairs_changed"] = len(out)
        if rule == "today":
            assert not out, f"today's rule does not reproduce {len(out)} pairs at {PIN}"
            continue
        got[f"{rule}.populated_after"] = len(best)
        got.update({f"{rule}.change.{k}": v for k, v in Counter(r["change"] for r in out).items()})
        got.update({f"{rule}.change_pic18.{k}": v for k, v in Counter(r["change"] for r in out if r["pic18"] == "yes").items()})
        got.update({f"{rule}.change_by_locality.{k}": v for k, v in Counter(r["new_row_locality"] for r in out).items()})
        got.update({f"{rule}.rows.{k}": v for k, v in rows.items()})
    in_b = {r["site_id"] for r in changed["rule_b"]}
    assert in_b <= {r["site_id"] for r in changed["rule_a"]}
    with open(HERE / "locality_followup.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[*changed["rule_a"][0], "changes_if_tier_b_needs_gate_name"], lineterminator="\n")
        w.writeheader()
        w.writerows(dict(r, changes_if_tier_b_needs_gate_name="yes" if r["site_id"] in in_b else "no")
                    for r in changed["rule_a"])
    for k, v in sorted(got.items()):
        print(f"{k}: {v}")
    return got

if __name__ == "__main__":
    main()
