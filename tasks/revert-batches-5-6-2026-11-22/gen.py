#!/usr/bin/env python3
"""Generate REMOVALS.csv, quarantine/ and COUNTS.csv from the diff between --base and the working tree (never by hand).
Usage (repo root):  python3 tasks/revert-batches-5-6-2026-11-22/gen.py --verdicts <binding-test verdicts.csv> [--base origin/main]
A removed row is a keyed row of data/evidence_*.csv, registry_links.csv or archive_links.csv present at the base and absent now
(keys as scripts/check_row_loss.py). The generator asserts nothing was added or changed. Quarantine rows are verbatim, except
(a) a non-role email address and (b) a person's name after ATTN/ATTENTION, each replaced by a marker (AGENTS section 6); every
replacement is listed in REDACTIONS.csv by path:line."""
import argparse, collections, csv, io, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_row_loss import table_of, row_key  # noqa: E402
csv.field_size_limit(10**9)

QTABLE = {"evidence": None, "registry_links": "registry_links", "archive_links": "archive_links"}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
ROLE = {"info", "sales", "contact", "support", "admin", "hr", "office", "service", "services", "customerservice", "orders",
        "webmaster", "marketing", "hello", "enquiries", "inquiries", "quotes", "quote", "purchasing", "accounting", "careers",
        "jobs", "general", "mail", "team", "help", "press", "billing", "rfq", "customercare", "reception", "estimating"}
ATTN = re.compile(r"(?i)\b(ATTN|ATTENTION):?(\s+)(?!(?:TAX|CORPORATE|PROPERTY|RETURNS|ACCOUNTS?|PURCHASING|LEGAL|PAYABLE)\b)([A-Za-z.'-]+\s+[A-Za-z.'-]+)(?=\s+\d|\s+[A-Z]{2,}\s)")


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout


def redact(cell):
    kinds = []
    def e(m):
        if m.group(0).split("@")[0].lower() in ROLE:
            return m.group(0)
        kinds.append("email"); return "[REDACTED: email address]"
    cell = EMAIL.sub(e, cell)
    def a(m):
        kinds.append("attn-name"); return f"{m.group(1)}:{m.group(2)}[REDACTED NAME]"
    return ATTN.sub(a, cell), kinds


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--verdicts", required=True); ap.add_argument("--base", default="origin/main"); a = ap.parse_args()
    base = git("merge-base", a.base, "HEAD").strip()
    names = [n for n in git("ls-tree", "--name-only", f"{base}:data/").split() if n.endswith(".csv")]
    removed = collections.defaultdict(list)     # qtable -> [(shard, base line no, raw line, parsed row, key, header)]
    for n in names:
        t = table_of("data/" + n)
        if t not in QTABLE:
            continue
        btxt = git("show", f"{base}:data/{n}")
        htxt = (ROOT / "data" / n).read_text(encoding="utf-8")
        if btxt == htxt:
            continue
        blines = btxt.split("\n")[:-1]; brows = list(csv.reader(io.StringIO(btxt)))
        assert len(blines) == len(brows), f"{n}: embedded newlines; line-based quarantine unsafe"
        hdr = brows[0]; hrows = list(csv.reader(io.StringIO(htxt)))
        assert hrows[0] == hdr
        bk = {}; hk = {}
        for i, r in enumerate(brows[1:], 2):
            k = row_key(t, hdr, r); assert k not in bk, (n, k); bk[k] = (i, r)
        for r in hrows[1:]:
            k = row_key(t, hdr, r); assert k not in hk, (n, k); hk[k] = r
        assert not set(hk) - set(bk), f"{n}: rows added"
        assert all(bk[k][1] == hk[k] for k in hk), f"{n}: rows changed"
        for k in sorted(set(bk) - set(hk), key=lambda k: bk[k][0]):
            i, r = bk[k]
            removed[t].append((n, i, blines[i - 1], r, k, hdr))
    out = HERE / "quarantine"; out.mkdir(exist_ok=True)
    counts, redactions = [], []
    with open(HERE / "REMOVALS.csv", "w", newline="", encoding="utf-8") as rf:
        rw = csv.writer(rf, lineterminator="\n"); rw.writerow(["table", "key", "reason"])
        for t in ("evidence", "registry_links", "archive_links"):
            rows = removed[t]
            hdrs = {tuple(x[5]) for x in rows}; assert len(hdrs) == 1, hdrs
            hdr = list(hdrs.pop())
            qname = {"evidence": "evidence_removed.csv"}.get(t, f"{t}.csv")
            # evidence is split by record table, as the data is: sites and organizations
            groups = collections.defaultdict(list)
            for x in rows:
                groups[("evidence_" + ("sites" if x[0].startswith("evidence_sites") else "organizations") if t == "evidence" else t)].append(x)
            for g, xs in sorted(groups.items()):
                with open(out / f"{g}.csv", "w", newline="", encoding="utf-8") as qf:
                    qw = csv.writer(qf, lineterminator="\n"); qw.writerow(hdr)
                    for n_, (shard, ln, raw, row, key, _h) in enumerate(xs, 2):
                        new = []
                        for j, c in enumerate(row):
                            c2, kinds = redact(c)
                            new.extend((k, hdr[j]) for k in kinds); row = row[:j] + [c2] + row[j + 1:]
                        for k, col in new:
                            redactions.append([f"tasks/revert-batches-5-6-2026-11-22/quarantine/{g}.csv", n_, f"data/{shard}", ln, key, col, k])
                        qw.writerow(row)
            for shard, ln, raw, row, key, _h in rows:
                d = dict(zip(hdr, row))
                why = d.get("created_by") or f"registry {d.get('registry')}"
                rw.writerow([t, key, f"batches 5 and 6 reverted, owner ruling 2026-11-22; {'created_by ' if d.get('created_by') else ''}{why}"])
            if t == "evidence":
                for k, v in sorted(collections.Counter(dict(zip(hdr, x[3]))["created_by"] for x in rows).items()):
                    counts.append(["evidence rows", "created_by", k, v])
            elif t == "registry_links":
                for k, v in sorted(collections.Counter(x[3][1] for x in rows).items()):
                    counts.append(["registry_links rows", "registry", k, v])
            else:
                counts.append(["archive_links rows", "all", "", len(rows)])
    with open(HERE / "COUNTS.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(["unit", "filter", "value", "rows"]); w.writerows(counts)
    with open(HERE / "REDACTIONS.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(["quarantine_path", "quarantine_line", "original_path", "original_line", "evidence_id_or_key", "column", "kind"]); w.writerows(redactions)
    # first-cut verdicts, keyed by evidence_id, verbatim columns, only for removed evidence rows
    eids = {x[4] for x in removed["evidence"]}
    with open(a.verdicts, newline="", encoding="utf-8") as f:
        vr = csv.DictReader(f); vh = vr.fieldnames; vrows = [r for r in vr if r["evidence_id"] in eids]
    with open(out / "first_cut_verdicts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=vh, lineterminator="\n"); w.writeheader(); w.writerows(vrows)
    print(f"removed: {dict((t, len(v)) for t, v in removed.items())}; verdict rows for removed evidence {len(vrows)} of {len(eids)}; redactions {len(redactions)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
