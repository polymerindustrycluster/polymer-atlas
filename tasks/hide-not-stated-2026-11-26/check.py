"""Named check for the 2026-11-26 NOT_STATED withholding. Run: python3 -I tasks/hide-not-stated-2026-11-26/check.py [--store PERSIST_DIR]
PERSIST_DIR is the controller's page store (or set ATLAS_PAGE_STORE); without it the page-URL manifest check, the pack comparison and the earlier second-family reads
are NOT_INSPECTED and the exit code is 3, never 0.

verify() regenerates data/value_basis.csv with scripts/value_basis.py from the repo's data, every other tasks/ folder and this folder's VALUE_VERDICTS.csv, and compares the
WHOLE table with the pinned base: same key set, same order and format, and the only differences are the keys of this folder's lines, each not_yet_checked ->
not_found_pending_refetch, each on its own record (SCHEMA §4.24 grain). Every withheld key must be a `withhold` line of second-family/ADJUDICATION-hide.csv whose second-family
class, recomputed from the inputs, is NOT_STATED; every `hold` line stays out. Then each planted defect must be rejected by the rule it names."""
import csv, hashlib, io, os, shutil, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
import build  # noqa: E402
import value_basis as vb  # noqa: E402

BASE = "12e79893"  # origin/main after #575 (git resolves the short form)
EXPECT = {("organizations", "markets_served"): 13, ("organizations", "processes"): 2, ("sites", "processes"): 11, ("sites", "markets_served"): 11}  # 37 keys
EXPECT_HOLDS = 42
EXPECT_REJECTED = 184
EXPECT_CANDIDATES = 263  # 79 adjudicated + 184 rejected
key = build.key
k3 = lambda r: (r["record_id"], r["field"], r["value"])
CLAIM_COLS = ["table", "record_id", "field", "verdict", "evidence_id"]
table = lambda text: {key(r): r for r in csv.DictReader(io.StringIO(text))}
GRAIN_REASON = "organization row only"


def second_family(store, adj):
    """{(record_id, field, value): class} the second family gave, from the primary inputs: the blind read of 2026-11-26 (second-family/read_scored.csv) and, with the store,
    the 2026-11-24 rounds. Returns (map, keys taken from the adjudication's own column because there is no store)."""
    second = {k3(r): r["second_class"] for r in build.read(HERE / "second-family/read_scored.csv") if r["batch_void"] == "False"}
    if store:
        for p in ("second-family/verdicts.csv", "second-family/round2/verdicts.csv"):
            for r in build.read(store / "requote-all-2026-11-24" / p):
                second.setdefault(k3(r), r["your_class"])
        return second, []
    missing = [a for a in adj if k3(a) not in second and a["second_family_class"] == "NOT_STATED"]
    second.update({k3(a): "NOT_STATED" for a in missing})
    return second, [k3(a) for a in missing]


def tasks_tree(tmp, verdicts, urls):
    """A tasks/ tree: every other tasks/ folder (symlinked: the proofs and the #575 verdicts the table also rests on) plus this folder with the (possibly planted) lines."""
    t = Path(tmp) / "tasks"
    t.mkdir()
    for d in sorted((ROOT / "tasks").iterdir()):
        if d.is_dir() and d.name != HERE.name:
            (t / d.name).symlink_to(d)
    d = t / HERE.name
    d.mkdir()
    shutil.copy(HERE / "README.md", d)
    build.write(d / "VALUE_VERDICTS.csv", vb.VERDICT_COLS, verdicts)
    build.write(d / "VALUE_PAGES.csv", ["page_sha256", "page_url", "requested_url"], [{"page_sha256": s, "page_url": u, "requested_url": q} for s, (u, q) in urls.items()])
    return t


def expected_claims(head_text, base_text, holds):
    """CLAIMS_CHECKED.csv: `withdrawn` for each key whose basis changed, `held` for each held key, each with the bound row the key rests on."""
    head, base = table(head_text), table(base_text)
    rows = [dict(zip(CLAIM_COLS, (k[0], k[1], k[2], "withdrawn", head[k]["evidence_id"]))) for k in sorted(head) if head[k] != base[k]]
    return rows + [dict(zip(CLAIM_COLS, (k[0], k[1], k[2], "held", head[k]["evidence_id"]))) for k in sorted(key(h) for h in holds)]


def claims_problems(claims, head_text, base_text, holds):
    """The file has no value column (the harness's format), so its rows are compared with the changed and held keys as a multiset."""
    row = lambda r: tuple(r[c] for c in CLAIM_COLS)
    have, want = Counter(map(row, claims)), Counter(map(row, expected_claims(head_text, base_text, holds)))
    return [("claims", f"CLAIMS_CHECKED.csv differs from the keys withheld or held: {sum((have - want).values())} rows not wanted, {sum((want - have).values())} missing")] if have != want else []


def frame_problems(adj, rejected, store):
    """263 candidates = 79 adjudicated + 184 rejected; with the store, the candidates are recomputed from the pack (the 249 NOT_STATED lines, the 2 lines the 2026-11-24
    adjudication takes to NOT_STATED, the 12 census lines of tasks/reread-labels-2026-11-26/HOLDS.csv)."""
    bad = []
    rkeys = [key(r) for r in rejected]
    if len(set(rkeys)) != len(rkeys) or len(rkeys) != EXPECT_REJECTED:
        bad.append(("frame", f"REJECTED.csv has {len(rkeys)} lines, {len(set(rkeys))} distinct keys, expected {EXPECT_REJECTED}"))
    both = {key(a) for a in adj} & set(rkeys)
    if both:
        bad.append(("frame", f"{len(both)} keys are both adjudicated and rejected: {sorted(both)[:2]}"))
    if store:
        pack = store / "requote-all-2026-11-24"
        lines = build.read(pack / "values.csv")
        cand = {key(r) for r in lines if r["class"] == "NOT_STATED"}
        by3 = {k3(r): key(r) for r in lines}
        cand |= {by3[k3(a)] for a in build.read(pack / "second-family/adjudicated.csv") if a["adjudicated_class"] == "NOT_STATED"}
        cand |= {key(h) for h in build.read(ROOT / "tasks/reread-labels-2026-11-26/HOLDS.csv") if h["reason"].startswith("Gemini 4 Hydrogen census NOT_STATED")}
        if cand != {key(a) for a in adj} | set(rkeys) or len(cand) != EXPECT_CANDIDATES:
            bad.append(("frame", f"the candidates recomputed from the pack ({len(cand)}) differ from the adjudicated and rejected keys ({len(adj) + len(rkeys)})"))
    return bad


def verify(verdicts, urls, head_text, base_text, store, adj, holds, second, grain_keys, pack_lines):
    """-> [(code, message)]; empty means every rule held. Pure over its arguments so planted defects can be injected."""
    bad, err = [], lambda code, msg: bad.append((code, msg))
    withhold = {key(a) for a in adj if a["action"] == "withhold"}
    hold_keys = {key(a) for a in adj if a["action"] == "hold"}
    have = {key(r): r for r in verdicts}
    for r in verdicts:
        if r["class"] != "NOT_STATED":
            err("class", f"{key(r)}: a {r['class']} line is outside this PR's scope (NOT_STATED only)")
        if key(r) in hold_keys or key(r) in {key(h) for h in holds}:
            err("held_line", f"{key(r)}: a held key is withheld")
        elif key(r) not in withhold:
            err("not_adjudicated", f"{key(r)}: the adjudication does not say withhold")
        if second.get(k3(r)) != "NOT_STATED":
            err("second_family", f"{key(r)}: the second family's class is {second.get(k3(r))}, not NOT_STATED")
    for k in sorted(withhold - have.keys()):
        err("line_dropped", f"{k}: a withhold line of the adjudication has no line in VALUE_VERDICTS.csv")
    for a in adj:  # the adjudication itself follows the rule: withhold only where both families read NOT_STATED and the line rests on the value's own record
        want = "withhold" if a["reader_class"] == "NOT_STATED" and second.get(k3(a)) == "NOT_STATED" and key(a) not in grain_keys else "hold"
        if a["action"] != want:
            err("adjudication", f"{key(a)}: action {a['action']}, the rule gives {want} (reader {a['reader_class']}, second family {second.get(k3(a))}, organization-row grain {key(a) in grain_keys})")
    with tempfile.TemporaryDirectory() as tmp:
        fresh_rows, problems, info = vb.generate(ROOT / "data", tasks_tree(tmp, verdicts, urls), store)
    for p in problems:
        err("generator", p)
    if problems:
        return bad
    fresh, head, base = {key(r): r for r in fresh_rows}, table(head_text), table(base_text)
    for name, other in (("head", head), ("base", base)):
        for k in sorted(other.keys() - fresh.keys()):
            err("extra_key", f"{name} table has {k} but generation does not")
        for k in sorted(fresh.keys() - other.keys()):
            err("dropped_key", f"{name} table lacks {k}")
    for k in sorted(head.keys() & fresh.keys()):
        if head[k] != fresh[k]:
            err("edited_row", f"data/value_basis.csv {k} is {head[k]['basis']}, generation gives {fresh[k]['basis']}")
    if not bad and vb.render(fresh_rows) != head_text:
        err("format", "data/value_basis.csv differs from a fresh generation in row order or formatting")
    moved = {k for k in fresh.keys() & base.keys() if fresh[k] != base[k]}
    at = {e["evidence_id"]: (e["record_table"], e["record_id"]) for e in vb.table_rows(ROOT / "data", "evidence")}
    for k in sorted(moved):
        if (base[k]["basis"], fresh[k]["basis"]) != ("not_yet_checked", vb.WITHHELD):
            err("basis_change", f"{k}: {base[k]['basis']} -> {fresh[k]['basis']}; only not_yet_checked -> {vb.WITHHELD} is allowed here")
        elif k[0] == "sites" and at.get(fresh[k]["evidence_id"]) != ("sites", k[1]):  # SCHEMA §4.24: a row on the organization gives a site's value at most not_yet_checked
            err("grain", f"{k}: withheld on {fresh[k]['evidence_id']}, which is not a row on the site itself")
    if Counter((k[0], k[2]) for k in moved) != Counter(EXPECT):
        err("counts", f"keys moved by (table, field) {dict(Counter((k[0], k[2]) for k in moved))}, expected {EXPECT} ({sum(EXPECT.values())} keys)")
    want = {key(r) for r in verdicts} - set(info["verdict_unbound"])
    if moved != want:
        err("scope", f"{len(moved ^ want)} keys differ between the keys the table moved and the keys of the lines that bind a page")
    if pack_lines is not None:
        for k in sorted(have.keys() - pack_lines.keys()):
            err("line_extra", f"{k}: a line the pack does not give")
        for k in sorted(have.keys() & pack_lines.keys()):
            if have[k] != pack_lines[k]:
                err("line_edited", f"{k}: the line differs from the pack's")
    return bad


def owner_counts(head_rows):
    """Owners of active tier A-C PIC-18 sites (organizations and ecosystem) that go from known to unknown, with the controller harness's definition
    (harness/pic18_unknown.py): known = the union of the owner's site tokens, else its own row's, less the keys now withheld. Unit: owners."""
    from regions import PIC18
    orgs, eco = {o["org_id"]: o for o in vb.table_rows(ROOT / "data", "organizations")}, {o["org_id"]: o for o in build.read(ROOT / "data/ecosystem.csv")}
    gt = {}
    for s in vb.table_rows(ROOT / "data", "sites"):
        if s["state"] == "OH" and s["county"] in PIC18 and s["operating_status"] == "active" and s["verification_tier"] in ("A", "B", "C"):
            gt.setdefault(s["org_id"], []).append(s)
    w = vb.withheld_keys(head_rows)

    def known(oid, field, drop):
        rec = orgs.get(oid) or eco.get(oid) or {}
        gone = lambda table, rid: {k[3] for k in drop if k[:3] == (table, rid, field)}
        return bool(set().union(*(set(vb.toks(s[field])) - gone("sites", s["site_id"]) for s in gt[oid])) or set(vb.toks(rec.get(field))) - gone("organizations", oid))
    sets = {"proc124": ([o for o in gt if (orgs.get(o) or {}).get("ring_primary") in ("1", "2", "4")], "processes"), "proc_all": (list(gt), "processes"), "mkt": (list(gt), "markets_served")}
    return {n: (sum(not known(o, f, set()) for o in os_), sum(not known(o, f, w) for o in os_), len(os_)) for n, (os_, f) in sets.items()}  # unknown before, after, owners


EXPECT_OWNERS = {"proc124": (204, 208, 601), "proc_all": (327, 331, 792), "mkt": (300, 301, 792)}  # (unknown before, unknown after, owners)


def main():
    store = Path(sys.argv[sys.argv.index("--store") + 1] if "--store" in sys.argv else os.environ.get("ATLAS_PAGE_STORE", "/nonexistent"))
    store = store if (store / "requote-all-2026-11-24/values.csv").exists() else None
    verdicts, holds, rejected = build.read(HERE / "VALUE_VERDICTS.csv"), build.read(HERE / "HOLDS.csv"), build.read(HERE / "REJECTED.csv")
    adj = build.read(HERE / "second-family/ADJUDICATION-hide.csv")
    urls = {r["page_sha256"]: (r["page_url"], r["requested_url"]) for r in build.read(HERE / "VALUE_PAGES.csv")}
    head_text = (ROOT / "data/value_basis.csv").read_text(encoding="utf-8")
    base_text = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE}:data/value_basis.csv"], capture_output=True, text=True, check=True).stdout
    if "--write-claims" in sys.argv:
        return build.write(HERE / "CLAIMS_CHECKED.csv", CLAIM_COLS, expected_claims(head_text, base_text, holds))
    second, unread = second_family(store, adj)
    pack = {key(r): r for r in build.read(store / "requote-all-2026-11-24/values.csv")} if store else None
    pack_lines = {k: r for k, r in pack.items() if k in {key(a) for a in adj if a["action"] == "withhold"}} if pack else None
    grain_keys = {key(a) for a in adj if GRAIN_REASON in a["reason"]}
    bad = []
    if len(adj) != 79 or Counter(a["action"] for a in adj) != Counter(withhold=len(verdicts), hold=EXPECT_HOLDS) or len(verdicts) != sum(EXPECT.values()):
        bad.append(("counts", f"{len(adj)} adjudication lines, {len(verdicts)} verdict lines, expected 79 = {sum(EXPECT.values())} withhold + {EXPECT_HOLDS} hold"))
    bad += frame_problems(adj, rejected, store)
    if build.read(HERE / "HOLDS.csv") != [{c: a[c] for c in build.HOLD_COLS} for a in adj if a["action"] == "hold"]:
        bad.append(("holds", "HOLDS.csv is not the adjudication's hold lines"))
    if store:  # the grain holds are the keys a NOT_STATED line would withhold on an organization row: tried, not assumed
        trial = [pack[k] for k in sorted({key(a) for a in adj if a["action"] == "hold" and a["reader_class"] == "NOT_STATED"})]  # every held line the re-read read NOT_STATED
        trial_urls = dict(urls)
        for r in trial:
            final, requested, _ = vb.manifest_index(store)[str((store / r["page_path"]).resolve())]
            trial_urls[r["page_sha256"]] = (final, requested if requested != final else "")
        with tempfile.TemporaryDirectory() as tmp:
            rows, problems, _ = vb.generate(ROOT / "data", tasks_tree(tmp, verdicts + trial, trial_urls), store)
        at = {e["evidence_id"]: (e["record_table"], e["record_id"]) for e in vb.table_rows(ROOT / "data", "evidence")}
        org_row = {key(r) for r in rows if r["basis"] == vb.WITHHELD and key(r) in {key(t) for t in trial} and r["record_table"] == "sites"
                   and at[r["evidence_id"]] != ("sites", r["record_id"])}
        if problems or org_row != grain_keys:
            bad.append(("grain_hold", f"the keys a NOT_STATED line would withhold on an organization row ({len(org_row)}) differ from the adjudication's grain holds ({len(grain_keys)}): {problems[:1]}"))
    bad += verify(verdicts, urls, head_text, base_text, store, adj, holds, second, grain_keys, pack_lines)
    claims = build.read(HERE / "CLAIMS_CHECKED.csv")
    bad += claims_problems(claims, head_text, base_text, holds)
    with open(HERE / "CLAIMS_CHECKED.csv", newline="", encoding="utf-8") as f:
        if next(csv.reader(f)) != CLAIM_COLS:
            bad.append(("claims", f"CLAIMS_CHECKED.csv header must be {','.join(CLAIM_COLS)}"))
    owners = owner_counts(list(table(head_text).values()))
    if owners != EXPECT_OWNERS:
        bad.append(("owners", f"owners unknown before, after, of (proc124, all-rings process, market): {owners}, expected {EXPECT_OWNERS}"))
    for line in (HERE / "INPUTS.sha256").read_text().splitlines():  # `persist/...` paths are in the controller's store, the rest in the repo
        digest, path = line.split("  ", 1)
        f = store / path.removeprefix("persist/") if path.startswith("persist/") and store else ROOT / path
        if path.startswith("persist/") and not store:
            print(f"NOT_INSPECTED input: {path}")
        elif not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != digest:
            bad.append(("inputs", f"{path}: missing or its sha256 differs from INPUTS.sha256"))
    for code, msg in bad:
        print(f"FAIL {code}: {msg}")
    print(f"real tree: {'FAIL' if bad else 'every rule held'}; {len(verdicts)} NOT_STATED lines, {len(holds)} holds, {len(rejected)} rejected, owners unknown before to after {owners}, "
          f"store {'read' if store else 'NOT_INSPECTED (manifest check, pack comparison, grain trial and the 2026-11-24 second-family reads skipped)'}")
    if unread:
        print(f"NOT_INSPECTED second-family reads (the 2026-11-24 rounds, in the store): {len(unread)} keys taken from the adjudication's own column")
    # planted defects: each is injected into a copy of the real inputs and must be rejected by the rule it names
    withhold_adj = [a for a in adj if a["action"] == "withhold"]
    hold_by = lambda text: next(a for a in adj if a["action"] == "hold" and text in a["reason"])
    base_args = dict(urls=urls, head_text=head_text, base_text=base_text, store=store, adj=adj, holds=holds, second=second, grain_keys=grain_keys, pack_lines=None)
    lines_for = lambda keys: [pack[k] for k in keys if k in pack] if pack else []

    def urls_for(extra):
        u = dict(urls)
        for r in extra:
            final, requested, _ = vb.manifest_index(store)[str((store / r["page_path"]).resolve())]
            u[r["page_sha256"]] = (final, requested if requested != final else "")
        return u
    blind = lines_for([key(hold_by("IMPLIED vs re-read NOT_STATED"))])  # a hold the second family disagreed on
    grain_line = lines_for(sorted(grain_keys))[:1]  # one of the organization-row site lines
    mutated = {**second, k3(withhold_adj[0]): "STATED"}
    rows = head_text.splitlines(keepends=True)
    i = next(n for n, line in enumerate(rows) if f",{vb.WITHHELD}," in line)
    edited = "".join(rows[:i] + [rows[i].replace(f",{vb.WITHHELD},", ",not_yet_checked,", 1)] + rows[i + 1:])
    dropped = "".join(rows[:i] + rows[i + 1:])
    plants = [  # (name, expected code, needs the store, verify() overrides)
        ("a hold line put back as NOT_STATED (a held key is withheld)", "held_line", True, dict(verdicts=verdicts + blind, urls=urls_for(blind))),
        ("one of the organization-row site lines put back", "grain", True, dict(verdicts=verdicts + grain_line, urls=urls_for(grain_line), adj=[dict(a, action="withhold") if key(a) in {key(g) for g in grain_line} else a for a in adj])),
        ("a withhold line dropped", "line_dropped", False, dict(verdicts=verdicts[1:])),
        ("an edited value_basis row", "edited_row", False, dict(verdicts=verdicts, head_text=edited)),
        ("a dropped value_basis key", "dropped_key", False, dict(verdicts=verdicts, head_text=dropped)),
        ("a withhold key whose second-family class is not NOT_STATED", "second_family", False, dict(verdicts=verdicts, second=mutated)),
        ("a verdict line whose class is STATED", "class", False, dict(verdicts=[dict(verdicts[0], **{"class": "STATED"})] + verdicts[1:])),
    ]
    failed = not store
    for name, code, needs_store, over in plants:
        if needs_store and not store:
            print(f"NOT_INSPECTED plant: {name} (needs the page store)")
            continue
        args = dict(base_args, **over)
        args["pack_lines"] = pack_lines if store else None
        got = verify(args.pop("verdicts"), args.pop("urls"), args.pop("head_text"), args.pop("base_text"), args.pop("store"), args.pop("adj"), args.pop("holds"), args.pop("second"), args.pop("grain_keys"), args.pop("pack_lines"))
        hit = [m for c, m in got if c == code]
        print(f"plant {'REJECTED' if hit else 'NOT REJECTED'}: {name} -> {hit[0][:170] if hit else got[:2]}")
        failed |= not hit
    for name, mutated_adj, mutated_rej in (("an adjudicated key also listed as rejected", adj, rejected[:-1] + [dict(rejected[-1], **{c: adj[0][c] for c in ("record_table", "record_id", "field", "value")})]),
                                           ("a rejected line dropped", adj, rejected[1:])):
        hit = [m for c, m in frame_problems(mutated_adj, mutated_rej, store) if c == "frame"]
        print(f"plant {'REJECTED' if hit else 'NOT REJECTED'}: {name} -> {hit[0][:130] if hit else ''}")
        failed |= not hit
    for name, mutated_claims in (("a dropped CLAIMS_CHECKED row", claims[1:]), ("a CLAIMS_CHECKED row with another bound row", [dict(claims[0], evidence_id="EVD-000000")] + claims[1:]),
                                 ("a held key claimed as withdrawn", [dict(c, verdict="withdrawn") if c is claims[-1] else c for c in claims])):
        hit = claims_problems(mutated_claims, head_text, base_text, holds)
        print(f"plant {'REJECTED' if hit else 'NOT REJECTED'}: {name} -> {hit[0][1][:120] if hit else ''}")
        failed |= not hit
    sys.exit(1 if bad or (failed and store) else 3 if failed or not store else 0)


if __name__ == "__main__":
    main()
