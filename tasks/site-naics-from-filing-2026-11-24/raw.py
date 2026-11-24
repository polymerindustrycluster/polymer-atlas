"""Read only the public filing columns used to adjudicate the candidate locators."""

import csv
import hashlib
import io
import zipfile
from collections import defaultdict
from frame import ITA, RAW, STORE

INSPECTION = RAW / "osha/2026-11-22-archive-snapshot/raw/OSHA_inspection.zip"


def read_filings(frame):
    wanted = defaultdict(set)
    for cited, all_filings in frame.values():
        for kind, day, key, *_ in all_filings:
            wanted[kind, day[:4]].add(key)
    found = defaultdict(set)
    paths = set()

    def read(stream, kind, fields, keys, year=None):
        reader = csv.reader(stream)
        header = next(reader)
        indexes = [header.index(c) for c in fields]
        for row in reader:
            if row[indexes[0]] not in keys:
                continue
            key, date, name, company, street, city, state, zipcode, code, count = [
                row[i] for i in indexes
            ]
            day = date[:10] if kind == "inspection" else date + "-12-31"
            if year and day[:4] != year:
                continue
            found[kind, day, key].add(
                (name, company, street, city, state, zipcode, code, count)
            )

    if ("ITA", "2025") in wanted:
        paths.add(ITA)
        with ITA.open(encoding="utf-8-sig", newline="") as h:
            read(
                h,
                "ITA",
                "establishment_ID year_filing_for establishment_name company_name street_address city state zip_code naics_code annual_average_employees".split(),
                wanted["ITA", "2025"],
                "2025",
            )
    for kind, year in wanted:
        if kind != "TRI":
            continue
        path = (
            RAW / "epa-tri-basic/2026-11-23-epa-national" / f"tri_basic_{year}_US.csv"
        )
        paths.add(path)
        with path.open(encoding="latin1", newline="") as h:
            read(
                h,
                kind,
                [
                    "2. TRIFD",
                    "1. YEAR",
                    "4. FACILITY NAME",
                    "4. FACILITY NAME",
                    "5. STREET ADDRESS",
                    "6. CITY",
                    "8. ST",
                    "9. ZIP",
                    "30. PRIMARY NAICS",
                    "1. YEAR",
                ],
                wanted[kind, year],
                year,
            )
    keys = set().union(*(ids for (k, _), ids in wanted.items() if k == "inspection"))
    if keys:
        paths.add(INSPECTION)
        fields = "ACTIVITY_NR OPEN_DATE ESTAB_NAME ESTAB_NAME SITE_ADDRESS SITE_CITY SITE_STATE SITE_ZIP NAICS_CODE NR_IN_ESTAB".split()
        with (
            INSPECTION.open("rb", buffering=4 * 1024 * 1024) as stream,
            zipfile.ZipFile(stream) as z,
        ):
            for member in z.namelist():
                if member.lower().endswith(".csv"):
                    with z.open(member) as raw:
                        read(
                            io.TextIOWrapper(
                                raw, encoding="utf-8-sig", errors="strict", newline=""
                            ),
                            "inspection",
                            fields,
                            keys,
                        )
    return found, paths


def hashes(paths):
    out = ""
    for path in sorted(paths):
        h = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                h.update(chunk)
        out += f"{h.hexdigest()}  {path.relative_to(STORE)}\n"
    return out
