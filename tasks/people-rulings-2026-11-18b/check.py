#!/usr/bin/env python3
"""Recompute and prove the people packet (owner rulings 2026-11-18b items 3 and 6).

Base = BASE env var, else merge-base of HEAD and origin/main; "now" = the working tree. Proves:
  frame recount at base (urlsplit rule vs an independent raw-text count, and by form); the pre-widening rule finds none of them;
  0 identifier URLs remain on people rows; the 13 evidence_people rows citing the UC form are unedited; every replacement has
  a new evidence row whose quote is found in order in its sha256-checked stored page and in the evidence note; people rows change
  only in public_profile_url, lab_url, sources, last_verified (frame rows) plus the two new blank status columns (every row);
  every status cell is blank (not recorded); new evidence ids only in EVD-396900..396949; PERSON-000359 is unchanged.
Then injects 8 defects into the "now" data and requires each to be caught. Exit 0 only when all hold.
"""
import copy, csv, os, re, subprocess, sys, uuid
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import *
import build

RAW_ID = re.compile(r'(?:[?&]unid=|researchdirectory\.uc\.edu/p/)[A-Za-z0-9]')  # independent of the urlsplit rule
def old_rule(cell):  # V-62 as merged in PR #379: only ?u= and /~ (kept here to show the widening is what catches the frame)
    return bool(re.search(r"[?&]u=[A-Za-z0-9]|/~[A-Za-z0-9]", cell or ""))

def git_show(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=REPO, capture_output=True, text=True, check=True).stdout

def base_ref():
    return os.environ.get("BASE") or subprocess.run(["git", "merge-base", "HEAD", "origin/main"], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()

has = has_account_identifier
def frame_ids(people): return [r["person_id"] for r in people if any(has(r[c]) for c in URL_COLS)]

def expected_cells(b, n):
    out = {}
    if n in build.BLANK:
        for c in ("public_profile_url", "lab_url"): out[c] = "" if has(b[c]) else b[c]
        srcs = [s for s in sources_list(b["sources"]) if not has(s)]
        if n in build.KEEP_SOURCE and build.KEEP_SOURCE[n] not in srcs: srcs.append(build.KEEP_SOURCE[n])
    else:
        url = build.PLAN[n][0]
        for c in ("public_profile_url", "lab_url"): out[c] = url if has(b[c]) else b[c]
        srcs = []
        for s in sources_list(b["sources"]):
            s = url if has(s) else s
            if s not in srcs: srcs.append(s)
        if url not in srcs: srcs.append(url)
    out["sources"] = ";".join(srcs)
    return out

def prove(base_people, base_ev, now_people, now_ev, witness, pages, pairs, man):
    bad = []
    bp = {r["person_id"]: r for r in base_people}
    base_frame = frame_ids(base_people)
    planned_ids = {"PERSON-%06d" % n for n in set(build.PLAN) | set(build.BLANK)}
    if set(base_frame) != planned_ids: bad.append(f"frame {sorted(set(base_frame) ^ planned_ids)} differs from the build plan")
    if frame_ids(now_people): bad.append(f"identifier URLs remain on people rows: {frame_ids(now_people)}")
    if [r["person_id"] for r in now_people] != [r["person_id"] for r in base_people]: bad.append("people row set or order changed")
    for r in now_people:
        if any((r.get(c) or "") != "" for c in NEW_COLS): bad.append(f"{r['person_id']} has a status cell set (every existing row stays blank)")
        b = bp.get(r["person_id"])
        if not b: continue
        diff = {c for c in r if c not in NEW_COLS and r[c] != b.get(c)}
        if diff - ALLOWED_COLS: bad.append(f"{r['person_id']} changed disallowed columns {sorted(diff - ALLOWED_COLS)}")
        if diff and r["person_id"] not in base_frame: bad.append(f"{r['person_id']} changed but is not a frame row")
        if r["person_id"] in base_frame and not r["sources"]: bad.append(f"{r['person_id']} sources empty")
    if next(r for r in now_people if r["person_id"] == "PERSON-000359") != {**bp["PERSON-000359"], "status": "", "status_date": ""}:
        bad.append("PERSON-000359 changed (it stays blank: no dated death source fetched)")
    now_by_id = {e["evidence_id"]: e for e in now_ev}
    for e in base_ev:
        if now_by_id.get(e["evidence_id"]) != e: bad.append(f"base evidence row {e['evidence_id']} edited or removed")
    base_ids = {x["evidence_id"] for x in base_ev}
    new = [e for e in now_ev if e["evidence_id"] not in base_ids]
    for e in new:
        if not EVD_LO <= int(e["evidence_id"][4:]) <= EVD_HI: bad.append(f"{e['evidence_id']} outside block {EVD_LO}-{EVD_HI}")
        if any(has(e[c]) for c in e): bad.append(f"{e['evidence_id']} carries an identifier URL")
    wit = {w["evidence_id"]: w for w in witness}
    if set(wit) != {e["evidence_id"] for e in new}: bad.append("witness.csv and new evidence rows differ")
    for e in new:
        w = wit.get(e["evidence_id"])
        if not w: continue
        row = next((r for r in now_people if r["person_id"] == e["record_id"]), None)
        if not row or e["source_ref"] not in sources_list(row["sources"]): bad.append(f"{e['evidence_id']} source_ref not in the row's sources")
        if e["record_id"] not in base_frame: bad.append(f"{e['evidence_id']} is on a non-frame row")
        segs = w["segments"].split(SEP.strip())
        if (w["url"], w["sha256"]) not in pairs: bad.append(f"{e['evidence_id']}: witness digest is not the fetch-manifest digest of its url")
        text = pages.get(w["sha256"])
        if text is None: bad.append(f"{e['evidence_id']}: stored page {w['sha256'][:12]} missing or hash mismatch")
        elif not in_order(text, segs): bad.append(f"{e['evidence_id']}: quote not found in order in stored page")
        if any(s.strip() not in e["notes"] for s in segs): bad.append(f"{e['evidence_id']}: note does not carry its quote")
        if w["url"] != e["source_ref"]: bad.append(f"{e['evidence_id']}: witness url differs from source_ref")
    per_person = {}
    for e in new: per_person.setdefault(e["record_id"], []).append(e)
    for n in sorted(set(build.PLAN) | set(build.BLANK)):
        pid = "PERSON-%06d" % n
        r = next((r for r in now_people if r["person_id"] == pid), None); b = bp.get(pid)
        if r is None or b is None: bad.append(f"{pid} missing"); continue
        got = per_person.get(pid, [])
        want = expected_cells(b, n)
        for c in URL_COLS:
            if r[c] != want[c]: bad.append(f"{pid} {c} is not its planned outcome")
        if n in build.BLANK:
            if got: bad.append(f"{pid} is a planned no-evidence row but has new evidence")
            if r["last_verified"] != b["last_verified"]: bad.append(f"{pid} no-evidence row but last_verified changed")
            continue
        if r["last_verified"] != TODAY: bad.append(f"{pid} replaced but last_verified not {TODAY}")
    # every field of every new evidence row, and every witness row, equals what the plan and the stored pages produce
    exp_ev, exp_wit = build.expected_evidence(base_people, base_ev, man)
    if sorted(new, key=lambda e: e["evidence_id"]) != sorted(exp_ev, key=lambda e: e["evidence_id"]):
        diff = [e["evidence_id"] for e in exp_ev if e not in new] + [e["evidence_id"] for e in new if e not in exp_ev]
        bad.append(f"new evidence rows differ from the planned rows in some field: {sorted(set(diff))}")
    if sorted(witness, key=lambda w: w["evidence_id"]) != sorted(exp_wit, key=lambda w: w["evidence_id"]):
        bad.append("witness.csv differs from the planned witness rows")
    for e in exp_ev:
        if build.EVD_ID[int(e["record_id"][7:])] > int(e["evidence_id"][4:]) or int(e["evidence_id"][4:]) >= build.EVD_ID[int(e["record_id"][7:])] + 1:
            bad.append(f"{e['evidence_id']} is not the id bound to {e['record_id']}")
    return bad

def main():
    base = base_ref()
    bpt, bev = git_show(base, "data/people.csv"), git_show(base, "data/evidence_people.csv")
    base_people, base_ev = read_csv(bpt), read_csv(bev)
    now_people = read_csv(open(REPO + "/data/people.csv", encoding="utf-8").read())
    now_ev = read_csv(open(REPO + "/data/evidence_people.csv", encoding="utf-8").read())
    witness = read_csv(open(HERE / "witness.csv", encoding="utf-8").read())
    bf = frame_ids(base_people)
    raw = sum(1 for r in base_people if any(RAW_ID.search(r[c]) for c in URL_COLS))
    unid = sum(1 for r in base_people if any(re.search(r"[?&]unid=[A-Za-z0-9]", r[c]) for c in URL_COLS))
    uc = sum(1 for r in base_people if any(re.search(r"researchdirectory\.uc\.edu/p/[A-Za-z0-9]", r[c]) for c in URL_COLS))
    fisid = sum(1 for r in base_people if any("fisid_" in r[c] for c in URL_COLS))
    old_hits = sum(1 for r in base_people if any(old_rule(r[c]) for c in URL_COLS))
    uc_ev = sum(1 for e in base_ev if any(has(e[c]) for c in e))
    form_ev = sum(1 for e in base_ev if any(RAW_ID.search(e[c]) for c in e))  # the 13 rows citing the unid / UC forms
    now_uc_ev = sum(1 for e in now_ev if any(has(e[c]) for c in e))
    no_ev = [p for p in bf if not any(e["record_id"] == p for e in now_ev if e["evidence_id"] not in {x["evidence_id"] for x in base_ev})]
    print(f"base {base[:9]}: people rows with an identifier URL (unit: people.csv rows, columns public_profile_url/lab_url/sources) {len(bf)} "
          f"(independent raw count {raw}); unid form {unid}, UC /p/ form {uc}; fisid_ rows accepted {fisid}; pre-widening rule finds {old_hits}; evidence_people rows citing the unid/UC forms {form_ev} (all identifier forms incl. earlier ?u= and /~: {uc_ev})")
    if form_ev != 13: print(f"NOTE: ruling counted 13 evidence rows citing the UC form at e1df30e4; recount here is {form_ev}")
    print(f"now: identifier rows {len(frame_ids(now_people))}; evidence_people rows citing them {now_uc_ev} (unchanged: {now_uc_ev == uc_ev}); "
          f"replaced with new evidence {len(bf) - len(no_ev)}, identifier removed without evidence {len(no_ev)}, held 0; new evidence rows {len(witness)}; "
          f"people rows {len(now_people)} (base {len(base_people)}), status cells set {sum(1 for r in now_people if r['status'] or r['status_date'])}")
    fails = []
    if raw != len(bf): fails.append(f"frame yield {len(bf)} differs from independent raw count {raw}")
    if old_hits != 0: fails.append("the pre-widening rule now finds frame rows: the widening is not what catches them")
    if now_uc_ev != uc_ev: fails.append("identifier-bearing evidence row count changed")
    pages = {}
    for sha in {w["sha256"] for w in witness}:
        try: pages[sha] = page_text(sha)
        except (OSError, ValueError): pass
    pairs = {(m["url"], m["sha256"]) for m in read_csv(open(HERE / "manifest.csv", encoding="utf-8").read())}
    pairs_persist = {(m["url"], m["sha256"]) for m in csv.DictReader(open(PERSIST + "manifest.csv"))}
    if not pairs <= pairs_persist: fails.append("committed manifest.csv has entries the persist manifest lacks")
    man = manifest()
    fails += prove(base_people, base_ev, now_people, now_ev, witness, pages, pairs, man)

    def inject(name, mut):
        p, e, w = copy.deepcopy(now_people), copy.deepcopy(now_ev), copy.deepcopy(witness)
        mut(p, e, w)
        caught = prove(base_people, base_ev, p, e, w, pages, pairs, man)
        print(f"inject {name}: {'caught' if caught else 'NOT CAUGHT'}")
        if not caught: fails.append(f"defect not caught: {name}")
    row = lambda p, n: next(r for r in p if r["person_id"] == n)
    inject("identifier URL left on a people row", lambda p, e, w: row(p, "PERSON-002010").update(sources="https://researchdirectory.uc.edu/" + "p/" + uuid.uuid4().hex))
    inject("old evidence row edited", lambda p, e, w: next(x for x in e if x["evidence_id"] == "EVD-280082").update(notes="edited"))
    inject("quote not on the stored page", lambda p, e, w: w[0].update(segments="Dr. Nobody Title: Chancellor of Mars"))
    inject("write to a cell outside scope (role)", lambda p, e, w: row(p, "PERSON-002010").update(role="department_chair"))
    inject("write to a cell outside scope on a non-frame row", lambda p, e, w: row(p, "PERSON-000001").update(research_specialties="x"))
    inject("status set on an existing row", lambda p, e, w: row(p, "PERSON-000359").update(status="deceased", status_date="2026-01-16"))
    inject("evidence id outside the block", lambda p, e, w: (e[-1].update(evidence_id="EVD-399999"), w[-1].update(evidence_id="EVD-399999")))
    inject("replacement without its evidence row", lambda p, e, w: ([e.remove(x) for x in [x for x in e if x["record_id"] == "PERSON-002010" and x["evidence_id"] >= "EVD-396900"]], [w.remove(x) for x in [x for x in w if x["person_id"] == "PERSON-002010"]]))
    inject("a source of an unaffected row dropped", lambda p, e, w: row(p, "PERSON-002112").update(sources=";".join(row(p, "PERSON-002112")["sources"].split(";")[1:])))
    inject("claim_detail of a new evidence row changed", lambda p, e, w: next(x for x in e if x["evidence_id"] == "EVD-396900").update(claim_detail="Wrong role: professor emeritus"))
    inject("source_class of a new evidence row changed", lambda p, e, w: next(x for x in e if x["evidence_id"] == "EVD-396900").update(source_class="government_filing"))
    inject("evidence id bound to another person (order-assigned)", lambda p, e, w: (next(x for x in e if x["evidence_id"] == "EVD-396900").update(record_id="PERSON-001303"), next(x for x in e if x["evidence_id"] == "EVD-396901").update(record_id="PERSON-000941")))
    def truncated_base():  # a base missing one frame row must be refused by the builder before anything is written
        cut = [r for r in base_people if r["person_id"] != "PERSON-000941"]
        try: build.guard(cut, [r for r in cut if frame_ids([r])])
        except SystemExit: caught = True
        else: caught = False
        print(f"inject truncated base (PERSON-000941 absent): {'refused' if caught else 'NOT REFUSED'}")
        if not caught: fails.append("defect not caught: truncated base")
    truncated_base()
    inject("planned no-evidence row given an evidence row", lambda p, e, w: (e.append({**e[-1], "evidence_id": "EVD-396940", "record_id": "PERSON-002011"}), w.append({**w[-1], "evidence_id": "EVD-396940", "person_id": "PERSON-002011"})))
    if fails:
        print("FAIL"); [print(" -", f) for f in fails]; sys.exit(1)
    print("OK: all proofs hold and all injected defects were caught")

if __name__ == "__main__":
    main()
