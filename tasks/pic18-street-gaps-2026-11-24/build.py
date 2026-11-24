"""Apply the sealed street packet against the two pinned canonical shards."""
import csv
import io
import os
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = (HERE / "BASE").read_text().strip()
SITES = "data/sites_OH.csv"
EVIDENCE = "data/evidence_sites_OH.csv"
LABEL = f"codex {HERE.name}"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def read(data):
    return list(csv.DictReader(io.StringIO(data.decode(), newline="")))


def encode(rows, header, line_end):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, list(rows[0]), lineterminator=line_end)
    if header:
        writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def evidence(fill):
    kind = fill["kind"]
    assert kind in {"inspection", "ita"}
    label = ("OSHA inspection" if kind == "inspection"
             else f"OSHA ITA Form 300A CY{fill['date'][:4]} establishment")
    addr = f"{fill['street']}, {fill['city']}, OH {fill['zip']}"
    return dict(evidence_id=fill["evidence_id"], record_table="sites", record_id=fill["site_id"],
                claim_type="address", claim_detail=f"physical site street; quote: {fill['operator']}, {addr}",
                source_class="government_filing", source_ref=f"{label} {fill['source_id']}; {fill['ref']}",
                observed_date=fill["date"], tier_effect="supports_A", created_by=LABEL,
                notes=f"Filed operator field: {fill['operator_field']}. Read from the held extract on 2026-11-24.",
                address_role="physical")


def versions():
    old_sites = git("show", f"{BASE}:{SITES}")
    old_evidence = git("show", f"{BASE}:{EVIDENCE}")
    sites = read(old_sites)
    ending = "\r\n" if b"\r\n" in old_sites else "\n"
    assert encode(sites, True, ending) == old_sites, "base site CSV does not round-trip"
    assert old_evidence.endswith(b"\n"), "base evidence has no terminal newline"
    by_id = {s["site_id"]: s for s in sites}
    fills = read((HERE / "FILLS.csv").read_bytes())
    assert fills and len(fills) == len({f["site_id"] for f in fills}) == len({f["evidence_id"] for f in fills})
    for fill in fills:
        site = by_id[fill["site_id"]]
        assert not site["street_address"].strip()
        site["street_address"] = fill["street"]
        if fill["zip_fill"]:
            assert not site["zip"]
            site["zip"] = fill["zip_fill"]
    evidence_rows = [evidence(f) for f in fills]
    ending_ev = "\r\n" if old_evidence.endswith(b"\r\n") else "\n"
    return {SITES: (old_sites, encode(sites, True, ending)),
            EVIDENCE: (old_evidence, old_evidence + encode(evidence_rows, False, ending_ev))}


def main():
    planned = versions()
    staged = []
    try:
        for name, (old, updated) in planned.items():
            path = ROOT / name
            before = path.read_bytes()
            assert before in (old, updated), f"{name}: unexpected prior edits"
            if before == updated:
                continue
            with NamedTemporaryFile(dir=path.parent, delete=False) as stream:
                staged.append((Path(stream.name), path))
                stream.write(updated)
                stream.flush()
                os.fsync(stream.fileno())
        for tmp, path in staged:
            os.chmod(tmp, path.stat().st_mode & 0o777)
            tmp.replace(path)
    finally:
        for tmp, _ in staged:
            tmp.unlink(missing_ok=True)
    print(f"Street packet applied to {len(staged)} shard(s)")


if __name__ == "__main__":
    main()
