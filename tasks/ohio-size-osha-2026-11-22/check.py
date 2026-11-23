#!/usr/bin/env python3
"""Replay all released Ohio OSHA decisions from raw and challenge the binding predicates."""
import argparse
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import build as W
from regions import PIC18

B = W.B
RAW_CHECK = W.upstream("check")


def require(test, reason):
    if not test:
        raise SystemExit(reason)


def known(value):
    return any(piece.strip() not in ("", "unknown") for piece in value.split(";"))


def independent_frame(data, base=None):
    """Direct census on the Ohio shard and organization fallback, independent of #468 frame()."""
    owners = defaultdict(list)
    for site in W.read(data / "sites_OH.csv", base):
        if (site["state"] == "OH" and site["county"] and site["county"] not in PIC18
                and site["operating_status"] == "active" and site["verification_tier"] in {"A", "B", "C"}):
            owners[site["org_id"]].append(site)
    fallback = {r["org_id"] for path in data.glob("organizations_*.csv")
                for r in W.read(path, base) if known(r["employee_band_ohio"])}
    unknown = {oid for oid, plant in owners.items() if oid not in fallback
               and not any(known(s["employee_band_site"]) for s in plant)}
    sites = {s["site_id"] for oid in unknown for s in owners[oid]}
    require(len(sites) == sum(len(owners[oid]) for oid in unknown), "duplicate independent site IDs")
    return owners, unknown, sites


def row_errors(p, row, site, orgs):
    """Check the raw witness independently of candidate search. Failures carry no source text."""
    kind = {"osha_ita": "ita", "osha_inspection": "insp"}[p["source"]]
    errors = []
    address_rows = B.unify([row], kind)
    if not address_rows:
        return ["street"]
    entry, = address_rows
    _, _, rid = RAW_CHECK.parse_loc(p["row_locator"])
    state, native_id = ((row["state"], row["id"]) if kind == "ita" else
                        (row["site_state"], row["activity_nr"]))
    if state.strip().upper() != "OH" or native_id != rid:
        errors.append("locator/state")
    if not (B.same_street(site["street_address"], entry["st"]) and B.city_ok(site, entry["city"], entry["zip"])):
        errors.append("street")
    name, _ = B.name_class(W.held_names(site, orgs), entry["names"])
    if name not in ("exact", "corporate_suffix_only") or name != p["name_match"]:
        errors.append("operator")
    dt = B.source_date(entry)
    if not W.valid_source_date(dt) or dt != p["source_date"] or str(B.year_of(entry)) != p["filing_year"]:
        errors.append("date")
    if B.band_of(B.count_of(entry)) != p["band"] or p["band"] not in B.BANDS:
        errors.append("band")
    if p["r13_source"] != {"ita": "1", "insp": "2"}[kind]:
        errors.append("source rank")
    return errors


def controls():
    site = dict(site_id="TEST-SITE", org_id="TEST-ORG", site_name="Sample Plastics - Plant",
                street_address="12 Example Street Suite 2", city="Sampleville", zip="44000",
                operating_status="active")
    orgs = {"TEST-ORG": dict(legal_name="Sample Plastics, Inc.")}
    raw = dict(id="10", state="OH", street_address="12 Example St Ste 2", city="Sampleville",
               zip_code="44000", establishment_name="Sample Plastics LLC", company_name="Sample Plastics",
               year_filing_for="2024", annual_average_employees="35", size="2", ein="", submitted="2025-03-01")
    packet = dict(source="osha_ita", row_locator="test.csv|row=1|id=10", name_match="exact",
                  source_date="2024-12-31", filing_year="2024", band="10-49", r13_source="1")
    require(row_errors(packet, raw, site, orgs) == [], "synthetic positive raw witness failed")
    require("band" in row_errors(dict(packet, band="5000+"), raw, site, orgs), "wrong band passed")
    require("street" in row_errors(packet, dict(raw, street_address="13 Example St"), site, orgs), "wrong street passed")
    require("street" in row_errors(packet, dict(raw, street_address="12 Example St Suite 8"), site, orgs), "wrong suite passed")
    stale = dict(raw, year_filing_for="2020")
    require("date" in row_errors(dict(packet, source_date="2020-12-31", filing_year="2020"), stale, site, orgs),
            "stale raw filing passed")
    child = dict(site, site_name="Sample Fabrication")
    child_orgs = {"TEST-ORG": dict(legal_name="Sample Fabrication Inc.", ultimate_parent_name="Sample Plastics")}
    require("operator" in row_errors(packet, raw, child, child_orgs), "parent-only filing passed")
    require(W.site_key("Sample Plastics - Sampleville plant") != W.operator_key("Sample Plastics"),
            "substantive site-name adornment was discarded")
    good = dict(raw, file="synthetic.csv", row="1", rid="10", member="")
    conflict = dict(estab_name="Sample Plastics Incorporated", site_address="12 Example St Suite 2",
                    site_city="Sampleville", site_zip="44000", open_date="2024-05-10", nr_in_estab="660")
    counts, street = W.context(orgs, [site])
    ix = {"ita": B.index(B.unify([good], "ita")), "insp": B.index([])}
    require(W.decide(site, orgs, ix, counts, street)[0] == "fill", "synthetic positive matcher failed")
    ix["insp"] = B.index(B.unify([conflict], "insp"))
    require(W.decide(site, orgs, ix, counts, street)[0] == "sources_disagree_in_window", "in-window conflict passed")
    require(W.private("Example Person LLC"), "individual-looking corporate-form name passed")
    adjacent = dict(conflict, nr_in_estab="55", open_date="2025-05-10")
    ix["insp"] = B.index(B.unify([adjacent], "insp"))
    result, decision = W.decide(site, orgs, ix, counts, street)
    require(result == "fill" and decision["band"] == "10-49"
            and decision["adjacent"]["band"] == "50-99", "newer adjacent inspection displaced ITA")
    print("Planted defects caught: wrong band, other street, wrong suite, stale raw date, parent-only name, "
          "substantive site suffix, in-window conflict, individual-looking name.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--data-dir", type=Path, default=W.ROOT / "data")
    parser.add_argument("--packet-dir", type=Path, default=W.HERE)
    parser.add_argument("--base", help="pre-application git ref for the frame and canonical diff check")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        controls()

    frame = W.read(args.packet_dir / "frame.csv")
    packet = W.read(args.packet_dir / "packet.csv")
    holds = W.read(args.packet_dir / "holds.csv")
    ids = [{r["site_id"] for r in rows} for rows in (frame, packet, holds)]
    require(all(len(keys) == len(rows) for keys, rows in zip(ids, (frame, packet, holds))), "duplicate site IDs")
    require(ids[0] == ids[1] | ids[2] and not ids[1] & ids[2], "frame membership/partition failed")
    owners, unknown, expected = independent_frame(args.data_dir, args.base)
    require(ids[0] == expected, "frame differs from independent Ohio-shard census")
    print(f"Independent census: {len(unknown)}/{len(owners)} organization rows size-unknown; "
          f"{len(frame)} frame site rows, {sum(r['civic_street'] == 'yes' for r in frame)} civic streets; "
          f"{len(packet)} fills + {len(holds)} holds.", flush=True)

    digests = W.manifest(args.raw)
    inputs = W.raw_inputs(args.raw)
    expected_hashes = "".join(f"{digests[path]}  {path}\n" for path in inputs)
    require((args.packet_dir / "INPUTS.sha256").read_text() == expected_hashes, "INPUTS does not equal OSHA raw manifest")
    for path in inputs:
        require(RAW_CHECK.sha(args.raw / path.removeprefix("raw/")) == digests[path], f"{path}: file hash mismatch")
    print(f"Verified {len(inputs)} raw OSHA SHA-256 digests.", flush=True)

    orgs, sites = W.load_atlas(args.data_dir, args.base)
    by_site = {s["site_id"]: s for s in sites}
    witnesses = list(packet)
    for p in packet:
        if p["adjacent_band"]:
            require(p["source"] == "osha_ita" and B.dist(p["band"], p["adjacent_band"]) == 1,
                    f"{p['site_id']}: adjacent witness is not one band apart from ITA")
            path = p["adjacent_source_file"]
            witnesses.append(dict(p, source="osha_inspection", source_file=path, file_sha256=digests[path],
                                  row_locator=p["adjacent_row_locator"], source_date=p["adjacent_source_date"],
                                  filing_year=p["adjacent_source_date"][:4], band=p["adjacent_band"],
                                  r13_source="2", name_match="exact"))
    for p in witnesses:
        require(p["source_file"] in inputs and p["file_sha256"] == digests[p["source_file"]],
                f"{p['site_id']}: source path or manifest digest mismatch")
    raw_rows = RAW_CHECK.fetch_rows(str(args.raw), witnesses)
    for p in witnesses:
        member, rownum, _ = RAW_CHECK.parse_loc(p["row_locator"])
        row = raw_rows[(p["source_file"], member)].get(rownum)
        require(row is not None, f"{p['site_id']}: raw row missing")
        errors = row_errors(p, row, by_site[p["site_id"]], orgs)
        require(not errors, f"{p['site_id']}: raw replay failed {', '.join(errors)}")
    print(f"Replayed {len(packet)} issued fills and {len(witnesses) - len(packet)} adjacent witnesses by pathname and raw row.", flush=True)

    selection = [by_site[k] for k in sorted(expected)]
    products = W.products(selection, orgs, sites, W.indexes(args.raw), digests)
    for result, saved, label in zip(products, (frame, packet, holds), ("frame", "packet", "holds")):
        require(result == saved, f"raw-extract decision replay diverged for {label}")
    edits = W.read(args.packet_dir / "edits.csv")
    evidence = W.read(args.packet_dir / "evidence_rows.csv")
    require(Counter(e["record_id"] for e in evidence) == Counter(ids[1]), "evidence/site cardinality mismatch")
    require(Counter(e["row_id"] for e in edits) == Counter({sid: 2 for sid in ids[1]}), "edits/site cardinality mismatch")
    if packet:
        first_id = int(evidence[0]["evidence_id"].removeprefix("EVD-"))
        require(first_id > 481199, "PR #468 evidence range reused")
        expected_edits, expected_evidence = W.application_rows(packet, sites, first_id)
        require(edits == expected_edits and evidence == expected_evidence, "application files differ from the packet")
    if args.base:
        require(args.data_dir.resolve() == W.ROOT / "data", "--base requires the repo data directory")
        changed = subprocess.check_output(["git", "-C", str(W.ROOT), "diff", "--name-only", args.base, "--", "data/"], text=True)
        paths = {"data/sites_OH.csv", "data/evidence_sites_OH.csv"} if packet else set()
        require(set(changed.splitlines()) == paths, "unexpected paths in canonical data diff")
        if packet:
            errs = RAW_CHECK.check_applied(args.base, packet)
            require(not errs, "canonical site/evidence scope or row preservation check failed")
            after_evidence = W.read(args.data_dir / "evidence_sites_OH.csv")
            require(after_evidence[-len(evidence):] == evidence, "appended canonical evidence differs from the packet")
            canonical = {s["site_id"]: s for s in W.read(args.data_dir / "sites_OH.csv")}
            require(all(canonical[e["row_id"]][e["column"]] == e["new_value"] for e in edits),
                    "applied site edits differ from the packet")
        _, after, _ = independent_frame(args.data_dir)
        require(unknown - after == {p["org_id"] for p in packet} and after <= unknown,
                "outside-PIC-18 organization size-unknown outcome mismatch")
        print(f"Ohio outside PIC-18 size-unknown organization rows: {len(unknown)} to {len(after)} of {len(owners)}.")

    print("Full-frame raw decision replay matched the packet and holds.")


if __name__ == "__main__":
    main()
