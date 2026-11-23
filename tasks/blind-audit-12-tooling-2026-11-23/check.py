"""Audit 12 regression check. All draw inputs here are synthetic."""
import csv
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))

import packets as p
import replay as r


def packet_check(root):
    tables = p.draw.fixture()
    # Give every synthetic site evidence and a link with explicit withheld metadata.
    links = tables.setdefault("registry_links", [])
    for n, site in enumerate(tables["sites"]):
        rid = site["site_id"]
        links.append(dict(org_id=site["org_id"], site_id=rid, registry="FRS",
                          registry_id=str(n), match_basis="exact identity", as_of="2026-11-23"))
        tables["evidence"].append(dict(evidence_id=f"EVD-{n:06d}", record_table="sites", record_id=rid,
                                       claim_type="address", source_ref="https://example.org/record",
                                       claim_detail="quote: private packet prose", tier_effect="supports_A",
                                       created_by="Claude"))
    reader = p.draw.MemReader(tables)
    draw_dir = root / "draw"
    seed = b"audit12-tooling-synthetic-only"
    at = "0" * 40
    sample, plants, _ = p.draw.run_draw(reader, at, seed, p.draw.sha(seed), draw_dir, plan=p.draw.TINY)
    frame_row = next(r for r in sample if r["table"] == "organizations" and r["stratum"] == "REST_US_RECORDS")
    reader.placements = lambda: {frame_row["record_id"]: ("REST_OF_COUNTRY", "private ruling basis")}
    out = root / "stage1"
    p.build(draw_dir, out, reader)
    with (out / "blind_a.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert (out / "blind_a.csv").read_bytes() == (out / "blind_b.csv").read_bytes()
    assert len(rows) == sum(r["stage"] == 1 for r in sample) + len(plants)
    assert not {r["record_id"] for r in rows} & {r["record_id"] for r in sample if r["stage"] == 2}
    lookup = {(r["table"], r["record_id"]): r for r in rows}
    site = next(r for r in rows if r["table"] == "sites")
    assert json.loads(site["evidence_json"]) == [{"claim_type": "address", "url": "https://example.org/record"}]
    link = json.loads(site["context_json"])["children"][0]
    assert link["values"]["site_id"] == site["record_id"] and "as_of" not in link["context"]
    assert "private ruling basis" not in (out / "blind_a.csv").read_text()
    for plant in plants:
        table, field = plant["table"], plant["field"]
        donor = next(r for r in reader.rows(table) if r[p.draw.ID_COL[table]] == plant["donor_record_id"])
        assert json.loads(lookup[(table, plant["record_id"])]["values_json"])[field] == donor[field]
    p.build(draw_dir, root / "stage2", reader, ["PROGRAMS"])
    with (root / "stage2" / "blind_a.csv").open(newline="") as f:
        extra = list(csv.DictReader(f))
    assert {r["record_id"] for r in extra} == {
        r["record_id"] for r in sample if r["stage"] == 2 and r["stratum"] == "PROGRAMS"
    }
    for leaked in (dict(rows[0], created_by="Some builder"),
                   dict(rows[0], context_json='{"created_by":"Some builder"}')):
        try:
            p.leak_scan([leaked])
        except ValueError:
            pass
        else:
            raise AssertionError("created_by escaped leak scan")
    print(f"PASS packet build and leak scan ({len(rows)} stage-1 synthetic rows including {len(plants)} plants)")


def replay_check():
    # Public admission batch #502 on main. Select ten distinct parents with stored proofs.
    at = p.draw.require_ancestor("7a9731f2881e8ed5cfc6bfb7b1121167505868d2")
    replay = r.Replay(at, r.STORE)
    proofs = replay.read("tasks/p1-process-web-2026-11-23/BINDING_PROOF.csv")
    ids = dict.fromkeys(x["record_id"] for x in p.csv_rows(proofs.decode()))
    targets = [key for key in replay.evidence if key[1] in ids][:10]
    assert len(targets) == len({key[1] for key in targets}) == 10
    results = replay.records(targets)
    assert len(results) == 10 and sum(len(row["evidence"]) for row in results) == 45
    assert all(any(e["status"] == "PASS" for e in record["evidence"]) for record in results)
    positive = next(e["evidence_id"] for record in results for e in record["evidence"] if e["status"] == "PASS")
    ev = next(e for key in targets for e in replay.evidence[key] if e["evidence_id"] == positive)
    planted = dict(ev, claim_detail=ev["claim_detail"] + " zzzauditfixtureword")
    assert replay.row(planted) == ("FIELD_ERROR", "quote_absent_from_capture")
    counts = p.Counter(e["status"] for record in results for e in record["evidence"])
    print(f"PASS replay on 10 distinct main records ({dict(sorted(counts.items()))} evidence rows), "
          "absent quote plant rejected")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        packet_check(Path(tmp))
    replay_check()
