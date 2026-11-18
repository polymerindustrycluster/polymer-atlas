"""Add IPEDS completions years the Urban Institute API does not serve correctly, straight from NCES complete data files.

Urban never serves C2023_A (see FINDING below), but NCES publishes it. Urban RECODES award levels
(bachelor's = 7, master's = 9, research doctorate = 22), so NCES AWLEVEL codes cannot be copied across. The mapping
is DERIVED, not assumed: NCES C2022_A rows are matched to the Urban 2022 rows already in raw_ipeds_national.json on
(unitid, cip, awards), and each NCES code must map to exactly one Urban code before any new year is added.
Rows written here carry the NCES file year (C2024_A -> 2024). ipeds_build.py moves them back one, onto the
fall-of-academic-year labels the rest of the series uses.

Run order: scripts/ipeds_fetch.py -> scripts/ipeds_fetch_nces.py -> scripts/ipeds_build.py
No contact address is sent (the User-Agent is generic).
"""
import csv
import io
import json
import os
import urllib.request
import zipfile
from collections import Counter, defaultdict

from fetch_ipeds_national import CIP, AWARD

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "ipeds", "raw_ipeds_national.json")
CACHE = os.path.join(ROOT, ".cache", "nces")  # NCES complete data files, ~80 MB, re-downloadable; gitignored
UA = {"User-Agent": "PIC-polymer-programs/1.0"}
# FINDING 2026-10-14 (the evidence-room's ipeds_mirror_fix.py found it first, 2026-08-31): Urban labels a year by the
# FALL of the academic year (Urban 2018 = C2019_A, Urban 2023 = C2024_A, 390/390 rows), except that Urban 2020 repeats
# C2020_A and Urban 2021-2022 serve C2021_A-C2022_A a year late. C2023_A (2022-23) is served nowhere. The calibration
# uses 2022, where Urban and NCES hold the same file; C2023_A and C2024_A come from NCES, and Urban's 2023 rows are
# dropped and used as a cross-check on mapped C2024_A. All relabelling is in ipeds_build.py.
CALIBRATION_YEAR = 2022
NEW_YEARS = [2023, 2024]
URBAN_LABEL_FOR = {2024: 2023}  # NCES C2024_A must reproduce Urban's (fall-labelled) 2023 rows
MIN_VOTES = 5


def nces_rows(year):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"C{year}_A.zip")
    if not os.path.exists(path):
        with urllib.request.urlopen(urllib.request.Request(
                f"https://nces.ed.gov/ipeds/datacenter/data/C{year}_A.zip", headers=UA), timeout=300) as r:
            data = r.read()
        with open(path, "wb") as f:
            f.write(data)
    with zipfile.ZipFile(path) as z:
        name = sorted(n for n in z.namelist() if n.lower().endswith(".csv"))[-1]  # *_rv.csv (revised) sorts last
        text = z.read(name).decode("utf-8-sig", errors="replace")
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        row = {k.strip().upper(): (v or "").strip() for k, v in row.items()}
        cip = row.get("CIPCODE", "").replace(".", "")
        if cip in CIP and row.get("MAJORNUM", "1") == "1":
            out.append((int(row["UNITID"]), cip, int(row["AWLEVEL"]), int(row.get("CTOTALT") or 0)))
    return out, name


def main():
    raw = json.load(open(RAW, encoding="utf-8"))
    # Pair rows only where the award COUNT is unique inside one (unitid, cip) group on BOTH sides; a count shared by
    # two award levels (e.g. 3 master's and 3 doctorates) cannot say which code is which.
    urban = defaultdict(list)
    for r in raw["rows"]:
        if r["year"] == CALIBRATION_YEAR:
            urban[(r["unitid"], r["cip"])].append((r["award_level"], r["awards"]))
    cal, cal_file = nces_rows(CALIBRATION_YEAR)
    nces = defaultdict(list)
    for unitid, cip, awlevel, total in cal:
        nces[(unitid, cip)].append((awlevel, total))
    votes = defaultdict(Counter)
    for key, n_rows in nces.items():
        u_rows = urban.get(key, [])
        u_counts, n_counts = Counter(a for _, a in u_rows), Counter(t for _, t in n_rows)
        for awlevel, total in n_rows:
            if total > 0 and n_counts[total] == 1 and u_counts[total] == 1:
                votes[awlevel][next(c for c, a in u_rows if a == total)] += 1
    mapping, problems, thin = {}, [], {}
    for awlevel, counter in sorted(votes.items()):
        top, n = counter.most_common(1)[0]
        if len(counter) > 1 and counter.most_common(2)[1][1] * 4 > n:  # a real competitor, not stray coincidence
            problems.append(f"NCES {awlevel}: ambiguous {dict(counter)}")
        if n < MIN_VOTES:  # a few coincidental count matches are not a mapping on their own
            thin[awlevel] = n
        mapping[awlevel] = top
    print(f"calibration {cal_file}: {len(cal)} NCES rows; derived NCES->Urban award map {mapping}")
    if problems:
        raise SystemExit("refusing to add years; award mapping is ambiguous: " + "; ".join(problems))
    # Urban's rows for a year NCES now supplies are MOVED to raw["urban_superseded"], not deleted: they are the
    # oracle for the cross-check below, and a re-run must find them there.
    superseded = raw.get("urban_superseded", [])
    superseded += [r for r in raw["rows"] if not r.get("source") and r["year"] in URBAN_LABEL_FOR.values()]
    urban_by_year = defaultdict(Counter)
    for r in superseded:
        urban_by_year[r["year"]][(r["unitid"], r["cip"], r["award_level"], r["awards"])] += 1
    keep = [r for r in raw["rows"] if not ((r.get("source") or "").startswith("NCES") or
                                           (not r.get("source") and r["year"] in URBAN_LABEL_FOR.values()))]
    new_rows, unmapped = [], Counter()
    seen_levels = defaultdict(set)  # NCES year -> award levels it uses
    for year in NEW_YEARS:
        rows, fname = nces_rows(year)
        # Levels with real awards: a level present only as zero-award rows was never exercised by the cross-check.
        seen_levels[year] = {awlevel for _, _, awlevel, total in rows if total > 0}
        mapped = Counter()
        for unitid, cip, awlevel, total in rows:
            code = mapping.get(awlevel)
            if code is None:
                unmapped[awlevel] += 1
                continue
            # Zero-award rows are kept: Urban carries them every year (84-104/yr), and ipeds_build may read a row as
            # "the program was reported this year". The cross-check below compares the full set, zeros included.
            mapped[(unitid, cip, code, total)] += 1
            new_rows.append({"year": year, "unitid": unitid, "fips": None, "cip": cip, "cip_title": CIP[cip][0],
                             "group": CIP[cip][1], "award_level": code, "award": AWARD.get(code, f"code {code}"),
                             "awards": total, "source": f"NCES {fname}"})
        print(f"{year} ({fname}): {sum(mapped.values())} rows; unmapped NCES award levels: {dict(unmapped)}")
        if year in URBAN_LABEL_FOR:  # cross-check: mapped NCES rows must reproduce Urban's mislabeled year
            urban = urban_by_year[URBAN_LABEL_FOR[year]]
            same = sum(min(n, urban[k]) for k, n in mapped.items())
            print(f"  cross-check vs Urban '{URBAN_LABEL_FOR[year]}': {same}/{sum(urban.values())} rows identical")
            if not same or same != sum(urban.values()) or same != sum(mapped.values()):  # 0 = 0 is not a pass
                raise SystemExit("refusing to write: mapped NCES rows do not reproduce Urban's rows exactly")
    if unmapped:
        raise SystemExit("refusing to write: some NCES award levels have no derived Urban code")
    # A thinly calibrated level is trusted only where the oracle cross-check exercised it: it must appear in a
    # cross-checked year, which reproduced Urban row for row. Used only in an unchecked year, it refuses.
    checked = set().union(*(seen_levels[y] for y in URBAN_LABEL_FOR))
    unvouched = {lvl: n for lvl, n in thin.items() if lvl not in checked and any(lvl in seen_levels[y] for y in NEW_YEARS)}
    print(f"  thin calibration (<{MIN_VOTES} matches): {thin}; vouched by the cross-check: "
          f"{sorted(set(thin) & checked)}")
    if unvouched:
        raise SystemExit(f"refusing to write: award levels with thin calibration and no cross-check: {unvouched}")
    if not all(any(r["year"] == y for r in new_rows) for y in NEW_YEARS):
        raise SystemExit("refusing to write: an NCES year produced no rows")
    raw["rows"] = keep + new_rows
    raw["urban_superseded"] = superseded
    raw["meta"]["years"] = [raw["meta"]["years"][0], max(NEW_YEARS)]
    raw["meta"]["nces_direct"] = {"years": NEW_YEARS, "award_map_from": CALIBRATION_YEAR, "award_map": mapping}
    tmp = RAW + ".tmp"
    json.dump(raw, open(tmp, "w", encoding="utf-8"), indent=1)
    os.replace(tmp, RAW)


if __name__ == "__main__":
    main()
