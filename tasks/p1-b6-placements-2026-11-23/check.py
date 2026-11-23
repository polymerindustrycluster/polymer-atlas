#!/usr/bin/env python3
"""Check the sealed B6 verdicts, exact evidence proofs and entire canonical data delta."""
import argparse
from collections import Counter
from datetime import date, datetime
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "7a9731f2"
DAY = date(2026, 11, 23)
LABEL = "codex " + HERE.name
PLACEMENTS = HERE.parent / "blind-audit-12-protocol-2026-11-23/placements.csv"
CLAIMS = ("table", "record_id", "field", "verdict", "evidence_id")
PACKET = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/p1-b6-2026-11-23"
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")

prior = runpy.run_path(str(HERE.parent / "p1-atlas8-corrections-2026-11-23/check.py"))
git, parse, require, sha, unique = (prior[k] for k in ("git", "parse", "require", "sha", "unique"))
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate


def read(path):
    return parse(path.read_bytes())


def manifest(path, root):
    loaded = {}
    for line in path.read_text().splitlines():
        digest, name = line.split("  ", 1)
        relative = Path(name)
        require(name not in loaded and not relative.is_absolute() and ".." not in relative.parts,
                f"{path.name}: duplicate or unsafe path {name}")
        raw = (root / name).read_bytes()
        require(sha(raw) == digest, f"{path.name}: hash mismatch for {name}")
        loaded[name] = raw
    return loaded


def by_id(ref, pattern, key):
    return unique(gate.rows(ref, pattern), lambda row: row[key], pattern)


def values(row):
    return {k: v for k, v in row.items() if k != "_at"}


def packet_cells(packet, places):
    source = manifest(HERE / "PACKET.sha256", packet)
    rows = parse(source["verdicts.csv"])
    verdicts = unique(rows, lambda r: (r["table"], r["record_id"], r["field"]), "packet")
    require(Counter(r["verdict"] for r in verdicts.values()) == {"VERIFIED": 31, "STILL_UNCERTAIN": 3}
            and len({r["record_id"] for r in verdicts.values()}) == 31, "packet population differs")
    allowed = {r["record_id"]: r["proposed_value"] for r in verdicts.values() if r["field"] == "placement"}
    allowed.update(dict.fromkeys(("ORG-002099", "ORG-002100", "ORG-002120", "ORG-002122"), "REST_OF_COUNTRY"))
    allowed.update(dict.fromkeys(("ORG-001503", "ORG-001835", "ORG-002085", "ORG-002115"), "REST_OF_OHIO"))
    allowed["ORG-003769"] = "EXCLUDED"
    if "ORG-001850" in places:
        allowed["ORG-001850"] = "PIC18_RECORDS"
    require({rid: row["stratum"] for rid, row in places.items()} == allowed,
            "placement set or stratum differs from owner and controller decisions")
    ecosystem = by_id(BASE, "ecosystem.csv", "org_id")
    for rid, stratum in allowed.items():
        if stratum == "REST_OF_COUNTRY":
            scope = ecosystem[rid]["geography_served"]
            require(scope in ("national", "international") and f"geography_served={scope}" in places[rid]["basis"],
                    f"{rid}: rest-of-country scope differs from the base record")
    for name, county, fips in (
        ("acsic", "Franklin", "39049"), ("hersh", "Franklin", "39049"),
        ("miltek", "Tuscarawas", "39157"), ("oiex", "Franklin", "39049"),
        ("wrs", "Union", "39159"), ("ysu", "Mahoning", "39099"),
    ):
        matches = json.loads(source[f"geo/geo_{name}.json"])["result"]["addressMatches"]
        require(len(matches) == 1 and {(c["NAME"], c["STATE"] + c["COUNTY"])
                for c in matches[0]["geographies"]["Counties"]} == {(county + " County", fips)},
                f"{name}: county or FIPS differs from the sealed Census response")
    cells = {}
    for key, r in verdicts.items():
        if key[1] not in places:
            require(r["verdict"] == "VERIFIED" and key[2] != "placement" and r["proposed_value"],
                    f"{key}: no verified cell fill")
            cells[key] = r["proposed_value"]
    require({r["record_id"] for r in verdicts.values()} == {key[1] for key in cells} | places.keys(),
            "placements and canonical cells must account for all packet records")
    # Controller authorized the city when the same verbatim address substantiates both fields.
    require(cells.get(("ecosystem", "ORG-002862", "state")) == "VA", "Adhesion Society state differs")
    cells["ecosystem", "ORG-002862", "city"] = "Alexandria"
    return cells


def check_records(base, head, expected):
    changed = {}
    for table, pattern in (("organizations", "organizations_*.csv"), ("ecosystem", "ecosystem.csv")):
        before = by_id(base, pattern, "org_id")
        after = by_id(head, pattern, "org_id")
        require(before.keys() == after.keys(), f"{table}: record added or lost")
        for rid, old in before.items():
            new = after[rid]
            require(values(old).keys() == values(new).keys(), f"{rid}: columns changed")
            changed.update({(table, rid, key): new[key] for key in values(old) if old[key] != new[key]})
            for key in values(old):
                if (table, rid, key) in expected:
                    require(not old[key], f"{rid}: overwrote a held value for {key}")
            moved = old["_at"].rsplit(":", 1)[0] != new["_at"].rsplit(":", 1)[0]
            require(moved == (rid == "ORG-000095"), f"{rid}: unexpected shard movement")
            if moved:
                require(old["_at"].startswith("data/organizations_US.csv:")
                        and new["_at"].startswith("data/organizations_OH.csv:"), "MKV shard differs")
    require(changed == expected, "canonical cell delta differs from the permitted packet fills")


def check_evidence(head, expected, ledger, store):
    after = by_id(head, "evidence_*.csv", "evidence_id")
    before = by_id(BASE, "evidence_*.csv", "evidence_id")
    require(all(eid in after and values(after[eid]) == values(row) for eid, row in before.items()),
            "existing evidence changed or was removed")
    ids = set(after) - set(before)
    floor = max(int(eid.split("-")[1]) for eid in before)
    require(ids == {f"EVD-{i:06d}" for i in range(floor + 1, floor + 1 + len(ids))},
            "evidence IDs are not consecutive above the base maximum")
    proofs = unique(read(HERE / "BINDING_PROOF.csv"), lambda r: r["evidence_id"], "binding proofs")
    old_archives = by_id(BASE, "archive_links.csv", "evidence_id")
    archives = by_id(head, "archive_links.csv", "evidence_id")
    require(archives.keys() - old_archives.keys() == ids and all(
        eid in archives and values(archives[eid]) == values(r) for eid, r in old_archives.items()),
        "archive links are not append-only or differ from the evidence")
    require(proofs.keys() == ids == {r["evidence_id"] for r in ledger.values()},
            "proofs, newly allocated evidence and claim witnesses differ")
    receipts = unique(read(HERE / "ARCHIVES.csv"), lambda r: r["evidence_id"], "capture receipts")
    require(receipts.keys() == ids, "archive receipts differ from the new evidence")
    inputs = manifest(HERE / "INPUTS.sha256", store)
    captured = {sha(raw): raw for raw in inputs.values()}
    require(captured.keys() == {r["capture_sha256"] for r in proofs.values()},
            "input captures differ from the proof set")
    base_idx, idx = gate.Index.load(BASE), gate.Index.load(head)
    evidence_tiers = Counter()
    for eid in sorted(ids):
        ev, proof, arc, receipt = after[eid], proofs[eid], archives[eid], receipts[eid]
        table, rid = ev["record_table"], ev["record_id"]
        rec = idx.record(table, rid)
        cells = sorted((key[2], expected[key]) for key, row in ledger.items()
                       if row["evidence_id"] == eid and key[:2] == (table, rid))
        require(cells and len(cells) == sum(r["evidence_id"] == eid for r in ledger.values()),
                f"{eid}: ledger links to a different record")
        require(ev["created_by"] == LABEL and ev["claim_type"] == "address"
                and ev["tier_effect"] == "supports_" + rec["verification_tier"]
                and ev["observed_date"] == DAY.isoformat() and ev["source_class"] == "own_site",
                f"{eid}: wrong claim class, effect, date or label")
        markers, delimiter, quote = ev["claim_detail"].partition("; quote: ")
        route = " (Wayback capture)" if proof["capture"] != ev["source_ref"] else ""
        require(markers == ", ".join(f"{k}={v}" for k, v in cells) + route and delimiter and quote,
                f"{eid}: evidence does not name every changed field and value")
        link = gate.ARCHIVE_RE.fullmatch(arc["archive_ref"])
        require(link and link[2] is None and gate.same_page(link[3], ev["source_ref"])
                and datetime.strptime(link[1], "%Y%m%d%H%M%S").date().isoformat() == arc["captured_at"]
                and arc["archive_ref"] == receipt["archive_ref"] and arc["captured_at"] == receipt["captured_at"]
                and arc["created_by"] == receipt["created_by"] and receipt["job_id"].startswith("spn2-"),
                f"{eid}: archive receipt differs from evidence")
        require(gate.judge(ev, idx)[:2] == ("READ_REQUIRED", "mechanics_clear"), f"{eid}: binding mechanics")
        raw = captured[proof["capture_sha256"]]
        problem = gate.proof_problem(proof, ev, idx, base_idx, arc, DAY, "openai", lambda _: raw)
        require(not problem, f"{eid}: {problem}")
        if rid == "ORG-002862":
            require(gate.quoted_place(quote)[:2] == ("Alexandria", "VA"),
                    "both companion fields must come from the same quote")
        evidence_tiers[rec["verification_tier"]] += 1
    return evidence_tiers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=PACKET)
    parser.add_argument("--store", type=Path, default=STORE)
    parser.add_argument("--at", default=None, help="a Git ref, or the working tree by default")
    args = parser.parse_args()
    src = read(HERE / "CLAIMS_CHECKED.csv")
    ledger = unique(src, lambda r: (r["table"], r["record_id"], r["field"]), "claims ledger")
    require(tuple(src.fieldnames) == CLAIMS and all(r["verdict"] == "corrected" for r in ledger.values()),
            "claims schema or verdict differs")
    places = unique(read(PLACEMENTS), lambda r: r["record_id"], "placements")
    require({r["record_id"] for r in places.values() if r["stratum"] == "EXCLUDED"} == {"ORG-003769"},
            "named exclusion differs from owner round 22")
    expected = packet_cells(args.packet, places)
    require(ledger.keys() == expected.keys(), "each changed cell needs exactly one packet-backed claim")
    check_records(BASE, args.at, expected)
    tiers = check_evidence(args.at, expected, ledger, args.store)
    base_input = args.at or "HEAD"
    changed_paths = set(git("diff", "--name-only", BASE, base_input, "--", "data").decode().splitlines())
    if args.at is None:
        changed_paths.update(git("diff", "--name-only", "HEAD", "--", "data").decode().splitlines())
        changed_paths.update(git("ls-files", "--others", "--exclude-standard", "--", "data").decode().splitlines())
    require(changed_paths == {"data/" + f for f in ("archive_links.csv", "ecosystem.csv", "organizations_OH.csv",
             "organizations_US.csv", "evidence_ecosystem.csv", "evidence_organizations_OH.csv")},
            "unexpected or missing changed data file")
    print(f"PASS: 34 packet rows, {len(places)} explicit dispositions, {len(expected)} changed cells, "
          f"{sum(tiers.values())} new evidence rows and archives. Evidence rows by held tier: {dict(sorted(tiers.items()))}.")


if __name__ == "__main__":
    main()
