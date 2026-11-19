"""Named check for the Permit re-score for owner ruling 2026-11-19b item 1 (rubber_extrusion -> extrusion): python3 tasks/permit-rubber-extrusion-2026-11-19b/check.py

Recomputes every published count from the stored permits, the Atlas rows and the canary screen; audits every proposal and every data change;
then proves the audit fails on every injected defect. Missing caches fail the run (a skipped check is not a pass).
"""
import copy, csv, glob, io, json, os, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import build as B
HERE, ROOT = B.HERE, B.ROOT
WRITE = ("processes", "capability")
# independent reference for the one authorized write: PR #402's reviewed witness (a second copy; build.py holds its own)
REF_WRITE = ("SITE-000264", "1315096", "Renewal PTIO for banbury mixers, mills, calenders, mixing tanks, extruder, and rotocure used to fabricated rubber membrane products for liners and tanks.")
SECTION_HEADING = "Permits for the following Emissions Unit(s) or groups of Emissions Units are in this document as indicated below:"
PAIR_RULE = not os.environ.get("CHECK_DISABLE_PAIR_RULE")   # the env var exists only to show the pair injections go green without the rule
EXPECTED_DEFECTS = 35   # README reads this number

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
        if t and B.is_ancillary(tx, p["quote"], B.position(tx, p["quote"])): v.append(("ANCILLARY", f"{s}: ancillary unit text mapped to {t}"))
        exp, guard = B.expiry(tx)
        if not guard: v.append(("EXPIRY_GUARD", f"{s}/{d}: an expiration is printed but not parsed"))
        if p["route"] in WRITE:
            strict, near = B.bind_near(h, st, org, h["facility_id"])
            if strict and not near: v.append(("BIND", f"{s}/{d}: written proposal on a document that does not bind (P2: only an abbreviation or Twp. suffix may differ)"))
            if B.position(tx, p["quote"]) not in ("unit_heading", "unit_paragraph", "unit_table_row", "permit_description"): v.append(("WITNESS", f"{s}/{d}: not an emissions-unit description or a Permit Description field"))
            if st["verification_tier"] in ("A", "B") and p["route"] == "processes" and p["strength"] == "supports_C": v.append(("TIER_C", f"{s}: supports_C term written to processes on a tier {st['verification_tier']} site"))
            if p["route"] == "capability" and (p["strength"] != "supports_C" or B.CAP_MAP.get(t) != p["capability_term"] or p["capability_term"] not in B.CAP_PROCESS): v.append(("CAP", f"{s}: capability row not a supports_C §3.6 mapping"))
            if t not in B.CAP_MAP and p["route"] == "capability": v.append(("CAP", f"{s}: {t} has no §3.6 mapping"))
        if B.position(tx, p["quote"]) == "permit_description" and p["strength"] not in ("", "supports_C"): v.append(("PD_STRENGTH", f"{s}/{d}: a Permit Description witness proposed at {p['strength']}, above supports_C"))
        if exp and exp < B.AS_OF and p["strength"] not in ("", "supports_C"): v.append(("EXPIRED", f"{s}/{d}: permit past its printed expiry {exp} proposed at {p['strength']}"))
        if p["strength"] == "supports_A" and (B.position(tx, p["quote"]) != "unit_paragraph" or p["grade"] != "narrative"): v.append(("STRENGTH", f"{s}: supports_A without a narrative unit paragraph"))
    if PAIR_RULE:   # the hold binds the (site, term) pair across every proposal, not only the row that carries the flag
        hp = B.held_pairs(props)
        v += [("OWNER_HOLD", f"{p['site_id']}/{p['term']}: a pair held for an owner ruling has a proposal routed to a write") for p in props if (p["site_id"], p["term"]) in hp and p["route"] != "hold"]
    v += [("PINNED", f"{p['site_id']}: the rubber_extrusion write is not the reviewed witness") for p in props
          if p["term"] == "rubber_extrusion" and p["route"] in WRITE and (p["site_id"], p["docid"], p["quote"]) != REF_WRITE]
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
            planned_n = sum(p["route"] == ("processes" if "evidence" in path else "capability") for p in props)
            if sum(r[key] not in have for r in new) > planned_n: v.append(("ROWS", f"{path}: more new rows than the plan ({planned_n})"))
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

BAD = re.compile(r"Inc|LLC|Co\b|Corp|Ohio|Division|Agency|Protection|Environmental|Governor|Director|Street|Road|Drive|Avenue|Facility|Permit|Page|Final|Dear|Plant|Company|Products|Polymer|"
                     r"Commission|Appeals|Review|Section|Chief|Office|District|Air|Pollution|Control|Quality|Management|Treasurer|Attorney|General|Enforcement|Fee|Date|Type|Unit|Emissions|Terms|Conditions|Table|Rule|Title|Part", re.I)
NAME = r"[A-Z][a-z]+(?: [A-Z]\.?)? [A-Z][A-Za-z'-]+"
def name_of(line):
    """The person name a line carries, if it is a name optionally followed by a comma and credentials ('Name, P.E.'), else ''."""
    seg = re.split(r"\s{2,}", line.strip())[0].rstrip(",")
    seg = re.sub(r",\s*[A-Za-z][A-Za-z.]*(?:,\s*[A-Za-z][A-Za-z.]*)*$", "", seg)
    return seg if re.fullmatch(NAME, seg) else ""

def company_corpus():
    """Lower-cased legal and trade names of the Ohio organizations: a two-word company name ("Plymouth Foam") is not a person."""
    sites, orgs = B.atlas(); oh = {s["org_id"] for s in sites.values() if s["state"] == "OH"}
    return " | ".join((o["legal_name"] + ";" + o["trade_names"]).lower() for o in orgs.values() if o["org_id"] in oh)

def names_in_docs():
    """Person names printed anywhere in the stored permits (cover-letter blocks, signatures with credentials), found at run time. Never written to a file or printed."""
    out = set(); corpus = company_corpus()
    for p in glob.glob(str(B.LANE / "docs/*.txt")):
        for l in Path(p).read_text().split("\n"):
            n = name_of(l)
            if n and not BAD.search(n) and n.lower() not in corpus: out.add(n)
    return out

TITLE = re.compile(r"\b(Chief|Manager|Supervisor|Engineer|Coordinator|Administrator|Specialist|Inspector)\b")
def signatories():
    """People printed as signatories: the name lines after 'Sincerely', and the name line directly above a title line. Found at run time, never printed."""
    out = set(); corpus = company_corpus()
    for p in glob.glob(str(B.LANE / "docs/*.txt")):
        L = Path(p).read_text().split("\n")
        for i, l in enumerate(L):
            if re.match(r"\s*Sincerely", l): out |= {n for n in (name_of(x) for x in L[i + 1:i + 14] if x.strip()) if n and not BAD.search(n) and n.lower() not in corpus}
            elif TITLE.search(l) and i:
                prev = next((L[k] for k in range(i - 1, max(0, i - 3), -1) if L[k].strip()), "")
                if name_of(prev) and not BAD.search(name_of(prev)) and name_of(prev).lower() not in corpus and len(l.strip()) < 80: out.add(name_of(prev))
    return out

def audit_complete(sites_now, ev_now, cap_now, props):
    """The applied state must equal the plan whatever a file's diff against the base looks like: every planned cell, and exactly the planned new rows."""
    v = []; cells = {r["site_id"]: set(r["processes"].split(";")) for r in sites_now}
    for p in props:
        if p["route"] == "processes" and p["term"] not in cells.get(p["site_id"], set()): v.append(("COMPLETE", f"{p['site_id']}: planned term {p['term']} is not in the processes cell"))
    n_ev = sum(p["route"] == "processes" for p in props); n_cp = sum(p["route"] == "capability" for p in props)
    mine_ev = [r for r in ev_now if r["created_by"] == B.WHO]; mine_cp = [r for r in cap_now if r["created_by"] == B.WHO]
    if len(mine_ev) != n_ev or len(mine_cp) != n_cp: v.append(("COMPLETE", f"{len(mine_ev)}/{n_ev} evidence rows and {len(mine_cp)}/{n_cp} capability rows applied"))
    if PAIR_RULE:
        hp = B.held_pairs(props)
        v += [("OWNER_HOLD", f"{s}: held term {t} is in the processes cell") for (s, t) in hp if t in cells.get(s, set())]
        v += [("OWNER_HOLD", f"{s}: an evidence row supports held term {t}") for (s, t) in hp for r in ev_now if r["record_id"] == s and r["claim_detail"].startswith(f"processes={t};")]
    return v

def audit_manifest(hashes, text, scr):
    """Printed Facility ID, derived from the hashed text, equals the manifest's and one of the site's ECHO-linked IDs."""
    v = []; link = {r["site_id"]: {x[-10:] for x in re.split(r"[;\s]+", r["echo_air_ids"]) if x} for r in scr}
    for d, h in hashes.items():
        fid = B.header(text(d))["facility_id"]
        if h["facility_id"] != fid: v.append(("MANIFEST", f"{d}: manifest Facility ID differs from the printed one"))
        if fid not in link.get(h["site_id"], set()): v.append(("MANIFEST", f"{d}: printed Facility ID is not one linked to {h['site_id']}"))
    return v

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

def lane_state_ok(data, props, names):
    """Invariant after any cut: no planned cell is published without every one of this lane's evidence rows."""
    cells = {r["site_id"]: set(r["processes"].split(";")) for r in B.read_csv(data / names[0])}
    published = any(p["term"] in cells.get(p["site_id"], set()) for p in props if p["route"] == "processes")
    ev = sum(r["created_by"] == B.WHO for r in B.read_csv(data / names[1]))
    return (not published) or ev == sum(p["route"] == "processes" for p in props)

def city_bound(printed, atlas):
    """Codex's township probe on the real SITE-002113 header: does printed city `printed` bind Atlas city `atlas` (Facility ID, holder and street held equal)?"""
    sites, orgs = B.atlas(); s = sites["SITE-002113"]; h = B.header(B.doc_text("1815636"))
    strict, near = B.bind_near(dict(h, holder_city=printed), dict(s, city=atlas), orgs[s["org_id"]], h["facility_id"])
    return not strict or bool(near)

def probe_interrupted_replay(props, hashes, base_ref_):
    """Codex's replay probe, from a clean merge-base copy and from the applied copy, cut at every replace: live shards stay whole, no cell is published without its rows, a retry reproduces the applied state.
    Also the base probe: an unrelated site's blanked cell is refused."""
    import tempfile
    from unittest.mock import patch
    names = ("sites_OH.csv", "evidence_sites_OH.csv", "site_capabilities.csv")
    tip = {n: (ROOT / "data" / n).read_bytes() for n in names}; old = {n: B.git("show", f"{base_ref_}:data/{n}").encode() for n in names}
    for start, src in (("base", old), ("applied", tip)):
        for cut_at in (1, 2, 3):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp); data = root / "data"; data.mkdir()
                for p in (ROOT / "data").glob("evidence_*.csv"):
                    if p.name not in names: (data / p.name).symlink_to(p)
                for n in names: (data / n).write_bytes(src[n])
                br = {data / n: rd(old[n].decode()) for n in names}
                real, calls = B.os.replace, []
                def cut(a, b):
                    if str(b).endswith(".stage"): return real(a, b)   # shard_io's own staging replace is not a publish
                    calls.append(a)
                    if len(calls) == cut_at: raise OSError("cut during replay")
                    return real(a, b)
                try:
                    with patch.object(B.os, "replace", cut): B.apply({"props": props}, hashes, root=root, base=br)
                except OSError: pass
                else: raise AssertionError("the cut never fired")
                assert not list(data.glob("*.stage")), "a stage file was left behind"
                assert lane_state_ok(data, props, names), f"{start}/cut {cut_at}: a planned cell was published without its evidence rows"
                if start == "applied": assert all((data / n).read_bytes() == tip[n] or n == names[0] for n in names[1:]), "a live shard changed during an interrupted replay"
                B.apply({"props": props}, hashes, root=root, base=br)
                assert all((data / n).read_bytes() == tip[n] for n in names), f"{start}/cut {cut_at}: the retry did not reproduce the applied state"
    with tempfile.TemporaryDirectory() as tmp:   # base probe: blank an unrelated site's processes cell in the live copy
        root = Path(tmp); data = root / "data"; data.mkdir()
        for p in (ROOT / "data").glob("evidence_*.csv"):
            if p.name not in names: (data / p.name).symlink_to(p)
        for n in names: (data / n).write_bytes(old[n])
        br = {data / n: rd(old[n].decode()) for n in names}
        plan = {p["site_id"] for p in props if p["route"] == "processes"}; rows = B.read_csv(data / names[0])
        next(r for r in rows if r["processes"] and r["site_id"] not in plan)["processes"] = ""
        B.write_csv(data / names[0], rows)
        try: B.apply({"props": props}, hashes, root=root, base=br)
        except AssertionError: pass
        else: raise AssertionError("an unrelated site's blanked processes cell was published")

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
    full = B.compute(dict(inp, caps=set(), ev_keys=set()))["props"]   # the plan as if no earlier PR had written anything: the injections below need write routes
    assert not audit(full, sites, orgs), audit(full, sites, orgs)
    assert [(p["site_id"], p["term"], p["capability_term"], p["route"]) for p in props if p["route"] in WRITE] == B.EXPECTED_WRITES, "the re-score must yield exactly one new row"
    assert [(p["site_id"], p["docid"], p["quote"]) for p in props if p["route"] in WRITE] == [REF_WRITE], "the one write is not the reviewed witness (independent reference)"
    inp4 = copy.deepcopy(inp); next(q for q in inp4["V"]["sites"]["SITE-000264"]["quotes"] if "rubber_extrusion" in q["terms"])["quote"] = "mills, calenders"
    assert B.compute(inp4)["viol"], "build.compute accepts a substituted quote for the authorized write"
    assert not audit_manifest(hashes, B.doc_text, inp["scr"]), audit_manifest(hashes, B.doc_text, inp["scr"])
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
    sites_cur, ev_cur, cap_cur = (B.read_csv(ROOT / f) for f in ("data/sites_OH.csv", "data/evidence_sites_OH.csv", "data/site_capabilities.csv"))
    assert not audit_complete(sites_cur, ev_cur, cap_cur, props), audit_complete(sites_cur, ev_cur, cap_cur, props)
    names = names_in_docs(); sig = signatories(); assert names and sig and sig <= names, "the privacy scan must know every signatory printed in the stored permits"
    assert not audit_privacy(task_files(), names), f"{len(audit_privacy(task_files(), names))} privacy findings"
    L = B.doc_text("1015038").split("\n"); i = next(i for i, l in enumerate(L) if "Assistant Chief" in l); who = name_of(L[i - 1])
    assert who and who in names and who in sig and len(audit_privacy({"README.md": who}, names)) >= 1, "the privacy gate misses the signatory printed with credentials"
    probe_interrupted_replay(props, hashes, base)
    for s_, fmt_ok in (("SITE-000264", True), ("SITE-001137", True), ("SITE-002113", True), ("SITE-000936", False), ("SITE-002114", False)):   # P2 positive and negative probes on the real rows
        r_ = next(x for x in model["sites"] if x["site_id"] == s_); assert (r_["bind"] == "BOUND") == fmt_ok, f"{s_}: bind {r_['bind']}, expected bound={fmt_ok}"
    assert city_bound("Newbury Twp.", "Newbury") and city_bound("Newbury", "Newbury Twp."), "a trailing township suffix must bind in both directions"
    assert not city_bound("Twp. Newbury", "Newbury"), "a leading township marker must not bind"
    for site_, term_, bad_quote in (("SITE-000814", "coating_formulation", "Permit Type: Renewal"), ("SITE-000814", "coating_formulation", "facility. Permit Type: Renewal Issue Date: 09/01/2023"),
                                    ("SITE-001530", "adhesive_sealant_formulation", SECTION_HEADING)):
        inp3 = copy.deepcopy(inp); next(q for q in inp3["V"]["sites"][site_]["quotes"] if term_ in q["terms"])["quote"] = bad_quote
        assert not [p for p in B.compute(inp3)["props"] if p["site_id"] == site_ and p["term"] == term_ and p["route"] in WRITE], "build.compute wrote a proposal whose witness is not wholly inside the Permit Description field"
    assert B.position(B.doc_text("1638095"), "FEPTIO renewal for blending vessels with powder dryers for the production of coatings and adhesives. Each emissions unit is vented to a dust collector for control of particulate emissions.") == "permit_description", "the committed multi-line description must still be a Permit Description"
    pos = copy.deepcopy([p for p in props if p["site_id"] == "SITE-000346"]); pos[0]["quote"] += ", blowdown tanks"
    assert not [g for g in audit(pos, sites, orgs) if g[0] == "ANCILLARY"], "a polymerization witness is rejected for one keyword in its equipment list"
    # ------------------------------------------------------------------------------------------------------------ injected defects
    def one(rule, mut, kind="props"):
        P = copy.deepcopy(full); S2, O2 = copy.deepcopy(sites), orgs
        if kind == "props":
            r = mut(P, S2) or P; got = audit(r, S2, O2)
        elif kind == "frame": got = audit_frame(mut(copy.deepcopy(inp["scr"])))
        elif kind == "data": got = audit_data(*mut(copy.deepcopy(bf), copy.deepcopy(nf)), props)
        elif kind == "written": got = audit_written(mut(copy.deepcopy(nf)), props, sites, hashes)
        elif kind == "complete": got = audit_complete(*mut(), props)
        elif kind == "manifest": got = audit_manifest(mut(copy.deepcopy(hashes)), B.doc_text, inp["scr"])
        elif kind == "ids": got = audit_ids(*mut())
        elif kind == "privacy": got = audit_privacy(mut(), names)
        assert any(g[0] == rule for g in got), f"injected defect {rule} was NOT caught: {got[:3]}"
        return rule
    def row(P, **m):
        return next(p for p in P if all(p[k] == v for k, v in m.items()))
    def scramble(P, S2):
        p = row(P, site_id="SITE-000664"); w = p["quote"].split(); p["quote"] = " ".join(w[3:6] + w[0:3] + w[6:])
    def other_street_number(P, S2):   # P2 must not relax the street number: SITE-000264's Atlas street gets a different number
        S2["SITE-000264"]["street_address"] = "5021 Enterprise Parkway"
    def blank_street(P, S2): S2["SITE-000814"]["street_address"] = "9999 Nowhere Rd"
    done = [
        one("QUOTE", lambda P, S2: row(P, site_id="SITE-000248").update(quote="Polyester gelcoat spray up booth for epoxy flooring.")),
        one("QUOTE", scramble),
        one("TERM", lambda P, S2: row(P, site_id="SITE-000248").update(term="composites_spray_up_fake")),
        one("ANCILLARY", lambda P, S2: row(P, site_id="SITE-000590").update(term="coating_applying", route="processes", strength="supports_C")),
        one("BIND", other_street_number),
        one("BIND", blank_street),
        one("TIER_C", lambda P, S2: row(P, site_id="SITE-001530", term="coating_formulation").update(route="processes")),
        one("EXPIRED", lambda P, S2: row(P, site_id="SITE-000238", term="composites_spray_up").update(strength="supports_A")),
    ]
    sites_now = nf.get("data/sites_OH.csv") or B.read_csv(ROOT / "data/sites_OH.csv"); sites_base = bf.get("data/sites_OH.csv") or rd(B.git("show", f"{base}:data/sites_OH.csv"))
    def cell_defect(b, n):
        b = {"data/sites_OH.csv": copy.deepcopy(sites_base)}; n = {"data/sites_OH.csv": copy.deepcopy(sites_base)}; n["data/sites_OH.csv"][5]["street_address"] = "tampered"; return b, n
    def row_defect(b, n):
        b = {"data/evidence_sites_OH.csv": rd(B.git("show", f"{base}:data/evidence_sites_OH.csv"))}; n = {"data/evidence_sites_OH.csv": copy.deepcopy(b["data/evidence_sites_OH.csv"])}; n["data/evidence_sites_OH.csv"][3]["notes"] = "edited"; return b, n
    def flip_cap(n):   # a written capability row with another term
        i = next(i for i, r in enumerate(n["data/site_capabilities.csv"]) if r["created_by"] == B.WHO); n["data/site_capabilities.csv"][i]["term"] = "calendering"; return n
    def restore_base():
        return (rd(B.git("show", f"{base}:data/sites_OH.csv")), ev_cur, rd(B.git("show", f"{base}:data/site_capabilities.csv")))
    def fake_digest(n):   # a falsified PDF digest in a written row's note
        i = next(i for i, r in enumerate(n["data/site_capabilities.csv"]) if r["created_by"] == B.WHO)
        n["data/site_capabilities.csv"][i]["notes"] = re.sub(r"sha256 [0-9a-f]{64}", "sha256 " + "0" * 64, n["data/site_capabilities.csv"][i]["notes"]); return n
    def other_term(P, S2): row(P, site_id="SITE-000264", term="rubber_extrusion").update(capability_term="calendering")
    def site_936_bound(P, S2):   # item 2: a write for SITE-000936 on its permit document must fail the bind
        h = copy.deepcopy(row(P, site_id="SITE-000264", term="rubber_extrusion")); h.update(site_id="SITE-000936", tier="C", docid="4213969", quote="Guardian Manufacturing Company", route="capability", capability_term="extrusion", strength="supports_C"); P.append(h)
    def second_row():
        extra = dict(next(r for r in cap_cur if r["created_by"] == B.WHO)); extra["capability_id"] = "CAP-999999"; return sites_cur, ev_cur, cap_cur + [extra]
    def other_table(b, n):   # a lane row in another table: an evidence row nobody planned
        b = {"data/evidence_sites_OH.csv": rd(B.git("show", f"{base}:data/evidence_sites_OH.csv"))}; n = {"data/evidence_sites_OH.csv": copy.deepcopy(b["data/evidence_sites_OH.csv"])}
        r = dict(n["data/evidence_sites_OH.csv"][0]); r.update(evidence_id="EVD-999999", created_by=B.WHO); n["data/evidence_sites_OH.csv"].append(r); return b, n
    def other_file(b, n):   # a change to a data file this lane may not touch
        b = {"data/people.csv": [{"person_id": "P1", "name": "x"}]}; n = {"data/people.csv": [{"person_id": "P1", "name": "y"}]}; return b, n
    def fake_manifest(h): h["4325660"]["facility_id"] = "0000000000"; return h
    def duplicate_row(P, S2):   # Codex's probe at proposal level: a second, unflagged proposal for the held pair
        h = copy.deepcopy(row(P, site_id="SITE-000248", term="coating_applying")); h.update(route="processes", hold_reason="", strength="supports_C"); P.append(h)
    def duplicate_verdict():   # the same probe at verdict level: build.compute must hold the unflagged duplicate itself
        inp2 = copy.deepcopy(inp); qs = inp2["V"]["sites"]["SITE-000248"]["quotes"]
        qs.append({k: v for k, v in next(q for q in qs if q.get("hold")).items() if k != "hold"})
        out = B.compute(inp2)["props"]
        return [p for p in out if p["site_id"] == "SITE-000248" and p["term"] == "coating_applying" and p["route"] != "hold"]
    def held_in_applied():
        s = copy.deepcopy(sites_cur); next(r for r in s if r["site_id"] == "SITE-000248")["processes"] += ";coating_applying"; return s, ev_cur, cap_cur
    assert not duplicate_verdict(), "build.compute wrote a duplicate of a held (site, term) pair"
    from unittest.mock import patch
    with patch.object(B, "held_pairs", lambda props: set()):   # the probe must be live: with the pair check off, the duplicate is written
        assert duplicate_verdict(), "the verdict-level duplicate probe is inert: it is not written even with the pair check disabled"
    done += [one("BIND", lambda P, S2: S2["SITE-000264"].update(city="Twp. Seville")),   # a LEADING township marker on a written row must not bind
             one("WITNESS", lambda P, S2: row(P, site_id="SITE-000814").update(quote="Permit Type: Renewal")),
             one("WITNESS", lambda P, S2: row(P, site_id="SITE-001530", term="adhesive_sealant_formulation").update(route="capability", capability_term="adhesive_sealant_formulation", strength="supports_C", quote=SECTION_HEADING)),   # Codex round 3: the heading that introduces the unit list
             one("WITNESS", lambda P, S2: row(P, site_id="SITE-000814").update(quote="facility. Permit Type: Renewal Issue Date: 09/01/2023")),   # Codex: starts inside the field, ends in the next one
             one("OWNER_HOLD", duplicate_row), one("OWNER_HOLD", held_in_applied, "complete"),
             one("OWNER_HOLD", lambda P, S2: row(P, site_id="SITE-000248", term="coating_applying").update(route="processes")),
             one("COMPLETE", restore_base, "complete"), one("WRITTEN", fake_digest, "written"), one("MANIFEST", fake_manifest, "manifest"),
             one("PINNED", lambda P, S2: row(P, site_id="SITE-000264", term="rubber_extrusion").update(quote="mills, calenders")),   # Codex round 1: a real but wrong witness
             one("CAP", other_term), one("BIND", site_936_bound), one("COMPLETE", second_row, "complete"), one("ROWS", other_table, "data"), one("FILE", other_file, "data"),
             one("ID", lambda: ([cap_base_max], cap_base_max, "capability"), "ids"),
             one("PRIVACY", lambda: {"README.md": "signed by " + sorted(sig)[0]}, "privacy"),
             one("WITNESS", lambda P, S2: row(P, site_id="SITE-000448").update(quote="ABS Compound Plant for Colored Pellets", term="compounding_extrusion", route="processes", strength="supports_C")),
             one("PD_STRENGTH", lambda P, S2: row(P, site_id="SITE-000814").update(strength="supports_A")),
             one("WRITTEN", flip_cap, "written"), one("CELLS", cell_defect, "data"), one("ROWS", row_defect, "data"),
             one("ID", lambda: ([ev_base_max], ev_base_max, "evidence"), "ids"),
             one("PRIVACY", lambda: {"README.md": "contact " + sorted(names)[0] + " about the permit"}, "privacy"),
             one("PRIVACY", lambda: {"README.md": "write to someone" + chr(64) + "example.com"}, "privacy"),
             one("FRAME", lambda scr: [dict(r, status="no_air_record") if r["site_id"] == "SITE-000590" else r for r in scr], "frame")]
    assert len([d for d in done if d]) == EXPECTED_DEFECTS, f"{len(done)} injected defects run, EXPECTED_DEFECTS says {EXPECTED_DEFECTS}"
    print(f"names {len(names)}, signatories {len(sig)}; ok: frame {B.N_FRAME} (independent count agrees); strict-bound {B.metrics(model)['strict_bound_sites']}, near-bound {B.metrics(model)['near_bound_sites']}; "
          f"{n_ev} evidence rows, {n_cp} capability rows planned, {len(mine_ev)}/{len(mine_cp)} applied and equal to the plan; {len([d for d in done if d])} injected defects all caught")

if __name__ == "__main__": main()
