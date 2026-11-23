#!/usr/bin/env python3
"""Replay ATLAS-9 evidence dispositions, the exact HQ proofs and the canonical delta."""
import argparse
from collections import Counter
from datetime import date, datetime
import io
from pathlib import Path
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "24f71798"
FIRST_PIN = "f88278056eb6ec742305c897db9a5fedff8b2481"
DAY = date(2026, 11, 23)
LABEL = "codex " + HERE.name
FIRST = "p1-read-atlas9-pic18-2026-11-23"
SECOND = "p1-read-claude-built-atlas9-2026-11-23"
PACKETS = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist"
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
CLAIMS = ("table", "record_id", "field", "verdict", "evidence_id")
DISPOSITIONS = ("evidence_id", "record_id", "first_read", "cross_read", "packet_disposition", "application")
QUEUE = ("evidence_id", "record_id", "settling_fact")
RECEIPT = ("evidence_id", "archive_ref", "captured_at", "created_by", "original_evidence_id", "job_id")

HQ = {
    "EVD-421210": ("ORG-000019", ("Akron", "OH", "Summit"), ("Charlotte", "NC"),
                   "https://kingmachinemolds.com/corporate/",
                   "Charlotte, North Carolina. Rapid growth prompted a move to a larger Westinghouse Blvd. "
                   "facility, which became the primary new mold plant and company headquarters."),
    "EVD-421769": ("ORG-001907", ("Cleveland", "OH", "Cuyahoga"), ("Kalamazoo", "MI"),
                   "https://totalplastics.com/contact-us/",
                   "Total Plastics Int'l Headquarters 2810 North Burdick Street Kalamazoo, MI 49004"),
}
STREETS = {"EVD-420053", "EVD-422278"}
SETTLING = (
    ("A primary source naming the held operator at the place asserted by the evidence.",
     "405009 405021 420672 421746 421747 421755 422451 422452 425139 425219 425230 425345 425423 422240 422241 425347"),
    ("An operator-specific address or official postal-city and ZIP tie that resolves the location discrepancy.",
     "421279 421737 425054 425055 425223"),
    ("A primary source linking the cited name to the held legal name at the claimed operation.",
     "421581 421582 421588 422235 422344 422645 405007 421281"),
    ("A primary page or filing that explicitly identifies the held place as the headquarters.",
     "421336 421556 425148 425069"),
    ("A readable and current primary source naming the held operator at the asserted place.",
     "420042 420045 422251 422288"),
    ("A primary source binding the stated production to the operator's Solon plant.", "014722 014723"),
    ("An operator-specific statement that the named market is served by its products or sales.", "015525 015529"),
)

prior = runpy.run_path(str(HERE.parent / "p1-atlas8-corrections-2026-11-23/check.py"))
git, parse, require, sha, unique, csv_bytes = (
    prior[k] for k in ("git", "parse", "require", "sha", "unique", "csv_bytes")
)
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate


def artifact(name, ref):
    path = HERE / name
    return git("show", f"{ref}:{path.relative_to(ROOT)}") if ref else path.read_bytes()


def manifest(raw, folder):
    inputs = {}
    for line in raw.decode().splitlines():
        digest, name = line.split("  ", 1)
        path = Path(name)
        require(name not in inputs and not path.is_absolute() and ".." not in path.parts,
                f"unsafe or repeated manifest path {name}")
        data = (folder / path).read_bytes()
        require(sha(data) == digest, f"hash mismatch: {name}")
        inputs[name] = data
    return inputs


def by_id(ref, pattern, key):
    return unique(gate.rows(ref, pattern), lambda row: row[key], pattern)


def stable(row):
    return {k: v for k, v in row.items() if k != "_at"}


def packet_rows(folder, ref):
    files = manifest(artifact("PACKET.sha256", ref), folder)
    require(sum(p.startswith(FIRST + "/") for p in files) == 14
            and sum(p.startswith(SECOND + "/") for p in files) == 6 and len(files) == 20,
            "packet manifest count differs")
    first = unique(parse(files[FIRST + "/verdicts.csv"]), lambda row: row["evidence_id"], "first packet")
    assigned = unique(parse(files[FIRST + "/claude_built.csv"]), lambda row: row["evidence_id"], "assigned cross-reads")
    second = unique(parse(files[SECOND + "/verdicts.csv"]), lambda row: row["evidence_id"], "cross-read packet")
    require(Counter(r["verdict"] for r in first.values()) == {"VERIFIED": 193, "REJECT": 4, "STILL_UNCERTAIN": 37}
            and Counter(r["verdict"] for r in second.values()) == {"VERIFIED": 33, "STILL_UNCERTAIN": 4},
            "packet verdict counts differ")
    require(assigned.keys() == second.keys() <= first.keys(), "cross-read assignment keys differ")
    before = by_id(BASE, "evidence_*.csv", "evidence_id")
    original = by_id(FIRST_PIN, "evidence_*.csv", "evidence_id")
    ids = sorted(first)
    dispositions = []
    for eid in ids:
        row = first[eid]
        held = before[eid]
        rid = row["record_id"]
        require(rid == held["record_id"] and stable(held) == stable(original[eid]),
                f"{eid}: underlying evidence fields drifted since the first reader pin")
        cross = second.get(eid)
        if cross:
            require(row["verdict"] == "VERIFIED" and rid == cross["record_id"] == assigned[eid]["record_id"]
                    and sha(held["claim_detail"].encode()) == cross["claim_detail_sha256"],
                    f"{eid}: cross-read record, verdict or claim digest differs")
        final = cross["verdict"] if cross else row["verdict"]
        disposition = {"VERIFIED": "verified", "STILL_UNCERTAIN": "queued"}.get(final)
        if final == "REJECT":
            disposition = "corrected" if row["correct_value"] else "withdrawn"
        application = "corrected" if eid == "EVD-421210" else disposition
        dispositions.append(dict(zip(DISPOSITIONS, (eid, rid, row["verdict"], cross["verdict"] if cross else "",
                                                    disposition, application))))
    require(Counter(r["packet_disposition"] for r in dispositions) ==
            {"verified": 189, "corrected": 1, "withdrawn": 3, "queued": 41}, "packet disposition totals differ")
    require({r["evidence_id"] for r in dispositions if r["application"] == "corrected"} == HQ.keys()
            and {r["evidence_id"] for r in dispositions if r["application"] == "withdrawn"} == STREETS,
            "controller application differs from two HQ corrections and two street withdrawals")
    require(sum(r["application"] == "verified" and bool(r["cross_read"]) for r in dispositions) == 33,
            "verified reader split differs")
    return dispositions, before


def ledgers(dispositions, new_eids):
    settling = {f"EVD-{n}": fact for fact, indexes in SETTLING for n in indexes.split()}
    holds = [dict(evidence_id=r["evidence_id"], record_id=r["record_id"], settling_fact=settling[r["evidence_id"]])
             for r in dispositions if r["application"] == "queued"]
    require({r["evidence_id"] for r in holds} == settling.keys(), "open queue coverage differs")
    claims = []
    for row in dispositions:
        eid, app = row["evidence_id"], row["application"]
        if app != "queued":
            witness = {"verified": eid, "corrected": new_eids.get(eid), "withdrawn": ""}[app]
            claims.append(dict(zip(CLAIMS, ("evidence", eid, "claim_detail", app, witness))))
    for eid, (rid, _, _, _, _) in HQ.items():
        claims += [dict(zip(CLAIMS, ("organizations", rid, field, "corrected", new_eids[eid])))
                   for field in ("hq_city", "hq_state", "hq_in_scope")]
        claims.append(dict(zip(CLAIMS, ("organizations", rid, "hq_county", "withdrawn", ""))))
    return claims, holds


def organization_delta():
    base = by_id(BASE, "organizations_OH.csv", "org_id")
    moved, destinations = {}, {}
    for rid, old, new, _, _ in HQ.values():
        orig = stable(base[rid])
        require(tuple(orig[k] for k in ("hq_city", "hq_state", "hq_county")) == old
                and orig["hq_country"] == "US" and orig["hq_in_scope"] == "ne_ohio",
                f"{rid}: the HQ contradiction drifted")
        moved[rid] = dict(orig, hq_city=new[0], hq_state=new[1], hq_county="", hq_in_scope="national_us")
        destinations[rid] = f"data/organizations_{new[1]}.csv"
    return moved, destinations


def expected_data(moved, destinations, evidence, archives):
    expected = {}
    paths = {"data/organizations_OH.csv", *destinations.values()}
    for path in sorted(paths):
        original = git("show", f"{BASE}:{path}")
        lines = list(io.StringIO(original.decode(), newline=""))
        rows = parse(original)
        parts, end = [lines[0].encode()], 1
        insert = next((r for r, p in destinations.items() if p == path), None)
        for row in rows:
            start, end = end, rows.line_num
            rid = row["org_id"]
            if insert and rid > insert:
                parts.append(csv_bytes([moved[insert]], rows.fieldnames, with_header=False))
                insert = None
            if path == "data/organizations_OH.csv" and rid in moved:
                continue
            require(rid not in moved, f"{path}: duplicate target record {rid}")
            parts.append("".join(lines[start:end]).encode())
        if insert:
            parts.append(csv_bytes([moved[insert]], rows.fieldnames, with_header=False))
        expected[path] = b"".join(parts)
    for ev in evidence:
        rid = ev["record_id"]
        path = destinations[rid].replace("/organizations_", "/evidence_organizations_")
        base = git("show", f"{BASE}:{path}")
        expected[path] = base + csv_bytes([ev], parse(base).fieldnames, with_header=False)
    base = git("show", f"{BASE}:data/archive_links.csv")
    expected["data/archive_links.csv"] = base + csv_bytes(archives, parse(base).fieldnames, with_header=False)
    return expected


def hq_witness(eid, old_eid, record, capture):
    rid, _, new, src, quote = HQ[old_eid]
    marker = " (Wayback capture)" if capture != src else ""
    return dict(evidence_id=eid, record_table="organizations", record_id=rid, claim_type="address",
                claim_detail=f"hq_city={new[0]}, hq_state={new[1]}{marker}; quote: {quote}",
                source_class="own_site", source_ref=src, observed_date=DAY.isoformat(),
                tier_effect="supports_" + record["verification_tier"], created_by=LABEL,
                notes=f"Supersedes the headquarters assertion in {old_eid}.", address_role="physical")


def offices_and_proofs(ref, before, inputs):
    moved, destinations = organization_delta()
    evidence, archives, new_eids = [], [], {}
    floor = max(int(eid.split("-")[1]) for eid in before)
    require(floor == 483045, "reviewed evidence allocation base differs")
    proofs = unique(parse(artifact("BINDING_PROOF.csv", ref)), lambda r: r["evidence_id"], "proofs")
    receipts = unique(parse(artifact("ARCHIVES.csv", ref)), lambda r: r["original_evidence_id"], "archive receipts")
    require(receipts.keys() == HQ.keys(), "receipt keys differ from approved corrections")
    base_arcs = by_id(BASE, "archive_links.csv", "evidence_id")
    base_idx = gate.Index.load(BASE)
    idx = gate.Index.load(ref) if ref else base_idx
    store = {sha(data): data for data in inputs.values()}
    require(len(store) == 2 and store.keys() == {p["capture_sha256"] for p in proofs.values()},
            "exact capture input membership differs")
    for step, (old_eid, (rid, _, _, src, _)) in enumerate(HQ.items(), 1):
        rec = moved[rid]
        eid = f"EVD-{floor + step:06d}"
        require(before[old_eid]["record_id"] == rid and before[old_eid]["claim_type"] == "address",
                f"{old_eid}: wrong underlying HQ claim")
        receipt, proof = receipts[old_eid], proofs[eid]
        require(receipt["evidence_id"] == eid, f"{eid}: receipt ID differs")
        arc = {k: receipt[k] for k in ("evidence_id", "archive_ref", "captured_at", "created_by")}
        link = gate.ARCHIVE_RE.fullmatch(arc["archive_ref"])
        require(link and not link[2] and link[3] == src and
                datetime.strptime(link[1], "%Y%m%d%H%M%S").date().isoformat() == arc["captured_at"],
                f"{eid}: source page or capture date differs")
        if old_eid == "EVD-421210":
            require(arc["archive_ref"] == base_arcs[old_eid]["archive_ref"]
                    and arc["created_by"] == "unknown" and not receipt["job_id"],
                    "King archive reuse or attribution differs")
        else:
            require(arc["created_by"] == LABEL and receipt["job_id"].startswith("spn2-")
                    and arc["captured_at"] == DAY.isoformat(), "Total Plastics save receipt differs")
        ev = hq_witness(eid, old_eid, rec, proof["capture"])
        require(gate.judge(ev, idx)[:2] == ("READ_REQUIRED", "mechanics_clear"), f"{eid}: gate floor")
        fault = gate.proof_problem(proof, ev, idx, base_idx, arc, DAY, "openai",
                                   lambda _: store[proof["capture_sha256"]])
        require(not fault, f"{eid}: capture proof failed: {fault}")
        new_eids[old_eid] = eid
        evidence.append(ev)
        archives.append(arc)
    require(proofs.keys() == set(new_eids.values()), "unexpected proof rows")
    require(all(before[eid]["record_id"] == "SITE-000156" and before[eid]["claim_type"] == "address"
                for eid in STREETS) and not base_idx.record("sites", "SITE-000156")["street_address"],
            "the two withdrawals must refer to the already-blank Swagelok street")
    return expected_data(moved, destinations, evidence, archives), new_eids


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--packet-root", type=Path, default=PACKETS)
    ap.add_argument("--store", type=Path, default=STORE)
    ap.add_argument("--at", help="read data and task artifacts from this Git ref")
    args = ap.parse_args()
    first = args.packet_root / FIRST
    dispositions, base = packet_rows(args.packet_root, args.at)
    # Packet code is private, sealed and invoked only by the task's local replay.
    subprocess.run([sys.executable, "-I", str(first / "scripts/check_verdicts.py"), str(first), str(first) + ".scratch"],
                   check=True, cwd=ROOT)
    subprocess.run([sys.executable, "-I", "packet.py"], check=True, cwd=args.packet_root / SECOND)
    inputs = manifest(artifact("INPUTS.sha256", args.at), args.store)
    data, new_eids = offices_and_proofs(args.at, base, inputs)
    claims, holds = ledgers(dispositions, new_eids)
    for name, rows, columns in (
        ("PACKET_DISPOSITIONS.csv", dispositions, DISPOSITIONS),
        ("CLAIMS_CHECKED.csv", claims, CLAIMS),
        ("OPEN_QUEUE.csv", holds, QUEUE),
    ):
        require(artifact(name, args.at) == csv_bytes(rows, columns), f"{name}: submitted ledger differs from replay")
    git_diff = ["diff", "--name-only", BASE]
    if args.at:
        git_diff.append(args.at)
    found = set(git(*git_diff, "--", "data/").decode().splitlines())
    if not args.at:
        found.update(git("ls-files", "--others", "--exclude-standard", "--", "data/").decode().splitlines())
    require(found == data.keys(), "changed canonical files differ")
    for path, raw in data.items():
        got = git("show", f"{args.at}:{path}") if args.at else (ROOT / path).read_bytes()
        require(got == raw, f"{path}: canonical delta differs from replay")
    print(f"PASS: {len(dispositions)} packet rows, {len(claims)} claims, 8 HQ cells, "
          f"{len(new_eids)} exact proofs and archives, {len(holds)} queued.")


if __name__ == "__main__":
    main()
