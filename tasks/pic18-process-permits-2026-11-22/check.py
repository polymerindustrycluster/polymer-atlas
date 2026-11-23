"""Named check for the PIC-18 process-permits canary (2026-11-22): uv run --with duckdb python tasks/pic18-process-permits-2026-11-22/check.py

Recomputes every published file from the stored permits, the Atlas rows and the lake; audits every proposal with the 2026-11-18 lane's own audit rules
(imported, not copied); then proves the audit fails on injected defects, among them a quote that is not in the stored text and a permit for another
facility. A missing cache, a missing lake or a missing duckdb fails the run (a skipped check is not a pass).
"""
import copy, csv, importlib.util, json, random, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import build as B, frame as F
sys.path.insert(0, str(B.ROOT / "scripts")); from regions import PIC18
lb, cb, P = B.lb, B.cb, B.P
sys.modules["build"] = lb   # the lane's check.py does `import build as B`; hand it the (re-pointed) lane build module
_spec = importlib.util.spec_from_file_location("lane_check", B.ROOT / "tasks/pic18-permit-lane-2026-11-18/check.py"); lc = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(lc)
_corp = lc.company_corpus
def _corp_plus_sites():
    """The lane's corpus of Ohio organization names, plus the frame sites' names: a two-word site name ("Ventra Salem") is not a person."""
    ids = {r["site_id"] for r in B.read_csv(HERE / "frame.csv")}
    return _corp() + " | " + " | ".join(s["site_name"].lower() for i, s in B.atlas()[0].items() if i in ids)
lc.company_corpus = _corp_plus_sites
EXPECTED_DEFECTS = 13   # README reads this number

def task_files(): return {p.name: p.read_text() for p in sorted(HERE.iterdir()) if p.suffix in (".csv", ".json", ".md", ".py", ".txt") and p.name != "check.py"} | {"check.py": Path(__file__).read_text()}
def same(a, b): return [{k: str(v) for k, v in r.items()} for r in a] == [{k: str(v) for k, v in r.items()} for r in b]

def main():
    # 1. frame: recomputed from the repo tree and the lake, must equal the published frame.csv and frame_stats.json; the canary is the registered draw
    rows, stats = F.compute()
    assert same(rows, B.read_csv(HERE / "frame.csv")), "frame.csv differs from the recomputed frame (run frame.py)"
    assert stats == json.load(open(HERE / "frame_stats.json")), "frame_stats.json differs from the recomputed stats"
    import fetch as FE
    new = FE.new_frame(); canary = sorted(r["site_id"] for r in B.read_csv(HERE / "canary_sites.csv"))
    assert canary == sorted(random.Random(FE.SEED).sample(new, min(FE.N, len(new)))) and len(canary) == min(FE.N, len(new)), "canary is not random.Random(20261122).sample(sorted(new frame), 25)"
    assert stats["with_id_new"] == len(new), "new-frame count differs from frame_stats"
    # 2. stored permits: hashes equal the fetch journal and doc_hashes.json
    scr = B.screen_rows(); assert same(scr, B.read_csv(HERE / "screen.csv")), "screen.csv differs from the recomputed screen"
    hashes = B.doc_hashes(scr); assert json.load(open(HERE / "doc_hashes.json")) == hashes, "doc_hashes.json differs from the stored permits"
    model = B.model_of(scr); inp = B.loaded(scr); sites, orgs, props = inp["sites"], inp["orgs"], model["props"]
    assert not model["viol"], model["viol"]
    assert same(B.read_csv(HERE / "sites.csv"), model["sites"]) and same(B.read_csv(HERE / "proposals.csv"), props), "sites.csv or proposals.csv differs from the recomputed rows (run build.py)"
    assert json.load(open(HERE / "metrics.json")) == B.all_metrics(scr, model), "metrics.json differs from the recomputed metrics"
    # outcome line against the controller's harness (an independent implementation) at the merge-base (origin/main) and at HEAD, and an independent count of the fall
    o = json.load(open(HERE / "metrics.json"))["outcome_line"]
    def harness(ref):
        h = subprocess.run([sys.executable, str(B.lb.S / "harness/pic18_unknown.py"), str(B.ROOT), ref], capture_output=True, text=True, check=True).stdout
        mm = re.search(r"org rows=(\d+) proc_unknown=(\d+)", h); assert mm, h; return int(mm[1]), int(mm[2])
    base_ref = F.BASE; hb = harness(base_ref); hh = harness("HEAD")
    assert hb == (o["pic18_org_rows"], o["process_unknown_before"]), f"outcome baseline differs from the harness at origin/main: {hb}"
    applied = bool(subprocess.run(["git", "-C", str(B.ROOT), "diff", "--name-only", base_ref, "HEAD", "--", "data/"], capture_output=True, text=True, check=True).stdout.strip())
    assert hh == (o["pic18_org_rows"], o["process_unknown_after"] if applied else o["process_unknown_before"]), f"outcome at HEAD differs from the harness: {hh} (applied={applied})"
    s0, o0 = F.atlas(); cur = {}
    for s in s0:
        if s["state"] == "OH" and s["county"] in PIC18 and s["operating_status"] == "active" and s["verification_tier"] in ("A", "B", "C"): cur.setdefault(s["org_id"], []).append(s)
    planned_orgs = {sites[s]["org_id"] for s in o["planned_site_terms"]}
    fall = sum(1 for oid in planned_orgs if oid in cur and not any((x["processes"] or "").strip(" ;") for x in cur[oid]) and not (o0.get(oid, {}).get("processes") or "").strip(" ;"))
    assert fall == o["fall"] == o["process_unknown_before"] - o["process_unknown_after"], f"outcome fall {o['fall']} differs from the independent count {fall}"
    # independent recount of the retrievable set: a site is retrievable when a stored final permit prints one of the site's own Facility IDs
    ids = {r["site_id"]: {a[-10:] for a in r["air_ids"].split(";")} for r in rows if r["air_ids"]}
    allsites = [t["site_id"] for t in FE.targets()]
    rec = sorted(s for s in allsites if any(B.final_permit(B.doc_text(d), f) and B.header(B.doc_text(d))["facility_id"] in ids[s] for x in [json.load(open(P / "search_hits_all.json"))[s]]
                                          for q in x["searches"] for d, _ in q.get("hits", []) if (P / "docs" / f"{d}.txt").exists() for f in [q["fid"]]))
    new26 = {t["site_id"] for t in FE.targets()}
    assert rec == sorted(s for s in model["frame"] if s in new26), f"retrievable recount {len(rec)} differs from the build's new-site frame"
    assert same(B.read_csv(HERE / "carried.csv"), B.carried()), "carried.csv differs from the re-bind of the carried sites on today's Atlas rows (run build.py)"
    carried = B.read_csv(HERE / "carried.csv"); scr_c = {r["site_id"] for r in scr if r["set"] == "carried_read_2026_11_18"}
    assert {x["site_id"] for x in carried} == scr_c and scr_c <= set(model["frame"]) and len(model["frame"]) == len(rec) + len(scr_c), "carried sites differ from the frame's carried set"
    # no silent pass: every fetched document is classified; a large one that is not a permit, a letter, a draft or a study fails the run
    Hh = json.load(open(P / "search_hits_all.json")); Jj = B.journal(); kinds = {}
    for s_, v_ in Hh.items():
        for q_ in v_["searches"]:
            for d_, _t in q_.get("hits", []):
                if d_ in Jj: kinds[d_] = B.classify(B.doc_text(d_))
    assert kinds and "other" not in kinds.values(), f"unclassified large documents: {[d for d, k in kinds.items() if k == 'other']}"
    assert all(isinstance(q_.get("n"), int) or "err" in q_ for v_ in Hh.values() for q_ in v_["searches"]), "a portal search has no parsed result count"
    # 3. audits (the earlier lane's rules): quote in stored text, §3.1 term, ancillary, bind, witness, tier, expiry, strength, owner holds
    assert not lc.audit(props, sites, orgs), lc.audit(props, sites, orgs)
    lb.N_FRAME = len(model["frame"]); assert not lc.audit_frame(scr), "frame"
    link = [{"site_id": r["site_id"], "echo_air_ids": r["echo_air_ids"]} for r in scr]
    assert not lc.audit_manifest(hashes, B.doc_text, link), lc.audit_manifest(hashes, B.doc_text, link)
    assert {p["route"] for p in props} <= {"processes", "capability", "already_held", "hold", "no_term"}
    base = F.BASE; planned = [p for p in props if p["route"] == "processes"]
    bf, nf = lc.data_diff(base)
    assert not lc.audit_data(bf, nf, planned), lc.audit_data(bf, nf, planned)   # only the planned `processes` unions on planned site rows, and new evidence rows by this lane
    assert not lc.audit_written(nf, planned, sites, hashes), "the rows written differ from the rows rebuilt from proposals.csv"
    ev_base = max(int(r["evidence_id"][4:]) for f_ in lb.git("ls-tree", "-r", "--name-only", base, "data/").split("\n") if re.match(r"data/evidence_.*\.csv", f_) for r in lc.rd(lb.git("show", f"{base}:{f_}")))
    mine = [int(r["evidence_id"][4:]) for r in nf.get("data/evidence_sites_OH.csv", []) if r["created_by"] == B.WHO]
    assert not lc.audit_ids(mine, ev_base, "evidence"), "evidence ids are not above the base maximum"
    if applied:
        sites_now, ev_now, cap_now = (B.read_csv(B.ROOT / f_) for f_ in ("data/sites_OH.csv", "data/evidence_sites_OH.csv", "data/site_capabilities.csv"))
        assert not lc.audit_complete(sites_now, ev_now, cap_now, planned), lc.audit_complete(sites_now, ev_now, cap_now, planned)
        assert len(mine) == len(planned) == 2, f"{len(mine)} evidence rows for {len(planned)} planned writes"
    assert not any(f_ not in ("data/sites_OH.csv", "data/evidence_sites_OH.csv") for f_ in nf), f"unexpected data files changed: {sorted(nf)}"
    names = lc.names_in_docs(); sig = lc.signatories(); assert names and sig and sig <= names, "the privacy scan must know every signatory printed in the stored permits"
    assert not lc.audit_privacy(task_files(), names), f"{len(lc.audit_privacy(task_files(), names))} privacy findings"
    # 4. injected defects: every one must be caught, by the rule that exists for it
    def row(Pp, **m): return next(p for p in Pp if all(p[k] == v for k, v in m.items()))
    def one(rule, mut, kind="props", expect=None):
        Pp = copy.deepcopy(props); S2 = copy.deepcopy(sites)
        if kind == "props": got = lc.audit(mut(Pp, S2) or Pp, S2, orgs)
        elif kind == "manifest": got = lc.audit_manifest(mut(copy.deepcopy(hashes)), B.doc_text, link)
        elif kind == "privacy": got = lc.audit_privacy(mut(), names)
        elif kind == "frame": got = lc.audit_frame(mut(copy.deepcopy(scr)))
        elif kind == "compute": got = [("COMPUTE", v) for v in mut()]
        assert any(g[0] == rule and (expect is None or expect in str(g[1])) for g in got), f"injected defect {rule} ({expect}) was NOT caught by its own rule: {got[:3]}"
        return rule
    written = [p for p in props if p["route"] in ("processes", "capability")] or [p for p in props if p["bind_doc"] == "BOUND" and p["term"]]
    assert written, "no bound proposal to plant defects on"
    other = next(h for h in hashes.values() if h["site_id"] != written[0]["site_id"]); w0 = written[0]["site_id"]; planted = "Polyester gelcoat spray up booth planted by the check that no permit prints."
    def swap_doc():   # a permit for another facility cited for this site
        d = next(d for d, h in hashes.items() if h["facility_id"] not in ids[w0]); return d
    def wrong_facility_screen():
        scr2 = copy.deepcopy(scr); r0 = next(r for r in scr2 if r["site_id"] == w0); r0["final_permit_docids"] = swap_doc(); inp2 = B.loaded(scr2)
        lb.N_FRAME = sum(r["status"] == "retrievable_permit" for r in scr2); return lb.compute(inp2)["viol"]
    def wrong_facility_verdict():
        inp2 = copy.deepcopy(inp); inp2["V"]["sites"][w0]["quotes"][0]["doc"] = swap_doc(); lb.N_FRAME = len(model["frame"]); return lb.compute(inp2)["viol"]
    def unseen_term():
        inp2 = copy.deepcopy(inp); inp2["V"]["sites"][w0]["quotes"][0]["terms"] = ["not_a_schema_term"]; lb.N_FRAME = len(model["frame"]); return lb.compute(inp2)["viol"]
    def planted_quote_verdict():
        inp2 = copy.deepcopy(inp); inp2["V"]["sites"][w0]["quotes"][0]["quote"] = planted; lb.N_FRAME = len(model["frame"]); return lb.compute(inp2)["viol"]
    done = [
        one("QUOTE", lambda Pp, S2: row(Pp, site_id=w0).update(quote=planted)),
        one("COMPUTE", planted_quote_verdict, "compute", "quote not found in order"),
        one("COMPUTE", wrong_facility_screen, "compute", "printed Facility IDs"),
        one("COMPUTE", wrong_facility_verdict, "compute", "is not one of the site's final permits"),
        one("COMPUTE", unseen_term, "compute", "is not in SCHEMA §3.1"),
        one("BIND", lambda Pp, S2: S2[w0].update(street_address="9999 Nowhere Rd")),
        one("TERM", lambda Pp, S2: row(Pp, site_id=w0).update(term="not_a_schema_term")),
        one("MANIFEST", lambda h: h[next(d for d, x in h.items() if x["site_id"] == w0)].update(facility_id="0000000000") or h, "manifest"),
        one("MANIFEST", lambda h: h[next(d for d, x in h.items() if x["site_id"] == w0)].update(site_id=other["site_id"]) or h, "manifest"),
        one("PRIVACY", lambda: {"README.md": "contact " + sorted(names)[0] + " about the permit"}, "privacy"),
        one("PRIVACY", lambda: {"README.md": "signed by " + sorted(sig)[0]}, "privacy"),
        one("PRIVACY", lambda: {"README.md": "write to someone" + chr(64) + "example.com"}, "privacy"),
        one("FRAME", lambda s: [dict(r, status="no_air_record") if r["site_id"] == w0 else r for r in s], "frame")]
    one_c = [d for d in done if d]; assert len(one_c) == EXPECTED_DEFECTS, f"{len(one_c)} injected defects run, EXPECTED_DEFECTS says {EXPECTED_DEFECTS}"
    m = B.all_metrics(scr, model); f = m["full_frame_read"]
    print(f"ok: frame {stats['frame_with_air_id']} sites with an air ID ({stats['with_id_new']} new, all read); canary {len(canary)}; retrievable {f['retrievable_permit_sites']}; strict-bound {f['strict_bound_sites']}; "
          f"any fill {f['sites_with_any_fill']}; outcome line {o['process_unknown_before']} -> {o['process_unknown_after']}; {len(one_c)} injected defects all caught")

if __name__ == "__main__": main()
