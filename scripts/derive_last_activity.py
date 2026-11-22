#!/usr/bin/env python3
"""Derive sites.last_activity_date / last_activity_source (SCHEMA §4.5, v1.19).

The two columns are DERIVED fields: this script is their only writer.
It recomputes them from scratch on every run from dated government-filing
witness extracts, so a re-run after a fresh bulk pull refreshes the whole
population and a hand-edit never survives. Absence (both fields empty)
means "no dated witness in hand" — never "inactive" (§4.5).

Sources at v1.19 (the OSHA bulk pull of 2026-11-21):

- OSHA inspections (day-precise): the witness extract's
  `witness_date_latest` is the establishment's latest inspection date,
  used verbatim. Source label: `osha_inspection`.
- OSHA ITA Form 300A (year-precise): the extract's `witness_date_latest`
  is the establishment's latest filing YEAR. A year-precision witness
  contributes the filing year's period end — **Dec 31 of that year** —
  and the date means "activity witnessed during that calendar year",
  never "activity on that day" (the §4.5 convention, stated here so the
  number is never read at a precision the witness does not carry).
  Source label: `osha_ita`.

Only tier-A matches (name + street) feed the derivation: a derived
record field must not rest on a name/city-only match. Tier-B extract
rows are counted and reported, never applied.

When both sources cover a site, the later date wins; on an exact date
tie the day-precise source (`osha_inspection`) is named, because its
date is a witnessed day rather than a period end.

Usage:
  python3 scripts/derive_last_activity.py [--data-dir data]
      [--inspection ~/workspace/osha-pull/out/witness_extract_sites_inspection.csv]
      [--ita ~/workspace/osha-pull/out/witness_extract_sites_ita.csv]
"""
import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
YEAR_RE = re.compile(r"\d{4}")


def candidates(path: Path, kind: str):
    """Yield (site_id, date, source_label, day_precise) from one extract."""
    out = []
    tier_b = 0
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("match_tier") or "").strip() != "A":
                tier_b += 1
                continue
            sid = (r.get("record_id") or "").strip()
            w = (r.get("witness_date_latest") or "").strip()
            if kind == "inspection":
                if not DATE_RE.fullmatch(w):
                    raise SystemExit(f"{path}: inspection witness_date_latest {w!r} is not a date")
                out.append((sid, date.fromisoformat(w), "osha_inspection", True))
            else:  # ita — year precision, period-end convention
                if not YEAR_RE.fullmatch(w):
                    raise SystemExit(f"{path}: ITA witness_date_latest {w!r} is not a year")
                out.append((sid, date(int(w), 12, 31), "osha_ita", False))
    return out, tier_b


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default=str(ROOT / "data"))
    ap.add_argument("--inspection", default=str(Path.home() / "workspace/osha-pull/out/witness_extract_sites_inspection.csv"))
    ap.add_argument("--ita", default=str(Path.home() / "workspace/osha-pull/out/witness_extract_sites_ita.csv"))
    a = ap.parse_args()

    best = {}  # site_id -> (date, source_label, day_precise)
    stats = {}
    for path_s, kind in ((a.inspection, "inspection"), (a.ita, "ita")):
        cands, tier_b = candidates(Path(path_s), kind)
        stats[kind] = (len(cands), tier_b)
        for sid, d, label, precise in cands:
            cur = best.get(sid)
            if cur is None or (d, precise) > (cur[0], cur[2]):
                best[sid] = (d, label, precise)

    data = Path(a.data_dir)
    files = sorted(data.glob("sites_*.csv"))
    if not files:
        raise SystemExit(f"no sites shards under {data}")
    known = set()
    for fp in files:
        with open(fp, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                known.add(r["site_id"])
    unknown = sorted(set(best) - known)
    if unknown:
        raise SystemExit(f"extracts name {len(unknown)} site_ids not in the Atlas: {unknown[:5]}")

    written = 0
    for fp in files:
        raw = fp.read_bytes()
        assert raw.endswith(b"\n") and b"\r" not in raw, f"{fp}: unexpected line endings"
        lines = raw.decode("utf-8").split("\n")[:-1]
        assert lines[0].endswith(",last_activity_date,last_activity_source"), f"{fp}: v1.19 header missing"
        for i in range(1, len(lines)):
            head, _old_date, _old_src = lines[i].rsplit(",", 2)
            sid = lines[i].split(",", 1)[0]
            if sid in best:
                d, label, _precise = best[sid]
                lines[i] = f"{head},{d.isoformat()},{label}"
                written += 1
            else:
                lines[i] = f"{head},,"
        fp.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))

    by_source = {}
    for _sid, (_d, label, _p) in best.items():
        by_source[label] = by_source.get(label, 0) + 1
    print(f"inspection extract: {stats['inspection'][0]} tier-A rows used, {stats['inspection'][1]} tier-B rows excluded")
    print(f"ita extract:        {stats['ita'][0]} tier-A rows used, {stats['ita'][1]} tier-B rows excluded")
    print(f"sites populated:    {written} (of {len(known)} sites) — by source: "
          + ", ".join(f"{k} {v}" for k, v in sorted(by_source.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
