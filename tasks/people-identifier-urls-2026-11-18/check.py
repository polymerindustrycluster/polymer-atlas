#!/usr/bin/env python3
"""Recompute and prove the people identifier-URL packet (owner rulings 2026-11-18 items 1 and 1b).

Base = BASE env var, else merge-base of HEAD and origin/main; "now" = the working tree. Proves:
  frame recount at base (csv rows vs an independent raw-line count) and now; 0 identifier URLs remain on people rows;
  every replaced row has new evidence rows whose quotes are found, in order, in the stored page (sha256-checked) and in
  the evidence note; every blanked row still has non-empty sources; no base evidence row changed, new ids only in
  EVD-396100..396199; people rows change only in public_profile_url, lab_url, sources, last_verified, and only on frame rows.
Then injects 5 defects into the "now" data and requires each to be caught. Exit 0 only when all hold.
"""
import csv, json, os, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import *
import build  # PLAN / BLANK / EXTRA / NARROW: the intended outcome per row, independent of what evidence survived

# independent of the urlsplit rule: a raw-text regex over the base file's lines, used only to count the frame
import re
RAW_ID = re.compile(r'[\w.-]+\.[A-Za-z]{2,}[^\s,"]*(?:[?&]u=|/~)[A-Za-z0-9]')

def git_show(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=REPO, capture_output=True, text=True, check=True).stdout

def base_ref():
    return os.environ.get("BASE") or subprocess.run(["git", "merge-base", "HEAD", "origin/main"], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()

def frame_ids(people):
    return [r["person_id"] for r in people if any(has_id(r[c]) for c in URL_COLS)]

def expected_cells(b, n):
    """Planned value of each URL cell of base row b for person number n, from the plan alone."""
    out = {}
    if n in build.BLANK:
        for c in ("public_profile_url", "lab_url"): out[c] = "" if has_id(b[c]) else b[c]
        srcs = [s for s in sources_list(b["sources"]) if not has_id(s)]
        if not srcs and n in build.KEEP_SOURCE: srcs = [build.KEEP_SOURCE[n]]
    else:
        url = build.PLAN[n][0]
        for c in ("public_profile_url", "lab_url"): out[c] = url if has_id(b[c]) else b[c]
        srcs = []
        for s in sources_list(b["sources"]):
            s = url if has_id(s) else s
            if s not in srcs: srcs.append(s)
        for p in [build.PLAN[n]] + ([build.EXTRA[n]] if n in build.EXTRA else []):
            if p[0] not in srcs: srcs.append(p[0])
    out["sources"] = ";".join(srcs)
    return out

def prove(base_people, base_ev, now_people, now_ev, witness, pages, pairs):
    """Return a list of failures (empty = all proofs hold). pages: sha -> visible text."""
    bad = []
    bp = {r["person_id"]: r for r in base_people}
    base_frame = frame_ids(base_people)
    expected = {"PERSON-%06d" % n for n in set(build.PLAN) | set(build.BLANK)}
    if set(base_frame) != expected: bad.append(f"frame {sorted(set(base_frame) ^ expected)} differs from the build plan")
    if frame_ids(now_people):
        bad.append(f"identifier URLs remain on people rows: {frame_ids(now_people)}")
    if len(now_people) != len(base_people) or [r["person_id"] for r in now_people] != [r["person_id"] for r in base_people]:
        bad.append("people row set or order changed")
    for r in now_people:
        b = bp.get(r["person_id"])
        if not b: continue
        diff = {c for c in r if r[c] != b.get(c)}
        if diff - ALLOWED_COLS: bad.append(f"{r['person_id']} changed disallowed columns {sorted(diff - ALLOWED_COLS)}")
        if diff and r["person_id"] not in base_frame: bad.append(f"{r['person_id']} changed but is not a frame row")
        if r["person_id"] in base_frame and not r["sources"]: bad.append(f"{r['person_id']} sources empty")
    # evidence: append-only
    now_by_id = {e["evidence_id"]: e for e in now_ev}
    for e in base_ev:
        if now_by_id.get(e["evidence_id"]) != e: bad.append(f"base evidence row {e['evidence_id']} edited or removed")
    new = [e for e in now_ev if e["evidence_id"] not in {x["evidence_id"] for x in base_ev}]
    for e in new:
        n = int(e["evidence_id"][4:])
        if not EVD_LO <= n <= EVD_HI: bad.append(f"{e['evidence_id']} outside block {EVD_LO}-{EVD_HI}")
        if has_id(e["source_ref"]) or any(has_id(e[c]) for c in e): bad.append(f"{e['evidence_id']} carries an identifier URL")
    # every replacement: new evidence row, quote in stored page and in note
    wit = {w["evidence_id"]: w for w in witness}
    if set(wit) != {e["evidence_id"] for e in new}: bad.append("witness.csv and new evidence rows differ")
    replaced = set()
    for e in new:
        w = wit.get(e["evidence_id"])
        if not w: continue
        replaced.add(e["record_id"])
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
    cited = {(e["record_id"], e["source_ref"]) for e in new}
    per_person = {}
    for e in new: per_person.setdefault(e["record_id"], []).append(e)
    for n in sorted(set(build.PLAN) | set(build.BLANK)):
        pid = "PERSON-%06d" % n
        r = next((r for r in now_people if r["person_id"] == pid), None); b = bp.get(pid)
        if r is None or b is None: bad.append(f"{pid} missing"); continue
        got = per_person.get(pid, [])
        # planned outcome of every URL cell (replaced with the planned URL, or blanked) and the other URLs preserved
        want_cells = expected_cells(b, n)
        for c in URL_COLS:
            if r[c] != want_cells[c]: bad.append(f"{pid} {c} is not its planned outcome")
        if n in build.BLANK:
            if got: bad.append(f"{pid} is a planned blank but has new evidence")
            if r["last_verified"] != b["last_verified"]: bad.append(f"{pid} blanked but last_verified changed")
            continue
        pages_ = [build.PLAN[n]] + ([build.EXTRA[n]] if n in build.EXTRA else [])
        planned = sorted((c[0], p[0], c[2], SEP.join(c[3])) for p in pages_ for c in p[2])
        have = sorted((e["claim_type"], e["source_ref"], e["tier_effect"], (wit.get(e["evidence_id"]) or {}).get("segments")) for e in got)
        if have != planned:
            bad.append(f"{pid} is a planned replacement; its evidence rows or witness quotes differ from the plan ({len(got)} found, {len(planned)} planned)")
        for e in got:
            if any(s.strip() not in e["notes"] for s in (wit.get(e["evidence_id"]) or {"segments": ""})["segments"].split(SEP.strip())):
                bad.append(f"{e['evidence_id']}: note does not carry the planned person's quote")
        if r["last_verified"] != TODAY: bad.append(f"{pid} replaced but last_verified not {TODAY}")
    return bad

def load_pages(witness):
    pages = {}
    for sha in {w["sha256"] for w in witness}:
        try: pages[sha] = page_text(sha)
        except (OSError, ValueError): pass
    return pages

def main():
    base = base_ref()
    bpt, bev = git_show(base, "data/people.csv"), git_show(base, "data/evidence_people.csv")
    base_people, base_ev = read_csv(bpt), read_csv(bev)
    now_people = read_csv(open(REPO + "/data/people.csv", encoding="utf-8").read())
    now_ev = read_csv(open(REPO + "/data/evidence_people.csv", encoding="utf-8").read())
    witness = read_csv(open(HERE / "witness.csv", encoding="utf-8").read())
    bf = frame_ids(base_people)
    raw = sum(1 for ln in bpt.splitlines() if ln.startswith("PERSON-") and RAW_ID.search(ln))
    by_form = {"?u=": sum(1 for r in base_people if any(__import__("re").search(r"[?&]u=[A-Za-z0-9]", r[c]) for c in URL_COLS)),
               "/~": sum(1 for r in base_people if any(__import__("re").search(r"/~[A-Za-z0-9]", r[c]) for c in URL_COLS))}
    base_idev = sum(1 for e in base_ev if any(has_id(e[c]) for c in e))
    now_idev = sum(1 for e in now_ev if any(has_id(e[c]) for c in e))
    blanked = [p for p in bf if not any(e["record_id"] == p for e in now_ev if e["evidence_id"] not in {x["evidence_id"] for x in base_ev})]
    replaced = [p for p in bf if p not in blanked]
    print(f"base {base[:9]}: frame rows {len(bf)} (independent raw-line count {raw}); by form {by_form}; people-table cells with identifier: "
          f"{sum(has_id(r[c]) for r in base_people for c in URL_COLS)}; identifier-bearing evidence_people rows {base_idev}")
    print(f"now: identifier rows on people {len(frame_ids(now_people))}; evidence rows citing identifier URLs {now_idev} (unchanged: {now_idev == base_idev}); "
          f"replaced {len(replaced)}, blanked {len(blanked)}, held 0; new evidence rows {len(witness)}")
    fails = []
    if raw != len(bf): fails.append(f"frame yield {len(bf)} differs from independent raw-line count {raw}")
    if now_idev != base_idev: fails.append("identifier-bearing evidence row count changed")
    pages = load_pages(witness)
    # committed manifest.csv == common.redact(persist manifest), byte for byte: every row and column (build.py writes exactly that)
    want = redact(open(PERSIST + "manifest.csv", encoding="utf-8").read()).replace("\r\n", "\n").encode()
    if (HERE / "manifest.csv").read_bytes() != want: fails.append("committed manifest.csv differs from the redacted persist manifest")
    for n in sorted(build.BLANK):
        pid = "PERSON-%06d" % n
        old = [e for e in base_ev if e["record_id"] == pid]
        row = next(r for r in now_people if r["person_id"] == pid)
        print(f"blank {pid}: base evidence rows {len(old)}, citing the removed URL {sum(any(has_id(e[c]) for c in e) for e in old)}, sources now {len(sources_list(row['sources']))}")
    fails += prove(base_people, base_ev, now_people, now_ev, witness, pages, pairs)

    # ---- inject defects; each must be caught ----
    import copy
    def inject(name, mut):
        p, e, w = copy.deepcopy(now_people), copy.deepcopy(now_ev), copy.deepcopy(witness)
        mut(p, e, w)
        caught = prove(base_people, base_ev, p, e, w, pages, pairs)
        print(f"inject {name}: {'caught' if caught else 'NOT CAUGHT'}")
        if not caught: fails.append(f"defect not caught: {name}")
    rep = replaced[0]
    inject("identifier URL put back on a people row", lambda p, e, w: next(r for r in p if r["person_id"] == rep).update(public_profile_url="https://www.example.edu/p.dot?" + "u=abc"))
    inject("old evidence row edited", lambda p, e, w: next(x for x in e if x["evidence_id"] == "EVD-333160").update(notes="edited"))
    inject("quote not on the stored page", lambda p, e, w: w[0].update(segments="Dr. Nobody Title: Chancellor of Mars"))
    inject("disallowed column changed", lambda p, e, w: next(r for r in p if r["person_id"] == rep).update(role="department_chair"))
    inject("evidence id outside the block", lambda p, e, w: (e[-1].update(evidence_id="EVD-399999"), w[-1].update(evidence_id="EVD-399999")))
    inject("replacement without its evidence row", lambda p, e, w: ([e.remove(x) for x in [x for x in e if x["record_id"] == rep and x["evidence_id"] >= "EVD-396100"]], [w.remove(x) for x in [x for x in w if x["person_id"] == rep]]))
    def only_evidence_of_1132(p, e, w):
        ids = {x["evidence_id"] for x in w if x["person_id"] == "PERSON-001132"}
        e[:] = [x for x in e if x["evidence_id"] not in ids]; w[:] = [x for x in w if x["evidence_id"] not in ids]
    inject("only evidence of a source-only replacement deleted", only_evidence_of_1132)
    def swap_digest(p, e, w):
        w[0].update(sha256=w[-1]["sha256"], segments=w[-1]["segments"])
        next(x for x in e if x["evidence_id"] == w[0]["evidence_id"])["notes"] = w[-1]["segments"]
    inject("witness digest and quote swapped for another page's", swap_digest)
    def swapped_person(p, e, w):  # a genuine quote from the same page, but another person's, in note and witness
        a = next(x for x in w if x["person_id"] == "PERSON-000043"); b = next(x for x in w if x["person_id"] == "PERSON-000045")
        r = next(x for x in e if x["evidence_id"] == a["evidence_id"])
        r["notes"] = r["notes"].replace(a["segments"], b["segments"]); a["segments"] = b["segments"]
    inject("another person's real quote on a roster page", swapped_person)
    inject("planned replacement left with an empty profile URL", lambda p, e, w: next(r for r in p if r["person_id"] == "PERSON-000043").update(public_profile_url=""))
    inject("planned blank given an unwitnessed URL", lambda p, e, w: next(r for r in p if r["person_id"] == "PERSON-000075").update(public_profile_url="https://example.invalid/"))
    def drop_other_source(p, e, w):  # PERSON-000050 keeps an unrelated source that must survive
        r = next(x for x in p if x["person_id"] == "PERSON-000050"); parts = r["sources"].split(";")
        assert len(parts) > 1; r["sources"] = ";".join(parts[1:])
    inject("unaffected source URL dropped", drop_other_source)
    if fails:
        print("FAIL"); [print(" -", f) for f in fails]; sys.exit(1)
    print("OK: all proofs hold and all injected defects were caught")

if __name__ == "__main__":
    main()
