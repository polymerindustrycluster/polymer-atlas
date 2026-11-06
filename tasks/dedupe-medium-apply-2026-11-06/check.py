#!/usr/bin/env python3
"""Named check for the dedupe-medium apply PR. Exit 0 = PASS. Read-only on data/.

  python3 tasks/dedupe-medium-apply-2026-11-06/check.py            # full check against git merge-base(HEAD, origin/main)
  python3 tasks/dedupe-medium-apply-2026-11-06/check.py --selftest # also plant defects; each must make the check fail
  python3 tasks/dedupe-medium-apply-2026-11-06/check.py --base REF # compare against another base

It derives the EXPECTED delta from the merged #254 packet (pairs.csv, operator_actions.csv) and the HELD list below, then
compares data/ with the base commit row by row. Fails on anything it could not inspect.

  files      exactly the expected data files differ; no data file other than those is touched
  rows       no keyed row disappears; no org/site row is added; changed rows change only the allowed columns, to the
             expected values (org folds, site tombstones, survivor notes, repoints, capability and registry follow-ons)
  tombstones every absorbed org is status=merged with successor_org_id = survivor; every retired site is closed and names its survivor
  evidence   new rows only, ids in EVD-333000..333999, one witness set per repointed site, quotes found in the raw FRS JSON
             (committed) or the cached page (sha256 in sources.csv); no existing evidence row changes
  edges      relationships.csv gains exactly the generated merged_into edge of each absorbed org (V-27 parity)
  held       the held cluster's records are untouched; tier1 columns are untouched
  idempotent re-running build.py on a copy of the applied data changes nothing
"""
import csv
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKET = ROOT / "tasks/dedupe-medium-2026-11-06"
PERSIST = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/dedupe-medium-apply-2026-11-06")
csv.field_size_limit(10 ** 9)
DATE = "2026-11-06"
BY = "claude-code dedupe-medium-apply-2026-11-06"
HELD = {"SND-0101", "SND-0049"}  # Farathane: GLEIF shows two separate legal entities; Jushi: STILL_UNCERTAIN cluster, controller carve-out
EVD_LO, EVD_HI = 333000, 333999
REL_LO = 470
ORG_ALLOWED_DUP = {"status", "status_date", "successor_org_id", "sources", "notes", "last_verified"}
ORG_ALLOWED_SURV = {"notes", "trade_names", "last_verified"}
PRESS_FILE = {"https://www.floordaily.net/flooring-news/tarkett-announces-acquisition-of-johnsonite/": "floordaily-johnsonite.txt",
              "https://www.gemspring.com/gemspring-capital-completes-acquisition-of-the-goodyear-tire-rubber-companys-polymer-chemicals-business": "gemspring-pr.txt",
              "https://news.goodyear.com/2025-11-03-Goodyear-Completes-Divestiture-of-Chemical-Business": "goodyear-divest.txt"}


# ------------------------------------------------------------------ io
def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def rows_of(text):
    return list(csv.DictReader(io.StringIO(text, newline="")))


def key_of(file, r):
    if file == "registry_links.csv":
        return "|".join([r["org_id"], r["registry"], r["registry_id"], r["site_id"]])
    return r[next(iter(r))]


def tables(ref, files):
    """{file: {key: row}} at git ref (None = working tree)."""
    out = {}
    for f in files:
        text = git("show", f"{ref}:data/{f}") if ref else (ROOT / "data" / f).read_text(encoding="utf-8")
        out[f] = {key_of(f, r): r for r in rows_of(text)}
    return out


def read_packet(name):
    return rows_of((PACKET / name).read_text(encoding="utf-8"))


def norm(s):
    return re.sub(r"\s+", " ", s.replace("’", "'")).strip()


# ------------------------------------------------------------------ expectation from the merged packet
def expectation(base_sites):
    pairs, acts = read_packet("pairs.csv"), read_packet("operator_actions.csv")
    ok = lambda r: r["cluster"] not in HELD and r["state"] == "to_apply"  # noqa: E731
    of = [(p["record_b"] if p["survivor"] == p["record_a"] else p["record_a"], p["survivor"], p["cluster"])
          for p in pairs if p["level"] == "org" and p["verdict"] == "DUPLICATE_OF" and ok(p)]
    sf = [(p["record_b"] if p["survivor"] == p["record_a"] else p["record_a"], p["survivor"], p["cluster"])
          for p in pairs if p["level"] == "site" and p["verdict"] == "DUPLICATE_OF" and ok(p)]
    rp = {a["record"]: (a["target"], a["cluster"]) for a in acts if a["action"] == "repoint_site" and ok(a)}
    moves = {s: (base_sites[s]["org_id"], t) for s, (t, _) in rp.items()}
    for dup, surv, _ in of:                              # sites of an absorbed org follow the fold
        for sid, r in base_sites.items():
            if r["org_id"] == dup:
                moves.setdefault(sid, (dup, surv))
    return of, sf, rp, moves


def diff_cols(a, b):
    return {c for c in a if a[c] != b.get(c)}


# ------------------------------------------------------------------ the checks
def check(base, cur, exp, changed_files, files_expected, raw_dir=HERE / "raw", sources=None):
    errs = []
    E = errs.append
    of, sf, rp, moves = exp
    orgs0, orgs, sites0, sites = base["orgs"], cur["orgs"], base["sites"], cur["sites"]

    # row sets: nothing disappears, no org/site added
    for name, b, c in (("orgs", orgs0, orgs), ("sites", sites0, sites), ("evidence", base["evidence"], cur["evidence"]),
                       ("relationships", base["rel"], cur["rel"]), ("capabilities", base["caps"], cur["caps"])):
        gone = set(b) - set(c)
        if gone:
            E(f"{name}: {len(gone)} row(s) disappeared, e.g. {sorted(gone)[:3]}")
    if set(orgs) != set(orgs0) or set(sites) != set(sites0):
        E("an org or site row was added (no new org/site ids are allowed)")

    # orgs
    dups = {d: (s, c) for d, s, c in of}
    survs = {s for _, s, _ in of}
    for oid in set(orgs0) | set(orgs):
        b, c = orgs0.get(oid), orgs.get(oid)
        if not b or not c:
            continue
        cols = diff_cols(b, c)
        if oid in dups:
            surv = dups[oid][0]
            if not cols <= ORG_ALLOWED_DUP:
                E(f"org {oid}: unexpected columns changed {sorted(cols - ORG_ALLOWED_DUP)}")
            want = dict(status="merged", status_date=DATE, successor_org_id=surv)
            for k, v in want.items():
                if c[k] != v:
                    E(f"org {oid}: {k} is {c[k]!r}, expected {v!r}")
            if not c["sources"].startswith(b["sources"]) or c["sources"] == b["sources"]:
                E(f"org {oid}: a source must be appended to sources")
            if not c["notes"].startswith(b["notes"]) or surv not in c["notes"]:
                E(f"org {oid}: notes must keep the old text and name {surv}")
            if "Kept as a tombstone, never deleted" not in c["notes"]:
                E(f"org {oid}: tombstone note missing")
        elif oid in survs:
            if not cols <= ORG_ALLOWED_SURV:
                E(f"org {oid}: unexpected columns changed {sorted(cols - ORG_ALLOWED_SURV)}")
            if not c["notes"].startswith(b["notes"]) or not any(d in c["notes"] for d, (s, _) in dups.items() if s == oid):
                E(f"org {oid}: survivor notes must name the absorbed record")
            if "trade_names" in cols and not c["trade_names"].startswith(b["trade_names"]):
                E(f"org {oid}: trade_names may only be extended")
        elif cols:
            E(f"org {oid}: changed {sorted(cols)} but is not in the scoped folds")
    for s, _ in dups.values():
        if orgs[s]["status"] != "active":
            E(f"survivor {s} is not active")
    for col in ("tier1_qualifier", "tier1_qualifier_basis"):
        if any(orgs[o][col] != orgs0[o][col] for o in orgs0):
            E(f"{col} was edited (derived fields are hands-off)")

    # sites
    folded = {d: (s, c) for d, s, c in sf}
    surv_sites = {s for _, s, _ in sf}
    for sid in set(sites0) & set(sites):
        b, c = sites0[sid], sites[sid]
        cols = diff_cols(b, c)
        expected_cols = set()
        if sid in folded:
            expected_cols |= {"operating_status", "notes", "last_verified"}
            if c["operating_status"] != "closed":
                E(f"site {sid}: retired site must be closed")
            sv = folded[sid][0]
            if sv not in c["notes"] or "Row never deleted" not in c["notes"] or not c["notes"].startswith(b["notes"]):
                E(f"site {sid}: tombstone note must keep the old text, name {sv} and say the row is never deleted")
            if b["operating_status"] == "closed":
                E(f"site {sid}: was already closed at the base")
        if sid in surv_sites:
            expected_cols |= {"notes", "last_verified"}
            if not c["notes"].startswith(b["notes"]) or not any(d in c["notes"] for d, (s, _) in folded.items() if s == sid):
                E(f"site {sid}: survivor notes must name the absorbed site")
            if c["operating_status"] != b["operating_status"]:
                E(f"site {sid}: a survivor's status must not change")
        if sid in moves:
            old, new = moves[sid]
            expected_cols |= {"org_id", "notes", "last_verified"}
            if b["org_id"] != old or c["org_id"] != new:
                E(f"site {sid}: org_id {b['org_id']}->{c['org_id']}, expected {old}->{new}")
            if old not in c["notes"] or not c["notes"].startswith(b["notes"]):
                E(f"site {sid}: notes must name the old org {old}")
            if orgs[new]["status"] != "active":
                E(f"site {sid}: new operator {new} is not active")
        if not cols <= expected_cols:
            E(f"site {sid}: unexpected columns changed {sorted(cols - expected_cols)}")
        if sid not in folded and sid not in surv_sites and sid not in moves and cols:
            E(f"site {sid}: changed {sorted(cols)} but is not in the scoped folds or repoints")
    for sid in folded:
        if sid in sites and sid not in moves and sites[sid]["org_id"] != sites0[sid]["org_id"]:
            E(f"site {sid}: org_id changed without a scoped move")

    # evidence: new rows only
    ev0, ev = base["evidence"], cur["evidence"]
    for k, r in ev0.items():
        if k in ev and ev[k] != r:
            E(f"evidence {k}: an existing row changed (append-only)")
    new_ev = {k: r for k, r in ev.items() if k not in ev0}
    by_site = {}
    for k, r in new_ev.items():
        n = int(k[4:]) if re.fullmatch(r"EVD-\d{6}", k) else -1
        if not EVD_LO <= n <= EVD_HI:
            E(f"evidence {k}: id outside EVD-{EVD_LO}..{EVD_HI}")
        if r["record_table"] != "sites" or r["claim_type"] != "parent" or r["created_by"] != BY:
            E(f"evidence {k}: expected a sites/parent row created by {BY}")
        by_site.setdefault(r["record_id"], []).append(r)
        # raw witness
        m = re.search(r'registry id (\d{12})', r["claim_detail"])
        quote = re.findall(r'"([^"]+)"', r["claim_detail"])
        tri = re.match(r"https://data\.epa\.gov/efservice/TRI_FACILITY/TRI_FACILITY_ID/(\w+)/JSON$", r["source_ref"])
        if m:
            f = raw_dir / f"frs_{m.group(1)}.json"
            if not f.exists():
                E(f"evidence {k}: raw FRS JSON {f.name} missing (cannot inspect)")
            else:
                j = json.loads(f.read_text())["Results"]["FRSFacility"][0]
                if not quote or quote[0] != j["FacilityName"] or j["LocationAddress"] not in r["claim_detail"]:
                    E(f"evidence {k}: registrant/address in the row do not equal the raw FRS JSON")
                if r["source_ref"] != f"https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id={m.group(1)}&output=JSON":
                    E(f"evidence {k}: source_ref is not the FRS REST URL of {m.group(1)}")
                # a registrant may be said to NAME THE OPERATOR only if it shares its leading word with the target org's name
                if "names the operator" in r["claim_detail"]:
                    target = orgs[moves[r["record_id"]][1]] if r["record_id"] in moves else {}
                    names = [target.get("legal_name", "")] + target.get("trade_names", "").split(";")
                    lead = lambda t: next(iter(re.findall(r"[a-z0-9]+", re.sub(r"^the\s+", "", t.lower()))), "")  # noqa: E731
                    if lead(j["FacilityName"]) not in {lead(n) for n in names if n.strip()}:
                        E(f"evidence {k}: registrant {j['FacilityName']!r} is said to name the operator but shares no leading word with {target.get('legal_name')!r}")
        elif tri:
            ff, fo = PERSIST / f"tri_facility_{tri.group(1)}.json", PERSIST / f"tri_form_{tri.group(1)}.json"
            if not ff.exists() or not fo.exists():
                E(f"evidence {k}: cached TRI JSON for {tri.group(1)} missing (cannot inspect)")
            else:
                fac, forms = json.loads(ff.read_text())[0], json.loads(fo.read_text())
                got = re.search(r"received (\d{4}-\d{2}-\d{2})", r["claim_detail"])
                if not quote or quote[0] != fac["facility_name"] or fac["street_address"] not in r["claim_detail"]:
                    E(f"evidence {k}: facility name/address in the row do not equal the TRI facility JSON")
                if not got or got.group(1) not in {f["received_date"][:10] for f in forms}:
                    E(f"evidence {k}: the filing date in the row is not a received_date in the TRI form JSON")
        else:
            fn = PRESS_FILE.get(r["source_ref"])
            if not fn or not (PERSIST / fn).exists():
                E(f"evidence {k}: cached page for {r['source_ref']} missing (cannot inspect)")
            else:
                page = norm((PERSIST / fn).read_text(errors="ignore"))
                if not quote or norm(quote[-1]) not in page:
                    E(f"evidence {k}: quote {quote[-1:]!r} not found on the cached page")
                if "gemspring.com" in r["source_ref"] and ("November 3, 2025" not in page or "release dated 2025-11-03" not in r["claim_detail"]
                                                          or re.search(r"completed .{0,80} on 2025-11-03", r["claim_detail"])):
                    E(f"evidence {k}: the Gemspring release is dated 2025-11-03 but does not date completion; the row must say 'release dated 2025-11-03' only")
                if "goodyear.com" in r["source_ref"] and "effective Oct. 31, 2025" in r["claim_detail"] and "effective 2025-10-31" not in r["claim_detail"]:
                    E(f"evidence {k}: effective date must be stated as 2025-10-31")
    for sid in rp:
        if sid not in by_site:
            E(f"repointed site {sid}: no evidence row")
    for sid in by_site:
        if sid not in rp:
            E(f"evidence for {sid} which is not a repointed site")

    # relationships: exactly the generated merged_into edges
    rel0, rel = base["rel"], cur["rel"]
    for k, r in rel0.items():
        if k in rel and rel[k] != r:
            E(f"relationship {k}: an existing row changed")
    new_rel = [r for k, r in rel.items() if k not in rel0]
    want_edges = {(d, "merged_into", s) for d, (s, _) in dups.items()}
    got_edges = {(r["from_org_id"], r["relationship_type"], r["to_org_id"]) for r in new_rel}
    if got_edges != want_edges or len(new_rel) != len(want_edges):
        E(f"relationships: new edges {sorted(got_edges)} != expected {sorted(want_edges)}")
    for r in new_rel:
        if int(r["relationship_id"][4:]) < REL_LO or r["effective_from"] or r["created_by"] != BY:
            E(f"relationship {r['relationship_id']}: id below REL-{REL_LO:06d}, a dated effective_from, or wrong created_by")
        if r["source_ref"] != f"organizations.csv: {r['from_org_id']}.successor_org_id + status":
            E(f"relationship {r['relationship_id']}: not a generated-from-column edge")

    # capabilities and registry links follow moved sites, nothing else
    for k, r in cur["caps"].items():
        b = base["caps"].get(k)
        if b is None:
            E(f"capability {k}: added")
            continue
        cols = diff_cols(b, r)
        if r["site_id"] in moves:
            if r["org_id"] != sites[r["site_id"]]["org_id"]:
                E(f"capability {k}: org_id does not equal its site's org_id (V-31)")
            if cols - {"org_id"}:
                E(f"capability {k}: more than org_id changed")
        elif cols:
            E(f"capability {k}: changed but its site is not moved")
    rl0, rl = base["links"], cur["links"]
    removed = {k: r for k, r in rl0.items() if k not in rl}
    added = {k: r for k, r in rl.items() if k not in rl0}
    if len(rl0) != len(rl) or len(removed) != len(added):
        E("registry_links: row count changed")
    for k, r in removed.items():
        site = r["site_id"]
        if site not in moves or not r["site_id"]:
            E(f"registry link {k}: removed but its site is not moved")
            continue
        nk = "|".join([moves[site][1], r["registry"], r["registry_id"], site])
        if nk not in added:
            E(f"registry link {k}: not re-keyed to the new operator {moves[site][1]}")
    manifest = {r["key"] for r in rows_of((HERE / "REMOVALS.csv").read_text())} if (HERE / "REMOVALS.csv").exists() else set()
    if manifest != set(removed):
        E(f"REMOVALS.csv {sorted(manifest)} != removed registry link keys {sorted(removed)}")

    # held cluster untouched
    held_ids = set()
    for p in read_packet("pairs.csv"):
        if p["cluster"] in HELD:
            held_ids |= {p["record_a"], p["record_b"]}
    for a in read_packet("operator_actions.csv"):
        if a["cluster"] in HELD:
            held_ids.add(a["record"])
    for rid in held_ids:
        for name, b, c in (("orgs", orgs0, orgs), ("sites", sites0, sites)):
            if rid in b and b[rid] != c[rid]:
                E(f"held record {rid} changed")
    # scoped files only
    want_files = set(files_expected)
    if set(changed_files) != want_files:
        E(f"changed data files {sorted(set(changed_files) ^ want_files)} differ from the expected set")
    # sources.csv pages
    for r in (sources or []):
        f = PERSIST / r["file"]
        if not f.exists():
            E(f"source {r['id']}: cached page {r['file']} missing (cannot inspect)")
        elif hashlib.sha256(f.read_bytes()).hexdigest() != r["sha256"] or norm(r["quote"]) not in norm(f.read_text(errors="ignore")):
            E(f"source {r['id']}: sha256 or quote does not match the cached page")
    return errs


def expected_files(exp, shard_of_org, shard_of_site, base_caps, base_links):
    of, sf, rp, moves = exp
    fs = {"relationships.csv"} if of else set()
    for d, s, _ in of:
        fs |= {shard_of_org[d], shard_of_org[s]}
    for d, s, _ in sf:
        fs |= {shard_of_site[d], shard_of_site[s]}
    fs |= {shard_of_site[sid] for sid in moves}
    fs |= {"evidence_sites_" + shard_of_site[sid].split("_", 1)[1] for sid in rp}
    if any(c["site_id"] in moves for c in base_caps.values()):
        fs.add("site_capabilities.csv")
    if any(l["site_id"] in moves for l in base_links.values()):
        fs.add("registry_links.csv")
    return fs


def main():
    argv = sys.argv[1:]
    base_ref = argv[argv.index("--base") + 1] if "--base" in argv else git("merge-base", "HEAD", "origin/main").strip()
    names = git("ls-tree", "--name-only", base_ref, "data/").split()
    pick = lambda pat: [n.split("/")[-1] for n in names if re.fullmatch(pat, n)]  # noqa: E731
    shard_orgs, shard_sites = pick(r"data/organizations_[A-Z]+\.csv"), pick(r"data/sites_[A-Z]+\.csv")
    ev_sites = pick(r"data/evidence_sites_[A-Z]+\.csv")
    allf = shard_orgs + shard_sites + ev_sites + ["relationships.csv", "registry_links.csv", "site_capabilities.csv"]

    def load_set(ref):
        t = tables(ref, allf)
        return dict(orgs={k: r for f in shard_orgs for k, r in t[f].items()}, sites={k: r for f in shard_sites for k, r in t[f].items()},
                    evidence={k: r for f in ev_sites for k, r in t[f].items()}, rel=t["relationships.csv"],
                    caps=t["site_capabilities.csv"], links=t["registry_links.csv"]), t

    base, tb = load_set(base_ref)
    cur, tc = load_set(None)
    shard_of_org = {k: f for f in shard_orgs for k in tb[f]}
    shard_of_site = {k: f for f in shard_sites for k in tb[f]}
    exp = expectation(base["sites"])
    files_expected = expected_files(exp, shard_of_org, shard_of_site, base["caps"], base["links"])
    changed = [f for f in allf if tb[f] != tc[f]]
    other = [p for p in git("diff", "--name-only", base_ref, "--", "data/").split() + git("ls-files", "--others", "--exclude-standard", "data/").split()
             if p.split("/")[-1] not in allf]
    srcs = rows_of((HERE / "sources.csv").read_text(encoding="utf-8")) if (HERE / "sources.csv").exists() else []
    errs = check(base, cur, exp, changed, files_expected, sources=srcs)
    if other:
        errs.append(f"data files outside the scoped set were touched: {other[:5]}")
    if not srcs:
        errs.append("sources.csv missing (cannot inspect the cached pages)")
    # the hold: GLEIF must still show two separate registrations (a different authority and entity id), else the hold is stale
    gl = rows_of((HERE / "hold_SND-0101_gleif.csv").read_text(encoding="utf-8")) if (HERE / "hold_SND-0101_gleif.csv").exists() else []
    if len(gl) != 2 or gl[0]["registration_authority"] == gl[1]["registration_authority"] or gl[1]["authority_entity_id"] != "5360808":
        errs.append("hold_SND-0101_gleif.csv does not show two separately registered Farathane entities (cannot support the hold)")

    # idempotence: re-run the builder on a copy of the applied data
    tmp = Path(tempfile.mkdtemp(prefix="dm-apply-idem-"))
    try:
        shutil.copytree(ROOT / "data", tmp / "data")
        digest = lambda: {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (tmp / "data").glob("*.csv")}  # noqa: E731
        before = digest()
        r = subprocess.run([sys.executable, str(HERE / "build.py"), "--data-dir", str(tmp / "data"), "--no-journal"], capture_output=True, text=True)
        if r.returncode or before != digest() or "EVIDENCE rows 0" not in r.stdout or "RELATIONSHIP rows 0" not in r.stdout:
            errs.append(f"builder is not idempotent on the applied data (rc {r.returncode}): {r.stdout[-200:]}{r.stderr[-200:]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if "--selftest" in argv:
        print("selftest: each planted defect must be caught")
        if not selftest(base, cur, exp, changed, files_expected, srcs):
            errs.append("selftest: a planted defect was NOT caught")
    if errs:
        print(f"FAIL: {len(errs)} problem(s)")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    of, sf, rp, moves = exp
    n_ev = len([k for k in cur["evidence"] if k not in base["evidence"]])
    n_rel = len([k for k in cur["rel"] if k not in base["rel"]])
    print(f"PASS: {len(of)} org folds, {len(sf)} site folds, {len(rp)} repoints ({len(moves)} site moves), {n_ev} evidence rows, "
          f"{n_rel} relationship edges; held {sorted(HELD)}; idempotent; files {len(changed)}")


def selftest(base, cur, exp, changed, files_expected, srcs):
    import copy
    of, sf, rp, moves = exp
    ok = True

    def mut(fn, expect):
        c = copy.deepcopy(cur)
        fn(c)
        errs = check(base, c, exp, changed, files_expected, sources=srcs)
        hit = [e for e in errs if expect in e]
        print(("  ok   " if hit else "  FAIL ") + expect + ("" if hit else f"  (got {errs[:2]})"))
        return bool(hit)

    d0, s0 = of[0][0], of[0][1]
    folded_sites = {d for d, _, _ in sf}
    sf0 = sf[0][0]
    rp0 = next(iter(rp))
    new_ev = [k for k in cur["evidence"] if k not in base["evidence"]]
    frs_ev = next(k for k in new_ev if "registry id" in cur["evidence"][k]["claim_detail"])
    press_ev = next(k for k in new_ev if "registry id" not in cur["evidence"][k]["claim_detail"])
    solo = next(s for s in rp if sum(cur["evidence"][k]["record_id"] == s for k in new_ev) == 1)
    cap_moved = next(k for k, r in cur["caps"].items() if r["site_id"] in moves)
    unscoped = next(s for s in cur["sites"] if s not in moves and s not in folded_sites and s not in {x for _, x, _ in sf})
    ok &= mut(lambda c: c["sites"].pop(sf0), "disappeared")
    ok &= mut(lambda c: c["orgs"][d0].update(successor_org_id=""), "successor_org_id is ''")
    ok &= mut(lambda c: c["orgs"][d0].update(status="active"), "status is 'active'")
    ok &= mut(lambda c: c["sites"][sf0].update(operating_status="active"), "retired site must be closed")
    ok &= mut(lambda c: c["sites"][sf0].update(notes="closed"), "tombstone note must keep the old text")
    ok &= mut(lambda c: c["sites"][rp0].update(org_id=base["sites"][rp0]["org_id"]), ", expected ")
    ok &= mut(lambda c: c["sites"][rp0].update(site_name="renamed"), "unexpected columns changed")
    ok &= mut(lambda c: c["sites"][unscoped].update(notes="x"), "not in the scoped folds or repoints")
    ok &= mut(lambda c: c["orgs"][s0].update(tier1_qualifier="national_footprint"), "tier1_qualifier")
    ok &= mut(lambda c: c["evidence"].pop(next(k for k in new_ev if cur["evidence"][k]["record_id"] == solo)), "no evidence row")
    ok &= mut(lambda c: c["evidence"][frs_ev].update(claim_detail=c["evidence"][frs_ev]["claim_detail"].replace('"', "'", 2)), "do not equal the raw FRS JSON")
    ok &= mut(lambda c: c["evidence"][press_ev].update(claim_detail=c["evidence"][press_ev]["claim_detail"].rsplit('"', 2)[0] + '"never said this"'), "not found on the cached page")
    ok &= mut(lambda c: c["evidence"].update({"EVD-999999": dict(cur["evidence"][frs_ev], evidence_id="EVD-999999")}), "outside EVD-")
    ok &= mut(lambda c: c["evidence"][next(iter(base["evidence"]))].update(notes="edited"), "an existing row changed")
    ok &= mut(lambda c: c["rel"].pop(next(k for k in c["rel"] if k not in base["rel"])), "new edges")
    ok &= mut(lambda c: c["orgs"].update({"ORG-099999": dict(c["orgs"][s0], org_id="ORG-099999")}), "was added")
    ok &= mut(lambda c: c["links"].pop(next(iter(c["links"]))), "registry_links: row count changed")
    ok &= mut(lambda c: c["caps"][cap_moved].update(org_id="ORG-000006"), "does not equal its site's org_id")
    gem = next(k for k in new_ev if "gemspring.com" in cur["evidence"][k]["source_ref"])
    ok &= mut(lambda c: c["evidence"][gem].update(claim_detail=c["evidence"][gem]["claim_detail"].replace("release dated 2025-11-03 announces that an affiliate has completed", "an affiliate completed", 1).replace("(the release does not state the completion date)", "on 2025-11-03")), "does not date completion")
    lit = next(k for k in new_ev if cur["evidence"][k]["record_id"] == "SITE-003478" and "states no operator" in cur["evidence"][k]["claim_detail"])
    ok &= mut(lambda c: c["evidence"][lit].update(claim_detail=c["evidence"][lit]["claim_detail"].split(": the registrant name")[0] + " names the operator of this establishment: ORG-000131 (Tarkett North America), not ORG-001836 (Johnsonite Inc.)"), "shares no leading word")
    tri = next(k for k in new_ev if "TRI_FACILITY" in cur["evidence"][k]["source_ref"])
    ok &= mut(lambda c: c["evidence"][tri].update(claim_detail=c["evidence"][tri]["claim_detail"].replace("received 2025-06-27", "received 2024-01-01")), "not a received_date")
    return ok


if __name__ == "__main__":
    main()
