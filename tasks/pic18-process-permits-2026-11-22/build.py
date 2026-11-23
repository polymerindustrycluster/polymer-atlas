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
    for c in read_csv(HERE / "canary_sites.csv"):
        s = c["site_id"]; h = hits[s]; ids = c["air_ids"].split(";"); fids = [x["fid"] for x in h["searches"]]
        n_hits = sum(x.get("n") or 0 for x in h["searches"]); err = [x for x in h["searches"] if "err" in x]
        docs = [d for x in h["searches"] for d in x.get("hits", [])]; fetched = [d for d, _ in docs if d in J]
        fin = sorted({d for d in fetched if any(cb.final_permit(doc_text(d), f) for f in fids)})
        if err: status = "search_failed"
        elif not n_hits: status = "air_record_no_document_found"
        elif not fin: status = "air_record_no_final_permit_in_newest_6"
        else: status = "retrievable_permit"
        out.append({"site_id": s, "echo_air_ids": c["air_ids"], "route": c["routes"], "edoc_documents_listed": n_hits, "docs_fetched": len(fetched), "final_permit_docids": ";".join(fin), "status": status})
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

SETTLE = {"not_bound": "", "ancillary_only": "a unit description that names a polymer process (the listed units are finishing paint booths)",
          "no_listed_process": "a unit description that names a §3.1 process, or a vocabulary ruling for the term in the note",
          "no_capability_destination": "tier A/B and supports_C, and the term has no §3.6 capability term: a unit narrative stating the operation (supports_A/B), or an owner ruling that adds a capability term"}

def readme(scr, model, m):
    fs = json.load(open(HERE / "frame_stats.json")); EXPECTED = int(re.search(r"EXPECTED_DEFECTS = (\d+)", (HERE / "check.py").read_text()).group(1))
    w = m["wilson95"]; pct = lambda k, n: f"{k}/{n} (Wilson 95% {w_of(k, n)})"
    def w_of(k, n): lo, hi = wilson(k, n); return f"{lo:.1%}–{hi:.1%}"
    sc = {r["site_id"]: r for r in scr}
    by_route = {}
    for k in ("lake", "frs"):
        ids = [r["site_id"] for r in scr if (k == "lake" and r["route"] == "lake") or (k == "frs" and "frs" in r["route"])]
        by_route[k] = (sum(sc[i]["status"] == "retrievable_permit" for i in ids), len(ids))
    P = {}
    for p in model["props"]: P.setdefault(p["site_id"], []).append(p)
    rows = []
    for r in model["sites"]:
        ps = P.get(r["site_id"], []); terms = "; ".join(sorted({p["term"] for p in ps if p["term"]})) or "none"
        wr = "; ".join(f"processes: `{p['term']}` ({p['strength']})" for p in ps if p["route"] == "processes") or "none"
        why = r["hold_reason"] + ((": " + r["strict_reasons"]) if r["hold_reason"] == "not_bound" else "") + ((". " + r["note"]) if r["note"] else "")
        rows.append(f"| {r['site_id']} | {r['tier']} | {r['strict_bind']} | {terms} | {wr} | {r['verdict']}{(': ' + why) if r['verdict'] != 'VERIFIED' else ''} |")
    nr = [s for s, r in sc.items() if r["status"] != "retrievable_permit"]
    return f"""# PIC-18 process from Ohio EPA air permits: frame, 25-site canary, packet only (change nothing under data/)

Claim: atlas-w22-process-permits, controller-assigned, 2026-11-22 (owner pick "Ohio air permits"). Reuses the 2026-11-18 lane unchanged (`tasks/pic18-permit-lane-2026-11-18/`, owner ruling 2026-11-18b item 1). Generated by `build.py`; checked by `check.py`. **Canary only: no data row, no PR.**

First user: the Atlas integrator, who decides at the next wave review whether to take the follow-up rulings below. Non-use is a finding if that review has not taken or declined them.

## The frame (`frame.py`, recomputed by `check.py`)

**Unit: Atlas sites, state OH, county in PIC-18, `operating_status` active, tier A–C.** {fs['pic18_active_ac_sites']} sites; **{fs['frame_no_process_site_and_org']}** have no process at the site and none at the organization (blank street on {fs['frame_blank_street']} of them).
Of those, **{fs['frame_with_air_id']} have an Ohio EPA air facility ID** by either route:

| Route | Sites with an ID |
|---|---|
| FRS registry link on the Atlas record (site's own, or organization-level when the organization has one frame site) -> lake `echo_air_facilities` | {fs['sites_with_id_from_frs']} |
| Lake `echo_air_facilities` (OH) row at the site's street (`derive_last_activity.same_street`) with the site's or organization's held name (`atlas.name_key` equal, or the earlier lane's holder token rule) | {fs['sites_with_id_from_lake']} |
| FRS only / lake only / both | {fs['frs_only']} / {fs['lake_only']} / {fs['both']} |

The lake route adds **{fs['lake_only']}** sites the FRS links do not reach. **{fs['same_street_name_mismatch_no_id']}** more frame sites match a lake row on street but not on name (a former or different operator at the address); they are not counted. Of the {fs['frame_with_air_id']}: **{fs['with_id_done_2026_11_18']}** were retrievable and examined on 2026-11-18 and are still without a process (held; 9 of that lane's 33 are no longer in the frame because a process is now on record); **{fs['with_id_searched_2026_11_18_no_permit']}** were searched then with no final permit retrievable; **{fs['with_id_new']}** are new. The frame is small: the **{fs['frame_no_process_site_and_org'] - fs['frame_with_air_id']}** sites without an ID are unreachable by this route (no ECHO air record at their street or name, or no street).

## Canary (seed 20261122)

`random.Random(20261122).sample(sorted(new sites), 25)` of the {fs['with_id_new']} new sites (`fetch.py draw`). Fetched by the documented route (Ohio EPA eDocument search by the 10-digit Facility ID; newest six non-draft documents per ID; no guessed URL). PDFs and text are in controller storage with sha256 (`doc_hashes.json`); none is in the repo (cover letters name individuals).

| Measure (unit: canary sites; tier mix A {m['tier_of_canary']['A']} / B {m['tier_of_canary']['B']} / C {m['tier_of_canary']['C']}) | Value |
|---|---|
| Retrievable final permit with the printed Facility ID | **{pct(m['retrievable_permit_sites'], 25)}**; by route: lake {by_route['lake'][0]}/{by_route['lake'][1]}, FRS-linked {by_route['frs'][0]}/{by_route['frs'][1]} |
| Not retrievable (availability facts, not absence) | {len(nr)}: {m['status'].get('air_record_no_document_found', 0)} portal search returned 0 documents; {m['status'].get('air_record_no_final_permit_in_newest_6', 0)} documents listed but no final permit among the newest six |
| Strictly bound (printed Facility ID, holder = Atlas legal or trade name, street, city) | **{pct(m['strict_bound_sites'], 25)}**; of retrievable {pct(m['strict_bound_sites'], m['retrievable_permit_sites'])} |
| Written to `processes` (tier C, bound, a §3.1 term at a unit) | **{pct(m['sites_with_process_written_to_processes'], 25)}**: {', '.join(m['process_sites']) or 'none'} |
| Capability row only (tier A/B) | {m['sites_with_capability_row_only']} |
| Any fill | **{pct(m['sites_with_any_fill'], 25)}**; of bound {pct(m['sites_with_any_fill'], m['strict_bound_sites'])} |
| Held sites by reason | {m['held_sites_by_reason']} |

Rules are the earlier lane's, unchanged and recomputed here: bind per cited document, witness position, strength (`supports_C` for a label, heading, table row or list; expiry caps at `supports_C`), route (tier C unions into `processes`; tier A/B -> `site_capabilities`, only for a §3.1 term with a §3.6 process term), ancillary test. Own-operation only; every quote is the holder's own permit and is checked as in order in the stored text.

## Per site

| Site | Tier | Bind | §3.1 terms proposed | Write | Verdict |
|---|---|---|---|---|---|
{chr(10).join(rows)}

`proposals.csv` has every quote with its document, permit number, dates, bind of that document, witness position, strength, route and hold reason. `sites.csv` has the site grain.

## What this says

**The route works but the yield is small.** {m['retrievable_permit_sites']} of 25 sites have a retrievable permit, 7 bind, 1 writes a process. Four of the 7 bound sites state no polymer process (a resin and chemical blender, a metals recovery plant, an inorganic catalyst plant, a plastic-parts paint-booth line); 2 more name a process with no capability destination (a roofing line's coating step, foam board cutting). **Nine of the 16 retrievable sites fail the bind, 8 on form rather than on identity** (holder form 5, blank Atlas street 2, municipality 1), and 3 of those carry a tier C term a write would take (below). The frame itself is the second limit: only {fs['frame_with_air_id']} of {fs['frame_no_process_site_and_org']} frame sites have an air ID.

**Expected change in the outcome line** (PIC-18 organization rows with process unknown, 322 of 794 at 393c389; only a `processes` cell on a tier C site moves it): this canary alone, **-1** (SITE-001078). Projected over the {fs['with_id_new']} new sites at the canary rate (1/25, Wilson 95% {w_of(1, 25)}): about -1 organization; the 25 sites of the canary are all but one of the new frame. The three form rulings below would add at most 3 more tier C sites in this canary (SITE-000981, SITE-001282, SITE-001399) — each unread beyond its unit headings and a single term — i.e. up to 4 of 25.

## Follow-up rulings (owner rulings; none applied). The earlier lane's three, restated with counts, and three new

Counts: earlier lane = its 33 retrievable sites; canary = these 25. No full-frame count exists yet beyond the 58 sites with an ID, because permits are read only for the 25 + 33.

1. **USPS abbreviations and a `Twp.` suffix bind** (earlier lane: 3 sites; canary: 0 sites differ in street abbreviation or `Twp.` alone; SITE-001399's `Pkwy` is one of two differences). Recommend yes, unchanged.
2. **A permit's `Permit Description` counts as an emissions-unit description at `supports_C`** (earlier: 1 site; canary: 0 sites, 1 duplicate quote at SITE-001937, whose site is held for another reason). Recommend yes, unchanged.
3. **Capability terms** (earlier: `compounding_unspecified`/`extrusion_unspecified` -> parents, 1 site; `coating_applying`, 2 sites). Canary adds **`coating_applying`: SITE-001690 (tier A)** and **`foam_fabrication`: SITE-001937 (tier B)**, i.e. 2 more sites held for no §3.6 destination. Recommend: leave `coating_applying` unmapped as before; add `foam_fabrication` as a §3.6 process term only if the owner wants fabrication at capability grain.
4. **NEW: holder-name form.** 5 of 16 retrievable canary sites fail on the holder: 3 on the holder alone, with street, city and Facility ID equal (`Johns Manville-Milan Plant` for `Johns Manville (Milan)`; `Ventra Sandusky, LLC` and `Ventra Salem, LLC` for `Ventra (Flex-N-Gate)`), and 2 with a second difference (`The Lincoln Electric Company` also differs in municipality; `Tarkett USA Inc.` for `Tarkett North America` also differs in street form). Recommend: also accept the Atlas **site name** (text before the locality). It settles the two Ventra sites; Johns Manville, Lincoln and Tarkett stay held as organization-identity questions.
5. **NEW: blank Atlas street** (2 of 16 retrievable: SITE-000220, SITE-001916; the permit prints a street). Recommend: hold; fill the street from a source other than the permit first.
6. **NEW: printed municipality differs from the Atlas city** at an equal street (SITE-001654 `Bedford` vs `Walton Hills`; SITE-000154 `Cleveland` vs `Euclid`, which also differs on the holder). Recommend: hold; a postal city is not an identity.

## Self-refute

- Grain: 25 sites, 18 proposals checked; the 2 written terms (SITE-001078) are unit-level; none rests on a permit or facility description.
- Strength: the written terms are graded `list` (a one-line unit label and a table row), so `supports_C`; no `supports_A` write.
- Attribution: all quotes are the holder's own permit; none from a parent, customer or equipment maker.
- Binding: SITE-001937's two older permits print holder `Trans-foam 281 SW` and are not cited; only the newest binds.

## Reproduction and checks

`uv run --with duckdb python tasks/pic18-process-permits-2026-11-22/frame.py` (frame), `python3 fetch.py draw|search|merge|docs` (network; resumable), `python3 build.py`, and the named check `uv run --with duckdb python tasks/pic18-process-permits-2026-11-22/check.py`: recomputes the frame from the repo and the lake, the registered draw, the stored-permit hashes, the screen, every proposal (with the earlier lane's audit rules, imported), the data diff (none under `data/`), a privacy scan (emails, phones, every person name printed in the stored permits), then runs {EXPECTED} injected defects and fails unless each is caught, including a quote not in the stored text and a permit for another facility.

Not checked: permits beyond the newest six documents per ID; the earlier lane's 24 held sites (not re-read) and the 8 sites it searched with no final permit (not re-searched); local-agency permits; whether any plant still runs the permitted equipment; units of unbound sites beyond headings and one term each. A permit is a statement as of its issue date and never a status finding.
"""

def main():
    scr = screen_rows(); write_csv("screen.csv", scr)
    model = model_of(scr)
    assert not model["viol"], model["viol"]
    write_csv("sites.csv", model["sites"]); write_csv("proposals.csv", model["props"])
    json.dump(doc_hashes(scr), open(HERE / "doc_hashes.json", "w"), indent=1, sort_keys=True)
    m = metrics(scr, model); json.dump(m, open(HERE / "metrics.json", "w"), indent=1)
    (HERE / "README.md").write_text(readme(scr, model, m)); print(json.dumps(m, indent=1)[:600])

if __name__ == "__main__": main()
