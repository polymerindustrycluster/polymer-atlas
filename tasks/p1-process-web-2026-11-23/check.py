#!/usr/bin/env python3
"""Replay the admitted process claims, held capture bytes, and entire data delta."""
import argparse
import csv
from collections import Counter, defaultdict
from datetime import date, datetime
import io
from pathlib import Path
import re
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "0b191fe6"
FIRST_ID = 483026
DAY = "2026-11-23"
LABEL = f"codex {HERE.name}"
HOLD = {"P3-000009", "P3-000010"}
HOSTED_ARCHIVED_PROOF = {"P3-000006", "P3-000007", "P3-000017", "P3-000018"}
ARCHIVED_PROOF = {"P3-000003", "P3-000004", "P3-000005"} | HOSTED_ARCHIVED_PROOF
REFRESHED = {"P3-000001", "P3-000002", "P3-000003", "P3-000004", "P3-000005",
             "P3-000008", "P3-000016", "P3-000017", "P3-000018"}
PACKET = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/process-web-scale-2026-11-23"
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
PROVENANCE = "provenance/process-web-2026-11-23/captures/"
WAYBACK_PROVENANCE = "provenance/process-web-2026-11-23-wayback/captures/"
HOSTED_WAYBACK_PROVENANCE = "provenance/process-web-2026-11-23-wayback-2/captures/"
CLAIMS = ("table", "record_id", "field", "verdict", "evidence_id")
QUEUE = ("packet_id", "table", "record_id", "field", "term", "settling_fact")

prior = runpy.run_path(str(HERE.parent / "p1-atlas8-corrections-2026-11-23/check.py"))
csv_bytes, git, parse, require, sha, unique = (
    prior[k] for k in ("csv_bytes", "git", "parse", "require", "sha", "unique")
)
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate
from regions import PIC18


def read_manifest(name, folder):
    result = {}
    for line in (HERE / name).read_text().splitlines():
        digest, rel = line.split("  ", 1)
        require(rel not in result, f"{name}: duplicate {rel}")
        raw = (folder / rel).read_bytes()
        require(sha(raw) == digest, f"{name}: bad hash for {rel}")
        result[rel] = raw
    return result


def record_path(row):
    return row["_at"].rsplit(":", 1)[0]


def census(idx, changes):
    owners = defaultdict(list)
    for site in idx.sites.values():
        if (site["state"] == "OH" and site["county"] in PIC18 and site["operating_status"] == "active"
                and site["verification_tier"] in ("A", "B", "C")):
            owners[site["org_id"]].append(site)
    unknown = set()
    for oid, sites in owners.items():
        rows = sites + [idx.orgs.get(oid, {})]
        cells = [changes.get(r.get("site_id") or oid, r.get("processes", "")) for r in rows]
        if not any(set(re.split(r";\s*", cell)) - {"", "unknown"} for cell in cells):
            unknown.add(oid)
    return len(owners), unknown


def build(packet, store, idx):
    inputs = read_manifest("PACKET.sha256", packet)
    observations = unique(parse(inputs["proposed_evidence.csv"]), lambda r: r["evidence_id"], "packet evidence")
    prior_proofs = unique(parse(inputs["BINDING_PROOF.csv"]), lambda r: r["evidence_id"], "packet proofs")
    proposed = list(parse(inputs["candidates.csv"]))
    selected = unique(parse((HERE / "CAPTURES.csv").read_bytes()), lambda r: r["evidence_id"], "capture selection")
    require(len(observations) == len(proposed) == 18 and observations.keys() == prior_proofs.keys(),
            "packet count or keys differ")
    require(selected.keys() == observations.keys() - HOLD, "held and selected dispositions differ from the ruling")
    releases = unique(parse((HERE / "ARCHIVES.csv").read_bytes()), lambda r: r["packet_id"], "archive receipts")
    require(releases and releases.keys() <= selected.keys(), "missing or ineligible archive receipt")
    dispositions = unique(parse((HERE / "HELD_REASONS.csv").read_bytes()), lambda r: r["packet_id"], "held receipts")
    require(dispositions.keys() <= observations.keys() - releases.keys() and all(
        r["settling_fact"] for r in dispositions.values()), "held reasons overlap admitted rows or are incomplete")
    archives, queue, captured = [], [], {}
    site_count = Counter(s["org_id"] for s in idx.sites.values())
    evidence, terms, proofs = defaultdict(list), defaultdict(list), []
    coverage, counts = set(), Counter()
    changes = {}
    claims = []
    for original, candidate in zip(observations.values(), proposed):
        local = original["evidence_id"]
        term = candidate["proposed_term"]
        table, rid = original["record_table"], original["record_id"]
        old_proof = prior_proofs[local]
        require(rid == (candidate["site_id"] or candidate["org_id"]) == old_proof["record_id"]
                and table == ("sites" if candidate["site_id"] else "organizations")
                and original["claim_detail"] == f"processes={term}; quote: {candidate['quote']}"
                and old_proof["claim_sha256"] == gate.claim_sha256(original), f"{local}: packet join")
        receipt = releases.get(local)
        if not receipt or (local in ARCHIVED_PROOF and not receipt["proof_sha256"]):
            if local in dispositions:
                settling = dispositions[local]["settling_fact"]
            elif local in HOLD:
                settling = "a capture whose bytes are stable across two gate fetches, or a held route"
            elif local in ARCHIVED_PROOF:
                settling = "a dated Wayback capture with an exact-byte proof and a Sonnet reading"
            else:
                settling = "a Wayback capture of the cited page for the archive-at-capture requirement"
            queue.append(dict(zip(QUEUE, (local, table, rid, "processes", term, settling))))
            continue
        archive = gate.ARCHIVE_RE.fullmatch(receipt["archive_ref"])
        require(archive is not None and archive[2] is None and gate.same_page(archive[3], original["source_ref"])
                and datetime.strptime(archive[1], "%Y%m%d%H%M%S").date().isoformat() == receipt["captured_at"]
                and receipt["captured_at"] <= DAY and receipt["capture_creator"],
                f"{local}: archive URL, date or creator differs")
        record = idx.record(table, rid)
        require(record is not None and record["processes"] == ""
                and original["tier_effect"] == "supports_" + record["verification_tier"],
                f"{local}: base cell or tier changed")
        owner = candidate["org_id"]
        if table == "sites":
            require(record["org_id"] == owner and (site_count[owner] == 1 or candidate["plant_city"] == record["city"]),
                    f"{local}: site grain")
        h, offset = (selected[local][f] for f in ("capture_sha256", "quote_offset"))
        eid = f"EVD-{FIRST_ID + len(proofs):06d}"
        row = dict(original, evidence_id=eid, created_by=LABEL)
        proof = dict(old_proof, evidence_id=eid, verdict="VERIFIED", reader_family="Claude Sonnet", reader_date=DAY)
        arc = dict(evidence_id=eid, archive_ref=receipt["archive_ref"], captured_at=receipt["captured_at"],
                   created_by=receipt["capture_creator"])
        if receipt["proof_sha256"]:
            h, offset = receipt["proof_sha256"], receipt["proof_offset"]
            row["claim_detail"] = row["claim_detail"].replace("; quote:", " (Wayback capture); quote:", 1)
            proof.update(capture=receipt["archive_ref"].replace(archive[1] + "/", archive[1] + "id_/", 1),
                         capture_date=receipt["captured_at"], claim_sha256=gate.claim_sha256(row))
        else:
            require(offset == old_proof["quote_offset"] and not gate.ARCHIVE_RE.fullmatch(old_proof["capture"]),
                    f"{local}: offset or live route changed")
            require((h != old_proof["capture_sha256"]) == (local in REFRESHED), f"{local}: unreviewed refresh")
            if local in REFRESHED:
                proof["capture_date"] = DAY
        proof.update(capture_sha256=h, quote_offset=offset)
        require(re.fullmatch(r"[a-f0-9]{64}", h), f"{local}: bad capture digest")
        capture_folder = PROVENANCE
        if receipt["proof_sha256"]:
            capture_folder = HOSTED_WAYBACK_PROVENANCE if local in HOSTED_ARCHIVED_PROOF else WAYBACK_PROVENANCE
        capture_path = f"{capture_folder}{h}.html"
        if capture_path not in captured:
            captured[capture_path] = (store / capture_path).read_bytes()
        raw = captured[capture_path]
        require(sha(raw) == h, f"{local}: archive or live capture hash mismatch")
        if local in REFRESHED and not receipt["proof_sha256"]:
            sealed = (packet / "captures" / f"{old_proof['capture_sha256']}.html").read_bytes()
            require(sha(sealed) == old_proof["capture_sha256"]
                    and gate.capture_text(sealed) == gate.capture_text(raw), f"{local}: refreshed main text changed")
        require(gate.judge(row, idx)[:2] == ("READ_REQUIRED", "mechanics_clear"), f"{local}: binding mechanics")
        fault = gate.proof_problem(proof, row, idx, idx, arc, date.fromisoformat(DAY), "openai", lambda _: raw)
        require(not fault, f"{local}: capture replay {fault}")
        if not proofs:
            bad = dict(proof, quote_offset=str(int(offset) + 1))
            require(gate.proof_problem(bad, row, idx, idx, arc, date.fromisoformat(DAY), "openai", lambda _: raw)
                    == "the quote is not at that offset in the capture's main text", "shifted offset escaped")
        proofs.append(proof)
        archives.append(arc)
        path = record_path(record)
        evidence[Path(path).with_name("evidence_" + Path(path).name)].append(row)
        terms[(path, table, rid)].append((term, eid))
        coverage.add(owner)
        counts[table, record["verification_tier"]] += 1
    for (path, table, rid), requested in terms.items():
        labels = [term for term, _ in requested]
        require(len(set(labels)) == len(labels), f"{rid}: duplicate process term")
        changes[rid] = ";".join(labels)
        claims.append(dict(zip(CLAIMS, (table, rid, "processes", "corrected", requested[0][1]))))
    require(len(proofs) > 0 and len(proofs) == len(archives) and len(proofs) + len(queue) == 18,
            "admitted and held rows must partition the original 18")
    require(coverage <= census(idx, {})[1], "the packet admits an already-known owner")
    n, before = census(idx, {})
    m, after = census(idx, changes)
    require(n == m == 794 and len(before) == 320 and before - after == coverage,
            "PIC-18 process unknown denominator or yield differs")
    manifest = "".join(f"{sha(raw)}  {path}\n" for path, raw in sorted(captured.items())).encode()
    return evidence, terms, changes, proofs, claims, counts, archives, queue, manifest, len(after)


def base_bytes(path):
    return git("show", f"{BASE}:{path}")


def expected_data(evidence, terms, changes, archives):
    evidence[Path("data/archive_links.csv")] = archives
    by_path = defaultdict(set)
    for path, _, rid in terms:
        by_path[path].add(rid)
    expected = {}
    for path, ids in by_path.items():
        prior_bytes = base_bytes(path)
        lines = list(io.StringIO(prior_bytes.decode(), newline=""))
        reader = parse(prior_bytes)
        id_field = "site_id" if Path(path).name.startswith("sites_") else "org_id"
        parts = [lines[0].encode()]
        end = 1
        seen = set()
        for row in reader:
            start, end = end, reader.line_num
            rid = row[id_field]
            if rid in ids:
                row["processes"] = changes[rid]
                parts.append(csv_bytes([row], reader.fieldnames, with_header=False))
                seen.add(rid)
            else:
                parts.append("".join(lines[start:end]).encode())
        require(seen == ids, f"{path}: missing applied record")
        expected[path] = b"".join(parts)
    for path_obj, additions in evidence.items():
        path = str(path_obj)
        original = base_bytes(path)
        require(original.endswith(b"\n"), f"{path}: unexpected record terminator")
        expected[path] = original + csv_bytes(additions, parse(original).fieldnames, with_header=False)
    return expected


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--packets", type=Path, default=PACKET)
    ap.add_argument("--store", type=Path, default=STORE)
    ap.add_argument("--apply-backup", type=Path)
    ap.add_argument("--preview", action="store_true", help="check and count admissible rows without writing")
    args = ap.parse_args()
    require(git("merge-base", "HEAD", BASE) == git("rev-parse", BASE), "wrong application base")
    base_ids = gate.rows(BASE, "evidence_*.csv")
    require(FIRST_ID == max(int(r["evidence_id"].split("-")[1]) for r in base_ids) + 1, "evidence ID floor drift")
    evidence, terms, changes, proofs, claims, counts, archives, queue, manifest, unknown = build(
        args.packets, args.store, gate.Index.load(BASE))
    print(f"Replayed {len(proofs)} proofs and archives, {len(changes)} cells, {len(queue)} held. {dict(counts)}")
    print(f"PIC-18 process unknown 320 -> {unknown} of 794 owners. Planted shifted proof offset rejected.")
    if args.preview:
        return
    expected = expected_data(evidence, terms, changes, archives)
    artifacts = {
        HERE / "CLAIMS_CHECKED.csv": csv_bytes(claims, CLAIMS),
        HERE / "BINDING_PROOF.csv": csv_bytes(proofs, gate.PROOF_COLS),
        HERE / "OPEN_QUEUE.csv": csv_bytes(queue, QUEUE),
        HERE / "INPUTS.sha256": manifest,
    }
    if args.apply_backup:
        args.apply_backup.mkdir(parents=True, exist_ok=True)
        for path, result in expected.items():
            original = base_bytes(path)
            require((ROOT / path).read_bytes() in (original, result), f"{path}: independent edits")
            backup = args.apply_backup / Path(path).name
            require(not backup.exists() or backup.read_bytes() == original, f"{path}: backup differs")
            backup.write_bytes(original)
        for p, result in [(ROOT / path, result) for path, result in expected.items()] + list(artifacts.items()):
            pending = p.with_suffix(".pending")
            pending.write_bytes(result)
            pending.replace(p)
    changed = set(git("diff", "--name-only", BASE, "--", "data/").decode().splitlines())
    require(changed == expected.keys(), f"additional or missing canonical files: {sorted(changed ^ expected.keys())}")
    for p, data in ({ROOT / path: result for path, result in expected.items()} | artifacts).items():
        require(p.read_bytes() == data, f"{p.name}: differs from admitted delta")
    print("PASS: complete data and task artifact delta")


if __name__ == "__main__":
    main()
