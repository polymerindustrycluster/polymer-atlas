"""Build or replay a single append-only correction to the Salem address evidence."""
import argparse
import csv
import hashlib
import io
from itertools import islice
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = HERE.parent / "pic18-street-fill-2026-11-22"
sys.path.insert(0, str(PRIOR))
import build as prior
from matching import same_street

EVIDENCE = "data/evidence_sites_OH.csv"
SITE = "SITE-001455"
OLD = "EVD-483012"
ORDINAL = 352594


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def base_rows(base, path):
    return csv.DictReader(io.StringIO(git("show", f"{base}:{path}").decode(), newline=""))


def next_id(base):
    files = git("ls-tree", "--name-only", f"{base}:data").decode().splitlines()
    ids = [int(row["evidence_id"].removeprefix("EVD-"))
           for name in files if name.startswith("evidence_") and name.endswith(".csv")
           and name != "evidence_all.csv" for row in base_rows(base, "data/" + name)]
    assert len(ids) == len(set(ids)), "duplicate evidence IDs at base"
    return f"EVD-{max(ids) + 1:06d}"


def raw_witness():
    manifest = (HERE / "INPUTS.sha256").read_text()
    assert len(manifest.splitlines()) == 1 and manifest in (PRIOR / "INPUTS.sha256").read_text()
    expected_hash, relative = manifest.strip().split("  ")
    path = prior.STORE / relative
    with path.open("rb") as source:
        assert hashlib.file_digest(source, "sha256").hexdigest() == expected_hash, "ITA input SHA-256 mismatch"
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as source:
        raw = next(islice(csv.DictReader(source), ORDINAL - 1, None))
    entry, = prior.B.unify([raw], "ita")
    assert raw["state"] == "OH" and prior.dmy(raw["date_submitted"]) == "2026-02-27"
    witness = prior.witness("ita", f"{relative}@{ORDINAL}", entry["names"], entry["st"], entry["city"],
                            entry["zip"], prior.B.source_date(entry))
    return witness, raw["company_name"].strip()


def verify_operator(row, legal_name):
    operator = row["claim_detail"].split("quote: ", 1)[1].split(", ", 1)[0]
    assert operator == legal_name, "quoted operator differs from the held legal name"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    base = git("merge-base", "HEAD", "origin/main").decode().strip()
    site = next(r for r in base_rows(base, "data/sites_OH.csv") if r["site_id"] == SITE)
    org = next(r for r in base_rows(base, "data/organizations_OH.csv") if r["org_id"] == site["org_id"])
    old = next(r for r in base_rows(base, EVIDENCE) if r["evidence_id"] == OLD)
    assert old["record_id"] == SITE and old["claim_type"] == "address"
    assert "AMERICAN STANDARD INC." in old["claim_detail"]
    assert "licensed brand" in org["trade_names"]

    witness, operator = raw_witness()
    assert operator == org["legal_name"] == "American Bath Group"
    assert same_street(witness["street"], site["street_address"])
    assert (witness["city"], witness["zip"]) == (site["city"], site["zip"])

    row = prior.evidence(witness, operator, SITE)
    row.update(evidence_id=next_id(base), created_by=f"codex {HERE.name}",
               notes=f"Packet {HERE.name}; physical role; answers {OLD} (SCHEMA 4.13): "
                     "its quoted operator is the licensed brand the record says does not operate this plant.")
    verify_operator(row, org["legal_name"])
    bad = dict(row, claim_detail=row["claim_detail"].replace(operator, "AMERICAN STANDARD INC.", 1))
    try:
        verify_operator(bad, org["legal_name"])
    except AssertionError as exc:
        assert str(exc) == "quoted operator differs from the held legal name"
        print("PASS: planted licensed-brand quote rejected at the same street")
    else:
        raise AssertionError("planted licensed-brand operator escaped")

    original = git("show", f"{base}:{EVIDENCE}")
    assert original.endswith(b"\n")
    line = io.StringIO(newline="")
    csv.DictWriter(line, fieldnames=list(old), lineterminator="\n").writerow(row)
    expected = original + line.getvalue().encode()
    path = ROOT / EVIDENCE
    if args.apply and path.read_bytes() == original:
        backup = Path(os.environ["BB_THREAD_STORAGE"]) / "sf-repair-evidence_sites_OH.before.csv"
        if backup.exists():
            assert backup.read_bytes() == original
        else:
            backup.write_bytes(original)
        pending = path.with_suffix(".tmp")
        pending.write_bytes(expected)
        pending.replace(path)
    assert path.read_bytes() == expected, "evidence shard must equal base plus the single replayed row"
    changed = git("diff", "--name-only", base, "--", "data").decode().splitlines()
    assert changed == [EVIDENCE], f"unexpected changed data: {changed}"
    print(f"PASS: {row['evidence_id']} reproduces from hashed ITA row {ORDINAL}, "
          f"binds to {SITE} and is the only data change")


if __name__ == "__main__":
    main()
