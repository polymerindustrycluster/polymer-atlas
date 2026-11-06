#!/usr/bin/env python3
"""Row-loss guard: fail when a change removes any keyed row from data/ without declaring it.

Records are never deleted (AGENTS.md §3: tombstone instead) and evidence is append-only (SCHEMA §4.13), but
validate.py checks each row, not whether rows vanished. On 2026-11-04 a rebased wave commit (805528a) rewrote
data/registry_links.csv from a stale copy and dropped 3,351 links with every check green. This script compares the
keyed rows of every data table at a base ref against the working tree (or a second ref) and fails on any key that
disappeared, unless a REMOVALS.csv manifest anywhere under tasks/ lists it (columns: table,key,reason).

Keys: shards are unioned per table (organizations_*.csv and ecosystem.csv share the org-id space, because an org may
move between them); tracked files outside data/ are checked by path (table "file", key = the path), so a merge that
deletes scripts or task folders fails too; registry_links is keyed org_id|registry|registry_id|site_id; people_identifiers
person_id|identifier_type|identifier_id (SCHEMA §4.21 grain, so an as_of refresh is not a loss); inclusion_log by the
whole row plus its occurrence number (identical rows are counted, not collapsed); every other table by its first column.

The base side is the merge-base of --base and the head, so a branch (or a PR merge ref) that lags main is not blamed
for rows main added since. A removal is allowed only by a REMOVALS.csv row that is new in the compared range (present
at the head, absent at the merge-base): a manifest from an earlier change cannot authorize a later, unrelated loss.

Usage:
  python3 scripts/check_row_loss.py --base origin/main            # base ref vs working tree
  python3 scripts/check_row_loss.py --base 92393de --head 805528a # two refs (known-answer: 3,351 links)
  python3 scripts/check_row_loss.py --base <before-sha> --literal  # push events: judge against the replaced commit
"""
import argparse, csv, io, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WHOLE_ROW = {"inclusion_log"}
COMPOSITE = {
    "registry_links": ("org_id", "registry", "registry_id", "site_id"),
    "people_identifiers": ("person_id", "identifier_type", "identifier_id"),
}


def table_of(path):
    name = Path(path).stem
    if name.startswith("evidence"):
        return "evidence"
    t = re.sub(r"_(?:[A-Z]{2}|INTL|US)$", "", name)
    return "org_ids" if t in ("organizations", "ecosystem") else t


def row_key(table, header, row):
    if table in COMPOSITE:
        d = dict(zip(header, row))
        return "|".join(d.get(c, "") for c in COMPOSITE[table])
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
        seen = defaultdict(int)
        for row in rows[1:]:
            if row:
                k = row_key(t, header, row)
                if t in WHOLE_ROW:  # count duplicates so removing one of several identical rows is seen
                    seen[k] += 1
                    k = f"{k}#{seen[k]}"
                keys[t].add(k)
    return keys


def declared_removals(ref):
    """{(manifest_path, table, key)} declared in tasks/**/REMOVALS.csv at ref (or the working tree)."""
    out = set()
    if ref is None:
        texts = [(str(p.relative_to(ROOT)), p.read_text(encoding="utf-8")) for p in (ROOT / "tasks").rglob("REMOVALS.csv")]
    else:
        texts = [(p, git("show", f"{ref}:{p}")) for p in git("ls-tree", "-r", "--name-only", ref, "tasks/").split()
                 if p.endswith("/REMOVALS.csv")]
    for path, text in texts:
        for r in csv.DictReader(io.StringIO(text)):
            out.add((path, (r.get("table") or "").strip(), (r.get("key") or "").strip()))
    return out


def tracked_files(ref):
    """Tracked file paths at ref, or (working tree) every tracked path that still exists on disk."""
    if ref is None:
        return {p for p in git("ls-files").split("\n") if p and (ROOT / p).exists()}
    return set(git("ls-tree", "-r", "--name-only", ref).split())


def removed_files(base, head, allowed=frozenset()):
    """Tracked files outside data/ present at base and gone at head, not declared as ("file", path)."""
    return sorted(p for p in base - head if not p.startswith("data/") and ("file", p) not in allowed)


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
    ap.add_argument("--literal", action="store_true",
                    help="compare --base itself, not its merge-base with the head (push events: a rollback or "
                         "non-fast-forward update must be judged against the commit it replaced)")
    a = ap.parse_args()
    base = git("rev-parse", a.base).strip() if a.literal else git("merge-base", a.base, a.head or "HEAD").strip()
    # a declaration counts only if its (manifest file, table, key) row is new in this range: an untouched old manifest
    # cannot authorize a later loss, but re-declaring a key in a new manifest file can
    allowed = {(t, k) for _, t, k in declared_removals(a.head) - declared_removals(base)}
    lost = removed_keys(read_tree(base), read_tree(a.head), allowed)
    gone = removed_files(tracked_files(base), tracked_files(a.head), allowed)
    if gone:  # a stale-tree merge can delete scripts and task folders while data/ looks intact (#163, 43326cd)
        lost["file"] = gone
    if not lost:
        print(f"row-loss guard: OK — no keyed row removed from data/ since {a.base} (merge-base {base[:10]})")
        return 0
    total = sum(len(v) for v in lost.values())
    print(f"row-loss guard: FAIL — {total} keyed rows removed since {a.base} (merge-base {base[:10]}) and not declared "
          "in a REMOVALS.csv added in this change")
    for t, ks in sorted(lost.items()):
        print(f"  {t}: {len(ks)} removed, e.g. {', '.join(ks[:5])}")
    print("If a removal is intended (a re-point, a merge), list each key in a REMOVALS.csv in your task folder "
          "(columns table,key,reason); for inclusion_log the key is the whole row plus '#<occurrence>'. Records themselves are tombstoned, never deleted (AGENTS.md §3).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
