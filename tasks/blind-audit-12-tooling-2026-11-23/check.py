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
                          registry_id=f"wave fixture {n}", match_basis="exact identity", as_of="2026-11-23"))
        site["employee_band_site"] = "10-49"
        tables["evidence"].append(dict(evidence_id=f"EVD-{n:06d}", record_table="sites", record_id=rid,
                                       claim_type="address", source_ref="https://example.org/record",
                                       claim_detail="quote: private packet prose", tier_effect="supports_A",
                                       created_by="Claude"))
        tables["evidence"].append(dict(evidence_id=f"EVD-{n+1000:06d}", record_table="sites", record_id=rid,
            claim_type="size_band", claim_detail="employee_band_site=10-49: OSHA ITA Form 300A CY2023",
            source_ref="OSHA ITA Form 300A CY2023, record id 1234",
            source_class="government_filing", observed_date="2026-11-23"))
    for row in tables["organizations"]:
        row["naics_primary_source_name"] = "Grok wave fixture"
        row["description_1line"] = "See Note 9"
    for row in tables["sites"]:
        row["street_address"] = "Claude Freeman Drive"
    reader = p.draw.MemReader(tables)
    draw_dir = root / "draw"
    seed = b"audit12-tooling-synthetic-only"
    at = "0" * 40
    sample, plants, _ = p.draw.run_draw(reader, at, seed, p.draw.sha(seed), draw_dir, plan=p.draw.TINY)
    frame_row = next(r for r in sample if r["table"] == "organizations" and r["stratum"] == "REST_US_RECORDS")
    reader.placements = lambda: {frame_row["record_id"]: ("REST_OF_COUNTRY", "private ruling basis")}
    out = root / "stage1"
    allowed = next(r for r in sample if r["table"] == "organizations" and r["stage"] == 1)
    cell = f"organizations/{allowed['record_id']}/description_1line"
    fixture = next(r for r in tables["organizations"] if r["org_id"] == allowed["record_id"])
    fixture["legal_name"] = "Claude Synthetic Manufacturing"
    inventory = list(p.false_positive_candidates(reader))
    assert dict(cell=cell, matched_token="Note", text="See Note 9") in inventory
    assert not any(r["cell"].endswith("/naics_primary_source_name") for r in inventory)
    naics = f"organizations/{allowed['record_id']}/naics_primary_source_name"
    p.build(draw_dir, out, reader, approved={(cell, "Note", "See Note 9"),
                                             (naics, "Grok", "Grok wave fixture"),
                                             (naics, "wave", "Grok wave fixture")})
    with (out / "blind_a.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert (out / "blind_a.csv").read_bytes() == (out / "blind_b.csv").read_bytes()
    assert len(rows) == sum(r["stage"] == 1 for r in sample) + len(plants)
    assert not {r["record_id"] for r in rows} & {r["record_id"] for r in sample if r["stage"] == 2}
    lookup = {(r["table"], r["record_id"]): r for r in rows}
    org = lookup["organizations", allowed["record_id"]]
    assert "naics_primary_source_name" in org["columns_under_audit"].split(";")
    assert json.loads(org["values_json"])["naics_primary_source_name"] == "[withheld for blindness]"
    assert json.loads(org["values_json"])["description_1line"] == "See Note 9"
    assert org["record_label"] == json.loads(org["values_json"])["legal_name"] == p.WITHHELD
    another = next(r for r in rows if r["table"] == "organizations" and r is not org)
    assert json.loads(another["values_json"])["description_1line"] == "[withheld for blindness]"
    assert "Grok wave fixture" not in (out / "blind_a.csv").read_text()
    with (out / "withheld_counts.csv").open(newline="") as f:
        counts = list(csv.DictReader(f))
    plant_keys = {p.record_key(r) for r in plants}
    expected = p.Counter()
    for row in rows:
        child_cells = [value for child in json.loads(row["context_json"])["children"]
                       for value in child["values"].values()]
        expected[row["stratum"], p.record_key(row) in plant_keys] += (
            list(json.loads(row["values_json"]).values()) + child_cells).count(p.WITHHELD)
    for count in counts:
        assert int(count["sampled_cells"]) == expected[count["stratum"], False]
        assert int(count["plant_cells"]) == expected[count["stratum"], True]
    site = next(r for r in rows if r["table"] == "sites")
    assert json.loads(site["values_json"])["street_address"] == "[withheld for blindness]"
    evidence = json.loads(site["evidence_json"])
    assert {"claim_type": "address", "url": "https://example.org/record"} in evidence
    assert {"claim_type": "size_band", "url": "", "filing_source": "osha_ita", "filing_year": 2023,
            "filing_id": "1234"} in evidence
    assert "2026-11-23" not in site["evidence_json"]
    assert not p.band_filings(tables["evidence"], "employee_band_site", "50-99")
    unknown = dict(next(e for e in tables["evidence"] if e["claim_type"] == "size_band"),
                   source_ref="OSHA ITA Form 300A", claim_detail="employee_band_site=10-49")
    assert p.band_filings([unknown], "employee_band_site", "10-49")[0]["filing_year"] is None
    inspection = dict(unknown, source_ref="OSHA inspection; source.zip!table.csv@2; id=5678",
                      claim_detail="employee_band_site=10-49; OSHA inspection, filing year 2018; quote: fixture")
    assert p.band_filings([inspection], "employee_band_site", "10-49") == [{
        "claim_type": "size_band", "url": "", "filing_source": "osha_inspection",
        "filing_year": 2018, "filing_id": "5678"}]
    link = json.loads(site["context_json"])["children"][0]
    public_url = "https://example.org/pr/annual-report"
    citation = dict(site, cited_sources=public_url)
    cell = f"sites/{site['record_id']}/cited_sources/url/1"
    candidate = (cell, "pr", public_url)
    hits = set()
    p.leak_scan([citation], context_candidates=hits)
    assert hits == {candidate}
    p.leak_scan([citation], approved={candidate})
    assert citation["cited_sources"] == public_url
    for unapproved, approvals in (
        (citation, ()),
        (dict(citation, cited_sources=public_url + "-other"), {candidate}),
        (dict(citation, record_id="SITE-999999"), {candidate}),
        (dict(citation, created_by="builder"), {candidate}),
        (dict(citation, cited_sources=public_url + "?created_by=abc"),
         {(cell, "pr", public_url + "?created_by=abc"), (cell, "created_by", public_url + "?created_by=abc")}),
    ):
        try:
            p.leak_scan([unapproved], approved=approvals)
        except ValueError:
            pass
        else:
            raise AssertionError("unapproved context escaped leak scan")
    inspected = dict(unknown, source_ref="https://www.osha.gov/ords/imis/establishment.inspection_detail?id=98765",
                     claim_detail="employee_band_site=10-49; OSHA inspection opened 2017-05-03")
    filing = p.band_filings([inspected], "employee_band_site", "10-49")[0]
    assert (filing["filing_source"], filing["filing_id"], filing["filing_year"]) == ("osha_inspection", "98765", 2017)
    lookalike = dict(inspected, source_ref=inspected["source_ref"].replace("www.osha.gov", "osha.gov.example"))
    assert p.band_filings([lookalike], "employee_band_site", "10-49")[0]["filing_year"] is None
    assert link["values"]["site_id"] == site["record_id"] and "as_of" not in link["context"]
    assert link["values"]["registry_id"] == p.WITHHELD
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
                   dict(rows[0], context_json='{"created_by":"Some builder"}'),
                   dict(rows[0], columns_under_audit=rows[0]["columns_under_audit"] + ";reviewer_label")):
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
