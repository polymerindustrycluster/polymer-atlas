#!/usr/bin/env python3
"""Named check for the PIC-18 Akron faculty lane.   python3 tasks/pic18-faculty-akron-2026-11-17/check.py [--selftest]
Recomputes verdict and frame counts, proves every VERIFIED quote is in its stored page (sha256 matches the file name), ties people rows to
evidence rows, proves no held people row changed and only the two allowed data files gained rows, IDs stay in block, and no email/phone
appears in any output. --selftest runs the checks against four injected defects and requires each to fail."""
import copy, csv, hashlib, io, json, re, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from pagetext import P, quote_in, text
from frame import build as build_frame
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(\(\d{3}\)\s*|\b\d{3}[-.])\d{3}[-.]\d{4}\b")
ALLOWED_DATA = {"data/people.csv", "data/evidence_people.csv"}
PBLOCK, EBLOCK = (2300, 2399), (393000, 393999)

def rd(p): return list(csv.DictReader(open(p, newline="", encoding="utf-8")))
def git(*a): return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout
def num(i): return int(i.split("-")[1])

def load():
    base = git("merge-base", "origin/main", "HEAD").strip()
    changed = set(git("diff", "--name-only", base).split()) | set(git("ls-files", "-o", "--exclude-standard").split())
    return dict(verdicts=rd(HERE / "verdicts.csv"), people=rd(ROOT / "data/people.csv"), evid=rd(ROOT / "data/evidence_people.csv"),
                base_people=list(csv.DictReader(io.StringIO(git("show", f"{base}:data/people.csv"), newline=""))),
                changed=changed, outputs={f.name: f.read_text(encoding="utf-8") for f in HERE.glob("*") if f.suffix in {".csv", ".md", ".json", ".py"} and f.name != "check.py"},
                manifest_text=(P / "manifest.csv").read_text(encoding="utf-8"), counts=json.load(open(HERE / "counts.json")))

def checks(w):
    f = []
    V, people, evid = w["verdicts"], w["people"], w["evid"]
    # 1. counts recompute: verdicts from verdicts.csv, frame from the stored listing pages vs an independent count of the pages' own rows
    vc = Counter(r["verdict"].split()[0] for r in V)
    if dict(vc) != w["counts"]["verdicts"]: f.append(f"verdict counts drift {dict(vc)} vs {w['counts']['verdicts']}")
    fr = build_frame()
    if dict(Counter(r["unit"] for r in fr)) != w["counts"]["frame_rows_by_unit"]: f.append("frame counts drift vs counts.json")
    seen_pages = {}
    for r in fr: seen_pages[r["listing_sha"]] = seen_pages.get(r["listing_sha"], 0) + 1
    for sha, n in seen_pages.items():
        t = text(sha)
        indep = len(re.findall(r"Title:", t)) if "Our Emeritus" not in t and "Our Adjunct" not in t else None
        if indep is not None and indep != n: f.append(f"frame yield {n} != independent 'Title:' count {indep} on page {sha[:8]}")
    for unit, tot in (("ME", 63), ("BME", 21)):
        if w["counts"]["frame_rows_by_unit"].get(unit) != tot: f.append(f"{unit} frame rows != the listing page's own 'Total results' {tot}")
    if len(V) != w["counts"]["persons_examined"]: f.append("persons_examined drift")
    rd_ = w["outputs"].get("README.md", "")
    for k, n in w["counts"]["verdicts"].items():
        if f"{n} {k}" not in rd_.replace("**", ""): f.append(f"README does not state {n} {k}")
    for unit, n in w["counts"]["frame_rows_by_unit"].items():
        if not re.search(rf"\|\s*{n}\s*\|", rd_): f.append(f"README table lacks the frame row count {n} for {unit}")
    # 2. every quote in every verdict row: stored page, matching sha256, words in order, <=25 words
    for r in V:
        for g in "ab":
            q, s = r[f"gate_{g}_quote"], r[f"gate_{g}_sha"]
            if not q: 
                if r["verdict"] == "VERIFIED": f.append(f"{r['name']}: VERIFIED row without gate {g} quote")
                continue
            if not (P / s).exists(): f.append(f"{r['name']}: stored page {s[:8]} missing"); continue
            if hashlib.sha256((P / s).read_bytes()).hexdigest() != s: f.append(f"{r['name']}: sha256 of stored page does not match its name {s[:8]}")
            if not quote_in(q, s): f.append(f"{r['name']}: gate {g} quote not in stored page")
            if len(q.split()) > 25: f.append(f"{r['name']}: gate {g} quote over 25 words")
    # 3. people rows <-> evidence rows
    new = [p for p in people if PBLOCK[0] <= num(p["person_id"]) <= PBLOCK[1]]
    ver = [r for r in V if r["verdict"] == "VERIFIED"]
    if len(new) != len(ver): f.append(f"{len(new)} new people rows vs {len(ver)} VERIFIED verdicts")
    pids = {p["person_id"] for p in people}
    for p in new:
        cl = {e["claim_type"] for e in evid if e["record_id"] == p["person_id"] and e["evidence_id"].startswith("EVD-393")}
        if not {"existence", "scope"} <= cl: f.append(f"{p['person_id']} lacks existence+scope evidence")
        if p["institution_org_id"] != "ORG-000501": f.append(f"{p['person_id']} institution")
        if not any(v["public_profile_url"] == p["public_profile_url"] and v["role_as_published"] == p["role_as_published"] and v["full_name"] == p["full_name"] for v in ver): f.append(f"{p['person_id']} does not match a VERIFIED verdict")
    mine = [e for e in evid if EBLOCK[0] <= num(e["evidence_id"]) <= EBLOCK[1]]
    for e in mine:
        if e["record_id"] not in pids: f.append(f"{e['evidence_id']} dangling record")
        if e["created_by"] != "atlas-w17-fac-a" or e["observed_date"] != "2026-11-17": f.append(f"{e['evidence_id']} created_by/observed_date")
        if e["record_table"] != "people" or e["source_class"] != "own_site": f.append(f"{e['evidence_id']} table/class")
    # 4. no held row changed; only the two data files changed; IDs in block
    base = {p["person_id"]: p for p in w["base_people"]}
    for pid, row in base.items():
        cur = next((p for p in people if p["person_id"] == pid), None)
        if cur != row: f.append(f"held people row {pid} changed or removed")
    for p in people:
        if p["person_id"] not in base and not PBLOCK[0] <= num(p["person_id"]) <= PBLOCK[1]: f.append(f"{p['person_id']} outside block")
    dirty = {c for c in w["changed"] if not c.startswith("tasks/pic18-faculty-akron-2026-11-17/")}
    if dirty - ALLOWED_DATA: f.append(f"files changed outside brief: {sorted(dirty - ALLOWED_DATA)}")
    # 5. privacy
    blobs = dict(w["outputs"]); blobs["manifest.csv(persist)"] = w["manifest_text"]
    blobs["new people rows"] = "\n".join(",".join(p.values()) for p in new); blobs["new evidence rows"] = "\n".join(",".join(e.values()) for e in mine)
    for n, b in blobs.items():
        if EMAIL.search(b) or PHONE.search(b): f.append(f"email/phone pattern in {n}")
    return f

def selftest(w):
    ok = not checks(w) or print("  baseline must pass before the injection test means anything")
    def inject(name, mut):
        nonlocal ok
        w2 = copy.deepcopy(w); mut(w2); got = checks(w2)
        print(("  caught " if got else "  MISSED "), name, "->", (got[0][:90] if got else "")); ok &= bool(got)
    def altered_quote(w2): v = next(r for r in w2["verdicts"] if r["verdict"] == "VERIFIED"); v["gate_b_quote"] += " cryogenic"
    def wrong_hash(w2): v = next(r for r in w2["verdicts"] if r["verdict"] == "VERIFIED"); v["gate_b_sha"] = "0" * 64
    def edited_held(w2): w2["people"][0]["role_as_published"] += " X"
    def email(w2): w2["outputs"]["README.md"] = w2["outputs"].get("README.md", "") + " contact jdoe@uakron.edu"
    for n, m in (("altered quote", altered_quote), ("wrong hash", wrong_hash), ("edited held row", edited_held), ("email in output", email)): inject(n, m)
    return ok

if __name__ == "__main__":
    w = load(); fails = checks(w)
    print("checks:", "PASS" if not fails else "FAIL"); [print("  FAIL", x) for x in fails]
    rc = 1 if fails else 0
    if "--selftest" in sys.argv:
        print("injected defects:"); rc |= 0 if selftest(w) else 1
    sys.exit(rc)
