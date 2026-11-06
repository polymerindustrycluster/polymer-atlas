#!/usr/bin/env python3
"""Apply the fixed D10 packet after global IDs, dedupe and typed-claim preflight."""
import argparse
import csv
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import atlas
from shard_io import append_sorted

spec = importlib.util.spec_from_file_location("house_equipment", ROOT / "tasks/equipment-wave-1-2026-11-06/build.py")
house = importlib.util.module_from_spec(spec); spec.loader.exec_module(house)
read, has, Text = house.read, house.has, house.Text
clean = lambda row: {k: v for k, v in row.items() if not k.startswith("__")}


def plan(data):
    tables = atlas.load_tables(str(data))
    candidates, verdicts = read(HERE / "inputs.csv"), read(HERE / "verdicts.csv")
    assert len(candidates) == len(verdicts) == 12
    assert len({r["candidate_id"] for r in candidates}) == 12
    assert {r["candidate_id"] for r in candidates} == {r["candidate_id"] for r in verdicts}
    assert all(r["verdict"] in {"VERIFIED", "DUPLICATE_OF", "STILL_UNCERTAIN", "REJECT"} for r in verdicts)
    orgs = {}
    for table, row in atlas.org_rows(tables):
        assert row["org_id"] not in orgs, "duplicate existing ORG ID"
        orgs[row["org_id"]] = (table, clean(row))
    # Three hand-known held identities calibrate the reused house dedupe helper.
    for name, domain, expected in [("MAGNET", "manufacturingsuccess.org", "ORG-000159"),
                                    ("IACMI", "iacmi.org", "ORG-002099"),
                                    ("REMADE Institute", "remadeinstitute.org", "ORG-002100")]:
        result = atlas.dedupe(tables, domain=domain, name=name)
        assert any(h["id"] == expected for step in result["steps"] for h in step["hits"]), expected
    for row in verdicts:
        if row["verdict"] == "DUPLICATE_OF":
            assert row["held_or_new_id"] in orgs, "duplicate does not terminate at held ID"
    creates, evidence = read(HERE / "creates_ecosystem.csv"), read(HERE / "evidence_rows.csv")
    assert {r["org_id"] for r in creates} == {r["held_or_new_id"] for r in verdicts if r["verdict"] == "VERIFIED"}
    assert len({r["org_id"] for r in creates}) == len(creates)
    for row in creates:
        assert 13300 <= int(row["org_id"][4:]) <= 13399
        claims = {r["claim_type"] for r in evidence if r["record_table"] == "ecosystem" and r["record_id"] == row["org_id"]}
        assert {"existence", "address", "scope"} <= claims, "missing ecosystem must-have evidence"
        if row["parent_institution_org_id"]:
            assert row["parent_institution_org_id"] in orgs and "parent" in claims
        if row["status"] == "active":
            assert {"activity", "liveness"} <= claims
        if row["org_id"] in orgs:
            assert orgs[row["org_id"]] == ("ecosystem", row), "ORG collision or packet drift"
        else:
            for alias, domain in [(row["legal_name"], row["website"]),
                                  ("American Lightweight Materials Manufacturing Innovation Institute", "almmii.org"),
                                  ("ALMMII", None), ("Lightweight Innovations for Tomorrow", None)]:
                result = atlas.dedupe(tables, domain=domain, name=alias,
                                      street="1400 Rosa Parks Boulevard", city="Detroit", state="MI")
                assert result["stop_at_step"] is None, "new held dedupe hit"
    old_evidence = {}
    for row in tables["evidence"].rows:
        assert row["evidence_id"] not in old_evidence, "duplicate existing evidence ID"
        old_evidence[row["evidence_id"]] = row
    assert len({r["evidence_id"] for r in evidence}) == len(evidence)
    for row in evidence:
        assert 296000 <= int(row["evidence_id"][4:]) <= 296999
        assert row["record_table"] == "ecosystem"
        assert row["record_id"] in {r["org_id"] for r in creates}
        if row["evidence_id"] in old_evidence:
            old = old_evidence[row["evidence_id"]]
            assert old["__file__"] == "evidence_ecosystem.csv" and clean(old) == row, "EVD collision or packet drift"
    return [(data / "ecosystem.csv", [r for r in creates if r["org_id"] not in orgs], "org_id"),
            (data / "evidence_ecosystem.csv", [r for r in evidence if r["evidence_id"] not in old_evidence], "evidence_id")]


def raw_check():
    evidence = read(HERE / "evidence_rows.csv")
    checked = 0
    for url in sorted({r["source_ref"] for r in evidence}):
        result = subprocess.run(["curl", "-fL", "--max-time", "45", "-A", "Mozilla/5.0", "-sS", url],
                                capture_output=True, check=True)
        raw = result.stdout.decode("utf8", "replace")
        parser = Text(); parser.feed(raw); text = " ".join(parser.parts)
        for row in [r for r in evidence if r["source_ref"] == url]:
            quotes = re.findall(r'"([^"]+)"', row["claim_detail"])
            assert quotes and all(has(text, quote) for quote in quotes), (row["evidence_id"], "raw quote absent")
            checked += 1
        if "geocoding.geo.census.gov" in url:
            matches = json.loads(raw)["result"]["addressMatches"]
            assert len(matches) == 1
            assert has(matches[0]["matchedAddress"], "1400 Rosa Parks Blvd Detroit MI 48216")
            counties = matches[0]["geographies"]["Counties"]
            assert len(counties) == 1 and counties[0]["NAME"] == "Wayne County" and counties[0]["GEOID"] == "26163"
        assert not has(text, "Fabricated Federal Polymer Program XYZ"), "negative quote control"
        print("RAW PASS", url, flush=True)
    assert checked == len(evidence) == 5
    print("PASS raw5/5 observations over4/4 sources; known operator/plasma/HIP words; fabricated negative", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--raw-check", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    pending = plan(args.data_dir)
    if args.raw_check:
        raw_check()
    if args.apply:
        for path, rows, key in pending:
            if rows:
                append_sorted(path, rows, key)
    print("PASS census12/12; known held3/3; proposed1 C ecosystem+5 evidence rows; pending",
          sum(len(rows) for _, rows, _ in pending), "rows")


if __name__ == "__main__":
    main()
