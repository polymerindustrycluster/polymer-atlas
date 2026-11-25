#!/usr/bin/env python3
"""Apply the HQ repair to a clean checkout of origin/main (run once), then write the packet files.

Reads data/ from the working tree, so run it only on an unedited tree. The Kenda capture bytes come from the
shared store (put there by the first run); the proof fields are computed from them, never typed.
"""
import csv, hashlib, io, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate

TASK = HERE.name
LABEL = f"claude-code {TASK}"
OBSERVED = "2026-11-25"
CAPTURE = "https://web.archive.org/web/20260519034412id_/https://www.kendatire.com/en-us/locations/"
CAP_DATE = "2026-05-19"
SOURCE = "https://www.kendatire.com/en-us/locations/"
QUOTE = "Kenda American Technology Center 5801 Mayfair Road N. Canton , OH 44720 United States"
EVD = "EVD-483143"
KENDA = "ORG-000197"
# Cleared: no readable own-site or filing statement of the HQ within the effort cap (README, "Cleared").
CLEARED = {"ORG-000022": "Summit", "ORG-000033": "Summit", "ORG-000050": "Portage", "ORG-000073": "Summit",
           "ORG-000186": "Cuyahoga", "ORG-000202": "Lorain", "ORG-003703": "GA"}
KENDA_CELLS = dict(hq_city="Green", hq_state="OH", hq_country="US", hq_in_scope="ne_ohio")
READER = ("OpenAI Codex", "2026-11-25")  # filled from the reading recorded in README


def load(name):
    with (ROOT / "data" / f"{name}.csv").open(newline="") as f:
        return list(csv.reader(f))


def save(name, rows):
    with (ROOT / "data" / f"{name}.csv").open("w", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)


def main(reader_family, reader_date):
    capture = (STORE / "provenance" / TASK).glob("*.html")
    body = gate.fetch_url(CAPTURE)
    sha = hashlib.sha256(body).hexdigest()
    dest = STORE / "provenance" / TASK / f"{sha}.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    offset = gate.capture_text(body).find(QUOTE)
    assert offset >= 0 and gate.capture_text(body).count(QUOTE) == 1

    us = load("organizations_US")
    head, key = us[0], {c: i for i, c in enumerate(us[0])}
    cleared, kenda_row = [], None
    for row in us[1:]:
        if row[0] in CLEARED:
            assert row[key["hq_county"]] == CLEARED[row[0]] and not row[key["hq_city"]] and not row[key["hq_state"]]
            row[key["hq_county"]] = ""
        if row[0] == KENDA:
            assert row[key["hq_county"]] == "Summit" and not any(row[key[k]] for k in KENDA_CELLS)
            for k, v in KENDA_CELLS.items():
                row[key[k]] = v
            kenda_row = row
            continue
        cleared.append(row)
    save("organizations_US", [head] + cleared)
    oh = load("organizations_OH")
    assert oh[0] == head
    oh = [head] + sorted(oh[1:] + [kenda_row], key=lambda r: r[0])
    save("organizations_OH", oh)

    evs = load("evidence_organizations_US")
    ek = {c: i for i, c in enumerate(evs[0])}
    moved = [r for r in evs[1:] if r[ek["record_id"]] == KENDA]
    assert [r[0] for r in moved] == ["EVD-421274"]
    save("evidence_organizations_US", [evs[0]] + [r for r in evs[1:] if r not in moved])
    new = {c: "" for c in evs[0]}
    new.update(evidence_id=EVD, record_table="organizations", record_id=KENDA, claim_type="address",
               claim_detail=("Own address of the Atlas record: street 5801 Mayfair Road, ZIP 44720, Ohio; the printed city N. Canton is "
                             "the USPS mailing city, the record's physical city is Green (parcel evidence in the record's notes); "
                             "live page and Wayback capture 2026-05-19 agree; quote: " + QUOTE),
               source_class="own_site", source_ref=SOURCE, observed_date=OBSERVED, tier_effect="supports_B",
               created_by=LABEL, notes="Exact-body reading by a non-Claude family; see BINDING_PROOF.csv.", address_role="physical")
    eoh = load("evidence_organizations_OH")
    assert eoh[0] == evs[0]
    save("evidence_organizations_OH", eoh + moved + [[new[c] for c in evs[0]]])
    arch = load("archive_links")
    arch.append([EVD, CAPTURE.replace("id_/", "/", 1), CAP_DATE, LABEL])
    save("archive_links", arch)

    ev = dict(zip(evs[0], [new[c] for c in evs[0]]))
    proof = [EVD, KENDA, gate.claim_sha256(ev), CAPTURE, CAP_DATE, sha, str(offset), "VERIFIED", reader_family, reader_date]
    with (HERE / "BINDING_PROOF.csv").open("w", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows([list(gate.PROOF_COLS), proof])
    (HERE / "INPUTS.sha256").write_text(f"{sha}  provenance/{TASK}/{sha}.html\n")
    claims = [["table", "record_id", "field", "verdict", "evidence_id"]]
    claims += [["organizations", KENDA, k, "corrected", EVD] for k in KENDA_CELLS]
    claims += [["organizations", i, "hq_county", "withdrawn", ""] for i in CLEARED]
    with (HERE / "CLAIMS_CHECKED.csv").open("w", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(claims)
    print("built; capture", sha, "offset", offset)


if __name__ == "__main__":
    main(*sys.argv[1:3])
