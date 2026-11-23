#!/usr/bin/env python3
"""Replay registry bindings using the named Parquet inputs and row locators."""
import argparse
from collections import defaultdict
import csv
import hashlib
from pathlib import Path

import duckdb

from build import (
    ANCHOR, CROSSWALK, EXACT, FACILITIES, FIELDS, FRS, LOCATORS, PROGRAM,
    PROOF_FIELDS, ROOT, RCRA, binding_reason, evaluate, held_elsewhere, read,
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_binding(registry, rid, site, owner, notes, facility, crosswalk=None, anchor=None, held=()):
    require(not held_elsewhere(site, held), "identifier_already_held_elsewhere")
    require(facility[0] == rid, "EPA row identifier differs")
    if anchor:
        code, program_id, frs_id, *_ = crosswalk
        require(PROGRAM.get(code) == registry and program_id == rid and frs_id == anchor[0],
                "FRS crosswalk disagrees with program and anchor identifiers")
        reason = binding_reason(site, owner, notes, anchor)
        require(not reason, reason)
    reason = binding_reason(site, owner, notes, facility, anchor)
    require(not reason, reason)


def negative_controls():
    site = {"site_id": "SITE-TEST", "org_id": "ORG-TEST", "street_address": "10 Eagle Street", "state": "OH"}
    owner = ({("akron",)}, "44305", {("example", "plastics")}, {("example", "parent")})
    rid = "OHD012345678"
    row = (rid, "Example Plastics Inc", "10 Eagle St", "Akron", "OH", "44305")
    verify_binding(RCRA, rid, site, owner, (), row)
    bad_street = (*row[:2], "20 Eagle St", *row[3:])
    bad_parent = (row[0], "Example Parent Inc", *row[2:])
    already_held = [{"site_id": "SITE-OTHER", "org_id": "ORG-OTHER"}]
    for facility, held, reason in (
        (bad_street, (), "street_mismatch"),
        (bad_parent, (), "recorded_parent_only"),
        (row, already_held, "identifier_already_held_elsewhere"),
    ):
        try:
            verify_binding(RCRA, rid, site, owner, (), facility, held=held)
        except ValueError as exc:
            require(str(exc) == reason, f"expected {reason}, got {exc}")
        else:
            raise ValueError(f"negative control passed: {reason}")
    print("Negative controls refused wrong street, parent-only operator and ID held elsewhere")


def replay(lake, directory, region, canary=False):
    _, selected, _, _, accepted, owners, leads, _ = evaluate(lake, region, canary)
    expected_frame = [{k: s[k] for k in ("site_id", "org_id", "county")} for s in selected]
    require(read(directory / "frame.csv") == expected_frame, "frame differs from pinned Atlas selection")
    packet = directory / "packet.csv"
    with packet.open(encoding="utf-8", newline="") as f:
        require(tuple(next(csv.reader(f))) == (*FIELDS, *PROOF_FIELDS), "packet column order")
    rows = read(packet)
    keys = [(r["site_id"], r["registry"], r["registry_id"]) for r in rows]
    require(len(keys) == len(set(keys)), "duplicate packet link")
    require(set(keys) == set(accepted), "packet identifiers differ from independently rebuilt selection")
    expected_leads = [{"site_id": sid, "registry": reg, "registry_id": rid, "reason": reason}
                      for (sid, reg, rid), reasons in sorted(leads.items()) for reason in reasons]
    require(read(directory / "leads.csv") == expected_leads, "lead reasons differ from rebuilt selection")

    # Fetch each named row independently of the join; the full provenance tuple
    # must point to exactly one record in the proper EPA table.
    conn = duckdb.connect()
    manifest = {r["parquet_path"]: r for r in read(lake / "MANIFEST.csv")}
    held = defaultdict(list)
    for row in read(ROOT / "data/registry_links.csv"):
        held[row["registry"], row["registry_id"]].append(row)
    notes = dict(conn.execute(
        """SELECT site_id, notes FROM read_parquet(?) UNION ALL
        SELECT org_id, notes FROM read_parquet(?)""",
        [str(lake / "atlas/atlas_sites.parquet"), str(lake / "atlas/atlas_orgs.parquet")],
    ).fetchall())
    notes.update((r["org_id"], r["notes"]) for r in read(ROOT / "data/ecosystem.csv"))
    requests = defaultdict(set)

    def locator(row, prefix, table, columns):
        path, digest, raw_row = (row[prefix + k] for k in LOCATORS)
        parquet = f"echo/{table}.parquet"
        m = manifest[parquet]
        require(path == m["raw_path_under_raw"] and digest == m["raw_sha256"], "unexpected raw source path or digest")
        require(raw_row.isdecimal() and int(raw_row) > 0, "invalid raw row locator")
        key = parquet, tuple(columns)
        requests[key].add(int(raw_row))
        return key, path, digest, int(raw_row)

    proofs = []
    for key, row in zip(keys, rows, strict=True):
        canonical, _ = accepted[key]
        require(tuple(row[k] for k in FIELDS) == canonical, "canonical registry fields differ")
        registry = row["registry"]
        table, *fields = FACILITIES[registry]
        locators = [locator(row, "", table, fields)]
        if row["match_basis"] == ANCHOR:
            locators.append(locator(row, "crosswalk_", CROSSWALK, ("PGM_SYS_ACRNM", "PGM_SYS_ID", "REGISTRY_ID")))
            table, *fields = FACILITIES[FRS]
            locators.append(locator(row, "frs_", table, fields))
        else:
            require(row["match_basis"] == EXACT and not any(row[k] for k in PROOF_FIELDS[3:]),
                    "unexpected crosswalk locator")
        proofs.append((key, locators))

    found = {}
    for (parquet, fields), requested in requests.items():
        for result in conn.execute(
            f"""SELECT {', '.join(fields)}, src_path, src_sha256, src_row
            FROM read_parquet(?) WHERE src_row IN (SELECT unnest(?))""",
            [str(lake / parquet), sorted(requested)],
        ).fetchall():
            src = (parquet, fields), *result[-3:]
            require(src not in found, "duplicate lake row locator")
            found[src] = tuple(v if v is not None else "" for v in result)
    for key, locators in proofs:
        require(all(loc in found for loc in locators), f"missing lake row locator for {key}")
        replayed = tuple(found[loc] for loc in locators)
        _, registry, rid = key
        site, owner = owners[key]
        site_notes = [notes.get(k) or "" for k in (site["site_id"], site["org_id"])]
        verify_binding(registry, rid, site, owner, site_notes, *replayed, held=held[registry, rid])
    print(f"Replayed {len(rows)} registry links using {len(found)} Parquet rows across {len(selected)} selected sites")


def check_hashes(lake, pins):
    lake_prefix = "provenance/lake/2026-11-22/"
    lines = pins.read_text(encoding="utf-8").splitlines()
    require(lines, "empty checksum manifest")
    for line in lines:
        expected, ref = line.split("  ", 1)
        if ref.startswith(lake_prefix):
            source = lake / ref.removeprefix(lake_prefix)
        elif ref.startswith("raw/"):
            source = lake.parents[1] / ref
        else:
            source = ROOT / ref
        with source.open("rb") as f:
            actual = hashlib.file_digest(f, "sha256").hexdigest()
        require(actual == expected, f"sha256 differs for {ref}")
    print(f"Verified {len(lines)} pinned input digests")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lake", type=Path)
    p.add_argument("--packet", type=Path, default=Path(__file__).parent)
    p.add_argument("--region", choices=("pic18", "rest-oh"), default="pic18")
    p.add_argument("--canary", action="store_true")
    p.add_argument("--negative-controls-only", action="store_true")
    p.add_argument("--hash-inputs", action="store_true")
    args = p.parse_args()
    if not args.negative_controls_only and args.lake is None:
        p.error("--lake is required for replay")
    negative_controls()
    if not args.negative_controls_only:
        if args.hash_inputs:
            check_hashes(args.lake, args.packet / "INPUTS.sha256")
        replay(args.lake, args.packet, args.region, args.canary)


if __name__ == "__main__":
    main()
