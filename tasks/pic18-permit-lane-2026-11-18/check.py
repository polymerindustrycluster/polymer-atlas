"""Named check for the PIC-18 air-permit lane: python3 tasks/pic18-permit-lane-2026-11-18/check.py

Recomputes every published count from the stored permits, the Atlas rows and the canary screen; audits every proposal and every data change;
then proves the audit fails on every injected defect. Missing caches fail the run (a skipped check is not a pass).
"""
import copy, csv, glob, io, json, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import build as B
HERE, ROOT = B.HERE, B.ROOT
WRITE = ("processes", "capability")

def base_ref(): return B.git("merge-base", "HEAD", "origin/main").strip()
def rd(text): return list(csv.DictReader(io.StringIO(text, newline="")))

def audit_frame(scr):
    n = sum(r["status"] == "retrievable_permit" for r in scr)
    return [("FRAME", f"frame has {n} sites, expected {B.N_FRAME}")] if n != B.N_FRAME else []

def audit(props, sites, orgs, text=B.doc_text):
    """Independent rules over the published proposal rows. Returns [(rule, message)]."""
    v = []
    for p in props:
        s, d, t = p["site_id"], p["docid"], p["term"]; tx = text(d); st = sites[s]; org = orgs[st["org_id"]]; h = B.cb.header(tx)
        if not B.cb.in_order(p["quote"], tx): v.append(("QUOTE", f"{s}/{d}: quote not in the stored permit, in order: {p['quote'][:50]}"))
        if t and t not in B.PROCESSES: v.append(("TERM", f"{s}: {t} is not a §3.1 term"))
        if t and B.ANCILLARY.search(p["quote"]): v.append(("ANCILLARY", f"{s}: ancillary unit text mapped to {t}"))
        exp, guard = B.expiry(tx)
        if not guard: v.append(("EXPIRY_GUARD", f"{s}/{d}: an expiration is printed but not parsed"))
        if p["route"] in WRITE:
            if B.bind_near(h, st, org, h["facility_id"])[0]: v.append(("BIND", f"{s}/{d}: written proposal on a document that does not strictly bind"))
            if B.position(tx, p["quote"]) not in ("unit_heading", "unit_paragraph", "unit_table_row"): v.append(("WITNESS", f"{s}/{d}: not an emissions-unit description"))
            if st["verification_tier"] in ("A", "B") and p["route"] == "processes" and p["strength"] == "supports_C": v.append(("TIER_C", f"{s}: supports_C term written to processes on a tier {st['verification_tier']} site"))
            if p["route"] == "capability" and (p["strength"] != "supports_C" or B.CAP_MAP.get(t) != p["capability_term"] or p["capability_term"] not in B.CAP_PROCESS): v.append(("CAP", f"{s}: capability row not a supports_C §3.6 mapping"))
            if t not in B.CAP_MAP and p["route"] == "capability": v.append(("CAP", f"{s}: {t} has no §3.6 mapping"))
        if exp and exp < B.AS_OF and p["strength"] not in ("", "supports_C"): v.append(("EXPIRED", f"{s}/{d}: permit past its printed expiry {exp} proposed at {p['strength']}"))
        if p["strength"] == "supports_A" and (B.position(tx, p["quote"]) != "unit_paragraph" or p["grade"] != "narrative"): v.append(("STRENGTH", f"{s}: supports_A without a narrative unit paragraph"))
    return v

def audit_data(base_files, now_files, props):
    """base_files / now_files: {path: [rows]} for every data file that differs. Allowed: processes cell unions on planned site rows, new evidence/capability rows by this lane."""
    v = []; planned = {}
    for p in props:
        if p["route"] == "processes": planned.setdefault(p["site_id"], set()).add(p["term"])
    for path in set(base_files) | set(now_files):
        old, new = base_files.get(path, []), now_files.get(path, [])
        if path == "data/sites_OH.csv":
            idx = {r["site_id"]: r for r in old}
            if [r["site_id"] for r in old] != [r["site_id"] for r in new if r["site_id"] in idx] or len(old) != len(new): v.append(("ROWS", "sites_OH.csv rows added, removed or reordered"))
            for r in new:
                o = idx.get(r["site_id"])
                if not o: continue
                diff = [c for c in r if r[c] != o[c]]
                if diff and diff != ["processes"]: v.append(("CELLS", f"{r['site_id']}: cells other than processes changed: {diff}"))
                if diff == ["processes"]:
                    if r["site_id"] not in planned or not (set(o["processes"].split(";")) - {""}) <= set(r["processes"].split(";")): v.append(("CELLS", f"{r['site_id']}: unplanned or non-union processes change"))
                    elif set(r["processes"].split(";")) - set(o["processes"].split(";")) - {""} != planned[r["site_id"]] - set(o["processes"].split(";")): v.append(("CELLS", f"{r['site_id']}: processes terms differ from the plan"))
        elif path in ("data/evidence_sites_OH.csv", "data/site_capabilities.csv"):
            key = "evidence_id" if "evidence" in path else "capability_id"; have = {r[key]: r for r in old}
            for r in new:
                if r[key] in have:
                    if have[r[key]] != r: v.append(("ROWS", f"{path}: existing row {r[key]} changed"))
                elif r["created_by"] != B.WHO: v.append(("ROWS", f"{path}: new row {r[key]} not created by this lane"))
            if any(k not in {r[key] for r in new} for k in have): v.append(("ROWS", f"{path}: a row was removed"))
        else: v.append(("FILE", f"{path}: a data file this lane may not touch changed"))
    return v

def audit_written(now_files, props, sites, hashes):
    """The rows this lane wrote must equal the rows rebuilt from the proposals (site, term, strength, source, dates, notes), at the ids found."""
    v = []
    for path, key, build in (("data/evidence_sites_OH.csv", "evidence_id", B.evidence_rows), ("data/site_capabilities.csv", "capability_id", B.capability_rows)):
        mine = sorted((r for r in now_files.get(path, []) if r["created_by"] == B.WHO), key=lambda r: r[key])
        if not mine: continue
        want = build(props, hashes, sites, int(mine[0][key][4:]))
        if [dict(r) for r in mine] != want: v.append(("WRITTEN", f"{path}: the rows written differ from the rows rebuilt from proposals.csv"))
    return v

def audit_ids(new_ids, floor, what):
    low = [i for i in new_ids if i <= floor]
    return [("ID", f"{what}: ids {low} are not above the maximum {floor} at the base")] if low else []

def names_in_docs():
    """Person names printed in the cover-letter blocks of the stored permits, found at run time. Never written to a file."""
    bad = re.compile(r"Inc|LLC|Co\b|Corp|Ohio|Division|Agency|Protection|Environmental|Governor|Director|Street|Road|Drive|Avenue|Facility|Permit|Page|Final|Dear|Plant|Company|Products|Polymer", re.I)
    out = set()
    for p in glob.glob(str(B.LANE / "docs/*.txt")):
        for l in Path(p).read_text().split("\n")[:45]:
            c = re.split(r"\s{2,}", l.strip())[0]
            if re.fullmatch(r"[A-Z][a-z]+(?: [A-Z]\.?)? [A-Z][A-Za-z'-]+", c) and not bad.search(c): out.add(c)
    return out

def audit_privacy(files, names):
    v = []
    for name, txt in files.items():
        if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", txt): v.append(("PRIVACY", f"{name}: an email address"))
        if re.search(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", txt): v.append(("PRIVACY", f"{name}: a phone number"))
        v += [("PRIVACY", f"{name}: a person's name from a stored permit") for n in names if n in txt]
    return v

def task_files(): return {p.name: p.read_text() for p in sorted(HERE.iterdir()) if p.suffix in (".csv", ".json", ".md", ".py", ".txt") and p.name != "check.py"} | {"check.py": Path(__file__).read_text()}

def data_diff(base):
    files = [f for f in B.git("diff", "--name-only", base, "--", "data/").split("\n") if f]
    b = {f: rd(B.git("show", f"{base}:{f}")) for f in files if B.git("ls-tree", base, f).strip()}
    return b, {f: B.read_csv(ROOT / f) for f in files}

def main():
    hashes = json.load(open(HERE / "doc_hashes.json")); J = {}
    for l in open(B.CAN / "fetch_journal_v2.jsonl"): d = json.loads(l); J[d["docid"]] = d
    for d, h in hashes.items():
        for ext, key in (("pdf", "pdf_sha256"), ("txt", "text_sha256")):
            assert B.sha(B.LANE / "docs" / f"{d}.{ext}") == h[key] == J[d][key], f"{d}.{ext}: stored file differs from doc_hashes.json or the canary's fetch journal"
    inp = B.loaded(); model = B.compute(inp); sites, orgs = inp["sites"], inp["orgs"]; props = model["props"]
    assert not model["viol"], model["viol"]
    assert not audit_frame(inp["scr"]), "frame"
    for f, rows in (("sites.csv", model["sites"]), ("proposals.csv", props)):
        assert [dict(r) for r in B.read_csv(HERE / f)] == [{k: str(v) for k, v in r.items()} for r in rows], f"{f} differs from the recomputed rows (run build.py)"
    assert json.load(open(HERE / "metrics.json")) == B.metrics(model), "metrics.json differs from the recomputed metrics"
    # independent count of the frame from the canary's per-site document list (not from `status`): sites with >=1 final permit whose printed ID is in the ECHO air IDs
    rec = [r["site_id"] for r in B.cb.screen_rows() if r["status"] == "retrievable_permit"]   # the canary's own screen, rebuilt from its caches and the printed Facility IDs
    assert sorted(rec) == model["frame"] and len(rec) == B.N_FRAME == B.metrics(model)["frame_sites"], "frame yield differs from the independent recount"
    assert not audit(props, sites, orgs), audit(props, sites, orgs)
    base = base_ref(); bf, nf = data_diff(base)
    ev_files = [f for f in B.git("ls-tree", "-r", "--name-only", base, "data/").split("\n") if re.match(r"data/evidence_.*\.csv", f)]
    ev_base_max = max(int(r["evidence_id"][4:]) for f in ev_files for r in rd(B.git("show", f"{base}:{f}")))
    cap_base_max = max(int(r["capability_id"][4:]) for r in rd(B.git("show", f"{base}:data/site_capabilities.csv")))
    mine_ev = [int(r["evidence_id"][4:]) for r in nf.get("data/evidence_sites_OH.csv", []) if r["created_by"] == B.WHO]
    mine_cp = [int(r["capability_id"][4:]) for r in nf.get("data/site_capabilities.csv", []) if r["created_by"] == B.WHO]
    others_ev = max([int(r["evidence_id"][4:]) for p in glob.glob(str(ROOT / "data/evidence_*.csv")) for r in B.read_csv(p) if r["created_by"] != B.WHO] + [ev_base_max])
    assert not audit_data(bf, nf, props), audit_data(bf, nf, props)
    assert not audit_written(nf, props, sites, hashes), "written rows differ from the plan"
    assert not audit_ids(mine_ev, others_ev, "evidence") and not audit_ids(mine_cp, cap_base_max, "capability")
    n_ev = sum(p["route"] == "processes" for p in props); n_cp = sum(p["route"] == "capability" for p in props)
    assert len(mine_ev) in (0, n_ev) and len(mine_cp) in (0, n_cp), f"partial apply: {len(mine_ev)}/{n_ev} evidence rows, {len(mine_cp)}/{n_cp} capability rows"
    names = names_in_docs(); assert names, "no person names found in the stored permits: the privacy injection cannot run"
    assert not audit_privacy(task_files(), names), audit_privacy(task_files(), names)
    # ------------------------------------------------------------------------------------------------------------ injected defects
    def one(rule, mut, kind="props"):
        P = copy.deepcopy(props); S2, O2 = copy.deepcopy(sites), orgs
        if kind == "props":
            r = mut(P, S2) or P; got = audit(r, S2, O2)
        elif kind == "frame": got = audit_frame(mut(copy.deepcopy(inp["scr"])))
        elif kind == "data": got = audit_data(*mut(copy.deepcopy(bf), copy.deepcopy(nf)), props)
        elif kind == "written": got = audit_written(mut(copy.deepcopy(nf)), props, sites, hashes)
        elif kind == "ids": got = audit_ids(*mut())
        elif kind == "privacy": got = audit_privacy(mut(), names)
        assert any(g[0] == rule for g in got), f"injected defect {rule} was NOT caught: {got[:3]}"
        return rule
    def row(P, **m):
        return next(p for p in P if all(p[k] == v for k, v in m.items()))
    def scramble(P, S2):
        p = row(P, site_id="SITE-000664"); w = p["quote"].split(); p["quote"] = " ".join(w[3:6] + w[0:3] + w[6:])
    def inject_site_bound(P, S2):  # an unbound site applied: turn the near-bound site's lead into a written proposal
        p = row(P, site_id="SITE-000264"); p["route"] = "capability"; p["capability_term"] = "calendering"
    def blank_street(P, S2): S2["SITE-000248"]["street_address"] = "9999 Nowhere Rd";
    done = [
        one("QUOTE", lambda P, S2: row(P, site_id="SITE-000248").update(quote="Polyester gelcoat spray up booth for epoxy flooring.")),
        one("QUOTE", scramble),
        one("TERM", lambda P, S2: row(P, site_id="SITE-000248").update(term="composites_spray_up_fake")),
        one("ANCILLARY", lambda P, S2: row(P, site_id="SITE-000590").update(term="coating_applying", route="processes", strength="supports_C")),
        one("BIND", inject_site_bound),
        one("BIND", blank_street),
        one("TIER_C", lambda P, S2: row(P, site_id="SITE-001530", term="coating_formulation").update(route="processes")),
        one("EXPIRED", lambda P, S2: row(P, site_id="SITE-000238", term="composites_spray_up").update(strength="supports_A")),
    ]
    sites_now = nf.get("data/sites_OH.csv") or B.read_csv(ROOT / "data/sites_OH.csv"); sites_base = bf.get("data/sites_OH.csv") or rd(B.git("show", f"{base}:data/sites_OH.csv"))
    def cell_defect(b, n):
        b = {"data/sites_OH.csv": copy.deepcopy(sites_base)}; n = {"data/sites_OH.csv": copy.deepcopy(sites_base)}; n["data/sites_OH.csv"][5]["street_address"] = "tampered"; return b, n
    def row_defect(b, n):
        b = {"data/evidence_sites_OH.csv": rd(B.git("show", f"{base}:data/evidence_sites_OH.csv"))}; n = {"data/evidence_sites_OH.csv": copy.deepcopy(b["data/evidence_sites_OH.csv"])}; n["data/evidence_sites_OH.csv"][3]["notes"] = "edited"; return b, n
    def flip_tier(n):
        i = next(i for i, r in enumerate(n["data/evidence_sites_OH.csv"]) if r["created_by"] == B.WHO and r["record_id"] == "SITE-000238"); n["data/evidence_sites_OH.csv"][i]["tier_effect"] = "supports_A"; return n
    done += [one("WITNESS", lambda P, S2: row(P, site_id="SITE-000814").update(route="processes", strength="supports_C")),
             one("WRITTEN", flip_tier, "written"), one("CELLS", cell_defect, "data"), one("ROWS", row_defect, "data"),
             one("ID", lambda: ([ev_base_max], ev_base_max, "evidence"), "ids"),
             one("PRIVACY", lambda: {"README.md": "contact " + sorted(names)[0] + " about the permit"}, "privacy"),
             one("PRIVACY", lambda: {"README.md": "write to someone" + chr(64) + "example.com"}, "privacy"),
             one("FRAME", lambda scr: [dict(r, status="no_air_record") if r["site_id"] == "SITE-000590" else r for r in scr], "frame")]
    print(f"ok: frame {B.N_FRAME} (independent count agrees); strict-bound {B.metrics(model)['strict_bound_sites']}, near-bound {B.metrics(model)['near_bound_sites']}; "
          f"{n_ev} evidence rows, {n_cp} capability rows planned, {len(mine_ev)}/{len(mine_cp)} applied; {len([d for d in done if d])} injected defects all caught")

if __name__ == "__main__": main()
