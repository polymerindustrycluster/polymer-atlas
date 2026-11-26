#!/usr/bin/env python3
"""Named check for the HQ blank-city repair (ORG-000197 Kenda American Technology Center, audit FAIL of #563).

    python3 check.py [BASE]    BASE defaults to the merge-base with origin/main (the tree before this PR)

The clean state must give no problems, then every planted defect must give a problem that names its rule.
Exit 0 only when both hold. Reads git and data/ only; fetches nothing.
"""
import copy
import csv
import io
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TASK = HERE.name
BASE = sys.argv[1] if len(sys.argv) > 1 else subprocess.check_output(
    ["git", "-C", str(ROOT), "merge-base", "origin/main", "HEAD"], text=True).strip()

KENDA, EVD = "ORG-000197", ("EVD-421274", "EVD-483143")
# The cells #563 filled (and the county it kept), with their values on the base; all go blank. The notes cell gains one entry.
CLEARED = {"hq_city": "Green", "hq_state": "OH", "hq_country": "US", "hq_in_scope": "ne_ohio", "hq_county": "Summit"}
NOTE = " | 2026-11-25: HQ not established"
ALLOWED_FILES = re.compile(r"data/(organizations|evidence_organizations)_(US|OH)\.csv"
                           rf"|tasks/{TASK}/[^/]+|tasks/hq-blank-city-2026-11-25/AUDIT\.md|tasks/QUEUE\.md")


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def rows_of(blob):
    return list(csv.DictReader(io.StringIO(blob.decode(), newline="")))


def load(base):
    """{'orgs': {shard: rows}, 'evs': {shard: rows}, 'archive': rows}; the shard files are those organization records live in."""
    names = git("ls-tree", "--name-only", BASE, "data/").decode().split() if base else \
        [f"data/{p.name}" for p in (ROOT / "data").iterdir()]
    out = dict(orgs={}, evs={}, archive=rows_of(git("show", f"{BASE}:data/archive_links.csv") if base else (ROOT / "data/archive_links.csv").read_bytes()))
    for n in sorted(names):
        m = re.fullmatch(r"data/(organizations|evidence_organizations)_([A-Z]+)\.csv", n)
        if m:
            out["orgs" if m[1] == "organizations" else "evs"][m[2]] = rows_of(git("show", f"{BASE}:{n}") if base else (ROOT / n).read_bytes())
    return out


def flat(shard_map, key):
    return {r[key]: (s, r) for s, rs in shard_map.items() for r in rs}


def org_shard(o):  # SCHEMA Appendix C §2
    st, c = o["hq_state"].strip().upper(), o["hq_country"].strip().upper()
    return st if st else ("INTL" if c not in ("", "US", "USA", "UNITED STATES") else "US")


def problems(head, base, claims, changed):
    out = []
    ho, bo = flat(head["orgs"], "org_id"), flat(base["orgs"], "org_id")
    # cells: the only organization cells that changed are the five cleared ones and the notes of Kenda
    if set(ho) != set(bo):
        out.append(f"cells: organization ids differ from base: {sorted(set(ho) ^ set(bo))[:5]}")
    diff = {(i, k) for i in set(ho) & set(bo) for k in ho[i][1] if ho[i][1][k] != bo[i][1].get(k)}
    want = {(KENDA, k) for k in CLEARED} | {(KENDA, "notes")}
    if diff != want:
        out.append(f"cells: changed cells differ from the five cleared plus notes: only changed {sorted(diff - want)[:5]}, not changed {sorted(want - diff)[:5]}")
    if KENDA in ho and KENDA in bo:
        b, h = bo[KENDA][1], ho[KENDA][1]
        for k, v in CLEARED.items():
            if not (b[k] == v and h[k] == ""):
                out.append(f"cells: {KENDA} {k} is {b[k]!r} -> {h[k]!r}, not {v!r} -> ''")
        # note: the old notes are kept whole and one dated entry is appended
        if not (h["notes"].startswith(b["notes"] + NOTE) and len(h["notes"]) > len(b["notes"] + NOTE) + 40 and "2026-11-25" in h["notes"][len(b["notes"]):]):
            out.append("note: notes is not the old notes plus one 2026-11-25 'HQ not established' entry")
    # claims: one withdrawn row per cleared cell, no evidence id, nothing else
    got = sorted((c["table"], c["record_id"], c["field"], c["verdict"], c["evidence_id"]) for c in claims)
    exp = sorted(("organizations", KENDA, k, "withdrawn", "") for k in CLEARED)
    if got != exp:
        out.append(f"claims: CLAIMS_CHECKED.csv rows differ from the five withdrawn cells: extra {sorted(set(got) - set(exp))[:3]}, missing {sorted(set(exp) - set(got))[:3]}")
    # blank city: the audit 13 smoke runner's frame is empty
    bad = sorted(i for i, (_, r) in ho.items() if r["hq_county"].strip() and not r["hq_city"].strip())
    if bad:
        out.append(f"blank city: head organizations with hq_county set and hq_city blank: {bad[:5]}")
    # shard: Kenda sits where Appendix C places a record with no stated HQ; every other organization stays in its shard
    if KENDA in ho and (ho[KENDA][0], org_shard(ho[KENDA][1])) != ("US", "US"):
        out.append(f"shard: {KENDA} sits in {ho[KENDA][0]}, Appendix C places it in {org_shard(ho[KENDA][1])}, not US")
    moved = [i for i in set(ho) & set(bo) if i != KENDA and ho[i][0] != bo[i][0]]
    if moved:
        out.append(f"shard: organizations other than {KENDA} changed shard: {moved[:5]}")
    # evidence: no row added, lost or altered; Kenda's two rows travel with it
    he, be = flat(head["evs"], "evidence_id"), flat(base["evs"], "evidence_id")
    if set(he) != set(be):
        out.append(f"evidence: rows added {sorted(set(he) - set(be))[:5]}, lost {sorted(set(be) - set(he))[:5]}")
    for e in set(he) & set(be):
        if he[e][1] != be[e][1]:
            out.append(f"evidence: {e} changed")
    for e in EVD:
        if e in he and KENDA in ho and he[e][0] != ho[KENDA][0]:
            out.append(f"evidence: {e} sits in {he[e][0]}, its organization in {ho[KENDA][0]}")
    for e, (s, r) in he.items():
        if r["record_table"] == "organizations" and r["record_id"] in ho and e not in EVD and e in be and s != be[e][0]:
            out.append(f"evidence: {e} changed shard but is not one of {EVD}")
            break
    if head["archive"] != base["archive"]:
        out.append("archive: archive_links.csv differs from base")
    # files
    stray = sorted(p for p in changed if not ALLOWED_FILES.fullmatch(p))
    if stray:
        out.append(f"files: changed outside the allowed set: {stray[:5]}")
    return out


def main():
    base, head = load(True), load(False)
    claims = rows_of((HERE / "CLAIMS_CHECKED.csv").read_bytes())
    changed = sorted(set(git("diff", "--name-only", BASE).decode().split() +
                         git("ls-files", "--others", "--exclude-standard").decode().split()))
    args = dict(head=head, base=base, claims=claims, changed=changed)
    clean = problems(**args)
    for p in clean:
        print("CLEAN STATE PROBLEM:", p)
    if clean:
        sys.exit(1)

    def plant(name, rule, mutate):
        a = copy.deepcopy(args)
        mutate(a)
        hit = [g for g in problems(**a) if g.startswith(rule)]
        print(("planted " if hit else "MISSED  ") + name + (": " + hit[0][:110] if hit else ""))
        return bool(hit)

    def org(a, i):
        return flat(a["head"]["orgs"], "org_id")[i][1]

    def ev(a, e):
        return flat(a["head"]["evs"], "evidence_id")[e][1]

    def move_org(a, src, dst):
        r = org(a, KENDA)
        a["head"]["orgs"][src].remove(r)
        a["head"]["orgs"][dst].append(r)

    def lose_evidence(a):
        a["head"]["evs"]["US"].remove(ev(a, EVD[0]))

    def evidence_left_behind(a):
        r = ev(a, EVD[1])
        a["head"]["evs"]["US"].remove(r)
        a["head"]["evs"]["OH"].append(r)

    def extra_evidence(a):
        a["head"]["evs"]["US"].append({**ev(a, EVD[0]), "evidence_id": "EVD-999999"})

    def ninth_owner(a):  # a ninth organization loses a county and the claims file is edited to match: the change set is fixed
        org(a, "ORG-000001")["hq_county"] = ""

    results = [
        plant("a cell outside the claims (Kenda description_1line)", "cells", lambda a: org(a, KENDA).__setitem__("description_1line", "x")),
        plant("another organization's cell changed (ORG-000022 hq_in_scope)", "cells", lambda a: org(a, "ORG-000022").__setitem__("hq_in_scope", "national_us")),
        plant("a ninth organization's county cleared", "cells", ninth_owner),
        plant("a cleared cell left at its old value (Kenda hq_county)", "cells", lambda a: org(a, KENDA).__setitem__("hq_county", "Summit")),
        plant("Kenda's city refilled (Green)", "cells", lambda a: org(a, KENDA).__setitem__("hq_city", "Green")),
        plant("a county with no city (Kenda hq_county Summit)", "blank city", lambda a: org(a, KENDA).__setitem__("hq_county", "Summit")),
        plant("the move missing: Kenda left in the OH shard", "shard", lambda a: move_org(a, "US", "OH")),
        plant("Kenda moved to a state shard with blank HQ state", "shard", lambda a: move_org(a, "US", "PA")),
        plant("the note lost", "note", lambda a: org(a, KENDA).__setitem__("notes", flat(base["orgs"], "org_id")[KENDA][1]["notes"])),
        plant("the old notes overwritten by the new entry", "note", lambda a: org(a, KENDA).__setitem__("notes", NOTE + ": x" * 20)),
        plant("a withdrawn row dropped", "claims", lambda a: a.__setitem__("claims", a["claims"][:-1])),
        plant("a claim marked corrected", "claims", lambda a: a["claims"][0].__setitem__("verdict", "corrected")),
        plant("a claim row for a ninth organization", "claims", lambda a: a["claims"].append(dict(a["claims"][0], record_id="ORG-000001"))),
        plant("Kenda's old evidence row lost", "evidence", lose_evidence),
        plant("Kenda's new evidence row left in the OH shard", "evidence", evidence_left_behind),
        plant("an evidence row added", "evidence", extra_evidence),
        plant("an evidence row altered", "evidence", lambda a: ev(a, EVD[1]).__setitem__("claim_detail", ev(a, EVD[1])["claim_detail"] + " x")),
        plant("an archive link dropped", "archive", lambda a: a["head"]["archive"].pop()),
        plant("a site file changed", "files", lambda a: a["changed"].append("data/sites_OH.csv")),
    ]
    if not all(results):
        print("FAIL: a planted defect was not caught")
        sys.exit(1)
    print(f"OK: {KENDA} five HQ cells withdrawn, moved to the US shard with {len(EVD)} evidence rows, no evidence row added; "
          f"{len(results)} planted defects caught")


if __name__ == "__main__":
    main()
