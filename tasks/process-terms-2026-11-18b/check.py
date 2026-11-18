#!/usr/bin/env python3
"""Recompute and prove PR B (owner ruling 2026-11-18b item 2): two new SCHEMA 3.1 terms and SITE-000562 `rubber_molding_transfer`.

Base = BASE env var, else merge-base of HEAD and origin/main. Proves, from the files (not from build.py's output):
  vocabulary: the PROCESSES vocabulary, the §3.1 term set and the validate.py PROCESSES set each equal the base set plus exactly the two new terms; the
  `rubber_molding` rollup members equal the base members plus exactly rubber_molding_transfer; SITE-000562 is tier C;
  sites_OH: same row count and ids as the base, no duplicate id, and the rows equal the base rows with only SITE-000562 `processes` changed (old values in order
  plus one appended, vocabulary term); site_capabilities unchanged; evidence_sites_OH: exactly base + 1 rows, unique ids, base rows intact and in order, the one new
  row equal in every field to the planned row, its id above the base maximum across all shards and above the floor; the quote carries the word of the term; the
  quote is found in order in the sha256-checked stored page; the cited URL and the locality URL are the manifest entries (url, sha256, files, organization) of the stored pages.
Then replays build.py on disposable copies of the base (clean build reproduces the committed bytes; a replay writes nothing; a wrong quote, swapped URLs, a truncated or
duplicated shard are refused before any write) and injects defects into the committed result, requiring each caught. Exit 0 only when all hold.
"""
import copy, csv, io, json, os, re, shutil, subprocess, sys, tempfile
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
    sec = schema[schema.index("### 3.1 Processes"):schema.index("### 3.2")]
    return set(re.findall(r"`([a-z0-9_]+)`", sec))
def validator_processes(src):
    blk = src[src.index("PROCESSES"):]; blk = blk[:blk.index("]")]
    return set(re.findall(r'"([a-z0-9_]+)"', blk))
def rollup_members(schema):
    line = next(l for l in schema.splitlines() if l.startswith("| `rubber_molding` | ROLLUP"))
    return re.findall(r"`([a-z0-9_]+)`", line.split("ROLLUP", 1)[1])
def expected_sites(bs):
    out = copy.deepcopy(bs)
    s = next(r for r in out if r["site_id"] == build.SITE)
    s["processes"] = ";".join([v for v in s["processes"].split(";") if v] + ["rubber_molding_transfer"])
    return out
def prove(B, N, d, man, page_text, base_max_id):
    """B/N: dicts of base/now inputs. Returns the list of failures."""
    bad = []
    bs, ns, bev, nev = B["sites"], N["sites"], B["ev"], N["ev"]
    for t in NEW:
        if t not in schema_terms(N["schema"]): bad.append(f"{t} missing from SCHEMA 3.1")
    if schema_terms(N["schema"]) != schema_terms(B["schema"]) | set(NEW): bad.append("the SCHEMA 3.1 term set is not the base set plus exactly the two new terms")
    if validator_processes(N["vsrc"]) != validator_processes(B["vsrc"]) | set(NEW): bad.append("validate.py PROCESSES is not the base set plus exactly the two new terms")
    if N["vocab"] != B["vocab"] | set(NEW): bad.append("the vocabulary export PROCESSES is not the base set plus exactly the two new terms")
    bm, nm = rollup_members(B["schema"]), rollup_members(N["schema"])
    if sorted(nm) != sorted(bm + ["rubber_molding_transfer"]): bad.append(f"rubber_molding rollup members {nm} are not the base members {bm} plus rubber_molding_transfer")
    site = next((r for r in bs if r["site_id"] == build.SITE), None)
    if not site or site["verification_tier"] != "C": bad.append(f"{build.SITE} is not tier C at the base: a menu term would be a site_capabilities row only")
    # sites_OH: counts, ids, full rows
    if len(ns) != len(bs): bad.append(f"sites_OH has {len(ns)} rows, base {len(bs)}")
    if len({r["site_id"] for r in ns}) != len(ns): bad.append("duplicate site_id in sites_OH")
    if ns != expected_sites(bs): bad.append("sites_OH rows differ from the base rows with only SITE-000562 processes + rubber_molding_transfer (a row dropped, added or another cell written)")
    nvals = [v for r in ns if r["site_id"] == build.SITE for v in r["processes"].split(";") if v]
    if nvals[-1:] and nvals[-1] not in N["vocab"]: bad.append(f"appended term {nvals[-1]!r} is not in SCHEMA 3.1")
    if B["cap"] != N["cap"]: bad.append("site_capabilities changed")
    # evidence: exact count, unique ids, base intact and in order, full planned row
    if len(nev) != len(bev) + 1: bad.append(f"evidence_sites_OH has {len(nev)} rows, expected base {len(bev)} + 1")
    if len({e["evidence_id"] for e in nev}) != len(nev): bad.append("duplicate evidence_id in evidence_sites_OH")
    bids = {e["evidence_id"] for e in bev}
    if [e for e in nev if e["evidence_id"] in bids] != bev: bad.append("base evidence rows edited, removed, duplicated or reordered")
    new = [e for e in nev if e["evidence_id"] not in bids]
    try: build.check_decision(d, site["org_id"] if site else "")
    except AssertionError as ex: bad.append(f"decision check failed: {ex}")
    if len(new) != 1 or new != [build.evidence_row(d, new[0]["evidence_id"])]: bad.append(f"new evidence rows differ from the planned single row ({[e['evidence_id'] for e in new]})")
    for e in new:
        if int(e["evidence_id"][4:]) <= max(base_max_id, build.EVD_FLOOR): bad.append(f"new evidence id {e['evidence_id']} does not exceed the base maximum EVD-{base_max_id} / the floor")
        if not (e["tier_effect"] == "supports_C" and e["claim_type"] == "scope" and e["source_class"] == "own_site"): bad.append(f"{e['evidence_id']} wrong strength/class")
        if build.TERM_WORD[build.TERM] not in e["claim_detail"].lower(): bad.append(f"{e['evidence_id']}: the quote lacks the word of the term")
    if not all(any(w == t for w in it) for it in [iter(re.findall(r"\w+", page_text))] for t in re.findall(r"\w+", d["quote"].lower())): bad.append("quote words not found in order in the stored page")
    return bad
def page_text_of(d):
    import html
    return html.unescape(re.sub(r"<[^>]+>", " ", (build.cap2a.CORPUS / d["raw_file"]).read_text(errors="replace"))).lower()
def main():
    base = base_ref()
    def at_base(p): return git_show(base, p)
    base_max_id = max(int(r["evidence_id"][4:]) for p in subprocess.run(["git", "ls-tree", "--name-only", base, "data/"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
                      if Path(p).name.startswith("evidence_") for r in rd(at_base(p)))
    voc = lambda text: set(json.loads(text)["vocabularies"]["PROCESSES"]["values"])
    B = dict(sites=rd(at_base("data/sites_OH.csv")), ev=rd(at_base("data/evidence_sites_OH.csv")), cap=rd(at_base("data/site_capabilities.csv")),
             vocab=voc(at_base("docs/schema/vocab.json")), schema=at_base("docs/SCHEMA.md"), vsrc=at_base("scripts/validate.py"))
    N = dict(sites=rd((ROOT / "data/sites_OH.csv").read_text()), ev=rd((ROOT / "data/evidence_sites_OH.csv").read_text()), cap=rd((ROOT / "data/site_capabilities.csv").read_text()),
             vocab=voc((ROOT / "docs/schema/vocab.json").read_text()), schema=(ROOT / "docs/SCHEMA.md").read_text(), vsrc=(ROOT / "scripts/validate.py").read_text())
    (d,) = rd((HERE / "decisions.csv").read_text()); page = page_text_of(d); man = build.manifest_by_file()
    raw_changed = subprocess.run(["git", "diff", "--numstat", base, "--", "data/sites_OH.csv"], cwd=ROOT, capture_output=True, text=True).stdout.split()[:2]
    changed = [r["site_id"] for r, b in zip(N["sites"], B["sites"]) if r != b]
    print(f"base {base[:9]}: new terms absent from the base vocabulary: {all(t not in B['vocab'] for t in NEW)}; {build.SITE} tier {next(r for r in B['sites'] if r['site_id'] == build.SITE)['verification_tier']}; "
          f"sites_OH rows {len(B['sites'])}, evidence_sites_OH rows {len(B['ev'])}, evidence maximum across all shards EVD-{base_max_id}")
    print(f"now: sites_OH rows {len(N['sites'])}, rows changed (csv) {len(changed)}, independent raw-line numstat added/removed {raw_changed}; evidence_sites_OH rows {len(N['ev'])} (added {len(N['ev']) - len(B['ev'])}); "
          f"site_capabilities rows {len(N['cap'])} (base {len(B['cap'])}); sites carrying composites_spray_up {sum('composites_spray_up' in r['processes'] for r in N['sites'])}; rollup members {rollup_members(N['schema'])}")
    fails = []
    if len(changed) != 1 or raw_changed != ["1", "1"]: fails.append(f"changed-row yield {len(changed)} differs from the raw-line count {raw_changed}")
    fails += prove(B, N, d, man, page, base_max_id)
    def inject(name, mut):
        b, n, dd = copy.deepcopy(B), copy.deepcopy(N), dict(d)
        mut(n, dd)
        pg = page_text_of(dd) if dd["raw_file"] == d["raw_file"] else ""
        caught = prove(b, n, dd, man, pg, base_max_id)
        print(f"inject {name}: {'caught' if caught else 'NOT CAUGHT'}")
        if not caught: fails.append(f"defect not caught: {name}")
    site = lambda n, i: next(r for r in n["sites"] if r["site_id"] == i)
    newev = lambda n: next(x for x in n["ev"] if x["created_by"] == build.WHO and x["record_id"] == build.SITE and x["claim_detail"].startswith("processes=rubber_molding_transfer"))
    inject("a term not in SCHEMA 3.1 written to processes", lambda n, dd: site(n, build.SITE).update(processes=site(n, build.SITE)["processes"].replace("rubber_molding_transfer", "rubber_molding_transferx")))
    inject("write outside scope (last_verified of the same site)", lambda n, dd: site(n, build.SITE).update(last_verified="2026-11-18"))
    inject("write outside scope (SITE-000248 processes)", lambda n, dd: site(n, "SITE-000248").update(processes=site(n, "SITE-000248")["processes"] + ";composites_spray_up"))
    inject("old term removed (union becomes replace)", lambda n, dd: site(n, build.SITE).update(processes="recycling_recovery;rubber_molding_transfer"))
    inject("evidence row edited (strength raised)", lambda n, dd: newev(n).update(tier_effect="supports_A"))
    inject("new evidence id fills a gap below the maximum", lambda n, dd: newev(n).update(evidence_id="EVD-396950"))
    inject("a base evidence row edited", lambda n, dd: next(x for x in n["ev"] if x["evidence_id"] == "EVD-396503").update(notes="edited"))
    inject("term missing from the vocabulary export", lambda n, dd: n.update(vocab=n["vocab"] - {"composites_spray_up"}))
    inject("term missing from validate.py PROCESSES", lambda n, dd: n.update(vsrc=n["vsrc"].replace('"rubber_molding_transfer", ', "", 1)))
    inject("rollup line not updated", lambda n, dd: n.update(schema=n["schema"].replace("+ `rubber_molding_transfer` **[v1.16]** + ", "+ ")))
    inject("rollup member swapped for a plastics subtype (rubber_molding_injection -> transfer_molding)", lambda n, dd: n.update(schema=n["schema"].replace("`rubber_molding_injection` |", "`transfer_molding` |", 1)))
    inject("site_capabilities row added", lambda n, dd: n["cap"].append(dict(n["cap"][0])))
    inject("quote supports compression molding only (no 'transfer')", lambda n, dd: (dd.update(quote="Compression Molding"), newev(n).update(claim_detail="processes=rubber_molding_transfer; quote: Compression Molding")))
    inject("cited URL and locality URL swapped", lambda n, dd: (dd.update(url=d["grain_url"], grain_url=d["url"]), newev(n).update(source_ref=d["grain_url"])))
    inject("one unrelated site row dropped (truncated shard)", lambda n, dd: n["sites"].pop(next(i for i, r in enumerate(n["sites"]) if r["site_id"] != build.SITE)))
    inject("one evidence row duplicated", lambda n, dd: n["ev"].insert(1, dict(n["ev"][0])))
    inject("one unrelated evidence row dropped (truncated shard)", lambda n, dd: n["ev"].pop(0))
    # build.py on disposable copies of the base
    def disposable(mut=None, decisions=None):
        with tempfile.TemporaryDirectory() as root:
            data = Path(root) / "data"; data.mkdir()
            for name in ("sites_OH.csv", "evidence_sites_OH.csv"): (data / name).write_text(at_base(f"data/{name}"))
            dec = Path(root) / "decisions.csv"; shutil.copy(decisions or HERE / "decisions.csv", dec)
            if mut: mut(data, dec)
            before = {p.name: p.read_bytes() for p in data.iterdir()}
            try: build.main(data, dec); refused = False
            except (AssertionError, SystemExit): refused = True
            return refused, all(p.read_bytes() == before[p.name] for p in data.iterdir()), {p.name: p.read_bytes() for p in data.iterdir()}
    def rewrite(path, fn):
        rows = rd(path.read_text()); fn(rows)
        buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows); path.write_text(buf.getvalue())
    ok_refused, _, out = disposable()
    same = not ok_refused and all(out[n] == (ROOT / "data" / n).read_bytes() for n in out)
    print(f"build.py on the base reproduces the committed shards byte for byte: {same}")
    if not same: fails.append("a clean build from the base does not reproduce the committed shards")
    # replay: apply once, then run again; the second run must not rewrite either shard (mtime and bytes)
    with tempfile.TemporaryDirectory() as root:
        data = Path(root) / "data"; data.mkdir()
        for name in ("sites_OH.csv", "evidence_sites_OH.csv"): shutil.copy(ROOT / "data" / name, data / name)
        for p in data.iterdir(): os.utime(p, ns=(1, 1))
        build.main(data, HERE / "decisions.csv")
        replay_quiet = all(p.stat().st_mtime_ns == 1 for p in data.iterdir())
    print(f"replay of build.py on the applied shards writes nothing: {replay_quiet}")
    if not replay_quiet: fails.append("a replay rewrote a shard")
    def refusal(name, mut):
        refused, untouched, _ = disposable(mut)
        ok = refused and untouched
        print(f"build.py {name}: refused={refused} inputs unchanged={untouched}: {'OK' if ok else 'NOT REFUSED'}")
        if not ok: fails.append(f"build.py did not refuse: {name}")
    refusal("with a quote that supports compression molding only", lambda data, dec: rewrite(dec, lambda rows: rows[0].update(quote="Compression Molding")))
    refusal("with the cited and locality URLs swapped", lambda data, dec: rewrite(dec, lambda rows: rows[0].update(url=rows[0]["grain_url"], grain_url=rows[0]["url"])))
    refusal("on a base with one unrelated site row and one evidence row removed", lambda data, dec: (rewrite(data / "sites_OH.csv", lambda rows: rows.pop(next(i for i, r in enumerate(rows) if r["site_id"] != build.SITE))), rewrite(data / "evidence_sites_OH.csv", lambda rows: rows.pop(0))))
    refusal("on a base with one evidence row duplicated", lambda data, dec: rewrite(data / "evidence_sites_OH.csv", lambda rows: rows.insert(1, dict(rows[0]))))
    refusal("on a tier A base row", lambda data, dec: rewrite(data / "sites_OH.csv", lambda rows: next(r for r in rows if r["site_id"] == build.SITE).update(verification_tier="A")))
    if fails:
        print("FAIL"); [print(" -", f) for f in fails]; sys.exit(1)
    print("OK: all proofs hold and all injected defects were caught")
if __name__ == "__main__": main()
