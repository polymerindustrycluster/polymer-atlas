#!/usr/bin/env python3
"""Replay permitted process claims from sealed Ohio EPA filing bytes."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import io
from pathlib import Path
import re
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "b2933fa96142a0c912dffab3dfc6e74212e3dc4e"
LABEL = HERE.name
PACKETS = Path.home() / ".bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist"
STORE = Path("/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store")
SITES = "data/sites_OH.csv"
EVIDENCE = "data/evidence_sites_OH.csv"
CLAIMS = ("table", "record_id", "field", "verdict", "evidence_id")
QUEUE = ("site_id", "docid", "token", "verdict", "settling_fact")
BINDING_PAGES = {"4359369": 5, "2242238": 7, "3267030": 5, "3029446": 7,
                 "4023003": 5, "3792297": 5, "1315096": 7}
PACKET_INPUTS = (f"{LABEL}/proposals.csv", f"{LABEL}/verdicts.csv",
                 "p2-air-permits-read-2026-11-23/README.md",
                 "p2-air-permits-read-2026-11-23/verdicts.csv")

prior = runpy.run_path(str(HERE.parent / "p1-atlas8-corrections-2026-11-23/check.py"))
git, parse, require, sha, unique, csv_bytes = (
    prior[k] for k in ("git", "parse", "require", "sha", "unique", "csv_bytes")
)
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence_binding as gate
from regions import PIC18
from export_vocab import literal_constants

PROCESSES = literal_constants()["PROCESSES"]


def artifact(name, ref):
    f = HERE / name
    return git("show", f"{ref}:{f.relative_to(ROOT)}") if ref else f.read_bytes()


def inputs(blob, folder):
    files = {}
    for line in blob.decode().splitlines():
        digest, path = line.split("  ", 1)
        require(path not in files and not Path(path).is_absolute() and ".." not in Path(path).parts,
                f"Unsafe or duplicate input {path}")
        data = (folder / path).read_bytes()
        require(sha(data) == digest, f"Hash mismatch: {path}")
        files[path] = data
    return files


def permit(path, docid, holder, street, city):
    pages = subprocess.check_output(["pdftotext", "-layout", str(path), "-"]).decode().split("\f")
    binding = " ".join(pages[BINDING_PAGES[docid] - 1].split())
    locality = re.escape(street) + r"\s*,?\s*" + re.escape(city) + r"\s*,?\s*(?:Ohio|OH)\s+([0-9]{5}(?:-[0-9]{4})?)\b"
    addr = re.search(locality, binding, re.IGNORECASE)
    require(holder.casefold() in binding.casefold() and addr, f"{docid}: permittee or address missing on binding page")
    effective = re.findall(r"(?m)^\s*Effective:?\s+(\d{1,2}/\d{1,2}/\d{4})\s*$", pages[2])
    require(len(effective) == 1, f"{docid}: missing or ambiguous effective date")
    return ([" ".join(p.split()) for p in pages],
            " ".join(" ".join(pages).split()),
            datetime.strptime(effective[0], "%m/%d/%Y").date().isoformat(), addr[1])


def unknown_owners(idx, changes):
    owners = defaultdict(list)
    for s in idx.sites.values():
        if (s["state"] == "OH" and s["county"] in PIC18 and s["operating_status"] == "active"
                and s["verification_tier"] in {"A", "B", "C"}):
            owners[s["org_id"]].append(s)
    missing = set()
    for oid, sites in owners.items():
        values = [idx.orgs[oid].get("processes", "")] + [changes.get(s["site_id"], s["processes"]) for s in sites]
        if not ({t.strip() for v in values for t in v.split(";")} - {"", "unknown"}):
            missing.add(oid)
    return len(owners), missing


def expected(packets, store, ref=None):
    sealed = inputs(artifact("PACKET.sha256", ref), packets)
    require(set(sealed) == set(PACKET_INPUTS), "Unexpected packet input set")
    raw = inputs(artifact("INPUTS.sha256", ref), store)
    doc_paths = unique(raw, lambda p: Path(p).stem.rsplit("_", 1)[-1], "permit document")
    require(doc_paths.keys() == BINDING_PAGES.keys() and
            all(re.fullmatch(r"raw/permits-oh-air/2026-11-2[23]/\d{10}_\d+\.pdf", p) for p in raw),
            "Permit manifest does not cover the seven sealed filings")
    keys = ("org_id", "site_id", "premise", "docid", "token", "quote_offset")
    key = lambda r: tuple(r[k] for k in keys)
    proposals = unique(parse(sealed[PACKET_INPUTS[0]]), key, "proposal")
    first_reads = unique(parse(sealed[PACKET_INPUTS[1]]), lambda r: r["org_id"], "first read")
    reads = unique(parse(sealed[PACKET_INPUTS[3]]), key, "independent read")
    require(Counter(r["verdict"] for r in first_reads.values()) ==
            {"PROCESS": 8, "NO_PROCESS_STATED": 9, "STILL_UNCERTAIN": 11} and
            Counter(r["verdict"] for r in reads.values()) == {"VERIFIED": 8, "REJECT": 2},
            "Packet populations changed")
    idx = gate.Index.load(BASE)
    require(len(idx.sites) == len(gate.rows(BASE, "sites_*.csv")), "Duplicate site ID")
    require(len(idx.orgs) == len(gate.rows(BASE, "organizations_*.csv")) + len(gate.rows(BASE, "ecosystem.csv")),
            "Duplicate owner ID")
    count, before = unknown_owners(idx, {})
    require((count, len(before)) == (794, 312), "Base PIC-18 owner census drifted")
    first = max(int(r["evidence_id"].split("-")[1]) for r in gate.rows(BASE, "evidence_*.csv")) + 1
    docs, changes, witness, claims, queue = {}, {}, [], {}, []
    for k, r in reads.items():
        rid, oid, docid, token = (r[s] for s in ("site_id", "org_id", "docid", "token"))
        p = proposals.get(k, {})
        require(first_reads[oid]["verdict"] == "PROCESS" and
                p.get("disposition") == "candidate" and p.get("grain") == "PLANT" and p.get("bound") == "Y" and
                all(r[f] == "PASS" for f in ("QUOTE", "BINDING", "TERM")) and
                all(p.get(f) == r[f] for f in ("quote", "pdf_sha256", "permit_number", "edocpub_url")) and
                all(p.get(f"printed_{f}") == r[f"permit_{f}"] for f in ("holder", "street", "city")),
                f"{rid}/{docid}: readings disagree on the source or quote")
        path = doc_paths[docid]
        require(sha(raw[path]) == r["pdf_sha256"] and Path(path).stem == f'{r["premise"]}_{docid}',
                f"{docid}: wrong filing or premises identifier")
        if docid not in docs:
            docs[docid] = permit(store / path, docid, r["permit_holder"], r["permit_street"], r["permit_city"])
        pages, text, date, zip_code = docs[docid]
        page, off, quote = int(r["pdf_page"]), int(r["quote_offset"]), r["quote"]
        require(r["premise"] in pages[BINDING_PAGES[docid] - 1] and r["permit_number"] in pages[2] and
                1 <= page <= len(pages) and quote in pages[page - 1] and text[off:off+len(quote)] == quote,
                f"{rid}/{docid}: quote does not replay")
        if r["verdict"] == "REJECT":
            require(rid == "SITE-001282" and docid == "3029446" and r["CURRENCY"] == "FAIL" and
                    "P0136216" in r["currency_basis"],
                    f"{rid}/{docid}: unexpected rejected source")
            queue.append(dict(zip(QUEUE, (rid, docid, token, "REJECT",
                "P0134426 was superseded by P0136216. A separately reviewed current permit witness is needed."))))
            continue
        site = idx.sites[rid]
        require(site["org_id"] == oid and oid in before and site["state"] == "OH" and site["county"] in PIC18
                and site["operating_status"] == "active" and site["verification_tier"] in {"A", "B"}
                and site["processes"] in {"", "unknown"} and token in PROCESSES and r["CURRENCY"] == "PASS",
                f"{rid}: site or controlled process is no longer eligible")
        require(changes.setdefault(rid, token) == token, f"{rid}: multiple proposed process terms")
        eid = f"EVD-{first + len(witness):06d}"
        locality = f'{r["permit_street"]}, {r["permit_city"]}, OH {zip_code}'
        ev = dict(evidence_id=eid, record_table="sites", record_id=rid, claim_type="activity",
                  claim_detail=f'processes {token} authorized for the site; process excerpt: "{quote}"; '
                               f'quote: permittee: {r["permit_holder"]}; address: {locality}',
                  source_class="government_filing",
                  source_ref=f'Ohio EPA Air Services eDocument {docid}, permit {r["permit_number"]}, '
                             f'process PDF p. {page}, premises PDF p. {BINDING_PAGES[docid]}',
                  observed_date=date, tier_effect=f'supports_{site["verification_tier"]}', created_by=LABEL,
                  notes="Permit read 2026-11-23. This witness records permit authorization.", address_role="")
        verdict, reason, _ = gate.judge(ev, idx)
        require(verdict == "PASS", f"{eid}: trusted binding {verdict} {reason}")
        witness.append(ev)
        claims.setdefault(rid, dict(zip(CLAIMS, ("sites", rid, "processes", "corrected", eid))))
    den, after = unknown_owners(idx, changes)
    require(len(changes) == len(claims) == 6 and len(witness) == 8 and len(queue) == 2
            and (den, len(after), len(before - after)) == (794, 306, 6) and after <= before,
            "Applied counts or PIC-18 owner outcome changed")

    original = git("show", f"{BASE}:{SITES}")
    reader = parse(original)
    lines = list(io.StringIO(original.decode(), newline=""))
    out, end, applied = [lines[0].encode()], 1, set()
    for row in reader:
        start, end = end, reader.line_num
        rid = row["site_id"]
        if rid in changes:
            row["processes"] = changes[rid]
            out.append(csv_bytes([row], reader.fieldnames, with_header=False))
            applied.add(rid)
        else:
            out.append("".join(lines[start:end]).encode())
    require(applied == changes.keys(), "Some corrected sites are outside the Ohio shard")
    old = git("show", f"{BASE}:{EVIDENCE}")
    require(old.endswith(b"\n"), "Evidence append would run into the last row")
    data = {SITES: b"".join(out), EVIDENCE: old + csv_bytes(witness, parse(old).fieldnames, with_header=False)}
    return data, {"CLAIMS_CHECKED.csv": csv_bytes(claims.values(), CLAIMS),
                  "OPEN_QUEUE.csv": csv_bytes(queue, QUEUE)}, Counter(r["tier_effect"] for r in witness)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--at", default="HEAD")
    ap.add_argument("--packets", type=Path, default=PACKETS)
    ap.add_argument("--store", type=Path, default=STORE)
    a = ap.parse_args()
    data, artifact_bytes, tiers = expected(a.packets, a.store, a.at)
    changed = set(git("diff", "--name-only", BASE, a.at, "--", "data/").decode().splitlines())
    require(changed == data.keys(), "Unexpected set of changed data files")
    for path, value in data.items():
        require(git("show", f"{a.at}:{path}") == value, f"{path}: unexpected data delta")
    for path, value in artifact_bytes.items():
        require(artifact(path, a.at) == value, f"{path}: packet replay differs")
    print(f"PASS: 10 verdicts, 7 PDFs, 8 witnesses ({dict(tiers)}), 6 corrected site cells, "
          "2 rejected quotes; 312 -> 306 process-unknown of 794 PIC-18 owners")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
