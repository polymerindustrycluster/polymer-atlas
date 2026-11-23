#!/usr/bin/env python3
"""Replay the exact #520 gate re-citations and the Kent name correction."""
import argparse
from collections import defaultdict
from datetime import date
import hashlib
from pathlib import Path
import re
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "b5958a7828dc0435bbf3327b36cdd10e81ec81ac"
PERSIST = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist"
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
LABEL = HERE.name
TODAY = "2026-11-23"
CLAIM_HEADER = ("table", "record_id", "field", "verdict", "evidence_id")
PRESS_ACTIONS = "p1-pic18-settle-2026-11-23/recite/actions.csv"
EDGAR_READ = "p1-read-atlas9-rest-us-2026-11-23/verdicts.csv"
KENT_READ = "p1-read-atlas8-open-2026-11-23/verdicts.csv"
ITA = "raw/osha/2026-11-22-archive-snapshot/raw/ita"
ITA21 = f"{ITA}/ITA-data-cy2021.zip"
ITA17 = f"{ITA}/ITA_Data_CY2017.zip"
FRS = "raw/epa-frs/2026-11-20-state-single/state_single_oh.zip"
SETTLE = "provenance/pic18-settle-2026-11-23/captures"
CAPTURES = "provenance/gate-recite-2026-11-23/captures"
PRESS = {
    "EVD-405007": ("8d19b2f39ad1d812fc68d7ebb17e711d3a038bcc771c05659b8b4b26e99f49d5", "press_explicit_hq"),
    "EVD-421581": ("97c68b10dd01292ba4bac2c642438047eda6c8efef63c91886deabe0d90e517b", "press_dateline"),
}
LINCOLN = "c4ce71eff309277530af66374fd456b5ad6e67f33da33fb87abf5e444b9bf4fe"
KENT = "fff47b4bc98f2f45d342129d3e4f5cc03406ed19dcbb7c8e22c5f90d4b2d83ea"
KENT_URL = "https://www.kent.edu/amlci/characterization-facility"
KENT_CAP = f"https://web.archive.org/web/20260609214342id_/{KENT_URL}"
KENT_QUOTE = "Characterization Facility Welcome to the AMLCI Characterization Facility!"
ADMITTED = (*PRESS, "EVD-421870", "EVD-422344", "EVD-420042")
FIRST_EVIDENCE = 483112

lib = runpy.run_path(str(HERE.parent / "p1-atlas8-corrections-2026-11-23/check.py"))
git, parse, require, sha, unique, csv_bytes, snapshot, expected_data = (
    lib[k] for k in ("git", "parse", "require", "sha", "unique", "csv_bytes", "snapshot", "expected_data")
)
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate
route = runpy.run_path(str(HERE.parent / "gate-routes-2026-11-23/check.py"))


def pinned(manifest, root, names):
    paths = {}
    for line in (HERE / manifest).read_text().splitlines():
        digest, name = line.split("  ", 1)
        require(name not in paths and re.fullmatch(r"[0-9a-f]{64}", digest), f"{manifest}: bad pin")
        paths[name] = root / name
        with paths[name].open("rb") as source:
            require(hashlib.file_digest(source, "sha256").hexdigest() == digest, f"{name}: hash differs")
    require(paths.keys() == set(names), f"{manifest}: inputs differ from the admitted set")
    return paths


def registry_quotes(files):
    def extract(rows, ids):
        width, hits = 0, []
        for r in rows:
            width = max(width, len(r["company_name"]))
            if r["establishment_id"] in ids:
                hits.append(r)
        index = unique(hits, lambda r: r["establishment_id"], "ITA establishment")
        require(index.keys() == ids, "ITA establishment missing")
        return width, index

    read_zip = route["read_zip"]
    w21, cy21 = read_zip(files[ITA21], lambda rd: extract(rd, {"356540"}))
    w17, cy17 = read_zip(files[ITA17], lambda rd: extract(rd, {"356540", "67077"}))
    m, earlier, s = cy21["356540"], cy17["356540"], cy17["67077"]
    short, full = m["company_name"], earlier["company_name"]
    addr = route["address"]
    require(w21 == len(short) == 43 and w17 == 100 and full.startswith(short) and len(full) > 43
            and addr(m, "zip_code").casefold() == addr(earlier, "zip_code").casefold(),
            "Mitsubishi CY2021 width or CY2017 full-name/address replay differs")
    matches = read_zip(files[FRS], lambda rows: [r for r in rows if r["REGISTRY_ID"] == "110039084558"])
    require(len(matches) == 1, "ShurTech FRS registry ID must identify one record")
    f = matches[0]
    require(gate.street_key(s["street_address"]) == gate.street_key(f["LOCATION_ADDRESS"])
            and s["city"].upper() == f["CITY_NAME"] and s["state"] == f["STATE_CODE"]
            and s["zip_code"] == f["POSTAL_CODE"].split("-")[0],
            "ShurTech ITA and FRS do not tie to the same address")
    return (f"company_name: {short}; establishment_name: {m['establishment_name']}; address: {addr(m, 'zip_code')}",
            f"facility_name: {s['company_name']}; address: {addr(s, 'zip_code')}; county: {f['COUNTY_NAME']}")


def expected(persist, store):
    records, evidence = snapshot(BASE)
    require(max(int(e[4:]) for e in evidence) + 1 == FIRST_EVIDENCE, "Evidence ID allocation changed")
    packet = pinned("PACKET.sha256", persist, (PRESS_ACTIONS, EDGAR_READ, KENT_READ))
    lincoln_path, kent_path = (f"{CAPTURES}/{x}.body" for x in (LINCOLN, KENT))
    press_paths = {eid: f"{SETTLE}/{digest}.body" for eid, (digest, _) in PRESS.items()}
    files = pinned("INPUTS.sha256", store, (ITA21, ITA17, FRS, lincoln_path, kent_path, *press_paths.values()))
    idx = gate.Index.load(BASE)
    admission = unique(parse(git("show", f"{BASE}:tasks/p1-pic18-settle-2026-11-23/RE_ADMISSION.csv")),
                       lambda r: r["evidence_id"], "G8 re-admission queue")
    require(len(admission) == 18 and set(ADMITTED) <= admission.keys(), "G8 queue census differs")
    reads = unique(parse((HERE / "WEB_READ.csv").read_bytes()), lambda r: r["claim_id"], "independent readings")
    require(reads.keys() == {*PRESS, "EVD-420042", "PROG-000014"}, "Reading coverage differs")
    claims, archives, proofs, new_rows = [], [], [], defaultdict(list)

    def claim(table, record, field, eid):
        claims.append(dict(zip(CLAIM_HEADER, (table, record, field, "corrected", eid))))

    def add(old_id, table, rid, ct, cls, source, effect, detail, quote, *, rule, role="", cap="", body=None,
            observed=TODAY, notes="", offset=None):
        require(not re.search(r"@|\b\d{3}[-. ]\d{3}[-. ]\d{4}\b", quote), f"{rid}: quote includes contact text")
        eid = f"EVD-{FIRST_EVIDENCE + sum(map(len, new_rows.values())):06d}"
        datum, _ = records[table, rid]
        row = dict(evidence_id=eid, record_table=table, record_id=rid, claim_type=ct, claim_detail=f"{detail}quote: {quote}",
                   source_class=cls, source_ref=source, observed_date=observed, tier_effect=effect, created_by=LABEL,
                   notes=notes, address_role=role)
        want = "PASS" if body is None else "READ_REQUIRED"
        require(gate.judge(row, idx)[:2] == (want, rule), f"{rid}: binding route differs")
        if old_id.startswith("EVD-"):
            require(evidence[old_id]["record_id"] == rid == admission[old_id]["record_id"], f"{old_id}: record differs")
            claim("evidence", old_id, "claim_detail", eid)
        if body is not None:
            archive = None
            stamp = TODAY
            if m := gate.ARCHIVE_RE.fullmatch(cap):
                stamp = f"{m[1][:4]}-{m[1][4:6]}-{m[1][6:8]}"
                archive = dict(evidence_id=eid, archive_ref=cap.replace(m[1]+"id_/", m[1]+"/", 1),
                               captured_at=stamp, created_by="unknown")
                archives.append(archive)
            if offset is None:
                offset = gate.capture_text(body).index(quote)
            reading = reads[old_id]
            require((reading["capture_sha256"], reading["quote_offset"]) == (sha(body), str(offset)),
                    f"{old_id}: independent read does not match the proof bytes and offset")
            proof = dict(zip(gate.PROOF_COLS, (eid, rid, gate.claim_sha256(row), cap, stamp, sha(body), str(offset),
                         reading["verdict"], reading["reader_family"], reading["reader_date"])))
            problem = gate.proof_problem(proof, row, idx, idx, archive, date.fromisoformat(observed), "openai", lambda _: body)
            require(not problem, f"{old_id}: {problem}")
            proofs.append(proof)
        new_rows[datum.replace("data/", "data/evidence_", 1)].append(row)
        return eid

    actions = unique(parse(packet[PRESS_ACTIONS].read_bytes()), lambda r: r["evidence_id"], "press actions")
    for old, (_, rule) in PRESS.items():
        a = actions[old]
        require(a["action"] == "HOLD_FOR_CONTROLLER" and a["source_class"] == "press",
                f"{old}: prior press route disposition differs")
        held = evidence[old]
        add(old, "organizations", a["record_id"], "existence", "press", a["new_source_ref"], held["tier_effect"],
            "dated notice of the held operator; ", gate.norm_space(a["quote"]), rule=rule,
            cap=a["capture_ref"], body=files[press_paths[old]].read_bytes(),
            notes=f"Replacement for {old} after the press route was admitted. Existence claim only.")

    mitsu, shur = registry_quotes(files)
    add("EVD-421870", "organizations", "ORG-002080", "existence", "government_filing",
        "OSHA ITA CY2021 establishment id 356540", "supports_B", "", mitsu,
        rule="ita_cy2021_unique_prefix_and_establishment", observed="2021-12-31",
        notes="Replacement for EVD-421870. CY2017 ITA establishment id 356540 confirms the untruncated name at the same site. Retrieved 2026-11-23.")
    add("EVD-422344", "sites", "SITE-000610", "address", "registry",
        "OSHA ITA CY2017 establishment id 67077; EPA FRS 110039084558", "supports_U", "place only; ", shur,
        rule="blank_street_registry", notes="Replacement for EVD-422344. Matched street in raw/osha/2026-11-22-archive-snapshot/raw/ita/ITA_Data_CY2017.zip and raw/epa-frs/2026-11-20-state-single/state_single_oh.zip. No canonical site street is asserted.")

    seco = files[lincoln_path].read_bytes()
    cik, _, quote, text = gate.edgar_business(seco, "submissions")
    sec_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    lincoln = next(r for r in parse(packet[EDGAR_READ].read_bytes()) if r["evidence_id"] == "EVD-420042")
    require(cik == "0000059527" and lincoln["verdict"] == "VERIFIED"
            and lincoln["capture_ref"] == sec_url, "Lincoln sealed EDGAR reading differs")
    add("EVD-420042", "sites", "SITE-000154", "address", "government_filing", f"SEC EDGAR {sec_url}",
        "supports_C", "headquarters business address, filing CIK 0000059527; ", quote, rule="sec_edgar",
        cap=sec_url, body=seco, offset=text.index(quote), role="physical",
        notes="Replacement for EVD-420042. The SEC business block gives the postal city and held ZIP.")

    kent = next(r for r in parse(packet[KENT_READ].read_bytes()) if r["record_id"] == "ORG-000503"
                and r["field"] == "polymer_program_name")
    ekey, pkey = ("ecosystem", "ORG-000503"), ("programs", "PROG-000014")
    old = records[pkey][1]["program_name"]
    corrected = "Characterization Facility"
    rollup = records[ekey][1]["polymer_program_name"].split("; ")
    require(old == "Kent State AMLCI Characterization Facility" and rollup.count(old) == 1
            and kent["verdict"] == "REJECT" and kent["source_url"] == KENT_URL, "Kent correction pin differs")
    new_rollup = "; ".join(corrected if value == old else value for value in rollup)
    require(new_rollup == kent["correct_value"], "Kent package rollup differs from corrected program name")
    kent_id = add("PROG-000014", *pkey, "existence", "own_site", KENT_URL, "supports_A",
                  "program_name Characterization Facility; ", KENT_QUOTE, rule="mechanics_clear",
                  cap=KENT_CAP, body=files[kent_path].read_bytes(),
                  notes="Kent State's own heading names the existing facility.")
    edits = {(*ekey, "polymer_program_name"): new_rollup, (*pkey, "program_name"): corrected}
    for k in edits:
        claim(*k, kent_id)
    data = expected_data(BASE, records, edits, [])
    for path, rows in {**new_rows, "data/archive_links.csv": archives}.items():
        existing = git("show", f"{BASE}:{path}")
        require(existing.endswith(b"\n"), f"{path}: append would run into the last row")
        data[path] = existing + csv_bytes(rows, parse(existing).fieldnames, with_header=False)
    holds = [r for eid, r in admission.items() if eid not in ADMITTED]
    require(len(claims) == 7 and sum(map(len, new_rows.values())) == 6 and len(archives) == 3
            and len(proofs) == 4 and len(holds) == 13, "Case reconciliation differs")
    artifacts = {
        "CLAIMS_CHECKED.csv": csv_bytes(claims, CLAIM_HEADER),
        "BINDING_PROOF.csv": csv_bytes(proofs, gate.PROOF_COLS),
        "REMAINING_RE_ADMISSION.csv": csv_bytes(holds, ("evidence_id", "record_id", "gate_extension")),
    }
    return data, artifacts


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--at", default="HEAD")
    ap.add_argument("--persist", type=Path, default=PERSIST)
    ap.add_argument("--store", type=Path, default=STORE)
    ap.add_argument("--apply-backup", type=Path)
    a = ap.parse_args()
    data, proofs = expected(a.persist, a.store)
    if a.apply_backup:
        a.apply_backup.mkdir(parents=True, exist_ok=True)
        for path, content in data.items():
            before = git("show", f"{BASE}:{path}")
            backup = a.apply_backup / Path(path).name
            require((ROOT / path).read_bytes() in (before, content), f"{path}: unrelated changes present")
            require(not backup.exists() or backup.read_bytes() == before, f"{path}: backup differs")
            backup.write_bytes(before)
        for path, content in data.items():
            (ROOT / path).write_bytes(content)
        for path, content in proofs.items():
            (HERE / path).write_bytes(content)
    else:
        delta = set(git("diff", "--name-only", BASE, a.at, "--", "data/").decode().splitlines())
        require(delta == data.keys(), "Canonical paths differ")
        for path, contents in {**data, **{f"{HERE.relative_to(ROOT)}/{k}": v for k, v in proofs.items()}}.items():
            require(git("show", f"{a.at}:{path}") == contents, f"{path}: applied bytes differ")
    print("PASS: 7 corrected claims, 2 changed fields, 6 appended witnesses, 3 archive links, 13 carried cases")


if __name__ == "__main__":
    main()
