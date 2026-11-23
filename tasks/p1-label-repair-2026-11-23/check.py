#!/usr/bin/env python3
"""Replay the sealed ATLAS-38 repairs through the current canonical shards."""
import argparse
from collections import Counter, defaultdict
import io
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "7ddcc37c590d775b1dd3b097e0664e4639119c9c"
PACKET = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/p1-label-repair-2026-11-23"
CLAIMS = ("table", "record_id", "field", "verdict", "evidence_id")

prior = runpy.run_path(str(HERE.parent / "p1-atlas8-corrections-2026-11-23/check.py"))
git, parse, require, sha, unique, csv_bytes = (
    prior[k] for k in ("git", "parse", "require", "sha", "unique", "csv_bytes")
)


def artifact(name, ref):
    path = HERE / name
    return git("show", f"{ref}:{path.relative_to(ROOT)}") if ref else path.read_bytes()


def lane_verification(packet, ref):
    manifest = artifact("PACKET.sha256", ref)
    require(manifest == (packet / "SHA256SUMS").read_bytes(), "Controller packet seal changed")
    files = {}
    for line in manifest.decode().splitlines():
        digest, filename = line.split("  ", 1)
        require(filename not in files and Path(filename).name == filename, "Invalid packet manifest path")
        raw = (packet / filename).read_bytes()
        require(sha(raw) == digest, f"Packet hash mismatch: {filename}")
        files[filename] = raw
    require(set(files) == {"README.md", "check.py", "edits.csv", "holds.csv", "counts.csv",
                           "reader-sample.csv", "researcher-sample.csv", "people-contact-counts.csv"},
            "Incomplete packet seal")
    lane = runpy.run_path(str(packet / "check.py"))
    rx = lane["scan_regex"](ROOT)
    lane["self_test"](rx)
    try:
        lane["packet_run"](ROOT, rx, False)
    except ValueError as exc:
        require(str(exc) == "FAIL strict in-scope scan: 830 unapproved hits remain", str(exc))
    else:
        require(False, "Pinned packet no longer reports the expected strict-scan result")
    return lane, rx, files


def expected(packet, ref=None):
    lane, rx, files = lane_verification(packet, ref)
    rows_at = lane["rows_at"]
    edits = unique(parse(files["edits.csv"]), lambda e: tuple(e[k] for k in CLAIMS[:3]), "repair")
    require(Counter(e["rule"] for e in edits.values()) ==
            {"naics_named_source": 1338, "naics_researcher_assignment": 405,
             "delete_build_wording": 143, "remove_contact_citation": 1}, "Unexpected repair counts")
    record_fields = defaultdict(dict)
    for (table, rid, field), edit in edits.items():
        record_fields[table, rid][field] = edit
    pin = lane["PIN"]
    archive_keys = {str(i): rid for i, (_, rid, _, _) in enumerate(rows_at(ROOT, pin, "archive_links"), 1)}
    approved = lane["approvals"](lane["APPROVAL"] / "approved.csv", archive_keys)
    withheld = lane["approvals"](lane["APPROVAL"] / "withheld.csv", archive_keys)
    approved_keys = {key for key, _ in approved}
    related = {"naics_primary", "naics_primary_source_type", "naics_confidence"}
    pinned_types = {rid: {field: row[field] for field in related}
                    for _, rid, row, _ in rows_at(ROOT, pin, "organizations")
                    if (("organizations", rid, lane["NAICS"]) in edits)}
    plans, seen, holds, people, tiers = defaultdict(dict), set(), [], Counter(), Counter()
    for table, rid, row, loc in rows_at(ROOT, BASE):
        path, line = loc.rsplit(":", 1)
        override = record_fields.get((table, rid), {})
        for field, e in override.items():
            key = table, rid, field
            before = row[field]
            digest = "sha256:" + sha(before.encode("utf-8"))
            contact = key == lane["CONTACT_KEY"] and e["rule"] == lane["CONTACT_RULE"]
            require((contact and e == lane["privacy_edit"](key, row) and digest == e["old"]) or
                    (not contact and not e["old"].startswith("sha256:") and before == e["old"]),
                    f"{loc} {field}: old-cell verification failed")
            require(key not in approved_keys and (key, e["new"]) not in withheld,
                    f"{loc} {field}: exact approval conflict")
            if field == lane["NAICS"]:
                require({f: row[f] for f in related} == pinned_types[rid],
                        f"{loc}: NAICS code, class or confidence drifted")
            require(e["new"] and e["new"] != before, f"{loc} {field}: empty or no-op replacement")
            seen.add(key)
            tiers[table, row["verification_tier"]] += 1
            plans[path].setdefault(int(line), {})[field] = e["new"]
        for field, old in row.items():
            key = table, rid, field
            value = override[field]["new"] if field in override else old
            if table == "people":
                people["before"] += lane["person_contact"](old)
                people["after"] += lane["person_contact"](value)
            if value and lane["in_scope"](table, field) and (rx.search(value) or (key, value) in withheld):
                if (key, value) in approved:
                    continue
                reason = lane["hold_reason"](table, field, (key, value) in withheld, key in approved_keys, row)
                source_type = row["naics_primary_source_type"] if field == lane["NAICS"] else ""
                holds.append(dict(zip(lane["HOLD"], (table, "" if table == "people" else rid, field, loc,
                                                    source_type, reason))))
    scopes = Counter(h["naics_source_type"] for h in holds)
    require(seen == edits.keys() and (people["before"], people["after"]) == (1, 0), "Repair or contact count differs")
    require(scopes == {"company_disclosed": 410, "government_filing": 149, "directory_assigned": 43,
                       "own_site": 1, "": 227}, "Current descriptive hold census differs from packet")
    def hold_key(row):
        return tuple(row[k] for k in lane["HOLD"] if k != "location")
    require(Counter(map(hold_key, holds)) == Counter(map(hold_key, parse(files["holds.csv"]))),
            "Current descriptive hold identities differ from the packet")

    output = {}
    for path, edits_by_line in plans.items():
        original = git("show", f"{BASE}:{path}")
        reader = parse(original)
        lines = list(io.StringIO(original.decode(), newline=""))
        chunks, end, applied = [lines[0].encode()], 1, set()
        for row in reader:
            start, end = end, reader.line_num
            if end in edits_by_line:
                row.update(edits_by_line[end])
                chunk = csv_bytes([row], reader.fieldnames, with_header=False)
                require(chunk.count(b"\n") == end - start, f"{path}:{end}: line locator drift")
                applied.add(end)
            else:
                chunk = "".join(lines[start:end]).encode()
            chunks.append(chunk)
        require(applied == edits_by_line.keys(), f"{path}: some corrections were not applied")
        output[path] = b"".join(chunks)
    ledger = [dict(zip(CLAIMS, (*key, "corrected", ""))) for key in sorted(seen)]
    artifacts = {"CLAIMS_CHECKED.csv": csv_bytes(ledger, CLAIMS),
                 "OPEN_QUEUE.csv": csv_bytes(holds, lane["HOLD"])}
    return output, artifacts, tiers


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--at", default="HEAD")
    ap.add_argument("--packet", type=Path, default=PACKET)
    args = ap.parse_args()
    data, artifacts, tiers = expected(args.packet, args.at)
    actual = set(git("diff", "--name-only", BASE, args.at, "--", "data/").decode().splitlines())
    require(actual == data.keys(), "Unexpected changed data paths")
    for path, value in data.items():
        require(git("show", f"{args.at}:{path}") == value, f"{path}: unexpected canonical delta")
    for name, value in artifacts.items():
        require(artifact(name, args.at) == value, f"{name}: ledger differs from current-base replay")
    print("PASS: 1,887 corrected cells and 830 descriptive holds; people contact cells 1 -> 0")
    print("Corrected cells by table and verification tier:", sorted(tiers.items()))


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        sys.exit(str(exc))
