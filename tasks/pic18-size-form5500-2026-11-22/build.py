#!/usr/bin/env python3
"""Form 5500 follow-up packet for the 28 fills withdrawn from PR #468 (packet only; nothing under data/ changes).
Applies Codex's two round-2 tests to every filing under the sponsor's EIN in the national files, before any address filter:
  test 1  one plan number with positive active participants in the window (a plan-number inventory by EIN, any state, any address);
  test 2  the selected return is the LATEST return of that plan (same EIN and plan number); a later return that cannot be bound to the recorded
          street is a hold, never an automatic fall-back to the older filing.
Also the partial-plan tests of the size packet (plan name, collective-bargaining field of the 5500 and the 5500-SF, pension/welfare feature codes).
No Form 5500 mailing street is written anywhere: equality with the recorded street is tested, the line is never published (owner round 12).
usage: build.py --cache DIR (extract_ein.py output f5500_ein28.csv) --eins eins.csv (site_id,ein) --data-dir BASEDATA --out DIR"""
import argparse, csv, re, sys
from collections import Counter, defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "pic18-size-sprint-2026-11-22"))
import build as B  # noqa: E402  (street_key / same_street / band_of / partial_plan / CUTOFF)
csv.field_size_limit(10**9)
rd = lambda p: list(csv.DictReader(open(p, newline="", encoding="utf-8")))

def src_date(r):
    b = r["plan_year"][:10]
    return r["tax_prd"][:10] if r.get("tax_prd") and r["tax_prd"][:10] >= b else f"{int(b[:4]) + 1}{b[4:]}"
def count(r):
    try: return int(float(r["active"] or 0))
    except ValueError: return 0
def band(r): return B.band_of(count(r)) if count(r) >= 1 else ""
def partial(r):
    """B.partial_plan reads cb / welfare / pension / plan_name; the 5500-SF collective-bargaining field is COLLECTIVELY_BARGAINED (extract_ein.py puts it in cb); a Y or 1 counts"""
    x = dict(r); x["cb"] = "1" if (r.get("cb") or "").strip().upper() in ("1", "Y") else ""
    return B.partial_plan(x)

def evaluate(inputs, inv, eins, sites):
    """-> (rows, inventory rows) ; rows carry the verdict under both readings of test 1"""
    by_ein = defaultdict(list)
    for r in inv: by_ein[r["ein"]].append(r)
    sd = {s["site_id"]: s for s in sites}; out = []
    for p in inputs:
        sid = p["site_id"]; ein = eins[sid]; s = sd[sid]
        rows = [r for r in by_ein[ein] if src_date(r) >= B.CUTOFF]
        ack = p["row_locator"].split("id=")[1]; sel = next(r for r in rows if r["rid"] == ack)
        plans_all = sorted({r["pn"] for r in rows}); plans_pos = sorted({r["pn"] for r in rows if count(r) >= 1})
        same_plan = [r for r in rows if r["pn"] == sel["pn"]]; latest = max(same_plan, key=lambda r: (r["plan_year"], src_date(r)))
        newer = [r for r in same_plan if (r["plan_year"], src_date(r)) > (sel["plan_year"], src_date(sel))]
        newer_binds = any(B.same_street(s["street_address"], r["mail1"]) or B.same_street(s["street_address"], r["loc1"]) for r in newer)
        why = []
        if len(plans_pos) != 1 or sel["pn"] not in plans_pos: why.append(("f5500_multiple_plans", f"{len(plans_pos)} plan numbers with positive participants in the window under the sponsor EIN ({', '.join(plans_pos)}); one is required"))
        if newer: why.append(("newer_return_of_same_plan", f"a return of plan {sel['pn']} for plan year {latest['plan_year'][:4]} exists under the same EIN" + ("; it binds to the recorded street, so it, not this older filing, would be the one to use" if newer_binds else "; it cannot be bound to the recorded street (different mailing line, not published), so the older filing is not used and nothing falls back")))
        pw = partial(sel)
        if pw: why.append(("f5500_partial_plan", pw))
        out.append(dict(p=p, sel=sel, plans_all=plans_all, plans_pos=plans_pos, newer=bool(newer), newer_binds=newer_binds, why=why, any_other_plan=len(plans_all) > 1))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cache", required=True); ap.add_argument("--eins", required=True); ap.add_argument("--data-dir", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    orgs, sites = B.load_atlas(a.data_dir); eins = {r["site_id"]: r["ein"] for r in rd(a.eins)}
    inputs = rd(HERE / "inputs_28.csv"); inv = rd(f"{a.cache}/f5500_ein28.csv")
    res = evaluate(inputs, inv, eins, sites)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    def w(name, hdr, rows):
        with open(out / name, "w", newline="") as f: x = csv.writer(f, lineterminator="\n"); x.writerow(hdr); x.writerows(rows)
    surv = [r for r in res if not r["why"]]
    w("packet.csv", ["site_id", "org_id", "source", "source_file", "file_sha256", "row_locator", "filing_year", "source_date", "band", "r13_source", "name_match", "evidence_id_withdrawn_from_646545f6_not_to_be_reused"],
      [[r["p"]["site_id"], r["p"]["org_id"], "form5500", r["p"]["source_file"], r["p"]["file_sha256"], r["p"]["row_locator"], r["p"]["filing_year"], r["p"]["source_date"], r["p"]["band"], 3, r["p"]["name_match"], r["p"]["evidence_id_646545f6"]] for r in surv])
    w("holds.csv", ["site_id", "org_id", "reason", "detail", "withdrawn_evidence_id"], [[r["p"]["site_id"], r["p"]["org_id"], r["why"][0][0], " | ".join(d for _, d in r["why"]), r["p"]["evidence_id_646545f6"]] for r in res if r["why"]])
    w("sponsor_plan_inventory.csv", ["site_id", "plan_number", "plan_year_begin", "source_date", "active_participants_band", "plan_type", "selected_filing", "source_file", "row_locator"],
      [[sid, r["pn"], r["plan_year"][:10], src_date(r), band(r), "pension" if (r["pension"] or "").strip() else ("welfare" if (r["welfare"] or "").strip() else "unknown"), "yes" if any(p["row_locator"].endswith("id=" + r["rid"]) and p["site_id"] == sid for p in inputs) else "",
        "raw/" + r["file"], f"{r['member']}|row={r['row']}|id={r['rid']}"] for sid, ein in sorted(eins.items()) for r in sorted([x for x in inv if x["ein"] == ein], key=lambda x: (x["pn"], x["plan_year"]))])
    anyplan = [r for r in res if not r["why"] and not r["any_other_plan"]]
    stats = dict(candidates=len(res), survive_positive_participants_reading=len(surv), survive_any_other_plan_number_reading=len(anyplan),
                 fail_multiple_plans_positive=sum(1 for r in res if any(k == "f5500_multiple_plans" for k, _ in r["why"])), fail_any_other_plan_number=sum(1 for r in res if r["any_other_plan"]),
                 fail_newer_return=sum(1 for r in res if r["newer"]), newer_return_binds_recorded_street=sum(1 for r in res if r["newer_binds"]), fail_partial_plan=sum(1 for r in res if any(k == "f5500_partial_plan" for k, _ in r["why"])),
                 filings_under_the_28_eins=len(inv), organizations_surviving=len({r["p"]["org_id"] for r in surv}))
    import json; (out / "counts.json").write_text(json.dumps(stats, indent=1) + "\n")
    print(stats)
    for r in res:
        if r["why"] or r["any_other_plan"]: print(r["p"]["site_id"], [k for k, _ in r["why"]], "other plan numbers:", r["plans_all"], "positive:", r["plans_pos"])

if __name__ == "__main__": main()
