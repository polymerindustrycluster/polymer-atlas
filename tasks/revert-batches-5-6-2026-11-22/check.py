#!/usr/bin/env python3
"""Check for PR revert-batches-5-6-2026-11-22. Run from the repo root:  python3 tasks/revert-batches-5-6-2026-11-22/check.py [--base origin/main]
Asserts: (1) every file under data/ and scripts/validate_debt_baseline.json is byte-identical to commit 4ee02127 (the tree before
batch 5), and the commits merged after 17834918 (batch 6's merge, up to --base) changed no data file or baseline; (2) the keyed rows
that left data/ since --base are exactly the keys of REMOVALS.csv, per table, and nothing was added or changed; (3) quarantine/ holds
every removed evidence row, registry link and archive link verbatim apart from the listed redactions (REDACTIONS.csv); (4)
first_cut_verdicts.csv has exactly one row per removed evidence id; (5) no non-role email address is left in quarantine/;
(6) docs/sources_registry.csv equals --base; (7) the PR touches only data/, the baseline, this folder, tasks/QUEUE.md, DECISIONS.md and that registry."""
import argparse, collections, csv, io, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(HERE))
import check_row_loss as crl
import gen
csv.field_size_limit(10**9)
PRE_BATCH5, BATCH6_MERGE = "4ee02127", "17834918"


def git(*a, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=check)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--base", default="origin/main"); a = ap.parse_args(); errs = []
    base = git("merge-base", a.base, "HEAD").stdout.strip()
    # (1) identical to the pre-batch-5 tree
    d = git("diff", "--name-status", PRE_BATCH5, "--", "data", "scripts/validate_debt_baseline.json").stdout.strip()
    if d:
        errs.append(f"data/ or baseline differs from {PRE_BATCH5}: {d.splitlines()[:5]}")
    later = git("log", "--format=%h %s", f"{BATCH6_MERGE}..{base}").stdout.strip().splitlines()
    if git("diff", "--name-only", BATCH6_MERGE, base, "--", "data", "scripts/validate_debt_baseline.json").stdout.strip():
        errs.append("a commit merged after batch 6 changed data/ or the baseline")
    # (2) removed keys == REMOVALS.csv
    declared = collections.defaultdict(set)
    for r in csv.DictReader(open(HERE / "REMOVALS.csv", newline="", encoding="utf-8")):
        declared[r["table"]].add(r["key"])
    bt, ht = crl.read_tree(base), crl.read_tree(None)
    gone = {t: bt[t] - ht.get(t, set()) for t in bt if bt[t] - ht.get(t, set())}
    added = {t: ht[t] - bt.get(t, set()) for t in ht if ht[t] - bt.get(t, set())}
    if added:
        errs.append(f"keys added: { {t: len(v) for t, v in added.items()} }")
    if {t: v for t, v in declared.items()} != gone:
        errs.append(f"REMOVALS.csv {({t: len(v) for t, v in declared.items()})} != removed keys {({t: len(v) for t, v in gone.items()})}")
    # (3) quarantine == removed rows, verbatim except redactions
    names = [n for n in git("ls-tree", "--name-only", f"{base}:data/").stdout.split() if n.endswith(".csv")]
    removed = {}                                    # (qfile, key) -> redacted base row
    for n in names:
        t = crl.table_of("data/" + n)
        if t not in gone:
            continue
        rows = list(csv.reader(io.StringIO(git("show", f"{base}:data/{n}").stdout)))
        for r in rows[1:]:
            k = crl.row_key(t, rows[0], r)
            if k in gone[t]:
                q = ("evidence_sites" if n.startswith("evidence_sites") else "evidence_organizations") if t == "evidence" else t
                removed[(q, k)] = [gen.redact(c)[0] for c in r]
    qrows = {}
    for q in ("evidence_sites", "evidence_organizations", "registry_links", "archive_links"):
        rows = list(csv.reader(open(HERE / "quarantine" / f"{q}.csv", newline="", encoding="utf-8")))
        t = "evidence" if q.startswith("evidence_") else q
        for r in rows[1:]:
            k = crl.row_key(t, rows[0], r)
            if (q, k) in qrows:
                errs.append(f"quarantine {q}: duplicate key {k}")
            qrows[(q, k)] = r
    if qrows != removed:
        errs.append(f"quarantine rows != removed rows: {len(qrows)} vs {len(removed)}; missing {len(set(removed) - set(qrows))}, extra {len(set(qrows) - set(removed))}, differing {sum(1 for k in set(qrows) & set(removed) if qrows[k] != removed[k])}")
    # (4) verdicts
    vids = [r["evidence_id"] for r in csv.DictReader(open(HERE / "quarantine/first_cut_verdicts.csv", newline="", encoding="utf-8"))]
    if sorted(vids) != sorted(gone.get("evidence", set())):
        errs.append(f"first_cut_verdicts.csv has {len(vids)} rows for {len(gone.get('evidence', set()))} removed evidence ids")
    # (5) emails
    em = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    markers = 0
    for f in sorted((HERE / "quarantine").glob("*.csv")):
        for ln, line in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
            markers += line.count("[REDACTED")
            for m in em.findall(line):
                if m.split("@")[0].lower() not in gen.ROLE:
                    errs.append(f"non-role email at {f.name}:{ln}")
    if markers != len(list(csv.DictReader(open(HERE / "REDACTIONS.csv", newline="", encoding="utf-8")))):
        errs.append("REDACTIONS.csv rows != redaction markers in quarantine/")
    # (6) registry, (7) touched paths
    if git("diff", "--name-only", base, "--", "docs/sources_registry.csv").stdout.strip():
        errs.append("docs/sources_registry.csv differs from base")
    ok = re.compile(r"data/.*|scripts/validate_debt_baseline\.json|tasks/revert-batches-5-6-2026-11-22/.*|tasks/QUEUE\.md|DECISIONS\.md")
    stray = [p for p in git("diff", "--name-only", base).stdout.split() if not ok.fullmatch(p)]
    if stray:
        errs.append(f"paths outside the expected set: {stray[:5]}")
    for e in errs:
        print("FAIL", e)
    if errs:
        return 1
    print(f"PASS: data/ and baseline identical to {PRE_BATCH5}; commits after {BATCH6_MERGE} up to {base[:8]} changed no data ({'; '.join(later)}); "
          f"removed keys {({t: len(v) for t, v in gone.items()})} = REMOVALS.csv = quarantine; {len(vids)} verdict rows; {markers} redaction markers; no non-role email")
    return 0


if __name__ == "__main__":
    sys.exit(main())
