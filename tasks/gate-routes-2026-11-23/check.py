"""Replay the named G8 cases from the shared store and the reader captures."""
import argparse
import csv
import hashlib
import io
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate


def read_zip(path, check):
    with zipfile.ZipFile(path) as archive:
        [member] = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        with archive.open(member) as handle:
            return check(csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8-sig", errors="replace")))


def ev(table, record, source, source_class, quote, claim="existence", detail=""):
    return dict(record_table=table, record_id=record, source_ref=source, source_class=source_class,
                claim_type=claim, claim_detail=f"{detail}quote: {quote}", tier_effect="supports_C",
                observed_date="2026-11-23")


def expect(row, idx, verdict, rule):
    actual = gate.judge(row, idx)[:2]
    assert actual == (verdict, rule), (row["record_id"], actual)


def replay(row, idx, capture, url, stamp, offset, archive=None, digest=None):
    proof = dict(record_id=row["record_id"], claim_sha256=gate.claim_sha256(row), verdict="VERIFIED",
                 reader_family="Gemini", reader_date="2026-11-23", capture=url, capture_date=stamp,
                 capture_sha256=digest or hashlib.sha256(capture).hexdigest(), quote_offset=str(offset))
    return gate.proof_problem(proof, row, idx, idx, archive, date(2026, 11, 23), "codex", lambda _: capture)


def address(row, zip_col):
    return f'{row["street_address"]}, {row["city"]}, {row["state"]} {row[zip_col]}'


def registry_row(rid, row, county, *, source="EPA ECHO RCRAInfo", claim="existence"):
    quote = f'facility_name: {row["facility_name"]}; address: {address(row, "zip")}; county: {county}'
    return ev("sites", rid, source, "registry", quote, claim, "place only; " if claim == "address" else "")


def registry_cases(store, idx):
    ita = store / "raw/osha/2026-11-22-archive-snapshot/raw/ita"

    def itarows(rows):
        width = 0
        picked = {}
        for row in rows:
            width = max(width, len(row["company_name"]))
            if row["establishment_id"] in {"356540", "67077"}:
                picked[row["establishment_id"]] = row
        return width, picked

    width, picked = read_zip(ita / "ITA-data-cy2021.zip", itarows)
    trunc = picked["356540"]
    older_width, older = read_zip(ita / "ITA_Data_CY2017.zip", itarows)
    assert width == len(trunc["company_name"]) == 43 and older_width == 100
    assert older["356540"]["company_name"].startswith(trunc["company_name"])
    assert len(older["356540"]["company_name"]) > 43
    quote = f'company_name: {trunc["company_name"]}; establishment_name: {trunc["establishment_name"]}; address: {address(trunc, "zip_code")}'
    mitsubishi = ev("organizations", "ORG-002080", "OSHA ITA CY2021 establishment id 356540", "government_filing", quote)
    expect(mitsubishi, idx, "PASS", "ita_cy2021_unique_prefix_and_establishment")
    competitor = dict(org_id="OTHER", legal_name=trunc["company_name"] + "ndustrial LLC")
    ambiguous = gate.Index(idx.sites.values(), [*idx.tables["organizations"].values(), competitor])
    expect(mitsubishi, ambiguous, "HELD", "ita_company_or_establishment_not_bound")

    ids = {"110039084558", "110004590979", "110054856615", "110020121125", "110004628476", "110018893786"}
    frs = read_zip(store / "raw/epa-frs/2026-11-20-state-single/state_single_oh.zip",
                   lambda rows: {r["REGISTRY_ID"]: r for r in rows if r["REGISTRY_ID"] in ids})
    assert frs.keys() == ids
    echo_file = store / "raw/echo/2026-11-22-archive-snapshot/out/echo_establishment_index.csv"
    with echo_file.open(newline="") as fh:
        echo = {(r["frs_registry_id"], r["program"]): r for r in csv.DictReader(fh)
                if r["frs_registry_id"] in ids}

    shurtech = older["67077"]
    locator = frs["110039084558"]
    assert gate.street_key(shurtech["street_address"]) == gate.street_key(locator["LOCATION_ADDRESS"])
    assert shurtech["city"].upper() == locator["CITY_NAME"] and shurtech["state"] == locator["STATE_CODE"]
    assert shurtech["zip_code"] == locator["POSTAL_CODE"].split("-")[0]
    shurtech = dict(shurtech, facility_name=shurtech["company_name"], zip=shurtech["zip_code"])
    row = registry_row("SITE-000610", shurtech, locator["COUNTY_NAME"],
                       source="OSHA ITA CY2017 establishment id 67077; EPA FRS 110039084558", claim="address")
    expect(row, idx, "PASS", "blank_street_registry")
    for old, new in ((", Avon,", ", Cleveland,"), ("44011", "44012"), ("LORAIN", "SUMMIT")):
        planted = row["claim_detail"].replace(old, new)
        assert planted != row["claim_detail"]
        expect(dict(row, claim_detail=planted), idx, "FAIL", "registry_place_not_bound")

    for rid, frsid, program, failure in (
        ("SITE-000212", "110004590979", "RCRA", "registry_place_not_bound"),
        ("SITE-000216", "110054856615", "RCRA", "registry_operator_not_held"),
        ("SITE-000928", "110020121125", "ICIS-AIR", "registry_operator_not_held"),
        ("SITE-000078", "110004628476", "RCRA", "registry_operator_not_held"),
    ):
        row = registry_row(rid, echo[(frsid, program)], frs[frsid]["COUNTY_NAME"])
        expect(row, idx, "FAIL", failure)

    # The KASE source locality is real. The organization has no held street/ZIP,
    # so only a test site with a supplied street and ZIP can exercise admission.
    kase = frs["110018893786"]
    kase_site = dict(site_id="TEST-KASE", org_id="ORG-001839", city=idx.orgs["ORG-001839"]["hq_city"],
                     state="OH", county=idx.orgs["ORG-001839"]["hq_county"], street_address=kase["LOCATION_ADDRESS"],
                     zip=kase["POSTAL_CODE"])
    kase_idx = gate.Index([kase_site], [idx.orgs["ORG-001839"]])
    row = registry_row("TEST-KASE", dict(facility_name=kase["PRIMARY_NAME"], city=kase["CITY_NAME"], state="OH",
                                        street_address=kase["LOCATION_ADDRESS"], zip=kase["POSTAL_CODE"]),
                       kase["COUNTY_NAME"])
    expect(row, kase_idx, "PASS", "mailing_city")
    for field, changed in (("street_address", "1 Hub Parkway"), ("zip", "44126"), ("county", "Summit")):
        wrong = gate.Index([dict(kase_site, **{field: changed})], [idx.orgs["ORG-001839"]])
        expect(row, wrong, "FAIL", "registry_place_not_bound")


def web_cases(persist, kent_capture, idx):
    root = persist / "p1-pic18-settle-2026-11-23"
    with (root / "recite/actions.csv").open(newline="") as handle:
        actions = {r["evidence_id"]: r for r in csv.DictReader(handle)}
    scratch = root / "recite.scratch"
    with (scratch / "captures.csv").open(newline="") as handle:
        captures = {r["evidence_id"]: r for r in csv.DictReader(handle)}
    bodies = {hashlib.sha256(body).hexdigest(): body for p in (scratch / "captures").glob("*.body")
              for body in (p.read_bytes(),)}
    for eid, rid, rule in (("EVD-405007", "ORG-000114", "press_explicit_hq"),
                           ("EVD-421581", "ORG-001481", "press_dateline")):
        proof, action = captures[eid], actions[eid]
        archive_url = proof["capture_ref"]
        m = gate.ARCHIVE_RE.fullmatch(archive_url)
        stamp = f"{m[1][:4]}-{m[1][4:6]}-{m[1][6:8]}"
        archive = dict(archive_ref=archive_url.replace("id_/", "/", 1), captured_at=stamp)
        quote = action["quote"]
        row = ev("organizations", rid, m[3], "press", quote)
        expect(row, idx, "READ_REQUIRED", rule)
        capture = bodies[proof["capture_sha256"]]
        assert replay(row, idx, capture, archive_url, stamp, gate.capture_text(capture).index(quote), archive,
                      proof["capture_sha256"]) == "", eid
        city = idx.orgs[rid]["hq_city"]
        planted = dict(row, claim_detail=row["claim_detail"].replace(city, "Akron"))
        assert gate.judge(planted, idx)[1] not in ("press_dateline", "press_explicit_hq")
        hq = dict(row, claim_type="address")
        if rule == "press_dateline":
            assert gate.judge(hq, idx)[1] not in ("press_dateline", "press_explicit_hq")
        else:
            expect(hq, idx, "READ_REQUIRED", "press_explicit_hq")

    kent = kent_capture.read_bytes()
    assert hashlib.sha256(kent).hexdigest() == "87056a6ac487575fb9e5769f91c9990b2597282b9497a24a3f2dcc62a397917b"
    assert b"header-util-ct-3" in kent and "Characterization Facility" in gate.capture_text(kent)
    planted = kent.replace(b"header-util-ct-3", b"site-header")
    assert "Characterization Facility" not in gate.capture_text(planted)

    lincoln = (persist / "p1-read-atlas9-rest-us-2026-11-23.scratch/extra/80148cbd78e3ef41.body").read_bytes()
    cik, _, quote, text = gate.edgar_business(lincoln, "submissions")
    assert cik == "0000059527"
    ref = f"https://data.sec.gov/submissions/CIK{cik}.json"
    row = ev("sites", "SITE-000154", ref, "government_filing", quote, "address")
    expect(row, idx, "READ_REQUIRED", "sec_edgar")
    assert replay(row, idx, lincoln, ref, "2026-11-23", text.index(quote)) == ""
    wrong = lincoln.replace(cik.encode(), b"0000059528")
    assert "linked filer" in replay(row, idx, wrong, ref, "2026-11-23", text.index(quote))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("store", type=Path)
    parser.add_argument("persist", type=Path)
    parser.add_argument("kent_capture", type=Path)
    args = parser.parse_args()
    idx = gate.Index.load()
    registry_cases(args.store, idx)
    web_cases(args.persist, args.kent_capture, idx)
    print("G8 real-case and planted near-miss replay passed")


if __name__ == "__main__":
    main()
