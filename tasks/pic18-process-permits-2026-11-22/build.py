"""PIC-18 Ohio EPA air-permit process lane, 2026-11-22: canary packet. Idempotent; writes only inside this folder (change nothing under data/).

  python3 build.py        # screen.csv, sites.csv, proposals.csv, metrics.json, doc_hashes.json, README.md from the stored permits + verdicts.json

Reuses the 2026-11-18 lane's rules unchanged (tasks/pic18-permit-lane-2026-11-18/build.py: header, strict bind, witness position, strength, route,
ancillary test, §3.1 / §3.6 mapping), loaded as `lb` and pointed at this lane's permit store and date. Nothing here asserts a bind, a strength or a
route: verdicts.json carries only the reader's quotes and §3.1 terms; everything else is recomputed from the stored permits and the Atlas rows.
"""
import csv, hashlib, importlib.util, json, re, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
P = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/process-permits-2026-11-22")
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m
lb = _load("lane_build", ROOT / "tasks/pic18-permit-lane-2026-11-18/build.py"); cb = lb.cb
lb.LANE = P; lb.AS_OF = "2026-11-22"; lb.WHO = "claude-code atlas-w22-process-permits"
AS_OF = lb.AS_OF; URL = lb.URL
read_csv, header, doc_text = lb.read_csv, lb.header, lb.doc_text
_atlas = lb.atlas
import functools
@functools.lru_cache(maxsize=None)
def atlas():
    """The lane's atlas(), plus non-organization entities from ecosystem.csv (the frame and the outcome harness count them: ORG ids with no organizations row)."""
    sites, orgs = _atlas(); orgs = dict(orgs)
    for r in read_csv(ROOT / "data/ecosystem.csv"):
        if r["org_id"] not in orgs: orgs[r["org_id"]] = {**r, "trade_names": r.get("trade_names", "") or ""}
    return sites, orgs
lb.atlas = atlas
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def journal():
    J = {}
    for l in open(P / "fetch_journal.jsonl"): d = json.loads(l); J[d["docid"]] = d
    return J

def screen_rows():
    """One row per canary site from the stored search hits and fetched documents: air IDs, documents listed, final permits whose printed Facility ID is one of the site's IDs."""
    hits = json.load(open(P / "search_hits_all.json")); J = journal(); out = []
    import fetch as FE
    canary = {c["site_id"] for c in read_csv(HERE / "canary_sites.csv")}
    for c in FE.targets():
        s = c["site_id"]; h = hits[s]; ids = c["air_ids"].split(";"); fids = [x["fid"] for x in h["searches"]]
        n_hits = sum(x.get("n") or 0 for x in h["searches"]); err = [x for x in h["searches"] if "err" in x]
        docs = [d for x in h["searches"] for d in x.get("hits", [])]; fetched = [d for d, _ in docs if d in J]
        fin = sorted({d for d in fetched if any(cb.final_permit(doc_text(d), f) for f in fids)})
        if err: status = "search_failed"
        elif not n_hits: status = "air_record_no_document_found"
        elif not fin: status = "air_record_no_final_permit_in_newest_6"
        else: status = "retrievable_permit"
        out.append({"site_id": s, "set": "canary" if s in canary else "frame_extra", "echo_air_ids": c["air_ids"], "route": c["routes"], "edoc_documents_listed": n_hits, "docs_fetched": len(fetched), "final_permit_docids": ";".join(fin), "status": status})
    return out

def write_csv(name, rows):
    with open(HERE / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n", extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def loaded(scr):
    caps = {(r["site_id"], r["capability_type"], r["term"]) for r in read_csv(ROOT / "data/site_capabilities.csv")}
    return dict(V=json.load(open(HERE / "verdicts.json")), scr=scr, text=doc_text, caps=caps, **dict(zip(("sites", "orgs"), atlas())))

def doc_hashes(scr):
    J = journal(); out = {}
    for r in scr:
        for d in r["final_permit_docids"].split(";"):
            if not d: continue
            for ext, key in (("pdf", "pdf_sha256"), ("txt", "text_sha256")):
                assert sha(P / "docs" / f"{d}.{ext}") == J[d][key], f"{d}.{ext}: sha256 differs from the fetch journal"
            h = header(doc_text(d))
            out[d] = dict(site_id=r["site_id"], url=URL + d, pdf_sha256=J[d]["pdf_sha256"], text_sha256=J[d]["text_sha256"], bytes=J[d]["bytes"], fetched_utc=J[d]["fetched_utc"],
                          permit_number=h["permit_number"], facility_id=h["facility_id"], issue_date=cb.mdy(h["issue_date"]), expiration_date=cb.mdy(h["expiration_date"]))
    return out

def model_of(scr):
    lb.N_FRAME = sum(r["status"] == "retrievable_permit" for r in scr)
    return lb.compute(loaded(scr))

def wilson(k, n): return [round(x, 3) for x in cb.wilson(k, n)]

def subset(scr, model, keep):
    """The canary (or any site subset) view of the full-frame model."""
    return ([r for r in scr if r["site_id"] in keep],
            {"frame": [s for s in model["frame"] if s in keep], "sites": [r for r in model["sites"] if r["site_id"] in keep], "props": [p for p in model["props"] if p["site_id"] in keep], "viol": model["viol"]})

def metrics(scr, model):
    n = len(scr); st = Counter(r["status"] for r in scr); ret = st["retrievable_permit"]; m = lb.metrics(model)
    sites = model["sites"]; bound = m["strict_bound_sites"]
    wrote = m["sites_with_process_written"]; cap = len(m["capability_only_sites"])
    fill = len(set(m["process_sites"]) | set(m["capability_only_sites"]))
    return {"canary_sites": n, "status": dict(st), "retrievable_permit_sites": ret, "strict_bound_sites": bound, "near_bound_sites": m["near_bound_sites"],
            "sites_with_process_written_to_processes": wrote, "process_sites": m["process_sites"], "sites_with_capability_row_only": cap,
            "sites_with_any_fill": fill, "verified_sites": m["verified_sites"], "still_uncertain_sites": m["still_uncertain_sites"], "reject_sites": m["reject_sites"],
            "held_sites_by_reason": m["held_sites_by_reason"], "proposal_holds_by_reason": m["proposal_holds_by_reason"],
            "tier_of_canary": dict(Counter(atlas()[0][r["site_id"]]["verification_tier"] for r in scr)),
            "wilson95": {"retrievable_of_canary": [ret, n, wilson(ret, n)], "bound_of_canary": [bound, n, wilson(bound, n)], "bound_of_retrievable": [bound, ret, wilson(bound, ret)] if ret else None,
                         "any_fill_of_canary": [fill, n, wilson(fill, n)], "processes_written_of_canary": [wrote, n, wilson(wrote, n)],
                         "any_fill_of_bound": [fill, bound, wilson(fill, bound)] if bound else None}}

def readme(scr, model, m):
    fs = json.load(open(HERE / "frame_stats.json")); EXPECTED = int(re.search(r"EXPECTED_DEFECTS = (\d+)", (HERE / "check.py").read_text()).group(1))
    c, f, o = m["canary"], m["full_frame_read"], m["outcome_line"]
    def w_of(k, n): lo, hi = wilson(k, n); return f"{lo:.1%}–{hi:.1%}"
    pct = lambda k, n: f"{k}/{n} (Wilson 95% {w_of(k, n)})"
    sc = {r["site_id"]: r for r in scr}; P = {}
    for p in model["props"]: P.setdefault(p["site_id"], []).append(p)
    by_route = {}
    for k in ("lake", "frs"):
        ids = [r["site_id"] for r in scr if r["set"] == "canary" and ((k == "lake" and r["route"] == "lake") or (k == "frs" and "frs" in r["route"]))]
        by_route[k] = (sum(sc[i]["status"] == "retrievable_permit" for i in ids), len(ids))
    rows = []
    for r in model["sites"]:
        ps = P.get(r["site_id"], []); terms = "; ".join(sorted({p["term"] for p in ps if p["term"]})) or "none"
        wr = "; ".join(f"processes: `{p['term']}` ({p['strength']})" for p in ps if p["route"] == "processes") or "none"
        why = r["hold_reason"] + ((": " + r["strict_reasons"]) if r["hold_reason"] == "not_bound" else "") + ((". " + r["note"]) if r["note"] else "")
        rows.append(f"| {r['site_id']} | {r['tier']} | {r['strict_bind']} | {terms} | {wr} | {r['verdict']}{(': ' + why) if r['verdict'] != 'VERIFIED' else ''} |")
    st = Counter(r["status"] for r in scr); sc2 = o["process_unknown_after_if"]; k1, k2, k3 = list(sc2.values())
    return f"""# PIC-18 process from Ohio EPA air permits: full frame (58 sites) as a packet, canary first (no change under data/)

Claim: atlas-w22-process-permits, controller-assigned, 2026-11-22 (owner pick "Ohio air permits"). Reuses the 2026-11-18 lane unchanged (`tasks/pic18-permit-lane-2026-11-18/`, owner ruling 2026-11-18b item 1) and applies the owner ruling of 2026-11-22 relayed by the controller: a permit emissions-unit description fills `processes` only when it **names** a process in the SCHEMA §3.1 vocabulary, quoted from the permit, for that site only; general equipment (mixer, blender, paint booth, station) fills nothing and is a hold; no equipment-implies-process mapping beyond the 2026-11-18 lane's. Generated by `build.py`; checked by `check.py`. **Packet only: no data row, no PR.**

First user: the Atlas integrator, who decides at the next wave review whether to take the follow-up rulings below. Non-use is a finding if that review has not taken or declined them.

## The frame (`frame.py`, recomputed by `check.py`)

**Unit: Atlas sites, state OH, county in PIC-18, `operating_status` active, tier A–C.** {fs['pic18_active_ac_sites']} sites; **{fs['frame_no_process_site_and_org']}** have no process at the site and none at the organization (blank street on {fs['frame_blank_street']}). **{fs['frame_with_air_id']} of those have an Ohio EPA air facility ID** (59 IDs; two sites carry two):

| Route | Sites with an ID |
|---|---|
| FRS registry link (the site's own, or organization-level when the organization has one frame site) -> lake `echo_air_facilities` | {fs['sites_with_id_from_frs']} |
| Lake `echo_air_facilities` (OH) row at the site's street (`derive_last_activity.same_street`) with the site's or organization's held name (`atlas.name_key` equal, or the earlier lane's holder token rule) | {fs['sites_with_id_from_lake']} |
| FRS only / lake only / both | {fs['frs_only']} / {fs['lake_only']} / {fs['both']} |

The lake route adds **{fs['lake_only']}** sites FRS does not reach (the 26 new sites are 18 lake-only and 8 with an FRS link the 2026-11-18 pool did not hold). **{fs['same_street_name_mismatch_no_id']}** more frame sites match a lake row on street but not on name (a different operator at the address); not counted. The other {fs['frame_no_process_site_and_org'] - fs['frame_with_air_id']} frame sites are unreachable by this route.

Of the {fs['frame_with_air_id']}: **{fs['with_id_done_2026_11_18']}** were retrievable and read on 2026-11-18 and are still without a process (held; 9 of that lane's 33 left the frame because a process is now on record); **{fs['with_id_searched_2026_11_18_no_permit']}** were searched then with no final permit retrievable (7 zero hits, 2 no final among the newest six, as Muse's re-download confirms); **{fs['with_id_new']}** are new: **25 drawn as the canary** (seed 20261122) and **1 more (SITE-002106)**, searched on the go with 0 documents returned.

Documents: Ohio EPA eDocument search by the 10-digit Facility ID, newest six non-draft documents per ID, the earlier lane's route (`fetch.py`; no URL guessed). The 24 earlier sites' documents are Muse's and the earlier lane's stored files and were not re-fetched. PDFs and text are in controller storage with sha256 (`doc_hashes.json`); none is in the repo (cover letters name individuals).

## Result

| Measure (unit: sites) | Canary (25 new) | Full frame read here (26 new) |
|---|---|---|
| Retrievable final permit with the printed Facility ID | **{pct(c['retrievable_permit_sites'], 25)}**; lake route {by_route['lake'][0]}/{by_route['lake'][1]}, FRS-linked {by_route['frs'][0]}/{by_route['frs'][1]} | {f['retrievable_permit_sites']}/26 |
| Not retrievable (availability facts, not absence) | {25 - c['retrievable_permit_sites']}: {c['status'].get('air_record_no_document_found', 0)} zero documents, {c['status'].get('air_record_no_final_permit_in_newest_6', 0)} no final permit in the newest six | {26 - f['retrievable_permit_sites']} |
| Strictly bound (printed Facility ID, holder = Atlas legal or trade name, street, city) | **{pct(c['strict_bound_sites'], 25)}**; of retrievable {pct(c['strict_bound_sites'], c['retrievable_permit_sites'])} | {f['strict_bound_sites']} |
| Written to `processes` (tier C, bound, a §3.1 process named at a unit) | **{pct(c['sites_with_process_written_to_processes'], 25)}**: {', '.join(c['process_sites']) or 'none'} | {f['sites_with_process_written_to_processes']} |
| Capability row only (tier A/B) | {c['sites_with_capability_row_only']} | {f['sites_with_capability_row_only']} |
| Any fill | **{pct(c['sites_with_any_fill'], 25)}** | {f['sites_with_any_fill']} |
| Held sites by reason | {c['held_sites_by_reason']} | {f['held_sites_by_reason']} |

The 24 earlier sites stay held under the new ruling as the 2026-11-18 lane left them (carried from its `sites.csv`, not re-read): 16 not bound, 2 near-bound (format), 1 ancillary, 3 no capability destination, 2 verified as capability rows or already held. The ruling changes nothing for them: no held one is a tier C site with a bound, named term.

**Outcome line this packet would give** (PIC-18 organization rows, process unknown, harness definition, working tree at 393c389): **{o['process_unknown_before']} -> {o['process_unknown_after']} of {o['pic18_org_rows']}** (-{o['fall']}: SITE-001078, `calendering`, ORG-000999's only PIC-18 site). Only a `processes` cell on a tier C site moves it. Rulings that would add (each an owner ruling, none applied): a holder rule that also accepts the Atlas site name -> **{k1}** (SITE-001282, `compression_molding`); that plus a plant-suffix holder rule -> **{k2}** (SITE-000981, `rubber_calendering` and `rubber_extrusion`, a rubber roofing calender/extruder line); opening the `processes` route to tier A/B sites with a bound, named unit term (SITE-000601, SITE-001888, SITE-001937, SITE-002124, SITE-002855) -> **{k3}** from the packet, upper bound.

## What this says

The route is real and thin. {f['retrievable_permit_sites']} of the 26 new sites have a permit, 7 bind, 1 writes. Of the 7 bound sites, 4 state no polymer process (a resin and chemical blender, a metals recovery plant, an inorganic catalyst plant, a plastic-parts paint-booth line), 1 is a roofing line of general equipment, and 1 (foam board cutting, tier B) names a process with no capability destination. Nine of the 16 retrievable sites fail the bind, 8 on form not identity (holder form 5, blank Atlas street 2, municipality 1). The frame is small because only {fs['frame_with_air_id']} of {fs['frame_no_process_site_and_org']} frame sites have an air ID, and the bind rule is the larger loss: it turns 16 retrievable permits into 7.

## Per site (the 26 sites read now)

| Site | Tier | Bind | §3.1 terms proposed | Write | Verdict |
|---|---|---|---|---|---|
{chr(10).join(rows)}

`proposals.csv` has every quote with its document, permit number, dates, bind, witness position, strength, route and hold reason; `sites.csv` the site grain. SITE-001078's other proposals: `laminating` held as equipment only ("Kawakami Laminator", a machine name) and `printing_decorating_plastics` held because the substrate is not stated. SITE-002106: the portal search returned 0 documents for its ID (an availability fact).

## Follow-up rulings (owner rulings; none applied). The earlier lane's three, restated with counts, and three new

Counts: earlier lane = its 33 retrievable sites (24 still in the frame); canary = the 16 retrievable sites read now.

1. **USPS abbreviations and a `Twp.` suffix bind.** Earlier lane: 3 sites (SITE-000264, SITE-001137, SITE-002113; SITE-001137 has since left the frame). Canary: 0 sites differ by that alone (SITE-001399's `Pkwy` is one of two differences). Recommend yes, unchanged.
2. **A permit's `Permit Description` counts as a unit description at `supports_C`.** Earlier: 1 site (SITE-000814, since filled elsewhere). Canary: 0. Recommend yes, unchanged; it matters little.
3. **Capability terms and the tier A/B route.** Earlier: `compounding_unspecified`/`extrusion_unspecified` -> their §3.6 parents (1 site), `coating_applying` (2 sites), `foam_molding_bead` (1). Canary adds `foam_fabrication` (SITE-001937). The 2026-11-22 ruling says a named process "may fill `processes`"; it does not say whether that lifts the 2026-11-14 rule that a `supports_C` term on a tier A/B record is a capability row only. **The packet keeps that rule.** If the owner lifts it, the outcome line moves to {k3} (5 sites above); recommend lifting only for a unit-level named term at a bound site, as the scenario counts.
4. **NEW: holder-name form.** 5 of 16 retrievable canary sites fail on the holder: 3 on the holder alone with street, city and Facility ID equal (`Johns Manville-Milan Plant` for `Johns Manville (Milan)`; `Ventra Sandusky, LLC` and `Ventra Salem, LLC` for `Ventra (Flex-N-Gate)`), 2 with a second difference (`The Lincoln Electric Company`, also municipality; `Tarkett USA Inc.` for `Tarkett North America`, also street form). Recommend: also accept the Atlas **site name** (text before the locality). It settles the two Ventra sites; Johns Manville, Lincoln and Tarkett stay held as organization-identity questions.
5. **NEW: blank Atlas street** (2 of 16: SITE-000220, SITE-001916; the permit prints a street, but the permit cannot supply the street it is tested against). Recommend: hold; fill the street from another source first. {fs['frame_blank_street']} of the {fs['frame_no_process_site_and_org']} frame sites have a blank street.
6. **NEW: printed municipality differs from the Atlas city** at an equal street (SITE-001654 `Bedford` vs `Walton Hills`; SITE-000154 `Cleveland` vs `Euclid`, which also differs on the holder). Recommend: hold; a postal city is not an identity.

## Self-refute

- Grain: {len(model['props'])} proposals; the one written term is unit-level, none rests on a permit or facility description.
- Strength: the written term is graded `list` (a one-line unit label), so `supports_C`; no `supports_A` write.
- Equipment rule: 3 quotes held as equipment only (a laminator, a rubber mixer, a roofing saturator line); resin blending, reactors and vinyl mixers carry no term; the one write names its process in the unit text ("heated rolling and calendering operations").
- Attribution: every quote is the holder's own permit; none from a parent, customer or equipment maker. Binding: SITE-001937's two older permits print holder `Trans-foam 281 SW` and are not cited.

## Reproduction and checks

`uv run --with duckdb python tasks/pic18-process-permits-2026-11-22/frame.py` (frame), `python3 fetch.py draw|search|merge|docs` (network; resumable; `new_facility_ids.csv` lists IDs not in Muse's manifest), `python3 build.py`, and the named check `uv run --with duckdb python tasks/pic18-process-permits-2026-11-22/check.py`: recomputes the frame from the repo and the lake, the registered draw, the stored-permit hashes, the screen, every proposal (the earlier lane's audit rules, imported), the outcome line against the controller harness, the data diff (none under `data/`), a privacy scan (emails, phones, every person name printed in the stored permits), then runs {EXPECTED} injected defects and fails unless each is caught, including a quote not in the stored text and a permit for another facility.

Not checked: permits beyond the newest six documents per ID; the 24 earlier held sites (carried, not re-read) and the 8 searched with no final permit (not re-searched); local-agency permits; whether any plant still runs the permitted equipment; units of unbound sites beyond headings and one term each. A permit is a statement as of its issue date and never a status finding.
"""

def unknown_orgs(planned=None):
    """The outcome harness's definition (S/harness/pic18_unknown.py) over the working tree: PIC-18 organization rows (ids with an active OH PIC-18 tier A-C site) whose
    process is unknown at site and organization grain; `planned` = {site_id: [terms]} is unioned into the site cells first."""
    sys.path.insert(0, str(ROOT / "scripts")); from regions import PIC18
    sites, orgs = atlas(); planned = planned or {}
    gt = {}
    for s in sites.values():
        if s["state"] == "OH" and s["county"] in PIC18 and s["operating_status"] == "active" and s["verification_tier"] in ("A", "B", "C") and s["verification_tier"]: gt.setdefault(s["org_id"], []).append(s)
    toks = lambda v: {x.strip() for x in (v or "").split(";") if x.strip() and x.strip() != "unknown"}
    unk = 0
    for oid, ss in gt.items():
        t = set().union(*(toks(s["processes"]) | set(planned.get(s["site_id"], [])) for s in ss)) or toks((orgs.get(oid) or {}).get("processes"))
        unk += not t
    return len(gt), unk

def outcome(model):
    planned = {}
    for p in model["props"]:
        if p["route"] == "processes": planned.setdefault(p["site_id"], []).append(p["term"])
    n, before = unknown_orgs(); _, after = unknown_orgs(planned)
    def plus(*extra):
        d = {s: list(t) for s, t in planned.items()}
        for s, t in extra: d.setdefault(s, []).extend(t)
        return unknown_orgs(d)[1]
    held = lambda s: sorted({p["term"] for p in model["props"] if p["site_id"] == s and p["hold_reason"] == "not_bound" and p["term"] and p["position"].startswith("unit_")})
    ab = [(p["site_id"], [p["term"]]) for p in model["props"] + read_csv(ROOT / "tasks/pic18-permit-lane-2026-11-18/proposals.csv")
          if p["bind_doc"] == "BOUND" and p["position"].startswith("unit_") and p["term"] and p["hold_reason"] in ("", "no_capability_destination") and p["tier"] in ("A", "B")]
    sc = {"site_name_holder_rule (SITE-001282)": plus(("SITE-001282", held("SITE-001282"))),
          "site_name_holder_rule + holder_suffix_rule (SITE-001282, SITE-000981)": plus(("SITE-001282", held("SITE-001282")), ("SITE-000981", held("SITE-000981"))),
          "tier_A_B_processes_route_open (bound, named unit-level term, tier A/B)": plus(*ab)}
    return {"pic18_org_rows": n, "process_unknown_before": before, "process_unknown_after": after, "fall": before - after, "planned_site_terms": planned,
            "process_unknown_after_if": sc, "tier_A_B_sites_in_that_scenario": sorted({s for s, _ in ab})}

def all_metrics(scr, model):
    canary = {r["site_id"] for r in scr if r["set"] == "canary"}
    return {"canary": metrics(*subset(scr, model, canary)), "full_frame_read": metrics(scr, model), "outcome_line": outcome(model)}

def main():
    scr = screen_rows(); write_csv("screen.csv", scr)
    model = model_of(scr)
    assert not model["viol"], model["viol"]
    write_csv("sites.csv", model["sites"]); write_csv("proposals.csv", model["props"])
    json.dump(doc_hashes(scr), open(HERE / "doc_hashes.json", "w"), indent=1, sort_keys=True)
    m = all_metrics(scr, model); json.dump(m, open(HERE / "metrics.json", "w"), indent=1)
    (HERE / "README.md").write_text(readme(scr, model, m)); print(json.dumps(m, indent=1)[:600])

if __name__ == "__main__": main()
