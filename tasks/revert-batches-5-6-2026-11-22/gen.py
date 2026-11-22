#!/usr/bin/env python3
"""Generate REMOVALS.csv, quarantine/ and COUNTS.csv from the diff between --base and the working tree (never by hand).
Usage (repo root):  python3 tasks/revert-batches-5-6-2026-11-22/gen.py --verdicts <binding-test verdicts.csv> [--base origin/main]
A removed row is a keyed row of data/evidence_*.csv, registry_links.csv or archive_links.csv present at the base and absent now
(keys as scripts/check_row_loss.py). The generator asserts nothing was added or changed. quarantine/ holds (a) evidence_leads.csv:
one row per removed evidence id, with NO free text (claim_detail and notes are dropped), plus the first-cut verdict columns, and (b)
registry_links.csv and archive_links.csv verbatim (no column holds free text: match_basis is a three-value code, archive_ref a
web.archive.org URL). The dropped text stays recoverable from commit 17834918 by evidence_id."""
import argparse, collections, csv, io, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_row_loss import table_of, row_key  # noqa: E402
csv.field_size_limit(10**9)

csv.field_size_limit(10**9)

LEAD_COLS = ["evidence_id", "record_table", "record_id", "claim_type", "source_class", "source_ref", "observed_date", "tier_effect",
             "created_by", "address_role"]
VERDICT_COLS = ["source", "verdict", "name_class", "street_class", "path", "line"]
DROPPED = ["claim_detail", "notes"]


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--verdicts", required=True); ap.add_argument("--base", default="origin/main"); a = ap.parse_args()
    base = git("merge-base", a.base, "HEAD").strip()
    names = [n for n in git("ls-tree", "--name-only", f"{base}:data/").split() if n.endswith(".csv")]
    removed = collections.defaultdict(list)     # table -> [(row dict, key, shard)]
    hdrs = {}
    for n in names:
        t = table_of("data/" + n)
        if t not in ("evidence", "registry_links", "archive_links"):
            continue
        btxt = git("show", f"{base}:data/{n}")
        htxt = (ROOT / "data" / n).read_text(encoding="utf-8")
        if btxt == htxt:
            continue
        brows = list(csv.reader(io.StringIO(btxt))); hrows = list(csv.reader(io.StringIO(htxt)))
        hdr = brows[0]; assert hrows[0] == hdr
        hdrs.setdefault(t, hdr); assert hdrs[t] == hdr
        bk = {}; hk = {}
        for r in brows[1:]:
            k = row_key(t, hdr, r); assert k not in bk, (n, k); bk[k] = r
        for r in hrows[1:]:
            k = row_key(t, hdr, r); assert k not in hk, (n, k); hk[k] = r
        assert not set(hk) - set(bk), f"{n}: rows added"
        assert all(bk[k] == hk[k] for k in hk), f"{n}: rows changed"
        for k in bk:
            if k not in hk:
                removed[t].append((dict(zip(hdr, bk[k])), k, n))
    out = HERE / "quarantine"; out.mkdir(exist_ok=True)
    counts = []
    with open(HERE / "REMOVALS.csv", "w", newline="", encoding="utf-8") as rf:
        rw = csv.writer(rf, lineterminator="\n"); rw.writerow(["table", "key", "reason"])
        for t in ("evidence", "registry_links", "archive_links"):
            for d, k, n in removed[t]:
                who = f"created_by {d['created_by']}" if d.get("created_by") else f"registry {d.get('registry')}"
                rw.writerow([t, k, f"batches 5 and 6 reverted, owner ruling 2026-11-22; {who}"])
    for t in ("registry_links", "archive_links"):
        with open(out / f"{t}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=hdrs[t], lineterminator="\n"); w.writeheader()
            for d, k, n in sorted(removed[t], key=lambda x: (x[2], )):
                w.writerow(d)
    eids = {k for d, k, n in removed["evidence"]}
    with open(a.verdicts, newline="", encoding="utf-8") as f:
        vmap = {}
        for r in csv.DictReader(f):
            if r["evidence_id"] in eids:
                assert r["evidence_id"] not in vmap; vmap[r["evidence_id"]] = r
    assert set(vmap) == eids, (len(vmap), len(eids))
    with open(out / "evidence_leads.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(LEAD_COLS + VERDICT_COLS)
        for d, k, n in sorted(removed["evidence"], key=lambda x: x[1]):
            v = vmap[k]
            for c in ("record_table", "record_id", "claim_type", "tier_effect", "created_by"):
                assert v[c] == d[c], (k, c)                       # the verdict file describes the same row
            w.writerow([d[c] for c in LEAD_COLS] + [v[c] for c in VERDICT_COLS])
    for k, v in sorted(collections.Counter(d["created_by"] for d, _k, _n in removed["evidence"]).items()):
        counts.append(["evidence rows", "created_by", k, v])
    for k, v in sorted(collections.Counter(d["registry"] for d, _k, _n in removed["registry_links"]).items()):
        counts.append(["registry_links rows", "registry", k, v])
    counts.append(["archive_links rows", "all", "", len(removed["archive_links"])])
    with open(HERE / "COUNTS.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(["unit", "filter", "value", "rows"]); w.writerows(counts)
    print(f"removed: { {t: len(v) for t, v in removed.items()} }; leads {len(eids)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
