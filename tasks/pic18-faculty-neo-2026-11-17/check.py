#!/usr/bin/env python3
"""Named check for PIC-18 faculty completeness (atlas-w17-fac-b). Exit 0 only if every check passes.
  python3 check.py            run the checks on the working tree
  python3 check.py --selftest inject four defects (altered quote, wrong hash, edited held row, email in a field); each must FAIL
Base for 'nothing else changed' is the merge-base with origin/main (override: BASE=ref)."""
import csv, io, os, re, subprocess, sys, copy
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common
REPO = common.REPO; TASK = "tasks/pic18-faculty-neo-2026-11-17"
P_BLOCK = (2400, 2499); E_BLOCK = (394000, 394999)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"); PHONE = re.compile(r"(?<!\d)(?:\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4})(?!\d)")
ALLOWED = {"data/people.csv", "data/evidence_people.csv"}

def git(*a): return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, check=True).stdout
def rows(text): return list(csv.DictReader(io.StringIO(text)))
def idn(s): return int(s.split("-")[1])

def check_verdicts(vrows):
    f = []
    for r in vrows:
        if r["verdict"] != "VERIFIED": continue
        for side in "ab":
            sha, q = r[f"gate_{side}_sha256"], r[f"gate_{side}_quote"]
            if not q or not sha: f.append(f"{r['full_name']}: gate {side} missing"); continue
            if len(q.split()) > 25: f.append(f"{r['full_name']}: gate {side} quote >25 words")
            if not os.path.exists(common.PERSIST + sha): f.append(f"{r['full_name']}: witness {sha[:8]} missing"); continue
            if not common.sha_ok(sha): f.append(f"{r['full_name']}: witness {sha[:8]} bytes do not hash to name")
            elif not common.quote_in(sha, q): f.append(f"{r['full_name']}: gate {side} quote not in stored page")
            if common.manifest().get(r[f"gate_{side}_url"]) != sha: f.append(f"{r['full_name']}: gate {side} sha not the manifest sha for its url")
    return f

def check_provenance(vrows):
    prov = {r["url"]: r["url_provenance"] for r in csv.DictReader(open(common.PERSIST + "manifest.csv"))}
    f = []
    for r in vrows:
        for side in "ab":
            u = r[f"gate_{side}_url"]
            if u and prov.get(u, "CONSTRUCTED").startswith("CONSTRUCTED"): f.append(f"{r['full_name']}: gate {side} url has constructed/unknown provenance")
    return f

def check_data(people, evid, base_people, base_evid, vrows):
    f = []
    bp = {p["person_id"]: p for p in base_people}; be = {e["evidence_id"]: e for e in base_evid}
    cp = {p["person_id"]: p for p in people}; ce = {e["evidence_id"]: e for e in evid}
    for k, v in bp.items():
        if cp.get(k) != v: f.append(f"existing people row changed or lost: {k}")
    for k, v in be.items():
        if ce.get(k) != v: f.append(f"existing evidence row changed or lost: {k}")
    newp = [p for k, p in cp.items() if k not in bp]; newe = [e for k, e in ce.items() if k not in be]
    for p in newp:
        if not P_BLOCK[0] <= idn(p["person_id"]) <= P_BLOCK[1]: f.append(f"person id outside block: {p['person_id']}")
        kinds = {e["claim_type"] for e in newe if e["record_id"] == p["person_id"]}
        if not {"existence", "scope"} <= kinds: f.append(f"{p['person_id']} lacks existence+scope evidence")
    for e in newe:
        if not E_BLOCK[0] <= idn(e["evidence_id"]) <= E_BLOCK[1]: f.append(f"evidence id outside block: {e['evidence_id']}")
        if e["record_id"] not in cp: f.append(f"{e['evidence_id']} record {e['record_id']} missing")
        if e["created_by"] != "atlas-w17-fac-b" or e["observed_date"] != "2026-11-17": f.append(f"{e['evidence_id']} created_by/observed_date wrong")
    ver = [r for r in vrows if r["verdict"] == "VERIFIED"]
    if len(newp) != len(ver): f.append(f"new people {len(newp)} != VERIFIED verdicts {len(ver)}")
    if sorted(p["full_name"] for p in newp) != sorted(r["full_name"] for r in ver): f.append("new people names differ from VERIFIED verdict names")
    for r in newp + newe:
        for k, v in r.items():
            if EMAIL.search(v or "") or PHONE.search(v or ""): f.append(f"email/phone pattern in new row field {k}")
    return f

def check_files(base):
    f = []
    changed = [l for l in git("diff", "--name-only", base).split() if l] + [l for l in git("ls-files", "--others", "--exclude-standard").split() if l]
    for c in changed:
        if c not in ALLOWED and not c.startswith(TASK + "/"): f.append(f"unexpected changed file: {c}")
    for c in changed:
        if c.startswith(TASK + "/") and os.path.isfile(os.path.join(REPO, c)) and c.endswith((".csv", ".md", ".json")):
            for n, line in enumerate(open(os.path.join(REPO, c), errors="ignore"), 1):
                if EMAIL.search(line) or PHONE.search(line): f.append(f"email/phone pattern in {c}:{n}")
    mp = common.PERSIST + "manifest.csv"
    for n, line in enumerate(open(mp), 1):
        if EMAIL.search(line) or PHONE.search(line): f.append(f"email/phone pattern in manifest:{n}")
    return f

def counts(vrows):
    return Counter(r["verdict"] for r in vrows), Counter((r["institution"], r["unit"], r["verdict"]) for r in vrows)

def check_published_counts(vrows):
    f = []; c, _ = counts(vrows)
    fr = list(csv.DictReader(open(os.path.join(HERE, "frame.csv"))))
    for r in fr:
        n = sum(1 for v in vrows if v["institution"] == r["institution"] and v["unit"] == r["unit"])
        if n != int(r["examined"]): f.append(f"frame.csv {r['institution']}/{r['unit']} examined {r['examined']} != recomputed {n}")
    listed = Counter(next(c for k, c in [("Macromolecular", "MACRO"), ("Materials Science", "MSE"), ("Chemical", "CBE"), ("Biomedical", "BME"), ("Mechanical", "MAE")] if k in t)
                     for _, _, t in common.case_entries() if "Professor" in t and any(k in t for k in ("Macromolecular", "Materials Science", "Chemical", "Biomedical", "Mechanical")))
    for r in fr:
        if r["listed"] not in ("n/a", "not counted"):
            if int(r["listed"]) != listed[r["unit"]]: f.append(f"frame.csv CWRU/{r['unit']} listed {r['listed']} != recount from stored directory {listed[r['unit']]}")
            if int(r["listed"]) != int(r["examined"]): f.append(f"frame.csv CWRU/{r['unit']}: listed {r['listed']} != examined {r['examined']} (unadjudicated frame rows)")
    if sum(int(r["examined"]) for r in fr) != len(vrows): f.append("frame.csv examined total != verdict rows")
    m = re.search(r"counts: (.*?) -->", open(os.path.join(HERE, "README.md")).read())
    pub = dict(kv.split("=") for kv in m.group(1).split()) if m else {}
    for k in ("VERIFIED", "REJECT", "STILL_UNCERTAIN", "DUPLICATE_OF"):
        if int(pub.get(k, -1)) != c[k]: f.append(f"README count {k}={pub.get(k)} != recomputed {c[k]}")
    sw = re.search(r"sweep: (.*?) -->", open(os.path.join(HERE, "README.md")).read())
    pub_sw = dict(kv.split("=") for kv in sw.group(1).split()) if sw else {}
    def typ(r):
        n = r["verdict_note"]
        for k, p in (("cwru_profile", "Gate B fails: own profile has a research"), ("kent_profile", "Gate B fails: AMLCI profile has a research"),
                     ("cwru_roster", "Gate B fails: department roster"), ("ysu_catalog", "Gate B fails: catalog listing")):
            if n.startswith(p): return k
        return "hand"
    sc = Counter(typ(r) for r in vrows if r["verdict"] == "REJECT" and r["verdict_note"].startswith("Gate B"))
    for k in ("cwru_profile", "kent_profile", "cwru_roster", "ysu_catalog", "hand"):
        if int(pub_sw.get(k, -1)) != sc[k]: f.append(f"README sweep table {k}={pub_sw.get(k)} != recomputed {sc[k]}")
    return f

def run(vrows=None, people=None, evid=None, base=None):
    base = base or os.environ.get("BASE") or git("merge-base", "HEAD", "origin/main").strip()
    vrows = vrows if vrows is not None else list(csv.DictReader(open(os.path.join(HERE, "verdicts.csv"))))
    people = people if people is not None else rows(open(os.path.join(REPO, "data/people.csv")).read())
    evid = evid if evid is not None else rows(open(os.path.join(REPO, "data/evidence_people.csv")).read())
    bp = rows(git("show", f"{base}:data/people.csv")); be = rows(git("show", f"{base}:data/evidence_people.csv"))
    return check_verdicts(vrows) + check_provenance(vrows) + check_data(people, evid, bp, be, vrows) + check_published_counts(vrows) + check_files(base)

def selftest():
    vrows = list(csv.DictReader(open(os.path.join(HERE, "verdicts.csv"))))
    people = rows(open(os.path.join(REPO, "data/people.csv")).read()); evid = rows(open(os.path.join(REPO, "data/evidence_people.csv")).read())
    base = os.environ.get("BASE") or git("merge-base", "HEAD", "origin/main").strip()
    assert not run(vrows, people, evid, base), "clean tree must pass before injecting defects"
    v = copy.deepcopy(vrows); i = next(k for k, r in enumerate(v) if r["verdict"] == "VERIFIED"); v[i]["gate_b_quote"] += " zebra"
    d1 = run(v, people, evid, base)
    v = copy.deepcopy(vrows); v[i]["gate_a_sha256"] = "0" * 64
    d2 = run(v, people, evid, base)
    p = copy.deepcopy(people); p[0]["role_as_published"] += " edited"
    d3 = run(vrows, p, evid, base)
    p = copy.deepcopy(people); p[-1]["role_as_published"] = "Professor jane.doe@example.edu"
    d4 = run(vrows, p, evid, base)
    ok = True
    for name, d in [("altered quote", d1), ("wrong hash", d2), ("edited held row", d3), ("email in a field", d4)]:
        print(f"  injected {name}: {'FAILS (good)' if d else 'PASSED (BAD)'}  {d[:1]}"); ok &= bool(d)
    return 0 if ok else 1

if __name__ == "__main__":
    if "--selftest" in sys.argv: sys.exit(selftest())
    fails = run()
    c, _ = counts(list(csv.DictReader(open(os.path.join(HERE, "verdicts.csv")))))
    print("verdicts:", dict(c))
    for x in fails: print("FAIL", x)
    print("PASS" if not fails else f"{len(fails)} FAILURES"); sys.exit(1 if fails else 0)
