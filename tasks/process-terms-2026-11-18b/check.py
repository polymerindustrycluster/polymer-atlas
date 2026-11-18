#!/usr/bin/env python3
"""Recompute and prove PR B (owner ruling 2026-11-18b item 2): two new SCHEMA 3.1 terms and SITE-000562 `rubber_molding_transfer`.

Base = BASE env var, else merge-base of HEAD and origin/main. Proves, from the files (not from build.py's output):
  both terms are absent from the base vocabulary, and present in SCHEMA 3.1, validate.py PROCESSES and docs/schema/vocab.json; the rubber term is in the
  `rubber_molding` rollup line; SITE-000562 is tier C (so a union into `processes` is allowed); exactly one site row changed (csv count and an independent
  raw-line count agree), only in `processes`, old values kept in order, one term appended; every appended term is in the vocabulary; no other site
  (SITE-000248, the permit sites) and no site_capabilities row changed; exactly one evidence row added (every field equal to the planned row; its id above the maximum across all evidence shards at the merge-base and above 397199),
  every base evidence row intact; the quote is found in order in the sha256-checked stored page.
Then injects 11 defects and requires each caught. Exit 0 only when all hold.
"""
import copy, csv, hashlib, io, json, os, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build
NEW = ("rubber_molding_transfer", "composites_spray_up")
def git_show(ref, path): return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
def base_ref(): return os.environ.get("BASE") or subprocess.run(["git", "merge-base", "HEAD", "origin/main"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
def rd(text): return list(csv.DictReader(io.StringIO(text, newline="")))
def schema_terms(schema):
    sec = schema[schema.index("### 3.1 Processes"):schema.index("### 3.2")] if "### 3.2" in schema else schema
    return set(re.findall(r"`([a-z0-9_]+)`", sec))
def validator_processes(src):
    blk = src[src.index("PROCESSES"):]; blk = blk[:blk.index("]")]
    return set(re.findall(r'"([a-z0-9_]+)"', blk))
def prove(bs, ns, bev, nev, bcap, ncap, vocab, schema, vsrc, page_text, base_max_id):
    bad = []
    for t in NEW:
        if t not in schema_terms(schema): bad.append(f"{t} missing from SCHEMA 3.1")
        if t not in validator_processes(vsrc): bad.append(f"{t} missing from validate.py PROCESSES")
        if t not in vocab: bad.append(f"{t} missing from docs/schema/vocab.json PROCESSES")
    if not re.search(r"\| `rubber_molding` \| ROLLUP[^\n]*`rubber_molding_transfer`", schema): bad.append("rubber_molding rollup line lacks rubber_molding_transfer")
    bb = {r["site_id"]: r for r in bs}
    if [r["site_id"] for r in ns] != [r["site_id"] for r in bs]: bad.append("sites_OH row set or order changed")
    changed = [r["site_id"] for r in ns if r != bb.get(r["site_id"])]
    if changed != [build.SITE]: bad.append(f"changed sites {changed} differ from [{build.SITE}]")
    for r in ns:
        b = bb.get(r["site_id"])
        if b and r != b:
            cols = {c for c in r if r[c] != b[c]}
            if cols != {"processes"}: bad.append(f"{r['site_id']} changed columns {sorted(cols)} (only processes allowed)")
            old = [v for v in b["processes"].split(";") if v]; new = [v for v in r["processes"].split(";") if v]
            if new != old + ["rubber_molding_transfer"]: bad.append(f"{r['site_id']} processes is not the old values in order plus rubber_molding_transfer")
            for t in new[len(old):]:  # only appended terms are tested: old values (e.g. the legacy recycling_recovery) are not this PR's
                if t not in vocab: bad.append(f"{r['site_id']} appended term {t!r} is not in SCHEMA 3.1")
            if b["verification_tier"] != "C" or r["verification_tier"] != "C": bad.append(f"{r['site_id']} is not tier C: a menu term would be a site_capabilities row only")
    if bcap != ncap: bad.append("site_capabilities changed")
    bid = {e["evidence_id"]: e for e in bev}
    for eid, e in bid.items():
        if next((x for x in nev if x["evidence_id"] == eid), None) != e: bad.append(f"base evidence row {eid} edited or removed")
    new = [e for e in nev if e["evidence_id"] not in bid]
    (d,) = rd(open(HERE / "decisions.csv").read())
    if len(new) != 1 or new != [build.evidence_row(d, new[0]["evidence_id"])]: bad.append(f"new evidence rows differ from the planned single row ({[e['evidence_id'] for e in new]})")
    if new and int(min(e["evidence_id"] for e in new)[4:]) <= max(base_max_id, build.EVD_FLOOR): bad.append(f"lowest new evidence id {min(e['evidence_id'] for e in new)} does not exceed the base maximum EVD-{base_max_id} / the floor")
    for e in new:
        if not (e["evidence_id"] >= "EVD-%06d" % (max(base_max_id, build.EVD_FLOOR) + 1) and e["tier_effect"] == "supports_C" and e["claim_type"] == "scope" and e["source_class"] == "own_site"): bad.append(f"{e['evidence_id']} wrong id/strength/class")
        q = d["quote"].lower().split(); words = iter(re.findall(r"\w+", page_text)); 
        if not all(any(w == t for w in words) for t in re.findall(r"\w+", d["quote"].lower())): bad.append("quote words not found in order in the stored page")
        if hashlib.sha256((build.cap2a.CORPUS / d["raw_file"]).read_bytes()).hexdigest() != d["sha256"]: bad.append("stored page hash mismatch")
    return bad
def page_text_of(d):
    import html
    raw = (build.cap2a.CORPUS / d["raw_file"]).read_text(errors="replace")
    return html.unescape(re.sub(r"<[^>]+>", " ", raw)).lower()
def main():
    base = base_ref()
    base_max_id = max(int(r["evidence_id"][4:]) for p in subprocess.run(["git", "ls-tree", "--name-only", base, "data/"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
                      if Path(p).name.startswith("evidence_") for r in rd(git_show(base, p)))
    bs, bev = rd(git_show(base, "data/sites_OH.csv")), rd(git_show(base, "data/evidence_sites_OH.csv"))
    bcap = rd(git_show(base, "data/site_capabilities.csv"))
    ns, nev = rd((ROOT / "data/sites_OH.csv").read_text()), rd((ROOT / "data/evidence_sites_OH.csv").read_text())
    ncap = rd((ROOT / "data/site_capabilities.csv").read_text())
    schema, vsrc = (ROOT / "docs/SCHEMA.md").read_text(), (ROOT / "scripts/validate.py").read_text()
    vocab = set(json.loads((ROOT / "docs/schema/vocab.json").read_text())["vocabularies"]["PROCESSES"]["values"])
    bvocab = set(json.loads(git_show(base, "docs/schema/vocab.json"))["vocabularies"]["PROCESSES"]["values"])
    (d,) = rd(open(HERE / "decisions.csv").read()); page = page_text_of(d)
    raw_changed = subprocess.run(["git", "diff", "--numstat", base, "--", "data/sites_OH.csv"], cwd=ROOT, capture_output=True, text=True).stdout.split()[:2]
    changed = [r["site_id"] for r in ns if r != next(b for b in bs if b["site_id"] == r["site_id"])]
    tier = next(r for r in bs if r["site_id"] == build.SITE)["verification_tier"]
    print(f"base {base[:9]}: new terms absent from the base vocabulary: {all(t not in bvocab for t in NEW)}; {build.SITE} tier {tier} (union into processes allowed on C only)")
    print(f"base evidence maximum across all shards EVD-{base_max_id}; now: sites_OH rows changed (csv) {len(changed)}, independent raw-line numstat added/removed {raw_changed}; evidence_sites_OH rows added {len(nev) - len(bev)}; site_capabilities rows {len(ncap)} (base {len(bcap)}); "
          f"sites carrying composites_spray_up {sum('composites_spray_up' in r['processes'] for r in ns)}; SITE-000562 processes = {next(r for r in ns if r['site_id'] == build.SITE)['processes']}")
    fails = []
    if len(changed) != 1 or raw_changed != ["1", "1"]: fails.append(f"changed-row yield {len(changed)} differs from the raw-line count {raw_changed}")
    if any(t in bvocab for t in NEW): fails.append("a new term is already in the base vocabulary")
    fails += prove(bs, ns, bev, nev, bcap, ncap, vocab, schema, vsrc, page, base_max_id)
    def inject(name, mut):
        s, e, c, v, sc, vs = copy.deepcopy(ns), copy.deepcopy(nev), copy.deepcopy(ncap), set(vocab), schema, vsrc
        out = mut(s, e, c, v, sc, vs) or (s, e, c, v, sc, vs); s, e, c, v, sc, vs = out
        caught = prove(bs, s, bev, e, bcap, c, v, sc, vs, page, base_max_id)
        print(f"inject {name}: {'caught' if caught else 'NOT CAUGHT'}")
        if not caught: fails.append(f"defect not caught: {name}")
    site = lambda s, i: next(r for r in s if r["site_id"] == i)
    inject("a term not in SCHEMA 3.1 written to processes", lambda s, e, c, v, sc, vs: site(s, "SITE-000562").update(processes=site(s, "SITE-000562")["processes"].replace("rubber_molding_transfer", "rubber_molding_transferx")))
    inject("write outside scope (last_verified of the same site)", lambda s, e, c, v, sc, vs: site(s, "SITE-000562").update(last_verified="2026-11-18"))
    inject("write outside scope (SITE-000248 processes)", lambda s, e, c, v, sc, vs: site(s, "SITE-000248").update(processes=site(s, "SITE-000248")["processes"] + ";composites_spray_up"))
    inject("old term removed (union becomes replace)", lambda s, e, c, v, sc, vs: site(s, "SITE-000562").update(processes="recycling_recovery;rubber_molding_transfer"))
    new_id = lambda e: next(x["evidence_id"] for x in e if x["created_by"] == build.WHO and x["record_id"] == "SITE-000562" and x["claim_detail"].startswith("processes=rubber_molding_transfer"))
    inject("evidence row edited (strength raised)", lambda s, e, c, v, sc, vs: next(x for x in e if x["evidence_id"] == new_id(e)).update(tier_effect="supports_A"))
    inject("new evidence id fills a gap below the maximum", lambda s, e, c, v, sc, vs: next(x for x in e if x["evidence_id"] == new_id(e)).update(evidence_id="EVD-396950"))
    inject("a base evidence row edited", lambda s, e, c, v, sc, vs: next(x for x in e if x["evidence_id"] == "EVD-396503").update(notes="edited"))
    inject("term missing from the vocabulary export", lambda s, e, c, v, sc, vs: (s, e, c, v - {"composites_spray_up"}, sc, vs))
    inject("term missing from validate.py PROCESSES", lambda s, e, c, v, sc, vs: (s, e, c, v, sc, vs.replace('"rubber_molding_transfer", ', "", 1)))
    inject("rubber_molding rollup line not updated", lambda s, e, c, v, sc, vs: (s, e, c, v, sc.replace("+ `rubber_molding_transfer` **[v1.16]** + ", "+ "), vs))
    inject("site_capabilities row added", lambda s, e, c, v, sc, vs: (s, e, c + [dict(c[0])], v, sc, vs))
    if fails:
        print("FAIL"); [print(" -", f) for f in fails]; sys.exit(1)
    print("OK: all proofs hold and all injected defects were caught")
if __name__ == "__main__": main()
