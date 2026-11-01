#!/usr/bin/env python3
"""Apply the P1 private-source scrub packet (owner ruling 2026-11-01, SCHEMA v1.7.6 P1).

Reads the packet's ``edits.csv`` (default packet directory: ``tasks/p1-<token>-scrub-2026-11-01``) and applies each edit
(file, row id, column, old-value hash -> new value) to a data directory, in place,
preserving header order, row order, line endings and CSV quoting style (the
files round-trip byte-for-byte through Python's csv module, which the script
verifies before it touches anything).

This is INTEGRATOR work (AGENTS.md section 2 rule 7: lanes never edit data/).
The script refuses to run against the repository's real ``data/`` directory
unless ``--i-am-the-integrator`` is passed. Point ``--data-dir`` at a temp copy
to rehearse:

    cp -r data /tmp/atlas_p1 && python3 scripts/apply_p1_crm_scrub.py --data-dir /tmp/atlas_p1
    ATLAS_DATA_DIR=/tmp/atlas_p1 python3 scripts/validate.py

Safety properties
  * all-or-nothing: every edit is validated (row exists, column exists, sha256 of
    the current cell == the packet's ``old_sha256``) against the in-memory files
    before any file is written; one mismatch aborts the run with nothing changed.
    The packet deliberately carries only a hash of each old value, so the packet
    itself republishes none of the text it removes;
  * only the files that carry edits are rewritten;
  * edits to ``sources`` must leave at least one entry; ``description_1line``
    must stay non-empty and <= 180 characters; tiers/bands must stay in their
    vocabularies; no new value may contain the banned token;
  * a post-run census proves how many case-insensitive whole-word occurrences of
    the banned token remain in any column of any CSV in the data directory
    (target: 0).

Derived fields are NOT touched. After applying the band edits the integrator
must re-run the tier1_qualifier derivation (AGENTS.md section 1); the script
prints how many organizations changed band across the 250-employee line.
Evidence rows and ID allocation are likewise the integrator's (no new IDs are
minted here).

Stdlib only.
"""
import argparse
import collections
import csv
import hashlib
import io
import os
import re
import sys
import tempfile
from pathlib import Path

csv.field_size_limit(10 ** 9)

# the banned token is assembled so this source file does not itself contain it
BANNED = "C" + "R" + "M"
ROOT = Path(__file__).resolve().parent.parent
REAL_DATA = (ROOT / "data").resolve()
DEFAULT_PACKET = ROOT / "tasks" / ("p1-" + BANNED.lower() + "-scrub-2026-11-01")
BANNED_RE = re.compile(r"\b" + BANNED + r"\b", re.I)
TIERS = {"A", "B", "C", "U"}
BANDS = {"", "1-9", "10-49", "50-99", "100-249", "250-499", "500-999", "1000-4999", "5000+", "unknown"}
BIG = {"250-499", "500-999", "1000-4999", "5000+"}


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


class Table:
    """One CSV file held in memory with exact round-trip."""

    def __init__(self, path):
        self.path = path
        raw = path.read_bytes()
        txt = raw.decode("utf-8")
        self.nl = "\r\n" if "\r\n" in txt else "\n"
        self.rows = list(csv.reader(io.StringIO(txt, newline="")))
        if self.serialize() != raw:
            die(f"{path.name}: does not round-trip byte-for-byte through csv; refusing to rewrite it")
        self.header = self.rows[0]
        self.col = {c: i for i, c in enumerate(self.header)}
        self.index = {}
        for n, r in enumerate(self.rows[1:], 1):
            self.index.setdefault(r[0], []).append(n)
        self.dirty = False

    def serialize(self):
        out = io.StringIO(newline="")
        csv.writer(out, lineterminator=self.nl).writerows(self.rows)
        return out.getvalue().encode("utf-8")


def read_edits(packet_dir):
    p = packet_dir / "edits.csv"
    if not p.exists():
        die(f"packet file not found: {p}")
    with open(p, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    need = {"file", "row_id", "column", "old_sha256", "new_value", "edit_class", "rationale"}
    if not rows or not need <= set(rows[0]):
        die(f"{p} lacks required columns {sorted(need)}")
    return rows


def check_new_value(e):
    col, new = e["column"], e["new_value"]
    if BANNED_RE.search(new):
        return "new value still contains the banned token"
    if col == "sources" and not new.strip():
        return "sources would be empty (>=1 source required)"
    if col == "description_1line" and (not new.strip() or len(new) > 180):
        return f"description_1line must be non-empty and <=180 chars (got {len(new)})"
    if col == "verification_tier" and new not in TIERS:
        return f"tier {new!r} outside A/B/C/U"
    if col == "employee_band_ohio" and new not in BANDS:
        return f"band {new!r} outside the SCHEMA 4.4 vocabulary"
    return None


def census(data_dir):
    tok = collections.Counter()
    sub = collections.Counter()
    for p in sorted(data_dir.glob("*.csv")):
        with open(p, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                for cell in r:
                    if cell:
                        n = len(BANNED_RE.findall(cell))
                        if n:
                            tok[p.name] += n
                        if re.search(BANNED, cell, re.I) and not n:
                            sub[p.name] += 1
    return tok, sub


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data-dir", required=True, help="directory holding the data CSVs (a temp copy to rehearse)")
    ap.add_argument("--packet-dir", default=str(DEFAULT_PACKET), help="packet directory holding edits.csv")
    ap.add_argument("--i-am-the-integrator", action="store_true",
                    help="required to run against the real data/ directory (integrator of record only)")
    ap.add_argument("--skip-tier-drop", action="store_true",
                    help="do not apply the TIER_DROP edits (text, source and band edits still apply)")
    ap.add_argument("--check", action="store_true", help="validate every edit and report, but write nothing")
    args = ap.parse_args()

    data_dir = Path(args.data_dir).resolve()
    if not data_dir.is_dir():
        die(f"--data-dir {data_dir} is not a directory")
    if data_dir == REAL_DATA and not args.i_am_the_integrator:
        die("refusing to edit the real data/ directory: lanes never edit data/ (AGENTS.md section 2 rule 7). "
            "Only the integrator of record may pass --i-am-the-integrator; otherwise use a temp copy.")
    if args.i_am_the_integrator and data_dir == REAL_DATA:
        print("NOTE: --i-am-the-integrator given; editing the real data/ directory.")

    edits = read_edits(Path(args.packet_dir))
    if args.skip_tier_drop:
        edits = [e for e in edits if e["edit_class"] != "TIER_DROP"]

    # ---- load every file that carries edits
    tables = {}
    errors = []
    seen = set()
    for e in edits:
        fn = e["file"]
        if fn not in tables:
            p = data_dir / fn
            if not p.exists():
                errors.append(f"{fn}: file not found in {data_dir}")
                tables[fn] = None
                continue
            tables[fn] = Table(p)
    if errors:
        die("; ".join(errors))

    # ---- validate all edits before writing anything
    plan = []
    for e in edits:
        t = tables[e["file"]]
        key = (e["file"], e["row_id"], e["column"])
        if key in seen:
            errors.append(f"duplicate edit for {key}")
            continue
        seen.add(key)
        if e["column"] not in t.col:
            errors.append(f"{key}: column not in header")
            continue
        hits = t.index.get(e["row_id"], [])
        if len(hits) != 1:
            errors.append(f"{key}: expected exactly one row with that id in {e['file']}, found {len(hits)}")
            continue
        n = hits[0]
        cur = t.rows[n][t.col[e["column"]]]
        if hashlib.sha256(cur.encode("utf-8")).hexdigest() != e["old_sha256"]:
            errors.append(f"{key}: current cell hash differs from the packet's old_sha256 (data drifted since the packet was built)")
            continue
        bad = check_new_value(e)
        if bad:
            errors.append(f"{key}: {bad}")
            continue
        plan.append((t, n, e, cur))
    if errors:
        print(f"{len(errors)} validation error(s); nothing was written:", file=sys.stderr)
        for m in errors[:40]:
            print("  -", m, file=sys.stderr)
        if len(errors) > 40:
            print(f"  ... and {len(errors) - 40} more", file=sys.stderr)
        sys.exit(1)

    # ---- apply in memory
    by_class = collections.Counter()
    by_file = collections.Counter()
    rows_changed = set()
    band_cleared = band_replaced = 0
    tier_moves = collections.Counter()
    crossed_up = crossed_down = 0
    for t, n, e, cur in plan:
        ci = t.col[e["column"]]
        t.rows[n][ci] = e["new_value"]
        t.dirty = True
        by_class[e["edit_class"]] += 1
        by_file[e["file"]] += 1
        rows_changed.add((e["file"], e["row_id"]))
        if e["column"] == "employee_band_ohio":
            if e["new_value"] == "":
                band_cleared += 1
            else:
                band_replaced += 1
            if cur in BIG and e["new_value"] not in BIG:
                crossed_down += 1
            if cur not in BIG and e["new_value"] in BIG:
                crossed_up += 1
        if e["column"] == "verification_tier":
            tier_moves[f"{cur}->{e['new_value']}"] += 1

    # ---- write (all files are staged to temp names, then moved into place)
    if not args.check:
        staged = []
        try:
            for fn, t in tables.items():
                if not t.dirty:
                    continue
                fd, tmp = tempfile.mkstemp(prefix=fn + ".", suffix=".tmp", dir=str(data_dir))
                with os.fdopen(fd, "wb") as fh:
                    fh.write(t.serialize())
                staged.append((tmp, data_dir / fn))
            for tmp, dest in staged:
                os.replace(tmp, dest)
        finally:
            for tmp, _ in staged:
                if os.path.exists(tmp):
                    os.unlink(tmp)

    # ---- summary
    mode = "CHECK ONLY (nothing written)" if args.check else "APPLIED"
    print(f"== apply_p1_scrub: {mode} in {data_dir}")
    print(f"edits: {len(plan)} across {len(rows_changed)} rows in {len(by_file)} files")
    for c, n in sorted(by_class.items()):
        print(f"  edit_class {c}: {n}")
    for f, n in sorted(by_file.items()):
        print(f"  file {f}: {n}")
    print(f"employee_band_ohio: {band_replaced} set to a public band, {band_cleared} cleared "
          f"(value edits only; a public band equal to the current value needs no value edit)")
    print(f"organizations crossing the 250-employee line: {crossed_down} drop below, {crossed_up} rise above "
          f"(re-run the tier1_qualifier derivation; never hand-edit it)")
    if tier_moves:
        print("verification_tier moves: " + ", ".join(f"{k}: {v}" for k, v in sorted(tier_moves.items())))
    if not args.check:
        tok, sub = census(data_dir)
        total = sum(tok.values())
        print(f"census (case-insensitive whole-word banned token, all columns, all CSVs in the directory): {total} remaining")
        for f, n in sorted(tok.items()):
            print(f"  {f}: {n}")
        if sub:
            print(f"note: {sum(sub.values())} cells contain the letters only inside an identifier (e.g. TRIFID values); not tokens, left untouched")
        print("next: re-run the tier1_qualifier derivation; run scripts/validate.py; shrink the V-50 entries in "
              "scripts/validate_debt_baseline.json; add evidence rows/IDs through the integrator route.")
        if total:
            sys.exit(3)


if __name__ == "__main__":
    main()
