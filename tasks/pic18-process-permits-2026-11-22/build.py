"""PIC-18 Ohio EPA air-permit process lane, 2026-11-22: canary packet. Idempotent; writes only inside this folder (change nothing under data/).

  python3 build.py        # screen.csv, sites.csv, proposals.csv, metrics.json, doc_hashes.json, README.md from the stored permits + verdicts.json

Reuses the 2026-11-18 lane's rules unchanged (tasks/pic18-permit-lane-2026-11-18/build.py: header, strict bind, witness position, strength, route,
ancillary test, §3.1 / §3.6 mapping), loaded as `lb` and pointed at this lane's permit store and date. Nothing here asserts a bind, a strength or a
route: verdicts.json carries only the reader's quotes and §3.1 terms; everything else is recomputed from the stored permits and the Atlas rows.
"""
import csv, hashlib, importlib.util, json, re, subprocess, sys
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
import bisect
@functools.lru_cache(maxsize=64)
def _toks(text):
    """(word tokens with their line numbers, lines), as the earlier lane's position() builds them. The lane's `text.count("\\n", 0, m.start())` per token is quadratic on a 600,000-character Title V permit; a bisect over newline offsets gives the same line number."""
    nl = [i for i, ch in enumerate(text) if ch == "\n"]
    return [(m.group(), bisect.bisect_left(nl, m.start())) for m in re.finditer(r"[a-z0-9]+", text.lower())], text.split("\n")

def position(text, quote):
    """lane build.position(), same rules, linear time."""
    toks, lines = _toks(text); q = cb.words(quote); n = len(q); w = [t for t, _ in toks]; found = ""
    for i in range(len(w) - n + 1):
        if w[i:i + n] != q: continue
        ln = toks[i][1]
        if "....." in lines[ln]: continue
        found = "other"
        if re.match(r"\s*\d+\.\s+([A-Z]\d{3}\b|Emissions Unit Group)", lines[ln]): return "unit_heading"
        for k in range(ln, max(-1, ln - 60), -1):
            L = lines[k]
            if re.match(r"\s*[a-z]\)\s", L): break
            if re.search(r"Permit Description:", L): cls = "permit_description" if ln - k < 6 else ""
            elif re.search(r"Facility Description:", L): cls = "facility_description" if ln - k < 3 else ""
            elif re.search(r"Operations,?\s+Propert\S*\s+and/or\s+Equipment\s+Description:\s*$", L): cls = "unit_paragraph" if ln - k < 8 else ""
            elif re.match(r"\s*EU\s*ID\b", L): cls = "unit_table_row"
            else: continue
            if cls: return cls
            break
    return found

def first_line(text, quote):
    toks, lines = _toks(text); q = cb.words(quote); n = len(q); w = [t for t, _ in toks]
    return next((toks[i][1] for i in range(len(w) - n + 1) if w[i:i + n] == q and "....." not in lines[toks[i][1]]), None)

_lane_position = lb.position; lb.position = position; lb.first_line = first_line

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def final_permit(text, fid):
    """The canary's final_permit() with one repair: older permits print `RE: FINALAIR POLLUTION ...` (pdftotext drops the space), which the canary's `FINAL\\s+AIR` read as not final."""
    return (fid in text and len(text) >= 15000 and bool(re.search(r"RE:\s*FINAL\s*AIR", text[:4000])) and bool(re.search(r"Emissions?\s+Unit", text)) and bool(re.search(r"Terms\s+and\s+Conditions", text, re.I)))

def classify(text):
    """final | proposed_or_draft | revocation | study | short_letter (< 15,000 characters, never a permit by the lane's rule) | other. A large document that is `other` is one this lane could not classify: check.py fails on it."""
    head = text[:4000]
    if re.search(r"RE:\s*(?:PRELIMINARY\s+)?(?:PROPOSED|DRAFT)\b", head): return "proposed_or_draft"
    if re.search(r"RE:\s*FINAL[^\n]*REVOCATION", head): return "revocation"
    if re.search(r"RE:\s*FINAL\s*AIR", head): return "final"
    if re.search(r"Engineering\s+Study", text[:1500]): return "study"
    return "short_letter" if len(text) < 15000 else "other"

def inspectable(d):
    """False for a document with a large PDF and almost no text (a scan or an image): it cannot be read as 'no permit'. Classified letters (revocation, proposed, draft) are inspectable."""
    j = journal()[d]; t = doc_text(d)
    return classify(t) in ("revocation", "proposed_or_draft", "final") or not (j["bytes"] > 200000 and len(t) < 10000)

CAN18 = lb.S / "persist/pic18-permit-canary-2026-11-18"
def journal():
    """This lane's fetch journal plus the 2026-11-18 canary's (the carried sites' documents; Muse's manifest and that lane's store hold the same files)."""
    J = {}
    for src in (CAN18 / "fetch_journal_v2.jsonl", P / "fetch_journal.jsonl"):
        for l in open(src): d = json.loads(l); J[d["docid"]] = d
    return J

def stage_carried():
    """Copy the carried sites' stored permits (read on 2026-11-18) into this lane's store, sha256-checked against the canary's fetch journal. No fetch."""
    import shutil
    J = journal(); n = 0
    for r in read_csv(ROOT / "tasks/pic18-permit-canary-2026-11-18/screen.csv"):
        for d in [x for x in r["final_permit_docids"].split(";") if x]:
            for ext, key in (("pdf", "pdf_sha256"), ("txt", "text_sha256")):
                src = CAN18 / "docs" / f"{d}.{ext}"; dst = P / "docs" / f"{d}.{ext}"
                assert sha(src) == J[d][key], f"{d}.{ext}: sha256 differs from the fetch journal"
                if not dst.exists() or sha(dst) != J[d][key]: shutil.copy2(src, dst); n += 1
    return n

def screen_rows():
    """One row per canary site from the stored search hits and fetched documents: air IDs, documents listed, final permits whose printed Facility ID is one of the site's IDs."""
    hits = json.load(open(P / "search_hits_all.json")); J = journal(); out = []
    import fetch as FE
    canary = {c["site_id"] for c in read_csv(HERE / "canary_sites.csv")}
    for c in FE.targets():
        s = c["site_id"]; h = hits[s]; ids = c["air_ids"].split(";"); fids = [x["fid"] for x in h["searches"]]
        assert all(isinstance(x.get("n"), int) or "err" in x for x in h["searches"]), f"{s}: a portal search has no parsed result count"
        n_hits = sum(x.get("n") or 0 for x in h["searches"]); err = [x for x in h["searches"] if "err" in x]
        docs = [d for x in h["searches"] for d in x.get("hits", [])]; fetched = [d for d, _ in docs if d in J]
        fin = sorted({d for d in fetched if any(final_permit(doc_text(d), f) for f in fids)})
        if err: status = "search_failed"
        elif not n_hits: status = "air_record_no_document_found"
        elif not fin and any(inspectable(d) is False for d in fetched): status = "document_not_text_inspectable"
        elif not fin: status = "air_record_no_final_permit_in_newest_6"
        else: status = "retrievable_permit"
        out.append({"site_id": s, "set": "canary" if s in canary else "frame_extra", "echo_air_ids": c["air_ids"], "route": c["routes"], "edoc_documents_listed": n_hits, "docs_fetched": len(fetched), "final_permit_docids": ";".join(fin), "status": status})
    return out + carried_screen(canary)

def carried_screen(canary):
    """The 32 frame sites with an ID that were screened on 2026-11-18 (24 read, 8 searched with no final permit): status and documents from that screen, no new fetch."""
    old = {r["site_id"]: r for r in read_csv(ROOT / "tasks/pic18-permit-canary-2026-11-18/screen.csv")}; out = []
    for r in read_csv(HERE / "frame.csv"):
        s = r["site_id"]
        if not r["air_ids"] or s in canary or s not in old: continue
        o = old[s]; out.append({"site_id": s, "set": "carried_read_2026_11_18" if o["status"] == "retrievable_permit" else "searched_2026_11_18_no_permit", "echo_air_ids": r["air_ids"], "route": r["routes"],
                                "edoc_documents_listed": o["edoc_documents_listed"], "docs_fetched": o["docs_fetched"], "final_permit_docids": o["final_permit_docids"], "status": o["status"]})
    return out

def write_csv(name, rows):
    with open(HERE / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n", extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def loaded(scr):
    caps = {(r["site_id"], r["capability_type"], r["term"]) for r in read_csv(ROOT / "data/site_capabilities.csv")}
    V = json.load(open(HERE / "verdicts.json")); have = {r["site_id"] for r in scr}
    for s, v in json.load(open(ROOT / "tasks/pic18-permit-lane-2026-11-18/verdicts.json"))["sites"].items():   # the carried sites' readings, recomputed under today's rows
        if s in have and s not in V["sites"]: V["sites"][s] = v
    return dict(V=V, scr=scr, text=doc_text, caps=caps, **dict(zip(("sites", "orgs"), atlas())))

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
    c, n26, f, o = m["canary"], m["new_26"], m["full_frame_read"], m["outcome_line"]
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
        rows.append(f"| {r['site_id']} | {sc[r['site_id']]['set'].replace('_2026_11_18', '')} | {r['tier']} | {r['strict_bind']} | {terms} | {wr} | {r['verdict']}{(': ' + why) if r['verdict'] != 'VERIFIED' else ''} |")
    car = read_csv(HERE / "carried.csv"); ck = Counter((x["bind_2026_11_18"], x["bind_today"]) for x in car)
    changed = [x["site_id"] for x in car if x["bind_2026_11_18"] != x["bind_today"] or bool(x["near_format_only"]) != (x["hold_reason_2026_11_18"] == "near_bound")]
    sc2 = o["process_unknown_after_if"]; k1, k2, k3 = list(sc2.values()); wrote = ", ".join(sorted(o["planned_site_terms"]))
    return f"""# PIC-18 process from Ohio EPA air permits: full frame (58 sites); 2 writes, everything else holds and leads

Claim: atlas-w22-process-permits, controller-assigned, 2026-11-22 (owner pick "Ohio air permits"). Reuses the 2026-11-18 lane unchanged (`tasks/pic18-permit-lane-2026-11-18/`, owner ruling 2026-11-18b item 1) and applies the owner ruling of 2026-11-22 relayed by the controller: a permit emissions-unit description fills `processes` only when it **names** a process in the SCHEMA §3.1 vocabulary, quoted from the permit, for that site only; general equipment (mixer, blender, paint booth, station) fills nothing and is a hold; no equipment-implies-process mapping beyond the 2026-11-18 lane's. Generated by `build.py`; checked by `check.py`. **Data change: the `processes` cell of SITE-001078 and SITE-000140 and one evidence row each ({', '.join(r['evidence_id'] for r in read_csv(ROOT / 'data/evidence_sites_OH.csv') if r['created_by'] == WHO) or 'allocated at apply'}), appended at the end of `data/evidence_sites_OH.csv` (that shard is not id-sorted on main; the rows are not re-sorted into it). Nothing else under `data/`.** `python3 build.py --apply` writes them; `INPUTS.sha256` lists the permit PDF in the shared store.

First user: the Atlas integrator, who decides at the next wave review whether to take the follow-up rulings below. Non-use is a finding if that review has not taken or declined them.

## The frame (`frame.py`, recomputed by `check.py`)

**Unit: Atlas sites, state OH, county in PIC-18, `operating_status` active, tier A–C.** {fs['pic18_active_ac_sites']} sites; **{fs['frame_no_process_site_and_org']}** have no process at the site and none at the organization (blank street on {fs['frame_blank_street']}). **{fs['frame_with_air_id']} of those have an Ohio EPA air facility ID** ({fs['distinct_air_ids']} distinct IDs; two sites carry two, and one ID sits on two sites, below):

| Route | Sites with an ID |
|---|---|
| FRS registry link (the site's own, or organization-level when the organization has one frame site) -> lake `echo_air_facilities` | {fs['sites_with_id_from_frs']} |
| Lake `echo_air_facilities` (OH) row at the site's street (`derive_last_activity.same_street`) with the site's or organization's held name | {fs['sites_with_id_from_lake']} |
| FRS only / lake only / both | {fs['frs_only']} / {fs['lake_only']} / {fs['both']} |

The lake route adds **{fs['lake_only']}** sites FRS does not reach. **Name rule substituted:** the owner's corporate-words rule is not in the repo (the lake's `scripts/matching.py` arrives with PR #467), so the lake match uses `atlas.name_key` equality or the earlier lane's holder token rule; of the {fs['lake_matches_name_key_exact'] + fs['lake_matches_token_rule_only']} lake ID matches, **{fs['lake_matches_name_key_exact']}** are `name_key`-exact and **{fs['lake_matches_token_rule_only']}** token-rule only. It affects which IDs are searched, not any write (every permit is bound on its own printed holder). **{fs['same_street_name_mismatch_no_id']}** more frame sites match a lake row on street but not on name (a different operator at the address); not counted. The other {fs['frame_no_process_site_and_org'] - fs['frame_with_air_id']} frame sites are unreachable by this route.

Of the {fs['frame_with_air_id']}: **{fs['with_id_done_2026_11_18']}** were read on 2026-11-18 and are still without a process (re-bound today below; 9 of that lane's 33 left the frame because a process is now on record); **{fs['with_id_searched_2026_11_18_no_permit']}** were searched then with no final permit (6 zero hits, 2 with only short letters, SITE-000517's being revocation letters; Muse's re-download found the same); **{fs['with_id_new']}** are new: **25 drawn as the canary** (seed 20261122) and **1 more (SITE-002106)**, searched on the go with 0 documents returned.

**Shared ID, a dedupe lead (not a merge).** `OH0000000322002004` is on **SITE-000981** (Johns Manville, 49 Lockwood Road, Milan, ORG-000911) and on **SITE-001513** (Clevite Elastomers Technical Center, 33 Lockwood Rd, Milan, ORG-001462, a different organization and street number). The permit prints 49 Lockwood Road, so it can only bind SITE-000981; whether SITE-001513's FRS link is wrong or the two share a facility is for the integrator. The SITE-000981 scenario below carries that caveat. (The ID is in Muse's manifest; its permits for it were fetched in the 2026-11-18 canary and are the ones read here.)

Documents: Ohio EPA eDocument search by the 10-digit Facility ID, newest six non-draft, non-correspondence documents per ID, the earlier lane's route (`fetch.py`; no URL guessed). The two cited PDFs: SITE-000140's is in the shared store (`raw/permits-oh-air/2026-11-22/`, Muse's file, same sha256); SITE-001078's (document 3281747) is in controller storage only and is not yet in the store (listed in `INPUTS.sha256` as a comment). The 24 carried sites' documents are the earlier lane's stored files (sha256-checked against its fetch journal, copied into this lane's store; no re-fetch). PDFs and text are in controller storage with sha256 (`doc_hashes.json`); none is in the repo (cover letters name individuals).

**Repaired format miss.** The 2026-11-18 screen read `RE: FINAL AIR` with a required space, so permits from 2016 and earlier that print `RE: FINALAIR` were classed not final. `build.py` now accepts both and `check.py` fails on any large unclassified document. Effect: SITE-001434 gains a permit (mixers only; held). No other site's status changes.

## Result

| Measure (unit: sites) | Canary (25) | New frame read now (26) | Full frame (58: 26 new + 24 carried read + 8 searched) |
|---|---|---|---|
| Retrievable final permit with the printed Facility ID | **{pct(c['retrievable_permit_sites'], 25)}**; lake route {by_route['lake'][0]}/{by_route['lake'][1]}, FRS-linked {by_route['frs'][0]}/{by_route['frs'][1]} | {n26['retrievable_permit_sites']}/26 | {f['retrievable_permit_sites']}/58 |
| Not retrievable (availability facts, not absence) | {25 - c['retrievable_permit_sites']}: {c['status'].get('air_record_no_document_found', 0)} zero documents, {c['status'].get('air_record_no_final_permit_in_newest_6', 0)} only letters (revocation) or correspondence | {26 - n26['retrievable_permit_sites']} | {58 - f['retrievable_permit_sites']} |
| Strictly bound today (printed Facility ID, holder = Atlas legal or trade name, street, city) | **{pct(c['strict_bound_sites'], 25)}**; of retrievable {pct(c['strict_bound_sites'], c['retrievable_permit_sites'])} | {n26['strict_bound_sites']} | {f['strict_bound_sites']} |
| Written to `processes` (tier C, bound, a §3.1 process named at a unit) | **{pct(c['sites_with_process_written_to_processes'], 25)}**: {', '.join(c['process_sites']) or 'none'} | {n26['sites_with_process_written_to_processes']} | **{f['sites_with_process_written_to_processes']}**: {', '.join(f['process_sites'])} |
| Capability row only (tier A/B) | {c['sites_with_capability_row_only']} | {n26['sites_with_capability_row_only']} | {f['sites_with_capability_row_only']} |
| Held sites by reason | {c['held_sites_by_reason']} | {n26['held_sites_by_reason']} | {f['held_sites_by_reason']} |

**The 24 carried sites were re-bound on today's Atlas rows** (`carried.csv`; their documents from 2026-11-18, the earlier lane's newest permit rule): bound then/now {ck[('BOUND', 'BOUND')]} unchanged, {ck[('NOT_BOUND', 'BOUND')]} newly bound, {ck[('NOT_BOUND', 'NOT_BOUND')]} unchanged not bound, ruling-relevant changes at {', '.join(changed)}. The Atlas street, blank on 2026-11-18, has since been filled for **SITE-000140** (tier C; now bound, `P027, EPE Foam Extrusion Line` names `foam_extrusion` at a unit heading: a **write**), **SITE-001792** (tier B; bound; a synthetic rubber pilot plant, no process named: hold) and **SITE-001743** (tier A; now a format-only near-bind on `Pkwy`: hold). The rest of the carried sites keep their 2026-11-18 verdicts; the 2026-11-22 ruling changes none of them, because no other carried tier C site is bound with a named term.

**Outcome line this packet would give** (PIC-18 organization rows, process unknown, harness definition, recomputed on origin/main and on this head by `check.py` with the controller harness): **{o['process_unknown_before']} -> {o['process_unknown_after']} of {o['pic18_org_rows']}** (-{o['fall']}: {wrote}; each the only PIC-18 site of its organization). Only a `processes` cell on a tier C site moves it. Rulings that would add (owner rulings, none applied): a holder rule that also accepts the Atlas site name -> **{k1}** (SITE-001282, `compression_molding`); that plus a plant-suffix holder rule -> **{k2}** (SITE-000981, `rubber_calendering` and `rubber_extrusion`, a rubber roofing calender/extruder line; caveat above); opening the `processes` route to tier A/B sites with a bound, named unit-level term (SITE-000601, SITE-001888, SITE-001937, SITE-002124, SITE-002855) -> **{k3}** from the packet, upper bound.

## What this says

**The decision that moves the number most is whether the 2026-11-22 ruling lifts the 2026-11-14 rule that a `supports_C` term on a tier A/B record is a capability row only: {o['process_unknown_after']} versus {k3}.** The packet keeps the rule.

The route is real and thin. Of the 26 new sites {n26['retrievable_permit_sites']} have a permit, 7 bind, 1 writes. Of the 7 bound new sites, 4 state no polymer process (a resin and chemical blender, a metals recovery plant, an inorganic catalyst plant, a plastic-parts paint-booth line), 1 is a roofing line of general equipment, and 1 (foam board cutting, tier B) names a process with no capability destination. Ten of the 17 retrievable new sites fail the bind, 9 on form not identity (holder form 6, blank Atlas street 2, municipality 1). The bind rule is the larger loss. Frame size is the other: only {fs['frame_with_air_id']} of {fs['frame_no_process_site_and_org']} frame sites have an air ID.

Four sites whose only documents in the newest six are revocation letters (SITE-000035, SITE-000250, SITE-002087, 2015-2020, and SITE-000517 from the earlier pool) are a record-health lead, not a status finding (AGENTS §3).

## Per site (the 58 frame sites read; the 8 searched with no final permit are in `screen.csv`)

| Site | Set | Tier | Bind | §3.1 terms proposed | Write | Verdict |
|---|---|---|---|---|---|---|
{chr(10).join(rows)}

`proposals.csv` has every quote with its document, permit number, dates, bind, witness position, strength, route and hold reason; `sites.csv` the site grain. SITE-001078's other proposals: `laminating` held as equipment only ("Kawakami Laminator", a machine name) and `printing_decorating_plastics` held because the substrate is not stated. SITE-002106: the portal search returned 0 documents for its ID (an availability fact).

## Follow-up rulings (owner rulings; none applied). The earlier lane's three, restated with counts, and three new

Counts: earlier lane = its 33 retrievable sites; today = the 41 retrievable sites above (17 new + 24 carried).

1. **USPS abbreviations and a `Twp.` suffix bind.** Today: **SITE-000264, SITE-001743, SITE-002113** differ by format alone (3 of 41; SITE-001137 left the frame). Among the 17 new, none but SITE-001743's carried case; SITE-001399's `Pkwy` is one of two differences. Recommend yes, unchanged: none of the three has a tier C term to write (SITE-000264 calendering is tier A; SITE-001743 and SITE-002113 name none).
2. **A permit's `Permit Description` counts as a unit description at `supports_C`.** Today: 0 sites would change (SITE-000814 was the one, since filled elsewhere). Recommend yes, unchanged; it matters little. Note SITE-000140's permit description also states its foam extrusion line; the write rests on the unit heading, not on it.
3. **Capability terms and the tier A/B route.** Earlier: `compounding_unspecified`/`extrusion_unspecified` -> parents (1 site), `coating_applying` (2), `foam_molding_bead` (1). New: `foam_fabrication` (SITE-001937). As above, whether the named-process ruling lifts the tier A/B capability-only rule is the one that moves the number. Recommend lifting only for a unit-level named term at a bound site, as the scenario counts.
4. **NEW: holder-name form.** 6 of 17 retrievable new sites fail on the holder: 3 on the holder alone with street, city and Facility ID equal (`Johns Manville-Milan Plant` for `Johns Manville (Milan)`; `Ventra Sandusky, LLC` and `Ventra Salem, LLC` for `Ventra (Flex-N-Gate)`), 3 with a second difference (`The Lincoln Electric Company`, also municipality; `Tarkett USA Inc.` for `Tarkett North America`, also street form; `ASK Chemicals (formerly Ashland Chemical)` for `ASK Chemicals LP`, also municipality). Recommend: also accept the Atlas **site name** (text before the locality). It settles the two Ventra sites; Johns Manville, Lincoln, Tarkett and ASK stay held as organization-identity questions.
5. **NEW: blank Atlas street** (2 of 17 new: SITE-000220, SITE-001916; the permit prints a street, but the permit cannot supply the street it is tested against). Recommend: hold; fill the street from another source first (the three carried sites above were bound that way). {fs['frame_blank_street']} of the {fs['frame_no_process_site_and_org']} frame sites have a blank street.
6. **NEW: printed municipality differs from the Atlas city** at an equal street (SITE-001654 `Bedford` vs `Walton Hills`; SITE-000154 `Cleveland` vs `Euclid`; SITE-001434 `Cleveland` vs `Cuyahoga Heights`; the last two also differ on the holder). Recommend: hold; a postal city is not an identity.

## Self-refute

- Grain: {len(model['props'])} proposals; the two written terms are unit-level (a unit paragraph and a unit heading); none rests on a permit or facility description.
- Strength: both written terms are graded `list` (a one-line label or heading), so `supports_C`; no `supports_A` write.
- Equipment rule: 3 new quotes held as equipment only (a laminator, a rubber mixer, a roofing saturator line); resin blending, reactors, mixers and vinyl mixers carry no term; the two writes name their process in the unit text ("heated rolling and calendering operations"; "EPE Foam Extrusion Line").
- Stale input: the carried sites' binds were recomputed on today's Atlas rows after the first draft carried them from 2026-11-18; three changed (above).
- Attribution: every quote is the holder's own permit; none from a parent, customer or equipment maker. Binding: SITE-001937's two older permits print holder `Trans-foam 281 SW` and are not cited.

## Reproduction and checks

`uv run --with duckdb python tasks/pic18-process-permits-2026-11-22/frame.py` (frame), `python3 fetch.py draw|search|merge|docs` (network; resumable; `new_facility_ids.csv` lists IDs not in Muse's manifest), `python3 build.py`, and the named check `uv run --with duckdb python tasks/pic18-process-permits-2026-11-22/check.py`: recomputes the frame from the repo and the lake, the registered draw, the stored-permit hashes, the screen (failing on an unparsed search count or an unclassified large document), every proposal (the earlier lane's audit rules, imported), the carried re-bind, the outcome line against the controller harness, the data diff (none under `data/`), a privacy scan (emails, phones, every person name printed in the stored permits), then runs {EXPECTED} injected defects and fails unless each is caught by the rule meant for it, including a quote not in the stored text and a permit for another facility.

Not checked: permits beyond the newest six documents per ID; the 8 sites searched with no final permit (not re-searched); the 23 carried sites other than the three that changed (their 2026-11-18 readings carried, re-bound only); local-agency permits; whether any plant still runs the permitted equipment; units of unbound sites beyond headings and one term each; OCR of image-only permits (none found: the 5 sites with no final permit hold revocation letters or correspondence). A permit is a statement as of its issue date and never a status finding.
"""

def unknown_orgs(planned=None):
    """The outcome harness's definition (S/harness/pic18_unknown.py) over the working tree: PIC-18 organization rows (ids with an active OH PIC-18 tier A-C site) whose
    process is unknown at site and organization grain; `planned` = {site_id: [terms]} is unioned into the site cells first."""
    sys.path.insert(0, str(ROOT / "scripts")); from regions import PIC18
    import frame as F
    sites, orgs = F.atlas(); sites = {s["site_id"]: s for s in sites}; planned = planned or {}
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

def carried():
    """The 24 sites read on 2026-11-18 that are still in the frame: strict bind recomputed on today's Atlas rows from that lane's stored permits (its newest permit, as that lane did)."""
    old = {r["site_id"]: r for r in read_csv(ROOT / "tasks/pic18-permit-lane-2026-11-18/sites.csv")}
    scr18 = {r["site_id"]: r for r in read_csv(ROOT / "tasks/pic18-permit-canary-2026-11-18/screen.csv")}
    L18 = lb.S / "persist/pic18-permit-lane-2026-11-18/docs"; sites, orgs = atlas(); out = []
    for r in read_csv(HERE / "frame.csv"):
        s = r["site_id"]
        if r["done_2026_11_18"] != "Y": continue
        docs = scr18[s]["final_permit_docids"].split(";"); tx = {d: (L18 / f"{d}.txt").read_text() for d in docs}; hd = {d: header(tx[d]) for d in docs}
        newest = sorted(docs, key=lambda d: (cb.mdy(hd[d]["issue_date"]), d), reverse=True)[0]
        strict, near = lb.bind_near(hd[newest], sites[s], orgs[sites[s]["org_id"]], hd[newest]["facility_id"])
        out.append({"site_id": s, "tier": sites[s]["verification_tier"], "bind_2026_11_18": old[s]["strict_bind"], "bind_today": "BOUND" if not strict else "NOT_BOUND", "near_format_only": near,
                    "reasons_today": "; ".join(strict), "verdict_2026_11_18": old[s]["verdict"], "hold_reason_2026_11_18": old[s]["hold_reason"]})
    return out

WHO = lb.WHO

def evidence_rows(props, hashes, sites, first_id):
    """The 2026-11-18 lane's evidence row, with this lane's retrieval date and ruling. Only route == processes proposals become rows."""
    rows, i = [], first_id
    for p in props:
        if p["route"] != "processes": continue
        h = hashes[p["docid"]]
        note = (f"government_filing: Ohio EPA air permit {p['permit_number']}, issued {p['issue_date']}, expiry {p['expiry']}"
                + (f"; past its printed expiry on {AS_OF}, capped at supports_C" if p["expired"] == "Y" else "")
                + f"; Facility ID {header(doc_text(p['docid']))['facility_id']}; printed Facility ID, holder, street and city equal the Atlas site row; witness: {p['position'].replace('_', ' ')} "
                  f"({'a sentence stating the operation' if p['strength'] == 'supports_A' else 'a label, heading, table row or equipment list: a list item'}) that names the process; "
                  f"PDF sha256 {h['pdf_sha256']}; retrieved {h['fetched_utc']} (Ohio EPA eDocument search by the printed Facility ID), stored text re-read; term unioned into processes "
                  "(owner rulings 2026-11-18b item 1 and 2026-11-22: a permit unit description names a §3.1 process); a permit is a statement as of its issue date, not a status finding.")
        rows.append(dict(evidence_id=f"EVD-{i:06d}", record_table="sites", record_id=p["site_id"], claim_type="scope", claim_detail=f"processes={p['term']}; quote: {p['quote']}",
                         source_class="government_filing", source_ref=f"Ohio EPA air permit {p['permit_number']} for Facility ID {header(doc_text(p['docid']))['facility_id']}, issued {p['issue_date']} (eDocument docid {p['docid']})",
                         observed_date=p["issue_date"], tier_effect=p["strength"], created_by=WHO, address_role="", notes=note + f" Portal document: {URL}{p['docid']}")); i += 1
    return rows
lb.evidence_rows = evidence_rows

def lb_git_show(path):
    import frame as F
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{F.BASE}:{path}"], capture_output=True, text=True, check=True).stdout

def apply_data(model, scr):
    """Write the planned `processes` unions and their evidence rows (the 2026-11-18 lane's staged, verified, atomic apply). Capability and hold proposals write nothing."""
    plan = dict(model, props=[p for p in model["props"] if p["route"] == "processes"])
    out = lb.apply(plan, doc_hashes(scr), root=ROOT)
    # keep the shard's existing order: lb.apply sorts by id, but the shard on main is not id-sorted, so a sort would rewrite ~200 unrelated lines
    import io
    ev = ROOT / "data/evidence_sites_OH.csv"; base = lb_git_show("data/evidence_sites_OH.csv"); old = list(csv.DictReader(io.StringIO(base, newline=""))); ids = {r["evidence_id"] for r in old}
    now = read_csv(ev); fields = list(now[0]); mine = [r for r in now if r["evidence_id"] not in ids]
    lb.write_csv(ev, [dict(r) for r in old] + mine, fields)
    return out

def all_metrics(scr, model):
    canary = {r["site_id"] for r in scr if r["set"] == "canary"}; new26 = {r["site_id"] for r in scr if r["set"] in ("canary", "frame_extra")}
    return {"canary": metrics(*subset(scr, model, canary)), "new_26": metrics(*subset(scr, model, new26)), "full_frame_read": metrics(scr, model), "outcome_line": outcome(model)}

def main():
    stage_carried()
    scr = screen_rows(); write_csv("screen.csv", scr)
    model = model_of(scr)
    assert not model["viol"], model["viol"]
    write_csv("sites.csv", model["sites"]); write_csv("proposals.csv", model["props"])
    json.dump(doc_hashes(scr), open(HERE / "doc_hashes.json", "w"), indent=1, sort_keys=True)
    write_csv("carried.csv", carried())
    m = all_metrics(scr, model); json.dump(m, open(HERE / "metrics.json", "w"), indent=1)
    (HERE / "README.md").write_text(readme(scr, model, m)); print(json.dumps(m, indent=1)[:600])

if __name__ == "__main__":
    main()
    if "--apply" in sys.argv:
        scr = screen_rows(); print("applied (evidence rows, capability rows, site cells):", apply_data(model_of(scr), scr))
