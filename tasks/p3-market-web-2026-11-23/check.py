#!/usr/bin/env python3
"""Replay the market packet, capture and archive attestations, and applied data."""
import argparse
from collections import Counter, defaultdict
from datetime import date, datetime
import io
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "66b39a5367b97304e063fe3e37e89474354f953c"
LABEL = HERE.name
DAY = date(2026, 11, 23)
PACKET = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist" / LABEL
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
CLAIMS = ("table", "record_id", "field", "verdict", "evidence_id")
QUEUE = ("packet_id", "record_id", "verdict", "settling_fact")
ROUTES = ("packet_id", "archive_ref", "archive_creator", "proof_capture", "proof_sha256", "quote_offset",
          "reader_family", "reader_date", "archive_sha256")

prior = runpy.run_path(str(HERE.parent / "p1-atlas8-corrections-2026-11-23/check.py"))
git, parse, require, sha, unique, csv_bytes = (
    prior[k] for k in ("git", "parse", "require", "sha", "unique", "csv_bytes")
)
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate
from regions import PIC18


def artifact(name, ref):
    f = HERE / name
    return git("show", f"{ref}:{f.relative_to(ROOT)}") if ref else f.read_bytes()


def manifest(data, folder):
    files = {}
    for line in data.decode().splitlines():
        digest, path = line.split("  ", 1)
        require(path not in files and not Path(path).is_absolute() and ".." not in Path(path).parts,
                f"unsafe or duplicate input path {path}")
        raw = (folder / path).read_bytes()
        require(sha(raw) == digest, f"hash mismatch: {path}")
        files[path] = raw
    return files


def market_tokens(value):
    return {term.strip() for term in value.split(";") if term.strip()} - {"unknown"}


def unknown_owners(idx, changes):
    qualifying = defaultdict(list)
    for s in idx.sites.values():
        if (s["state"] == "OH" and s["county"] in PIC18 and s["operating_status"] == "active"
                and s["verification_tier"] in ("A", "B", "C")):
            qualifying[s["org_id"]].append(s)
    missing = set()
    for oid, sites in qualifying.items():
        records = sites + [idx.orgs[oid]]
        if not any(market_tokens(changes.get(r.get("site_id") or oid, r.get("markets_served", ""))) for r in records):
            missing.add(oid)
    return len(qualifying), missing


def evidence_row(row, eid, capture):
    header = parse(git("show", f"{BASE}:data/evidence_organizations_OH.csv"))
    out = {key: row.get(key, "") for key in header.fieldnames}
    if capture != row["source_ref"]:
        out["claim_detail"] = row["claim_detail"].replace("; quote:", " (Wayback capture); quote:", 1)
        require(out["claim_detail"] != row["claim_detail"], f"{eid}: missing quote separator")
    out["evidence_id"] = eid
    out["created_by"] = LABEL
    return out


def edit_data(changes, evidence, archives, idx):
    by_record_file = defaultdict(dict)
    for rid, new in changes.items():
        record = idx.sites[rid] if rid.startswith("SITE-") else idx.orgs[rid]
        by_record_file[record["_at"].rsplit(":", 1)[0]][rid] = new
    output = {}
    for path, edits in by_record_file.items():
        existing = git("show", f"{BASE}:{path}")
        rows = parse(existing)
        lines = list(io.StringIO(existing.decode(), newline=""))
        chunks, end = [lines[0].encode()], 1
        seen = set()
        for row in rows:
            start, end = end, rows.line_num
            rid = row.get("site_id") or row["org_id"]
            if rid in edits:
                row["markets_served"] = edits[rid]
                chunks.append(csv_bytes([row], rows.fieldnames, with_header=False))
                seen.add(rid)
            else:
                chunks.append("".join(lines[start:end]).encode())
        require(seen == edits.keys(), f"{path}: missing changed record")
        output[path] = b"".join(chunks)
    for path, rows in dict(evidence, **{"data/archive_links.csv": archives}).items():
        before = git("show", f"{BASE}:{path}")
        require(before.endswith(b"\n"), f"{path}: no newline before append")
        output[path] = before + csv_bytes(rows, parse(before).fieldnames, with_header=False)
    return output


def unadmitted_reason(packet_id, reading):
    if packet_id == "P3-MKT-000007":
        return "held", "A public archive copy carrying the verified own-site quote."
    if reading["verdict"] == "REJECT":
        if packet_id == "P3-MKT-000031":
            return "rejected", "The cited statement is attributed to a partner in a customer story."
        return "rejected", "The group wording fails operator binding and the proposed market term."
    if packet_id == "P3-MKT-000010":
        return "held", "A current first-party statement naming the market served by this operator."
    if packet_id == "P3-MKT-000019":
        return "held", "An owner ruling on the section 3.3 term for electrical-utility customers."
    if reading["BINDING"] == "HOLD":
        return "held", "An operator-specific statement tying the published market to the regional organization."
    return "held", "An explicit end-market statement mapping to the proposed SCHEMA section 3.3 term."


def expected(packet, store, ref=None):
    source = manifest(artifact("PACKET.sha256", ref), packet)
    candidates = unique(parse(source["candidates.csv"]), lambda r: r["evidence_id"], "candidate")
    first, scale = (list(parse(source[name])) for name in ("reading-first.csv", "reading-scale.csv"))
    votes = unique(first + scale, lambda r: r["evidence_id"], "reader verdict")
    require(len(first) == 8 and len(scale) == 32 and votes.keys() == candidates.keys()
            and Counter(r["verdict"] for r in votes.values()) == {"VERIFIED": 29, "STILL_UNCERTAIN": 9, "REJECT": 2},
            "sealed verdict population differs")
    release = unique(parse(artifact("CAPTURE_READS.csv", ref)), lambda r: r["packet_id"], "read attestations")
    verified = {k for k, v in votes.items() if v["verdict"] == "VERIFIED"}
    require(release.keys() == verified - {"P3-MKT-000007"}, "unapproved candidate admission or hold")
    receipts = unique(parse(source["ARCHIVE_STATUS.csv"]), lambda r: r["source_ref"], "archive receipts")
    bodies = manifest(artifact("INPUTS.sha256", ref), store)
    captures = {sha(x): x for x in bodies.values()}
    require(captures.keys() == {r[k] for r in release.values() for k in ("proof_sha256", "archive_sha256")},
            "capture manifest keys differ")
    idx = gate.Index.load(BASE)
    frame = unique(parse(source["frame.csv"]), lambda r: r["org_id"], "packet frame")
    denominator, before = unknown_owners(idx, {})
    require(denominator == 794 and before == frame.keys() and len(before) == 316, "corrected-base frame differs")
    terms_doc = git("show", f"{BASE}:docs/SCHEMA.md").decode()
    vocab = set(re.findall(r"`([a-z][a-z0-9_]+)`", terms_doc.split("### 3.3 Markets Served", 1)[1].split("### 3.4", 1)[0]))
    base_evs = unique(gate.rows(BASE, "evidence_*.csv"), lambda r: r["evidence_id"], "existing evidence")
    archive_ids = {r["evidence_id"] for r in gate.rows(BASE, "archive_links.csv")}
    floor = max(int(k[4:]) for k in base_evs.keys() | archive_ids)
    require(floor == 483065, "evidence allocator base differs")
    archives, proofs, queue = [], [], []
    evidence, markets, handles = defaultdict(list), defaultdict(list), defaultdict(list)
    tiers, owners = Counter(), set()
    for packet_id, row in candidates.items():
        reading = votes[packet_id]
        if packet_id not in release:
            verdict, fact = unadmitted_reason(packet_id, reading)
            queue.append(dict(zip(QUEUE, (packet_id, row["record_id"], verdict, fact))))
            continue
        route = release[packet_id]
        arc_url = route["archive_ref"]
        match = gate.ARCHIVE_RE.fullmatch(arc_url)
        original = receipts[row["source_ref"]]
        require(original["status"] == "success" and match and not match[2]
                and gate.same_page(match[3], row["source_ref"]), f"{packet_id}: wrong archive page")
        require(route["archive_creator"] in (LABEL, "unknown"), f"{packet_id}: inconsistent capture creator")
        if route["archive_creator"] == LABEL:
            require(arc_url == original["archive_ref"] and original["job_id"], f"{packet_id}: no capture creator receipt")
        cap_day = datetime.strptime(match[1], "%Y%m%d%H%M%S").date().isoformat()
        cap = route["proof_capture"]
        archive_raw = captures[route["archive_sha256"]]
        require(row["quote"] in gate.capture_text(archive_raw), f"{packet_id}: archive proof quote absent")
        require(cap == row["source_ref"] or cap == arc_url.replace(match[1]+"/",match[1]+"id_/",1),
                f"{packet_id}: wrong public proof route")
        if cap != row["source_ref"]:
            require(route["proof_sha256"] == route["archive_sha256"], f"{packet_id}: archive proof body differs")
        rid, table, term = (row[k] for k in ("record_id", "record_table", "term"))
        record = idx.record(table, rid)
        owner = row["org_id"]
        require(record and owner in before and not market_tokens(record["markets_served"]) and term in vocab
                and row["tier_effect"] == "supports_" + record["verification_tier"],
                f"{packet_id}: changed scope, vocabulary or tier")
        require((record["org_id"] == owner and row["site_id"] == rid) if table == "sites"
                else table == "organizations" and rid == owner and not row["site_id"], f"{packet_id}: grain changed")
        eid = f"EVD-{floor + 1 + len(proofs):06d}"
        ev = evidence_row(row, eid, cap)
        arc = dict(evidence_id=eid, archive_ref=arc_url, captured_at=cap_day, created_by=route["archive_creator"])
        proof = dict(evidence_id=eid, record_id=rid, claim_sha256=gate.claim_sha256(ev),
                     capture=cap, capture_date=cap_day if cap != row["source_ref"] else DAY.isoformat(),
                     capture_sha256=route["proof_sha256"], quote_offset=route["quote_offset"], verdict="VERIFIED",
                     reader_family=route["reader_family"], reader_date=route["reader_date"])
        require(gate.judge(ev, idx)[:2] == ("READ_REQUIRED", "mechanics_clear"), f"{packet_id}: binding mechanics")
        require(not gate.proof_problem(proof, ev, idx, idx, arc, DAY, "openai",
                                      lambda _: captures[proof["capture_sha256"]]), f"{packet_id}: proof replay failed")
        path = Path(record["_at"].rsplit(":", 1)[0])
        evidence[str(path.with_name("evidence_" + path.name))].append(ev)
        archives.append(arc)
        proofs.append(proof)
        markets[rid].append(term)
        handles[(table, rid)].append(eid)
        owners.add(owner)
        tiers[record["verification_tier"]] += 1
    require(markets and all(len(set(v)) == len(v) for v in markets.values()), "no markets or duplicate market terms")
    changes = {rid: ";".join(v) for rid, v in markets.items()}
    n, after = unknown_owners(idx, changes)
    require(n == denominator and before - after == owners and len(after) == 316 - len(owners), "market outcome differs")
    claims = [dict(zip(CLAIMS, (table, rid, "markets_served", "corrected", ids[0])))
              for (table, rid), ids in handles.items()]
    data = edit_data(changes, evidence, archives, idx)
    outputs = {
        "CLAIMS_CHECKED.csv": csv_bytes(claims, CLAIMS),
        "BINDING_PROOF.csv": csv_bytes(proofs, gate.PROOF_COLS),
        "OPEN_QUEUE.csv": csv_bytes(queue, QUEUE),
    }
    return data, outputs, tiers, len(owners), len(after)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--at", help="check canonical data and task files from this Git commit")
    parser.add_argument("--packet", type=Path, default=PACKET)
    parser.add_argument("--store", type=Path, default=STORE)
    args = parser.parse_args()
    data, outputs, tiers, owners, after = expected(args.packet, args.store, args.at)
    subprocess.run([sys.executable, "-I", "packet.py", "check"], cwd=args.packet, check=True)
    for name, raw in outputs.items():
        require(artifact(name, args.at) == raw, f"{name}: submitted rows differ from replay")
    cmd = ["diff", "--name-only", BASE] + ([args.at] if args.at else [])
    paths = set(git(*cmd, "--", "data/").decode().splitlines())
    if not args.at:
        paths.update(git("ls-files", "--others", "--exclude-standard", "--", "data/").decode().splitlines())
    require(paths == data.keys(), "changed canonical files differ from replay")
    for path, raw in data.items():
        got = git("show", f"{args.at}:{path}") if args.at else (ROOT / path).read_bytes()
        require(got == raw, f"{path}: canonical delta differs from replay")
    cells = sum(1 for _ in parse(outputs["CLAIMS_CHECKED.csv"]))
    print(f"PASS: 40 packet decisions, {sum(tiers.values())} witnesses {dict(sorted(tiers.items()))}, "
          f"{cells} claims, {owners} newly known PIC-18 owners. Unknown market: 316 to {after} of 794.")


if __name__ == "__main__":
    main()
