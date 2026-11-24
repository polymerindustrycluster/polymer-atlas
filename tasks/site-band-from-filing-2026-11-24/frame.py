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
    last_write = git("show", "-s", "--format=%cs", BASE).decode().strip()
    for i, r in site.items():
        field = "employee_band_site"
        evidence = [e for e in ev[i] if e["claim_type"] == "size_band"]
        recs = filings[i]
        support = []
        other = False
        for e in evidence:
            t = e["claim_detail"] + " " + e["source_ref"]
            ds = re.findall(
                r"(?:source date |open date |opened |on )(\d{4}-\d\d-\d\d)", t, re.I
            )
            ys = re.findall(r"\bCY\s*(20\d\d)", t, re.I)
            if not ds and ys:
                ds = [max(ys) + "-12-31"]
            relevant = [
                f
                for f in recs
                if f[2]
                and re.search(r"\b" + re.escape(f[2]) + r"\b", t)
                and f[3]
                and (not ds or f[1] in ds)
            ]
            if relevant:
                support.extend((f[1], e["observed_date"]) for f in relevant)
            else:
                other = True
        facts = [(f[1], f[3]) for f in recs if f[3] and f[1]]
        d, w = max(support, default=("", ""))
        if not other and d and r[field] not in ("", "unknown") and facts:
            latest = max(day for day, _ in facts)
            if latest >= max(d, str(int(last_write[:4]) - 10) + last_write[4:]) and any(
                b != r[field] for day, b in facts if day == latest
            ):
                frame[i] = (recs, recs)
    import hashlib

    assert (
        hashlib.sha256("\n".join(sorted(frame)).encode()).hexdigest()
        == "2d6551912710808939944266690765b44ef3867cd8723359716b49d6272caf73"
    ), "base frame differs from original census IDs"
    return frame
