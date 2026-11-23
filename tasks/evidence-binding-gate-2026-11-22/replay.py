#!/usr/bin/env python3
"""Replay the gate over the last 40 first-parent commits to main before the branch cut (8f30ce0f).

For each commit that added or changed evidence rows: rows PASS / FAIL / HELD / READ_REQUIRED / UNINSPECTABLE; how
many rows were held (HELD, READ_REQUIRED or UNINSPECTABLE: this gate has no admission path for them) and how many of
those had a data/archive_links.csv capture at that commit; and whether the binding gate (--new-since: fails on any FAIL or held row)
and the provenance rules (--provenance-since) would have passed. Provenance is presence only, as in the gate (a label
naming exactly one folder, a non-empty check.py, a new label adding its own folder); nothing is executed. Writes
replay.csv beside itself. Takes about 5 minutes.

Usage: python3 tasks/evidence-binding-gate-2026-11-22/replay.py
"""
import csv
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
import check_evidence_binding as b  # noqa: E402

MAIN, N = "8f30ce0f", 40


def main():
    commits = b.git("log", "--first-parent", "--format=%H %s", "-n", str(N), MAIN).splitlines()
    assert len(commits) == N, f"read {len(commits)} of {N} commits"
    out = []
    for line in commits:
        h, subj = line.split(" ", 1)
        new = b.changed_rows(b.rows(h + "^1", "evidence_*.csv"), b.rows(h, "evidence_*.csv"))
        if not new:
            continue
        res = b.judge_all(new, b.Index.load(h))
        v = Counter(r["verdict"] for r in res)
        unins = {r["evidence_id"] for r in res if r["verdict"] not in ("PASS", "FAIL")}
        archive = {r["evidence_id"]: r["archive_ref"] for r in b.rows(h, "archive_links.csv")}
        paths = set(b.git("ls-tree", "-r", "--name-only", h, "tasks/").split())
        base_paths = set(b.git("ls-tree", "-r", "--name-only", h + "^1", "tasks/").split())
        base_labels = {e["created_by"].strip() for e in b.rows(h + "^1", "evidence_*.csv")}
        prov = b.provenance_problems(
            new, base_labels, lambda f: any(x.startswith(f"tasks/{f}/") for x in base_paths),
            lambda f: (b.tasks_file(h, f"tasks/{f}/check.py") or b"").strip() if f"tasks/{f}/check.py" in paths else b"")
        out.append({"commit": h[:9], "subject": subj[:60], "rows": len(new), "PASS": v["PASS"], "FAIL": v["FAIL"],
                    "HELD": v["HELD"], "READ_REQUIRED": v["READ_REQUIRED"], "UNINSPECTABLE": v["UNINSPECTABLE"],
                    "held": len(unins),
                    "of_which_archive_link": len(unins & set(archive)),
                    "labels": len({e["created_by"].strip() for e in new}), "provenance_problems": len(prov),
                    "binding_gate": "fail" if v["FAIL"] or unins else "pass",
                    "provenance": "fail" if prov else "pass"})
        print(" ".join(f"{k}={x}" for k, x in out[-1].items()), flush=True)
    with open(HERE / "replay.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} of {N} commits added or changed evidence rows; binding gate would pass "
          f"{sum(r['binding_gate'] == 'pass' for r in out)}, provenance {sum(r['provenance'] == 'pass' for r in out)}")


if __name__ == "__main__":
    sys.exit(main())
