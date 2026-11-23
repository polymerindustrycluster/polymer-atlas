"""Shared helpers for the three 2026-11-22 consistency packets (entity-type, org-site, region). The same file sits in
each folder so a folder stands alone; keep the three byte-identical (check.py of each asserts nothing about the others).
Reuses scripts/derive_tier1.Shard (byte-exact CSV round trip) and scripts/regions.py (the one region definition)."""
import csv, io, os, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from derive_tier1 import Shard          # noqa: E402  byte-exact round trip; refuses a file that does not round-trip
from regions import PIC18, REGION       # noqa: E402

csv.field_size_limit(10 ** 9)
CHANGE_COLS = ["change_id", "frame", "table", "file", "record_id", "column", "before", "after", "rule", "basis"]


def base_ref():
    """The commit the packet was built on (BASE_REF, one line). Pinned so a later main does not move the check."""
    return (HERE / "BASE_REF").read_text().strip()


def export_tree(ref, dest):
    """data/ as it was at `ref`, extracted into dest/data (git archive, no working-tree dependence)."""
    dest = Path(dest); dest.mkdir(parents=True, exist_ok=True)
    p = subprocess.run(f"git -C {ROOT} archive {ref} data | tar -x -C {dest}", shell=True, capture_output=True)
    if p.returncode:
        raise SystemExit(f"cannot export data/ at {ref}: {p.stderr.decode()[:300]}")
    return dest / "data"


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def tagged(data, pattern):
    """[(file name, row dict)] over every shard matching pattern."""
    return [(p.name, r) for p in sorted(Path(data).glob(pattern)) for r in read_csv(p)]


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header, lineterminator="\n"); w.writeheader(); w.writerows(rows)


def split_vals(s):
    return [x.strip() for x in (s or "").split(";") if x.strip()]


def is_ohio_pic18(state, county):
    return state == "OH" and county in REGION


def apply_changes(data, changes, frames=None):
    """Write each change (before -> after) into data/. A cell whose current value is not `before` stops the run:
    that is the no-overwrite guarantee. Only shard files with changed rows are rewritten."""
    data = Path(data)
    by_file = {}
    for c in changes:
        if frames and c["frame"] not in frames:
            continue
        by_file.setdefault(c["file"], []).append(c)
    for fname, cs in by_file.items():
        sh = Shard(data / fname)
        idcol = sh.header[0]
        index = {row[0]: i for i, row in enumerate(sh.rows) if i}
        for c in cs:
            i = index.get(c["record_id"])
            if i is None:
                raise SystemExit(f"{fname}: {c['record_id']} not found")
            j = sh.col[c["column"]]
            if sh.rows[i][j] != c["before"]:
                raise SystemExit(f"{fname} {c['record_id']} {c['column']}: cell is {sh.rows[i][j]!r}, packet says before={c['before']!r}")
            sh.rows[i][j] = c["after"]
        (data / fname).write_bytes(sh.serialize())


def diff_trees(a, b):
    """({(file, id, column): (a, b)}, [structural problems]) between two data/ trees, cell by cell.
    Row or file additions and removals, and header changes, are reported as problems."""
    a, b = Path(a), Path(b); cells, bad = {}, []
    fa = {p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file()}
    fb = {p.relative_to(b).as_posix() for p in b.rglob("*") if p.is_file()}
    if fa != fb:
        bad.append(f"files differ: +{sorted(fb - fa)[:3]} -{sorted(fa - fb)[:3]}")
    for f in sorted(fa & fb):
        if (a / f).read_bytes() == (b / f).read_bytes() or not f.endswith(".csv"):
            if not f.endswith(".csv") and (a / f).read_bytes() != (b / f).read_bytes():
                bad.append(f"{f}: non-csv file changed")
            continue
        ra = list(csv.reader(open(a / f, newline="", encoding="utf-8")))
        rb = list(csv.reader(open(b / f, newline="", encoding="utf-8")))
        if ra[0] != rb[0] or len(ra) != len(rb):
            bad.append(f"{f}: header or row count changed ({len(ra)} -> {len(rb)})"); continue
        for x, y in zip(ra[1:], rb[1:]):
            if x[0] != y[0]:
                bad.append(f"{f}: row order or id changed at {x[0]}"); break
            for h, u, v in zip(ra[0], x, y):
                if u != v:
                    cells[(f, x[0], h)] = (u, v)
    return cells, bad


def run_validator(data):
    """(exit code, output lines) of scripts/validate.py on a data dir."""
    env = dict(os.environ, ATLAS_DATA_DIR=str(data))
    p = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py")], capture_output=True, text=True, env=env)
    return p.returncode, (p.stdout + p.stderr).splitlines()


def verify_cells(changes, expected, base_cells):
    """Errors when the packet's cells are not exactly what recomputation gives from the base rows.
    changes: packet rows. expected: {(file, id, column): after}. base_cells: {(file, id, column): base value}."""
    errs, seen = [], {}
    for c in changes:
        k = (c["file"], c["record_id"], c["column"])
        if k in seen:
            errs.append(f"duplicate change for {k}")
        seen[k] = c
        if k not in base_cells:
            errs.append(f"{k}: no such cell in the base tree"); continue
        if c["before"] != base_cells[k]:
            errs.append(f"{k}: before {c['before']!r} != base cell {base_cells[k]!r}")
        if k not in expected:
            errs.append(f"{k}: proposed but not produced by the rule (after={c['after']!r}, base={base_cells[k]!r})")
        elif c["after"] != expected[k]:
            errs.append(f"{k}: after {c['after']!r} != recomputed {expected[k]!r}")
    for k in expected:
        if k not in seen:
            errs.append(f"{k}: the rule produces it but the packet omits it")
    return errs


def verify_scratch(changes, base_data, frames=None):
    """Apply the packet to a scratch copy of the base tree and check: validator output identical to the base's (and
    exit 0); changed cells equal the packet exactly, in no other file or column; the validator really reads the scratch
    copy (a planted duplicate id there makes it fail). Returns (errors, info dict)."""
    errs, info = [], {}
    with tempfile.TemporaryDirectory(prefix="atlas-scratch-") as tmp:
        scratch = Path(tmp) / "data"; shutil.copytree(base_data, scratch)
        apply_changes(scratch, changes, frames)
        cells, bad = diff_trees(base_data, scratch)
        errs += bad
        want = {(c["file"], c["record_id"], c["column"]): (c["before"], c["after"]) for c in changes
                if not frames or c["frame"] in frames}
        if cells != want:
            errs.append(f"scratch diff != packet: {len(set(cells) ^ set(want))} cells differ")
        rc0, out0 = run_validator(base_data)
        rc1, out1 = run_validator(scratch)
        info.update(validator_base_rc=rc0, validator_scratch_rc=rc1, validator_lines=len(out1))
        if rc1 != 0:
            errs.append(f"validator fails on the scratch apply (rc {rc1}): {[l for l in out1 if 'ERROR' in l][:3]}")
        if sorted(out0) != sorted(out1):
            errs.append("validator output differs between base and scratch: "
                        f"{sorted(set(out1) ^ set(out0))[:4]}")
        # the validator must be reading the scratch dir: plant a duplicate org id there and expect a failure
        sh = Shard(next(scratch.glob("organizations_OH.csv")))
        sh.rows.append(list(sh.rows[1]))
        (scratch / "organizations_OH.csv").write_bytes(sh.serialize())
        rc2, _ = run_validator(scratch)
        info["validator_plant_rc"] = rc2
        if rc2 == 0:
            errs.append("validator passed on a planted duplicate id: it is not reading the scratch copy")
    return errs, info


def org_frame(org, org_sites):
    """'pic18' | 'ohio_rest' | 'outside': an organization is in the region when its HQ county, or the county of any
    non-closed Ohio site, is in REGION (scripts/regions.py); in Ohio-rest when only Ohio HQ/site counties fall outside it."""
    live = [s for s in org_sites if s["operating_status"] != "closed"]
    if is_ohio_pic18(org["hq_state"], org["hq_county"]) or any(is_ohio_pic18(s["state"], s["county"]) for s in live):
        return "pic18"
    if org["hq_state"] == "OH" or any(s["state"] == "OH" for s in live):
        return "ohio_rest"
    return "outside"


def sites_by_org(data):
    out = {}
    for _f, s in tagged(data, "sites_*.csv"):
        out.setdefault(s["org_id"], []).append(s)
    return out


def cell_lookup(data, keys):
    """{(file, id, column): value} for the requested keys, read from data/."""
    out = {}
    for f in {k[0] for k in keys}:
        for r in read_csv(Path(data) / f):
            idc = next(iter(r))
            for k in keys:
                if k[0] == f and k[1] == r[idc]:
                    out[k] = r[k[2]]
    return out


def check_main(recompute, plant_cols, known=None, independent=None):
    """The packet check. recompute(base_data) -> {(file, id, column): after} for every frame the packet may carry.
    plant_cols: [(file, column)] where a planted overwrite of a non-blank cell is tried. Exit 0 = pass.
      python3 check.py [--frames pic18 ohio_rest]   (default: every frame in changes.csv)"""
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--frames", nargs="*"); ap.add_argument("--skip-validator", action="store_true")
    a = ap.parse_args()
    errs = []
    with tempfile.TemporaryDirectory(prefix="atlas-base-") as tmp:
        base = export_tree(base_ref(), tmp)
        changes = read_csv(HERE / "changes.csv")
        frames = set(a.frames or {c["frame"] for c in changes})
        mine = [c for c in changes if c["frame"] in frames]
        expected = {k: v for k, v in recompute(base).items()}
        # recompute covers every frame the rule can reach; restrict to the packet's frames via its own rows' frame
        keys_frame = {(c["file"], c["record_id"], c["column"]): c["frame"] for c in changes}
        expected_here = {k: v for k, v in expected.items() if keys_frame.get(k) in frames or k not in keys_frame}
        bc = cell_lookup(base, set(expected_here) | {(c["file"], c["record_id"], c["column"]) for c in mine})
        errs += verify_cells(mine, expected_here, bc)
        print(f"recomputed {len(expected_here)} cells; packet carries {len(mine)} in frames {sorted(frames)}")
        # planted failures: each must be caught
        if mine:
            bad = [dict(c) for c in mine]; bad[0]["after"] = "PLANTED_WRONG"
            if not verify_cells(bad, expected_here, bc):
                errs.append("planted wrong value was NOT caught")
            if not verify_cells(mine[1:], expected_here, bc):
                errs.append("planted omission was NOT caught")
        for f, col in plant_cols:
            row = next((r for r in read_csv(base / f) if r[col].strip() not in ("", "unknown") and (f, r[next(iter(r))], col) not in expected_here), None)
            if row is None:
                errs.append(f"no non-blank {col} cell in {f} to plant an overwrite on"); continue
            k = (f, row[next(iter(row))], col)
            ow = mine + [dict(mine[0], file=f, record_id=k[1], column=col, before=row[col], after="PLANTED_OVERWRITE")]
            if not verify_cells(ow, expected_here, {**bc, k: row[col]}):
                errs.append(f"planted overwrite of non-blank {k} was NOT caught by the recompute")
            try:
                with tempfile.TemporaryDirectory() as t2:
                    sc = Path(t2) / "data"; shutil.copytree(base, sc)
                    apply_changes(sc, [dict(mine[0], file=f, record_id=k[1], column=col, before="", after="PLANTED_OVERWRITE", frame=mine[0]["frame"])])
                errs.append(f"apply wrote over non-blank {k} (a blank 'before' was accepted)")
            except SystemExit:
                pass
        for name, got, want in (known() if known else []):
            if got != want:
                errs.append(f"known answer {name}: got {got!r}, want {want!r}")
        if independent:   # a second derivation of the same claim, written without rules.py, over the packet and the base
            errs += independent(base, mine)
        if not a.skip_validator:
            e2, info = verify_scratch(changes, base, frames)
            errs += e2; print("scratch apply:", info)
        # the working tree: untouched, or exactly some whole frames of the packet applied
        cells, bad = diff_trees(base, ROOT / "data")
        if cells or bad:
            ok = False
            for fr in [{f} for f in sorted({c["frame"] for c in changes})] + [{c["frame"] for c in changes}]:
                want = {(c["file"], c["record_id"], c["column"]): (c["before"], c["after"]) for c in changes if c["frame"] in fr}
                ok |= (cells == want and not bad)
            if not ok:
                errs.append(f"working-tree data/ differs from base by {len(cells)} cells that are not a whole frame of this packet; {bad[:2]}")
        # no personal data in anything this folder ships
        import re
        pat = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b")
        for p in HERE.rglob("*.csv"):
            for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if pat.search(line):
                    errs.append(f"email/phone pattern at {p.relative_to(ROOT)}:{n}")
    print("PASS" if not errs else "FAIL")
    for e in errs[:40]:
        print("  -", e)
    return 1 if errs else 0
