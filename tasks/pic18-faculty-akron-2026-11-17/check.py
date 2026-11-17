#!/usr/bin/env python3
"""Named check for the PIC-18 Akron faculty lane.   python3 tasks/pic18-faculty-akron-2026-11-17/check.py [--selftest]
Needs the persist folder (raw pages, sha256-named; see pagetext.P) and fails, rather than skips, when it is absent.
Recomputes verdict and frame counts (frame yield vs an independent count taken from the pages themselves), proves every quote is in its
stored page whose sha256 matches its name and is a manifest row, ties people rows to evidence rows (url and quote equal the verdict's),
proves no held people row changed and only the two allowed data files gained rows, IDs stay in block, and no email/phone appears in any
output (this file included). --selftest injects five defects and requires each to produce a failure the clean run does not have."""
import copy, csv, hashlib, io, json, re, subprocess, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from pagetext import P, quote_in, text, redact
from frame import build as build_frame
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IDENT = re.compile(r"[?&]u=[A-Za-z0-9_.-]+")  # a UA network id in a URL; committed files carry u=<id> only
PHONE = re.compile(r"(\(\d{3}\)\s*|\b\d{3}[-.])\d{3}[-.]\d{4}\b")
ALLOWED_DATA = {"data/people.csv", "data/evidence_people.csv"}
PBLOCK, EBLOCK = (2300, 2399), (393000, 393999)
PB_UNITS = ("SPSPE-adjunct", "SPSPE-emeritus")

def rd(p): return list(csv.DictReader(open(p, newline="", encoding="utf-8")))
def git(*a): return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout
def num(i): return int(i.split("-")[1])

def load():
    base = git("merge-base", "origin/main", "HEAD").strip()
    changed = set(git("diff", "--name-only", base).split()) | set(git("ls-files", "-o", "--exclude-standard").split())
    return dict(verdicts=rd(HERE / "verdicts.csv"), people=rd(ROOT / "data/people.csv"), evid=rd(ROOT / "data/evidence_people.csv"),
                base_people=list(csv.DictReader(io.StringIO(git("show", f"{base}:data/people.csv"), newline=""))),
                changed=changed, counts=json.load(open(HERE / "counts.json")),
                outputs={f.name: f.read_text(encoding="utf-8") for f in HERE.glob("*") if f.suffix in {".csv", ".md", ".json", ".py"}},
                manifest=rd(P / "manifest.csv"))

def independent_rows(sha, unit):
    """Row count taken from the page text, not from frame.py's parser."""
    t = text(sha)
    if unit in PB_UNITS:
        seg = t[t.find("Our " + ("Emeritus" if "emeritus" in unit else "Adjunct")):]
        return len(re.findall(r"\bDr\. ", seg.split("The University of Akron 302")[0]))
    return len(re.findall(r"\bTitle:", t))

def checks(w):
    f = []
    if not P.exists(): return [f"persist folder {P} missing: raw pages cannot be checked"]
    V, people, evid = w["verdicts"], w["people"], w["evid"]
    man = {(redact(m["url"]), m["sha256"]) for m in w["manifest"]}
    # 1. counts: verdicts from verdicts.csv; frame from the stored listing pages against the pages' own counts
    vc = Counter(r["verdict"].split()[0] for r in V)
    if dict(vc) != w["counts"]["verdicts"]: f.append(f"verdict counts drift {dict(vc)} vs {w['counts']['verdicts']}")
    fr = build_frame()
    if dict(Counter(r["unit"] for r in fr)) != w["counts"]["frame_rows_by_unit"]: f.append("frame counts drift vs counts.json")
    pages = {}
    for r in fr: pages.setdefault((r["unit"], r["listing_sha"]), 0); pages[(r["unit"], r["listing_sha"])] += 1
    for (unit, sha), n in pages.items():
        if (next(r["listing_url"] for r in fr if r["listing_sha"] == sha), sha) not in man: f.append(f"listing page {sha[:8]} not a manifest row")
        if independent_rows(sha, unit) != n: f.append(f"frame yield {n} != independent count {independent_rows(sha, unit)} on {unit} page {sha[:8]}")
    for unit in ("ME", "BME"):  # the listing's own "Total results" badge
        first = next(sha for (u, sha) in pages if u == unit)
        tot = int(re.search(r"Total results:\s*(\d+)", text(first)).group(1))
        if w["counts"]["frame_rows_by_unit"].get(unit) != tot: f.append(f"{unit} frame rows != the listing page's own 'Total results' {tot}")
    if len(V) != w["counts"]["persons_examined"]: f.append("persons_examined drift")
    rd_ = w["outputs"].get("README.md", "").replace("**", "")
    for k, n in w["counts"]["verdicts"].items():
        if f"{n} {k}" not in rd_: f.append(f"README does not state {n} {k}")
    for unit, n in w["counts"]["frame_rows_by_unit"].items():
        if not re.search(rf"\|\s*{n}\s*\|", rd_): f.append(f"README table lacks the frame row count {n} for {unit}")
    # 2. every quote: stored page, sha256 equals its name, a manifest row, words in order, <=25 words
    for r in V:
        for g in "ab":
            q, s, u = r[f"gate_{g}_quote"], r[f"gate_{g}_sha"], r[f"gate_{g}_url"]
            if not q:
                if r["verdict"] == "VERIFIED": f.append(f"{r['name']}: VERIFIED row without gate {g} quote")
                continue
            if not (P / s).exists(): f.append(f"{r['name']}: stored page {s[:8]} missing"); continue
            if hashlib.sha256((P / s).read_bytes()).hexdigest() != s: f.append(f"{r['name']}: sha256 of stored page does not match its name {s[:8]}")
            if (u, s) not in man: f.append(f"{r['name']}: gate {g} (url, sha) is not a manifest row")
            if not quote_in(q, s): f.append(f"{r['name']}: gate {g} quote not in stored page")
            if len(q.split()) > 25: f.append(f"{r['name']}: gate {g} quote over 25 words")
    # 3. people rows <-> evidence rows
    new = [p for p in people if PBLOCK[0] <= num(p["person_id"]) <= PBLOCK[1]]
    ver = [r for r in V if r["verdict"] == "VERIFIED"]
    if len(new) != len(ver): f.append(f"{len(new)} new people rows vs {len(ver)} VERIFIED verdicts")
    pids = {p["person_id"] for p in people}
    mine = [e for e in evid if EBLOCK[0] <= num(e["evidence_id"]) <= EBLOCK[1]]
    for p in new:
        v = next((v for v in ver if v["public_profile_url"] == p["public_profile_url"]), None)
        if not v or (v["role_as_published"], v["full_name"], v["role"], v["research_specialties"]) != (p["role_as_published"], p["full_name"], p["role"], p["research_specialties"]):
            f.append(f"{p['person_id']} does not match a VERIFIED verdict"); continue
        if p["institution_org_id"] != "ORG-000501" or p["verification_tier"] != "A" or p["last_verified"] != "2026-11-17": f.append(f"{p['person_id']} institution/tier/date")
        es = {e["claim_type"]: e for e in mine if e["record_id"] == p["person_id"]}
        if not {"existence", "scope"} <= set(es): f.append(f"{p['person_id']} lacks existence+scope evidence"); continue
        for ct, g in (("existence", "a"), ("scope", "b")):
            if es[ct]["source_ref"] != v[f"gate_{g}_url"] or es[ct]["notes"] != "Raw words in order: " + v[f"gate_{g}_quote"]: f.append(f"{es[ct]['evidence_id']} url/quote differs from the verdict")
    for e in mine:
        if e["record_id"] not in pids: f.append(f"{e['evidence_id']} dangling record")
        if e["created_by"] != "atlas-w17-fac-a" or e["observed_date"] != "2026-11-17": f.append(f"{e['evidence_id']} created_by/observed_date")
        if e["record_table"] != "people" or e["source_class"] != "own_site": f.append(f"{e['evidence_id']} table/class")
    # 4. no held row changed; only the two data files changed; IDs in block
    base = {p["person_id"]: p for p in w["base_people"]}
    cur = {p["person_id"]: p for p in people}
    for pid, row in base.items():
        if cur.get(pid) != row: f.append(f"held people row {pid} changed or removed")
    for p in people:
        if p["person_id"] not in base and not PBLOCK[0] <= num(p["person_id"]) <= PBLOCK[1]: f.append(f"{p['person_id']} outside block")
    dirty = {c for c in w["changed"] if not c.startswith("tasks/pic18-faculty-akron-2026-11-17/")}
    if dirty - ALLOWED_DATA: f.append(f"files changed outside brief: {sorted(dirty - ALLOWED_DATA)}")
    # 5. privacy: every output, the persist manifest, this file, and the new data rows
    blobs = dict(w["outputs"])
    blobs["new people rows"] = "\n".join(",".join(p.values()) for p in new); blobs["new evidence rows"] = "\n".join(",".join(e.values()) for e in mine)
    for n, b in blobs.items():
        if EMAIL.search(b) or PHONE.search(b): f.append(f"email/phone pattern in {n}")
        if IDENT.search(b): f.append(f"UA network identifier in a URL in {n}")
    if w["outputs"].get("manifest.csv", "").replace("\r\n", "\n") != redact(open(P / "manifest.csv", newline="", encoding="utf-8").read().replace("\r\n", "\n")):
        f.append("committed manifest.csv is not the redacted persist manifest")
    return f

def selftest(w):
    base = checks(w)
    if base: print("  clean run must pass before the injections mean anything"); return False
    ok = True
    mail = "jdoe" + "@" + "uakron.edu"  # built at runtime so this file scans clean
    def inject(name, mut, expect):
        nonlocal ok
        w2 = copy.deepcopy(w); mut(w2); got = checks(w2)
        hit = [x for x in got if expect in x]
        print(("  caught " if hit else "  MISSED "), name, "->", (hit[0][:90] if hit else got[:1]))
        ok &= bool(hit)
    ver = lambda w2: next(r for r in w2["verdicts"] if r["verdict"] == "VERIFIED")
    inject("altered quote", lambda w2: ver(w2).update(gate_b_quote=ver(w2)["gate_b_quote"] + " cryogenic"), "quote not in stored page")
    other = next(m["sha256"] for m in w["manifest"] if m["sha256"] != next(r for r in w["verdicts"] if r["verdict"] == "VERIFIED")["gate_b_sha"])
    inject("hash of a different stored page", lambda w2: ver(w2).update(gate_b_sha=other), "not a manifest row")
    inject("hash with no stored page", lambda w2: ver(w2).update(gate_b_sha="0" * 64), "stored page")
    fake = "1" * 64  # a stored file whose bytes do not hash to its name
    (P / fake).write_bytes(b"tampered")
    try: inject("stored page tampered", lambda w2: ver(w2).update(gate_b_sha=fake), "does not match its name")
    finally: (P / fake).unlink()
    inject("edited held row", lambda w2: w2["people"][0].update(role_as_published=w2["people"][0]["role_as_published"] + " X"), "held people row")
    inject("email in a data field", lambda w2: next(p for p in w2["people"] if p["person_id"] == "PERSON-002302").update(research_specialties="polymer thin films;" + mail), "email/phone pattern in new people rows")
    inject("UA id URL in a new data row", lambda w2: next(p for p in w2["people"] if p["person_id"] == "PERSON-002302").update(public_profile_url="https://www.uakron.edu/chemistry/faculty-staff/detail.dot" + "?u" + "=jutta"), "UA network identifier in a URL in new people rows")
    inject("extra file changed", lambda w2: w2["changed"].add("data/organizations_OH.csv"), "files changed outside brief")
    return ok

if __name__ == "__main__":
    w = load(); fails = checks(w)
    print("checks:", "PASS" if not fails else "FAIL"); [print("  FAIL", x) for x in fails]
    rc = 1 if fails else 0
    if "--selftest" in sys.argv:
        print("injected defects:"); rc |= 0 if selftest(w) else 1
    sys.exit(rc)
