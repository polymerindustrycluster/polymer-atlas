#!/usr/bin/env python3
"""Row-loss guard: fail when a change removes any keyed row from data/ without declaring it.

Records are never deleted (AGENTS.md §3: tombstone instead) and evidence is append-only (SCHEMA §4.13), but
validate.py checks each row, not whether rows vanished. On 2026-11-04 a rebased wave commit (805528a) rewrote
data/registry_links.csv from a stale copy and dropped 3,351 links with every check green. This script compares the
keyed rows of every data table at a base ref against the working tree (or a second ref) and fails on any key that
disappeared, unless a REMOVALS.csv manifest anywhere under tasks/ lists it (columns: table,key,reason).

Keys: shards are unioned per table (organizations_*.csv and ecosystem.csv share the org-id space, because an org may
move between them); registry_links is keyed org_id|registry|registry_id|site_id; inclusion_log and
people_identifiers by the whole row; every other table by its first column.

Usage:
  python3 scripts/check_row_loss.py --base origin/main            # base ref vs working tree
  python3 scripts/check_row_loss.py --base 92393de --head 805528a # two refs (known-answer: 3,351 links)
"""
import argparse, csv, io, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WHOLE_ROW = {"inclusion_log", "people_identifiers"}


def table_of(path):
    name = Path(path).stem
    if name.startswith("evidence"):
        return "evidence"
    t = re.sub(r"_(?:[A-Z]{2}|INTL|US)$", "", name)
    return "org_ids" if t in ("organizations", "ecosystem") else t


def row_key(table, header, row):
    if table == "registry_links":
        d = dict(zip(header, row))
        return "|".join(d.get(c, "") for c in ("org_id", "registry", "registry_id", "site_id"))
    if table in WHOLE_ROW:
        return "|".join(row)
    return row[0]


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def read_tree(ref):
    """{table: set(keys)} for data/*.csv at a git ref, or the working tree when ref is None."""
    if ref is None:
        files = {str(p.relative_to(ROOT)): p.read_text(encoding="utf-8") for p in sorted((ROOT / "data").glob("*.csv"))}
    else:
        names = [n for n in git("ls-tree", "--name-only", f"{ref}:data/").split() if n.endswith(".csv")]
        files = {f"data/{n}": git("show", f"{ref}:data/{n}") for n in names}
    keys = defaultdict(set)
    for path, text in files.items():
        t = table_of(path)
        rows = list(csv.reader(io.StringIO(text)))
        if not rows:
            continue
        header = rows[0]
        for row in rows[1:]:
            if row:
                keys[t].add(row_key(t, header, row))
    return keys


def declared_removals(ref):
    """(table, key) pairs declared in any tasks/**/REMOVALS.csv at ref (or the working tree)."""
    out = set()
    if ref is None:
        texts = [p.read_text(encoding="utf-8") for p in (ROOT / "tasks").rglob("REMOVALS.csv")]
    else:
        texts = [git("show", f"{ref}:{p}") for p in git("ls-tree", "-r", "--name-only", ref, "tasks/").split()
                 if p.endswith("/REMOVALS.csv")]
    for text in texts:
        for r in csv.DictReader(io.StringIO(text)):
            out.add(((r.get("table") or "").strip(), (r.get("key") or "").strip()))
    return out


def removed_keys(base, head, allowed=frozenset()):
    """{table: [keys]} present in base, absent from head, and not in allowed {(table, key)}."""
    undeclared = defaultdict(list)
    for t, keys in base.items():
        for k in sorted(keys - head.get(t, set())):
            if (t, k) not in allowed:
                undeclared[t].append(k)
    return undeclared


def main():
    ap = argparse.ArgumentParser(description="Fail when keyed rows vanish from data/ without a REMOVALS.csv entry.")
    ap.add_argument("--base", required=True, help="git ref to compare against (e.g. origin/main)")
    ap.add_argument("--head", help="git ref for the new side (default: the working tree)")
    a = ap.parse_args()
    lost = removed_keys(read_tree(a.base), read_tree(a.head), declared_removals(a.head))
    if not lost:
        print(f"row-loss guard: OK — no keyed row removed from data/ since {a.base}")
        return 0
    total = sum(len(v) for v in lost.values())
    print(f"row-loss guard: FAIL — {total} keyed rows removed since {a.base} and not declared in a tasks/**/REMOVALS.csv")
    for t, ks in sorted(lost.items()):
        print(f"  {t}: {len(ks)} removed, e.g. {', '.join(ks[:5])}")
    print("If a removal is intended (a re-point, a merge), list each key in your task folder's REMOVALS.csv "
          "(columns table,key,reason). Records themselves are tombstoned, never deleted (AGENTS.md §3).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
