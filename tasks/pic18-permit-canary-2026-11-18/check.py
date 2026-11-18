"""Named check for the PIC-18 air-permit scout. Recomputes every published count from the frozen caches and fails on:
a quote not in its stored document, a term not in §3.1, a site outside the pool, a frame site with no verdict, any change under data/.
It binds every quote to its establishment (site -> verdict document -> printed Facility ID), recomputes every bind field from the stored permit text and every published metric from the rows, and then proves it fails by injecting 9 defects. Missing caches or tools fail the run (never skipped).
Usage: python3 check.py"""
import copy, csv, hashlib, importlib.util, json, random, re, subprocess, sys, zipfile, io
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pbuild", HERE / "build.py"); B = importlib.util.module_from_spec(spec); sys.modules["pbuild"] = B; spec.loader.exec_module(B)
ROOT, S, P, REF = B.ROOT, B.S, B.P, B.REF

def rd(name): return list(csv.DictReader(open(HERE / name)))

def git(*a): return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout

def load():
    for need in (P / "ohio_epa_search_hits.json", P / "fetch_journal_v2.jsonl", B.ECHO_ZIP, S / "briefs/w1118b/frames.json"):
        if not need.exists(): raise SystemExit(f"FAIL: missing cache {need} (a check that cannot inspect its input must not pass)")
    if subprocess.run(["pdftotext", "-v"], capture_output=True).returncode not in (0, 99): raise SystemExit("FAIL: pdftotext missing")
    st = {"pool": rd("pool.csv"), "screen": rd("screen.csv"), "sites": rd("canary_sites.csv"), "quotes": rd("canary_quotes.csv"), "metrics": json.load(open(HERE / "metrics.json")),
          "verdicts": json.load(open(HERE / "canary_verdicts.json"))["sites"], "hashes": json.load(open(HERE / "doc_hashes.json")),
          "frames": json.load(open(S / "briefs/w1118b/frames.json")), "hits": json.load(open(P / "ohio_epa_search_hits.json")),
          "journal": {d["docid"]: d for d in map(json.loads, open(P / "fetch_journal_v2.jsonl"))}}
    want = {i for p in st["pool"] for i in p["frs_ids"].split(";") if i}; air = {}
    for r in csv.DictReader(io.TextIOWrapper(zipfile.ZipFile(B.ECHO_ZIP).open("ECHO_EXPORTER.csv"), encoding="utf-8", errors="replace", newline="")):
        if r["REGISTRY_ID"] in want and r["AIR_FLAG"] == "Y": air[r["REGISTRY_ID"]] = r["AIR_IDS"]
    st["echo_air"] = air
    st["screen_recompute"] = [{k: str(v) for k, v in r.items()} for r in B.screen_rows()]
    bad = []
    for d, h in st["hashes"].items():
        pdf = P / "docs" / f"{d}.pdf"
        if hashlib.sha256(pdf.read_bytes()).hexdigest() != h["pdf_sha256"]: bad.append(f"pdf hash differs for {d}")
        t = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
        if hashlib.sha256(t.encode()).hexdigest() != h["text_sha256"] or t != doc_text(d): bad.append(f"text hash differs for {d}")
    st["doc_bad"] = bad
    orgs = {r["org_id"]: r for r in B.ref_rows("organizations_")}; sites = {r["site_id"]: r for r in B.ref_rows("sites_")}
    rec = {}
    for p in st["pool"]:
        v = st["verdicts"].get(p["site_id"])
        if not v: continue
        hdr = [B.header(doc_text(d)) for d in v["docs"]]; fid = p["echo_air_ids"].split(";")[0][-10:]; o = orgs[p["org_id"]]; a = sites[p["site_id"]]
        rr = B.bind_registered(hdr, fid, a, o)
        rec[p["site_id"]] = {"record_tier": a["verification_tier"], "facility_id_printed": hdr[0]["facility_id"], "holder_printed": hdr[0]["holder"], "permit_street_printed": hdr[0]["holder_street"],
                             "permit_city_printed": hdr[0]["holder_city"], "atlas_street": a["street_address"], "atlas_city": a["city"],
                             "bind_registered": "BOUND" if not rr else "NOT_BOUND", "bind_registered_reasons": "; ".join(rr), "fid": fid, "doc_fids": {d: B.header(doc_text(d))["facility_id"] for d in v["docs"]}}
    st["bind_recomputed"] = rec
    st["vocab"] = B.processes()
    st["schema31"] = set(re.findall(r"`([a-z0-9_]+)`", re.search(r"### 3\.1 Processes.*?### 3\.2", open(ROOT / "docs/SCHEMA.md").read(), re.S).group(0)))
    base = git("merge-base", "HEAD", "origin/main").strip()
    st["changed"] = [x for x in git("diff", "--name-only", base).split("\n") + git("status", "--porcelain").split("\n") if x.strip()]
    return st

def doc_text(d): return open(P / "docs" / f"{d}.txt").read()

def checks(st):
    f = []
    pool = {p["site_id"] for p in st["pool"]}
    # inputs: pool equals the controller's frame pool; the controller's provisional draw lies inside it
    if len(pool) != 58 or st["frames"]["permit_pool"] != len(pool): f.append("pool size differs from the controller frame permit_pool")
    if not set(st["frames"]["permit_frame_sites"]) <= pool: f.append("controller frame site outside the pool")
    # no site outside the pool, anywhere
    for name in ("screen", "sites", "quotes"):
        for r in st[name]:
            if r["site_id"] not in pool: f.append(f"{name}: site outside the pool {r['site_id']}")
    if {r["site_id"] for r in st["screen"]} != pool: f.append("screen.csv does not cover the pool exactly")
    # echo air flags: independent recount from the pinned ECHO exporter
    air = st["echo_air"]
    n_air = sum(any(i in air for i in p["frs_ids"].split(";")) for p in st["pool"])
    if n_air != st["metrics"]["air_record_sites"]: f.append(f"air_record_sites {st['metrics']['air_record_sites']} != recount {n_air}")
    if any(set(p["echo_air_ids"].split(";")) - {""} != {air[i] for i in p["frs_ids"].split(";") if i in air} for p in st["pool"]): f.append("pool.csv echo_air_ids differ from the exporter")
    # screen recomputed from caches (same code path) and yield against an independent count of fetched documents
    if st["screen_recompute"] != [dict(r) for r in st["screen"]]: f.append("screen.csv differs from a recompute from the caches")
    sel = set()
    for site, v in st["hits"].items():
        c = sorted({(B.pdate(t), d) for x in v["searches"] for d, t in x.get("hits", []) if "DRAFT" not in t and "CORRESPONDENCE" not in t}, reverse=True)[:6]; sel |= {d for _, d in c}
    if sel != set(st["journal"]): f.append(f"fetched documents {len(st['journal'])} != documents the rule selects {len(sel)}")
    stat = {}
    for r in st["screen"]: stat[r["status"]] = stat.get(r["status"], 0) + 1
    ret = stat.get("retrievable_permit", 0)
    # every retrievable site has stored final permits that pass the classifier; every non-retrievable site has a stated reason; every frame site has a verdict
    for r in st["screen"]:
        if r["status"] == "retrievable_permit" and not r["final_permit_docids"]: f.append(f"{r['site_id']} retrievable but no document")
        if r["status"] != "retrievable_permit" and not r["reason"]: f.append(f"{r['site_id']} has no reason")
    ids = sorted(r["site_id"] for r in st["screen"] if r["status"] == "retrievable_permit")
    draw = random.Random(B.SEED).sample(ids, min(10, len(ids)))
    if draw != st["metrics"]["canary_draw"]: f.append("canary draw differs from random.Random(20261118).sample(sorted(ids), 10)")
    for s in draw:
        if s not in {r["site_id"] for r in st["sites"]}: f.append(f"frame site {s} has no verdict row")
        if s not in st["verdicts"]: f.append(f"frame site {s} has no authored verdict")
    if {r["site_id"] for r in st["sites"]} != set(draw): f.append("canary_sites.csv is not exactly the draw")
    # quotes: verbatim in the stored document, bound to the site through the printed Facility ID, terms in §3.1
    rec = st["bind_recomputed"]
    for q in st["quotes"]:
        sid = q["site_id"]
        if q["docid"] not in st["hashes"]: f.append(f"{q['quote_id']} cites an unpinned document"); continue
        if sid not in st["verdicts"] or q["docid"] not in st["verdicts"][sid]["docs"]: f.append(f"{q['quote_id']} document {q['docid']} is not a document of {sid}")
        elif sid in rec and rec[sid]["doc_fids"].get(q["docid"]) != rec[sid]["fid"]: f.append(f"{q['quote_id']} document prints Facility ID {rec[sid]['doc_fids'].get(q['docid'])}, not {sid}'s {rec[sid]['fid']}")
        if not B.in_order(q["quote"], doc_text(q["docid"])): f.append(f"{q['quote_id']} quote not in stored document {q['docid']}")
        terms = [t for t in q["terms"].split(";") if t]
        for t in terms:
            if t not in st["vocab"] or t not in st["schema31"]: f.append(f"{q['quote_id']} term {t} not in §3.1")
        want_cls = "none" if not terms else ("unspecified" if all(t.endswith("_unspecified") for t in terms) else "specific")
        if q["term_class"] != want_cls: f.append(f"{q['quote_id']} term_class {q['term_class']} != {want_cls}")
        if q["witness"] not in {"unit_heading", "unit_equipment", "unit_term", "permit_description"}: f.append(f"{q['quote_id']} unknown witness")
        if q["proposed_strength"] not in {"supports_A", "supports_C"}: f.append(f"{q['quote_id']} unknown strength")
        if q["proposal_status"] != "HELD": f.append(f"{q['quote_id']} not HELD")
    f += st["doc_bad"]
    # bind fields: recomputed from the stored permit text and the Atlas rows at the pinned ref, never trusted from the csv
    for r in st["sites"]:
        want = rec.get(r["site_id"])
        if not want: f.append(f"{r['site_id']} has no recomputed bind"); continue
        for k in ("record_tier", "facility_id_printed", "holder_printed", "permit_street_printed", "permit_city_printed", "atlas_street", "atlas_city", "bind_registered", "bind_registered_reasons"):
            if r[k] != want[k]: f.append(f"{r['site_id']} {k} '{r[k]}' differs from recompute '{want[k]}'")
    # every published metric recomputed from the rows
    m = st["metrics"]; want_m = B.compute_metrics(st["screen"], st["sites"], st["quotes"]); want_m["canary_draw"] = draw
    for k in sorted(set(m) | set(want_m)):
        if m.get(k) != want_m.get(k): f.append(f"metric {k}: published {m.get(k)} != recomputed {want_m.get(k)}")
    if m["registered_specific"]["hit"] < 0: f.append("negative hit count")
    # nothing outside this task folder, nothing under data/
    rel = str(HERE.relative_to(ROOT))
    for line in st["changed"]:
        path = line[3:] if re.match(r"^[ MADRCU?!]{2} ", line) else line
        if path.startswith("data/") or not path.startswith(rel + "/"): f.append(f"change outside the task folder: {path}")
    return f

def inject(st):
    """Each defect must make checks() fail; returns (caught, total)."""
    def mut(fn): s = copy.deepcopy(st); fn(s); return s
    def swap(s):
        a = next(q for q in s["quotes"] if q["site_id"] == "SITE-000601"); b = next(q for q in s["quotes"] if q["site_id"] == "SITE-000997"); a["site_id"], b["site_id"] = b["site_id"], a["site_id"]
    def fake_bind(s): s["sites"][0].update(facility_id_printed="0000000000", holder_printed="Invented Holder LLC", permit_street_printed="1 Nowhere Rd")
    def zero(s):
        s["metrics"]["bound_registered"] = 0; s["metrics"]["registered_specific"].update(hit=0, projected_sites_of_58=0.0, projected_range=[0.0, 0.0], wilson95=[0.0, 0.0])
    cases = [("fabricated quote", mut(lambda s: s["quotes"][0].update(quote="Polyurethane foam pouring line for mattresses"))),
             ("term not in §3.1", mut(lambda s: s["quotes"][0].update(terms="thermoforming_hot_stamping"))),
             ("site outside the pool", mut(lambda s: s["quotes"][0].update(site_id="SITE-009999"))),
             ("frame site without verdict", mut(lambda s: s.update(sites=s["sites"][1:]))),
             ("change under data/", mut(lambda s: s["changed"].append(" M data/sites_OH.csv"))),
             ("count tampered", mut(lambda s: s["metrics"].update(retrievable_permit_sites=s["metrics"]["retrievable_permit_sites"] + 1))),
             ("real quotes swapped between two sites", mut(swap)),
             ("fabricated bind fields", mut(fake_bind)),
             ("zeroed bound total and projection", mut(zero))]
    caught = 0
    for name, s in cases:
        r = checks(s); caught += bool(r); print(f"  injected [{name}]: {'REJECTED' if r else 'NOT CAUGHT'}")
    return caught, len(cases)

if __name__ == "__main__":
    st = load(); fails = checks(st)
    for x in fails: print("FAIL:", x)
    if fails: sys.exit(1)
    m = st["metrics"]; print(f"base checks PASS (pool 58, air-record {m['air_record_sites']}, retrievable {m['retrievable_permit_sites']}, bound {m['bound_registered']}/10, registered specific {m['registered_specific']['hit']}/10, broadened {m['broadened_specific']['hit']}/10)")
    c, n = inject(st)
    if c != n: print(f"FAIL: only {c}/{n} injected defects caught"); sys.exit(1)
    print(f"PASS: {n}/{n} injected defects rejected")
