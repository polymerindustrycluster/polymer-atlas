"""Named check for the PIC-18 air-permit scout. Recomputes every published count from the frozen caches and fails on:
a quote not in its stored document, a term not in §3.1, a site outside the pool, a frame site with no verdict, any change under data/.
Then proves it fails by injecting 6 defects. Missing caches or tools fail the run (never skipped).
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
    st["vocab"] = B.processes()
    st["schema31"] = set(re.findall(r"`([a-z0-9_]+)`", re.search(r"### 3\.1 Processes.*?### 3\.2", open(ROOT / "docs/SCHEMA.md").read(), re.S).group(0)))
    st["changed"] = [x for x in git("diff", "--name-only", REF).split("\n") + git("status", "--porcelain").split("\n") if x.strip()]
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
    if stat != st["metrics"]["status_counts"]: f.append("status counts differ from metrics.json")
    ret = stat.get("retrievable_permit", 0)
    if ret != st["metrics"]["retrievable_permit_sites"]: f.append("retrievable count differs from metrics.json")
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
    # quotes, terms, hashes
    for q in st["quotes"]:
        if q["docid"] not in st["hashes"]: f.append(f"{q['quote_id']} cites an unpinned document"); continue
        if not B.in_order(q["quote"], doc_text(q["docid"])): f.append(f"{q['quote_id']} quote not in stored document {q['docid']}")
        terms = [t for t in q["terms"].split(";") if t]
        for t in terms:
            if t not in st["vocab"] or t not in st["schema31"]: f.append(f"{q['quote_id']} term {t} not in §3.1")
        want_cls = "none" if not terms else ("unspecified" if all(t.endswith("_unspecified") for t in terms) else "specific")
        if q["term_class"] != want_cls: f.append(f"{q['quote_id']} term_class {q['term_class']} != {want_cls}")
        if q["proposal_status"] != "HELD": f.append(f"{q['quote_id']} not HELD")
        if q["proposed_strength"] != B.strength_of(q["source_part"]): f.append(f"{q['quote_id']} strength differs from the source_part rule")
    f += st["doc_bad"]
    # canary counts recomputed from the quotes + bind
    sp = an = 0
    for r in st["sites"]:
        qs = [q for q in st["quotes"] if q["site_id"] == r["site_id"]]
        s_ = any(q["term_class"] == "specific" for q in qs) and r["bind"] == "BOUND"; a_ = any(q["term_class"] in ("specific", "unspecified") for q in qs) and r["bind"] == "BOUND"
        if (r["specific_hit"] == "Y") != s_ or (r["any_term_hit"] == "Y") != a_: f.append(f"{r['site_id']} hit flags differ from its quotes")
        sp += s_; an += a_
    m = st["metrics"]
    if (sp, an) != (m["specific_hit"], m["any_term_hit"]): f.append("hit counts differ from metrics.json")
    spn = len({q["site_id"] for q in st["quotes"] if q["term_class"] == "specific" and q["proposed_strength"] == "supports_A"})
    if spn != m["specific_hit_narrative_strength"]: f.append("narrative-strength count differs from metrics.json")
    if m["specific_wilson95"] != B.wilson(sp, 10) or m["any_term_wilson95"] != B.wilson(an, 10): f.append("Wilson interval differs")
    if m["projected_specific_sites_of_58"] != round(ret * sp / 10, 1): f.append("projection differs")
    # nothing outside this task folder, nothing under data/
    rel = str(HERE.relative_to(ROOT))
    for line in st["changed"]:
        path = line[3:] if re.match(r"^[ MADRCU?!]{2} ", line) else line
        if path.startswith("data/") or not path.startswith(rel + "/"): f.append(f"change outside the task folder: {path}")
    return f

def inject(st):
    """Each defect must make checks() fail; returns the number of defects caught."""
    cases = []
    def mut(fn): s = copy.deepcopy(st); fn(s); return s
    cases.append(("fabricated quote", mut(lambda s: s["quotes"][0].update(quote="Polyurethane foam pouring line for mattresses"))))
    cases.append(("term not in §3.1", mut(lambda s: s["quotes"][0].update(terms="thermoforming_hot_stamping"))))
    cases.append(("site outside the pool", mut(lambda s: s["quotes"][0].update(site_id="SITE-009999"))))
    cases.append(("frame site without verdict", mut(lambda s: s.update(sites=s["sites"][1:]))))
    cases.append(("change under data/", mut(lambda s: s["changed"].append(" M data/sites_OH.csv"))))
    cases.append(("count tampered", mut(lambda s: s["metrics"].update(retrievable_permit_sites=s["metrics"]["retrievable_permit_sites"] + 1))))
    caught = 0
    for name, s in cases:
        r = checks(s); caught += bool(r); print(f"  injected [{name}]: {'REJECTED' if r else 'NOT CAUGHT'}")
    return caught, len(cases)

if __name__ == "__main__":
    st = load(); fails = checks(st)
    for x in fails: print("FAIL:", x)
    if fails: sys.exit(1)
    print(f"base checks PASS (pool 58, air-record {st['metrics']['air_record_sites']}, retrievable {st['metrics']['retrievable_permit_sites']}, canary specific {st['metrics']['specific_hit']}/10)")
    c, n = inject(st)
    if c != n: print(f"FAIL: only {c}/{n} injected defects caught"); sys.exit(1)
    print(f"PASS: {n}/{n} injected defects rejected")
