#!/usr/bin/env python3
"""Check for PR revert-batches-5-6-2026-11-22. Run from the repo root:  python3 tasks/revert-batches-5-6-2026-11-22/check.py [--base origin/main]
Asserts: (1) every file under data/ and scripts/validate_debt_baseline.json is byte-identical to commit 4ee02127 (the tree before
batch 5), and the commits merged after 17834918 (batch 6's merge, up to --base) changed no data file or baseline; (2) the keyed rows
that left data/ since --base are exactly the keys of REMOVALS.csv, per table, and nothing was added or changed; (3) quarantine/ holds
every removed registry link and archive link verbatim; (4) quarantine/evidence_leads.csv has exactly the removed evidence ids, the
fixed columns and no claim_detail or notes; (5) no email, phone pattern or account URL (scripts/check_account_urls.py's logic) in this folder;
(6) docs/sources_registry.csv equals --base; (7) the PR touches only data/, the baseline, this folder, tasks/QUEUE.md, DECISIONS.md, README.md (inventory paragraph) and the
id allocator (scripts/atlas.py, its caller build_integration_sets.py, test_atlas_cli.py)."""
import argparse, collections, csv, io, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(HERE))
import check_row_loss as crl
import gen
import check_account_urls  # noqa: F401
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
    names = [n for n in git("ls-tree", "--name-only", f"{base}:data/").stdout.split() if n.endswith(".csv")]
    # (3) registry_links / archive_links quarantine == removed rows, verbatim
    removed = {}                                    # (table, key) -> row
    leads_src = {}                                  # evidence_id -> removed evidence row dict
    for n in names:
        t = crl.table_of("data/" + n)
        if t not in gone:
            continue
        rows = list(csv.reader(io.StringIO(git("show", f"{base}:data/{n}").stdout)))
        for r in rows[1:]:
            k = crl.row_key(t, rows[0], r)
            if k in gone[t]:
                removed[(t, k)] = r
                if t == "evidence":
                    leads_src[k] = dict(zip(rows[0], r))
    for t in ("registry_links", "archive_links"):
        rows = list(csv.reader(open(HERE / "quarantine" / f"{t}.csv", newline="", encoding="utf-8")))
        got = {crl.row_key(t, rows[0], r): r for r in rows[1:]}
        want_t = {k: r for (tt, k), r in removed.items() if tt == t}
        if got != want_t or len(got) != len(rows) - 1:
            errs.append(f"quarantine/{t}.csv != removed {t} rows ({len(got)} vs {len(want_t)})")
    # (4) the leads file: exactly the removed evidence ids, no free text columns
    with open(HERE / "quarantine/evidence_leads.csv", newline="", encoding="utf-8") as f:
        lr = csv.DictReader(f); lcols = lr.fieldnames; leads = list(lr)
    if lcols != gen.LEAD_COLS + gen.VERDICT_COLS:
        errs.append(f"leads columns {lcols}")
    if set(lcols) & set(gen.DROPPED) or any(c in lcols for c in ("claim_detail", "notes")):
        errs.append("leads file carries a dropped free-text column")
    ids = [r["evidence_id"] for r in leads]
    if sorted(ids) != sorted(gone.get("evidence", set())) or len(set(ids)) != len(ids):
        errs.append(f"leads ids ({len(ids)}) != removed evidence ids ({len(gone.get('evidence', set()))})")
    bad = [r["evidence_id"] for r in leads if r["evidence_id"] in leads_src and any(r[c] != leads_src[r["evidence_id"]][c] for c in gen.LEAD_COLS)]
    if bad:
        errs.append(f"{len(bad)} leads rows differ from the removed row in a kept column, e.g. {bad[:3]}")
    # (5) no email, no phone, no account URL anywhere in this folder
    import check_account_urls as cau
    em = re.compile(r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    ph = re.compile(r"(?<!\d)(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)")
    for f in sorted(HERE.rglob("*")):
        if not f.is_file() or f.suffix not in (".csv", ".md"):
            continue
        raw = f.read_bytes()
        for ln in cau.findings(cau.read(raw)):
            errs.append(f"account URL at {f.relative_to(HERE)}:{ln}")
        for ln, line in enumerate(raw.decode("utf-8").split("\n"), 1):
            if em.search(line) or ph.search(line):
                errs.append(f"email or phone pattern at {f.relative_to(HERE)}:{ln}")
    # (6) registry, (7) touched paths
    if git("diff", "--name-only", base, "--", "docs/sources_registry.csv").stdout.strip():
        errs.append("docs/sources_registry.csv differs from base")
    ok = re.compile(r"data/.*|scripts/validate_debt_baseline\.json|tasks/revert-batches-5-6-2026-11-22/.*|tasks/QUEUE\.md|DECISIONS\.md|README\.md|scripts/atlas\.py|scripts/build_integration_sets\.py|scripts/test_atlas_cli\.py")
    stray = [p for p in git("diff", "--name-only", base).stdout.split() if not ok.fullmatch(p)]
    if stray:
        errs.append(f"paths outside the expected set: {stray[:5]}")
    for e in errs:
        print("FAIL", e)
    if errs:
        return 1
    print(f"PASS: data/ and baseline identical to {PRE_BATCH5}; commits after {BATCH6_MERGE} up to {base[:8]} changed no data ({'; '.join(later)}); "
          f"removed keys {({t: len(v) for t, v in gone.items()})} = REMOVALS.csv = quarantine; {len(ids)} lead rows; no email, phone or account URL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
