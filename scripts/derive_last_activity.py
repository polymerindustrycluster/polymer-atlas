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
record field must not rest on a name/city-only match. The extract's own
`match_tier` is NOT trusted for the street leg (the 2026-11-21 harness
built tier A from name + city + state with no street test): an extract
row is applied to a site only when `same_street()` says the extract's
`street_as_printed` is the site's `street_address`: equal, non-empty
`atlas.street_key` values with a civic number (the repo's one street normaliser), and no
conflicting suite or unit. A site with a blank street_address gets no derived date. Tier-B rows and rows
that fail the street test are counted and reported, never applied.
Owner ruling 2026-11-22, "Fix script, re-derive".

When both sources cover a site, the later date wins; on an exact date
tie the day-precise source (`osha_inspection`) is named, because its
date is a witnessed day rather than a period end.

Usage:
  python3 scripts/derive_last_activity.py [--data-dir data]
      [--inspection tasks/last-activity-street-leg-2026-11-22/inputs/witness_extract_sites_inspection.csv]
      [--ita tasks/last-activity-street-leg-2026-11-22/inputs/witness_extract_sites_ita.csv]
"""
import argparse
import csv
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atlas import street_key  # noqa: E402  (stdlib-only module, no import side effects)

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "tasks/last-activity-street-leg-2026-11-22/inputs"
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
YEAR_RE = re.compile(r"\d{4}")

# ---- street test ----------------------------------------------------------------------------------------
_UNIT = re.compile(r"\b(?:suite|ste|unit|apt|apartment|room|rm)\b\.?\s*#?\s*([a-z0-9-]+)|(?<=\S)\s*#\s*([a-z0-9-]+)", re.I)
_NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"}


def _units(street: str) -> set:
    """Suite / unit designators a street string states (`Suite 100`, `Ste. 5`, `Unit B`, `Apt 2`, `Rm 7`, a non-leading `#12`)."""
    return {re.sub(r"[^a-z0-9]", "", (g1 or g2).lower()) for g1, g2 in _UNIT.findall(street or "")} - {""}


def has_civic_number(key: str) -> bool:
    """A civic number in a street key: a token containing a digit, or a leading number word (one to ten); not a PO box in any spelling (PO Box, P.O. Box, P O Box, POB, P.O.B., Post Office Box)."""
    toks = key.split()
    if re.search(r"\b(?:p ?o ?b(?:ox)?|post ?office ?box)(?=[\s\d]|$)", key):
        return False                                                    # a PO box is not a civic address
    return any(re.search(r"\d", t) for t in toks) or bool(toks) and toks[0] in _NUMBER_WORDS


def same_street(site_street: str, printed: str) -> bool:
    """The extract's street is the site's street: both `atlas.street_key` values are equal, non-empty, and carry a civic
    number plus at least one more token (a bare number cannot witness a street). `street_key` discards suites, so when
    the record and the extract both state a suite or unit and they differ, the row is not applied. A blank street is
    never equal. No second normaliser lives here: variants the key misses are rejected, not guessed."""
    key = street_key(site_street)
    if not key or key != street_key(printed) or not has_civic_number(key) or len(key.split()) < 2:
        return False
    ua, ub = _units(site_street), _units(printed)
    return not (ua and ub and ua != ub)


# ---- derivation ----------------------------------------------------------------------------------------
def load_streets(files):
    """site_id -> street_address over every sites shard."""
    out = {}
    for fp in files:
        with open(fp, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                out[r["site_id"]] = r["street_address"]
    return out


def candidates(path: Path, kind: str, streets: dict):
    """-> (applied [(site_id, date, source_label, day_precise)], rejected [(site_id, kind, printed)], tier_b).
    A tier-A row is applied only when same_street() holds."""
    applied, rejected, tier_b = [], [], 0
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
                d, label, precise = date.fromisoformat(w), "osha_inspection", True
            else:  # ita — year precision, period-end convention
                if not YEAR_RE.fullmatch(w):
                    raise SystemExit(f"{path}: ITA witness_date_latest {w!r} is not a year")
                d, label, precise = date(int(w), 12, 31), "osha_ita", False
            if sid not in streets:
                raise SystemExit(f"{path}: extract names site_id {sid} not in the Atlas")
            if same_street(streets[sid], r.get("street_as_printed") or ""):
                applied.append((sid, d, label, precise))
            else:
                rejected.append((sid, kind, r.get("street_as_printed") or ""))
    return applied, rejected, tier_b


def derive(data: Path, inspection: Path, ita: Path):
    """-> (best {site_id: (date, label, precise)}, stats, rejected rows, shard files, streets)."""
    files = sorted(data.glob("sites_*.csv"))
    if not files:
        raise SystemExit(f"no sites shards under {data}")
    streets = load_streets(files)
    best, stats, rejected = {}, {}, []
    for path, kind in ((inspection, "inspection"), (ita, "ita")):
        applied, rej, tier_b = candidates(Path(path), kind, streets)
        stats[kind] = (len(applied), tier_b, len(rej))
        rejected += rej
        for sid, d, label, precise in applied:
            cur = best.get(sid)
            if cur is None or (d, precise) > (cur[0], cur[2]):
                best[sid] = (d, label, precise)
    return best, stats, rejected, files, streets


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default=str(ROOT / "data"))
    ap.add_argument("--inspection", default=str(INPUTS / "witness_extract_sites_inspection.csv"))
    ap.add_argument("--ita", default=str(INPUTS / "witness_extract_sites_ita.csv"))
    a = ap.parse_args()

    best, stats, rejected, files, streets = derive(Path(a.data_dir), Path(a.inspection), Path(a.ita))
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

    by_source = Counter(label for _d, label, _p in best.values())
    for kind in ("inspection", "ita"):
        n, tier_b, rej = stats[kind]
        print(f"{kind + ' extract:':<19} {n} tier-A rows applied, {rej} tier-A rows failed the street test, {tier_b} tier-B rows excluded")
    print(f"sites populated:    {written} (of {len(streets)} sites) — by source: "
          + ", ".join(f"{k} {v}" for k, v in sorted(by_source.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
