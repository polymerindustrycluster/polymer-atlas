"""Restore the registry links dropped by commit 805528a (merged with PR #68 as bac5809, 2026-11-04).

805528a ("ID skimpy-state wave, rebased by integrator") added its 4 intended FRS links and
rewrote data/registry_links.csv from a stale copy, dropping 3,351 links that were on main at
its parent 91cd1a8 (the PR #67 merge; its registry file is byte-identical to 92393de's). This script re-appends every dropped link that is still valid on the
current tree, and writes a journal of every row it restores, re-points or holds.

Rules (in order, per lost row):
  1. key (org_id, registry, registry_id, site_id) already at HEAD -> nothing to do
  2. (registry, registry_id, site_id) at HEAD under another org -> HOLD: deliberate re-point
     after 2026-11-04 (e.g. the Ametek Nesquehoning plant -> Niche Polymer, #123)
  3. org-grain row (no site_id) whose (registry, registry_id) is at HEAD under another org -> HOLD
  4. org_id no longer exists -> HOLD
  5. site-keyed row whose site no longer exists -> HOLD
  6. site-keyed row whose site now belongs to another org -> RESTORE re-pointed to the site's
     current org (the site moved by a dated pass; V-6 requires site and org to agree)
  7. otherwise -> RESTORE as it was (tombstoned/merged orgs keep their own links as history)
Usage: python3 restore.py [--write]   (dry run without --write)
"""
import csv, io, subprocess, sys, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data"
BASE = "91cd1a8"   # parent of 805528a (PR #67 merge): last tree with the full link set
OUT = Path(__file__).resolve().parent

def key(r): return (r["org_id"], r["registry"], r["registry_id"], r.get("site_id", ""))

base_txt = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE}:data/registry_links.csv"],
                          capture_output=True, text=True, check=True).stdout
base = list(csv.DictReader(io.StringIO(base_txt)))
with open(D / "registry_links.csv", newline="") as f:
    rd = csv.DictReader(f); header = rd.fieldnames; head = list(rd)

orgs = {}
for p in glob.glob(str(D / "organizations_*.csv")) + [str(D / "ecosystem.csv")]:
    for r in csv.DictReader(open(p, newline="")):
        orgs[r["org_id"]] = r
site_org = {}
for p in glob.glob(str(D / "sites_*.csv")):
    for r in csv.DictReader(open(p, newline="")):
        site_org[r["site_id"]] = r["org_id"]

head_keys = {key(r) for r in head}
head_fac = {(r["registry"], r["registry_id"], r["site_id"]): r["org_id"] for r in head if r.get("site_id")}
head_orgid = {}
for r in head:
    if not r.get("site_id"):
        head_orgid.setdefault((r["registry"], r["registry_id"]), set()).add(r["org_id"])

restore, journal = [], []
for r in base:
    k = key(r)
    if k in head_keys:
        continue
    sid, oid = r.get("site_id", ""), r["org_id"]
    act, note, row = None, "", dict(r)
    if sid and (r["registry"], r["registry_id"], sid) in head_fac:
        act, note = "HOLD", f"re-pointed at HEAD to {head_fac[(r['registry'], r['registry_id'], sid)]}"
    elif not sid and (head_orgid.get((r["registry"], r["registry_id"])) or set()) - {oid}:
        act, note = "HOLD", f"same id held at HEAD by {sorted(head_orgid[(r['registry'], r['registry_id'])])}"
    elif oid not in orgs:
        act, note = "HOLD", "org_id no longer exists"
    elif sid and sid not in site_org:
        act, note = "HOLD", "site_id no longer exists"
    elif sid and site_org[sid] != oid:
        if site_org[sid] not in orgs:
            act, note = "HOLD", f"site now under unknown org {site_org[sid]}"
        else:
            act, note = "RESTORE_REPOINTED", f"site {sid} now belongs to {site_org[sid]} (was {oid})"
            row["org_id"] = site_org[sid]
    else:
        st = (orgs[oid].get("status") or "").strip()
        act = "RESTORE"
        if st in ("merged", "acquired", "closed", "tombstone", "renamed"):
            note = f"org status {st}; link kept on the original record as history"
    if act.startswith("RESTORE"):
        if key(row) in head_keys or key(row) in {key(x) for x in restore}:
            act, note = "SKIP_DUP", "re-pointed key already present"
        else:
            restore.append(row)
    journal.append({"action": act, **{c: r.get(c, "") for c in header}, "restored_org_id": row["org_id"] if act.startswith("RESTORE") else "", "note": note})

from collections import Counter
print("lost rows considered:", len(journal))
print(Counter(j["action"] for j in journal))
print(Counter(j["registry"] for j in journal if j["action"].startswith("RESTORE")))
assert len({key(x) for x in restore}) == len(restore), "duplicate restored keys"
if "--write" in sys.argv:
    if not restore:
        sys.exit("nothing left to restore; journal.csv kept as the record of the first --write")
    # journal only on a --write that restores rows, so a later run cannot overwrite the record
    with open(OUT / "journal.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(journal[0].keys()), lineterminator="\n"); w.writeheader(); w.writerows(journal)
    with open(D / "registry_links.csv", "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, lineterminator="\n")
        for row in restore:
            w.writerow({c: row.get(c, "") for c in header})
    print("appended", len(restore), "rows to data/registry_links.csv")
