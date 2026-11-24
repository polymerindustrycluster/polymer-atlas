"""Replay the target reason of the November 24 candidate census against BASE."""

import csv
import io
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE = (HERE / "BASE").read_text().strip()
STORE = Path(
    os.environ.get(
        "ATLAS_STORE", "/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store"
    )
)
RAW = STORE / "raw"
ITA = (
    RAW
    / "osha/2026-11-22-archive-snapshot/raw/ita/ITA_300A_Summary_Data_2025_partial.csv"
)
sys.path.insert(0, str(REPO / "scripts"))
from atlas import name_key, site_name_key, squash, street_key
from matching import same_street


def git(*args):
    return subprocess.check_output(["git", "-C", str(REPO), *args])


def rows(path):
    return list(
        csv.DictReader(io.StringIO(git("show", BASE + ":" + path).decode("utf-8-sig")))
    )


def empband(n):
    bounds = [
        (1, "1-9"),
        (10, "10-49"),
        (50, "50-99"),
        (100, "100-249"),
        (250, "250-499"),
        (500, "500-999"),
        (1000, "1000-4999"),
        (5000, "5000+"),
    ]
    return next((b for x, b in reversed(bounds) if n >= x), "")


def loc(r, p=""):
    city = squash(r[p + "city"])
    state = r[p + "state"].upper()
    return ("" if city in {"unknown", "unspecified", "undetermined"} else city), state


def build():
    files = git("ls-tree", "-r", "--name-only", BASE, "data").decode().splitlines()

    def shards(prefix):
        return [
            r
            for f in files
            if re.fullmatch("data/" + prefix + r"_[A-Z]+\.csv", f)
            for r in rows(f)
        ]

    org = {r["org_id"]: r for r in shards("organizations")}
    site = {r["site_id"]: r for r in shards("sites")}
    eco = {r["org_id"]: r for r in rows("data/ecosystem.csv")}
    ev = defaultdict(list)
    for e in shards("evidence_sites"):
        ev[e["record_id"]].append(e)
    frame = {}
    # Re-bind primary filing extracts independently to this snapshot's name, street and city/state.
    lookup = defaultdict(list)
    for i, s in site.items():
        if s["street_address"]:
            lookup[(*loc(s), street_key(s["street_address"]))].append(i)
    filings = defaultdict(list)

    def bind(city, state, street, names, kind, day, key, number, naics):
        ids = lookup.get((squash(city), state.upper(), street_key(street)), [])
        matches = []
        for i in ids:
            s = site[i]
            o = org.get(s["org_id"]) or eco[s["org_id"]]
            held = {
                name_key(n)
                for n in [o["legal_name"], *o.get("trade_names", "").split(";")]
            } | {site_name_key(s["site_name"], s["city"])}
            if same_street(s["street_address"], street) and (
                held & {name_key(n) for n in names}
            ) - {""}:
                matches.append(i)
        if len(matches) == 1:
            b = empband(int(number)) if number.isdigit() else ""
            filings[matches[0]].append((kind, day, key, b, naics, names[0], street))

    with io.TextIOWrapper(
        io.BytesIO(ITA.read_bytes()), encoding="utf-8-sig", newline=""
    ) as h:
        for r in csv.DictReader(h):
            if r["year_filing_for"] == "2025":
                bind(
                    r["city"],
                    r["state"],
                    r["street_address"],
                    [r["establishment_name"], r["company_name"]],
                    "ITA",
                    "2025-12-31",
                    r["establishment_ID"],
                    r["annual_average_employees"],
                    r["naics_code"],
                )
    for r in rows("tasks/osha-spine-2026-11-01/establishments.csv"):
        args = (r["city"], r["state"], r["street"], [r["name"]], "inspection")
        bind(
            *args,
            r["latest_inspection"],
            r["latest_activity_nr"],
            r["nr_in_estab_latest_insp"],
            r["naics_latest"] if len(set(r["naics_all"].split(";"))) == 1 else "",
        )
        if (
            r["nr_latest_valid_open_date"]
            and r["nr_latest_valid_open_date"] != r["latest_inspection"]
        ):
            bind(
                *args,
                r["nr_latest_valid_open_date"],
                r["nr_latest_valid_activity_nr"],
                r["nr_in_estab_latest_valid"],
                "",
            )
    # Resolve only TRI reporting years explicitly cited on the site record or its code evidence.
    tri_years = defaultdict(set)
    for i, r in site.items():
        refs = [r["sources"]] + [
            e["source_ref"] for e in ev[i] if e["claim_type"] == "code"
        ]
        for ref in refs:
            for piece in ref.split(";"):
                if re.search(r"\bTRI\b", piece, re.I):
                    for y in re.findall(
                        r"(?:RY|reporting year)\s*(20\d\d)", piece, re.I
                    ):
                        tri_years[y].add(i)
    for year, ids in sorted(tri_years.items()):
        path = (
            RAW
            / "epa-tri-basic/2026-11-23-epa-national"
            / ("tri_basic_" + year + "_US.csv")
        )
        if not path.is_file():
            raise FileNotFoundError(path)
        seen = set()
        with io.TextIOWrapper(
            io.BytesIO(path.read_bytes()), encoding="latin1", newline=""
        ) as h:
            for row in csv.DictReader(h):
                key = (
                    row["2. TRIFD"],
                    row["30. PRIMARY NAICS"],
                    row["4. FACILITY NAME"],
                    row["5. STREET ADDRESS"],
                    row["6. CITY"],
                    row["8. ST"],
                )
                if (
                    key in seen
                    or not re.fullmatch(r"\d{6}", key[1])
                    or row["1. YEAR"] != year
                ):
                    continue
                seen.add(key)
                if any(
                    i in ids
                    for i in lookup.get(
                        (squash(key[4]), key[5], street_key(key[3])), []
                    )
                ):
                    bind(
                        key[4],
                        key[5],
                        key[3],
                        [key[2]],
                        "TRI",
                        year + "-12-31",
                        key[0],
                        "",
                        key[1],
                    )
    for i, r in (org | site).items():
        cs = []
        held = r["naics_primary"]
        if i in site and held and r["naics_primary_source_type"]:
            cite = (
                r["sources"]
                + " "
                + " ".join(e["source_ref"] for e in ev[i] if e["claim_type"] == "code")
            )
            for f in filings[i]:
                if not f[4] or not f[2]:
                    continue
                exact_id = re.search(r"\b" + re.escape(f[2]) + r"\b", cite)
                if (
                    (f[0] == "inspection" and exact_id)
                    or (f[0] == "TRI" and i in tri_years[f[1][:4]])
                    or (
                        f[0] == "ITA"
                        and re.search(
                            r"(?:ITA|300A)[^;]{0,65}(?:CY\s*2025|Summary_Data_2025)",
                            cite,
                            re.I,
                        )
                    )
                ):
                    cs.append(f)
        if any(f[4] != held for f in cs):
            frame[i] = (cs, filings[i])
    import hashlib

    assert (
        hashlib.sha256("\n".join(sorted(frame)).encode()).hexdigest()
        == "f2c7efb262c5276d066357e0bf4bf3f9b0233f635028dd84976e319463a4a130"
    ), "base frame differs from original census IDs"
    return frame
