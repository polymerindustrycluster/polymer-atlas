#!/usr/bin/env python3
"""Recomputes every published count, then proves the validators fail on injected defects. Exit 1 on any failure."""
import copy, csv, io, re, shutil, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(HERE))
from site_corpus import on_page
import build

SCHEMA = (ROOT / "docs/SCHEMA.md").read_text()
SEC31 = set(re.findall(r"`([a-z0-9_]+)`", SCHEMA.split("### 3.1 Processes")[1].split("### 3.2 Materials")[0]))
STRENGTHS = {"supports_A", "supports_C"}
git = lambda *a: subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout


def validate_claims(claims, pages, tiers=None):
    tiers = tiers or {r["org_id"]: r["verification_tier"] for r in build.read(ROOT / "data" / build.ORG_SHARD)}
    for c in claims:
        who = f"{c['org_id']} {c['term']}"
        assert c["org_id"] in build.ORGS, f"{who}: org outside the frame"
        assert c["term"] in SEC31, f"{who}: term not in SCHEMA 3.1"
        assert c["strength"] in STRENGTHS, f"{who}: strength {c['strength']}"
        assert not (c["strength"] == "supports_C" and tiers[c["org_id"]] in "AB"), f"{who}: supports_C scope term on tier {tiers[c['org_id']]} fails V-25"
        pg = [p for p in pages if p["org_id"] == c["org_id"] and p["text_file"] and Path(p["text_file"]).name == c["page"]]
        assert pg, f"{who}: page {c['page']} is not a stored page of the org"
        assert pg[0]["sha_ok"], f"{who}: stored page sha256 does not match its manifest"
        assert c["observed_date"] == pg[0]["observed_date"], f"{who}: observed_date is not the page's stored date"
        assert on_page(c["quote"], Path(pg[0]["text_file"]).read_text(errors="replace")), f"{who}: quote not found in stored page"


def check_diff(base_orgs, head_orgs, base_sites, head_sites):
    """Only a blank `processes` cell on a frame organization row may change; no site row may change. Returns the applied org ids."""
    b = {r["org_id"]: r for r in base_orgs}; h = {r["org_id"]: r for r in head_orgs}; applied = []
    assert set(b) == set(h), "organization rows added or removed"
    for oid, r in h.items():
        diff = {k for k in r if r[k] != b[oid][k]}
        if not diff: continue
        assert oid in build.ORGS, f"{oid}: row outside the frame changed"
        assert diff == {"processes"}, f"{oid}: columns other than processes changed: {sorted(diff)}"
        assert b[oid]["processes"] == "", f"{oid}: write to a non-blank processes cell"
        applied.append(oid)
    assert base_sites == head_sites, "a site row changed"
    return applied


def load_sites(root_dir):
    return {r["site_id"]: r for f in sorted(Path(root_dir).glob("sites_*.csv")) for r in build.read(f)}


def check_verdicts(verdicts, claims, holds):
    """Every frame ID has exactly one verdict; VERIFIED iff it has claims; a held verdict matches holds.csv."""
    ids = [v["org_id"] for v in verdicts]
    assert sorted(ids) == sorted(build.ORGS), f"verdicts do not cover the frame exactly once: {sorted(set(build.ORGS) ^ set(ids)) or 'duplicate id'}"
    held = sorted(set(build.ORGS) - {c["org_id"] for c in claims})
    assert sorted(h["org_id"] for h in holds) == held, "holds.csv must have exactly one row per held org id (missing, extra or duplicate row)"  # list, before any dict
    hd = {h["org_id"]: h for h in holds}
    assert all(h["reason"].strip() and h["settling_fact"].strip() for h in holds), "a hold has a blank reason or settling fact"
    for v in verdicts:
        o = v["org_id"]; terms = ";".join(sorted(c["term"] for c in claims if c["org_id"] == o))
        assert v["stratum"] == build.STRATUM[o] and v["terms"] == terms, f"{o}: stratum or terms disagree with the frame and claims"
        if terms: assert v["verdict"] == "VERIFIED" and not v["hold_reason"] and not v["settling_fact"], f"{o}: claims but not a clean VERIFIED"
        else: assert v["verdict"] == "STILL_UNCERTAIN" and v["hold_reason"] == hd[o]["reason"] and v["settling_fact"] == hd[o]["settling_fact"], f"{o}: held verdict does not match holds.csv"


def check_evidence(ev_rows, claims):
    block = [r for r in ev_rows if r["evidence_id"].startswith("EVD-396")]
    assert all(build.EVD_LO <= int(r["evidence_id"][4:]) <= build.EVD_HI for r in block), "evidence id outside EVD-396000..396099"
    assert len(block) == len(claims), f"evidence rows {len(block)} != claims {len(claims)}"
    assert all(r["record_table"] == "organizations" and r["claim_type"] == "scope" and r["source_class"] == "own_site" for r in block)
    return len(block)


def base_data():
    base = git("merge-base", "HEAD", "origin/main").strip()
    names = [n for n in git("ls-tree", "--name-only", base, "data/").split() if n.split("/")[-1].startswith(("sites_", build.ORG_SHARD, build.EVD_SHARD))]
    show = lambda n: list(csv.DictReader(io.StringIO(git("show", f"{base}:{n}"), newline="")))
    sites = {r["site_id"]: r for n in names if "sites_" in n and "evidence" not in n for r in show(n)}
    return base, show(f"data/{build.ORG_SHARD}"), sites, show(f"data/{build.EVD_SHARD}")


def selftest(pages):
    ctrl = dict(org_id="ORG-001986", term="rotational_molding", page="09f2287b75bc27a4b02e6f42cdab10d08742afdb76e2f0cfb8d1e0fc12501a7c.txt",
                quote="has worked with the ROTOMOLDING community for over 35 years", strength="supports_A", observed_date="2026-11-16")
    validate_claims([ctrl], pages)  # positive control: fixture only, never written to data
    def fails(name, fn):
        try: fn()
        except AssertionError as e: print(f"  injected defect refused: {name}: {e}"); return
        raise SystemExit(f"FAIL: injected defect NOT caught: {name}")
    fails("term not in 3.1", lambda: validate_claims([{**ctrl, "term": "rotomolding"}], pages))
    fails("quote not in stored page", lambda: validate_claims([{**ctrl, "quote": "we rotationally mold polyethylene tanks"}], pages))
    fails("supports_C on tier B", lambda: validate_claims([{**ctrl, "strength": "supports_C"}], pages))
    fails("page hash mismatch", lambda: validate_claims([ctrl], [{**p, "sha_ok": False} for p in pages]))
    fails("org outside frame", lambda: validate_claims([{**ctrl, "org_id": "ORG-000001"}], pages, {"ORG-000001": "A"}))
    hold_rows = build.read(HERE / "holds.csv"); ver = build.read(HERE / "verdicts.csv")
    check_verdicts(ver, [], hold_rows)
    fails("held verdict missing", lambda: check_verdicts(ver[:-1], [], hold_rows))
    fails("verdict duplicated", lambda: check_verdicts(ver[:-1] + [ver[0]], [], hold_rows))
    fails("held verdict differs from holds.csv", lambda: check_verdicts([{**ver[0], "settling_fact": "x"}] + ver[1:], [], hold_rows))
    fails("conflicting duplicate hold row", lambda: check_verdicts(ver, [], [{**hold_rows[-1], "settling_fact": "conflicting entry"}] + hold_rows))
    blank_v = ver[:-1] + [{**ver[-1], "settling_fact": ""}]; blank_h = hold_rows[:-1] + [{**hold_rows[-1], "settling_fact": ""}]
    fails("blank settling fact (verdict and hold both empty)", lambda: check_verdicts(blank_v, [], blank_h))
    fails("hold row missing", lambda: check_verdicts(ver, [], hold_rows[:-1]))
    with tempfile.TemporaryDirectory() as d:  # image bodies are not pages
        g = Path(d) / "a.txt"; g.write_bytes(b"GIF89a\x01\x00"); assert build.is_image(g)
        g.write_bytes(b"\x89PNG\r\n\x1a\n"); assert build.is_image(g)
        g.write_text("Our extrusion capabilities"); assert not build.is_image(g)
    with tempfile.TemporaryDirectory() as d:  # the writer, on a copy
        d = Path(d)
        for n in (build.ORG_SHARD, build.EVD_SHARD): shutil.copy(ROOT / "data" / n, d / n)
        base_o, base_e = build.read(d / build.ORG_SHARD), build.read(d / build.EVD_SHARD)
        assert build.apply([ctrl], d, pages) == 1
        snap = (d / build.ORG_SHARD).read_bytes(), (d / build.EVD_SHARD).read_bytes()
        assert build.apply([ctrl], d, pages) == 0 and snap == ((d / build.ORG_SHARD).read_bytes(), (d / build.EVD_SHARD).read_bytes()), "apply not idempotent"
        head_o = build.read(d / build.ORG_SHARD)
        assert check_diff(base_o, head_o, {}, {}) == ["ORG-001986"]; assert check_evidence(build.read(d / build.EVD_SHARD), [ctrl]) == 1
        bad = copy.deepcopy(head_o); next(r for r in bad if r["org_id"] == "ORG-001986")["materials"] = "thermoplastics"
        fails("write to a non-process column", lambda: check_diff(base_o, bad, {}, {}))
        pre = copy.deepcopy(base_o); next(r for r in pre if r["org_id"] == "ORG-001986")["processes"] = "extrusion_sheet"
        fails("write to a non-blank cell", lambda: check_diff(pre, head_o, {}, {}))
        s = load_sites(ROOT / "data"); s2 = copy.deepcopy(s); s2["SITE-001980"]["processes"] = "rotational_molding"
        fails("write to a site row", lambda: check_diff(base_o, head_o, s, s2))
        fails("evidence id out of range", lambda: check_evidence([{**build.read(d / build.EVD_SHARD)[-1], "evidence_id": "EVD-396100"}], [ctrl]))


def main():
    pages = build.stored_pages(); claims = build.read(HERE / "claims.csv"); verdicts = build.read(HERE / "verdicts.csv")
    base, base_o, base_s, _ = base_data()
    head_o = build.read(ROOT / "data" / build.ORG_SHARD)
    validate_claims(claims, pages)
    check_verdicts(verdicts, claims, build.read(HERE / "holds.csv"))
    applied = check_diff(base_o, head_o, base_s, load_sites(ROOT / "data"))
    n_ev = check_evidence(build.read(ROOT / "data" / build.EVD_SHARD), claims)
    assert sorted(applied) == sorted({c["org_id"] for c in claims}), "applied orgs differ from claims"
    assert sorted(r["org_id"] for r in verdicts if r["verdict"] == "VERIFIED") == sorted(applied), "verdicts.csv disagrees with the data"
    # independent count of the input: readable text files on disk vs manifest rows that say ok
    disk = sum(1 for o in build.ORGS for f in (build.CORPUS / o).glob("*.txt") if not build.is_image(f)) + sum(1 for p in pages if p["source"] == "live" and p["text_file"])
    manifest_ok = sum(1 for p in pages if p["text_file"])
    assert disk == manifest_ok, f"pages on disk {disk} != manifest ok pages {manifest_ok}"
    assert all(p["sha_ok"] for p in pages if p["status"] == "ok"), "a stored page fails its sha256"
    assert not [p for p in pages if p["status"] == "ok" and not p["text_file"] and not p["image"]], "an ok page has no text and is not an image"
    assert all(not (p["image"] and p["text_file"]) for p in pages), "an image counted as a readable page"
    assert len(base_o) and sum(1 for r in head_o if r["org_id"] in build.ORGS and r["processes"] == "") == 10 - len(applied)
    allowed = {f"data/{build.ORG_SHARD}", f"data/{build.EVD_SHARD}"}
    touched = set(git("diff", "--name-only", base, "--", "data/").split()) | set(git("ls-files", "--others", "--exclude-standard", "data/").split())
    assert touched <= allowed, f"files outside the allowed shards changed: {sorted(touched - allowed)}"
    selftest(pages)
    have = {o for o in build.ORGS if any(p["org_id"] == o and p["text_file"] for p in pages)}
    print(f"frame={len(build.ORGS)} orgs (H {len(build.FRAME['H'])}, N {len(build.FRAME['N'])}); manifest/live rows={len(pages)}; readable text pages={manifest_ok}; "
          f"orgs with >=1 readable page={len(have)}; claims={len(claims)}; orgs applied={len(applied)} "
          f"(H {sum(build.STRATUM[o]=='H' for o in applied)}/5, N {sum(build.STRATUM[o]=='N' for o in applied)}/5); evidence rows={n_ev}; base={base[:7]}")
    out = lambda ref: subprocess.run(["python3", str(build.S.parent / "harness/pic18_unknown.py"), str(ROOT), ref], capture_output=True, text=True, check=True).stdout
    unk = lambda ref: int(re.search(r"proc_unknown=(\d+)", out(ref))[1])
    assert unk(base) == 331, "baseline process_unknown at 099497f is 331"
    assert unk(base) - unk("HEAD") == len(applied), "process_unknown fall != organizations applied (commit first: the harness reads git refs)"
    print(out(base).strip()); print(out("HEAD").strip(), f"fall={unk(base) - unk('HEAD')}")
    print("check.py OK")


if __name__ == "__main__":
    main()
