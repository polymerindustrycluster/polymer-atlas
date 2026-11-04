#!/usr/bin/env python3
"""Evidence repair round 2 (scope rows), prep step. Joins the lane inputs to today's evidence rows and writes:
- checked.csv: the weak population, in build_repair.py's format (claim_type and tier_effect from data, check and
  check_detail from the deterministic audit verdict that queued each row);
- replacements.csv: every lane outcome, with column `raw` from the integrator's raw re-fetch (FOUND and
  CONTRADICTED rows; NONE_FOUND rows get raw "n/a").

    python3 tasks/evidence-repair-2-2026-11-04/prep.py --data-dir data
"""
import argparse, csv, re, sys, unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, r"C:\Users\JohnSwanson\Documents\pic-github\polymer-faculty-census")
W = lambda s: re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower())


def read(p):
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write(p, rows, fields):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n", extrasaction="ignore"); w.writeheader(); w.writerows(rows)


def found(u, q, cache={}):
    from tools.layer_b_fetch import call, env
    fc, key = env("FIRECRAWL_BASE_URL").rstrip("/"), env("FIRECRAWL_NAS_API_KEY")
    q, seen = W(q), False
    for main in (True, False):
        if (u, main) not in cache:
            try:
                r = call(f"{fc}/v2/scrape", {"url": u, "formats": ["markdown"], "onlyMainContent": main},
                         {"Authorization": f"Bearer {key}"}, timeout=150)
                d = r.get("data") or {}
                cache[(u, main)] = W(d.get("markdown")) if (d.get("metadata") or {}).get("statusCode") == 200 else None
            except Exception:
                cache[(u, main)] = None
        p = cache[(u, main)]
        if p:
            seen = True
            if q and any(p[i:i + len(q)] == q for i in range(len(p) - len(q) + 1)):
                return "yes"
    return "no" if seen else "unfetchable"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    a = ap.parse_args()
    ev = {r["evidence_id"]: r for f in sorted(Path(a.data_dir).glob("evidence*.csv")) for r in read(f)}
    checked, repl = [], []
    for i in (1, 2, 3):
        for r in read(HERE / "lanes" / f"S{i}_input.csv"):
            e = ev[r["evidence_id"]]  # KeyError = the queued row is gone from data: stop, do not guess
            checked.append({**e, "check": r["verdict"], "check_detail": r["reason"]})
        outs = read(HERE / "lanes" / f"S{i}_out.csv")
        assert len(outs) == len(read(HERE / "lanes" / f"S{i}_input.csv")), f"lane S{i}: outputs != inputs"
        for r in outs:
            r["raw"] = found(r["source_url"].strip(), r["quote"]) if r["outcome"] in ("FOUND", "CONTRADICTED") and r["source_url"].startswith("http") else "n/a"
            repl.append(r)
    assert len({r["evidence_id"] for r in checked}) == len(checked), "duplicate queued evidence ids"
    write(HERE / "checked.csv", checked, list(checked[0].keys()))
    write(HERE / "replacements.csv", repl, ["evidence_id", "outcome", "source_class", "source_url", "quote", "note", "raw"])
    from collections import Counter
    print(len(checked), "queued;", Counter((r["outcome"], r["raw"]) for r in repl))


if __name__ == "__main__":
    main()
