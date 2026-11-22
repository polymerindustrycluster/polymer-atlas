#!/usr/bin/env python3
"""Replay the gate over the last 40 first-parent commits to main before the branch cut (8f30ce0f).

For each commit that added or re-pointed evidence rows: rows PASS / FAIL / UNINSPECTABLE; how many rows would have
needed a per-row proof line (every UNINSPECTABLE row) and how many of those had a data/archive_links.csv capture at
that commit; and whether the binding gate (--new-since) and the provenance check (--provenance-since) would have
passed. Writes replay.csv beside itself. Takes about 5 minutes.

Usage: python3 tasks/evidence-binding-gate-2026-11-22/replay.py
"""
import csv
import subprocess
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
        unins = {r["evidence_id"] for r in res if r["verdict"] == "UNINSPECTABLE"}
        archive = {r["evidence_id"]: r["archive_ref"] for r in b.rows(h, "archive_links.csv")}
        paths = set(b.git("ls-tree", "-r", "--name-only", h, "tasks/").split())
        prov = b.provenance_missing(new, lambda t: f"tasks/{t}/check.py" in paths)
        proofs = b.check_proofs(res, {e["evidence_id"]: e for e in new}, archive,
                                lambda p: b.tasks_file(h, p) if p in paths else None)
        out.append({"commit": h[:9], "subject": subj[:60], "rows": len(new), "PASS": v["PASS"], "FAIL": v["FAIL"],
                    "UNINSPECTABLE": v["UNINSPECTABLE"], "needs_proof_line": len(unins),
                    "of_which_archive_link": len(unins & set(archive)),
                    "labels": len({e["created_by"].strip() for e in new}), "labels_without_check_py": len(prov),
                    "proof_file_present": "no" if any("no tasks/<folder>" in x for x in proofs) else
                    ("n/a" if not unins else "yes"),
                    "binding_gate": "fail" if v["FAIL"] or proofs else "pass",
                    "provenance": "fail" if prov else "pass"})
        print(" ".join(f"{k}={x}" for k, x in out[-1].items()), flush=True)
    with open(HERE / "replay.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} of {N} commits added or re-pointed evidence rows; binding gate would pass "
          f"{sum(r['binding_gate'] == 'pass' for r in out)}, provenance {sum(r['provenance'] == 'pass' for r in out)}")


if __name__ == "__main__":
    sys.exit(main())
