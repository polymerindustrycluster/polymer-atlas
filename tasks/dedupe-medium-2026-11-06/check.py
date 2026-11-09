#!/usr/bin/env python3
"""Named check for the dedupe-medium packet. Exit 0 = PASS. Read-only.

  python3 tasks/dedupe-medium-2026-11-06/check.py            # full check (needs the persist/ pages and the FRS cache)
  python3 tasks/dedupe-medium-2026-11-06/check.py --offline  # skip ONLY the FRS-cache comparison, and say so
  python3 tasks/dedupe-medium-2026-11-06/check.py --selftest # plant defects; each must make the check fail

What it proves (every item fails closed):
  frame      verdicts.csv has exactly the strength=medium clusters of site-name-dedupe leads.csv (34), one row each,
             records column equal to leads.csv
  verdicts   grammar; verdict and survivor re-derived from the org-level pairs; STILL_UNCERTAIN names a settling fact
  chains     every DUPLICATE_OF survivor exists, is live (org status active) and is never itself folded; no record is
             folded twice; no record is the survivor of two clusters; recorded folds are visible in the tree
             (status merged/acquired + successor, or a tombstone note); to_apply folds are re-derived from data/
  actions    repoint targets are live orgs; hold_operator names a settling fact
  sources    every TREE/FRS/WEB token resolves; cached pages match their sha256 and contain the quote
  data       no file under data/ differs from origin/main
"""
import csv
import difflib
import glob
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEADS = ROOT / "tasks/site-name-dedupe-2026-11-06/leads.csv"
PERSIST = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/dedupe-medium-2026-11-06")
FRS_DB = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/cache/bulk/frs.sqlite")
csv.field_size_limit(10 ** 9)

VERDICT_COLS = ["cluster", "name_key", "records", "verdict", "survivor", "org_state", "deciding_or_settling_fact", "sources",
                "site_folds_to_apply", "operator_actions", "lookups"]
COST_COLS = ["folded_evidence", "folded_registry_links", "folded_relationships", "survivor_evidence", "survivor_registry_links", "survivor_relationships"]
PAIR_COLS = ["pair_id", "cluster", "level", "record_a", "record_b", "verdict", "survivor", "state", "basis", "operator_org", "fact",
             "sources"] + COST_COLS
ACTION_COLS = ["action_id", "cluster", "action", "record", "target", "state", "fact", "sources"]
GRAMMAR = {"DUPLICATE_OF", "DISTINCT", "STILL_UNCERTAIN"}
EXPECTED_MEDIUM = 34          # independent count: strength == medium in PR #244's leads.csv README table
DIRS = {"n", "s", "e", "w", "ne", "nw", "se", "sw", "north", "south", "east", "west", "ridc"}


# ------------------------------------------------------------------ shared with build.py
def load_leads():
    with open(LEADS, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r["strength"] == "medium"]


def folded_of(p):
    return p["record_b"] if p["survivor"] == p["record_a"] else p["record_a"]


def derive_verdict(org_pairs):
    """Cluster verdict from its org-level pairs. Open (not 'recorded') pairs decide; if every org pair is already
    recorded in the tree, the cluster is DUPLICATE_OF (state recorded)."""
    open_ = [p for p in org_pairs if p["state"] != "recorded"]
    if open_:
        for v in ("DUPLICATE_OF", "STILL_UNCERTAIN", "DISTINCT"):
            hit = [p for p in open_ if p["verdict"] == v]
            if hit:
                return v, ";".join(p["survivor"] for p in hit if v == "DUPLICATE_OF"), ("to_apply" if v == "DUPLICATE_OF" else "n/a")
    rec = [p for p in org_pairs if p["verdict"] == "DUPLICATE_OF"]
    if rec:
        return "DUPLICATE_OF", ";".join(p["survivor"] for p in rec), "recorded"
    return "DISTINCT", "", "n/a"


def counts(verdicts, pairs, actions):
    vc = Counter((v["verdict"], v["org_state"]) for v in verdicts)
    pc = Counter((p["level"], p["verdict"], p["state"]) for p in pairs)
    ac = Counter((a["action"], a["state"]) for a in actions)
    c: dict = {
        "clusters": len(verdicts),
        "clusters_DUPLICATE_OF_recorded": vc[("DUPLICATE_OF", "recorded")],
        "clusters_DUPLICATE_OF_to_apply": vc[("DUPLICATE_OF", "to_apply")],
        "clusters_DISTINCT": vc[("DISTINCT", "n/a")],
        "clusters_STILL_UNCERTAIN": vc[("STILL_UNCERTAIN", "n/a")],
        "org_pairs_DUPLICATE_OF_to_apply": pc[("org", "DUPLICATE_OF", "to_apply")],
        "site_pairs_DUPLICATE_OF_to_apply": pc[("site", "DUPLICATE_OF", "to_apply")],
        "site_pairs_DUPLICATE_OF_recorded": pc[("site", "DUPLICATE_OF", "recorded")],
        "org_pairs_DUPLICATE_OF_recorded": pc[("org", "DUPLICATE_OF", "recorded")],
        "pairs_DISTINCT": sum(n for (_lv, v, _s), n in pc.items() if v == "DISTINCT"),
        "pairs_STILL_UNCERTAIN": sum(n for (_lv, v, _s), n in pc.items() if v == "STILL_UNCERTAIN"),
        "actions_repoint_site_to_apply": ac[("repoint_site", "to_apply")],
        "actions_hold_operator": ac[("hold_operator", "hold")],
    }
    c["readme_lines"] = [
        f"{c['clusters']} medium clusters",
        f"{c['clusters_DUPLICATE_OF_recorded']} DUPLICATE_OF (already recorded in the tree)",
        f"{c['clusters_DUPLICATE_OF_to_apply']} DUPLICATE_OF (org fold to apply)",
        f"{c['clusters_DISTINCT']} DISTINCT",
        f"{c['clusters_STILL_UNCERTAIN']} STILL_UNCERTAIN",
        f"{c['site_pairs_DUPLICATE_OF_to_apply']} site folds to apply",
        f"{c['actions_repoint_site_to_apply']} repoint_site",
        f"{c['actions_hold_operator']} hold_operator",
    ]
    return c


# ------------------------------------------------------------------ data
def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_tree():
    orgs, sites = {}, {}
    for f in glob.glob(str(ROOT / "data/organizations_*.csv")):
        for r in read_csv(f):
            orgs[r["org_id"]] = r
    eco = ROOT / "data/ecosystem.csv"
    for r in read_csv(eco):
        orgs.setdefault(r["org_id"], r)
    for f in glob.glob(str(ROOT / "data/sites_*.csv")):
        for r in read_csv(f):
            sites[r["site_id"]] = r
    return orgs, sites


def norm_text(s):
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"').replace("”", '"')).strip()


def street_key(site):
    s = site.get("street_address", "")
    if not s:
        m = re.search(r"Street(?: \(per Grok\))?:\s*(\d[^.;]*?)(?:\.|;|$)", site.get("notes", ""))
        s = m.group(1) if m else ""
    toks = re.findall(r"[a-z0-9]+", s.lower())
    if not toks or not toks[0].isdigit():
        return None
    rest = [t for t in toks[1:] if t not in DIRS]
    return toks[0], (rest[0] if rest else "")


def frs_ids(site):
    return set(re.findall(r"\b110\d{9}\b", site.get("sources", "") + " " + site.get("notes", "")))


def host(url):
    return re.sub(r"^https?://(www\.)?", "", url.strip().lower()).split("/")[0]


def site_basis_ok(basis, a, b, pair_sources):
    ka, kb = street_key(a), street_key(b)
    if basis == "shared_frs_id":
        return bool(frs_ids(a) & frs_ids(b))
    if basis == "same_street":
        return ka is not None and ka == kb
    if basis == "street_variant":
        return (ka is not None and kb is not None and ka[0] == kb[0]
                and difflib.SequenceMatcher(None, ka[1], kb[1]).ratio() >= 0.8)
    if basis == "same_city_streetless":
        return ((ka is None) != (kb is None) and a["city"].lower() == b["city"].lower() and a["state"] == b["state"]
                and any(t.startswith(("FRS:", "WEB:")) for t in pair_sources.split(";")))
    return False


# ------------------------------------------------------------------ checks
def run(verdicts, pairs, actions, evidence, frs_rows, leads, orgs, sites, errs=None, offline=False, cache_ok=True):
    errs = [] if errs is None else errs
    E = errs.append
    # frame
    lead_ids = [L["cluster_id"] for L in leads]
    if len(leads) != EXPECTED_MEDIUM:
        E(f"frame: leads.csv has {len(leads)} medium clusters, expected {EXPECTED_MEDIUM}")
    vc = Counter(v["cluster"] for v in verdicts)
    for cid in lead_ids:
        if vc[cid] != 1:
            E(f"frame: cluster {cid} has {vc[cid]} verdict rows (want exactly 1)")
    for cid in vc:
        if cid not in lead_ids:
            E(f"frame: verdict for {cid} which is not a medium cluster")
    by_lead = {L["cluster_id"]: L for L in leads}
    pairs_by = {}
    for p in pairs:
        pairs_by.setdefault(p["cluster"], []).append(p)
    actions_by = {}
    for a in actions:
        actions_by.setdefault(a["cluster"], []).append(a)

    def live_org(oid):
        r = orgs.get(oid)
        return bool(r) and r["status"] == "active"

    folded_map, survivor_cluster = {}, {}
    for p in pairs:
        cid = p["cluster"]
        if cid not in by_lead:
            E(f"pair {p['pair_id']}: unknown cluster {cid}")
            continue
        if p["verdict"] not in GRAMMAR:
            E(f"pair {p['pair_id']}: verdict {p['verdict']!r} outside the grammar")
        a, b = p["record_a"], p["record_b"]
        tab = orgs if p["level"] == "org" else sites
        for r in (a, b):
            if r not in tab:
                E(f"pair {p['pair_id']}: {r} is not a held {p['level']} record")
        L = by_lead[cid]
        ids = set(L["record_ids"].split(";")) | set(L["org_ids"].split(";"))
        if not ({a, b} & ids):
            E(f"pair {p['pair_id']}: neither record is in cluster {cid}")
        if not p["fact"].strip():
            E(f"pair {p['pair_id']}: empty fact")
        if p["verdict"] == "STILL_UNCERTAIN" and "Settling fact" not in p["fact"]:
            E(f"pair {p['pair_id']}: STILL_UNCERTAIN without a named 'Settling fact'")
        if p["verdict"] != "DUPLICATE_OF":
            if p["survivor"] or p["state"] != "n/a":
                E(f"pair {p['pair_id']}: {p['verdict']} must have empty survivor and state n/a")
            continue
        s, f = p["survivor"], None
        if s not in (a, b):
            E(f"pair {p['pair_id']}: survivor {s!r} is neither record")
            continue
        f = folded_of(p)
        if p["state"] not in ("recorded", "to_apply"):
            E(f"pair {p['pair_id']}: DUPLICATE_OF state {p['state']!r}")
        if f in folded_map:
            E(f"pair {p['pair_id']}: {f} is folded twice (also into {folded_map[f][0]})")
        folded_map[f] = (s, cid, p)
        if s in survivor_cluster and survivor_cluster[s] != cid:
            E(f"pair {p['pair_id']}: {s} is a survivor in two clusters ({survivor_cluster[s]}, {cid})")
        survivor_cluster.setdefault(s, cid)
    # chains end at a held, live record; survivors are never folded
    for f, (s, cid, p) in folded_map.items():
        seen, cur = {f}, s
        while cur in folded_map:
            if cur in seen:
                E(f"chain from {f}: cycle at {cur}")
                break
            seen.add(cur)
            cur = folded_map[cur][0]
        if p["level"] == "org":
            if not live_org(cur):
                E(f"chain from {f}: ends at {cur} which is not a held active org")
        elif cur not in sites:
            E(f"chain from {f}: ends at {cur} which is not a held site")
        if s in folded_map:
            E(f"survivor {s} (pair {p['pair_id']}) is itself folded in {folded_map[s][2]['pair_id']}")
        # state-specific proof against data/
        if p["state"] == "to_apply" and history(s) < history(f):
            E(f"pair {p['pair_id']}: survivor {s} holds less history {history(s)} than folded {f} {history(f)} (links, evidence)")
        if p["level"] == "org":
            fr = orgs.get(f, {})
            if p["state"] == "recorded":
                ok = fr.get("status") in ("merged", "acquired") and (fr.get("successor_org_id") == s or s in fr.get("notes", ""))
                if not ok:
                    E(f"pair {p['pair_id']}: recorded org fold {f}>{s} not visible in the tree (status/successor/notes)")
            else:
                if fr.get("status") != "active":
                    E(f"pair {p['pair_id']}: to_apply org fold but {f} is not active (status {fr.get('status')!r})")
                if not live_org(s):
                    E(f"pair {p['pair_id']}: survivor org {s} is not active")
                if p["basis"] == "same_website":
                    if not (fr.get("website") and orgs[s].get("website") and host(fr["website"]) == host(orgs[s]["website"])):
                        E(f"pair {p['pair_id']}: same_website not true for {f} / {s}")
                elif p["basis"] == "division_of_survivor_site":
                    ok = any(q["level"] == "site" and q["state"] == "to_apply" and q["basis"] == "same_street"
                             and sites[folded_of(q)]["org_id"] == f and sites[q["survivor"]]["org_id"] == s
                             for q in pairs_by[p["cluster"]] if q["verdict"] == "DUPLICATE_OF")
                    if not ok:
                        E(f"pair {p['pair_id']}: division_of_survivor_site has no same_street site pair under {f}/{s}")
                else:
                    E(f"pair {p['pair_id']}: org to_apply basis {p['basis']!r} unknown")
        else:
            fs, ss = sites.get(f, {}), sites.get(s, {})
            if p["state"] == "recorded":
                if not (s in fs.get("notes", "") or f in ss.get("notes", "")):
                    E(f"pair {p['pair_id']}: recorded site fold {f}>{s} not visible in either row's notes")
            else:
                if re.search(r"tombstoned as duplicate|folded into|Retired in integration pass", fs.get("notes", "")):
                    E(f"pair {p['pair_id']}: {f} already carries a tombstone note")
                if fs.get("city", "").lower() != ss.get("city", "").lower() or fs.get("state") != ss.get("state"):
                    E(f"pair {p['pair_id']}: {f} and {s} are in different cities/states")
                if not site_basis_ok(p["basis"], fs, ss, p["sources"]):
                    E(f"pair {p['pair_id']}: basis {p['basis']!r} does not hold for {f} / {s} in data/")
                po = ss.get("org_id", "")
                rep = [a for a in actions if a["action"] == "repoint_site" and a["record"] == s]
                op = p.get("operator_org", "")
                if op:
                    if not live_org(op):
                        E(f"pair {p['pair_id']}: operator_org {op} is not an active org")
                    elif po != op and not any(a["target"] == op for a in rep):
                        E(f"pair {p['pair_id']}: survivor {s} sits under {po}, operator is {op}, and no repoint_site moves it")
                    elif po == op and rep:
                        E(f"pair {p['pair_id']}: survivor {s} is already under the operator {op} but has a repoint action")
                elif not any(a["action"] == "hold_operator" and a["record"] == s for a in actions):
                    E(f"pair {p['pair_id']}: operator unsettled (operator_org blank) but no hold_operator on survivor {s}")
                if not live_org(po) and not rep:
                    E(f"pair {p['pair_id']}: survivor site {s} sits under non-active org {po} with no repoint action")
    # verdict rows
    for v in verdicts:
        cid = v["cluster"]
        if cid not in by_lead:
            continue
        if v["verdict"] not in GRAMMAR:
            E(f"verdict {cid}: {v['verdict']!r} outside the grammar")
        if v["records"] != by_lead[cid]["record_ids"]:
            E(f"verdict {cid}: records column differs from leads.csv")
        if v["name_key"] != by_lead[cid]["name_key"]:
            E(f"verdict {cid}: name_key differs from leads.csv")
        org_pairs = [p for p in pairs_by.get(cid, []) if p["level"] == "org"]
        if not org_pairs:
            E(f"verdict {cid}: no org-level pair")
            continue
        dv, ds, dstate = derive_verdict(org_pairs)
        if (v["verdict"], v["survivor"], v["org_state"]) != (dv, ds, dstate):
            E(f"verdict {cid}: row says {(v['verdict'], v['survivor'], v['org_state'])}, pairs derive {(dv, ds, dstate)}")
        if v["verdict"] == "DUPLICATE_OF":
            for s in v["survivor"].split(";"):
                if s not in orgs:
                    E(f"verdict {cid}: survivor {s} is not a held org")
        if not v["deciding_or_settling_fact"].strip():
            E(f"verdict {cid}: empty deciding_or_settling_fact")
    # actions
    for a in actions:
        if a["cluster"] not in by_lead:
            E(f"action {a['action_id']}: unknown cluster")
        if a["record"] not in sites:
            E(f"action {a['action_id']}: {a['record']} is not a held site")
        if a["action"] == "repoint_site":
            if a["target"] not in orgs or not live_org(a["target"]):
                E(f"action {a['action_id']}: repoint target {a['target']} is not an active org")
            elif sites.get(a["record"], {}).get("org_id") == a["target"]:
                E(f"action {a['action_id']}: {a['record']} already belongs to {a['target']}")
            if a["state"] != "to_apply":
                E(f"action {a['action_id']}: repoint_site state must be to_apply")
        elif a["action"] == "hold_operator":
            ts = a["target"].split("|")
            if len(ts) != 2 or any(t not in orgs for t in ts):
                E(f"action {a['action_id']}: hold_operator target must be two held orgs 'A|B'")
            if "Settling fact" not in a["fact"] or a["state"] != "hold":
                E(f"action {a['action_id']}: hold_operator needs state hold and a named 'Settling fact'")
        else:
            E(f"action {a['action_id']}: unknown action {a['action']!r}")
    # sources
    ev = {e["id"]: e for e in evidence}
    fr = {r["registry_id"]: r for r in frs_rows}

    def check_tokens(label, s):
        toks = [t for t in s.split(";") if t]
        if not toks:
            E(f"{label}: no sources")
        for t in toks:
            kind, _, ref = t.partition(":")
            if kind == "TREE":
                if ref not in orgs and ref not in sites:
                    E(f"{label}: TREE:{ref} not in data/")
            elif kind == "FRS":
                if ref not in fr:
                    E(f"{label}: FRS:{ref} not in frs_excerpt.csv")
            elif kind == "WEB":
                if ref not in ev:
                    E(f"{label}: WEB:{ref} not in evidence.csv")
            else:
                E(f"{label}: bad source token {t!r}")
    for v in verdicts:
        check_tokens(f"verdict {v['cluster']}", v["sources"])
    for p in pairs:
        check_tokens(f"pair {p['pair_id']}", p["sources"])
    for a in actions:
        check_tokens(f"action {a['action_id']}", a["sources"])
    for e in evidence:
        f = PERSIST / e["file"]
        if not f.exists():
            E(f"evidence {e['id']}: cached page {f} missing (cannot inspect)")
            continue
        if hashlib.sha256(f.read_bytes()).hexdigest() != e["sha256"]:
            E(f"evidence {e['id']}: sha256 of {e['file']} differs from evidence.csv")
        if norm_text(e["quote"]) not in norm_text(f.read_text(errors="ignore")):
            E(f"evidence {e['id']}: quote not found on the cached page")
    if offline:
        print("NOTE: --offline: FRS rows were NOT compared with the ECHO cache")
    elif not FRS_DB.exists():
        E(f"FRS cache {FRS_DB} missing (cannot inspect; use --offline to skip this one comparison)")
    elif cache_ok:
        db = sqlite3.connect(f"file:{FRS_DB}?mode=ro", uri=True)
        for r in frs_rows:
            rows = db.execute("select payload from records where id=?", (r["registry_id"],)).fetchall()
            if len(rows) != 1:
                E(f"frs {r['registry_id']}: {len(rows)} cache rows")
                continue
            p = json.loads(rows[0][0])
            got = (p["FAC_NAME"], p["FAC_STREET"], p["FAC_CITY"], p["FAC_STATE"], p["FAC_ZIP"])
            if got != (r["fac_name"], r["fac_street"], r["fac_city"], r["fac_state"], r["fac_zip"]):
                E(f"frs {r['registry_id']}: excerpt differs from cache {got}")
    return errs


_LC = []


def link_counts():
    """Rows that reference each record id: evidence (record_id), registry_links (org_id/site_id), relationships (from/to)."""
    if _LC:
        return _LC[0]
    ev, rl, rel = Counter(), Counter(), Counter()
    for f in glob.glob(str(ROOT / "data/evidence_*.csv")):
        for r in read_csv(f):
            ev[r["record_id"]] += 1
    for r in read_csv(ROOT / "data/registry_links.csv"):
        rl[r["org_id"]] += 1
        if r["site_id"]:
            rl[r["site_id"]] += 1
    for r in read_csv(ROOT / "data/relationships.csv"):
        rel[r["from_org_id"]] += 1
        rel[r["to_org_id"]] += 1
    _LC.append((ev, rl, rel))
    return _LC[0]


def history(rec):
    """(registry_links + relationships, evidence rows): what a fold would orphan if this record were the folded side."""
    ev, rl, rel = link_counts()
    return rl[rec] + rel[rec], ev[rec]


def fold_cost(p, lc):
    """The six COST_COLS for one to_apply DUPLICATE_OF pair (folded side vs survivor side)."""
    ev, rl, rel = lc
    f, s = folded_of(p), p["survivor"]
    return dict(folded_evidence=ev[f], folded_registry_links=rl[f], folded_relationships=rel[f],
                survivor_evidence=ev[s], survivor_registry_links=rl[s], survivor_relationships=rel[s])


def check_costs(pairs):
    errs, lc = [], link_counts()
    for p in pairs:
        want = fold_cost(p, lc) if (p["verdict"] == "DUPLICATE_OF" and p["state"] == "to_apply") else {c: "" for c in COST_COLS}
        for c in COST_COLS:
            if str(want[c]) != str(p.get(c, "")):
                errs.append(f"pair {p['pair_id']}: {c} is {p.get(c)!r}, data/ says {want[c]!r}")
    return errs


def known_answers():
    """The street matcher on cases whose answer is known before it is trusted."""
    errs = []
    k = lambda street: street_key({"street_address": street, "notes": ""})  # noqa: E731
    if k("1570 E Highland Rd") != k("1570 Highland Rd"):
        errs.append("known answer: '1570 E Highland Rd' must equal '1570 Highland Rd'")
    if k("111 RIDC Park West Drive") != k("111 Park West Dr."):
        errs.append("known answer: RIDC Park West must equal Park West")
    if difflib.SequenceMatcher(None, k("48 Powhatten Ave.")[1], k("48 Powhattan Ave.")[1]).ratio() < 0.8:
        errs.append("known answer: Powhatten/Powhattan must be a street variant")
    if k("1550 Universal Rd") == k("1441 Universal Rd"):
        errs.append("known answer: 1550 and 1441 Universal Rd must differ")
    notes_only = street_key({"street_address": "", "notes": "Source: x. Street (per Grok): 4050 Clough Woods Drive. NAICS"})
    if notes_only != k("4050 Clough Woods Dr"):
        errs.append("known answer: street read from notes must equal the street field")
    return errs


def data_untouched():
    errs = []
    try:
        d1 = subprocess.run(["git", "diff", "--name-only", "origin/main...HEAD", "--", "data/"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        d2 = subprocess.run(["git", "status", "--porcelain", "--", "data/"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\n")
    except Exception as e:  # noqa: BLE001
        return [f"data: cannot run git ({e}); cannot show data/ is untouched"]
    if d1:
        errs.append(f"this branch changed data/ relative to origin/main: {d1[:5]}")
    if any(x.strip() for x in d2):
        errs.append(f"data/ has uncommitted changes: {d2[:5]}")
    return errs


def check_counts_and_readme(verdicts, pairs, actions):
    errs = []
    cj = json.loads((HERE / "counts.json").read_text())
    now = counts(verdicts, pairs, actions)
    if cj != now:
        errs.append("counts.json differs from counts recomputed from the CSVs")
    readme = (HERE / "README.md").read_text() if (HERE / "README.md").exists() else ""
    for line in now["readme_lines"]:
        if line not in readme:
            errs.append(f"README.md does not state {line!r}")
    return errs


def load_all():
    return dict(verdicts=read_csv(HERE / "verdicts.csv"), pairs=read_csv(HERE / "pairs.csv"),
                actions=read_csv(HERE / "operator_actions.csv"), evidence=read_csv(HERE / "evidence.csv"),
                frs_rows=read_csv(HERE / "frs_excerpt.csv"), leads=load_leads())


def selftest(base, orgs, sites):
    """Plant one defect at a time; the check must fail with the expected message."""
    import copy

    def mutate(fn, expect, **kw):
        d = copy.deepcopy(base)
        fn(d)
        errs = run(d["verdicts"], d["pairs"], d["actions"], d["evidence"], d["frs_rows"], d["leads"], orgs, sites,
                   cache_ok=False, **kw)
        hit = [e for e in errs if expect in e]
        print(("  ok   " if hit else "  FAIL ") + expect + ("" if hit else f"  (got {errs[:2]})"))
        return bool(hit)

    def pair(d, pid):
        return next(p for p in d["pairs"] if p["pair_id"] == pid)

    ok = True
    # 1 survivor that is itself a tombstone (merged org)
    def m1(d):
        p = next(p for p in d["pairs"] if p["verdict"] == "DUPLICATE_OF" and p["level"] == "org" and p["state"] == "to_apply")
        p["record_b"] = p["survivor"] = "ORG-001846"
        for v in d["verdicts"]:
            if v["cluster"] == p["cluster"]:
                v["survivor"] = p["survivor"]
    ok &= mutate(m1, "is not active")
    # 2 a record folded in two clusters
    def m2(d):
        p = next(p for p in d["pairs"] if p["level"] == "org" and p["verdict"] == "DUPLICATE_OF" and p["state"] == "recorded")
        q = dict(p)
        q["pair_id"] = "PXXX"
        q["cluster"] = "SND-0014" if p["cluster"] != "SND-0014" else "SND-0009"
        d["pairs"].append(q)
    ok &= mutate(m2, "is folded twice")
    # 3 a survivor that is itself folded
    def m3b(d):
        p = next(p for p in d["pairs"] if p["level"] == "site" and p["state"] == "to_apply")
        q = dict(p)
        q["pair_id"] = "PXXX"
        q["record_a"], q["record_b"], q["survivor"] = p["survivor"], "SITE-000001", "SITE-000001"
        d["pairs"].append(q)
    ok &= mutate(m3b, "is itself folded")
    # 4 a site fold across cities
    def m4(d):
        p = next(p for p in d["pairs"] if p["level"] == "site" and p["state"] == "to_apply")
        s = sites[p["survivor"]]
        other = next(r for r in sites.values() if r["city"].lower() != s["city"].lower() and r["site_id"] != p["survivor"])
        p["record_a" if p["record_a"] != p["survivor"] else "record_b"] = other["site_id"]
    ok &= mutate(m4, "different cities")
    # 5 a basis that does not hold
    def m5(d):
        p = next(p for p in d["pairs"] if p["level"] == "site" and p["state"] == "to_apply" and p["basis"] == "same_street")
        p["basis"] = "shared_frs_id"
    ok &= mutate(m5, "does not hold")
    # 6 drop a cluster
    ok &= mutate(lambda d: d.__setitem__("verdicts", d["verdicts"][1:]), "has 0 verdict rows")
    # 7 verdict not derivable from pairs
    def m7(d):
        v = next(v for v in d["verdicts"] if v["verdict"] == "DISTINCT")
        v["verdict"] = "DUPLICATE_OF"
        v["survivor"] = "ORG-000001"
    ok &= mutate(m7, "pairs derive")
    # 8 STILL_UNCERTAIN without a settling fact
    def m8(d):
        p = next(p for p in d["pairs"] if p["verdict"] == "STILL_UNCERTAIN")
        p["fact"] = "unclear"
    ok &= mutate(m8, "without a named 'Settling fact'")
    # 9 recorded fold the tree does not show
    def m9(d):
        p = next(p for p in d["pairs"] if p["level"] == "org" and p["state"] == "recorded")
        p["survivor"] = folded_of(p)
        for v in d["verdicts"]:
            if v["cluster"] == p["cluster"]:
                v["survivor"] = p["survivor"]
    ok &= mutate(m9, "not visible in the tree")
    # 10 evidence quote not on the page
    def m10(d):
        d["evidence"][0]["quote"] += " XYZZY"
    ok &= mutate(m10, "quote not found")
    # 11 an unresolved source token
    def m11(d):
        d["pairs"][0]["sources"] += ";FRS:999999999999"
    ok &= mutate(m11, "not in frs_excerpt.csv")
    # 12 a survivor in two clusters
    def m12(d):
        p = next(p for p in d["pairs"] if p["level"] == "org" and p["verdict"] == "DUPLICATE_OF")
        q = dict(p)
        q["pair_id"] = "PXXX"
        q["cluster"] = "SND-0016"
        q["record_a"], q["record_b"], q["survivor"] = "ORG-002674", p["survivor"], p["survivor"]
        d["pairs"].append(q)
    ok &= mutate(m12, "survivor in two clusters")
    # 13 survivor holding less history than the folded record
    def m13(d):
        p = next(p for p in d["pairs"] if p["record_a"] == "SITE-004181")
        p["survivor"] = "SITE-004181"
    ok &= mutate(m13, "holds less history")
    # 14 unsettled operator without a hold_operator action
    def m14(d):
        d["actions"] = [a for a in d["actions"] if not (a["action"] == "hold_operator" and a["record"] == "SITE-003765")]
    ok &= mutate(m14, "no hold_operator on survivor")
    # 15 survivor under a non-operator org without a repoint
    def m15(d):
        d["actions"] = [a for a in d["actions"] if not (a["action"] == "repoint_site" and a["record"] == "SITE-002962")]
    ok &= mutate(m15, "no repoint_site moves it")
    return ok


def main():
    offline = "--offline" in sys.argv
    orgs, sites = load_tree()
    base = load_all()
    errs = run(base["verdicts"], base["pairs"], base["actions"], base["evidence"], base["frs_rows"], base["leads"], orgs, sites,
               offline=offline)
    errs += data_untouched()
    errs += known_answers()
    errs += check_costs(base["pairs"])
    errs += check_counts_and_readme(base["verdicts"], base["pairs"], base["actions"])
    if "--selftest" in sys.argv:
        print("selftest: each planted defect must be caught")
        if not selftest(base, orgs, sites):
            errs.append("selftest: a planted defect was NOT caught")
    if errs:
        print(f"FAIL: {len(errs)} problem(s)")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    c = counts(base["verdicts"], base["pairs"], base["actions"])
    print(f"PASS: {c['clusters']} clusters; " + "; ".join(c["readme_lines"][1:5]) + f"; {c['site_pairs_DUPLICATE_OF_to_apply']} site folds to apply")


if __name__ == "__main__":
    main()
