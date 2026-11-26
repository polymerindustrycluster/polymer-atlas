"""Named check for the 2026-11-26 re-read basis labels. Run: python3 -I tasks/reread-labels-2026-11-26/check.py [--store PERSIST_DIR]
PERSIST_DIR is the controller's page store (default: the 2026-11 atlas persist dir); without it the replay, the manifest and the
rebuild-from-the-pack checks are NOT_INSPECTED and the exit code is 3, never 0.

verify() regenerates the table from the repo's data and this folder's VALUE_VERDICTS.csv with scripts/value_basis.py and compares the WHOLE
data/value_basis.csv with the pinned base: same key set, same order and format, and the only differences are the keys of the labelled lines,
each not_yet_checked -> stated or implied. Nothing is withheld, every line is STATED or IMPLIED, and (with the store) every STATED quote
replays and the lines equal the pack's lines. Then each planted defect must be rejected by the rule it names."""
import csv, hashlib, io, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
import build  # noqa: E402
import value_basis as vb  # noqa: E402

BASE = "f921eba8d809acbba29dae22f1723a95e3cc82eb"  # origin/main after #573
STORE = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist")
MOVES = {("not_yet_checked", "stated"), ("not_yet_checked", "implied")}
key = lambda r: (r["record_table"], r["record_id"], r["field"], r["value"])


def table(text):
    return {key(r): r for r in csv.DictReader(io.StringIO(text))}


def tasks_tree(tmp, verdicts, urls):
    """A tasks/ tree with this folder's (possibly planted) files and the repo's proof files and READMEs the generator reads."""
    t = Path(tmp) / "tasks"
    for proof in (ROOT / "tasks").glob("*/BINDING_PROOF.csv"):
        (t / proof.parent.name).mkdir(parents=True)
        for f in (proof, proof.parent / "README.md"):
            if f.exists():
                (t / proof.parent.name / f.name).symlink_to(f)
    d = t / HERE.name
    d.mkdir()
    shutil.copy(HERE / "README.md", d)
    build.write(d / "VALUE_VERDICTS.csv", vb.VERDICT_COLS, verdicts)
    build.write(d / "VALUE_PAGES.csv", ["page_sha256", "page_url", "requested_url"], [{"page_sha256": s, "page_url": u, "requested_url": q} for s, (u, q) in urls.items()])
    return t


def verify(verdicts, urls, head_text, base_text, store, pack_lines):
    """-> [(code, message)]; empty means every rule held. Pure over its arguments so planted defects can be injected."""
    bad, err = [], lambda code, msg: bad.append((code, msg))
    for r in verdicts:
        if r["class"] not in ("STATED", "IMPLIED"):
            err("class", f"{key(r)}: a {r['class']} line is outside this PR's scope (labels only)")
    with tempfile.TemporaryDirectory() as tmp:
        fresh_rows, problems, info = vb.generate(ROOT / "data", tasks_tree(tmp, verdicts, urls), store)
    for p in problems:
        err("generator", p)
    if problems:
        return bad
    fresh, head, base = {key(r): r for r in fresh_rows}, table(head_text), table(base_text)
    for k in sorted(key(r) for r in fresh_rows if r["basis"] == vb.WITHHELD):
        err("withheld", f"{k}: this key would be withheld; hiding is a separate PR")
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
    for k in sorted(moved):
        if (base[k]["basis"], fresh[k]["basis"]) not in MOVES:
            err("basis_change", f"{k}: {base[k]['basis']} -> {fresh[k]['basis']}; only not_yet_checked -> stated or implied is allowed here")
    want = {key(r) for r in verdicts} - set(info["verdict_unbound"])
    if moved != want:
        err("scope", f"{len(moved ^ want)} keys differ between the keys the table moved and the keys of the lines that bind a page")
    if pack_lines is not None:
        have = {key(r): r for r in verdicts}
        for k in sorted(pack_lines.keys() - have.keys()):
            err("line_dropped", f"{k}: a pack STATED or IMPLIED line is missing from VALUE_VERDICTS.csv and not listed in HOLDS.csv")
        for k in sorted(have.keys() & pack_lines.keys()):
            if have[k] != pack_lines[k]:
                err("line_edited", f"{k}: the line differs from the pack's (after adjudication)")
        for k in sorted(have.keys() - pack_lines.keys()):
            err("line_extra", f"{k}: a line the pack does not give")
    return bad


def main():
    store = Path(sys.argv[sys.argv.index("--store") + 1]) if "--store" in sys.argv else STORE
    store = store if (store / "requote-all-2026-11-24/values.csv").exists() else None
    verdicts, holds = build.read(HERE / "VALUE_VERDICTS.csv"), build.read(HERE / "HOLDS.csv")
    urls = {r["page_sha256"]: (r["page_url"], r["requested_url"]) for r in build.read(HERE / "VALUE_PAGES.csv")}
    head_text = (ROOT / "data/value_basis.csv").read_text(encoding="utf-8")
    base_text = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE}:data/value_basis.csv"], capture_output=True, text=True, check=True).stdout
    pack = None
    if store:
        lines, _ = build.candidates(store / "requote-all-2026-11-24")
        held = {key(r) for r in holds}
        pack = {key(r): r for r in lines if key(r) not in held}
    bad = verify(verdicts, urls, head_text, base_text, store, pack)
    for line in (HERE / "INPUTS.sha256").read_text().splitlines():  # `persist/...` paths are in the controller's store, the rest in the repo
        digest, path = line.split("  ", 1)
        f = store / path.removeprefix("persist/") if path.startswith("persist/") and store else ROOT / path
        if path.startswith("persist/") and not store:
            print(f"NOT_INSPECTED input: {path}")
        elif not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != digest:
            bad.append(("inputs", f"{path}: missing or its sha256 differs from INPUTS.sha256"))
    for code, msg in bad:
        print(f"FAIL {code}: {msg}")
    print(f"real tree: {'FAIL' if bad else 'every rule held'}; {len(verdicts)} lines, {len(holds)} held out, store {'read' if store else 'NOT_INSPECTED (replay, manifest and pack comparison skipped)'}")
    # planted defects: each is injected into a copy of the real inputs and must be rejected by the rule it names
    stated = next(r for r in verdicts if r["class"] == "STATED" and key(r) not in {key(u) for u in build.read(HERE / "UNBOUND.csv")})
    moved_offset = [dict(r, offset=str(int(r["offset"]) + 1)) if r is stated else r for r in verdicts]
    not_stated = [dict(r, **{"class": "NOT_STATED", "quote": "", "offset": ""}) if r is stated else r for r in verdicts]
    elsewhere = dict(urls, **{stated["page_sha256"]: ("https://example.org/elsewhere", "")})
    rows = head_text.splitlines(keepends=True)
    i = next(n for n, line in enumerate(rows) if ",stated," in line)
    edited = "".join(rows[:i] + [rows[i].replace(",stated,", ",not_yet_checked,", 1)] + rows[i + 1:])
    dropped = "".join(rows[:i] + rows[i + 1:])
    plants = [  # (name, expected code, needs the page store, args)
        ("a NOT_STATED line slipped in (a withheld key appears)", "withheld", False, (not_stated, urls, head_text, store)),
        ("a STATED quote with a moved offset", "generator", True, (moved_offset, urls, head_text, store)),
        ("a line whose page is on no site a bound row cites", "generator", False, (verdicts, elsewhere, head_text, None)),
        ("an edited value_basis row", "edited_row", False, (verdicts, urls, edited, store)),
        ("a dropped value_basis key", "dropped_key", False, (verdicts, urls, dropped, store)),
        ("a dropped verdict line", "line_dropped", True, ([r for r in verdicts if r is not stated], urls, head_text, store)),
    ]
    failed = not store
    for name, code, needs_store, (vs, us, ht, st) in plants:
        if needs_store and not store:
            print(f"NOT_INSPECTED plant: {name} (needs the page store)")
            continue
        got = verify(vs, us, ht, base_text, st, pack if st else None)
        hit = [m for c, m in got if c == code]
        print(f"plant {'REJECTED' if hit else 'NOT REJECTED'}: {name} -> {hit[0][:160] if hit else got[:2]}")
        failed |= not hit
    sys.exit(1 if bad or (failed and store) else 3 if failed else 0)


if __name__ == "__main__":
    main()
